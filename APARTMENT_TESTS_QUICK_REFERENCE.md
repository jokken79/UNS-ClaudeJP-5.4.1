# 🚀 Quick Reference: Apartment Tests

## File Location
`/home/user/UNS-ClaudeJP-5.4.1/backend/tests/test_apartment_services.py`

---

## 📋 Test Index (38 tests total)

### 🏠 ApartmentService (16 tests)

#### Create/Read (6 tests)
1. `test_create_apartment_success` → ✅ Create apartment with all fields
2. `test_create_apartment_duplicate_name` → ❌ Prevent duplicate names (400)
3. `test_get_apartment_with_stats_success` → ✅ Get apartment + occupancy stats
4. `test_get_apartment_not_found` → ❌ Non-existent apartment (404)
5. `test_list_apartments_no_filters` → ✅ List all apartments
6. `test_list_apartments_with_search` → ✅ Search by text query

#### Update/Delete (4 tests)
7. `test_update_apartment_success` → ✅ Full update
8. `test_update_apartment_partial` → ✅ Partial update (only changed fields)
9. `test_delete_apartment_success` → ✅ Delete without dependencies
10. `test_delete_apartment_with_active_assignment_fails` → ❌ Cannot delete with active assignments (400)

#### Filters (2 tests)
11. `test_list_apartments_with_prefecture_filter` → ✅ Filter by prefecture (e.g., 東京都)
12. `test_list_apartments_with_rent_range` → ✅ Filter by min/max rent

#### Calculations (4 tests)
13. `test_calculate_prorated_rent_full_month` → ✅ Full month = monthly_rent
14. `test_calculate_prorated_rent_partial_month` → ✅ Prorated for partial month
15. `test_get_cleaning_fee_default` → ✅ Default cleaning fee from apartment
16. `test_get_cleaning_fee_custom` → ✅ Override with custom amount

---

### 💰 AdditionalChargeService (12 tests)

#### Create (3 tests)
17. `test_create_charge_success` → ✅ Create cleaning/repair charge
18. `test_create_charge_invalid_assignment` → ❌ Assignment must exist (404)
19. `test_create_charge_different_types` → ✅ Support cleaning, repair, damage, other

#### List/Get (4 tests)
20. `test_list_charges_no_filters` → ✅ List all charges
21. `test_list_charges_with_assignment_filter` → ✅ Filter by assignment_id
22. `test_list_charges_with_status_filter` → ✅ Filter by status (pending/approved/cancelled)
23. `test_get_charge_success` → ✅ Get charge by ID
24. `test_get_charge_not_found` → ❌ Non-existent charge (404)

#### Approve/Cancel (2 tests)
25. `test_approve_charge_success` → ✅ Approve pending charge (ADMIN only)
26. `test_cancel_charge_success` → ✅ Cancel pending charge

#### Delete (2 tests)
27. `test_delete_charge_pending_only` → ✅ Soft delete pending charge
28. `test_delete_approved_charge_fails` → ❌ Cannot delete approved charges (400)

---

### 📊 DeductionService (10 tests)

#### Retrieve (3 tests)
29. `test_get_monthly_deductions_empty` → ✅ Empty month returns []
30. `test_get_monthly_deductions_invalid_month` → ❌ Month must be 1-12 (400)
31. `test_get_monthly_deductions_invalid_year` → ❌ Year must be 2020-2030 (400)

#### Generate (3 tests)
32. `test_generate_monthly_deductions_success` → ✅ Generate deductions for all active assignments
33. `test_generate_monthly_deductions_duplicate_fails` → ❌ Cannot generate twice (409)
34. `test_generate_deductions_includes_additional_charges` → ✅ Includes approved charges in total

#### Get/Update (4 tests)
35. `test_get_deduction_success` → ✅ Get deduction by ID
36. `test_get_deduction_not_found` → ❌ Non-existent deduction (404)
37. `test_update_deduction_status_pending_to_processed` → ✅ Status transition
38. `test_update_deduction_status_processed_to_paid` → ✅ Final status transition (ADMIN only)

---

## 🏃 Running Tests

### Run All Tests
```bash
docker exec uns-claudejp-backend pytest backend/tests/test_apartment_services.py -v
```

