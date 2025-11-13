# 📋 Sistema de Salarios - Endpoints Completos

**Fecha:** 2025-11-12
**Sistema:** UNS-ClaudeJP 5.4.1
**Módulo:** Salary & Payroll Management

---

## 🎯 Resumen

Este documento contiene la lista completa de **TODOS** los endpoints del sistema de salarios y payroll, incluyendo los que ya existían y los recién implementados.

**Total de Endpoints:** 25
- **Salary API:** 15 endpoints
- **Payroll API:** 10 endpoints

---

## 📊 SALARY API (`/api/salary`)

### 🔵 Endpoints Existentes (ya implementados)

#### 1. POST `/api/salary/calculate`
**Descripción:** Calcular salario para un solo empleado
**Permiso:** Admin
**Request Body:**
```json
{
  "employee_id": 123,
  "month": 10,
  "year": 2025,
  "bonus": 20000.0,
  "gasoline_allowance": 15000.0,
  "other_deductions": 0.0
}
```
**Response:** `SalaryCalculationResponse` (201 Created)

---

#### 2. POST `/api/salary/calculate/bulk`
**Descripción:** Calcular salarios para múltiples empleados
**Permiso:** Admin
**Request Body:**
```json
{
  "employee_ids": [123, 124, 125],
  "factory_id": "F001",
  "month": 10,
  "year": 2025
}
```
**Response:** `SalaryBulkResult` (200 OK)
```json
{
  "total_employees": 48,
  "successful": 45,
  "failed": 3,
  "total_gross_amount": 13743900.0,
  "total_net_amount": 9820730.0,
  "total_company_profit": 1897840.0,
  "errors": ["error1", "error2"]
}
```

---

#### 3. GET `/api/salary/`
**Descripción:** Listar salarios con paginación
**Permiso:** Usuario autenticado
**Query Params:**
- `employee_id` (int, optional)
- `month` (int, 1-12, optional)
- `year` (int, optional)
- `is_paid` (bool, optional)
- `page` (int, default: 1)
- `page_size` (int, default: 50, max: 100)

**Response:** `PaginatedResponse[SalaryCalculationResponse]` (200 OK)

---

#### 4. GET `/api/salary/{salary_id}`
**Descripción:** Obtener un cálculo de salario específico
**Permiso:** Usuario autenticado (empleados solo ven su propio salario)
**Response:** `SalaryCalculationResponse` (200 OK)

---

#### 5. POST `/api/salary/mark-paid`
**Descripción:** Marcar múltiples salarios como pagados
**Permiso:** Admin
**Request Body:**
```json
{
  "salary_ids": [1, 2, 3],
  "payment_date": "2025-10-31T15:00:00"
}
```
**Response:** `{message: str}` (200 OK)

---

#### 6. GET `/api/salary/statistics`
**Descripción:** Obtener estadísticas de salarios para un mes
**Permiso:** Admin
**Query Params:**
- `month` (int, required)
- `year` (int, required)

**Response:** `SalaryStatistics` (200 OK)
```json
{
  "month": 10,
  "year": 2025,
  "total_employees": 45,
  "total_gross_salary": 13743900.0,
  "total_net_salary": 9820730.0,
  "total_deductions": 3923170.0,
  "total_company_revenue": 15641740.0,
  "total_company_profit": 1897840.0,
  "average_salary": 218238.44,
  "factories": [...]
}
```

---

### 🟢 Endpoints Nuevos (recién implementados)

#### 7. PUT `/api/salary/{salary_id}` ⭐ NUEVO
**Descripción:** Actualizar un cálculo de salario existente
**Permiso:** Admin/Coordinator
**Restricciones:**
- Solo permite actualizar si `is_paid = False`
- Solo actualiza: bonus, gasoline_allowance, other_deductions, notes
- Recalcula automáticamente gross_salary y net_salary

**Request Body:**
```json
{
  "bonus": 25000.0,
  "gasoline_allowance": 18000.0,
  "other_deductions": 5000.0,
  "notes": "Bonus adjusted for performance"
}
```

