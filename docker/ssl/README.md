# SSL Certificates Directory

This directory contains SSL/TLS certificates used by Nginx for HTTPS connections.

## Development

Generate self-signed certificates:
```bash
bash scripts/generate-ssl-certs.sh
```

This creates:
- `cert.pem` - SSL/TLS certificate
- `key.pem` - Private key

**Never commit these files to git** (security risk)

## Production

For production deployment, use:
1. **Let's Encrypt** (free, recommended)
2. **AWS Certificate Manager** (if on AWS)
3. **Commercial CA** (DigiCert, Comodo, etc.)

See `docs/SSL_CERTIFICATES.md` for detailed instructions.

## Security Notes

- `key.pem` must have permissions `600` (read/write owner only)
- Never share private key files
- Never commit private keys to version control
- Rotate certificates annually or as needed
