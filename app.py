"""
News Analyzer API (Refactored)
Clean architecture with standardized responses and proper error handling
"""
import os
import time
import logging
import uuid
from functools import wraps
from flask import Flask, request, render_template, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import Config
from services.news_analyzer import NewsAnalyzer
from services.response_builder import ResponseBuilder, AnalysisResponseBuilder
from services.service_registry import service_registry

# Configure logging
logging.basicConfig(
    level=Config.LOGGING['level'],
    format=Config.LOGGING['format'],
    filename=Config.LOGGING['file']
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
            static_folder='static',
            static_url_path='/static')

# Configuration
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = Config.DEBUG

# CORS configuration
CORS(app, origins=['*'])

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[f"{Config.RATE_LIMITS['requests_per_minute']} per minute"]
)

# Initialize services
try:
    news_analyzer = NewsAnalyzer()
    logger.info("NewsAnalyzer initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize NewsAnalyzer: {e}")
    news_analyzer = None

# Validate configuration on startup
config_status = Config.validate()
if not config_status['valid']:
    logger.error(f"Configuration errors: {config_status['errors']}")
if config_status['warnings']:
    logger.warning(f"Configuration warnings: {config_status['warnings']}")


# Middleware
@app.before_request
def before_request():
    """Set up request context"""
    g.start_time = time.time()
    g.request_id = str(uuid.uuid4())
    
    # Set for ResponseBuilder
    ResponseBuilder._start_time = g.start_time
    ResponseBuilder._request_id = g.request_id
    
    # Log request
    logger.info(f"Request {g.request_id}: {request.method} {request.path}")


@app.after_request
def after_request(response):
    """Log response and add headers"""
    if hasattr(g, 'start_time'):
        elapsed = time.time() - g.start_time
        response.headers['X-Response-Time'] = f"{elapsed:.3f}"
        
    if hasattr(g, 'request_id'):
        response.headers['X-Request-ID'] = g.request_id
        
    # Security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Log response
    logger.info(f"Response {getattr(g, 'request_id', 'unknown')}: "
               f"{response.status_code} ({elapsed:.3f}s)")
    
    return response


