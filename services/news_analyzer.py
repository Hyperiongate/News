"""
Enhanced NewsAnalyzer with Adaptive Scoring and Paywall Detection
COMPLETE VERSION - Includes all original functionality plus fixes:
1. Adaptive scoring for missing services (author extraction failures)
2. Paywall detection with user guidance
3. Article and findings summary generation
4. No dummy data analysis - fail gracefully instead
"""

import logging
import time
from typing import Dict, Any, Optional, List
import re
import json
import traceback

logger = logging.getLogger(__name__)

class NewsAnalyzer:
    """Enhanced news analyzer with adaptive scoring and better error handling"""
    
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
    
    def __init__(self, config=None):
        self.config = config or {}
        self.pipeline = None  # Will be injected
        self.article_extractor = None  # Will be injected
        self.openai_enhancer = None  # Will be injected
        logger.info("NewsAnalyzer initialized")
        
    def analyze(self, url: str = None, text: str = None) -> Dict[str, Any]:
        """
        Main analysis method with enhanced error handling and adaptive scoring
        """
        start_time = time.time()
        logger.info("=" * 80)
        logger.info(f"STARTING ENHANCED ANALYSIS - URL: {bool(url)}, Text: {bool(text)}")
        logger.info("=" * 80)
        
        # Step 1: Extract article content
        if url:
            extraction_result = self._extract_article_from_url(url)
            
            # Check for paywall or extraction failure
            if not extraction_result['success']:
                if extraction_result.get('paywall_detected'):
                    logger.info(f"Paywall detected for {extraction_result.get('domain', 'unknown')}")
                    return {
                        'success': False,
                        'error': 'paywall_detected',
                        'message': 'This site requires a subscription. Please copy and paste the article text into the text box below for analysis.',
                        'source': extraction_result.get('domain', 'Unknown'),
                        'trust_score': None,
                        'processing_time': time.time() - start_time
                    }
                else:
                    logger.error(f"Extraction failed: {extraction_result.get('error', 'Unknown error')}")
                    return {
                        'success': False,
                        'error': 'extraction_failed',
                        'message': 'Unable to extract article content. Please copy and paste the article text for analysis.',
                        'trust_score': None,
                        'processing_time': time.time() - start_time
                    }
            
            article_data = extraction_result
            
        elif text:
            # Direct text input - create article data structure
            article_data = self._create_article_from_text(text)
        else:
            return {
                'success': False,
                'error': 'no_input',
                'message': 'Please provide either a URL or article text',
                'trust_score': None
            }
        
        # Step 2: Run analysis pipeline with quality check
        try:
            pipeline_results = self.pipeline.analyze(article_data) if self.pipeline else {}
            
            # Step 3: Assess extraction quality
            extraction_quality = self._assess_extraction_quality(article_data, pipeline_results)
            
            if extraction_quality == 'failed':
                logger.warning("Extraction quality too poor for analysis")
                return {
                    'success': False,
                    'error': 'insufficient_data',
                    'message': 'Unable to extract enough content for meaningful analysis. Please copy and paste the full article text.',
                    'trust_score': None,
                    'processing_time': time.time() - start_time
                }
            
            # Step 4: Normalize pipeline results (from original)
            normalized_results = self._normalize_pipeline_results(pipeline_results)
            
            # Step 5: Calculate trust score with adaptive weights if needed
            trust_score = self._calculate_adaptive_trust_score(
                normalized_results.get('detailed_analysis', {}),
                extraction_quality
            )
            
            # Step 6: Generate summaries
            summaries = self._generate_summaries(article_data, normalized_results, trust_score)
            
            # Step 7: Build response
            response = self._build_frontend_response(
                article_data, 
                normalized_results, 
                trust_score,
                summaries,
                extraction_quality
            )
            
            response['processing_time'] = time.time() - start_time
            logger.info(f"Analysis completed in {response['processing_time']:.2f}s")
            
            return response
            
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'analysis_failed',
                'message': f'Analysis error: {str(e)}',
                'trust_score': None,
                'processing_time': time.time() - start_time
            }
    
    def _extract_article_from_url(self, url: str) -> Dict[str, Any]:
        """
        Extract article with paywall detection
        """
        try:
            if self.article_extractor:
                result = self.article_extractor.extract(url)
                
                # Check for paywall indicators
                if self._detect_paywall(result):
                    return {
                        'success': False,
                        'paywall_detected': True,
                        'domain': self._extract_domain(url)
                    }
                
                # Check for sufficient content
                if not result.get('content') or len(result.get('content', '')) < 100:
                    return {
                        'success': False,
                        'error': 'insufficient_content',
                        'domain': self._extract_domain(url)
                    }
                
                return result
            else:
                # Fallback if no extractor
                return {
                    'success': False,
                    'error': 'no_extractor'
                }
                
        except Exception as e:
            logger.error(f"Extraction error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _detect_paywall(self, extraction_result: Dict) -> bool:
        """
        Detect if content is behind a paywall
        """
        # Check for paywall indicators
        paywall_markers = [
            'subscription required',
            'subscribe to read',
            'paywall',
            'please log in',
            'member-only content',
            'exclusive for subscribers',
            'sign up to continue reading',
            'subscribers only'
        ]
        
        content = (extraction_result.get('content', '') + 
                  extraction_result.get('title', '')).lower()
        
        # Check for very short content with paywall keywords
        if len(content) < 500:
            for marker in paywall_markers:
                if marker in content:
                    return True
        
        # Check if we got minimal extraction (title but no real content)
        if extraction_result.get('title') and len(extraction_result.get('content', '')) < 200:
            return True
            
        return False
    
    def _assess_extraction_quality(self, article_data: Dict, pipeline_results: Dict) -> str:
        """
        Assess the quality of extraction to determine scoring approach
        Returns: 'full', 'partial', or 'failed'
        """
        detailed = pipeline_results.get('detailed_analysis', {})
        
        # Count successful service extractions
        successful_services = 0
        total_services = len(self.STANDARD_WEIGHTS)
        
        for service_name in self.STANDARD_WEIGHTS.keys():
            service_data = detailed.get(service_name, {})
            # Use _safe_get for nested data
            score = self._safe_get(service_data, 'score', 0)
            if score > 0:
                successful_services += 1
        
        # Check critical data
        has_content = bool(article_data.get('content')) and len(article_data.get('content', '')) > 200
        has_title = bool(article_data.get('title'))
        has_source = bool(article_data.get('source') or article_data.get('domain'))
        
        # Determine quality level
        if successful_services >= total_services - 1 and has_content and has_title:
            return 'full'
        elif successful_services >= 3 and has_content:
            return 'partial'
        else:
            return 'failed'
    
    def _normalize_pipeline_results(self, pipeline_results: Dict) -> Dict[str, Any]:
        """
        Normalize pipeline results to handle various data formats (FROM ORIGINAL)
        """
        normalized = {
            'success': pipeline_results.get('success', True),
            'detailed_analysis': {}
        }
        
        detailed = pipeline_results.get('detailed_analysis', {})
        
        for service_name, service_data in detailed.items():
            if service_data is None:
                normalized['detailed_analysis'][service_name] = {}
                continue
            
            # Handle different data types
            if isinstance(service_data, (int, float)):
                normalized['detailed_analysis'][service_name] = {'score': service_data}
            elif isinstance(service_data, str):
                normalized['detailed_analysis'][service_name] = {'result': service_data}
            elif isinstance(service_data, list):
                normalized['detailed_analysis'][service_name] = {'findings': service_data}
            elif isinstance(service_data, dict):
                normalized['detailed_analysis'][service_name] = service_data
            else:
                normalized['detailed_analysis'][service_name] = {'data': str(service_data)}
        
        return normalized
    
    def _calculate_adaptive_trust_score(self, detailed_analysis: Dict, extraction_quality: str) -> float:
        """
        Calculate trust score with adaptive weights based on extraction quality
        """
        # Check if author extraction failed
        author_data = detailed_analysis.get('author_analyzer', {})
        author_score = self._safe_get(author_data, 'score', 0) or self._safe_get(author_data, 'credibility_score', 0)
        
        # Check source credibility
        source_data = detailed_analysis.get('source_credibility', {})
        source_score = self._safe_get(source_data, 'score', 0) or self._safe_get(source_data, 'credibility_score', 0)
        
        # Determine which weights to use
        if author_score == 0 and source_score >= 70:
            # Reputable source with missing author - use adaptive weights
            logger.info(f"Using adaptive weights - reputable source ({source_score}) with no author data")
            weights = self.ADAPTIVE_WEIGHTS_NO_AUTHOR
            skip_author = True
        else:
            # Use standard weights
            weights = self.STANDARD_WEIGHTS
            skip_author = False
        
        # Calculate weighted score
        total_score = 0
        total_weight = 0
        
        for service_name, weight in weights.items():
            if skip_author and service_name == 'author_analyzer':
                continue
                
            service_data = detailed_analysis.get(service_name, {})
            
            # Get service score with special handling
            if service_name == 'bias_detector':
                # Convert bias to objectivity
                bias_score = self._safe_get(service_data, 'bias_score', 50) or self._safe_get(service_data, 'score', 50)
                service_score = 100 - bias_score
            elif service_name == 'fact_checker':
                # Calculate from claims if available
                service_score = self._calculate_fact_check_score(service_data)
            elif service_name == 'transparency_analyzer':
                # Calculate from sources/quotes if available
                service_score = self._calculate_transparency_score(service_data)
            elif service_name == 'manipulation_detector':
                # Invert manipulation score
                manip_score = self._safe_get(service_data, 'score', 0) or self._safe_get(service_data, 'manipulation_score', 0)
                service_score = 100 - manip_score
            else:
                # Standard score extraction
                service_score = self._safe_get(service_data, 'score', 0) or \
                               self._safe_get(service_data, 'credibility_score', 0) or \
                               self._safe_get(service_data, 'quality_score', 0)
            
            total_score += service_score * weight
            total_weight += weight
        
        # Normalize if we skipped services
        if total_weight > 0 and total_weight < 1:
            total_score = total_score / total_weight * 100
        
        # Round to integer
        final_score = round(min(max(total_score, 0), 100))
        
        logger.info(f"Trust score calculated: {final_score} (extraction_quality: {extraction_quality}, adaptive: {skip_author})")
        
        return final_score
    
    def _calculate_fact_check_score(self, data: Dict) -> float:
        """Calculate fact checking score from claims data"""
        claims_found = self._safe_get(data, 'claims_found', 0) or self._safe_get(data, 'claims_analyzed', 0)
        claims_verified = self._safe_get(data, 'claims_verified', 0)
        
        if claims_found > 0:
            return (claims_verified / claims_found) * 100
        
        return self._safe_get(data, 'score', 50)
    
    def _calculate_transparency_score(self, data: Dict) -> float:
        """Calculate transparency score from sources and quotes"""
        sources = self._safe_get(data, 'source_count', 0) or self._safe_get(data, 'sources_cited', 0)
        quotes = self._safe_get(data, 'quote_count', 0) or self._safe_get(data, 'quotes_used', 0)
        
        if sources > 0 or quotes > 0:
            source_score = min(sources * 8, 50)
            quote_score = min(quotes * 10, 50)
            return min(source_score + quote_score, 100)
        
        return self._safe_get(data, 'score', 0) or self._safe_get(data, 'transparency_score', 0)
    
    def _generate_summaries(self, article_data: Dict, pipeline_results: Dict, trust_score: float) -> Dict[str, str]:
        """
        Generate article summary and findings summary
        """
        summaries = {}
        
        # Article Summary - what the article is about
        if article_data.get('content'):
            # Try OpenAI if available
            if self.openai_enhancer:
                try:
                    openai_data = pipeline_results.get('detailed_analysis', {}).get('openai_enhancer', {})
                    if openai_data and openai_data.get('summary'):
                        summaries['article_summary'] = openai_data['summary']
                    else:
                        # Generate new summary
                        ai_summary = self.openai_enhancer.generate_summary(
                            article_data['content'][:2000]
                        )
                        summaries['article_summary'] = ai_summary
                except Exception as e:
                    logger.warning(f"OpenAI summary generation failed: {e}")
            
            # Fallback to simple extraction
            if 'article_summary' not in summaries:
                # Use first 200 chars of content or description
                content_preview = article_data.get('content', '')[:200].strip()
                title = article_data.get('title', 'Article')
                if content_preview:
                    summaries['article_summary'] = f"{title}: {content_preview}..."
                else:
                    summaries['article_summary'] = title
        else:
            summaries['article_summary'] = article_data.get('title', 'Unable to extract article summary')
        
        # Findings Summary - what we found
        summaries['findings_summary'] = self._generate_findings_narrative(
            pipeline_results.get('detailed_analysis', {}),
            trust_score,
            article_data
        )
        
        return summaries
    
    def _generate_findings_narrative(self, detailed_analysis: Dict, trust_score: float, article_data: Dict) -> str:
        """
        Generate a narrative summary of what we found
        """
        source = article_data.get('source') or article_data.get('domain', 'this source')
        
        # Determine trust level
        if trust_score >= 80:
            trust_level = "high credibility"
            recommendation = "This article can generally be trusted for accurate information."
        elif trust_score >= 60:
            trust_level = "good credibility"
            recommendation = "This article is reasonably reliable but verify key claims."
        elif trust_score >= 40:
            trust_level = "moderate credibility"
            recommendation = "Approach with caution and cross-reference important information."
        else:
            trust_level = "low credibility"
            recommendation = "Significant concerns exist. Verify all claims through other sources."
        
        # Extract key findings
        strengths = []
        weaknesses = []
        
        # Source credibility
        source_data = detailed_analysis.get('source_credibility', {})
        source_score = self._safe_get(source_data, 'score', 0)
        if source_score >= 70:
            strengths.append("reputable source")
        elif source_score < 40 and source_score > 0:
            weaknesses.append("questionable source credibility")
        
        # Bias
        bias_data = detailed_analysis.get('bias_detector', {})
        bias_score = self._safe_get(bias_data, 'bias_score', 50) or self._safe_get(bias_data, 'score', 50)
        if bias_score >= 60:
            weaknesses.append("significant bias detected")
        elif bias_score <= 30:
            strengths.append("minimal bias")
        
        # Fact checking
        fact_data = detailed_analysis.get('fact_checker', {})
        fact_score = self._calculate_fact_check_score(fact_data)
        if fact_score >= 80:
            strengths.append("strong factual accuracy")
        elif fact_score < 50 and fact_score > 0:
            weaknesses.append("factual concerns")
        
        # Build narrative
        narrative = f"Analysis of {source} shows {trust_level} (score: {trust_score}/100). "
        
        if strengths:
            narrative += f"Strengths include {', '.join(strengths)}. "
        
        if weaknesses:
            narrative += f"Concerns include {', '.join(weaknesses)}. "
        
        narrative += recommendation
        
        return narrative
    
    def _build_frontend_response(self, article_data: Dict, pipeline_results: Dict, 
                                 trust_score: float, summaries: Dict, 
                                 extraction_quality: str) -> Dict[str, Any]:
        """
        Build the response for the frontend with all required fields
        """
        response = {
            'success': True,
            'trust_score': trust_score,
            'extraction_quality': extraction_quality,
            
            # Article info
            'article_summary': summaries.get('article_summary', ''),
            'source': article_data.get('source') or article_data.get('domain', 'Unknown'),
            'author': article_data.get('author', 'Unknown'),
            'findings_summary': summaries.get('findings_summary', ''),
            
            # Trust level
            'trust_level': self._get_trust_level(trust_score),
            
            # Detailed analysis from pipeline
            'detailed_analysis': pipeline_results.get('detailed_analysis', {}),
            
            # Analysis metadata
            'analysis': {
                'trust_score': trust_score,
                'trust_level': self._get_trust_level(trust_score),
                'summary': summaries.get('findings_summary', '')
            },
            
            # Article data
            'article': {
                'title': article_data.get('title', ''),
                'content': article_data.get('content', ''),
                'url': article_data.get('url', ''),
                'source': article_data.get('source', ''),
                'domain': article_data.get('domain', ''),
                'author': article_data.get('author', ''),
                'published_date': article_data.get('published_date', ''),
                'excerpt': article_data.get('excerpt', '') or article_data.get('content', '')[:500]
            }
        }
        
        # Add extraction quality indicator if partial
        if extraction_quality == 'partial':
            response['extraction_note'] = 'Some services could not analyze this article fully. Scores are based on available data.'
        
        # Add any additional metadata
        response['services_available'] = self._count_available_services(pipeline_results)
        response['errors'] = pipeline_results.get('errors', [])
        
        return response
    
    def _get_trust_level(self, score: float) -> str:
        """Get trust level label from score"""
        if score >= 80:
            return 'Highly Trustworthy'
        elif score >= 60:
            return 'Generally Trustworthy'
        elif score >= 40:
            return 'Moderate Trust'
        else:
            return 'Low Trustworthiness'
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            return domain
        except:
            return 'Unknown'
    
    def _create_article_from_text(self, text: str) -> Dict[str, Any]:
        """Create article data structure from raw text input"""
        # Try to extract title (first line or first sentence)
        lines = text.strip().split('\n')
        title = lines[0][:200] if lines else 'Untitled Article'
        
        # Remove title from content
        content = '\n'.join(lines[1:]) if len(lines) > 1 else text
        
        return {
            'success': True,
            'title': title.strip(),
            'content': content.strip(),
            'source': 'Text Input',
            'domain': 'User Provided',
            'author': 'Unknown',
            'url': '',
            'published_date': '',
            'excerpt': content[:500] if content else ''
        }
    
    def _safe_get(self, data: Any, key: str, default: Any = None) -> Any:
        """
        Safely get value from dict or return default (FROM ORIGINAL)
        Handles both dict access and list indexing
        """
        if data is None:
            return default
        
        if isinstance(data, dict):
            return data.get(key, default)
        elif isinstance(data, list):
            try:
                idx = int(key) if isinstance(key, str) and key.isdigit() else key
                if isinstance(idx, int) and 0 <= idx < len(data):
                    return data[idx]
            except (ValueError, TypeError, IndexError):
                pass
        
        return default
    
    def _extract_findings(self, service_data: Dict) -> List[str]:
        """
        Extract findings from service data (FROM ORIGINAL)
        """
        findings = []
        
        # Check various possible locations for findings
        if isinstance(service_data, dict):
            # Direct findings field
            if 'findings' in service_data:
                f = service_data['findings']
                if isinstance(f, list):
                    findings.extend(f)
                elif isinstance(f, str):
                    findings.append(f)
            
            # Issues field
            if 'issues' in service_data:
                issues = service_data['issues']
                if isinstance(issues, list):
                    findings.extend(issues)
            
            # Strengths and weaknesses
            if 'strengths' in service_data:
                strengths = service_data['strengths']
                if isinstance(strengths, list):
                    findings.extend([f"Strength: {s}" for s in strengths])
            
            if 'weaknesses' in service_data:
                weaknesses = service_data['weaknesses']
                if isinstance(weaknesses, list):
                    findings.extend([f"Weakness: {w}" for w in weaknesses])
        
        return findings
    
    def _count_available_services(self, pipeline_results: Dict) -> int:
        """Count how many services returned valid results"""
        count = 0
        detailed = pipeline_results.get('detailed_analysis', {})
        
        for service_name, service_data in detailed.items():
            if service_data and isinstance(service_data, dict):
                # Check if service has meaningful data
                if service_data.get('score') is not None or \
                   service_data.get('findings') or \
                   service_data.get('result'):
                    count += 1
        
        return count
