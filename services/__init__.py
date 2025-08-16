"""
Services package initialization
"""
import logging

logger = logging.getLogger(__name__)

# Import all service modules to ensure they're available when service_registry initializes
# This forces the modules to be loaded even if service_registry doesn't import them directly
try:
    from . import article_extractor
    logger.info("services/__init__.py: article_extractor module imported successfully")
except ImportError as e:
    logger.error(f"services/__init__.py: Failed to import article_extractor: {e}")

try:
    from . import source_credibility
    logger.info("services/__init__.py: source_credibility module imported successfully")
except ImportError as e:
    logger.error(f"services/__init__.py: Failed to import source_credibility: {e}")

try:
    from . import author_analyzer
    logger.info("services/__init__.py: author_analyzer module imported successfully")
except ImportError as e:
    logger.error(f"services/__init__.py: Failed to import author_analyzer: {e}")

try:
    from . import bias_detector
    logger.info("services/__init__.py: bias_detector module imported successfully")
except ImportError as e:
    logger.error(f"services/__init__.py: Failed to import bias_detector: {e}")

try:
    from . import fact_checker
    logger.info("services/__init__.py: fact_checker module imported successfully")
except ImportError as e:
    logger.error(f"services/__init__.py: Failed to import fact_checker: {e}")

try:
    from . import transparency_analyzer
    logger.info("services/__init__.py: transparency_analyzer module imported successfully")
except ImportError as e:
    logger.error(f"services/__init__.py: Failed to import transparency_analyzer: {e}")

try:
    from . import manipulation_detector
    logger.info("services/__init__.py: manipulation_detector module imported successfully")
except ImportError as e:
    logger.error(f"services/__init__.py: Failed to import manipulation_detector: {e}")

try:
    from . import content_analyzer
    logger.info("services/__init__.py: content_analyzer module imported successfully")
except ImportError as e:
    logger.error(f"services/__init__.py: Failed to import content_analyzer: {e}")

try:
    from . import plagiarism_detector
    logger.info("services/__init__.py: plagiarism_detector module imported successfully")
except ImportError as e:
    logger.error(f"services/__init__.py: Failed to import plagiarism_detector: {e}")

# Now import the service registry AFTER all services are imported
try:
    from .service_registry import service_registry
    logger.info("services/__init__.py: service_registry imported successfully")
except ImportError as e:
    logger.error(f"services/__init__.py: Failed to import service_registry: {e}")

# The service_registry will handle the actual registration
# We just need to ensure the modules are loaded
