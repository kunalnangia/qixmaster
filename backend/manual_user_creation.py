#!/usr/bin/env python3
"""
Manual user creation script to bypass startup issues
"""
import asyncio
import sys
import os
from datetime import datetime

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

async def create_users_manually():
    """Create test users manually with comprehensive pgbouncer compatibility"""
    
    print("🛠️  MANUAL USER CREATION")
    print("=" * 40)
    
    async_engine = None  # Initialize to None
    
    try:
        # Load environment
        from dotenv import load_dotenv
        load_dotenv()
        
        # Import required modules
        from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
        from sqlalchemy.pool import NullPool  # Add NullPool import
        from app.models.db_models import User
        from app.core.security import get_password_hash
        from sqlalchemy.future import select
        import uuid
        
        # Get database URL and modify for pgbouncer compatibility
        DATABASE_URL_ASYNC = os.getenv("DATABASE_URL_ASYNC") or os.getenv("DATABASE_URL")
        if not DATABASE_URL_ASYNC:
            raise ValueError("No DATABASE_URL or DATABASE_URL_ASYNC found in environment variables")
        
        # Ensure we use asyncpg driver and add comprehensive pgbouncer parameters
        if not DATABASE_URL_ASYNC.startswith("postgresql+asyncpg://"):
            DATABASE_URL_ASYNC = DATABASE_URL_ASYNC.replace("postgresql://", "postgresql+asyncpg://")
        
        # Add comprehensive pgbouncer compatibility parameters
        pgbouncer_params = [
            "statement_cache_size=0",
            "prepared_statement_cache_size=0"
        ]
        
        # Check which parameters are already in the URL and add missing ones
        for param in pgbouncer_params:
            if param not in DATABASE_URL_ASYNC:
                separator = "&" if "?" in DATABASE_URL_ASYNC else "?"
                DATABASE_URL_ASYNC += f"{separator}{param}"
                separator = "&"  # subsequent parameters use &
        
        # Also ensure the parameters are in the original DATABASE_URL for consistency
        DATABASE_URL = os.getenv("DATABASE_URL")
        if DATABASE_URL:
            for param in pgbouncer_params:
                if param not in DATABASE_URL:
                    separator = "&" if "?" in DATABASE_URL else "?"
                    DATABASE_URL += f"{separator}{param}"
        
        print(f"🔗 Using database connection with comprehensive pgbouncer compatibility")
        
        # Create async engine with comprehensive pgbouncer compatibility
        # Let PgBouncer do pooling by using NullPool and disable all caches
        async_engine = create_async_engine(
            DATABASE_URL_ASYNC,
            echo=False,
            poolclass=NullPool,  # Let PgBouncer do pooling instead of SQLAlchemy
            connect_args={
                "statement_cache_size": 0,  # Disable prepared statements
                "prepared_statement_cache_size": 0,  # Additional asyncpg parameter
            },
            # Disable compiled query cache at SQLAlchemy level
            execution_options={
                "compiled_cache": None,  # Disable compiled query cache
            }
        )
        
        # Create session factory
        AsyncSessionLocal = async_sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        async with AsyncSessionLocal() as session:
            print("✅ Database connection successful")
            
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
                print(f"\n👤 Creating user: {user_data['email']}")
                
                # Check if user exists
                result = await session.execute(
                    select(User).where(User.id == user_data['id'])
                )
                existing_user = result.scalars().first()
                
                if existing_user:
                    print(f"   ⚠️  User already exists: {user_data['id']}")
                    continue
                
                # Create user using constructor pattern (proper SQLAlchemy approach)
                new_user = User(
                    id=str(user_data['id']),
                    email=str(user_data['email']),
                    full_name=str(user_data['full_name']),
                    hashed_password=get_password_hash(user_data['password']),
                    role=str(user_data['role']),
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                session.add(new_user)
                await session.commit()
                
                # Verify creation
                result = await session.execute(
                    select(User).where(User.id == user_data['id'])
                )
                created_user = result.scalars().first()
                
                if created_user:
                    print(f"   ✅ User created successfully!")
                    print(f"      ID: {created_user.id}")
                    print(f"      Email: {created_user.email}")
                    print(f"      Role: {created_user.role}")
                else:
                    print(f"   ❌ User creation failed")
                    return False
            
            print("\n🎉 All users created successfully!")
            print("\n📋 Login credentials:")
            print("   Test User: test@example.com / test1234")
            print("   AI User: ai-tests@example.com / ai-system-user")
            
        # Clean up async engine
        if async_engine:
            await async_engine.dispose()
        return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
        # Clean up async engine in case of error
        try:
            if async_engine:
                await async_engine.dispose()
        except:
            pass  # Ignore cleanup errors
            
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(create_users_manually())
        if success:
            print("\n✅ User creation completed successfully!")
            print("🚀 Now restart the backend server")
            sys.exit(0)
        else:
            print("\n❌ User creation failed!")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Script execution failed: {e}")
        sys.exit(1)