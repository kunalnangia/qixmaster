import psycopg2
from psycopg2 import OperationalError
import os
import sys
from dotenv import load_dotenv

def test_ssl_mode(sslmode):
    """Test a specific SSL mode with the database."""
    # Load environment variables
    load_dotenv()
    
    # Get database credentials from environment variables
    db_host = os.getenv('DB_HOST', 'db.lflecyuvttemfoyixngi.supabase.co')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'postgres')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD')
    
    if not db_password:
        raise ValueError("DB_PASSWORD environment variable is not set")
    
    try:
        conn_params = {
            'host': db_host,
            'port': db_port,
            'database': db_name,
            'user': db_user,
            'password': db_password,
            'sslmode': sslmode,
            'connect_timeout': 5
        }
        
        print("Attempting to connect...")
        conn = psycopg2.connect(**conn_params)
        print("✅ Connection successful!")
        
        # Test a simple query
        with conn.cursor() as cur:
            cur.execute("SELECT version()")
            version = cur.fetchone()[0]
            print(f"PostgreSQL version: {version}")
            
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        
        # More detailed error information
        if isinstance(e, psycopg2.OperationalError):
            print("\nPossible solutions:")
            print("1. Check if the database server is running and accessible")
            print("2. Verify the hostname and port are correct")
            print("3. Check if your IP is whitelisted in Supabase")
            print("4. Try a different SSL mode")
            print("5. Check Supabase dashboard for any service issues")
    
    finally:
        if conn is not None:
            conn.close()
            print("Connection closed.")

if __name__ == "__main__":
    # Test different SSL modes
    for sslmode in ['disable', 'allow', 'prefer', 'require', 'verify-ca', 'verify-full']:
        test_connection(sslmode)
