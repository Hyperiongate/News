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
        'args': dict(request.args),
        'start_time': request.start_time.isoformat()
    }
    
    if request.method == 'POST' and request.is_json:
        debug_info['requests'][request.id]['body'] = request.get_json()
    
    logger.info(f"Request {request.id}: {request.method} {request.path}")

@app.after_request
def after_request(response):
    """Log response and timing"""
    if hasattr(request, 'id'):
        duration = (datetime.now() - request.start_time).total_seconds()
        logger.info(f"Request {request.id} completed in {duration:.2f}s with status {response.status_code}")
        
        # Update debug info
        if request.id in debug_info['requests']:
            debug_info['requests'][request.id]['duration'] = duration
            debug_info['requests'][request.id]['status_code'] = response.status_code
    
    return response

# Data cleaning functions
def clean_service_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Clean service data by removing corrupted fields"""
    cleaned = {}
    
    for key, value in data.items():
        # Skip HTML field if it contains corrupted data
        if key == 'html' and isinstance(value, str):
            if contains_corrupted_data(value):
                logger.warning(f"Skipping corrupted HTML field")
                continue
        
        # Recursively clean nested dictionaries
        if isinstance(value, dict):
            cleaned[key] = clean_service_data(value)
        # Clean lists
        elif isinstance(value, list):
            cleaned[key] = [clean_value(item) for item in value]
        else:
            cleaned_value = clean_value(value)
            if cleaned_value is not None:
                cleaned[key] = cleaned_value
    
    return cleaned

def clean_article_data(article: Dict[str, Any]) -> Dict[str, Any]:
    """Clean article data specifically"""
    cleaned = {}
    
    # Define safe fields that should be preserved
    safe_fields = [
        'title', 'author', 'publish_date', 'url', 'domain', 
        'description', 'image', 'keywords', 'word_count', 
        'source', 'language', 'extraction_metadata'
    ]
    
    for field in safe_fields:
        if field in article:
            value = article[field]
            # Special handling for extraction_metadata
            if field == 'extraction_metadata' and isinstance(value, dict):
                cleaned[field] = {k: v for k, v in value.items() if k != 'html'}
            else:
                cleaned_value = clean_value(value)
                if cleaned_value is not None:
                    cleaned[field] = cleaned_value
    
    # Handle text field specially - truncate if corrupted
    if 'text' in article:
        text = article['text']
        if isinstance(text, str):
            if contains_corrupted_data(text):
                # Try to extract any clean portion
                clean_portion = extract_clean_text(text)
                if clean_portion:
                    cleaned['text'] = clean_portion
                else:
                    cleaned['text'] = "Article text could not be extracted properly."
            else:
                cleaned['text'] = text
    
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

# MAIN ROUTES

@app.route('/')
def index():
    """Serve the main application page"""
    try:
        logger.info("Serving index page")
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering template: {e}", exc_info=True)
        return f"Error loading page: {str(e)}", 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/diagnostic')
def diagnostic():
    """Diagnostic page for CSS issues"""
    try:
        return render_template('diagnostic.html')
    except Exception as e:
        return f"Diagnostic page error: {str(e)}", 500

@app.route('/api/status')
def status():
    """Get system status"""
    try:
        # Get service status
        service_status = news_analyzer.service_status
        
        return jsonify({
            'status': 'operational',
            'version': '1.0.0',
            'services': service_status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return ResponseBuilder.error(str(e), 500)

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    """Main analysis endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return ResponseBuilder.error("No data provided", 400)
        
        # Log request
        logger.info(f"Analysis request: {data}")
        
        # Extract URL or text
        url = data.get('url')
        text = data.get('text')
        pro_mode = data.get('is_pro', False)
        
        if not url and not text:
            return ResponseBuilder.error("Please provide either 'url' or 'text'", 400)
        
        # Perform analysis
        logger.info(f"Analyzing: {url if url else 'text content'}")
        
        if url:
            result = news_analyzer.analyze(url, content_type='url', pro_mode=pro_mode)
        else:
            result = news_analyzer.analyze(text, content_type='text', pro_mode=pro_mode)
        
        if result.get('success'):
            # Transform the result to match frontend expectations
            transformed_result = transform_analysis_result(result)
            
            # Build response
            return ResponseBuilder.success(
                transformed_result,
                message="Analysis completed successfully",
                metadata={
                    'processing_time': result.get('pipeline_metadata', {}).get('total_duration', 0),
                    'services_used': list(transformed_result.get('detailed_analysis', {}).keys())
                }
            )
        else:
            error_msg = result.get('error', 'Analysis failed')
            logger.error(f"Analysis failed: {error_msg}")
            return ResponseBuilder.error(error_msg, 400)
            
    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        debug_info['errors'].append({
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'traceback': traceback.format_exc()
        })
        return ResponseBuilder.error(f"Analysis error: {str(e)}", 500)

