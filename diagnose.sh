#!/bin/bash
# Quick diagnostic script for Django backend issues

echo "=== Django Backend Diagnostic ==="
echo ""

echo "1. Checking containers status..."
docker compose ps
echo ""

echo "2. Checking Gunicorn/Django process..."
docker compose exec backend ps aux | grep -E "(gunicorn|runserver|python.*manage)" || echo "⚠️  No Django process found!"
echo ""

echo "3. Checking what's listening on port 8000..."
docker compose exec backend netstat -tuln | grep 8000 || docker compose exec backend ss -tuln | grep 8000 || echo "⚠️  Nothing listening on port 8000!"
echo ""

echo "4. Testing backend directly (from inside container)..."
docker compose exec backend curl -s http://localhost:8000/api/ | head -20 || echo "⚠️  Backend not responding!"
echo ""

echo "5. Testing nginx to backend connection..."
docker compose exec nginx wget -qO- http://backend:8000/api/ 2>&1 | head -20 || echo "⚠️  Nginx can't reach backend!"
echo ""

echo "6. Checking backend logs (last 30 lines)..."
echo "---"
docker compose logs --tail=30 backend
echo "---"
echo ""

echo "7. Checking nginx logs (last 20 lines)..."
echo "---"
docker compose logs --tail=20 nginx
echo "---"
echo ""

echo "8. Checking environment variables..."
docker compose exec backend env | grep -E "(DEBUG|DB_HOST|ALLOWED_HOSTS)" || echo "⚠️  Environment variables not found!"
echo ""

echo "9. Testing database connection..."
docker compose exec backend python -c "
import os
try:
    import psycopg
    conn = psycopg.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        port=os.environ.get('DB_PORT', '5432'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', ''),
        dbname=os.environ.get('DB_NAME', 'postgres')
    )
    print('✅ Database connection successful!')
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
" 2>&1
echo ""

echo "=== Diagnostic Complete ==="
echo ""
echo "Common fixes:"
echo "1. If DEBUG=1, set DEBUG=0 in .env to use Gunicorn"
echo "2. If database connection fails, check RDS credentials in .env"
echo "3. If Gunicorn not running, restart: docker compose restart backend"
echo "4. If nginx can't reach backend, check network: docker compose exec nginx ping backend"
