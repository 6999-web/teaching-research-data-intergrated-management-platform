# Deployment Checklist - Teaching Office Evaluation System
# 部署检查清单 - 教研室工作考评系统

## Pre-Deployment (部署前)

### Infrastructure (基础设施)

- [ ] Server provisioned with minimum requirements (4 CPU, 8GB RAM, 100GB storage)
- [ ] Static IP address assigned
- [ ] Domain name configured and DNS propagated
- [ ] Firewall configured (ports 80, 443, 5432, 9000, 9001)
- [ ] SSH access configured with key-based authentication
- [ ] Non-root user created with sudo privileges

### Software Installation (软件安装)

- [ ] Docker installed and running (version 20.10+)
- [ ] Docker Compose installed (version 2.0+)
- [ ] Git installed
- [ ] OpenSSL installed
- [ ] System packages updated (`apt-get update && apt-get upgrade`)

### Repository Setup (仓库设置)

- [ ] Repository cloned to server
- [ ] Correct branch checked out (main/production)
- [ ] Git credentials configured (if needed for updates)

## Configuration (配置)

### Environment Variables (环境变量)

- [ ] `backend/.env` file created from `.env.production` template
- [ ] `POSTGRES_USER` set to unique username
- [ ] `POSTGRES_PASSWORD` set to strong password (32+ characters)
- [ ] `POSTGRES_DB` set to production database name
- [ ] `MINIO_ACCESS_KEY` generated (20+ characters)
- [ ] `MINIO_SECRET_KEY` generated (40+ characters)
- [ ] `SECRET_KEY` generated for JWT (32+ characters)
- [ ] `DEEPSEEK_API_KEY` configured with valid API key
- [ ] `BACKEND_CORS_ORIGINS` set to production domain
- [ ] `ALLOWED_HOSTS` configured with production domain

### SSL/TLS Certificates (SSL证书)

