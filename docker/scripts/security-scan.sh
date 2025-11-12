#!/bin/bash
# ========================================
# Docker Image Security Scanning with Trivy
# ========================================
#
# Purpose: Scan Docker images for vulnerabilities using Trivy
# Usage: ./security-scan.sh [image_name] [--severity CRITICAL,HIGH]
#
# Example: ./security-scan.sh backend
#          ./security-scan.sh all
#          ./security-scan.sh backend --severity CRITICAL
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
IMAGE_NAME=${1:-all}
SEVERITY=${2:-CRITICAL,HIGH,MEDIUM}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_DIR="./logs/security-scans"
REPORT_FILE="${REPORT_DIR}/scan_${IMAGE_NAME}_${TIMESTAMP}.txt"
JSON_REPORT="${REPORT_DIR}/scan_${IMAGE_NAME}_${TIMESTAMP}.json"

# Create report directory
mkdir -p ${REPORT_DIR}

echo -e "${BLUE}========================================${NC}" | tee -a ${REPORT_FILE}
echo -e "${BLUE}Docker Image Security Scan${NC}" | tee -a ${REPORT_FILE}
echo -e "${BLUE}========================================${NC}" | tee -a ${REPORT_FILE}
echo -e "${BLUE}Image:${NC} ${IMAGE_NAME}" | tee -a ${REPORT_FILE}
echo -e "${BLUE}Severity:${NC} ${SEVERITY}" | tee -a ${REPORT_FILE}
echo -e "${BLUE}Timestamp:${NC} ${TIMESTAMP}" | tee -a ${REPORT_FILE}
echo "" | tee -a ${REPORT_FILE}

# Function to scan single image
scan_image() {
    local image=$1
    local full_image="uns-claudejp-${image}:latest"

    echo -e "${YELLOW}[Scanning]${NC} ${full_image}..." | tee -a ${REPORT_FILE}

    # Check if image exists
    if ! docker images | grep -q "uns-claudejp-${image}"; then
        echo -e "${RED}[ERROR]${NC} Image ${full_image} not found. Build it first." | tee -a ${REPORT_FILE}
        return 1
    fi

    # Run Trivy scan
    echo -e "${BLUE}Running Trivy scan...${NC}" | tee -a ${REPORT_FILE}

    # HTML report
    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
        -v $(pwd)/${REPORT_DIR}:/reports \
        aquasec/trivy:latest image \
        --severity ${SEVERITY} \
        --format template \
        --template "@contrib/html.tpl" \
        --output /reports/scan_${image}_${TIMESTAMP}.html \
        ${full_image}

    # JSON report (for parsing)
    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
        -v $(pwd)/${REPORT_DIR}:/reports \
        aquasec/trivy:latest image \
        --severity ${SEVERITY} \
        --format json \
        --output /reports/scan_${image}_${TIMESTAMP}.json \
        ${full_image}

    # Console output with summary
    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
        aquasec/trivy:latest image \
        --severity ${SEVERITY} \
        ${full_image} | tee -a ${REPORT_FILE}

    # Count vulnerabilities
    local critical=$(grep -c "CRITICAL" ${REPORT_FILE} || echo "0")
    local high=$(grep -c "HIGH" ${REPORT_FILE} || echo "0")
    local medium=$(grep -c "MEDIUM" ${REPORT_FILE} || echo "0")

    echo "" | tee -a ${REPORT_FILE}
    echo -e "${BLUE}========================================${NC}" | tee -a ${REPORT_FILE}
    echo -e "${BLUE}Scan Summary for ${image}:${NC}" | tee -a ${REPORT_FILE}
    echo -e "${BLUE}========================================${NC}" | tee -a ${REPORT_FILE}
    echo -e "Critical vulnerabilities: ${critical}" | tee -a ${REPORT_FILE}
    echo -e "High vulnerabilities: ${high}" | tee -a ${REPORT_FILE}
    echo -e "Medium vulnerabilities: ${medium}" | tee -a ${REPORT_FILE}
    echo -e "${BLUE}========================================${NC}" | tee -a ${REPORT_FILE}
    echo "" | tee -a ${REPORT_FILE}

    # HTML report location
    echo -e "${GREEN}[OK]${NC} HTML report: ${REPORT_DIR}/scan_${image}_${TIMESTAMP}.html" | tee -a ${REPORT_FILE}
    echo -e "${GREEN}[OK]${NC} JSON report: ${REPORT_DIR}/scan_${image}_${TIMESTAMP}.json" | tee -a ${REPORT_FILE}
    echo "" | tee -a ${REPORT_FILE}

    # Return status based on critical vulnerabilities
    if [ ${critical} -gt 0 ]; then
        echo -e "${RED}[FAIL]${NC} Critical vulnerabilities found!" | tee -a ${REPORT_FILE}
        return 1
    elif [ ${high} -gt 5 ]; then
        echo -e "${YELLOW}[WARNING]${NC} Multiple high severity vulnerabilities found" | tee -a ${REPORT_FILE}
        return 0
    else
        echo -e "${GREEN}[PASS]${NC} No critical vulnerabilities found" | tee -a ${REPORT_FILE}
        return 0
    fi
}

