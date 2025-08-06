"""
Base Analyzer Class
All analysis services should inherit from this base class
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import time
import logging
from functools import wraps
import asyncio
from concurrent.futures import ThreadPoolExecutor, TimeoutError

from config import Config, ServiceConfig

logger = logging.getLogger(__name__)


def with_timeout(func):
    """Decorator to add timeout to analyzer methods"""
    @wraps(func)
    async def async_wrapper(self, *args, **kwargs):
        try:
            return await asyncio.wait_for(
                func(self, *args, **kwargs),
                timeout=self.config.timeout
            )
        except asyncio.TimeoutError:
            logger.error(f"{self.service_name} timed out after {self.config.timeout}s")
            return self.get_timeout_result()
    
    @wraps(func)
    def sync_wrapper(self, *args, **kwargs):
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, self, *args, **kwargs)
                return future.result(timeout=self.config.timeout)
        except TimeoutError:
            logger.error(f"{self.service_name} timed out after {self.config.timeout}s")
            return self.get_timeout_result()
    
    # Return appropriate wrapper based on function type
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def with_retry(func):
    """Decorator to add retry logic to analyzer methods"""
    @wraps(func)
    async def async_wrapper(self, *args, **kwargs):
        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                return await func(self, *args, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < self.config.max_retries - 1:
                    wait_time = (attempt + 1) * 2  # Exponential backoff
                    logger.warning(f"{self.service_name} attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"{self.service_name} failed after {self.config.max_retries} attempts: {e}")
        return self.get_error_result(str(last_error))
    
    @wraps(func)
    def sync_wrapper(self, *args, **kwargs):
        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < self.config.max_retries - 1:
                    wait_time = (attempt + 1) * 2  # Exponential backoff
                    logger.warning(f"{self.service_name} attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"{self.service_name} failed after {self.config.max_retries} attempts: {e}")
        return self.get_error_result(str(last_error))
    
    # Return appropriate wrapper based on function type
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


class BaseAnalyzer(ABC):
    """Base class for all analysis services"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.config: ServiceConfig = Config.get_service_config(service_name)
        self.is_available = self._check_availability()
        self._performance_stats = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'total_time': 0,
            'average_time': 0
        }
        
        if self.is_available:
            logger.info(f"{service_name} initialized successfully")
        else:
            logger.warning(f"{service_name} is not available")
    
    @abstractmethod
    def _check_availability(self) -> bool:
        """
        Check if the service is available and properly configured
        Each service should implement its own availability check
        """
        pass
    
    @abstractmethod
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis method that each service must implement
        
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
            'available': False,
            'error': 'Service unavailable',
            'timestamp': time.time()
        }
    
    def get_error_result(self, error_message: str) -> Dict[str, Any]:
        """Get error result format"""
        return {
            'service': self.service_name,
            'available': self.is_available,
            'error': error_message,
            'timestamp': time.time()
        }
    
    def get_timeout_result(self) -> Dict[str, Any]:
        """Get timeout result format"""
        return {
            'service': self.service_name,
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
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper


class AsyncBaseAnalyzer(BaseAnalyzer):
    """Base class for async analysis services"""
    
    @abstractmethod
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Async analysis method"""
        pass
    
    async def analyze_with_timeout(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze with timeout protection"""
        try:
            return await asyncio.wait_for(
                self.analyze(data),
                timeout=self.config.timeout
            )
        except asyncio.TimeoutError:
            return self.get_timeout_result()
