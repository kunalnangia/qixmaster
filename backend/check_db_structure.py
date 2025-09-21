#!/usr/bin/env python3
"""
Script to check database structure
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

def check_db_structure():
    """Check the database structure"""
    
    print("=" * 60)
    print("Checking Database Structure")
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
                # Check all tables
                cur.execute("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    ORDER BY table_name
                """)
                
                tables = [row[0] for row in cur.fetchall()]
                print(f"Tables in database: {tables}")
                
                # Check if test_cases table exists
                if 'test_cases' in tables:
                    print("\n--- test_cases table structure ---")
                    cur.execute("""
                        SELECT column_name, data_type, is_nullable 
                        FROM information_schema.columns 
                        WHERE table_schema = 'public' AND table_name = 'test_cases'
                        ORDER BY ordinal_position
                    """)
                    
                    columns = cur.fetchall()
                    for column in columns:
                        print(f"  {column[0]}: {column[1]} (nullable: {column[2]})")
                        
                    # Check test_type column specifically
                    cur.execute("""
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns 
                        WHERE table_schema = 'public' AND table_name = 'test_cases' AND column_name = 'test_type'
                    """)
                    
                    test_type_info = cur.fetchone()
                    if test_type_info:
                        print(f"\n  test_type column: {test_type_info[1]}")
                        if 'enum' in test_type_info[1]:
                            print("  This is an enum column")
                    
                # Check enum types
                print("\n--- Enum types ---")
                cur.execute("""
                    SELECT t.typname, e.enumlabel
                    FROM pg_type t 
                    JOIN pg_enum e ON t.oid = e.enumtypid  
                    JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
                    WHERE n.nspname = 'public'
                    ORDER BY t.typname, e.enumsortorder
                """)
                
                enum_rows = cur.fetchall()
                enums = {}
                for typname, enumlabel in enum_rows:
                    if typname not in enums:
                        enums[typname] = []
                    enums[typname].append(enumlabel)
                
                for typname, values in enums.items():
                    print(f"  {typname}: {values}")
                
                return True
                
        finally:
            conn.close()
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_db_structure()
    sys.exit(0 if success else 1)