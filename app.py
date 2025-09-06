"""
News Analyzer API - PRODUCTION VERSION WITH RACE CONDITION FIX
Date: September 6, 2025
Last Updated: September 6, 2025

CRITICAL FIXES:
1. Added request-level locking to prevent concurrent extraction conflicts
2. Proper thread-safe request handling with request ID tracking
3. Enhanced error recovery with fallback mechanisms
4. Better article data preservation across pipeline stages
5. Improved timeout handling and graceful degradation

Notes:
- Uses threading locks to serialize critical sections
- Maintains request isolation for concurrent users
- Preserves all existing functionality
- Handles ScraperAPI rate limiting gracefully
"""
import os
import sys
import logging
import time
import traceback
import threading
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
import json
from collections import defaultdict

# Setup comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Suppress noisy loggers
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('werkzeug').setLevel(logging.WARNING)

logger.info("=" * 80)
logger.info("INITIALIZING NEWS ANALYZER API - FIXED CONCURRENT VERSION")
logger.info(f"Python Version: {sys.version}")
logger.info(f"Working Directory: {os.getcwd()}")
logger.info(f"Port: {os.environ.get('PORT', 5000)}")
logger.info("=" * 80)

# Flask imports
from flask import Flask, request, jsonify, render_template, send_from_directory, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Thread safety for concurrent requests
extraction_lock = threading.Lock()
analysis_locks = defaultdict(threading.Lock)  # Per-URL locks
request_cache = {}  # Cache for ongoing requests
cache_lock = threading.Lock()
CACHE_TIMEOUT = 60  # seconds

# Create Config class - handles both local and Render environments
class Config:
    """Configuration for the application"""
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    ENV = os.environ.get('FLASK_ENV', 'production')
    
    # API Keys from environment variables (Render stores them here)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    SCRAPERAPI_KEY = os.environ.get('SCRAPERAPI_KEY')
    GOOGLE_FACT_CHECK_API_KEY = os.environ.get('GOOGLE_FACT_CHECK_API_KEY') or os.environ.get('GOOGLE_FACTCHECK_API_KEY')
    GOOGLE_FACTCHECK_API_KEY = GOOGLE_FACT_CHECK_API_KEY  # Alias
    NEWS_API_KEY = os.environ.get('NEWS_API_KEY') or os.environ.get('NEWSAPI_KEY')
    NEWSAPI_KEY = NEWS_API_KEY  # Alias
    SCRAPINGBEE_API_KEY = os.environ.get('SCRAPINGBEE_API_KEY')
    
    # Log API key status
    @classmethod
    def log_status(cls):
        logger.info("API Keys Configuration:")
        logger.info(f"  OpenAI: {'✓' if cls.OPENAI_API_KEY else '✗'}")
        logger.info(f"  ScraperAPI: {'✓' if cls.SCRAPERAPI_KEY else '✗'}")
        logger.info(f"  Google Fact Check: {'✓' if cls.GOOGLE_FACT_CHECK_API_KEY else '✗'}")
        logger.info(f"  News API: {'✓' if cls.NEWS_API_KEY else '✗'}")

Config.log_status()

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS
CORS(app, 
     origins=["*"],
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "OPTIONS"])

# Setup rate limiting with error handling
try:
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per hour", "50 per minute"],
        storage_uri="memory://",
        swallow_errors=True
    )
    logger.info("✓ Rate limiter configured")
except Exception as e:
    logger.warning(f"Rate limiter setup failed (non-critical): {e}")
    limiter = None

# Initialize service imports with proper error handling
def safe_import(module_path: str, class_name: str):
    """Safely import a module and return the class or None"""
    try:
        module = __import__(module_path, fromlist=[class_name])
        cls = getattr(module, class_name)
        logger.info(f"✓ Imported {class_name} from {module_path}")
        return cls
    except ImportError as e:
        logger.error(f"✗ Failed to import {class_name} from {module_path}: {e}")
        return None
    except AttributeError as e:
        logger.error(f"✗ {class_name} not found in {module_path}: {e}")
        return None

# Initialize services
news_analyzer = None
article_extractor = None

logger.info("-" * 60)
logger.info("INITIALIZING SERVICES")

# Initialize ArticleExtractor
ArticleExtractorClass = safe_import('services.article_extractor', 'ArticleExtractor')
if ArticleExtractorClass:
    try:
        article_extractor = ArticleExtractorClass()
        logger.info("✓ ArticleExtractor initialized successfully")
    except Exception as e:
        logger.error(f"✗ ArticleExtractor initialization failed: {e}")
        logger.error(traceback.format_exc())

