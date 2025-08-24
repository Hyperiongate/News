"""
Fixed Analysis Pipeline with Performance Optimizations
"""
import asyncio
import time
import logging
from typing import Dict, Any, List, Optional, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback

from .service_registry import get_service_registry
from .base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)

class AnalysisPipeline:
    """
    Fixed pipeline with proper parallel execution and timeout handling
    """
    
    # Service groups for parallel execution
    STAGE_1_SERVICES = ['article_extractor']  # Must run first
    STAGE_2_SERVICES = [  # Can run in parallel after extraction
        'source_credibility',
        'author_analyzer',
        'bias_detector',
        'transparency_analyzer',
        'manipulation_detector',
        'content_analyzer'
    ]
    STAGE_3_SERVICES = ['fact_checker']  # Depends on article content
    STAGE_4_SERVICES = ['openai_enhancer']  # Enhancement layer
    
    def __init__(self):
        self.registry = get_service_registry()
        self.executor = ThreadPoolExecutor(max_workers=8)  # Increased workers
        
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run analysis pipeline with optimized parallel execution
        """
        start_time = time.time()
        results = {
            'success': True,
            'article': None,
            'trust_score': 50,
            'trust_level': 'Unknown',
            'services_available': 0,
            'pipeline_metadata': {
                'stages_completed': [],
                'service_timings': {},
                'total_services': 0
            }
        }
        
        try:
            # Stage 1: Article Extraction (must complete first)
            logger.info("Stage 1: Article Extraction")
            article_data = self._run_stage_sequential(self.STAGE_1_SERVICES, data, results)
            
            if not article_data or not article_data.get('article_extractor', {}).get('success'):
                logger.error("Article extraction failed")
                results['success'] = False
                results['error'] = 'Failed to extract article content'
                return results
            
            # Update article data
            extracted_article = self._extract_article_data(article_data['article_extractor'])
            results['article'] = extracted_article
            enriched_data = {**data, 'article': extracted_article}
            
            # Stage 2: Core Analysis (parallel execution)
            logger.info("Stage 2: Core Analysis Services (Parallel)")
            stage2_start = time.time()
            stage2_results = self._run_stage_parallel(self.STAGE_2_SERVICES, enriched_data, results)
            logger.info(f"Stage 2 completed in {time.time() - stage2_start:.2f}s")
            
            # Merge stage 2 results
            for service_name, service_result in stage2_results.items():
                results[service_name] = service_result
            
            # Stage 3: Fact Checking (can run after extraction)
            logger.info("Stage 3: Fact Checking")
            stage3_results = self._run_stage_parallel(self.STAGE_3_SERVICES, enriched_data, results)
            for service_name, service_result in stage3_results.items():
                results[service_name] = service_result
            
            # Stage 4: Enhancement (optional, non-blocking)
            if data.get('is_pro', False):
                logger.info("Stage 4: AI Enhancement")
                # Run enhancement in background, don't wait
                self._run_stage_async(self.STAGE_4_SERVICES, enriched_data, results)
            
            # Calculate trust score from available results
            results['trust_score'] = self._calculate_trust_score(results)
            results['trust_level'] = self._get_trust_level(results['trust_score'])
            
            # Update metadata
            total_time = time.time() - start_time
            results['pipeline_metadata']['total_time'] = total_time
            results['pipeline_metadata']['services_available'] = len([
                s for s in results.keys() 
                if isinstance(results.get(s), dict) and results[s].get('success')
            ])
            
            logger.info(f"Pipeline completed in {total_time:.2f}s with {results['pipeline_metadata']['services_available']} services")
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}", exc_info=True)
            results['success'] = False
            results['error'] = str(e)
            
        return results
    
    def _run_stage_sequential(self, services: List[str], data: Dict[str, Any], 
                            results: Dict[str, Any]) -> Dict[str, Any]:
        """Run services sequentially (for dependencies)"""
        stage_results = {}
        
        for service_name in services:
            if not self.registry.is_service_available(service_name):
                logger.warning(f"Service {service_name} not available")
                continue
                
            try:
                start_time = time.time()
                result = self.registry.analyze_with_service(service_name, data)
                duration = time.time() - start_time
                
                stage_results[service_name] = result
                results['pipeline_metadata']['service_timings'][service_name] = duration
                
                logger.info(f"Service {service_name} completed in {duration:.2f}s")
                
            except Exception as e:
                logger.error(f"Service {service_name} failed: {str(e)}")
                stage_results[service_name] = {
                    'success': False,
                    'error': str(e),
                    'service': service_name
                }
                
        return stage_results
    
    def _run_stage_parallel(self, services: List[str], data: Dict[str, Any], 
                          results: Dict[str, Any]) -> Dict[str, Any]:
        """Run services in parallel with timeout protection"""
        stage_results = {}
        futures = {}
        
        # Submit all tasks
        for service_name in services:
            if not self.registry.is_service_available(service_name):
                logger.warning(f"Service {service_name} not available")
                continue
                
            future = self.executor.submit(self._run_service_with_timeout, service_name, data)
            futures[future] = service_name
        
        # Collect results with timeout
        timeout = 10  # 10 second timeout per service
        for future in as_completed(futures, timeout=timeout):
            service_name = futures[future]
            try:
                result, duration = future.result()
                stage_results[service_name] = result
                results['pipeline_metadata']['service_timings'][service_name] = duration
                logger.info(f"Service {service_name} completed in {duration:.2f}s")
            except Exception as e:
                logger.error(f"Service {service_name} failed: {str(e)}")
                stage_results[service_name] = {
                    'success': False,
                    'error': str(e),
                    'service': service_name
                }
        
        return stage_results
    
    def _run_service_with_timeout(self, service_name: str, data: Dict[str, Any]) -> tuple:
        """Run a single service with timeout protection"""
        start_time = time.time()
        try:
            # FIXED: Access the service using get_service method instead of _services
            service = self.registry.get_service(service_name)
            if service and hasattr(service, 'analyze_with_timeout'):
                result = service.analyze_with_timeout(data)
            else:
                result = self.registry.analyze_with_service(service_name, data)
            
            duration = time.time() - start_time
            return result, duration
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Service {service_name} error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'service': service_name
            }, duration
    
    def _run_stage_async(self, services: List[str], data: Dict[str, Any], 
                        results: Dict[str, Any]) -> None:
        """Run services asynchronously without blocking"""
        for service_name in services:
            if self.registry.is_service_available(service_name):
                self.executor.submit(self._run_service_async, service_name, data, results)
    
    def _run_service_async(self, service_name: str, data: Dict[str, Any], 
                          results: Dict[str, Any]) -> None:
        """Run a service asynchronously and update results"""
        try:
            start_time = time.time()
            result = self.registry.analyze_with_service(service_name, data)
            duration = time.time() - start_time
            
            results[service_name] = result
            results['pipeline_metadata']['service_timings'][service_name] = duration
            
            logger.info(f"Async service {service_name} completed in {duration:.2f}s")
            
        except Exception as e:
            logger.error(f"Async service {service_name} failed: {str(e)}")
    
    def _extract_article_data(self, extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract article data from extraction service result"""
        if not extraction_result.get('success'):
            return {}
            
        # Handle different extraction result formats
        if 'article' in extraction_result:
            return extraction_result['article']
        elif 'data' in extraction_result:
            return extraction_result['data']
        else:
            # Extract relevant fields
            article_fields = ['title', 'text', 'author', 'publish_date', 
                            'domain', 'url', 'word_count', 'language']
            return {
                field: extraction_result.get(field) 
                for field in article_fields 
                if field in extraction_result
            }
    
    def _calculate_trust_score(self, results: Dict[str, Any]) -> int:
        """Calculate overall trust score from service results"""
        scores = []
        weights = {
            'source_credibility': 0.25,
            'author_analyzer': 0.20,
            'bias_detector': 0.20,
            'fact_checker': 0.15,
            'transparency_analyzer': 0.10,
            'manipulation_detector': 0.10
        }
        
        for service, weight in weights.items():
            if service in results and isinstance(results[service], dict):
                service_data = results[service]
                if service_data.get('success'):
                    # Extract score from service
                    score = self._extract_service_score(service, service_data)
                    if score is not None:
                        scores.append((score, weight))
        
        if not scores:
            return 50  # Default middle score
        
        # Calculate weighted average
        total_weight = sum(weight for _, weight in scores)
        weighted_sum = sum(score * weight for score, weight in scores)
        
        return int(weighted_sum / total_weight) if total_weight > 0 else 50
    
    def _extract_service_score(self, service_name: str, data: Dict[str, Any]) -> Optional[int]:
        """Extract numerical score from service result"""
        # Common score field names
        score_fields = ['trust_score', 'credibility_score', 'score', 'overall_score']
        
        # Check common fields first
        for field in score_fields:
            if field in data and isinstance(data[field], (int, float)):
                return int(data[field])
        
        # Service-specific logic
        if service_name == 'bias_detector':
            # For bias, invert the score (less bias = higher trust)
            bias_score = data.get('bias_score', data.get('score', 50))
            return 100 - int(bias_score)
            
        elif service_name == 'fact_checker':
            # Calculate from fact check results
            if 'fact_checks' in data and isinstance(data['fact_checks'], list):
                if len(data['fact_checks']) > 0:
                    verified = sum(1 for fc in data['fact_checks'] 
                                 if fc.get('verdict', '').lower() in ['true', 'verified', 'correct'])
                    return int((verified / len(data['fact_checks'])) * 100)
            return 75  # Default if no claims to check
            
        elif service_name == 'manipulation_detector':
            # Less manipulation = higher trust
            manipulation_score = data.get('manipulation_score', 0)
            tactics_count = len(data.get('tactics_found', []))
            if tactics_count > 5:
                return 20
            elif tactics_count > 2:
                return 50
            else:
                return 100 - int(manipulation_score)
        
        return None
    
    def _get_trust_level(self, score: int) -> str:
        """Get trust level description from score"""
        if score >= 80:
            return 'Very High'
        elif score >= 60:
            return 'High'
        elif score >= 40:
            return 'Moderate'
        elif score >= 20:
            return 'Low'
        else:
            return 'Very Low'
