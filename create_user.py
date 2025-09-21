#!/usr/bin/env python3
"""
Simple script to create a test user for login testing
"""

try:
    # Import required modules
    import sys
    import os
    from pathlib import Path
    
    # Add the project root to Python path to access backend module
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    # Import each module individually to avoid issues
    from backend.db.session import SessionLocal, engine  # type: ignore
    from backend.models.db_models import User  # type: ignore
    from backend.auth.security import get_password_hash  # type: ignore
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError
    import uuid
    from datetime import datetime
    
    def create_test_user():
        """Create a test user directly in the database"""
        print("🔧 Creating test user...")
        
        # Test user details
        test_email = "testuser@example.com"
        test_password = "password123"
        test_name = "Test User"
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Check if user already exists
            existing_user = db.execute(
                text("SELECT id, email FROM users WHERE email = :email"),
                {"email": test_email}
            ).fetchone()
            
            if existing_user:
                print(f"✅ Test user already exists!")
                print(f"   Email: {existing_user[1]}")
                print(f"   ID: {existing_user[0]}")
                print(f"   You can login with: {test_email} / {test_password}")
                return True
            
            # Hash the password
            hashed_password = get_password_hash(test_password)
            
            # Create new user
            user_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            db.execute(
                text("""
                    INSERT INTO users (id, email, full_name, hashed_password, role, is_active, created_at, updated_at)
                    VALUES (:id, :email, :full_name, :hashed_password, :role, :is_active, :created_at, :updated_at)
                """),
                {
                    "id": user_id,
                    "email": test_email,
                    "full_name": test_name,
                    "hashed_password": hashed_password,
                    "role": "tester",
                    "is_active": True,
                    "created_at": now,
                    "updated_at": now
                }
            )
            
            db.commit()
            
            print(f"✅ Test user created successfully!")
            print(f"   Email: {test_email}")
            print(f"   Password: {test_password}")
            print(f"   Name: {test_name}")
            print(f"   ID: {user_id}")
            print(f"\n🚀 You can now login at: http://localhost:5175")
            
            return True
            
        except IntegrityError as e:
            print(f"❌ User already exists or database constraint violation: {e}")
            db.rollback()
            return False
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    if __name__ == "__main__":
        print("=== EmergentIntelliTest User Creation ===")
        success = create_test_user()
        if success:
            print("\n✅ Setup complete! You can now login to the application.")
        else:
            print("\n❌ Setup failed. Please check the error messages above.")
            sys.exit(1)

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the project root directory and the backend is properly set up.")
    sys.exit(1)