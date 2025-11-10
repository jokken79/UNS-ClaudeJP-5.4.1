"""
Debug Script for Photo Extraction Issues

This script adds comprehensive logging to diagnose:
1. Unicode encoding errors (cp932 codec issues)
2. TableDefs access errors in Access database
"""

import sys
import os
import json
import logging
import locale
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# Configure logging with UTF-8 encoding to avoid cp932 issues
log_file = f'debug_extract_photos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def diagnose_system_environment():
    """Diagnose system environment and encoding issues"""
    
    logger.info("=" * 80)
    logger.info("DIAGNOSING SYSTEM ENVIRONMENT")
    logger.info("=" * 80)
    
    # Check Python version
    import platform
    logger.info(f"Python version: {platform.python_version()}")
    logger.info(f"System: {platform.system()}")
    logger.info(f"Architecture: {platform.architecture()}")
    
    # Check encoding
    logger.info(f"Default encoding: {sys.getdefaultencoding()}")
    logger.info(f"File system encoding: {sys.getfilesystemencoding()}")
    logger.info(f"Locale encoding: {locale.getpreferredencoding()}")
    
    # Check current directory
    logger.info(f"Current working directory: {os.getcwd()}")
    
    # Test Unicode characters
    try:
        test_unicode = "✓ Test Unicode: ✓ ✓ ✓"
        logger.info(f"Unicode test: {test_unicode}")
    except Exception as e:
        logger.error(f"Unicode test failed: {e}")
    
    return True

def test_pywin32_installation():
    """Test pywin32 installation and Access connectivity"""
    
    logger.info("=" * 80)
    logger.info("TESTING PYWIN32 INSTALLATION")
    logger.info("=" * 80)
    
    try:
        import win32com.client as win32
        logger.info("✓ pywin32 is installed")
        
        # Test Access application
        try:
            access_app = win32.Dispatch("Access.Application")
            logger.info("✓ Access application can be created")
            access_app.Quit()
        except Exception as e:
            logger.error(f"✗ Cannot create Access application: {e}")
            return False
            
    except ImportError as e:
        logger.error(f"✗ pywin32 not installed: {e}")
        logger.error("Install with: pip install pywin32")
        return False
    
    return True

def test_database_access(database_path: Path):
    """Test database access and TableDefs specifically"""
    
    logger.info("=" * 80)
    logger.info("TESTING DATABASE ACCESS")
    logger.info("=" * 80)
    
    if not database_path.exists():
        logger.error(f"Database file not found: {database_path}")
        return False
    
    logger.info(f"Testing access to: {database_path}")
    logger.info(f"File size: {database_path.stat().st_size / (1024*1024):.1f} MB")
    
    try:
        import win32com.client as win32
        
        # Test different connection methods
        methods = [
            ("GetObject", lambda: win32.GetObject(str(database_path))),
            ("Dispatch+OpenCurrentDatabase", lambda: create_access_with_open(database_path))
        ]
        
        def create_access_with_open(db_path):
            app = win32.Dispatch("Access.Application")
            app.OpenCurrentDatabase(str(db_path))
            return app
        
        for method_name, method_func in methods:
            try:
                logger.info(f"Testing method: {method_name}")
                access_app = method_func()
                logger.info(f"✓ {method_name} successful")
                
                # Test TableDefs access specifically
                try:
                    logger.info("Testing TableDefs access...")
                    table_defs = access_app.TableDefs
                    logger.info(f"✓ TableDefs object accessible: {type(table_defs)}")
                    
                    # Try to iterate through tables
                    table_count = 0
                    for table_obj in table_defs:
                        table_count += 1
                        logger.debug(f"  Table {table_count}: {table_obj.Name}")
                        if table_count > 5:  # Limit to avoid too much output
                            break
                    
                    logger.info(f"✓ Found {table_count} tables (showing first 5)")
                    
                except Exception as table_error:
                    logger.error(f"✗ TableDefs access failed: {table_error}")
                    logger.error(f"Error type: {type(table_error)}")
                    import traceback
                    logger.debug(traceback.format_exc())
                
                # Clean up
                try:
                    access_app.Quit()
                except:
                    pass
                    
                return True
                
            except Exception as method_error:
                logger.error(f"✗ {method_name} failed: {method_error}")
                logger.error(f"Error type: {type(method_error)}")
                continue
    
    except ImportError as e:
        logger.error(f"✗ Cannot import win32com: {e}")
        return False
    
    return False

