# 🌱 Salary System Seed Data - Summary

**Created:** 2025-11-12
**Version:** 1.0
**Status:** ✅ Ready for Testing

---

## 📋 What Was Created

### 1. Main Seed Script
**File:** `/backend/scripts/seed_salary_data.py` (500+ lines)

Comprehensive seed script that creates realistic test data for the entire salary system:

- ✅ **5 Employees** with diverse profiles
- ✅ **2 Factories** (Toyota Nagoya, Honda Suzuka)
- ✅ **5 Apartments** with varying rents
- ✅ **100 Timer Cards** (October 2025, 20 days × 5 employees)
- ✅ **5 Salary Calculations** for October 2025
- ✅ **PayrollSettings** with Japanese labor law rates
- ✅ **1 PayrollRun** in draft status
- ✅ **5 EmployeePayroll** records

### 2. Verification Script
**File:** `/backend/scripts/verify_salary_seed.py`

Validates that all seed data was created correctly:

- ✅ Counts all records created
- ✅ Displays detailed summary
- ✅ Validates expected counts
- ✅ Shows total payroll amounts
- ✅ Returns exit code 0 on success

### 3. Windows Batch Script
**File:** `/scripts/SEED_SALARY_DATA.bat`

User-friendly Windows script for one-click seeding:

- ✅ Checks Docker is running
- ✅ Verifies backend container exists
- ✅ Asks for confirmation before seeding
- ✅ Runs seed script
- ✅ Runs verification script
- ✅ Provides Adminer access instructions

### 4. Documentation
**File:** `/backend/scripts/SEED_SALARY_README.md`

Complete documentation covering:

- ✅ Overview of what gets created
- ✅ Detailed employee profiles table
- ✅ Timer card patterns explanation
- ✅ Salary components breakdown
- ✅ Factory and apartment details
- ✅ PayrollSettings rates
- ✅ Usage instructions (Docker, local, custom DB)
- ✅ Expected output
- ✅ Troubleshooting guide
- ✅ Integration testing guide

---

## 🚀 How to Use

### Quick Start (Windows)

```batch
cd scripts
SEED_SALARY_DATA.bat
```

### Manual Execution (Docker)

```bash
# Seed data
docker exec uns-claudejp-backend python backend/scripts/seed_salary_data.py

# Verify
docker exec uns-claudejp-backend python backend/scripts/verify_salary_seed.py
```

### Local Development

```bash
cd /home/user/UNS-ClaudeJP-5.4.1
python backend/scripts/seed_salary_data.py
python backend/scripts/verify_salary_seed.py
```

---

## 📊 Data Created

### Employees (5)

| ID | Name | Rate | Factory | Position | Nationality |
|----|------|------|---------|----------|-------------|
| 1001 | 田中太郎 | ¥1,000/h | Toyota Nagoya | 組立作業員 | 日本 |
| 1002 | 佐藤花子 | ¥1,100/h | Toyota Nagoya | 検査員 | 日本 |
| 1003 | 鈴木次郎 | ¥950/h | Honda Suzuka | プレス作業員 | ベトナム |
| 1004 | 山田美咲 | ¥1,150/h | Honda Suzuka | ライン管理者 | 日本 |
| 1005 | 石川拓也 | ¥1,050/h | Toyota Nagoya | 溶接工 | フィリピン |

### Timer Cards (100)

**October 2025** - 20 working days per employee:
- Regular 8-hour days (8:30-17:30)
- Overtime days with 3 extra hours
- Night shifts (22:00-07:00)
- All approved for immediate calculation

### Salary Calculations (5)

**Estimated totals for October 2025:**
- **Gross Payroll:** ¥918,750
- **Deductions:** ¥150,000
- **Net Payroll:** ¥768,750
- **Company Profit:** ¥481,250

### Factories (2)

**Toyota Nagoya** (TOYOTA__NAGOYA):
- Location: 愛知県名古屋市港区大江町1-1
- Overtime bonus: ¥5,000
- Attendance bonus: ¥10,000

