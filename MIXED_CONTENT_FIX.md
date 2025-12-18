# Fixing Mixed Content Error (HTTPS Frontend → HTTP Backend)

## Problem
Vercel serves your frontend over HTTPS, but your backend is HTTP. Browsers block HTTP requests from HTTPS pages (Mixed Content policy).

## Solutions

### Option 1: Set Up HTTPS on Backend (Recommended)

**If you have a domain name pointing to 56.228.17.128:**

1. **Point domain to EC2 IP:**
   - Add A record: `mujemaateqwa.org` → `56.228.17.128`
   - Add A record: `www.mujemaateqwa.org` → `56.228.17.128`

2. **Get Let's Encrypt SSL certificate:**
   ```bash
   cd ~/teqwa-backend/teqwa-backend
   
   # Stop nginx temporarily
   docker compose stop nginx
   
   # Get certificates
   docker run -it --rm \
     -v "$(pwd)/nginx/ssl:/etc/letsencrypt" \
     -p 80:80 \
     certbot/certbot certonly --standalone \
     -d mujemaateqwa.org \
     -d www.mujemaateqwa.org \
     --email admin@mujemaateqwa.org \
     --agree-tos \
     --non-interactive
   
   # Copy certificates
   cp nginx/ssl/live/mujemaateqwa.org/fullchain.pem nginx/ssl/cert.pem
   cp nginx/ssl/live/mujemaateqwa.org/privkey.pem nginx/ssl/key.pem
   
   # Update nginx config to use HTTPS (uncomment HTTPS server block)
   # Restart nginx
   docker compose start nginx
   ```

3. **Update Vercel environment variable:**
   - `VITE_API_URL=https://mujemaateqwa.org/api`

### Option 2: Use Vercel Proxy (Temporary Workaround)

Configure Vercel to proxy API requests, avoiding Mixed Content:

1. **Create `vercel.json` in frontend root:**
   ```json
   {
     "rewrites": [
       {
         "source": "/api/:path*",
         "destination": "http://56.228.17.128/api/:path*"
       }
     ]
   }
   ```

2. **Update frontend to use relative URLs:**
   - Set `VITE_API_URL=/api` (relative path)
   - Vercel will proxy `/api/*` to your backend

### Option 3: Fix VITE_API_URL (Immediate Fix for Double Path)

**Current issue:** `VITE_API_URL=http://56.228.17.128/api/v1/` causes double paths.

**Fix in Vercel:**
- Set `VITE_API_URL=http://56.228.17.128` (base domain only, no `/api/v1/`)

The frontend code already appends `/api/v1`:
```javascript
const API_BASE_URL = `${API_URL}/api/v1`;  // API_URL is VITE_API_URL
```

So if `VITE_API_URL=http://56.228.17.128`, then:
- `API_BASE_URL = http://56.228.17.128/api/v1` ✓

## Recommended Approach

1. **Immediate:** Fix `VITE_API_URL` to `http://56.228.17.128` (removes double path)
2. **Short-term:** Use Vercel proxy (Option 2) to avoid Mixed Content
3. **Long-term:** Set up HTTPS with domain + Let's Encrypt (Option 1)

## Testing

After fixing `VITE_API_URL`:
- URLs should be: `http://56.228.17.128/api/v1/...` (not double path)
- Mixed Content will still show, but URLs will be correct

After setting up HTTPS or Vercel proxy:
- Mixed Content error will be resolved
- All requests will work from Vercel frontend
