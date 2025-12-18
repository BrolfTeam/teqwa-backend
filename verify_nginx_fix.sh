#!/bin/bash
# Script to verify and fix nginx configuration

echo "=== Verifying Nginx Configuration ==="
echo ""

echo "1. Checking nginx config file on host..."
cat nginx/default.conf | grep -A 3 "location /api/"
echo ""

echo "2. Checking nginx config inside container..."
docker compose exec nginx cat /etc/nginx/conf.d/default.conf | grep -A 3 "location /api/"
echo ""

echo "3. Testing nginx config syntax..."
docker compose exec nginx nginx -t
echo ""

echo "4. If configs don't match, restarting nginx container..."
if ! docker compose exec nginx cat /etc/nginx/conf.d/default.conf | grep -q "proxy_set_header Host 56.228.17.128"; then
    echo "Config mismatch detected! Restarting nginx..."
    docker compose restart nginx
    sleep 3
else
    echo "Config looks correct. Reloading nginx..."
    docker compose exec nginx nginx -s reload
fi
echo ""

echo "5. Verifying config after reload..."
docker compose exec nginx cat /etc/nginx/conf.d/default.conf | grep -A 3 "location /api/"
echo ""

echo "=== Verification Complete ==="
