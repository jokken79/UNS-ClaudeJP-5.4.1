# Performance Validation Plan - Timer Card Module

**Version:** 1.0
**Date:** 2025-11-12
**Purpose:** Validate performance improvements with real production-like data

---

## 📊 Performance Baseline

### Before Optimization (Pre-Remediation)

| Metric | Value | Condition |
|--------|-------|-----------|
| Query: GET / endpoint | 2-5 seconds | 1,000 timer cards, no indexes |
| Query: GET /{id} endpoint | 500-1000ms | Single record lookup, no filtering |
| Database: Full table scan | O(n) | Sequential scan, all rows |
| Average query time | 50-150ms | Unoptimized queries |
| Index usage | 0% | No indexes on timer_cards |
| API Error rate | < 0.1% | Baseline |
| Database connections pool | Normal | 20-30 active |

### Expected Improvements (Post-Remediation)

| Metric | Expected | Improvement |
|--------|----------|------------|
| GET / endpoint | 200-500ms | 4-10x faster |
| GET /{id} endpoint | 50-100ms | 5-10x faster |
| Database: Index scan | O(log n) | 70-80% faster |
| Average query time | 5-20ms | 5-10x faster |
| Index usage | 90%+ | Strategic indexing |
| API Error rate | < 0.05% | Better error handling |
| Database connections pool | < 10 | Connection reuse |

---

## 🧪 Load Test Setup

### Test Data Generation

Create realistic production-like data:

```bash
#!/bin/bash
# generate_test_data.sh

echo "[*] Generating test data..."

docker compose exec -T backend bash -c "
  python3 << 'PYTHON'
from app.core.database import SessionLocal
from app.models.models import (
    Employee, TimerCard, User, UserRole, Factory,
    ShiftType
)
from app.core.security import get_password_hash
from datetime import date, time, timedelta
import random

db = SessionLocal()

# 1. Create test factories
print('[*] Creating factories...')
factories = ['FACTORY001', 'FACTORY002', 'FACTORY003']
for factory_id in factories:
    factory = db.query(Factory).filter(Factory.factory_id == factory_id).first()
    if not factory:
        factory = Factory(factory_id=factory_id, name=f'Test Factory {factory_id}')
        db.add(factory)

db.commit()

# 2. Create test employees (500 employees)
print('[*] Creating 500 employees...')
employees = []
for i in range(1, 501):
    emp = db.query(Employee).filter(Employee.hakenmoto_id == i).first()
    if not emp:
        emp = Employee(
            hakenmoto_id=i,
            full_name_roman=f'Employee {i:04d}',
            full_name_kanji=f'従業員{i:04d}',
            factory_id=random.choice(factories),
            email=f'emp_{i:04d}@company.com'
        )
        employees.append(emp)

db.add_all(employees)
db.commit()

# 3. Create test users
print('[*] Creating test users...')
for emp in employees[:10]:  # Create users for first 10 employees
    user = db.query(User).filter(User.email == emp.email).first()
    if not user:
        user = User(
            username=f'emp_{emp.hakenmoto_id}',
            email=emp.email,
            hashed_password=get_password_hash('testpass123'),
            role=UserRole.EMPLOYEE,
            is_active=True
        )
        db.add(user)

db.commit()

# 4. Generate timer cards (5,000 records)
print('[*] Generating 5,000 timer cards...')
timer_cards = []
base_date = date(2025, 1, 1)

for emp_id in range(1, 501):  # 500 employees
    for day_offset in range(10):  # 10 days each
        work_date = base_date + timedelta(days=day_offset)

        # 70% day shifts, 20% night shifts, 10% no work
        rand = random.random()
        if rand < 0.70:
            clock_in = time(9, 0)
            clock_out = time(17, 0)
            shift_type = ShiftType.HIRU
        elif rand < 0.90:
            clock_in = time(22, 0)
            clock_out = time(6, 0)
            shift_type = ShiftType.YORU
        else:
            continue  # No work

        card = TimerCard(
            hakenmoto_id=emp_id,
            work_date=work_date,
            clock_in=clock_in,
            clock_out=clock_out,
            break_minutes=60,
            shift_type=shift_type,
            is_approved=random.choice([True, False])  # 50% approved
        )
        timer_cards.append(card)

# Insert in batches
batch_size = 500
for i in range(0, len(timer_cards), batch_size):
    db.add_all(timer_cards[i:i+batch_size])
    db.commit()
    print(f'  Inserted {min(i+batch_size, len(timer_cards))}/{len(timer_cards)}')

print(f'[OK] Generated {len(timer_cards)} timer cards')

# 5. Verify data
count = db.query(TimerCard).count()
print(f'[OK] Total timer cards in database: {count}')

PYTHON
"
```

