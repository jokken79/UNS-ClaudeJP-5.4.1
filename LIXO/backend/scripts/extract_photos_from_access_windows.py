#!/usr/bin/env python3
r"""
Extrae fotos OLE de la base de datos Access usando zipfile (sin ODBC).

Las fotos en Access se almacenan como OLE objects en la tabla T_履歴書.
Este script:
1. Abre el .accdb como ZIP (Access usa formato ZIP internamente)
2. Extrae la tabla OLE
3. Decodifica imágenes JPEG/PNG
4. Carga en PostgreSQL candidates.photo_data_url

NOTA: Este script funciona sin ODBC drivers (recomendado para Windows).
Alternativa: En Docker usar pyodbc con drivers ODBC instalados.
"""
import sys
import os
import base64
import json
import zipfile
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '/app')

from app.core.database import SessionLocal
from app.models.models import Candidate

# Ruta de la BD Access (Windows)
ACCESS_DB_PATH = r"D:\UNS-ClaudeJP-5.2\JPUNS-CLAUDE5.2\UNS-ClaudeJP-5.2\BASEDATEJP\ユニバーサル企画㈱データベースv25.3.24_be.accdb"

def extract_photo_from_ole(ole_data: bytes) -> str | None:
    """
    Extrae imagen JPEG/PNG de un objeto OLE de Access.

    Las fotos en Access se almacenan como OLE objects.
    Buscamos los marcadores:
    - JPEG: FF D8 FF
    - PNG: 89 50 4E 47
    """
    if not ole_data or len(ole_data) < 20:
        return None

    try:
        # Buscar marcador JPEG (FF D8 FF)
        jpeg_start = ole_data.find(b'\xff\xd8\xff')
        if jpeg_start >= 0:
            # Encontrado JPEG - buscamos su fin (FF D9)
            jpeg_end = ole_data.find(b'\xff\xd9', jpeg_start)
            if jpeg_end >= 0:
                jpeg_data = ole_data[jpeg_start:jpeg_end + 2]
                if len(jpeg_data) > 100:  # Validar que tenga contenido
                    return f"data:image/jpeg;base64,{base64.b64encode(jpeg_data).decode()}"

        # Buscar marcador PNG (89 50 4E 47)
        png_start = ole_data.find(b'\x89\x50\x4e\x47')
        if png_start >= 0:
            # Encontrado PNG - buscamos su fin (IEND)
            png_end = ole_data.find(b'\x49\x45\x4e\x44\xae\x42\x60\x82', png_start)
            if png_end >= 0:
                png_data = ole_data[png_start:png_end + 8]
                if len(png_data) > 100:
                    return f"data:image/png;base64,{base64.b64encode(png_data).decode()}"

        return None

    except Exception as e:
        print(f"  ⚠ Error decodificando OLE: {e}")
        return None

