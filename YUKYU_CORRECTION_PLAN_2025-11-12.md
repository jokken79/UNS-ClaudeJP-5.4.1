# 🚀 PLAN DE CORRECCIONES DEL SISTEMA YUKYU
**Estado:** 📋 LISTO PARA EJECUTAR
**Duración Estimada:** 4-6 horas
**Fase:** 1 (CRÍTICA), 2 (ALTA), 3 (MEDIA)

---

## 📊 DIAGRAMA DEL FLUJO DE CORRECCIONES

```
┌────────────────────────────────────────────────────────────────┐
│                    ANÁLISIS COMPLETO ✅                         │
│   Identificados 5 problemas críticos + 3 inconsistencias      │
└────────────────────────────────────────────────────────────────┘
                             ↓
┌────────────────────────────────────────────────────────────────┐
│              FASE 1: CRÍTICA (Deploy Bloqueada)               │
├────────────────────────────────────────────────────────────────┤
│ 1. Transacciones LIFO                [Priority: 🔴 CRITICAL]  │
│ 2. Validación Fechas Laborales       [Priority: 🔴 CRITICAL]  │
│ 3. Mapeo de Roles (TANTOSHA)         [Priority: 🔴 CRITICAL]  │
└────────────────────────────────────────────────────────────────┘
                             ↓
                      Tests Automatizados
                             ↓
┌────────────────────────────────────────────────────────────────┐
│                FASE 2: ALTA (Pre-Lanzamiento)                │
├────────────────────────────────────────────────────────────────┤
│ 4. Normalizar Factory ID             [Priority: 🟠 HIGH]      │
│ 5. Validación 5-day Minimum          [Priority: 🟠 HIGH]      │
└────────────────────────────────────────────────────────────────┘
                             ↓
                   Validación de Permisos
                             ↓
┌────────────────────────────────────────────────────────────────┐
│               FASE 3: MEDIA (Mejoras Futuras)               │
├────────────────────────────────────────────────────────────────┤
│ 6. Auditoría de Cambios              [Priority: 🟡 MEDIUM]   │
│ 7. Mejoras de Notificación           [Priority: 🟡 MEDIUM]   │
│ 8. Resolución de Inconsistencias     [Priority: 🟡 MEDIUM]   │
└────────────────────────────────────────────────────────────────┘
                             ↓
┌────────────────────────────────────────────────────────────────┐
│                  ✅ SISTEMA LISTO PARA PROD                   │
└────────────────────────────────────────────────────────────────┘
```

---

## 🔴 FASE 1: CRÍTICA (DEBE HACER AHORA)

### ✏️ Corrección #1: Implementar Transacciones LIFO
**Archivo:** `/backend/app/services/yukyu_service.py`
**Líneas Afectadas:** 692-780 (función `_deduct_yukyus_lifo`)
**Cambios Requeridos:**

#### ANTES (❌ Sin Transacción):
```python
async def _deduct_yukyus_lifo(
    self,
    employee_id: int,
    days_to_deduct: float,
    request_id: int,
    start_date: date,
    end_date: date
) -> None:
    """Deduct yukyus using LIFO"""
    balances = self.db.query(YukyuBalance).filter(
        YukyuBalance.employee_id == employee_id,
        YukyuBalance.status == YukyuStatus.ACTIVE,
        YukyuBalance.days_available > 0
    ).order_by(YukyuBalance.assigned_date.desc()).all()

    remaining_to_deduct = Decimal(str(days_to_deduct))

    for balance in balances:  # ❌ LOOP SIN TRANSACCIÓN
        if remaining_to_deduct <= 0:
            break

        # ❌ Si falla aquí, balance anterior fue actualizado
        balance.days_used += to_deduct_from_this
        balance.days_remaining = balance.days_total - balance.days_used

    # ❌ Si falla aquí, todos los balances fueron actualizados
    self.db.add(usage_detail)
    self.db.commit()
```

