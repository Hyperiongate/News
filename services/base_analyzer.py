"""
Base Analyzer Abstract Class
All analysis services should inherit from this base class
"""
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from functools import wraps
import asyncio

from config import Config

logger = logging.getLogger(__name__)


class BaseAnalyzer(ABC):
    """
    Base class for all analysis services
    Provides common functionality and interface
    """
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.config = Config.get_service_config(service_name)
        self.is_available = self._check_availability()
        self._performance_stats = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'total_time': 0,
            'average_time': 0
        }
        
        logger.info(f"{service_name} initialized successfully")
    
    @abstractmethod
    def _check_availability(self) -> bool:
        """
        Check if the service is available (has required API keys, etc.)
        Must be implemented by each service
        """
        pass
    
    @abstractmethod
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis method
        
        Args:
            data: Input data for analysis
            
        Returns:
            Analysis results dictionary
        """
        pass
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about the service"""
        return {
            'name': self.service_name,
            'available': self.is_available,
            'enabled': self.config.enabled if self.config else False,
            'performance': self._performance_stats.copy()
        }
    
    def get_default_result(self) -> Dict[str, Any]:
        """Get default result when service is unavailable"""
        return {
            'service': self.service_name,
            'success': False,  # FIXED: Added success field
            'available': False,
            'error': 'Service unavailable',
            'timestamp': time.time()
        }
    
    def get_error_result(self, error_message: str) -> Dict[str, Any]:
        """Get error result format"""
        return {
            'service': self.service_name,
            'success': False,  # FIXED: Added success field
            'available': self.is_available,
            'error': error_message,
            'timestamp': time.time()
        }
    
    def get_timeout_result(self) -> Dict[str, Any]:
        """Get timeout result format"""
        return {
            'service': self.service_name,
            'success': False,  # FIXED: Added success field
            'available': self.is_available,
            'error': f'Analysis timed out after {self.config.timeout}s',
            'timeout': True,
            'timestamp': time.time()
        }
    
    def validate_input(self, data: Dict[str, Any], required_fields: List[str]) -> Optional[str]:
        """
        Validate input data has required fields
        
        Returns:
            Error message if validation fails, None if valid
        """
        if not data:
            return "No input data provided"
        
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return f"Missing required fields: {', '.join(missing_fields)}"
        
        return None
    
    def track_performance(self, func):
        """Decorator to track performance metrics"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                self._performance_stats['successful_calls'] += 1
                return result
            except Exception as e:
                self._performance_stats['failed_calls'] += 1
                raise e
            finally:
                elapsed = time.time() - start_time
                self._performance_stats['total_calls'] += 1
                self._performance_stats['total_time'] += elapsed
                if self._performance_stats['total_calls'] > 0:
                    self._performance_stats['average_time'] = (
                        self._performance_stats['total_time'] / 
                        self._performance_stats['total_calls']
                    )
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                self._performance_stats['successful_calls'] += 1
                return result
            except Exception as e:
                self._performance_stats['failed_calls'] += 1
                raise e
            finally:
                elapsed = time.time() - start_time
                self._performance_stats['total_calls'] += 1
                self._performance_stats['total_time'] += elapsed
                if self._performance_stats['total_calls'] > 0:
                    self._performance_stats['average_time'] = (
                        self._performance_stats['total_time'] / 
                        self._performance_stats['total_calls']
                    )
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    
    def analyze_with_timeout(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run analysis with timeout protection
        
        Args:
            data: Input data for analysis
            
        Returns:
            Analysis results or timeout error
        """
        import concurrent.futures
        
        timeout = self.config.timeout if self.config else 30
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.analyze, data)
            try:
                result = future.result(timeout=timeout)
                return result
            except concurrent.futures.TimeoutError:
                return self.get_timeout_result()
            except Exception as e:
                logger.error(f"Service {self.service_name} failed: {e}")
                return self.get_error_result(str(e))


class AsyncBaseAnalyzer(BaseAnalyzer):
    """
    Async version of BaseAnalyzer for services that need async operations
    """
    
    @abstractmethod
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Async main analysis method
        
        Args:
            data: Input data for analysis
            
        Returns:
            Analysis results dictionary
        """
        pass
    
    async def analyze_with_timeout(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run async analysis with timeout protection
        
        Args:
            data: Input data for analysis
            
        Returns:
            Analysis results or timeout error
        """
        timeout = self.config.timeout if self.config else 30
        
        try:
            result = await asyncio.wait_for(
                self.analyze(data), 
                timeout=timeout
            )
            return result
        except asyncio.TimeoutError:
            return self.get_timeout_result()
        except Exception as e:
            logger.error(f"Async service {self.service_name} failed: {e}")
            return self.get_error_result(str(e))
