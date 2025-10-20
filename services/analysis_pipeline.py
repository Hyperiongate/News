"""
Analysis Pipeline - v12.6 TRUST SCORE FIXED TO 100%
Date: October 20, 2025
Version: 12.6 - CRITICAL FIX: Trust score weights now total 100%

CHANGES FROM 12.5:
✅ FIXED: Trust score weights rebalanced from 90% to 100%
  - Source Credibility: 25% → 30% (+5%)
  - Author Analyzer: 15% (unchanged)
  - Bias Detector: 20% (unchanged)
  - Fact Checker: 15% (unchanged)
  - Transparency: 10% (unchanged)
  - Manipulation: 10% (was missing!)
  - Content: 0% (informational only, removed from scoring)
✅ PRESERVED: All v12.5 optimizations (7 parallel workers)
✅ PRESERVED: All logging and error handling
✅ PRESERVED: Exact same response format

This is the COMPLETE file ready to deploy.
Save as: services/analysis_pipeline.py (REPLACE existing file)
"""

import logging
import time
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback

logger = logging.getLogger(__name__)


class AnalysisPipeline:
    """
    Analysis Pipeline v12.6 - TRUST SCORE FIXED TO 100%
    """
    
    # FIXED v12.6: Weights now total 100% (was 90%)
    SERVICE_WEIGHTS = {
        'source_credibility': 0.30,      # Was 0.25, increased by 5%
        'author_analyzer': 0.15,         # Unchanged
        'bias_detector': 0.20,           # Unchanged
        'fact_checker': 0.15,            # Unchanged
        'transparency_analyzer': 0.10,   # Unchanged
        'manipulation_detector': 0.10,   # Was missing! Now included
        'content_analyzer': 0.00         # Was 0.05, now informational only
    }
    
    def __init__(self):
        """Initialize pipeline with available services"""
        # PRESERVED v12.5: 7 workers for true parallel execution
        self.executor = ThreadPoolExecutor(max_workers=7)
        
        # Import services directly
        self.services = {}
        self._load_services()
        
        # Verify weights total 100%
        total = sum(self.SERVICE_WEIGHTS.values())
        logger.info(f"[Pipeline v12.6] Trust score weights: {total*100:.1f}%")
        
        if abs(total - 1.0) > 0.001:
            logger.error(f"[Pipeline v12.6] ERROR: Weights total {total*100:.1f}%, not 100%!")
        else:
            logger.info("[Pipeline v12.6] ✓ Trust score properly balanced at 100%")
        
        logger.info(f"[Pipeline v12.6] Initialized with {len(self.services)} services")
        logger.info(f"[Pipeline v12.6] 7 parallel workers (all services run simultaneously)")
    
    def _load_services(self):
        """Load available services"""
        
        # Article Extractor (critical)
        try:
            from services.article_extractor import ArticleExtractor
            self.services['article_extractor'] = ArticleExtractor()
            logger.info("✓ ArticleExtractor loaded")
        except Exception as e:
            logger.error(f"✗ ArticleExtractor failed: {e}")
        
        # Source Credibility
        try:
            from services.source_credibility import SourceCredibility
            self.services['source_credibility'] = SourceCredibility()
            logger.info("✓ SourceCredibility loaded")
        except Exception as e:
            logger.warning(f"SourceCredibility unavailable: {e}")
        
        # Author Analyzer
        try:
            from services.author_analyzer import AuthorAnalyzer
            self.services['author_analyzer'] = AuthorAnalyzer()
            logger.info("✓ AuthorAnalyzer loaded")
        except Exception as e:
            logger.warning(f"AuthorAnalyzer unavailable: {e}")
        
        # Bias Detector
        try:
            from services.bias_detector import BiasDetector
            self.services['bias_detector'] = BiasDetector()
            logger.info("✓ BiasDetector loaded")
        except Exception as e:
            logger.warning(f"BiasDetector unavailable: {e}")
        
        # Fact Checker
        try:
            from services.fact_checker import FactChecker
            self.services['fact_checker'] = FactChecker()
            logger.info("✓ FactChecker loaded")
        except Exception as e:
            logger.warning(f"FactChecker unavailable: {e}")
        
        # Transparency Analyzer
        try:
            from services.transparency_analyzer import TransparencyAnalyzer
            self.services['transparency_analyzer'] = TransparencyAnalyzer()
            logger.info("✓ TransparencyAnalyzer loaded")
        except Exception as e:
            logger.warning(f"TransparencyAnalyzer unavailable: {e}")
        
        # Manipulation Detector
        try:
            from services.manipulation_detector import ManipulationDetector
            self.services['manipulation_detector'] = ManipulationDetector()
            logger.info("✓ ManipulationDetector loaded")
        except Exception as e:
            logger.warning(f"ManipulationDetector unavailable: {e}")
        
        # Content Analyzer
        try:
            from services.content_analyzer import ContentAnalyzer
            self.services['content_analyzer'] = ContentAnalyzer()
            logger.info("✓ ContentAnalyzer loaded")
        except Exception as e:
            logger.warning(f"ContentAnalyzer unavailable: {e}")
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis method
        v12.6 - TRUST SCORE FIXED + v12.5 optimizations preserved
        """
        start_time = time.time()
        
        logger.info("=" * 80)
        logger.info("[PIPELINE v12.6] STARTING ANALYSIS")
        logger.info("[PIPELINE v12.6] Trust score weights: 100% (FIXED)")
        
        # Determine input type
        url = data.get('url', '')
        text = data.get('text', '') or data.get('content', '')
        
        if url:
            logger.info(f"Input: URL - {url}")
        elif text:
            logger.info(f"Input: Text ({len(text)} chars)")
        else:
            logger.error("No input provided")
            return self._error_response("No URL or text provided")
        
        # STAGE 1: Extract Article
        logger.info("STAGE 1: Article Extraction")
        
        if 'article_extractor' not in self.services:
            logger.error("Article extractor not available")
            return self._error_response("Article extraction service not available")
        
        try:
            extractor = self.services['article_extractor']
            extraction_result = extractor.analyze(data)
            
            if not extraction_result.get('success'):
                logger.error(f"Extraction failed: {extraction_result.get('error')}")
                return {
                    'success': False,
                    'error': extraction_result.get('error', 'Extraction failed'),
                    'trust_score': 0,
                    'article': {},
                    'detailed_analysis': {}
                }
            
            # Get article data from extraction result
            article_data = extraction_result.get('data', {})
            
            if not article_data.get('text'):
                logger.error("No text extracted")
                return self._error_response("No content could be extracted")
            
            # VERIFY AND LOG ARTICLE DATA (PRESERVED)
            logger.info("=" * 80)
            logger.info("[PIPELINE v12.6] VERIFYING ARTICLE DATA FOR SERVICES")
            logger.info(f"[PIPELINE] Extracted author: '{article_data.get('author', 'NOT FOUND')}'")
            logger.info(f"[PIPELINE] Extracted domain: '{article_data.get('domain', 'NOT FOUND')}'")
            logger.info(f"[PIPELINE] Extracted source: '{article_data.get('source', 'NOT FOUND')}'")
            
            # Log author page URL if available (PRESERVED)
            author_page_url = article_data.get('author_page_url')
            if author_page_url:
                logger.info(f"[PIPELINE v12.6] ✓ Author page URL extracted: {author_page_url}")
            else:
                logger.info(f"[PIPELINE v12.6] ⚠ No author page URL found")
            
            # Ensure critical fields are present with defaults (PRESERVED)
            if 'author' not in article_data or not article_data['author']:
                article_data['author'] = 'Unknown'
                logger.warning("[PIPELINE] Author field was missing or empty, set to 'Unknown'")
            
            if 'domain' not in article_data or not article_data['domain']:
                article_data['domain'] = article_data.get('source', '').lower().replace(' ', '')
                logger.warning(f"[PIPELINE] Domain field was missing, inferred: '{article_data['domain']}'")
            
            if 'source' not in article_data or not article_data['source']:
                article_data['source'] = article_data.get('domain', 'Unknown')
                logger.warning(f"[PIPELINE] Source field was missing, using domain: '{article_data['source']}'")
            
            # Also add URL if present
            if url and 'url' not in article_data:
                article_data['url'] = url
            
            logger.info("[PIPELINE v12.6] Article data prepared for services:")
            logger.info(f"  - author: {article_data.get('author')}")
            logger.info(f"  - author_page_url: {article_data.get('author_page_url', 'None')}")
            logger.info(f"  - domain: {article_data.get('domain')}")
            logger.info(f"  - source: {article_data.get('source')}")
            logger.info(f"  - title: {article_data.get('title', '')[:50]}...")
            logger.info(f"  - word_count: {article_data.get('word_count', 0)}")
            logger.info("=" * 80)
            
            logger.info(f"✓ Extracted: {article_data.get('word_count', 0)} words")
            logger.info(f"✓ Title: {article_data.get('title', 'Unknown')[:50]}...")
            logger.info(f"✓ Source: {article_data.get('source', 'Unknown')}")
            logger.info(f"✓ Author: {article_data.get('author', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Extraction exception: {e}")
            return self._error_response(f"Extraction failed: {str(e)}")
        
        # STAGE 2: Run Analysis Services (OPTIMIZED v12.5, PRESERVED v12.6)
        logger.info("STAGE 2: Running Analysis Services")
        logger.info("[Pipeline v12.6] All 7 services will run simultaneously...")
        
        service_results = {}
        futures = {}
        
        # PRESERVED v12.5: 7 workers for true parallel execution
        with ThreadPoolExecutor(max_workers=7) as executor:
            services_to_run = [
                'source_credibility', 'author_analyzer', 'bias_detector', 
                'fact_checker', 'transparency_analyzer', 
                'manipulation_detector', 'content_analyzer'
            ]
            
            for service_name in services_to_run:
                if service_name in self.services:
                    service = self.services[service_name]
                    
                    # PRESERVED: Log what we're passing to author_analyzer
                    if service_name == 'author_analyzer':
                        logger.info("=" * 80)
                        logger.info("[PIPELINE v12.6] PASSING TO AUTHOR_ANALYZER:")
                        logger.info(f"  - author: '{article_data.get('author')}'")
                        logger.info(f"  - author_page_url: '{article_data.get('author_page_url', 'None')}'")
                        logger.info(f"  - domain: '{article_data.get('domain')}'")
                        logger.info(f"  - source: '{article_data.get('source')}'")
                        logger.info(f"  - text length: {len(article_data.get('text', ''))}")
                        logger.info("=" * 80)
                    
                    future = executor.submit(self._run_service, service_name, service, article_data)
                    futures[future] = service_name
            
            # Collect results with PRESERVED v12.5 timeouts
            for future in as_completed(futures):
                service_name = futures[future]
                
                # PRESERVED v12.5: Optimized timeouts
                timeout = 20  # Default 20s
                
                if service_name == 'author_analyzer':
                    timeout = 30  # 30s for author (scraping takes time)
                elif service_name == 'fact_checker':
                    timeout = 25  # 25s for fact checker
                
                try:
                    logger.info(f"[PIPELINE v12.6] Waiting for {service_name} (timeout: {timeout}s)...")
                    result = future.result(timeout=timeout)
                    if result:
                        service_results[service_name] = result
                        logger.info(f"✓ {service_name}: completed")
                    else:
                        logger.warning(f"✗ {service_name}: returned empty result")
                        service_results[service_name] = self._get_default_service_data(service_name)
                except TimeoutError as e:
                    logger.error(f"✗ {service_name}: TIMEOUT after {timeout}s")
                    service_results[service_name] = self._get_default_service_data(service_name)
                except Exception as e:
                    logger.error(f"✗ {service_name}: ERROR: {e}")
                    logger.error(f"✗ {service_name}: Traceback: {traceback.format_exc()}")
                    service_results[service_name] = self._get_default_service_data(service_name)
        
        # STAGE 3: Calculate Trust Score (FIXED v12.6)
        logger.info("STAGE 3: Calculating Trust Score (FIXED - 100% weights)")
        trust_score = self._calculate_trust_score(service_results)
        
        logger.info(f"✓ Trust Score: {trust_score}/100")
        logger.info(f"✓ Services completed: {len(service_results)}")
        
        # Build response (PRESERVED - exact same format)
        response = {
            'success': True,
            'trust_score': trust_score,
            'article': article_data,
            'detailed_analysis': service_results,
            'processing_time': round(time.time() - start_time, 2),
            'services_used': len(service_results)
        }
        
        logger.info("=" * 80)
        logger.info(f"[PIPELINE v12.6] ANALYSIS COMPLETE - {response['processing_time']}s")
        logger.info(f"[PIPELINE v12.6] Trust score calculated with 100% weight distribution")
        logger.info("=" * 80)
        
        return response
    
    def _run_service(self, service_name: str, service: Any, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single service and return flattened data (PRESERVED from v12.5)"""
        try:
            # PRESERVED: Verify data before calling service
            if service_name == 'author_analyzer':
                logger.info("[PIPELINE v12.6] _run_service called for author_analyzer")
                logger.info(f"[PIPELINE] Data keys available: {list(data.keys())}")
                logger.info(f"[PIPELINE] Author value: '{data.get('author', 'MISSING')}'")
                logger.info(f"[PIPELINE] Author page URL: '{data.get('author_page_url', 'MISSING')}'")
            
            # Call service
            result = service.analyze(data)
            
            # PRESERVED: DEBUG LOGGING FOR AUTHOR ANALYZER
            if service_name == 'author_analyzer':
                logger.info("=" * 60)
                logger.info("[DEBUG AUTHOR] Raw result from author_analyzer:")
                if isinstance(result, dict):
                    logger.info(f"[DEBUG AUTHOR] Top-level keys: {list(result.keys())}")
                    if 'data' in result:
                        data_keys = list(result['data'].keys())
                        logger.info(f"[DEBUG AUTHOR] Data keys ({len(data_keys)}): {data_keys[:15]}")
                        logger.info(f"[DEBUG AUTHOR] name: {result['data'].get('name', 'MISSING')}")
                        logger.info(f"[DEBUG AUTHOR] articles_found: {result['data'].get('articles_found', 'MISSING')}")
                logger.info("=" * 60)
            
            # PRESERVED: Extract and flatten data
            if isinstance(result, dict):
                # If result has 'data' field, extract it
                if 'data' in result:
                    service_data = result['data']
                else:
                    service_data = result
                
                # PRESERVED: DEBUG for author
                if service_name == 'author_analyzer':
                    logger.info(f"[DEBUG AUTHOR] Returning to pipeline with keys: {list(service_data.keys())[:15]}")
                    logger.info(f"[DEBUG AUTHOR] Final name: {service_data.get('name', 'MISSING')}")
                    logger.info(f"[DEBUG AUTHOR] Final articles_found: {service_data.get('articles_found', 'MISSING')}")
                
                # PRESERVED: Ensure required fields
                if 'score' not in service_data:
                    service_data['score'] = 50
                
                # PRESERVED: Add analysis section if missing
                if 'analysis' not in service_data:
                    service_data['analysis'] = {
                        'what_we_looked': f'Analyzed {service_name.replace("_", " ")}',
                        'what_we_found': f'Analysis completed',
                        'what_it_means': f'Results processed'
                    }
                
                return service_data
            
            return self._get_default_service_data(service_name)
            
        except Exception as e:
            logger.error(f"Service {service_name} failed: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return self._get_default_service_data(service_name)
    
    def _get_default_service_data(self, service_name: str) -> Dict[str, Any]:
        """Get default data for a failed service (PRESERVED)"""
        return {
            'score': 50,
            'analysis': {
                'what_we_looked': f'Attempted {service_name.replace("_", " ")} analysis',
                'what_we_found': 'Service temporarily unavailable',
                'what_it_means': 'Partial analysis completed'
            }
        }
    
    def _calculate_trust_score(self, service_results: Dict[str, Any]) -> int:
        """
        Calculate weighted trust score
        FIXED v12.6: Now uses 100% weight distribution
        """
        weighted_sum = 0
        total_weight = 0
        
        logger.info("[TrustScore v12.6] Calculating with 100% weight distribution:")
        
        for service_name, weight in self.SERVICE_WEIGHTS.items():
            if weight == 0:  # Skip services with 0 weight (content_analyzer)
                continue
                
            if service_name in service_results:
                service_data = service_results[service_name]
                score = service_data.get('score', 50)
                weighted_contribution = score * weight
                weighted_sum += weighted_contribution
                total_weight += weight
                
                logger.info(f"  {service_name}: {score} × {weight*100:.0f}% = {weighted_contribution:.1f}")
        
        logger.info(f"  Total weight used: {total_weight*100:.1f}%")
        logger.info(f"  Weighted sum: {weighted_sum:.1f}")
        
        if total_weight > 0:
            final_score = int(weighted_sum / total_weight)
            logger.info(f"  Final score: {final_score}/100")
            return final_score
        
        logger.warning("[TrustScore v12.6] No valid scores - returning default 50")
        return 50
    
    def _error_response(self, error_msg: str) -> Dict[str, Any]:
        """Create error response (PRESERVED)"""
        return {
            'success': False,
            'error': error_msg,
            'trust_score': 0,
            'article': {},
            'detailed_analysis': {}
        }


logger.info("[AnalysisPipeline] v12.6 loaded - TRUST SCORE FIXED TO 100%")

# This file is not truncated
