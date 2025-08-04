#!/usr/bin/env python3
"""
Test script to verify login functionality
"""

import requests
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_login_functionality():
    """Test the login functionality"""
    
    # Base URL for the application
    base_url = "http://localhost:5000"
    
    print("=== Testing Login Functionality ===\n")
    
    # Test 1: Check if the application is running
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ Application is running (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("❌ Application is not running. Please start the application first.")
        print("Run: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error connecting to application: {e}")
        return False
    
    # Test 2: Check login page
    try:
        response = requests.get(f"{base_url}/login", timeout=5)
        if response.status_code == 200:
            print("✅ Login page is accessible")
        else:
            print(f"❌ Login page returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing login page: {e}")
        return False
    
    # Test 3: Check register page
    try:
        response = requests.get(f"{base_url}/register", timeout=5)
        if response.status_code == 200:
            print("✅ Register page is accessible")
        else:
            print(f"❌ Register page returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing register page: {e}")
        return False
    
    # Test 4: Test login with demo credentials
    print("\n=== Testing Demo Login ===")
    
    # Test with public user
    try:
        login_data = {
            'username': 'user',
            'password': 'password'
        }
        response = requests.post(f"{base_url}/login", data=login_data, timeout=5, allow_redirects=False)
        
        if response.status_code in [302, 200]:  # Redirect or success
            print("✅ Public user login successful")
        else:
            print(f"❌ Public user login failed (Status: {response.status_code})")
            print(f"Response content: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Error testing public user login: {e}")
    
    # Test with police user
    try:
        login_data = {
            'username': 'police',
            'password': 'password'
        }
        response = requests.post(f"{base_url}/login", data=login_data, timeout=5, allow_redirects=False)
        
        if response.status_code in [302, 200]:  # Redirect or success
            print("✅ Police user login successful")
        else:
            print(f"❌ Police user login failed (Status: {response.status_code})")
            print(f"Response content: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Error testing police user login: {e}")
    
    # Test with admin user
    try:
        login_data = {
            'username': 'admin',
            'password': 'password'
        }
        response = requests.post(f"{base_url}/login", data=login_data, timeout=5, allow_redirects=False)
        
        if response.status_code in [302, 200]:  # Redirect or success
            print("✅ Admin user login successful")
        else:
            print(f"❌ Admin user login failed (Status: {response.status_code})")
            print(f"Response content: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Error testing admin user login: {e}")
    
    print("\n=== Test Summary ===")
    print("If you're still having issues, please check:")
    print("1. The application is running (python app.py)")
    print("2. You're using the correct URL (http://localhost:5000)")
    print("3. The database has demo users (run scripts/setup_sqlite_db.py if needed)")
    print("4. Check the browser console for JavaScript errors")
    print("5. Check the application logs for server-side errors")
    
    return True

if __name__ == "__main__":
    test_login_functionality() 