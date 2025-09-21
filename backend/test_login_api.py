#!/usr/bin/env python3
"""
Test script to reproduce the exact login API error
"""

import os
import sys
import json
import traceback
import asyncio
from dotenv import load_dotenv

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
sys.path.append(os.path.dirname(__file__))

# Load environment variables
load_dotenv()

async def test_login_endpoint():
    """Test the login endpoint directly to reproduce the error"""
    
    try:
        print("=== Testing Login Endpoint Directly ===")
        
        # Import necessary modules
        from app.main import app
        from app.schemas.user import UserLogin
        from app.db.session import get_db
        from sqlalchemy.ext.asyncio import AsyncSession
        from fastapi import Request
        from unittest.mock import Mock
        
        # Create a mock request
        request = Mock()
        request.url = Mock()
        request.url.path = "/api/auth/login"
        
        # Create user login data
        user_data = UserLogin(
            email="testuser1@example.com",
            password="test123"  # Using the correct password from our debug
        )
        
        print(f"Testing login with:")
        print(f"  Email: {user_data.email}")
        print(f"  Password: {user_data.password}")
        
        # Get a database session
        db_gen = get_db()
        db = await db_gen.__anext__()
        
        try:
            # Import the login function from main.py
            from app.main import login
            
            print("Calling login function...")
            result = await login(request, user_data, db)
            
            print("✅ Login successful!")
            print(f"Result keys: {list(result.keys())}")
            print(f"Token type: {result.get('token_type')}")
            print(f"User info: {result.get('user', {}).get('email')}")
            
        except Exception as e:
            print(f"❌ Login failed with error: {e}")
            print(f"Error type: {type(e).__name__}")
            print("Full traceback:")
            traceback.print_exc()
            
            # Try to get more details about the error
            if hasattr(e, 'detail'):
                print(f"Error detail: {e.detail}")
            if hasattr(e, 'status_code'):
                print(f"Status code: {e.status_code}")
                
        finally:
            # Close the database session
            try:
                await db.close()
            except:
                pass
                
    except Exception as main_error:
        print(f"❌ Main test error: {main_error}")
        print("Full traceback:")
        traceback.print_exc()

async def test_auth_service_directly():
    """Test the AuthService directly"""
    
    try:
        print("\n=== Testing AuthService Directly ===")
        
        from app.auth.security import AuthService
        from app.db.session import get_db
        
        # Get a database session
        db_gen = get_db()
        db = await db_gen.__anext__()
        
        try:
            # Create AuthService instance
            auth_service = AuthService(db)
            
            print("Testing authenticate_user method...")
            
            result = await auth_service.authenticate_user(
                email="testuser1@example.com",
                password="test123"
            )
            
            print("✅ AuthService authentication successful!")
            print(f"User ID: {result.get('id')}")
            print(f"Email: {result.get('email')}")
            
        except Exception as e:
            print(f"❌ AuthService failed with error: {e}")
            print(f"Error type: {type(e).__name__}")
            print("Full traceback:")
            traceback.print_exc()
            
        finally:
            # Close the database session
            try:
                await db.close()
            except:
                pass
                
    except Exception as main_error:
        print(f"❌ AuthService test error: {main_error}")
        print("Full traceback:")
        traceback.print_exc()

async def test_verify_password_in_context():
    """Test verify_password in the exact context it's used"""
    
    try:
        print("\n=== Testing verify_password in Login Context ===")
        
        from app.auth.security import verify_password
        from app.models.db_models import User
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.future import select
        from app.db.session import get_db
        
        # Get a database session
        db_gen = get_db()
        db = await db_gen.__anext__()
        
        try:
            # Query the database for the user (same as login function)
            query = select(User).where(User.email == "testuser1@example.com")
            result = await db.execute(query)
            user = result.scalars().first()
            
            if not user:
                print("❌ User not found in database")
                return
                
            print(f"Found user: {user.email}")
            print(f"User.hashed_password type: {type(user.hashed_password)}")
            print(f"User.hashed_password value: {str(user.hashed_password)[:50]}...")
            
            # Test the exact call that's in the login function
            password_to_test = "test123"
            print(f"Testing password: {password_to_test}")
            
            # This is the exact line from main.py:639
            verification_result = verify_password(password_to_test, str(user.hashed_password))
            
            print(f"✅ Password verification result: {verification_result}")
            
        except Exception as e:
            print(f"❌ Verification failed with error: {e}")
            print(f"Error type: {type(e).__name__}")
            print("Full traceback:")
            traceback.print_exc()
            
        finally:
            # Close the database session
            try:
                await db.close()
            except:
                pass
                
    except Exception as main_error:
        print(f"❌ Context test error: {main_error}")
        print("Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 Testing login functionality in API context...")
    
    # Run the tests
    asyncio.run(test_verify_password_in_context())
    asyncio.run(test_auth_service_directly())
    asyncio.run(test_login_endpoint())
    
    print("\n=== All Tests Complete ===")