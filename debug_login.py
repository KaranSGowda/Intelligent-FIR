#!/usr/bin/env python3
"""
Debug script for login issues
"""

import requests
import sys
import os

def debug_login():
    """Debug login functionality step by step"""
    
    base_url = "http://localhost:5000"
    
    print("=== Login Debug Script ===\n")
    
    # Test 1: Check if app is running
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ App is running (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ App not running: {e}")
        print("Please start the app with: python app.py")
        return
    
    # Test 2: Get login page and check for CSRF token
    try:
        response = requests.get(f"{base_url}/login", timeout=5)
        print(f"✅ Login page accessible (Status: {response.status_code})")
        
        # Check if page contains expected elements
        content = response.text
        if 'username' in content and 'password' in content:
            print("✅ Login form elements found")
        else:
            print("❌ Login form elements missing")
            
    except Exception as e:
        print(f"❌ Error accessing login page: {e}")
        return
    
    # Test 3: Test login with session
    session = requests.Session()
    
    try:
        # First get the login page to establish session
        response = session.get(f"{base_url}/login", timeout=5)
        print("✅ Session established")
        
        # Test login with demo user
        login_data = {
            'username': 'user',
            'password': 'password',
            'login_as': 'public'
        }
        
        print("\nAttempting login with demo user...")
        response = session.post(f"{base_url}/login", data=login_data, timeout=5, allow_redirects=False)
        
        print(f"Login response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            print("✅ Login successful - redirect detected")
            redirect_url = response.headers.get('Location', '')
            print(f"Redirect URL: {redirect_url}")
            
            # Follow redirect
            response = session.get(f"{base_url}{redirect_url}", timeout=5)
            print(f"After redirect status: {response.status_code}")
            
        elif response.status_code == 200:
            print("⚠️ Login returned 200 - might be showing error page")
            if 'error' in response.text.lower() or 'incorrect' in response.text.lower():
                print("❌ Login failed - error message detected")
            else:
                print("✅ Login might be successful")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during login test: {e}")
    
    print("\n=== Debug Complete ===")
    print("If login is still not working, check:")
    print("1. Browser console for JavaScript errors")
    print("2. Application logs in the terminal")
    print("3. Network tab in browser dev tools")
    print("4. Try different browser or incognito mode")

if __name__ == "__main__":
    debug_login() 