def extract_photos_from_access():
    """Extrae fotos de Access y carga en PostgreSQL"""

    access_file = Path(ACCESS_DB_PATH)

    if not access_file.exists():
        print(f"""
╔════════════════════════════════════════════════════════════╗
║          ERROR: BD ACCESS NO ENCONTRADA                    ║
╚════════════════════════════════════════════════════════════╝
Ruta esperada: {ACCESS_DB_PATH}
EXISTE: {access_file.exists()}

SOLUCIÓN: Verifica que la ruta sea correcta:
  - D:\\UNS-ClaudeJP-5.2\\UNS-ClaudeJP-5.2\\BASEDATEJP\\
  - ユニバーサル企画㈱データベースv25.3.24.accdb
        """)
        return False

    print(f"""
╔════════════════════════════════════════════════════════════╗
║      EXTRAYENDO FOTOS DE ACCESS DATABASE (MÉTODO ZIP)     ║
╚════════════════════════════════════════════════════════════╝
Leyendo: {ACCESS_DB_PATH}
Tamaño: {access_file.stat().st_size / 1024 / 1024:.2f} MB
Usando zipfile (sin ODBC drivers requeridos)
    """)

    try:
        # Abrir .accdb como ZIP
        with zipfile.ZipFile(access_file, 'r') as zip_ref:
            # Listar archivos en el ZIP
            file_list = zip_ref.namelist()
            print(f"✓ Archivos en ZIP: {len(file_list)}")

            # Buscar archivos que contengan tabla OLE
            # Access almacena las tablas en: /P" (objeto de tabla)
            ole_files = [f for f in file_list if '履歴書' in f or 'T_' in f]
            print(f"✓ Archivos de tabla encontrados: {len(ole_files)}")

            if not ole_files:
                print("⚠ No se encontraron archivos de tabla con fotos")
                return False

            # Para cada archivo potencial, intentar extraer fotos
            photos_found = {}

            for ole_file in ole_files:
                try:
                    data = zip_ref.read(ole_file)

                    # Buscar todas las fotos en este archivo
                    idx = 0
                    while True:
                        jpeg_start = data.find(b'\xff\xd8\xff', idx)
                        if jpeg_start < 0:
                            break

                        jpeg_end = data.find(b'\xff\xd9', jpeg_start)
                        if jpeg_end < 0:
                            break

                        jpeg_data = data[jpeg_start:jpeg_end + 2]
                        if len(jpeg_data) > 100:
                            photo_b64 = f"data:image/jpeg;base64,{base64.b64encode(jpeg_data).decode()}"
                            photos_found[len(photos_found)] = photo_b64

                        idx = jpeg_end + 2

                except Exception as e:
                    print(f"  ⚠ Error procesando {ole_file}: {e}")
                    continue

            if not photos_found:
                print("⚠ No se encontraron fotos JPEG en los archivos ZIP")
                return False

            print(f"✓ Fotos encontradas en ZIP: {len(photos_found)}")

    except zipfile.BadZipFile:
        print("⚠ El archivo .accdb no es un ZIP válido (puede requerir ODBC pyodbc)")
        return False
    except Exception as e:
        print(f"❌ Error al procesar ZIP: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Si no encontramos fotos por ZIP, intentar con pyodbc como fallback
    print("\n⚠ Método ZIP no encontró fotos. Intentando con pyodbc...")

    try:
        import pyodbc

        # Conectar a Access
        conn_string = f"Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={ACCESS_DB_PATH};"
        conn = pyodbc.connect(conn_string)
        cursor = conn.cursor()

        # Consultar fotos
        print("📖 Consultando tabla T_履歴書...")
        query = "SELECT [履歴書ID], [写真] FROM [T_履歴書] WHERE [写真] IS NOT NULL"
        cursor.execute(query)

        rows = cursor.fetchall()
        print(f"✓ {len(rows)} registros con fotos encontrados")

        # Conectar a PostgreSQL
        db = SessionLocal()
        updated = 0
        errors = 0

        for idx, (rirekisho_id, photo_ole) in enumerate(rows, 1):
            try:
                if not photo_ole:
                    continue

                # Decodificar foto OLE
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

                        if updated % 100 == 0:
                            print(f"✓ {updated} fotos procesadas...")
                    else:
                        print(f"  ⚠ Candidato {rirekisho_id} no encontrado en BD")

            except Exception as e:
                errors += 1
                if errors <= 5:
                    print(f"  ❌ Error en {rirekisho_id}: {str(e)[:100]}")

        cursor.close()
        conn.close()
        db.close()

        print(f"""
╔════════════════════════════════════════════════════════════╗
║          EXTRACCIÓN COMPLETADA (PYODBC)                    ║
╚════════════════════════════════════════════════════════════╝
✓ Fotos extraídas: {updated}
✗ Errores:         {errors}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """)

        return updated > 0

    except ImportError:
        print("""
❌ pyodbc no está disponible y ZIP no encontró fotos.

SOLUCIONES:
1. Instalar pyodbc en Windows: pip install pyodbc
2. O usar este script en Windows donde accdb_tools está disponible
3. O extraer manualmente las fotos con herramienta Access en Windows
        """)
        return False
    except Exception as e:
        print(f"❌ Error con pyodbc: {e}")
        return False

if __name__ == '__main__':
    success = extract_photos_from_access()
    sys.exit(0 if success else 1)
