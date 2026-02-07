# Configuration Summary - Teaching Office Evaluation System
# 配置摘要 - 教研室工作考评系统

## Overview (概述)

This document provides a comprehensive summary of all configuration files and settings for the Teaching Office Evaluation System production deployment.

本文档提供教研室工作考评系统生产部署的所有配置文件和设置的综合摘要。

---

## Configuration Files (配置文件)

### 1. Environment Configuration (环境配置)

#### File: `backend/.env.production`

**Purpose**: Production environment variables for backend application

**Key Settings**:
- Database connection parameters
- MinIO object storage credentials
- JWT authentication secrets
- DeepSeek API configuration
- CORS and security settings
- Backup configuration
- Performance tuning parameters

**Security Notes**:
- All passwords and secrets must be changed from defaults
- Use strong, randomly generated values (minimum 32 characters)
- Never commit this file to version control
- Store securely in password manager

**Generation Commands**:
```bash
# Generate strong password
openssl rand -base64 32

# Generate hex key
openssl rand -hex 32

# Generate MinIO access key (20 chars)
openssl rand -hex 20

# Generate MinIO secret key (40 chars)
openssl rand -hex 40
```

---

### 2. Docker Compose Configuration (Docker Compose配置)

#### File: `docker-compose.production.yml`

**Purpose**: Production container orchestration

**Services Defined**:
1. **postgres**: PostgreSQL database
   - Image: postgres:15-alpine
   - Port: 5432
   - Volume: postgres_data
   - Health check enabled
   - Automatic restart

2. **minio**: MinIO object storage
   - Image: minio/minio:latest
   - Ports: 9000 (API), 9001 (Console)
   - Volume: minio_data
   - Health check enabled
   - Automatic restart

3. **backend**: FastAPI application
   - Build: backend/Dockerfile.production
   - Port: 8000
   - Depends on: postgres, minio
   - Log volume mounted
   - SSL volume mounted

4. **frontend**: Vue.js + Nginx
   - Build: frontend/Dockerfile.production
   - Ports: 80 (HTTP), 443 (HTTPS)
   - Depends on: backend
   - SSL volume mounted
   - Nginx config mounted

5. **postgres_backup**: Automated backup service
   - Runs daily backup script
   - Retention: 30 days (configurable)
   - Volume: backups/postgres

**Networks**:
- teaching_office_network (bridge)

**Volumes**:
- postgres_data (persistent database storage)
- minio_data (persistent object storage)

---

### 3. SSL/TLS Configuration (SSL配置)

#### Directory: `ssl/`

**Required Files**:
- `teaching-office.crt`: SSL certificate
- `teaching-office.key`: Private key
- `teaching-office-ca.crt`: CA bundle (optional)

**Certificate Sources**:
1. **Let's Encrypt** (Recommended for production)
   - Free, automated renewal
   - Trusted by all browsers
   - 90-day validity

2. **Commercial CA** (DigiCert, GlobalSign, etc.)
   - Extended validation options
   - Longer validity periods
   - Premium support

3. **Self-Signed** (Testing only)
   - Not trusted by browsers
   - Generates security warnings
   - Use only for development

**File Permissions**:
```bash
chmod 644 teaching-office.crt
chmod 600 teaching-office.key
```

**Renewal Schedule**:
- Let's Encrypt: Every 60 days (auto-renew at 30 days)
- Commercial: 30 days before expiration
- Set calendar reminders

---

### 4. Nginx Configuration (Nginx配置)

#### File: `nginx/nginx.conf`

**Key Features**:
- HTTP to HTTPS redirect
- SSL/TLS termination
- Reverse proxy to backend API
- Static file serving for frontend
- Gzip compression
- Security headers
- Rate limiting
- File upload optimization

**Security Headers**:
- X-Frame-Options: SAMEORIGIN
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security (HSTS)
- Referrer-Policy

**Rate Limiting**:
- API endpoints: 60 requests/minute
- Upload endpoints: 10 requests/minute
- Burst allowance configured

**File Upload**:
- Max body size: 500MB
- Timeout: 300 seconds
- Request buffering: off

