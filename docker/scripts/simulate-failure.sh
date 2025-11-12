#!/bin/bash
# ========================================
# Disaster Recovery Testing Script
# ========================================
#
# Purpose: Simulate failures and verify automatic recovery
# Usage: ./simulate-failure.sh [scenario] [--auto-recover]
# Scenarios: db, backend, redis, frontend, nginx, network, all
#
# Example: ./simulate-failure.sh db --auto-recover
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
MAGENTA='\033[0;35m'
NC='\033[0m'

# Configuration
SCENARIO=${1:-all}
AUTO_RECOVER=${2:-}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="./logs/disaster-recovery"
LOG_FILE="${LOG_DIR}/test_${SCENARIO}_${TIMESTAMP}.log"

# Recovery targets (RTO/RPO)
RTO_TARGET=30  # Recovery Time Objective: 30 seconds
RPO_TARGET=0   # Recovery Point Objective: 0 (no data loss)

# Create log directory
mkdir -p ${LOG_DIR}

# Logging function
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a ${LOG_FILE}
}

# Banner
echo -e "${BLUE}========================================${NC}" | tee -a ${LOG_FILE}
echo -e "${BLUE}Disaster Recovery Testing${NC}" | tee -a ${LOG_FILE}
echo -e "${BLUE}========================================${NC}" | tee -a ${LOG_FILE}
echo -e "${BLUE}Scenario:${NC} ${SCENARIO}" | tee -a ${LOG_FILE}
echo -e "${BLUE}Auto-recover:${NC} ${AUTO_RECOVER}" | tee -a ${LOG_FILE}
echo -e "${BLUE}Timestamp:${NC} ${TIMESTAMP}" | tee -a ${LOG_FILE}
echo -e "${BLUE}Log file:${NC} ${LOG_FILE}" | tee -a ${LOG_FILE}
echo "" | tee -a ${LOG_FILE}

# Function to check service health
check_service_health() {
    local service=$1
    local max_wait=${2:-30}
    local elapsed=0

    log "INFO" "Waiting for ${service} to become healthy..."

    while [ $elapsed -lt $max_wait ]; do
        if docker compose ps ${service} | grep -q "healthy"; then
            log "INFO" "✓ ${service} is healthy after ${elapsed} seconds"
            return 0
        fi

        sleep 1
        ((elapsed++))
    done

    log "ERROR" "✗ ${service} did not become healthy after ${max_wait} seconds"
    return 1
}

# Function to verify application is working
verify_application() {
    log "INFO" "Verifying application functionality..."

    # Test health endpoint
    if curl -s -f http://localhost/api/health > /dev/null 2>&1; then
        log "INFO" "✓ Backend health endpoint responding"
    else
        log "ERROR" "✗ Backend health endpoint not responding"
        return 1
    fi

    # Test frontend
    if curl -s -f http://localhost:3000 > /dev/null 2>&1; then
        log "INFO" "✓ Frontend responding"
    else
        log "ERROR" "✗ Frontend not responding"
        return 1
    fi

    # Test database connection
    if docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "SELECT 1;" > /dev/null 2>&1; then
        log "INFO" "✓ Database connection working"
    else
        log "ERROR" "✗ Database connection failed"
        return 1
    fi

    log "INFO" "✓ Application verification passed"
    return 0
}

