#!/usr/bin/env python3
"""
Debug script to test login functionality and identify the source of the error.
"""

import os
import sys
import traceback
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, select
from sqlalchemy.orm import sessionmaker

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
sys.path.append(os.path.dirname(__file__))

# Load environment variables
load_dotenv()

def test_password_verification():
    """Test password verification with the exact same logic as the login endpoint"""
    
    try:
        # Import the verification function
        from app.auth.security import verify_password
        from app.core.security import verify_password as core_verify_password
        
        print("=== Testing Password Verification ===")
        
        # Database connection
        db_url = os.getenv('DATABASE_URL')
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # Get the user data
            result = conn.execute(
                text('SELECT id, email, hashed_password FROM users WHERE email = :email'),
                {'email': 'testuser1@example.com'}
            )
            user_data = result.fetchone()
            
            if not user_data:
                print("❌ User not found in database")
                return False
                
            user_id, email, stored_hash = user_data
            test_password = "test123"
            
            print(f"User ID: {user_id}")
            print(f"Email: {email}")
            print(f"Stored hash type: {type(stored_hash)}")
            print(f"Stored hash length: {len(stored_hash)}")
            print(f"Stored hash: {stored_hash[:50]}...")
            print(f"Test password: {test_password}")
            print(f"Test password type: {type(test_password)}")
            
            # Test with app.auth.security version
            print("\n--- Testing with app.auth.security.verify_password ---")
            try:
                result1 = verify_password(test_password, stored_hash)
                print(f"✅ app.auth.security.verify_password result: {result1}")
            except Exception as e:
                print(f"❌ app.auth.security.verify_password error: {e}")
                print(f"Error type: {type(e)}")
                print("Traceback:")
                traceback.print_exc()
            
            # Test with app.core.security version
            print("\n--- Testing with app.core.security.verify_password ---")
            try:
                result2 = core_verify_password(test_password, stored_hash)
                print(f"✅ app.core.security.verify_password result: {result2}")
            except Exception as e:
                print(f"❌ app.core.security.verify_password error: {e}")
                print(f"Error type: {type(e)}")
                print("Traceback:")
                traceback.print_exc()
            
            # Test direct bcrypt usage
            print("\n--- Testing with direct bcrypt usage ---")
            try:
                import bcrypt
                # bcrypt expects bytes
                password_bytes = test_password.encode('utf-8')
                hash_bytes = stored_hash.encode('utf-8')
                result3 = bcrypt.checkpw(password_bytes, hash_bytes)
                print(f"✅ Direct bcrypt result: {result3}")
            except Exception as e:
                print(f"❌ Direct bcrypt error: {e}")
                print("Traceback:")
                traceback.print_exc()
            
            # Test passlib usage (what should be used)
            print("\n--- Testing with passlib (expected method) ---")
            try:
                from passlib.context import CryptContext
                pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                result4 = pwd_context.verify(test_password, stored_hash)
                print(f"✅ Passlib result: {result4}")
            except Exception as e:
                print(f"❌ Passlib error: {e}")
                print("Traceback:")
                traceback.print_exc()
                
    except Exception as e:
        print(f"❌ Main error: {e}")
        print("Traceback:")
        traceback.print_exc()
        return False

def test_with_different_passwords():
    """Test with different password values to see if any work"""
    
    test_passwords = ["test123", "Test@1234!", "testpassword", "password123", "test1234"]
    
    try:
        from app.auth.security import verify_password
        
        # Database connection
        db_url = os.getenv('DATABASE_URL')
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # Get the user data
            result = conn.execute(
                text('SELECT hashed_password FROM users WHERE email = :email'),
                {'email': 'testuser1@example.com'}
            )
            user_data = result.fetchone()
            
            if not user_data:
                print("❌ User not found in database")
                return False
                
            stored_hash = user_data[0]
            
            print("\n=== Testing Different Passwords ===")
            for password in test_passwords:
                try:
                    result = verify_password(password, stored_hash)
                    print(f"Password '{password}': {'✅ MATCH' if result else '❌ No match'}")
                    if result:
                        print(f"🎉 FOUND WORKING PASSWORD: {password}")
                        return password
                except Exception as e:
                    print(f"Password '{password}': ❌ Error - {e}")
                    
    except Exception as e:
        print(f"❌ Test error: {e}")
        traceback.print_exc()
        
    return None

if __name__ == "__main__":
    print("🔍 Debugging login functionality...")
    
    # Test password verification
    test_password_verification()
    
    # Test with different passwords
    working_password = test_with_different_passwords()
    
    if working_password:
        print(f"\n✅ Working password found: {working_password}")
    else:
        print("\n❌ No working password found")
        
    print("\n=== Debug Complete ===")