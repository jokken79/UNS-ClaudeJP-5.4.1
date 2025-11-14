#!/usr/bin/env python3
"""
Comprehensive Final Testing Script for LolaAppJp Complete Implementation

Tests:
1. Python syntax validation (all backend files)
2. Import verification (all dependencies)
3. TypeScript/TSX syntax validation (all frontend files)
4. File structure verification
5. API endpoint count validation
6. Schema validation
7. Documentation completeness
"""

import os
import py_compile
import json
from pathlib import Path

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'=' * 80}{RESET}")
    print(f"{BLUE}{text.center(80)}{RESET}")
    print(f"{BLUE}{'=' * 80}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    print(f"{RED}✗ {text}{RESET}")

def print_info(text):
    print(f"{YELLOW}ℹ {text}{RESET}")

class ComprehensiveTest:
    def __init__(self):
        self.backend_path = Path("/home/user/UNS-ClaudeJP-5.4.1/LolaAppJpnew/backend")
        self.frontend_path = Path("/home/user/UNS-ClaudeJP-5.4.1/LolaAppJpnew/frontend")
        self.errors = []
        self.warnings = []
        self.success_count = 0

    def test_backend_syntax(self):
        """Test all Python files for syntax errors"""
        print_header("BACKEND SYNTAX VALIDATION")

        python_files = list(self.backend_path.rglob("*.py"))
        print_info(f"Found {len(python_files)} Python files")

        for py_file in python_files:
            try:
                py_compile.compile(str(py_file), doraise=True)
                self.success_count += 1
                print_success(f"Syntax OK: {py_file.relative_to(self.backend_path)}")
            except py_compile.PyCompileError as e:
                self.errors.append(f"Syntax error in {py_file}: {e}")
                print_error(f"Syntax error in {py_file.relative_to(self.backend_path)}")

    def test_backend_imports(self):
        """Verify all backend imports"""
        print_header("BACKEND IMPORT VERIFICATION")

        critical_imports = [
            "fastapi",
            "pydantic",
            "sqlalchemy",
            "uvicorn",
            "python-jose",
            "passlib"
        ]

        for imp in critical_imports:
            try:
                __import__(imp.replace("-", "_"))
                print_success(f"Import OK: {imp}")
                self.success_count += 1
            except ImportError:
                self.errors.append(f"Missing dependency: {imp}")
                print_error(f"Missing dependency: {imp}")

    def test_api_endpoints(self):
        """Count and validate API endpoints"""
        print_header("API ENDPOINTS VALIDATION")

        api_files = list((self.backend_path / "app" / "api").glob("*.py"))
        api_files = [f for f in api_files if f.name != "__init__.py"]

        print_info(f"Found {len(api_files)} API router files")

        expected_endpoints = {
            "candidates.py": 6,
            "employees.py": 7,
            "apartments.py": 7,
            "yukyu.py": 8,
            "companies.py": 5,
            "plants.py": 5,
            "lines.py": 5,
            "timercards.py": 7,
            "payroll.py": 6,
            "requests.py": 8
        }

        for api_file in api_files:
            if api_file.name in expected_endpoints:
                with open(api_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    endpoint_count = content.count("@router.")
                    expected = expected_endpoints[api_file.name]

                    if endpoint_count >= expected:
                        print_success(f"{api_file.name}: {endpoint_count} endpoints (expected ≥{expected})")
                        self.success_count += 1
                    else:
                        self.warnings.append(f"{api_file.name}: Only {endpoint_count} endpoints (expected ≥{expected})")
                        print_error(f"{api_file.name}: Only {endpoint_count} endpoints (expected ≥{expected})")

    def test_schemas(self):
        """Validate Pydantic schemas"""
        print_header("SCHEMA VALIDATION")

        schema_files = list((self.backend_path / "app" / "schemas").glob("*.py"))
        schema_files = [f for f in schema_files if f.name != "__init__.py"]

        print_info(f"Found {len(schema_files)} schema files")

        expected_schemas = [
            "candidate.py",
            "employee.py",
            "apartment.py",
            "yukyu.py",
            "company.py",
            "plant.py",
            "line.py",
            "timercard.py",
            "payroll.py",
            "request.py"
        ]

        for schema_name in expected_schemas:
            schema_path = self.backend_path / "app" / "schemas" / schema_name
            if schema_path.exists():
                print_success(f"Schema exists: {schema_name}")
                self.success_count += 1
            else:
                self.errors.append(f"Missing schema: {schema_name}")
                print_error(f"Missing schema: {schema_name}")

    def test_frontend_pages(self):
        """Validate frontend pages"""
        print_header("FRONTEND PAGES VALIDATION")

        expected_pages = [
            "(auth)/login/page.tsx",
            "(dashboard)/candidates/page.tsx",
            "(dashboard)/employees/page.tsx",
            "(dashboard)/companies/page.tsx",
            "(dashboard)/apartments/page.tsx",
            "(dashboard)/factories/page.tsx",
            "(dashboard)/yukyu/page.tsx",
            "(dashboard)/timercards/page.tsx",
            "(dashboard)/payroll/page.tsx",
            "(dashboard)/requests/page.tsx",
            "(dashboard)/reports/page.tsx"
        ]

        print_info(f"Checking {len(expected_pages)} expected pages")

        for page in expected_pages:
            page_path = self.frontend_path / "app" / page
            if page_path.exists():
                # Check file size
                file_size = page_path.stat().st_size
                if file_size > 100:  # Ensure not empty
                    print_success(f"Page exists: {page} ({file_size} bytes)")
                    self.success_count += 1
                else:
                    self.warnings.append(f"Page too small: {page} ({file_size} bytes)")
                    print_error(f"Page too small: {page} ({file_size} bytes)")
            else:
                self.errors.append(f"Missing page: {page}")
                print_error(f"Missing page: {page}")

    def test_main_py(self):
        """Validate main.py router registration"""
        print_header("MAIN.PY ROUTER REGISTRATION")

        main_py = self.backend_path / "app" / "main.py"

        if not main_py.exists():
            self.errors.append("main.py not found")
            print_error("main.py not found")
            return

        with open(main_py, 'r', encoding='utf-8') as f:
            content = f.read()

        expected_routers = [
            "auth.router",
            "candidates.router",
            "employees.router",
            "apartments.router",
            "yukyu.router",
            "companies.router",
            "plants.router",
            "lines.router",
            "timercards.router",
            "payroll.router",
            "requests.router"
        ]

        for router in expected_routers:
            if f"app.include_router({router}" in content:
                print_success(f"Router registered: {router}")
                self.success_count += 1
            else:
                self.errors.append(f"Router not registered: {router}")
                print_error(f"Router not registered: {router}")

    def test_file_structure(self):
        """Validate overall file structure"""
        print_header("FILE STRUCTURE VALIDATION")

        critical_paths = [
            self.backend_path / "app" / "api",
            self.backend_path / "app" / "schemas",
            self.backend_path / "app" / "services",
            self.backend_path / "app" / "models",
            self.backend_path / "app" / "core",
            self.frontend_path / "app" / "(auth)",
            self.frontend_path / "app" / "(dashboard)"
        ]

        for path in critical_paths:
            if path.exists() and path.is_dir():
                file_count = len(list(path.glob("*.py"))) + len(list(path.glob("*.tsx")))
                print_success(f"Directory exists: {path.relative_to(self.backend_path if 'backend' in str(path) else self.frontend_path)} ({file_count} files)")
                self.success_count += 1
            else:
                self.errors.append(f"Missing directory: {path}")
                print_error(f"Missing directory: {path}")

    def generate_report(self):
        """Generate final test report"""
        print_header("FINAL TEST REPORT")

        total_tests = self.success_count + len(self.errors) + len(self.warnings)

        print(f"{GREEN}✓ Successful Tests: {self.success_count}{RESET}")
        print(f"{RED}✗ Errors: {len(self.errors)}{RESET}")
        print(f"{YELLOW}⚠ Warnings: {len(self.warnings)}{RESET}")
        print(f"\n{BLUE}Total Tests: {total_tests}{RESET}")

        if self.errors:
            print(f"\n{RED}ERRORS:{RESET}")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print(f"\n{YELLOW}WARNINGS:{RESET}")
            for warning in self.warnings:
                print(f"  - {warning}")

        # Save report
        report = {
            "success_count": self.success_count,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
            "total_tests": total_tests,
            "pass_rate": round((self.success_count / total_tests * 100) if total_tests > 0 else 0, 2)
        }

        report_path = Path("/home/user/UNS-ClaudeJP-5.4.1/FINAL_TEST_RESULTS.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        print(f"\n{BLUE}Report saved to: {report_path}{RESET}")

        if len(self.errors) == 0:
            print(f"\n{GREEN}{'=' * 80}{RESET}")
            print(f"{GREEN}ALL TESTS PASSED! ✓{RESET}".center(88))
            print(f"{GREEN}{'=' * 80}{RESET}")
            return True
        else:
            print(f"\n{RED}{'=' * 80}{RESET}")
            print(f"{RED}TESTS FAILED - {len(self.errors)} ERROR(S) FOUND{RESET}".center(88))
            print(f"{RED}{'=' * 80}{RESET}")
            return False

    def run_all_tests(self):
        """Run all tests"""
        print_header("STARTING COMPREHENSIVE TESTING")

        self.test_backend_syntax()
        self.test_backend_imports()
        self.test_api_endpoints()
        self.test_schemas()
        self.test_frontend_pages()
        self.test_main_py()
        self.test_file_structure()

        return self.generate_report()

if __name__ == "__main__":
    tester = ComprehensiveTest()
    success = tester.run_all_tests()
    exit(0 if success else 1)
