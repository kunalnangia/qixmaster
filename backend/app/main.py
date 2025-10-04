import os
import sys
import logging
import json
import traceback
import uuid
import asyncio
import subprocess
from datetime import datetime, timedelta
from typing import Optional, List
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from pydantic import BaseModel, EmailStr

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import core components and dependencies, including the new async functions
from app.db.session import get_db, get_db_sync, sync_engine, initialize_database, force_connection_reset
from app.core.security import create_access_token, get_password_hash, verify_password, oauth2_scheme
from app.auth.security import AuthService
from app.websocket.manager import WebSocketManager
from app.core.logging_config import setup_queue_logging, get_queue_logger

# Import schemas
from app.schemas.user import UserCreate, UserLogin
from app.schemas.project import ProjectCreate, Project as ProjectResponse

# Import database models (must be after session to avoid circular imports)
from app.models.db_models import (
    User, Project, Team, TestCase, TestStep, TestPlan, TestExecution,
    Comment, TeamMember, Environment, Attachment, TestPlanTestCase, ActivityLog
)

# Import the new database CRUD operations
from app.db.crud import ensure_test_user_exists, ensure_ai_generator_user_exists
# Import API routers
from app.api.v1.routes import (
    test_cases, teams, environments, attachments, projects, comments,
    auth, executions, ai, newman, test_plans
)

# Configure logging
logger = setup_queue_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_dir="logs"
)
logger.info("=" * 80)
logger.info("Application starting with queue-based logging")
logger.info("=" * 80)

# Initialize the WebSocket manager
websocket_manager = WebSocketManager()

# Access token expiration time in minutes
ACCESS_TOKEN_EXPIRE_MINUTES = 30

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events.
    This function is now responsible for initializing the database asynchronously.
    """
    logger.info("Starting database initialization with a 30-second timeout...")
    try:
        # Asynchronously initialize the database engine by calling the new function
        async_engine_instance = await initialize_database()
        
        # Now, force a connection reset to ensure PgBouncer compatibility
        await asyncio.wait_for(force_connection_reset(), timeout=30.0)
        
        logger.info("[SUCCESS] Database connections reset for PgBouncer compatibility")

        logger.info("Ensuring test user and AI generator user exist...")
        # Use the asynchronously created engine instance for database operations
        test_user_id = await ensure_test_user_exists(async_engine_instance)
        ai_user_id = await ensure_ai_generator_user_exists(async_engine_instance)
        logger.info(f"[SUCCESS] Test user ready: {test_user_id}")
        logger.info(f"[SUCCESS] AI Generator user ready: {ai_user_id}")

    except asyncio.TimeoutError:
        logger.error("[ERROR] Database initialization timed out after 30 seconds.")
        logger.warning("[OFFLINE MODE] Starting application without full database initialization")
        logger.warning("[OFFLINE MODE] Some features may not work properly until database is available")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        logger.error(traceback.format_exc())
        logger.warning("[OFFLINE MODE] Starting application without full database initialization")
        logger.warning("[OFFLINE MODE] Some features may not work properly until database is available")

    # Your Docker Newman initialization logic can stay here
    # ...

    yield
    logger.info("Application shutdown")

app = FastAPI(
    title="IntelliTest AI Automation Platform",
    description="Enterprise-grade AI-powered test automation platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# CORS middleware configuration
origins = [
    "http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176",
    "http://127.0.0.1:5173", "http://127.0.0.1:5174", "http://127.0.0.1:5175", "http://127.0.0.1:5176",
    "http://localhost:3000", "http://127.0.0.1:3000",
    "http://localhost:8000", "http://127.001:8000", "http://127.0.0.1:8001", "http://127.0.0.1:8001",
    "http://192.168.1.2:5175", "http://192.168.1.2:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600
)

# Create API router with /api prefix
api_router = APIRouter(prefix="/api")

# Attach routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(test_cases.router, prefix="/api/v1")
app.include_router(teams.router, prefix="/api/v1")
app.include_router(environments.router, prefix="/api/v1")
app.include_router(attachments.router, prefix="/api/v1")
app.include_router(comments.router, prefix="/api/v1")
app.include_router(executions.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(newman.router, prefix="/api/v1")
app.include_router(test_plans.router, prefix="/api/v1")

# Include the main API router in the application
app.include_router(api_router)

# Add a simple root endpoint to confirm the server is running
@app.get("/")
async def read_root():
    return {"message": "Welcome to the IntelliTest API!"}

# WebSocket endpoint
@app.websocket("/api/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "join_room":
                    await websocket_manager.join_room(user_id, message.get("room_id"))
                elif message.get("type") == "leave_room":
                    await websocket_manager.leave_room(user_id, message.get("room_id"))
            except Exception as e:
                logger.error(f"WebSocket message handling error: {e}")
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
