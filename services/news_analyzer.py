"""
News Analyzer Service - WITH SERVICE-INTEGRATED CHARTS
Date: October 8, 2025
Version: 13.1 - CHARTS NOW EMBEDDED IN EACH SERVICE

CHANGES FROM 13.0:
- Charts now embedded in each service's data (chart_data field)
- Added _integrate_charts_into_services() method
- Called after normalizing detailed_analysis in _build_response()
- All existing functionality preserved (DO NO HARM)

DEPLOYMENT:
Replace services/news_analyzer.py with this complete file
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
        logger.info("[NewsAnalyzer v13.1] Initialized - WITH SERVICE-INTEGRATED CHARTS")
    
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
        response = {
            'success': True,
            'trust_score': trust_score,
            'article_summary': title[:200] if title else 'Article analyzed',
            'source': source,
            'author': author,
            'findings_summary': self._generate_findings_summary(normalized_detailed, trust_score),
            'detailed_analysis': normalized_detailed,
            'processing_time': round(time.time() - start_time, 2),
            'content_type': content_type,
            'word_count': article_data.get('word_count', 0)
        }
        
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
        
        Args:
            detailed_analysis: Normalized service data dict
            
        Returns:
            Same dict with chart_data added to each service
        """
        try:
            logger.info("[NewsAnalyzer] Integrating charts into service data...")
            
            from services.chart_generator import ChartGenerator
            
            chart_gen = ChartGenerator()
            
            # Service ID mapping (service key -> chart service ID)
            service_map = {
                'source_credibility': 'source_credibility',
                'bias_detector': 'bias_detector',
                'fact_checker': 'fact_checker',
                'transparency_analyzer': 'transparency_analyzer',
                'manipulation_detector': 'manipulation_detector',
                'author_analyzer': 'author_analyzer',
                'content_analyzer': 'content_analyzer'
            }
            
            charts_generated = 0
            
            # Generate chart for each service
            for service_key, chart_service_id in service_map.items():
                if service_key in detailed_analysis:
                    service_data = detailed_analysis[service_key]
                    
                    # Skip if data is empty or error
                    if not service_data or not isinstance(service_data, dict):
                        logger.debug(f"[Charts] Skipping {service_key} - no valid data")
                        continue
                    
                    # Generate chart data for this service
                    try:
                        chart_data = chart_gen.generate_service_chart(chart_service_id, service_data)
                        
                        if chart_data:
                            # Embed chart data into service response
                            detailed_analysis[service_key]['chart_data'] = chart_data
                            charts_generated += 1
                            logger.debug(f"[Charts] ✓ {service_key}: chart integrated")
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
    
    def _generate_findings_summary(self, detailed: Dict[str, Any], trust_score: int) -> str:
        """Generate human-readable findings summary"""
        
        findings = []
        
        # Trust level
        if trust_score >= 80:
            findings.append("This article demonstrates high credibility and trustworthiness.")
        elif trust_score >= 60:
            findings.append("This article shows moderate credibility with some areas of concern.")
        else:
            findings.append("This article raises significant credibility concerns.")
        
        # Source credibility
        source_data = detailed.get('source_credibility', {})
        source_score = source_data.get('credibility_score', source_data.get('score', 0))
        if source_score >= 80:
            findings.append("The source has an excellent reputation.")
        elif source_score < 50:
            findings.append("The source has limited credibility.")
        
        # Bias detection
        bias_data = detailed.get('bias_detector', {})
        bias_score = bias_data.get('objectivity_score', bias_data.get('score', 0))
        if bias_score < 50:
            findings.append("Significant bias detected in the content.")
        
        # Fact checking
        fact_data = detailed.get('fact_checker', {})
        fact_score = fact_data.get('verification_score', 
                                   fact_data.get('accuracy_score', fact_data.get('score', 0)))
        if fact_score >= 80:
            findings.append("Strong factual accuracy verified.")
        elif fact_score < 50:
            findings.append("Multiple factual concerns identified.")
        
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
            'findings_summary': error_msg,
            'detailed_analysis': {},
            'charts': {}
        }
