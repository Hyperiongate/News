"""
News Analyzer Service - FRONTEND DATA FORMAT FIX
CRITICAL FIXES:
1. Returns data in exact format frontend expects
2. Proper extraction of article, source, and author information
3. Bulletproof response building with comprehensive fallbacks
4. Fixed trust score and findings summary generation
"""
import logging
from typing import Dict, Any, Optional
import time
from datetime import datetime

from services.analysis_pipeline import AnalysisPipeline
from services.service_registry import get_service_registry

logger = logging.getLogger(__name__)

class NewsAnalyzer:
    """
    FRONTEND DATA FORMAT FIX: Returns data in exact format frontend expects
    """
    
    def __init__(self):
        """Initialize with error handling"""
        try:
            self.pipeline = AnalysisPipeline()
            self.service_registry = get_service_registry()
            
            # Check service availability
            registry_status = self.service_registry.get_service_status()
            working_services = sum(1 for s in registry_status.get('services', {}).values() 
                                 if s.get('available', False))
            
            logger.info(f"NewsAnalyzer initialized - {working_services} services available")
            
        except Exception as e:
            logger.error(f"NewsAnalyzer initialization failed: {str(e)}", exc_info=True)
    
    def analyze(self, content: str, content_type: str = 'url', pro_mode: bool = False) -> Dict[str, Any]:
        """
        CRITICAL FIX: Main analysis method that returns exact frontend format
        Frontend expects: {success, trust_score, article_summary, source, author, findings_summary, detailed_analysis}
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
            logger.info("NEWS ANALYZER - FRONTEND DATA FORMAT FIX")
            logger.info(f"Content type: {content_type}")
            logger.info(f"Content: {str(content)[:100]}...")
            logger.info("=" * 80)
            
            # Validate pipeline
            if not hasattr(self, 'pipeline') or not self.pipeline:
                return self._build_error_response("Pipeline not available", content, content_type)
            
            # Run analysis pipeline
            try:
                pipeline_results = self.pipeline.analyze(data)
                logger.info(f"Pipeline completed - success: {pipeline_results.get('success', False)}")
            except Exception as pipeline_error:
                logger.error(f"Pipeline execution failed: {str(pipeline_error)}", exc_info=True)
                return self._build_error_response(f"Analysis failed: {str(pipeline_error)}", content, content_type)
            
            # Validate pipeline results
            if not isinstance(pipeline_results, dict) or not pipeline_results:
                return self._build_error_response("Pipeline returned invalid data", content, content_type)
            
            # CRITICAL FIX: Build response in exact frontend format
            response = self._build_frontend_response(pipeline_results, content, content_type)
            
            logger.info("=" * 80)
            logger.info("FRONTEND RESPONSE BUILT SUCCESSFULLY")
            logger.info(f"Success: {response.get('success', False)}")
            logger.info(f"Trust Score: {response.get('trust_score', 0)}")
            logger.info(f"Article Summary Length: {len(response.get('article_summary', ''))}")
            logger.info(f"Source: {response.get('source', 'Unknown')}")
            logger.info(f"Author: {response.get('author', 'Unknown')}")
            logger.info(f"Detailed Analysis Services: {len(response.get('detailed_analysis', {}))}")
            logger.info("=" * 80)
            
            return response
            
        except Exception as e:
            logger.error(f"Critical NewsAnalyzer error: {str(e)}", exc_info=True)
            return self._build_error_response(f"System error: {str(e)}", content, content_type)
    
    def _build_frontend_response(self, pipeline_results: Dict[str, Any], content: str, content_type: str) -> Dict[str, Any]:
        """
        CRITICAL FIX: Build response in exact format frontend expects
        """
        try:
            # Extract article data
            article_data = pipeline_results.get('article', {})
            logger.info(f"Article data keys: {list(article_data.keys())}")
            
            # Extract trust score
            trust_score = pipeline_results.get('trust_score', 50)
            if not isinstance(trust_score, (int, float)) or trust_score < 0 or trust_score > 100:
                trust_score = 50
            trust_score = int(trust_score)
            
            # CRITICAL FIX: Build article_summary (frontend expects this field)
            article_summary = self._extract_article_summary(article_data, content, content_type)
            
            # CRITICAL FIX: Extract source information
            source = self._extract_source_info(article_data, pipeline_results)
            
            # CRITICAL FIX: Extract author information  
            author = self._extract_author_info(article_data, pipeline_results)
            
            # Build detailed_analysis for service pages
            detailed_analysis = self._build_detailed_analysis(pipeline_results)
            
            # Generate findings summary
            findings_summary = self._generate_findings_summary(trust_score, detailed_analysis)
            
            # CRITICAL FIX: Return in exact frontend format
            response = {
                'success': True,
                'trust_score': trust_score,
                'article_summary': article_summary,
                'source': source,
                'author': author,
                'findings_summary': findings_summary,
                'detailed_analysis': detailed_analysis
            }
            
            # Log what we built for verification
            logger.info("FRONTEND RESPONSE VERIFICATION:")
            logger.info(f"✓ trust_score: {trust_score} (int)")
            logger.info(f"✓ article_summary: '{article_summary[:50]}...' ({len(article_summary)} chars)")
            logger.info(f"✓ source: '{source}'")
            logger.info(f"✓ author: '{author}'")
            logger.info(f"✓ detailed_analysis: {len(detailed_analysis)} services")
            
            return response
            
        except Exception as e:
            logger.error(f"Frontend response building failed: {str(e)}", exc_info=True)
            return self._build_error_response(f"Response building failed: {str(e)}", content, content_type)
    
    def _extract_article_summary(self, article_data: Dict[str, Any], content: str, content_type: str) -> str:
        """Extract article summary for frontend display"""
        
        # Strategy 1: Use article text (preferred)
        article_text = article_data.get('text', '')
        if article_text and len(article_text.strip()) > 50:
            # Use first 200 characters of text
            summary = article_text.strip()
            if len(summary) > 200:
                summary = summary[:200].rsplit(' ', 1)[0] + "..."
            logger.info(f"Article summary from text: {len(summary)} chars")
            return summary
        
        # Strategy 2: Use article title
        article_title = article_data.get('title', '')
        if article_title and article_title != 'Unknown Title':
            logger.info(f"Article summary from title: {article_title}")
            return article_title
        
        # Strategy 3: Use input content if text type
        if content_type == 'text' and content:
            summary = content.strip()
            if len(summary) > 200:
                summary = summary[:200].rsplit(' ', 1)[0] + "..."
            logger.info(f"Article summary from input: {len(summary)} chars")
            return summary
        
        # Strategy 4: Fallback
        logger.warning("No article summary available - using fallback")
        return "Article content extracted but summary not available"
    
    def _extract_source_info(self, article_data: Dict[str, Any], pipeline_results: Dict[str, Any]) -> str:
        """Extract source information for frontend"""
        
        # Strategy 1: From article domain
        domain = article_data.get('domain', '')
        if domain and domain.strip():
            logger.info(f"Source from article domain: {domain}")
            return domain
        
        # Strategy 2: Parse URL for domain
        url = article_data.get('url', '')
        if url:
            try:
                from urllib.parse import urlparse
                parsed = urlparse(url)
                if parsed.netloc:
                    domain = parsed.netloc
                    if domain.startswith('www.'):
                        domain = domain[4:]
                    logger.info(f"Source from URL parsing: {domain}")
                    return domain
            except Exception as e:
                logger.warning(f"URL parsing failed: {e}")
        
        # Strategy 3: From source_credibility service
        if 'source_credibility' in pipeline_results:
            source_data = pipeline_results['source_credibility']
            if isinstance(source_data, dict) and source_data.get('success'):
                source_name = source_data.get('source_name', '')
                if source_name and source_name not in ['Unknown Source', 'Unknown']:
                    logger.info(f"Source from credibility service: {source_name}")
                    return source_name
        
        logger.warning("No source information found - using fallback")
        return 'Unknown'
    
    def _extract_author_info(self, article_data: Dict[str, Any], pipeline_results: Dict[str, Any]) -> str:
        """Extract author information for frontend"""
        
        # Strategy 1: From article data (preferred)
        article_author = article_data.get('author', '')
        if article_author and article_author.strip() and article_author.lower() not in ['unknown', 'null', 'none']:
            logger.info(f"Author from article data: {article_author}")
            return article_author
        
        # Strategy 2: From author_analyzer service
        if 'author_analyzer' in pipeline_results:
            author_data = pipeline_results['author_analyzer']
            if isinstance(author_data, dict) and author_data.get('success'):
                author_name = author_data.get('author_name', '')
                if author_name and author_name.strip() and author_name.lower() not in ['unknown', 'null', 'none']:
                    logger.info(f"Author from analyzer service: {author_name}")
                    return author_name
        
        logger.warning("No author information found - using fallback")
        return 'Unknown'
    
    def _build_detailed_analysis(self, pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
        """Build detailed_analysis object for frontend service pages"""
        
        detailed_analysis = {}
        
        # Expected services that frontend knows about
        expected_services = [
            'source_credibility', 'author_analyzer', 'bias_detector', 
            'fact_checker', 'transparency_analyzer', 'manipulation_detector',
            'content_analyzer', 'openai_enhancer'
        ]
        
        for service_name in expected_services:
            if service_name in pipeline_results:
                service_data = pipeline_results[service_name]
                
                if isinstance(service_data, dict):
                    if service_data.get('success', False):
                        # Service succeeded - include all data
                        detailed_analysis[service_name] = service_data
                        logger.info(f"✓ {service_name}: Added to detailed_analysis")
                    else:
                        # Service failed - create error structure
                        detailed_analysis[service_name] = {
                            'success': False,
                            'error': service_data.get('error', 'Service failed'),
                            'available': service_data.get('available', False),
                            'service': service_name,
                            'score': 0,
                            'level': 'Error'
                        }
                        logger.warning(f"✗ {service_name}: Added error structure")
                else:
                    # Invalid service data
                    detailed_analysis[service_name] = {
                        'success': False,
                        'error': 'Invalid service response',
                        'available': False,
                        'service': service_name,
                        'score': 0,
                        'level': 'Error'
                    }
            else:
                # Service not in pipeline results
                detailed_analysis[service_name] = {
                    'success': False,
                    'error': 'Service not available',
                    'available': False,
                    'service': service_name,
                    'score': 0,
                    'level': 'Unavailable'
                }
                logger.info(f"- {service_name}: Not available, added placeholder")
        
        logger.info(f"Built detailed_analysis with {len(detailed_analysis)} services")
        return detailed_analysis
    
    def _generate_findings_summary(self, trust_score: int, detailed_analysis: Dict[str, Any]) -> str:
        """Generate findings summary based on analysis results"""
        
        try:
            # Base assessment from trust score
            if trust_score >= 80:
                base_assessment = "This article demonstrates very high trustworthiness"
            elif trust_score >= 70:
                base_assessment = "This article demonstrates high trustworthiness"
            elif trust_score >= 60:
                base_assessment = "This article is generally trustworthy"
            elif trust_score >= 40:
                base_assessment = "This article shows moderate trustworthiness"
            elif trust_score >= 20:
                base_assessment = "This article has low trustworthiness"
            else:
                base_assessment = "This article has very low trustworthiness"
            
            # Collect specific findings
            findings = []
            
            # Check source credibility
            if 'source_credibility' in detailed_analysis:
                source_data = detailed_analysis['source_credibility']
                if source_data.get('success') and isinstance(source_data.get('score'), (int, float)):
                    score = source_data['score']
                    if score >= 80:
                        findings.append("Source shows excellent credibility")
                    elif score < 40:
                        findings.append("Source credibility concerns identified")
            
            # Check bias
            if 'bias_detector' in detailed_analysis:
                bias_data = detailed_analysis['bias_detector']
                if bias_data.get('success') and isinstance(bias_data.get('score'), (int, float)):
                    score = bias_data['score']
                    if score > 70:
                        findings.append("High bias detected in content")
                    elif score < 30:
                        findings.append("Content shows minimal bias")
            
            # Check author credibility  
            if 'author_analyzer' in detailed_analysis:
                author_data = detailed_analysis['author_analyzer']
                if author_data.get('success') and isinstance(author_data.get('score'), (int, float)):
                    score = author_data['score']
                    if score >= 75:
                        findings.append("Author demonstrates strong credibility")
                    elif score < 40:
                        findings.append("Author credibility is questionable")
            
            # Check fact verification
            if 'fact_checker' in detailed_analysis:
                fact_data = detailed_analysis['fact_checker']
                if fact_data.get('success') and isinstance(fact_data.get('score'), (int, float)):
                    score = fact_data['score']
                    if score >= 80:
                        findings.append("Claims are well-verified")
                    elif score < 50:
                        findings.append("Some claims lack proper verification")
            
            # Build final summary
            summary_parts = [f"{base_assessment} with a score of {trust_score}/100"]
            
            if findings:
                summary_parts.append(". ".join(findings))
            
            final_summary = ". ".join(summary_parts) + "."
            
            logger.info(f"Generated findings summary: {len(final_summary)} chars")
            return final_summary
            
        except Exception as e:
            logger.error(f"Findings summary generation failed: {e}")
            return f"Analysis completed with a trust score of {trust_score}/100."
    
    def _build_error_response(self, error_message: str, content: str, content_type: str) -> Dict[str, Any]:
        """Build error response in exact frontend format"""
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
