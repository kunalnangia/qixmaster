#!/usr/bin/env python3
"""
Create Sample Projects for AI Testing
"""
import asyncio
import sys
import os
from datetime import datetime

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

async def create_projects():
    """Create sample projects for AI test generation"""
    
    print("📁 CREATING SAMPLE PROJECTS")
    print("=" * 50)
    
    try:
        # Import required modules
        from dotenv import load_dotenv
        load_dotenv()
        
        from app.db.session import AsyncSessionLocal
        from app.models.db_models import Project, User
        from sqlalchemy.future import select
        
        async with AsyncSessionLocal() as session:
            
            # Step 1: Verify test user exists
            print("👤 Verifying test user exists...")
            result = await session.execute(
                select(User).where(User.id == "temp-user-id-for-testing")
            )
            test_user = result.scalars().first()
            
            if not test_user:
                print("❌ Test user not found! Please run create_testuser1.py first")
                return False
            
            print(f"✅ Test user found: {test_user.email}")
            print()
            
            # Step 2: Create sample projects
            print("📁 Creating sample projects...")
            
            sample_projects = [
                {
                    "id": "ecommerce-testing",
                    "name": "E-Commerce Platform Testing",
                    "description": "Comprehensive testing for e-commerce platform including payment flows, cart functionality, and user management"
                },
                {
                    "id": "banking-webapp-tests",
                    "name": "Banking Web Application Tests",
                    "description": "Security and functionality testing for banking web application with focus on transaction security"
                },
                {
                    "id": "social-media-testing",
                    "name": "Social Media Platform Testing",
                    "description": "Testing for social media features including user posts, messaging, and notifications"
                },
                {
                    "id": "booking-system-tests",
                    "name": "Hotel Booking System Tests",
                    "description": "End-to-end testing for hotel booking system covering search, booking, and payment processing"
                },
                {
                    "id": "healthcare-portal-tests",
                    "name": "Healthcare Portal Testing",
                    "description": "Testing for healthcare patient portal including appointments and medical records"
                }
            ]
            
            created_count = 0
            for project_data in sample_projects:
                # Check if project already exists
                result = await session.execute(
                    select(Project).where(Project.id == project_data["id"])
                )
                existing_project = result.scalars().first()
                
                if existing_project:
                    print(f"  ⏭️  Already exists: {project_data['name']}")
                else:
                    # Create new project
                    project = Project(
                        id=project_data["id"],
                        name=project_data["name"],
                        description=project_data["description"],
                        created_by="temp-user-id-for-testing",
                        is_active=True,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    session.add(project)
                    created_count += 1
                    print(f"  ✅ Created: {project_data['name']}")
            
            # Commit all projects
            await session.commit()
            print()
            
            # Step 3: Verify projects were created
            print("📋 Verifying projects...")
            result = await session.execute(select(Project))
            all_projects = result.scalars().all()
            
            print(f"Total projects: {len(all_projects)}")
            for project in all_projects:
                print(f"  ✅ {project.name}")
                print(f"     ID: {project.id}")
                print(f"     Created by: {project.created_by}")
                print()
        
        print("🎉 SUCCESS!")
        print("=" * 50)
        print(f"Created {created_count} new projects")
        print("Projects are ready for AI test generation!")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating projects: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(create_projects())
        if success:
            print("✅ Project creation completed successfully!")
            sys.exit(0)
        else:
            print("❌ Project creation failed!")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Script execution failed: {str(e)}")
        sys.exit(1)