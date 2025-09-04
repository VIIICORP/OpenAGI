"""Tests for OpenAGI core functionality."""

import pytest
from unittest.mock import Mock, patch
from openagi.core.platform import OpenAGI
from openagi.core.config import Config
from openagi.models.registry import ModelRegistry, ModelInfo, ModelCategory


class TestConfig:
    """Test configuration management."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        
        assert config.get("openagi.models.cache_dir") == "./models"
        assert config.get("openagi.api.port") == 8000
        assert config.get("openagi.storage.backend") == "local"
        
    def test_config_override(self):
        """Test configuration overrides."""
        config = Config(host="127.0.0.1", port=9000)
        
        assert config.get("host") == "127.0.0.1"
        assert config.get("port") == 9000
        
    def test_nested_config_access(self):
        """Test nested configuration access."""
        config = Config()
        
        gpu_memory = config.get("openagi.models.gpu_memory_fraction")
        assert gpu_memory == 0.8


class TestModelRegistry:
    """Test model registry functionality."""
    
    def test_model_registry_initialization(self):
        """Test model registry loads models."""
        config = Config()
        registry = ModelRegistry(config)
        
        assert registry.count() > 0
        assert len(registry.list_categories()) > 0
        
    def test_model_categories(self):
        """Test model categories are properly loaded."""
        config = Config()
        registry = ModelRegistry(config)
        
        categories = registry.list_categories()
        
        # Check that all expected categories have models
        expected_categories = ["llm", "vision", "audio", "multimodal", "embedding"]
        for category in expected_categories:
            assert category in categories
            assert categories[category] > 0
            
    def test_model_search(self):
        """Test model search functionality."""
        config = Config()
        registry = ModelRegistry(config)
        
        # Search for Llama models
        llama_models = registry.search("llama")
        assert len(llama_models) > 0
        
        # All results should contain "llama" in name, description, or tags
        for model in llama_models:
            found = (
                "llama" in model.name.lower() or
                "llama" in model.description.lower() or
                any("llama" in tag.lower() for tag in model.tags)
            )
            assert found
            
    def test_model_filtering(self):
        """Test model filtering by category."""
        config = Config()
        registry = ModelRegistry(config)
        
        # Filter by LLM category
        llm_models = registry.list(category="llm")
        assert len(llm_models) > 0
        
        # All results should be LLM models
        for model in llm_models:
            assert model.category == ModelCategory.LLM
            
    def test_model_info_structure(self):
        """Test model info has required fields."""
        config = Config()
        registry = ModelRegistry(config)
        
        # Get first model
        models = registry.list()
        assert len(models) > 0
        
        model = models[0]
        
        # Check required fields
        assert hasattr(model, 'id')
        assert hasattr(model, 'name')
        assert hasattr(model, 'category')
        assert hasattr(model, 'description')
        assert hasattr(model, 'provider')
        assert hasattr(model, 'parameters')
        assert hasattr(model, 'capabilities')
        assert hasattr(model, 'modalities')
        
        # Check types
        assert isinstance(model.id, str)
        assert isinstance(model.name, str)
        assert isinstance(model.category, ModelCategory)
        assert isinstance(model.parameters, int)
        assert isinstance(model.capabilities, list)
        assert isinstance(model.modalities, list)


class TestOpenAGIPlatform:
    """Test main OpenAGI platform."""
    
    def test_platform_initialization(self):
        """Test platform initializes successfully."""
        agi = OpenAGI()
        
        assert agi.models is not None
        assert agi.agents is not None
        assert agi.storage is not None
        assert agi.metrics is not None
        assert agi.config is not None
        
    def test_platform_stats(self):
        """Test platform statistics."""
        agi = OpenAGI()
        stats = agi.get_stats()
        
        assert "total_models" in stats
        assert "categories" in stats
        assert "active_agents" in stats
        assert "storage_usage" in stats
        assert "system_metrics" in stats
        
        assert stats["total_models"] > 0
        assert len(stats["categories"]) > 0
        
    def test_platform_health_check(self):
        """Test platform health check."""
        agi = OpenAGI()
        health = agi.health_check()
        
        assert "status" in health
        assert "models" in health
        assert "agents" in health
        assert "storage" in health
        assert "metrics" in health
        
        assert health["status"] == "healthy"
        
    def test_list_categories(self):
        """Test listing model categories."""
        agi = OpenAGI()
        categories = agi.list_categories()
        
        assert isinstance(categories, dict)
        assert len(categories) > 0
        
        # Check for expected categories
        expected_categories = ["llm", "vision", "audio", "multimodal", "embedding"]
        for category in expected_categories:
            assert category in categories
            
    def test_search_models(self):
        """Test model search through platform."""
        agi = OpenAGI()
        
        # Search for text models
        text_models = agi.search_models("text", category="llm")
        assert len(text_models) > 0
        
        # Search for vision models
        vision_models = agi.search_models("image", category="vision")
        assert len(vision_models) > 0


@pytest.fixture
def mock_model_registry():
    """Create a mock model registry for testing."""
    registry = Mock(spec=ModelRegistry)
    
    # Mock some basic methods
    registry.count.return_value = 20000
    registry.list_categories.return_value = {
        "llm": 5000,
        "vision": 3000,
        "audio": 2000,
        "multimodal": 1500,
        "embedding": 1000
    }
    
    return registry


def test_platform_with_mock_registry(mock_model_registry):
    """Test platform with mocked model registry."""
    with patch('openagi.core.platform.ModelRegistry', return_value=mock_model_registry):
        agi = OpenAGI()
        
        # Test that mock is used
        assert agi.models.count() == 20000
        categories = agi.models.list_categories()
        assert categories["llm"] == 5000


class TestModelInfo:
    """Test ModelInfo data structure."""
    
    def test_model_info_creation(self):
        """Test creating ModelInfo instances."""
        model = ModelInfo(
            id="test-model",
            name="Test Model",
            category=ModelCategory.LLM,
            description="A test model",
            provider="Test Provider",
            model_type="transformer",
            size="7B",
            parameters=7_000_000_000,
            license="Apache-2.0",
            tags=["test", "llm"],
            capabilities=["text-generation"],
            languages=["en"],
            modalities=["text"],
            hardware_requirements={"min_gpu_memory": "8GB"},
            performance_metrics={"perplexity": 10.5}
        )
        
        assert model.id == "test-model"
        assert model.name == "Test Model"
        assert model.category == ModelCategory.LLM
        assert model.parameters == 7_000_000_000
        assert "test" in model.tags
        assert "text-generation" in model.capabilities


if __name__ == "__main__":
    pytest.main([__file__])