"""
Extractor de fotos desde Access usando DAO (Data Access Objects)
=================================================================

Este script extrae fotos almacenadas como Attachments en Access 2007+.
Usa win32com.client con DAO para acceder a las tablas de attachments.

Requiere: pywin32 (pip install pywin32)
"""
import sys
import json
import base64
from pathlib import Path
from datetime import datetime

try:
    import win32com.client
except ImportError:
    print("[ERROR] pywin32 no esta instalado")
    print("[INFO] Instalar con: pip install pywin32")
    sys.exit(1)

# ANSI Colors for Windows cmd.exe
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_success(message):
    print(f"{Colors.GREEN}[OK] {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.RED}[ERROR] {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.YELLOW}[AVISO] {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.BLUE}[INFO] {message}{Colors.ENDC}")

def extract_photos_from_access(db_path: Path, output_file: Path):
    """
    Extrae fotos desde Access usando DAO API

    Args:
        db_path: Ruta al archivo .accdb
        output_file: Ruta donde guardar el JSON con fotos

    Returns:
        dict: Estadisticas de extraccion
    """
    print(f"\n{Colors.CYAN}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}>>> EXTRACTOR DE FOTOS - Access -> JSON (DAO){Colors.ENDC}")
    print(f"{Colors.CYAN}{'=' * 80}{Colors.ENDC}\n")

    print_info(f"Base de datos: {db_path.name}")
    print_info(f"Archivo salida: {output_file.name}")
    print()

    # Verificar que el archivo existe
    if not db_path.exists():
        print_error(f"No se encontro: {db_path}")
        return None

    stats = {
        'total_records': 0,
        'with_photo_field': 0,
        'photos_extracted': 0,
        'errors': 0
    }

    photos = {}

    try:
        # Crear engine DAO
        print_info("Iniciando DAO Engine...")
        engine = win32com.client.Dispatch("DAO.DBEngine.120")

        # Abrir base de datos
        print_info("Abriendo base de datos...")
        db = engine.OpenDatabase(str(db_path))

        # Abrir tabla de candidatos
        print_info("Abriendo tabla T_履歴書...")
        rs = db.OpenRecordset("T_履歴書")

        # Contar total de registros
        rs.MoveLast()
        total = rs.RecordCount
        rs.MoveFirst()

        print_info(f"Total de registros: {total}")
        print()
        print_info("Extrayendo fotos (puede tardar 2-3 minutos)...")
        print()

        # Procesar cada registro
        current = 0
        while not rs.EOF:
            current += 1
            stats['total_records'] += 1

            # Mostrar progreso cada 100 registros
            if current % 100 == 0:
                progress = (current / total) * 100
                bar_length = 40
                filled = int(bar_length * current / total)
                bar = '#' * filled + '-' * (bar_length - filled)
                print(f"\r{Colors.CYAN}[{bar}]{Colors.ENDC} {progress:.1f}% ({current}/{total})", end='', flush=True)

            try:
                # Obtener ID del candidato
                rirekisho_id = str(rs.Fields("履歴書ID").Value)

                # Intentar obtener el campo de foto (Attachment)
                photo_field = rs.Fields("写真")

                # Verificar si tiene attachments
                if photo_field.Value is not None:
                    stats['with_photo_field'] += 1

                    # Obtener recordset de attachments
                    rs_attach = photo_field.Value

                    # Si hay attachments
                    if rs_attach.RecordCount > 0:
                        rs_attach.MoveFirst()

                        # Obtener datos del primer attachment
                        file_data = rs_attach.Fields("FileData").Value

                        # Convertir a bytes array
                        if file_data:
                            # file_data es un array de bytes de COM
                            # Necesitamos convertirlo a bytes de Python
                            photo_bytes = bytes(file_data)

                            # Codificar en Base64
                            photo_base64 = base64.b64encode(photo_bytes).decode('utf-8')

                            # Crear Data URL
                            data_url = f"data:image/jpeg;base64,{photo_base64}"

                            # Guardar en diccionario
                            photos[rirekisho_id] = data_url
                            stats['photos_extracted'] += 1

            except Exception as e:
                stats['errors'] += 1
                # No imprimir errores individuales para no saturar la consola

            rs.MoveNext()

        # Progreso final
        bar = '#' * 40
        print(f"\r{Colors.CYAN}[{bar}]{Colors.ENDC} 100.0% ({total}/{total})")
        print()

        # Cerrar recordsets y base de datos
        rs.Close()
        db.Close()

        print_success("Extraccion completada")
        print()

        # Preparar datos para JSON
        output_data = {
            'timestamp': datetime.now().isoformat(),
            'access_database': str(db_path),
            'table': 'T_履歴書',
            'photo_field': '写真',
            'statistics': stats,
            'mappings': photos
        }

        # Guardar JSON
        print_info(f"Guardando JSON: {output_file}")
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        # Calcular tamano del archivo
        file_size_mb = output_file.stat().st_size / (1024 * 1024)
        print_success(f"Archivo guardado: {file_size_mb:.1f} MB")
        print()

        # Resumen
        print(f"{Colors.CYAN}{'=' * 80}{Colors.ENDC}")
        print(f"{Colors.BOLD}=== RESUMEN DE EXTRACCION ==={Colors.ENDC}")
        print(f"{Colors.CYAN}{'=' * 80}{Colors.ENDC}\n")

        print(f"{Colors.BOLD}Total registros:{Colors.ENDC}     {stats['total_records']}")
        print(f"{Colors.BOLD}Con campo foto:{Colors.ENDC}      {stats['with_photo_field']}")
        print(f"{Colors.BOLD}Fotos extraidas:{Colors.ENDC}     {stats['photos_extracted']}")
        print(f"{Colors.BOLD}Errores:{Colors.ENDC}             {stats['errors']}")

        if stats['photos_extracted'] > 0:
            print()
            print_success(f"Extraccion exitosa: {stats['photos_extracted']} fotos")

        print(f"\n{Colors.CYAN}{'=' * 80}{Colors.ENDC}\n")

        return stats

    except Exception as e:
        print()
        print_error(f"Error durante extraccion: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Funcion principal"""

    # Configuracion de rutas
    project_root = Path(__file__).parent.parent.parent
    db_path = project_root / "base-datos" / "ユニバーサル企画㈱データベースv25.3.24.accdb"
    output_file = project_root / "config" / "access_photo_mappings.json"

    # Verificar que la base de datos existe
    if not db_path.exists():
        print_error(f"Base de datos no encontrada: {db_path}")
        print_info("Asegurate de que la carpeta base-datos existe")
        sys.exit(1)

    # Extraer fotos
    start_time = datetime.now()

    stats = extract_photos_from_access(db_path, output_file)

    end_time = datetime.now()
    elapsed = (end_time - start_time).total_seconds()

    if stats and stats['photos_extracted'] > 0:
        print_info(f"Tiempo total: {elapsed:.1f} segundos")
        sys.exit(0)
    else:
        print_error("No se pudieron extraer fotos")
        sys.exit(1)

if __name__ == "__main__":
    main()
