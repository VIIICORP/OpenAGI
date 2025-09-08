"""
Self-Healing AI Module

This module implements advanced self-healing AI capabilities that can automatically
detect, diagnose, and recover from various types of issues and failures.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import json

from .config import ConfigManager
from .monitoring import HealthMonitor
from .recovery import RecoveryManager


class HealingStrategy(Enum):
    """Different strategies for self-healing."""
    RESTART = "restart"
    ROLLBACK = "rollback"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    RECONFIGURE = "reconfigure"
    FAILOVER = "failover"
    OPTIMIZE = "optimize"
    REPAIR = "repair"
    ISOLATE = "isolate"
    REINITIALIZE = "reinitialize"


@dataclass
class HealingAction:
    """Represents a self-healing action."""
    action_id: str
    strategy: HealingStrategy
    target: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    status: str = "pending"
    result: Optional[str] = None


@dataclass
class Issue:
    """Represents a detected issue."""
    issue_id: str
    issue_type: str
    severity: str
    description: str
    affected_components: List[str]
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    resolved: bool = False


class SelfHealingAI:
    """
    Advanced Self-Healing AI system with comprehensive recovery capabilities.
    
    This system can automatically detect issues, analyze their root causes,
    and apply appropriate healing strategies to restore system health.
    """
    
    def __init__(self, config_manager: ConfigManager, health_monitor: HealthMonitor, 
                 recovery_manager: RecoveryManager):
        """Initialize the Self-Healing AI system."""
        self.config_manager = config_manager
        self.health_monitor = health_monitor
        self.recovery_manager = recovery_manager
        self.logger = logging.getLogger(__name__)
        
        # Healing state
        self._running = False
        self._issues: Dict[str, Issue] = {}
        self._healing_actions: Dict[str, HealingAction] = {}
        self._healing_history: List[HealingAction] = []
        
        # Learning and adaptation
        self._success_patterns: Dict[str, List[HealingStrategy]] = {}
        self._failure_patterns: Dict[str, List[HealingStrategy]] = {}
        
        # Healing strategies registry
        self._strategies: Dict[HealingStrategy, Callable] = {
            HealingStrategy.RESTART: self._restart_strategy,
            HealingStrategy.ROLLBACK: self._rollback_strategy,
            HealingStrategy.SCALE_UP: self._scale_up_strategy,
            HealingStrategy.SCALE_DOWN: self._scale_down_strategy,
            HealingStrategy.RECONFIGURE: self._reconfigure_strategy,
            HealingStrategy.FAILOVER: self._failover_strategy,
            HealingStrategy.OPTIMIZE: self._optimize_strategy,
            HealingStrategy.REPAIR: self._repair_strategy,
            HealingStrategy.ISOLATE: self._isolate_strategy,
            HealingStrategy.REINITIALIZE: self._reinitialize_strategy,
        }
        
        self.logger.info("Self-Healing AI system initialized")
    
    async def start(self) -> None:
        """Start the self-healing AI system."""
        if self._running:
            return
        
        self._running = True
        
        # Start healing monitoring loop
        asyncio.create_task(self._healing_monitor())
        
        self.logger.info("Self-Healing AI system started")
    
    async def stop(self) -> None:
        """Stop the self-healing AI system."""
        self._running = False
        self.logger.info("Self-Healing AI system stopped")
    
    async def heal(self, issue_type: str, context: Dict[str, Any]) -> None:
        """
        Main healing method that analyzes issues and applies appropriate healing strategies.
        """
        issue_id = f"issue_{int(time.time() * 1000)}"
        
        # Create issue record
        issue = Issue(
            issue_id=issue_id,
            issue_type=issue_type,
            severity=self._assess_severity(issue_type, context),
            description=f"Detected issue: {issue_type}",
            affected_components=self._identify_affected_components(context),
            context=context
        )
        
        self._issues[issue_id] = issue
        self.logger.warning(f"Issue detected: {issue.description} (ID: {issue_id})")
        
        # Analyze and select healing strategy
        strategies = await self._analyze_and_select_strategies(issue)
        
        # Apply healing strategies
        for strategy in strategies:
            action = await self._apply_healing_strategy(issue, strategy)
            if action and action.status == "success":
                issue.resolved = True
                break
        
        # Learn from the healing attempt
        await self._learn_from_healing(issue, strategies)
    
    async def handle_feature_error(self, feature_name: str, error: Exception) -> None:
        """Handle errors in feature execution."""
        context = {
            "feature_name": feature_name,
            "error_type": type(error).__name__,
            "error_message": str(error)
        }
        await self.heal("feature_execution_error", context)
    
    async def _analyze_and_select_strategies(self, issue: Issue) -> List[HealingStrategy]:
        """Analyze the issue and select appropriate healing strategies."""
        strategies = []
        
        # Rule-based strategy selection
        if issue.issue_type == "agent_unhealthy":
            strategies = [HealingStrategy.RESTART, HealingStrategy.RECONFIGURE]
        elif issue.issue_type == "high_memory_usage":
            strategies = [HealingStrategy.OPTIMIZE, HealingStrategy.SCALE_UP]
        elif issue.issue_type == "high_cpu_usage":
            strategies = [HealingStrategy.OPTIMIZE, HealingStrategy.SCALE_UP]
        elif issue.issue_type == "network_error":
            strategies = [HealingStrategy.RESTART, HealingStrategy.FAILOVER]
        elif issue.issue_type == "feature_execution_error":
            strategies = [HealingStrategy.RESTART, HealingStrategy.ROLLBACK, HealingStrategy.REPAIR]
        elif issue.issue_type == "data_corruption":
            strategies = [HealingStrategy.ROLLBACK, HealingStrategy.REPAIR]
        elif issue.issue_type == "performance_degradation":
            strategies = [HealingStrategy.OPTIMIZE, HealingStrategy.SCALE_UP]
        else:
            # Default strategies for unknown issues
            strategies = [HealingStrategy.RESTART, HealingStrategy.RECONFIGURE]
        
        # Apply learning - prefer strategies that have worked before for similar issues
        if issue.issue_type in self._success_patterns:
            learned_strategies = self._success_patterns[issue.issue_type]
            # Prioritize learned successful strategies
            strategies = learned_strategies + [s for s in strategies if s not in learned_strategies]
        
        # Remove strategies that have consistently failed
        if issue.issue_type in self._failure_patterns:
            failed_strategies = self._failure_patterns[issue.issue_type]
            strategies = [s for s in strategies if s not in failed_strategies]
        
        self.logger.info(f"Selected healing strategies for {issue.issue_type}: {[s.value for s in strategies]}")
        return strategies
    
    async def _apply_healing_strategy(self, issue: Issue, strategy: HealingStrategy) -> Optional[HealingAction]:
        """Apply a specific healing strategy."""
        action_id = f"action_{int(time.time() * 1000)}"
        
        action = HealingAction(
            action_id=action_id,
            strategy=strategy,
            target=issue.issue_id,
            parameters=issue.context
        )
        
        self._healing_actions[action_id] = action
        
        try:
            self.logger.info(f"Applying healing strategy: {strategy.value} for issue {issue.issue_id}")
            
            # Execute the strategy
            strategy_handler = self._strategies[strategy]
            result = await strategy_handler(issue, action)
            
            action.status = "success" if result else "failed"
            action.result = "Healing strategy applied successfully" if result else "Healing strategy failed"
            
            self._healing_history.append(action)
            
            return action
            
        except Exception as e:
            action.status = "error"
            action.result = f"Error applying strategy: {str(e)}"
            self.logger.error(f"Error applying healing strategy {strategy.value}: {e}")
            return action
    
    async def _learn_from_healing(self, issue: Issue, strategies: List[HealingStrategy]) -> None:
        """Learn from healing attempts to improve future performance."""
        successful_strategies = []
        failed_strategies = []
        
        # Analyze which strategies worked
        for action in self._healing_history[-len(strategies):]:  # Get recent actions
            if action.target == issue.issue_id:
                if action.status == "success":
                    successful_strategies.append(action.strategy)
                else:
                    failed_strategies.append(action.strategy)
        
        # Update learning patterns
        if successful_strategies:
            if issue.issue_type not in self._success_patterns:
                self._success_patterns[issue.issue_type] = []
            self._success_patterns[issue.issue_type].extend(successful_strategies)
            
            # Keep only the most recent successful strategies (max 10)
            self._success_patterns[issue.issue_type] = self._success_patterns[issue.issue_type][-10:]
        
        if failed_strategies:
            if issue.issue_type not in self._failure_patterns:
                self._failure_patterns[issue.issue_type] = []
            self._failure_patterns[issue.issue_type].extend(failed_strategies)
            
            # Keep only the most recent failed strategies (max 10)
            self._failure_patterns[issue.issue_type] = self._failure_patterns[issue.issue_type][-10:]
        
        self.logger.info(f"Learning updated for issue type: {issue.issue_type}")
    
    def _assess_severity(self, issue_type: str, context: Dict[str, Any]) -> str:
        """Assess the severity of an issue."""
        # Critical issues
        if issue_type in ["system_failure", "data_corruption", "security_breach"]:
            return "critical"
        
        # High severity issues
        if issue_type in ["agent_failure", "network_partition", "storage_failure"]:
            return "high"
        
        # Medium severity issues
        if issue_type in ["agent_unhealthy", "high_memory_usage", "high_cpu_usage"]:
            return "medium"
        
        # Low severity issues
        return "low"
    
    def _identify_affected_components(self, context: Dict[str, Any]) -> List[str]:
        """Identify components affected by an issue."""
        components = []
        
        if "agent_id" in context:
            components.append(f"agent:{context['agent_id']}")
        
        if "feature_name" in context:
            components.append(f"feature:{context['feature_name']}")
        
        if "component" in context:
            components.append(context["component"])
        
        return components or ["system"]
    
    # Healing strategy implementations
    async def _restart_strategy(self, issue: Issue, action: HealingAction) -> bool:
        """Restart strategy implementation."""
        self.logger.info(f"Executing restart strategy for issue {issue.issue_id}")
        # Simulate restart operation
        await asyncio.sleep(1)
        return True
    
    async def _rollback_strategy(self, issue: Issue, action: HealingAction) -> bool:
        """Rollback strategy implementation."""
        self.logger.info(f"Executing rollback strategy for issue {issue.issue_id}")
        # Simulate rollback operation
        await asyncio.sleep(1)
        return True
    
    async def _scale_up_strategy(self, issue: Issue, action: HealingAction) -> bool:
        """Scale up strategy implementation."""
        self.logger.info(f"Executing scale up strategy for issue {issue.issue_id}")
        # Simulate scaling operation
        await asyncio.sleep(1)
        return True
    
    async def _scale_down_strategy(self, issue: Issue, action: HealingAction) -> bool:
        """Scale down strategy implementation."""
        self.logger.info(f"Executing scale down strategy for issue {issue.issue_id}")
        # Simulate scaling operation
        await asyncio.sleep(1)
        return True
    
    async def _reconfigure_strategy(self, issue: Issue, action: HealingAction) -> bool:
        """Reconfiguration strategy implementation."""
        self.logger.info(f"Executing reconfigure strategy for issue {issue.issue_id}")
        # Simulate reconfiguration
        await asyncio.sleep(1)
        return True
    
    async def _failover_strategy(self, issue: Issue, action: HealingAction) -> bool:
        """Failover strategy implementation."""
        self.logger.info(f"Executing failover strategy for issue {issue.issue_id}")
        # Simulate failover operation
        await asyncio.sleep(1)
        return True
    
    async def _optimize_strategy(self, issue: Issue, action: HealingAction) -> bool:
        """Optimization strategy implementation."""
        self.logger.info(f"Executing optimize strategy for issue {issue.issue_id}")
        # Simulate optimization
        await asyncio.sleep(1)
        return True
    
    async def _repair_strategy(self, issue: Issue, action: HealingAction) -> bool:
        """Repair strategy implementation."""
        self.logger.info(f"Executing repair strategy for issue {issue.issue_id}")
        # Simulate repair operation
        await asyncio.sleep(1)
        return True
    
    async def _isolate_strategy(self, issue: Issue, action: HealingAction) -> bool:
        """Isolation strategy implementation."""
        self.logger.info(f"Executing isolate strategy for issue {issue.issue_id}")
        # Simulate isolation
        await asyncio.sleep(1)
        return True
    
    async def _reinitialize_strategy(self, issue: Issue, action: HealingAction) -> bool:
        """Reinitialization strategy implementation."""
        self.logger.info(f"Executing reinitialize strategy for issue {issue.issue_id}")
        # Simulate reinitialization
        await asyncio.sleep(1)
        return True
    
    async def _healing_monitor(self) -> None:
        """Monitor healing effectiveness and trigger proactive healing."""
        while self._running:
            try:
                # Check for proactive healing opportunities
                await self._proactive_healing_check()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                self.logger.error(f"Healing monitor error: {e}")
                await asyncio.sleep(10)
    
    async def _proactive_healing_check(self) -> None:
        """Perform proactive healing checks."""
        # Check system metrics and trigger preemptive healing
        health_status = await self.health_monitor.get_health_status()
        
        # CPU usage check
        if health_status.get("cpu_usage", 0) > 80:
            await self.heal("high_cpu_usage", {"cpu_usage": health_status["cpu_usage"]})
        
        # Memory usage check
        if health_status.get("memory_usage", 0) > 85:
            await self.heal("high_memory_usage", {"memory_usage": health_status["memory_usage"]})
        
        # Disk usage check
        if health_status.get("disk_usage", 0) > 90:
            await self.heal("high_disk_usage", {"disk_usage": health_status["disk_usage"]})
    
    def get_healing_stats(self) -> Dict[str, Any]:
        """Get healing statistics."""
        total_actions = len(self._healing_history)
        successful_actions = sum(1 for action in self._healing_history if action.status == "success")
        
        return {
            "total_issues": len(self._issues),
            "resolved_issues": sum(1 for issue in self._issues.values() if issue.resolved),
            "total_healing_actions": total_actions,
            "successful_actions": successful_actions,
            "success_rate": (successful_actions / total_actions * 100) if total_actions > 0 else 0,
            "learned_patterns": len(self._success_patterns),
            "active_issues": sum(1 for issue in self._issues.values() if not issue.resolved)
        }