**Honda Suzuka** (HONDA__SUZUKA):
- Location: 三重県鈴鹿市平田町1907
- Overtime bonus: ¥4,000
- Attendance bonus: ¥8,000

### Apartments (5)

| Code | Name | Type | Rent | Location |
|------|------|------|------|----------|
| APT001 | さくら荘 | 1K | ¥30,000 | 名古屋市熱田区 |
| APT002 | グリーンハイツ | 1DK | ¥35,000 | 名古屋市港区 |
| APT003 | サンシャイン | 1LDK | ¥40,000 | 四日市市 |
| APT004 | コーポ山田 | 1K | ¥25,000 | 名古屋市南区 |
| APT005 | ライオンズマンション | 2DK | ¥50,000 | 鈴鹿市 |

### PayrollSettings

Configured with Japanese labor law standards:

| Setting | Value | Description |
|---------|-------|-------------|
| Overtime Rate | 1.25 | 125% premium |
| Night Shift Rate | 1.25 | 125% premium |
| Holiday Rate | 1.35 | 135% premium |
| Sunday Rate | 1.35 | 135% premium |
| Standard Hours | 160/month | Base hours |
| Income Tax | 10% | Tax rate |
| Resident Tax | 5% | Local tax |
| Health Insurance | 4.75% | Insurance |
| Pension | 10% | Pension |
| Employment Insurance | 0.3% | Insurance |

---

## ✅ What You Can Test Now

### API Endpoints

#### Salary Endpoints
```bash
# List all salaries
GET http://localhost:8000/api/salary/

# Get salary details
GET http://localhost:8000/api/salary/{id}

# Calculate salary for employee
POST http://localhost:8000/api/salary/calculate
```

#### Payroll Endpoints
```bash
# List payroll runs
GET http://localhost:8000/api/payroll/

# Get payroll run details
GET http://localhost:8000/api/payroll/{id}

# Export to Excel
GET http://localhost:8000/api/payroll/export/excel?month=10&year=2025

# Export PDF payslip
GET http://localhost:8000/api/payroll/export/pdf/{employee_id}?month=10&year=2025
```

### Frontend Pages

- **Salary List:** http://localhost:3000/salary
- **Salary Details:** http://localhost:3000/salary/{id}
- **Payroll:** http://localhost:3000/payroll
- **Reports:** http://localhost:3000/reports/salary

### Database Queries (Adminer)

Access Adminer at http://localhost:8080:

```sql
-- View all seeded employees
SELECT * FROM employees WHERE hakenmoto_id >= 1001;

-- View timer cards
SELECT e.full_name_kanji, tc.work_date, tc.shift_type,
       tc.regular_hours, tc.overtime_hours, tc.night_hours
FROM timer_cards tc
JOIN employees e ON tc.hakenmoto_id = e.hakenmoto_id
WHERE e.hakenmoto_id >= 1001
ORDER BY e.hakenmoto_id, tc.work_date;

-- View salary calculations
SELECT e.full_name_kanji, sc.month, sc.year,
       sc.total_regular_hours, sc.total_overtime_hours,
       sc.gross_salary, sc.net_salary, sc.company_profit
FROM salary_calculations sc
JOIN employees e ON sc.employee_id = e.id
WHERE e.hakenmoto_id >= 1001;

-- View payroll run
SELECT * FROM payroll_runs ORDER BY created_at DESC LIMIT 1;

-- View employee payroll
SELECT ep.employee_id, ep.regular_hours, ep.overtime_hours,
       ep.gross_amount, ep.net_amount
FROM employee_payroll ep
ORDER BY ep.employee_id;
```

---

## 🔧 Troubleshooting

### "relation does not exist"

**Cause:** Database migrations not applied
**Solution:**
```bash
docker exec uns-claudejp-backend alembic upgrade head
```

### "database connection failed"

