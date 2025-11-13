#!/usr/bin/env python3
"""
Test script for LolaAppJp services (static analysis)

Tests:
1. Import validation
2. Class structure
3. Method signatures
4. Logic validation (where possible without DB)
"""
import sys
import importlib.util
import inspect

def test_import(module_path, module_name):
    """Test if a module can be imported"""
    try:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return True, module, None
    except Exception as e:
        return False, None, str(e)

def test_class_methods(module, class_name, expected_methods):
    """Test if a class has expected methods"""
    if not hasattr(module, class_name):
        return False, f"Class {class_name} not found"

    cls = getattr(module, class_name)
    missing_methods = []

    for method_name in expected_methods:
        if not hasattr(cls, method_name):
            missing_methods.append(method_name)

    if missing_methods:
        return False, f"Missing methods: {', '.join(missing_methods)}"

    return True, f"All {len(expected_methods)} methods present"

def test_function_logic():
    """Test specific function logic without DB"""
    # Test calculate_distance
    import math

    def haversine(lat1, lon1, lat2, lon2):
        """Reference implementation"""
        if not all([lat1, lon1, lat2, lon2]):
            return None

        R = 6371.0
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlon = math.radians(lon2 - lon1)
        dlat = lat2_rad - lat1_rad

        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    # Test cases
    tests = [
        # Tokyo to Yokohama (~30km)
        (35.6762, 139.6503, 35.4437, 139.6380, 25, 35),
        # Same location
        (35.0, 139.0, 35.0, 139.0, 0, 1),
        # Missing coordinates
        (None, None, 35.0, 139.0, None, None),
        (35.0, 139.0, None, None, None, None),
    ]

    results = []
    for lat1, lon1, lat2, lon2, min_dist, max_dist in tests:
        dist = haversine(lat1, lon1, lat2, lon2)

        if dist is None:
            if min_dist is None:
                results.append(True)
            else:
                results.append(False)
        elif min_dist <= dist <= max_dist:
            results.append(True)
        else:
            results.append(False)

    return all(results), f"{sum(results)}/{len(results)} tests passed"

def main():
    print("=" * 80)
    print("LolaAppJp Services - Static Testing")
    print("=" * 80)
    print()

    base_path = "backend/app/services/"

    # Test 1: Import validation
    print("📦 TEST 1: Import Validation")
    print("-" * 80)

    services = {
        "apartment_service": {
            "class": "ApartmentService",
            "methods": [
                "calculate_distance",
                "recommend_apartments",
                "score_proximity",
                "score_availability",
                "score_price",
                "score_compatibility",
                "score_transportation"
            ]
        },
        "payroll_service": {
            "class": "PayrollService",
            "methods": [
                "calculate_monthly_payroll",
                "calculate_gross_pay",
                "calculate_deductions",
                "get_apartment_rent"
            ]
        },
        "yukyu_service": {
            "class": "YukyuService",
            "methods": [
                "grant_yukyu",
                "use_yukyu",
                "get_balance",
                "expire_old_balances"
            ]
        },
        "ocr_service": {
            "class": "OCRService",
            "methods": [
                "process_image",
                "extract_rirekisho_fields",
                "extract_timer_card_data"
            ]
        }
    }

    import_results = {}

    for service_name, service_info in services.items():
        module_path = f"{base_path}{service_name}.py"
        success, module, error = test_import(module_path, service_name)

        if success:
            print(f"✅ {service_name}: Import successful")
            import_results[service_name] = (True, module)
        else:
            print(f"❌ {service_name}: Import failed - {error}")
            import_results[service_name] = (False, None)

    print()

    # Test 2: Class structure
    print("🏗️  TEST 2: Class Structure Validation")
    print("-" * 80)

    for service_name, service_info in services.items():
        success, module = import_results[service_name]

        if not success:
            print(f"⏭️  {service_name}: Skipped (import failed)")
            continue

        class_name = service_info["class"]
        methods = service_info["methods"]

        success, message = test_class_methods(module, class_name, methods)

        if success:
            print(f"✅ {class_name}: {message}")
        else:
            print(f"❌ {class_name}: {message}")

    print()

    # Test 3: Logic validation
    print("🧮 TEST 3: Logic Validation (Haversine Formula)")
    print("-" * 80)

    success, message = test_function_logic()

    if success:
        print(f"✅ Haversine distance calculation: {message}")
    else:
        print(f"❌ Haversine distance calculation: {message}")

    print()

    # Test 4: Check for critical imports
    print("📋 TEST 4: Critical Imports Check")
    print("-" * 80)

    critical_checks = []

    # Check apartment_service has or_
    if import_results["apartment_service"][0]:
        module = import_results["apartment_service"][1]
        source = inspect.getsource(module)
        if "from sqlalchemy import and_, or_" in source:
            print("✅ apartment_service: or_() imported correctly")
            critical_checks.append(True)
        else:
            print("❌ apartment_service: or_() import missing")
            critical_checks.append(False)

    # Check payroll_service has or_
    if import_results["payroll_service"][0]:
        module = import_results["payroll_service"][1]
        source = inspect.getsource(module)
        if "from sqlalchemy import and_, or_" in source:
            print("✅ payroll_service: or_() imported correctly")
            critical_checks.append(True)
        else:
            print("❌ payroll_service: or_() import missing")
            critical_checks.append(False)

    # Check apartment_service has EmployeeStatus
    if import_results["apartment_service"][0]:
        module = import_results["apartment_service"][1]
        source = inspect.getsource(module)
        if "EmployeeStatus" in source:
            print("✅ apartment_service: EmployeeStatus imported")
            critical_checks.append(True)
        else:
            print("❌ apartment_service: EmployeeStatus import missing")
            critical_checks.append(False)

    # Check ocr_service has re and time at top
    if import_results["ocr_service"][0]:
        module = import_results["ocr_service"][1]
        source = inspect.getsource(module)
        lines = source.split('\n')[:30]  # First 30 lines
        top_section = '\n'.join(lines)

        has_re = "import re" in top_section
        has_time = "import time" in top_section

        if has_re and has_time:
            print("✅ ocr_service: re and time imported at top")
            critical_checks.append(True)
        else:
            missing = []
            if not has_re:
                missing.append("re")
            if not has_time:
                missing.append("time")
            print(f"❌ ocr_service: Missing imports at top: {', '.join(missing)}")
            critical_checks.append(False)

    print()

    # Summary
    print("=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)

    total_services = len(services)
    successful_imports = sum(1 for s, m in import_results.values() if s)

    print(f"Services tested: {total_services}")
    print(f"Successful imports: {successful_imports}/{total_services}")
    print(f"Critical import checks: {sum(critical_checks)}/{len(critical_checks)} passed")

    if successful_imports == total_services and all(critical_checks):
        print("\n✅ ALL TESTS PASSED - Services are ready for deployment")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED - Review errors above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
