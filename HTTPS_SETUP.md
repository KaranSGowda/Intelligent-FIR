# HTTPS Setup Guide for Intelligent FIR System

This guide will help you set up HTTPS for the Intelligent FIR system to resolve audio recording compatibility issues.

## 🚀 Quick Start (Windows)

### Option 1: Using PowerShell Script (Recommended)
1. Right-click on `run_https.ps1`
2. Select "Run with PowerShell"
3. Follow the prompts to generate SSL certificates
4. The app will start automatically with HTTPS

### Option 2: Using Batch File
1. Double-click `run_https.bat`
2. Follow the prompts to generate SSL certificates
3. The app will start automatically with HTTPS

### Option 3: Manual Setup
1. Open Command Prompt or PowerShell
2. Run: `python generate_ssl_cert.py`
3. Run: `python app.py --https`
4. Access the app at: `https://localhost:5000`

## 🔧 Prerequisites

### Install OpenSSL (Required for SSL Certificate Generation)

#### Windows:
1. Download OpenSSL from: https://slproweb.com/products/Win32OpenSSL.html
2. Choose the latest version (e.g., Win64 OpenSSL v3.x.x)
3. Install with default settings
4. Add OpenSSL to your PATH environment variable

#### macOS:
```bash
brew install openssl
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install openssl
```

#### Linux (CentOS/RHEL):
```bash
sudo yum install openssl
```

## 📋 Step-by-Step Setup

### 1. Generate SSL Certificates
```bash
python generate_ssl_cert.py
```

This will create:
- `ssl_certs/cert.pem` - SSL certificate
- `ssl_certs/key.pem` - Private key

### 2. Start the Application with HTTPS
```bash
python app.py --https
```

### 3. Access the Application
- URL: `https://localhost:5000`
- Note: You'll see a security warning (normal for self-signed certificates)
- Click "Advanced" → "Proceed to localhost (unsafe)"

## 🔍 Troubleshooting

### SSL Certificate Issues
**Error: "SSL certificates not found"**
```bash
python generate_ssl_cert.py
```

**Error: "OpenSSL not found"**
- Install OpenSSL (see Prerequisites section)
- Ensure OpenSSL is in your system PATH

### Browser Security Warning
When you access `https://localhost:5000`, you'll see a security warning because we're using a self-signed certificate. This is normal for development.

**Chrome/Edge:**
1. Click "Advanced"
2. Click "Proceed to localhost (unsafe)"

**Firefox:**
1. Click "Advanced"
2. Click "Accept the Risk and Continue"

**Safari:**
1. Click "Show Details"
2. Click "visit this website"
3. Click "Visit Website" in the popup

### Audio Recording Still Not Working
1. **Check browser console** (F12 → Console) for error messages
2. **Allow microphone permissions** when prompted
3. **Try a different browser** (Chrome, Firefox, Edge)
4. **Check microphone settings** in Windows Privacy Settings

## 🌐 Production Deployment

For production deployment, you should use a proper SSL certificate from a trusted Certificate Authority (CA) like Let's Encrypt.

### Using Let's Encrypt (Recommended for Production)
1. Install Certbot: https://certbot.eff.org/
2. Generate certificates: `certbot certonly --standalone -d yourdomain.com`
3. Update the SSL context in `app.py` to use the Let's Encrypt certificates

## 📱 Mobile Testing

To test on mobile devices:
1. Find your computer's IP address: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
2. Start the app: `python app.py --https --host 0.0.0.0`
3. Access from mobile: `https://YOUR_IP_ADDRESS:5000`
4. Accept the security warning on mobile

## 🔒 Security Notes

- Self-signed certificates are for development only
- Never use self-signed certificates in production
- The generated certificates are valid for 365 days
- Keep the private key (`ssl_certs/key.pem`) secure

## 📞 Support

If you encounter issues:
1. Check the browser console for error messages
2. Ensure OpenSSL is properly installed
3. Try running the compatibility test: `AudioRecorder.testBrowserCompatibility()`
4. Check that microphone permissions are granted

## ✅ Verification

After setup, you should see:
- ✅ "Browser compatibility check passed" in console
- ✅ "Ready to record (HTTPS detected - optimal compatibility)" status
- ✅ Audio recording works without compatibility warnings 