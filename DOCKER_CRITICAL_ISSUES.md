# Docker Compose - CRITICAL ISSUES & FIXES

**Analysis Date**: 2025-11-14  
**Status**: ⚠️ CRITICAL - 4 blocking issues for production

---

## CRITICAL ISSUE #1: REDIS_PASSWORD Missing Documentation

**Severity**: 🔴 CRITICAL  
**Location**: 
- Missing from: `.env.example`
- Used in: `docker-compose.yml` line 68
- Service: `redis`

**Problem**:
```yaml
# docker-compose.yml line 68
command: redis-server --requirepass ${REDIS_PASSWORD}

# .env.example
# MISSING! No REDIS_PASSWORD variable defined
```

**Risk**: 
- If `REDIS_PASSWORD` is not set in .env, Redis will start WITHOUT authentication
- Security vulnerability: Anyone can access Redis without password

**Fix**:
```bash
# Add to .env.example:
REDIS_PASSWORD=change-me-to-secure-password

# Add to .env.production:
REDIS_PASSWORD=<strong-random-password>
```

**Verification**:
```bash
# Check Redis requires password
docker exec uns-claudejp-redis redis-cli ping
# Should return: (error) ERR invalid password

docker exec uns-claudejp-redis redis-cli -a your-password ping
# Should return: PONG
```

---

## CRITICAL ISSUE #2: Two Incompatible Production Architectures

**Severity**: 🔴 CRITICAL  
**Location**: 
- File 1: `docker-compose.yml` (uses Nginx)
- File 2: `docker-compose.prod.yml` (uses Traefik)

**Problem**:
```
docker-compose.yml:
  ├── Reverse Proxy: Nginx (nginx:1.26-alpine)
  ├── Service Names: backend, frontend, db, etc.
  └── Services: 12 core + observability

docker-compose.prod.yml (COMPLETELY DIFFERENT):
  ├── Reverse Proxy: Traefik v3.0 (different architecture!)
  ├── Service Names: uns-claudejp-app, uns-claudejp-db-prod, etc.
  ├── Networks: 5 isolated networks (not compatible)
  └── Missing: No Next.js frontend service
```

**Risk**: 
- Unclear which configuration to use for production
- Environment variables different between files
- Cannot use same .env for both
- One file is newer but not documented

**Decision Required**: Choose ONE architecture

**Option A - Keep docker-compose.yml (RECOMMENDED)**
```bash
# Advantages:
# - Currently used for dev/prod
# - Simpler configuration
# - Nginx is lighter weight
# - Better documented in project

# Action:
rm docker-compose.prod.yml  # Delete old incompatible file
# Or refactor it to be compatible
```

**Option B - Migrate to docker-compose.prod.yml**
```bash
# Advantages:
# - More production-hardened (AppArmor, seccomp, caps)
# - Better security controls
# - Traefik + Let's Encrypt automation
# - Resource limits defined

# Action:
# Need to add frontend service
# Need to document migration
# Need to update build process
```

**Recommendation**: Keep docker-compose.yml, mark docker-compose.prod.yml as DEPRECATED

---

## CRITICAL ISSUE #3: Default Credentials in Code

**Severity**: 🔴 CRITICAL  
**Location**:
- Grafana defaults: `docker-compose.yml` lines 429-430
- Demo credentials: `.env.example` lines 156-157

**Problem**:
```yaml
# docker-compose.yml - Grafana
environment:
  GF_SECURITY_ADMIN_USER: ${GRAFANA_ADMIN_USER:-admin}      # Default: admin
  GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_ADMIN_PASSWORD:-admin}  # Default: admin ❌

# .env.example - Demo credentials
NEXT_PUBLIC_DEMO_USER=admin
NEXT_PUBLIC_DEMO_PASS=admin123  # Exposed in frontend! ❌
```

**Risk**:
- Grafana accessible with admin/admin (standard default)
- Demo password exposed in frontend config
- Anyone can compromise monitoring dashboards

**Fix - Immediate**:
```bash
# .env.example - Add Grafana password:
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=<change-me-to-secure-password>

# .env.production - Override:
GRAFANA_ADMIN_USER=<different-from-admin>
GRAFANA_ADMIN_PASSWORD=<very-secure-password>

# .env.example - Remove or secure demo credentials:
# REMOVE THIS:
# NEXT_PUBLIC_DEMO_USER=admin
# NEXT_PUBLIC_DEMO_PASS=admin123
```

**Fix - Update docker-compose.yml**:
```yaml
# Ensure it doesn't use defaults
grafana:
  environment:
    GF_SECURITY_ADMIN_USER: ${GRAFANA_ADMIN_USER}      # No default
    GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_ADMIN_PASSWORD}  # Required
```

