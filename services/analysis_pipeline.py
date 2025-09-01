"""
COMPLETE FIXED Analysis Pipeline - DATA FLOW SOLUTION
CRITICAL FIXES:
1. Fixed service data extraction to handle your actual service return format
2. Corrected author data extraction from nested structures
3. Ensured all services return data in format frontend expects
4. Fixed timeout handling to prevent worker shutdowns
"""
import asyncio
import time
import logging
from typing import Dict, Any, List, Optional, Set
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
import traceback

from .service_registry import get_service_registry
from .base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)

class AnalysisPipeline:
    """
    COMPLETE FIXED: Pipeline with proper data extraction for your service format
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
        FIXED: Run analysis pipeline with proper data structure handling
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
            logger.info("STARTING COMPLETE FIXED ANALYSIS PIPELINE")
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
            
            # FIXED: Handle your actual service return format
            extractor_result = article_data['article_extractor']
            if not extractor_result.get('success', False):
                logger.error(f"Article extraction failed: {extractor_result.get('error', 'Unknown error')}")
                results['success'] = False
                results['error'] = 'Article extraction failed'
                results['summary'] = 'Could not extract article content'
                return results
            
            # FIXED: Extract article from your service's actual structure
            article_info = self._extract_article_data_fixed(extractor_result)
            results['article'] = article_info
            logger.info(f"Article extracted: '{article_info.get('title', 'No title')[:100]}...'")
            
            # FIXED: Create enriched data for subsequent services
            enriched_data = {**data}
            enriched_data.update(article_info)  # Add article fields to data
            enriched_data['article'] = article_info  # Also provide as nested object
            
            # Stage 2: Core Analysis Services (parallel) - FIXED TIMEOUT HANDLING
            logger.info("STAGE 2: Core Analysis Services (Parallel)")
            stage2_results = self._run_stage_parallel_fixed(self.STAGE_2_SERVICES, enriched_data)
            
            # Stage 3: Fact Checking - FIXED TIMEOUT HANDLING
            logger.info("STAGE 3: Fact Checking")
            stage3_results = self._run_stage_parallel_fixed(self.STAGE_3_SERVICES, enriched_data)
            
            # Stage 4: AI Enhancement (if pro mode) - FIXED TIMEOUT HANDLING
            stage4_results = {}
            if data.get('is_pro', False):
                logger.info("STAGE 4: AI Enhancement")
                stage4_results = self._run_stage_parallel_fixed(self.STAGE_4_SERVICES, enriched_data)
            
            # FIXED: Combine all service results with proper data extraction
            all_service_results = {}
            all_service_results.update(article_data)  # Stage 1
            all_service_results.update(stage2_results)  # Stage 2
            all_service_results.update(stage3_results)  # Stage 3
            all_service_results.update(stage4_results)  # Stage 4
            
            # FIXED: Process results in format frontend expects - THIS IS THE KEY FIX
            processed_results = {}
            successful_services = 0
            
            for service_name, service_result in all_service_results.items():
                logger.info(f"\n=== PROCESSING {service_name.upper()} RESULT ===")
                logger.info(f"Success: {service_result.get('success', False)}")
                logger.info(f"Has data key: {'data' in service_result}")
                logger.info(f"Result keys: {list(service_result.keys())}")
                
                if service_result.get('success', False):
                    # CRITICAL FIX: Extract data using your actual service structure
                    clean_data = self._extract_service_data_fixed(service_name, service_result)
                    processed_results[service_name] = clean_data
                    successful_services += 1
                    logger.info(f"✓ {service_name}: Successfully processed {len(clean_data)} data fields")
                    
                    # DEBUG: Log some key fields to verify extraction
                    if service_name == 'author_analyzer' and 'author_name' in clean_data:
                        logger.info(f"✓ AUTHOR EXTRACTED: {clean_data['author_name']}")
                    if 'score' in clean_data:
                        logger.info(f"✓ SCORE EXTRACTED: {clean_data['score']}")
                        
                else:
                    # Keep failed service info for debugging
                    processed_results[service_name] = {
                        'success': False,
                        'error': service_result.get('error', 'Service failed'),
                        'available': service_result.get('available', False),
                        'service': service_name
                    }
                    error_msg = f"Service {service_name} failed: {service_result.get('error', 'Unknown error')}"
                    results['errors'].append(error_msg)
                    logger.warning(f"✗ {service_name}: {error_msg}")
            
            # FIXED: Store processed results in the format frontend expects
            results.update(processed_results)  # Merge service results directly into main results
            
            # Calculate trust score from successful services
            results['trust_score'] = self._calculate_trust_score_fixed(processed_results)
            results['trust_level'] = self._get_trust_level(results['trust_score'])
            results['summary'] = f"Analysis complete. {successful_services} services provided data."
            
            # Update metadata
            total_time = time.time() - start_time
            results['pipeline_metadata']['total_time'] = total_time
            results['pipeline_metadata']['services_available'] = successful_services
            results['services_available'] = successful_services
            
            logger.info("=" * 80)
            logger.info("COMPLETE FIXED PIPELINE SUMMARY:")
            logger.info(f"Total time: {total_time:.2f}s")
            logger.info(f"Successful services: {successful_services}")
            logger.info(f"Trust score: {results['trust_score']}")
            logger.info(f"Final result keys: {list(results.keys())}")
            
            # DEBUG: Log author data for verification
            if 'author_analyzer' in processed_results:
                auth_data = processed_results['author_analyzer']
                if isinstance(auth_data, dict) and auth_data.get('success'):
                    logger.info(f"✓ FINAL AUTHOR DATA: {auth_data.get('author_name', 'NOT FOUND')}")
                    
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
    
    def _run_stage_parallel_fixed(self, services: List[str], data: Dict[str, Any]) -> Dict[str, Any]:
        """
        CRITICAL FIX: Run services in parallel with INDIVIDUAL timeouts, not collection timeout
        """
        stage_results = {}
        futures = {}
        
        # Submit all tasks
        for service_name in services:
            if not self.registry.is_service_available(service_name):
                logger.warning(f"Service {service_name} not available")
                continue
                
            future = self.executor.submit(self._run_service_with_timeout, service_name, data)
            futures[future] = service_name
        
        # CRITICAL FIX: Collect results with individual service handling
        completed_count = 0
        total_futures = len(futures)
        max_wait_time = 60  # Maximum time to wait for all services
        start_time = time.time()
        
        # Wait for each future individually
        for future in futures:
            service_name = futures[future]
            remaining_time = max_wait_time - (time.time() - start_time)
            
            if remaining_time <= 0:
                logger.warning(f"Service {service_name} timed out (pipeline max time exceeded)")
                stage_results[service_name] = {
                    'success': False,
                    'error': 'Pipeline timeout exceeded',
                    'service': service_name,
                    'available': False
                }
                continue
            
            try:
                # Wait for individual service with remaining time
                result, duration = future.result(timeout=min(remaining_time, 45))
                stage_results[service_name] = result
                completed_count += 1
                logger.info(f"Service {service_name} completed in {duration:.2f}s ({completed_count}/{total_futures})")
                
            except TimeoutError:
                logger.warning(f"Service {service_name} timed out after 45s")
                stage_results[service_name] = {
                    'success': False,
                    'error': 'Service timeout (45s)',
                    'service': service_name,
                    'available': False
                }
                
            except Exception as e:
                logger.error(f"Service {service_name} failed: {str(e)}", exc_info=True)
                stage_results[service_name] = {
                    'success': False,
                    'error': str(e),
                    'service': service_name,
                    'available': False
                }
        
        logger.info(f"Parallel stage completed: {completed_count}/{total_futures} services successful")
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
    
    def _extract_article_data_fixed(self, extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """FIXED: Extract article data from your actual service format"""
        if not extraction_result.get('success'):
            return {
                'title': 'Unknown Title',
                'text': '',
                'author': 'Unknown',
                'url': '',
                'extraction_successful': False
            }
        
        # FIXED: Your services return data under 'data' key
        article_data = extraction_result.get('data', {})
        
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
    
    def _extract_service_data_fixed(self, service_name: str, service_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        CRITICAL FIX: Extract data from your actual service formats
        This is the key method that fixes the data flow issue
        """
        logger.info(f"=== EXTRACTING DATA FROM {service_name.upper()} ===")
        
        # Start with base service info
        extracted = {
            'success': service_result.get('success', False),
            'service': service_name,
            'timestamp': service_result.get('timestamp', time.time()),
            'available': service_result.get('available', True)
        }
        
        # If service failed, return minimal info
        if not service_result.get('success', False):
            extracted['error'] = service_result.get('error', 'Service failed')
            logger.info(f"Service {service_name} failed: {extracted['error']}")
            return extracted
        
        # CRITICAL FIX: Your services return data under 'data' key
        service_data = service_result.get('data', {})
        if not service_data:
            logger.warning(f"No 'data' key in {service_name} result, using top-level data")
            # Fallback: extract from top level, excluding metadata
            service_data = {k: v for k, v in service_result.items() 
                          if k not in ['success', 'service', 'timestamp', 'available', 'metadata']}
        
        logger.info(f"Service data keys for {service_name}: {list(service_data.keys())}")
        
        # CRITICAL FIX: Copy ALL data from the service's data object
        for key, value in service_data.items():
            if key not in ['success', 'service', 'timestamp', 'available']:
                extracted[key] = value
        
        # CRITICAL FIX: Service-specific field mapping for your actual services
        if service_name == 'source_credibility':
            # Ensure all expected fields exist
            extracted.update({
                'credibility_score': service_data.get('score', service_data.get('credibility_score', 50)),
                'credibility_level': service_data.get('level', service_data.get('credibility_level', 'Unknown')),
                'source_type': service_data.get('source_type', 'Unknown'),
                'source_name': service_data.get('source_name', 'Unknown Source'),
                'trust_indicators': service_data.get('trust_indicators', []),
                'findings': service_data.get('findings', []),
                'score': service_data.get('score', service_data.get('credibility_score', 50))
            })
            
        elif service_name == 'author_analyzer':
            # CRITICAL FIX: Ensure author_name is properly extracted
            author_name = (service_data.get('author_name') or 
                          service_data.get('name') or 
                          service_data.get('author') or 
                          'Unknown')
            
            extracted.update({
                'author_name': author_name,
                'author_score': service_data.get('author_score', service_data.get('score', 50)),
                'score': service_data.get('score', service_data.get('author_score', 50)),
                'credibility_score': service_data.get('credibility_score', service_data.get('score', 50)),
                'verified': service_data.get('verified', False),
                'bio': service_data.get('bio', ''),
                'position': service_data.get('position', ''),
                'credentials': service_data.get('credentials', {}),
                'social_media': service_data.get('social_media', {}),
                'linkedin_profile': service_data.get('linkedin_profile'),
                'twitter_profile': service_data.get('twitter_profile'),
                'wikipedia_page': service_data.get('wikipedia_page'),
                'personal_website': service_data.get('personal_website'),
                'muckrack_profile': service_data.get('muckrack_profile'),
                'publishing_history': service_data.get('publishing_history', []),
                'additional_links': service_data.get('additional_links', {}),
                'level': service_data.get('level', 'Unknown')
            })
            
            logger.info(f"✓ AUTHOR DATA EXTRACTED: {author_name} (score: {extracted['score']})")
            
        elif service_name == 'bias_detector':
            extracted.update({
                'bias_score': service_data.get('bias_score', service_data.get('score', 0)),
                'score': service_data.get('score', service_data.get('bias_score', 0)),
                'bias_direction': service_data.get('bias_direction', 'neutral'),
                'bias_level': service_data.get('bias_level', service_data.get('level', 'Unknown')),
                'political_leaning': service_data.get('political_leaning', 'center'),
                'loaded_phrases': service_data.get('loaded_phrases', []),
                'patterns': service_data.get('patterns', []),
                'level': service_data.get('level', service_data.get('bias_level', 'Unknown'))
            })
            
        elif service_name == 'fact_checker':
            extracted.update({
                'fact_checks': service_data.get('fact_checks', []),
                'verification_score': service_data.get('verification_score', service_data.get('score', 50)),
                'score': service_data.get('score', service_data.get('verification_score', 50)),
                'verified_claims': service_data.get('verified_claims', 0),
                'disputed_claims': service_data.get('disputed_claims', 0),
                'total_claims': service_data.get('total_claims', 0),
                'claims_checked': service_data.get('claims_checked', 0),
                'level': service_data.get('level', service_data.get('verification_level', 'Unknown'))
            })
            
        elif service_name == 'transparency_analyzer':
            extracted.update({
                'transparency_score': service_data.get('transparency_score', service_data.get('score', 50)),
                'score': service_data.get('score', service_data.get('transparency_score', 50)),
                'transparency_level': service_data.get('transparency_level', service_data.get('level', 'Unknown')),
                'checklist_results': service_data.get('checklist_results', {}),
                'recommendations': service_data.get('recommendations', []),
                'indicators': service_data.get('transparency_indicators', service_data.get('indicators', [])),
                'level': service_data.get('level', service_data.get('transparency_level', 'Unknown'))
            })
            
        elif service_name == 'manipulation_detector':
            extracted.update({
                'manipulation_score': service_data.get('manipulation_score', service_data.get('score', 0)),
                'score': service_data.get('score', service_data.get('manipulation_score', 0)),
                'tactics_found': service_data.get('tactics_found', []),
                'emotional_language': service_data.get('emotional_language', []),
                'risk_level': service_data.get('risk_level', service_data.get('level', 'Low')),
                'level': service_data.get('level', service_data.get('risk_level', 'Low'))
            })
            
        elif service_name == 'content_analyzer':
            extracted.update({
                'content_score': service_data.get('content_score', service_data.get('score', 50)),
                'score': service_data.get('score', service_data.get('content_score', 50)),
                'quality_score': service_data.get('quality_score', service_data.get('score', 50)),
                'readability_score': service_data.get('readability_score', 50),
                'quality_metrics': service_data.get('quality_metrics', {}),
                'content_structure': service_data.get('content_structure', {}),
                'level': service_data.get('level', 'Unknown')
            })
            
        elif service_name == 'openai_enhancer':
            extracted.update({
                'ai_summary': service_data.get('enhanced_summary', service_data.get('ai_summary', '')),
                'key_insights': service_data.get('key_points', service_data.get('key_insights', [])),
                'credibility_assessment': service_data.get('credibility_assessment', ''),
                'enhancement_score': service_data.get('enhancement_score', service_data.get('score', 50)),
                'score': service_data.get('score', service_data.get('enhancement_score', 50))
            })
        
        logger.info(f"✓ {service_name}: Extracted {len(extracted)} total fields")
        return extracted
    
    def _calculate_trust_score_fixed(self, service_results: Dict[str, Any]) -> int:
        """Calculate trust score from FIXED service results"""
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
                score = self._extract_service_score_fixed(service, service_results[service])
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
    
    def _extract_service_score_fixed(self, service_name: str, data: Dict[str, Any]) -> Optional[int]:
        """Extract score from FIXED service data"""
        # FIXED: Handle your actual field names with proper fallbacks
        score_fields = ['score', 'credibility_score', 'author_score', 'transparency_score', 
                       'verification_score', 'trust_score', 'overall_score']
        
        # Check common fields first
        for field in score_fields:
            if field in data and isinstance(data[field], (int, float)):
                score = int(data[field])
                logger.info(f"Found score for {service_name}: {field} = {score}")
                return score
        
        # Service-specific logic for your actual services
        if service_name == 'bias_detector':
            bias_score = data.get('bias_score', 0)
            if isinstance(bias_score, (int, float)):
                inverted = max(0, min(100, 100 - int(bias_score)))  # Invert bias score
                logger.info(f"Inverted bias score for {service_name}: {bias_score} -> {inverted}")
                return inverted
            
        elif service_name == 'fact_checker':
            verified = data.get('verified_claims', 0)
            disputed = data.get('disputed_claims', 0)
            total = verified + disputed
            if total > 0:
                score = int((verified / total) * 100)
                logger.info(f"Calculated fact check score: {verified}/{total} = {score}")
                return score
            return 75  # Default if no claims
            
        elif service_name == 'manipulation_detector':
            manipulation_score = data.get('manipulation_score', 0)
            tactics_count = len(data.get('tactics_found', []))
            if tactics_count > 5:
                return 20
            elif tactics_count > 2:
                return 50
            elif isinstance(manipulation_score, (int, float)):
                inverted = max(0, min(100, 100 - int(manipulation_score)))
                logger.info(f"Inverted manipulation score: {manipulation_score} -> {inverted}")
                return inverted
        
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
