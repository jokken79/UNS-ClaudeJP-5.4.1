"""
Yukyu Service (有給休暇サービス)
================================

Service for managing paid vacation (yukyu) following Japanese labor law.

Features:
- Automatic calculation based on employment duration (6mo=10d, 18mo=11d, etc.)
- LIFO deduction (newest yukyus used first)
- Automatic expiration after 2 years (時効 - jikou)
- Request workflow: TANTOSHA creates → KEIRI approves
- Support for hannichi (半休 - half day = 0.5)
- Alerts for 5-day minimum usage requirement

Author: UNS-ClaudeJP System
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
from dateutil.relativedelta import relativedelta

from app.models.models import (
    YukyuBalance,
    YukyuRequest,
    YukyuUsageDetail,
    Employee,
    User,
    Factory,
    YukyuStatus,
    RequestStatus,
    RequestType,
    UserRole,
)
from app.schemas.yukyu import (
    YukyuBalanceCreate,
    YukyuBalanceUpdate,
    YukyuBalanceResponse,
    YukyuBalanceSummary,
    YukyuRequestCreate,
    YukyuRequestUpdate,
    YukyuRequestApprove,
    YukyuRequestReject,
    YukyuRequestResponse,
    YukyuCalculationRequest,
    YukyuCalculationResponse,
    YukyuReport,
    YukyuAlert,
    EmployeeByFactoryResponse,
)


class YukyuService:
    """Service for yukyu (paid vacation) operations"""

    def __init__(self, db: Session):
        self.db = db

    # -------------------------------------------------------------------------
    # YUKYU CALCULATION (Japanese Labor Law)
    # -------------------------------------------------------------------------

    def calculate_yukyu_entitlement(self, hire_date: date, current_date: date = None) -> Tuple[int, int]:
        """
        Calculate yukyu entitlement based on Japanese labor law.

        Law reference:
        - 6 months:   10 days
        - 1.5 years:  11 days
        - 2.5 years:  12 days
        - 3.5 years:  14 days
        - 4.5 years:  16 days
        - 5.5 years:  18 days
        - 6.5+ years: 20 days (maximum)

        Args:
            hire_date: Employee hire date (入社日)
            current_date: Date to calculate from (defaults to today)

        Returns:
            Tuple[months_worked, days_entitled]
        """
        if current_date is None:
            current_date = date.today()

        # Calculate months since hire
        delta = relativedelta(current_date, hire_date)
        months_worked = delta.years * 12 + delta.months

        # Determine yukyu days based on months
        if months_worked < 6:
            return months_worked, 0
        elif months_worked < 18:
            return months_worked, 10
        elif months_worked < 30:
            return months_worked, 11
        elif months_worked < 42:
            return months_worked, 12
        elif months_worked < 54:
            return months_worked, 14
        elif months_worked < 66:
            return months_worked, 16
        elif months_worked < 78:
            return months_worked, 18
        else:
            return months_worked, 20

    def get_assignment_date(self, hire_date: date, months: int) -> date:
        """
        Get the date when yukyu should be assigned.

        Args:
            hire_date: Employee hire date
            months: Months since hire (6, 18, 30, 42, etc.)

        Returns:
            Assignment date
        """
        return hire_date + relativedelta(months=months)

    async def calculate_and_create_balances(
        self,
        employee_id: int,
        calculation_date: date = None
    ) -> YukyuCalculationResponse:
        """
        Calculate and create yukyu balances for an employee.

        This creates all missing balance records from hire date to current date.
        Called when:
        - Employee is first created
        - Monthly cron job to assign new yukyus
        - Manual recalculation by admin

        Args:
            employee_id: Employee ID
            calculation_date: Date to calculate up to (defaults to today)

        Returns:
            Calculation result with number of balances created

        Raises:
            HTTPException: If employee not found
        """
        from fastapi import HTTPException

        if calculation_date is None:
            calculation_date = date.today()

        # Get employee
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")

        if not employee.hire_date:
            raise HTTPException(status_code=400, detail="Employee has no hire date")

        # Calculate entitlement
        months_worked, _ = self.calculate_yukyu_entitlement(employee.hire_date, calculation_date)

        # Get existing balances
        existing_balances = self.db.query(YukyuBalance).filter(
            YukyuBalance.employee_id == employee_id
        ).all()
        existing_months = {b.months_worked for b in existing_balances}

        # Create missing balances
        milestones = [6, 18, 30, 42, 54, 66, 78, 90, 102, 114, 126]  # Up to ~10 years
        balances_created = 0

        for milestone in milestones:
            if milestone > months_worked:
                break

            if milestone in existing_months:
                continue

            # Calculate days for this milestone
            _, days = self.calculate_yukyu_entitlement(employee.hire_date,
                                                        self.get_assignment_date(employee.hire_date, milestone))

            # Get carryover from previous balance
            carryover = 0
            if milestone > 6:
                prev_balance = self.db.query(YukyuBalance).filter(
                    and_(
                        YukyuBalance.employee_id == employee_id,
                        YukyuBalance.months_worked == milestone - 12
                    )
                ).first()

                if prev_balance:
                    carryover = prev_balance.days_remaining

            # Create balance
            assigned_date = self.get_assignment_date(employee.hire_date, milestone)
            expires_on = assigned_date + relativedelta(years=2)
            fiscal_year = assigned_date.year

            balance = YukyuBalance(
                employee_id=employee_id,
                fiscal_year=fiscal_year,
                assigned_date=assigned_date,
                months_worked=milestone,
                days_assigned=days,
                days_carried_over=carryover,
                days_total=days + carryover,
                days_used=0,
                days_remaining=days + carryover,
                days_expired=0,
                days_available=days + carryover,
                expires_on=expires_on,
                status=YukyuStatus.ACTIVE,
            )

            self.db.add(balance)
            balances_created += 1

        self.db.commit()

        # Get total available
        total_available = self.db.query(
            func.sum(YukyuBalance.days_available)
        ).filter(
            and_(
                YukyuBalance.employee_id == employee_id,
                YukyuBalance.status == YukyuStatus.ACTIVE
            )
        ).scalar() or 0

        return YukyuCalculationResponse(
            employee_id=employee_id,
            employee_name=employee.full_name_kanji,
            hire_date=employee.hire_date,
            months_since_hire=months_worked,
            yukyus_created=balances_created,
            total_available_days=total_available,
            message=f"Created {balances_created} yukyu balance(s). Total available: {total_available} days."
        )

    # -------------------------------------------------------------------------
    # YUKYU BALANCE QUERIES
    # -------------------------------------------------------------------------

    async def get_employee_yukyu_summary(self, employee_id: int) -> YukyuBalanceSummary:
        """
        Get complete yukyu summary for an employee.

        Args:
            employee_id: Employee ID

        Returns:
            Complete summary with all balances and alerts

        Raises:
            HTTPException: If employee not found
        """
        from fastapi import HTTPException

        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")

        # Get all active balances
        balances = self.db.query(YukyuBalance).filter(
            and_(
                YukyuBalance.employee_id == employee_id,
                YukyuBalance.status == YukyuStatus.ACTIVE
            )
        ).order_by(YukyuBalance.assigned_date.desc()).all()

        # Calculate totals
        total_available = sum(b.days_available for b in balances)
        total_used = sum(b.days_used for b in balances)
        total_expired = sum(b.days_expired for b in balances)

        # Find oldest expiration date
        oldest_expiration = None
        if balances:
            oldest_expiration = min(b.expires_on for b in balances)

        # Check if needs to use 5 days minimum
        # TODO: Implement year-based tracking for 5-day minimum
        needs_5_days = False

        return YukyuBalanceSummary(
            employee_id=employee_id,
            employee_name=employee.full_name_kanji,
            total_available=total_available,
            total_used=total_used,
            total_expired=total_expired,
            balances=[YukyuBalanceResponse.model_validate(b) for b in balances],
            oldest_expiration_date=oldest_expiration,
            needs_to_use_minimum_5_days=needs_5_days
        )

    async def get_employees_by_factory(self, factory_id: str) -> List[EmployeeByFactoryResponse]:
        """
        Get all employees in a factory with their yukyu availability.

        Used by TANTOSHA to see employees they can request yukyus for.

        Args:
            factory_id: Factory ID (派遣先ID)

        Returns:
            List of employees with yukyu info
        """
        employees = self.db.query(Employee).filter(
            Employee.factory_id == factory_id
        ).all()

        result = []
        for emp in employees:
            # Calculate total available yukyus
            total_available = self.db.query(
                func.sum(YukyuBalance.days_available)
            ).filter(
                and_(
                    YukyuBalance.employee_id == emp.id,
                    YukyuBalance.status == YukyuStatus.ACTIVE
                )
            ).scalar() or 0

            result.append(EmployeeByFactoryResponse(
                id=emp.id,
                rirekisho_id=emp.rirekisho_id,
                full_name_kanji=emp.full_name_kanji,
                full_name_kana=emp.full_name_kana,
                factory_id=emp.factory_id,
                factory_name=emp.factory.name if emp.factory else None,
                hire_date=emp.hire_date,
                yukyu_available=total_available
            ))

        return result

    # -------------------------------------------------------------------------
    # YUKYU REQUESTS (TANTOSHA → KEIRI workflow)
    # -------------------------------------------------------------------------

    async def create_request(
        self,
        request_data: YukyuRequestCreate,
        user_id: int
    ) -> YukyuRequestResponse:
        """
        Create yukyu request (by TANTOSHA).

        Workflow:
        1. Validate employee exists
        2. Calculate days requested (can be 0.5 for hannichi)
        3. Check employee has enough yukyus available
        4. Create request with status=PENDING
        5. Return request details

        Args:
            request_data: Request data
            user_id: ID of user creating request (TANTOSHA)

        Returns:
            Created request

        Raises:
            HTTPException: If validations fail
        """
        from fastapi import HTTPException

        # Validate employee
        employee = self.db.query(Employee).filter(
            Employee.id == request_data.employee_id
        ).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")

        # Calculate total available yukyus
        total_available = self.db.query(
            func.sum(YukyuBalance.days_available)
        ).filter(
            and_(
                YukyuBalance.employee_id == request_data.employee_id,
                YukyuBalance.status == YukyuStatus.ACTIVE
            )
        ).scalar() or 0

        # Validate enough yukyus
        if request_data.days_requested > total_available:
            raise HTTPException(
                status_code=400,
                detail=f"Employee only has {total_available} yukyu days available, but {request_data.days_requested} were requested"
            )

        # Create request
        yukyu_request = YukyuRequest(
            employee_id=request_data.employee_id,
            requested_by_user_id=user_id,
            factory_id=request_data.factory_id,
            request_type=RequestType(request_data.request_type),
            start_date=request_data.start_date,
            end_date=request_data.end_date,
            days_requested=request_data.days_requested,
            yukyu_available_at_request=total_available,
            status=RequestStatus.PENDING,
            notes=request_data.notes
        )

        self.db.add(yukyu_request)
        self.db.commit()
        self.db.refresh(yukyu_request)

        return await self._build_request_response(yukyu_request)

    async def approve_request(
        self,
        request_id: int,
        approval_data: YukyuRequestApprove,
        user_id: int
    ) -> YukyuRequestResponse:
        """
        Approve yukyu request (by KEIRI).

        Workflow:
        1. Get request and validate status is PENDING
        2. Deduct yukyus using LIFO (newest first)
        3. Create usage_details records
        4. Update request status to APPROVED
        5. Return updated request

        Args:
            request_id: Request ID
            approval_data: Approval data
            user_id: ID of user approving (KEIRI)

        Returns:
            Approved request

        Raises:
            HTTPException: If request not found or already processed
        """
        from fastapi import HTTPException

        # Get request
        request = self.db.query(YukyuRequest).filter(
            YukyuRequest.id == request_id
        ).first()
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")

        if request.status != RequestStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail=f"Request is already {request.status.value}"
            )

        # Deduct yukyus using LIFO
        await self._deduct_yukyus_lifo(
            employee_id=request.employee_id,
            days_to_deduct=float(request.days_requested),
            request_id=request.id,
            start_date=request.start_date,
            end_date=request.end_date
        )

        # Update request
        request.status = RequestStatus.APPROVED
        request.approved_by_user_id = user_id
        request.approval_date = datetime.now()
        if approval_data.notes:
            request.notes = (request.notes or "") + f"\n[Approved] {approval_data.notes}"

        self.db.commit()
        self.db.refresh(request)

        return await self._build_request_response(request)

    async def reject_request(
        self,
        request_id: int,
        rejection_data: YukyuRequestReject,
        user_id: int
    ) -> YukyuRequestResponse:
        """
        Reject yukyu request (by KEIRI).

        Args:
            request_id: Request ID
            rejection_data: Rejection data with reason
            user_id: ID of user rejecting (KEIRI)

        Returns:
            Rejected request

        Raises:
            HTTPException: If request not found or already processed
        """
        from fastapi import HTTPException

        # Get request
        request = self.db.query(YukyuRequest).filter(
            YukyuRequest.id == request_id
        ).first()
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")

        if request.status != RequestStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail=f"Request is already {request.status.value}"
            )

        # Update request
        request.status = RequestStatus.REJECTED
        request.approved_by_user_id = user_id
        request.approval_date = datetime.now()
        request.rejection_reason = rejection_data.rejection_reason

        self.db.commit()
        self.db.refresh(request)

        return await self._build_request_response(request)

    async def list_requests(
        self,
        user: User,
        factory_id: Optional[str] = None,
        status: Optional[str] = None,
        employee_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[YukyuRequestResponse]:
        """
        List yukyu requests with filtering based on user role.

        TANTOSHA: Can only see requests for their factory
        KEIRI/ADMIN: Can see all requests

        Args:
            user: Current user
            factory_id: Filter by factory
            status: Filter by status (pending, approved, rejected)
            employee_id: Filter by employee
            limit: Max results
            offset: Pagination offset

        Returns:
            List of requests
        """
        query = self.db.query(YukyuRequest)

        # Role-based filtering
        if user.role == UserRole.TANTOSHA:
            # TANTOSHA can only see their factory's requests
            if not factory_id:
                # Get user's factory from their employee record or config
                # For now, require factory_id
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=400,
                    detail="TANTOSHA must specify factory_id"
                )
            query = query.filter(YukyuRequest.factory_id == factory_id)
        elif factory_id:
            # KEIRI/ADMIN can optionally filter by factory
            query = query.filter(YukyuRequest.factory_id == factory_id)

        # Additional filters
        if status:
            query = query.filter(YukyuRequest.status == RequestStatus(status))
        if employee_id:
            query = query.filter(YukyuRequest.employee_id == employee_id)

        # Order and paginate
        requests = query.order_by(
            YukyuRequest.request_date.desc()
        ).limit(limit).offset(offset).all()

        return [await self._build_request_response(r) for r in requests]

    # -------------------------------------------------------------------------
    # LIFO DEDUCTION LOGIC
    # -------------------------------------------------------------------------

    async def _deduct_yukyus_lifo(
        self,
        employee_id: int,
        days_to_deduct: float,
        request_id: int,
        start_date: date,
        end_date: date
    ) -> None:
        """
        Deduct yukyus using LIFO (Last In, First Out).

        Newest yukyus are used first. This is the user's requirement.

        Args:
            employee_id: Employee ID
            days_to_deduct: Days to deduct (can be 0.5 for hannichi)
            request_id: Request ID for tracking
            start_date: Start date of yukyu
            end_date: End date of yukyu

        Raises:
            HTTPException: If not enough yukyus available
        """
        from fastapi import HTTPException

        # Get active balances, newest first (LIFO)
        balances = self.db.query(YukyuBalance).filter(
            and_(
                YukyuBalance.employee_id == employee_id,
                YukyuBalance.status == YukyuStatus.ACTIVE,
                YukyuBalance.days_available > 0
            )
        ).order_by(YukyuBalance.assigned_date.desc()).all()

        if not balances:
            raise HTTPException(
                status_code=400,
                detail="No yukyu balances available"
            )

        remaining_to_deduct = Decimal(str(days_to_deduct))

        # Generate dates for usage tracking
        usage_dates = []
        current = start_date
        while current <= end_date:
            usage_dates.append(current)
            current += timedelta(days=1)

        # Deduct from newest balances first
        for balance in balances:
            if remaining_to_deduct <= 0:
                break

            available = Decimal(str(balance.days_available))
            to_deduct_from_this = min(remaining_to_deduct, available)

            # Update balance
            balance.days_used += int(to_deduct_from_this) if to_deduct_from_this == int(to_deduct_from_this) else float(to_deduct_from_this)
            balance.days_remaining = balance.days_total - balance.days_used
            balance.days_available = balance.days_remaining - balance.days_expired

            # Create usage details
            days_per_date = to_deduct_from_this / len(usage_dates) if usage_dates else to_deduct_from_this
            for usage_date in usage_dates:
                detail = YukyuUsageDetail(
                    request_id=request_id,
                    balance_id=balance.id,
                    usage_date=usage_date,
                    days_deducted=days_per_date
                )
                self.db.add(detail)

            remaining_to_deduct -= to_deduct_from_this

        if remaining_to_deduct > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough yukyus available. Missing {remaining_to_deduct} days."
            )

        self.db.commit()

    # -------------------------------------------------------------------------
    # EXPIRATION & MAINTENANCE
    # -------------------------------------------------------------------------

    async def expire_old_yukyus(self) -> int:
        """
        Expire yukyus that are older than 2 years.

        Called by cron job daily.

        Returns:
            Number of balances expired
        """
        today = date.today()

        # Find balances that should be expired
        balances_to_expire = self.db.query(YukyuBalance).filter(
            and_(
                YukyuBalance.status == YukyuStatus.ACTIVE,
                YukyuBalance.expires_on <= today
            )
        ).all()

        for balance in balances_to_expire:
            balance.status = YukyuStatus.EXPIRED
            balance.days_expired = balance.days_remaining
            balance.days_available = 0

        self.db.commit()
        return len(balances_to_expire)

    # -------------------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------------------

    async def _build_request_response(self, request: YukyuRequest) -> YukyuRequestResponse:
        """Build full request response with related data."""
        employee = self.db.query(Employee).filter(Employee.id == request.employee_id).first()
        requested_by = self.db.query(User).filter(User.id == request.requested_by_user_id).first()
        approved_by = None
        if request.approved_by_user_id:
            approved_by = self.db.query(User).filter(User.id == request.approved_by_user_id).first()
        factory = None
        if request.factory_id:
            factory = self.db.query(Factory).filter(Factory.id == request.factory_id).first()

        return YukyuRequestResponse(
            id=request.id,
            employee_id=request.employee_id,
            requested_by_user_id=request.requested_by_user_id,
            factory_id=request.factory_id,
            request_type=request.request_type.value,
            start_date=request.start_date,
            end_date=request.end_date,
            days_requested=request.days_requested,
            yukyu_available_at_request=request.yukyu_available_at_request,
            request_date=request.request_date,
            status=request.status.value,
            approved_by_user_id=request.approved_by_user_id,
            approval_date=request.approval_date,
            rejection_reason=request.rejection_reason,
            notes=request.notes,
            created_at=request.created_at,
            updated_at=request.updated_at,
            employee_name=employee.full_name_kanji if employee else None,
            factory_name=factory.name if factory else None,
            requested_by_name=requested_by.full_name if requested_by else None,
            approved_by_name=approved_by.full_name if approved_by else None,
        )
