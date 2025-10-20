# services/news_analyzer.py
"""
News Analyzer Service - WITH ENHANCED "WHAT WE FOUND" SUMMARY
Date: October 20, 2025
Version: 21.1 - CRITICAL SUCCESS FLAG FIX

CHANGE LOG:
- 2025-10-20: v21.1 - CRITICAL FIX: Always set success=True in _build_response
  * Bug: Response was missing success=True, causing frontend to show "Analysis failed"
  * Fix: Line 153 now explicitly sets success=True in response dict
  * This ensures DataTransformer passes success=True to frontend
- 2025-10-13: v21.0 - Enhanced _generate_findings_summary() method
  * Now generates 2-5 sentence conversational summaries
  * Highlights specific concerns from each service
  * Dynamic content based on actual findings
  * Always ends with Pro version upgrade prompt
  * Replaces generic statements with actionable insights

Previous versions:
- v13.1 - Charts embedded in services
- v13.0 - Chart generation integration
- Earlier - Initial orchestrator

DEPLOYMENT:
Replace existing services/news_analyzer.py with this complete file
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
    Clean orchestrator for news analysis with insights, enrichment, and charts
    """
    
    def __init__(self):
        """Initialize with pipeline and enhancement services"""
        self.pipeline = AnalysisPipeline()
        self.insight_generator = InsightGenerator()
        self.data_enricher = DataEnricher()
        logger.info("[NewsAnalyzer v21.1] Initialized - WITH SUCCESS FLAG FIX")
    
    def analyze(self, content: str, content_type: str = 'url', pro_mode: bool = False) -> Dict[str, Any]:
        """
        Main analysis method - clean and simple
        
        Args:
            content: URL or text to analyze
            content_type: 'url' or 'text'
            pro_mode: Not used (for compatibility)
            
        Returns:
            Properly formatted analysis results with insights, enrichment, and charts
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
            logger.info("[NewsAnalyzer v21.1] Starting Analysis")
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
                
                # ===== TIER 2: CHART GENERATION (TOP LEVEL - PRESERVED) =====
                logger.info("[NewsAnalyzer] Generating chart visualizations...")
                from services.chart_generator import ChartGenerator
                chart_gen = ChartGenerator()
                chart_result = chart_gen.generate_all_charts(response)
                
                if chart_result.get('success'):
                    response['charts'] = chart_result.get('charts', {})
                    logger.info(f"[NewsAnalyzer] ✓ Generated {chart_result.get('chart_count', 0)} charts")
                else:
                    logger.warning("[NewsAnalyzer] Chart generation failed")
                    response['charts'] = {}
                
                logger.info("[NewsAnalyzer] ✓ All enhancements complete")
                
            except Exception as e:
                logger.error(f"[NewsAnalyzer] Enhancement error (continuing): {e}")
                # Continue without enhancements
                if 'insights' not in response:
                    response['insights'] = {}
                if 'charts' not in response:
                    response['charts'] = {}
            
            logger.info("=" * 80)
            logger.info(f"[NewsAnalyzer] COMPLETE - {time.time() - analysis_start:.2f}s")
            logger.info(f"[NewsAnalyzer v21.1] ✓ SUCCESS=TRUE IN RESPONSE")
            logger.info("=" * 80)
            
            return response
            
        except Exception as e:
            logger.error(f"[NewsAnalyzer] Critical error: {e}", exc_info=True)
            return self._create_error_response(f"Analysis failed: {str(e)}")
    
    def _build_response(self, pipeline_results: Dict[str, Any], 
                       content: str, content_type: str,
                       start_time: float) -> Dict[str, Any]:
        """Build formatted response for frontend"""
        
        article_data = pipeline_results.get('article', {})
        detailed = pipeline_results.get('detailed_analysis', {})
        trust_score = pipeline_results.get('trust_score', 50)
        
        # Extract key information
        source = article_data.get('source', 'Unknown Source')
        author = article_data.get('author', 'Staff Writer')
        title = article_data.get('title', 'Article Analysis')
        
        # Normalize detailed analysis (ensures consistent 'score' fields)
        normalized_detailed = self._normalize_detailed_analysis(detailed)
        
        # ===== NEW v13.1: INTEGRATE CHARTS INTO EACH SERVICE =====
        # This adds 'chart_data' field to each service's response
        normalized_detailed = self._integrate_charts_into_services(normalized_detailed)
        
        # Build response
        # ===== CRITICAL FIX v21.1: ALWAYS SET SUCCESS=TRUE =====
        response = {
            'success': True,  # ← THIS WAS THE BUG! This line ensures frontend knows analysis succeeded
            'trust_score': trust_score,
            'article_summary': title[:200] if title else 'Article analyzed',
            'source': source,
            'author': author,
            'findings_summary': self._generate_findings_summary(normalized_detailed, trust_score, source),
            'detailed_analysis': normalized_detailed,
            'processing_time': round(time.time() - start_time, 2),
            'content_type': content_type,
            'word_count': article_data.get('word_count', 0)
        }
        
        logger.info(f"[NewsAnalyzer v21.1] ✓ Response built with success=True")
        
        return response
    
    def _normalize_detailed_analysis(self, detailed: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all services have consistent score field"""
        
        normalized = {}
        
        for service_name, service_data in detailed.items():
            if not isinstance(service_data, dict):
                continue
            
            normalized_service = service_data.copy()
            
            # Ensure 'score' field exists based on service type
            if 'score' not in normalized_service:
                if service_name == 'source_credibility':
                    normalized_service['score'] = service_data.get('credibility_score', 50)
                elif service_name == 'bias_detector':
                    normalized_service['score'] = service_data.get('objectivity_score', 50)
                elif service_name == 'fact_checker':
                    normalized_service['score'] = service_data.get('verification_score', 
                                                   service_data.get('accuracy_score', 50))
                elif service_name == 'author_analyzer':
                    normalized_service['score'] = service_data.get('credibility_score', 50)
                elif service_name == 'transparency_analyzer':
                    normalized_service['score'] = service_data.get('transparency_score', 50)
                elif service_name == 'manipulation_detector':
                    normalized_service['score'] = service_data.get('integrity_score', 50)
                elif service_name == 'content_analyzer':
                    normalized_service['score'] = service_data.get('quality_score', 50)
                else:
                    normalized_service['score'] = 50
            
            normalized[service_name] = normalized_service
        
        return normalized
    
    def _integrate_charts_into_services(self, detailed_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        ===== NEW METHOD v13.1 =====
        Integrate chart data into each service's response
        
        This adds a 'chart_data' field to each service containing its visualization data.
        Frontend (service-templates.js) will read this and render charts inside service cards.
        """
        try:
            from services.chart_generator import ChartGenerator
            chart_gen = ChartGenerator()
            
            # Map service names to their chart generation methods
            service_map = {
                'source_credibility': 'source_credibility',
                'bias_detector': 'bias_detector',
                'fact_checker': 'fact_checker',
                'author_analyzer': 'author_analyzer',
                'transparency_analyzer': 'transparency_analyzer',
                'manipulation_detector': 'manipulation_detector',
                'content_analyzer': 'content_analyzer'
            }
            
            charts_generated = 0
            
            for service_key, chart_id in service_map.items():
                if service_key in detailed_analysis:
                    try:
                        service_data = detailed_analysis[service_key]
                        
                        # Generate chart for this service
                        chart_data = chart_gen.generate_service_chart(chart_id, service_data)
                        
                        if chart_data and chart_data.get('success'):
                            # Embed chart directly in service data
                            detailed_analysis[service_key]['chart_data'] = chart_data.get('chart')
                            charts_generated += 1
                            logger.debug(f"[Charts] ✓ {service_key}: chart embedded")
                        else:
                            logger.debug(f"[Charts] ✗ {service_key}: no chart data returned")
                            
                    except Exception as e:
                        logger.warning(f"[Charts] Failed to generate chart for {service_key}: {e}")
                        continue
            
            logger.info(f"[NewsAnalyzer] ✓ Integrated {charts_generated}/{len(service_map)} charts into services")
            
            return detailed_analysis
            
        except Exception as e:
            logger.error(f"[NewsAnalyzer] Chart integration failed: {e}", exc_info=True)
            # Non-critical - return original data if charts fail
            return detailed_analysis
    
    def _generate_findings_summary(self, detailed: Dict[str, Any], trust_score: int, source: str) -> str:
        """
        ===== ENHANCED v21.0 =====
        Generate conversational, informative "What We Found" summary (2-5 sentences)
        
        This replaces the generic summary with specific, actionable insights based on
        what each service actually found during analysis.
        """
        
        # Collect specific concerns and strengths from each service
        concerns = []
        strengths = []
        
        # Source Credibility Analysis (25% weight)
        source_data = detailed.get('source_credibility', {})
        if source_data:
            source_score = source_data.get('score', 0)
            
            if source_score < 60:
                concerns.append('weak source credibility')
            elif source_score >= 80:
                strengths.append('strong source credibility')
        
        # Bias Detection (20% weight)
        bias_data = detailed.get('bias_detector', {})
        if bias_data:
            bias_score = bias_data.get('score', 0)
            # Try to get political lean from various possible field names
            political_lean = abs(
                bias_data.get('political_lean', 
                bias_data.get('bias_score', 
                bias_data.get('lean', 0)))
            )
            
            if bias_score < 70 or political_lean > 50:
                if political_lean > 70:
                    concerns.append('significant political bias')
                else:
                    concerns.append('noticeable bias')
            elif bias_score >= 90 and political_lean < 30:
                strengths.append('minimal bias')
        
        # Author Analysis (15% weight)
        author_data = detailed.get('author_analyzer', {})
        if author_data:
            author_score = author_data.get('score', 0)
            
            if author_score < 60:
                concerns.append('limited author credibility')
            elif author_score >= 85:
                strengths.append('credible author')
        
        # Fact Checking (15% weight)
        fact_data = detailed.get('fact_checker', {})
        if fact_data:
            fact_score = fact_data.get('score', 0)
            
            if fact_score >= 90:
                strengths.append('strong factual accuracy')
            elif fact_score < 60:
                concerns.append('factual accuracy issues')
        
        # Transparency (10% weight)
        trans_data = detailed.get('transparency_analyzer', {})
        if trans_data:
            trans_score = trans_data.get('score', 0)
            
            if trans_score < 50:
                concerns.append('poor transparency')
            elif trans_score >= 85:
                strengths.append('good transparency')
        
        # Manipulation Detection (10% weight)
        manip_data = detailed.get('manipulation_detector', {})
        if manip_data:
            manip_score = manip_data.get('score', 0)
            manipulation_detected = manip_data.get('manipulation_detected', False)
            
            if manip_score < 60 or manipulation_detected:
                concerns.append('manipulative techniques detected')
        
        # Content Quality (5% weight)
        quality_data = detailed.get('content_analyzer', {})
        if quality_data:
            quality_score = quality_data.get('score', 0)
            
            if quality_score < 50:
                concerns.append('low content quality')
        
        # Build conversational summary (2-5 sentences)
        summary_parts = []
        
        # Sentence 1: Overall assessment
        if trust_score >= 70:
            summary_parts.append(
                f"This article from {source} shows moderate to high credibility "
                f"with a trust score of {trust_score}/100."
            )
        elif trust_score >= 40:
            summary_parts.append(
                f"This article from {source} shows mixed credibility "
                f"with a trust score of {trust_score}/100."
            )
        else:
            summary_parts.append(
                f"This article from {source} shows low credibility "
                f"with a trust score of {trust_score}/100."
            )
        
        # Sentence 2-3: Specific findings
        if concerns:
            # Format concerns naturally
            if len(concerns) == 1:
                summary_parts.append(f"Our analysis identified {concerns[0]}.")
            elif len(concerns) == 2:
                summary_parts.append(f"Our analysis identified {concerns[0]} and {concerns[1]}.")
            else:
                # Multiple concerns: list them naturally
                last_concern = concerns[-1]
                other_concerns = ', '.join(concerns[:-1])
                summary_parts.append(
                    f"Our analysis identified {other_concerns}, and {last_concern}."
                )
        elif strengths:
            # If no concerns, highlight strengths
            if len(strengths) == 1:
                summary_parts.append(f"The article demonstrates {strengths[0]}.")
            else:
                summary_parts.append(f"The article demonstrates {' and '.join(strengths)}.")
        
        # Sentence 4: Recommendation (if needed)
        if trust_score < 60:
            summary_parts.append("We recommend verifying claims through additional sources.")
        
        # Sentence 5: Pro version prompt (always included)
        summary_parts.append("Upgrade to Pro for detailed breakdowns and source comparisons.")
        
        return ' '.join(summary_parts)
    
    def _create_error_response(self, error_msg: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            'success': False,
            'error': error_msg,
            'trust_score': 0,
            'article_summary': 'Analysis failed',
            'source': 'Unknown',
            'author': 'Unknown',
            'findings_summary': error_msg,
            'detailed_analysis': {},
            'charts': {}
        }

# This file is not truncated
