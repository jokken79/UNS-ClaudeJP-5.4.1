# Advanced Monitoring with Grafana and Prometheus

## Overview

UNS-ClaudeJP 5.4.1 includes a comprehensive monitoring stack with Grafana dashboards and Prometheus alerting rules for business metrics, infrastructure health, and security monitoring.

**Version:** 1.0.0
**Last Updated:** 2025-11-12
**Author:** Claude Code

---

## Table of Contents

- [Available Dashboards](#available-dashboards)
- [Alerting Rules](#alerting-rules)
- [Accessing Grafana](#accessing-grafana)
- [Dashboard Guide](#dashboard-guide)
- [Alert Configuration](#alert-configuration)
- [Custom Metrics](#custom-metrics)
- [Troubleshooting](#troubleshooting)

---

## Available Dashboards

### 1. Business Metrics Dashboard
**UID:** `uns-business-metrics`
**URL:** http://localhost:3001/d/uns-business-metrics

**Panels:**
- **Total Candidates**: Current count of candidates in system
- **Active Employees**: Number of currently active employees
- **Total Factories**: Client sites/factories registered
- **Pending Requests**: Employee requests awaiting approval
- **API Request Rate**: Real-time API traffic
- **Response Status Distribution**: Success vs error responses (pie chart)
- **New Candidates (Daily)**: Candidate registration trends
- **OCR Processing Rate**: OCR success/failure tracking

**Use Cases:**
- Daily business operations monitoring
- Track candidate pipeline
- Monitor employee requests
- OCR service health

**Recommended Refresh:** 30 seconds

---

### 2. Infrastructure Dashboard
**UID:** `uns-infrastructure`
**URL:** http://localhost:3001/d/uns-infrastructure

**Panels:**
- **Container CPU Usage**: CPU utilization per container
- **Container Memory Usage**: Memory consumption per container
- **Database Connections**: Active vs max connections
- **Network I/O**: RX/TX traffic per container
- **Docker Volume Usage**: Persistent volume disk usage
- **Response Time Percentiles**: p50, p95, p99 latencies
- **Redis Cache Hit Rate**: Cache effectiveness

**Use Cases:**
- Capacity planning
- Performance optimization
- Resource allocation
- Bottleneck identification

**Recommended Refresh:** 30 seconds

---

### 3. Security Dashboard
**UID:** `uns-security`
**URL:** http://localhost:3001/d/uns-security

**Panels:**
- **Failed Logins (1h)**: Authentication failure tracking
- **Unauthorized Access (401)**: Unauthorized API attempts
- **Forbidden Access (403)**: Permission violations
- **Active Sessions**: Current user sessions
- **Login Attempts**: Success vs failed over time
- **Top Failed Login IPs**: IP addresses with most failures
- **HTTP Status Codes**: Status code distribution
- **Rate Limit Violations**: Rate limiting enforcement
- **JWT Validation Failure Rate**: Token validation issues
- **SQL Injection Attempts (1h)**: Security threat detection

**Use Cases:**
- Security incident detection
- Brute force attack monitoring
- Access pattern analysis
- Compliance reporting

**Recommended Refresh:** 30 seconds

---

## Alerting Rules

### Critical Alerts (Immediate Action - < 5 minutes)

| Alert Name | Condition | Duration | Action |
|------------|-----------|----------|--------|
| **ServiceDown** | Service unreachable | 1 minute | Restart service immediately |
| **DatabaseDown** | PostgreSQL down | 30 seconds | Critical! Database restart |
| **HighErrorRate** | > 10% 5xx errors | 5 minutes | Check backend logs |
| **DatabaseConnectionPoolExhausted** | > 90% connections | 2 minutes | Scale backend or increase pool |
| **DiskSpaceCritical** | > 90% disk usage | 5 minutes | Clean up immediately |

### High Priority Alerts (Action within 30 minutes)

| Alert Name | Condition | Duration | Action |
|------------|-----------|----------|--------|
| **HighResponseTime** | p95 > 1 second | 10 minutes | Investigate performance |
| **MemoryUsageHigh** | > 85% memory | 5 minutes | Check for memory leaks |
| **CPUUsageHigh** | > 80% CPU | 10 minutes | Scale or optimize |
| **RedisDown** | Redis unreachable | 2 minutes | Restart Redis |
| **BackendInstanceDown** | < 2 instances running | 5 minutes | Scale backend |

### Warning Alerts (Monitor/Plan Action)

| Alert Name | Condition | Duration | Action |
|------------|-----------|----------|--------|
| **ResponseTimeWarning** | p95 > 0.5 second | 15 minutes | Monitor and plan optimization |
| **DatabaseConnectionsWarning** | > 70% connections | 10 minutes | Plan scaling |
| **DiskSpaceWarning** | > 70% disk usage | 10 minutes | Plan cleanup |
| **RedisCacheHitRateLow** | < 80% hit rate | 30 minutes | Review cache strategy |
| **HighAuthFailureRate** | > 10% login failures | 10 minutes | Check for attacks |

### Security Alerts

| Alert Name | Condition | Duration | Action |
|------------|-----------|----------|--------|
| **FailedLoginSpike** | > 20 failures in 5min | 5 minutes | Investigate brute force |
| **UnauthorizedAccessAttempts** | > 50 401s in 5min | 5 minutes | Review access logs |
| **SQLInjectionAttempt** | Any SQL injection detected | 1 minute | Critical! Block IP |
| **RateLimitViolations** | > 100 violations in 5min | 5 minutes | Investigate DoS |

### Business Alerts

| Alert Name | Condition | Duration | Action |
|------------|-----------|----------|--------|
| **PendingRequestsHigh** | > 50 pending requests | 30 minutes | Notify coordinators |
| **OCRFailureRateHigh** | > 20% OCR failures | 30 minutes | Check OCR service |
| **NoNewCandidatesRecently** | No candidates in 24h | 2 hours | Check candidate portal |

---

## Accessing Grafana

### URLs

**Grafana Dashboard:**
- URL: http://localhost:3001
- Default user: `admin`
- Default password: `admin`

**Prometheus:**
- URL: http://localhost:9090
- Alerts page: http://localhost:9090/alerts
- Targets page: http://localhost:9090/targets

**Tempo (Tracing):**
- URL: http://localhost:3200

### First Time Setup

1. **Access Grafana:**
   ```
   http://localhost:3001
   Login: admin / admin
   ```

2. **Change Password:**
   - Click on user profile (bottom left)
   - Change password
   - Save

3. **Explore Dashboards:**
   - Click "Dashboards" → "Browse"
   - Open "UNS-ClaudeJP Business Metrics"
   - Pin to favorites (star icon)

4. **Configure Alerts:**
   - Go to "Alerting" → "Alert rules"
   - Review existing alerts
   - Configure notification channels (Email, Slack, etc.)

---

## Dashboard Guide

### Business Metrics Dashboard

**Daily Operations Workflow:**

1. **Morning Check** (9:00 AM):
   - Check Total Candidates (trend up?)
   - Check Active Employees (any changes?)
   - Check Pending Requests (need attention?)
   - Review API Request Rate (normal traffic?)

2. **Midday Review** (12:00 PM):
   - Check OCR Processing Rate (any failures?)
   - Review Response Status Distribution (errors?)
   - Check New Candidates (meeting targets?)

3. **End of Day** (5:00 PM):
   - Review daily candidate registrations
   - Clear pending requests
   - Check for any anomalies

**Key Metrics to Watch:**
- Pending Requests > 20: Priority review needed
- OCR failure rate > 10%: Service issue
- Error rate > 1%: Backend investigation

---

### Infrastructure Dashboard

**Performance Monitoring Workflow:**

1. **Resource Usage:**
   - CPU: Should be < 70% average
   - Memory: Should be < 80% average
   - Disk: Should be < 70%

2. **Database Health:**
   - Connections: Should be < 70% of max
   - Response time: p95 < 500ms

3. **Network:**
   - Monitor for unusual spikes
   - Check for sustained high traffic

**Capacity Planning:**
- Review weekly trends
- Plan scaling at 70% resource usage
- Archive old data when disk > 70%

**Optimization Targets:**
- p95 response time: < 200ms (excellent), < 500ms (good)
- CPU usage: < 50% (comfortable headroom)
- Memory usage: < 70% (prevents OOM)
- Cache hit rate: > 90% (optimal)

---

### Security Dashboard

**Security Monitoring Workflow:**

1. **Hourly Checks:**
   - Failed Logins < 10 (normal user errors)
   - Unauthorized Access < 20 (normal)
   - Active Sessions (verify expected)

2. **Daily Review:**
   - Review Top Failed Login IPs
   - Check Rate Limit Violations
   - Review HTTP Status Codes distribution

3. **Incident Response:**
   - Failed Login Spike (> 20): Block IP
   - SQL Injection Attempt: Critical incident
   - Unusual 401/403 patterns: Investigate

**Security Thresholds:**
- Failed logins > 5/hour from single IP: Investigate
- 401 errors > 50/hour: Possible attack
- SQL injection attempts > 0: Immediate action

---

## Alert Configuration

### Notification Channels

Configure alerting in Prometheus Alertmanager or Grafana:

**Email Alerts:**
```yaml
# grafana/provisioning/alerting/email.yaml
apiVersion: 1
contactPoints:
  - name: email
    receivers:
      - uid: email
        type: email
        settings:
          addresses: admin@uns-kikaku.com
```

**Slack Alerts:**
```yaml
# grafana/provisioning/alerting/slack.yaml
apiVersion: 1
contactPoints:
  - name: slack
    receivers:
      - uid: slack
        type: slack
        settings:
          url: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
          text: "Alert: {{.CommonAnnotations.summary}}"
```

**PagerDuty (Critical Only):**
```yaml
# alertmanager.yml
route:
  receiver: 'pagerduty'
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
    - match:
        severity: high
      receiver: 'email'
```

### Customizing Alerts

Edit: `docker/observability/prometheus-alerts.yml`

**Example - Custom Business Alert:**
```yaml
- alert: LowCandidateRegistrations
  expr: rate(candidates_created_total[1h]) < 0.1
  for: 2h
  labels:
    severity: warning
    component: business
  annotations:
    summary: "Low candidate registration rate"
    description: "Only {{$value}} candidates/hour (expected: > 1/hour)"
    runbook: "Check candidate portal and marketing campaigns"
```

**Reload Configuration:**
```bash
# Reload Prometheus config
curl -X POST http://localhost:9090/-/reload

# Or restart Prometheus
docker compose restart prometheus
```

---

## Custom Metrics

### Adding Backend Metrics

**Step 1: Instrument Backend Code**

```python
# backend/app/main.py
from prometheus_client import Counter, Histogram

# Define metrics
candidates_created = Counter(
    'candidates_created_total',
    'Total number of candidates created'
)

ocr_duration = Histogram(
    'ocr_processing_duration_seconds',
    'OCR processing time'
)

# Use in code
@app.post("/candidates")
async def create_candidate(candidate: CandidateCreate):
    candidates_created.inc()  # Increment counter
    return await candidate_service.create(candidate)

@app.post("/ocr/process")
async def process_ocr(file: UploadFile):
    with ocr_duration.time():  # Time the operation
        result = await ocr_service.process(file)
    return result
```

**Step 2: Expose Metrics Endpoint**

Metrics are automatically exposed at `/metrics`:
```
http://localhost:8000/metrics
```

**Step 3: Add to Grafana Dashboard**

1. Edit dashboard JSON
2. Add new panel
3. Add query:
   ```promql
   rate(candidates_created_total[5m])
   ```
4. Save dashboard

---

## Troubleshooting

### Issue: Dashboards not loading

**Symptoms:**
- Grafana shows "No data"
- Panels are empty

**Solution:**
```bash
# 1. Check Prometheus is scraping
curl http://localhost:9090/api/v1/targets

# 2. Check backend is exposing metrics
curl http://localhost:8000/metrics

# 3. Verify Grafana datasource
# Grafana → Configuration → Data Sources → Prometheus
# Test connection

# 4. Check Prometheus logs
docker compose logs prometheus
```

### Issue: Alerts not firing

**Symptoms:**
- Alerts in "Inactive" state despite conditions being met

**Solution:**
```bash
# 1. Check alert rules loaded
curl http://localhost:9090/api/v1/rules

# 2. Verify evaluation interval
# Should be 15s in prometheus.yml

# 3. Check alert rule syntax
docker compose exec prometheus promtool check rules /etc/prometheus/prometheus-alerts.yml

# 4. Restart Prometheus
docker compose restart prometheus
```

### Issue: High disk usage from metrics

**Symptoms:**
- Docker volume usage > 80%
- Prometheus pod taking lots of space

**Solution:**
```bash
# 1. Check Prometheus storage
docker exec uns-claudejp-prometheus du -sh /prometheus

# 2. Reduce retention (default: 15 days)
# Edit docker-compose.yml:
# command: ["--config.file=/etc/prometheus/prometheus.yml", "--storage.tsdb.retention.time=7d"]

# 3. Clean old data
docker compose restart prometheus
```

### Issue: Metrics missing

**Symptoms:**
- Some panels show "No data"
- Inconsistent metrics

**Solution:**
```bash
# 1. Check if metric exists in Prometheus
curl 'http://localhost:9090/api/v1/query?query=metric_name'

# 2. Verify scrape targets
http://localhost:9090/targets

# 3. Check backend logs for metric export errors
docker compose logs backend | grep metrics

# 4. Verify metric names match dashboard queries
```

---

## Best Practices

1. **Dashboard Organization:**
   - Use folders to group related dashboards
   - Name dashboards clearly
   - Add descriptions to panels
   - Set appropriate time ranges

2. **Alert Tuning:**
   - Start with conservative thresholds
   - Adjust based on actual usage patterns
   - Avoid alert fatigue
   - Group related alerts

3. **Performance:**
   - Use appropriate scrape intervals
   - Limit query time ranges
   - Use recording rules for complex queries
   - Archive old metrics

4. **Security:**
   - Change default Grafana password
   - Use authentication for Prometheus
   - Restrict access to monitoring tools
   - Monitor access logs

5. **Maintenance:**
   - Review dashboards monthly
   - Update alert thresholds quarterly
   - Clean up old data regularly
   - Document custom metrics

---

## Metric Reference

### Backend Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | Total HTTP requests by endpoint |
| `http_request_duration_seconds` | Histogram | Request duration distribution |
| `candidates_total` | Gauge | Current candidate count |
| `employees_active_total` | Gauge | Active employee count |
| `auth_login_failed_total` | Counter | Failed login attempts |
| `ocr_requests_total` | Counter | OCR processing requests |
| `rate_limit_exceeded_total` | Counter | Rate limit violations |

### System Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `container_cpu_usage_seconds_total` | Counter | Container CPU usage |
| `container_memory_usage_bytes` | Gauge | Container memory usage |
| `node_filesystem_avail_bytes` | Gauge | Available disk space |
| `pg_stat_database_numbackends` | Gauge | Database connections |
| `redis_keyspace_hits_total` | Counter | Redis cache hits |

---

**Related Documentation:**
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Backend Scaling](../SCALING.md)
- [Disaster Recovery](../DISASTER_RECOVERY.md)

**Version History:**
- v1.0.0 (2025-11-12): Initial advanced monitoring setup with 3 dashboards and comprehensive alerts
