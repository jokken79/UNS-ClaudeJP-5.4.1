"""
Servicio de Asignaciones V2.0
=============================

Servicio para gestión de asignaciones empleado-apartamento (社宅) con:
- Crear/actualizar/finalizar asignaciones
- Cálculo de renta prorrateada
- Transferencias entre apartamentos
- Integración con cargos adicionales y deducciones

Autor: Sistema UNS-ClaudeJP
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Tuple
from datetime import datetime, date
import calendar
from decimal import Decimal

from app.models.models import (
    Apartment,
    ApartmentAssignment,
    Employee,
    User,
    AssignmentStatus,
)
from app.schemas.apartment_v2 import (
    AssignmentCreate,
    AssignmentResponse,
    AssignmentUpdate,
    AssignmentListItem,
    TransferRequest,
    TransferResponse,
    ProratedCalculationRequest,
    ProratedCalculationResponse,
    TotalCalculationRequest,
    TotalCalculationResponse,
    AssignmentStatus,
)


class AssignmentService:
    """Servicio para operaciones de asignaciones"""

    def __init__(self, db: Session):
        self.db = db

    # -------------------------------------------------------------------------
    # GESTIÓN DE ASIGNACIONES
    # -------------------------------------------------------------------------

    async def create_assignment(
        self,
        assignment: AssignmentCreate,
        user_id: int,
    ) -> AssignmentResponse:
        """
        Crear nueva asignación empleado-apartamento

        Flujo completo:
        1. Validar apartamento existe y está activo
        2. Validar empleado existe y está activo
        3. Verificar que empleado no tiene otra asignación activa
        4. Calcular renta prorrateada si es necesario
        5. Calcular total a descontar
        6. Crear registro en apartment_assignments
        7. Actualizar empleado (apartment_id)
        8. Generar deducción (si es mes completo)

        Args:
            assignment: Datos de la asignación
            user_id: ID del usuario

        Returns:
            Asignación creada

        Raises:
            HTTPException: Si hay validaciones fallidas
        """
        from fastapi import HTTPException

        # 1. Validar apartamento
        apartment = self.db.query(Apartment).filter(
            and_(
                Apartment.id == assignment.apartment_id,
                Apartment.deleted_at.is_(None)
            )
        ).first()

        if not apartment:
            raise HTTPException(
                status_code=404,
                detail="Apartamento no encontrado"
            )

        if apartment.status != "active":
            raise HTTPException(
                status_code=400,
                detail="El apartamento no está activo"
            )

        # 2. Validar empleado
        employee = self.db.query(Employee).filter(
            and_(
                Employee.id == assignment.employee_id,
                Employee.deleted_at.is_(None)
            )
        ).first()

        if not employee:
            raise HTTPException(
                status_code=404,
                detail="Empleado no encontrado"
            )

        if not employee.is_active:
            raise HTTPException(
                status_code=400,
                detail="El empleado no está activo"
            )

        # 3. Verificar que empleado no tiene asignación activa
        # Verificar tanto en Employee como en ApartmentAssignment
        existing_employee_assignment = self.db.query(Employee).filter(
            and_(
                Employee.id == assignment.employee_id,
                Employee.apartment_id.isnot(None),
                Employee.deleted_at.is_(None)
            )
        ).first()

        existing_assignment_record = self.db.query(ApartmentAssignment).filter(
            and_(
                ApartmentAssignment.employee_id == assignment.employee_id,
                ApartmentAssignment.status == AssignmentStatus.ACTIVE,
                ApartmentAssignment.deleted_at.is_(None)
            )
        ).first()

        if existing_employee_assignment or existing_assignment_record:
            raise HTTPException(
                status_code=400,
                detail="El empleado ya tiene una asignación activa. Debe finalizarla primero."
            )

        # 4. Calcular renta prorrateada si es necesario
        prorated_rent = await self._calculate_rent_for_assignment(
            assignment.monthly_rent,
            assignment.start_date,
            assignment.end_date,
            assignment.year if hasattr(assignment, 'year') else assignment.start_date.year,
            assignment.month if hasattr(assignment, 'month') else assignment.start_date.month,
        )

        # 5. Calcular total a descontar (solo renta por ahora)
        total_deduction = prorated_rent.prorated_rent

        try:
            # 6. Crear registro en apartment_assignments
            assignment_record = ApartmentAssignment(
                apartment_id=assignment.apartment_id,
                employee_id=assignment.employee_id,
                start_date=assignment.start_date,
                end_date=assignment.end_date,
                monthly_rent=assignment.monthly_rent,
                days_in_month=prorated_rent.days_in_month,
                days_occupied=prorated_rent.days_occupied,
                prorated_rent=prorated_rent.prorated_rent,
                is_prorated=prorated_rent.is_prorated,
                total_deduction=total_deduction,
                contract_type=assignment.contract_type,
                status=AssignmentStatus.ACTIVE,
                notes=assignment.notes,
            )
            self.db.add(assignment_record)
            self.db.flush()  # Para obtener el ID

            # 7. SINCRONIZAR: Actualizar employee.apartment_id
            self._sync_employee_apartment(
                employee_id=assignment.employee_id,
                apartment_id=assignment.apartment_id,
                start_date=assignment.start_date,
                monthly_rent=assignment.monthly_rent,
                action="assign",
            )

            # 8. Generar deducción si es mes completo
            if not prorated_rent.is_prorated:
                # TODO: Crear deducción en rent_deductions
                pass

            self.db.commit()

            # Construir respuesta
            return await self._build_assignment_response(
                assignment_id=assignment_record.id,
                assignment_data=assignment,
                employee_data=employee,
                apartment_data=apartment,
                prorated_rent=prorated_rent,
            )

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error al crear asignación: {str(e)}"
            )

    async def end_assignment(
        self,
        assignment_id: int,
        update: AssignmentUpdate,
        user_id: int,
    ) -> AssignmentResponse:
        """
        Finalizar asignación (salida del empleado)

        Proceso:
        1. Validar asignación existe y está activa
        2. Calcular días ocupados hasta fecha fin
        3. Calcular renta prorrateada
        4. Agregar cargo de limpieza
        5. Agregar otros cargos adicionales
        6. Calcular total a descontar
        7. Actualizar asignación como 'ended'
        8. Actualizar empleado (apartment_id = null)
        9. Generar deducción final

        Args:
            assignment_id: ID de la asignación
            update: Datos de actualización
            user_id: ID del usuario

        Returns:
            Asignación finalizada

        Raises:
            HTTPException: Si hay validaciones fallidas
        """
        from fastapi import HTTPException

        # 1. Validar asignación existe y está activa
        assignment = self.db.query(ApartmentAssignment).filter(
            and_(
                ApartmentAssignment.id == assignment_id,
                ApartmentAssignment.deleted_at.is_(None)
            )
        ).first()

        if not assignment:
            raise HTTPException(
                status_code=404,
                detail="Asignación no encontrada"
            )

        if assignment.status != AssignmentStatus.ACTIVE:
            raise HTTPException(
                status_code=400,
                detail=f"La asignación no está activa (estado actual: {assignment.status.value})"
            )

        # Validar que end_date se haya proporcionado
        if not update.end_date:
            raise HTTPException(
                status_code=400,
                detail="Debe proporcionar una fecha de finalización"
            )

        # Validar que end_date sea >= start_date
        if update.end_date < assignment.start_date:
            raise HTTPException(
                status_code=400,
                detail="La fecha de finalización no puede ser anterior a la fecha de inicio"
            )

        try:
            # 2-3. Calcular renta prorrateada hasta la fecha de fin
            prorated_rent = await self._calculate_rent_for_assignment(
                assignment.monthly_rent,
                assignment.start_date,
                update.end_date,
                update.end_date.year,
                update.end_date.month,
            )

            # 4. Calcular total con cargos adicionales (limpieza, etc.)
            # TODO: Agregar cargos adicionales de AdditionalCharge
            total_deduction = prorated_rent.prorated_rent

            # 5. Actualizar asignación como 'ended'
            assignment.end_date = update.end_date
            assignment.status = AssignmentStatus.ENDED
            assignment.days_occupied = prorated_rent.days_occupied
            assignment.prorated_rent = prorated_rent.prorated_rent
            assignment.is_prorated = prorated_rent.is_prorated
            assignment.total_deduction = total_deduction
            if update.notes:
                assignment.notes = update.notes
            assignment.updated_at = datetime.now()

            self.db.flush()

            # 6. SINCRONIZAR: Actualizar empleado (apartment_id = null)
            self._sync_employee_apartment(
                employee_id=assignment.employee_id,
                apartment_id=None,
                action="unassign",
            )

            # 7. Generar deducción final
            # TODO: Crear deducción en rent_deductions

            self.db.commit()

            # Obtener datos para respuesta
            employee = self.db.query(Employee).filter(Employee.id == assignment.employee_id).first()
            apartment = self.db.query(Apartment).filter(Apartment.id == assignment.apartment_id).first()

            # Construir datos de asignación para la respuesta
            from app.schemas.apartment_v2 import AssignmentCreate
            assignment_data = AssignmentCreate(
                apartment_id=assignment.apartment_id,
                employee_id=assignment.employee_id,
                start_date=assignment.start_date,
                end_date=assignment.end_date,
                monthly_rent=assignment.monthly_rent,
                contract_type=assignment.contract_type,
                notes=assignment.notes,
            )

            return await self._build_assignment_response(
                assignment_id=assignment.id,
                assignment_data=assignment_data,
                employee_data=employee,
                apartment_data=apartment,
                prorated_rent=prorated_rent,
            )

        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error al finalizar asignación: {str(e)}"
            )

    async def transfer_assignment(
        self,
        transfer: TransferRequest,
        user_id: int,
    ) -> TransferResponse:
        """
        Transferir empleado de un apartamento a otro (mudanza)

        Proceso atómico (3 pasos):
        1. Finalizar apartamento actual
        2. Iniciar nuevo apartamento
        3. Actualizar empleado

        Args:
            transfer: Datos de la transferencia
            user_id: ID del usuario

        Returns:
            Detalles de la transferencia

        Raises:
            HTTPException: Si hay validaciones fallidas
        """
        from fastapi import HTTPException
        from sqlalchemy.exc import SQLAlchemyError

        # TODO: Implementar transferencia completa
        # Placeholder para ejemplo
        raise HTTPException(status_code=501, detail="Funcionalidad en desarrollo")

    # -------------------------------------------------------------------------
    # LISTADO Y CONSULTA
    # -------------------------------------------------------------------------

    async def list_assignments(
        self,
        skip: int = 0,
        limit: int = 100,
        employee_id: Optional[int] = None,
        apartment_id: Optional[int] = None,
        status_filter: Optional[str] = None,
        start_date_from: Optional[date] = None,
        start_date_to: Optional[date] = None,
    ) -> List[AssignmentListItem]:
        """
        Listar asignaciones con filtros

        Args:
            skip: Registros a omitir
            limit: Límite de registros
            employee_id: Filtrar por empleado
            apartment_id: Filtrar por apartamento
            status_filter: Filtrar por estado
            start_date_from: Fecha inicio desde
            start_date_to: Fecha inicio hasta

        Returns:
            Lista de asignaciones
        """
        # TODO: Implementar consulta a apartment_assignments
        # Placeholder
        return []

    async def get_assignment(
        self,
        assignment_id: int,
    ) -> AssignmentResponse:
        """
        Obtener asignación por ID

        Args:
            assignment_id: ID de la asignación

        Returns:
            Asignación con detalles

        Raises:
            HTTPException: Si no se encuentra
        """
        from fastapi import HTTPException

        # TODO: Implementar consulta a apartment_assignments
        # Placeholder
        raise HTTPException(status_code=501, detail="Funcionalidad en desarrollo")

    async def get_active_assignments(
        self,
    ) -> List[AssignmentListItem]:
        """
        Obtener todas las asignaciones activas

        Returns:
            Lista de asignaciones activas
        """
        # TODO: Implementar
        return []

    # -------------------------------------------------------------------------
    # CÁLCULOS
    # -------------------------------------------------------------------------

    async def calculate_prorated_rent(
        self,
        calculation: ProratedCalculationRequest,
    ) -> ProratedCalculationResponse:
        """
        Calcular renta prorrateada

        Args:
            calculation: Datos para el cálculo

        Returns:
            Resultado del cálculo
        """
        # Calcular días en el mes
        days_in_month = calendar.monthrange(calculation.year, calculation.month)[1]

        # Calcular días ocupados
        if calculation.end_date:
            days_occupied = (calculation.end_date - calculation.start_date).days + 1
        else:
            # Hasta fin de mes
            end_of_month = datetime(calculation.year, calculation.month, days_in_month).date()
            days_occupied = (end_of_month - calculation.start_date).days + 1

        # Validar
        if days_occupied < 1:
            days_occupied = 1
        if days_occupied > days_in_month:
            days_occupied = days_in_month

        # Calcular tasa diaria (con decimales)
        daily_rate = Decimal(calculation.monthly_rent) / Decimal(days_in_month)

        # Calcular renta prorrateada y redondear
        prorated_rent = int((daily_rate * Decimal(days_occupied)).quantize(Decimal('1')))

        is_prorated = days_occupied != days_in_month

        return ProratedCalculationResponse(
            monthly_rent=calculation.monthly_rent,
            year=calculation.year,
            month=calculation.month,
            days_in_month=days_in_month,
            start_date=calculation.start_date,
            end_date=calculation.end_date,
            days_occupied=days_occupied,
            daily_rate=daily_rate,
            prorated_rent=prorated_rent,
            is_prorated=is_prorated,
        )

    async def calculate_total_deduction(
        self,
        calculation: TotalCalculationRequest,
    ) -> TotalCalculationResponse:
        """
        Calcular deducción total (renta + cargos adicionales)

        Fórmula:
        Total = Renta + Σ(Cargos Adicionales)

        Args:
            calculation: Datos para el cálculo

        Returns:
            Resultado del cálculo
        """
        # Sumar cargos adicionales
        additional_charges_total = sum(
            charge.get("amount", 0)
            for charge in calculation.additional_charges
        )

        # Calcular total
        total_deduction = calculation.base_rent + additional_charges_total

        # Construir breakdown
        breakdown = [
            {
                "type": "rent",
                "amount": calculation.base_rent,
                "description": "Renta prorrateada" if calculation.is_prorated else "Renta mensual"
            }
        ]

        for charge in calculation.additional_charges:
            breakdown.append({
                "type": charge.get("charge_type", "other"),
                "amount": charge.get("amount", 0),
                "description": charge.get("description", "Cargo adicional")
            })

        return TotalCalculationResponse(
            base_rent=calculation.base_rent,
            additional_charges_total=additional_charges_total,
            total_deduction=total_deduction,
            breakdown=breakdown,
        )

    # -------------------------------------------------------------------------
    # MÉTODOS AUXILIARES
    # -------------------------------------------------------------------------

    async def _calculate_rent_for_assignment(
        self,
        monthly_rent: int,
        start_date: date,
        end_date: Optional[date],
        year: int,
        month: int,
    ) -> ProratedCalculationResponse:
        """Calcular renta para una asignación"""
        # Crear request de cálculo
        calculation = ProratedCalculationRequest(
            monthly_rent=monthly_rent,
            start_date=start_date,
            end_date=end_date,
            year=year,
            month=month,
        )

        return await self.calculate_prorated_rent(calculation)

    async def _build_assignment_response(
        self,
        assignment_id: int,
        assignment_data: AssignmentCreate,
        employee_data: Employee,
        apartment_data: Apartment,
        prorated_rent: ProratedCalculationResponse,
    ) -> AssignmentResponse:
        """Construir respuesta de asignación"""
        # Placeholder - TODO: Implementar con datos reales
        return AssignmentResponse(
            id=assignment_id,
            apartment_id=assignment_data.apartment_id,
            employee_id=assignment_data.employee_id,
            start_date=assignment_data.start_date,
            end_date=assignment_data.end_date,
            monthly_rent=assignment_data.monthly_rent,
            days_in_month=prorated_rent.days_in_month,
            days_occupied=prorated_rent.days_occupied,
            prorated_rent=prorated_rent.prorated_rent,
            is_prorated=prorated_rent.is_prorated,
            total_deduction=prorated_rent.prorated_rent,
            contract_type=assignment_data.contract_type,
            notes=assignment_data.notes,
            status=AssignmentStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            apartment=ApartmentResponse(
                id=apartment_data.id,
                name=apartment_data.name,
                building_name=apartment_data.building_name,
                room_number=apartment_data.room_number,
                floor_number=apartment_data.floor_number,
                postal_code=apartment_data.postal_code,
                prefecture=apartment_data.prefecture,
                city=apartment_data.city,
                address_line1=apartment_data.address_line1,
                address_line2=apartment_data.address_line2,
                room_type=apartment_data.room_type,
                size_sqm=apartment_data.size_sqm,
                base_rent=apartment_data.base_rent,
                management_fee=apartment_data.management_fee,
                deposit=apartment_data.deposit,
                key_money=apartment_data.key_money,
                default_cleaning_fee=apartment_data.default_cleaning_fee,
                contract_start_date=apartment_data.contract_start_date,
                contract_end_date=apartment_data.contract_end_date,
                landlord_name=apartment_data.landlord_name,
                landlord_contact=apartment_data.landlord_contact,
                real_estate_agency=apartment_data.real_estate_agency,
                emergency_contact=apartment_data.emergency_contact,
                notes=apartment_data.notes,
                status=apartment_data.status,
                created_at=apartment_data.created_at,
                updated_at=apartment_data.updated_at,
                full_address=None,
                total_monthly_cost=apartment_data.base_rent + apartment_data.management_fee,
                active_assignments=0,
            ),
            employee={
                "id": employee_data.id,
                "full_name_kanji": employee_data.full_name_kanji,
                "full_name_kana": employee_data.full_name_kana,
            },
        )

    def _sync_employee_apartment(
        self,
        employee_id: int,
        apartment_id: Optional[int],
        start_date: Optional[date] = None,
        monthly_rent: Optional[int] = None,
        action: str = "assign",
    ) -> Employee:
        """
        Sincronizar employee.apartment_id con ApartmentAssignment

        Esta función mantiene la sincronización bidireccional entre:
        - Employee.apartment_id (sistema legacy V1)
        - ApartmentAssignment (sistema moderno V2)

        Args:
            employee_id: ID del empleado
            apartment_id: ID del apartamento (None para limpiar)
            start_date: Fecha de inicio de asignación
            monthly_rent: Renta mensual
            action: 'assign' | 'unassign' | 'transfer'

        Returns:
            Empleado actualizado

        Raises:
            HTTPException: Si el empleado no existe
        """
        from fastapi import HTTPException

        employee = self.db.query(Employee).filter(
            and_(
                Employee.id == employee_id,
                Employee.deleted_at.is_(None)
            )
        ).first()

        if not employee:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")

        if action == "assign":
            employee.apartment_id = apartment_id
            employee.apartment_start_date = start_date or date.today()
            employee.apartment_rent = monthly_rent or 0
            employee.apartment_move_out_date = None

        elif action == "unassign":
            employee.apartment_id = None
            employee.apartment_move_out_date = date.today()
            employee.apartment_rent = None

        elif action == "transfer":
            employee.apartment_id = apartment_id
            employee.apartment_start_date = start_date or date.today()
            employee.apartment_rent = monthly_rent or 0

        employee.updated_at = datetime.now()
        self.db.flush()

        return employee
