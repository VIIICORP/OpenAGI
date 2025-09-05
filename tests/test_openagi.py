"""
OpenAGI Test Suite

Basic tests to verify platform functionality.
"""

import pytest
import numpy as np
from openagi import OpenAGI, FeatureRegistry
from openagi.core import AIFeature


class DummyFeature(AIFeature):
    """Dummy feature for testing."""
    
    def __init__(self):
        super().__init__("dummy_feature", "test", "A dummy feature for testing")
    
    def execute(self, *args, **kwargs):
        return {"status": "success", "args": args, "kwargs": kwargs}


def test_platform_initialization():
    """Test that the platform initializes correctly."""
    platform = OpenAGI()
    assert platform is not None
    assert platform.registry is not None


def test_feature_registry():
    """Test feature registry functionality."""
    registry = FeatureRegistry()
    
    # Test registration
    dummy_feature = DummyFeature()
    registry.register(dummy_feature)
    
    # Test retrieval
    retrieved = registry.get_feature("dummy_feature")
    assert retrieved is not None
    assert retrieved.name == "dummy_feature"
    
    # Test listing
    features = registry.list_features()
    assert "dummy_feature" in features
    
    # Test categories
    categories = registry.list_categories()
    assert "test" in categories


def test_platform_stats():
    """Test platform statistics."""
    platform = OpenAGI()
    stats = platform.get_platform_stats()
    
    assert "total_features" in stats
    assert "categories" in stats
    assert "category_breakdown" in stats
    assert stats["total_features"] > 0


def test_feature_search():
    """Test feature search functionality."""
    platform = OpenAGI()
    
    # Search for text-related features
    results = platform.search_features("text")
    assert len(results) > 0
    
    # Each result should have required fields
    for result in results:
        assert "name" in result
        assert "category" in result
        assert "description" in result


def test_feature_execution():
    """Test feature execution."""
    platform = OpenAGI()
    
    # Test NLP feature
    result = platform.execute_feature("text_tokenizer", "hello world", method="word")
    assert result is not None
    
    # Test with invalid feature
    with pytest.raises(ValueError):
        platform.execute_feature("nonexistent_feature")


def test_nlp_features():
    """Test NLP feature functionality."""
    platform = OpenAGI()
    
    text = "This is a test sentence for OpenAGI."
    
    # Test sentiment analysis
    sentiment = platform.execute_feature("sentiment_analyzer", text)
    assert "positive" in sentiment
    assert "negative" in sentiment
    assert "neutral" in sentiment
    
    # Test keyword extraction
    keywords = platform.execute_feature("keyword_extractor", text, max_keywords=3)
    assert isinstance(keywords, list)
    
    # Test language detection
    language = platform.execute_feature("language_detector", text)
    assert "language" in language
    assert "confidence" in language


def test_computer_vision_features():
    """Test computer vision features."""
    platform = OpenAGI()
    
    # Create a test image
    image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    
    # Test object detection
    objects = platform.execute_feature("object_detector", image)
    assert isinstance(objects, list)
    
    # Test face detection
    faces = platform.execute_feature("face_detector", image)
    assert isinstance(faces, list)
    
    # Test image enhancement
    enhanced = platform.execute_feature("image_enhancer", image, enhancement_type="contrast")
    assert enhanced.shape == image.shape


def test_machine_learning_features():
    """Test machine learning features."""
    platform = OpenAGI()
    
    # Generate test data
    X = np.random.randn(50, 4)
    y = np.random.randint(0, 2, 50)
    
    # Test clustering
    cluster_result = platform.execute_feature("kmeans_clusterer", X, k=3)
    assert "labels" in cluster_result
    assert "centroids" in cluster_result
    assert len(cluster_result["labels"]) == len(X)
    
    # Test PCA
    pca_result = platform.execute_feature("pca_reducer", X, n_components=2)
    assert "transformed_data" in pca_result
    assert "explained_variance_ratio" in pca_result


def test_audio_processing_features():
    """Test audio processing features."""
    platform = OpenAGI()
    
    # Generate test audio
    audio = np.random.randn(1000)
    
    # Test audio feature extraction
    features = platform.execute_feature("audio_feature_extractor", audio, sample_rate=44100)
    assert "duration" in features
    assert "rms_energy" in features
    assert "mfccs" in features
    
    # Test audio enhancement
    enhanced = platform.execute_feature("audio_enhancer", audio, enhancement_type="normalize")
    assert enhanced.shape == audio.shape


if __name__ == "__main__":
    pytest.main([__file__])