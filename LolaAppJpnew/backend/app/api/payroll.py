"""
Payroll API - Salary calculations

Endpoints:
- POST /payroll/calculate - Calculate payroll for single employee
- POST /payroll/batch - Calculate payroll for multiple employees
- GET /payroll/employee/{employee_id} - Get payroll history for employee
- GET /payroll/{year}/{month} - Get all payroll records for a month
- POST /payroll/export - Export payroll to Excel/CSV
- GET /payroll/summary/{year}/{month} - Get payroll summary for month
"""
from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_user
from app.models.models import User, Employee, EmployeeStatus
from app.schemas.payroll import (
    PayrollCalculationRequest,
    PayrollCalculationResponse,
    PayrollBatchCalculationRequest,
    PayrollBatchCalculationResponse
)
from app.services.payroll_service import PayrollService

router = APIRouter()


@router.post("/calculate", response_model=PayrollCalculationResponse)
async def calculate_payroll(
    request: PayrollCalculationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Calculate monthly payroll for single employee

    Calculates based on:
    - Timer card hours (regular, overtime, night, holiday)
    - Yukyu days used
    - Apartment rent deductions
    - Tax and insurance deductions
    """
    employee = db.query(Employee).filter(
        Employee.hakenmoto_id == request.employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with hakenmoto_id {request.employee_id} not found"
        )

    payroll_service = PayrollService(db)

    try:
        result = payroll_service.calculate_monthly_payroll(
            employee=employee,
            year=request.year,
            month=request.month
        )

        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/batch", response_model=PayrollBatchCalculationResponse)
async def calculate_payroll_batch(
    request: PayrollBatchCalculationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Calculate payroll for multiple employees (or all active employees)

    If employee_ids is None, calculates for all active employees.
    """
    payroll_service = PayrollService(db)

    # Get employee list
    if request.employee_ids:
        employees = db.query(Employee).filter(
            Employee.hakenmoto_id.in_(request.employee_ids)
        ).all()
    else:
        # Get all active employees
        employees = db.query(Employee).filter(
            Employee.status == EmployeeStatus.ACTIVE,
            Employee.is_deleted == False
        ).all()

    if not employees:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No employees found"
        )

    # Calculate payroll for each employee
    results = []
    success_count = 0
    error_count = 0
    total_gross_pay = 0.0
    total_net_pay = 0.0

    for employee in employees:
        try:
            result = payroll_service.calculate_monthly_payroll(
                employee=employee,
                year=request.year,
                month=request.month
            )
            results.append(result)
            success_count += 1
            total_gross_pay += result["gross_pay"]
            total_net_pay += result["net_pay"]
        except Exception as e:
            error_count += 1
            # Add error result
            results.append({
                "employee_id": employee.hakenmoto_id,
                "employee_name": employee.full_name_kanji or employee.full_name_roman,
                "year": request.year,
                "month": request.month,
                "error": str(e),
                "gross_pay": 0.0,
                "net_pay": 0.0
            })

    return {
        "year": request.year,
        "month": request.month,
        "total_employees": len(employees),
        "success_count": success_count,
        "error_count": error_count,
        "total_gross_pay": total_gross_pay,
        "total_net_pay": total_net_pay,
        "results": results
    }


@router.get("/employee/{employee_id}")
async def get_employee_payroll_history(
    employee_id: int,
    start_year: Optional[int] = None,
    start_month: Optional[int] = None,
    end_year: Optional[int] = None,
    end_month: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get payroll history for specific employee"""
    employee = db.query(Employee).filter(
        Employee.hakenmoto_id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with hakenmoto_id {employee_id} not found"
        )

    from app.models.models import PayrollRecord
    query = db.query(PayrollRecord).filter(
        PayrollRecord.employee_id == employee_id
    )

    # Apply date filters if provided
    if start_year and start_month:
        start_date = date(start_year, start_month, 1)
        query = query.filter(PayrollRecord.payroll_date >= start_date)

    if end_year and end_month:
        from calendar import monthrange
        _, last_day = monthrange(end_year, end_month)
        end_date = date(end_year, end_month, last_day)
        query = query.filter(PayrollRecord.payroll_date <= end_date)

    records = query.order_by(PayrollRecord.payroll_date.desc()).all()

    return {
        "employee_id": employee_id,
        "employee_name": employee.full_name_kanji or employee.full_name_roman,
        "total_records": len(records),
        "records": records
    }


@router.get("/{year}/{month}")
async def get_monthly_payroll(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all payroll records for a specific month"""
    from app.models.models import PayrollRecord
    from calendar import monthrange

    _, last_day = monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, last_day)

    records = db.query(PayrollRecord).filter(
        PayrollRecord.payroll_date >= start_date,
        PayrollRecord.payroll_date <= end_date
    ).all()

    total_gross_pay = sum(r.gross_pay for r in records)
    total_net_pay = sum(r.net_pay for r in records)

    return {
        "year": year,
        "month": month,
        "total_employees": len(records),
        "total_gross_pay": total_gross_pay,
        "total_net_pay": total_net_pay,
        "records": records
    }


@router.get("/summary/{year}/{month}")
async def get_payroll_summary(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get payroll summary statistics for a month"""
    from app.models.models import PayrollRecord
    from calendar import monthrange
    from sqlalchemy import func

    _, last_day = monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, last_day)

    # Aggregate statistics
    summary = db.query(
        func.count(PayrollRecord.id).label('total_employees'),
        func.sum(PayrollRecord.gross_pay).label('total_gross_pay'),
        func.sum(PayrollRecord.net_pay).label('total_net_pay'),
        func.sum(PayrollRecord.regular_pay).label('total_regular_pay'),
        func.sum(PayrollRecord.overtime_pay).label('total_overtime_pay'),
        func.sum(PayrollRecord.total_deductions).label('total_deductions'),
        func.avg(PayrollRecord.gross_pay).label('average_gross_pay'),
        func.avg(PayrollRecord.net_pay).label('average_net_pay')
    ).filter(
        PayrollRecord.payroll_date >= start_date,
        PayrollRecord.payroll_date <= end_date
    ).first()

    return {
        "year": year,
        "month": month,
        "total_employees": summary.total_employees or 0,
        "total_gross_pay": float(summary.total_gross_pay or 0),
        "total_net_pay": float(summary.total_net_pay or 0),
        "total_regular_pay": float(summary.total_regular_pay or 0),
        "total_overtime_pay": float(summary.total_overtime_pay or 0),
        "total_deductions": float(summary.total_deductions or 0),
        "average_gross_pay": float(summary.average_gross_pay or 0),
        "average_net_pay": float(summary.average_net_pay or 0)
    }
