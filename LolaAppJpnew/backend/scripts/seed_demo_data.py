"""
Seed demo data for LolaAppJp

Creates:
- Sample companies, plants, and lines
- Sample apartments
- Sample candidates
- Sample employees

Usage:
    python scripts/seed_demo_data.py
"""
import sys
import os
from datetime import date, datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.models import (
    Company, Plant, Line, Apartment, Candidate, Employee,
    CandidateStatus, EmployeeStatus, ContractType
)


def seed_companies(db: Session):
    """Create sample companies with plants and lines"""
    print("📊 Creating companies...")

    # Company 1: 高雄工業株式会社
    company1 = Company(
        name="高雄工業株式会社",
        name_kana="タカオコウギョウ",
        address="愛知県名古屋市港区1-2-3",
        phone="052-123-4567",
        default_closing_date=15,
        default_payment_date=0,  # End of month
    )
    db.add(company1)
    db.flush()

    plant1 = Plant(
        company_id=company1.id,
        name="本社工場",
        address="愛知県名古屋市港区1-2-3",
        default_work_hours="昼勤：7時00分～15時30分　夜勤：19時00分～3時30分",
        default_break_time="昼勤：11時00分～11時45分 まで（45分）",
        default_overtime_limit="3時間/日、42時間/月、320時間/年迄とする。",
        time_unit=15.0,
    )
    db.add(plant1)
    db.flush()

    line1 = Line(
        plant_id=plant1.id,
        line_number="Factory-39",
        name="リフト作業",
        hourly_rate=1750.0,
    )
    db.add(line1)

    # Company 2: トヨタ自動車株式会社
    company2 = Company(
        name="トヨタ自動車株式会社",
        name_kana="トヨタジドウシャ",
        address="愛知県豊田市トヨタ町1",
        phone="0565-28-2121",
        default_closing_date=20,
        default_payment_date=0,
    )
    db.add(company2)
    db.flush()

    plant2 = Plant(
        company_id=company2.id,
        name="元町工場",
        address="愛知県豊田市元町1",
        default_work_hours="8:00-17:00",
        default_break_time="12:00-13:00 (60分)",
        default_overtime_limit="2時間/日、40時間/月",
        time_unit=15.0,
    )
    db.add(plant2)
    db.flush()

    line2 = Line(
        plant_id=plant2.id,
        line_number="LINE-001",
        name="組立ライン",
        hourly_rate=1800.0,
    )
    db.add(line2)

    db.commit()
    print(f"   ✅ Created 2 companies, 2 plants, 2 lines")


def seed_apartments(db: Session):
    """Create sample apartments"""
    print("🏠 Creating apartments...")

    apartments = [
        Apartment(
            name="ドミトリー名古屋1",
            address="愛知県名古屋市港区宝神町1-2-3",
            total_capacity=20,
            current_occupancy=12,
            monthly_rent=30000.0,
            utilities_included=True,
            amenities=["WiFi", "駐車場", "洗濯機", "共同キッチン"],
            room_type="Dormitory",
            is_available=True,
        ),
        Apartment(
            name="ドミトリー名古屋2",
            address="愛知県名古屋市港区築地町2-3-4",
            total_capacity=15,
            current_occupancy=8,
            monthly_rent=28000.0,
            utilities_included=True,
            amenities=["WiFi", "洗濯機"],
            room_type="Dormitory",
            is_available=True,
        ),
        Apartment(
            name="シェアハウス豊田",
            address="愛知県豊田市山之手1-2-3",
            total_capacity=10,
            current_occupancy=5,
            monthly_rent=35000.0,
            utilities_included=False,
            amenities=["WiFi", "駐車場", "洗濯機", "個室"],
            room_type="Shared",
            is_available=True,
        ),
    ]

    for apt in apartments:
        db.add(apt)

    db.commit()
    print(f"   ✅ Created {len(apartments)} apartments")


def seed_candidates(db: Session):
    """Create sample candidates"""
    print("👤 Creating candidates...")

    candidates = [
        Candidate(
            rirekisho_id="RH-2025-001",
            full_name_kanji="グエン・ヴァン・アン",
            full_name_kana="グエン・ヴァン・アン",
            full_name_roman="Nguyen Van An",
            date_of_birth=date(1995, 3, 15),
            age=29,
            gender="男性",
            nationality="ベトナム",
            current_address="愛知県名古屋市港区1-2-3",
            phone="090-1234-5678",
            email="nguyen.an@example.com",
            residence_status="技能実習",
            zairyu_expiry_date=date(2026, 12, 31),
            japanese_level="N3",
            status=CandidateStatus.PENDING,
        ),
        Candidate(
            rirekisho_id="RH-2025-002",
            full_name_kanji="レ・ティ・フエ",
            full_name_kana="レ・ティ・フエ",
            full_name_roman="Le Thi Hue",
            date_of_birth=date(1998, 7, 20),
            age=26,
            gender="女性",
            nationality="ベトナム",
            current_address="愛知県名古屋市中区2-3-4",
            phone="080-2345-6789",
            email="le.hue@example.com",
            residence_status="技能実習",
            zairyu_expiry_date=date(2026, 6, 30),
            japanese_level="N4",
            status=CandidateStatus.APPROVED,
        ),
        Candidate(
            rirekisho_id="RH-2025-003",
            full_name_kanji="山田太郎",
            full_name_kana="ヤマダタロウ",
            full_name_roman="Yamada Taro",
            date_of_birth=date(1990, 1, 10),
            age=35,
            gender="男性",
            nationality="日本",
            current_address="愛知県豊田市1-1-1",
            phone="070-3456-7890",
            email="yamada.taro@example.com",
            japanese_level="Native",
            status=CandidateStatus.HIRED,
        ),
    ]

    for candidate in candidates:
        db.add(candidate)

    db.commit()
    print(f"   ✅ Created {len(candidates)} candidates")


def seed_employees(db: Session):
    """Create sample employees from hired candidates"""
    print("👷 Creating employees...")

    # Get hired candidate and first line
    candidate = db.query(Candidate).filter(Candidate.status == CandidateStatus.HIRED).first()
    line = db.query(Line).first()

    if not candidate or not line:
        print("   ⚠️  Skipped (no hired candidates or lines)")
        return

    employee = Employee(
        rirekisho_id=candidate.rirekisho_id,
        full_name_kanji=candidate.full_name_kanji,
        full_name_kana=candidate.full_name_kana,
        full_name_roman=candidate.full_name_roman,
        date_of_birth=candidate.date_of_birth,
        gender=candidate.gender,
        nationality=candidate.nationality,
        current_address=candidate.current_address,
        phone=candidate.phone,
        email=candidate.email,
        hire_date=date.today() - timedelta(days=30),
        contract_type=ContractType.HAKEN,
        status=EmployeeStatus.ACTIVE,
        line_id=line.id,
        jikyu=1750,
        position="作業員",
    )

    db.add(employee)
    db.commit()
    print(f"   ✅ Created 1 employee")


def main():
    """Run all seed functions"""
    print("=" * 60)
    print("  LolaAppJp - Seed Demo Data")
    print("=" * 60)
    print()

    # Create tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_companies(db)
        seed_apartments(db)
        seed_candidates(db)
        seed_employees(db)

        print()
        print("✅ All demo data seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error seeding data: {e}")
        raise
    finally:
        db.close()

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
