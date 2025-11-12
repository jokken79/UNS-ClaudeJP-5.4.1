# Grafana & Prometheus Configuration - Timer Card Module Monitoring

**Version:** 1.0
**Date:** 2025-11-12
**Purpose:** Setup monitoring, alerting, and observability for Timer Card module

---

## 📊 Prometheus Configuration

### prometheus.yml - Add Timer Card Scrape Config

Add this section to your Prometheus configuration:

```yaml
# Timer Card Module Monitoring
  - job_name: 'timer-cards-api'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
    scrape_timeout: 10s

    # Timer card specific metrics
    metric_relabel_configs:
      - source_labels: [__name__]
        regex: 'timer_card_.*|hakenmoto_.*|approval_.*'
        action: keep

# OCR Monitoring
  - job_name: 'timer-card-ocr'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
    metric_relabel_configs:
      - source_labels: [__name__]
        regex: 'ocr_.*|timeout_.*'
        action: keep
```

### Alert Rules - timer_card_alerts.yml

```yaml
groups:
  - name: timer_card_alerts
    interval: 30s
    rules:
      # Critical Alerts
      - alert: TimerCardDatabaseDown
        expr: timer_card_database_connection{status="failed"} > 0
        for: 1m
        labels:
          severity: critical
          module: timer_cards
        annotations:
          summary: "Timer Card Database Connection Failed"
          description: "Database connectivity lost for {{ $value }} seconds"
          runbook: "docs/DISASTER_RECOVERY_PLAN.md#scenario-1-database-corruption"

      - alert: TimerCardDuplicateDetected
        expr: increase(timer_card_duplicate_errors_total[5m]) > 0
        labels:
          severity: critical
          module: timer_cards
        annotations:
          summary: "Duplicate Timer Card Detected"
          description: "{{ $value }} duplicate timer card attempts in last 5 minutes"
          runbook: "docs/OPERATIONS_MANUAL.md#issue-1-duplicate-timer-card-error"

      - alert: TimerCardApprovalBacklog
        expr: timer_card_pending_approvals > 100
        for: 2h
        labels:
          severity: high
          module: timer_cards
        annotations:
          summary: "Large Timer Card Approval Backlog"
          description: "{{ $value }} cards awaiting approval (> 100)"

      # Performance Alerts
      - alert: TimerCardQuerySlow
        expr: timer_card_query_duration_seconds{percentile="p99"} > 0.5
        for: 5m
        labels:
          severity: high
          module: timer_cards
        annotations:
          summary: "Slow Timer Card Queries"
          description: "99th percentile query time: {{ $value }}s (> 500ms)"

      - alert: TimerCardAPIHighLatency
        expr: timer_card_api_response_time_seconds{endpoint="/api/timer-cards"} > 1.0
        for: 5m
        labels:
          severity: warning
          module: timer_cards
        annotations:
          summary: "Timer Card API High Latency"
          description: "API response time: {{ $value }}s"

      - alert: OCRTimeoutRate
        expr: increase(ocr_timeout_errors_total[5m]) > 5
        labels:
          severity: warning
          module: timer_cards
        annotations:
          summary: "High OCR Timeout Rate"
          description: "{{ $value }} OCR timeouts in last 5 minutes"

      # Data Integrity Alerts
      - alert: TimerCardOrphanedRecords
        expr: timer_card_orphaned_records_count > 0
        labels:
          severity: critical
          module: timer_cards
        annotations:
          summary: "Orphaned Timer Card Records Detected"
          description: "{{ $value }} timer cards reference non-existent employees"
          runbook: "docs/OPERATIONS_MANUAL.md#data-integrity-checks"

      - alert: TimerCardIncompleteApproval
        expr: timer_card_incomplete_approval_count > 0
        labels:
          severity: high
          module: timer_cards
        annotations:
          summary: "Incomplete Approval Workflow"
          description: "{{ $value }} cards have approval state inconsistency"

      - alert: TimerCardFactoryMismatch
        expr: timer_card_factory_mismatch_count > 0
        labels:
          severity: medium
          module: timer_cards
        annotations:
          summary: "Factory ID Mismatch Detected"
          description: "{{ $value }} timer cards have factory_id != employee.factory_id"

      # Resource Alerts
      - alert: DatabaseConnectionPoolExhausted
        expr: database_connection_pool_available < 5
        for: 2m
        labels:
          severity: critical
          module: database
        annotations:
          summary: "Database Connection Pool Nearly Exhausted"
          description: "Only {{ $value }} connections available"

      - alert: TimerCardDiskSpaceLow
        expr: node_filesystem_avail_bytes{mountpoint="/var/lib/postgresql"} < 1073741824
        labels:
          severity: critical
          module: database
        annotations:
          summary: "Low Disk Space on Database Volume"
          description: "Less than 1GB available"
```

---

## 📈 Grafana Dashboard Configuration

### Timer Card Module Overview Dashboard

