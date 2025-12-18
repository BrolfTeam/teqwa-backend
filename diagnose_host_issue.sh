#!/bin/bash
# Comprehensive diagnostic script for ALLOWED_HOSTS issue

echo "=== Django ALLOWED_HOSTS Diagnostic ==="
echo ""

echo "1. Checking nginx configuration..."
echo "---"
docker compose exec nginx cat /etc/nginx/conf.d/default.conf | grep -A 5 "location /api/"
echo ""

echo "2. Testing nginx to backend connection..."
echo "---"
docker compose exec nginx wget -O- http://backend:8000/api/ 2>&1 | head -10
echo ""

echo "3. Checking backend ALLOWED_HOSTS from container..."
echo "---"
docker compose exec backend python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.conf import settings
print('ALLOWED_HOSTS:', settings.ALLOWED_HOSTS)
print('DEBUG:', settings.DEBUG)
"
echo ""

echo "4. Checking environment variables..."
echo "---"
docker compose exec backend env | grep -E "ALLOWED_HOSTS|DEBUG|DB_HOST"
echo ""

echo "5. Testing what Host header Django receives..."
echo "---"
docker compose exec backend cat /tmp/debug.log 2>/dev/null | tail -5 | python3 -m json.tool 2>/dev/null || echo "Debug log not found or empty"
echo ""

echo "6. Backend logs (last 20 lines)..."
echo "---"
docker compose logs --tail=20 backend | grep -E "DisallowedHost|ERROR|400|Listening|gunicorn"
echo ""

echo "7. Testing direct backend access (bypassing nginx)..."
echo "---"
docker compose exec backend python -c "
import requests
try:
    r = requests.get('http://localhost:8000/api/', headers={'Host': '56.228.17.128'})
    print(f'Status: {r.status_code}')
    print(f'Response: {r.text[:200]}')
except Exception as e:
    print(f'Error: {e}')
"
echo ""

echo "=== Diagnostic Complete ==="
echo ""
echo "If you see 'DisallowedHost' errors, check:"
echo "1. Nginx Host header is set to '56.228.17.128' (not 'backend:8000')"
echo "2. ALLOWED_HOSTS includes 'backend', 'backend:8000', and '56.228.17.128'"
echo "3. Environment variable ALLOWED_HOSTS is not overriding defaults"
