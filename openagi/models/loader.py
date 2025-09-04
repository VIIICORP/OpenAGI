"""Model loader for OpenAGI."""

import logging
import importlib
from typing import Any, Dict, Optional
from pathlib import Path

from .registry import ModelInfo

logger = logging.getLogger(__name__)


class ModelLoader:
    """
    Universal model loader for all supported AI frameworks.
    
    Handles loading models from various sources:
    - Hugging Face Hub
    - Local files
    - API endpoints
    - Custom implementations
    """
    
    def __init__(self, config):
        """Initialize the model loader."""
        self.config = config
        self.cache_dir = Path(config.get("openagi.models.cache_dir", "./models"))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def load(self, model_info: ModelInfo, **kwargs) -> Any:
        """
        Load a model based on its information.
        
        Args:
            model_info: Model metadata
            **kwargs: Additional loading parameters
            
        Returns:
            Loaded model instance
        """
        logger.info(f"Loading model: {model_info.name} ({model_info.id})")
        
        # Determine loading strategy based on model type and source
        if model_info.huggingface_id:
            return self._load_huggingface_model(model_info, **kwargs)
        elif model_info.openai_id:
            return self._load_openai_model(model_info, **kwargs)
        elif model_info.anthropic_id:
            return self._load_anthropic_model(model_info, **kwargs)
        elif model_info.local_path:
            return self._load_local_model(model_info, **kwargs)
        elif model_info.api_endpoint:
            return self._load_api_model(model_info, **kwargs)
        else:
            return self._load_custom_model(model_info, **kwargs)
            
    def _load_huggingface_model(self, model_info: ModelInfo, **kwargs):
        """Load model from Hugging Face Hub."""
        try:
            if model_info.category.value == "llm":
                return self._load_hf_text_model(model_info, **kwargs)
            elif model_info.category.value == "vision":
                return self._load_hf_vision_model(model_info, **kwargs)
            elif model_info.category.value == "audio":
                return self._load_hf_audio_model(model_info, **kwargs)
            elif model_info.category.value == "multimodal":
                return self._load_hf_multimodal_model(model_info, **kwargs)
            elif model_info.category.value == "embedding":
                return self._load_hf_embedding_model(model_info, **kwargs)
            else:
                return self._load_hf_generic_model(model_info, **kwargs)
        except Exception as e:
            logger.error(f"Failed to load Hugging Face model {model_info.id}: {e}")
            raise
            
    def _load_hf_text_model(self, model_info: ModelInfo, **kwargs):
        """Load Hugging Face text generation model."""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            device = kwargs.get("device", "auto")
            torch_dtype = kwargs.get("torch_dtype", "auto")
            
            tokenizer = AutoTokenizer.from_pretrained(
                model_info.huggingface_id,
                cache_dir=self.cache_dir / "tokenizers"
            )
            
            model = AutoModelForCausalLM.from_pretrained(
                model_info.huggingface_id,
                cache_dir=self.cache_dir / "models",
                device_map=device,
                torch_dtype=torch_dtype,
                **kwargs
            )
            
            return HuggingFaceTextModel(model, tokenizer, model_info)
            
        except ImportError:
            logger.error("transformers library not available")
            raise
            
    def _load_hf_vision_model(self, model_info: ModelInfo, **kwargs):
        """Load Hugging Face vision model."""
        try:
            from transformers import AutoImageProcessor, AutoModel
            
            processor = AutoImageProcessor.from_pretrained(
                model_info.huggingface_id,
                cache_dir=self.cache_dir / "processors"
            )
            
            model = AutoModel.from_pretrained(
                model_info.huggingface_id,
                cache_dir=self.cache_dir / "models",
                **kwargs
            )
            
            return HuggingFaceVisionModel(model, processor, model_info)
            
        except ImportError:
            logger.error("transformers library not available")
            raise
            
    def _load_hf_audio_model(self, model_info: ModelInfo, **kwargs):
        """Load Hugging Face audio model."""
        try:
            from transformers import AutoProcessor, AutoModel
            
            processor = AutoProcessor.from_pretrained(
                model_info.huggingface_id,
                cache_dir=self.cache_dir / "processors"
            )
            
            model = AutoModel.from_pretrained(
                model_info.huggingface_id,
                cache_dir=self.cache_dir / "models",
                **kwargs
            )
            
            return HuggingFaceAudioModel(model, processor, model_info)
            
        except ImportError:
            logger.error("transformers library not available")
            raise
            
    def _load_hf_multimodal_model(self, model_info: ModelInfo, **kwargs):
        """Load Hugging Face multimodal model."""
        try:
            from transformers import AutoProcessor, AutoModel
            
            processor = AutoProcessor.from_pretrained(
                model_info.huggingface_id,
                cache_dir=self.cache_dir / "processors"
            )
            
            model = AutoModel.from_pretrained(
                model_info.huggingface_id,
                cache_dir=self.cache_dir / "models",
                **kwargs
            )
            
            return HuggingFaceMultimodalModel(model, processor, model_info)
            
        except ImportError:
            logger.error("transformers library not available")
            raise
            
    def _load_hf_embedding_model(self, model_info: ModelInfo, **kwargs):
        """Load Hugging Face embedding model."""
        try:
            from sentence_transformers import SentenceTransformer
            
            model = SentenceTransformer(
                model_info.huggingface_id,
                cache_folder=self.cache_dir / "sentence_transformers"
            )
            
            return SentenceTransformerModel(model, model_info)
            
        except ImportError:
            logger.error("sentence-transformers library not available")
            raise
            
    def _load_hf_generic_model(self, model_info: ModelInfo, **kwargs):
        """Load generic Hugging Face model."""
        try:
            from transformers import pipeline
            
            pipe = pipeline(
                task=model_info.capabilities[0] if model_info.capabilities else "feature-extraction",
                model=model_info.huggingface_id,
                **kwargs
            )
            
            return HuggingFacePipelineModel(pipe, model_info)
            
        except ImportError:
            logger.error("transformers library not available")
            raise
            
    def _load_openai_model(self, model_info: ModelInfo, **kwargs):
        """Load OpenAI model."""
        try:
            import openai
            
            api_key = kwargs.get("api_key") or self.config.get("openai.api_key")
            if not api_key:
                raise ValueError("OpenAI API key required")
                
            return OpenAIModel(model_info, api_key)
            
        except ImportError:
            logger.error("openai library not available")
            raise
            
    def _load_anthropic_model(self, model_info: ModelInfo, **kwargs):
        """Load Anthropic model."""
        try:
            import anthropic
            
            api_key = kwargs.get("api_key") or self.config.get("anthropic.api_key")
            if not api_key:
                raise ValueError("Anthropic API key required")
                
            return AnthropicModel(model_info, api_key)
            
        except ImportError:
            logger.error("anthropic library not available")
            raise
            
    def _load_local_model(self, model_info: ModelInfo, **kwargs):
        """Load model from local path."""
        local_path = Path(model_info.local_path)
        if not local_path.exists():
            raise FileNotFoundError(f"Local model path not found: {local_path}")
            
        return LocalModel(model_info, local_path, **kwargs)
        
    def _load_api_model(self, model_info: ModelInfo, **kwargs):
        """Load model via API endpoint."""
        return APIModel(model_info, **kwargs)
        
    def _load_custom_model(self, model_info: ModelInfo, **kwargs):
        """Load custom model implementation."""
        return CustomModel(model_info, **kwargs)