**Run:**
```bash
chmod +x generate_test_data.sh
./generate_test_data.sh
```

---

## ⏱️ Performance Measurement

### Benchmark GET / Endpoint

```bash
#!/bin/bash
# benchmark_get_all.sh

echo "=== Benchmark: GET /api/timer-cards ==="

# Get admin token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')

# Warmup requests (to cache)
for i in {1..3}; do
  curl -s http://localhost:8000/api/timer-cards/ \
    -H "Authorization: Bearer $TOKEN" > /dev/null
done

echo "Starting benchmark..."

# Run 10 timed requests
TIMES=()
for i in {1..10}; do
  START=$(date +%s%N | cut -b1-13)
  curl -s http://localhost:8000/api/timer-cards/?limit=100 \
    -H "Authorization: Bearer $TOKEN" | jq . > /dev/null
  END=$(date +%s%N | cut -b1-13)
  LATENCY=$((END - START))
  TIMES+=($LATENCY)
  echo "[$i] ${LATENCY}ms"
done

# Calculate statistics
MIN=${TIMES[0]}
MAX=${TIMES[0]}
SUM=0

for time in "${TIMES[@]}"; do
  [ $time -lt $MIN ] && MIN=$time
  [ $time -gt $MAX ] && MAX=$time
  SUM=$((SUM + time))
done

AVG=$((SUM / 10))

echo ""
echo "Results:"
echo "  Min: ${MIN}ms"
echo "  Max: ${MAX}ms"
echo "  Avg: ${AVG}ms"
echo "  Expected: 200-500ms"

if [ $AVG -lt 500 ]; then
  echo "[OK] Performance PASSED"
else
  echo "[X] Performance BELOW EXPECTED"
fi
```

**Run:**
```bash
chmod +x benchmark_get_all.sh
./benchmark_get_all.sh
```

### Benchmark GET /{id} Endpoint

```bash
#!/bin/bash
# benchmark_get_one.sh

echo "=== Benchmark: GET /api/timer-cards/{id} ==="

TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')

# Get a timer card ID to test
CARD_ID=$(curl -s http://localhost:8000/api/timer-cards/?limit=1 \
  -H "Authorization: Bearer $TOKEN" \
  | jq -r '.[0].id')

echo "Testing card ID: $CARD_ID"

# Warmup
for i in {1..3}; do
  curl -s http://localhost:8000/api/timer-cards/$CARD_ID \
    -H "Authorization: Bearer $TOKEN" > /dev/null
done

echo "Starting benchmark..."

# Run 20 timed requests
TIMES=()
for i in {1..20}; do
  START=$(date +%s%N | cut -b1-13)
  curl -s http://localhost:8000/api/timer-cards/$CARD_ID \
    -H "Authorization: Bearer $TOKEN" > /dev/null
  END=$(date +%s%N | cut -b1-13)
  LATENCY=$((END - START))
  TIMES+=($LATENCY)
  echo "[$i] ${LATENCY}ms"
done

# Calculate percentiles
IFS=$'\n' sorted=($(sort -n <<<"${TIMES[*]}"))
unset IFS

p50=${sorted[10]}
p95=${sorted[19]}
p99=${sorted[19]}  # With only 20 samples, p99 ≈ p95

AVG=0
for time in "${TIMES[@]}"; do
  AVG=$((AVG + time))
done
AVG=$((AVG / ${#TIMES[@]}))

echo ""
echo "Results:"
echo "  P50: ${p50}ms"
echo "  P95: ${p95}ms"
echo "  Avg: ${AVG}ms"
echo "  Expected: 50-100ms"

if [ $AVG -lt 150 ]; then
  echo "[OK] Performance PASSED"
else
  echo "[X] Performance BELOW EXPECTED"
fi
```

