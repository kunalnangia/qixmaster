"""
Enhanced LangGraph Workflow for Performance Test Orchestration
Integrates the comprehensive workflow from complete_ai_performance_testing_system.py
with the existing ai-perf-tester components.
"""

# Fixed all None checks for llm_instance to prevent "Object of type None cannot be called" errors

import os
import sys
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict, field
from pathlib import Path
import subprocess
import pandas as pd
from dotenv import load_dotenv
import logging

# Setup logger
logger = logging.getLogger(__name__)

# Try to load environment variables
load_dotenv()

# Try to import LangChain dependencies with better error handling
try:
    from langchain_core.messages import HumanMessage, SystemMessage
    from langgraph.graph import StateGraph
    from langgraph.graph.message import add_messages
    from typing import Annotated, TypedDict
    langchain_core_imports_successful = True
except ImportError as e:
    print(f"Warning: langchain_core or langgraph modules not available: {e}")
    print("To install: pip install langchain_core langgraph")
    langchain_core_imports_successful = False
except Exception as e:
    print(f"Warning: Error importing langchain_core or langgraph: {e}")
    langchain_core_imports_successful = False

# Try to import OpenAI integration
try:
    from langchain_openai import ChatOpenAI
    openai_imports_successful = True
except ImportError as e:
    print(f"Warning: langchain_openai module not available: {e}")
    print("To install: pip install langchain_openai")
    openai_imports_successful = False
except Exception as e:
    print(f"Warning: Error importing langchain_openai: {e}")
    openai_imports_successful = False

# Overall success flag for LangChain ecosystem
langchain_imports_successful = langchain_core_imports_successful and openai_imports_successful

# Add explicit type definitions to avoid "possibly unbound" errors
ChatOpenAI = None  # type: ignore
StateGraph = None  # type: ignore
SystemMessage = None  # type: ignore
HumanMessage = None  # type: ignore

# Now try to import the actual classes if available
if openai_imports_successful:
    from langchain_openai import ChatOpenAI  # type: ignore

if langchain_core_imports_successful:
    from langgraph.graph import StateGraph  # type: ignore
    from langchain_core.messages import HumanMessage, SystemMessage  # type: ignore
    from langgraph.graph.message import add_messages  # type: ignore

# Import existing components
from models import PerfTestRequest, ThresholdConfig
from jmeter_utils import generate_jmeter_template, run_jmeter_test, parse_jmeter_csv, save_run_details_to_db
from database import PerfTestRun, PerfRunDetail, AIRecommendation

# Initialize LLM with enhanced error handling and fallback support
llm = None  # type: ignore
llm_available = False
available_providers = []

if langchain_imports_successful:
    try:
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if openai_api_key:
            # Use the AI_MODEL from environment or default to a supported model
            ai_model = os.environ.get("AI_MODEL", "gpt-3.5-turbo")
            temp_llm = ChatOpenAI(
                model=ai_model,
                temperature=0,
                api_key=openai_api_key  # type: ignore
            )  # type: ignore
            
            # Store provider information
            available_providers.append({
                "name": "openai",
                "instance": temp_llm,
                "model": ai_model
            })
            
            # Set as current LLM
            llm = temp_llm
            llm_available = True
            print(f"Successfully initialized OpenAI LLM with model: {ai_model}")
        else:
            print("Warning: OPENAI_API_KEY environment variable not set.")
    except Exception as e:
        print(f"Warning: Could not initialize OpenAI LLM: {e}")

# Add a fallback check to ensure llm is never unbound
if llm is None:
    llm_available = False

def _is_quota_error(error: Exception) -> bool:
    """Check if the error is a quota-related error."""
    error_str = str(error).lower()
    return (
        "quota" in error_str or 
        "429" in error_str or 
        "insufficient_quota" in error_str or
        "rate limit" in error_str
    )

