#!/usr/bin/env python3
"""
Quick PgBouncer Fix Script
Run this script when you encounter DuplicatePreparedStatementError
"""
import asyncio
import sys
import os
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def apply_pgbouncer_fix():
    """Apply the database connection fix"""
    
    print("Database Connection Fix Utility")
    print("=" * 50)
    print(f"Run time: {datetime.now()}")
    
    try:
        # Import the fix function
        from app.db.session import force_connection_reset
        
        print("\n[INFO] Applying database connection reset...")
        success = await force_connection_reset()
        
        if success:
            print("\n[SUCCESS] Database connection fix applied successfully!")
            print("[INFO] You can now try using the application again.")
            return True
        else:
            print("\n[ERROR] Database connection fix failed.")
            print("[INFO] You may need to restart the application server.")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Fix script failed: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(apply_pgbouncer_fix())
        
        if success:
            print("\n" + "=" * 50)
            print("[RESULT] Fix applied successfully!")
            print("[NEXT] Try using the application again.")
        else:
            print("\n" + "=" * 50)
            print("[RESULT] Fix failed - manual intervention needed")
            print("[NEXT] Consider restarting the application server")
            
    except Exception as e:
        print(f"\n[CRITICAL] Fix script error: {str(e)}")
        sys.exit(1)
    
    print("=" * 50)