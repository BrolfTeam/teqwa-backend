# Environment Configuration Notes for EC2 Deployment

## Required .env Variables

When deploying to EC2, ensure your `.env` file includes:

```env
# Frontend URL (Vercel)
FRONTEND_URL=https://teqwa-frontend.vercel.app

# CORS Allowed Origins (comma-separated)
CORS_ALLOWED_ORIGINS=https://teqwa-frontend.vercel.app

# Allowed Hosts (comma-separated)
ALLOWED_HOSTS=56.228.17.128,localhost,127.0.0.1

# Other required variables...
# (Database, Secret Key, etc.)
```

## Settings Defaults

The Django settings.py has been updated with these defaults:
- **ALLOWED_HOSTS**: Includes `56.228.17.128` by default
- **FRONTEND_URL**: Defaults to `https://teqwa-frontend.vercel.app` in production
- **CORS_ALLOWED_ORIGINS**: Defaults to `https://teqwa-frontend.vercel.app` if not set

You can override these via environment variables if needed.
