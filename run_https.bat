@echo off
echo ========================================
echo   Intelligent FIR System - HTTPS Mode
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if SSL certificates exist
if not exist "ssl_certs\cert.pem" (
    echo SSL certificates not found. Generating them...
    python generate_ssl_cert.py
    if errorlevel 1 (
        echo Failed to generate SSL certificates
        echo Please install OpenSSL and try again
        pause
        exit /b 1
    )
)

echo Starting Intelligent FIR System with HTTPS...
echo.
echo URL: https://localhost:5000
echo.
echo Note: You may see a security warning - this is normal for self-signed certificates
echo Click 'Advanced' and 'Proceed to localhost' to continue
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py --https

pause 