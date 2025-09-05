"""AI Agent implementation with self-learning capabilities."""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import json

from ..learning.self_learning import SelfLearningSystem


class AIAgent:
    """
    Intelligent AI agent with self-learning and adaptation capabilities.
    
    Each agent can handle specific types of tasks and continuously
    improves its performance through learning.
    """
    
    def __init__(self, name: str, capabilities: List[str], config: Dict[str, Any]):
        self.name = name
        self.capabilities = set(capabilities)
        self.config = config
        self.logger = logging.getLogger(f"openagi.agent.{name}")
        
        # Performance tracking
        self.performance_score = 1.0
        self.task_history: List[Dict[str, Any]] = []
        self.success_rate = 1.0
        
        # Learning components
        self.learning_system: Optional[SelfLearningSystem] = None
        self.knowledge_base: Dict[str, Any] = {}
        
        # State
        self.is_initialized = False
        self.is_busy = False
        
        self.logger.info(f"Agent '{name}' created with capabilities: {capabilities}")
    
    async def initialize(self, learning_system: SelfLearningSystem) -> None:
        """Initialize the agent with learning system."""
        self.learning_system = learning_system
        
        # Load previous knowledge if available
        await self._load_knowledge()
        
        # Initialize capabilities
        await self._initialize_capabilities()
        
        self.is_initialized = True
        self.logger.info(f"Agent '{self.name}' initialized")
    
    async def _load_knowledge(self) -> None:
        """Load previous knowledge and experiences."""
        # In a real implementation, this would load from persistent storage
        self.knowledge_base = {
            "experiences": [],
            "learned_patterns": {},
            "optimization_history": [],
            "capability_improvements": {}
        }
    
    async def _initialize_capabilities(self) -> None:
        """Initialize agent capabilities."""
        for capability in self.capabilities:
            await self._setup_capability(capability)
    
    async def _setup_capability(self, capability: str) -> None:
        """Setup a specific capability."""
        capability_configs = {
            "natural_language": {
                "model_type": "transformer",
                "max_tokens": 2048,
                "temperature": 0.7
            },
            "reasoning": {
                "logic_engine": "neural_symbolic",
                "max_depth": 10,
                "confidence_threshold": 0.8
            },
            "learning": {
                "algorithm": "gradient_descent",
                "learning_rate": 0.001,
                "batch_size": 32
            },
            "planning": {
                "horizon": 100,
                "exploration_rate": 0.1,
                "objective_weights": {"efficiency": 0.5, "accuracy": 0.5}
            },
            "general": {
                "adaptability": 0.8,
                "curiosity": 0.6,
                "creativity": 0.4
            }
        }
        
        config = capability_configs.get(capability, {})
        self.knowledge_base[f"capability_{capability}"] = config
        
        self.logger.debug(f"Capability '{capability}' configured")
    
    def can_handle_task(self, task_type: str, required_capabilities: List[str]) -> bool:
        """Check if agent can handle a specific task."""
        if not self.is_initialized:
            return False
        
        # Check if agent has required capabilities
        if required_capabilities:
            has_capabilities = all(cap in self.capabilities for cap in required_capabilities)
            if not has_capabilities:
                return False
        
        # Check task type compatibility
        compatible_types = {
            "text_processing": ["natural_language", "general"],
            "data_analysis": ["reasoning", "learning", "general"],
            "problem_solving": ["reasoning", "planning", "general"],
            "learning_task": ["learning", "general"],
            "general": ["general"]
        }
        
        agent_types = set()
        for cap in self.capabilities:
            agent_types.update(compatible_types.get(cap, []))
        
        return task_type in agent_types or "general" in self.capabilities
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task and return results."""
        if self.is_busy:
            raise RuntimeError(f"Agent '{self.name}' is currently busy")
        
        self.is_busy = True
        start_time = datetime.now()
        
        try:
            task_id = task.get("id", f"task_{start_time.timestamp()}")
            self.logger.info(f"Processing task {task_id}")
            
            # Analyze task
            task_analysis = await self._analyze_task(task)
            
            # Execute task
            result = await self._execute_task(task, task_analysis)
            
            # Learn from execution
            await self._learn_from_execution(task, result, task_analysis)
            
            # Update performance metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            await self._update_performance(task, result, execution_time)
            
            return {
                "status": "success",
                "result": result,
                "execution_time": execution_time,
                "agent": self.name,
                "confidence": task_analysis.get("confidence", 0.8)
            }
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {str(e)}")
            execution_time = (datetime.now() - start_time).total_seconds()
            await self._update_performance(task, None, execution_time, success=False)
            
            return {
                "status": "error",
                "error": str(e),
                "execution_time": execution_time,
                "agent": self.name
            }
        finally:
            self.is_busy = False
    
    async def _analyze_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze task to determine best approach."""
        task_type = task.get("type", "general")
        complexity = self._estimate_complexity(task)
        
        # Use learning system to predict best approach
        approach = "default"
        confidence = 0.8
        
        if self.learning_system:
            prediction = await self.learning_system.predict_approach(task, self.capabilities)
            approach = prediction.get("approach", approach)
            confidence = prediction.get("confidence", confidence)
        
        return {
            "type": task_type,
            "complexity": complexity,
            "approach": approach,
            "confidence": confidence,
            "estimated_time": complexity * 2.0  # seconds
        }
    
    def _estimate_complexity(self, task: Dict[str, Any]) -> float:
        """Estimate task complexity (0-1 scale)."""
        # Simple heuristic - in reality would be more sophisticated
        data_size = len(str(task.get("data", "")))
        requirements = len(task.get("requirements", []))
        
        complexity = min(1.0, (data_size / 1000 + requirements / 10) / 2)
        return complexity
    
    async def _execute_task(self, task: Dict[str, Any], analysis: Dict[str, Any]) -> Any:
        """Execute the actual task."""
        task_type = task.get("type", "general")
        data = task.get("data", {})
        
        # Simulate task execution based on type
        if task_type == "text_processing":
            return await self._process_text(data, analysis)
        elif task_type == "data_analysis":
            return await self._analyze_data(data, analysis)
        elif task_type == "problem_solving":
            return await self._solve_problem(data, analysis)
        elif task_type == "learning_task":
            return await self._learn_from_data(data, analysis)
        else:
            return await self._general_processing(data, analysis)
    
    async def _process_text(self, data: Any, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Process text-based tasks."""
        text = str(data.get("text", ""))
        operation = data.get("operation", "analyze")
        
        # Simulate text processing
        result = {
            "processed_text": text.upper() if operation == "uppercase" else text.lower(),
            "word_count": len(text.split()),
            "sentiment": "positive",  # Simulated
            "keywords": text.split()[:5],
            "confidence": analysis["confidence"]
        }
        
        return result
    
    async def _analyze_data(self, data: Any, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data and extract insights."""
        dataset = data.get("dataset", [])
        
        # Simulate data analysis
        result = {
            "sample_count": len(dataset),
            "features_detected": ["feature_1", "feature_2", "feature_3"],
            "patterns": ["pattern_a", "pattern_b"],
            "insights": ["insight_1", "insight_2"],
            "confidence": analysis["confidence"]
        }
        
        return result
    
    async def _solve_problem(self, data: Any, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Solve complex problems using reasoning."""
        problem = data.get("problem", "")
        constraints = data.get("constraints", [])
        
        # Simulate problem solving
        result = {
            "solution": f"Optimized solution for: {problem[:50]}...",
            "steps": ["step_1", "step_2", "step_3"],
            "satisfied_constraints": len(constraints),
            "optimization_score": 0.85,
            "confidence": analysis["confidence"]
        }
        
        return result
    
    async def _learn_from_data(self, data: Any, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Learn patterns from provided data."""
        training_data = data.get("training_data", [])
        learning_objective = data.get("objective", "classification")
        
        # Simulate learning
        result = {
            "model_trained": True,
            "accuracy": 0.92,
            "learning_objective": learning_objective,
            "training_samples": len(training_data),
            "patterns_learned": 15,
            "confidence": analysis["confidence"]
        }
        
        return result
    
    async def _general_processing(self, data: Any, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general-purpose tasks."""
        # Simulate general processing
        result = {
            "processed": True,
            "data_summary": str(data)[:100],
            "processing_approach": analysis["approach"],
            "confidence": analysis["confidence"]
        }
        
        return result
    
    async def _learn_from_execution(self, task: Dict[str, Any], result: Any, analysis: Dict[str, Any]) -> None:
        """Learn from task execution to improve future performance."""
        experience = {
            "task_type": task.get("type"),
            "complexity": analysis["complexity"],
            "approach": analysis["approach"],
            "success": result is not None,
            "timestamp": datetime.now().isoformat()
        }
        
        self.knowledge_base["experiences"].append(experience)
        
        # Learn with the learning system
        if self.learning_system:
            await self.learning_system.learn_from_experience(self.name, experience)
    
    async def _update_performance(self, task: Dict[str, Any], result: Any, 
                                execution_time: float, success: bool = True) -> None:
        """Update agent performance metrics."""
        # Record task in history
        task_record = {
            "task_id": task.get("id"),
            "type": task.get("type"),
            "success": success,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat()
        }
        
        self.task_history.append(task_record)
        
        # Update success rate
        recent_tasks = self.task_history[-100:]  # Last 100 tasks
        successes = sum(1 for t in recent_tasks if t["success"])
        self.success_rate = successes / len(recent_tasks) if recent_tasks else 1.0
        
        # Update performance score
        time_factor = max(0.1, 1.0 - (execution_time / 10.0))  # Penalize slow execution
        success_factor = 1.0 if success else 0.5
        
        self.performance_score = (self.performance_score * 0.9 + 
                                (self.success_rate * time_factor * success_factor) * 0.1)
    
    async def evolve(self) -> None:
        """Evolve and improve the agent based on experiences."""
        if not self.learning_system:
            return
        
        # Analyze performance trends
        if len(self.task_history) > 10:
            recent_performance = self._analyze_recent_performance()
            
            # Adapt based on performance
            if recent_performance["declining"]:
                await self._adapt_strategies()
            
            # Learn new capabilities if needed
            if recent_performance["capability_gaps"]:
                await self._expand_capabilities(recent_performance["capability_gaps"])
    
    def _analyze_recent_performance(self) -> Dict[str, Any]:
        """Analyze recent performance trends."""
        recent_tasks = self.task_history[-50:]
        
        # Check for declining performance
        first_half = recent_tasks[:25]
        second_half = recent_tasks[25:]
        
        first_success = sum(1 for t in first_half if t["success"]) / len(first_half) if first_half else 0
        second_success = sum(1 for t in second_half if t["success"]) / len(second_half) if second_half else 0
        
        declining = second_success < first_success - 0.1
        
        # Identify capability gaps (simplified)
        failed_types = [t["type"] for t in recent_tasks if not t["success"]]
        capability_gaps = list(set(failed_types))
        
        return {
            "declining": declining,
            "capability_gaps": capability_gaps,
            "recent_success_rate": second_success
        }
    
    async def _adapt_strategies(self) -> None:
        """Adapt agent strategies based on performance."""
        self.logger.info(f"Agent '{self.name}' adapting strategies due to performance decline")
        
        # Adjust confidence thresholds
        for capability in self.capabilities:
            config = self.knowledge_base.get(f"capability_{capability}", {})
            if "confidence_threshold" in config:
                config["confidence_threshold"] *= 0.95  # Lower threshold
    
    async def _expand_capabilities(self, needed_capabilities: List[str]) -> None:
        """Expand agent capabilities to handle new task types."""
        for capability in needed_capabilities:
            if capability not in self.capabilities:
                self.logger.info(f"Agent '{self.name}' learning new capability: {capability}")
                self.capabilities.add(capability)
                await self._setup_capability(capability)
    
    async def cleanup(self) -> None:
        """Cleanup agent resources."""
        # Save knowledge base
        await self._save_knowledge()
        self.logger.info(f"Agent '{self.name}' cleaned up")
    
    async def _save_knowledge(self) -> None:
        """Save agent knowledge and experiences."""
        # In a real implementation, this would save to persistent storage
        self.logger.debug(f"Knowledge saved for agent '{self.name}'")