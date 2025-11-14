"""
Apartments API - CRUD operations + intelligent assignment

Endpoints:
- POST /apartments - Create apartment
- GET /apartments - List all apartments
- GET /apartments/{id} - Get apartment details
- PUT /apartments/{id} - Update apartment
- DELETE /apartments/{id} - Soft delete apartment
- GET /apartments/recommend/{employee_id} - Get smart recommendations
- POST /apartments/{id}/assign/{employee_id} - Assign apartment to employee
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_user
from app.models.models import User, Apartment, Employee
from app.schemas.apartment import (
    ApartmentCreate,
    ApartmentUpdate,
    ApartmentResponse,
    ApartmentListResponse,
    ApartmentRecommendationResponse
)
from app.services.apartment_service import ApartmentService

router = APIRouter()


@router.post("/", response_model=ApartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_apartment(
    apartment: ApartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new apartment"""
    db_apartment = Apartment(**apartment.dict())
    db_apartment.current_occupancy = 0
    db_apartment.is_available = True

    try:
        db.add(db_apartment)
        db.commit()
        db.refresh(db_apartment)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return db_apartment


@router.get("/", response_model=ApartmentListResponse)
async def list_apartments(
    skip: int = 0,
    limit: int = 100,
    available_only: bool = False,
    min_capacity: Optional[int] = None,
    max_rent: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all apartments with optional filtering"""
    query = db.query(Apartment).filter(Apartment.is_deleted == False)

    if available_only:
        query = query.filter(
            Apartment.is_available == True,
            Apartment.current_occupancy < Apartment.total_capacity
        )

    if min_capacity:
        query = query.filter(Apartment.total_capacity >= min_capacity)

    if max_rent:
        query = query.filter(Apartment.monthly_rent <= max_rent)

    total = query.count()
    apartments = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "apartments": apartments
    }


@router.get("/{apartment_id}", response_model=ApartmentResponse)
async def get_apartment(
    apartment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get apartment by ID"""
    apartment = db.query(Apartment).filter(
        Apartment.id == apartment_id,
        Apartment.is_deleted == False
    ).first()

    if not apartment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Apartment with id {apartment_id} not found"
        )

    return apartment


@router.put("/{apartment_id}", response_model=ApartmentResponse)
async def update_apartment(
    apartment_id: int,
    apartment_update: ApartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update apartment information"""
    apartment = db.query(Apartment).filter(
        Apartment.id == apartment_id,
        Apartment.is_deleted == False
    ).first()

    if not apartment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Apartment with id {apartment_id} not found"
        )

    for field, value in apartment_update.dict(exclude_unset=True).items():
        setattr(apartment, field, value)

    try:
        db.commit()
        db.refresh(apartment)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return apartment


@router.delete("/{apartment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_apartment(
    apartment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Soft delete apartment"""
    apartment = db.query(Apartment).filter(
        Apartment.id == apartment_id,
        Apartment.is_deleted == False
    ).first()

    if not apartment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Apartment with id {apartment_id} not found"
        )

    apartment.is_deleted = True
    apartment.is_available = False

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return None


@router.get("/recommend/{employee_id}", response_model=ApartmentRecommendationResponse)
async def recommend_apartments(
    employee_id: int,
    max_results: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get smart apartment recommendations for employee

    Uses weighted scoring algorithm:
    - 40% Proximity to factory
    - 25% Availability
    - 15% Price affordability
    - 10% Roommate compatibility
    - 10% Transportation access
    """
    employee = db.query(Employee).filter(
        Employee.hakenmoto_id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with hakenmoto_id {employee_id} not found"
        )

    apartment_service = ApartmentService(db)
    recommendations = apartment_service.recommend_apartments(employee, max_results=max_results)

    if not recommendations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No available apartments found matching criteria"
        )

    # Format response
    formatted_recommendations = []
    for rec in recommendations:
        formatted_recommendations.append({
            "apartment": rec["apartment"],
            "score": rec["score"],
            "proximity_score": rec["scores"]["proximity"],
            "availability_score": rec["scores"]["availability"],
            "price_score": rec["scores"]["price"],
            "compatibility_score": rec["scores"]["compatibility"],
            "transportation_score": rec["scores"]["transportation"]
        })

    return {
        "employee_id": employee_id,
        "recommendations": formatted_recommendations
    }


@router.post("/{apartment_id}/assign/{employee_id}")
async def assign_apartment_to_employee(
    apartment_id: int,
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Assign apartment to employee"""
    apartment = db.query(Apartment).filter(
        Apartment.id == apartment_id,
        Apartment.is_deleted == False
    ).first()

    if not apartment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Apartment with id {apartment_id} not found"
        )

    employee = db.query(Employee).filter(
        Employee.hakenmoto_id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with hakenmoto_id {employee_id} not found"
        )

    if apartment.current_occupancy >= apartment.total_capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apartment is at full capacity"
        )

    # Remove from old apartment if exists
    if employee.apartment_id:
        old_apartment = db.query(Apartment).filter(
            Apartment.id == employee.apartment_id
        ).first()
        if old_apartment:
            old_apartment.current_occupancy = max(0, old_apartment.current_occupancy - 1)

    # Assign to new apartment
    employee.apartment_id = apartment_id
    apartment.current_occupancy += 1

    try:
        db.commit()
        db.refresh(employee)
        db.refresh(apartment)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return {
        "success": True,
        "message": f"Employee {employee.full_name_kanji} assigned to apartment {apartment.name}",
        "employee": employee,
        "apartment": apartment
    }
