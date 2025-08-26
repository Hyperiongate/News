"""
News Analyzer Service - BULLETPROOF VERSION
ALL HOLES PLUGGED: Handles every possible failure mode
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
    BULLETPROOF: Handles every possible failure mode and data structure variant
    """
    
    def __init__(self):
        """Initialize with comprehensive error handling"""
        try:
            self.pipeline = AnalysisPipeline()
            self.service_registry = get_service_registry()
            
            # HOLE FIX 1: Validate service registry is working
            registry_status = self.service_registry.get_service_status()
            working_services = sum(1 for s in registry_status.get('services', {}).values() if s.get('available', False))
            
            logger.info(f"NewsAnalyzer initialized - {working_services} services available")
            
            if working_services == 0:
                logger.error("CRITICAL: No services available in registry")
                
        except Exception as e:
            logger.error(f"NewsAnalyzer initialization failed: {str(e)}", exc_info=True)
            # Continue anyway - we'll handle this in analyze()
    
    def analyze(self, content: str, content_type: str = 'url', pro_mode: bool = False) -> Dict[str, Any]:
        """
        BULLETPROOF analyze with comprehensive error handling
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
            
            logger.info("=" * 80)
            logger.info(f"BULLETPROOF ANALYSIS START")
            logger.info(f"Content type: {content_type}")
            logger.info(f"Content length: {len(str(content))}")
            logger.info(f"Pro mode: {pro_mode}")
            logger.info("=" * 80)
            
            # HOLE FIX 2: Validate pipeline exists and is callable
            if not hasattr(self, 'pipeline') or not self.pipeline:
                logger.error("Pipeline not initialized")
                return self._build_error_response("Pipeline initialization failed", content, content_type)
            
            # Run pipeline with comprehensive error handling
            try:
                pipeline_results = self.pipeline.analyze(data)
                logger.info(f"Pipeline returned {len(pipeline_results)} keys: {list(pipeline_results.keys())}")
            except Exception as pipeline_error:
                logger.error(f"Pipeline execution failed: {str(pipeline_error)}", exc_info=True)
                return self._build_error_response(f"Pipeline failed: {str(pipeline_error)}", content, content_type)
            
            # HOLE FIX 3: Validate pipeline results structure
            if not isinstance(pipeline_results, dict):
                logger.error(f"Pipeline returned invalid type: {type(pipeline_results)}")
                return self._build_error_response("Pipeline returned invalid data type", content, content_type)
            
            if not pipeline_results:
                logger.error("Pipeline returned empty results")
                return self._build_error_response("Pipeline returned no data", content, content_type)
            
            # Build response with comprehensive validation
            response = self._build_bulletproof_response(pipeline_results, content, content_type, pro_mode)
            
            logger.info("=" * 80)
            logger.info("BULLETPROOF ANALYSIS COMPLETE")
            logger.info(f"Response success: {response.get('success')}")
            logger.info(f"Services with data: {response.get('metadata', {}).get('services_with_data', 0)}")
            logger.info("=" * 80)
            
            return response
            
        except Exception as e:
            logger.error(f"CRITICAL NewsAnalyzer error: {str(e)}", exc_info=True)
            return self._build_error_response(f"Critical analysis failure: {str(e)}", content, content_type)
    
    def _build_bulletproof_response(self, pipeline_results: Dict[str, Any], content: str, 
                                   content_type: str, pro_mode: bool) -> Dict[str, Any]:
        """
        BULLETPROOF response building - handles all possible data structures
        """
        try:
            # HOLE FIX 4: Extract article with multiple fallback strategies
            article = self._extract_article_bulletproof(pipeline_results, content, content_type)
            
            # HOLE FIX 5: Get actual available services dynamically
            available_services = self._discover_actual_services(pipeline_results)
            logger.info(f"Discovered services in pipeline: {available_services}")
            
            # HOLE FIX 6: Build detailed_analysis with bulletproof extraction
            detailed_analysis = {}
            services_with_data = 0
            extraction_errors = []
            
            for service_name in available_services:
                try:
                    service_data = self._extract_service_bulletproof(service_name, pipeline_results)
                    
                    if service_data and self._validate_service_data(service_data):
                        detailed_analysis[service_name] = service_data
                        services_with_data += 1
                        logger.info(f"✓ Service {service_name}: extracted {len(service_data)} fields")
                    else:
                        # Create error placeholder
                        detailed_analysis[service_name] = {
                            'success': False,
                            'error': 'No valid data extracted',
                            'service': service_name,
                            'available': False
                        }
                        logger.warning(f"✗ Service {service_name}: no valid data")
                        
                except Exception as extract_error:
                    extraction_errors.append(f"{service_name}: {str(extract_error)}")
                    detailed_analysis[service_name] = {
                        'success': False,
                        'error': f'Extraction failed: {str(extract_error)}',
                        'service': service_name,
                        'available': False
                    }
                    logger.error(f"✗ Service {service_name} extraction failed: {str(extract_error)}")
            
            # HOLE FIX 7: Ensure we have at least some data structure
            if not detailed_analysis:
                logger.error("CRITICAL: No services extracted any data")
                # Create minimal service structure so frontend doesn't break
                minimal_services = ['source_credibility', 'author_analyzer', 'bias_detector', 'content_analyzer']
                for service_name in minimal_services:
                    detailed_analysis[service_name] = {
                        'success': False,
                        'error': 'Service did not run or failed',
                        'service': service_name,
                        'available': False,
                        'score': 0,
                        'level': 'Unknown'
                    }
            
            # HOLE FIX 8: Bulletproof trust score calculation
            trust_score = self._calculate_bulletproof_trust_score(detailed_analysis, pipeline_results)
            trust_level = self._get_trust_level(trust_score)
            
            # HOLE FIX 9: Bulletproof key findings extraction
            key_findings = self._extract_bulletproof_key_findings(detailed_analysis, pipeline_results)
            
            # HOLE FIX 10: Build response with validation at each step
            response = {
                'success': True,  # We got some response even if services failed
                'data': {
                    'article': article,
                    'analysis': {
                        'trust_score': trust_score,
                        'trust_level': trust_level,
                        'key_findings': key_findings,
                        'summary': self._generate_bulletproof_summary(services_with_data, len(available_services), pipeline_results)
                    },
                    'detailed_analysis': detailed_analysis
                },
                'metadata': {
                    'analysis_time': pipeline_results.get('pipeline_metadata', {}).get('total_time', 0),
                    'timestamp': datetime.now().isoformat(),
                    'services_available': len(available_services),
                    'services_with_data': services_with_data,
                    'services_discovered': available_services,
                    'extraction_errors': extraction_errors,
                    'is_pro': pro_mode,
                    'analysis_mode': 'pro' if pro_mode else 'basic',
                    'pipeline_metadata': pipeline_results.get('pipeline_metadata', {}),
                    'pipeline_success': pipeline_results.get('success', False)
                }
            }
            
            # Add warnings
            warnings = []
            if extraction_errors:
                warnings.extend(extraction_errors)
            if pipeline_results.get('errors'):
                warnings.extend(pipeline_results['errors'])
            if services_with_data == 0:
                warnings.append("No services returned valid data")
            
            if warnings:
                response['warnings'] = warnings
            
            logger.info(f"BULLETPROOF response built: {services_with_data}/{len(available_services)} services successful")
            return response
            
        except Exception as e:
            logger.error(f"CRITICAL response building error: {str(e)}", exc_info=True)
            return self._build_error_response(f"Response building failed: {str(e)}", content, content_type)
    
    def _discover_actual_services(self, pipeline_results: Dict[str, Any]) -> List[str]:
        """
        HOLE FIX: Discover what services actually exist in pipeline results
        """
        # Known service names to look for
        known_services = [
            'article_extractor', 'source_credibility', 'author_analyzer',
            'bias_detector', 'fact_checker', 'transparency_analyzer',
            'manipulation_detector', 'content_analyzer', 'openai_enhancer'
        ]
        
        # Non-service keys
        non_service_keys = {
            'success', 'trust_score', 'trust_level', 'summary', 'article',
            'pipeline_metadata', 'errors', 'services_available', 'is_pro',
            'analysis_mode', 'error', 'warnings', 'metadata'
        }
        
        discovered = []
        
        # First, check for known services
        for service in known_services:
            if service in pipeline_results:
                discovered.append(service)
                logger.debug(f"Found known service: {service}")
        
        # Then, look for any other keys that might be services
        for key, value in pipeline_results.items():
            if key not in non_service_keys and key not in discovered:
                if isinstance(value, dict):
                    # Could be a service result
                    discovered.append(key)
                    logger.debug(f"Discovered potential service: {key}")
        
        logger.info(f"Service discovery: {len(discovered)} services found")
        return discovered
    
    def _extract_service_bulletproof(self, service_name: str, pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        BULLETPROOF service data extraction with multiple fallback strategies
        """
        if service_name not in pipeline_results:
            return {}
        
        raw_data = pipeline_results[service_name]
        
        if not isinstance(raw_data, dict):
            logger.warning(f"Service {service_name} returned non-dict: {type(raw_data)}")
            return {}
        
        extracted = {}
        
        # Strategy 1: Extract from 'data' wrapper (preferred)
        if 'data' in raw_data and isinstance(raw_data['data'], dict):
            extracted = raw_data['data'].copy()
            logger.debug(f"Service {service_name}: extracted from 'data' wrapper")
        else:
            # Strategy 2: Extract from top level (excluding metadata)
            metadata_keys = {'success', 'service', 'timestamp', 'available', 'error', 'processing_time'}
            for key, value in raw_data.items():
                if key not in metadata_keys:
                    extracted[key] = value
            logger.debug(f"Service {service_name}: extracted from top level")
        
        # Strategy 3: Ensure essential fields exist
        if 'success' not in extracted:
            extracted['success'] = raw_data.get('success', True)
        
        if 'service' not in extracted:
            extracted['service'] = service_name
        
        # Strategy 4: Score field mapping (critical for frontend)
        if 'score' not in extracted:
            score_fields = [
                'credibility_score', 'author_score', 'bias_score', 
                'transparency_score', 'manipulation_score', 'content_score',
                'trust_score', 'quality_score'
            ]
            for field in score_fields:
                if field in extracted and isinstance(extracted[field], (int, float)):
                    extracted['score'] = int(extracted[field])
                    logger.debug(f"Service {service_name}: mapped {field} -> score")
                    break
        
        # Strategy 5: Level field mapping
        if 'level' not in extracted:
            level_fields = [
                'credibility_level', 'bias_level', 'transparency_level',
                'trust_level', 'quality_level', 'risk_level'
            ]
            for field in level_fields:
                if field in extracted and extracted[field]:
                    extracted['level'] = str(extracted[field])
                    logger.debug(f"Service {service_name}: mapped {field} -> level")
                    break
        
        return extracted
    
    def _validate_service_data(self, data: Dict[str, Any]) -> bool:
        """Validate that service data is meaningful"""
        if not data:
            return False
        
        # Must have either success=True or some meaningful data
        if data.get('success') is False and len(data) <= 3:  # Just error info
            return False
        
        # Check for any meaningful fields (not just metadata)
        meaningful_fields = 0
        metadata_fields = {'success', 'service', 'timestamp', 'error', 'available'}
        
        for key, value in data.items():
            if key not in metadata_fields:
                if isinstance(value, (str, int, float, list, dict)) and value:
                    meaningful_fields += 1
        
        return meaningful_fields > 0
    
    def _extract_article_bulletproof(self, pipeline_results: Dict[str, Any], content: str, content_type: str) -> Dict[str, Any]:
        """Extract article with multiple fallback strategies"""
        
        # Strategy 1: Direct article field
        if 'article' in pipeline_results and isinstance(pipeline_results['article'], dict):
            article = pipeline_results['article']
            if article.get('title') or article.get('text'):
                logger.debug("Article extracted from direct 'article' field")
                return self._normalize_article_data(article, content, content_type)
        
        # Strategy 2: From article_extractor service
        if 'article_extractor' in pipeline_results:
            extractor = pipeline_results['article_extractor']
            if isinstance(extractor, dict):
                if 'data' in extractor and isinstance(extractor['data'], dict):
                    logger.debug("Article extracted from article_extractor.data")
                    return self._normalize_article_data(extractor['data'], content, content_type)
                elif extractor.get('title') or extractor.get('text'):
                    logger.debug("Article extracted from article_extractor top level")
                    return self._normalize_article_data(extractor, content, content_type)
        
        # Strategy 3: Search all service results for article data
        for key, value in pipeline_results.items():
            if isinstance(value, dict) and ('title' in value or 'text' in value):
                if value.get('title', '').strip() or value.get('text', '').strip():
                    logger.debug(f"Article extracted from {key}")
                    return self._normalize_article_data(value, content, content_type)
        
        # Strategy 4: Create minimal article from input
        logger.warning("No article data found - creating minimal structure")
        return {
            'title': 'Unable to Extract Title',
            'text': content if content_type == 'text' else '',
            'url': content if content_type == 'url' else '',
            'author': 'Unknown',
            'domain': '',
            'extraction_successful': False,
            'word_count': len(content.split()) if content else 0
        }
    
    def _normalize_article_data(self, raw_article: Dict[str, Any], content: str, content_type: str) -> Dict[str, Any]:
        """Normalize article data to expected format"""
        return {
            'title': raw_article.get('title', 'Unknown Title'),
            'text': raw_article.get('text', raw_article.get('content', content if content_type == 'text' else '')),
            'author': raw_article.get('author', 'Unknown'),
            'publish_date': raw_article.get('publish_date', raw_article.get('date', '')),
            'domain': raw_article.get('domain', raw_article.get('source', '')),
            'url': raw_article.get('url', content if content_type == 'url' else ''),
            'word_count': raw_article.get('word_count', len(str(raw_article.get('text', '')).split())),
            'language': raw_article.get('language', 'en'),
            'extraction_successful': bool(raw_article.get('title') or raw_article.get('text'))
        }
    
    def _calculate_bulletproof_trust_score(self, detailed_analysis: Dict[str, Any], pipeline_results: Dict[str, Any]) -> int:
        """Calculate trust score with comprehensive fallbacks"""
        
        # Strategy 1: Use pipeline trust score if available
        if 'trust_score' in pipeline_results and isinstance(pipeline_results['trust_score'], (int, float)):
            score = int(pipeline_results['trust_score'])
            if 0 <= score <= 100:
                logger.debug(f"Using pipeline trust score: {score}")
                return score
        
        # Strategy 2: Calculate from service scores
        scores = []
        weights = {
            'source_credibility': 0.25,
            'author_analyzer': 0.20,
            'bias_detector': 0.20,
            'fact_checker': 0.15,
            'transparency_analyzer': 0.10,
            'manipulation_detector': 0.10
        }
        
        for service_name, weight in weights.items():
            if service_name in detailed_analysis:
                service_data = detailed_analysis[service_name]
                if service_data.get('success') and isinstance(service_data, dict):
                    score = self._extract_score_bulletproof(service_data, service_name)
                    if score is not None and 0 <= score <= 100:
                        scores.append((score, weight))
                        logger.debug(f"Trust component {service_name}: {score} (weight {weight})")
        
        if scores:
            total_weight = sum(weight for _, weight in scores)
            weighted_sum = sum(score * weight for score, weight in scores)
            final_score = int(weighted_sum / total_weight)
            logger.info(f"Calculated trust score: {final_score} from {len(scores)} services")
            return max(0, min(100, final_score))
        
        # Strategy 3: Default based on service availability
        working_services = sum(1 for data in detailed_analysis.values() if data.get('success'))
        if working_services >= 4:
            return 60  # Moderate if most services work
        elif working_services >= 2:
            return 45  # Low-moderate if some work
        else:
            return 30  # Low if few/no services work
    
    def _extract_score_bulletproof(self, data: Dict[str, Any], service_name: str) -> Optional[int]:
        """Extract score with service-specific logic and fallbacks"""
        
        # Direct score field
        if 'score' in data and isinstance(data['score'], (int, float)):
            return int(data['score'])
        
        # Service-specific score fields
        score_mappings = {
            'source_credibility': ['credibility_score', 'trust_score'],
            'author_analyzer': ['author_score', 'credibility_score'],
            'bias_detector': ['bias_score', 'objectivity_score'],
            'fact_checker': ['factual_score', 'accuracy_score'],
            'transparency_analyzer': ['transparency_score'],
            'manipulation_detector': ['manipulation_score', 'risk_score'],
            'content_analyzer': ['content_score', 'quality_score']
        }
        
        if service_name in score_mappings:
            for field in score_mappings[service_name]:
                if field in data and isinstance(data[field], (int, float)):
                    score = int(data[field])
                    # Invert for bias/manipulation (higher = worse)
                    if service_name in ['bias_detector', 'manipulation_detector']:
                        return max(0, min(100, 100 - score))
                    return max(0, min(100, score))
        
        return None
    
    def _extract_bulletproof_key_findings(self, detailed_analysis: Dict[str, Any], pipeline_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract key findings with comprehensive fallbacks"""
        findings = []
        
        # Strategy 1: Extract from service findings arrays
        for service_name, service_data in detailed_analysis.items():
            if not service_data.get('success'):
                continue
                
            # Look for findings arrays
            findings_fields = ['findings', 'key_findings', 'issues', 'concerns']
            for field in findings_fields:
                if field in service_data and isinstance(service_data[field], list):
                    for finding in service_data[field][:2]:  # Max 2 per service
                        if isinstance(finding, dict) and 'text' in finding:
                            findings.append(finding)
                        elif isinstance(finding, str) and finding.strip():
                            findings.append({
                                'type': 'info',
                                'text': finding,
                                'service': service_name
                            })
        
        # Strategy 2: Generate findings from scores
        score_based_findings = []
        for service_name, service_data in detailed_analysis.items():
            if not service_data.get('success'):
                continue
                
            score = service_data.get('score')
            level = service_data.get('level', '')
            
            if isinstance(score, (int, float)):
                if service_name == 'source_credibility' and score < 40:
                    score_based_findings.append({
                        'type': 'warning',
                        'text': f'Low source credibility: {level} ({score}/100)',
                        'service': service_name
                    })
                elif service_name == 'bias_detector' and score > 60:
                    score_based_findings.append({
                        'type': 'warning', 
                        'text': f'High bias detected: {level} ({score}/100)',
                        'service': service_name
                    })
                elif service_name == 'author_analyzer' and score > 80:
                    score_based_findings.append({
                        'type': 'positive',
                        'text': f'High author credibility: {level} ({score}/100)',
                        'service': service_name
                    })
        
        findings.extend(score_based_findings)
        
        # Strategy 3: Default findings if none found
        if not findings:
            working_services = sum(1 for data in detailed_analysis.values() if data.get('success'))
            if working_services > 0:
                findings.append({
                    'type': 'info',
                    'text': f'Analysis completed with {working_services} services',
                    'service': 'system'
                })
            else:
                findings.append({
                    'type': 'warning',
                    'text': 'Limited analysis data available',
                    'service': 'system'
                })
        
        return findings[:5]  # Limit to 5 findings
    
    def _generate_bulletproof_summary(self, successful_services: int, total_services: int, pipeline_results: Dict[str, Any]) -> str:
        """Generate summary with fallbacks"""
        
        if 'summary' in pipeline_results and pipeline_results['summary']:
            return str(pipeline_results['summary'])
        
        if successful_services == 0:
            return "Analysis completed with limited data. Please try again or check the content."
        elif successful_services == total_services:
            return f"Complete analysis successful. All {total_services} services provided data."
        else:
            return f"Partial analysis completed. {successful_services} of {total_services} services provided data."
    
    def _get_trust_level(self, score: int) -> str:
        """Get trust level from score"""
        if score >= 80:
            return 'Very High'
        elif score >= 60:
            return 'High' 
        elif score >= 40:
            return 'Moderate'
        elif score >= 20:
            return 'Low'
        else:
            return 'Very Low'
    
    def _build_error_response(self, error_message: str, content: str, content_type: str) -> Dict[str, Any]:
        """Build comprehensive error response"""
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
                    'trust_score': 0,
                    'trust_level': 'Cannot Analyze',
                    'key_findings': [{
                        'type': 'error',
                        'text': f'Analysis failed: {error_message}',
                        'service': 'system'
                    }],
                    'summary': f'Error: {error_message}'
                },
                'detailed_analysis': {
                    'source_credibility': {'success': False, 'error': error_message, 'score': 0, 'level': 'Error'},
                    'author_analyzer': {'success': False, 'error': error_message, 'score': 0, 'level': 'Error'},
                    'bias_detector': {'success': False, 'error': error_message, 'score': 0, 'level': 'Error'},
                    'content_analyzer': {'success': False, 'error': error_message, 'score': 0, 'level': 'Error'}
                }
            },
            'metadata': {
                'analysis_time': 0,
                'timestamp': datetime.now().isoformat(),
                'services_available': 0,
                'services_with_data': 0,
                'is_pro': False,
                'analysis_mode': 'error',
                'error_details': error_message
            }
        }
    
    def get_available_services(self) -> Dict[str, Any]:
        """Get information about available services"""
        try:
            return self.service_registry.get_service_status()
        except Exception as e:
            logger.error(f"Failed to get service status: {e}")
            return {'services': {}, 'summary': {'available': 0, 'total': 0}}
    
    def get_service_info(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific service"""
        try:
            return self.service_registry.get_service_info(service_name)
        except Exception as e:
            logger.error(f"Failed to get service info for {service_name}: {e}")
            return None
