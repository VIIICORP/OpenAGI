"""
Task Management Module for OpenAGI
Handles task scheduling, execution, and management
"""

import threading
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum
from core import BaseModule, SystemStatus, Priority


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(Enum):
    """Types of tasks"""
    SYSTEM = "system"
    USER = "user"
    MAINTENANCE = "maintenance"
    SECURITY = "security"
    CRITICAL = "critical"


@dataclass
class Task:
    """Task definition"""
    id: str
    name: str
    description: str
    task_type: TaskType
    priority: Priority
    function: Callable
    args: tuple = ()
    kwargs: dict = None
    scheduled_time: Optional[datetime] = None
    timeout: Optional[int] = None
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}
        if self.created_at is None:
            self.created_at = datetime.now()


class TaskManagerModule(BaseModule):
    """Task management and scheduling system"""
    
    def __init__(self):
        super().__init__("TaskManager")
        self.tasks: Dict[str, Task] = {}
        self.task_queue: List[str] = []
        self.running_tasks: Dict[str, threading.Thread] = {}
        self.completed_tasks: List[str] = []
        self.worker_threads = 4
        self.workers: List[threading.Thread] = []
        self.task_lock = threading.Lock()
        self.scheduler_thread = None
        
    def initialize(self) -> bool:
        """Initialize the task manager"""
        try:
            self.logger.info("Initializing Task Manager module...")
            self.status = SystemStatus.RUNNING
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Task Manager: {e}")
            self.status = SystemStatus.ERROR
            return False
            
    def start(self) -> bool:
        """Start the task manager"""
        try:
            self._running = True
            
            # Start worker threads
            for i in range(self.worker_threads):
                worker = threading.Thread(target=self._worker_loop, args=(i,), daemon=True)
                worker.start()
                self.workers.append(worker)
                
            # Start scheduler thread
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.scheduler_thread.start()
            
            self.logger.info(f"Task Manager started with {self.worker_threads} workers")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start Task Manager: {e}")
            return False
            
    def stop(self) -> bool:
        """Stop the task manager"""
        self._running = False
        
        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=5)
            
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
            
        self.status = SystemStatus.SHUTDOWN
        self.logger.info("Task Manager stopped")
        return True
        
    def create_task(self, name: str, description: str, function: Callable, 
                   task_type: TaskType = TaskType.USER, priority: Priority = Priority.MEDIUM,
                   args: tuple = (), kwargs: dict = None, 
                   scheduled_time: Optional[datetime] = None,
                   timeout: Optional[int] = None, max_retries: int = 3) -> str:
        """Create a new task"""
        task_id = str(uuid.uuid4())
        
        task = Task(
            id=task_id,
            name=name,
            description=description,
            task_type=task_type,
            priority=priority,
            function=function,
            args=args,
            kwargs=kwargs or {},
            scheduled_time=scheduled_time,
            timeout=timeout,
            max_retries=max_retries
        )
        
        with self.task_lock:
            self.tasks[task_id] = task
            if scheduled_time is None or scheduled_time <= datetime.now():
                self._add_to_queue(task_id)
            
        self.logger.info(f"Created task {task_id}: {name}")
        return task_id
        
    def _add_to_queue(self, task_id: str):
        """Add task to execution queue (sorted by priority)"""
        task = self.tasks[task_id]
        
        # Insert task in priority order
        inserted = False
        for i, queued_id in enumerate(self.task_queue):
            queued_task = self.tasks[queued_id]
            if task.priority.value < queued_task.priority.value:
                self.task_queue.insert(i, task_id)
                inserted = True
                break
                
        if not inserted:
            self.task_queue.append(task_id)
            
    def _worker_loop(self, worker_id: int):
        """Worker thread main loop"""
        self.logger.info(f"Worker {worker_id} started")
        
        while self._running:
            task_id = None
            
            with self.task_lock:
                if self.task_queue:
                    task_id = self.task_queue.pop(0)
                    
            if task_id:
                self._execute_task(task_id, worker_id)
            else:
                time.sleep(0.1)  # Short sleep if no tasks
                
        self.logger.info(f"Worker {worker_id} stopped")
        
    def _execute_task(self, task_id: str, worker_id: int):
        """Execute a single task"""
        task = self.tasks[task_id]
        
        try:
            self.logger.info(f"Worker {worker_id} executing task {task_id}: {task.name}")
            
            with self.task_lock:
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.now()
                self.running_tasks[task_id] = threading.current_thread()
                
            # Execute the task function
            if task.timeout:
                # TODO: Implement timeout handling
                result = task.function(*task.args, **task.kwargs)
            else:
                result = task.function(*task.args, **task.kwargs)
                
            with self.task_lock:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                task.result = result
                if task_id in self.running_tasks:
                    del self.running_tasks[task_id]
                self.completed_tasks.append(task_id)
                
            self.logger.info(f"Task {task_id} completed successfully")
            
        except Exception as e:
            with self.task_lock:
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.now()
                task.error = str(e)
                task.retry_count += 1
                
                if task_id in self.running_tasks:
                    del self.running_tasks[task_id]
                    
                # Retry if possible
                if task.retry_count < task.max_retries:
                    self.logger.warning(f"Task {task_id} failed, retrying ({task.retry_count}/{task.max_retries})")
                    task.status = TaskStatus.PENDING
                    self._add_to_queue(task_id)
                else:
                    self.logger.error(f"Task {task_id} failed permanently: {e}")
                    self.completed_tasks.append(task_id)
                    
    def _scheduler_loop(self):
        """Scheduler thread for handling scheduled tasks"""
        self.logger.info("Scheduler started")
        
        while self._running:
            try:
                current_time = datetime.now()
                
                with self.task_lock:
                    for task_id, task in self.tasks.items():
                        if (task.status == TaskStatus.PENDING and 
                            task.scheduled_time and 
                            task.scheduled_time <= current_time and
                            task_id not in self.task_queue):
                            self._add_to_queue(task_id)
                            self.logger.info(f"Scheduled task {task_id} added to queue")
                            
                self.heartbeat()
                time.sleep(1)  # Check every second
                
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                time.sleep(1)
                
        self.logger.info("Scheduler stopped")
        
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        with self.task_lock:
            if task_id not in self.tasks:
                return False
                
            task = self.tasks[task_id]
            
            if task.status == TaskStatus.PENDING:
                if task_id in self.task_queue:
                    self.task_queue.remove(task_id)
                task.status = TaskStatus.CANCELLED
                task.completed_at = datetime.now()
                self.completed_tasks.append(task_id)
                self.logger.info(f"Cancelled pending task {task_id}")
                return True
            elif task.status == TaskStatus.RUNNING:
                # TODO: Implement task interruption
                self.logger.warning(f"Cannot cancel running task {task_id} (not implemented)")
                return False
            else:
                self.logger.warning(f"Cannot cancel task {task_id} in status {task.status}")
                return False
                
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        if task_id not in self.tasks:
            return None
            
        task = self.tasks[task_id]
        return {
            'id': task.id,
            'name': task.name,
            'description': task.description,
            'type': task.task_type.value,
            'priority': task.priority.value,
            'status': task.status.value,
            'created_at': task.created_at.isoformat(),
            'started_at': task.started_at.isoformat() if task.started_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'retry_count': task.retry_count,
            'max_retries': task.max_retries,
            'error': task.error
        }
        
    def get_status(self) -> Dict[str, Any]:
        """Get task manager status"""
        with self.task_lock:
            pending_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.PENDING]
            running_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.RUNNING]
            completed_tasks = [t for t in self.tasks.values() if t.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]]
            
        return {
            'module': self.name,
            'status': self.status.value,
            'total_tasks': len(self.tasks),
            'pending_tasks': len(pending_tasks),
            'running_tasks': len(running_tasks),
            'completed_tasks': len(completed_tasks),
            'queue_length': len(self.task_queue),
            'worker_threads': self.worker_threads,
            'uptime': (datetime.now() - self.created_at).total_seconds()
        }
        
    def get_recent_tasks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent tasks"""
        recent_task_ids = sorted(
            self.tasks.keys(),
            key=lambda tid: self.tasks[tid].created_at,
            reverse=True
        )[:limit]
        
        return [self.get_task_status(tid) for tid in recent_task_ids]


# Example task functions for testing
def example_computation_task(duration: int = 1, name: str = "computation"):
    """Example computational task"""
    time.sleep(duration)
    return f"Completed {name} task after {duration} seconds"


def example_failing_task():
    """Example task that always fails"""
    raise Exception("This task is designed to fail")