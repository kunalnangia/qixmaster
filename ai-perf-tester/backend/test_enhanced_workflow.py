#!/usr/bin/env python3
"""
Test script for the enhanced workflow integration
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import PerfTestRequest, ThresholdConfig
from enhanced_workflow import EnhancedAIPerformanceTester

async def test_enhanced_workflow():
    """Test the enhanced workflow"""
    print("Testing Enhanced AI Performance Tester...")
    
    # Create a test request
    test_request = PerfTestRequest(
        test_name="Enhanced Workflow Test",
        test_type="load",
        url="https://httpbin.org/get",
        concurrent_users=10,
        duration=30,
        ramp_up_time=5,
        thresholds=ThresholdConfig(
            response_time=1000,
            error_rate=1,
            throughput=10
        )
    )
    
    # Initialize the enhanced tester
    tester = EnhancedAIPerformanceTester()
    
    if tester.workflow is None:
        print("❌ LangGraph not available, testing basic implementation")
        try:
            results = await tester.run_enhanced_performance_test(test_request)
            print(f"✅ Basic implementation test completed: {results}")
        except Exception as e:
            print(f"❌ Basic implementation test failed: {e}")
    else:
        print("✅ LangGraph available, testing enhanced workflow")
        try:
            results = await tester.run_enhanced_performance_test(test_request)
            print(f"✅ Enhanced workflow test completed: {results}")
        except Exception as e:
            print(f"❌ Enhanced workflow test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_workflow())