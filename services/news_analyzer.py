"""
News Analyzer Service - FIXED VERSION
Properly handles short content without incorrectly flagging as insufficient
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
    News analysis orchestrator with fixed content validation
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
            
            # Cache for last analysis
            self._last_analysis = None
            
        except Exception as e:
            logger.error(f"NewsAnalyzer initialization failed: {str(e)}", exc_info=True)
            self.pipeline = None
            self.service_registry = None
    
    def analyze(self, content: str, content_type: str = 'url', pro_mode: bool = False) -> Dict[str, Any]:
        """
        Main analysis method with fixed content validation
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
            
            # Normalize pipeline results
            pipeline_results = self._normalize_pipeline_results(pipeline_results)
            
            # Build response
            response = self._build_frontend_response(pipeline_results, content)
            
            logger.info("Pipeline completed. Success: " + str(response.get('success', False)))
            logger.info(f"Pipeline keys: {list(response.keys())}")
            
            return response
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            return self._error_response(str(e), content, 'analysis_error')
    
    def _normalize_pipeline_results(self, results: Any) -> Dict[str, Any]:
        """Normalize pipeline results to ensure it's always a proper dict"""
        if results is None:
            return {}
        if isinstance(results, dict):
            return results
        if isinstance(results, list):
            return {'services': results}
        return {'result': str(results)}
    
    def _build_frontend_response(self, pipeline_results: Dict[str, Any], content: str) -> Dict[str, Any]:
        """Build response for frontend with fixed content validation"""
        start_time = time.time()
        
        # Check for pipeline success/failure
        if not pipeline_results.get('success', False):
            error_msg = pipeline_results.get('error', 'Analysis failed')
            
            # CRITICAL FIX: Check if this is really insufficient content or just an extraction issue
            if error_msg == 'insufficient_content':
                # Get what we actually extracted
                article = pipeline_results.get('article', {})
                text = article.get('text', '') or article.get('content', '')
                word_count = article.get('word_count', 0)
                
                # FIXED: More reasonable thresholds for short articles
                # Some news updates are legitimately short (50-200 words)
                if word_count > 10 or len(text) > 50:
                    # We have SOME content, proceed with analysis
                    logger.info(f"Proceeding with short content: {word_count} words, {len(text)} chars")
                else:
                    # Really insufficient content
                    return self._build_error_response(error_msg, content, start_time)
            else:
                # Other error
                return self._build_error_response(error_msg, content, start_time)
        
        # Extract article data
        article = pipeline_results.get('article', {})
        
        # Handle both 'text' and 'content' fields
        article_content = article.get('text', '') or article.get('content', '')
        
        # Extract service results
        detailed_analysis = {}
        for service_name in self.STANDARD_WEIGHTS.keys():
            if service_name in pipeline_results:
                service_data = pipeline_results[service_name]
                if service_data and isinstance(service_data, dict):
                    detailed_analysis[service_name] = self._normalize_service_data(service_data)
        
        # Calculate trust score
        trust_score = self._calculate_trust_score(detailed_analysis)
        
        # Assess extraction quality with FIXED thresholds
        extraction_quality = self._assess_extraction_quality(
            article, 
            detailed_analysis,
            pipeline_results
        )
        
        # Build article summary
        article_summary = self._build_article_summary(article)
        
        # Build findings summary
        findings_summary = self._build_findings_summary(
            trust_score,
            article.get('domain', 'Unknown'),
            detailed_analysis,
            extraction_quality
        )
        
        # Return complete response
        return {
            'success': True,
            'trust_score': trust_score,
            'article_summary': article_summary,
            'source': article.get('domain', 'Unknown'),
            'author': article.get('author', 'Unknown'),
            'findings_summary': findings_summary,
            'detailed_analysis': detailed_analysis,
            'processing_time': time.time() - start_time,
            'extraction_quality': extraction_quality,
            'message': pipeline_results.get('message', '')
        }
    
    def _assess_extraction_quality(self, article: Dict, detailed_analysis: Dict, pipeline_results: Dict) -> str:
        """
        FIXED: Assess extraction quality with reasonable thresholds
        """
        # Count services that ran
        successful_services = len(detailed_analysis)
        
        # Get content and word count
        content = article.get('text', '') or article.get('content', '')
        word_count = article.get('word_count', 0)
        
        # FIXED: Lower thresholds for legitimate short content
        # Many news updates are 50-200 words
        has_minimal_content = (len(content) > 30) or (word_count > 5)
        has_title = bool(article.get('title'))
        has_source = bool(article.get('domain') or article.get('source'))
        
        logger.info(f"Extraction quality: {successful_services}/{len(self.STANDARD_WEIGHTS)} services, "
                   f"content={len(content)} chars, word_count={word_count}, "
                   f"title={has_title}, source={has_source}")
        
        # Determine quality level with FIXED logic
        if successful_services >= 5 and has_minimal_content and has_title:
            return 'full'
        elif successful_services >= 3 and has_minimal_content:
            return 'partial'
        elif successful_services >= 1 and (has_minimal_content or has_title):
            return 'minimal'  # New level for short but valid content
        else:
            return 'failed'
    
    def _calculate_trust_score(self, detailed_analysis: Dict) -> int:
        """Calculate weighted trust score"""
        if not detailed_analysis:
            return 0
        
        total_score = 0
        total_weight = 0
        
        for service_name, weight in self.STANDARD_WEIGHTS.items():
            if service_name in detailed_analysis:
                service_data = detailed_analysis[service_name]
                score = self._extract_service_score(service_name, service_data)
                
                if score is not None:
                    # Apply inverse logic for bias and manipulation
                    if service_name in ['bias_detector', 'manipulation_detector']:
                        score = 100 - score
                    
                    logger.info(f"Trust component {service_name}: {score} (weight: {weight})")
                    total_score += score * weight
                    total_weight += weight
        
        if total_weight > 0:
            final_score = int(total_score / total_weight)
            logger.info(f"Final trust score: {final_score} (from {len(detailed_analysis)} services)")
            return final_score
        
        return 0
    
    def _extract_service_score(self, service_name: str, service_data: Any) -> Optional[int]:
        """Extract score from service data"""
        if service_data is None:
            return None
        
        # Direct score
        if isinstance(service_data, (int, float)):
            return int(service_data)
        
        if not isinstance(service_data, dict):
            return None
        
        # Special handling for specific services FIRST
        if service_name == 'fact_checker':
            # FIXED: Always calculate from claims ratio when available
            checks = service_data.get('claims_checked', 0)
            verified = service_data.get('verified_claims', 0)
            if checks > 0:
                return int((verified / checks) * 100)
            # Only use the score field if no claims data available
            if 'score' in service_data:
                return int(service_data['score'])
        
        elif service_name == 'source_credibility':
            rating = service_data.get('rating', '')
            ratings_map = {
                'Very High': 90,
                'High': 70,
                'Medium': 50,
                'Low': 30,
                'Very Low': 10
            }
            if rating in ratings_map:
                return ratings_map[rating]
        
        # Generic score extraction for other services
        score_keys = ['score', 'trust_score', 'credibility_score', 'overall_score', 'final_score']
        
        for key in score_keys:
            if key in service_data:
                value = service_data[key]
                if isinstance(value, (int, float)):
                    return int(value)
        
        return None
    
    def _normalize_service_data(self, service_data: Any) -> Dict:
        """Normalize service data to consistent format"""
        if service_data is None:
            return {}
        
        if isinstance(service_data, dict):
            return service_data
        
        if isinstance(service_data, (int, float)):
            return {'score': int(service_data)}
        
        if isinstance(service_data, str):
            return {'result': service_data}
        
        if isinstance(service_data, list):
            return {'findings': service_data}
        
        return {'data': str(service_data)}
    
    def _build_article_summary(self, article: Dict) -> str:
        """Build article summary"""
        title = article.get('title', '')
        content = article.get('text', '') or article.get('content', '')
        word_count = article.get('word_count', 0)
        
        if title and len(title) > 10:
            summary = title
        elif content:
            # Take first 200 chars or first sentence
            summary = content[:200].strip()
            if '.' in summary:
                summary = summary[:summary.index('.')+1]
        else:
            summary = 'Article content not available'
        
        # Add word count if available
        if word_count > 0:
            summary += f" ({word_count} words)"
        
        return summary
    
    def _build_findings_summary(self, trust_score: int, source: str, detailed_analysis: Dict, quality: str) -> str:
        """Build findings summary"""
        findings = []
        
        # Trust level
        trust_level = self._get_trust_level(trust_score)
        findings.append(f"Trust Score: {trust_score}/100 ({trust_level})")
        
        # Source
        if source and source != 'Unknown':
            findings.append(f"Source: {source}")
        
        # Key findings from services
        if 'bias_detector' in detailed_analysis:
            bias_data = detailed_analysis['bias_detector']
            bias_score = self._extract_service_score('bias_detector', bias_data)
            if bias_score is not None:
                bias_level = self._get_bias_level(bias_score)
                findings.append(f"Bias: {bias_level}")
        
        if 'fact_checker' in detailed_analysis:
            fact_data = detailed_analysis['fact_checker']
            fact_score = self._extract_service_score('fact_checker', fact_data)
            if fact_score is not None:
                findings.append(f"Fact Check: {fact_score}% verified")
        
        # Quality note for short content
        if quality == 'minimal':
            findings.append("Note: Limited content available for full analysis")
        elif quality == 'partial':
            findings.append("Partial analysis completed")
        
        return " | ".join(findings) if findings else "Analysis completed."
    
    def _get_trust_level(self, score: int) -> str:
        """Get trust level from score"""
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
    
    def _get_bias_level(self, score: int) -> str:
        """Get bias level from score"""
        if score <= 20:
            return 'Minimal'
        elif score <= 40:
            return 'Low'
        elif score <= 60:
            return 'Moderate'
        elif score <= 80:
            return 'High'
        else:
            return 'Extreme'
    
    def _build_error_response(self, error_msg: str, content: str, start_time: float) -> Dict:
        """Build error response"""
        return {
            'success': False,
            'error': error_msg,
            'message': error_msg,
            'trust_score': 0,
            'article_summary': 'Analysis failed',
            'source': 'Unknown',
            'author': 'Unknown',
            'findings_summary': f'Analysis failed: {error_msg}',
            'detailed_analysis': {},
            'processing_time': time.time() - start_time
        }
    
    def _error_response(self, error: str, content: str, error_type: str) -> Dict:
        """Build error response (backward compatible)"""
        return {
            'success': False,
            'error': error_type,
            'message': error,
            'trust_score': 0,
            'article_summary': 'Analysis failed',
            'source': 'Unknown',
            'author': 'Unknown',
            'findings_summary': f'Analysis failed: {error}',
            'detailed_analysis': {},
            'processing_time': 0
        }
    
    def get_available_services(self) -> List[str]:
        """Get list of available services"""
        if not self.service_registry:
            return []
        
        status = self.service_registry.get_service_status()
        return [name for name, info in status.get('services', {}).items() 
                if info.get('available', False)]
    
    def get_last_analysis(self) -> Optional[Dict]:
        """Get the last analysis result (for debugging)"""
        return self._last_analysis
    
    def clear_cache(self):
        """Clear any cached data"""
        self._last_analysis = None
        logger.info("Cache cleared")
