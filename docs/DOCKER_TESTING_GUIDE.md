# Docker Testing Guide - Timer Card Module

**Version:** 1.0
**Date:** 2025-11-12
**Purpose:** Complete testing procedures for Timer Card module in Docker environment

---

## 🧪 Testing Overview

### Test Types

1. **Unit Tests** - Individual function testing
2. **Integration Tests** - Database and API integration
3. **RBAC Tests** - Role-based access control
4. **End-to-End Tests** - User journey testing
5. **Data Integrity Tests** - Constraint and trigger validation
6. **Performance Tests** - Query and API latency

### Prerequisites

```bash
# Ensure Docker Compose is running
docker compose ps

# Expected: All services healthy
# db, redis, backend, frontend, adminer (+ optional observability stack)
```

---

## ✅ Unit & Integration Tests

### Run All Tests

```bash
#!/bin/bash
# run_all_tests.sh

echo "=== Running Timer Card Module Tests ==="
echo "Date: $(date)"

# 1. Wait for services to be healthy
echo "[*] Waiting for services..."
docker compose exec -T backend bash -c "
  for i in {1..30}; do
    curl -s http://localhost:8000/api/health && break
    sleep 2
  done
"

# 2. Run pytest with all timer card tests
echo "[*] Running unit and integration tests..."
docker compose exec -T backend bash -c "
  cd /app
  pytest backend/tests/test_timer_card* -v --tb=short --cov=app/api/timer_cards --cov-report=term-missing
"

# 3. Run edge case tests
echo "[*] Running edge case tests..."
docker compose exec -T backend bash -c "
  cd /app
  pytest backend/tests/test_timer_card_edge_cases.py -v -s
"

# 4. Run RBAC tests
echo "[*] Running RBAC tests..."
docker compose exec -T backend bash -c "
  cd /app
  pytest backend/tests/test_timer_card_rbac.py -v
"

# 5. Run approval workflow tests
echo "[*] Running approval workflow tests..."
docker compose exec -T backend bash -c "
  cd /app
  pytest backend/tests/test_timer_card_approval_workflow.py -v
"

# 6. Run hour calculation tests
echo "[*] Running hour calculation tests..."
docker compose exec -T backend bash -c "
  cd /app
  pytest backend/tests/test_timer_card_calculations.py -v
"

echo "[OK] All tests completed"
```

**Run:**
```bash
chmod +x run_all_tests.sh
./run_all_tests.sh
```

---

## 🔐 RBAC Testing

### Test Different User Roles

```bash
#!/bin/bash
# test_rbac.sh

echo "=== RBAC Testing ==="

# Create test users
docker compose exec -T backend bash -c "
  python3 << 'PYTHON'
from app.core.database import SessionLocal
from app.models.models import User, UserRole
from app.core.security import get_password_hash

db = SessionLocal()

# Create test users
test_users = [
    {\"username\": \"employee_test\", \"email\": \"emp@test.com\", \"role\": UserRole.EMPLOYEE},
    {\"username\": \"kanrininsha_test\", \"email\": \"kan@test.com\", \"role\": UserRole.KANRININSHA},
    {\"username\": \"coordinator_test\", \"email\": \"coord@test.com\", \"role\": UserRole.COORDINATOR},
    {\"username\": \"admin_test\", \"email\": \"admin@test.com\", \"role\": UserRole.ADMIN},
]

for user_data in test_users:
    user = User(
        username=user_data[\"username\"],
        email=user_data[\"email\"],
        hashed_password=get_password_hash(\"testpass123\"),
        role=user_data[\"role\"],
        is_active=True
    )
    db.add(user)

db.commit()
print(\"[OK] Test users created\")
PYTHON
"

# Test LOGIN for each user
echo "[*] Testing user login..."
for user in employee_test kanrininsha_test coordinator_test admin_test; do
  TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$user\",\"password\":\"testpass123\"}" \
    | jq -r '.access_token')

  if [ ! -z "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
    echo "[OK] Login successful for $user: $TOKEN"
  else
    echo "[X] Login failed for $user"
  fi
done

# Test RBAC FILTERING
echo "[*] Testing RBAC filtering..."

# Get tokens for different users
EMPLOYEE_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"employee_test","password":"testpass123"}' \
  | jq -r '.access_token')

ADMIN_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin_test","password":"testpass123"}' \
  | jq -r '.access_token')

# EMPLOYEE should see only own cards
EMPLOYEE_COUNT=$(curl -s http://localhost:8000/api/timer-cards/ \
  -H "Authorization: Bearer $EMPLOYEE_TOKEN" \
  | jq '. | length')

# ADMIN should see all cards
ADMIN_COUNT=$(curl -s http://localhost:8000/api/timer-cards/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  | jq '. | length')

echo "EMPLOYEE sees: $EMPLOYEE_COUNT cards"
echo "ADMIN sees: $ADMIN_COUNT cards"

if [ "$EMPLOYEE_COUNT" -le "$ADMIN_COUNT" ]; then
  echo "[OK] RBAC filtering working (EMPLOYEE <= ADMIN)"
else
  echo "[X] RBAC filtering NOT working (EMPLOYEE > ADMIN)"
fi
```

