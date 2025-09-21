#!/usr/bin/env python3
"""
Script to generate test cases from google.com using the API
"""
import requests
import json
from datetime import datetime

def generate_google_test_cases():
    """Generate test cases from google.com using the API endpoint"""
    
    print("=" * 60)
    print("Generating Test Cases from Google.com using API")
    print("=" * 60)
    print(f"Run time: {datetime.now()}")
    print()
    
    # API endpoint
    url = "http://127.0.0.1:8001/api/v1/test-cases/generate-from-url"
    
    # Request payload
    payload = {
        "url": "https://www.google.com",
        "project_id": "default-project-id",
        "test_count": 10  # Maximum allowed by the API
    }
    
    print(f"Sending request to {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        # Send request to API
        response = requests.post(url, json=payload)
        
        # Check if request was successful
        if response.status_code == 200 or response.status_code == 201:
            print("Request successful!")
            result = response.json()
            
            # Print summary of generated test cases
            test_cases = result.get("generated_test_cases", [])
            print(f"Generated {len(test_cases)} test cases:")
            
            # Group by test type
            test_types = {}
            for tc in test_cases:
                test_type = tc.get("test_type", "functional")
                if test_type not in test_types:
                    test_types[test_type] = []
                test_types[test_type].append(tc)
            
            # Print summary by test type
            for test_type, cases in test_types.items():
                print(f"- {test_type}: {len(cases)} test cases")
                
                # Print titles of each test case
                for i, tc in enumerate(cases):
                    print(f"  {i+1}. {tc.get('title')}")
            
            print()
            print("Test case generation completed successfully!")
            print("You can now view the test cases in the UI")
            return True
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return False
    
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    generate_google_test_cases()