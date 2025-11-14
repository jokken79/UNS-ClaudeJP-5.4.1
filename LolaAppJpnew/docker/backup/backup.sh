#!/bin/sh
# ============================================================================
# Automated PostgreSQL Backup Script for LolaAppJp
# ============================================================================

set -e

# Configuration from environment variables
BACKUP_DIR="/backups"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
BACKUP_TIME="${BACKUP_TIME:-02:00}"
RUN_ON_STARTUP="${BACKUP_RUN_ON_STARTUP:-true}"

# Database configuration
HOST="${POSTGRES_HOST:-db}"
DB="${POSTGRES_DB:-lolaappjp}"
USER="${POSTGRES_USER:-lola_admin}"

echo "========================================="
echo "  LolaAppJp Backup Service"
echo "========================================="
echo "Database: ${DB}@${HOST}"
echo "Backup Directory: ${BACKUP_DIR}"
echo "Retention: ${RETENTION_DAYS} days"
echo "Scheduled Time: ${BACKUP_TIME} JST"
echo "========================================="

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Function to perform backup
perform_backup() {
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    BACKUP_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.sql.gz"

    echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting backup..."

    # Perform backup with pg_dump and compress
    if PGPASSWORD="${POSTGRES_PASSWORD}" pg_dump \
        -h "${HOST}" \
        -U "${USER}" \
        -d "${DB}" \
        --no-owner \
        --no-acl \
        -Fp | gzip > "${BACKUP_FILE}"; then

        BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
        echo "$(date '+%Y-%m-%d %H:%M:%S') - ✅ Backup completed: ${BACKUP_FILE} (${BACKUP_SIZE})"

        # Clean up old backups
        find "${BACKUP_DIR}" -name "backup_*.sql.gz" -type f -mtime +${RETENTION_DAYS} -delete
        REMAINING=$(find "${BACKUP_DIR}" -name "backup_*.sql.gz" -type f | wc -l)
        echo "$(date '+%Y-%m-%d %H:%M:%S') - 🗑️  Old backups cleaned (${REMAINING} backups remaining)"
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') - ❌ Backup failed!"
        exit 1
    fi
}

# Wait for database to be ready
echo "Waiting for database to be ready..."
until PGPASSWORD="${POSTGRES_PASSWORD}" pg_isready -h "${HOST}" -U "${USER}" -d "${DB}"; do
    sleep 2
done
echo "✅ Database is ready"

# Run backup on startup if configured
if [ "${RUN_ON_STARTUP}" = "true" ]; then
    echo "Running initial backup on startup..."
    perform_backup
fi

# Setup cron job for scheduled backups
# Convert time like "02:00" to cron format "0 2 * * *"
HOUR=$(echo ${BACKUP_TIME} | cut -d: -f1 | sed 's/^0*//')
MINUTE=$(echo ${BACKUP_TIME} | cut -d: -f2 | sed 's/^0*//')

# Create cron schedule
CRON_SCHEDULE="${MINUTE:-0} ${HOUR:-2} * * *"

echo "Setting up cron job: ${CRON_SCHEDULE}"

# Create cron job
echo "${CRON_SCHEDULE} /backup.sh run-backup >> /var/log/backup.log 2>&1" > /etc/crontabs/root

# Run backup if called with "run-backup" argument
if [ "$1" = "run-backup" ]; then
    perform_backup
    exit 0
fi

# Start cron in foreground
echo "Starting cron daemon..."
echo "Backup will run daily at ${BACKUP_TIME} JST"
echo "========================================="

# Create log file
touch /var/log/backup.log

# Start crond and tail the log
crond -f &
tail -f /var/log/backup.log
