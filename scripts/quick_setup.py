#!/usr/bin/env python3
"""
Quick Setup Script for Intelligent FIR System
Initializes the organized project structure and sets up the development environment
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")

def create_env_file():
    """Create .env file from .env.example if it doesn't exist"""
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            print("✅ Created .env file from .env.example")
            print("📝 Please edit .env file with your configuration")
        else:
            print("⚠️ .env.example not found, creating basic .env")
            with open('.env', 'w') as f:
                f.write("""# Intelligent FIR System Configuration
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=True
DATABASE_URL=sqlite:///instance/fir_system.db
""")
    else:
        print("✅ .env file already exists")

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("💡 Try running: pip install -r requirements.txt")
        return False
    return True

def setup_database():
    """Initialize the database"""
    print("🗄️ Setting up database...")
    try:
        # Ensure instance directory exists
        os.makedirs('instance', exist_ok=True)
        
        # Run database setup
        subprocess.run([sys.executable, 'scripts/setup_db.py'], 
                      check=True, capture_output=True)
        print("✅ Database initialized successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to setup database: {e}")
        print("💡 Try running: python scripts/setup_db.py")
        return False
    except FileNotFoundError:
        print("⚠️ Database setup script not found, creating basic database...")
        # Create a minimal database setup
        try:
            from app import create_app
            from models import db
            
            app = create_app()
            with app.app_context():
                db.create_all()
                print("✅ Basic database created")
        except Exception as e:
            print(f"❌ Failed to create database: {e}")
            return False
    return True

def download_nltk_data():
    """Download required NLTK data"""
    print("📚 Downloading NLTK data...")
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        print("✅ NLTK data downloaded")
    except ImportError:
        print("⚠️ NLTK not installed, skipping NLTK data download")
    except Exception as e:
        print(f"⚠️ Failed to download NLTK data: {e}")

def check_ffmpeg():
    """Check if FFmpeg is available"""
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      capture_output=True, check=True)
        print("✅ FFmpeg is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ FFmpeg not found - voice transcription may not work")
        print("💡 Install FFmpeg for audio processing features")

def create_directories():
    """Create necessary directories"""
    directories = [
        'static/uploads/evidence',
        'static/uploads/audio', 
        'static/uploads/images',
        'static/pdfs',
        'logs',
        'backup'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    print("✅ Created necessary directories")

def test_application():
    """Test if the application starts correctly"""
    print("🧪 Testing application startup...")
    try:
        # Import the app to check for import errors
        from app import create_app
        app = create_app()
        
        # Test basic functionality
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code in [200, 302]:  # 302 for redirect to login
                print("✅ Application starts successfully")
                return True
            else:
                print(f"⚠️ Application returned status code: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Application test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Intelligent FIR System - Quick Setup")
    print("=" * 50)
    
    # Change to project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)
    
    # Run setup steps
    steps = [
        ("Checking Python version", check_python_version),
        ("Creating environment file", create_env_file),
        ("Installing dependencies", install_dependencies),
        ("Creating directories", create_directories),
        ("Setting up database", setup_database),
        ("Downloading NLTK data", download_nltk_data),
        ("Checking FFmpeg", check_ffmpeg),
        ("Testing application", test_application),
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        try:
            result = step_func()
            if result is False:
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ {step_name} failed: {e}")
            failed_steps.append(step_name)
    
    print("\n" + "=" * 50)
    
    if not failed_steps:
        print("🎉 Setup completed successfully!")
        print("\n🚀 Next steps:")
        print("1. Edit .env file with your configuration")
        print("2. Run the application: python app.py")
        print("3. Open http://localhost:5000 in your browser")
        print("4. Register a new account or use demo credentials")
    else:
        print("⚠️ Setup completed with some issues:")
        for step in failed_steps:
            print(f"   - {step}")
        print("\n💡 Please resolve the issues above and try again")
        print("   You can run individual scripts in the scripts/ directory")
    
    print("\n📚 Documentation:")
    print("   - Project Structure: PROJECT_STRUCTURE.md")
    print("   - Development Guide: DEVELOPMENT_GUIDE.md")
    print("   - Documentation: docs/")

if __name__ == "__main__":
    main()