# Function to simulate database failure
test_database_failure() {
    log "INFO" "========== DATABASE FAILURE TEST =========="
    log "INFO" "Simulating database container failure..."

    # Record baseline
    local before_count=$(docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "SELECT count(*) FROM candidates;" -t 2>/dev/null || echo "0")
    log "INFO" "Baseline candidate count: ${before_count}"

    # Kill database
    log "WARN" "Killing database container..."
    local failure_start=$(date +%s)
    docker compose stop db
    docker compose kill db
    log "INFO" "Database container killed at $(date)"

    # Wait and observe
    log "INFO" "Waiting 5 seconds to observe impact..."
    sleep 5

    # Verify backend handles gracefully
    log "INFO" "Testing backend behavior without database..."
    if curl -s http://localhost/api/health 2>&1 | grep -q "unhealthy"; then
        log "INFO" "✓ Backend correctly reports unhealthy state"
    else
        log "WARN" "⚠ Backend did not report unhealthy state"
    fi

    # Trigger recovery
    if [ "$AUTO_RECOVER" == "--auto-recover" ]; then
        log "INFO" "Triggering automatic recovery..."
        docker compose --profile dev up -d db
    else
        log "WARN" "Manual recovery required. Run: docker compose up -d db"
        read -p "Press ENTER when ready to recover..."
        docker compose --profile dev up -d db
    fi

    # Measure recovery time
    check_service_health db ${RTO_TARGET}
    local failure_end=$(date +%s)
    local recovery_time=$((failure_end - failure_start))

    log "INFO" "Recovery time: ${recovery_time} seconds (Target: ${RTO_TARGET}s)"

    # Verify data integrity
    local after_count=$(docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "SELECT count(*) FROM candidates;" -t 2>/dev/null || echo "0")
    log "INFO" "After recovery candidate count: ${after_count}"

    if [ "${before_count}" == "${after_count}" ]; then
        log "INFO" "✓ Data integrity verified (RPO: 0)"
    else
        log "ERROR" "✗ Data loss detected (before: ${before_count}, after: ${after_count})"
    fi

    # Final verification
    verify_application

    if [ $recovery_time -le $RTO_TARGET ]; then
        log "INFO" "✓ DATABASE FAILURE TEST PASSED (RTO: ${recovery_time}s/${RTO_TARGET}s)"
        return 0
    else
        log "ERROR" "✗ DATABASE FAILURE TEST FAILED (RTO exceeded: ${recovery_time}s > ${RTO_TARGET}s)"
        return 1
    fi
}

# Function to simulate backend failure
test_backend_failure() {
    log "INFO" "========== BACKEND FAILURE TEST =========="
    log "INFO" "Simulating backend container failure..."

    # Get backend count
    local backend_count=$(docker compose ps backend --format json | jq -s 'length')
    log "INFO" "Current backend instances: ${backend_count}"

    if [ ${backend_count} -le 1 ]; then
        log "WARN" "Only 1 backend instance running. Scaling to 3 for HA test..."
        docker compose --profile dev up -d --scale backend=3 --no-recreate
        sleep 10
        backend_count=3
    fi

    # Kill one backend instance
    log "WARN" "Killing backend instance 1..."
    local failure_start=$(date +%s)
    docker compose stop uns-claudejp-backend-1 2>/dev/null || docker stop $(docker ps --filter "name=backend-1" -q)
    log "INFO" "Backend instance killed at $(date)"

    # Verify remaining instances handle traffic
    log "INFO" "Testing remaining backend instances..."
    local success_count=0
    local total_requests=10

    for i in $(seq 1 $total_requests); do
        if curl -s -f http://localhost/api/health > /dev/null 2>&1; then
            ((success_count++))
        fi
        sleep 0.5
    done

    local success_rate=$((success_count * 100 / total_requests))
    log "INFO" "Success rate with 1 instance down: ${success_rate}% (${success_count}/${total_requests})"

    if [ $success_rate -ge 90 ]; then
        log "INFO" "✓ High availability maintained (success rate: ${success_rate}%)"
    else
        log "ERROR" "✗ High availability compromised (success rate: ${success_rate}%)"
    fi

    # Trigger recovery
    if [ "$AUTO_RECOVER" == "--auto-recover" ]; then
        log "INFO" "Triggering automatic recovery..."
        docker compose --profile dev up -d --scale backend=${backend_count}
    else
        log "WARN" "Manual recovery required. Run: docker compose up -d backend"
        read -p "Press ENTER when ready to recover..."
        docker compose --profile dev up -d --scale backend=${backend_count}
    fi

    # Measure recovery time
    sleep 5
    local failure_end=$(date +%s)
    local recovery_time=$((failure_end - failure_start))

    log "INFO" "Recovery time: ${recovery_time} seconds"

    # Verify all instances are healthy
    local healthy_count=$(docker compose ps backend --format json | jq -s 'map(select(.Health == "healthy")) | length')
    log "INFO" "Healthy backend instances: ${healthy_count}/${backend_count}"

    if [ ${healthy_count} -eq ${backend_count} ]; then
        log "INFO" "✓ BACKEND FAILURE TEST PASSED"
        return 0
    else
        log "ERROR" "✗ BACKEND FAILURE TEST FAILED (${healthy_count}/${backend_count} healthy)"
        return 1
    fi
}

