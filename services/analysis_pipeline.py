"""
Analysis Pipeline - PRODUCTION v10.0
Date Modified: October 3, 2025
Last Updated: October 3, 2025

FIXES IN THIS VERSION:
1. Detects when extraction fails and prompts user to paste content
2. Returns user-friendly error messages instead of proceeding with empty data
3. Properly validates article content before running analyses
4. Signals frontend to show text input when extraction is blocked
5. No more wasted API calls on empty content

This is the COMPLETE replacement for services/analysis_pipeline.py
"""

import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed
import traceback

from services.service_registry import get_service_registry

logger = logging.getLogger(__name__)


class AnalysisPipeline:
    """
    Orchestrates the analysis flow with proper extraction validation and user prompts
    """
    
    MIN_ARTICLE_LENGTH = 200  # Minimum characters for valid article analysis
    
    # Service execution order
    SERVICE_GROUPS = {
        'extraction': ['article_extractor'],
        'primary': ['source_credibility', 'author_analyzer'],
        'secondary': ['bias_detector', 'fact_checker', 'transparency_analyzer'],
        'tertiary': ['manipulation_detector', 'content_analyzer'],
        'enhancement': ['openai_enhancer', 'plagiarism_detector']
    }
    
    # Services that need special data
    SERVICES_NEEDING_URL = ['source_credibility', 'plagiarism_detector']
    SERVICES_NEEDING_AUTHOR = ['author_analyzer']
    
    def __init__(self, max_workers: int = 5):
        """Initialize the analysis pipeline"""
        self.service_registry = get_service_registry()
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        self.available_services = self._get_available_services()
        logger.info(f"AnalysisPipeline v10.0 initialized with {len(self.available_services)} services")
    
    def _get_available_services(self) -> Dict[str, Any]:
        """Get all available services from registry"""
        try:
            return self.service_registry.get_available_services()
        except Exception as e:
            logger.error(f"Failed to get available services: {e}")
            return {}
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis method with extraction validation and user prompting
        """
        start_time = time.time()
        logger.info("=" * 80)
        logger.info("[PIPELINE v10.0] STARTING ANALYSIS")
        
        # Determine input type
        url = data.get('url', '')
        text = data.get('text', '') or data.get('content', '')
        
        if url:
            logger.info(f"Input type: URL - {url}")
        elif text:
            logger.info(f"Input type: Text ({len(text)} chars)")
        else:
            logger.error("No valid input provided")
            return self._create_error_response(
                "No URL or text provided",
                user_message="Please provide a URL or paste article text to analyze."
            )
        
        logger.info("=" * 80)
        
        # STAGE 1: Article Extraction
        logger.info("STAGE 1: Article Extraction")
        extraction_result = self._extract_article(data)
        
        # Check if extraction failed and we should prompt user
        if extraction_result.get('prompt_for_text'):
            logger.warning("⚠ Extraction blocked - prompting user for text input")
            return {
                'success': False,
                'prompt_for_text': True,
                'user_message': extraction_result.get('user_message'),
                'domain': extraction_result.get('domain'),
                'url': extraction_result.get('url'),
                'error': extraction_result.get('error'),
                'trust_score': 0,
                'article': {},
                'detailed_analysis': {},
                'processing_time': round(time.time() - start_time, 2),
                'timestamp': time.time()
            }
        
        # Validate we have real content
        if not extraction_result or not extraction_result.get('text'):
            logger.error("❌ Extraction failed - no content")
            return self._create_error_response(
                "Failed to extract article content",
                user_message=(
                    "Unable to extract article content. The website may be blocking automated access.\n\n"
                    "Please copy and paste the article text to analyze it."
                )
            )
        
        text_content = extraction_result.get('text', '')
        if len(text_content) < self.MIN_ARTICLE_LENGTH:
            logger.error(f"❌ Insufficient content: {len(text_content)} chars (minimum {self.MIN_ARTICLE_LENGTH})")
            
            domain = extraction_result.get('domain', 'this website')
            return {
                'success': False,
                'prompt_for_text': True,
                'user_message': (
                    f"Unable to extract sufficient content from {domain}. "
                    "This website may be blocking automated access.\n\n"
                    "Please copy and paste the article text below to analyze it."
                ),
                'domain': extraction_result.get('domain'),
                'url': extraction_result.get('url'),
                'error': 'Insufficient content extracted',
                'trust_score': 0,
                'article': {},
                'detailed_analysis': {},
                'processing_time': round(time.time() - start_time, 2),
                'timestamp': time.time()
            }
        
        # Log successful extraction
        logger.info(f"✓ Extracted: {extraction_result.get('title', 'Unknown')[:50]}...")
        logger.info(f"✓ Text length: {len(text_content)} chars")
        logger.info(f"✓ Word count: {extraction_result.get('word_count', 0)}")
        logger.info(f"✓ Domain: {extraction_result.get('domain', 'Unknown')}")
        
        # STAGE 2: Run Analysis Services
        logger.info("STAGE 2: Running Analysis Services")
        service_results = self._run_analysis_services(extraction_result)
        
        # STAGE 3: Calculate Trust Score
        logger.info("STAGE 3: Calculating Trust Score")
        trust_score = self._calculate_trust_score(service_results)
        
        # Log results summary
        successful_services = [name for name, result in service_results.items() 
                              if result and result.get('success')]
        failed_services = [name for name, result in service_results.items() 
                          if not result or not result.get('success')]
        
        logger.info(f"✓ Successful services: {len(successful_services)}")
        logger.info(f"✗ Failed services: {len(failed_services)}")
        logger.info(f"✓ Final trust score: {trust_score}/100")
        
        # Build response
        response = {
            'success': True,
            'trust_score': trust_score,
            'article': extraction_result,
            'detailed_analysis': service_results,
            'processing_time': round(time.time() - start_time, 2),
            'services_used': len(successful_services),
            'timestamp': time.time()
        }
        
        logger.info("=" * 80)
        logger.info(f"[PIPELINE v10.0] ANALYSIS COMPLETE - Trust Score: {trust_score}/100")
        logger.info("=" * 80)
        
        return response
    
    def _extract_article(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract article with proper error handling"""
        try:
            url = data.get('url', '')
            
            extractor = self.service_registry.get_service('article_extractor')
            if not extractor:
                logger.error("❌ Article extractor service not available")
                return {
                    'prompt_for_text': True,
                    'user_message': 'Article extraction service unavailable. Please paste the article text.',
                    'error': 'Service unavailable'
                }
            
            logger.info("[article_extractor] Starting extraction...")
            
            result = extractor.analyze(data)
            
            # Check if extraction succeeded
            if not result.get('success'):
                logger.error(f"[article_extractor] ❌ Failed: {result.get('error', 'Unknown error')}")
                
                # Check if we should prompt user for text
                if result.get('prompt_for_text'):
                    return {
                        'prompt_for_text': True,
                        'user_message': result.get('user_message'),
                        'domain': result.get('data', {}).get('domain'),
                        'url': result.get('data', {}).get('url') or url,
                        'error': result.get('error')
                    }
                
                # Generic extraction failure
                return {
                    'prompt_for_text': True,
                    'user_message': (
                        'Unable to extract article content. Please copy and paste the article text below.'
                    ),
                    'error': result.get('error', 'Extraction failed')
                }
            
            # Extraction succeeded
            if not result.get('data'):
                logger.error("[article_extractor] ❌ No data in result")
                return {
                    'prompt_for_text': True,
                    'user_message': 'No content extracted. Please paste the article text.',
                    'error': 'No data returned'
                }
            
            article_data = result['data']
            
            # Validate text content
            text_length = len(article_data.get('text', ''))
            logger.info(f"[article_extractor] ✓ Extracted {text_length} chars")
            
            # Ensure required fields
            article_data.setdefault('url', url)
            article_data.setdefault('domain', self._extract_domain(url) if url else '')
            article_data.setdefault('title', 'Unknown Title')
            article_data.setdefault('author', 'Unknown')
            article_data.setdefault('source', article_data.get('domain', ''))
            
            return article_data
                
        except Exception as e:
            logger.error(f"[article_extractor] ❌ Exception: {e}", exc_info=True)
            return {
                'prompt_for_text': True,
                'user_message': 'Extraction error occurred. Please paste the article text.',
                'error': str(e)
            }
    
    def _run_analysis_services(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run all analysis services"""
        results = {}
        
        # Get services to run
        services_to_run = []
        for group in ['primary', 'secondary', 'tertiary']:
            for service_name in self.SERVICE_GROUPS.get(group, []):
                if service_name in self.available_services or self.service_registry.get_service(service_name):
                    services_to_run.append(service_name)
        
        logger.info(f"Running services: {services_to_run}")
        
        # Run services in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            
            for service_name in services_to_run:
                service_data = self._prepare_service_data(service_name, article_data)
                
                if service_name == 'source_credibility':
                    logger.info(f"→ source_credibility: domain='{service_data.get('domain')}', url='{service_data.get('url', '')[:50]}...'")
                
                future = executor.submit(self._run_service, service_name, service_data)
                futures[future] = service_name
            
            # Collect results
            for future in as_completed(futures):
                service_name = futures[future]
                try:
                    result = future.result(timeout=10)
                    results[service_name] = result
                    
                    if result and result.get('success'):
                        score = result.get('data', {}).get('score', 0)
                        logger.info(f"✓ {service_name}: score={score}")
                    else:
                        error = result.get('error', 'Unknown') if result else 'No result'
                        logger.warning(f"✗ {service_name}: {error}")
                            
                except TimeoutError:
                    logger.error(f"✗ {service_name}: Timeout")
                    results[service_name] = self._create_service_timeout_result(service_name)
                except Exception as e:
                    logger.error(f"✗ {service_name}: {e}")
                    results[service_name] = self._create_service_error_result(service_name, str(e))
        
        return results
    
    def _prepare_service_data(self, service_name: str, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare service-specific data"""
        service_data = article_data.copy()
        
        # Ensure URL and domain for services that need them
        if service_name in self.SERVICES_NEEDING_URL or service_name == 'source_credibility':
            if not service_data.get('url'):
                service_data['url'] = article_data.get('url', '')
            if not service_data.get('domain'):
                service_data['domain'] = self._extract_domain(service_data.get('url', '')) or article_data.get('source', '')
        
        # Ensure author for author analyzer
        if service_name in self.SERVICES_NEEDING_AUTHOR:
            if not service_data.get('author'):
                service_data['author'] = article_data.get('author', 'Unknown')
        
        # Standard fields
        service_data.setdefault('text', article_data.get('text', ''))
        service_data.setdefault('content', article_data.get('text', ''))
        service_data.setdefault('title', article_data.get('title', ''))
        
        return service_data
    
    def _run_service(self, service_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single service"""
        try:
            logger.info(f"[{service_name}] Starting...")
            
            service = self.service_registry.get_service(service_name)
            if not service:
                logger.error(f"[{service_name}] Not found in registry")
                return self._create_service_error_result(service_name, "Service not found")
            
            result = self.service_registry.analyze_with_service(service_name, data)
            
            if result:
                logger.info(f"[{service_name}] Result: success={result.get('success')}")
            else:
                logger.warning(f"[{service_name}] Returned None")
            
            return result
            
        except Exception as e:
            logger.error(f"[{service_name}] Error: {e}")
            return self._create_service_error_result(service_name, str(e))
    
    def _calculate_trust_score(self, service_results: Dict[str, Any]) -> int:
        """Calculate overall trust score"""
        weights = {
            'source_credibility': 0.25,
            'author_analyzer': 0.15,
            'bias_detector': 0.20,
            'fact_checker': 0.15,
            'transparency_analyzer': 0.10,
            'manipulation_detector': 0.10,
            'content_analyzer': 0.05
        }
        
        weighted_sum = 0
        total_weight = 0
        
        for service_name, weight in weights.items():
            if service_name in service_results:
                result = service_results[service_name]
                if result and result.get('data'):
                    score = result['data'].get('score', 50)
                    weighted_sum += score * weight
                    total_weight += weight
        
        if total_weight > 0:
            trust_score = int(weighted_sum / total_weight)
        else:
            trust_score = 50
        
        return max(0, min(100, trust_score))
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.lower().replace('www.', '')
        except:
            return ''
    
    def _create_error_response(self, error_msg: str, user_message: str = None) -> Dict[str, Any]:
        """Create error response"""
        return {
            'success': False,
            'error': error_msg,
            'user_message': user_message or error_msg,
            'trust_score': 0,
            'article': {},
            'detailed_analysis': {},
            'processing_time': 0,
            'timestamp': time.time()
        }
    
    def _create_service_error_result(self, service_name: str, error: str) -> Dict[str, Any]:
        """Create error result for a service"""
        return {
            'service': service_name,
            'success': False,
            'error': error,
            'data': {'score': 0, 'error': error},
            'timestamp': time.time()
        }
    
    def _create_service_timeout_result(self, service_name: str) -> Dict[str, Any]:
        """Create timeout result"""
        return {
            'service': service_name,
            'success': False,
            'error': 'Service timed out',
            'timeout': True,
            'data': {'score': 0, 'error': 'Timeout'},
            'timestamp': time.time()
        }
    
    def close(self):
        """Clean up resources"""
        self.executor.shutdown(wait=False)


def analyze_article(url: str = None, text: str = None) -> Dict[str, Any]:
    """Convenience function to analyze an article"""
    pipeline = AnalysisPipeline()
    try:
        data = {}
        if url:
            data['url'] = url
        if text:
            data['text'] = text
        
        if not data:
            return {'success': False, 'error': 'No URL or text provided'}
        
        return pipeline.analyze(data)
    finally:
        pipeline.close()