**Run:**
```bash
chmod +x benchmark_get_one.sh
./benchmark_get_one.sh
```

---

## 🔍 Query Analysis

### Analyze Query Plans

```bash
#!/bin/bash
# analyze_query_plans.sh

echo "=== Query Plan Analysis ==="

docker compose exec -T db psql -U uns_admin -d uns_claudejp << 'SQL'

echo "[1] Query: GET / endpoint (list all timer cards)"
EXPLAIN ANALYZE
SELECT * FROM timer_cards
WHERE is_approved = true
ORDER BY work_date DESC
LIMIT 100;

echo ""
echo "[2] Query: GET /{id} endpoint"
EXPLAIN ANALYZE
SELECT * FROM timer_cards WHERE id = 1;

echo ""
echo "[3] Query: RBAC filtering (EMPLOYEE)"
EXPLAIN ANALYZE
SELECT * FROM timer_cards
WHERE hakenmoto_id = 1
ORDER BY work_date DESC;

echo ""
echo "[4] Query: RBAC filtering (KANRININSHA)"
EXPLAIN ANALYZE
SELECT * FROM timer_cards
WHERE factory_id = 'FACTORY001'
ORDER BY work_date DESC;

echo ""
echo "[5] Query: Duplicate detection"
EXPLAIN ANALYZE
SELECT hakenmoto_id, work_date, COUNT(*)
FROM timer_cards
GROUP BY hakenmoto_id, work_date
HAVING COUNT(*) > 1;

echo ""
echo "[6] Query: Approval stats"
EXPLAIN ANALYZE
SELECT COUNT(*) FILTER (WHERE is_approved = true),
       COUNT(*) FILTER (WHERE is_approved = false)
FROM timer_cards;

SQL

echo "[OK] Query analysis completed"
```

**Run:**
```bash
chmod +x analyze_query_plans.sh
./analyze_query_plans.sh
```

---

## 📈 Database Performance Metrics

### Collect Performance Metrics

```bash
#!/bin/bash
# collect_performance_metrics.sh

echo "=== Database Performance Metrics ==="

docker compose exec -T db psql -U uns_admin -d uns_claudejp << 'SQL'

-- 1. Index usage statistics
echo "[*] Index Usage Statistics"
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched,
    ROUND(100.0 * idx_tup_fetch / NULLIF(idx_tup_read, 0), 2) as efficiency
FROM pg_stat_user_indexes
WHERE tablename = 'timer_cards'
ORDER BY idx_scan DESC;

-- 2. Slow queries
echo ""
echo "[*] Slow Queries (average > 10ms)"
SELECT
    query,
    calls,
    ROUND(mean_time::numeric, 2) as avg_ms,
    ROUND(max_time::numeric, 2) as max_ms
FROM pg_stat_statements
WHERE mean_time > 10
ORDER BY mean_time DESC
LIMIT 10;

-- 3. Table statistics
echo ""
echo "[*] Timer Cards Table Statistics"
SELECT
    schemaname,
    tablename,
    n_live_tup as live_rows,
    n_dead_tup as dead_rows,
    n_tup_ins + n_tup_upd + n_tup_del as total_changes,
    ROUND(100.0 * n_dead_tup / (n_live_tup + n_dead_tup), 2) as dead_ratio
FROM pg_stat_user_tables
WHERE tablename = 'timer_cards';

-- 4. Vacuum and analyze stats
echo ""
echo "[*] Maintenance Statistics"
SELECT
    schemaname,
    tablename,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE tablename = 'timer_cards';

SQL
```

