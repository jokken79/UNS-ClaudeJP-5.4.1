"""
TimerCards API - CRUD operations + OCR processing

Endpoints:
- POST /timercards - Create timercard
- GET /timercards - List all timercards
- GET /timercards/{id} - Get timercard details
- PUT /timercards/{id} - Update timercard
- DELETE /timercards/{id} - Delete timercard
- POST /timercards/ocr - Process OCR for monthly timecards (PDF)
- GET /timercards/employee/{employee_id} - Get timercards for employee
"""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.deps import get_db, get_current_active_user
from app.models.models import User, Employee, TimerCard
from app.schemas.timercard import (
    TimerCardCreate,
    TimerCardUpdate,
    TimerCardResponse,
    TimerCardListResponse,
    TimerCardOCRRequest
)
from app.services.ocr_service import OCRService

router = APIRouter()


@router.post("/", response_model=TimerCardResponse, status_code=status.HTTP_201_CREATED)
async def create_timercard(
    timercard: TimerCardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new timercard"""
    # Verify employee exists
    employee = db.query(Employee).filter(
        Employee.hakenmoto_id == timercard.employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with hakenmoto_id {timercard.employee_id} not found"
        )

    # Check for duplicate (same employee + same date)
    existing = db.query(TimerCard).filter(
        and_(
            TimerCard.employee_id == timercard.employee_id,
            TimerCard.work_date == timercard.work_date,
            TimerCard.is_deleted == False
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"TimerCard already exists for employee {timercard.employee_id} on {timercard.work_date}"
        )

    db_timercard = TimerCard(**timercard.dict())

    try:
        db.add(db_timercard)
        db.commit()
        db.refresh(db_timercard)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return db_timercard


@router.get("/", response_model=TimerCardListResponse)
async def list_timercards(
    skip: int = 0,
    limit: int = 100,
    employee_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all timercards with optional filtering"""
    query = db.query(TimerCard).filter(TimerCard.is_deleted == False)

    if employee_id:
        query = query.filter(TimerCard.employee_id == employee_id)

    if start_date:
        query = query.filter(TimerCard.work_date >= start_date)

    if end_date:
        query = query.filter(TimerCard.work_date <= end_date)

    total = query.count()
    timercards = query.order_by(TimerCard.work_date.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "timercards": timercards
    }


@router.get("/employee/{employee_id}", response_model=TimerCardListResponse)
async def get_employee_timercards(
    employee_id: int,
    year: Optional[int] = None,
    month: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all timercards for a specific employee"""
    employee = db.query(Employee).filter(
        Employee.hakenmoto_id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with hakenmoto_id {employee_id} not found"
        )

    query = db.query(TimerCard).filter(
        TimerCard.employee_id == employee_id,
        TimerCard.is_deleted == False
    )

    # Filter by year/month if provided
    if year and month:
        from calendar import monthrange
        _, last_day = monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)
        query = query.filter(
            and_(
                TimerCard.work_date >= start_date,
                TimerCard.work_date <= end_date
            )
        )

    total = query.count()
    timercards = query.order_by(TimerCard.work_date.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "timercards": timercards
    }


@router.get("/{timercard_id}", response_model=TimerCardResponse)
async def get_timercard(
    timercard_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get timercard by ID"""
    timercard = db.query(TimerCard).filter(
        TimerCard.id == timercard_id,
        TimerCard.is_deleted == False
    ).first()

    if not timercard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TimerCard with ID {timercard_id} not found"
        )

    return timercard


@router.put("/{timercard_id}", response_model=TimerCardResponse)
async def update_timercard(
    timercard_id: int,
    timercard_update: TimerCardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update timercard information"""
    timercard = db.query(TimerCard).filter(
        TimerCard.id == timercard_id,
        TimerCard.is_deleted == False
    ).first()

    if not timercard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TimerCard with ID {timercard_id} not found"
        )

    # Update fields
    for field, value in timercard_update.dict(exclude_unset=True).items():
        setattr(timercard, field, value)

    try:
        db.commit()
        db.refresh(timercard)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return timercard


@router.delete("/{timercard_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_timercard(
    timercard_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Soft delete timercard"""
    timercard = db.query(TimerCard).filter(
        TimerCard.id == timercard_id,
        TimerCard.is_deleted == False
    ).first()

    if not timercard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TimerCard with ID {timercard_id} not found"
        )

    timercard.is_deleted = True

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return None


@router.post("/ocr")
async def process_timercard_ocr(
    file: UploadFile = File(...),
    employee_id: int = 0,
    month: int = 0,
    year: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Process OCR for monthly timercard PDF

    Accepts PDF file and extracts daily attendance records:
    - Work dates
    - Clock in/out times
    - Hours breakdown (regular, overtime, night, holiday)
    """
    if employee_id == 0 or month == 0 or year == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="employee_id, month, and year are required"
        )

    employee = db.query(Employee).filter(
        Employee.hakenmoto_id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with hakenmoto_id {employee_id} not found"
        )

    # Read file
    pdf_data = await file.read()

    # Process OCR
    ocr_service = OCRService()
    result = await ocr_service.process_image(pdf_data, document_type="timercard")

    if result.get("success"):
        # Extract timercard fields (implementation would parse daily records)
        return {
            "success": True,
            "message": "OCR processed successfully",
            "provider": result.get("provider"),
            "confidence": result.get("confidence"),
            "employee_id": employee_id,
            "month": month,
            "year": year,
            "extracted_records": [],  # TODO: Implement daily record extraction
            "note": "Daily record extraction not yet implemented"
        }
    else:
        return {
            "success": False,
            "message": result.get("error", "OCR processing failed"),
            "provider": result.get("provider")
        }
