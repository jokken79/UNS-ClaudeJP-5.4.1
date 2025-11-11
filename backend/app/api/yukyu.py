"""
Yukyu (有給休暇 - Paid Vacation) API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.models import User, UserRole
from app.schemas.yukyu import (
    YukyuBalanceResponse,
    YukyuBalanceSummary,
    YukyuRequestCreate,
    YukyuRequestResponse,
    YukyuRequestApprove,
    YukyuRequestReject,
    YukyuCalculationRequest,
    YukyuCalculationResponse,
    EmployeeByFactoryResponse,
)
from app.services.auth_service import auth_service
from app.services.yukyu_service import YukyuService

router = APIRouter()


# ============================================================================
# YUKYU BALANCE ENDPOINTS
# ============================================================================

@router.post("/balances/calculate", response_model=YukyuCalculationResponse)
async def calculate_employee_yukyus(
    calc_request: YukyuCalculationRequest,
    current_user: User = Depends(auth_service.require_role(["admin", "keitosan"])),
    db: Session = Depends(get_db)
):
    """
    Calculate and create yukyu balances for an employee.

    **Permissions:** ADMIN, KEITOSAN

    **What it does:**
    - Calculates yukyus based on employee hire date and Japanese labor law
    - Creates missing balance records for all milestones (6mo, 18mo, 30mo, etc.)
    - Returns total available yukyu days

    **When to use:**
    - After creating a new employee
    - Monthly cron job to assign new yukyus
    - Manual recalculation by admin
    """
    service = YukyuService(db)
    return await service.calculate_and_create_balances(
        employee_id=calc_request.employee_id,
        calculation_date=calc_request.calculation_date
    )


@router.get("/balances/{employee_id}", response_model=YukyuBalanceSummary)
async def get_employee_yukyu_summary(
    employee_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get complete yukyu summary for an employee.

    **Permissions:** Any authenticated user

    **Returns:**
    - All active yukyu balances
    - Total available, used, and expired days
    - Oldest expiration date
    - Alert if needs to use 5 days minimum
    """
    service = YukyuService(db)
    return await service.get_employee_yukyu_summary(employee_id)


# ============================================================================
# YUKYU REQUEST ENDPOINTS
# ============================================================================

