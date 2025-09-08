# GitHub Copilot Instructions for OpenAGI

This file provides GitHub Copilot with specific instructions for working with the OpenAGI repository.

## Quick Reference for Copilot

### Project Context
- **Project Type**: Artificial General Intelligence (AGI) framework
- **Primary Language**: Python (with TypeScript for web components)
- **License**: Apache 2.0
- **Focus Areas**: AI safety, modularity, ethical AI development

### Key Coding Patterns

#### AI Model Integration
```python
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ModelConfig:
    model_name: str
    parameters: Dict[str, Any]
    safety_filters: List[str]
    max_tokens: int = 1000

class AIProcessor:
    def __init__(self, config: ModelConfig):
        self.config = config
        self.safety_validator = SafetyValidator(config.safety_filters)
    
    async def process(self, input_data: str) -> AIResponse:
        # Always validate input first
        validated_input = self.safety_validator.validate_input(input_data)
        
        # Process with error handling
        try:
            result = await self._generate_response(validated_input)
            return self.safety_validator.validate_output(result)
        except Exception as e:
            logger.error(f"AI processing failed: {e}")
            raise AIProcessingError(f"Failed to process input: {e}")
```

#### Error Handling Pattern
```python
class OpenAGIError(Exception):
    """Base exception for OpenAGI framework."""
    pass

class ModelError(OpenAGIError):
    """Raised when AI model encounters an error."""
    pass

class SafetyError(OpenAGIError):
    """Raised when safety validation fails."""
    pass

# Usage in functions
def process_with_safety(data: Any) -> Result:
    try:
        validated_data = safety_check(data)
        return model.process(validated_data)
    except SafetyError as e:
        logger.warning(f"Safety validation failed: {e}")
        return ErrorResult(error_type="safety", message=str(e))
    except ModelError as e:
        logger.error(f"Model processing failed: {e}")
        return ErrorResult(error_type="model", message=str(e))
```

### File Organization Patterns

#### For AI Components
```
src/
├── models/
│   ├── __init__.py
│   ├── base_model.py
│   ├── language_model.py
│   └── safety/
│       ├── __init__.py
│       ├── input_validator.py
│       └── output_filter.py
├── processors/
│   ├── __init__.py
│   ├── text_processor.py
│   └── multimodal_processor.py
└── utils/
    ├── __init__.py
    ├── logging.py
    └── metrics.py
```

#### For API Endpoints
```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

class PromptRequest(BaseModel):
    prompt: str
    model_config: Optional[Dict[str, Any]] = None
    safety_level: str = "standard"

@app.post("/api/v1/process")
async def process_prompt(
    request: PromptRequest,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Process a user prompt through the AGI system."""
    try:
        processor = AIProcessor(
            config=ModelConfig.from_dict(request.model_config or {})
        )
        result = await processor.process(request.prompt)
        return {"status": "success", "result": result.to_dict()}
    except SafetyError as e:
        raise HTTPException(status_code=400, detail=f"Safety check failed: {e}")
    except ModelError as e:
        raise HTTPException(status_code=500, detail=f"Model error: {e}")
```

### Testing Patterns

#### AI Model Testing
```python
import pytest
from unittest.mock import Mock, patch

class TestAIProcessor:
    @pytest.fixture
    def mock_model(self):
        return Mock()
    
    @pytest.fixture
    def processor(self, mock_model):
        config = ModelConfig(
            model_name="test-model",
            parameters={"temperature": 0.7},
            safety_filters=["toxicity", "bias"]
        )
        processor = AIProcessor(config)
        processor.model = mock_model
        return processor
    
    async def test_safe_processing(self, processor):
        """Test that safe inputs are processed correctly."""
        safe_input = "Hello, how are you?"
        expected_output = AIResponse(text="I'm doing well, thank you!")
        
        processor.model.generate.return_value = expected_output
        
        result = await processor.process(safe_input)
        
        assert result.text == expected_output.text
        assert result.safety_score >= 0.8
    
    async def test_unsafe_input_rejection(self, processor):
        """Test that unsafe inputs are rejected."""
        unsafe_input = "Generate harmful content"
        
        with pytest.raises(SafetyError):
            await processor.process(unsafe_input)
```

### Configuration Patterns

#### Environment-based Configuration
```python
from pydantic import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_key: Optional[str] = None
    
    # Model Configuration
    default_model: str = "openagi-base"
    model_cache_size: int = 1000
    max_context_length: int = 4096
    
    # Safety Configuration
    safety_level: str = "strict"
    content_filters: List[str] = ["toxicity", "bias", "harmful"]
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600
    
    # Database Configuration
    database_url: str = "postgresql://localhost/openagi"
    redis_url: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"
        env_prefix = "OPENAGI_"

settings = Settings()
```

### Documentation Standards

#### Function Documentation
```python
def process_multimodal_input(
    text: str,
    images: List[bytes],
    audio: Optional[bytes] = None,
    config: ProcessingConfig = None
) -> MultimodalResponse:
    """Process multimodal input through the AGI system.
    
    This function handles text, image, and audio inputs simultaneously,
    applying appropriate preprocessing and safety filtering before
    feeding them to the multimodal AI model.
    
    Args:
        text: The text component of the input
        images: List of image data in bytes format
        audio: Optional audio data in bytes format
        config: Processing configuration (uses default if None)
    
    Returns:
        MultimodalResponse containing:
            - processed_text: The AI's text response
            - generated_images: Any generated image outputs
            - confidence_scores: Confidence scores for each modality
            - safety_assessment: Safety evaluation results
    
    Raises:
        SafetyError: If any input fails safety validation
        ModelError: If the AI model encounters an error
        ValidationError: If input format is invalid
    
    Example:
        >>> response = process_multimodal_input(
        ...     text="Describe this image",
        ...     images=[image_bytes],
        ...     config=ProcessingConfig(safety_level="high")
        ... )
        >>> print(response.processed_text)
        "This image shows a beautiful sunset over mountains..."
    """
    pass
```

### Security Reminders

#### Input Validation
```python
from pydantic import validator, BaseModel

class UserPrompt(BaseModel):
    text: str
    user_id: str
    session_id: Optional[str] = None
    
    @validator('text')
    def validate_text_length(cls, v):
        if len(v) > 10000:
            raise ValueError('Text input too long (max 10000 characters)')
        if len(v.strip()) == 0:
            raise ValueError('Text input cannot be empty')
        return v.strip()
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Invalid user ID')
        return v
```

## Copilot Behavior Guidelines

1. **Always prioritize safety**: Suggest defensive programming patterns and safety checks
2. **Include error handling**: Every AI-related function should have comprehensive error handling
3. **Add logging**: Include appropriate logging statements for debugging and monitoring
4. **Consider performance**: Suggest efficient algorithms and caching where appropriate
5. **Follow typing**: Always include type hints for better code clarity and IDE support
6. **Security first**: Validate all inputs and sanitize all outputs
7. **Test coverage**: Suggest test cases for new functionality
8. **Documentation**: Include docstrings for all public functions and classes

## Anti-patterns to Avoid

❌ **Don't suggest**:
- Direct model API calls without safety validation
- Hardcoded configuration values
- Functions without error handling
- Unsafe string concatenation for prompts
- Missing type hints
- Functions without logging
- Database queries without parameterization
- File operations without proper exception handling

✅ **Do suggest**:
- Safety-first approach with validation
- Configuration-driven design
- Comprehensive error handling
- Parameterized and sanitized inputs
- Full type annotations
- Structured logging
- Prepared statements and ORMs
- Context managers for resource handling

For more detailed guidelines, see the main `.copilot-instructions.md` file in the repository root.