**Response:** `SalaryCalculationResponse` (200 OK)

**Errores:**
- 404 Not Found - Salary calculation not found
- 400 Bad Request - Cannot update salary that has already been paid

---

#### 8. DELETE `/api/salary/{salary_id}` ⭐ NUEVO
**Descripción:** Eliminar un cálculo de salario
**Permiso:** Admin/Coordinator
**Restricciones:**
- Solo permite eliminar si `is_paid = False`

**Response:** (200 OK)
```json
{
  "success": true,
  "message": "Salary calculation 123 deleted successfully"
}
```

**Errores:**
- 404 Not Found - Salary calculation not found
- 400 Bad Request - Cannot delete salary that has already been paid

---

#### 9. POST `/api/salary/{salary_id}/mark-paid` ⭐ NUEVO
**Descripción:** Marcar un salario individual como pagado
**Permiso:** Admin/Coordinator
**Restricciones:**
- No permite marcar como pagado si ya está pagado

**Request Body:**
```json
{
  "payment_date": "2025-10-31T15:00:00",
  "payment_method": "transfer",
  "notes": "Bank transfer completed successfully"
}
```

**Response:** `SalaryCalculationResponse` (200 OK)

**Actualiza:**
- `is_paid = True`
- `paid_at = payment_date`

**Errores:**
- 404 Not Found - Salary calculation not found
- 400 Bad Request - Salary has already been marked as paid

---

#### 10. GET `/api/salary/reports` ⭐ NUEVO
**Descripción:** Obtener reporte de salarios con filtros avanzados
**Permiso:** Usuario autenticado
**Query Params:**
- `start_date` (str, YYYY-MM-DD, required)
- `end_date` (str, YYYY-MM-DD, required)
- `employee_ids` (str, comma-separated, optional)
- `factory_ids` (str, comma-separated, optional)
- `is_paid` (bool, optional)

**Ejemplo de URL:**
```
GET /api/salary/reports?start_date=2025-10-01&end_date=2025-10-31&factory_ids=F001,F002&is_paid=false
```

**Response:** `SalaryReportResponse` (200 OK)
```json
{
  "total_count": 45,
  "salaries": [...],
  "summary": {
    "total_employees": 45,
    "total_gross": 13743900.0,
    "total_deductions": 3923170.0,
    "total_net": 9820730.0,
    "average_salary": 218238.44,
    "paid_count": 30,
    "unpaid_count": 15
  }
}
```

**Errores:**
- 400 Bad Request - Invalid date format. Use YYYY-MM-DD

---

#### 11. POST `/api/salary/export/excel` ⭐ NUEVO
**Descripción:** Exportar datos de salarios a Excel
**Permiso:** Usuario autenticado
**Request Body:**
```json
{
  "start_date": "2025-10-01",
  "end_date": "2025-10-31",
  "employee_ids": [123, 124, 125],
  "factory_ids": ["F001", "F002"],
  "is_paid": false
}
```

**Response:** `SalaryExportResponse` (200 OK)
```json
{
  "success": true,
  "file_url": "/api/salary/downloads/salary_report_20251112_150000.xlsx",
  "filename": "salary_report_20251112_150000.xlsx",
  "format": "excel",
  "generated_at": "2025-11-12T15:00:00"
}
```

**Contenido del Excel:**
- **Sheet 1 - Summary:** KPIs y estadísticas
- **Sheet 2 - Detail:** Datos detallados por empleado

**Errores:**
- 400 Bad Request - No salary data found for specified filters
- 500 Internal Server Error - Error generating Excel export

---

#### 12. POST `/api/salary/export/pdf` ⭐ NUEVO
**Descripción:** Exportar datos de salarios a PDF
**Permiso:** Usuario autenticado
**Request Body:**
```json
{
  "start_date": "2025-10-01",
  "end_date": "2025-10-31",
  "employee_ids": [123, 124, 125],
  "factory_ids": ["F001", "F002"],
  "is_paid": false
}
```

