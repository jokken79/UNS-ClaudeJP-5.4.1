# 🚀 Production Deployment Guide - UNS-ClaudeJP 5.4.1

## Pre-Deployment Checklist

### 1. Code & Security Review
- [ ] All audit findings reviewed in AUDIT_REPORT_2025_11_14.md
- [ ] 7 critical issues resolved (confirmed in git history)
- [ ] No debug statements in code
- [ ] No hardcoded credentials
- [ ] All tests passing (run: ./run_all_tests.sh)

### 2. Configuration Setup
- [ ] .env.production file created with real values
- [ ] All "change-me-*" values replaced with SECURE passwords
- [ ] POSTGRES_PASSWORD is 32+ characters
- [ ] SECRET_KEY is 64+ characters
- [ ] REDIS_PASSWORD is 32+ characters
- [ ] GRAFANA_ADMIN_PASSWORD changed from default
- [ ] FRONTEND_URL updated to production domain
- [ ] BACKEND_CORS_ORIGINS updated to production domain

### 3. Infrastructure Preparation
- [ ] Docker and Docker Compose installed
- [ ] SSL/TLS certificates obtained (Let's Encrypt or CA)
- [ ] Nginx configured with certificates
- [ ] Database backups tested and working
- [ ] Monitoring tools configured (Grafana access verified)
- [ ] Email (SMTP) credentials tested

### 4. Database Preparation
- [ ] All migrations applied successfully
- [ ] Database backups taken
- [ ] Backup restore procedure tested
- [ ] Alembic current version matches latest

### 5. Testing
- [ ] All E2E tests passing (15 test suites)
- [ ] Backend pytest tests passing (35+)
- [ ] Frontend type-check passing
- [ ] Frontend build successful
- [ ] API health check responding
- [ ] Authentication working with test credentials

### 6. Monitoring & Alerting
- [ ] Grafana dashboards accessible
- [ ] Prometheus scraping metrics
- [ ] OpenTelemetry traces being collected
- [ ] Alert rules configured
- [ ] Logging configured and working

---

## Step-by-Step Deployment

### Phase 1: Pre-Production Staging (Mandatory)

**1.1 Deploy to Staging Environment**

```bash
# 1. On staging server
git clone https://github.com/your-org/UNS-ClaudeJP-5.4.1.git
cd UNS-ClaudeJP-5.4.1

# 2. Create staging .env
cp .env.production .env.staging
# Edit .env.staging with staging values (different from production)

# 3. Start services
docker compose --env-file .env.staging up -d

# 4. Wait for healthy
sleep 30
docker compose ps
```

**1.2 Run Full Test Suite on Staging**

```bash
# Run all tests
./run_all_tests.sh

# Expected: All tests pass (6 phases)
# If failures: Fix before proceeding to production
```

**1.3 Smoke Test in Staging**

```bash
# Test critical workflows manually
# 1. Login with test user
# 2. Create a candidate
# 3. Create an employee
# 4. Process payroll
# 5. Check Grafana dashboards
```

**1.4 Performance & Load Testing (Optional)**

```bash
# Run load test on staging to identify bottlenecks
# This ensures production can handle real traffic
```

**1.5 Security Scan (Optional)**

```bash
# Run OWASP/security scan on staging environment
# Verify no vulnerabilities before production
```

---

### Phase 2: Production Deployment

**2.1 Backup Everything**

```bash
# On production server

# 1. Backup existing database (if upgrading)
docker exec uns-claudejp-db pg_dump -U uns_admin uns_claudejp > \
  ./backups/pre-deployment-$(date +%Y%m%d-%H%M%S).sql

# 2. Backup code (if upgrading)
tar -czf ./backups/code-backup-$(date +%Y%m%d-%H%M%S).tar.gz ./

# 3. Backup docker volumes
docker run --rm -v postgres_data:/data -v ./backups:/backup \
  alpine tar czf /backup/postgres-data-$(date +%Y%m%d-%H%M%S).tar.gz -C / data
```

**2.2 Deploy Production Code**

```bash
# 1. Clone or update repository
git clone https://github.com/your-org/UNS-ClaudeJP-5.4.1.git
cd UNS-ClaudeJP-5.4.1

# 2. Checkout specific version/tag
git checkout v5.4.1  # or latest stable tag

# 3. Create production .env (with REAL production values)
# DO NOT copy from staging!
# Generate new SECRET_KEY, passwords, etc.
cp .env.production .env.prod
# Edit .env.prod with actual production credentials

# 4. Create SSL certificate directory
mkdir -p ./certs
# Copy SSL certificates to ./certs/
# Example: ./certs/fullchain.pem, ./certs/privkey.pem
```

**2.3 Build Docker Images**

```bash
# Build backend and frontend images
docker compose -f docker-compose.yml build

# This uses Dockerfile from docker/ directory
# Pulls base images and builds application images
```

**2.4 Start Services**

```bash
# 1. Stop old services (if any)
docker compose down  # Preserves volumes

# 2. Start new services with production .env
docker compose --env-file .env.prod up -d

# 3. Monitor startup (takes ~30-60 seconds)
docker compose logs -f
```

**2.5 Verify Deployment**

```bash
# 1. Check all services are healthy
docker compose ps
# All containers should show "healthy" or "running"

# 2. Test health endpoint
curl http://localhost:8000/api/health
# Should return: {"status": "ok", "version": "5.4.1", "environment": "production"}

# 3. Test database connection
docker exec uns-claudejp-backend alembic current
# Should show: add_search_indexes (latest migration)

# 4. Test Redis connection
docker exec uns-claudejp-redis redis-cli ping
# Should return: PONG

# 5. Test Grafana access
curl http://localhost:3001
# Should return: Grafana login page
```

**2.6 Configure Nginx (if needed)**

```bash
# 1. Edit nginx configuration
nano ./docker/nginx/nginx.conf

# 2. Update server_name to production domain
# 3. Uncomment SSL certificate lines if using HTTPS

# 4. Test nginx configuration
docker exec uns-claudejp-nginx nginx -t

# 5. Reload nginx
docker exec uns-claudejp-nginx nginx -s reload
```

---

### Phase 3: Post-Deployment Validation

**3.1 Functional Testing**

```bash
# 1. Test login with production credentials
curl -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"YOUR_PROD_PASSWORD"}'

# 2. Test protected endpoints
TOKEN=$(above_response)
curl -X GET http://localhost/api/candidates \
  -H "Authorization: Bearer $TOKEN"

# 3. Test database operations
# Create test candidate, employee, etc.

# 4. Test Grafana access with new credentials
# Admin user / new password
```

**3.2 Performance Verification**

```bash
# 1. Check API response times
time curl http://localhost/api/health

# 2. Monitor resource usage
docker stats

# 3. Check database query performance
docker exec uns-claudejp-backend \
  psql -U uns_admin -d uns_claudejp \
  -c "SELECT COUNT(*) FROM candidates;"
```

**3.3 Monitoring Setup**

```bash
# 1. Verify Grafana dashboards are working
# Access: http://localhost:3001

# 2. Verify Prometheus metrics collection
curl http://localhost:9090/api/v1/targets

# 3. Verify OpenTelemetry traces
# Access Grafana Tempo dashboard

# 4. Verify logs are being collected
docker compose logs backend | head -20
```

**3.4 Backup Verification**

```bash
# 1. Verify backups are being created
ls -lh ./backups/

# 2. Test backup restore procedure
# (Do this on a test environment, not production!)
docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp < backup.sql
```

---

### Phase 4: Cutover (Go Live)

**4.1 Update DNS**

```bash
# 1. Update DNS records to point to new production server
# Example: A record points to production IP

# 2. Verify DNS propagation
dig your-production-domain.com
# Should resolve to production IP
```

**4.2 Update External References**

```bash
# 1. Update any API documentation with new URLs
# 2. Notify users of any URL changes
# 3. Update client applications to use new URLs
```

**4.3 Monitor First 24 Hours**

```bash
# Monitor these metrics closely:
# 1. CPU and memory usage
docker stats

# 2. Disk I/O
iotop

# 3. Network bandwidth
iftop

# 4. Application logs
docker compose logs -f backend

# 5. Error rates
# Check Grafana dashboards

# 6. User activity
# Monitor login success rates
```

---

## Rollback Plan

If something goes wrong:

```bash
# 1. STOP current services
docker compose down

# 2. RESTORE from backup
cat ./backups/pre-deployment-*.sql | \
  docker exec -i uns-claudejp-db psql -U uns_admin uns_claudejp

# 3. RESTORE code from backup
tar -xzf ./backups/code-backup-*.tar.gz

# 4. START old services
docker compose --env-file .env.prod up -d

# 5. VERIFY everything works
docker compose ps
curl http://localhost:8000/api/health
```

---

## Production Operations

### Daily Checklist

```bash
# Run daily:
- [ ] Check disk space: df -h
- [ ] Check memory: free -h
- [ ] Check CPU: top
- [ ] Check backups exist: ls -lh ./backups/
- [ ] Check logs for errors: docker compose logs --tail=50 backend
- [ ] Verify Grafana dashboards
- [ ] Check database health
```

### Weekly Tasks

```bash
# Once per week:
- [ ] Review security logs
- [ ] Test backup restore
- [ ] Review monitoring alerts
- [ ] Update dependencies (if needed)
- [ ] Review performance metrics
```

### Monthly Tasks

```bash
# Once per month:
- [ ] Full security audit
- [ ] Performance optimization review
- [ ] Capacity planning
- [ ] Disaster recovery drill
- [ ] Documentation update
```

---

## Troubleshooting

### Services Won't Start

```bash
# 1. Check logs
docker compose logs

# 2. Check port conflicts
netstat -tulpn | grep LISTEN

# 3. Check volume permissions
ls -la ./postgres_data/

# 4. Rebuild images
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Database Connection Fails

```bash
# 1. Check DATABASE_URL in .env
grep DATABASE_URL .env.prod

# 2. Test connection directly
docker exec -it uns-claudejp-db \
  psql -U uns_admin -d uns_claudejp -c "SELECT 1;"

# 3. Check network
docker network ls
docker network inspect uns-network
```

### Performance Issues

```bash
# 1. Check resource limits
docker stats

# 2. Check slow queries
docker exec uns-claudejp-backend \
  psql -U uns_admin -d uns_claudejp \
  -c "SELECT query, calls, total_time FROM pg_stat_statements LIMIT 10;"

# 3. Check indexes
docker exec uns-claudejp-backend \
  psql -U uns_admin -d uns_claudejp -c "\di"
```

---

## Monitoring & Alerting

### Key Metrics to Monitor

1. **Application Health**
   - API response times
   - Error rate
   - Request throughput

2. **Infrastructure**
   - CPU usage
   - Memory usage
   - Disk usage
   - Network I/O

3. **Database**
   - Connection pool usage
   - Query execution time
   - Lock contention
   - Replication lag (if applicable)

4. **Security**
   - Failed login attempts
   - Unauthorized access attempts
   - SSL/TLS errors

### Setting up Alerts

Configure alerts in Grafana for:
- High CPU usage (>80%)
- High memory usage (>85%)
- High disk usage (>90%)
- API errors (>5%)
- Database connection pool exhausted
- Backup failed

---

## Scaling

### Horizontal Scaling (Add Backend Servers)

```bash
# Scale backend to 3 instances
docker compose up -d --scale backend=3

# Nginx will automatically load balance
# No reconfiguration needed
```

### Vertical Scaling (More Resources)

```bash
# Update docker-compose.yml with resource limits
# Restart services
docker compose down
docker compose up -d
```

---

## Support & Documentation

- AUDIT_REPORT_2025_11_14.md - Complete audit findings
- CLAUDE.md - Development guide
- API_VERIFICATION_GUIDE.md - API testing
- PLAYWRIGHT_TESTING_PLAN.md - E2E testing
- docs/ - Additional documentation

---

**Last Updated**: November 14, 2025  
**Deployment Status**: Ready for Production  
**Version**: 5.4.1

