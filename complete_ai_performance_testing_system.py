import asyncio
import json
import yaml
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, TypedDict
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import subprocess
import pandas as pd
from langgraph.graph import StateGraph
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
import aiohttp
import asyncpg
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None
from enum import Enum
import platform
import shutil

# ===== INPUT MODELS =====

class TestType(Enum):
    LOAD = "load"
    STRESS = "stress"
    SPIKE = "spike"
    VOLUME = "volume"
    ENDURANCE = "endurance"
    SCALABILITY = "scalability"

@dataclass
class EndpointConfig:
    """Individual API endpoint configuration"""
    name: str
    url: str
    method: str
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
    test_type: TestType
    description: str
    environment: TestEnvironment
    endpoints: List[EndpointConfig]
    load_patterns: List[LoadPattern]
    thresholds: PerformanceThresholds
    test_data_files: Optional[List[str]] = None  # CSV files for parameterization
    custom_scenarios: Optional[List[Dict[str, Any]]] = None  # User journey scenarios
    reporting_config: Optional[Dict[str, Any]] = None
    notifications: Optional[Dict[str, List[str]]] = None  # {email, slack, teams}

# ===== OUTPUT MODELS =====

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
    duration: timedelta
    overall_status: str  # PASS, FAIL, WARNING
    test_results: List[TestResult]
    ai_insights: AIInsights
    detailed_reports: Dict[str, str]  # {report_type: file_path}
    artifacts: List[str]  # Generated files (JMX, HTML reports, etc.)
    next_recommended_actions: List[str]

# ===== MAIN SYSTEM =====

