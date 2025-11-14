"""
Employees API - CRUD operations + factory/apartment assignment

Endpoints:
- POST /employees - Create employee from candidate
- GET /employees - List all employees
- GET /employees/{hakenmoto_id} - Get employee details
- PUT /employees/{hakenmoto_id} - Update employee
- DELETE /employees/{hakenmoto_id} - Soft delete employee
- POST /employees/{hakenmoto_id}/assign-factory - Assign to factory/line
- POST /employees/{hakenmoto_id}/assign-apartment - Auto-assign or manual assign apartment
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_user
from app.models.models import User, Employee, Candidate, EmployeeStatus, Line
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    EmployeeListResponse,
    AssignFactoryRequest,
    AssignApartmentRequest
)
from app.services.apartment_service import ApartmentService

router = APIRouter()


@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create employee from candidate

    This should typically be called after a Nyusha request is approved,
    but can also be called directly.
    """
    # Verify candidate exists
    candidate = db.query(Candidate).filter(
        Candidate.rirekisho_id == employee.rirekisho_id
    ).first()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with rirekisho_id {employee.rirekisho_id} not found"
        )

    # Verify line exists
    line = db.query(Line).filter(Line.id == employee.line_id).first()
    if not line:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Line with id {employee.line_id} not found"
        )

    # Create employee copying relevant candidate data
    db_employee = Employee(
        rirekisho_id=employee.rirekisho_id,
        full_name_kanji=employee.full_name_kanji,
        full_name_kana=employee.full_name_kana,
        full_name_roman=candidate.full_name_roman,
        date_of_birth=candidate.date_of_birth,
        gender=candidate.gender,
        nationality=candidate.nationality,
        phone=candidate.phone,
        email=candidate.email,
        current_address=candidate.current_address,
        line_id=employee.line_id,
        jikyu=employee.jikyu,
        contract_type=employee.contract_type,
        hire_date=employee.hire_date,
        status=EmployeeStatus.ACTIVE
    )

    try:
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return db_employee


@router.get("/", response_model=EmployeeListResponse)
async def list_employees(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    line_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all employees with optional filtering"""
    query = db.query(Employee).filter(Employee.is_deleted == False)

    if status:
        try:
            status_enum = EmployeeStatus[status.upper()]
            query = query.filter(Employee.status == status_enum)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}"
            )

    if line_id:
        query = query.filter(Employee.line_id == line_id)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Employee.full_name_kanji.ilike(search_pattern)) |
            (Employee.full_name_kana.ilike(search_pattern)) |
            (Employee.rirekisho_id.ilike(search_pattern))
        )

    total = query.count()
    employees = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "employees": employees
    }


@router.get("/{hakenmoto_id}", response_model=EmployeeResponse)
async def get_employee(
    hakenmoto_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get employee by hakenmoto_id"""
    employee = db.query(Employee).filter(
        Employee.hakenmoto_id == hakenmoto_id,
        Employee.is_deleted == False
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with hakenmoto_id {hakenmoto_id} not found"
        )

    return employee


@router.put("/{hakenmoto_id}", response_model=EmployeeResponse)
async def update_employee(
    hakenmoto_id: int,
    employee_update: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update employee information"""
    employee = db.query(Employee).filter(
        Employee.hakenmoto_id == hakenmoto_id,
        Employee.is_deleted == False
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with hakenmoto_id {hakenmoto_id} not found"
        )

    # Update fields
    for field, value in employee_update.dict(exclude_unset=True).items():
        if field == "status" and value:
            try:
                status_enum = EmployeeStatus[value.upper()]
                setattr(employee, field, status_enum)
            except KeyError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {value}"
                )
        else:
            setattr(employee, field, value)

    try:
        db.commit()
        db.refresh(employee)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return employee


@router.delete("/{hakenmoto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    hakenmoto_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Soft delete employee"""
    employee = db.query(Employee).filter(
        Employee.hakenmoto_id == hakenmoto_id,
        Employee.is_deleted == False
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with hakenmoto_id {hakenmoto_id} not found"
        )

    employee.is_deleted = True
    employee.status = EmployeeStatus.RESIGNED

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return None


@router.post("/{hakenmoto_id}/assign-factory")
async def assign_factory(
    hakenmoto_id: int,
    request: AssignFactoryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Assign employee to factory/line"""
    employee = db.query(Employee).filter(
        Employee.hakenmoto_id == hakenmoto_id,
        Employee.is_deleted == False
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with hakenmoto_id {hakenmoto_id} not found"
        )

    # Verify line exists
    line = db.query(Line).filter(Line.id == request.line_id).first()
    if not line:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Line with id {request.line_id} not found"
        )

    employee.line_id = request.line_id

    try:
        db.commit()
        db.refresh(employee)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

    return {
        "success": True,
        "message": f"Employee assigned to line {line.name}",
        "employee": employee,
        "line": line
    }


@router.post("/{hakenmoto_id}/assign-apartment")
async def assign_apartment(
    hakenmoto_id: int,
    request: AssignApartmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Auto-assign or manually assign apartment to employee

    If apartment_id is None, uses ApartmentService to recommend best apartment.
    If apartment_id is provided, assigns that specific apartment.
    """
    employee = db.query(Employee).filter(
        Employee.hakenmoto_id == hakenmoto_id,
        Employee.is_deleted == False
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with hakenmoto_id {hakenmoto_id} not found"
        )

    apartment_service = ApartmentService(db)

    if request.apartment_id is None:
        # Auto-assign: get recommendations
        recommendations = apartment_service.recommend_apartments(employee, max_results=1)

        if not recommendations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No available apartments found for this employee"
            )

        best_apartment = recommendations[0]["apartment"]
        score = recommendations[0]["score"]

        employee.apartment_id = best_apartment.id

        try:
            db.commit()
            db.refresh(employee)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )

        return {
            "success": True,
            "message": "Employee auto-assigned to apartment",
            "assignment_type": "auto",
            "employee": employee,
            "apartment": best_apartment,
            "score": score,
            "score_breakdown": recommendations[0]
        }
    else:
        # Manual assignment
        from app.models.models import Apartment

        apartment = db.query(Apartment).filter(
            Apartment.id == request.apartment_id
        ).first()

        if not apartment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Apartment with id {request.apartment_id} not found"
            )

        if apartment.current_occupancy >= apartment.total_capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Apartment is at full capacity"
            )

        employee.apartment_id = apartment.id
        apartment.current_occupancy += 1

        try:
            db.commit()
            db.refresh(employee)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )

        return {
            "success": True,
            "message": "Employee manually assigned to apartment",
            "assignment_type": "manual",
            "employee": employee,
            "apartment": apartment
        }
