"""
News Analyzer API
Main Flask application for analyzing news articles
"""
import os
import sys
import logging
import json
import traceback
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import uuid
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from services.news_analyzer import NewsAnalyzer
from services.response_builder import ResponseBuilder, AnalysisResponseBuilder

# Configure logging
logging.basicConfig(
    level=Config.LOGGING['level'],
    format=Config.LOGGING['format'],
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
news_analyzer = NewsAnalyzer()

# Request tracking
@app.before_request
def before_request():
    """Log incoming requests"""
    request.id = str(uuid.uuid4())
    request.start_time = datetime.now()
    
    # Set request ID for response builder
    ResponseBuilder._request_id = request.id
    ResponseBuilder._start_time = int(datetime.now().timestamp() * 1000)
    
    # Log request details
    logger.info(f"Request {request.id}: {request.method} {request.path}")
    
    if request.method == 'POST' and request.is_json:
        # Log POST data (be careful with sensitive data in production)
        data = request.get_json()
        if data:
            # Truncate long content for logging
            log_data = data.copy()
            if 'content' in log_data and len(str(log_data['content'])) > 100:
                log_data['content'] = str(log_data['content'])[:100] + '...'
            logger.debug(f"Request {request.id} data: {log_data}")

@app.after_request
def after_request(response):
    """Log response details"""
    if hasattr(request, 'id') and hasattr(request, 'start_time'):
        duration = (datetime.now() - request.start_time).total_seconds()
        logger.info(f"Response {request.id}: {response.status_code} ({duration:.3f}s)")
    
    # Add security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    return response

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    """Handle bad request errors"""
    response, status_code = ResponseBuilder.error("Bad Request", 400)
    return response, status_code

@app.errorhandler(404)
def not_found(error):
    """Handle not found errors"""
    response, status_code = ResponseBuilder.error("Resource not found", 404)
    return response, status_code

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {error}", exc_info=True)
    response, status_code = ResponseBuilder.error("Internal server error", 500)
    return response, status_code

# Routes
@app.route('/')
def index():
    """Serve the main application page"""
    try:
        # First try static folder
        index_path = os.path.join(app.static_folder, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(app.static_folder, 'index.html')
        
        # Then try templates folder
        if app.template_folder:
            template_path = os.path.join(app.template_folder, 'index.html')
            if os.path.exists(template_path):
                return send_from_directory(app.template_folder, 'index.html')
        
        # If not found, return error
        logger.error(f"index.html not found in {app.static_folder} or {app.template_folder}")
        response, status_code = ResponseBuilder.error("Main page not found", 404)
        return response, status_code
        
    except Exception as e:
        logger.error(f"Error serving index: {e}", exc_info=True)
        response, status_code = ResponseBuilder.error("Error loading main page", 500)
        return response, status_code

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
        # Get configuration validation
        config_status = Config.validate()
        
        # Get service status from analyzer
        service_status = news_analyzer.get_service_status()
        
        return jsonify({
            'status': 'operational' if config_status['valid'] else 'degraded',
            'config': config_status,
            'services': service_status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        response, status_code = ResponseBuilder.error("Status check failed", 500)
        return response, status_code

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Analyze a news article
    
    Expected JSON payload:
    {
        "url": "https://example.com/article" OR "text": "Article content...",
        "type": "url" or "text",
        "options": {
            "pro_mode": true/false
        }
    }
    """
    try:
        # Validate request
        if not request.is_json:
            response, status_code = ResponseBuilder.error("Content-Type must be application/json", 400)
            return response, status_code
        
        data = request.get_json()
        
        # Extract parameters
        content = data.get('url') or data.get('text') or data.get('content')
        content_type = data.get('type', 'url')
        options = data.get('options', {})
        
        # Basic validation
        if not content:
            response, status_code = ResponseBuilder.error("Missing 'url' or 'text' field", 400)
            return response, status_code
        
        if content_type not in ['url', 'text']:
            response, status_code = ResponseBuilder.error("Invalid type. Must be 'url' or 'text'", 400)
            return response, status_code
        
        # Log analysis request
        logger.info(f"Starting analysis: type={content_type}, pro={options.get('pro_mode', False)}, content_length={len(str(content))}")
        
        # Perform analysis
        result = news_analyzer.analyze(
            content=content,
            content_type=content_type,
            pro_mode=options.get('pro_mode', False)
        )
        
        # Build response based on success/failure
        if result.get('success', False):
            # Extract necessary data for AnalysisResponseBuilder
            article_data = result.get('article', {})
            processing_time = result.get('pipeline_metadata', {}).get('total_time', 0)
            services_used = list(result.get('pipeline_metadata', {}).get('stages_completed', {}).keys())
            
            # Use AnalysisResponseBuilder for successful analysis
            return AnalysisResponseBuilder.build_analysis_response(
                analysis_results=result,
                article_data=article_data,
                processing_time=processing_time,
                services_used=services_used
            )
        else:
            # Extract error message
            error_msg = result.get('error', 'Analysis failed')
            response, status_code = ResponseBuilder.error(error_msg, 400)
            return response, status_code
            
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        response, status_code = ResponseBuilder.error(str(e), 400)
        return response, status_code
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        response, status_code = ResponseBuilder.error("Analysis failed due to an internal error", 500)
        return response, status_code

@app.route('/api/services')
def services():
    """Get available services and their status"""
    try:
        service_status = news_analyzer.get_service_status()
        return jsonify({
            'services': service_status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Service status check failed: {e}")
        response, status_code = ResponseBuilder.error("Service status check failed", 500)
        return response, status_code

@app.route('/api/config')
def config():
    """Get public configuration"""
    try:
        # Only return non-sensitive configuration
        public_config = {
            'pipeline': {
                'max_timeout': Config.PIPELINE['max_total_timeout'],
                'parallel_processing': Config.PIPELINE['parallel_processing'],
                'min_required_services': Config.PIPELINE['min_required_services']
            },
            'services': {
                name: {
                    'enabled': config.enabled,
                    'timeout': config.timeout
                }
                for name, config in Config.SERVICES.items()
            },
            'trust_score_weights': Config.TRUST_SCORE_WEIGHTS
        }
        
        return jsonify(public_config)
    except Exception as e:
        logger.error(f"Config endpoint failed: {e}")
        response, status_code = ResponseBuilder.error("Config retrieval failed", 500)
        return response, status_code

@app.route('/api/debug/services', methods=['GET'])
def debug_services():
    """Debug endpoint to check service status"""
    try:
        from services.service_registry import service_registry
        from services.analysis_pipeline import pipeline
        from config import Config
        
        # Get service registry status
        registry_status = service_registry.get_service_status()
        
        # Check article_extractor specifically
        article_extractor = service_registry.get_service('article_extractor')
        article_extractor_info = None
        if article_extractor:
            article_extractor_info = {
                'found': True,
                'is_available': article_extractor.is_available,
                'service_name': getattr(article_extractor, 'service_name', 'MISSING'),
                'class_name': article_extractor.__class__.__name__
            }
        else:
            article_extractor_info = {'found': False}
        
        # Check pipeline stages
        stages_info = []
        for stage in pipeline.stages:
            # Get available services for this stage
            available_services = [
                s for s in stage.services 
                if service_registry.get_service(s) and service_registry.get_service(s).is_available
            ]
            stages_info.append({
                'name': stage.name,
                'configured_services': stage.services,
                'available_services': available_services,
                'required': stage.required
            })
        
        # Check config
        config_info = {
            'article_extractor_enabled': Config.is_service_enabled('article_extractor'),
            'services_configured': list(Config.SERVICES.keys()),
            'pipeline_stages': getattr(Config, 'PIPELINE_STAGES', 'NOT FOUND'),
            'service_to_stage': getattr(Config, 'SERVICE_TO_STAGE', 'NOT FOUND')
        }
        
        debug_info = {
            'registry_status': registry_status,
            'article_extractor': article_extractor_info,
            'pipeline_stages': stages_info,
            'config': config_info,
            'all_registered_services': list(service_registry.services.keys()),
            'all_async_services': list(service_registry.async_services.keys()),
            'failed_services': service_registry.failed_services
        }
        
        return jsonify(debug_info), 200
        
    except Exception as e:
        logger.error(f"Debug endpoint error: {e}", exc_info=True)
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

# Serve static files (JS, CSS, etc.)
@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    # Security check - prevent directory traversal
    if '..' in path or path.startswith('/'):
        response, status_code = ResponseBuilder.error("Invalid path", 400)
        return response, status_code
    
    # Special handling for JS files
    if path.startswith('js/'):
        file_path = os.path.join(app.static_folder, path)
        logger.info(f"Attempting to serve JS file: {path.split('/')[-1]}")
        logger.info(f"Looking in: {file_path}")
        
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            logger.info(f"Successfully served {path.split('/')[-1]} ({file_size} bytes)")
            return send_from_directory(app.static_folder, path)
        else:
            logger.error(f"JS file not found: {file_path}")
            response, status_code = ResponseBuilder.error("File not found", 404)
            return response, status_code
    
    # Try to serve the file
    try:
        return send_from_directory(app.static_folder, path)
    except Exception as e:
        logger.debug(f"Static file not found: {path}")
        # Don't return error for common missing files
        if path in ['favicon.ico', 'robots.txt']:
            return '', 404
        response, status_code = ResponseBuilder.error("File not found", 404)
        return response, status_code

if __name__ == '__main__':
    # Validate configuration on startup
    config_status = Config.validate()
    if not config_status['valid']:
        logger.error(f"Configuration errors: {config_status['errors']}")
        sys.exit(1)
    
    if config_status['warnings']:
        for warning in config_status['warnings']:
            logger.warning(f"Configuration warning: {warning}")
    
    # Log startup information
    logger.info(f"Starting News Analyzer API in {Config.ENV} mode")
    logger.info(f"Enabled services: {config_status['enabled_services']}")
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=Config.DEBUG
    )
