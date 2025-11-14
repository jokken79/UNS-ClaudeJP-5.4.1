#!/usr/bin/env python3
"""
Deep Bug Analysis - LolaAppJp Implementation

Searches for:
1. Common Python bugs (missing imports, wrong types, logic errors)
2. API inconsistencies
3. Frontend-backend mismatches
4. Security issues
5. Data validation problems
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple

# Colors
RED = '\033[91m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
BLUE = '\033[94m'
RESET = '\033[0m'

class BugHunter:
    def __init__(self):
        self.backend_path = Path("/home/user/UNS-ClaudeJP-5.4.1/LolaAppJpnew/backend")
        self.frontend_path = Path("/home/user/UNS-ClaudeJP-5.4.1/LolaAppJpnew/frontend")
        self.bugs = []
        self.warnings = []
        self.suggestions = []

    def print_header(self, text):
        print(f"\n{BLUE}{'=' * 80}{RESET}")
        print(f"{BLUE}{text.center(80)}{RESET}")
        print(f"{BLUE}{'=' * 80}{RESET}\n")

    def print_bug(self, severity, file, line, issue):
        color = RED if severity == "BUG" else YELLOW
        print(f"{color}[{severity}] {file}:{line}{RESET}")
        print(f"  → {issue}\n")

    def check_missing_error_handling(self):
        """Check for database operations without try-catch"""
        self.print_header("CHECKING ERROR HANDLING")

        api_files = list((self.backend_path / "app" / "api").glob("*.py"))

        for api_file in api_files:
            if api_file.name == "__init__.py":
                continue

            with open(api_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

                # Check for db.commit() without error handling
                for i, line in enumerate(lines, 1):
                    if 'db.commit()' in line:
                        # Look for try-except block
                        start = max(0, i - 10)
                        block = '\n'.join(lines[start:i])

                        if 'try:' not in block and 'except' not in block:
                            self.warnings.append({
                                'file': api_file.name,
                                'line': i,
                                'issue': 'db.commit() without try-except - could cause unhandled errors'
                            })
                            self.print_bug("WARNING", api_file.name, i,
                                         "db.commit() without error handling")

    def check_sql_injection_risks(self):
        """Check for potential SQL injection vulnerabilities"""
        self.print_header("CHECKING SQL INJECTION RISKS")

        api_files = list((self.backend_path / "app" / "api").glob("*.py"))
        service_files = list((self.backend_path / "app" / "services").glob("*.py"))

        all_files = api_files + service_files

        dangerous_patterns = [
            (r'\.filter\([^)]*%s', 'String formatting in filter() - use parameters instead'),
            (r'\.filter\([^)]*\.format\(', 'String .format() in filter() - use parameters instead'),
            (r'f".*SELECT.*{', 'F-string in SQL query - potential injection risk'),
        ]

        for file in all_files:
            if file.name == "__init__.py":
                continue

            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

                for i, line in enumerate(lines, 1):
                    for pattern, issue in dangerous_patterns:
                        if re.search(pattern, line):
                            self.bugs.append({
                                'file': file.name,
                                'line': i,
                                'issue': issue
                            })
                            self.print_bug("BUG", file.name, i, issue)

    def check_authentication_bypass(self):
        """Check for endpoints without authentication"""
        self.print_header("CHECKING AUTHENTICATION")

        api_files = list((self.backend_path / "app" / "api").glob("*.py"))

        for api_file in api_files:
            if api_file.name in ["__init__.py", "auth.py"]:
                continue

            with open(api_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

                in_endpoint = False
                endpoint_line = 0
                has_auth = False

                for i, line in enumerate(lines, 1):
                    if '@router.' in line and ('get' in line or 'post' in line or 'put' in line or 'delete' in line):
                        # Check if previous endpoint had auth
                        if in_endpoint and not has_auth:
                            self.bugs.append({
                                'file': api_file.name,
                                'line': endpoint_line,
                                'issue': 'Endpoint without authentication check (missing get_current_active_user)'
                            })
                            self.print_bug("BUG", api_file.name, endpoint_line,
                                         "Endpoint without authentication")

                        in_endpoint = True
                        endpoint_line = i
                        has_auth = False

                    if 'get_current_active_user' in line or 'get_current_user' in line:
                        has_auth = True

    def check_cors_configuration(self):
        """Check CORS configuration"""
        self.print_header("CHECKING CORS CONFIGURATION")

        main_py = self.backend_path / "app" / "main.py"

        if main_py.exists():
            with open(main_py, 'r', encoding='utf-8') as f:
                content = f.read()

                if 'allow_origins=["*"]' in content or 'allow_origins = ["*"]' in content:
                    self.warnings.append({
                        'file': 'main.py',
                        'line': 0,
                        'issue': 'CORS allows all origins (*) - security risk in production'
                    })
                    self.print_bug("WARNING", "main.py", "N/A",
                                 "CORS allows all origins - should restrict in production")
                else:
                    print(f"{GREEN}✓ CORS properly configured{RESET}")

    def check_password_security(self):
        """Check password handling"""
        self.print_header("CHECKING PASSWORD SECURITY")

        auth_files = [
            self.backend_path / "app" / "api" / "auth.py",
            self.backend_path / "app" / "core" / "security.py"
        ]

        for file in auth_files:
            if file.exists():
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # Check for plaintext password storage
                    if re.search(r'password\s*=\s*["\']', content):
                        self.bugs.append({
                            'file': file.name,
                            'line': 0,
                            'issue': 'Possible plaintext password storage'
                        })
                        self.print_bug("BUG", file.name, "N/A",
                                     "Possible plaintext password storage")

                    # Check for weak password hashing
                    if 'md5' in content.lower() or 'sha1' in content.lower():
                        self.bugs.append({
                            'file': file.name,
                            'line': 0,
                            'issue': 'Weak password hashing algorithm (use bcrypt/argon2)'
                        })
                        self.print_bug("BUG", file.name, "N/A",
                                     "Weak password hashing")

    def check_type_consistency(self):
        """Check type consistency between schemas and APIs"""
        self.print_header("CHECKING TYPE CONSISTENCY")

        # Check if employee_id is consistently int vs str
        issues_found = False

        schema_files = list((self.backend_path / "app" / "schemas").glob("*.py"))

        for schema_file in schema_files:
            with open(schema_file, 'r', encoding='utf-8') as f:
                content = f.read()

                # Check for mixed int/str employee_id
                if 'employee_id: str' in content and 'employee_id: int' in content:
                    self.bugs.append({
                        'file': schema_file.name,
                        'line': 0,
                        'issue': 'Inconsistent employee_id type (both str and int)'
                    })
                    self.print_bug("BUG", schema_file.name, "N/A",
                                 "Inconsistent employee_id type")
                    issues_found = True

        if not issues_found:
            print(f"{GREEN}✓ Type consistency looks good{RESET}")

    def check_frontend_api_urls(self):
        """Check if frontend API URLs are correct"""
        self.print_header("CHECKING FRONTEND API URLS")

        frontend_pages = list(self.frontend_path.rglob("page.tsx"))

        issues_found = False

        for page in frontend_pages:
            with open(page, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

                for i, line in enumerate(lines, 1):
                    # Check for hardcoded localhost
                    if 'localhost:8000' in line:
                        self.suggestions.append({
                            'file': str(page.relative_to(self.frontend_path)),
                            'line': i,
                            'issue': 'Hardcoded localhost URL - should use environment variable'
                        })

                    # Check for incorrect API paths
                    if 'fetch(' in line and '/api/' in line:
                        # Extract URL
                        match = re.search(r'fetch\([\'"]([^\'"]+)[\'"]', line)
                        if match:
                            url = match.group(1)
                            if not url.startswith('http'):
                                continue

                            # Check if endpoint exists in backend
                            path = url.split('/api/')[-1] if '/api/' in url else ''
                            if path and not self._endpoint_exists(path):
                                self.warnings.append({
                                    'file': str(page.relative_to(self.frontend_path)),
                                    'line': i,
                                    'issue': f'API endpoint may not exist: {path}'
                                })
                                issues_found = True

        if not issues_found:
            print(f"{GREEN}✓ Frontend API URLs look correct{RESET}")

    def _endpoint_exists(self, path: str) -> bool:
        """Check if an endpoint exists in backend"""
        # Simple check - look for the router file
        parts = path.split('/')
        if not parts:
            return True

        router_name = parts[0]
        router_file = self.backend_path / "app" / "api" / f"{router_name}.py"

        return router_file.exists()

    def check_infinite_loops(self):
        """Check for potential infinite loops"""
        self.print_header("CHECKING INFINITE LOOPS")

        python_files = list(self.backend_path.rglob("*.py"))

        issues_found = False

        for py_file in python_files:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

                for i, line in enumerate(lines, 1):
                    # Check for while True without timeout
                    if 'while True:' in line:
                        # Look ahead for timeout or break
                        next_20_lines = '\n'.join(lines[i:i+20])

                        if 'timeout' not in next_20_lines and 'max_attempts' not in next_20_lines:
                            self.warnings.append({
                                'file': str(py_file.relative_to(self.backend_path)),
                                'line': i,
                                'issue': 'while True without timeout protection'
                            })
                            self.print_bug("WARNING", str(py_file.relative_to(self.backend_path)), i,
                                         "while True without timeout")
                            issues_found = True

        if not issues_found:
            print(f"{GREEN}✓ No infinite loop risks found{RESET}")

    def generate_report(self):
        """Generate final bug report"""
        self.print_header("BUG ANALYSIS REPORT")

        total_issues = len(self.bugs) + len(self.warnings) + len(self.suggestions)

        print(f"{RED}Critical Bugs: {len(self.bugs)}{RESET}")
        print(f"{YELLOW}Warnings: {len(self.warnings)}{RESET}")
        print(f"{BLUE}Suggestions: {len(self.suggestions)}{RESET}")
        print(f"\nTotal Issues: {total_issues}")

        if self.bugs:
            print(f"\n{RED}CRITICAL BUGS:{RESET}")
            for bug in self.bugs[:10]:  # Show first 10
                print(f"  - {bug['file']}:{bug['line']} - {bug['issue']}")

        if self.warnings:
            print(f"\n{YELLOW}WARNINGS:{RESET}")
            for warning in self.warnings[:10]:
                print(f"  - {warning['file']}:{warning['line']} - {warning['issue']}")

        if len(self.bugs) == 0:
            print(f"\n{GREEN}{'=' * 80}{RESET}")
            print(f"{GREEN}NO CRITICAL BUGS FOUND! ✓{RESET}".center(88))
            print(f"{GREEN}{'=' * 80}{RESET}")
            return True
        else:
            print(f"\n{RED}{'=' * 80}{RESET}")
            print(f"{RED}FOUND {len(self.bugs)} CRITICAL BUG(S)!{RESET}".center(88))
            print(f"{RED}{'=' * 80}{RESET}")
            return False

    def run_all_checks(self):
        """Run all bug checks"""
        self.check_missing_error_handling()
        self.check_sql_injection_risks()
        self.check_authentication_bypass()
        self.check_cors_configuration()
        self.check_password_security()
        self.check_type_consistency()
        self.check_frontend_api_urls()
        self.check_infinite_loops()

        return self.generate_report()

if __name__ == "__main__":
    hunter = BugHunter()
    success = hunter.run_all_checks()
    exit(0 if success else 1)
