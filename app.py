"""
News Analyzer API
Main Flask application for analyzing news articles
"""
import os
import sys
import logging
import json
import traceback
from typing import Dict, Any, Optional, List
from flask import Flask, request, jsonify, send_from_directory, make_response, render_template
from flask_cors import CORS
import uuid
from datetime import datetime
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from services.news_analyzer import NewsAnalyzer
from services.response_builder import ResponseBuilder, AnalysisResponseBuilder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize services
logger.info("=== INITIALIZING NEWS ANALYZER ===")
news_analyzer = NewsAnalyzer()
logger.info("=== NEWS ANALYZER INITIALIZED ===")

# Debug tracking
debug_info = {
    'requests': {},
    'errors': [],
    'service_calls': [],
    'initialization_log': []
}

# Request tracking
@app.before_request
def before_request():
    """Log incoming requests"""
    request.id = str(uuid.uuid4())
    request.start_time = datetime.now()
    
    # Set request ID for response builder
    ResponseBuilder._request_id = request.id
    ResponseBuilder._start_time = int(datetime.now().timestamp() * 1000)
    
    # Store request info for debugging
    debug_info['requests'][request.id] = {
        'method': request.method,
        'path': request.path,
        'timestamp': request.start_time.isoformat(),
        'args': dict(request.args),
        'json': request.get_json(silent=True) if request.is_json else None
    }
    
    logger.info(f"Request {request.id}: {request.method} {request.path}")

@app.after_request
def after_request(response):
    """Log response and add headers"""
    if hasattr(request, 'id'):
        duration = (datetime.now() - request.start_time).total_seconds()
        logger.info(f"Request {request.id} completed in {duration:.3f}s with status {response.status_code}")
        
        # Update request info
        if request.id in debug_info['requests']:
            debug_info['requests'][request.id].update({
                'status': response.status_code,
                'duration': duration,
                'completed': datetime.now().isoformat()
            })
    
    # Add security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    return response

@app.errorhandler(Exception)
def handle_error(error):
    """Global error handler"""
    error_id = str(uuid.uuid4())
    error_info = {
        'id': error_id,
        'type': type(error).__name__,
        'message': str(error),
        'traceback': traceback.format_exc(),
        'timestamp': datetime.now().isoformat()
    }
    
    # Store error for debugging
    debug_info['errors'].append(error_info)
    
    # Log error
    logger.error(f"Error {error_id}: {error_info['type']} - {error_info['message']}")
    logger.error(error_info['traceback'])
    
    # Return appropriate error response
    if isinstance(error, ValueError):
        return jsonify({
            'success': False,
            'error': str(error),
            'error_id': error_id
        }), 400
    
    # Generic error response
    return jsonify({
        'success': False,
        'error': 'An internal error occurred',
        'error_id': error_id
    }), 500