def require_analyzer(f):
    """Decorator to ensure analyzer is available"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not news_analyzer:
            return ResponseBuilder.error(
                "Analysis service is temporarily unavailable",
                status_code=503,
                error_code="SERVICE_UNAVAILABLE"
            )
        return f(*args, **kwargs)
    return decorated_function


# Routes
@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/api/health')
def health():
    """Health check endpoint"""
    health_data = {
        'status': 'healthy' if news_analyzer else 'degraded',
        'version': '2.0',
        'environment': Config.ENV,
        'services': service_registry.get_service_status()['summary'] if news_analyzer else {}
    }
    
    status_code = 200 if news_analyzer else 503
    return ResponseBuilder.success(health_data, status_code=status_code)


@app.route('/api/analyze', methods=['POST'])
@require_analyzer
@limiter.limit(f"{Config.RATE_LIMITS['requests_per_hour']} per hour")
def analyze():
    """
    Main analysis endpoint
    Accepts: { "url": "https://..." } or { "text": "article content..." }
    Returns: Standardized analysis response
    """
    try:
        # Parse request
        data = request.get_json()
        if not data:
            return ResponseBuilder.error(
                "No data provided",
                status_code=400,
                error_code="MISSING_DATA"
            )
        
        # Validate input
        url = data.get('url')
        text = data.get('text')
        
        if not url and not text:
            return ResponseBuilder.error(
                "Either 'url' or 'text' is required",
                status_code=400,
                error_code="MISSING_INPUT"
            )
        
        if url and text:
            return ResponseBuilder.error(
                "Provide either 'url' or 'text', not both",
                status_code=400,
                error_code="INVALID_INPUT"
            )
        
        # Determine content and type
        if url:
            content = url
            content_type = 'url'
            
            # Basic URL validation
            if not url.startswith(('http://', 'https://')):
                return ResponseBuilder.error(
                    "Invalid URL format. URL must start with http:// or https://",
                    status_code=400,
                    error_code="INVALID_URL"
                )
        else:
            content = text
            content_type = 'text'
            
            # Basic text validation
            if len(text.strip()) < 100:
                return ResponseBuilder.error(
                    "Text too short. Please provide at least 100 characters",
                    status_code=400,
                    error_code="TEXT_TOO_SHORT"
                )
            
            if len(text) > 50000:
                return ResponseBuilder.error(
                    "Text too long. Maximum 50,000 characters",
                    status_code=400,
                    error_code="TEXT_TOO_LONG"
                )
        
        # Check pro status
        is_pro = data.get('is_pro', False)
        
        # Log analysis start
        logger.info(f"Starting analysis: type={content_type}, pro={is_pro}, "
                   f"content_length={len(content)}")
        
        # Perform analysis
        start_time = time.time()
        results = news_analyzer.analyze(content, content_type, is_pro)
        processing_time = time.time() - start_time
        
        # Check if analysis succeeded
        if not results.get('success'):
            return ResponseBuilder.error(
                results.get('error', 'Analysis failed'),
                status_code=400,
                error_code="ANALYSIS_FAILED",
                details=results.get('errors')
            )
        
        # Build response
        article_data = results.get('article', {})
        
        # FIX: Use 'successful_services' instead of 'services_succeeded'
        # The pipeline stores the list of successful service names in 'successful_services'
        # but stores the count in 'services_succeeded'
        pipeline_metadata = results.get('pipeline_metadata', {})
        services_used = pipeline_metadata.get('successful_services', [])
        
        # Ensure services_used is a list
        if not isinstance(services_used, list):
            logger.warning(f"services_used is not a list: {type(services_used)}")
            services_used = []
        
        return AnalysisResponseBuilder.build_analysis_response(
            analysis_results=results,
            article_data=article_data,
            processing_time=processing_time,
            services_used=services_used
        )
        
    except Exception as e:
        logger.error(f"Analysis endpoint error: {str(e)}", exc_info=True)
        return ResponseBuilder.error(
            e,
            status_code=500,
            error_code="INTERNAL_ERROR"
        )


@app.route('/api/services/status')
def services_status():
    """Get status of all analysis services"""
    try:
        if not news_analyzer:
            return ResponseBuilder.error(
                "Service registry not available",
                status_code=503,
                error_code="SERVICE_UNAVAILABLE"
            )
        
        status = news_analyzer.get_service_status()
        return ResponseBuilder.success(
            status,
            message="Service status retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Service status error: {str(e)}", exc_info=True)
        return ResponseBuilder.error(e, status_code=500)


@app.route('/api/services/reload', methods=['POST'])
@require_analyzer
def reload_services():
    """Reload failed services"""
    try:
        # Optional: Add authentication check here
        auth_token = request.headers.get('Authorization')
        if auth_token != f"Bearer {Config.SECRET_KEY}":
            return ResponseBuilder.error(
                "Unauthorized",
                status_code=401,
                error_code="UNAUTHORIZED"
            )
        
        result = news_analyzer.reload_services()
        
        return ResponseBuilder.success(
            result,
            message=f"Reloaded {len(result['reloaded'])} services"
        )
        
    except Exception as e:
        logger.error(f"Service reload error: {str(e)}", exc_info=True)
        return ResponseBuilder.error(e, status_code=500)


@app.route('/api/config/validate')
def validate_config():
    """Validate current configuration"""
    try:
        validation = Config.validate()
        
        if validation['valid']:
            return ResponseBuilder.success(
                validation,
                message="Configuration is valid"
            )
        else:
            return ResponseBuilder.partial_success(
                {'warnings': validation['warnings']},
                validation['errors'],
                message="Configuration has errors"
            )
            
    except Exception as e:
        logger.error(f"Config validation error: {str(e)}", exc_info=True)
        return ResponseBuilder.error(e, status_code=500)


# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return ResponseBuilder.error(
        "Endpoint not found",
        status_code=404,
        error_code="NOT_FOUND"
    )


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return ResponseBuilder.error(
        "Internal server error",
        status_code=500,
        error_code="INTERNAL_ERROR"
    )


@app.errorhandler(429)
def rate_limit_exceeded(error):
    """Handle rate limit errors"""
    return ResponseBuilder.error(
        "Rate limit exceeded. Please try again later",
        status_code=429,
        error_code="RATE_LIMIT_EXCEEDED"
    )


if __name__ == '__main__':
    # Get port from environment
    port = int(os.environ.get('PORT', 5000))
    
    # Start message
    logger.info(f"Starting News Analyzer API on port {port}")
    logger.info(f"Environment: {Config.ENV}")
    logger.info(f"Services available: {config_status['enabled_services']}")
    
    # Run app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=Config.DEBUG
    )
