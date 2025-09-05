"""
Recovery Manager Module

This module handles recovery operations, backup management, and restoration
of the OpenAGI platform in case of failures or issues.
"""

import asyncio
import logging
import time
import json
import os
import shutil
import pickle
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path
import zipfile
from datetime import datetime, timedelta

from .config import ConfigManager


@dataclass
class BackupInfo:
    """Information about a backup."""
    backup_id: str
    timestamp: float
    backup_type: str  # full, incremental, configuration
    size_bytes: int
    file_path: str
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryPoint:
    """Represents a recovery point."""
    point_id: str
    timestamp: float
    state: Dict[str, Any]
    components: List[str]
    checksum: str
    description: str


class RecoveryManager:
    """
    Comprehensive recovery management system for the OpenAGI platform.
    
    Handles backup creation, restoration, rollback operations, and maintains
    recovery points for the entire platform state.
    """
    
    def __init__(self, config_manager: ConfigManager):
        """Initialize the recovery manager."""
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        # Recovery configuration
        self.backup_dir = Path(self.config_manager.get("recovery.backup_dir", "./backups"))
        self.max_backups = self.config_manager.get("recovery.max_backups", 50)
        self.backup_interval = self.config_manager.get("recovery.backup_interval", 3600)  # 1 hour
        self.auto_backup_enabled = self.config_manager.get("recovery.auto_backup", True)
        
        # Recovery state
        self._running = False
        self._backups: Dict[str, BackupInfo] = {}
        self._recovery_points: Dict[str, RecoveryPoint] = {}
        self._recovery_operations: List[Dict[str, Any]] = []
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Recovery strategies
        self._recovery_strategies: Dict[str, Callable] = {
            "restart_component": self._restart_component,
            "restore_backup": self._restore_backup,
            "rollback_config": self._rollback_config,
            "reset_to_defaults": self._reset_to_defaults,
            "partial_restore": self._partial_restore,
            "emergency_recovery": self._emergency_recovery,
        }
        
        self.logger.info("Recovery manager initialized")
    
    async def start(self) -> None:
        """Start the recovery manager."""
        if self._running:
            return
        
        self._running = True
        
        # Load existing backups
        await self._load_backup_index()
        
        # Start automatic backup if enabled
        if self.auto_backup_enabled:
            asyncio.create_task(self._auto_backup_loop())
        
        # Start recovery monitoring
        asyncio.create_task(self._recovery_monitor())
        
        self.logger.info("Recovery manager started")
    
    async def stop(self) -> None:
        """Stop the recovery manager."""
        self._running = False
        
        # Save backup index
        await self._save_backup_index()
        
        self.logger.info("Recovery manager stopped")
    
    async def create_backup(self, backup_type: str = "full", description: str = "") -> str:
        """Create a backup of the platform state."""
        backup_id = f"backup_{int(time.time() * 1000)}"
        timestamp = time.time()
        
        try:
            # Create backup directory
            backup_path = self.backup_dir / backup_id
            backup_path.mkdir(exist_ok=True)
            
            # Collect platform state
            platform_state = await self._collect_platform_state()
            
            # Save state to backup
            state_file = backup_path / "platform_state.json"
            with open(state_file, 'w') as f:
                json.dump(platform_state, f, indent=2)
            
            # Backup configuration
            config_state = self.config_manager.export_config()
            config_file = backup_path / "config.json"
            with open(config_file, 'w') as f:
                json.dump(config_state, f, indent=2)
            
            # Create backup archive
            archive_path = self.backup_dir / f"{backup_id}.zip"
            await self._create_backup_archive(backup_path, archive_path)
            
            # Calculate size
            size_bytes = archive_path.stat().st_size
            
            # Create backup info
            backup_info = BackupInfo(
                backup_id=backup_id,
                timestamp=timestamp,
                backup_type=backup_type,
                size_bytes=size_bytes,
                file_path=str(archive_path),
                description=description or f"{backup_type.title()} backup",
                metadata={
                    "platform_version": "1.0.0",
                    "components": list(platform_state.keys()),
                    "agent_count": len(platform_state.get("agents", {}))
                }
            )
            
            self._backups[backup_id] = backup_info
            
            # Cleanup old backups
            await self._cleanup_old_backups()
            
            # Remove temporary directory
            shutil.rmtree(backup_path)
            
            self.logger.info(f"Backup created: {backup_id} ({size_bytes} bytes)")
            return backup_id
            
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
            raise
    
    async def restore_backup(self, backup_id: str, components: Optional[List[str]] = None) -> bool:
        """Restore from a backup."""
        if backup_id not in self._backups:
            raise ValueError(f"Backup not found: {backup_id}")
        
        backup_info = self._backups[backup_id]
        
        try:
            # Record recovery operation
            operation_id = f"restore_{int(time.time() * 1000)}"
            self._recovery_operations.append({
                "operation_id": operation_id,
                "type": "restore",
                "backup_id": backup_id,
                "components": components,
                "timestamp": time.time(),
                "status": "started"
            })
            
            # Extract backup
            backup_dir = await self._extract_backup(backup_info.file_path)
            
            # Load platform state
            state_file = backup_dir / "platform_state.json"
            with open(state_file, 'r') as f:
                platform_state = json.load(f)
            
            # Load configuration
            config_file = backup_dir / "config.json"
            with open(config_file, 'r') as f:
                config_state = json.load(f)
            
            # Restore components
            if components:
                # Partial restore
                for component in components:
                    if component in platform_state:
                        await self._restore_component(component, platform_state[component])
            else:
                # Full restore
                await self._restore_platform_state(platform_state)
                self.config_manager.import_config(config_state)
            
            # Update operation status
            for op in self._recovery_operations:
                if op["operation_id"] == operation_id:
                    op["status"] = "completed"
                    break
            
            # Cleanup extraction directory
            shutil.rmtree(backup_dir)
            
            self.logger.info(f"Backup restored successfully: {backup_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error restoring backup {backup_id}: {e}")
            
            # Update operation status
            for op in self._recovery_operations:
                if op["operation_id"] == operation_id:
                    op["status"] = "failed"
                    op["error"] = str(e)
                    break
            
            return False
    
    async def create_recovery_point(self, description: str = "") -> str:
        """Create a recovery point for quick rollback."""
        point_id = f"rp_{int(time.time() * 1000)}"
        timestamp = time.time()
        
        try:
            # Collect current state
            state = await self._collect_platform_state()
            components = list(state.keys())
            
            # Calculate checksum
            state_str = json.dumps(state, sort_keys=True)
            checksum = str(hash(state_str))
            
            # Create recovery point
            recovery_point = RecoveryPoint(
                point_id=point_id,
                timestamp=timestamp,
                state=state,
                components=components,
                checksum=checksum,
                description=description or f"Recovery point {point_id}"
            )
            
            self._recovery_points[point_id] = recovery_point
            
            # Limit recovery points
            if len(self._recovery_points) > 20:
                # Remove oldest recovery point
                oldest_id = min(self._recovery_points.keys(), 
                              key=lambda x: self._recovery_points[x].timestamp)
                del self._recovery_points[oldest_id]
            
            self.logger.info(f"Recovery point created: {point_id}")
            return point_id
            
        except Exception as e:
            self.logger.error(f"Error creating recovery point: {e}")
            raise
    
    async def rollback_to_recovery_point(self, point_id: str) -> bool:
        """Rollback to a specific recovery point."""
        if point_id not in self._recovery_points:
            raise ValueError(f"Recovery point not found: {point_id}")
        
        recovery_point = self._recovery_points[point_id]
        
        try:
            # Create current state backup before rollback
            backup_id = await self.create_backup("pre_rollback", f"Before rollback to {point_id}")
            
            # Restore state from recovery point
            await self._restore_platform_state(recovery_point.state)
            
            self.logger.info(f"Rolled back to recovery point: {point_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error rolling back to recovery point {point_id}: {e}")
            return False
    
    async def execute_recovery_strategy(self, strategy: str, context: Dict[str, Any]) -> bool:
        """Execute a specific recovery strategy."""
        if strategy not in self._recovery_strategies:
            raise ValueError(f"Unknown recovery strategy: {strategy}")
        
        try:
            recovery_func = self._recovery_strategies[strategy]
            result = await recovery_func(context)
            
            self.logger.info(f"Recovery strategy executed: {strategy}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing recovery strategy {strategy}: {e}")
            return False
    
    async def _collect_platform_state(self) -> Dict[str, Any]:
        """Collect the current platform state."""
        # This would collect state from the actual platform components
        # For now, return a mock state structure
        return {
            "platform_info": {
                "version": "1.0.0",
                "timestamp": time.time(),
                "uptime": time.time()  # Would be actual uptime
            },
            "agents": {},  # Would contain actual agent states
            "configuration": self.config_manager.export_config(),
            "monitoring": {
                "metrics_count": 0,  # Would be actual metrics
                "alerts_count": 0
            },
            "features": {
                "enabled_features": [],  # Would list enabled features
                "feature_stats": {}
            }
        }
    
    async def _restore_platform_state(self, state: Dict[str, Any]) -> None:
        """Restore the platform to a specific state."""
        # This would restore the actual platform components
        # For now, just log the restoration
        self.logger.info("Restoring platform state...")
        
        # Simulate restoration delay
        await asyncio.sleep(1)
        
        self.logger.info("Platform state restored")
    
    async def _restore_component(self, component: str, state: Any) -> None:
        """Restore a specific component."""
        self.logger.info(f"Restoring component: {component}")
        
        # Simulate component restoration
        await asyncio.sleep(0.5)
        
        self.logger.info(f"Component restored: {component}")
    
    async def _create_backup_archive(self, source_dir: Path, archive_path: Path) -> None:
        """Create a compressed backup archive."""
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in source_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_dir)
                    zipf.write(file_path, arcname)
    
    async def _extract_backup(self, archive_path: str) -> Path:
        """Extract a backup archive."""
        extract_dir = self.backup_dir / f"extract_{int(time.time() * 1000)}"
        extract_dir.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            zipf.extractall(extract_dir)
        
        return extract_dir
    
    async def _cleanup_old_backups(self) -> None:
        """Clean up old backups to maintain storage limits."""
        if len(self._backups) <= self.max_backups:
            return
        
        # Sort backups by timestamp
        sorted_backups = sorted(self._backups.items(), 
                              key=lambda x: x[1].timestamp)
        
        # Remove oldest backups
        backups_to_remove = sorted_backups[:-self.max_backups]
        
        for backup_id, backup_info in backups_to_remove:
            try:
                # Remove backup file
                if os.path.exists(backup_info.file_path):
                    os.remove(backup_info.file_path)
                
                # Remove from index
                del self._backups[backup_id]
                
                self.logger.info(f"Removed old backup: {backup_id}")
                
            except Exception as e:
                self.logger.error(f"Error removing backup {backup_id}: {e}")
    
    async def _load_backup_index(self) -> None:
        """Load the backup index from disk."""
        index_file = self.backup_dir / "backup_index.json"
        
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    index_data = json.load(f)
                
                # Convert to BackupInfo objects
                for backup_id, backup_data in index_data.items():
                    self._backups[backup_id] = BackupInfo(**backup_data)
                
                self.logger.info(f"Loaded {len(self._backups)} backups from index")
                
            except Exception as e:
                self.logger.error(f"Error loading backup index: {e}")
    
    async def _save_backup_index(self) -> None:
        """Save the backup index to disk."""
        index_file = self.backup_dir / "backup_index.json"
        
        try:
            # Convert BackupInfo objects to dicts
            index_data = {}
            for backup_id, backup_info in self._backups.items():
                index_data[backup_id] = {
                    "backup_id": backup_info.backup_id,
                    "timestamp": backup_info.timestamp,
                    "backup_type": backup_info.backup_type,
                    "size_bytes": backup_info.size_bytes,
                    "file_path": backup_info.file_path,
                    "description": backup_info.description,
                    "metadata": backup_info.metadata
                }
            
            with open(index_file, 'w') as f:
                json.dump(index_data, f, indent=2)
            
            self.logger.info("Backup index saved")
            
        except Exception as e:
            self.logger.error(f"Error saving backup index: {e}")
    
    async def _auto_backup_loop(self) -> None:
        """Automatic backup loop."""
        while self._running:
            try:
                await self.create_backup("auto", "Automatic backup")
                await asyncio.sleep(self.backup_interval)
            except Exception as e:
                self.logger.error(f"Auto backup error: {e}")
                await asyncio.sleep(60)  # Retry after 1 minute on error
    
    async def _recovery_monitor(self) -> None:
        """Monitor recovery operations and cleanup."""
        while self._running:
            try:
                # Cleanup old recovery operations
                cutoff_time = time.time() - (7 * 24 * 3600)  # 7 days
                self._recovery_operations = [
                    op for op in self._recovery_operations
                    if op["timestamp"] > cutoff_time
                ]
                
                await asyncio.sleep(3600)  # Check every hour
            except Exception as e:
                self.logger.error(f"Recovery monitor error: {e}")
                await asyncio.sleep(300)  # Retry after 5 minutes
    
    # Recovery strategy implementations
    async def _restart_component(self, context: Dict[str, Any]) -> bool:
        """Restart a specific component."""
        component = context.get("component")
        self.logger.info(f"Restarting component: {component}")
        
        # Simulate component restart
        await asyncio.sleep(2)
        
        return True
    
    async def _restore_backup(self, context: Dict[str, Any]) -> bool:
        """Restore from backup strategy."""
        backup_id = context.get("backup_id")
        components = context.get("components")
        
        if not backup_id:
            # Use latest backup
            if not self._backups:
                return False
            backup_id = max(self._backups.keys(), 
                          key=lambda x: self._backups[x].timestamp)
        
        return await self.restore_backup(backup_id, components)
    
    async def _rollback_config(self, context: Dict[str, Any]) -> bool:
        """Rollback configuration to previous state."""
        self.logger.info("Rolling back configuration")
        
        # This would rollback configuration changes
        await asyncio.sleep(1)
        
        return True
    
    async def _reset_to_defaults(self, context: Dict[str, Any]) -> bool:
        """Reset component to default settings."""
        component = context.get("component", "system")
        self.logger.info(f"Resetting {component} to defaults")
        
        # Simulate reset operation
        await asyncio.sleep(1)
        
        return True
    
    async def _partial_restore(self, context: Dict[str, Any]) -> bool:
        """Perform partial restoration of specific components."""
        components = context.get("components", [])
        backup_id = context.get("backup_id")
        
        if backup_id and backup_id in self._backups:
            return await self.restore_backup(backup_id, components)
        
        return False
    
    async def _emergency_recovery(self, context: Dict[str, Any]) -> bool:
        """Emergency recovery procedure."""
        self.logger.warning("Executing emergency recovery")
        
        # Create emergency backup first
        backup_id = await self.create_backup("emergency", "Emergency backup before recovery")
        
        # Reset to safe state
        await self._reset_to_defaults({"component": "all"})
        
        # Restart all components
        await self._restart_component({"component": "all"})
        
        return True
    
    def get_backup_list(self) -> List[Dict[str, Any]]:
        """Get list of available backups."""
        return [
            {
                "backup_id": info.backup_id,
                "timestamp": info.timestamp,
                "backup_type": info.backup_type,
                "size_bytes": info.size_bytes,
                "description": info.description,
                "age_hours": (time.time() - info.timestamp) / 3600,
                "metadata": info.metadata
            }
            for info in sorted(self._backups.values(), 
                             key=lambda x: x.timestamp, reverse=True)
        ]
    
    def get_recovery_points(self) -> List[Dict[str, Any]]:
        """Get list of available recovery points."""
        return [
            {
                "point_id": rp.point_id,
                "timestamp": rp.timestamp,
                "description": rp.description,
                "components": rp.components,
                "age_hours": (time.time() - rp.timestamp) / 3600
            }
            for rp in sorted(self._recovery_points.values(), 
                           key=lambda x: x.timestamp, reverse=True)
        ]
    
    def get_recovery_stats(self) -> Dict[str, Any]:
        """Get recovery statistics."""
        total_backup_size = sum(backup.size_bytes for backup in self._backups.values())
        
        return {
            "backups_count": len(self._backups),
            "recovery_points_count": len(self._recovery_points),
            "total_backup_size_bytes": total_backup_size,
            "recovery_operations_count": len(self._recovery_operations),
            "auto_backup_enabled": self.auto_backup_enabled,
            "backup_interval_hours": self.backup_interval / 3600,
            "backup_directory": str(self.backup_dir),
            "recovery_strategies": list(self._recovery_strategies.keys())
        }