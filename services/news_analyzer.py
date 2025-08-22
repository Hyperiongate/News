"""
News Analyzer Service - Main orchestrator for news credibility analysis
Fixed to work with the new AnalysisPipeline class
"""

import logging
from typing import Dict, Any, Optional

from services.analysis_pipeline import AnalysisPipeline
from services.service_registry import get_service_registry

logger = logging.getLogger(__name__)


class NewsAnalyzer:
    """
    Main orchestrator for news article analysis using the pipeline pattern
    """
    
    def __init__(self):
        """Initialize the news analyzer"""
        self.pipeline = AnalysisPipeline()
        self.service_registry = get_service_registry()
        logger.info("NewsAnalyzer initialized with pipeline pattern")
    
    def analyze(self, content: str, content_type: str = 'url', pro_mode: bool = False) -> Dict[str, Any]:
        """
        Analyze news content for credibility
        
        Args:
            content: URL or text to analyze
            content_type: 'url' or 'text'
            pro_mode: Whether to use pro features
            
        Returns:
            Analysis results with trust score and service outputs
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
            
            # Run pipeline analysis
            logger.info(f"Starting analysis for {content_type}: {content[:100]}...")
            results = self.pipeline.analyze(data)
            
            # Log results
            if results.get('success'):
                logger.info(f"Analysis completed successfully with trust score: {results.get('trust_score', 'N/A')}")
            else:
                logger.error(f"Analysis failed: {results.get('error', 'Unknown error')}")
            
            return results
            
        except Exception as e:
            logger.error(f"NewsAnalyzer error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'trust_score': 50,
                'trust_level': 'Unknown',
                'services_available': 0
            }
    
    def get_available_services(self) -> Dict[str, Any]:
        """Get information about available services"""
        return self.service_registry.get_service_status()
    
    def get_service_info(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific service"""
        return self.service_registry.get_service_info(service_name)
