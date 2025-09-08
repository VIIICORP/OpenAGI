"""
Unit tests for OpenAGI NLP features
"""

import pytest
from openagi.features.nlp import (
    TextTokenizer, SentimentAnalyzer, KeywordExtractor, 
    LanguageDetector, TextCleaner
)


class TestTextTokenizer:
    """Test cases for TextTokenizer feature."""
    
    def test_word_tokenization(self):
        """Test word tokenization."""
        tokenizer = TextTokenizer()
        result = tokenizer.execute("Hello world, this is a test!", method="word")
        
        assert result["method"] == "word"
        assert result["count"] == 6
        assert "hello" in result["tokens"]
        assert "world" in result["tokens"]
    
    def test_sentence_tokenization(self):
        """Test sentence tokenization."""
        tokenizer = TextTokenizer()
        result = tokenizer.execute("First sentence. Second sentence! Third?", method="sentence")
        
        assert result["method"] == "sentence"
        assert result["count"] == 3
        assert "First sentence" in result["tokens"]


class TestSentimentAnalyzer:
    """Test cases for SentimentAnalyzer feature."""
    
    def test_positive_sentiment(self):
        """Test positive sentiment detection."""
        analyzer = SentimentAnalyzer()
        result = analyzer.execute("I love this amazing product!")
        
        assert result["sentiment"] == "positive"
        assert result["confidence"] > 0.5
        assert result["positive_signals"] > 0
    
    def test_negative_sentiment(self):
        """Test negative sentiment detection."""
        analyzer = SentimentAnalyzer()
        result = analyzer.execute("This is terrible and awful!")
        
        assert result["sentiment"] == "negative"
        assert result["confidence"] > 0.5
        assert result["negative_signals"] > 0
    
    def test_neutral_sentiment(self):
        """Test neutral sentiment detection."""
        analyzer = SentimentAnalyzer()
        result = analyzer.execute("This is a statement about something.")
        
        assert result["sentiment"] == "neutral"
        assert result["positive_signals"] == 0
        assert result["negative_signals"] == 0


class TestKeywordExtractor:
    """Test cases for KeywordExtractor feature."""
    
    def test_keyword_extraction(self):
        """Test keyword extraction."""
        extractor = KeywordExtractor()
        result = extractor.execute("artificial intelligence machine learning artificial intelligence")
        
        assert len(result["keywords"]) > 0
        assert result["total_words"] > 0
        
        # Check that "artificial" and "intelligence" are extracted
        keyword_words = [kw["word"] for kw in result["keywords"]]
        assert "artificial" in keyword_words
        assert "intelligence" in keyword_words
    
    def test_max_keywords_limit(self):
        """Test max keywords limitation."""
        extractor = KeywordExtractor()
        result = extractor.execute(
            "word1 word2 word3 word4 word5 word6", 
            max_keywords=3
        )
        
        assert len(result["keywords"]) <= 3


class TestLanguageDetector:
    """Test cases for LanguageDetector feature."""
    
    def test_english_detection(self):
        """Test English language detection."""
        detector = LanguageDetector()
        result = detector.execute("The quick brown fox jumps over the lazy dog")
        
        assert result["language"] == "english"
        assert result["confidence"] > 0


class TestTextCleaner:
    """Test cases for TextCleaner feature."""
    
    def test_lowercase_cleaning(self):
        """Test lowercase text cleaning."""
        cleaner = TextCleaner()
        result = cleaner.execute("HELLO WORLD", lowercase=True)
        
        assert result["cleaned_text"] == "hello world"
        assert "lowercase" in result["operations_performed"]
    
    def test_punctuation_removal(self):
        """Test punctuation removal."""
        cleaner = TextCleaner()
        result = cleaner.execute("Hello, world!", remove_punctuation=True)
        
        assert "," not in result["cleaned_text"]
        assert "!" not in result["cleaned_text"]
        assert "remove_punctuation" in result["operations_performed"]


if __name__ == "__main__":
    pytest.main([__file__])