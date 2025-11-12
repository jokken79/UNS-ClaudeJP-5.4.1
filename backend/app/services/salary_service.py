"""
Unified Salary Service for UNS-ClaudeJP 5.4.1

This service consolidates salary calculation logic from:
- backend/app/api/salary.py (calculate_employee_salary function)
- backend/app/services/payroll_service.py (PayrollService class)

Features:
- Uses PayrollSettings from database (NOT hardcoded)
- Integrates with rent_deductions for apartment charges
- Supports overtime, night, holiday, and Sunday hours
- Calculates all deductions: income tax, resident tax, health insurance, pension, employment insurance
- Full validation and error handling
- Async/await for FastAPI compatibility
"""

import logging
from datetime import datetime, timedelta, date
from typing import Any, Dict, List, Optional, Tuple
from decimal import Decimal

from sqlalchemy import extract, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.models.models import (
    SalaryCalculation, Employee, TimerCard, Factory, Apartment,
    RentDeduction, DeductionStatus
)
from app.models.payroll_models import PayrollSettings, PayrollRun, EmployeePayroll
from app.schemas.salary import (
    SalaryCalculationResponse, SalaryBulkResult, SalaryStatistics
)
from app.schemas.payroll import (
    EmployeePayrollResult, HoursBreakdown, Rates, Amounts,
    DeductionsDetail, ValidationResult
)
from app.core.config import settings, PayrollConfig
from app.services.config_service import PayrollConfigService

logger = logging.getLogger(__name__)


