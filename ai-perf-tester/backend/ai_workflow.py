"""
LangGraph Workflow for Performance Test Analysis and Recommendations
"""

import os
import sys
from typing import Dict, List, Any, Annotated, TypedDict
from dotenv import load_dotenv

# Try to load from multiple possible locations, prioritizing root directory
# 1. Check if we're in the ai-perf-tester directory structure
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
root_env = os.path.join(project_root, ".env")
backend_env = os.path.join(current_dir, ".env")

# Load environment variables - prioritize root .env but fallback to backend .env
env_loaded = False

# Try root .env first (where the API keys are)
if os.path.exists(root_env):
    print(f"Loading environment from root: {root_env}")
    load_dotenv(root_env, override=True)
    env_loaded = True
# Try backend .env as fallback
elif os.path.exists(backend_env):
    print(f"Loading environment from backend: {backend_env}")
    load_dotenv(backend_env, override=True)
    env_loaded = True
else:
    print("Warning: No .env file found. Please create one with your API keys.")

if not env_loaded:
    print("Warning: No .env file found. Please create one with your API keys.")

# Try to import LangChain dependencies with better error handling
try:
    from langchain_core.messages import HumanMessage, SystemMessage
    from langgraph.graph import StateGraph
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

# Try to import Gemini integration
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    gemini_imports_successful = True
except ImportError as e:
    print(f"Warning: langchain_google_genai module not available: {e}")
    print("To install: pip install langchain_google_genai")
    gemini_imports_successful = False
except Exception as e:
    print(f"Warning: Error importing langchain_google_genai: {e}")
    gemini_imports_successful = False
    
# Overall success flag for LangChain ecosystem
langchain_imports_successful = langchain_core_imports_successful and (openai_imports_successful or gemini_imports_successful)

# Add explicit type definitions to avoid "possibly unbound" errors
# These will be overridden if the actual classes are imported successfully
ChatOpenAI = None  # type: ignore
ChatGoogleGenerativeAI = None  # type: ignore
StateGraph = None  # type: ignore
SystemMessage = None  # type: ignore
HumanMessage = None  # type: ignore

# Now try to import the actual classes if available
if openai_imports_successful:
    from langchain_openai import ChatOpenAI  # type: ignore

if gemini_imports_successful:
    from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore

if langchain_core_imports_successful:
    from langgraph.graph import StateGraph  # type: ignore
    from langchain_core.messages import HumanMessage, SystemMessage  # type: ignore

# Define state types
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
    
class AnalysisState(TypedDict):
    perf_data: PerformanceData
    analysis: str
    bottlenecks: List[str]
    recommendations: List[str]
    next_steps: List[str]
    output_report: str

# Initialize LLM with enhanced error handling and fallback support
llm = None  # type: ignore
llm_available = False
used_model = "none"
available_providers = []

if langchain_imports_successful:
    # Check which providers are available and their API keys
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    gemini_api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    
    # Build list of available providers based on priority order
    ai_model_priority = os.environ.get("AI_MODEL_PRIORITY", "openai,google").split(",")
    
    for provider in ai_model_priority:
        provider = provider.strip()
        
        if provider == "openai" and openai_imports_successful and openai_api_key:
            try:
                ai_model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
                temp_llm = ChatOpenAI(
                    model=ai_model,
                    temperature=0,
                    api_key=openai_api_key  # type: ignore
                )  # type: ignore
                available_providers.append({
                    "name": "openai",
                    "instance": temp_llm,
                    "model": ai_model
                })
                print(f"Successfully initialized OpenAI LLM with model: {ai_model}")
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI LLM: {e}")
        
        elif provider == "google" and gemini_imports_successful and gemini_api_key:
            try:
                gemini_model = os.environ.get("GOOGLE_MODEL", "gemini-pro")
                temp_llm = ChatGoogleGenerativeAI(
                    model=gemini_model,
                    temperature=0,
                    api_key=gemini_api_key  # type: ignore
                )  # type: ignore
                available_providers.append({
                    "name": "google",
                    "instance": temp_llm,
                    "model": gemini_model
                })
                print(f"Successfully initialized Gemini LLM with model: {gemini_model}")
            except Exception as e:
                print(f"Warning: Could not initialize Gemini LLM: {e}")
    
    # Set the first available provider as the current LLM
    if available_providers:
        llm = available_providers[0]["instance"]
        llm_available = True
        used_model = f"{available_providers[0]['name']} ({available_providers[0]['model']})"
        print(f"Using {used_model} as primary AI provider")
    else:
        print("Warning: No LLM could be initialized. AI analysis features will be disabled.")
        print("Please set either OPENAI_API_KEY or GOOGLE_API_KEY/GEMINI_API_KEY in the .env file.")

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

