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
            'response_time_ms': ResponseBuilder._get_response_time(),
            'api_version': Config.API_VERSION
        }
        
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
        
        # Extract data from each service result
        for service_name, result in analysis_results.items():
            if isinstance(result, dict) and result.get('success'):
                # Extract the data field if it exists
                if 'data' in result:
                    extracted_results[service_name] = result['data']
                else:
                    # If no data field, use the entire result (legacy format)
                    extracted_results[service_name] = result
            else:
                # Service failed or returned empty result
                extracted_results[service_name] = {}
        
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
            'detailed_analysis': {
                'source_credibility': extracted_results.get('source_credibility', {}),
                'author_analysis': extracted_results.get('author_analysis', {}),
                'bias_analysis': extracted_results.get('bias_analysis', {}),
                'transparency_analysis': extracted_results.get('transparency_analysis', {}),
                'fact_checks': extracted_results.get('fact_checks', []),
                'manipulation_analysis': extracted_results.get('manipulation_analysis', extracted_results.get('persuasion_analysis', {})),
                'content_analysis': extracted_results.get('content_analysis', {})
            }
        }
        
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
        """Extract key findings from analysis results"""
        findings = []
        
        # Source credibility finding
        source_cred = analysis_results.get('source_credibility', {})
        if source_cred and source_cred.get('rating'):
            findings.append({
                'type': 'source_credibility',
                'title': 'Source Credibility',
                'finding': f"{source_cred.get('rating')} credibility source",
                'impact': 'high' if source_cred.get('rating') in ['Very Low', 'Low'] else 'medium'
            })
        
        # Author finding
        author = analysis_results.get('author_analysis', {})
        if author and author.get('level'):
            findings.append({
                'type': 'author',
                'title': 'Author Credibility',
                'finding': f"{author.get('level')} author credibility",
                'impact': 'high' if author.get('score', 0) < 40 else 'medium'
            })
        
        # Bias finding
        bias = analysis_results.get('bias_analysis', {})
        if bias and bias.get('political_lean') is not None:
            lean = bias.get('political_lean', 0)
            if abs(lean) > 0.5:
                findings.append({
                    'type': 'bias',
                    'title': 'Political Bias',
                    'finding': f"Strong {'right' if lean > 0 else 'left'}-leaning bias detected",
                    'impact': 'high'
                })
        
        # Manipulation finding
        manipulation = analysis_results.get('manipulation_analysis', {})
        if manipulation and manipulation.get('manipulation_score', 0) > 50:
            findings.append({
                'type': 'manipulation',
                'title': 'Manipulation Tactics',
                'finding': 'Significant manipulation tactics detected',
                'impact': 'high'
            })
        
        # Fact checking finding
        fact_checks = analysis_results.get('fact_checks', [])
        if fact_checks:
            false_claims = sum(1 for fc in fact_checks if 'false' in str(fc.get('verdict', '')).lower())
            if false_claims > 0:
                findings.append({
                    'type': 'fact_check',
                    'title': 'Fact Check',
                    'finding': f"{false_claims} false claim{'s' if false_claims > 1 else ''} identified",
                    'impact': 'high'
                })
        
        return findings
    
    @staticmethod
    def _generate_cache_key(article_data: Dict[str, Any]) -> str:
        """Generate cache key for the analysis"""
        import hashlib
        
        # Use URL or text hash as cache key
        if article_data.get('url'):
            key_source = article_data['url']
        else:
            key_source = article_data.get('text', '')[:1000]  # First 1000 chars of text
            
        return hashlib.md5(key_source.encode('utf-8')).hexdigest()
