"""
TruthLens News Analyzer - Complete with Debate Arena & Live Streaming
Version: 10.2.0
Date: October 25, 2025

CHANGES FROM 10.1.0:
1. ADDED: /api/youtube/process endpoint for YouTube transcript extraction
2. ADDED: Import for services.youtube_scraper module
3. FIXED: Frontend now properly connects to backend YouTube processing
4. REASON: Frontend was calling /api/youtube/process but endpoint didn't exist (404 errors)
5. PRESERVED: All v10.1.0 functionality (DO NO HARM ✓)

CHANGES FROM 10.0.1:
1. ADDED: /transcript route to render transcript.html (standalone transcript page)
2. ENHANCEMENT: Users can now access transcript functionality via tab OR standalone page
3. PRESERVED: All v10.0.1 functionality (DO NO HARM ✓)

CHANGES FROM 10.0.0:
1. FIXED: Enhanced error handling for live stream route registration
2. FIXED: Better logging to debug 404 errors for /api/transcript/live/* routes
3. ADDED: Route listing in logs to verify which endpoints are registered
4. All v10.0.0 functionality preserved (DO NO HARM ✓)

EXISTING FEATURES (v10.0.0):
- YouTube Live stream analysis
- Real-time audio transcription (AssemblyAI)
- Automatic claim extraction from live streams
- Live fact-checking as speech happens
- Server-Sent Events for frontend updates
- Cost: $0/month with free tier (100 hours)

REQUIREMENTS:
- services/live_stream_analyzer.py (Live streaming engine)
- services/youtube_scraper.py (YouTube transcript extraction)
- transcript_routes.py (Transcript & live stream routes)
- ASSEMBLYAI_API_KEY environment variable (for live streaming)
- SCRAPINGBEE_API_KEY environment variable (for YouTube transcripts)
- yt-dlp and ffmpeg system dependencies

PREVIOUS FEATURES PRESERVED:
- News Analysis (7 AI Services) - v8.x
- Debate Arena (Phase 1 text-based) - v9.0.0
- All v8.x enhancements

This file is complete and ready to deploy.
Last modified: October 25, 2025 - Added /api/youtube/process endpoint v10.2.0
"""

import os
import re
import json
import time
import logging
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# CRITICAL IMPORTS FOR DATA TRANSFORMATION FIX
from services.news_analyzer import NewsAnalyzer
from services.data_transformer import DataTransformer

# YOUTUBE TRANSCRIPT EXTRACTION (v10.2.0)
from services.youtube_scraper import extract_youtube_transcript

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# FLASK APP INITIALIZATION
# ============================================================================
app = Flask(__name__, 
            static_folder='static',
            static_url_path='/static',
            template_folder='templates')
CORS(app)

# Set secret key for session management
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

logger.info("=" * 80)
logger.info("Flask app initialized with EXPLICIT static configuration:")
logger.info(f"  static_folder: {app.static_folder}")
logger.info(f"  static_url_path: {app.static_url_path}")
logger.info(f"  template_folder: {app.template_folder}")
logger.info("=" * 80)

# ============================================================================
# NEW: DATABASE CONFIGURATION FOR DEBATE ARENA (v9.0.0)
# ============================================================================

database_url = os.getenv('DATABASE_URL')

if database_url:
    # Render uses 'postgres://' but SQLAlchemy needs 'postgresql://'
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'connect_timeout': 10
        }
    }
    
    logger.info("=" * 80)
    logger.info("DATABASE CONFIGURATION:")
    logger.info("  ✓ PostgreSQL configured for Debate Arena")
    logger.info("  ✓ Connection pooling enabled")
    logger.info("  ✓ Auto-reconnect on failure")
    logger.info("=" * 80)
    
    # Initialize SQLAlchemy
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy(app)
    
    # Import debate models
    from debate_models import User, Debate, Argument, Vote
    
    # Initialize database
    with app.app_context():
        try:
            db.create_all()
            logger.info("  ✓ Database tables created/verified")
        except Exception as e:
            logger.error(f"  ✗ Database initialization error: {e}")
else:
    db = None
    logger.info("=" * 80)
    logger.info("DATABASE: Not configured (Debate Arena disabled)")
    logger.info("=" * 80)

# ============================================================================
# INITIALIZE SERVICES
# ============================================================================

news_analyzer_service = NewsAnalyzer()
data_transformer = DataTransformer()

