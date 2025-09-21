#!/usr/bin/env python3
"""
Script to check enum values in the database
"""
import os
import sys
from pathlib import Path
import psycopg2

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
from dotenv import load_dotenv
env_path = backend_dir / '.env'
load_dotenv(env_path)

def check_enum_values():
    """Check the enum values in the database"""
    
    print("=" * 60)
    print("Checking Enum Values in Database")
    print("=" * 60)
    
    try:
        # Get database URL from environment
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            print("❌ DATABASE_URL not found in environment variables")
            return False
            
        print(f"Connecting to database...")
        
        # Connect using psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        
        print("✅ Database connection successful")
        
        try:
            with conn.cursor() as cur:
                # Check test_type enum values
                cur.execute("""
                    SELECT enumlabel FROM pg_enum 
                    WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'test_type')
                    ORDER BY enumsortorder
                """)
                
                test_type_values = [row[0] for row in cur.fetchall()]
                print(f"test_type enum values: {test_type_values}")
                
                # Check priority enum values
                cur.execute("""
                    SELECT enumlabel FROM pg_enum 
                    WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'priority_level')
                    ORDER BY enumsortorder
                """)
                
                priority_values = [row[0] for row in cur.fetchall()]
                print(f"priority_level enum values: {priority_values}")
                
                # Check status enum values
                cur.execute("""
                    SELECT enumlabel FROM pg_enum 
                    WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'test_status')
                    ORDER BY enumsortorder
                """)
                
                status_values = [row[0] for row in cur.fetchall()]
                print(f"test_status enum values: {status_values}")
                
                return True
                
        finally:
            conn.close()
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_enum_values()
    sys.exit(0 if success else 1)