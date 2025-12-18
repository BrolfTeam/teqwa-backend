#!/bin/bash
# Test script to verify the ALLOWED_HOSTS fix

echo "=== Testing ALLOWED_HOSTS Fix ==="
echo ""

echo "1. Pulling latest code..."
cd ~/teqwa-backend/teqwa-backend
git pull origin main
echo ""

echo "2. Rebuilding backend..."
docker compose build backend
echo ""

echo "3. Restarting services..."
docker compose restart backend
sleep 5
docker compose exec nginx nginx -s reload
sleep 2
echo ""

echo "4. Clearing debug log..."
docker compose exec backend rm -f /tmp/debug.log
echo ""

echo "5. Testing request..."
docker compose exec nginx wget -O- http://backend:8000/api/ 2>&1
echo ""

echo "6. Debug log contents:"
docker compose exec backend cat /tmp/debug.log 2>/dev/null | python3 -m json.tool 2>/dev/null || docker compose exec backend cat /tmp/debug.log
echo ""

echo "7. Backend logs (errors only):"
docker compose logs --tail=50 backend | grep -E "DisallowedHost|ERROR|400|200 OK|Listening"
echo ""

echo "8. Testing from outside..."
curl -v http://56.228.17.128/api/ 2>&1 | head -20
echo ""

echo "=== Test Complete ==="
