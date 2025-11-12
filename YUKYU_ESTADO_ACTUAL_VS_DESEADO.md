# 📊 ESTADO ACTUAL VS DESEADO: SISTEMA YUKYU

**Comparativa:** Sistema Actual (2025-11-12) → Sistema Mejorado

---

## 🏗️ COMPONENTE 1: LIFO DEDUCTION (Deducción LIFO)

### ESTADO ACTUAL ❌
```
PROBLEMA: Sin transacción SQL
RIESGO: Race condition, inconsistencia de datos

Código Actual:
┌─────────────────────────────────────────────────┐
│ for balance in balances:                        │
│     balance.days_used += to_deduct  ← UPDATE 1 │
│     balance.days_remaining = ...    ← UPDATE 2 │
│ self.db.commit()  ← TOO LATE!                   │
│                                                 │
│ request.status = APPROVED           ← UPDATE 3 │
│ self.db.add(usage_detail)           ← UPDATE 4 │
│ self.db.commit()  ← FINAL COMMIT                │
└─────────────────────────────────────────────────┘

Escenario de Fallo:
┌─────────────────────────────────────────────────┐
│ Solicitud A aprobada:                           │
│ Balance 2025: 11 → 8 ✓ ACTUALIZADO             │
│ Balance 2024: 9 → actualizar...                │
│ 💥 ERROR DE RED                                 │
│                                                 │
│ Request A: status = PENDING (no fue saved)     │
│ Balance 2024: 9 (NO ACTUALIZADO)               │
│ Data Inconsistente ❌                           │
└─────────────────────────────────────────────────┘

Efecto:
- Empleado puede solicitar OTRO yukyu
- Sistema cuenta los mismos 9 días dos veces
- FRAUDE POTENCIAL
```

### ESTADO DESEADO ✅
```
SOLUCIÓN: Con transacción SQLAlchemy
SEGURIDAD: Commit-all-or-rollback-all

Código Mejorado:
┌─────────────────────────────────────────────────┐
│ try:                                            │
│     with self.db.begin_nested():  ← INICIA TX  │
│         for balance in balances:                │
│             balance.days_used += ...  ← UPD 1  │
│             balance.days_remaining = ..← UPD 2 │
│             self.db.flush()                    │
│                                                 │
│         request.status = APPROVED   ← UPD 3   │
│         self.db.add(usage_detail)   ← UPD 4   │
│                                                 │
│     self.db.commit()  ← COMMIT ALL TOGETHER    │
│ except SQLAlchemyError:                        │
│     self.db.rollback()  ← REVIERTE TODO        │
│     raise error                                 │
└─────────────────────────────────────────────────┘

Escenario de Fallo (Mejorado):
┌─────────────────────────────────────────────────┐
│ Solicitud A aprobada:                           │
│ Balance 2025: 11 → 8 ✓                         │
│ Balance 2024: 9 → actualizar...                │
│ 💥 ERROR DE RED                                 │
│                                                 │
│ ROLLBACK AUTOMÁTICO:                           │
│ Request A: status = PENDING                    │
│ Balance 2025: 11 (REVERTIDO)                   │
│ Balance 2024: 9 (REVERTIDO)                    │
│ Data Consistente ✅                             │
│                                                 │
│ Sistema retorna error amable:                  │
│ "Transaction failed, please retry"             │
└─────────────────────────────────────────────────┘

Efecto:
- Data siempre consistente
- No hay fraude posible
- Seguridad garantizada
```

---

## 📅 COMPONENTE 2: VALIDACIÓN DE FECHAS LABORALES

### ESTADO ACTUAL ❌
```
PROBLEMA: Acepta cualquier fecha

Validaciones Actuales:
✓ start_date ≤ end_date
✓ days_requested ≤ available
❌ Fin de semana (土日)
❌ Feriados japoneses (祝日)
❌ Fechas pasadas
❌ Máximo días continuos

Ejemplo - INCORRECTO:
┌─────────────────────────────────────────────────┐
│ Request: "Vacaciones 3-4 agosto 2025"          │
│ ┌─────────────────────────────────────────────┐ │
│ │ 2025-08-03: SÁBADO  ← Pero sistema cuenta  │ │
│ │ 2025-08-04: DOMINGO ← 2 días de yukyu!     │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ Sistema Actual:                                 │
│ if (3 ≤ 2 ≤ 18):  ✓ VÁLIDO                    │
│                                                 │
│ Resultado: Empleado pierde 2 días injustamente │
└─────────────────────────────────────────────────┘

Caso Real Problemático:
┌─────────────────────────────────────────────────┐
│ Períodos:                                       │
│ - 2025-12-01 a 2025-12-07 (lunes a domingo)   │
│ - Solicita: 7 días completos                   │
│ - Sistema: ✓ VÁLIDO (7 ≤ 18)                  │
│                                                 │
│ Realidad:                                       │
│ - Sábado 6: Sin trabajo (no cuenta)           │
│ - Domingo 7: Sin trabajo (no cuenta)          │
│ - Empleado pierde 2 días sin razón            │
└─────────────────────────────────────────────────┘
```

