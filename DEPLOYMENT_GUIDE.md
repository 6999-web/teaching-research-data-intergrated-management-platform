# Deployment Guide - Teaching Office Evaluation System
# 部署指南 - 教研室工作考评系统

## Table of Contents (目录)

1. [Prerequisites (前置要求)](#prerequisites)
2. [Environment Configuration (环境配置)](#environment-configuration)
3. [SSL/TLS Certificate Setup (SSL证书配置)](#ssl-certificate-setup)
4. [Database Configuration (数据库配置)](#database-configuration)
5. [MinIO Storage Configuration (MinIO存储配置)](#minio-storage-configuration)
6. [Backup Strategy (备份策略)](#backup-strategy)
7. [Deployment Steps (部署步骤)](#deployment-steps)
8. [Post-Deployment Verification (部署后验证)](#post-deployment-verification)
9. [Monitoring and Maintenance (监控与维护)](#monitoring-and-maintenance)
10. [Troubleshooting (故障排除)](#troubleshooting)

---

## Prerequisites (前置要求)

### System Requirements (系统要求)

- **Operating System**: Linux (Ubuntu 20.04+ or CentOS 8+ recommended)
- **CPU**: 4 cores minimum (8 cores recommended)
- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 100GB minimum (SSD recommended)
- **Network**: Static IP address with domain name

### Software Requirements (软件要求)

- Docker 20.10+
- Docker Compose 2.0+
- Git
- OpenSSL (for certificate generation)

### Installation (安装)

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

---

## Environment Configuration (环境配置)

### 1. Clone Repository (克隆仓库)

```bash
git clone <repository-url>
cd teaching-office-evaluation-system
```

### 2. Configure Production Environment (配置生产环境)

```bash
# Copy production environment template
cp backend/.env.production backend/.env

# Edit environment variables
nano backend/.env
```

### 3. Required Environment Variables (必需的环境变量)

Update the following variables in `backend/.env`:

#### Database Configuration (数据库配置)
```bash
POSTGRES_USER=teaching_office_user
POSTGRES_PASSWORD=<STRONG_PASSWORD>  # Generate: openssl rand -base64 32
POSTGRES_DB=teaching_office_evaluation_prod
```

#### MinIO Configuration (MinIO配置)
```bash
MINIO_ACCESS_KEY=<MINIO_ACCESS_KEY>  # Generate: openssl rand -hex 20
MINIO_SECRET_KEY=<MINIO_SECRET_KEY>  # Generate: openssl rand -hex 40
MINIO_BUCKET=teaching-office-attachments-prod
MINIO_SECURE=true
```

#### JWT Configuration (JWT配置)
```bash
SECRET_KEY=<JWT_SECRET_KEY>  # Generate: openssl rand -hex 32
```

#### DeepSeek API Configuration (DeepSeek API配置)
```bash
DEEPSEEK_API_KEY=<YOUR_DEEPSEEK_API_KEY>
```

#### CORS Configuration (跨域配置)
```bash
BACKEND_CORS_ORIGINS=["https://your-production-domain.com"]
```

---

## SSL Certificate Setup (SSL证书配置)

### Option 1: Let's Encrypt (Recommended for Production)

```bash
# Install Certbot
sudo apt-get install certbot

# Obtain certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./ssl/teaching-office.crt
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./ssl/teaching-office.key

# Set permissions
chmod 644 ./ssl/teaching-office.crt
chmod 600 ./ssl/teaching-office.key
```

### Option 2: Self-Signed Certificate (Testing Only)

```bash
cd ssl

# Generate private key
openssl genrsa -out teaching-office.key 2048

# Generate certificate
openssl req -new -x509 -key teaching-office.key -out teaching-office.crt -days 365

# Set permissions
chmod 644 teaching-office.crt
chmod 600 teaching-office.key
```

### Update Nginx Configuration (更新Nginx配置)

Edit `nginx/nginx.conf` and replace `your-production-domain.com` with your actual domain.

---

## Database Configuration (数据库配置)

### 1. Initialize Database (初始化数据库)

The database will be automatically initialized on first startup. To manually initialize:

```bash
# Start only the database
docker-compose -f docker-compose.production.yml up -d postgres

# Wait for database to be ready
sleep 10

# Run migrations
docker-compose -f docker-compose.production.yml exec backend alembic upgrade head
```

### 2. Database Connection Pool (数据库连接池)

Configure in `backend/.env`:

```bash
POOL_SIZE=20
MAX_OVERFLOW=10
MAX_CONNECTIONS=100
```

### 3. Database Performance Tuning (数据库性能调优)

For production, consider tuning PostgreSQL settings:

```bash
# Edit postgresql.conf
max_connections = 100
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 10MB
min_wal_size = 1GB
max_wal_size = 4GB
```

---

## MinIO Storage Configuration (MinIO存储配置)

### 1. Create Bucket (创建存储桶)

After starting MinIO, create the bucket:

```bash
# Install MinIO Client
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc
sudo mv mc /usr/local/bin/

# Configure MinIO client
mc alias set myminio https://your-domain.com:9000 <MINIO_ACCESS_KEY> <MINIO_SECRET_KEY>

# Create bucket
mc mb myminio/teaching-office-attachments-prod

# Set bucket policy (private)
mc anonymous set none myminio/teaching-office-attachments-prod
```

### 2. Storage Lifecycle Policy (存储生命周期策略)

Configure automatic cleanup of temporary files:

```bash
# Create lifecycle policy
cat > lifecycle.json <<EOF
{
  "Rules": [
    {
      "ID": "DeleteTempFiles",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "temp/"
      },
      "Expiration": {
        "Days": 7
      }
    }
  ]
}
EOF

# Apply lifecycle policy
mc ilm import myminio/teaching-office-attachments-prod < lifecycle.json
```

### 3. Storage Monitoring (存储监控)

```bash
# Check bucket size
mc du myminio/teaching-office-attachments-prod

# List objects
mc ls myminio/teaching-office-attachments-prod
```

---

## Backup Strategy (备份策略)

### 1. Automated Database Backups (自动数据库备份)

Backups are configured to run daily at 2 AM (configurable in docker-compose.production.yml).

#### Manual Backup (手动备份)

```bash
# Run backup script
docker-compose -f docker-compose.production.yml exec postgres_backup /backup.sh
```

#### Backup Configuration (备份配置)

Edit `backend/.env`:

```bash
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 2 * * *  # Daily at 2 AM
BACKUP_RETENTION_DAYS=30   # Keep backups for 30 days
```

### 2. MinIO Storage Backups (MinIO存储备份)

```bash
# Make backup script executable
chmod +x scripts/backup-minio.sh

# Run backup
./scripts/backup-minio.sh
```

### 3. Backup Verification (备份验证)

```bash
# List database backups
ls -lh backups/postgres/

# List MinIO backups
ls -lh backups/minio/

# Test restore (on test environment only!)
./scripts/restore-postgres.sh backups/postgres/teaching_office_YYYYMMDD_HHMMSS.sql.gz
```

### 4. Off-Site Backup (异地备份)

For disaster recovery, sync backups to remote storage:

```bash
# Using rsync to remote server
rsync -avz --delete backups/ user@backup-server:/path/to/backups/

# Using AWS S3
aws s3 sync backups/ s3://your-backup-bucket/teaching-office-backups/

# Using rclone (supports multiple cloud providers)
rclone sync backups/ remote:teaching-office-backups/
```

---

## Deployment Steps (部署步骤)

### 1. Pre-Deployment Checklist (部署前检查清单)

- [ ] Environment variables configured
- [ ] SSL certificates in place
- [ ] Domain DNS configured
- [ ] Firewall rules configured (ports 80, 443, 5432, 9000, 9001)
- [ ] Backup directories created
- [ ] Docker and Docker Compose installed

### 2. Build and Start Services (构建并启动服务)

```bash
# Create necessary directories
mkdir -p backups/postgres backups/minio backend/logs

# Make backup scripts executable
chmod +x scripts/*.sh

# Build and start all services
docker-compose -f docker-compose.production.yml up -d --build

# Check service status
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f
```

### 3. Initialize Application (初始化应用)

```bash
# Run database migrations
docker-compose -f docker-compose.production.yml exec backend alembic upgrade head

# Create initial admin user (if script exists)
docker-compose -f docker-compose.production.yml exec backend python scripts/create_admin.py

# Initialize MinIO bucket
mc alias set myminio https://your-domain.com:9000 <ACCESS_KEY> <SECRET_KEY>
mc mb myminio/teaching-office-attachments-prod
```

### 4. Verify Deployment (验证部署)

```bash
# Check backend health
curl https://your-domain.com/api/health

# Check frontend
curl https://your-domain.com/

# Check database connection
docker-compose -f docker-compose.production.yml exec postgres psql -U teaching_office_user -d teaching_office_evaluation_prod -c "SELECT version();"

# Check MinIO
mc admin info myminio
```

---

## Post-Deployment Verification (部署后验证)

### 1. Functional Testing (功能测试)

- [ ] User login works
- [ ] Self-evaluation form submission works
- [ ] File upload works
- [ ] AI scoring triggers successfully
- [ ] Manual scoring works
- [ ] Data synchronization works
- [ ] Result publication works

### 2. Performance Testing (性能测试)

```bash
# Test API response time
curl -w "@curl-format.txt" -o /dev/null -s https://your-domain.com/api/health

# Load testing (using Apache Bench)
ab -n 1000 -c 10 https://your-domain.com/api/health
```

### 3. Security Testing (安全测试)

```bash
# Check SSL configuration
openssl s_client -connect your-domain.com:443 -tls1_2

# Check security headers
curl -I https://your-domain.com/

# Scan for vulnerabilities (using nmap)
nmap -sV --script ssl-enum-ciphers -p 443 your-domain.com
```

---

## Monitoring and Maintenance (监控与维护)

### 1. Log Monitoring (日志监控)

```bash
# View all logs
docker-compose -f docker-compose.production.yml logs -f

# View specific service logs
docker-compose -f docker-compose.production.yml logs -f backend
docker-compose -f docker-compose.production.yml logs -f postgres

# Check log files
tail -f backend/logs/app.log
```

### 2. Resource Monitoring (资源监控)

```bash
# Check container resource usage
docker stats

# Check disk usage
df -h
du -sh backups/

# Check database size
docker-compose -f docker-compose.production.yml exec postgres psql -U teaching_office_user -d teaching_office_evaluation_prod -c "SELECT pg_size_pretty(pg_database_size('teaching_office_evaluation_prod'));"
```

### 3. Automated Monitoring (自动化监控)

Consider setting up monitoring tools:

- **Prometheus + Grafana**: For metrics and dashboards
- **ELK Stack**: For log aggregation and analysis
- **Uptime monitoring**: Pingdom, UptimeRobot, or StatusCake
- **APM**: New Relic, Datadog, or Application Insights

### 4. Regular Maintenance Tasks (定期维护任务)

#### Daily (每日)
- Check service health
- Review error logs
- Verify backups completed

#### Weekly (每周)
- Review resource usage
- Check disk space
- Test backup restoration (on test environment)

#### Monthly (每月)
- Update dependencies
- Review security patches
- Optimize database (VACUUM, ANALYZE)
- Review and rotate logs

#### Quarterly (每季度)
- Security audit
- Performance review
- Disaster recovery drill
- Certificate renewal check

---

## Troubleshooting (故障排除)

### Common Issues (常见问题)

#### 1. Services Won't Start (服务无法启动)

```bash
# Check logs
docker-compose -f docker-compose.production.yml logs

# Check if ports are in use
sudo netstat -tulpn | grep -E ':(80|443|5432|9000|9001)'

# Restart services
docker-compose -f docker-compose.production.yml restart
```

#### 2. Database Connection Failed (数据库连接失败)

```bash
# Check database is running
docker-compose -f docker-compose.production.yml ps postgres

# Check database logs
docker-compose -f docker-compose.production.yml logs postgres

# Test connection
docker-compose -f docker-compose.production.yml exec postgres psql -U teaching_office_user -d teaching_office_evaluation_prod
```

#### 3. SSL Certificate Issues (SSL证书问题)

```bash
# Verify certificate
openssl x509 -in ssl/teaching-office.crt -text -noout

# Check certificate expiration
openssl x509 -in ssl/teaching-office.crt -noout -dates

# Verify certificate and key match
openssl x509 -noout -modulus -in ssl/teaching-office.crt | openssl md5
openssl rsa -noout -modulus -in ssl/teaching-office.key | openssl md5
```

#### 4. File Upload Fails (文件上传失败)

```bash
# Check MinIO is running
docker-compose -f docker-compose.production.yml ps minio

# Check MinIO logs
docker-compose -f docker-compose.production.yml logs minio

# Verify bucket exists
mc ls myminio/teaching-office-attachments-prod

# Check disk space
df -h
```

#### 5. High Memory Usage (内存使用率高)

```bash
# Check container memory usage
docker stats

# Restart specific service
docker-compose -f docker-compose.production.yml restart backend

# Adjust memory limits in docker-compose.production.yml
```

### Emergency Procedures (应急程序)

#### Complete System Restart (完整系统重启)

```bash
# Stop all services
docker-compose -f docker-compose.production.yml down

# Wait 10 seconds
sleep 10

# Start all services
docker-compose -f docker-compose.production.yml up -d

# Monitor startup
docker-compose -f docker-compose.production.yml logs -f
```

#### Rollback Deployment (回滚部署)

```bash
# Stop current deployment
docker-compose -f docker-compose.production.yml down

# Restore database from backup
./scripts/restore-postgres.sh backups/postgres/teaching_office_YYYYMMDD_HHMMSS.sql.gz

# Checkout previous version
git checkout <previous-commit-hash>

# Rebuild and start
docker-compose -f docker-compose.production.yml up -d --build
```

---

## Support and Contact (支持与联系)

For additional support:

- Documentation: [Link to documentation]
- Issue Tracker: [Link to issue tracker]
- Email: support@your-domain.com
- Emergency Hotline: [Phone number]

---

## Appendix (附录)

### A. Firewall Configuration (防火墙配置)

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow PostgreSQL (only from specific IPs if needed)
sudo ufw allow from <trusted-ip> to any port 5432

# Allow MinIO (only from specific IPs if needed)
sudo ufw allow from <trusted-ip> to any port 9000
sudo ufw allow from <trusted-ip> to any port 9001

# Enable firewall
sudo ufw enable
```

### B. System Optimization (系统优化)

```bash
# Increase file descriptor limits
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Optimize kernel parameters
sudo sysctl -w net.core.somaxconn=1024
sudo sysctl -w net.ipv4.tcp_max_syn_backlog=2048
```

### C. Useful Commands (常用命令)

```bash
# View all running containers
docker ps

# Execute command in container
docker-compose -f docker-compose.production.yml exec <service> <command>

# Copy files from container
docker cp <container-id>:/path/in/container /path/on/host

# View container resource usage
docker stats --no-stream

# Clean up unused Docker resources
docker system prune -a
```
