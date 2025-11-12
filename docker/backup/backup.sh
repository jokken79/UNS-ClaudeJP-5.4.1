#!/bin/bash

# ========================================
# UNS-ClaudeJP 5.4.1 - Automated Database Backup
# ========================================
#
# Purpose: Automatic PostgreSQL database backups with retention policy
# Schedule: Runs every 24 hours (configurable)
# Retention: Last 30 days
#
# Author: Claude Code
# Created: 2025-11-12
# Version: 1.0.0
#
# ========================================

set -e  # Exit on error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failure

# ========================================
# CONFIGURATION
# ========================================

BACKUP_DIR="/backups"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.sql"
BACKUP_COMPRESSED="${BACKUP_FILE}.gz"
LOG_FILE="${BACKUP_DIR}/backup.log"

# Database connection from environment
POSTGRES_DB="${POSTGRES_DB:-uns_claudejp}"
POSTGRES_USER="${POSTGRES_USER:-uns_admin}"
POSTGRES_HOST="${POSTGRES_HOST:-db}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"

# ========================================
# LOGGING FUNCTION
# ========================================

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${LOG_FILE}"
}

# ========================================
# ERROR HANDLER
# ========================================

error_exit() {
    log "ERROR: $1"
    exit 1
}

# ========================================
# CREATE BACKUP DIRECTORY
# ========================================

mkdir -p "${BACKUP_DIR}" || error_exit "Failed to create backup directory"

log "========================================="
log "Starting database backup"
log "Database: ${POSTGRES_DB}"
log "Timestamp: ${TIMESTAMP}"
log "========================================="

# ========================================
# CHECK DATABASE CONNECTION
# ========================================

log "Checking database connection..."
if ! pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" > /dev/null 2>&1; then
    error_exit "Database is not ready. Backup aborted."
fi
log "✓ Database connection OK"

# ========================================
# CREATE BACKUP
# ========================================

log "Creating backup: ${BACKUP_FILE}"

# Perform pg_dump with custom format for better compression and restore options
if pg_dump \
    -h "${POSTGRES_HOST}" \
    -p "${POSTGRES_PORT}" \
    -U "${POSTGRES_USER}" \
    -d "${POSTGRES_DB}" \
    --format=plain \
    --no-owner \
    --no-acl \
    --clean \
    --if-exists \
    --verbose \
    > "${BACKUP_FILE}" 2>> "${LOG_FILE}"; then
    log "✓ Database dump completed successfully"
else
    error_exit "Database dump failed"
fi

# ========================================
# COMPRESS BACKUP
# ========================================

log "Compressing backup..."
if gzip -f "${BACKUP_FILE}"; then
    BACKUP_SIZE=$(du -h "${BACKUP_COMPRESSED}" | cut -f1)
    log "✓ Backup compressed successfully: ${BACKUP_SIZE}"
else
    error_exit "Backup compression failed"
fi

# ========================================
# VERIFY BACKUP
# ========================================

log "Verifying backup integrity..."
if gunzip -t "${BACKUP_COMPRESSED}" > /dev/null 2>&1; then
    log "✓ Backup integrity verified"
else
    error_exit "Backup verification failed"
fi

# ========================================
# CLEANUP OLD BACKUPS (RETENTION POLICY)
# ========================================

log "Applying retention policy (${RETENTION_DAYS} days)..."

# Count backups before cleanup
BACKUPS_BEFORE=$(find "${BACKUP_DIR}" -name "backup_*.sql.gz" -type f | wc -l)

# Delete backups older than retention period
if find "${BACKUP_DIR}" -name "backup_*.sql.gz" -type f -mtime +${RETENTION_DAYS} -delete 2>> "${LOG_FILE}"; then
    BACKUPS_AFTER=$(find "${BACKUP_DIR}" -name "backup_*.sql.gz" -type f | wc -l)
    BACKUPS_DELETED=$((BACKUPS_BEFORE - BACKUPS_AFTER))
    log "✓ Retention policy applied: ${BACKUPS_DELETED} old backup(s) deleted"
    log "  Total backups remaining: ${BACKUPS_AFTER}"
else
    log "WARNING: Failed to apply retention policy (non-critical)"
fi

# ========================================
# CLEANUP OLD LOGS (Keep last 90 days)
# ========================================

if [ -f "${LOG_FILE}" ]; then
    # Keep only last 10000 lines of logs
    tail -n 10000 "${LOG_FILE}" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "${LOG_FILE}"
fi

# ========================================
# SUMMARY
# ========================================

log "========================================="
log "Backup completed successfully!"
log "File: ${BACKUP_COMPRESSED}"
log "Size: ${BACKUP_SIZE}"
log "Retention: ${RETENTION_DAYS} days"
log "========================================="

# Optional: Send notification (uncomment if needed)
# curl -X POST "http://backend:8000/api/notifications/backup-success" \
#   -H "Content-Type: application/json" \
#   -d "{\"backup_file\": \"${BACKUP_COMPRESSED}\", \"size\": \"${BACKUP_SIZE}\"}" || true

exit 0