# Model wrapper classes
class BaseModel:
    """Base class for all model wrappers."""
    
    def __init__(self, model_info: ModelInfo):
        self.model_info = model_info
        self.id = model_info.id
        self.name = model_info.name
        self.category = model_info.category


class HuggingFaceTextModel(BaseModel):
    """Wrapper for Hugging Face text models."""
    
    def __init__(self, model, tokenizer, model_info):
        super().__init__(model_info)
        self.model = model
        self.tokenizer = tokenizer
        
    def generate(self, prompt: str, **kwargs):
        """Generate text from prompt."""
        inputs = self.tokenizer(prompt, return_tensors="pt")
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs.input_ids,
                max_length=kwargs.get("max_length", 512),
                temperature=kwargs.get("temperature", 0.7),
                do_sample=kwargs.get("do_sample", True),
                **kwargs
            )
            
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
    def chat(self, messages: list, **kwargs):
        """Chat interface for conversation models."""
        # Convert messages to prompt format
        prompt = self._format_chat_prompt(messages)
        return self.generate(prompt, **kwargs)
        
    def _format_chat_prompt(self, messages: list) -> str:
        """Format chat messages as prompt."""
        formatted = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            formatted += f"{role}: {content}\n"
        formatted += "assistant: "
        return formatted


class HuggingFaceVisionModel(BaseModel):
    """Wrapper for Hugging Face vision models."""
    
    def __init__(self, model, processor, model_info):
        super().__init__(model_info)
        self.model = model
        self.processor = processor
        
    def classify(self, image, **kwargs):
        """Classify image."""
        inputs = self.processor(image, return_tensors="pt")
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = outputs.logits.softmax(dim=-1)
            
        return predictions.cpu().numpy()
        
    def encode_image(self, image, **kwargs):
        """Get image embeddings."""
        inputs = self.processor(image, return_tensors="pt")
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            
        return outputs.last_hidden_state.mean(dim=1).cpu().numpy()


