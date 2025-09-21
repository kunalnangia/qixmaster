#!/usr/bin/env python3
"""
Create Sample Projects and Verify AI Generator Setup
"""
import asyncio
import sys
import os
from datetime import datetime
import uuid

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

async def create_sample_projects():
    """Create sample projects for testing"""
    
    print("=" * 60)
    print("Creating Sample Projects & Verifying AI Generator Setup")
    print("=" * 60)
    print(f"Run time: {datetime.now()}")
    print()
    
    try:
        # Import required modules
        from dotenv import load_dotenv
        load_dotenv()
        
        from app.db.session import AsyncSessionLocal, ensure_ai_generator_user_exists, ensure_test_user_exists
        from app.models.db_models import Project, User
        from sqlalchemy import text
        from sqlalchemy.future import select
        
        print("[1] Ensuring system users exist...")
        
        # Ensure AI Generator user exists
        try:
            ai_user_id = await ensure_ai_generator_user_exists()
            print(f"   ✅ AI Generator User: {ai_user_id}")
        except Exception as e:
            print(f"   ❌ Failed to create AI Generator user: {e}")
            return False
        
        # Ensure test user exists
        try:
            test_user_id = await ensure_test_user_exists()
            print(f"   ✅ Test User: {test_user_id}")
            
            # Verify the test user actually exists in the database
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(User).where(User.id == test_user_id))
                user = result.scalars().first()
                if not user:
                    print(f"   ❌ Test user {test_user_id} not found in database, recreating...")
                    # Force create the user
                    from app.core.security import get_password_hash
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
                    print(f"   ✅ Test user created successfully: {test_user_id}")
                else:
                    print(f"   ✅ Test user verified in database: {test_user_id}")
                    
        except Exception as e:
            print(f"   ❌ Failed to create/verify test user: {e}")
            return False
        
        print()
        print("[2] Creating sample projects...")
        
        # Sample projects to create
        sample_projects = [
            {
                "id": "ecommerce-testing",
                "name": "E-Commerce Platform Testing",
                "description": "Comprehensive testing project for e-commerce platform including payment flows, cart functionality, and user management"
            },
            {
                "id": "banking-webapp-tests",
                "name": "Banking Web Application Tests", 
                "description": "Security and functionality testing for banking web application with focus on transaction security and user authentication"
            },
            {
                "id": "social-media-testing",
                "name": "Social Media Platform Testing",
                "description": "Testing project for social media features including user posts, messaging, notifications, and privacy settings"
            },
            {
                "id": "booking-system-tests",
                "name": "Hotel Booking System Tests",
                "description": "End-to-end testing for hotel booking system covering search, booking flow, payment processing, and reservation management"
            },
            {
                "id": "healthcare-portal-tests", 
                "name": "Healthcare Portal Testing",
                "description": "Testing project for healthcare patient portal including appointment scheduling, medical records, and telemedicine features"
            }
        ]
        
        async with AsyncSessionLocal() as session:
            created_projects = []
            
            for project_data in sample_projects:
                # Check if project already exists
                result = await session.execute(
                    select(Project).where(Project.id == project_data["id"])
                )
                existing_project = result.scalars().first()
                
                if existing_project:
                    print(f"   ⏭️  Project already exists: {project_data['name']}")
                    created_projects.append(existing_project)
                else:
                    # Create new project
                    project = Project(
                        id=project_data["id"],
                        name=project_data["name"],
                        description=project_data["description"],
                        created_by=test_user_id,  # Use test user as creator
                        is_active=True,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    
                    session.add(project)
                    created_projects.append(project)
                    print(f"   ✅ Created: {project_data['name']}")
            
            # Commit all projects
            await session.commit()
            
            print()
            print(f"[SUCCESS] {len(created_projects)} projects ready for testing!")
            
            # List all projects
            print()
            print("Available Projects:")
            for i, project in enumerate(created_projects, 1):
                print(f"   {i}. {project.name}")
                print(f"      ID: {project.id}")
                print(f"      Description: {project.description[:80]}...")
                print()
        
        print("=" * 60)
        print("✅ SETUP COMPLETE!")
        print()
        print("Next Steps:")
        print("1. Start your backend server:")
        print("   uvicorn app.main:app --reload --host 127.0.0.1 --port 8001")
        print()
        print("2. Start your frontend:")
        print("   npm run dev")
        print()
        print("3. Open the application: http://localhost:5175/")
        print()
        print("4. Try generating test cases with these projects!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up sample projects: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(create_sample_projects())
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"❌ Script execution failed: {str(e)}")
        sys.exit(1)