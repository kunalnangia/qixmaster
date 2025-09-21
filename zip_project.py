import os
import zipfile
import sys
from pathlib import Path

def zip_project(project_dir, output_zip):
    """
    Create a zip archive of the entire project
    """
    print(f"Creating zip archive of {project_dir} to {output_zip}")
    
    # Get absolute paths
    project_dir = os.path.abspath(project_dir)
    output_zip = os.path.abspath(output_zip)
    
    # Ensure the project directory exists
    if not os.path.exists(project_dir):
        print(f"Error: Project directory {project_dir} does not exist")
        return False
    
    # Create zip file
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk through all files and directories
        for root, dirs, files in os.walk(project_dir):
            # Skip __pycache__ directories and virtual environments
            dirs[:] = [d for d in dirs if d != '__pycache__' and d != '.venv' and d != 'node_modules' and d != '.git']
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # Skip the zip file itself if it's in the project directory
                if os.path.abspath(file_path) == output_zip:
                    continue
                
                # Skip .pyc files
                if file.endswith('.pyc'):
                    continue
                
                # Calculate the relative path for the zip file
                rel_path = os.path.relpath(file_path, start=os.path.dirname(project_dir))
                
                # Add the file to the zip
                print(f"Adding {rel_path}")
                zipf.write(file_path, rel_path)
    
    print(f"Successfully created {output_zip}")
    return True

if __name__ == "__main__":
    # Default project directory is the current directory
    project_dir = "ai-perf-tester"
    
    # Default output zip name
    output_zip = "ai-perf-tester.zip"
    
    # Check if custom paths were provided
    if len(sys.argv) > 1:
        project_dir = sys.argv[1]
    
    if len(sys.argv) > 2:
        output_zip = sys.argv[2]
    
    # Zip the project
    zip_project(project_dir, output_zip)