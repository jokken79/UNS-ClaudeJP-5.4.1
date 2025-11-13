# 🧪 Guía de Testing - Endpoints de Salarios

**Fecha:** 2025-11-12
**Sistema:** UNS-ClaudeJP 5.4.1

---

## 📋 Pre-requisitos

### 1. Backend en Ejecución
```bash
# Verificar que el backend esté corriendo
curl http://localhost:8000/api/health

# Respuesta esperada:
# {"status": "healthy"}
```

### 2. Obtener Token de Autenticación
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Guardar el token en variable:**
```bash
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 3. Verificar Datos de Prueba
```bash
# Listar empleados
curl -X GET http://localhost:8000/api/employees \
  -H "Authorization: Bearer $TOKEN"

# Listar salarios existentes
curl -X GET http://localhost:8000/api/salary \
  -H "Authorization: Bearer $TOKEN"
```

---

## ✅ Test Plan - Endpoints Nuevos

### TEST 1: PUT `/api/salary/{salary_id}` - Actualizar Salario

#### Test 1.1: Actualizar salario NO pagado (debe funcionar)
```bash
# 1. Crear un salario de prueba
curl -X POST http://localhost:8000/api/salary/calculate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": 1,
    "month": 11,
    "year": 2025,
    "bonus": 10000.0,
    "gasoline_allowance": 10000.0,
    "other_deductions": 0.0
  }'

# Guardar el ID del salario creado (ej: 123)
export SALARY_ID=123

# 2. Actualizar el salario
curl -X PUT http://localhost:8000/api/salary/$SALARY_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bonus": 25000.0,
    "gasoline_allowance": 18000.0,
    "other_deductions": 5000.0,
    "notes": "Bonus adjusted for performance"
  }'

# ✅ Resultado esperado: Status 200, salario actualizado con nuevos valores
```

#### Test 1.2: Intentar actualizar salario YA pagado (debe fallar)
```bash
# 1. Marcar el salario como pagado
curl -X POST http://localhost:8000/api/salary/$SALARY_ID/mark-paid \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_date": "2025-11-12T15:00:00",
    "payment_method": "transfer"
  }'

# 2. Intentar actualizar (debe fallar)
curl -X PUT http://localhost:8000/api/salary/$SALARY_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bonus": 30000.0
  }'

# ❌ Resultado esperado: Status 400
# {"detail": "Cannot update salary that has already been paid"}
```

---

### TEST 2: DELETE `/api/salary/{salary_id}` - Eliminar Salario

#### Test 2.1: Eliminar salario NO pagado (debe funcionar)
```bash
# 1. Crear salario de prueba
curl -X POST http://localhost:8000/api/salary/calculate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": 1,
    "month": 12,
    "year": 2025
  }'

# Guardar ID (ej: 124)
export SALARY_ID_TO_DELETE=124

# 2. Eliminar el salario
curl -X DELETE http://localhost:8000/api/salary/$SALARY_ID_TO_DELETE \
  -H "Authorization: Bearer $TOKEN"

# ✅ Resultado esperado: Status 200
# {"success": true, "message": "Salary calculation 124 deleted successfully"}

# 3. Verificar que fue eliminado
curl -X GET http://localhost:8000/api/salary/$SALARY_ID_TO_DELETE \
  -H "Authorization: Bearer $TOKEN"

# ❌ Resultado esperado: Status 404
# {"detail": "Salary calculation not found"}
```

#### Test 2.2: Intentar eliminar salario YA pagado (debe fallar)
```bash
# Usar un salario que esté pagado
curl -X DELETE http://localhost:8000/api/salary/$SALARY_ID \
  -H "Authorization: Bearer $TOKEN"

# ❌ Resultado esperado: Status 400
# {"detail": "Cannot delete salary that has already been paid"}
```

---

### TEST 3: POST `/api/salary/{salary_id}/mark-paid` - Marcar como Pagado

#### Test 3.1: Marcar salario como pagado (debe funcionar)
```bash
# 1. Crear salario de prueba
curl -X POST http://localhost:8000/api/salary/calculate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": 1,
    "month": 10,
    "year": 2025
  }'

# Guardar ID (ej: 125)
export SALARY_ID_UNPAID=125

