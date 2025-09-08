"""
Isolated Analysis Pipeline - ARCHITECTURAL FIX
Date: 2025-01-27
Author: System Architect

PROBLEM SOLVED:
- Services no longer depend on each other's output format
- Each service gets clean, immutable input data
- Failures are isolated and don't cascade
- Services can be modified independently without breaking others

KEY CHANGES:
1. Each service receives the SAME original article data
2. No service modifies shared state
3. Results are aggregated AFTER all services complete
4. Proper error boundaries prevent cascade failures
5. Service results are validated before use
"""

import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed
import traceback
from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum

from services.service_registry import get_service_registry

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service execution status"""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    UNAVAILABLE = "unavailable"


@dataclass
class ServiceResult:
    """Encapsulates a service result with metadata"""
    service_name: str
    status: ServiceStatus
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    execution_time: float = 0.0
    
    @property
    def is_successful(self) -> bool:
        return self.status == ServiceStatus.SUCCESS


@dataclass
class IsolatedServiceContext:
    """Immutable context for service execution"""
    article_data: Dict[str, Any]
    original_request: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_service_input(self) -> Dict[str, Any]:
        """Create immutable input for a service"""
        # Deep copy to ensure immutability
        return deepcopy({
            **self.article_data,
            **self.original_request,
            'article': self.article_data,  # Some services expect this
            'metadata': self.metadata
        })


class ServiceIsolator:
    """Isolates service execution to prevent cascade failures"""
    
    def __init__(self, service_name: str, service_instance: Any):
        self.service_name = service_name
        self.service = service_instance
        self.timeout = self._get_timeout()
    
    def _get_timeout(self) -> int:
        """Get service timeout from config"""
        from config import Config
        service_config = Config.get_service_config(self.service_name)
        return service_config.timeout if service_config else 30
    
    def execute(self, context: IsolatedServiceContext) -> ServiceResult:
        """Execute service in isolation"""
        start_time = time.time()
        
        try:
            # Check if service is available
            if not self._is_available():
                return ServiceResult(
                    service_name=self.service_name,
                    status=ServiceStatus.UNAVAILABLE,
                    error="Service not available"
                )
            
            # Create immutable input data
            input_data = context.to_service_input()
            
            # Execute with timeout protection
            result = self._execute_with_timeout(input_data)
            
            # Validate and normalize result
            if self._validate_result(result):
                return ServiceResult(
                    service_name=self.service_name,
                    status=ServiceStatus.SUCCESS,
                    data=self._extract_data(result),
                    execution_time=time.time() - start_time
                )
            else:
                return ServiceResult(
                    service_name=self.service_name,
                    status=ServiceStatus.FAILED,
                    error="Invalid result format",
                    execution_time=time.time() - start_time
                )
                
        except TimeoutError:
            return ServiceResult(
                service_name=self.service_name,
                status=ServiceStatus.TIMEOUT,
                error=f"Service timed out after {self.timeout}s",
                execution_time=self.timeout
            )
        except Exception as e:
            logger.error(f"Service {self.service_name} failed: {e}")
            return ServiceResult(
                service_name=self.service_name,
                status=ServiceStatus.FAILED,
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    def _is_available(self) -> bool:
        """Check if service is available"""
        try:
            return hasattr(self.service, 'is_available') and self.service.is_available
        except:
            return False
    
    def _execute_with_timeout(self, input_data: Dict[str, Any]) -> Any:
        """Execute service with timeout"""
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.service.analyze, input_data)
            return future.result(timeout=self.timeout)
    
    def _validate_result(self, result: Any) -> bool:
        """Validate service result structure"""
        if not isinstance(result, dict):
            return False
        
        # Check for required fields
        if 'success' not in result:
            return False
        
        # If not successful, it's still valid (contains error info)
        if not result['success']:
            return True
        
        # For successful results, check for data
        return 'data' in result or 'score' in result or 'analysis' in result
    
    def _extract_data(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize service data"""
        # Handle different result formats
        if 'data' in result:
            return result['data']
        elif 'analysis' in result:
            return result['analysis']
        else:
            # Return everything except metadata
            return {k: v for k, v in result.items() 
                   if k not in ['success', 'service', 'timestamp', 'available']}


