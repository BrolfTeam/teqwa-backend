# Server Setup Instructions

## Step 1: Create docker-compose.yml on Server

Run this command on your server to create the docker-compose.yml file:

```bash
cd ~/teqwa-backend

cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # 1. Django Backend
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: teqwa_backend
    restart: unless-stopped
    env_file: .env
    expose:
      - "8000"
    networks:
      - teqwa_network

  # 2. React Frontend (Build Stage)
  frontend:
    build:
      context: ../teqwa-frontend
      dockerfile: Dockerfile
    container_name: teqwa_frontend
    # This container just builds the files, Nginx will serve them.
    networks:
      - teqwa_network

  # 3. Nginx (The Entry Point)
  nginx:
    image: nginx:stable-alpine
    container_name: teqwa_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro # SSL certificates
      - ../teqwa-frontend/dist:/usr/share/nginx/html:ro # Points to React build
      - static_volume:/app/static
      - media_volume:/app/media
    depends_on:
      - backend
    networks:
      - teqwa_network

networks:
  teqwa_network:
    driver: bridge

volumes:
  static_volume:
  media_volume:
EOF
```

## Step 2: Verify File Created

```bash
ls -la docker-compose.yml
cat docker-compose.yml
```

## Step 3: Ensure Required Directories Exist

```bash
# Create nginx directory if it doesn't exist
mkdir -p nginx/ssl

# Verify nginx config exists
ls -la nginx/default.conf
```

## Step 4: Alternative - Copy from Local Machine

If you prefer to copy from your local machine:

**On your local machine:**
```bash
# Use scp to copy the file
scp docker-compose.yml ubuntu@your-server-ip:~/teqwa-backend/
```

**Or use rsync for entire directory:**
```bash
rsync -avz --exclude 'node_modules' --exclude '__pycache__' \
  teqwa-backend/ ubuntu@your-server-ip:~/teqwa-backend/
```

## Step 5: Verify All Required Files

```bash
cd ~/teqwa-backend

# Check required files
echo "=== Checking required files ==="
ls -la docker-compose.yml
ls -la Dockerfile
ls -la nginx/default.conf
ls -la .env  # This should exist with your configuration
```

## Step 6: Start Services

Once docker-compose.yml exists:

```bash
# Build and start
docker compose up -d --build

# Check status
docker compose ps

# View logs
docker compose logs -f
```