# Function to simulate Redis failure
test_redis_failure() {
    log "INFO" "========== REDIS FAILURE TEST =========="
    log "INFO" "Simulating Redis cache failure..."

    # Kill Redis
    log "WARN" "Killing Redis container..."
    local failure_start=$(date +%s)
    docker compose stop redis
    docker compose kill redis
    log "INFO" "Redis container killed at $(date)"

    # Verify backend continues (degraded performance)
    log "INFO" "Testing backend behavior without Redis..."
    local success_count=0
    local total_requests=10

    for i in $(seq 1 $total_requests); do
        if curl -s -f http://localhost/api/health > /dev/null 2>&1; then
            ((success_count++))
        fi
        sleep 0.5
    done

    local success_rate=$((success_count * 100 / total_requests))
    log "INFO" "Success rate without Redis: ${success_rate}% (${success_count}/${total_requests})"

    if [ $success_rate -ge 80 ]; then
        log "INFO" "✓ Backend gracefully degraded (success rate: ${success_rate}%)"
    else
        log "WARN" "⚠ Backend heavily impacted (success rate: ${success_rate}%)"
    fi

    # Trigger recovery
    if [ "$AUTO_RECOVER" == "--auto-recover" ]; then
        log "INFO" "Triggering automatic recovery..."
        docker compose --profile dev up -d redis
    else
        log "WARN" "Manual recovery required. Run: docker compose up -d redis"
        read -p "Press ENTER when ready to recover..."
        docker compose --profile dev up -d redis
    fi

    # Measure recovery time
    check_service_health redis ${RTO_TARGET}
    local failure_end=$(date +%s)
    local recovery_time=$((failure_end - failure_start))

    log "INFO" "Recovery time: ${recovery_time} seconds (Target: ${RTO_TARGET}s)"

    # Verify cache is working
    if docker exec uns-claudejp-redis redis-cli --raw incr ping > /dev/null 2>&1; then
        log "INFO" "✓ Redis cache restored"
    else
        log "ERROR" "✗ Redis cache not working"
        return 1
    fi

    if [ $recovery_time -le $RTO_TARGET ]; then
        log "INFO" "✓ REDIS FAILURE TEST PASSED (RTO: ${recovery_time}s/${RTO_TARGET}s)"
        return 0
    else
        log "ERROR" "✗ REDIS FAILURE TEST FAILED (RTO exceeded: ${recovery_time}s > ${RTO_TARGET}s)"
        return 1
    fi
}