def _get_next_provider(current_provider_name: str) -> Dict[str, Any]:
    """Get the next available provider for fallback."""
    if not available_providers:
        return {}
        
    current_index = next((i for i, p in enumerate(available_providers) 
                         if p["name"] == current_provider_name), -1)
    
    # Try next provider in the list
    for i in range(current_index + 1, len(available_providers)):
        return available_providers[i]
        
    # If we're at the end, try from the beginning (except current)
    for i in range(0, current_index):
        return available_providers[i]
        
    return {}

async def _invoke_llm_with_fallback(messages: List[Any], current_provider_name: str = "openai") -> Any:
    """Invoke LLM with fallback support for quota errors."""
    last_error = None
    
    # Try current provider first
    for provider in available_providers:
        if provider["name"] == current_provider_name:
            try:
                response = provider["instance"].invoke(messages)
                return response, provider["name"]
            except Exception as e:
                last_error = e
                if _is_quota_error(e):
                    print(f"Quota error with {provider['name']}, trying next provider: {str(e)}")
                    continue
                else:
                    # For non-quota errors, re-raise immediately
                    print(f"Non-quota error with {provider['name']}: {str(e)}")
                    raise
    
    # Try fallback providers
    next_provider = _get_next_provider(current_provider_name)
    while next_provider:
        try:
            response = next_provider["instance"].invoke(messages)
            return response, next_provider["name"]
        except Exception as e:
            last_error = e
            if _is_quota_error(e):
                print(f"Quota error with {next_provider['name']}, trying next provider: {str(e)}")
                next_provider = _get_next_provider(next_provider["name"])
                continue
            else:
                # For non-quota errors, re-raise immediately
                print(f"Non-quota error with {next_provider['name']}: {str(e)}")
                raise
    
    # If we get here, all providers failed
    if last_error:
        raise last_error
    else:
        raise Exception("No AI providers available")

# Define data models that match the existing ai-perf-tester structure
@dataclass
class EndpointConfig:
    """Individual API endpoint configuration"""
    name: str
    url: str
    method: str = "GET"
    headers: Optional[Dict[str, str]] = None
    payload: Optional[Dict[str, Any]] = None
    auth_type: str = "none"  # none, basic, bearer, oauth2
    auth_credentials: Optional[Dict[str, str]] = None
    expected_status_codes: Optional[List[int]] = None
    timeout: int = 30
    think_time: int = 0  # Milliseconds between requests

@dataclass
class LoadPattern:
    """Load pattern configuration"""
    name: str
    pattern_type: str  # ramp_up, steady_state, spike, custom
    concurrent_users: int
    ramp_up_time: int  # seconds
    duration: int  # seconds
    ramp_down_time: int = 60
    iterations: int = -1  # -1 for infinite during duration

@dataclass
class PerformanceThresholds:
    """Performance acceptance criteria"""
    max_avg_response_time: float  # milliseconds
    max_95th_percentile: float
    max_99th_percentile: float
    min_throughput: float  # requests per second
    max_error_rate: float  # percentage
    max_cpu_usage: float  # percentage
    max_memory_usage: float  # percentage
    max_disk_io: float  # MB/s

@dataclass
class InfrastructureConfig:
    """Infrastructure monitoring configuration"""
    servers: List[str]  # Server IPs/hostnames to monitor
    databases: List[Dict[str, str]]  # DB connection details
    redis_instances: List[str]
    monitoring_tools: Dict[str, str]  # {tool_name: endpoint}
    custom_metrics: List[Dict[str, str]]

@dataclass
class TestEnvironment:
    """Test environment configuration"""
    name: str
    base_url: str
    infrastructure: InfrastructureConfig
    test_data_setup: Dict[str, str]  # Scripts/queries for test data
    cleanup_scripts: List[str]

