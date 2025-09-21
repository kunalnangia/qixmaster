import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Import the necessary modules
from app.db.session import AsyncSessionLocal
from app.models.db_models import User
from sqlalchemy.future import select

async def check_users():
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(User))
            users = result.scalars().all()
            print("Users in database:")
            for user in users:
                print(f"  User ID: {user.id}, Email: {user.email}")
        except Exception as e:
            print(f"Error checking users: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_users())