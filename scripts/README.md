# Backup and Maintenance Scripts
# 备份和维护脚本

## Overview (概述)

This directory contains scripts for database backup, MinIO backup, and system maintenance.

本目录包含数据库备份、MinIO备份和系统维护的脚本。

## Scripts (脚本)

### 1. backup-postgres.sh

**Purpose**: Automated PostgreSQL database backup

**Usage**:
```bash
# Manual execution
./scripts/backup-postgres.sh

# Via Docker
docker-compose -f docker-compose.production.yml exec postgres_backup /backup.sh
```

**Features**:
- Creates compressed SQL dump
- Automatic cleanup of old backups
- Configurable retention period
- Backup verification

**Configuration**:
- `BACKUP_RETENTION_DAYS`: Number of days to keep backups (default: 30)
- Backups stored in: `backups/postgres/`

**Output Format**:
```
teaching_office_YYYYMMDD_HHMMSS.sql.gz
```

---

### 2. backup-minio.sh

**Purpose**: Automated MinIO object storage backup

**Usage**:
```bash
# Manual execution
./scripts/backup-minio.sh
```

**Features**:
- Mirrors entire bucket to local directory
- Creates compressed archive
- Automatic cleanup of old backups
- Configurable retention period

**Configuration**:
- `BACKUP_RETENTION_DAYS`: Number of days to keep backups (default: 30)
- Backups stored in: `backups/minio/`

**Output Format**:
```
minio_YYYYMMDD_HHMMSS.tar.gz
```

**Prerequisites**:
- MinIO Client (mc) installed
- MinIO credentials configured

---

### 3. restore-postgres.sh

**Purpose**: Restore PostgreSQL database from backup

**Usage**:
```bash
# List available backups
./scripts/restore-postgres.sh

# Restore specific backup
./scripts/restore-postgres.sh backups/postgres/teaching_office_20240101_020000.sql.gz
```

**Features**:
- Interactive confirmation
- Terminates existing connections
- Drops and recreates database
- Restores from compressed backup

**Warning**: This will overwrite all existing data!

---

## Automated Backup Schedule (自动备份计划)

### Database Backup

Configured in `docker-compose.production.yml`:

```yaml
postgres_backup:
  # Runs daily backup
  command: |
    while true; do
      sleep 86400  # 24 hours
      /backup.sh
    done
```

**Default Schedule**: Daily at container startup + 24 hours

**To customize**: Modify the sleep duration or use cron

### MinIO Backup

**Manual execution required** or set up cron job:

```bash
# Edit crontab
crontab -e

# Add daily backup at 3 AM
0 3 * * * /path/to/scripts/backup-minio.sh >> /var/log/minio-backup.log 2>&1
```

---

## Backup Verification (备份验证)

### Verify Database Backup

```bash
# List backups
ls -lh backups/postgres/

# Check backup file integrity
gunzip -t backups/postgres/teaching_office_YYYYMMDD_HHMMSS.sql.gz

# View backup contents (first 100 lines)
gunzip -c backups/postgres/teaching_office_YYYYMMDD_HHMMSS.sql.gz | head -n 100
```

### Verify MinIO Backup

```bash
# List backups
ls -lh backups/minio/

# Check archive integrity
tar -tzf backups/minio/minio_YYYYMMDD_HHMMSS.tar.gz > /dev/null

# List archive contents
tar -tzf backups/minio/minio_YYYYMMDD_HHMMSS.tar.gz | head -n 20
```

---

## Restore Procedures (恢复程序)

### Database Restore

**⚠️ WARNING**: This will delete all existing data!

1. **Stop application services**:
```bash
docker-compose -f docker-compose.production.yml stop backend
```

2. **Restore database**:
```bash
./scripts/restore-postgres.sh backups/postgres/teaching_office_YYYYMMDD_HHMMSS.sql.gz
```

3. **Restart services**:
```bash
docker-compose -f docker-compose.production.yml start backend
```

