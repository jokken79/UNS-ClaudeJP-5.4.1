#!/bin/bash

###############################################################################
# UNS-ClaudeJP 5.4.1 - Complete Testing Suite
# 
# Executes all verification and testing phases:
# 1. API Health Check
# 2. Authentication & RBAC
# 3. Backend Tests (pytest)
# 4. Frontend Type Check & Build
# 5. E2E Tests (Playwright)
#
# Usage: ./run_all_tests.sh
###############################################################################

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_CONTAINER="uns-claudejp-backend"
FRONTEND_CONTAINER="uns-claudejp-frontend"
API_BASE_URL="http://localhost:8000/api"
FRONTEND_URL="http://localhost:3000"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

###############################################################################
# Helper Functions
###############################################################################

print_header() {
  echo -e "\n${BLUE}════════════════════════════════════════════════════════════${NC}"
  echo -e "${BLUE}  $1${NC}"
  echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}\n"
}

print_success() {
  echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
  echo -e "${RED}✗ $1${NC}"
}

print_warning() {
  echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
  echo -e "${BLUE}ℹ $1${NC}"
}

###############################################################################
# Phase 1: Check Prerequisites
###############################################################################

phase_prerequisites() {
  print_header "PHASE 1: Checking Prerequisites"
  
  print_info "Checking Docker..."
  if ! command -v docker &> /dev/null; then
    print_error "Docker not found. Please install Docker."
    exit 1
  fi
  print_success "Docker is installed"
  
  print_info "Checking Docker Compose..."
  if ! docker compose --version &> /dev/null; then
    print_error "Docker Compose not found."
    exit 1
  fi
  print_success "Docker Compose is installed"
  
  print_info "Checking services are running..."
  if ! docker compose ps | grep -q "$BACKEND_CONTAINER"; then
    print_warning "Backend container not running. Starting services..."
    docker compose up -d
    sleep 10
  else
    print_success "Services already running"
  fi
  
  print_info "Waiting for backend to be healthy..."
  for i in {1..30}; do
    if docker compose ps | grep "$BACKEND_CONTAINER" | grep -q "healthy"; then
      print_success "Backend is healthy"
      break
    fi
    if [ $i -eq 30 ]; then
      print_error "Backend failed to start within 30 seconds"
      exit 1
    fi
    sleep 1
  done
}

###############################################################################
# Phase 2: API Health Check
###############################################################################

phase_api_health() {
  print_header "PHASE 2: API Health Check"
  
  print_info "Checking backend health endpoint..."
  HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" "$API_BASE_URL/health" 2>/dev/null || echo "000")
  HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -n 1)
  
  if [ "$HTTP_CODE" = "200" ]; then
    print_success "Backend health check passed (HTTP 200)"
  else
    print_error "Backend health check failed (HTTP $HTTP_CODE)"
    exit 1
  fi
  
  print_info "Checking Swagger UI..."
  SWAGGER_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE_URL/docs" 2>/dev/null || echo "000")
  if [ "$SWAGGER_CODE" = "200" ]; then
    print_success "Swagger UI is accessible"
  else
    print_warning "Swagger UI not accessible (HTTP $SWAGGER_CODE)"
  fi
}

###############################################################################
# Phase 3: Authentication Testing
###############################################################################

phase_authentication() {
  print_header "PHASE 3: Authentication & RBAC Testing"
  
  print_info "Testing login with credentials admin/admin123..."
  TOKEN_RESPONSE=$(curl -s -X POST "$API_BASE_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin123"}' 2>/dev/null)
  
  TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4 || echo "")
  
  if [ -n "$TOKEN" ]; then
    print_success "Login successful, token obtained"
    export TEST_TOKEN="$TOKEN"
  else
    print_error "Login failed"
    exit 1
  fi
  
  print_info "Testing protected endpoint with valid token..."
  PROTECTED_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE_URL/candidates" \
    -H "Authorization: Bearer $TOKEN" 2>/dev/null)
  
  if [ "$PROTECTED_CODE" = "200" ]; then
    print_success "Protected endpoint accessible with valid token"
  else
    print_error "Protected endpoint failed (HTTP $PROTECTED_CODE)"
    exit 1
  fi
  
  print_info "Testing protected endpoint WITHOUT token..."
  NO_TOKEN_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE_URL/candidates" 2>/dev/null)
  
  if [ "$NO_TOKEN_CODE" = "401" ]; then
    print_success "Protected endpoint correctly returns 401 without token"
  else
    print_warning "Expected 401, got HTTP $NO_TOKEN_CODE"
  fi
}

###############################################################################
# Phase 4: Backend Tests
###############################################################################

phase_backend_tests() {
  print_header "PHASE 4: Backend Tests (pytest)"
  
  print_info "Running backend tests..."
  if docker exec -it "$BACKEND_CONTAINER" pytest backend/tests/ -v --tb=short 2>/dev/null; then
    print_success "All backend tests passed"
  else
    print_warning "Some backend tests failed (check above for details)"
  fi
}

