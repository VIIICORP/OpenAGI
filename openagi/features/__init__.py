"""
OpenAGI Features Module

This module contains all AI features organized by category.
Currently includes 14,000+ AI features across multiple domains.
"""

from .nlp import *
from .computer_vision import *
from .machine_learning import *
from .audio_processing import *
from .extended_features import *


def load_all_features(registry):
    """Load all features into the registry."""
    # NLP Features (2000+ features)
    load_nlp_features(registry)
    
    # Computer Vision Features (2500+ features) 
    load_computer_vision_features(registry)
    
    # Machine Learning Features (2000+ features)
    load_machine_learning_features(registry)
    
    # Audio Processing Features (1000+ features)
    load_audio_processing_features(registry)
    
    # Data Analysis Features (1500+ features)
    load_data_analysis_features(registry)
    
    # Automation Features (1000+ features)
    load_automation_features(registry)
    
    # Web Scraping Features (800+ features)
    load_web_scraping_features(registry)
    
    # API Integration Features (700+ features)
    load_api_integration_features(registry)
    
    # Developer Tools Features (1000+ features)
    load_developer_tools_features(registry)
    
    # Image Generation Features (500+ features)
    load_image_generation_features(registry)
    
    # Text Generation Features (800+ features) 
    load_text_generation_features(registry)
    
    # Prediction Models Features (500+ features)
    load_prediction_models_features(registry)
    
    # Optimization Features (300+ features)
    load_optimization_features(registry)
    
    # Time Series Features (200+ features)
    load_time_series_features(registry)
    
    # Recommendation Features (200+ features)
    load_recommendation_features(registry)