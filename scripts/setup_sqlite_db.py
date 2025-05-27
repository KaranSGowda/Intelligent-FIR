"""
Script to set up and optimize the SQLite database for the Intelligent FIR System.
This script will:
1. Create the SQLite database file if it doesn't exist
2. Create all database tables
3. Initialize legal sections
4. Create demo users (optional)
5. Apply SQLite optimizations
"""

import os
import sys
import sqlite3

def optimize_sqlite_connection(db_path):
    """Apply performance optimizations to SQLite database"""
    print("Applying SQLite optimizations...")
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Enable WAL mode for better concurrency and performance
        cursor.execute("PRAGMA journal_mode=WAL;")
        
        # Set synchronous mode to NORMAL for better performance
        cursor.execute("PRAGMA synchronous=NORMAL;")
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys=ON;")
        
        # Set temp store to MEMORY for better performance
        cursor.execute("PRAGMA temp_store=MEMORY;")
        
        # Set cache size to 10000 pages (about 40MB)
        cursor.execute("PRAGMA cache_size=10000;")
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        print("✅ SQLite optimizations applied successfully")
    except Exception as e:
        print(f"❌ Error applying SQLite optimizations: {e}")

def setup_database():
    """Set up the database schema and initial data"""
    try:
        # Import Flask app and create application context
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
            
            # Get the database path from the app config
            db_path = app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", "")
            
            print("\nDatabase setup completed successfully!")
            return db_path
            
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def create_backup(db_path):
    """Create a backup of the database"""
    import shutil
    from datetime import datetime
    
    # Create backups directory if it doesn't exist
    os.makedirs("backups", exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"backups/fir_system_{timestamp}.db"
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backup created: {backup_path}")
    except Exception as e:
        print(f"❌ Error creating database backup: {e}")

if __name__ == "__main__":
    print("=== Intelligent FIR System - SQLite Database Setup ===\n")
    
    # Set environment variable for SQLite database
    os.environ["DATABASE_URL"] = "sqlite:///fir_system.db"
    
    # Check if database file already exists
    db_exists = os.path.exists("fir_system.db")
    if db_exists:
        print("⚠️ Database file already exists.")
        backup = input("Do you want to create a backup before proceeding? (y/n): ").lower().strip() == 'y'
        if backup:
            create_backup("fir_system.db")
    
    # Set up the database
    db_path = setup_database()
    
    # Apply SQLite optimizations
    optimize_sqlite_connection(db_path)
    
    print("\nYou can now run the application with:")
    print("python main.py")
