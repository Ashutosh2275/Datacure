#!/bin/bash
#
# Generate self-signed SSL certificates for DataCure
# For development/testing use only. For production, use Let's Encrypt or commercial CA.
#
# Usage:
#   bash scripts/generate-ssl-certs.sh
#
# This will create:
#   - docker/ssl/cert.pem (certificate)
#   - docker/ssl/key.pem (private key)
#

set -e

CERT_DIR="docker/ssl"
CERT_PEM="$CERT_DIR/cert.pem"
KEY_PEM="$CERT_DIR/key.pem"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}DataCure SSL Certificate Generation${NC}"
echo "==============================================="

# Create ssl directory if it doesn't exist
mkdir -p "$CERT_DIR"

# Check if certificates already exist
if [ -f "$CERT_PEM" ] && [ -f "$KEY_PEM" ]; then
    echo -e "${YELLOW}SSL certificates already exist.${NC}"
    read -p "Regenerate certificates? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping certificate generation."
        exit 0
    fi
fi

echo "Generating self-signed SSL certificate..."
echo "Certificate validity: 365 days"
echo "Key size: 4096 bits (RSA)"
echo ""

# Generate self-signed certificate
openssl req -x509 \
    -newkey rsa:4096 \
    -nodes \
    -out "$CERT_PEM" \
    -keyout "$KEY_PEM" \
    -days 365 \
    -subj "/C=IN/ST=Karnataka/L=Bangalore/O=DataCure/CN=localhost/emailAddress=admin@datacure.local"

# Set proper permissions
chmod 600 "$KEY_PEM"
chmod 644 "$CERT_PEM"

echo -e "${GREEN}✓ SSL certificates generated successfully!${NC}"
echo ""
echo "Certificate details:"
openssl x509 -in "$CERT_PEM" -noout -text | grep -A 1 "Issuer\|Subject\|Not Before\|Not After"
echo ""
echo "Files created:"
echo "  - $CERT_PEM"
echo "  - $KEY_PEM"
echo ""
echo -e "${YELLOW}Note:${NC}"
echo "  - This is a self-signed certificate suitable for development only"
echo "  - For production, use Let's Encrypt or a trusted Certificate Authority"
echo "  - Certificate expires in 365 days"
echo "  - To regenerate, delete these files and rerun this script"
echo ""
echo "For Let's Encrypt setup, see: docs/DEPLOYMENT.md"
