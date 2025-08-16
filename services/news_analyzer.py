"""
News Analyzer Service (Refactored)
Clean implementation using pipeline and service registry
"""
import logging
from typing import Dict, Any, Optional
from config import Config
from services.analysis_pipeline import get_pipeline
from services.service_registry import get_service_registry

logger = logging.getLogger(__name__)


class NewsAnalyzer:
    """
    Main orchestrator for news analysis
    Now uses pipeline pattern for clean processing
    """
    
    def __init__(self):
        """Initialize analyzer with pipeline"""
        self.pipeline = get_pipeline()
        self.service_registry = get_service_registry()
        self.service_status = self.service_registry.get_service_status()
        
        logger.info(f"NewsAnalyzer initialized with {self.service_status['summary']['total_available']} available services")
    
    def analyze(self, content: str, content_type: str = 'url', pro_mode: bool = False) -> Dict[str, Any]:
        """
        Perform comprehensive analysis on news content
        
        Args:
            content: URL or text to analyze
            content_type: 'url' or 'text'
            pro_mode: Whether to use premium features (changed from is_pro to match app.py)
            
        Returns:
            Standardized analysis results
        """
        try:
            logger.info(f"Starting analysis - type: {content_type}, pro: {pro_mode}")
            
            # Set options based on pro status
            options = {
                'is_pro': pro_mode,
                'include_fact_checking': pro_mode,
                'include_ai_summary': pro_mode and Config.OPENAI_API_KEY,
                'include_manipulation_detection': pro_mode,
                'detailed_bias_analysis': pro_mode
            }
            
            # FIXED: Always use sync pipeline since all our services are sync
            # The async pipeline was causing "Service not found or not async" errors
            # because ArticleExtractor and other services are sync, not async
            results = self.pipeline.run(content, content_type, options)
            
            # Add service metadata
            results['services_available'] = self.service_status['summary']['total_available']
            results['is_pro'] = pro_mode
            results['analysis_mode'] = 'premium' if pro_mode else 'basic'
            
            # Log completion
            logger.info(f"Analysis completed - success: {results.get('success')}, "
                       f"trust_score: {results.get('trust_score')}, "
                       f"duration: {results.get('pipeline_metadata', {}).get('total_duration', 0):.2f}s")
            
            return results
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f'Analysis failed: {str(e)}',
                'trust_score': 50,
                'trust_level': 'Unknown',
                'services_available': self.service_status['summary']['total_available'],
                'is_pro': pro_mode,
                'analysis_mode': 'error'
            }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get current status of all services"""
        return self.service_registry.get_service_status()
    
    def reload_services(self) -> Dict[str, Any]:
        """Reload all services and return new status"""
        # Reload failed services
        failed_services = self.service_registry.failed_services.copy()
        reloaded = []
        
        for service_name in failed_services:
            if self.service_registry.reload_service(service_name):
                reloaded.append(service_name)
        
        # Update status
        self.service_status = self.service_registry.get_service_status()
        
        return {
            'reloaded': reloaded,
            'current_status': self.service_status
        }
