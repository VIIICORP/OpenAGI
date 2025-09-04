"""Agent manager for coordinating multiple agents."""

import logging
import threading
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, Future
from queue import Queue, Empty
import time

from .base import Agent, AgentTask, AgentStatus, ConversationalAgent, VisionAgent, MultimodalAgent

logger = logging.getLogger(__name__)


class AgentManager:
    """
    Manages and coordinates multiple AI agents in the OpenAGI platform.
    
    Provides:
    - Agent registration and discovery
    - Task distribution and load balancing
    - Agent collaboration and communication
    - Resource management
    """
    
    def __init__(self, config, model_registry):
        """
        Initialize the agent manager.
        
        Args:
            config: Configuration object
            model_registry: Model registry for agent access
        """
        self.config = config
        self.model_registry = model_registry
        
        self.agents: Dict[str, Agent] = {}
        self.task_queue = Queue()
        self.executor = ThreadPoolExecutor(
            max_workers=config.get("openagi.agents.max_concurrent", 10)
        )
        self.running_tasks: Dict[str, Future] = {}
        
        self._shutdown = False
        self._monitor_thread = None
        
        # Start monitoring thread
        self._start_monitoring()
        
        logger.info("Agent manager initialized")
        
    def register_agent(self, agent: Agent) -> str:
        """
        Register an agent with the manager.
        
        Args:
            agent: Agent instance to register
            
        Returns:
            Agent ID
        """
        self.agents[agent.id] = agent
        logger.info(f"Registered agent: {agent.name} ({agent.id})")
        return agent.id
        
    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent.
        
        Args:
            agent_id: ID of agent to unregister
            
        Returns:
            True if agent was found and removed
        """
        if agent_id in self.agents:
            agent = self.agents.pop(agent_id)
            logger.info(f"Unregistered agent: {agent.name} ({agent_id})")
            return True
        return False
        
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by ID."""
        return self.agents.get(agent_id)
        
    def list_agents(self, status: Optional[AgentStatus] = None) -> List[Agent]:
        """
        List agents, optionally filtered by status.
        
        Args:
            status: Optional status filter
            
        Returns:
            List of matching agents
        """
        agents = list(self.agents.values())
        if status:
            agents = [a for a in agents if a.status == status]
        return agents
        
    def find_agents_by_capability(self, capability: str) -> List[Agent]:
        """
        Find agents that have a specific capability.
        
        Args:
            capability: Capability name to search for
            
        Returns:
            List of agents with the capability
        """
        return [
            agent for agent in self.agents.values()
            if agent.has_capability(capability)
        ]
        
    def create_agent(self, agent_type: str, name: str = None, config: Dict[str, Any] = None) -> Agent:
        """
        Create and register a new agent.
        
        Args:
            agent_type: Type of agent to create
            name: Optional agent name
            config: Optional agent configuration
            
        Returns:
            Created agent instance
        """
        if agent_type == "conversational":
            agent = ConversationalAgent(
                model_registry=self.model_registry,
                name=name,
                config=config
            )
        elif agent_type == "vision":
            agent = VisionAgent(
                model_registry=self.model_registry,
                name=name,
                config=config
            )
        elif agent_type == "multimodal":
            agent = MultimodalAgent(
                model_registry=self.model_registry,
                name=name,
                config=config
            )
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
            
        self.register_agent(agent)
        return agent
        
    def submit_task(self, task: AgentTask, agent_id: Optional[str] = None) -> str:
        """
        Submit a task for execution.
        
        Args:
            task: Task to execute
            agent_id: Optional specific agent to use
            
        Returns:
            Task ID
        """
        if agent_id:
            agent = self.get_agent(agent_id)
            if not agent:
                raise ValueError(f"Agent {agent_id} not found")
            if agent.status != AgentStatus.IDLE:
                raise ValueError(f"Agent {agent_id} is not idle")
        else:
            agent = self._find_best_agent(task)
            if not agent:
                raise ValueError("No suitable agent available")
                
        # Submit task for execution
        future = self.executor.submit(self._execute_task, agent, task)
        self.running_tasks[task.id] = future
        
        logger.info(f"Submitted task {task.id} to agent {agent.name}")
        return task.id
        
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a running task.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task status information
        """
        if task_id in self.running_tasks:
            future = self.running_tasks[task_id]
            
            if future.done():
                try:
                    task = future.result()
                    return {
                        "id": task.id,
                        "status": task.status.value,
                        "outputs": task.outputs,
                        "error": task.error
                    }
                except Exception as e:
                    return {
                        "id": task_id,
                        "status": "failed",
                        "error": str(e)
                    }
            else:
                return {
                    "id": task_id,
                    "status": "running"
                }
                
        return None
        
    def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> Optional[AgentTask]:
        """
        Wait for a task to complete.
        
        Args:
            task_id: Task ID
            timeout: Optional timeout in seconds
            
        Returns:
            Completed task or None if timeout
        """
        if task_id in self.running_tasks:
            future = self.running_tasks[task_id]
            try:
                return future.result(timeout=timeout)
            except Exception as e:
                logger.error(f"Error waiting for task {task_id}: {e}")
                return None
                
        return None
        
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a running task.
        
        Args:
            task_id: Task ID
            
        Returns:
            True if task was cancelled
        """
        if task_id in self.running_tasks:
            future = self.running_tasks[task_id]
            return future.cancel()
        return False
        
    def _find_best_agent(self, task: AgentTask) -> Optional[Agent]:
        """Find the best agent for a task."""
        # Simple strategy: find idle agent with required capability
        task_type = task.metadata.get("task_type", "general")
        
        for agent in self.agents.values():
            if agent.status == AgentStatus.IDLE:
                if task_type == "general" or agent.has_capability(task_type):
                    return agent
                    
        return None
        
    def _execute_task(self, agent: Agent, task: AgentTask) -> AgentTask:
        """Execute a task on an agent."""
        try:
            return agent.execute_task(task)
        finally:
            # Clean up completed task
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]
                
    def _start_monitoring(self):
        """Start the monitoring thread."""
        self._monitor_thread = threading.Thread(target=self._monitor_agents)
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
        
    def _monitor_agents(self):
        """Monitor agent health and performance."""
        while not self._shutdown:
            try:
                # Check agent health
                for agent in list(self.agents.values()):
                    if agent.status == AgentStatus.RUNNING:
                        # Check for stuck tasks
                        if agent.current_task:
                            task_duration = (
                                time.time() - agent.current_task.started_at.timestamp()
                                if agent.current_task.started_at else 0
                            )
                            max_duration = self.config.get("openagi.agents.default_timeout", 600)
                            
                            if task_duration > max_duration:
                                logger.warning(
                                    f"Agent {agent.name} has been running task "
                                    f"{agent.current_task.id} for {task_duration:.0f}s"
                                )
                                
                # Clean up completed tasks
                completed_tasks = [
                    task_id for task_id, future in self.running_tasks.items()
                    if future.done()
                ]
                for task_id in completed_tasks:
                    del self.running_tasks[task_id]
                    
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in agent monitoring: {e}")
                time.sleep(5)
                
    def get_stats(self) -> Dict[str, Any]:
        """Get agent manager statistics."""
        agent_stats = {}
        for status in AgentStatus:
            agent_stats[status.value] = len([
                a for a in self.agents.values() if a.status == status
            ])
            
        return {
            "total_agents": len(self.agents),
            "agent_status": agent_stats,
            "running_tasks": len(self.running_tasks),
            "agent_types": self._get_agent_type_counts()
        }
        
    def _get_agent_type_counts(self) -> Dict[str, int]:
        """Get counts of different agent types."""
        type_counts = {}
        for agent in self.agents.values():
            agent_type = agent.__class__.__name__
            type_counts[agent_type] = type_counts.get(agent_type, 0) + 1
        return type_counts
        
    def count_active(self) -> int:
        """Count active agents."""
        return len([a for a in self.agents.values() if a.status == AgentStatus.RUNNING])
        
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on agent manager."""
        healthy_agents = 0
        total_agents = len(self.agents)
        
        for agent in self.agents.values():
            if agent.status in [AgentStatus.IDLE, AgentStatus.RUNNING]:
                healthy_agents += 1
                
        return {
            "status": "healthy" if healthy_agents == total_agents else "degraded",
            "healthy_agents": healthy_agents,
            "total_agents": total_agents,
            "running_tasks": len(self.running_tasks)
        }
        
    def shutdown_all(self):
        """Shutdown all agents and the manager."""
        logger.info("Shutting down agent manager")
        
        # Stop monitoring
        self._shutdown = True
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
            
        # Cancel running tasks
        for task_id, future in list(self.running_tasks.items()):
            future.cancel()
            
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        # Clear agents
        self.agents.clear()
        
        logger.info("Agent manager shutdown complete")


class AgentOrchestrator:
    """
    High-level orchestrator for complex multi-agent workflows.
    
    Coordinates multiple agents to solve complex tasks that require
    different capabilities or collaboration.
    """
    
    def __init__(self, agent_manager: AgentManager):
        """Initialize the orchestrator."""
        self.agent_manager = agent_manager
        
    def create_workflow(self, workflow_config: Dict[str, Any]) -> str:
        """
        Create a multi-agent workflow.
        
        Args:
            workflow_config: Workflow configuration
            
        Returns:
            Workflow ID
        """
        # Implementation for complex workflows
        pass
        
    def execute_pipeline(self, tasks: List[Dict[str, Any]]) -> List[Any]:
        """
        Execute a pipeline of tasks across multiple agents.
        
        Args:
            tasks: List of task configurations
            
        Returns:
            List of results
        """
        results = []
        
        for task_config in tasks:
            task = AgentTask(
                description=task_config.get("description", ""),
                inputs=task_config.get("inputs", {}),
                metadata=task_config.get("metadata", {})
            )
            
            agent_type = task_config.get("agent_type")
            if agent_type:
                agents = [a for a in self.agent_manager.agents.values() 
                         if a.__class__.__name__.lower().startswith(agent_type.lower())]
                if agents:
                    agent = agents[0]  # Use first available
                    task_id = self.agent_manager.submit_task(task, agent.id)
                    completed_task = self.agent_manager.wait_for_task(task_id)
                    if completed_task:
                        results.append(completed_task.outputs)
                    else:
                        results.append({"error": "Task failed"})
                else:
                    results.append({"error": f"No {agent_type} agent available"})
            else:
                task_id = self.agent_manager.submit_task(task)
                completed_task = self.agent_manager.wait_for_task(task_id)
                if completed_task:
                    results.append(completed_task.outputs)
                else:
                    results.append({"error": "Task failed"})
                    
        return results