### ESTADO DESEADO ✅
```
SOLUCIÓN: Validador de fechas laborales

Validaciones Completas:
✓ start_date ≤ end_date
✓ days_requested ≤ available
✓ Fin de semana (土日) ← NUEVO
✓ Feriados japoneses (祝日) ← NUEVO
✓ Fechas pasadas ← NUEVO
✓ Máximo 30 días continuos ← NUEVO

Ejemplo - CORRECTO:
┌─────────────────────────────────────────────────┐
│ Request: "Vacaciones 3-4 agosto 2025"          │
│ ┌─────────────────────────────────────────────┐ │
│ │ 2025-08-03: SÁBADO  ← is_business_day: NO │ │
│ │ 2025-08-04: DOMINGO ← is_business_day: NO │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ Validación:                                     │
│ business_days = 0 (no hay días laborales)      │
│ days_requested = 2.0                           │
│ 0 ≠ 2.0 → ❌ RECHAZA CON ERROR:               │
│ "Período no contiene días laborales"           │
│                                                 │
│ Empleado NO pierde yukyus injustamente ✓      │
└─────────────────────────────────────────────────┘

Caso Real Mejorado:
┌─────────────────────────────────────────────────┐
│ Períodos:                                       │
│ - 2025-12-01 a 2025-12-07 (lunes a domingo)   │
│ - Solicita: 7 días completos                   │
│                                                 │
│ Validación:                                     │
│ - Lunes 1: ✓ Día laboral                      │
│ - Martes 2: ✓ Día laboral                     │
│ - Miércoles 3: ✓ Día laboral                  │
│ - Jueves 4: ✓ Día laboral                     │
│ - Viernes 5: ✓ Día laboral                    │
│ - Sábado 6: ✗ Fin de semana                   │
│ - Domingo 7: ✗ Fin de semana                  │
│                                                 │
│ business_days = 5 (solo laborales)             │
│ days_requested = 7.0                           │
│ 5 ≠ 7 → ❌ RECHAZA CON ERROR:                 │
│ "Días solicitados (7) no coinciden con"        │
│ "días laborales (5) en ese período"            │
│                                                 │
│ Sistema sugiere:                               │
│ "Use 2025-12-01 a 2025-12-05 para 5 días"     │
└─────────────────────────────────────────────────┘
```

---

## 👤 COMPONENTE 3: MAPEO DE ROLES (TANTOSHA)

### ESTADO ACTUAL ❌
```
PROBLEMA: TANTOSHA mapeado como EMPLOYEE

Rol Hierarchy (Real):
┌─────────────────────────────────┐
│ SUPER_ADMIN (全権)              │
│   ↓                             │
│ ADMIN (管理者)                  │
│   ↓                             │
│ KEIRI + TANTOSHA (並列)         │
│   ↓                             │
│ COORDINATOR (調整者)            │
│   ↓                             │
│ KANRININSHA (管理人)            │
│   ↓                             │
│ EMPLOYEE (従業員)               │
│   ↓                             │
│ CONTRACT_WORKER (契約社員)      │
└─────────────────────────────────┘

Código Actual (INCORRECTO):
┌─────────────────────────────────┐
│ @router.post("/requests/")      │
│ async def create_request(        │
│     current_user = Depends(      │
│         require_role("employee") │  ← INCORRECTO
│     )                            │
│ ):                               │
│     # Solo EMPLOYEE puede crear │
│     # Pero TANTOSHA no es EMPLOYEE!
└─────────────────────────────────┘

Problema de Seguridad:
┌─────────────────────────────────┐
│ EMPLOYEE (empleado regular):    │
│ - Puede ver propios yukyus      │
│ - NO puede crear solicitudes    │
│                                 │
│ TANTOSHA (operador RR.HH.):    │
│ - DEBE crear solicitudes        │
│ - Pero código dice "employee"   │
│                                 │
│ Resultado:                       │
│ ❌ TANTOSHA NO puede acceder    │
│ ❌ Endpoint bloqueado           │
│ ❌ Feature no funciona          │
│                                 │
│ O:                              │
│ ❌ Otro rol gana acceso equivoc │
│ ❌ ESCALACIÓN DE PRIVILEGIOS    │
└─────────────────────────────────┘
```

