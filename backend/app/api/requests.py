"""
Requests API Endpoints (Yukyu, Ikkikokoku, Taisha, etc.)

NOTE (2025-11-12): This API handles ALL request types generically.
For yukyu-specific operations (balance management, calculations, reports),
use the specialized /api/yukyu endpoints which provide richer functionality.

Supported request types:
- YUKYU (有給休暇) - Paid vacation -> Use /api/yukyu for advanced features
- IKKIKOKOKU (一時帰国) - Temporary return home
- TAISHA (退社) - Resignation
- NYUUSHA (入社) - New hire
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from datetime import date, datetime

from app.core.database import get_db
from app.models.models import Request, Employee, User, RequestType, RequestStatus, Candidate, CandidateStatus
from app.schemas.request import RequestCreate, RequestUpdate, RequestResponse, RequestReview, EmployeeDataInput
from app.schemas.base import PaginatedResponse, create_paginated_response
from app.services.auth_service import auth_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=RequestResponse, status_code=201)
async def create_request(
    request_data: RequestCreate,
    current_user: User = Depends(auth_service.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create new request (yukyu, ikkikokoku, taisha, nyuusha, etc.)

    NOTE: For yukyu requests with automatic balance deduction and
    advanced validations, consider using POST /api/yukyu/requests/ instead.
    """
    # Verify employee exists
    employee = db.query(Employee).filter(Employee.id == request_data.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Check if employee can make request (only their own unless admin)
    if current_user.role.value == "employee":
        # Employee can only request for themselves
        # You'd need to link user to employee here
        pass

    # Calculate total days (for validation)
    delta = request_data.end_date - request_data.start_date
    total_days = delta.days + 1

    # Check yukyu balance for yukyu/hankyu requests
    if request_data.request_type in [RequestType.YUKYU, RequestType.HANKYU]:
        if employee.yukyu_remaining < float(total_days):
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient yukyu balance. Available: {employee.yukyu_remaining}"
            )

    # Create request with hakenmoto_id from employee
    request_dict = request_data.model_dump()
    request_dict['hakenmoto_id'] = employee.hakenmoto_id
    del request_dict['employee_id']  # Remove employee_id from schema
    if 'total_days' in request_dict:
        del request_dict['total_days']  # Remove total_days - it's a computed property

    new_request = Request(**request_dict)
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return new_request


