"""
Requests API - Workflow system for approvals

Endpoints:
- POST /requests - Create request
- GET /requests - List all requests
- GET /requests/{id} - Get request details
- PUT /requests/{id} - Update request
- DELETE /requests/{id} - Delete request
- POST /requests/{id}/submit - Submit request for approval
- POST /requests/{id}/approve - Approve request
- POST /requests/{id}/reject - Reject request
"""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.deps import get_db, get_current_active_user
from app.models.models import (
    User, Request, RequestType, RequestStatus,
    Candidate, Employee, EmployeeStatus, Line
)
from app.schemas.request import (
    RequestCreate,
    RequestUpdate,
    RequestResponse,
    RequestListResponse,
    RequestApprovalRequest
)

router = APIRouter()


@router.post("/", response_model=RequestResponse, status_code=status.HTTP_201_CREATED)
async def create_request(
    request: RequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new request"""
    # Validate request_type
    try:
        request_type = RequestType[request.request_type.upper()]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request_type: {request.request_type}. Must be NYUSHA, YUKYU, TAISHA, or TRANSFER"
        )

    # Validate candidate_id for NYUSHA requests
    if request_type == RequestType.NYUSHA:
        if not request.candidate_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="candidate_id is required for NYUSHA requests"
            )
        candidate = db.query(Candidate).filter(
            Candidate.rirekisho_id == request.candidate_id
        ).first()
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Candidate with rirekisho_id {request.candidate_id} not found"
            )

    # Validate employee_id for other request types
    if request_type in [RequestType.YUKYU, RequestType.TAISHA, RequestType.TRANSFER]:
        if not request.employee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"employee_id is required for {request_type.value} requests"
            )
        employee = db.query(Employee).filter(
            Employee.hakenmoto_id == request.employee_id
        ).first()
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with hakenmoto_id {request.employee_id} not found"
            )

    db_request = Request(
        request_type=request_type,
        status=RequestStatus.DRAFT,
        created_by=current_user.id,
        candidate_id=request.candidate_id,
        employee_id=request.employee_id,
        request_data=request.request_data,
        notes=request.notes
    )

    try:
        db.add(db_request)
        db.commit()
        db.refresh(db_request)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return db_request


@router.get("/", response_model=RequestListResponse)
async def list_requests(
    skip: int = 0,
    limit: int = 100,
    request_type: Optional[str] = None,
    status: Optional[str] = None,
    employee_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all requests with optional filtering"""
    query = db.query(Request)

    if request_type:
        try:
            type_enum = RequestType[request_type.upper()]
            query = query.filter(Request.request_type == type_enum)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid request_type: {request_type}"
            )

    if status:
        try:
            status_enum = RequestStatus[status.upper()]
            query = query.filter(Request.status == status_enum)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}"
            )

    if employee_id:
        query = query.filter(Request.employee_id == employee_id)

    total = query.count()
    requests = query.order_by(Request.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "requests": requests
    }


@router.get("/{request_id}", response_model=RequestResponse)
async def get_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get request by ID"""
    request = db.query(Request).filter(Request.id == request_id).first()

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Request with ID {request_id} not found"
        )

    return request


@router.put("/{request_id}", response_model=RequestResponse)
async def update_request(
    request_id: int,
    request_update: RequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update request (only DRAFT status can be edited)"""
    request = db.query(Request).filter(Request.id == request_id).first()

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Request with ID {request_id} not found"
        )

    if request.status != RequestStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update request with status {request.status.value}. Only DRAFT requests can be edited."
        )

    # Update fields
    for field, value in request_update.dict(exclude_unset=True).items():
        if field == "request_type" and value:
            try:
                value = RequestType[value.upper()]
            except KeyError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid request_type: {value}"
                )
        setattr(request, field, value)

    try:
        db.commit()
        db.refresh(request)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return request


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete request (only DRAFT status can be deleted)"""
    request = db.query(Request).filter(Request.id == request_id).first()

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Request with ID {request_id} not found"
        )

    if request.status != RequestStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete request with status {request.status.value}. Only DRAFT requests can be deleted."
        )

    try:
        db.delete(request)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return None


@router.post("/{request_id}/submit", response_model=RequestResponse)
async def submit_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Submit request for approval"""
    request = db.query(Request).filter(Request.id == request_id).first()

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Request with ID {request_id} not found"
        )

    if request.status != RequestStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot submit request with status {request.status.value}. Only DRAFT requests can be submitted."
        )

    request.status = RequestStatus.PENDING

    try:
        db.commit()
        db.refresh(request)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return request