def test_alternative_extraction_methods(database_path: Path):
    """Test alternative extraction methods"""
    
    logger.info("=" * 80)
    logger.info("TESTING ALTERNATIVE EXTRACTION METHODS")
    logger.info("=" * 80)
    
    # Method 1: pyodbc
    try:
        import pyodbc
        logger.info("Testing pyodbc connection...")
        
        # Try different connection strings
        connection_strings = [
            f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={database_path};",
            f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={database_path};UID=admin;PWD=;",
        ]
        
        for conn_str in connection_strings:
            try:
                conn = pyodbc.connect(conn_str)
                logger.info("✓ pyodbc connection successful")
                
                # Test table access
                cursor = conn.cursor()
                tables = cursor.tables(tableType='TABLE').fetchall()
                logger.info(f"✓ Found {len(tables)} tables via pyodbc")
                
                for table_info in tables[:5]:  # Show first 5
                    logger.debug(f"  Table: {table_info[2]}")
                
                conn.close()
                return True
                
            except Exception as pyodbc_error:
                logger.warning(f"pyodbc connection failed: {pyodbc_error}")
                continue
                
    except ImportError:
        logger.warning("pyodbc not available")
    
    # Method 2: zipfile (for Access 2007+)
    try:
        import zipfile
        logger.info("Testing zipfile method...")
        
        try:
            with zipfile.ZipFile(database_path, 'r') as zip_file:
                file_list = zip_file.namelist()[:10]  # First 10 files
                logger.info(f"✓ Database can be opened as ZIP (found {len(file_list)} files)")
                for file_name in file_list:
                    logger.debug(f"  File: {file_name}")
                return True
        except Exception as zip_error:
            logger.warning(f"zipfile method failed: {zip_error}")
            
    except ImportError:
        logger.warning("zipfile not available")
    
    return False

def main():
    """Main diagnostic workflow"""
    
    # Import locale for encoding detection
    import locale
    
    logger.info("DEBUG PHOTO EXTRACTION SCRIPT")
    logger.info("=" * 80)
    
    # Step 1: Diagnose system environment
    diagnose_system_environment()
    
    # Step 2: Test pywin32
    pywin32_ok = test_pywin32_installation()
    
    # Step 3: Find database
    database_path = Path("BASEDATEJP/ユニバーサル企画㈱データベースv25.3.24_be.accdb")
    if not database_path.exists():
        # Try to find it
        base_path = Path("BASEDATEJP")
        if base_path.exists():
            accdb_files = list(base_path.glob("**/*.accdb"))
            if accdb_files:
                database_path = accdb_files[0]
                logger.info(f"Found database: {database_path}")
            else:
                logger.error("No .accdb files found in BASEDATEJP")
                return 1
        else:
            logger.error("BASEDATEJP folder not found")
            return 1
    
    # Step 4: Test database access
    db_access_ok = test_database_access(database_path)
    
    # Step 5: Test alternative methods
    alt_methods_ok = test_alternative_extraction_methods(database_path)
    
    # Summary
    logger.info("=" * 80)
    logger.info("DIAGNOSIS SUMMARY")
    logger.info("=" * 80)
    logger.info(f"pywin32 installation: {'✓ OK' if pywin32_ok else '✗ FAILED'}")
    logger.info(f"Database access: {'✓ OK' if db_access_ok else '✗ FAILED'}")
    logger.info(f"Alternative methods: {'✓ OK' if alt_methods_ok else '✗ FAILED'}")
    
    if not pywin32_ok:
        logger.info("\nRECOMMENDATION: Install pywin32")
        logger.info("Command: pip install pywin32")
    
    if not db_access_ok and alt_methods_ok:
        logger.info("\nRECOMMENDATION: Use alternative extraction method")
        logger.info("The database can be accessed but pywin32 TableDefs fails")
    
    if not db_access_ok and not alt_methods_ok:
        logger.info("\nRECOMMENDATION: Check database file and Access installation")
        logger.info("1. Ensure Microsoft Access is installed")
        logger.info("2. Install Microsoft Access Database Engine")
        logger.info("3. Check if database file is corrupted")
    
    return 0

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)