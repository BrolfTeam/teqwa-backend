#!/bin/bash
# Verify security group configuration and connectivity

echo "=== Security Group and Connectivity Verification ==="
echo ""

echo "1. Checking which security group is attached to this instance..."
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
echo "Instance ID: $INSTANCE_ID"
echo ""

echo "2. Getting instance metadata..."
echo "Public IP: $(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo "Private IP: $(curl -s http://169.254.169.254/latest/meta-data/local-ipv4)"
echo ""

echo "3. Checking if port 80 is accessible from outside..."
echo "Testing with curl from external service..."
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" --max-time 5 http://56.228.17.128/api/v1/ || echo "Connection failed"
echo ""

echo "4. Checking nginx status..."
docker compose ps nginx
echo ""

echo "5. Testing local connectivity..."
curl -s http://localhost/api/v1/ | head -c 100
echo "..."
echo ""

echo "6. Checking port binding..."
sudo ss -tuln | grep :80
echo ""

echo "=== Verification Complete ==="
echo ""
echo "If connection still fails from outside:"
echo "1. Verify the security group shown in AWS Console is attached to instance $INSTANCE_ID"
echo "2. Check if instance has a public IP assigned"
echo "3. Verify route table allows internet gateway access"
echo "4. Wait 30-60 seconds after security group changes"
