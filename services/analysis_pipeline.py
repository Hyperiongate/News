"""
COMPLETE FIXED Analysis Pipeline - DATA FLOW SOLUTION
CRITICAL FIXES:
1. Fixed service data extraction to handle actual service return format
2. Corrected author data extraction from nested structures  
3. Ensured all services return data in format frontend expects
4. Fixed timeout handling to prevent worker shutdowns
5. FIXED: Proper article data propagation to frontend
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
            
            # CRITICAL FIX: Extract article from the actual service structure
            article_info = self._extract_article_data_bulletproof(extractor_result)
            results['article'] = article_info
            logger.info(f"✓ ARTICLE EXTRACTED: '{article_info.get('title', 'No title')[:50]}...'")
            logger.info(f"✓ ARTICLE AUTHOR: '{article_info.get('author', 'Unknown')}'")
            logger.info(f"✓ ARTICLE WORD COUNT: {article_info.get('word_count', 0)}")
            
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
            
            # CRITICAL FIX: Process results in format frontend expects
            processed_results = {}
            successful_services = 0
            
            for service_name, service_result in all_service_results.items():
                logger.info(f"\n=== PROCESSING {service_name.upper()} RESULT ===")
                logger.info(f"Success: {service_result.get('success', False)}")
                logger.info(f"Has data key: {'data' in service_result}")
                logger.info(f"Result keys: {list(service_result.keys())}")
                
                if service_result.get('success', False):
                    # CRITICAL FIX: Extract data using the actual service structure
                    clean_data = self._extract_service_data_bulletproof(service_name, service_result)
                    processed_results[service_name] = clean_data
                    successful_services += 1
                    logger.info(f"✓ {service_name}: Successfully processed {len(clean_data)} data fields")
                    
                    # DEBUG: Log key fields to verify extraction
                    if service_name == 'author_analyzer' and clean_data.get('author_name'):
                        logger.info(f"✓ AUTHOR EXTRACTED: {clean_data['author_name']}")
                    if clean_data.get('score') is not None:
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
            results['trust_score'] = self._calculate_trust_score_bulletproof(processed_results)
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
            
            # DEBUG: Verify article data is preserved for frontend
            final_article = results.get('article', {})
            logger.info(f"✓ FINAL ARTICLE TITLE: {final_article.get('title', 'NOT FOUND')}")
            logger.info(f"✓ FINAL ARTICLE AUTHOR: {final_article.get('author', 'NOT FOUND')}")
            logger.info(f"✓ FINAL ARTICLE URL: {final_article.get('url', 'NOT FOUND')}")
            
            # DEBUG: Log author analyzer data for verification
            if 'author_analyzer' in processed_results:
                auth_data = processed_results['author_analyzer']
                if isinstance(auth_data, dict) and auth_data.get('success'):
                    logger.info(f"✓ FINAL AUTHOR ANALYZER DATA: {auth_data.get('author_name', 'NOT FOUND')}")
                    
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}", exc_info=True)
            results['success'] = False
            results['error'] = str(e)
            results['summary'] = f'Pipeline failed: {str(e)}'
            
        return results
    
    def _extract_article_data_bulletproof(self, extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        BULLETPROOF: Extract article data from any service format
        """
        logger.info("=== BULLETPROOF ARTICLE EXTRACTION ===")
        
        if not extraction_result.get('success'):
            logger.warning("Extraction result marked as failed")
            return {
                'title': 'Unknown Title',
                'text': '',
                'author': 'Unknown',
                'url': '',
                'domain': '',
                'extraction_successful': False
            }
        
        # Strategy 1: Check for 'data' wrapper (your services use this)
        article_data = {}
        if 'data' in extraction_result and isinstance(extraction_result['data'], dict):
            article_data = extraction_result['data']
            logger.info(f"Found data wrapper with keys: {list(article_data.keys())}")
        else:
            # Fallback: use top-level data
            article_data = {k: v for k, v in extraction_result.items() 
                          if k not in ['success', 'service', 'timestamp', 'available', 'extraction_metadata']}
            logger.info(f"Using top-level data with keys: {list(article_data.keys())}")
        
        # Strategy 2: Handle nested article structure
        if 'article' in article_data and isinstance(article_data['article'], dict):
            article_data = article_data['article']
            logger.info("Found nested article structure")
        
        # Strategy 3: Extract with comprehensive field mapping
        extracted = {
            'title': (article_data.get('title') or 
                     article_data.get('headline') or 
                     'Unknown Title'),
            'text': (article_data.get('text') or 
                    article_data.get('content') or 
                    article_data.get('body') or ''),
            'author': (article_data.get('author') or 
                      article_data.get('author_name') or 
                      article_data.get('byline') or 
                      'Unknown'),
            'publish_date': (article_data.get('publish_date') or 
                           article_data.get('date') or 
                           article_data.get('published_date') or ''),
            'domain': (article_data.get('domain') or 
                      article_data.get('source') or 
                      article_data.get('site_name') or ''),
            'url': (article_data.get('url') or 
                   article_data.get('link') or ''),
            'word_count': (article_data.get('word_count') or 
                         len(str(article_data.get('text', '')).split())),
            'language': article_data.get('language', 'en'),
            'extraction_successful': True
        }
        
        # Log what we extracted
        logger.info(f"✓ Extracted title: {extracted['title'][:50]}...")
        logger.info(f"✓ Extracted author: {extracted['author']}")
        logger.info(f"✓ Extracted domain: {extracted['domain']}")
        logger.info(f"✓ Word count: {extracted['word_count']}")
        
        return extracted
    
    def _extract_service_data_bulletproof(self, service_name: str, service_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        BULLETPROOF: Extract data from any service format with comprehensive field mapping
        """
        logger.info(f"=== BULLETPROOF EXTRACTION FROM {service_name.upper()} ===")
        
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
            extracted['score'] = 0
            extracted['level'] = 'Error'
            logger.info(f"Service {service_name} failed: {extracted['error']}")
            return extracted
        
        # CRITICAL FIX: Extract data from any wrapper format
        service_data = {}
        
        # Strategy 1: Check for 'data' wrapper
        if 'data' in service_result and isinstance(service_result['data'], dict):
            service_data = service_result['data']
            logger.info(f"Found data wrapper with {len(service_data)} keys")
        else:
            # Strategy 2: Use top-level data (excluding metadata)
            metadata_keys = {'success', 'service', 'timestamp', 'available', 'error', 'processing_time', 'metadata'}
            service_data = {k: v for k, v in service_result.items() if k not in metadata_keys}
            logger.info(f"Using top-level data with {len(service_data)} keys")
        
        # Copy all non-metadata fields
        for key, value in service_data.items():
            if key not in ['success', 'service', 'timestamp', 'available']:
                extracted[key] = value
        
        # CRITICAL FIX: Service-specific field mapping with bulletproof fallbacks
        if service_name == 'source_credibility':
            extracted.update({
                'credibility_score': self._extract_score(service_data, ['score', 'credibility_score', 'trust_score'], 50),
                'credibility_level': self._extract_level(service_data, ['level', 'credibility_level', 'trust_level'], 'Unknown'),
                'source_type': service_data.get('source_type', 'Unknown'),
                'source_name': service_data.get('source_name', 'Unknown Source'),
                'trust_indicators': service_data.get('trust_indicators', []),
                'findings': service_data.get('findings', [])
            })
            # Ensure score field exists
            if 'score' not in extracted:
                extracted['score'] = extracted['credibility_score']
            
        elif service_name == 'author_analyzer':
            # BULLETPROOF author extraction
            author_name = self._extract_author_name(service_data)
            author_score = self._extract_score(service_data, ['score', 'author_score', 'credibility_score'], 50)
            
            extracted.update({
                'author_name': author_name,
                'author_score': author_score,
                'score': author_score,
                'credibility_score': author_score,
                'verified': service_data.get('verified', False),
                'bio': service_data.get('bio', ''),
                'position': service_data.get('position', ''),
                'credentials': service_data.get('credentials', {}),
                'social_media': service_data.get('social_media', {}),
                'publishing_history': service_data.get('publishing_history', []),
                'level': self._extract_level(service_data, ['level', 'credibility_level'], 'Unknown')
            })
            
            logger.info(f"✓ AUTHOR BULLETPROOF: {author_name} (score: {author_score})")
            
        elif service_name == 'bias_detector':
            bias_score = self._extract_score(service_data, ['bias_score', 'score'], 0)
            extracted.update({
                'bias_score': bias_score,
                'score': bias_score,
                'bias_direction': service_data.get('bias_direction', 'neutral'),
                'bias_level': self._extract_level(service_data, ['level', 'bias_level'], 'Unknown'),
                'political_leaning': service_data.get('political_leaning', 'center'),
                'loaded_phrases': service_data.get('loaded_phrases', []),
                'patterns': service_data.get('patterns', []),
                'level': self._extract_level(service_data, ['level', 'bias_level'], 'Unknown')
            })
            
        elif service_name == 'fact_checker':
            verification_score = self._extract_score(service_data, ['verification_score', 'score', 'factual_score'], 50)
            extracted.update({
                'fact_checks': service_data.get('fact_checks', []),
                'verification_score': verification_score,
                'score': verification_score,
                'verified_claims': service_data.get('verified_claims', 0),
                'disputed_claims': service_data.get('disputed_claims', 0),
                'total_claims': service_data.get('total_claims', 0),
                'level': self._extract_level(service_data, ['level', 'verification_level'], 'Unknown')
            })
            
        elif service_name == 'transparency_analyzer':
            transparency_score = self._extract_score(service_data, ['transparency_score', 'score'], 50)
            extracted.update({
                'transparency_score': transparency_score,
                'score': transparency_score,
                'transparency_level': self._extract_level(service_data, ['level', 'transparency_level'], 'Unknown'),
                'checklist_results': service_data.get('checklist_results', {}),
                'recommendations': service_data.get('recommendations', []),
                'indicators': service_data.get('transparency_indicators', service_data.get('indicators', [])),
                'level': self._extract_level(service_data, ['level', 'transparency_level'], 'Unknown')
            })
            
        elif service_name == 'manipulation_detector':
            manipulation_score = self._extract_score(service_data, ['manipulation_score', 'score'], 0)
            extracted.update({
                'manipulation_score': manipulation_score,
                'score': manipulation_score,
                'tactics_found': service_data.get('tactics_found', []),
                'emotional_language': service_data.get('emotional_language', []),
                'risk_level': self._extract_level(service_data, ['level', 'risk_level'], 'Low'),
                'level': self._extract_level(service_data, ['level', 'risk_level'], 'Low')
            })
            
        elif service_name == 'content_analyzer':
            content_score = self._extract_score(service_data, ['content_score', 'quality_score', 'score'], 50)
            extracted.update({
                'content_score': content_score,
                'score': content_score,
                'quality_score': content_score,
                'readability_score': service_data.get('readability_score', 50),
                'quality_metrics': service_data.get('quality_metrics', {}),
                'content_structure': service_data.get('content_structure', {}),
                'level': self._extract_level(service_data, ['level', 'quality_level'], 'Unknown')
            })
            
        elif service_name == 'openai_enhancer':
            enhancement_score = self._extract_score(service_data, ['enhancement_score', 'score'], 50)
            extracted.update({
                'ai_summary': service_data.get('enhanced_summary', service_data.get('ai_summary', '')),
                'key_insights': service_data.get('key_points', service_data.get('key_insights', [])),
                'credibility_assessment': service_data.get('credibility_assessment', ''),
                'enhancement_score': enhancement_score,
                'score': enhancement_score
            })
        
        # Ensure every service has score and level
        if 'score' not in extracted or extracted['score'] is None:
            extracted['score'] = 50
        if 'level' not in extracted or not extracted['level']:
            extracted['level'] = 'Unknown'
        
        logger.info(f"✓ {service_name}: Extracted {len(extracted)} fields (score: {extracted.get('score')})")
        return extracted
    
    def _extract_score(self, data: Dict[str, Any], field_names: List[str], default: int) -> int:
        """Extract score with fallbacks"""
        for field in field_names:
            if field in data and isinstance(data[field], (int, float)):
                return max(0, min(100, int(data[field])))
        return default
    
    def _extract_level(self, data: Dict[str, Any], field_names: List[str], default: str) -> str:
        """Extract level with fallbacks"""
        for field in field_names:
            if field in data and data[field]:
                return str(data[field])
        return default
    
    def _extract_author_name(self, data: Dict[str, Any]) -> str:
        """BULLETPROOF author name extraction"""
        author_fields = ['author_name', 'name', 'author', 'byline', 'writer']
        
        for field in author_fields:
            if field in data and data[field]:
                author = str(data[field]).strip()
                if author and author.lower() not in ['unknown', 'null', 'none', '']:
                    return author
        
        return 'Unknown'
    
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
        CRITICAL FIX: Run services in parallel with INDIVIDUAL timeouts
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
        max_wait_time = 90  # Maximum time to wait for all services
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
                result, duration = future.result(timeout=min(remaining_time, 60))
                stage_results[service_name] = result
                completed_count += 1
                logger.info(f"Service {service_name} completed in {duration:.2f}s ({completed_count}/{total_futures})")
                
            except TimeoutError:
                logger.warning(f"Service {service_name} timed out after 60s")
                stage_results[service_name] = {
                    'success': False,
                    'error': 'Service timeout (60s)',
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
    
    def _calculate_trust_score_bulletproof(self, service_results: Dict[str, Any]) -> int:
        """Calculate trust score from service results with bulletproof handling"""
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
                score = self._extract_service_score_bulletproof(service, service_results[service])
                if score is not None:
                    scores.append((score, weight))
                    logger.info(f"Trust component - {service}: {score} (weight: {weight})")
        
        if not scores:
            logger.warning("No service scores available for trust calculation")
            return 30  # Low default
        
        # Calculate weighted average
        total_weight = sum(weight for _, weight in scores)
        weighted_sum = sum(score * weight for score, weight in scores)
        
        final_score = int(weighted_sum / total_weight) if total_weight > 0 else 30
        logger.info(f"Final trust score: {final_score} (from {len(scores)} services)")
        return max(0, min(100, final_score))
    
    def _extract_service_score_bulletproof(self, service_name: str, data: Dict[str, Any]) -> Optional[int]:
        """Extract score from service data with bulletproof handling"""
        # Get score using the extraction helper
        score = data.get('score')
        if isinstance(score, (int, float)):
            score = int(score)
            
            # Handle services where higher score = worse (invert them)
            if service_name in ['bias_detector', 'manipulation_detector']:
                return max(0, min(100, 100 - score))
            
            return max(0, min(100, score))
        
        # Fallback calculations for specific services
        if service_name == 'fact_checker':
            verified = data.get('verified_claims', 0)
            disputed = data.get('disputed_claims', 0) 
            total = verified + disputed
            if total > 0:
                return int((verified / total) * 100)
            return 70  # Default for fact checker
            
        elif service_name == 'author_analyzer':
            # If author is known, give base score
            author = data.get('author_name', 'Unknown')
            if author and author.lower() not in ['unknown', 'null', 'none']:
                return 60  # Known author baseline
        
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