# Main execution
if [ "${IMAGE_NAME}" == "all" ]; then
    echo -e "${YELLOW}[Scanning]${NC} All UNS-ClaudeJP images..." | tee -a ${REPORT_FILE}
    echo "" | tee -a ${REPORT_FILE}

    IMAGES=("backend" "frontend")
    TOTAL_CRITICAL=0
    TOTAL_HIGH=0
    TOTAL_MEDIUM=0
    FAILED_IMAGES=()

    for img in "${IMAGES[@]}"; do
        echo -e "${BLUE}========================================${NC}" | tee -a ${REPORT_FILE}
        echo -e "${BLUE}Scanning: ${img}${NC}" | tee -a ${REPORT_FILE}
        echo -e "${BLUE}========================================${NC}" | tee -a ${REPORT_FILE}
        echo "" | tee -a ${REPORT_FILE}

        if scan_image ${img}; then
            echo -e "${GREEN}✓ ${img} scan completed${NC}" | tee -a ${REPORT_FILE}
        else
            echo -e "${RED}✗ ${img} scan failed${NC}" | tee -a ${REPORT_FILE}
            FAILED_IMAGES+=("${img}")
        fi

        echo "" | tee -a ${REPORT_FILE}
        sleep 2
    done

    # Overall summary
    echo -e "${BLUE}========================================${NC}" | tee -a ${REPORT_FILE}
    echo -e "${BLUE}Overall Scan Summary${NC}" | tee -a ${REPORT_FILE}
    echo -e "${BLUE}========================================${NC}" | tee -a ${REPORT_FILE}
    echo -e "Images scanned: ${#IMAGES[@]}" | tee -a ${REPORT_FILE}
    echo -e "Images passed: $((${#IMAGES[@]} - ${#FAILED_IMAGES[@]}))" | tee -a ${REPORT_FILE}
    echo -e "Images failed: ${#FAILED_IMAGES[@]}" | tee -a ${REPORT_FILE}

    if [ ${#FAILED_IMAGES[@]} -gt 0 ]; then
        echo -e "${RED}Failed images:${NC}" | tee -a ${REPORT_FILE}
        for img in "${FAILED_IMAGES[@]}"; do
            echo -e "  - ${img}" | tee -a ${REPORT_FILE}
        done
    fi

    echo -e "${BLUE}========================================${NC}" | tee -a ${REPORT_FILE}
    echo "" | tee -a ${REPORT_FILE}

    if [ ${#FAILED_IMAGES[@]} -eq 0 ]; then
        echo -e "${GREEN}[SUCCESS]${NC} All images passed security scan!" | tee -a ${REPORT_FILE}
        exit 0
    else
        echo -e "${RED}[FAILURE]${NC} Some images have critical vulnerabilities" | tee -a ${REPORT_FILE}
        exit 1
    fi
else
    scan_image ${IMAGE_NAME}
fi

echo "" | tee -a ${REPORT_FILE}
echo -e "${BLUE}========================================${NC}" | tee -a ${REPORT_FILE}
echo -e "${GREEN}Security scan completed!${NC}" | tee -a ${REPORT_FILE}
echo -e "${BLUE}========================================${NC}" | tee -a ${REPORT_FILE}
echo "" | tee -a ${REPORT_FILE}
echo -e "${BLUE}Reports saved to:${NC}" | tee -a ${REPORT_FILE}
echo -e "  - Text: ${REPORT_FILE}" | tee -a ${REPORT_FILE}
echo -e "  - HTML: ${REPORT_DIR}/scan_${IMAGE_NAME}_${TIMESTAMP}.html" | tee -a ${REPORT_FILE}
echo -e "  - JSON: ${REPORT_DIR}/scan_${IMAGE_NAME}_${TIMESTAMP}.json" | tee -a ${REPORT_FILE}
echo "" | tee -a ${REPORT_FILE}
echo -e "${BLUE}Next steps:${NC}" | tee -a ${REPORT_FILE}
echo -e "  1. Review HTML report in browser" | tee -a ${REPORT_FILE}
echo -e "  2. Update base images if needed" | tee -a ${REPORT_FILE}
echo -e "  3. Update dependencies to patch vulnerabilities" | tee -a ${REPORT_FILE}
echo -e "  4. Re-scan after fixes" | tee -a ${REPORT_FILE}
echo "" | tee -a ${REPORT_FILE}