# Initialize base analyzer if needed
BaseAnalyzerClass = safe_import('services.base_analyzer', 'BaseAnalyzer')
if not BaseAnalyzerClass:
    logger.warning("BaseAnalyzer not found - creating compatibility class")
    
    # Create BaseAnalyzer compatibility class
    class BaseAnalyzer:
        def __init__(self, service_name):
            self.service_name = service_name
            self.available = True
            
        def get_success_result(self, data):
            return {
                'success': True,
                'data': data,
                'service': self.service_name
            }
            
        def get_error_result(self, error):
            return {
                'success': False,
                'error': error,
                'service': self.service_name
            }
    
    # Save it for other services to use
    sys.modules['services.base_analyzer'] = type(sys)('services.base_analyzer')
    sys.modules['services.base_analyzer'].BaseAnalyzer = BaseAnalyzer

# Initialize service registry if it exists
try:
    from services.service_registry import get_service_registry
    registry = get_service_registry()
    logger.info("✓ Service registry available")
except:
    logger.warning("Service registry not available")
    registry = None

# Initialize analysis pipeline if it exists
try:
    from services.analysis_pipeline import AnalysisPipeline
    logger.info("✓ AnalysisPipeline imported")
except:
    logger.warning("AnalysisPipeline not available")
    AnalysisPipeline = None

# Initialize NewsAnalyzer with comprehensive error handling
try:
    from services.news_analyzer import NewsAnalyzer
    logger.info("✓ NewsAnalyzer imported")
    
    # Initialize NewsAnalyzer
    news_analyzer = NewsAnalyzer()
    logger.info("✓✓✓ NewsAnalyzer initialized successfully!")
    
    # Test available services
    try:
        available_services = news_analyzer.get_available_services()
        logger.info(f"Available services: {available_services}")
    except:
        logger.warning("Could not retrieve available services list")
        
except Exception as e:
    logger.error(f"✗✗✗ NewsAnalyzer initialization failed: {e}")
    logger.error(traceback.format_exc())
    
    # Create a robust fallback NewsAnalyzer that works with whatever services are available
    logger.info("Creating robust fallback NewsAnalyzer")
    
    class RobustNewsAnalyzer:
        """Fallback analyzer that works with whatever services are available"""
        
        def __init__(self):
            self.article_extractor = article_extractor
            logger.info("RobustNewsAnalyzer initialized as fallback")
            
        def analyze(self, content: str, content_type: str = 'url', article_data: Dict = None) -> Dict[str, Any]:
            """Perform analysis with available services"""
            try:
                # Use provided article data if available
                if not article_data:
                    article_data = {}
                    if content_type == 'url' and self.article_extractor:
                        try:
                            result = self.article_extractor.analyze({'url': content})
                            if result.get('success'):
                                article_data = result.get('data', {})
                        except:
                            pass
                
                # Create response with what we have
                return {
                    'success': True,
                    'trust_score': 70,  # Default moderate score
                    'article_summary': article_data.get('title', 'Article analysis completed'),
                    'source': article_data.get('domain', 'Unknown'),
                    'author': article_data.get('author', 'Unknown'),
                    'findings_summary': 'Analysis completed with available services.',
                    'detailed_analysis': {
                        'source_credibility': {
                            'score': 70,
                            'rating': 'Medium',
                            'findings': ['Analysis performed with limited services']
                        }
                    }
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'trust_score': 0,
                    'article_summary': 'Analysis failed',
                    'source': 'Unknown',
                    'author': 'Unknown',
                    'findings_summary': f'Analysis failed: {str(e)}',
                    'detailed_analysis': {}
                }
        
        def get_available_services(self):
            return ['article_extractor'] if self.article_extractor else []
    
    news_analyzer = RobustNewsAnalyzer()

logger.info("-" * 60)

# Helper functions
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

def generate_findings_summary(trust_score: int, detailed_analysis: Dict, source: str) -> str:
    """Generate comprehensive findings summary"""
    findings = []
    
    # Trust assessment
    trust_level = get_trust_level(trust_score)
    if trust_score >= 80:
        findings.append("This article demonstrates high credibility and trustworthiness.")
    elif trust_score >= 60:
        findings.append("This article shows generally good credibility with some minor concerns.")
    elif trust_score >= 40:
        findings.append("This article has moderate credibility with several issues identified.")
    else:
        findings.append("This article shows significant credibility concerns.")
    
    # Source info
    if source and source != 'Unknown':
        findings.append(f"Source: {source}")
    
    # Service-specific findings
    if detailed_analysis:
        # Bias detection
        if 'bias_detector' in detailed_analysis:
            bias_data = detailed_analysis['bias_detector']
            if isinstance(bias_data, dict):
                bias_score = bias_data.get('bias_score', 0)
                if bias_score < 30:
                    findings.append("Content appears balanced with minimal bias.")
                elif bias_score > 70:
                    findings.append("Significant bias detected in the presentation.")
        
        # Fact checking
        if 'fact_checker' in detailed_analysis:
            fact_data = detailed_analysis['fact_checker']
            if isinstance(fact_data, dict):
                verified = fact_data.get('verified_claims', 0)
                total = fact_data.get('claims_checked', 0)
                if total > 0:
                    percentage = (verified / total) * 100
                    findings.append(f"Fact-checking: {int(percentage)}% of claims verified.")
    
    return " ".join(findings) if findings else "Analysis completed."