def transform_analysis_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Transform backend result to match frontend expectations"""
    
    # Debug logging
    logger.info(f"Transforming result with keys: {list(result.keys())}")
    
    # Extract all service results
    services = {}
    metadata_services = []
    
    # The pipeline returns service results directly in the result dict
    service_names = [
        'article_extractor', 'source_credibility', 'author_analyzer',
        'bias_detector', 'fact_checker', 'transparency_analyzer',
        'manipulation_detector', 'content_analyzer'
    ]
    
    for service_name in service_names:
        if service_name in result and isinstance(result[service_name], dict):
            # Check if it's a valid service result (has 'success' field)
            service_result = result[service_name]
            if 'success' in service_result and service_result.get('success'):
                # Extract the data field if it exists, otherwise use the whole result
                if 'data' in service_result:
                    services[service_name] = clean_service_data(service_result['data'])
                else:
                    # Remove metadata fields for cleaner output
                    cleaned_result = {
                        k: v for k, v in service_result.items()
                        if k not in ['service', 'success', 'timestamp', 'available']
                    }
                    services[service_name] = clean_service_data(cleaned_result)
                
                metadata_services.append(service_name)
                logger.info(f"Found successful service: {service_name}")
    
    logger.info(f"Total services found: {len(services)}")
    logger.info(f"Services used: {metadata_services}")
    
    # Extract article metadata from article_extractor if available
    article_data = {}
    if 'article' in result:
        article_data = clean_article_data(result['article'])
    elif 'article_extractor' in result and result['article_extractor'].get('success'):
        # Extract from article_extractor service result
        extractor_data = result['article_extractor']
        if 'data' in extractor_data:
            article_data = clean_article_data(extractor_data['data'])
        else:
            # Legacy format - extract relevant fields
            article_fields = ['title', 'text', 'author', 'publish_date', 'url', 
                           'domain', 'description', 'image', 'keywords', 'word_count', 
                           'source', 'language']
            temp_article = {}
            for field in article_fields:
                if field in extractor_data:
                    temp_article[field] = extractor_data[field]
            article_data = clean_article_data(temp_article)
    
    # Build the expected structure
    transformed = {
        'analysis': {
            'trust_score': result.get('trust_score', 0),
            'trust_level': result.get('trust_level', 'unknown'),
            'summary': result.get('summary', 'Analysis completed'),
            'timestamp': datetime.now().isoformat(),
            'key_findings': extract_key_findings(services)
        },
        'article': article_data,
        'detailed_analysis': services,
        'metadata': {
            'services_available': result.get('pipeline_metadata', {}).get('total_available_services', 0),
            'is_pro': result.get('is_pro', False),
            'analysis_mode': 'premium' if result.get('is_pro', False) else 'basic',
            'processing_time': result.get('pipeline_metadata', {}).get('total_duration', 0)
        }
    }
    
    return transformed

def extract_key_findings(services: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract key findings from service results"""
    findings = []
    
    # Source credibility finding
    if 'source_credibility' in services:
        source = services['source_credibility']
        score = source.get('credibility_score', source.get('score', 0))
        if score < 50:
            findings.append({
                'type': 'negative',
                'finding': 'Low source credibility',
                'text': f"Source credibility score: {score}/100",
                'severity': 'high'
            })
        elif score >= 80:
            findings.append({
                'type': 'positive',
                'finding': 'High source credibility',
                'text': f"Source credibility score: {score}/100",
                'severity': 'low'
            })
    
    # Bias detection finding
    if 'bias_detector' in services:
        bias = services['bias_detector']
        bias_score = bias.get('bias_score', bias.get('score', 0))
        if bias_score > 60:
            findings.append({
                'type': 'negative',
                'finding': 'High bias detected',
                'text': f"Bias score: {bias_score}%",
                'severity': 'high'
            })
        elif bias_score < 30:
            findings.append({
                'type': 'positive',
                'finding': 'Low bias detected',
                'text': f"Bias score: {bias_score}%",
                'severity': 'low'
            })
    
    # Fact checking finding
    if 'fact_checker' in services:
        facts = services['fact_checker']
        if 'fact_checks' in facts and isinstance(facts['fact_checks'], list):
            total = len(facts['fact_checks'])
            verified = sum(1 for f in facts['fact_checks'] 
                         if f.get('verdict') in ['True', 'Verified', 'true', 'verified'])
            if total > 0:
                accuracy = int((verified / total) * 100)
                if accuracy < 50:
                    findings.append({
                        'type': 'negative',
                        'finding': 'Low fact accuracy',
                        'text': f"Only {verified}/{total} claims verified ({accuracy}%)",
                        'severity': 'high'
                    })
                elif accuracy >= 80:
                    findings.append({
                        'type': 'positive',
                        'finding': 'High fact accuracy',
                        'text': f"{verified}/{total} claims verified ({accuracy}%)",
                        'severity': 'low'
                    })
    
    # Author credibility finding
    if 'author_analyzer' in services:
        author = services['author_analyzer']
        if author.get('author_name'):
            score = author.get('credibility_score', author.get('author_score', 0))
            if score > 0:
                if score < 40:
                    findings.append({
                        'type': 'warning',
                        'finding': 'Limited author credibility',
                        'text': f"Author {author['author_name']} has credibility score: {score}/100",
                        'severity': 'medium'
                    })
                elif score >= 70:
                    findings.append({
                        'type': 'positive',
                        'finding': 'Credible author',
                        'text': f"Author {author['author_name']} has credibility score: {score}/100",
                        'severity': 'low'
                    })
        else:
            findings.append({
                'type': 'warning',
                'finding': 'No author information',
                'text': 'Article lacks author attribution',
                'severity': 'medium'
            })
    
    # Sort findings by severity (high first)
    severity_order = {'high': 0, 'medium': 1, 'low': 2}
    findings.sort(key=lambda f: severity_order.get(f.get('severity', 'medium'), 1))
    
    return findings[:5]  # Return top 5 findings

