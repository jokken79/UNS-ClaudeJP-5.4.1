#!/bin/bash

# ========================================
# UNS-ClaudeJP 5.4.1 - Database Restore
# ========================================
#
# Purpose: Restore PostgreSQL database from backup
# Usage: ./restore.sh <backup_file.sql.gz>
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
LOG_FILE="${BACKUP_DIR}/restore.log"

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
# USAGE
# ========================================

usage() {
    echo "Usage: $0 <backup_file.sql.gz>"
    echo ""
    echo "Examples:"
    echo "  $0 /backups/backup_20251112_120000.sql.gz"
    echo "  $0 backup_20251112_120000.sql.gz  (searches in ${BACKUP_DIR})"
    echo ""
    echo "Available backups:"
    find "${BACKUP_DIR}" -name "backup_*.sql.gz" -type f -printf "  %p (%TY-%Tm-%Td %TH:%TM)\n" 2>/dev/null || echo "  No backups found"
    exit 1
}

# ========================================
# VALIDATE INPUT
# ========================================

if [ $# -eq 0 ]; then
    log "ERROR: No backup file specified"
    usage
fi

BACKUP_FILE="$1"

# If relative path, check in backup directory
if [[ ! "$BACKUP_FILE" = /* ]]; then
    BACKUP_FILE="${BACKUP_DIR}/${BACKUP_FILE}"
fi

# Check if backup file exists
if [ ! -f "${BACKUP_FILE}" ]; then
    log "ERROR: Backup file not found: ${BACKUP_FILE}"
    usage
fi

log "========================================="
log "Starting database restore"
log "Database: ${POSTGRES_DB}"
log "Backup file: ${BACKUP_FILE}"
log "========================================="

# ========================================
# CONFIRMATION PROMPT
# ========================================

echo ""
echo "⚠️  WARNING: This will REPLACE ALL DATA in database '${POSTGRES_DB}'"
echo ""
read -p "Are you sure you want to continue? (type 'yes' to confirm): " CONFIRMATION

if [ "${CONFIRMATION}" != "yes" ]; then
    log "Restore cancelled by user"
    exit 0
fi

log "User confirmed restore operation"

# ========================================
# CHECK DATABASE CONNECTION
# ========================================

log "Checking database connection..."
if ! pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" > /dev/null 2>&1; then
    error_exit "Database is not ready. Restore aborted."
fi
log "✓ Database connection OK"

# ========================================
# CREATE PRE-RESTORE BACKUP (SAFETY)
# ========================================

SAFETY_BACKUP="${BACKUP_DIR}/pre_restore_$(date +%Y%m%d_%H%M%S).sql.gz"
log "Creating safety backup: ${SAFETY_BACKUP}"

if pg_dump \
    -h "${POSTGRES_HOST}" \
    -p "${POSTGRES_PORT}" \
    -U "${POSTGRES_USER}" \
    -d "${POSTGRES_DB}" \
    --format=plain \
    --no-owner \
    --no-acl \
    | gzip > "${SAFETY_BACKUP}" 2>> "${LOG_FILE}"; then
    log "✓ Safety backup created successfully"
else
    log "WARNING: Failed to create safety backup (continuing anyway)"
fi

# ========================================
# DECOMPRESS BACKUP
# ========================================

TEMP_SQL_FILE="/tmp/restore_${POSTGRES_DB}_$$.sql"
log "Decompressing backup..."

if gunzip -c "${BACKUP_FILE}" > "${TEMP_SQL_FILE}" 2>> "${LOG_FILE}"; then
    BACKUP_SIZE=$(du -h "${TEMP_SQL_FILE}" | cut -f1)
    log "✓ Backup decompressed successfully: ${BACKUP_SIZE}"
else
    error_exit "Failed to decompress backup"
fi

# ========================================
# RESTORE DATABASE
# ========================================

log "Restoring database (this may take several minutes)..."

if psql \
    -h "${POSTGRES_HOST}" \
    -p "${POSTGRES_PORT}" \
    -U "${POSTGRES_USER}" \
    -d "${POSTGRES_DB}" \
    --single-transaction \
    --set ON_ERROR_STOP=on \
    < "${TEMP_SQL_FILE}" 2>> "${LOG_FILE}"; then
    log "✓ Database restored successfully"
else
    error_exit "Database restore failed. Check ${LOG_FILE} for details. Safety backup available at: ${SAFETY_BACKUP}"
fi

# ========================================
# CLEANUP TEMPORARY FILES
# ========================================

log "Cleaning up temporary files..."
rm -f "${TEMP_SQL_FILE}" || log "WARNING: Failed to remove temporary file"

# ========================================
# VERIFY RESTORE
# ========================================

log "Verifying database connection after restore..."
if pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" > /dev/null 2>&1; then
    log "✓ Database is operational after restore"
else
    error_exit "Database is not responding after restore"
fi

# ========================================
# SUMMARY
# ========================================

log "========================================="
log "Restore completed successfully!"
log "Restored from: ${BACKUP_FILE}"
log "Safety backup: ${SAFETY_BACKUP}"
log "========================================="

echo ""
echo "✓ Database restored successfully"
echo ""
echo "Safety backup available at: ${SAFETY_BACKUP}"
echo "You can delete it manually if restore is verified:"
echo "  rm ${SAFETY_BACKUP}"
echo ""

exit 0
