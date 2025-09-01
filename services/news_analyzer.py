"""
News Analyzer Service - COMPLETE FRONTEND DATA SOLUTION
CRITICAL FIXES:
1. Fixed response structure to match frontend expectations exactly
2. Proper article, analysis, and detailed_analysis objects
3. Bulletproof data extraction and field mapping
4. Comprehensive error handling with proper fallbacks
"""
import logging
from typing import Dict, Any, Optional, List
import time
from datetime import datetime

from services.analysis_pipeline import AnalysisPipeline
from services.service_registry import get_service_registry

logger = logging.getLogger(__name__)

class NewsAnalyzer:
    """
    COMPLETE FRONTEND DATA SOLUTION: Returns data in exact format frontend expects
    """
    
    def __init__(self):
        """Initialize with comprehensive error handling"""
        try:
            self.pipeline = AnalysisPipeline()
            self.service_registry = get_service_registry()
            
            # Validate service registry is working
            registry_status = self.service_registry.get_service_status()
            working_services = sum(1 for s in registry_status.get('services', {}).values() if s.get('available', False))
            
            logger.info(f"NewsAnalyzer initialized - {working_services} services available")
            
            if working_services == 0:
                logger.error("CRITICAL: No services available in registry")
                
        except Exception as e:
            logger.error(f"NewsAnalyzer initialization failed: {str(e)}", exc_info=True)
            # Continue anyway - we'll handle this in analyze()
    
    def analyze(self, content: str, content_type: str = 'url', pro_mode: bool = False) -> Dict[str, Any]:
        """
        COMPLETE FRONTEND DATA SOLUTION: Returns exact structure frontend expects
        """
        try:
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
            logger.info("COMPLETE FRONTEND DATA SOLUTION")
            logger.info(f"Content type: {content_type}")
            logger.info(f"Content length: {len(str(content))}")
            logger.info(f"Pro mode: {pro_mode}")
            logger.info("=" * 80)
            
            # Validate pipeline exists
            if not hasattr(self, 'pipeline') or not self.pipeline:
                logger.error("Pipeline not initialized")
                return self._build_frontend_error_response("Pipeline initialization failed", content, content_type)
            
            # Run pipeline
            try:
                pipeline_results = self.pipeline.analyze(data)
                logger.info(f"Pipeline returned {len(pipeline_results)} keys: {list(pipeline_results.keys())}")
            except Exception as pipeline_error:
                logger.error(f"Pipeline execution failed: {str(pipeline_error)}", exc_info=True)
                return self._build_frontend_error_response(f"Pipeline failed: {str(pipeline_error)}", content, content_type)
            
            # Validate pipeline results
            if not isinstance(pipeline_results, dict) or not pipeline_results:
                logger.error("Pipeline returned invalid or empty results")
                return self._build_frontend_error_response("Pipeline returned no data", content, content_type)
            
            # Build response in EXACT frontend format
            response = self._build_frontend_response(pipeline_results, content, content_type, pro_mode)
            
            logger.info("=" * 80)
            logger.info("FRONTEND DATA SOLUTION COMPLETE")
            logger.info(f"Response success: {response.get('success')}")
            logger.info(f"Trust score: {response.get('trust_score', 'N/A')}")
            logger.info(f"Article title: {response.get('article_summary', 'N/A')[:50]}...")
            logger.info(f"Source: {response.get('source', 'N/A')}")
            logger.info(f"Author: {response.get('author', 'N/A')}")
            logger.info("=" * 80)
            
            return response
            
        except Exception as e:
            logger.error(f"CRITICAL NewsAnalyzer error: {str(e)}", exc_info=True)
            return self._build_frontend_error_response(f"Critical analysis failure: {str(e)}", content, content_type)
    
    def _build_frontend_response(self, pipeline_results: Dict[str, Any], content: str, 
                                content_type: str, pro_mode: bool) -> Dict[str, Any]:
        """
        CRITICAL: Build response in EXACT format frontend expects
        Frontend expects these exact top-level fields:
        - success
        - trust_score
        - article_summary
        - source
        - author
        - findings_summary
        - detailed_analysis (object with service data)
        """
        try:
            # Extract article data from pipeline
            article_data = pipeline_results.get('article', {})
            if not article_data:
                logger.warning("No article data in pipeline results")
                article_data = self._create_fallback_article(content, content_type)
            
            # Calculate trust score
            trust_score = pipeline_results.get('trust_score', 50)
            if not isinstance(trust_score, (int, float)) or trust_score < 0 or trust_score > 100:
                trust_score = 50
            trust_score = int(trust_score)
            
            # Extract core frontend fields
            article_title = article_data.get('title', 'Unknown Title')
            article_text = article_data.get('text', '')
            
            # Create article summary (first 200 chars of text or title)
            if article_text and len(article_text) > 100:
                article_summary = article_text[:200] + "..." if len(article_text) > 200 else article_text
            else:
                article_summary = article_title
            
            # Extract source information
            source_info = self._extract_source_info(article_data, pipeline_results)
            
            # Extract author information
            author_info = self._extract_author_info(article_data, pipeline_results)
            
            # Build detailed_analysis object for frontend service pages
            detailed_analysis = self._build_detailed_analysis(pipeline_results)
            
            # Generate findings summary
            findings_summary = self._generate_findings_summary(trust_score, detailed_analysis, pipeline_results)
            
            # CRITICAL: Build response in EXACT frontend format
            response = {
                'success': True,
                'trust_score': trust_score,
                'article_summary': article_summary,
                'source': source_info,
                'author': author_info,
                'findings_summary': findings_summary,
                'detailed_analysis': detailed_analysis
            }
            
            logger.info("✓ FRONTEND RESPONSE BUILT:")
            logger.info(f"  - trust_score: {trust_score}")
            logger.info(f"  - article_summary: {len(article_summary)} chars")
            logger.info(f"  - source: {source_info}")
            logger.info(f"  - author: {author_info}")
            logger.info(f"  - detailed_analysis services: {len(detailed_analysis)}")
            
            return response
            
        except Exception as e:
            logger.error(f"Frontend response building failed: {str(e)}", exc_info=True)
            return self._build_frontend_error_response(f"Response building failed: {str(e)}", content, content_type)
    
    def _extract_source_info(self, article_data: Dict[str, Any], pipeline_results: Dict[str, Any]) -> str:
        """Extract source information for frontend"""
        
        # Strategy 1: From article data
        domain = article_data.get('domain', '')
        if domain:
            return domain
        
        # Strategy 2: From URL
        url = article_data.get('url', '')
        if url:
            try:
                from urllib.parse import urlparse
                parsed = urlparse(url)
                if parsed.netloc:
                    return parsed.netloc
            except:
                pass
        
        # Strategy 3: From source credibility service
        if 'source_credibility' in pipeline_results:
            source_data = pipeline_results['source_credibility']
            if isinstance(source_data, dict) and source_data.get('success'):
                source_name = source_data.get('source_name', '')
                if source_name and source_name != 'Unknown Source':
                    return source_name
        
        return 'Unknown'
    
    def _extract_author_info(self, article_data: Dict[str, Any], pipeline_results: Dict[str, Any]) -> str:
        """Extract author information for frontend"""
        
        # Strategy 1: From article data
        article_author = article_data.get('author', '')
        if article_author and article_author.lower() not in ['unknown', 'null', 'none', '']:
            return article_author
        
        # Strategy 2: From author analyzer service
        if 'author_analyzer' in pipeline_results:
            author_data = pipeline_results['author_analyzer']
            if isinstance(author_data, dict) and author_data.get('success'):
                author_name = author_data.get('author_name', '')
                if author_name and author_name.lower() not in ['unknown', 'null', 'none', '']:
                    logger.info(f"✓ AUTHOR FROM SERVICE: {author_name}")
                    return author_name
        
        return 'Unknown'
    
    def _build_detailed_analysis(self, pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
        """Build detailed_analysis object for frontend service pages"""
        
        detailed_analysis = {}
        
        # Define expected services and their required structure
        expected_services = [
            'source_credibility', 'author_analyzer', 'bias_detector', 
            'fact_checker', 'transparency_analyzer', 'manipulation_detector',
            'content_analyzer', 'openai_enhancer'
        ]
        
        for service_name in expected_services:
            if service_name in pipeline_results:
                service_data = pipeline_results[service_name]
                
                if isinstance(service_data, dict) and service_data.get('success', False):
                    # Service succeeded - copy all data
                    detailed_analysis[service_name] = service_data.copy()
                    logger.info(f"✓ Service {service_name} added to detailed_analysis")
                else:
                    # Service failed - create error structure
                    detailed_analysis[service_name] = {
                        'success': False,
                        'error': service_data.get('error', 'Service failed') if isinstance(service_data, dict) else 'Service failed',
                        'available': service_data.get('available', False) if isinstance(service_data, dict) else False,
                        'service': service_name,
                        'score': 0,
                        'level': 'Error'
                    }
                    logger.warning(f"✗ Service {service_name} failed, added error structure")
            else:
                # Service not in pipeline results - create unavailable structure
                detailed_analysis[service_name] = {
                    'success': False,
                    'error': 'Service not available',
                    'available': False,
                    'service': service_name,
                    'score': 0,
                    'level': 'Unavailable'
                }
                logger.info(f"- Service {service_name} not available, added placeholder")
        
        logger.info(f"✓ Built detailed_analysis with {len(detailed_analysis)} services")
        return detailed_analysis
    
    def _generate_findings_summary(self, trust_score: int, detailed_analysis: Dict[str, Any], 
                                 pipeline_results: Dict[str, Any]) -> str:
        """Generate findings summary based on analysis results"""
        
        try:
            # Base assessment from trust score
            if trust_score >= 80:
                base_assessment = "This article demonstrates high trustworthiness"
            elif trust_score >= 60:
                base_assessment = "This article is generally trustworthy"
            elif trust_score >= 40:
                base_assessment = "This article has moderate trustworthiness"
            elif trust_score >= 20:
                base_assessment = "This article shows low trustworthiness"
            else:
                base_assessment = "This article has very low trustworthiness"
            
            # Collect specific findings
            findings = []
            
            # Check source credibility
            if 'source_credibility' in detailed_analysis:
                source_data = detailed_analysis['source_credibility']
                if source_data.get('success') and source_data.get('score', 0) < 40:
                    findings.append("Source credibility concerns identified")
            
            # Check bias
            if 'bias_detector' in detailed_analysis:
                bias_data = detailed_analysis['bias_detector']
                if bias_data.get('success') and bias_data.get('score', 0) > 60:
                    findings.append("Significant bias detected")
            
            # Check author credibility
            if 'author_analyzer' in detailed_analysis:
                author_data = detailed_analysis['author_analyzer']
                if author_data.get('success') and author_data.get('score', 0) > 70:
                    findings.append("Author shows good credibility")
            
            # Check manipulation
            if 'manipulation_detector' in detailed_analysis:
                manip_data = detailed_analysis['manipulation_detector']
                if manip_data.get('success'):
                    tactics = len(manip_data.get('tactics_found', []))
                    if tactics > 2:
                        findings.append("Multiple manipulation tactics found")
            
            # Build final summary
            if findings:
                return f"{base_assessment}. {'. '.join(findings)}."
            else:
                return f"{base_assessment} based on available analysis."
                
        except Exception as e:
            logger.error(f"Findings summary generation failed: {e}")
            return f"Analysis completed with trust score of {trust_score}/100."
    
    def _create_fallback_article(self, content: str, content_type: str) -> Dict[str, Any]:
        """Create fallback article data when extraction fails"""
        return {
            'title': 'Article Analysis',
            'text': content if content_type == 'text' else '',
            'author': 'Unknown',
            'url': content if content_type == 'url' else '',
            'domain': '',
            'word_count': len(content.split()) if content else 0,
            'extraction_successful': False
        }
    
    def _build_frontend_error_response(self, error_message: str, content: str, content_type: str) -> Dict[str, Any]:
        """Build error response in frontend format"""
        return {
            'success': False,
            'error': error_message,
            'trust_score': 0,
            'article_summary': 'Article summary not available',
            'source': 'Unknown',
            'author': 'Unknown',
            'findings_summary': f'Analysis failed: {error_message}',
            'detailed_analysis': {
                'source_credibility': {'success': False, 'error': error_message, 'score': 0, 'level': 'Error'},
                'author_analyzer': {'success': False, 'error': error_message, 'score': 0, 'level': 'Error'},
                'bias_detector': {'success': False, 'error': error_message, 'score': 0, 'level': 'Error'},
                'fact_checker': {'success': False, 'error': error_message, 'score': 0, 'level': 'Error'},
                'transparency_analyzer': {'success': False, 'error': error_message, 'score': 0, 'level': 'Error'},
                'manipulation_detector': {'success': False, 'error': error_message, 'score': 0, 'level': 'Error'},
                'content_analyzer': {'success': False, 'error': error_message, 'score': 0, 'level': 'Error'},
                'openai_enhancer': {'success': False, 'error': error_message, 'score': 0, 'level': 'Error'}
            }
        }
    
    def get_available_services(self) -> Dict[str, Any]:
        """Get information about available services"""
        try:
            return self.service_registry.get_service_status()
        except Exception as e:
            logger.error(f"Failed to get service status: {e}")
            return {'services': {}, 'summary': {'available': 0, 'total': 0}}
    
    def get_service_info(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific service"""
        try:
            return self.service_registry.get_service_info(service_name)
        except Exception as e:
            logger.error(f"Failed to get service info for {service_name}: {e}")
            return None
