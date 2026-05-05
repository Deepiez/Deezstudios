#!/bin/bash
# ===========================================
# Database Backup Script
# Run via cron: 0 2 * * * /path/to/backup.sh
# ===========================================

set -e

BACKUP_DIR="/var/backups/content-studio"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Load env
source "$(dirname "$0")/../.env"

echo "[$(date)] Starting backup..."

# PostgreSQL dump
docker exec studio-postgres pg_dump \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB" \
    --format=custom \
    --compress=9 \
    > "$BACKUP_DIR/db_${TIMESTAMP}.dump"

echo "[$(date)] Database backup: db_${TIMESTAMP}.dump ($(du -h "$BACKUP_DIR/db_${TIMESTAMP}.dump" | cut -f1))"

# Clean old backups
find "$BACKUP_DIR" -name "db_*.dump" -mtime +$RETENTION_DAYS -delete
echo "[$(date)] Cleaned backups older than ${RETENTION_DAYS} days"

echo "[$(date)] Backup complete!"