### ESTADO DESEADO ✅
```
SOLUCIÓN: Mapeo de roles correcto

Código Mejorado:
┌──────────────────────────────────┐
│ @router.post("/requests/")       │
│ async def create_request(         │
│     current_user: User = Depends( │
│         require_role([            │  ← CORRECTO
│             "tantosha",           │
│             "admin",              │
│             "keitosan"            │
│         ])                        │
│     )                             │
│ ):                                │
│     # Exactamente los roles      │
│     # que pueden crear requests   │
└──────────────────────────────────┘

Matriz de Permisos Correcta:
┌──────────────────────────────────┬───────┐
│ Acción                           │ Roles │
├──────────────────────────────────┼───────┤
│ Ver propios yukyus               │ ALL   │
│ Ver todos yukyus                 │ ADM,K │
│ Crear solicitud (TANTOSHA)       │ TAN,A │
│ Aprobar solicitud (KEIRI)        │ ADM,K │
│ Rechazar solicitud               │ ADM,K │
│ Calcular yukyus                  │ ADM   │
│ Expirar yukyus                   │ ADM   │
│ Ver reportes                     │ ADM,K │
│ Exportar Excel                   │ ADM,K │
└──────────────────────────────────┴───────┘

ADM = ADMIN, K = KEIRI/KEITOSAN, TAN = TANTOSHA

Seguridad Garantizada:
✓ TANTOSHA accede correctamente
✓ Otros roles NO escalan privilegios
✓ Permiso granular por endpoint
✓ Documentado y auditable
```

---

## 🏭 COMPONENTE 4: FACTORY_ID TYPE NORMALIZATION

### ESTADO ACTUAL ⚠️
```
PROBLEMA: Inconsistencia de tipos

Base de Datos (Modelo):
┌─────────────────────────────────┐
│ factory_id = Column(Integer)    │
│                                 │
│ Tipo: INTEGER (1-9999)          │
└─────────────────────────────────┘

Schema de Validación:
┌─────────────────────────────────┐
│ factory_id: Optional[str]       │  ← STRING ❌
│                                 │
│ Tipo: STRING ("F001", etc.)     │
└─────────────────────────────────┘

API Endpoint:
┌─────────────────────────────────┐
│ @router.get(                    │
│     "/employees/by-factory/{id}"│
│ )                               │
│ async def get_employees_by_fac( │
│     factory_id: str  ← STRING   │
│ ):                              │
│     query.filter(               │
│         Employee.factory_id == int(factory_id)  │
│         ↑ Conversion manual ❌   │
│     )                            │
└─────────────────────────────────┘

Impacto:
- Type validation falla
- Errores: "invalid literal for int()"
- Debugging difícil
- No type-safe (Python/TypeScript)
```

### ESTADO DESEADO ✅
```
SOLUCIÓN: Tipos consistentes (INTEGER)

Base de Datos:
┌─────────────────────────────────┐
│ factory_id = Column(Integer)    │
│ Tipo: INTEGER ✓                 │
└─────────────────────────────────┘

Schema de Validación:
┌─────────────────────────────────┐
│ factory_id: int                 │  ← INTEGER ✓
│ factory_id: Optional[int] = None │
│ Tipo: INTEGER ✓                 │
└─────────────────────────────────┘

API Endpoint:
┌─────────────────────────────────┐
│ @router.get(                    │
│     "/employees/by-factory/{id}"│
│ )                               │
│ async def get_employees_by_fac( │
│     factory_id: int  ← INTEGER  │
│ ):                              │
│     query.filter(               │
│         Employee.factory_id == factory_id │
│         ✓ Sin conversión manual  │
│     )                            │
└─────────────────────────────────┘

Beneficios:
✓ Type-safe en toda la app
✓ Validación automática
✓ Mejor performance (sin cast)
✓ Errores más claros
```

---

## ⚖️ COMPONENTE 5: VALIDACIÓN 5-DAY MINIMUM

