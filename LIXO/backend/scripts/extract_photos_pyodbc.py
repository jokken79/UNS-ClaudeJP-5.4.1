"""
Extract Photos from Access Database using pyodbc

This script uses pyodbc instead of pywin32 to avoid Access database locking issues.
It successfully connects and extracts photos using the alternative method.
"""

import sys
import os
import json
import logging
import base64
import struct
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# Configure logging with UTF-8 encoding to avoid cp932 issues
log_file = f'extract_photos_pyodbc_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
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

def extract_photos_using_pyodbc(access_db_path: Path) -> Dict[str, Any]:
    """Extract photos using pyodbc instead of pywin32"""
    
    logger.info(f"\nStarting photo extraction using pyodbc from: {access_db_path}")

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
        
        # Find the table with photos (likely T_履歴書 or similar)
        photo_table = None
        for table_info in tables:
            table_name = table_info[2]
            logger.debug(f"Checking table: {table_name}")
            if "履歴書" in table_name or "履歴" in table_name or "RIREKISHO" in table_name.upper():
                photo_table = table_name
                logger.info(f"Found photo table: {photo_table}")
                break
        
        if not photo_table:
            # Try to find table with photo-related columns
            logger.info("Photo table not found by name, searching for photo columns...")
            for table_info in tables:
                table_name = table_info[2]
                try:
                    columns = cursor.columns(table=table_name).fetchall()
                    for col_info in columns:
                        col_name = col_info[2]
                        if "写真" in col_name or "Photo" in col_name or "photo" in col_name:
                            photo_table = table_name
                            logger.info(f"Found table with photo column: {photo_table} (column: {col_name})")
                            break
                    if photo_table:
                        break
                except Exception as e:
                    logger.debug(f"Error checking table {table_name}: {e}")
                    continue
        
        if not photo_table:
            logger.warning("No photo table found, trying all tables...")
            # As a last resort, try the first few tables
            for table_info in tables[:5]:
                table_name = table_info[2]
                try:
                    # Test if we can query this table
                    test_query = f"SELECT TOP 1 * FROM [{table_name}]"
                    cursor.execute(test_query)
                    row = cursor.fetchone()
                    if row:
                        photo_table = table_name
                        logger.info(f"Using table: {photo_table}")
                        break
                except Exception as e:
                    logger.debug(f"Cannot query table {table_name}: {e}")
                    continue
        
        if not photo_table:
            logger.error("No suitable table found for photo extraction")
            return {"error": "no_photo_table_found"}
        
        # Get table structure
        columns = cursor.columns(table=photo_table).fetchall()
        logger.info(f"Table {photo_table} has {len(columns)} columns")
        
        # Find photo column
        photo_column = None
        for col_info in columns:
            col_name = col_info[2]
            col_type = col_info[3]
            logger.debug(f"Column: {col_name} (Type: {col_type})")
            if "写真" in col_name or "Photo" in col_name or "photo" in col_name:
                photo_column = col_name
                logger.info(f"Found photo column: {photo_column}")
                break
        
        if not photo_column:
            logger.warning("Photo column not found by name, trying OLE columns...")
            for col_info in columns:
                col_name = col_info[2]
                col_type = col_info[3]
                # OLE Object columns in Access typically have type -155 (LONGVARBINARY) or similar
                if col_type in [-155, -4, -3]:  # OLE Object, LONGVARBINARY, VARBINARY
                    photo_column = col_name
                    logger.info(f"Found potential photo column: {photo_column} (Type: {col_type})")
                    break
        
        if not photo_column:
            logger.error("No photo column found")
            return {"error": "no_photo_column_found"}
        
        # Extract photos
        logger.info(f"Extracting photos from table {photo_table}, column {photo_column}...")
        
        # First, get count
        count_query = f"SELECT COUNT(*) FROM [{photo_table}] WHERE [{photo_column}] IS NOT NULL"
        cursor.execute(count_query)
        total_with_photos = cursor.fetchone()[0]
        logger.info(f"Found {total_with_photos} records with photos")
        
        # Extract data
        query = f"SELECT * FROM [{photo_table}] WHERE [{photo_column}] IS NOT NULL"
        cursor.execute(query)
        
        mappings = {}
        total_records = 0
        extracted_photos = 0
        errors = 0
        
        # Get column names to find ID column
        column_names = [desc[0] for desc in cursor.description]
        logger.debug(f"Columns: {column_names}")
        
        # Find ID column (first column or one with 'ID' in name)
        id_column = column_names[0]  # Use first column as ID
        for col_name in column_names:
            if "ID" in col_name.upper() or "番号" in col_name:
                id_column = col_name
                break
        
        logger.info(f"Using {id_column} as record ID")
        
        rows = cursor.fetchall()
        logger.info(f"Processing {len(rows)} records...")
        
        for row in rows:
            total_records += 1
            
            try:
                # Get record ID
                record_id = str(row[id_column]) if row[id_column] else f"record_{total_records}"
                
                # Get photo data
                photo_data = row[photo_column]
                
                if photo_data:
                    try:
                        # Convert binary data to base64
                        if isinstance(photo_data, bytes):
                            base64_data = base64.b64encode(photo_data).decode('utf-8')
                            photo_data_url = f"data:image/jpeg;base64,{base64_data}"
                            mappings[record_id] = photo_data_url
                            extracted_photos += 1
                        else:
                            logger.debug(f"Photo data for {record_id} is not binary: {type(photo_data)}")
                    
                    except Exception as e:
                        errors += 1
                        logger.debug(f"Error processing photo for {record_id}: {e}")
                
                if total_records % 50 == 0:
                    logger.info(f"  Processed {total_records} records, extracted {extracted_photos} photos")
            
            except Exception as e:
                errors += 1
                logger.debug(f"Error processing record {total_records}: {e}")
        
        conn.close()
        
        logger.info(f"\nExtraction complete:")
        logger.info(f"  Total records processed: {total_records}")
        logger.info(f"  Photos extracted: {extracted_photos}")
        logger.info(f"  Errors: {errors}")
        
        return {
            "success": True,
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

def save_photo_mappings(mappings: Dict, output_path: Path) -> bool:
    """Save photo mappings to JSON file"""
    
    try:
        output = {
            "timestamp": datetime.now().isoformat(),
            "source": "pyodbc_extract_from_databasejp",
            "method": "pyodbc",
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
    """Main extraction workflow using pyodbc"""
    
    logger.info("=" * 80)
    logger.info("EXTRACT PHOTOS USING PYODBC")
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
    
    # Extract photos using pyodbc
    result = extract_photos_using_pyodbc(access_db)
    
    if "error" in result:
        logger.error(f"Extraction failed: {result['error']}")
        return 1
    
    # Save mappings
    if result.get("mappings"):
        if save_photo_mappings(result["mappings"], output_file):
            logger.info("\n" + "=" * 80)
            logger.info("EXTRACTION SUCCESSFUL")
            logger.info("=" * 80)
            logger.info(f"Photos extracted: {result['with_photos']}")
            logger.info(f"Output file: {output_file}")
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