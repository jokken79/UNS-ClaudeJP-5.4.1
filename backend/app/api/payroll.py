"""
Payroll API Router - FastAPI endpoints
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.core.database import get_db
from app.services.payroll_service import PayrollService
from app.services.payroll_integration_service import PayrollIntegrationService
from app.models.payroll_models import PayrollRun as PayrollRunModel, EmployeePayroll
from app.models.models import Employee
from app.schemas.payroll import (
    PayrollRunCreate,
    PayrollRun,
    PayrollRunSummary,
    EmployeePayrollCreate,
    EmployeePayrollResult,
    BulkPayrollRequest,
    BulkPayrollResult,
    PayslipRequest,
    PayslipInfo,
    PayrollSettings,
    PayrollSettingsCreate,
    PayrollSettingsUpdate,
    PayrollApprovalRequest,
    PayrollApprovalResponse,
    PayrollSummary,
    SuccessResponse,
    ErrorResponse,
    HoursBreakdown,
    Rates,
    Amounts,
    DeductionsDetail,
    ValidationResult,
)

router = APIRouter(prefix="/api/payroll", tags=["payroll"])

# Dependency to get PayrollService
def get_payroll_service(db: Session = Depends(get_db)) -> PayrollService:
    return PayrollService(db_session=db)

# Dependency to get PayrollIntegrationService
def get_payroll_integration_service(db: Session = Depends(get_db)) -> PayrollIntegrationService:
    return PayrollIntegrationService(db_session=db)


# ============================================================================
# Payroll Runs Endpoints
# ============================================================================

@router.post(
    "/runs",
    response_model=PayrollRun,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new payroll run",
    description="Creates a new payroll run for a specific pay period"
)
def create_payroll_run(
    payroll_data: PayrollRunCreate,
    service: PayrollService = Depends(get_payroll_service),
    db: Session = Depends(get_db)
):
    """Create a new payroll run.

    Args:
        payroll_data: Payroll run data with pay period dates
        service: Payroll service instance
        db: Database session

    Returns:
        Created payroll run

    Raises:
        HTTPException: If creation fails
    """
    try:
        # Create PayrollRun object
        payroll_run = PayrollRunModel(
            pay_period_start=payroll_data.pay_period_start.date(),
            pay_period_end=payroll_data.pay_period_end.date(),
            status="draft",
            total_employees=0,
            total_gross_amount=0,
            total_deductions=0,
            total_net_amount=0,
            created_by=payroll_data.created_by
        )

        # Add to database
        db.add(payroll_run)
        db.commit()
        db.refresh(payroll_run)

        # Convert to schema with proper type conversions
        return PayrollRun(
            id=payroll_run.id,
            pay_period_start=datetime.combine(payroll_run.pay_period_start, datetime.min.time()),
            pay_period_end=datetime.combine(payroll_run.pay_period_end, datetime.min.time()),
            status=payroll_run.status,
            total_employees=payroll_run.total_employees,
            total_gross_amount=float(payroll_run.total_gross_amount),
            total_deductions=float(payroll_run.total_deductions),
            total_net_amount=float(payroll_run.total_net_amount),
            created_by=payroll_run.created_by,
            created_at=payroll_run.created_at,
            updated_at=payroll_run.updated_at
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating payroll run: {str(e)}"
        )


@router.get(
    "/runs",
    response_model=List[PayrollRunSummary],
    summary="Get all payroll runs",
    description="Retrieves a list of all payroll runs with pagination"
)
def get_payroll_runs(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    service: PayrollService = Depends(get_payroll_service),
    db: Session = Depends(get_db)
):
    """Get all payroll runs with optional filtering and pagination.

    Args:
        skip: Number of items to skip
        limit: Maximum number of items to return
        status_filter: Optional status filter
        service: Payroll service instance
        db: Database session

    Returns:
        List of payroll run summaries

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        # Build query
        query = db.query(PayrollRunModel)

        # Apply status filter if provided
        if status_filter:
            query = query.filter(PayrollRunModel.status == status_filter)

        # Apply pagination and ordering
        payroll_runs = query.order_by(PayrollRunModel.created_at.desc()).offset(skip).limit(limit).all()

        # Convert to PayrollRunSummary schemas
        return [
            PayrollRunSummary(
                id=run.id,
                pay_period_start=datetime.combine(run.pay_period_start, datetime.min.time()),
                pay_period_end=datetime.combine(run.pay_period_end, datetime.min.time()),
                status=run.status,
                total_employees=run.total_employees,
                total_gross_amount=float(run.total_gross_amount),
                total_net_amount=float(run.total_net_amount),
                created_at=run.created_at
            )
            for run in payroll_runs
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving payroll runs: {str(e)}"
        )


