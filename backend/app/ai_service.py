import os
import logging
import json
import uuid
from typing import List, Dict, Any, cast, Optional
from datetime import datetime

# Import models with correct paths
from app.models.db_models import TestCase as DBTestCase, TestStep, TestType, Priority
from app.schemas.ai import AIAnalysisResult
from app.llm_chat import LlmChat
from app.mcp.website_test_generator import website_test_generator

# Initialize logger

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        # AIService no longer requires a specific API key as LlmChat handles multiple providers
        pass
    
    def _create_chat_session(self, system_message: str) -> LlmChat:
        """Create a new chat session with system message"""
        return LlmChat(
            session_id=str(uuid.uuid4()),
            system_message=system_message
        ).with_model("openai", os.environ.get("OPENAI_MODEL", "gpt-4o"))
    
    async def generate_test_cases(self, prompt: str, test_type: TestType, priority: Priority, count: int = 1) -> List[DBTestCase]:
        """Generate test cases using AI"""
        system_message = f"""You are an expert QA engineer specialized in creating comprehensive test cases. 
        Generate {count} detailed test case(s) for {test_type} testing with {priority} priority.
        
        Your response must be a valid JSON array containing test cases with this exact structure:
        {{
            "title": "Clear test case title",
            "description": "Detailed description of what this test validates",
            "steps": [
                {{
                    "step_number": 1,
                    "description": "Detailed step description",
                    "expected_result": "Expected outcome for this step"
                }}
            ],
            "expected_result": "Overall expected result",
            "preconditions": "Any prerequisites or setup needed",
            "tags": ["relevant", "tags"],
            "test_data": {{"key": "value pairs for test data"}}
        }}
        
        Make the test cases comprehensive, realistic, and cover edge cases when appropriate.
        """
        
        try:
            chat = self._create_chat_session(system_message)
            response = await chat.complete_json(prompt)
            
            # Response is already parsed JSON from complete_json
            # Ensure response is treated as Dict/List, not str
            test_cases_data: List[Dict[str, Any]]
            if isinstance(response, list):
                test_cases_data = response
            elif isinstance(response, dict):
                test_cases_data = [response]
            else:
                # Fallback to JSON parsing if response is string
                test_cases_data = json.loads(str(response))
                if not isinstance(test_cases_data, list):
                    test_cases_data = [test_cases_data]
            
            test_cases = []
            for case_data in test_cases_data:
                # Ensure case_data is a dictionary
                if not isinstance(case_data, dict):
                    continue
                    
                # Convert steps to TestStep objects
                steps = []
                for step_data in case_data.get("steps", []):
                    step = TestStep(
                        step_number=step_data["step_number"],
                        description=step_data["description"],
                        expected_result=step_data["expected_result"],
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    steps.append(step)
                
                # Create TestCase object
                test_case = DBTestCase(
                    title=case_data["title"],
                    description=case_data.get("description", ""),
                    project_id="",  # Will be set by the caller
                    test_type=test_type,
                    priority=priority,
                    status="draft",
                    steps=steps,
                    expected_result=case_data.get("expected_result", ""),
                    created_by="",  # Will be set by the caller
                    tags=case_data.get("tags", []),
                    ai_generated=True,
                    self_healing_enabled=True,
                    preconditions=case_data.get("preconditions", ""),
                    test_data=case_data.get("test_data", {})
                )
                test_cases.append(test_case)
            
            return test_cases
            
        except Exception as e:
            logger.error(f"Error generating test cases: {str(e)}")
            raise Exception(f"Failed to generate test cases: {str(e)}")
    
    async def debug_test_failure(self, test_case: DBTestCase, error_message: str, logs: Optional[str] = None) -> AIAnalysisResult:
        """Analyze test failure and provide debugging insights"""
        system_message = """You are an expert QA engineer and debugging specialist. 
        Analyze test failures and provide clear, actionable debugging insights.
        
        Your response must be a valid JSON object with this structure:
        {
            "analysis": "Clear explanation of what went wrong",
            "suggestions": ["Specific actionable suggestions to fix the issue"],
            "confidence_score": 0.85,
            "root_cause": "Identified root cause",
            "fix_suggestions": ["Suggested fixes"],
            "related_issues": ["Related issues found"]
        }
        
        Focus on practical solutions and root cause analysis.
        """
        
        try:
            chat = self._create_chat_session(system_message)
            
            debug_prompt = f"""
            Test Case: {test_case.title}
            Description: {test_case.description}
            Test Type: {test_case.test_type}
            
            Steps:
            {json.dumps([step.dict() for step in test_case.steps], indent=2)}
            
            Error Message: {error_message}
            
            Logs: {logs or "No logs available"}
            
            Please analyze this test failure and provide debugging insights.
            """
            
            response = await chat.complete_json(debug_prompt)
            
            # Response is already parsed JSON from complete_json
            analysis_data: Dict[str, Any] = response if isinstance(response, dict) else {}
            
            return AIAnalysisResult(
                analysis=analysis_data["analysis"],
                suggestions=analysis_data["suggestions"],
                confidence_score=analysis_data["confidence_score"],
                root_cause=analysis_data.get("root_cause"),
                fix_suggestions=analysis_data.get("fix_suggestions", []),
                related_issues=analysis_data.get("related_issues", [])
            )
            
        except Exception as e:
            logger.error(f"Error debugging test failure: {str(e)}")
            return AIAnalysisResult(
                analysis=f"AI debugging failed: {str(e)}",
                suggestions=["Check test configuration", "Review error logs manually"],
                confidence_score=0.0,
                root_cause="AI analysis error",
                fix_suggestions=["Review test manually"],
                related_issues=[]
            )
    
    async def prioritize_test_cases(self, test_cases: List[DBTestCase], context: str) -> List[str]:
        """Prioritize test cases based on context using AI"""
        system_message = """You are an expert QA strategist specializing in test prioritization.
        Analyze the given context and test cases to determine optimal execution order.
        
        Your response must be a valid JSON array containing test case IDs in priority order:
        ["test_case_id_1", "test_case_id_2", "test_case_id_3"]
        
        Consider factors like:
        - Risk assessment
        - Impact of potential failures
        - Dependencies between tests
        - Context-specific requirements
        """
        
        try:
            chat = self._create_chat_session(system_message)
            
            # Prepare test case summaries
            test_summaries = []
            for tc in test_cases:
                test_summaries.append({
                    "id": tc.id,
                    "title": tc.title,
                    "description": tc.description,
                    "type": tc.test_type,
                    "priority": tc.priority,
                    "tags": tc.tags
                })
            
            prioritization_prompt = f"""
            Context: {context}
            
            Test Cases to Prioritize:
            {json.dumps(test_summaries, indent=2)}
            
            Please analyze these test cases and return them in priority order based on the given context.
            Return only the test case IDs in the optimal execution order.
            """
            
            response = await chat.complete_json(prioritization_prompt)
            
            # Response is already parsed JSON from complete_json
            if isinstance(response, list):
                prioritized_ids = [str(item) for item in response]
            elif isinstance(response, dict):
                prioritized_ids = response.get("prioritized_ids", [])
            else:
                prioritized_ids = []
            
            return prioritized_ids
            
        except Exception as e:
            logger.error(f"Error prioritizing test cases: {str(e)}")
            # Return original order if AI fails
            return [str(tc.id) for tc in test_cases]
    
    async def generate_test_insights(self, executions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate insights from test execution data"""
        system_message = """You are an expert QA analyst specialized in test analytics and insights.
        Analyze test execution data to provide valuable insights and recommendations.
        
        Your response must be a valid JSON object with this structure:
        {
            "insights": [
                {
                    "type": "trend|issue|recommendation",
                    "title": "Insight title",
                    "description": "Detailed insight description",
                    "severity": "low|medium|high",
                    "action_items": ["actionable recommendations"]
                }
            ],
            "summary": "Overall summary of test health",
            "recommendations": ["High-level strategic recommendations"]
        }
        """
        
        try:
            chat = self._create_chat_session(system_message)
            
            insights_prompt = f"""
            Test Execution Data:
            {json.dumps(executions, indent=2)}
            
            Please analyze this test execution data and provide insights about:
            - Test performance trends
            - Common failure patterns
            - Areas needing attention
            - Recommendations for improvement
            """
            
            response = await chat.complete_json(insights_prompt)
            
            # Response is already parsed JSON from complete_json
            insights_data: Dict[str, Any] = response if isinstance(response, dict) else {}
            
            return insights_data
            
        except Exception as e:
            logger.error(f"Error generating test insights: {str(e)}")
            return {
                "insights": [],
                "summary": "Unable to generate insights due to AI analysis error",
                "recommendations": ["Review test execution data manually"]
            }
    
    async def suggest_test_improvements(self, test_case: DBTestCase, execution_history: List[Dict[str, Any]]) -> List[str]:
        """Suggest improvements for a test case based on execution history"""
        system_message = """You are an expert QA engineer specializing in test optimization.
        Analyze test cases and their execution history to suggest improvements.
        
        Your response must be a valid JSON array containing specific improvement suggestions:
        ["Suggestion 1", "Suggestion 2", "Suggestion 3"]
        
        Focus on actionable improvements that can enhance test reliability and effectiveness.
        """
        
        try:
            chat = self._create_chat_session(system_message)
            
            improvement_prompt = f"""
            Test Case: {test_case.title}
            Description: {test_case.description}
            Type: {test_case.test_type}
            
            Steps:
            {json.dumps([step.dict() for step in test_case.steps], indent=2)}
            
            Execution History:
            {json.dumps(execution_history, indent=2)}
            
            Please suggest specific improvements for this test case based on its execution history.
            """
            
            response = await chat.complete_json(improvement_prompt)
            
            # Response is already parsed JSON from complete_json
            if isinstance(response, list):
                suggestions = [str(item) for item in response]
            elif isinstance(response, dict):
                suggestions = response.get("suggestions", [])
            else:
                suggestions = []
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error suggesting test improvements: {str(e)}")
            return ["Review test case manually for optimization opportunities"]

    async def generate_test_cases_from_url(self, url: str, project_id: str, test_type: TestType = TestType.FUNCTIONAL, priority: Priority = Priority.MEDIUM, count: int = 5) -> List[Dict[str, Any]]:
        """Generate test cases by analyzing a website URL using MCP server"""
        try:
            # Basic URL validation
            if not url.startswith(('http://', 'https://')):
                raise ValueError(f"Invalid URL format: {url}. URL must start with http:// or https://")
                
            logger.info(f"Generating test cases from URL: {url}")
            
            # Use MCP server to analyze website and generate test cases
            test_cases_data = await website_test_generator.generate_test_cases_from_url(
                url=url,
                project_id=project_id,
                test_count=count
            )
            
            # Convert to the expected format
            formatted_test_cases = []
            for case_data in test_cases_data:
                formatted_test_case = {
                    "title": case_data["title"],
                    "description": case_data["description"],
                    "test_type": case_data.get("test_type", test_type),
                    "priority": case_data.get("priority", priority),
                    "status": "draft",
                    "steps": case_data.get("steps", []),
                    "expected_result": case_data.get("expected_result", ""),
                    "tags": case_data.get("tags", []),
                    "preconditions": case_data.get("preconditions", ""),
                    "test_data": case_data.get("test_data", {}),
                    "ai_generated": True,
                    "self_healing_enabled": True
                }
                formatted_test_cases.append(formatted_test_case)
            
            logger.info(f"Successfully generated {len(formatted_test_cases)} test cases from URL")
            return formatted_test_cases
            
        except Exception as e:
            logger.error(f"Error generating test cases from URL {url}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise ValueError(f"Failed to generate test cases from URL: {str(e)}")

# Create a global instance for easy importing
ai_service = AIService()