# Helper functions
def clean_service_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Clean service data to remove None values and empty strings"""
    if not isinstance(data, dict):
        return data
    
    cleaned = {}
    for key, value in data.items():
        if value is None or value == '':
            continue
        
        if isinstance(value, dict):
            cleaned_value = clean_service_data(value)
            if cleaned_value:  # Only include non-empty dicts
                cleaned[key] = cleaned_value
        elif isinstance(value, list):
            cleaned[key] = [clean_value(item) for item in value if clean_value(item) is not None]
        else:
            cleaned[key] = clean_value(value)
    
    # Special handling for article extractor
    if 'content' in cleaned and 'text' not in cleaned:
        # Check if content looks like text or URL
        content = cleaned.get('content', '')
        if isinstance(content, str):
            if content.startswith('http://') or content.startswith('https://'):
                cleaned['url'] = content
            else:
                cleaned['text'] = content
    
    # Ensure we have at least basic fields
    if 'title' not in cleaned or not cleaned.get('title'):
        cleaned['title'] = 'Unknown Title'
    
    if 'domain' not in cleaned and 'url' in cleaned:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(cleaned['url'])
            cleaned['domain'] = parsed.netloc
        except:
            pass
    
    return cleaned

def clean_value(value: Any) -> Any:
    """Clean individual values"""
    if isinstance(value, str):
        if contains_corrupted_data(value):
            # For short strings, return None
            if len(value) < 100:
                return None
            # For longer strings, try to extract clean portion
            clean_portion = extract_clean_text(value)
            return clean_portion if clean_portion else None
        return value
    elif isinstance(value, (int, float, bool)):
        return value
    elif isinstance(value, dict):
        return clean_service_data(value)
    elif isinstance(value, list):
        return [clean_value(item) for item in value if clean_value(item) is not None]
    else:
        return value

def contains_corrupted_data(text: str) -> bool:
    """Check if text contains corrupted data indicators"""
    if not isinstance(text, str):
        return False
    
    # Check for replacement character which indicates encoding issues
    if '\ufffd' in text:
        return True
    
    # Check for excessive non-printable characters
    non_printable_count = sum(1 for char in text if ord(char) < 32 and char not in '\n\r\t')
    if len(text) > 0 and non_printable_count / len(text) > 0.1:  # More than 10% non-printable
        return True
    
    return False

def extract_clean_text(text: str) -> Optional[str]:
    """Try to extract clean portions of text"""
    if not text:
        return None
    
    # Split by common delimiters and find clean segments
    segments = text.split('\n')
    clean_segments = []
    
    for segment in segments:
        if segment and not contains_corrupted_data(segment):
            clean_segments.append(segment.strip())
    
    # If we found clean segments, join them
    if clean_segments:
        result = '\n'.join(clean_segments)
        # Only return if we have meaningful content
        if len(result) > 50:  # At least 50 characters
            return result
    
    return None

def clean_article_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Clean and standardize article data"""
    if not isinstance(data, dict):
        return {}
    
    cleaned = {}
    
    # Essential fields
    essential_fields = ['title', 'text', 'author', 'publish_date', 'url', 'domain']
    for field in essential_fields:
        if field in data and data[field]:
            cleaned[field] = data[field]
    
    # Additional fields
    optional_fields = ['description', 'image', 'keywords', 'word_count', 'source', 'language']
    for field in optional_fields:
        if field in data and data[field]:
            cleaned[field] = data[field]
    
    # Ensure we have defaults
    if 'title' not in cleaned:
        cleaned['title'] = 'Untitled'
    if 'author' not in cleaned:
        cleaned['author'] = 'Unknown'
    
    return cleaned

