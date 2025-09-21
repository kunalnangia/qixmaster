#!/usr/bin/env python3
"""
Fix User Conflicts and Create testuser1@example.com
"""
import asyncio
import sys
import os
from datetime import datetime

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

async def fix_user_conflicts():
    """Fix user conflicts and create the requested user"""
    
    print("🔧 FIXING USER CONFLICTS")
    print("=" * 50)
    
    try:
        # Import required modules
        from dotenv import load_dotenv
        load_dotenv()
        
        from app.db.session import AsyncSessionLocal
        from app.models.db_models import User
        from app.core.security import get_password_hash
        from sqlalchemy.future import select
        from sqlalchemy import delete
        
        async with AsyncSessionLocal() as session:
            
            # Step 1: Check what users exist
            print("📊 Checking existing users...")
            result = await session.execute(select(User))
            existing_users = result.scalars().all()
            
            print(f"Found {len(existing_users)} users:")
            for user in existing_users:
                print(f"  - {user.email} (ID: {user.id}, Role: {user.role})")
            print()
            
            # Step 2: Fix the conflicting test@example.com user
            print("🔧 Fixing test@example.com conflict...")
            
            # Find the existing test@example.com user
            result = await session.execute(
                select(User).where(User.email == "test@example.com")
            )
            conflicting_user = result.scalars().first()
            
            if conflicting_user:
                if conflicting_user.id != "temp-user-id-for-testing":
                    print(f"  Conflict found: test@example.com exists with ID '{conflicting_user.id}'")
                    print(f"  Expected ID: 'temp-user-id-for-testing'")
                    
                    # Option 1: Update the existing user's ID
                    print("  Updating existing user to have correct ID...")
                    conflicting_user.id = "temp-user-id-for-testing"
                    conflicting_user.full_name = "Test User"
                    conflicting_user.role = "tester"
                    conflicting_user.updated_at = datetime.utcnow()
                    
                    await session.commit()
                    print("  ✅ Updated existing user to correct ID")
                else:
                    print("  ✅ test@example.com user already has correct ID")
            else:
                # Create the test user if it doesn't exist
                print("  Creating test@example.com user...")
                test_user = User(
                    id="temp-user-id-for-testing",
                    email="test@example.com",
                    full_name="Test User",
                    hashed_password=get_password_hash("test1234"),
                    role="tester",
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(test_user)
                await session.commit()
                print("  ✅ Created test@example.com user")
            print()
            
            # Step 3: Ensure AI Generator user exists
            print("🤖 Ensuring AI Generator user exists...")
            result = await session.execute(
                select(User).where(User.id == "ai-generator")
            )
            ai_user = result.scalars().first()
            
            if not ai_user:
                ai_user = User(
                    id="ai-generator",
                    email="ai-tests@example.com",
                    full_name="AI Test Generator",
                    hashed_password=get_password_hash("ai-system-user"),
                    role="system",
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(ai_user)
                await session.commit()
                print("  ✅ Created AI Generator user")
            else:
                print("  ✅ AI Generator user already exists")
            print()
            
            # Step 4: Create the requested user testuser1@example.com
            print("👤 Creating requested user testuser1@example.com...")
            
            # Check if this user already exists
            result = await session.execute(
                select(User).where(User.email == "testuser1@example.com")
            )
            existing_testuser1 = result.scalars().first()
            
            if existing_testuser1:
                print("  ⏭️  User testuser1@example.com already exists")
                print(f"     ID: {existing_testuser1.id}")
                print(f"     Name: {existing_testuser1.full_name}")
            else:
                # Create the new user
                new_user = User(
                    id="testuser1",
                    email="testuser1@example.com",
                    full_name="Test User 1",
                    hashed_password=get_password_hash("test123"),
                    role="tester",
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(new_user)
                await session.commit()
                print("  ✅ Created testuser1@example.com user")
            print()
            
            # Step 5: Verify all users are now properly created
            print("📋 Final verification...")
            result = await session.execute(select(User))
            all_users = result.scalars().all()
            
            print(f"Total users: {len(all_users)}")
            for user in all_users:
                status = "✅" if user.is_active else "❌"
                print(f"  {status} {user.full_name}")
                print(f"     Email: {user.email}")
                print(f"     ID: {user.id}")
                print(f"     Role: {user.role}")
                print()
        
        print("🎉 SUCCESS!")
        print("=" * 50)
        print("📧 Available Users:")
        print("1. Test User: test@example.com (password: test1234)")
        print("2. Test User 1: testuser1@example.com (password: test123)")
        print("3. AI Generator: ai-tests@example.com (system user)")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing users: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(fix_user_conflicts())
        if success:
            print("✅ User management completed successfully!")
            sys.exit(0)
        else:
            print("❌ User management failed!")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Script execution failed: {str(e)}")
        sys.exit(1)