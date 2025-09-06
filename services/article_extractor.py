"""
Analysis Pipeline - FIXED WITH AUTHOR ANALYZER
Date: September 6, 2025
Last Updated: September 6, 2025

CRITICAL FIXES:
1. Author analyzer is now properly included in core services
2. Fixed service data extraction to handle all return formats
3. Proper timeout handling for each service
4. Better error recovery and logging

Notes:
- Author analyzer runs in parallel with other core services
- Each service has individual timeout protection
- Proper data extraction from BaseAnalyzer wrapper format
"""
import time
import logging
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed
import traceback

from services.service_registry import get_service_registry

logger = logging.getLogger(__name__)


class AnalysisPipeline:
    """
    FIXED: Pipeline with proper author analyzer integration
    """
    
    def __init__(self):
        self.registry = get_service_registry()
        self.executor = ThreadPoolExecutor(max_workers=8)
        logger.info("AnalysisPipeline initialized with author analyzer support")
        
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis method with author analyzer included
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
            'detailed_analysis': {},
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
            
            # Extract article data
            article_data = self._extract_article_data_fixed(article_result)
            results['article'] = article_data
            logger.info(f"✓ Article extracted: '{article_data.get('title', 'No title')[:50]}...'")
            logger.info(f"✓ Author found: {article_data.get('author', 'Unknown')}")
            logger.info(f"✓ Domain: {article_data.get('domain', 'Unknown')}")
            
            # Create enriched data for other services
            enriched_data = {**data}
            enriched_data.update(article_data)
            enriched_data['article'] = article_data
            
            # Stage 2: Core Analysis Services (parallel) - INCLUDING AUTHOR ANALYZER
            logger.info("STAGE 2: Core Analysis Services")
            core_services = [
                'source_credibility', 
                'author_analyzer',  # FIXED: Author analyzer is now included
                'bias_detector', 
                'transparency_analyzer', 
                'manipulation_detector', 
                'content_analyzer'
            ]
            
            # Log which services are available
            available_core = [s for s in core_services if self.registry.is_service_available(s)]
            logger.info(f"Available core services: {available_core}")
            
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
            
            # Process service results into detailed_analysis
            detailed_analysis = {}
            for service_name, service_result in all_services.items():
                logger.info(f"\n=== PROCESSING {service_name.upper()} ===")
                
                if not service_result:
                    logger.warning(f"✗ {service_name}: No result")
                    continue
                
                # Extract the actual analysis data
                service_data = self._extract_service_data_fixed(service_name, service_result)
                
                if service_data:
                    detailed_analysis[service_name] = service_data
                    score = service_data.get('score', service_data.get(f'{service_name}_score', 0))
                    logger.info(f"✓ {service_name}: Processed successfully (score: {score})")
                else:
                    logger.warning(f"✗ {service_name}: Failed to extract data")
            
            # Check if author_analyzer is in the results
            if 'author_analyzer' not in detailed_analysis:
                logger.warning("Author analyzer NOT in detailed_analysis!")
            else:
                logger.info("✓ Author analyzer successfully included in detailed_analysis")
            
            # Calculate trust score
            trust_score = self._calculate_trust_score(detailed_analysis)
            
            # Determine trust level
            if trust_score >= 80:
                trust_level = 'Very High'
            elif trust_score >= 60:
                trust_level = 'High'  
            elif trust_score >= 40:
                trust_level = 'Medium'
            elif trust_score >= 20:
                trust_level = 'Low'
            else:
                trust_level = 'Very Low'
            
            # Update results
            results.update({
                'success': True,
                'article': article_data,
                'trust_score': trust_score,
                'trust_level': trust_level,
                'summary': f"Analysis complete - Trust Score: {trust_score}/100",
                'detailed_analysis': detailed_analysis,
                'services_available': len(detailed_analysis)
            })
            
            processing_time = time.time() - start_time
            logger.info("=" * 80)
            logger.info("FIXED PIPELINE COMPLETE")
            logger.info(f"Time: {processing_time:.2f}s | Services: {len(detailed_analysis)} | Trust: {trust_score}")
            logger.info(f"Final article title: {article_data.get('title', 'Unknown')}")
            logger.info(f"Final article author: {article_data.get('author', 'Unknown')}")
            logger.info("=" * 80)
            
            return results
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}", exc_info=True)
            results['success'] = False
            results['error'] = str(e)
            return results
    
    def _extract_article(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract article with article_extractor service"""
        try:
            if not self.registry.is_service_available('article_extractor'):
                logger.error("article_extractor service not available")
                return None
            
            result = self.registry.analyze_with_service('article_extractor', data)
            return result
        except Exception as e:
            logger.error(f"Article extraction error: {e}")
            return None
    
    def _extract_article_data_fixed(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        FIXED: Extract article data from various result formats
        """
        logger.info("=== EXTRACTING ARTICLE DATA ===")
        
        # Initialize with defaults
        article_data = {
            'title': 'Unknown',
            'author': 'Unknown',
            'content': '',
            'text': '',
            'url': '',
            'domain': 'unknown',
            'source': 'unknown',
            'word_count': 0,
            'publish_date': None
        }
        
        # Handle different result structures
        if 'data' in result:
            # BaseAnalyzer format: {success: true, data: {...}}
            data = result['data']
            logger.info(f"Using BaseAnalyzer format with keys: {list(data.keys())[:10]}")
        elif 'analysis_complete' in result:
            # Direct format with analysis_complete flag
            data = result
            logger.info(f"Using top-level data with keys: {list(data.keys())[:10]}")
        else:
            # Unknown format - try to use as-is
            data = result
            logger.info(f"Using unknown format with keys: {list(result.keys())[:10]}")
        
        # Extract fields (with multiple possible key names)
        article_data['title'] = data.get('title', data.get('headline', 'Unknown'))
        article_data['author'] = data.get('author', data.get('authors', 'Unknown'))
        article_data['content'] = data.get('content', data.get('text', ''))
        article_data['text'] = data.get('text', data.get('content', ''))
        article_data['url'] = data.get('url', data.get('link', ''))
        article_data['domain'] = data.get('domain', data.get('source', 'unknown'))
        article_data['source'] = data.get('source', data.get('domain', 'unknown'))
        article_data['word_count'] = data.get('word_count', len(article_data['content'].split()))
        article_data['publish_date'] = data.get('publish_date', data.get('date', None))
        
        # Clean domain
        article_data['domain'] = self._clean_domain(article_data['domain'])
        article_data['source'] = article_data['domain']  # Keep them in sync
        
        # Log what we extracted
        logger.info(f"✓ Extracted title: {article_data['title'][:50]}...")
        logger.info(f"✓ Extracted author: {article_data['author']}")
        logger.info(f"✓ Extracted domain: {article_data['domain']}")
        logger.info(f"✓ Word count: {article_data['word_count']}")
        
        return article_data
    
    def _clean_domain(self, domain: str) -> str:
        """Clean domain name"""
        if not domain:
            return 'unknown'
            
        # Remove www. prefix
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
        
        # Submit tasks for available services
        for service_name in services:
            if self.registry.is_service_available(service_name):
                logger.info(f"Submitting {service_name} to executor")
                future = self.executor.submit(self._run_single_service, service_name, data)
                futures[future] = service_name
            else:
                logger.warning(f"{service_name} is not available")
        
        # Collect results with individual timeouts
        for future in as_completed(futures, timeout=90):  # Overall timeout
            service_name = futures[future]
            try:
                result = future.result(timeout=30)  # Individual service timeout
                results[service_name] = result
                logger.info(f"✓ {service_name} completed")
            except TimeoutError:
                logger.warning(f"✗ {service_name} timed out")
                results[service_name] = {
                    'success': False,
                    'error': 'Service timeout',
                    'service': service_name
                }
            except Exception as e:
                logger.error(f"✗ {service_name} failed: {e}")
                results[service_name] = {
                    'success': False,
                    'error': str(e),
                    'service': service_name
                }
        
        return results
    
    def _run_single_service(self, service_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single service with error handling"""
        try:
            logger.info(f"Running {service_name}...")
            result = self.registry.analyze_with_service(service_name, data)
            if result:
                logger.info(f"{service_name} returned result")
            else:
                logger.warning(f"{service_name} returned None")
            return result
        except Exception as e:
            logger.error(f"Error in {service_name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'service': service_name
            }
    
    def _extract_service_data_fixed(self, service_name: str, service_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        FIXED: Extract the actual analysis data from service result
        """
        if not service_result:
            return None
        
        # Handle error results
        if not service_result.get('success', False):
            return None
        
        # Extract data based on service response format
        if 'data' in service_result:
            # BaseAnalyzer format
            return service_result['data']
        elif 'analysis' in service_result:
            # Some services use 'analysis' key
            return service_result['analysis']
        elif service_name in service_result:
            # Service name as key
            return service_result[service_name]
        else:
            # Return the whole result (minus metadata)
            data = {k: v for k, v in service_result.items() 
                   if k not in ['success', 'service', 'timestamp', 'available']}
            return data if data else None
    
    def _calculate_trust_score(self, detailed_analysis: Dict[str, Any]) -> int:
        """Calculate weighted trust score from all services"""
        weights = {
            'source_credibility': 0.25,
            'bias_detector': 0.20,
            'fact_checker': 0.15,
            'transparency_analyzer': 0.10,
            'manipulation_detector': 0.10,
            'author_analyzer': 0.15,  # Added weight for author analyzer
            'content_analyzer': 0.05
        }
        
        total_weight = 0
        weighted_sum = 0
        
        for service, weight in weights.items():
            if service in detailed_analysis:
                service_data = detailed_analysis[service]
                
                # Extract score (different services use different keys)
                score = None
                if isinstance(service_data, dict):
                    score = (service_data.get('score') or 
                            service_data.get(f'{service}_score') or
                            service_data.get('credibility_score') or
                            service_data.get('trust_score') or
                            service_data.get('overall_score') or
                            service_data.get('combined_credibility_score'))  # For author_analyzer
                    
                    # Special handling for bias (inverse score)
                    if service == 'bias_detector' and 'bias_score' in service_data:
                        score = 100 - service_data['bias_score']
                    
                    # Special handling for manipulation (inverse score)
                    if service == 'manipulation_detector' and 'manipulation_score' in service_data:
                        score = 100 - service_data['manipulation_score']
                
                if score is not None:
                    logger.info(f"Trust component {service}: {score} (weight: {weight})")
                    weighted_sum += score * weight
                    total_weight += weight
        
        # Calculate final score
        if total_weight > 0:
            trust_score = int(weighted_sum / total_weight)
        else:
            trust_score = 50  # Default if no services available
        
        logger.info(f"Final trust score: {trust_score} (from {len(detailed_analysis)} services)")
        return trust_score