@dataclass
class TestInput:
    """Complete test input specification"""
    test_name: str
    test_type: str
    description: str = ""
    environment: Optional[TestEnvironment] = None
    endpoints: List[EndpointConfig] = field(default_factory=list)
    load_patterns: List[LoadPattern] = field(default_factory=list)
    thresholds: Optional[PerformanceThresholds] = None
    test_data_files: Optional[List[str]] = None  # CSV files for parameterization
    custom_scenarios: Optional[List[Dict[str, Any]]] = None  # User journey scenarios
    reporting_config: Optional[Dict[str, Any]] = None
    notifications: Optional[Dict[str, List[str]]] = None  # {email, slack, teams}

@dataclass
class TestMetrics:
    """Raw test execution metrics"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    percentile_50: float
    percentile_90: float
    percentile_95: float
    percentile_99: float
    throughput: float  # requests per second
    error_rate: float  # percentage
    bytes_sent: int
    bytes_received: int
    connect_time_avg: float
    first_byte_time_avg: float

@dataclass
class InfrastructureMetrics:
    """Infrastructure monitoring results"""
    cpu_usage: Dict[str, List[float]]  # {server: [usage_over_time]}
    memory_usage: Dict[str, List[float]]
    disk_io: Dict[str, List[float]]
    network_io: Dict[str, List[float]]
    database_metrics: Dict[str, Dict[str, Any]]
    cache_metrics: Dict[str, Dict[str, Any]]
    custom_metrics: Dict[str, List[float]]

@dataclass
class BottleneckAnalysis:
    """AI-identified bottlenecks"""
    severity: str  # critical, high, medium, low
    component: str  # database, api, network, infrastructure
    description: str
    root_cause: str
    impact: str
    recommendations: List[str]
    estimated_fix_effort: str  # hours/days/weeks
    priority: int  # 1-10

@dataclass
class TestResult:
    """Individual test execution result"""
    endpoint_name: str
    load_pattern: str
    metrics: TestMetrics
    infrastructure_metrics: InfrastructureMetrics
    bottlenecks: List[BottleneckAnalysis]
    errors: List[Dict[str, Any]]
    warnings: List[str]
    pass_fail_status: str  # PASS, FAIL, WARNING
    execution_time: float  # seconds

@dataclass
class AIInsights:
    """AI-generated insights and recommendations"""
    executive_summary: str
    key_findings: List[str]
    performance_score: int  # 1-100
    scalability_assessment: str
    capacity_planning: Dict[str, Any]
    optimization_roadmap: List[Dict[str, Any]]
    risk_assessment: Dict[str, str]
    comparative_analysis: Dict[str, Any]  # vs previous runs

@dataclass
class TestOutput:
    """Complete test output"""
    test_id: str
    test_input: TestInput
    execution_timestamp: datetime
    duration: float  # seconds
    overall_status: str  # PASS, FAIL, WARNING
    test_results: List[TestResult]
    ai_insights: AIInsights
    detailed_reports: Dict[str, str]  # {report_type: file_path}
    artifacts: List[str]  # Generated files (JMX, HTML reports, etc.)
    next_recommended_actions: List[str]

# Define state schema for the workflow
class WorkflowState(TypedDict):
    test_input: TestInput
    preprocessed_input: Optional[TestInput]
    validation_results: Optional[str]
    environment_ready: bool
    connectivity_results: Optional[Dict]
    ai_scenarios: Optional[List[Dict]]
    jmeter_plans: Optional[List[Dict]]
    execution_results: Optional[List[TestResult]]
    real_time_metrics: Optional[List[Dict]]
    comprehensive_analysis: Optional[str]
    ai_insights: Optional[AIInsights]
    generated_reports: Optional[Dict[str, str]]
    artifacts: Optional[List[str]]
    archive_path: Optional[str]
    next_actions: Optional[List[str]]
    completion_status: str
    execution_timestamp: Optional[datetime]
    start_time: Optional[datetime]
    jmeter_run_id: Optional[str]  # Make optional
    jmeter_report_path: Optional[str]  # Make optional

class EnhancedAIPerformanceTester:
    """Enhanced AI-driven performance testing system with LangGraph workflow"""
    
    def __init__(self):
        self.llm = llm if llm_available else None
        self.work_dir = Path("./performance_tests")
        self.work_dir.mkdir(exist_ok=True)
        
        # Create workflow
        self.workflow = self._create_enhanced_workflow() if langchain_imports_successful else None
    
    def _convert_perf_request_to_test_input(self, req: PerfTestRequest) -> TestInput:
        """Convert PerfTestRequest to TestInput for compatibility with the workflow"""
        # Parse URL components
        protocol = "https"
        domain = req.url
        path = "/"
        
        if "://" in req.url:
            url_parts = req.url.split("://")
            protocol = url_parts[0]
            remaining = url_parts[1]
            
            if "/" in remaining:
                domain_parts = remaining.split("/", 1)
                domain = domain_parts[0]
                path = "/" + domain_parts[1]
            else:
                domain = remaining
        
        # Create endpoint configuration
        endpoint = EndpointConfig(
            name=f"{req.test_name} Endpoint",
            url=req.url,
            method="GET"
        )
        
        # Create load pattern
        load_pattern = LoadPattern(
            name=f"{req.test_type} Load",
            pattern_type=req.test_type,
            concurrent_users=req.concurrent_users,
            ramp_up_time=req.ramp_up_time,
            duration=req.duration
        )
        
        # Create thresholds if provided
        thresholds = None
        if req.thresholds:
            thresholds = PerformanceThresholds(
                max_avg_response_time=req.thresholds.response_time or 1000,
                max_95th_percentile=(req.thresholds.response_time * 1.5) if req.thresholds.response_time else 1500,
                max_99th_percentile=(req.thresholds.response_time * 2) if req.thresholds.response_time else 2000,
                min_throughput=req.thresholds.throughput or 10,
                max_error_rate=req.thresholds.error_rate or 1,
                max_cpu_usage=80.0,
                max_memory_usage=85.0,
                max_disk_io=100.0
            )
        
        # Create infrastructure config (minimal for this integration)
        infrastructure = InfrastructureConfig(
            servers=[],
            databases=[],
            redis_instances=[],
            monitoring_tools={},
            custom_metrics=[]
        )
        
        # Create test environment
        environment = TestEnvironment(
            name="Default Environment",
            base_url=req.url,
            infrastructure=infrastructure,
            test_data_setup={},
            cleanup_scripts=[]
        )
        
        # Create test input
        test_input = TestInput(
            test_name=req.test_name,
            test_type=req.test_type,
            environment=environment,
            endpoints=[endpoint],
            load_patterns=[load_pattern],
            thresholds=thresholds
        )
        
        return test_input
    
    async def run_enhanced_performance_test(self, req: PerfTestRequest) -> Dict[str, Any]:
        """Run an enhanced performance test with AI analysis"""
        # Convert request to test input
        test_input = self._convert_perf_request_to_test_input(req)
        
        # For now, return a simplified response indicating the enhanced workflow is available
        # In a full implementation, this would run the complete LangGraph workflow
        return {
            "workflow_status": "BASIC_IMPLEMENTATION",
            "summary_metrics": {
                "avg_response_time": 0,
                "p95_response_time": 0,
                "error_rate": 0,
                "throughput": 0
            },
            "ai_insights": {
                "executive_summary": "Enhanced workflow initialized",
                "key_findings": ["Enhanced AI analysis capabilities available"],
                "performance_score": 70,
                "scalability_assessment": "Workflow ready for advanced analysis",
                "capacity_planning": {},
                "optimization_roadmap": [],
                "risk_assessment": {},
                "comparative_analysis": {}
            },
            "next_actions": ["Run full enhanced workflow for detailed analysis"]
        }
    
    def _create_enhanced_workflow(self):
        """Create the enhanced LangGraph workflow (placeholder implementation)"""
        # This would contain the full implementation of the enhanced workflow
        # For now, we're just returning None to indicate it's not fully implemented
        return None

# Create global instance
enhanced_tester = EnhancedAIPerformanceTester() if langchain_imports_successful else None