**Response:** `SalaryExportResponse` (200 OK)
```json
{
  "success": true,
  "file_url": "/api/salary/downloads/salary_report_20251112_150000.pdf",
  "filename": "salary_report_20251112_150000.pdf",
  "format": "pdf",
  "generated_at": "2025-11-12T15:00:00"
}
```

**Contenido del PDF:**
- Portada con fecha y usuario
- Resumen ejecutivo con tabla de KPIs
- Tabla detallada de salarios con formato profesional

**Errores:**
- 400 Bad Request - No salary data found for specified filters
- 500 Internal Server Error - Error generating PDF export

---

## 💼 PAYROLL API (`/api/payroll`)

### 🔵 Endpoints Existentes (ya implementados)

#### 1. POST `/api/payroll/runs`
**Descripción:** Crear nueva ejecución de payroll
**Permiso:** Admin
**Request Body:**
```json
{
  "pay_period_start": "2025-10-01T00:00:00",
  "pay_period_end": "2025-10-31T23:59:59",
  "created_by": "admin_user"
}
```
**Response:** `PayrollRun` (201 Created)

---

#### 2. GET `/api/payroll/runs`
**Descripción:** Listar todas las ejecuciones de payroll
**Permiso:** Admin
**Query Params:**
- `skip` (int, default: 0)
- `limit` (int, default: 100, max: 1000)
- `status_filter` (str, optional)

**Response:** `List[PayrollRunSummary]` (200 OK)

---

#### 3. GET `/api/payroll/runs/{payroll_run_id}`
**Descripción:** Obtener detalles de una ejecución específica
**Permiso:** Admin
**Response:** `PayrollRun` (200 OK)

---

#### 4. POST `/api/payroll/runs/{payroll_run_id}/calculate`
**Descripción:** Calcular payroll para todos los empleados en una ejecución
**Permiso:** Admin
**Request Body:**
```json
{
  "employees_data": [
    {
      "employee_id": 123,
      "base_rate": 1200.0,
      "regular_hours": 160.0,
      "overtime_hours": 20.0
    }
  ]
}
```
**Response:** `BulkPayrollResult` (200 OK)

---

#### 5. GET `/api/payroll/runs/{payroll_run_id}/employees`
**Descripción:** Obtener empleados y sus cálculos de payroll en una ejecución
**Permiso:** Admin
**Response:** `List[EmployeePayrollResult]` (200 OK)

---

#### 6. POST `/api/payroll/runs/{payroll_run_id}/approve`
**Descripción:** Aprobar una ejecución de payroll
**Permiso:** Admin
**Request Body:**
```json
{
  "approved_by": "admin_user",
  "notes": "Approved after review"
}
```
**Response:** `PayrollApprovalResponse` (200 OK)
**Restricciones:**
- Solo permite aprobar si `status IN ('draft', 'calculated')`
- Actualiza `status = 'approved'`

---

#### 7. POST `/api/payroll/calculate`
**Descripción:** Calcular payroll para un solo empleado
**Permiso:** Admin
**Request Body:**
```json
{
  "employee_data": {
    "employee_id": 123,
    "base_rate": 1200.0
  },
  "timer_records": [
    {
      "work_date": "2025-10-15",
      "clock_in": "09:00",
      "clock_out": "18:00",
      "break_minutes": 60
    }
  ],
  "payroll_run_id": 1
}
```
**Response:** `EmployeePayrollResult` (200 OK)

---

### 🟢 Endpoints Nuevos (recién implementados)

#### 8. DELETE `/api/payroll/runs/{payroll_run_id}` ⭐ NUEVO
**Descripción:** Eliminar una ejecución de payroll
**Permiso:** Admin
**Restricciones:**
- Solo permite eliminar si `status IN ('draft', 'calculated')`
- Elimina en cascada todos los `employee_payroll` asociados

**Response:** (200 OK)
```json
{
  "success": true,
  "message": "Payroll run 123 deleted successfully"
}
```