# Define analysis nodes
async def analyze_performance_data(state: AnalysisState) -> AnalysisState:
    """Analyze the performance test data and identify patterns"""
    # If LLM is not available, return early
    if not llm_available:
        return {
            **state,
            "analysis": "AI analysis is not available. Please set OPENAI_API_KEY or GEMINI_API_KEY environment variable in the .env file to enable AI features."
        }
    
    perf_data = state["perf_data"]
    
    prompt = f"""
    Analyze the following performance test results:
    
    Test Name: {perf_data['test_name']}
    Test Type: {perf_data['test_type']}
    URL: {perf_data['url']}
    Configuration: {perf_data['concurrent_users']} concurrent users, {perf_data['duration']}s duration, {perf_data['ramp_up_time']}s ramp-up
    
    Summary Metrics:
    - Average Response Time: {perf_data['summary_metrics'].get('avg_response_time', 'N/A')} ms
    - 95th Percentile Response Time: {perf_data['summary_metrics'].get('p95_response_time', 'N/A')} ms
    - Error Rate: {perf_data['summary_metrics'].get('error_rate', 'N/A')}%
    - Throughput: {perf_data['summary_metrics'].get('throughput', 'N/A')} requests/min
    
    Provide a comprehensive analysis of these test results. Identify any patterns, anomalies, 
    or performance issues. Focus on actionable insights that can help improve the system's performance.
    """
    
    messages = [
        SystemMessage(content="You are a performance testing expert. Analyze test results and identify performance issues."),  # type: ignore
        HumanMessage(content=prompt)  # type: ignore
    ]
    
    try:
        response, provider_used = await _invoke_llm_with_fallback(messages, "openai")
        analysis = str(response.content)
    except Exception as e:
        analysis = f"AI analysis failed: {str(e)}"
    
    return {
        **state,
        "analysis": analysis
    }

async def identify_bottlenecks(state: AnalysisState) -> AnalysisState:
    """Identify performance bottlenecks from the analysis"""
    # If LLM is not available, return early
    if not llm_available:
        return {
            **state,
            "bottlenecks": ["AI analysis is not available. Please set OPENAI_API_KEY or GEMINI_API_KEY environment variable in the .env file to enable AI features."]
        }
    
    analysis = state["analysis"]
    perf_data = state["perf_data"]
    
    prompt = f"""
    Based on this performance analysis:
    {analysis}
    
    And these test results:
    - Test Name: {perf_data['test_name']}
    - Test Type: {perf_data['test_type']}
    - URL: {perf_data['url']}
    - Average Response Time: {perf_data['summary_metrics'].get('avg_response_time', 'N/A')} ms
    - Error Rate: {perf_data['summary_metrics'].get('error_rate', 'N/A')}%
    - Throughput: {perf_data['summary_metrics'].get('throughput', 'N/A')} requests/min
    
    Identify 3-5 specific performance bottlenecks. For each bottleneck, specify:
    1. What component or area is affected
    2. The likely root cause
    3. The impact on performance
    """
    
    messages = [
        SystemMessage(content="You are a performance optimization expert. Identify specific bottlenecks."),  # type: ignore
        HumanMessage(content=prompt)  # type: ignore
    ]
    
    try:
        response, provider_used = await _invoke_llm_with_fallback(messages, "openai")
        
        # Extract bottlenecks as a list
        bottlenecks_text = str(response.content)
        bottlenecks = [line.strip() for line in bottlenecks_text.split("\n") if line.strip().startswith("- ")]
        
        # If no formatted list is found, use the entire text
        if not bottlenecks:
            bottlenecks = [bottlenecks_text]
    except Exception as e:
        bottlenecks = [f"AI bottleneck identification failed: {str(e)}"]
    
    return {
        **state,
        "bottlenecks": bottlenecks
    }

