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
                    'services_used': list(result.get('services', {}).keys())
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
    # Extract services data
    services = result.get('services', {})
    
    # Build the expected structure
    transformed = {
        'analysis': {
            'trust_score': result.get('trust_score', 0),
            'trust_level': result.get('trust_level', 'unknown'),
            'summary': result.get('summary', {}),
            'timestamp': datetime.now().isoformat()
        },
        'article': result.get('metadata', {}),
        'detailed_analysis': services,
        'metadata': {
            'services_available': result.get('services_available', 0),
            'is_pro': result.get('is_pro', False),
            'analysis_mode': result.get('analysis_mode', 'basic'),
            'processing_time': result.get('pipeline_metadata', {}).get('total_duration', 0)
        }
    }
    
    return transformed

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
    logger.info(f"Debug endpoints available: /api/debug/info, /api/debug/services, /api/debug/test-analyze")
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=Config.DEBUG
    )