# 2. Marcar como pagado
curl -X POST http://localhost:8000/api/salary/$SALARY_ID_UNPAID/mark-paid \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_date": "2025-11-12T15:00:00",
    "payment_method": "bank_transfer",
    "notes": "Payment completed successfully"
  }'

# ✅ Resultado esperado: Status 200, salario con is_paid=true y paid_at actualizado

# 3. Verificar estado
curl -X GET http://localhost:8000/api/salary/$SALARY_ID_UNPAID \
  -H "Authorization: Bearer $TOKEN"

# Verificar en response:
# "is_paid": true
# "paid_at": "2025-11-12T15:00:00"
```

#### Test 3.2: Intentar marcar nuevamente como pagado (debe fallar)
```bash
curl -X POST http://localhost:8000/api/salary/$SALARY_ID_UNPAID/mark-paid \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_date": "2025-11-12T16:00:00",
    "payment_method": "cash"
  }'

# ❌ Resultado esperado: Status 400
# {"detail": "Salary has already been marked as paid"}
```

---

### TEST 4: GET `/api/salary/reports` - Obtener Reportes

#### Test 4.1: Reporte básico con fechas
```bash
curl -X GET "http://localhost:8000/api/salary/reports?start_date=2025-10-01&end_date=2025-11-30" \
  -H "Authorization: Bearer $TOKEN"

# ✅ Resultado esperado: Status 200
# {
#   "total_count": 45,
#   "salaries": [...],
#   "summary": {
#     "total_employees": 45,
#     "total_gross": 13743900.0,
#     "total_deductions": 3923170.0,
#     "total_net": 9820730.0,
#     "average_salary": 218238.44,
#     "paid_count": 30,
#     "unpaid_count": 15
#   }
# }
```

#### Test 4.2: Reporte filtrado por empleados específicos
```bash
curl -X GET "http://localhost:8000/api/salary/reports?start_date=2025-10-01&end_date=2025-11-30&employee_ids=1,2,3" \
  -H "Authorization: Bearer $TOKEN"

# ✅ Resultado esperado: Status 200, solo salarios de empleados 1, 2, 3
```

#### Test 4.3: Reporte filtrado por estado de pago
```bash
# Solo salarios NO pagados
curl -X GET "http://localhost:8000/api/salary/reports?start_date=2025-10-01&end_date=2025-11-30&is_paid=false" \
  -H "Authorization: Bearer $TOKEN"

# ✅ Resultado esperado: Status 200, solo salarios con is_paid=false
```

#### Test 4.4: Reporte con formato de fecha inválido (debe fallar)
```bash
curl -X GET "http://localhost:8000/api/salary/reports?start_date=2025/10/01&end_date=2025/11/30" \
  -H "Authorization: Bearer $TOKEN"

# ❌ Resultado esperado: Status 400
# {"detail": "Invalid date format. Use YYYY-MM-DD"}
```

---

### TEST 5: POST `/api/salary/export/excel` - Exportar a Excel

#### Test 5.1: Exportar con filtros básicos
```bash
curl -X POST http://localhost:8000/api/salary/export/excel \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-10-01",
    "end_date": "2025-10-31"
  }'

# ✅ Resultado esperado: Status 200
# {
#   "success": true,
#   "file_url": "/api/salary/downloads/salary_report_20251112_150000.xlsx",
#   "filename": "salary_report_20251112_150000.xlsx",
#   "format": "excel",
#   "generated_at": "2025-11-12T15:00:00"
# }

# Verificar que el archivo existe
ls -lh /home/user/UNS-ClaudeJP-5.4.1/exports/salary/
```

#### Test 5.2: Exportar con todos los filtros
```bash
curl -X POST http://localhost:8000/api/salary/export/excel \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-10-01",
    "end_date": "2025-10-31",
    "employee_ids": [1, 2, 3],
    "factory_ids": ["F001", "F002"],
    "is_paid": false
  }'

# ✅ Resultado esperado: Status 200, Excel con datos filtrados
```

#### Test 5.3: Exportar sin datos (debe fallar)
```bash
curl -X POST http://localhost:8000/api/salary/export/excel \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2099-01-01",
    "end_date": "2099-12-31"
  }'