```json
{
  "dashboard": {
    "title": "Timer Card Module - Comprehensive Monitoring",
    "tags": ["timer-cards", "payroll", "taiko"],
    "timezone": "Asia/Tokyo",
    "panels": [
      {
        "id": 1,
        "title": "Timer Cards - Total Count",
        "targets": [
          {
            "expr": "timer_card_total_count",
            "refId": "A"
          }
        ],
        "type": "stat",
        "gridPos": {"h": 4, "w": 6, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Approval Status Distribution",
        "targets": [
          {
            "expr": "timer_card_approved_count",
            "refId": "A",
            "legendFormat": "Approved"
          },
          {
            "expr": "timer_card_pending_approvals",
            "refId": "B",
            "legendFormat": "Pending"
          }
        ],
        "type": "piechart",
        "gridPos": {"h": 4, "w": 6, "x": 6, "y": 0}
      },
      {
        "id": 3,
        "title": "Average Work Hours by Shift Type",
        "targets": [
          {
            "expr": "avg(timer_card_regular_hours) by (shift_type)",
            "refId": "A"
          }
        ],
        "type": "bargauge",
        "gridPos": {"h": 4, "w": 6, "x": 12, "y": 0}
      },
      {
        "id": 4,
        "title": "Night Hours Distribution",
        "targets": [
          {
            "expr": "timer_card_night_hours_total",
            "refId": "A"
          }
        ],
        "type": "stat",
        "gridPos": {"h": 4, "w": 6, "x": 18, "y": 0}
      },
      {
        "id": 5,
        "title": "Query Performance - GET /api/timer-cards",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, timer_card_api_duration_seconds_bucket{endpoint=\"/api/timer-cards\"})",
            "refId": "A",
            "legendFormat": "p50"
          },
          {
            "expr": "histogram_quantile(0.95, timer_card_api_duration_seconds_bucket{endpoint=\"/api/timer-cards\"})",
            "refId": "B",
            "legendFormat": "p95"
          },
          {
            "expr": "histogram_quantile(0.99, timer_card_api_duration_seconds_bucket{endpoint=\"/api/timer-cards\"})",
            "refId": "C",
            "legendFormat": "p99"
          }
        ],
        "type": "timeseries",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 4}
      },
      {
        "id": 6,
        "title": "API Error Rate",
        "targets": [
          {
            "expr": "rate(timer_card_api_errors_total[5m])",
            "refId": "A"
          }
        ],
        "type": "timeseries",
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 4}
      },
      {
        "id": 7,
        "title": "Database Queries - By Operation",
        "targets": [
          {
            "expr": "rate(timer_card_db_queries_total[5m]) by (operation)",
            "refId": "A"
          }
        ],
        "type": "timeseries",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 12}
      },
      {
        "id": 8,
        "title": "Approval Workflow Metrics",
        "targets": [
          {
            "expr": "timer_card_approval_time_seconds",
            "refId": "A"
          }
        ],
        "type": "timeseries",
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 12}
      },
      {
        "id": 9,
        "title": "OCR Processing - Success vs Failure",
        "targets": [
          {
            "expr": "rate(ocr_processing_success_total[5m])",
            "refId": "A",
            "legendFormat": "Success"
          },
          {
            "expr": "rate(ocr_processing_failed_total[5m])",
            "refId": "B",
            "legendFormat": "Failed"
          }
        ],
        "type": "timeseries",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 20}
      },
      {
        "id": 10,
        "title": "OCR Processing Time",
        "targets": [
          {
            "expr": "histogram_quantile(0.99, ocr_processing_duration_seconds_bucket)",
            "refId": "A"
          }
        ],
        "type": "timeseries",
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 20}
      },
      {
        "id": 11,
        "title": "Data Integrity Checks",
        "targets": [
          {
            "expr": "timer_card_duplicate_count",
            "refId": "A",
            "legendFormat": "Duplicates"
          },
          {
            "expr": "timer_card_orphaned_records_count",
            "refId": "B",
            "legendFormat": "Orphaned"
          },
          {
            "expr": "timer_card_invalid_approval_count",
            "refId": "C",
            "legendFormat": "Invalid Approvals"
          }
        ],
        "type": "timeseries",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 28}
      },
      {
        "id": 12,
        "title": "Resource Usage",
        "targets": [
          {
            "expr": "process_resident_memory_bytes{job=\"timer-cards-api\"}",
            "refId": "A",
            "legendFormat": "Backend Memory"
          }
        ],
        "type": "timeseries",
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 28}
      }
    ]
  }
}
```

---

## 🔧 Custom Metrics to Instrument

Add these Prometheus metrics to `backend/app/main.py`:

```python
from prometheus_client import Counter, Histogram, Gauge
from datetime import datetime

# Timer Card Counters
timer_card_total_count = Gauge(
    'timer_card_total_count',
    'Total number of timer cards',
    ['shift_type']
)

timer_card_approved_count = Gauge(
    'timer_card_approved_count',
    'Number of approved timer cards'
)

timer_card_pending_approvals = Gauge(
    'timer_card_pending_approvals',
    'Number of pending approvals'
)

timer_card_duplicate_errors_total = Counter(
    'timer_card_duplicate_errors_total',
    'Total duplicate timer card attempts'
)

timer_card_night_hours_total = Gauge(
    'timer_card_night_hours_total',
    'Total night hours worked (22:00-05:00)'
)

# API Performance Metrics
timer_card_api_response_time = Histogram(
    'timer_card_api_response_time_seconds',
    'API response time in seconds',
    ['endpoint', 'method', 'status']
)

timer_card_api_errors_total = Counter(
    'timer_card_api_errors_total',
    'Total API errors',
    ['endpoint', 'status_code']
)

# Database Metrics
timer_card_db_queries_total = Counter(
    'timer_card_db_queries_total',
    'Total database queries',
    ['operation', 'table']
)

timer_card_query_duration = Histogram(
    'timer_card_query_duration_seconds',
    'Database query duration',
    ['operation'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 5.0)
)

# Data Integrity Metrics
timer_card_duplicate_count = Gauge(
    'timer_card_duplicate_count',
    'Number of duplicate timer cards detected'
)

timer_card_orphaned_records_count = Gauge(
    'timer_card_orphaned_records_count',
    'Number of orphaned timer card records'
)

timer_card_incomplete_approval_count = Gauge(
    'timer_card_incomplete_approval_count',
    'Number of incomplete approval states'
)

timer_card_factory_mismatch_count = Gauge(
    'timer_card_factory_mismatch_count',
    'Number of factory_id mismatches'
)

# OCR Metrics
ocr_processing_success_total = Counter(
    'ocr_processing_success_total',
    'Total successful OCR processing attempts'
)

ocr_processing_failed_total = Counter(
    'ocr_processing_failed_total',
    'Total failed OCR processing attempts',
    ['provider', 'reason']
)

ocr_timeout_errors_total = Counter(
    'ocr_timeout_errors_total',
    'Total OCR timeout errors'
)

ocr_processing_duration = Histogram(
    'ocr_processing_duration_seconds',
    'OCR processing duration',
    ['provider'],
    buckets=(1, 5, 10, 30, 60, 120)
)

# Approval Workflow Metrics
timer_card_approval_time = Histogram(
    'timer_card_approval_time_seconds',
    'Time from submission to approval',
    buckets=(300, 900, 1800, 3600, 7200, 86400)  # 5min to 1day
)
```

---

## 📍 Integration Points

### In GET / endpoint (timer_cards.py)

```python
@router.get("/", response_model=list[TimerCardResponse])
async def get_timer_cards(
    ...
):
    start_time = time.time()

    try:
        # Query logic
        ...

        # Record metrics
        timer_card_api_response_time.labels(
            endpoint="/api/timer-cards",
            method="GET",
            status="200"
        ).observe(time.time() - start_time)

        return timer_cards

    except Exception as e:
        timer_card_api_errors_total.labels(
            endpoint="/api/timer-cards",
            status_code="500"
        ).inc()
        raise
```

### In database operations

```python
def update_integrity_metrics(db: Session):
    """Update data integrity metrics"""

    # Count duplicates
    duplicates = db.query(
        func.count(TimerCard.id)
    ).filter(
        # duplicate detection query
    ).scalar()

    timer_card_duplicate_count.set(duplicates)

    # Count orphaned records
    orphaned = db.query(
        func.count(TimerCard.id)
    ).filter(
        ~exists(select(1).select_from(Employee).where(...))
    ).scalar()

    timer_card_orphaned_records_count.set(orphaned)
```

---

## 🚀 Deployment Steps

### 1. Update docker-compose.yml

Add Prometheus scrape config for backend:

```yaml
backend:
  environment:
    - PROMETHEUS_ENABLED=true
    - PROMETHEUS_PORT=8000
```

### 2. Enable Prometheus metrics in FastAPI

```python
# backend/app/main.py
from prometheus_client import make_asgi_app
from prometheus_fastapi_instrumentator import Instrumentator

# Add Prometheus middleware
Instrumentator().instrument(app).expose(app)

# Or manually
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

### 3. Restart Services

```bash
docker compose restart backend
```

### 4. Verify Metrics Endpoint

```bash
curl http://localhost:8000/metrics | grep timer_card
```

### 5. Import Grafana Dashboard

```bash
# Via Grafana UI:
# 1. Grafana > Dashboards > Import
# 2. Paste the JSON dashboard config above
# 3. Select Prometheus as data source
# 4. Import
```

### 6. Enable Alert Rules

```bash
# Add to prometheus.yml
rule_files:
  - /etc/prometheus/timer_card_alerts.yml

# Restart Prometheus
docker compose restart prometheus
```

---

## 📊 Monitoring Schedule

**Real-Time Monitoring:**
- Query performance (p99 latency)
- Error rates
- API response times
- Database connection pool

**Hourly Checks:**
- Approval backlog
- OCR success rate
- Data integrity

**Daily Reviews:**
- Night hours totals
- Holiday bonus calculations
- Average shift duration
- RBAC access patterns

**Weekly Analysis:**
- Performance trends
- Error patterns
- Capacity planning

---

**Grafana & Prometheus Setup:** Ready for deployment
**Last Updated:** 2025-11-12
