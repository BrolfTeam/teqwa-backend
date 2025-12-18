# Troubleshooting: Django Not Responding Behind Nginx

## Quick Diagnostic Commands

Run these on your EC2 instance to diagnose the issue:

### 1. Check if Backend Container is Running
```bash
docker compose ps
```

### 2. Check Gunicorn Process Inside Backend Container
```bash
docker compose exec backend ps aux
```

**Expected output:** You should see a `gunicorn` process listening on `0.0.0.0:8000`

**If you see `127.0.0.1:8000` instead:** Gunicorn is not accessible from Nginx container.

### 3. Check Backend Logs
```bash
docker compose logs backend
```

Look for:
- Database connection errors
- Gunicorn startup messages
- Any error messages

### 4. Test Backend Directly (Bypass Nginx)
```bash
# Test if backend responds directly
docker compose exec backend curl http://localhost:8000/api/

# Or from host
curl http://localhost:8000/api/
```

### 5. Test Nginx to Backend Connection
```bash
# From inside nginx container
docker compose exec nginx wget -O- http://backend:8000/api/

# Or test DNS resolution
docker compose exec nginx ping backend
```

### 6. Check Nginx Configuration
```bash
# Test nginx config syntax
docker compose exec nginx nginx -t

# Reload nginx after any config changes
docker compose exec nginx nginx -s reload
```

## Common Issues and Fixes

### Issue 1: Gunicorn Not Binding to 0.0.0.0

**Symptom:** `ps aux` shows Gunicorn on `127.0.0.1:8000`

**Fix:** The `gunicorn_config.py` should have:
```python
bind = "0.0.0.0:8000"
```

**Verify:**
```bash
docker compose exec backend cat gunicorn_config.py | grep bind
```

### Issue 2: DEBUG Mode Using Development Server

**Symptom:** Backend is using `runserver` instead of Gunicorn

**Check:**
```bash
docker compose exec backend ps aux | grep -E "(runserver|gunicorn)"
```

**Fix:** Ensure `.env` has:
```env
DEBUG=0
# or
DEBUG=False
```

### Issue 3: Database Connection Failing

**Symptom:** Backend container keeps restarting or logs show DB errors

**Check:**
```bash
docker compose logs backend | grep -i "database\|db\|connection"
```

**Fix:** Verify `.env` has correct RDS credentials:
```env
DB_HOST=your-rds-endpoint.aws.com
DB_PORT=5432
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
```

**Test connection:**
```bash
docker compose exec backend python -c "
import os
import psycopg
conn = psycopg.connect(
    host=os.environ.get('DB_HOST'),
    port=os.environ.get('DB_PORT', '5432'),
    user=os.environ.get('DB_USER'),
    password=os.environ.get('DB_PASSWORD'),
    dbname=os.environ.get('DB_NAME')
)
print('Database connection successful!')
conn.close()
"
```

### Issue 4: ALLOWED_HOSTS Not Set Correctly

**Symptom:** Django returns 400 Bad Request

**Check:**
```bash
docker compose logs backend | grep -i "allowed_hosts\|disallowedhost"
```

**Fix:** Ensure `.env` includes:
```env
ALLOWED_HOSTS=56.228.17.128,localhost,127.0.0.1
```

### Issue 5: Nginx Can't Reach Backend Container

**Symptom:** Nginx logs show "upstream connection refused"

**Check:**
```bash
docker compose logs nginx | grep -i "upstream\|backend\|connection"
```

**Fix:** 
1. Ensure both containers are on same network:
   ```bash
   docker compose exec backend hostname
   docker compose exec nginx ping backend
   ```

2. Restart both containers:
   ```bash
   docker compose restart backend nginx
   ```

### Issue 6: Port Binding Issues

**Symptom:** Container can't bind to port 8000

**Check:**
```bash
docker compose exec backend netstat -tuln | grep 8000
```

**Fix:** Ensure no other process is using port 8000:
```bash
sudo lsof -i :8000
```

## Step-by-Step Recovery

If Django isn't responding, follow these steps:

### Step 1: Stop All Containers
```bash
docker compose down
```

### Step 2: Verify Configuration Files
```bash
# Check .env exists and has required variables
cat .env | grep -E "(DEBUG|DB_HOST|ALLOWED_HOSTS|FRONTEND_URL)"

# Check gunicorn config
cat gunicorn_config.py | grep bind
```

### Step 3: Rebuild Containers
```bash
docker compose build --no-cache backend
```

### Step 4: Start Containers
```bash
docker compose up -d
```

### Step 5: Check Logs
```bash
# Watch logs in real-time
docker compose logs -f backend nginx
```

### Step 6: Verify Gunicorn is Running
```bash
docker compose exec backend ps aux | grep gunicorn
```

### Step 7: Test Connection
```bash
# From host
curl http://56.228.17.128/api/

# From inside nginx container
docker compose exec nginx wget -O- http://backend:8000/api/
```

## Quick Fix Script

Run this script to diagnose and fix common issues:

```bash
#!/bin/bash
echo "=== Django Backend Diagnostic ==="

echo "1. Checking containers..."
docker compose ps

echo "2. Checking Gunicorn process..."
docker compose exec backend ps aux | grep -E "(gunicorn|runserver)" || echo "No process found!"

echo "3. Checking backend logs (last 20 lines)..."
docker compose logs --tail=20 backend

echo "4. Testing backend directly..."
docker compose exec backend curl -s http://localhost:8000/api/ || echo "Backend not responding!"

echo "5. Testing nginx to backend..."
docker compose exec nginx wget -qO- http://backend:8000/api/ || echo "Nginx can't reach backend!"

echo "6. Checking network connectivity..."
docker compose exec nginx ping -c 1 backend || echo "Network issue!"

echo "=== Diagnostic Complete ==="
```

## Expected Working State

When everything is working correctly:

1. **Containers:** Both `backend` and `nginx` show as "Up" in `docker compose ps`
2. **Gunicorn:** `ps aux` shows: `gunicorn: master [gunicorn]` and worker processes
3. **Binding:** Gunicorn listens on `0.0.0.0:8000` (visible in `netstat` or `ss`)
4. **Logs:** Backend logs show "Booting worker" messages
5. **API:** `curl http://56.228.17.128/api/` returns JSON response
6. **Nginx:** Nginx logs show successful proxy requests (200 status codes)