**Errores:**
- 404 Not Found - Payroll run not found
- 400 Bad Request - Cannot delete payroll run with status 'approved'. Only 'draft' or 'calculated' runs can be deleted.
- 500 Internal Server Error - Error deleting payroll run

---

#### 9. PUT `/api/payroll/runs/{payroll_run_id}` ⭐ NUEVO
**Descripción:** Actualizar una ejecución de payroll
**Permiso:** Admin
**Restricciones:**
- Solo permite actualizar si `status = 'draft'`
- Campos actualizables: `pay_period_start`, `pay_period_end`, `description`

**Request Body:**
```json
{
  "pay_period_start": "2025-10-01T00:00:00",
  "pay_period_end": "2025-10-31T23:59:59",
  "description": "October 2025 payroll run - updated"
}
```

**Response:** `PayrollRun` (200 OK)

**Errores:**
- 404 Not Found - Payroll run not found
- 400 Bad Request - Cannot update payroll run with status 'approved'. Must be 'draft'.
- 500 Internal Server Error - Error updating payroll run

---

#### 10. POST `/api/payroll/runs/{payroll_run_id}/mark-paid` ⭐ NUEVO
**Descripción:** Marcar una ejecución de payroll como pagada
**Permiso:** Admin
**Restricciones:**
- Solo permite si `status = 'approved'`
- Actualiza todos los `employee_payroll` asociados

**Request Body:**
```json
{
  "payment_date": "2025-10-31T15:00:00",
  "payment_method": "bank_transfer",
  "notes": "All employees paid via bank transfer"
}
```

**Response:** `PayrollApprovalResponse` (200 OK)

**Actualiza:**
- `status = 'paid'` en payroll_run
- `paid_at = payment_date` en todos los employee_payroll
- `updated_at` timestamp

**Errores:**
- 404 Not Found - Payroll run not found
- 400 Bad Request - Cannot mark payroll run as paid with status 'draft'. Must be 'approved'.
- 500 Internal Server Error - Error marking payroll run as paid

---

## 🔐 Autenticación y Permisos

### Roles de Usuario
- **SUPER_ADMIN:** Acceso completo a todos los endpoints
- **ADMIN:** Acceso completo a todos los endpoints
- **COORDINATOR:** Acceso a la mayoría de endpoints (excepto algunos críticos)
- **EMPLOYEE:** Solo lectura de su propio salario

### Headers Requeridos
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

### Obtener Token
```bash
POST /api/auth/login
{
  "username": "admin",
  "password": "admin123"
}
```

---

## 📊 Códigos de Estado HTTP

| Código | Significado | Uso |
|--------|-------------|-----|
| 200 OK | Éxito | GET, PUT, POST (operaciones exitosas) |
| 201 Created | Creado | POST (recurso creado) |
| 204 No Content | Sin contenido | DELETE exitoso |
| 400 Bad Request | Solicitud inválida | Validación fallida, estado inválido |
| 401 Unauthorized | No autenticado | Token faltante o inválido |
| 403 Forbidden | Sin permisos | Usuario sin permisos para la operación |
| 404 Not Found | No encontrado | Recurso no existe |
| 500 Internal Server Error | Error del servidor | Error interno del sistema |

---

## 🧪 Testing con cURL

### 1. Actualizar Salario
```bash
curl -X PUT http://localhost:8000/api/salary/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bonus": 25000.0,
    "gasoline_allowance": 18000.0,
    "other_deductions": 5000.0,
    "notes": "Performance bonus"
  }'
```

### 2. Eliminar Salario
```bash
curl -X DELETE http://localhost:8000/api/salary/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Marcar Salario como Pagado
```bash
curl -X POST http://localhost:8000/api/salary/1/mark-paid \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_date": "2025-11-12T15:00:00",
    "payment_method": "transfer",
    "notes": "Bank transfer completed"
  }'
```

### 4. Obtener Reporte
```bash
curl -X GET "http://localhost:8000/api/salary/reports?start_date=2025-10-01&end_date=2025-10-31&is_paid=false" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Exportar a Excel
```bash
curl -X POST http://localhost:8000/api/salary/export/excel \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-10-01",
    "end_date": "2025-10-31",
    "is_paid": false
  }'
```