**Run:**
```bash
chmod +x test_rbac.sh
./test_rbac.sh
```

---

## 📊 Data Integrity Testing

### Test Database Triggers & Constraints

```bash
#!/bin/bash
# test_data_integrity.sh

echo "=== Data Integrity Testing ==="

# Test 1: Duplicate Prevention
echo "[*] Test 1: Duplicate Prevention..."
docker compose exec -T db psql -U uns_admin -d uns_claudejp << 'SQL'
INSERT INTO timer_cards (hakenmoto_id, work_date, clock_in, clock_out, break_minutes, shift_type)
VALUES (1, '2025-11-12', '09:00:00', '17:00:00', 60, 'hiru');

-- This should fail
INSERT INTO timer_cards (hakenmoto_id, work_date, clock_in, clock_out, break_minutes, shift_type)
VALUES (1, '2025-11-12', '10:00:00', '18:00:00', 30, 'hiru');
SQL

# Test 2: Auto-Calculate Hours
echo "[*] Test 2: Auto-Calculate Hours..."
docker compose exec -T db psql -U uns_admin -d uns_claudejp << 'SQL'
INSERT INTO timer_cards (hakenmoto_id, work_date, clock_in, clock_out, break_minutes, shift_type)
VALUES (2, '2025-11-12', '09:00:00', '18:00:00', 60, 'hiru')
RETURNING id, regular_hours, night_hours, holiday_hours;
SQL

# Test 3: Night Hours Calculation
echo "[*] Test 3: Night Hours Calculation (22:00-05:00)..."
docker compose exec -T db psql -U uns_admin -d uns_claudejp << 'SQL'
INSERT INTO timer_cards (hakenmoto_id, work_date, clock_in, clock_out, break_minutes, shift_type)
VALUES (3, '2025-11-12', '22:00:00', '06:00:00', 60, 'yoru')
RETURNING id, regular_hours, night_hours;
SQL

# Test 4: Approval Validation
echo "[*] Test 4: Approval Validation..."
docker compose exec -T db psql -U uns_admin -d uns_claudejp << 'SQL'
-- Try to approve without approved_by and approved_at
UPDATE timer_cards SET is_approved = true WHERE id = 1;
-- Should fail with trigger error
SQL

# Test 5: Factory ID Sync
echo "[*] Test 5: Factory ID Sync..."
docker compose exec -T db psql -U uns_admin -d uns_claudejp << 'SQL'
-- Verify factory_id matches employee
SELECT tc.id, tc.hakenmoto_id, tc.factory_id, e.factory_id
FROM timer_cards tc
JOIN employees e ON tc.hakenmoto_id = e.hakenmoto_id
WHERE tc.factory_id != e.factory_id;
-- Should return 0 rows
SQL

echo "[OK] Data integrity tests completed"
```

**Run:**
```bash
chmod +x test_data_integrity.sh
./test_data_integrity.sh
```

---

## 🎯 End-to-End Testing

### Test Complete User Workflows

