# Disaster Recovery Plan

## Overview

This document outlines the disaster recovery procedures for UNS-ClaudeJP 5.4.1, including Recovery Time Objectives (RTO), Recovery Point Objectives (RPO), and automated failure testing.

**Version:** 1.0.0
**Last Updated:** 2025-11-12
**Author:** Claude Code

---

## Table of Contents

- [Recovery Objectives](#recovery-objectives)
- [Failure Scenarios](#failure-scenarios)
- [Automated Testing](#automated-testing)
- [Manual Recovery Procedures](#manual-recovery-procedures)
- [Backup and Restore](#backup-and-restore)
- [Monitoring and Alerts](#monitoring-and-alerts)
- [Escalation Procedures](#escalation-procedures)

---

## Recovery Objectives

### RTO (Recovery Time Objective)

**Definition**: Maximum acceptable time for service restoration after a failure.

| Service | RTO Target | Acceptable | Critical |
|---------|-----------|------------|----------|
| **Database (PostgreSQL)** | 30 seconds | 60 seconds | 120 seconds |
| **Backend (FastAPI)** | 15 seconds | 30 seconds | 60 seconds |
| **Frontend (Next.js)** | 20 seconds | 40 seconds | 80 seconds |
| **Redis Cache** | 20 seconds | 40 seconds | 80 seconds |
| **Nginx** | 10 seconds | 20 seconds | 40 seconds |
| **Complete System** | 60 seconds | 120 seconds | 300 seconds |

### RPO (Recovery Point Objective)

**Definition**: Maximum acceptable data loss measured in time.

| Data Type | RPO Target | Backup Frequency | Retention |
|-----------|-----------|------------------|-----------|
| **Database** | 0 (no loss) | Continuous WAL | 30 days |
| **Uploaded Files** | 24 hours | Daily incremental | 30 days |
| **Configuration** | 0 (version control) | Git commits | Indefinite |
| **Logs** | 24 hours | Daily rotation | 30 days |
| **Application State** | 0 (stateless) | N/A | N/A |

### Service Level Objectives (SLO)

| Metric | Target | Measurement Period |
|--------|--------|-------------------|
| **Availability** | 99.9% (8.76h downtime/year) | Monthly |
| **MTBF** | 720 hours (30 days) | Quarterly |
| **MTTR** | < 30 minutes | Per incident |
| **Data Durability** | 99.999% | Annual |

---

## Failure Scenarios

### 1. Database Failure

**Scenario**: PostgreSQL container crashes or becomes unresponsive

**Impact**:
- ❌ All write operations fail
- ❌ Read operations fail (unless cached)
- ✅ Frontend remains accessible (shows error states)
- ✅ Static content remains available

**Detection**:
- Health check failures (interval: 10s)
- Connection timeout errors in backend logs
- Prometheus alert: `up{job="postgres"} == 0`

**Automatic Recovery**:
- Docker restart policy: `always`
- Expected recovery time: 20-30 seconds
- Health check retries: 10 attempts

**Data Protection**:
- Persistent volume: `postgres_data`
- Write-Ahead Logging (WAL) enabled
- Daily automated backups
- Point-in-time recovery capability

**Verification**:
```bash
# Run automated test
./docker/scripts/simulate-failure.sh db --auto-recover

# Expected result:
# - RTO: < 30 seconds
# - RPO: 0 (no data loss)
# - Success rate: 100%
```

---

### 2. Backend Failure

**Scenario**: One or more backend instances crash

**Impact**:
- ✅ High availability maintained (if multiple instances)
- ⚠️ Partial degradation (single instance scenario)
- ⚠️ Increased latency during recovery

**Detection**:
- Health check failures (interval: 30s)
- Nginx upstream errors
- Prometheus alert: `up{job="backend"} < replica_count`

**Automatic Recovery**:
- Docker restart policy: `always`
- Nginx removes failed instance from pool
- Expected recovery time: 15-20 seconds
- Load redistributed to healthy instances

**High Availability**:
- Recommended: 2-3 backend instances minimum
- Nginx performs health checks every 30s
- Failed instances excluded from load balancing

**Verification**:
```bash
# Run automated test
./docker/scripts/simulate-failure.sh backend --auto-recover

# Expected result:
# - RTO: < 20 seconds
# - HA maintained: > 90% success rate
# - Zero user-visible errors
```

---

### 3. Redis Cache Failure

**Scenario**: Redis container crashes or becomes unresponsive

**Impact**:
- ✅ Backend continues operation (graceful degradation)
- ⚠️ Performance degradation (direct DB queries)
- ⚠️ Increased database load
- ⚠️ Session data loss (users re-authenticate)

**Detection**:
- Health check failures (interval: 10s)
- Increased DB query latency
- Prometheus alert: `up{job="redis"} == 0`

**Automatic Recovery**:
- Docker restart policy: `always`
- Expected recovery time: 10-20 seconds
- Cache warming: automatic on reconnect

**Graceful Degradation**:
- Backend falls back to database
- Session data regenerated on login
- No critical functionality lost

**Verification**:
```bash
# Run automated test
./docker/scripts/simulate-failure.sh redis --auto-recover

# Expected result:
# - RTO: < 20 seconds
# - Degraded mode: > 80% success rate
# - Automatic cache recovery
```

---

### 4. Frontend Failure

**Scenario**: Next.js frontend container crashes

**Impact**:
- ❌ User interface unavailable
- ✅ API remains accessible
- ✅ Backend operations continue

**Detection**:
- Health check failures (interval: 30s)
- HTTP 502/504 errors
- Prometheus alert: `up{job="frontend"} == 0`

**Automatic Recovery**:
- Docker restart policy: `always`
- Expected recovery time: 20-30 seconds (includes build)

**Verification**:
```bash
# Simulate frontend failure
docker compose stop frontend

# Verify automatic restart
docker compose ps frontend

# Expected: "Up (healthy)" within 30 seconds
```

---

### 5. Nginx Failure

**Scenario**: Nginx reverse proxy crashes

**Impact**:
- ❌ All HTTP/HTTPS traffic blocked
- ✅ Backend services continue running
- ✅ Direct service access possible (development)

**Detection**:
- Health check failures (interval: 30s)
- Connection refused errors
- Prometheus alert: `up{job="nginx"} == 0`

**Automatic Recovery**:
- Docker restart policy: `always`
- Expected recovery time: 5-10 seconds

**Workaround** (temporary):
```bash
# Direct backend access (dev only)
curl http://localhost:8000/api/health

# Direct frontend access
curl http://localhost:3000
```

---

### 6. Network Partition

**Scenario**: Network connectivity lost between services

**Impact**:
- ⚠️ Service-specific failures
- ✅ High availability handles isolated failures
- ⚠️ Cascading failures possible

**Detection**:
- Connection timeout errors
- Service health checks fail
- Prometheus alert: `up{job="*"} == 0` for multiple services

**Automatic Recovery**:
- Docker network auto-heals on reconnection
- Services reconnect automatically
- Expected recovery time: < 30 seconds

**Verification**:
```bash
# Run network partition test
./docker/scripts/simulate-failure.sh network --auto-recover

# Expected result:
# - Services reconnect automatically
# - No data loss
# - HA maintained if multiple instances
```

---

### 7. Complete System Failure

**Scenario**: Host server crash, power failure, or hardware failure

**Impact**:
- ❌ All services unavailable
- ✅ Data persisted in volumes
- ✅ Configuration in version control

**Recovery Procedure**:
```bash
# 1. Restart Docker daemon
sudo systemctl start docker

# 2. Start all services
docker compose --profile dev up -d

# 3. Verify health
docker compose ps

# 4. Check data integrity
./docker/scripts/verify-system.sh

# Expected recovery time: 2-5 minutes
```

**Data Safety**:
- All data in persistent volumes
- Automatic backup before shutdown (if graceful)
- Daily backups retained for 30 days

---

## Automated Testing

### Running Disaster Recovery Tests

**Linux/macOS:**
```bash
# Test all scenarios
./docker/scripts/simulate-failure.sh all --auto-recover

# Test specific scenario
./docker/scripts/simulate-failure.sh db --auto-recover
./docker/scripts/simulate-failure.sh backend --auto-recover
./docker/scripts/simulate-failure.sh redis --auto-recover
./docker/scripts/simulate-failure.sh network --auto-recover

# Manual recovery (interactive)
./docker/scripts/simulate-failure.sh db
```

**Windows:**
```cmd
# Test all scenarios
scripts\TEST_DISASTER_RECOVERY.bat all

# Test specific scenario
scripts\TEST_DISASTER_RECOVERY.bat db
scripts\TEST_DISASTER_RECOVERY.bat backend
scripts\TEST_DISASTER_RECOVERY.bat redis
```

### Test Schedule

**Recommended Testing Frequency**:
- **Development**: Weekly (automated in CI/CD)
- **Staging**: Bi-weekly
- **Production**: Monthly (during maintenance window)
- **After Changes**: Always (before deployment)

### Test Reports

Test results are logged to:
```
docker/scripts/logs/disaster-recovery/
├── test_db_20251112_143022.log
├── test_backend_20251112_143122.log
├── test_redis_20251112_143222.log
└── test_all_20251112_143322.log
```

**Key Metrics in Reports**:
- Recovery time (RTO compliance)
- Data integrity (RPO compliance)
- Success rate during failure
- Service health after recovery

---

## Manual Recovery Procedures

### Database Recovery

**Symptoms**:
- Backend logs show database connection errors
- Health endpoint returns unhealthy
- Adminer cannot connect

**Recovery Steps**:
```bash
# 1. Check database status
docker compose ps db

# 2. View database logs
docker compose logs db --tail 100

# 3. Restart database
docker compose restart db

# 4. Wait for healthy status (max 30s)
docker compose ps db

# 5. Verify connectivity
docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "SELECT 1;"

# 6. Check data integrity
docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "SELECT count(*) FROM candidates;"

# If data is corrupt, restore from backup:
./scripts/RESTAURAR_DATOS.bat backups/latest.sql.gz
```

### Backend Recovery

**Symptoms**:
- API returns 502/504 errors
- Frontend shows connection errors
- Nginx logs show upstream errors

**Recovery Steps**:
```bash
# 1. Check backend status
docker compose ps backend

# 2. View backend logs
docker compose logs backend --tail 100

# 3. Restart all backend instances
docker compose restart backend

# 4. Or recreate with scaling
docker compose up -d --scale backend=3 --force-recreate

# 5. Verify health
curl http://localhost/api/health

# 6. Check all instances
docker compose ps backend
```

### Redis Recovery

**Symptoms**:
- Slow performance
- Session data lost
- Backend logs show Redis connection errors

**Recovery Steps**:
```bash
# 1. Check Redis status
docker compose ps redis

# 2. View Redis logs
docker compose logs redis --tail 100

# 3. Restart Redis
docker compose restart redis

# 4. Verify connectivity
docker exec uns-claudejp-redis redis-cli --raw incr ping

# 5. Check cache warming
# (automatic on backend reconnect)
```

### Complete System Recovery

**When to Use**: After host reboot, Docker daemon crash, or infrastructure failure

**Recovery Steps**:
```bash
# 1. Verify Docker is running
docker version

# 2. Start all services
cd /path/to/UNS-ClaudeJP-5.4.1
docker compose --profile dev up -d

# 3. Monitor startup (takes 2-3 minutes)
docker compose logs -f

# 4. Verify all services healthy
docker compose ps

# Expected output: All services "Up (healthy)"

# 5. Verify data integrity
docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c \
  "SELECT count(*) FROM candidates;"

# 6. Test application functionality
curl http://localhost/api/health
curl http://localhost:3000

# 7. Check logs for errors
docker compose logs --tail 100 | grep -i error
```

---

## Backup and Restore

### Automated Backups

**Backup Service**: Runs daily at 02:00 JST

```yaml
# docker-compose.yml
backup:
  container_name: uns-claudejp-backup
  environment:
    BACKUP_TIME: "02:00"
    RETENTION_DAYS: 30
  volumes:
    - ./backups:/backups
```

**Backup Location**:
```
backups/
├── backup_20251112_020000.sql.gz
├── backup_20251111_020000.sql.gz
└── ...
```

### Manual Backup

**Linux/macOS:**
```bash
# Full database backup
docker exec uns-claudejp-db pg_dump -U uns_admin -d uns_claudejp -F c -f /tmp/backup.dump

# Copy to host
docker cp uns-claudejp-db:/tmp/backup.dump ./backups/manual_$(date +%Y%m%d).dump

# Or use backup script
./scripts/BACKUP_DATOS.bat
```

**Windows:**
```cmd
# Run backup script
scripts\BACKUP_DATOS.bat

# Backup saved to: backups\backup_YYYYMMDD_HHMMSS.sql.gz
```

### Restore from Backup

**Linux/macOS:**
```bash
# 1. Stop backend to prevent writes
docker compose stop backend

# 2. Restore database
cat backups/backup_20251112.sql.gz | gunzip | \
  docker exec -i uns-claudejp-db psql -U uns_admin -d uns_claudejp

# 3. Restart backend
docker compose start backend

# 4. Verify data
docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c \
  "SELECT count(*) FROM candidates;"
```

**Windows:**
```cmd
# Run restore script
scripts\RESTAURAR_DATOS.bat backups\backup_20251112.sql.gz

# Verify restoration
docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "SELECT count(*) FROM candidates;"
```

---

## Monitoring and Alerts

### Health Check Endpoints

| Service | Endpoint | Interval | Timeout |
|---------|----------|----------|---------|
| Backend | http://localhost:8000/api/health | 30s | 10s |
| Frontend | http://localhost:3000 | 30s | 10s |
| Nginx | http://localhost/nginx-health | 30s | 10s |
| Database | `pg_isready` | 10s | 10s |
| Redis | `redis-cli ping` | 10s | 5s |

### Prometheus Alerts

**Critical Alerts** (immediate action required):
```promql
# Service down
up{job=~"backend|frontend|postgres|redis"} == 0

# High error rate
rate(http_requests_total{status=~"5.."}[5m]) > 0.1

# Database connections exhausted
pg_stat_database_numbackends / pg_settings_max_connections > 0.9
```

**Warning Alerts** (investigate within 30 minutes):
```promql
# High response time
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1

# Disk space low
(node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.2

# Memory usage high
container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9
```

### Log Monitoring

**Critical Log Patterns**:
```bash
# Watch for critical errors
docker compose logs -f | grep -i "fatal\|critical\|emergency"

# Database errors
docker compose logs db | grep -i "error\|fail"

# Backend errors
docker compose logs backend | grep -i "500\|error"
```

---

## Escalation Procedures

### Incident Severity Levels

| Level | Description | Response Time | Escalation |
|-------|-------------|---------------|------------|
| **P1 - Critical** | Complete system down | 15 minutes | Immediate |
| **P2 - High** | Major functionality impaired | 1 hour | 30 minutes |
| **P3 - Medium** | Partial functionality impaired | 4 hours | 2 hours |
| **P4 - Low** | Minor issue, no impact | 24 hours | 12 hours |

### Response Workflow

**P1 - Critical Incident**:
1. **Detect** (0-5 min):
   - Monitoring alert triggers
   - Automated notification sent
   - On-call engineer paged

2. **Assess** (5-10 min):
   - Check service status
   - Review logs
   - Determine root cause

3. **Mitigate** (10-15 min):
   - Execute recovery procedure
   - Verify service restoration
   - Monitor for recurrence

4. **Resolve** (15-30 min):
   - Full system verification
   - Data integrity check
   - Update status page

5. **Post-Mortem** (24-48 hours):
   - Root cause analysis
   - Prevention measures
   - Documentation update

### Contact Information

**On-Call Rotation**:
- Primary: [Contact details]
- Secondary: [Contact details]
- Escalation: [Management contact]

**External Support**:
- Docker Support: [Details]
- Cloud Provider: [Details]
- Database DBA: [Details]

---

## Best Practices

1. **Regular Testing**: Test disaster recovery procedures monthly
2. **Documentation**: Keep runbooks updated with recent changes
3. **Automation**: Automate recovery where possible
4. **Monitoring**: Ensure all critical services have health checks
5. **Backups**: Verify backups daily, test restore quarterly
6. **Communication**: Update stakeholders during incidents
7. **Review**: Conduct post-mortems for all P1/P2 incidents
8. **Training**: Train all engineers on recovery procedures

---

## Appendix

### Quick Reference Commands

```bash
# Check all service status
docker compose ps

# Restart specific service
docker compose restart [service]

# View service logs
docker compose logs -f [service]

# Run disaster recovery test
./docker/scripts/simulate-failure.sh all --auto-recover

# Create manual backup
./scripts/BACKUP_DATOS.bat

# Restore from backup
./scripts/RESTAURAR_DATOS.bat backups/backup_YYYYMMDD.sql.gz

# Scale backend for high availability
docker compose up -d --scale backend=3

# Monitor system resources
docker stats
```

### Related Documentation

- [Backend Scaling](SCALING.md) - Horizontal scaling procedures
- [Load Testing](load-test/README.md) - Performance testing
- [Monitoring](../docs/observability/) - Prometheus + Grafana setup
- [Troubleshooting](../docs/04-troubleshooting/TROUBLESHOOTING.md) - Common issues

---

**Version History**:
- v1.0.0 (2025-11-12): Initial disaster recovery plan and automated testing
