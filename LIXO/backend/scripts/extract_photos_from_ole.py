#!/usr/bin/env python3
"""
Extrae fotos en formato OLE de access_candidates_data.json
y las carga como base64 data URLs en la BD.

Las fotos en Access se almacenan como OLE objects (Object Linking & Embedding).
Este script:
1. Lee el JSON con las fotos OLE
2. Decodifica el OLE binario
3. Convierte a base64
4. Actualiza la BD
"""
import sys
import json
import base64
from pathlib import Path

sys.path.insert(0, '/app')

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.models import Candidate

def extract_photo_from_ole(ole_data: bytes) -> str | None:
    """
    Extrae imagen JPEG/PNG de un objeto OLE de Access.

    Formato OLE de Access para imágenes:
    - Comienza con: FF D8 FF (JPEG) o 89 50 4E 47 (PNG)
    - El OLE es un contenedor que envuelve la imagen real

    Esta función busca el marcador de inicio JPEG/PNG dentro del OLE.
    """
    if not ole_data or len(ole_data) < 20:
        return None

    try:
        # Buscar marcador JPEG (FF D8 FF)
        jpeg_start = ole_data.find(b'\xff\xd8\xff')
        if jpeg_start >= 0:
            # Encontrado JPEG - buscamos su fin
            jpeg_end = ole_data.find(b'\xff\xd9', jpeg_start)
            if jpeg_end >= 0:
                jpeg_data = ole_data[jpeg_start:jpeg_end + 2]
                if len(jpeg_data) > 100:  # Validar que tenga contenido
                    return f"data:image/jpeg;base64,{base64.b64encode(jpeg_data).decode()}"

        # Buscar marcador PNG (89 50 4E 47)
        png_start = ole_data.find(b'\x89\x50\x4e\x47')
        if png_start >= 0:
            # Encontrado PNG - buscamos su fin (IEND chunk: 49 45 4E 44)
            png_end = ole_data.find(b'\x49\x45\x4e\x44\xae\x42\x60\x82', png_start)
            if png_end >= 0:
                png_data = ole_data[png_start:png_end + 8]
                if len(png_data) > 100:
                    return f"data:image/png;base64,{base64.b64encode(png_data).decode()}"

        return None

    except Exception as e:
        print(f"  Error decodificando OLE: {e}")
        return None

def load_json_with_encoding(filepath: str):
    """Carga JSON detectando encoding automáticamente"""
    with open(filepath, 'rb') as f:
        raw = f.read()

    # Intentar diferentes encodings
    for encoding in ['utf-8', 'utf-16', 'utf-16-le', 'utf-16-be', 'shift_jis', 'cp932']:
        try:
            return json.loads(raw.decode(encoding))
        except:
            continue

    # Fallback: ignorar errores de encoding
    return json.loads(raw.decode('utf-8', errors='ignore'))

def extract_photos_from_access_json():
    """Extrae fotos OLE del JSON de Access"""

    json_file = Path('/app/config/access_candidates_data.json')

    if not json_file.exists():
        print(f"❌ Archivo no encontrado: {json_file}")
        return False

    print(f"""
╔════════════════════════════════════════════════════════════╗
║          EXTRAYENDO FOTOS DE FORMATO OLE                   ║
╚════════════════════════════════════════════════════════════╝
Leyendo: {json_file}
    """)

    try:
        # Cargar JSON con detección automática de encoding
        data = load_json_with_encoding(str(json_file))

        if not isinstance(data, list):
            print("❌ El JSON debe ser un array")
            return False

        print(f"✓ Archivo cargado: {len(data)} candidatos")

    except Exception as e:
        print(f"❌ Error al cargar JSON: {e}")
        return False

    # Conectar a BD
    db = SessionLocal()
    updated = 0
    skipped = 0
    errors = 0

    try:
        for idx, record in enumerate(data, 1):
            try:
                # Obtener rirekisho_id (puede estar con nombre en japonés)
                rirekisho_id = None
                photo_ole = None

                # Buscar rirekisho_id (muchas variaciones de nombre)
                for key in record.keys():
                    key_str = str(key).lower()
                    if 'id' in key_str and any(x in key_str for x in ['rirekisho', '履歴書', 'resid']):
                        rirekisho_id = record.get(key)
                        break

                # Buscar campo de foto OLE
                for key in record.keys():
                    key_str = str(key).lower()
                    if any(x in key_str for x in ['photo', 'foto', '写真', 'image']):
                        val = record.get(key)
                        if val and isinstance(val, (bytes, str)):
                            if isinstance(val, str):
                                # Si es string, podría ser base64 o hex
                                try:
                                    photo_ole = base64.b64decode(val)
                                except:
                                    try:
                                        photo_ole = bytes.fromhex(val)
                                    except:
                                        pass
                            else:
                                photo_ole = val
                            break

                if not rirekisho_id:
                    skipped += 1
                    continue

                if not photo_ole or len(photo_ole) < 20:
                    skipped += 1
                    continue

                # Intentar extraer foto del OLE
                photo_data_url = extract_photo_from_ole(photo_ole)

                if photo_data_url:
                    # Buscar candidato en BD
                    candidate = db.query(Candidate).filter(
                        Candidate.rirekisho_id == str(rirekisho_id)
                    ).first()

                    if candidate:
                        candidate.photo_data_url = photo_data_url
                        db.commit()
                        updated += 1

                        if updated % 50 == 0:
                            print(f"✓ {updated} fotos procesadas...")
                    else:
                        skipped += 1
                else:
                    skipped += 1

            except Exception as e:
                errors += 1
                if errors < 10:
                    print(f"⚠ Error en registro {idx}: {str(e)[:80]}")

        print(f"""
╔════════════════════════════════════════════════════════════╗
║          EXTRACCIÓN COMPLETADA                             ║
╚════════════════════════════════════════════════════════════╝
✓ Fotos extraídas: {updated}
━ Sin foto OLE:    {skipped}
✗ Errores:         {errors}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """)

        return updated > 0

    except Exception as e:
        print(f"❌ Error general: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == '__main__':
    success = extract_photos_from_access_json()
    sys.exit(0 if success else 1)