#### DESPUÉS (✅ Con Transacción):
```python
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

async def _deduct_yukyus_lifo(
    self,
    employee_id: int,
    days_to_deduct: float,
    request_id: int,
    start_date: date,
    end_date: date
) -> None:
    """Deduct yukyus using LIFO with transaction safety"""
    from fastapi import HTTPException

    try:
        # ✅ INICIA TRANSACCIÓN ANIDADA
        with self.db.begin_nested():
            balances = self.db.query(YukyuBalance).filter(
                YukyuBalance.employee_id == employee_id,
                YukyuBalance.status == YukyuStatus.ACTIVE,
                YukyuBalance.days_available > 0
            ).order_by(YukyuBalance.assigned_date.desc()).all()

            if not balances:
                raise ValueError("No yukyu balances available")

            remaining_to_deduct = Decimal(str(days_to_deduct))
            usage_details = []

            # ✅ TODOS los cambios aquí se aplican junto o se revierten juntos
            for balance in balances:
                if remaining_to_deduct <= 0:
                    break

                available = Decimal(str(balance.days_available))
                to_deduct_from_this = min(remaining_to_deduct, available)

                # Actualiza balance
                balance.days_used = (balance.days_used or 0) + float(to_deduct_from_this)
                balance.days_remaining = balance.days_total - balance.days_used
                balance.days_available = Decimal(str(balance.days_available)) - to_deduct_from_this
                self.db.flush()  # Asegura validación de constraints

                remaining_to_deduct -= to_deduct_from_this

                # Crea usage details
                current = start_date
                while current <= end_date:
                    usage_details.append(
                        YukyuUsageDetail(
                            request_id=request_id,
                            balance_id=balance.id,
                            usage_date=current,
                            days_deducted=Decimal('0.5') if (end_date - start_date).days == 0 else Decimal('1.0')
                        )
                    )
                    current += timedelta(days=1)

            # ✅ Agregar todos los usage details
            for detail in usage_details:
                self.db.add(detail)

            self.db.flush()  # Pre-commit check

        # ✅ COMMIT FINAL (after block succeeds)
        self.db.commit()

    except (SQLAlchemyError, IntegrityError) as e:
        self.db.rollback()  # ✅ REVIERTE TODO si hay error
        raise HTTPException(
            status_code=500,
            detail=f"Transaction failed during yukyu deduction: {str(e)}"
        )
    except Exception as e:
        self.db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Failed to deduct yukyus: {str(e)}"
        )
```

**Testing Requerido:**
```bash
# Test 1: Deducción normal
POST /api/yukyu/requests/ with days=3.0
→ Verify all balances updated correctly

# Test 2: Race condition (simultáneo)
# Simular 2 requests approve() al mismo tiempo
# Verify: solo uno falla gracefully, data es consistente

# Test 3: Rollback
# Simular error en medio del processo
# Verify: TODOS los balances revienen al original
```

---

### ✏️ Corrección #2: Validación de Fechas Laborales
**Archivo:** `/backend/app/services/yukyu_service.py` (nuevo módulo: `dates_validator.py`)
**Líneas Afectadas:** 580 (create_request - agregar validación)

#### Paso 1: Crear módulo de validación
**Nuevo Archivo:** `/backend/app/utils/japanese_dates.py`

