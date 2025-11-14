# 📋 JPlanapp.md - PLAN COMPLETO DE DESARROLLO
## UNS-ClaudeJP 5.4.1 - Sistema HR para Empresas de 派遣 (Dispatch)

**Fecha:** 2025-11-13
**Versión:** 5.4.1
**Stack:** FastAPI 0.115.6 + Next.js 16.0.0 + PostgreSQL 15 + Docker
**Autor:** ADMIN (Creador del sistema)

---

## 🎯 VISIÓN Y OBJETIVOS DEL SISTEMA

### Objetivo Principal
Sistema completo de gestión de recursos humanos para empresas de staffing japonesas (人材派遣会社) que administran empleados temporales en múltiples fábricas clientes.

### Prioridades de Desarrollo (Definidas por el Usuario)

**PRIORIDAD 1 (CRÍTICA): Pipeline de Contratación**
- Candidates (候補者 - Candidatos)
- 入社連絡票 (Nyusha Renraku Hyo - Formulario de Nueva Contratación)
- Employees (派遣社員 - Empleados Dispatch)
- Factories (派遣先 - Clientes/Fábricas) - BIEN DEFINIDAS

**PRIORIDAD 2 (ALTA): Operaciones Diarias**
- Apartments (アパート - Viviendas para empleados)
- Yukyu (有給休暇 - Vacaciones Pagadas)

**PRIORIDAD 3 (MEDIA): Control de Horas**
- Timer Cards OCR (タイムカード - Registro de asistencia)
- Procesamiento automático con reglas de fábrica
- Identificación de empleados con OCR

**PRIORIDAD 4 (FUTURA): Finanzas**
- Payroll (給与 - Nómina)
- Integración con timer cards procesados

---

## 👥 SISTEMA DE ROLES (DEFINITIVO)

### Jerarquía de Roles

```
ADMIN (最高管理者)
  ↓
TORISHIMARIYAKU (取締役 - Directores)
  ↓
KEIRI (経理 - Administración/Contabilidad)
  ↓
TANTOSHA (担当者 - Encargados/Supervisores)
  ↓
HAKEN_SHAIN (派遣社員 - Empleados Dispatch)
UKEOI (請負 - Empleados Contratistas)
```

### Permisos por Rol

| Acción | ADMIN | TORISHIMARIYAKU | KEIRI | TANTOSHA | HAKEN_SHAIN |
|--------|-------|-----------------|-------|----------|-------------|
| **Candidates** |
| Crear | ✅ | ✅ | ✅ | ✅ | ❌ |
| Ver | ✅ | ✅ | ✅ | ✅ | ❌ |
| Editar | ✅ | ✅ | ✅ | ✅ | ❌ |
| Eliminar | ✅ | ✅ | ❌ | ❌ | ❌ |
| **入社連絡票** |
| Crear | ✅ | ✅ | ✅ | ✅ | ❌ |
| Aprobar | ✅ | ✅ | ✅ | ❌ | ❌ |
| Ver | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Employees** |
| Crear (via 入社連絡票) | ✅ | ✅ | ✅ | ❌ | ❌ |
| Ver todos | ✅ | ✅ | ✅ | ✅ | ❌ |
| Ver propio | ✅ | ✅ | ✅ | ✅ | ✅ |
| Editar | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Apartments** |
| Asignar | ✅ | ✅ | ✅ | ❌ | ❌ |
| Ver | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Timer Cards** |
| Subir PDF | ✅ | ✅ | ✅ | ✅ | ❌ |
| Aprobar | ✅ | ✅ | ✅ | ❌ | ❌ |
| Ver propios | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Payroll** |
| Calcular | ✅ | ✅ | ✅ | ❌ | ❌ |
| Aprobar | ✅ | ✅ | ❌ | ❌ | ❌ |
| Ver propio | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Yukyu** |
| Crear solicitud | ✅ | ✅ | ✅ | ✅ | ✅ |
| Aprobar | ✅ | ✅ | ✅ | ❌ | ❌ |

### Descripción de Roles

**ADMIN (あなた - Tú)**
- Súper administrador con acceso TOTAL
- Puede hacer TODO sin restricciones
- Gestiona usuarios y permisos

**TORISHIMARIYAKU (取締役 - Jefes/Directores)**
- Segunda jerarquía más alta
- Aprueban contrataciones y decisiones importantes
- Acceso a reportes financieros completos

**KEIRI (経理 - Administración)**
- Manejan contabilidad y finanzas
- Aprueban pagos y nóminas
- Gestionan apartamentos y deducciones

**TANTOSHA (担当者 - Encargados)**
- Supervisores de empleados
- Crean solicitudes pero NO aprueban
- Suben timer cards
- Gestionan operaciones diarias

**HAKEN_SHAIN / UKEOI (Empleados)**
- Acceso limitado: solo ven sus propios datos
- Sueldos y contratos (en el futuro)
- Solicitudes de yukyu

---

## 🗄️ ARQUITECTURA DE BASE DE DATOS

### Tablas Principales (13 Tablas)

```sql
-- USUARIOS Y AUTENTICACIÓN
users (id, username, email, password_hash, role, is_active)
refresh_tokens (id, token, user_id, expires_at, revoked)

-- PERSONAL
candidates (id, rirekisho_id, applicant_id, status, ~60 campos履歴書)
employees (id, hakenmoto_id, rirekisho_id, factory_id, apartment_id, ~60 campos)
contract_workers (id, hakenmoto_id, rirekisho_id, ~60 campos)
staff (id, staff_id, rirekisho_id, ~40 campos)

-- CLIENTES
factories (id, factory_id, company_name, plant_name, config JSON)

-- VIVIENDA
apartments (id, apartment_code, name, capacity, base_rent, config)
apartment_assignments (id, apartment_id, employee_id, start_date, end_date, status)
apartment_factory (id, apartment_id, factory_id, distance_km, commute_minutes)
additional_charges (id, assignment_id, charge_type, amount, status)
rent_deductions (id, assignment_id, year, month, total_deduction, status)

-- DOCUMENTOS
documents (id, candidate_id, employee_id, document_type, file_path, ocr_data)

-- SOLICITUDES
requests (id, hakenmoto_id, candidate_id, request_type, status, employee_data JSONB)

-- ASISTENCIA
timer_cards (id, hakenmoto_id, factory_id, work_date, clock_in, clock_out,
            regular_hours, overtime_hours, night_hours, holiday_hours, is_approved)

-- VACACIONES
yukyu_balances (id, employee_id, fiscal_year, days_assigned, days_used, days_remaining, expires_on)
yukyu_requests (id, employee_id, start_date, end_date, days_requested, status, approved_by)
yukyu_usage_details (id, request_id, balance_id, usage_date, days_deducted)

-- NÓMINA
salary_calculations (id, employee_id, year, month, gross_salary, net_salary,
                    total_regular_hours, total_overtime_hours, apartment_deduction, is_paid)

-- AUDITORÍA
audit_log (id, user_id, action, table_name, record_id, old_values, new_values, ip_address)
admin_audit_logs (id, admin_user_id, action_type, resource_type, previous_value, new_value)

-- CONFIGURACIÓN
system_settings (id, key, value, description)
page_visibility (id, page_key, is_enabled, disabled_message)
role_page_permissions (id, role_key, page_key, is_enabled)
```

### Relaciones Clave

```
Candidate (1) ←──→ (0..N) Employee  [vía rirekisho_id]
Employee (N) ──→ (1) Factory         [vía factory_id]
Employee (N) ──→ (0..1) Apartment    [vía apartment_id]
Employee (1) ←──→ (0..N) TimerCard   [vía hakenmoto_id]
Employee (1) ←──→ (0..N) YukyuBalance
Employee (1) ←──→ (0..N) YukyuRequest
Employee (1) ←──→ (0..N) SalaryCalculation

Candidate (1) ←──→ (0..N) Request    [vía candidate_id]
Request (1) ──→ (0..1) Employee      [vía hakenmoto_id después de aprobar]

Apartment (1) ←──→ (N) ApartmentAssignment
Apartment (N) ←──→ (N) Factory       [vía apartment_factory]
ApartmentAssignment (1) ←──→ (N) AdditionalCharge
ApartmentAssignment (1) ←──→ (N) RentDeduction
```

---

## 📊 PRIORIDAD 1: CANDIDATE → 入社連絡票 → EMPLOYEE

### Estados del Candidate

```
┌─────────┐
│ pending │ → Recién creado, esperando revisión
└────┬────┘
     │ evaluate(👍)
     ↓
┌──────────┐
│ approved │ → Aprobado, se auto-crea 入社連絡票
└────┬─────┘
     │ approve_nyuusha()
     ↓
┌───────┐
│ hired │ → Employee creado, contratación completa
└───────┘

Además:
┌──────────┐
│ rejected │ → No fue aceptado (puede volver a aplicar)
└──────────┘

┌──────────┐
│ resigned │ → Era employee, renunció (puede re-contratar)
└──────────┘
```

### Flujo Completo Paso a Paso

#### **PASO 1: Candidato Aplica (履歴書)**

**Usuario:** KEIRI, TANTOSHA, TORISHIMARIYAKU, ADMIN
**Página:** `/dashboard/candidates/new`
**Endpoint:** `POST /api/candidates/rirekisho/form`

**Proceso:**
1. Usuario sube PDF/imagen de履歴書 O llena formulario manualmente
2. Si hay OCR: Sistema extrae ~60 campos automáticamente
3. Se genera `rirekisho_id` automático: "UNS-001", "UNS-002", etc.
4. Se genera `applicant_id` secuencial: "2000", "2001", etc.
5. Foto comprimida automáticamente (< 200KB)
6. Status inicial: **"pending"**