**Cause:** Database not running
**Solution:**
```bash
docker compose ps db
docker compose up -d db
```

### "duplicate key value"

**Cause:** Previous seed data not cleared
**Solution:**
```bash
# The script auto-clears, but if it fails, manually delete:
docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "
DELETE FROM employee_payroll;
DELETE FROM payroll_runs;
DELETE FROM salary_calculations;
DELETE FROM timer_cards;
DELETE FROM employees WHERE hakenmoto_id >= 1001;
"
```

### Script fails silently

**Cause:** Python errors
**Solution:**
```bash
# Check Python syntax
python -m py_compile backend/scripts/seed_salary_data.py

# Run with verbose errors
docker exec -it uns-claudejp-backend python -u backend/scripts/seed_salary_data.py
```

---

## 📁 File Structure

```
UNS-ClaudeJP-5.4.1/
├── backend/
│   └── scripts/
│       ├── seed_salary_data.py          # Main seed script
│       ├── verify_salary_seed.py        # Verification script
│       └── SEED_SALARY_README.md        # Detailed documentation
│
├── scripts/
│   └── SEED_SALARY_DATA.bat             # Windows batch script
│
└── SALARY_SEED_SUMMARY.md               # This file
```

---

## 🎯 Next Steps

### For Development

1. **Run the seed script** to create test data
2. **Verify** the data was created correctly
3. **Test API endpoints** with Swagger UI
4. **Test frontend pages** with the UI
5. **Run unit tests** against the seed data

### For Testing

1. **Salary Calculations**
   - Verify overtime calculations (125%)
   - Verify night shift calculations (125%)
   - Verify holiday calculations (135%)
   - Verify bonuses and allowances

2. **Payroll Processing**
   - Create payroll runs
   - Generate payslips
   - Export to Excel
   - Export to PDF

3. **Reports**
   - Monthly salary reports
   - Employee salary details
   - Factory-wise summaries
   - Profit margin analysis

### For Production

1. **DO NOT** run this seed script in production
2. **USE** proper employee import from Excel
3. **CONFIGURE** PayrollSettings through admin UI
4. **REVIEW** all calculations before marking as paid

---

## 📚 Related Documentation

- **Main README:** `/README.md`
- **CLAUDE.md:** `/CLAUDE.md` (development guide)
- **Seed README:** `/backend/scripts/SEED_SALARY_README.md`
- **API Docs:** http://localhost:8000/api/docs
- **Architecture:** `/docs/architecture/`

---

## 🔐 Security Notes

- **Test data only** - NOT for production use
- **Hakenmoto IDs** start at 1001 to avoid conflicts
- **Factory IDs** use test prefixes (TOYOTA__, HONDA__)
- **Apartment codes** use APT prefix
- **All data** can be safely deleted without affecting production

---

## ✅ Validation Checklist

After running the seed script, verify:

- [ ] 2 factories created (TOYOTA__NAGOYA, HONDA__SUZUKA)
- [ ] 5 apartments created (APT001-APT005)
- [ ] 5 employees created (1001-1005)
- [ ] 100 timer cards created (20 per employee)
- [ ] 5 salary calculations created
- [ ] 1 payroll run created
- [ ] 5 employee payroll records created
- [ ] PayrollSettings configured
- [ ] All timer cards approved
- [ ] Gross payroll ≈ ¥918,750
- [ ] Net payroll ≈ ¥768,750
- [ ] Company profit ≈ ¥481,250

---

## 📞 Support

If you encounter issues:

1. **Check logs:** `docker compose logs backend`
2. **Verify database:** `docker compose ps db`
3. **Check migrations:** `docker exec uns-claudejp-backend alembic current`
4. **Review documentation:** See links above
5. **Run verification:** `python backend/scripts/verify_salary_seed.py`

---

**Created by:** Claude Code
**Date:** 2025-11-12
**Version:** UNS-ClaudeJP 5.4.1
**License:** Part of UNS-ClaudeJP HR Management System
