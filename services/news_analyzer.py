"""
Complete Enhanced NewsAnalyzer with Backward Compatibility
CRITICAL: Maintains ALL existing functionality plus enhancements
Works with existing app.py without any changes
"""

import logging
import time
from typing import Dict, Any, Optional, List
import re
import json
import traceback
from datetime import datetime

from services.analysis_pipeline import AnalysisPipeline
from services.service_registry import get_service_registry

logger = logging.getLogger(__name__)

class NewsAnalyzer:
    """Complete news analyzer with backward compatibility and all enhancements"""
    
    # Standard service weights
    STANDARD_WEIGHTS = {
        'source_credibility': 0.25,
        'author_analyzer': 0.15,
        'bias_detector': 0.20,
        'fact_checker': 0.15,
        'transparency_analyzer': 0.10,
        'manipulation_detector': 0.10,
        'content_analyzer': 0.05
    }
    
    # Weights when author data is missing for reputable sources
    ADAPTIVE_WEIGHTS_NO_AUTHOR = {
        'source_credibility': 0.35,  # +10% from author
        'bias_detector': 0.25,       # +5% from author
        'fact_checker': 0.15,
        'transparency_analyzer': 0.10,
        'manipulation_detector': 0.10,
        'content_analyzer': 0.05
    }
    
    def __init__(self):
        """Initialize NewsAnalyzer with all services"""
        logger.info("=" * 80)
        logger.info("Initializing Enhanced NewsAnalyzer")
        logger.info("=" * 80)
        
        try:
            self.pipeline = AnalysisPipeline()
            logger.info("Analysis pipeline initialized")
        except Exception as e:
            logger.error(f"Failed to initialize pipeline: {e}")
            self.pipeline = None
            
        try:
            self.registry = get_service_registry()
            logger.info(f"Service registry initialized")
        except Exception as e:
            logger.error(f"Failed to initialize registry: {e}")
            self.registry = None
        
        self._cache = {}
        self._last_analysis = None
        logger.info("NewsAnalyzer initialization complete")
        
    def get_available_services(self):
        """Get list of available services"""
        try:
            if self.registry:
                status = self.registry.get_service_status()
                return list(status.get('services', {}).keys())
            return []
        except Exception as e:
            logger.error(f"Error getting available services: {e}")
            return []
    
    def analyze(self, content=None, content_type=None, url=None, text=None):
        """
        BACKWARD COMPATIBLE: Accepts both old and new calling conventions
        Old: analyze(content='...', content_type='url'|'text')
        New: analyze(url='...') or analyze(text='...')
        """
        start_time = time.time()
        
        # Log the call
        logger.info("=" * 80)
        logger.info("NEWSANALYZER.ANALYZE CALLED")
        
        # BACKWARD COMPATIBILITY: Convert old calling convention to new
        if content is not None and content_type is not None:
            logger.info(f"Backward compatible mode: content_type={content_type}")
            if content_type == 'url':
                url = content
                text = None
            else:
                text = content
                url = None
        
        logger.info(f"Input: URL={bool(url)}, Text={bool(text)}")
        
        # Validate input
        if not url and not text:
            logger.warning("No input provided")
            return self._error_response(
                'no_input',
                'Please provide either a URL or article text',
                start_time
            )
        
        # Check pipeline availability
        if not self.pipeline:
            logger.error("Pipeline not available")
            return self._error_response(
                'service_unavailable',
                'Analysis service is not available',
                start_time
            )
        
        try:
            # Prepare input data for pipeline
            input_data = self._prepare_input_data(url, text)
            
            # Run the analysis pipeline
            logger.info("Running analysis pipeline...")
            pipeline_results = self.pipeline.analyze(input_data)
            
            # Process pipeline results
            return self._process_pipeline_results(pipeline_results, url, text, start_time)
            
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}", exc_info=True)
            return self._error_response(
                'analysis_failed',
                f'Analysis failed: {str(e)}',
                start_time
            )
    
    def _prepare_input_data(self, url, text):
        """Prepare input data for pipeline"""
        input_data = {
            'url': url if url else None,
            'text': text if text else None,
            'content_type': 'url' if url else 'text',
            'timestamp': datetime.now().isoformat()
        }
        
        # Add URL metadata if available
        if url:
            input_data['domain'] = self._extract_domain(url)
            
        return input_data
    
    def _process_pipeline_results(self, pipeline_results, url, text, start_time):
        """Process results from pipeline and build response"""
        
        # Check for pipeline failures
        if not pipeline_results.get('success', False):
            return self._handle_pipeline_failure(pipeline_results, url, start_time)
        
        # Extract data from pipeline results
        article_data = self._extract_article_data(pipeline_results)
        detailed_analysis = self._extract_detailed_analysis(pipeline_results)
        
        # Assess extraction quality
        extraction_quality = self._assess_extraction_quality(article_data, detailed_analysis)
        
        # Check for insufficient content
        if extraction_quality == 'failed':
            logger.warning("Insufficient content for analysis")
            return self._error_response(
                'insufficient_content',
                'Unable to extract enough content for meaningful analysis',
                start_time,
                article_data=article_data
            )
        
        # Calculate trust score with adaptive weights if needed
        trust_score = self._calculate_adaptive_trust_score(detailed_analysis, extraction_quality)
        
        # Generate summaries
        article_summary = self._generate_article_summary(article_data, detailed_analysis)
        findings_summary = self._generate_findings_summary(
            trust_score,
            article_data.get('source') or article_data.get('domain', 'Unknown'),
            detailed_analysis
        )
        
        # Build successful response
        response = self._build_success_response(
            trust_score=trust_score,
            article_summary=article_summary,
            findings_summary=findings_summary,
            article_data=article_data,
            detailed_analysis=detailed_analysis,
            extraction_quality=extraction_quality,
            start_time=start_time
        )
        
        # Cache the result
        self._last_analysis = response
        
        logger.info(f"Analysis successful: score={trust_score}, time={response['processing_time']:.2f}s")
        logger.info("=" * 80)
        
        return response
    
    def _handle_pipeline_failure(self, pipeline_results, url, start_time):
        """Handle pipeline failure scenarios"""
        
        # Check for paywall
        if self._detect_paywall(pipeline_results):
            logger.info("Paywall detected")
            return {
                'success': False,
                'error': 'paywall_detected',
                'message': 'This site requires a subscription. Please copy and paste the article text into the text box below for analysis.',
                'trust_score': 0,
                'article_summary': 'Subscription required',
                'source': self._extract_domain(url) if url else 'Unknown',
                'author': 'Unknown',
                'findings_summary': 'Unable to access article due to paywall. Please copy and paste the text.',
                'detailed_analysis': {},
                'processing_time': time.time() - start_time
            }
        
        # General extraction failure
        error_msg = pipeline_results.get('error', 'Extraction failed')
        return self._error_response(
            'extraction_failed',
            f'Unable to extract article: {error_msg}',
            start_time
        )
    
    def _extract_article_data(self, pipeline_results):
        """Extract article data from pipeline results"""
        article = pipeline_results.get('article', {})
        
        # Ensure all expected fields exist
        return {
            'title': article.get('title', ''),
            'content': article.get('content', ''),
            'source': article.get('source', ''),
            'domain': article.get('domain', ''),
            'author': article.get('author', 'Unknown'),
            'published_date': article.get('published_date', ''),
            'url': article.get('url', ''),
            'excerpt': article.get('excerpt', '') or article.get('content', '')[:500]
        }
    
    def _extract_detailed_analysis(self, pipeline_results):
        """Extract and normalize detailed analysis from pipeline results"""
        detailed = pipeline_results.get('detailed_analysis', {})
        normalized = {}
        
        for service_name, service_data in detailed.items():
            if service_data is None:
                normalized[service_name] = {}
            elif isinstance(service_data, dict):
                normalized[service_name] = service_data
            elif isinstance(service_data, (int, float)):
                normalized[service_name] = {'score': service_data}
            elif isinstance(service_data, str):
                normalized[service_name] = {'result': service_data}
            elif isinstance(service_data, list):
                normalized[service_name] = {'findings': service_data}
            else:
                normalized[service_name] = {'data': str(service_data)}
        
        return normalized
    
    def _detect_paywall(self, pipeline_results):
        """Detect if article is behind paywall"""
        article = pipeline_results.get('article', {})
        content = article.get('content', '')
        title = article.get('title', '')
        error = pipeline_results.get('error', '').lower()
        
        # Check error messages
        if 'paywall' in error or 'subscription' in error:
            return True
        
        # Paywall indicators
        paywall_markers = [
            'subscribe to read',
            'subscription required',
            'subscribers only',
            'please log in',
            'paywall',
            'member exclusive',
            'premium content'
        ]
        
        # Check for short content with paywall markers
        full_text = (content + ' ' + title).lower()
        if len(content) < 500:
            for marker in paywall_markers:
                if marker in full_text:
                    return True
        
        # Title but minimal content often indicates paywall
        if title and len(content) < 200:
            return True
            
        return False
    
    def _assess_extraction_quality(self, article_data, detailed_analysis):
        """Assess quality of extraction"""
        # Count successful services
        successful_services = 0
        total_services = len(self.STANDARD_WEIGHTS)
        
        for service_name in self.STANDARD_WEIGHTS.keys():
            service_data = detailed_analysis.get(service_name, {})
            score = self._safe_get(service_data, 'score', 0) or \
                   self._safe_get(service_data, 'credibility_score', 0) or \
                   self._safe_get(service_data, 'quality_score', 0)
            if score > 0:
                successful_services += 1
        
        # Check content quality
        content = article_data.get('content', '')
        has_content = bool(content) and len(content) > 200
        has_title = bool(article_data.get('title'))
        has_source = bool(article_data.get('source') or article_data.get('domain'))
        
        # Log assessment
        logger.info(f"Extraction quality: {successful_services}/{total_services} services, "
                   f"content={len(content)} chars, title={has_title}, source={has_source}")
        
        # Determine quality level
        if successful_services >= total_services - 1 and has_content and has_title:
            return 'full'
        elif successful_services >= 3 and has_content:
            return 'partial'
        else:
            return 'failed'
    
    def _calculate_adaptive_trust_score(self, detailed_analysis, extraction_quality):
        """Calculate trust score with adaptive weights for missing services"""
        
        # Extract key scores
        author_score = self._get_service_score(detailed_analysis.get('author_analyzer', {}), 'author')
        source_score = self._get_service_score(detailed_analysis.get('source_credibility', {}), 'source')
        
        # Determine weight strategy
        if author_score == 0 and source_score >= 70:
            # Reputable source with missing author - use adaptive weights
            logger.info(f"Adaptive scoring: reputable source ({source_score}) with no author")
            weights = self.ADAPTIVE_WEIGHTS_NO_AUTHOR
            skip_author = True
        else:
            weights = self.STANDARD_WEIGHTS
            skip_author = False
        
        # Calculate weighted score
        total_score = 0
        total_weight = 0
        scores_breakdown = {}
        
        for service_name, weight in weights.items():
            if skip_author and service_name == 'author_analyzer':
                continue
            
            service_data = detailed_analysis.get(service_name, {})
            service_score = self._get_service_score(service_data, service_name)
            
            # Apply service-specific transformations
            if service_name == 'bias_detector':
                # Convert bias to objectivity
                bias = service_score
                service_score = 100 - bias
                scores_breakdown[service_name] = f"{service_score}% (objectivity from {bias}% bias)"
            elif service_name == 'manipulation_detector':
                # Invert manipulation score
                manip = service_score
                service_score = 100 - manip
                scores_breakdown[service_name] = f"{service_score}% (inverted from {manip}% manipulation)"
            else:
                scores_breakdown[service_name] = f"{service_score}%"
            
            total_score += service_score * weight
            total_weight += weight
        
        # Normalize if weights don't sum to 1
        if total_weight > 0 and total_weight < 1:
            total_score = total_score / total_weight
        
        final_score = round(min(max(total_score, 0), 100))
        
        logger.info(f"Trust score calculation: {final_score}")
        logger.info(f"Breakdown: {scores_breakdown}")
        
        return final_score
    
    def _get_service_score(self, service_data, service_name):
        """Extract score from service data with service-specific logic"""
        
        if service_name == 'fact_checker':
            # Special handling for fact checker
            claims_found = self._safe_get(service_data, 'claims_found', 0) or \
                          self._safe_get(service_data, 'claims_analyzed', 0)
            claims_verified = self._safe_get(service_data, 'claims_verified', 0)
            
            if claims_found > 0:
                return (claims_verified / claims_found) * 100
            
        elif service_name == 'transparency_analyzer':
            # Special handling for transparency
            sources = self._safe_get(service_data, 'source_count', 0) or \
                     self._safe_get(service_data, 'sources_cited', 0)
            quotes = self._safe_get(service_data, 'quote_count', 0) or \
                    self._safe_get(service_data, 'quotes_used', 0)
            
            if sources > 0 or quotes > 0:
                return min(sources * 8 + quotes * 10, 100)
        
        # Default score extraction
        return (self._safe_get(service_data, 'score', 0) or
                self._safe_get(service_data, 'credibility_score', 0) or
                self._safe_get(service_data, 'quality_score', 0) or
                self._safe_get(service_data, 'bias_score', 50))  # Bias defaults to 50
    
    def _generate_article_summary(self, article_data, detailed_analysis):
        """Generate comprehensive article summary"""
        
        # Try AI-enhanced summary first
        openai_data = detailed_analysis.get('openai_enhancer', {})
        if openai_data:
            ai_summary = openai_data.get('summary') or openai_data.get('ai_summary')
            if ai_summary:
                return ai_summary
        
        # Build summary from article data
        title = article_data.get('title', '')
        content = article_data.get('content', '')
        excerpt = article_data.get('excerpt', '')
        
        if content and len(content) > 100:
            # Extract meaningful preview
            preview = self._extract_preview(content, 200)
            if title:
                return f"{title}: {preview}"
            return preview
        elif excerpt:
            return excerpt
        elif title:
            return title
        else:
            return "Article content not available"
    
    def _generate_findings_summary(self, trust_score, source, detailed_analysis):
        """Generate comprehensive findings narrative"""
        
        # Determine trust level and recommendation
        if trust_score >= 80:
            level = "high credibility"
            rec = "This article can generally be trusted for accurate information."
        elif trust_score >= 60:
            level = "good credibility"
            rec = "This article is reasonably reliable but verify key claims."
        elif trust_score >= 40:
            level = "moderate credibility"
            rec = "Approach with caution and cross-reference important information."
        else:
            level = "low credibility"
            rec = "Significant concerns exist. Verify all claims through other sources."
        
        # Extract key findings for narrative
        strengths = []
        weaknesses = []
        
        # Analyze source credibility
        source_score = self._get_service_score(
            detailed_analysis.get('source_credibility', {}), 'source'
        )
        if source_score >= 70:
            strengths.append("reputable source")
        elif 0 < source_score < 40:
            weaknesses.append("questionable source credibility")
        
        # Analyze bias
        bias_score = self._get_service_score(
            detailed_analysis.get('bias_detector', {}), 'bias'
        )
        if bias_score >= 60:
            weaknesses.append("significant bias detected")
        elif bias_score <= 30:
            strengths.append("minimal bias")
        
        # Analyze fact checking
        fact_score = self._get_service_score(
            detailed_analysis.get('fact_checker', {}), 'fact_checker'
        )
        if fact_score >= 80:
            strengths.append("strong factual accuracy")
        elif 0 < fact_score < 50:
            weaknesses.append("factual accuracy concerns")
        
        # Analyze transparency
        trans_score = self._get_service_score(
            detailed_analysis.get('transparency_analyzer', {}), 'transparency'
        )
        if trans_score >= 70:
            strengths.append("good transparency")
        elif 0 < trans_score < 30:
            weaknesses.append("poor transparency")
        
        # Build narrative
        narrative = f"Analysis of {source} shows {level} (score: {trust_score}/100). "
        
        if strengths:
            narrative += f"Strengths include {', '.join(strengths)}. "
        
        if weaknesses:
            narrative += f"Concerns include {', '.join(weaknesses)}. "
        
        narrative += rec
        
        return narrative
    
    def _build_success_response(self, **kwargs):
        """Build successful analysis response"""
        response = {
            'success': True,
            'trust_score': kwargs['trust_score'],
            'article_summary': kwargs['article_summary'],
            'source': kwargs['article_data'].get('source') or kwargs['article_data'].get('domain', 'Unknown'),
            'author': kwargs['article_data'].get('author', 'Unknown'),
            'findings_summary': kwargs['findings_summary'],
            'detailed_analysis': kwargs['detailed_analysis'],
            'trust_level': self._get_trust_level(kwargs['trust_score']),
            'processing_time': time.time() - kwargs['start_time'],
            'extraction_quality': kwargs['extraction_quality']
        }
        
        # Add extraction note if partial
        if kwargs['extraction_quality'] == 'partial':
            response['extraction_note'] = 'Some services could not fully analyze this article. Scores are based on available data.'
        
        # Add article data for reference
        response['article'] = kwargs['article_data']
        
        # Add metadata
        response['timestamp'] = datetime.now().isoformat()
        response['services_analyzed'] = list(kwargs['detailed_analysis'].keys())
        
        return response
    
    def _error_response(self, error_type, message, start_time, article_data=None):
        """Build error response"""
        response = {
            'success': False,
            'error': error_type,
            'message': message,
            'trust_score': 0,
            'article_summary': article_data.get('title', 'Analysis failed') if article_data else 'Analysis failed',
            'source': article_data.get('source', 'Unknown') if article_data else 'Unknown',
            'author': article_data.get('author', 'Unknown') if article_data else 'Unknown',
            'findings_summary': message,
            'detailed_analysis': {},
            'processing_time': time.time() - start_time
        }
        return response
    
    def _get_trust_level(self, score):
        """Get trust level from score (matching app.py)"""
        if score >= 80:
            return 'Very High'
        elif score >= 60:
            return 'High'
        elif score >= 40:
            return 'Medium'
        elif score >= 20:
            return 'Low'
        else:
            return 'Very Low'
    
    def _extract_domain(self, url):
        """Extract domain from URL"""
        if not url:
            return 'Unknown'
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            return domain if domain else 'Unknown'
        except Exception as e:
            logger.warning(f"Error extracting domain: {e}")
            return 'Unknown'
    
    def _extract_preview(self, content, max_length=200):
        """Extract a meaningful preview from content"""
        if not content:
            return ''
        
        # Clean up whitespace
        content = ' '.join(content.split())
        
        if len(content) <= max_length:
            return content
        
        # Try to cut at sentence boundary
        preview = content[:max_length]
        last_period = preview.rfind('.')
        if last_period > max_length * 0.7:  # If period is reasonably far
            return preview[:last_period + 1]
        
        # Cut at word boundary
        last_space = preview.rfind(' ')
        if last_space > 0:
            return preview[:last_space] + '...'
        
        return preview + '...'
    
    def _safe_get(self, data, key, default=None):
        """Safely get value from dict or list"""
        if data is None:
            return default
            
        if isinstance(data, dict):
            return data.get(key, default)
            
        if isinstance(data, list):
            try:
                idx = int(key) if isinstance(key, str) and key.isdigit() else key
                if isinstance(idx, int) and 0 <= idx < len(data):
                    return data[idx]
            except (ValueError, TypeError, IndexError):
                pass
        
        return default
    
    def get_last_analysis(self):
        """Get the last analysis result (for debugging)"""
        return self._last_analysis
    
    def clear_cache(self):
        """Clear analysis cache"""
        self._cache = {}
        self._last_analysis = None
