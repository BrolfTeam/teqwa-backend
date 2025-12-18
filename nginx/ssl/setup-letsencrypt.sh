#!/bin/bash

# Let's Encrypt SSL Certificate Setup Script
# Run this from the teqwa-backend directory

DOMAIN="mujemaateqwa.org"
SSL_DIR="./nginx/ssl"
LETSENCRYPT_DIR="$SSL_DIR"

echo "🔒 Setting up Let's Encrypt SSL certificates for $DOMAIN"
echo ""

# Check if running from correct directory
if [ ! -d "nginx/ssl" ]; then
    echo "❌ Error: Please run this script from the teqwa-backend directory"
    exit 1
fi

# Stop any services using port 80
echo "⚠️  Make sure port 80 is available (stop nginx if running)"
echo "   Run: docker compose down (if services are running)"
echo ""
read -p "Press Enter to continue..."

# Get certificates
echo "📥 Requesting certificates from Let's Encrypt..."
docker run -it --rm \
    -v "$(pwd)/nginx/ssl:/etc/letsencrypt" \
    -p 80:80 \
    certbot/certbot certonly --standalone \
    -d "$DOMAIN" \
    -d "www.$DOMAIN" \
    --email admin@$DOMAIN \
    --agree-tos \
    --non-interactive

if [ $? -ne 0 ]; then
    echo "❌ Failed to obtain certificates"
    exit 1
fi

# Copy certificates to expected location
echo "📋 Copying certificates to expected location..."
CERT_SOURCE="$SSL_DIR/live/$DOMAIN"
if [ -d "$CERT_SOURCE" ]; then
    cp "$CERT_SOURCE/fullchain.pem" "$SSL_DIR/cert.pem"
    cp "$CERT_SOURCE/privkey.pem" "$SSL_DIR/key.pem"
    
    # Set proper permissions
    chmod 644 "$SSL_DIR/cert.pem"
    chmod 600 "$SSL_DIR/key.pem"
    
    echo "✅ Certificates copied successfully!"
    echo "   - Certificate: $SSL_DIR/cert.pem"
    echo "   - Private Key: $SSL_DIR/key.pem"
else
    echo "❌ Certificate directory not found: $CERT_SOURCE"
    exit 1
fi

echo ""
echo "🎉 SSL certificates are ready!"
echo "   You can now start your services with: docker compose up -d"
