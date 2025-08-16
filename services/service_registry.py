"""
Service Registry
Central management for all analysis services
"""
import logging
from typing import Dict, Any, Optional, List, Type
import importlib
import inspect
from concurrent.futures import ThreadPoolExecutor
import asyncio

from config import Config
from services.base_analyzer import BaseAnalyzer, AsyncBaseAnalyzer

logger = logging.getLogger(__name__)


class ServiceRegistry:
    """Registry for managing all analysis services"""
    
    # Service mapping - maps service names to their module and class names
    SERVICE_MAPPING = {
        'article_extractor': ('services.article_extractor', 'ArticleExtractor'),
        'source_credibility': ('services.source_credibility', 'SourceCredibility'),
        'author_analyzer': ('services.author_analyzer', 'AuthorAnalyzer'),
        'bias_detector': ('services.bias_detector', 'BiasDetector'),
        'fact_checker': ('services.fact_checker', 'FactChecker'),
        'transparency_analyzer': ('services.transparency_analyzer', 'TransparencyAnalyzer'),
        'manipulation_detector': ('services.manipulation_detector', 'ManipulationDetector'),
        'content_analyzer': ('services.content_analyzer', 'ContentAnalyzer'),
        'plagiarism_detector': ('services.plagiarism_detector', 'PlagiarismDetector'),
    }
    
    def __init__(self):
        self.services: Dict[str, BaseAnalyzer] = {}
        self.async_services: Dict[str, AsyncBaseAnalyzer] = {}
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
        logger.info("STARTING SERVICE REGISTRY INITIALIZATION")
        logger.info("=" * 80)
        
        # First, try to import all service modules to ensure they're loaded
        logger.info("Phase 1: Pre-importing all service modules...")
        for service_name, (module_name, class_name) in self.SERVICE_MAPPING.items():
            try:
                logger.info(f"Pre-importing {module_name}...")
                importlib.import_module(module_name)
                logger.info(f"✓ Successfully pre-imported {module_name}")
            except Exception as e:
                logger.error(f"✗ Failed to pre-import {module_name}: {e}")
        
        logger.info("\nPhase 2: Instantiating services...")
        
        for service_name, (module_name, class_name) in self.SERVICE_MAPPING.items():
            logger.info(f"\n--- Processing {service_name} ---")
            
            # Check if service is enabled in config
            if not Config.is_service_enabled(service_name):
                logger.info(f"Service {service_name} is disabled in configuration")
                continue
                
            try:
                # Import the module
                logger.info(f"Importing module {module_name}...")
                module = importlib.import_module(module_name)
                
                # Get the class
                logger.info(f"Getting class {class_name} from module...")
                if not hasattr(module, class_name):
                    raise AttributeError(f"Module {module_name} has no class {class_name}")
                service_class = getattr(module, class_name)
                
                # Instantiate service
                logger.info(f"Instantiating {class_name}...")
                service_instance = service_class()
                logger.info(f"✓ Successfully instantiated {class_name}")
                
                # Check if it's properly inherited from BaseAnalyzer
                if not isinstance(service_instance, (BaseAnalyzer, AsyncBaseAnalyzer)):
                    logger.error(f"✗ Service {service_name} does not inherit from BaseAnalyzer")
                    self.failed_services[service_name] = "Invalid service class"
                    continue
                
                # Check if service is available
                is_available = service_instance.is_available
                logger.info(f"Service {service_name} availability: {is_available}")
                
                if not is_available:
                    logger.warning(f"Service {service_name} initialized but not available")
                    self.failed_services[service_name] = "Service not available"
                    # Still register it so we can check availability later
                
                # Register based on type
                if isinstance(service_instance, AsyncBaseAnalyzer):
                    self.async_services[service_name] = service_instance
                    logger.info(f"✓ Registered async service: {service_name}")
                else:
                    self.services[service_name] = service_instance
                    logger.info(f"✓ Registered sync service: {service_name}")
                    
            except ImportError as e:
                logger.error(f"✗ Failed to import {service_name}: {e}")
                self.failed_services[service_name] = f"Import error: {str(e)}"
            except AttributeError as e:
                logger.error(f"✗ Class {class_name} not found in {module_name}: {e}")
                self.failed_services[service_name] = f"Class not found: {str(e)}"
            except Exception as e:
                logger.error(f"✗ Failed to initialize {service_name}: {e}", exc_info=True)
                self.failed_services[service_name] = f"Initialization error: {str(e)}"
        
        logger.info("\n" + "=" * 80)
        logger.info(f"SERVICE REGISTRY INITIALIZATION COMPLETE")
        logger.info(f"Sync services registered: {len(self.services)}")
        logger.info(f"Async services registered: {len(self.async_services)}")
        logger.info(f"Failed services: {len(self.failed_services)}")
        logger.info(f"Available services: {list(self.services.keys()) + list(self.async_services.keys())}")
        logger.info("=" * 80 + "\n")
    
    def get_service(self, service_name: str) -> Optional[BaseAnalyzer]:
        """Get a service by name"""
        self._ensure_initialized()
        return self.services.get(service_name) or self.async_services.get(service_name)
    
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
    
    async def analyze_with_service_async(self, service_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run analysis with async service"""
        self._ensure_initialized()
        service = self.async_services.get(service_name)
        if not service:
            return {
                'service': service_name,
                'success': False,  # Always include success field
                'error': 'Service not found or not async',
                'available': False
            }
        
        if not service.is_available:
            return service.get_default_result()
        
        try:
            return await service.analyze_with_timeout(data)
        except Exception as e:
            logger.error(f"Async service {service_name} failed: {e}")
            return service.get_error_result(str(e))
    
    def analyze_with_service(self, service_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run analysis with sync service"""
        self._ensure_initialized()
        service = self.services.get(service_name)
        
        if not service:
            # Check if it's an async service
            if service_name in self.async_services:
                # Run async service in sync context
                return asyncio.run(self.analyze_with_service_async(service_name, data))
            
            return {
                'service': service_name,
                'success': False,  # Always include success field
                'error': 'Service not found',
                'available': False
            }
        
        if not service.is_available:
            return service.get_default_result()
        
        try:
            result = service.analyze(data)
            # Ensure success field is present
            if 'success' not in result:
                logger.warning(f"Service {service_name} result missing 'success' field, adding it")
                result['success'] = 'error' not in result
            return result
        except Exception as e:
            logger.error(f"Service {service_name} failed: {e}", exc_info=True)
            return service.get_error_result(str(e))
    
    def analyze_parallel(self, services: List[str], data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Run multiple services in parallel
        
        Args:
            services: List of service names to run
            data: Data to analyze
            
        Returns:
            Dictionary mapping service names to their results
        """
        self._ensure_initialized()
        results = {}
        
        # Separate sync and async services
        sync_services = [s for s in services if s in self.services]
        async_services = [s for s in services if s in self.async_services]
        
        # Run sync services in thread pool
        if sync_services:
            with ThreadPoolExecutor(max_workers=len(sync_services)) as executor:
                futures = {
                    executor.submit(self.analyze_with_service, service, data): service
                    for service in sync_services
                }
                
                for future in futures:
                    service_name = futures[future]
                    try:
                        results[service_name] = future.result()
                    except Exception as e:
                        logger.error(f"Service {service_name} failed in parallel execution: {e}")
                        results[service_name] = {
                            'service': service_name,
                            'success': False,  # Always include success field
                            'error': str(e),
                            'available': False
                        }
        
        # Run async services
        if async_services:
            async def run_async_services():
                tasks = [
                    self.analyze_with_service_async(service, data)
                    for service in async_services
                ]
                return await asyncio.gather(*tasks, return_exceptions=True)
            
            async_results = asyncio.run(run_async_services())
            
            for service_name, result in zip(async_services, async_results):
                if isinstance(result, Exception):
                    results[service_name] = {
                        'service': service_name,
                        'success': False,  # Always include success field
                        'error': str(result),
                        'available': False
                    }
                else:
                    results[service_name] = result
        
        return results
    
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
                
                if isinstance(service_instance, AsyncBaseAnalyzer):
                    self.async_services[service_name] = service_instance
                else:
                    self.services[service_name] = service_instance
                
                logger.info(f"Successfully reloaded service: {service_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to reload service {service_name}: {e}")
            self.failed_services[service_name] = f"Reload failed: {str(e)}"
            
        return False


# Global service registry instance - now with lazy initialization
_service_registry = None

def get_service_registry():
    """Get or create the global service registry instance"""
    global _service_registry
    if _service_registry is None:
        logger.info("Creating global service registry instance")
        _service_registry = ServiceRegistry()
    return _service_registry

# For backward compatibility, also create a global instance
service_registry = get_service_registry()
