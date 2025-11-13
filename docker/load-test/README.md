# Load Testing with Apache JMeter

## Overview

This directory contains a complete load testing infrastructure for UNS-ClaudeJP 5.4.1 using Apache JMeter. The setup includes distributed testing capabilities with multiple JMeter instances and real-time monitoring via Grafana.

**Version:** 1.0.0
**Last Updated:** 2025-11-12
**Author:** Claude Code

---

## Table of Contents

- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Test Scenarios](#test-scenarios)
- [Running Tests](#running-tests)
- [Understanding Results](#understanding-results)
- [Monitoring](#monitoring)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

---

## Architecture

### Components

```
┌─────────────────┐
│  JMeter Master  │  Coordinates test execution
└────────┬────────┘
         │
    ┌────┴─────┬─────────┬─────────┐
    │          │         │         │
┌───▼───┐  ┌───▼───┐ ┌───▼───┐  ┌───▼───┐
│Slave 1│  │Slave 2│ │Slave 3│  │ ... │  Generate load
└───┬───┘  └───┬───┘ └───┬───┘  └───┬───┘
    │          │         │         │
    └──────────┴─────────┴─────────┘
               │
         ┌─────▼──────┐
         │   Nginx    │  Load balancer
         │   (LB)     │
         └─────┬──────┘
               │
    ┌──────────┴──────────┬──────────┐
    │                     │          │
┌───▼───┐           ┌───▼───┐   ┌───▼───┐
│Backend│           │Backend│   │Backend│  Process requests
│   1   │           │   2   │   │   3   │
└───┬───┘           └───┬───┘   └───┬───┘
    │                     │          │
    └──────────┬──────────┴──────────┘
               │
        ┌──────▼──────┐
        │ PostgreSQL  │  Database
        └─────────────┘

         Metrics Flow:
    JMeter → InfluxDB → Grafana
```

### Services

1. **jmeter-master**: Coordinates and aggregates test results
2. **jmeter-slave-1/2/3**: Generate distributed load
3. **influxdb**: Stores real-time metrics
4. **jmeter-grafana**: Visualizes test metrics (port 3002)

---

## Quick Start

### Prerequisites

1. Main UNS-ClaudeJP application running:
   ```bash
   docker compose --profile dev up -d
   ```

2. Backend scaled for load testing (optional):
   ```bash
   docker compose --profile dev up -d --scale backend=3
   ```

### Run Your First Load Test

**Linux/macOS:**
```bash
# 1. Navigate to load-test directory
cd docker/load-test

# 2. Start JMeter services
docker compose up -d

# 3. Run light load test (100 users)
./run-load-test.sh light

# 4. View results
# HTML report will be generated in: reports/light_TIMESTAMP/index.html
```

**Windows:**
```cmd
# 1. Navigate to load-test directory
cd docker\load-test

# 2. Start JMeter services
docker compose up -d

# 3. Run light load test (100 users)
RUN_LOAD_TEST.bat light

# 4. View results
# HTML report will be generated in: reports\light_TIMESTAMP\index.html
```

---

## Test Scenarios

### Pre-configured Scenarios

| Scenario | Users | Ramp-up | Duration | Use Case |
|----------|-------|---------|----------|----------|
| **light** | 100 | 60s | 5min | Development testing, smoke tests |
| **medium** | 1,000 | 120s | 5min | Performance validation, staging |
| **heavy** | 10,000 | 300s | 5min | Stress testing, capacity planning |
| **custom** | Variable | Variable | Variable | Specific test requirements |

### What Each Test Does

All scenarios execute the following user journey:

1. **Health Check** - Verify backend is responding
2. **Login** - Authenticate with credentials (admin/admin123)
3. **Get Candidates** - Fetch candidate list (authenticated)
4. **Get Employees** - Fetch employee list (authenticated)
5. **Get Factories** - Fetch factory list (authenticated)
6. **Think Time** - Random delay (1-4 seconds) between requests

This simulates a typical user browsing the application.

---

## Running Tests

### Standard Scenarios

**Linux/macOS:**
```bash
# Light load (100 users, 5 minutes)
./run-load-test.sh light

# Medium load (1000 users, 5 minutes)
./run-load-test.sh medium

# Heavy load (10000 users, 5 minutes)
./run-load-test.sh heavy

# Custom duration (medium load for 10 minutes)
./run-load-test.sh medium 600
```

**Windows:**
```cmd
# Light load
RUN_LOAD_TEST.bat light

# Medium load
RUN_LOAD_TEST.bat medium

# Heavy load
RUN_LOAD_TEST.bat heavy
```

### Custom Scenarios

**Linux/macOS:**
```bash
# Custom: 500 users, 90s ramp-up, 10min duration
./run-load-test.sh custom 600 500 90

# Generate custom test plan
./generate-test-plan.sh custom 500 90 600
```

### Distributed Testing

The setup automatically uses all 3 slave instances for distributed load generation:

```bash
# Master coordinates, slaves generate load
# Automatically configured in run-load-test.sh
# -R jmeter-slave-1,jmeter-slave-2,jmeter-slave-3
```

---

## Understanding Results

### Output Files

After each test, you'll find:

```
docker/load-test/
├── results/
│   └── SCENARIO_TIMESTAMP/
│       ├── results.jtl          # Raw test data (CSV format)
│       └── summary.txt          # Test summary
├── reports/
│   └── SCENARIO_TIMESTAMP/
│       ├── index.html           # Main HTML report (OPEN THIS!)
│       ├── content/             # Report assets
│       └── statistics.json      # JSON summary
└── test-plans/
    └── SCENARIO-load.jmx        # JMeter test plan
```

### HTML Report

The HTML report (`reports/SCENARIO_TIMESTAMP/index.html`) contains:

1. **Test and Report Information**
   - Test duration, start/end time
   - Total requests, throughput

2. **APDEX (Application Performance Index)**
   - Score: 0 (poor) to 1 (excellent)
   - Based on response time thresholds

3. **Requests Summary**
   - Total requests
   - Success rate (should be >99%)
   - Error rate (should be <1%)

4. **Statistics**
   - Min/Max/Average response times
   - 90th, 95th, 99th percentiles
   - Throughput (requests/second)
   - KB/sec

5. **Charts**
   - Response times over time
   - Throughput over time
   - Response time percentiles
   - Active threads over time

6. **Errors** (if any)
   - Error types
   - Error messages
   - Failure percentage

### Key Metrics to Monitor

**Response Time:**
- **Good**: Average < 200ms, 95th percentile < 500ms
- **Acceptable**: Average < 500ms, 95th percentile < 1000ms
- **Poor**: Average > 1000ms or high variance

**Throughput:**
- Requests per second (RPS)
- Should scale linearly with backend instances
- Compare: 1 instance vs 3 instances

**Error Rate:**
- **Excellent**: < 0.1%
- **Good**: < 1%
- **Acceptable**: < 5%
- **Poor**: > 5%

**Success Rate:**
- **Target**: > 99.9%
- **Minimum**: > 95%

---

## Monitoring

### Real-Time Monitoring

While test is running, monitor via:

**Grafana Dashboards:**
```
URL: http://localhost:3002
User: admin
Password: admin

Dashboards:
- JMeter Performance (if configured)
- Backend metrics
- Infrastructure metrics
```

**Prometheus Queries:**
```
URL: http://localhost:9090

Useful queries:
- rate(http_requests_total[1m])
- histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

**Docker Logs:**
```bash
# Backend logs
docker compose logs -f backend

# Nginx access logs (shows load distribution)
docker compose logs -f nginx | grep "/api/"

# JMeter master logs
docker compose -f docker/load-test/docker-compose.yml logs -f jmeter-master
```

### System Metrics

Monitor system resources during tests:

```bash
# Docker stats (CPU, memory per container)
docker stats

# Backend instances specifically
docker stats $(docker ps --filter "name=backend" --format "{{.Names}}")
```

---

## Advanced Usage

### Modifying Test Plans

Edit generated `.jmx` files or modify the generator:

```bash
# Edit generator script
nano generate-test-plan.sh

# Regenerate all test plans
./generate-test-plan.sh all
```

### Adding Custom Endpoints

Edit `generate-test-plan.sh` and add HTTP samplers:

```xml
<HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="Custom Endpoint">
  <stringProp name="HTTPSampler.path">/api/your-endpoint</stringProp>
  <stringProp name="HTTPSampler.method">GET</stringProp>
  <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
</HTTPSamplerProxy>
```

### Scaling JMeter Slaves

Add more slaves in `docker-compose.yml`:

```yaml
jmeter-slave-4:
  image: justb4/jmeter:5.6.3
  container_name: uns-jmeter-slave-4
  environment:
    - JVM_ARGS=-Xms512m -Xmx1024m
  networks:
    - uns-loadtest
  command: jmeter-server
```

Update `run-load-test.sh`:
```bash
JMETER_SLAVES="uns-jmeter-slave-1,uns-jmeter-slave-2,uns-jmeter-slave-3,uns-jmeter-slave-4"
```

### Tuning JMeter Performance

Increase JVM memory for large tests:

```yaml
# docker-compose.yml
jmeter-master:
  environment:
    - JVM_ARGS=-Xms1024m -Xmx4096m
```

### InfluxDB Integration

Configure JMeter to send real-time metrics:

1. Start InfluxDB:
   ```bash
   docker compose up -d influxdb
   ```

2. Configure backend listener in test plan (already configured in generator)

3. Access metrics:
   ```
   URL: http://localhost:8086
   Org: uns-kikaku
   Token: jmeter-token-2025
   ```

---

## Troubleshooting

### Issue: JMeter services won't start

**Solution:**
```bash
# Check for port conflicts
docker compose -f docker/load-test/docker-compose.yml down
docker compose -f docker/load-test/docker-compose.yml up -d

# View logs
docker compose -f docker/load-test/docker-compose.yml logs
```

### Issue: Cannot connect to backend

**Symptoms:** Test fails immediately with connection errors

**Solution:**
```bash
# 1. Verify main app is running
docker compose --profile dev ps

# 2. Check nginx is healthy
docker compose exec nginx curl http://localhost/api/health

# 3. Verify network connectivity
docker compose -f docker/load-test/docker-compose.yml exec jmeter-master \
  curl http://nginx:80/api/health
```

### Issue: High error rate (>5%)

**Possible causes:**
1. Backend instances are overwhelmed
2. Database connection pool exhausted
3. Network issues

**Solutions:**
```bash
# 1. Scale backend
docker compose --profile dev up -d --scale backend=5

# 2. Check backend logs for errors
docker compose logs backend | grep -i error

# 3. Monitor database connections
docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c \
  "SELECT count(*) FROM pg_stat_activity;"

# 4. Reduce test load
./run-load-test.sh light  # Start with lighter load
```

### Issue: JMeter runs out of memory

**Symptoms:** Test crashes mid-execution with OutOfMemoryError

**Solution:**
```bash
# Increase JVM heap in docker-compose.yml
# jmeter-master:
#   environment:
#     - JVM_ARGS=-Xms2048m -Xmx4096m

# Restart services
docker compose -f docker/load-test/docker-compose.yml restart
```

### Issue: Results file is huge

**Solution:**
```bash
# Compress old results
cd docker/load-test/results
gzip *.jtl

# Clean up old results (keep last 30 days)
find results/ -type f -mtime +30 -delete
find reports/ -type d -mtime +30 -exec rm -rf {} +
```

---

## Performance Targets

### Development Environment

| Metric | Target | Acceptable |
|--------|--------|------------|
| Avg Response Time | < 100ms | < 200ms |
| 95th Percentile | < 250ms | < 500ms |
| Throughput | > 100 RPS | > 50 RPS |
| Success Rate | > 99.5% | > 98% |
| Error Rate | < 0.5% | < 2% |

### Production Environment

| Metric | Target | Acceptable |
|--------|--------|------------|
| Avg Response Time | < 50ms | < 100ms |
| 95th Percentile | < 150ms | < 300ms |
| Throughput | > 500 RPS | > 250 RPS |
| Success Rate | > 99.9% | > 99% |
| Error Rate | < 0.1% | < 1% |

---

## Best Practices

1. **Start Small**: Begin with `light` scenario, then scale up
2. **Baseline First**: Run tests on single backend instance to establish baseline
3. **Scale Testing**: Test with 1, 2, 3, 5 backend instances to find optimal count
4. **Monitor Resources**: Watch CPU, memory, database connections during tests
5. **Iterate**: Run tests multiple times to account for variance
6. **Document**: Keep notes of configuration changes and their impact
7. **Clean Up**: Archive or delete old test results regularly

---

## Next Steps

After running load tests:

1. **Analyze Results**: Review HTML reports for bottlenecks
2. **Compare Scenarios**: Compare light vs medium vs heavy
3. **Test Scaling**: Run same test with 1, 3, 5 backend instances
4. **Optimize**: Based on results, tune backend/database/nginx
5. **Set Baselines**: Document acceptable performance thresholds
6. **Automate**: Integrate into CI/CD pipeline (optional)

---

## Related Documentation

- [Backend Scaling Guide](../SCALING.md) - Horizontal scaling setup
- [Disaster Recovery](../scripts/simulate-failure.sh) - Failure testing
- [Monitoring](../../docs/observability/) - Prometheus + Grafana setup

---

**Version History:**
- v1.0.0 (2025-11-12): Initial load testing infrastructure
