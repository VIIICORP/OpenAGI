"""Self-learning system implementation."""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
import random
import math

from ..config.settings import Config


class SelfLearningSystem:
    """
    Core self-learning system that enables agents to improve over time.
    
    Features:
    - Pattern recognition and learning
    - Performance optimization
    - Adaptive strategy selection
    - Knowledge graph construction
    - Continuous improvement algorithms
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger("openagi.learning")
        
        # Learning state
        self.knowledge_graph: Dict[str, Any] = {}
        self.patterns: Dict[str, List[Dict[str, Any]]] = {}
        self.strategies: Dict[str, Dict[str, Any]] = {}
        self.performance_history: List[Dict[str, Any]] = []
        
        # Learning parameters
        self.learning_rate = config.get("learning.rate", 0.01)
        self.exploration_rate = config.get("learning.exploration_rate", 0.1)
        self.pattern_threshold = config.get("learning.pattern_threshold", 0.8)
        
        # Neural network components (simplified)
        self.neural_weights: Dict[str, List[float]] = {}
        self.hidden_layers = config.get("learning.hidden_layers", [64, 32])
        
        # Statistics
        self.learning_iterations = 0
        self.patterns_discovered = 0
        self.strategies_optimized = 0
        
        self.logger.info("Self-learning system initialized")
    
    async def initialize(self) -> None:
        """Initialize the learning system."""
        # Initialize neural network weights
        await self._initialize_neural_network()
        
        # Load existing knowledge if available
        await self._load_knowledge()
        
        # Initialize default strategies
        await self._initialize_strategies()
        
        self.logger.info("Self-learning system ready")
    
    async def _initialize_neural_network(self) -> None:
        """Initialize neural network components."""
        # Simple feedforward network initialization
        layer_sizes = [100] + self.hidden_layers + [50]  # Input -> Hidden -> Output
        
        for i in range(len(layer_sizes) - 1):
            layer_name = f"layer_{i}"
            input_size = layer_sizes[i]
            output_size = layer_sizes[i + 1]
            
            # Xavier initialization
            limit = math.sqrt(6.0 / (input_size + output_size))
            weights = [random.uniform(-limit, limit) for _ in range(input_size * output_size)]
            
            self.neural_weights[layer_name] = weights
    
    async def _load_knowledge(self) -> None:
        """Load existing knowledge from storage."""
        # In production, this would load from persistent storage
        self.knowledge_graph = {
            "concepts": {},
            "relationships": {},
            "learned_facts": {},
            "optimization_results": {}
        }
    
    async def _initialize_strategies(self) -> None:
        """Initialize default learning strategies."""
        self.strategies = {
            "gradient_descent": {
                "type": "optimization",
                "parameters": {"learning_rate": self.learning_rate, "momentum": 0.9},
                "success_rate": 0.8,
                "usage_count": 0
            },
            "reinforcement_learning": {
                "type": "adaptive",
                "parameters": {"epsilon": self.exploration_rate, "gamma": 0.95},
                "success_rate": 0.75,
                "usage_count": 0
            },
            "pattern_matching": {
                "type": "recognition",
                "parameters": {"threshold": self.pattern_threshold, "window_size": 10},
                "success_rate": 0.85,
                "usage_count": 0
            },
            "neural_adaptation": {
                "type": "neural",
                "parameters": {"adaptation_rate": 0.001, "regularization": 0.01},
                "success_rate": 0.9,
                "usage_count": 0
            }
        }
    
    async def learn_from_task(self, task: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Learn from a completed task."""
        learning_data = {
            "task_type": task.get("type", "unknown"),
            "task_complexity": self._estimate_complexity(task),
            "result_quality": self._evaluate_result_quality(result),
            "execution_time": result.get("execution_time", 0),
            "success": result.get("status") == "success",
            "timestamp": datetime.now()
        }
        
        # Update knowledge graph
        await self._update_knowledge_graph(task, result, learning_data)
        
        # Discover new patterns
        await self._discover_patterns(learning_data)
        
        # Optimize strategies
        await self._optimize_strategies(learning_data)
        
        # Update neural network
        await self._update_neural_network(learning_data)
        
        self.learning_iterations += 1
        self.logger.debug(f"Learned from task: {task.get('id', 'unknown')}")
    
    async def _update_knowledge_graph(self, task: Dict[str, Any], result: Dict[str, Any], 
                                    learning_data: Dict[str, Any]) -> None:
        """Update the knowledge graph with new information."""
        task_type = learning_data["task_type"]
        
        # Update concept knowledge
        if task_type not in self.knowledge_graph["concepts"]:
            self.knowledge_graph["concepts"][task_type] = {
                "instances": 0,
                "success_rate": 0.0,
                "avg_complexity": 0.0,
                "avg_execution_time": 0.0,
                "patterns": []
            }
        
        concept = self.knowledge_graph["concepts"][task_type]
        concept["instances"] += 1
        
        # Update running averages
        alpha = 1.0 / concept["instances"]  # Learning rate decreases with more samples
        concept["success_rate"] = (1 - alpha) * concept["success_rate"] + alpha * (1 if learning_data["success"] else 0)
        concept["avg_complexity"] = (1 - alpha) * concept["avg_complexity"] + alpha * learning_data["task_complexity"]
        concept["avg_execution_time"] = (1 - alpha) * concept["avg_execution_time"] + alpha * learning_data["execution_time"]
        
        # Update relationships
        agent_name = result.get("agent", "unknown")
        relationship_key = f"{task_type}_{agent_name}"
        
        if relationship_key not in self.knowledge_graph["relationships"]:
            self.knowledge_graph["relationships"][relationship_key] = {
                "strength": 0.5,
                "interactions": 0,
                "success_rate": 0.0
            }
        
        rel = self.knowledge_graph["relationships"][relationship_key]
        rel["interactions"] += 1
        rel["success_rate"] = ((rel["success_rate"] * (rel["interactions"] - 1)) + 
                              (1 if learning_data["success"] else 0)) / rel["interactions"]
        rel["strength"] = min(1.0, rel["strength"] + (0.1 if learning_data["success"] else -0.05))
    
    async def _discover_patterns(self, learning_data: Dict[str, Any]) -> None:
        """Discover new patterns in the learning data."""
        task_type = learning_data["task_type"]
        
        if task_type not in self.patterns:
            self.patterns[task_type] = []
        
        # Add current data point
        pattern_data = {
            "complexity": learning_data["task_complexity"],
            "execution_time": learning_data["execution_time"],
            "success": learning_data["success"],
            "quality": learning_data["result_quality"],
            "timestamp": learning_data["timestamp"].isoformat()
        }
        
        self.patterns[task_type].append(pattern_data)
        
        # Keep only recent patterns (sliding window)
        max_patterns = self.config.get("learning.max_patterns", 1000)
        if len(self.patterns[task_type]) > max_patterns:
            self.patterns[task_type] = self.patterns[task_type][-max_patterns:]
        
        # Analyze for new patterns
        if len(self.patterns[task_type]) >= 10:
            await self._analyze_patterns(task_type)
    
    async def _analyze_patterns(self, task_type: str) -> None:
        """Analyze patterns to discover insights."""
        patterns = self.patterns[task_type]
        
        # Simple correlation analysis
        complexities = [p["complexity"] for p in patterns[-50:]]
        execution_times = [p["execution_time"] for p in patterns[-50:]]
        successes = [1 if p["success"] else 0 for p in patterns[-50:]]
        
        if len(complexities) >= 10:
            # Check complexity-time correlation
            correlation = self._calculate_correlation(complexities, execution_times)
            if abs(correlation) > 0.7:
                insight = {
                    "type": "complexity_time_correlation",
                    "correlation": correlation,
                    "confidence": abs(correlation),
                    "discovered_at": datetime.now().isoformat()
                }
                
                concept = self.knowledge_graph["concepts"].get(task_type, {})
                if "insights" not in concept:
                    concept["insights"] = []
                concept["insights"].append(insight)
                
                self.patterns_discovered += 1
                self.logger.info(f"Discovered pattern for {task_type}: complexity-time correlation = {correlation:.3f}")
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi * xi for xi in x)
        sum_y2 = sum(yi * yi for yi in y)
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = math.sqrt((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y))
        
        return numerator / denominator if denominator != 0 else 0.0
    
    async def _optimize_strategies(self, learning_data: Dict[str, Any]) -> None:
        """Optimize learning strategies based on performance."""
        success = learning_data["success"]
        quality = learning_data["result_quality"]
        
        # Update strategy performance
        for strategy_name, strategy in self.strategies.items():
            # Simplified strategy update - in reality would be more sophisticated
            if strategy["usage_count"] > 0:
                alpha = 0.1  # Learning rate for strategy optimization
                new_success_rate = (1 - alpha) * strategy["success_rate"] + alpha * (1 if success else 0)
                strategy["success_rate"] = new_success_rate
                
                # Adapt parameters based on performance
                if new_success_rate > 0.9:
                    # Strategy is working well, be more aggressive
                    await self._increase_strategy_aggressiveness(strategy)
                elif new_success_rate < 0.6:
                    # Strategy needs improvement, be more conservative
                    await self._decrease_strategy_aggressiveness(strategy)
        
        self.strategies_optimized += 1
    
    async def _increase_strategy_aggressiveness(self, strategy: Dict[str, Any]) -> None:
        """Make strategy more aggressive when performing well."""
        params = strategy["parameters"]
        
        if "learning_rate" in params:
            params["learning_rate"] = min(0.1, params["learning_rate"] * 1.1)
        if "epsilon" in params:
            params["epsilon"] = max(0.01, params["epsilon"] * 0.95)
    
    async def _decrease_strategy_aggressiveness(self, strategy: Dict[str, Any]) -> None:
        """Make strategy more conservative when underperforming."""
        params = strategy["parameters"]
        
        if "learning_rate" in params:
            params["learning_rate"] = max(0.001, params["learning_rate"] * 0.9)
        if "epsilon" in params:
            params["epsilon"] = min(0.3, params["epsilon"] * 1.05)
    
    async def _update_neural_network(self, learning_data: Dict[str, Any]) -> None:
        """Update neural network weights based on learning data."""
        # Simplified neural network update
        # In practice, this would implement proper backpropagation
        
        # Create input vector from learning data
        input_vector = self._create_input_vector(learning_data)
        
        # Create target vector
        target = 1.0 if learning_data["success"] else 0.0
        
        # Simple weight update (gradient descent approximation)
        for layer_name, weights in self.neural_weights.items():
            for i in range(len(weights)):
                # Simplified update rule
                gradient = (target - 0.5) * input_vector[i % len(input_vector)]
                weights[i] += self.learning_rate * gradient
    
    def _create_input_vector(self, learning_data: Dict[str, Any]) -> List[float]:
        """Create input vector from learning data."""
        # Normalize and vectorize learning data
        vector = [
            learning_data["task_complexity"],
            learning_data["result_quality"],
            learning_data["execution_time"] / 10.0,  # Normalize time
            1.0 if learning_data["success"] else 0.0
        ]
        
        # Pad to match expected input size
        while len(vector) < 100:
            vector.append(0.0)
        
        return vector[:100]  # Truncate if too long
    
    def _estimate_complexity(self, task: Dict[str, Any]) -> float:
        """Estimate task complexity."""
        # Simple heuristic - in practice would be more sophisticated
        data_size = len(str(task.get("data", "")))
        requirements = len(task.get("requirements", []))
        
        complexity = min(1.0, (data_size / 1000 + requirements / 10) / 2)
        return complexity
    
    def _evaluate_result_quality(self, result: Dict[str, Any]) -> float:
        """Evaluate the quality of a result."""
        if result.get("status") != "success":
            return 0.0
        
        # Simple quality metric based on confidence and completeness
        confidence = result.get("confidence", 0.5)
        
        # Check for result completeness
        result_data = result.get("result", {})
        completeness = 1.0 if result_data else 0.5
        
        return (confidence + completeness) / 2
    
    async def predict_approach(self, task: Dict[str, Any], agent_capabilities: set) -> Dict[str, Any]:
        """Predict the best approach for a task."""
        task_type = task.get("type", "general")
        complexity = self._estimate_complexity(task)
        
        # Use knowledge graph to predict
        if task_type in self.knowledge_graph["concepts"]:
            concept = self.knowledge_graph["concepts"][task_type]
            
            # Find best strategy based on historical performance
            best_strategy = max(self.strategies.items(), 
                              key=lambda x: x[1]["success_rate"])
            
            confidence = concept["success_rate"] * best_strategy[1]["success_rate"]
            
            return {
                "approach": best_strategy[0],
                "confidence": confidence,
                "estimated_time": concept["avg_execution_time"] * (1 + complexity)
            }
        
        # Default prediction for unknown task types
        return {
            "approach": "neural_adaptation",
            "confidence": 0.6,
            "estimated_time": 5.0
        }
    
    async def learn_from_experience(self, agent_name: str, experience: Dict[str, Any]) -> None:
        """Learn from an agent's experience."""
        # Update agent-specific knowledge
        agent_key = f"agent_{agent_name}"
        
        if agent_key not in self.knowledge_graph["learned_facts"]:
            self.knowledge_graph["learned_facts"][agent_key] = {
                "experiences": [],
                "performance_trend": [],
                "specializations": []
            }
        
        agent_facts = self.knowledge_graph["learned_facts"][agent_key]
        agent_facts["experiences"].append(experience)
        
        # Keep only recent experiences
        if len(agent_facts["experiences"]) > 100:
            agent_facts["experiences"] = agent_facts["experiences"][-100:]
        
        # Analyze agent specializations
        await self._analyze_agent_specializations(agent_name, agent_facts)
    
    async def _analyze_agent_specializations(self, agent_name: str, agent_facts: Dict[str, Any]) -> None:
        """Analyze what tasks an agent specializes in."""
        experiences = agent_facts["experiences"]
        
        if len(experiences) < 10:
            return
        
        # Count task types and success rates
        task_performance = {}
        for exp in experiences[-50:]:  # Recent experiences
            task_type = exp["task_type"]
            if task_type not in task_performance:
                task_performance[task_type] = {"total": 0, "successes": 0}
            
            task_performance[task_type]["total"] += 1
            if exp["success"]:
                task_performance[task_type]["successes"] += 1
        
        # Identify specializations (tasks with >80% success rate and >5 instances)
        specializations = []
        for task_type, perf in task_performance.items():
            success_rate = perf["successes"] / perf["total"]
            if success_rate > 0.8 and perf["total"] >= 5:
                specializations.append({
                    "task_type": task_type,
                    "success_rate": success_rate,
                    "experience_count": perf["total"]
                })
        
        agent_facts["specializations"] = specializations
        
        if specializations:
            self.logger.info(f"Agent {agent_name} specializes in: {[s['task_type'] for s in specializations]}")
    
    async def evolve(self) -> None:
        """Trigger evolution cycle for the learning system."""
        self.logger.info("Starting learning system evolution...")
        
        # Evolve strategies
        await self._evolve_strategies()
        
        # Optimize neural network architecture
        await self._optimize_network_architecture()
        
        # Consolidate knowledge
        await self._consolidate_knowledge()
        
        # Cleanup old data
        await self._cleanup_old_data()
        
        self.logger.info(f"Evolution complete. Iteration: {self.learning_iterations}")
    
    async def _evolve_strategies(self) -> None:
        """Evolve learning strategies based on performance."""
        # Remove underperforming strategies
        strategies_to_remove = []
        for name, strategy in self.strategies.items():
            if strategy["usage_count"] > 100 and strategy["success_rate"] < 0.3:
                strategies_to_remove.append(name)
        
        for name in strategies_to_remove:
            del self.strategies[name]
            self.logger.info(f"Removed underperforming strategy: {name}")
        
        # Create new strategies by combining successful ones
        if len(self.strategies) >= 2:
            await self._create_hybrid_strategies()
    
    async def _create_hybrid_strategies(self) -> None:
        """Create new strategies by combining successful existing ones."""
        # Find top 2 performing strategies
        top_strategies = sorted(self.strategies.items(), 
                              key=lambda x: x[1]["success_rate"], 
                              reverse=True)[:2]
        
        if len(top_strategies) == 2:
            strategy1, strategy2 = top_strategies
            
            # Create hybrid strategy
            hybrid_name = f"hybrid_{strategy1[0]}_{strategy2[0]}"
            if hybrid_name not in self.strategies:
                hybrid_params = {}
                
                # Combine parameters
                for key in strategy1[1]["parameters"]:
                    if key in strategy2[1]["parameters"]:
                        hybrid_params[key] = (strategy1[1]["parameters"][key] + 
                                            strategy2[1]["parameters"][key]) / 2
                    else:
                        hybrid_params[key] = strategy1[1]["parameters"][key]
                
                self.strategies[hybrid_name] = {
                    "type": "hybrid",
                    "parameters": hybrid_params,
                    "success_rate": (strategy1[1]["success_rate"] + strategy2[1]["success_rate"]) / 2,
                    "usage_count": 0,
                    "parent_strategies": [strategy1[0], strategy2[0]]
                }
                
                self.logger.info(f"Created hybrid strategy: {hybrid_name}")
    
    async def _optimize_network_architecture(self) -> None:
        """Optimize neural network architecture."""
        # Simple architecture optimization
        if self.learning_iterations % 100 == 0:
            # Occasionally adjust hidden layer sizes based on performance
            current_performance = sum(s["success_rate"] for s in self.strategies.values()) / len(self.strategies)
            
            if current_performance < 0.7:
                # Increase network capacity
                self.hidden_layers = [min(128, layer + 8) for layer in self.hidden_layers]
                await self._initialize_neural_network()
                self.logger.info(f"Increased network capacity: {self.hidden_layers}")
    
    async def _consolidate_knowledge(self) -> None:
        """Consolidate and compress learned knowledge."""
        # Remove redundant patterns
        for task_type, patterns in self.patterns.items():
            if len(patterns) > 500:
                # Keep most recent and most informative patterns
                sorted_patterns = sorted(patterns, 
                                       key=lambda p: p["timestamp"], 
                                       reverse=True)
                self.patterns[task_type] = sorted_patterns[:500]
    
    async def _cleanup_old_data(self) -> None:
        """Clean up old, irrelevant data."""
        # Remove old performance history
        cutoff_time = datetime.now().timestamp() - (30 * 24 * 3600)  # 30 days
        
        self.performance_history = [
            h for h in self.performance_history 
            if h.get("timestamp", 0) > cutoff_time
        ]
    
    def get_status(self) -> Dict[str, Any]:
        """Get current learning system status."""
        return {
            "learning_iterations": self.learning_iterations,
            "patterns_discovered": self.patterns_discovered,
            "strategies_optimized": self.strategies_optimized,
            "active_strategies": len(self.strategies),
            "knowledge_concepts": len(self.knowledge_graph.get("concepts", {})),
            "total_patterns": sum(len(patterns) for patterns in self.patterns.values()),
            "neural_layers": len(self.neural_weights),
            "learning_rate": self.learning_rate,
            "exploration_rate": self.exploration_rate
        }
    
    async def save_state(self) -> None:
        """Save learning system state."""
        # In production, this would save to persistent storage
        state = {
            "knowledge_graph": self.knowledge_graph,
            "patterns": {k: v[-100:] for k, v in self.patterns.items()},  # Keep recent patterns
            "strategies": self.strategies,
            "neural_weights": self.neural_weights,
            "learning_iterations": self.learning_iterations,
            "patterns_discovered": self.patterns_discovered,
            "strategies_optimized": self.strategies_optimized
        }
        
        self.logger.info("Learning system state saved")