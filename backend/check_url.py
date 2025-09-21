import os
from dotenv import load_dotenv
import sys

# Load environment variables from the root .env file
# Try multiple possible paths to find the .env file
env_paths = [
    '../.env',  # Original path
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'),  # Root directory
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'),  # Alternative path
]

env_loaded = False
for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"Loaded .env file from: {env_path}")
        env_loaded = True
        break

if not env_loaded:
    print("Warning: Could not find .env file in any expected location")

# Get database URL with proper null checking
db_url = os.getenv('DATABASE_URL')
if db_url is None:
    print("Error: DATABASE_URL not found in environment variables")
    sys.exit(1)

print(f"DATABASE_URL: {db_url[:100]}...")

# Construct async URL
async_url = str(db_url).replace('postgresql://', 'postgresql+asyncpg://')
print(f"Async URL before modification: {async_url[:100]}...")

# Add statement_cache_size parameter
if 'statement_cache_size' not in async_url:
    async_url += ('&' if '?' in async_url else '?') + 'statement_cache_size=0'
    
print(f"Async URL after modification: {async_url[:100]}...")