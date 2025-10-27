"""
File: app.py
Last Updated: October 27, 2025 - v10.2.6
Description: Main Flask application with complete news analysis, transcript checking, and YouTube features

CHANGES IN v10.2.6 (October 27, 2025):
========================
NEW FEATURE: Simple Debate Arena - Anonymous, No-Auth Debate System
- ADDED: simple_debate_models.py integration - Simplified database models (no User model!)
- ADDED: simple_debate_routes.py integration - Anonymous debate API routes
- ADDED: /simple-debate-arena route - New simplified debate interface
- FEATURE: Three simple modes - Pick a Fight, Join a Fight, Judgement City (Vote)
- FEATURE: Anonymous voting via browser fingerprint
- FEATURE: 250-word argument limit with live counter
- FEATURE: Real-time voting bar chart visualization
- PRESERVED: All v10.2.5 functionality including old /debate-arena (DO NO HARM ✓)

HOW IT WORKS:
1. Pick a Fight - User creates debate topic and first argument
2. Join a Fight - Another user adds opposing argument
3. Judgement City - Users vote on arguments with bar chart visualization
4. No authentication required - completely anonymous
5. Browser fingerprint prevents duplicate voting

DEPLOYMENT REQUIREMENTS:
- Add simple_debate_models.py to project root
- Add simple_debate_routes.py to project root
- Add templates/simple-debate-arena.html
- Deploy updated app.py
- All existing features preserved (news analysis, transcripts, old debate arena)

CHANGES IN v10.2.5 (October 27, 2025):
========================
NEW FEATURE: Transcript Creation Without Analysis
- ADDED: /api/youtube/create-transcript endpoint - Extract transcript only, no fact-checking
- ADDED: /api/youtube/download-transcript-pdf endpoint - Generate formatted PDF from transcript
- ADDED: PDF generation using reportlab library
- FEATURE: Users can now choose "Create Transcript" or "Analyze Video"
- FEATURE: One-click PDF download with video metadata
- PRESERVED: All existing functionality (DO NO HARM ✓)

HOW IT WORKS:
1. User enters YouTube URL
2. User clicks "Create Transcript" button (new)
3. System extracts transcript using ScrapingBee
4. Transcript displayed with metadata (title, channel, duration, date)
5. User can download as formatted PDF
6. No job creation, no analysis, instant results

TruthLens News Analyzer - Complete with Debate Arena & Live Streaming
Version: 10.2.6 - SIMPLE DEBATE ARENA INTEGRATION
Date: October 27, 2025

This file is complete and ready to deploy to GitHub/Render.
Last modified: October 27, 2025 - v10.2.6 SIMPLE DEBATE ARENA
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
        logger.warning(f"  ⚠ Old debate models not found: {e}")
        logger.warning("  ⚠ Old Debate Arena (/debate-arena) will be disabled")
    
    # Import NEW simple debate models (v10.2.6)
    simple_debate_available = False
    try:
        from simple_debate_models import SimpleDebate, SimpleArgument, SimpleVote
        from simple_debate_routes import simple_debate_bp
        
        # Register the simple debate blueprint
        app.register_blueprint(simple_debate_bp)
        
        logger.info("  ✓ Simple debate models imported successfully")
        logger.info("  ✓ Simple debate routes registered at /api/simple-debate")
        simple_debate_available = True
    except ImportError as e:
        logger.warning(f"  ⚠ Simple debate models not found: {e}")
        logger.warning("  ⚠ Simple Debate Arena (/simple-debate-arena) will be disabled")
    
    # Initialize database (create all tables)
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
    """Old Debate Arena page (v9.0.0 - with authentication)"""
    if not old_debate_available:
        return render_template('error.html', 
                             message="Old Debate Arena is not available. Please set DATABASE_URL and ensure debate_models.py exists."), 503
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
        return render_template('error.html', 
                             message="Simple Debate Arena is not available. Please set DATABASE_URL and ensure simple_debate_models.py and simple_debate_routes.py exist."), 503
    return render_template('simple-debate-arena.html')

# ============================================================================
# API ROUTES - NEWS ANALYSIS
# ============================================================================

@app.route('/api/analyze-news', methods=['POST'])
def analyze_news():
    """Main endpoint for news article analysis."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        url = data.get('url')
        article_text = data.get('article_text')
        
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
        
        # Extract article if URL provided
        metadata = None
        if url:
            if not validate_url(url):
                return jsonify({
                    'success': False,
                    'error': 'Invalid URL format'
                }), 400
            
            logger.info(f"Extracting article from URL: {url}")
            extracted_text, metadata = extract_article_text(url)
            
            if not extracted_text:
                return jsonify({
                    'success': False,
                    'error': 'Failed to extract article text from URL. Please try pasting the article text directly.'
                }), 400
            
            article_text = extracted_text
            logger.info(f"Successfully extracted {len(article_text)} characters")
        
        # Analyze the article
        logger.info("Starting comprehensive analysis...")
        raw_results = news_analyzer_service.analyze_news(
            article_text=article_text,
            url=url
        )
        
        logger.info("Analysis complete - transforming data...")
        
        # Transform the results
        final_results = data_transformer.transform_analysis_results(
            raw_results=raw_results,
            url=url,
            metadata=metadata
        )
        
        logger.info("Data transformation complete")
        logger.info("=" * 80)
        
        return jsonify({
            'success': True,
            'results': final_results
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
        logger.error(f"Status check error for job {job_id}: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# API ROUTES - TRANSCRIPT CREATION WITHOUT ANALYSIS (v10.2.5)
# ============================================================================

@app.route('/api/youtube/create-transcript', methods=['POST'])
def create_transcript_only():
    """
    NEW in v10.2.5: Create transcript from YouTube URL without analysis
    Returns transcript data immediately without creating a job
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
        
        # Extract transcript directly
        transcript_data = extract_youtube_transcript(youtube_url)
        
        if not transcript_data or not transcript_data.get('transcript'):
            return jsonify({
                'success': False,
                'error': 'Failed to extract transcript. Please check the URL and try again.'
            }), 400
        
        logger.info(f"✅ Successfully extracted transcript ({len(transcript_data['transcript'])} characters)")
        
        return jsonify({
            'success': True,
            'transcript_data': transcript_data
        })
        
    except Exception as e:
        logger.error(f"Transcript creation error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Failed to create transcript: {str(e)}'
        }), 500


@app.route('/api/youtube/download-transcript-pdf', methods=['POST'])
def download_transcript_pdf():
    """
    NEW in v10.2.5: Generate and download transcript as PDF
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
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor='#1a1a1a',
            spaceAfter=12,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor='#4a4a4a',
            spaceAfter=6,
            spaceBefore=12
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=10,
            textColor='#2a2a2a',
            spaceAfter=6,
            alignment=TA_LEFT
        )
        
        # Build PDF content
        story = []
        
        # Title
        story.append(Paragraph("YouTube Video Transcript", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Metadata
        if transcript_data.get('title'):
            story.append(Paragraph(f"<b>Title:</b> {transcript_data['title']}", body_style))
        if transcript_data.get('channel'):
            story.append(Paragraph(f"<b>Channel:</b> {transcript_data['channel']}", body_style))
        if transcript_data.get('duration'):
            story.append(Paragraph(f"<b>Duration:</b> {transcript_data['duration']}", body_style))
        if transcript_data.get('upload_date'):
            story.append(Paragraph(f"<b>Upload Date:</b> {transcript_data['upload_date']}", body_style))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Transcript content
        story.append(Paragraph("Transcript", heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Split transcript into paragraphs and add to PDF
        transcript_text = transcript_data.get('transcript', '')
        paragraphs = transcript_text.split('\n\n')
        
        for para in paragraphs:
            if para.strip():
                # Escape HTML special characters
                para_clean = para.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(para_clean, body_style))
                story.append(Spacer(1, 0.1*inch))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        # Create response
        response = Response(pdf_data, mimetype='application/pdf')
        
        # Generate filename from title or use default
        title = transcript_data.get('title', 'transcript')
        # Clean filename
        filename = re.sub(r'[^\w\s-]', '', title).strip()
        filename = re.sub(r'[-\s]+', '-', filename)
        filename = f"{filename[:50]}.pdf"  # Limit length
        
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.headers['Content-Length'] = len(pdf_data)
        
        return response
        
    except Exception as e:
        logger.error(f"PDF generation error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'PDF generation failed: {str(e)}'
        }), 500


@app.route('/api/youtube/test-transcript-setup', methods=['GET'])
def test_transcript_setup():
    """
    Diagnostic endpoint to check if transcript creation is properly configured
    """
    issues = []
    status = "healthy"
    
    # Check ScrapingBee API key
    scrapingbee_key = os.getenv('SCRAPINGBEE_API_KEY')
    if not scrapingbee_key:
        issues.append("SCRAPINGBEE_API_KEY not set")
        status = "unhealthy"
    
    # Check reportlab import
    try:
        import reportlab
        reportlab_version = reportlab.Version
    except ImportError:
        issues.append("reportlab not installed")
        reportlab_version = "NOT INSTALLED"
        status = "unhealthy"
    
    # Check if extract_youtube_transcript is available
    try:
        from services.youtube_scraper import extract_youtube_transcript
        youtube_scraper_status = "available"
    except ImportError as e:
        issues.append(f"youtube_scraper import failed: {str(e)}")
        youtube_scraper_status = "NOT AVAILABLE"
        status = "unhealthy"
    
    return jsonify({
        'status': status,
        'transcript_creation_feature': {
            'endpoint_registered': True,
            'scrapingbee_configured': bool(scrapingbee_key),
            'reportlab_installed': reportlab_version,
            'youtube_scraper_available': youtube_scraper_status
        },
        'issues': issues if issues else None,
        'message': 'All checks passed' if status == "healthy" else 'Configuration issues detected'
    })


# HEALTH CHECK & DEBUG ROUTES
# ============================================================================

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'version': '10.2.6',
        'timestamp': datetime.utcnow().isoformat(),
        'features': {
            'news_analysis': 'v8.5.1 - 7 AI services with bias awareness',
            'old_debate_arena': 'v9.0.0 - Challenge & Pick-a-Fight with auth' if old_debate_available else 'disabled',
            'simple_debate_arena': 'v10.2.6 - Anonymous debates with 3 modes' if simple_debate_available else 'disabled',
            'live_streaming': 'v10.0.0 - YouTube Live analysis with AssemblyAI',
            'youtube_transcripts': 'v10.2.3 - YouTube URL transcript extraction (FIXED with job integration)',
            'transcript_analysis': 'v10.2.3 - Full transcript fact-checking with proper job management',
            'transcript_creation': 'v10.2.5 - Create transcript without analysis + PDF download',
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
    logger.info("TRUTHLENS NEWS ANALYZER - STARTING v10.2.6")
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
    logger.info("NEW IN v10.2.6 (SIMPLE DEBATE ARENA):")
    logger.info("  ✅ ADDED: Simple Debate Arena - completely anonymous")
    logger.info("  ✅ ADDED: /simple-debate-arena route and template")
    logger.info("  ✅ ADDED: simple_debate_models.py integration")
    logger.info("  ✅ ADDED: simple_debate_routes.py blueprint registration")
    logger.info("  ✅ FEATURE: Pick a Fight, Join a Fight, Judgement City modes")
    logger.info("  ✅ FEATURE: Browser fingerprint for anonymous voting")
    logger.info("  ✅ FEATURE: 250-word limit with live counter")
    logger.info("  ✅ FEATURE: Real-time voting bar chart")
    logger.info("  ✅ PRESERVED: All v10.2.5 functionality (DO NO HARM)")
    logger.info("")
    logger.info("NEW IN v10.2.5 (TRANSCRIPT CREATION):")
    logger.info("  ✅ ADDED: /api/youtube/create-transcript endpoint")
    logger.info("  ✅ ADDED: /api/youtube/download-transcript-pdf endpoint")
    logger.info("  ✅ FEATURE: Create transcript without full analysis")
    logger.info("  ✅ FEATURE: Download transcripts as formatted PDF")
    logger.info("")
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
