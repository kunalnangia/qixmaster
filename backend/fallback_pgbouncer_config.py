#!/usr/bin/env python3
"""
Fallback PgBouncer Configuration Script
Use this if direct connection has issues and you need to fall back to PgBouncer with enhanced fixes
"""
import os
import sys
from datetime import datetime

def apply_fallback_pgbouncer_config():
    """Apply fallback PgBouncer configuration with maximum prepared statement disabling"""
    
    print("=" * 70)
    print("PgBouncer Fallback Configuration Script")
    print("=" * 70)
    print(f"Run time: {datetime.now()}")
    print()
    
    try:
        # Path to .env file
        env_file_path = os.path.join(os.path.dirname(__file__), '.env')
        
        if not os.path.exists(env_file_path):
            print(f"[ERROR] .env file not found at: {env_file_path}")
            return False
        
        # Read current .env content
        with open(env_file_path, 'r') as f:
            content = f.read()
        
        print("[INFO] Switching back to PgBouncer with enhanced prepared statement disabling...")
        
        # Replace database URLs to use PgBouncer with maximum compatibility settings
        new_content = content.replace(
            'DATABASE_URL="postgresql://postgres:Ayeshaayesha121@db.lflecyuvttemfoyixngi.supabase.co:5432/postgres"',
            'DATABASE_URL="postgresql://postgres.lflecyuvttemfoyixngi:Ayeshaayesha121@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"'
        )
        
        new_content = new_content.replace(
            'DATABASE_URL_ASYNC="postgresql+asyncpg://postgres:Ayeshaayesha121@db.lflecyuvttemfoyixngi.supabase.co:5432/postgres"',
            'DATABASE_URL_ASYNC="postgresql+asyncpg://postgres.lflecyuvttemfoyixngi:Ayeshaayesha121@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres?statement_cache_size=0&prepared_statement_cache_size=0&server_side_cursors=false"'
        )
        
        # Update comments
        new_content = new_content.replace(
            '# SOLUTION: Using direct PostgreSQL connection (bypassing PgBouncer) to eliminate prepared statement conflicts',
            '# FALLBACK: Using PgBouncer with maximum prepared statement disabling for compatibility'
        )
        
        new_content = new_content.replace(
            '# Direct connection (RECOMMENDED) - Bypasses PgBouncer, uses asyncpg\'s native pooling',
            '# PgBouncer connection with enhanced prepared statement disabling'
        )
        
        new_content = new_content.replace(
            '# Async connection (for FastAPI operations) - Direct connection with asyncpg native pooling',
            '# Async connection (for FastAPI operations) - PgBouncer with maximum compatibility settings'
        )
        
        new_content = new_content.replace(
            '# PgBouncer alternatives (if direct connection has issues)',
            '# Direct connection alternatives (if PgBouncer still has issues)'
        )
        
        # Write updated content
        with open(env_file_path, 'w') as f:
            f.write(new_content)
        
        print("[SUCCESS] .env file updated with fallback PgBouncer configuration")
        print()
        print("Applied settings:")
        print("  ✓ Using PgBouncer pooler endpoint")
        print("  ✓ statement_cache_size=0")
        print("  ✓ prepared_statement_cache_size=0") 
        print("  ✓ server_side_cursors=false")
        print()
        print("This configuration maximally disables prepared statement caching to work with PgBouncer.")
        print()
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to apply fallback configuration: {str(e)}")
        return False

def print_fallback_instructions():
    """Print instructions for using the fallback configuration"""
    print("=" * 70)
    print("FALLBACK CONFIGURATION APPLIED")
    print("=" * 70)
    print()
    print("⚠️  Now using PgBouncer with maximum prepared statement disabling")
    print()
    print("NEXT STEPS:")
    print()
    print("1. Restart your application to pick up the new configuration:")
    print("   cd C:\\Users\\kunal\\Downloads\\qix-master\\qix-master\\backend")
    print("   uvicorn app.main:app --reload --host 127.0.0.1 --port 8001")
    print()
    print("2. Test the application functionality")
    print()
    print("3. If you still get prepared statement errors:")
    print("   - Run: python fix_pgbouncer.py")
    print("   - Consider contacting Supabase support about PgBouncer settings")
    print()
    print("4. To switch back to direct connection:")
    print("   - Edit .env file manually")
    print("   - Or run: python test_direct_connection.py")
    print()
    print("=" * 70)

def main():
    """Main execution function"""
    
    success = apply_fallback_pgbouncer_config()
    
    if success:
        print_fallback_instructions()
        print("[RESULT] Fallback configuration applied successfully")
        return 0
    else:
        print("[RESULT] Failed to apply fallback configuration")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"[CRITICAL ERROR] Script execution failed: {str(e)}")
        sys.exit(1)