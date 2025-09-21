import requests
import time

def test_backend():
    """Test if the backend is responding"""
    try:
        print("Testing backend connection...")
        response = requests.get("http://127.0.0.1:8001/health", timeout=5)
        print(f"Backend is responding! Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return True
    except requests.exceptions.ConnectionError:
        print("Backend is not responding - connection error")
        return False
    except requests.exceptions.Timeout:
        print("Backend is not responding - timeout")
        return False
    except Exception as e:
        print(f"Backend test failed with error: {e}")
        return False

if __name__ == "__main__":
    # Wait a few seconds for the server to start
    print("Waiting for server to start...")
    time.sleep(5)
    
    # Test the backend
    success = test_backend()
    
    if not success:
        print("Backend is not accessible. Please check if the server is running.")
    else:
        print("Backend is accessible!")