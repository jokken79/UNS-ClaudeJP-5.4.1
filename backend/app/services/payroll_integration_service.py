"""
Payroll Integration Service
Connects timer card OCR data with payroll calculations
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, between
import logging

from app.models.models import TimerCard, Employee, Factory, YukyuRequest, RequestStatus
from app.schemas.payroll import EmployeePayrollResult

logger = logging.getLogger(__name__)


class PayrollIntegrationService:
    """
    Service that integrates timer card OCR data with payroll calculations.

    Handles the flow:
    Timer Card → Employee → Payroll Calculation
    """

    def __init__(self, db_session: Session):
        """Initialize with database session."""
        self.db = db_session

    def get_timer_cards_for_payroll(
        self,
        employee_id: int,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """
        Fetch timer card records for a specific employee and date range.

        Args:
            employee_id: ID of the employee
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            Dictionary with employee info and timer card records
        """
        try:
            # Convert string dates to date objects
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()

            # Get employee with factory info
            employee = (
                self.db.query(Employee)
                .filter(Employee.id == employee_id)
                .first()
            )

            if not employee:
                return {
                    'success': False,
                    'error': f'Employee with ID {employee_id} not found'
                }

            # Get timer cards for the date range (ONLY APPROVED)
            timer_cards = (
                self.db.query(TimerCard)
                .filter(
                    and_(
                        TimerCard.hakenmoto_id == employee.hakenmoto_id,
                        TimerCard.work_date >= start_dt,
                        TimerCard.work_date <= end_dt,
                        TimerCard.is_approved == True  # SECURITY: Only use approved timer cards for payroll
                    )
                )
                .order_by(TimerCard.work_date.asc())
                .all()
            )

            # Convert timer cards to dict format
            timer_records = []
            for card in timer_cards:
                timer_records.append({
                    'timer_card_id': card.id,
                    'work_date': card.work_date.isoformat(),
                    'clock_in': card.clock_in.strftime('%H:%M') if card.clock_in else None,
                    'clock_out': card.clock_out.strftime('%H:%M') if card.clock_out else None,
                    'break_minutes': card.break_minutes or 0,
                    'regular_hours': float(card.regular_hours) if card.regular_hours else 0.0,
                    'overtime_hours': float(card.overtime_hours) if card.overtime_hours else 0.0,
                    'night_hours': float(card.night_hours) if card.night_hours else 0.0,
                    'holiday_hours': float(card.holiday_hours) if card.holiday_hours else 0.0,
                    'is_approved': card.is_approved
                })

            # Get factory info if available
            factory_info = None
            if employee.factory:
                factory_info = {
                    'factory_id': employee.factory_id,
                    'company_name': employee.factory.company_name,
                    'plant_name': employee.factory.plant_name
                }

            return {
                'success': True,
                'employee': {
                    'employee_id': employee.id,
                    'hakenmoto_id': employee.hakenmoto_id,
                    'full_name_kanji': employee.full_name_kanji,
                    'full_name_kana': employee.full_name_kana,
                    'jikyu': employee.jikyu or 0,
                    'factory_info': factory_info,
                    'apartment_rent': employee.apartment_rent or 0,
                    'standard_hours_per_month': 160  # Default teiji (定時), puede venir de PayrollSettings
                },
                'timer_records': timer_records,
                'date_range': {
                    'start_date': start_date,
                    'end_date': end_date
                },
                'total_records': len(timer_records)
            }

        except ValueError as e:
            logger.error(f"Date parsing error: {e}")
            return {
                'success': False,
                'error': f'Invalid date format. Expected YYYY-MM-DD: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Error fetching timer cards: {e}", exc_info=True)
            return {
                'success': False,
                'error': f'Error fetching timer cards: {str(e)}'
            }

    def calculate_payroll_from_timer_cards(
        self,
        employee_id: int,
        start_date: str,
        end_date: str,
        payroll_settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate payroll for an employee using their timer card records.

        Args:
            employee_id: ID of the employee
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            payroll_settings: Optional payroll settings override

        Returns:
            Dictionary with payroll calculation result
        """
        try:
            # Get timer cards data
            timer_data = self.get_timer_cards_for_payroll(employee_id, start_date, end_date)

            if not timer_data['success']:
                return timer_data

            employee = timer_data['employee']
            timer_records = timer_data['timer_records']

            # Obtener yukyus aprobados para el período
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()

            yukyu_requests = self.db.query(YukyuRequest).filter(
                YukyuRequest.employee_id == employee_id,
                YukyuRequest.status == RequestStatus.APPROVED,
                YukyuRequest.start_date <= end_date_obj,
                YukyuRequest.end_date >= start_date_obj
            ).all()

            yukyu_days_approved = sum(float(r.days_requested) for r in yukyu_requests) if yukyu_requests else 0

            # Log para auditoría
            if yukyu_days_approved > 0:
                logger.info(
                    f"Employee {employee_id}: {yukyu_days_approved} approved yukyu days in period {start_date}-{end_date}"
                )

            if not timer_records:
                return {
                    'success': False,
                    'error': 'No timer card records found for the specified period'
                }

            # Calculate total hours from timer cards
            hours_breakdown = self._calculate_hours_from_timer_cards(timer_records)

            # Calculate payment amounts
            payment_amounts = self._calculate_payment_amounts(
                employee, hours_breakdown, payroll_settings
            )

            # Calculate deductions
            deductions = self._calculate_deductions(
                employee, payment_amounts['gross_amount']
            )

            # Build complete payroll result
            result = {
                'success': True,
                'employee_id': employee['employee_id'],
                'pay_period_start': start_date,
                'pay_period_end': end_date,
                'hours_breakdown': hours_breakdown,
                'rates': {
                    'base_rate': float(employee['jikyu']),
                    'overtime_rate': payroll_settings.get('overtime_rate', 1.25) if payroll_settings else 1.25,
                    'night_shift_rate': payroll_settings.get('night_shift_rate', 1.25) if payroll_settings else 1.25,
                    'holiday_rate': payroll_settings.get('holiday_rate', 1.35) if payroll_settings else 1.35,
                    'sunday_rate': payroll_settings.get('sunday_rate', 1.35) if payroll_settings else 1.35
                },
                'amounts': payment_amounts,
                'deductions_detail': deductions,
                'validation': {
                    'is_valid': True,
                    'errors': [],
                    'warnings': [
                        f"Payroll calculated from {len(timer_records)} timer card records"
                    ],
                    'validated_at': datetime.now().isoformat()
                },
                'calculated_at': datetime.now().isoformat()
            }

            return result

        except Exception as e:
            logger.error(f"Error calculating payroll: {e}", exc_info=True)
            return {
                'success': False,
                'error': f'Error calculating payroll: {str(e)}'
            }

    def _calculate_hours_from_timer_cards(self, timer_records: List[Dict]) -> Dict[str, Any]:
        """Calculate total hours from timer card records."""
        total_regular = sum(r['regular_hours'] for r in timer_records)
        total_overtime = sum(r['overtime_hours'] for r in timer_records)
        total_night = sum(r['night_hours'] for r in timer_records)
        total_holiday = sum(r['holiday_hours'] for r in timer_records)

        # Get unique work days
        work_days = len(set(r['work_date'] for r in timer_records))

        total_hours = total_regular + total_overtime + total_night + total_holiday

        return {
            'regular_hours': round(total_regular, 2),
            'overtime_hours': round(total_overtime, 2),
            'night_shift_hours': round(total_night, 2),
            'holiday_hours': round(total_holiday, 2),
            'total_hours': round(total_hours, 2),
            'work_days': work_days
        }

    def _calculate_payment_amounts(
        self,
        employee: Dict,
        hours_breakdown: Dict,
        payroll_settings: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Calculate payment amounts based on hours and rates."""
        base_rate = float(employee['jikyu'])
        overtime_rate = payroll_settings.get('overtime_rate', 1.25) if payroll_settings else 1.25
        night_rate = payroll_settings.get('night_shift_rate', 1.25) if payroll_settings else 1.25
        holiday_rate = payroll_settings.get('holiday_rate', 1.35) if payroll_settings else 1.35

        # Calculate base amount (regular hours at base rate)
        base_amount = int(hours_breakdown['regular_hours'] * base_rate)

        # Calculate overtime amount (overtime hours at 1.25x)
        overtime_amount = int(hours_breakdown['overtime_hours'] * base_rate * overtime_rate)

        # Calculate night shift amount (night hours at 1.25x)
        night_amount = int(hours_breakdown['night_shift_hours'] * base_rate * night_rate)

        # Calculate holiday amount (holiday hours at 1.35x)
        holiday_amount = int(hours_breakdown['holiday_hours'] * base_rate * holiday_rate)

        # Total gross amount
        gross_amount = base_amount + overtime_amount + night_amount + holiday_amount

        # For now, no additional deductions in amounts
        # (Deductions are calculated separately)
        total_deductions = 0
        net_amount = gross_amount - total_deductions

        return {
            'base_amount': base_amount,
            'overtime_amount': overtime_amount,
            'night_shift_amount': night_amount,
            'holiday_amount': holiday_amount,
            'sunday_amount': 0,  # Not implemented yet
            'gross_amount': gross_amount,
            'total_deductions': total_deductions,
            'net_amount': net_amount
        }

    def _calculate_deductions(
        self,
        employee: Dict,
        gross_amount: float
    ) -> Dict[str, Any]:
        """Calculate deductions (apartment rent, insurance, taxes, etc.)."""
        # Apartment rent deduction
        # Solo deducir si es 社宅 (corporate housing)
        is_corporate_housing = employee.get('is_corporate_housing', False)
        if is_corporate_housing:
            apartment_deduction = employee.get('apartment_rent', 0)
        else:
            apartment_deduction = 0

        # Calculate social insurance (approximate)
        # This would be calculated based on actual rates in a real system
        health_insurance = int(gross_amount * 0.05)  # 5% approximation
        pension = int(gross_amount * 0.09)  # 9% approximation
        employment_insurance = int(gross_amount * 0.006)  # 0.6% approximation

        # Calculate income tax (approximate)
        # This is simplified; real calculation would be more complex
        income_tax = int(gross_amount * 0.05)  # 5% approximation

        # Resident tax (approximate)
        resident_tax = int(gross_amount * 0.10)  # 10% approximation

        # Total deductions
        total_deductions = (
            apartment_deduction +
            health_insurance +
            pension +
            employment_insurance +
            income_tax +
            resident_tax
        )

        return {
            'income_tax': income_tax,
            'resident_tax': resident_tax,
            'health_insurance': health_insurance,
            'pension': pension,
            'employment_insurance': employment_insurance,
            'apartment': apartment_deduction,
            'other': 0
        }

    def get_unprocessed_timer_cards(
        self,
        employee_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get timer cards that haven't been used for payroll calculation yet.

        Args:
            employee_id: Optional employee filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum number of records to return

        Returns:
            Dictionary with unprocessed timer card records
        """
        try:
            query = self.db.query(TimerCard).filter(TimerCard.is_approved == True)

            if employee_id:
                # Convert employee.id to hakenmoto_id for filtering
                employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
                if employee:
                    query = query.filter(TimerCard.hakenmoto_id == employee.hakenmoto_id)
                else:
                    # If employee not found, return empty result
                    return {'success': True, 'records': [], 'total': 0}

            if start_date:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(TimerCard.work_date >= start_dt)

            if end_date:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(TimerCard.work_date <= end_dt)

            timer_cards = query.order_by(TimerCard.work_date.desc()).limit(limit).all()

            # Group by employee hakenmoto_id
            grouped_records = {}
            for card in timer_cards:
                hakenmoto_id = card.hakenmoto_id
                if hakenmoto_id not in grouped_records:
                    grouped_records[hakenmoto_id] = {
                        'hakenmoto_id': hakenmoto_id,
                        'employee_name': card.employee.full_name_kanji if card.employee else 'Unknown',
                        'timer_cards': []
                    }

                grouped_records[hakenmoto_id]['timer_cards'].append({
                    'id': card.id,
                    'work_date': card.work_date.isoformat(),
                    'clock_in': card.clock_in.strftime('%H:%M') if card.clock_in else None,
                    'clock_out': card.clock_out.strftime('%H:%M') if card.clock_out else None,
                    'break_minutes': card.break_minutes or 0,
                    'regular_hours': float(card.regular_hours) if card.regular_hours else 0.0,
                    'overtime_hours': float(card.overtime_hours) if card.overtime_hours else 0.0,
                    'is_approved': card.is_approved
                })

            return {
                'success': True,
                'total_employees': len(grouped_records),
                'total_records': len(timer_cards),
                'employees': list(grouped_records.values())
            }

        except Exception as e:
            logger.error(f"Error fetching unprocessed timer cards: {e}", exc_info=True)
            return {
                'success': False,
                'error': f'Error fetching unprocessed timer cards: {str(e)}'
            }
