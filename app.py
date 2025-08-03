"""
Simplified News Analyzer API
Clean, maintainable, and focused on what works
"""
import os
import logging
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from datetime import datetime
from typing import Dict, Any, Optional

# Import only the essential services
from services.article_extractor import ArticleExtractor
from services.news_analyzer import NewsAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app with explicit static folder configuration
app = Flask(__name__, 
            static_folder='static',
            static_url_path='/static')
CORS(app)

# Fix the incomplete line - use environment variable with fallback
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')

# Initialize services
try:
    article_extractor = ArticleExtractor()
    news_analyzer = NewsAnalyzer()
    logger.info("Services initialized successfully")
except Exception as e:
    logger.error(f"Error initializing services: {e}")
    article_extractor = None
    news_analyzer = None

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/health')
def health():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            'article_extractor': article_extractor is not None,
            'news_analyzer': news_analyzer is not None
        }
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Main analysis endpoint
    Accepts: { "url": "https://..." } or { "text": "article content..." }
    Returns: Comprehensive analysis with trust score
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Determine content type and content
        url = data.get('url')
        text = data.get('text')
        
        if url:
            content = url
            content_type = 'url'
            logger.info(f"Analyzing URL: {url}")
        elif text:
            content = text
            content_type = 'text'
            logger.info("Analyzing text content")
        else:
            return jsonify({
                'success': False,
                'error': 'Either URL or text is required'
            }), 400
        
        # Check if services are available
        if not news_analyzer:
            return jsonify({
                'success': False,
                'error': 'Analysis service is temporarily unavailable'
            }), 503
        
        # Determine if user is pro (for now, default to basic)
        is_pro = data.get('is_pro', False)
        
        # Perform analysis
        result = news_analyzer.analyze(content, content_type=content_type, is_pro=is_pro)
        
        # Check if analysis was successful
        if not result.get('success', False):
            error_msg = result.get('error', 'Analysis failed')
            logger.error(f"Analysis failed: {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
        logger.info(f"Analysis completed successfully. Trust score: {result.get('trust_score', 'N/A')}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500

@app.route('/api/extract', methods=['POST'])
def extract():
    """
    Article extraction endpoint
    Accepts: { "url": "https://..." }
    Returns: Extracted article content
    """
    try:
        data = request.get_json()
        if not data or not data.get('url'):
            return jsonify({
                'success': False,
                'error': 'URL is required'
            }), 400
        
        url = data.get('url')
        logger.info(f"Extracting article from: {url}")
        
        if not article_extractor:
            return jsonify({
                'success': False,
                'error': 'Extraction service is temporarily unavailable'
            }), 503
        
        # Extract article
        result = article_extractor.extract_from_url(url)
        
        if not result.get('success', False):
            error_msg = result.get('error', 'Extraction failed')
            logger.error(f"Extraction failed: {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Extraction error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Extraction failed: {str(e)}'
        }), 500

# Serve static files explicitly (helps with some deployment environments)
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory(app.static_folder, filename)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Get port from environment variable (for deployment)
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
