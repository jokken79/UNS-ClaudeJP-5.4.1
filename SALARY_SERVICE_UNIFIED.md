# Unified Salary Service - Implementation Summary

**Created**: 2025-11-12
**File**: `backend/app/services/salary_service.py`
**Lines**: 896
**Status**: ✅ Complete - Ready for integration

---

## 📋 Overview

This document describes the **Unified Salary Service** that consolidates and improves the salary calculation logic from:
- `backend/app/api/salary.py` (calculate_employee_salary function)
- `backend/app/services/payroll_service.py` (PayrollService class)

The new service provides a professional, type-safe, and maintainable solution for salary calculations in UNS-ClaudeJP 5.4.1.

---

## 🎯 Key Features

### 1. **Unified Architecture**
- Single `SalaryService` class that consolidates all salary logic
- Async/await throughout for FastAPI compatibility
- Dependency injection with `AsyncSession`
- Full type hints and comprehensive docstrings

### 2. **Database-Driven Configuration**
- ✅ Uses `PayrollSettings` from database (NOT hardcoded)
- ✅ Configurable rates: overtime, night shift, holiday, Sunday
- ✅ Fallback to settings.py defaults if DB config not available
- ✅ Easy to update rates without code changes

### 3. **Advanced Apartment Deductions**
- ✅ Integrates with `rent_deductions` table (V2 system)
- ✅ Supports base rent + additional charges
- ✅ Automatic prorated rent calculation based on work days
- ✅ Multiple deduction statuses (PENDING, PROCESSED)
- ✅ Fallback to `employee.apartment_rent` if no deductions found

### 4. **Comprehensive Hour Tracking**
- ✅ Regular hours (通常時間)
- ✅ Overtime hours (時間外労働)
- ✅ Night shift hours (深夜労働: 22:00-05:00)
- ✅ Holiday hours (休日労働: weekends)
- ✅ Uses pre-calculated hours from `timer_cards` table

### 5. **Complete Deduction Support**
- ✅ Apartment rent (from rent_deductions)
- ✅ Income tax (所得税)
- ✅ Resident tax (住民税)
- ✅ Health insurance (健康保険)
- ✅ Pension (年金)
- ✅ Employment insurance (雇用保険)
- ✅ Other deductions (customizable)

### 6. **Factory Integration**
- ✅ Reads factory-specific configurations
- ✅ Gasoline allowance (ガソリン手当)
- ✅ Attendance bonus (皆勤手当)
- ✅ Company profit calculation (jikyu_tanka - employee rate)

### 7. **Full Validation**
- ✅ Pre-calculation validation
- ✅ Error and warning system
- ✅ Duplicate detection (prevents recalculation)
- ✅ Data integrity checks

---

## 🏗️ Class Structure

```python
class SalaryService:
    def __init__(self, db: AsyncSession)

    # Public Methods
    async def calculate_salary(...)           # Calculate single employee
    async def calculate_bulk_salaries(...)    # Bulk calculation
    async def mark_as_paid(...)               # Mark as paid
    async def get_salary_statistics(...)      # Monthly statistics
    async def validate_salary(...)            # Pre-calculation validation

    # Private Helper Methods
    async def _get_employee(...)              # Fetch employee
    async def _get_factory(...)               # Fetch factory
    async def _get_timer_cards(...)           # Fetch timer cards
    async def _get_payroll_settings(...)      # Fetch payroll config
    async def _calculate_hours_breakdown(...) # Calculate hours
    async def _calculate_amounts(...)         # Calculate amounts
    async def _get_apartment_deductions(...)  # Get rent deductions
```

---

## 📊 Method Details

### 1. `calculate_salary()`

**Purpose**: Calculate salary for a single employee
**Returns**: `SalaryCalculationResponse`

**Process**:
1. Fetch employee data
2. Get approved timer cards for the month
3. Load payroll settings from database
4. Calculate hours breakdown (regular, overtime, night, holiday)
5. Calculate gross amounts for each hour type
6. Get apartment deductions from rent_deductions table
7. Calculate bonuses from factory config
8. Calculate gross and net salary
9. Calculate factory payment and company profit
10. Save to database (optional)

**Parameters**:
```python
employee_id: int                               # Employee ID
month: int                                     # Month (1-12)
year: int                                      # Year (e.g., 2025)
timer_records: Optional[List[TimerCard]]       # Pre-loaded timer cards
bonus: Optional[int]                           # Override bonus
gasoline_allowance: Optional[int]              # Override gasoline
other_deductions: Optional[int]                # Additional deductions
save_to_db: bool = True                        # Save to database
```

