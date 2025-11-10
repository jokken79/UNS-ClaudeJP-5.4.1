#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Extrae fotos OLE de la base de datos Access original.

Ruta BD Access: D:\UNS-ClaudeJP-5.2\UNS-ClaudeJP-5.2\BASEDATEJP\ユニバーサル企画㈱データベースv25.3.24.accdb
Tabla: T_履歴書
Campo de fotos: 写真
Campo ID: 履歴書ID

Este script:
1. Conecta a Access con pyodbc
2. Lee fotos OLE del campo 写真
3. Decodifica y convierte a base64
4. Carga en PostgreSQL candidates.photo_data_url
"""
import sys
import io
import base64
from pathlib import Path
from io import BytesIO

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os
from dotenv import load_dotenv

# Detectar si estamos en Windows o Docker
if os.name == 'nt':
    # Windows - usar ruta del host
    script_dir = Path(__file__).parent.parent.parent  # Subir 3 niveles desde backend/scripts/
    sys.path.insert(0, str(script_dir / 'backend'))
    ACCESS_DB_PATH = str(script_dir / 'BASEDATEJP' / 'ユニバーサル企画㈱データベースv25.3.24_be.accdb')

    # Cargar .env desde raíz del proyecto
    env_file = script_dir / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        print(f"[OK] .env cargado desde: {env_file}")
    else:
        print(f"[WARNING] .env no encontrado en: {env_file}")
        print("  Asegurate de tener .env con DATABASE_URL configurado")
else:
    # Docker Linux
    sys.path.insert(0, '/app')
    ACCESS_DB_PATH = r"/app/BASEDATEJP/ユニバーサル企画㈱データベースv25.3.24_be.accdb"
    load_dotenv()

from app.core.database import SessionLocal
from app.models.models import Candidate

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
║      EXTRAYENDO FOTOS DE ACCESS DATABASE                   ║
╚════════════════════════════════════════════════════════════╝
Leyendo: {ACCESS_DB_PATH}
Tamaño: {access_file.stat().st_size / 1024 / 1024:.2f} MB
    """)

    try:
        import pyodbc
    except ImportError:
        print("""
❌ pyodbc no está instalado.

SOLUCIÓN en Docker:
  pip install pyodbc

En Windows local:
  pip install pyodbc

IMPORTANTE: En Linux/Docker necesita driver ODBC para Access.
Alternativa: Usar el unified_photo_import.py en Windows.
        """)
        return False

    try:
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
║          EXTRACCIÓN COMPLETADA                             ║
╚════════════════════════════════════════════════════════════╝
✓ Fotos extraídas: {updated}
✗ Errores:         {errors}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """)

        return updated > 0

    except Exception as e:
        print(f"❌ Error general: {e}")
        print(f"   Tipo: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = extract_photos_from_access()
    sys.exit(0 if success else 1)
