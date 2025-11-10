"""
Simple Photo Importer from JSON (Linux-compatible)
=====================================================

This script imports photos from access_photo_mappings.json to PostgreSQL.
Unlike unified_photo_import.py, this does NOT require pywin32 or win32com,
making it compatible with Linux containers.

Usage:
    python import_photos_from_json_simple.py
    python import_photos_from_json_simple.py --file config/access_photo_mappings.json
    python import_photos_from_json_simple.py --batch-size 50

Requirements:
    - PostgreSQL running
    - SQLAlchemy, psycopg2
    - JSON file with photo mappings

Author: Claude Code
Date: 2025-11-10
Version: 1.0
"""

import sys
import os
import json
import logging
from pathlib import Path
from typing import Dict
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# PostgreSQL Configuration from environment
POSTGRES_USER = os.getenv('POSTGRES_USER', 'uns_admin')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'uns_claudejp')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')

# Detect if running in Docker
if os.path.exists('/.dockerenv'):
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'db')
else:
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')

POSTGRES_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"


def load_photo_mappings(json_file: Path) -> Dict[str, str]:
    """
    Load photo mappings from JSON file.

    Args:
        json_file: Path to access_photo_mappings.json

    Returns:
        Dict mapping rirekisho_id to photo_data_url

    Raises:
        FileNotFoundError: If JSON file doesn't exist
        json.JSONDecodeError: If JSON is invalid
    """
    if not json_file.exists():
        raise FileNotFoundError(f"Photo mappings file not found: {json_file}")

    logger.info(f"Loading photo mappings from: {json_file}")
    file_size_mb = json_file.stat().st_size / (1024 * 1024)
    logger.info(f"File size: {file_size_mb:.2f} MB")

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Handle both formats:
    # 1. Direct mapping: {"R-001": "data:image/jpeg;base64,..."}
    # 2. Nested format: {"mappings": {"R-001": "data:image/jpeg;base64,..."}}
    if 'mappings' in data:
        mappings = data['mappings']
    else:
        mappings = data

    logger.info(f"Loaded {len(mappings)} photo mappings")

    # Log sample entries for verification
    if mappings:
        sample_keys = list(mappings.keys())[:3]
        for key in sample_keys:
            value_preview = mappings[key][:80] + "..." if len(mappings[key]) > 80 else mappings[key]
            logger.info(f"  Sample: {key} -> {value_preview}")

    return mappings


def import_photos_to_database(mappings: Dict[str, str], batch_size: int = 100) -> Dict[str, int]:
    """
    Import photos to PostgreSQL candidates table.

    Args:
        mappings: Dict mapping rirekisho_id to photo_data_url
        batch_size: Number of updates per batch

    Returns:
        Dict with statistics: updated, skipped, errors

    Raises:
        SQLAlchemyError: If database connection or query fails
    """
    logger.info(f"Connecting to PostgreSQL: {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")

    engine = create_engine(POSTGRES_URL)

    stats = {
        'updated': 0,
        'skipped': 0,  # Already have photo
        'not_found': 0,  # rirekisho_id not found
        'errors': 0
    }

    processed = 0
    total = len(mappings)

    try:
        with engine.connect() as conn:
            for rirekisho_id, photo_data_url in mappings.items():
                processed += 1

                try:
                    # Check if candidate exists and doesn't already have a photo
                    check_query = text("""
                        SELECT id, photo_data_url
                        FROM candidates
                        WHERE rirekisho_id = :rirekisho_id AND deleted_at IS NULL
                    """)
                    result = conn.execute(check_query, {"rirekisho_id": rirekisho_id})
                    row = result.fetchone()

                    if not row:
                        stats['not_found'] += 1
                        logger.debug(f"Candidate not found: {rirekisho_id}")
                        continue

                    candidate_id, existing_photo = row

                    # Skip if already has photo
                    if existing_photo and existing_photo.strip():
                        stats['skipped'] += 1
                        logger.debug(f"Candidate {rirekisho_id} already has photo, skipping")
                        continue

                    # Update with photo
                    update_query = text("""
                        UPDATE candidates
                        SET photo_data_url = :photo,
                            updated_at = NOW()
                        WHERE rirekisho_id = :rirekisho_id AND deleted_at IS NULL
                    """)
                    result = conn.execute(
                        update_query,
                        {"photo": photo_data_url, "rirekisho_id": rirekisho_id}
                    )

                    if result.rowcount > 0:
                        stats['updated'] += 1
                        logger.debug(f"✓ Updated candidate {rirekisho_id} (ID: {candidate_id})")
                    else:
                        stats['errors'] += 1
                        logger.warning(f"Failed to update candidate {rirekisho_id}")

                except SQLAlchemyError as e:
                    stats['errors'] += 1
                    logger.error(f"Error updating candidate {rirekisho_id}: {e}")

                # Commit in batches
                if processed % batch_size == 0:
                    conn.commit()
                    logger.info(f"Progress: {processed}/{total} processed, {stats['updated']} updated")

            # Final commit
            conn.commit()
            logger.info(f"✓ Final commit completed")

    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        raise

    return stats