logger.info("=" * 80)
logger.info("NEWS ANALYZER SERVICE INITIALIZATION:")
logger.info(f"  ✓ NewsAnalyzer initialized")
logger.info(f"  ✓ DataTransformer initialized")
logger.info(f"  ✓ Ready to process news articles")
logger.info("=" * 80)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def extract_article_text(url: str) -> Tuple[Optional[str], Optional[Dict]]:
    """Extract article text and metadata from URL using Beautiful Soup."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Extract metadata
        metadata = {
            'title': soup.find('title').text.strip() if soup.find('title') else None,
            'description': None,
            'author': None,
            'published_date': None
        }
        
        # Try to get description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            metadata['description'] = meta_desc['content']
        
        # Try to get author
        meta_author = soup.find('meta', attrs={'name': 'author'})
        if meta_author and meta_author.get('content'):
            metadata['author'] = meta_author['content']
        
        # Extract article text
        article_text = None
        
        # Try common article containers
        article = soup.find('article')
        if article:
            article_text = article.get_text(separator='\n', strip=True)
        else:
            # Try common content divs
            content_divs = soup.find_all('div', class_=re.compile(r'(article|content|post|story)', re.I))
            if content_divs:
                article_text = '\n'.join(div.get_text(separator='\n', strip=True) for div in content_divs)
            else:
                # Fall back to body
                body = soup.find('body')
                if body:
                    article_text = body.get_text(separator='\n', strip=True)
        
        if article_text:
            # Clean up the text
            lines = [line.strip() for line in article_text.split('\n') if line.strip()]
            article_text = '\n'.join(lines)
        
        return article_text, metadata
        
    except Exception as e:
        logger.error(f"Error extracting article text: {e}")
        return None, None

def is_valid_url(url: str) -> bool:
    """Check if a string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

# ============================================================================
# DEBATE ARENA ROUTES (v9.0.0)
# ============================================================================

if database_url:
    try:
        from debate_routes import debate_bp
        app.register_blueprint(debate_bp)
        logger.info("=" * 80)
        logger.info("DEBATE ARENA ROUTES:")
        logger.info("  ✓ Blueprint registered at /api/debate")
        logger.info("  ✓ Challenge mode available")
        logger.info("  ✓ Pick-a-fight mode available")
        logger.info("=" * 80)
    except Exception as e:
        logger.error(f"✗ Failed to import debate_routes.py: {e}")
        logger.error("✗ Make sure debate_routes.py exists in the same directory as app.py")

# ============================================================================
# TRANSCRIPT & LIVE STREAM ROUTES (v10.0.0)
# ============================================================================

try:
    from transcript_routes import transcript_bp
    app.register_blueprint(transcript_bp)
    logger.info("=" * 80)
    logger.info("TRANSCRIPT ROUTES:")
    
    # List all transcript routes
    transcript_routes = [rule.rule for rule in app.url_map.iter_rules() if '/api/transcript/' in rule.rule]
    logger.info(f"✓ Registered transcript routes: {', '.join(transcript_routes)}")
    
    # Check specifically for live stream routes
    if transcript_routes:
        live_routes = [r for r in transcript_routes if 'live' in r]
        if live_routes:
            logger.info(f"✓ Live stream routes found: {', '.join(live_routes)}")
        else:
            logger.warning("⚠️  Live stream routes not found in transcript_bp - check transcript_routes.py")
    
    logger.info("=" * 80)
    
except Exception as e:
    logger.error(f"✗ Failed to import transcript_routes.py: {e}")
    logger.error("✗ Make sure transcript_routes.py exists in the same directory as app.py")
    logger.error("=" * 80)

# ============================================================================
# STATIC PAGE ROUTES
# ============================================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/debate-arena')
def debate_arena():
    return render_template('debate-arena.html')

@app.route('/live-stream')
def live_stream():
    return render_template('live-stream.html')

@app.route('/transcript')
def transcript_page():
    """
    Standalone transcript analysis page with YouTube URL support
    
    NEW IN v10.1.0 - This route renders the standalone transcript.html page
    Users can analyze transcripts via this page OR via the tab on index.html
    - Full YouTube URL support via ScrapingBee API
    - Text transcript paste support
    - Audio file upload support (future)
    - Real-time fact-checking
    """
    return render_template('transcript.html')

# ============================================================================
# HEALTH CHECK & DEBUG ROUTES
# ============================================================================

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'version': '10.2.0',
        'timestamp': datetime.utcnow().isoformat(),
        'features': {
            'news_analysis': 'v8.5.1 - 7 AI services with bias awareness',
            'debate_arena': 'v9.0.0 - Challenge & Pick-a-Fight modes' if database_url else 'disabled',
            'live_streaming': 'v10.0.0 - YouTube Live analysis with AssemblyAI',
            'youtube_transcripts': 'v10.2.0 - YouTube URL transcript extraction'
        }
    })

