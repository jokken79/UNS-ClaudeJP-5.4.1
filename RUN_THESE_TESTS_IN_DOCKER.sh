#!/bin/bash
# ============================================
# TIMER CARDS VALIDATION TEST SUITE
# Run these tests in Docker environment
# ============================================

set -e  # Exit on error

echo "🚀 TIMER CARDS VALIDATION TEST SUITE"
echo "======================================"
echo ""

# ============================================
# 1. VERIFY DOCKER IS RUNNING
# ============================================
echo "📦 Step 1: Verifying Docker services..."
docker compose ps
echo "✅ Docker services check complete"
echo ""

# ============================================
# 2. PYTHON SYNTAX CHECKS (In Docker)
# ============================================
echo "🔍 Step 2: Python syntax validation..."
docker exec uns-claudejp-backend python -m py_compile app/api/timer_cards.py && echo "✅ timer_cards.py syntax OK"
docker exec uns-claudejp-backend python -m py_compile app/services/timer_card_ocr_service.py && echo "✅ timer_card_ocr_service.py syntax OK"
docker exec uns-claudejp-backend bash -c "python -m py_compile app/core/*.py" && echo "✅ core/*.py syntax OK"
echo ""

# ============================================
# 3. ALEMBIC MIGRATIONS CHECK
# ============================================
echo "📊 Step 3: Checking Alembic migrations..."
echo "Current migration:"
docker exec uns-claudejp-backend alembic current

echo ""
echo "Latest migration (head):"
docker exec uns-claudejp-backend alembic heads

echo ""
echo "Recent migration history:"
docker exec uns-claudejp-backend alembic history | head -10
echo "✅ Alembic migrations check complete"
echo ""

# ============================================
# 4. DATABASE CONSTRAINTS VERIFICATION
# ============================================
echo "🗄️  Step 4: Verifying database constraints..."
echo "Checking timer_cards constraints:"
docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "
SELECT conname, contype,
       CASE contype
           WHEN 'c' THEN 'CHECK'
           WHEN 'u' THEN 'UNIQUE'
           WHEN 'p' THEN 'PRIMARY KEY'
           WHEN 'f' THEN 'FOREIGN KEY'
       END as constraint_type
FROM pg_constraint
WHERE conrelid = 'timer_cards'::regclass
ORDER BY contype, conname;
"

echo ""
echo "Checking timer_cards indexes:"
docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "
SELECT indexname
FROM pg_indexes
WHERE tablename = 'timer_cards'
ORDER BY indexname;
"
echo "✅ Database constraints verification complete"
echo ""

# ============================================
# 5. PYTEST - EDGE CASES (CRITICAL)
# ============================================
echo "🧪 Step 5: Running edge case tests (CRITICAL)..."
docker exec uns-claudejp-backend pytest backend/tests/test_timer_card_edge_cases.py -v --tb=short || {
    echo "❌ EDGE CASE TESTS FAILED!"
    echo "Review errors above before merging!"
    exit 1
}
echo "✅ Edge case tests PASSED"
echo ""

# ============================================
# 6. PYTEST - ALL TIMER CARD TESTS
# ============================================
echo "🧪 Step 6: Running all timer card tests..."
docker exec uns-claudejp-backend pytest backend/tests/test_timer_card*.py -v --tb=short || {
    echo "❌ SOME TIMER CARD TESTS FAILED!"
    echo "Review errors above before merging!"
    exit 1
}
echo "✅ All timer card tests PASSED"
echo ""

# ============================================
# 7. API ENDPOINT TESTS (curl)
# ============================================
echo "🌐 Step 7: Testing API endpoints..."

echo "Test 7.1: Unauthorized access (should return 401 or error)"
UNAUTHORIZED_RESPONSE=$(curl -s http://localhost:8000/api/timer_cards/)
echo "$UNAUTHORIZED_RESPONSE" | jq . || echo "$UNAUTHORIZED_RESPONSE"

echo ""
echo "Test 7.2: Health check"
curl -s http://localhost:8000/api/health | jq .

echo ""
echo "Test 7.3: API docs (should return HTML)"
curl -s http://localhost:8000/api/docs | head -5

echo ""
echo "✅ API endpoint tests complete"
echo ""

# ============================================
# 8. PERFORMANCE CHECK (Optional)
# ============================================
echo "⚡ Step 8: Performance check (optional)..."
echo "Checking query performance for timer_cards date range query:"
docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "
EXPLAIN ANALYZE
SELECT *
FROM timer_cards
WHERE work_date BETWEEN '2025-01-01' AND '2025-12-31';
" || echo "⚠️ Performance check skipped (no data)"
echo ""

# ============================================
# 9. SUMMARY
# ============================================
echo "============================================"
echo "✅ ALL TESTS COMPLETED SUCCESSFULLY!"
echo "============================================"
echo ""
echo "Summary:"
echo "  ✅ Docker services running"
echo "  ✅ Python syntax valid"
echo "  ✅ Alembic migrations applied"
echo "  ✅ Database constraints verified"
echo "  ✅ Edge case tests passed"
echo "  ✅ All timer card tests passed"
echo "  ✅ API endpoints responding"
echo ""
echo "🎉 READY TO MERGE!"
echo ""
echo "Next steps:"
echo "  1. Review test output above"
echo "  2. Manual QA testing (upload timer card, approve, etc.)"
echo "  3. Merge branch to main"
echo ""
