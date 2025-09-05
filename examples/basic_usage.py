"""
Example: Basic OpenAGI Usage

This example demonstrates how to:
1. Initialize the OpenAGI engine
2. Process different types of tasks
3. Monitor system performance
4. Trigger learning and evolution
"""

import asyncio
import json
from openagi import OpenAGIEngine


async def main():
    print("🚀 OpenAGI Basic Example")
    print("=" * 50)
    
    # Initialize the OpenAGI engine
    print("1. Initializing OpenAGI Engine...")
    engine = OpenAGIEngine()
    await engine.initialize()
    
    try:
        # Show initial status
        status = engine.get_status()
        print(f"   ✅ Engine initialized with {len(status['agents'])} agents")
        print(f"   🔌 Loaded {len(status['plugins'])} plugins/features")
        
        # Example 1: Text Processing Task
        print("\n2. Processing Text Analysis Task...")
        text_task = {
            "id": "example_text_task",
            "type": "text_processing",
            "data": {
                "text": "OpenAGI is a revolutionary AI platform with self-learning capabilities.",
                "operation": "sentiment"
            },
            "requirements": ["natural_language"]
        }
        
        result = await engine.process_task(text_task)
        print(f"   📊 Task Status: {result['status']}")
        print(f"   🤖 Processed by: {result['agent']}")
        print(f"   ⏱️  Execution Time: {result['execution_time']:.2f}s")
        if result.get('result'):
            print(f"   📈 Result: {json.dumps(result['result'], indent=6)}")
        
        # Example 2: Data Analysis Task
        print("\n3. Processing Data Analysis Task...")
        data_task = {
            "id": "example_data_task",
            "type": "data_analysis",
            "data": {
                "dataset": [1, 2, 3, 4, 5, 10, 2, 3, 4, 6],
                "analysis_type": "statistical"
            },
            "requirements": ["data_analysis", "statistics"]
        }
        
        result = await engine.process_task(data_task)
        print(f"   📊 Task Status: {result['status']}")
        print(f"   🤖 Processed by: {result['agent']}")
        print(f"   📈 Insights: {len(result.get('result', {}).get('insights', []))} found")
        
        # Example 3: Problem Solving Task
        print("\n4. Processing Problem Solving Task...")
        problem_task = {
            "id": "example_problem_task",
            "type": "problem_solving",
            "data": {
                "problem": "Optimize delivery route for 5 locations",
                "constraints": ["minimize_distance", "time_windows"],
                "parameters": {"locations": 5, "vehicles": 2}
            },
            "requirements": ["reasoning", "planning"]
        }
        
        result = await engine.process_task(problem_task)
        print(f"   📊 Task Status: {result['status']}")
        print(f"   🎯 Optimization Score: {result.get('result', {}).get('optimization_score', 'N/A')}")
        
        # Example 4: Learning Task
        print("\n5. Processing Learning Task...")
        learning_task = {
            "id": "example_learning_task",
            "type": "learning_task",
            "data": {
                "training_data": [
                    ([1, 2], [3]),
                    ([2, 3], [5]),
                    ([3, 4], [7]),
                    ([4, 5], [9])
                ],
                "objective": "regression",
                "algorithm": "neural_network"
            },
            "requirements": ["learning", "training"]
        }
        
        result = await engine.process_task(learning_task)
        print(f"   📊 Task Status: {result['status']}")
        print(f"   🧠 Model Accuracy: {result.get('result', {}).get('accuracy', 'N/A')}")
        
        # Show agent performance
        print("\n6. Agent Performance Summary...")
        for agent_name, agent in engine.agents.items():
            print(f"   🤖 {agent_name}:")
            print(f"      Performance Score: {agent.performance_score:.2f}")
            print(f"      Success Rate: {agent.success_rate:.1%}")
            print(f"      Tasks Completed: {len(agent.task_history)}")
        
        # Trigger evolution
        print("\n7. Triggering System Evolution...")
        await engine.evolve()
        
        learning_status = engine.learning_system.get_status()
        print(f"   🧬 Learning Iterations: {learning_status['learning_iterations']}")
        print(f"   🔍 Patterns Discovered: {learning_status['patterns_discovered']}")
        print(f"   ⚙️  Strategies Optimized: {learning_status['strategies_optimized']}")
        
        # Final status
        print("\n8. Final System Status...")
        final_status = engine.get_status()
        print(f"   📈 Total Tasks Completed: {final_status['metrics']['tasks_completed']}")
        print(f"   🧠 Learning Iterations: {final_status['metrics']['learning_iterations']}")
        print(f"   ⏱️  System Uptime: {final_status['uptime_seconds']:.1f}s")
        
        print("\n✅ Example completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        # Cleanup
        await engine.shutdown()
        print("👋 OpenAGI Engine shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())