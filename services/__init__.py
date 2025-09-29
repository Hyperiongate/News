"""
Services package initialization
Date: September 28, 2025

Simple initialization that doesn't interfere with the service registry
"""

import logging

logger = logging.getLogger(__name__)

# Import the service registry getter
try:
    from .service_registry import get_service_registry
    logger.info("Services package initialized - registry available")
except ImportError as e:
    logger.error(f"Failed to import service registry: {e}")
    get_service_registry = None

# That's it - don't manually import or register services
# The registry will handle all service loading automatically

__all__ = ['get_service_registry']
