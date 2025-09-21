#!/usr/bin/env python3
"""
Create Projects for All Users
"""
import asyncio
import sys
import os
from datetime import datetime

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

async def create_projects_for_users():
    """Create sample projects for all users in the database"""
    
    print("📁 CREATING PROJECTS FOR ALL USERS")
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
            
            # Step 1: Get all users in the database
            print("👥 Getting all users...")
            result = await session.execute(select(User))
            all_users = result.scalars().all()
            
            if not all_users:
                print("❌ No users found in database!")
                print("Creating default users first...")
                
                # Create default users
                default_users = [
                    {
                        "id": "temp-user-id-for-testing",
                        "email": "test@example.com",
                        "full_name": "Test User",
                        "password": "test1234",
                        "role": "tester"
                    },
                    {
                        "id": "testuser1",
                        "email": "testuser1@example.com",
                        "full_name": "Test User 1",
                        "password": "test123",
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
                
                created_users = []
                for user_data in default_users:
                    # Check if user already exists by email
                    result = await session.execute(
                        select(User).where(User.email == user_data["email"])
                    )
                    existing_user = result.scalars().first()
                    
                    if not existing_user:
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
                        created_users.append(user)
                        print(f"  ✅ Created user: {user_data['email']}")
                    else:
                        created_users.append(existing_user)
                        print(f"  ⏭️  User exists: {user_data['email']}")
                
                await session.commit()
                all_users = created_users
            
            print(f"Found {len(all_users)} users:")
            for user in all_users:
                print(f"  - {user.full_name} ({user.email}) - Role: {user.role}")
            print()
            
            # Step 2: Define project templates for different user types
            print("📋 Creating project templates...")
            
            # Projects for regular users (testers)
            tester_projects = [
                {
                    "id_suffix": "ecommerce",
                    "name": "E-Commerce Platform Testing",
                    "description": "Comprehensive testing for e-commerce platform including payment flows, cart functionality, and user management"
                },
                {
                    "id_suffix": "banking",
                    "name": "Banking Web Application Tests",
                    "description": "Security and functionality testing for banking web application with focus on transaction security"
                },
                {
                    "id_suffix": "social",
                    "name": "Social Media Platform Testing",
                    "description": "Testing for social media features including user posts, messaging, and notifications"
                }
            ]
            
            # Projects for system users (AI)
            system_projects = [
                {
                    "id_suffix": "ai-generated",
                    "name": "AI Generated Test Cases",
                    "description": "Repository for AI-generated test cases from various sources and prompts"
                },
                {
                    "id_suffix": "website-analysis",
                    "name": "Website Analysis Testing",
                    "description": "Test cases generated from website URL analysis using MCP server"
                }
            ]
            
            # Step 3: Create projects for each user
            total_created = 0
            
            for user in all_users:
                print(f"📁 Creating projects for {user.full_name}...")
                
                # Choose project templates based on user role
                if user.role == "system":
                    project_templates = system_projects
                else:
                    project_templates = tester_projects
                
                user_projects_created = 0
                for template in project_templates:
                    project_id = f"{user.id}-{template['id_suffix']}"
                    
                    # Check if project already exists
                    result = await session.execute(
                        select(Project).where(Project.id == project_id)
                    )
                    existing_project = result.scalars().first()
                    
                    if existing_project:
                        print(f"  ⏭️  Already exists: {template['name']}")
                    else:
                        # Create new project
                        project = Project(
                            id=project_id,
                            name=f"{template['name']} - {user.full_name}",
                            description=template['description'],
                            created_by=user.id,
                            is_active=True,
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                        session.add(project)
                        user_projects_created += 1
                        total_created += 1
                        print(f"  ✅ Created: {template['name']}")
                
                print(f"  📊 Created {user_projects_created} projects for {user.full_name}")
                print()
            
            # Commit all projects
            await session.commit()
            
            # Step 4: Verify projects were created
            print("📋 Verifying all projects...")
            result = await session.execute(select(Project))
            all_projects = result.scalars().all()
            
            print(f"Total projects in database: {len(all_projects)}")
            print()
            
            # Group projects by user
            projects_by_user = {}
            for project in all_projects:
                if project.created_by not in projects_by_user:
                    projects_by_user[project.created_by] = []
                projects_by_user[project.created_by].append(project)
            
            for user_id, projects in projects_by_user.items():
                user_result = await session.execute(
                    select(User).where(User.id == user_id)
                )
                user = user_result.scalars().first()
                user_name = user.full_name if user else "Unknown User"
                
                print(f"👤 {user_name} ({user_id}):")
                for project in projects:
                    print(f"  ✅ {project.name}")
                    print(f"     ID: {project.id}")
                print()
        
        print("🎉 SUCCESS!")
        print("=" * 60)
        print(f"Created {total_created} new projects")
        print("All users now have projects available!")
        print()
        print("🚀 Next Steps:")
        print("1. Start the backend server:")
        print("   uvicorn app.main:app --reload --host 127.0.0.1 --port 8001")
        print()
        print("2. Start the frontend:")
        print("   npm run dev")
        print()
        print("3. Open the application: http://localhost:5175/")
        print("4. Navigate to AI Generator page")
        print("5. Select a project and generate test cases!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating projects: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(create_projects_for_users())
        if success:
            print("✅ Project creation completed successfully!")
            sys.exit(0)
        else:
            print("❌ Project creation failed!")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Script execution failed: {str(e)}")
        sys.exit(1)