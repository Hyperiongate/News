"""
News Analyzer Service - WITH INSIGHT GENERATION
Date: October 6, 2025
Version: 12.2

CHANGES FROM 12.1:
- Added InsightGenerator integration
- Added DataEnricher integration
- Preserves ALL existing functionality
- Adds executive insights to response
- Adds comparative context to all services

DEPLOYMENT:
Replace services/news_analyzer.py with this file
"""

import logging
import time
from typing import Dict, Any, Optional

from services.analysis_pipeline import AnalysisPipeline
from services.insight_generator import InsightGenerator
from services.data_enricher import DataEnricher

logger = logging.getLogger(__name__)


class NewsAnalyzer:
    """
    Clean orchestrator for news analysis with proper data formatting
    """
    
    def __init__(self):
        """Initialize with pipeline and enhancement services"""
        self.pipeline = AnalysisPipeline()
        self.insight_generator = InsightGenerator()
        self.data_enricher = DataEnricher()
        logger.info("[NewsAnalyzer v12.2] Initialized with insights & enrichment")
    
    def analyze(self, content: str, content_type: str = 'url', pro_mode: bool = False) -> Dict[str, Any]:
        """
        Main analysis method - clean and simple
        
        Args:
            content: URL or text to analyze
            content_type: 'url' or 'text'
            pro_mode: Not used (for compatibility)
            
        Returns:
            Properly formatted analysis results with insights
        """
        
        analysis_start = time.time()
        
        try:
            # Validate inputs
            if not content:
                return self._create_error_response("No content provided")
            
            # Prepare data for pipeline
            data = {}
            if content_type == 'url':
                data['url'] = content.strip()
            else:
                data['text'] = content
            
            logger.info("=" * 80)
            logger.info("[NewsAnalyzer] Starting Analysis")
            logger.info(f"Type: {content_type}")
            logger.info(f"Content length: {len(content)}")
            
            # Run pipeline
            pipeline_results = self.pipeline.analyze(data)
            
            # Check if pipeline succeeded
            if not pipeline_results.get('success'):
                return self._create_error_response(
                    pipeline_results.get('error', 'Analysis failed')
                )
            
            # Build response with properly formatted data
            response = self._build_response(
                pipeline_results,
                content,
                content_type,
                analysis_start
            )
            
            # ===== ENHANCEMENT PHASE =====
            try:
                logger.info("[NewsAnalyzer] Generating executive insights...")
                insights = self.insight_generator.generate_insights(response)
                response['insights'] = insights
                
                logger.info("[NewsAnalyzer] Enriching data with comparative context...")
                response = self.data_enricher.enrich_data(response)
                
                logger.info("[NewsAnalyzer] ✓ Insights and enrichment complete")
            except Exception as e:
                logger.error(f"[NewsAnalyzer] Enhancement error (continuing): {e}")
                # Continue without enhancements if there's an error
            # ===== END ENHANCEMENT PHASE =====
            
            logger.info(f"[NewsAnalyzer] Complete - Trust Score: {response['trust_score']}")
            logger.info("=" * 80)
            
            return response
            
        except Exception as e:
            logger.error(f"[NewsAnalyzer] Error: {e}")
            return self._create_error_response(str(e))
    
    def _build_response(
        self,
        pipeline_results: Dict[str, Any],
        original_content: str,
        content_type: str,
        start_time: float
    ) -> Dict[str, Any]:
        """Build clean, properly formatted response"""
        
        # Extract article data
        article = pipeline_results.get('article', {})
        
        # Extract trust score
        trust_score = pipeline_results.get('trust_score', 0)
        
        # Process and flatten service results
        detailed_analysis = self._process_service_results(
            pipeline_results.get('detailed_analysis', {})
        )
        
        # Generate findings summary
        findings = self._generate_findings(trust_score, detailed_analysis)
        
        # Build response
        return {
            'success': True,
            'trust_score': trust_score,
            'article_summary': article.get('title', 'Article analyzed'),
            'source': article.get('source', article.get('domain', 'Unknown')),
            'author': article.get('author', 'Unknown'),
            'findings_summary': findings,
            'detailed_analysis': detailed_analysis,
            'article_metadata': {
                'url': article.get('url', ''),
                'word_count': article.get('word_count', 0),
                'extraction_method': article.get('extraction_method', 'unknown')
            },
            'processing_time': round(time.time() - start_time, 2),
            'services_used': pipeline_results.get('services_used', 0)
        }
    
    def _process_service_results(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """Process and ensure proper structure for each service"""
        
        processed = {}
        
        for service_name, service_data in raw_results.items():
            if not service_data:
                continue
            
            # Ensure each service has required fields
            processed_data = self._ensure_service_fields(service_name, service_data)
            processed[service_name] = processed_data
        
        return processed
    
    def _ensure_service_fields(self, service_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure service data has all required fields for frontend
        
        CRITICAL: This method ADDS missing required fields but PRESERVES all existing fields
        """
        
        # Start with ALL the data we have - don't filter anything out!
        result = data.copy()
        
        # Ensure score exists
        if 'score' not in result:
            result['score'] = 50
        
        # Service-specific REQUIRED field defaults (only add if missing)
        if service_name == 'source_credibility':
            result.setdefault('organization', result.get('source', 'Unknown'))
            result.setdefault('founded', 2000)
            result.setdefault('credibility', 'Medium')
            result.setdefault('bias', 'Moderate')
            
        elif service_name == 'bias_detector':
            result.setdefault('bias_score', result.get('score', 50))
            result.setdefault('direction', 'center')
            result.setdefault('political_lean', result.get('direction', 'center'))
            
        elif service_name == 'fact_checker':
            result.setdefault('accuracy_score', result.get('score', 50))
            result.setdefault('claims_checked', 0)
            result.setdefault('claims_verified', 0)
            result.setdefault('claims', [])
            
        elif service_name == 'transparency_analyzer':
            result.setdefault('transparency_score', result.get('score', 50))
            result.setdefault('sources_cited', result.get('sources_count', 0))
            result.setdefault('quotes_included', result.get('quotes_count', 0))
            result.setdefault('source_count', result.get('sources_cited', 0))
            result.setdefault('quote_count', result.get('quotes_included', 0))
            
        elif service_name == 'manipulation_detector':
            result.setdefault('integrity_score', result.get('score', 80))
            result.setdefault('techniques_found', 0)
            result.setdefault('techniques', [])
            result.setdefault('tactics_found', result.get('techniques', []))
            
        elif service_name == 'content_analyzer':
            result.setdefault('quality_score', result.get('score', 50))
            result.setdefault('readability', 'Medium')
            result.setdefault('readability_level', result.get('readability', 'Medium'))
            result.setdefault('word_count', 0)
            
        elif service_name == 'author_analyzer':
            # CRITICAL FIX: Only add required fields if missing, preserve ALL existing fields!
            result.setdefault('credibility_score', result.get('score', 50))
            result.setdefault('name', result.get('author_name', 'Unknown'))
            result.setdefault('credibility', result.get('credibility_score', 50))
            result.setdefault('expertise', 'General')
            result.setdefault('track_record', 'Unknown')
        
        # Ensure analysis section exists
        if 'analysis' not in result:
            result['analysis'] = {}
        
        # Ensure all analysis sub-fields exist
        result['analysis'].setdefault(
            'what_we_looked',
            f"Analyzed {service_name.replace('_', ' ')}"
        )
        result['analysis'].setdefault(
            'what_we_found',
            f"Score: {result.get('score', 50)}/100"
        )
        result['analysis'].setdefault(
            'what_it_means',
            self._get_meaning_for_score(service_name, result.get('score', 50))
        )
        
        return result
    
    def _get_meaning_for_score(self, service_name: str, score: int) -> str:
        """Generate appropriate meaning text"""
        
        if score >= 80:
            quality = "excellent"
        elif score >= 60:
            quality = "good"
        elif score >= 40:
            quality = "moderate"
        else:
            quality = "concerning"
        
        meanings = {
            'source_credibility': f"The source shows {quality} credibility.",
            'bias_detector': f"Bias level is {quality}.",
            'fact_checker': f"Factual accuracy is {quality}.",
            'transparency_analyzer': f"Transparency is {quality}.",
            'manipulation_detector': f"Content integrity is {quality}.",
            'content_analyzer': f"Content quality is {quality}.",
            'author_analyzer': f"Author credibility is {quality}."
        }
        
        return meanings.get(service_name, f"Analysis shows {quality} results.")
    
    def _generate_findings(self, trust_score: int, detailed_analysis: Dict[str, Any]) -> str:
        """Generate findings summary"""
        
        findings = []
        
        # Overall assessment
        if trust_score >= 80:
            findings.append("✓ High credibility and trustworthiness.")
        elif trust_score >= 60:
            findings.append("⚠ Generally credible with some concerns.")
        elif trust_score >= 40:
            findings.append("⚠ Moderate credibility with issues.")
        else:
            findings.append("✗ Significant credibility concerns.")
        
        # Add specific findings
        if 'source_credibility' in detailed_analysis:
            source_score = detailed_analysis['source_credibility'].get('score', 0)
            if source_score >= 80:
                findings.append("Source is well-established.")
            elif source_score < 40:
                findings.append("Source has credibility issues.")
        
        if 'bias_detector' in detailed_analysis:
            bias_score = detailed_analysis['bias_detector'].get('bias_score', 50)
            if bias_score < 30:
                findings.append("Strong bias detected.")
            elif bias_score > 70:
                findings.append("Minimal bias detected.")
        
        return " ".join(findings)
    
    def _create_error_response(self, error_msg: str) -> Dict[str, Any]:
        """Create error response"""
        
        return {
            'success': False,
            'error': error_msg,
            'trust_score': 0,
            'article_summary': 'Analysis failed',
            'source': 'Unknown',
            'author': 'Unknown',
            'findings_summary': f'Analysis could not be completed: {error_msg}',
            'detailed_analysis': {},
            'article_metadata': {},
            'processing_time': 0,
            'services_used': 0
        }
