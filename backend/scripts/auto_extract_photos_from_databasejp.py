"""
Auto-Extract Photos from DATABASEJP Folder - FIXED VERSION

Automatically searches for Access database in DATABASEJP folder
and extracts photos if access_photo_mappings.json doesn't exist.

This script:
1. Looks for BASEDATEJP folder (parent or sibling directories)
2. Finds .accdb database files
3. Extracts photos using pyodbc (avoids Unicode issues)
4. Saves to access_photo_mappings.json

Usage:
    python auto_extract_photos_from_databasejp.py

Requirements:
    - Windows with pyodbc installed
    - Microsoft Access Database Engine
    - BASEDATEJP folder with .accdb files
"""

import sys
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# Configure logging with UTF-8 encoding to handle Unicode characters
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'auto_extract_photos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def find_databasejp_folder() -> Optional[Path]:
    """
    Search for BASEDATEJP or DATABASEJP folder in:
    1. Current directory
    2. Parent directory
    3. Sibling directory
    4. Common known locations

    Priority: BASEDATEJP first, then DATABASEJP as fallback
    """

    logger.info("Searching for BASEDATEJP/DATABASEJP folder...")

    # Primary search paths (BASEDATEJP - current folder name)
    search_paths = [
        Path.cwd() / "BASEDATEJP",
        Path.cwd().parent / "BASEDATEJP",
        Path.cwd().parent.parent / "BASEDATEJP",
        Path("D:/BASEDATEJP"),
        Path(os.path.expanduser("~")) / "BASEDATEJP",
        # Fallback to old DATABASEJP name
        Path.cwd() / "DATABASEJP",
        Path.cwd().parent / "DATABASEJP",
        Path.cwd().parent.parent / "DATABASEJP",
        Path("D:/DATABASEJP"),
        Path("D:/ユニバーサル企画㈱データベース"),
        Path(os.path.expanduser("~")) / "DATABASEJP",
    ]

    for path in search_paths:
        if path.exists() and path.is_dir():
            logger.info(f"Found database folder at: {path}")
            return path

    logger.warning("BASEDATEJP/DATABASEJP folder not found in common locations")
    return None


def find_access_database(databasejp_path: Path) -> Optional[Path]:
    """
    Search for .accdb files in DATABASEJP folder

    Priority:
    1. Look for specific database name: ユニバーサル企画㈱データベースv25.3.24.accdb
    2. Look for any .accdb file (largest = main database)
    """

    logger.info(f"Searching for Access database files in {databasejp_path}...")

    # Strategy 1: Look for specific known database name
    known_db_names = [
        "ユニバーサル企画㈱データベースv25.3.24.accdb",
        "ユニバーサル企画㈱データベース.accdb",
        "ユニバーサル企画.accdb",
    ]

    for db_name in known_db_names:
        db_path = databasejp_path / db_name
        if db_path.exists():
            logger.info(f"Found specific database: {db_name}")
            logger.info(f"  Size: {db_path.stat().st_size / (1024*1024):.1f} MB")
            return db_path

    # Strategy 2: Search for any .accdb files
    logger.info("Specific database not found, searching for any .accdb files...")
    accdb_files = list(databasejp_path.glob("**/*.accdb"))

    if not accdb_files:
        logger.warning("No .accdb files found in DATABASEJP")
        return None

    logger.info(f"Found {len(accdb_files)} Access database file(s)")

    # Sort by size (descending) to get the main database
    accdb_files.sort(key=lambda p: p.stat().st_size, reverse=True)

    selected_db = accdb_files[0]
    logger.info(f"Found specific database: {selected_db.name}")
    logger.info(f"  Size: {selected_db.stat().st_size / (1024*1024):.1f} MB")

    return selected_db