@router.get(
    "/runs/{payroll_run_id}",
    response_model=PayrollRun,
    summary="Get payroll run details",
    description="Retrieves detailed information about a specific payroll run"
)
def get_payroll_run(
    payroll_run_id: int,
    service: PayrollService = Depends(get_payroll_service),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific payroll run.

    Args:
        payroll_run_id: ID of the payroll run
        service: Payroll service instance
        db: Database session

    Returns:
        Payroll run details

    Raises:
        HTTPException: If payroll run not found or retrieval fails
    """
    try:
        # Query PayrollRun by ID
        payroll_run = db.query(PayrollRunModel).filter(PayrollRunModel.id == payroll_run_id).first()

        if not payroll_run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payroll run {payroll_run_id} not found"
            )

        # Convert to schema with proper type conversions
        return PayrollRun(
            id=payroll_run.id,
            pay_period_start=datetime.combine(payroll_run.pay_period_start, datetime.min.time()),
            pay_period_end=datetime.combine(payroll_run.pay_period_end, datetime.min.time()),
            status=payroll_run.status,
            total_employees=payroll_run.total_employees,
            total_gross_amount=float(payroll_run.total_gross_amount),
            total_deductions=float(payroll_run.total_deductions),
            total_net_amount=float(payroll_run.total_net_amount),
            created_by=payroll_run.created_by,
            created_at=payroll_run.created_at,
            updated_at=payroll_run.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving payroll run: {str(e)}"
        )


@router.post(
    "/runs/{payroll_run_id}/calculate",
    response_model=BulkPayrollResult,
    summary="Calculate payroll for all employees",
    description="Calculates payroll for all employees in a payroll run"
)
def calculate_payroll_run(
    payroll_run_id: int,
    request: BulkPayrollRequest,
    service: PayrollService = Depends(get_payroll_service)
):
    """Calculate payroll for all employees in a payroll run.

    Args:
        payroll_run_id: ID of the payroll run
        request: Bulk payroll request with employee data
        service: Payroll service instance

    Returns:
        Bulk payroll calculation results

    Raises:
        HTTPException: If calculation fails
    """
    try:
        result = service.calculate_bulk_payroll(
            employees_data=request.employees_data,
            payroll_run_id=payroll_run_id
        )

        if not result['total_employees']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No employee data provided"
            )

        return BulkPayrollResult(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating payroll: {str(e)}"
        )


@router.get(
    "/runs/{payroll_run_id}/employees",
    response_model=List[EmployeePayrollResult],
    summary="Get employees in payroll run",
    description="Retrieves all employees and their payroll calculations for a run"
)
def get_payroll_run_employees(
    payroll_run_id: int,
    service: PayrollService = Depends(get_payroll_service),
    db: Session = Depends(get_db)
):
    """Get all employees and their payroll calculations for a payroll run.

    Args:
        payroll_run_id: ID of the payroll run
        service: Payroll service instance
        db: Database session

    Returns:
        List of employee payroll results

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        # Query EmployeePayroll with join to Employee
        employee_payrolls = db.query(EmployeePayroll, Employee).join(
            Employee, Employee.id == EmployeePayroll.employee_id
        ).filter(
            EmployeePayroll.payroll_run_id == payroll_run_id
        ).all()

        # Convert to EmployeePayrollResult schemas
        results = []
        for emp_payroll, employee in employee_payrolls:
            # Build hours breakdown
            hours_breakdown = HoursBreakdown(
                regular_hours=float(emp_payroll.regular_hours),
                overtime_hours=float(emp_payroll.overtime_hours),
                night_shift_hours=float(emp_payroll.night_shift_hours),
                holiday_hours=float(emp_payroll.holiday_hours),
                sunday_hours=float(emp_payroll.sunday_hours),
                total_hours=float(emp_payroll.regular_hours + emp_payroll.overtime_hours +
                                emp_payroll.night_shift_hours + emp_payroll.holiday_hours +
                                emp_payroll.sunday_hours),
                work_days=0  # Not stored in current schema
            )

            # Build rates
            rates = Rates(
                base_rate=float(emp_payroll.base_rate),
                overtime_rate=float(emp_payroll.overtime_rate),
                night_shift_rate=float(emp_payroll.night_shift_rate),
                holiday_rate=float(emp_payroll.holiday_rate),
                sunday_rate=float(emp_payroll.holiday_rate)  # Using holiday_rate as proxy
            )

            # Build amounts
            amounts = Amounts(
                base_amount=float(emp_payroll.base_amount),
                overtime_amount=float(emp_payroll.overtime_amount),
                night_shift_amount=float(emp_payroll.night_shift_amount),
                holiday_amount=float(emp_payroll.holiday_amount),
                sunday_amount=0,  # Not stored separately
                gross_amount=float(emp_payroll.gross_amount),
                total_deductions=float(emp_payroll.total_deductions),
                net_amount=float(emp_payroll.net_amount)
            )

            # Build deductions detail
            deductions_detail = DeductionsDetail(
                income_tax=float(emp_payroll.income_tax),
                resident_tax=float(emp_payroll.resident_tax),
                health_insurance=float(emp_payroll.health_insurance),
                pension=float(emp_payroll.pension),
                employment_insurance=float(emp_payroll.employment_insurance),
                apartment=0,  # Not stored in current schema
                other=0
            )

            # Build validation result
            validation = ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                validated_at=datetime.now()
            )

            # Create result
            results.append(EmployeePayrollResult(
                success=True,
                employee_id=emp_payroll.employee_id,
                payroll_run_id=emp_payroll.payroll_run_id,
                pay_period_start=emp_payroll.pay_period_start.isoformat(),
                pay_period_end=emp_payroll.pay_period_end.isoformat(),
                hours_breakdown=hours_breakdown,
                rates=rates,
                amounts=amounts,
                deductions_detail=deductions_detail,
                validation=validation,
                calculated_at=emp_payroll.created_at
            ))

        return results

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving employees: {str(e)}"
        )


