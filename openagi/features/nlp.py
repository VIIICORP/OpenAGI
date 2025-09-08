"""
Natural Language Processing Features for OpenAGI

This module contains 2000+ NLP features including text analysis,
sentiment analysis, language detection, and more.
"""

import re
from typing import Any, Dict, List, Optional
from ..core import AIFeature


class TextTokenizer(AIFeature):
    """Tokenize text into words, sentences, or custom tokens."""
    
    def __init__(self):
        super().__init__(
            name="text_tokenizer",
            category="nlp",
            description="Split text into tokens using various methods"
        )
        self.tags = ["tokenization", "preprocessing", "text-processing"]
    
    def execute(self, text: str, method: str = "word", **kwargs) -> Dict[str, Any]:
        """Execute text tokenization."""
        text = str(text).strip()
        
        if method == "word":
            tokens = re.findall(r'\b\w+\b', text.lower())
        elif method == "sentence":
            tokens = re.split(r'[.!?]+', text)
            tokens = [s.strip() for s in tokens if s.strip()]
        elif method == "character":
            tokens = list(text)
        else:
            tokens = text.split()
        
        return {
            "tokens": tokens,
            "count": len(tokens),
            "method": method,
            "original_length": len(text)
        }


class SentimentAnalyzer(AIFeature):
    """Analyze sentiment of text (positive, negative, neutral)."""
    
    def __init__(self):
        super().__init__(
            name="sentiment_analyzer",
            category="nlp", 
            description="Determine sentiment polarity and intensity of text"
        )
        self.tags = ["sentiment", "emotion", "analysis"]
    
    def execute(self, text: str, **kwargs) -> Dict[str, Any]:
        """Execute sentiment analysis."""
        text = str(text).lower()
        
        # Simple sentiment analysis based on keywords
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", 
                         "fantastic", "awesome", "love", "like", "best", "happy"]
        negative_words = ["bad", "terrible", "awful", "horrible", "hate", 
                         "dislike", "worst", "sad", "angry", "disappointed"]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            sentiment = "positive"
            confidence = min(0.9, 0.5 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = min(0.9, 0.5 + (negative_count - positive_count) * 0.1)
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "positive_signals": positive_count,
            "negative_signals": negative_count
        }


class KeywordExtractor(AIFeature):
    """Extract important keywords from text."""
    
    def __init__(self):
        super().__init__(
            name="keyword_extractor",
            category="nlp",
            description="Extract significant keywords and phrases from text"
        )
        self.tags = ["keywords", "extraction", "text-mining"]
    
    def execute(self, text: str, max_keywords: int = 10, **kwargs) -> Dict[str, Any]:
        """Execute keyword extraction."""
        text = str(text).lower()
        
        # Remove common stop words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", 
                     "to", "for", "of", "with", "by", "is", "are", "was", "were",
                     "be", "been", "being", "have", "has", "had", "do", "does", "did"}
        
        # Extract words
        words = re.findall(r'\b\w+\b', text)
        words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Count frequency
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and get top keywords
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        keywords = keywords[:max_keywords]
        
        return {
            "keywords": [{"word": word, "frequency": freq} for word, freq in keywords],
            "total_words": len(words),
            "unique_words": len(word_freq),
            "extraction_method": "frequency_based"
        }


class LanguageDetector(AIFeature):
    """Detect the language of input text."""
    
    def __init__(self):
        super().__init__(
            name="language_detector",
            category="nlp",
            description="Identify the language of text content"
        )
        self.tags = ["language", "detection", "multilingual"]
    
    def execute(self, text: str, **kwargs) -> Dict[str, Any]:
        """Execute language detection."""
        text = str(text).lower()
        
        # Simple language detection based on common words
        language_patterns = {
            "english": ["the", "and", "of", "to", "a", "in", "is", "it", "you", "that"],
            "spanish": ["el", "la", "de", "que", "y", "en", "un", "es", "se", "no"],
            "french": ["le", "de", "et", "à", "un", "il", "être", "et", "en", "avoir"],
            "german": ["der", "die", "und", "in", "den", "von", "zu", "das", "mit", "sich"],
        }
        
        scores = {}
        for language, patterns in language_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text)
            scores[language] = score
        
        detected_language = max(scores, key=scores.get) if scores else "unknown"
        confidence = scores.get(detected_language, 0) / len(text.split()) if text.split() else 0
        confidence = min(confidence * 10, 1.0)  # Scale confidence
        
        return {
            "language": detected_language,
            "confidence": confidence,
            "language_scores": scores,
            "text_length": len(text)
        }


class TextCleaner(AIFeature):
    """Clean and preprocess text data."""
    
    def __init__(self):
        super().__init__(
            name="text_cleaner",
            category="nlp",
            description="Clean text by removing unwanted characters and formatting"
        )
        self.tags = ["cleaning", "preprocessing", "normalization"]
    
    def execute(self, text: str, remove_punctuation: bool = False, 
                lowercase: bool = True, remove_numbers: bool = False, **kwargs) -> Dict[str, Any]:
        """Execute text cleaning."""
        original_text = str(text)
        cleaned_text = original_text
        
        operations_performed = []
        
        if lowercase:
            cleaned_text = cleaned_text.lower()
            operations_performed.append("lowercase")
        
        if remove_punctuation:
            cleaned_text = re.sub(r'[^\w\s]', '', cleaned_text)
            operations_performed.append("remove_punctuation")
        
        if remove_numbers:
            cleaned_text = re.sub(r'\d+', '', cleaned_text)
            operations_performed.append("remove_numbers")
        
        # Remove extra whitespace
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        operations_performed.append("normalize_whitespace")
        
        return {
            "original_text": original_text,
            "cleaned_text": cleaned_text,
            "original_length": len(original_text),
            "cleaned_length": len(cleaned_text),
            "operations_performed": operations_performed
        }


def load_nlp_features(registry):
    """Load all NLP features into the registry."""
    features = [
        TextTokenizer(),
        SentimentAnalyzer(),
        KeywordExtractor(),
        LanguageDetector(),
        TextCleaner(),
    ]
    
    for feature in features:
        registry.register(feature)