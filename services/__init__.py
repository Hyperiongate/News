"""
Services package initialization - ROBUST VERSION
Date: September 6, 2025

This ensures all services are properly imported and registered
"""
import logging

logger = logging.getLogger(__name__)

# CRITICAL: Import service registry first to create the singleton
try:
    from .service_registry import get_service_registry
    logger.info("✓ service_registry imported")
except ImportError as e:
    logger.error(f"✗ Failed to import service_registry: {e}")
    get_service_registry = None

# Force registration of article_extractor by importing and instantiating it
try:
    from .article_extractor import ArticleExtractor
    # Create instance to force registration
    _article_extractor_instance = ArticleExtractor()
    logger.info(f"✓ ArticleExtractor imported and instantiated - available: {_article_extractor_instance.available}")
    
    # Register with the service registry if it exists
    if get_service_registry:
        registry = get_service_registry()
        registry.services['article_extractor'] = _article_extractor_instance
        logger.info("✓ ArticleExtractor manually registered with service registry")
except Exception as e:
    logger.error(f"✗ Failed to import/register ArticleExtractor: {e}", exc_info=True)

# Import other services (optional - they can fail)
services_to_import = [
    'source_credibility',
    'author_analyzer',
    'bias_detector',
    'fact_checker',
    'transparency_analyzer',
    'manipulation_detector',
    'content_analyzer',
    'plagiarism_detector',
    'openai_enhancer'
]

for service in services_to_import:
    try:
        exec(f"from . import {service}")
        logger.info(f"  ✓ {service} module imported")
    except ImportError as e:
        logger.warning(f"  ⚠ {service} not available: {e}")

# Export the registry
__all__ = ['get_service_registry']
