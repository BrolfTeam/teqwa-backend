# Let's Encrypt SSL Certificate Setup Script (PowerShell)
# Run this from the teqwa-backend directory

$DOMAIN = "mujemaateqwa.org"
$SSL_DIR = ".\nginx\ssl"
$LETSENCRYPT_DIR = $SSL_DIR

Write-Host "🔒 Setting up Let's Encrypt SSL certificates for $DOMAIN" -ForegroundColor Cyan
Write-Host ""

# Check if running from correct directory
if (-not (Test-Path "nginx\ssl")) {
    Write-Host "❌ Error: Please run this script from the teqwa-backend directory" -ForegroundColor Red
    exit 1
}

# Stop any services using port 80
Write-Host "⚠️  Make sure port 80 is available (stop nginx if running)" -ForegroundColor Yellow
Write-Host "   Run: docker compose down (if services are running)" -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to continue"

# Get certificates
Write-Host "📥 Requesting certificates from Let's Encrypt..." -ForegroundColor Cyan
$currentDir = (Get-Location).Path
docker run -it --rm `
    -v "${currentDir}\nginx\ssl:/etc/letsencrypt" `
    -p 80:80 `
    certbot/certbot certonly --standalone `
    -d $DOMAIN `
    -d "www.$DOMAIN" `
    --email "admin@$DOMAIN" `
    --agree-tos `
    --non-interactive

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to obtain certificates" -ForegroundColor Red
    exit 1
}

# Copy certificates to expected location
Write-Host "📋 Copying certificates to expected location..." -ForegroundColor Cyan
$CERT_SOURCE = Join-Path $SSL_DIR "live\$DOMAIN"
if (Test-Path $CERT_SOURCE) {
    Copy-Item (Join-Path $CERT_SOURCE "fullchain.pem") (Join-Path $SSL_DIR "cert.pem") -Force
    Copy-Item (Join-Path $CERT_SOURCE "privkey.pem") (Join-Path $SSL_DIR "key.pem") -Force
    
    # Set proper permissions (Windows may not support chmod, but we try)
    Write-Host "✅ Certificates copied successfully!" -ForegroundColor Green
    Write-Host "   - Certificate: $SSL_DIR\cert.pem" -ForegroundColor Green
    Write-Host "   - Private Key: $SSL_DIR\key.pem" -ForegroundColor Green
} else {
    Write-Host "❌ Certificate directory not found: $CERT_SOURCE" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 SSL certificates are ready!" -ForegroundColor Green
Write-Host "   You can now start your services with: docker compose up -d" -ForegroundColor Green
