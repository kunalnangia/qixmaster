from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import subprocess
import json
import logging
import uuid
from datetime import datetime
import os

from app.db.session import get_db
from app.models.db_models import User
from app.core.security import get_current_user
from app.schemas.test_case import TestCaseResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Remove the prefix here since it's added in main.py
router = APIRouter(tags=["newman"])

class NewmanTestRequest(BaseModel):
    collection_url: str
    api_key: str
    test_case_id: Optional[str] = None
    environment: Optional[Dict[str, Any]] = None

class NewmanTestResponse(BaseModel):
    run_id: str
    success: bool
    results: Dict[str, Any]
    duration: float
    timestamp: datetime

def check_docker_newman():
    """Check if Docker and Newman are available"""
    try:
        # Check if Docker is available
        docker_result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if docker_result.returncode != 0:
            return False, "Docker is not available"
        
        # Check if Newman image is available, pull if not
        inspect_result = subprocess.run(
            ["docker", "image", "inspect", "postman/newman"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if inspect_result.returncode != 0:
            # Try to pull the image
            logger.info("Newman Docker image not found, pulling...")
            pull_result = subprocess.run(
                ["docker", "pull", "postman/newman"],
                capture_output=True,
                text=True,
                timeout=120
            )
            if pull_result.returncode != 0:
                return False, f"Failed to pull Newman Docker image: {pull_result.stderr}"
        
        # Test Newman
        test_result = subprocess.run(
            ["docker", "run", "--rm", "-t", "postman/newman", "--version"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if test_result.returncode != 0:
            return False, f"Newman Docker test failed: {test_result.stderr}"
        
        return True, "Docker Newman is ready"
    except subprocess.TimeoutExpired:
        return False, "Docker command timed out"
    except FileNotFoundError:
        return False, "Docker is not installed"
    except Exception as e:
        return False, f"Error checking Docker Newman: {str(e)}"

@router.post("/run", response_model=NewmanTestResponse)
async def run_newman_test(
    request: NewmanTestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Restore authentication
):
    """
    Run a Postman collection using Newman via Docker
    """
    run_id = str(uuid.uuid4())
    start_time = datetime.now()
    
    try:
        # Check if Docker Newman is available
        is_ready, message = check_docker_newman()
        if not is_ready:
            logger.error(f"Docker Newman not ready: {message}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Docker Newman not ready: {message}"
            )
        
        # Construct the Newman command
        # If the collection_url already contains the full URL, use it as is
        # Otherwise, construct it from the collection ID and API key
        if request.collection_url.startswith('http'):
            collection_url = request.collection_url
        else:
            collection_url = f"https://api.getpostman.com/collections/{request.collection_url}?apikey={request.api_key}"
        
        # Build the Docker command
        cmd = [
            "docker", "run", "--rm", "-t",
            "postman/newman",
            "run", collection_url
        ]
        
        # Add environment variables if provided
        if request.environment:
            # Create individual --env-var arguments
            for key, value in request.environment.items():
                cmd.extend(["--env-var", f"{key}={value}"])
        
        logger.info(f"Executing Newman command: {' '.join(cmd)}")
        
        # Run the Docker command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Parse the output
        output_lines = result.stdout.strip().split('\n')
        
        # Try to parse the last line as JSON (Newman's JSON reporter output)
        newman_results = {}
        try:
            # Look for JSON output in the last few lines
            for line in reversed(output_lines):
                if line.startswith('{'):
                    newman_results = json.loads(line)
                    break
        except json.JSONDecodeError:
            # If JSON parsing fails, use the raw output
            newman_results = {
                "raw_output": result.stdout,
                "error_output": result.stderr,
                "return_code": result.returncode
            }
        
        # Check if the test was successful
        success = result.returncode == 0
        
        # Log the results
        logger.info(f"Newman test completed. Success: {success}, Duration: {duration}s")
        
        return NewmanTestResponse(
            run_id=run_id,
            success=success,
            results=newman_results,
            duration=duration,
            timestamp=end_time
        )
        
    except subprocess.TimeoutExpired:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.error("Newman test timed out")
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="Newman test timed out after 5 minutes"
        )
    except FileNotFoundError:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.error("Docker not found")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Docker is not installed. Newman tests require Docker to be installed and running."
        )
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.error(f"Error running Newman test: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running Newman test: {str(e)}"
        )
