# Pydantic models for AI Performance Tester
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class ThresholdConfig(BaseModel):
    response_time: Optional[float] = Field(1000, description="Response time threshold in ms")
    error_rate: Optional[float] = Field(1, description="Error rate threshold in percentage")
    throughput: Optional[float] = Field(10, description="Throughput threshold in requests per second")

class PerfTestRequest(BaseModel):
    test_name: str
    test_type: str = Field(..., description="Type of test: load, stress, spike, endurance")
    url: str
    concurrent_users: int = Field(10, ge=1, description="Number of concurrent users")
    duration: int = Field(60, ge=1, description="Test duration in seconds")
    ramp_up_time: int = Field(10, ge=0, description="Ramp-up time in seconds")
    thresholds: Optional[ThresholdConfig] = None
    custom_parameters: Optional[Dict[str, Any]] = None

class AIAnalysisRequest(BaseModel):
    run_id: str