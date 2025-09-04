"""API client for OpenAGI."""

import logging
import requests
from typing import Dict, List, Any, Optional, Union
import json

logger = logging.getLogger(__name__)


class OpenAGIClient:
    """
    Client for interacting with OpenAGI platform API.
    
    Provides convenient methods for:
    - Model discovery and loading
    - Agent creation and management
    - Task execution
    - System monitoring
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = None):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the OpenAGI API
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
            
        logger.info(f"OpenAGI client initialized for {base_url}")
        
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to API."""
        url = f"{self.base_url}/api/v1{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
            
    def get_status(self) -> Dict[str, Any]:
        """Get platform status."""
        return self._request("GET", "/status")
        
    def get_health(self) -> Dict[str, Any]:
        """Get platform health check."""
        return self._request("GET", "/health")
        
    def get_stats(self) -> Dict[str, Any]:
        """Get platform statistics."""
        return self._request("GET", "/stats")
        
    # Model API
    def list_models(self, category: str = None, provider: str = None, 
                   size: str = None) -> List[Dict[str, Any]]:
        """
        List available models.
        
        Args:
            category: Optional category filter
            provider: Optional provider filter
            size: Optional size filter
            
        Returns:
            List of model information
        """
        params = {}
        if category:
            params["category"] = category
        if provider:
            params["provider"] = provider
        if size:
            params["size"] = size
            
        return self._request("GET", "/models", params=params)
        
    def get_model(self, model_id: str) -> Dict[str, Any]:
        """
        Get information about a specific model.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Model information
        """
        return self._request("GET", f"/models/{model_id}")
        
    def search_models(self, query: str, category: str = None) -> List[Dict[str, Any]]:
        """
        Search for models.
        
        Args:
            query: Search query
            category: Optional category filter
            
        Returns:
            List of matching models
        """
        params = {"q": query}
        if category:
            params["category"] = category
            
        return self._request("GET", "/models/search", params=params)
        
    def load_model(self, model_id: str, **kwargs) -> Dict[str, Any]:
        """
        Load a model for inference.
        
        Args:
            model_id: Model identifier
            **kwargs: Additional loading parameters
            
        Returns:
            Model loading result
        """
        data = {"model_id": model_id, "parameters": kwargs}
        return self._request("POST", "/models/load", json=data)
        
    def unload_model(self, model_id: str) -> Dict[str, Any]:
        """
        Unload a model.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Unloading result
        """
        return self._request("POST", f"/models/{model_id}/unload")
        
    # Inference API
    def generate_text(self, model_id: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate text using a language model.
        
        Args:
            model_id: Model identifier
            prompt: Input prompt
            **kwargs: Generation parameters
            
        Returns:
            Generated text response
        """
        data = {
            "model_id": model_id,
            "prompt": prompt,
            "parameters": kwargs
        }
        return self._request("POST", "/generate/text", json=data)
        
    def chat(self, model_id: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Chat with a conversational model.
        
        Args:
            model_id: Model identifier
            messages: Conversation messages
            **kwargs: Generation parameters
            
        Returns:
            Chat response
        """
        data = {
            "model_id": model_id,
            "messages": messages,
            "parameters": kwargs
        }
        return self._request("POST", "/chat", json=data)
        
    def classify_image(self, model_id: str, image_data: bytes, **kwargs) -> Dict[str, Any]:
        """
        Classify an image.
        
        Args:
            model_id: Model identifier
            image_data: Image data as bytes
            **kwargs: Classification parameters
            
        Returns:
            Classification results
        """
        files = {"image": image_data}
        data = {"model_id": model_id, "parameters": json.dumps(kwargs)}
        return self._request("POST", "/vision/classify", files=files, data=data)
        
    def transcribe_audio(self, model_id: str, audio_data: bytes, **kwargs) -> Dict[str, Any]:
        """
        Transcribe audio to text.
        
        Args:
            model_id: Model identifier
            audio_data: Audio data as bytes
            **kwargs: Transcription parameters
            
        Returns:
            Transcription result
        """
        files = {"audio": audio_data}
        data = {"model_id": model_id, "parameters": json.dumps(kwargs)}
        return self._request("POST", "/audio/transcribe", files=files, data=data)
        
    def generate_embeddings(self, model_id: str, texts: List[str], **kwargs) -> Dict[str, Any]:
        """
        Generate text embeddings.
        
        Args:
            model_id: Model identifier
            texts: List of texts to embed
            **kwargs: Embedding parameters
            
        Returns:
            Generated embeddings
        """
        data = {
            "model_id": model_id,
            "texts": texts,
            "parameters": kwargs
        }
        return self._request("POST", "/embeddings", json=data)
        
    # Agent API
    def list_agents(self, status: str = None) -> List[Dict[str, Any]]:
        """
        List agents.
        
        Args:
            status: Optional status filter
            
        Returns:
            List of agents
        """
        params = {}
        if status:
            params["status"] = status
            
        return self._request("GET", "/agents", params=params)
        
    def create_agent(self, agent_type: str, name: str = None, 
                    config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a new agent.
        
        Args:
            agent_type: Type of agent to create
            name: Optional agent name
            config: Optional agent configuration
            
        Returns:
            Created agent information
        """
        data = {
            "agent_type": agent_type,
            "name": name,
            "config": config or {}
        }
        return self._request("POST", "/agents", json=data)
        
    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Get agent information.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Agent information
        """
        return self._request("GET", f"/agents/{agent_id}")
        
    def delete_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Delete an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Deletion result
        """
        return self._request("DELETE", f"/agents/{agent_id}")
        
    def submit_task(self, agent_id: str, task_description: str, 
                   inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Submit a task to an agent.
        
        Args:
            agent_id: Agent identifier
            task_description: Description of the task
            inputs: Task inputs
            
        Returns:
            Task submission result
        """
        data = {
            "agent_id": agent_id,
            "description": task_description,
            "inputs": inputs or {}
        }
        return self._request("POST", "/tasks", json=data)
        
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get task status.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task status information
        """
        return self._request("GET", f"/tasks/{task_id}")
        
    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """
        Cancel a running task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Cancellation result
        """
        return self._request("POST", f"/tasks/{task_id}/cancel")
        
    # Metrics API
    def get_metrics(self) -> Dict[str, Any]:
        """Get platform metrics."""
        return self._request("GET", "/metrics")
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system resource metrics."""
        return self._request("GET", "/metrics/system")
        
    # Convenience methods
    def quick_chat(self, prompt: str, model: str = "llama2-7b-chat") -> str:
        """
        Quick chat with default model.
        
        Args:
            prompt: Chat prompt
            model: Model to use
            
        Returns:
            Response text
        """
        try:
            # Load model if needed
            self.load_model(model)
            
            # Generate response
            response = self.generate_text(model, prompt)
            return response.get("text", "")
            
        except Exception as e:
            logger.error(f"Quick chat failed: {e}")
            return f"Error: {e}"
            
    def analyze_image(self, image_data: bytes, model: str = "resnet-50") -> Dict[str, Any]:
        """
        Quick image analysis.
        
        Args:
            image_data: Image data as bytes
            model: Model to use
            
        Returns:
            Analysis results
        """
        try:
            # Load model if needed
            self.load_model(model)
            
            # Classify image
            return self.classify_image(model, image_data)
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return {"error": str(e)}
            
    def transcribe(self, audio_data: bytes, model: str = "whisper-large-v3") -> str:
        """
        Quick audio transcription.
        
        Args:
            audio_data: Audio data as bytes
            model: Model to use
            
        Returns:
            Transcribed text
        """
        try:
            # Load model if needed
            self.load_model(model)
            
            # Transcribe audio
            response = self.transcribe_audio(model, audio_data)
            return response.get("text", "")
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return f"Error: {e}"


# Alias for backwards compatibility
Client = OpenAGIClient