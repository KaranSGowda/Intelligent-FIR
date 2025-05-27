#!/usr/bin/env python3
"""
Application Status Checker
Verifies that the Intelligent FIR System is running correctly
"""

import requests
import sys
import time

def check_server_status():
    """Check if the Flask server is responding"""
    urls_to_try = [
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "http://192.168.137.99:5000"
    ]
    
    print("🔍 Checking server status...")
    
    for url in urls_to_try:
        try:
            print(f"   Trying {url}...")
            response = requests.get(url, timeout=5)
            if response.status_code in [200, 302]:  # 302 for redirect to login
                print(f"✅ Server is running at {url}")
                print(f"   Status Code: {response.status_code}")
                return url
            else:
                print(f"⚠️ Server responded with status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to {url}")
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout connecting to {url}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    return None

def check_database():
    """Check if database is accessible"""
    try:
        import sqlite3
        import os
        
        db_paths = [
            "instance/fir_system.db",
            "fir_system.db"
        ]
        
        for db_path in db_paths:
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                conn.close()
                print(f"✅ Database found at {db_path} with {len(tables)} tables")
                return True
        
        print("❌ Database not found")
        return False
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    required_modules = [
        'flask',
        'flask_login',
        'flask_sqlalchemy',
        'werkzeug',
        'reportlab',
        'nltk',
        'sklearn'
    ]
    
    print("📦 Checking dependencies...")
    missing = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            print(f"   ❌ {module} - MISSING")
            missing.append(module)
    
    if missing:
        print(f"\n⚠️ Missing dependencies: {', '.join(missing)}")
        print("💡 Run: pip install -r requirements.txt")
        return False
    
    return True

def check_files():
    """Check if essential files exist"""
    essential_files = [
        "app.py",
        "models.py",
        "extensions.py",
        "requirements.txt",
        "routes/auth.py",
        "routes/fir.py",
        "templates/layout.html",
        "templates/login.html"
    ]
    
    print("📁 Checking essential files...")
    missing = []
    
    for file_path in essential_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING")
            missing.append(file_path)
    
    if missing:
        print(f"\n⚠️ Missing files: {', '.join(missing)}")
        return False
    
    return True

def main():
    """Main diagnostic function"""
    print("🚀 Intelligent FIR System - Status Check")
    print("=" * 50)
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Check files
    files_ok = check_files()
    
    # Check database
    db_ok = check_database()
    
    # Check server
    server_url = check_server_status()
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    
    if deps_ok and files_ok and db_ok and server_url:
        print("🎉 ALL CHECKS PASSED!")
        print(f"🌐 Your application is running at: {server_url}")
        print("\n🎯 Next steps:")
        print("1. Open your browser")
        print(f"2. Go to: {server_url}")
        print("3. You should see the login page")
        print("4. Register a new account or use existing credentials")
        
        # Try to open browser automatically
        try:
            import webbrowser
            print(f"\n🌐 Opening {server_url} in your default browser...")
            webbrowser.open(server_url)
        except:
            print("💡 Please manually open the URL in your browser")
            
    else:
        print("❌ SOME ISSUES FOUND:")
        if not deps_ok:
            print("   - Missing dependencies")
        if not files_ok:
            print("   - Missing essential files")
        if not db_ok:
            print("   - Database issues")
        if not server_url:
            print("   - Server not responding")
        
        print("\n🔧 SOLUTIONS:")
        if not deps_ok:
            print("   Run: pip install -r requirements.txt")
        if not files_ok:
            print("   Ensure all project files are in place")
        if not db_ok:
            print("   Run: python scripts/setup_db.py")
        if not server_url:
            print("   Run: python app.py")

if __name__ == "__main__":
    import os
    main()
