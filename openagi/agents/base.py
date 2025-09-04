"""Base agent class for OpenAGI."""

import logging
import uuid
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent execution status."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class AgentTask:
    """Represents a task for an agent."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    status: AgentStatus = AgentStatus.IDLE
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentCapability:
    """Describes an agent capability."""
    name: str
    description: str
    input_types: List[str]
    output_types: List[str]
    parameters: Dict[str, Any] = field(default_factory=dict)


class Agent(ABC):
    """
    Base class for all OpenAGI agents.
    
    Agents are autonomous AI entities that can:
    - Execute tasks
    - Use tools and models
    - Collaborate with other agents
    - Learn and adapt
    """
    
    def __init__(self, agent_id: str = None, name: str = None, config: Dict[str, Any] = None):
        """
        Initialize the agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name
            config: Agent configuration
        """
        self.id = agent_id or str(uuid.uuid4())
        self.name = name or f"Agent-{self.id[:8]}"
        self.config = config or {}
        
        self.status = AgentStatus.IDLE
        self.current_task: Optional[AgentTask] = None
        self.task_history: List[AgentTask] = []
        self.capabilities: List[AgentCapability] = []
        self.tools: Dict[str, Any] = {}
        self.memory: Dict[str, Any] = {}
        
        self.created_at = datetime.now()
        self.last_active = datetime.now()
        
        logger.info(f"Initialized agent: {self.name} ({self.id})")
        
    @abstractmethod
    def execute_task(self, task: AgentTask) -> AgentTask:
        """
        Execute a task.
        
        Args:
            task: Task to execute
            
        Returns:
            Updated task with results
        """
        pass
        
    @abstractmethod
    def get_capabilities(self) -> List[AgentCapability]:
        """
        Get list of agent capabilities.
        
        Returns:
            List of capabilities
        """
        pass
        
    def add_capability(self, capability: AgentCapability):
        """Add a new capability to the agent."""
        self.capabilities.append(capability)
        logger.info(f"Added capability '{capability.name}' to agent {self.name}")
        
    def has_capability(self, capability_name: str) -> bool:
        """Check if agent has a specific capability."""
        return any(cap.name == capability_name for cap in self.capabilities)
        
    def add_tool(self, name: str, tool: Any):
        """Add a tool to the agent's toolkit."""
        self.tools[name] = tool
        logger.info(f"Added tool '{name}' to agent {self.name}")
        
    def get_tool(self, name: str) -> Any:
        """Get a tool by name."""
        return self.tools.get(name)
        
    def run_task(self, task_description: str, inputs: Dict[str, Any] = None) -> AgentTask:
        """
        Run a task with description and inputs.
        
        Args:
            task_description: Description of the task
            inputs: Input parameters
            
        Returns:
            Completed task
        """
        task = AgentTask(
            description=task_description,
            inputs=inputs or {}
        )
        
        return self.execute_task(task)
        
    def start_task(self, task: AgentTask):
        """Start executing a task."""
        self.current_task = task
        self.status = AgentStatus.RUNNING
        task.status = AgentStatus.RUNNING
        task.started_at = datetime.now()
        self.last_active = datetime.now()
        
        logger.info(f"Agent {self.name} started task: {task.description}")
        
    def complete_task(self, task: AgentTask, outputs: Dict[str, Any] = None):
        """Complete a task."""
        task.status = AgentStatus.COMPLETED
        task.completed_at = datetime.now()
        task.outputs = outputs or {}
        
        self.task_history.append(task)
        self.current_task = None
        self.status = AgentStatus.IDLE
        self.last_active = datetime.now()
        
        logger.info(f"Agent {self.name} completed task: {task.description}")
        
    def fail_task(self, task: AgentTask, error: str):
        """Mark a task as failed."""
        task.status = AgentStatus.FAILED
        task.completed_at = datetime.now()
        task.error = error
        
        self.task_history.append(task)
        self.current_task = None
        self.status = AgentStatus.IDLE
        self.last_active = datetime.now()
        
        logger.error(f"Agent {self.name} failed task: {task.description} - {error}")
        
    def pause_task(self, task: AgentTask):
        """Pause the current task."""
        task.status = AgentStatus.PAUSED
        self.status = AgentStatus.PAUSED
        
        logger.info(f"Agent {self.name} paused task: {task.description}")
        
    def resume_task(self, task: AgentTask):
        """Resume a paused task."""
        task.status = AgentStatus.RUNNING
        self.status = AgentStatus.RUNNING
        self.last_active = datetime.now()
        
        logger.info(f"Agent {self.name} resumed task: {task.description}")
        
    def get_status(self) -> Dict[str, Any]:
        """Get agent status information."""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "current_task": self.current_task.id if self.current_task else None,
            "total_tasks": len(self.task_history),
            "successful_tasks": len([t for t in self.task_history if t.status == AgentStatus.COMPLETED]),
            "failed_tasks": len([t for t in self.task_history if t.status == AgentStatus.FAILED]),
            "capabilities": [cap.name for cap in self.capabilities],
            "tools": list(self.tools.keys()),
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat()
        }
        
    def update_memory(self, key: str, value: Any):
        """Update agent memory."""
        self.memory[key] = value
        
    def get_memory(self, key: str, default: Any = None) -> Any:
        """Get value from agent memory."""
        return self.memory.get(key, default)
        
    def clear_memory(self):
        """Clear agent memory."""
        self.memory.clear()
        
    def save_state(self) -> Dict[str, Any]:
        """Save agent state for persistence."""
        return {
            "id": self.id,
            "name": self.name,
            "config": self.config,
            "status": self.status.value,
            "capabilities": [
                {
                    "name": cap.name,
                    "description": cap.description,
                    "input_types": cap.input_types,
                    "output_types": cap.output_types,
                    "parameters": cap.parameters
                }
                for cap in self.capabilities
            ],
            "memory": self.memory,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "task_history": [
                {
                    "id": task.id,
                    "description": task.description,
                    "status": task.status.value,
                    "created_at": task.created_at.isoformat(),
                    "started_at": task.started_at.isoformat() if task.started_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "error": task.error
                }
                for task in self.task_history
            ]
        }
        
    @classmethod
    def load_state(cls, state: Dict[str, Any]) -> 'Agent':
        """Load agent from saved state."""
        agent = cls(
            agent_id=state["id"],
            name=state["name"],
            config=state["config"]
        )
        
        agent.status = AgentStatus(state["status"])
        agent.memory = state["memory"]
        agent.created_at = datetime.fromisoformat(state["created_at"])
        agent.last_active = datetime.fromisoformat(state["last_active"])
        
        # Restore capabilities
        for cap_data in state["capabilities"]:
            capability = AgentCapability(
                name=cap_data["name"],
                description=cap_data["description"],
                input_types=cap_data["input_types"],
                output_types=cap_data["output_types"],
                parameters=cap_data["parameters"]
            )
            agent.add_capability(capability)
            
        return agent


