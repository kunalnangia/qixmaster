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
from app.schemas.test_plan import TestPlanCreate, TestPlanUpdate, TestPlanResponse
from app.models.db_models import Status

router = APIRouter(
    prefix="",  # Prefix is handled in main.py
    tags=["test-plans"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=TestPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_test_plan(
    test_plan: TestPlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new test plan
    """
    # Check if project exists
    result = await db.execute(
        select(models.Project).where(models.Project.id == test_plan.project_id)
    )
    db_project = result.scalars().first()
    
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {test_plan.project_id} not found"
        )
    
    # Convert Pydantic model to dict and add required fields
    test_plan_data = test_plan.dict(exclude_unset=True)
    db_test_plan = models.TestPlan(
        **test_plan_data,
        id=str(uuid.uuid4()),
        created_by=current_user.get("id") if isinstance(current_user, dict) else getattr(current_user, "id", None),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(db_test_plan)
    await db.commit()
    await db.refresh(db_test_plan)
    
    return TestPlanResponse(
        id=str(db_test_plan.id),
        name=str(db_test_plan.name),
        description=str(db_test_plan.description) if db_test_plan.description is not None else None,
        project_id=str(db_test_plan.project_id),
        created_by=str(db_test_plan.created_by),
        status=getattr(db_test_plan, 'status', Status.DRAFT),
        scheduled_date=getattr(db_test_plan, 'scheduled_start', None),
        created_at=getattr(db_test_plan, 'created_at', datetime.utcnow()),
        updated_at=getattr(db_test_plan, 'updated_at', datetime.utcnow()),
        test_case_ids=[]
    )

@router.get("/", response_model=List[TestPlanResponse])
async def list_test_plans(
    project_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    limit: int = 100,
    skip: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List test plans with optional filtering
    """
    try:
        # Build query
        query = select(models.TestPlan)
        
        # Apply filters
        if project_id:
            query = query.where(models.TestPlan.project_id == project_id)
        if status_filter:
            query = query.where(models.TestPlan.status == status_filter)
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        test_plans = result.scalars().all()
        
        # Get test case IDs for each test plan
        response_list = []
        for test_plan in test_plans:
            # Get associated test case IDs
            test_case_ids_result = await db.execute(
                select(models.TestPlanTestCase.test_case_id)
                .where(models.TestPlanTestCase.test_plan_id == test_plan.id)
            )
            test_case_ids = [row[0] for row in test_case_ids_result.all()]
            
            response_list.append(TestPlanResponse(
                id=str(test_plan.id),
                name=str(test_plan.name),
                description=str(test_plan.description) if test_plan.description is not None else None,
                project_id=str(test_plan.project_id),
                created_by=str(test_plan.created_by),
                status=getattr(test_plan, 'status', Status.DRAFT),
                scheduled_date=getattr(test_plan, 'scheduled_start', None),
                created_at=getattr(test_plan, 'created_at', datetime.utcnow()),
                updated_at=getattr(test_plan, 'updated_at', datetime.utcnow()),
                test_case_ids=test_case_ids
            ))
        
        return response_list
        
    except Exception as e:
        print(f"Error fetching test plans: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return empty list on error for now to avoid breaking the frontend
        return []

@router.get("/{test_plan_id}", response_model=TestPlanResponse)
async def get_test_plan(
    test_plan_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a test plan by ID
    """
    stmt = select(models.TestPlan).where(models.TestPlan.id == test_plan_id)
    
    result = await db.execute(stmt)
    test_plan = result.scalars().first()
    
    if not test_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test plan with id {test_plan_id} not found"
        )
    
    # Get associated test case IDs
    test_case_ids_result = await db.execute(
        select(models.TestPlanTestCase.test_case_id)
        .where(models.TestPlanTestCase.test_plan_id == test_plan.id)
    )
    test_case_ids = [row[0] for row in test_case_ids_result.all()]
    
    return TestPlanResponse(
        id=str(test_plan.id),
        name=str(test_plan.name),
        description=str(test_plan.description) if test_plan.description is not None else None,
        project_id=str(test_plan.project_id),
        created_by=str(test_plan.created_by),
        status=getattr(test_plan, 'status', Status.DRAFT),
        scheduled_date=getattr(test_plan, 'scheduled_start', None),
        created_at=getattr(test_plan, 'created_at', datetime.utcnow()),
        updated_at=getattr(test_plan, 'updated_at', datetime.utcnow()),
        test_case_ids=test_case_ids
    )

@router.put("/{test_plan_id}", response_model=TestPlanResponse)
async def update_test_plan(
    test_plan_id: str,
    test_plan: TestPlanUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update a test plan
    """
    # Get existing test plan
    result = await db.execute(
        select(models.TestPlan).where(models.TestPlan.id == test_plan_id)
    )
    db_test_plan = result.scalars().first()
    
    if not db_test_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test plan with id {test_plan_id} not found"
        )
    
    # Update fields
    update_data = test_plan.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "scheduled_date":
            setattr(db_test_plan, "scheduled_start", value)
        else:
            setattr(db_test_plan, field, value)
    
    setattr(db_test_plan, 'updated_at', datetime.utcnow())
    
    db.add(db_test_plan)
    await db.commit()
    await db.refresh(db_test_plan)
    
    # Get associated test case IDs
    test_case_ids_result = await db.execute(
        select(models.TestPlanTestCase.test_case_id)
        .where(models.TestPlanTestCase.test_plan_id == db_test_plan.id)
    )
    test_case_ids = [row[0] for row in test_case_ids_result.all()]
    
    return TestPlanResponse(
        id=str(db_test_plan.id),
        name=str(db_test_plan.name),
        description=str(db_test_plan.description) if db_test_plan.description is not None else None,
        project_id=str(db_test_plan.project_id),
        created_by=str(db_test_plan.created_by),
        status=getattr(db_test_plan, 'status', Status.DRAFT),
        scheduled_date=getattr(db_test_plan, 'scheduled_start', None),
        created_at=getattr(db_test_plan, 'created_at', datetime.utcnow()),
        updated_at=getattr(db_test_plan, 'updated_at', datetime.utcnow()),
        test_case_ids=test_case_ids
    )

@router.delete("/{test_plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_plan(
    test_plan_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a test plan
    """
    result = await db.execute(
        select(models.TestPlan).where(models.TestPlan.id == test_plan_id)
    )
    db_test_plan = result.scalars().first()
    
    if not db_test_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test plan with id {test_plan_id} not found"
        )
    
    await db.delete(db_test_plan)
    await db.commit()
    
    return None