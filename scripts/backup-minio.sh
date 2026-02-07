#!/bin/bash
# MinIO Object Storage Backup Script
# MinIO对象存储备份脚本

set -e

# Configuration
BACKUP_DIR="/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/minio_${TIMESTAMP}.tar.gz"
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}

# MinIO configuration
MINIO_ENDPOINT=${MINIO_ENDPOINT:-minio:9000}
MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}
MINIO_SECRET_KEY=${MINIO_SECRET_KEY}
MINIO_BUCKET=${MINIO_BUCKET:-teaching-office-attachments-prod}

echo "=========================================="
echo "Starting MinIO backup: ${TIMESTAMP}"
echo "=========================================="

# Create backup directory if it doesn't exist
mkdir -p ${BACKUP_DIR}

# Install mc (MinIO Client) if not present
if ! command -v mc &> /dev/null; then
    echo "Installing MinIO Client..."
    wget https://dl.min.io/client/mc/release/linux-amd64/mc -O /usr/local/bin/mc
    chmod +x /usr/local/bin/mc
fi

# Configure MinIO client
echo "Configuring MinIO client..."
mc alias set myminio http://${MINIO_ENDPOINT} ${MINIO_ACCESS_KEY} ${MINIO_SECRET_KEY}

# Create temporary directory for backup
TEMP_DIR="${BACKUP_DIR}/temp_${TIMESTAMP}"
mkdir -p ${TEMP_DIR}

# Mirror bucket to local directory
echo "Downloading bucket contents: ${MINIO_BUCKET}..."
mc mirror myminio/${MINIO_BUCKET} ${TEMP_DIR}

# Check if mirror was successful
if [ $? -eq 0 ]; then
    echo "✓ Download completed successfully"
    
    # Create compressed archive
    echo "Creating compressed archive..."
    tar -czf ${BACKUP_FILE} -C ${TEMP_DIR} .
    
    # Get backup file size
    BACKUP_SIZE=$(du -h ${BACKUP_FILE} | cut -f1)
    echo "✓ Backup completed: ${BACKUP_FILE}"
    echo "  Backup size: ${BACKUP_SIZE}"
    
    # Clean up temporary directory
    rm -rf ${TEMP_DIR}
else
    echo "✗ Backup failed!"
    rm -rf ${TEMP_DIR}
    exit 1
fi

# Clean up old backups
echo "Cleaning up backups older than ${RETENTION_DAYS} days..."
find ${BACKUP_DIR} -name "minio_*.tar.gz" -type f -mtime +${RETENTION_DAYS} -delete

# List remaining backups
BACKUP_COUNT=$(find ${BACKUP_DIR} -name "minio_*.tar.gz" -type f | wc -l)
echo "Total backups retained: ${BACKUP_COUNT}"

echo "=========================================="
echo "Backup process completed"
echo "=========================================="
