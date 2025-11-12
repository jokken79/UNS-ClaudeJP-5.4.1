#!/bin/bash
# ========================================
# JMeter Load Test Runner
# ========================================
#
# Purpose: Execute load tests against UNS-ClaudeJP backend
# Usage: ./run-load-test.sh [scenario] [duration]
# Scenarios: light (100 users), medium (1000 users), heavy (10000 users)
# Duration: Test duration in seconds (default: 300)
#
# Example: ./run-load-test.sh medium 600
#
# Author: Claude Code
# Created: 2025-11-12
# Version: 1.0.0
#
# ========================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SCENARIO=${1:-light}
DURATION=${2:-300}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_DIR="./results/${SCENARIO}_${TIMESTAMP}"
REPORT_DIR="./reports/${SCENARIO}_${TIMESTAMP}"

# JMeter configuration
JMETER_MASTER="uns-jmeter-master"
JMETER_SLAVES="uns-jmeter-slave-1,uns-jmeter-slave-2,uns-jmeter-slave-3"

# Backend URL (adjust if needed)
BACKEND_URL="http://nginx:80"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}UNS-ClaudeJP Load Testing${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Scenario:${NC} ${SCENARIO}"
echo -e "${BLUE}Duration:${NC} ${DURATION} seconds"
echo -e "${BLUE}Timestamp:${NC} ${TIMESTAMP}"
echo ""

# Step 1: Validate scenario
echo -e "${YELLOW}[1/7]${NC} Validating scenario..."
case ${SCENARIO} in
    light)
        USERS=100
        RAMP_UP=60
        TEST_PLAN="test-plans/light-load.jmx"
        ;;
    medium)
        USERS=1000
        RAMP_UP=120
        TEST_PLAN="test-plans/medium-load.jmx"
        ;;
    heavy)
        USERS=10000
        RAMP_UP=300
        TEST_PLAN="test-plans/heavy-load.jmx"
        ;;
    custom)
        USERS=${3:-500}
        RAMP_UP=${4:-60}
        TEST_PLAN="test-plans/custom-load.jmx"
        echo -e "${BLUE}Custom scenario: ${USERS} users, ${RAMP_UP}s ramp-up${NC}"
        ;;
    *)
        echo -e "${RED}ERROR: Invalid scenario '${SCENARIO}'${NC}"
        echo -e "Valid scenarios: light, medium, heavy, custom"
        exit 1
        ;;
esac
echo -e "${GREEN}✓ Scenario validated: ${USERS} users, ${RAMP_UP}s ramp-up${NC}"
echo ""

# Step 2: Check if JMeter services are running
echo -e "${YELLOW}[2/7]${NC} Checking JMeter services..."
if ! docker ps | grep -q ${JMETER_MASTER}; then
    echo -e "${YELLOW}Starting JMeter services...${NC}"
    cd "$(dirname "$0")"
    docker compose up -d
    sleep 10
fi
echo -e "${GREEN}✓ JMeter services are running${NC}"
echo ""

# Step 3: Verify backend is accessible
echo -e "${YELLOW}[3/7]${NC} Verifying backend accessibility..."
if docker exec ${JMETER_MASTER} curl -s -f "${BACKEND_URL}/api/health" > /dev/null; then
    echo -e "${GREEN}✓ Backend is accessible at ${BACKEND_URL}${NC}"
else
    echo -e "${RED}ERROR: Cannot reach backend at ${BACKEND_URL}${NC}"
    echo -e "${YELLOW}Make sure the main application is running:${NC}"
    echo -e "  docker compose --profile dev up -d"
    exit 1
fi
echo ""

# Step 4: Create results directory
echo -e "${YELLOW}[4/7]${NC} Creating results directory..."
mkdir -p ${RESULTS_DIR}
mkdir -p ${REPORT_DIR}
echo -e "${GREEN}✓ Results directory created: ${RESULTS_DIR}${NC}"
echo ""

# Step 5: Generate test plan if it doesn't exist
echo -e "${YELLOW}[5/7]${NC} Preparing test plan..."
if [ ! -f "${TEST_PLAN}" ]; then
    echo -e "${YELLOW}Generating test plan: ${TEST_PLAN}${NC}"
    ./generate-test-plan.sh ${SCENARIO} ${USERS} ${RAMP_UP} ${DURATION}
fi
echo -e "${GREEN}✓ Test plan ready: ${TEST_PLAN}${NC}"
echo ""

# Step 6: Run JMeter test
echo -e "${YELLOW}[6/7]${NC} Running JMeter load test..."
echo -e "${BLUE}This will take approximately $((RAMP_UP + DURATION)) seconds...${NC}"
echo ""

docker exec ${JMETER_MASTER} jmeter \
    -n \
    -t /tests/$(basename ${TEST_PLAN}) \
    -l /results/$(basename ${RESULTS_DIR})/results.jtl \
    -e \
    -o /reports/$(basename ${REPORT_DIR}) \
    -Jthreads=${USERS} \
    -Jrampup=${RAMP_UP} \
    -Jduration=${DURATION} \
    -Jhost=${BACKEND_URL} \
    -R ${JMETER_SLAVES}

echo ""
echo -e "${GREEN}✓ Load test completed${NC}"
echo ""

# Step 7: Generate summary report
echo -e "${YELLOW}[7/7]${NC} Generating summary report..."

# Extract key metrics from results
TOTAL_REQUESTS=$(docker exec ${JMETER_MASTER} grep -c "^[0-9]" /results/$(basename ${RESULTS_DIR})/results.jtl || echo "0")
SUCCESS_REQUESTS=$(docker exec ${JMETER_MASTER} grep ",200," /results/$(basename ${RESULTS_DIR})/results.jtl | wc -l || echo "0")
FAILED_REQUESTS=$((TOTAL_REQUESTS - SUCCESS_REQUESTS))
SUCCESS_RATE=$((SUCCESS_REQUESTS * 100 / TOTAL_REQUESTS))

cat > ${RESULTS_DIR}/summary.txt <<EOF
========================================
Load Test Summary
========================================

Test Configuration:
  Scenario: ${SCENARIO}
  Users: ${USERS}
  Ramp-up: ${RAMP_UP} seconds
  Duration: ${DURATION} seconds
  Timestamp: ${TIMESTAMP}

Results:
  Total Requests: ${TOTAL_REQUESTS}
  Successful: ${SUCCESS_REQUESTS}
  Failed: ${FAILED_REQUESTS}
  Success Rate: ${SUCCESS_RATE}%

Reports:
  JTL Results: ${RESULTS_DIR}/results.jtl
  HTML Report: ${REPORT_DIR}/index.html
  Summary: ${RESULTS_DIR}/summary.txt

View HTML Report:
  Open in browser: ${REPORT_DIR}/index.html
  Or run: xdg-open ${REPORT_DIR}/index.html

========================================
EOF

echo -e "${GREEN}✓ Summary report generated${NC}"
echo ""

# Display summary
cat ${RESULTS_DIR}/summary.txt

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Load test completed successfully!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "  1. Open HTML report: ${YELLOW}${REPORT_DIR}/index.html${NC}"
echo -e "  2. View raw results: ${YELLOW}${RESULTS_DIR}/results.jtl${NC}"
echo -e "  3. Check Grafana: ${YELLOW}http://localhost:3002${NC} (admin/admin)"
echo -e "  4. Compare with previous tests in: ${YELLOW}./results/${NC}"
echo ""