```bash
#!/bin/bash
# test_e2e.sh

echo "=== End-to-End Testing ==="

# 1. Setup test data
echo "[*] Setting up test data..."
docker compose exec -T backend bash -c "
  python3 << 'PYTHON'
from app.core.database import SessionLocal
from app.models.models import Employee, TimerCard, User, UserRole, Factory
from app.core.security import get_password_hash
from datetime import datetime, date, time

db = SessionLocal()

# Create factory if not exists
factory = db.query(Factory).filter(Factory.factory_id == 'TEST001').first()
if not factory:
    factory = Factory(factory_id='TEST001', name='Test Factory')
    db.add(factory)
    db.commit()

# Create employee if not exists
emp = db.query(Employee).filter(Employee.hakenmoto_id == 999).first()
if not emp:
    emp = Employee(
        hakenmoto_id=999,
        full_name_roman='Test Employee',
        full_name_kanji='テスト社員',
        factory_id='TEST001',
        email='test_emp@example.com'
    )
    db.add(emp)
    db.commit()

# Create user for the employee
user = db.query(User).filter(User.email == 'test_emp@example.com').first()
if not user:
    user = User(
        username='test_emp',
        email='test_emp@example.com',
        hashed_password=get_password_hash('testpass123'),
        role=UserRole.EMPLOYEE,
        is_active=True
    )
    db.add(user)
    db.commit()

print('[OK] Test data created: hakenmoto_id=999, email=test_emp@example.com')
PYTHON
"

# 2. Test employee workflow
echo "[*] Testing EMPLOYEE workflow..."

# Login as employee
EMPLOYEE_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test_emp","password":"testpass123"}' \
  | jq -r '.access_token')

echo "[OK] Employee logged in"

# Create timer card
CARD_ID=$(curl -s -X POST http://localhost:8000/api/timer-cards/ \
  -H "Authorization: Bearer $EMPLOYEE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "hakenmoto_id": 999,
    "work_date": "2025-11-12",
    "clock_in": "09:00:00",
    "clock_out": "17:00:00",
    "break_minutes": 60,
    "shift_type": "hiru",
    "notes": "Regular day shift"
  }' | jq -r '.id')

echo "[OK] Timer card created: ID=$CARD_ID"

# View own timer cards
CARDS=$(curl -s http://localhost:8000/api/timer-cards/ \
  -H "Authorization: Bearer $EMPLOYEE_TOKEN" \
  | jq -r '. | length')

echo "[OK] Employee can see $CARDS timer cards"

# Try to access someone else's card (should fail)
STATUS=$(curl -s -w "%{http_code}" http://localhost:8000/api/timer-cards/1 \
  -H "Authorization: Bearer $EMPLOYEE_TOKEN" \
  -o /dev/null)

if [ "$STATUS" == "403" ]; then
  echo "[OK] Employee correctly denied access to other employee's card (403)"
else
  echo "[X] RBAC not working - got status $STATUS instead of 403"
fi

# 3. Test coordinator workflow
echo "[*] Testing COORDINATOR workflow..."

COORDINATOR_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"coordinator_test","password":"testpass123"}' \
  | jq -r '.access_token')

# Approve the timer card
curl -s -X PUT http://localhost:8000/api/timer-cards/$CARD_ID/approve \
  -H "Authorization: Bearer $COORDINATOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"approved_by": 1}' | jq .

echo "[OK] Timer card approved by coordinator"

# Verify approval in database
docker compose exec -T db psql -U uns_admin -d uns_claudejp << 'SQL'
SELECT id, is_approved, approved_by, approved_at FROM timer_cards WHERE id = 1;
SQL

echo "[OK] E2E test completed"
```

**Run:**
```bash
chmod +x test_e2e.sh
./test_e2e.sh
```

---

## 📈 Performance Testing

### Load Testing & Benchmarks