async def generate_recommendations(state: AnalysisState) -> AnalysisState:
    """Generate recommendations to address the bottlenecks"""
    # If LLM is not available, return early
    if not llm_available:
        return {
            **state,
            "recommendations": ["AI analysis is not available. Please set OPENAI_API_KEY or GEMINI_API_KEY environment variable in the .env file to enable AI features."]
        }
    
    analysis = state["analysis"]
    bottlenecks = state["bottlenecks"]
    
    bottlenecks_text = "\n".join([f"- {b}" for b in bottlenecks])
    
    prompt = f"""
    Based on this performance analysis:
    {analysis}
    
    And these identified bottlenecks:
    {bottlenecks_text}
    
    Provide specific, actionable recommendations to improve performance. Include code examples
    or configuration changes where appropriate. Focus on practical solutions that could be
    implemented immediately.
    """
    
    messages = [
        SystemMessage(content="You are a performance optimization expert. Provide actionable recommendations."),  # type: ignore
        HumanMessage(content=prompt)  # type: ignore
    ]
    
    try:
        response, provider_used = await _invoke_llm_with_fallback(messages, "openai")
        
        # Extract recommendations as a list
        recommendations_text = str(response.content)
        recommendations = [line.strip() for line in recommendations_text.split("\n") if line.strip().startswith("- ")]
        
        # If no formatted list is found, use the entire text
        if not recommendations:
            recommendations = [recommendations_text]
    except Exception as e:
        recommendations = [f"AI recommendation generation failed: {str(e)}"]
    
    return {
        **state,
        "recommendations": recommendations
    }

async def suggest_next_tests(state: AnalysisState) -> AnalysisState:
    """Suggest next performance tests to run based on the analysis"""
    # If LLM is not available, return early
    if not llm_available:
        return {
            **state,
            "next_steps": ["AI analysis is not available. Please set OPENAI_API_KEY environment variable to enable AI features."]
        }
    
    analysis = state["analysis"]
    bottlenecks = state["bottlenecks"]
    recommendations = state["recommendations"]
    
    bottlenecks_text = "\n".join([f"- {b}" for b in bottlenecks])
    recommendations_text = "\n".join([f"- {r}" for r in recommendations])
    
    prompt = f"""
    Based on the performance analysis, bottlenecks, and recommendations:
    
    Analysis: {analysis}
    
    Bottlenecks:
    {bottlenecks_text}
    
    Recommendations:
    {recommendations_text}
    
    Suggest 3-5 specific next performance tests that should be run to:
    1. Validate the effectiveness of the recommendations
    2. Further investigate potential bottlenecks
    3. Explore other performance aspects not yet covered
    
    For each test, specify the test type, configuration parameters, and what to look for in the results.
    """
    
    messages = [
        SystemMessage(content="You are a performance testing expert. Suggest logical next tests to run."),  # type: ignore
        HumanMessage(content=prompt)  # type: ignore
    ]
    
    try:
        response, provider_used = await _invoke_llm_with_fallback(messages, "openai")
        
        # Extract next steps as a list
        next_steps_text = str(response.content)
        next_steps = [line.strip() for line in next_steps_text.split("\n") if line.strip().startswith("- ")]
        
        # If no formatted list is found, use the entire text
        if not next_steps:
            next_steps = [next_steps_text]
    except Exception as e:
        next_steps = [f"AI next test suggestion failed: {str(e)}"]
    
    return {
        **state,
        "next_steps": next_steps
    }

