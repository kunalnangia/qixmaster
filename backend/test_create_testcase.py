import requests
import json

# Test data similar to what the frontend sends
test_data = {
    "title": "Test Case from Python Script",
    "description": "This is a test case created from a Python script",
    "test_type": "functional",
    "priority": "medium",
    "status": "draft",
    "tags": [],
    "ai_generated": False,
    "self_healing_enabled": False,
    "project_id": "default-project-id",
    "created_by": "temp-user-id"
}

# Send POST request to create test case
response = requests.post(
    "http://127.0.0.1:8001/api/v1/test-cases/",
    headers={
        "Content-Type": "application/json", 
        "Origin": "http://localhost:5175"
    },
    data=json.dumps(test_data)
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")