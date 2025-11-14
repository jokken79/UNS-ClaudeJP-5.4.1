"""
Companies API - CRUD operations

Endpoints:
- POST /companies - Create company
- GET /companies - List all companies
- GET /companies/{id} - Get company details
- PUT /companies/{id} - Update company
- DELETE /companies/{id} - Delete company
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_user
from app.models.models import User, Company
from app.schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyListResponse
)

router = APIRouter()


@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new company"""
    # Check if company name already exists
    existing = db.query(Company).filter(
        Company.name == company.name
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Company with name '{company.name}' already exists"
        )

    db_company = Company(**company.dict())

    try:
        db.add(db_company)
        db.commit()
        db.refresh(db_company)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return db_company


@router.get("/", response_model=CompanyListResponse)
async def list_companies(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all companies with optional filtering"""
    query = db.query(Company)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Company.name.ilike(search_pattern)) |
            (Company.name_kana.ilike(search_pattern))
        )

    total = query.count()
    companies = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "companies": companies
    }


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get company by ID"""
    company = db.query(Company).filter(
        Company.id == company_id
    ).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {company_id} not found"
        )

    return company


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_update: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update company information"""
    company = db.query(Company).filter(
        Company.id == company_id
    ).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {company_id} not found"
        )

    # Check if new name conflicts with another company
    if company_update.name and company_update.name != company.name:
        existing = db.query(Company).filter(
            Company.name == company_update.name
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Company with name '{company_update.name}' already exists"
            )

    # Update fields
    for field, value in company_update.dict(exclude_unset=True).items():
        setattr(company, field, value)

    try:
        db.commit()
        db.refresh(company)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete company (hard delete)"""
    company = db.query(Company).filter(
        Company.id == company_id
    ).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {company_id} not found"
        )

    # Check if company has plants
    from app.models.models import Plant
    plants = db.query(Plant).filter(Plant.company_id == company_id).count()
    if plants > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete company: {plants} plant(s) still reference this company"
        )

    try:
        db.delete(company)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return None
