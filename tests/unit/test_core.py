"""
Unit tests for OpenAGI core functionality
"""

import pytest
from openagi.core import OpenAGI, FeatureRegistry, AIFeature


class MockFeature(AIFeature):
    """Mock feature for testing."""
    
    def __init__(self):
        super().__init__("mock_feature", "test", "A mock feature for testing")
    
    def execute(self, *args, **kwargs):
        return {"result": "mock_executed", "args": args, "kwargs": kwargs}


class TestFeatureRegistry:
    """Test cases for FeatureRegistry."""
    
    def test_registry_initialization(self):
        """Test registry initialization."""
        registry = FeatureRegistry()
        assert len(registry.list_features()) == 0
        assert len(registry.list_categories()) == 0
    
    def test_feature_registration(self):
        """Test feature registration."""
        registry = FeatureRegistry()
        feature = MockFeature()
        
        registry.register(feature)
        
        assert len(registry.list_features()) == 1
        assert feature.name in registry.list_features()
        assert len(registry.list_categories()) == 1
        assert feature.category in registry.list_categories()
    
    def test_feature_retrieval(self):
        """Test feature retrieval."""
        registry = FeatureRegistry()
        feature = MockFeature()
        registry.register(feature)
        
        retrieved = registry.get_feature("mock_feature")
        assert retrieved is not None
        assert retrieved.name == "mock_feature"
        
        not_found = registry.get_feature("nonexistent")
        assert not_found is None
    
    def test_feature_search(self):
        """Test feature search functionality."""
        registry = FeatureRegistry()
        feature = MockFeature()
        registry.register(feature)
        
        results = registry.search_features("mock")
        assert len(results) == 1
        assert results[0].name == "mock_feature"
        
        results = registry.search_features("nonexistent")
        assert len(results) == 0


class TestOpenAGI:
    """Test cases for OpenAGI main class."""
    
    def test_platform_initialization(self):
        """Test platform initialization."""
        platform = OpenAGI()
        assert platform.registry is not None
        assert platform.config is not None
    
    def test_platform_stats(self):
        """Test platform statistics."""
        platform = OpenAGI()
        stats = platform.get_platform_stats()
        
        assert "total_features" in stats
        assert "categories" in stats
        assert "category_breakdown" in stats
        assert "version" in stats
    
    def test_feature_execution(self):
        """Test feature execution."""
        platform = OpenAGI()
        feature = MockFeature()
        platform.registry.register(feature)
        
        result = platform.execute_feature("mock_feature", "test_arg", test_kwarg="test_value")
        
        assert result["result"] == "mock_executed"
        assert "test_arg" in result["args"]
        assert result["kwargs"]["test_kwarg"] == "test_value"
    
    def test_feature_execution_not_found(self):
        """Test feature execution with non-existent feature."""
        platform = OpenAGI()
        
        with pytest.raises(ValueError, match="Feature 'nonexistent' not found"):
            platform.execute_feature("nonexistent")


if __name__ == "__main__":
    pytest.main([__file__])