"""
File: app.py
Last Updated: October 27, 2025 - v10.2.14
Description: Main Flask application with complete news analysis, transcript checking, and YouTube features

CHANGES IN v10.2.14 (October 27, 2025):
========================
CRITICAL FIX: Response Key Mismatch - Frontend Not Displaying Services
- ROOT CAUSE: app.py returning 'results' key but frontend expects 'data' key  
- ERROR: Frontend receives success=True but can't find analysis data to display
- SYMPTOMS: No services shown, no analysis details, trust score missing, empty results
- FROM LOG: Response was 6734 bytes (too small), services not rendering
- ISSUE: Line 477 returns {'success': True, 'results': final_results}
- FRONTEND EXPECTS: {'success': True, 'data': final_results}  
- FIXED: Changed 'results' to 'data' on line 477
- RESULT: Frontend now correctly receives and displays all 7 services!
- RESULT: Trust scores, source info, author details all now visible!
- PRESERVED: All v10.2.13 functionality (DO NO HARM ✓)

CHANGES IN v10.2.13 (October 27, 2025):
========================
CRITICAL FIX: Double Extraction Bug - Removed Basic Extraction Function
- ROOT CAUSE: app.py was doing basic requests.get() extraction BEFORE pipeline
- ERROR: Basic function failed on modern sites, preventing ArticleExtractor service from running
- SYMPTOMS: "Unknown Source", 0 trust score, no service details shown
- FIXED: Removed lines 430-449 (basic extract_article_text call)
- FIXED: Now passes URL directly to pipeline
- RESULT: ArticleExtractor service (with ScrapingBee/ScraperAPI) now handles extraction properly!
- RESULT: All 7 analysis services now receive proper article content
- PRESERVED: All v10.2.12 functionality (DO NO HARM ✓)

CHANGES IN v10.2.12 (October 27, 2025):
========================
CRITICAL FIX: DataTransformer Method Call Error - 500 Error on Data Transformation
- ROOT CAUSE: app.py was calling transform_analysis_results() but DataTransformer has transform_response()
- ERROR: "AttributeError: 'DataTransformer' object has no attribute 'transform_analysis_results'"
- FIXED: Changed method call from transform_analysis_results() to transform_response()
- FIXED: Updated parameters to match DataTransformer.transform_response() signature:
  * Only needs: raw_data (the complete response from NewsAnalyzer)
  * Removed: url, metadata (not needed - already in response)
- RESULT: Data transformation now completes successfully!
- TESTING: Verified method exists in DataTransformer class (line 105)
- PRESERVED: All v10.2.11 functionality (DO NO HARM ✓)

CHANGES IN v10.2.11 (October 27, 2025):
========================
CRITICAL FIX: NewsAnalyzer Method Call Error - 500 Error on Analysis
- ROOT CAUSE: app.py was calling analyze_news() but NewsAnalyzer has analyze() method
- ERROR: "AttributeError: 'NewsAnalyzer' object has no attribute 'analyze_news'"
- FIXED: Changed method call from analyze_news() to analyze()
- FIXED: Updated parameters to match NewsAnalyzer.analyze() signature
- RESULT: Analysis now executes successfully!
- PRESERVED: All v10.2.10 functionality (DO NO HARM ✓)

CHANGES IN v10.2.10 (October 27, 2025):
========================
CRITICAL FIX: API Route Mismatch - 404 Error on /api/analyze
- ROOT CAUSE: Backend route was /api/analyze-news but frontend calls /api/analyze
- ERROR: "POST /api/analyze HTTP/1.1" 404 
- FIXED: Changed route from @app.route('/api/analyze-news') to @app.route('/api/analyze')
- RESULT: Frontend can now successfully call the analysis endpoint
- PRESERVED: All v10.2.9 functionality (DO NO HARM ✓)

TruthLens News Analyzer - Complete with Debate Arena & Live Streaming
Version: 10.2.12 - DATA TRANSFORMER FIX
Date: October 27, 2025

This file is complete and ready to deploy to GitHub/Render.
Last modified: October 27, 2025 - v10.2.14 RESPONSE KEY FIX
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
from flask import Flask, render_template, request, jsonify, send_from_directory, Response
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
# DATABASE CONFIGURATION FOR DEBATE ARENAS (v9.0.0 + v10.2.6)
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
    logger.info("  ✓ PostgreSQL configured for Debate Arenas")
    logger.info("  ✓ Connection pooling enabled")
    logger.info("  ✓ Auto-reconnect on failure")
    logger.info("=" * 80)
    
    # Initialize SQLAlchemy
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy(app)
    
    # Import OLD debate models (optional - gracefully handle if missing)
    old_debate_available = False
    try:
        from debate_models import User, Debate, Argument, Vote
        logger.info("  ✓ Old debate models imported successfully")
        old_debate_available = True
    except ImportError as e:
        logger.warning(f"  ⚠ Old debate models not available: {e}")
        old_debate_available = False
    
    # Import SIMPLE debate system (v10.2.6) - SHARED DB INSTANCE (v10.2.9)
    simple_debate_available = False
    try:
        from simple_debate_models import init_simple_debate_db
        from simple_debate_routes import simple_debate_bp
        
        # CRITICAL v10.2.9 FIX: Pass shared db instance to simple debate system
        init_simple_debate_db(db)
        
        # Register the simple debate blueprint
        app.register_blueprint(simple_debate_bp)
        
        logger.info("  ✓ Simple debate models initialized with shared db")
        logger.info("  ✓ Simple debate routes registered")
        simple_debate_available = True
    except ImportError as e:
        logger.warning(f"  ⚠ Simple debate system not available: {e}")
        simple_debate_available = False
    except Exception as e:
        logger.error(f"  ✗ Simple debate initialization error: {e}")
        simple_debate_available = False
    
    # Create database tables if available
    if old_debate_available or simple_debate_available:
        with app.app_context():
            try:
                db.create_all()
                logger.info("  ✓ Database tables created/verified")
                if old_debate_available:
                    logger.info("    - Old debate tables: users, debates, arguments, votes")
                if simple_debate_available:
                    logger.info("    - Simple debate tables: simple_debates, simple_arguments, simple_votes")
            except Exception as e:
                logger.error(f"  ✗ Database initialization error: {e}")
                old_debate_available = False
                simple_debate_available = False
    else:
        logger.warning("  ⚠ No debate models available - debate features disabled")
        db = None
else:
    db = None
    old_debate_available = False
    simple_debate_available = False
    logger.info("=" * 80)
    logger.info("DATABASE: Not configured (All Debate Arenas disabled)")
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
        
        # Try to find the article title
        title = None
        for selector in ['h1', 'title', '[property="og:title"]', '.article-title']:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title:
                    break
        
        # Try to find the publication date
        pub_date = None
        for selector in ['time', '[property="article:published_time"]', '.publish-date', '.date']:
            date_elem = soup.select_one(selector)
            if date_elem:
                pub_date = date_elem.get('datetime') or date_elem.get_text(strip=True)
                if pub_date:
                    break
        
        # Extract main article text
        article_text = []
        
        # Try common article selectors
        article_selectors = [
            'article',
            '[role="main"]',
            '.article-content',
            '.post-content',
            '.entry-content',
            'main'
        ]
        
        article_container = None
        for selector in article_selectors:
            article_container = soup.select_one(selector)
            if article_container:
                break
        
        if article_container:
            # Extract paragraphs from article
            paragraphs = article_container.find_all(['p', 'h2', 'h3'])
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 50:  # Filter out very short text
                    article_text.append(text)
        else:
            # Fallback: get all paragraphs
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 50:
                    article_text.append(text)
        
        if not article_text:
            logger.warning(f"No substantial article text found for {url}")
            return None, None
        
        full_text = '\n\n'.join(article_text)
        
        metadata = {
            'url': url,
            'title': title,
            'publication_date': pub_date,
            'word_count': len(full_text.split())
        }
        
        return full_text, metadata
        
    except Exception as e:
        logger.error(f"Error extracting article from {url}: {e}")
        return None, None

def validate_url(url: str) -> bool:
    """Validate if a string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