**Customization Required**:
- Replace `your-production-domain.com` with actual domain
- Adjust rate limits based on expected traffic
- Configure SSL certificate paths

---

### 5. Database Configuration (数据库配置)

#### Connection Settings (in `.env`):
```
POSTGRES_SERVER=postgres
POSTGRES_USER=teaching_office_user
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=teaching_office_evaluation_prod
POSTGRES_PORT=5432
```

#### Connection Pool Settings:
```
POOL_SIZE=20
MAX_OVERFLOW=10
MAX_CONNECTIONS=100
```

#### Performance Tuning (PostgreSQL):
- shared_buffers: 2GB
- effective_cache_size: 6GB
- maintenance_work_mem: 512MB
- work_mem: 10MB
- max_connections: 100

#### Backup Configuration:
- Schedule: Daily at 2 AM
- Retention: 30 days
- Format: SQL dump (gzipped)
- Location: backups/postgres/

---

### 6. MinIO Configuration (MinIO配置)

#### Connection Settings (in `.env`):
```
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=<access-key>
MINIO_SECRET_KEY=<secret-key>
MINIO_BUCKET=teaching-office-attachments-prod
MINIO_SECURE=true
```

#### Bucket Configuration:
- Name: teaching-office-attachments-prod
- Policy: Private (no public access)
- Versioning: Enabled (recommended)
- Lifecycle: Delete temp files after 7 days

#### Storage Optimization:
- Compression: Enabled for text files
- Encryption: Server-side encryption (SSE)
- Replication: Configure for disaster recovery

#### Backup Configuration:
- Method: Mirror to local directory, then compress
- Schedule: Daily (manual or cron)
- Retention: 30 days
- Location: backups/minio/

---

### 7. Backup Configuration (备份配置)

#### Database Backup (PostgreSQL)

**Script**: `scripts/backup-postgres.sh`

**Features**:
- Automated daily backups
- Gzip compression
- Configurable retention period
- Backup verification
- Automatic cleanup of old backups

**Configuration**:
```bash
BACKUP_DIR=/backups
RETENTION_DAYS=30
BACKUP_SCHEDULE="0 2 * * *"  # Daily at 2 AM
```

**Backup File Format**:
```
teaching_office_YYYYMMDD_HHMMSS.sql.gz
```

#### MinIO Backup

**Script**: `scripts/backup-minio.sh`

**Features**:
- Full bucket mirror
- Tar.gz compression
- Configurable retention
- Automatic cleanup

**Configuration**:
```bash
BACKUP_DIR=/backups
RETENTION_DAYS=30
```

**Backup File Format**:
```
minio_YYYYMMDD_HHMMSS.tar.gz
```

#### Restore Procedures

**Database Restore**:
```bash
./scripts/restore-postgres.sh backups/postgres/teaching_office_YYYYMMDD_HHMMSS.sql.gz
```

**MinIO Restore**:
```bash
# Extract backup
tar -xzf backups/minio/minio_YYYYMMDD_HHMMSS.tar.gz -C /tmp/restore

# Mirror to MinIO
mc mirror /tmp/restore myminio/teaching-office-attachments-prod
```

---

### 8. Application Configuration (应用配置)

#### Backend (FastAPI)

**File**: `backend/app/core/config.py`

**Key Settings**:
- Project name and version
- API prefix (/api)
- Database URL construction
- MinIO connection parameters
- JWT configuration
- CORS origins
- Logging configuration

**Production Overrides** (in `.env`):
```
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
WORKERS=4
```

#### Frontend (Vue.js)

**Build Configuration**: `frontend/vite.config.ts`

**Production Build**:
```bash
npm run build
```

**Output**: `frontend/dist/`

**Environment Variables**:
- API base URL
- Application title
- Feature flags

---

## Security Configuration (安全配置)

### 1. Authentication (认证)

**Method**: JWT (JSON Web Tokens)

**Configuration**:
```
SECRET_KEY=<strong-random-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days
```

**Security Best Practices**:
- Use strong, random secret key (32+ characters)
- Rotate secret key periodically
- Implement token refresh mechanism
- Store tokens securely on client side

