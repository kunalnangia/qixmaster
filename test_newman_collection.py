import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Postman API key from environment variables
postman_api_key = os.getenv('POSTMAN_API_KEY')
postman_collection_id = os.getenv('POSTMAN_COLLECTION_ID', '47463989-8d6cec84-fb64-48dc-8d71-7c2e6ba45c28')

if not postman_api_key:
    raise ValueError("POSTMAN_API_KEY environment variable is not set")

# Test the Newman endpoint with the specific collection URL mentioned
url = "http://127.0.0.1:8001/api/v1/newman/run"

# Request data with the specific collection URL and API key from environment variables
data = {
    "collection_url": f"https://api.getpostman.com/collections/{postman_collection_id}",
    "api_key": postman_api_key
}

headers = {
    "Content-Type": "application/json"
}

print("Testing Newman endpoint with specific collection...")
print(f"Collection URL: {data['collection_url']}")
print("Note: You need to provide a valid API key for this to work")

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

print("\nTo test with Docker directly, you can run:")
print(f"docker run -t postman/newman run \"https://api.getpostman.com/collections/{postman_collection_id}?apikey={postman_api_key}\"")
print("\nNote: Make sure to set the POSTMAN_API_KEY environment variable in your shell before running the Docker command:")
print(f"export POSTMAN_API_KEY='{postman_api_key}' && docker run -e POSTMAN_API_KEY=$POSTMAN_API_KEY -t postman/newman run \"https://api.getpostman.com/collections/{postman_collection_id}?apikey=$POSTMAN_API_KEY\"")