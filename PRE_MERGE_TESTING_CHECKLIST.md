# Pre-Merge Testing Checklist

**Branch**: `claude/analyze-timer-card-agents-011CV41DXT6SHZsDHxK96WJ9`
**Date**: 2025-11-12
**Total Changes**: 11 files, +2,901/-140 lines

## ✅ Validation Already Completed

- ✅ Python syntax validation (all files pass)
- ✅ TypeScript type checking (types/api.ts has no errors)
- ✅ Migration syntax validation
- ✅ Git commits created (6 commits)
- ✅ Pushed to remote successfully

## 🧪 Required Testing Before Merge

### 1. Code Review

**Reviewers should check:**
- [ ] Security improvements in `backend/app/api/timer_cards.py`
- [ ] RBAC implementation correctness
- [ ] Night hours calculation logic (22:00-05:00 JST)
- [ ] Holiday hours calculation logic (Japanese holidays)
- [ ] Rate limiting configuration
- [ ] Database migration correctness
- [ ] Test coverage adequacy

### 2. Backend Tests

```bash
# Pull latest code
git checkout claude/analyze-timer-card-agents-011CV41DXT6SHZsDHxK96WJ9
git pull origin claude/analyze-timer-card-agents-011CV41DXT6SHZsDHxK96WJ9

# Run timer card tests
docker exec uns-claudejp-backend pytest backend/tests/test_timer_card*.py -v

# Run with coverage
docker exec uns-claudejp-backend pytest backend/tests/test_timer_card*.py \
  --cov=app.api.timer_cards \
  --cov=app.services.payroll_integration_service \
  --cov-report=html \
  -v

# Check coverage report
# Coverage should be ~80% for timer_cards module
```

**Expected Results:**
- [ ] All tests pass
- [ ] No test failures or errors
- [ ] Coverage >= 80%

### 3. Database Migration

```bash
# Stop services
cd scripts && STOP.bat

# Start only database
docker compose up -d db

# Check current migration status
docker exec uns-claudejp-backend alembic current

# Apply new migration
docker exec uns-claudejp-backend alembic upgrade head

# Verify migration applied
docker exec uns-claudejp-backend alembic current
# Should show: 2025_11_12_1900 (head)

# Check database for new indexes
docker exec -it uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "
SELECT indexname, tablename
FROM pg_indexes
WHERE tablename = 'timer_cards'
ORDER BY indexname;
"

# Check constraints
docker exec -it uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "
SELECT conname, contype, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conrelid = 'timer_cards'::regclass;
"
```

**Expected Results:**
- [ ] Migration applies without errors
- [ ] 9 new indexes created on timer_cards table
- [ ] 7 CHECK constraints + 1 UNIQUE constraint added
- [ ] No existing data violations

### 4. Frontend Type Check

```bash
cd frontend

# Full type check
npm run type-check

# Check only our changes
npx tsc --noEmit types/api.ts

# Check for timer card related types
grep -n "TimerCard" types/api.ts
```

**Expected Results:**
- [ ] types/api.ts has no TypeScript errors
- [ ] TimerCard interface includes night_hours, holiday_hours
- [ ] No breaking changes in existing types

### 5. Integration Testing

```bash
# Start all services
cd scripts && START.bat

# Wait for services to be healthy (2-3 minutes)
docker compose ps

# Test backend health
curl http://localhost:8000/api/health

# Test frontend health
curl http://localhost:3000/api/health
```

#### 5.1 Timer Cards API Testing

```bash
# Login to get token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')

# Test GET all timer cards
curl -X GET http://localhost:8000/api/timer_cards/ \
  -H "Authorization: Bearer $TOKEN" \
  | jq

# Test GET single timer card (should work for admin)
curl -X GET http://localhost:8000/api/timer_cards/1 \
  -H "Authorization: Bearer $TOKEN" \
  | jq

# Test rate limiting (send 30 requests quickly)
for i in {1..30}; do
  curl -X GET http://localhost:8000/api/timer_cards/ \
    -H "Authorization: Bearer $TOKEN" \
    -w "\nRequest $i: %{http_code}\n"
done
# Should see 429 (Too Many Requests) after ~20 requests

# Test creating timer card with night hours
curl -X POST http://localhost:8000/api/timer_cards/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": 1,
    "work_date": "2025-11-12",
    "start_time": "22:00:00",
    "end_time": "06:00:00",
    "break_duration": 60
  }' | jq

# Should return timer card with night_hours calculated
```