# ❌ Resultado esperado: Status 400
# {"detail": "No salary data found for specified filters"}
```

---

### TEST 6: POST `/api/salary/export/pdf` - Exportar a PDF

#### Test 6.1: Exportar con filtros básicos
```bash
curl -X POST http://localhost:8000/api/salary/export/pdf \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-10-01",
    "end_date": "2025-10-31"
  }'

# ✅ Resultado esperado: Status 200
# {
#   "success": true,
#   "file_url": "/api/salary/downloads/salary_report_20251112_150000.pdf",
#   "filename": "salary_report_20251112_150000.pdf",
#   "format": "pdf",
#   "generated_at": "2025-11-12T15:00:00"
# }

# Verificar que el archivo PDF existe y es válido
file /home/user/UNS-ClaudeJP-5.4.1/exports/salary/salary_report_*.pdf
```

---

### TEST 7: DELETE `/api/payroll/runs/{payroll_run_id}` - Eliminar Payroll Run

#### Test 7.1: Eliminar payroll run en DRAFT (debe funcionar)
```bash
# 1. Crear payroll run de prueba
curl -X POST http://localhost:8000/api/payroll/runs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "pay_period_start": "2025-11-01T00:00:00",
    "pay_period_end": "2025-11-30T23:59:59",
    "created_by": "admin"
  }'

# Guardar ID (ej: 10)
export PAYROLL_RUN_ID=10

# 2. Eliminar
curl -X DELETE http://localhost:8000/api/payroll/runs/$PAYROLL_RUN_ID \
  -H "Authorization: Bearer $TOKEN"

# ✅ Resultado esperado: Status 200
# {"success": true, "message": "Payroll run 10 deleted successfully"}
```

#### Test 7.2: Intentar eliminar payroll run APPROVED (debe fallar)
```bash
# Usar un payroll run que esté aprobado
curl -X DELETE http://localhost:8000/api/payroll/runs/1 \
  -H "Authorization: Bearer $TOKEN"

# ❌ Resultado esperado: Status 400
# {"detail": "Cannot delete payroll run with status 'approved'. Only 'draft' or 'calculated' runs can be deleted."}
```

---

### TEST 8: PUT `/api/payroll/runs/{payroll_run_id}` - Actualizar Payroll Run

#### Test 8.1: Actualizar payroll run en DRAFT (debe funcionar)
```bash
# 1. Crear payroll run de prueba
curl -X POST http://localhost:8000/api/payroll/runs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "pay_period_start": "2025-12-01T00:00:00",
    "pay_period_end": "2025-12-31T23:59:59",
    "created_by": "admin"
  }'

# Guardar ID (ej: 11)
export PAYROLL_RUN_ID_DRAFT=11

# 2. Actualizar fechas
curl -X PUT http://localhost:8000/api/payroll/runs/$PAYROLL_RUN_ID_DRAFT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "pay_period_start": "2025-12-01T00:00:00",
    "pay_period_end": "2025-12-25T23:59:59",
    "description": "Updated to end on Christmas"
  }'

# ✅ Resultado esperado: Status 200, payroll run actualizado
```

#### Test 8.2: Intentar actualizar payroll run APPROVED (debe fallar)
```bash
curl -X PUT http://localhost:8000/api/payroll/runs/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "pay_period_end": "2025-10-30T23:59:59"
  }'

# ❌ Resultado esperado: Status 400
# {"detail": "Cannot update payroll run with status 'approved'. Must be 'draft'."}
```

---

### TEST 9: POST `/api/payroll/runs/{payroll_run_id}/mark-paid` - Marcar Payroll como Pagado

#### Test 9.1: Marcar payroll APPROVED como pagado (debe funcionar)
```bash
# 1. Crear y aprobar payroll run
curl -X POST http://localhost:8000/api/payroll/runs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "pay_period_start": "2025-10-01T00:00:00",
    "pay_period_end": "2025-10-31T23:59:59",
    "created_by": "admin"
  }'

# Guardar ID (ej: 12)
export PAYROLL_RUN_ID_APPROVED=12

# 2. Aprobar el payroll run
curl -X POST http://localhost:8000/api/payroll/runs/$PAYROLL_RUN_ID_APPROVED/approve \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "approved_by": "admin",
    "notes": "Approved for payment"
  }'

