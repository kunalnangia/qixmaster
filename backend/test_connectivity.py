#!/usr/bin/env python3
"""
Test Backend Connectivity and Endpoints
"""
import requests
import json

def test_backend():
    """Test if backend is running and endpoints are accessible"""
    base_url = "http://127.0.0.1:8001"
    
    print("🔍 Testing Backend Connectivity")
    print("=" * 50)
    
    # Test 1: Health check
    try:
        print("1. Testing health endpoint...")
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Health endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"   ❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health endpoint error: {str(e)}")
    
    # Test 2: Projects debug endpoint
    try:
        print("\n2. Testing projects debug endpoint...")
        response = requests.get(f"{base_url}/api/projects-debug", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Projects debug endpoint working")
            print(f"   Found {data.get('count', 0)} projects")
            if data.get('projects'):
                for project in data['projects'][:3]:
                    print(f"   - {project['name']} (ID: {project['id']})")
        else:
            print(f"   ❌ Projects debug endpoint failed: {response.status_code}")
            try:
                print(f"   Error: {response.json()}")
            except:
                print(f"   Raw response: {response.text}")
    except Exception as e:
        print(f"   ❌ Projects debug endpoint error: {str(e)}")
    
    # Test 3: Projects test endpoint
    try:
        print("\n3. Testing projects test endpoint...")
        response = requests.get(f"{base_url}/api/projects-test", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Projects test endpoint working")
            print(f"   Found {len(data)} projects")
            if data:
                for project in data[:3]:
                    print(f"   - {project['name']} (ID: {project['id']})")
        else:
            print(f"   ❌ Projects test endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Projects test endpoint error: {str(e)}")
    
    # Test 4: Login endpoint
    try:
        print("\n4. Testing login endpoint...")
        login_data = {
            "email": "test@example.com",
            "password": "test1234"
        }
        response = requests.post(f"{base_url}/api/auth/login", json=login_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Login endpoint working")
            print(f"   User: {data.get('email', 'N/A')}")
            print(f"   Token: {data.get('access_token', 'N/A')[:20]}...")
        else:
            print(f"   ❌ Login endpoint failed: {response.status_code}")
            try:
                print(f"   Error: {response.json()}")
            except:
                print(f"   Raw response: {response.text}")
    except Exception as e:
        print(f"   ❌ Login endpoint error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🔧 Next Steps:")
    print("1. If backend is not running: uvicorn app.main:app --reload --host 127.0.0.1 --port 8001")
    print("2. If no projects found: python setup_database.py")
    print("3. If frontend issues persist: Check browser console")

if __name__ == "__main__":
    test_backend()