**Expected Results:**
- [ ] All API endpoints respond correctly
- [ ] Rate limiting works (429 after threshold)
- [ ] Night hours calculated automatically
- [ ] Holiday hours calculated for Japanese holidays
- [ ] RBAC validation works (403 for unauthorized access)

#### 5.2 Frontend UI Testing

**Manual Steps:**

1. **Navigate to Timer Cards page**
   - [ ] Open http://localhost:3000/timercards
   - [ ] Page loads without errors
   - [ ] No console errors in browser dev tools

2. **List View**
   - [ ] Timer cards list loads quickly (<1 second)
   - [ ] Pagination works
   - [ ] Filtering works
   - [ ] Sorting works

3. **Create Timer Card**
   - [ ] Click "Add Timer Card" button
   - [ ] Fill in form with night shift (22:00-06:00)
   - [ ] Submit form
   - [ ] Verify night_hours is calculated and displayed
   - [ ] Check for validation errors on invalid input

4. **Edit Timer Card**
   - [ ] Click edit on existing timer card
   - [ ] Modify times
   - [ ] Save changes
   - [ ] Verify changes persisted

5. **Approve Timer Card**
   - [ ] Select unapproved timer card
   - [ ] Click approve button
   - [ ] Verify status changes to approved
   - [ ] Check audit trail shows approval

6. **RBAC Testing**
   - [ ] Login as different user roles
   - [ ] Verify EMPLOYEE can only see own timer cards
   - [ ] Verify ADMIN can see all timer cards
   - [ ] Verify unauthorized actions show error

### 6. Performance Testing

```bash
# Test query performance with indexes

# Before: baseline query (if rolling back migration for test)
docker exec -it uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "
EXPLAIN ANALYZE
SELECT * FROM timer_cards
WHERE employee_id = 1
AND work_date BETWEEN '2025-01-01' AND '2025-12-31'
ORDER BY work_date DESC;
"

# Should show index usage: "Index Scan using idx_timer_cards_employee_date"
# Execution time should be < 50ms

# Test with larger dataset (if available)
# Query should still be fast with 1000+ records
```

**Expected Results:**
- [ ] Queries use indexes (check EXPLAIN ANALYZE output)
- [ ] Query time < 50ms for typical queries
- [ ] No sequential scans on timer_cards table

### 7. OCR Timeout Testing

```bash
# Test OCR processing with timeout

# Upload a timer card image via API
curl -X POST http://localhost:8000/api/timer_cards/ocr \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/timer_card_image.jpg"

# Should complete within 30 seconds or return timeout error
# Check logs for timeout handling
docker compose logs backend | grep -i timeout
```

**Expected Results:**
- [ ] OCR completes within 30 seconds for normal images
- [ ] Timeout error returned gracefully after 30s
- [ ] No hanging requests
- [ ] Error message is clear and actionable

### 8. Security Testing

#### 8.1 IDOR Vulnerability Check

```bash
# Login as regular employee
EMPLOYEE_TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"employee","password":"employee123"}' \
  | jq -r '.access_token')

# Try to access another employee's timer card
curl -X GET http://localhost:8000/api/timer_cards/999 \
  -H "Authorization: Bearer $EMPLOYEE_TOKEN" \
  -w "\nHTTP Code: %{http_code}\n"

# Should return 403 Forbidden (not 200)
```

**Expected Results:**
- [ ] IDOR attempt returns 403 Forbidden
- [ ] Error message does not leak information
- [ ] Audit log records unauthorized attempt

#### 8.2 Rate Limiting Check

