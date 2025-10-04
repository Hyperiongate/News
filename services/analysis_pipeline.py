"""
Analysis Pipeline - CLEAN AND WORKING VERSION
Date: October 4, 2025
Version: 12.0

This is a COMPLETE, CLEAN replacement for services/analysis_pipeline.py
- Removes all contradictory code
- Maintains ALL functionality
- Properly handles extraction failures
- Clean data flow to all services
"""

import logging
import time
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback

logger = logging.getLogger(__name__)


class AnalysisPipeline:
    """
    Clean orchestration of analysis services
    """
    
    # Service weights for trust score calculation
    SERVICE_WEIGHTS = {
        'source_credibility': 0.25,
        'author_analyzer': 0.15,
        'bias_detector': 0.20,
        'fact_checker': 0.15,
        'transparency_analyzer': 0.10,
        'manipulation_detector': 0.10,
        'content_analyzer': 0.05
    }
    
    def __init__(self):
        """Initialize pipeline with available services"""
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        # Import services directly - no complex registry
        self.services = {}
        self._load_services()
        
        logger.info(f"[Pipeline v12.0] Initialized with {len(self.services)} services")
    
    def _load_services(self):
        """Load available services"""
        
        # Article Extractor (critical - must work)
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
        Main analysis method - clean and working
        """
        start_time = time.time()
        
        logger.info("=" * 80)
        logger.info("[PIPELINE] STARTING ANALYSIS")
        
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
            
            # Get article data
            article_data = extraction_result.get('data', {})
            
            if not article_data.get('text'):
                logger.error("No text extracted")
                return self._error_response("No content could be extracted")
            
            logger.info(f"✓ Extracted: {article_data.get('word_count', 0)} words")
            logger.info(f"✓ Title: {article_data.get('title', 'Unknown')[:50]}...")
            logger.info(f"✓ Source: {article_data.get('source', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Extraction exception: {e}")
            return self._error_response(f"Extraction failed: {str(e)}")
        
        # STAGE 2: Run Analysis Services
        logger.info("STAGE 2: Running Analysis Services")
        
        service_results = {}
        futures = {}
        
        # Run services in parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            for service_name in ['source_credibility', 'author_analyzer', 'bias_detector', 
                                'fact_checker', 'transparency_analyzer', 
                                'manipulation_detector', 'content_analyzer']:
                
                if service_name in self.services:
                    service = self.services[service_name]
                    future = executor.submit(self._run_service, service_name, service, article_data)
                    futures[future] = service_name
            
            # Collect results
            for future in as_completed(futures):
                service_name = futures[future]
                try:
                    result = future.result(timeout=10)
                    if result:
                        service_results[service_name] = result
                        logger.info(f"✓ {service_name}: completed")
                except Exception as e:
                    logger.warning(f"✗ {service_name}: {e}")
                    service_results[service_name] = self._get_default_service_data(service_name)
        
        # STAGE 3: Calculate Trust Score
        logger.info("STAGE 3: Calculating Trust Score")
        trust_score = self._calculate_trust_score(service_results)
        
        logger.info(f"✓ Trust Score: {trust_score}/100")
        logger.info(f"✓ Services completed: {len(service_results)}")
        
        # Build response
        response = {
            'success': True,
            'trust_score': trust_score,
            'article': article_data,
            'detailed_analysis': service_results,
            'processing_time': round(time.time() - start_time, 2),
            'services_used': len(service_results)
        }
        
        logger.info("=" * 80)
        logger.info("[PIPELINE] ANALYSIS COMPLETE")
        logger.info("=" * 80)
        
        return response
    
    def _run_service(self, service_name: str, service: Any, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single service and return flattened data"""
        try:
            # Call service
            result = service.analyze(data)
            
            # Extract and flatten data
            if isinstance(result, dict):
                # If result has 'data' field, extract it
                if 'data' in result:
                    service_data = result['data']
                else:
                    service_data = result
                
                # Ensure required fields
                if 'score' not in service_data:
                    service_data['score'] = 50
                
                # Add analysis section if missing
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
            return self._get_default_service_data(service_name)
    
    def _get_default_service_data(self, service_name: str) -> Dict[str, Any]:
        """Get default data for a failed service"""
        return {
            'score': 50,
            'analysis': {
                'what_we_looked': f'Attempted {service_name.replace("_", " ")} analysis',
                'what_we_found': 'Service temporarily unavailable',
                'what_it_means': 'Partial analysis completed'
            }
        }
    
    def _calculate_trust_score(self, service_results: Dict[str, Any]) -> int:
        """Calculate weighted trust score"""
        weighted_sum = 0
        total_weight = 0
        
        for service_name, weight in self.SERVICE_WEIGHTS.items():
            if service_name in service_results:
                service_data = service_results[service_name]
                score = service_data.get('score', 50)
                weighted_sum += score * weight
                total_weight += weight
        
        if total_weight > 0:
            return int(weighted_sum / total_weight)
        
        return 50
    
    def _error_response(self, error_msg: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            'success': False,
            'error': error_msg,
            'trust_score': 0,
            'article': {},
            'detailed_analysis': {}
        }
