"""
Analysis Pipeline - COMPLETE DATA FLOW FIX
CRITICAL FIXES:
1. Fixed service data extraction to handle actual service return format
2. Proper article data extraction from nested structures
3. Bulletproof field mapping for all services
4. Fixed timeout handling to prevent worker shutdowns
"""
import time
import logging
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import traceback

from .service_registry import get_service_registry

logger = logging.getLogger(__name__)

class AnalysisPipeline:
    """
    COMPLETE FIX: Pipeline with proper data extraction for service format
    """
    
    def __init__(self):
        self.registry = get_service_registry()
        self.executor = ThreadPoolExecutor(max_workers=8)
        
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis method with fixed data structure handling
        """
        start_time = time.time()
        logger.info("=" * 80)
        logger.info("STARTING FIXED ANALYSIS PIPELINE")
        logger.info(f"Input data keys: {list(data.keys())}")
        logger.info("=" * 80)
        
        # Initialize results structure
        results = {
            'success': True,
            'article': {},
            'trust_score': 50,
            'trust_level': 'Unknown',
            'summary': 'Analysis in progress...',
            'services_available': 0,
            'errors': []
        }
        
        try:
            # Stage 1: Article Extraction (sequential - required first)
            logger.info("STAGE 1: Article Extraction")
            article_result = self._extract_article(data)
            
            if not article_result or not article_result.get('success'):
                error_msg = article_result.get('error', 'Article extraction failed') if article_result else 'No article data'
                logger.error(f"Article extraction failed: {error_msg}")
                results.update({
                    'success': False,
                    'error': 'Article extraction failed',
                    'summary': 'Could not extract article content'
                })
                return results
            
            # CRITICAL FIX: Extract article data from proper wrapper format
            article_data = self._extract_article_data_fixed(article_result)
            results['article'] = article_data
            logger.info(f"✓ Article extracted: '{article_data.get('title', 'No title')[:50]}...'")
            logger.info(f"✓ Author found: {article_data.get('author', 'Unknown')}")
            logger.info(f"✓ Domain: {article_data.get('domain', 'Unknown')}")
            
            # Create enriched data for other services
            enriched_data = {**data}
            enriched_data.update(article_data)
            enriched_data['article'] = article_data
            
            # Stage 2: Core Analysis Services (parallel)
            logger.info("STAGE 2: Core Analysis Services")
            core_services = [
                'source_credibility', 'author_analyzer', 'bias_detector', 
                'transparency_analyzer', 'manipulation_detector', 'content_analyzer'
            ]
            core_results = self._run_services_parallel(core_services, enriched_data)
            
            # Stage 3: Fact Checking
            logger.info("STAGE 3: Fact Checking")
            fact_results = self._run_services_parallel(['fact_checker'], enriched_data)
            
            # Stage 4: AI Enhancement (if pro mode)
            ai_results = {}
            if data.get('is_pro', False):
                logger.info("STAGE 4: AI Enhancement")
                ai_results = self._run_services_parallel(['openai_enhancer'], enriched_data)
            
            # Combine all service results
            all_services = {}
            all_services.update(core_results)
            all_services.update(fact_results)
            all_services.update(ai_results)
            
            # CRITICAL FIX: Process each service result with proper data extraction
            processed_results = {}
            successful_services = 0
            
            for service_name, service_result in all_services.items():
                logger.info(f"\n=== PROCESSING {service_name.upper()} ===")
                
                if service_result and service_result.get('success', False):
                    # Extract data using fixed method
                    clean_data = self._extract_service_data_fixed(service_name, service_result)
                    processed_results[service_name] = clean_data
                    successful_services += 1
                    logger.info(f"✓ {service_name}: Processed successfully (score: {clean_data.get('score', 'N/A')})")
                else:
                    # Handle failed service
                    error_msg = service_result.get('error', 'Service failed') if service_result else 'No response'
                    processed_results[service_name] = {
                        'success': False,
                        'error': error_msg,
                        'service': service_name,
                        'score': 0,
                        'level': 'Error'
                    }
                    results['errors'].append(f"{service_name}: {error_msg}")
                    logger.warning(f"✗ {service_name}: {error_msg}")
            
            # Store processed results
            results.update(processed_results)
            
            # Calculate trust score
            results['trust_score'] = self._calculate_trust_score(processed_results)
            results['trust_level'] = self._get_trust_level(results['trust_score'])
            results['summary'] = f"Analysis complete. {successful_services} services provided data."
            results['services_available'] = successful_services
            
            # Final logging
            total_time = time.time() - start_time
            logger.info("=" * 80)
            logger.info("FIXED PIPELINE COMPLETE")
            logger.info(f"Time: {total_time:.2f}s | Services: {successful_services} | Trust: {results['trust_score']}")
            logger.info(f"Final article title: {article_data.get('title', 'Unknown')}")
            logger.info(f"Final article author: {article_data.get('author', 'Unknown')}")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}", exc_info=True)
            results.update({
                'success': False,
                'error': str(e),
                'summary': f'Pipeline failed: {str(e)}'
            })
        
        return results
    
    def _extract_article(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract article using article_extractor service"""
        if not self.registry.is_service_available('article_extractor'):
            return None
            
        try:
            return self.registry.analyze_with_service('article_extractor', data)
        except Exception as e:
            logger.error(f"Article extraction failed: {e}")
            return None
    
    def _extract_article_data_fixed(self, extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        CRITICAL FIX: Extract article data from actual service format
        """
        logger.info("=== EXTRACTING ARTICLE DATA ===")
        
        if not extraction_result.get('success'):
            logger.warning("Article extraction was not successful")
            return {
                'title': 'Unknown Title',
                'text': '',
                'author': 'Unknown',
                'url': '',
                'domain': '',
                'extraction_successful': False
            }
        
        # CRITICAL FIX: Handle the actual data wrapper format
        article_data = {}
        
        # Strategy 1: Look for 'data' wrapper (your services use this)
        if 'data' in extraction_result and isinstance(extraction_result['data'], dict):
            article_data = extraction_result['data']
            logger.info(f"Found data wrapper with keys: {list(article_data.keys())}")
        else:
            # Strategy 2: Look at top level (excluding metadata)
            metadata_keys = {'success', 'service', 'timestamp', 'available', 'extraction_metadata'}
            article_data = {k: v for k, v in extraction_result.items() if k not in metadata_keys}
            logger.info(f"Using top-level data with keys: {list(article_data.keys())}")
        
        # Extract with comprehensive field mapping and fallbacks
        extracted = {
            'title': article_data.get('title', 'Unknown Title'),
            'text': article_data.get('text', article_data.get('content', '')),
            'author': article_data.get('author', 'Unknown'),
            'publish_date': article_data.get('publish_date', article_data.get('date', '')),
            'domain': self._clean_domain(article_data.get('domain', '')),
            'url': article_data.get('url', ''),
            'word_count': article_data.get('word_count', 0),
            'language': article_data.get('language', 'en'),
            'extraction_successful': article_data.get('extraction_successful', False)
        }
        
        # Log what was extracted
        logger.info(f"✓ Extracted title: {extracted['title'][:50]}...")
        logger.info(f"✓ Extracted author: {extracted['author']}")
        logger.info(f"✓ Extracted domain: {extracted['domain']}")
        logger.info(f"✓ Word count: {extracted['word_count']}")
        
        return extracted
    
    def _clean_domain(self, domain: str) -> str:
        """Clean domain name for display"""
        if not domain:
            return ''
        
        # Remove www prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Remove protocol if present
        if domain.startswith('http://'):
            domain = domain[7:]
        elif domain.startswith('https://'):
            domain = domain[8:]
        
        # Remove trailing slash
        if domain.endswith('/'):
            domain = domain[:-1]
        
        return domain
    
    def _run_services_parallel(self, services: List[str], data: Dict[str, Any]) -> Dict[str, Any]:
        """Run services in parallel with timeout protection"""
        results = {}
        futures = {}
        
        # Submit tasks
        for service_name in services:
            if self.registry.is_service_available(service_name):
                future = self.executor.submit(self._run_single_service, service_name, data)
                futures[future] = service_name
        
        # Collect results with individual timeouts
        for future in futures:
            service_name = futures[future]
            try:
                result = future.result(timeout=60)  # 60 second timeout per service
                results[service_name] = result
            except TimeoutError:
                logger.warning(f"{service_name} timed out")
                results[service_name] = {
                    'success': False,
                    'error': 'Service timeout',
                    'service': service_name
                }
            except Exception as e:
                logger.error(f"{service_name} failed: {e}")
                results[service_name] = {
                    'success': False,
                    'error': str(e),
                    'service': service_name
                }
        
        return results
    
    def _run_single_service(self, service_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single service with error handling"""
        try:
            return self.registry.analyze_with_service(service_name, data)
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'service': service_name
            }
    
    def _extract_service_data_fixed(self, service_name: str, service_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        CRITICAL FIX: Extract data from service results with proper field mapping
        """
        # Base service info
        extracted = {
            'success': service_result.get('success', False),
            'service': service_name,
            'timestamp': service_result.get('timestamp', time.time()),
            'available': True
        }
        
        if not service_result.get('success', False):
            extracted.update({
                'error': service_result.get('error', 'Service failed'),
                'score': 0,
                'level': 'Error'
            })
            return extracted
        
        # CRITICAL FIX: Extract data from wrapper format
        service_data = service_result.get('data', {})
        if not service_data:
            # Fallback to top-level data
            metadata_keys = {'success', 'service', 'timestamp', 'available', 'error'}
            service_data = {k: v for k, v in service_result.items() if k not in metadata_keys}
        
        # Copy all data fields
        for key, value in service_data.items():
            extracted[key] = value
        
        # Service-specific field mapping with fallbacks
        if service_name == 'source_credibility':
            extracted.update({
                'credibility_score': service_data.get('score', service_data.get('credibility_score', 50)),
                'credibility_level': service_data.get('level', service_data.get('credibility_level', 'Unknown')),
                'source_name': service_data.get('source_name', 'Unknown Source'),
                'source_type': service_data.get('source_type', 'Unknown'),
                'trust_indicators': service_data.get('trust_indicators', []),
                'findings': service_data.get('findings', [])
            })
            if 'score' not in extracted:
                extracted['score'] = extracted['credibility_score']
        
        elif service_name == 'author_analyzer':
            author_name = (service_data.get('author_name') or 
                          service_data.get('name') or 
                          service_data.get('author') or 'Unknown')
            author_score = service_data.get('score', service_data.get('author_score', 50))
            
            extracted.update({
                'author_name': author_name,
                'author_score': author_score,
                'score': author_score,
                'credibility_score': author_score,
                'verified': service_data.get('verified', False),
                'bio': service_data.get('bio', ''),
                'credentials': service_data.get('credentials', {}),
                'level': service_data.get('level', 'Unknown')
            })
        
        elif service_name == 'bias_detector':
            bias_score = service_data.get('bias_score', service_data.get('score', 0))
            extracted.update({
                'bias_score': bias_score,
                'score': bias_score,
                'bias_direction': service_data.get('bias_direction', 'neutral'),
                'bias_level': service_data.get('level', service_data.get('bias_level', 'Unknown')),
                'political_leaning': service_data.get('political_leaning', 'center'),
                'loaded_phrases': service_data.get('loaded_phrases', []),
                'level': service_data.get('level', service_data.get('bias_level', 'Unknown'))
            })
        
        elif service_name == 'fact_checker':
            verification_score = service_data.get('verification_score', service_data.get('score', 50))
            extracted.update({
                'fact_checks': service_data.get('fact_checks', []),
                'verification_score': verification_score,
                'score': verification_score,
                'verified_claims': service_data.get('verified_claims', 0),
                'disputed_claims': service_data.get('disputed_claims', 0),
                'total_claims': service_data.get('total_claims', 0),
                'level': service_data.get('level', 'Unknown')
            })
        
        elif service_name == 'transparency_analyzer':
            transparency_score = service_data.get('transparency_score', service_data.get('score', 50))
            extracted.update({
                'transparency_score': transparency_score,
                'score': transparency_score,
                'transparency_level': service_data.get('level', service_data.get('transparency_level', 'Unknown')),
                'checklist_results': service_data.get('checklist_results', {}),
                'recommendations': service_data.get('recommendations', []),
                'indicators': service_data.get('indicators', []),
                'level': service_data.get('level', service_data.get('transparency_level', 'Unknown'))
            })
        
        elif service_name == 'manipulation_detector':
            manipulation_score = service_data.get('manipulation_score', service_data.get('score', 0))
            extracted.update({
                'manipulation_score': manipulation_score,
                'score': manipulation_score,
                'tactics_found': service_data.get('tactics_found', []),
                'emotional_language': service_data.get('emotional_language', []),
                'risk_level': service_data.get('level', service_data.get('risk_level', 'Low')),
                'level': service_data.get('level', service_data.get('risk_level', 'Low'))
            })
        
        elif service_name == 'content_analyzer':
            content_score = service_data.get('content_score', service_data.get('score', 50))
            extracted.update({
                'content_score': content_score,
                'score': content_score,
                'quality_score': service_data.get('quality_score', content_score),
                'readability_score': service_data.get('readability_score', 50),
                'quality_metrics': service_data.get('quality_metrics', {}),
                'level': service_data.get('level', 'Unknown')
            })
        
        elif service_name == 'openai_enhancer':
            enhancement_score = service_data.get('enhancement_score', service_data.get('score', 50))
            extracted.update({
                'ai_summary': service_data.get('enhanced_summary', service_data.get('ai_summary', '')),
                'key_insights': service_data.get('key_points', service_data.get('key_insights', [])),
                'credibility_assessment': service_data.get('credibility_assessment', ''),
                'enhancement_score': enhancement_score,
                'score': enhancement_score
            })
        
        # Ensure all services have required fields
        if 'score' not in extracted or extracted['score'] is None:
            extracted['score'] = 50
        if 'level' not in extracted or not extracted['level']:
            extracted['level'] = 'Unknown'
        
        return extracted
    
    def _calculate_trust_score(self, service_results: Dict[str, Any]) -> int:
        """Calculate trust score from service results"""
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
                service_data = service_results[service]
                score = service_data.get('score', 50)
                
                # Handle services where higher score = worse (invert them)
                if service in ['bias_detector', 'manipulation_detector']:
                    score = 100 - score
                
                scores.append((score, weight))
                logger.info(f"Trust component {service}: {score} (weight: {weight})")
        
        if not scores:
            return 30  # Low default when no services available
        
        # Calculate weighted average
        total_weight = sum(weight for _, weight in scores)
        weighted_sum = sum(score * weight for score, weight in scores)
        final_score = int(weighted_sum / total_weight)
        
        logger.info(f"Final trust score: {final_score} (from {len(scores)} services)")
        return max(0, min(100, final_score))
    
    def _get_trust_level(self, score: int) -> str:
        """Get trust level from score"""
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
