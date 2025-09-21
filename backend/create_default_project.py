#!/usr/bin/env python3
"""
Script to create a default project for test case generation
"""
import asyncio
import sys
import os
from datetime import datetime
import uuid
import traceback

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

async def create_default_project():
    """Create a default project for test case generation"""
    
    print("=" * 60)
    print("Creating Default Project")
    print("=" * 60)
    print(f"Run time: {datetime.now()}")
    print()
    
    try:
        # Import required modules
        from dotenv import load_dotenv
        load_dotenv()
        
        from app.db.session import AsyncSessionLocal, ensure_ai_generator_user_exists
        from app.models.db_models import Project
        from sqlalchemy.future import select
        
        # Default project ID
        project_id = "default-project-id"
        
        print(f"Default Project ID: {project_id}")
        print()
        
        # Ensure AI generator user exists
        print("1. Ensuring AI generator user exists...")
        ai_user_id = await ensure_ai_generator_user_exists()
        print(f"   AI Generator user ID: {ai_user_id}")
        print()
        
        # Check if project exists, create if not
        print("2. Checking if default project exists...")
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Project).where(Project.id == project_id)
            )
            db_project = result.scalars().first()
            
            if not db_project:
                print("   Project doesn't exist. Creating...")
                db_project = Project(
                    id=project_id,
                    name="Default Project",
                    description="Default project for test case generation",
                    created_by=ai_user_id,
                    is_active=True
                )
                session.add(db_project)
                await session.commit()
                await session.refresh(db_project)
                print("   Project created successfully")
            else:
                print("   Project already exists")
        
        print()
        print("Default project creation/verification completed successfully!")
        return True
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run the async function
    asyncio.run(create_default_project())