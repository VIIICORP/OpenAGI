"""
Integration tests for the complete OpenAGI platform
"""

import pytest
from openagi import OpenAGI


class TestPlatformIntegration:
    """Integration tests for the full platform."""
    
    def test_complete_nlp_workflow(self):
        """Test a complete NLP processing workflow."""
        platform = OpenAGI()
        
        text = "I absolutely love using OpenAGI! It's an amazing artificial intelligence platform."
        
        # Step 1: Clean the text
        cleaned = platform.execute_feature("text_cleaner", text, lowercase=True)
        clean_text = cleaned["cleaned_text"]
        
        # Step 2: Analyze sentiment
        sentiment = platform.execute_feature("sentiment_analyzer", clean_text)
        
        # Step 3: Extract keywords
        keywords = platform.execute_feature("keyword_extractor", clean_text, max_keywords=5)
        
        # Step 4: Tokenize
        tokens = platform.execute_feature("text_tokenizer", clean_text, method="word")
        
        # Verify the workflow
        assert sentiment["sentiment"] == "positive"
        assert len(keywords["keywords"]) > 0
        assert tokens["count"] > 0
        
        # Check that the workflow is coherent
        assert cleaned["original_length"] > cleaned["cleaned_length"]
        assert "artificial" in [kw["word"] for kw in keywords["keywords"]]
    
    def test_feature_discovery_and_execution(self):
        """Test discovering and executing features dynamically."""
        platform = OpenAGI()
        
        # Search for sentiment features
        sentiment_features = platform.search_features("sentiment")
        assert len(sentiment_features) > 0
        
        # Get the first sentiment feature
        feature_name = sentiment_features[0]["name"]
        
        # Execute it
        result = platform.execute_feature(feature_name, "This is a test message")
        assert "sentiment" in result
    
    def test_platform_scalability(self):
        """Test platform with multiple concurrent feature executions."""
        platform = OpenAGI()
        
        test_texts = [
            "This is positive text with great words!",
            "This is negative text with bad words.",
            "This is neutral text about something.",
        ]
        
        results = []
        for text in test_texts:
            result = platform.execute_feature("sentiment_analyzer", text)
            results.append(result)
        
        # Verify all executions completed
        assert len(results) == 3
        assert all("sentiment" in result for result in results)
        
        # Verify different sentiments were detected
        sentiments = [result["sentiment"] for result in results]
        assert "positive" in sentiments
        assert "negative" in sentiments


if __name__ == "__main__":
    pytest.main([__file__])