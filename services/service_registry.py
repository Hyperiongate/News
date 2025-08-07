"""
News Analyzer API (Refactored)
Clean architecture with standardized responses and proper error handling
"""
import os
import sys
import time
import logging
import uuid
from functools import wraps
from flask import Flask, request, render_template, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Configure logging BEFORE imports to capture initialization errors
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to see all initialization messages
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout  # Output to stdout for Render logs
)
logger = logging.getLogger(__name__)

logger.info("Starting News Analyzer API initialization...")

# Import config first
try:
    from config import Config
    logger.info("Config imported successfully")
except Exception as e:
    logger.error(f"Failed to import Config: {e}")
    raise

# Import services with error handling
try:
    logger.info("Service registry imported successfully")
    
    # Log the service status
    status = service_registry.get_service_status()
    logger.info(f"Service status: {status['summary']}")
    
    # Log details about each service
    for service_name, service_info in status['services'].items():
        if service_info.get('registered'):
            logger.info(f"Service {service_name}: registered={service_info['registered']}, available={service_info['available']}")
        else:
            logger.warning(f"Service {service_name}: FAILED - {service_info.get('error', service_info.get('reason', 'Unknown'))}")
            
except Exception as e:
    logger.error(f"Failed to import service_registry: {e}")
    raise

try:
    from services.news_analyzer import NewsAnalyzer
    logger.info("NewsAnalyzer imported successfully")
except Exception as e:
    logger.error(f"Failed to import NewsAnalyzer: {e}")
    raise

try:
    from services.response_builder import ResponseBuilder, AnalysisResponseBuilder
    logger.info("Response builders imported successfully")
except Exception as e:
    logger.error(f"Failed to import response builders: {e}")
    raise

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
    logger.info("Initializing NewsAnalyzer...")
    news_analyzer = NewsAnalyzer()
    logger.info("NewsAnalyzer initialized successfully")
    logger.info(f"Available services: {news_analyzer.service_status['summary']['total_available']}")
except Exception as e:
    logger.error(f"Failed to initialize NewsAnalyzer: {e}")
    import traceback
    logger.error(f"Traceback: {traceback.format_exc()}")
    news_analyzer = None

# Validate configuration on startup
config_status = Config.validate()
if not config_status['valid']:
    logger.error(f"Configuration errors: {config_status['errors']}")
if config_status['warnings']:
    logger.warning(f"Configuration warnings: {config_status['warnings']}")

# Log final initialization status
logger.info(f"News Analyzer API initialized. Services available: {news_analyzer is not None}")

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
        services_used = list(results.get('pipeline_metadata', {}).get('services_succeeded', []))
        
        return AnalysisResponseBuilder.build_analysis_response(
            analysis_results=results,
            article_data=article_data,
            processing_time=processing_time,
            services_used=services_used
        )
        
    except Exception as e:
        logger.error(f"Analysis endpoint error: {str(e)}", exc_info=True)
        return ResponseBuilder.error(
            "An unexpected error occurred",
            status_code=500,
            error_code="INTERNAL_ERROR"
        )


@app.route('/api/services')
def services():
    """Get service status"""
    return ResponseBuilder.success(service_registry.get_service_status())


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return ResponseBuilder.error(
        "Endpoint not found",
        status_code=404,
        error_code="NOT_FOUND"
    )


@app.errorhandler(429)
def rate_limit_exceeded(e):
    """Handle rate limit errors"""
    return ResponseBuilder.error(
        "Rate limit exceeded. Please try again later.",
        status_code=429,
        error_code="RATE_LIMIT_EXCEEDED"
    )


@app.errorhandler(500)
def internal_error(e):
    """Handle internal errors"""
    logger.error(f"Internal error: {str(e)}", exc_info=True)
    return ResponseBuilder.error(
        "Internal server error",
        status_code=500,
        error_code="INTERNAL_ERROR"
    )


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)
