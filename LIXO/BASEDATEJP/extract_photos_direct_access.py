#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extraer fotos directamente de base de datos Access
Script alternativo más robusto para extraer fotos de la base de datos Access
"""

import sys
import os
import json
import base64
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Configurar logging para evitar errores de codificación
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'extract_photos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def find_database() -> Optional[Path]:
    """Buscar la base de datos Access"""
    search_paths = [
        Path.cwd() / "BASEDATEJP",
        Path.cwd().parent / "BASEDATEJP",
        Path("D:/BASEDATEJP"),
    ]
    
    for path in search_paths:
        if path.exists():
            # Buscar archivos .accdb
            accdb_files = list(path.glob("**/*.accdb"))
            if accdb_files:
                # Devolver el más grande
                accdb_files.sort(key=lambda p: p.stat().st_size, reverse=True)
                logger.info(f"Base de datos encontrada: {accdb_files[0]}")
                return accdb_files[0]
    
    return None

def extract_photos_with_pyodbc(db_path: Path) -> Dict[str, Any]:
    """Extraer fotos usando pyodbc (método alternativo)"""
    try:
        import pyodbc
    except ImportError:
        logger.error("pyodbc no está instalado. Instalando...")
        os.system("pip install pyodbc")
        import pyodbc
    
    # Connection string para Access
    conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};"
    
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Listar tablas
        tables = []
        for row in cursor.tables():
            if "履歴書" in row.table_name or "Rirekisho" in row.table_name:
                tables.append(row.table_name)
        
        if not tables:
            logger.warning("No se encontraron tablas de履歴書")
            # Intentar con nombres comunes
            tables = ["T_履歴書", "履歴書", "T_Rirekisho"]
        
        table_name = tables[0] if tables else "T_履歴書"
        logger.info(f"Usando tabla: {table_name}")
        
        # Obtener columnas
        columns = []
        cursor.execute(f"SELECT TOP 1 * FROM [{table_name}]")
        for column in cursor.description:
            if "写真" in column[0] or "Photo" in column[0] or "photo" in column[0]:
                columns.append(column[0])
        
        if not columns:
            logger.warning("No se encontraron columnas de foto")
            columns = ["写真", "Photo", "photo"]
        
        photo_column = columns[0] if columns else "写真"
        logger.info(f"Usando columna: {photo_column}")
        
        # Extraer datos
        cursor.execute(f"SELECT * FROM [{table_name}]")
        rows = cursor.fetchall()
        
        mappings = {}
        total_records = len(rows)
        with_photos = 0
        
        logger.info(f"Procesando {total_records} registros...")
        
        for i, row in enumerate(rows):
            try:
                # Obtener ID (primer campo)
                record_id = str(row[0]) if row[0] else f"record_{i+1}"
                
                # Buscar columna de foto
                photo_data = None
                for col_name in columns:
                    try:
                        col_index = [desc[0] for desc in cursor.description].index(col_name)
                        if row[col_index]:
                            photo_data = row[col_index]
                            break
                    except (ValueError, IndexError):
                        continue
                
                if photo_data:
                    # Convertir a base64
                    if isinstance(photo_data, bytes):
                        base64_data = base64.b64encode(photo_data).decode('utf-8')
                        photo_url = f"data:image/jpeg;base64,{base64_data}"
                        mappings[record_id] = photo_url
                        with_photos += 1
                    elif isinstance(photo_data, str) and photo_data.startswith('/9j/'):
                        # Ya es base64 de JPEG
                        photo_url = f"data:image/jpeg;base64,{photo_data}"
                        mappings[record_id] = photo_url
                        with_photos += 1
                
                if (i + 1) % 100 == 0:
                    logger.info(f"  Procesados {i+1}/{total_records}, fotos extraídas: {with_photos}")
                    
            except Exception as e:
                logger.debug(f"Error procesando registro {i}: {e}")
                continue
        
        conn.close()
        
        logger.info(f"Extracción completada:")
        logger.info(f"  Total registros: {total_records}")
        logger.info(f"  Fotos extraídas: {with_photos}")
        
        return {
            "success": True,
            "total_records": total_records,
            "with_photos": with_photos,
            "mappings": mappings
        }
        
    except Exception as e:
        logger.error(f"Error con pyodbc: {e}")
        return {"error": f"pyodbc_error: {e}"}

def extract_photos_with_win32com(db_path: Path) -> Dict[str, Any]:
    """Extraer fotos usando win32com (método original mejorado)"""
    try:
        import win32com.client as win32
    except ImportError:
        logger.error("pywin32 no está instalado")
        return {"error": "pywin32_not_installed"}
    
    try:
        # Conectar a la base de datos
        conn_str = f"Provider=Microsoft.ACE.OLEDB.12.0;Data Source={db_path};"
        conn = win32.Dispatch("ADODB.Connection")
        conn.Open(conn_str)
        
        # Listar tablas
        rs = win32.Dispatch("ADODB.Recordset")
        rs.Open("SELECT Name FROM MSysObjects WHERE Type=1 AND Flags=0", conn)
        
        tables = []
        while not rs.EOF:
            table_name = rs.Fields("Name").Value
            if "履歴書" in table_name or "Rirekisho" in table_name:
                tables.append(table_name)
            rs.MoveNext()
        rs.Close()
        
        if not tables:
            tables = ["T_履歴書", "履歴書", "T_Rirekisho"]
        
        table_name = tables[0]
        logger.info(f"Usando tabla: {table_name}")
        
        # Extraer datos
        rs.Open(f"SELECT * FROM [{table_name}]", conn)
        
        mappings = {}
        total_records = 0
        with_photos = 0
        
        # Obtener nombres de columnas
        columns = []
        for i in range(rs.Fields.Count):
            col_name = rs.Fields(i).Name
            if "写真" in col_name or "Photo" in col_name or "photo" in col_name:
                columns.append(col_name)
        
        if not columns:
            columns = ["写真", "Photo", "photo"]
        
        photo_column = columns[0]
        logger.info(f"Usando columna: {photo_column}")
        
        while not rs.EOF:
            total_records += 1
            try:
                # Obtener ID
                record_id = str(rs.Fields(0).Value) if rs.Fields(0).Value else f"record_{total_records}"
                
                # Obtener foto
                photo_field = rs.Fields(photo_column)
                if photo_field and photo_field.Value:
                    photo_data = photo_field.Value
                    
                    if isinstance(photo_data, bytes):
                        base64_data = base64.b64encode(photo_data).decode('utf-8')
                        photo_url = f"data:image/jpeg;base64,{base64_data}"
                        mappings[record_id] = photo_url
                        with_photos += 1
                
                if total_records % 100 == 0:
                    logger.info(f"  Procesados {total_records}, fotos extraídas: {with_photos}")
                    
            except Exception as e:
                logger.debug(f"Error procesando registro {total_records}: {e}")
            
            rs.MoveNext()
        
        rs.Close()
        conn.Close()
        
        logger.info(f"Extracción completada:")
        logger.info(f"  Total registros: {total_records}")
        logger.info(f"  Fotos extraídas: {with_photos}")
        
        return {
            "success": True,
            "total_records": total_records,
            "with_photos": with_photos,
            "mappings": mappings
        }
        
    except Exception as e:
        logger.error(f"Error con win32com: {e}")
        return {"error": f"win32com_error: {e}"}

def main():
    """Función principal"""
    logger.info("=" * 80)
    logger.info("EXTRAER FOTOS DE BASE DE DATOS ACCESS")
    logger.info("=" * 80)
    
    # Buscar base de datos
    db_path = find_database()
    if not db_path:
        logger.error("No se encontró la base de datos Access")
        return 1
    
    logger.info(f"Base de datos: {db_path}")
    logger.info(f"Tamaño: {db_path.stat().st_size / (1024*1024):.1f} MB")
    
    # Intentar extraer con diferentes métodos
    result = None
    
    # Método 1: pyodbc
    logger.info("\nIntentando extracción con pyodbc...")
    result = extract_photos_with_pyodbc(db_path)
    
    if "error" in result:
        logger.info("pyodbc falló, intentando con win32com...")
        # Método 2: win32com
        result = extract_photos_with_win32com(db_path)
    
    if "error" in result:
        logger.error(f"Todos los métodos fallaron: {result['error']}")
        return 1
    
    # Guardar resultados
    output_file = Path.cwd() / "access_photo_mappings.json"
    
    try:
        output = {
            "timestamp": datetime.now().isoformat(),
            "source": "direct_access_extraction",
            "database": str(db_path),
            "statistics": {
                "total_records": result["total_records"],
                "with_photos": result["with_photos"],
                "total_mappings": len(result["mappings"])
            },
            "mappings": result["mappings"]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\nResultados guardados en: {output_file}")
        logger.info(f"Total de mappings: {len(result['mappings'])}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error guardando resultados: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)