# 📁 Salary Seed System - File Index

**Quick reference for all salary seed files**

---

## 🎯 Main Scripts

### Seed Script
```
/backend/scripts/seed_salary_data.py
```
- **Lines:** 821
- **Purpose:** Create comprehensive salary test data
- **Creates:** 5 employees, 2 factories, 5 apartments, 100 timer cards, 5 salaries, payroll run
- **Usage:** `docker exec uns-claudejp-backend python backend/scripts/seed_salary_data.py`

### Verification Script
```
/backend/scripts/verify_salary_seed.py
```
- **Lines:** 222
- **Purpose:** Verify all seed data was created correctly
- **Validates:** Counts, totals, relationships
- **Usage:** `docker exec uns-claudejp-backend python backend/scripts/verify_salary_seed.py`

### Windows Batch Script
```
/scripts/SEED_SALARY_DATA.bat
```
- **Lines:** ~150
- **Purpose:** One-click seed execution for Windows
- **Features:** Docker checks, confirmation prompt, seed + verify
- **Usage:** `cd scripts && SEED_SALARY_DATA.bat`

---

## 📚 Documentation

### Quick Reference (1 page)
```
/SALARY_SEED_QUICKREF.md
```
- **Audience:** Developers needing quick commands
- **Contains:** Commands, endpoints, queries, troubleshooting
- **Read time:** 2-3 minutes

### Executive Summary (Complete)
```
/SALARY_SEED_SUMMARY.md
```
- **Audience:** Team leads, QA, developers
- **Contains:** Full overview, tables, testing guide, validation
- **Read time:** 10-15 minutes

### Detailed Documentation
```
/backend/scripts/SEED_SALARY_README.md
```
- **Audience:** Developers, integrators
- **Contains:** Detailed specs, usage, troubleshooting, integration guide
- **Read time:** 15-20 minutes

### File Index (This file)
```
/SALARY_SEED_INDEX.md
```
- **Audience:** Everyone
- **Contains:** File locations and quick access
- **Read time:** 2 minutes

---

## 📊 Related System Files

### Models
```
/backend/app/models/models.py
  - Employee (line 533)
  - TimerCard (line 807)
  - SalaryCalculation (line 845)
  - Factory (line 424)
  - Apartment (line 446)

/backend/app/models/payroll_models.py
  - PayrollRun (line 11)
  - EmployeePayroll (line 31)
  - PayrollSettings (line 83)
```

### Schemas
```
/backend/app/schemas/salary.py
  - SalaryBase, SalaryCreate, SalaryResponse

/backend/app/schemas/payroll.py
  - PayrollRunBase, PayrollRunResponse
  - EmployeePayrollBase, EmployeePayrollResponse
```

### Services
```
/backend/app/services/salary_service.py
  - SalaryService (unified service)

/backend/app/services/payroll_service.py
  - PayrollService
```

### API Endpoints
```
/backend/app/api/salary.py
  - GET /api/salary/
  - GET /api/salary/{id}
  - POST /api/salary/calculate
  - GET /api/salary/employee/{employee_id}

/backend/app/api/payroll.py
  - GET /api/payroll/
  - GET /api/payroll/{id}
  - POST /api/payroll/run
  - GET /api/payroll/export/excel
  - GET /api/payroll/export/pdf/{employee_id}
```

### Frontend Pages
```
/frontend/app/(dashboard)/salary/page.tsx
  - Salary list page

/frontend/app/(dashboard)/salary/[id]/page.tsx
  - Salary details page

/frontend/app/(dashboard)/payroll/page.tsx
  - Payroll management page

/frontend/app/(dashboard)/reports/salary/page.tsx
  - Salary reports page
```

---

## 🗄️ Database Tables Affected

```sql
employees              -- 5 test records (hakenmoto_id >= 1001)
factories              -- 2 test factories
apartments             -- 5 test apartments
timer_cards            -- 100 test timer cards
salary_calculations    -- 5 test salary calculations
payroll_runs           -- 1 test payroll run
employee_payroll       -- 5 test employee payroll records
payroll_settings       -- 1 settings record (shared)
```

---

## 📖 Reading Order

### For Quick Start
1. **SALARY_SEED_QUICKREF.md** - Commands and quick reference
2. Run seed script
3. Done!

### For Understanding
1. **SALARY_SEED_SUMMARY.md** - What gets created and why
2. **SEED_SALARY_README.md** - Full documentation
3. **Source code** - seed_salary_data.py

### For Integration/Testing
1. **SEED_SALARY_README.md** - Full documentation
2. **SALARY_SEED_SUMMARY.md** - Testing guide section
3. **API docs** - http://localhost:8000/api/docs

---

## 🚀 Quick Access Commands

```bash
# View quick reference
cat /home/user/UNS-ClaudeJP-5.4.1/SALARY_SEED_QUICKREF.md

# View summary
cat /home/user/UNS-ClaudeJP-5.4.1/SALARY_SEED_SUMMARY.md

# View full docs
cat /home/user/UNS-ClaudeJP-5.4.1/backend/scripts/SEED_SALARY_README.md

# Run seed
docker exec uns-claudejp-backend python backend/scripts/seed_salary_data.py

# Run verification
docker exec uns-claudejp-backend python backend/scripts/verify_salary_seed.py

# Windows one-click
cd scripts && SEED_SALARY_DATA.bat
```

---

## 📞 Support

**Primary docs:** `/backend/scripts/SEED_SALARY_README.md`
**Quick help:** `/SALARY_SEED_QUICKREF.md`
**File index:** This file

---

**Created:** 2025-11-12
**Version:** 1.0
**Part of:** UNS-ClaudeJP 5.4.1 HR Management System
