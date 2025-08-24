"""
News Analyzer API - Main Flask Application
FIXED: Better error handling for extraction failures
"""
import os
import sys
import logging
import time
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List
import json

# Flask imports
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Application imports
from config import Config
from services.news_analyzer import NewsAnalyzer
from services.service_registry import get_service_registry

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS
CORS(app, origins=["*"])

# Setup rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour", "20 per minute"],
    storage_uri="memory://"
)

# Initialize services
news_analyzer = NewsAnalyzer()

# Performance tracking storage
performance_stats = {}

# Debug information storage
debug_info = {
    'requests': [],
    'errors': [],
    'service_timings': {}
}

# FIXED: Enhanced service data extraction that preserves all fields
def extract_service_data(service_result: Dict[str, Any]) -> Dict[str, Any]:
    """Extract meaningful data from service result - FIXED VERSION"""
    if not isinstance(service_result, dict):
        return {}
    
    # If service result has 'data' field, extract it
    if 'data' in service_result and isinstance(service_result['data'], dict):
        extracted_data = service_result['data'].copy()
        
        # CRITICAL FIX: Ensure commonly expected fields are at top level
        # This makes the data accessible to frontend without deep nesting
        
        # For content_analyzer
        if 'content_score' in extracted_data:
            extracted_data['score'] = extracted_data.get('score', extracted_data['content_score'])
            extracted_data['quality_score'] = extracted_data.get('content_score')
        
        # For transparency_analyzer
        if 'transparency_score' in extracted_data:
            extracted_data['score'] = extracted_data.get('score', extracted_data['transparency_score'])
        
        # Ensure all services have a score field
        if 'score' not in extracted_data:
            # Try to find any score-like field
            for key in ['quality_score', 'credibility_score', 'bias_score', 'transparency_score']:
                if key in extracted_data:
                    extracted_data['score'] = extracted_data[key]
                    break
        
        return extracted_data
    
    # Otherwise, extract all fields except metadata
    exclude_fields = {'success', 'service', 'timestamp', 'available', 'error', 'processing_time'}
    extracted = {k: v for k, v in service_result.items() if k not in exclude_fields}
    
    # Ensure score field exists
    if 'score' not in extracted:
        for key in ['quality_score', 'credibility_score', 'bias_score', 'transparency_score']:
            if key in extracted:
                extracted['score'] = extracted[key]
                break
    
    return extracted

# Helper to identify service results in pipeline output
def is_service_result(key: str, value: Any) -> bool:
    """Check if a key-value pair is a service result"""
    # Known non-service keys
    non_service_keys = {
        'success', 'trust_score', 'trust_level', 'summary', 
        'pipeline_metadata', 'errors', 'article', 'services_available', 
        'is_pro', 'analysis_mode'
    }
    
    if key in non_service_keys:
        return False
    
    # Check if value looks like a service result
    if isinstance(value, dict):
        # Service results typically have 'success' field
        if 'success' in value:
            return True
        # Or have typical service data fields
        service_indicators = {'score', 'analysis', 'data', 'results', 'level', 'findings'}
        if any(indicator in value for indicator in service_indicators):
            return True
    
    return False

