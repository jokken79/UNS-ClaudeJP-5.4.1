from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List, Optional
from datetime import datetime
import logging

from app.core.database import get_db
from app.models.models import Apartment, Employee, User
from app.services.auth_service import auth_service
from app.schemas.apartment import (
    ApartmentCreate,
    ApartmentUpdate,
    ApartmentResponse,
    ApartmentWithEmployees,
    ApartmentStats,
    EmployeeAssignment,
    EmployeeBasic
)

# Logger for deprecation warnings
logger = logging.getLogger(__name__)

# DEPRECATED: This API V1 will be removed on 2025-12-31
# Please migrate to /api/apartments-v2 (apartments_v2.py)
router = APIRouter(tags=["apartments-v1-deprecated"])


# Helper function to calculate occupancy status
def calculate_apartment_status(employees_count: int, capacity: int) -> tuple[float, str]:
    """Calculate occupancy rate and status"""
    if capacity == 0:
        return 0.0, "disponible"

    occupancy_rate = (employees_count / capacity) * 100

    if employees_count == 0:
        status = "disponible"
    elif employees_count < capacity:
        status = "parcial"
    else:
        status = "lleno"

    return occupancy_rate, status


@router.get("/", response_model=List[ApartmentResponse])
async def get_apartments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    available_only: bool = Query(False, description="Mostrar solo apartamentos disponibles"),
    search: Optional[str] = Query(None, description="Buscar por código o dirección"),
    min_capacity: Optional[int] = Query(None, ge=1, description="Capacidad mínima"),
    max_rent: Optional[int] = Query(None, ge=0, description="Renta máxima"),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_active_user)
):
    """
    DEPRECATED: This API will be removed on 2025-12-31.

    Use GET /api/apartments-v2/apartments instead.

    **Migration Guide:**
    - New endpoint: GET /api/apartments-v2/apartments
    - Enhanced features: pagination, advanced filters, statistics
    - Full documentation at /api/docs#/Apartments%20V2

    Obtener lista de apartamentos con filtros.

    Requiere autenticación.
    """
    logger.warning(
        "DEPRECATED API V1 called: GET /api/apartments/ - "
        "Please migrate to /api/apartments-v2/apartments (will be removed 2025-12-31)"
    )

    # Base query with employee count
    query = db.query(
        Apartment,
        func.count(Employee.id).label('employees_count')
    ).outerjoin(
        Employee,
        (Employee.apartment_id == Apartment.id) & (Employee.is_active == True)
    ).group_by(Apartment.id)

    # Apply filters
    if available_only:
        query = query.having(func.count(Employee.id) < Apartment.capacity)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Apartment.apartment_code.ilike(search_pattern)) |
            (Apartment.address.ilike(search_pattern))
        )

    if min_capacity:
        query = query.filter(Apartment.capacity >= min_capacity)

    if max_rent:
        query = query.filter(Apartment.monthly_rent <= max_rent)

    # Execute query
    results = query.offset(skip).limit(limit).all()

    # Build response with calculated fields
    apartments = []
    for apartment, employees_count in results:
        occupancy_rate, status = calculate_apartment_status(employees_count, apartment.capacity or 0)

        apt_dict = {
            "id": apartment.id,
            "apartment_code": apartment.apartment_code,
            "address": apartment.address,
            "monthly_rent": apartment.monthly_rent,
            "capacity": apartment.capacity,
            "is_available": apartment.is_available,
            "notes": apartment.notes,
            "created_at": apartment.created_at,
            "employees_count": employees_count,
            "occupancy_rate": round(occupancy_rate, 2),
            "status": status
        }
        apartments.append(ApartmentResponse(**apt_dict))

    return apartments


