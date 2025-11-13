# RBAC Timer Cards - Guía de Testing

## 🧪 Testing Manual del RBAC

### Pre-requisitos

1. **Backend corriendo:**
   ```bash
   docker compose up -d backend
   docker compose logs -f backend
   ```

2. **Usuarios de prueba necesarios:**
   - Employee: `employee@test.com` / password (rol: EMPLOYEE)
   - Manager: `manager@test.com` / password (rol: KANRININSHA)
   - Admin: `admin@test.com` / password (rol: ADMIN)

3. **Employee records en DB:**
   - Employee con email `employee@test.com` → hakenmoto_id=100
   - Manager con email `manager@test.com` → factory_id=FACTORY_A

---

## 📍 Test Suite 1: GET `/api/timer_cards/` (List)

### Test 1.1: Employee ve solo sus timer cards ✅

**Setup:**
```sql
-- Crear timer cards de prueba
INSERT INTO timer_cards (hakenmoto_id, work_date, clock_in, clock_out, is_approved)
VALUES
  (100, '2025-11-10', '09:00', '18:00', false),  -- Del employee
  (101, '2025-11-10', '09:00', '18:00', false);  -- De otro employee
```

**Test:**
```bash
# 1. Login como employee
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "employee@test.com",
    "password": "password"
  }'
# Response: { "access_token": "TOKEN_EMPLOYEE", ... }

# 2. List timer cards
curl -X GET http://localhost:8000/api/timer_cards/ \
  -H "Authorization: Bearer TOKEN_EMPLOYEE"
```

**Expected Result:**
```json
[
  {
    "id": 1,
    "hakenmoto_id": 100,  // ✅ Solo su timer card
    "work_date": "2025-11-10",
    ...
  }
]
// ❌ NO debe incluir hakenmoto_id=101
```

**Verification:**
```bash
# Check logs
docker compose logs backend | grep "filtering timer cards"
# Debe mostrar: "User employee filtering timer cards for hakenmoto_id=100"
```

---

### Test 1.2: Manager ve solo su factory ✅

**Setup:**
```sql
-- Crear timer cards de diferentes factories
INSERT INTO timer_cards (hakenmoto_id, factory_id, work_date, clock_in, clock_out)
VALUES
  (200, 'FACTORY_A', '2025-11-10', '09:00', '18:00'),  -- Su factory
  (201, 'FACTORY_B', '2025-11-10', '09:00', '18:00');  -- Otra factory
```

**Test:**
```bash
# 1. Login como manager
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "manager@test.com",
    "password": "password"
  }'
# Response: { "access_token": "TOKEN_MANAGER", ... }

# 2. List timer cards
curl -X GET http://localhost:8000/api/timer_cards/ \
  -H "Authorization: Bearer TOKEN_MANAGER"
```

**Expected Result:**
```json
[
  {
    "id": 10,
    "factory_id": "FACTORY_A",  // ✅ Solo su factory
    ...
  }
]
// ❌ NO debe incluir factory_id=FACTORY_B
```

---

### Test 1.3: Admin ve TODOS los timer cards ✅

**Test:**
```bash
# 1. Login como admin
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin@test.com",
    "password": "password"
  }'

# 2. List timer cards
curl -X GET http://localhost:8000/api/timer_cards/ \
  -H "Authorization: Bearer TOKEN_ADMIN"
```

**Expected Result:**
```json
[
  { "id": 1, "hakenmoto_id": 100, ... },
  { "id": 2, "hakenmoto_id": 101, ... },
  { "id": 10, "factory_id": "FACTORY_A", ... },
  { "id": 11, "factory_id": "FACTORY_B", ... }
]
// ✅ Debe incluir TODOS los timer cards sin filtrado
```

---

## 📍 Test Suite 2: GET `/api/timer_cards/{id}` (Get by ID)

### Test 2.1: Employee accede a su timer card ✅

**Test:**
```bash
# Employee intenta acceder a SU timer card (id=1, hakenmoto_id=100)
curl -X GET http://localhost:8000/api/timer_cards/1 \
  -H "Authorization: Bearer TOKEN_EMPLOYEE"
```

**Expected Result:**
```json
{
  "id": 1,
  "hakenmoto_id": 100,
  "work_date": "2025-11-10",
  ...
}
// ✅ Status 200 OK
```

**Log Expected:**
```
INFO: User employee accessed timer card 1
```

---

### Test 2.2: Employee intenta acceder a timer card ajeno ❌

