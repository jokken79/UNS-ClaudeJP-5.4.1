"""
Candidates API - CRUD operations + OCR processing

Endpoints:
- POST /candidates - Create candidate
- GET /candidates - List all candidates
- GET /candidates/{rirekisho_id} - Get candidate details
- PUT /candidates/{rirekisho_id} - Update candidate
- DELETE /candidates/{rirekisho_id} - Delete candidate
- POST /candidates/{rirekisho_id}/ocr - Process OCR for candidate document
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_user
from app.models.models import User, Candidate, CandidateStatus
from app.schemas.candidate import (
    CandidateCreate,
    CandidateUpdate,
    CandidateResponse,
    CandidateListResponse
)
from app.services.ocr_service import OCRService

router = APIRouter()


@router.post("/", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    candidate: CandidateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new candidate"""
    # Check if rirekisho_id already exists
    existing = db.query(Candidate).filter(
        Candidate.rirekisho_id == candidate.rirekisho_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Candidate with rirekisho_id {candidate.rirekisho_id} already exists"
        )

    db_candidate = Candidate(**candidate.dict())
    db_candidate.status = CandidateStatus.PENDING

    try:
        db.add(db_candidate)
        db.commit()
        db.refresh(db_candidate)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return db_candidate


@router.get("/", response_model=CandidateListResponse)
async def list_candidates(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all candidates with optional filtering"""
    query = db.query(Candidate).filter(Candidate.is_deleted == False)

    if status:
        try:
            status_enum = CandidateStatus[status.upper()]
            query = query.filter(Candidate.status == status_enum)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}"
            )

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Candidate.full_name_kanji.ilike(search_pattern)) |
            (Candidate.full_name_kana.ilike(search_pattern)) |
            (Candidate.rirekisho_id.ilike(search_pattern))
        )

    total = query.count()
    candidates = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "candidates": candidates
    }


@router.get("/{rirekisho_id}", response_model=CandidateResponse)
async def get_candidate(
    rirekisho_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get candidate by rirekisho_id"""
    candidate = db.query(Candidate).filter(
        Candidate.rirekisho_id == rirekisho_id,
        Candidate.is_deleted == False
    ).first()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with rirekisho_id {rirekisho_id} not found"
        )

    return candidate


@router.put("/{rirekisho_id}", response_model=CandidateResponse)
async def update_candidate(
    rirekisho_id: str,
    candidate_update: CandidateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update candidate information"""
    candidate = db.query(Candidate).filter(
        Candidate.rirekisho_id == rirekisho_id,
        Candidate.is_deleted == False
    ).first()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with rirekisho_id {rirekisho_id} not found"
        )

    # Update fields
    for field, value in candidate_update.dict(exclude_unset=True).items():
        if field == "status" and value:
            try:
                status_enum = CandidateStatus[value.upper()]
                setattr(candidate, field, status_enum)
            except KeyError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {value}"
                )
        else:
            setattr(candidate, field, value)

    try:
        db.commit()
        db.refresh(candidate)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return candidate


@router.delete("/{rirekisho_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate(
    rirekisho_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Soft delete candidate"""
    candidate = db.query(Candidate).filter(
        Candidate.rirekisho_id == rirekisho_id,
        Candidate.is_deleted == False
    ).first()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with rirekisho_id {rirekisho_id} not found"
        )

    candidate.is_deleted = True

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return None


@router.post("/{rirekisho_id}/ocr")
async def process_candidate_ocr(
    rirekisho_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Process OCR for candidate resume (履歴書)

    Accepts image files (JPG, PNG, PDF) and extracts:
    - Name (kanji, kana, roman)
    - Date of birth
    - Phone number
    - Email address
    - Current address
    """
    candidate = db.query(Candidate).filter(
        Candidate.rirekisho_id == rirekisho_id,
        Candidate.is_deleted == False
    ).first()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with rirekisho_id {rirekisho_id} not found"
        )

    # Read file
    image_data = await file.read()

    # Process OCR
    ocr_service = OCRService()
    result = await ocr_service.process_image(image_data, document_type="rirekisho")

    if result.get("success"):
        # Extract fields
        fields = ocr_service.extract_rirekisho_fields(result)

        # Update candidate with OCR data
        for field, value in fields.items():
            if value and hasattr(candidate, field):
                # Only update if field is empty
                current_value = getattr(candidate, field)
                if not current_value:
                    setattr(candidate, field, value)

        candidate.ocr_data = result

        try:
            db.commit()
            db.refresh(candidate)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )

        return {
            "success": True,
            "message": "OCR processed successfully",
            "provider": result.get("provider"),
            "confidence": result.get("confidence"),
            "extracted_fields": fields,
            "candidate": candidate
        }
    else:
        return {
            "success": False,
            "message": result.get("error", "OCR processing failed"),
            "provider": result.get("provider"),
            "candidate": candidate
        }
