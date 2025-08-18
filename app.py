import os
import logging
import traceback
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory, make_response
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

# Import services
from services.news_analyzer import NewsAnalyzer
from services.analysis_pipeline import AnalysisPipeline
from services.service_registry import ServiceRegistry
from utils.config import Config
from utils.response_builder import ResponseBuilder

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
    static_folder='static',
    template_folder='templates'
)

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configure rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Initialize services
try:
    logger.info("Initializing services...")
    config = Config()
    registry = ServiceRegistry()
    pipeline = AnalysisPipeline(registry)
    analyzer = NewsAnalyzer(pipeline)
    logger.info("Services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {e}", exc_info=True)
    analyzer = None

# Debug info storage
debug_info = {
    'requests': [],
    'errors': [],
    'service_calls': []
}

# MAIN ROUTE - SERVE INDEX.HTML
@app.route('/')
def index():
    """Serve the main application page"""
    try:
        logger.info("Serving index page")
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering template: {e}", exc_info=True)
        return f"Error loading page: {str(e)}", 500

# STATIC FILE ROUTES
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

# API ROUTES
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
        config_status = Config.validate()
        
        return jsonify({
            'status': 'operational',
            'version': '1.0.0',
            'services': {
                'analyzer': analyzer is not None,
                'registry': ServiceRegistry.get_available_services() if analyzer else []
            },
            'config': config_status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
@limiter.limit("10 per minute")
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
        debug_info['requests'].append({
            'timestamp': datetime.now().isoformat(),
            'data': data,
            'ip': get_remote_address()
        })
        
        # Extract URL or text
        url = data.get('url')
        text = data.get('text')
        
        if not url and not text:
            return ResponseBuilder.error("Please provide either 'url' or 'text'", 400)
        
        if not analyzer:
            return ResponseBuilder.error("Analysis service unavailable", 503)
        
        # Perform analysis
        logger.info(f"Analyzing: {url if url else 'text content'}")
        
        if url:
            result = analyzer.analyze_url(url)
        else:
            result = analyzer.analyze_text(text)
        
        if result.get('success'):
            # Build response with all service results
            response_data = {
                'success': True,
                'data': {
                    'trust_score': result.get('trust_score', 0),
                    'trust_level': result.get('trust_level', 'unknown'),
                    'services': result.get('services', {}),
                    'metadata': result.get('metadata', {}),
                    'summary': result.get('summary', {}),
                    'timestamp': datetime.now().isoformat()
                }
            }
            return jsonify(response_data), 200
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

# DEBUG ROUTES
@app.route('/api/debug/info')
def debug_get_info():
    """Get debug information"""
    return jsonify(debug_info)

@app.route('/api/debug/test')
def debug_test():
    """Test endpoint for debugging"""
    try:
        test_result = {
            'analyzer_available': analyzer is not None,
            'services': ServiceRegistry.get_available_services() if analyzer else [],
            'config_valid': Config.validate(),
            'timestamp': datetime.now().isoformat()
        }
        return jsonify(test_result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ERROR HANDLERS
@app.errorhandler(404)
def not_found(e):
    return ResponseBuilder.error("Resource not found", 404)

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {e}", exc_info=True)
    return ResponseBuilder.error("Internal server error", 500)

@app.errorhandler(429)
def rate_limit_exceeded(e):
    return ResponseBuilder.error("Rate limit exceeded. Please try again later.", 429)

# Run the application
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting TruthLens server on port {port}")
    logger.info(f"Debug mode: {debug_mode}")
    logger.info(f"Static folder: {app.static_folder}")
    logger.info(f"Template folder: {app.template_folder}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode
    )
