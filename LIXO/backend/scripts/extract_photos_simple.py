"""
Simple Photo Extraction Script

This script uses a simpler approach to avoid Unicode column name issues.
It extracts photos using column indices instead of names.
"""

import sys
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# Configure logging with UTF-8 encoding to avoid cp932 issues
log_file = f'extract_photos_simple_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def find_databasejp_folder() -> Optional[Path]:
    """Search for BASEDATEJP folder"""
    
    logger.info("Searching for BASEDATEJP folder...")
    
    search_paths = [
        Path.cwd() / "BASEDATEJP",
        Path.cwd().parent / "BASEDATEJP",
        Path.cwd().parent.parent / "BASEDATEJP",
        Path("D:/BASEDATEJP"),
        Path(os.path.expanduser("~")) / "BASEDATEJP",
    ]

    for path in search_paths:
        if path.exists() and path.is_dir():
            logger.info(f"Found database folder at: {path}")
            return path

    logger.warning("BASEDATEJP folder not found")
    return None

def find_access_database(databasejp_path: Path) -> Optional[Path]:
    """Search for .accdb files in BASEDATEJP folder"""
    
    logger.info(f"Searching for Access database files in {databasejp_path}...")
    
    # Look for the specific known database name
    known_db_names = [
        "ユニバーサル企画㈱データベースv25.3.24_be.accdb",
        "ユニバーサル企画㈱データベースv25.3.24.accdb",
        "ユニバーサル企画㈱データベース.accdb",
    ]

    for db_name in known_db_names:
        db_path = databasejp_path / db_name
        if db_path.exists():
            logger.info(f"Found specific database: {db_name}")
            logger.info(f"  Size: {db_path.stat().st_size / (1024*1024):.1f} MB")
            return db_path

    # Search for any .accdb files
    logger.info("Specific database not found, searching for any .accdb files...")
    accdb_files = list(databasejp_path.glob("**/*.accdb"))

    if not accdb_files:
        logger.warning("No .accdb files found in BASEDATEJP")
        return None

    logger.info(f"Found {len(accdb_files)} Access database file(s)")

    # Sort by size (descending) to get the main database
    accdb_files.sort(key=lambda p: p.stat().st_size, reverse=True)

    selected_db = accdb_files[0]
    logger.info(f"Selected largest database: {selected_db.name} ({selected_db.stat().st_size / (1024*1024):.1f} MB)")

    return selected_db