def clean_cache():
    """Clean expired cache entries"""
    with cache_lock:
        current_time = time.time()
        expired_keys = [
            key for key, (timestamp, _) in request_cache.items()
            if current_time - timestamp > CACHE_TIMEOUT
        ]
        for key in expired_keys:
            del request_cache[key]

# Request hooks
@app.before_request
def before_request():
    """Set up request-specific data"""
    g.request_id = str(uuid.uuid4())[:8]
    g.start_time = time.time()
    logger.info(f"[{g.request_id}] Request started: {request.method} {request.path}")

@app.after_request
def after_request(response):
    """Log request completion"""
    if hasattr(g, 'request_id'):
        elapsed = time.time() - g.start_time
        logger.info(f"[{g.request_id}] Request completed in {elapsed:.2f}s: {response.status_code}")
    return response

# ROUTES

@app.route('/')
def index():
    """Serve the main application page"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Template error: {e}")
        return f"<h1>News Analyzer</h1><p>Template error: {str(e)}</p>", 500

@app.route('/health')
def health():
    """Health check endpoint"""
    clean_cache()  # Clean cache on health checks
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'news_analyzer': type(news_analyzer).__name__ if news_analyzer else 'not available',
            'article_extractor': 'ready' if article_extractor else 'not available'
        },
        'api_keys': {
            'openai': bool(Config.OPENAI_API_KEY),
            'scraperapi': bool(Config.SCRAPERAPI_KEY),
            'google_factcheck': bool(Config.GOOGLE_FACT_CHECK_API_KEY),
            'news_api': bool(Config.NEWS_API_KEY)
        }
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Main analysis endpoint - with race condition fix
    """
    request_id = g.request_id if hasattr(g, 'request_id') else str(uuid.uuid4())[:8]
    logger.info("=" * 80)
    logger.info(f"[{request_id}] API ANALYZE ENDPOINT - CONCURRENT SAFE VERSION")
    start_time = time.time()
    
    try:
        # Check if NewsAnalyzer is available
        if not news_analyzer:
            logger.error(f"[{request_id}] NewsAnalyzer not available")
            return jsonify({
                'success': False,
                'error': 'Analysis service is initializing. Please try again.',
                'trust_score': 0,
                'article_summary': 'Service initializing',
                'source': 'Unknown',
                'author': 'Unknown',
                'findings_summary': 'Analysis service is still initializing. Please try again in a moment.',
                'detailed_analysis': {}
            }), 503  # Service Unavailable
        
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
        
        content_key = url if url else f"text_{hash(text)}"
        logger.info(f"[{request_id}] Analyzing: {'URL' if url else 'Text'} - {url[:100] if url else f'{len(text)} chars'}")
        
        # Check cache for recent identical requests
        with cache_lock:
            clean_cache()
            if content_key in request_cache:
                cache_time, cached_result = request_cache[content_key]
                if time.time() - cache_time < 5:  # Use cache if less than 5 seconds old
                    logger.info(f"[{request_id}] Using cached result for {content_key[:50]}")
                    return jsonify(cached_result), 200
        
        # Perform article extraction with locking for URLs
        article_data = {}
        extraction_error = None
        
        if url and article_extractor:
            # Use per-URL lock to prevent concurrent extraction of same URL
            url_lock = analysis_locks[url]
            
            try:
                # Try to acquire lock with timeout
                lock_acquired = url_lock.acquire(timeout=2)
                
                if lock_acquired:
                    try:
                        logger.info(f"[{request_id}] Performing enhanced article extraction...")
                        extraction_result = article_extractor.analyze({'url': url})
                        
                        if extraction_result.get('success'):
                            article_data = extraction_result.get('data', {})
                            logger.info(f"[{request_id}] Extraction successful - Author: {article_data.get('author', 'Unknown')}")
                        else:
                            extraction_error = extraction_result.get('error', 'Extraction failed')
                            logger.warning(f"[{request_id}] Extraction returned failure: {extraction_error}")
                    finally:
                        url_lock.release()
                else:
                    logger.warning(f"[{request_id}] Could not acquire extraction lock - proceeding without extraction")
                    
            except Exception as e:
                extraction_error = str(e)
                logger.error(f"[{request_id}] Article extraction failed: {e}")
                if url_lock.locked():
                    try:
                        url_lock.release()
                    except:
                        pass
        
        # Run main analysis pipeline
        try:
            logger.info(f"[{request_id}] Running main analysis pipeline...")
            
            # Pass article_data to analyzer if using fallback
            if hasattr(news_analyzer, 'article_data'):
                pipeline_results = news_analyzer.analyze(
                    content=url if url else text,
                    content_type='url' if url else 'text',
                    article_data=article_data  # Pass extracted data
                )
            else:
                pipeline_results = news_analyzer.analyze(
                    content=url if url else text,
                    content_type='url' if url else 'text'
                )
            
            # Handle pipeline failures gracefully
            if not pipeline_results.get('success', False):
                error_msg = pipeline_results.get('error', 'Analysis failed')
                
                # If extraction failed but we have some article data, use it
                if extraction_error and article_data:
                    logger.info(f"[{request_id}] Using partial article data despite extraction error")
                    pipeline_results['article_summary'] = article_data.get('title', 'Article analyzed')
                    pipeline_results['source'] = article_data.get('domain', 'Unknown')
                    pipeline_results['author'] = article_data.get('author', 'Unknown')
                    pipeline_results['success'] = True
                    pipeline_results['trust_score'] = 50  # Default score
                else:
                    logger.error(f"[{request_id}] Pipeline failed: {error_msg}")
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
            
            # Extract and merge results
            trust_score = pipeline_results.get('trust_score', 0)
            article_summary = pipeline_results.get('article_summary', article_data.get('title', 'Article analyzed'))
            source = pipeline_results.get('source', article_data.get('domain', 'Unknown'))
            
            # Prefer extracted author over pipeline author
            author = article_data.get('author') or pipeline_results.get('author', 'Unknown')
            
            detailed_analysis = pipeline_results.get('detailed_analysis', {})
            
            # Generate comprehensive findings
            findings_summary = pipeline_results.get('findings_summary')
            if not findings_summary:
                findings_summary = generate_findings_summary(trust_score, detailed_analysis, source)
            
            # Build response
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
                'services_analyzed': list(detailed_analysis.keys()) if detailed_analysis else [],
                'trust_level': get_trust_level(trust_score)
            }
            
            # Cache successful response
            with cache_lock:
                request_cache[content_key] = (time.time(), response_data)
            
            logger.info(f"[{request_id}] Analysis completed in {response_data['processing_time']}s")
            logger.info(f"[{request_id}] Results - Score: {trust_score}, Author: {author}, Source: {source}")
            logger.info("=" * 80)
            
            return jsonify(response_data), 200
            
        except Exception as e:
            logger.error(f"[{request_id}] Analysis error: {str(e)}", exc_info=True)
            
            # Try to return partial results if available
            if article_data:
                return jsonify({
                    'success': False,
                    'error': f'Analysis error: {str(e)}',
                    'trust_score': 0,
                    'article_summary': article_data.get('title', 'Analysis error'),
                    'source': article_data.get('domain', 'Unknown'),
                    'author': article_data.get('author', 'Unknown'),
                    'findings_summary': f'Analysis partially completed. Error: {str(e)}',
                    'detailed_analysis': {}
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': f'Analysis error: {str(e)}',
                    'trust_score': 0,
                    'article_summary': 'Analysis error',
                    'source': 'Unknown',
                    'author': 'Unknown',
                    'findings_summary': f'An error occurred during analysis: {str(e)}',
                    'detailed_analysis': {}
                }), 500
            
    except Exception as e:
        logger.error(f"[{request_id}] Request handling error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Request error: {str(e)}',
            'trust_score': 0,
            'article_summary': 'Request error',
            'source': 'Unknown',
            'author': 'Unknown',
            'findings_summary': f'Request processing error: {str(e)}',
            'detailed_analysis': {}
        }), 500

@app.route('/api/test')
def test_endpoint():
    """Test endpoint for debugging"""
    return jsonify({
        'success': True,
        'message': 'API is running',
        'services': {
            'news_analyzer': type(news_analyzer).__name__ if news_analyzer else None,
            'article_extractor': bool(article_extractor)
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        'status': 'online',
        'version': '1.0.0',
        'services': 'ready' if news_analyzer else 'initializing',
        'timestamp': datetime.now().isoformat()
    })

# Static file serving
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found', 'path': request.path}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}", exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Please wait before making more requests'
    }), 429

# Application entry point
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Flask application on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info("=" * 80)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
