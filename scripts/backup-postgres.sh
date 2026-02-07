#!/bin/bash
# PostgreSQL Database Backup Script
# 数据库备份脚本

set -e

# Configuration
BACKUP_DIR="/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/teaching_office_${TIMESTAMP}.sql.gz"
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}

# Database connection info
DB_HOST=${POSTGRES_SERVER:-postgres}
DB_USER=${POSTGRES_USER}
DB_PASSWORD=${POSTGRES_PASSWORD}
DB_NAME=${POSTGRES_DB}

echo "=========================================="
echo "Starting database backup: ${TIMESTAMP}"
echo "=========================================="

# Create backup directory if it doesn't exist
mkdir -p ${BACKUP_DIR}

# Perform backup
echo "Backing up database ${DB_NAME}..."
PGPASSWORD=${DB_PASSWORD} pg_dump \
  -h ${DB_HOST} \
  -U ${DB_USER} \
  -d ${DB_NAME} \
  --format=plain \
  --no-owner \
  --no-acl \
  | gzip > ${BACKUP_FILE}

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "✓ Backup completed successfully: ${BACKUP_FILE}"
    
    # Get backup file size
    BACKUP_SIZE=$(du -h ${BACKUP_FILE} | cut -f1)
    echo "  Backup size: ${BACKUP_SIZE}"
else
    echo "✗ Backup failed!"
    exit 1
fi

# Clean up old backups
echo "Cleaning up backups older than ${RETENTION_DAYS} days..."
find ${BACKUP_DIR} -name "teaching_office_*.sql.gz" -type f -mtime +${RETENTION_DAYS} -delete

# List remaining backups
BACKUP_COUNT=$(find ${BACKUP_DIR} -name "teaching_office_*.sql.gz" -type f | wc -l)
echo "Total backups retained: ${BACKUP_COUNT}"

echo "=========================================="
echo "Backup process completed"
echo "=========================================="
