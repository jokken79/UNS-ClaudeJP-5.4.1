"""
SQLAlchemy database models for LolaAppJp

Database Schema:
    - users: System users with role-based access
    - candidates: Job candidates (履歴書/Rirekisho)
    - employees: Active employees (派遣社員)
    - companies: Client companies
    - plants: Client factory/plant locations
    - lines: Production lines within plants
    - apartments: Employee housing
    - apartment_assignments: Employee-apartment mappings
    - yukyu_balances: Paid vacation balances
    - yukyu_transactions: Paid vacation transactions (LIFO)
    - timer_cards: Daily attendance records
    - requests: Workflow requests (入社連絡票, 有休申請, etc.)
    - payroll_records: Monthly payroll calculations
"""
import enum
from datetime import datetime, date
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime, Float, Text,
    ForeignKey, Enum, JSON, Index, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


# ============================================================================
# ENUMS
# ============================================================================

class UserRole(str, enum.Enum):
    """
    User role hierarchy (descending privileges):
    ADMIN > TORISHIMARIYAKU > KEIRI > TANTOSHA > HAKEN_SHAIN > UKEOI
    """
    ADMIN = "ADMIN"                          # Super admin (全権限)
    TORISHIMARIYAKU = "TORISHIMARIYAKU"      # Director/Boss (取締役)
    KEIRI = "KEIRI"                          # Accounting/Administration (経理)
    TANTOSHA = "TANTOSHA"                    # Supervisor/Manager (担当者)
    HAKEN_SHAIN = "HAKEN_SHAIN"              # Dispatch employee (派遣社員)
    UKEOI = "UKEOI"                          # Contract worker (請負)


class CandidateStatus(str, enum.Enum):
    """Candidate application status"""
    PENDING = "PENDING"          # 審査中
    APPROVED = "APPROVED"        # 承認済み
    REJECTED = "REJECTED"        # 却下
    HIRED = "HIRED"              # 採用済み (入社連絡票 approved)


class EmployeeStatus(str, enum.Enum):
    """Employee status"""
    ACTIVE = "ACTIVE"            # 在籍中
    ON_LEAVE = "ON_LEAVE"        # 休職中
    RESIGNED = "RESIGNED"        # 退職済み
    TERMINATED = "TERMINATED"    # 解雇


class ContractType(str, enum.Enum):
    """Employment contract type"""
    HAKEN = "HAKEN"              # 派遣 (Dispatch)
    UKEOI = "UKEOI"              # 請負 (Contract)
    SEISHAIN = "SEISHAIN"        # 正社員 (Full-time)


class RequestType(str, enum.Enum):
    """Request workflow types"""
    NYUSHA = "NYUSHA"            # 入社連絡票 (New hire notification)
    YUKYU = "YUKYU"              # 有給休暇申請 (Paid leave request)
    TAISHA = "TAISHA"            # 退社申請 (Resignation request)
    TRANSFER = "TRANSFER"        # 配置転換 (Transfer request)


class RequestStatus(str, enum.Enum):
    """Request approval status"""
    DRAFT = "DRAFT"              # 下書き
    PENDING = "PENDING"          # 承認待ち
    APPROVED = "APPROVED"        # 承認済み
    REJECTED = "REJECTED"        # 却下


class YukyuTransactionType(str, enum.Enum):
    """Yukyu transaction types"""
    GRANT = "GRANT"              # 付与
    USE = "USE"                  # 使用
    EXPIRE = "EXPIRE"            # 失効
    ADJUSTMENT = "ADJUSTMENT"    # 調整


# ============================================================================
# MODELS
# ============================================================================

