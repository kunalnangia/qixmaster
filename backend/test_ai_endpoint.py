#!/usr/bin/env python3
"""
Test script to verify AI URL generation endpoint with PgBouncer fixes
"""
import asyncio
import aiohttp
import json
import sys

async def test_ai_endpoint():
    """Test the AI URL generation endpoint"""
    
    api_url = "http://127.0.0.1:8001/api/ai/generate-tests-from-url"
    
    # Test payload
    payload = {
        "url": "https://example.com",
        "project_id": "test-project-pgbouncer-fix",
        "test_type": "functional",
        "priority": "medium",
        "count": 2
    }
    
    print("🧪 Testing AI URL Generation Endpoint (PgBouncer Fix)")
    print(f"📍 URL: {api_url}")
    print(f"📋 Payload: {json.dumps(payload, indent=2)}")
    print("-" * 60)
    
    try:
        timeout = aiohttp.ClientTimeout(total=60)  # 60 second timeout
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                api_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                print(f"📊 Response Status: {response.status}")
                print(f"📋 Response Headers: {dict(response.headers)}")
                
                # Try to get response text first to handle JSON parsing issues
                try:
                    response_text = await response.text()
                    print(f"📝 Raw Response: {response_text[:500]}...")
                    
                    if response.status == 200:
                        # Try to parse as JSON
                        data = json.loads(response_text)
                        print("✅ API call successful!")
                        print(f"📝 Generated {len(data)} test cases:")
                        
                        for i, test_case in enumerate(data, 1):
                            print(f"  {i}. {test_case.get('title', 'Untitled')}")
                            print(f"     Description: {test_case.get('description', 'No description')[:80]}...")
                        
                        return True
                    else:
                        # Try to parse error response as JSON
                        try:
                            error_data = json.loads(response_text)
                            print(f"❌ API Error: {error_data.get('detail', 'Unknown error')}")
                        except json.JSONDecodeError:
                            print(f"❌ Non-JSON Error Response: {response_text}")
                        return False
                        
                except Exception as e:
                    print(f"❌ Error reading response: {str(e)}")
                    return False
                    
    except asyncio.TimeoutError:
        print("❌ Request timed out")
        return False
    except aiohttp.ClientError as e:
        print(f"❌ Network error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("AI Endpoint Test with PgBouncer Fix")
    print("="*60)
    
    try:
        success = asyncio.run(test_ai_endpoint())
        
        if success:
            print("\n🎉 SUCCESS: Endpoint working correctly!")
            print("💡 The JSON parsing issue should now be fixed")
        else:
            print("\n⚠️ Issues detected - check server logs")
            
    except KeyboardInterrupt:
        print("\n⛔ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        sys.exit(1)
    
    print("="*60)