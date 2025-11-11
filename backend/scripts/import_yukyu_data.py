"""
Import Yukyu Data from CSV
===========================

Imports historical yukyu data from yukyu_data.csv into the database.

This script:
1. Reads yukyu_data.csv (exported from Excel)
2. Maps employees by name or rirekisho_id
3. Creates YukyuBalance records for each fiscal year
4. Preserves historical data from Excel

Usage:
    python scripts/import_yukyu_data.py

Author: UNS-ClaudeJP System
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.models import (
    Employee,
    YukyuBalance,
    YukyuStatus,
)


def parse_japanese_date(date_str: str) -> date:
    """
    Parse Japanese date string to Python date.

    Formats supported:
    - YYYY/M/D (e.g., 2020/2/1)
    - YYYY-MM-DD
    """
    if pd.isna(date_str) or date_str == '' or date_str == 'nan':
        return None

    date_str = str(date_str).strip()

    try:
        # Try YYYY/M/D format
        if '/' in date_str:
            parts = date_str.split('/')
            if len(parts) == 3:
                year, month, day = parts
                return date(int(year), int(month), int(day))

        # Try YYYY-MM-DD format
        if '-' in date_str:
            return datetime.strptime(date_str, '%Y-%m-%d').date()

        print(f"⚠️  Could not parse date: {date_str}")
        return None
    except Exception as e:
        print(f"⚠️  Error parsing date '{date_str}': {e}")
        return None


def find_employee_by_name(db: Session, name: str, factory_name: str = None) -> Employee:
    """
    Find employee by name (kanji or kana).

    Args:
        db: Database session
        name: Employee name
        factory_name: Optional factory name for filtering

    Returns:
        Employee or None
    """
    # Try exact match on full_name_kanji
    employee = db.query(Employee).filter(
        Employee.full_name_kanji == name
    ).first()

    if employee:
        return employee

    # Try kana name
    employee = db.query(Employee).filter(
        Employee.full_name_kana == name
    ).first()

    if employee:
        return employee

    # Try partial match (for cases like "NGUYEN ANH TUAN" vs "グエン　アン　トゥアン")
    employee = db.query(Employee).filter(
        Employee.full_name_kanji.contains(name.split()[0]) if name else False
    ).first()

    return employee


def import_yukyu_data(csv_path: str, db: Session):
    """
    Import yukyu data from CSV.

    Args:
        csv_path: Path to yukyu_data.csv
        db: Database session
    """
    print("="*80)
    print("📊 IMPORTING YUKYU DATA FROM CSV")
    print("="*80)

    # Read CSV
    print(f"\n📂 Reading CSV: {csv_path}")
    df = pd.read_csv(csv_path, encoding='cp932')

    print(f"   Total rows: {len(df)}")
    print(f"   Columns: {len(df.columns)}")

    # Clean data
    df_clean = df[df['社員№'].notna()].copy()
    print(f"   Valid rows: {len(df_clean)}")

    # Statistics
    stats = {
        'total_rows': len(df_clean),
        'employees_found': 0,
        'employees_not_found': 0,
        'balances_created': 0,
        'balances_skipped': 0,
        'errors': 0
    }

    print("\n" + "="*80)
    print("🔄 PROCESSING YUKYU RECORDS")
    print("="*80)

    # Process each row
    for idx, row in df_clean.iterrows():
        try:
            # Extract data
            employee_num = row['社員№']
            name = row['氏名']
            factory_name = row['派遣先']
            hire_date_str = row['入社日']
            months_worked = row['経過月']
            assigned_date_str = row['有給発生']

            # Skip header rows
            if name == '氏名' or pd.isna(name):
                stats['balances_skipped'] += 1
                continue

            # Parse dates
            hire_date = parse_japanese_date(hire_date_str)
            assigned_date = parse_japanese_date(assigned_date_str)

            if not assigned_date:
                stats['balances_skipped'] += 1
                continue

            # Find employee
            employee = find_employee_by_name(db, name, factory_name)

            if not employee:
                if stats['employees_not_found'] < 10:  # Only show first 10
                    print(f"   ⚠️  Employee not found: {name} (社員№ {employee_num}) at {factory_name}")
                stats['employees_not_found'] += 1
                stats['balances_skipped'] += 1
                continue

            stats['employees_found'] += 1

            # Extract yukyu data
            days_assigned = row.get('付与数', 0)
            days_carried_over = row.get('繰越', 0)
            days_total = row.get('保有数', 0)
            days_used = row.get('消化日数', 0)
            days_remaining = row.get('期末残高', 0)
            days_expired = row.get('時効数', 0)
            days_available = row.get('時効後残', 0)

            # Convert to int (handle NaN and strings)
            def to_int(val, default=0):
                if pd.isna(val):
                    return default
                try:
                    return int(float(val))
                except:
                    return default

            days_assigned = to_int(days_assigned)
            days_carried_over = to_int(days_carried_over)
            days_total = to_int(days_total)
            days_used = to_int(days_used)
            days_remaining = to_int(days_remaining)
            days_expired = to_int(days_expired)
            days_available = to_int(days_available)
            months_worked = to_int(months_worked)

            # Skip if no days assigned (header row or invalid data)
            if days_assigned == 0 and days_total == 0:
                stats['balances_skipped'] += 1
                continue

            # Calculate expiration date (2 years from assigned_date)
            from dateutil.relativedelta import relativedelta
            expires_on = assigned_date + relativedelta(years=2)

            # Determine status (expired if expires_on < today)
            status = YukyuStatus.EXPIRED if expires_on < date.today() else YukyuStatus.ACTIVE

            # Fiscal year
            fiscal_year = assigned_date.year

            # Check if balance already exists
            existing_balance = db.query(YukyuBalance).filter(
                YukyuBalance.employee_id == employee.id,
                YukyuBalance.assigned_date == assigned_date,
                YukyuBalance.months_worked == months_worked
            ).first()

            if existing_balance:
                stats['balances_skipped'] += 1
                continue

            # Create balance
            balance = YukyuBalance(
                employee_id=employee.id,
                fiscal_year=fiscal_year,
                assigned_date=assigned_date,
                months_worked=months_worked,
                days_assigned=days_assigned,
                days_carried_over=days_carried_over,
                days_total=days_total,
                days_used=days_used,
                days_remaining=days_remaining,
                days_expired=days_expired,
                days_available=days_available,
                expires_on=expires_on,
                status=status,
                notes=f"Imported from Excel - 社員№ {employee_num}"
            )

            db.add(balance)
            stats['balances_created'] += 1

            # Commit every 100 records
            if stats['balances_created'] % 100 == 0:
                db.commit()
                print(f"   ✅ Committed {stats['balances_created']} balances...")

        except Exception as e:
            print(f"   ❌ Error processing row {idx}: {e}")
            stats['errors'] += 1
            continue

    # Final commit
    db.commit()

    print("\n" + "="*80)
    print("✅ IMPORT COMPLETED")
    print("="*80)
    print(f"\n📊 Statistics:")
    print(f"   Total rows processed:     {stats['total_rows']}")
    print(f"   Employees found:          {stats['employees_found']}")
    print(f"   Employees not found:      {stats['employees_not_found']}")
    print(f"   Balances created:         {stats['balances_created']}")
    print(f"   Balances skipped:         {stats['balances_skipped']}")
    print(f"   Errors:                   {stats['errors']}")

    return stats


def main():
    """Main entry point."""
    csv_path = "/home/user/UNS-ClaudeJP-5.4.1/yukyu_data.csv"

    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        sys.exit(1)

    db = SessionLocal()
    try:
        stats = import_yukyu_data(csv_path, db)

        if stats['balances_created'] > 0:
            print(f"\n✅ Successfully imported {stats['balances_created']} yukyu balances!")
        else:
            print("\n⚠️  No balances were created. Check employee names in CSV.")

    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