**Campos Guardados (~60 campos):**
- Información básica: nombre (kanji/kana/roman), fecha nacimiento, género, nacionalidad
- Contacto: teléfono, email, dirección completa
- Documentos: pasaporte, 在留カード, 運転免許証
- Familia: hasta 5 miembros con relación, edad, dependientes
- Experiencia laboral: empresas anteriores, fechas
- Habilidades: NC旋盤, 溶接, フォークリフト, etc.
- Idiomas: japonés (N1-N5), otros idiomas
- Físico: altura, peso, talla ropa, grupo sanguíneo
- Emergencia: contacto de emergencia

**Resultado:**
- Candidate creado con `status = "pending"`
- Visible en `/dashboard/candidates` para revisión

---

#### **PASO 2: Evaluación Rápida (👍/👎)**

**Usuario:** KEIRI, TANTOSHA, TORISHIMARIYAKU, ADMIN
**Página:** `/dashboard/candidates/{id}`
**Endpoint:** `POST /api/candidates/{id}/evaluate`

**Proceso:**
```
Si ADMIN/KEIRI/TORISHIMARIYAKU hace clic en 👍:
  1. candidate.status = "approved"
  2. candidate.approved_by = current_user.id
  3. candidate.approved_at = NOW()

  4. 🆕 AUTO-CREAR 入社連絡票:
     Request.create(
       candidate_id = candidate.id,
       request_type = "NYUUSHA",
       status = "PENDING",
       employee_data = {}  // JSON vacío
     )

Si hace clic en 👎:
  1. candidate.status = "rejected"
  2. reason guardado en notes
```

**Resultado:**
- Candidate: `status = "approved"`
- Request: Nueva入社連絡票 creada automáticamente
- Notificación: "入社連絡票 creada para {nombre}"

---

#### **PASO 3: Llenar Datos de Employee (入社連絡票)**

**Usuario:** KEIRI, TORISHIMARIYAKU, ADMIN (NO tantosha)
**Página:** `/dashboard/requests/{id}/employee-data`
**Endpoint:** `PUT /api/requests/{id}/employee-data`

**Formulario入社連絡票:**

```
┌─────────────────────────────────────────────────────────────────┐
│  📋 入社連絡票 (New Hire Notification Form)                      │
│  Request ID: #12345 | Candidate: 山田太郎 (UNS-123)             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ▼ SECCIÓN 1: Datos del Candidato (Read-Only)                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 氏名 (Nombre):    山田太郎 (Yamada Taro)                    │ │
│  │ 生年月日:         1990-05-15 (35 años)                      │ │
│  │ 国籍:             ベトナム                                  │ │
│  │ 在留資格:         技能実習                                  │ │
│  │ 在留期限:         2026-12-31                                │ │
│  │ 電話:             090-1234-5678                             │ │
│  │ Email:            yamada@example.com                        │ │
│  │ 住所:             愛知県弥富市楠3-13-2                      │ │
│  │ 免許:             普通自動車免許 (2025-08-15まで)            │ │
│  │ 写真:             [Photo Preview]                           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ▼ SECCIÓN 2: Asignación de Fábrica ⭐ NUEVO                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 派遣先企業 (Company):                                        │ │
│  │ [Dropdown] ▼ 高雄工業株式会社                               │ │
│  │            - アサヒフォージ株式会社                          │ │
│  │            - 三幸技研株式会社                                │ │
│  │            - 日本製鋼所                                      │ │
│  │                                                              │ │
│  │ 工場 (Plant):                                                │ │
│  │ [Dropdown] ▼ 本社工場                                        │ │
│  │            - CVJ工場                                         │ │
│  │            - 静岡工場                                        │ │
│  │            - HUB工場                                         │ │
│  │                                                              │ │
│  │ ライン (Line):                                               │ │
│  │ [Dropdown] ▼ リフト作業 (¥1750/h)                           │ │
│  │            - Aライン (¥1650/h)                               │ │
│  │            - Tライン (¥1650/h)                               │ │
│  │            - バリ取り (¥1650/h)                              │ │
│  │                                                              │ │
│  │ 配属先 (Department):  [_______________________]              │ │
│  │                      (ej: 製作課)                            │ │
│  │                                                              │ │
│  │ 仕事内容 (Job Description):                                  │ │
│  │ [Textarea]                                                   │ │
│  │ CVJメス型番の施削加工                                        │ │
│  │                                                              │ │
│  │ 派遣先社員ID (Factory Employee ID):  [E-_______]            │ │
│  │                                                              │ │
│  │ 時給 (Hourly Rate): ¥ [1750] /時間 ✅ Auto-filled          │ │
│  │ 請求単価 (Billing Rate): ¥ [2000] /時間                    │ │
│  │ 差額利益: ¥250 /時間 (自動計算)                             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ▼ SECCIÓN 3: Fechas y Contrato ⭐ NUEVO                       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 入社日 (Hire Date):          [2025-11-15]                   │ │
│  │ 現入社 (Current Hire Date):  [2025-11-15] (si es nuevo)    │ │
│  │ 契約形態 (Contract Type):                                    │ │
│  │ ( ) 派遣社員 (Dispatch)                                     │ │
│  │ (•) 請負 (Contract)                                         │ │
│  │ 雇用期間 (Period):           [2025-11-15] ~ [2026-11-14]   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ▼ SECCIÓN 4: Apartamento (Opcional) ⭐ NUEVO                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ ☐ Asignar apartamento ahora                                 │ │
│  │                                                              │ │
│  │ [Si checked:]                                                │ │
│  │ アパート (Apartment):                                        │ │
│  │ [Autocomplete] サンライズ荘 A-101                           │ │
│  │                                                              │ │
│  │ 🔍 O buscar recomendaciones inteligentes:                   │ │
│  │ [Recomendar Apartamentos] ← scoring automático              │ │
│  │                                                              │ │
│  │ Si seleccionado:                                             │ │
│  │ - 賃料 (Rent): ¥50,000/月                                   │ │
│  │ - 入居日 (Move-in): [2025-11-15]                            │ │
│  │ - 社宅 (Corporate Housing): ☐ Sí                           │ │
│  │ - 住宅手当 (Subsidy): ¥ [0]                                 │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ▼ SECCIÓN 5: Información Bancaria ⭐ NUEVO                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 銀行名 (Bank Name):    [愛知銀行]                           │ │
│  │ 支店名 (Branch):       [当知支店]                           │ │
│  │ 口座番号 (Account):    [1234567890]                         │ │
│  │ 口座名義 (Name):       [ヤマダ タロウ]                      │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ▼ SECCIÓN 6: Emergencia (Opcional - override candidate)       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ ☐ Actualizar contacto de emergencia                         │ │
│  │ 緊急連絡先氏名:  [_______________________]                  │ │
│  │ 続柄:            [_______________________]                  │ │
│  │ 電話番号:        [___-____-____]                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ▼ SECCIÓN 7: Notas Adicionales                                │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 備考 (Notes):                                                │ │
│  │ [Textarea]                                                   │ │
│  │                                                              │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  [Guardar Borrador] [Cancelar]                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Validaciones:**
- Factory requerida ✅
- Hire date requerida ✅
- Jikyu > 0 ✅
- Bank account válido (10-12 dígitos) ✅
- Si apartment checked, apartment_id requerido ✅

**Resultado:**
- Request: `employee_data = {JSON completo con todos los campos}`
- Status: Sigue siendo "PENDING", listo para aprobar

---

#### **PASO 4: Aprobar入社連絡票 → Crear Employee**

**Usuario:** KEIRI, TORISHIMARIYAKU, ADMIN (NO tantosha)
**Página:** `/dashboard/requests/{id}`
**Endpoint:** `POST /api/requests/{id}/approve-nyuusha`

**Proceso:**
```python
1. Validar:
   - request_type == NYUUSHA ✓
   - status == PENDING ✓
   - employee_data != {} ✓
   - candidate_id existe ✓

2. Verificar no duplicado:
   - NO existe Employee con mismo rirekisho_id
   - Si existe → Error "Empleado ya existe"

3. Generar hakenmoto_id automático:
   - SELECT MAX(hakenmoto_id) FROM employees
   - new_hakenmoto_id = max + 1
   - Ejemplo: 1, 2, 3, 4, 5...

4. Crear Employee:
   - Copiar ~40 campos de Candidate:
     * full_name_*, date_of_birth, gender, nationality
     * phone, email, address
     * passport_number, zairyu_card_number, visa_*
     * license_*, emergency_contact_*
     * photo_data_url (FOTO)

   - Agregar campos de employee_data:
     * hakenmoto_id (auto-generado)
     * rirekisho_id (vínculo con Candidate)
     * factory_id, hakensaki_shain_id
     * hire_date, current_hire_date
     * jikyu, position, contract_type
     * apartment_id (si aplica)
     * bank_name, bank_account

   - Status inicial: "active"

5. Actualizar Candidate:
   - candidate.status = "hired"

6. Actualizar Request:
   - request.status = "completed" (済)
   - request.approved_by = current_user.id
   - request.approved_at = NOW()
   - request.hakenmoto_id = new_hakenmoto_id

7. COMMIT todo en una transacción

8. Si employee tiene apartment_id:
   - Crear ApartmentAssignment automáticamente
   - Status: "active"
   - Start date: hire_date
```

**Resultado:**
- ✅ Employee creado con hakenmoto_id único
- ✅ Candidate vinculado (status = "hired")
- ✅ Request marcado como completado (済)
- ✅ Apartment asignado (si aplica)
- ✅ Visible en `/dashboard/employees`

---

### Re-contratación Workflow

**Escenario:** Employee renuncia y vuelve después de 6 meses

**Proceso:**

```
1. Employee actual renuncia:
   ├─ employee.status = "resigned"
   ├─ employee.termination_date = 2025-06-15
   ├─ employee.termination_reason = "帰国"
   └─ candidate.status NO CAMBIA (sigue "hired")

2. Employee quiere volver (6 meses después):
   ├─ ¿Crear nuevo Candidate? ❌ NO
   ├─ Usar mismo Candidate (rirekisho_id = UNS-123) ✅
   ├─ ¿Actualizar datos? Sí, si han cambiado
   └─ candidate.status = "hired" (ya está)