### ESTADO ACTUAL ❌
```
PROBLEMA: Solo flag, no validación fuerte

Implementación Actual:
┌─────────────────────────────────────┐
│ def check_minimum_5_days(...) -> bool
│     # Retorna True/False             │
│                                     │
│ Response:                           │
│ {                                   │
│     "needs_to_use_minimum_5_days": true,  │
│     ...                             │
│ }                                   │
└─────────────────────────────────────┘

Problema Legal:
- Requisito: Mínimo 5 yukyus por año fiscal
- Responsable: EMPRESA (no empleado)
- Actual: Solo info, sin prevención
- Resultado: INCUMPLIMIENTO DE LEY

Escenario Actual:
┌─────────────────────────────────────┐
│ Año Fiscal 2025 (Abril-Marzo):      │
│ Empleado: 山田太郎                  │
│ Yukyus usados: 2 días                │
│ Faltantes: 3 días                    │
│                                     │
│ Sistema muestra:                    │
│ ⚠️ needs_to_use_minimum_5_days: true│
│                                     │
│ Pero:                               │
│ - NO previene cierre del año        │
│ - NO envía alerta al admin          │
│ - NO impide entrada de más requests │
│                                     │
│ Resultado: Año cierra sin usar 3d  │
│ → EMPRESA INCUMPLE LEY LABORAL ❌   │
└─────────────────────────────────────┘
```

### ESTADO DESEADO ✅
```
SOLUCIÓN: Validación fuerte + Alertas

Implementación Mejorada:
┌─────────────────────────────────────┐
│ def check_minimum_5_days_requirement(
│     employee_id, fiscal_year
│ ) -> (bool, int, str):              │
│     # Retorna: (compliant, remaining, warning)
│                                     │
│ Response:                           │
│ {                                   │
│     "minimum_5_days_compliant": false,
│     "minimum_5_days_remaining": 3,   │
│     "compliance_warning": "⚠️ LEGAL", │
│     ...                             │
│ }                                   │
└─────────────────────────────────────┘

Acciones Automáticas:
1. CHECK: Cada solicitud de yukyu
2. ALERT: Si quedan ≤3 días sin usar
3. WARNING: Visible en dashboard rojo
4. AUDIT: Registra en compliance log

Escenario Mejorado:
┌─────────────────────────────────────┐
│ Año Fiscal 2025:                    │
│ Empleado: 山田太郎                  │
│ Yukyus usados: 2 días                │
│ Faltantes: 3 días                    │
│                                     │
│ Sistema muestra:                    │
│ 🔴 ALERTA ROJA:                     │
│ "⚠️ LEGAL: Mínimo 5 días requerido" │
│ "Actualmente: 2d, Faltantes: 3d"   │
│ "Plazo: Hasta 31 de Marzo 2026"    │
│                                     │
│ Y:                                  │
│ - Admin recibe notificación         │
│ - Entra en compliance dashboard     │
│ - KEIRI puede ver alertas de todos  │
│ - Se previene incumplimiento ✓      │
└─────────────────────────────────────┘

Matriz de Alertas:
┌──────────────────┬────────┬────────┐
│ Días Usados      │ Alert  │ Color  │
├──────────────────┼────────┼────────┤
│ 0-2 días         │ 🔴 XXX │ RED    │
│ 3-4 días         │ 🟡 !!  │ YELLOW │
│ 5+ días          │ 🟢 OK  │ GREEN  │
└──────────────────┴────────┴────────┘
```

---

## 📊 TABLA COMPARATIVA FINAL

| Componente | Actual | Mejorado | Crítica |
|-----------|--------|----------|---------|
| **LIFO Transacción** | ❌ Sin TX | ✅ SQLAlchemy | 🔴 CRÍTICA |
| **Validación Fechas** | ❌ Ninguna | ✅ Completa | 🔴 CRÍTICA |
| **Mapeo de Roles** | ⚠️ Incorrecto | ✅ Correcto | 🔴 CRÍTICA |
| **Factory ID Type** | ⚠️ Mixto | ✅ Integer | 🟠 ALTA |
| **5-Day Validation** | ⚠️ Flag only | ✅ Fuerte | 🟠 ALTA |
| **Seguridad** | 🔴 Débil | 🟢 Fuerte | - |
| **Compliance** | 🔴 Riesgo | 🟢 Seguro | - |

---

## 🎯 RESUMEN VISUAL

```
ANTES (❌)              DESPUÉS (✅)
──────────────────────────────────

Transacciones:         Transacciones:
❌ Race conditions     ✅ Atomic commits

Validaciones:          Validaciones:
❌ Cualquier fecha     ✅ Solo laborales

Permisos:              Permisos:
❌ TANTOSHA bloqueado  ✅ TANTOSHA activo

Types:                 Types:
❌ Mixed int/str       ✅ Consistentes

Compliance:            Compliance:
❌ Incumplimiento      ✅ Ley cumplida

Deploy Ready:          Deploy Ready:
🔴 NO                  🟢 SÍ
```

---

**Documento Generado:** 2025-11-12 por Claude Code
**Próximo Paso:** Aprobación de correcciones
**Tiempo Estimado de Correcciones:** 4-6 horas