**Test:**
```bash
# Employee intenta acceder a timer card de otro (id=2, hakenmoto_id=101)
curl -X GET http://localhost:8000/api/timer_cards/2 \
  -H "Authorization: Bearer TOKEN_EMPLOYEE"
```

**Expected Result:**
```json
{
  "detail": "Access denied: You can only view your own timer cards"
}
// ✅ Status 403 Forbidden
```

**Log Expected:**
```
WARNING: User employee attempted to access timer card 2 belonging to different employee
```

---

### Test 2.3: Manager accede a timer card de su factory ✅

**Test:**
```bash
# Manager intenta acceder a timer card de FACTORY_A (id=10)
curl -X GET http://localhost:8000/api/timer_cards/10 \
  -H "Authorization: Bearer TOKEN_MANAGER"
```

**Expected Result:**
```json
{
  "id": 10,
  "factory_id": "FACTORY_A",
  ...
}
// ✅ Status 200 OK
```

---

### Test 2.4: Manager intenta acceder a otra factory ❌

**Test:**
```bash
# Manager intenta acceder a timer card de FACTORY_B (id=11)
curl -X GET http://localhost:8000/api/timer_cards/11 \
  -H "Authorization: Bearer TOKEN_MANAGER"
```

**Expected Result:**
```json
{
  "detail": "Access denied: You can only view timer cards from your factory"
}
// ✅ Status 403 Forbidden
```

**Log Expected:**
```
WARNING: Manager manager attempted to access timer card from different factory
```

---

## 📍 Test Suite 3: Edge Cases

### Test 3.1: Employee sin Employee record ❌

**Setup:**
```sql
-- Usuario employee2 existe en users pero NO en employees
INSERT INTO users (username, email, role, password_hash)
VALUES ('employee2', 'employee2@test.com', 'EMPLOYEE', 'hash');
```

**Test:**
```bash
# Login como employee2
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "employee2@test.com",
    "password": "password"
  }'

# List timer cards
curl -X GET http://localhost:8000/api/timer_cards/ \
  -H "Authorization: Bearer TOKEN_EMPLOYEE2"
```

**Expected Result:**
```json
[]
// ✅ Lista vacía (no timer cards)
```

**Log Expected:**
```
WARNING: User employee2 (role: EMPLOYEE) has no employee record
```

---

### Test 3.2: Manager sin factory_id ❌

**Setup:**
```sql
-- Manager sin factory_id asignado
INSERT INTO employees (hakenmoto_id, email, factory_id)
VALUES (300, 'manager2@test.com', NULL);
```

**Test:**
```bash
# List timer cards como manager sin factory
curl -X GET http://localhost:8000/api/timer_cards/ \
  -H "Authorization: Bearer TOKEN_MANAGER2"
```

**Expected Result:**
```json
[]
// ✅ Lista vacía
```

**Log Expected:**
```
WARNING: Manager manager2 has no factory assignment
```

---

### Test 3.3: Timer card inexistente ❌

**Test:**
```bash
# Acceder a ID que no existe
curl -X GET http://localhost:8000/api/timer_cards/99999 \
  -H "Authorization: Bearer TOKEN_ADMIN"
```

**Expected Result:**
```json
{
  "detail": "Timer card not found"
}
// ✅ Status 404 Not Found
```

---

## 🐍 Python Test Script (Pytest)

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# ============================================
# Test Setup
# ============================================

@pytest.fixture
def employee_token():
    """Login as employee and return token"""
    response = client.post("/api/auth/login", json={
        "username": "employee@test.com",
        "password": "password"
    })
    return response.json()["access_token"]

@pytest.fixture
def manager_token():
    """Login as manager and return token"""
    response = client.post("/api/auth/login", json={
        "username": "manager@test.com",
        "password": "password"
    })
    return response.json()["access_token"]

@pytest.fixture
def admin_token():
    """Login as admin and return token"""
    response = client.post("/api/auth/login", json={
        "username": "admin@test.com",
        "password": "password"
    })
    return response.json()["access_token"]

# ============================================
# RBAC Tests
# ============================================

def test_employee_sees_only_own_timer_cards(employee_token):
    """Employee should only see their own timer cards"""
    headers = {"Authorization": f"Bearer {employee_token}"}
    response = client.get("/api/timer_cards/", headers=headers)

    assert response.status_code == 200
    timer_cards = response.json()

    # All timer cards should belong to this employee (hakenmoto_id=100)
    for card in timer_cards:
        assert card["hakenmoto_id"] == 100

