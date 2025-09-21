import os
import sys

# Add backend directory to Python path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

print("Simple import test: Checking if modules can be imported...")

# Test 1: Check if we can import the db module
try:
    import app.db
    print("✅ SUCCESS: 'import app.db' works!")
except Exception as e:
    print(f"❌ FAILED: 'import app.db' failed with error: {e}")

# Test 2: Check if we can import specific items from db module
try:
    from app.db import SessionLocal
    print("✅ SUCCESS: 'from app.db import SessionLocal' works!")
except Exception as e:
    print(f"❌ FAILED: 'from app.db import SessionLocal' failed with error: {e}")

# Test 3: Check the contents of the db module
try:
    import app.db
    contents = [item for item in dir(app.db) if not item.startswith('_')]
    print(f"✅ SUCCESS: app.db module contents: {contents}")
except Exception as e:
    print(f"❌ FAILED: Could not inspect app.db module: {e}")

print("\nSimple import test completed.")