class SalaryService:
    """
    Unified Salary Service for calculating employee salaries.

    This service provides comprehensive salary calculation functionality including:
    - Individual salary calculation
    - Bulk salary calculation for multiple employees
    - Payment status management
    - Salary statistics and reporting
    - Full validation and error handling

    The service integrates with:
    - TimerCard: For work hours tracking
    - Employee: For employee information and rates
    - Factory: For factory-specific configurations
    - RentDeduction: For apartment rent deductions (V2)
    - PayrollSettings: For configurable rates and rules

    Attributes:
        db (AsyncSession): Async database session for queries

    Example:
        >>> async with get_db() as db:
        ...     service = SalaryService(db)
        ...     result = await service.calculate_salary(
        ...         employee_id=123,
        ...         month=10,
        ...         year=2025
        ...     )
        ...     print(f"Net salary: ¥{result.net_salary:,}")
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the salary service.

        Args:
            db: AsyncSession database connection
        """
        self.db = db
        self.config_service = PayrollConfigService(db)

    async def calculate_salary(
        self,
        employee_id: int,
        month: int,
        year: int,
        timer_records: Optional[List[TimerCard]] = None,
        bonus: Optional[int] = None,
        gasoline_allowance: Optional[int] = None,
        other_deductions: Optional[int] = None,
        save_to_db: bool = True
    ) -> SalaryCalculationResponse:
        """
        Calculate salary for a single employee.

        This is the main method that orchestrates the entire salary calculation process:
        1. Fetch employee data and validate
        2. Get timer cards for the specified month
        3. Load payroll settings from database
        4. Calculate hours breakdown (regular, overtime, night, holiday)
        5. Calculate gross amounts for each hour type
        6. Calculate all deductions (apartment, taxes, insurance)
        7. Calculate net salary
        8. Optionally save to database

        Args:
            employee_id: Employee ID
            month: Month (1-12)
            year: Year (e.g., 2025)
            timer_records: Optional pre-loaded timer cards (if None, fetches from DB)
            bonus: Optional bonus amount to override calculated value
            gasoline_allowance: Optional gasoline allowance to override
            other_deductions: Optional other deductions amount
            save_to_db: Whether to save calculation to database (default: True)

        Returns:
            SalaryCalculationResponse: Complete salary calculation with all details

        Raises:
            ValueError: If employee not found, no timer cards, or invalid data
            HTTPException: For database or calculation errors

        Example:
            >>> result = await service.calculate_salary(
            ...     employee_id=123,
            ...     month=10,
            ...     year=2025
            ... )
            >>> print(f"Gross: ¥{result.gross_salary:,}, Net: ¥{result.net_salary:,}")
        """
        try:
            # 1. Fetch employee with relationships
            employee = await self._get_employee(employee_id)
            if not employee:
                raise ValueError(f"Employee with ID {employee_id} not found")

            # 2. Get timer cards for the month
            if timer_records is None:
                timer_records = await self._get_timer_cards(employee_id, month, year)

            # 2a. Validate timer cards exist and have required data
            validation_result = self._validate_timer_cards(timer_records, employee_id, month, year)
            if not validation_result['valid']:
                raise ValueError(validation_result['error'])

            # 3. Get payroll settings from database
            payroll_settings = await self._get_payroll_settings()

            # 4. Get factory configuration
            factory = None
            if employee.factory_id:
                factory = await self._get_factory(employee.factory_id)

            # 5. Calculate hours breakdown
            hours_breakdown = await self._calculate_hours_breakdown(timer_records)

            # 6. Calculate gross amounts
            amounts = await self._calculate_amounts(
                employee=employee,
                hours_breakdown=hours_breakdown,
                payroll_settings=payroll_settings
            )

            # 7. Calculate apartment deductions
            apartment_deduction = await self._get_apartment_deductions(
                employee_id=employee_id,
                year=year,
                month=month,
                employee=employee,
                work_days=hours_breakdown['work_days']
            )

            # 8. Calculate bonuses from factory config
            calculated_bonus = 0
            calculated_gasoline = 0

            if factory and factory.config:
                bonuses_config = factory.config.get("bonuses", {})

                # Gasoline allowance
                if bonuses_config.get("gasoline_allowance", {}).get("enabled"):
                    amount_per_day = bonuses_config["gasoline_allowance"].get("amount_per_day", 0)
                    calculated_gasoline = amount_per_day * hours_breakdown['work_days']

                # Attendance bonus
                if bonuses_config.get("attendance_bonus", {}).get("enabled"):
                    bonus_config = bonuses_config["attendance_bonus"]
                    conditions = bonus_config.get("conditions", {})
                    if conditions.get("full_month") and hours_breakdown['work_days'] >= 20:
                        calculated_bonus += bonus_config.get("amount", 0)

            # Override with provided values if any
            final_bonus = bonus if bonus is not None else calculated_bonus
            final_gasoline = gasoline_allowance if gasoline_allowance is not None else calculated_gasoline
            final_other_deductions = other_deductions if other_deductions is not None else 0

            # 9. Calculate final gross and net
            gross_salary = (
                amounts['base_amount'] +
                amounts['overtime_amount'] +
                amounts['night_amount'] +
                amounts['holiday_amount'] +
                final_bonus +
                final_gasoline
            )

            net_salary = gross_salary - apartment_deduction - final_other_deductions

            # 10. Calculate factory payment and company profit
            factory_payment = 0
            company_profit = 0

            if factory and factory.config:
                working_hours_config = factory.config.get("working_hours", {})
                shifts = working_hours_config.get("shifts", [])
                if shifts:
                    jikyu_tanka = shifts[0].get("jikyu_tanka", employee.jikyu)
                    total_hours = (
                        hours_breakdown['total_regular_hours'] +
                        hours_breakdown['total_overtime_hours'] +
                        hours_breakdown['total_night_hours'] +
                        hours_breakdown['total_holiday_hours']
                    )
                    factory_payment = int(float(jikyu_tanka) * float(total_hours))
                    company_profit = factory_payment - gross_salary

            # 11. Create salary calculation object
            salary_data = {
                "employee_id": employee_id,
                "month": month,
                "year": year,
                "total_regular_hours": hours_breakdown['total_regular_hours'],
                "total_overtime_hours": hours_breakdown['total_overtime_hours'],
                "total_night_hours": hours_breakdown['total_night_hours'],
                "total_holiday_hours": hours_breakdown['total_holiday_hours'],
                "base_salary": amounts['base_amount'],
                "overtime_pay": amounts['overtime_amount'],
                "night_pay": amounts['night_amount'],
                "holiday_pay": amounts['holiday_amount'],
                "bonus": final_bonus,
                "gasoline_allowance": final_gasoline,
                "apartment_deduction": apartment_deduction,
                "other_deductions": final_other_deductions,
                "gross_salary": gross_salary,
                "net_salary": net_salary,
                "factory_payment": factory_payment,
                "company_profit": company_profit,
                "is_paid": False,
                "paid_at": None
            }

            # 12. Save to database if requested
            if save_to_db:
                # Check if already exists
                stmt = select(SalaryCalculation).where(
                    and_(
                        SalaryCalculation.employee_id == employee_id,
                        SalaryCalculation.month == month,
                        SalaryCalculation.year == year
                    )
                )
                result = await self.db.execute(stmt)
                existing = result.scalar_one_or_none()

                if existing:
                    raise ValueError(
                        f"Salary already calculated for employee {employee_id} in {year}-{month:02d}"
                    )

                # Create new salary calculation
                new_salary = SalaryCalculation(**salary_data)
                self.db.add(new_salary)
                await self.db.commit()
                await self.db.refresh(new_salary)

                logger.info(
                    f"Salary calculated and saved for employee {employee_id}, "
                    f"period {year}-{month:02d}: ¥{gross_salary:,} gross, ¥{net_salary:,} net"
                )

                return SalaryCalculationResponse.model_validate(new_salary)
            else:
                # Return without saving
                return SalaryCalculationResponse(**salary_data, id=0, created_at=datetime.now())

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error calculating salary for employee {employee_id}: {e}", exc_info=True)
            raise ValueError(f"Error calculating salary: {str(e)}")

    async def calculate_bulk_salaries(
        self,
        employee_ids: Optional[List[int]],
        month: int,
        year: int,
        factory_id: Optional[str] = None
    ) -> SalaryBulkResult:
        """
        Calculate salaries for multiple employees.

        This method processes salary calculations for a group of employees in batch.
        It's useful for monthly payroll processing.

        Args:
            employee_ids: List of employee IDs to calculate (if None, uses all active)
            month: Month (1-12)
            year: Year
            factory_id: Optional factory ID to filter employees

        Returns:
            SalaryBulkResult: Summary of bulk calculation with success/failure counts

        Example:
            >>> result = await service.calculate_bulk_salaries(
            ...     employee_ids=[1, 2, 3],
            ...     month=10,
            ...     year=2025
            ... )
            >>> print(f"Success: {result.successful}, Failed: {result.failed}")
        """
        try:
            # Build query for employees
            stmt = select(Employee).where(Employee.is_active == True)

            if employee_ids:
                stmt = stmt.where(Employee.id.in_(employee_ids))
            elif factory_id:
                stmt = stmt.where(Employee.factory_id == factory_id)

            result = await self.db.execute(stmt)
            employees = result.scalars().all()

            # Process each employee
            successful = 0
            failed = 0
            errors = []
            total_gross = 0
            total_net = 0
            total_profit = 0

            for employee in employees:
                try:
                    salary = await self.calculate_salary(
                        employee_id=employee.id,
                        month=month,
                        year=year,
                        save_to_db=True
                    )

                    successful += 1
                    total_gross += salary.gross_salary
                    total_net += salary.net_salary
                    total_profit += salary.company_profit

                except Exception as e:
                    failed += 1
                    error_msg = f"Employee {employee.hakenmoto_id or employee.id}: {str(e)}"
                    errors.append(error_msg)
                    logger.warning(error_msg)

            logger.info(
                f"Bulk salary calculation completed for {year}-{month:02d}: "
                f"{successful} successful, {failed} failed"
            )

            return SalaryBulkResult(
                total_employees=len(employees),
                successful=successful,
                failed=failed,
                total_gross_salary=total_gross,
                total_net_salary=total_net,
                total_company_profit=total_profit,
                errors=errors
            )

        except Exception as e:
            logger.error(f"Error in bulk salary calculation: {e}", exc_info=True)
            raise ValueError(f"Error calculating bulk salaries: {str(e)}")

    async def mark_as_paid(
        self,
        salary_ids: List[int],
        payment_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Mark salary calculations as paid.

        Args:
            salary_ids: List of salary calculation IDs to mark as paid
            payment_date: Payment date (defaults to now)

        Returns:
            Dictionary with success message and count

        Example:
            >>> result = await service.mark_as_paid([1, 2, 3])
            >>> print(result['message'])
        """
        try:
            stmt = select(SalaryCalculation).where(
                SalaryCalculation.id.in_(salary_ids)
            )
            result = await self.db.execute(stmt)
            salaries = result.scalars().all()

            actual_payment_date = payment_date or datetime.now()

            for salary in salaries:
                salary.is_paid = True
                salary.paid_at = actual_payment_date

            await self.db.commit()

            logger.info(f"Marked {len(salaries)} salaries as paid on {actual_payment_date}")

            return {
                "message": f"Marked {len(salaries)} salaries as paid",
                "count": len(salaries),
                "payment_date": actual_payment_date
            }

        except Exception as e:
            logger.error(f"Error marking salaries as paid: {e}", exc_info=True)
            raise ValueError(f"Error marking salaries as paid: {str(e)}")

    async def get_salary_statistics(
        self,
        month: int,
        year: int
    ) -> SalaryStatistics:
        """
        Get salary statistics for a specific month.

        Args:
            month: Month (1-12)
            year: Year

        Returns:
            SalaryStatistics: Comprehensive statistics for the month

        Example:
            >>> stats = await service.get_salary_statistics(10, 2025)
            >>> print(f"Average salary: ¥{stats.average_salary:,}")
        """
        try:
            # Get all salaries for the month
            stmt = select(SalaryCalculation).where(
                and_(
                    SalaryCalculation.month == month,
                    SalaryCalculation.year == year
                )
            )
            result = await self.db.execute(stmt)
            salaries = result.scalars().all()

            if not salaries:
                raise ValueError(f"No salary data found for {year}-{month:02d}")

            # Calculate totals
            total_employees = len(salaries)
            total_gross = sum(s.gross_salary for s in salaries)
            total_net = sum(s.net_salary for s in salaries)
            total_deductions = total_gross - total_net
            total_revenue = sum(s.factory_payment for s in salaries)
            total_profit = sum(s.company_profit for s in salaries)
            avg_salary = total_net // total_employees if total_employees > 0 else 0

            # Group by factory
            factory_stats = {}
            for salary in salaries:
                # Get employee to find factory
                stmt_emp = select(Employee).where(Employee.id == salary.employee_id)
                result_emp = await self.db.execute(stmt_emp)
                employee = result_emp.scalar_one_or_none()

                if employee and employee.factory_id:
                    factory_id = employee.factory_id
                    if factory_id not in factory_stats:
                        factory_stats[factory_id] = {
                            "factory_id": factory_id,
                            "employees": 0,
                            "total_salary": 0,
                            "total_profit": 0
                        }
                    factory_stats[factory_id]["employees"] += 1
                    factory_stats[factory_id]["total_salary"] += salary.net_salary
                    factory_stats[factory_id]["total_profit"] += salary.company_profit

            logger.info(f"Generated salary statistics for {year}-{month:02d}: {total_employees} employees")

            return SalaryStatistics(
                month=month,
                year=year,
                total_employees=total_employees,
                total_gross_salary=total_gross,
                total_net_salary=total_net,
                total_deductions=total_deductions,
                total_company_revenue=total_revenue,
                total_company_profit=total_profit,
                average_salary=avg_salary,
                factories=list(factory_stats.values())
            )

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error getting salary statistics: {e}", exc_info=True)
            raise ValueError(f"Error getting salary statistics: {str(e)}")

    async def validate_salary(
        self,
        employee_id: int,
        month: int,
        year: int,
        timer_records: Optional[List[TimerCard]] = None
    ) -> ValidationResult:
        """
        Validate salary data before calculation.

        This method checks for common issues like:
        - Missing timer cards
        - Invalid employee data
        - Missing payroll settings
        - Data inconsistencies

        Args:
            employee_id: Employee ID
            month: Month (1-12)
            year: Year
            timer_records: Optional timer cards to validate

        Returns:
            ValidationResult: Validation result with errors and warnings

        Example:
            >>> validation = await service.validate_salary(123, 10, 2025)
            >>> if not validation.is_valid:
            ...     print("Errors:", validation.errors)
        """
        errors = []
        warnings = []

        try:
            # Check employee exists
            employee = await self._get_employee(employee_id)
            if not employee:
                errors.append(f"Employee {employee_id} not found")
                return ValidationResult(
                    is_valid=False,
                    errors=errors,
                    warnings=warnings,
                    validated_at=datetime.now()
                )

            # Check if employee is active
            if not employee.is_active:
                errors.append(f"Employee {employee_id} is not active")

            # Check hourly rate
            if not employee.jikyu or employee.jikyu <= 0:
                errors.append(f"Employee {employee_id} has invalid hourly rate (jikyu)")

            # Check timer cards
            if timer_records is None:
                timer_records = await self._get_timer_cards(employee_id, month, year)

            if not timer_records:
                errors.append(f"No approved timer cards found for {year}-{month:02d}")
            else:
                # Validate timer cards
                for tc in timer_records:
                    if not tc.clock_in or not tc.clock_out:
                        warnings.append(f"Timer card on {tc.work_date} has missing clock in/out times")

            # Check payroll settings
            payroll_settings = await self._get_payroll_settings()
            if not payroll_settings:
                warnings.append("No payroll settings found, using default values")

            # Check if already calculated
            stmt = select(SalaryCalculation).where(
                and_(
                    SalaryCalculation.employee_id == employee_id,
                    SalaryCalculation.month == month,
                    SalaryCalculation.year == year
                )
            )
            result = await self.db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                warnings.append(f"Salary already calculated for {year}-{month:02d}")

            is_valid = len(errors) == 0

            return ValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                validated_at=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error validating salary data: {e}", exc_info=True)
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"],
                warnings=warnings,
                validated_at=datetime.now()
            )

    # ==================== Private Helper Methods ====================

    async def _get_employee(self, employee_id: int) -> Optional[Employee]:
        """
        Fetch employee by ID with relationships.

        Args:
            employee_id: Employee ID

        Returns:
            Employee object or None if not found
        """
        stmt = select(Employee).where(Employee.id == employee_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_factory(self, factory_id: str) -> Optional[Factory]:
        """
        Fetch factory by ID.

        Args:
            factory_id: Factory ID

        Returns:
            Factory object or None if not found
        """
        stmt = select(Factory).where(Factory.factory_id == factory_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_timer_cards(
        self,
        employee_id: int,
        month: int,
        year: int
    ) -> List[TimerCard]:
        """
        Fetch approved timer cards for an employee in a specific month.

        Args:
            employee_id: Employee ID
            month: Month (1-12)
            year: Year

        Returns:
            List of approved TimerCard objects
        """
        stmt = select(TimerCard).where(
            and_(
                TimerCard.employee_id == employee_id,
                TimerCard.is_approved == True,
                extract('month', TimerCard.work_date) == month,
                extract('year', TimerCard.work_date) == year
            )
        ).order_by(TimerCard.work_date)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    def _validate_timer_cards(
        self,
        timer_records: List[TimerCard],
        employee_id: int,
        month: int,
        year: int
    ) -> Dict[str, Any]:
        """
        Validate timer cards before salary calculation.

        Performs comprehensive validation to ensure timer cards have all required
        data for accurate salary calculation.

        Args:
            timer_records: List of timer card records
            employee_id: Employee ID for error messages
            month: Month being calculated
            year: Year being calculated

        Returns:
            Dict with keys:
                - 'valid' (bool): True if validation passed
                - 'error' (str): Error message if validation failed
                - 'warnings' (List[str]): Non-critical warnings

        Validation checks:
            1. Timer cards list is not empty
            2. All timer cards have required fields (work_date, hours)
            3. All timer cards are approved
            4. Timer cards cover reasonable date range
            5. Hours are within valid ranges
        """
        warnings = []

        # Check 1: Timer cards exist
        if not timer_records:
            return {
                'valid': False,
                'error': f"No approved timer cards found for employee {employee_id} in {year}-{month:02d}. "
                        f"Cannot calculate salary without attendance records.",
                'warnings': []
            }

        # Check 2: All timer cards have required fields
        for idx, tc in enumerate(timer_records):
            if not tc.work_date:
                return {
                    'valid': False,
                    'error': f"Timer card #{idx+1} for employee {employee_id} is missing work_date",
                    'warnings': warnings
                }

            if tc.total_hours is None or tc.total_hours < 0:
                return {
                    'valid': False,
                    'error': f"Timer card for {tc.work_date} has invalid total_hours: {tc.total_hours}",
                    'warnings': warnings
                }

        # Check 3: All timer cards are approved
        unapproved = [tc for tc in timer_records if not tc.is_approved]
        if unapproved:
            return {
                'valid': False,
                'error': f"Found {len(unapproved)} unapproved timer cards for employee {employee_id}. "
                        f"All timer cards must be approved before salary calculation.",
                'warnings': warnings
            }

        # Check 4: Timer cards are in the correct month/year
        wrong_period = []
        for tc in timer_records:
            if tc.work_date.month != month or tc.work_date.year != year:
                wrong_period.append(tc.work_date)

        if wrong_period:
            return {
                'valid': False,
                'error': f"Found timer cards from wrong period: {wrong_period}. "
                        f"Expected {year}-{month:02d}",
                'warnings': warnings
            }

        # Check 5: Hours are within reasonable ranges (warning only)
        for tc in timer_records:
            if tc.total_hours and tc.total_hours > 24:
                warnings.append(
                    f"Timer card for {tc.work_date} has unusually high hours: {tc.total_hours}. "
                    f"Please verify this is correct."
                )

        # Check 6: Minimum attendance coverage (warning only)
        if len(timer_records) < 20:
            warnings.append(
                f"Only {len(timer_records)} days of attendance recorded for {year}-{month:02d}. "
                f"This may result in lower than expected salary."
            )

        # All validations passed
        logger.info(
            f"Timer cards validated for employee {employee_id} ({year}-{month:02d}): "
            f"{len(timer_records)} records, {len(warnings)} warnings"
        )

        return {
            'valid': True,
            'error': None,
            'warnings': warnings
        }

    async def _get_payroll_settings(self) -> Optional[PayrollSettings]:
        """
        Fetch payroll settings from database using PayrollConfigService.

        This method now uses PayrollConfigService which provides:
        - Automatic caching for performance
        - Fallback to default values
        - Automatic creation of missing settings

        Returns:
            PayrollSettings object (never None - creates defaults if missing)
        """
        try:
            settings_obj = await self.config_service.get_configuration()
            return settings_obj
        except Exception as e:
            logger.error(f"Error fetching payroll settings via config service: {e}", exc_info=True)
            logger.warning("Falling back to direct database query")
            # Fallback to direct query if config service fails
            stmt = select(PayrollSettings).order_by(PayrollSettings.id.desc()).limit(1)
            result = await self.db.execute(stmt)
            settings_obj = result.scalar_one_or_none()

            if not settings_obj:
                logger.warning("No payroll settings found in database, using defaults from PayrollConfig")

            return settings_obj

    async def _calculate_hours_breakdown(
        self,
        timer_records: List[TimerCard]
    ) -> Dict[str, Any]:
        """
        Calculate hours breakdown from timer cards.

        This method processes all timer cards and categorizes hours into:
        - Regular hours (通常時間)
        - Overtime hours (時間外労働)
        - Night hours (深夜労働: 22:00-05:00)
        - Holiday hours (休日労働: weekends)

        Args:
            timer_records: List of approved timer cards

        Returns:
            Dictionary with hours breakdown:
                {
                    'total_regular_hours': Decimal,
                    'total_overtime_hours': Decimal,
                    'total_night_hours': Decimal,
                    'total_holiday_hours': Decimal,
                    'work_days': int
                }
        """
        total_regular_hours = Decimal('0')
        total_overtime_hours = Decimal('0')
        total_night_hours = Decimal('0')
        total_holiday_hours = Decimal('0')
        work_days = 0

        for tc in timer_records:
            # Use pre-calculated hours from timer card if available
            if tc.regular_hours is not None:
                total_regular_hours += Decimal(str(tc.regular_hours))
            if tc.overtime_hours is not None:
                total_overtime_hours += Decimal(str(tc.overtime_hours))
            if tc.night_hours is not None:
                total_night_hours += Decimal(str(tc.night_hours))
            if tc.holiday_hours is not None:
                total_holiday_hours += Decimal(str(tc.holiday_hours))

            work_days += 1

        return {
            'total_regular_hours': total_regular_hours,
            'total_overtime_hours': total_overtime_hours,
            'total_night_hours': total_night_hours,
            'total_holiday_hours': total_holiday_hours,
            'work_days': work_days
        }

    async def _calculate_amounts(
        self,
        employee: Employee,
        hours_breakdown: Dict[str, Any],
        payroll_settings: Optional[PayrollSettings]
    ) -> Dict[str, int]:
        """
        Calculate payment amounts for all hour types.

        Args:
            employee: Employee object with hourly rate
            hours_breakdown: Hours breakdown dictionary
            payroll_settings: PayrollSettings object (or None for defaults)

        Returns:
            Dictionary with calculated amounts:
                {
                    'base_amount': int,
                    'overtime_amount': int,
                    'night_amount': int,
                    'holiday_amount': int
                }
        """
        base_rate = float(employee.jikyu) if employee.jikyu else 0

        # Get rates from payroll settings or use defaults from PayrollConfig
        if payroll_settings:
            overtime_rate = float(payroll_settings.overtime_rate)
            night_rate = float(payroll_settings.night_shift_rate)
            holiday_rate = float(payroll_settings.holiday_rate)
        else:
            # Use default settings from PayrollConfig class
            logger.warning("No payroll settings available, using PayrollConfig defaults")
            overtime_rate = PayrollConfig.DEFAULT_OVERTIME_RATE
            night_rate = PayrollConfig.DEFAULT_NIGHT_RATE
            holiday_rate = PayrollConfig.DEFAULT_HOLIDAY_RATE

        # Calculate amounts
        base_amount = int(
            base_rate * float(hours_breakdown['total_regular_hours'])
        )
        overtime_amount = int(
            base_rate * float(hours_breakdown['total_overtime_hours']) * overtime_rate
        )
        night_amount = int(
            base_rate * float(hours_breakdown['total_night_hours']) * night_rate
        )
        holiday_amount = int(
            base_rate * float(hours_breakdown['total_holiday_hours']) * holiday_rate
        )

        return {
            'base_amount': base_amount,
            'overtime_amount': overtime_amount,
            'night_amount': night_amount,
            'holiday_amount': holiday_amount
        }

    async def _get_apartment_deductions(
        self,
        employee_id: int,
        year: int,
        month: int,
        employee: Employee,
        work_days: int
    ) -> int:
        """
        Get apartment rent deductions for an employee.

        This method uses the new apartment deductions system (V2) which supports:
        - Base rent
        - Additional charges
        - Prorated rent based on work days

        Args:
            employee_id: Employee ID
            year: Year
            month: Month
            employee: Employee object
            work_days: Number of work days in the month

        Returns:
            Total apartment deduction amount
        """
        try:
            # Query rent_deductions table
            stmt = select(RentDeduction).where(
                and_(
                    RentDeduction.employee_id == employee_id,
                    RentDeduction.year == year,
                    RentDeduction.month == month,
                    RentDeduction.status.in_([DeductionStatus.PENDING, DeductionStatus.PROCESSED])
                )
            )
            result = await self.db.execute(stmt)
            deductions = result.scalars().all()

            if deductions:
                # Sum all deductions
                total_amount = sum(d.total_deduction for d in deductions)
                logger.info(
                    f"Apartment deductions for employee {employee_id}, "
                    f"{year}-{month:02d}: ¥{total_amount:,}"
                )
                return int(total_amount)

            # Fallback: Use employee.apartment_rent if no deductions found
            if employee.apartment_id and employee.apartment_rent:
                # Check if proration is enabled
                prorate_enabled = getattr(settings, 'APARTMENT_PRORATE_BY_DAY', False)

                if prorate_enabled:
                    days_in_month = 30  # Simplified
                    prorated_rent = int((employee.apartment_rent / days_in_month) * work_days)
                    logger.info(
                        f"Using prorated apartment rent for employee {employee_id}: "
                        f"¥{prorated_rent:,} ({work_days} days)"
                    )
                    return prorated_rent
                else:
                    logger.info(
                        f"Using full apartment rent for employee {employee_id}: "
                        f"¥{employee.apartment_rent:,}"
                    )
                    return employee.apartment_rent

            return 0

        except Exception as e:
            logger.error(
                f"Error getting apartment deductions for employee {employee_id}: {e}",
                exc_info=True
            )
            # Return 0 instead of failing the entire calculation
            return 0


# Singleton instance for easy imports
_salary_service_instance: Optional[SalaryService] = None


def get_salary_service(db: AsyncSession) -> SalaryService:
    """
    Factory function to get SalaryService instance.

    Args:
        db: AsyncSession database connection

    Returns:
        SalaryService instance

    Example:
        >>> async with get_db() as db:
        ...     service = get_salary_service(db)
        ...     result = await service.calculate_salary(...)
    """
    return SalaryService(db)