# MAIN ROUTES

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    registry = get_service_registry()
    service_status = registry.get_service_status()
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': service_status['services'],
        'summary': service_status['summary']
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Main analysis endpoint - FIXED version with better error handling
    Accepts: { "url": "..." } or { "text": "..." }
    """
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Log the request
        logger.info(f"Analysis request received with keys: {list(data.keys())}")
        
        # Validate input - support both url and text
        url = data.get('url')
        text = data.get('text')
        
        if not url and not text:
            return jsonify({
                'success': False,
                'error': 'Please provide either a URL or text to analyze'
            }), 400
        
        # Determine content type
        content = url if url else text
        content_type = 'url' if url else 'text'
        
        # Check for pro mode
        pro_mode = data.get('pro_mode', False) or data.get('is_pro', False)
        
        # Run analysis with timing
        start_time = time.time()
        
        try:
            # Get results from pipeline
            pipeline_results = news_analyzer.analyze(content, content_type, pro_mode)
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            return jsonify({
                'success': False,
                'error': f'Analysis failed: {str(e)}'
            }), 500
        
        total_time = time.time() - start_time
        
        # Check if extraction failed
        if not pipeline_results.get('success', False):
            # Look for specific error information
            error_msg = pipeline_results.get('error', 'Unknown error')
            
            # Check if article extraction failed
            if 'article_extractor' in pipeline_results:
                extractor_result = pipeline_results['article_extractor']
                if not extractor_result.get('success', False):
                    error_msg = extractor_result.get('error', 'Failed to extract article content')
            
            # Return a proper error response with partial data
            return jsonify({
                'success': False,
                'error': error_msg,
                'data': {
                    'article': {
                        'title': 'Extraction Failed',
                        'url': content if content_type == 'url' else '',
                        'text': content if content_type == 'text' else '',
                        'extraction_successful': False,
                        'error': error_msg
                    },
                    'analysis': {
                        'trust_score': 0,
                        'trust_level': 'Cannot Analyze',
                        'key_findings': [{
                            'type': 'error',
                            'text': 'Unable to extract article content',
                            'explanation': error_msg
                        }],
                        'summary': f'Analysis failed: {error_msg}'
                    },
                    'detailed_analysis': {}
                },
                'metadata': {
                    'analysis_time': total_time,
                    'timestamp': datetime.now().isoformat(),
                    'error_details': error_msg
                }
            }), 200  # Return 200 with error in response body for better frontend handling
        
        # Extract service results from pipeline output
        service_results = {}
        article_data = None
        
        # Log what we got from pipeline
        logger.info(f"Pipeline results keys: {list(pipeline_results.keys())}")
        
        for key, value in pipeline_results.items():
            if key == 'article':
                article_data = value
            elif is_service_result(key, value):
                # Extract the actual data from service result
                service_data = extract_service_data(value)
                if service_data:
                    service_results[key] = service_data
                    logger.info(f"Extracted {key} data with {len(service_data)} fields")
                    # Log first few fields for debugging
                    for field_name in list(service_data.keys())[:5]:
                        logger.info(f"  - {key}.{field_name}: {type(service_data[field_name]).__name__}")
        
        # Ensure we have article data
        if not article_data:
            # Try to get from article_extractor
            if 'article_extractor' in pipeline_results:
                article_data = extract_service_data(pipeline_results['article_extractor'])
            
            if not article_data or not article_data.get('text'):
                # Create minimal article data
                article_data = {
                    'title': 'Unknown Title',
                    'url': content if content_type == 'url' else '',
                    'text': content if content_type == 'text' else '',
                    'extraction_successful': False,
                    'error': 'Could not extract article content'
                }
        
        # Build the response in the format frontend expects
        response_data = {
            'success': True,  # Overall request succeeded even if some services failed
            'data': {
                'article': article_data,
                'analysis': {
                    'trust_score': pipeline_results.get('trust_score', 50),
                    'trust_level': pipeline_results.get('trust_level', 'Unknown'),
                    'key_findings': extract_key_findings(service_results),
                    'summary': pipeline_results.get('summary', 'Analysis completed')
                },
                'detailed_analysis': service_results
            },
            'metadata': {
                'analysis_time': total_time,
                'timestamp': datetime.now().isoformat(),
                'pipeline_metadata': pipeline_results.get('pipeline_metadata', {}),
                'services_available': len(service_results),
                'is_pro': pipeline_results.get('is_pro', False),
                'analysis_mode': pipeline_results.get('analysis_mode', 'basic')
            }
        }
        
        # Add warnings if any services failed
        if pipeline_results.get('errors'):
            response_data['warnings'] = pipeline_results['errors']
        
        # Log success
        logger.info(f"Analysis completed in {total_time:.2f}s")
        logger.info(f"Services included: {list(service_results.keys())}")
        logger.info("=" * 80)
        logger.info("FINAL detailed_analysis structure:")
        for service_name, service_data in service_results.items():
            logger.info(f"{service_name}:")
            for key in list(service_data.keys())[:5]:
                value = service_data[key]
                if isinstance(value, (str, int, float, bool)):
                    logger.info(f"  - {key}: {value}")
                else:
                    logger.info(f"  - {key}: {type(value).__name__}")
        logger.info("=" * 80)
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Unexpected error in analyze endpoint: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred during analysis',
            'data': {
                'article': {
                    'title': 'Error',
                    'extraction_successful': False,
                    'error': str(e)
                },
                'analysis': {
                    'trust_score': 0,
                    'trust_level': 'Error',
                    'key_findings': [],
                    'summary': 'Analysis could not be completed'
                },
                'detailed_analysis': {}
            }
        }), 200

@app.route('/api/debug/test-extraction', methods=['POST'])
def test_extraction():
    """Debug endpoint to test article extraction directly"""
    try:
        data = request.get_json() or {}
        url = data.get('url', 'https://www.reuters.com/technology/')
        
        registry = get_service_registry()
        
        # Test if article_extractor is available
        if not registry.is_service_available('article_extractor'):
            return jsonify({
                'success': False,
                'error': 'Article extractor service not available',
                'service_status': registry.get_service_status()
            })
        
        # Try to extract
        result = registry.analyze_with_service('article_extractor', {'url': url})
        
        return jsonify({
            'success': result.get('success', False),
            'url': url,
            'result': result,
            'extracted_fields': list(result.keys()) if isinstance(result, dict) else []
        })
        
    except Exception as e:
        logger.error(f"Extraction test error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        })

@app.route('/api/debug/test-services-data', methods=['POST'])
def test_services_data():
    """Debug endpoint to check what data services are actually returning"""
    try:
        data = request.get_json() or {}
        test_text = data.get('text', """
        The president announced new economic policies today. According to a government report,
        unemployment has decreased by 2.5% this quarter. The author, John Smith, cited multiple
        sources including the Bureau of Labor Statistics. "This is encouraging news," said the
        Treasury Secretary in a press conference. However, some economists argue these numbers
        don't tell the full story. The methodology used in the study has been questioned by critics.
        Contact us at editor@example.com for more information.
        """)
        
        registry = get_service_registry()
        results = {}
        
        # Test each service individually
        test_data = {
            'text': test_text,
            'title': 'Test Article for Debugging',
            'author': 'John Smith',
            'domain': 'example.com',
            'url': 'https://example.com/test'
        }
        
        services_to_test = ['content_analyzer', 'transparency_analyzer', 'author_analyzer']
        
        for service_name in services_to_test:
            if registry.is_service_available(service_name):
                result = registry.analyze_with_service(service_name, test_data)
                
                # Extract the data
                extracted = extract_service_data(result)
                
                results[service_name] = {
                    'raw_result': result,
                    'extracted_data': extracted,
                    'has_score': 'score' in extracted,
                    'score_value': extracted.get('score'),
                    'all_keys': list(extracted.keys()) if extracted else [],
                    'success': result.get('success', False)
                }
            else:
                results[service_name] = {
                    'error': 'Service not available'
                }
        
        return jsonify({
            'success': True,
            'services_tested': results,
            'test_text_length': len(test_text)
        })
        
    except Exception as e:
        logger.error(f"Service data test error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        })

# Helper functions

def extract_key_findings(service_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract key findings from service results"""
    findings = []
    
    # Check source credibility
    if 'source_credibility' in service_results:
        data = service_results['source_credibility']
        score = data.get('credibility_score', data.get('score', 0))
        if score < 60:
            findings.append({
                'type': 'warning',
                'text': f'Low source credibility score: {score}/100',
                'service': 'source_credibility'
            })
    
    # Check bias
    if 'bias_detector' in service_results:
        data = service_results['bias_detector']
        bias_score = data.get('bias_score', data.get('score', 0))
        if bias_score > 60:
            findings.append({
                'type': 'warning', 
                'text': f'High bias detected: {bias_score}/100',
                'service': 'bias_detector'
            })
    
    # Check transparency
    if 'transparency_analyzer' in service_results:
        data = service_results['transparency_analyzer']
        transparency_score = data.get('transparency_score', data.get('score', 0))
        if transparency_score < 50:
            findings.append({
                'type': 'warning',
                'text': f'Low transparency: {transparency_score}/100',
                'service': 'transparency_analyzer'
            })
    
    # Check content quality
    if 'content_analyzer' in service_results:
        data = service_results['content_analyzer']
        quality_score = data.get('content_score', data.get('quality_score', data.get('score', 0)))
        if quality_score < 50:
            findings.append({
                'type': 'info',
                'text': f'Content quality concerns: {quality_score}/100',
                'service': 'content_analyzer'
            })
    
    return findings[:5]  # Return top 5 findings

