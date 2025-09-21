#!/usr/bin/env python3
"""
Test script to verify database connection and project fetching without PgBouncer issues
"""
import asyncio
import sys
import os
from datetime import datetime

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

async def test_project_fetch():
    """Test project fetching with proper database connection handling"""
    
    print("=" * 60)
    print("Testing Project Fetch with PgBouncer Compatibility")
    print("=" * 60)
    print(f"Run time: {datetime.now()}")
    print()
    
    try:
        # Import required modules
        from dotenv import load_dotenv
        load_dotenv()
        
        # Import database session
        from app.db.session import AsyncSessionLocal
        from app.models.db_models import Project
        from sqlalchemy.future import select
        
        # Test database fetching
        print("1. Testing project fetching...")
        async with AsyncSessionLocal() as session:
            try:
                # Fetch all projects
                result = await session.execute(
                    select(Project).where(Project.is_active == True)
                )
                projects = result.scalars().all()
                
                print(f"   Found {len(projects)} active project(s)")
                for project in projects:
                    print(f"   - {project.id}: {project.name}")
                
                print()
                print("[SUCCESS] Project fetching works correctly!")
                return True
                
            except Exception as e:
                print(f"   [ERROR] Database operation failed: {str(e)}")
                import traceback
                traceback.print_exc()
                return False

    except Exception as e:
        print(f"[ERROR] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(test_project_fetch())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[CRITICAL] Script execution failed: {str(e)}")
        sys.exit(1)