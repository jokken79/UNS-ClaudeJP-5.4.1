#!/usr/bin/env python3
"""
Simple Importer - Basic initialization without resilience framework dependencies
"""

import subprocess
import sys
import time

def run_command(cmd, description):
    """Run a command and log the result"""
    print(f"\n[*] {description}...")
    print(f"    Command: {cmd}")

    result = subprocess.run(cmd, shell=True, cwd="/app")

    if result.returncode == 0:
        print(f"    [OK] {description} completed successfully")
        return True
    else:
        print(f"    [!] {description} had errors (exit code: {result.returncode})")
        # Don't fail on non-critical operations
        return False

def main():
    print("\n" + "="*80)
    print("                    SIMPLE IMPORTER")
    print("                 Database Initialization")
    print("="*80)

    # Critical operations
    critical_ops = [
        ("alembic upgrade head", "Running Alembic migrations"),
        ("python scripts/create_admin_user.py", "Creating admin user"),
    ]

    # Non-critical operations
    non_critical_ops = [
        ("python scripts/import_data.py 2>/dev/null || true", "Importing demo data"),
        ("python scripts/sync_candidate_employee_status.py 2>/dev/null || true", "Syncing candidates"),
    ]

    # Run critical operations
    print("\n[*] Running critical operations...")
    for cmd, desc in critical_ops:
        if not run_command(cmd, desc):
            print(f"\n[X] CRITICAL ERROR: {desc} failed")
            print("[X] Database initialization incomplete")
            sys.exit(1)

    # Run non-critical operations
    print("\n[*] Running non-critical operations...")
    for cmd, desc in non_critical_ops:
        run_command(cmd, desc)  # Don't fail if these don't exist

    print("\n" + "="*80)
    print("              [OK] INITIALIZATION COMPLETED")
    print("="*80 + "\n")

    sys.exit(0)

if __name__ == "__main__":
    main()