@router.get("/stats", response_model=ApartmentStats)
async def get_apartment_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_active_user)
):
    """
    DEPRECATED: This API will be removed on 2025-12-31.

    Use GET /api/apartments-v2/reports/occupancy instead.

    **Migration Guide:**
    - New endpoint: GET /api/apartments-v2/reports/occupancy
    - More comprehensive statistics and breakdowns
    - Full documentation at /api/docs#/Apartments%20V2

    Obtener estadísticas globales de apartamentos.

    Requiere autenticación.
    """
    logger.warning(
        "DEPRECATED API V1 called: GET /api/apartments/stats - "
        "Please migrate to /api/apartments-v2/reports/occupancy (will be removed 2025-12-31)"
    )

    # Total apartments and capacity
    total_apartments = db.query(func.count(Apartment.id)).scalar() or 0
    total_capacity = db.query(func.sum(Apartment.capacity)).scalar() or 0

    # Occupied apartments and employee count
    occupied_query = db.query(
        func.count(func.distinct(Employee.apartment_id)).label('apartments_occupied'),
        func.count(Employee.id).label('total_employees')
    ).filter(
        Employee.is_active == True,
        Employee.apartment_id.isnot(None)
    ).first()

    apartments_occupied = occupied_query.apartments_occupied or 0
    total_employees_assigned = occupied_query.total_employees or 0

    # Full apartments (capacity reached)
    apartments_full = db.query(func.count(Apartment.id)).select_from(
        Apartment
    ).outerjoin(
        Employee,
        (Employee.apartment_id == Apartment.id) & (Employee.is_active == True)
    ).group_by(Apartment.id).having(
        func.count(Employee.id) >= Apartment.capacity
    ).count()

    # Available apartments
    apartments_available = total_apartments - apartments_occupied

    # Calculate occupancy percentage
    occupancy_percentage = (total_employees_assigned / total_capacity * 100) if total_capacity > 0 else 0

    # Total and average rent
    total_monthly_rent = db.query(func.sum(Apartment.monthly_rent)).scalar() or 0
    average_rent = total_monthly_rent / total_apartments if total_apartments > 0 else 0

    return ApartmentStats(
        total_apartments=total_apartments,
        total_capacity=total_capacity,
        apartments_occupied=apartments_occupied,
        apartments_available=apartments_available,
        apartments_full=apartments_full,
        total_employees_assigned=total_employees_assigned,
        occupancy_percentage=round(occupancy_percentage, 2),
        total_monthly_rent=total_monthly_rent,
        average_rent=round(average_rent, 2)
    )


@router.get("/{apartment_id}", response_model=ApartmentWithEmployees)
async def get_apartment(
    apartment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_active_user)
):
    """
    DEPRECATED: This API will be removed on 2025-12-31.

    Use GET /api/apartments-v2/apartments/{apartment_id} instead.

    **Migration Guide:**
    - New endpoint: GET /api/apartments-v2/apartments/{apartment_id}
    - Enhanced details with assignment history and statistics
    - Full documentation at /api/docs#/Apartments%20V2

    Obtener detalles de un apartamento específico con empleados asignados.

    Requiere autenticación.
    """
    logger.warning(
        f"DEPRECATED API V1 called: GET /api/apartments/{apartment_id} - "
        f"Please migrate to /api/apartments-v2/apartments/{apartment_id} (will be removed 2025-12-31)"
    )

    # Get apartment
    apartment = db.query(Apartment).filter(Apartment.id == apartment_id).first()
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartamento no encontrado")

    # Get employees assigned to this apartment
    employees = db.query(Employee).filter(
        Employee.apartment_id == apartment_id,
        Employee.is_active == True
    ).all()

    # Calculate occupancy
    employees_count = len(employees)
    occupancy_rate, status = calculate_apartment_status(employees_count, apartment.capacity or 0)

    # Build response
    apt_dict = {
        "id": apartment.id,
        "apartment_code": apartment.apartment_code,
        "address": apartment.address,
        "monthly_rent": apartment.monthly_rent,
        "capacity": apartment.capacity,
        "is_available": apartment.is_available,
        "notes": apartment.notes,
        "created_at": apartment.created_at,
        "employees_count": employees_count,
        "occupancy_rate": round(occupancy_rate, 2),
        "status": status,
        "employees": [
            EmployeeBasic(
                id=emp.id,
                hakenmoto_id=emp.hakenmoto_id,
                full_name_kanji=emp.full_name_kanji,
                full_name_kana=emp.full_name_kana,
                phone=emp.phone,
                apartment_start_date=emp.apartment_start_date
            ) for emp in employees
        ]
    }

    return ApartmentWithEmployees(**apt_dict)


@router.post("/", response_model=ApartmentResponse, status_code=201)
async def create_apartment(
    apartment: ApartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_active_user)
):
    """
    DEPRECATED: This API will be removed on 2025-12-31.

    Use POST /api/apartments-v2/apartments instead.

    **Migration Guide:**
    - New endpoint: POST /api/apartments-v2/apartments
    - Enhanced validation and additional fields
    - Full documentation at /api/docs#/Apartments%20V2

    Crear un nuevo apartamento.

    Requiere autenticación.
    """
    logger.warning(
        "DEPRECATED API V1 called: POST /api/apartments/ - "
        "Please migrate to /api/apartments-v2/apartments (will be removed 2025-12-31)"
    )

    # Check if apartment code already exists
    existing = db.query(Apartment).filter(
        Apartment.apartment_code == apartment.apartment_code
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe un apartamento con el código '{apartment.apartment_code}'"
        )

    # Create new apartment
    db_apartment = Apartment(**apartment.model_dump())
    db.add(db_apartment)
    db.commit()
    db.refresh(db_apartment)

    # Return with calculated fields
    return ApartmentResponse(
        id=db_apartment.id,
        apartment_code=db_apartment.apartment_code,
        address=db_apartment.address,
        monthly_rent=db_apartment.monthly_rent,
        capacity=db_apartment.capacity,
        is_available=db_apartment.is_available,
        notes=db_apartment.notes,
        created_at=db_apartment.created_at,
        employees_count=0,
        occupancy_rate=0.0,
        status="disponible"
    )


