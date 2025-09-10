# Intelligent FIR System - HTTPS Launcher
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Intelligent FIR System - HTTPS Mode" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if SSL certificates exist
$certFile = "ssl_certs\cert.pem"
$keyFile = "ssl_certs\key.pem"

if (-not (Test-Path $certFile) -or -not (Test-Path $keyFile)) {
    Write-Host "🔐 SSL certificates not found. Generating them..." -ForegroundColor Yellow
    
    try {
        python generate_ssl_cert.py
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to generate SSL certificates"
        }
        Write-Host "✅ SSL certificates generated successfully!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to generate SSL certificates" -ForegroundColor Red
        Write-Host "Please install OpenSSL and try again:" -ForegroundColor Yellow
        Write-Host "   Download from: https://slproweb.com/products/Win32OpenSSL.html" -ForegroundColor Cyan
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "✅ SSL certificates found" -ForegroundColor Green
}

Write-Host ""
Write-Host "🚀 Starting Intelligent FIR System with HTTPS..." -ForegroundColor Green
Write-Host ""
Write-Host "URL: https://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  Note: You may see a security warning - this is normal for self-signed certificates" -ForegroundColor Yellow
Write-Host "   Click 'Advanced' and 'Proceed to localhost' to continue" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Start the application
python app.py --https 