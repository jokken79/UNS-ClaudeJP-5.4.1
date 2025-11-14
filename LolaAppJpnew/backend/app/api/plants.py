"""
Plants API - CRUD operations

Endpoints:
- POST /plants - Create plant
- GET /plants - List all plants
- GET /plants/{id} - Get plant details
- PUT /plants/{id} - Update plant
- DELETE /plants/{id} - Delete plant
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_user
from app.models.models import User, Plant, Company
from app.schemas.plant import (
    PlantCreate,
    PlantUpdate,
    PlantResponse,
    PlantListResponse
)

router = APIRouter()


@router.post("/", response_model=PlantResponse, status_code=status.HTTP_201_CREATED)
async def create_plant(
    plant: PlantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new plant"""
    # Verify company exists
    company = db.query(Company).filter(
        Company.id == plant.company_id
    ).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {plant.company_id} not found"
        )

    # Validate coordinates
    if plant.latitude is not None and (plant.latitude < -90 or plant.latitude > 90):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Latitude must be between -90 and 90"
        )

    if plant.longitude is not None and (plant.longitude < -180 or plant.longitude > 180):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Longitude must be between -180 and 180"
        )

    db_plant = Plant(**plant.dict())

    try:
        db.add(db_plant)
        db.commit()
        db.refresh(db_plant)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return db_plant


@router.get("/", response_model=PlantListResponse)
async def list_plants(
    skip: int = 0,
    limit: int = 100,
    company_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all plants with optional filtering"""
    query = db.query(Plant)

    if company_id:
        query = query.filter(Plant.company_id == company_id)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Plant.name.ilike(search_pattern)) |
            (Plant.address.ilike(search_pattern))
        )

    total = query.count()
    plants = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "plants": plants
    }


@router.get("/{plant_id}", response_model=PlantResponse)
async def get_plant(
    plant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get plant by ID"""
    plant = db.query(Plant).filter(
        Plant.id == plant_id
    ).first()

    if not plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plant with ID {plant_id} not found"
        )

    return plant


@router.put("/{plant_id}", response_model=PlantResponse)
async def update_plant(
    plant_id: int,
    plant_update: PlantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update plant information"""
    plant = db.query(Plant).filter(
        Plant.id == plant_id
    ).first()

    if not plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plant with ID {plant_id} not found"
        )

    # Verify new company exists if company_id is being changed
    if plant_update.company_id and plant_update.company_id != plant.company_id:
        company = db.query(Company).filter(
            Company.id == plant_update.company_id
        ).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with ID {plant_update.company_id} not found"
            )

    # Validate coordinates
    if plant_update.latitude is not None and (plant_update.latitude < -90 or plant_update.latitude > 90):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Latitude must be between -90 and 90"
        )

    if plant_update.longitude is not None and (plant_update.longitude < -180 or plant_update.longitude > 180):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Longitude must be between -180 and 180"
        )

    # Update fields
    for field, value in plant_update.dict(exclude_unset=True).items():
        setattr(plant, field, value)

    try:
        db.commit()
        db.refresh(plant)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return plant


@router.delete("/{plant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plant(
    plant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete plant (hard delete)"""
    plant = db.query(Plant).filter(
        Plant.id == plant_id
    ).first()

    if not plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plant with ID {plant_id} not found"
        )

    # Check if plant has lines
    from app.models.models import Line
    lines = db.query(Line).filter(Line.plant_id == plant_id).count()
    if lines > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete plant: {lines} line(s) still reference this plant"
        )

    try:
        db.delete(plant)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return None