def test_employee_cannot_access_other_timer_card(employee_token):
    """Employee should get 403 when accessing other's timer card"""
    headers = {"Authorization": f"Bearer {employee_token}"}
    # Assuming timer_card id=2 belongs to hakenmoto_id=101 (not this employee)
    response = client.get("/api/timer_cards/2", headers=headers)

    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]

def test_manager_sees_only_factory_timer_cards(manager_token):
    """Manager should only see timer cards from their factory"""
    headers = {"Authorization": f"Bearer {manager_token}"}
    response = client.get("/api/timer_cards/", headers=headers)

    assert response.status_code == 200
    timer_cards = response.json()

    # All timer cards should be from FACTORY_A
    for card in timer_cards:
        assert card["factory_id"] == "FACTORY_A"

def test_manager_cannot_access_other_factory_timer_card(manager_token):
    """Manager should get 403 when accessing other factory's timer card"""
    headers = {"Authorization": f"Bearer {manager_token}"}
    # Assuming timer_card id=11 belongs to FACTORY_B
    response = client.get("/api/timer_cards/11", headers=headers)

    assert response.status_code == 403
    assert "different factory" in response.json()["detail"]

def test_admin_sees_all_timer_cards(admin_token):
    """Admin should see all timer cards without restrictions"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/timer_cards/", headers=headers)

    assert response.status_code == 200
    timer_cards = response.json()

    # Should include timer cards from multiple hakenmoto_ids and factories
    hakenmoto_ids = {card["hakenmoto_id"] for card in timer_cards}
    assert len(hakenmoto_ids) > 1  # Multiple employees

def test_employee_without_employee_record_gets_empty_list(db_session):
    """Employee user without employee record should get empty list"""
    # Create user without employee record
    # ... (setup code)

    # Login and get timer cards
    # Should return []
    pass

def test_nonexistent_timer_card_returns_404(admin_token):
    """Accessing non-existent timer card should return 404"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/timer_cards/99999", headers=headers)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
```

---

## 📊 Checklist de Testing

### GET `/` Endpoint:
- [ ] EMPLOYEE ve solo sus timer cards (hakenmoto_id match)
- [ ] EMPLOYEE sin employee record → lista vacía
- [ ] KANRININSHA ve solo su factory (factory_id match)
- [ ] KANRININSHA sin factory_id → lista vacía
- [ ] COORDINATOR ve todos los timer cards
- [ ] ADMIN ve todos los timer cards sin filtrado
- [ ] Logs INFO aparecen correctamente
- [ ] Logs WARNING aparecen para edge cases

### GET `/{id}` Endpoint:
- [ ] EMPLOYEE accede a su timer card → 200 OK
- [ ] EMPLOYEE intenta acceder a otro → 403 Forbidden
- [ ] KANRININSHA accede a su factory → 200 OK
- [ ] KANRININSHA intenta acceder a otra factory → 403 Forbidden
- [ ] ADMIN accede a cualquier timer card → 200 OK
- [ ] Timer card inexistente → 404 Not Found
- [ ] Logs INFO registran accesos exitosos
- [ ] Logs WARNING registran intentos denegados

### Performance:
- [ ] N+1 queries prevenidos (eager loading)
- [ ] Límite máximo 1000 registros respetado
- [ ] ORDER BY work_date DESC funciona
- [ ] Response times < 500ms con 1000 registros

---

## 🔍 Verificación de Logs

**Buscar logs relevantes:**
```bash
# Filtrado por rol
docker compose logs backend | grep "filtering timer cards"

# Warnings de acceso denegado
docker compose logs backend | grep "attempted to access"

# Employee sin record
docker compose logs backend | grep "has no employee record"

# Manager sin factory
docker compose logs backend | grep "has no factory assignment"

# Accesos exitosos
docker compose logs backend | grep "accessed timer card"
```

---

## ✅ Criterios de Éxito

**RBAC considerado exitoso si:**

1. ✅ Employees solo ven sus propios timer cards
2. ✅ Managers solo ven timer cards de su factory
3. ✅ Admins ven todos sin restricciones
4. ✅ 403 Forbidden para accesos no autorizados
5. ✅ 404 Not Found para IDs inexistentes
6. ✅ Logs completos (INFO + WARNING)
7. ✅ Performance aceptable (< 500ms)
8. ✅ Sin breaking changes en otros endpoints

---

**Autor:** Claude Code
**Fecha:** 2025-11-12
**Versión:** 1.0
