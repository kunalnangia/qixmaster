#!/usr/bin/env python3
"""
Standalone user creation script - completely isolated from main application
"""
import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import bcrypt

# Load environment variables
load_dotenv()

async def create_test_users():
    """Create test users with completely isolated database connection"""
    
    print("🛠️  STANDALONE USER CREATION")
    print("=" * 40)
    
    engine = None
    
    try:
        # Direct imports to avoid main app conflicts
        from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
        from sqlalchemy import Column, String, Boolean, DateTime, text
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.future import select
        
        # Get database URL
        DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("DATABASE_URL_ASYNC")
        if not DATABASE_URL:
            raise ValueError("No DATABASE_URL found in environment variables")
        
        # Ensure asyncpg driver
        if not DATABASE_URL.startswith("postgresql+asyncpg://"):
            DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        
        # Add PgBouncer compatibility parameters
        if "statement_cache_size=0" not in DATABASE_URL:
            separator = "&" if "?" in DATABASE_URL else "?"
            DATABASE_URL += f"{separator}statement_cache_size=0"
        
        print(f"🔗 Connecting to: {DATABASE_URL[:50]}...")
        
        # Create completely isolated async engine
        engine = create_async_engine(
            DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
            pool_size=1,
            max_overflow=0,
            pool_recycle=300,
            connect_args={
                "statement_cache_size": 0,
                "prepared_statement_cache_size": 0,
                "command_timeout": 60
            },
            execution_options={
                "compiled_cache": None,
                "autocommit": False,
            }
        )
        
        # Create session factory
        AsyncSessionLocal = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Define minimal User model for this script only
        Base = declarative_base()
        
        class User(Base):
            __tablename__ = "users"
            
            id = Column(String, primary_key=True)
            email = Column(String, unique=True, index=True, nullable=False)
            full_name = Column(String, nullable=False)
            hashed_password = Column(String, nullable=False)
            role = Column(String, default="tester")
            is_active = Column(Boolean, default=True)
            created_at = Column(DateTime)
            updated_at = Column(DateTime)
        
        # Hash passwords with bcrypt
        def hash_password(password: str) -> str:
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        async with AsyncSessionLocal() as session:
            print("✅ Database connection successful")
            
            # Test basic connection
            result = await session.execute(text("SELECT 'connection_test' as test"))
            test_value = result.scalar()
            print(f"🔍 Connection test result: {test_value}")
            
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
                result = await session.execute(
                    text("SELECT id FROM users WHERE id = :user_id"),
                    {"user_id": user_data['id']}
                )
                existing_user = result.scalar()
                
                if existing_user:
                    print(f"   ⚠️  User already exists: {user_data['id']}")
                    continue
                
                # Create user with raw SQL to avoid ORM prepared statement issues
                now = datetime.utcnow()
                hashed_password = hash_password(user_data['password'])
                
                await session.execute(
                    text("""
                        INSERT INTO users (id, email, full_name, hashed_password, role, is_active, created_at, updated_at)
                        VALUES (:id, :email, :full_name, :hashed_password, :role, :is_active, :created_at, :updated_at)
                    """),
                    {
                        'id': user_data['id'],
                        'email': user_data['email'],
                        'full_name': user_data['full_name'],
                        'hashed_password': hashed_password,
                        'role': user_data['role'],
                        'is_active': True,
                        'created_at': now,
                        'updated_at': now
                    }
                )
                
                await session.commit()
                
                # Verify creation
                result = await session.execute(
                    text("SELECT id, email, role FROM users WHERE id = :user_id"),
                    {"user_id": user_data['id']}
                )
                created_user = result.first()
                
                if created_user:
                    print(f"   ✅ User created successfully!")
                    print(f"      ID: {created_user[0]}")
                    print(f"      Email: {created_user[1]}")
                    print(f"      Role: {created_user[2]}")
                else:
                    print(f"   ❌ User creation failed")
                    return False
            
            print("\\n🎉 All users created successfully!")
            print("\\n📋 Login credentials:")
            print("   Test User: test@example.com / test1234")
            print("   AI User: ai-tests@example.com / ai-system-user")
            
        # Clean up
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
        # Clean up on error
        try:
            if engine is not None:
                await engine.dispose()
        except:
            pass
            
        return False

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