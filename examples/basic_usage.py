"""
Basic OpenAGI Platform Usage Example

Demonstrates core functionality of the OpenAGI platform including
model loading, pipeline creation, and self-testing.
"""

import asyncio
from openagi import OpenAGI, SelfTestSuite
from openagi.config.manager import get_config


async def main():
    """Main example function."""
    print("🤖 OpenAGI Platform Example")
    print("=" * 50)
    
    # Initialize the platform
    print("\n1. Initializing OpenAGI Platform...")
    agi = OpenAGI(auto_start=True)
    
    try:
        # Get platform status
        print("\n2. Getting platform status...")
        status = await agi.get_status()
        print(f"   Platform ID: {status.id}")
        print(f"   Status: {status.status}")
        print(f"   Models loaded: {status.models_loaded}")
        print(f"   Active sessions: {status.active_sessions}")
        print(f"   CPU usage: {status.cpu_usage:.1f}%")
        print(f"   Memory usage: {status.memory_usage:.1f}%")
        
        # Create a session
        print("\n3. Creating user session...")
        session_id = await agi.create_session("demo_user")
        print(f"   Session ID: {session_id}")
        
        # Create AI pipeline
        print("\n4. Creating AI pipeline...")
        pipeline_id = await agi.create_pipeline(
            models=["gpt-base", "vision-base"],
            session_id=session_id
        )
        print(f"   Pipeline ID: {pipeline_id}")
        
        # Run inference
        print("\n5. Running inference...")
        inputs = {
            "text": "Hello, OpenAGI! Please process this text.",
            "image": "demo_image.jpg",
            "parameters": {
                "max_length": 100,
                "temperature": 0.7
            }
        }
        
        result = await agi.process(pipeline_id, inputs)
        print(f"   Processing completed in {result.get('processing_time_ms', 0)}ms")
        print(f"   Result: {result.get('outputs', {}).get('result', 'No result')}")
        
        # Run self-tests
        print("\n6. Running self-tests...")
        test_results = await agi.run_tests(
            suite="quick",  # Run quick test suite for demo
            models=["gpt-base"]
        )
        
        print(f"   Tests completed:")
        print(f"   Total: {test_results.get('total_tests', 0)}")
        print(f"   Passed: {test_results.get('passed', 0)}")
        print(f"   Failed: {test_results.get('failed', 0)}")
        print(f"   Errors: {test_results.get('errors', 0)}")
        
        if test_results.get('total_tests', 0) > 0:
            pass_rate = test_results.get('passed', 0) / test_results.get('total_tests', 1)
            print(f"   Pass rate: {pass_rate:.2%}")
        
        # Close session
        print("\n7. Cleaning up...")
        await agi.close_session(session_id)
        print("   Session closed")
        
    finally:
        # Stop the platform
        await agi.stop()
        print("   Platform stopped")
    
    print("\n✅ Example completed successfully!")


async def test_framework_example():
    """Example of using the testing framework directly."""
    print("\n🧪 Self-Testing Framework Example")
    print("=" * 50)
    
    # Get configuration
    config = get_config()
    
    # Initialize test suite
    test_suite = SelfTestSuite(config.testing.to_dict())
    
    print("\n1. Running focused test suite...")
    
    # Run a small subset of tests for demonstration
    result = await test_suite.run_suite(
        suite_name="demo",
        sample_rate=0.001,  # Run 0.1% of tests
        max_parallel=2
    )
    
    print(f"\n2. Test results:")
    print(f"   Suite: {result.suite_name}")
    print(f"   Total tests: {result.total_tests}")
    print(f"   Passed: {result.passed}")
    print(f"   Failed: {result.failed}")
    print(f"   Errors: {result.errors}")
    print(f"   Duration: {(result.end_time - result.start_time).total_seconds():.2f}s")
    
    # Generate report
    if result.summary_metrics:
        print(f"\n3. Performance metrics:")
        metrics = result.summary_metrics
        print(f"   Avg execution time: {metrics.get('avg_execution_time_ms', 0):.2f}ms")
        print(f"   P95 execution time: {metrics.get('p95_execution_time_ms', 0):.2f}ms")
        print(f"   Pass rate: {metrics.get('pass_rate', 0):.2%}")
        print(f"   Error rate: {metrics.get('error_rate', 0):.2%}")
    
    print("\n✅ Testing framework example completed!")


if __name__ == "__main__":
    # Run the main example
    asyncio.run(main())
    
    # Run the testing framework example
    asyncio.run(test_framework_example())