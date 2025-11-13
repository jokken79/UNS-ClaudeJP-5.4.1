# UNS-ClaudeJP 5.4.1 - Automated Backup System

## Overview

This automated backup system provides:
- **Scheduled backups** every 24 hours (configurable)
- **Retention policy** of 30 days (configurable)
- **Compressed backups** using gzip
- **Automatic cleanup** of old backups
- **Easy restore** from any backup

## Configuration

### Environment Variables (`.env`)

```bash
# Backup retention in days (default: 30)
BACKUP_RETENTION_DAYS=30

# Backup interval in hours (default: 24)
BACKUP_INTERVAL_HOURS=24

# Backup time (HH:MM format, JST timezone)
BACKUP_TIME=02:00

# Run backup on service startup
BACKUP_RUN_ON_STARTUP=true
```

## Service Management

### Start Backup Service

The backup service runs automatically with docker-compose:

```bash
# Windows
cd scripts
START.bat

# Linux/macOS
docker compose --profile dev up -d
```

### View Backup Logs

```bash
# View live backup logs
docker logs -f uns-claudejp-backup

# View backup log file
docker exec uns-claudejp-backup cat /backups/backup.log

# View cron log
docker exec uns-claudejp-backup cat /backups/cron.log
```

### Manual Backup

To trigger a backup manually:

```bash
# Run backup immediately
docker exec uns-claudejp-backup /scripts/backup.sh
```

## Backup Files

Backups are stored in `./backups/` directory:

```
backups/
├── backup_20251112_020000.sql.gz
├── backup_20251113_020000.sql.gz
├── backup_20251114_020000.sql.gz
├── backup.log
└── cron.log
```

### Backup File Format

- **Filename**: `backup_YYYYMMDD_HHMMSS.sql.gz`
- **Format**: Compressed SQL dump (gzip)
- **Contents**: Complete database dump

## Restore from Backup

### Interactive Restore (Recommended)

```bash
# List available backups
docker exec uns-claudejp-backup ls -lh /backups/backup_*.sql.gz

# Restore from specific backup (interactive confirmation)
docker exec -it uns-claudejp-backup /scripts/restore.sh backup_20251112_020000.sql.gz
```

The restore script will:
1. Show confirmation prompt
2. Create a safety backup before restore
3. Restore the database
4. Verify the restore was successful

### Non-interactive Restore (Automated)

⚠️ **WARNING**: This skips the confirmation prompt!

```bash
# Restore without confirmation (use with caution)
docker exec uns-claudejp-backup bash -c "echo 'yes' | /scripts/restore.sh backup_20251112_020000.sql.gz"
```

### Restore from Windows (PowerShell)

```powershell
# List backups
docker exec uns-claudejp-backup ls -lh /backups/backup_*.sql.gz

# Interactive restore
docker exec -it uns-claudejp-backup /scripts/restore.sh backup_20251112_020000.sql.gz
```

### Restore from Windows (CMD)

```cmd
REM List backups
docker exec uns-claudejp-backup ls -lh /backups/backup_*.sql.gz

REM Interactive restore
docker exec -it uns-claudejp-backup /scripts/restore.sh backup_20251112_020000.sql.gz
```

## Manual Restore (Alternative Method)

If you prefer to restore manually:

```bash
# 1. Copy backup to host
docker cp uns-claudejp-backup:/backups/backup_20251112_020000.sql.gz ./

# 2. Decompress backup
gunzip backup_20251112_020000.sql.gz

# 3. Restore to database
docker exec -i uns-claudejp-db psql -U uns_admin -d uns_claudejp < backup_20251112_020000.sql
```

## Backup to External Storage

### Copy Backups to External Drive

```bash
# Windows (PowerShell)
Copy-Item -Path "backups\*" -Destination "E:\UNS-Backups\" -Recurse

# Linux/macOS
cp -r backups/* /mnt/external-drive/UNS-Backups/
```

### Automated Cloud Sync (Optional)

To sync backups to cloud storage (AWS S3, Azure Blob, etc.), add to `backup.sh`:

```bash
# Example: AWS S3 sync (requires aws-cli)
aws s3 sync /backups/ s3://your-bucket/uns-backups/ \
  --exclude "*" \
  --include "backup_*.sql.gz"
```