```python
"""
Japanese Date Utilities
- Feriados japoneses (祝日)
- Cálculos de días laborales
"""

from datetime import date, timedelta
from typing import List

# Feriados Nacionales Japoneses 2025 (固定祝日)
JAPANESE_HOLIDAYS_FIXED = {
    (1, 1):   "元日 (New Year's Day)",
    (2, 11):  "建国記念日 (Foundation Day)",
    (4, 29):  "昭和の日 (Showa Day)",
    (5, 3):   "憲法記念日 (Constitution Day)",
    (5, 4):   "みどりの日 (Greenery Day)",
    (5, 5):   "こどもの日 (Children's Day)",
    (7, 15):  "海の日 (Marine Day)",
    (8, 11):  "山の日 (Mountain Day)",
    (9, 15):  "敬老の日 (Respect for the Aged Day)",
    (10, 13): "体育の日 (Sports Day)",
    (11, 3):  "文化の日 (Culture Day)",
    (11, 23): "勤労感謝の日 (Labor Thanksgiving Day)",
    (12, 25): "クリスマス (Christmas - opcional)",
}

def get_japanese_holidays(year: int) -> List[date]:
    """
    Retorna lista de feriados japoneses para el año.

    Para equinoxios (vernal y otoño), usar cálculo especial.
    """
    holidays = []

    # Feriados fijos
    for (month, day), name in JAPANESE_HOLIDAYS_FIXED.items():
        try:
            holidays.append(date(year, month, day))
        except ValueError:
            pass

    # Equinoxios aproximados (cálculos complejos, usar tabla)
    # Vernal Equinox (春分): ~20-21 de marzo
    # Autumnal Equinox (秋分): ~22-23 de septiembre

    vernal_equinox_day = 21  # Aproximado para 2025
    autumnal_equinox_day = 23  # Aproximado para 2025

    holidays.append(date(year, 3, vernal_equinox_day))
    holidays.append(date(year, 9, autumnal_equinox_day))

    return sorted(holidays)

def is_weekend(check_date: date) -> bool:
    """Retorna True si es fin de semana (土日)"""
    return check_date.weekday() >= 5  # 5=Sábado, 6=Domingo

def is_holiday(check_date: date) -> bool:
    """Retorna True si es feriado nacional japonés"""
    holidays = get_japanese_holidays(check_date.year)
    return check_date in holidays

def is_business_day(check_date: date) -> bool:
    """Retorna True si es día laboral (no fin de semana, no feriado)"""
    return not is_weekend(check_date) and not is_holiday(check_date)

def count_business_days(start_date: date, end_date: date) -> float:
    """
    Cuenta días laborales entre fechas (inclusive).

    Retorna como decimal:
    - Día completo: 1.0
    - Fin de semana/feriado: 0.0
    """
    if start_date > end_date:
        return 0.0

    business_days = 0.0
    current = start_date

    while current <= end_date:
        if is_business_day(current):
            business_days += 1.0
        current += timedelta(days=1)

    return business_days

def validate_yukyu_request_dates(
    start_date: date,
    end_date: date,
    days_requested: float,
    allow_past: bool = False
) -> tuple[bool, str]:
    """
    Valida fechas de solicitud yukyu completa.

    Retorna: (is_valid, error_message)
    """

    # 1. Rango válido
    if start_date > end_date:
        return False, "start_date debe ser menor o igual a end_date"

    # 2. No en el pasado
    if not allow_past and start_date < date.today():
        return False, "No se pueden solicitar yukyus para fechas pasadas"

    # 3. No más de 30 días continuos
    delta_days = (end_date - start_date).days + 1
    if delta_days > 30:
        return False, "Máximo 30 días continuos de yukyu permitidos"

    # 4. Valida que días solicitados coincidan con días laborales
    business_days = count_business_days(start_date, end_date)

    # Permite pequeña tolerancia (0.5 días)
    if abs(business_days - days_requested) > 0.5:
        return False, (
            f"Días solicitados ({days_requested}) no coinciden con "
            f"días laborales ({business_days}) en ese período"
        )

    # 5. Valida que haya al menos un día laboral
    if business_days == 0:
        return False, "El período solicitado no contiene días laborales"

    return True, ""

def get_next_business_day(from_date: date) -> date:
    """Retorna el próximo día laboral"""
    current = from_date + timedelta(days=1)
    while not is_business_day(current):
        current += timedelta(days=1)
    return current

def get_previous_business_day(from_date: date) -> date:
    """Retorna el día laboral anterior"""
    current = from_date - timedelta(days=1)
    while not is_business_day(current):
        current -= timedelta(days=1)
    return current
```

#### Paso 2: Integrar validación en servicio
**Modificar:** `/backend/app/services/yukyu_service.py` línea 580

