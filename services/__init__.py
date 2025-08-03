"""
services/__init__.py
Makes the services directory a Python package and handles imports
"""

__version__ = "2.1.0"
__service__ = "news-analyzer-enhanced"

# Import all service classes for easy access
__all__ = [
    # Core services - USE ACTUAL CLASS NAMES
    'ArticleExtractor',
    'AuthorAnalyzer',
    'BiasAnalyzer',
    'ClickbaitDetector',
    'FactChecker',
    'SourceCredibility',  # FIXED: Changed from SourceCredibilityAnalyzer
    'TransparencyAnalyzer',
    'ContentAnalyzer',
    'ManipulationDetector',
    'ReadabilityAnalyzer',
    'EmotionAnalyzer',
    'ClaimExtractor',
    'ImageAnalyzer',
    'NetworkAnalyzer',
    'PDFGenerator',
    'ReportGenerator',
    # Enhanced services
    'EnhancedContextAnalyzer',
    'EconomicFactChecker',
    'OriginalityAnalyzer',
    # Additional services
    'NewsAnalyzer'    # Removed NewsExtractor since it doesn't exist
]

# Try to import all services
try:
    from .article_extractor import ArticleExtractor
except ImportError:
    pass

try:
    from .author_analyzer import AuthorAnalyzer
except ImportError:
    pass

try:
    from .bias_analyzer import BiasAnalyzer
except ImportError:
    pass

try:
    from .clickbait_detector import ClickbaitDetector
except ImportError:
    pass

try:
    from .fact_checker import FactChecker
except ImportError:
    pass

try:
    from .source_credibility import SourceCredibility  # FIXED: Correct class name
except ImportError:
    pass

try:
    from .transparency_analyzer import TransparencyAnalyzer
except ImportError:
    pass

try:
    from .content_analyzer import ContentAnalyzer
except ImportError:
    pass

try:
    from .manipulation_detector import ManipulationDetector
except ImportError:
    pass

try:
    from .readability_analyzer import ReadabilityAnalyzer
except ImportError:
    pass

try:
    from .emotion_analyzer import EmotionAnalyzer
except ImportError:
    pass

try:
    from .claim_extractor import ClaimExtractor
except ImportError:
    pass

try:
    from .image_analyzer import ImageAnalyzer
except ImportError:
    pass

try:
    from .network_analyzer import NetworkAnalyzer
except ImportError:
    pass

try:
    from .pdf_generator import PDFGenerator
except ImportError:
    pass

try:
    from .report_generator import ReportGenerator
except ImportError:
    pass

# Import additional services
try:
    from .news_analyzer import NewsAnalyzer
except ImportError:
    pass

# Import new enhanced services
try:
    from .enhanced_context_analyzer import EnhancedContextAnalyzer
except ImportError:
    pass

try:
    from .economic_fact_checker import EconomicFactChecker
except ImportError:
    pass

try:
    from .originality_analyzer import OriginalityAnalyzer
except ImportError:
    pass
