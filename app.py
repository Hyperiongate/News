"""
TruthLens News Analyzer - Complete with Debate Arena & Live Streaming
Version: 10.2.4 - NAVIGATION FIX
Date: October 26, 2025

CRITICAL FIX FROM 10.2.3:
========================
ROOT CAUSE: Missing static page routes for navigation menu items
  - Navigation header showed: Features, About, Live Stream, Debate Arena, Contact
  - But app.py only had routes for: News Analysis (/) and Transcript
  - Users got 404 errors clicking on Features, About, Contact, Live Stream, Debate Arena

THE FIX:
========
1. ADDED: 5 missing static page routes:
   - /features → features.html
   - /about → about.html
   - /contact → contact.html
   - /live-stream → live-stream.html
   - /debate-arena → debate-arena.html

2. PRESERVED: All v10.2.3 functionality (DO NO HARM ✓)
   - YouTube job integration still works
   - News analysis still works
   - Transcript analysis still works
   - API routes unchanged

DEPLOYMENT:
===========
Replace existing app.py completely with this file.
All navigation menu items will now work properly.

This file is complete and ready to deploy to GitHub/Render.
Last modified: October 26, 2025 - v10.2.4 NAVIGATION FIX
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

# ============================================================================
# TRANSCRIPT & LIVE STREAM ROUTES (v10.0.0) - FIXED IN v10.2.2
# ============================================================================

# NEW IN v10.2.3: Import job management from transcript_routes
# This allows /api/youtube/process to create jobs properly
transcript_job_api = None

try:
    from transcript_routes import transcript_bp
    # Also import the job management functions we need
    from transcript_routes import create_job_via_api
    transcript_job_api = create_job_via_api
    
    app.register_blueprint(transcript_bp, url_prefix='/api/transcript')
    logger.info("=" * 80)
    logger.info("TRANSCRIPT ROUTES:")
    
    # List all transcript routes
    transcript_routes = [rule.rule for rule in app.url_map.iter_rules() if '/api/transcript/' in rule.rule]
    logger.info(f"✓ Registered transcript routes: {len(transcript_routes)} routes")
    for route in transcript_routes:
        logger.info(f"  - {route}")
    
    logger.info("  ✓ Job management API imported for YouTube integration")
    logger.info("=" * 80)
    
except ImportError as e:
    logger.warning(f"⚠ Failed to import transcript_routes.py: {e}")
    logger.warning("⚠ Transcript analysis endpoints will not be available")
    logger.warning("⚠ YouTube processing will also be disabled")
    logger.info("=" * 80)

# ============================================================================
# STATIC PAGE ROUTES (v10.2.4) - NAVIGATION FIX
# ============================================================================

@app.route('/')
def index():
    """News Analysis page (main page)"""
    return render_template('index.html')

@app.route('/transcript')
def transcript_page():
    """Standalone transcript analysis page"""
    return render_template('transcript.html')

# NEW IN v10.2.4: Added missing static page routes for navigation menu
@app.route('/features')
def features_page():
    """Features page"""
    return render_template('features.html')

@app.route('/about')
def about_page():
    """About page"""
    return render_template('about.html')

@app.route('/contact')
def contact_page():
    """Contact page"""
    return render_template('contact.html')

@app.route('/live-stream')
def live_stream_page():
    """Live Stream Analysis page"""
    return render_template('live-stream.html')

@app.route('/debate-arena')
def debate_arena_page():
    """Debate Arena page"""
    return render_template('debate-arena.html')

# ============================================================================
# DEBATE ARENA ROUTES (v9.0.0) - Optional
# ============================================================================

# Only register debate routes if database is available
if database_url and db:
    try:
        from debate_routes import debate_bp
        app.register_blueprint(debate_bp, url_prefix='/api/debate')
        logger.info("=" * 80)
        logger.info("DEBATE ARENA ROUTES:")
        logger.info("  ✓ Debate routes registered at /api/debate/*")
        logger.info("=" * 80)
    except ImportError as e:
        logger.warning(f"⚠ Failed to import debate_routes: {e}")
        logger.warning("⚠ Debate Arena will not be available")
        logger.info("=" * 80)

# ============================================================================
# NEWS ANALYSIS API ROUTES (v8.5.1)
# ============================================================================

@app.route('/api/analyze', methods=['POST'])
def analyze_article():
    """
    Main news analysis endpoint (v8.5.1)
    Analyzes news articles using 7 AI services
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'success': False, 'error': 'No URL provided'}), 400
        
        logger.info("=" * 80)
        logger.info(f"NEWS ANALYSIS REQUEST:")
        logger.info(f"  URL: {url}")
        logger.info(f"  Timestamp: {datetime.now().isoformat()}")
        logger.info("=" * 80)
        
        # Extract article content
        logger.info("Step 1: Extracting article content...")
        article_text, metadata = extract_article_text(url)
        
        if not article_text:
            return jsonify({
                'success': False,
                'error': 'Could not extract article content from URL'
            }), 400
        
        logger.info(f"  ✓ Extracted {len(article_text)} characters")
        
        # Analyze with NewsAnalyzer
        logger.info("Step 2: Running comprehensive analysis...")
        raw_results = news_analyzer_service.analyze(url, article_text, metadata)
        
        if not raw_results.get('success'):
            return jsonify({
                'success': False,
                'error': raw_results.get('error', 'Analysis failed')
            }), 500
        
        logger.info("  ✓ Analysis complete")
        
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
# YOUTUBE TRANSCRIPT API (FIXED IN v10.2.3)
# ============================================================================

