"""
Payroll Calculation Service

Calculates monthly payroll based on:
- Timer card hours (regular, overtime, night, holiday)
- Yukyu days used
- Apartment rent deductions
- Social insurance and tax deductions
"""
from datetime import date
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.models import (
    Employee, TimerCard, PayrollRecord,
    YukyuTransaction, YukyuTransactionType,
    ApartmentAssignment
)


class PayrollService:
    """Service for payroll calculations"""

    # Tax and insurance rates (simplified - should be from settings/DB)
    SOCIAL_INSURANCE_RATE = 0.145  # 14.5%
    HEALTH_INSURANCE_RATE = 0.050  # 5.0%
    PENSION_INSURANCE_RATE = 0.091  # 9.1%
    EMPLOYMENT_INSURANCE_RATE = 0.005  # 0.5%
    INCOME_TAX_RATE = 0.05  # 5% (simplified flat rate)

    # Overtime multipliers (Japanese labor law)
    OVERTIME_MULTIPLIER = 1.25  # 125% for overtime
    NIGHT_MULTIPLIER = 1.25     # 125% for night work
    HOLIDAY_MULTIPLIER = 1.35   # 135% for holiday work

    def __init__(self, db: Session):
        self.db = db

    def get_timer_cards_for_month(
        self,
        employee: Employee,
        year: int,
        month: int
    ) -> List[TimerCard]:
        """Get all timer cards for employee in specified month"""
        from calendar import monthrange

        # Get first and last day of month
        _, last_day = monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)

        timer_cards = self.db.query(TimerCard).filter(
            and_(
                TimerCard.employee_id == employee.hakenmoto_id,
                TimerCard.work_date >= start_date,
                TimerCard.work_date <= end_date,
                TimerCard.is_deleted == False
            )
        ).all()

        return timer_cards

    def get_yukyu_days_for_month(
        self,
        employee: Employee,
        year: int,
        month: int
    ) -> float:
        """Get total yukyu days used in month"""
        from calendar import monthrange

        _, last_day = monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)

        transactions = self.db.query(YukyuTransaction).filter(
            and_(
                YukyuTransaction.employee_id == employee.hakenmoto_id,
                YukyuTransaction.transaction_type == YukyuTransactionType.USE,
                YukyuTransaction.transaction_date >= start_date,
                YukyuTransaction.transaction_date <= end_date
            )
        ).all()

        total_days = sum(abs(t.days) for t in transactions)
        return total_days

    def get_apartment_rent(
        self,
        employee: Employee,
        year: int,
        month: int
    ) -> float:
        """Get apartment rent for month"""
        from calendar import monthrange

        _, last_day = monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)

        # Get active apartment assignment
        assignment = self.db.query(ApartmentAssignment).filter(
            and_(
                ApartmentAssignment.employee_id == employee.hakenmoto_id,
                ApartmentAssignment.is_active == True,
                ApartmentAssignment.move_in_date <= end_date,
                or_(
                    ApartmentAssignment.move_out_date == None,
                    ApartmentAssignment.move_out_date >= start_date
                )
            )
        ).first()

        if not assignment:
            return 0.0

        # Check if move-in was this month (prorated)
        if assignment.move_in_date.year == year and assignment.move_in_date.month == month:
            if assignment.prorated_first_month is not None:
                return assignment.prorated_first_month

        # Check if move-out was this month (prorated)
        if assignment.move_out_date and assignment.move_out_date.year == year and assignment.move_out_date.month == month:
            if assignment.prorated_last_month is not None:
                return assignment.prorated_last_month

        # Regular monthly rent
        return assignment.monthly_rent

    def calculate_gross_pay(
        self,
        base_hourly_rate: float,
        regular_hours: float,
        overtime_hours: float,
        night_hours: float,
        holiday_hours: float,
        yukyu_days: float
    ) -> Dict[str, float]:
        """
        Calculate gross pay breakdown

        Returns dict with individual pay components
        """
        # Calculate each component
        regular_pay = regular_hours * base_hourly_rate
        overtime_pay = overtime_hours * base_hourly_rate * self.OVERTIME_MULTIPLIER
        night_pay = night_hours * base_hourly_rate * self.NIGHT_MULTIPLIER
        holiday_pay = holiday_hours * base_hourly_rate * self.HOLIDAY_MULTIPLIER

        # Yukyu pay (8 hours per day at regular rate)
        yukyu_pay = yukyu_days * 8 * base_hourly_rate

        # Total gross pay
        gross_pay = regular_pay + overtime_pay + night_pay + holiday_pay + yukyu_pay

        return {
            "regular_pay": round(regular_pay, 2),
            "overtime_pay": round(overtime_pay, 2),
            "night_pay": round(night_pay, 2),
            "holiday_pay": round(holiday_pay, 2),
            "yukyu_pay": round(yukyu_pay, 2),
            "gross_pay": round(gross_pay, 2)
        }

    def calculate_deductions(
        self,
        gross_pay: float,
        apartment_rent: float,
        other_deductions: float = 0.0
    ) -> Dict[str, float]:
        """
        Calculate all deductions from gross pay

        Returns dict with individual deduction components
        """
        # Social insurance
        social_insurance = gross_pay * self.SOCIAL_INSURANCE_RATE

        # Health insurance
        health_insurance = gross_pay * self.HEALTH_INSURANCE_RATE

        # Pension insurance
        pension_insurance = gross_pay * self.PENSION_INSURANCE_RATE

        # Employment insurance
        employment_insurance = gross_pay * self.EMPLOYMENT_INSURANCE_RATE

        # Income tax (simplified - should use progressive tax tables)
        income_tax = gross_pay * self.INCOME_TAX_RATE

        # Total deductions
        total_deductions = (
            social_insurance +
            health_insurance +
            pension_insurance +
            employment_insurance +
            income_tax +
            apartment_rent +
            other_deductions
        )

        return {
            "social_insurance": round(social_insurance, 2),
            "health_insurance": round(health_insurance, 2),
            "pension_insurance": round(pension_insurance, 2),
            "employment_insurance": round(employment_insurance, 2),
            "income_tax": round(income_tax, 2),
            "apartment_rent": round(apartment_rent, 2),
            "other_deductions": round(other_deductions, 2),
            "total_deductions": round(total_deductions, 2)
        }

    def calculate_monthly_payroll(
        self,
        employee: Employee,
        year: int,
        month: int
    ) -> PayrollRecord:
        """
        Calculate complete payroll for employee for specified month

        Creates and returns PayrollRecord
        """
        # Check if payroll already exists
        existing = self.db.query(PayrollRecord).filter(
            and_(
                PayrollRecord.employee_id == employee.hakenmoto_id,
                PayrollRecord.year == year,
                PayrollRecord.month == month
            )
        ).first()

        if existing and existing.is_finalized:
            raise ValueError(f"Payroll for {year}/{month} is already finalized")

        # Get timer cards
        timer_cards = self.get_timer_cards_for_month(employee, year, month)

        # Aggregate hours
        total_regular_hours = sum(tc.regular_hours for tc in timer_cards)
        total_overtime_hours = sum(tc.overtime_hours for tc in timer_cards)
        total_night_hours = sum(tc.night_hours for tc in timer_cards)
        total_holiday_hours = sum(tc.holiday_hours for tc in timer_cards)

        # Get yukyu days
        yukyu_days = self.get_yukyu_days_for_month(employee, year, month)

        # Get apartment rent
        apartment_rent = self.get_apartment_rent(employee, year, month)

        # Calculate gross pay
        gross_components = self.calculate_gross_pay(
            base_hourly_rate=employee.jikyu,
            regular_hours=total_regular_hours,
            overtime_hours=total_overtime_hours,
            night_hours=total_night_hours,
            holiday_hours=total_holiday_hours,
            yukyu_days=yukyu_days
        )

        # Calculate deductions
        deduction_components = self.calculate_deductions(
            gross_pay=gross_components["gross_pay"],
            apartment_rent=apartment_rent
        )

        # Calculate net pay
        net_pay = gross_components["gross_pay"] - deduction_components["total_deductions"]

        # Create or update payroll record
        if existing:
            record = existing
        else:
            record = PayrollRecord(
                employee_id=employee.hakenmoto_id,
                year=year,
                month=month
            )

        # Update all fields
        record.regular_hours = total_regular_hours
        record.overtime_hours = total_overtime_hours
        record.night_hours = total_night_hours
        record.holiday_hours = total_holiday_hours
        record.yukyu_days = yukyu_days

        record.base_hourly_rate = employee.jikyu
        record.overtime_multiplier = self.OVERTIME_MULTIPLIER
        record.night_multiplier = self.NIGHT_MULTIPLIER
        record.holiday_multiplier = self.HOLIDAY_MULTIPLIER

        record.regular_pay = gross_components["regular_pay"]
        record.overtime_pay = gross_components["overtime_pay"]
        record.night_pay = gross_components["night_pay"]
        record.holiday_pay = gross_components["holiday_pay"]
        record.gross_pay = gross_components["gross_pay"]

        record.social_insurance = deduction_components["social_insurance"]
        record.health_insurance = deduction_components["health_insurance"]
        record.pension_insurance = deduction_components["pension_insurance"]
        record.employment_insurance = deduction_components["employment_insurance"]
        record.income_tax = deduction_components["income_tax"]
        record.apartment_rent = apartment_rent
        record.other_deductions = deduction_components["other_deductions"]
        record.total_deductions = deduction_components["total_deductions"]

        record.net_pay = net_pay

        if not existing:
            self.db.add(record)

        self.db.commit()
        self.db.refresh(record)

        return record

    def finalize_payroll(
        self,
        record: PayrollRecord,
        finalized_by_user_id: int
    ) -> PayrollRecord:
        """
        Finalize payroll record (lock it from further edits)

        Args:
            record: PayrollRecord to finalize
            finalized_by_user_id: User ID who is finalizing

        Returns:
            Updated PayrollRecord
        """
        from datetime import datetime

        if record.is_finalized:
            raise ValueError("Payroll is already finalized")

        record.is_finalized = True
        record.finalized_by = finalized_by_user_id
        record.finalized_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(record)

        return record

    def calculate_batch_payroll(
        self,
        year: int,
        month: int,
        employee_ids: Optional[List[int]] = None
    ) -> List[PayrollRecord]:
        """
        Calculate payroll for multiple employees

        If employee_ids is None, calculate for all active employees

        Returns list of PayrollRecords created/updated
        """
        from app.models.models import EmployeeStatus

        if employee_ids:
            employees = self.db.query(Employee).filter(
                Employee.hakenmoto_id.in_(employee_ids)
            ).all()
        else:
            employees = self.db.query(Employee).filter(
                Employee.status == EmployeeStatus.ACTIVE
            ).all()

        records = []
        for employee in employees:
            try:
                record = self.calculate_monthly_payroll(employee, year, month)
                records.append(record)
            except Exception as e:
                print(f"Error calculating payroll for employee {employee.hakenmoto_id}: {e}")
                continue

        return records
