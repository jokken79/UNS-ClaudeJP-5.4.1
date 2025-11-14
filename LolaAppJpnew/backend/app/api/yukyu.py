"""
Yukyu (Paid Vacation) API - CRUD operations + LIFO deduction

Endpoints:
- POST /yukyu/grant - Grant annual yukyu to employee
- POST /yukyu/use - Use yukyu (LIFO deduction)
- GET /yukyu/balance/{employee_id} - Get employee's yukyu balance
- GET /yukyu/transactions/{employee_id} - Get transaction history
- POST /yukyu/expire - Mark expired balances
- GET /yukyu/summary/{employee_id} - Get comprehensive summary
- POST /yukyu/auto-grant - Auto-grant for all active employees
- POST /yukyu/adjust - Manual adjustment
"""
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_user
from app.models.models import User, Employee, YukyuBalance, YukyuTransaction
from app.schemas.yukyu import (
    YukyuGrantRequest,
    YukyuUseRequest,
    YukyuBalanceResponse,
    YukyuTransactionResponse,
    YukyuSummaryResponse,
    YukyuAutoGrantRequest
)
from app.services.yukyu_service import YukyuService

router = APIRouter()


@router.post("/grant", response_model=YukyuBalanceResponse)
async def grant_yukyu(
    request: YukyuGrantRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Grant annual yukyu to employee

    Creates a new YukyuBalance for the specified fiscal year.
    """
    employee = db.query(Employee).filter(
        Employee.hakenmoto_id == request.employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with hakenmoto_id {request.employee_id} not found"
        )

    yukyu_service = YukyuService(db)

    try:
        balance = yukyu_service.grant_yukyu(
            employee=employee,
            fiscal_year=request.fiscal_year,
            granted_days=request.granted_days,
            grant_date=request.grant_date,
            reason=request.reason
        )

        return balance
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/use")
async def use_yukyu(
    request: YukyuUseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Use yukyu with LIFO deduction

    Deducts from newest balances first (Last-In-First-Out).
    """
    employee = db.query(Employee).filter(
        Employee.hakenmoto_id == request.employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with hakenmoto_id {request.employee_id} not found"
        )

    yukyu_service = YukyuService(db)

    try:
        transactions = yukyu_service.use_yukyu(
            employee=employee,
            days_to_use=request.days_to_use,
            usage_date=request.usage_date,
            start_date=request.start_date,
            end_date=request.end_date,
            reason=request.reason
        )

        return {
            "success": True,
            "message": f"Successfully deducted {request.days_to_use} days using LIFO",
            "days_deducted": request.days_to_use,
            "transactions": transactions
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/balance/{employee_id}", response_model=List[YukyuBalanceResponse])
async def get_balance(
    employee_id: int,
    include_expired: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get yukyu balances for employee"""
    employee = db.query(Employee).filter(
        Employee.hakenmoto_id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with hakenmoto_id {employee_id} not found"
        )

    yukyu_service = YukyuService(db)
    balances = yukyu_service.get_balance(employee, include_expired=include_expired)

    return balances


@router.get("/transactions/{employee_id}", response_model=List[YukyuTransactionResponse])
async def get_transactions(
    employee_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get yukyu transaction history for employee"""
    employee = db.query(Employee).filter(
        Employee.hakenmoto_id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with hakenmoto_id {employee_id} not found"
        )

    transactions = db.query(YukyuTransaction).filter(
        YukyuTransaction.employee_id == employee_id
    ).order_by(
        YukyuTransaction.transaction_date.desc()
    ).limit(limit).all()

    return transactions


@router.post("/expire")
async def expire_old_balances(
    as_of_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Mark expired yukyu balances

    Japanese labor law: Yukyu expires after 2 years.
    """
    yukyu_service = YukyuService(db)
    expired_count = yukyu_service.expire_old_balances(as_of_date=as_of_date)

    return {
        "success": True,
        "message": f"Marked {expired_count} balances as expired",
        "expired_count": expired_count,
        "as_of_date": as_of_date or date.today()
    }


@router.get("/summary/{employee_id}", response_model=YukyuSummaryResponse)
async def get_summary(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get comprehensive yukyu summary for employee"""
    employee = db.query(Employee).filter(
        Employee.hakenmoto_id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with hakenmoto_id {employee_id} not found"
        )

    yukyu_service = YukyuService(db)

    # Get all balances
    balances = yukyu_service.get_balance(employee, include_expired=True)

    # Get recent transactions
    transactions = db.query(YukyuTransaction).filter(
        YukyuTransaction.employee_id == employee_id
    ).order_by(
        YukyuTransaction.transaction_date.desc()
    ).limit(10).all()

    # Calculate totals
    total_granted = sum(b.granted_days for b in balances)
    total_used = sum(b.used_days for b in balances)
    total_remaining = sum(b.remaining_days for b in balances if not b.is_expired)

    return {
        "employee_id": employee_id,
        "employee_name": employee.full_name_kanji,
        "total_granted": total_granted,
        "total_used": total_used,
        "total_remaining": total_remaining,
        "balances": balances,
        "recent_transactions": transactions
    }


@router.post("/auto-grant")
async def auto_grant_annual_yukyu(
    request: YukyuAutoGrantRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Auto-grant annual yukyu to all active employees

    Based on years of service and Japanese labor law standards.
    """
    yukyu_service = YukyuService(db)
    results = yukyu_service.auto_grant_annual_yukyu(
        fiscal_year=request.fiscal_year,
        grant_date=request.grant_date
    )

    success_count = len([r for r in results if r["success"]])
    error_count = len([r for r in results if not r["success"]])

    return {
        "success": True,
        "message": f"Auto-granted yukyu to {success_count} employees",
        "success_count": success_count,
        "error_count": error_count,
        "fiscal_year": request.fiscal_year,
        "results": results
    }


@router.post("/adjust")
async def adjust_yukyu(
    employee_id: int,
    fiscal_year: int,
    adjustment_days: float,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Manual yukyu adjustment

    For corrections or special circumstances.
    """
    employee = db.query(Employee).filter(
        Employee.hakenmoto_id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with hakenmoto_id {employee_id} not found"
        )

    balance = db.query(YukyuBalance).filter(
        YukyuBalance.employee_id == employee_id,
        YukyuBalance.fiscal_year == fiscal_year
    ).first()

    if not balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No yukyu balance found for employee {employee_id} in FY{fiscal_year}"
        )

    # Create adjustment transaction
    from app.models.models import YukyuTransactionType

    transaction = YukyuTransaction(
        balance_id=balance.id,
        employee_id=employee_id,
        transaction_type=YukyuTransactionType.ADJUSTMENT,
        transaction_date=date.today(),
        days=adjustment_days,
        description=f"Manual adjustment: {reason}"
    )

    balance.granted_days += adjustment_days
    balance.remaining_days += adjustment_days

    try:
        db.add(transaction)
        db.commit()
        db.refresh(balance)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return {
        "success": True,
        "message": f"Adjusted yukyu by {adjustment_days} days",
        "balance": balance,
        "transaction": transaction
    }
