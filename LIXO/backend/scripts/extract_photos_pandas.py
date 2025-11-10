#!/usr/bin/env python3
"""
Extrae fotos de Access DB usando pandas-access
(Alternativa sin pyodbc ni drivers ODBC)
"""

import sys
import os
import base64
from pathlib import Path

sys.path.insert(0, '/app')

from app.core.database import SessionLocal
from app.models.models import Candidate

ACCESS_DB_PATH = Path('/app/BASEDATEJP/ユニバーサル企画㈱データベースv25.3.24_be.accdb')

def extract_photo_from_ole(ole_data: bytes) -> str | None:
    """Extrae imagen JPEG/PNG de un objeto OLE de Access."""
    if not ole_data or len(ole_data) < 20:
        return None

    try:
        # Buscar marcador JPEG (FF D8 FF)
        jpeg_start = ole_data.find(b'\xff\xd8\xff')
        if jpeg_start >= 0:
            jpeg_end = ole_data.find(b'\xff\xd9', jpeg_start)
            if jpeg_end >= 0:
                jpeg_data = ole_data[jpeg_start:jpeg_end + 2]
                if len(jpeg_data) > 100:
                    return f"data:image/jpeg;base64,{base64.b64encode(jpeg_data).decode()}"

        # Buscar marcador PNG (89 50 4E 47)
        png_start = ole_data.find(b'\x89\x50\x4e\x47')
        if png_start >= 0:
            png_end = ole_data.find(b'\x49\x45\x4e\x44\xae\x42\x60\x82', png_start)
            if png_end >= 0:
                png_data = ole_data[png_start:png_end + 8]
                if len(png_data) > 100:
                    return f"data:image/png;base64,{base64.b64encode(png_data).decode()}"

        return None
    except Exception:
        return None


def main():
    """Intenta extraer fotos con pandas-access."""
    print("\n" + "=" * 60)
    print("  EXTRACCIÓN DE FOTOS CON PANDAS-ACCESS")
    print("=" * 60 + "\n")

    if not ACCESS_DB_PATH.exists():
        print(f"❌ Access DB no encontrada: {ACCESS_DB_PATH}")
        return 1

    print(f"✓ Access DB encontrada: {ACCESS_DB_PATH}")
    print(f"  Tamaño: {ACCESS_DB_PATH.stat().st_size / 1024 / 1024:.2f} MB\n")

    try:
        import pandas_access as mdb
        print("✓ pandas-access disponible\n")
    except ImportError:
        print("❌ pandas-access no instalado")
        print("   Instalando: pip install pandas-access")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas-access"])
            import pandas_access as mdb
            print("✓ pandas-access instalado\n")
        except Exception as e:
            print(f"❌ Error instalando pandas-access: {e}")
            return 1

    try:
        # Leer tabla T_履歴書
        print("📖 Leyendo tabla T_履歴書...")

        # Abrir base de datos
        with mdb.Database(str(ACCESS_DB_PATH)) as db:
            # Listar tablas disponibles
            tables = db.table_names()
            print(f"✓ Tablas encontradas: {len(tables)}\n")

            # Buscar tabla de履歴書
            rirekisho_table = None
            for table in tables:
                if '履歴書' in table:
                    rirekisho_table = table
                    break

            if not rirekisho_table:
                print("❌ Tabla de履歴書 no encontrada")
                print(f"   Tablas disponibles: {', '.join(tables[:10])}")
                return 1

            print(f"✓ Tabla encontrada: {rirekisho_table}\n")

            # Leer tabla
            df = db.read_table(rirekisho_table)
            print(f"✓ Registros leídos: {len(df)}")
            print(f"✓ Columnas: {', '.join(df.columns[:5])}...\n")

            # Buscar columna de foto
            photo_col = None
            for col in df.columns:
                if '写真' in col or 'photo' in col.lower():
                    photo_col = col
                    break

            if not photo_col:
                print("❌ Columna de foto no encontrada")
                print(f"   Columnas disponibles: {', '.join(df.columns)}")
                return 1

            print(f"✓ Columna de foto: {photo_col}\n")

            # Procesar fotos
            db_session = SessionLocal()
            updated = 0
            errors = 0

            print("📸 Procesando fotos...")

            for idx, row in df.iterrows():
                try:
                    rirekisho_id = row.get('履歴書ID') or row.get('ID')
                    photo_ole = row.get(photo_col)

                    if not photo_ole or not rirekisho_id:
                        continue

                    # Convertir a bytes si es necesario
                    if isinstance(photo_ole, str):
                        photo_ole = photo_ole.encode('latin-1')

                    photo_data_url = extract_photo_from_ole(photo_ole)

                    if photo_data_url:
                        candidate = db_session.query(Candidate).filter(
                            Candidate.rirekisho_id == str(rirekisho_id)
                        ).first()

                        if candidate:
                            candidate.photo_data_url = photo_data_url
                            db_session.commit()
                            updated += 1

                            if updated % 50 == 0:
                                print(f"  ✓ {updated} fotos procesadas...")

                except Exception as e:
                    errors += 1
                    if errors < 5:
                        print(f"  ⚠ Error en registro {idx}: {str(e)[:50]}")

            db_session.close()

            print(f"\n✓ Fotos extraídas: {updated}")
            print(f"✗ Errores: {errors}")

            if updated > 0:
                print("\n✅ EXTRACCIÓN EXITOSA")
                return 0
            else:
                print("\n⚠ No se extrajeron fotos")
                return 1

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
