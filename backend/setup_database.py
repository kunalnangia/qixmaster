#!/usr/bin/env python3
"""
Setup Database with Users and Projects
"""
import asyncio
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def setup_database():
    """Setup database with test users and projects"""
    print("🔧 Setting up database...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        from app.db.session import AsyncSessionLocal
        from app.models.db_models import Project, User
        from app.core.security import get_password_hash
        from sqlalchemy.future import select
        
        async with AsyncSessionLocal() as session:
            
            # Create test user
            print("Creating test user...")
            test_user_id = "temp-user-id-for-testing"
            
            result = await session.execute(select(User).where(User.id == test_user_id))
            test_user = result.scalars().first()
            
            if not test_user:
                test_user = User(
                    id=test_user_id,
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
                print("✅ Test user created")
            else:
                print("✅ Test user exists")
            
            # Create projects
            print("Creating projects...")
            projects_data = [
                {
                    "id": "project-1",
                    "name": "E-Commerce Testing",
                    "description": "Testing for e-commerce platform"
                },
                {
                    "id": "project-2", 
                    "name": "Banking Application Tests",
                    "description": "Banking application testing"
                },
                {
                    "id": "project-3",
                    "name": "Social Media Platform",
                    "description": "Social media features testing"
                }
            ]
            
            for project_data in projects_data:
                result = await session.execute(select(Project).where(Project.id == project_data["id"]))
                existing_project = result.scalars().first()
                
                if not existing_project:
                    project = Project(
                        id=project_data["id"],
                        name=project_data["name"],
                        description=project_data["description"],
                        created_by=test_user_id,
                        is_active=True,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    session.add(project)
                    print(f"✅ Created: {project_data['name']}")
                else:
                    print(f"⏭️  Exists: {project_data['name']}")
            
            await session.commit()
            
            # Verify setup
            result = await session.execute(select(User))
            users = result.scalars().all()
            result = await session.execute(select(Project))
            projects = result.scalars().all()
            
            print(f"\n✅ Setup complete!")
            print(f"Users: {len(users)}")
            print(f"Projects: {len(projects)}")
            print(f"\nLogin credentials:")
            print(f"Email: test@example.com")
            print(f"Password: test1234")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(setup_database())
    if success:
        print("✅ Database setup completed!")
    else:
        print("❌ Database setup failed!")