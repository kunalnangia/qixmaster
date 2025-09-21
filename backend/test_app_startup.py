#!/usr/bin/env python3
"""
Simple server startup test
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, '.')

try:
    print("🔍 Testing imports...")
    from app.main import app
    print("✅ Successfully imported FastAPI app!")
    
    print("🔍 Testing if app is configured correctly...")
    print(f"App title: {app.title}")
    print(f"App version: {app.version}")
    
    # Test if routes are properly loaded
    routes = []
    for route in app.routes:
        # Safely get path and methods - different route types have different attributes
        path = getattr(route, 'path', None)
        if path:
            methods = getattr(route, 'methods', None) or ['GET']
            routes.append(f"{methods} {path}")
    
    print(f"\n📋 Found {len(routes)} routes:")
    ai_routes = [r for r in routes if '/ai/' in r]
    for route in ai_routes:
        print(f"  {route}")
    
    if not ai_routes:
        print("⚠️  No AI routes found!")
    else:
        print("✅ AI routes found!")
    
    print("\n🎯 The application appears to be properly configured!")
    print("💡 You can start the server manually with:")
    print("   uvicorn app.main:app --host 127.0.0.1 --port 8001")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're running this from the backend directory")
    print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
