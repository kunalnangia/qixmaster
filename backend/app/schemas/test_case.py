from pydantic import BaseModel, Field, ConfigDict, HttpUrl
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

# Complete TestType enum
class TestType(str, Enum):
    FUNCTIONAL = "functional"
    REGRESSION = "regression"
    SMOKE = "smoke"
    UAT = "uat"
    PERFORMANCE = "performance"
    SECURITY = "security"
    API = "api"
    VISUAL = "visual"
    INTEGRATION = "integration"
    UNIT = "unit"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Status(str, Enum):
    DRAFT = "draft"
    READY = "ready"
    PASS = "pass"
    FAIL = "fail"
    BLOCKED = "blocked"
    NOT_RUN = "not_run"

class EnvironmentType(str, Enum):
    DEV = "dev"
    QA = "qa"
    STAGING = "staging"
    PROD = "prod"

class AutomationStatus(str, Enum):
    MANUAL = "manual"
    AUTOMATED = "automated"
    CANDIDATE = "candidate"

# TestStep model
class TestStepBase(BaseModel):
    step_number: int
    description: str
    expected_result: str
    actual_result: Optional[str] = None

class TestStepCreate(TestStepBase):
    pass

class TestStep(TestStepBase):
    id: str
    test_case_id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# TestCase model with all required fields
class TestCaseBase(BaseModel):
    # Basic Information
    title: str
    description: Optional[str] = None
    requirement_reference: Optional[str] = None  # Jira/Requirement ID
    test_type: TestType = TestType.FUNCTIONAL
    priority: Priority = Priority.MEDIUM
    status: Status = Status.DRAFT
    module_feature: Optional[str] = None  # Area of the application
    tags: List[str] = []
    version_build: Optional[str] = None  # Application version being tested
    
    # Execution-Focused Fields
    preconditions: Optional[str] = None  # Setup/data/environment required
    test_data: Optional[Dict[str, Any]] = None  # Inputs, files, parameters, credentials
    expected_result: Optional[str] = None
    actual_result: Optional[str] = None
    environment: Optional[EnvironmentType] = None
    automation_status: Optional[AutomationStatus] = AutomationStatus.MANUAL
    
    # Ownership and Tracking
    owner: Optional[str] = None  # Who created/owns the test
    assigned_to: Optional[str] = None
    
    # Collaboration & Reporting Fields
    linked_defects: List[str] = []  # Integration with bug tracker
    attachments: List[str] = []  # Screenshots, logs, API payloads, UX mocks

class TestCaseCreate(TestCaseBase):
    project_id: str
    test_steps: List[TestStepCreate] = []

class TestCaseUpdate(BaseModel):
    # Make all fields optional for updates
    title: Optional[str] = None
    description: Optional[str] = None
    requirement_reference: Optional[str] = None
    test_type: Optional[TestType] = None
    priority: Optional[Priority] = None
    status: Optional[Status] = None
    module_feature: Optional[str] = None
    tags: Optional[List[str]] = None
    version_build: Optional[str] = None
    preconditions: Optional[str] = None
    test_data: Optional[Dict[str, Any]] = None
    expected_result: Optional[str] = None
    actual_result: Optional[str] = None
    environment: Optional[EnvironmentType] = None
    automation_status: Optional[AutomationStatus] = None
    owner: Optional[str] = None
    assigned_to: Optional[str] = None
    linked_defects: Optional[List[str]] = None
    attachments: Optional[List[str]] = None
    
    model_config = ConfigDict(from_attributes=True)

# Response model
class TestCaseResponse(TestCaseBase):
    id: str
    project_id: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    test_steps: List[TestStep] = []
    ai_generated: bool = False
    self_healing_enabled: bool = False
    
    model_config = ConfigDict(from_attributes=True)

# URL Generation Schema for MCP Server
class URLGenerationRequest(BaseModel):
    url: str = Field(..., description="Website URL to analyze for test case generation")
    project_id: str = Field(..., description="Project ID where test cases will be created")
    test_count: int = Field(default=5, ge=1, le=10, description="Number of test cases to generate (1-10)")
    
class URLGenerationResponse(BaseModel):
    generated_test_cases: List[TestCaseResponse]
    analysis_summary: str
    url_analyzed: str