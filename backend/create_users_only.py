#!/usr/bin/env python3
"""
Create Required Users Only
"""
import asyncio
import sys
import os
from datetime import datetime

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

async def create_required_users():
    """Create only the required system users"""
    
    print("=" * 60)
    print("Creating Required Users")
    print("=" * 60)
    print(f"Run time: {datetime.now()}")
    print()
    
    try:
        # Import required modules
        from dotenv import load_dotenv
        load_dotenv()
        
        from app.db.session import AsyncSessionLocal
        from app.models.db_models import User
        from app.core.security import get_password_hash
        from sqlalchemy.future import select
        
        print("[1] Creating system users...")
        
        # User constants
        TEST_USER_ID = "temp-user-id-for-testing"
        TEST_USER_EMAIL = "test@example.com"
        TEST_USER_NAME = "Test User"
        
        AI_GENERATOR_USER_ID = "ai-generator"
        AI_GENERATOR_EMAIL = "ai-tests@example.com"
        AI_GENERATOR_NAME = "AI Test Generator"
        
        async with AsyncSessionLocal() as session:
            users_created = 0
            
            # Create test user
            result = await session.execute(select(User).where(User.id == TEST_USER_ID))
            existing_user = result.scalars().first()
            
            if not existing_user:
                test_user = User(
                    id=TEST_USER_ID,
                    email=TEST_USER_EMAIL,
                    full_name=TEST_USER_NAME,
                    hashed_password=get_password_hash("test1234"),
                    role="tester",
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(test_user)
                users_created += 1
                print(f"   ✅ Test User: {TEST_USER_ID}")
            else:
                print(f"   ⏭️  Test User already exists: {TEST_USER_ID}")
            
            # Create AI Generator user
            result = await session.execute(select(User).where(User.id == AI_GENERATOR_USER_ID))
            existing_ai_user = result.scalars().first()
            
            if not existing_ai_user:
                ai_user = User(
                    id=AI_GENERATOR_USER_ID,
                    email=AI_GENERATOR_EMAIL,
                    full_name=AI_GENERATOR_NAME,
                    hashed_password=get_password_hash("ai-system-user"),
                    role="system",
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(ai_user)
                users_created += 1
                print(f"   ✅ AI Generator User: {AI_GENERATOR_USER_ID}")
            else:
                print(f"   ⏭️  AI Generator User already exists: {AI_GENERATOR_USER_ID}")
            
            # Commit all users
            if users_created > 0:
                await session.commit()
                print(f"\n[SUCCESS] Created {users_created} new users!")
            else:
                print(f"\n[INFO] All required users already exist.")
        
        print("=" * 60)
        print("✅ USER CREATION COMPLETE!")
        print()
        print("Available Users:")
        print(f"1. Test User")
        print(f"   ID: {TEST_USER_ID}")
        print(f"   Email: {TEST_USER_EMAIL}")
        print(f"   Password: test1234")
        print()
        print(f"2. AI Generator User")
        print(f"   ID: {AI_GENERATOR_USER_ID}")
        print(f"   Email: {AI_GENERATOR_EMAIL}")
        print(f"   Role: system")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating users: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(create_required_users())
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"❌ Script execution failed: {str(e)}")
        sys.exit(1)