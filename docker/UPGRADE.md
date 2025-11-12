# Deployment and Upgrade Strategies

## Overview

This document describes deployment and upgrade strategies for UNS-ClaudeJP 5.4.1, including blue-green deployments, canary releases, rolling updates, and rollback procedures for zero-downtime deployments.

**Version:** 1.0.0
**Last Updated:** 2025-11-12
**Author:** Claude Code

---

## Table of Contents

- [Deployment Strategies](#deployment-strategies)
- [Blue-Green Deployment](#blue-green-deployment)
- [Canary Release](#canary-release)
- [Rolling Update](#rolling-update)
- [Rollback Procedures](#rollback-procedures)
- [Version Management](#version-management)
- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Post-Deployment Verification](#post-deployment-verification)

---

## Deployment Strategies

### Strategy Comparison

| Strategy | Downtime | Risk | Complexity | Use Case |
|----------|----------|------|------------|----------|
| **Blue-Green** | Zero | Low | Medium | Production releases |
| **Canary** | Zero | Very Low | High | High-risk changes |
| **Rolling** | Zero | Medium | Low | Routine updates |
| **Recreate** | Yes | Low | Very Low | Development only |

### Choosing a Strategy

**Use Blue-Green when**:
- Deploying to production
- Want instant rollback capability
- Have sufficient resources (2x capacity)
- Need zero downtime

**Use Canary when**:
- Testing new features in production
- Want gradual exposure
- Need detailed monitoring
- High-risk changes

**Use Rolling when**:
- Routine updates (patches, minor versions)
- Limited resources
- Accept brief performance impact
- Automated deployments

---

## Blue-Green Deployment

### Concept

Run two identical production environments:
- **Blue**: Current production version
- **Green**: New version being deployed

Switch traffic from Blue to Green instantly when ready.

```
┌──────────┐
│  Users   │
└────┬─────┘
     │
┌────▼─────┐
│  Router  │ ← Switch here
│ (Nginx)  │
└────┬─────┘
     │
     ├─────────────┬─────────────┐
     │             │             │
┌────▼────┐   ┌────▼────┐   ┌────▼────┐
│ Blue v1 │   │Green v2 │   │Green v2 │
│(current)│   │  (new)  │   │  (new)  │
└─────────┘   └─────────┘   └─────────┘
     ↑             ↑             ↑
     └─────────────┴─────────────┘
              Database
```

### Implementation

#### Step 1: Prepare New Version

```bash
# Build new version
cd UNS-ClaudeJP-5.4.1

# Tag new version
git tag v5.4.2
export NEW_VERSION=v5.4.2

# Build new images
docker compose build backend frontend
docker tag uns-claudejp-backend:latest uns-claudejp-backend:${NEW_VERSION}
docker tag uns-claudejp-frontend:latest uns-claudejp-frontend:${NEW_VERSION}
```

#### Step 2: Deploy Green Environment

```bash
# Create docker-compose.green.yml
cat > docker-compose.green.yml <<EOF
services:
  backend-green:
    image: uns-claudejp-backend:${NEW_VERSION}
    container_name: uns-claudejp-backend-green
    env_file: .env
    environment:
      # Same as blue, but separate instances
      DATABASE_URL: postgresql://\${POSTGRES_USER}:\${POSTGRES_PASSWORD}@db:5432/\${POSTGRES_DB}
      DEPLOYMENT_COLOR: green
    volumes:
      - ./backend:/app
      - ./uploads:/app/uploads
    depends_on:
      db:
        condition: service_healthy
    networks:
      - uns-network
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 30s

  frontend-green:
    image: uns-claudejp-frontend:${NEW_VERSION}
    container_name: uns-claudejp-frontend-green
    env_file: .env
    environment:
      NEXT_PUBLIC_API_URL: http://backend-green:8000
      DEPLOYMENT_COLOR: green
    volumes:
      - ./frontend:/app
    depends_on:
      backend-green:
        condition: service_healthy
    networks:
      - uns-network
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://localhost:3000 || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 30s

networks:
  uns-network:
    external: true
EOF

# Deploy green environment
docker compose -f docker-compose.green.yml up -d

# Wait for green to be healthy
docker compose -f docker-compose.green.yml ps
```

#### Step 3: Test Green Environment

```bash
# Test green directly (not through nginx yet)
docker exec uns-claudejp-backend-green curl http://localhost:8000/api/health
docker exec uns-claudejp-frontend-green curl http://localhost:3000

# Run smoke tests against green
curl -s http://backend-green:8000/api/health
curl -s http://frontend-green:3000

# Run full test suite
./docker/scripts/test-deployment.sh green
```

#### Step 4: Database Migrations

```bash
# Run migrations on green (if needed)
# IMPORTANT: Migrations must be backward compatible with blue!

docker exec uns-claudejp-backend-green bash -c "cd /app && alembic upgrade head"

# Verify migrations
docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "\d+"
```

#### Step 5: Switch Traffic (Nginx)

Update nginx configuration to route to green:

```bash
# Create new nginx config
cat > docker/nginx/nginx-green.conf <<EOF
upstream backend {
    server backend-green:8000;
    keepalive 32;
}

upstream frontend {
    server frontend-green:3000;
    keepalive 32;
}
# ... rest of config
EOF

# Update nginx
docker cp docker/nginx/nginx-green.conf uns-claudejp-nginx:/etc/nginx/nginx.conf
docker exec uns-claudejp-nginx nginx -t
docker exec uns-claudejp-nginx nginx -s reload

# Or restart nginx
docker compose restart nginx
```

**Alternative: Use environment variable**

```yaml
# docker-compose.yml
nginx:
  environment:
    BACKEND_HOST: ${BACKEND_COLOR:-backend}:8000
    FRONTEND_HOST: ${FRONTEND_COLOR:-frontend}:3000
```

```bash
# Switch to green
export BACKEND_COLOR=backend-green
export FRONTEND_COLOR=frontend-green
docker compose restart nginx
```

#### Step 6: Monitor

```bash
# Monitor nginx access logs
docker compose logs -f nginx | grep -E "200|500"

# Monitor green instances
docker compose -f docker-compose.green.yml logs -f

# Check metrics in Grafana
# http://localhost:3001

# Monitor error rate
watch -n 1 'docker compose logs nginx --tail 100 | grep -c " 500 "'
```

#### Step 7: Keep Blue for Rollback

```bash
# Keep blue running for quick rollback
# Don't stop blue instances yet!

# After 24-48 hours of stable green, remove blue:
docker compose -f docker-compose.yml stop backend frontend
docker compose -f docker-compose.yml rm -f backend frontend
```

---

## Canary Release

### Concept

Gradually roll out new version to a small percentage of users, then increase exposure if metrics look good.

```
100% Traffic
     │
     ▼
┌─────────┐
│  Nginx  │
└────┬────┘
     │
     ├──90%──► Blue (v1) [Stable]
     │
     └──10%──► Green (v2) [Canary]

Gradually increase green traffic:
10% → 25% → 50% → 75% → 100%
```

### Implementation

#### Step 1: Deploy Canary Instance

```bash
# Build and deploy canary (green)
docker compose -f docker-compose.green.yml up -d --scale backend-green=1

# Verify canary is healthy
docker compose -f docker-compose.green.yml ps backend-green
```

#### Step 2: Configure Weighted Routing

**Option A: Nginx split_clients**

```nginx
# docker/nginx/nginx.conf

# Split traffic based on request ID
split_clients "${remote_addr}${request_uri}" $backend_pool {
    10%     backend-green;   # Canary
    *       backend;         # Stable
}

upstream backend {
    server backend:8000;
}

upstream backend-green {
    server backend-green:8000;
}

server {
    location /api/ {
        proxy_pass http://$backend_pool/api/;
    }
}
```

**Option B: Header-based routing**

```nginx
# Route specific users to canary
map $http_x_canary_user $backend_pool {
    default         backend;
    "enabled"       backend-green;
}

server {
    location /api/ {
        proxy_pass http://$backend_pool/api/;
    }
}
```

```bash
# Test canary with header
curl -H "X-Canary-User: enabled" http://localhost/api/health
```

#### Step 3: Monitor Canary Metrics

```bash
# Compare error rates: blue vs green
echo "Blue error rate:"
docker compose logs backend | grep -c "ERROR"

echo "Green error rate:"
docker compose -f docker-compose.green.yml logs backend-green | grep -c "ERROR"

# Compare response times
# Use Prometheus queries:
# histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{instance="backend"}[5m]))
# histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{instance="backend-green"}[5m]))
```

#### Step 4: Increase Traffic Gradually

```nginx
# Increase to 25%
split_clients "${remote_addr}${request_uri}" $backend_pool {
    25%     backend-green;
    *       backend;
}

# Increase to 50%
split_clients "${remote_addr}${request_uri}" $backend_pool {
    50%     backend-green;
    *       backend;
}

# Increase to 100%
split_clients "${remote_addr}${request_uri}" $backend_pool {
    100%    backend-green;
}
```

**Automation script:**

```bash
#!/bin/bash
# Gradual canary rollout

PERCENTAGES=(10 25 50 75 100)
WAIT_TIME=3600  # 1 hour between increases

for PCT in "${PERCENTAGES[@]}"; do
    echo "Increasing canary traffic to ${PCT}%"

    # Update nginx config
    sed -i "s/[0-9]\+%     backend-green/${PCT}%     backend-green/" docker/nginx/nginx.conf
    docker exec uns-claudejp-nginx nginx -s reload

    # Monitor for 1 hour
    echo "Monitoring for ${WAIT_TIME} seconds..."
    sleep ${WAIT_TIME}

    # Check error rate
    ERROR_RATE=$(docker compose -f docker-compose.green.yml logs backend-green --tail 1000 | grep -c "ERROR")

    if [ ${ERROR_RATE} -gt 10 ]; then
        echo "ERROR: High error rate detected (${ERROR_RATE}). Rolling back!"
        sed -i "s/${PCT}%     backend-green/0%     backend-green/" docker/nginx/nginx.conf
        docker exec uns-claudejp-nginx nginx -s reload
        exit 1
    fi

    echo "✓ ${PCT}% rollout successful"
done

echo "✓ Canary release completed successfully!"
```

---

## Rolling Update

### Concept

Update instances one at a time, ensuring at least N-1 instances are always running.

```
Initial state:
[Backend-1] [Backend-2] [Backend-3]
    v1          v1          v1

Step 1: Update instance 1
[Backend-1] [Backend-2] [Backend-3]
    v2          v1          v1

Step 2: Update instance 2
[Backend-1] [Backend-2] [Backend-3]
    v2          v2          v1

Step 3: Update instance 3
[Backend-1] [Backend-2] [Backend-3]
    v2          v2          v2
```

### Implementation

```bash
#!/bin/bash
# Rolling update script

NEW_VERSION=v5.4.2

# Build new version
docker compose build backend
docker tag uns-claudejp-backend:latest uns-claudejp-backend:${NEW_VERSION}

# Get current instance count
INSTANCE_COUNT=$(docker compose ps backend --format json | jq -s 'length')

# Update each instance
for i in $(seq 1 ${INSTANCE_COUNT}); do
    CONTAINER_NAME="uns-claudejp-backend-${i}"

    echo "Updating ${CONTAINER_NAME}..."

    # Remove old instance
    docker stop ${CONTAINER_NAME}
    docker rm ${CONTAINER_NAME}

    # Start new instance
    docker compose up -d --scale backend=${INSTANCE_COUNT} --no-recreate

    # Wait for new instance to be healthy
    echo "Waiting for new instance to be healthy..."
    sleep 10

    # Verify health
    NEW_CONTAINER=$(docker ps --filter "name=backend" --format "{{.Names}}" | grep -v "backend-[0-9]*$" | head -n 1)
    docker exec ${NEW_CONTAINER} python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"

    if [ $? -ne 0 ]; then
        echo "ERROR: New instance failed health check. Rolling back!"
        docker stop ${NEW_CONTAINER}
        # Restart old version (from backup)
        exit 1
    fi

    echo "✓ ${CONTAINER_NAME} updated successfully"

    # Wait before next instance
    sleep 5
done

echo "✓ Rolling update completed successfully!"
```

**Docker Compose Native Rolling Update:**

```yaml
# docker-compose.yml
backend:
  deploy:
    update_config:
      parallelism: 1        # Update 1 instance at a time
      delay: 10s            # Wait 10s between updates
      failure_action: rollback
      monitor: 60s          # Monitor for 60s after update
      max_failure_ratio: 0.3
      order: start-first    # Start new before stopping old
```

```bash
# Trigger rolling update
docker compose up -d --no-deps --build backend
```

---

## Rollback Procedures

### Immediate Rollback (Blue-Green)

**Fastest rollback: Switch back to blue**

```bash
# Option 1: Switch nginx config
export BACKEND_COLOR=backend
export FRONTEND_COLOR=frontend
docker compose restart nginx

# Option 2: Update nginx manually
docker cp docker/nginx/nginx-blue.conf uns-claudejp-nginx:/etc/nginx/nginx.conf
docker exec uns-claudejp-nginx nginx -s reload

# Verify rollback
curl http://localhost/api/health
docker compose logs nginx --tail 20
```

**Time to rollback: < 10 seconds**

### Rollback Canary Release

```bash
# Reduce canary traffic to 0%
sed -i 's/[0-9]\+%     backend-green/0%     backend-green/' docker/nginx/nginx.conf
docker exec uns-claudejp-nginx nginx -s reload

# Or remove canary completely
docker compose -f docker-compose.green.yml down

# Verify rollback
docker compose logs nginx --tail 20
```

**Time to rollback: < 30 seconds**

### Rollback Rolling Update

```bash
# Option 1: Rollback with docker compose
docker compose up -d --no-deps backend

# Option 2: Pull previous image
docker pull uns-claudejp-backend:v5.4.1
docker tag uns-claudejp-backend:v5.4.1 uns-claudejp-backend:latest
docker compose up -d --no-deps --force-recreate backend

# Option 3: Restore from backup image
docker load -i backups/backend_v5.4.1.tar
docker compose up -d --no-deps --force-recreate backend
```

**Time to rollback: 1-3 minutes**

### Database Rollback

**IMPORTANT: Database rollbacks are risky!**

```bash
# Option 1: Rollback migration (if safe)
docker exec uns-claudejp-backend bash -c "cd /app && alembic downgrade -1"

# Option 2: Restore from backup
./scripts/RESTAURAR_DATOS.bat backups/backup_before_upgrade.sql.gz

# Verify rollback
docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "\d+"
```

**Prevention: Always test migrations in staging first!**

---

## Version Management

### Versioning Strategy

**Semantic Versioning**: MAJOR.MINOR.PATCH

- **MAJOR**: Breaking changes (e.g., 5.x → 6.0)
- **MINOR**: New features, backward compatible (e.g., 5.4 → 5.5)
- **PATCH**: Bug fixes, backward compatible (e.g., 5.4.1 → 5.4.2)

### Tagging Releases

```bash
# Create git tag
git tag -a v5.4.2 -m "Release 5.4.2: Bug fixes and performance improvements"
git push origin v5.4.2

# Build and tag Docker images
docker compose build
docker tag uns-claudejp-backend:latest uns-claudejp-backend:v5.4.2
docker tag uns-claudejp-frontend:latest uns-claudejp-frontend:v5.4.2

# Push to registry (if using Docker registry)
docker push uns-claudejp-backend:v5.4.2
docker push uns-claudejp-frontend:v5.4.2
```

### Image Management

```bash
# List all versions
docker images | grep uns-claudejp

# Keep last 3 versions
docker images --format "{{.Repository}}:{{.Tag}}" | \
  grep uns-claudejp-backend | \
  tail -n +4 | \
  xargs docker rmi

# Save image for rollback
docker save uns-claudejp-backend:v5.4.1 -o backups/backend_v5.4.1.tar
```

---

## Pre-Deployment Checklist

### Before ANY Deployment

- [ ] Code reviewed and approved
- [ ] Tests passing (unit, integration, E2E)
- [ ] Database migrations tested in staging
- [ ] Backward compatibility verified
- [ ] Rollback plan documented
- [ ] Backup created (database, images)
- [ ] Monitoring dashboards ready
- [ ] On-call engineer notified
- [ ] Maintenance window scheduled (if needed)
- [ ] Changelog updated

### Production-Specific

- [ ] Staging deployment successful
- [ ] Load testing completed
- [ ] Security scan passed
- [ ] Performance benchmarks met
- [ ] Capacity planning reviewed
- [ ] DNS/CDN updated (if needed)
- [ ] SSL certificates valid
- [ ] Third-party integrations tested

---

## Post-Deployment Verification

### Immediate Checks (0-15 minutes)

```bash
# 1. All services healthy
docker compose ps

# 2. Health endpoints responding
curl http://localhost/api/health
curl http://localhost:3000

# 3. No errors in logs
docker compose logs --tail 100 | grep -i error

# 4. Database connectivity
docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "SELECT 1;"

# 5. Redis connectivity
docker exec uns-claudejp-redis redis-cli ping

# 6. Smoke tests
./docker/scripts/smoke-tests.sh
```

### Monitoring (15-60 minutes)

```bash
# 1. Check error rate
# Should be < 0.1%
docker compose logs nginx --tail 1000 | grep -c " 500 " || echo "0"

# 2. Check response times
# 95th percentile should be < 500ms
# View in Grafana: http://localhost:3001

# 3. Check resource usage
docker stats

# 4. Check database performance
docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c \
  "SELECT query, calls, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"
```

### Extended Monitoring (1-24 hours)

- Monitor error rates every hour
- Check database growth rate
- Verify backup jobs complete
- Monitor third-party API calls
- Check scheduled tasks execute
- Verify metrics in Prometheus/Grafana

---

## Best Practices

1. **Always Test in Staging**: Never deploy directly to production
2. **Use Blue-Green for Major Releases**: Instant rollback capability
3. **Use Canary for Risky Changes**: Gradual exposure reduces risk
4. **Database Migrations**: Always backward compatible
5. **Monitor Closely**: First 24 hours are critical
6. **Document Everything**: Deployment notes, issues, rollbacks
7. **Automate**: CI/CD pipeline for consistent deployments
8. **Communication**: Notify team before, during, after deployment

---

## Quick Reference

### Deployment Commands

```bash
# Blue-Green Deployment
docker compose -f docker-compose.green.yml up -d
docker compose restart nginx
docker compose -f docker-compose.yml down  # After verification

# Canary Release
docker compose -f docker-compose.green.yml up -d --scale backend-green=1
# Update nginx config with split_clients
docker exec uns-claudejp-nginx nginx -s reload

# Rolling Update
docker compose up -d --no-deps --build backend

# Rollback
docker compose restart nginx  # Blue-green
docker compose up -d --no-deps backend:v5.4.1  # Rolling
```

### Verification Commands

```bash
# Health check
curl http://localhost/api/health

# Version check
curl http://localhost/api/version

# Service status
docker compose ps

# Error rate
docker compose logs nginx --tail 1000 | grep -c " 500 "
```

---

**Related Documentation**:
- [Disaster Recovery](DISASTER_RECOVERY.md) - Failure recovery procedures
- [Scaling Guide](SCALING.md) - Horizontal scaling
- [Load Testing](load-test/README.md) - Performance testing

**Version History**:
- v1.0.0 (2025-11-12): Initial upgrade strategy documentation
