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
    }
    
    def __init__(self):
        self.services: Dict[str, BaseAnalyzer] = {}
        self.async_services: Dict[str, AsyncBaseAnalyzer] = {}
        self.failed_services: Dict[str, str] = {}
        self._initialize_services()
        
    def _initialize_services(self):
        """Initialize all configured services"""
        logger.info("Initializing service registry...")
        
        for service_name, (module_name, class_name) in self.SERVICE_MAPPING.items():
            # Check if service is enabled in config
            if not Config.is_service_enabled(service_name):
                logger.info(f"Service {service_name} is disabled in configuration")
                continue
                
            try:
                # Dynamic import
                module = importlib.import_module(module_name)
                service_class = getattr(module, class_name)
                
                # Instantiate service
                service_instance = service_class()
                
                # Check if it's properly inherited from BaseAnalyzer
                if not isinstance(service_instance, (BaseAnalyzer, AsyncBaseAnalyzer)):
                    logger.error(f"Service {service_name} does not inherit from BaseAnalyzer")
                    self.failed_services[service_name] = "Invalid service class"
                    continue
                
                # Check if service is available
                if not service_instance.is_available:
                    logger.warning(f"Service {service_name} initialized but not available")
                    self.failed_services[service_name] = "Service not available"
                    # Still register it so we can check availability later
                
                # Register based on type
                if isinstance(service_instance, AsyncBaseAnalyzer):
                    self.async_services[service_name] = service_instance
                    logger.info(f"Registered async service: {service_name}")
                else:
                    self.services[service_name] = service_instance
                    logger.info(f"Registered service: {service_name}")
                    
            except ImportError as e:
                logger.error(f"Failed to import {service_name}: {e}")
                self.failed_services[service_name] = f"Import error: {str(e)}"
            except AttributeError as e:
                logger.error(f"Class {class_name} not found in {module_name}: {e}")
                self.failed_services[service_name] = f"Class not found: {str(e)}"
            except Exception as e:
                logger.error(f"Failed to initialize {service_name}: {e}")
                self.failed_services[service_name] = f"Initialization error: {str(e)}"
        
        logger.info(f"Service registry initialized: {len(self.services)} sync services, "
                   f"{len(self.async_services)} async services, {len(self.failed_services)} failed")
    
    def get_service(self, service_name: str) -> Optional[BaseAnalyzer]:
        """Get a service by name"""
        return self.services.get(service_name) or self.async_services.get(service_name)
    
    def get_all_services(self) -> Dict[str, BaseAnalyzer]:
        """Get all registered services"""
        all_services = {}
        all_services.update(self.services)
        all_services.update(self.async_services)
        return all_services
    
    def get_available_services(self) -> Dict[str, BaseAnalyzer]:
        """Get only available services"""
        return {
            name: service 
            for name, service in self.get_all_services().items() 
            if service.is_available
        }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of all services"""
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
        service = self.async_services.get(service_name)
        if not service:
            return {
                'service': service_name,
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
        service = self.services.get(service_name)
        if not service:
            # Check if it's an async service
            if service_name in self.async_services:
                # Run async service in sync context
                return asyncio.run(self.analyze_with_service_async(service_name, data))
            
            return {
                'service': service_name,
                'error': 'Service not found',
                'available': False
            }
        
        if not service.is_available:
            return service.get_default_result()
        
        try:
            return service.analyze(data)
        except Exception as e:
            logger.error(f"Service {service_name} failed: {e}")
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
                        results[service_name] = future.result(timeout=30)
                    except Exception as e:
                        logger.error(f"Parallel analysis failed for {service_name}: {e}")
                        service = self.services.get(service_name)
                        results[service_name] = service.get_error_result(str(e)) if service else {
                            'error': str(e),
                            'service': service_name
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
            
            for service, result in zip(async_services, async_results):
                if isinstance(result, Exception):
                    logger.error(f"Async parallel analysis failed for {service}: {result}")
                    service_obj = self.async_services.get(service)
                    results[service] = service_obj.get_error_result(str(result)) if service_obj else {
                        'error': str(result),
                        'service': service
                    }
                else:
                    results[service] = result
        
        return results
    
    def reload_service(self, service_name: str) -> bool:
        """
        Reload a specific service
        
        Args:
            service_name: Name of service to reload
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Remove existing service
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


# Global service registry instance
service_registry = ServiceRegistry()
