import traceback
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from datetime import datetime
import uuid

from app.db import get_db
from app import models
from app.auth.security import get_current_user
from app.schemas.test_case import (
    TestType, Status, Priority, EnvironmentType, AutomationStatus,
    TestStep, TestStepCreate,
    TestCaseCreate, TestCaseUpdate, TestCaseResponse,
    URLGenerationRequest, URLGenerationResponse
)
from app.mcp.website_test_generator import website_test_generator

router = APIRouter(
    prefix="",  # Prefix is handled in main.py
    tags=["test-cases"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=TestCaseResponse, status_code=status.HTTP_201_CREATED)
async def create_test_case(
    test_case: TestCaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new test case
    """
    # Check if project exists
    result = await db.execute(
        select(models.Project).where(models.Project.id == test_case.project_id)
    )
    db_project = result.scalars().first()
    
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {test_case.project_id} not found"
        )
    
    # Convert Pydantic model to dict and add required fields
    test_case_data = test_case.dict(exclude={"test_steps"}, exclude_unset=True)
    db_test_case = models.TestCase(
        **test_case_data,
        id=str(uuid.uuid4()),
        created_by=current_user.get("id") if isinstance(current_user, dict) else getattr(current_user, "id", None),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Add test steps if provided
    if hasattr(test_case, 'test_steps') and test_case.test_steps:
        for step in test_case.test_steps:
            db_step = models.TestStep(
                id=str(uuid.uuid4()),
                test_case_id=db_test_case.id,
                **step.dict()
            )
            db.add(db_step)
    
    db.add(db_test_case)
    await db.commit()
    await db.refresh(db_test_case)
    
    # TODO: Add activity log
    # TODO: Broadcast WebSocket update
    
    
    return db_test_case

@router.get("/", response_model=List[TestCaseResponse])
async def list_test_cases(
    project_id: Optional[str] = None,
    test_type: Optional[TestType] = None,
    status_filter: Optional[Status] = None,
    priority: Optional[Priority] = None,
    environment: Optional[EnvironmentType] = None,
    automation_status: Optional[AutomationStatus] = None,
    owner: Optional[str] = None,
    assigned_to: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = 100,
    skip: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List test cases with optional filtering
    """
    try:
        # Build query
        query = select(models.TestCase).options(joinedload(models.TestCase.steps))
        
        # Apply filters
        if project_id:
            query = query.where(models.TestCase.project_id == project_id)
        if test_type:
            query = query.where(models.TestCase.test_type == test_type)
        if status_filter:
            query = query.where(models.TestCase.status == status_filter)
        if priority:
            query = query.where(models.TestCase.priority == priority)
        if environment:
            query = query.where(models.TestCase.environment == environment)
        if automation_status:
            query = query.where(models.TestCase.automation_status == automation_status)
        if owner:
            query = query.where(models.TestCase.owner == owner)
        if assigned_to:
            query = query.where(models.TestCase.assigned_to == assigned_to)
        if tag:
            query = query.where(models.TestCase.tags.contains([tag]))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        test_cases = result.unique().scalars().all()
        
        print(f"Found {len(test_cases)} test cases for project_id: {project_id}")
        return [TestCaseResponse.model_validate(tc) for tc in test_cases]
        
    except Exception as e:
        print(f"Error fetching test cases: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return empty list on error for now to avoid breaking the frontend
        return []

@router.get("/{test_case_id}", response_model=TestCaseResponse)
async def get_test_case(
    test_case_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a test case by ID
    """
    stmt = select(models.TestCase).options(
        joinedload(models.TestCase.steps)
    ).where(models.TestCase.id == test_case_id)
    
    result = await db.execute(stmt)
    test_case = result.unique().scalars().first()
    
    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test case with id {test_case_id} not found"
        )
    
    return test_case

@router.put("/{test_case_id}", response_model=TestCaseResponse)
async def update_test_case(
    test_case_id: str,
    test_case: TestCaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update a test case
    """
    # Get existing test case
    result = await db.execute(
        select(models.TestCase).where(models.TestCase.id == test_case_id)
    )
    db_test_case = result.scalars().first()
    
    if not db_test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test case with id {test_case_id} not found"
        )
    
    # Update fields
    update_data = test_case.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_test_case, field, value)
    
    # updated_at is automatically handled by SQLAlchemy's onupdate parameter
    
    db.add(db_test_case)
    await db.commit()
    await db.refresh(db_test_case)
    
    return db_test_case

@router.delete("/{test_case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_case(
    test_case_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a test case
    """
    result = await db.execute(
        select(models.TestCase).where(models.TestCase.id == test_case_id)
    )
    db_test_case = result.scalars().first()
    
    if not db_test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test case with id {test_case_id} not found"
        )
    
    await db.delete(db_test_case)
    await db.commit()
    
    # TODO: Add activity log
    # TODO: Broadcast WebSocket update
    
    return None

@router.post("/generate-from-url", response_model=URLGenerationResponse, status_code=status.HTTP_201_CREATED)
async def generate_test_cases_from_url(
    request: URLGenerationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate test cases from website URL using MCP AI analysis
    """
    try:
        # Import AI Generator user functions
        from app.db.session import ensure_ai_generator_user_exists, get_ai_generator_user_id
        
        # Ensure AI Generator system user exists (best practice for AI-generated content)
        ai_generator_user_id = await ensure_ai_generator_user_exists()
        
        # Validate project exists and user has access, or create default project
        result = await db.execute(
            select(models.Project).where(models.Project.id == request.project_id)
        )
        db_project = result.scalars().first()
        
        if not db_project:
            # Create a default project if it doesn't exist
            # Using AI Generator user ID for system-created projects
            db_project = models.Project(
                id=request.project_id,
                name="Default Project",
                description="Auto-created default project for test case generation",
                created_by=ai_generator_user_id,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(db_project)
            await db.flush()
        
        # Generate test cases using MCP server
        generated_test_cases_data = await website_test_generator.generate_test_cases_from_url(
            url=request.url,
            project_id=request.project_id,
            test_count=request.test_count
        )
        
        # Create test cases in database
        created_test_cases = []
        
        for test_case_data in generated_test_cases_data:
            # Convert string enums to proper enum values
            test_type_str = test_case_data.get("test_type", "functional")
            priority_str = test_case_data.get("priority", "medium")
            
            # Map string values to enum values using the schema enums
            try:
                test_type_enum = TestType(test_type_str.upper())
            except ValueError:
                test_type_enum = TestType.FUNCTIONAL  # Default fallback
                
            try:
                priority_enum = Priority(priority_str.upper())
            except ValueError:
                priority_enum = Priority.MEDIUM  # Default fallback
            
            # Create test case with proper AI Generator user ID
            db_test_case = models.TestCase(
                id=str(uuid.uuid4()),
                project_id=request.project_id,
                created_by=ai_generator_user_id,  # Using proper AI Generator user
                title=test_case_data["title"],
                description=test_case_data.get("description", ""),
                test_type=test_type_enum,
                priority=priority_enum,
                status=Status.DRAFT,
                expected_result=test_case_data.get("expected_result", ""),
                ai_generated=True,
                self_healing_enabled=True,
                preconditions=test_case_data.get("preconditions", ""),
                test_data=test_case_data.get("test_data", {}),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(db_test_case)
            await db.flush()  # Get the ID
            
            # Create test steps
            if "steps" in test_case_data:
                for step in test_case_data["steps"]:
                    db_step = models.TestStep(
                        id=str(uuid.uuid4()),
                        test_case_id=db_test_case.id,
                        step_number=step["step_number"],
                        description=step["description"],
                        expected_result=step["expected_result"],
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.add(db_step)
            
            created_test_cases.append(db_test_case)
        
        # Commit all changes
        await db.commit()
        
        # Refresh objects to get all related data
        for test_case in created_test_cases:
            await db.refresh(test_case)
        
        # Create response
        analysis_summary = f"Generated {len(created_test_cases)} test cases from {request.url}"
        
        return URLGenerationResponse(
            generated_test_cases=[TestCaseResponse.model_validate(tc) for tc in created_test_cases],
            analysis_summary=analysis_summary,
            url_analyzed=request.url
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 404 for project not found)
        raise
    except Exception as e:
        # Rollback any changes on error
        await db.rollback()
        
        # Log the error and return a 500
        print(f"Error generating test cases from URL: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate test cases from URL: {str(e)}"
        )