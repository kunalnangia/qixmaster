import asyncio
import aiohttp
import json

async def test_ai_url_generation():
    """Test the AI URL generation API endpoint"""
    
    api_url = "http://127.0.0.1:8001/api/ai/generate-tests-from-url"
    
    # Test payload matching the user's request
    payload = {
        "url": "https://hostbooks.com",
        "project_id": "test-project-id",
        "test_type": "functional",
        "priority": "medium", 
        "count": 2
    }
    
    print("🧪 Testing AI URL Generation API...")
    print(f"📍 URL: {api_url}")
    print(f"📋 Payload: {json.dumps(payload, indent=2)}")
    print("-" * 50)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                api_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                print(f"📊 Response Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print("✅ API call successful!")
                    print(f"📝 Generated {len(data)} test cases:")
                    
                    for i, test_case in enumerate(data, 1):
                        print(f"  {i}. {test_case.get('title', 'Untitled')}")
                        print(f"     Description: {test_case.get('description', 'No description')[:100]}...")
                    
                    return True
                    
                else:
                    error_text = await response.text()
                    print(f"❌ API call failed with status {response.status}")
                    print(f"📋 Error response: {error_text}")
                    return False
                    
    except aiohttp.ClientConnectorError:
        print("❌ Could not connect to the server.")
        print("💡 Make sure the FastAPI server is running on port 8001")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("="*60)
    print("AI URL Generation API Test")
    print("="*60)
    
    success = asyncio.run(test_ai_url_generation())
    
    if success:
        print("\n🎉 SUCCESS: AI URL generation is working correctly!")
    else:
        print("\n⚠️  The API test failed. Check the server logs for more details.")
    
    print("="*60)