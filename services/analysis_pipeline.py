"""
REAL Fixed Analysis Pipeline
CRITICAL: Works with your actual service return formats
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
    REAL FIXED: Pipeline compatible with your service return formats
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
        self.executor = ThreadPoolExecutor(max_workers=8)
        
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run analysis pipeline with REAL service data handling
        """
        start_time = time.time()
        
        # Initialize results with proper structure
        results = {
            'success': True,
            'article': None,
            'trust_score': 50,
            'trust_level': 'Unknown',
            'summary': 'Analysis in progress...',
            'services_available': 0,
            'pipeline_metadata': {
                'stages_completed': [],
                'service_timings': {},
                'total_services': 0
            },
            'errors': []
        }
        
        try:
            logger.info("=" * 80)
            logger.info("STARTING REAL ANALYSIS PIPELINE")
            logger.info(f"Input data keys: {list(data.keys())}")
            logger.info("=" * 80)
            
            # Stage 1: Article Extraction (must complete first)
            logger.info("STAGE 1: Article Extraction")
            article_data = self._run_stage_sequential(self.STAGE_1_SERVICES, data)
            
            if not article_data or 'article_extractor' not in article_data:
                logger.error("Article extraction failed - no data returned")
                results['success'] = False
                results['error'] = 'Failed to extract article content'
                results['summary'] = 'Article extraction failed'
                return results
            
            # REAL FIX: Handle your actual service return format
            extractor_result = article_data['article_extractor']
            if not extractor_result.get('success', False):
                logger.error(f"Article extraction failed: {extractor_result.get('error', 'Unknown error')}")
                results['success'] = False
                results['error'] = 'Article extraction failed'
                results['summary'] = 'Could not extract article content'
                return results
            
            # REAL FIX: Extract article from your service's actual structure
            article_info = self._extract_article_data_real(extractor_result)
            results['article'] = article_info
            logger.info(f"Article extracted: '{article_info.get('title', 'No title')[:100]}...'")
            
            # REAL FIX: Create enriched data for subsequent services
            enriched_data = {**data}
            enriched_data.update(article_info)  # Add article fields to data
            enriched_data['article'] = article_info  # Also provide as nested object
            
            # Stage 2: Core Analysis Services (parallel)
            logger.info("STAGE 2: Core Analysis Services (Parallel)")
            stage2_results = self._run_stage_parallel(self.STAGE_2_SERVICES, enriched_data)
            
            # Stage 3: Fact Checking
            logger.info("STAGE 3: Fact Checking")
            stage3_results = self._run_stage_parallel(self.STAGE_3_SERVICES, enriched_data)
            
            # Stage 4: AI Enhancement (if pro mode)
            stage4_results = {}
            if data.get('is_pro', False):
                logger.info("STAGE 4: AI Enhancement")
                stage4_results = self._run_stage_parallel(self.STAGE_4_SERVICES, enriched_data)
            
            # REAL FIX: Combine all service results and flatten nested data
            all_service_results = {}
            all_service_results.update(article_data)  # Stage 1
            all_service_results.update(stage2_results)  # Stage 2
            all_service_results.update(stage3_results)  # Stage 3
            all_service_results.update(stage4_results)  # Stage 4
            
            # REAL FIX: Process results in format frontend expects
            processed_results = {}
            successful_services = 0
            
            for service_name, service_result in all_service_results.items():
                logger.info(f"\nProcessing {service_name} result:")
                logger.info(f"  Success: {service_result.get('success', False)}")
                logger.info(f"  Has data key: {'data' in service_result}")
                logger.info(f"  Keys: {list(service_result.keys())}")
                
                if service_result.get('success', False):
                    # REAL FIX: Handle your actual service data structure
                    clean_data = self._extract_service_data_real(service_name, service_result)
                    processed_results[service_name] = clean_data
                    successful_services += 1
                    logger.info(f"  Processed data keys: {list(clean_data.keys())}")
                else:
                    # Keep failed service info for debugging
                    processed_results[service_name] = {
                        'success': False,
                        'error': service_result.get('error', 'Service failed'),
                        'available': service_result.get('available', False)
                    }
                    error_msg = f"Service {service_name} failed: {service_result.get('error', 'Unknown error')}"
                    results['errors'].append(error_msg)
                    logger.warning(f"  {error_msg}")
            
            # REAL FIX: Store processed results in the format frontend expects
            results.update(processed_results)  # Merge service results directly into main results
            
            # Calculate trust score from successful services
            results['trust_score'] = self._calculate_trust_score_real(processed_results)
            results['trust_level'] = self._get_trust_level(results['trust_score'])
            results['summary'] = f"Analysis complete. {successful_services} services provided data."
            
            # Update metadata
            total_time = time.time() - start_time
            results['pipeline_metadata']['total_time'] = total_time
            results['pipeline_metadata']['services_available'] = successful_services
            results['services_available'] = successful_services
            
            logger.info("=" * 80)
            logger.info("REAL PIPELINE COMPLETION SUMMARY:")
            logger.info(f"Total time: {total_time:.2f}s")
            logger.info(f"Successful services: {successful_services}")
            logger.info(f"Trust score: {results['trust_score']}")
            logger.info(f"Final result keys: {list(results.keys())}")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}", exc_info=True)
            results['success'] = False
            results['error'] = str(e)
            results['summary'] = f'Pipeline failed: {str(e)}'
            
        return results
    
    def _run_stage_sequential(self, services: List[str], data: Dict[str, Any]) -> Dict[str, Any]:
        """Run services sequentially (for dependencies)"""
        stage_results = {}
        
        for service_name in services:
            if not self.registry.is_service_available(service_name):
                logger.warning(f"Service {service_name} not available")
                continue
                
            try:
                logger.info(f"Running {service_name}...")
                start_time = time.time()
                result = self.registry.analyze_with_service(service_name, data)
                duration = time.time() - start_time
                
                stage_results[service_name] = result
                logger.info(f"Service {service_name} completed in {duration:.2f}s")
                
            except Exception as e:
                logger.error(f"Service {service_name} failed: {str(e)}", exc_info=True)
                stage_results[service_name] = {
                    'success': False,
                    'error': str(e),
                    'service': service_name,
                    'available': False
                }
                
        return stage_results
    
    def _run_stage_parallel(self, services: List[str], data: Dict[str, Any]) -> Dict[str, Any]:
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
        timeout = 45  # Increased timeout for better reliability
        for future in as_completed(futures, timeout=timeout):
            service_name = futures[future]
            try:
                result, duration = future.result()
                stage_results[service_name] = result
                logger.info(f"Service {service_name} completed in {duration:.2f}s")
            except Exception as e:
                logger.error(f"Service {service_name} failed: {str(e)}", exc_info=True)
                stage_results[service_name] = {
                    'success': False,
                    'error': str(e),
                    'service': service_name,
                    'available': False
                }
        
        return stage_results
    
    def _run_service_with_timeout(self, service_name: str, data: Dict[str, Any]) -> tuple:
        """Run a single service with timeout protection"""
        start_time = time.time()
        try:
            result = self.registry.analyze_with_service(service_name, data)
            duration = time.time() - start_time
            return result, duration
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Service {service_name} error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'service': service_name,
                'available': False
            }, duration
    
    def _extract_article_data_real(self, extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """REAL FIX: Extract article data from your actual service format"""
        if not extraction_result.get('success'):
            return {
                'title': 'Unknown Title',
                'text': '',
                'author': 'Unknown',
                'url': '',
                'extraction_successful': False
            }
        
        # REAL FIX: Your services return data under 'data' key
        article_data = extraction_result.get('data', extraction_result)
        
        # Handle different extraction result formats
        if 'article' in article_data:
            article_data = article_data['article']
        
        # Extract standard fields
        extracted = {
            'title': article_data.get('title', 'Unknown Title'),
            'text': article_data.get('text', article_data.get('content', '')),
            'author': article_data.get('author', 'Unknown'),
            'publish_date': article_data.get('publish_date', article_data.get('date', '')),
            'domain': article_data.get('domain', article_data.get('source', '')),
            'url': article_data.get('url', ''),
            'word_count': article_data.get('word_count', len(article_data.get('text', '').split())),
            'language': article_data.get('language', 'en'),
            'extraction_successful': True
        }
        
        logger.info(f"Extracted article: {extracted['title'][:50]}... ({extracted['word_count']} words)")
        return extracted
    
    def _extract_service_data_real(self, service_name: str, service_result: Dict[str, Any]) -> Dict[str, Any]:
        """REAL FIX: Extract data from your actual service formats"""
        # Start with base service info
        extracted = {
            'success': service_result.get('success', False),
            'service': service_name,
            'timestamp': service_result.get('timestamp', time.time())
        }
        
        # If service failed, return minimal info
        if not service_result.get('success', False):
            extracted['error'] = service_result.get('error', 'Service failed')
            extracted['available'] = service_result.get('available', False)
            return extracted
        
        # REAL FIX: Your services return data under 'data' key
        service_data = service_result.get('data', {})
        if not service_data:
            logger.warning(f"No 'data' key in {service_name} result")
            # Fallback to extracting from top level
            service_data = service_result
        
        # REAL FIX: Extract all data from the service's data object
        for key, value in service_data.items():
            if key not in ['success', 'service', 'timestamp', 'available', 'analysis_complete']:
                extracted[key] = value
        
        # REAL FIX: Service-specific field mapping for your actual services
        if service_name == 'source_credibility':
            # Your service returns score, level, etc. under data
            extracted.update({
                'credibility_score': service_data.get('score', service_data.get('credibility_score', 50)),
                'credibility_level': service_data.get('level', service_data.get('credibility_level', 'Unknown')),
                'source_type': service_data.get('source_type', 'Unknown'),
                'trust_indicators': service_data.get('trust_indicators', []),
                'findings': service_data.get('findings', [])
            })
            
        elif service_name == 'author_analyzer':
            extracted.update({
                'author_name': service_data.get('author_name', 'Unknown'),
                'author_score': service_data.get('author_score', service_data.get('score', 50)),
                'credentials': service_data.get('credentials', {}),
                'publishing_history': service_data.get('publishing_history', [])
            })
            
        elif service_name == 'bias_detector':
            extracted.update({
                'bias_score': service_data.get('bias_score', service_data.get('score', 0)),
                'bias_direction': service_data.get('bias_direction', 'neutral'),
                'political_leaning': service_data.get('political_leaning', 'center'),
                'loaded_phrases': service_data.get('loaded_phrases', []),
                'patterns': service_data.get('patterns', [])
            })
            
        elif service_name == 'fact_checker':
            extracted.update({
                'fact_checks': service_data.get('fact_checks', []),
                'verified_claims': service_data.get('verified_claims', 0),
                'disputed_claims': service_data.get('disputed_claims', 0),
                'total_claims': service_data.get('total_claims', 0)
            })
            
        elif service_name == 'transparency_analyzer':
            extracted.update({
                'transparency_score': service_data.get('transparency_score', service_data.get('score', 50)),
                'transparency_level': service_data.get('transparency_level', 'Unknown'),
                'checklist_results': service_data.get('checklist_results', {}),
                'recommendations': service_data.get('recommendations', []),
                'indicators': service_data.get('transparency_indicators', service_data.get('indicators', []))
            })
            
        elif service_name == 'manipulation_detector':
            extracted.update({
                'manipulation_score': service_data.get('manipulation_score', service_data.get('score', 0)),
                'tactics_found': service_data.get('tactics_found', []),
                'emotional_language': service_data.get('emotional_language', []),
                'risk_level': service_data.get('risk_level', 'Low')
            })
            
        elif service_name == 'content_analyzer':
            extracted.update({
                'content_score': service_data.get('content_score', service_data.get('score', 50)),
                'quality_score': service_data.get('quality_score', service_data.get('score', 50)),
                'readability_score': service_data.get('readability_score', 50),
                'quality_metrics': service_data.get('quality_metrics', {}),
                'content_structure': service_data.get('content_structure', {})
            })
            
        elif service_name == 'openai_enhancer':
            extracted.update({
                'ai_summary': service_data.get('enhanced_summary', service_data.get('ai_summary', '')),
                'key_insights': service_data.get('key_points', service_data.get('key_insights', [])),
                'credibility_assessment': service_data.get('credibility_assessment', ''),
                'enhancement_score': service_data.get('enhancement_score', service_data.get('score', 50))
            })
        
        return extracted
    
    def _calculate_trust_score_real(self, service_results: Dict[str, Any]) -> int:
        """Calculate trust score from REAL service results"""
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
            if service in service_results and service_results[service].get('success'):
                score = self._extract_service_score_real(service, service_results[service])
                if score is not None:
                    scores.append((score, weight))
                    logger.info(f"Trust score component - {service}: {score} (weight: {weight})")
        
        if not scores:
            logger.warning("No service scores available for trust calculation")
            return 50
        
        # Calculate weighted average
        total_weight = sum(weight for _, weight in scores)
        weighted_sum = sum(score * weight for score, weight in scores)
        
        final_score = int(weighted_sum / total_weight) if total_weight > 0 else 50
        logger.info(f"Final trust score: {final_score} (from {len(scores)} services)")
        return final_score
    
    def _extract_service_score_real(self, service_name: str, data: Dict[str, Any]) -> Optional[int]:
        """Extract score from REAL service data"""
        # REAL FIX: Handle your actual field names
        score_fields = ['credibility_score', 'author_score', 'transparency_score', 
                       'score', 'trust_score', 'overall_score']
        
        # Check common fields first
        for field in score_fields:
            if field in data and isinstance(data[field], (int, float)):
                return int(data[field])
        
        # Service-specific logic for your actual services
        if service_name == 'bias_detector':
            bias_score = data.get('bias_score', 0)
            return max(0, min(100, 100 - int(bias_score)))  # Invert bias score
            
        elif service_name == 'fact_checker':
            verified = data.get('verified_claims', 0)
            disputed = data.get('disputed_claims', 0)
            total = verified + disputed
            if total > 0:
                return int((verified / total) * 100)
            return 75  # Default if no claims
            
        elif service_name == 'manipulation_detector':
            manipulation_score = data.get('manipulation_score', 0)
            tactics_count = len(data.get('tactics_found', []))
            if tactics_count > 5:
                return 20
            elif tactics_count > 2:
                return 50
            else:
                return max(0, min(100, 100 - int(manipulation_score)))
        
        logger.warning(f"No score found for {service_name}")
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
