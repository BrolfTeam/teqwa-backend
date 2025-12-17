# Fly.io Deployment Guide for Teqwa Backend

This guide will help you deploy the Teqwa Backend to Fly.io.

## Prerequisites

1. **Fly.io Account**: Sign up at [fly.io](https://fly.io)
2. **Fly CLI**: Install the Fly CLI tool
   ```bash
   # macOS/Linux
   curl -L https://fly.io/install.sh | sh
   
   # Windows (PowerShell)
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   ```
3. **Docker**: Fly.io uses Docker for builds (optional if using remote builds)

## Initial Setup

### 1. Login to Fly.io

```bash
fly auth login
```

### 2. Initialize Fly.io App

Navigate to the `teqwa-backend` directory and initialize:

```bash
cd teqwa-backend
fly launch
```

When prompted:
- **App name**: Choose a unique name (e.g., `teqwa-backend-prod`) or use the default
- **Region**: Choose a region close to your users (e.g., `iad` for US East, `lhr` for London)
- **PostgreSQL**: Select **Yes** to create a PostgreSQL database
- **Redis**: Select **No** (unless you need it)
- **Deploy now**: Select **No** (we'll configure environment variables first)

### 3. Configure PostgreSQL Database

If you didn't create a database during `fly launch`, create one now:

```bash
fly postgres create --name teqwa-db --region iad
```

Attach the database to your app:

```bash
fly postgres attach --app teqwa-backend teqwa-db
```

This will automatically set the `DATABASE_URL` environment variable.

## Environment Variables

Set all required environment variables using `fly secrets set`:

```bash
# Required: Django Secret Key (generate a strong secret key)
fly secrets set SECRET_KEY="your-very-long-random-secret-key-here"

# Required: Debug mode (set to 0 for production)
fly secrets set DEBUG="0"

# Required: Allowed hosts (comma-separated list)
fly secrets set ALLOWED_HOSTS="teqwa-backend.fly.dev,your-custom-domain.com"

# Required: Frontend URL (for CORS and email links)
fly secrets set FRONTEND_URL="https://your-frontend-domain.com"

# Required: CORS allowed origins (comma-separated list)
fly secrets set CORS_ALLOWED_ORIGINS="https://your-frontend-domain.com"

# Email Configuration
fly secrets set EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
fly secrets set EMAIL_HOST="smtp.gmail.com"
fly secrets set EMAIL_PORT="587"
fly secrets set EMAIL_USE_TLS="True"
fly secrets set EMAIL_HOST_USER="your-email@gmail.com"
fly secrets set EMAIL_HOST_PASSWORD="your-app-password"
fly secrets set DEFAULT_FROM_EMAIL="noreply@teqwa.com"

# Payment Configuration (Chapa)
fly secrets set CHAPA_SECRET_KEY="your-chapa-secret-key"
fly secrets set CHAPA_WEBHOOK_SECRET="your-webhook-secret"
fly secrets set WEBHOOK_URL="https://teqwa-backend.fly.dev/api/v1/payments/webhook/"

# AWS S3 Configuration (for media files in production)
fly secrets set AWS_ACCESS_KEY_ID="your-aws-access-key"
fly secrets set AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
fly secrets set AWS_STORAGE_BUCKET_NAME="your-bucket-name"
fly secrets set AWS_S3_REGION_NAME="us-east-1"

# Optional: SSL/TLS settings
fly secrets set USE_TLS="True"
fly secrets set SECURE_SSL_REDIRECT="True"
```

### View Current Secrets

```bash
fly secrets list
```

### Update a Secret

```bash
fly secrets set SECRET_KEY="new-secret-key"
```

### Remove a Secret

```bash
fly secrets unset SECRET_KEY
```

## Configuration Files

### fly.toml

The `fly.toml` file has been pre-configured with:
- HTTP service on port 8000
- Health checks on `/api/v1/`
- Auto-scaling (stops when idle, starts on request)
- HTTPS enforcement

You can customize the region and resources:

```bash
# Edit fly.toml to change region
fly.toml -> primary_region = "iad"  # Change to your preferred region

# Scale resources if needed
fly scale vm shared-cpu-1x --memory 1024
```

## Deployment

### 1. Deploy the Application

```bash
fly deploy
```

This will:
- Build the Docker image
- Push it to Fly.io
- Deploy and start the application
- Run migrations automatically (via docker-entrypoint.py)

### 2. Check Deployment Status

```bash
fly status
```

### 3. View Logs

```bash
# Real-time logs
fly logs

# Follow logs
fly logs -a teqwa-backend
```

## Post-Deployment

### 1. Create Superuser

The application will automatically attempt to create a superuser via the `create_superuser_auto` management command. If you need to create one manually:

```bash
fly ssh console
python manage.py createsuperuser
```

### 2. Run Migrations (if needed)

Migrations run automatically on startup, but you can run them manually:

```bash
fly ssh console
python manage.py migrate
```

### 3. Collect Static Files

Static files are collected automatically in production mode, but you can do it manually:

```bash
fly ssh console
python manage.py collectstatic --noinput
```

### 4. Access Django Admin

Visit: `https://your-app-name.fly.dev/admin/`

## Custom Domain

### 1. Add Your Domain

```bash
fly certs add your-domain.com
```

### 2. Update DNS

Add a CNAME record pointing to `your-app-name.fly.dev`:

```
Type: CNAME
Name: api (or @ for root domain)
Value: your-app-name.fly.dev
```

### 3. Update Environment Variables

After adding the domain, update `ALLOWED_HOSTS`:

```bash
fly secrets set ALLOWED_HOSTS="your-app-name.fly.dev,your-domain.com"
```

## Scaling

### Scale Vertically (More Resources)

```bash
# Scale to 2GB RAM
fly scale vm shared-cpu-1x --memory 2048

# Scale to dedicated CPU
fly scale vm dedicated-cpu-1x --memory 2048
```

### Scale Horizontally (More Instances)

```bash
# Scale to 2 instances
fly scale count 2

# Auto-scale based on load
# Configure in fly.toml under [http_service]
```

## Monitoring

### View Metrics

```bash
fly metrics
```

### View App Info

```bash
fly info
```

### SSH into Container

```bash
fly ssh console
```

## Troubleshooting

### Application Won't Start

1. **Check logs**:
   ```bash
   fly logs
   ```

2. **Check environment variables**:
   ```bash
   fly secrets list
   ```

3. **Verify database connection**:
   ```bash
   fly ssh console
   python manage.py dbshell
   ```

### Database Connection Issues

1. **Verify DATABASE_URL is set**:
   ```bash
   fly secrets list | grep DATABASE_URL
   ```

2. **Test database connection**:
   ```bash
   fly ssh console
   python -c "import os; import dj_database_url; print(dj_database_url.parse(os.environ['DATABASE_URL']))"
   ```

### Static Files Not Loading

1. **Collect static files**:
   ```bash
   fly ssh console
   python manage.py collectstatic --noinput
   ```

2. **Check STATIC_ROOT**:
   ```bash
   fly ssh console
   ls -la staticfiles/
   ```

### CORS Issues

1. **Verify CORS_ALLOWED_ORIGINS**:
   ```bash
   fly secrets list | grep CORS
   ```

2. **Update CORS settings**:
   ```bash
   fly secrets set CORS_ALLOWED_ORIGINS="https://your-frontend.com"
   ```

### Health Check Failing

The health check endpoint is `/api/v1/`. If it's failing:

1. **Check if the API is accessible**:
   ```bash
   curl https://your-app-name.fly.dev/api/v1/
   ```

2. **Update health check path in fly.toml** if needed

## Backup and Restore

### Database Backup

```bash
# Create backup
fly postgres connect -a teqwa-db
pg_dump -U postgres teqwa_db > backup.sql

# Or use fly postgres backup
fly postgres backup create -a teqwa-db
```

### Database Restore

```bash
fly postgres connect -a teqwa-db
psql -U postgres teqwa_db < backup.sql
```

## Updates and Maintenance

### Deploy Updates

```bash
# Pull latest changes
git pull

# Deploy
fly deploy
```

### Rollback

```bash
# List releases
fly releases

# Rollback to previous version
fly releases rollback
```

### Restart Application

```bash
fly apps restart teqwa-backend
```

## Cost Optimization

1. **Use auto-scaling**: Configured in `fly.toml` to stop machines when idle
2. **Choose appropriate VM size**: Start with `shared-cpu-1x` and scale as needed
3. **Monitor usage**: Use `fly metrics` to track resource usage

## Security Checklist

- [x] Set `DEBUG=False` in production
- [x] Use strong `SECRET_KEY`
- [x] Configure `ALLOWED_HOSTS` properly
- [x] Set up HTTPS (automatic with Fly.io)
- [x] Configure CORS properly
- [x] Use secure database passwords (handled by Fly.io)
- [x] Set up email service
- [x] Configure AWS S3 for media files
- [x] Enable security headers (configured in settings.py)

## Support

- **Fly.io Docs**: https://fly.io/docs
- **Fly.io Community**: https://community.fly.io
- **Django on Fly.io**: https://fly.io/docs/django/

## Quick Reference

```bash
# Deploy
fly deploy

# View logs
fly logs

# SSH into app
fly ssh console

# Scale
fly scale count 2

# Secrets
fly secrets set KEY="value"
fly secrets list
fly secrets unset KEY

# Database
fly postgres connect -a teqwa-db

# Status
fly status
fly info
fly metrics
```