def verify_import() -> Dict[str, int]:
    """
    Verify photo import by counting candidates with photos.

    Returns:
        Dict with total_candidates, with_photos, without_photos
    """
    logger.info("Verifying photo import...")

    engine = create_engine(POSTGRES_URL)

    try:
        with engine.connect() as conn:
            query = text("""
                SELECT
                    COUNT(*) AS total_candidates,
                    COUNT(photo_data_url) AS with_photos,
                    COUNT(*) - COUNT(photo_data_url) AS without_photos
                FROM candidates
                WHERE deleted_at IS NULL
            """)
            result = conn.execute(query)
            row = result.fetchone()

            verification = {
                'total_candidates': row[0],
                'with_photos': row[1],
                'without_photos': row[2]
            }

            logger.info(f"Verification results:")
            logger.info(f"  Total candidates: {verification['total_candidates']}")
            logger.info(f"  With photos: {verification['with_photos']}")
            logger.info(f"  Without photos: {verification['without_photos']}")

            if verification['with_photos'] > 0:
                percentage = (verification['with_photos'] / verification['total_candidates']) * 100
                logger.info(f"  Photo coverage: {percentage:.1f}%")

            return verification

    except SQLAlchemyError as e:
        logger.error(f"Verification error: {e}")
        return {}


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Import photos from JSON to PostgreSQL (Linux-compatible)'
    )
    parser.add_argument(
        '--file',
        default='config/access_photo_mappings.json',
        help='Path to photo mappings JSON file (default: config/access_photo_mappings.json)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Number of updates per batch (default: 100)'
    )
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='Only verify existing photos, do not import'
    )

    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("Simple Photo Importer (Linux-compatible)")
    logger.info("=" * 80)
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")

    try:
        # Verify only mode
        if args.verify_only:
            verify_import()
            return 0

        # Load photo mappings
        json_file = Path(args.file)
        mappings = load_photo_mappings(json_file)

        if not mappings:
            logger.warning("No photo mappings found in JSON file")
            return 1

        # Import photos
        logger.info("")
        logger.info("Starting photo import...")
        stats = import_photos_to_database(mappings, args.batch_size)

        # Print results
        logger.info("")
        logger.info("=" * 80)
        logger.info("IMPORT RESULTS")
        logger.info("=" * 80)
        logger.info(f"  ✓ Updated: {stats['updated']}")
        logger.info(f"  ⊘ Skipped (already have photo): {stats['skipped']}")
        logger.info(f"  ✗ Not found in database: {stats['not_found']}")
        logger.info(f"  ⚠ Errors: {stats['errors']}")
        logger.info("")

        # Verify import
        verify_import()

        # Final message
        logger.info("")
        logger.info("=" * 80)
        if stats['updated'] > 0:
            logger.info("✓ Photo import completed successfully!")
        else:
            logger.warning("⚠ No photos were imported (candidates may already have photos)")
        logger.info("=" * 80)

        return 0

    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
        logger.error("")
        logger.error("Make sure access_photo_mappings.json exists in config/ directory")
        logger.error("Run BUSCAR_FOTOS_AUTO.bat first to extract photos from Access database")
        return 1

    except json.JSONDecodeError as e:
        logger.error(f"JSON error: {e}")
        logger.error("The photo mappings file is not valid JSON")
        return 1

    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        logger.error("Make sure PostgreSQL is running and accessible")
        return 1

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