**Example**:
```python
async with get_db() as db:
    service = SalaryService(db)
    result = await service.calculate_salary(
        employee_id=123,
        month=10,
        year=2025
    )
    print(f"Gross: ¥{result.gross_salary:,}, Net: ¥{result.net_salary:,}")
```

---

### 2. `calculate_bulk_salaries()`

**Purpose**: Calculate salaries for multiple employees
**Returns**: `SalaryBulkResult`

**Process**:
1. Query employees (by IDs or factory_id)
2. Loop through each employee
3. Calculate salary for each
4. Track successes and failures
5. Aggregate totals

**Parameters**:
```python
employee_ids: Optional[List[int]]              # Employee IDs (None = all active)
month: int                                     # Month (1-12)
year: int                                      # Year
factory_id: Optional[str]                      # Filter by factory
```

**Example**:
```python
result = await service.calculate_bulk_salaries(
    employee_ids=[1, 2, 3],
    month=10,
    year=2025
)
print(f"Success: {result.successful}, Failed: {result.failed}")
print(f"Total gross: ¥{result.total_gross_salary:,}")
```

---

### 3. `mark_as_paid()`

**Purpose**: Mark salary calculations as paid
**Returns**: `Dict[str, Any]`

**Parameters**:
```python
salary_ids: List[int]                          # Salary calculation IDs
payment_date: Optional[datetime]               # Payment date (default: now)
```

**Example**:
```python
result = await service.mark_as_paid([1, 2, 3])
print(result['message'])  # "Marked 3 salaries as paid"
```

---

### 4. `get_salary_statistics()`

**Purpose**: Get comprehensive statistics for a month
**Returns**: `SalaryStatistics`

**Includes**:
- Total employees
- Total gross/net salary
- Total deductions
- Company revenue and profit
- Average salary
- Per-factory breakdown

**Example**:
```python
stats = await service.get_salary_statistics(10, 2025)
print(f"Average salary: ¥{stats.average_salary:,}")
print(f"Total profit: ¥{stats.total_company_profit:,}")
```

---

### 5. `validate_salary()`

**Purpose**: Validate salary data before calculation
**Returns**: `ValidationResult`

**Checks**:
- Employee exists and is active
- Valid hourly rate (jikyu)
- Timer cards exist and are approved
- Payroll settings available
- No duplicate calculations

**Example**:
```python
validation = await service.validate_salary(123, 10, 2025)
if not validation.is_valid:
    print("Errors:", validation.errors)
    print("Warnings:", validation.warnings)
```

---

## 🔧 Integration with Existing Systems

### Database Tables Used

| Table | Purpose |
|-------|---------|
| `employees` | Employee data, hourly rate (jikyu) |
| `timer_cards` | Work hours tracking |
| `payroll_settings` | Configurable rates and rules |
| `rent_deductions` | Apartment rent deductions (V2) |
| `salary_calculations` | Saved salary calculations |
| `factories` | Factory configurations and bonuses |
| `apartments` | Apartment information (fallback) |

### Schemas Used

| Schema | Purpose |
|--------|---------|
| `SalaryCalculationResponse` | Return type for calculate_salary |
| `SalaryBulkResult` | Return type for bulk calculations |
| `SalaryStatistics` | Return type for statistics |
| `ValidationResult` | Return type for validation |
| `HoursBreakdown` | Hours detail structure |
| `Amounts` | Payment amounts structure |
| `DeductionsDetail` | Deductions breakdown |

---

## 📈 Calculation Flow

```
START
  ↓
[1] Fetch Employee
  ↓
[2] Get Timer Cards (approved for month)
  ↓
[3] Load PayrollSettings from DB
  ↓
[4] Calculate Hours Breakdown
    - Regular hours
    - Overtime hours
    - Night shift hours
    - Holiday hours
  ↓
[5] Calculate Amounts
    - Base amount = regular_hours × jikyu
    - Overtime amount = overtime_hours × jikyu × overtime_rate
    - Night amount = night_hours × jikyu × night_rate
    - Holiday amount = holiday_hours × jikyu × holiday_rate
  ↓
[6] Get Apartment Deductions
    - Query rent_deductions table
    - Fallback to employee.apartment_rent
    - Apply proration if enabled
  ↓
[7] Calculate Bonuses (from factory config)
    - Gasoline allowance
    - Attendance bonus
  ↓
[8] Calculate Totals
    - Gross = base + overtime + night + holiday + bonuses
    - Net = gross - apartment - other_deductions
  ↓
[9] Calculate Company Profit
    - Factory payment = jikyu_tanka × total_hours
    - Profit = factory_payment - gross_salary
  ↓
[10] Save to Database
  ↓
RETURN SalaryCalculationResponse
```

