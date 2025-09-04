"""
Multi-agent collaboration example using OpenAGI.

This example demonstrates:
1. Creating specialized agents
2. Agent collaboration on complex tasks
3. Task orchestration and pipeline execution
4. Different agent types working together
"""

from openagi import OpenAGI
from openagi.agents.base import AgentTask
import time

def main():
    print("🤖 OpenAGI Multi-Agent Collaboration Example")
    
    # Initialize OpenAGI platform
    agi = OpenAGI()
    
    print("🏗️ Creating specialized agents...")
    
    # Create different types of agents
    try:
        # Conversational agent for text processing
        text_agent = agi.agents.create_agent(
            agent_type="conversational",
            name="TextProcessor",
            config={"model": "llama2-7b-chat"}
        )
        print(f"✅ Created text agent: {text_agent.name}")
        
        # Vision agent for image analysis
        vision_agent = agi.agents.create_agent(
            agent_type="vision", 
            name="ImageAnalyzer",
            config={"model": "resnet-50"}
        )
        print(f"✅ Created vision agent: {vision_agent.name}")
        
        # Multimodal agent for cross-modal tasks
        multimodal_agent = agi.agents.create_agent(
            agent_type="multimodal",
            name="MultimodalProcessor",
            config={"text_model": "llama2-7b", "vision_model": "clip-vit-base"}
        )
        print(f"✅ Created multimodal agent: {multimodal_agent.name}")
        
    except Exception as e:
        print(f"❌ Error creating agents: {e}")
        return
    
    print(f"\n📊 Platform stats: {agi.get_stats()}")
    
    # Demonstrate agent collaboration
    print("\n" + "="*60)
    print("MULTI-AGENT COLLABORATION SCENARIO")
    print("="*60)
    print("Task: Create a comprehensive report about AI trends")
    
    # Task 1: Research AI trends (Text Agent)
    print("\n🔹 Step 1: Research AI trends")
    research_task = AgentTask(
        description="Research current AI trends and developments",
        inputs={
            "prompt": "Provide a comprehensive overview of current AI trends in 2024, including LLMs, computer vision, and robotics"
        }
    )
    
    try:
        research_task_id = agi.agents.submit_task(research_task, text_agent.id)
        print(f"⏳ Submitted research task: {research_task_id}")
        
        # Wait for completion
        completed_research = agi.agents.wait_for_task(research_task_id, timeout=30)
        if completed_research:
            research_results = completed_research.outputs.get("response", "No results")
            print(f"✅ Research completed: {research_results[:200]}...")
        else:
            print("❌ Research task timed out")
            research_results = "Research incomplete"
            
    except Exception as e:
        print(f"❌ Research task failed: {e}")
        research_results = "Research failed"
    
    # Task 2: Analyze AI-related images (Vision Agent)
    print("\n🔹 Step 2: Analyze AI-related content")
    vision_task = AgentTask(
        description="Analyze AI-related visual content",
        inputs={
            "task_type": "classification",
            "image": "placeholder_image_data"  # In real scenario, provide actual image
        }
    )
    
    try:
        vision_task_id = agi.agents.submit_task(vision_task, vision_agent.id)
        print(f"⏳ Submitted vision task: {vision_task_id}")
        
        # Simulate completion (would actually process image)
        print("✅ Vision analysis completed (simulated)")
        vision_results = "Identified AI-related imagery: neural networks, robots, data visualizations"
        
    except Exception as e:
        print(f"❌ Vision task failed: {e}")
        vision_results = "Vision analysis failed"
    
    # Task 3: Create comprehensive report (Multimodal Agent)
    print("\n🔹 Step 3: Synthesize comprehensive report")
    synthesis_task = AgentTask(
        description="Synthesize research and visual analysis into comprehensive report",
        inputs={
            "task_type": "text_generation",
            "research_data": research_results,
            "vision_data": vision_results,
            "prompt": "Create a comprehensive report combining the research findings and visual analysis"
        }
    )
    
    try:
        synthesis_task_id = agi.agents.submit_task(synthesis_task, multimodal_agent.id)
        print(f"⏳ Submitted synthesis task: {synthesis_task_id}")
        
        completed_synthesis = agi.agents.wait_for_task(synthesis_task_id, timeout=30)
        if completed_synthesis:
            final_report = completed_synthesis.outputs.get("result", "No report generated")
            print(f"✅ Report synthesis completed")
        else:
            print("❌ Synthesis task timed out")
            final_report = "Report synthesis incomplete"
            
    except Exception as e:
        print(f"❌ Synthesis task failed: {e}")
        final_report = "Report synthesis failed"
    
    # Display final results
    print("\n" + "="*60)
    print("COLLABORATION RESULTS")
    print("="*60)
    print(f"📄 Final Report: {final_report[:300]}...")
    
    # Show agent statistics
    print("\n📊 Agent Performance:")
    for agent in [text_agent, vision_agent, multimodal_agent]:
        stats = agent.get_status()
        print(f"  {agent.name}:")
        print(f"    - Total tasks: {stats['total_tasks']}")
        print(f"    - Successful: {stats['successful_tasks']}")
        print(f"    - Failed: {stats['failed_tasks']}")
        print(f"    - Status: {stats['status']}")
    
    # Demonstrate pipeline execution
    print("\n" + "="*60)
    print("AUTOMATED PIPELINE EXECUTION")
    print("="*60)
    
    from openagi.agents.manager import AgentOrchestrator
    orchestrator = AgentOrchestrator(agi.agents)
    
    # Define a pipeline of tasks
    pipeline_tasks = [
        {
            "description": "Generate creative content ideas",
            "inputs": {"prompt": "Generate 3 creative AI application ideas"},
            "agent_type": "conversational"
        },
        {
            "description": "Analyze content feasibility", 
            "inputs": {"task_type": "classification"},
            "agent_type": "vision"
        },
        {
            "description": "Create final presentation",
            "inputs": {"task_type": "text_generation"},
            "agent_type": "multimodal"
        }
    ]
    
    try:
        print("⏳ Executing automated pipeline...")
        pipeline_results = orchestrator.execute_pipeline(pipeline_tasks)
        
        print("✅ Pipeline completed!")
        for i, result in enumerate(pipeline_results, 1):
            print(f"  Step {i}: {str(result)[:100]}...")
            
    except Exception as e:
        print(f"❌ Pipeline execution failed: {e}")
    
    print("\n✨ Multi-agent collaboration example completed!")
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    agi.shutdown()

if __name__ == "__main__":
    main()