class ConversationalAgent(Agent):
    """Agent specialized for conversation and text interaction."""
    
    def __init__(self, model_registry, **kwargs):
        super().__init__(**kwargs)
        self.model_registry = model_registry
        self.llm_model = None
        
        # Add conversational capabilities
        self.add_capability(AgentCapability(
            name="text_generation",
            description="Generate text responses",
            input_types=["text"],
            output_types=["text"]
        ))
        
        self.add_capability(AgentCapability(
            name="conversation",
            description="Engage in multi-turn conversations",
            input_types=["conversation_history"],
            output_types=["text"]
        ))
        
    def execute_task(self, task: AgentTask) -> AgentTask:
        """Execute a conversational task."""
        self.start_task(task)
        
        try:
            if "prompt" in task.inputs:
                response = self._generate_response(task.inputs["prompt"])
                self.complete_task(task, {"response": response})
            elif "messages" in task.inputs:
                response = self._handle_conversation(task.inputs["messages"])
                self.complete_task(task, {"response": response})
            else:
                self.fail_task(task, "No valid input provided")
                
        except Exception as e:
            self.fail_task(task, str(e))
            
        return task
        
    def get_capabilities(self) -> List[AgentCapability]:
        """Get conversational capabilities."""
        return self.capabilities
        
    def _generate_response(self, prompt: str) -> str:
        """Generate a response to a prompt."""
        if not self.llm_model:
            self.llm_model = self.model_registry.load("llama2-7b-chat")
            
        return self.llm_model.generate(prompt)
        
    def _handle_conversation(self, messages: List[Dict[str, str]]) -> str:
        """Handle multi-turn conversation."""
        if not self.llm_model:
            self.llm_model = self.model_registry.load("llama2-7b-chat")
            
        return self.llm_model.chat(messages)


