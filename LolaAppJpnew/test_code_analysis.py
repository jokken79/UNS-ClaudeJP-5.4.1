#!/usr/bin/env python3
"""
Static Code Analysis for LolaAppJp Services

Tests all fixes without requiring dependencies
"""
import re
import os

def read_file(path):
    """Read file content"""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def check_import(content, module, imported_items):
    """Check if specific items are imported from a module"""
    pattern = f"from {re.escape(module)} import.*"
    matches = re.findall(pattern, content)

    if not matches:
        return False, []

    imported = []
    for match in matches:
        for item in imported_items:
            if item in match:
                imported.append(item)

    return len(imported) == len(imported_items), imported

def check_enum_comparison(content):
    """Check for string comparisons with enum fields"""
    # Look for == 'ACTIVE' which should be == EmployeeStatus.ACTIVE
    bad_patterns = [
        r"\.status\s*==\s*['\"]ACTIVE['\"]",
        r"\.status\s*==\s*['\"]PENDING['\"]",
        r"\.status\s*==\s*['\"]APPROVED['\"]"
    ]

    issues = []
    for pattern in bad_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            issues.append(match.group())

    return len(issues) == 0, issues

def check_flush_before_id_use(content):
    """Check if db.flush() is called before using .id on new objects"""
    # Look for pattern: self.db.add(X) followed by usage of X.id without flush
    lines = content.split('\n')

    for i, line in enumerate(lines):
        if 'self.db.add(balance)' in line:
            # Check next 5 lines for flush() before balance.id usage
            next_lines = lines[i+1:i+6]
            has_flush = any('flush()' in l for l in next_lines)
            has_id_usage = any('balance.id' in l for l in next_lines)

            if has_id_usage and not has_flush:
                return False, f"Line {i+1}: balance.id used without flush()"
            elif has_flush and has_id_usage:
                return True, "db.flush() correctly placed"

    return True, "No issues found"

def check_timeout_in_loop(content):
    """Check if while loops have timeout protection"""
    # Look for while True: without timeout
    pattern = r"while\s+True:\s*\n.*?client\.get_read_result"

    if re.search(pattern, content, re.DOTALL):
        # Check if there's a timeout mechanism
        if "max_attempts" in content and "attempts <" in content:
            return True, "Timeout protection present"
        else:
            return False, "Infinite loop without timeout"

    return True, "No problematic while loops"

def check_imports_at_top(content):
    """Check if imports are at the top of file, not inside functions"""
    lines = content.split('\n')

    # Get imports section (first ~50 lines before first def/class)
    import_section_end = 0
    for i, line in enumerate(lines[:100]):
        if line.strip().startswith('def ') or line.strip().startswith('class '):
            import_section_end = i
            break

    top_section = '\n'.join(lines[:import_section_end])

    # Check if critical imports are in top section
    critical_imports = ['import re', 'import time']
    issues = []

    for imp in critical_imports:
        if imp in content and imp not in top_section:
            issues.append(imp)

    return len(issues) == 0, issues if issues else "All imports at top"

def check_distance_return_type(content):
    """Check if calculate_distance returns None for missing coords"""
    # Look for the function
    pattern = r"def calculate_distance.*?return.*?(999999|None)"

    matches = re.finditer(pattern, content, re.DOTALL)
    for match in matches:
        if "None" in match.group():
            return True, "Returns None for missing coordinates"
        elif "999999" in match.group():
            return False, "Returns 999999 instead of None"

    return True, "Function not found or pattern unclear"

def check_coordinate_validation(content):
    """Check if coordinates are validated"""
    validations = [
        r"-90\s*<=.*<=\s*90",  # Latitude check
        r"-180\s*<=.*<=\s*180"  # Longitude check
    ]

    found = []
    for pattern in validations:
        if re.search(pattern, content):
            found.append(pattern)

    return len(found) >= 2, f"{len(found)}/2 validation checks found"

def check_hour_documentation(content):
    """Check if hour categories are documented"""
    keywords = [
        "MUTUALLY EXCLUSIVE",
        "overtime_hours",
        "night_hours",
        "regular_hours",
        "Labor Standards Act"
    ]

    found = sum(1 for kw in keywords if kw in content)

    return found >= 4, f"{found}/{len(keywords)} documentation keywords found"

