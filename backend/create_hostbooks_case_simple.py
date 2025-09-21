#!/usr/bin/env python3
"""
Simple script to create a performance test case for https://hostbooks.com
"""
import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
from dotenv import load_dotenv
env_path = backend_dir / '.env'
load_dotenv(env_path)

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import uuid
from datetime import datetime

def create_hostbooks_test_case():
    """Create a performance test case for https://hostbooks.com"""
    
    print("=" * 60)
    print("Creating Performance Test Case for HostBooks.com")
    print("=" * 60)
    
    try:
        # Get database URL from environment
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            print("❌ DATABASE_URL not found in environment variables")
            return False
            
        print(f"Connecting to database...")
        
        # Create sync engine
        engine = create_engine(
            str(DATABASE_URL).replace("postgresql://", "postgresql+psycopg2://"),
            echo=False
        )
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # Check if the test case already exists
            result = db.execute(
                text("""
                    SELECT id FROM test_cases 
                    WHERE title = :title AND project_id = :project_id
                """),
                {
                    "title": "HostBooks Performance Test",
                    "project_id": "default-project-id"
                }
            )
            existing_case = result.fetchone()
            
            if existing_case:
                print(f"✅ Test case already exists with ID: {existing_case[0]}")
                return True
            
            # Insert the test case directly
            test_case_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            # First, ensure the project exists
            result = db.execute(
                text("SELECT id FROM projects WHERE id = :project_id"),
                {"project_id": "default-project-id"}
            )
            project_exists = result.fetchone()
            
            if not project_exists:
                # Create default project
                db.execute(
                    text("""
                        INSERT INTO projects (id, name, description, created_by, is_active, created_at, updated_at)
                        VALUES (:id, :name, :description, :created_by, :is_active, :created_at, :updated_at)
                    """),
                    {
                        "id": "default-project-id",
                        "name": "Default Project",
                        "description": "Default project for test case generation",
                        "created_by": "ai-generator",  # Using the AI generator user ID
                        "is_active": True,
                        "created_at": now,
                        "updated_at": now
                    }
                )
                print("✅ Created default project")
            
            # Create the test case
            db.execute(
                text("""
                    INSERT INTO test_cases 
                    (id, title, description, project_id, test_type, priority, status, 
                     expected_result, created_by, ai_generated, self_healing_enabled, 
                     prerequisites, test_data, created_at, updated_at)
                    VALUES 
                    (:id, :title, :description, :project_id, :test_type, :priority, :status,
                     :expected_result, :created_by, :ai_generated, :self_healing_enabled,
                     :prerequisites, :test_data, :created_at, :updated_at)
                """),
                {
                    "id": test_case_id,
                    "title": "HostBooks Performance Test",
                    "description": "Performance test case for https://hostbooks.com to evaluate loading times, response times, and overall performance metrics",
                    "project_id": "default-project-id",
                    "test_type": "performance",
                    "priority": "high",
                    "status": "active",
                    "expected_result": "Page loads within acceptable time limits with minimal errors",
                    "created_by": "ai-generator",
                    "ai_generated": True,
                    "self_healing_enabled": True,
                    "prerequisites": "Ensure HostBooks website is accessible",
                    "test_data": '{"url": "https://hostbooks.com", "test_parameters": {"concurrent_users": 10, "duration": 60, "ramp_up_time": 10}}',
                    "created_at": now,
                    "updated_at": now
                }
            )
            
            db.commit()
            print("✅ Performance test case created successfully")
            print(f"   Test Case ID: {test_case_id}")
            print("   You can now select this test case in the performance tab dropdown.")
            
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_hostbooks_test_case()
    sys.exit(0 if success else 1)