@router.post(
    "/runs/{payroll_run_id}/approve",
    response_model=PayrollApprovalResponse,
    summary="Approve a payroll run",
    description="Approves a payroll run for payment"
)
def approve_payroll_run(
    payroll_run_id: int,
    request: PayrollApprovalRequest,
    service: PayrollService = Depends(get_payroll_service),
    db: Session = Depends(get_db)
):
    """Approve a payroll run for payment.

    Args:
        payroll_run_id: ID of the payroll run
        request: Approval request with approver info
        service: Payroll service instance
        db: Database session

    Returns:
        Approval result

    Raises:
        HTTPException: If approval fails
    """
    try:
        # Query PayrollRun by ID
        payroll_run = db.query(PayrollRunModel).filter(PayrollRunModel.id == payroll_run_id).first()

        if not payroll_run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payroll run {payroll_run_id} not found"
            )

        # Validate status - can only approve draft or calculated runs
        if payroll_run.status not in ['draft', 'calculated']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot approve payroll run with status '{payroll_run.status}'. Must be 'draft' or 'calculated'."
            )

        # Update status to approved
        payroll_run.status = 'approved'
        payroll_run.updated_at = datetime.now()

        # Commit changes
        db.commit()
        db.refresh(payroll_run)

        # Return approval response
        return PayrollApprovalResponse(
            success=True,
            payroll_run_id=payroll_run_id,
            status=payroll_run.status,
            approved_by=request.approved_by,
            approved_at=payroll_run.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error approving payroll run: {str(e)}"
        )


