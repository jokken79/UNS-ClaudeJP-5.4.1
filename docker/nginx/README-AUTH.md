# Nginx Authentication Setup

## Overview
This directory contains authentication configuration for securing Prometheus and other monitoring endpoints.

## Grafana Authentication

Grafana authentication is configured via environment variables in `.env`:

```bash
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=UNS-Grafana-2025-SecureP@ss!
```

**Default credentials**: `admin` / `UNS-Grafana-2025-SecureP@ss!`

**⚠️ IMPORTANT**: Change this password in production!

## Prometheus Authentication (Basic Auth)

Prometheus is protected via Nginx Basic Authentication.

### Option 1: Using Docker (Recommended)

Generate htpasswd file using Docker:

```bash
# Windows (PowerShell)
docker run --rm httpd:alpine htpasswd -nb prometheus 'UNS-Prometheus-2025-SecureP@ss!' > docker\nginx\htpasswd

# Linux/macOS
docker run --rm httpd:alpine htpasswd -nb prometheus 'UNS-Prometheus-2025-SecureP@ss!' > docker/nginx/htpasswd
```

### Option 2: Using htpasswd CLI

If you have `htpasswd` installed:

```bash
htpasswd -nb prometheus 'UNS-Prometheus-2025-SecureP@ss!' > docker/nginx/htpasswd
```

### Option 3: Pre-generated File

A pre-generated `htpasswd` file is included with credentials:
- **Username**: `prometheus`
- **Password**: `UNS-Prometheus-2025-SecureP@ss!`

**⚠️ IMPORTANT**: Change this password in production!

## Enabling Authentication in Nginx

Edit `docker/nginx/nginx.conf` and uncomment the authentication lines for Prometheus:

```nginx
location /prometheus/ {
    # Uncomment these lines to enable authentication:
    # auth_basic "Prometheus - Restricted Access";
    # auth_basic_user_file /etc/nginx/htpasswd;

    proxy_pass http://prometheus/;
    # ... rest of config
}
```

Then update the nginx service in `docker-compose.yml` to mount the htpasswd file:

```yaml
nginx:
  # ... existing config
  volumes:
    - ./docker/nginx/htpasswd:/etc/nginx/htpasswd:ro
    # ... other volumes
```

## Testing Authentication

After enabling authentication, access Prometheus:

```bash
# Without credentials (should fail)
curl http://localhost/prometheus/

# With credentials (should work)
curl -u prometheus:UNS-Prometheus-2025-SecureP@ss! http://localhost/prometheus/
```

## Security Best Practices

1. **Change default passwords** before deploying to production
2. **Use HTTPS** in production (see nginx.conf SSL section)
3. **Restrict access by IP** for additional security
4. **Rotate passwords** regularly
5. **Store credentials securely** (use environment variables, not hardcoded)

## Generating New Passwords

To generate a new secure password:

```bash
# Windows (PowerShell)
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})

# Linux/macOS
openssl rand -base64 32
```

Then update both `.env` and `htpasswd` files accordingly.
