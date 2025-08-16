"""
Services package initialization
Import order matters! Service modules must be imported before service_registry
"""
import logging
logger = logging.getLogger(__name__)

# First, import all service modules to ensure they're available
# when service_registry tries to instantiate them
logger.info("services/__init__.py: Starting service module imports")

# Import base classes first
try:
    from . import base_analyzer
    logger.info("services/__init__.py: base_analyzer imported")
except ImportError as e:
    logger.error(f"services/__init__.py: Failed to import base_analyzer: {e}")

# Then import all service implementations
service_modules = [
    'article_extractor',
    'source_credibility', 
    'author_analyzer',
    'bias_detector',
    'fact_checker',
    'transparency_analyzer',
    'manipulation_detector',
    'content_analyzer',
    'plagiarism_detector'
]

for module_name in service_modules:
    try:
        exec(f"from . import {module_name}")
        logger.info(f"services/__init__.py: {module_name} module imported successfully")
    except ImportError as e:
        logger.error(f"services/__init__.py: Failed to import {module_name}: {e}")

# Now it's safe to import service_registry and pipeline
# as all service modules are loaded
try:
    from .service_registry import service_registry
    logger.info("services/__init__.py: service_registry imported successfully")
except ImportError as e:
    logger.error(f"services/__init__.py: Failed to import service_registry: {e}")

try:
    from .analysis_pipeline import pipeline
    logger.info("services/__init__.py: analysis_pipeline imported successfully")
except ImportError as e:
    logger.error(f"services/__init__.py: Failed to import analysis_pipeline: {e}")

# Export the main components
__all__ = [
    'service_registry',
    'pipeline',
    'base_analyzer',
    'BaseAnalyzer',
    'AsyncBaseAnalyzer'
]

logger.info("services/__init__.py: Package initialization complete")