# ============================================================================
# Employee Payroll Endpoints
# ============================================================================

@router.post(
    "/calculate",
    response_model=EmployeePayrollResult,
    summary="Calculate payroll for one employee",
    description="Calculates payroll for a single employee based on timer records"
)
def calculate_employee_payroll(
    request: EmployeePayrollCreate,
    service: PayrollService = Depends(get_payroll_service)
):
    """Calculate payroll for a single employee.

    Args:
        request: Employee payroll request with data and timer records
        service: Payroll service instance

    Returns:
        Employee payroll calculation result

    Raises:
        HTTPException: If calculation fails
    """
    try:
        result = service.calculate_employee_payroll(
            employee_data=request.employee_data.dict(),
            timer_records=[r.dict() for r in request.timer_records],
            payroll_run_id=request.payroll_run_id
        )

        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['error']
            )

        # Convert datetime strings to datetime objects
        if 'pay_period_start' in result:
            result['pay_period_start'] = result['pay_period_start']
        if 'pay_period_end' in result:
            result['pay_period_end'] = result['pay_period_end']

        return EmployeePayrollResult(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating payroll: {str(e)}"
        )


@router.post(
    "/calculate-from-timer-cards/{employee_id}",
    response_model=EmployeePayrollResult,
    summary="Calculate payroll from database timer cards",
    description="Calculates payroll for an employee using their timer card records from the database"
)
def calculate_payroll_from_timer_cards(
    employee_id: int = Path(..., ge=1, description="Employee ID"),
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    service: PayrollIntegrationService = Depends(get_payroll_integration_service)
):
    """Calculate payroll for an employee using their timer card records from the database.

    This endpoint:
    1. Fetches timer card records for the employee in the specified date range
    2. Matches timer cards to employee
    3. Calculates payroll based on the timer card data
    4. Returns the calculated payroll result

    Args:
        employee_id: Employee ID
        start_date: Start date in YYYY-MM-DD format (e.g., "2025-10-01")
        end_date: End date in YYYY-MM-DD format (e.g., "2025-10-31")
        service: Payroll integration service instance

    Returns:
        Employee payroll calculation result

    Raises:
        HTTPException: If employee not found or calculation fails
    """
    try:
        # Calculate payroll from timer cards
        result = service.calculate_payroll_from_timer_cards(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date
        )

        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND if 'not found' in result.get('error', '').lower() else status.HTTP_400_BAD_REQUEST,
                detail=result['error']
            )

        return EmployeePayrollResult(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating payroll from timer cards: {str(e)}"
        )


# ============================================================================
# Payslip Endpoints
# ============================================================================