def extract_key_findings(services: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract key findings from service results"""
    findings = []
    
    # Check source credibility
    if 'source_credibility' in services:
        sc = services['source_credibility']
        score = sc.get('credibility_score', 0)
        if score < 50:
            findings.append({
                'type': 'warning',
                'service': 'source_credibility',
                'text': f'Low source credibility ({score}/100)'
            })
    
    # Check bias
    if 'bias_detector' in services:
        bd = services['bias_detector']
        bias_score = bd.get('bias_score', 0)
        if bias_score > 70:
            findings.append({
                'type': 'warning',
                'service': 'bias_detector',
                'text': f'High bias detected ({bias_score}%)'
            })
    
    # Check fact checking
    if 'fact_checker' in services:
        fc = services['fact_checker']
        if fc.get('fact_checks'):
            false_count = sum(1 for check in fc['fact_checks'] 
                            if check.get('verdict', '').lower() in ['false', 'mostly false'])
            if false_count > 0:
                findings.append({
                    'type': 'alert',
                    'service': 'fact_checker',
                    'text': f'{false_count} false claim(s) detected'
                })
    
    return findings[:5]  # Limit to 5 findings

def transform_analysis_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Transform backend result to match frontend expectations"""
    
    # Debug logging
    logger.info(f"=== TRANSFORM DEBUG ===")
    logger.info(f"Input result keys: {list(result.keys())}")
    
    # Extract all service results
    services = {}
    metadata_services = []
    
    # The pipeline returns service results directly in the result dict
    service_names = [
        'article_extractor', 'source_credibility', 'author_analyzer',
        'bias_detector', 'fact_checker', 'transparency_analyzer',
        'manipulation_detector', 'content_analyzer', 'plagiarism_detector'
    ]
    
    for service_name in service_names:
        if service_name in result and isinstance(result[service_name], dict):
            service_result = result[service_name]
            if 'success' in service_result and service_result.get('success'):
                # Extract the data
                if 'data' in service_result:
                    services[service_name] = clean_service_data(service_result['data'])
                else:
                    # Remove metadata fields
                    cleaned_result = {
                        k: v for k, v in service_result.items()
                        if k not in ['service', 'success', 'timestamp', 'available', 'error']
                    }
                    services[service_name] = clean_service_data(cleaned_result)
                
                metadata_services.append(service_name)
    
    logger.info(f"Found {len(services)} services: {metadata_services}")
    
    # Extract article metadata
    article_data = {}
    if 'article' in result:
        article_data = clean_article_data(result['article'])
    elif 'article_extractor' in services:
        article_data = clean_article_data(services['article_extractor'])
    
    # Build the expected structure
    transformed = {
        'article': article_data,
        'analysis': {
            'trust_score': result.get('trust_score', 0),
            'trust_level': result.get('trust_level', 'unknown'),
            'summary': result.get('summary', 'Analysis completed'),
            'key_findings': extract_key_findings(services)
        },
        'detailed_analysis': services
    }
    
    logger.info(f"=== TRANSFORM OUTPUT ===")
    logger.info(f"Article keys: {list(transformed['article'].keys())}")
    logger.info(f"Analysis keys: {list(transformed['analysis'].keys())}")
    logger.info(f"Detailed analysis services: {list(transformed['detailed_analysis'].keys())}")
    
    return transformed

# MAIN ROUTES

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    # Get service registry status
    from services.service_registry import get_service_registry
    registry = get_service_registry()
    service_status = registry.get_service_status()
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': service_status['services'],
        'summary': service_status['summary']
    })

