"""
News Analyzer API - Fixed with proper data flow from backend to frontend
Main Flask application for analyzing news articles
"""
import os
import sys
import logging
import json
import traceback
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

# Configure logging with enhanced debugging
logging.basicConfig(
    level=Config.LOGGING['level'],
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
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

# Initialize services with debug logging
logger.info("=== INITIALIZING NEWS ANALYZER ===")
news_analyzer = NewsAnalyzer()
logger.info("=== NEWS ANALYZER INITIALIZED ===")

# Debug tracking - make it global so it's accessible everywhere
debug_info = {
    'requests': {},
    'errors': [],
    'service_calls': [],
    'initialization_log': []
}

# Request tracking
@app.before_request
def before_request():
    """Log incoming requests with enhanced debugging"""
    global debug_info
    request.id = str(uuid.uuid4())
    request.start_time = datetime.now()
    
    # Set request ID for response builder
    ResponseBuilder._request_id = request.id
    ResponseBuilder._start_time = int(datetime.now().timestamp() * 1000)
    
    # Store request info for debugging
    debug_info['requests'][request.id] = {
        'method': request.method,
        'path': request.path,
        'start_time': request.start_time.isoformat(),
        'headers': dict(request.headers),
        'remote_addr': request.remote_addr
    }
    
    # Log request details
    logger.info(f"Request {request.id}: {request.method} {request.path}")
    logger.debug(f"Request {request.id} headers: {dict(request.headers)}")
    
    if request.method == 'POST' and request.is_json:
        # Log POST data (be careful with sensitive data in production)
        data = request.get_json()
        if data:
            # Truncate long content for logging
            log_data = data.copy()
            if 'content' in log_data and len(str(log_data['content'])) > 100:
                log_data['content'] = str(log_data['content'])[:100] + '...'
            logger.debug(f"Request {request.id} data: {log_data}")
            debug_info['requests'][request.id]['data'] = log_data

@app.after_request
def after_request(response):
    """Log response details with enhanced debugging"""
    global debug_info
    if hasattr(request, 'id') and hasattr(request, 'start_time'):
        duration = (datetime.now() - request.start_time).total_seconds()
        
        # Update debug info
        if request.id in debug_info['requests']:
            debug_info['requests'][request.id]['response_code'] = response.status_code
            debug_info['requests'][request.id]['duration'] = duration
            debug_info['requests'][request.id]['end_time'] = datetime.now().isoformat()
        
        logger.info(f"Response {request.id}: {response.status_code} ({duration:.3f}s)")
        
        # Log response headers for debugging
        logger.debug(f"Response {request.id} headers: {dict(response.headers)}")
    
    # Add security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Add debug header in development
    if Config.DEBUG:
        response.headers['X-Request-ID'] = getattr(request, 'id', 'unknown')
    
    return response

# Error handlers with enhanced debugging
@app.errorhandler(400)
def bad_request(error):
    """Handle bad request errors"""
    global debug_info
    logger.warning(f"Bad request: {error}")
    debug_info['errors'].append({
        'timestamp': datetime.now().isoformat(),
        'type': 'bad_request',
        'error': str(error),
        'request_id': getattr(request, 'id', 'unknown')
    })
    response, status_code = ResponseBuilder.error("Bad Request", 400)
    return response, status_code

@app.errorhandler(404)
def not_found(error):
    """Handle not found errors"""
    global debug_info
    logger.warning(f"Not found: {request.path}")
    debug_info['errors'].append({
        'timestamp': datetime.now().isoformat(),
        'type': 'not_found',
        'path': request.path,
        'error': str(error),
        'request_id': getattr(request, 'id', 'unknown')
    })
    response, status_code = ResponseBuilder.error("Resource not found", 404)
    return response, status_code

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    global debug_info
    error_id = str(uuid.uuid4())
    logger.error(f"Internal server error {error_id}: {error}", exc_info=True)
    
    # Store detailed error info
    debug_info['errors'].append({
        'timestamp': datetime.now().isoformat(),
        'type': 'internal_error',
        'error_id': error_id,
        'error': str(error),
        'traceback': traceback.format_exc(),
        'request_id': getattr(request, 'id', 'unknown')
    })
    
    response, status_code = ResponseBuilder.error(f"Internal server error (Error ID: {error_id})", 500)
    return response, status_code

# Routes
@app.route('/')
def index():
    """Serve the main application page"""
    try:
        # Use Flask's render_template for templates folder
        from flask import render_template
        logger.debug(f"Rendering index.html from templates folder")
        return render_template('index.html')
        
    except Exception as e:
        logger.error(f"Error serving index: {e}", exc_info=True)
        # Try static folder as fallback
        try:
            index_path = os.path.join(app.static_folder, 'index.html')
            if os.path.exists(index_path):
                logger.debug(f"Serving index.html from static folder: {index_path}")
                return send_from_directory(app.static_folder, 'index.html')
        except:
            pass
        
        response, status_code = ResponseBuilder.error("Error loading main page", 500)
        return response, status_code

# TRUTHLENS STATIC FILE ROUTES WITH CORRECT MIME TYPES

@app.route('/truthlens-core.js')
def serve_truthlens_core():
    """Serve TruthLens core JavaScript with correct MIME type"""
    return serve_js_file('truthlens-core.js')

@app.route('/truthlens-display.js')
def serve_truthlens_display():
    """Serve TruthLens display JavaScript with correct MIME type"""
    return serve_js_file('truthlens-display.js')

@app.route('/truthlens-services.js')
def serve_truthlens_services():
    """Serve TruthLens services JavaScript with correct MIME type"""
    return serve_js_file('truthlens-services.js')

@app.route('/truthlens-styles.css')
def serve_truthlens_styles():
    """Serve TruthLens CSS with correct MIME type"""
    return serve_css_file('truthlens-styles.css')

def serve_js_file(filename):
    """Helper to serve JavaScript files with correct MIME type"""
    try:
        # Check multiple locations
        locations = [
            os.path.join(app.static_folder, filename),
            os.path.join(app.static_folder, 'js', filename),
            os.path.join('.', filename),
            os.path.join('static', filename),
            os.path.join('static', 'js', filename)
        ]
        
        for location in locations:
            if os.path.exists(location):
                logger.info(f"Serving {filename} from {location}")
                with open(location, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                response = make_response(content)
                response.headers['Content-Type'] = 'application/javascript; charset=utf-8'
                response.headers['Cache-Control'] = 'public, max-age=3600'
                return response
        
        logger.error(f"JavaScript file {filename} not found in any location")
        logger.error(f"Searched locations: {locations}")
        return f"// Error: {filename} not found", 404
        
    except Exception as e:
        logger.error(f"Error serving {filename}: {str(e)}")
        return f"// Error loading {filename}: {str(e)}", 500

def serve_css_file(filename):
    """Helper to serve CSS files with correct MIME type"""
    try:
        # Check multiple locations
        locations = [
            os.path.join(app.static_folder, filename),
            os.path.join(app.static_folder, 'css', filename),
            os.path.join('.', filename),
            os.path.join('static', filename),
            os.path.join('static', 'css', filename)
        ]
        
        for location in locations:
            if os.path.exists(location):
                logger.info(f"Serving {filename} from {location}")
                with open(location, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                response = make_response(content)
                response.headers['Content-Type'] = 'text/css; charset=utf-8'
                response.headers['Cache-Control'] = 'public, max-age=3600'
                return response
        
        logger.error(f"CSS file {filename} not found in any location")
        return "/* Error: file not found */", 404
        
    except Exception as e:
        logger.error(f"Error serving {filename}: {str(e)}")
        return f"/* Error loading {filename}: {str(e)} */", 500

# ORIGINAL API ROUTES

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/status')
def status():
    """Get system status with debugging info"""
    try:
        # Get configuration validation
        config_status = Config.validate()
        
        # Get service status from analyzer
        service_status = news_analyzer.get_service_status()
        
        # Add debug info
        debug_status = {
            'total_requests': len(debug_info['requests']),
            'recent_errors': len(debug_info['errors']),
            'active_services': sum(1 for s in service_status.values() if s.get('available', False))
        }
        
        return jsonify({
            'status': 'operational' if config_status['valid'] else 'degraded',
            'config': config_status,
            'services': service_status,
            'debug': debug_status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        response, status_code = ResponseBuilder.error("Status check failed", 500)
        return response, status_code

@app.route('/api/test')
def test_endpoint():
    """Simple test endpoint to verify new code is deployed"""
    return jsonify({
        'status': 'ok',
        'message': 'Debug-enhanced app with proper data flow is running',
        'timestamp': datetime.now().isoformat(),
        'debug_routes': [
            '/api/debug/info',
            '/api/debug/services', 
            '/api/debug/test-analyze',
            '/api/debug/clear'
        ]
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Analyze a news article with enhanced debugging and proper data flow
    
    Expected JSON payload:
    {
        "url": "https://example.com/article" OR "text": "Article content...",
        "type": "url" or "text",
        "options": {
            "pro_mode": true/false
        }
    }
    """
    global debug_info
    try:
        # Start timing
        analysis_start = time.time()
        
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
        
        # Track service call
        service_call_id = str(uuid.uuid4())
        debug_info['service_calls'].append({
            'id': service_call_id,
            'timestamp': datetime.now().isoformat(),
            'request_id': request.id,
            'type': 'analyze',
            'content_type': content_type,
            'options': options
        })
        
        # Perform analysis with detailed logging
        logger.debug(f"Calling news_analyzer.analyze with content_type={content_type}")
        result = news_analyzer.analyze(
            content=content,
            content_type=content_type,
            pro_mode=options.get('pro_mode', False)
        )
        
        # Log analysis completion
        analysis_duration = time.time() - analysis_start
        logger.info(f"Analysis completed in {analysis_duration:.3f}s, success={result.get('success', False)}")
        
        # Update service call tracking
        for call in debug_info['service_calls']:
            if call['id'] == service_call_id:
                call['duration'] = analysis_duration
                call['success'] = result.get('success', False)
                if not result.get('success', False):
                    call['error'] = result.get('error', 'Unknown error')
        
        # Build response based on success/failure
        if result.get('success', False):
            # CRITICAL FIX: Transform the result to include service data properly
            transformed_result = transform_analysis_result(result)
            
            # Log what we're sending to frontend
            logger.info(f"=== SENDING TO FRONTEND ===")
            logger.info(f"Trust score: {transformed_result.get('trust_score')}")
            logger.info(f"Services included: {list(transformed_result.get('services', {}).keys())}")
            
            return jsonify(transformed_result)
        else:
            # Extract error message
            error_msg = result.get('error', 'Analysis failed')
            logger.error(f"Analysis failed: {error_msg}")
            
            # Log failed stages if available
            if 'pipeline_metadata' in result:
                failed_stages = result['pipeline_metadata'].get('failed_stages', {})
                if failed_stages:
                    logger.error(f"Failed stages: {failed_stages}")
            
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

def transform_analysis_result(result):
    """
    Transform the analysis result to match frontend expectations
    This is the CRITICAL function that ensures data flows properly
    """
    # Log the incoming result structure for debugging
    logger.debug(f"=== TRANSFORM INPUT ===")
    logger.debug(f"Result keys: {list(result.keys())}")
    
    # Extract base data
    article_data = result.get('article', {})
    pipeline_metadata = result.get('pipeline_metadata', {})
    
    # Build the transformed response
    transformed = {
        'success': True,
        'status': 'completed',
        'timestamp': datetime.now().isoformat(),
        
        # Trust score and level
        'trust_score': result.get('trust_score', 50),
        'trust_level': result.get('trust_level', 'Unknown'),
        
        # Article information
        'article': {
            'url': article_data.get('url', ''),
            'title': article_data.get('title', 'Untitled'),
            'author': article_data.get('author', 'Unknown'),
            'publish_date': article_data.get('publish_date', ''),
            'domain': article_data.get('domain', ''),
            'content': article_data.get('content', ''),
            'excerpt': article_data.get('excerpt', ''),
            'word_count': article_data.get('word_count', 0),
            'reading_time': article_data.get('reading_time', 0)
        },
        
        # Summary and recommendations
        'summary': result.get('summary', {}),
        'recommendations': result.get('recommendations', []),
        
        # CRITICAL: Service results mapped to frontend structure
        'services': {}
    }
    
    # Service names to check for in the result
    service_names = [
        'fact_checker',
        'author_analyzer', 
        'bias_detector',
        'source_credibility',
        'transparency_analyzer',
        'manipulation_detector',
        'content_analyzer'
    ]
    
    # Extract service results from the result object
    # Services might be at top level or nested in a 'services' key
    services_data = result.get('services', {})
    
    for service_name in service_names:
        # Check multiple possible locations for service data
        service_data = None
        
        # First check if it's a top-level key
        if service_name in result:
            service_data = result[service_name]
        # Then check if it's in services object
        elif service_name in services_data:
            service_data = services_data[service_name]
        # Also check with underscores replaced by hyphens
        elif service_name.replace('_', '-') in result:
            service_data = result[service_name.replace('_', '-')]
        
        if service_data and isinstance(service_data, dict):
            # Handle different possible structures
            # Some services might have success/data/metadata structure
            if 'success' in service_data and service_data['success']:
                transformed['services'][service_name] = {
                    'success': True,
                    'timestamp': service_data.get('timestamp', datetime.now().isoformat()),
                    'data': service_data.get('data', service_data),
                    'metadata': service_data.get('metadata', {})
                }
            # Others might have the data directly
            elif any(key in service_data for key in ['score', 'results', 'analysis', 'findings']):
                transformed['services'][service_name] = {
                    'success': True,
                    'timestamp': service_data.get('timestamp', datetime.now().isoformat()),
                    'data': service_data,
                    'metadata': {}
                }
            
            logger.debug(f"Added {service_name} to services")
    
    # Add metadata
    transformed['metadata'] = {
        'processing_time': pipeline_metadata.get('total_duration', 0),
        'services_used': list(transformed['services'].keys()),
        'successful_services': len(transformed['services']),
        'pipeline_stages': pipeline_metadata.get('stages_completed', {}),
        'errors': result.get('errors', [])
    }
    
    # Add trust breakdown based on available services
    trust_components = {}
    
    for service_name, service_result in transformed['services'].items():
        service_data = service_result.get('data', {})
        
        # Extract scores based on service type
        if service_name == 'fact_checker':
            # Look for various possible score fields
            score = (service_data.get('accuracy_score') or 
                    service_data.get('fact_score') or 
                    service_data.get('score') or 50)
            trust_components['fact_accuracy'] = score
            
        elif service_name == 'author_analyzer':
            score = (service_data.get('credibility_score') or 
                    service_data.get('author_score') or 
                    service_data.get('score') or 50)
            trust_components['author_credibility'] = score
            
        elif service_name == 'bias_detector':
            # Bias score needs to be inverted for trust
            bias_score = (service_data.get('bias_score') or 
                         service_data.get('score') or 50)
            trust_components['objectivity'] = max(0, 100 - bias_score)
            
        elif service_name == 'source_credibility':
            score = (service_data.get('credibility_score') or 
                    service_data.get('reputation_score') or 
                    service_data.get('score') or 50)
            trust_components['source_reputation'] = score
            
        elif service_name == 'transparency_analyzer':
            score = (service_data.get('transparency_score') or 
                    service_data.get('score') or 50)
            trust_components['transparency'] = score
            
        elif service_name == 'manipulation_detector':
            # Manipulation score needs to be inverted
            manip_score = (service_data.get('manipulation_score') or 
                          service_data.get('score') or 50)
            trust_components['authenticity'] = max(0, 100 - manip_score)
    
    transformed['trust_breakdown'] = trust_components
    
    # Calculate overall metrics if we have components
    if trust_components:
        transformed['overall_metrics'] = {
            'average_trust': sum(trust_components.values()) / len(trust_components),
            'lowest_score': min(trust_components.values()),
            'highest_score': max(trust_components.values()),
            'components_analyzed': len(trust_components)
        }
    
    # Log the output
    logger.debug(f"=== TRANSFORM OUTPUT ===")
    logger.debug(f"Services included: {list(transformed['services'].keys())}")
    logger.debug(f"Trust components: {list(trust_components.keys())}")
    
    return transformed

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

# ENHANCED DEBUG ENDPOINTS

@app.route('/api/debug/info', methods=['GET'])
def debug_full_info():
    """Get comprehensive debug information"""
    global debug_info
    try:
        # Clean up old requests (keep last 100)
        if len(debug_info['requests']) > 100:
            sorted_requests = sorted(debug_info['requests'].items(), 
                                   key=lambda x: x[1].get('start_time', ''), 
                                   reverse=True)
            debug_info['requests'] = dict(sorted_requests[:100])
        
        # Keep last 50 errors
        if len(debug_info['errors']) > 50:
            debug_info['errors'] = debug_info['errors'][-50:]
        
        # Keep last 100 service calls
        if len(debug_info['service_calls']) > 100:
            debug_info['service_calls'] = debug_info['service_calls'][-100:]
        
        return jsonify({
            'requests': debug_info['requests'],
            'errors': debug_info['errors'],
            'service_calls': debug_info['service_calls'],
            'initialization_log': debug_info['initialization_log'],
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Debug info endpoint error: {e}", exc_info=True)
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/debug/services', methods=['GET'])
def debug_services():
    """Debug endpoint to check service status with detailed info"""
    global debug_info
    try:
        from services.service_registry import service_registry
        from config import Config
        
        logger.debug("=== DEBUG SERVICES ENDPOINT ===")
        
        # Get service registry status
        registry_status = service_registry.get_service_status()
        
        # Try to get pipeline info
        pipeline_info = None
        try:
            from services.analysis_pipeline import AnalysisPipeline
            pipeline = AnalysisPipeline()
            
            # Get pipeline stages info
            stages_info = []
            for stage in pipeline.stages:
                # Get available services for this stage
                available_services = []
                unavailable_services = []
                
                for service_name in stage.services:
                    service = service_registry.get_service(service_name)
                    if service:
                        if service.is_available:
                            available_services.append(service_name)
                        else:
                            unavailable_services.append({
                                'name': service_name,
                                'reason': 'is_available returned False'
                            })
                    else:
                        unavailable_services.append({
                            'name': service_name,
                            'reason': 'Not found in registry'
                        })
                
                stages_info.append({
                    'name': stage.name,
                    'configured_services': stage.services,
                    'available_services': available_services,
                    'unavailable_services': unavailable_services,
                    'required': stage.required
                })
            
            pipeline_info = {
                'stages': stages_info,
                'total_stages': len(stages_info)
            }
        except Exception as e:
            pipeline_info = {'error': str(e)}
        
        # Check article_extractor specifically
        article_extractor = service_registry.get_service('article_extractor')
        article_extractor_info = None
        if article_extractor:
            article_extractor_info = {
                'found': True,
                'is_available': article_extractor.is_available,
                'service_name': getattr(article_extractor, 'service_name', 'MISSING'),
                'class_name': article_extractor.__class__.__name__,
                'attributes': {
                    'has_extract_method': hasattr(article_extractor, 'extract'),
                    'has_analyze_method': hasattr(article_extractor, 'analyze'),
                    '_available': getattr(article_extractor, '_available', 'MISSING')
                }
            }
        else:
            article_extractor_info = {'found': False}
        
        # Check config
        config_info = {
            'article_extractor_enabled': Config.is_service_enabled('article_extractor'),
            'services_configured': list(Config.SERVICES.keys()),
            'pipeline_stages': getattr(Config, 'PIPELINE_STAGES', 'NOT FOUND'),
            'service_to_stage': getattr(Config, 'SERVICE_TO_STAGE', 'NOT FOUND')
        }
        
        # Get all registered services details
        all_services_details = {}
        for name, service in service_registry.services.items():
            all_services_details[name] = {
                'class_name': service.__class__.__name__,
                'is_available': service.is_available,
                'has_analyze': hasattr(service, 'analyze'),
                'has_extract': hasattr(service, 'extract') if name == 'article_extractor' else False
            }
        
        debug_data = {
            'registry_status': registry_status,
            'article_extractor': article_extractor_info,
            'pipeline': pipeline_info,
            'config': config_info,
            'all_services_details': all_services_details,
            'all_registered_services': list(service_registry.services.keys()),
            'all_async_services': list(service_registry.async_services.keys()),
            'failed_services': service_registry.failed_services,
            'initialization_errors': debug_info.get('initialization_log', [])
        }
        
        return jsonify(debug_data), 200
        
    except Exception as e:
        logger.error(f"Debug endpoint error: {e}", exc_info=True)
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/debug/test-analyze', methods=['POST'])
def debug_test_analyze():
    """Test analysis with detailed debugging output"""
    try:
        data = request.get_json() or {}
        test_url = data.get('url', 'https://www.bbc.com/news/world-us-canada-12345678')
        
        logger.info(f"=== DEBUG TEST ANALYZE: {test_url} ===")
        
        # Track each step
        steps = []
        
        # Step 1: Check service availability
        steps.append({
            'step': 'Check Services',
            'timestamp': datetime.now().isoformat(),
            'services': news_analyzer.get_service_status()
        })
        
        # Step 2: Try to analyze
        try:
            result = news_analyzer.analyze(
                content=test_url,
                content_type='url',
                pro_mode=False
            )
            
            # Log raw result structure
            logger.debug(f"Raw result keys: {list(result.keys())}")
            
            # Transform the result
            if result.get('success', False):
                transformed_result = transform_analysis_result(result)
                
                steps.append({
                    'step': 'Analysis Complete',
                    'timestamp': datetime.now().isoformat(),
                    'success': True,
                    'services_in_result': list(transformed_result.get('services', {}).keys()),
                    'trust_score': transformed_result.get('trust_score'),
                    'trust_components': transformed_result.get('trust_breakdown', {})
                })
                
                final_result = transformed_result
            else:
                steps.append({
                    'step': 'Analysis Failed',
                    'timestamp': datetime.now().isoformat(),
                    'success': False,
                    'error': result.get('error', 'Unknown error')
                })
                final_result = result
            
        except Exception as e:
            steps.append({
                'step': 'Analysis Exception',
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'traceback': traceback.format_exc()
            })
            final_result = {'success': False, 'error': str(e)}
        
        return jsonify({
            'test_url': test_url,
            'result': final_result,
            'debug_steps': steps,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Debug test analyze error: {e}", exc_info=True)
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/debug/clear', methods=['POST'])
def debug_clear():
    """Clear debug information"""
    global debug_info
    try:
        debug_info['requests'].clear()
        debug_info['errors'].clear()
        debug_info['service_calls'].clear()
        
        return jsonify({
            'status': 'cleared',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Enhanced static file serving with proper MIME types
@app.route('/<path:path>')
def serve_static(path):
    """Serve static files with correct MIME types"""
    # Security check - prevent directory traversal
    if '..' in path or path.startswith('/'):
        response, status_code = ResponseBuilder.error("Invalid path", 400)
        return response, status_code
    
    # Determine MIME type based on file extension
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
        '.ico': 'image/x-icon'
    }
    
    # Get file extension
    _, ext = os.path.splitext(path)
    mime_type = mime_types.get(ext.lower(), 'application/octet-stream')
    
    # Try to find and serve the file
    try:
        # Check multiple possible locations
        possible_paths = [
            os.path.join(app.static_folder, path),
            os.path.join('.', path),
            path
        ]
        
        # Special handling for JS files that might be in a js/ subdirectory
        if ext == '.js' and not path.startswith('js/'):
            possible_paths.append(os.path.join(app.static_folder, 'js', path))
        
        for file_path in possible_paths:
            if os.path.exists(file_path) and os.path.isfile(file_path):
                logger.info(f"Serving {path} from {file_path} with MIME type {mime_type}")
                
                # Read file and create response with correct MIME type
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                response = make_response(content)
                response.headers['Content-Type'] = f'{mime_type}; charset=utf-8' if mime_type.startswith('text/') or mime_type == 'application/javascript' else mime_type
                response.headers['Cache-Control'] = 'public, max-age=3600'
                
                return response
        
        # File not found
        logger.debug(f"Static file not found: {path}")
        # Don't return error for common missing files
        if path in ['favicon.ico', 'robots.txt']:
            return '', 404
        response, status_code = ResponseBuilder.error("File not found", 404)
        return response, status_code
        
    except Exception as e:
        logger.error(f"Error serving static file {path}: {e}")
        response, status_code = ResponseBuilder.error("Error serving file", 500)
        return response, status_code

# Startup initialization tracking
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