3. Crear nueva 入社連絡票:
   ├─ POST /api/candidates/{id}/evaluate (de nuevo)
   ├─ Se crea Request #2 para mismo candidate
   └─ employee_data se llena de nuevo

4. Aprobar nueva 入社連絡票:
   ├─ Se genera NUEVO hakenmoto_id (ej: 456)
   ├─ Se crea NUEVO Employee con mismo rirekisho_id
   ├─ Resultado:
   │  Employee #1 (hakenmoto_id=123, status="resigned")
   │  Employee #2 (hakenmoto_id=456, status="active")
   └─ Ambos vinculados a Candidate UNS-123
```

**Historial:**
```sql
SELECT * FROM employees WHERE rirekisho_id = 'UNS-123';
-- Resultado:
-- id=1, hakenmoto_id=123, status=resigned, hire_date=2025-01-01, termination_date=2025-06-15
-- id=2, hakenmoto_id=456, status=active, hire_date=2025-12-01, termination_date=NULL
```

---

## 🏭 PRIORIDAD 1.5: FACTORIES (Bien Definidas)

### Estructura Actual (JSON Files)

**Ubicación:** `config/factories/*.json`

**Ejemplo:** `高雄工業株式会社_本社工場.json`

```json
{
  "factory_id": "高雄工業株式会社_本社工場",
  "client_company": {
    "name": "高雄工業株式会社",
    "address": "愛知県弥富市楠三丁目13番地2",
    "phone": "0567-68-8110",
    "responsible_person": {
      "department": "愛知事業所",
      "name": "部長 安藤 忍",
      "phone": "0567-68-8110"
    },
    "complaint_handler": {
      "department": "人事広報管理部",
      "name": "部長 山田 茂",
      "phone": "0567-68-8110"
    }
  },
  "plant": {
    "name": "本社工場",
    "address": "愛知県弥富市楠三丁目13番地2",
    "phone": "0567-68-8110"
  },
  "lines": [
    {
      "line_id": "Factory-39",
      "assignment": {
        "department": "第一営業部本社営業課",
        "line": "リフト作業",
        "supervisor": {
          "department": "",
          "name": "係長 坂上 舞",
          "phone": "0567-68-8110"
        }
      },
      "job": {
        "description": "鋳造材料の工場内加工ラインへの供給",
        "hourly_rate": 1750.0
      }
    },
    {
      "line_id": "Factory-40",
      "assignment": {
        "department": "製作課",
        "line": "Aライン",
        "supervisor": {
          "name": "係長 山本 絋平"
        }
      },
      "job": {
        "description": "CVJメス型番の施削加工",
        "hourly_rate": 1650.0
      }
    }
  ],
  "schedule": {
    "work_hours": "昼勤：7時00分～15時30分　夜勤：19時00分～3時30分",
    "break_time": "昼勤：11時00分～11時45分 まで　夜勤：23時00分～23時45分　まで　（45分）",
    "calendar": "月～金　(シフトに準ずる）休日は、土曜日・日曜日・年末年始・GW・夏季休暇",
    "start_date": "2024-10-01",
    "end_date": "2025-09-30",
    "non_work_day_labor": "１ヶ月に２日の範囲内で命ずることができる。",
    "overtime_labor": "3時間/日、42時間/月、320時間/年迄とする。",
    "time_unit": "15.0"
  },
  "payment": {
    "closing_date": "15日",
    "payment_date": "当月末日",
    "bank_account": "愛知銀行　当知支店　普通2075479",
    "worker_closing_date": "15日",
    "worker_payment_date": "15日"
  }
}
```

### Propuesta de Mejora: DB Normalizada

**Razón:** JSON files difíciles de mantener, sin validación, sin cascading dropdowns

**Nueva Estructura:**

```sql
-- Companies (企業)
CREATE TABLE companies (
  id SERIAL PRIMARY KEY,
  company_code VARCHAR(50) UNIQUE NOT NULL,
  company_name VARCHAR(200) NOT NULL,
  address TEXT,
  phone VARCHAR(20),
  responsible_person_name VARCHAR(100),
  responsible_person_dept VARCHAR(100),
  responsible_person_phone VARCHAR(20),
  complaint_handler_name VARCHAR(100),
  complaint_handler_dept VARCHAR(100),
  complaint_handler_phone VARCHAR(20),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Plants (工場)
CREATE TABLE plants (
  id SERIAL PRIMARY KEY,
  company_id INT REFERENCES companies(id) ON DELETE CASCADE,
  plant_code VARCHAR(50) UNIQUE NOT NULL,
  plant_name VARCHAR(200) NOT NULL,
  factory_id VARCHAR(200) UNIQUE NOT NULL, -- Legacy: "Company__Plant"
  address TEXT,
  phone VARCHAR(20),

  -- Schedule config
  work_hours TEXT, -- "昼勤：7:00～15:30　夜勤：19:00～3:30"
  break_time TEXT, -- "昼勤：11:00～11:45（45分）"
  calendar TEXT,   -- "月～金 (シフトに準ずる)"
  overtime_limit_daily INT,   -- 3時間/日
  overtime_limit_monthly INT, -- 42時間/月
  overtime_limit_yearly INT,  -- 320時間/年
  time_unit NUMERIC(5,2),     -- 15.0 (minutos para redondeo)

  -- Payment config
  closing_date VARCHAR(10),        -- "15日"
  payment_date VARCHAR(10),        -- "当月末日"
  worker_closing_date VARCHAR(10), -- "15日"
  worker_payment_date VARCHAR(10), -- "15日"
  bank_account TEXT,

  -- Dates
  contract_start_date DATE,
  contract_end_date DATE,

  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Lines (ライン)
CREATE TABLE lines (
  id SERIAL PRIMARY KEY,
  plant_id INT REFERENCES plants(id) ON DELETE CASCADE,
  line_code VARCHAR(50) NOT NULL,
  line_name VARCHAR(200) NOT NULL,
  department VARCHAR(200),        -- 製作課
  supervisor_name VARCHAR(100),   -- 係長 山本 絋平
  supervisor_dept VARCHAR(100),
  supervisor_phone VARCHAR(20),
  job_description TEXT,           -- CVJメス型番の施削加工
  hourly_rate NUMERIC(10,2) NOT NULL, -- ¥1650/h
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(plant_id, line_code)
);

-- Índices
CREATE INDEX idx_companies_code ON companies(company_code);
CREATE INDEX idx_plants_company ON plants(company_id);
CREATE INDEX idx_plants_factory_id ON plants(factory_id);
CREATE INDEX idx_lines_plant ON lines(plant_id);
```

### UI Jerárquica (Tree View)

**Página:** `/dashboard/factories`

```
┌─────────────────────────────────────────────────────────────────┐
│  🏭 FACTORIES MANAGEMENT                      [+ Add Company]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  🔍 Search: [____________]  Filter: [All] [Active] [Inactive]   │
│                                                                  │
│  📋 Companies (14 total)                                         │
│                                                                  │
│  ┌─ 🏢 高雄工業株式会社 (Takao Kogyo)          [Edit] [Delete]  │
│  │  📍 愛知県弥富市楠三丁目13番地2                               │
│  │  ☎ 0567-68-8110                                              │
│  │  👤 Responsible: 部長 安藤 忍                                │
│  │                                                               │
│  │  ├─ 🏭 本社工場 (Headquarters Plant)       [Edit] [Delete]  │
│  │  │  📍 Same address                                          │
│  │  │  ⏰ 昼勤：7:00～15:30 / 夜勤：19:00～3:30                 │
│  │  │  💰 Closing: 15日 | Payment: 当月末日                     │
│  │  │  📊 8 lines, 45 active employees                         │
│  │  │                                                            │
│  │  │  ├─ 📦 リフト作業 (Forklift Work)      [Edit] [Delete]   │
│  │  │  │  💵 ¥1,750/h                                           │
│  │  │  │  👤 Supervisor: 係長 坂上 舞                           │
│  │  │  │  👷 5 employees assigned                               │
│  │  │  │                                                         │
│  │  │  ├─ 🔧 Aライン (A Line)                                   │
│  │  │  │  💵 ¥1,650/h                                           │
│  │  │  │  👤 Supervisor: 係長 山本 絋平                         │
│  │  │  │  👷 8 employees assigned                               │
│  │  │  │                                                         │
│  │  │  ├─ 🔧 Tライン (T Line)                                   │
│  │  │  ├─ 🔨 バリ取り (Deburring)                              │
│  │  │  ├─ ♻️ 切紛回収 (Chip Collection)                        │
│  │  │  ├─ 🔧 Fライン (F Line)                                   │
│  │  │  ├─ 🔩 六面加工 (6-Face Processing)                      │
│  │  │  └─ 🔧 Gライン (G Line)                                   │
│  │  │                                                            │
│  │  ├─ 🏭 CVJ工場 (CVJ Plant)                [Edit] [Delete]   │
│  │  │  📊 8 lines, 32 employees                                │
│  │  │                                                            │
│  │  ├─ 🏭 静岡工場 (Shizuoka Plant)           [Edit] [Delete]   │
│  │  │  📊 6 lines, 18 employees                                │
│  │  │                                                            │
│  │  └─ 🏭 HUB工場 (HUB Plant)                 [Edit] [Delete]   │
│  │     📊 4 lines, 12 employees                                │
│  │                                                               │
│  └─ [Expand/Collapse]                                           │
│                                                                  │
│  ┌─ 🏢 アサヒフォージ株式会社 (Asahi Forge)     [Edit] [Delete]  │
│  │  📍 岡山県真庭市...                                           │
│  │  ☎ 0867-XX-XXXX                                             │
│  │                                                               │
│  │  └─ 🏭 真庭工場 (Maniwa Plant)             [Edit] [Delete]   │
│  │     📊 5 lines, 22 employees                                │
│  │                                                               │
│  └─ [Expand/Collapse]                                           │
│                                                                  │
│  ... (12 more companies)                                        │
│                                                                  │
│  [Import from JSON] [Export to JSON] [Bulk Edit]                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Cascading Dropdowns en入社連絡票

**Implementación:**

```typescript
// frontend/components/nyuusha/factory-selector.tsx

const [companies, setCompanies] = useState([])
const [plants, setPlants] = useState([])
const [lines, setLines] = useState([])

const [selectedCompany, setSelectedCompany] = useState(null)
const [selectedPlant, setSelectedPlant] = useState(null)
const [selectedLine, setSelectedLine] = useState(null)

// 1. Cargar companies al montar
useEffect(() => {
  fetch('/api/factories/companies').then(setCompanies)
}, [])

// 2. Cuando selecciona company, cargar sus plants
useEffect(() => {
  if (selectedCompany) {
    fetch(`/api/factories/companies/${selectedCompany}/plants`)
      .then(setPlants)
  }
}, [selectedCompany])

// 3. Cuando selecciona plant, cargar sus lines
useEffect(() => {
  if (selectedPlant) {
    fetch(`/api/factories/plants/${selectedPlant}/lines`)
      .then(setLines)
  }
}, [selectedPlant])

// 4. Cuando selecciona line, auto-fill hourly_rate
useEffect(() => {
  if (selectedLine) {
    const line = lines.find(l => l.id === selectedLine)
    setValue('jikyu', line.hourly_rate) // ✅ Auto-fill
  }
}, [selectedLine])

return (
  <div>
    <Select
      label="Company"
      options={companies}
      onChange={setSelectedCompany}
    />

    <Select
      label="Plant"
      options={plants}
      onChange={setSelectedPlant}
      disabled={!selectedCompany}
    />

    <Select
      label="Line"
      options={lines}
      onChange={setSelectedLine}
      disabled={!selectedPlant}
    />

    <Input
      label="Hourly Rate"
      value={form.jikyu}
      readOnly
      suffix="円/時間"
    />
  </div>
)
```

### Factory Rules para Timer Cards

**Uso:** Cuando se procesan timer cards, se leen las reglas del plant

```python
# backend/app/services/timer_card_processor.py

def calculate_hours_with_factory_rules(timer_card, plant_config):
    """
    Aplica reglas específicas de la factory para calcular horas.
    """
    # 1. Parse work_hours
    work_hours = parse_work_hours(plant_config.work_hours)
    # Ejemplo: {"day_shift": ("07:00", "15:30"), "night_shift": ("19:00", "03:30")}

    # 2. Determinar shift type
    shift_type = determine_shift(timer_card.clock_in, work_hours)

    # 3. Parse break_time
    break_minutes = parse_break_time(plant_config.break_time, shift_type)
    # Ejemplo: day_shift = 45 min

    # 4. Calcular total worked
    total_minutes = calculate_minutes(timer_card.clock_in, timer_card.clock_out)
    total_minutes -= break_minutes

    # 5. Calcular regular vs overtime usando work_hours del plant
    regular_hours_limit = calculate_regular_limit(work_hours, shift_type)
    # Ejemplo: day_shift = 8.5h (7:00-15:30 menos 45min break)

    total_hours = total_minutes / 60

    if total_hours <= regular_hours_limit:
        regular_hours = total_hours
        overtime_hours = 0
    else:
        regular_hours = regular_hours_limit
        overtime_hours = total_hours - regular_hours_limit

    # 6. Validar límites de overtime
    if overtime_hours > plant_config.overtime_limit_daily:
        raise ValidationError(
            f"Overtime exceeds daily limit: {overtime_hours}h > {plant_config.overtime_limit_daily}h"
        )

    # 7. Aplicar time_unit (redondeo)
    time_unit = plant_config.time_unit  # 15.0 minutos
    regular_hours = round_to_unit(regular_hours, time_unit)
    overtime_hours = round_to_unit(overtime_hours, time_unit)

    # 8. Detectar night hours (22:00-05:00)
    night_hours = calculate_night_hours(timer_card.clock_in, timer_card.clock_out)

    # 9. Detectar holiday
    is_holiday = is_japanese_holiday(timer_card.work_date)
    holiday_hours = total_hours if is_holiday else 0

    return {
        "regular_hours": regular_hours,
        "overtime_hours": overtime_hours,
        "night_hours": night_hours,
        "holiday_hours": holiday_hours,
        "shift_type": shift_type
    }
```

---

## 🏠 PRIORIDAD 2: APARTMENTS (Sistema Inteligente)

### Vista de Disponibilidad

**Página:** `/dashboard/apartments`

**Card View con Status Visual:**

```
┌─────────────────────────────────────────────────────────────────┐
│  🏢 APARTMENTS OVERVIEW                   [+ Add Apartment]      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📊 SUMMARY                                                      │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐     │
│  │ Total    │Available │ Partial  │ Full     │ Maint.   │     │
│  │ 45 units │ 12 🟢   │ 18 🟡   │ 10 🔴   │ 5 🔵    │     │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘     │
│                                                                  │
│  💰 Occupancy: 73% ████████████░░░░   Rent: ¥2,450,000/month   │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│  📍 APARTMENTS                                                   │
│                                                                  │
│  ┌──────────────────────┐  ┌──────────────────────┐           │
│  │ 🟢 AVAILABLE         │  │ 🟡 PARTIAL           │           │
│  │ サンライズ荘 A-101   │  │ グリーンパーク 203    │           │
│  │                      │  │                      │           │
│  │ 📍 弥富市楠3-13-2    │  │ 📍 名古屋市港区      │           │
│  │ 🛏️  0/4 beds         │  │ 🛏️  2/3 beds         │           │
│  │ 💰 ¥50,000/月        │  │ 💰 ¥45,000/月        │           │
│  │ 🏭 高雄工業: 2.3km    │  │ 🏭 高雄工業: 4.8km    │           │
│  │ 🚗 Parking: Yes      │  │ 🚗 Parking: Yes      │           │
│  │                      │  │ Residents:           │           │
│  │ [Assign Employee]    │  │ - Nguyen Van A       │           │
│  │                      │  │ - Tran Thi B         │           │
│  │                      │  │ [+ Add Resident]     │           │
│  └──────────────────────┘  └──────────────────────┘           │
│                                                                  │
│  ┌──────────────────────┐  ┌──────────────────────┐           │
│  │ 🔴 FULL              │  │ 🔵 MAINTENANCE       │           │
│  │ 富士マンション 304   │  │ コーポ田中 B-205     │           │
│  │                      │  │                      │           │
│  │ 📍 あま市甚目寺      │  │ 📍 海部郡蟹江町      │           │
│  │ 🛏️  4/4 beds         │  │ 🛏️  ─/2 beds         │           │
│  │ 💰 ¥55,000/月        │  │ 💰 ¥40,000/月        │           │
│  │ 🏭 日本製鋼: 1.5km    │  │ 🔧 Water leak repair │           │
│  │ 🚗 Parking: No       │  │ 📅 ETA: 2025-11-20   │           │
│  │ Residents:           │  │                      │           │
│  │ - Liu Wei            │  │ Previous:            │           │
│  │ - Chen Ming          │  │ - Pham Van C         │           │
│  │ - Wang Fang          │  │                      │           │
│  │ - Zhang Li           │  │ [View Repair Log]    │           │
│  │ [View Details]       │  │                      │           │
│  └──────────────────────┘  └──────────────────────┘           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Auto-asignación Inteligente

**Algoritmo con Scoring:**

```python
# backend/app/services/apartment_recommendation_service.py

WEIGHTS = {
    'proximity_to_factory': 40,      # 40% - Más importante
    'availability': 25,               # 25% - Segundo
    'price_affordability': 15,        # 15% - Tercero
    'roommate_compatibility': 10,     # 10% - Cuarto
    'transportation': 10              # 10% - Quinto
}

def recommend_apartments(employee_id, max_results=5):
    employee = get_employee(employee_id)
    factory = get_factory(employee.factory_id)
    apartments = get_available_apartments()

    scored = []

    for apt in apartments:
        # Calcular scoring individual
        scores = {
            'proximity': score_proximity(apt, factory),
            'availability': score_availability(apt),
            'price': score_price(apt, employee),
            'compatibility': score_compatibility(apt, employee),
            'transportation': score_transportation(apt, employee)
        }

        # Total weighted
        total = (
            scores['proximity'] * WEIGHTS['proximity_to_factory'] +
            scores['availability'] * WEIGHTS['availability'] +
            scores['price'] * WEIGHTS['price_affordability'] +
            scores['compatibility'] * WEIGHTS['roommate_compatibility'] +
            scores['transportation'] * WEIGHTS['transportation']
        ) / 100

        scored.append({
            'apartment': apt,
            'total_score': total,
            'breakdown': scores,
            'reason': generate_reason(scores)
        })

    # Ordenar por score
    scored.sort(key=lambda x: x['total_score'], reverse=True)

    return scored[:max_results]

def score_proximity(apartment, factory):
    """< 2km = 100, 2-5km = 80, 5-10km = 50, >10km = 20"""
    assoc = get_apartment_factory_association(apartment.id, factory.id)
    if not assoc:
        return 0
    distance = assoc.distance_km
    if distance < 2: return 100
    elif distance < 5: return 80
    elif distance < 10: return 50
    else: return 20

def score_availability(apartment):
    """Completamente vacío = 100, 1 bed = 80, 2+ beds = 90+"""
    occupied = count_active_assignments(apartment.id)
    available_beds = apartment.capacity - occupied
    if occupied == 0: return 100
    elif available_beds >= 3: return 100
    elif available_beds == 2: return 90
    elif available_beds == 1: return 80
    else: return 0

def score_price(apartment, employee):
    """Rent < 20% salary = 100, 20-30% = 80, 30-40% = 50, >40% = 20"""
    monthly_salary = employee.jikyu * 8 * 22  # Aproximado
    rent = apartment.base_rent
    percentage = (rent / monthly_salary) * 100
    if percentage < 20: return 100
    elif percentage < 30: return 80
    elif percentage < 40: return 50
    else: return 20

def score_compatibility(apartment, employee):
    """Same nationality +50, same language +30, age diff <10 +20"""
    roommates = get_current_residents(apartment.id)
    if not roommates:
        return 100  # No roommates = 100% compatible

    score = 0
    same_nationality = any(r.nationality == employee.nationality for r in roommates)
    if same_nationality:
        score += 50
        score += 30  # Assume same language

    for roommate in roommates:
        age_diff = abs(calculate_age(employee.date_of_birth) - calculate_age(roommate.date_of_birth))
        if age_diff < 10:
            score += 20
            break

    return min(score, 100)

def score_transportation(apartment, employee):
    """Has car + parking = 100, no car + no parking = 100, mismatch = 50"""
    has_car = bool(employee.license_number)
    has_parking = apartment.parking_spaces > 0
    if has_car and has_parking: return 100
    elif not has_car and not has_parking: return 100
    else: return 50
```

**UI de Recomendaciones:**

```
┌─────────────────────────────────────────────────────────────────┐
│  🔍 RECOMMENDED APARTMENTS FOR: Nguyen Van A                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ⭐ #1: サンライズ荘 A-101                   Score: 92.5/100    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 📍 弥富市楠3-13-2                                           │ │
│  │ 💰 ¥50,000/月 (25% of salary - affordable!)               │ │
│  │ 🛏️  0/4 beds - Completely available                        │ │
│  │ 🏭 高雄工業: 2.3km - Very close!                           │ │
│  │ 🚗 Parking: Yes - Perfect match (employee has car)        │ │
│  │                                                             │ │
│  │ 📊 Breakdown:                                               │ │
│  │ - Proximity: 100/100 (< 2km)                               │ │
│  │ - Availability: 100/100 (empty)                            │ │
│  │ - Price: 80/100 (25% salary)                               │ │
│  │ - Compatibility: 100/100 (no roommates)                    │ │
│  │ - Transportation: 100/100 (has parking)                    │ │
│  │                                                             │ │
│  │ [Assign to This Apartment]                                 │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ⭐ #2: グリーンパーク 203                   Score: 78.0/100    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 📍 名古屋市港区                                             │ │
│  │ 💰 ¥45,000/月 (18% of salary - very affordable!)          │ │
│  │ 🛏️  1/3 beds - 2 beds available                            │ │
│  │ 🏭 高雄工業: 4.8km - Close                                 │ │
│  │ 🚗 Parking: Yes                                            │ │
│  │ 👥 Roommates: Tran Thi B (Vietnam, 28 years old)          │ │
│  │                                                             │ │
│  │ [Assign to This Apartment]                                 │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ... (3 more recommendations)                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Capacity Tracking

**Página:** `/dashboard/apartments/{id}/capacity`

```
┌─────────────────────────────────────────────────────────────────┐
│  🛏️  CAPACITY TRACKER - サンライズ荘 A-101                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Occupancy: 2/4 beds  ████████░░░░░░░░ 50%                      │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ BED 1 🟢 OCCUPIED                                         │  │
│  │ ├─ Name: Nguyen Van A (阮文A)                             │  │
│  │ ├─ Move-in: 2025-01-15                                    │  │
│  │ ├─ Factory: 高雄工業_本社工場                             │  │
│  │ ├─ Rent: ¥50,000/月                                       │  │
│  │ └─ [View Details] [End Assignment]                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ BED 2 🟢 OCCUPIED                                         │  │
│  │ ├─ Name: Tran Thi B (陳氏B)                               │  │
│  │ ├─ Move-in: 2025-03-01                                    │  │
│  │ └─ [View Details] [End Assignment]                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ BED 3 ⚪ AVAILABLE                                        │  │
│  │ └─ [Assign Employee]                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ BED 4 ⚪ AVAILABLE                                        │  │
│  │ └─ [Assign Employee]                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ⚠️  ALERTS: None                                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

-- Si está lleno:
┌─────────────────────────────────────────────────────────────────┐
│  🛏️  CAPACITY TRACKER - 富士マンション 304                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Occupancy: 4/4 beds  ████████████████ 100% 🔴 FULL            │
│                                                                  │
│  (4 beds shown occupied)                                         │
│                                                                  │
│  ⚠️  ALERTS:                                                     │
│  🔴 CRITICAL: Apartment at maximum capacity                     │
│  📅 Bed 2 contract expires in 15 days (2025-11-28)              │
│                                                                  │
│  💡 Want to assign another employee?                             │
│     Requires ADMIN approval                                      │
│     [Request Override] [Find Alternative]                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Features Inteligentes

**1. Transfer Suggestions:**
```python
# Trigger: cuando employee.factory_id cambia
if employee.apartment_id and new_factory_distance > 10km:
    recommendations = recommend_apartments(employee_id)
    send_alert("Consider apartment transfer", recommendations)
```

**2. Contract Expiry Alerts:**
```python
# Cron job diario
def check_expiring_contracts():
    expiring_30 = get_assignments_expiring_in(30)
    expiring_60 = get_assignments_expiring_in(60)
    expiring_90 = get_assignments_expiring_in(90)

    for assignment in expiring_30:
        send_email(assignment.employee, "Contract expires in 30 days")
        send_line(assignment.employee, "契約が30日後に期限切れになります")
```

**3. Auto Rent Deductions:**
```python
# Cron job: 1er día de cada mes
def auto_generate_monthly_deductions(year, month):
    active_assignments = get_active_assignments()

    for assignment in active_assignments:
        # Calcular rent (prorate si es necesario)
        if assignment.is_prorated:
            base_rent = calculate_prorated_rent(assignment, year, month)
        else:
            base_rent = assignment.monthly_rent

        # Obtener cargos adicionales del mes
        additional = sum_additional_charges(assignment, year, month)

        # Crear deducción
        RentDeduction.create(
            assignment_id=assignment.id,
            employee_id=assignment.employee_id,
            year=year,
            month=month,
            base_rent=base_rent,
            additional_charges=additional,
            total_deduction=base_rent + additional,
            status="pending"
        )
```

**4. Cleaning Fee Auto-add:**
```python
# Cuando se termina assignment
def end_apartment_assignment(assignment_id, end_date):
    assignment = get_assignment(assignment_id)
    apartment = assignment.apartment

    # Terminar assignment
    assignment.end_date = end_date
    assignment.status = "ended"

    # Auto agregar cleaning fee
    cleaning_fee = apartment.default_cleaning_fee or 20000
    AdditionalCharge.create(
        assignment_id=assignment.id,
        employee_id=assignment.employee_id,
        charge_type="cleaning",
        description="清掃費用 (退去時)",
        amount=cleaning_fee,
        charge_date=end_date,
        status="pending"
    )
```

---

## 📅 PRIORIDAD 2.5: YUKYU (有給休暇)

### Sistema Ya Implementado ✅

**Estado Actual:** Sistema COMPLETO y funcional

**Tablas:**
- `yukyu_balances` - Registros de yukyu por año fiscal
- `yukyu_requests` - Solicitudes de yukyu
- `yukyu_usage_details` - Detalle de uso (LIFO)

**Workflow:**
1. **Acumulación Automática:** Basada en hire_date
   - 6 meses: 10 días
   - 18 meses: 11 días
   - 30 meses: 12 días
   - 42 meses: 14 días
   - 54 meses: 16 días
   - 66+ meses: 18-20 días

2. **Solicitud:** TANTOSHA crea request para employee
3. **Aprobación:** KEIRI o TORISHIMARIYAKU aprueba/rechaza
4. **Deducción:** Sistema usa LIFO (newest balances first)
5. **Expiración:** 2 años (時効)

**APIs Existentes:**
- `GET /api/yukyu/balances/{employee_id}` - Ver balance
- `POST /api/yukyu/requests` - Crear solicitud
- `PUT /api/yukyu/requests/{id}/approve` - Aprobar
- `PUT /api/yukyu/requests/{id}/reject` - Rechazar
- `GET /api/yukyu/summary/{employee_id}` - Resumen

**Frontend:** `/dashboard/yukyu`

✅ **No requiere cambios, está completo**

---

## 📄 PRIORIDAD 3: TIMER CARDS OCR

### Flujo Completo

#### **PASO 1: Upload PDF**

**Usuario:** KEIRI, TANTOSHA, TORISHIMARIYAKU, ADMIN
**Página:** `/dashboard/timercards/upload`
**Endpoint:** `POST /api/timercards/ocr/upload`

**UI:**

```
┌─────────────────────────────────────────────────────────────────┐
│  📄 UPLOAD TIMER CARDS PDF                                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📅 対象月 (Target Month):  [November 2025 ▼]                   │
│                                                                  │
│  🏭 派遣先 (Factory):       [高雄工業_本社工場 ▼]               │
│                                                                  │
│  📂 タイムカードPDF (PDF File):                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                                                             │ │
│  │          Drag & Drop PDF here                              │ │
│  │               or                                            │ │
│  │          [Browse Files]                                     │ │
│  │                                                             │ │
│  │  Supported: PDF (max 50MB)                                 │ │
│  │  Expected format: Multi-page, one employee per page        │ │
│  │                                                             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ✅ ファイル選択済み: takao_timercards_2025-11.pdf (12.5MB)    │
│     Pages: 25 | Estimated employees: 25                         │
│                                                                  │
│  [Upload and Process] [Cancel]                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### **PASO 2: OCR Processing**

**Backend Process:**

```python
# backend/app/services/timer_card_ocr_service.py

def process_timer_card_pdf(file_path, factory_id, year, month):
    """
    Procesa PDF de timer cards con OCR.
    """
    # 1. Extraer páginas
    pdf = extract_pdf_pages(file_path)

    # 2. Obtener factory config
    plant = get_plant_by_factory_id(factory_id)
    factory_config = {
        'work_hours': plant.work_hours,
        'break_time': plant.break_time,
        'overtime_limit_daily': plant.overtime_limit_daily,
        'overtime_limit_monthly': plant.overtime_limit_monthly,
        'time_unit': plant.time_unit
    }

    results = []

    # 3. Procesar cada página (un employee por página)
    for page_num, page in enumerate(pdf.pages):
        try:
            # 4. Extraer header (factory name, employee info)
            header = extract_header(page)

            # 5. Identificar employee con fuzzy matching
            employee = identify_employee(
                name=header.employee_name,
                employee_id=header.employee_id,
                factory_id=factory_id,
                confidence_threshold=85
            )

            if not employee:
                results.append({
                    'page': page_num + 1,
                    'status': 'error',
                    'error': 'Employee not found',
                    'ocr_data': header
                })
                continue

            # 6. Extraer tabla de asistencia (31 días)
            table = extract_attendance_table(page)
            # table = [
            #   {'date': '2025-11-01', 'clock_in': '07:00', 'clock_out': '17:30', 'break': '45分', 'notes': ''},
            #   {'date': '2025-11-02', 'clock_in': '07:00', 'clock_out': '19:45', 'break': '45分', 'notes': '残業'},
            #   ...
            # ]

            # 7. Procesar cada día
            daily_records = []
            for row in table:
                if not row['clock_in']:  # Día sin trabajo (休日)
                    continue

                # Parsear tiempos
                clock_in = parse_time(row['clock_in'])
                clock_out = parse_time(row['clock_out'])
                break_minutes = parse_break(row['break'])

                # Aplicar factory rules
                hours = calculate_hours_with_factory_rules(
                    clock_in=clock_in,
                    clock_out=clock_out,
                    break_minutes=break_minutes,
                    work_date=row['date'],
                    factory_config=factory_config
                )

                # Validar límites
                validation = validate_hours(hours, factory_config)

                daily_records.append({
                    'work_date': row['date'],
                    'clock_in': clock_in,
                    'clock_out': clock_out,
                    'break_minutes': break_minutes,
                    'regular_hours': hours['regular_hours'],
                    'overtime_hours': hours['overtime_hours'],
                    'night_hours': hours['night_hours'],
                    'holiday_hours': hours['holiday_hours'],
                    'total_weighted_hours': calculate_weighted_total(hours),
                    'shift_type': hours['shift_type'],
                    'validation_errors': validation['errors'],
                    'validation_warnings': validation['warnings'],
                    'ocr_confidence': header.confidence
                })

            results.append({
                'page': page_num + 1,
                'status': 'success',
                'employee': employee,
                'records': daily_records,
                'monthly_totals': calculate_monthly_totals(daily_records)
            })

        except Exception as e:
            results.append({
                'page': page_num + 1,
                'status': 'error',
                'error': str(e)
            })

    return results
```

**Identificación de Employee (Fuzzy Matching):**

```python
def identify_employee(name, employee_id, factory_id, confidence_threshold=85):
    """
    Identifica employee con fuzzy matching.
    """
    # 1. Buscar por employee_id exacto
    if employee_id:
        employee = Employee.query.filter(
            Employee.hakensaki_shain_id == employee_id,
            Employee.factory_id == factory_id
        ).first()
        if employee:
            return {'employee': employee, 'confidence': 100, 'match_type': 'id'}

    # 2. Buscar por nombre con fuzzy matching
    factory_employees = Employee.query.filter(
        Employee.factory_id == factory_id,
        Employee.is_active == True
    ).all()

    best_match = None
    best_score = 0

    for emp in factory_employees:
        # Comparar con nombres en diferentes formatos
        scores = [
            fuzz.ratio(name, emp.full_name_kanji),
            fuzz.ratio(name, emp.full_name_kana),
            fuzz.ratio(name, emp.full_name_roman)
        ]
        score = max(scores)

        if score > best_score:
            best_score = score
            best_match = emp

    # 3. Retornar si confidence >= threshold
    if best_score >= confidence_threshold:
        return {'employee': best_match, 'confidence': best_score, 'match_type': 'name'}

    # 4. No encontrado
    return None
```

**Aplicar Factory Rules:**

```python
def calculate_hours_with_factory_rules(clock_in, clock_out, break_minutes, work_date, factory_config):
    """
    Calcula horas aplicando reglas de factory.
    """
    # 1. Parse work_hours
    work_hours = parse_work_hours(factory_config['work_hours'])
    # {'day_shift': ('07:00', '15:30'), 'night_shift': ('19:00', '03:30')}

    # 2. Determinar shift
    shift_type = determine_shift(clock_in, work_hours)

    # 3. Calcular total
    total_minutes = (clock_out - clock_in).total_seconds() / 60
    total_minutes -= break_minutes
    total_hours = total_minutes / 60

    # 4. Regular vs overtime
    if shift_type == 'day_shift':
        regular_limit = 8.5  # 7:00-15:30 = 8.5h - 0.75h break = 7.75h trabajo
    elif shift_type == 'night_shift':
        regular_limit = 8.5  # 19:00-03:30 = 8.5h - 0.75h break = 7.75h trabajo
    else:
        regular_limit = 8.0

    if total_hours <= regular_limit:
        regular_hours = total_hours
        overtime_hours = 0
    else:
        regular_hours = regular_limit
        overtime_hours = total_hours - regular_limit

    # 5. Night hours (22:00-05:00)
    night_hours = calculate_night_hours(clock_in, clock_out)

    # 6. Holiday
    is_holiday = is_japanese_holiday(work_date)
    holiday_hours = total_hours if is_holiday else 0

    # 7. Redondeo según time_unit
    time_unit = factory_config['time_unit'] / 60  # 15 min = 0.25h
    regular_hours = round_to_unit(regular_hours, time_unit)
    overtime_hours = round_to_unit(overtime_hours, time_unit)
    night_hours = round_to_unit(night_hours, time_unit)

    return {
        'regular_hours': regular_hours,
        'overtime_hours': overtime_hours,
        'night_hours': night_hours,
        'holiday_hours': holiday_hours,
        'shift_type': shift_type
    }
```

#### **PASO 3: Review UI**

**Página:** `/dashboard/timercards/review/{batch_id}`

```
┌─────────────────────────────────────────────────────────────────┐
│  📊 TIMER CARDS REVIEW - November 2025                          │
│  Factory: 高雄工業_本社工場 | Employees: 25 | Total Records: 545│
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📋 VALIDATION SUMMARY                                           │
│  ┌──────────┬───────────┬───────────┬──────────┐               │
│  │ Success  │ Errors    │ Warnings  │ Pending  │               │
│  │ 22 ✅   │ 1 🔴     │ 2 ⚠️     │ 25       │               │
│  └──────────┴───────────┴───────────┴──────────┘               │
│                                                                  │
│  🔴 Errors (1):                                                  │
│  - Page 15: Employee "Tran Thi 8" not found (88% match)        │
│                                                                  │
│  ⚠️  Warnings (2):                                               │
│  - Nguyen Van A (11/12): Overtime 3.5h > 3h limit              │
│  - Liu Wei (11/20): Total monthly overtime 45h > 42h limit     │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│  📊 EMPLOYEE GRID (Editable)                    [Export Excel]  │
│                                                                  │
│  🔍 Filter: [All] [Errors Only] [Warnings Only]                │
│                                                                  │
│  ┌─────┬────────────┬────────┬───────┬────────┬───────┬──────┐│
│  │ Sel │ Employee   │ Regular│ Over  │ Night  │Holiday│Status││
│  ├─────┼────────────┼────────┼───────┼────────┼───────┼──────┤│
│  │ ☐  │Nguyen Van A│ 170.5h │ 12.0h │ 22.0h  │  0h   │ ⚠️  ││
│  │     │阮文A       │        │(3.5h  │        │       │      ││
│  │     │EMP-001     │        │exceed)│        │       │      ││
│  │     │            │        │       │        │       │[Edit]││
│  ├─────┼────────────┼────────┼───────┼────────┼───────┼──────┤│
│  │ ☐  │Tran Thi B  │ 168.0h │ 8.5h  │ 15.0h  │  0h   │ ✅  ││
│  │     │陳氏B       │        │       │        │       │      ││
│  │     │EMP-002     │        │       │        │       │[Edit]││
│  ├─────┼────────────┼────────┼───────┼────────┼───────┼──────┤│
│  │ ☐  │Chen Ming   │ 165.0h │ 10.0h │ 18.5h  │  0h   │ ✅  ││
│  │     │陳明       │        │       │        │       │[Edit]││
│  ├─────┼────────────┼────────┼───────┼────────┼───────┼──────┤│
│  │ ☐  │Tran Thi 8  │   ?    │   ?   │   ?    │  ?    │ 🔴  ││
│  │     │NOT FOUND   │        │       │        │       │      ││
│  │     │OCR: 88%    │        │       │        │       │[Fix] ││
│  ├─────┼────────────┼────────┼───────┼────────┼───────┼──────┤│
│  │ ☐  │Liu Wei     │ 172.0h │ 15.0h │ 20.0h  │  0h   │ ⚠️  ││
│  │     │劉偉       │        │(45h   │        │       │      ││
│  │     │EMP-004     │        │total) │        │       │[Edit]││
│  └─────┴────────────┴────────┴───────┴────────┴───────┴──────┘│
│                                                                  │
│  ... (20 more employees)                                         │
│                                                                  │
│  ☑️ Select All | ☐ Select Errors | ☐ Select Warnings            │
│                                                                  │
│  [Approve Selected (22)] [Reject All] [Export] [Re-process]    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Edit Modal:**

```
┌─────────────────────────────────────────────────────────────────┐
│  ✏️ EDIT TIMER CARD - Nguyen Van A (November 2025)             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Showing 22 work days (9 weekend/holidays excluded)             │
│                                                                  │
│  ┌────┬────────┬──────────┬──────────┬───────┬────────┬──────┐ │
│  │Date│Clock In│Clock Out │Break(min)│Regular│Overtime│Status│ │
│  ├────┼────────┼──────────┼──────────┼───────┼────────┼──────┤ │
│  │11/1│ 07:00  │ 17:30    │ 45       │ 8.5h  │ 0h     │ ✅  │ │
│  │11/2│ 07:00  │ 19:45    │ 45       │ 8.5h  │ 3.5h   │ ⚠️  │ │
│  │    │        │          │          │       │>3h lim │      │ │
│  │11/3│   -    │    -     │  -       │  -    │  -     │休日 │ │
│  │11/4│ 07:00  │ 17:00    │ 45       │ 8.25h │ 0h     │ ✅  │ │
│  │...│        │          │          │       │        │      │ │
│  └────┴────────┴──────────┴──────────┴───────┴────────┴──────┘ │
│                                                                  │
│  📊 Monthly Totals:                                              │
│  - Regular Hours: 170.5h                                         │
│  - Overtime Hours: 12.0h (1 day exceeds daily limit)           │
│  - Night Hours: 22.0h                                            │
│  - Holiday Hours: 0h                                             │
│  - Total Weighted: 189.25h                                       │
│                                                                  │
│  ⚠️  Validation Warnings:                                        │
│  - 11/2: Overtime 3.5h > 3h daily limit                         │
│                                                                  │
│  📝 Override Reason (if approving with warnings):                │
│  [Textarea]                                                      │
│  例: 緊急納期対応のため残業3.5h承認                             │
│                                                                  │
│  [Save Changes] [Approve Anyway] [Cancel]                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### **PASO 4: Approval**

**Endpoint:** `POST /api/timercards/batch/{batch_id}/approve`

**Proceso:**
```python
def approve_timer_card_batch(batch_id, selected_employee_ids, current_user):
    """
    Aprueba timer cards seleccionados.
    """
    # 1. Validar permisos
    if current_user.role not in [UserRole.ADMIN, UserRole.KEIRI, UserRole.TORISHIMARIYAKU]:
        raise HTTPException(403, "No autorizado")

    # 2. Obtener batch
    batch = get_timer_card_batch(batch_id)

    # 3. Filtrar solo selected
    records_to_approve = [
        r for r in batch.records
        if r.employee_id in selected_employee_ids
    ]

    # 4. Guardar en processed_timer_cards
    for record in records_to_approve:
        ProcessedTimerCard.create(
            employee_id=record.employee_id,
            hakenmoto_id=record.hakenmoto_id,
            factory_id=record.factory_id,
            year=batch.year,
            month=batch.month,
            work_date=record.work_date,
            clock_in=record.clock_in,
            clock_out=record.clock_out,
            break_minutes=record.break_minutes,
            regular_hours=record.regular_hours,
            overtime_hours=record.overtime_hours,
            night_hours=record.night_hours,
            holiday_hours=record.holiday_hours,
            total_weighted_hours=record.total_weighted_hours,
            shift_type=record.shift_type,
            status="approved",
            approved_by=current_user.id,
            approved_at=NOW(),
            ocr_confidence=record.ocr_confidence,
            validation_errors=record.validation_errors,
            validation_warnings=record.validation_warnings
        )

    # 5. Marcar batch como procesado
    batch.status = "approved"
    batch.approved_count = len(records_to_approve)

    return {
        'success': True,
        'approved_count': len(records_to_approve),
        'employees': selected_employee_ids
    }
```

### Tabla processed_timer_cards

```sql
CREATE TABLE processed_timer_cards (
  id SERIAL PRIMARY KEY,

  -- Referencias
  employee_id INT REFERENCES employees(id) ON DELETE CASCADE,
  hakenmoto_id INT NOT NULL,
  factory_id VARCHAR(200) NOT NULL,

  -- Periodo
  year INT NOT NULL,
  month INT NOT NULL,
  work_date DATE NOT NULL,

  -- Shift
  shift_type VARCHAR(20), -- 'day', 'night', 'other'

  -- Tiempos raw
  clock_in TIME NOT NULL,
  clock_out TIME NOT NULL,
  break_minutes INT DEFAULT 0,

  -- Horas calculadas (con factory rules)
  regular_hours NUMERIC(5,2) DEFAULT 0,
  overtime_hours NUMERIC(5,2) DEFAULT 0,
  night_hours NUMERIC(5,2) DEFAULT 0,
  holiday_hours NUMERIC(5,2) DEFAULT 0,

  -- Total weighted (para payroll)
  total_weighted_hours NUMERIC(6,2) DEFAULT 0,
  -- Calculation: regular × 1.0 + overtime × 1.25 + night × 0.25 adicional + holiday × 1.35

  -- Status workflow
  status VARCHAR(20) DEFAULT 'pending',
  -- 'pending' → 'reviewed' → 'approved' → 'paid'

  -- OCR metadata
  ocr_confidence NUMERIC(5,2), -- 0-100
  ocr_corrections TEXT, -- JSON de correcciones manuales

  -- Validaciones
  validation_errors TEXT[], -- Array de errores
  validation_warnings TEXT[], -- Array de warnings

  -- Aprobación
  reviewed_by INT REFERENCES users(id),
  reviewed_at TIMESTAMP,
  approved_by INT REFERENCES users(id),
  approved_at TIMESTAMP,

  -- Notas
  notes TEXT,
  override_reason TEXT, -- Si aprobó con warnings

  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  -- Constraints
  UNIQUE(hakenmoto_id, work_date),
  CHECK(status IN ('pending', 'reviewed', 'approved', 'paid')),
  CHECK(month >= 1 AND month <= 12)
);

-- Índices
CREATE INDEX idx_processed_tc_employee ON processed_timer_cards(employee_id);
CREATE INDEX idx_processed_tc_factory ON processed_timer_cards(factory_id);
CREATE INDEX idx_processed_tc_period ON processed_timer_cards(year, month);
CREATE INDEX idx_processed_tc_status ON processed_timer_cards(status);
CREATE INDEX idx_processed_tc_date ON processed_timer_cards(work_date);
```

### Integración con Payroll

```python
# backend/app/services/payroll_service.py

def create_salary_calculation_from_timer_cards(employee_id, year, month):
    """
    Crea SalaryCalculation desde processed_timer_cards aprobados.
    """
    # 1. Obtener timer cards aprobados del mes
    timer_cards = ProcessedTimerCard.query.filter(
        ProcessedTimerCard.employee_id == employee_id,
        ProcessedTimerCard.year == year,
        ProcessedTimerCard.month == month,
        ProcessedTimerCard.status == 'approved'
    ).all()

    if not timer_cards:
        raise ValueError("No approved timer cards found")

    # 2. Obtener employee
    employee = Employee.query.get(employee_id)

    # 3. Sumar totales
    total_regular = sum(tc.regular_hours for tc in timer_cards)
    total_overtime = sum(tc.overtime_hours for tc in timer_cards)
    total_night = sum(tc.night_hours for tc in timer_cards)
    total_holiday = sum(tc.holiday_hours for tc in timer_cards)

    # 4. Calcular pagos
    base_salary = total_regular * employee.jikyu
    overtime_pay = total_overtime * employee.jikyu * 1.25
    night_pay = total_night * employee.jikyu * 0.25  # Adicional 25%
    holiday_pay = total_holiday * employee.jikyu * 1.35

    gross_salary = base_salary + overtime_pay + night_pay + holiday_pay

    # 5. Obtener deducciones (apartment, etc.)
    apartment_deduction = 0
    if employee.apartment_id:
        rent_deduction = RentDeduction.query.filter(
            RentDeduction.employee_id == employee_id,
            RentDeduction.year == year,
            RentDeduction.month == month,
            RentDeduction.status.in_(['pending', 'processed'])
        ).first()
        if rent_deduction:
            apartment_deduction = rent_deduction.total_deduction

    # 6. Calcular neto
    net_salary = gross_salary - apartment_deduction

    # 7. Crear SalaryCalculation
    salary_calc = SalaryCalculation.create(
        employee_id=employee_id,
        year=year,
        month=month,
        total_regular_hours=total_regular,
        total_overtime_hours=total_overtime,
        total_night_hours=total_night,
        total_holiday_hours=total_holiday,
        base_salary=int(base_salary),
        overtime_pay=int(overtime_pay),
        night_pay=int(night_pay),
        holiday_pay=int(holiday_pay),
        gross_salary=int(gross_salary),
        apartment_deduction=int(apartment_deduction),
        net_salary=int(net_salary),
        is_paid=False
    )

    # 8. Actualizar timer cards status
    for tc in timer_cards:
        tc.status = 'paid'

    return salary_calc
```

**Ejemplo Cálculo:**

```
Employee: Nguyen Van A
Month: November 2025
Jikyu: ¥1,650/h

Timer Cards (approved):
- Regular: 170.5h
- Overtime: 12.0h
- Night: 22.0h
- Holiday: 0h

Cálculo:
- Base: 170.5h × ¥1,650 = ¥281,325
- Overtime: 12.0h × ¥1,650 × 1.25 = ¥24,750
- Night (adicional): 22.0h × ¥1,650 × 0.25 = ¥9,075
- Holiday: 0h × ¥1,650 × 1.35 = ¥0

Gross Salary: ¥315,150

Deducciones:
- Apartment: ¥50,000

Net Salary: ¥265,150
```

---

## 💰 PRIORIDAD 4: PAYROLL (Futuro)

### Estado Actual

**Tablas Existentes:**
- `salary_calculations` ✅
- `processed_timer_cards` ✅
- `rent_deductions` ✅

**APIs Existentes:**
- Cálculo básico de salario ✅
- Integración con timer cards ✅
- Deducciones de apartment ✅

**Pendiente:**
- UI completa de payroll
- Reportes PDF de recibo de pago
- Integración bancaria para pagos
- Historial de pagos
- Dashboards de análisis

**Nota:** Esta prioridad se implementará DESPUÉS de que Prioridades 1-3 estén 100% funcionales.

---

## 📱 FRONTEND - PÁGINAS PRINCIPALES

### Por Prioridad

#### PRIORIDAD 1: Core HR (14 páginas)

```
/dashboard
  /candidates
    /                      # Lista de candidates
    /new                   # Crear candidate (formulario履歴書)
    /{id}                  # Ver detalle + evaluación (👍/👎)
    /{id}/edit             # Editar candidate

  /requests
    /                      # Lista de todas las requests
    /{id}                  # Ver detalle de request
    /{id}/employee-data    # Llenar入社連絡票
    /{id}/approve          # Aprobar NYUUSHA

  /employees
    /                      # Lista de employees
    /new                   # Crear employee (legacy, no usar)
    /{id}                  # Ver detalle employee
    /{id}/edit             # Editar employee

  /factories
    /                      # Tree view de companies/plants/lines
    /companies/new         # Crear company
    /plants/new            # Crear plant
    /lines/new             # Crear line
```

#### PRIORIDAD 2: Operaciones (19 páginas)

```
/dashboard
  /apartments
    /                      # Card view con status
    /new                   # Crear apartment
    /{id}                  # Detalle apartment
    /{id}/capacity         # Capacity tracker
    /{id}/history          # Historial completo
    /assignments           # Lista de assignments
    /recommend/{emp_id}    # Recomendaciones inteligentes

  /yukyu
    /                      # Dashboard yukyu
    /balances              # Balances por employee
    /requests              # Lista de requests
    /requests/new          # Crear request
    /requests/{id}         # Detalle request
    /requests/{id}/approve # Aprobar/rechazar
```

#### PRIORIDAD 3: Asistencia (7 páginas)

```
/dashboard
  /timercards
    /                      # Lista de timer cards
    /upload                # Upload PDF
    /review/{batch_id}     # Review OCR results
    /processed             # Processed timer cards
    /{id}                  # Detalle timer card
    /employee/{emp_id}     # Timer cards de employee
```

#### PRIORIDAD 4: Finanzas (10 páginas)

```
/dashboard
  /payroll
    /                      # Dashboard payroll
    /calculate             # Calcular salarios
    /month/{year}/{month}  # Salarios del mes
    /{id}                  # Detalle salary calculation
    /reports               # Reportes
    /export                # Export a Excel
```

#### Admin/Config (14 páginas)

```
/dashboard
  /users                   # Gestión de usuarios
  /settings                # Configuración sistema
  /audit-logs              # Logs de auditoría
  /reports                 # Reportes generales
  /dashboard               # Dashboard principal
```

**Total:** ~64 páginas implementadas

---

## 🚀 IMPLEMENTACIÓN - ROADMAP

### Fase 1: Quick Wins (Semana 1-2) ⚡ CRÍTICO

**Objetivo:** Solucionar 70% de problemas críticos actuales

**Tareas:**
1. ✅ Agregar transaction wrappers en payroll (2 días)
2. ✅ Crear índices de base de datos (1 día)
3. ✅ Frontend retry logic (axios-retry) (2 horas)
4. ✅ Offline detection banner (2 horas)
5. ✅ Row-level locking en apartment assignments (3 días)

**Entregables:**
- Sistema estable para pruebas
- Reducción 70% de race conditions
- Better UX en red lenta

---

### Fase 2: Factories Normalizadas (Semana 3-4) 🏭

**Objetivo:** DB normalizada para factories con UI jerárquica

**Tareas:**
1. Crear migration para companies/plants/lines (2 días)
2. Script de importación desde JSON (1 día)
3. Backend APIs (GET, POST, PUT, DELETE) (2 días)
4. UI tree view en /dashboard/factories (3 días)
5. Cascading dropdowns en入社連絡票 (2 días)
6. Testing completo (2 días)

**Entregables:**
- 14 companies, 24 plants, 150+ lines en DB
- UI tree view funcional
- Cascading dropdowns con auto-fill de hourly_rate

---

### Fase 3: 入社連絡票 Mejorado (Semana 5-6) 📋

**Objetivo:** Formulario completo con todas las secciones

**Tareas:**
1. Backend: actualizar employee_data schema (1 día)
2. UI: formulario completo 7 secciones (4 días)
3. Integración con apartment recommendations (2 días)
4. Validaciones frontend/backend (2 días)
5. Testing workflow completo (1 día)

**Entregables:**
- Formulario入社連絡票 100% completo
- Recomendaciones inteligentes de apartments
- Workflow Candidate → Employee funcional

---

### Fase 4: Apartments Inteligente (Semana 7-9) 🏠

**Objetivo:** Sistema completo con auto-asignación y features inteligentes

**Tareas:**
1. Backend: recommendation service con scoring (3 días)
2. UI: card view mejorado (2 días)
3. UI: capacity tracker (2 días)
4. UI: dashboard con métricas (2 días)
5. UI: historial timeline (1 día)
6. Features inteligentes:
   - Transfer suggestions (2 días)
   - Contract alerts (1 día)
   - Auto rent deductions (2 días)
7. Testing (2 días)

**Entregables:**
- Sistema de scoring funcional
- Dashboard completo
- 4 features inteligentes activas
- Cron jobs configurados

---

### Fase 5: Timer Cards OCR (Semana 10-12) 📄

**Objetivo:** OCR completo con factory rules

**Tareas:**
1. Backend: OCR service (5 días)
   - PDF parsing (Camelot)
   - Fuzzy matching de employees
   - Factory rules application
   - Validaciones
2. Backend: tabla processed_timer_cards (1 día)
3. UI: upload page (2 días)
4. UI: review grid editable (4 días)
5. UI: edit modal (2 días)
6. Integración con payroll (2 días)
7. Testing con PDFs reales (2 días)

**Entregables:**
- OCR funcional con 95%+ accuracy
- Review UI completo
- Integración con payroll
- Reducción 87% en tiempo de procesamiento

---

### Fase 6: Testing & QA (Semana 13-14) 🧪

**Objetivo:** Sistema 100% estable y probado

**Tareas:**
1. Unit tests (backend) (3 días)
2. Integration tests (3 días)
3. E2E tests (Playwright) (3 días)
4. Load testing (1 día)
5. Bug fixes (3 días)

**Entregables:**
- Coverage > 80%
- Zero critical bugs
- Performance validated

---

### Fase 7: Deployment (Semana 15-16) 🚀

**Objetivo:** Deploy a producción

**Tareas:**
1. Setup production environment (2 días)
2. Migration scripts (1 día)
3. Data import/backup (2 días)
4. Monitoring setup (Grafana dashboards) (2 días)
5. Documentation final (2 días)
6. Training sessions (3 días)

**Entregables:**
- Sistema en producción
- Backups automáticos
- Monitoring activo
- Team trained

---

## 📊 MÉTRICAS DE ÉXITO

### KPIs del Sistema

| Métrica | Actual | Meta (3 meses) | Meta (6 meses) |
|---------|--------|----------------|----------------|
| **Disponibilidad** |
| Uptime | 95% | 99% | 99.9% |
| Avg Response Time | 800ms | 200ms | 100ms |
| Failed Requests | 5% | 1% | 0.1% |
| **Operaciones** |
| Candidate → Employee | 5 días | 1 día | 4 horas |
| Timer Card Processing | 8 horas | 1 hora | 15 min |
| OCR Accuracy | 70% | 95% | 99% |
| **Performance** |
| DB Query Time | 500ms | 50ms | 10ms |
| Frontend Cache Hit | 10% | 70% | 90% |
| OCR Throughput | 8/min | 50/min | 200/min |
| **Business** |
| Active Employees | 150 | 300 | 500 |
| Apartments Managed | 45 | 70 | 100 |
| Factories Integrated | 14 | 25 | 40 |

---

## 🔒 SEGURIDAD Y COMPLIANCE

### Datos Sensibles

**Protegidos:**
- Passwords (bcrypt hash)
- JWT tokens (HTTP-only cookies)
- Bank accounts (encrypted)
- Photos (compressed, access-controlled)

**Audit Trail:**
- Todos los cambios en `audit_log`
- Admin actions en `admin_audit_logs`
- Login attempts tracked

### GDPR/Privacy

- Employee consent para data processing
- Right to be forgotten (soft delete)
- Data export en Excel/PDF
- Access logs

---

## 📚 DOCUMENTOS DE REFERENCIA

### Análisis Completo

1. **`docs/architecture/COMPLETE_ARCHITECTURE_ANALYSIS.md`**
   - Análisis completo del sistema actual
   - Endpoints documentados con líneas de código
   - 1,854 líneas de análisis detallado

2. **`docs/architecture/TIMER_CARDS_OCR_COMPLETE_DESIGN.md`**
   - Diseño completo del sistema OCR
   - Algoritmos de procesamiento
   - Ejemplos con números reales

3. **`docs/architecture/FACTORY_SYSTEM_DESIGN.md`**
   - Sistema jerárquico de factories
   - Cascading dropdowns
   - Factory rules para timer cards

4. **`docs/architecture/FRONTEND_BACKEND_DEPENDENCY_ANALYSIS.md`**
   - Análisis de fragilidad del frontend
   - Quick wins implementables

5. **`docs/architecture/EXECUTIVE_AUDIT_REPORT.md`**
   - Auditoría ejecutiva completa
   - ROI y análisis financiero
   - Plan de migración a microservicios

---

## ✅ CONCLUSIÓN

Este es el **plan completo y definitivo** para el desarrollo de UNS-ClaudeJP 5.4.1 basado en las prioridades del usuario:

1. ✅ **Candidate → 入社連絡票 → Employee** (PRIORIDAD 1)
2. ✅ **Factories bien definidas** (Company → Plants → Lines)
3. ✅ **Apartments inteligentes** (PRIORIDAD 2)
4. ✅ **Yukyu** (ya implementado)
5. ✅ **Timer Cards OCR** (PRIORIDAD 3)
6. ✅ **Payroll** (PRIORIDAD 4 - futuro)

**Implementación:** 16 semanas (4 meses)
**Inversión estimada:** ¥10M
**ROI:** 3 meses
**Beneficios:** Sistema enterprise-grade, escalable, con 99.9% uptime

---

**Preparado por:** Claude Code
**Fecha:** 2025-11-13
**Versión:** 1.0 FINAL
