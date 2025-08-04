#!/usr/bin/env python3
"""
Test script to verify registration functionality
"""

import requests
import sys
import os
import time

def test_registration():
    """Test the registration functionality"""
    
    base_url = "http://localhost:5000"
    
    print("=== Testing Registration Functionality ===\n")
    
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
    
    # Test 2: Check register page
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
    
    # Test 3: Test registration with new user
    print("\n=== Testing Registration ===")
    
    # Generate unique username
    timestamp = int(time.time())
    test_username = f"testuser_{timestamp}"
    test_email = f"testuser_{timestamp}@example.com"
    
    try:
        registration_data = {
            'username': test_username,
            'email': test_email,
            'password': 'testpassword123',
            'full_name': 'Test User',
            'phone': '1234567890',
            'address': 'Test Address',
            'role': 'public'
        }
        
        print(f"Attempting to register user: {test_username}")
        response = requests.post(f"{base_url}/register", data=registration_data, timeout=5, allow_redirects=False)
        
        if response.status_code == 302:
            print("✅ Registration successful - redirect detected")
            redirect_url = response.headers.get('Location', '')
            print(f"Redirect URL: {redirect_url}")
            
            # Test login with the newly created user
            print(f"\nTesting login with newly created user: {test_username}")
            login_data = {
                'username': test_username,
                'password': 'testpassword123',
                'login_as': 'public'
            }
            
            session = requests.Session()
            response = session.post(f"{base_url}/login", data=login_data, timeout=5, allow_redirects=False)
            
            if response.status_code == 302:
                print("✅ Login with newly created user successful")
            else:
                print(f"❌ Login with newly created user failed (Status: {response.status_code})")
                
        elif response.status_code == 200:
            print("⚠️ Registration returned 200 - might be showing error page")
            if 'error' in response.text.lower() or 'already exists' in response.text.lower():
                print("❌ Registration failed - error message detected")
                print(f"Response content: {response.text[:300]}...")
            else:
                print("✅ Registration might be successful")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response content: {response.text[:300]}...")
            
    except Exception as e:
        print(f"❌ Error during registration test: {e}")
    
    print("\n=== Registration Test Complete ===")
    print("If registration is still not working, check:")
    print("1. All required fields are filled")
    print("2. Username and email are unique")
    print("3. Password meets minimum requirements (6+ characters)")
    print("4. Email format is valid")
    print("5. Browser console for JavaScript errors")
    
    return True

if __name__ == "__main__":
    test_registration() 