# 🔍 API & Authentication Verification Guide

## Verificación de API Endpoints

### 1. Verificar Backend API Health

```bash
# Dentro del contenedor backend o local
curl -X GET http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "ok",
  "version": "5.4.1",
  "environment": "development"
}
```

### 2. Verificar Todos los Endpoints

**Core Endpoints (27 routers):**

#### Authentication (auth/)
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Expected: JWT token response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 28800
}

# Refresh token
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Authorization: Bearer YOUR_TOKEN"

# Logout
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Candidates (candidates/)
```bash
# Get all candidates
curl -X GET http://localhost:8000/api/candidates \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create candidate
curl -X POST http://localhost:8000/api/candidates \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...candidate_data...}'

# Get candidate by ID
curl -X GET http://localhost:8000/api/candidates/{id} \
  -H "Authorization: Bearer YOUR_TOKEN"

# Update candidate
curl -X PUT http://localhost:8000/api/candidates/{id} \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...updated_data...}'

# Delete candidate
curl -X DELETE http://localhost:8000/api/candidates/{id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Employees (employees/)
```bash
curl -X GET http://localhost:8000/api/employees \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Factories (factories/)
```bash
curl -X GET http://localhost:8000/api/factories \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Timer Cards (timer_cards/)
```bash
curl -X GET http://localhost:8000/api/timer_cards \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Payroll (payroll/)
```bash
curl -X GET http://localhost:8000/api/payroll \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Requests (requests/)
```bash
curl -X GET http://localhost:8000/api/requests \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Dashboard (dashboard/)
```bash
curl -X GET http://localhost:8000/api/dashboard/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Admin (admin/)
```bash
curl -X GET http://localhost:8000/api/admin/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Verificar Documentación API

```bash
# Swagger UI
curl http://localhost:8000/api/docs

# ReDoc
curl http://localhost:8000/api/redoc

# OpenAPI JSON
curl http://localhost:8000/api/openapi.json
```

---

## 🔐 Authentication & Authorization Testing

### 1. JWT Token Validation

**Default Credentials:**
```
Username: admin
Password: admin123
```

### 2. Test Login Flow

```bash
# 1. Get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')

echo "Token: $TOKEN"

# 2. Use token to access protected endpoint
curl -X GET http://localhost:8000/api/candidates \
  -H "Authorization: Bearer $TOKEN"

# 3. Try with invalid token (should fail)
curl -X GET http://localhost:8000/api/candidates \
  -H "Authorization: Bearer invalid_token"
# Expected: 401 Unauthorized
```

### 3. Test Role-Based Access Control (RBAC)

**Available Roles:**
- SUPER_ADMIN
- ADMIN
- COORDINATOR
- KANRININSHA
- EMPLOYEE
- CONTRACT_WORKER

**Test endpoint with different roles:**

```bash
# Create user with specific role
curl -X POST http://localhost:8000/api/admin/users \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_coordinator",
    "password": "password123",
    "role": "COORDINATOR"
  }'

# Login as coordinator
COORD_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test_coordinator","password":"password123"}' \
  | jq -r '.access_token')

# Try to access admin-only endpoint (should fail)
curl -X GET http://localhost:8000/api/admin/stats \
  -H "Authorization: Bearer $COORD_TOKEN"
# Expected: 403 Forbidden (insufficient permissions)

# Try to access coordinator endpoint (should succeed)
curl -X GET http://localhost:8000/api/candidates \
  -H "Authorization: Bearer $COORD_TOKEN"
# Expected: 200 OK
```

### 4. Test Authorization Errors

```bash
# Missing token
curl -X GET http://localhost:8000/api/candidates
# Expected: 401 Unauthorized

# Invalid token format
curl -X GET http://localhost:8000/api/candidates \
  -H "Authorization: InvalidFormat token"
# Expected: 401 Unauthorized

# Expired token
# (Use token that's expired)
curl -X GET http://localhost:8000/api/candidates \
  -H "Authorization: Bearer expired_token"
# Expected: 401 Unauthorized
```

---

## 🧪 Backend Testing (pytest)

### Run All Tests

```bash
docker exec -it uns-claudejp-backend pytest backend/tests/ -v
```

### Run Specific Test File

```bash
docker exec -it uns-claudejp-backend pytest backend/tests/test_auth.py -v
```

### Run Tests Matching Pattern

```bash
docker exec -it uns-claudejp-backend pytest -k "test_login" -v
```

### Run with Coverage

```bash
docker exec -it uns-claudejp-backend pytest --cov=app backend/tests/
```