```bash
# Test rate limiting from single IP

for i in {1..150}; do
  curl -s -X GET http://localhost:8000/api/timer_cards/ \
    -H "Authorization: Bearer $TOKEN" \
    -w "%{http_code}\n" \
    -o /dev/null
  sleep 0.1
done | sort | uniq -c

# Should see:
# ~100 requests with 200
# ~50 requests with 429
```

**Expected Results:**
- [ ] Rate limiting kicks in after threshold
- [ ] 429 (Too Many Requests) returned with clear message
- [ ] Rate limit resets after time window

### 9. Payroll Integration Testing

```bash
# Test payroll integration with timer cards

# Approve a timer card first
curl -X PATCH http://localhost:8000/api/timer_cards/1/approve \
  -H "Authorization: Bearer $TOKEN"

# Run payroll calculation
curl -X POST http://localhost:8000/api/payroll/calculate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": 1,
    "start_date": "2025-11-01",
    "end_date": "2025-11-30"
  }' | jq

# Should include night_hours and holiday_hours in calculation

# Try with unapproved timer card (should fail)
curl -X POST http://localhost:8000/api/payroll/calculate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": 2,
    "start_date": "2025-11-01",
    "end_date": "2025-11-30"
  }' | jq

# Should return error if any timer cards are unapproved
```

**Expected Results:**
- [ ] Only approved timer cards included in payroll
- [ ] Night hours correctly calculated in payroll
- [ ] Holiday hours correctly calculated in payroll
- [ ] Error returned for unapproved timer cards

### 10. Rollback Testing (Optional but Recommended)

```bash
# Test rollback of migration (in staging only!)

# Rollback migration
docker exec uns-claudejp-backend alembic downgrade -1

# Verify indexes removed
docker exec -it uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "
SELECT COUNT(*) FROM pg_indexes WHERE tablename = 'timer_cards';
"

# Re-apply migration
docker exec uns-claudejp-backend alembic upgrade head

# Verify everything works again
```

**Expected Results:**
- [ ] Rollback removes indexes and constraints cleanly
- [ ] Re-applying migration works without errors
- [ ] No data loss during rollback/reapply

## 📊 Test Results Summary

| Test Category | Status | Notes |
|---------------|--------|-------|
| Code Review | ⏳ | |
| Backend Tests | ⏳ | |
| Database Migration | ⏳ | |
| Frontend Type Check | ✅ | types/api.ts validated |
| Integration Tests | ⏳ | |
| Performance Tests | ⏳ | |
| OCR Timeout Tests | ⏳ | |
| Security Tests | ⏳ | |
| Payroll Integration | ⏳ | |
| Rollback Tests | ⏳ | Optional |

## 🚫 Known Issues to Watch For

1. **Rate Limiting**: If using nginx/reverse proxy, ensure real IP is passed
2. **OCR Timeouts**: Large images may still timeout (consider image preprocessing)
3. **RBAC**: Manual integration required (see MANUAL_RBAC_UPDATES.md)
4. **Migration**: Test in staging first, backup production before applying
5. **Frontend**: Preexisting errors in payroll/page.tsx (not our changes)

## 🚀 Deployment Checklist

**Pre-Deployment:**
- [ ] All tests pass
- [ ] Code review approved
- [ ] Database backup created
- [ ] Rollback plan documented

**Deployment:**
- [ ] Pull latest code
- [ ] Stop services
- [ ] Apply database migration
- [ ] Start services
- [ ] Verify health checks

**Post-Deployment:**
- [ ] Smoke tests pass
- [ ] Monitor logs for errors
- [ ] Check performance metrics
- [ ] Verify RBAC behavior

## 📞 Support

If any tests fail:
1. Check logs: `docker compose logs backend`
2. Review error messages carefully
3. Check TIMER_CARD_REMEDIATION_COMPLETE.md for details
4. Contact development team

---

**Status**: Ready for testing
**Branch**: claude/analyze-timer-card-agents-011CV41DXT6SHZsDHxK96WJ9
**Estimated Testing Time**: 2-3 hours
**Priority**: HIGH (security fixes included)
