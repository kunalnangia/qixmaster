import asyncio
import sys
import os
import uuid
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Import the necessary modules
from app.db.session import AsyncSessionLocal
from app.models.db_models import User, Project, TestCase
from sqlalchemy.future import select
from sqlalchemy import text

async def create_test_data():
    async with AsyncSessionLocal() as db:
        try:
            # Check if test user exists
            result = await db.execute(
                select(User).where(User.email == "test@example.com")
            )
            user = result.scalars().first()
            
            if not user:
                # Create test user
                user = User(
                    id="temp-test-user-id",
                    email="test@example.com",
                    full_name="Test User",
                    hashed_password="fake_hashed_password",
                    role="tester",
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                db.add(user)
                print("Created test user")
            else:
                print("Test user already exists")
            
            # Check if default project exists
            result = await db.execute(
                select(Project).where(Project.id == "default-project-id")
            )
            project = result.scalars().first()
            
            if not project:
                # Create default project
                project = Project(
                    id="default-project-id",
                    name="Default Test Project",
                    description="Default project for testing",
                    created_by="temp-test-user-id",
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                db.add(project)
                print("Created default project")
            else:
                print("Default project already exists")
            
            # Commit changes
            await db.commit()
            print("Test data created successfully")
            
        except Exception as e:
            await db.rollback()
            print(f"Error creating test data: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_test_data())