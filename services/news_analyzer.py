"""
News Analyzer Service - Main orchestrator for news credibility analysis
REAL FIXED: Works with your actual service return formats
"""
import logging
from typing import Dict, Any, Optional, List
import time
from datetime import datetime

from services.analysis_pipeline import AnalysisPipeline
from services.service_registry import get_service_registry

logger = logging.getLogger(__name__)

class NewsAnalyzer:
    """
    Main orchestrator for news article analysis using the pipeline pattern
    REAL FIXED: Handles your actual service data formats
    """
    
    def __init__(self):
        """Initialize the news analyzer"""
        self.pipeline = AnalysisPipeline()
        self.service_registry = get_service_registry()
        logger.info("NewsAnalyzer initialized with REAL fixed pipeline pattern")
    
    def analyze(self, content: str, content_type: str = 'url', pro_mode: bool = False) -> Dict[str, Any]:
        """
        Analyze news content for credibility
        REAL FIXED: Creates proper response for your frontend
        
        Args:
            content: URL or text to analyze
            content_type: 'url' or 'text'
            pro_mode: Whether to use pro features
            
        Returns:
            Analysis results in format expected by your frontend
        """
        try:
            # Prepare input data for pipeline
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
            logger.info(f"STARTING REAL NEWS ANALYSIS")
            logger.info(f"Content type: {content_type}")
            logger.info(f"Content: {content[:100]}...")
            logger.info(f"Pro mode: {pro_mode}")
            logger.info("=" * 80)
            
            # Run pipeline analysis
            pipeline_results = self.pipeline.analyze(data)
            
            logger.info("=" * 80)
            logger.info("REAL PIPELINE RESULTS RECEIVED")
            logger.info(f"Success: {pipeline_results.get('success')}")
            logger.info(f"Trust score: {pipeline_results.get('trust_score')}")
            logger.info(f"Services available: {pipeline_results.get('services_available')}")
            logger.info(f"Pipeline keys: {list(pipeline_results.keys())}")
            logger.info("=" * 80)
            
            # REAL FIX: Transform pipeline results to your frontend format
            response = self._build_real_response(pipeline_results, content, content_type, pro_mode)
            
            logger.info("=" * 80)
            logger.info("REAL FINAL RESPONSE BUILT")
            logger.info(f"Response success: {response.get('success')}")
            logger.info(f"Response keys: {list(response.keys())}")
            if 'data' in response:
                logger.info(f"Response data keys: {list(response['data'].keys())}")
                if 'detailed_analysis' in response['data']:
                    detailed = response['data']['detailed_analysis']
                    logger.info(f"Detailed analysis services: {list(detailed.keys())}")
                    # Show first service's data structure
                    if detailed:
                        first_service = list(detailed.keys())[0]
                        first_data = detailed[first_service]
                        logger.info(f"Sample service data ({first_service}): {list(first_data.keys())}")
            logger.info("=" * 80)
            
            return response
            
        except Exception as e:
            logger.error(f"NewsAnalyzer error: {str(e)}", exc_info=True)
            return self._build_error_response(str(e), content, content_type)
    
    def _build_real_response(self, pipeline_results: Dict[str, Any], content: str, 
                            content_type: str, pro_mode: bool) -> Dict[str, Any]:
        """
        REAL FIX: Build response in format your frontend actually expects
        """
        try:
            # Extract article information
            article = pipeline_results.get('article', {})
            if not article or not article.get('extraction_successful', True):
                article = {
                    'title': 'Unknown Title',
                    'author': 'Unknown',
                    'url': content if content_type == 'url' else '',
                    'text': content if content_type == 'text' else '',
                    'extraction_successful': False
                }
            
            # REAL FIX: Build detailed_analysis with your service data
            detailed_analysis = {}
            
            # Your actual service list
            service_list = [
                'article_extractor', 'source_credibility', 'author_analyzer',
                'bias_detector', 'fact_checker', 'transparency_analyzer',
                'manipulation_detector', 'content_analyzer', 'openai_enhancer'
            ]
            
            services_with_data = 0
            for service_name in service_list:
                if service_name in pipeline_results:
                    service_data = pipeline_results[service_name]
                    
                    # REAL FIX: Handle your actual service data structure
                    if isinstance(service_data, dict) and service_data.get('success', False):
                        # Your services are already processed by pipeline
                        detailed_analysis[service_name] = service_data
                        services_with_data += 1
                        logger.info(f"Service {service_name}: SUCCESS - {len(service_data)} fields")
                    else:
                        # Service failed or no data
                        logger.warning(f"Service {service_name}: FAILED or no data")
                        detailed_analysis[service_name] = {
                            'success': False,
                            'error': service_data.get('error', 'Service did not return data') if isinstance(service_data, dict) else 'No data returned',
                            'service': service_name,
                            'available': False
                        }
                else:
                    # Service not in pipeline results
                    logger.info(f"Service {service_name}: Not in pipeline results")
                    detailed_analysis[service_name] = {
                        'success': False,
                        'error': 'Service did not run',
                        'service': service_name,
                        'available': False
                    }
            
            # REAL FIX: Extract key findings from your actual service data
            key_findings = self._extract_real_key_findings(detailed_analysis)
            
            # Build final response in YOUR expected format
            response = {
                'success': pipeline_results.get('success', True),
                'data': {
                    'article': article,
                    'analysis': {
                        'trust_score': pipeline_results.get('trust_score', 50),
                        'trust_level': pipeline_results.get('trust_level', 'Unknown'),
                        'key_findings': key_findings,
                        'summary': pipeline_results.get('summary', 'Analysis completed')
                    },
                    'detailed_analysis': detailed_analysis  # This is what your frontend needs!
                },
                'metadata': {
                    'analysis_time': pipeline_results.get('pipeline_metadata', {}).get('total_time', 0),
                    'timestamp': datetime.now().isoformat(),
                    'services_available': services_with_data,
                    'services_with_data': services_with_data,
                    'is_pro': pro_mode,
                    'analysis_mode': 'pro' if pro_mode else 'basic',
                    'pipeline_metadata': pipeline_results.get('pipeline_metadata', {})
                }
            }
            
            # Add warnings if any services failed
            if pipeline_results.get('errors'):
                response['warnings'] = pipeline_results['errors']
            
            logger.info(f"Built REAL response with {services_with_data} successful services")
            return response
            
        except Exception as e:
            logger.error(f"Error building REAL response: {str(e)}", exc_info=True)
            return self._build_error_response(f"Response building failed: {str(e)}", content, content_type)
    
    def _extract_real_key_findings(self, detailed_analysis: Dict[str, Any]) -> List[str]:
        """Extract key findings from your REAL service data"""
        findings = []
        
        # REAL FIX: Extract from your actual service data structure
        
        # Source credibility findings
        if 'source_credibility' in detailed_analysis:
            sc_data = detailed_analysis['source_credibility']
            if sc_data.get('success'):
                # Your service returns findings array
                service_findings = sc_data.get('findings', [])
                if service_findings:
                    # Add first few findings
                    for finding in service_findings[:2]:
                        if isinstance(finding, dict):
                            findings.append(finding.get('text', str(finding)))
                        else:
                            findings.append(str(finding))
                else:
                    # Fallback to score-based finding
                    score = sc_data.get('credibility_score', sc_data.get('score', 50))
                    level = sc_data.get('credibility_level', sc_data.get('level', 'Unknown'))
                    findings.append(f"Source credibility: {level} ({score}/100)")
        
        # Author findings
        if 'author_analyzer' in detailed_analysis:
            auth_data = detailed_analysis['author_analyzer']
            if auth_data.get('success'):
                author_name = auth_data.get('author_name', 'Unknown')
                author_score = auth_data.get('author_score', 50)
                if author_name != 'Unknown':
                    findings.append(f"Author: {author_name} (credibility: {author_score}/100)")
        
        # Bias findings
        if 'bias_detector' in detailed_analysis:
            bias_data = detailed_analysis['bias_detector']
            if bias_data.get('success'):
                bias_direction = bias_data.get('bias_direction', 'neutral')
                political_leaning = bias_data.get('political_leaning', '')
                if bias_direction != 'neutral' or political_leaning != 'center':
                    bias_text = political_leaning if political_leaning else bias_direction
                    findings.append(f"Political bias detected: {bias_text}")
        
        # Fact check findings
        if 'fact_checker' in detailed_analysis:
            fc_data = detailed_analysis['fact_checker']
            if fc_data.get('success'):
                verified = fc_data.get('verified_claims', 0)
                disputed = fc_data.get('disputed_claims', 0)
                total = fc_data.get('total_claims', verified + disputed)
                if total > 0:
                    findings.append(f"Fact check: {verified}/{total} claims verified")
        
        # Manipulation findings
        if 'manipulation_detector' in detailed_analysis:
            manip_data = detailed_analysis['manipulation_detector']
            if manip_data.get('success'):
                tactics = manip_data.get('tactics_found', [])
                tactics_count = len(tactics) if isinstance(tactics, list) else tactics
                if tactics_count > 0:
                    findings.append(f"Manipulation tactics detected: {tactics_count}")
        
        # AI enhancement findings
        if 'openai_enhancer' in detailed_analysis:
            ai_data = detailed_analysis['openai_enhancer']
            if ai_data.get('success'):
                key_insights = ai_data.get('key_insights', [])
                if key_insights and isinstance(key_insights, list):
                    findings.extend(key_insights[:2])  # Add top 2 AI insights
        
        # Default finding if none found
        if not findings:
            findings.append("Analysis completed successfully")
        
        return findings[:5]  # Limit to 5 findings
    
    def _build_error_response(self, error_message: str, content: str, content_type: str) -> Dict[str, Any]:
        """Build error response in expected format"""
        return {
            'success': False,
            'error': error_message,
            'data': {
                'article': {
                    'title': 'Analysis Failed',
                    'author': 'Unknown',
                    'url': content if content_type == 'url' else '',
                    'text': content if content_type == 'text' else '',
                    'extraction_successful': False
                },
                'analysis': {
                    'trust_score': 50,
                    'trust_level': 'Unknown',
                    'key_findings': ['Analysis failed'],
                    'summary': f'Error: {error_message}'
                },
                'detailed_analysis': {}
            },
            'metadata': {
                'analysis_time': 0,
                'timestamp': datetime.now().isoformat(),
                'services_available': 0,
                'services_with_data': 0,
                'is_pro': False,
                'analysis_mode': 'error'
            }
        }
    
    def get_available_services(self) -> Dict[str, Any]:
        """Get information about available services"""
        return self.service_registry.get_service_status()
    
    def get_service_info(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific service"""
        return self.service_registry.get_service_info(service_name)
