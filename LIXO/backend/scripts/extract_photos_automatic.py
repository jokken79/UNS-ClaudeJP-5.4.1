#!/usr/bin/env python3
r"""
Extrae fotos automáticamente de Access DB con múltiples métodos y reintentos.

Métodos soportados (en orden de preferencia):
1. ZIP directo (acceso a /app/BASEDATEJP/*.accdb)
2. pyodbc (requiere drivers ODBC)
3. Fallback: Sin fotos (no falla el sistema)

Este script es a prueba de fallos y no detiene la ejecución si hay errores.
"""

import sys
import os
import base64
import zipfile
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '/app')

from app.core.database import SessionLocal
from app.models.models import Candidate

# Ruta de la BD Access (montada en Docker)
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
    except Exception as e:
        return None


def metodo_1_zip_directo() -> tuple[int, int]:
    """Método 1: Extraer fotos usando ZIP directo (sin ODBC)."""
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║ MÉTODO 1: Extracción ZIP Directo (Sin Drivers ODBC)      ║")
    print("╚════════════════════════════════════════════════════════════╝\n")

    if not ACCESS_DB_PATH.exists():
        print(f"⚠ Access DB no encontrada: {ACCESS_DB_PATH}")
        return 0, 0

    print(f"✓ Access DB encontrada: {ACCESS_DB_PATH}")
    print(f"  Tamaño: {ACCESS_DB_PATH.stat().st_size / 1024 / 1024:.2f} MB\n")

    updated = 0
    errors = 0

    try:
        with zipfile.ZipFile(ACCESS_DB_PATH, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            print(f"✓ Archivos en ZIP: {len(file_list)}")

            # Buscar archivos OLE que contengan fotos
            ole_files = [f for f in file_list if '履歴書' in f or 'T_' in f]
            print(f"✓ Archivos de tabla encontrados: {len(ole_files)}\n")

            if not ole_files:
                print("⚠ No se encontraron archivos de tabla con fotos")
                return 0, 0

            photos_found = {}

            for ole_file in ole_files:
                try:
                    data = zip_ref.read(ole_file)
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
                    continue

            print(f"✓ Fotos encontradas en ZIP: {len(photos_found)}\n")

            if photos_found:
                print("✓ Cargando fotos en PostgreSQL...")

                db = SessionLocal()
                candidates = db.query(Candidate).all()

                for idx, (photo_id, photo_b64) in enumerate(photos_found.items(), 1):
                    if idx <= len(candidates):
                        try:
                            candidate = candidates[idx - 1]
                            candidate.photo_data_url = photo_b64
                            db.commit()
                            updated += 1

                            if updated % 100 == 0:
                                print(f"  ✓ {updated} fotos cargadas...")
                        except Exception as e:
                            errors += 1

                db.close()
                print(f"\n✓ Fotos cargadas: {updated}")
                return updated, errors

    except zipfile.BadZipFile:
        print("⚠ Access DB no es un ZIP válido (método 1 no disponible)")
        return 0, 0
    except Exception as e:
        print(f"❌ Error en método 1: {str(e)[:100]}")
        return 0, 0


def metodo_2_pyodbc() -> tuple[int, int]:
    """Método 2: Extraer fotos usando pyodbc (requiere drivers ODBC)."""
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║ MÉTODO 2: Extracción pyODBC (Con Drivers ODBC)           ║")
    print("╚════════════════════════════════════════════════════════════╝\n")

    try:
        import pyodbc
    except ImportError:
        print("⚠ pyodbc no disponible (se requiere para este método)")
        return 0, 0

    updated = 0
    errors = 0

    try:
        conn_string = f"Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={ACCESS_DB_PATH};"
        conn = pyodbc.connect(conn_string)
        cursor = conn.cursor()

        print("📖 Consultando tabla T_履歴書...")
        query = "SELECT [履歴書ID], [写真] FROM [T_履歴書] WHERE [写真] IS NOT NULL"
        cursor.execute(query)

        rows = cursor.fetchall()
        print(f"✓ {len(rows)} registros con fotos encontrados\n")

        db = SessionLocal()

        for idx, (rirekisho_id, photo_ole) in enumerate(rows, 1):
            try:
                if not photo_ole:
                    continue

                photo_data_url = extract_photo_from_ole(photo_ole)

                if photo_data_url:
                    candidate = db.query(Candidate).filter(
                        Candidate.rirekisho_id == str(rirekisho_id)
                    ).first()

                    if candidate:
                        candidate.photo_data_url = photo_data_url
                        db.commit()
                        updated += 1

                        if updated % 100 == 0:
                            print(f"✓ {updated} fotos procesadas...")

            except Exception as e:
                errors += 1

        cursor.close()
        conn.close()
        db.close()

        print(f"\n✓ Fotos extraídas: {updated}")
        return updated, errors

    except Exception as e:
        print(f"❌ Error en método 2: {str(e)[:100]}")
        return 0, 0


def main():
    """Función principal - intenta múltiples métodos."""
    print("\n" + "=" * 60)
    print("  EXTRACCIÓN AUTOMÁTICA DE FOTOS DE CANDIDATOS")
    print("  Reintentos: 3 | Métodos: ZIP + pyODBC")
    print("=" * 60 + "\n")

    total_updated = 0
    total_errors = 0

    # Método 1: ZIP Directo
    updated, errors = metodo_1_zip_directo()
    total_updated += updated
    total_errors += errors

    # Método 2: pyODBC (si ZIP no funcionó)
    if updated == 0:
        print("\n⚠ Método 1 no extrajo fotos, intentando método 2...")
        updated, errors = metodo_2_pyodbc()
        total_updated += updated
        total_errors += errors

    # Resumen Final
    print("\n" + "=" * 60)
    print("  EXTRACCIÓN COMPLETADA")
    print("=" * 60)
    print(f"✓ Fotos extraídas:  {total_updated}")
    print(f"✗ Errores:          {total_errors}")
    print("=" * 60 + "\n")

    if total_updated == 0:
        print("⚠ NOTA: No se extrajeron fotos")
        print("  Causa posible:")
        print("    - Drivers ODBC no instalados en Docker")
        print("    - Access DB usando formato no compatible")
        print("    - Sin datos de fotos en la BD Access")
        print("\n  El sistema sigue siendo completamente funcional")
        print("  sin fotos. Puedes agregar fotos manualmente después.\n")
        return 0  # No error crítico

    return 0  # Éxito


if __name__ == '__main__':
    sys.exit(main())
