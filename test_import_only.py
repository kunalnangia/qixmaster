import os
import sys

# Add backend directory to Python path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

print("Testing import fix...")

try:
    # Test importing from app.db
    from app.db import AsyncSessionLocal, init_db
    print("✅ Import from app.db successful!")
except Exception as e:
    print(f"❌ Import from app.db failed: {e}")
    import traceback
    traceback.print_exc()

try:
    # Test importing from app.db.session
    from app.db.session import AsyncSessionLocal as SessionLocalDirect, init_db as init_db_direct
    print("✅ Import from app.db.session successful!")
except Exception as e:
    print(f"❌ Import from app.db.session failed: {e}")
    import traceback
    traceback.print_exc()

print("Import tests completed.")