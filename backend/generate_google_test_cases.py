#!/usr/bin/env python3
"""
Script to generate test cases from google.com for various test types
"""
import asyncio
import sys
import os
from datetime import datetime
import traceback

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

async def generate_google_test_cases():
    """Generate test cases from google.com for various test types"""
    
    print("=" * 60)
    print("Generating Test Cases from Google.com")
    print("=" * 60)
    print(f"Run time: {datetime.now()}")
    print()
    
    try:
        # Import required modules
        from dotenv import load_dotenv
        load_dotenv()
        
        from app.mcp.website_test_generator import website_test_generator
        from app.db.session import AsyncSessionLocal, ensure_ai_generator_user_exists
        from app.models.db_models import Project, TestCase, TestStep, TestType, Priority, Status
        from sqlalchemy.future import select
        import uuid
        
        # Use default project ID
        project_id = "default-project-id"
        test_url = "https://www.google.com"
        
        print(f"Testing with URL: {test_url}")
        print(f"Project ID: {project_id}")
        print()
        
        # Force a connection reset if needed for PgBouncer compatibility
        from app.db.session import reset_database_connections
        print("1. Resetting database connections for PgBouncer compatibility...")
        reset_success = await reset_database_connections()
        if reset_success:
            print("   [SUCCESS] Database connections reset successfully")
        else:
            print("   [WARNING] Database connection reset failed, continuing anyway...")
        print()
        
        # Ensure AI generator user exists
        print("2. Ensuring AI generator user exists...")
        ai_user_id = await ensure_ai_generator_user_exists()
        print(f"   AI Generator user ID: {ai_user_id}")
        print()
        
        # Check if project exists, create if not
        print("3. Checking if project exists...")
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
        
        # Generate test cases from URL
        print("4. Generating test cases from URL...")
        try:
            generated_test_cases = await website_test_generator.generate_test_cases_from_url(
                url=test_url,
                project_id=project_id,
                test_count=20  # Generate more to ensure we have enough for each type
            )
            
            print(f"   Generated {len(generated_test_cases)} test cases")
            for i, test_case in enumerate(generated_test_cases):
                print(f"   {i+1}. {test_case['title']} (Type: {test_case.get('test_type', 'functional')})")
            
        except Exception as e:
            print(f"   [ERROR] Failed to generate test cases: {str(e)}")
            traceback.print_exc()
            return False
        
        print()
        
        # Save test cases to database with proper test types
        print("5. Saving test cases to database with proper test types...")
        async with AsyncSessionLocal() as session:
            # Group test cases by type
            test_types = {}
            for tc in generated_test_cases:
                test_type = tc.get("test_type", "functional")
                if test_type not in test_types:
                    test_types[test_type] = []
                test_types[test_type].append(tc)
            
            # If some test types are missing, assign some of the functional tests to them
            functional_tests = test_types.get("functional", [])
            required_types = ["api", "visual", "security", "performance"]
            
            for req_type in required_types:
                if req_type not in test_types or len(test_types[req_type]) == 0:
                    # Take some functional tests and convert them
                    if functional_tests:
                        print(f"   No {req_type} tests found. Converting some functional tests...")
                        test_types[req_type] = []
                        # Take up to 2 functional tests for this type
                        for _ in range(min(2, len(functional_tests))):
                            if functional_tests:
                                test = functional_tests.pop(0)
                                test["test_type"] = req_type
                                test_types[req_type].append(test)
            
            # Save test cases by type
            created_count = 0
            for test_type, test_cases in test_types.items():
                print(f"   Saving {len(test_cases)} {test_type} test cases...")
                
                for tc in test_cases:
                    # Map string values to enum values
                    try:
                        test_type_enum = TestType(test_type.upper())
                    except ValueError:
                        test_type_enum = TestType.FUNCTIONAL  # Default fallback
                        
                    try:
                        priority_str = tc.get("priority", "medium")
                        priority_enum = Priority(priority_str.upper())
                    except ValueError:
                        priority_enum = Priority.MEDIUM  # Default fallback
                    
                    # Create test case
                    db_test_case = TestCase(
                        id=str(uuid.uuid4()),
                        title=tc["title"],
                        description=tc.get("description", ""),
                        project_id=project_id,
                        test_type=test_type_enum,
                        priority=priority_enum,
                        status=Status.DRAFT,
                        expected_result=tc.get("expected_result", ""),
                        created_by=ai_user_id,
                        ai_generated=True,
                        self_healing_enabled=True,
                        preconditions=tc.get("preconditions", ""),
                        test_data=tc.get("test_data", {}),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    
                    session.add(db_test_case)
                    await session.flush()  # Get the ID
                    
                    # Create test steps
                    if "steps" in tc:
                        for step in tc["steps"]:
                            db_step = TestStep(
                                id=str(uuid.uuid4()),
                                test_case_id=db_test_case.id,
                                step_number=step["step_number"],
                                description=step["description"],
                                expected_result=step["expected_result"],
                                created_at=datetime.utcnow(),
                                updated_at=datetime.utcnow()
                            )
                            session.add(db_step)
                    
                    created_count += 1
            
            # Commit all changes
            await session.commit()
            print(f"   Successfully saved {created_count} test cases to database")
        
        print()
        print("6. Summary of test cases generated:")
        for test_type, test_cases in test_types.items():
            print(f"   - {test_type}: {len(test_cases)} test cases")
        
        print()
        print("Test case generation completed successfully!")
        print("You can now view the test cases in the UI")
        print()
        return True
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run the async function
    asyncio.run(generate_google_test_cases())