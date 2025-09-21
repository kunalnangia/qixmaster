import requests
import json

# Test the performance testing endpoint
url = "http://127.0.0.1:8002/run-performance-test"
payload = {
    "test_name": "UI Enhancement Test",
    "test_type": "load",
    "url": "https://httpbin.org/get",
    "concurrent_users": 5,
    "duration": 10,
    "ramp_up_time": 2,
    "thresholds": {
        "response_time": 1000,
        "error_rate": 1,
        "throughput": 10
    }
}

headers = {
    "Content-Type": "application/json"
}

print("Testing enhanced workflow UI enhancements...")
print(f"Sending request to: {url}")

try:
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(f"Response status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("Response received successfully!")
        print("Checking for enhanced workflow indicators...")
        
        # Check for enhanced workflow indicators
        if "enhanced_workflow" in data:
            print(f"✅ Enhanced workflow indicator found: {data['enhanced_workflow']}")
        else:
            print("❌ Enhanced workflow indicator not found")
            
        if "workflow_status" in data:
            print(f"✅ Workflow status found: {data['workflow_status']}")
        else:
            print("❌ Workflow status not found")
            
        if "ai_insights" in data:
            print(f"✅ AI insights found: {'Available' if data['ai_insights'] else 'Empty'}")
        else:
            print("❌ AI insights not found")
            
        print("\nFull response keys:", list(data.keys()))
        
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Error occurred: {e}")