@router.post("/{request_id}/approve", response_model=RequestResponse)
async def approve_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Approve request and execute the action

    - NYUSHA: Create employee from candidate
    - YUKYU: Deduct yukyu days
    - TAISHA: Update employee status to RESIGNED
    - TRANSFER: Update employee's line_id
    """
    request = db.query(Request).filter(Request.id == request_id).first()

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Request with ID {request_id} not found"
        )

    if request.status != RequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve request with status {request.status.value}. Only PENDING requests can be approved."
        )

    # Execute request action
    try:
        if request.request_type == RequestType.NYUSHA:
            # Create employee from candidate
            candidate = db.query(Candidate).filter(
                Candidate.rirekisho_id == request.candidate_id
            ).first()

            if not candidate:
                raise ValueError(f"Candidate {request.candidate_id} not found")

            # Extract data from request_data
            request_data = request.request_data or {}
            line_id = request_data.get("line_id")

            if not line_id:
                raise ValueError("line_id is required in request_data for NYUSHA requests")

            # Verify line exists
            line = db.query(Line).filter(Line.id == line_id).first()
            if not line:
                raise ValueError(f"Line {line_id} not found")

            # Create employee (simplified - would use employee service in production)
            employee = Employee(
                full_name_roman=candidate.full_name_roman,
                full_name_kanji=candidate.full_name_kanji,
                full_name_kana=candidate.full_name_kana,
                date_of_birth=candidate.date_of_birth,
                email=candidate.email,
                phone=candidate.phone,
                current_address=candidate.current_address,
                line_id=line_id,
                status=EmployeeStatus.ACTIVE,
                hire_date=request_data.get("hire_date", date.today())
            )

            db.add(employee)
            db.flush()  # Get employee.hakenmoto_id

            # Update candidate status
            from app.models.models import CandidateStatus
            candidate.status = CandidateStatus.HIRED

        elif request.request_type == RequestType.YUKYU:
            # Deduct yukyu (would use yukyu service in production)
            pass

        elif request.request_type == RequestType.TAISHA:
            # Update employee status
            employee = db.query(Employee).filter(
                Employee.hakenmoto_id == request.employee_id
            ).first()

            if employee:
                employee.status = EmployeeStatus.RESIGNED
                employee.resignation_date = request.request_data.get("resignation_date", date.today())

        elif request.request_type == RequestType.TRANSFER:
            # Update employee line
            employee = db.query(Employee).filter(
                Employee.hakenmoto_id == request.employee_id
            ).first()

            if employee:
                new_line_id = request.request_data.get("new_line_id")
                if new_line_id:
                    employee.line_id = new_line_id

        # Update request status
        request.status = RequestStatus.APPROVED
        request.approved_by = current_user.id
        request.approved_at = date.today()

        db.commit()
        db.refresh(request)

        return request

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error approving request: {str(e)}"
        )


@router.post("/{request_id}/reject", response_model=RequestResponse)
async def reject_request(
    request_id: int,
    approval_request: RequestApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Reject request"""
    request = db.query(Request).filter(Request.id == request_id).first()

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Request with ID {request_id} not found"
        )

    if request.status != RequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject request with status {request.status.value}. Only PENDING requests can be rejected."
        )

    if not approval_request.reason:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rejection reason is required"
        )

    request.status = RequestStatus.REJECTED
    request.approved_by = current_user.id
    request.approved_at = date.today()
    request.rejection_reason = approval_request.reason

    try:
        db.commit()
        db.refresh(request)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return request
