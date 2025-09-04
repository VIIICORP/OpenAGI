"""
Model Manager for OpenAGI - handles various LLM integrations.

This module provides a unified interface for working with different
large language models, including local and cloud-based options.
"""

import logging
import os
from typing import Dict, List, Any, Optional, Union
from enum import Enum
import json

logger = logging.getLogger(__name__)

class ModelType(Enum):
    """Types of supported models."""
    OPENAI = "openai"
    HUGGINGFACE = "huggingface"
    LLAMACPP = "llamacpp"
    CTRANSFORMERS = "ctransformers"
    LOCAL = "local"

class ModelManager:
    """
    Unified interface for managing and using different LLM models.
    
    Supports OpenAI models, Hugging Face transformers, local models
    via llama.cpp, and other open-source LLM implementations.
    """
    
    def __init__(self):
        """Initialize the model manager."""
        self.available_models = {}
        self.loaded_models = {}
        self.current_model = None
        self.model_configs = {}
        
        # Initialize available model discovery
        self._discover_models()
    
    def _discover_models(self):
        """Discover available models on the system."""
        
        # OpenAI models (if API key available)
        try:
            import openai
            if os.getenv("OPENAI_API_KEY"):
                self.available_models.update(self._get_openai_models())
        except ImportError:
            logger.info("OpenAI library not available")
        
        # Hugging Face models
        try:
            import transformers
            self.available_models.update(self._get_huggingface_models())
        except ImportError:
            logger.info("Transformers library not available")
        
        # llama.cpp models
        try:
            import llama_cpp
            self.available_models.update(self._get_llamacpp_models())
        except ImportError:
            logger.info("llama-cpp-python not available")
        
        # CTransformers models
        try:
            import ctransformers
            self.available_models.update(self._get_ctransformers_models())
        except ImportError:
            logger.info("ctransformers not available")
        
        logger.info(f"Discovered {len(self.available_models)} available models")
    
    def _get_openai_models(self) -> Dict[str, Dict]:
        """Get available OpenAI models."""
        return {
            "gpt-4": {
                "type": ModelType.OPENAI,
                "name": "GPT-4",
                "description": "OpenAI's most capable model",
                "max_tokens": 8192,
                "cost_per_1k_tokens": 0.03
            },
            "gpt-3.5-turbo": {
                "type": ModelType.OPENAI,
                "name": "GPT-3.5 Turbo",
                "description": "Fast and capable OpenAI model",
                "max_tokens": 4096,
                "cost_per_1k_tokens": 0.002
            },
            "gpt-3.5-turbo-16k": {
                "type": ModelType.OPENAI,
                "name": "GPT-3.5 Turbo 16K",
                "description": "Extended context OpenAI model",
                "max_tokens": 16384,
                "cost_per_1k_tokens": 0.004
            }
        }
    
    def _get_huggingface_models(self) -> Dict[str, Dict]:
        """Get recommended Hugging Face models."""
        return {
            "microsoft/DialoGPT-medium": {
                "type": ModelType.HUGGINGFACE,
                "name": "DialoGPT Medium",
                "description": "Conversational AI model",
                "size": "medium",
                "local": True
            },
            "microsoft/phi-2": {
                "type": ModelType.HUGGINGFACE,
                "name": "Phi-2",
                "description": "Microsoft's small but capable language model",
                "size": "small",
                "local": True
            },
            "mistralai/Mistral-7B-Instruct-v0.1": {
                "type": ModelType.HUGGINGFACE,
                "name": "Mistral 7B Instruct",
                "description": "Instruction-following model from Mistral AI",
                "size": "7B",
                "local": True
            },
            "meta-llama/Llama-2-7b-chat-hf": {
                "type": ModelType.HUGGINGFACE,
                "name": "Llama 2 7B Chat",
                "description": "Meta's Llama 2 chat model",
                "size": "7B",
                "local": True,
                "requires_auth": True
            }
        }
    
    def _get_llamacpp_models(self) -> Dict[str, Dict]:
        """Get llama.cpp compatible models."""
        # These would typically be GGUF files stored locally
        models = {}
        
        # Check common model directories
        common_paths = [
            os.path.expanduser("~/models"),
            "/models",
            "./models"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                for file in os.listdir(path):
                    if file.endswith(('.gguf', '.bin')):
                        model_id = f"local/{file}"
                        models[model_id] = {
                            "type": ModelType.LLAMACPP,
                            "name": file,
                            "description": f"Local GGUF model: {file}",
                            "path": os.path.join(path, file),
                            "local": True
                        }
        
        return models
    
    def _get_ctransformers_models(self) -> Dict[str, Dict]:
        """Get CTransformers compatible models."""
        return {
            "marella/gpt4all-j-ggml": {
                "type": ModelType.CTRANSFORMERS,
                "name": "GPT4All-J",
                "description": "GPT4All-J model via CTransformers",
                "model_type": "gptj",
                "local": True
            },
            "TheBloke/Llama-2-7B-Chat-GGML": {
                "type": ModelType.CTRANSFORMERS,
                "name": "Llama 2 7B Chat (GGML)",
                "description": "Llama 2 7B Chat in GGML format",
                "model_type": "llama",
                "local": True
            }
        }
    
    def list_models(self, model_type: Optional[ModelType] = None, 
                   local_only: bool = False) -> Dict[str, Dict]:
        """
        List available models.
        
        Args:
            model_type: Filter by model type
            local_only: Only show local models
            
        Returns:
            Dictionary of available models
        """
        filtered_models = {}
        
        for model_id, model_info in self.available_models.items():
            # Filter by type
            if model_type and model_info["type"] != model_type:
                continue
            
            # Filter by local availability
            if local_only and not model_info.get("local", False):
                continue
            
            filtered_models[model_id] = model_info
        
        return filtered_models
    
    def load_model(self, model_id: str, **kwargs) -> Dict[str, Any]:
        """
        Load a model for use.
        
        Args:
            model_id: ID of the model to load
            **kwargs: Model-specific configuration
            
        Returns:
            Dictionary containing load result
        """
        if model_id not in self.available_models:
            return {
                "success": False,
                "error": f"Model {model_id} not available"
            }
        
        if model_id in self.loaded_models:
            return {
                "success": True,
                "message": f"Model {model_id} already loaded",
                "model": self.loaded_models[model_id]
            }
        
        model_info = self.available_models[model_id]
        model_type = model_info["type"]
        
        try:
            if model_type == ModelType.OPENAI:
                model = self._load_openai_model(model_id, model_info, **kwargs)
            elif model_type == ModelType.HUGGINGFACE:
                model = self._load_huggingface_model(model_id, model_info, **kwargs)
            elif model_type == ModelType.LLAMACPP:
                model = self._load_llamacpp_model(model_id, model_info, **kwargs)
            elif model_type == ModelType.CTRANSFORMERS:
                model = self._load_ctransformers_model(model_id, model_info, **kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported model type: {model_type}"
                }
            
            self.loaded_models[model_id] = model
            self.current_model = model_id
            
            return {
                "success": True,
                "model_id": model_id,
                "model": model
            }
            
        except Exception as e:
            logger.error(f"Failed to load model {model_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _load_openai_model(self, model_id: str, model_info: Dict, **kwargs):
        """Load an OpenAI model."""
        import openai
        
        return {
            "type": "openai",
            "model_id": model_id,
            "client": openai,
            "config": model_info
        }
    
    def _load_huggingface_model(self, model_id: str, model_info: Dict, **kwargs):
        """Load a Hugging Face model."""
        from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
        
        logger.info(f"Loading Hugging Face model: {model_id}")
        
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(model_id)
        
        # Create a text generation pipeline
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            **kwargs
        )
        
        return {
            "type": "huggingface",
            "model_id": model_id,
            "tokenizer": tokenizer,
            "model": model,
            "pipeline": pipe,
            "config": model_info
        }
    
    def _load_llamacpp_model(self, model_id: str, model_info: Dict, **kwargs):
        """Load a llama.cpp model."""
        from llama_cpp import Llama
        
        model_path = model_info["path"]
        logger.info(f"Loading llama.cpp model: {model_path}")
        
        llm = Llama(
            model_path=model_path,
            **kwargs
        )
        
        return {
            "type": "llamacpp",
            "model_id": model_id,
            "llm": llm,
            "config": model_info
        }
    
    def _load_ctransformers_model(self, model_id: str, model_info: Dict, **kwargs):
        """Load a CTransformers model."""
        from ctransformers import AutoModelForCausalLM
        
        logger.info(f"Loading CTransformers model: {model_id}")
        
        llm = AutoModelForCausalLM.from_pretrained(
            model_id,
            model_type=model_info.get("model_type", "llama"),
            **kwargs
        )
        
        return {
            "type": "ctransformers",
            "model_id": model_id,
            "llm": llm,
            "config": model_info
        }
    
    def generate_text(self, prompt: str, model_id: Optional[str] = None, 
                     **kwargs) -> Dict[str, Any]:
        """
        Generate text using a loaded model.
        
        Args:
            prompt: Input prompt
            model_id: Specific model to use (default: current model)
            **kwargs: Generation parameters
            
        Returns:
            Dictionary containing generation result
        """
        target_model_id = model_id or self.current_model
        
        if not target_model_id:
            return {
                "success": False,
                "error": "No model specified or loaded"
            }
        
        if target_model_id not in self.loaded_models:
            # Try to load the model
            load_result = self.load_model(target_model_id)
            if not load_result["success"]:
                return load_result
        
        model = self.loaded_models[target_model_id]
        model_type = model["type"]
        
        try:
            if model_type == "openai":
                return self._generate_openai(model, prompt, **kwargs)
            elif model_type == "huggingface":
                return self._generate_huggingface(model, prompt, **kwargs)
            elif model_type == "llamacpp":
                return self._generate_llamacpp(model, prompt, **kwargs)
            elif model_type == "ctransformers":
                return self._generate_ctransformers(model, prompt, **kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported model type: {model_type}"
                }
                
        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_openai(self, model, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text using OpenAI model."""
        import openai
        
        response = openai.ChatCompletion.create(
            model=model["model_id"],
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        
        return {
            "success": True,
            "text": response.choices[0].message.content,
            "model": model["model_id"],
            "usage": response.usage._asdict() if hasattr(response, 'usage') else None
        }
    
    def _generate_huggingface(self, model, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text using Hugging Face model."""
        pipeline = model["pipeline"]
        
        # Set default generation parameters
        generation_kwargs = {
            "max_length": kwargs.get("max_length", 100),
            "temperature": kwargs.get("temperature", 0.7),
            "do_sample": True,
            **kwargs
        }
        
        result = pipeline(prompt, **generation_kwargs)
        generated_text = result[0]["generated_text"]
        
        # Remove the prompt from the generated text
        if generated_text.startswith(prompt):
            generated_text = generated_text[len(prompt):].strip()
        
        return {
            "success": True,
            "text": generated_text,
            "model": model["model_id"]
        }
    
    def _generate_llamacpp(self, model, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text using llama.cpp model."""
        llm = model["llm"]
        
        result = llm(
            prompt,
            max_tokens=kwargs.get("max_tokens", 128),
            temperature=kwargs.get("temperature", 0.7),
            **kwargs
        )
        
        return {
            "success": True,
            "text": result["choices"][0]["text"],
            "model": model["model_id"]
        }
    
    def _generate_ctransformers(self, model, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text using CTransformers model."""
        llm = model["llm"]
        
        result = llm(
            prompt,
            max_new_tokens=kwargs.get("max_new_tokens", 128),
            temperature=kwargs.get("temperature", 0.7),
            **kwargs
        )
        
        return {
            "success": True,
            "text": result,
            "model": model["model_id"]
        }
    
    def unload_model(self, model_id: str) -> Dict[str, Any]:
        """
        Unload a model to free memory.
        
        Args:
            model_id: ID of the model to unload
            
        Returns:
            Dictionary containing unload result
        """
        if model_id not in self.loaded_models:
            return {
                "success": False,
                "error": f"Model {model_id} not loaded"
            }
        
        try:
            del self.loaded_models[model_id]
            
            if self.current_model == model_id:
                self.current_model = None
            
            # Force garbage collection
            import gc
            gc.collect()
            
            return {
                "success": True,
                "message": f"Model {model_id} unloaded"
            }
            
        except Exception as e:
            logger.error(f"Failed to unload model {model_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_model_info(self, model_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about a model.
        
        Args:
            model_id: Model to get info for (default: current model)
            
        Returns:
            Dictionary containing model information
        """
        target_model_id = model_id or self.current_model
        
        if not target_model_id:
            return {"error": "No model specified"}
        
        info = {
            "model_id": target_model_id,
            "available": target_model_id in self.available_models,
            "loaded": target_model_id in self.loaded_models,
            "is_current": target_model_id == self.current_model
        }
        
        if target_model_id in self.available_models:
            info.update(self.available_models[target_model_id])
        
        return info
    
    def get_status(self) -> Dict[str, Any]:
        """Get model manager status."""
        return {
            "total_available": len(self.available_models),
            "loaded_models": list(self.loaded_models.keys()),
            "current_model": self.current_model,
            "model_types": list(set(m["type"].value for m in self.available_models.values()))
        }