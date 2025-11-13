# ANÁLISIS EXHAUSTIVO DE LA BASE DE DATOS PostgreSQL
# UNS-ClaudeJP v5.4.1

**Fecha:** 2025-11-13  
**BD:** uns_claudejp (PostgreSQL 15.14)  
**Dueño:** uns_admin

## RESUMEN

36 tablas, 1,136 registros con datos, 51 relaciones foráneas

### Datos Poblados
- audit_log: 1,070 registros
- employees: 37 registros
- staff: 16 registros
- factories: 11 registros
- users: 2 registros
- Resto: 0 registros

---

## TABLAS PRINCIPALES (Descripción Ejecutiva)

### 1. USERS (2 registros) - Autenticación
ID, username (UNIQUE), email (UNIQUE), password_hash, role (8 tipos), full_name, is_active

Roles: SUPER_ADMIN > ADMIN > KEITOSAN > TANTOSHA > COORDINATOR > KANRININSHA > EMPLOYEE > CONTRACT_WORKER

### 2. CANDIDATES (0) - 履歴書 Formulario Candidatura
100+ campos: nombres, fecha nacimiento, nacionalidad, dirección, teléfono, email, pasaporte, tarjeta residencia, licencia, foto (base64), familia (5), experiencia laboral (14), idiomas, cualificaciones, salud, etc.

Índices especiales: TRIGRAM (búsqueda difusa) en nombres

### 3. EMPLOYEES (37) - 派遣社員 Empleados Activos
Derivados de candidates. ID/hakenmoto_id, factory, apartment, workplace, department, region, salary (jikyu), vacaciones (yukyu), seguros, visa, estado contractual

### 4-7. OPERACIONES: timer_cards, salary_calculations, employee_payroll, payroll_runs

### 8-12. ALOJAMIENTO: apartments, apartment_assignments, apartment_factory, rent_deductions, additional_charges

### 13-16. INFRAESTRUCTURA: factories (11), regions, workplaces, documents

### 17-19. PRESTACIONES YUKYU: yukyu_balances, yukyu_requests, yukyu_usage_details

### 20-24. AUDITORÍA: audit_log (1,070), admin_audit_logs, page_visibility, system_settings, role_page_permissions

### 25-26. AUTENTICACIÓN: refresh_tokens, contracts

### 27-36. APOYO: staff (16), departments, residence_types, residence_statuses, candidate_forms, contract_workers, alembic_version

---

## ENUMERACIONES (14 ENUM TYPES)

user_role: SUPER_ADMIN, ADMIN, KEITOSAN, TANTOSHA, COORDINATOR, KANRININSHA, EMPLOYEE, CONTRACT_WORKER

Estados: apartment_status (ACTIVE/INACTIVE/MAINTENANCE/RESERVED), assignment_status (ACTIVE/ENDED/CANCELLED/TRANSFERRED), charge_status, deduction_status, request_status, yukyu_status

Tipos: room_type (ONE_K/ONE_DK/ONE_LDK/TWO_K/TWO_DK/TWO_LDK/THREE_LDK/STUDIO/OTHER), shift_type (ASA/HIRU/YORU/OTHER), document_type, request_type, charge_type

Auditoría: adminactiontype, resourcetype

---

## RELACIONES (51 FOREIGN KEYS)

Candidates ← Users (approved_by)
Employees ← Candidates (rirekisho_id), Factories (factory_id), Apartments (apartment_id), Departments, Regions

Operaciones ← Employees (via hakenmoto_id: timer_cards, requests)
Operaciones ← Employees (via id: assignments, payroll, contracts)

Alojamiento ← Apartments (región), Assignments (employee, apartment)

Nómina ← Payroll_runs

Prestaciones ← Employees (yukyu_balances)

Auditoría ← Users (audit_log, admin_audit_logs)

---

## CARACTERÍSTICAS ESPECIALES

1. **Búsqueda Trigram (pg_trgm)**: Índices GIN en nombres para búsqueda difusa
2. **JSON/JSONB Fields**: photo_data_url (base64), form_data, employee_data (snapshots)
3. **Soft Delete**: deleted_at timestamp para borrado lógico
4. **Dual IDs**: id interno + hakenmoto_id empresarial en employees
5. **Índices de Rango**: por fecha en timer_cards, assignments, payroll

---

## TRIGGERS

Triggers: 0
Funciones personalizadas: 0

La lógica está en FastAPI backend, no en BD.

---

## USUARIOS DE BD

uns_admin (OWNER de todos los objetos)
postgres (SUPERUSER del sistema)

---

## RECOMENDACIONES

1. Índice en audit_log.created_at para limpieza automática
2. Vistas para consultas complejas
3. Particionamiento de audit_log y timer_cards por fechas
4. VACUUM ANALYZE regular
5. Política de retención de auditoría (2 años)