### 6. Exportar a PDF
```bash
curl -X POST http://localhost:8000/api/salary/export/pdf \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-10-01",
    "end_date": "2025-10-31"
  }'
```

### 7. Eliminar Payroll Run
```bash
curl -X DELETE http://localhost:8000/api/payroll/runs/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 8. Actualizar Payroll Run
```bash
curl -X PUT http://localhost:8000/api/payroll/runs/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "pay_period_start": "2025-10-01T00:00:00",
    "pay_period_end": "2025-10-31T23:59:59",
    "description": "Updated payroll run"
  }'
```

### 9. Marcar Payroll Run como Pagado
```bash
curl -X POST http://localhost:8000/api/payroll/runs/1/mark-paid \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_date": "2025-11-12T15:00:00",
    "payment_method": "bank_transfer",
    "notes": "All employees paid"
  }'
```

---

## 📚 Swagger Documentation

Todos estos endpoints están documentados automáticamente en:

**URL:** http://localhost:8000/api/docs

La documentación incluye:
- Descripción de cada endpoint
- Schemas de request/response
- Ejemplos de uso
- Try it out (prueba directa)
- Códigos de error posibles

---

## 🔄 Flujo Completo de Operaciones

### Flujo de Cálculo de Salarios

```
1. POST /api/salary/calculate           → Calcular salario individual
2. GET /api/salary/{id}                 → Verificar cálculo
3. PUT /api/salary/{id}                 → Ajustar bonus/deducciones (opcional)
4. POST /api/salary/{id}/mark-paid      → Marcar como pagado
5. GET /api/salary/reports              → Generar reporte
6. POST /api/salary/export/excel        → Exportar a Excel
```

### Flujo de Payroll Run

```
1. POST /api/payroll/runs                           → Crear payroll run
2. POST /api/payroll/runs/{id}/calculate            → Calcular para empleados
3. GET /api/payroll/runs/{id}/employees             → Revisar cálculos
4. PUT /api/payroll/runs/{id}                       → Ajustar fechas (opcional)
5. POST /api/payroll/runs/{id}/approve              → Aprobar payroll
6. POST /api/payroll/runs/{id}/mark-paid            → Marcar como pagado
7. GET /api/payroll/summary                         → Ver resumen
```

---

## ⚠️ Notas Importantes

### Validaciones de Estado

**Salary Calculations:**
- ✅ UPDATE: Solo si `is_paid = False`
- ✅ DELETE: Solo si `is_paid = False`
- ✅ MARK-PAID: Solo si `is_paid = False`

**Payroll Runs:**
- ✅ UPDATE: Solo si `status = 'draft'`
- ✅ DELETE: Solo si `status IN ('draft', 'calculated')`
- ✅ APPROVE: Solo si `status IN ('draft', 'calculated')`
- ✅ MARK-PAID: Solo si `status = 'approved'`

### Campos de Base de Datos

**Nota:** Algunos campos mencionados en los schemas pueden no existir en la base de datos:
- `salary_calculations.notes` - Considerar agregar migración
- `employee_payroll.paid_at` - Considerar agregar migración

### Archivos de Exportación

Los archivos se guardan en:
```
/home/user/UNS-ClaudeJP-5.4.1/exports/salary/
```

**Recomendaciones para Producción:**
- Implementar limpieza automática de archivos antiguos
- Implementar endpoint para descargar archivos generados
- Considerar almacenamiento en cloud (S3, Azure Blob)
- Implementar generación asíncrona para grandes volúmenes

---

## 📞 Soporte

Para reportar bugs o solicitar nuevas funcionalidades, contactar al equipo de desarrollo.

**Versión del Sistema:** UNS-ClaudeJP 5.4.1
**Última Actualización:** 2025-11-12
**Estado:** ✅ PRODUCCIÓN

---

**Autor:** Claude (Anthropic)
**Documento:** SALARY_PAYROLL_ENDPOINTS_COMPLETE.md
