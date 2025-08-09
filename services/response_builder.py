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
            analysis_results: Results from all analyzers
            article_data: Extracted article data
            processing_time: Total processing time
            services_used: List of services that were used
            
        Returns:
            Flask Response object
        """
        # FIXED: Properly extract data from service results
        extracted_results = {}
        
        # Log what we're working with
        logger.info(f"Building response - analysis_results keys: {list(analysis_results.keys())}")
        logger.info(f"Services used: {services_used}")
        
        # Extract data from each service result
        for service_name, result in analysis_results.items():
            if isinstance(result, dict) and result.get('success'):
                # Extract the data field if it exists
                if 'data' in result:
                    extracted_results[service_name] = result['data']
                    logger.info(f"Extracted data from {service_name}")
                else:
                    # If no data field, use the entire result (legacy format)
                    extracted_results[service_name] = result
                    logger.info(f"Using full result from {service_name} (no data field)")
            else:
                # Service failed or returned empty result
                extracted_results[service_name] = {}
                logger.warning(f"Service {service_name} failed or returned empty result")
        
        # Log what we extracted
        logger.info(f"Extracted results keys: {list(extracted_results.keys())}")
        
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
                'key_findings': AnalysisResponseBuilder._extract_key_findings(extracted_results)
            },
            # FIXED: Use correct service names that match the service registry
            'detailed_analysis': {
                'source_credibility': extracted_results.get('source_credibility', {}),
                'author_analyzer': extracted_results.get('author_analyzer', {}),  # FIXED: was 'author_analysis'
                'bias_detector': extracted_results.get('bias_detector', {}),      # FIXED: was 'bias_analysis'
                'transparency_analyzer': extracted_results.get('transparency_analyzer', {}),  # FIXED: was 'transparency_analysis'
                'fact_checker': extracted_results.get('fact_checker', {}),        # FIXED: was 'fact_checks'
                'manipulation_detector': extracted_results.get('manipulation_detector', {}),  # FIXED: was 'manipulation_analysis'
                'content_analyzer': extracted_results.get('content_analyzer', {}),  # FIXED: was 'content_analysis'
                'plagiarism_detector': extracted_results.get('plagiarism_detector', {})  # Added missing service
            }
        }
        
        # Log final detailed_analysis structure
        logger.info(f"Final detailed_analysis keys: {list(data['detailed_analysis'].keys())}")
        for key, value in data['detailed_analysis'].items():
            if value:
                logger.info(f"  {key}: {type(value).__name__} with {len(value) if isinstance(value, (dict, list)) else 'scalar'} items")
        
        # Build metadata
        metadata = {
            'processing_time_seconds': round(processing_time, 2),
            'services_used': services_used,
            'services_available': len(services_used),
            'analysis_timestamp': datetime.utcnow().isoformat() + 'Z',
            'cache_key': AnalysisResponseBuilder._generate_cache_key(article_data)
        }
        
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
        if source_cred and source_cred.get('rating'):
            findings.append({
                'type': 'source_credibility',
                'severity': 'high' if source_cred.get('rating') in ['Very Low', 'Low'] else 'medium',
                'text': f"{source_cred.get('rating')} credibility source: {source_cred.get('reason', 'Based on domain analysis')}",
                'finding': f"Source has {source_cred.get('rating')} credibility"
            })
        
        # Author finding - FIXED: using 'author_analyzer' not 'author_analysis'
        author = analysis_results.get('author_analyzer', {})
        if author and author.get('credibility_level'):
            findings.append({
                'type': 'author',
                'severity': 'high' if author.get('credibility_level') in ['Very Low', 'Low'] else 'medium',
                'text': f"Author credibility: {author.get('credibility_level')}",
                'finding': f"Author has {author.get('credibility_level')} credibility"
            })
        
        # Bias finding - FIXED: using 'bias_detector' not 'bias_analysis'
        bias = analysis_results.get('bias_detector', {})
        if bias and bias.get('overall_bias'):
            severity = 'high' if bias.get('overall_bias') in ['Extreme', 'Strong'] else 'medium'
            findings.append({
                'type': 'bias',
                'severity': severity,
                'text': f"{bias.get('overall_bias')} bias detected across multiple dimensions",
                'finding': f"{bias.get('overall_bias')} bias present"
            })
        
        # Fact checking finding - FIXED: using 'fact_checker' not 'fact_checks'
        facts = analysis_results.get('fact_checker', {})
        if facts and facts.get('claims_checked'):
            verified = facts.get('verified_count', 0)
            total = facts.get('claims_checked', 0)
            if total > 0:
                percentage = (verified / total) * 100
                severity = 'negative' if percentage < 50 else 'positive' if percentage > 80 else 'warning'
                findings.append({
                    'type': 'fact_check',
                    'severity': severity,
                    'text': f"{verified} of {total} claims verified ({percentage:.0f}%)",
                    'finding': f"Fact verification: {percentage:.0f}%"
                })
        
        # Manipulation finding - using correct name
        manipulation = analysis_results.get('manipulation_detector', {})
        if manipulation and manipulation.get('manipulation_level'):
            if manipulation.get('manipulation_level') != 'None':
                findings.append({
                    'type': 'manipulation',
                    'severity': 'high',
                    'text': f"{manipulation.get('manipulation_level')} level of manipulation detected",
                    'finding': "Potential manipulation detected"
                })
        
        # Content quality finding
        content = analysis_results.get('content_analyzer', {})
        if content and content.get('quality_score'):
            score = content.get('quality_score', 0)
            if score < 50:
                findings.append({
                    'type': 'content_quality',
                    'severity': 'warning',
                    'text': f"Low content quality score: {score}/100",
                    'finding': "Content quality concerns"
                })
        
        # Transparency finding
        transparency = analysis_results.get('transparency_analyzer', {})
        if transparency and transparency.get('transparency_score'):
            score = transparency.get('transparency_score', 0)
            if score < 50:
                findings.append({
                    'type': 'transparency',
                    'severity': 'warning',
                    'text': f"Low transparency score: {score}/100",
                    'finding': "Transparency issues identified"
                })
        
        # Log findings
        logger.info(f"Extracted {len(findings)} key findings")
        
        return findings
    
    @staticmethod
    def _generate_cache_key(article_data: Dict[str, Any]) -> str:
        """Generate cache key for article"""
        import hashlib
        
        # Use URL or title as cache key base
        key_base = article_data.get('url') or article_data.get('title', '')
        return hashlib.md5(key_base.encode()).hexdigest()
