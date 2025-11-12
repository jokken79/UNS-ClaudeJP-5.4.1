# Docker Image Security Scanning with Trivy

## Overview

UNS-ClaudeJP 5.4.1 includes automated security vulnerability scanning for Docker images using Trivy, an open-source security scanner for containers and other artifacts.

**Version:** 1.0.0
**Last Updated:** 2025-11-12
**Author:** Claude Code

---

## Table of Contents

- [What is Trivy?](#what-is-trivy)
- [Quick Start](#quick-start)
- [Running Scans](#running-scans)
- [Understanding Reports](#understanding-reports)
- [Vulnerability Remediation](#vulnerability-remediation)
- [CI/CD Integration](#cicd-integration)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## What is Trivy?

**Trivy** is a comprehensive security scanner that detects:
- **OS package vulnerabilities** (Alpine, Debian, Ubuntu, etc.)
- **Application dependencies** (Python, Node.js, etc.)
- **Misconfigurations** (Docker, Kubernetes)
- **Secrets** (API keys, passwords)
- **Licenses** (GPL, MIT, etc.)

### Why Use Trivy?

- ✅ **Fast**: Scans complete in seconds
- ✅ **Comprehensive**: Multiple vulnerability databases
- ✅ **Easy to use**: Single command, multiple output formats
- ✅ **CI/CD friendly**: Exit codes for automation
- ✅ **Up-to-date**: Daily database updates

---

## Quick Start

### Prerequisites

- Docker installed and running
- UNS-ClaudeJP images built locally

### Run Your First Scan

**Linux/macOS:**
```bash
cd /home/user/UNS-ClaudeJP-5.4.1
./docker/scripts/security-scan.sh backend
```

**Windows:**
```cmd
cd UNS-ClaudeJP-5.4.1
scripts\SECURITY_SCAN.bat backend
```

**Expected Output:**
```
========================================
Docker Image Security Scan
========================================
Image: backend
Severity: CRITICAL,HIGH,MEDIUM
Timestamp: 20251112_143022

[Scanning] uns-claudejp-backend:latest...
Running Trivy scan...

========================================
Scan Summary for backend:
========================================
Critical vulnerabilities: 0
High vulnerabilities: 2
Medium vulnerabilities: 5
========================================

[PASS] No critical vulnerabilities found
```

---

## Running Scans

### Scan Single Image

**Backend:**
```bash
./docker/scripts/security-scan.sh backend
```

**Frontend:**
```bash
./docker/scripts/security-scan.sh frontend
```

### Scan All Images

```bash
./docker/scripts/security-scan.sh all
```

This will scan:
- uns-claudejp-backend:latest
- uns-claudejp-frontend:latest

### Scan with Custom Severity

```bash
# Only critical vulnerabilities
./docker/scripts/security-scan.sh backend --severity CRITICAL

# Critical and high only
./docker/scripts/security-scan.sh backend --severity CRITICAL,HIGH

# All severities
./docker/scripts/security-scan.sh backend --severity CRITICAL,HIGH,MEDIUM,LOW
```

### Manual Trivy Commands

**Quick scan:**
```bash
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:latest image uns-claudejp-backend:latest
```

**Scan with table format:**
```bash
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:latest image \
  --severity CRITICAL,HIGH \
  --format table \
  uns-claudejp-backend:latest
```

**Scan with JSON output:**
```bash
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:latest image \
  --format json \
  --output backend-scan.json \
  uns-claudejp-backend:latest
```

---

## Understanding Reports

### Report Formats

After each scan, three report files are generated:

1. **HTML Report** - `scan_IMAGE_TIMESTAMP.html`
   - Visual, interactive report
   - Best for reviewing in browser
   - Color-coded severity levels
   - Grouped by package

2. **JSON Report** - `scan_IMAGE_TIMESTAMP.json`
   - Machine-readable format
   - Best for CI/CD integration
   - Detailed vulnerability data
   - Parseable for automation

3. **Text Report** - `scan_IMAGE_TIMESTAMP.txt`
   - Console output
   - Quick reference
   - Summary statistics

**Report Location:**
```
docker/scripts/logs/security-scans/
├── scan_backend_20251112_143022.html
├── scan_backend_20251112_143022.json
├── scan_backend_20251112_143022.txt
├── scan_frontend_20251112_143515.html
├── scan_frontend_20251112_143515.json
└── scan_frontend_20251112_143515.txt
```

### Severity Levels

| Severity | Description | Action Required |
|----------|-------------|-----------------|
| **CRITICAL** | Exploitable, high impact | Fix immediately (< 24 hours) |
| **HIGH** | Serious vulnerability | Fix within 1 week |
| **MEDIUM** | Moderate risk | Fix within 1 month |
| **LOW** | Minor issue | Fix when convenient |

### Reading HTML Reports

**Structure:**
1. **Summary Section**: Total vulnerabilities by severity
2. **Vulnerability Table**: Detailed list with:
   - Package name
   - Installed version
   - Fixed version (if available)
   - Severity level
   - CVE ID
   - Description
3. **Recommendations**: Suggested remediation

**Example Entry:**
```
Package: openssl
Installed: 1.1.1k-1
Fixed: 1.1.1l-1
Severity: CRITICAL
CVE: CVE-2021-3711
Description: Buffer overflow in SM2 decryption
```

### JSON Report Structure

```json
{
  "SchemaVersion": 2,
  "ArtifactName": "uns-claudejp-backend:latest",
  "ArtifactType": "container_image",
  "Metadata": {
    "ImageID": "sha256:abc123...",
    "RepoTags": ["uns-claudejp-backend:latest"]
  },
  "Results": [
    {
      "Target": "python-app (python)",
      "Vulnerabilities": [
        {
          "VulnerabilityID": "CVE-2021-3711",
          "PkgName": "openssl",
          "InstalledVersion": "1.1.1k-1",
          "FixedVersion": "1.1.1l-1",
          "Severity": "CRITICAL",
          "Description": "Buffer overflow in SM2 decryption",
          "References": [
            "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-3711"
          ]
        }
      ]
    }
  ]
}
```

---

## Vulnerability Remediation

### Step 1: Identify Critical Issues

```bash
# Scan with critical only
./docker/scripts/security-scan.sh backend --severity CRITICAL

# Review HTML report
open docker/scripts/logs/security-scans/scan_backend_*.html
```

### Step 2: Update Base Images

**Backend (Python):**
```dockerfile
# Dockerfile.backend - BEFORE
FROM python:3.11-alpine

# Dockerfile.backend - AFTER (update to latest patch)
FROM python:3.11.9-alpine3.19
```

**Frontend (Node.js):**
```dockerfile
# Dockerfile.frontend - BEFORE
FROM node:20-alpine

# Dockerfile.frontend - AFTER (update to latest patch)
FROM node:20.11-alpine3.19
```

### Step 3: Update Dependencies

**Python Dependencies:**
```bash
# Update requirements.txt versions
cd backend

# Update specific package
pip install --upgrade package-name

# Freeze updated versions
pip freeze > requirements.txt
```

**Node.js Dependencies:**
```bash
# Update package.json versions
cd frontend

# Update specific package
npm update package-name

# Update all packages (careful!)
npm update

# Check for outdated packages
npm outdated
```

### Step 4: Rebuild and Re-scan

```bash
# Rebuild images
docker compose build

# Re-scan
./docker/scripts/security-scan.sh all

# Verify fixes
diff old_scan.json new_scan.json
```

### Common Vulnerability Fixes

**CVE in OS packages (Alpine):**
```dockerfile
# Update base image
FROM python:3.11.9-alpine3.19

# Update all packages
RUN apk update && apk upgrade
```

**CVE in Python packages:**
```bash
# requirements.txt
# BEFORE
requests==2.28.0

# AFTER (patched version)
requests==2.31.0
```

**CVE in Node.js packages:**
```json
// package.json
// BEFORE
"dependencies": {
  "express": "4.17.1"
}

// AFTER (patched version)
"dependencies": {
  "express": "4.18.2"
}
```

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/security-scan.yml
name: Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  trivy-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build Docker images
        run: docker compose build

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'uns-claudejp-backend:latest'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

      - name: Fail on critical vulnerabilities
        run: |
          docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
            aquasec/trivy:latest image \
            --severity CRITICAL \
            --exit-code 1 \
            uns-claudejp-backend:latest
```

### GitLab CI

```yaml
# .gitlab-ci.yml
trivy-scan:
  stage: test
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA -f docker/Dockerfile.backend .
    - docker run --rm -v /var/run/docker.sock:/var/run/docker.sock
      aquasec/trivy:latest image
      --exit-code 1
      --severity CRITICAL,HIGH
      $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  only:
    - merge_requests
    - main
```

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash

echo "Running security scan..."
./docker/scripts/security-scan.sh backend --severity CRITICAL

if [ $? -ne 0 ]; then
    echo "Security scan failed! Fix critical vulnerabilities before committing."
    exit 1
fi

echo "Security scan passed!"
```

### Docker Build Check

```bash
# scripts/build-and-scan.sh
#!/bin/bash

# Build
docker compose build backend

# Scan
./docker/scripts/security-scan.sh backend --severity CRITICAL

# Exit with scan result
exit $?
```

---

## Best Practices

### 1. Regular Scanning Schedule

**Recommended frequency:**
- **Development**: Before every commit
- **Staging**: Daily (automated)
- **Production**: Weekly (automated) + after every deployment

**Automate with cron:**
```bash
# crontab -e
0 2 * * * cd /path/to/UNS-ClaudeJP && ./docker/scripts/security-scan.sh all
```

### 2. Fix Critical Issues Immediately

**Priority workflow:**
1. **CRITICAL**: Fix within 24 hours
2. **HIGH**: Fix within 1 week
3. **MEDIUM**: Fix within 1 month
4. **LOW**: Backlog

### 3. Keep Base Images Updated

**Check for updates:**
```bash
# Pull latest base images
docker pull python:3.11-alpine
docker pull node:20-alpine

# Check for newer tags
curl -s https://hub.docker.com/v2/repositories/library/python/tags | jq '.results[].name'
```

**Update regularly:**
- Base images: Monthly
- Dependencies: Quarterly
- Security patches: Immediately

### 4. Use Specific Version Tags

**Bad practice:**
```dockerfile
FROM python:3.11      # Too vague
FROM python:latest    # Never use latest!
```

**Good practice:**
```dockerfile
FROM python:3.11.9-alpine3.19  # Specific, reproducible
```

### 5. Minimize Attack Surface

**Reduce image size:**
- Use Alpine Linux base images
- Multi-stage builds
- Remove unnecessary packages
- Don't install dev dependencies in production

**Example:**
```dockerfile
# Multi-stage build
FROM python:3.11-alpine AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-alpine
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["uvicorn", "app.main:app"]
```

### 6. Review Dependencies Regularly

**Check outdated packages:**
```bash
# Python
pip list --outdated

# Node.js
npm outdated

# Check for security advisories
npm audit
pip-audit
```

### 7. Document Accepted Risks

**Create `.trivyignore` for known false positives:**
```
# .trivyignore
CVE-2021-1234  # False positive, not exploitable in our context
CVE-2022-5678  # Accepted risk, fix planned for next quarter
```

### 8. Monitor CVE Databases

**Subscribe to security advisories:**
- National Vulnerability Database (NVD)
- GitHub Security Advisories
- Package-specific security lists

---

## Troubleshooting

### Issue: Trivy fails to download database

**Symptoms:**
```
FATAL: failed to download vulnerability DB
```

**Solution:**
```bash
# 1. Check internet connection
ping google.com

# 2. Clear Trivy cache
docker run --rm -v trivy-cache:/root/.cache/ aquasec/trivy:latest image --clear-cache

# 3. Retry scan
./docker/scripts/security-scan.sh backend
```

### Issue: False positive vulnerabilities

**Symptoms:**
- Vulnerabilities reported that don't apply to your usage

**Solution:**
```bash
# 1. Create .trivyignore file
cat > .trivyignore <<EOF
CVE-2021-1234  # Not exploitable in our context
EOF

# 2. Re-scan with ignore file
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd)/.trivyignore:/.trivyignore \
  aquasec/trivy:latest image \
  --ignorefile /.trivyignore \
  uns-claudejp-backend:latest
```

### Issue: Too many results

**Symptoms:**
- Scan returns hundreds of vulnerabilities

**Solution:**
```bash
# 1. Focus on critical/high only
./docker/scripts/security-scan.sh backend --severity CRITICAL,HIGH

# 2. Filter by package type
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:latest image \
  --vuln-type os \
  uns-claudejp-backend:latest

# 3. Ignore low severity
# Set threshold in .trivyignore or CI/CD
```

### Issue: Scan takes too long

**Symptoms:**
- Scan doesn't complete in reasonable time

**Solution:**
```bash
# 1. Update Trivy database first
docker pull aquasec/trivy:latest

# 2. Use specific scan targets
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:latest image \
  --scanners vuln \
  --skip-dirs /tmp,/var \
  uns-claudejp-backend:latest

# 3. Use cache effectively
# Database is cached after first download
```

---

## Report Interpretation

### Example Report Analysis

**Scan Output:**
```
Total: 42 (CRITICAL: 2, HIGH: 8, MEDIUM: 15, LOW: 17)

┌─────────────┬────────────────┬──────────┬───────────────────┬───────────────┐
│   Library   │ Vulnerability  │ Severity │ Installed Version │ Fixed Version │
├─────────────┼────────────────┼──────────┼───────────────────┼───────────────┤
│ openssl     │ CVE-2021-3711  │ CRITICAL │ 1.1.1k-1          │ 1.1.1l-1      │
│ libcrypto   │ CVE-2021-3711  │ CRITICAL │ 1.1.1k-1          │ 1.1.1l-1      │
│ urllib3     │ CVE-2023-45803 │ HIGH     │ 1.26.5            │ 1.26.17       │
└─────────────┴────────────────┴──────────┴───────────────────┴───────────────┘
```

**Action Plan:**
1. **CRITICAL - OpenSSL (CVE-2021-3711)**:
   - Update base image to latest Alpine version
   - Rebuild image immediately
   - Re-scan to verify fix

2. **CRITICAL - libcrypto (CVE-2021-3711)**:
   - Same issue as OpenSSL (linked)
   - Fixed by updating base image

3. **HIGH - urllib3 (CVE-2023-45803)**:
   - Update requirements.txt: `urllib3>=1.26.17`
   - Run `pip install --upgrade urllib3`
   - Rebuild and re-scan

---

## Summary

✅ **Regular scanning**: Integrate into development workflow
✅ **Prioritize fixes**: Critical first, then high, medium, low
✅ **Keep updated**: Base images and dependencies
✅ **Automate**: CI/CD integration
✅ **Document**: Track fixes and accepted risks

**Next Steps:**
- Run your first scan: `./docker/scripts/security-scan.sh all`
- Review HTML reports
- Create remediation plan for critical issues
- Set up automated scanning

---

**Related Documentation:**
- [Disaster Recovery](DISASTER_RECOVERY.md)
- [Upgrade Strategies](UPGRADE.md)
- [Monitoring](observability/MONITORING.md)

**External Resources:**
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [CVE Database](https://cve.mitre.org/)
- [NIST NVD](https://nvd.nist.gov/)

**Version History:**
- v1.0.0 (2025-11-12): Initial Trivy security scanning integration