### 2. Authorization (授权)

**Roles**:
- teaching_office: Teaching office users
- evaluation_team: Evaluation team members
- evaluation_office: Evaluation office staff
- president_office: President office staff

**Access Control**:
- Role-based access control (RBAC)
- Endpoint-level permissions
- Resource-level permissions

### 3. HTTPS/TLS

**Configuration**:
- TLS 1.2 and 1.3 only
- Strong cipher suites
- HSTS enabled
- Certificate pinning (optional)

### 4. Rate Limiting

**API Endpoints**:
- 60 requests per minute per IP
- Burst: 20 requests

**Upload Endpoints**:
- 10 requests per minute per IP
- Burst: 5 requests

### 5. Input Validation

**Backend**:
- Pydantic models for request validation
- SQL injection prevention (SQLAlchemy ORM)
- XSS prevention (output encoding)

**Frontend**:
- Form validation
- Input sanitization
- CSRF protection

### 6. Firewall Rules

**Required Ports**:
- 80 (HTTP - redirect to HTTPS)
- 443 (HTTPS)
- 5432 (PostgreSQL - restrict to localhost or specific IPs)
- 9000 (MinIO API - restrict to localhost or specific IPs)
- 9001 (MinIO Console - restrict to admin IPs)

**UFW Configuration**:
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow from <trusted-ip> to any port 5432
sudo ufw allow from <trusted-ip> to any port 9000
sudo ufw allow from <trusted-ip> to any port 9001
sudo ufw enable
```

---

## Performance Configuration (性能配置)

### 1. Backend Performance

**Gunicorn Workers**:
```
WORKERS=4  # (2 x CPU cores) + 1
```

**Database Connection Pool**:
```
POOL_SIZE=20
MAX_OVERFLOW=10
```

**Caching** (if implemented):
- Redis for session storage
- Application-level caching
- Database query caching

### 2. Frontend Performance

**Nginx Optimization**:
- Gzip compression enabled
- Static asset caching (1 year)
- HTTP/2 enabled
- Keepalive connections

**Build Optimization**:
- Code splitting
- Tree shaking
- Minification
- Asset optimization

### 3. Database Performance

**Indexing**:
- Primary keys
- Foreign keys
- Frequently queried columns

**Query Optimization**:
- Use EXPLAIN ANALYZE
- Optimize N+1 queries
- Use database views for complex queries

**Maintenance**:
```sql
VACUUM ANALYZE;  -- Weekly
REINDEX;         -- Monthly
```

### 4. Storage Performance

**MinIO**:
- SSD storage recommended
- Erasure coding for redundancy
- Distributed mode for high availability

---

## Monitoring Configuration (监控配置)

### 1. Application Logs

**Location**:
- Backend: `backend/logs/`
- Nginx: `/var/log/nginx/`
- Docker: `docker logs <container>`

**Log Levels**:
- Production: INFO
- Debug: DEBUG (temporary)

**Log Rotation**:
- Max size: 10MB
- Max files: 3
- Compression: enabled

### 2. Health Checks

**Endpoints**:
- Backend: `https://domain.com/api/health`
- Frontend: `https://domain.com/health`

**Docker Health Checks**:
- Interval: 30 seconds
- Timeout: 10 seconds
- Retries: 3

### 3. Metrics Collection

**System Metrics**:
- CPU usage
- Memory usage
- Disk usage
- Network I/O

**Application Metrics**:
- Request rate
- Response time
- Error rate
- Active users

**Database Metrics**:
- Connection count
- Query performance
- Cache hit rate
- Replication lag

### 4. Alerting

**Alert Conditions**:
- Service down
- High error rate (>5%)
- High response time (>2s)
- Disk usage >80%
- Memory usage >90%
- Certificate expiring (<30 days)

**Alert Channels**:
- Email
- SMS
- Slack/Teams
- PagerDuty

---

## Maintenance Configuration (维护配置)

### 1. Update Schedule

**Security Updates**:
- Apply immediately for critical vulnerabilities
- Weekly for non-critical updates