# DEBUG ROUTES

@app.route('/api/debug/info')
def debug_get_info():
    """Get debug information"""
    return jsonify(debug_info)

@app.route('/api/debug/services')
def debug_services():
    """Get detailed service information"""
    try:
        from services.service_registry import service_registry
        
        services_info = {}
        for name, service in service_registry.services.items():
            services_info[name] = {
                'available': service.is_available,
                'class': service.__class__.__name__,
                'module': service.__class__.__module__
            }
        
        return jsonify({
            'services': services_info,
            'failed': service_registry.failed_services,
            'total': len(services_info),
            'available': sum(1 for s in services_info.values() if s['available'])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/test-analyze')
def debug_test_analyze():
    """Test analysis with a known good URL"""
    test_url = "https://www.bbc.com/news/world-us-canada-68562045"
    
    try:
        logger.info(f"Running test analysis on: {test_url}")
        
        result = news_analyzer.analyze(test_url, content_type='url', pro_mode=True)
        
        return jsonify({
            'test_url': test_url,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Test analysis error: {e}", exc_info=True)
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/debug/openai')
def debug_openai():
    """Debug endpoint specifically for OpenAI service"""
    try:
        from services.service_registry import get_service_registry
        registry = get_service_registry()
        
        # Basic info
        openai_info = {
            'api_key_set': bool(Config.OPENAI_API_KEY),
            'api_key_length': len(Config.OPENAI_API_KEY) if Config.OPENAI_API_KEY else 0,
            'service_enabled_in_config': Config.is_service_enabled('openai_enhancer'),
        }
        
        # Registry status
        status = registry.get_service_status()
        if 'openai_enhancer' in status['services']:
            openai_info['registry_status'] = status['services']['openai_enhancer']
        else:
            openai_info['registry_status'] = 'Not in registry'
            if 'openai_enhancer' in status.get('failed_services', {}):
                openai_info['failure_reason'] = status['failed_services']['openai_enhancer']
        
        # Test the service
        service = registry.get_service('openai_enhancer')
        if service:
            openai_info['service_available'] = service.is_available
            
            # Try a minimal test
            if service.is_available:
                test_result = service.analyze({
                    'title': 'Debug Test',
                    'text': 'Testing OpenAI service availability.',
                    'author': 'Debug',
                    'source': 'Debug'
                })
                openai_info['test_success'] = test_result.get('success', False)
                if not test_result.get('success'):
                    openai_info['test_error'] = test_result.get('error')
        else:
            openai_info['service_available'] = False
        
        return jsonify({
            'status': 'debug',
            'openai_service': openai_info,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"OpenAI debug error: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# STATIC FILE SERVING

@app.route('/static/<path:path>')
def serve_static_files(path):
    """Serve static files with correct MIME types"""
    try:
        # Security check
        if '..' in path or path.startswith('/'):
            return "Invalid path", 400
        
        # Determine MIME type
        mime_types = {
            '.js': 'application/javascript',
            '.css': 'text/css',
            '.html': 'text/html',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.ico': 'image/x-icon',
            '.woff': 'font/woff',
            '.woff2': 'font/woff2',
            '.ttf': 'font/ttf'
        }
        
        _, ext = os.path.splitext(path)
        mime_type = mime_types.get(ext.lower(), 'application/octet-stream')
        
        # Serve the file
        response = send_from_directory(app.static_folder, path)
        response.headers['Content-Type'] = mime_type
        response.headers['Cache-Control'] = 'public, max-age=3600'
        return response
        
    except Exception as e:
        logger.error(f"Error serving static file {path}: {e}")
        return f"File not found: {path}", 404

# ERROR HANDLERS

@app.errorhandler(404)
def not_found(e):
    return ResponseBuilder.error("Resource not found", 404)

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {e}", exc_info=True)
    return ResponseBuilder.error("Internal server error", 500)

# STARTUP

def track_initialization():
    """Track service initialization for debugging"""
    global debug_info
    try:
        from services.service_registry import service_registry
        
        debug_info['initialization_log'].append({
            'timestamp': datetime.now().isoformat(),
            'event': 'startup',
            'services_loaded': list(service_registry.services.keys()),
            'services_available': [
                name for name, service in service_registry.services.items() 
                if service.is_available
            ],
            'failed_services': service_registry.failed_services
        })
    except Exception as e:
        debug_info['initialization_log'].append({
            'timestamp': datetime.now().isoformat(),
            'event': 'startup_error',
            'error': str(e)
        })

if __name__ == '__main__':
    # Validate configuration on startup
    config_status = Config.validate()
    if not config_status['valid']:
        logger.error(f"Configuration errors: {config_status['errors']}")
        sys.exit(1)
    
    if config_status['warnings']:
        for warning in config_status['warnings']:
            logger.warning(f"Configuration warning: {warning}")
    
    # Track initialization
    track_initialization()
    
    # Log startup information
    logger.info(f"Starting News Analyzer API in {Config.ENV} mode")
    logger.info(f"Enabled services: {config_status['enabled_services']}")
    logger.info(f"Debug endpoints available: /api/debug/info, /api/debug/services, /api/debug/test-analyze, /api/debug/openai")
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=Config.DEBUG
    )
