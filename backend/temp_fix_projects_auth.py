#!/usr/bin/env python3
"""
Temporary Fix: Create projects endpoint without authentication
This is a temporary workaround to test the projects dropdown.
"""
import asyncio
import sys
import os
from datetime import datetime

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

async def create_projects_and_setup_auth():
    """Create projects and setup basic authentication flow"""
    
    print("🔧 TEMPORARY FIX: Setting up projects without authentication")
    print("=" * 60)
    
    try:
        # Import required modules
        from dotenv import load_dotenv
        load_dotenv()
        
        from app.db.session import AsyncSessionLocal
        from app.models.db_models import Project, User
        from app.core.security import get_password_hash
        from sqlalchemy.future import select
        
        async with AsyncSessionLocal() as session:
            
            # Step 1: Ensure we have a test user
            print("👤 Setting up test user...")
            
            test_user_id = "temp-user-id-for-testing"
            result = await session.execute(
                select(User).where(User.id == test_user_id)
            )
            test_user = result.scalars().first()
            
            if not test_user:
                # Create test user
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
                print(f"   ✅ Created test user: {test_user.email}")
            else:
                print(f"   ✅ Test user exists: {test_user.email}")
            
            # Step 2: Create projects for the test user
            print("📁 Creating projects...")
            
            sample_projects = [
                {
                    "id": "ecommerce-testing-project",
                    "name": "E-Commerce Platform Testing",
                    "description": "Comprehensive testing for e-commerce platform including payment flows, cart functionality, and user management"
                },
                {
                    "id": "banking-webapp-project",
                    "name": "Banking Web Application Tests",
                    "description": "Security and functionality testing for banking web application with focus on transaction security"
                },
                {
                    "id": "social-media-project",
                    "name": "Social Media Platform Testing",
                    "description": "Testing for social media features including user posts, messaging, and notifications"
                },
                {
                    "id": "ai-testing-project",
                    "name": "AI Test Generation Project",
                    "description": "Project for testing AI-generated test cases and automated testing workflows"
                }
            ]
            
            created_projects = []
            for project_data in sample_projects:
                # Check if project exists
                result = await session.execute(
                    select(Project).where(Project.id == project_data["id"])
                )
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
                    created_projects.append(project)
                    print(f"   ✅ Created: {project_data['name']}")
                else:
                    created_projects.append(existing_project)
                    print(f"   ⏭️  Exists: {project_data['name']}")
            
            await session.commit()
            
            # Step 3: Verify projects
            print("📊 Verifying projects...")
            result = await session.execute(select(Project))
            all_projects = result.scalars().all()
            
            print(f"   Total projects in database: {len(all_projects)}")
            for project in all_projects:
                print(f"   - {project.name} (ID: {project.id})")
        
        print()
        print("🎉 SETUP COMPLETE!")
        print("=" * 60)
        print("📧 Test User Credentials:")
        print("Email: test@example.com")
        print("Password: test1234")
        print()
        print("🔗 Projects Created:")
        for i, project in enumerate(created_projects, 1):
            print(f"{i}. {project.name}")
            print(f"   ID: {project.id}")
        print()
        print("🚀 Next Steps:")
        print("1. Make sure backend is running: uvicorn app.main:app --reload --host 127.0.0.1 --port 8001")
        print("2. Start frontend: npm run dev")
        print("3. Login with test@example.com / test1234")
        print("4. Projects should now appear in dropdown!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(create_projects_and_setup_auth())
        if success:
            print("✅ Temporary fix completed successfully!")
            sys.exit(0)
        else:
            print("❌ Temporary fix failed!")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Script execution failed: {str(e)}")
        sys.exit(1)