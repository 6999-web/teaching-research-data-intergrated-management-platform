#!/bin/bash
# PostgreSQL Database Restore Script
# 数据库恢复脚本

set -e

# Check if backup file is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file.sql.gz>"
    echo "Available backups:"
    ls -lh /backups/teaching_office_*.sql.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE=$1

# Check if backup file exists
if [ ! -f "${BACKUP_FILE}" ]; then
    echo "Error: Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

# Database connection info
DB_HOST=${POSTGRES_SERVER:-postgres}
DB_USER=${POSTGRES_USER}
DB_PASSWORD=${POSTGRES_PASSWORD}
DB_NAME=${POSTGRES_DB}

echo "=========================================="
echo "Starting database restore"
echo "=========================================="
echo "Backup file: ${BACKUP_FILE}"
echo "Target database: ${DB_NAME}"
echo ""
read -p "Are you sure you want to restore? This will overwrite existing data! (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

# Drop existing connections
echo "Terminating existing connections..."
PGPASSWORD=${DB_PASSWORD} psql -h ${DB_HOST} -U ${DB_USER} -d postgres -c \
  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${DB_NAME}' AND pid <> pg_backend_pid();"

# Drop and recreate database
echo "Recreating database..."
PGPASSWORD=${DB_PASSWORD} psql -h ${DB_HOST} -U ${DB_USER} -d postgres -c "DROP DATABASE IF EXISTS ${DB_NAME};"
PGPASSWORD=${DB_PASSWORD} psql -h ${DB_HOST} -U ${DB_USER} -d postgres -c "CREATE DATABASE ${DB_NAME};"

# Restore backup
echo "Restoring backup..."
gunzip -c ${BACKUP_FILE} | PGPASSWORD=${DB_PASSWORD} psql -h ${DB_HOST} -U ${DB_USER} -d ${DB_NAME}

# Check if restore was successful
if [ $? -eq 0 ]; then
    echo "✓ Database restored successfully"
else
    echo "✗ Restore failed!"
    exit 1
fi

echo "=========================================="
echo "Restore process completed"
echo "=========================================="