@app.route('/api/status')
def api_status():
    """Get detailed API status"""
    # Get service registry
    from services.service_registry import get_service_registry
    registry = get_service_registry()
    service_status = registry.get_service_status()
    
    # Get configuration status
    config_status = Config.validate()
    
    return jsonify({
        'api_version': '2.0',
        'status': 'operational',
        'timestamp': datetime.now().isoformat(),
        'services': service_status,
        'configuration': config_status,
        'stats': {
            'total_requests': len(debug_info['requests']),
            'total_errors': len(debug_info['errors']),
            'uptime': (datetime.now() - app.config.get('start_time', datetime.now())).total_seconds()
        }
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Main analysis endpoint
    Accepts: { "url": "..." } or { "text": "..." }
    """
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            return ResponseBuilder.error("No data provided", 400)
        
        # Log request
        logger.info(f"Analysis request received with keys: {list(data.keys())}")
        
        # Extract URL or text
        url = data.get('url')
        text = data.get('text')
        
        if not url and not text:
            return ResponseBuilder.error("Either URL or text must be provided", 400)
        
        if url and text:
            return ResponseBuilder.error("Provide either URL or text, not both", 400)
        
        # Prepare content for analysis
        content = url if url else text
        content_type = 'url' if url else 'text'
        
        # Get options from request
        options = data.get('options', {})
        
        # Run analysis
        logger.info(f"Starting analysis for {content_type}: {content[:100]}...")
        start_time = time.time()
        
        result = news_analyzer.analyze(content, content_type, options)
        
        analysis_time = time.time() - start_time
        logger.info(f"Analysis completed in {analysis_time:.2f}s")
        
        # Check if analysis succeeded
        if not result.get('success'):
            error_msg = result.get('error', 'Analysis failed')
            logger.error(f"Analysis failed: {error_msg}")
            return ResponseBuilder.error(error_msg, 400)
        
        # Transform the result
        logger.info("Transforming result for frontend...")
        transformed_result = transform_analysis_result(result)
        
        # Add metadata
        metadata = {
            'request_id': request.id,
            'analysis_time': analysis_time,
            'timestamp': datetime.now().isoformat()
        }
        
        # Build and return response
        logger.info("Building response...")
        response = ResponseBuilder.success(
            data=transformed_result,
            message="Analysis completed successfully",
            metadata=metadata
        )
        
        logger.info("=== RESPONSE DEBUG ===")
        logger.info(f"Response type: {type(response)}")
        logger.info(f"Response status: {response[1] if isinstance(response, tuple) else 'unknown'}")
        
        return response
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}", exc_info=True)
        return ResponseBuilder.error(str(e), 500)

# TEST ENDPOINT
@app.route('/api/test/response-structure')
def test_response_structure():
    """Test endpoint to verify response structure"""
    test_data = {
        'article': {
            'title': 'Test Article',
            'author': 'Test Author',
            'domain': 'example.com'
        },
        'analysis': {
            'trust_score': 75,
            'trust_level': 'High',
            'summary': 'This is a test response',
            'key_findings': []
        },
        'detailed_analysis': {
            'source_credibility': {
                'credibility_score': 85,
                'source_name': 'Example News'
            }
        }
    }
    
    return ResponseBuilder.success(
        data=test_data,
        message="Test response",
        metadata={'test': True}
    )

# DEBUG ROUTES (only in development)

@app.route('/api/debug/services')
def debug_services():
    """Debug endpoint to check service status"""
    if not Config.DEBUG:
        return jsonify({'error': 'Not available in production'}), 403
    
    from services.service_registry import get_service_registry
    registry = get_service_registry()
    
    return jsonify({
        'registry_status': registry.get_service_status(),
        'service_details': registry.get_service_details(),
        'configuration': Config.validate()
    })

@app.route('/api/debug/requests')
def debug_requests():
    """Debug endpoint to see recent requests"""
    if not Config.DEBUG:
        return jsonify({'error': 'Not available in production'}), 403
    
    # Get last 10 requests
    recent_requests = sorted(
        debug_info['requests'].items(),
        key=lambda x: x[1]['timestamp'],
        reverse=True
    )[:10]
    
    return jsonify({
        'total_requests': len(debug_info['requests']),
        'recent_requests': [req[1] for req in recent_requests]
    })

@app.route('/api/debug/errors')
def debug_errors():
    """Debug endpoint to see recent errors"""
    if not Config.DEBUG:
        return jsonify({'error': 'Not available in production'}), 403
    
    return jsonify({
        'total_errors': len(debug_info['errors']),
        'recent_errors': debug_info['errors'][-10:]  # Last 10 errors
    })

@app.route('/api/debug/test/<service_name>')
def debug_test_service(service_name):
    """Debug endpoint to test individual services"""
    if not Config.DEBUG:
        return jsonify({'error': 'Not available in production'}), 403
    
    from services.service_registry import get_service_registry
    registry = get_service_registry()
    
    # Test data
    test_data = {
        'url': 'https://www.example.com/test-article',
        'text': 'This is a test article for debugging purposes.',
        'title': 'Test Article',
        'content': 'This is test content for service debugging.'
    }
    
    try:
        service = registry.get_service(service_name)
        if not service:
            return jsonify({
                'success': False,
                'error': f'Service {service_name} not found'
            }), 404
        
        result = service.analyze(test_data)
        
        return jsonify({
            'success': True,
            'service': service_name,
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'service': service_name,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

# Static file serving for templates
@app.route('/templates/<path:filename>')
def serve_template(filename):
    """Serve template files"""
    return send_from_directory('templates', filename)

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
