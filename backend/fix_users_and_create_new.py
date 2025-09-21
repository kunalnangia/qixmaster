#!/usr/bin/env python3
"""
Comprehensive User Management - Fix conflicts and create requested user
"""
import asyncio
import sys
import os
from datetime import datetime

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

async def manage_users():
    """Manage users - check existing, resolve conflicts, create new"""
    
    print("=" * 70)
    print("🔧 USER MANAGEMENT & CONFLICT RESOLUTION")
    print("=" * 70)
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
        from sqlalchemy import delete
        
        async with AsyncSessionLocal() as session:
            
            # Step 1: Check existing users
            print("[1] 📊 Checking existing users...")
            result = await session.execute(select(User))
            existing_users = result.scalars().all()
            
            print(f"   Found {len(existing_users)} users:")
            for user in existing_users:
                print(f"   - ID: {user.id} | Email: {user.email} | Name: {user.full_name}")
            print()
            
            # Step 2: Clean up conflicting users if needed
            print("[2] 🧹 Resolving conflicts...")
            
            # Check for the problematic test@example.com user
            result = await session.execute(
                select(User).where(User.email == "test@example.com")
            )
            existing_test_user = result.scalars().first()
            
            if existing_test_user and existing_test_user.id != "temp-user-id-for-testing":
                print(f"   ⚠️  Conflict found: test@example.com exists with ID '{existing_test_user.id}'")
                print(f"   🗑️  Removing conflicting user...")
                await session.delete(existing_test_user)
                await session.commit()
                print(f"   ✅ Removed conflicting user")
            else:
                print(f"   ✅ No conflicts found")
            print()
            
            # Step 3: Create required system users
            print("[3] 👥 Creating required system users...")
            
            users_to_create = [
                {
                    "id": "temp-user-id-for-testing",
                    "email": "test@example.com",
                    "full_name": "Test User",
                    "password": "test1234",
                    "role": "tester"
                },
                {
                    "id": "ai-generator",
                    "email": "ai-tests@example.com", 
                    "full_name": "AI Test Generator",
                    "password": "ai-system-user",
                    "role": "system"
                }
            ]
            
            created_count = 0
            for user_data in users_to_create:
                # Check if user exists
                result = await session.execute(
                    select(User).where(User.id == user_data["id"])
                )
                existing = result.scalars().first()
                
                if not existing:
                    user = User(
                        id=user_data["id"],
                        email=user_data["email"],
                        full_name=user_data["full_name"],
                        hashed_password=get_password_hash(user_data["password"]),
                        role=user_data["role"],
                        is_active=True,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    session.add(user)
                    created_count += 1
                    print(f"   ✅ Created: {user_data['full_name']} ({user_data['email']})")
                else:
                    print(f"   ⏭️  Already exists: {user_data['full_name']}")
            
            # Step 4: Create the requested user
            print()
            print("[4] 🆕 Creating requested user...")
            
            requested_user_data = {
                "id": "testuser1",
                "email": "testuser1@example.com",
                "full_name": "Test User 1",
                "password": "test123",
                "role": "tester"
            }
            
            # Check if requested user exists
            result = await session.execute(
                select(User).where(User.email == requested_user_data["email"])
            )
            existing_requested = result.scalars().first()
            
            if not existing_requested:
                requested_user = User(
                    id=requested_user_data["id"],
                    email=requested_user_data["email"],
                    full_name=requested_user_data["full_name"],
                    hashed_password=get_password_hash(requested_user_data["password"]),
                    role=requested_user_data["role"],
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(requested_user)
                created_count += 1
                print(f"   ✅ Created requested user: {requested_user_data['full_name']} ({requested_user_data['email']})")
            else:
                print(f"   ⏭️  Requested user already exists: {requested_user_data['email']}")
            
            # Step 5: Commit all changes
            if created_count > 0:
                await session.commit()
                print(f"\n[SUCCESS] ✅ Created {created_count} new users!")
            else:
                print(f"\n[INFO] ℹ️  All users already exist")
            
            # Step 6: Final verification
            print()
            print("[5] 🔍 Final user list:")
            result = await session.execute(select(User))
            final_users = result.scalars().all()
            
            for i, user in enumerate(final_users, 1):
                print(f"   {i}. {user.full_name}")
                print(f"      ID: {user.id}")
                print(f"      Email: {user.email}")
                print(f"      Role: {user.role}")
                print(f"      Active: {user.is_active}")
                print()
        
        print("=" * 70)
        print("🎉 USER MANAGEMENT COMPLETE!")
        print()
        print("📋 Available Login Credentials:")
        print("1. Test User:")
        print("   Email: test@example.com")
        print("   Password: test1234")
        print()
        print("2. Test User 1 (Requested):")
        print("   Email: testuser1@example.com")
        print("   Password: test123")
        print()
        print("3. AI Generator (System):")
        print("   Email: ai-tests@example.com")
        print("   Role: system")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"❌ Error managing users: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(manage_users())
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"❌ Script execution failed: {str(e)}")
        sys.exit(1)