---

## 🚀 Usage Examples

### Example 1: Calculate Single Employee Salary

```python
from app.services.salary_service import get_salary_service
from app.core.database import get_db

async with get_db() as db:
    service = get_salary_service(db)

    # Calculate salary for employee 123 in October 2025
    result = await service.calculate_salary(
        employee_id=123,
        month=10,
        year=2025
    )

    print(f"Employee: {result.employee_id}")
    print(f"Period: {result.year}-{result.month:02d}")
    print(f"Work hours: {result.total_regular_hours}h")
    print(f"Overtime: {result.total_overtime_hours}h")
    print(f"Gross salary: ¥{result.gross_salary:,}")
    print(f"Deductions: ¥{result.apartment_deduction + result.other_deductions:,}")
    print(f"Net salary: ¥{result.net_salary:,}")
```

### Example 2: Bulk Calculate for Factory

```python
# Calculate salaries for all employees in factory "FAC-001"
result = await service.calculate_bulk_salaries(
    employee_ids=None,  # None = all active employees
    factory_id="FAC-001",
    month=10,
    year=2025
)

print(f"Total employees: {result.total_employees}")
print(f"Successful: {result.successful}")
print(f"Failed: {result.failed}")
print(f"Total gross: ¥{result.total_gross_salary:,}")
print(f"Total net: ¥{result.total_net_salary:,}")
print(f"Company profit: ¥{result.total_company_profit:,}")

if result.errors:
    print("\nErrors:")
    for error in result.errors:
        print(f"  - {error}")
```

### Example 3: Validate Before Calculating

```python
# Validate before calculating
validation = await service.validate_salary(
    employee_id=123,
    month=10,
    year=2025
)

if validation.is_valid:
    # Proceed with calculation
    result = await service.calculate_salary(123, 10, 2025)
    print(f"Calculation successful: ¥{result.net_salary:,}")
else:
    # Handle errors
    print("Validation failed:")
    for error in validation.errors:
        print(f"  ERROR: {error}")
    for warning in validation.warnings:
        print(f"  WARNING: {warning}")
```

### Example 4: Mark Salaries as Paid

```python
# Get unpaid salaries for October 2025
from app.models.models import SalaryCalculation

stmt = select(SalaryCalculation).where(
    and_(
        SalaryCalculation.year == 2025,
        SalaryCalculation.month == 10,
        SalaryCalculation.is_paid == False
    )
)
result = await db.execute(stmt)
unpaid_salaries = result.scalars().all()

# Mark as paid
salary_ids = [s.id for s in unpaid_salaries]
result = await service.mark_as_paid(
    salary_ids=salary_ids,
    payment_date=datetime(2025, 10, 25)
)

print(result['message'])  # "Marked 15 salaries as paid"
```

### Example 5: Get Monthly Statistics

```python
# Get statistics for October 2025
stats = await service.get_salary_statistics(
    month=10,
    year=2025
)

print(f"Period: {stats.year}-{stats.month:02d}")
print(f"Total employees: {stats.total_employees}")
print(f"Average salary: ¥{stats.average_salary:,}")
print(f"Total gross: ¥{stats.total_gross_salary:,}")
print(f"Total deductions: ¥{stats.total_deductions:,}")
print(f"Total net: ¥{stats.total_net_salary:,}")
print(f"Company revenue: ¥{stats.total_company_revenue:,}")
print(f"Company profit: ¥{stats.total_company_profit:,}")

print("\nPer-factory breakdown:")
for factory in stats.factories:
    print(f"  {factory['factory_id']}: {factory['employees']} employees, "
          f"¥{factory['total_salary']:,} total, "
          f"¥{factory['total_profit']:,} profit")
```

---

## 🔄 Migration Path

### Phase 1: Testing (Current)
1. ✅ Service created and documented
2. ⏳ Write unit tests for all methods
3. ⏳ Test with real data in development environment
4. ⏳ Verify calculations match existing system

### Phase 2: Integration
1. Update `backend/app/api/salary.py` to use `SalaryService`
2. Update endpoints to call service methods
3. Add error handling for service exceptions
4. Update API documentation

### Phase 3: Deprecation
1. Mark old functions as deprecated
2. Add migration warnings
3. Update all calling code
4. Remove old implementations