- [ ] SSL certificate obtained (Let's Encrypt or commercial CA)
- [ ] Certificate file placed at `ssl/teaching-office.crt`
- [ ] Private key file placed at `ssl/teaching-office.key`
- [ ] Certificate permissions set correctly (644 for .crt, 600 for .key)
- [ ] Certificate verified with `openssl x509 -in ssl/teaching-office.crt -text -noout`
- [ ] Certificate and key match verified
- [ ] Certificate expiration date noted (set reminder for renewal)

### Nginx Configuration (Nginx配置)

- [ ] `nginx/nginx.conf` updated with production domain name
- [ ] SSL certificate paths verified in nginx.conf
- [ ] Rate limiting configured appropriately
- [ ] Client max body size set for file uploads (100M+)
- [ ] Gzip compression enabled
- [ ] Security headers configured

### Docker Configuration (Docker配置)

- [ ] `docker-compose.production.yml` reviewed
- [ ] Service resource limits configured (if needed)
- [ ] Volume paths verified
- [ ] Network configuration reviewed
- [ ] Logging configuration set

## Backup Configuration (备份配置)

### Backup Scripts (备份脚本)

- [ ] Backup scripts made executable (`chmod +x scripts/*.sh`)
- [ ] Backup directories created (`mkdir -p backups/postgres backups/minio`)
- [ ] Backup retention days configured in `.env`
- [ ] Backup schedule verified in docker-compose.production.yml

### Off-Site Backup (异地备份)

- [ ] Remote backup location configured (S3, rsync, rclone)
- [ ] Backup sync script created and tested
- [ ] Backup sync scheduled (cron job)
- [ ] Backup encryption configured (if required)

## Deployment (部署)

### Initial Deployment (初始部署)

- [ ] All configuration files reviewed and validated
- [ ] Backup directories created
- [ ] Log directories created (`mkdir -p backend/logs`)
- [ ] Docker images built (`docker-compose -f docker-compose.production.yml build`)
- [ ] Services started (`docker-compose -f docker-compose.production.yml up -d`)
- [ ] All containers running (`docker-compose -f docker-compose.production.yml ps`)
- [ ] No errors in logs (`docker-compose -f docker-compose.production.yml logs`)

### Database Initialization (数据库初始化)

- [ ] Database migrations run (`alembic upgrade head`)
- [ ] Initial admin user created
- [ ] Database connection verified
- [ ] Sample data loaded (if applicable)

### MinIO Initialization (MinIO初始化)

- [ ] MinIO client (mc) installed
- [ ] MinIO alias configured
- [ ] Production bucket created
- [ ] Bucket policy set to private
- [ ] Lifecycle policy configured (if applicable)

## Verification (验证)

### Service Health Checks (服务健康检查)

- [ ] Backend health endpoint responds (`curl https://domain.com/api/health`)
- [ ] Frontend loads successfully (`curl https://domain.com/`)
- [ ] Database accepts connections
- [ ] MinIO accepts connections
- [ ] All Docker containers healthy

### Functional Testing (功能测试)

- [ ] User can access login page
- [ ] User can log in successfully
- [ ] Self-evaluation form loads
- [ ] File upload works
- [ ] AI scoring can be triggered
- [ ] Manual scoring interface works
- [ ] Data synchronization works
- [ ] Result publication works

### Security Testing (安全测试)

- [ ] HTTPS enforced (HTTP redirects to HTTPS)
- [ ] SSL certificate valid and trusted
- [ ] Security headers present (X-Frame-Options, X-Content-Type-Options, etc.)
- [ ] HSTS header configured
- [ ] Rate limiting works
- [ ] Unauthorized access blocked
- [ ] SQL injection protection verified
- [ ] XSS protection verified

### Performance Testing (性能测试)

- [ ] API response time acceptable (<500ms for simple requests)
- [ ] File upload speed acceptable
- [ ] Database query performance acceptable
- [ ] Frontend load time acceptable (<3s)
- [ ] Concurrent user handling tested

## Monitoring Setup (监控设置)

### Log Monitoring (日志监控)

- [ ] Application logs accessible
- [ ] Error logs reviewed
- [ ] Log rotation configured
- [ ] Log aggregation tool configured (optional: ELK, Splunk)

### Resource Monitoring (资源监控)

- [ ] CPU usage monitored
- [ ] Memory usage monitored
- [ ] Disk usage monitored
- [ ] Network usage monitored
- [ ] Container resource usage tracked

### Uptime Monitoring (运行时间监控)

- [ ] Uptime monitoring service configured (Pingdom, UptimeRobot, etc.)
- [ ] Alert notifications configured (email, SMS, Slack)
- [ ] Health check endpoints monitored
- [ ] SSL certificate expiration monitored

### Application Monitoring (应用监控)

- [ ] APM tool configured (optional: New Relic, Datadog)
- [ ] Error tracking configured (optional: Sentry)
- [ ] Performance metrics collected
- [ ] User analytics configured (optional)

## Post-Deployment (部署后)

### Documentation (文档)

- [ ] Deployment details documented
- [ ] Configuration changes documented
- [ ] Access credentials stored securely (password manager)
- [ ] Runbook created for common operations
- [ ] Disaster recovery plan documented

### Team Handoff (团队交接)

- [ ] Operations team trained
- [ ] Access credentials shared securely
- [ ] Monitoring dashboards shared
- [ ] Support contacts documented
- [ ] Escalation procedures defined

### Backup Verification (备份验证)

- [ ] First automated backup completed successfully
- [ ] Backup files verified
- [ ] Restore procedure tested (on test environment)
- [ ] Backup monitoring configured
- [ ] Backup alerts configured

### Maintenance Schedule (维护计划)

- [ ] Daily maintenance tasks scheduled
- [ ] Weekly maintenance tasks scheduled
- [ ] Monthly maintenance tasks scheduled
- [ ] Quarterly maintenance tasks scheduled
- [ ] Certificate renewal reminder set

## Rollback Plan (回滚计划)

### Rollback Preparation (回滚准备)

- [ ] Previous version tagged in Git
- [ ] Database backup taken before deployment
- [ ] MinIO backup taken before deployment
- [ ] Rollback procedure documented
- [ ] Rollback tested on staging environment

### Rollback Triggers (回滚触发条件)

- [ ] Critical bugs identified
- [ ] Performance degradation detected
- [ ] Security vulnerabilities discovered
- [ ] Data corruption detected
- [ ] Service unavailability exceeds threshold

## Sign-Off (签字确认)

### Deployment Team (部署团队)

- [ ] DevOps Engineer: _________________ Date: _______
- [ ] Backend Developer: _________________ Date: _______
- [ ] Frontend Developer: _________________ Date: _______
- [ ] QA Engineer: _________________ Date: _______

### Stakeholders (利益相关者)

- [ ] Project Manager: _________________ Date: _______
- [ ] Product Owner: _________________ Date: _______
- [ ] Security Officer: _________________ Date: _______
- [ ] Operations Manager: _________________ Date: _______

## Notes (备注)

```
Deployment Date: _______________
Deployment Time: _______________
Deployed By: _______________
Version/Commit: _______________

Issues Encountered:
_________________________________
_________________________________
_________________________________

Resolutions:
_________________________________
_________________________________
_________________________________

Additional Notes:
_________________________________
_________________________________
_________________________________
```

---

## Quick Reference Commands (快速参考命令)

```bash
# Start services
docker-compose -f docker-compose.production.yml up -d

# Stop services
docker-compose -f docker-compose.production.yml down

# View logs
docker-compose -f docker-compose.production.yml logs -f

# Restart service
docker-compose -f docker-compose.production.yml restart <service>

# Run database backup
docker-compose -f docker-compose.production.yml exec postgres_backup /backup.sh

# Check service status
docker-compose -f docker-compose.production.yml ps

# Execute command in container
docker-compose -f docker-compose.production.yml exec <service> <command>
```
