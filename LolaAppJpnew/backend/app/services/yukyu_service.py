"""
Yukyu (Paid Vacation) Service - LIFO Deduction Strategy

Implements Last-In-First-Out deduction for paid vacation days:
- Newest grants are used first
- Oldest grants expire first
- Automatic expiration tracking (2 years)
- Fiscal year management
"""
from datetime import date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.models import (
    Employee, YukyuBalance, YukyuTransaction,
    YukyuTransactionType, Request, RequestType, RequestStatus
)


class YukyuService:
    """Service for Yukyu management with LIFO deduction"""

    def __init__(self, db: Session):
        self.db = db

    def get_fiscal_year(self, reference_date: date) -> int:
        """
        Get fiscal year for a given date

        Japanese fiscal year: April 1 - March 31
        """
        if reference_date.month >= 4:
            return reference_date.year
        else:
            return reference_date.year - 1

    def calculate_grant_amount(
        self,
        hire_date: date,
        reference_date: date
    ) -> float:
        """
        Calculate yukyu grant amount based on years of service

        Japanese labor law standard:
        - 6 months: 10 days
        - 1.5 years: 11 days
        - 2.5 years: 12 days
        - 3.5 years: 14 days
        - 4.5 years: 16 days
        - 5.5 years: 18 days
        - 6.5+ years: 20 days
        """
        days_worked = (reference_date - hire_date).days
        years = days_worked / 365.25

        if years < 0.5:
            return 0.0
        elif years < 1.5:
            return 10.0
        elif years < 2.5:
            return 11.0
        elif years < 3.5:
            return 12.0
        elif years < 4.5:
            return 14.0
        elif years < 5.5:
            return 16.0
        elif years < 6.5:
            return 18.0
        else:
            return 20.0

    def grant_yukyu(
        self,
        employee: Employee,
        fiscal_year: int,
        granted_days: float,
        grant_date: date
    ) -> YukyuBalance:
        """
        Grant yukyu days to employee for fiscal year

        Creates balance record with 2-year expiration
        """
        # Check if already granted for this fiscal year
        existing = self.db.query(YukyuBalance).filter(
            and_(
                YukyuBalance.employee_id == employee.hakenmoto_id,
                YukyuBalance.fiscal_year == fiscal_year
            )
        ).first()

        if existing:
            raise ValueError(f"Yukyu already granted for fiscal year {fiscal_year}")

        # Create balance record
        expiry_date = grant_date + timedelta(days=730)  # 2 years

        balance = YukyuBalance(
            employee_id=employee.hakenmoto_id,
            fiscal_year=fiscal_year,
            granted_days=granted_days,
            used_days=0.0,
            remaining_days=granted_days,
            grant_date=grant_date,
            expiry_date=expiry_date,
            is_expired=False
        )

        self.db.add(balance)

        # Create grant transaction
        transaction = YukyuTransaction(
            balance_id=balance.id,
            employee_id=employee.hakenmoto_id,
            transaction_type=YukyuTransactionType.GRANT,
            transaction_date=grant_date,
            days=granted_days,
            description=f"Annual grant for FY{fiscal_year}"
        )

        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(balance)

        return balance

    def get_available_balances(
        self,
        employee: Employee,
        as_of_date: Optional[date] = None
    ) -> List[YukyuBalance]:
        """
        Get available yukyu balances for employee, sorted by fiscal year (newest first)

        LIFO: Returns balances from newest to oldest for deduction
        """
        if as_of_date is None:
            as_of_date = date.today()

        balances = self.db.query(YukyuBalance).filter(
            and_(
                YukyuBalance.employee_id == employee.hakenmoto_id,
                YukyuBalance.remaining_days > 0,
                YukyuBalance.is_expired == False,
                YukyuBalance.expiry_date > as_of_date
            )
        ).order_by(YukyuBalance.fiscal_year.desc()).all()  # DESC = LIFO

        return balances

    def calculate_total_available(
        self,
        employee: Employee,
        as_of_date: Optional[date] = None
    ) -> float:
        """Calculate total available yukyu days"""
        balances = self.get_available_balances(employee, as_of_date)
        return sum(b.remaining_days for b in balances)

    def use_yukyu(
        self,
        employee: Employee,
        days_to_use: float,
        usage_date: date,
        request_id: Optional[int] = None,
        description: Optional[str] = None
    ) -> List[YukyuTransaction]:
        """
        Deduct yukyu days using LIFO strategy

        Uses newest grants first (highest fiscal year)
        Returns list of transactions created
        """
        if days_to_use <= 0:
            raise ValueError("Days to use must be positive")

        # Get available balances (sorted newest first for LIFO)
        balances = self.get_available_balances(employee, usage_date)

        # Check if enough days available
        total_available = sum(b.remaining_days for b in balances)
        if total_available < days_to_use:
            raise ValueError(
                f"Insufficient yukyu days. Available: {total_available}, Requested: {days_to_use}"
            )

        # Deduct from balances using LIFO
        remaining_to_deduct = days_to_use
        transactions = []

        for balance in balances:
            if remaining_to_deduct <= 0:
                break

            # Calculate deduction from this balance
            deduction = min(remaining_to_deduct, balance.remaining_days)

            # Update balance
            balance.used_days += deduction
            balance.remaining_days -= deduction

            # Create transaction
            transaction = YukyuTransaction(
                balance_id=balance.id,
                employee_id=employee.hakenmoto_id,
                transaction_type=YukyuTransactionType.USE,
                transaction_date=usage_date,
                days=-deduction,  # Negative for usage
                request_id=request_id,
                description=description or f"Yukyu usage from FY{balance.fiscal_year}"
            )

            self.db.add(transaction)
            transactions.append(transaction)

            remaining_to_deduct -= deduction

        self.db.commit()

        return transactions

    def expire_old_balances(self, as_of_date: Optional[date] = None) -> int:
        """
        Mark expired yukyu balances

        Returns number of balances expired
        """
        if as_of_date is None:
            as_of_date = date.today()

        # Find balances that have expired
        expired_balances = self.db.query(YukyuBalance).filter(
            and_(
                YukyuBalance.is_expired == False,
                YukyuBalance.expiry_date <= as_of_date,
                YukyuBalance.remaining_days > 0
            )
        ).all()

        count = 0
        for balance in expired_balances:
            # Mark as expired
            balance.is_expired = True

            # Create expiration transaction for remaining days
            if balance.remaining_days > 0:
                transaction = YukyuTransaction(
                    balance_id=balance.id,
                    employee_id=balance.employee_id,
                    transaction_type=YukyuTransactionType.EXPIRE,
                    transaction_date=as_of_date,
                    days=-balance.remaining_days,  # Negative for expiration
                    description=f"Expired yukyu from FY{balance.fiscal_year}"
                )
                self.db.add(transaction)

                # Zero out remaining days
                balance.remaining_days = 0.0

            count += 1

        self.db.commit()

        return count

    def get_employee_yukyu_summary(
        self,
        employee: Employee,
        as_of_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive yukyu summary for employee

        Returns dict with balances, transactions, and totals
        """
        if as_of_date is None:
            as_of_date = date.today()

        balances = self.get_available_balances(employee, as_of_date)
        total_available = sum(b.remaining_days for b in balances)

        # Get recent transactions (last 12 months)
        one_year_ago = as_of_date - timedelta(days=365)
        recent_transactions = self.db.query(YukyuTransaction).filter(
            and_(
                YukyuTransaction.employee_id == employee.hakenmoto_id,
                YukyuTransaction.transaction_date >= one_year_ago
            )
        ).order_by(YukyuTransaction.transaction_date.desc()).all()

        # Calculate totals
        granted_this_year = sum(
            t.days for t in recent_transactions
            if t.transaction_type == YukyuTransactionType.GRANT
        )

        used_this_year = sum(
            abs(t.days) for t in recent_transactions
            if t.transaction_type == YukyuTransactionType.USE
        )

        expired_this_year = sum(
            abs(t.days) for t in recent_transactions
            if t.transaction_type == YukyuTransactionType.EXPIRE
        )

        return {
            "employee_id": employee.hakenmoto_id,
            "employee_name": employee.full_name_kanji,
            "total_available": total_available,
            "balances": [
                {
                    "fiscal_year": b.fiscal_year,
                    "granted": b.granted_days,
                    "used": b.used_days,
                    "remaining": b.remaining_days,
                    "grant_date": b.grant_date.isoformat(),
                    "expiry_date": b.expiry_date.isoformat(),
                    "days_until_expiry": (b.expiry_date - as_of_date).days
                }
                for b in balances
            ],
            "recent_transactions": [
                {
                    "date": t.transaction_date.isoformat(),
                    "type": t.transaction_type.value,
                    "days": t.days,
                    "description": t.description
                }
                for t in recent_transactions[:10]  # Last 10 transactions
            ],
            "year_totals": {
                "granted": granted_this_year,
                "used": used_this_year,
                "expired": expired_this_year
            }
        }

    def auto_grant_annual_yukyu(self, as_of_date: Optional[date] = None) -> int:
        """
        Automatically grant annual yukyu to all eligible employees

        Should be run on each employee's anniversary date
        Returns number of employees granted yukyu
        """
        if as_of_date is None:
            as_of_date = date.today()

        from app.models.models import EmployeeStatus

        # Get all active employees
        employees = self.db.query(Employee).filter(
            Employee.status == EmployeeStatus.ACTIVE
        ).all()

        granted_count = 0
        fiscal_year = self.get_fiscal_year(as_of_date)

        for employee in employees:
            # Check if employee is eligible (has hire_date)
            if not employee.hire_date:
                continue

            # Calculate yukyu amount
            days_to_grant = self.calculate_grant_amount(employee.hire_date, as_of_date)

            if days_to_grant <= 0:
                continue

            # Check if already granted this fiscal year
            existing = self.db.query(YukyuBalance).filter(
                and_(
                    YukyuBalance.employee_id == employee.hakenmoto_id,
                    YukyuBalance.fiscal_year == fiscal_year
                )
            ).first()

            if existing:
                continue  # Already granted

            # Grant yukyu
            try:
                self.grant_yukyu(employee, fiscal_year, days_to_grant, as_of_date)
                granted_count += 1
            except Exception as e:
                print(f"Error granting yukyu to employee {employee.hakenmoto_id}: {e}")
                continue

        return granted_count