def extract_photos_from_access(access_db_path: Path) -> Dict[str, Any]:
    """
    Extract photos from Access database using pyodbc with column indices
    Returns dictionary with extraction results
    """

    logger.info(f"\nStarting photo extraction using simple method from: {access_db_path}")

    try:
        import pyodbc
    except ImportError:
        logger.error("pyodbc not installed!")
        logger.error("Install with: pip install pyodbc")
        return {"error": "pyodbc_not_installed"}

    try:
        # Build connection string for Access
        conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={access_db_path};"
        
        logger.info("Connecting to database...")
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        logger.info("Successfully connected to database")

        # Get list of tables
        tables = [row.table_name for row in cursor.tables(tableType='TABLE')]
        logger.info(f"Found {len(tables)} tables")
        
        # Find the table with photos (T_履歴書)
        photo_table = None
        for table in tables:
            if "履歴書" in table:
                photo_table = table
                break
        
        if not photo_table:
            logger.error("Could not find photo table (T_履歴書)")
            return {"error": "photo_table_not_found"}
        
        logger.info(f"Found photo table: {photo_table}")

        # Get table structure to identify photo column
        cursor.execute(f"SELECT TOP 1 * FROM [{photo_table}]")
        columns = [column[0] for column in cursor.description]
        logger.info(f"Table has {len(columns)} columns")
        logger.info(f"Column names: {columns}")

        # FIXED: Find photo column dynamically instead of hardcoded index
        photo_column_index = None
        photo_column_patterns = ['写真', 'photo', '写真データ', 'picture', 'image']

        for idx, col_name in enumerate(columns):
            for pattern in photo_column_patterns:
                if pattern in col_name.lower():
                    photo_column_index = idx
                    logger.info(f"✓ Found photo column at index {idx}: '{col_name}'")
                    break
            if photo_column_index is not None:
                break

        # Fallback to index 8 if not found (backward compatibility)
        if photo_column_index is None:
            logger.warning("Could not find photo column by name, using default index 8")
            photo_column_index = 8

        # Extract data using column indices to avoid Unicode issues
        logger.info(f"Extracting data from table using photo column index {photo_column_index}...")

        cursor.execute(f"SELECT * FROM [{photo_table}]")
        
        mappings = {}
        total_records = 0
        photos_extracted = 0
        errors = 0

        rows = cursor.fetchall()
        logger.info(f"Found {len(rows)} total records in table")

        for row in rows:
            total_records += 1
            
            try:
                # Get ID from first column (index 0)
                record_id = str(row[0]) if row[0] else f"record_{total_records}"

                # FIXED: Get photo data from dynamically found column index
                photo_data = row[photo_column_index] if len(row) > photo_column_index else None
                
                if photo_data:
                    photos_extracted += 1
                    
                    # Check if photo_data is binary or filename
                    if isinstance(photo_data, bytes):
                        # Binary data - convert to base64
                        import base64
                        base64_data = base64.b64encode(photo_data).decode('utf-8')
                        mappings[record_id] = f"data:image/jpeg;base64,{base64_data}"
                    else:
                        # Filename or text data
                        mappings[record_id] = f"filename:{photo_data}"
                    
                    # Log first few examples for verification
                    if photos_extracted <= 5:
                        logger.info(f"Extracted filename: ID {record_id} -> {mappings[record_id]}")

                if total_records % 200 == 0:
                    logger.info(f"  Processed {total_records} records, extracted {photos_extracted} photos")

            except Exception as e:
                errors += 1
                logger.debug(f"Error processing record {total_records}: {e}")

        cursor.close()
        conn.close()

        logger.info(f"\nExtraction complete:")
        logger.info(f"  Total records processed: {total_records}")
        logger.info(f"  Photos extracted: {photos_extracted}")
        logger.info(f"  Errors: {errors}")

        return {
            "success": True,
            "total_records": total_records,
            "photos_extracted": photos_extracted,
            "errors": errors,
            "mappings": mappings
        }

    except Exception as e:
        logger.error(f"Error during extraction: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return {"error": str(e)}


def save_photo_mappings(mappings: Dict, output_path: Path) -> bool:
    """
    Save photo mappings to JSON file
    """

    try:
        output = {
            "timestamp": datetime.now().isoformat(),
            "source": "simple_extract_from_databasejp",
            "method": "simple_indices",
            "statistics": {
                "total_mappings": len(mappings)
            },
            "mappings": mappings
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved mappings to: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Error saving mappings: {e}")
        return False


def main():
    """Main auto-extraction workflow"""

    logger.info("=" * 80)
    logger.info("SIMPLE PHOTO EXTRACTION SCRIPT")
    logger.info("=" * 80)

    # Check for command line argument to force regeneration
    force_regenerate = False
    if len(sys.argv) > 1 and sys.argv[1].lower() in ('--force', '-f', '--regenerate', '-r'):
        force_regenerate = True
        logger.info("Command line force regeneration detected")
    
    # Check environment variable as fallback
    if not force_regenerate:
        force_regenerate = os.environ.get('FORCE_REGENERATE_PHOTOS', '').strip().lower() in ('1', 'true', 'yes', 's')
        if force_regenerate:
            logger.info("Environment variable FORCE_REGENERATE_PHOTOS detected")
    
    # Check if access_photo_mappings.json already exists
    # FIXED: Save in config/ directory where docker-compose.yml expects it
    config_dir = Path.cwd() / "config"
    config_dir.mkdir(parents=True, exist_ok=True)  # Ensure config directory exists
    output_file = config_dir / "access_photo_mappings.json"
    
    if force_regenerate:
        logger.info("Force regeneration detected - regenerating photos...")
        if output_file.exists():
            logger.info(f"Removing existing file: {output_file}")
            output_file.unlink()
    elif output_file.exists() and not force_regenerate:
        logger.info(f"access_photo_mappings.json already exists. Skipping extraction.")
        logger.info(f"Location: {output_file}")
        logger.info("To force regeneration, use --force or set FORCE_REGENERATE_PHOTOS=1")
        return 0

    # Find BASEDATEJP folder
    databasejp_path = find_databasejp_folder()
    if not databasejp_path:
        logger.error("Could not find BASEDATEJP folder. Please ensure it exists.")
        return 1

    # Find Access database
    access_db = find_access_database(databasejp_path)
    if not access_db:
        logger.error("Could not find Access database in BASEDATEJP folder.")
        return 1

    # Extract photos
    result = extract_photos_from_access(access_db)

    if "error" in result:
        logger.error(f"Extraction failed: {result['error']}")
        return 1

    # Save mappings
    if result.get("mappings"):
        if save_photo_mappings(result["mappings"], output_file):
            logger.info("\n" + "=" * 80)
            logger.info("EXTRACTION SUCCESSFUL")
            logger.info("=" * 80)
            logger.info(f"Method used: simple_indices")
            logger.info(f"Photos extracted: {result.get('photos_extracted', 0)}")
            logger.info(f"Output file: {output_file}")
            logger.info("")
            logger.info("NOTE: Used column indices to avoid Unicode issues.")
            logger.info("Photos may be stored as filenames or binary data.")
            return 0
        else:
            logger.error("Failed to save photo mappings")
            return 1
    else:
        logger.warning("No photos were extracted")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