class IsolatedAnalysisPipeline:
    """
    New pipeline architecture with complete service isolation
    """
    
    # Service execution order (dependencies)
    STAGE_DEPENDENCIES = {
        'extraction': [],  # No dependencies
        'core_analysis': ['extraction'],  # Depends on extraction
        'fact_checking': ['extraction'],  # Depends on extraction
        'enhancement': ['extraction', 'core_analysis']  # Depends on both
    }
    
    # Service to stage mapping
    SERVICE_STAGES = {
        'article_extractor': 'extraction',
        'source_credibility': 'core_analysis',
        'author_analyzer': 'core_analysis',
        'bias_detector': 'core_analysis',
        'transparency_analyzer': 'core_analysis',
        'manipulation_detector': 'core_analysis',
        'content_analyzer': 'core_analysis',
        'fact_checker': 'fact_checking',
        'openai_enhancer': 'enhancement'
    }
    
    def __init__(self):
        self.registry = get_service_registry()
        self.executor = ThreadPoolExecutor(max_workers=8)
        logger.info("IsolatedAnalysisPipeline initialized")
    
    def analyze(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis method with complete service isolation
        """
        start_time = time.time()
        request_id = request_data.get('request_id', 'unknown')
        
        logger.info("=" * 80)
        logger.info(f"[{request_id}] ISOLATED PIPELINE STARTING")
        logger.info(f"Input type: {'URL' if 'url' in request_data else 'Text'}")
        logger.info("=" * 80)
        
        # Initialize response
        response = {
            'success': False,
            'article': {},
            'trust_score': 50,
            'trust_level': 'Unknown',
            'detailed_analysis': {},
            'errors': [],
            'metadata': {
                'pipeline_version': '2.0',
                'isolated_execution': True
            }
        }
        
        try:
            # Stage 1: Article Extraction (Sequential - Required)
            extraction_result = self._extract_article(request_data)
            
            if not extraction_result.is_successful:
                response['success'] = False
                response['errors'].append(f"Extraction failed: {extraction_result.error}")
                return response
            
            # Create immutable context for all services
            context = IsolatedServiceContext(
                article_data=extraction_result.data,
                original_request=request_data,
                metadata={'extraction_time': extraction_result.execution_time}
            )
            
            response['article'] = extraction_result.data
            logger.info(f"✓ Article extracted: {extraction_result.data.get('title', 'Unknown')[:50]}...")
            
            # Stage 2: Parallel Analysis with Isolation
            analysis_results = self._run_analysis_services(context)
            
            # Stage 3: Process Results (No Inter-Service Dependencies)
            for service_name, result in analysis_results.items():
                if result.is_successful:
                    response['detailed_analysis'][service_name] = result.data
                    logger.info(f"✓ {service_name}: Success")
                else:
                    logger.warning(f"✗ {service_name}: {result.status.value} - {result.error}")
                    response['errors'].append(f"{service_name}: {result.error}")
            
            # Stage 4: Calculate Trust Score (From Independent Results)
            response['trust_score'] = self._calculate_trust_score(response['detailed_analysis'])
            response['trust_level'] = self._get_trust_level(response['trust_score'])
            
            # Mark as successful if we got meaningful results
            response['success'] = len(response['detailed_analysis']) >= 3
            
            # Add metadata
            response['metadata'].update({
                'processing_time': time.time() - start_time,
                'services_succeeded': len(response['detailed_analysis']),
                'services_failed': len(response['errors'])
            })
            
            logger.info("=" * 80)
            logger.info(f"[{request_id}] PIPELINE COMPLETE")
            logger.info(f"Services: {len(response['detailed_analysis'])} succeeded, {len(response['errors'])} failed")
            logger.info(f"Trust Score: {response['trust_score']}/100")
            logger.info(f"Time: {response['metadata']['processing_time']:.2f}s")
            logger.info("=" * 80)
            
            return response
            
        except Exception as e:
            logger.error(f"Pipeline critical error: {e}", exc_info=True)
            response['success'] = False
            response['errors'].append(f"Pipeline error: {str(e)}")
            return response
    
    def _extract_article(self, request_data: Dict[str, Any]) -> ServiceResult:
        """Extract article with isolation"""
        try:
            # Get article extractor
            extractor = self.registry.get_service('article_extractor')
            if not extractor:
                return ServiceResult(
                    service_name='article_extractor',
                    status=ServiceStatus.UNAVAILABLE,
                    error="Article extractor not available"
                )
            
            # Create isolator
            isolator = ServiceIsolator('article_extractor', extractor)
            
            # Create minimal context for extraction
            context = IsolatedServiceContext(
                article_data={},
                original_request=request_data
            )
            
            # Execute with isolation
            return isolator.execute(context)
            
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return ServiceResult(
                service_name='article_extractor',
                status=ServiceStatus.FAILED,
                error=str(e)
            )
    
    def _run_analysis_services(self, context: IsolatedServiceContext) -> Dict[str, ServiceResult]:
        """Run all analysis services in parallel with complete isolation"""
        results = {}
        futures = {}
        
        # Get available services
        available_services = self.registry.get_available_services()
        
        # Submit all analysis services (except extractor and enhancer)
        for service_name, service in available_services.items():
            if service_name in ['article_extractor', 'openai_enhancer']:
                continue  # Skip extraction (already done) and enhancement (do later)
            
            logger.info(f"Submitting {service_name} for isolated execution")
            isolator = ServiceIsolator(service_name, service)
            future = self.executor.submit(isolator.execute, context)
            futures[future] = service_name
        
        # Collect results with timeout protection
        for future in as_completed(futures, timeout=60):
            service_name = futures[future]
            try:
                result = future.result(timeout=30)
                results[service_name] = result
            except Exception as e:
                logger.error(f"Failed to get result for {service_name}: {e}")
                results[service_name] = ServiceResult(
                    service_name=service_name,
                    status=ServiceStatus.FAILED,
                    error=str(e)
                )
        
        # Optional: Run enhancement if available and other services succeeded
        if len([r for r in results.values() if r.is_successful]) >= 3:
            enhancer = self.registry.get_service('openai_enhancer')
            if enhancer and enhancer.is_available:
                logger.info("Running optional enhancement service")
                isolator = ServiceIsolator('openai_enhancer', enhancer)
                enhancement_result = isolator.execute(context)
                if enhancement_result.is_successful:
                    results['openai_enhancer'] = enhancement_result
        
        return results
    
    def _calculate_trust_score(self, detailed_analysis: Dict[str, Any]) -> int:
        """Calculate trust score from isolated service results"""
        weights = {
            'source_credibility': 0.25,
            'author_analyzer': 0.15,
            'bias_detector': 0.20,
            'fact_checker': 0.15,
            'transparency_analyzer': 0.10,
            'manipulation_detector': 0.10,
            'content_analyzer': 0.05
        }
        
        total_weight = 0
        weighted_sum = 0
        
        for service, weight in weights.items():
            if service in detailed_analysis:
                service_data = detailed_analysis[service]
                
                # Extract score (handle different formats)
                score = self._extract_score(service, service_data)
                
                if score is not None:
                    logger.info(f"Trust component {service}: {score} (weight: {weight})")
                    weighted_sum += score * weight
                    total_weight += weight
        
        # Calculate final score
        if total_weight > 0:
            trust_score = int(weighted_sum / total_weight)
        else:
            trust_score = 50  # Default
        
        return max(0, min(100, trust_score))
    
    def _extract_score(self, service_name: str, service_data: Dict[str, Any]) -> Optional[float]:
        """Extract score from service data (handles various formats)"""
        if not isinstance(service_data, dict):
            return None
        
        # Standard score fields
        for field in ['score', 'trust_score', 'credibility_score', 'overall_score']:
            if field in service_data:
                return float(service_data[field])
        
        # Service-specific fields
        if service_name == 'bias_detector' and 'bias_score' in service_data:
            # Invert bias score (high bias = low trust)
            return 100 - float(service_data['bias_score'])
        
        if service_name == 'manipulation_detector' and 'manipulation_score' in service_data:
            # Invert manipulation score
            return 100 - float(service_data['manipulation_score'])
        
        if service_name == 'author_analyzer':
            # Check for various author score fields
            for field in ['combined_credibility_score', 'author_score']:
                if field in service_data:
                    return float(service_data[field])
        
        return None
    
    def _get_trust_level(self, score: int) -> str:
        """Convert trust score to level"""
        if score >= 80:
            return 'Very High'
        elif score >= 60:
            return 'High'
        elif score >= 40:
            return 'Medium'
        elif score >= 20:
            return 'Low'
        else:
            return 'Very Low'


# Backward Compatibility Wrapper
class AnalysisPipeline:
    """
    Wrapper to maintain backward compatibility with existing code
    while using the new isolated pipeline internally
    """
    
    def __init__(self):
        self.isolated_pipeline = IsolatedAnalysisPipeline()
        self.registry = get_service_registry()
        logger.info("AnalysisPipeline initialized with isolation wrapper")
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Backward compatible analyze method"""
        # Use the isolated pipeline
        result = self.isolated_pipeline.analyze(data)
        
        # Ensure backward compatibility with expected format
        if 'summary' not in result:
            result['summary'] = f"Analysis complete - Trust Score: {result.get('trust_score', 0)}/100"
        
        if 'services_available' not in result:
            result['services_available'] = len(result.get('detailed_analysis', {}))
        
        return result
