# ⚡ QUICK TEST REFERENCE

## 🚀 Run All Tests (Automated)

```bash
# Option 1: Run automated test script
cd /home/user/UNS-ClaudeJP-5.4.1
./RUN_THESE_TESTS_IN_DOCKER.sh
```

---

## 🎯 Run Individual Tests

### Critical Edge Cases (22 tests)
```bash
docker exec uns-claudejp-backend pytest backend/tests/test_timer_card_edge_cases.py -v
```

### All Timer Card Tests (62 tests)
```bash
docker exec uns-claudejp-backend pytest backend/tests/test_timer_card*.py -v
```

### Specific Test Function
```bash
docker exec uns-claudejp-backend pytest backend/tests/test_timer_card_edge_cases.py::TestDuplicateRecords::test_duplicate_employee_same_day_rejected -v
```

---

## 🔍 Quick Checks

### 1. Docker Status
```bash
docker compose ps
```

### 2. Alembic Status
```bash
docker exec uns-claudejp-backend alembic current
```

### 3. Database Constraints
```bash
docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "\d+ timer_cards"
```

### 4. API Health
```bash
curl http://localhost:8000/api/health | jq .
```

---

## 📊 Test Categories

| Test File | Tests | Focus |
|-----------|-------|-------|
| `test_timer_card_edge_cases.py` | 22 | **CRITICAL** - Constraints, validation |
| `test_timer_card_parsers.py` | 10 | OCR parsing logic |
| `test_timer_card_ocr_simple.py` | 8 | Simple OCR formats |
| `test_timer_card_ocr.py` | 11 | Advanced OCR |
| `test_timer_card_ocr_integration.py` | 3 | Database integration |
| `test_timer_cards_api.py` | 4 | API endpoints |
| `test_timer_card_stress.py` | 2 | Performance |
| `test_timer_card_end_to_end.py` | 2 | Complete workflows |

---

## ✅ Expected Results

All tests should **PASS**. If any test fails:

1. Check error message
2. Review constraint name (e.g., `ck_timer_cards_*`)
3. Verify database migration applied
4. Check test data fixtures

---

## 🐛 Common Issues

### Issue: Tests fail with "No module named 'pytest'"
**Solution:** Tests must run inside Docker container
```bash
docker exec uns-claudejp-backend pytest ...
```

### Issue: IntegrityError in tests
**Solution:** This is expected for negative tests! Check test name contains "rejected" or "fails"

### Issue: Alembic migration not applied
**Solution:** Run migrations
```bash
docker exec uns-claudejp-backend alembic upgrade head
```

---

## 📝 Verification Checklist

Before merging, verify:

- [ ] All 62 pytest tests pass
- [ ] Database has 9 indexes on timer_cards
- [ ] Database has 7 constraints on timer_cards
- [ ] API returns 401 for unauthorized access
- [ ] Alembic shows correct migration (2025_11_12_2000)
- [ ] No syntax errors in Python files
- [ ] Manual QA testing completed

---

## 🎉 Success Criteria

```
✅ 62/62 tests PASSED
✅ 7 constraints verified
✅ 9 indexes verified
✅ API endpoints responding
✅ Alembic up to date
```

**Result:** READY TO MERGE! 🚀

---

**See also:**
- `TEST_VALIDATION_REPORT.md` - Detailed analysis
- `RUN_THESE_TESTS_IN_DOCKER.sh` - Automated test script
