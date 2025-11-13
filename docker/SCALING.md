# Backend Horizontal Scaling Guide

## Overview

UNS-ClaudeJP 5.4.1 supports horizontal scaling for the backend service, allowing you to run multiple backend instances behind an nginx load balancer for improved performance and reliability.

**Version:** 1.0.0
**Last Updated:** 2025-11-12
**Author:** Claude Code

---

## Table of Contents

- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Scaling Commands](#scaling-commands)
- [Load Balancing](#load-balancing)
- [Testing](#testing)
- [Monitoring](#monitoring)
- [Performance Tuning](#performance-tuning)
- [Troubleshooting](#troubleshooting)
- [Production Recommendations](#production-recommendations)

---

## Architecture

### How It Works

```
┌─────────────┐
│   Nginx     │  Port 80/443 (Single entry point)
│Load Balancer│
└──────┬──────┘
       │ Round-robin distribution
       ├──────────┬──────────┬──────────┐
       │          │          │          │
   ┌───▼───┐  ┌───▼───┐  ┌───▼───┐  ┌───▼───┐
   │Backend│  │Backend│  │Backend│  │Backend│
   │   1   │  │   2   │  │   3   │  │  ...  │
   └───┬───┘  └───┬───┘  └───┬───┘  └───┬───┘
       │          │          │          │
       └──────────┴──────────┴──────────┘
                   │
            ┌──────▼──────┐
            │  PostgreSQL  │
            │   (Shared)   │
            └──────────────┘
```

### Components

1. **Nginx Load Balancer**
   - Acts as reverse proxy
   - Distributes requests using round-robin algorithm
   - Performs health checks on backend instances
   - Handles SSL/TLS termination

2. **Backend Instances**
   - Stateless FastAPI applications
   - Each runs on port 8000 internally
   - Auto-discovered via Docker DNS (127.0.0.11)
   - Share the same PostgreSQL database

3. **Shared Resources**
   - PostgreSQL database (single instance)
   - Redis cache (single instance)
   - Volumes for uploads and logs

---

## Quick Start

### Basic Scaling

```bash
# Start with 3 backend instances
docker compose --profile dev up -d --scale backend=3

# Verify instances are running
docker compose ps backend

# Test the scaling
./docker/scripts/test-backend-scaling.sh 3
```

### Windows Users

```cmd
# Start with 3 backend instances
docker compose --profile dev up -d --scale backend=3

# Verify instances
docker compose ps backend

# Test the scaling
scripts\TEST_BACKEND_SCALING.bat 3
```

---

## Scaling Commands

### Development Environment

```bash
# Scale to N instances
docker compose --profile dev up -d --scale backend=N

# Examples:
docker compose --profile dev up -d --scale backend=1   # Single instance
docker compose --profile dev up -d --scale backend=3   # 3 instances
docker compose --profile dev up -d --scale backend=5   # 5 instances

# Scale down
docker compose --profile dev up -d --scale backend=1
```

### Production Environment

```bash
# Production uses backend-prod service
docker compose --profile prod up -d --scale backend-prod=4

# With multiple workers per instance (recommended)
# Each backend-prod already runs with 4 uvicorn workers
# So 3 instances × 4 workers = 12 total workers
docker compose --profile prod up -d --scale backend-prod=3
```

### Important Notes

1. **No Port Conflicts**: Backend instances don't expose ports directly - nginx handles all external traffic
2. **Automatic Discovery**: Docker DNS automatically resolves `backend` to all running instances
3. **Stateless Design**: All instances are identical and stateless
4. **Shared Database**: All instances connect to the same PostgreSQL database

---

## Load Balancing

### Algorithm

Nginx uses **round-robin** load balancing by default:
- Request 1 → Backend Instance 1
- Request 2 → Backend Instance 2
- Request 3 → Backend Instance 3
- Request 4 → Backend Instance 1 (cycle repeats)

### Alternative Algorithms

Edit `docker/nginx/nginx.conf` to change the algorithm:

```nginx
upstream backend {
    # Round-robin (default) - distributes evenly
    server backend:8000 max_fails=3 fail_timeout=30s;

    # OR: Least connections - sends to instance with fewest active connections
    least_conn;
    server backend:8000 max_fails=3 fail_timeout=30s;

    # OR: IP hash - same client always goes to same backend
    ip_hash;
    server backend:8000 max_fails=3 fail_timeout=30s;

    # OR: Generic hash - hash on specific variable
    hash $request_uri consistent;
    server backend:8000 max_fails=3 fail_timeout=30s;
}
```

### Health Checks

Nginx configuration includes health checks:
- **max_fails**: 3 failures before marking instance as down
- **fail_timeout**: 30 seconds before retrying a failed instance
- **keepalive**: 32 persistent connections for connection pooling

---

## Testing

### Automated Test Script

**Linux/macOS:**
```bash
# Test with 3 instances (default)
./docker/scripts/test-backend-scaling.sh

# Test with custom number
./docker/scripts/test-backend-scaling.sh 5
```

**Windows:**
```cmd
# Test with 3 instances (default)
scripts\TEST_BACKEND_SCALING.bat

# Test with custom number
scripts\TEST_BACKEND_SCALING.bat 5
```

### Manual Testing

```bash
# 1. Scale to 3 instances
docker compose --profile dev up -d --scale backend=3

# 2. Verify all instances are healthy
docker compose ps backend

# 3. Check each instance directly
for i in {1..3}; do
    docker exec uns-claudejp-backend-$i python -c \
        "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/api/health').read())"
done

# 4. Test through nginx (should distribute requests)
for i in {1..10}; do
    curl -s http://localhost/api/health
    sleep 0.5
done

# 5. Monitor nginx logs to see distribution
docker compose logs nginx | grep "GET /api/health"
```

### Load Testing

For comprehensive load testing, see the Load Testing section in [M2-DOCKER].

---

## Monitoring

### View Running Instances

```bash
# List all backend instances
docker compose ps backend

# Detailed status
docker compose ps backend --format "table {{.Name}}\t{{.Status}}\t{{.Health}}"
```

### Monitor Logs

```bash
# All backend instances
docker compose logs -f backend

# Specific instance
docker compose logs -f uns-claudejp-backend-1

# Nginx access logs (shows load distribution)
docker compose logs -f nginx

# Filter for API requests only
docker compose logs nginx | grep "/api/"
```

### Prometheus Metrics

Access Prometheus at http://localhost:9090

**Useful queries:**
```promql
# Request rate per backend instance
rate(http_requests_total{service="backend"}[5m])

# Average response time
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Active connections
sum(backend_connections_active) by (instance)

# Error rate
rate(http_requests_total{status=~"5.."}[5m])
```

### Grafana Dashboards

Access Grafana at http://localhost:3001 (admin/admin)

Pre-configured dashboards:
1. **Backend Performance** - Request rates, response times, errors
2. **Infrastructure** - CPU, memory, network per instance
3. **Load Balancing** - Distribution across instances

---

## Performance Tuning

### Recommended Instance Count

**Development:**
- **1 instance**: Standard development (sufficient for most cases)
- **2-3 instances**: Testing load balancing and HA
- **4+ instances**: Load testing scenarios

**Production:**
- **Formula**: `instances = (expected_rps / 100) + 1`
- **Example**: 500 RPS → 6 instances
- **Minimum**: 2 instances (for high availability)
- **Maximum**: Based on database connection pool size

### Database Connection Pool

With multiple backend instances, watch your PostgreSQL connection limit:

```python
# backend/app/core/database.py
# Default pool size per instance
pool_size = 5
max_overflow = 10

# Total connections = instances × (pool_size + max_overflow)
# Example: 3 instances × 15 connections = 45 total connections
```

**PostgreSQL default max_connections**: 100

**Recommended configuration for scaling:**
```bash
# .env
POSTGRES_MAX_CONNECTIONS=200  # Increase if needed
BACKEND_POOL_SIZE=5           # Connections per instance
BACKEND_MAX_OVERFLOW=5        # Overflow per instance
```

### Nginx Tuning

For high-scale deployments, adjust nginx configuration:

```nginx
# docker/nginx/nginx.conf

# Increase worker connections
events {
    worker_connections 2048;  # Up from 1024
}

# Increase keepalive connections
upstream backend {
    server backend:8000;
    keepalive 64;            # Up from 32
    keepalive_requests 200;  # Up from 100
}
```

### Resource Limits

Set Docker resource limits in `docker-compose.yml`:

```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '1.0'
        memory: 1G
      reservations:
        cpus: '0.5'
        memory: 512M
```

---

## Troubleshooting

### Issue: Instances won't scale

**Symptoms:**
- `docker compose up -d --scale backend=3` fails
- Error: "container name already in use"

**Solution:**
```bash
# 1. Stop all services
docker compose down

# 2. Verify container_name is removed from backend service
grep -A 5 "backend:" docker-compose.yml
# Should NOT have "container_name: uns-claudejp-backend"

# 3. Start with scaling
docker compose --profile dev up -d --scale backend=3
```

### Issue: Nginx can't reach backends

**Symptoms:**
- 502 Bad Gateway errors
- Nginx logs show "no live upstreams"

**Solution:**
```bash
# 1. Verify backends are healthy
docker compose ps backend

# 2. Check backend health directly
docker exec uns-claudejp-backend-1 python -c \
    "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"

# 3. Check nginx DNS resolution
docker exec uns-claudejp-nginx nslookup backend

# 4. Restart nginx
docker compose restart nginx
```

### Issue: Uneven load distribution

**Symptoms:**
- Some instances receive more traffic than others
- Nginx logs show imbalanced distribution

**Solution:**
```bash
# 1. Verify all instances are healthy
docker compose ps backend

# 2. Check nginx upstream status
docker exec uns-claudejp-nginx nginx -T | grep -A 10 "upstream backend"

# 3. Clear nginx connection cache
docker compose restart nginx

# 4. Consider using least_conn algorithm (see Load Balancing section)
```

### Issue: Database connection pool exhausted

**Symptoms:**
- Errors: "connection pool exhausted"
- Slow response times
- Timeouts

**Solution:**
```bash
# 1. Check current connections
docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c \
    "SELECT count(*) FROM pg_stat_activity;"

# 2. Reduce instances or increase pool limit
# Edit .env:
POSTGRES_MAX_CONNECTIONS=200

# 3. Reduce pool size per instance
# Edit backend/app/core/database.py:
pool_size = 3
max_overflow = 5

# 4. Restart services
docker compose down
docker compose --profile dev up -d --scale backend=3
```

---

## Production Recommendations

### Minimum Configuration

```bash
# Use production profile with 2 instances minimum
docker compose --profile prod up -d --scale backend-prod=2

# Each backend-prod runs with 4 uvicorn workers
# Total workers: 2 instances × 4 workers = 8 workers
```

### High Availability Setup

```yaml
# docker-compose.yml additions for production

backend-prod:
  deploy:
    replicas: 3              # Always run 3 instances
    restart_policy:
      condition: on-failure
      delay: 5s
      max_attempts: 3
      window: 120s
    resources:
      limits:
        cpus: '2.0'
        memory: 2G
      reservations:
        cpus: '1.0'
        memory: 1G
```

### Health Check Configuration

```yaml
backend-prod:
  healthcheck:
    test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"]
    interval: 15s           # More frequent checks
    timeout: 5s
    retries: 3
    start_period: 60s
```

### Monitoring Alerts

Configure Prometheus alerts for production:

```yaml
# docker/observability/prometheus-alerts.yml

groups:
  - name: backend_scaling
    rules:
      - alert: BackendInstanceDown
        expr: up{job="backend"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Backend instance is down"

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
```

### Deployment Strategy

For zero-downtime deployments:

```bash
# 1. Deploy new version with different tag
docker compose --profile prod build backend-prod

# 2. Scale up with new version
docker compose --profile prod up -d --scale backend-prod=6 --no-recreate

# 3. Wait for health checks to pass
sleep 30

# 4. Scale down old instances
# (Docker Compose will keep newest instances)
docker compose --profile prod up -d --scale backend-prod=3

# 5. Verify all instances are new version
docker compose ps backend-prod
```

---

## Summary

✅ **Horizontal scaling implemented** - Backend can scale from 1 to N instances
✅ **Load balancing configured** - Nginx distributes traffic evenly
✅ **Health checks enabled** - Failed instances automatically excluded
✅ **Monitoring ready** - Prometheus and Grafana track all instances
✅ **Production-ready** - HA configuration available

**Next Steps:**
- [M2] Set up load testing with Apache JMeter
- [M3] Test disaster recovery scenarios
- [M5] Configure advanced Grafana dashboards

---

**Related Documentation:**
- [docker-compose.yml](/docker-compose.yml) - Service configuration
- [docker/nginx/nginx.conf](/docker/nginx/nginx.conf) - Load balancer configuration
- [TROUBLESHOOTING.md](/docs/04-troubleshooting/TROUBLESHOOTING.md) - General troubleshooting

**Version History:**
- v1.0.0 (2025-11-12): Initial implementation of horizontal scaling