```python
from app.utils.japanese_dates import validate_yukyu_request_dates

async def create_request(
    self,
    request: YukyuRequestCreate,
    current_user: User,
    db: Session
) -> YukyuRequestResponse:
    """Create yukyu request with validations"""
    from fastapi import HTTPException

    # ✅ VALIDACIÓN 1: Fechas laborales
    is_valid, error_msg = validate_yukyu_request_dates(
        start_date=request.start_date,
        end_date=request.end_date,
        days_requested=request.days_requested,
        allow_past=False  # No permite fechas pasadas
    )

    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid dates for yukyu request: {error_msg}"
        )

    # ... resto del código ...
```

---

### ✏️ Corrección #3: Mapeo de Roles (TANTOSHA)
**Archivo:** `/backend/app/api/yukyu.py`
**Líneas Afectadas:** 150-170 (endpoint create_request)

#### ANTES (❌):
```python
@router.post("/requests/")
async def create_request(
    request: YukyuRequestCreate,
    current_user = Depends(require_role("employee"))  # ❌ INCORRECTO
):
```

#### DESPUÉS (✅):
```python
@router.post("/requests/")
async def create_request(
    request: YukyuRequestCreate,
    current_user: User = Depends(
        require_role(["tantosha", "admin", "keitosan"])  # ✅ CORRECTO
    )
):
    """
    Create a new yukyu request.
    Only TANTOSHA (and ADMIN/KEITOSAN) can create requests.
    """
```

**Cambios en todos los endpoints:**

```python
# Endpoint: GET /balances/{employee_id}
# BEFORE: require_role("employee")
# AFTER:  require_role(["admin", "keiri", "keitosan", "employee"])
#         → employee solo ve sus propios datos

# Endpoint: GET /yukyu-reports
# BEFORE: require_role("admin")
# AFTER:  require_role(["admin", "keiri", "keitosan"])

# Endpoint: POST /maintenance/expire-old-yukyus
# BEFORE: require_role("admin")
# AFTER:  require_role(["admin"])  # Solo admin
```

**Crear función helper para validar:**

```python
# En core/deps.py
def require_role(roles: Union[str, List[str]]):
    """
    Dependency para validar que usuario tiene uno de los roles especificados.

    Uso:
        Depends(require_role("admin"))  # Un rol
        Depends(require_role(["admin", "keiri"]))  # Múltiples roles
    """
    if isinstance(roles, str):
        roles = [roles]

    def check_role(current_user: User = Depends(get_current_user)):
        if current_user.role.value not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"User role {current_user.role} cannot access this resource. "
                       f"Required roles: {', '.join(roles)}"
            )
        return current_user

    return check_role
```

---

## 🟠 FASE 2: ALTA (Antes del Lanzamiento)

### ✏️ Corrección #4: Normalizar Factory ID
**Archivos:**
- `/backend/app/models/models.py` (verificar tipo)
- `/backend/app/schemas/yukyu.py` (cambiar type)
- `/backend/app/api/yukyu.py` (actualizar endpoint paths)

#### En Schemas (`/backend/app/schemas/yukyu.py`):
```python
class YukyuRequestCreate(BaseModel):
    employee_id: int
    factory_id: int  # ✅ CAMBIAR DE str A int
    request_type: str = "yukyu"
    start_date: date
    end_date: date
    days_requested: Decimal = Field(..., ge=0.5, le=40.0, decimal_places=1)
    notes: Optional[str] = None

class YukyuRequestResponse(BaseModel):
    id: int
    employee_id: int
    factory_id: int  # ✅ CAMBIAR DE str A int
    # ... resto
```

---

### ✏️ Corrección #5: Validación 5-Day Minimum Fuerte
**Archivo:** `/backend/app/services/yukyu_service.py`

#### ANTES (❌ Débil):
```python
def check_minimum_5_days(self, employee_id: int) -> bool:
    """Solo retorna un flag, no previene nada"""
    # Solo genera: needs_to_use_minimum_5_days: True/False
```

