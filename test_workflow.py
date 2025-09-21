#!/usr/bin/env python3
"""
Simple test script to verify the workflow implementation
"""

from complete_ai_performance_testing_system import (
    ComprehensiveAIPerformanceTester,
    TestInput,
    TestType,
    EndpointConfig,
    LoadPattern,
    PerformanceThresholds,
    InfrastructureConfig,
    TestEnvironment
)

def create_simple_test():
    """Create a simple test configuration"""
    # Define a simple endpoint
    endpoint = EndpointConfig(
        name="Health Check",
        url="https://httpbin.org/get",
        method="GET",
        timeout=30
    )
    
    # Define a simple load pattern
    load_pattern = LoadPattern(
        name="Simple Load Test",
        pattern_type="steady_state",
        concurrent_users=10,
        ramp_up_time=30,
        duration=60,
        ramp_down_time=30
    )
    
    # Define simple performance thresholds
    thresholds = PerformanceThresholds(
        max_avg_response_time=5000,    # 5 seconds
        max_95th_percentile=10000,     # 10 seconds
        max_99th_percentile=15000,     # 15 seconds
        min_throughput=1,              # 1 req/sec minimum
        max_error_rate=5.0,            # 5% error rate
        max_cpu_usage=90.0,            # 90% CPU
        max_memory_usage=90.0,         # 90% Memory
        max_disk_io=100.0              # 100 MB/s
    )
    
    # Define simple infrastructure
    infrastructure = InfrastructureConfig(
        servers=["localhost"],
        databases=[],
        redis_instances=[],
        monitoring_tools={},
        custom_metrics=[]
    )
    
    # Define test environment
    environment = TestEnvironment(
        name="Local Test Environment",
        base_url="https://httpbin.org",
        infrastructure=infrastructure,
        test_data_setup={},
        cleanup_scripts=[]
    )
    
    # Create complete test input
    return TestInput(
        test_name="Simple Health Check Test",
        test_type=TestType.LOAD,
        description="Simple test to verify the workflow implementation",
        environment=environment,
        endpoints=[endpoint],
        load_patterns=[load_pattern],
        thresholds=thresholds
    )

if __name__ == "__main__":
    print("Testing the AI Performance Testing System...")
    
    # Create test configuration
    test_config = create_simple_test()
    
    # Initialize the testing system
    tester = ComprehensiveAIPerformanceTester()
    
    print(f"Test system initialized with JMeter path: {tester.jmeter_path}")
    print(f"Working directory: {tester.work_dir}")
    print(f"Workflow created: {tester.workflow is not None}")
    
    print("\nTest configuration:")
    print(f"  Test name: {test_config.test_name}")
    print(f"  Endpoints: {[ep.name for ep in test_config.endpoints]}")
    print(f"  Load patterns: {[lp.name for lp in test_config.load_patterns]}")
    
    print("\n✅ Test setup completed successfully!")
    print("Note: To run the full test, you would need to execute:")
    print("  import asyncio")
    print("  asyncio.run(tester.run_complete_performance_test(test_config))")