#!/bin/bash

# Let's Encrypt SSL Certificate Setup Script for api.mujemaateqwa.org
# Run this from the teqwa-backend/teqwa-backend directory

DOMAIN="api.mujemaateqwa.org"
EMAIL="admin@mujemaateqwa.org"
SSL_DIR="./nginx/ssl"

echo "🔒 Setting up Let's Encrypt SSL certificates for $DOMAIN"
echo ""

# Check if running from correct directory
if [ ! -d "nginx/ssl" ]; then
    echo "❌ Error: Please run this script from the teqwa-backend/teqwa-backend directory"
    exit 1
fi

# Check if domain is pointing to this server
echo "⚠️  IMPORTANT: Make sure $DOMAIN points to this server's IP (56.228.17.128)"
echo "   Add an A record in Cloudflare: api -> 56.228.17.128 (DNS only)"
echo ""
read -p "Press Enter to continue after DNS is configured..."

# Ensure nginx is running for webroot challenge
echo "📋 Starting nginx container for certificate validation..."
docker compose up -d nginx

# Wait a moment for nginx to start
sleep 3

# Get certificates using webroot method (nginx must be running)
echo "📥 Requesting certificates from Let's Encrypt..."
docker compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    --non-interactive \
    -d "$DOMAIN"

if [ $? -ne 0 ]; then
    echo "❌ Failed to obtain certificates"
    echo "   Make sure:"
    echo "   1. DNS A record for $DOMAIN points to 56.228.17.128"
    echo "   2. Port 80 is accessible from the internet"
    echo "   3. Firewall allows inbound traffic on port 80"
    exit 1
fi

# Copy certificates to expected location (from docker volume)
echo "📋 Copying certificates to expected location..."
docker compose run --rm certbot sh -c "
    cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /etc/nginx/ssl/cert.pem && \
    cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /etc/nginx/ssl/key.pem && \
    chmod 644 /etc/nginx/ssl/cert.pem && \
    chmod 600 /etc/nginx/ssl/key.pem
"

# Alternative: Copy from volume to local directory
CERT_VOLUME=$(docker volume inspect teqwa-backend_certbot_conf --format '{{ .Mountpoint }}' 2>/dev/null)
if [ -n "$CERT_VOLUME" ] && [ -d "$CERT_VOLUME/live/$DOMAIN" ]; then
    echo "📋 Copying certificates from volume to local directory..."
    sudo cp "$CERT_VOLUME/live/$DOMAIN/fullchain.pem" "$SSL_DIR/cert.pem"
    sudo cp "$CERT_VOLUME/live/$DOMAIN/privkey.pem" "$SSL_DIR/key.pem"
    sudo chmod 644 "$SSL_DIR/cert.pem"
    sudo chmod 600 "$SSL_DIR/key.pem"
    echo "✅ Certificates copied successfully!"
else
    echo "⚠️  Note: Certificates are in Docker volume. Nginx will read them directly."
    echo "   Volume location: certbot_conf:/etc/letsencrypt"
fi

echo ""
echo "🎉 SSL certificates are ready!"
echo "   Restarting nginx to load certificates..."
docker compose restart nginx

echo ""
echo "✅ Setup complete! Your API is now available at:"
echo "   https://$DOMAIN/api/v1/"