#### DESPUÉS (✅ Fuerte):
```python
def check_minimum_5_days_requirement(
    self,
    employee_id: int,
    fiscal_year: int
) -> tuple[bool, int, str]:
    """
    Valida requisito legal japonés: mínimo 5 días de yukyu por año.

    Retorna: (is_compliant, days_remaining_to_use, warning_message)
    """
    # Período fiscal: Abril del año anterior - Marzo del año actual
    start_month = 4
    end_month = 3

    if fiscal_year not in [2024, 2025, 2026]:
        return True, 0, ""

    # Determina rango de fechas
    if datetime.now().month >= start_month:
        fiscal_start = date(datetime.now().year, start_month, 1)
        fiscal_end = date(datetime.now().year + 1, end_month, 31)
    else:
        fiscal_start = date(datetime.now().year - 1, start_month, 1)
        fiscal_end = date(datetime.now().year, end_month, 31)

    # Cuenta yukyus usados en fiscal year
    days_used = self.db.query(func.sum(YukyuUsageDetail.days_deducted)).filter(
        YukyuUsageDetail.usage_date >= fiscal_start,
        YukyuUsageDetail.usage_date <= fiscal_end
    ).scalar() or 0

    days_remaining = max(0, 5 - days_used)
    is_compliant = days_used >= 5

    # Genera warning
    if not is_compliant:
        warning = f"⚠️ LEGAL: Empleado debe usar mínimo 5 días en año fiscal. " \
                  f"Actuales: {days_used}d, Faltantes: {days_remaining}d"
    else:
        warning = ""

    return is_compliant, days_remaining, warning

# En endpoint GET /balances:
def get_balances(self, ...) -> YukyuBalanceSummary:
    # ...
    is_compliant, days_remaining, warning = self.check_minimum_5_days_requirement(
        employee_id, fiscal_year=2025
    )

    # Retorna en response
    return YukyuBalanceSummary(
        # ...
        minimum_5_days_compliant=is_compliant,
        minimum_5_days_remaining=days_remaining,
        compliance_warning=warning
    )

# En endpoint Frontend:
# Si warning, mostrar ALERTA ROJA visible en dashboard
```

---

## 🟡 FASE 3: MEDIA (Mejoras Futuras)

### Mejora #6: Auditoría de Cambios
**Crear tabla:** `yukyu_audit_log`
**Registrar:** Quién cambió qué y cuándo

### Mejora #7: Notificaciones Mejoradas
**Implementar:** Envío real de emails/LINE cuando se aprueba/rechaza

### Mejora #8: Resolver Inconsistencias
**Decidir:** Eliminar request types no usados o implementarlos

---

## ✅ CHECKLIST DE EJECUCIÓN

### Fase 1 (Crítica):
- [ ] Transacciones LIFO implementadas
- [ ] Module `japanese_dates.py` creado
- [ ] Validación de fechas integrada
- [ ] Roles en endpoints corregidos
- [ ] Tests E2E: Todos pasan ✓
- [ ] Frontend: Sin errores de validación ✓

### Fase 2 (Alta):
- [ ] Factory ID normalizado
- [ ] 5-day minimum validation activa
- [ ] Response schemas actualizados
- [ ] Tests de compliance

### Fase 3 (Media):
- [ ] Auditoría implementada
- [ ] Notificaciones reales
- [ ] Inconsistencias resueltas

---

## 🎯 COMANDOS DE EJECUCIÓN

```bash
# Después de aplicar correcciones:

# 1. Run tests
pytest backend/tests/ -v -k yukyu

# 2. Run E2E tests
npm run test:e2e -- yukyu

# 3. Type check
npm run type-check

# 4. Build
npm run build

# 5. Verify no breaking changes
git diff backend/

# 6. Commit changes
git add .
git commit -m "fix: Corregir problemas críticos en sistema yukyu (transacciones, validaciones, permisos)"

# 7. Push
git push -u origin claude/analyze-yukyu-system-011CV43pu9HBJ3NxmCpZMzdL
```

---

**Documento Generado:** 2025-11-12 por Claude Code
**Estado:** 📋 Listo para Ejecución de Fase 1
**Próximo Paso:** Delegar a agentes especializados para implementar correcciones
