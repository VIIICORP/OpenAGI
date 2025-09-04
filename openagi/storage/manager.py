"""Storage manager for OpenAGI."""

import logging
import json
import pickle
from typing import Any, Dict, List, Optional
from pathlib import Path
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class StorageBackend(ABC):
    """Abstract base class for storage backends."""
    
    @abstractmethod
    def store(self, key: str, data: Any, metadata: Dict[str, Any] = None) -> bool:
        """Store data with a key."""
        pass
        
    @abstractmethod
    def retrieve(self, key: str) -> Any:
        """Retrieve data by key."""
        pass
        
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass
        
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete data by key."""
        pass
        
    @abstractmethod
    def list_keys(self, prefix: str = "") -> List[str]:
        """List all keys with optional prefix."""
        pass
        
    @abstractmethod
    def get_size(self) -> int:
        """Get total storage size in bytes."""
        pass


class LocalStorageBackend(StorageBackend):
    """Local filesystem storage backend."""
    
    def __init__(self, base_path: str):
        """Initialize local storage."""
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
    def store(self, key: str, data: Any, metadata: Dict[str, Any] = None) -> bool:
        """Store data to local file."""
        try:
            file_path = self.base_path / f"{key}.pkl"
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
                
            # Store metadata if provided
            if metadata:
                meta_path = self.base_path / f"{key}.meta.json"
                with open(meta_path, 'w') as f:
                    json.dump(metadata, f)
                    
            return True
        except Exception as e:
            logger.error(f"Failed to store {key}: {e}")
            return False
            
    def retrieve(self, key: str) -> Any:
        """Retrieve data from local file."""
        try:
            file_path = self.base_path / f"{key}.pkl"
            if not file_path.exists():
                raise FileNotFoundError(f"Key {key} not found")
                
            with open(file_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            logger.error(f"Failed to retrieve {key}: {e}")
            raise
            
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        file_path = self.base_path / f"{key}.pkl"
        return file_path.exists()
        
    def delete(self, key: str) -> bool:
        """Delete data by key."""
        try:
            file_path = self.base_path / f"{key}.pkl"
            meta_path = self.base_path / f"{key}.meta.json"
            
            deleted = False
            if file_path.exists():
                file_path.unlink()
                deleted = True
                
            if meta_path.exists():
                meta_path.unlink()
                
            return deleted
        except Exception as e:
            logger.error(f"Failed to delete {key}: {e}")
            return False
            
    def list_keys(self, prefix: str = "") -> List[str]:
        """List all keys with optional prefix."""
        keys = []
        for file_path in self.base_path.rglob("*.pkl"):
            key = str(file_path.relative_to(self.base_path))[:-4]  # Remove .pkl
            if key.startswith(prefix):
                keys.append(key)
        return keys
        
    def get_size(self) -> int:
        """Get total storage size."""
        total_size = 0
        for file_path in self.base_path.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size


class StorageManager:
    """
    Manages data storage for OpenAGI platform.
    
    Provides unified interface for storing:
    - Model weights and configurations
    - Agent states and memory
    - Task results and history
    - User data and preferences
    """
    
    def __init__(self, config):
        """Initialize storage manager."""
        self.config = config
        
        backend_type = config.get("openagi.storage.backend", "local")
        storage_path = config.get("openagi.storage.path", "./data")
        
        if backend_type == "local":
            self.backend = LocalStorageBackend(storage_path)
        else:
            raise ValueError(f"Unsupported storage backend: {backend_type}")
            
        logger.info(f"Storage manager initialized with {backend_type} backend")
        
    def store_model_weights(self, model_id: str, weights: Any) -> bool:
        """Store model weights."""
        key = f"models/weights/{model_id}"
        return self.backend.store(key, weights, {"type": "model_weights"})
        
    def retrieve_model_weights(self, model_id: str) -> Any:
        """Retrieve model weights."""
        key = f"models/weights/{model_id}"
        return self.backend.retrieve(key)
        
    def store_agent_state(self, agent_id: str, state: Dict[str, Any]) -> bool:
        """Store agent state."""
        key = f"agents/state/{agent_id}"
        return self.backend.store(key, state, {"type": "agent_state"})
        
    def retrieve_agent_state(self, agent_id: str) -> Dict[str, Any]:
        """Retrieve agent state."""
        key = f"agents/state/{agent_id}"
        return self.backend.retrieve(key)
        
    def store_task_result(self, task_id: str, result: Any) -> bool:
        """Store task result."""
        key = f"tasks/results/{task_id}"
        return self.backend.store(key, result, {"type": "task_result"})
        
    def retrieve_task_result(self, task_id: str) -> Any:
        """Retrieve task result."""
        key = f"tasks/results/{task_id}"
        return self.backend.retrieve(key)
        
    def store_user_data(self, user_id: str, data: Any) -> bool:
        """Store user data."""
        key = f"users/data/{user_id}"
        return self.backend.store(key, data, {"type": "user_data"})
        
    def retrieve_user_data(self, user_id: str) -> Any:
        """Retrieve user data."""
        key = f"users/data/{user_id}"
        return self.backend.retrieve(key)
        
    def store_embedding_cache(self, embedding_id: str, embeddings: Any) -> bool:
        """Store embeddings in cache."""
        key = f"embeddings/cache/{embedding_id}"
        return self.backend.store(key, embeddings, {"type": "embeddings"})
        
    def retrieve_embedding_cache(self, embedding_id: str) -> Any:
        """Retrieve embeddings from cache."""
        key = f"embeddings/cache/{embedding_id}"
        return self.backend.retrieve(key)
        
    def store_conversation_history(self, conversation_id: str, history: List[Dict]) -> bool:
        """Store conversation history."""
        key = f"conversations/history/{conversation_id}"
        return self.backend.store(key, history, {"type": "conversation_history"})
        
    def retrieve_conversation_history(self, conversation_id: str) -> List[Dict]:
        """Retrieve conversation history."""
        key = f"conversations/history/{conversation_id}"
        return self.backend.retrieve(key)
        
    def list_stored_models(self) -> List[str]:
        """List all stored models."""
        keys = self.backend.list_keys("models/weights/")
        return [key.split("/")[-1] for key in keys]
        
    def list_agent_states(self) -> List[str]:
        """List all stored agent states."""
        keys = self.backend.list_keys("agents/state/")
        return [key.split("/")[-1] for key in keys]
        
    def list_task_results(self) -> List[str]:
        """List all stored task results."""
        keys = self.backend.list_keys("tasks/results/")
        return [key.split("/")[-1] for key in keys]
        
    def clear_cache(self, cache_type: str = None) -> bool:
        """Clear cache data."""
        try:
            if cache_type == "embeddings":
                keys = self.backend.list_keys("embeddings/cache/")
            elif cache_type == "models":
                keys = self.backend.list_keys("models/weights/")
            else:
                keys = self.backend.list_keys()
                
            for key in keys:
                self.backend.delete(key)
                
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False
            
    def get_usage(self) -> Dict[str, Any]:
        """Get storage usage statistics."""
        total_size = self.backend.get_size()
        
        # Count different data types
        counts = {
            "models": len(self.backend.list_keys("models/")),
            "agents": len(self.backend.list_keys("agents/")),
            "tasks": len(self.backend.list_keys("tasks/")),
            "users": len(self.backend.list_keys("users/")),
            "embeddings": len(self.backend.list_keys("embeddings/")),
            "conversations": len(self.backend.list_keys("conversations/"))
        }
        
        return {
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "item_counts": counts,
            "total_items": sum(counts.values())
        }
        
    def health_check(self) -> Dict[str, Any]:
        """Perform storage health check."""
        try:
            # Test basic operations
            test_key = "health_check_test"
            test_data = {"test": True, "timestamp": "now"}
            
            # Test store
            store_success = self.backend.store(test_key, test_data)
            
            # Test retrieve
            if store_success:
                retrieved = self.backend.retrieve(test_key)
                retrieve_success = retrieved == test_data
            else:
                retrieve_success = False
                
            # Test delete
            delete_success = self.backend.delete(test_key)
            
            usage = self.get_usage()
            
            return {
                "status": "healthy" if all([store_success, retrieve_success, delete_success]) else "unhealthy",
                "operations": {
                    "store": store_success,
                    "retrieve": retrieve_success,
                    "delete": delete_success
                },
                "usage": usage
            }
            
        except Exception as e:
            logger.error(f"Storage health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
            
    def close(self):
        """Close storage connections."""
        logger.info("Storage manager closed")