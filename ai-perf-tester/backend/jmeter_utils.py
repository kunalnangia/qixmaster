"""
JMeter Utilities for Performance Testing
"""
import os
import subprocess
import csv
import logging
import uuid
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any, Tuple
from sqlalchemy.orm import Session

# Import PerfTestRequest from models instead of main to avoid circular imports
from models import PerfTestRequest
# Import database models from database instead of main
from database import PerfRunDetail, PerfTestRun, AIRecommendation
from ai_workflow import analyze_performance_test

# Configure logging
logger = logging.getLogger(__name__)

def generate_jmeter_template(test_request: PerfTestRequest) -> str:
    """Generate a JMeter test plan based on the test request"""
    # Create a unique template name
    template_name = f"jmx_templates/{test_request.test_name.replace(' ', '_')}_{uuid.uuid4()}.jmx"
    
    # Parse URL components
    protocol = "https"
    domain = test_request.url
    path = "/"
    
    if "://" in test_request.url:
        url_parts = test_request.url.split("://")
        protocol = url_parts[0]
        remaining = url_parts[1]
        
        if "/" in remaining:
            domain_parts = remaining.split("/", 1)
            domain = domain_parts[0]
            path = "/" + domain_parts[1]
        else:
            domain = remaining
    
    # Basic JMeter test plan with Thread Group and HTTP Request
    jmeter_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.2">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="{test_request.test_name}" enabled="true">
      <stringProp name="TestPlan.comments"></stringProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.tearDown_on_shutdown">true</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
      <elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
        <collectionProp name="Arguments.arguments"/>
      </elementProp>
      <stringProp name="TestPlan.user_define_classpath"></stringProp>
    </TestPlan>
    <hashTree>
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Thread Group" enabled="true">
        <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="Loop Controller" enabled="true">
          <boolProp name="LoopController.continue_forever">false</boolProp>
          <intProp name="LoopController.loops">-1</intProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">{test_request.concurrent_users}</stringProp>
        <stringProp name="ThreadGroup.ramp_time">{test_request.ramp_up_time}</stringProp>
        <boolProp name="ThreadGroup.scheduler">true</boolProp>
        <stringProp name="ThreadGroup.duration">{test_request.duration}</stringProp>
        <stringProp name="ThreadGroup.delay">0</stringProp>
        <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
      </ThreadGroup>
      <hashTree>
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="HTTP Request" enabled="true">
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
            <collectionProp name="Arguments.arguments"/>
          </elementProp>
          <stringProp name="HTTPSampler.domain">{domain}</stringProp>
          <stringProp name="HTTPSampler.port"></stringProp>
          <stringProp name="HTTPSampler.protocol">{protocol}</stringProp>
          <stringProp name="HTTPSampler.contentEncoding"></stringProp>
          <stringProp name="HTTPSampler.path">{path}</stringProp>
          <stringProp name="HTTPSampler.method">GET</stringProp>
          <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
          <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
          <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
          <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          <stringProp name="HTTPSampler.embedded_url_re"></stringProp>
          <stringProp name="HTTPSampler.connect_timeout"></stringProp>
          <stringProp name="HTTPSampler.response_timeout"></stringProp>
        </HTTPSamplerProxy>
        <hashTree/>
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
          <stringProp name="filename"></stringProp>
        </ResultCollector>
        <hashTree/>
        <ResultCollector guiclass="SummaryReport" testclass="ResultCollector" testname="Summary Report" enabled="true">
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
          <stringProp name="filename"></stringProp>
        </ResultCollector>
        <hashTree/>
      </hashTree>
    </hashTree>
  </hashTree>
