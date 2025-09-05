"""
Advanced OpenAGI Platform Usage Example

Demonstrates advanced features including custom models,
extensive testing scenarios, and performance monitoring.
"""

import asyncio
import time
from typing import Dict, Any
from openagi import OpenAGI, BaseModel
from openagi.testing.framework import TestCategory, TestCase
from openagi.api.client import APIClient


class CustomAIModel(BaseModel):
    """Example custom AI model implementation."""
    
    async def load(self) -> bool:
        """Load the custom model."""
        print(f"Loading custom model: {self.name}")
        await asyncio.sleep(0.1)  # Simulate loading time
        self.loaded = True
        return True
    
    async def unload(self) -> bool:
        """Unload the custom model."""
        print(f"Unloading custom model: {self.name}")
        self.loaded = False
        return True
    
    async def predict(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run prediction on custom model."""
        if not self.loaded:
            raise RuntimeError("Model not loaded")
        
        # Simulate processing
        await asyncio.sleep(0.05)
        
        return {
            "model": self.name,
            "inputs_processed": len(inputs),
            "prediction": f"Custom prediction from {self.name}",
            "confidence": 0.92,
            "processing_time_ms": 50
        }
    
    async def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate inputs for custom model."""
        return isinstance(inputs, dict) and len(inputs) > 0


async def advanced_platform_example():
    """Advanced platform usage example."""
    print("🚀 Advanced OpenAGI Platform Example")
    print("=" * 60)
    
    # Initialize platform with custom configuration
    agi = OpenAGI(auto_start=True)
    
    try:
        # Register custom model
        print("\n1. Registering custom AI model...")
        custom_model = CustomAIModel("custom-nlp-model")
        await custom_model.load()
        
        # Create multiple sessions for load testing
        print("\n2. Creating multiple sessions...")
        sessions = []
        for i in range(5):
            session_id = await agi.create_session(f"user_{i}")
            sessions.append(session_id)
        
        print(f"   Created {len(sessions)} sessions")
        
        # Create multiple pipelines
        print("\n3. Creating AI pipelines...")
        pipelines = []
        for i, session_id in enumerate(sessions):
            models = ["gpt-base", "vision-base"] if i % 2 == 0 else ["audio-base", "multimodal-base"]
            pipeline_id = await agi.create_pipeline(models, session_id)
            pipelines.append(pipeline_id)
        
        print(f"   Created {len(pipelines)} pipelines")
        
        # Concurrent inference testing
        print("\n4. Running concurrent inference tests...")
        start_time = time.time()
        
        async def run_inference_batch(pipeline_id: str, batch_size: int = 10):
            """Run a batch of inference requests."""
            results = []
            for i in range(batch_size):
                inputs = {
                    "text": f"Test input {i} for pipeline {pipeline_id}",
                    "data": list(range(i * 10, (i + 1) * 10)),
                    "metadata": {"batch": i, "pipeline": pipeline_id}
                }
                result = await agi.process(pipeline_id, inputs)
                results.append(result)
            return results
        
        # Run concurrent batches
        tasks = [run_inference_batch(pid, 5) for pid in pipelines]
        batch_results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_requests = sum(len(batch) for batch in batch_results)
        
        print(f"   Processed {total_requests} requests in {end_time - start_time:.2f}s")
        print(f"   Throughput: {total_requests / (end_time - start_time):.2f} req/s")
        
        # Run comprehensive self-tests
        print("\n5. Running comprehensive self-tests...")
        test_results = await agi.run_tests(
            suite="comprehensive",
            models=["gpt-base", "vision-base", "audio-base"]
        )
        
        print(f"   Comprehensive test results:")
        print(f"   Total: {test_results.get('total_tests', 0)}")
        print(f"   Passed: {test_results.get('passed', 0)}")
        print(f"   Failed: {test_results.get('failed', 0)}")
        print(f"   Pass rate: {test_results.get('passed', 0) / max(test_results.get('total_tests', 1), 1):.2%}")
        
        # Performance monitoring
        print("\n6. Performance monitoring...")
        status = await agi.get_status()
        print(f"   CPU usage: {status.cpu_usage:.1f}%")
        print(f"   Memory usage: {status.memory_usage:.1f}%")
        print(f"   Active sessions: {status.active_sessions}")
        
        # Cleanup
        print("\n7. Cleaning up resources...")
        for session_id in sessions:
            await agi.close_session(session_id)
        
        await custom_model.unload()
        
    finally:
        await agi.stop()
    
    print("\n✅ Advanced example completed successfully!")


async def api_client_example():
    """Example using the API client."""
    print("\n🌐 API Client Example")
    print("=" * 40)
    
    # Note: This assumes the OpenAGI server is running
    async with APIClient("http://localhost:8000") as client:
        try:
            # Check server status
            status = await client.get_status()
            print(f"Server status: {status.get('status', 'unknown')}")
            
            # List available models
            models = await client.list_models()
            print(f"Available models: {len(models)}")
            
            # Create session via API
            session_resp = await client.create_session("api_user")
            session_id = session_resp.get("session_id")
            print(f"Created session: {session_id}")
            
            # Create pipeline via API
            pipeline_resp = await client.create_pipeline(
                models=["gpt-base"],
                session_id=session_id
            )
            pipeline_id = pipeline_resp.get("pipeline_id")
            print(f"Created pipeline: {pipeline_id}")
            
            # Run inference via API
            inference_result = await client.run_inference(
                pipeline_id=pipeline_id,
                inputs={"text": "API test input"}
            )
            print(f"Inference result: {inference_result.get('outputs', {})}")
            
            print("✅ API client example completed!")
            
        except Exception as e:
            print(f"❌ API client example failed: {e}")
            print("   (This is expected if the server is not running)")


async def stress_testing_example():
    """Example of stress testing the platform."""
    print("\n💪 Stress Testing Example")
    print("=" * 40)
    
    agi = OpenAGI(auto_start=True)
    
    try:
        print("\n1. Creating stress test scenario...")
        
        # Create many sessions rapidly
        session_ids = []
        start_time = time.time()
        
        for i in range(20):
            session_id = await agi.create_session(f"stress_user_{i}")
            session_ids.append(session_id)
        
        session_creation_time = time.time() - start_time
        print(f"   Created {len(session_ids)} sessions in {session_creation_time:.2f}s")
        
        # Create pipelines for each session
        pipeline_ids = []
        start_time = time.time()
        
        for session_id in session_ids:
            pipeline_id = await agi.create_pipeline(["gpt-base"], session_id)
            pipeline_ids.append(pipeline_id)
        
        pipeline_creation_time = time.time() - start_time
        print(f"   Created {len(pipeline_ids)} pipelines in {pipeline_creation_time:.2f}s")
        
        # Stress test with concurrent requests
        print("\n2. Running stress test...")
        
        async def stress_inference(pipeline_id: str, request_count: int = 10):
            """Generate stress load on a pipeline."""
            for i in range(request_count):
                inputs = {
                    "text": f"Stress test request {i}",
                    "load_factor": i,
                    "timestamp": time.time()
                }
                await agi.process(pipeline_id, inputs)
        
        # Run stress test
        start_time = time.time()
        stress_tasks = [stress_inference(pid, 5) for pid in pipeline_ids[:10]]  # Use first 10 pipelines
        await asyncio.gather(*stress_tasks)
        stress_time = time.time() - start_time
        
        total_requests = 10 * 5  # 10 pipelines * 5 requests each
        print(f"   Processed {total_requests} stress requests in {stress_time:.2f}s")
        print(f"   Stress throughput: {total_requests / stress_time:.2f} req/s")
        
        # Check platform health after stress test
        status = await agi.get_status()
        print(f"\n3. Post-stress platform health:")
        print(f"   CPU usage: {status.cpu_usage:.1f}%")
        print(f"   Memory usage: {status.memory_usage:.1f}%")
        print(f"   Active sessions: {status.active_sessions}")
        
        # Cleanup stress test resources
        for session_id in session_ids:
            await agi.close_session(session_id)
        
        print("✅ Stress testing completed!")
        
    finally:
        await agi.stop()


if __name__ == "__main__":
    # Run all advanced examples
    asyncio.run(advanced_platform_example())
    asyncio.run(api_client_example())
    asyncio.run(stress_testing_example())