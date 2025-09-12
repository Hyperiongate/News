"""
News Analyzer Service - COMPLETE FRONTEND DATA FIX
Date: September 12, 2025
Last Updated: September 12, 2025

CRITICAL FIXES:
1. Properly formats all service data for frontend consumption
2. Ensures detailed_analysis includes all service results
3. Fixes data structure to match frontend expectations
4. Includes all analysis fields the frontend displays
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
    News analysis orchestrator with COMPLETE frontend data handling
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
        Main analysis method with complete frontend response
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
            
            # Build complete response for frontend
            response = self._build_complete_frontend_response(pipeline_results, content)
            
            logger.info("Pipeline completed. Success: " + str(response.get('success', False)))
            logger.info(f"Response size: {len(str(response))} chars")
            logger.info(f"Services included: {list(response.get('detailed_analysis', {}).keys())}")
            
            return response
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            return self._error_response(str(e), content, 'analysis_error')
    
    def _extract_service_data(self, service_result: Any) -> Dict[str, Any]:
        """
        Extract and format service data for frontend consumption
        """
        if not service_result:
            return {}
        
        # Handle BaseAnalyzer wrapper format
        if isinstance(service_result, dict):
            # Extract data from nested structure if present
            if 'data' in service_result and isinstance(service_result['data'], dict):
                data = service_result['data']
            else:
                data = service_result
            
            # Ensure all required fields are present
            formatted = {}
            
            # Copy all fields
            for key, value in data.items():
                formatted[key] = value
            
            # Ensure score field exists
            if 'score' not in formatted:
                # Try to find a score in various fields
                for score_field in ['credibility_score', 'bias_score', 'quality_score', 
                                  'transparency_score', 'manipulation_score', 'fact_check_score']:
                    if score_field in formatted:
                        formatted['score'] = formatted[score_field]
                        break
                else:
                    # Default score if none found
                    formatted['score'] = 50
            
            # Ensure analysis section exists for frontend display
            if 'analysis' not in formatted:
                formatted['analysis'] = {
                    'what_we_looked': formatted.get('what_we_looked', 'Service analysis'),
                    'what_we_found': formatted.get('what_we_found', 'Analysis results'),
                    'what_it_means': formatted.get('what_it_means', 'Results interpretation')
                }
            
            return formatted
        
        return {}
    
    def _build_complete_frontend_response(self, pipeline_results: Dict[str, Any], content: str) -> Dict[str, Any]:
        """
        Build COMPLETE response for frontend with all service data properly formatted
        """
        start_time = time.time()
        
        # Check for pipeline success/failure
        if not pipeline_results.get('success', False):
            error_msg = pipeline_results.get('error', 'Analysis failed')
            return self._error_response(error_msg, content, 'pipeline_failed')
        
        # Extract article data
        article = pipeline_results.get('article', {})
        
        # Get the calculated trust score
        trust_score = pipeline_results.get('trust_score', 50)
        
        # Get and format detailed analysis for ALL services
        raw_analysis = pipeline_results.get('detailed_analysis', {})
        detailed_analysis = {}
        
        # Process each service result
        for service_name, service_result in raw_analysis.items():
            formatted_data = self._extract_service_data(service_result)
            if formatted_data:
                detailed_analysis[service_name] = formatted_data
                logger.info(f"Formatted {service_name}: {list(formatted_data.keys())[:5]}...")
        
        # Special handling for author_analyzer
        if 'author_analyzer' in detailed_analysis:
            author_data = detailed_analysis['author_analyzer']
            # Ensure all author fields are present
            author_data['combined_credibility_score'] = author_data.get('combined_credibility_score', 
                                                                        author_data.get('score', 50))
            author_data['author_name'] = author_data.get('author_name', 
                                                        author_data.get('name', article.get('author', 'Unknown')))
            
        # Count services that provided data
        services_count = len(detailed_analysis)
        
        # Build extraction quality metrics
        extraction_quality = {
            'score': 100 if article.get('extraction_successful') else 0,
            'services_used': services_count,
            'content_length': len(article.get('content', '')),
            'word_count': article.get('word_count', 0),
            'has_title': bool(article.get('title')),
            'has_author': bool(article.get('author') and article.get('author') != 'Unknown'),
            'has_source': bool(article.get('domain') and article.get('domain') != 'Unknown')
        }
        
        # Generate comprehensive findings summary
        findings_summary = self._generate_comprehensive_findings(
            trust_score,
            detailed_analysis,
            article
        )
        
        # Build the complete response with ALL data
        response = {
            'success': True,
            'trust_score': trust_score,
            'article_summary': article.get('title', 'Article analyzed'),
            'source': article.get('domain', article.get('source', 'Unknown')),
            'author': article.get('author', 'Unknown'),
            'findings_summary': findings_summary,
            'detailed_analysis': detailed_analysis,  # This contains ALL service data
            'article_metadata': {
                'url': article.get('url', content if content_type == 'url' else ''),
                'word_count': article.get('word_count', 0),
                'published_date': article.get('published_date', ''),
                'extraction_method': article.get('extraction_method', 'unknown')
            },
            'processing_time': round(time.time() - start_time, 2),
            'extraction_quality': extraction_quality,
            'services_summary': {
                'total': services_count,
                'successful': services_count,
                'failed': 0,
                'services': list(detailed_analysis.keys())
            },
            'message': f'Analysis complete - {services_count} services provided data.'
        }
        
        # Log what we're sending
        logger.info(f"Response built with trust_score={trust_score}, services={services_count}")
        logger.info(f"Detailed analysis keys: {list(detailed_analysis.keys())}")
        for service_name in detailed_analysis:
            service_data = detailed_analysis[service_name]
            logger.info(f"  {service_name}: score={service_data.get('score', 'N/A')}, "
                       f"fields={len(service_data)} keys")
        
        return response
    
    def _generate_comprehensive_findings(self, trust_score: int, detailed_analysis: Dict, article: Dict) -> str:
        """Generate comprehensive findings summary with all service insights"""
        findings = []
        
        # Overall trust assessment
        if trust_score >= 80:
            findings.append("✓ This article demonstrates high credibility and trustworthiness.")
        elif trust_score >= 60:
            findings.append("⚠ This article shows generally good credibility with some concerns.")
        elif trust_score >= 40:
            findings.append("⚠ This article has moderate credibility with several issues.")
        else:
            findings.append("✗ This article shows significant credibility concerns.")
        
        # Source credibility
        if 'source_credibility' in detailed_analysis:
            source_data = detailed_analysis['source_credibility']
            source_score = source_data.get('score', 0)
            source_name = article.get('domain', 'the source')
            if source_score >= 70:
                findings.append(f"The source {source_name} has established credibility.")
            elif source_score < 40:
                findings.append(f"The source {source_name} has limited credibility.")
        
        # Author credibility
        if 'author_analyzer' in detailed_analysis:
            author_data = detailed_analysis['author_analyzer']
            author_score = author_data.get('combined_credibility_score', 0)
            author_name = author_data.get('author_name', article.get('author', 'Unknown'))
            if author_name and author_name != 'Unknown':
                if author_score >= 70:
                    findings.append(f"Author {author_name} has strong credentials (score: {author_score}/100).")
                elif author_score >= 50:
                    findings.append(f"Author {author_name} has moderate credentials (score: {author_score}/100).")
                else:
                    findings.append(f"Author {author_name} has limited verified credentials.")
        
        # Bias detection
        if 'bias_detector' in detailed_analysis:
            bias_data = detailed_analysis['bias_detector']
            bias_score = bias_data.get('bias_score', bias_data.get('score', 50))
            political_lean = bias_data.get('political_lean', '')
            if bias_score < 30:
                findings.append("Content appears balanced with minimal bias.")
            elif bias_score > 70:
                findings.append(f"Significant bias detected ({political_lean} lean).")
        
        # Fact checking
        if 'fact_checker' in detailed_analysis:
            fact_data = detailed_analysis['fact_checker']
            claims_verified = fact_data.get('claims_verified', 0)
            claims_found = fact_data.get('claims_found', 0)
            if claims_found > 0:
                verification_rate = (claims_verified / claims_found) * 100
                findings.append(f"Fact-check: {claims_verified}/{claims_found} claims verified ({int(verification_rate)}%).")
        
        # Manipulation detection
        if 'manipulation_detector' in detailed_analysis:
            manip_data = detailed_analysis['manipulation_detector']
            manip_score = manip_data.get('manipulation_score', manip_data.get('score', 50))
            if manip_score > 70:
                findings.append("Warning: Manipulative techniques detected.")
            elif manip_score < 30:
                findings.append("No significant manipulation techniques found.")
        
        # Transparency
        if 'transparency_analyzer' in detailed_analysis:
            trans_data = detailed_analysis['transparency_analyzer']
            sources_cited = trans_data.get('sources_cited', 0)
            if sources_cited > 5:
                findings.append(f"Good transparency with {sources_cited} sources cited.")
            elif sources_cited == 0:
                findings.append("No sources cited - transparency concern.")
        
        return " ".join(findings) if findings else "Analysis completed."
    
    def _error_response(self, error_msg: str, content: str, error_type: str = 'unknown') -> Dict[str, Any]:
        """Create comprehensive error response"""
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
            'article_metadata': {},
            'processing_time': 0,
            'extraction_quality': {
                'score': 0,
                'services_used': 0
            },
            'services_summary': {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'services': []
            },
            'message': error_msg
        }
    
    def get_available_services(self) -> List[str]:
        """Get list of available services"""
        if self.service_registry:
            return [
                name for name, service in self.service_registry.services.items()
                if service and hasattr(service, 'available') and service.available
            ]
        return []
