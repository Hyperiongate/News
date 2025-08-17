"""
Response Builder - FIXED VERSION
Ensures consistent response format across all endpoints
Properly extracts data from service results
"""
import time
import json
import gzip
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from flask import Response, jsonify
import logging

from config import Config

logger = logging.getLogger(__name__)


class ResponseBuilder:
    """Build standardized API responses"""
    
    @staticmethod
    def success(data: Dict[str, Any], 
                message: Optional[str] = None,
                metadata: Optional[Dict[str, Any]] = None,
                status_code: int = 200) -> Response:
        """
        Build successful response
        
        Args:
            data: Response data
            message: Optional success message
            metadata: Optional metadata
            status_code: HTTP status code
            
        Returns:
            Flask Response object
        """
        response = {
            'success': True,
            'data': data,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        if message:
            response['message'] = message
            
        if metadata or Config.RESPONSE_FORMAT['include_metadata']:
            response['metadata'] = ResponseBuilder._build_metadata(metadata)
        
        # Check response size and compress if needed
        response_json = json.dumps(response)
        size_mb = len(response_json.encode('utf-8')) / (1024 * 1024)
        
        if Config.RESPONSE_FORMAT['compress_large_responses'] and size_mb > 1:
            return ResponseBuilder._compressed_response(response, status_code)
        
        return jsonify(response), status_code
    
    @staticmethod
    def error(error: Union[str, Exception, Dict[str, Any]], 
              status_code: int = 400,
              error_code: Optional[str] = None,
              details: Optional[Dict[str, Any]] = None) -> Response:
        """
        Build error response
        
        Args:
            error: Error message, exception, or error dict
            status_code: HTTP status code
            error_code: Machine-readable error code
            details: Additional error details
            
        Returns:
            Flask Response object
        """
        # Extract error message
        if isinstance(error, Exception):
            error_message = str(error)
            error_type = error.__class__.__name__
        elif isinstance(error, dict):
            error_message = error.get('message', 'Unknown error')
            error_type = error.get('type', 'Error')
            error_code = error_code or error.get('code')
            details = details or error.get('details')
        else:
            error_message = str(error)
            error_type = 'Error'
        
        response = {
            'success': False,
            'error': {
                'message': error_message,
                'type': error_type,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        }
        
        if error_code:
            response['error']['code'] = error_code
            
        if details:
            response['error']['details'] = details
            
        if Config.RESPONSE_FORMAT['include_debug_info'] and Config.DEBUG:
            response['error']['debug'] = {
                'traceback': ResponseBuilder._get_traceback(),
                'request_id': ResponseBuilder._get_request_id()
            }
        
        logger.error(f"API Error: {error_type} - {error_message}")
        
        return jsonify(response), status_code
    
    @staticmethod
    def partial_success(successful_data: Dict[str, Any],
                       failures: List[Dict[str, Any]],
                       message: Optional[str] = None) -> Response:
        """
        Build response for partial success (some operations succeeded, some failed)
        
        Args:
            successful_data: Data from successful operations
            failures: List of failure details
            message: Optional message
            
        Returns:
            Flask Response object
        """
        response = {
            'success': 'partial',
            'data': successful_data,
            'failures': failures,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        if message:
            response['message'] = message
            
        return jsonify(response), 207  # 207 Multi-Status
    
    @staticmethod
    def _build_metadata(custom_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Build metadata for response"""
        metadata = {
            'response_time_ms': ResponseBuilder._get_response_time()
        }
        
        # Add API version if it exists
        if hasattr(Config, 'API_VERSION'):
            metadata['api_version'] = Config.API_VERSION
        
        if custom_metadata:
            metadata.update(custom_metadata)
            
        return metadata
    
    @staticmethod
    def _compressed_response(data: Dict[str, Any], status_code: int) -> Response:
        """Create compressed response"""
        json_str = json.dumps(data)
        compressed = gzip.compress(json_str.encode('utf-8'))
        
        response = Response(compressed, status=status_code)
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Encoding'] = 'gzip'
        
        return response
    
    @staticmethod
    def _get_response_time() -> int:
        """Get response time in milliseconds"""
        # This should be set by middleware
        return getattr(ResponseBuilder, '_start_time', 0)
    
    @staticmethod
    def _get_request_id() -> str:
        """Get request ID for tracking"""
        # This should be set by middleware
        return getattr(ResponseBuilder, '_request_id', 'unknown')
    
    @staticmethod
    def _get_traceback() -> Optional[str]:
        """Get exception traceback for debugging"""
        import traceback
        import sys
        
        exc_info = sys.exc_info()
        if exc_info[0]:
            return ''.join(traceback.format_exception(*exc_info))
        return None


class AnalysisResponseBuilder(ResponseBuilder):
    """Specialized response builder for analysis endpoints"""
    
    @staticmethod
    def build_analysis_response(analysis_results: Dict[str, Any],
                               article_data: Dict[str, Any],
                               processing_time: float,
                               services_used: List[str]) -> Response:
        """
        Build standardized analysis response
        
        Args:
            analysis_results: Results from all analyzers (including service results)
            article_data: Extracted article data
            processing_time: Total processing time
            services_used: List of services that were used
            
        Returns:
            Flask Response object
        """
        logger.info("=" * 80)
        logger.info("AnalysisResponseBuilder.build_analysis_response called")
        logger.info(f"analysis_results keys: {list(analysis_results.keys())}")
        logger.info(f"article_data keys: {list(article_data.keys())}")
        logger.info(f"services_used: {services_used}")
        logger.info("=" * 80)
        
        # CRITICAL FIX: The analysis_results contains ALL pipeline results including service results
        # Service results are stored directly with their service names as keys
        
        # Extract service results from the analysis_results
        service_results = {}
        metadata_fields = ['success', 'trust_score', 'trust_level', 'summary', 'pipeline_metadata', 
                          'errors', 'article', 'services_available', 'is_pro', 'analysis_mode']
        
        # Check all keys in analysis_results
        for key, value in analysis_results.items():
            # If it's not a metadata field and it's a dict, it's likely a service result
            if key not in metadata_fields and isinstance(value, dict):
                # Additional check: service results should have 'success' field
                if 'success' in value or 'data' in value or key in services_used:
                    service_results[key] = value
                    logger.info(f"Found service result: {key} (has success: {'success' in value})")
        
        logger.info(f"Extracted {len(service_results)} service results")
        
        # Now build the detailed_analysis section with actual data
        detailed_analysis = {}
        
        # Process each service that was used
        for service_name in services_used:
            logger.info(f"Processing service: {service_name}")
            
            # Try to find the service result
            result = None
            
            # First check if it's directly in analysis_results
            if service_name in analysis_results:
                result = analysis_results[service_name]
                logger.info(f"Found {service_name} in analysis_results directly")
            # Then check service_results
            elif service_name in service_results:
                result = service_results[service_name]
                logger.info(f"Found {service_name} in extracted service_results")
            
            if result:
                # Extract the actual data from the service result
                if result.get('success', False):
                    # If the service has a 'data' field, use it
                    if 'data' in result and isinstance(result['data'], dict):
                        detailed_analysis[service_name] = result['data']
                        logger.info(f"Added {service_name} data from 'data' field: {list(result['data'].keys())}")
                    else:
                        # Otherwise, extract relevant fields (exclude metadata)
                        service_data = {}
                        exclude_fields = ['service', 'success', 'available', 'timestamp', 'error', 'message']
                        
                        for k, v in result.items():
                            if k not in exclude_fields:
                                service_data[k] = v
                        
                        if service_data:
                            detailed_analysis[service_name] = service_data
                            logger.info(f"Added {service_name} data from result fields: {list(service_data.keys())}")
                        else:
                            # If no data found, include the whole result (minus excluded fields)
                            detailed_analysis[service_name] = {k: v for k, v in result.items() 
                                                              if k not in exclude_fields}
                            logger.warning(f"No specific data found for {service_name}, including all fields")
                else:
                    # Service failed - check if there's partial data
                    if 'data' in result:
                        detailed_analysis[service_name] = result['data']
                        logger.warning(f"Service {service_name} failed but has data")
                    else:
                        detailed_analysis[service_name] = {}
                        logger.warning(f"Service {service_name} failed with no data")
            else:
                # Service result not found
                detailed_analysis[service_name] = {}
                logger.error(f"No result found for service {service_name}")
                logger.error(f"Available keys in analysis_results: {list(analysis_results.keys())}")
        
        # Log what we're putting in detailed_analysis
        logger.info("=" * 50)
        logger.info("Final detailed_analysis structure:")
        for service, data in detailed_analysis.items():
            logger.info(f"  {service}: {list(data.keys()) if data else 'empty'}")
            # Log first few fields of each service for debugging
            if data:
                for key in list(data.keys())[:3]:
                    logger.info(f"    - {key}: {type(data[key]).__name__}")
        logger.info("=" * 50)
        
        # Extract key findings from the detailed analysis
        key_findings = AnalysisResponseBuilder._extract_key_findings(detailed_analysis)
        
        # Structure the response data
        data = {
            'article': {
                'title': article_data.get('title', 'Untitled'),
                'author': article_data.get('author', 'Unknown'),
                'publish_date': article_data.get('publish_date'),
                'url': article_data.get('url'),
                'domain': article_data.get('domain'),
                'word_count': article_data.get('word_count', 0),
                'excerpt': AnalysisResponseBuilder._create_excerpt(article_data.get('text', ''))
            },
            'analysis': {
                'trust_score': analysis_results.get('trust_score', 50),
                'trust_level': analysis_results.get('trust_level', 'Unknown'),
                'summary': analysis_results.get('summary'),
                'key_findings': key_findings
            },
            # Use the properly extracted service data
            'detailed_analysis': detailed_analysis
        }
        
        # Build metadata
        metadata = {
            'processing_time_seconds': round(processing_time, 2),
            'services_used': services_used,
            'services_available': len(services_used),
            'analysis_timestamp': datetime.utcnow().isoformat() + 'Z',
            'cache_key': AnalysisResponseBuilder._generate_cache_key(article_data)
        }
        
        # Final logging before response
        logger.info("=" * 80)
        logger.info("FINAL RESPONSE STRUCTURE:")
        logger.info(f"Article: {list(data['article'].keys())}")
        logger.info(f"Analysis: {list(data['analysis'].keys())}")
        logger.info(f"Detailed Analysis Services: {list(data['detailed_analysis'].keys())}")
        logger.info(f"Metadata: {list(metadata.keys())}")
        logger.info("=" * 80)
        
        return ResponseBuilder.success(
            data=data,
            message="Analysis completed successfully",
            metadata=metadata
        )
    
    @staticmethod
    def _create_excerpt(text: str, max_length: int = 200) -> str:
        """Create article excerpt"""
        if not text:
            return ""
        
        # Clean and truncate
        excerpt = text.strip()
        if len(excerpt) > max_length:
            excerpt = excerpt[:max_length].rsplit(' ', 1)[0] + '...'
            
        return excerpt
    
    @staticmethod
    def _extract_key_findings(analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract key findings from analysis results - FIXED to use correct service names"""
        findings = []
        
        # Source credibility finding
        source_cred = analysis_results.get('source_credibility', {})
        if source_cred and source_cred.get('credibility_score') is not None:
            score = source_cred.get('credibility_score', 0)
            level = source_cred.get('credibility_level', 'Unknown')
            severity = 'high' if score < 40 else 'medium' if score < 70 else 'low'
            findings.append({
                'type': 'source_credibility',
                'severity': severity,
                'text': f"Source has {level} credibility (score: {score}/100)",
                'finding': f"Source credibility: {level}"
            })
        
        # Author finding
        author = analysis_results.get('author_analyzer', {})
        if author and author.get('credibility_level'):
            findings.append({
                'type': 'author',
                'severity': 'high' if author.get('credibility_level') in ['Very Low', 'Low'] else 'medium',
                'text': f"Author credibility: {author.get('credibility_level')}",
                'finding': f"Author has {author.get('credibility_level')} credibility"
            })
        
        # Bias finding
        bias = analysis_results.get('bias_detector', {})
        if bias and bias.get('overall_bias'):
            severity = 'high' if bias.get('overall_bias') in ['Extreme', 'Strong'] else 'medium'
            findings.append({
                'type': 'bias',
                'severity': severity,
                'text': f"{bias.get('overall_bias')} bias detected across multiple dimensions",
                'finding': f"{bias.get('overall_bias')} bias present"
            })
        
        # Transparency finding
        transparency = analysis_results.get('transparency_analyzer', {})
        if transparency and transparency.get('transparency_score') is not None:
            score = transparency.get('transparency_score', 0)
            severity = 'high' if score < 40 else 'medium' if score < 70 else 'low'
            findings.append({
                'type': 'transparency',
                'severity': severity,
                'text': f"Transparency score: {score}/100",
                'finding': f"{'Low' if score < 40 else 'Moderate' if score < 70 else 'High'} transparency"
            })
        
        # Fact checking finding
        facts = analysis_results.get('fact_checker', {})
        if facts:
            # Try different possible field names
            claims_checked = facts.get('claims_checked') or facts.get('total_claims') or 0
            verified_count = facts.get('verified_count') or facts.get('verified_facts') or 0
            
            # Also check if verified_facts is a list
            if isinstance(facts.get('verified_facts'), list):
                verified_count = len(facts.get('verified_facts', []))
            
            if claims_checked > 0:
                percentage = (verified_count / claims_checked) * 100
                severity = 'high' if percentage < 50 else 'low' if percentage > 80 else 'medium'
                findings.append({
                    'type': 'fact_checking',
                    'severity': severity,
                    'text': f"{verified_count}/{claims_checked} claims verified ({percentage:.0f}%)",
                    'finding': f"{percentage:.0f}% of claims verified"
                })
        
        # Manipulation finding
        manipulation = analysis_results.get('manipulation_detector', {})
        if manipulation and manipulation.get('manipulation_detected') is not None:
            if manipulation.get('manipulation_detected'):
                findings.append({
                    'type': 'manipulation',
                    'severity': 'high',
                    'text': 'Potential manipulation techniques detected',
                    'finding': 'Manipulation detected'
                })
        
        # Sort by severity (high first)
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        findings.sort(key=lambda x: severity_order.get(x.get('severity', 'medium'), 1))
        
        # Limit to top 5 findings
        return findings[:5]
    
    @staticmethod
    def _generate_cache_key(article_data: Dict[str, Any]) -> str:
        """Generate cache key for article"""
        import hashlib
        
        # Use URL if available, otherwise use title+author
        if article_data.get('url'):
            key_source = article_data['url']
        else:
            key_source = f"{article_data.get('title', '')}-{article_data.get('author', '')}"
        
        return hashlib.md5(key_source.encode()).hexdigest()


# For backward compatibility
def build_response(success: bool, 
                  data: Optional[Dict[str, Any]] = None,
                  error: Optional[str] = None,
                  status_code: int = 200) -> Response:
    """Legacy response builder for backward compatibility"""
    if success:
        return ResponseBuilder.success(data or {}, status_code=status_code)
    else:
        return ResponseBuilder.error(error or "Unknown error", status_code=status_code)
