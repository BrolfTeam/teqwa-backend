# Production Deployment Checklist

## ✅ Current Status
Your API is now live at `https://api.mujemaateqwa.org`

All services are running:
- ✅ Nginx (HTTPS proxy)
- ✅ Django Backend (internal only)
- ✅ PostgreSQL Database
- ✅ Certbot (auto-renewal)

## 🚀 Safely Leaving the Server

### 1. Verify Everything is Running
```bash
docker compose ps
```
All containers should show "Up" or "healthy" status.

### 2. Check Logs (Optional)
```bash
docker compose logs --tail=50
```
Look for any errors. If everything looks good, proceed.

### 3. Exit Safely
```bash
# Exit the SSH session
exit
```

Your containers will **continue running** in the background. Docker's `restart: unless-stopped` policy ensures they restart automatically if the server reboots.

## 🔧 Reconnecting When Issues Occur

### From Windows (WSL)

#### 1. Open WSL Terminal
```bash
# In PowerShell or Windows Terminal
wsl
```

#### 2. SSH to EC2
```bash
ssh -i ~/.ssh/your-key.pem ubuntu@56.228.17.128
```

#### 3. Navigate to Project
```bash
cd ~/teqwa-backend/teqwa-backend
```

## 🩺 Common Troubleshooting Commands

### Check Container Status
```bash
docker compose ps
```

### View Live Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f nginx
docker compose logs -f backend
```

### Restart a Service
```bash
# Restart Nginx
docker compose restart nginx

# Restart backend
docker compose restart backend

# Restart everything
docker compose restart
```

### Check SSL Certificate
```bash
sudo certbot certificates
```

### Renew SSL Manually
```bash
docker compose exec certbot certbot renew
docker compose restart nginx
```

### Apply Code Changes
```bash
git pull
docker compose up -d --build backend
```

### Database Issues
```bash
# Run migrations
docker compose exec backend python manage.py migrate

# Check database connection
docker compose exec backend python manage.py dbshell
```

### Full Reset (Nuclear Option)
```bash
docker compose down
docker compose up -d --build --force-recreate
```

## 📊 Monitoring

### Check if API is Accessible
```bash
curl https://api.mujemaateqwa.org/health/
```

### Check Disk Space
```bash
df -h
```

### Check Memory
```bash
free -h
```

## 🔐 Security Notes

1. **Backend Port**: Port 8000 is NOT exposed to the internet (internal only)
2. **Database Port**: Port 5432 is exposed - consider restricting in production
3. **SSL**: Auto-renews every 12 hours via Certbot
4. **Firewall**: Ensure AWS Security Group allows ports 80, 443

## 📁 Important Files

- `docker-compose.yml` - Service definitions
- `nginx/default.conf` - Nginx configuration
- `.env` - Environment variables (sensitive!)
- `fix_migrations.sh` - Database migration helper

## 🆘 Emergency Contacts

If you need to roll back changes:
```bash
git log --oneline -5  # See recent commits
git checkout <commit-hash>  # Revert to specific commit
docker compose up -d --build
```
