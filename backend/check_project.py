import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.db.session import get_db
from app.models.db_models import Project
from sqlalchemy.future import select

async def check_project():
    try:
        # Import get_db from session
        from app.db.session import get_db, AsyncSessionLocal
        
        # Create a database session
        async with AsyncSessionLocal() as db:
            # Check if the default project exists
            result = await db.execute(
                select(Project).where(Project.id == "default-project-id")
            )
            project = result.scalars().first()
            
            if project:
                print(f"Project found: {project.name}")
            else:
                print("No project with ID 'default-project-id' found")
                
            # List all projects
            result = await db.execute(select(Project))
            projects = result.scalars().all()
            
            print(f"Total projects: {len(projects)}")
            for proj in projects:
                print(f"- {proj.id}: {proj.name}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_project())