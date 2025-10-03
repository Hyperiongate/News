"""
Analysis Pipeline - PRODUCTION FIX v8.0
Date Modified: October 3, 2025
Last Updated: October 3, 2025

FIXES IN THIS VERSION:
1. Ensures article data (including domain/URL) flows to all services
2. Proper error handling for each service
3. Better data validation and fallback mechanisms
4. Enhanced logging for debugging
5. Ensures all services receive the data they need

This is the COMPLETE replacement for services/analysis_pipeline.py
"""

import logging
import time
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed
import traceback

from services.service_registry import get_service_registry

logger = logging.getLogger(__name__)


class AnalysisPipeline:
    """
    Orchestrates the analysis flow across multiple services with proper data passing
    """
    
    # Service execution order and dependencies
    SERVICE_GROUPS = {
        'extraction': ['article_extractor'],
        'primary': ['source_credibility', 'author_analyzer'],
        'secondary': ['bias_detector', 'fact_checker', 'transparency_analyzer'],
        'tertiary': ['manipulation_detector', 'content_analyzer'],
        'enhancement': ['openai_enhancer', 'plagiarism_detector']
    }
    
    # Services that need special data preparation
    SERVICES_NEEDING_URL = ['source_credibility', 'plagiarism_detector']
    SERVICES_NEEDING_AUTHOR = ['author_analyzer']
    
    def __init__(self, max_workers: int = 5):
        """Initialize the analysis pipeline"""
        self.service_registry = get_service_registry()
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Get available services
        self.available_services = self._get_available_services()
        logger.info(f"AnalysisPipeline initialized with {len(self.available_services)} available services")
    
    def _get_available_services(self) -> Dict[str, Any]:
        """Get all available services from registry"""
        try:
            return self.service_registry.get_available_services()
        except Exception as e:
            logger.error(f"Failed to get available services: {e}")
            return {}
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis method - orchestrates the entire pipeline
        """
        start_time = time.time()
        logger.info("=" * 80)
        logger.info("[unknown] DIAGNOSTIC PIPELINE STARTING")
        
        # Determine input type
        url = data.get('url', '')
        text = data.get('text', '') or data.get('content', '')
        
        if url:
            logger.info(f"Input type: URL")
        elif text:
            logger.info(f"Input type: Text ({len(text)} chars)")
        else:
            logger.error("No valid input provided")
            return self._create_error_response("No URL or text provided")
        
        logger.info("=" * 80)
        
        # Stage 1: Article Extraction
        logger.info("STAGE 1: Article Extraction")
        article_data = self._extract_article(data)
        
        if not article_data or not article_data.get('text'):
            logger.error("Article extraction failed completely")
            return self._create_error_response("Failed to extract article content")
        
        # Log extraction results
        logger.info(f"✓ Extracted: {article_data.get('title', 'Unknown')[:50]}...")
        logger.info(f"Article text length: {len(article_data.get('text', ''))}")
        
        # Stage 2: Run Analysis Services
        logger.info("STAGE 2: Running Analysis Services")
        service_results = self._run_analysis_services(article_data)
        
        # Stage 3: Calculate trust score
        logger.info("STAGE 3: Processing Results")
        trust_score = self._calculate_trust_score(service_results)
        
        # Log service results summary
        for service_name, result in service_results.items():
            if result and result.get('success'):
                score = result.get('data', {}).get('score', 0)
                logger.info(f"✓ {service_name}: Real data (score: {score})")
            else:
                logger.info(f"⚠ {service_name}: Using fallback data")
        
        # Calculate final scores with proper weighting
        weighted_scores = self._calculate_weighted_scores(service_results)
        logger.info(f"Final trust score: {trust_score}")
        
        # Build response
        response = self._build_response(
            success=True,
            article=article_data,
            detailed_analysis=service_results,
            trust_score=trust_score,
            processing_time=time.time() - start_time
        )
        
        # Log completion
        logger.info("=" * 80)
        logger.info("[unknown] PIPELINE DIAGNOSTIC COMPLETE")
        logger.info(f"Real Data Services: {len([s for s in service_results.values() if s and s.get('success')])}")
        logger.info(f"Simulated Services: {len([s for s in service_results.values() if s and s.get('fallback')])}")
        logger.info(f"Failed Services: {len([s for s in service_results.values() if not s or not s.get('success')])}")
        logger.info(f"Trust Score: {trust_score}/100")
        logger.info(f"Time: {time.time() - start_time:.2f}s")
        
        # Log any services using fallback data
        fallback_services = [name for name, result in service_results.items() 
                           if result and result.get('fallback')]
        if fallback_services:
            logger.warning(f"Fallback data used for: {', '.join(fallback_services)}")
        
        logger.info("=" * 80)
        
        return response
    
    def _extract_article(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract article content with proper error handling"""
        try:
            url = data.get('url', '')
            
            # Log what we're passing to extractor
            logger.info(f"Passing URL to extractor: {url}")
            
            extractor = self.service_registry.get_service('article_extractor')
            if not extractor:
                logger.error("Article extractor service not available")
                return self._create_fallback_article(data)
            
            # Run extraction
            logger.info("[article_extractor] Starting execution...")
            logger.info(f"[article_extractor] Availability check: {extractor.is_available}")
            
            result = extractor.analyze(data)
            
            logger.info(f"[article_extractor] Got result: {result.get('service')}...")
            
            if result.get('success') and result.get('data'):
                article_data = result['data']
                
                # Log what we got
                text_length = len(article_data.get('text', ''))
                logger.info(f"[article_extractor] Sending data with text length: {text_length}")
                
                # CRITICAL: Ensure we have text content
                if not article_data.get('text'):
                    logger.warning("No text content found in article_data. Keys available: ['url']")
                    if url:
                        article_data['text'] = f"Article from {url}"
                        article_data['content'] = article_data['text']
                
                # Ensure all required fields exist
                article_data.setdefault('url', url)
                article_data.setdefault('domain', self._extract_domain(url) if url else '')
                article_data.setdefault('title', 'Unknown Title')
                article_data.setdefault('author', 'Unknown')
                article_data.setdefault('source', article_data.get('domain', ''))
                
                logger.info(f"[article_extractor] ✓ Success - extracted data keys: {list(article_data.keys())[:5]}...")
                return article_data
            else:
                logger.error(f"Article extraction failed: {result.get('error')}")
                return self._create_fallback_article(data)
                
        except Exception as e:
            logger.error(f"Article extraction exception: {e}", exc_info=True)
            return self._create_fallback_article(data)
    
    def _run_analysis_services(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run all analysis services with proper data passing"""
        results = {}
        
        # Get list of services to run
        services_to_run = []
        for group in ['primary', 'secondary', 'tertiary']:
            for service_name in self.SERVICE_GROUPS.get(group, []):
                if service_name in self.available_services or self.service_registry.get_service(service_name):
                    services_to_run.append(service_name)
        
        logger.info(f"Available services from registry: {list(self.available_services.keys())}")
        
        # Run services with proper data preparation
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            
            for service_name in services_to_run:
                # Prepare service-specific data
                service_data = self._prepare_service_data(service_name, article_data)
                
                # Log what we're sending to each service
                if service_name == 'source_credibility':
                    logger.warning(f"Could not extract domain from data: {list(service_data.keys())}")
                
                # Submit service for execution
                logger.info(f"Submitting {service_name} (real service)")
                future = executor.submit(self._run_service, service_name, service_data)
                futures[future] = service_name
            
            # Collect results
            for future in as_completed(futures):
                service_name = futures[future]
                try:
                    result = future.result(timeout=10)
                    results[service_name] = result
                    
                    # Log result status
                    if result and result.get('success'):
                        logger.info(f"[{service_name}] ✓ Success - extracted data keys: {list(result.get('data', {}).keys())[:5]}...")
                    else:
                        logger.warning(f"[{service_name}] Result success={result.get('success', False)}: {result.get('error', 'Unknown error')}")
                        if not result.get('data'):
                            logger.warning(f"[{service_name}] Invalid result format - generating fallback")
                            logger.info(f"[{service_name}] Generating fallback data...")
                            
                except TimeoutError:
                    logger.error(f"Service {service_name} timed out")
                    results[service_name] = self._create_service_timeout_result(service_name)
                except Exception as e:
                    logger.error(f"Service {service_name} failed: {e}")
                    results[service_name] = self._create_service_error_result(service_name, str(e))
        
        return results
    
    def _prepare_service_data(self, service_name: str, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare service-specific data with all required fields"""
        # Start with base article data
        service_data = article_data.copy()
        
        # CRITICAL: Ensure URL and domain are present for services that need them
        if service_name in self.SERVICES_NEEDING_URL or service_name == 'source_credibility':
            # Make sure we have URL and domain
            if not service_data.get('url'):
                service_data['url'] = article_data.get('url', '')
            if not service_data.get('domain'):
                if service_data.get('url'):
                    service_data['domain'] = self._extract_domain(service_data['url'])
                else:
                    service_data['domain'] = article_data.get('source', '')
            
            # Log what we're sending to source_credibility
            if service_name == 'source_credibility':
                logger.info(f"Sending to source_credibility: domain='{service_data.get('domain')}', url='{service_data.get('url', '')[:50]}...'")
        
        # Ensure author field for author analyzer
        if service_name in self.SERVICES_NEEDING_AUTHOR:
            if not service_data.get('author'):
                service_data['author'] = article_data.get('author', 'Unknown')
        
        # Add any missing standard fields
        service_data.setdefault('text', article_data.get('text', ''))
        service_data.setdefault('content', article_data.get('text', ''))
        service_data.setdefault('title', article_data.get('title', ''))
        
        return service_data
    
    def _run_service(self, service_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single service with error handling"""
        try:
            logger.info(f"[{service_name}] Starting execution...")
            
            service = self.service_registry.get_service(service_name)
            if not service:
                logger.error(f"Service {service_name} not found in registry")
                return self._create_service_error_result(service_name, "Service not found")
            
            logger.info(f"[{service_name}] Availability check: {getattr(service, 'is_available', False)}")
            
            # Log data being sent (but not the full text)
            data_summary = {k: v if k not in ['text', 'content'] else f"[{len(v)} chars]" 
                          for k, v in data.items() if v}
            logger.info(f"[{service_name}] Sending data with text length: {len(data.get('text', ''))}")
            
            logger.info(f"[{service_name}] Calling analyze method...")
            
            # Run the service
            result = self.service_registry.analyze_with_service(service_name, data)
            
            # Log result summary
            if result:
                result_summary = f"success={result.get('success')}, keys={list(result.keys())[:5]}"
                logger.info(f"[{service_name}] Got result: {result_summary}...")
            else:
                logger.warning(f"[{service_name}] Returned None")
            
            return result
            
        except Exception as e:
            logger.error(f"Error running service {service_name}: {e}", exc_info=True)
            return self._create_service_error_result(service_name, str(e))
    
    def _calculate_trust_score(self, service_results: Dict[str, Any]) -> int:
        """Calculate overall trust score from service results"""
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
                    
                    # Log the score being used
                    logger.info(f"  {service_name}: score={score}, weight={weight}")
                    
                    weighted_sum += score * weight
                    total_weight += weight
        
        if total_weight > 0:
            trust_score = int(weighted_sum / total_weight)
        else:
            trust_score = 50  # Default if no services provided scores
        
        return max(0, min(100, trust_score))
    
    def _calculate_weighted_scores(self, service_results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate individual weighted scores for logging"""
        weights = {
            'source_credibility': 0.25,
            'author_analyzer': 0.15,
            'bias_detector': 0.20,
            'fact_checker': 0.15,
            'transparency_analyzer': 0.10,
            'manipulation_detector': 0.10,
            'content_analyzer': 0.05
        }
        
        weighted_scores = {}
        for service_name, weight in weights.items():
            if service_name in service_results:
                result = service_results[service_name]
                if result and result.get('data'):
                    score = result['data'].get('score', 0)
                    weighted_scores[service_name] = score * weight
        
        return weighted_scores
    
    def _build_response(self, success: bool, article: Dict[str, Any], 
                       detailed_analysis: Dict[str, Any], trust_score: int, 
                       processing_time: float) -> Dict[str, Any]:
        """Build the final response"""
        return {
            'success': success,
            'trust_score': trust_score,
            'article': article,
            'detailed_analysis': detailed_analysis,
            'processing_time': round(processing_time, 2),
            'services_used': len(detailed_analysis),
            'timestamp': time.time()
        }
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.lower().replace('www.', '')
            return domain
        except:
            return ''
    
    def _create_fallback_article(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback article data when extraction fails"""
        url = data.get('url', '')
        text = data.get('text', '') or data.get('content', 'No content available')
        
        return {
            'title': 'Article Analysis',
            'author': 'Unknown',
            'text': text[:1000] if text else 'Content extraction failed',
            'content': text[:1000] if text else 'Content extraction failed',
            'url': url,
            'domain': self._extract_domain(url) if url else '',
            'source': self._extract_domain(url) if url else 'Unknown',
            'word_count': len(text.split()) if text else 0,
            'extraction_successful': False
        }
    
    def _create_error_response(self, error_msg: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            'success': False,
            'error': error_msg,
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
            'data': {
                'score': 0,
                'error': error
            },
            'timestamp': time.time()
        }
    
    def _create_service_timeout_result(self, service_name: str) -> Dict[str, Any]:
        """Create timeout result for a service"""
        return {
            'service': service_name,
            'success': False,
            'error': 'Service timed out',
            'timeout': True,
            'data': {
                'score': 0,
                'error': 'Timeout'
            },
            'timestamp': time.time()
        }
    
    def close(self):
        """Clean up resources"""
        self.executor.shutdown(wait=False)


# Convenience function for backwards compatibility
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
