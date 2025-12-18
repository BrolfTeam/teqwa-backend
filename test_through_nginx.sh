#!/bin/bash
# Test through nginx (port 80) to verify proxy_set_header works

echo "=== Testing Through Nginx (Port 80) ==="
echo ""

echo "1. Clearing debug log..."
docker compose exec backend rm -f /tmp/debug.log
echo ""

echo "2. Testing through nginx port 80 (this uses proxy_set_header)..."
docker compose exec nginx wget -O- http://localhost:80/api/ 2>&1
echo ""

echo "3. Debug log (should show 56.228.17.128 as Host header):"
docker compose exec backend cat /tmp/debug.log 2>/dev/null | tail -2 | python3 -m json.tool 2>/dev/null || docker compose exec backend cat /tmp/debug.log | tail -2
echo ""

echo "4. Testing /api/v1/ endpoint (actual API root)..."
docker compose exec nginx wget -O- http://localhost:80/api/v1/ 2>&1 | head -30
echo ""

echo "5. Testing from outside (through public IP)..."
curl -v http://56.228.17.128/api/v1/ 2>&1 | head -30
echo ""

echo "=== Test Complete ==="
