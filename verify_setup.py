#!/usr/bin/env python3
"""
Quick Setup Verification for AI Generator
"""
import asyncio
import sys
import os
import requests
from datetime import datetime

# Add backend directory to Python path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

def check_backend_running():
    """Check if backend server is running"""
    try:
        response = requests.get('http://127.0.0.1:8001/api/docs', timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running at http://127.0.0.1:8001")
            return True
        else:
            print(f"❌ Backend responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running or not accessible at http://127.0.0.1:8001")
        return False
    except Exception as e:
        print(f"❌ Error checking backend: {str(e)}")
        return False

async def check_database_setup():
    """Check if users and projects exist in database"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        from app.db.session import AsyncSessionLocal
        from app.models.db_models import User, Project
        from sqlalchemy.future import select
        
        async with AsyncSessionLocal() as session:
            # Check users
            result = await session.execute(select(User))
            users = result.scalars().all()
            print(f"📊 Database has {len(users)} users")
            
            for user in users[:5]:  # Show first 5 users
                print(f"   - {user.full_name} ({user.email}) - Role: {user.role}")
            
            # Check projects
            result = await session.execute(select(Project))
            projects = result.scalars().all()
            print(f"📊 Database has {len(projects)} projects")
            
            for project in projects:
                print(f"   - {project.name} (ID: {project.id})")
            
            return len(users) > 0 and len(projects) > 0
            
    except Exception as e:
        print(f"❌ Error checking database: {str(e)}")
        return False

def check_frontend_setup():
    """Check if frontend is accessible"""
    try:
        response = requests.get('http://localhost:5175', timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is running at http://localhost:5175")
            return True
        else:
            print(f"❌ Frontend responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Frontend is not running or not accessible at http://localhost:5175")
        return False
    except Exception as e:
        print(f"❌ Error checking frontend: {str(e)}")
        return False

async def main():
    print("🔍 AI Generator Setup Verification")
    print("=" * 50)
    print(f"Time: {datetime.now()}")
    print()
    
    # Check backend
    print("[1] Checking Backend...")
    backend_ok = check_backend_running()
    print()
    
    # Check database
    print("[2] Checking Database...")
    if backend_ok:
        db_ok = await check_database_setup()
    else:
        print("⏭️ Skipping database check (backend not running)")
        db_ok = False
    print()
    
    # Check frontend
    print("[3] Checking Frontend...")
    frontend_ok = check_frontend_setup()
    print()
    
    # Summary
    print("=" * 50)
    print("📋 SUMMARY:")
    print(f"Backend: {'✅ Running' if backend_ok else '❌ Not Running'}")
    print(f"Database: {'✅ Has Data' if db_ok else '❌ Missing Data'}")
    print(f"Frontend: {'✅ Running' if frontend_ok else '❌ Not Running'}")
    print()
    
    if not backend_ok:
        print("🔧 TO FIX BACKEND:")
        print("cd backend")
        print("uvicorn app.main:app --reload --host 127.0.0.1 --port 8001")
        print()
        
    if not db_ok:
        print("🔧 TO FIX DATABASE:")
        print("cd backend")
        print("python create_users_only.py")
        print("python create_projects_only.py")
        print()
        
    if not frontend_ok:
        print("🔧 TO FIX FRONTEND:")
        print("cd frontend")
        print("npm install")
        print("npm run dev")
        print()
    
    if backend_ok and db_ok and frontend_ok:
        print("🎉 ALL SYSTEMS GO!")
        print("🚀 Ready to use AI Generator at: http://localhost:5175")
    else:
        print("❌ Some issues need to be resolved first")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Script failed: {str(e)}")
        sys.exit(1)