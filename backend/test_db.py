from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
db_url = os.getenv("DATABASE_URL")

if not db_url:
    print("❌ DATABASE_URL not found in environment variables")
    exit(1)

print(f"🔍 Testing connection to database...")

try:
    # Create engine and test connection
    engine = create_engine(db_url)
    with engine.connect() as conn:
        print("✅ Successfully connected to the database!")
        print("\n📋 Listing tables in the database:")
        # Use text() for raw SQL
        result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"))
        for row in result:
            print(f"- {row[0]}")
        
        # Test a simple query
        print("\n🔍 Testing a simple query...")
        result = conn.execute(text("SELECT version();"))
        version = result.scalar()
        print(f"✅ Database version: {version}")

except Exception as e:
    print(f"❌ Database connection failed: {e}")