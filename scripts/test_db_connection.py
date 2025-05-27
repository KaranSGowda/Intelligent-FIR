"""
Script to test the connection to the online database.
This script will:
1. Try to connect to the database
2. List the tables in the database
3. Count the number of users
"""

import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed. Please run: pip install python-dotenv")
    sys.exit(1)

# Get the database URL
db_url = os.environ.get('DATABASE_URL')
if not db_url:
    print("DATABASE_URL not found in environment variables or .env file")
    sys.exit(1)

print(f"Testing connection to: {db_url}")

try:
    from app import create_app
    from extensions import db
    from models import User, FIR, LegalSection
    from sqlalchemy import inspect
    
    app = create_app()
    
    with app.app_context():
        # Test connection
        try:
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"\n✅ Successfully connected to the database")
            print(f"Tables in database: {tables}")
            
            # Count records
            user_count = User.query.count()
            fir_count = FIR.query.count()
            section_count = LegalSection.query.count()
            
            print(f"\nDatabase statistics:")
            print(f"- Users: {user_count}")
            print(f"- FIRs: {fir_count}")
            print(f"- Legal Sections: {section_count}")
            
            # List some users if they exist
            if user_count > 0:
                users = User.query.all()
                print(f"\nUsers in database:")
                for user in users:
                    print(f"- {user.username} ({user.email}): {user.role}")
            
            print("\nDatabase connection test completed successfully!")
            
        except Exception as db_error:
            print(f"\n❌ Database connection error: {db_error}")
            import traceback
            traceback.print_exc()
            
except ImportError as e:
    print(f"Error importing required modules: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