@router.post(
    "/payslips/generate",
    response_model=PayslipInfo,
    summary="Generate payslip PDF",
    description="Generates a payslip PDF for an employee"
)
def generate_payslip(
    request: PayslipRequest,
    service: PayrollService = Depends(get_payroll_service),
    db: Session = Depends(get_db)
):
    """Generate a payslip PDF for an employee.

    Args:
        request: Payslip generation request
        service: Payroll service instance
        db: Database session

    Returns:
        Payslip generation result

    Raises:
        HTTPException: If generation fails
    """
    try:
        # Query EmployeePayroll by employee_id and payroll_run_id
        employee_payroll = db.query(EmployeePayroll).filter(
            EmployeePayroll.employee_id == request.employee_id,
            EmployeePayroll.payroll_run_id == request.payroll_run_id
        ).first()

        if not employee_payroll:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No payroll record found for employee {request.employee_id} in payroll run {request.payroll_run_id}"
            )

        # Build payroll_data dict from database fields
        payroll_data = {
            'pay_period_start': employee_payroll.pay_period_start.isoformat(),
            'pay_period_end': employee_payroll.pay_period_end.isoformat(),
            'hours': {
                'regular_hours': float(employee_payroll.regular_hours),
                'overtime_hours': float(employee_payroll.overtime_hours),
                'night_shift_hours': float(employee_payroll.night_shift_hours),
                'holiday_hours': float(employee_payroll.holiday_hours),
                'sunday_hours': float(employee_payroll.sunday_hours)
            },
            'rates': {
                'base_rate': float(employee_payroll.base_rate),
                'overtime_rate': float(employee_payroll.overtime_rate),
                'night_shift_rate': float(employee_payroll.night_shift_rate),
                'holiday_rate': float(employee_payroll.holiday_rate)
            },
            'amounts': {
                'base_amount': float(employee_payroll.base_amount),
                'overtime_amount': float(employee_payroll.overtime_amount),
                'night_shift_amount': float(employee_payroll.night_shift_amount),
                'holiday_amount': float(employee_payroll.holiday_amount),
                'gross_amount': float(employee_payroll.gross_amount),
                'total_deductions': float(employee_payroll.total_deductions),
                'net_amount': float(employee_payroll.net_amount)
            },
            'deductions': {
                'income_tax': float(employee_payroll.income_tax),
                'resident_tax': float(employee_payroll.resident_tax),
                'health_insurance': float(employee_payroll.health_insurance),
                'pension': float(employee_payroll.pension),
                'employment_insurance': float(employee_payroll.employment_insurance)
            }
        }

        # Call service to generate payslip
        result = service.generate_payslip(
            employee_id=request.employee_id,
            payroll_data=payroll_data
        )

        # Update employee_payroll with payslip info
        employee_payroll.payslip_generated = True
        if result.get('pdf_path'):
            employee_payroll.payslip_pdf_path = result['pdf_path']
        db.commit()

        return PayslipInfo(**result)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating payslip: {str(e)}"
        )


@router.get(
    "/payslips/{payslip_id}",
    response_model=PayslipInfo,
    summary="Get payslip information",
    description="Retrieves information about a generated payslip"
)
def get_payslip(
    payslip_id: str,
    service: PayrollService = Depends(get_payroll_service)
):
    """Get information about a generated payslip.

    Args:
        payslip_id: ID of the payslip
        service: Payroll service instance

    Returns:
        Payslip information

    Raises:
        HTTPException: If payslip not found
    """
    try:
        result = service.payslip_generator.get_payslip_info(payslip_id)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payslip {payslip_id} not found"
            )

        return PayslipInfo(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving payslip: {str(e)}"
        )


# ============================================================================
# Payroll Settings Endpoints
# ============================================================================