@router.post("/requests/", response_model=YukyuRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_yukyu_request(
    request_data: YukyuRequestCreate,
    current_user: User = Depends(auth_service.require_role(["tantosha", "admin", "keitosan"])),
    db: Session = Depends(get_db)
):
    """
    Create yukyu request (by TANTOSHA).

    **Permissions:** TANTOSHA, ADMIN, KEITOSAN

    **Workflow:**
    1. TANTOSHA selects employee from their factory
    2. Requests yukyu days (can be 0.5 for hannichi - half day)
    3. System validates employee has enough yukyus available
    4. Request created with status=PENDING
    5. KEIRI receives notification to approve/reject

    **Request Types:**
    - `yukyu`: Full paid vacation day
    - `hankyu`: Half day (半休)
    - `ikkikokoku`: Temporary return to home country (一時帰国)
    - `taisha`: Resignation (退社)
    """
    service = YukyuService(db)
    return await service.create_request(request_data, current_user.id)


@router.get("/requests/", response_model=List[YukyuRequestResponse])
async def list_yukyu_requests(
    factory_id: Optional[str] = Query(None, description="Filter by factory ID"),
    status: Optional[str] = Query(None, description="Filter by status (pending, approved, rejected)"),
    employee_id: Optional[int] = Query(None, description="Filter by employee ID"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    List yukyu requests with role-based filtering.

    **Permissions:**
    - **TANTOSHA:** Can only see requests for their factory (factory_id required)
    - **KEIRI/ADMIN:** Can see all requests (factory_id optional)

    **Filters:**
    - `factory_id`: Filter by factory
    - `status`: Filter by status (pending, approved, rejected)
    - `employee_id`: Filter by specific employee
    - `limit`: Max results (default 100, max 500)
    - `offset`: Pagination offset
    """
    service = YukyuService(db)
    return await service.list_requests(
        user=current_user,
        factory_id=factory_id,
        status=status,
        employee_id=employee_id,
        limit=limit,
        offset=offset
    )


@router.put("/requests/{request_id}/approve", response_model=YukyuRequestResponse)
async def approve_yukyu_request(
    request_id: int,
    approval_data: YukyuRequestApprove,
    current_user: User = Depends(auth_service.require_role(["keitosan", "admin"])),
    db: Session = Depends(get_db)
):
    """
    Approve yukyu request (by KEIRI).

    **Permissions:** KEITOSAN, ADMIN

    **What happens when approved:**
    1. Validates request is in PENDING status
    2. Deducts yukyu days using LIFO (newest first)
    3. Creates usage_details records linking to specific balances
    4. Updates request status to APPROVED
    5. Records approval date and approving user

    **LIFO Deduction:**
    Newest yukyus are used first to maximize usage before expiration.

    Example:
    - Employee has: 8 days from 2023 + 11 days from 2024 = 19 days total
    - Request: 5 days
    - Deduction: 5 days from 2024 (newest)
    - Remaining: 8 days from 2023 + 6 days from 2024 = 14 days total
    """
    service = YukyuService(db)
    return await service.approve_request(request_id, approval_data, current_user.id)


@router.put("/requests/{request_id}/reject", response_model=YukyuRequestResponse)
async def reject_yukyu_request(
    request_id: int,
    rejection_data: YukyuRequestReject,
    current_user: User = Depends(auth_service.require_role(["keitosan", "admin"])),
    db: Session = Depends(get_db)
):
    """
    Reject yukyu request (by KEIRI).

    **Permissions:** KEITOSAN, ADMIN

    **Required:**
    - `rejection_reason`: Reason for rejection (shown to employee)

    **What happens:**
    1. Validates request is in PENDING status
    2. Updates status to REJECTED
    3. Records rejection reason, date, and rejecting user
    4. No yukyus are deducted
    """
    service = YukyuService(db)
    return await service.reject_request(request_id, rejection_data, current_user.id)


# ============================================================================
# EMPLOYEE LOOKUP FOR TANTOSHA
# ============================================================================

@router.get("/employees/by-factory/{factory_id}", response_model=List[EmployeeByFactoryResponse])
async def get_employees_by_factory(
    factory_id: str,
    current_user: User = Depends(auth_service.require_role(["tantosha", "admin", "keitosan"])),
    db: Session = Depends(get_db)
):
    """
    Get all employees in a factory with their yukyu availability.

    **Permissions:** TANTOSHA, ADMIN, KEITOSAN

    **Use case:**
    TANTOSHA uses this to see which employees they can request yukyus for.

    **Returns:**
    - Employee ID, name, hire date
    - Current yukyu days available
    - Factory info
    """
    service = YukyuService(db)
    return await service.get_employees_by_factory(factory_id)


# ============================================================================
# MAINTENANCE ENDPOINTS
# ============================================================================

@router.post("/maintenance/expire-old-yukyus", response_model=dict)
async def expire_old_yukyus(
    current_user: User = Depends(auth_service.require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """
    Expire yukyus that are older than 2 years (時効 - jikou).

    **Permissions:** ADMIN only

    **When to call:**
    - Daily cron job
    - Manual trigger by admin

    **What it does:**
    - Finds all active balances with expires_on <= today
    - Marks them as EXPIRED
    - Moves days_remaining to days_expired
    - Sets days_available to 0

    **Returns:**
    - Number of balances expired
    """
    service = YukyuService(db)
    count = await service.expire_old_yukyus()
    return {
        "message": f"Expired {count} yukyu balance(s)",
        "count": count
    }