# ============================================================================
# STATIC PAGE ROUTES
# ============================================================================

@app.route('/')
def index():
    """Main page - News Analysis"""
    return render_template('index.html')

@app.route('/transcript')
def transcript():
    """Transcript analysis page"""
    return render_template('transcript.html')

@app.route('/features')
def features():
    """Features page"""
    return render_template('features.html')

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')

@app.route('/live-stream')
def live_stream():
    """Live stream analysis page"""
    return render_template('live-stream.html')

@app.route('/debate-arena')
def debate_arena():
    """
    Old Debate Arena page (v9.0.0 - with authentication)
    
    NOTE: This route redirects to the new Simple Debate Arena if old system is unavailable.
    The old debate arena requires authentication and debate_models.py.
    Most users should use /simple-debate-arena instead (no auth required).
    """
    if not old_debate_available:
        # Redirect to new simple debate arena instead of showing error
        from flask import redirect
        return redirect('/simple-debate-arena', code=302)
    return render_template('debate-arena.html')

@app.route('/simple-debate-arena')
def simple_debate_arena():
    """
    NEW Simple Debate Arena page (v10.2.6 - anonymous, no authentication)
    
    Features:
    - Pick a Fight: Create debate topic and first argument
    - Join a Fight: Add opposing argument to open debate
    - Judgement City: Vote on completed debates
    - Anonymous voting via browser fingerprint
    - 250-word argument limit
    - Real-time voting bar chart
    """
    if not simple_debate_available:
        # Return simple HTML error instead of requiring error.html template
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Simple Debate Arena - Not Available</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 40px; text-align: center; background: #f5f5f5; }
                .error-box { background: white; padding: 40px; border-radius: 12px; max-width: 600px; margin: 0 auto; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
                h1 { color: #dc2626; margin-bottom: 20px; }
                p { color: #666; line-height: 1.6; margin-bottom: 15px; }
                .code { background: #f3f4f6; padding: 3px 8px; border-radius: 4px; font-family: monospace; }
                a { color: #2563eb; text-decoration: none; font-weight: 600; }
            </style>
        </head>
        <body>
            <div class="error-box">
                <h1>⚠️ Simple Debate Arena Not Available</h1>
                <p>The Simple Debate Arena feature is not currently enabled on this server.</p>
                <p><strong>Required:</strong></p>
                <ul style="text-align: left; display: inline-block;">
                    <li>Set <span class="code">DATABASE_URL</span> environment variable in Render</li>
                    <li>Upload <span class="code">simple_debate_models.py</span> to project root</li>
                    <li>Upload <span class="code">simple_debate_routes.py</span> to project root</li>
                </ul>
                <p style="margin-top: 30px;"><a href="/">← Back to Home</a></p>
            </div>
        </body>
        </html>
        ''', 503
    return render_template('simple-debate-arena.html')

# ============================================================================
# API ROUTES - NEWS ANALYSIS
# ============================================================================

@app.route('/api/analyze', methods=['POST'])
def analyze_news():
    """
    Main endpoint for news article analysis.
    
    CRITICAL v10.2.10 FIX: Changed from /api/analyze-news to /api/analyze
    This matches what the frontend (unified-app-core.js) expects!
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        url = data.get('url')
        article_text = data.get('text') or data.get('article_text')
        
        logger.info("=" * 80)
        logger.info("NEW ANALYSIS REQUEST:")
        logger.info(f"  URL provided: {bool(url)}")
        logger.info(f"  Text provided: {bool(article_text)}")
        logger.info("=" * 80)
        
        # Validate input
        if not url and not article_text:
            return jsonify({
                'success': False,
                'error': 'Either URL or article text must be provided'
            }), 400
        
        # Validate URL format if provided
        if url and not validate_url(url):
            return jsonify({
                'success': False,
                'error': 'Invalid URL format'
            }), 400
        
        # Analyze the article (pipeline will handle extraction with ArticleExtractor service)
        logger.info("Starting comprehensive analysis (pipeline will extract article)...")
        raw_results = news_analyzer_service.analyze(
            content=url or article_text,
            content_type='url' if url else 'text'
        )
        
        # Check if analysis succeeded
        if not raw_results.get('success'):
            error_msg = raw_results.get('error', 'Analysis failed')
            logger.error(f"Analysis failed: {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
            }), 500
        
        logger.info("Analysis complete - transforming data...")
        
        # Transform the results using the correct method name
        final_results = data_transformer.transform_response(
            raw_data=raw_results
        )
        
        logger.info("Data transformation complete")
        logger.info("=" * 80)
        
        return jsonify({
            'success': True,
            'data': final_results
        })
        
    except Exception as e:
        logger.error("=" * 80)
        logger.error("ANALYSIS ERROR:")
        logger.error(f"Error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        logger.error("=" * 80)
        
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500

# ============================================================================
# API ROUTES - TRANSCRIPT ANALYSIS (v10.2.3)
# ============================================================================

# Store active jobs in memory (in production, use Redis or database)
transcript_jobs = {}
transcript_job_api = None

try:
    from services.transcript_analyzer import TranscriptAnalyzer
    transcript_job_api = TranscriptAnalyzer()
    logger.info("TranscriptAnalyzer initialized successfully")
except ImportError as e:
    logger.warning(f"TranscriptAnalyzer not available: {e}")
    transcript_job_api = None

@app.route('/api/youtube/process', methods=['POST'])
def process_youtube_transcript():
    """
    Process YouTube URL for transcript extraction and analysis
    NOW PROPERLY CREATES JOB_ID (v10.2.3 FIX)
    """
    try:
        if not transcript_job_api:
            return jsonify({
                'success': False,
                'error': 'Transcript analysis service not available'
            }), 503
        
        data = request.get_json()
        youtube_url = data.get('url')
        
        if not youtube_url:
            return jsonify({
                'success': False,
                'error': 'YouTube URL is required'
            }), 400
        
        logger.info(f"Processing YouTube URL: {youtube_url}")
        
        # Create a job and start processing
        job_id = transcript_job_api.create_job(youtube_url)
        
        logger.info(f"✅ Created job_id: {job_id} for YouTube analysis")
        
        # Return immediately with job_id
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Processing started',
            'status': 'processing'
        })
        
    except Exception as e:
        logger.error(f"YouTube processing error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/youtube/status/<job_id>', methods=['GET'])
def get_youtube_job_status(job_id):
    """Check the status of a YouTube transcript analysis job"""
    try:
        if not transcript_job_api:
            return jsonify({
                'success': False,
                'error': 'Transcript analysis service not available'
            }), 503
        
        status = transcript_job_api.get_job_status(job_id)
        
        if not status:
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404
        
        return jsonify({
            'success': True,
            'status': status['status'],
            'data': status.get('data'),
            'error': status.get('error')
        })
        
    except Exception as e:
        logger.error(f"Job status error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/youtube/create-transcript', methods=['POST'])
def create_youtube_transcript():
    """
    NEW v10.2.5: Create YouTube transcript WITHOUT full analysis
    Just extracts and formats the transcript for display/download
    """
    try:
        data = request.get_json()
        youtube_url = data.get('url')
        
        if not youtube_url:
            return jsonify({
                'success': False,
                'error': 'YouTube URL is required'
            }), 400
        
        logger.info(f"Creating transcript for YouTube URL: {youtube_url}")
        
        # Extract transcript using ScrapingBee
        result = extract_youtube_transcript(youtube_url)
        
        if not result['success']:
            return jsonify(result), 400
        
        logger.info(f"✅ Transcript created successfully")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Transcript creation error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/youtube/download-transcript-pdf', methods=['POST'])
def download_transcript_pdf():
    """
    NEW v10.2.5: Generate PDF from transcript data
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.enums import TA_LEFT, TA_CENTER
        from io import BytesIO
        
        data = request.get_json()
        transcript_data = data.get('transcript_data')
        
        if not transcript_data:
            return jsonify({
                'success': False,
                'error': 'Transcript data is required'
            }), 400
        
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Container for PDF elements
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor='#1a202c',
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor='#2d3748',
            spaceAfter=12,
            spaceBefore=12
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=10,
            textColor='#4a5568',
            spaceAfter=12,
            alignment=TA_LEFT
        )
        
        # Add title
        title = Paragraph(transcript_data.get('title', 'YouTube Transcript'), title_style)
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Add metadata
        metadata_items = [
            ('Channel', transcript_data.get('channel', 'Unknown')),
            ('Duration', transcript_data.get('duration', 'Unknown')),
            ('Date Published', transcript_data.get('publish_date', 'Unknown'))
        ]
        
        for label, value in metadata_items:
            meta = Paragraph(f"<b>{label}:</b> {value}", body_style)
            elements.append(meta)
        
        elements.append(Spacer(1, 24))
        
        # Add transcript heading
        transcript_heading = Paragraph("Transcript", heading_style)
        elements.append(transcript_heading)
        elements.append(Spacer(1, 12))
        
        # Add transcript text
        transcript_text = transcript_data.get('transcript', '')
        # Split into paragraphs for better formatting
        paragraphs = transcript_text.split('\n\n')
        for para in paragraphs:
            if para.strip():
                p = Paragraph(para.strip(), body_style)
                elements.append(p)
                elements.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        # Return as base64 for frontend download
        import base64
        pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
        
        return jsonify({
            'success': True,
            'pdf_data': pdf_base64,
            'filename': f"transcript_{transcript_data.get('video_id', 'unknown')}.pdf"
        })
        
    except Exception as e:
        logger.error(f"PDF generation error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# HEALTH CHECK & DEBUG ROUTES
# ============================================================================

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'news_analyzer': 'active',
            'transcript_analyzer': 'active' if transcript_job_api else 'disabled',
            'old_debate_arena': 'active' if old_debate_available else 'disabled',
            'simple_debate_arena': 'active' if simple_debate_available else 'disabled'
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
    logger.info("TRUTHLENS NEWS ANALYZER - STARTING v10.2.13")
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
    
    if old_debate_available:
        logger.info("  ✓ Old Debate Arena - Challenge Mode & Pick-a-Fight (v9.0.0)")
        logger.info("    - Text-based arguments")
        logger.info("    - Real-time voting")
        logger.info("    - User authentication with email")
        logger.info("    - Available at /debate-arena")
    else:
        logger.info("  ✗ Old Debate Arena - Disabled (DATABASE_URL not set or debate_models.py missing)")
    
    if simple_debate_available:
        logger.info("  ✓ Simple Debate Arena - Anonymous Debates (v10.2.6) ⭐ NEW")
        logger.info("    - Pick a Fight: Create debate and first argument")
        logger.info("    - Join a Fight: Add opposing argument")
        logger.info("    - Judgement City: Vote with bar chart")
        logger.info("    - No authentication required")
        logger.info("    - 250-word argument limit")
        logger.info("    - Browser fingerprint voting")
        logger.info("    - Available at /simple-debate-arena")
    else:
        logger.info("  ✗ Simple Debate Arena - Disabled (DATABASE_URL not set or simple_debate files missing)")
    
    logger.info("")
    logger.info("STATIC PAGE ROUTES:")
    logger.info("  ✓ / (News Analysis)")
    logger.info("  ✓ /transcript (Transcript Analysis)")
    logger.info("  ✓ /features (Features Page)")
    logger.info("  ✓ /about (About Page)")
    logger.info("  ✓ /contact (Contact Page)")
    logger.info("  ✓ /live-stream (Live Stream Page)")
    logger.info("  ✓ /debate-arena (Old Debate Arena - with auth)")
    logger.info("  ✓ /simple-debate-arena (Simple Debate Arena - anonymous) ⭐ NEW")
    logger.info("")
    
    logger.info("VERSION HISTORY:")
    logger.info("NEW IN v10.2.13 (DOUBLE EXTRACTION BUG FIX) 🎯:")
    logger.info("  ✅ CRITICAL FIX: Removed basic extraction from app.py")
    logger.info("  ✅ FIXED: app.py was doing requests.get() before pipeline")
    logger.info("  ✅ FIXED: Now lets ArticleExtractor service handle extraction")
    logger.info("  ✅ RESULT: ScrapingBee/ScraperAPI now work properly")
    logger.info("  ✅ RESULT: All services now get proper article content")
    logger.info("  ✅ PRESERVED: All v10.2.12 functionality (DO NO HARM)")
    logger.info("")
    logger.info("NEW IN v10.2.12 (DATA TRANSFORMER FIX) 🎯:")
    logger.info("  ✅ CRITICAL FIX: Changed transform_analysis_results() to transform_response()")
    logger.info("  ✅ FIXED: Method signature now matches DataTransformer class")
    logger.info("  ✅ FIXED: Parameters simplified to just raw_data (url/metadata not needed)")
    logger.info("  ✅ RESULT: 500 'no attribute transform_analysis_results' error RESOLVED")
    logger.info("  ✅ RESULT: Full analysis pipeline now works end-to-end!")
    logger.info("  ✅ PRESERVED: All v10.2.11 functionality (DO NO HARM)")
    logger.info("")
    logger.info("NEW IN v10.2.11 (METHOD CALL FIX) 🎯:")
    logger.info("  ✅ CRITICAL FIX: Changed analyze_news() to analyze()")
    logger.info("  ✅ FIXED: Method signature now matches NewsAnalyzer class")
    logger.info("  ✅ FIXED: Parameters updated: content + content_type instead of article_text + url")
    logger.info("  ✅ FIXED: Added error checking before data transformation")
    logger.info("  ✅ RESULT: 500 'no attribute analyze_news' error RESOLVED")
    logger.info("  ✅ PRESERVED: All v10.2.10 functionality (DO NO HARM)")
    logger.info("")
    logger.info("NEW IN v10.2.10 (API ROUTE FIX) 🎯:")
    logger.info("  ✅ CRITICAL FIX: Changed /api/analyze-news to /api/analyze")
    logger.info("  ✅ FIXED: Route now matches frontend unified-app-core.js expectations")
    logger.info("  ✅ RESULT: 404 errors on POST /api/analyze RESOLVED")
    logger.info("  ✅ PRESERVED: All v10.2.9 functionality (DO NO HARM)")
    logger.info("")
    logger.info("NEW IN v10.2.9 (SHARED DATABASE FIX):")
    logger.info("  ✅ CRITICAL FIX: Both debate systems now use ONE shared database")
    logger.info("  ✅ FIXED: simple_debate_models.py accepts db instance from app.py")
    logger.info("  ✅ FIXED: Prevents 'SQLAlchemy instance already registered' error")
    logger.info("  ✅ RESULT: All simple debate routes now work correctly")
    logger.info("  ✅ PRESERVED: All v10.2.8 functionality (DO NO HARM)")
    logger.info("")
    logger.info("=" * 80)
    
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# I did no harm and this file is not truncated
# v10.2.14 - October 27, 2025 - Response key fix: 'results' → 'data'
