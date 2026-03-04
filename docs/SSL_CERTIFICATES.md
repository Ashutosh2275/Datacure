# SSL/TLS Configuration for DataCure

## Overview

DataCure uses SSL/TLS for secure HTTPS communication. This document covers development and production configurations.

## Development Setup (Self-Signed Certificates)

### Quick Start

```bash
# Generate self-signed SSL certificates
bash scripts/generate-ssl-certs.sh

# This creates:
#   - docker/ssl/cert.pem
#   - docker/ssl/key.pem
```

The script generates:
- **Self-signed X.509 certificate** (365 days validity)
- **4096-bit RSA private key**
- Valid for: localhost, 127.0.0.1
- Issued to: DataCure (local development)

### Certificate Details

```bash
# View certificate details
openssl x509 -in docker/ssl/cert.pem -noout -text

# Verify certificate and key match
openssl x509 -noout -modulus -in docker/ssl/cert.pem | openssl md5
openssl rsa -noout -modulus -in docker/ssl/key.pem | openssl md5
# Both hashes should match
```

### Docker Usage

Certificates are automatically mounted by docker-compose.yml:

```yaml
volumes:
  - ./docker/ssl:/etc/nginx/ssl:ro
```

Nginx configuration uses them:

```nginx
ssl_certificate /etc/nginx/ssl/cert.pem;
ssl_certificate_key /etc/nginx/ssl/key.pem;
```

### Browser Warnings

When accessing via `https://localhost`:
- Modern browsers will show certificate warnings (expected for self-signed)
- Click "Advanced" → "Proceed to localhost (unsafe)" to continue
- Warnings are **safe** - you're using HTTPS, just unverified certificate

### Regenerating Certificates

```bash
# Delete old certificates
rm -rf docker/ssl/*

# Generate new ones
bash scripts/generate-ssl-certs.sh
```

## Production Setup (Let's Encrypt)

### Prerequisites

- Valid domain name (not localhost)
- Email address for Let's Encrypt
- Ports 80 and 443 must be publicly accessible
- AWS ACM or similar (alternative approach)

### Option 1: Let's Encrypt via Certbot (Recommended)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --standalone \
  -d yourdomain.com \
  -d www.yourdomain.com \
  --email your-email@example.com \
  --agree-tos \
  --non-interactive

# Certificate location: /etc/letsencrypt/live/yourdomain.com/
```

Update docker-compose for production:

```yaml
volumes:
  # Use Let's Encrypt certificates
  - /etc/letsencrypt/live/yourdomain.com/fullchain.pem:/etc/nginx/ssl/cert.pem:ro
  - /etc/letsencrypt/live/yourdomain.com/privkey.pem:/etc/nginx/ssl/key.pem:ro
```

### Option 2: AWS Certificate Manager (ACM)

If running on AWS:

```bash
# Create certificate in ACM via AWS Console or CLI
aws acm request-certificate \
  --domain-name yourdomain.com \
  --subject-alternative-names www.yourdomain.com \
  --region us-east-1

# Use ALB/NLB to handle SSL termination
# Nginx doesn't need local certificates in this case
```

### Option 3: Commercial Certificate Authority

Purchase certificate from:
- DigiCert
- Comodo
- GlobalSign
- Let's Encrypt (free alternative)

How to install:

```bash
# Copy certificate and key to docker/ssl/
cp your-certificate.crt docker/ssl/cert.pem
cp your-private-key.key docker/ssl/key.pem

# Set permissions
chmod 600 docker/ssl/key.pem
chmod 644 docker/ssl/cert.pem
```

## Nginx Configuration

Current configuration in `docker/nginx.conf`:

```nginx
server {
    listen 443 ssl http2;
    server_name localhost;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}

server {
    listen 80;
    server_name _;

    # Redirect HTTP to HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}
```

### Security Headers Explained

- **HSTS** (Strict-Transport-Security): Force HTTPS for 1 year
- **X-Frame-Options**: Prevent clickjacking attacks
- **X-Content-Type-Options**: Prevent MIME-type sniffing
- **X-XSS-Protection**: Enable browser XSS protection
- **Referrer-Policy**: Control referrer information

## Certificate Renewal

### Let's EncryptAuto-renewal (Recommended):

```bash
# Certbot automatically renews 30 days before expiry
# Verify auto-renewal works:
sudo certbot renew --dry-run

# Check renewal timer (systemd):
sudo systemctl status certbot.timer
```

Manual renewal:

```bash
sudo certbot renew
```

### Self-Signed Certificate Renewal

Self-signed certificates expire after 365 days. To renew:

```bash
bash scripts/generate-ssl-certs.sh
# Then restart Docker containers
docker-compose restart nginx
```

## Testing SSL Configuration

### Using curl

```bash
# Test self-signed certificate (ignore verification)
curl -k https://localhost/health

# With verbose output
curl -kv https://localhost/health

# Check certificate details
# Expect warning about self-signed cert - that's normal
```

### Using OpenSSL

```bash
# Test connection and certificate
openssl s_client -connect localhost:443

# View certificate info
openssl s_client -connect localhost:443 -showcerts

# Test specific TLS version
openssl s_client -connect localhost:443 -tls1_2
openssl s_client -connect localhost:443 -tls1_3
```

### Using SSL Labs (for production domains)

Visit: https://www.ssllabs.com/ssltest/

Enter your production domain for comprehensive SSL/TLS analysis.

## Common Issues & Solutions

### Issue: "Connection refused" on HTTPS

**Cause**: Nginx not running or SSL not configured
**Solution**:
```bash
docker-compose logs nginx
docker-compose restart nginx
```

### Issue: "SSL: CERTIFICATE_VERIFY_FAILED"

**Cause**: Self-signed certificate (development) or expired certificate (production)
**Solution**:
- Development: Use `curl -k` or `-k` flag to ignore verification
- Production: Check certificate expiry: `openssl x509 -in cert.pem -noout -dates`

### Issue: "SSL: WRONG_VERSION_NUMBER"

**Cause**: HTTP client connecting to HTTPS server, or protocol mismatch
**Solution**: Ensure you're using `https://` not `http://`

### Issue: "certificate does not match hostname"

**Cause**: Certificate CN doesn't match domain name
**Solution**: Regenerate certificate with correct domain, or use wildcard certificate

## Security Best Practices

1. **Always use HTTPS in production** - No exceptions
2. **Keep certificates updated** - Auto-renew via certbot or monitoring
3. **Use strong ciphers** - Configure TLS 1.2+ only (no SSL 3.0, TLS 1.0, 1.1)
4. **Enable HSTS** - Force browsers to use HTTPS
5. **Monitor certificate expiry** - Setup alerts 30 days before expiry
6. **Separate keys from certificates** - Store keys securely with proper permissions
7. **Never commit private keys** - Add `/docker/ssl/key.pem` to .gitignore

## References

- Let's Encrypt: https://letsencrypt.org/
- Certbot Documentation: https://certbot.eff.org/
- Mozilla SSL Configuration Generator: https://ssl-config.mozilla.org/
- OWASP TLS Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Protection_Cheat_Sheet.html
