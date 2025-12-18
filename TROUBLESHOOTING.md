# Troubleshooting Guide

## Docker Compose "no configuration file provided" Error

### Issue
```
no configuration file provided: not found
```

### Solutions

#### 1. Verify File Exists
```bash
# Check if docker-compose.yml exists
ls -la docker-compose.yml

# Check current directory
pwd
# Should show: /home/ubuntu/teqwa-backend
```

#### 2. Use Correct Command Syntax

**Option A: Docker Compose V2 (newer, recommended)**
```bash
docker compose up -d --build
```

**Option B: Docker Compose V1 (older, uses hyphen)**
```bash
docker-compose up -d --build
```

**Check which version you have:**
```bash
# Check Docker Compose version
docker compose version
# OR
docker-compose --version
```

#### 3. Specify File Explicitly
```bash
# Explicitly specify the file
docker compose -f docker-compose.yml up -d --build

# OR with hyphen version
docker-compose -f docker-compose.yml up -d --build
```

#### 4. Verify You're in the Right Directory
```bash
# Navigate to the correct directory
cd ~/teqwa-backend

# Verify files exist
ls -la | grep -E "(docker-compose|Dockerfile|nginx)"

# Should show:
# - docker-compose.yml
# - Dockerfile
# - nginx/ (directory)
```

#### 5. Check File Permissions
```bash
# Ensure file is readable
chmod 644 docker-compose.yml

# Check file content
head -5 docker-compose.yml
```

## Common Issues and Fixes

### Issue: Port Already in Use
```bash
# Check what's using the port
sudo lsof -i :80
sudo lsof -i :443

# Stop conflicting services
sudo systemctl stop nginx
sudo systemctl stop apache2  # if applicable
```

### Issue: Frontend Build Not Found
```bash
# Build frontend first
cd ~/teqwa-frontend
npm install
npm run build

# Verify dist folder exists
ls -la dist/

# Then start docker compose
cd ~/teqwa-backend
docker compose up -d --build
```

### Issue: .env File Missing
```bash
# Check if .env exists
ls -la .env

# If missing, copy from example
cp .env.productionbackend.example .env

# Edit with your values
nano .env
```

### Issue: Permission Denied
```bash
# Add user to docker group (if not already)
sudo usermod -aG docker $USER

# Log out and back in, or:
newgrp docker

# Try again
docker compose up -d --build
```

### Issue: Docker Daemon Not Running
```bash
# Check Docker status
sudo systemctl status docker

# Start Docker if stopped
sudo systemctl start docker

# Enable Docker on boot
sudo systemctl enable docker
```

## Step-by-Step Deployment Checklist

1. **Verify Prerequisites**
   ```bash
   # Check Docker
   docker --version
   docker compose version  # or docker-compose --version
   
   # Check you're in right directory
   pwd  # Should be ~/teqwa-backend
   ```

2. **Stop System Nginx**
   ```bash
   sudo systemctl stop nginx
   sudo systemctl disable nginx
   ```

3. **Verify Port 80 is Free**
   ```bash
   sudo ss -tuln | grep :80
   # Should return nothing
   ```

4. **Build Frontend**
   ```bash
   cd ~/teqwa-frontend
   npm install
   npm run build
   ```

5. **Verify .env File**
   ```bash
   cd ~/teqwa-backend
   ls -la .env
   # If missing, create from example
   ```

6. **Start Docker Services**
   ```bash
   # Try with space (V2)
   docker compose up -d --build
   
   # OR try with hyphen (V1)
   docker-compose up -d --build
   
   # OR specify file explicitly
   docker compose -f docker-compose.yml up -d --build
   ```

7. **Check Status**
   ```bash
   docker compose ps
   # OR
   docker-compose ps
   ```

8. **View Logs if Issues**
   ```bash
   docker compose logs
   # OR
   docker-compose logs
   ```

## Quick Diagnostic Commands

```bash
# Full diagnostic
echo "=== Docker Version ==="
docker --version
docker compose version 2>/dev/null || docker-compose --version

echo "=== Current Directory ==="
pwd

echo "=== Required Files ==="
ls -la docker-compose.yml Dockerfile nginx/default.conf 2>/dev/null

echo "=== Port Status ==="
sudo ss -tuln | grep -E ':(80|443)'

echo "=== Docker Status ==="
sudo systemctl status docker

echo "=== Docker Group ==="
groups | grep docker
```
