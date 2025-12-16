# Teqwa Backend - Production Deployment Guide

This guide covers deploying the Teqwa backend API to production.

## Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Domain name (optional but recommended)
- SSL certificate (Let's Encrypt recommended)

## Environment Configuration

Create a `.env` file with the following variables:

```env
# Django Settings
DEBUG=0
SECRET_KEY=your-super-secret-key-change-this-in-production
ALLOWED_HOSTS=api.yourdomain.com,yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname
# OR use individual settings:
DB_NAME=teqwa_db
DB_USER=teqwa_user
DB_PASSWORD=your-secure-password
DB_HOST=localhost
DB_PORT=5432

# Frontend URL (for CORS and email links)
FRONTEND_URL=https://yourdomain.com

# CORS (comma-separated list)
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# AWS S3 Configuration (for production media files)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=teqwa-media-bucket
AWS_S3_REGION_NAME=us-east-1

# Payment Gateway (Chapa)
CHAPA_SECRET_KEY=your-chapa-secret-key
WEBHOOK_URL=https://api.yourdomain.com
```

## Deployment Options

### Option 1: Docker Deployment

#### Using Docker Compose

```bash
docker compose up -d
```

#### Using Docker Directly

```bash
docker build -t teqwa-backend .
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  teqwa-backend
```

### Option 2: Traditional Server (Ubuntu/Debian)

#### 1. Install Dependencies

```bash
sudo apt update
sudo apt install python3.11 python3-pip python3-venv postgresql nginx
```

#### 2. Set Up PostgreSQL

```bash
sudo -u postgres psql
CREATE DATABASE teqwa_db;
CREATE USER teqwa_user WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE teqwa_db TO teqwa_user;
\q
```

#### 3. Clone and Set Up Repository

```bash
git clone <repository-url>
cd teqwa-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 4. Configure Environment

```bash
cp .env.example .env
nano .env  # Edit with your settings
```

#### 5. Run Migrations

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

#### 6. Set Up Gunicorn Service

Create `/etc/systemd/system/teqwa-backend.service`:

```ini
[Unit]
Description=Teqwa Backend Gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/teqwa-backend
Environment="PATH=/path/to/teqwa-backend/venv/bin"
ExecStart=/path/to/teqwa-backend/venv/bin/gunicorn config.wsgi:application --bind unix:/path/to/teqwa-backend/teqwa.sock --config gunicorn_config.py

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable teqwa-backend
sudo systemctl start teqwa-backend
```

#### 7. Configure Nginx

Create `/etc/nginx/sites-available/teqwa-backend`:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/path/to/teqwa-backend/teqwa.sock;
    }

    location /static/ {
        alias /path/to/teqwa-backend/staticfiles/;
    }

    location /media/ {
        alias /path/to/teqwa-backend/media/;
    }
}
```

Enable and test:

```bash
sudo ln -s /etc/nginx/sites-available/teqwa-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 8. Set Up SSL

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```

### Option 3: Platform-as-a-Service (PaaS)

#### DigitalOcean App Platform

1. Connect repository
2. Set build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
3. Set run command: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --config gunicorn_config.py`
4. Add PostgreSQL database component
5. Configure environment variables

#### AWS Elastic Beanstalk

1. Install EB CLI
2. Initialize: `eb init`
3. Create environment: `eb create teqwa-backend-prod`
4. Set environment variables
5. Deploy: `eb deploy`

## Security Checklist

- [ ] Set `DEBUG=False`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Use secure database passwords
- [ ] Set up email service
- [ ] Configure AWS S3 for media (if using)
- [ ] Set up database backups
- [ ] Configure firewall rules
- [ ] Enable rate limiting
- [ ] Set up monitoring and logging

## Monitoring and Maintenance

### View Logs

```bash
# Gunicorn logs
sudo journalctl -u teqwa-backend -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Database Backups

```bash
# Create backup
pg_dump -U teqwa_user teqwa_db > backup_$(date +%Y%m%d).sql

# Restore backup
psql -U teqwa_user teqwa_db < backup_20231216.sql
```

### Updates

```bash
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart teqwa-backend
```

## API Documentation

Access API documentation at:
- Swagger UI: `https://api.yourdomain.com/api/docs/`
- OpenAPI Schema: `https://api.yourdomain.com/api/schema/`

## Troubleshooting

### Database Connection Issues

```bash
python manage.py dbshell
```

### Static Files Not Loading

```bash
python manage.py collectstatic --noinput
```

### Permission Issues

```bash
sudo chown -R www-data:www-data /path/to/teqwa-backend
```

### Check Service Status

```bash
sudo systemctl status teqwa-backend
```