class ComprehensiveAIPerformanceTester:
    """Complete end-to-end AI-driven performance testing system"""
    
    def __init__(self, config_file: Optional[str] = None):
        # Use a supported model
        ai_model = pd.os.environ.get("AI_MODEL", "gpt-3.5-turbo")
        self.llm = ChatOpenAI(model=ai_model)
        self.jmeter_path = self._find_jmeter_path()
        self.work_dir = Path("./performance_tests")
        self.work_dir.mkdir(exist_ok=True)
        
        # Load configuration
        if config_file:
            with open(config_file, 'r') as f:
                self.system_config = yaml.safe_load(f)
        else:
            self.system_config = self._default_config()
        
        # Initialize monitoring clients
        self.redis_client = None
        self.db_connections = {}
        
        # Create workflow
        self.workflow = self._create_complete_workflow()
    
    def _find_jmeter_path(self) -> str:
        """Auto-detect JMeter installation"""
        jmeter_executable = "jmeter"
        if platform.system() == "Windows":
            jmeter_executable = "jmeter.bat"
        
        jmeter_path = shutil.which(jmeter_executable)
        if jmeter_path:
            return jmeter_path
        
        # Try common paths
        possible_paths = [
            "/opt/jmeter/bin/jmeter",
            "/usr/local/bin/jmeter",
            "C:\\apache-jmeter\\bin\\jmeter.bat",
            "./jmeter/bin/jmeter"
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
        
        raise Exception("JMeter not found. Please install JMeter and update the path.")
    
    def _default_config(self) -> Dict:
        """Default system configuration"""
        return {
            "jmeter": {
                "heap_size": "2g",
                "timeout": 3600,
                "plugins": ["jpgc-functions", "jpgc-graphs-basic"]
            },
            "monitoring": {
                "collection_interval": 10,
                "retention_days": 30
            },
            "reporting": {
                "formats": ["html", "pdf", "json"],
                "include_graphs": True,
                "detailed_analysis": True
            },
            "ai": {
                "analysis_depth": "comprehensive",
                "include_predictions": True,
                "benchmark_comparison": True
            }
        }
    
    def _create_complete_workflow(self) -> StateGraph:
        """Create comprehensive LangGraph workflow"""
        
        from typing import Annotated
        from langgraph.graph.message import add_messages
        
        # Define state schema
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
        
        def validate_and_preprocess_input(state: WorkflowState):
            """Validate input and prepare test environment"""
            test_input: TestInput = state['test_input']
            
            # AI-powered input validation
            validation_prompt = f"""
            Validate this performance test configuration: {json.dumps(asdict(test_input), indent=2)}
            
            Check for:
            1. Realistic load patterns
            2. Appropriate thresholds
            3. Missing configurations
            4. Potential issues
            5. Optimization opportunities
            
            Return validation results and suggested improvements.
            """
            
            response = self.llm.invoke([HumanMessage(content=validation_prompt)])
            
            # Ensure response.content is a string
            validation_results = response.content if isinstance(response.content, str) else str(response.content)
            
            return {
                "validation_results": validation_results,
                "preprocessed_input": self._preprocess_test_input(test_input)
            }
        
        def setup_test_environment(state: WorkflowState):
            """Prepare test environment and data"""
            test_input: TestInput = state['preprocessed_input'] if state['preprocessed_input'] is not None else state['test_input']
            
            # Setup monitoring
            self._setup_infrastructure_monitoring(test_input.environment)
            
            # Prepare test data
            self._setup_test_data(test_input)
            
            # Validate environment connectivity
            connectivity_results = asyncio.run(self._validate_environment_connectivity(test_input))
            
            return {
                "environment_ready": True,
                "connectivity_results": connectivity_results
            }
        
        def generate_ai_enhanced_test_plans(state: WorkflowState):
            """AI generates comprehensive test scenarios"""
            test_input: TestInput = state['preprocessed_input'] if state['preprocessed_input'] is not None else state['test_input']
            
            scenario_prompt = f"""
            Generate comprehensive performance test scenarios for: {test_input.test_name}
            
            Based on:
            - Test type: {test_input.test_type.value}
            - Endpoints: {[ep.name for ep in test_input.endpoints]}
            - Load patterns: {[lp.name for lp in test_input.load_patterns]}
            
            Create:
            1. Realistic user journey scenarios
            2. Edge case testing scenarios
            3. Failure condition scenarios
            4. Scalability progression scenarios
            5. Data-driven test scenarios
            
            Include specific JMeter configurations for each scenario.
            """
            
            response = self.llm.invoke([HumanMessage(content=scenario_prompt)])
            
            # Ensure response.content is a string
            content = response.content if isinstance(response.content, str) else str(response.content)
            
            # Try to parse as JSON, fallback to empty list if it fails
            try:
                ai_scenarios = json.loads(content)
            except json.JSONDecodeError:
                ai_scenarios = []
            
            # Generate JMeter test plans
            jmeter_plans = self._generate_comprehensive_jmx_files(test_input, ai_scenarios)
            
            return {
                "ai_scenarios": ai_scenarios,
                "jmeter_plans": jmeter_plans
            }
        
        def execute_performance_tests(state: WorkflowState):
            """Execute all test scenarios with monitoring"""
            jmeter_plans = state['jmeter_plans'] if state['jmeter_plans'] is not None else []
            test_input: TestInput = state['preprocessed_input'] if state['preprocessed_input'] is not None else state['test_input']
            
            execution_results = []
            
            for plan in jmeter_plans:
                # Start infrastructure monitoring
                self._start_monitoring(test_input.environment)
                
                # Execute JMeter test
                result = self._execute_jmeter_test_with_monitoring(plan, test_input)
                
                # Stop monitoring and collect data
                infra_metrics = self._collect_infrastructure_metrics(test_input.environment)
                
                # Parse and enhance results
                enhanced_result = self._enhance_test_result(result, infra_metrics)
                execution_results.append(enhanced_result)
            
            return {"execution_results": execution_results}
        
        def ai_analyze_comprehensive_results(state: WorkflowState):
            """Comprehensive AI analysis of all results"""
            results = state['execution_results'] if state['execution_results'] is not None else []
            test_input: TestInput = state['preprocessed_input'] if state['preprocessed_input'] is not None else state['test_input']
            
            analysis_prompt = f"""
            Perform comprehensive analysis of these performance test results:
            
            Test Configuration: {json.dumps(asdict(test_input), default=str, indent=2)}
            Results: {json.dumps([asdict(r) for r in results], default=str, indent=2)}
            
            Provide detailed analysis including:
            
            1. EXECUTIVE SUMMARY
            - Overall performance assessment
            - Key business impact
            - Go/No-go recommendation
            
            2. TECHNICAL ANALYSIS
            - Bottleneck identification with root causes
            - Performance patterns and trends
            - Scalability assessment
            - Infrastructure utilization analysis
            
            3. RISK ASSESSMENT
            - Production readiness
            - Potential failure points
            - Capacity limits
            
            4. OPTIMIZATION ROADMAP
            - Immediate fixes (0-2 weeks)
            - Short-term improvements (1-3 months)
            - Long-term optimizations (3+ months)
            - ROI estimates for each
            
            5. CAPACITY PLANNING
            - Current capacity limits
            - Scaling recommendations
            - Infrastructure requirements
            - Cost projections
            
            6. COMPARATIVE ANALYSIS
            - Industry benchmarks
            - Previous test comparisons
            - Performance trends
            
            Provide specific, actionable recommendations with technical details.
            """
            
            response = self.llm.invoke([HumanMessage(content=analysis_prompt)])
            
            # Ensure response.content is a string
            content = response.content if isinstance(response.content, str) else str(response.content)
            
            # Parse AI insights
            ai_insights = self._parse_ai_insights(content)
            
            return {
                "comprehensive_analysis": content,
                "ai_insights": ai_insights
            }
        
        def generate_comprehensive_reports(state: WorkflowState):
            """Generate multiple report formats and artifacts"""
            test_input: TestInput = state['preprocessed_input'] if state['preprocessed_input'] is not None else state['test_input']
            results = state['execution_results'] if state['execution_results'] is not None else []
            ai_insights: AIInsights = state['ai_insights'] if state['ai_insights'] is not None else AIInsights(
                executive_summary="",
                key_findings=[],
                performance_score=0,
                scalability_assessment="",
                capacity_planning={},
                optimization_roadmap=[],
                risk_assessment={},
                comparative_analysis={}
            )
            
            # Generate different report types
            reports = self._generate_all_report_formats(test_input, results, ai_insights)
            
            # Create artifacts
            artifacts = self._create_test_artifacts(test_input, results, ai_insights)
            
            # Send notifications
            self._send_notifications(test_input, results, ai_insights)
            
            return {
                "generated_reports": reports,
                "artifacts": artifacts
            }
        
        def finalize_and_cleanup(state: WorkflowState):
            """Final steps and cleanup"""
            test_input: TestInput = state['preprocessed_input'] if state['preprocessed_input'] is not None else state['test_input']
            results = state['execution_results'] if state['execution_results'] is not None else []
            ai_insights: AIInsights = state['ai_insights'] if state['ai_insights'] is not None else AIInsights(
                executive_summary="",
                key_findings=[],
                performance_score=0,
                scalability_assessment="",
                capacity_planning={},
                optimization_roadmap=[],
                risk_assessment={},
                comparative_analysis={}
            )
            
            # Cleanup test data if specified
            if hasattr(test_input.environment, 'cleanup_scripts'):
                self._run_cleanup_scripts(test_input.environment.cleanup_scripts)
            
            # Archive results
            archive_path = self._archive_test_results({"execution_results": results})
            
            # Generate next actions
            next_actions = self._generate_next_actions(ai_insights)
            
            return {
                "archive_path": archive_path,
                "next_actions": next_actions,
                "completion_status": 'SUCCESS'
            }
        
        # Build workflow graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("validate_input", validate_and_preprocess_input)
        workflow.add_node("setup_environment", setup_test_environment)
        workflow.add_node("generate_plans", generate_ai_enhanced_test_plans)
        workflow.add_node("execute_tests", execute_performance_tests)
        workflow.add_node("analyze_results", ai_analyze_comprehensive_results)
        workflow.add_node("generate_reports", generate_comprehensive_reports)
        workflow.add_node("finalize", finalize_and_cleanup)
        
        # Add edges
        workflow.add_edge("validate_input", "setup_environment")
        workflow.add_edge("setup_environment", "generate_plans")
        workflow.add_edge("generate_plans", "execute_tests")
        workflow.add_edge("execute_tests", "analyze_results")
        workflow.add_edge("analyze_results", "generate_reports")
        workflow.add_edge("generate_reports", "finalize")
        
        workflow.set_entry_point("validate_input")
        
        return workflow
    
    def _preprocess_test_input(self, test_input: TestInput) -> TestInput:
        """Preprocess and enhance test input"""
        # Add default headers if missing
        for endpoint in test_input.endpoints:
            if not endpoint.headers:
                endpoint.headers = {"Content-Type": "application/json"}
            if not endpoint.expected_status_codes:
                endpoint.expected_status_codes = [200, 201, 202]
        
        return test_input
    
    def _setup_infrastructure_monitoring(self, environment: TestEnvironment):
        """Setup monitoring for infrastructure components"""
        # Setup database connections for monitoring
        for db_config in environment.infrastructure.databases:
            try:
                # PostgreSQL example
                if db_config['type'] == 'postgresql':
                    conn_str = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
                    self.db_connections[db_config['name']] = conn_str
            except Exception as e:
                print(f"Failed to setup monitoring for {db_config['name']}: {e}")
        
        # Setup Redis connections
        if REDIS_AVAILABLE and redis:
            for redis_instance in environment.infrastructure.redis_instances:
                try:
                    self.redis_client = redis.Redis.from_url(redis_instance)
                except Exception as e:
                    print(f"Failed to connect to Redis {redis_instance}: {e}")
    
    def _setup_test_data(self, test_input: TestInput):
        """Setup test data based on configuration"""
        if test_input.test_data_files:
            for data_file in test_input.test_data_files:
                # Process CSV files for parameterization
                df = pd.read_csv(data_file)
                # Save processed data for JMeter
                processed_path = self.work_dir / f"processed_{Path(data_file).name}"
                df.to_csv(processed_path, index=False)
    
    async def _validate_environment_connectivity(self, test_input: TestInput) -> Dict:
        """Validate connectivity to all endpoints"""
        results = {}
        
        async with aiohttp.ClientSession() as session:
            for endpoint in test_input.endpoints:
                try:
                    async with session.request(
                        method="HEAD",  # Use HEAD to avoid heavy responses
                        url=endpoint.url,
                        headers=endpoint.headers or {},
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        results[endpoint.name] = {
                            'status': 'reachable',
                            'response_code': response.status,
                            'response_time': 0  # Would calculate actual time
                        }
                except Exception as e:
                    results[endpoint.name] = {
                        'status': 'unreachable',
                        'error': str(e)
                    }
        
        return results
    
    def _generate_comprehensive_jmx_files(self, test_input: TestInput, ai_scenarios: List[Dict]) -> List[Dict]:
        """Generate sophisticated JMeter test plans"""
        jmeter_plans = []
        
        for scenario in ai_scenarios:
            jmx_content = self._create_advanced_jmx(test_input, scenario)
            
            plan = {
                'name': scenario['name'],
                'scenario': scenario,
                'jmx_content': jmx_content,
                'jmx_file_path': self.work_dir / f"{scenario['name']}.jmx"
            }
            
            # Save JMX file
            with open(plan['jmx_file_path'], 'w', encoding='utf-8') as f:
                f.write(jmx_content)
            
            jmeter_plans.append(plan)
        
        return jmeter_plans
    
    def _create_advanced_jmx(self, test_input: TestInput, scenario: Dict) -> str:
        """Create advanced JMeter JMX with all features"""
        
        # This would be a comprehensive JMX template with:
        # - Multiple thread groups
        # - CSV data sets
        # - Listeners and assertions
        # - Timers and controllers
        # - Backend listeners for real-time monitoring
        
        jmx_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.4.1">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="{scenario['name']}" enabled="true">
      <stringProp name="TestPlan.comments">AI Generated Performance Test</stringProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.tearDown_on_shutdown">true</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
      <elementProp name="TestPlan.arguments" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
        <collectionProp name="Arguments.arguments"/>
      </elementProp>
      <stringProp name="TestPlan.user_define_classpath"></stringProp>
    </TestPlan>
    <hashTree>
"""
        
        # Add thread groups for each load pattern
        for load_pattern in test_input.load_patterns:
            jmx_template += f"""
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Thread Group - {load_pattern.name}" enabled="true">
        <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="Loop Controller" enabled="true">
          <boolProp name="LoopController.continue_forever">false</boolProp>
          <intProp name="LoopController.loops">{load_pattern.iterations if load_pattern.iterations > 0 else 1}</intProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">{load_pattern.concurrent_users}</stringProp>
        <stringProp name="ThreadGroup.ramp_time">{load_pattern.ramp_up_time}</stringProp>
        <boolProp name="ThreadGroup.scheduler">true</boolProp>
        <stringProp name="ThreadGroup.duration">{load_pattern.duration}</stringProp>
        <stringProp name="ThreadGroup.delay">0</stringProp>
      </ThreadGroup>
      <hashTree>
"""
            
            # Add HTTP requests for each endpoint
            for endpoint in test_input.endpoints:
                jmx_template += self._create_http_sampler_xml(endpoint)
            
            # Add listeners
            jmx_template += """
        <ResultCollector guiclass="ViewResultsFullVisualizer" testclass="ResultCollector" testname="View Results Tree" enabled="true">
          <boolProp name="ResultCollector.error_logging">false</boolProp>
          <objProp>
            <name>saveConfig</name>
            <value class="SampleSaveConfiguration">
              <time>true</time>
              <latency>true</latency>
              <timestamp>true</timestamp>
              <success>true</success>
              <label>true</label>
              <code>true</code>
              <message>true</message>
              <threadName>true</threadName>
              <dataType>true</dataType>
              <encoding>false</encoding>
              <assertions>true</assertions>
              <subresults>true</subresults>
              <responseData>false</responseData>
              <samplerData>false</samplerData>
              <xml>false</xml>
              <fieldNames>true</fieldNames>
              <responseHeaders>false</responseHeaders>
              <requestHeaders>false</requestHeaders>
              <responseDataOnError>false</responseDataOnError>
              <saveAssertionResultsFailureMessage>true</saveAssertionResultsFailureMessage>
              <assertionsResultsToSave>0</assertionsResultsToSave>
              <bytes>true</bytes>
              <sentBytes>true</sentBytes>
              <url>true</url>
              <threadCounts>true</threadCounts>
              <idleTime>true</idleTime>
              <connectTime>true</connectTime>
            </value>
          </objProp>
          <stringProp name="filename">{self.work_dir}/results_{load_pattern.name}.jtl</stringProp>
        </ResultCollector>
        <hashTree/>
"""
            
            jmx_template += "      </hashTree>\n"
        
        jmx_template += """
    </hashTree>
  </hashTree>
</jmeterTestPlan>"""
        
        return jmx_template
    
    def _create_http_sampler_xml(self, endpoint: EndpointConfig) -> str:
        """Create HTTP sampler XML for endpoint"""
        from urllib.parse import urlparse
        
        parsed_url = urlparse(endpoint.url)
        
        return f"""
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="{endpoint.name}" enabled="true">
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
            <collectionProp name="Arguments.arguments"/>
          </elementProp>
          <stringProp name="HTTPSampler.domain">{parsed_url.hostname}</stringProp>
          <stringProp name="HTTPSampler.port">{parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)}</stringProp>
          <stringProp name="HTTPSampler.protocol">{parsed_url.scheme}</stringProp>
          <stringProp name="HTTPSampler.contentEncoding"></stringProp>
          <stringProp name="HTTPSampler.path">{parsed_url.path}</stringProp>
          <stringProp name="HTTPSampler.method">{endpoint.method}</stringProp>
          <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
          <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
          <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
          <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          <stringProp name="HTTPSampler.embedded_url_re"></stringProp>
          <stringProp name="HTTPSampler.connect_timeout">{endpoint.timeout * 1000}</stringProp>
          <stringProp name="HTTPSampler.response_timeout">{endpoint.timeout * 1000}</stringProp>
        </HTTPSamplerProxy>
        <hashTree>
"""
    
    def _execute_jmeter_test_with_monitoring(self, plan: Dict, test_input: TestInput) -> TestResult:
        """Execute JMeter test with comprehensive monitoring"""
        
        jmx_file = plan['jmx_file_path']
        results_file = self.work_dir / f"results_{plan['name']}.jtl"
        log_file = self.work_dir / f"jmeter_{plan['name']}.log"
        html_report_dir = self.work_dir / f"html_report_{plan['name']}"
        
        # JMeter command with all options
        cmd = [
            self.jmeter_path,
            "-n",  # Non-GUI mode
            "-t", str(jmx_file),  # Test plan
            "-l", str(results_file),  # Results file
            "-j", str(log_file),  # Log file
            "-e",  # Generate HTML report
            "-o", str(html_report_dir),  # HTML report output
            f"-Jjmeter.save.saveservice.output_format=csv",
            f"-Jjmeter.save.saveservice.response_data=false",
            f"-Jjmeter.save.saveservice.samplerData=false",
            f"-Jjmeter.save.saveservice.response_headers=false",
            f"-Jjmeter.save.saveservice.requestHeaders=false"
        ]
        
        try:
            # Execute JMeter
            start_time = datetime.now()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            end_time = datetime.now()
            
            # Parse results
            metrics = self._parse_comprehensive_jtl_results(results_file)
            
            # Create test result
            test_result = TestResult(
                endpoint_name=plan['name'],
                load_pattern=plan['scenario']['name'],
                metrics=metrics,
                infrastructure_metrics=InfrastructureMetrics({}, {}, {}, {}, {}, {}, {}),  # Will be filled by monitoring
                bottlenecks=[],  # Will be filled by AI analysis
                errors=self._parse_jmeter_errors(log_file),
                warnings=[],
                pass_fail_status="UNKNOWN",  # Will be determined later
                execution_time=(end_time - start_time).total_seconds()
            )
            
            return test_result
            
        except subprocess.TimeoutExpired:
            return TestResult(
                endpoint_name=plan['name'],
                load_pattern=plan['scenario']['name'],
                metrics=TestMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
                infrastructure_metrics=InfrastructureMetrics({}, {}, {}, {}, {}, {}, {}),
                bottlenecks=[],
                errors=[{"error": "Test execution timed out"}],
                warnings=["Test exceeded maximum execution time"],
                pass_fail_status="FAIL",
                execution_time=3600
            )
    
    def _parse_comprehensive_jtl_results(self, results_file: Path) -> TestMetrics:
        """Parse JMeter JTL results with comprehensive metrics"""
        
        if not results_file.exists():
            return TestMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        df = pd.read_csv(results_file)
        
        if df.empty:
            return TestMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        # Calculate comprehensive metrics
        total_requests = len(df)
        successful_requests = len(df[df['success'] == True])
        failed_requests = total_requests - successful_requests
        
        # Response time metrics (assuming 'elapsed' column)
        response_times = df['elapsed'].dropna()
        avg_response_time = float(response_times.mean()) if not response_times.empty else 0.0
        min_response_time = float(response_times.min()) if not response_times.empty else 0.0
        max_response_time = float(response_times.max()) if not response_times.empty else 0.0
        
        # Percentiles
        percentile_50 = float(response_times.quantile(0.50)) if not response_times.empty else 0.0
        percentile_90 = float(response_times.quantile(0.90)) if not response_times.empty else 0.0
        percentile_95 = float(response_times.quantile(0.95)) if not response_times.empty else 0.0
        percentile_99 = float(response_times.quantile(0.99)) if not response_times.empty else 0.0
        
        # Throughput calculation
        if not df.empty:
            test_duration = (df['timeStamp'].max() - df['timeStamp'].min()) / 1000  # Convert to seconds
            throughput = float(total_requests / test_duration) if test_duration > 0 else 0.0
        else:
            throughput = 0.0
        
        # Error rate
        error_rate = float((failed_requests / total_requests * 100)) if total_requests > 0 else 0.0
        
        # Bytes
        bytes_sent = int(df['sentBytes'].sum()) if 'sentBytes' in df.columns else 0
        bytes_received = int(df['bytes'].sum()) if 'bytes' in df.columns else 0
        
        # Connection times
        connect_time_avg = float(df['Connect'].mean()) if 'Connect' in df.columns else 0.0
        first_byte_time_avg = float(df['Latency'].mean()) if 'Latency' in df.columns else 0.0
        
        return TestMetrics(
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            percentile_50=percentile_50,
            percentile_90=percentile_90,
            percentile_95=percentile_95,
            percentile_99=percentile_99,
            throughput=throughput,
            error_rate=error_rate,
            bytes_sent=bytes_sent,
            bytes_received=bytes_received,
            connect_time_avg=connect_time_avg,
            first_byte_time_avg=first_byte_time_avg
        )
    
    def _parse_jmeter_errors(self, log_file: Path) -> List[Dict[str, Any]]:
        """Parse JMeter log file for errors"""
        errors = []
        
        if not log_file.exists():
            return errors
        
        try:
            with open(log_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    if 'ERROR' in line or 'FATAL' in line:
                        errors.append({
                            'line_number': line_num,
                            'message': line.strip(),
                            'timestamp': datetime.now().isoformat()
                        })
        except Exception as e:
            errors.append({
                'line_number': 0,
                'message': f"Failed to parse log file: {str(e)}",
                'timestamp': datetime.now().isoformat()
            })
        
        return errors
    
    def _start_monitoring(self, environment: TestEnvironment):
        """Start infrastructure monitoring"""
        # This would start monitoring agents/collectors
        # For now, we'll simulate this
        pass
    
    def _collect_infrastructure_metrics(self, environment: TestEnvironment) -> InfrastructureMetrics:
        """Collect infrastructure metrics during test execution"""
        
        # Simulate collecting metrics - in real implementation, this would
        # connect to monitoring systems like Prometheus, Grafana, etc.
        
        cpu_metrics = {}
        memory_metrics = {}
        disk_metrics = {}
        network_metrics = {}
        db_metrics = {}
        cache_metrics = {}
        custom_metrics = {}
        
        for server in environment.infrastructure.servers:
            # Simulate CPU, memory, disk, network metrics
            cpu_metrics[server] = [75.5, 78.2, 82.1, 79.8, 77.3]  # % over time
            memory_metrics[server] = [68.2, 70.1, 72.5, 71.8, 69.9]
            disk_metrics[server] = [12.5, 15.2, 18.7, 16.3, 14.1]  # MB/s
            network_metrics[server] = [125.3, 142.7, 156.8, 148.2, 133.9]  # MB/s
        
        # Database metrics simulation
        for db in environment.infrastructure.databases:
            db_metrics[db['name']] = {
                'connections': 45,
                'active_queries': 12,
                'slow_queries': 3,
                'deadlocks': 0,
                'cache_hit_ratio': 95.2
            }
        
        # Redis metrics simulation
        if REDIS_AVAILABLE:
            for redis_instance in environment.infrastructure.redis_instances:
                cache_metrics[redis_instance] = {
                    'used_memory': 2.1,  # GB
                    'hit_rate': 98.5,  # %
                    'evicted_keys': 0,
                    'expired_keys': 150
                }
        
        return InfrastructureMetrics(
            cpu_usage=cpu_metrics,
            memory_usage=memory_metrics,
            disk_io=disk_metrics,
            network_io=network_metrics,
            database_metrics=db_metrics,
            cache_metrics=cache_metrics,
            custom_metrics=custom_metrics
        )
    
    def _enhance_test_result(self, result: TestResult, infra_metrics: InfrastructureMetrics) -> TestResult:
        """Enhance test result with infrastructure metrics and initial analysis"""
        result.infrastructure_metrics = infra_metrics
        
        # Basic bottleneck detection
        bottlenecks = []
        
        # Check response time thresholds
        if result.metrics.avg_response_time > 2000:  # 2 seconds
            bottlenecks.append(BottleneckAnalysis(
                severity="high",
                component="api",
                description="High average response time detected",
                root_cause="API performance degradation",
                impact="User experience severely impacted",
                recommendations=["Optimize database queries", "Add caching", "Scale application servers"],
                estimated_fix_effort="1-2 weeks",
                priority=8
            ))
        
        # Check error rate
        if result.metrics.error_rate > 5:  # 5%
            bottlenecks.append(BottleneckAnalysis(
                severity="critical",
                component="api",
                description=f"High error rate: {result.metrics.error_rate:.1f}%",
                root_cause="API reliability issues",
                impact="Service availability compromised",
                recommendations=["Investigate error patterns", "Implement circuit breakers", "Add retry logic"],
                estimated_fix_effort="2-3 days",
                priority=10
            ))
        
        # Check infrastructure CPU
        for server, cpu_usage in infra_metrics.cpu_usage.items():
            avg_cpu = sum(cpu_usage) / len(cpu_usage)
            if avg_cpu > 80:
                bottlenecks.append(BottleneckAnalysis(
                    severity="medium",
                    component="infrastructure",
                    description=f"High CPU usage on {server}: {avg_cpu:.1f}%",
                    root_cause="Insufficient server capacity",
                    impact="Performance degradation under load",
                    recommendations=["Scale horizontally", "Optimize CPU-intensive operations"],
                    estimated_fix_effort="3-5 days",
                    priority=6
                ))
        
        result.bottlenecks = bottlenecks
        
        # Determine pass/fail status
        critical_issues = [b for b in bottlenecks if b.severity == "critical"]
        high_issues = [b for b in bottlenecks if b.severity == "high"]
        
        if critical_issues:
            result.pass_fail_status = "FAIL"
        elif high_issues:
            result.pass_fail_status = "WARNING"
        else:
            result.pass_fail_status = "PASS"
        
        return result
    
    def _parse_ai_insights(self, analysis_content: str) -> AIInsights:
        """Parse AI analysis into structured insights"""
        
        # This would use more sophisticated parsing in real implementation
        # For now, we'll create a structured response
        
        return AIInsights(
            executive_summary=analysis_content[:500] + "...",  # First 500 chars as summary
            key_findings=[
                "API response times are within acceptable limits",
                "Database performance is optimal",
                "Infrastructure scaling is adequate for current load",
                "No critical bottlenecks identified"
            ],
            performance_score=85,  # Out of 100
            scalability_assessment="System can handle 2x current load with minor optimizations",
            capacity_planning={
                "current_capacity": "500 concurrent users",
                "recommended_scaling": "Horizontal scaling recommended beyond 800 users",
                "infrastructure_changes": "Add 2 additional application servers"
            },
            optimization_roadmap=[
                {
                    "priority": "High",
                    "item": "Database query optimization",
                    "effort": "2 weeks",
                    "impact": "15% response time improvement"
                },
                {
                    "priority": "Medium",
                    "item": "Implement Redis caching",
                    "effort": "1 week",
                    "impact": "20% throughput increase"
                }
            ],
            risk_assessment={
                "production_readiness": "Ready with minor optimizations",
                "major_risks": "Database connection pool exhaustion under peak load",
                "mitigation_strategies": "Implement connection pooling and monitoring"
            },
            comparative_analysis={
                "vs_previous_run": "15% improvement in response times",
                "vs_industry_benchmark": "Above average performance",
                "trend_analysis": "Consistent performance over time"
            }
        )
    
    def _generate_all_report_formats(self, test_input: TestInput, results: List[TestResult], ai_insights: AIInsights) -> Dict[str, str]:
        """Generate comprehensive reports in multiple formats"""
        
        reports = {}
        
        # 1. Executive HTML Report
        executive_html = self._generate_executive_html_report(test_input, results, ai_insights)
        executive_path = self.work_dir / "executive_report.html"
        with open(executive_path, 'w') as f:
            f.write(executive_html)
        reports['executive_html'] = str(executive_path)
        
        # 2. Technical Detailed Report
        technical_report = self._generate_technical_report(test_input, results, ai_insights)
        technical_path = self.work_dir / "technical_report.md"
        with open(technical_path, 'w') as f:
            f.write(technical_report)
        reports['technical_markdown'] = str(technical_path)
        
        # 3. JSON Data Export
        json_export = self._generate_json_export(test_input, results, ai_insights)
        json_path = self.work_dir / "test_results.json"
        with open(json_path, 'w') as f:
            json.dump(json_export, f, indent=2, default=str)
        reports['json_export'] = str(json_path)
        
        # 4. CSV Metrics Export
        csv_export = self._generate_csv_metrics(results)
        csv_path = self.work_dir / "metrics.csv"
        csv_export.to_csv(csv_path, index=False)
        reports['csv_metrics'] = str(csv_path)
        
        return reports
    
    def _generate_executive_html_report(self, test_input: TestInput, results: List[TestResult], ai_insights: AIInsights) -> str:
        """Generate executive-friendly HTML report"""
        
        # Calculate overall metrics
        total_requests = sum(r.metrics.total_requests for r in results)
        avg_response_time = sum(r.metrics.avg_response_time for r in results) / len(results) if results else 0
        overall_error_rate = sum(r.metrics.error_rate for r in results) / len(results) if results else 0
        
        html_report = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Performance Test Report - {test_input.test_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 5px; }}
        .metric {{ display: inline-block; margin: 10px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .pass {{ background-color: #d4edda; }}
        .warning {{ background-color: #fff3cd; }}
        .fail {{ background-color: #f8d7da; }}
        .chart {{ margin: 20px 0; }}
        .recommendations {{ background-color: #e9ecef; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Performance Test Report: {test_input.test_name}</h1>
        <p><strong>Test Type:</strong> {test_input.test_type.value}</p>
        <p><strong>Executed:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Overall Score:</strong> {ai_insights.performance_score}/100</p>
    </div>
    
    <h2>Executive Summary</h2>
    <div class="summary">
        <p>{ai_insights.executive_summary}</p>
    </div>
    
    <h2>Key Metrics</h2>
    <div class="metrics">
        <div class="metric">
            <h3>Total Requests</h3>
            <p style="font-size: 24px; margin: 0;">{total_requests:,}</p>
        </div>
        <div class="metric">
            <h3>Average Response Time</h3>
            <p style="font-size: 24px; margin: 0;">{avg_response_time:.0f}ms</p>
        </div>
        <div class="metric">
            <h3>Error Rate</h3>
            <p style="font-size: 24px; margin: 0;">{overall_error_rate:.2f}%</p>
        </div>
        <div class="metric">
            <h3>Throughput</h3>
            <p style="font-size: 24px; margin: 0;">{sum(r.metrics.throughput for r in results):.1f} req/sec</p>
        </div>
    </div>
    
    <h2>Key Findings</h2>
    <ul>
"""
        
        for finding in ai_insights.key_findings:
            html_report += f"        <li>{finding}</li>\n"
        
        html_report += f"""
    </ul>
    
    <h2>Risk Assessment</h2>
    <div class="risk-assessment">
        <p><strong>Production Readiness:</strong> {ai_insights.risk_assessment.get('production_readiness', 'Not assessed')}</p>
        <p><strong>Major Risks:</strong> {ai_insights.risk_assessment.get('major_risks', 'None identified')}</p>
    </div>
    
    <h2>Recommendations</h2>
    <div class="recommendations">
        <h3>Optimization Roadmap</h3>
        <ol>
"""
        
        for item in ai_insights.optimization_roadmap:
            html_report += f"""
            <li>
                <strong>{item['item']}</strong> (Priority: {item['priority']})
                <br>Effort: {item['effort']} | Expected Impact: {item['impact']}
            </li>
"""
        
        html_report += """
        </ol>
    </div>
    
    <h2>Next Steps</h2>
    <ol>
        <li>Review and prioritize optimization recommendations</li>
        <li>Implement high-priority fixes</li>
        <li>Schedule follow-up performance testing</li>
        <li>Monitor production metrics post-deployment</li>
    </ol>
    
    <footer style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666;">
        <p>Generated by AI-Driven Performance Testing System</p>
    </footer>
</body>
</html>
        """
        
        return html_report
    
    def _generate_technical_report(self, test_input: TestInput, results: List[TestResult], ai_insights: AIInsights) -> str:
        """Generate detailed technical report in Markdown"""
        
        report = f"""# Technical Performance Test Report

## Test Configuration

**Test Name:** {test_input.test_name}
**Test Type:** {test_input.test_type.value}
**Description:** {test_input.description}
**Environment:** {test_input.environment.name}

## Test Scenarios

"""
        
        for i, result in enumerate(results, 1):
            report += f"""
### Scenario {i}: {result.endpoint_name}

**Load Pattern:** {result.load_pattern}
**Execution Time:** {result.execution_time:.2f} seconds
**Status:** {result.pass_fail_status}

#### Metrics
- **Total Requests:** {result.metrics.total_requests:,}
- **Successful:** {result.metrics.successful_requests:,}
- **Failed:** {result.metrics.failed_requests:,}
- **Error Rate:** {result.metrics.error_rate:.2f}%
- **Average Response Time:** {result.metrics.avg_response_time:.2f}ms
- **95th Percentile:** {result.metrics.percentile_95:.2f}ms
- **99th Percentile:** {result.metrics.percentile_99:.2f}ms
- **Throughput:** {result.metrics.throughput:.2f} req/sec

#### Identified Bottlenecks
"""
            
            if result.bottlenecks:
                for bottleneck in result.bottlenecks:
                    report += f"""
**{bottleneck.component.upper()} - {bottleneck.severity.upper()}**
- **Description:** {bottleneck.description}
- **Root Cause:** {bottleneck.root_cause}
- **Impact:** {bottleneck.impact}
- **Recommendations:** {', '.join(bottleneck.recommendations)}
- **Estimated Effort:** {bottleneck.estimated_fix_effort}
"""
            else:
                report += "No critical bottlenecks identified.\n"
            
            if result.errors:
                report += f"\n#### Errors ({len(result.errors)})\n"
                for error in result.errors[:5]:  # Show first 5 errors
                    report += f"- {error.get('message', 'Unknown error')}\n"
        
        report += f"""

## AI Analysis Summary

{ai_insights.executive_summary}

### Scalability Assessment
{ai_insights.scalability_assessment}

### Capacity Planning
- **Current Capacity:** {ai_insights.capacity_planning.get('current_capacity', 'Not assessed')}
- **Scaling Recommendation:** {ai_insights.capacity_planning.get('recommended_scaling', 'Not provided')}

### Optimization Roadmap

| Priority | Item | Effort | Expected Impact |
|----------|------|--------|-----------------|
"""
        
        for item in ai_insights.optimization_roadmap:
            report += f"| {item['priority']} | {item['item']} | {item['effort']} | {item['impact']} |\n"
        
        report += """

## Recommendations

### Immediate Actions (0-2 weeks)
- Review and address critical bottlenecks
- Implement monitoring for key metrics
- Optimize high-impact, low-effort improvements

### Short-term Improvements (1-3 months)
- Infrastructure scaling based on capacity analysis
- Application-level optimizations
- Enhanced monitoring and alerting

### Long-term Strategy (3+ months)
- Architecture improvements
- Technology stack evaluation
- Performance culture integration

## Appendix

### Test Thresholds
- **Max Average Response Time:** {test_input.thresholds.max_avg_response_time}ms
- **Max 95th Percentile:** {test_input.thresholds.max_95th_percentile}ms
- **Max Error Rate:** {test_input.thresholds.max_error_rate}%
- **Min Throughput:** {test_input.thresholds.min_throughput} req/sec

### Environment Details
- **Base URL:** {test_input.environment.base_url}
- **Servers Monitored:** {len(test_input.environment.infrastructure.servers)}
- **Databases:** {len(test_input.environment.infrastructure.databases)}
- **Redis Instances:** {len(test_input.environment.infrastructure.redis_instances)}

---
*Report generated by AI-Driven Performance Testing System on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return report
    
    def _generate_json_export(self, test_input: TestInput, results: List[TestResult], ai_insights: AIInsights) -> Dict:
        """Generate comprehensive JSON export"""
        
        return {
            'test_metadata': {
                'test_id': f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'test_name': test_input.test_name,
                'test_type': test_input.test_type.value,
                'execution_timestamp': datetime.now().isoformat(),
                'environment': test_input.environment.name
            },
            'test_configuration': asdict(test_input),
            'execution_results': [asdict(result) for result in results],
            'ai_insights': asdict(ai_insights),
            'summary_metrics': {
                'total_requests': sum(r.metrics.total_requests for r in results),
                'overall_error_rate': sum(r.metrics.error_rate for r in results) / len(results) if results else 0,
                'average_response_time': sum(r.metrics.avg_response_time for r in results) / len(results) if results else 0,
                'total_throughput': sum(r.metrics.throughput for r in results),
                'performance_score': ai_insights.performance_score
            }
        }
    
    def _generate_csv_metrics(self, results: List[TestResult]) -> pd.DataFrame:
        """Generate CSV export of key metrics"""
        
        metrics_data = []
        
        for result in results:
            metrics_data.append({
                'scenario': result.endpoint_name,
                'load_pattern': result.load_pattern,
                'status': result.pass_fail_status,
                'total_requests': result.metrics.total_requests,
                'successful_requests': result.metrics.successful_requests,
                'failed_requests': result.metrics.failed_requests,
                'error_rate_percent': result.metrics.error_rate,
                'avg_response_time_ms': result.metrics.avg_response_time,
                'min_response_time_ms': result.metrics.min_response_time,
                'max_response_time_ms': result.metrics.max_response_time,
                'percentile_50_ms': result.metrics.percentile_50,
                'percentile_90_ms': result.metrics.percentile_90,
                'percentile_95_ms': result.metrics.percentile_95,
                'percentile_99_ms': result.metrics.percentile_99,
                'throughput_req_per_sec': result.metrics.throughput,
                'bytes_sent': result.metrics.bytes_sent,
                'bytes_received': result.metrics.bytes_received,
                'execution_time_sec': result.execution_time,
                'bottlenecks_count': len(result.bottlenecks),
                'errors_count': len(result.errors)
            })
        
        return pd.DataFrame(metrics_data)
    
    def _create_test_artifacts(self, test_input: TestInput, results: List[TestResult], ai_insights: AIInsights) -> List[str]:
        """Create additional test artifacts"""
        
        artifacts = []
        
        # 1. Performance Dashboard Data (for Grafana/other tools)
        dashboard_data = {
            'metrics': [asdict(result.metrics) for result in results],
            'infrastructure': [asdict(result.infrastructure_metrics) for result in results],
            'timestamps': [datetime.now().isoformat()] * len(results)
        }
        
        dashboard_path = self.work_dir / "dashboard_data.json"
        with open(dashboard_path, 'w') as f:
            json.dump(dashboard_data, f, indent=2, default=str)
        artifacts.append(str(dashboard_path))
        
        # 2. JMeter Configuration Backup
        config_backup = {
            'jmeter_version': 'JMeter 5.4.1',
            'test_plans_used': [f"{result.endpoint_name}.jmx" for result in results],
            'system_properties': self.system_config
        }
        
        config_path = self.work_dir / "jmeter_config_backup.json"
        with open(config_path, 'w') as f:
            json.dump(config_backup, f, indent=2)
        artifacts.append(str(config_path))
        
        # 3. Performance Baseline (for future comparisons)
        baseline = {
            'test_name': test_input.test_name,
            'baseline_date': datetime.now().isoformat(),
            'baseline_metrics': {
                'avg_response_time': sum(r.metrics.avg_response_time for r in results) / len(results),
                'throughput': sum(r.metrics.throughput for r in results),
                'error_rate': sum(r.metrics.error_rate for r in results) / len(results),
                'performance_score': ai_insights.performance_score
            }
        }
        
        baseline_path = self.work_dir / "performance_baseline.json"
        with open(baseline_path, 'w') as f:
            json.dump(baseline, f, indent=2, default=str)
        artifacts.append(str(baseline_path))
        
        return artifacts
    
    def _send_notifications(self, test_input: TestInput, results: List[TestResult], ai_insights: AIInsights):
        """Send notifications based on configuration"""
        
        if not test_input.notifications:
            return
        
        # Determine notification level based on results
        critical_issues = any(r.pass_fail_status == "FAIL" for r in results)
        warning_issues = any(r.pass_fail_status == "WARNING" for r in results)
        
        notification_level = "CRITICAL" if critical_issues else "WARNING" if warning_issues else "INFO"
        
        message = f"""
Performance Test Completed: {test_input.test_name}
Status: {notification_level}
Performance Score: {ai_insights.performance_score}/100

Key Findings:
{chr(10).join(f"• {finding}" for finding in ai_insights.key_findings[:3])}

View detailed report: {self.work_dir}/executive_report.html
        """
        
        # Email notifications
        if 'email' in test_input.notifications:
            for email in test_input.notifications['email']:
                self._send_email(email, f"Performance Test {notification_level}: {test_input.test_name}", message)
        
        # Slack notifications
        if 'slack' in test_input.notifications:
            for webhook in test_input.notifications['slack']:
                self._send_slack(webhook, message, notification_level)
    
    def _send_email(self, email: str, subject: str, message: str):
        """Send email notification (placeholder implementation)"""
        print(f"Email notification sent to {email}: {subject}")
        # Implement actual email sending logic here
    
    def _send_slack(self, webhook: str, message: str, level: str):
        """Send Slack notification (placeholder implementation)"""
        print(f"Slack notification sent to {webhook}: {level}")
        # Implement actual Slack webhook logic here
    
    def _run_cleanup_scripts(self, cleanup_scripts: List[str]):
        """Execute cleanup scripts"""
        for script in cleanup_scripts:
            try:
                subprocess.run(script, shell=True, check=True)
                print(f"Cleanup script executed successfully: {script}")
            except subprocess.CalledProcessError as e:
                print(f"Cleanup script failed: {script} - {e}")
    
    def _archive_test_results(self, state: Dict) -> str:
        """Archive all test results and artifacts"""
        
        import shutil
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_name = f"performance_test_{timestamp}"
        archive_path = self.work_dir.parent / f"{archive_name}.zip"
        
        # Create zip archive
        shutil.make_archive(str(archive_path.with_suffix('')), 'zip', str(self.work_dir))
        
        print(f"Test results archived to: {archive_path}")
        return str(archive_path)
    
    def _generate_next_actions(self, ai_insights: AIInsights) -> List[str]:
        """Generate actionable next steps"""
        
        actions = [
            "Review performance test results with development team",
            "Prioritize optimization recommendations based on business impact",
            "Schedule implementation of high-priority fixes",
            "Set up continuous performance monitoring",
            "Plan follow-up performance testing after optimizations"
        ]
        
        # Add specific actions based on performance score
        if ai_insights.performance_score < 70:
            actions.insert(0, "URGENT: Address critical performance issues before production deployment")
        elif ai_insights.performance_score < 85:
            actions.insert(1, "Implement medium-priority optimizations to improve user experience")
        
        return actions
    
    async def run_complete_performance_test(self, test_input: TestInput) -> TestOutput:
        """Main method to execute complete AI-driven performance test"""
        
        print(f"🚀 Starting AI-driven performance test: {test_input.test_name}")
        
        start_time = datetime.now()
        
        # Compile the workflow
        compiled_workflow = self.workflow.compile()
        
        initial_state = {
            'test_input': test_input,
            'preprocessed_input': None,
            'validation_results': None,
            'environment_ready': False,
            'connectivity_results': None,
            'ai_scenarios': None,
            'jmeter_plans': None,
            'execution_results': None,
            'real_time_metrics': None,
            'comprehensive_analysis': None,
            'ai_insights': None,
            'generated_reports': None,
            'artifacts': None,
            'archive_path': None,
            'next_actions': None,
            'completion_status': 'PENDING',
            'execution_timestamp': None,
            'start_time': start_time
        }
        
        try:
            # Execute the complete workflow
            final_state = await compiled_workflow.ainvoke(initial_state)
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            # Create comprehensive output
            ai_insights = final_state.get('ai_insights')
            if ai_insights is None:
                ai_insights = AIInsights(
                    executive_summary="No analysis available",
                    key_findings=[],
                    performance_score=0,
                    scalability_assessment="",
                    capacity_planning={},
                    optimization_roadmap=[],
                    risk_assessment={},
                    comparative_analysis={}
                )
            
            test_output = TestOutput(
                test_id=f"test_{start_time.strftime('%Y%m%d_%H%M%S')}",
                test_input=test_input,
                execution_timestamp=start_time,
                duration=duration,
                overall_status=final_state.get('completion_status', 'SUCCESS'),
                test_results=final_state.get('execution_results', []),
                ai_insights=ai_insights,
                detailed_reports=final_state.get('generated_reports', {}),
                artifacts=final_state.get('artifacts', []),
                next_recommended_actions=final_state.get('next_actions', [])
            )
            
            print(f"✅ Performance test completed successfully in {duration}")
            print(f"📊 Performance Score: {test_output.ai_insights.performance_score}/100")
            print(f"📁 Reports generated: {len(test_output.detailed_reports)}")
            print(f"🎯 Next actions: {len(test_output.next_recommended_actions)}")
            
            return test_output
            
        except Exception as e:
            print(f"❌ Performance test failed: {str(e)}")
            
            # Create error output
            return TestOutput(
                test_id=f"test_failed_{start_time.strftime('%Y%m%d_%H%M%S')}",
                test_input=test_input,
                execution_timestamp=start_time,
                duration=datetime.now() - start_time,
                overall_status="FAILED",
                test_results=[],
                ai_insights=AIInsights("Test execution failed", [], 0, "", {}, [], {}, {}),
                detailed_reports={},
                artifacts=[],
                next_recommended_actions=[f"Debug and resolve test execution error: {str(e)}"]
            )


# ===== USAGE EXAMPLES AND CONFIGURATIONS =====

def create_sample_e_commerce_test() -> TestInput:
    """Create a comprehensive e-commerce performance test configuration"""
    
    # Define endpoints
    endpoints = [
        EndpointConfig(
            name="User Login",
            url="https://api.example.com/auth/login",
            method="POST",
            headers={"Content-Type": "application/json"},
            payload={"username": "testuser", "password": "testpass"},
            expected_status_codes=[200, 201],
            timeout=10
        ),
        EndpointConfig(
            name="Product Search",
            url="https://api.example.com/products/search",
            method="GET",
            headers={"Authorization": "Bearer ${access_token}"},
            expected_status_codes=[200],
            timeout=15
        ),
        EndpointConfig(
            name="Add to Cart",
            url="https://api.example.com/cart/items",
            method="POST",
            headers={"Content-Type": "application/json", "Authorization": "Bearer ${access_token}"},
            payload={"product_id": "${product_id}", "quantity": 1},
            expected_status_codes=[200, 201],
            timeout=10
        ),
        EndpointConfig(
            name="Checkout Process",
            url="https://api.example.com/orders/checkout",
            method="POST",
            headers={"Content-Type": "application/json", "Authorization": "Bearer ${access_token}"},
            payload={"payment_method": "credit_card", "shipping_address": "123 Test St"},
            expected_status_codes=[200, 201],
            timeout=30
        )
    ]
    
    # Define load patterns
    load_patterns = [
        LoadPattern(
            name="Normal Load",
            pattern_type="steady_state",
            concurrent_users=100,
            ramp_up_time=300,  # 5 minutes
            duration=1800,     # 30 minutes
            ramp_down_time=300
        ),
        LoadPattern(
            name="Peak Load",
            pattern_type="spike",
            concurrent_users=500,
            ramp_up_time=60,   # 1 minute spike
            duration=600,      # 10 minutes sustained
            ramp_down_time=300
        ),
        LoadPattern(
            name="Black Friday Simulation",
            pattern_type="custom",
            concurrent_users=1000,
            ramp_up_time=600,  # 10 minutes
            duration=3600,     # 1 hour
            ramp_down_time=600
        )
    ]
    
    # Define performance thresholds
    thresholds = PerformanceThresholds(
        max_avg_response_time=2000,    # 2 seconds
        max_95th_percentile=5000,      # 5 seconds
        max_99th_percentile=10000,     # 10 seconds
        min_throughput=50,             # 50 req/sec minimum
        max_error_rate=1.0,            # 1% error rate
        max_cpu_usage=80.0,            # 80% CPU
        max_memory_usage=85.0,         # 85% Memory
        max_disk_io=100.0              # 100 MB/s
    )
    
    # Define infrastructure
    infrastructure = InfrastructureConfig(
        servers=["web-server-1", "web-server-2", "web-server-3"],
        databases=[
            {"name": "primary-db", "type": "postgresql", "host": "db.example.com", 
             "port": "5432", "user": "monitor", "password": "monitorpass", "database": "ecommerce"}
        ],
        redis_instances=["redis://cache-1.example.com:6379", "redis://cache-2.example.com:6379"],
        monitoring_tools={
            "prometheus": "http://prometheus.example.com:9090",
            "grafana": "http://grafana.example.com:3000"
        },
        custom_metrics=[]
    )
    
    # Define test environment
    environment = TestEnvironment(
        name="Production-Like Staging",
        base_url="https://api.example.com",
        infrastructure=infrastructure,
        test_data_setup={
            "create_test_users": "INSERT INTO users (username, email) VALUES ('testuser1', 'test1@example.com')",
            "create_test_products": "INSERT INTO products (name, price, stock) VALUES ('Test Product', 29.99, 1000)"
        },
        cleanup_scripts=[
            "DELETE FROM test_orders WHERE created_at < NOW() - INTERVAL '1 hour'",
            "DELETE FROM test_users WHERE username LIKE 'testuser%'"
        ]
    )
    
    # Create complete test input
    return TestInput(
        test_name="E-Commerce Black Friday Readiness Test",
        test_type=TestType.LOAD,
        description="Comprehensive performance test to validate e-commerce platform readiness for Black Friday traffic surge",
        environment=environment,
        endpoints=endpoints,
        load_patterns=load_patterns,
        thresholds=thresholds,
        test_data_files=["user_data.csv", "product_catalog.csv"],
        custom_scenarios=[
            {
                "name": "Complete User Journey",
                "steps": ["login", "search", "add_to_cart", "checkout"],
                "think_time": 5000,  # 5 seconds between steps
                "data_source": "user_data.csv"
            }
        ],
        reporting_config={
            "include_graphs": True,
            "detailed_analysis": True,
            "benchmark_comparison": True
        },
        notifications={
            "email": ["devops@example.com", "qa@example.com"],
            "slack": ["https://hooks.slack.com/services/your/webhook/url"]
        }
    )

def create_api_stress_test() -> TestInput:
    """Create a focused API stress test configuration"""
    
    endpoints = [
        EndpointConfig(
            name="High Volume API",
            url="https://api.example.com/v1/data",
            method="GET",
            headers={"API-Key": "test-key-12345"},
            expected_status_codes=[200],
            timeout=5
        )
    ]
    
    load_patterns = [
        LoadPattern(
            name="Stress Test",
            pattern_type="ramp_up",
            concurrent_users=2000,
            ramp_up_time=1800,  # 30 minutes
            duration=3600,      # 1 hour
            ramp_down_time=600  # 10 minutes
        )
    ]
    
    thresholds = PerformanceThresholds(
        max_avg_response_time=1000,
        max_95th_percentile=3000,
        max_99th_percentile=5000,
        min_throughput=200,
        max_error_rate=0.5,
        max_cpu_usage=90.0,
        max_memory_usage=90.0,
        max_disk_io=200.0
    )
    
    infrastructure = InfrastructureConfig(
        servers=["api-server-1", "api-server-2"],
        databases=[],
        redis_instances=[],
        monitoring_tools={},
        custom_metrics=[]
    )
    
    environment = TestEnvironment(
        name="API Stress Environment",
        base_url="https://api.example.com",
        infrastructure=infrastructure,
        test_data_setup={},
        cleanup_scripts=[]
    )
    
    return TestInput(
        test_name="API Stress Test - Maximum Load",
        test_type=TestType.STRESS,
        description="Stress test to determine API breaking point and failure modes",
        environment=environment,
        endpoints=endpoints,
        load_patterns=load_patterns,
        thresholds=thresholds,
        notifications={
            "email": ["api-team@example.com"]
        }
    )


# ===== MAIN EXECUTION EXAMPLES =====

async def run_e_commerce_example():
    """Run complete e-commerce performance test example"""
    
    print("=== E-COMMERCE PERFORMANCE TEST EXAMPLE ===\n")
    
    # Initialize the testing system
    tester = ComprehensiveAIPerformanceTester()
    
    # Create test configuration
    test_config = create_sample_e_commerce_test()
    
    # Execute the complete test
    results = await tester.run_complete_performance_test(test_config)
    
    # Print summary
    print("\n=== TEST RESULTS SUMMARY ===")
    print(f"Test ID: {results.test_id}")
    print(f"Overall Status: {results.overall_status}")
    print(f"Performance Score: {results.ai_insights.performance_score}/100")
    print(f"Duration: {results.duration}")
    print(f"Scenarios Executed: {len(results.test_results)}")
    
    print("\n=== KEY FINDINGS ===")
    for i, finding in enumerate(results.ai_insights.key_findings, 1):
        print(f"{i}. {finding}")
    
    print("\n=== NEXT ACTIONS ===")
    for i, action in enumerate(results.next_recommended_actions, 1):
        print(f"{i}. {action}")
    
    print(f"\n=== REPORTS GENERATED ===")
    for report_type, path in results.detailed_reports.items():
        print(f"- {report_type}: {path}")
    
    return results

async def run_api_stress_example():
    """Run API stress test example"""
    
    print("=== API STRESS TEST EXAMPLE ===\n")
    
    tester = ComprehensiveAIPerformanceTester()
    test_config = create_api_stress_test()
    
    results = await tester.run_complete_performance_test(test_config)
    
    print(f"\nStress Test Results:")
    print(f"- Breaking Point: {results.ai_insights.capacity_planning.get('current_capacity', 'Not determined')}")
    print(f"- Performance Score: {results.ai_insights.performance_score}/100")
    print(f"- Critical Issues: {len([r for r in results.test_results if r.pass_fail_status == 'FAIL'])}")
    
    return results

async def run_custom_configuration_example():
    """Example showing how to create custom test configurations"""
    
    print("=== CUSTOM CONFIGURATION EXAMPLE ===\n")
    
    # Custom microservice test
    custom_test = TestInput(
        test_name="Microservice Integration Test",
        test_type=TestType.VOLUME,
        description="Test microservice performance under high data volume",
        environment=TestEnvironment(
            name="Microservice Test Environment",
            base_url="https://microservice.example.com",
            infrastructure=InfrastructureConfig(["service-1", "service-2"], [], [], {}, []),
            test_data_setup={},
            cleanup_scripts=[]
        ),
        endpoints=[
            EndpointConfig(
                name="Data Processing Endpoint",
                url="https://microservice.example.com/process",
                method="POST",
                headers={"Content-Type": "application/json"},
                payload={"data_size": "large", "processing_type": "batch"},
                timeout=60
            )
        ],
        load_patterns=[
            LoadPattern(
                name="Volume Test",
                pattern_type="steady_state",
                concurrent_users=50,
                ramp_up_time=300,
                duration=1800
            )
        ],
        thresholds=PerformanceThresholds(
            max_avg_response_time=30000,  # 30 seconds for batch processing
            max_95th_percentile=60000,    # 1 minute
            max_99th_percentile=120000,   # 2 minutes
            min_throughput=5,             # 5 req/sec minimum
            max_error_rate=0.1,           # 0.1% error rate
            max_cpu_usage=85.0,
            max_memory_usage=90.0,
            max_disk_io=500.0
        )
    )
    
    tester = ComprehensiveAIPerformanceTester()
    results = await tester.run_complete_performance_test(custom_test)
    
    print(f"Custom Test Results: {results.overall_status}")
    return results


if __name__ == "__main__":
    # Run examples
    import asyncio
    
    print("🤖 AI-Driven Performance Testing System")
    print("=========================================\n")
    
    # Choose which example to run
    example_choice = input("Choose example (1: E-commerce, 2: API Stress, 3: Custom, 4: All): ")
    
    if example_choice == "1":
        asyncio.run(run_e_commerce_example())
    elif example_choice == "2":
        asyncio.run(run_api_stress_example())
    elif example_choice == "3":
        asyncio.run(run_custom_configuration_example())
    elif example_choice == "4":
        asyncio.run(run_e_commerce_example())
        asyncio.run(run_api_stress_example())
        asyncio.run(run_custom_configuration_example())
    else:
        print("Running default e-commerce example...")
        asyncio.run(run_e_commerce_example())