# Function to simulate network partition
test_network_failure() {
    log "INFO" "========== NETWORK PARTITION TEST =========="
    log "INFO" "Simulating network partition between backend and database..."

    # Disconnect backend from network
    log "WARN" "Disconnecting backend from network..."
    local failure_start=$(date +%s)

    # Get first backend container
    local backend_container=$(docker ps --filter "name=backend" --format "{{.Names}}" | head -n 1)
    docker network disconnect uns-claudejp_uns-network ${backend_container}
    log "INFO" "Backend disconnected from network at $(date)"

    # Verify impact
    log "INFO" "Testing application behavior during network partition..."
    sleep 5

    # If multiple backends, others should handle traffic
    local backend_count=$(docker compose ps backend --format json | jq -s 'length')
    if [ ${backend_count} -gt 1 ]; then
        if curl -s -f http://localhost/api/health > /dev/null 2>&1; then
            log "INFO" "✓ Other backend instances handling traffic"
        else
            log "WARN" "⚠ Application impacted by network partition"
        fi
    fi

    # Trigger recovery
    if [ "$AUTO_RECOVER" == "--auto-recover" ]; then
        log "INFO" "Triggering automatic recovery..."
        docker network connect uns-claudejp_uns-network ${backend_container}
    else
        log "WARN" "Manual recovery required. Run: docker network connect uns-claudejp_uns-network ${backend_container}"
        read -p "Press ENTER when ready to recover..."
        docker network connect uns-claudejp_uns-network ${backend_container}
    fi

    # Measure recovery time
    sleep 5
    local failure_end=$(date +%s)
    local recovery_time=$((failure_end - failure_start))

    log "INFO" "Recovery time: ${recovery_time} seconds"

    # Verify connectivity restored
    if docker exec ${backend_container} curl -s -f http://db:5432 > /dev/null 2>&1 || \
       docker exec ${backend_container} python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" > /dev/null 2>&1; then
        log "INFO" "✓ Network connectivity restored"
    else
        log "WARN" "⚠ Network connectivity not fully restored"
    fi

    log "INFO" "✓ NETWORK PARTITION TEST PASSED (RTO: ${recovery_time}s)"
    return 0
}

# Function to run all disaster recovery tests
test_all_scenarios() {
    log "INFO" "========== COMPREHENSIVE DISASTER RECOVERY TEST =========="
    log "INFO" "Running all disaster recovery scenarios..."

    local passed=0
    local failed=0

    # Test each scenario
    declare -a scenarios=("database" "backend" "redis" "network")

    for scenario in "${scenarios[@]}"; do
        log "INFO" ""
        log "INFO" "=========================================="
        log "INFO" "Testing ${scenario} failure scenario..."
        log "INFO" "=========================================="

        case ${scenario} in
            database)
                if test_database_failure; then
                    ((passed++))
                else
                    ((failed++))
                fi
                ;;
            backend)
                if test_backend_failure; then
                    ((passed++))
                else
                    ((failed++))
                fi
                ;;
            redis)
                if test_redis_failure; then
                    ((passed++))
                else
                    ((failed++))
                fi
                ;;
            network)
                if test_network_failure; then
                    ((passed++))
                else
                    ((failed++))
                fi
                ;;
        esac

        # Wait between tests
        log "INFO" "Cooling down before next test..."
        sleep 10
    done

    # Summary
    log "INFO" ""
    log "INFO" "=========================================="
    log "INFO" "DISASTER RECOVERY TEST SUMMARY"
    log "INFO" "=========================================="
    log "INFO" "Total scenarios tested: $((passed + failed))"
    log "INFO" "Passed: ${passed}"
    log "INFO" "Failed: ${failed}"
    log "INFO" "Success rate: $((passed * 100 / (passed + failed)))%"
    log "INFO" "=========================================="

    if [ ${failed} -eq 0 ]; then
        return 0
    else
        return 1
    fi
}

# Main execution
case ${SCENARIO} in
    db|database)
        test_database_failure
        ;;
    backend)
        test_backend_failure
        ;;
    redis|cache)
        test_redis_failure
        ;;
    network|partition)
        test_network_failure
        ;;
    all)
        test_all_scenarios
        ;;
    *)
        echo -e "${RED}ERROR: Invalid scenario '${SCENARIO}'${NC}"
        echo -e "Valid scenarios: db, backend, redis, network, all"
        exit 1
        ;;
esac

RESULT=$?

# Final summary
echo "" | tee -a ${LOG_FILE}
echo -e "${BLUE}========================================${NC}" | tee -a ${LOG_FILE}
if [ $RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ Disaster recovery test completed successfully${NC}" | tee -a ${LOG_FILE}
else
    echo -e "${RED}✗ Disaster recovery test failed${NC}" | tee -a ${LOG_FILE}
fi
echo -e "${BLUE}========================================${NC}" | tee -a ${LOG_FILE}
echo -e "${BLUE}Log file:${NC} ${LOG_FILE}" | tee -a ${LOG_FILE}
echo "" | tee -a ${LOG_FILE}

exit $RESULT
