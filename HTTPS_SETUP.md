# HTTPS Setup Guide for api.mujemaateqwa.org

This guide will help you set up HTTPS for your backend API using Let's Encrypt SSL certificates.

## Prerequisites

1. **DNS Configuration**: Add an A record in Cloudflare:
   - **Type**: A
   - **Name**: `api`
   - **Content**: `56.228.17.128`
   - **Proxy status**: DNS only (gray cloud, NOT proxied)
   - **TTL**: Auto

2. **Wait for DNS propagation** (5-15 minutes)

3. **Verify DNS**:
   ```bash
   dig api.mujemaateqwa.org
   # or
   nslookup api.mujemaateqwa.org
   ```
   Should return: `56.228.17.128`

## Step 1: Update DNS Record in Cloudflare

1. Log in to Cloudflare dashboard
2. Select `mujemaateqwa.org` domain
3. Go to **DNS** → **Records**
4. Click **+ Add record**
5. Configure:
   - **Type**: A
   - **Name**: `api`
   - **IPv4 address**: `56.228.17.128`
   - **Proxy status**: DNS only (gray cloud)
   - **TTL**: Auto
6. Click **Save**

## Step 2: Pull Latest Code

On your EC2 instance:

```bash
cd ~/teqwa-backend/teqwa-backend
git pull origin main
```

## Step 3: Update Environment Variables

Make sure your `.env` file includes:

```env
ALLOWED_HOSTS=api.mujemaateqwa.org,56.228.17.128,localhost,127.0.0.1
SECURE_SSL_REDIRECT=True
```

## Step 4: Rebuild and Start Services

```bash
# Stop existing containers
docker compose down

# Rebuild and start (this will create new volumes for certbot)
docker compose up -d --build
```

## Step 5: Obtain SSL Certificates

```bash
# Make the script executable
chmod +x nginx/ssl/setup-letsencrypt.sh

# Run the setup script
./nginx/ssl/setup-letsencrypt.sh
```

The script will:
1. Start nginx (required for certificate validation)
2. Request certificates from Let's Encrypt
3. Copy certificates to the correct location
4. Restart nginx with SSL enabled

## Step 6: Verify HTTPS is Working

```bash
# Test the API endpoint
curl https://api.mujemaateqwa.org/api/v1/

# Test admin endpoint
curl -I https://api.mujemaateqwa.org/admin/

# Check certificate
openssl s_client -connect api.mujemaateqwa.org:443 -servername api.mujemaateqwa.org
```

## Step 7: Update Frontend API URL

In your Vercel project settings, update the environment variable:

- **Variable**: `VITE_API_URL`
- **Value**: `https://api.mujemaateqwa.org`

Also update `vercel.json`:

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://api.mujemaateqwa.org/api/:path*"
    }
  ]
}
```

## Certificate Renewal

Certificates are automatically renewed by the `certbot` container that runs in the background. It checks for renewal every 12 hours.

To manually renew:

```bash
docker compose run --rm certbot renew
docker compose restart nginx
```

## Troubleshooting

### Certificate generation fails

1. **Check DNS**: Ensure `api.mujemaateqwa.org` points to `56.228.17.128`
   ```bash
   dig api.mujemaateqwa.org
   ```

2. **Check port 80**: Ensure it's accessible
   ```bash
   sudo netstat -tuln | grep :80
   ```

3. **Check firewall**: Ensure AWS Security Group allows inbound traffic on port 80

4. **Check nginx logs**:
   ```bash
   docker compose logs nginx
   ```

### Nginx can't find certificates

Certificates are stored in Docker volumes. To check:

```bash
docker volume inspect teqwa-backend_certbot_conf
docker compose exec certbot ls -la /etc/letsencrypt/live/api.mujemaateqwa.org/
```

### Mixed Content Errors

If your frontend still shows mixed content errors:
1. Ensure `VITE_API_URL` uses `https://` (not `http://`)
2. Update `vercel.json` to proxy to `https://api.mujemaateqwa.org`
3. Clear browser cache and hard refresh

## Security Notes

- HTTPS is now enforced (HTTP redirects to HTTPS)
- Secure cookies are enabled
- HSTS headers are set
- All API requests must use HTTPS
