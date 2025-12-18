# Production Deployment Guide

## Prerequisites

- Ubuntu server with Docker and Docker Compose installed
- Domain name pointing to your server IP
- SSL certificates (Let's Encrypt recommended)

## Port Conflicts Resolution

### Issue: System Nginx vs Docker Nginx

If you have system-level nginx installed (as shown by `systemctl status nginx`), it will conflict with the Docker nginx container on port 80.

### Solution: Stop System Nginx (Recommended for Docker Setup)

Since we're using Docker Compose with nginx, we should stop and disable the system nginx:

```bash
# Stop system nginx
sudo systemctl stop nginx

# Disable system nginx from starting on boot
sudo systemctl disable nginx

# Verify it's stopped
sudo systemctl status nginx

# Verify port 80 is free
sudo ss -tuln | grep :80
```

**Note:** If you need to keep system nginx for other purposes, you can:
1. Change Docker nginx to use a different port (e.g., 8080)
2. Configure system nginx as a reverse proxy to Docker containers

### Alternative: Use System Nginx as Reverse Proxy

If you prefer to use system nginx instead of Docker nginx:

1. **Stop Docker nginx** (remove from docker-compose.yml or don't start it)
2. **Configure system nginx** to proxy to Docker containers
3. **Update system nginx config** at `/etc/nginx/sites-available/default` or create a new site config

## Deployment Steps

### 1. Prepare Environment

```bash
# Navigate to project directory
cd ~/teqwa-backend

# Ensure .env file exists with all required variables
# See .env.productionbackend.example for reference
```

### 2. Stop System Nginx (if running)

```bash
sudo systemctl stop nginx
sudo systemctl disable nginx
```

### 3. Build Frontend

The frontend needs to be built before starting services:

```bash
# Build frontend (from teqwa-frontend directory or adjust path)
cd ~/teqwa-frontend
npm install
npm run build
```

### 4. Start Docker Services

```bash
cd ~/teqwa-backend

# Start all services
docker compose up -d --build

# Check status
docker compose ps

# View logs
docker compose logs -f
```

### 5. Run Django Migrations

```bash
# Run migrations
docker compose exec backend python manage.py migrate

# Collect static files
docker compose exec backend python manage.py collectstatic --noinput
```

### 6. Setup SSL Certificates

```bash
# Make sure port 80 is available (Docker nginx should be stopped temporarily)
docker compose stop nginx

# Run Let's Encrypt setup
cd ~/teqwa-backend
./nginx/ssl/setup-letsencrypt.sh

# Restart nginx
docker compose start nginx
```

### 7. Verify Deployment

```bash
# Check all containers are running
docker compose ps

# Test HTTP (should redirect to HTTPS)
curl -I http://mujemaateqwa.org

# Test HTTPS
curl -I https://mujemaateqwa.org

# Check nginx logs
docker compose logs nginx

# Check backend logs
docker compose logs backend
```

## Troubleshooting

### Port 80 Already in Use

```bash
# Find what's using port 80
sudo lsof -i :80
sudo ss -tuln | grep :80

# Stop system nginx if it's running
sudo systemctl stop nginx
```

### Docker Containers Not Starting

```bash
# Check logs
docker compose logs

# Check if ports are available
sudo netstat -tulpn | grep -E ':(80|443|8000)'

# Restart Docker daemon if needed
sudo systemctl restart docker
```

### SSL Certificate Issues

```bash
# Test nginx configuration
docker compose exec nginx nginx -t

# Check certificate files exist
ls -la nginx/ssl/

# Verify certificate permissions
ls -la nginx/ssl/*.pem
```

### Frontend Not Loading

```bash
# Verify frontend build exists
ls -la ../teqwa-frontend/dist/

# Rebuild frontend if needed
cd ../teqwa-frontend
npm run build

# Restart nginx
cd ../teqwa-backend
docker compose restart nginx
```

## Maintenance

### Update Application

```bash
cd ~/teqwa-backend

# Pull latest code
git pull

# Rebuild and restart
docker compose up -d --build

# Run migrations
docker compose exec backend python manage.py migrate

# Collect static files
docker compose exec backend python manage.py collectstatic --noinput
```

### Renew SSL Certificates

```bash
cd ~/teqwa-backend

# Stop nginx temporarily
docker compose stop nginx

# Renew certificates
./nginx/ssl/renew-letsencrypt.sh

# Start nginx
docker compose start nginx
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f nginx
docker compose logs -f backend
docker compose logs -f frontend
```

### Restart Services

```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart nginx
docker compose restart backend
```

## Security Checklist

- [ ] System nginx stopped and disabled
- [ ] SSL certificates installed and working
- [ ] HTTPS redirect configured
- [ ] Environment variables secured (.env not in git)
- [ ] Database credentials secure (RDS)
- [ ] Firewall configured (only ports 80, 443 open)
- [ ] Regular backups configured
- [ ] SSL certificate auto-renewal set up

## Monitoring

### Health Checks

```bash
# Check container health
docker compose ps

# Test endpoints
curl https://mujemaateqwa.org
curl https://mujemaateqwa.org/api/
```

### Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df
```