**Application Updates**:
- Monthly release cycle
- Hotfixes as needed

**Dependency Updates**:
- Quarterly review
- Update to latest stable versions

### 2. Backup Schedule

**Daily**:
- Database backup (2 AM)
- MinIO backup (3 AM)

**Weekly**:
- Full system backup
- Backup verification

**Monthly**:
- Off-site backup sync
- Disaster recovery drill

### 3. Maintenance Windows

**Scheduled Maintenance**:
- Day: Sunday
- Time: 2:00 AM - 4:00 AM (local time)
- Frequency: Monthly

**Emergency Maintenance**:
- As needed for critical issues
- Notify users 1 hour in advance (if possible)

---

## Disaster Recovery Configuration (灾难恢复配置)

### 1. Backup Strategy

**3-2-1 Rule**:
- 3 copies of data
- 2 different storage types
- 1 off-site backup

**Implementation**:
- Primary: Production database and storage
- Secondary: Local backups (backups/ directory)
- Tertiary: Off-site backups (S3, remote server)

### 2. Recovery Time Objective (RTO)

**Target**: 4 hours

**Procedures**:
1. Provision new server (1 hour)
2. Restore from backup (2 hours)
3. Verify and test (1 hour)

### 3. Recovery Point Objective (RPO)

**Target**: 24 hours

**Implementation**:
- Daily backups ensure maximum 24-hour data loss
- Consider more frequent backups for critical periods

### 4. Failover Configuration

**Database**:
- Primary-replica setup (optional)
- Automatic failover (optional)
- Manual failover procedure documented

**Application**:
- Load balancer with health checks (optional)
- Multiple application instances (optional)
- Blue-green deployment (optional)

---

## Compliance Configuration (合规配置)

### 1. Data Privacy

**GDPR/Privacy Compliance**:
- Data encryption at rest and in transit
- User consent management
- Data retention policies
- Right to deletion

### 2. Audit Logging

**Logged Events**:
- User authentication
- Data access
- Data modifications
- Administrative actions

**Log Retention**:
- Minimum: 1 year
- Recommended: 3 years

### 3. Access Control

**Principle of Least Privilege**:
- Users have minimum necessary permissions
- Regular access reviews
- Immediate revocation on termination

---

## Troubleshooting Configuration (故障排除配置)

### 1. Debug Mode

**Enable Debug Logging** (temporary):
```bash
# In .env
LOG_LEVEL=DEBUG
DEBUG=true

# Restart services
docker-compose -f docker-compose.production.yml restart backend
```

**Disable After Troubleshooting**:
```bash
LOG_LEVEL=INFO
DEBUG=false
```

### 2. Common Issues

See `DEPLOYMENT_GUIDE.md` Troubleshooting section for detailed procedures.

---

## Configuration Validation (配置验证)

### Pre-Deployment Checklist

Use `DEPLOYMENT_CHECKLIST.md` to verify all configurations before deployment.

### Validation Commands

```bash
# Validate environment file
cat backend/.env | grep -v '^#' | grep -v '^$'

# Validate Docker Compose
docker-compose -f docker-compose.production.yml config

# Validate Nginx configuration
docker run --rm -v $(pwd)/nginx/nginx.conf:/etc/nginx/nginx.conf:ro nginx nginx -t

# Validate SSL certificate
openssl x509 -in ssl/teaching-office.crt -text -noout
```

---

## Support and Documentation (支持与文档)

### Additional Resources

- **Deployment Guide**: `DEPLOYMENT_GUIDE.md`
- **Deployment Checklist**: `DEPLOYMENT_CHECKLIST.md`
- **SSL Configuration**: `ssl/README.md`
- **Backup Scripts**: `scripts/`

### Contact Information

- Technical Support: support@your-domain.com
- Emergency Hotline: [Phone number]
- Documentation: [Link to documentation]
- Issue Tracker: [Link to issue tracker]

---

## Version History (版本历史)

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | YYYY-MM-DD | Initial production configuration | [Name] |

---

**Last Updated**: [Date]
**Reviewed By**: [Name]
**Next Review Date**: [Date]