async def generate_final_report(state: AnalysisState) -> AnalysisState:
    """Generate a comprehensive final report with all findings"""
    test_name = state["perf_data"]["test_name"]
    test_type = state["perf_data"]["test_type"]
    url = state["perf_data"]["url"]
    analysis = state["analysis"]
    bottlenecks = state["bottlenecks"]
    recommendations = state["recommendations"]
    next_steps = state["next_steps"]
    
    bottlenecks_text = "\n".join([f"- {b}" for b in bottlenecks])
    recommendations_text = "\n".join([f"- {r}" for r in recommendations])
    next_steps_text = "\n".join([f"- {s}" for s in next_steps])
    
    report = f"""
    # Performance Test Analysis Report
    
    ## Test Information
    - **Test Name**: {test_name}
    - **Test Type**: {test_type}
    - **URL Tested**: {url}
    - **Configuration**: {state["perf_data"]["concurrent_users"]} concurrent users, {state["perf_data"]["duration"]}s duration, {state["perf_data"]["ramp_up_time"]}s ramp-up
    
    ## Summary Metrics
    - **Average Response Time**: {state["perf_data"]["summary_metrics"].get("avg_response_time", "N/A")} ms
    - **95th Percentile Response Time**: {state["perf_data"]["summary_metrics"].get("p95_response_time", "N/A")} ms
    - **Error Rate**: {state["perf_data"]["summary_metrics"].get("error_rate", "N/A")}%
    - **Throughput**: {state["perf_data"]["summary_metrics"].get("throughput", "N/A")} requests/min
    
    ## Analysis
    {analysis}
    
    ## Identified Bottlenecks
    {bottlenecks_text}
    
    ## Recommendations
    {recommendations_text}
    
    ## Suggested Next Tests
    {next_steps_text}
    """
    
    return {
        **state,
        "output_report": report
    }

# Create LangGraph workflow
def create_performance_analysis_graph() -> "StateGraph":  # type: ignore
    """Create a LangGraph workflow for performance test analysis"""
    # Define the graph
    workflow = StateGraph(AnalysisState)  # type: ignore
    
    # Add nodes
    workflow.add_node("analyze_data", analyze_performance_data)
    workflow.add_node("identify_bottlenecks", identify_bottlenecks)
    workflow.add_node("generate_recommendations", generate_recommendations)
    workflow.add_node("suggest_next_tests", suggest_next_tests)
    workflow.add_node("generate_report", generate_final_report)
    
    # Add edges
    workflow.add_edge("analyze_data", "identify_bottlenecks")
    workflow.add_edge("identify_bottlenecks", "generate_recommendations")
    workflow.add_edge("generate_recommendations", "suggest_next_tests")
    workflow.add_edge("suggest_next_tests", "generate_report")
    
    # Set entry point
    workflow.set_entry_point("analyze_data")
    
    return workflow

# Function to run the analysis
async def analyze_performance_test(perf_data: PerformanceData) -> Dict[str, Any]:
    """Run the performance analysis workflow on test data"""
    # Initialize the graph
    graph = create_performance_analysis_graph()
    
    # Compile the graph
    app = graph.compile()
    
    # Create initial state
    initial_state: AnalysisState = {
        "perf_data": perf_data,
        "analysis": "",
        "bottlenecks": [],
        "recommendations": [],
        "next_steps": [],
        "output_report": ""
    }
    
    # Run the workflow
    try:
        result = await app.ainvoke(initial_state)
        return {
            "analysis": result["analysis"],
            "bottlenecks": result["bottlenecks"],
            "recommendations": result["recommendations"],
            "next_steps": result["next_steps"],
            "report": result["output_report"]
        }
    except Exception as e:
        return {
            "analysis": f"AI analysis workflow failed: {str(e)}",
            "bottlenecks": [],
            "recommendations": [],
            "next_steps": [],
            "report": f"# Performance Test Analysis Report\n\nAI analysis workflow failed: {str(e)}"
        }