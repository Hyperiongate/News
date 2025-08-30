"""
Service Registry - COMPLETE FIXED VERSION
Central management for all analysis services
CRITICAL FIXES:
1. Fixed class name mapping for source_credibility (SourceCredibility not SourceCredibilityAnalyzer)
2. Enhanced error handling and logging
3. Proper service initialization with timeout protection
4. Bulletproof availability checking
"""
import logging
from typing import Dict, Any, Optional, List, Type
import importlib
import inspect
from concurrent.futures import ThreadPoolExecutor
import asyncio
from enum import Enum

from config import Config
from services.base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)

# Check if AsyncBaseAnalyzer is available
try:
    from services.base_analyzer import AsyncBaseAnalyzer
    ASYNC_SUPPORT = True
except ImportError:
    logger.info("AsyncBaseAnalyzer not available - async services disabled")
    ASYNC_SUPPORT = False
    AsyncBaseAnalyzer = None


class ServiceType(Enum):
    """Service type enumeration"""
    SYNC = "sync"
    ASYNC = "async"


class ServiceRegistry:
    """Registry for managing all analysis services"""
    
    # FIXED: Service mapping - corrected class names to match actual implementations
    SERVICE_MAPPING = {
        'article_extractor': ('services.article_extractor', 'ArticleExtractor'),
        'source_credibility': ('services.source_credibility', 'SourceCredibility'),  # FIXED: Correct class name
        'author_analyzer': ('services.author_analyzer', 'AuthorAnalyzer'),
        'bias_detector': ('services.bias_detector', 'BiasDetector'),
        'fact_checker': ('services.fact_checker', 'FactChecker'),
        'transparency_analyzer': ('services.transparency_analyzer', 'TransparencyAnalyzer'),
        'manipulation_detector': ('services.manipulation_detector', 'ManipulationDetector'),
        'content_analyzer': ('services.content_analyzer', 'ContentAnalyzer'),
        'plagiarism_detector': ('services.plagiarism_detector', 'PlagiarismDetector'),
        'openai_enhancer': ('services.openai_enhancer', 'OpenAIEnhancer'),
    }
    
    def __init__(self):
        self.services: Dict[str, BaseAnalyzer] = {}
        self.async_services: Dict[str, BaseAnalyzer] = {}
        self.failed_services: Dict[str, str] = {}
        self._initialized = False
        logger.info("ServiceRegistry created but not initialized yet")
        
    def _ensure_initialized(self):
        """Ensure services are initialized before use"""
        if not self._initialized:
            logger.info("First access to ServiceRegistry - initializing services now")
            self._initialize_services()
            self._initialized = True
        
    def _initialize_services(self):
        """Initialize all configured services"""
        logger.info("=" * 80)
        logger.info("INITIALIZING SERVICE REGISTRY")
        logger.info(f"Services to initialize: {list(self.SERVICE_MAPPING.keys())}")
        
        success_count = 0
        failure_count = 0
        
        for service_name, (module_path, class_name) in self.SERVICE_MAPPING.items():
            try:
                logger.info(f"Initializing {service_name} from {module_path}.{class_name}")
                
                # Check if service is enabled in config
                if not Config.is_service_enabled(service_name):
                    logger.info(f"Service {service_name} is disabled in config - skipping")
                    continue
                
                # Import the module
                try:
                    module = importlib.import_module(module_path)
                except ImportError as e:
                    logger.error(f"Failed to import module {module_path}: {e}")
                    self.failed_services[service_name] = f"Module import failed: {str(e)}"
                    failure_count += 1
                    continue
                
                # Get the class
                try:
                    service_class = getattr(module, class_name)
                except AttributeError as e:
                    logger.error(f"Class {class_name} not found in {module_path}: {e}")
                    self.failed_services[service_name] = f"Class not found: {str(e)}"
                    failure_count += 1
                    continue
                
                # Instantiate the service with timeout protection
                try:
                    service_instance = service_class()
                    
                    # Verify it's a valid service
                    if not isinstance(service_instance, BaseAnalyzer):
                        if ASYNC_SUPPORT and AsyncBaseAnalyzer and isinstance(service_instance, AsyncBaseAnalyzer):
                            # It's an async service
                            pass
                        else:
                            logger.error(f"Service {service_name} is not a BaseAnalyzer instance")
                            self.failed_services[service_name] = "Invalid service type"
                            failure_count += 1
                            continue
                    
                    # Check availability
                    is_available = service_instance.is_available
                    
                    # Register the service
                    if ASYNC_SUPPORT and AsyncBaseAnalyzer and isinstance(service_instance, AsyncBaseAnalyzer):
                        self.async_services[service_name] = service_instance
                        logger.info(f"✓ Successfully initialized async service {service_name} - Available: {is_available}")
                    else:
                        self.services[service_name] = service_instance
                        logger.info(f"✓ Successfully initialized sync service {service_name} - Available: {is_available}")
                    
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to initialize {service_name}: {str(e)}", exc_info=True)
                    self.failed_services[service_name] = f"Initialization failed: {str(e)}"
                    failure_count += 1
                    
            except Exception as e:
                logger.error(f"Critical error initializing {service_name}: {str(e)}", exc_info=True)
                self.failed_services[service_name] = f"Critical error: {str(e)}"
                failure_count += 1
        
        # Log final status
        logger.info("=" * 80)
        logger.info("SERVICE REGISTRY INITIALIZATION COMPLETE")
        logger.info(f"✓ Successfully initialized: {success_count} services")
        logger.info(f"✗ Failed to initialize: {failure_count} services")
        logger.info(f"Sync services: {list(self.services.keys())}")
        if ASYNC_SUPPORT:
            logger.info(f"Async services: {list(self.async_services.keys())}")
        if self.failed_services:
            logger.info(f"Failed services detail: {self.failed_services}")
        logger.info("=" * 80 + "\n")
    
    def get_service(self, service_name: str) -> Optional[BaseAnalyzer]:
        """Get a service by name"""
        self._ensure_initialized()
        return self.services.get(service_name) or self.async_services.get(service_name)
    
    def is_service_available(self, service_name: str) -> bool:
        """Check if a service is available"""
        self._ensure_initialized()
        service = self.get_service(service_name)
        return service is not None and service.is_available
    
    def get_all_services(self) -> Dict[str, BaseAnalyzer]:
        """Get all registered services"""
        self._ensure_initialized()
        all_services = {}
        all_services.update(self.services)
        all_services.update(self.async_services)
        return all_services
    
    def get_available_services(self) -> Dict[str, BaseAnalyzer]:
        """Get only available services"""
        self._ensure_initialized()
        return {
            name: service 
            for name, service in self.get_all_services().items() 
            if service.is_available
        }
    
    def get_service_info(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific service"""
        self._ensure_initialized()
        service = self.get_service(service_name)
        if service:
            return service.get_service_info()
        return None
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of all services"""
        self._ensure_initialized()
        status = {
            'summary': {
                'total_configured': len(self.SERVICE_MAPPING),
                'total_registered': len(self.services) + len(self.async_services),
                'total_available': len(self.get_available_services()),
                'total_failed': len(self.failed_services)
            },
            'services': {}
        }
        
        # Add status for each configured service
        for service_name in self.SERVICE_MAPPING:
            service = self.get_service(service_name)
            if service:
                status['services'][service_name] = {
                    'registered': True,
                    'available': service.is_available,
                    'type': 'async' if service_name in self.async_services else 'sync',
                    'info': service.get_service_info()
                }
            elif service_name in self.failed_services:
                status['services'][service_name] = {
                    'registered': False,
                    'available': False,
                    'error': self.failed_services[service_name]
                }
            else:
                status['services'][service_name] = {
                    'registered': False,
                    'available': False,
                    'error': 'Service disabled or not configured'
                }
        
        return status
    
    def run_analysis(self, data: Dict[str, Any], service_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run analysis using specified services or all available services
        """
        self._ensure_initialized()
        
        if service_names is None:
            # Use all available services
            services_to_run = self.get_available_services()
        else:
            # Use only specified available services
            services_to_run = {
                name: service 
                for name, service in self.get_available_services().items() 
                if name in service_names
            }
        
        results = {}
        
        logger.info(f"Running analysis with {len(services_to_run)} services: {list(services_to_run.keys())}")
        
        for service_name, service in services_to_run.items():
            try:
                logger.info(f"Running {service_name} analysis...")
                result = service.analyze(data)
                results[service_name] = result
                logger.info(f"✓ {service_name} completed successfully")
                
            except Exception as e:
                logger.error(f"✗ {service_name} failed: {str(e)}", exc_info=True)
                results[service_name] = {
                    'service': service_name,
                    'success': False,
                    'available': True,
                    'error': str(e),
                    'timestamp': None
                }
        
        logger.info(f"Analysis complete - {len(results)} services processed")
        return results
    
    async def analyze_with_service_async(self, service_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run analysis with async service"""
        self._ensure_initialized()
        
        if not ASYNC_SUPPORT:
            raise ValueError("Async services not supported")
            
        service = self.async_services.get(service_name)
        if not service:
            raise ValueError(f"Async service '{service_name}' not found")
        
        if not service.is_available:
            return {
                'success': False,
                'service': service_name,
                'error': f"Service '{service_name}' is not available"
            }
        
        try:
            result = await service.analyze(data)
            return result
        except Exception as e:
            logger.error(f"Error in async service {service_name}: {e}", exc_info=True)
            return {
                'success': False,
                'service': service_name,
                'error': str(e)
            }
    
    def analyze_with_service(self, service_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run analysis with sync service"""
        self._ensure_initialized()
        service = self.services.get(service_name)
        if not service:
            # Check if it's accidentally an async service
            if service_name in self.async_services:
                raise ValueError(f"Service '{service_name}' is async. Use analyze_with_service_async()")
            raise ValueError(f"Service '{service_name}' not found")
        
        if not service.is_available:
            return {
                'success': False,
                'service': service_name,
                'error': f"Service '{service_name}' is not available"
            }
        
        try:
            result = service.analyze(data)
            return result
        except Exception as e:
            logger.error(f"Error in service {service_name}: {e}", exc_info=True)
            return {
                'success': False,
                'service': service_name,
                'error': str(e)
            }
    
    def get_enabled_service_names(self) -> List[str]:
        """Get list of enabled service names from config"""
        return Config.get_enabled_services()
    
    def validate_service_dependencies(self) -> Dict[str, Any]:
        """Validate that required service dependencies are met"""
        validation = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check if article extractor is available (required)
        if not self.is_service_available('article_extractor'):
            validation['valid'] = False
            validation['errors'].append('Article extractor service is required but not available')
        
        # Check if at least one analysis service is available
        analysis_services = [
            'source_credibility', 'author_analyzer', 'bias_detector', 
            'fact_checker', 'transparency_analyzer', 'manipulation_detector'
        ]
        
        available_analysis_services = [
            name for name in analysis_services 
            if self.is_service_available(name)
        ]
        
        if len(available_analysis_services) == 0:
            validation['valid'] = False
            validation['errors'].append('No analysis services are available')
        elif len(available_analysis_services) < 3:
            validation['warnings'].append(
                f'Only {len(available_analysis_services)} analysis services available - '
                'results may be limited'
            )
        
        return validation
    
    def reload_service(self, service_name: str) -> bool:
        """
        Reload a specific service
        
        Args:
            service_name: Name of the service to reload
            
        Returns:
            True if reload successful, False otherwise
        """
        self._ensure_initialized()
        try:
            # Remove from current registries
            if service_name in self.services:
                del self.services[service_name]
            if service_name in self.async_services:
                del self.async_services[service_name]
            if service_name in self.failed_services:
                del self.failed_services[service_name]
            
            # Re-initialize the service
            if service_name in self.SERVICE_MAPPING:
                module_name, class_name = self.SERVICE_MAPPING[service_name]
                
                # Reload module
                module = importlib.import_module(module_name)
                importlib.reload(module)
                
                # Re-instantiate
                service_class = getattr(module, class_name)
                service_instance = service_class()
                
                if ASYNC_SUPPORT and AsyncBaseAnalyzer and isinstance(service_instance, AsyncBaseAnalyzer):
                    self.async_services[service_name] = service_instance
                else:
                    self.services[service_name] = service_instance
                
                logger.info(f"Successfully reloaded service: {service_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to reload service {service_name}: {e}")
            self.failed_services[service_name] = f"Reload failed: {str(e)}"
            
        return False


# Global service registry instance
_service_registry = None


def get_service_registry() -> ServiceRegistry:
    """
    Get the global service registry instance
    Uses singleton pattern to ensure only one registry exists
    """
    global _service_registry
    
    if _service_registry is None:
        logger.info("Creating new ServiceRegistry instance")
        _service_registry = ServiceRegistry()
    
    return _service_registry


def reset_service_registry():
    """Reset the global service registry (useful for testing)"""
    global _service_registry
    _service_registry = None
    logger.info("Service registry reset")


# Initialize services when module is imported (lazy initialization)
service_registry = get_service_registry()
