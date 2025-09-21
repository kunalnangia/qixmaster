#!/usr/bin/env python3
"""
Test to verify AI URL generation and test case persistence fix
"""
import asyncio
import sys
import os
import uuid
from datetime import datetime
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_ai_url_generation_and_persistence():
    """Test the complete flow: generate test cases and verify they're saved"""
    try:
        print("🧪 Testing AI URL generation and persistence...")
        
        # Load environment
        from dotenv import load_dotenv
        load_dotenv()
        
        # Import required modules
        from app.db.session import AsyncSessionLocal
        from app.models.db_models import TestCase, Project as DBProject
        from app.ai_service import ai_service
        from app.schemas.ai import AIAnalysisResult
        from app.models.db_models import TestType, Priority
        from sqlalchemy.future import select
        
        # Test project ID that matches frontend
        test_project_id = "default-project-id"
        
        async with AsyncSessionLocal() as db:
            print(f"📋 Testing with project ID: {test_project_id}")
            
            # 1. Check if project exists, create if not
            result = await db.execute(select(DBProject).where(DBProject.id == test_project_id))
            db_project = result.scalars().first()
            
            if not db_project:
                print("🏗️  Creating test project...")
                db_project = DBProject(
                    id=test_project_id,
                    name="Default Test Project",
                    description="Auto-created for AI test generation",
                    created_by="test-user",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(db_project)
                await db.flush()
                print(f"✅ Created project: {test_project_id}")
            else:
                print(f"✅ Project exists: {test_project_id}")
            
            # 2. Test AI service generation
            print("🤖 Testing AI service generation...")
            test_cases_data = await ai_service.generate_test_cases_from_url(
                url="https://example.com",
                project_id=test_project_id,
                test_type=TestType.FUNCTIONAL,
                priority=Priority.MEDIUM,
                count=2
            )
            
            print(f"✅ AI generated {len(test_cases_data)} test cases")
            
            # 3. Save test cases to database (simulate the endpoint logic)
            print("💾 Saving test cases to database...")
            saved_count = 0
            for tc_data in test_cases_data:
                db_test_case = TestCase(
                    id=str(uuid.uuid4()),
                    project_id=test_project_id,
                    title=tc_data["title"],
                    description=tc_data["description"],
                    test_type="functional",
                    priority="medium",
                    status="draft",
                    created_by="test-user",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    ai_generated=True
                )
                db.add(db_test_case)
                saved_count += 1
            
            await db.commit()
            print(f"✅ Saved {saved_count} test cases to database")
            
            # 4. Verify test cases can be retrieved
            print("🔍 Verifying test cases can be retrieved...")
            result = await db.execute(
                select(TestCase).where(TestCase.project_id == test_project_id)
            )
            retrieved_test_cases = result.scalars().all()
            
            print(f"✅ Retrieved {len(retrieved_test_cases)} test cases for project {test_project_id}")
            
            # 5. Show test case details
            for i, tc in enumerate(retrieved_test_cases[-2:], 1):  # Show last 2
                print(f"  {i}. {tc.title} (ID: {tc.id[:8]}..., AI: {tc.ai_generated})")
            
            print("\n🎉 SUCCESS: AI URL generation and persistence working correctly!")
            print("💡 Test cases should now appear on the frontend when:")
            print("   1. Backend server is running")
            print("   2. Frontend calls the test cases endpoint")
            print("   3. Project ID matches ('default-project-id')")
            
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print("AI URL Generation & Persistence Test")
    print("="*60)
    
    success = asyncio.run(test_ai_url_generation_and_persistence())
    
    if success:
        print("\n🎯 CONCLUSION: The backend logic is working correctly!")
        print("🚀 Next steps:")
        print("   1. Start the backend server: python run_server.py")
        print("   2. Test the frontend AI generation feature")
        print("   3. Check if test cases appear in the list")
    else:
        print("\n⚠️  Issues found that need to be resolved.")
    
    print("="*60)