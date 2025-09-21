import requests
import json

# Test the Newman endpoint
url = "http://127.0.0.1:8001/api/v1/newman/run"

# Sample request data with a public collection
data = {
    "collection_url": "https://www.getpostman.com/collections/8a0c0cb484c3b7be06d6",
    "api_key": "test"
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