"""
Lines API - CRUD operations

Endpoints:
- POST /lines - Create line
- GET /lines - List all lines
- GET /lines/{id} - Get line details
- PUT /lines/{id} - Update line
- DELETE /lines/{id} - Delete line
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_user
from app.models.models import User, Line, Plant
from app.schemas.line import (
    LineCreate,
    LineUpdate,
    LineResponse,
    LineListResponse
)

router = APIRouter()


@router.post("/", response_model=LineResponse, status_code=status.HTTP_201_CREATED)
async def create_line(
    line: LineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new production line"""
    # Verify plant exists
    plant = db.query(Plant).filter(
        Plant.id == line.plant_id
    ).first()

    if not plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plant with ID {line.plant_id} not found"
        )

    db_line = Line(**line.dict())

    try:
        db.add(db_line)
        db.commit()
        db.refresh(db_line)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return db_line


@router.get("/", response_model=LineListResponse)
async def list_lines(
    skip: int = 0,
    limit: int = 100,
    plant_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all production lines with optional filtering"""
    query = db.query(Line).filter(Line.is_deleted == False)

    if plant_id:
        query = query.filter(Line.plant_id == plant_id)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Line.name.ilike(search_pattern)) |
            (Line.line_number.ilike(search_pattern)) |
            (Line.description.ilike(search_pattern))
        )

    total = query.count()
    lines = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "lines": lines
    }


@router.get("/{line_id}", response_model=LineResponse)
async def get_line(
    line_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get production line by ID"""
    line = db.query(Line).filter(
        Line.id == line_id,
        Line.is_deleted == False
    ).first()

    if not line:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Line with ID {line_id} not found"
        )

    return line


@router.put("/{line_id}", response_model=LineResponse)
async def update_line(
    line_id: int,
    line_update: LineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update production line information"""
    line = db.query(Line).filter(
        Line.id == line_id,
        Line.is_deleted == False
    ).first()

    if not line:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Line with ID {line_id} not found"
        )

    # Verify new plant exists if plant_id is being changed
    if line_update.plant_id and line_update.plant_id != line.plant_id:
        plant = db.query(Plant).filter(
            Plant.id == line_update.plant_id
        ).first()
        if not plant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plant with ID {line_update.plant_id} not found"
            )

    # Update fields
    for field, value in line_update.dict(exclude_unset=True).items():
        setattr(line, field, value)

    try:
        db.commit()
        db.refresh(line)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return line


@router.delete("/{line_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_line(
    line_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Soft delete production line"""
    line = db.query(Line).filter(
        Line.id == line_id,
        Line.is_deleted == False
    ).first()

    if not line:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Line with ID {line_id} not found"
        )

    # Check if line has employees
    from app.models.models import Employee
    employees = db.query(Employee).filter(
        Employee.line_id == line_id,
        Employee.is_deleted == False
    ).count()

    if employees > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete line: {employees} employee(s) still assigned to this line"
        )

    line.is_deleted = True

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return None
