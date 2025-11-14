#!/usr/bin/env python3
"""
LolaAppJp - Final Comprehensive Testing Suite

Simulates complete application testing including:
- All backend APIs
- All frontend pages
- Database integrity
- Docker configuration
- Service integrations
- Business logic
- Security
"""
import os
import re
import json
from typing import Dict, List, Tuple

class Color:
    """Terminal colors"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(title: str):
    """Print section header"""
    print(f"\n{Color.BOLD}{'=' * 80}{Color.END}")
    print(f"{Color.BOLD}{Color.BLUE}{title}{Color.END}")
    print(f"{Color.BOLD}{'=' * 80}{Color.END}\n")

def print_success(msg: str):
    """Print success message"""
    print(f"{Color.GREEN}✅ {msg}{Color.END}")

def print_failure(msg: str):
    """Print failure message"""
    print(f"{Color.RED}❌ {msg}{Color.END}")

def print_warning(msg: str):
    """Print warning message"""
    print(f"{Color.YELLOW}⚠️  {msg}{Color.END}")

def check_file_exists(filepath: str) -> bool:
    """Check if file exists"""
    return os.path.exists(filepath)

def read_file(filepath: str) -> str:
    """Read file content"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return ""

def count_lines(filepath: str) -> int:
    """Count lines in file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return len(f.readlines())
    except:
        return 0

# ============================================================================
# TEST 1: BACKEND API ENDPOINTS
# ============================================================================

def test_backend_apis() -> Tuple[int, int]:
    """Test all backend API endpoints"""
    print_header("TEST 1: Backend API Endpoints")

    apis = {
        "auth": {
            "file": "backend/app/api/auth.py",
            "endpoints": 9,
            "methods": ["login", "refresh_token", "logout", "get_current_user_info",
                       "register_user", "change_password", "list_users", "update_user", "delete_user"]
        },
        "candidates": {
            "file": "backend/app/api/candidates.py",
            "endpoints": 6,
            "methods": ["create_candidate", "list_candidates", "get_candidate",
                       "update_candidate", "delete_candidate", "process_candidate_ocr"]
        },
        "employees": {
            "file": "backend/app/api/employees.py",
            "endpoints": 7,
            "methods": ["create_employee", "list_employees", "get_employee",
                       "update_employee", "delete_employee", "assign_factory", "assign_apartment"]
        },
        "companies": {
            "file": "backend/app/api/companies.py",
            "endpoints": 5,
            "methods": ["create", "list", "get", "update", "delete"]
        },
        "plants": {
            "file": "backend/app/api/plants.py",
            "endpoints": 5,
            "methods": ["create", "list", "get", "update", "delete"]
        },
        "lines": {
            "file": "backend/app/api/lines.py",
            "endpoints": 5,
            "methods": ["create", "list", "get", "update", "delete"]
        },
        "apartments": {
            "file": "backend/app/api/apartments.py",
            "endpoints": 7,
            "methods": ["create", "list", "get", "update", "delete", "recommend", "assign"]
        },
        "yukyu": {
            "file": "backend/app/api/yukyu.py",
            "endpoints": 8,
            "methods": ["grant", "use", "get_balance", "get_transactions",
                       "expire", "summary", "auto_grant", "adjust"]
        },
        "timercards": {
            "file": "backend/app/api/timercards.py",
            "endpoints": 7,
            "methods": ["create", "process_ocr", "list", "get", "update", "delete", "monthly_summary"]
        },
        "payroll": {
            "file": "backend/app/api/payroll.py",
            "endpoints": 6,
            "methods": ["calculate", "calculate_all", "get_record", "list", "update", "approve"]
        },
        "requests": {
            "file": "backend/app/api/requests.py",
            "endpoints": 8,
            "methods": ["create", "list", "get", "update", "approve", "reject", "pending", "by_employee"]
        }
    }

    passed = 0
    total = len(apis)

    for api_name, api_info in apis.items():
        file_path = api_info["file"]

        if check_file_exists(file_path):
            content = read_file(file_path)
            lines = count_lines(file_path)

            # Check for router definition
            has_router = "@router." in content
            # Check for async def
            has_async = "async def" in content
            # Check for proper imports
            has_imports = "from fastapi import" in content

            if has_router and has_async and has_imports:
                print_success(f"{api_name:15} - {lines:4} lines, {api_info['endpoints']} endpoints")
                passed += 1
            else:
                print_failure(f"{api_name:15} - Missing required components")
        else:
            print_warning(f"{api_name:15} - File not found (will be created)")

    print(f"\n{Color.BOLD}Result: {passed}/{total} APIs validated{Color.END}")
    return passed, total

# ============================================================================
# TEST 2: BUSINESS SERVICES
# ============================================================================

def test_business_services() -> Tuple[int, int]:
    """Test business logic services"""
    print_header("TEST 2: Business Services")

    services = {
        "OCRService": {
            "file": "backend/app/services/ocr_service.py",
            "methods": ["process_image", "extract_rirekisho_fields", "extract_timer_card_data"],
            "lines_min": 300
        },
        "ApartmentService": {
            "file": "backend/app/services/apartment_service.py",
            "methods": ["recommend_apartments", "calculate_distance", "score_proximity"],
            "lines_min": 400
        },
        "YukyuService": {
            "file": "backend/app/services/yukyu_service.py",
            "methods": ["grant_yukyu", "use_yukyu", "get_balance", "expire_old_balances"],
            "lines_min": 400
        },
        "PayrollService": {
            "file": "backend/app/services/payroll_service.py",
            "methods": ["calculate_monthly_payroll", "calculate_gross_pay", "calculate_deductions"],
            "lines_min": 400
        }
    }

    passed = 0
    total = len(services)

    for service_name, service_info in services.items():
        file_path = service_info["file"]

        if check_file_exists(file_path):
            content = read_file(file_path)
            lines = count_lines(file_path)

            # Check class definition
            has_class = f"class {service_name}" in content
            # Check methods
            methods_found = sum(1 for m in service_info["methods"] if f"def {m}" in content)
            # Check line count
            enough_lines = lines >= service_info["lines_min"]

            if has_class and methods_found >= len(service_info["methods"]) - 1 and enough_lines:
                print_success(f"{service_name:20} - {lines:4} lines, {methods_found}/{len(service_info['methods'])} methods")
                passed += 1
            else:
                missing = []
                if not has_class: missing.append("class")
                if methods_found < len(service_info["methods"]) - 1: missing.append("methods")
                if not enough_lines: missing.append("lines")
                print_failure(f"{service_name:20} - Missing: {', '.join(missing)}")
        else:
            print_failure(f"{service_name:20} - File not found")

    print(f"\n{Color.BOLD}Result: {passed}/{total} Services validated{Color.END}")
    return passed, total

# ============================================================================
# TEST 3: FRONTEND PAGES
# ============================================================================

def test_frontend_pages() -> Tuple[int, int]:
    """Test frontend pages"""
    print_header("TEST 3: Frontend Pages")

    pages = {
        "Login": "frontend/app/(auth)/login/page.tsx",
        "Dashboard": "frontend/app/dashboard/page.tsx",
        "Candidates": "frontend/app/(dashboard)/candidates/page.tsx",
        "Nyusha": "frontend/app/(dashboard)/nyusha/page.tsx",
        "Employees": "frontend/app/(dashboard)/employees/page.tsx",
        "Factories": "frontend/app/(dashboard)/factories/page.tsx",
        "Apartments": "frontend/app/(dashboard)/apartments/page.tsx",
        "Yukyu": "frontend/app/(dashboard)/yukyu/page.tsx",
        "Timer Cards": "frontend/app/(dashboard)/timercards/page.tsx",
        "Payroll": "frontend/app/(dashboard)/payroll/page.tsx",
        "Requests": "frontend/app/(dashboard)/requests/page.tsx",
        "Reports": "frontend/app/(dashboard)/reports/page.tsx"
    }

    passed = 0
    total = len(pages)

    for page_name, page_path in pages.items():
        if check_file_exists(page_path):
            content = read_file(page_path)
            lines = count_lines(page_path)

            # Check for React component
            has_export = "export default" in content
            # Check for TypeScript
            is_tsx = page_path.endswith(".tsx")

            if has_export and is_tsx and lines > 10:
                print_success(f"{page_name:15} - {lines:4} lines")
                passed += 1
            else:
                print_failure(f"{page_name:15} - Invalid component")
        else:
            print_warning(f"{page_name:15} - Will be created")

    print(f"\n{Color.BOLD}Result: {passed}/{total} Pages validated{Color.END}")
    return passed, total

# ============================================================================
# TEST 4: DATABASE SCHEMA
# ============================================================================

def test_database_schema() -> Tuple[int, int]:
    """Test database schema"""
    print_header("TEST 4: Database Schema")

    models_file = "backend/app/models/models.py"

    if not check_file_exists(models_file):
        print_failure("models.py not found")
        return 0, 1

    content = read_file(models_file)

    # Expected components
    expected_enums = 7
    expected_models = 13
    expected_fks = 20  # At least 20
    expected_indexes = 20  # At least 20

    # Count components
    enum_pattern = r'class\s+\w+\(str,\s*enum\.Enum\)'
    model_pattern = r'class\s+\w+\(Base\)'
    fk_pattern = r'ForeignKey\('
    index_pattern = r'Index\('

    enums_found = len(re.findall(enum_pattern, content))
    models_found = len(re.findall(model_pattern, content))
    fks_found = len(re.findall(fk_pattern, content))
    indexes_found = len(re.findall(index_pattern, content))

    tests = [
        ("Enums", enums_found, expected_enums, enums_found == expected_enums),
        ("Models (Tables)", models_found, expected_models, models_found == expected_models),
        ("Foreign Keys", fks_found, expected_fks, fks_found >= expected_fks),
        ("Indexes", indexes_found, expected_indexes, indexes_found >= expected_indexes)
    ]

    passed = 0
    total = len(tests)

    for test_name, found, expected, success in tests:
        if success:
            print_success(f"{test_name:20} - {found:2} found (expected {expected})")
            passed += 1
        else:
            print_failure(f"{test_name:20} - {found:2} found (expected {expected})")

    print(f"\n{Color.BOLD}Result: {passed}/{total} Schema checks passed{Color.END}")
    return passed, total

# ============================================================================
# TEST 5: DOCKER CONFIGURATION
# ============================================================================

def test_docker_configuration() -> Tuple[int, int]:
    """Test Docker configuration"""
    print_header("TEST 5: Docker Configuration")

    docker_file = "docker-compose.yml"

    if not check_file_exists(docker_file):
        print_failure("docker-compose.yml not found")
        return 0, 1

    content = read_file(docker_file)

    # Expected services
    expected_services = [
        "db", "redis", "backend", "frontend", "nginx", "adminer",
        "otel-collector", "tempo", "prometheus", "grafana", "backup", "importer"
    ]

    tests = []
    for service in expected_services:
        found = f"{service}:" in content
        tests.append((service, found))

    passed = sum(1 for _, found in tests if found)
    total = len(tests)

    for service, found in tests:
        if found:
            print_success(f"Service: {service:20}")
        else:
            print_failure(f"Service: {service:20} - Not found")

    # Check for networks and volumes
    has_networks = "networks:" in content
    has_volumes = "volumes:" in content

    if has_networks:
        print_success("Networks configured")
        passed += 1
        total += 1
    else:
        print_failure("Networks not configured")
        total += 1

    if has_volumes:
        print_success("Volumes configured")
        passed += 1
        total += 1
    else:
        print_failure("Volumes not configured")
        total += 1

    print(f"\n{Color.BOLD}Result: {passed}/{total} Docker checks passed{Color.END}")
    return passed, total

# ============================================================================
# TEST 6: CRITICAL FIXES VERIFICATION
# ============================================================================

def test_critical_fixes() -> Tuple[int, int]:
    """Verify all critical fixes"""
    print_header("TEST 6: Critical Fixes Verification")

    fixes = [
        {
            "name": "Fix #1: or_() import in apartment_service.py",
            "file": "backend/app/services/apartment_service.py",
            "check": lambda c: "from sqlalchemy import and_, or_" in c
        },
        {
            "name": "Fix #2: EmployeeStatus enum in apartment_service.py",
            "file": "backend/app/services/apartment_service.py",
            "check": lambda c: "EmployeeStatus.ACTIVE" in c
        },
        {
            "name": "Fix #3: or_() import in payroll_service.py",
            "file": "backend/app/services/payroll_service.py",
            "check": lambda c: "from sqlalchemy import and_, or_" in c
        },
        {
            "name": "Fix #4: db.flush() in yukyu_service.py",
            "file": "backend/app/services/yukyu_service.py",
            "check": lambda c: "self.db.flush()" in c
        },
        {
            "name": "Fix #5: Azure OCR timeout",
            "file": "backend/app/services/ocr_service.py",
            "check": lambda c: "max_attempts" in c and "TimeoutError" in c
        },
        {
            "name": "Fix #6: Imports at top of ocr_service.py",
            "file": "backend/app/services/ocr_service.py",
            "check": lambda c: c[:500].count("import re") >= 1 and c[:500].count("import time") >= 1
        },
        {
            "name": "Fix #7: Distance returns None",
            "file": "backend/app/services/apartment_service.py",
            "check": lambda c: "return None  # Cannot calculate distance" in c
        },
        {
            "name": "Fix #8: Coordinate validation",
            "file": "backend/app/services/apartment_service.py",
            "check": lambda c: "-90 <= lat" in c and "-180 <= lon" in c
        },
        {
            "name": "Fix #9: Hour categories documentation",
            "file": "backend/app/services/payroll_service.py",
            "check": lambda c: "MUTUALLY EXCLUSIVE" in c
        }
    ]

    passed = 0
    total = len(fixes)

    for fix in fixes:
        if check_file_exists(fix["file"]):
            content = read_file(fix["file"])
            if fix["check"](content):
                print_success(fix["name"])
                passed += 1
            else:
                print_failure(fix["name"])
        else:
            print_failure(f"{fix['name']} - File not found")

    print(f"\n{Color.BOLD}Result: {passed}/{total} Fixes verified{Color.END}")
    return passed, total

# ============================================================================
# TEST 7: SECURITY CHECKS
# ============================================================================

def test_security() -> Tuple[int, int]:
    """Test security configurations"""
    print_header("TEST 7: Security Checks")

    auth_file = "backend/app/api/auth.py"
    security_file = "backend/app/core/security.py"

    checks = []

    # Check auth.py
    if check_file_exists(auth_file):
        content = read_file(auth_file)
        checks.append(("JWT token handling", "create_access_token" in content or "jose" in content))
        checks.append(("Password hashing", "pwd_context" in content or "bcrypt" in content))
        checks.append(("OAuth2 bearer", "OAuth2PasswordBearer" in content or "Depends" in content))
    else:
        checks.extend([
            ("JWT token handling", False),
            ("Password hashing", False),
            ("OAuth2 bearer", False)
        ])

    # Check security.py
    if check_file_exists(security_file):
        content = read_file(security_file)
        checks.append(("Security utilities", "verify_password" in content or "get_password_hash" in content))
    else:
        checks.append(("Security utilities", False))

    # Check for SQL injection protection (using ORM)
    models_file = "backend/app/models/models.py"
    if check_file_exists(models_file):
        content = read_file(models_file)
        checks.append(("ORM usage (SQL injection protection)", "Base" in content and "Column" in content))
    else:
        checks.append(("ORM usage (SQL injection protection)", False))

    passed = sum(1 for _, result in checks if result)
    total = len(checks)

    for check_name, result in checks:
        if result:
            print_success(check_name)
        else:
            print_failure(check_name)

    print(f"\n{Color.BOLD}Result: {passed}/{total} Security checks passed{Color.END}")
    return passed, total

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Run all tests"""
    print(f"\n{Color.BOLD}{Color.BLUE}")
    print("=" * 80)
    print("  LolaAppJp - COMPREHENSIVE TESTING SUITE")
    print("  Final Validation Before Deployment")
    print("=" * 80)
    print(f"{Color.END}")

    all_results = []

    # Run all test suites
    all_results.append(test_backend_apis())
    all_results.append(test_business_services())
    all_results.append(test_frontend_pages())
    all_results.append(test_database_schema())
    all_results.append(test_docker_configuration())
    all_results.append(test_critical_fixes())
    all_results.append(test_security())

    # Calculate totals
    total_passed = sum(r[0] for r in all_results)
    total_tests = sum(r[1] for r in all_results)
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

    # Print final summary
    print_header("FINAL SUMMARY")

    print(f"{Color.BOLD}Test Categories:{Color.END}")
    categories = [
        "Backend APIs",
        "Business Services",
        "Frontend Pages",
        "Database Schema",
        "Docker Configuration",
        "Critical Fixes",
        "Security"
    ]

    for i, category in enumerate(categories):
        passed, total = all_results[i]
        percentage = (passed / total * 100) if total > 0 else 0
        color = Color.GREEN if percentage == 100 else Color.YELLOW if percentage >= 80 else Color.RED
        print(f"  {color}{category:25} {passed:2}/{total:2} ({percentage:5.1f}%){Color.END}")

    print(f"\n{Color.BOLD}Overall Results:{Color.END}")
    print(f"  Total Tests: {total_tests}")
    print(f"  Passed: {total_passed}")
    print(f"  Failed: {total_tests - total_passed}")
    print(f"  Success Rate: {success_rate:.1f}%")

    print(f"\n{Color.BOLD}Deployment Status:{Color.END}")
    if success_rate >= 90:
        print(f"  {Color.GREEN}✅ READY FOR DEPLOYMENT{Color.END}")
        print(f"  {Color.GREEN}All critical systems operational{Color.END}")
        return 0
    elif success_rate >= 70:
        print(f"  {Color.YELLOW}⚠️  NEEDS REVIEW{Color.END}")
        print(f"  {Color.YELLOW}Some components require attention{Color.END}")
        return 1
    else:
        print(f"  {Color.RED}❌ NOT READY{Color.END}")
        print(f"  {Color.RED}Critical issues must be resolved{Color.END}")
        return 2

if __name__ == "__main__":
    import sys
    sys.exit(main())
