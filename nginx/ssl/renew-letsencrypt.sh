#!/bin/bash

# Let's Encrypt SSL Certificate Renewal Script
# Run this from the teqwa-backend directory

DOMAIN="mujemaateqwa.org"
SSL_DIR="./nginx/ssl"

echo "🔄 Renewing Let's Encrypt SSL certificates for $DOMAIN"
echo ""

# Check if running from correct directory
if [ ! -d "nginx/ssl" ]; then
    echo "❌ Error: Please run this script from the teqwa-backend directory"
    exit 1
fi

# Renew certificates
echo "📥 Renewing certificates..."
docker run --rm \
    -v "$(pwd)/nginx/ssl:/etc/letsencrypt" \
    -p 80:80 \
    certbot/certbot renew

if [ $? -ne 0 ]; then
    echo "❌ Failed to renew certificates"
    exit 1
fi

# Copy renewed certificates to expected location
echo "📋 Copying renewed certificates..."
CERT_SOURCE="$SSL_DIR/live/$DOMAIN"
if [ -d "$CERT_SOURCE" ]; then
    cp "$CERT_SOURCE/fullchain.pem" "$SSL_DIR/cert.pem"
    cp "$CERT_SOURCE/privkey.pem" "$SSL_DIR/key.pem"
    
    # Set proper permissions
    chmod 644 "$SSL_DIR/cert.pem"
    chmod 600 "$SSL_DIR/key.pem"
    
    echo "✅ Certificates renewed and copied successfully!"
    
    # Reload nginx if running
    if docker ps | grep -q teqwa_nginx; then
        echo "🔄 Reloading Nginx..."
        docker exec teqwa_nginx nginx -s reload
        echo "✅ Nginx reloaded with new certificates"
    fi
else
    echo "❌ Certificate directory not found: $CERT_SOURCE"
    exit 1
fi

echo ""
echo "🎉 Certificate renewal complete!"