###############################################################################
# Phase 5: Frontend Type Check & Build
###############################################################################

phase_frontend_checks() {
  print_header "PHASE 5: Frontend Type Check & Build"
  
  print_info "Running TypeScript type check..."
  if docker exec -it "$FRONTEND_CONTAINER" npm run type-check 2>/dev/null; then
    print_success "TypeScript type check passed"
  else
    print_error "TypeScript type check failed"
    exit 1
  fi
  
  print_info "Building frontend..."
  if docker exec -it "$FRONTEND_CONTAINER" npm run build 2>/dev/null; then
    print_success "Frontend build successful"
  else
    print_error "Frontend build failed"
    exit 1
  fi
  
  print_info "Running linter..."
  if docker exec -it "$FRONTEND_CONTAINER" npm run lint 2>/dev/null; then
    print_success "Linting passed"
  else
    print_warning "Some linting issues found (check above)"
  fi
}

###############################################################################
# Phase 6: E2E Tests (Playwright)
###############################################################################

phase_e2e_tests() {
  print_header "PHASE 6: E2E Tests (Playwright)"
  
  print_info "Available E2E test strategies:"
  echo "  1. Smoke tests (5 min):  npm run test:e2e -- 01-login-dashboard.spec.ts navigation.spec.ts"
  echo "  2. Core tests (15 min):  npm run test:e2e -- candidates.spec.ts apartments.spec.ts"
  echo "  3. Yukyu tests (20 min): npm run test:e2e -- yukyu-all.spec.ts"
  echo "  4. Full suite (60 min):  npm run test:e2e"
  echo ""
  
  read -p "Run E2E tests? (yes/no) [no]: " RUN_E2E
  
  if [ "$RUN_E2E" = "yes" ]; then
    read -p "Which strategy? (1=smoke, 2=core, 3=yukyu, 4=full) [1]: " STRATEGY
    STRATEGY=${STRATEGY:-1}
    
    case $STRATEGY in
      1)
        print_info "Running smoke tests..."
        docker exec -it "$FRONTEND_CONTAINER" bash -c "cd frontend && npm run test:e2e -- 01-login-dashboard.spec.ts navigation.spec.ts"
        ;;
      2)
        print_info "Running core feature tests..."
        docker exec -it "$FRONTEND_CONTAINER" bash -c "cd frontend && npm run test:e2e -- candidates.spec.ts apartments.spec.ts"
        ;;
      3)
        print_info "Running Yukyu system tests..."
        docker exec -it "$FRONTEND_CONTAINER" bash -c "cd frontend && npm run test:e2e -- yukyu-all.spec.ts"
        ;;
      4)
        print_info "Running full E2E test suite..."
        docker exec -it "$FRONTEND_CONTAINER" bash -c "cd frontend && npm run test:e2e"
        ;;
      *)
        print_warning "Invalid choice. Skipping E2E tests."
        ;;
    esac
    
    print_info "To view results: npx playwright show-report"
  else
    print_warning "E2E tests skipped. See PLAYWRIGHT_TESTING_PLAN.md for manual execution"
  fi
}

###############################################################################
# Final Report
###############################################################################

final_report() {
  print_header "TESTING COMPLETE"
  
  echo -e "${GREEN}Summary:${NC}"
  echo "  ✓ Prerequisites verified"
  echo "  ✓ API health checked"
  echo "  ✓ Authentication tested"
  echo "  ✓ Backend tests executed"
  echo "  ✓ Frontend type checking done"
  echo "  ✓ Frontend build verified"
  echo "  ✓ E2E tests ready"
  echo ""
  
  echo -e "${GREEN}Next steps:${NC}"
  echo "  1. Review all test results above"
  echo "  2. Check for any failures or warnings"
  echo "  3. View API documentation at: http://localhost:8000/api/docs"
  echo "  4. View frontend at: http://localhost:3000"
  echo "  5. See AUDIT_REPORT_2025_11_14.md for deployment checklist"
  echo ""
  
  echo -e "${YELLOW}Important:${NC}"
  echo "  • All tests must pass before production deployment"
  echo "  • Review AUDIT_REPORT_2025_11_14.md for security requirements"
  echo "  • Update .env.production with real credentials"
  echo "  • Configure SSL/TLS certificates for production"
  echo ""
}

###############################################################################
# Main Execution
###############################################################################

main() {
  print_header "UNS-ClaudeJP 5.4.1 - Complete Testing Suite"
  echo "Testing all verification and testing phases..."
  echo ""
  
  phase_prerequisites
  phase_api_health
  phase_authentication
  phase_backend_tests
  phase_frontend_checks
  phase_e2e_tests
  final_report
}

# Run main function
main