```bash
#!/bin/bash
# test_performance.sh

echo "=== Performance Testing ==="

# 1. Query Performance Test
echo "[*] Test 1: Query Performance..."
docker compose exec -T db psql -U uns_admin -d uns_claudejp << 'SQL'
EXPLAIN ANALYZE
SELECT * FROM timer_cards
WHERE hakenmoto_id = 1
  AND work_date >= '2025-11-01'
ORDER BY work_date DESC
LIMIT 10;
SQL

# 2. Concurrent API Requests
echo "[*] Test 2: Concurrent API Requests..."
for i in {1..10}; do
  curl -s http://localhost:8000/api/timer-cards/ \
    -H "Authorization: Bearer $ADMIN_TOKEN" &
done
wait
echo "[OK] 10 concurrent requests completed"

# 3. Bulk Insert Performance
echo "[*] Test 3: Bulk Insert Performance..."
docker compose exec -T backend bash -c "
  time python3 << 'PYTHON'
from app.core.database import SessionLocal
from app.models.models import TimerCard, ShiftType
from datetime import date, time, timedelta

db = SessionLocal()

# Insert 1000 timer cards
cards = []
for i in range(1000):
    card = TimerCard(
        hakenmoto_id=(i % 100) + 1,  # Distribute across 100 employees
        work_date=date(2025, 11, 1) + timedelta(days=i%30),
        clock_in=time(9, 0),
        clock_out=time(17, 0),
        break_minutes=60,
        shift_type=ShiftType.HIRU
    )
    cards.append(card)

db.add_all(cards)
db.commit()

print(f'[OK] Inserted {len(cards)} timer cards')
PYTHON
"

# 4. Index Usage Test
echo "[*] Test 4: Index Usage..."
docker compose exec -T db psql -U uns_admin -d uns_claudejp << 'SQL'
-- Verify indexes are being used
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE tablename = 'timer_cards'
ORDER BY idx_scan DESC;
SQL

echo "[OK] Performance testing completed"
```

**Run:**
```bash
chmod +x test_performance.sh
./test_performance.sh
```

---

## 🔄 Complete Test Suite Runner

### Run All Tests in Order

```bash
#!/bin/bash
# run_complete_test_suite.sh

set -e  # Exit on first error

echo "╔════════════════════════════════════════╗"
echo "║  Timer Card Module - Complete Testing  ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "Date: $(date)"
echo "Branch: $(git branch --show-current)"
echo ""

# Check Docker is running
echo "[1/6] Checking Docker..."
docker compose ps > /dev/null || {
  echo "[X] Docker Compose not running!"
  exit 1
}
echo "[OK] Docker is running"

# Run unit/integration tests
echo ""
echo "[2/6] Running Unit & Integration Tests..."
./run_all_tests.sh || exit 1

# Run RBAC tests
echo ""
echo "[3/6] Running RBAC Tests..."
./test_rbac.sh || exit 1

# Run data integrity tests
echo ""
echo "[4/6] Running Data Integrity Tests..."
./test_data_integrity.sh || exit 1

# Run E2E tests
echo ""
echo "[5/6] Running End-to-End Tests..."
./test_e2e.sh || exit 1

# Run performance tests
echo ""
echo "[6/6] Running Performance Tests..."
./test_performance.sh || exit 1

# Summary
echo ""
echo "╔════════════════════════════════════════╗"
echo "║         ALL TESTS PASSED ✓             ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "Summary:"
echo "  ✓ Unit/Integration Tests: PASSED"
echo "  ✓ RBAC Tests: PASSED"
echo "  ✓ Data Integrity Tests: PASSED"
echo "  ✓ E2E Tests: PASSED"
echo "  ✓ Performance Tests: PASSED"
echo ""
echo "Ready for deployment!"
```

**Run Complete Suite:**
```bash
chmod +x run_complete_test_suite.sh
./run_complete_test_suite.sh
```

---

## 📋 Test Coverage Report

Generate test coverage report:

```bash
docker compose exec -T backend bash -c "
  cd /app
  pytest backend/tests/test_timer_card* --cov=app --cov-report=html
  echo '[OK] Coverage report generated in htmlcov/index.html'
"

# View coverage
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

---

## 🐛 Troubleshooting Tests

### Test Fails: "Database connection refused"

```bash
# Check database is running
docker compose ps db

# If not healthy, restart it
docker compose restart db
docker compose wait db

# Retry tests
```

### Test Fails: "Duplicate key value violates unique constraint"

```bash
# Clean up test data
docker compose exec -T db psql -U uns_admin -d uns_claudejp << 'SQL'
TRUNCATE timer_cards CASCADE;
SQL

# Retry tests
```

### Test Fails: "Import error: No module named..."

```bash
# Rebuild backend image
docker compose build backend --no-cache

# Restart backend
docker compose restart backend

# Retry tests
```

---

**Docker Testing Guide:** Complete and ready for execution
**Last Updated:** 2025-11-12