class HuggingFaceAudioModel(BaseModel):
    """Wrapper for Hugging Face audio models."""
    
    def __init__(self, model, processor, model_info):
        super().__init__(model_info)
        self.model = model
        self.processor = processor
        
    def transcribe(self, audio, **kwargs):
        """Transcribe audio to text."""
        inputs = self.processor(audio, return_tensors="pt", sampling_rate=16000)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            
        return self.processor.decode(outputs.logits.argmax(dim=-1)[0])
        
    def synthesize(self, text, **kwargs):
        """Synthesize text to audio."""
        # Implementation depends on specific model
        raise NotImplementedError("Audio synthesis not implemented")


class HuggingFaceMultimodalModel(BaseModel):
    """Wrapper for Hugging Face multimodal models."""
    
    def __init__(self, model, processor, model_info):
        super().__init__(model_info)
        self.model = model
        self.processor = processor
        
    def generate_from_image(self, image, prompt="", **kwargs):
        """Generate text from image."""
        inputs = self.processor(text=prompt, images=image, return_tensors="pt")
        
        with torch.no_grad():
            outputs = self.model.generate(**inputs, **kwargs)
            
        return self.processor.decode(outputs[0], skip_special_tokens=True)


class SentenceTransformerModel(BaseModel):
    """Wrapper for Sentence Transformer models."""
    
    def __init__(self, model, model_info):
        super().__init__(model_info)
        self.model = model
        
    def encode(self, texts, **kwargs):
        """Encode texts to embeddings."""
        return self.model.encode(texts, **kwargs)
        
    def similarity(self, text1, text2, **kwargs):
        """Compute similarity between texts."""
        embeddings = self.encode([text1, text2])
        return float(self.model.similarity(embeddings[0:1], embeddings[1:2])[0][0])


class HuggingFacePipelineModel(BaseModel):
    """Wrapper for Hugging Face pipeline models."""
    
    def __init__(self, pipeline, model_info):
        super().__init__(model_info)
        self.pipeline = pipeline
        
    def __call__(self, *args, **kwargs):
        """Call the pipeline."""
        return self.pipeline(*args, **kwargs)


class OpenAIModel(BaseModel):
    """Wrapper for OpenAI models."""
    
    def __init__(self, model_info, api_key):
        super().__init__(model_info)
        import openai
        self.client = openai.OpenAI(api_key=api_key)
        
    def generate(self, prompt: str, **kwargs):
        """Generate text from prompt."""
        response = self.client.completions.create(
            model=self.model_info.openai_id,
            prompt=prompt,
            **kwargs
        )
        return response.choices[0].text
        
    def chat(self, messages: list, **kwargs):
        """Chat interface."""
        response = self.client.chat.completions.create(
            model=self.model_info.openai_id,
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content


class AnthropicModel(BaseModel):
    """Wrapper for Anthropic models."""
    
    def __init__(self, model_info, api_key):
        super().__init__(model_info)
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)
        
    def generate(self, prompt: str, **kwargs):
        """Generate text from prompt."""
        response = self.client.completions.create(
            model=self.model_info.anthropic_id,
            prompt=prompt,
            **kwargs
        )
        return response.completion
        
    def chat(self, messages: list, **kwargs):
        """Chat interface."""
        # Convert to Anthropic format
        prompt = self._format_anthropic_prompt(messages)
        return self.generate(prompt, **kwargs)
        
    def _format_anthropic_prompt(self, messages: list) -> str:
        """Format messages for Anthropic."""
        formatted = ""
        for msg in messages:
            if msg["role"] == "user":
                formatted += f"Human: {msg['content']}\n\n"
            elif msg["role"] == "assistant":
                formatted += f"Assistant: {msg['content']}\n\n"
        formatted += "Assistant: "
        return formatted


class LocalModel(BaseModel):
    """Wrapper for local models."""
    
    def __init__(self, model_info, local_path, **kwargs):
        super().__init__(model_info)
        self.local_path = local_path
        # Load model from local path
        
    def __call__(self, *args, **kwargs):
        """Generic call interface."""
        raise NotImplementedError("Local model interface not implemented")


class APIModel(BaseModel):
    """Wrapper for API-based models."""
    
    def __init__(self, model_info, **kwargs):
        super().__init__(model_info)
        self.api_endpoint = model_info.api_endpoint
        
    def __call__(self, *args, **kwargs):
        """Generic API call interface."""
        import requests
        
        response = requests.post(
            self.api_endpoint,
            json={"inputs": args, "parameters": kwargs}
        )
        
        return response.json()


class CustomModel(BaseModel):
    """Wrapper for custom model implementations."""
    
    def __init__(self, model_info, **kwargs):
        super().__init__(model_info)
        # Load custom implementation based on model_info.id
        
    def __call__(self, *args, **kwargs):
        """Generic call interface."""
        raise NotImplementedError("Custom model interface not implemented")