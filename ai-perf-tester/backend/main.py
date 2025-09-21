# FastAPI backend with JMeter integration and LangGraph AI analysis
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import subprocess, os, uuid, csv, json, shutil
from datetime import datetime
from collections import defaultdict
import aiofiles
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Import LangGraph workflow with error handling
try:
    from ai_workflow import analyze_performance_test
    ai_analysis_available = True
    logger.info("AI analysis module loaded successfully")
except ImportError as e:
    logger.error(f"Failed to import AI analysis module: {e}")
    logger.warning("AI analysis features will be disabled")
    ai_analysis_available = False
    
    # Define a placeholder function when AI analysis is not available
    async def analyze_performance_test(perf_data):
        return {
            "analysis": "AI analysis is not available. LangGraph or OpenAI API dependencies are missing.",
            "bottlenecks": ["AI analysis is not available"],
            "recommendations": ["Install required dependencies: pip install langchain langchain_core langchain-openai"],
            "next_steps": ["Set OPENAI_API_KEY environment variable"],
            "report": "AI analysis is not available"
        }

# Import database models
from database import PerfTestRun, PerfRunDetail, AIRecommendation, Base

# Database configuration
DATABASE_URL = "sqlite:///./perf.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="AI Performance Tester API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
os.makedirs("jmx_templates", exist_ok=True)
os.makedirs("results", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

# Serve static files (JMeter reports)
app.mount("/reports", StaticFiles(directory="results"), name="reports")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import models from separate file to avoid circular imports
from models import PerfTestRequest, ThresholdConfig, AIAnalysisRequest

# Import JMeter utilities
from jmeter_utils import (
    generate_jmeter_template,
    run_jmeter_test,
    parse_jmeter_csv,
    save_run_details_to_db,
    run_ai_analysis
)

# Import the enhanced workflow
try:
    from enhanced_workflow import EnhancedAIPerformanceTester
    enhanced_workflow_available = True
    enhanced_tester = EnhancedAIPerformanceTester()
    logger.info("Enhanced AI Performance Tester loaded successfully")
except ImportError as e:
    logger.warning(f"Enhanced AI Performance Tester not available: {e}")
    enhanced_workflow_available = False
    enhanced_tester = None

# API routes
@app.post("/run-performance-test")
async def run_performance_test(
    req: PerfTestRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Run a performance test and return results"""
    logger.info(f"Received performance test request: {req.test_name}")
    
    # If enhanced workflow is available, use it
    if enhanced_workflow_available and enhanced_tester:
        try:
            logger.info("Using enhanced AI workflow for performance test")
            enhanced_results = await enhanced_tester.run_enhanced_performance_test(req)
            
            # If the enhanced workflow was successful, return its results
            if enhanced_results.get("workflow_status") not in ["BASIC_IMPLEMENTATION", None]:
                logger.info("Enhanced workflow completed successfully")
                run_id = str(uuid.uuid4())
                
                # Create test run record with enhanced results
                run = PerfTestRun(
                    id=run_id,
                    test_name=req.test_name,
                    test_type=req.test_type,
                    url=req.url,
                    concurrent_users=req.concurrent_users,
                    duration=req.duration,
                    ramp_up_time=req.ramp_up_time,
                    thresholds=req.thresholds.dict() if req.thresholds else None,
                    summary_metrics=enhanced_results.get("summary_metrics", {}),
                    jmx_file_path="enhanced_workflow_used"
                )
                db.add(run)
                db.commit()
                
                # Run AI analysis in background if available
                if ai_analysis_available:
                    background_tasks.add_task(
                        run_ai_analysis,
                        run_id=run_id,
                        parsed_data={"response_times": [], "error_rate_series": [], "throughput_series": []},
                        summary_metrics=enhanced_results.get("summary_metrics", {}),
                        test_request=req,
                        db_func=get_db
                    )
                
                # Handle report paths for enhanced workflow
                jmeter_report_path = enhanced_results.get("jmeter_report_path")
                jmeter_run_id = enhanced_results.get("jmeter_run_id")
                
                if jmeter_report_path and jmeter_run_id:
                    # Use the actual JMeter report path from enhanced workflow
                    detailed_reports = {
                        "executive_html": f"/reports/{jmeter_run_id}/report/index.html",
                        "dashboard_html": f"/reports/{jmeter_run_id}/report/dashboard.html" if os.path.exists(f"results/{jmeter_run_id}/report/dashboard.html") else f"/reports/{jmeter_run_id}/report/index.html"
                    }
                    
                    # Verify the report files exist, create placeholders if they don't
                    executive_report_path = f"results/{jmeter_run_id}/report/index.html"
                    dashboard_report_path = f"results/{jmeter_run_id}/report/dashboard.html"
                    
                    if not os.path.exists(executive_report_path):
                        os.makedirs(os.path.dirname(executive_report_path), exist_ok=True)
                        with open(executive_report_path, "w") as f:
                            f.write("<html><body><h1>JMeter Report</h1><p>Report is being generated or was not created properly.</p></body></html>")
                    
                    if not os.path.exists(dashboard_report_path):
                        os.makedirs(os.path.dirname(dashboard_report_path), exist_ok=True)
                        with open(dashboard_report_path, "w") as f:
                            f.write("<html><body><h1>JMeter Dashboard</h1><p>Dashboard is being generated or was not created properly.</p></body></html>")
                elif jmeter_run_id:
                    # Fallback to default paths if JMeter reports are available but path not provided
                    detailed_reports = {
                        "executive_html": f"/reports/{jmeter_run_id}/report/index.html",
                        "dashboard_html": f"/reports/{jmeter_run_id}/report/dashboard.html" if os.path.exists(f"results/{jmeter_run_id}/report/dashboard.html") else f"/reports/{jmeter_run_id}/report/index.html"
                    }
                    
                    # Verify the report files exist, create placeholders if they don't
                    executive_report_path = f"results/{jmeter_run_id}/report/index.html"
                    dashboard_report_path = f"results/{jmeter_run_id}/report/dashboard.html"
                    
                    if not os.path.exists(executive_report_path):
                        os.makedirs(os.path.dirname(executive_report_path), exist_ok=True)
                        with open(executive_report_path, "w") as f:
                            f.write("<html><body><h1>JMeter Report</h1><p>Report is being generated or was not created properly.</p></body></html>")
                    
                    if not os.path.exists(dashboard_report_path):
                        os.makedirs(os.path.dirname(dashboard_report_path), exist_ok=True)
                        with open(dashboard_report_path, "w") as f:
                            f.write("<html><body><h1>JMeter Dashboard</h1><p>Dashboard is being generated or was not created properly.</p></body></html>")
                else:
                    # Fallback to default paths if no JMeter run ID
                    detailed_reports = {
                        "executive_html": f"/reports/{run_id}/report/index.html",
                        "dashboard_html": f"/reports/{run_id}/report/dashboard.html" if os.path.exists(f"results/{run_id}/report/dashboard.html") else f"/reports/{run_id}/report/index.html"
                    }
                    
                    # Verify the report files exist, create placeholders if they don't
                    executive_report_path = f"results/{run_id}/report/index.html"
                    dashboard_report_path = f"results/{run_id}/report/dashboard.html"
                    
                    if not os.path.exists(executive_report_path):
                        os.makedirs(os.path.dirname(executive_report_path), exist_ok=True)
                        with open(executive_report_path, "w") as f:
                            f.write("<html><body><h1>JMeter Report</h1><p>Report is being generated or was not created properly.</p></body></html>")
                    
                    if not os.path.exists(dashboard_report_path):
                        os.makedirs(os.path.dirname(dashboard_report_path), exist_ok=True)
                        with open(dashboard_report_path, "w") as f:
                            f.write("<html><body><h1>JMeter Dashboard</h1><p>Dashboard is being generated or was not created properly.</p></body></html>")
                
                return {
                    "run_id": run_id,
                    "summary_metrics": enhanced_results.get("summary_metrics", {}),
                    "enhanced_workflow": True,
                    "workflow_status": enhanced_results.get("workflow_status"),
                    "ai_insights": enhanced_results.get("ai_insights", {}),
                    "next_actions": enhanced_results.get("next_actions", []),
                    "detailed_reports": detailed_reports
                }
        except Exception as e:
            logger.error(f"Enhanced workflow failed, falling back to basic implementation: {str(e)}")
            # Continue with basic implementation if enhanced workflow fails
    
    # Fallback to original implementation
    logger.info("Using basic implementation for performance test")
    run_id = str(uuid.uuid4())
    
    # Generate JMeter template
    jmx_file = generate_jmeter_template(req)
    
    try:
        # Run JMeter test
        results_file, report_path = run_jmeter_test(jmx_file, run_id)
        
        # Parse results
        parsed = parse_jmeter_csv(results_file)
        
        # Calculate summary metrics
        summary_metrics = {}
        
        if parsed["response_times"]:
            summary_metrics["avg_response_time"] = round(sum(parsed["response_times"]) / len(parsed["response_times"]), 2)
            summary_metrics["p95_response_time"] = round(sorted(parsed["response_times"])[int(len(parsed["response_times"]) * 0.95) - 1], 2) if len(parsed["response_times"]) > 20 else 0
        else:
            summary_metrics["avg_response_time"] = 0
            summary_metrics["p95_response_time"] = 0
            
        if parsed["error_rate_series"]:
            summary_metrics["error_rate"] = round(max(parsed["error_rate_series"]), 2)
        else:
            summary_metrics["error_rate"] = 0
            
        if parsed["throughput_series"]:
            summary_metrics["throughput"] = max(parsed["throughput_series"])
        else:
            summary_metrics["throughput"] = 0
        
        # Create test run record
        run = PerfTestRun(
            id=run_id,
            test_name=req.test_name,
            test_type=req.test_type,
            url=req.url,
            concurrent_users=req.concurrent_users,
            duration=req.duration,
            ramp_up_time=req.ramp_up_time,
            thresholds=req.thresholds.dict() if req.thresholds else None,
            summary_metrics=summary_metrics,
            jmx_file_path=jmx_file
        )
        db.add(run)
        db.commit()
        
        # Save detailed results
        save_run_details_to_db(db, run_id, parsed)
        
        # Run AI analysis in background
        background_tasks.add_task(
            run_ai_analysis,
            run_id=run_id,
            parsed_data=parsed,
            summary_metrics=summary_metrics,
            test_request=req,
            db_func=get_db
        )
        
        # Ensure report files exist
        executive_report_path = f"results/{run_id}/report/index.html"
        dashboard_report_path = f"results/{run_id}/report/dashboard.html"
        
        if not os.path.exists(executive_report_path):
            os.makedirs(os.path.dirname(executive_report_path), exist_ok=True)
            with open(executive_report_path, "w") as f:
                f.write("<html><body><h1>JMeter Report</h1><p>Report is being generated or was not created properly.</p></body></html>")
        
        if not os.path.exists(dashboard_report_path):
            os.makedirs(os.path.dirname(dashboard_report_path), exist_ok=True)
            with open(dashboard_report_path, "w") as f:
                f.write("<html><body><h1>JMeter Dashboard</h1><p>Dashboard is being generated or was not created properly.</p></body></html>")
        
        # Return response
        return {
            "run_id": run_id,
            "summary_metrics": summary_metrics,
            "detailed_reports": {
                "executive_html": f"/reports/{run_id}/report/index.html",
                "dashboard_html": f"/reports/{run_id}/report/dashboard.html" if os.path.exists(f"results/{run_id}/report/dashboard.html") else f"/reports/{run_id}/report/index.html"
            }
        }
    except Exception as e:
        logger.error(f"Error running performance test: {str(e)}")
        # Clean up generated JMX file on error
        try:
            if os.path.exists(jmx_file):
                os.remove(jmx_file)
        except:
            pass
            
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run performance test: {str(e)}"
        )

@app.get("/performance-history")
def get_history(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Get performance test history"""
    runs = db.query(PerfTestRun).order_by(PerfTestRun.created_at.desc()).all()
    
    return [
        {
            "run_id": r.id,
            "test_name": r.test_name,
            "test_type": r.test_type,
            "url": r.url,
            "concurrent_users": r.concurrent_users,
            "duration": r.duration,
            "avg_response_time": r.summary_metrics.get("avg_response_time"),
            "p95_response_time": r.summary_metrics.get("p95_response_time"),
            "error_rate": r.summary_metrics.get("error_rate"),
            "throughput": r.summary_metrics.get("throughput"),
            "created_at": r.created_at.isoformat() if r.created_at is not None else None,
            "has_ai_analysis": bool(r.ai_analysis)
        }
        for r in runs
    ]

@app.get("/run-details/{run_id}")
def get_run_details(run_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get detailed time series data for a test run"""
    # Get test run
    test_run = db.query(PerfTestRun).filter(PerfTestRun.id == run_id).first()
    if not test_run:
        raise HTTPException(status_code=404, detail="Run details not found")
    
    # Get time series data
    details = db.query(PerfRunDetail).filter(PerfRunDetail.run_id == run_id).order_by(PerfRunDetail.timestamp).all()
    
    # Format response
    return {
        "run_id": run_id,
        "test_name": test_run.test_name,
        "test_type": test_run.test_type,
        "url": test_run.url,
        "concurrent_users": test_run.concurrent_users,
        "duration": test_run.duration,
        "ramp_up_time": test_run.ramp_up_time,
        "created_at": test_run.created_at.isoformat() if test_run.created_at is not None else None,
        "summary_metrics": test_run.summary_metrics,
        "thresholds": test_run.thresholds,
        "report_url": f"/reports/{run_id}/report/index.html",
        "time_series": {
            "timestamps": [d.timestamp.isoformat() for d in details],
            "response_times": [d.avg_response_time for d in details],
            "error_rate_series": [d.error_rate for d in details],
            "throughput_series": [d.throughput for d in details],
        }
    }

@app.get("/ai-analysis/{run_id}")
def get_ai_analysis(run_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get AI analysis for a test run"""
    # Get test run with AI analysis
    test_run = db.query(PerfTestRun).filter(PerfTestRun.id == run_id).first()
    if not test_run:
        raise HTTPException(status_code=404, detail="Test run not found")
    
    # Get recommendations
    recommendations = db.query(AIRecommendation).filter(AIRecommendation.run_id == run_id).all()
    
    # Format recommendations by category using explicit value access
    bottlenecks = [r.description for r in recommendations if getattr(r, 'category', None) == "bottleneck"]
    improvement_recs = [r.description for r in recommendations if getattr(r, 'category', None) == "recommendation"]
    next_tests = [r.description for r in recommendations if getattr(r, 'category', None) == "next_test"]
    
    # Return analysis data
    return {
        "run_id": run_id,
        "test_name": getattr(test_run, 'test_name', ""),
        "full_report": getattr(test_run, 'ai_analysis', None) or "AI analysis not available",
        "bottlenecks": bottlenecks,
        "recommendations": improvement_recs,
        "next_tests": next_tests
    }

@app.post("/request-ai-analysis")
async def request_ai_analysis(
    req: AIAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Request AI analysis for an existing test run"""
    # Get test run
    test_run = db.query(PerfTestRun).filter(PerfTestRun.id == req.run_id).first()
    if not test_run:
        raise HTTPException(status_code=404, detail="Test run not found")
    
    # Get time series data
    details = db.query(PerfRunDetail).filter(PerfRunDetail.run_id == req.run_id).order_by(PerfRunDetail.timestamp).all()
    
    # Format time series data
    parsed_data = {
        "timestamps": [d.timestamp.isoformat() for d in details],
        "response_times": [getattr(d, 'avg_response_time', 0) for d in details],
        "error_rate_series": [getattr(d, 'error_rate', 0) for d in details],
        "throughput_series": [getattr(d, 'throughput', 0) for d in details],
    }
    
    # Extract values from test_run using getattr to avoid type errors
    test_name = getattr(test_run, 'test_name', "")
    test_type = getattr(test_run, 'test_type', "")
    url = getattr(test_run, 'url', "")
    concurrent_users = getattr(test_run, 'concurrent_users', 0)
    duration = getattr(test_run, 'duration', 0)
    ramp_up_time = getattr(test_run, 'ramp_up_time', 0)
    thresholds = getattr(test_run, 'thresholds', None)
    summary_metrics = getattr(test_run, 'summary_metrics', {})
    
    # Create test request model
    test_request = PerfTestRequest(
        test_name=test_name,
        test_type=test_type,
        url=url,
        concurrent_users=concurrent_users,
        duration=duration,
        ramp_up_time=ramp_up_time,
        thresholds=ThresholdConfig(**thresholds) if thresholds and isinstance(thresholds, dict) else None
    )
    
    # Run AI analysis in background
    background_tasks.add_task(
        run_ai_analysis,
        run_id=req.run_id,
        parsed_data=parsed_data,
        summary_metrics=summary_metrics,
        test_request=test_request,
        db_func=get_db
    )
    
    return {
        "status": "success",
        "message": "AI analysis started",
        "run_id": req.run_id
    }

# Add health check endpoint
@app.get("/health")
def health_check() -> Dict[str, Any]:
    """Health check endpoint to verify the server is running"""
    # Check if JMeter is installed
    jmeter_home = os.environ.get('JMETER_HOME', None)
    jmeter_in_path = False
    jmeter_version = None
    
    try:
        # Try running JMeter
        result = subprocess.run(["jmeter", "--version"], capture_output=True, text=True, timeout=10)
        jmeter_in_path = result.returncode == 0
        if jmeter_in_path:
            jmeter_version = result.stdout.strip()
    except Exception as e:
        # If direct jmeter command fails, try other approaches
        try:
            # Try jmeter.bat on Windows
            if os.name == 'nt':
                result = subprocess.run(["jmeter.bat", "--version"], capture_output=True, text=True, timeout=10)
                jmeter_in_path = result.returncode == 0
                if jmeter_in_path:
                    jmeter_version = result.stdout.strip()
        except Exception as e2:
            logger.debug(f"Error checking jmeter.bat in PATH: {str(e2)}")
            logger.warning(f"Error checking JMeter in PATH: {str(e)}")
    
    # Try checking jmeter in JMETER_HOME with full path
    jmeter_home_valid = False
    jmeter_home_version = None
    if jmeter_home:
        jmeter_exec = os.path.join(jmeter_home, "bin", "jmeter.bat" if os.name == 'nt' else "jmeter")
        if os.path.exists(jmeter_exec):
            jmeter_home_valid = True
            try:
                # Try to get version from JMETER_HOME
                result = subprocess.run([jmeter_exec, "--version"], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    jmeter_home_version = result.stdout.strip()
                    # If we found JMeter via JMETER_HOME, consider it as available
                    if not jmeter_in_path:
                        jmeter_in_path = True
                        jmeter_version = jmeter_home_version
            except Exception as e:
                logger.warning(f"Error checking JMeter in JMETER_HOME: {str(e)}")
    
    # Check for a custom JMeter installation in the project directory
    custom_jmeter_path = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), "apache-jmeter-5.6.3")
    custom_jmeter_exists = os.path.exists(custom_jmeter_path)
    
    # If we have a custom JMeter installation, try to use it for version check
    if custom_jmeter_exists and not jmeter_in_path:
        jmeter_exec = os.path.join(custom_jmeter_path, "bin", "jmeter.bat" if os.name == 'nt' else "jmeter")
        if os.path.exists(jmeter_exec):
            try:
                result = subprocess.run([jmeter_exec, "--version"], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    jmeter_in_path = True
                    jmeter_version = result.stdout.strip()
            except Exception as e:
                logger.debug(f"Error checking custom JMeter installation: {str(e)}")
    
    # Check if JMeter server is running by checking for Java processes with JMeter in command line
    jmeter_server_running = False
    try:
        if os.name == 'nt':  # Windows
            # More accurate way to check for JMeter server process
            result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq java.exe"], capture_output=True, text=True)
            # Check if the output contains jmeter-related processes
            if "jmeter" in result.stdout.lower() or "JMeter" in result.stdout:
                jmeter_server_running = True
            else:
                # Also check for processes listening on port 50000
                netstat_result = subprocess.run(["netstat", "-an"], capture_output=True, text=True)
                if ":50000" in netstat_result.stdout and "LISTENING" in netstat_result.stdout:
                    jmeter_server_running = True
        else:  # Unix/Linux
            result = subprocess.run(["ps", "-ef"], capture_output=True, text=True)
            jmeter_server_running = "jmeter" in result.stdout.lower()
    except Exception as e:
        logger.warning(f"Error checking JMeter process: {str(e)}")
    
    # Check if port 50000 is in use (JMeter RMI port)
    port_50000_in_use = False
    # Check if alternative port 51000 is in use
    port_51000_in_use = False
    
    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run(["netstat", "-an"], capture_output=True, text=True)
            port_50000_in_use = ":50000" in result.stdout and "LISTENING" in result.stdout
            
            # Check alternative port
            port_51000_in_use = ":51000" in result.stdout and "LISTENING" in result.stdout
        else:  # Unix/Linux
            result = subprocess.run(["netstat", "-an"], capture_output=True, text=True)
            port_50000_in_use = ":50000" in result.stdout and "LISTEN" in result.stdout
            
            # Check alternative port
            port_51000_in_use = ":51000" in result.stdout and "LISTEN" in result.stdout
    except Exception as e:
        logger.warning(f"Error checking JMeter ports: {str(e)}")
    
    # Check Java
    java_ok = False
    java_version = None
    try:
        result = subprocess.run(["java", "-version"], capture_output=True, text=True, timeout=10)
        java_ok = result.returncode == 0
        if java_ok:
            java_version = result.stderr.strip()
    except Exception as e:
        logger.warning(f"Error checking Java: {str(e)}")
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "jmeter_in_path": jmeter_in_path,
        "jmeter_home": jmeter_home,
        "jmeter_home_valid": jmeter_home_valid,
        "jmeter_home_version": jmeter_home_version,
        "custom_jmeter_exists": custom_jmeter_exists,
        "custom_jmeter_path": custom_jmeter_path if custom_jmeter_exists else None,
        "jmeter_server_running": jmeter_server_running,
        "jmeter_port_active": port_50000_in_use,
        "jmeter_alt_port_active": port_51000_in_use,
        "jmeter_version": jmeter_version,
        "java_installed": java_ok,
        "java_version": java_version,
        "server_directories": {
            "jmx_templates": os.path.exists("jmx_templates"),
            "results": os.path.exists("results"),
            "uploads": os.path.exists("uploads")
        }
    }
