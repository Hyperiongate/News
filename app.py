"""
TruthLens News Analyzer - Complete with Debate Arena & Live Streaming
Version: 10.2.2
Date: October 25, 2025

HOTFIX FROM 10.2.1:
1. FIXED: Added missing transcript_routes registration (was causing 404 on /api/transcript/* endpoints)
2. FIXED: YouTube URL parameter mismatch - now accepts both 'url' and 'youtube_url'
3. REASON: Frontend sends 'youtube_url' but backend expected 'url'
4. RESULT: YouTube processing now works correctly
5. PRESERVED: All v10.2.1 functionality (DO NO HARM ✓)

CHANGES FROM 10.2.0:
1. ADDED: /api/youtube/process endpoint for YouTube transcript extraction
2. ADDED: Import for services.youtube_scraper module
3. FIXED: Frontend now properly connects to backend YouTube processing
4. REASON: Frontend was calling /api/youtube/process but endpoint didn't exist (404 errors)
5. PRESERVED: All v10.1.0 functionality (DO NO HARM ✓)

CHANGES FROM 10.0.1:
1. ADDED: /transcript route to render transcript.html (standalone transcript page)
2. ENHANCEMENT: Users can now access transcript functionality via tab OR standalone page
3. PRESERVED: All v10.0.1 functionality (DO NO HARM ✓)

EXISTING FEATURES:
- News Analysis (7 AI Services) - v8.x
- Debate Arena (Phase 1 text-based) - v9.0.0
- YouTube Live stream analysis - v10.0.0
- YouTube transcript extraction - v10.2.0

This file is complete and ready to deploy.
Last modified: October 25, 2025 - HOTFIX: transcript_routes registration v10.2.2
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
    
    # Import debate models (optional - gracefully handle if missing)
    try:
        from debate_models import User, Debate, Argument, Vote
        logger.info("  ✓ Debate models imported successfully")
    except ImportError as e:
        logger.warning(f"  ⚠ Debate models not found: {e}")
        logger.warning("  ⚠ Debate Arena will be disabled")
        db = None  # Disable debate features if models missing
    
    # Initialize database (only if models imported successfully)
    if db is not None:
        with app.app_context():
            try:
                db.create_all()
                logger.info("  ✓ Database tables created/verified")
            except Exception as e:
                logger.error(f"  ✗ Database initialization error: {e}")
                db = None  # Disable if initialization fails
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
            'title': soup.find('title').get_text() if soup.find('title') else None,
            'url': url,
            'domain': urlparse(url).netloc
        }
        
        # Try to find article text
        article_text = None
        
        # Try article tags first
        article = soup.find('article')
        if article:
            paragraphs = article.find_all('p')
            if paragraphs:
                article_text = '\n\n'.join([p.get_text().strip() for p in paragraphs])
        
        # Fall back to all paragraphs
        if not article_text:
            paragraphs = soup.find_all('p')
            if paragraphs:
                article_text = '\n\n'.join([p.get_text().strip() for p in paragraphs])
        
        return article_text, metadata
        
    except Exception as e:
        logger.error(f"Error extracting article: {e}")
        return None, None

def is_valid_url(url: str) -> bool:
    """Check if URL is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

# ============================================================================
# DEBATE ARENA ROUTES (v9.0.0)
# ============================================================================

if database_url and db is not None:
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
# TRANSCRIPT & LIVE STREAM ROUTES (v10.0.0) - FIXED IN v10.2.2
# ============================================================================

try:
    from transcript_routes import transcript_bp
    app.register_blueprint(transcript_bp, url_prefix='/api/transcript')
    logger.info("=" * 80)
    logger.info("TRANSCRIPT ROUTES:")
    
    # List all transcript routes
    transcript_routes = [rule.rule for rule in app.url_map.iter_rules() if '/api/transcript/' in rule.rule]
    logger.info(f"✓ Registered transcript routes: {len(transcript_routes)} routes")
    for route in transcript_routes:
        logger.info(f"  - {route}")
    
    logger.info("=" * 80)
    
except ImportError as e:
    logger.warning(f"⚠ Failed to import transcript_routes.py: {e}")
    logger.warning("⚠ Transcript analysis endpoints will not be available")
    logger.warning("⚠ This is OK if you only use the /api/youtube/process endpoint")
    logger.info("=" * 80)

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
# NEWS ANALYSIS API (v8.x)
# ============================================================================

