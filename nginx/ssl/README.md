# SSL Certificate Setup

This directory should contain your SSL certificates for HTTPS.

## Required Files

Place the following files in this directory:

- `cert.pem` - Your SSL certificate file (or fullchain.pem for Let's Encrypt)
- `key.pem` - Your private key file (or privkey.pem for Let's Encrypt)

## Option 1: Let's Encrypt (Recommended - Free)

### Automated Setup (Recommended)

**For Linux/Mac:**
```bash
cd teqwa-backend
chmod +x nginx/ssl/setup-letsencrypt.sh
./nginx/ssl/setup-letsencrypt.sh
```

**For Windows (PowerShell):**
```powershell
cd teqwa-backend
.\nginx\ssl\setup-letsencrypt.ps1
```

### Manual Setup

1. **Get certificates** (run from teqwa-backend directory):
   ```bash
   docker run -it --rm \
     -v "$(pwd)/nginx/ssl:/etc/letsencrypt" \
     -p 80:80 \
     certbot/certbot certonly --standalone \
     -d mujemaateqwa.org \
     -d www.mujemaateqwa.org \
     --email admin@mujemaateqwa.org \
     --agree-tos \
     --non-interactive
   ```

2. **Copy certificates to expected location**:
   ```bash
   # The certificates are created in nginx/ssl/live/mujemaateqwa.org/
   # Copy them to the root of the ssl directory
   cp nginx/ssl/live/mujemaateqwa.org/fullchain.pem nginx/ssl/cert.pem
   cp nginx/ssl/live/mujemaateqwa.org/privkey.pem nginx/ssl/key.pem
   
   # Set proper permissions (Linux/Mac)
   chmod 644 nginx/ssl/cert.pem
   chmod 600 nginx/ssl/key.pem
   ```

### Auto-renewal with Certbot

**Automated Renewal Script:**

**For Linux/Mac:**
```bash
cd teqwa-backend
chmod +x nginx/ssl/renew-letsencrypt.sh
./nginx/ssl/renew-letsencrypt.sh
```

**For Windows (PowerShell):**
```powershell
cd teqwa-backend
.\nginx\ssl\renew-letsencrypt.ps1
```

**Set up a cron job (Linux) or scheduled task (Windows) to run renewal:**

**Linux Cron (runs twice daily):**
```bash
# Add to crontab: crontab -e
0 0,12 * * * cd /path/to/teqwa-backend && ./nginx/ssl/renew-letsencrypt.sh >> /var/log/letsencrypt-renewal.log 2>&1
```

**Manual Renewal:**
```bash
docker run --rm \
  -v "$(pwd)/nginx/ssl:/etc/letsencrypt" \
  -p 80:80 \
  certbot/certbot renew

# Then copy the renewed certificates
cp nginx/ssl/live/mujemaateqwa.org/fullchain.pem nginx/ssl/cert.pem
cp nginx/ssl/live/mujemaateqwa.org/privkey.pem nginx/ssl/key.pem
```

## Option 2: cPanel SSL Certificates

If you're using cPanel:

1. Generate or upload your SSL certificate in cPanel
2. Download the certificate and private key
3. Place them in this directory as:
   - `cert.pem` (your certificate)
   - `key.pem` (your private key)

## Option 3: Commercial SSL Certificate

1. Purchase SSL certificate from a provider (DigiCert, GoDaddy, etc.)
2. Download the certificate and private key files
3. Place them in this directory as:
   - `cert.pem` (your certificate)
   - `key.pem` (your private key)

## Security Notes

- **Never commit** `key.pem` to version control
- Keep private keys secure (600 permissions)
- Certificates typically expire after 90 days (Let's Encrypt) or 1 year (commercial)
- Set up auto-renewal for Let's Encrypt certificates

## Testing

After placing certificates, test the configuration:
```bash
docker compose up nginx
# Or test nginx config
docker exec teqwa_nginx nginx -t
```

## Troubleshooting

- **Permission denied**: Ensure key.pem has 600 permissions
- **Certificate not found**: Check file names match exactly (cert.pem, key.pem)
- **Expired certificate**: Renew your certificates