@app.route('/api/youtube/process', methods=['POST'])
def process_youtube():
    """
    Process YouTube URL and extract transcript with JOB CREATION
    
    FIXED IN v10.2.3: Now properly integrates with job system!
    
    Flow:
      1. Extract YouTube transcript using ScrapingBee
      2. Create a job in the job management system
      3. Start background processing (claim extraction + fact-checking)
      4. Return job_id to frontend
      5. Frontend polls /api/transcript/status/{job_id}
    
    Frontend sends: 
        {'url': 'https://www.youtube.com/watch?v=...'} 
        OR
        {'youtube_url': 'https://www.youtube.com/watch?v=...'}
    
    Returns:
        Success:
            {
                'success': True,
                'job_id': 'abc123...',
                'message': 'Analysis started',
                'video_title': 'Video Title',
                'status_url': '/api/transcript/status/abc123...'
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
        
        # Accept both 'url' and 'youtube_url' parameters
        url = data.get('url') or data.get('youtube_url')
        
        logger.info("=" * 80)
        logger.info("API /api/youtube/process endpoint called - Version 10.2.3")
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
        
        # Check if transcript_routes is available
        if transcript_job_api is None:
            logger.error("Transcript routes not available - cannot create job")
            return jsonify({
                'success': False,
                'error': 'Transcript processing system not available',
                'suggestion': 'Please ensure transcript_routes.py is installed'
            }), 503
        
        # Step 1: Extract YouTube transcript
        logger.info("Step 1: Extracting YouTube transcript...")
        result = extract_youtube_transcript(url)
        
        if not result.get('success'):
            error_msg = result.get('error', 'Unknown error')
            logger.error(f"Step 1: Failed - {error_msg}")
            logger.info("=" * 80)
            return jsonify({
                'success': False,
                'error': error_msg,
                'suggestion': result.get('suggestion', 'Please try again')
            }), 400
        
        # Step 2: Extract transcript text
        transcript = result.get('transcript', '')
        if not transcript:
            logger.error("Step 2: No transcript extracted from video")
            logger.info("=" * 80)
            return jsonify({
                'success': False,
                'error': 'No transcript available for this video',
                'suggestion': 'This video may not have captions enabled'
            }), 400
        
        transcript_length = len(transcript)
        video_title = result.get('metadata', {}).get('title', 'Unknown')
        video_channel = result.get('metadata', {}).get('channel', 'Unknown')
        
        logger.info(f"Step 2: Success! Extracted {transcript_length} characters")
        logger.info(f"  - Video Title: {video_title}")
        logger.info(f"  - Channel: {video_channel}")
        
        # Step 3: Create job via transcript_routes API
        logger.info("Step 3: Creating analysis job...")
        job_response = transcript_job_api(transcript, 'youtube', result.get('metadata', {}))
        
        if not job_response.get('success'):
            logger.error(f"Step 3: Failed to create job - {job_response.get('error')}")
            logger.info("=" * 80)
            return jsonify({
                'success': False,
                'error': 'Failed to start analysis',
                'suggestion': 'Please try again'
            }), 500
        
        job_id = job_response.get('job_id')
        logger.info(f"Step 3: ✓ Created job {job_id}")
        
        logger.info("Step 4: Background processing started")
        logger.info("=" * 80)
        
        # Step 4: Return job_id to frontend
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'YouTube video processed successfully - analysis in progress',
            'video_title': video_title,
            'video_channel': video_channel,
            'transcript_length': transcript_length,
            'status_url': f'/api/transcript/status/{job_id}'
        })
        
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
        'version': '10.2.4',
        'timestamp': datetime.utcnow().isoformat(),
        'features': {
            'news_analysis': 'v8.5.1 - 7 AI services with bias awareness',
            'debate_arena': 'v9.0.0 - Challenge & Pick-a-Fight modes' if database_url and db else 'disabled',
            'live_streaming': 'v10.0.0 - YouTube Live analysis with AssemblyAI',
            'youtube_transcripts': 'v10.2.3 - YouTube URL transcript extraction (FIXED with job integration)',
            'transcript_analysis': 'v10.2.3 - Full transcript fact-checking with proper job management',
            'navigation': 'v10.2.4 - All menu items work (Features, About, Contact, Live Stream, Debate Arena)'
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
    logger.info("TRUTHLENS NEWS ANALYZER - STARTING v10.2.4")
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
    
    if os.getenv('SCRAPINGBEE_API_KEY') and transcript_job_api:
        logger.info("  ✓ YouTube Transcript Extraction - Video transcript analysis")
        logger.info("    - Extract transcripts from any YouTube video")
        logger.info("    - Automatic caption retrieval")
        logger.info("    - Comprehensive fact-checking with job management")
        logger.info("    - ✅ FIXED: Now properly creates jobs and returns job_id")
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
    logger.info("STATIC PAGE ROUTES:")
    logger.info("  ✓ / (News Analysis)")
    logger.info("  ✓ /transcript (Transcript Analysis)")
    logger.info("  ✓ /features (Features Page) - NEW IN v10.2.4")
    logger.info("  ✓ /about (About Page) - NEW IN v10.2.4")
    logger.info("  ✓ /contact (Contact Page) - NEW IN v10.2.4")
    logger.info("  ✓ /live-stream (Live Stream Page) - NEW IN v10.2.4")
    logger.info("  ✓ /debate-arena (Debate Arena Page) - NEW IN v10.2.4")
    logger.info("")
    
    logger.info("VERSION HISTORY:")
    logger.info("NEW IN v10.2.4 (NAVIGATION FIX):")
    logger.info("  ✅ FIXED: Added 5 missing static page routes")
    logger.info("  ✅ ADDED: /features route")
    logger.info("  ✅ ADDED: /about route")
    logger.info("  ✅ ADDED: /contact route")
    logger.info("  ✅ ADDED: /live-stream route")
    logger.info("  ✅ ADDED: /debate-arena route")
    logger.info("  ✅ RESULT: All navigation menu items now work!")
    logger.info("")
    logger.info("NEW IN v10.2.3 (YOUTUBE JOB FIX):")
    logger.info("  ✅ FIXED: YouTube endpoint now creates job_id properly")
    logger.info("  ✅ FIXED: Integrated /api/youtube/process with job management")
    logger.info("  ✅ FIXED: No more 'undefined' job_id or 404 polling errors")
    logger.info("=" * 80)
    
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# I did no harm and this file is not truncated
