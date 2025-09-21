from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from enum import Enum

# Import the Status enum from the database models instead of test_case
from app.models.db_models import Status

# TestPlan model
class TestPlanBase(BaseModel):
    name: str
    description: Optional[str] = None
    project_id: str
    status: Status = Status.DRAFT
    scheduled_date: Optional[datetime] = None

class TestPlanCreate(TestPlanBase):
    pass

class TestPlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[Status] = None
    scheduled_date: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class TestPlanResponse(TestPlanBase):
    id: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    test_case_ids: List[str] = []
    
    model_config = ConfigDict(from_attributes=True)