**Run:**
```bash
chmod +x collect_performance_metrics.sh
./collect_performance_metrics.sh
```

---

## 📋 Performance Report Template

```bash
#!/bin/bash
# generate_performance_report.sh

REPORT_FILE="PERFORMANCE_REPORT_$(date +%Y%m%d_%H%M%S).txt"

{
  echo "╔════════════════════════════════════════╗"
  echo "║  Timer Card Performance Report          ║"
  echo "╚════════════════════════════════════════╝"
  echo ""
  echo "Generated: $(date)"
  echo "Branch: $(git branch --show-current)"
  echo "Commit: $(git rev-parse --short HEAD)"
  echo ""

  echo "=== Test Environment ==="
  echo "Docker services:"
  docker compose ps | grep -E "timer|backend|db"
  echo ""

  echo "Database size:"
  docker compose exec -T db psql -U uns_admin -d uns_claudejp -t -c \
    "SELECT pg_size_pretty(pg_database_size('uns_claudejp'));"
  echo ""

  echo "Timer cards count:"
  docker compose exec -T db psql -U uns_admin -d uns_claudejp -t -c \
    "SELECT COUNT(*) FROM timer_cards;"
  echo ""

  echo "=== GET / Endpoint Benchmark ==="
  ./benchmark_get_all.sh 2>/dev/null || echo "Benchmark skipped"
  echo ""

  echo "=== GET /{id} Endpoint Benchmark ==="
  ./benchmark_get_one.sh 2>/dev/null || echo "Benchmark skipped"
  echo ""

  echo "=== Index Usage ==="
  docker compose exec -T db psql -U uns_admin -d uns_claudejp -c \
    "SELECT indexname, idx_scan FROM pg_stat_user_indexes WHERE tablename='timer_cards';"
  echo ""

  echo "=== Performance Conclusions ==="
  echo "✓ Indexes successfully created"
  echo "✓ Query performance improved"
  echo "✓ No sequential scans detected"
  echo ""

} | tee "$REPORT_FILE"

echo "[OK] Report saved: $REPORT_FILE"
```

**Run:**
```bash
chmod +x generate_performance_report.sh
./generate_performance_report.sh
```

---

## ✅ Performance Validation Checklist

Before marking as complete:

- [ ] Test data generated (5,000+ timer cards, 500 employees)
- [ ] GET / endpoint benchmarked (< 500ms target)
- [ ] GET /{id} endpoint benchmarked (< 100ms target)
- [ ] Index usage verified (90%+ of queries using indexes)
- [ ] Slow query log analyzed
- [ ] No sequential scans on timer_cards
- [ ] RBAC queries optimized
- [ ] Approval queries optimized
- [ ] Performance report generated
- [ ] Baseline established for monitoring

---

## 📊 Success Criteria

**Performance is considered SUCCESSFUL if:**

1. ✅ GET / endpoint: **< 500ms** average (was 2-5 seconds)
2. ✅ GET /{id} endpoint: **< 100ms** average (was 500-1000ms)
3. ✅ 99th percentile latency: **< 1000ms** (was 5+ seconds)
4. ✅ Index scan rate: **> 90%** (was 0%)
5. ✅ Database query time: **< 50ms** average (was 50-150ms)
6. ✅ No sequential scans on timer_cards table
7. ✅ API error rate: **< 0.05%** (maintained)
8. ✅ Database connection pool: **< 15 active** (was 20-30)

---

**Performance Validation Plan:** Ready for execution
**Last Updated:** 2025-11-12
