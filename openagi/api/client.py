"""
API Client for OpenAGI Platform

Provides a client interface for interacting with the OpenAGI API.
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
import structlog

logger = structlog.get_logger(__name__)


class APIClient:
    """
    Client for interacting with OpenAGI platform API.
    
    Provides easy access to all platform features via REST API.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL of the OpenAGI server
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
        
        logger.info("API client initialized", base_url=base_url)
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def connect(self) -> None:
        """Establish connection to the API."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        self.session = aiohttp.ClientSession(
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=30)
        )
    
    async def close(self) -> None:
        """Close the API connection."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def get_status(self) -> Dict[str, Any]:
        """Get platform status."""
        return await self._request("GET", "/api/v1/status")
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models."""
        return await self._request("GET", "/api/v1/models")
    
    async def load_model(self, model_name: str) -> Dict[str, Any]:
        """Load a model."""
        return await self._request("POST", f"/api/v1/models/{model_name}/load")
    
    async def unload_model(self, model_name: str) -> Dict[str, Any]:
        """Unload a model."""
        return await self._request("POST", f"/api/v1/models/{model_name}/unload")
    
    async def create_session(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new session."""
        data = {"user_id": user_id} if user_id else {}
        return await self._request("POST", "/api/v1/sessions", json=data)
    
    async def create_pipeline(self, models: List[str], session_id: Optional[str] = None) -> Dict[str, Any]:
        """Create an AI pipeline."""
        data = {
            "models": models,
            "session_id": session_id
        }
        return await self._request("POST", "/api/v1/pipelines", json=data)
    
    async def run_inference(self, pipeline_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run inference on a pipeline."""
        data = {
            "pipeline_id": pipeline_id,
            "inputs": inputs
        }
        return await self._request("POST", "/api/v1/inference", json=data)
    
    async def run_tests(
        self, 
        suite: str = "comprehensive",
        models: Optional[List[str]] = None,
        sample_rate: Optional[float] = None
    ) -> Dict[str, Any]:
        """Run tests on the platform."""
        data = {
            "suite": suite,
            "models": models,
            "sample_rate": sample_rate
        }
        return await self._request("POST", "/api/v1/test/run", json=data)
    
    async def get_test_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get test execution history."""
        params = {"limit": limit}
        return await self._request("GET", "/api/v1/test/history", params=params)
    
    async def _request(
        self, 
        method: str, 
        path: str, 
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to the API."""
        if not self.session:
            await self.connect()
        
        url = f"{self.base_url}{path}"
        
        try:
            async with self.session.request(
                method, 
                url, 
                json=json, 
                params=params
            ) as response:
                response.raise_for_status()
                return await response.json()
                
        except aiohttp.ClientError as e:
            logger.error("API request failed", method=method, path=path, error=str(e))
            raise
        except Exception as e:
            logger.error("Unexpected error in API request", method=method, path=path, error=str(e))
            raise