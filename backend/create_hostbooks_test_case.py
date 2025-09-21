#!/usr/bin/env python3
"""
Script to create a performance test case for https://hostbooks.com
"""
import asyncio
import sys
import os
from datetime import datetime
import uuid

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

async def create_hostbooks_test_case():
    """Create a performance test case for https://hostbooks.com"""
    
    print("=" * 60)
    print("Creating Performance Test Case for HostBooks.com")
    print("=" * 60)
    print(f"Run time: {datetime.now()}")
    print()
    
    try:
        # Import required modules
        from dotenv import load_dotenv
        load_dotenv()
        
        from app.db.session import AsyncSessionLocal, ensure_ai_generator_user_exists
        from app.models.db_models import Project, TestCase, TestType, Priority, Status
        from sqlalchemy.future import select
        
        # Default project ID
        project_id = "default-project-id"
        
        print(f"Using Project ID: {project_id}")
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
        
        # Create performance test case for HostBooks.com
        print("3. Creating performance test case for HostBooks.com...")
        async with AsyncSessionLocal() as session:
            # Check if test case already exists
            result = await session.execute(
                select(TestCase).where(
                    TestCase.title == "HostBooks Performance Test",
                    TestCase.project_id == project_id
                )
            )
            existing_test_case = result.scalars().first()
            
            if existing_test_case:
                print("   Test case already exists. Skipping creation.")
                print(f"   Test Case ID: {existing_test_case.id}")
            else:
                # Create new performance test case
                test_case = TestCase(
                    id=str(uuid.uuid4()),
                    title="HostBooks Performance Test",
                    description="Performance test case for https://hostbooks.com to evaluate loading times, response times, and overall performance metrics",
                    project_id=project_id,
                    test_type=TestType.PERFORMANCE,
                    priority=Priority.HIGH,
                    status=Status.ACTIVE,
                    expected_result="Page loads within acceptable time limits with minimal errors",
                    created_by=ai_user_id,
                    ai_generated=True,
                    self_healing_enabled=True,
                    preconditions="Ensure HostBooks website is accessible",
                    test_data={
                        "url": "https://hostbooks.com",
                        "test_parameters": {
                            "concurrent_users": 10,
                            "duration": 60,
                            "ramp_up_time": 10
                        }
                    },
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                session.add(test_case)
                await session.commit()
                await session.refresh(test_case)
                print("   Performance test case created successfully")
                print(f"   Test Case ID: {test_case.id}")
                print(f"   Test Type: {test_case.test_type}")
                print(f"   Priority: {test_case.priority}")
        
        print()
        print("Performance test case creation completed successfully!")
        print("You can now select this test case in the performance tab dropdown.")
        return True
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run the async function
    success = asyncio.run(create_hostbooks_test_case())
    sys.exit(0 if success else 1)