</jmeterTestPlan>"""
    
    # Save the template to a file
    with open(template_name, "w") as f:
        f.write(jmeter_template)
    
    return template_name

def run_jmeter_test(jmx_file: str, run_id: str) -> Tuple[str, str]:
    """Run JMeter test and return results file and report path"""
    logger.info(f"Running JMeter test with file {jmx_file} for run ID {run_id}")
    
    results_dir = f"results/{run_id}"
    os.makedirs(results_dir, exist_ok=True)
    results_file = os.path.join(results_dir, "results.csv")
    report_dir = os.path.join(results_dir, "report")
    
    # Get JMeter path - check multiple possible locations
    jmeter_cmd = None
    
    # Option 1: Check JMETER_HOME environment variable
    jmeter_home = os.environ.get('JMETER_HOME')
    if jmeter_home and os.path.exists(jmeter_home):
        if os.name == 'nt':  # Windows
            jmeter_exec = os.path.join(jmeter_home, "bin", "jmeter.bat")
        else:  # Unix/Linux/Mac
            jmeter_exec = os.path.join(jmeter_home, "bin", "jmeter")
        
        if os.path.exists(jmeter_exec):
            jmeter_cmd = jmeter_exec
            logger.info(f"Using JMeter from JMETER_HOME: {jmeter_cmd}")
    
    # Option 2: Check if jmeter is in PATH
    if not jmeter_cmd:
        jmeter_cmd = "jmeter"  # Try default command
    
    # Run JMeter test
    try:
        cmd = [
            jmeter_cmd,
            "-n",  # Non-GUI mode
            "-t", jmx_file,  # Test plan file
            "-l", results_file,  # Results file
            "-j", os.path.join(results_dir, "jmeter.log"),  # JMeter log file
            "-e",  # Generate report dashboard
            "-o", report_dir  # Output directory for report
        ]
        
        logger.info(f"Executing JMeter command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            logger.error(f"JMeter failed with return code {result.returncode}")
            logger.error(f"Stdout: {result.stdout}")
            logger.error(f"Stderr: {result.stderr}")
            raise Exception(f"JMeter failed: {result.stderr}")
        
        logger.info("JMeter test completed successfully")
        return results_file, report_dir
        
    except subprocess.TimeoutExpired:
        logger.error("JMeter test timed out")
        raise Exception("JMeter test timed out after 5 minutes")
    except Exception as e:
        logger.error(f"Error running JMeter: {str(e)}")
        raise Exception(f"Error running JMeter: {str(e)}")

def parse_jmeter_csv(file_path: str) -> Dict[str, Any]:
    """Parse JMeter CSV results into time series data"""
    logger.info(f"Parsing JMeter CSV file: {file_path}")
    
    bucket = defaultdict(list)
    
    try:
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    ts = datetime.fromtimestamp(int(row["timeStamp"]) / 1000)
                    elapsed = float(row["elapsed"])
                    success = row["success"].lower() == "true"
                    minute_bucket = ts.replace(second=0, microsecond=0)
                    bucket[minute_bucket].append((elapsed, success))
                except (KeyError, ValueError) as e:
                    logger.warning(f"Error parsing row in CSV: {e}")
                    continue
    except FileNotFoundError:
        logger.error(f"Results file not found: {file_path}")
        return {
            "timestamps": [],
            "response_times": [],
            "error_rate_series": [],
            "throughput_series": []
        }
    
    data = {"timestamps": [], "response_times": [], "error_rate_series": [], "throughput_series": []}
    
    for ts, samples in sorted(bucket.items()):
        total = len(samples)
        if total > 0:
            errors = sum(1 for _, s in samples if not s)
            avg_resp = sum(e for e, _ in samples) / total
            
            data["timestamps"].append(ts.isoformat())
            data["response_times"].append(round(avg_resp, 2))
            data["error_rate_series"].append(round(errors / total * 100, 2))
            data["throughput_series"].append(total)
    
    return data

def save_run_details_to_db(db: Session, run_id: str, parsed_data: Dict[str, Any]) -> None:
    """Save time series data to database"""
    logger.info(f"Saving run details to database for run ID {run_id}")
    
    rows = []
    for ts, resp, err, thr in zip(
        parsed_data["timestamps"],
        parsed_data["response_times"],
        parsed_data["error_rate_series"],
        parsed_data["throughput_series"]
    ):
        try:
            timestamp = datetime.fromisoformat(ts)
            rows.append(
                PerfRunDetail(
                    run_id=run_id,
                    timestamp=timestamp,
                    avg_response_time=resp,
                    error_rate=err,
                    throughput=thr
                )
            )
        except ValueError as e:
            logger.warning(f"Error parsing timestamp {ts}: {e}")
    
    if rows:
        db.add_all(rows)
        db.commit()
        logger.info(f"Saved {len(rows)} detail records for run ID {run_id}")
    else:
        logger.warning(f"No details to save for run ID {run_id}")

async def save_ai_analysis_to_db(db: Session, run_id: str, analysis_result: Dict[str, Any]) -> None:
    """Save AI analysis results to database"""
    logger.info(f"Saving AI analysis to database for run ID {run_id}")
    
    # Get the test run
    test_run = db.query(PerfTestRun).filter(PerfTestRun.id == run_id).first()
    if not test_run:
        logger.error(f"Test run {run_id} not found")
        return
    
    # Save the full analysis report
    test_run.ai_analysis = analysis_result.get("report", "")
    
    # Save individual recommendations
    recommendations = []
    
    # Add bottlenecks
    for bottleneck in analysis_result.get("bottlenecks", []):
        recommendations.append(
            AIRecommendation(
                run_id=run_id,
                category="bottleneck",
                description=bottleneck
            )
        )
    
    # Add recommendations
    for recommendation in analysis_result.get("recommendations", []):
        recommendations.append(
            AIRecommendation(
                run_id=run_id,
                category="recommendation",
                description=recommendation
            )
        )
    
    # Add next tests
    for next_test in analysis_result.get("next_steps", []):
        recommendations.append(
            AIRecommendation(
                run_id=run_id,
                category="next_test",
                description=next_test
            )
        )
    
    # Add all recommendations
    if recommendations:
        db.add_all(recommendations)
    
    # Commit changes
    db.commit()
    logger.info(f"Saved AI analysis for run ID {run_id}")

def _is_quota_error(error: Exception) -> bool:
    """Check if the error is a quota-related error."""
    error_str = str(error).lower()
    return (
        "quota" in error_str or 
        "429" in error_str or 
        "insufficient_quota" in error_str or
        "rate limit" in error_str
    )

async def run_ai_analysis(
    run_id: str,
    parsed_data: Dict[str, Any],
    summary_metrics: Dict[str, Any],
    test_request: PerfTestRequest,
    db_func
) -> None:
    """Run AI analysis on test results with fallback support for quota errors"""
    logger.info(f"Running AI analysis for test run {run_id}")
    
    db = None
    try:
        # Get previous runs for comparison
        db = next(db_func())
        previous_runs = db.query(PerfTestRun).filter(
            PerfTestRun.test_type == test_request.test_type,
            PerfTestRun.id != run_id
        ).order_by(PerfTestRun.created_at.desc()).limit(5).all()
        
        previous_runs_data = [
            {
                "id": run.id,
                "test_name": run.test_name,
                "summary_metrics": run.summary_metrics or {},
                "created_at": run.created_at.isoformat() if run.created_at else ""
            }
            for run in previous_runs
        ]
        
        # Prepare performance data for AI analysis with correct types
        perf_data: PerformanceData = {
            "test_name": test_request.test_name,
            "test_type": test_request.test_type,
            "url": test_request.url,
            "concurrent_users": int(test_request.concurrent_users),
            "duration": int(test_request.duration),
            "ramp_up_time": int(test_request.ramp_up_time),
            "summary_metrics": summary_metrics,
            "time_series_data": parsed_data,
            "previous_runs": previous_runs_data
        }
        
        # Run AI analysis with fallback support
        analysis_result = None
        last_error = None
        
        try:
            # Try primary AI analysis
            analysis_result = await analyze_performance_test(perf_data)
        except Exception as e:
            last_error = e
            logger.warning(f"Primary AI analysis failed: {str(e)}")
            
            # Check if it's a quota error and try fallback
            if _is_quota_error(e):
                logger.info("Attempting fallback AI analysis due to quota error")
                try:
                    # Try alternative analysis approach or reduced functionality
                    analysis_result = {
                        "analysis": f"AI analysis completed with reduced functionality due to quota limitations: {str(e)}",
                        "bottlenecks": ["Unable to identify specific bottlenecks due to quota limitations"],
                        "recommendations": ["Check quota limits for your AI provider", "Consider using alternative AI models"],
                        "next_steps": ["Upgrade your AI provider plan or use alternative models"],
                        "report": f"# Performance Test Analysis Report\n\nAI analysis completed with reduced functionality due to quota limitations: {str(e)}"
                    }
                except Exception as fallback_error:
                    logger.error(f"Fallback AI analysis also failed: {str(fallback_error)}")
                    last_error = fallback_error
            else:
                # Re-raise non-quota errors
                raise
        
        # If we still don't have a result, create a basic one
        if analysis_result is None and last_error is not None:
            analysis_result = {
                "analysis": f"AI analysis failed: {str(last_error)}",
                "bottlenecks": [],
                "recommendations": [],
                "next_steps": [],
                "report": f"# Performance Test Analysis Report\n\nAI analysis failed: {str(last_error)}"
            }
        elif analysis_result is None:
            analysis_result = {
                "analysis": "AI analysis failed: Unknown error",
                "bottlenecks": [],
                "recommendations": [],
                "next_steps": [],
                "report": "# Performance Test Analysis Report\n\nAI analysis failed: Unknown error"
            }
        
        # Save analysis results
        if analysis_result is not None:
            await save_ai_analysis_to_db(db, run_id, analysis_result)
        
        logger.info(f"AI analysis completed for test run {run_id}")
    except Exception as e:
        logger.error(f"Error running AI analysis: {str(e)}")
        # Save error information to database as well
        try:
            if db is not None:
                test_run = db.query(PerfTestRun).filter(PerfTestRun.id == run_id).first()
                if test_run:
                    test_run.ai_analysis = f"AI analysis failed: {str(e)}"
                    db.commit()
        except Exception as db_error:
            logger.error(f"Error saving AI analysis error to database: {str(db_error)}")
    finally:
        if db is not None:
            db.close()

# Add typing for PerformanceData to match ai_workflow
from typing import TypedDict

class PerformanceData(TypedDict):
    test_name: str
    test_type: str
    url: str
    concurrent_users: int
    duration: int
    ramp_up_time: int
    summary_metrics: Dict[str, Any]
    time_series_data: Dict[str, List[Any]]
    previous_runs: List[Dict[str, Any]]