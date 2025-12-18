# Let's Encrypt SSL Certificate Renewal Script (PowerShell)
# Run this from the teqwa-backend directory

$DOMAIN = "mujemaateqwa.org"
$SSL_DIR = ".\nginx\ssl"

Write-Host "🔄 Renewing Let's Encrypt SSL certificates for $DOMAIN" -ForegroundColor Cyan
Write-Host ""

# Check if running from correct directory
if (-not (Test-Path "nginx\ssl")) {
    Write-Host "❌ Error: Please run this script from the teqwa-backend directory" -ForegroundColor Red
    exit 1
}

# Renew certificates
Write-Host "📥 Renewing certificates..." -ForegroundColor Cyan
$currentDir = (Get-Location).Path
docker run --rm `
    -v "${currentDir}\nginx\ssl:/etc/letsencrypt" `
    -p 80:80 `
    certbot/certbot renew

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to renew certificates" -ForegroundColor Red
    exit 1
}

# Copy renewed certificates to expected location
Write-Host "📋 Copying renewed certificates..." -ForegroundColor Cyan
$CERT_SOURCE = Join-Path $SSL_DIR "live\$DOMAIN"
if (Test-Path $CERT_SOURCE) {
    Copy-Item (Join-Path $CERT_SOURCE "fullchain.pem") (Join-Path $SSL_DIR "cert.pem") -Force
    Copy-Item (Join-Path $CERT_SOURCE "privkey.pem") (Join-Path $SSL_DIR "key.pem") -Force
    
    Write-Host "✅ Certificates renewed and copied successfully!" -ForegroundColor Green
    
    # Reload nginx if running
    $nginxRunning = docker ps --filter "name=teqwa_nginx" --format "{{.Names}}"
    if ($nginxRunning -eq "teqwa_nginx") {
        Write-Host "🔄 Reloading Nginx..." -ForegroundColor Cyan
        docker exec teqwa_nginx nginx -s reload
        Write-Host "✅ Nginx reloaded with new certificates" -ForegroundColor Green
    }
} else {
    Write-Host "❌ Certificate directory not found: $CERT_SOURCE" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 Certificate renewal complete!" -ForegroundColor Green
