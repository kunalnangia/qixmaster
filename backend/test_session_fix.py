#!/usr/bin/env python3
"""
Test script to verify the session.py fix
"""
import sys
import os

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

def test_imports():
    """Test that the new functions can be imported"""
    try:
        from app.db.session import ensure_ai_generator_user_exists, ensure_test_user_exists
        print("✅ Successfully imported ensure_ai_generator_user_exists and ensure_test_user_exists")
        return True
    except ImportError as e:
        print(f"❌ Failed to import functions: {e}")
        return False

if __name__ == "__main__":
    print("Testing session.py fix...")
    success = test_imports()
    if success:
        print("🎉 Fix verification successful!")
    else:
        print("💥 Fix verification failed!")
    sys.exit(0 if success else 1)