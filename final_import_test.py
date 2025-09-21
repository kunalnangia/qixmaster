import os
import sys

# Add backend directory to Python path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

print("Final test: Verifying that the original import error is fixed...")

try:
    # This is the exact import that was failing before our fix
    from app.db import AsyncSessionLocal, init_db
    print("✅ SUCCESS: Import 'app.db' with AsyncSessionLocal and init_db now works!")
    
    # Also test the direct session import
    from app.db.session import AsyncSessionLocal as DirectAsyncSessionLocal, init_db as DirectInitDb
    print("✅ SUCCESS: Direct import 'app.db.session' also works!")
    
    print("\n🎉 All import issues have been resolved! 🎉")
    
except ImportError as e:
    print(f"❌ FAILED: Import still failing with error: {e}")
    import traceback
    traceback.print_exc()
    
except Exception as e:
    print(f"❌ FAILED: Unexpected error: {e}")
    import traceback
    traceback.print_exc()

print("\nFinal import test completed.")