**Verification**:
```bash
# Test Grafana login
curl -u admin:admin http://localhost:3001/api/health
# If this works, you still have default credentials!
```

---

## CRITICAL ISSUE #4: ENVIRONMENT Variable Mismatch

**Severity**: 🔴 CRITICAL  
**Location**:
- `docker-compose.yml` lines 101, 137, 215
- `.env.example` line 67

**Problem**:
```yaml
# docker-compose.yml - backend (dev)
environment:
  ENVIRONMENT: ${ENVIRONMENT:-development}  # Default: development

# docker-compose.yml - backend-prod (prod)
environment:
  ENVIRONMENT: ${ENVIRONMENT:-production}   # Default: production (but uses .env value!)

# .env.example
ENVIRONMENT=development  # Sets default to DEVELOPMENT
```

**Risk**:
1. If .env is not customized, `backend-prod` gets ENVIRONMENT=development
2. Application might log debug info in production
3. Behavior differs between dev and prod unexpectedly

**Example Scenario**:
```bash
# Production deployment
docker compose --profile prod up -d

# .env is NOT overridden
# .env still has: ENVIRONMENT=development

# Result: backend-prod service gets ENVIRONMENT=development
# Production logs verbose debug info
# Security risk!
```

**Fix - Create .env.production**:
```bash
# Create new file: .env.production
ENVIRONMENT=production
DEBUG=false
POSTGRES_PASSWORD=<secure>
SECRET_KEY=<secure>
REDIS_PASSWORD=<secure>
GRAFANA_ADMIN_PASSWORD=<secure>
FRONTEND_URL=https://your-domain.com
```

**Fix - Update docker-compose.yml**:
```yaml
# CHANGE THIS:
environment:
  ENVIRONMENT: ${ENVIRONMENT:-production}

# TO THIS (remove defaults to force override):
environment:
  ENVIRONMENT: ${ENVIRONMENT}  # Required from .env

# OR use explicit defaults appropriate for profile:
# backend-prod should explicitly require ENVIRONMENT
```

**Usage**:
```bash
# Development
docker compose --env-file .env.development --profile dev up -d

# Production
docker compose --env-file .env.production --profile prod up -d
```

---

## Summary of Fixes

| Issue | Impact | Fix | Priority |
|-------|--------|-----|----------|
| REDIS_PASSWORD missing | No auth on Redis | Add to .env.example | 🔴 CRITICAL |
| Two prod architectures | Unclear deployment | Keep docker-compose.yml, delete prod.yml | 🔴 CRITICAL |
| Default credentials | Security breach | Override all defaults, use secure values | 🔴 CRITICAL |
| ENV mismatch | Dev mode in prod | Create .env.production, require ENVIRONMENT | 🔴 CRITICAL |

---

## Implementation Checklist

- [ ] Add REDIS_PASSWORD to .env.example
- [ ] Create .env.production file with all secure values
- [ ] Delete or deprecate docker-compose.prod.yml
- [ ] Update docker-compose.yml to require ENVIRONMENT (no defaults)
- [ ] Override GRAFANA_ADMIN_PASSWORD in .env files
- [ ] Remove or secure demo credentials from .env.example
- [ ] Test with `--env-file .env.production` before deploying
- [ ] Document environment configuration in README
- [ ] Add .env.production to .gitignore (if not already)

---

## Pre-Production Checklist

```bash
# 1. Verify environment variables
echo "REDIS_PASSWORD: ${REDIS_PASSWORD:?REDIS_PASSWORD not set}"
echo "POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?POSTGRES_PASSWORD not set}"
echo "SECRET_KEY: ${SECRET_KEY:?SECRET_KEY not set}"
echo "GRAFANA_ADMIN_PASSWORD: ${GRAFANA_ADMIN_PASSWORD:?GRAFANA_ADMIN_PASSWORD not set}"
echo "ENVIRONMENT: ${ENVIRONMENT:?ENVIRONMENT not set}"

# 2. Verify Grafana default password is overridden
grep "admin:admin" docker-compose.yml || echo "✅ No hardcoded admin:admin found"

# 3. Verify REDIS_PASSWORD is documented
grep -i "REDIS_PASSWORD" .env || echo "❌ REDIS_PASSWORD not in .env"
grep -i "REDIS_PASSWORD" .env.example || echo "❌ REDIS_PASSWORD not in .env.example"

# 4. Verify no docker-compose.prod.yml conflict
ls -la docker-compose*.yml

# 5. Test with production env
docker compose --env-file .env.production --profile prod config | head -50
```

---

**Next Steps**: 
1. Read full analysis: `/home/user/UNS-ClaudeJP-5.4.1/DOCKER_COMPOSE_ANALYSIS.md`
2. Implement fixes above
3. Test in staging environment
4. Deploy to production

