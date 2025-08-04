#!/usr/bin/env python3
"""
Test script to check login functionality and database
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from app import app, db
    from models import User, Role
    from sqlalchemy import text
    
    with app.app_context():
        print("=== Database Connection Test ===")
        
        # Check if database exists and has tables
        try:
            # Use the correct SQLAlchemy syntax
            result = db.session.execute(text("SELECT 1"))
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            sys.exit(1)
        
        # Check for users
        users = User.query.all()
        print(f"📊 Found {len(users)} users in database")
        
        for user in users:
            print(f"  - {user.username} ({user.role}) - {user.full_name}")
        
        # Test specific demo users
        demo_users = ['user', 'police', 'admin']
        demo_created = False
        
        for username in demo_users:
            user = User.query.filter_by(username=username).first()
            if user:
                print(f"✅ Demo user '{username}' exists")
                # Test password
                if user.check_password('password'):
                    print(f"✅ Password for '{username}' is correct")
                else:
                    print(f"❌ Password for '{username}' is incorrect")
            else:
                print(f"❌ Demo user '{username}' not found - creating...")
                # Create demo user
                new_user = User()
                new_user.username = username
                new_user.email = f"{username}@demo.com"
                new_user.full_name = f"Demo {username.title()} User"
                new_user.role = username  # user, police, admin
                new_user.set_password('password')
                
                db.session.add(new_user)
                demo_created = True
        
        if demo_created:
            try:
                db.session.commit()
                print("✅ Demo users created successfully")
            except Exception as e:
                print(f"❌ Failed to create demo users: {e}")
                db.session.rollback()
        
        print("\n=== Login Route Test ===")
        print("Login route should be available at: /login")
        print("Register route should be available at: /register")
        
        # Test form submission simulation
        print("\n=== Form Test ===")
        with app.test_client() as client:
            # Test GET request to login page
            response = client.get('/login')
            if response.status_code == 200:
                print("✅ Login page loads successfully")
            else:
                print(f"❌ Login page failed to load: {response.status_code}")
            
            # Test POST request to login page
            response = client.post('/login', data={
                'username': 'user',
                'password': 'password',
                'login_as': 'public'
            }, follow_redirects=True)
            
            if response.status_code == 200:
                print("✅ Login form submission works")
                if 'dashboard' in response.request.url:
                    print("✅ Redirect to dashboard successful")
                else:
                    print(f"⚠️  Redirected to: {response.request.url}")
            else:
                print(f"❌ Login form submission failed: {response.status_code}")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the project root directory")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 