class VisionAgent(Agent):
    """Agent specialized for computer vision tasks."""
    
    def __init__(self, model_registry, **kwargs):
        super().__init__(**kwargs)
        self.model_registry = model_registry
        self.vision_models = {}
        
        # Add vision capabilities
        self.add_capability(AgentCapability(
            name="image_classification",
            description="Classify images",
            input_types=["image"],
            output_types=["classification"]
        ))
        
        self.add_capability(AgentCapability(
            name="object_detection",
            description="Detect objects in images",
            input_types=["image"],
            output_types=["detections"]
        ))
        
        self.add_capability(AgentCapability(
            name="image_captioning",
            description="Generate captions for images",
            input_types=["image"],
            output_types=["text"]
        ))
        
    def execute_task(self, task: AgentTask) -> AgentTask:
        """Execute a vision task."""
        self.start_task(task)
        
        try:
            if "image" in task.inputs:
                task_type = task.inputs.get("task_type", "classification")
                result = self._process_image(task.inputs["image"], task_type)
                self.complete_task(task, {"result": result})
            else:
                self.fail_task(task, "No image input provided")
                
        except Exception as e:
            self.fail_task(task, str(e))
            
        return task
        
    def get_capabilities(self) -> List[AgentCapability]:
        """Get vision capabilities."""
        return self.capabilities
        
    def _process_image(self, image, task_type: str):
        """Process image based on task type."""
        if task_type == "classification":
            if "classifier" not in self.vision_models:
                self.vision_models["classifier"] = self.model_registry.load("resnet-50")
            return self.vision_models["classifier"].classify(image)
            
        elif task_type == "detection":
            if "detector" not in self.vision_models:
                self.vision_models["detector"] = self.model_registry.load("yolo-v8m")
            return self.vision_models["detector"].detect(image)
            
        elif task_type == "captioning":
            if "captioner" not in self.vision_models:
                self.vision_models["captioner"] = self.model_registry.load("blip-large")
            return self.vision_models["captioner"].generate_from_image(image)
            
        else:
            raise ValueError(f"Unknown task type: {task_type}")


class MultimodalAgent(Agent):
    """Agent that can handle multiple modalities."""
    
    def __init__(self, model_registry, **kwargs):
        super().__init__(**kwargs)
        self.model_registry = model_registry
        self.models = {}
        
        # Add multimodal capabilities
        self.add_capability(AgentCapability(
            name="text_to_image",
            description="Generate images from text",
            input_types=["text"],
            output_types=["image"]
        ))
        
        self.add_capability(AgentCapability(
            name="image_to_text",
            description="Generate text from images",
            input_types=["image"],
            output_types=["text"]
        ))
        
        self.add_capability(AgentCapability(
            name="speech_to_text",
            description="Convert speech to text",
            input_types=["audio"],
            output_types=["text"]
        ))
        
        self.add_capability(AgentCapability(
            name="text_to_speech",
            description="Convert text to speech",
            input_types=["text"],
            output_types=["audio"]
        ))
        
    def execute_task(self, task: AgentTask) -> AgentTask:
        """Execute a multimodal task."""
        self.start_task(task)
        
        try:
            task_type = task.inputs.get("task_type")
            
            if task_type == "text_to_image":
                result = self._text_to_image(task.inputs["prompt"])
            elif task_type == "image_to_text":
                result = self._image_to_text(task.inputs["image"])
            elif task_type == "speech_to_text":
                result = self._speech_to_text(task.inputs["audio"])
            elif task_type == "text_to_speech":
                result = self._text_to_speech(task.inputs["text"])
            else:
                raise ValueError(f"Unknown task type: {task_type}")
                
            self.complete_task(task, {"result": result})
            
        except Exception as e:
            self.fail_task(task, str(e))
            
        return task
        
    def get_capabilities(self) -> List[AgentCapability]:
        """Get multimodal capabilities."""
        return self.capabilities
        
    def _text_to_image(self, prompt: str):
        """Generate image from text."""
        if "text_to_image" not in self.models:
            self.models["text_to_image"] = self.model_registry.load("stable-diffusion-xl")
        return self.models["text_to_image"].generate(prompt)
        
    def _image_to_text(self, image):
        """Generate text from image."""
        if "image_to_text" not in self.models:
            self.models["image_to_text"] = self.model_registry.load("blip-large")
        return self.models["image_to_text"].generate_from_image(image)
        
    def _speech_to_text(self, audio):
        """Convert speech to text."""
        if "speech_to_text" not in self.models:
            self.models["speech_to_text"] = self.model_registry.load("whisper-large-v3")
        return self.models["speech_to_text"].transcribe(audio)
        
    def _text_to_speech(self, text: str):
        """Convert text to speech."""
        if "text_to_speech" not in self.models:
            self.models["text_to_speech"] = self.model_registry.load("bark")
        return self.models["text_to_speech"].synthesize(text)