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

# Helper function to extract service data
def extract_service_data(service_result: Dict[str, Any]) -> Dict[str, Any]:
    """Extract meaningful data from service result"""
    if not isinstance(service_result, dict):
        return {}
    
    # If service result has 'data' field, use it
    if 'data' in service_result and isinstance(service_result['data'], dict):
        return service_result['data']
    
    # Otherwise, extract all fields except metadata
    exclude_fields = {'success', 'service', 'timestamp', 'available', 'error', 'processing_time'}
    return {k: v for k, v in service_result.items() if k not in exclude_fields}

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
        
        for key, value in pipeline_results.items():
            if key == 'article':
                article_data = value
            elif is_service_result(key, value):
                # Extract the actual data from service result
                service_data = extract_service_data(value)
                if service_data:
                    service_results[key] = service_data
                    logger.info(f"Extracted {key} data with {len(service_data)} fields")
        
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
        if bias_score > 40:
            findings.append({
                'type': 'warning',
                'text': f'Significant bias detected: {bias_score}/100',
                'service': 'bias_detector'
            })
    
    # Check fact checking
    if 'fact_checker' in service_results:
        data = service_results['fact_checker']
        if data.get('unverified_claims', 0) > 0:
            findings.append({
                'type': 'info',
                'text': f'{data.get("unverified_claims", 0)} unverified claims found',
                'service': 'fact_checker'
            })
    
    return findings[:5]  # Limit to 5 findings

# Debug routes

@app.route('/api/debug/services')
def debug_services():
    """Get detailed service information"""
    registry = get_service_registry()
    
    return jsonify({
        'status': registry.get_service_status(),
        'performance': performance_stats
    })

# Static file serving for templates
@app.route('/templates/<path:filename>')
def serve_template(filename):
    """Serve template files"""
    try:
        # Security check
        if '..' in filename or filename.startswith('/'):
            return "Invalid path", 400
            
        # Serve the template file
        return send_from_directory('templates', filename)
    except Exception as e:
        logger.error(f"Error serving template {filename}: {e}")
        return f"Error loading template: {str(e)}", 500

# Initialize app state
app.config['start_time'] = datetime.now()

if __name__ == '__main__':
    # Validate configuration
    config_status = Config.validate()
    
    logger.info("Configuration Status:")
    logger.info(f"  Valid: {config_status['valid']}")
    logger.info(f"  Enabled Services: {config_status['enabled_services']}")
    
    if config_status['warnings']:
        logger.warning("Configuration Warnings:")
        for warning in config_status['warnings']:
            logger.warning(f"  - {warning}")
    
    if config_status['errors']:
        logger.error("Configuration Errors:")
        for error in config_status['errors']:
            logger.error(f"  - {error}")
    
    # Get port from environment or config
    port = int(os.environ.get('PORT', 5000))
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=Config.DEBUG
    )
