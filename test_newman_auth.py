import requests
import json

# First, let's login to get an access token
login_url = "http://127.0.0.1:8001/api/v1/auth/login"

# You'll need to use actual credentials here
login_data = {
    "username": "test@example.com",
    "password": "testpassword"
}

try:
    # Login
    login_response = requests.post(login_url, data=login_data)
    print(f"Login Status Code: {login_response.status_code}")
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        print(f"Login Response: {login_result}")
        
        # Extract the access token
        access_token = login_result.get("access_token")
        
        if access_token:
            # Now test the Newman endpoint with the access token
            newman_url = "http://127.0.0.1:8001/api/v1/newman/run"
            
            # Sample request data (you'll need to replace with actual values)
            newman_data = {
                "collection_url": "https://api.getpostman.com/collections/12345678-1234-1234-1234-123456789012",
                "api_key": "PMAK-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
            
            newman_response = requests.post(newman_url, headers=headers, json=newman_data)
            print(f"Newman Status Code: {newman_response.status_code}")
            print(f"Newman Response: {newman_response.json()}")
        else:
            print("Failed to get access token")
    else:
        print(f"Login failed: {login_response.text}")
        
except Exception as e:
    print(f"Error: {e}")