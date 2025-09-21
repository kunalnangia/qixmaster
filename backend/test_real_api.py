#!/usr/bin/env python3
"""
Test the login API endpoint directly with the correct password
"""

import requests
import json

def test_api_login():
    """Test the actual API login endpoint"""
    
    # API endpoint
    url = "http://127.0.0.1:8001/api/auth/login"
    
    # Login data with the correct password we discovered
    login_data = {
        "email": "testuser1@example.com",
        "password": "test123"  # This is the correct password
    }
    
    print("=== Testing API Login Endpoint ===")
    print(f"URL: {url}")
    print(f"Email: {login_data['email']}")
    print(f"Password: {login_data['password']}")
    
    try:
        # Make the request
        response = requests.post(url, json=login_data, timeout=30)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ LOGIN SUCCESSFUL!")
            print(f"Token Type: {result.get('token_type')}")
            print(f"Access Token: {result.get('access_token', 'N/A')[:50]}...")
            print(f"User Email: {result.get('user', {}).get('email')}")
            print(f"User ID: {result.get('user', {}).get('id')}")
            print(f"User Role: {result.get('user', {}).get('role')}")
        else:
            print(f"\n❌ LOGIN FAILED!")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Response Text: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Could not connect to {url}")
        print("Make sure the backend server is running on port 8001")
    except requests.exceptions.Timeout:
        print(f"\n❌ Request timed out")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    test_api_login()