---

## 🧪 Testing Checklist

- [ ] Test `calculate_salary()` with valid employee
- [ ] Test with employee without timer cards (should fail)
- [ ] Test with employee without apartment (should work)
- [ ] Test with employee with rent_deductions
- [ ] Test with employee with old apartment_rent
- [ ] Test with factory bonuses enabled
- [ ] Test with factory bonuses disabled
- [ ] Test overtime, night, holiday calculations
- [ ] Test `calculate_bulk_salaries()` with multiple employees
- [ ] Test bulk calculation with errors
- [ ] Test `mark_as_paid()` functionality
- [ ] Test `get_salary_statistics()` accuracy
- [ ] Test `validate_salary()` error detection
- [ ] Test with no PayrollSettings (should use defaults)
- [ ] Test duplicate calculation prevention

---

## 📝 Code Quality

### Type Safety
- ✅ Full type hints on all methods
- ✅ Pydantic schemas for all return types
- ✅ SQLAlchemy models with proper typing

### Documentation
- ✅ Comprehensive docstrings (Google style)
- ✅ Usage examples in docstrings
- ✅ Inline comments for complex logic
- ✅ This documentation file

### Error Handling
- ✅ Try-catch blocks around DB operations
- ✅ Meaningful error messages
- ✅ Proper exception propagation
- ✅ Logging for all major operations

### Code Organization
- ✅ Clear separation of public/private methods
- ✅ Single Responsibility Principle
- ✅ DRY (Don't Repeat Yourself)
- ✅ Consistent naming conventions

---

## ⚙️ Configuration

### PayrollSettings (Database)

Create/update payroll settings:

```sql
INSERT INTO payroll_settings (
    overtime_rate,
    night_shift_rate,
    holiday_rate,
    sunday_rate,
    standard_hours_per_month
) VALUES (
    1.25,  -- 25% premium for overtime
    1.25,  -- 25% premium for night shift
    1.35,  -- 35% premium for holidays
    1.35,  -- 35% premium for Sundays
    160    -- Standard monthly hours
);
```

### Environment Variables (settings.py)

Fallback configuration if PayrollSettings not found:

```python
# Salary calculation settings
OVERTIME_RATE_25 = 1.25          # 25% overtime premium
NIGHT_SHIFT_PREMIUM = 1.25       # 25% night shift premium
HOLIDAY_WORK_PREMIUM = 1.35      # 35% holiday premium
APARTMENT_PRORATE_BY_DAY = True  # Enable daily proration
```

---

## 🐛 Known Limitations

1. **Sunday Hours**: Currently not separately tracked (combined with holiday_hours)
2. **Tax Calculations**: Simplified (5% income tax, 10% resident tax)
   - TODO: Implement progressive tax brackets
   - TODO: Add dependent deductions
3. **Insurance Calculations**: Fixed percentages
   - TODO: Use actual insurance rate tables
4. **Public Holidays**: Not distinguished from weekends
   - TODO: Add Japanese holiday calendar

---

## 🎯 Future Enhancements

### Short-term
1. Add unit tests (pytest)
2. Add integration tests
3. Performance optimization for bulk calculations
4. Add caching for PayrollSettings

### Medium-term
1. Implement progressive tax calculation
2. Add detailed insurance calculations
3. Support for multiple pay periods (weekly, bi-weekly)
4. PDF payslip generation integration

### Long-term
1. Historical rate tracking (audit trail)
2. What-if calculation scenarios
3. Salary projection and forecasting
4. Integration with accounting systems

---

## 📚 Related Documentation

- **API Documentation**: `backend/app/api/salary.py`
- **Old Service**: `backend/app/services/payroll_service.py`
- **Database Models**: `backend/app/models/models.py`
- **Schemas**: `backend/app/schemas/salary.py`, `backend/app/schemas/payroll.py`
- **Apartment System**: `docs/apartment-deductions-v2.md` (if exists)

---

## 🤝 Contributing

When modifying this service:

1. **Add tests** for new functionality
2. **Update docstrings** with examples
3. **Log important operations** (INFO level)
4. **Handle errors gracefully** (don't fail entire batch)
5. **Use Decimal** for monetary calculations
6. **Follow async/await** patterns
7. **Update this documentation**

---

## 📞 Support

For questions or issues:
- Check logs in `docker compose logs backend`
- Review database queries with SQL logging
- Verify PayrollSettings are configured
- Check timer card approval status

---

**END OF DOCUMENT**
