#!/usr/bin/env python3
"""
Pure asyncpg user creation script - no SQLAlchemy
"""
import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import bcrypt
import asyncpg

# Load environment variables
load_dotenv()

async def create_test_users():
    """Create test users using pure asyncpg"""
    
    print("🛠️  PURE ASYNCPG USER CREATION")
    print("=" * 40)
    
    conn = None
    try:
        # Get database URL
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            raise ValueError("No DATABASE_URL found in environment variables")
        
        print(f"🔗 Connecting to: {DATABASE_URL[:50]}...")
        
        # Connect directly with asyncpg - no prepared statement caching
        conn = await asyncpg.connect(
            DATABASE_URL,
            statement_cache_size=0,  # Disable prepared statements
            command_timeout=60
        )
        
        print("✅ Database connection successful")
        
        # Test connection
        result = await conn.fetchval("SELECT 'connection_test' as test")
        print(f"🔍 Connection test result: {result}")
        
        # Hash password function
        def hash_password(password: str) -> str:
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Test user data
        users_to_create = [
            {
                'id': 'temp-user-id-for-testing',
                'email': 'test@example.com',
                'full_name': 'Test User',
                'password': 'test1234',
                'role': 'tester'
            },
            {
                'id': 'ai-generator',
                'email': 'ai-tests@example.com', 
                'full_name': 'AI Test Generator',
                'password': 'ai-system-user',
                'role': 'system'
            }
        ]
        
        for user_data in users_to_create:
            print(f"\\n👤 Creating user: {user_data['email']}")
            
            # Check if user exists
            existing_user = await conn.fetchval(
                "SELECT id FROM users WHERE id = $1",
                user_data['id']
            )
            
            if existing_user:
                print(f"   ⚠️  User already exists: {user_data['id']}")
                continue
            
            # Create user
            now = datetime.utcnow()
            hashed_password = hash_password(user_data['password'])
            
            await conn.execute(
                """
                INSERT INTO users (id, email, full_name, hashed_password, role, is_active, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                user_data['id'],
                user_data['email'],
                user_data['full_name'],
                hashed_password,
                user_data['role'],
                True,
                now,
                now
            )
            
            # Verify creation
            created_user = await conn.fetchrow(
                "SELECT id, email, role FROM users WHERE id = $1",
                user_data['id']
            )
            
            if created_user:
                print(f"   ✅ User created successfully!")
                print(f"      ID: {created_user['id']}")
                print(f"      Email: {created_user['email']}")
                print(f"      Role: {created_user['role']}")
            else:
                print(f"   ❌ User creation failed")
                return False
        
        print("\\n🎉 All users created successfully!")
        print("\\n📋 Login credentials:")
        print("   Test User: test@example.com / test1234")
        print("   AI User: ai-tests@example.com / ai-system-user")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if conn:
            await conn.close()

if __name__ == "__main__":
    try:
        success = asyncio.run(create_test_users())
        if success:
            print("\\n✅ User creation completed successfully!")
            print("🚀 You can now start the backend server")
            sys.exit(0)
        else:
            print("\\n❌ User creation failed!")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Script execution failed: {e}")
        sys.exit(1)