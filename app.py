"""
News Analyzer API - COMPLETE FIXED VERSION
CRITICAL FIX: Direct data extraction from NewsAnalyzer response
Eliminates complex extraction functions that were breaking the data flow
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
try:
    logger.info("=" * 80)
    logger.info("INITIALIZING NEWS ANALYZER")
    news_analyzer = NewsAnalyzer()
    logger.info("NewsAnalyzer initialized successfully")
    
    # Check available services
    available = news_analyzer.get_available_services()
    logger.info(f"Available services: {available}")
    
    # Log ScraperAPI status
    scraperapi_key = os.getenv('SCRAPERAPI_KEY')
    if scraperapi_key:
        logger.info(f"ScraperAPI: ENABLED (key ends with: ...{scraperapi_key[-4:]})")
    else:
        logger.info("ScraperAPI: NOT CONFIGURED")
    
    logger.info("=" * 80)
except Exception as e:
    logger.error(f"CRITICAL: Failed to initialize NewsAnalyzer: {str(e)}", exc_info=True)
    news_analyzer = None

def get_trust_level(score: int) -> str:
    """Convert trust score to level"""
    if score >= 80:
        return 'Very High'
    elif score >= 60:
        return 'High'
    elif score >= 40:
        return 'Medium'
    elif score >= 20:
        return 'Low'
    else:
        return 'Very Low'

# MAIN ROUTES

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': 'ready' if news_analyzer else 'initializing'
    })

@app.route('/api/analyze', methods=['POST'])
@limiter.limit("10 per minute")  # Rate limiting
def analyze():
    """
    COMPLETELY FIXED Main analysis endpoint
    CRITICAL FIX: Direct data extraction from NewsAnalyzer response
    """
    logger.info("=" * 80)
    logger.info("API ANALYZE ENDPOINT - DIRECT EXTRACTION VERSION")
    start_time = time.time()
    
    try:
        # Check if NewsAnalyzer is available
        if not news_analyzer:
            logger.error("NewsAnalyzer not initialized")
            return jsonify({
                'success': False,
                'error': 'Analysis service not available',
                'trust_score': 0,
                'article_summary': 'Service unavailable',
                'source': 'Unknown',
                'author': 'Unknown', 
                'findings_summary': 'Analysis service is not available.',
                'detailed_analysis': {}
            }), 500

        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided',
                'trust_score': 0,
                'article_summary': 'No data provided',
                'source': 'Unknown',
                'author': 'Unknown',
                'findings_summary': 'No data was provided for analysis.',
                'detailed_analysis': {}
            }), 400

        # Extract URL or text
        url = data.get('url', '').strip()
        text = data.get('text', '').strip()
        
        if not url and not text:
            return jsonify({
                'success': False,
                'error': 'URL or text required',
                'trust_score': 0,
                'article_summary': 'No content provided',
                'source': 'Unknown',
                'author': 'Unknown',
                'findings_summary': 'Either a URL or text content is required for analysis.',
                'detailed_analysis': {}
            }), 400
        
        logger.info(f"Analyzing: URL={url[:50] + '...' if url else 'None'}, Text={'Present' if text else 'None'}")
        
        # Run analysis through NewsAnalyzer
        try:
            pipeline_results = news_analyzer.analyze(
                content=url if url else text,
                content_type='url' if url else 'text'
            )
            
            logger.info(f"Pipeline completed. Success: {pipeline_results.get('success', False)}")
            logger.info(f"Pipeline keys: {list(pipeline_results.keys())}")
            
            # Check if pipeline succeeded
            if not pipeline_results.get('success', False):
                error_msg = pipeline_results.get('error', 'Analysis failed')
                return jsonify({
                    'success': False,
                    'error': error_msg,
                    'trust_score': 0,
                    'article_summary': 'Analysis failed',
                    'source': 'Unknown',
                    'author': 'Unknown',
                    'findings_summary': f'Analysis failed: {error_msg}',
                    'detailed_analysis': {}
                }), 500
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}", exc_info=True)
            return jsonify({
                'success': False,
                'error': f'Analysis failed: {str(e)}',
                'trust_score': 0,
                'article_summary': 'Analysis error',
                'source': 'Unknown',
                'author': 'Unknown',
                'findings_summary': f'Analysis failed: {str(e)}',
                'detailed_analysis': {}
            }), 500
        
        # CRITICAL FIX: Direct extraction from NewsAnalyzer response
        # The NewsAnalyzer is already returning the correct format - just use it directly!
        trust_score = pipeline_results.get('trust_score', 0)
        article_summary = pipeline_results.get('article_summary', 'Article summary not available')
        source = pipeline_results.get('source', 'Unknown')
        author = pipeline_results.get('author', 'Unknown')
        findings_summary = pipeline_results.get('findings_summary', 'Analysis completed.')
        detailed_analysis = pipeline_results.get('detailed_analysis', {})
        
        logger.info(f"Direct extraction results:")
        logger.info(f"  Trust Score: {trust_score}")
        logger.info(f"  Source: {source}")
        logger.info(f"  Author: {author}")
        logger.info(f"  Article Summary: {len(article_summary)} chars")
        logger.info(f"  Detailed Analysis Services: {len(detailed_analysis)}")
        
        # Build final response
        response_data = {
            'success': True,
            'trust_score': trust_score,
            'article_summary': article_summary,
            'source': source,
            'author': author,
            'findings_summary': findings_summary,
            'detailed_analysis': detailed_analysis,
            'processing_time': round(time.time() - start_time, 2),
            'timestamp': datetime.now().isoformat(),
            'services_analyzed': list(detailed_analysis.keys()),
            'trust_level': get_trust_level(trust_score)
        }
        
        logger.info(f"Analysis completed successfully in {response_data['processing_time']}s")
        logger.info(f"Final response - Trust Score: {trust_score}, Source: {source}, Author: {author}")
        logger.info(f"Services in response: {list(detailed_analysis.keys())}")
        logger.info("=" * 80)
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Critical analyze error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'System error: {str(e)}',
            'trust_score': 0,
            'article_summary': 'System error',
            'source': 'Unknown',
            'author': 'Unknown',
            'findings_summary': f'System error occurred: {str(e)}',
            'detailed_analysis': {}
        }), 500

@app.route('/api/test', methods=['GET', 'POST'])
def test_endpoint():
    """Test endpoint that returns simple data without analysis"""
    logger.info("TEST ENDPOINT HIT")
    
    # Check if NewsAnalyzer exists
    analyzer_status = "initialized" if news_analyzer else "failed"
    
    # Try to get service status
    try:
        registry = get_service_registry()
        service_status = registry.get_service_status()
        services = list(service_status.get('services', {}).keys())
    except Exception as e:
        services = f"Error: {str(e)}"
    
    # Check ScraperAPI status
    scraperapi_status = "enabled" if os.getenv('SCRAPERAPI_KEY') else "not configured"
    
    return jsonify({
        'success': True,
        'message': 'Test endpoint working',
        'news_analyzer': analyzer_status,
        'services': services,
        'scraperapi': scraperapi_status,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/status')
def api_status():
    """Simple status check"""
    scraperapi_available = bool(os.getenv('SCRAPERAPI_KEY'))
    
    return jsonify({
        'status': 'online', 
        'services': 'ready',
        'scraperapi': 'enabled' if scraperapi_available else 'not configured',
        'timestamp': datetime.now().isoformat()
    })

# Debug Routes
@app.route('/api/debug/services')
def debug_services():
    """Debug endpoint to check service status"""
    if not news_analyzer:
        return jsonify({'error': 'NewsAnalyzer not initialized'}), 500
    
    try:
        registry = get_service_registry()
        status = registry.get_service_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/config')
def debug_config():
    """Debug endpoint to check configuration (without exposing secrets)"""
    config_info = {
        'openai_configured': bool(Config.OPENAI_API_KEY),
        'scraperapi_configured': bool(Config.SCRAPERAPI_KEY),
        'scrapingbee_configured': bool(Config.SCRAPINGBEE_API_KEY),
        'google_factcheck_configured': bool(Config.GOOGLE_FACT_CHECK_API_KEY or Config.GOOGLE_FACTCHECK_API_KEY),
        'news_api_configured': bool(Config.NEWS_API_KEY or Config.NEWSAPI_KEY),
        'environment': Config.ENV,
        'debug': Config.DEBUG
    }
    
    return jsonify(config_info)

@app.route('/templates/<path:filename>')
def serve_template(filename):
    """Serve template files"""
    try:
        if '..' in filename or filename.startswith('/'):
            return "Invalid path", 400
        return send_from_directory('templates', filename)
    except Exception as e:
        return f"Error: {str(e)}", 500

# Error Handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Rate limit exceeded', 'message': str(e.description)}), 429

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