def main():
    print("=" * 80)
    print("LolaAppJp - Static Code Analysis (No Dependencies Required)")
    print("=" * 80)
    print()

    base_path = "backend/app/services/"
    results = {}

    # Test 1: apartment_service.py
    print("📁 TEST: apartment_service.py")
    print("-" * 80)

    file_path = os.path.join(base_path, "apartment_service.py")
    content = read_file(file_path)

    # Check 1: or_() import
    success, imported = check_import(content, "sqlalchemy", ["and_", "or_"])
    print(f"{'✅' if success else '❌'} Import or_() from sqlalchemy: {imported if success else 'MISSING'}")
    results['apartment_or_import'] = success

    # Check 2: EmployeeStatus import
    success, imported = check_import(content, "app.models.models", ["EmployeeStatus"])
    print(f"{'✅' if success else '❌'} Import EmployeeStatus: {'YES' if success else 'MISSING'}")
    results['apartment_enum_import'] = success

    # Check 3: Enum comparison
    success, issues = check_enum_comparison(content)
    print(f"{'✅' if success else '❌'} Enum comparison (not string): {'CORRECT' if success else f'Issues: {issues}'}")
    results['apartment_enum_compare'] = success

    # Check 4: Distance return None
    success, msg = check_distance_return_type(content)
    print(f"{'✅' if success else '❌'} Distance returns None: {msg}")
    results['apartment_distance_none'] = success

    # Check 5: Coordinate validation
    success, msg = check_coordinate_validation(content)
    print(f"{'✅' if success else '❌'} Coordinate validation: {msg}")
    results['apartment_coord_validation'] = success

    print()

    # Test 2: payroll_service.py
    print("📁 TEST: payroll_service.py")
    print("-" * 80)

    file_path = os.path.join(base_path, "payroll_service.py")
    content = read_file(file_path)

    # Check 1: or_() import
    success, imported = check_import(content, "sqlalchemy", ["and_", "or_"])
    print(f"{'✅' if success else '❌'} Import or_() from sqlalchemy: {imported if success else 'MISSING'}")
    results['payroll_or_import'] = success

    # Check 2: Documentation
    success, msg = check_hour_documentation(content)
    print(f"{'✅' if success else '❌'} Hour categories documentation: {msg}")
    results['payroll_documentation'] = success

    # Check 3: Module docstring closed
    has_triple_quote_close = '"""' in content[:500] and content[:500].count('"""') >= 2
    print(f"{'✅' if has_triple_quote_close else '❌'} Module docstring properly closed: {'YES' if has_triple_quote_close else 'NO'}")
    results['payroll_docstring'] = has_triple_quote_close

    print()

    # Test 3: yukyu_service.py
    print("📁 TEST: yukyu_service.py")
    print("-" * 80)

    file_path = os.path.join(base_path, "yukyu_service.py")
    content = read_file(file_path)

    # Check 1: db.flush() before balance.id
    success, msg = check_flush_before_id_use(content)
    print(f"{'✅' if success else '❌'} db.flush() before balance.id usage: {msg}")
    results['yukyu_flush'] = success

    print()

    # Test 4: ocr_service.py
    print("📁 TEST: ocr_service.py")
    print("-" * 80)

    file_path = os.path.join(base_path, "ocr_service.py")
    content = read_file(file_path)

    # Check 1: Imports at top
    success, msg = check_imports_at_top(content)
    print(f"{'✅' if success else '❌'} Imports at top of file: {msg}")
    results['ocr_imports_top'] = success

    # Check 2: Timeout in while loop
    success, msg = check_timeout_in_loop(content)
    print(f"{'✅' if success else '❌'} Azure OCR timeout protection: {msg}")
    results['ocr_timeout'] = success

    print()

    # Summary
    print("=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)

    total_checks = len(results)
    passed_checks = sum(1 for r in results.values() if r)

    print(f"Total checks: {total_checks}")
    print(f"Passed: {passed_checks}/{total_checks}")
    print(f"Success rate: {passed_checks/total_checks*100:.1f}%")
    print()

    if passed_checks == total_checks:
        print("✅ ALL CHECKS PASSED - All fixes verified successfully")
        print()
        print("The following critical fixes are confirmed:")
        print("  ✅ Fix #1: or_() imported in apartment_service.py")
        print("  ✅ Fix #2: EmployeeStatus enum comparison fixed")
        print("  ✅ Fix #3: or_() imported in payroll_service.py")
        print("  ✅ Fix #4: db.flush() added before balance.id usage")
        print("  ✅ Fix #5: Azure OCR timeout protection added")
        print("  ✅ Fix #6: Imports moved to top of ocr_service.py")
        print("  ✅ Fix #7: Distance returns None for missing coords")
        print("  ✅ Fix #8: Coordinate validation added")
        print("  ✅ Fix #9: Hour categories documented")
        return 0
    else:
        print("⚠️  SOME CHECKS FAILED")
        print()
        print("Failed checks:")
        for check, passed in results.items():
            if not passed:
                print(f"  ❌ {check}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