@router.get("/", response_model=PaginatedResponse[RequestResponse])
async def list_requests(
    employee_id: int = Query(None, description="Filter by employee ID"),
    status: RequestStatus = Query(None, description="Filter by request status"),
    request_type: RequestType = Query(None, description="Filter by request type"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(auth_service.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List requests with pagination.

    Returns paginated list of employee requests (yukyu, ikkikokoku, taisha, etc.)
    """
    query = db.query(Request)

    # Apply filters
    if employee_id:
        # Convert employee.id to hakenmoto_id for filtering
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if employee:
            query = query.filter(Request.hakenmoto_id == employee.hakenmoto_id)
        else:
            # If employee not found, return empty result
            return create_paginated_response(items=[], total=0, page=page, page_size=page_size)

    if status:
        query = query.filter(Request.status == status)
    if request_type:
        query = query.filter(Request.request_type == request_type)

    # Get total count
    total = query.count()

    # Calculate pagination
    skip = (page - 1) * page_size

    # Get paginated results
    items = (
        query
        .order_by(Request.created_at.desc())
        .offset(skip)
        .limit(page_size)
        .all()
    )

    return create_paginated_response(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{request_id}", response_model=RequestResponse)
async def get_request(
    request_id: int,
    current_user: User = Depends(auth_service.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get request by ID"""
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request


@router.put("/{request_id}", response_model=RequestResponse)
async def update_request(
    request_id: int,
    request_update: RequestUpdate,
    current_user: User = Depends(auth_service.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update request (before approval)"""
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    if request.status != RequestStatus.PENDING:
        raise HTTPException(status_code=400, detail="Can only update pending requests")

    # Update fields, excluding total_days (computed property)
    for field, value in request_update.model_dump(exclude_unset=True).items():
        if field != 'total_days':
            setattr(request, field, value)

    db.commit()
    db.refresh(request)
    return request


@router.post("/{request_id}/review", response_model=RequestResponse)
async def review_request(
    request_id: int,
    review_data: RequestReview,
    current_user: User = Depends(auth_service.require_role("admin")),
    db: Session = Depends(get_db)
):
    """Approve or reject request"""
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    if request.status != RequestStatus.PENDING:
        raise HTTPException(status_code=400, detail="Request already reviewed")

    request.status = review_data.status
    request.approved_by = current_user.id
    request.approved_at = func.now()
    if review_data.notes:
        request.notes = review_data.notes

    # Update yukyu balance if approved
    if review_data.status == RequestStatus.APPROVED:
        if request.request_type in [RequestType.YUKYU, RequestType.HANKYU]:
            employee = db.query(Employee).filter(Employee.hakenmoto_id == request.hakenmoto_id).first()
            if employee:
                employee.yukyu_used += float(request.total_days)
                employee.yukyu_remaining -= float(request.total_days)

    db.commit()
    db.refresh(request)
    return request


@router.post("/{request_id}/approve", response_model=RequestResponse)
async def approve_request(
    request_id: int,
    current_user: User = Depends(auth_service.require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Approve a request (convenience endpoint).
    Shortcut for /review with status=APPROVED.

    NOTE: For yukyu requests, /api/yukyu/requests/{id}/approve provides
    comprehensive approval logic with balance validation and history tracking.
    """
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    if request.status != RequestStatus.PENDING:
        raise HTTPException(status_code=400, detail="Request already reviewed")

    request.status = RequestStatus.APPROVED
    request.approved_by = current_user.id
    request.approved_at = func.now()

    # Update yukyu balance if approved
    if request.request_type in [RequestType.YUKYU, RequestType.HANKYU]:
        employee = db.query(Employee).filter(Employee.hakenmoto_id == request.hakenmoto_id).first()
        if employee:
            employee.yukyu_used += float(request.total_days)
            employee.yukyu_remaining -= float(request.total_days)

    db.commit()
    db.refresh(request)
    return request


@router.post("/{request_id}/reject", response_model=RequestResponse)
async def reject_request_endpoint(
    request_id: int,
    reason: str,
    current_user: User = Depends(auth_service.require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Reject a request with reason (convenience endpoint).
    Shortcut for /review with status=REJECTED.
    """
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    if request.status != RequestStatus.PENDING:
        raise HTTPException(status_code=400, detail="Request already reviewed")

    request.status = RequestStatus.REJECTED
    request.approved_by = current_user.id
    request.approved_at = func.now()
    request.notes = reason

    db.commit()
    db.refresh(request)
    return request


@router.delete("/{request_id}")
async def delete_request(
    request_id: int,
    current_user: User = Depends(auth_service.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete request (only pending requests)"""
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    if request.status != RequestStatus.PENDING:
        raise HTTPException(status_code=400, detail="Can only delete pending requests")

    db.delete(request)
    db.commit()
    return {"message": "Request deleted"}


# ═══════════════════════════════════════════════════════════════════════════
#  🆕 ENDPOINTS FOR 入社連絡票 (NYUUSHA RENRAKUHYO) WORKFLOW
# ═══════════════════════════════════════════════════════════════════════════

@router.put("/{request_id}/employee-data")
async def save_employee_data(
    request_id: int,
    employee_data: EmployeeDataInput,
    current_user: User = Depends(auth_service.require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Save employee-specific data for a 入社連絡票 (New Hire Notification Form)

    This endpoint allows admins to fill in the employee-specific fields
    before approving the 入社連絡票 and creating the employee record.

    The data is stored as JSON in the employee_data field and will be used
    when the request is approved to create the employee.

    **Required role**: admin or higher
    """
    # Get request
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    # Verify it's a NYUUSHA request
    if request.request_type != RequestType.NYUUSHA:
        raise HTTPException(
            status_code=400,
            detail="This endpoint is only for 入社連絡票 (NYUUSHA) requests"
        )

    # Verify request is still pending
    if request.status != RequestStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot modify request with status: {request.status}"
        )

    # Save employee data as JSON
    request.employee_data = employee_data.model_dump()

    db.commit()
    db.refresh(request)

    logger.info(f"Saved employee data for 入社連絡票 request {request_id} by user {current_user.id}")

    return {
        "message": "Employee data saved successfully",
        "request_id": request.id,
        "employee_data": request.employee_data
    }


@router.post("/{request_id}/approve-nyuusha")
async def approve_nyuusha_request(
    request_id: int,
    current_user: User = Depends(auth_service.require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Approve a 入社連絡票 (New Hire Notification Form) and create employee record

    This endpoint:
    1. Validates the request is a NYUUSHA type and has employee_data filled
    2. Creates an Employee record with data from both candidate and employee_data
    3. Updates the candidate status to HIRED
    4. Updates the request status to COMPLETED
    5. Links the employee to the request via hakenmoto_id

    **Required role**: admin or higher
    """
    # 1. Get and validate request
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    if request.request_type != RequestType.NYUUSHA:
        raise HTTPException(
            status_code=400,
            detail="This endpoint is only for 入社連絡票 (NYUUSHA) requests"
        )

    if request.status != RequestStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Request is already {request.status}"
        )

    if not request.employee_data:
        raise HTTPException(
            status_code=400,
            detail="Employee data must be filled before approval. Use PUT /api/requests/{id}/employee-data first."
        )

    # 2. Get candidate
    if not request.candidate_id:
        raise HTTPException(
            status_code=400,
            detail="Request has no associated candidate"
        )

    candidate = db.query(Candidate).filter(Candidate.id == request.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Associated candidate not found")

    # 3. Check if employee already exists
    existing_employee = db.query(Employee).filter(
        Employee.rirekisho_id == candidate.rirekisho_id
    ).first()

    if existing_employee:
        raise HTTPException(
            status_code=400,
            detail=f"Employee already exists for this candidate (hakenmoto_id: {existing_employee.hakenmoto_id})"
        )

    # 4. Generate hakenmoto_id
    max_hakenmoto_id = db.query(func.max(Employee.hakenmoto_id)).scalar() or 0
    new_hakenmoto_id = max_hakenmoto_id + 1

    # 5. Extract employee data from JSON
    emp_data = request.employee_data

    # 6. Create Employee record
    new_employee = Employee(
        hakenmoto_id=new_hakenmoto_id,
        rirekisho_id=candidate.rirekisho_id,

        # Copy personal data from candidate (40+ fields)
        full_name_roman=candidate.full_name_roman,
        full_name_kanji=candidate.full_name_kanji,
        full_name_kana=candidate.full_name_kana,
        date_of_birth=candidate.date_of_birth,
        gender=candidate.gender,
        nationality=candidate.nationality,
        email=candidate.email,
        phone=candidate.phone,
        address=candidate.address,
        photo_data_url=candidate.photo_data_url,
        passport_number=candidate.passport_number,
        zairyu_card_number=candidate.zairyu_card_number,
        visa_type=candidate.visa_type,
        visa_expiration=candidate.visa_expiration,
        marital_status=candidate.marital_status,
        dependents=candidate.dependents,

        # Add employee-specific data from employee_data JSON
        factory_id=emp_data.get("factory_id"),
        hire_date=emp_data.get("hire_date"),
        jikyu=emp_data.get("jikyu"),
        position=emp_data.get("position"),
        contract_type=emp_data.get("contract_type"),
        hakensaki_shain_id=emp_data.get("hakensaki_shain_id"),
        apartment_id=emp_data.get("apartment_id"),
        bank_name=emp_data.get("bank_name"),
        bank_account=emp_data.get("bank_account"),
        emergency_contact_name=emp_data.get("emergency_contact_name"),
        emergency_contact_phone=emp_data.get("emergency_contact_phone"),

        # Status
        status="active",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    db.add(new_employee)
    db.flush()  # Get the employee ID without committing

    # 7. Update candidate status to HIRED
    candidate.status = CandidateStatus.HIRED

    # 8. Update request
    request.status = RequestStatus.COMPLETED  # 済
    request.approved_by = current_user.id
    request.approved_at = datetime.now()
    request.hakenmoto_id = new_hakenmoto_id  # Link request to employee

    db.commit()
    db.refresh(new_employee)

    logger.info(
        f"入社連絡票 approved: Request {request_id} → Employee created "
        f"(hakenmoto_id: {new_hakenmoto_id}, rirekisho_id: {candidate.rirekisho_id})"
    )

    return {
        "message": "入社連絡票 approved successfully. Employee created.",
        "employee_id": new_employee.id,
        "hakenmoto_id": new_hakenmoto_id,
        "rirekisho_id": new_employee.rirekisho_id,
        "candidate_status": candidate.status,
        "request_status": request.status
    }