4. **Verify restoration**:
```bash
docker-compose -f docker-compose.production.yml exec postgres psql -U teaching_office_user -d teaching_office_evaluation_prod -c "SELECT COUNT(*) FROM users;"
```

### MinIO Restore

1. **Extract backup**:
```bash
mkdir -p /tmp/minio-restore
tar -xzf backups/minio/minio_YYYYMMDD_HHMMSS.tar.gz -C /tmp/minio-restore
```

2. **Mirror to MinIO**:
```bash
mc mirror /tmp/minio-restore myminio/teaching-office-attachments-prod
```

3. **Verify restoration**:
```bash
mc ls myminio/teaching-office-attachments-prod
```

4. **Cleanup**:
```bash
rm -rf /tmp/minio-restore
```

---

## Off-Site Backup (异地备份)

### Using rsync

```bash
# Sync to remote server
rsync -avz --delete backups/ user@backup-server:/path/to/backups/
```

### Using AWS S3

```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure

# Sync to S3
aws s3 sync backups/ s3://your-backup-bucket/teaching-office-backups/
```

### Using rclone

```bash
# Install rclone
curl https://rclone.org/install.sh | sudo bash

# Configure remote
rclone config

# Sync to remote
rclone sync backups/ remote:teaching-office-backups/
```

---

## Monitoring Backups (监控备份)

### Check Backup Status

```bash
# List recent backups
ls -lt backups/postgres/ | head -n 5
ls -lt backups/minio/ | head -n 5

# Check backup sizes
du -sh backups/postgres/
du -sh backups/minio/

# Count backups
echo "PostgreSQL backups: $(ls backups/postgres/*.sql.gz 2>/dev/null | wc -l)"
echo "MinIO backups: $(ls backups/minio/*.tar.gz 2>/dev/null | wc -l)"
```

### Backup Alerts

Set up monitoring to alert if:
- Backup fails
- Backup size is unusually small (possible corruption)
- No backup in last 48 hours
- Disk space low (<20%)

---

## Troubleshooting (故障排除)

### Backup Script Fails

**Check logs**:
```bash
docker-compose -f docker-compose.production.yml logs postgres_backup
```

**Common issues**:
1. Insufficient disk space
2. Database connection failed
3. Permission denied

**Solutions**:
```bash
# Check disk space
df -h

# Check database connection
docker-compose -f docker-compose.production.yml exec postgres pg_isready

# Check permissions
ls -la backups/
```

### Restore Fails

**Common issues**:
1. Backup file corrupted
2. Database version mismatch
3. Insufficient permissions

**Solutions**:
```bash
# Verify backup integrity
gunzip -t backups/postgres/teaching_office_YYYYMMDD_HHMMSS.sql.gz

# Check PostgreSQL version
docker-compose -f docker-compose.production.yml exec postgres psql --version

# Check permissions
ls -la backups/postgres/
```

---

## Best Practices (最佳实践)

1. **Test restores regularly** (monthly)
2. **Monitor backup completion** (automated alerts)
3. **Keep multiple backup copies** (3-2-1 rule)
4. **Encrypt sensitive backups**
5. **Document restore procedures**
6. **Verify backup integrity**
7. **Store backups off-site**
8. **Rotate backup retention** (keep daily for 7 days, weekly for 4 weeks, monthly for 12 months)

---

## Maintenance Schedule (维护计划)

### Daily
- Automated database backup
- Automated MinIO backup (if configured)
- Check backup completion

### Weekly
- Verify backup integrity
- Test restore on staging environment
- Review backup sizes

### Monthly
- Full disaster recovery drill
- Review and update retention policies
- Clean up old backups manually if needed

---

## Support (支持)

For issues with backup scripts:
- Check logs: `docker-compose -f docker-compose.production.yml logs`
- Review documentation: `DEPLOYMENT_GUIDE.md`
- Contact support: support@your-domain.com