@app.route('/debug/static-files')
def debug_static_files():
    """Debug route to check static file configuration."""
    static_path = os.path.join(app.root_path, 'static')
    
    debug_info = {
        'app_root_path': app.root_path,
        'static_folder': app.static_folder,
        'static_url_path': app.static_url_path,
        'static_path_exists': os.path.exists(static_path),
        'static_contents': []
    }
    
    if os.path.exists(static_path):
        for root, dirs, files in os.walk(static_path):
            rel_root = os.path.relpath(root, static_path)
            for file in files:
                rel_path = os.path.join(rel_root, file) if rel_root != '.' else file
                debug_info['static_contents'].append(rel_path)
    
    return jsonify(debug_info)

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Explicitly serve static files."""
    return send_from_directory(app.static_folder, filename)

# ============================================================================
# NEWS ANALYSIS API
# ============================================================================

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        url = data.get('url')
        text = data.get('text')
        
        logger.info("=" * 80)
        logger.info("API /analyze endpoint called - Version 10.2.0")
        logger.info(f"URL provided: {bool(url)}")
        logger.info(f"Text provided: {bool(text)} ({len(text) if text else 0} chars)")
        
        if url:
            content = url
            content_type = 'url'
            logger.info(f"Analyzing URL: {url}")
        elif text:
            content = text
            content_type = 'text'
            logger.info(f"Analyzing text content: {len(text)} characters")
        else:
            logger.error("No URL or text provided")
            return jsonify({'success': False, 'error': 'No URL or text provided'}), 400
        
        logger.info("Step 1: Running NewsAnalyzer...")
        raw_results = news_analyzer_service.analyze(
            content=content,
            content_type=content_type,
            pro_mode=data.get('pro_mode', False)
        )
        
        logger.info("Step 2: Transforming data to match frontend contract...")
        transformed_results = data_transformer.transform_response(raw_results)
        
        logger.info(f"Sending to frontend:")
        logger.info(f"  - Success: {transformed_results.get('success')}")
        logger.info(f"  - Trust Score: {transformed_results.get('trust_score')}")
        logger.info(f"  - Source: {transformed_results.get('source')}")
        logger.info(f"  - Author: {transformed_results.get('author')}")
        logger.info("=" * 80)
        
        return jsonify(transformed_results)
        
    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# YOUTUBE TRANSCRIPT API (NEW IN v10.2.0)
# ============================================================================

@app.route('/api/youtube/process', methods=['POST'])
def process_youtube():
    """
    Process YouTube URL and extract transcript
    
    NEW IN v10.2.0 - This endpoint was missing, causing 404 errors
    
    Frontend sends: {'url': 'https://www.youtube.com/watch?v=...'}
    
    Returns:
        Success:
            {
                'success': True,
                'transcript': 'Full transcript text...',
                'metadata': {
                    'video_id': 'abc123',
                    'title': 'Video Title',
                    'channel': 'Channel Name',
                    'duration': 300,
                    'views': 1000000,
                    'upload_date': '2025-01-15'
                }
            }
        
        Error:
            {
                'success': False,
                'error': 'Error message',
                'suggestion': 'Helpful suggestion'
            }
    """
    try:
        data = request.json
        url = data.get('url')
        
        logger.info("=" * 80)
        logger.info("API /api/youtube/process endpoint called - Version 10.2.0")
        logger.info(f"YouTube URL: {url}")
        
        if not url:
            logger.error("No YouTube URL provided")
            return jsonify({
                'success': False,
                'error': 'No YouTube URL provided',
                'suggestion': 'Please provide a valid YouTube URL'
            }), 400
        
        # Validate URL format
        if 'youtube.com' not in url and 'youtu.be' not in url:
            logger.error("Invalid YouTube URL format")
            return jsonify({
                'success': False,
                'error': 'Invalid YouTube URL',
                'suggestion': 'URL must be from youtube.com or youtu.be'
            }), 400
        
        logger.info("Step 1: Extracting YouTube transcript...")
        result = extract_youtube_transcript(url)
        
        if result.get('success'):
            transcript_length = len(result.get('transcript', ''))
            logger.info(f"Step 2: Success! Extracted {transcript_length} characters")
            logger.info(f"  - Video Title: {result.get('metadata', {}).get('title', 'Unknown')}")
            logger.info(f"  - Channel: {result.get('metadata', {}).get('channel', 'Unknown')}")
            logger.info(f"  - Duration: {result.get('metadata', {}).get('duration_formatted', 'Unknown')}")
        else:
            error_msg = result.get('error', 'Unknown error')
            logger.error(f"Step 2: Failed - {error_msg}")
        
        logger.info("=" * 80)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"YouTube processing error: {e}", exc_info=True)
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}',
            'suggestion': 'Please try again later or contact support'
        }), 500

# ============================================================================
# DEBUG API KEYS ROUTE
# ============================================================================

@app.route('/debug/api-keys', methods=['GET'])
def debug_api_keys():
    return jsonify({
        'anthropic': bool(os.getenv('ANTHROPIC_API_KEY')),
        'openai': bool(os.getenv('OPENAI_API_KEY')),
        'google_fact_check': bool(os.getenv('GOOGLE_FACT_CHECK_API_KEY')),
        'assemblyai': bool(os.getenv('ASSEMBLYAI_API_KEY')),
        'scrapingbee': bool(os.getenv('SCRAPINGBEE_API_KEY')),
        'database': bool(database_url)
    })

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    logger.info("=" * 80)
    logger.info("TRUTHLENS NEWS ANALYZER - STARTING v10.2.0")
    logger.info("=" * 80)
    logger.info("")
    logger.info("AVAILABLE FEATURES:")
    logger.info("  ✓ News Analysis - 7 AI services with comprehensive fact-checking")
    logger.info("    - Source credibility analysis")
    logger.info("    - Bias detection (enhanced with outlet awareness)")
    logger.info("    - Fact-checking with multiple sources")
    logger.info("    - Author analysis (supports unknown authors)")
    logger.info("    - Transparency evaluation")
    logger.info("    - Content quality assessment")
    logger.info("    - Manipulation detection")
    logger.info("")
    
    if os.getenv('ASSEMBLYAI_API_KEY'):
        logger.info("  ✓ Live Stream Analysis - YouTube Live with real-time transcription")
        logger.info("    - Real-time audio transcription (AssemblyAI)")
        logger.info("    - Automatic claim extraction")
        logger.info("    - Live fact-checking")
        logger.info("    - Server-Sent Events for updates")
    else:
        logger.info("  ✗ Live Streaming - Disabled (set ASSEMBLYAI_API_KEY to enable)")
    
    if os.getenv('SCRAPINGBEE_API_KEY'):
        logger.info("  ✓ YouTube Transcript Extraction - Video transcript analysis")
        logger.info("    - Extract transcripts from any YouTube video")
        logger.info("    - Automatic caption retrieval")
        logger.info("    - Comprehensive fact-checking")
    else:
        logger.info("  ✗ YouTube Transcripts - Disabled (set SCRAPINGBEE_API_KEY to enable)")
    
    if database_url:
        logger.info("  ✓ Debate Arena - Challenge Mode & Pick-a-Fight")
        logger.info("    - Text-based arguments")
        logger.info("    - Real-time voting")
        logger.info("    - User authentication")
    else:
        logger.info("  ✗ Debate Arena - Disabled (set DATABASE_URL to enable)")
    
    logger.info("")
    logger.info("VERSION HISTORY:")
    logger.info("FROM v8.5.1:")
    logger.info("  ✓ Author profile URL extraction")
    logger.info("FROM v8.5.0:")
    logger.info("  ✓ /features, /pricing, /about, /contact pages")
    logger.info("FROM v8.4.0:")
    logger.info("  ✓ Enhanced bias detection with outlet awareness")
    logger.info("FROM v8.3.0:")
    logger.info("  ✓ Unknown author support with outlet-based credibility")
    logger.info("FROM v9.0.0:")
    logger.info("  ✓ Debate Arena backend (Phase 1)")
    logger.info("  ✓ PostgreSQL database integration")
    logger.info("")
    logger.info("NEW IN v10.0.0:")
    logger.info("  ✓ Live Stream transcript analysis")
    logger.info("  ✓ YouTube Live support with yt-dlp")
    logger.info("  ✓ Real-time transcription with AssemblyAI")
    logger.info("  ✓ Live fact-checking as speech happens")
    logger.info("  ✓ Server-Sent Events for frontend updates")
    logger.info("  ✓ Cost: $0/month with AssemblyAI free tier (100 hours)")
    logger.info("")
    logger.info("NEW IN v10.2.0:")
    logger.info("  ✓ YouTube transcript extraction endpoint")
    logger.info("  ✓ /api/youtube/process for video transcript analysis")
    logger.info("  ✓ Full integration with ScrapingBee service")
    logger.info("  ✓ Fixed 404 errors on YouTube processing")
    logger.info("=" * 80)
    
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# I did no harm and this file is not truncated