class User(Base):
    """
    System users with role-based access control

    Hierarchy: ADMIN > TORISHIMARIYAKU > KEIRI > TANTOSHA > HAKEN_SHAIN > UKEOI
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(Enum(UserRole), nullable=False, default=UserRole.HAKEN_SHAIN)

    # Employee linkage (optional - for HAKEN_SHAIN and UKEOI roles)
    employee_id = Column(Integer, ForeignKey("employees.hakenmoto_id"), nullable=True)

    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

    # Relationships
    employee = relationship("Employee", back_populates="user", foreign_keys=[employee_id])

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role.value})>"


class Candidate(Base):
    """
    Job candidates with rirekisho (履歴書) data

    Key: rirekisho_id (unique candidate ID)
    Note: Candidates NEVER get deleted. They stay in this table forever.
    """
    __tablename__ = "candidates"

    # Primary key
    rirekisho_id = Column(String(50), primary_key=True, index=True)  # e.g., "RH-2025-001"

    # Basic info (基本情報)
    full_name_kanji = Column(String(255), nullable=False, index=True)
    full_name_kana = Column(String(255))
    full_name_roman = Column(String(255))
    date_of_birth = Column(Date)
    age = Column(Integer)
    gender = Column(String(10))  # 男性/女性
    nationality = Column(String(100))

    # Contact (連絡先)
    current_address = Column(Text)
    phone = Column(String(20))
    email = Column(String(255), index=True)

    # Zairyu card (在留カード)
    zairyu_card_number = Column(String(50))
    residence_status = Column(String(100))  # 在留資格
    period_of_stay = Column(String(50))     # 在留期間
    zairyu_expiry_date = Column(Date)

    # My Number
    my_number = Column(String(20))

    # Emergency contact (緊急連絡先)
    emergency_contact_name = Column(String(255))
    emergency_contact_phone = Column(String(20))
    emergency_contact_relationship = Column(String(100))

    # Education (学歴)
    education_data = Column(JSON)  # Array of education entries

    # Work history (職歴)
    work_history_data = Column(JSON)  # Array of work history entries

    # Skills & qualifications (資格・スキル)
    qualifications = Column(JSON)  # Array of qualifications
    japanese_level = Column(String(20))  # JLPT N1-N5
    skills = Column(Text)

    # Photo
    photo_data_url = Column(Text)  # Base64 encoded photo

    # Bank info
    bank_name = Column(String(255))
    bank_branch = Column(String(255))
    bank_account_type = Column(String(20))  # 普通/当座
    bank_account_number = Column(String(50))
    bank_account_holder = Column(String(255))

    # Status
    status = Column(Enum(CandidateStatus), default=CandidateStatus.PENDING, nullable=False, index=True)

    # OCR metadata
    ocr_processed = Column(Boolean, default=False)
    ocr_data = Column(JSON)  # Raw OCR results

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)  # Soft delete

    # Relationships
    employees = relationship("Employee", back_populates="candidate")
    requests = relationship("Request", back_populates="candidate")

    __table_args__ = (
        Index("idx_candidate_status", "status"),
        Index("idx_candidate_created", "created_at"),
    )

    def __repr__(self):
        return f"<Candidate(rirekisho_id={self.rirekisho_id}, name={self.full_name_kanji}, status={self.status.value})>"


class Company(Base):
    """
    Client companies (normalized from factories JSON)

    Example: 高雄工業株式会社
    """
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    name_kana = Column(String(255))

    # Contact info
    address = Column(Text)
    phone = Column(String(20))
    email = Column(String(255))
    website = Column(String(500))

    # Payment terms
    default_closing_date = Column(Integer)  # 締め日 (1-31)
    default_payment_date = Column(Integer)  # 支払日 (1-31 or 0 for end of month)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)

    # Relationships
    plants = relationship("Plant", back_populates="company", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Company(id={self.id}, name={self.name})>"


class Plant(Base):
    """
    Client factory/plant locations

    Example: 本社工場, 第二工場
    """
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String(255), nullable=False)  # e.g., "本社工場"

    # Location
    address = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)

    # Work schedule (default for all lines)
    default_work_hours = Column(String(500))  # e.g., "昼勤：7時00分～15時30分"
    default_break_time = Column(String(500))
    default_overtime_limit = Column(String(500))  # e.g., "3時間/日、42時間/月"
    time_unit = Column(Float, default=15.0)  # Time rounding unit (minutes)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)

    # Relationships
    company = relationship("Company", back_populates="plants")
    lines = relationship("Line", back_populates="plant", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("company_id", "name", name="uq_plant_company_name"),
        Index("idx_plant_company", "company_id"),
    )

    def __repr__(self):
        return f"<Plant(id={self.id}, name={self.name}, company_id={self.company_id})>"


class Line(Base):
    """
    Production lines within plants

    Example: リフト作業, 組立ライン
    """
    __tablename__ = "lines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=False)
    line_number = Column(String(50))  # e.g., "Factory-39"
    name = Column(String(255), nullable=False)  # e.g., "リフト作業"

    # Job details
    description = Column(Text)
    hourly_rate = Column(Float, nullable=False)  # Base hourly wage

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)

    # Relationships
    plant = relationship("Plant", back_populates="lines")
    employees = relationship("Employee", back_populates="line")

    __table_args__ = (
        Index("idx_line_plant", "plant_id"),
    )

    def __repr__(self):
        return f"<Line(id={self.id}, name={self.name}, hourly_rate={self.hourly_rate})>"


class Employee(Base):
    """
    Active employees (派遣社員)

    Created from approved 入社連絡票 (Nyusha Request)
    Links to original Candidate via rirekisho_id
    """
    __tablename__ = "employees"

    # Primary key (auto-increment)
    hakenmoto_id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # Link to candidate (one candidate can have multiple employee records over time)
    rirekisho_id = Column(String(50), ForeignKey("candidates.rirekisho_id"), nullable=False, index=True)

    # Basic info (copied from Candidate at hire time)
    full_name_kanji = Column(String(255), nullable=False, index=True)
    full_name_kana = Column(String(255))
    full_name_roman = Column(String(255))
    date_of_birth = Column(Date)
    gender = Column(String(10))
    nationality = Column(String(100))

    # Contact
    current_address = Column(Text)
    phone = Column(String(20))
    email = Column(String(255))

    # Employment details
    hire_date = Column(Date, nullable=False, index=True)
    contract_type = Column(Enum(ContractType), nullable=False)
    status = Column(Enum(EmployeeStatus), default=EmployeeStatus.ACTIVE, nullable=False, index=True)

    # Factory assignment
    line_id = Column(Integer, ForeignKey("lines.id"), nullable=False)
    jikyu = Column(Integer, nullable=False)  # Hourly wage (時給)
    position = Column(String(255))  # Job position

    # Apartment assignment (optional)
    apartment_id = Column(Integer, ForeignKey("apartments.id"), nullable=True)

    # Bank info (may be updated from candidate data)
    bank_name = Column(String(255))
    bank_branch = Column(String(255))
    bank_account_type = Column(String(20))
    bank_account_number = Column(String(50))
    bank_account_holder = Column(String(255))

    # Resignation
    resignation_date = Column(Date)
    resignation_reason = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)

    # Relationships
    candidate = relationship("Candidate", back_populates="employees")
    line = relationship("Line", back_populates="employees")
    apartment = relationship("Apartment", back_populates="residents", foreign_keys=[apartment_id])
    user = relationship("User", back_populates="employee", uselist=False)
    apartment_assignments = relationship("ApartmentAssignment", back_populates="employee")
    yukyu_balances = relationship("YukyuBalance", back_populates="employee")
    timer_cards = relationship("TimerCard", back_populates="employee")
    payroll_records = relationship("PayrollRecord", back_populates="employee")
    requests = relationship("Request", back_populates="employee", foreign_keys="Request.employee_id")

    __table_args__ = (
        Index("idx_employee_status", "status"),
        Index("idx_employee_hire_date", "hire_date"),
        Index("idx_employee_line", "line_id"),
    )

    def __repr__(self):
        return f"<Employee(hakenmoto_id={self.hakenmoto_id}, name={self.full_name_kanji}, status={self.status.value})>"


class Apartment(Base):
    """
    Employee housing (寮/寮)

    Supports multiple residents with capacity tracking
    """
    __tablename__ = "apartments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True, index=True)

    # Location
    address = Column(Text, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)

    # Capacity
    total_capacity = Column(Integer, nullable=False)  # Max residents
    current_occupancy = Column(Integer, default=0, nullable=False)

    # Pricing
    monthly_rent = Column(Float, nullable=False)
    utilities_included = Column(Boolean, default=False)
    deposit_required = Column(Float, default=0.0)

    # Amenities
    amenities = Column(JSON)  # ["WiFi", "Parking", "Laundry", etc.]
    room_type = Column(String(100))  # "Single", "Shared", "Dormitory"

    # Availability
    is_available = Column(Boolean, default=True, nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)

    # Relationships
    residents = relationship("Employee", back_populates="apartment", foreign_keys="Employee.apartment_id")
    assignments = relationship("ApartmentAssignment", back_populates="apartment")

    __table_args__ = (
        CheckConstraint("current_occupancy >= 0", name="check_occupancy_positive"),
        CheckConstraint("current_occupancy <= total_capacity", name="check_occupancy_capacity"),
        Index("idx_apartment_available", "is_available"),
    )

    def __repr__(self):
        return f"<Apartment(id={self.id}, name={self.name}, occupancy={self.current_occupancy}/{self.total_capacity})>"


class ApartmentAssignment(Base):
    """
    Employee apartment assignment history

    Tracks move-in, move-out, and prorated rent calculations
    """
    __tablename__ = "apartment_assignments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.hakenmoto_id"), nullable=False, index=True)
    apartment_id = Column(Integer, ForeignKey("apartments.id"), nullable=False, index=True)

    # Assignment period
    move_in_date = Column(Date, nullable=False)
    move_out_date = Column(Date)

    # Rent (may differ from apartment.monthly_rent due to prorating or special rates)
    monthly_rent = Column(Float, nullable=False)
    prorated_first_month = Column(Float)
    prorated_last_month = Column(Float)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    employee = relationship("Employee", back_populates="apartment_assignments")
    apartment = relationship("Apartment", back_populates="assignments")

    __table_args__ = (
        Index("idx_assignment_employee", "employee_id"),
        Index("idx_assignment_apartment", "apartment_id"),
        Index("idx_assignment_active", "is_active"),
    )

    def __repr__(self):
        return f"<ApartmentAssignment(id={self.id}, employee_id={self.employee_id}, apartment_id={self.apartment_id})>"


class YukyuBalance(Base):
    """
    Paid vacation balance (有給休暇残高)

    Tracks yearly grants with LIFO deduction
    """
    __tablename__ = "yukyu_balances"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.hakenmoto_id"), nullable=False, index=True)

    # Fiscal year
    fiscal_year = Column(Integer, nullable=False)  # e.g., 2025

    # Balance
    granted_days = Column(Float, nullable=False)  # Initially granted (e.g., 10.0)
    used_days = Column(Float, default=0.0, nullable=False)
    remaining_days = Column(Float, nullable=False)  # granted - used

    # Grant date and expiry
    grant_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False)  # Usually 2 years from grant

    # Status
    is_expired = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    employee = relationship("Employee", back_populates="yukyu_balances")
    transactions = relationship("YukyuTransaction", back_populates="balance")

    __table_args__ = (
        UniqueConstraint("employee_id", "fiscal_year", name="uq_yukyu_employee_year"),
        Index("idx_yukyu_employee", "employee_id"),
        Index("idx_yukyu_expiry", "expiry_date"),
    )

    def __repr__(self):
        return f"<YukyuBalance(id={self.id}, employee_id={self.employee_id}, year={self.fiscal_year}, remaining={self.remaining_days})>"


class YukyuTransaction(Base):
    """
    Paid vacation transactions (LIFO deduction)

    Types: GRANT, USE, EXPIRE, ADJUSTMENT
    """
    __tablename__ = "yukyu_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    balance_id = Column(Integer, ForeignKey("yukyu_balances.id"), nullable=False, index=True)
    employee_id = Column(Integer, ForeignKey("employees.hakenmoto_id"), nullable=False, index=True)

    # Transaction details
    transaction_type = Column(Enum(YukyuTransactionType), nullable=False)
    transaction_date = Column(Date, nullable=False)
    days = Column(Float, nullable=False)  # Positive for GRANT, negative for USE/EXPIRE

    # Reference
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=True)  # Link to yukyu request
    description = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    balance = relationship("YukyuBalance", back_populates="transactions")
    request = relationship("Request", back_populates="yukyu_transactions")

    __table_args__ = (
        Index("idx_transaction_balance", "balance_id"),
        Index("idx_transaction_date", "transaction_date"),
    )

    def __repr__(self):
        return f"<YukyuTransaction(id={self.id}, type={self.transaction_type.value}, days={self.days})>"


class TimerCard(Base):
    """
    Daily attendance records (タイムカード)

    Processed from OCR (PDF upload) with factory rules applied
    """
    __tablename__ = "timer_cards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.hakenmoto_id"), nullable=False, index=True)

    # Work date
    work_date = Column(Date, nullable=False, index=True)

    # Time tracking
    clock_in = Column(DateTime(timezone=True))
    clock_out = Column(DateTime(timezone=True))

    # Break times (minutes)
    break_minutes = Column(Integer, default=0)

    # Calculated hours (after rounding by factory time_unit)
    regular_hours = Column(Float, default=0.0)
    overtime_hours = Column(Float, default=0.0)
    night_hours = Column(Float, default=0.0)
    holiday_hours = Column(Float, default=0.0)

    # OCR metadata
    ocr_processed = Column(Boolean, default=False)
    ocr_confidence = Column(Float)  # 0.0 - 1.0
    ocr_raw_data = Column(JSON)

    # Manual review
    needs_review = Column(Boolean, default=False)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)

    # Relationships
    employee = relationship("Employee", back_populates="timer_cards")
    reviewer = relationship("User")

    __table_args__ = (
        UniqueConstraint("employee_id", "work_date", name="uq_timercard_employee_date"),
        Index("idx_timercard_employee", "employee_id"),
        Index("idx_timercard_date", "work_date"),
        Index("idx_timercard_review", "needs_review"),
    )

    def __repr__(self):
        return f"<TimerCard(id={self.id}, employee_id={self.employee_id}, date={self.work_date})>"


class Request(Base):
    """
    Workflow requests with approval process

    Types:
        - NYUSHA (入社連絡票): New hire notification (Candidate → Employee)
        - YUKYU (有休申請): Paid leave request
        - TAISHA (退社申請): Resignation request
        - TRANSFER (配置転換): Transfer request
    """
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Request type
    request_type = Column(Enum(RequestType), nullable=False, index=True)
    status = Column(Enum(RequestStatus), default=RequestStatus.DRAFT, nullable=False, index=True)

    # Requester
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Subject (depends on request type)
    candidate_id = Column(String(50), ForeignKey("candidates.rirekisho_id"), nullable=True, index=True)  # For NYUSHA
    employee_id = Column(Integer, ForeignKey("employees.hakenmoto_id"), nullable=True, index=True)  # For YUKYU, TAISHA, TRANSFER

    # Request data (type-specific JSON)
    request_data = Column(JSON)  # For NYUSHA: employee_data (factory, jikyu, hire_date, etc.)
                                  # For YUKYU: { start_date, end_date, days }
                                  # For TAISHA: { resignation_date, reason }
                                  # For TRANSFER: { new_factory_id, transfer_date }

    # Approval workflow
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True))
    rejected_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    rejected_at = Column(DateTime(timezone=True))
    rejection_reason = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by])
    rejecter = relationship("User", foreign_keys=[rejected_by])
    candidate = relationship("Candidate", back_populates="requests")
    employee = relationship("Employee", back_populates="requests", foreign_keys=[employee_id])
    yukyu_transactions = relationship("YukyuTransaction", back_populates="request")

    __table_args__ = (
        Index("idx_request_type_status", "request_type", "status"),
        Index("idx_request_created", "created_at"),
    )

    def __repr__(self):
        return f"<Request(id={self.id}, type={self.request_type.value}, status={self.status.value})>"


class PayrollRecord(Base):
    """
    Monthly payroll calculations

    Calculates salary based on timer cards, yukyu, and factory rates
    """
    __tablename__ = "payroll_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.hakenmoto_id"), nullable=False, index=True)

    # Period
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)

    # Work hours (aggregated from timer cards)
    regular_hours = Column(Float, default=0.0)
    overtime_hours = Column(Float, default=0.0)
    night_hours = Column(Float, default=0.0)
    holiday_hours = Column(Float, default=0.0)

    # Yukyu days used this month
    yukyu_days = Column(Float, default=0.0)

    # Pay rates
    base_hourly_rate = Column(Float, nullable=False)
    overtime_multiplier = Column(Float, default=1.25)  # 125%
    night_multiplier = Column(Float, default=1.25)
    holiday_multiplier = Column(Float, default=1.35)

    # Gross pay
    regular_pay = Column(Float, default=0.0)
    overtime_pay = Column(Float, default=0.0)
    night_pay = Column(Float, default=0.0)
    holiday_pay = Column(Float, default=0.0)
    gross_pay = Column(Float, default=0.0)

    # Deductions
    social_insurance = Column(Float, default=0.0)
    health_insurance = Column(Float, default=0.0)
    pension_insurance = Column(Float, default=0.0)
    employment_insurance = Column(Float, default=0.0)
    income_tax = Column(Float, default=0.0)
    apartment_rent = Column(Float, default=0.0)  # Deducted if assigned apartment
    other_deductions = Column(Float, default=0.0)
    total_deductions = Column(Float, default=0.0)

    # Net pay
    net_pay = Column(Float, default=0.0)

    # Status
    is_finalized = Column(Boolean, default=False)
    finalized_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    finalized_at = Column(DateTime(timezone=True))

    # Payment
    payment_date = Column(Date)
    is_paid = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    employee = relationship("Employee", back_populates="payroll_records")
    finalizer = relationship("User", foreign_keys=[finalized_by])

    __table_args__ = (
        UniqueConstraint("employee_id", "year", "month", name="uq_payroll_employee_period"),
        Index("idx_payroll_employee", "employee_id"),
        Index("idx_payroll_period", "year", "month"),
        Index("idx_payroll_finalized", "is_finalized"),
    )

    def __repr__(self):
        return f"<PayrollRecord(id={self.id}, employee_id={self.employee_id}, period={self.year}-{self.month:02d}, net_pay={self.net_pay})>"
