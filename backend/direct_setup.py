import os
import sys
import asyncio
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🚀 DIRECT SETUP - Creating Users and Projects")
print("=" * 60)

async def direct_setup():
    try:
        print("Loading modules...")
        from dotenv import load_dotenv
        load_dotenv()
        
        from app.db.session import AsyncSessionLocal
        from app.models.db_models import Project, User
        from app.core.security import get_password_hash
        from sqlalchemy.future import select
        
        print("Connecting to database...")
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
                print("✅ Test user already exists")
            
            # Create projects
            print("Creating projects...")
            projects_data = [
                {
                    "id": "ecommerce-testing-project",
                    "name": "E-Commerce Platform Testing",
                    "description": "Testing for e-commerce platform"
                },
                {
                    "id": "banking-webapp-project", 
                    "name": "Banking Web Application Tests",
                    "description": "Banking application testing"
                },
                {
                    "id": "social-media-project",
                    "name": "Social Media Platform Testing", 
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
            
            # Verify
            print("Verifying setup...")
            result = await session.execute(select(User))
            users = result.scalars().all()
            result = await session.execute(select(Project))
            projects = result.scalars().all()
            
            print(f"✅ Users: {len(users)}")
            print(f"✅ Projects: {len(projects)}")
            
        print()
        print("🎉 SETUP COMPLETE!")
        print("📧 Login: test@example.com / test1234")
        print("🔗 API: http://127.0.0.1:8001/api/projects-debug")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(direct_setup())
    if success:
        print("✅ Setup completed!")
    else:
        print("❌ Setup failed!")