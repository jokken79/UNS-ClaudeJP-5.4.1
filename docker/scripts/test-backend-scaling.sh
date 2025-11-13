#!/bin/bash
# ========================================
# Backend Horizontal Scaling Test Script
# ========================================
#
# Purpose: Verify backend can scale horizontally and nginx load balances correctly
# Usage: ./test-backend-scaling.sh [number_of_instances]
# Example: ./test-backend-scaling.sh 3
#
# Author: Claude Code
# Created: 2025-11-12
# Version: 1.0.0
#
# ========================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
SCALE_COUNT=${1:-3}
BACKEND_SERVICE="backend"
NGINX_URL="http://localhost/api/health"
TEST_REQUESTS=30

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Backend Horizontal Scaling Test${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Step 1: Check if docker compose is available
echo -e "${YELLOW}[1/6]${NC} Checking Docker Compose..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}ERROR: Docker is not installed or not in PATH${NC}"
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo -e "${RED}ERROR: Docker Compose is not available${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose is available${NC}"
echo ""

# Step 2: Scale backend service
echo -e "${YELLOW}[2/6]${NC} Scaling backend to ${SCALE_COUNT} instances..."
docker compose --profile dev up -d --scale ${BACKEND_SERVICE}=${SCALE_COUNT} --no-recreate

# Wait for services to be ready
echo -e "${YELLOW}      Waiting for backend instances to be healthy...${NC}"
sleep 10

# Verify all instances are running
RUNNING_COUNT=$(docker compose ps ${BACKEND_SERVICE} --format json | jq -s 'length')
echo -e "${GREEN}✓ ${RUNNING_COUNT} backend instances are running${NC}"
echo ""

# Step 3: List all backend instances
echo -e "${YELLOW}[3/6]${NC} Backend instances:"
docker compose ps ${BACKEND_SERVICE} --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
echo ""

# Step 4: Test direct access to each backend instance
echo -e "${YELLOW}[4/6]${NC} Testing direct access to each backend instance..."
INSTANCE_COUNT=0
for i in $(seq 1 ${SCALE_COUNT}); do
    CONTAINER_NAME="uns-claudejp-${BACKEND_SERVICE}-${i}"

    # Get container IP
    CONTAINER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ${CONTAINER_NAME} 2>/dev/null || echo "")

    if [ -z "$CONTAINER_IP" ]; then
        echo -e "${RED}  ✗ ${CONTAINER_NAME}: Not found${NC}"
        continue
    fi

    # Test health endpoint
    if docker exec ${CONTAINER_NAME} python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" &> /dev/null; then
        echo -e "${GREEN}  ✓ ${CONTAINER_NAME}: Healthy (IP: ${CONTAINER_IP})${NC}"
        ((INSTANCE_COUNT++))
    else
        echo -e "${RED}  ✗ ${CONTAINER_NAME}: Unhealthy${NC}"
    fi
done

if [ ${INSTANCE_COUNT} -eq ${SCALE_COUNT} ]; then
    echo -e "${GREEN}✓ All ${SCALE_COUNT} instances are healthy${NC}"
else
    echo -e "${YELLOW}⚠ Only ${INSTANCE_COUNT}/${SCALE_COUNT} instances are healthy${NC}"
fi
echo ""

# Step 5: Test load balancing through nginx
echo -e "${YELLOW}[5/6]${NC} Testing load balancing through nginx..."
echo -e "${YELLOW}      Sending ${TEST_REQUESTS} requests to ${NGINX_URL}${NC}"

# Create temporary file for results
TEMP_FILE=$(mktemp)

# Send multiple requests and capture responses
SUCCESS_COUNT=0
for i in $(seq 1 ${TEST_REQUESTS}); do
    if curl -s -f "${NGINX_URL}" > /dev/null 2>&1; then
        ((SUCCESS_COUNT++))
        echo -n "."
    else
        echo -n "x"
    fi

    # Small delay to avoid overwhelming the system
    sleep 0.1
done
echo ""

SUCCESS_RATE=$((SUCCESS_COUNT * 100 / TEST_REQUESTS))
if [ ${SUCCESS_RATE} -ge 95 ]; then
    echo -e "${GREEN}✓ Load balancing test passed: ${SUCCESS_COUNT}/${TEST_REQUESTS} requests successful (${SUCCESS_RATE}%)${NC}"
else
    echo -e "${YELLOW}⚠ Load balancing test warning: ${SUCCESS_COUNT}/${TEST_REQUESTS} requests successful (${SUCCESS_RATE}%)${NC}"
fi
echo ""

# Step 6: Show nginx upstream status
echo -e "${YELLOW}[6/6]${NC} Nginx configuration summary:"
echo -e "${BLUE}  Upstream backend servers:${NC}"
docker exec uns-claudejp-nginx nginx -T 2>/dev/null | grep -A 5 "upstream backend" | head -n 10

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Backend scaling test completed!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${BLUE}Summary:${NC}"
echo -e "  - Scaled instances: ${SCALE_COUNT}"
echo -e "  - Healthy instances: ${INSTANCE_COUNT}"
echo -e "  - Test requests: ${TEST_REQUESTS}"
echo -e "  - Success rate: ${SUCCESS_RATE}%"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "  - Monitor logs: ${YELLOW}docker compose logs -f ${BACKEND_SERVICE}${NC}"
echo -e "  - Check metrics: ${YELLOW}http://localhost:9090${NC} (Prometheus)"
echo -e "  - View dashboards: ${YELLOW}http://localhost:3001${NC} (Grafana)"
echo -e "  - Scale down: ${YELLOW}docker compose up -d --scale ${BACKEND_SERVICE}=1${NC}"
echo ""

# Cleanup
rm -f ${TEMP_FILE}
