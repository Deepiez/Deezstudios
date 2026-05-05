#!/bin/bash
# ===========================================
# SSL Certificate Setup (Let's Encrypt)
# Run once on VPS to setup HTTPS
# ===========================================

set -e

DOMAIN=${1:-""}

if [ -z "$DOMAIN" ]; then
    echo "Usage: ./setup-ssl.sh your-domain.com"
    exit 1
fi

echo "=== Setting up SSL for: $DOMAIN ==="

# Install certbot if not present
if ! command -v certbot &> /dev/null; then
    echo "Installing certbot..."
    apt-get update
    apt-get install -y certbot
fi

# Stop nginx temporarily
docker compose -f docker-compose.prod.yml stop nginx 2>/dev/null || true

# Get certificate
certbot certonly --standalone \
    -d "$DOMAIN" \
    --non-interactive \
    --agree-tos \
    --email "admin@$DOMAIN" \
    --preferred-challenges http

# Copy certs to nginx ssl directory
SSL_DIR="$(dirname "$0")/../docker/nginx/ssl"
mkdir -p "$SSL_DIR"
cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$SSL_DIR/fullchain.pem"
cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$SSL_DIR/privkey.pem"

echo ""
echo "SSL certificates installed!"
echo ""
echo "Next steps:"
echo "1. Edit docker/nginx/nginx.conf - uncomment the HTTPS server block"
echo "2. Update server_name to: $DOMAIN"
echo "3. Restart: docker compose -f docker-compose.prod.yml restart nginx"
echo ""
echo "Auto-renewal cron (add to crontab):"
echo "0 3 * * 1 certbot renew --quiet && cp /etc/letsencrypt/live/$DOMAIN/*.pem $(realpath $SSL_DIR)/ && docker compose -f $(realpath $(dirname $0)/../docker-compose.prod.yml) restart nginx"
