#!/usr/bin/env python3
"""
Direct database script to create a performance test case for https://hostbooks.com
"""
import os
import sys
from pathlib import Path
import psycopg2
import uuid
from datetime import datetime
import json

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
from dotenv import load_dotenv
env_path = backend_dir / '.env'
load_dotenv(env_path)

def create_hostbooks_test_case():
    """Create a performance test case for https://hostbooks.com using direct psycopg2"""
    
    print("=" * 60)
    print("Creating Performance Test Case for HostBooks.com")
    print("=" * 60)
    
    try:
        # Get database URL from environment
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            print("❌ DATABASE_URL not found in environment variables")
            return False
            
        print(f"Connecting to database...")
        print(f"Database URL: {DATABASE_URL[:60]}...")
        
        # Parse the DATABASE_URL to extract connection parameters
        # Format: postgresql://user:password@host:port/database
        import re
        match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', DATABASE_URL)
        if not match:
            print("❌ Invalid DATABASE_URL format")
            return False
            
        user, password, host, port, database = match.groups()
        
        # Connect using psycopg2
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        
        print("✅ Database connection successful")
        
        try:
            with conn.cursor() as cur:
                # Check if the test case already exists
                cur.execute("""
                    SELECT id FROM test_cases 
                    WHERE title = %s AND project_id = %s
                """, ("HostBooks Performance Test", "default-project-id"))
                
                existing_case = cur.fetchone()
                
                if existing_case:
                    print(f"✅ Test case already exists with ID: {existing_case[0]}")
                    return True
                
                # Check if default project exists
                cur.execute("""
                    SELECT id FROM projects WHERE id = %s
                """, ("default-project-id",))
                
                project_exists = cur.fetchone()
                
                if not project_exists:
                    # Create default project
                    now = datetime.utcnow()
                    cur.execute("""
                        INSERT INTO projects (id, name, description, created_by, is_active, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        "default-project-id",
                        "Default Project",
                        "Default project for test case generation",
                        "ai-generator",  # Using the AI generator user ID
                        True,
                        now,
                        now
                    ))
                    print("✅ Created default project")
                
                # Create the test case
                test_case_id = str(uuid.uuid4())
                now = datetime.utcnow()
                
                test_data = {
                    "url": "https://hostbooks.com",
                    "test_parameters": {
                        "concurrent_users": 10,
                        "duration": 60,
                        "ramp_up_time": 10
                    }
                }
                
                cur.execute("""
                    INSERT INTO test_cases 
                    (id, title, description, project_id, test_type, priority, status, 
                     expected_result, created_by, ai_generated, self_healing_enabled, 
                     prerequisites, test_data, created_at, updated_at)
                    VALUES 
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    test_case_id,
                    "HostBooks Performance Test",
                    "Performance test case for https://hostbooks.com to evaluate loading times, response times, and overall performance metrics",
                    "default-project-id",
                    "performance",
                    "high",
                    "active",
                    "Page loads within acceptable time limits with minimal errors",
                    "ai-generator",
                    True,
                    True,
                    "Ensure HostBooks website is accessible",
                    json.dumps(test_data),
                    now,
                    now
                ))
                
                conn.commit()
                print("✅ Performance test case created successfully")
                print(f"   Test Case ID: {test_case_id}")
                print("   You can now select this test case in the performance tab dropdown.")
                
                return True
                
        finally:
            conn.close()
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_hostbooks_test_case()
    sys.exit(0 if success else 1)