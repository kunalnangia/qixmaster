import psycopg2
from urllib.parse import urlparse
import sys
import os
from dotenv import load_dotenv

def test_connection():
    """Test connection to Supabase database using environment variables."""
    # Load environment variables
    load_dotenv()
    
    # Get database credentials from environment variables
    db_name = os.getenv('DB_NAME', 'postgres')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = int(os.getenv('DB_PORT', '5432'))
    
    # Validate required environment variables
    if not all([db_user, db_password, db_host]):
        raise ValueError("DB_USER, DB_PASSWORD, and DB_HOST environment variables must be set")
    
    print(f"Connecting to database: {db_user}@{db_host}:{db_port}/{db_name}")
    
    try:
        # Connect to the database
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            sslmode='require',
            connect_timeout=10
        )
        
        # If we get here, connection was successful
        print("✅ Successfully connected to the database!")
        
        # Get database version
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            print(f"\n📊 Database version: {version}")
            
            # Get list of tables
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            
            tables = [row[0] for row in cur.fetchall()]
            print(f"\n📋 Found {len(tables)} tables in the database:")
            for table in tables:
                print(f"  • {table}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed!")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {str(e)}")
        
        # Provide specific troubleshooting tips based on error
        if "Connection refused" in str(e):
            print("\n🔧 Troubleshooting:")
            print("1. Check if the database server is running")
            print("2. Verify the hostname and port are correct")
            print("3. Check if your IP is whitelisted in the database firewall")
            
        elif "authentication failed" in str(e).lower():
            print("\n🔧 Troubleshooting:")
            print("1. Verify the username and password are correct")
            print("2. Check if the user has permission to access the database")
            
        elif "does not exist" in str(e).lower():
            print("\n🔧 Troubleshooting:")
            print("1. Verify the database name is correct")
            print("2. The database may need to be created")
            
        return False

if __name__ == "__main__":
    # Test with the provided connection string
    connection_string = "postgresql://postgres:Ayeshaayesha121@db.lflecyuvttemfoyixngi.supabase.co:5432/postgres"
    success = test_connection(connection_string)
    
    if not success:
        print("\n❌ Database connection test failed. Please check the error message above.")
        sys.exit(1)
    else:
        print("\n✅ Database connection test completed successfully!")
