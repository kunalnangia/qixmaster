import requests
from dotenv import load_dotenv
import os

def test_supabase_tables():
    # Load environment variables
    load_dotenv()
    
    # Supabase configuration
    SUPABASE_URL = "https://lflecyuvttemfoyixngi.supabase.co/rest/v1/"
    
    # Get Supabase key from environment variables
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    if not SUPABASE_KEY:
        raise ValueError("SUPABASE_KEY environment variable is not set")
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}'
    }
    
    print("Testing Supabase Tables...")
    
    # List of tables to check
    tables_to_check = [
        'users', 'test_runs', 'test_cases',
        'test_suites', 'test_executions', 'test_results'
    ]
    
    for table in tables_to_check:
        try:
            print(f"\nChecking table: {table}")
            response = requests.get(
                f"{SUPABASE_URL}{table}?select=*&limit=1",
                headers=headers
            )
            
            if response.status_code == 200:
                print(f"✅ Table '{table}' exists and is accessible")
                data = response.json()
                if data:
                    print(f"   First row columns: {', '.join(data[0].keys())}")
            else:
                print(f"❌ Table '{table}' not found or not accessible")
                print(f"   Status code: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ Error accessing table '{table}': {str(e)}")
    
    print("\nTest completed.")

if __name__ == "__main__":
    test_supabase_tables()
