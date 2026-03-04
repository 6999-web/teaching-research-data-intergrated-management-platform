# SSL/TLS Certificate Configuration
# SSL/TLS证书配置

## Overview (概述)

This directory contains SSL/TLS certificates for HTTPS configuration in production.

本目录包含生产环境HTTPS配置所需的SSL/TLS证书。

## Required Files (必需文件)

Place the following files in this directory:

请将以下文件放置在此目录中：

1. `teaching-office.crt` - SSL certificate (SSL证书)
2. `teaching-office.key` - Private key (私钥)
3. `teaching-office-ca.crt` - Certificate Authority bundle (可选，CA证书链)

## Generating Self-Signed Certificate for Testing (生成测试用自签名证书)

For testing purposes only, you can generate a self-signed certificate:

仅用于测试目的，您可以生成自签名证书：

```bash
# Generate private key
openssl genrsa -out teaching-office.key 2048

# Generate certificate signing request
openssl req -new -key teaching-office.key -out teaching-office.csr

# Generate self-signed certificate (valid for 365 days)
openssl x509 -req -days 365 -in teaching-office.csr -signkey teaching-office.key -out teaching-office.crt

# Clean up CSR
rm teaching-office.csr
```

## Production Certificate (生产环境证书)

For production, obtain a certificate from a trusted Certificate Authority (CA):

生产环境请从可信的证书颁发机构(CA)获取证书：

### Recommended Certificate Authorities:

- Let's Encrypt (Free, automated)
- DigiCert
- GlobalSign
- Sectigo

### Using Let's Encrypt with Certbot:

```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot

# Obtain certificate
sudo certbot certonly --standalone -d your-domain.com

# Certificates will be in /etc/letsencrypt/live/your-domain.com/
# Copy them to this directory:
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./teaching-office.crt
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./teaching-office.key
```

## File Permissions (文件权限)

Ensure proper permissions for security:

确保正确的文件权限以保证安全：

```bash
chmod 644 teaching-office.crt
chmod 600 teaching-office.key
```

## Certificate Renewal (证书更新)

SSL certificates expire and need renewal:

SSL证书会过期，需要定期更新：

- Let's Encrypt certificates expire every 90 days
- Set up automatic renewal with certbot:

```bash
# Test renewal
sudo certbot renew --dry-run

# Set up automatic renewal (cron job)
sudo crontab -e
# Add: 0 0 * * * certbot renew --quiet
```

## Verification (验证)

Verify your certificate:

验证您的证书：

```bash
# Check certificate details
openssl x509 -in teaching-office.crt -text -noout

# Verify certificate and key match
openssl x509 -noout -modulus -in teaching-office.crt | openssl md5
openssl rsa -noout -modulus -in teaching-office.key | openssl md5
# The MD5 hashes should match
```

## Security Notes (安全注意事项)

1. **Never commit private keys to version control** (永远不要将私钥提交到版本控制)
2. Keep private keys secure with proper permissions (使用适当的权限保护私钥)
3. Use strong encryption (minimum 2048-bit RSA) (使用强加密，最少2048位RSA)
4. Regularly update certificates before expiration (定期在过期前更新证书)
5. Monitor certificate expiration dates (监控证书过期日期)

## Troubleshooting (故障排除)

### Certificate not trusted:
- Ensure you have the complete certificate chain
- Include intermediate certificates

### Permission denied:
- Check file permissions (644 for .crt, 600 for .key)
- Ensure the user running the application has read access

### Certificate expired:
- Renew the certificate
- Update the files in this directory
- Restart the services
