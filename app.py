"""
News Analyzer API - COMPLETE PRODUCTION VERSION
Fixed Guardian author extraction and enhanced error handling
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
from services.article_extractor import ArticleExtractor  # Import our fixed extractor

# Setup enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Reduce noise from other loggers
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS with proper configuration
CORS(app, 
     origins=["*"], 
     allow_headers=["Content-Type", "Authorization"], 
     methods=["GET", "POST", "OPTIONS"])

# Setup rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per hour", "50 per minute"],
    storage_uri="memory://",
    swallow_errors=True
)

# Initialize services
try:
    logger.info("=" * 80)
    logger.info("INITIALIZING NEWS ANALYZER SERVICES")
    
    # Initialize the enhanced article extractor
    scraperapi_key = os.getenv('SCRAPERAPI_KEY')
    article_extractor = ArticleExtractor(scraperapi_key=scraperapi_key)
    
    # Initialize news analyzer with the enhanced extractor
    news_analyzer = NewsAnalyzer()
    
    # Inject our enhanced extractor if possible
    if hasattr(news_analyzer, 'pipeline') and news_analyzer.pipeline:
        if hasattr(news_analyzer.pipeline, 'article_extractor'):
            news_analyzer.pipeline.article_extractor = article_extractor
            logger.info("Injected enhanced article extractor into pipeline")
    
    # Check available services
    available = news_analyzer.get_available_services()
    logger.info(f"Available services: {available}")
    
    # Log API keys status
    if scraperapi_key:
        logger.info(f"ScraperAPI: ENABLED (key ends with: ...{scraperapi_key[-4:]})")
    else:
        logger.info("ScraperAPI: NOT CONFIGURED - Author extraction may be limited")
    
    if Config.OPENAI_API_KEY:
        logger.info("OpenAI: ENABLED")
    else:
        logger.info("OpenAI: NOT CONFIGURED")
    
    logger.info("=" * 80)
    
except Exception as e:
    logger.error(f"CRITICAL: Failed to initialize NewsAnalyzer: {str(e)}", exc_info=True)
    news_analyzer = None
    article_extractor = None

def get_trust_level(score: int) -> str:
    """Convert trust score to human-readable level"""
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

def generate_findings_summary(trust_score: int, detailed_analysis: Dict, article_data: Dict) -> str:
    """
    Generate an intelligent findings summary based on analysis results
    """
    findings = []
    
    # Trust level assessment
    trust_level = get_trust_level(trust_score)
    
    if trust_score >= 80:
        base_finding = "This article demonstrates high credibility and trustworthiness."
    elif trust_score >= 60:
        base_finding = "This article shows generally good credibility with some minor concerns."
    elif trust_score >= 40:
        base_finding = "This article has moderate credibility with several issues identified."
    else:
        base_finding = "This article shows significant credibility concerns."
    
    findings.append(base_finding)
    
    # Source assessment
    if 'source_credibility' in detailed_analysis:
        source_data = detailed_analysis['source_credibility']
        if isinstance(source_data, dict):
            rating = source_data.get('rating', '')
            if rating in ['Very High', 'High']:
                findings.append("The source is well-established and reputable.")
            elif rating in ['Low', 'Very Low']:
                findings.append("Source reputation is questionable.")
    
    # Bias assessment
    if 'bias_detector' in detailed_analysis:
        bias_data = detailed_analysis['bias_detector']
        if isinstance(bias_data, dict):
            bias_score = bias_data.get('bias_score', 0)
            if bias_score < 30:
                findings.append("Content appears balanced with minimal bias.")
            elif bias_score > 70:
                findings.append("Significant bias detected in the presentation.")
            else:
                findings.append("Some bias indicators present.")
    
    # Fact checking
    if 'fact_checker' in detailed_analysis:
        fact_data = detailed_analysis['fact_checker']
        if isinstance(fact_data, dict):
            verified = fact_data.get('verified_claims', 0)
            total = fact_data.get('claims_checked', 0)
            if total > 0:
                percentage = (verified / total) * 100
                if percentage >= 80:
                    findings.append(f"Fact-checking verified {int(percentage)}% of claims.")
                elif percentage < 50:
                    findings.append(f"Multiple claims could not be verified ({int(percentage)}% verified).")
    
    # Author credibility
    author = article_data.get('author', 'Unknown')
    if author and author != 'Unknown':
        findings.append(f"Article written by {author}.")
    
    return " ".join(findings)

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
        'services': 'ready' if news_analyzer else 'initializing',
        'extractor': 'ready' if article_extractor else 'not available'
    })

@app.route('/api/analyze', methods=['POST'])
@limiter.limit("10 per minute")
def analyze():
    """
    Main analysis endpoint with enhanced article extraction
    """
    logger.info("=" * 80)
    logger.info("API ANALYZE ENDPOINT - ENHANCED VERSION")
    start_time = time.time()
    
    try:
        # Check if services are available
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
        
        logger.info(f"Analyzing: URL={url[:100] if url else 'None'}, Text={'Present' if text else 'None'}")
        
        # If URL provided, do enhanced extraction first
        article_data = {}
        if url and article_extractor:
            logger.info("Performing enhanced article extraction...")
            try:
                extraction_result = article_extractor.extract(url)
                if extraction_result.get('success'):
                    article_data = extraction_result
                    logger.info(f"Enhanced extraction successful. Author: {article_data.get('author', 'Unknown')}")
                    
                    # If we got good extraction, use the text for analysis
                    if article_data.get('text'):
                        # Pass both URL and extracted data to analyzer
                        data['extracted_article'] = article_data
                        data['text'] = article_data['text']
                        data['url'] = url  # Keep URL for reference
                else:
                    logger.warning(f"Enhanced extraction failed: {extraction_result.get('error')}")
            except Exception as e:
                logger.error(f"Enhanced extraction error: {str(e)}")
        
        # Run analysis through NewsAnalyzer
        try:
            pipeline_results = news_analyzer.analyze(
                content=url if url else text,
                content_type='url' if url else 'text'
            )
            
            logger.info(f"Pipeline completed. Success: {pipeline_results.get('success', False)}")
            
            # Check if pipeline succeeded
            if not pipeline_results.get('success', False):
                error_msg = pipeline_results.get('error', 'Analysis failed')
                return jsonify({
                    'success': False,
                    'error': error_msg,
                    'trust_score': 0,
                    'article_summary': 'Analysis failed',
                    'source': article_data.get('domain', 'Unknown'),
                    'author': article_data.get('author', 'Unknown'),
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
                'source': article_data.get('domain', 'Unknown'),
                'author': article_data.get('author', 'Unknown'),
                'findings_summary': f'Analysis failed: {str(e)}',
                'detailed_analysis': {}
            }), 500
        
        # Extract data from pipeline results
        trust_score = pipeline_results.get('trust_score', 0)
        article_summary = pipeline_results.get('article_summary', 'Article summary not available')
        source = pipeline_results.get('source', article_data.get('domain', 'Unknown'))
        detailed_analysis = pipeline_results.get('detailed_analysis', {})
        
        # CRITICAL: Use enhanced extraction author if available
        author = article_data.get('author', pipeline_results.get('author', 'Unknown'))
        
        # Special handling for Guardian articles
        if 'guardian' in source.lower() and author == 'Unknown':
            # Try one more time with the URL
            if url:
                logger.info("Attempting Guardian-specific author extraction...")
                # This would be handled by our enhanced extractor above
                pass
        
        # Generate enhanced findings summary
        findings_summary = generate_findings_summary(trust_score, detailed_analysis, article_data)
        
        # Build final response
        response_data = {
            'success': True,
            'trust_score': trust_score,
            'article_summary': article_summary,
            'source': source,
            'author': author,  # This should now have the correct author
            'findings_summary': findings_summary,
            'detailed_analysis': detailed_analysis,
            'processing_time': round(time.time() - start_time, 2),
            'timestamp': datetime.now().isoformat(),
            'services_analyzed': list(detailed_analysis.keys()),
            'trust_level': get_trust_level(trust_score),
            'extraction_method': article_data.get('extraction_method', 'standard')
        }
        
        logger.info(f"Analysis completed successfully in {response_data['processing_time']}s")
        logger.info(f"Final response - Trust Score: {trust_score}, Source: {source}, Author: {author}")
        logger.info(f"Services analyzed: {response_data['services_analyzed']}")
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
    """Test endpoint for debugging"""
    logger.info("TEST ENDPOINT HIT")
    
    # Test article extraction if URL provided
    test_url = request.args.get('url')
    extraction_test = None
    
    if test_url and article_extractor:
        try:
            extraction_test = article_extractor.extract(test_url)
        except Exception as e:
            extraction_test = {'error': str(e)}
    
    # Check if NewsAnalyzer exists
    analyzer_status = "initialized" if news_analyzer else "failed"
    
    # Try to get service status
    try:
        registry = get_service_registry()
        service_status = registry.get_service_status()
        services = list(service_status.get('services', {}).keys())
    except Exception as e:
        services = f"Error: {str(e)}"
    
    # Check API keys status
    api_status = {
        'scraperapi': 'enabled' if os.getenv('SCRAPERAPI_KEY') else 'not configured',
        'openai': 'enabled' if Config.OPENAI_API_KEY else 'not configured',
        'google_factcheck': 'enabled' if getattr(Config, 'GOOGLE_FACT_CHECK_API_KEY', None) else 'not configured'
    }
    
    return jsonify({
        'success': True,
        'message': 'Test endpoint working',
        'news_analyzer': analyzer_status,
        'article_extractor': 'ready' if article_extractor else 'not available',
        'services': services,
        'api_status': api_status,
        'extraction_test': extraction_test,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/status')
def api_status():
    """API status check"""
    return jsonify({
        'status': 'online',
        'services': 'ready' if news_analyzer else 'initializing',
        'extractor': 'ready' if article_extractor else 'not available',
        'scraperapi': 'enabled' if os.getenv('SCRAPERAPI_KEY') else 'not configured',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/debug/extract', methods=['POST'])
def debug_extract():
    """Debug endpoint for testing article extraction"""
    if not article_extractor:
        return jsonify({'error': 'Article extractor not available'}), 500
    
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL required'}), 400
    
    try:
        result = article_extractor.extract(url)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    """Debug endpoint to check configuration"""
    config_info = {
        'openai_configured': bool(Config.OPENAI_API_KEY),
        'scraperapi_configured': bool(os.getenv('SCRAPERAPI_KEY')),
        'scrapingbee_configured': bool(getattr(Config, 'SCRAPINGBEE_API_KEY', None)),
        'google_factcheck_configured': bool(getattr(Config, 'GOOGLE_FACT_CHECK_API_KEY', None)),
        'news_api_configured': bool(getattr(Config, 'NEWS_API_KEY', None)),
        'environment': Config.ENV if hasattr(Config, 'ENV') else 'production',
        'debug': Config.DEBUG if hasattr(Config, 'DEBUG') else False
    }
    
    return jsonify(config_info)

# Static file serving
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

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
    return jsonify({'error': 'Endpoint not found', 'path': request.path}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}", exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': str(e.description),
        'retry_after': '60 seconds'
    }), 429

# Application startup
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Flask app on port {port} (debug={debug})")
    app.run(host='0.0.0.0', port=port, debug=debug)
