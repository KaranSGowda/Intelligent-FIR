"""
Script to set up the online PostgreSQL database for the Intelligent FIR System.
This script will:
1. Install required dependencies
2. Create all database tables
3. Initialize legal sections
4. Create demo users (optional)
"""

import os
import sys
import subprocess

def install_dependencies():
    """Install required Python packages"""
    print("Installing required dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary", "python-dotenv"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        sys.exit(1)

def setup_database():
    """Set up the database schema and initial data"""
    try:
        # Import after installing dependencies
        from app import create_app
        from extensions import db
        from utils.legal_mapper import initialize_legal_sections
        from models import User, Role

        print("Creating application context...")
        app = create_app()

        with app.app_context():
            print("Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully")

            print("Initializing legal sections...")
            initialize_legal_sections()
            print("✅ Legal sections initialized")

            # Check if we should create demo users
            create_users = input("Do you want to create demo users? (y/n): ").lower().strip() == 'y'

            if create_users:
                print("Creating demo users...")
                # Check if users already exist
                if User.query.filter_by(username='user').first() is None:
                    # Create demo users
                    demo_users = [
                        {
                            'username': 'user',
                            'password': 'password',
                            'email': 'user@example.com',
                            'full_name': 'Demo User',
                            'role': Role.PUBLIC
                        },
                        {
                            'username': 'police',
                            'password': 'password',
                            'email': 'police@example.com',
                            'full_name': 'Police Officer',
                            'role': Role.POLICE
                        },
                        {
                            'username': 'admin',
                            'password': 'password',
                            'email': 'admin@example.com',
                            'full_name': 'System Admin',
                            'role': Role.ADMIN
                        }
                    ]

                    for user_data in demo_users:
                        user = User(
                            username=user_data['username'],
                            email=user_data['email'],
                            full_name=user_data['full_name'],
                            role=user_data['role']
                        )
                        user.set_password(user_data['password'])
                        db.session.add(user)

                    db.session.commit()
                    print("✅ Demo users created successfully")
                else:
                    print("⚠️ Demo users already exist, skipping creation")

            print("\nDatabase setup completed successfully!")
            print("\nYou can now run the application with:")
            print("python main.py")

    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    print("=== Intelligent FIR System - Online Database Setup ===\n")

    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️ .env file not found. Please create it with your database connection details.")
        print("Example .env file content:")
        print("""
DATABASE_URL=postgresql://postgres:your-password@db.your-project-ref.supabase.co:5432/postgres
SECRET_KEY=your-secret-key-here
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
        """)
        sys.exit(1)

    # Confirm database URL is set
    try:
        from dotenv import load_dotenv
        load_dotenv()
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            print("❌ DATABASE_URL not found in .env file or environment variables")
            sys.exit(1)
        elif db_url.startswith('sqlite'):
            print("❌ DATABASE_URL is still set to SQLite. Please update it to your PostgreSQL connection string")
            sys.exit(1)
        elif 'your-password' in db_url or 'your-project-ref' in db_url:
            print("❌ DATABASE_URL contains placeholder values. Please update it with your actual Supabase connection details")
            sys.exit(1)
        else:
            # Mask the password in the printed URL for security
            masked_url = db_url.replace(db_url.split(':')[2].split('@')[0], '********')
            print(f"✅ Using database: {masked_url}")
    except ImportError:
        print("⚠️ python-dotenv not installed. Installing dependencies...")
        install_dependencies()
        from dotenv import load_dotenv
        load_dotenv()

    # Install dependencies
    install_dependencies()

    # Set up the database
    setup_database()
