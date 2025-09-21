import psycopg2
from urllib.parse import urlparse
import os

def get_projects_table_details():
    # Connection parameters from .env file
    db_url = "postgresql://postgres.lflecyuvttemfoyixngi:Ayeshaayesha121@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
    
    try:
        # Parse the database URL
        result = urlparse(db_url)
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        port = result.port
        
        print(f"Connecting to {hostname}:{port}/{database} as {username}...")
        
        # Connect to the database
        conn = psycopg2.connect(
            dbname=database,
            user=username,
            password=password,
            host=hostname,
            port=port,
            sslmode="require"
        )
        
        # Create a cursor
        cur = conn.cursor()
        
        # Get the PostgreSQL version
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"\n✅ Connected to PostgreSQL {version[0]}")
        
        # Get detailed column information for the 'projects' table
        table_name = 'projects'
        print(f"\nGetting detailed column information for '{table_name}' table:")
        
        cur.execute(f"""
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length,
                numeric_precision,
                numeric_scale
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = '{table_name}'
            ORDER BY ordinal_position;
        """)
        
        columns = cur.fetchall()
        
        if columns:
            print(f"\nColumns in '{table_name}' table:")
            print(f"{'Column Name':<25} {'Data Type':<20} {'Nullable':<10} {'Default Value':<20} {'Max Length':<12} {'Precision':<10} {'Scale'}")
            print("-" * 120)
            
            for col in columns:
                column_name, data_type, is_nullable, column_default, max_length, precision, scale = col
                print(f"{column_name:<25} {data_type:<20} {is_nullable:<10} {str(column_default):<20} {str(max_length):<12} {str(precision):<10} {str(scale)}")
            
            # Get primary key information
            cur.execute(f"""
                SELECT a.attname
                FROM pg_index i
                JOIN pg_attribute a ON a.attrelid = i.indrelid 
                    AND a.attnum = ANY(i.indkey)
                WHERE i.indrelid = '{table_name}'::regclass
                AND i.indisprimary;
            """)
            
            primary_keys = cur.fetchall()
            if primary_keys:
                print(f"\nPrimary Key(s): {', '.join([pk[0] for pk in primary_keys])}")
            
            # Get foreign key information
            cur.execute(f"""
                SELECT
                    kcu.column_name, 
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM 
                    information_schema.table_constraints AS tc 
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                      AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                      AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY' 
                AND tc.table_name = '{table_name}';
            """)
            
            foreign_keys = cur.fetchall()
            if foreign_keys:
                print(f"\nForeign Keys:")
                for fk in foreign_keys:
                    print(f"  {fk[0]} -> {fk[1]}({fk[2]})")
            else:
                print(f"\nNo foreign keys found for '{table_name}' table.")
                
        else:
            print(f"\nNo columns found for '{table_name}' table.")
        
        # Close the cursor and connection
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error connecting to the database:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")
        
        # More specific error handling
        if "password authentication failed" in str(e).lower():
            print("\n🔑 Authentication failed. Please check your username and password.")
        elif "connection timed out" in str(e).lower():
            print("\n⏱️ Connection timed out. Check your network and firewall settings.")
        elif "no pg_hba.conf entry" in str(e).lower():
            print("\n🔒 No pg_hba.conf entry. Your IP might not be whitelisted in Supabase.")
        
        print("\n🔧 Troubleshooting steps:")
        print("1. Verify your IP is whitelisted in Supabase")
        print("2. Check if the database server is running and accessible")
        print("3. Try connecting with a different client (like DBeaver or pgAdmin)")

if __name__ == "__main__":
    get_projects_table_details()