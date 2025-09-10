#!/usr/bin/env python3
"""
Generate self-signed SSL certificate for HTTPS development
This script creates a self-signed certificate for local development
"""

import os
import subprocess
import sys
from pathlib import Path

def generate_ssl_certificate():
    """Generate a self-signed SSL certificate for development"""
    
    # Create certificates directory
    cert_dir = Path("ssl_certs")
    cert_dir.mkdir(exist_ok=True)
    
    cert_file = cert_dir / "cert.pem"
    key_file = cert_dir / "key.pem"
    
    # Check if certificates already exist
    if cert_file.exists() and key_file.exists():
        print("✅ SSL certificates already exist!")
        print(f"Certificate: {cert_file}")
        print(f"Private key: {key_file}")
        return True
    
    print("🔐 Generating self-signed SSL certificate...")
    
    try:
        # Generate private key
        subprocess.run([
            "openssl", "genrsa", "-out", str(key_file), "2048"
        ], check=True, capture_output=True)
        
        # Generate certificate
        subprocess.run([
            "openssl", "req", "-new", "-x509", "-key", str(key_file),
            "-out", str(cert_file), "-days", "365", "-subj",
            "/C=IN/ST=State/L=City/O=Intelligent-FIR/OU=Development/CN=localhost"
        ], check=True, capture_output=True)
        
        print("✅ SSL certificate generated successfully!")
        print(f"Certificate: {cert_file}")
        print(f"Private key: {key_file}")
        print("\n⚠️  Note: This is a self-signed certificate for development only.")
        print("   Your browser will show a security warning - this is normal.")
        print("   Click 'Advanced' and 'Proceed to localhost' to continue.")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating SSL certificate: {e}")
        print("Make sure OpenSSL is installed on your system.")
        return False
    except FileNotFoundError:
        print("❌ OpenSSL not found. Please install OpenSSL:")
        print("   Windows: Download from https://slproweb.com/products/Win32OpenSSL.html")
        print("   macOS: brew install openssl")
        print("   Linux: sudo apt-get install openssl")
        return False

if __name__ == "__main__":
    success = generate_ssl_certificate()
    if success:
        print("\n🚀 You can now run the app with HTTPS!")
        print("   python app.py --https")
    else:
        sys.exit(1) 