## Monitoring

### Check Backup Service Health

```bash
# Check if backup service is running
docker ps | grep uns-claudejp-backup

# Check health status
docker inspect uns-claudejp-backup | grep -A 5 Health
```

### Verify Recent Backup

```bash
# List backups from last 7 days
docker exec uns-claudejp-backup find /backups -name "backup_*.sql.gz" -type f -mtime -7

# Check backup file size
docker exec uns-claudejp-backup du -h /backups/backup_*.sql.gz
```

## Troubleshooting

### Problem: No backups are being created

**Solution 1**: Check if cron is running
```bash
docker exec uns-claudejp-backup pgrep crond
```

**Solution 2**: Check backup logs
```bash
docker logs uns-claudejp-backup
docker exec uns-claudejp-backup cat /backups/backup.log
```

**Solution 3**: Run manual backup to see errors
```bash
docker exec uns-claudejp-backup /scripts/backup.sh
```

### Problem: Backup fails with "database not ready"

**Solution**: Ensure database service is healthy
```bash
docker ps | grep uns-claudejp-db
docker exec uns-claudejp-db pg_isready -U uns_admin -d uns_claudejp
```

### Problem: Old backups not being deleted

**Solution**: Check retention policy in `.env`
```bash
grep BACKUP_RETENTION_DAYS .env
```

### Problem: Disk space full

**Solution 1**: Reduce retention days
```bash
# In .env
BACKUP_RETENTION_DAYS=7
```

**Solution 2**: Manually delete old backups
```bash
# Delete backups older than 7 days
docker exec uns-claudejp-backup find /backups -name "backup_*.sql.gz" -type f -mtime +7 -delete
```

## Security Best Practices

1. **Encrypt backups** for sensitive data:
   ```bash
   # Encrypt backup
   gpg -c backup_20251112_020000.sql.gz

   # Decrypt backup
   gpg -d backup_20251112_020000.sql.gz.gpg > backup_20251112_020000.sql.gz
   ```

2. **Store backups off-site** (external drive, cloud storage)

3. **Test restores regularly** to ensure backups are valid

4. **Monitor disk space** to prevent backup failures

5. **Restrict access** to backup files (contains sensitive data)

## Advanced Configuration

### Change Backup Schedule

Edit `BACKUP_TIME` in `.env`:

```bash
# Daily at 3 AM
BACKUP_TIME=03:00

# Multiple backups per day (edit cron directly in Dockerfile.backup)
# Example: Every 6 hours
CRON_SCHEDULE="0 */6 * * *"
```

### Custom Retention Policy

```bash
# Keep backups for 90 days
BACKUP_RETENTION_DAYS=90

# Keep backups for 7 days (weekly rotation)
BACKUP_RETENTION_DAYS=7
```

### Exclude Specific Tables

Edit `backup.sh` and add `--exclude-table`:

```bash
pg_dump \
  --exclude-table=audit_log \
  --exclude-table=session_logs \
  ...
```

## Recovery Scenarios

### Scenario 1: Accidental Data Deletion

1. Identify when data was deleted
2. Find backup before deletion
3. Restore from that backup

```bash
# List backups with timestamps
docker exec uns-claudejp-backup ls -lh /backups/

# Restore from backup before deletion
docker exec -it uns-claudejp-backup /scripts/restore.sh backup_20251111_020000.sql.gz
```

### Scenario 2: Database Corruption

1. Stop application services
2. Restore from most recent valid backup
3. Restart services

```bash
# Stop services
docker compose stop backend frontend

# Restore database
docker exec -it uns-claudejp-backup /scripts/restore.sh backup_20251112_020000.sql.gz

# Restart services
docker compose start backend frontend
```

### Scenario 3: Migration to New Server

1. Copy backups to new server
2. Set up docker-compose
3. Restore from backup

```bash
# On new server
docker compose up -d db
docker exec -i uns-claudejp-db psql -U uns_admin -d uns_claudejp < backup_20251112_020000.sql
docker compose up -d
```

## Support

For issues or questions:
- Check logs: `docker logs uns-claudejp-backup`
- Review backup.log: `docker exec uns-claudejp-backup cat /backups/backup.log`
- Contact: dev@uns-kikaku.com