### Expected Test Files

```
backend/tests/
├── test_auth.py              # Authentication tests
├── test_candidates.py        # Candidate CRUD tests
├── test_employees.py         # Employee CRUD tests
├── test_factories.py         # Factory CRUD tests
├── test_timercards.py        # Timer card tests
├── test_payroll.py           # Payroll calculation tests
├── test_requests.py          # Request workflow tests
├── test_admin.py             # Admin operations tests
└── test_rbac.py              # Role-based access control tests
```

### Expected Results

```
============== 35+ tests passed ==============
```

---

## 🎭 Frontend Testing (npm)

### Type Checking

```bash
docker exec -it uns-claudejp-frontend npm run type-check
```

### Unit Tests

```bash
docker exec -it uns-claudejp-frontend npm test
```

### Build Verification

```bash
docker exec -it uns-claudejp-frontend npm run build
```

### Linting

```bash
docker exec -it uns-claudejp-frontend npm run lint
```

---

## 🎬 E2E Testing (Playwright)

See: **PLAYWRIGHT_TESTING_PLAN.md** for complete guide

### Quick E2E Tests

```bash
# Smoke tests (5 min)
docker exec -it uns-claudejp-frontend npm run test:e2e -- \
  01-login-dashboard.spec.ts navigation.spec.ts

# Full suite (60 min)
docker exec -it uns-claudejp-frontend npm run test:e2e
```

---

## ✅ Complete Testing Checklist

### Phase 1: API Health (5 min)
- [ ] GET /api/health returns 200 OK
- [ ] Swagger UI accessible at /api/docs
- [ ] ReDoc accessible at /api/redoc

### Phase 2: Authentication (10 min)
- [ ] Login with admin/admin123 returns JWT token
- [ ] Token can be used to access protected endpoints
- [ ] Invalid credentials return 401
- [ ] Missing token returns 401
- [ ] Expired token returns 401

### Phase 3: RBAC (15 min)
- [ ] Admin can access all endpoints
- [ ] Coordinator can access coordinator endpoints
- [ ] Employee gets 403 on admin endpoints
- [ ] Role-based filtering works (users only see their data)

### Phase 4: API Endpoints (30 min)
- [ ] Candidates: GET, POST, PUT, DELETE all work
- [ ] Employees: CRUD operations functional
- [ ] Factories: CRUD operations functional
- [ ] Timer Cards: CRUD operations functional
- [ ] Payroll: Calculations correct
- [ ] Requests: Workflow transitions work

### Phase 5: Backend Tests (20 min)
- [ ] All pytest tests pass (35+)
- [ ] No test failures
- [ ] Coverage > 80%

### Phase 6: Frontend Type Check (10 min)
- [ ] npm run type-check passes
- [ ] No TypeScript errors
- [ ] npm run lint passes

### Phase 7: Frontend Build (20 min)
- [ ] npm run build succeeds
- [ ] No build errors
- [ ] Bundle size acceptable

### Phase 8: E2E Tests (60 min)
- [ ] All 15 Playwright tests pass
- [ ] Login flow works
- [ ] Navigation works
- [ ] CRUD operations functional
- [ ] Yukyu system functional
- [ ] Payroll system functional
- [ ] Admin panel functional

---

## 🐛 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Check token is valid and not expired |
| 403 Forbidden | Check user has required role/permissions |
| 404 Not Found | Check endpoint URL is correct |
| Connection refused | Ensure backend is running on port 8000 |
| CORS errors | Check FRONTEND_URL in .env |
| Type errors | Run npm run type-check and fix |
| Test failures | Check Docker containers are healthy |

---

## 📊 Testing Strategy

**Recommended execution order:**

1. **API Health Check** (5 min) - Quick verification
2. **Manual API Testing** (15 min) - curl requests
3. **Authentication Testing** (10 min) - JWT and RBAC
4. **Backend Tests** (20 min) - pytest suite
5. **Frontend Type Check** (10 min) - TypeScript
6. **Frontend Build** (20 min) - Production build
7. **E2E Tests** (60 min) - Playwright suite

**Total time: ~140 minutes (~2.5 hours)**

---

## 🎯 Success Criteria

✅ All health checks pass
✅ All API endpoints respond correctly
✅ Authentication and RBAC work properly
✅ All backend tests pass (35+)
✅ No TypeScript errors
✅ Build succeeds without errors
✅ All E2E tests pass (15 suites)

If all criteria are met, the application is **ready for production deployment**.