@router.get(
    "/settings",
    response_model=PayrollSettings,
    summary="Get payroll settings",
    description="Retrieves the current payroll settings"
)
def get_payroll_settings(
    service: PayrollService = Depends(get_payroll_service),
    db: Session = Depends(get_db)
):
    """Get current payroll settings.

    Args:
        service: Payroll service instance
        db: Database session

    Returns:
        Payroll settings

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        settings = service._get_payroll_settings()

        if not settings:
            # Return default settings
            return PayrollSettings(
                id=1,
                company_id=None,
                overtime_rate=1.25,
                night_shift_rate=1.25,
                holiday_rate=1.35,
                sunday_rate=1.35,
                standard_hours_per_month=160,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

        # Convert Decimal to float for Pydantic
        settings_dict = {k: float(v) if isinstance(v, (int, float)) else v
                        for k, v in settings.items()}

        return PayrollSettings(
            id=1,
            company_id=settings_dict.get('company_id'),
            overtime_rate=settings_dict.get('overtime_rate', 1.25),
            night_shift_rate=settings_dict.get('night_shift_rate', 1.25),
            holiday_rate=settings_dict.get('holiday_rate', 1.35),
            sunday_rate=settings_dict.get('sunday_rate', 1.35),
            standard_hours_per_month=settings_dict.get('standard_hours_per_month', 160),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving settings: {str(e)}"
        )


@router.put(
    "/settings",
    response_model=PayrollSettings,
    summary="Update payroll settings",
    description="Updates the payroll settings"
)
def update_payroll_settings(
    settings: PayrollSettingsUpdate,
    service: PayrollService = Depends(get_payroll_service)
):
    """Update payroll settings.

    Args:
        settings: Updated settings data
        service: Payroll service instance

    Returns:
        Updated payroll settings

    Raises:
        HTTPException: If update fails
    """
    try:
        # Convert to dict, excluding None values
        settings_dict = {k: v for k, v in settings.dict(exclude_unset=True).items()
                        if v is not None}

        result = service.update_payroll_settings(settings_dict)

        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['error']
            )

        return PayrollSettings(
            id=1,
            company_id=None,
            **settings_dict,
            created_at=datetime.now(),
            updated_at=datetime.fromisoformat(result['updated_at'])
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating settings: {str(e)}"
        )


# ============================================================================
# Summary Endpoints
# ============================================================================

@router.get(
    "/summary",
    response_model=List[PayrollSummary],
    summary="Get payroll summary",
    description="Retrieves a summary view of all payroll runs"
)
def get_payroll_summary(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of items to return"),
    service: PayrollService = Depends(get_payroll_service),
    db: Session = Depends(get_db)
):
    """Get a summary view of all payroll runs.

    Args:
        skip: Number of items to skip
        limit: Maximum number of items to return
        service: Payroll service instance
        db: Database session

    Returns:
        List of payroll summaries

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        # Query PayrollRun with aggregated employee_payroll data
        query = db.query(
            PayrollRunModel.id.label('payroll_run_id'),
            PayrollRunModel.pay_period_start,
            PayrollRunModel.pay_period_end,
            PayrollRunModel.status,
            PayrollRunModel.total_employees,
            PayrollRunModel.total_gross_amount,
            PayrollRunModel.total_deductions,
            PayrollRunModel.total_net_amount,
            func.coalesce(
                func.sum(
                    EmployeePayroll.regular_hours +
                    EmployeePayroll.overtime_hours +
                    EmployeePayroll.night_shift_hours +
                    EmployeePayroll.holiday_hours +
                    EmployeePayroll.sunday_hours
                ),
                0
            ).label('total_hours'),
            func.coalesce(func.avg(EmployeePayroll.gross_amount), 0).label('avg_gross_amount'),
            PayrollRunModel.created_at
        ).outerjoin(
            EmployeePayroll, EmployeePayroll.payroll_run_id == PayrollRunModel.id
        ).group_by(
            PayrollRunModel.id
        ).order_by(
            PayrollRunModel.created_at.desc()
        ).offset(skip).limit(limit).all()

        # Convert to PayrollSummary schemas
        summaries = []
        for row in query:
            summaries.append(PayrollSummary(
                payroll_run_id=row.payroll_run_id,
                pay_period_start=datetime.combine(row.pay_period_start, datetime.min.time()),
                pay_period_end=datetime.combine(row.pay_period_end, datetime.min.time()),
                status=row.status,
                total_employees=row.total_employees,
                total_gross_amount=float(row.total_gross_amount),
                total_deductions=float(row.total_deductions),
                total_net_amount=float(row.total_net_amount),
                total_hours=float(row.total_hours),
                avg_gross_amount=float(row.avg_gross_amount),
                created_at=row.created_at
            ))

        return summaries

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving summary: {str(e)}"
        )