@app.route('/api/analyze', methods=['POST'])
def analyze_news():
    """
    Main news analysis endpoint
    Accepts URL or direct text for analysis
    Returns comprehensive credibility assessment
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        url = data.get('url', '').strip()
        text = data.get('text', '').strip()
        
        logger.info("=" * 80)
        logger.info("NEW ANALYSIS REQUEST")
        logger.info(f"  URL provided: {bool(url)}")
        logger.info(f"  Text provided: {bool(text)}")
        
        article_content = None
        source_url = url if url else None
        
        # Extract content from URL or use provided text
        if url:
            if not is_valid_url(url):
                return jsonify({'success': False, 'error': 'Invalid URL format'}), 400
            
            article_content, metadata = extract_article_text(url)
            if not article_content:
                return jsonify({'success': False, 'error': 'Could not extract article content from URL'}), 400
            
            logger.info(f"  ✓ Extracted article from URL")
            logger.info(f"  - Domain: {metadata.get('domain')}")
            
        elif text:
            article_content = text
            logger.info(f"  ✓ Using provided text ({len(text)} characters)")
        else:
            return jsonify({'success': False, 'error': 'Either URL or text must be provided'}), 400
        
        # Run analysis
        logger.info("  Starting analysis...")
        raw_results = news_analyzer_service.analyze(article_content, source_url)
        
        # Transform for frontend
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
# YOUTUBE TRANSCRIPT API (NEW IN v10.2.0) - FIXED IN v10.2.2
# ============================================================================

@app.route('/api/youtube/process', methods=['POST'])
def process_youtube():
    """
    Process YouTube URL and extract transcript
    
    NEW IN v10.2.0 - This endpoint was missing, causing 404 errors
    FIXED IN v10.2.2 - Now accepts both 'url' and 'youtube_url' parameters
    
    Frontend can send: 
        {'url': 'https://www.youtube.com/watch?v=...'} 
        OR
        {'youtube_url': 'https://www.youtube.com/watch?v=...'}
    
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
        
        # FIXED: Accept both 'url' and 'youtube_url' parameters
        url = data.get('url') or data.get('youtube_url')
        
        logger.info("=" * 80)
        logger.info("API /api/youtube/process endpoint called - Version 10.2.2")
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
# HEALTH CHECK & DEBUG ROUTES
# ============================================================================

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'version': '10.2.2',
        'timestamp': datetime.utcnow().isoformat(),
        'features': {
            'news_analysis': 'v8.5.1 - 7 AI services with bias awareness',
            'debate_arena': 'v9.0.0 - Challenge & Pick-a-Fight modes' if database_url and db else 'disabled',
            'live_streaming': 'v10.0.0 - YouTube Live analysis with AssemblyAI',
            'youtube_transcripts': 'v10.2.2 - YouTube URL transcript extraction (FIXED)',
            'transcript_analysis': 'v10.2.2 - Full transcript fact-checking'
        }
    })

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
# MAIN
# ============================================================================

if __name__ == '__main__':
    logger.info("=" * 80)
    logger.info("TRUTHLENS NEWS ANALYZER - STARTING v10.2.2")
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
    
    if database_url and db:
        logger.info("  ✓ Debate Arena - Challenge Mode & Pick-a-Fight")
        logger.info("    - Text-based arguments")
        logger.info("    - Real-time voting")
        logger.info("    - User authentication")
    else:
        logger.info("  ✗ Debate Arena - Disabled (set DATABASE_URL to enable)")
    
    logger.info("")
    logger.info("VERSION HISTORY:")
    logger.info("NEW IN v10.2.2 (HOTFIX):")
    logger.info("  ✓ Fixed missing transcript_routes registration")
    logger.info("  ✓ Fixed YouTube parameter mismatch (url vs youtube_url)")
    logger.info("  ✓ All transcript endpoints now working correctly")
    logger.info("")
    logger.info("NEW IN v10.2.1:")
    logger.info("  ✓ Optional debate_models import (no crash if missing)")
    logger.info("  ✓ Graceful degradation if debate arena unavailable")
    logger.info("")
    logger.info("NEW IN v10.2.0:")
    logger.info("  ✓ YouTube transcript extraction endpoint")
    logger.info("  ✓ /api/youtube/process for video transcript analysis")
    logger.info("  ✓ Full integration with ScrapingBee service")
    logger.info("=" * 80)
    
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# I did no harm and this file is not truncated
