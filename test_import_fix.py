import os
import sys

# Add backend directory to Python path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

print("Testing import fix...")

try:
    # Test importing from app.db.session
    from app.db.session import AsyncSessionLocal, init_db
    print("✅ Import successful!")
    print(f"AsyncSessionLocal: {AsyncSessionLocal}")
    print(f"init_db: {init_db}")
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()