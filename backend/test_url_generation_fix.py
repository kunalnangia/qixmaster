#!/usr/bin/env python3
"""
Test script to verify URL-based test case generation fix with proper database connection handling
"""
import asyncio
import sys
import os
from datetime import datetime

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

async def test_url_generation_fix():
    """Test URL-based test case generation with proper database connection handling"""
    
    print("=" * 60)
    print("Testing URL-based Test Case Generation Fix")
    print("=" * 60)
    print(f"Run time: {datetime.now()}")
    print()
    
    try:
        # Import required modules
        from dotenv import load_dotenv
        load_dotenv()
        
        from app.mcp.website_test_generator import website_test_generator
        from app.db.session import AsyncSessionLocal, force_connection_reset
        from app.models.db_models import Project, TestCase, TestStep
        from sqlalchemy.future import select
        import uuid
        
        # Test URL
        test_url = "https://httpbin.org/forms/post"
        project_id = "test-project-" + str(uuid.uuid4())[:8]
        
        print(f"Testing with URL: {test_url}")
        print(f"Project ID: {project_id}")
        print()
        
        # Force a connection reset to ensure PgBouncer compatibility
        print("1. Resetting database connections for PgBouncer compatibility...")
        reset_success = await force_connection_reset()
        if reset_success:
            print("   [SUCCESS] Database connections reset successfully")
        else:
            print("   [WARNING] Database connection reset failed, continuing anyway...")
        print()
        
        # Generate test cases from URL
        print("2. Generating test cases from URL...")
        try:
            generated_test_cases = await website_test_generator.generate_test_cases_from_url(
                url=test_url,
                project_id=project_id,
                test_count=3
            )
            
            print(f"   Generated {len(generated_test_cases)} test cases")
            for i, test_case in enumerate(generated_test_cases):
                print(f"   {i+1}. {test_case['title']}")
            
        except Exception as e:
            print(f"   [ERROR] Failed to generate test cases: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        print()
        
        # Test database saving
        print("3. Testing database saving...")
        async with AsyncSessionLocal() as session:
            try:
                # Create a test project
                project = Project(
                    id=project_id,
                    name="Test Project",
                    description="Test project for URL generation",
                    created_by="ai-generator",
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(project)
                await session.commit()
                await session.refresh(project)
                
                print(f"   Created project: {project.name}")
                
                # Save test cases to database
                created_test_cases = []
                for test_case_data in generated_test_cases:
                    # Create test case
                    test_case = TestCase(
                        id=str(uuid.uuid4()),
                        project_id=project_id,
                        created_by="ai-generator",
                        title=test_case_data["title"],
                        description=test_case_data.get("description", ""),
                        test_type="functional",  # Using string value for now
                        priority="medium",       # Using string value for now
                        status="draft",
                        expected_result=test_case_data.get("expected_result", ""),
                        ai_generated=True,
                        self_healing_enabled=True,
                        preconditions=test_case_data.get("preconditions", ""),
                        test_data=test_case_data.get("test_data", {}),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    session.add(test_case)
                    await session.flush()  # Get the ID
                    
                    # Create test steps
                    if "steps" in test_case_data:
                        for step_data in test_case_data["steps"]:
                            step = TestStep(
                                id=str(uuid.uuid4()),
                                test_case_id=test_case.id,
                                step_number=step_data["step_number"],
                                description=step_data["description"],
                                expected_result=step_data["expected_result"],
                                created_at=datetime.utcnow(),
                                updated_at=datetime.utcnow()
                            )
                            session.add(step)
                    
                    created_test_cases.append(test_case)
                
                await session.commit()
                
                print(f"   Saved {len(created_test_cases)} test cases to database")
                
                # Verify saved test cases
                print("4. Verifying saved test cases...")
                result = await session.execute(
                    select(TestCase).where(TestCase.project_id == project_id)
                )
                saved_test_cases = result.scalars().all()
                
                print(f"   Found {len(saved_test_cases)} test cases in database")
                
                # Check test steps
                for test_case in saved_test_cases[:2]:  # Check first 2 test cases
                    await session.refresh(test_case)
                    print(f"   Test case: {test_case.title}")
                    print(f"   Steps count: {len(test_case.steps)}")
                    for step in test_case.steps:
                        print(f"     Step {step.step_number}: {step.description}")
                
                print()
                print("[SUCCESS] URL-based test case generation and database saving works correctly!")
                return True
                
            except Exception as e:
                print(f"   [ERROR] Database operation failed: {str(e)}")
                import traceback
                traceback.print_exc()
                await session.rollback()
                return False

    except Exception as e:
        print(f"[ERROR] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(test_url_generation_fix())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[CRITICAL] Script execution failed: {str(e)}")
        sys.exit(1)