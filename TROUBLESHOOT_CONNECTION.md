# Troubleshooting: Connection Refused (ERR_CONNECTION_REFUSED)

## Issue
Browser shows "ERR_CONNECTION_REFUSED" when accessing `http://56.228.17.128`

## Common Causes

### 1. EC2 Security Group Not Allowing Port 80

**Check:**
```bash
# On EC2 instance, check if nginx is listening
sudo ss -tuln | grep :80
# Should show: tcp LISTEN 0 511 0.0.0.0:80
```

**Fix:**
1. Go to AWS EC2 Console
2. Select your instance
3. Click "Security" tab
4. Click on the Security Group
5. Click "Edit inbound rules"
6. Add rule:
   - Type: HTTP
   - Protocol: TCP
   - Port: 80
   - Source: 0.0.0.0/0 (or your IP for security)
   - Description: Allow HTTP traffic
7. Save rules

### 2. Docker Containers Not Running

**Check:**
```bash
docker compose ps
# Should show nginx and backend as "Up"
```

**Fix:**
```bash
docker compose up -d
docker compose ps
```

### 3. Nginx Container Not Listening on Port 80

**Check:**
```bash
# Check if nginx is running
docker compose logs nginx

# Check if port 80 is bound
docker compose exec nginx netstat -tuln | grep 80
# OR
sudo netstat -tuln | grep :80
```

**Fix:**
```bash
# Restart nginx
docker compose restart nginx

# Verify
docker compose ps nginx
```

### 4. Firewall Blocking Port 80

**Check:**
```bash
# Check UFW (Ubuntu Firewall)
sudo ufw status

# Check if port 80 is allowed
sudo ufw status | grep 80
```

**Fix:**
```bash
# Allow port 80
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Reload firewall
sudo ufw reload
```

### 5. Docker Port Mapping Issue

**Check docker-compose.yml:**
```yaml
nginx:
  ports:
    - "80:80"  # Must be present
```

**Verify:**
```bash
docker compose exec nginx cat /etc/nginx/conf.d/default.conf
docker compose ps
```

## Quick Diagnostic Commands

Run these on your EC2 instance:

```bash
# 1. Check containers are running
docker compose ps

# 2. Check nginx is listening
sudo ss -tuln | grep :80

# 3. Check firewall
sudo ufw status

# 4. Test from inside EC2
curl http://localhost
curl http://56.228.17.128

# 5. Check nginx logs
docker compose logs nginx | tail -20

# 6. Check if port is accessible from outside
# (Run this from your local machine, not EC2)
telnet 56.228.17.128 80
# OR
nc -zv 56.228.17.128 80
```

## Most Likely Issue: Security Group

**90% of connection refused errors are due to Security Group configuration.**

### Step-by-Step Security Group Fix:

1. **AWS Console → EC2 → Instances**
2. **Select your instance** (ip-172-31-29-7)
3. **Security tab** → Click on Security Group name
4. **Inbound rules** → **Edit inbound rules**
5. **Add rule:**
   - Type: `HTTP`
   - Protocol: `TCP`
   - Port range: `80`
   - Source: `0.0.0.0/0` (or specific IP for better security)
   - Description: `Allow HTTP traffic`
6. **Save rules**

### Verify After Fix:

```bash
# From your local machine
curl -v http://56.228.17.128/api/v1/

# Should return JSON response, not connection refused
```

## Testing Checklist

- [ ] Security Group allows port 80 from 0.0.0.0/0
- [ ] UFW firewall allows port 80 (if enabled)
- [ ] Docker containers are running (`docker compose ps`)
- [ ] Nginx is listening on port 80 (`sudo ss -tuln | grep :80`)
- [ ] Can access from EC2 itself (`curl http://localhost`)
- [ ] Nginx logs show no errors (`docker compose logs nginx`)
