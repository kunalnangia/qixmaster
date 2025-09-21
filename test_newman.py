import requests
import json

# Test the Newman endpoint
url = "http://127.0.0.1:8001/api/v1/newman/run"

# Sample request data (you'll need to replace with actual values)
data = {
    "collection_url": "https://api.getpostman.com/collections/12345678-1234-1234-1234-123456789012",
    "api_key": "PMAK-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
}

headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")