# API Status and debugging endpoints

@app.route('/api/status')
def api_status():
    """Get API status and service availability"""
    return jsonify(news_analyzer.get_available_services())

@app.route('/api/debug/services')
def debug_services():
    """Debug endpoint to check service status"""
    registry = get_service_registry()
    status = registry.get_service_status()
    
    # Add more debug info
    status['registered_services'] = list(registry._services.keys())
    status['failed_services'] = registry._failed_services
    
    return jsonify(status)

@app.route('/api/debug/analyze-test', methods=['GET', 'POST'])
def debug_analyze_test():
    """Test analysis with a sample URL"""
    test_url = "https://www.reuters.com/technology/artificial-intelligence/openai-allows-employees-sell-shares-tender-offer-led-softbank-2024-11-27/"
    
    result = news_analyzer.analyze(test_url, 'url', False)
    
    # Extract service results for easier debugging
    service_data = {}
    for key, value in result.items():
        if is_service_result(key, value):
            service_data[key] = {
                'success': value.get('success', False),
                'has_data': 'data' in value,
                'data_keys': list(value.get('data', {}).keys()) if isinstance(value.get('data'), dict) else [],
                'error': value.get('error')
            }
    
    return jsonify({
        'test_url': test_url,
        'success': result.get('success', False),
        'trust_score': result.get('trust_score'),
        'services_found': list(service_data.keys()),
        'service_details': service_data,
        'full_result': result
    })

@app.route('/api/debug/clear-cache', methods=['POST'])
def clear_cache():
    """Clear any caches (placeholder for future implementation)"""
    return jsonify({
        'success': True,
        'message': 'Cache cleared (if implemented)'
    })

# Static file serving for service pages
@app.route('/<path:filename>')
def serve_static_html(filename):
    """Serve static HTML files from templates directory"""
    if filename.endswith('.html'):
        return render_template(filename)
    return send_from_directory('static', filename)

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Development server
    app.run(debug=True, host='0.0.0.0', port=5000)