@router.put("/{apartment_id}", response_model=ApartmentResponse)
async def update_apartment(
    apartment_id: int,
    apartment: ApartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_active_user)
):
    """
    DEPRECATED: This API will be removed on 2025-12-31.

    Use PUT /api/apartments-v2/apartments/{apartment_id} instead.

    **Migration Guide:**
    - New endpoint: PUT /api/apartments-v2/apartments/{apartment_id}
    - Enhanced validation and additional fields
    - Full documentation at /api/docs#/Apartments%20V2

    Actualizar un apartamento existente.

    Requiere autenticación.
    """
    logger.warning(
        f"DEPRECATED API V1 called: PUT /api/apartments/{apartment_id} - "
        f"Please migrate to /api/apartments-v2/apartments/{apartment_id} (will be removed 2025-12-31)"
    )

    # Get existing apartment
    db_apartment = db.query(Apartment).filter(Apartment.id == apartment_id).first()
    if not db_apartment:
        raise HTTPException(status_code=404, detail="Apartamento no encontrado")

    # Check if new apartment code already exists
    if apartment.apartment_code and apartment.apartment_code != db_apartment.apartment_code:
        existing = db.query(Apartment).filter(
            Apartment.apartment_code == apartment.apartment_code
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe un apartamento con el código '{apartment.apartment_code}'"
            )

    # Update fields
    update_data = apartment.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_apartment, field, value)

    db.commit()
    db.refresh(db_apartment)

    # Get employee count for response
    employees_count = db.query(func.count(Employee.id)).filter(
        Employee.apartment_id == apartment_id,
        Employee.is_active == True
    ).scalar() or 0

    occupancy_rate, status = calculate_apartment_status(employees_count, db_apartment.capacity or 0)

    return ApartmentResponse(
        id=db_apartment.id,
        apartment_code=db_apartment.apartment_code,
        address=db_apartment.address,
        monthly_rent=db_apartment.monthly_rent,
        capacity=db_apartment.capacity,
        is_available=db_apartment.is_available,
        notes=db_apartment.notes,
        created_at=db_apartment.created_at,
        employees_count=employees_count,
        occupancy_rate=round(occupancy_rate, 2),
        status=status
    )


@router.delete("/{apartment_id}", status_code=204)
async def delete_apartment(
    apartment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_active_user)
):
    """
    DEPRECATED: This API will be removed on 2025-12-31.

    Use DELETE /api/apartments-v2/apartments/{apartment_id} instead.

    **Migration Guide:**
    - New endpoint: DELETE /api/apartments-v2/apartments/{apartment_id}
    - Enhanced soft-delete with better validation
    - Full documentation at /api/docs#/Apartments%20V2

    Eliminar un apartamento.

    Solo se puede eliminar si no tiene empleados asignados.
    Requiere autenticación.
    """
    logger.warning(
        f"DEPRECATED API V1 called: DELETE /api/apartments/{apartment_id} - "
        f"Please migrate to /api/apartments-v2/apartments/{apartment_id} (will be removed 2025-12-31)"
    )

    # Get apartment
    db_apartment = db.query(Apartment).filter(Apartment.id == apartment_id).first()
    if not db_apartment:
        raise HTTPException(status_code=404, detail="Apartamento no encontrado")

    # Check if has assigned employees
    employees_count = db.query(func.count(Employee.id)).filter(
        Employee.apartment_id == apartment_id,
        Employee.is_active == True
    ).scalar() or 0

    if employees_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede eliminar el apartamento porque tiene {employees_count} empleado(s) asignado(s). Primero remueve los empleados."
        )

    # Delete apartment
    db.delete(db_apartment)
    db.commit()

    return None


