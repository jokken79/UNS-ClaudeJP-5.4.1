"""
Payroll Models - SQLAlchemy models for payroll tables
"""
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.types import Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class PayrollRun(Base):
    """Model for payroll runs."""
    __tablename__ = "payroll_runs"

    id = Column(Integer, primary_key=True, index=True)
    pay_period_start = Column(Date, nullable=False, index=True)
    pay_period_end = Column(Date, nullable=False, index=True)
    status = Column(String(20), default="draft", index=True)
    total_employees = Column(Integer, default=0)
    total_gross_amount = Column(Numeric(15, 2), default=0)
    total_deductions = Column(Numeric(15, 2), default=0)
    total_net_amount = Column(Numeric(15, 2), default=0)
    created_by = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    employee_payrolls = relationship("EmployeePayroll", back_populates="payroll_run")


class EmployeePayroll(Base):
    """Model for employee payroll details."""
    __tablename__ = "employee_payroll"

    id = Column(Integer, primary_key=True, index=True)
    payroll_run_id = Column(Integer, ForeignKey("payroll_runs.id"), nullable=False, index=True)
    employee_id = Column(Integer, nullable=False, index=True)
    pay_period_start = Column(Date, nullable=False)
    pay_period_end = Column(Date, nullable=False)

    # Hours breakdown
    regular_hours = Column(Numeric(5, 2), default=0)
    overtime_hours = Column(Numeric(5, 2), default=0)
    night_shift_hours = Column(Numeric(5, 2), default=0)
    holiday_hours = Column(Numeric(5, 2), default=0)
    sunday_hours = Column(Numeric(5, 2), default=0)

    # Rates (JPY per hour)
    base_rate = Column(Numeric(10, 2), nullable=False)
    overtime_rate = Column(Numeric(10, 2), nullable=False)
    night_shift_rate = Column(Numeric(10, 2), nullable=False)
    holiday_rate = Column(Numeric(10, 2), nullable=False)

    # Amounts (JPY)
    base_amount = Column(Numeric(12, 2), default=0)
    overtime_amount = Column(Numeric(12, 2), default=0)
    night_shift_amount = Column(Numeric(12, 2), default=0)
    holiday_amount = Column(Numeric(12, 2), default=0)
    gross_amount = Column(Numeric(12, 2), default=0)

    # Deductions
    income_tax = Column(Numeric(10, 2), default=0)
    resident_tax = Column(Numeric(10, 2), default=0)
    health_insurance = Column(Numeric(10, 2), default=0)
    pension = Column(Numeric(10, 2), default=0)
    employment_insurance = Column(Numeric(10, 2), default=0)
    total_deductions = Column(Numeric(12, 2), default=0)

    # Net amount
    net_amount = Column(Numeric(12, 2), default=0)

    # Yukyu (有給休暇) Information
    yukyu_days_approved = Column(Numeric(4, 1), default=0)  # Días de yukyu aprobados en período
    yukyu_deduction_jpy = Column(Numeric(10, 2), default=0)  # Monto deducido por yukyu (¥)
    yukyu_request_ids = Column(Text, nullable=True)  # JSON: [1, 2, 3] para referencia a requests

    # Metadata
    timer_card_period_id = Column(Integer)
    payslip_generated = Column(Boolean, default=False)
    payslip_pdf_path = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    payroll_run = relationship("PayrollRun", back_populates="employee_payrolls")


class PayrollSettings(Base):
    """Model for payroll settings."""
    __tablename__ = "payroll_settings"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, index=True)
    overtime_rate = Column(Numeric(4, 2), default=1.25)
    night_shift_rate = Column(Numeric(4, 2), default=1.25)
    holiday_rate = Column(Numeric(4, 2), default=1.35)
    sunday_rate = Column(Numeric(4, 2), default=1.35)
    standard_hours_per_month = Column(Numeric(5, 2), default=160)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
