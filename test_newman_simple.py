import requests
import json

# Test the Newman endpoint
url = "http://127.0.0.1:8001/api/v1/newman/run"

# Sample request data
data = {
    "collection_url": "https://postman-echo.com/get?foo1=bar1&foo2=bar2",
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