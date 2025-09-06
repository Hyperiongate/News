"""
News Analyzer Service - FIXED RESPONSE BUILDING VERSION
Date: September 6, 2025
Last Updated: September 6, 2025

CRITICAL FIXES:
1. Trust score now properly passed to frontend (was being overridden to 0)
2. Extraction quality calculation fixed
3. Proper handling when author_analyzer is unavailable
4. Response building preserves calculated values
"""
import logging
from typing import Dict, Any, Optional, List, Union
import time
from datetime import datetime
import traceback

from services.analysis_pipeline import AnalysisPipeline
from services.service_registry import get_service_registry

logger = logging.getLogger(__name__)


class NewsAnalyzer:
    """
    News analysis orchestrator with FIXED response building
    """
    
    # Service weight configuration
    STANDARD_WEIGHTS = {
        'source_credibility': 0.25,
        'author_analyzer': 0.15,
        'bias_detector': 0.20,
        'fact_checker': 0.15,
        'transparency_analyzer': 0.10,
        'manipulation_detector': 0.10,
        'content_analyzer': 0.05
    }
    
    def __init__(self):
        """Initialize with error handling"""
        try:
            self.pipeline = AnalysisPipeline()
            self.service_registry = get_service_registry()
            
            registry_status = self.service_registry.get_service_status()
            working_services = sum(1 for s in registry_status.get('services', {}).values() 
                                 if s.get('available', False))
            
            logger.info(f"NewsAnalyzer initialized - {working_services} services available")
            
        except Exception as e:
            logger.error(f"NewsAnalyzer initialization failed: {str(e)}", exc_info=True)
            self.pipeline = None
            self.service_registry = None
    
    def analyze(self, content: str, content_type: str = 'url', pro_mode: bool = False) -> Dict[str, Any]:
        """
        Main analysis method with FIXED response building
        """
        try:
            # Check initialization
            if not self.pipeline:
                logger.error("Pipeline not initialized")
                return self._error_response("Analysis service not available", '', 'initialization_failed')
            
            # Prepare input data
            data = {
                'is_pro': pro_mode,
                'analysis_mode': 'pro' if pro_mode else 'basic'
            }
            
            if content_type == 'url':
                data['url'] = content
            else:
                data['text'] = content
                data['content_type'] = 'text'
            
            logger.info("=" * 80)
            logger.info("NEWSANALYZER.ANALYZE CALLED")
            logger.info(f"Backward compatible mode: content_type={content_type}")
            logger.info(f"Input: URL={content_type == 'url'}, Text={content_type == 'text'}")
            
            # Run pipeline
            logger.info("Running analysis pipeline...")
            pipeline_results = self.pipeline.analyze(data)
            
            # Build response with FIXED trust score handling
            response = self._build_frontend_response_fixed(pipeline_results, content)
            
            logger.info("Pipeline completed. Success: " + str(response.get('success', False)))
            logger.info(f"Pipeline keys: {list(response.keys())}")
            
            return response
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            return self._error_response(str(e), content, 'analysis_error')
    
    def _build_frontend_response_fixed(self, pipeline_results: Dict[str, Any], content: str) -> Dict[str, Any]:
        """
        FIXED: Build response for frontend preserving calculated values
        """
        start_time = time.time()
        
        # Check for pipeline success/failure
        if not pipeline_results.get('success', False):
            error_msg = pipeline_results.get('error', 'Analysis failed')
            return self._error_response(error_msg, content, 'pipeline_failed')
        
        # Extract article data
        article = pipeline_results.get('article', {})
        
        # Get the ACTUAL calculated trust score from pipeline
        trust_score = pipeline_results.get('trust_score', 50)
        
        # Get detailed analysis
        detailed_analysis = pipeline_results.get('detailed_analysis', {})
        
        # Count actual services that provided data
        services_count = len(detailed_analysis)
        
        # Calculate extraction quality based on what we actually have
        extraction_quality = {
            'score': 100 if article.get('extraction_successful') else 0,
            'services_used': services_count,
            'content_length': len(article.get('content', '')),
            'word_count': article.get('word_count', 0),
            'has_title': bool(article.get('title')),
            'has_source': bool(article.get('domain'))
        }
        
        # Generate findings summary
        findings_summary = self._generate_findings_summary(
            trust_score,
            detailed_analysis,
            article
        )
        
        # Build the response with CORRECT values
        response = {
            'success': True,
            'trust_score': trust_score,  # Use the ACTUAL calculated score
            'article_summary': article.get('title', 'Article analyzed'),
            'source': article.get('domain', 'Unknown'),
            'author': article.get('author', 'Unknown'),
            'findings_summary': findings_summary,
            'detailed_analysis': detailed_analysis,
            'processing_time': round(time.time() - start_time, 2),
            'extraction_quality': extraction_quality,
            'message': f'Analysis complete - {services_count} services provided data.'
        }
        
        # Log what we're actually sending
        logger.info(f"Extraction quality: {services_count}/{len(self.STANDARD_WEIGHTS)} services, "
                   f"content={len(article.get('content', ''))} chars, "
                   f"word_count={article.get('word_count', 0)}, "
                   f"title={bool(article.get('title'))}, "
                   f"source={bool(article.get('domain'))}")
        
        return response
    
    def _generate_findings_summary(self, trust_score: int, detailed_analysis: Dict, article: Dict) -> str:
        """Generate comprehensive findings summary"""
        findings = []
        
        # Trust level assessment
        if trust_score >= 80:
            findings.append("This article demonstrates high credibility and trustworthiness.")
        elif trust_score >= 60:
            findings.append("This article shows generally good credibility with some minor concerns.")
        elif trust_score >= 40:
            findings.append("This article has moderate credibility with several issues identified.")
        else:
            findings.append("This article shows significant credibility concerns.")
        
        # Add source info
        source = article.get('domain', '')
        if source and source != 'Unknown':
            findings.append(f"Published by {source}.")
        
        # Add service-specific findings
        if detailed_analysis:
            # Bias detection
            if 'bias_detector' in detailed_analysis:
                bias_data = detailed_analysis['bias_detector']
                if isinstance(bias_data, dict):
                    bias_score = bias_data.get('bias_score', 0)
                    if bias_score < 30:
                        findings.append("Content appears balanced with minimal bias.")
                    elif bias_score > 70:
                        findings.append("Significant bias detected in the presentation.")
            
            # Fact checking
            if 'fact_checker' in detailed_analysis:
                fact_data = detailed_analysis['fact_checker']
                if isinstance(fact_data, dict):
                    verified = fact_data.get('verified_claims', 0)
                    total = fact_data.get('claims_checked', 0)
                    if total > 0:
                        percentage = (verified / total) * 100
                        findings.append(f"Fact-checking: {int(percentage)}% of claims verified.")
            
            # Author credibility (if available)
            if 'author_analyzer' in detailed_analysis:
                author_data = detailed_analysis['author_analyzer']
                if isinstance(author_data, dict):
                    author_score = author_data.get('combined_credibility_score', 0)
                    if author_score > 0:
                        findings.append(f"Author credibility score: {author_score}/100.")
        
        return " ".join(findings) if findings else "Analysis completed."
    
    def _error_response(self, error_msg: str, content: str, error_type: str = 'unknown') -> Dict[str, Any]:
        """Create error response"""
        return {
            'success': False,
            'error': error_msg,
            'error_type': error_type,
            'trust_score': 0,
            'article_summary': 'Analysis failed',
            'source': 'Unknown',
            'author': 'Unknown',
            'findings_summary': f'Analysis failed: {error_msg}',
            'detailed_analysis': {},
            'processing_time': 0,
            'extraction_quality': {
                'score': 0,
                'services_used': 0
            }
        }
    
    def get_available_services(self) -> List[str]:
        """Get list of available services"""
        if self.service_registry:
            return [
                name for name, service in self.service_registry.services.items()
                if service and hasattr(service, 'available') and service.available
            ]
        return []
