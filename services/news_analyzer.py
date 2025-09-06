"""
News Analyzer Service - FIXED AUTHOR DATA EXTRACTION
Date: September 6, 2025
Last Updated: September 6, 2025

CRITICAL FIXES:
1. Properly extracts author_analyzer data from BaseAnalyzer wrapper
2. Passes combined_credibility_score to frontend
3. Includes author details in findings summary
4. Handles both wrapped and unwrapped service responses
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
    News analysis orchestrator with FIXED author data extraction
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
        Main analysis method with FIXED author data extraction
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
            
            # Build response with FIXED author data extraction
            response = self._build_frontend_response_fixed(pipeline_results, content)
            
            logger.info("Pipeline completed. Success: " + str(response.get('success', False)))
            logger.info(f"Pipeline keys: {list(response.keys())}")
            
            return response
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            return self._error_response(str(e), content, 'analysis_error')
    
    def _extract_author_data(self, author_result: Any) -> Dict[str, Any]:
        """
        Extract author data from various possible formats
        Handles BaseAnalyzer wrapper and direct results
        """
        if not author_result:
            return {}
        
        # If it's a BaseAnalyzer result wrapper
        if isinstance(author_result, dict):
            # Check if data is nested in 'data' field (BaseAnalyzer format)
            if 'data' in author_result and isinstance(author_result['data'], dict):
                data = author_result['data']
            else:
                # Direct format
                data = author_result
            
            # Extract all relevant author fields
            extracted = {}
            
            # Get credibility score (check multiple possible locations)
            for score_field in ['combined_credibility_score', 'credibility_score', 'score', 'author_score']:
                if score_field in data:
                    extracted['combined_credibility_score'] = data[score_field]
                    extracted['score'] = data[score_field]
                    break
            
            # Get author name
            for name_field in ['author_name', 'name', 'authors']:
                if name_field in data:
                    extracted['author_name'] = data[name_field]
                    extracted['name'] = data[name_field]
                    break
            
            # Get other fields
            field_mappings = {
                'position': ['position', 'title', 'role'],
                'organization': ['organization', 'company', 'employer'],
                'bio': ['bio', 'biography', 'description'],
                'verified': ['verified', 'is_verified', 'verification_status'],
                'expertise_areas': ['expertise_areas', 'expertise_domains', 'specialties'],
                'publication_history': ['publication_history', 'recent_articles', 'articles'],
                'awards': ['awards', 'awards_recognition', 'recognition'],
                'article_count': ['article_count', 'total_articles', 'publication_count'],
                'social_profiles': ['social_profiles', 'social_media', 'profiles'],
                'linkedin_profile': ['linkedin_profile', 'linkedin_url', 'linkedin'],
                'twitter_profile': ['twitter_profile', 'twitter_url', 'twitter'],
                'wikipedia_page': ['wikipedia_page', 'wikipedia_url', 'wikipedia']
            }
            
            for target_field, source_fields in field_mappings.items():
                for source_field in source_fields:
                    if source_field in data and data[source_field]:
                        extracted[target_field] = data[source_field]
                        break
            
            # Handle authors array if present
            if 'authors' in data and isinstance(data['authors'], list) and data['authors']:
                # If there's an authors array, extract data from first author
                first_author = data['authors'][0]
                if isinstance(first_author, dict):
                    for key, value in first_author.items():
                        if key not in extracted:
                            extracted[key] = value
            
            # Copy all original data as fallback
            for key, value in data.items():
                if key not in extracted:
                    extracted[key] = value
            
            logger.info(f"Extracted author data with score: {extracted.get('combined_credibility_score', 0)}")
            return extracted
        
        return {}
    
    def _build_frontend_response_fixed(self, pipeline_results: Dict[str, Any], content: str) -> Dict[str, Any]:
        """
        FIXED: Build response for frontend with proper author data extraction
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
        
        # CRITICAL FIX: Properly extract author_analyzer data
        if 'author_analyzer' in detailed_analysis:
            author_data = self._extract_author_data(detailed_analysis['author_analyzer'])
            # Replace the raw result with extracted data
            detailed_analysis['author_analyzer'] = author_data
            logger.info(f"Author analyzer data extracted: {list(author_data.keys())}")
        
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
        
        # Generate findings summary with author info
        findings_summary = self._generate_findings_summary_with_author(
            trust_score,
            detailed_analysis,
            article
        )
        
        # Build the response with CORRECT values
        response = {
            'success': True,
            'trust_score': trust_score,
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
        logger.info(f"Response built with trust_score={trust_score}, services={services_count}")
        if 'author_analyzer' in detailed_analysis:
            author_score = detailed_analysis['author_analyzer'].get('combined_credibility_score', 0)
            logger.info(f"Author credibility score in response: {author_score}")
        
        return response
    
    def _generate_findings_summary_with_author(self, trust_score: int, detailed_analysis: Dict, article: Dict) -> str:
        """Generate comprehensive findings summary including author credibility"""
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
        
        # Add author credibility info
        author = article.get('author', '')
        if author and author != 'Unknown':
            if 'author_analyzer' in detailed_analysis:
                author_data = detailed_analysis['author_analyzer']
                author_score = author_data.get('combined_credibility_score', 0) or author_data.get('score', 0)
                if author_score > 0:
                    if author_score >= 70:
                        findings.append(f"Author {author} has high credibility (score: {author_score}/100).")
                    elif author_score >= 50:
                        findings.append(f"Author {author} has moderate credibility (score: {author_score}/100).")
                    else:
                        findings.append(f"Author {author} has limited verified credibility (score: {author_score}/100).")
                else:
                    findings.append(f"Written by {author}.")
            else:
                findings.append(f"Written by {author}.")
        
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
