#!/usr/bin/env python3
"""
Simple Debug Script
"""
import asyncio
import sys
import os

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

print("Starting debug script...")

try:
    from dotenv import load_dotenv
    print("✅ dotenv imported")
    load_dotenv()
    print("✅ .env loaded")
    
    from app.db.session import AsyncSessionLocal
    print("✅ AsyncSessionLocal imported")
    
    from app.models.db_models import User
    print("✅ User model imported")
    
    from app.core.security import get_password_hash
    print("✅ Security functions imported")
    
    async def test_db():
        print("Testing database connection...")
        async with AsyncSessionLocal() as session:
            print("✅ Database session created")
            
            from sqlalchemy.future import select
            result = await session.execute(select(User))
            users = result.scalars().all()
            print(f"✅ Found {len(users)} users in database")
            
            for user in users:
                print(f"   - {user.email} (ID: {user.id})")
    
    print("Running async test...")
    asyncio.run(test_db())
    print("✅ All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()