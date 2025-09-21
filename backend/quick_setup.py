#!/usr/bin/env python3
"""
Quick Setup: Create Users and Projects
"""
import asyncio
import sys
import os
from datetime import datetime

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

async def quick_setup():
    """Quick setup to create users and projects"""
    
    print("🚀 QUICK SETUP - Creating Users and Projects")
    print("=" * 60)
    
    try:
        # Import required modules
        from dotenv import load_dotenv
        load_dotenv()
        
        from app.db.session import AsyncSessionLocal
        from app.models.db_models import Project, User
        from app.core.security import get_password_hash
        from sqlalchemy.future import select
        from sqlalchemy import delete
        
        async with AsyncSessionLocal() as session:
            
            # Step 1: Clean up any conflicting users
            print("🧹 Cleaning up conflicts...")
            
            # Remove any existing test@example.com user that doesn't have the right ID
            result = await session.execute(
                select(User).where(User.email == "test@example.com")
            )
            existing_test_user = result.scalars().first()
            
            if existing_test_user and existing_test_user.id != "temp-user-id-for-testing":
                print(f"   Removing conflicting user: {existing_test_user.id}")
                await session.delete(existing_test_user)
                await session.commit()
            
            print("   ✅ Conflicts resolved")
            
            # Step 2: Create required users
            print("👥 Creating users...")
            
            users_to_create = [
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
            for user_data in users_to_create:
                # Check if user exists
                result = await session.execute(
                    select(User).where(User.id == user_data["id"])
                )
                existing = result.scalars().first()
                
                if not existing:
                    user = User(\n                        id=user_data[\"id\"],\n                        email=user_data[\"email\"],\n                        full_name=user_data[\"full_name\"],\n                        hashed_password=get_password_hash(user_data[\"password\"]),\n                        role=user_data[\"role\"],\n                        is_active=True,\n                        created_at=datetime.utcnow(),\n                        updated_at=datetime.utcnow()\n                    )\n                    session.add(user)\n                    created_users.append(user)\n                    print(f\"   ✅ Created: {user_data['full_name']} ({user_data['email']})\")\n                else:\n                    created_users.append(existing)\n                    print(f\"   ⏭️  Exists: {user_data['full_name']}\")\n            \n            await session.commit()\n            \n            # Step 3: Create projects for each user\n            print(\"📁 Creating projects...\")\n            \n            project_templates = [\n                {\n                    \"suffix\": \"ecommerce\",\n                    \"name\": \"E-Commerce Platform Testing\",\n                    \"description\": \"Comprehensive testing for e-commerce platform including payment flows, cart functionality, and user management\"\n                },\n                {\n                    \"suffix\": \"banking\",\n                    \"name\": \"Banking Web Application Tests\",\n                    \"description\": \"Security and functionality testing for banking web application with focus on transaction security\"\n                },\n                {\n                    \"suffix\": \"social\",\n                    \"name\": \"Social Media Platform Testing\",\n                    \"description\": \"Testing for social media features including user posts, messaging, and notifications\"\n                }\n            ]\n            \n            total_projects = 0\n            for user in created_users:\n                if user.role == \"system\":\n                    # Special projects for AI/system users\n                    project_templates_for_user = [\n                        {\n                            \"suffix\": \"ai-generated\",\n                            \"name\": \"AI Generated Test Cases\",\n                            \"description\": \"Repository for AI-generated test cases from various sources and prompts\"\n                        }\n                    ]\n                else:\n                    project_templates_for_user = project_templates\n                \n                for template in project_templates_for_user:\n                    project_id = f\"{user.id}-{template['suffix']}\"\n                    \n                    # Check if project exists\n                    result = await session.execute(\n                        select(Project).where(Project.id == project_id)\n                    )\n                    existing_project = result.scalars().first()\n                    \n                    if not existing_project:\n                        project = Project(\n                            id=project_id,\n                            name=f\"{template['name']} - {user.full_name}\",\n                            description=template['description'],\n                            created_by=user.id,\n                            is_active=True,\n                            created_at=datetime.utcnow(),\n                            updated_at=datetime.utcnow()\n                        )\n                        session.add(project)\n                        total_projects += 1\n                        print(f\"   ✅ {template['name']} for {user.full_name}\")\n                    else:\n                        print(f\"   ⏭️  Project exists: {template['name']}\")\n            \n            await session.commit()\n            \n            # Step 4: Verify setup\n            print(\"📋 Verifying setup...\")\n            \n            # Count users\n            result = await session.execute(select(User))\n            all_users = result.scalars().all()\n            \n            # Count projects\n            result = await session.execute(select(Project))\n            all_projects = result.scalars().all()\n            \n            print(f\"   Users: {len(all_users)}\")\n            print(f\"   Projects: {len(all_projects)}\")\n            \n        print()\n        print(\"🎉 SETUP COMPLETE!\")\n        print(\"=\" * 60)\n        print(\"📧 Login Credentials:\")\n        print(\"1. Test User: test@example.com (password: test1234)\")\n        print(\"2. Test User 1: testuser1@example.com (password: test123)\")\n        print()\n        print(\"🚀 Next Steps:\")\n        print(\"1. Backend should already be running on: http://127.0.0.1:8001\")\n        print(\"2. Start frontend: npm run dev\")\n        print(\"3. Open: http://localhost:5175/\")\n        print(\"4. Navigate to AI Generator page\")\n        print(\"5. Login and select a project\")\n        print(\"6. Generate test cases!\")\n        print(\"=\" * 60)\n        \n        return True\n        \n    except Exception as e:\n        print(f\"❌ Setup failed: {str(e)}\")\n        import traceback\n        traceback.print_exc()\n        return False\n\nif __name__ == \"__main__\":\n    try:\n        success = asyncio.run(quick_setup())\n        if success:\n            print(\"✅ Setup completed successfully!\")\n            sys.exit(0)\n        else:\n            print(\"❌ Setup failed!\")\n            sys.exit(1)\n    except Exception as e:\n        print(f\"❌ Script execution failed: {str(e)}\")\n        sys.exit(1)