@router.post("/{apartment_id}/assign", response_model=dict)
async def assign_employee_to_apartment(
    apartment_id: int,
    assignment: EmployeeAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_active_user)
):
    """
    DEPRECATED: This API will be removed on 2025-12-31.

    Use POST /api/apartments-v2/assignments instead.

    **Migration Guide:**
    - New endpoint: POST /api/apartments-v2/assignments
    - Enhanced assignment with prorated rent calculations
    - Automatic deduction generation
    - Full documentation at /api/docs#/Apartments%20V2

    Asignar un empleado a un apartamento.

    Verifica capacidad antes de asignar.
    Requiere autenticación.
    """
    logger.warning(
        f"DEPRECATED API V1 called: POST /api/apartments/{apartment_id}/assign - "
        "Please migrate to /api/apartments-v2/assignments (will be removed 2025-12-31)"
    )

    # Get apartment
    apartment = db.query(Apartment).filter(Apartment.id == apartment_id).first()
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartamento no encontrado")

    # Get employee
    employee = db.query(Employee).filter(Employee.id == assignment.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    # Check if employee is active
    if not employee.is_active:
        raise HTTPException(status_code=400, detail="El empleado no está activo")

    # Check capacity
    current_employees = db.query(func.count(Employee.id)).filter(
        Employee.apartment_id == apartment_id,
        Employee.is_active == True
    ).scalar() or 0

    if current_employees >= (apartment.capacity or 0):
        raise HTTPException(
            status_code=400,
            detail=f"El apartamento ha alcanzado su capacidad máxima ({apartment.capacity})"
        )

    # Assign apartment
    employee.apartment_id = apartment_id
    employee.apartment_start_date = assignment.start_date or datetime.now()
    if assignment.rent_amount:
        employee.apartment_rent = assignment.rent_amount
    else:
        employee.apartment_rent = apartment.monthly_rent

    db.commit()

    return {
        "message": f"Empleado {employee.full_name_kanji} asignado exitosamente al apartamento {apartment.apartment_code}",
        "employee_id": employee.id,
        "apartment_id": apartment.id
    }


@router.post("/{apartment_id}/remove", response_model=dict)
async def remove_employee_from_apartment(
    apartment_id: int,
    assignment: EmployeeAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_active_user)
):
    """
    DEPRECATED: This API will be removed on 2025-12-31.

    Use PUT /api/apartments-v2/assignments/{assignment_id}/end instead.

    **Migration Guide:**
    - New endpoint: PUT /api/apartments-v2/assignments/{assignment_id}/end
    - Enhanced with prorated rent, cleaning fees, and final deduction calculation
    - Full documentation at /api/docs#/Apartments%20V2

    Remover un empleado de un apartamento.

    Requiere autenticación.
    """
    logger.warning(
        f"DEPRECATED API V1 called: POST /api/apartments/{apartment_id}/remove - "
        "Please migrate to /api/apartments-v2/assignments/{{id}}/end (will be removed 2025-12-31)"
    )

    # Get employee
    employee = db.query(Employee).filter(Employee.id == assignment.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    # Verify employee is assigned to this apartment
    if employee.apartment_id != apartment_id:
        raise HTTPException(
            status_code=400,
            detail="El empleado no está asignado a este apartamento"
        )

    # Remove assignment
    employee.apartment_id = None
    employee.apartment_move_out_date = assignment.end_date or datetime.now()

    db.commit()

    return {
        "message": f"Empleado {employee.full_name_kanji} removido exitosamente del apartamento",
        "employee_id": employee.id,
        "apartment_id": apartment_id
    }


@router.get("/{apartment_id}/employees", response_model=List[EmployeeBasic])
async def get_apartment_employees(
    apartment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_active_user)
):
    """
    DEPRECATED: This API will be removed on 2025-12-31.

    Use GET /api/apartments-v2/assignments/apartment/{apartment_id}/active instead.

    **Migration Guide:**
    - New endpoint: GET /api/apartments-v2/assignments/apartment/{apartment_id}/active
    - Enhanced with assignment details and rent information
    - Full documentation at /api/docs#/Apartments%20V2

    Obtener lista de empleados asignados a un apartamento.

    Requiere autenticación.
    """
    logger.warning(
        f"DEPRECATED API V1 called: GET /api/apartments/{apartment_id}/employees - "
        f"Please migrate to /api/apartments-v2/assignments/apartment/{apartment_id}/active (will be removed 2025-12-31)"
    )

    # Verify apartment exists
    apartment = db.query(Apartment).filter(Apartment.id == apartment_id).first()
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartamento no encontrado")

    # Get employees
    employees = db.query(Employee).filter(
        Employee.apartment_id == apartment_id,
        Employee.is_active == True
    ).all()

    return [
        EmployeeBasic(
            id=emp.id,
            hakenmoto_id=emp.hakenmoto_id,
            full_name_kanji=emp.full_name_kanji,
            full_name_kana=emp.full_name_kana,
            phone=emp.phone,
            apartment_start_date=emp.apartment_start_date
        ) for emp in employees
    ]
