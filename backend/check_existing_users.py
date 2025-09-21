#!/usr/bin/env python3
"""
Check existing users in the database
"""
import asyncio
import sys
import os
from datetime import datetime

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

async def check_existing_users():
    """Check what users already exist in the database"""
    
    print("=" * 60)
    print("Checking Existing Users")
    print("=" * 60)
    print(f"Run time: {datetime.now()}")
    print()
    
    try:
        # Import required modules
        from dotenv import load_dotenv
        load_dotenv()
        
        from app.db.session import AsyncSessionLocal
        from app.models.db_models import User
        from sqlalchemy.future import select
        
        async with AsyncSessionLocal() as session:
            # Get all users
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            print(f"Found {len(users)} users in database:")
            print()
            
            for user in users:
                print(f"ID: {user.id}")
                print(f"Email: {user.email}")
                print(f"Name: {user.full_name}")
                print(f"Role: {user.role}")
                print(f"Active: {user.is_active}")
                print(f"Created: {user.created_at}")
                print("-" * 40)
            
            return users
            
    except Exception as e:
        print(f"❌ Error checking users: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    try:
        users = asyncio.run(check_existing_users())
        sys.exit(0)
    except Exception as e:
        print(f"❌ Script execution failed: {str(e)}")
        sys.exit(1)