def extract_photos_simple(access_db_path: Path) -> Dict[str, Any]:
    """Extract photos using simple approach"""
    
    logger.info(f"\nStarting photo extraction using simple method from: {access_db_path}")

    try:
        import pyodbc
    except ImportError:
        logger.error("pyodbc not installed!")
        logger.error("Install with: pip install pyodbc")
        return {"error": "pyodbc_not_installed"}

    try:
        # Connection string for Access
        conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={access_db_path};"
        
        logger.info("Connecting to database...")
        conn = pyodbc.connect(conn_str)
        logger.info("Successfully connected to database")
        
        cursor = conn.cursor()
        
        # Get all tables
        tables = cursor.tables(tableType='TABLE').fetchall()
        logger.info(f"Found {len(tables)} tables")
        
        # Find the table with photos (T_履歴書)
        photo_table = None
        for table_info in tables:
            table_name = table_info[2]
            logger.debug(f"Checking table: {table_name}")
            if "履歴書" in table_name or "履歴" in table_name:
                photo_table = table_name
                logger.info(f"Found photo table: {photo_table}")
                break
        
        if not photo_table:
            logger.error("Photo table T_履歴書 not found")
            return {"error": "no_photo_table_found"}
        
        # Simple query to get all data from the table
        logger.info("Extracting data from table...")
        query = f"SELECT * FROM [{photo_table}]"
        cursor.execute(query)
        
        # Get all rows
        rows = cursor.fetchall()
        logger.info(f"Found {len(rows)} total records in table")
        
        # Extract photos using column indices
        # Based on analysis: ID is column 0, Photo is column 8 (9th column)
        mappings = {}
        total_records = 0
        extracted_photos = 0
        errors = 0
        
        for row in rows:
            total_records += 1
            
            try:
                # Column 0: ID (T_履歴書ID)
                record_id = str(row[0]) if row[0] else f"record_{total_records}"
                
                # Column 8: Photo (写真)
                photo_value = row[8] if len(row) > 8 else None
                
                if photo_value:
                    # Check if it's a filename (string) or binary data
                    if isinstance(photo_value, str):
                        # It's a filename
                        photo_filename = photo_value.strip()
                        if photo_filename and ('.' in photo_filename.lower() and any(ext in photo_filename.lower() for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif'])):
                            photo_data_url = f"filename:{photo_filename}"
                            mappings[record_id] = photo_data_url
                            extracted_photos += 1
                            if extracted_photos <= 5:  # Show first few examples
                                logger.info(f"Extracted filename: ID {record_id} -> {photo_filename}")
                    elif isinstance(photo_value, bytes):
                        # It's binary data
                        import base64
                        base64_data = base64.b64encode(photo_value).decode('utf-8')
                        photo_data_url = f"data:image/jpeg;base64,{base64_data}"
                        mappings[record_id] = photo_data_url
                        extracted_photos += 1
                        if extracted_photos <= 5:  # Show first few examples
                            logger.info(f"Extracted binary: ID {record_id} -> {len(photo_value)} bytes")
                
            except Exception as e:
                errors += 1
                logger.debug(f"Error processing record {total_records}: {e}")
            
            if total_records % 200 == 0:
                logger.info(f"  Processed {total_records} records, extracted {extracted_photos} photos")
        
        conn.close()
        
        logger.info(f"\nExtraction complete:")
        logger.info(f"  Total records processed: {total_records}")
        logger.info(f"  Photos extracted: {extracted_photos}")
        logger.info(f"  Errors: {errors}")
        
        return {
            "success": True,
            "method": "simple_indices",
            "total_records": total_records,
            "with_photos": extracted_photos,
            "errors": errors,
            "mappings": mappings
        }
    
    except Exception as e:
        logger.error(f"Error during extraction: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return {"error": str(e)}

def save_photo_mappings(mappings: Dict, output_path: Path, method: str) -> bool:
    """Save photo mappings to JSON file"""
    
    try:
        output = {
            "timestamp": datetime.now().isoformat(),
            "source": "simple_extract_from_databasejp",
            "method": method,
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
    """Main extraction workflow"""
    
    logger.info("=" * 80)
    logger.info("SIMPLE PHOTO EXTRACTION SCRIPT")
    logger.info("=" * 80)
    
    # Check if access_photo_mappings.json already exists
    output_file = Path.cwd() / "access_photo_mappings.json"
    if output_file.exists():
        logger.info(f"access_photo_mappings.json already exists.")
        response = input("Overwrite existing file? (S/N): ")
        if response.upper() not in ['S', 'SI']:
            logger.info("Extraction cancelled.")
            return 0
    
    # Find BASEDATEJP folder
    databasejp_path = find_databasejp_folder()
    if not databasejp_path:
        logger.error("Could not find BASEDATEJP folder.")
        return 1
    
    # Find Access database
    access_db = find_access_database(databasejp_path)
    if not access_db:
        logger.error("Could not find Access database in BASEDATEJP folder.")
        return 1
    
    # Extract photos
    result = extract_photos_simple(access_db)
    
    if "error" in result:
        logger.error(f"Extraction failed: {result['error']}")
        return 1
    
    # Save mappings
    if result.get("mappings"):
        method = result.get("method", "unknown")
        if save_photo_mappings(result["mappings"], output_file, method):
            logger.info("\n" + "=" * 80)
            logger.info("EXTRACTION SUCCESSFUL")
            logger.info("=" * 80)
            logger.info(f"Method used: {method}")
            logger.info(f"Photos extracted: {result['with_photos']}")
            logger.info(f"Output file: {output_file}")
            
            if method == "simple_indices":
                logger.info("\nNOTE: Used column indices to avoid Unicode issues.")
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