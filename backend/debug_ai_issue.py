#!/usr/bin/env python3
"""
Debug script to identify why AI-generated test cases are not visible on the frontend.
This script will:
1. Test database connectivity
2. Check if test cases are being saved
3. Verify the AI URL generation endpoint functionality
"""

import asyncio
import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_database_connection():
    """Test if database connection works"""
    try:
        print("🔍 Testing database connection...")
        
        from app.db.session import async_engine
        from sqlalchemy import text
        
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Database connected successfully: {version}")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def check_test_cases_table():
    """Check if test cases table exists and has data"""
    try:
        print("\n🔍 Checking test_cases table...")
        
        from app.db.session import AsyncSessionLocal
        from sqlalchemy import text
        
        async with AsyncSessionLocal() as session:
            # Check if table exists
            result = await session.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_name = 'test_cases'
            """))
            table_exists = result.scalar()
            
            if table_exists:
                print("✅ test_cases table exists")
                
                # Count existing test cases
                result = await session.execute(text("SELECT COUNT(*) FROM test_cases"))
                count = result.scalar()
                print(f"📊 Found {count} test cases in database")
                
                # Show recent test cases
                if count is not None and count > 0:
                    result = await session.execute(text("""
                        SELECT id, title, project_id, created_at, ai_generated 
                        FROM test_cases 
                        ORDER BY created_at DESC 
                        LIMIT 5
                    """))
                    test_cases = result.fetchall()
                    print("📋 Recent test cases:")
                    for tc in test_cases:
                        ai_flag = "🤖" if tc[4] else "👤"
                        print(f"  {ai_flag} {tc[1]} (ID: {tc[0]}, Project: {tc[2]})")
                
                return True
            else:
                print("❌ test_cases table does not exist")
                return False
                
    except Exception as e:
        print(f"❌ Error checking test_cases table: {e}")
        return False

async def test_ai_generation_endpoint():
    """Test the AI generation endpoint logic without HTTP"""
    try:
        print("\n🔍 Testing AI generation logic...")
        
        # Import required modules
        from app.ai_service import AIService
        from app.models.db_models import TestType, Priority
        
        # Create AI service instance
        ai_service = AIService()
        
        # Test generating test cases
        test_cases = await ai_service.generate_test_cases_from_url(
            url="https://example.com",
            project_id="test-project-123",
            test_type=TestType.FUNCTIONAL,
            priority=Priority.MEDIUM,
            count=2
        )
        
        print(f"✅ AI generation successful! Generated {len(test_cases)} test cases:")
        for i, tc in enumerate(test_cases, 1):
            print(f"  {i}. {tc.get('title', 'Untitled')}")
            
        return test_cases
        
    except Exception as e:
        print(f"❌ AI generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_save_to_database():
    """Test saving generated test cases to database"""
    try:
        print("\n🔍 Testing database save functionality...")
        
        # Generate test cases first
        test_cases = await test_ai_generation_endpoint()
        if not test_cases:
            print("❌ Cannot test save - no test cases generated")
            return False
        
        # Import database modules
        from app.db.session import AsyncSessionLocal
        from app.models.db_models import TestCase
        from datetime import datetime
        import uuid
        
        async with AsyncSessionLocal() as session:
            saved_count = 0
            for tc_data in test_cases[:1]:  # Save just one for testing
                # Create test case
                db_test_case = TestCase(
                    id=str(uuid.uuid4()),
                    project_id="debug-test-project",
                    title=tc_data["title"],
                    description=tc_data["description"],
                    test_type="functional",
                    priority="medium",
                    status="draft",
                    created_by="debug-user",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    ai_generated=True
                )
                
                session.add(db_test_case)
                await session.flush()
                saved_count += 1
                print(f"✅ Saved test case: {db_test_case.title} (ID: {db_test_case.id})")
            
            await session.commit()
            print(f"✅ Successfully saved {saved_count} test case(s) to database")
            return True
            
    except Exception as e:
        print(f"❌ Database save failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all debug tests"""
    print("="*60)
    print("🐛 AI Test Case Persistence Debug Script")
    print("="*60)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    success_count = 0
    total_tests = 4
    
    # Test 1: Database Connection
    if await test_database_connection():
        success_count += 1
    
    # Test 2: Check test_cases table
    if await check_test_cases_table():
        success_count += 1
    
    # Test 3: AI Generation
    if await test_ai_generation_endpoint():
        success_count += 1
    
    # Test 4: Database Save
    if await test_save_to_database():
        success_count += 1
    
    # Summary
    print("\n" + "="*60)
    print(f"📊 SUMMARY: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed! The AI test case generation should be working.")
        print("💡 If test cases still don't appear on frontend, check:")
        print("   - Frontend API endpoint URL")
        print("   - Authentication/authorization")
        print("   - Project ID matching")
    else:
        print("⚠️  Some tests failed. Issues need to be resolved:")
        if success_count == 0:
            print("   - Check database connection and configuration")
        elif success_count <= 2:
            print("   - Check database schema and AI service configuration")
        else:
            print("   - Check frontend integration and API endpoints")
    
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())