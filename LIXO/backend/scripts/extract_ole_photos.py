"""
Extract OLE photos from Access database
========================================

Access stores photos as OLE objects (LONGCHAR type).
This script extracts them properly.
"""
import pyodbc
import struct
from pathlib import Path
import sys

# Add colors for Windows
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

def extract_ole_image(ole_data):
    """
    Extract image data from OLE object

    OLE format has a header that needs to be stripped.
    The actual image data starts after the OLE header.
    """
    if not ole_data or not isinstance(ole_data, (bytes, str)):
        return None

    # Convert string to bytes if needed
    if isinstance(ole_data, str):
        try:
            ole_data = ole_data.encode('latin-1')
        except:
            return None

    # OLE objects often start with specific headers
    # Try to find JPEG signature (FFD8FF)
    jpeg_start = ole_data.find(b'\xff\xd8\xff')
    if jpeg_start >= 0:
        return ole_data[jpeg_start:]

    # Try to find PNG signature (89504E47)
    png_start = ole_data.find(b'\x89PNG')
    if png_start >= 0:
        return ole_data[png_start:]

    # Try to find BMP signature (424D)
    bmp_start = ole_data.find(b'BM')
    if bmp_start >= 0 and bmp_start < 100:  # BMP should be near start
        return ole_data[bmp_start:]

    # If no signature found, try common OLE offsets
    common_offsets = [0, 20, 40, 78, 300]
    for offset in common_offsets:
        if offset < len(ole_data):
            chunk = ole_data[offset:]
            # Check if it looks like image data
            if chunk.startswith(b'\xff\xd8\xff') or chunk.startswith(b'\x89PNG') or chunk.startswith(b'BM'):
                return chunk

    return None

def main():
    """Extract all photos from Access database"""

    # Configuration
    project_root = Path(__file__).parent.parent.parent
    db_path = project_root / "base-datos" / "ユニバーサル企画㈱データベースv25.3.24.accdb"
    output_dir = project_root / "uploads" / "photos" / "candidates"

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{Colors.CYAN}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}>>> EXTRACTOR DE FOTOS OLE DESDE ACCESS{Colors.ENDC}")
    print(f"{Colors.CYAN}{'=' * 80}{Colors.ENDC}\n")

    print(f"{Colors.BLUE}[INFO]{Colors.ENDC} Base de datos: {db_path.name}")
    print(f"{Colors.BLUE}[INFO]{Colors.ENDC} Carpeta destino: {output_dir}")
    print()

    try:
        # Connect to Access
        conn_str = (
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={db_path};'
        )
        print(f"{Colors.BLUE}[INFO]{Colors.ENDC} Conectando a Access...")
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        print(f"{Colors.GREEN}[OK]{Colors.ENDC} Conexion exitosa\n")

        # Query with photos
        print(f"{Colors.BLUE}[INFO]{Colors.ENDC} Consultando candidatos con fotos...")
        cursor.execute("SELECT 履歴書ID, 氏名, 写真 FROM T_履歴書 WHERE 写真 IS NOT NULL")

        # Count total
        rows = cursor.fetchall()
        total = len(rows)
        print(f"{Colors.BLUE}[INFO]{Colors.ENDC} Encontrados: {total} candidatos con fotos\n")

        if total == 0:
            print(f"{Colors.YELLOW}[AVISO]{Colors.ENDC} No hay fotos para extraer")
            return 0

        # Extract photos
        print(f"{Colors.BLUE}[INFO]{Colors.ENDC} Extrayendo fotos...")
        stats = {'success': 0, 'failed': 0, 'skipped': 0}

        for idx, row in enumerate(rows, 1):
            rirekisho_id = row[0]
            name = row[1]
            photo_data = row[2]

            # Show progress
            if idx % 100 == 0:
                progress = (idx / total) * 100
                bar_len = 40
                filled = int(bar_len * idx / total)
                bar = '#' * filled + '-' * (bar_len - filled)
                print(f"\r{Colors.CYAN}[{bar}]{Colors.ENDC} {progress:.1f}% ({idx}/{total})", end='', flush=True)

            # Skip if no data
            if not photo_data:
                stats['skipped'] += 1
                continue

            try:
                # Extract image from OLE
                image_data = extract_ole_image(photo_data)

                if image_data:
                    # Determine extension
                    if image_data.startswith(b'\xff\xd8\xff'):
                        ext = 'jpg'
                    elif image_data.startswith(b'\x89PNG'):
                        ext = 'png'
                    elif image_data.startswith(b'BM'):
                        ext = 'bmp'
                    else:
                        ext = 'jpg'  # Default

                    # Save file
                    filename = f"candidate_{rirekisho_id}.{ext}"
                    filepath = output_dir / filename

                    with open(filepath, 'wb') as f:
                        f.write(image_data)

                    stats['success'] += 1
                else:
                    stats['failed'] += 1

            except Exception as e:
                stats['failed'] += 1

        # Final progress bar
        bar = '#' * 40
        print(f"\r{Colors.CYAN}[{bar}]{Colors.ENDC} 100.0% ({total}/{total})")
        print()

        # Summary
        print(f"\n{Colors.CYAN}{'=' * 80}{Colors.ENDC}")
        print(f"{Colors.BOLD}=== RESUMEN ==={Colors.ENDC}")
        print(f"{Colors.CYAN}{'=' * 80}{Colors.ENDC}\n")

        print(f"{Colors.BOLD}Total candidatos:{Colors.ENDC} {total}")
        print(f"{Colors.BOLD}Fotos extraidas:{Colors.ENDC} {stats['success']}")
        print(f"{Colors.BOLD}Fallidas:{Colors.ENDC} {stats['failed']}")
        print(f"{Colors.BOLD}Sin datos:{Colors.ENDC} {stats['skipped']}")

        if stats['success'] > 0:
            print(f"\n{Colors.GREEN}[OK]{Colors.ENDC} Fotos guardadas en: {output_dir}")

        print(f"\n{Colors.CYAN}{'=' * 80}{Colors.ENDC}\n")

        conn.close()
        return stats['success']

    except Exception as e:
        print(f"\n{Colors.RED}[ERROR]{Colors.ENDC} {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    extracted = main()
    sys.exit(0 if extracted > 0 else 1)