### Run Single Test Class
```bash
# ApartmentService tests only
docker exec uns-claudejp-backend pytest backend/tests/test_apartment_services.py::TestApartmentService -v

# AdditionalChargeService tests only
docker exec uns-claudejp-backend pytest backend/tests/test_apartment_services.py::TestAdditionalChargeService -v

# DeductionService tests only
docker exec uns-claudejp-backend pytest backend/tests/test_apartment_services.py::TestDeductionService -v
```

### Run Single Test
```bash
# Run specific test by name
docker exec uns-claudejp-backend pytest backend/tests/test_apartment_services.py::TestApartmentService::test_create_apartment_success -v
```

### Run with Coverage
```bash
docker exec uns-claudejp-backend pytest backend/tests/test_apartment_services.py \
  --cov=app.services.apartment_service \
  --cov=app.services.additional_charge_service \
  --cov=app.services.deduction_service \
  --cov-report=html
```

### Debug Mode
```bash
# Show full traceback
docker exec uns-claudejp-backend pytest backend/tests/test_apartment_services.py -vvs --tb=long

# Stop on first failure
docker exec uns-claudejp-backend pytest backend/tests/test_apartment_services.py -x
```

---

## 🔍 Test Data Fixtures

### Users
- `admin_user` → Admin user (ADMIN role, username: admin_test)

### Apartments
- `sample_apartment` → テスト社宅 A-301, ¥50,000/month, 東京都千代田区
- `second_apartment` → テスト社宅 B-201, ¥60,000/month, 東京都千代田区

### Employees
- `sample_employee` → 山田太郎 (hakenmoto_id: 10001)
- `second_employee` → 田中花子 (hakenmoto_id: 10002)

### Assignments
- `active_assignment` → Active assignment for Nov 2025

---

## 📊 Expected Test Results

### ✅ All Pass Scenario
```
========== 38 passed in 12.34s ==========
```

### ❌ Common Failures

#### Database Connection Error
```
Error: postgresql://... connection refused
```
**Fix:** Ensure database service is running
```bash
docker compose ps db
docker compose logs db
```

#### Import Error
```
ImportError: cannot import name 'ApartmentService'
```
**Fix:** Verify service files exist and PYTHONPATH is set
```bash
export PYTHONPATH=/home/user/UNS-ClaudeJP-5.4.1/backend:$PYTHONPATH
```

#### Fixture Error
```
fixture 'client' not found
```
**Fix:** Ensure conftest.py is in tests/ directory

---

## 🎯 Key Assertions

### Status Codes
- `200 OK` → Successful retrieval
- `201 Created` → Successful creation
- `400 Bad Request` → Validation error, business rule violation
- `404 Not Found` → Resource doesn't exist
- `409 Conflict` → Duplicate operation

### Service Validations
- Duplicate names prevented
- Active assignments block deletion
- Only pending charges can be deleted/cancelled
- Prorated rent = (monthly_rent / days_in_month) × days_occupied
- Deduction includes base_rent + approved additional_charges

---

## 📈 Coverage Goals

| Service | Target | Current |
|---------|--------|---------|
| `apartment_service.py` | 80% | ~77% |
| `additional_charge_service.py` | 85% | ~85% |
| `deduction_service.py` | 85% | ~87% |
| **Overall** | **83%** | **~82%** ✅ |

---

## 🔧 Maintenance Checklist

When modifying apartment services:
- [ ] Add test for new service method
- [ ] Update existing tests if method signature changes
- [ ] Run full test suite before committing
- [ ] Update this reference if test count changes
- [ ] Check coverage report for untested branches

---

## 📚 Related Documentation

- **Full Report:** `/home/user/UNS-ClaudeJP-5.4.1/APARTMENT_TESTS_REPORT.md`
- **API Tests:** `/home/user/UNS-ClaudeJP-5.4.1/backend/tests/test_apartments_v2_api.py`
- **Assignment Tests:** `/home/user/UNS-ClaudeJP-5.4.1/backend/tests/test_assignment_service.py`
- **Service Code:** `/home/user/UNS-ClaudeJP-5.4.1/backend/app/services/`

---

**Last Updated:** 2025-11-12
**Test File:** `test_apartment_services.py`
**Lines of Code:** 1005
**Total Tests:** 38
