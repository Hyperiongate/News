"""
Create this file as services/__init__.py
This ensures all services can be imported properly
"""

# This file makes the services directory a Python package
# It can be empty, but we'll import all services to ensure they're available

# Import all service classes to ensure they're accessible
from .base_analyzer import BaseAnalyzer, AsyncBaseAnalyzer
from .article_extractor import ArticleExtractor
from .source_credibility import SourceCredibility
from .author_analyzer import AuthorAnalyzer
from .bias_detector import BiasDetector
from .fact_checker import FactChecker
from .transparency_analyzer import TransparencyAnalyzer
from .manipulation_detector import ManipulationDetector
from .content_analyzer import ContentAnalyzer

__all__ = [
    'BaseAnalyzer',
    'AsyncBaseAnalyzer',
    'ArticleExtractor',
    'SourceCredibility', 
    'AuthorAnalyzer',
    'BiasDetector',
    'FactChecker',
    'TransparencyAnalyzer',
    'ManipulationDetector',
    'ContentAnalyzer'
]