# 3. Marcar como pagado
curl -X POST http://localhost:8000/api/payroll/runs/$PAYROLL_RUN_ID_APPROVED/mark-paid \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_date": "2025-11-12T15:00:00",
    "payment_method": "bank_transfer",
    "notes": "All employees paid via bank transfer"
  }'

# ✅ Resultado esperado: Status 200
# {
#   "success": true,
#   "payroll_run_id": 12,
#   "status": "paid",
#   "approved_by": null,
#   "approved_at": "2025-11-12T15:00:00"
# }
```

#### Test 9.2: Intentar marcar payroll DRAFT como pagado (debe fallar)
```bash
curl -X POST http://localhost:8000/api/payroll/runs/$PAYROLL_RUN_ID_DRAFT/mark-paid \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_date": "2025-11-12T15:00:00",
    "payment_method": "bank_transfer"
  }'

# ❌ Resultado esperado: Status 400
# {"detail": "Cannot mark payroll run as paid with status 'draft'. Must be 'approved'."}
```

---

## 📊 Checklist de Testing

### Endpoints de Salary
- [ ] PUT /api/salary/{id} - Actualizar salario no pagado ✅
- [ ] PUT /api/salary/{id} - Fallar al actualizar salario pagado ❌
- [ ] DELETE /api/salary/{id} - Eliminar salario no pagado ✅
- [ ] DELETE /api/salary/{id} - Fallar al eliminar salario pagado ❌
- [ ] POST /api/salary/{id}/mark-paid - Marcar como pagado ✅
- [ ] POST /api/salary/{id}/mark-paid - Fallar si ya está pagado ❌
- [ ] GET /api/salary/reports - Reporte básico ✅
- [ ] GET /api/salary/reports - Con filtros de empleados ✅
- [ ] GET /api/salary/reports - Con filtro de estado de pago ✅
- [ ] GET /api/salary/reports - Fallar con formato de fecha inválido ❌
- [ ] POST /api/salary/export/excel - Exportar con datos ✅
- [ ] POST /api/salary/export/excel - Fallar sin datos ❌
- [ ] POST /api/salary/export/pdf - Exportar con datos ✅
- [ ] POST /api/salary/export/pdf - Fallar sin datos ❌

### Endpoints de Payroll
- [ ] DELETE /api/payroll/runs/{id} - Eliminar draft ✅
- [ ] DELETE /api/payroll/runs/{id} - Fallar al eliminar approved ❌
- [ ] PUT /api/payroll/runs/{id} - Actualizar draft ✅
- [ ] PUT /api/payroll/runs/{id} - Fallar al actualizar approved ❌
- [ ] POST /api/payroll/runs/{id}/mark-paid - Marcar approved como pagado ✅
- [ ] POST /api/payroll/runs/{id}/mark-paid - Fallar al marcar draft ❌

---

## 🔍 Verificación de Swagger

1. Abrir navegador: http://localhost:8000/api/docs
2. Verificar que todos los nuevos endpoints aparezcan:
   - PUT /api/salary/{salary_id}
   - DELETE /api/salary/{salary_id}
   - POST /api/salary/{salary_id}/mark-paid
   - GET /api/salary/reports
   - POST /api/salary/export/excel
   - POST /api/salary/export/pdf
   - DELETE /api/payroll/runs/{payroll_run_id}
   - PUT /api/payroll/runs/{payroll_run_id}
   - POST /api/payroll/runs/{payroll_run_id}/mark-paid

3. Verificar que cada endpoint tenga:
   - Descripción completa
   - Schemas de request/response
   - Ejemplos
   - Botón "Try it out"

---

## 📝 Reporte de Bugs

Si encuentras algún bug durante el testing, documentar con:

```
Endpoint: PUT /api/salary/{id}
Request: {...}
Expected: Status 200, salario actualizado
Actual: Status 500, Internal Server Error
Error Message: {...}
Steps to Reproduce: 1) ..., 2) ..., 3) ...
```

---

**Autor:** Claude (Anthropic)
**Documento:** TESTING_GUIDE_SALARY_ENDPOINTS.md
**Estado:** ✅ LISTO PARA TESTING
