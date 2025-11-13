# 🚀 Salary Seed - Quick Reference

**One-page guide for seeding salary test data**

---

## ⚡ Quick Commands

### Windows (One-Click)

```batch
cd scripts
SEED_SALARY_DATA.bat
```

### Docker

```bash
# Seed
docker exec uns-claudejp-backend python backend/scripts/seed_salary_data.py

# Verify
docker exec uns-claudejp-backend python backend/scripts/verify_salary_seed.py
```

### Local

```bash
python backend/scripts/seed_salary_data.py
python backend/scripts/verify_salary_seed.py
```

---

## 📊 What Gets Created

| Resource | Count | Details |
|----------|-------|---------|
| **Employees** | 5 | IDs: 1001-1005, Rates: ¥950-¥1,150/h |
| **Factories** | 2 | Toyota Nagoya, Honda Suzuka |
| **Apartments** | 5 | Rents: ¥25k-¥50k/month |
| **Timer Cards** | 100 | October 2025, 20 days × 5 employees |
| **Salaries** | 5 | October 2025, Total: ¥918,750 gross |
| **Payroll Run** | 1 | Draft status, ¥768,750 net |
| **Settings** | 1 | Japanese labor law rates |

---

## 🎯 Test Endpoints

### Swagger UI
```
http://localhost:8000/api/docs
```

### Salary
```bash
GET  /api/salary/                      # List all
GET  /api/salary/{id}                  # Details
POST /api/salary/calculate             # Calculate
GET  /api/salary/employee/{id}         # By employee
```

### Payroll
```bash
GET  /api/payroll/                     # List runs
GET  /api/payroll/{id}                 # Run details
POST /api/payroll/run                  # Create run
GET  /api/payroll/export/excel         # Excel export
GET  /api/payroll/export/pdf/{emp_id}  # PDF payslip
```

---

## 🔍 Database Queries

### Adminer
```
http://localhost:8080
Server: db
User: uns_admin
Password: uns_password
Database: uns_claudejp
```

### Quick Queries

```sql
-- Seeded employees
SELECT * FROM employees WHERE hakenmoto_id >= 1001;

-- Timer cards summary
SELECT
  e.full_name_kanji,
  COUNT(*) as days,
  SUM(tc.regular_hours) as regular_h,
  SUM(tc.overtime_hours) as ot_h,
  SUM(tc.night_hours) as night_h
FROM timer_cards tc
JOIN employees e ON tc.hakenmoto_id = e.hakenmoto_id
WHERE e.hakenmoto_id >= 1001
GROUP BY e.full_name_kanji;

-- Salary summary
SELECT
  e.full_name_kanji,
  sc.gross_salary,
  sc.net_salary,
  sc.company_profit
FROM salary_calculations sc
JOIN employees e ON sc.employee_id = e.id
WHERE e.hakenmoto_id >= 1001;

-- Payroll run
SELECT * FROM payroll_runs ORDER BY created_at DESC LIMIT 1;
```

---

## 🛠️ Troubleshooting

### Migrations Not Applied
```bash
docker exec uns-claudejp-backend alembic upgrade head
```

### Database Not Running
```bash
docker compose up -d db
docker compose logs db
```

### Clear Old Data
```bash
docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "
DELETE FROM employee_payroll;
DELETE FROM payroll_runs;
DELETE FROM salary_calculations;
DELETE FROM timer_cards;
DELETE FROM employees WHERE hakenmoto_id >= 1001;
"
```

### Check Syntax
```bash
python -m py_compile backend/scripts/seed_salary_data.py
```

---

## 📁 Files

```
backend/scripts/
├── seed_salary_data.py          # Main seed (821 lines)
├── verify_salary_seed.py        # Verification (222 lines)
└── SEED_SALARY_README.md        # Full docs

scripts/
└── SEED_SALARY_DATA.bat         # Windows batch

docs/
├── SALARY_SEED_SUMMARY.md       # This summary
└── SALARY_SEED_QUICKREF.md      # This file
```

---

## ✅ Validation

Expected results from verify script:

- Factories: **2**
- Apartments: **5**
- Employees: **5**
- Timer Cards: **100**
- Salary Calcs: **5**
- Payroll Runs: **1**
- Gross: **¥918,750**
- Net: **¥768,750**
- Profit: **¥481,250**

---

## 🚨 Important Notes

- ⚠️ **Test data only** - NOT for production
- ✅ **Safe to run multiple times** - Auto-clears old data
- 🔒 **Production data protected** - Only deletes hakenmoto_id >= 1001
- 📅 **October 2025** - All data is for this month
- 🇯🇵 **Japanese labor law** - Rates: OT=125%, Night=125%, Holiday=135%

---

## 📞 Need Help?

1. **Full docs:** `/backend/scripts/SEED_SALARY_README.md`
2. **Summary:** `/SALARY_SEED_SUMMARY.md`
3. **Logs:** `docker compose logs backend`
4. **Status:** `docker compose ps`

---

**Quick Start:** `cd scripts && SEED_SALARY_DATA.bat` (Windows)
**Quick Start:** `docker exec uns-claudejp-backend python backend/scripts/seed_salary_data.py` (Other)

**Created:** 2025-11-12 | **Version:** 1.0 | **UNS-ClaudeJP 5.4.1**
