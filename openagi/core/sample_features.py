#!/usr/bin/env python3
"""
Sample Features for OpenAGI Platform

This module contains sample AI features for demonstration purposes.
"""

from typing import Any, Dict, List
import logging
from ..core.feature import AIFeature

logger = logging.getLogger(__name__)


class TextTokenizerFeature(AIFeature):
    """Sample text tokenization feature."""
    
    def __init__(self):
        super().__init__(
            name="text_tokenizer",
            category="nlp",
            description="Tokenizes text into words, sentences, or subwords"
        )
    
    def execute(self, text: str, method: str = "word") -> Dict[str, Any]:
        """
        Tokenize input text.
        
        Args:
            text: Input text to tokenize
            method: Tokenization method ('word', 'sentence', 'char')
            
        Returns:
            Dictionary with tokenization results
        """
        if method == "word":
            tokens = text.split()
        elif method == "sentence":
            tokens = text.split('.')
            tokens = [t.strip() for t in tokens if t.strip()]
        elif method == "char":
            tokens = list(text)
        else:
            raise ValueError(f"Unsupported tokenization method: {method}")
        
        return {
            "tokens": tokens,
            "count": len(tokens),
            "method": method,
            "original_text": text
        }


class SentimentAnalysisFeature(AIFeature):
    """Sample sentiment analysis feature."""
    
    def __init__(self):
        super().__init__(
            name="sentiment_analysis",
            category="nlp", 
            description="Analyzes sentiment of text (positive, negative, neutral)"
        )
    
    def execute(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of input text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with sentiment analysis results
        """
        # Simple rule-based sentiment analysis for demo
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "love", "like"]
        negative_words = ["bad", "terrible", "awful", "hate", "dislike", "worst"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
            confidence = min(0.6 + (positive_count - negative_count) * 0.1, 0.95)
        elif negative_count > positive_count:
            sentiment = "negative"  
            confidence = min(0.6 + (negative_count - positive_count) * 0.1, 0.95)
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "positive_indicators": positive_count,
            "negative_indicators": negative_count,
            "text": text
        }


class ImageClassificationFeature(AIFeature):
    """Sample image classification feature."""
    
    def __init__(self):
        super().__init__(
            name="image_classification",
            category="computer_vision",
            description="Classifies images into predefined categories"
        )
    
    def execute(self, image_path: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Classify input image.
        
        Args:
            image_path: Path to input image
            top_k: Number of top predictions to return
            
        Returns:
            Dictionary with classification results
        """
        # Mock classification results for demo
        mock_predictions = [
            {"label": "cat", "confidence": 0.85},
            {"label": "dog", "confidence": 0.12},
            {"label": "bird", "confidence": 0.02},
            {"label": "fish", "confidence": 0.01},
        ]
        
        return {
            "predictions": mock_predictions[:top_k],
            "image_path": image_path,
            "top_prediction": mock_predictions[0]["label"],
            "confidence": mock_predictions[0]["confidence"]
        }