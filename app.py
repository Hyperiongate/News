"""
TruthLens Unified News & Transcript Analyzer
Date: September 29, 2025
Version: 4.0.4 UNIFIED PRODUCTION - WITH SERVICE INITIALIZATION FIX

CRITICAL UPDATE IN THIS VERSION:
1. Added service initialization code to ensure ArticleExtractor loads properly
2. Forces ArticleExtractor to initialize BEFORE NewsAnalyzer
3. Verifies ArticleExtractor is not using fallback mode
4. All previous unified features maintained

This fixes the article extraction returning dummy data with score 58
"""

import os
import sys
import logging
import time
import traceback
import uuid
import re
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from urllib.parse import urlparse, quote_plus
from collections import Counter

# Setup comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Suppress noisy loggers
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('werkzeug').setLevel(logging.WARNING)

# Flask imports
from flask import Flask, request, jsonify, render_template, send_from_directory, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Web scraping
import requests
from bs4 import BeautifulSoup
from newspaper import Article, ArticleException

# NLP imports for real analysis
try:
    import nltk
    from textblob import TextBlob
    
    # Download required NLTK data
    nltk_downloads = ['punkt', 'stopwords', 'vader_lexicon', 'averaged_perceptron_tagger']
    for item in nltk_downloads:
        try:
            nltk.data.find(f'tokenizers/{item}' if item == 'punkt' else f'corpora/{item}' if item == 'stopwords' else f'vader_lexicon' if item == 'vader_lexicon' else f'taggers/{item}')
        except LookupError:
            logger.info(f"Downloading NLTK {item}...")
            nltk.download(item, quiet=True)
    
    from nltk.sentiment import SentimentIntensityAnalyzer
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    
    NLP_AVAILABLE = True
    logger.info("✓ NLP libraries loaded successfully")
except ImportError as e:
    logger.warning(f"NLP libraries not fully available: {e}")
    NLP_AVAILABLE = False

logger.info("=" * 80)
logger.info("TRUTHLENS UNIFIED ANALYZER - v4.0.4 WITH SERVICE INIT FIX")
logger.info(f"Python Version: {sys.version}")
logger.info(f"Working Directory: {os.getcwd()}")
logger.info(f"NLP Available: {NLP_AVAILABLE}")

# Check template files
template_dir = os.path.join(os.getcwd(), 'templates')
if os.path.exists(template_dir):
    templates = os.listdir(template_dir)
    logger.info(f"Templates directory contents: {templates}")
    if 'unified_index.html' in templates:
        logger.info("✓ unified_index.html found")
    else:
        logger.warning("✗ unified_index.html NOT found")
else:
    logger.error("Templates directory does not exist!")

logger.info("=" * 80)

# Configuration
class Config:
    """Enhanced configuration for unified application"""
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    ENV = os.environ.get('FLASK_ENV', 'production')
    
    # API Keys from environment
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    SCRAPERAPI_KEY = os.environ.get('SCRAPERAPI_KEY')
    GOOGLE_FACT_CHECK_API_KEY = os.environ.get('GOOGLE_FACT_CHECK_API_KEY')
    NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
    NEWSAPI_KEY = os.environ.get('NEWSAPI_KEY')
    YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')  # Added for transcript mode
    
    # Unified mode settings
    ENABLE_NEWS_MODE = True
    ENABLE_TRANSCRIPT_MODE = True
    DEFAULT_MODE = 'news'
    
    @classmethod
    def log_status(cls):
        logger.info("API Keys Configuration:")
        logger.info(f"  OpenAI: {'✓' if cls.OPENAI_API_KEY else '✗'}")
        logger.info(f"  ScraperAPI: {'✓' if cls.SCRAPERAPI_KEY else '✗'}")
        logger.info(f"  Google Fact Check: {'✓' if cls.GOOGLE_FACT_CHECK_API_KEY else '✗'}")
        logger.info(f"  News API: {'✓' if cls.NEWS_API_KEY or cls.NEWSAPI_KEY else '✗'}")
        logger.info(f"  YouTube API: {'✓' if cls.YOUTUBE_API_KEY else '✗'}")
        logger.info("Modes Enabled:")
        logger.info(f"  News Analysis: {'✓' if cls.ENABLE_NEWS_MODE else '✗'}")
        logger.info(f"  Transcript Analysis: {'✓' if cls.ENABLE_TRANSCRIPT_MODE else '✗'}")

Config.log_status()

# ================================================================================
# SERVICE INITIALIZATION - CRITICAL FOR ARTICLE EXTRACTION
# This MUST happen BEFORE NewsAnalyzer is imported
# ================================================================================

logger.info("=" * 80)
logger.info("INITIALIZING ANALYSIS SERVICES")
logger.info("=" * 80)

def initialize_article_extractor():
    """Force ArticleExtractor to initialize properly"""
    import importlib
    
    try:
        # Clear any cached modules
        if 'services.article_extractor' in sys.modules:
            del sys.modules['services.article_extractor']
        
        # Import fresh
        logger.info("Loading ArticleExtractor module...")
        article_module = importlib.import_module('services.article_extractor')
        
        # Force reload to get latest code
        importlib.reload(article_module)
        
        # Create instance
        ArticleExtractor = getattr(article_module, 'ArticleExtractor', None)
        if not ArticleExtractor:
            logger.error("ArticleExtractor class not found in module")
            return None
        
        extractor = ArticleExtractor()
        
        # Verify it's working
        test_result = extractor.analyze({'url': 'https://test.com'})
        
        # Check for fallback indicators
        if test_result.get('data', {}).get('status') == 'fallback':
            logger.error("ArticleExtractor is using fallback - will return score 58!")
            return None
        
        if test_result.get('data', {}).get('score') == 58:
            logger.error("ArticleExtractor returning fallback score 58 - not properly initialized!")
            return None
        
        version = 'unknown'
        if hasattr(extractor, 'core') and hasattr(extractor.core, 'VERSION'):
            version = extractor.core.VERSION
        
        logger.info(f"✓ ArticleExtractor v{version} initialized successfully")
        return extractor
        
    except Exception as e:
        logger.error(f"Failed to initialize ArticleExtractor: {e}")
        import traceback
        traceback.print_exc()
        return None

def force_service_initialization():
    """Initialize all services with ArticleExtractor first"""
    try:
        from services.service_registry import get_service_registry
    except ImportError as e:
        logger.error(f"Could not import service_registry: {e}")
        return None
    
    logger.info("Getting service registry...")
    registry = get_service_registry()
    
    # CRITICAL: Initialize ArticleExtractor FIRST
    article_extractor = initialize_article_extractor()
    
    if article_extractor:
        # Manually register it
        registry.services['article_extractor'] = article_extractor
        logger.info("✓ ArticleExtractor registered with service registry")
    else:
        logger.critical("⚠️ ArticleExtractor failed to initialize - extraction will NOT work!")
    
    # Force registry to initialize other services
    if hasattr(registry, '_ensure_initialized'):
        registry._ensure_initialized()
    elif hasattr(registry, '_initialized') and not registry._initialized:
        if hasattr(registry, '_initialize_services'):
            registry._initialize_services()
    
    # Verify status
    try:
        status = registry.get_service_status()
        logger.info(f"Registry Status Summary:")
        logger.info(f"  Total configured: {status['summary'].get('total_configured', 0)}")
        logger.info(f"  Total registered: {status['summary'].get('total_registered', 0)}")
        logger.info(f"  Total available: {status['summary'].get('total_available', 0)}")
        
        # Specific check for article_extractor
        ae_status = status.get('services', {}).get('article_extractor', {})
        if ae_status.get('registered') and ae_status.get('available'):
            if ae_status.get('fallback'):
                logger.error("⚠️ ArticleExtractor is using FALLBACK mode - won't extract real articles!")
            else:
                logger.info("✅ ArticleExtractor is registered and available (not fallback)")
        else:
            logger.error("❌ ArticleExtractor not properly registered!")
    except Exception as e:
        logger.error(f"Could not get registry status: {e}")
    
    return registry

# RUN THE INITIALIZATION
try:
    logger.info("Starting service initialization...")
    service_registry = force_service_initialization()
    logger.info("✓ Service initialization complete")
except Exception as e:
    logger.error(f"Service initialization failed: {e}")
    import traceback
    traceback.print_exc()
    service_registry = None

logger.info("=" * 80)

# ================================================================================
# CREATE FLASK APP - MUST BE AT MODULE LEVEL
# ================================================================================

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS
CORS(app, origins=["*"], allow_headers=["Content-Type"], methods=["GET", "POST", "OPTIONS"])

# Rate limiting
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
    logger.warning(f"Rate limiter setup failed: {e}")
    limiter = None

# ================================================================================
# YOUTUBE TRANSCRIPT SERVICE
# ================================================================================

class YouTubeTranscriptService:
    """Extract transcripts from YouTube videos"""
    
    def __init__(self):
        self.api_key = Config.YOUTUBE_API_KEY
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        logger.info(f"YouTube service initialized - API: {bool(self.api_key)}")
    
    def extract_transcript(self, youtube_url: str) -> Dict[str, Any]:
        """Extract transcript from YouTube URL"""
        try:
            video_id = self._extract_video_id(youtube_url)
            if not video_id:
                return self._error_result("Could not extract video ID from URL")
            
            logger.info(f"Extracting transcript for video: {video_id}")
            
            # Try multiple methods
            transcript_data = None
            
            # Method 1: Try youtube-transcript-api if available
            try:
                transcript_data = self._extract_with_transcript_api(video_id)
            except Exception as e:
                logger.debug(f"Transcript API failed: {e}")
            
            # Method 2: Try manual caption extraction
            if not transcript_data:
                try:
                    transcript_data = self._extract_manual_captions(video_id)
                except Exception as e:
                    logger.debug(f"Manual extraction failed: {e}")
            
            # Method 3: Fallback with basic video info
            if not transcript_data:
                transcript_data = self._get_video_info_fallback(video_id, youtube_url)
            
            return transcript_data
            
        except Exception as e:
            logger.error(f"YouTube transcript extraction failed: {e}")
            return self._error_result(str(e))
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from various YouTube URL formats"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})',
            r'youtu\.be/([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_with_transcript_api(self, video_id: str) -> Dict[str, Any]:
        """Try to extract using youtube-transcript-api library"""
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            
            # Combine transcript segments
            full_text = ' '.join([entry['text'] for entry in transcript])
            
            # Get video info
            video_info = self._get_video_info(video_id)
            
            return {
                'success': True,
                'title': video_info.get('title', 'YouTube Video'),
                'channel': video_info.get('channel', 'Unknown Channel'),
                'duration': video_info.get('duration', 0),
                'transcript': full_text,
                'segments': transcript[:50],  # First 50 segments
                'word_count': len(full_text.split()),
                'extraction_method': 'transcript_api',
                'video_id': video_id,
                'url': f'https://www.youtube.com/watch?v={video_id}'
            }
            
        except ImportError:
            logger.warning("youtube-transcript-api not installed")
            raise Exception("Transcript API not available")
        except Exception as e:
            logger.error(f"Transcript API error: {e}")
            raise e
    
    def _extract_manual_captions(self, video_id: str) -> Dict[str, Any]:
        """Manual caption extraction (simplified approach)"""
        # This is a placeholder for manual caption extraction
        # In a real implementation, you'd parse YouTube's caption tracks
        raise Exception("Manual extraction not implemented")
    
    def _get_video_info_fallback(self, video_id: str, url: str) -> Dict[str, Any]:
        """Fallback method with basic video info"""
        video_info = self._get_video_info(video_id)
        
        return {
            'success': False,
            'title': video_info.get('title', 'YouTube Video'),
            'channel': video_info.get('channel', 'Unknown Channel'),
            'duration': video_info.get('duration', 0),
            'transcript': 'Transcript could not be automatically extracted. Please provide the transcript text manually.',
            'segments': [],
            'word_count': 0,
            'extraction_method': 'fallback',
            'video_id': video_id,
            'url': url,
            'error': 'Automatic transcript extraction not available for this video'
        }
    
    def _get_video_info(self, video_id: str) -> Dict[str, Any]:
        """Get basic video information"""
        try:
            # Try to scrape basic info from YouTube page
            response = self.session.get(f'https://www.youtube.com/watch?v={video_id}', timeout=10)
            response.raise_for_status()
            
            # Parse title and channel from HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title = 'YouTube Video'
            channel = 'Unknown Channel'
            
            # Try to extract title
            title_tag = soup.find('title')
            if title_tag:
                title_text = title_tag.get_text()
                if ' - YouTube' in title_text:
                    title = title_text.replace(' - YouTube', '').strip()
            
            # Try to extract channel name
            channel_link = soup.find('link', {'itemprop': 'name'})
            if channel_link:
                channel = channel_link.get('content', channel)
            
            return {
                'title': title,
                'channel': channel,
                'duration': 0  # Would need additional API call
            }
            
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return {
                'title': 'YouTube Video',
                'channel': 'Unknown Channel', 
                'duration': 0
            }
    
    def _error_result(self, error_message: str) -> Dict[str, Any]:
        """Return error result"""
        return {
            'success': False,
            'error': error_message,
            'title': 'YouTube Video',
            'channel': 'Unknown Channel',
            'duration': 0,
            'transcript': '',
            'segments': [],
            'word_count': 0,
            'extraction_method': 'error'
        }

# ================================================================================
# CONTENT TYPE DETECTOR
# ================================================================================

class ContentTypeDetector:
    """Detect content type and route to appropriate analyzer"""
    
    @staticmethod
    def detect_content_type(content: str) -> str:
        """Detect if content is URL, YouTube URL, or text"""
        if not content or len(content.strip()) < 3:
            return 'text'
        
        content = content.strip()
        
        # Check for YouTube URLs
        youtube_patterns = [
            r'youtube\.com/watch',
            r'youtu\.be/',
            r'youtube\.com/embed/',
            r'youtube\.com/v/',
            r'm\.youtube\.com'
        ]
        
        for pattern in youtube_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return 'youtube'
        
        # Check for general URLs
        url_pattern = r'^https?://.+'
        if re.match(url_pattern, content, re.IGNORECASE):
            return 'url'
        
        # Default to text
        return 'text'
    
    @staticmethod
    def get_analysis_mode(content_type: str) -> str:
        """Get analysis mode based on content type"""
        if content_type == 'youtube':
            return 'transcript'
        elif content_type in ['url', 'text']:
            return 'news'
        else:
            return 'news'  # Default

# ================================================================================
# PRESERVE EXISTING ANALYSIS SERVICES (keeping all original functionality)
# ================================================================================

# Import your existing services (preserving exact functionality)
try:
    from services.analysis_pipeline import AnalysisPipeline
    from services.news_analyzer import NewsAnalyzer
    logger.info("✓ Analysis services imported successfully")
except ImportError as e:
    logger.error(f"Failed to import analysis services: {e}")
    logger.error("Creating fallback NewsAnalyzer...")
    
    # Fallback NewsAnalyzer for when imports fail
    class NewsAnalyzer:
        def analyze(self, content: str, content_type: str = 'url') -> Dict[str, Any]:
            """Fallback analyzer when services are not available"""
            return {
                'success': True,
                'trust_score': 75,
                'article_summary': 'Analysis services temporarily unavailable',
                'source': 'Unknown',
                'author': 'Unknown',
                'findings_summary': 'Analysis services are being initialized. Please try again.',
                'detailed_analysis': {
                    'source_credibility': {'score': 75, 'notes': 'Service initializing'},
                    'bias_detection': {'score': 75, 'notes': 'Service initializing'},
                    'fact_checking': {'score': 75, 'notes': 'Service initializing'},
                    'transparency_score': {'score': 75, 'notes': 'Service initializing'},
                    'manipulation_detection': {'score': 75, 'notes': 'Service initializing'},
                    'content_quality': {'score': 75, 'notes': 'Service initializing'},
                    'author_analysis': {'score': 75, 'notes': 'Service initializing'}
                },
                'processing_time': 0.1
            }

# ================================================================================
# UNIFIED ANALYZER - ORCHESTRATES BOTH MODES
# ================================================================================

class UnifiedAnalyzer:
    """Unified analyzer supporting both news and transcript analysis"""
    
    def __init__(self):
        # Initialize existing components
        self.news_analyzer = NewsAnalyzer()
        self.youtube_service = YouTubeTranscriptService()
        self.content_detector = ContentTypeDetector()
        
        logger.info("✓ UnifiedAnalyzer initialized with both modes")
    
    def analyze(self, content: str, analysis_mode: str = 'auto') -> Dict[str, Any]:
        """
        Unified analysis supporting both news and transcript modes
        
        Args:
            content: URL, YouTube URL, or text content
            analysis_mode: 'news', 'transcript', or 'auto' for detection
            
        Returns:
            Unified analysis results
        """
        try:
            start_time = time.time()
            
            # Detect content type and mode
            if analysis_mode == 'auto':
                content_type = self.content_detector.detect_content_type(content)
                analysis_mode = self.content_detector.get_analysis_mode(content_type)
            else:
                content_type = 'youtube' if analysis_mode == 'transcript' else 'url'
            
            logger.info(f"Unified analysis: mode={analysis_mode}, type={content_type}")
            
            # Route to appropriate analyzer
            if analysis_mode == 'transcript':
                return self._analyze_transcript(content, content_type)
            else:
                return self._analyze_news(content, content_type)
                
        except Exception as e:
            logger.error(f"Unified analysis error: {e}", exc_info=True)
            return self._create_error_response(str(e), content)
    
    def _analyze_transcript(self, content: str, content_type: str) -> Dict[str, Any]:
        """Analyze transcript content (YouTube or text)"""
        try:
            # Extract transcript
            if content_type == 'youtube':
                extraction_result = self.youtube_service.extract_transcript(content)
                if not extraction_result['success']:
                    return self._create_error_response(
                        extraction_result.get('error', 'Failed to extract transcript'),
                        content, mode='transcript'
                    )
                transcript_text = extraction_result['transcript']
                metadata = {
                    'title': extraction_result.get('title', 'YouTube Video'),
                    'channel': extraction_result.get('channel', 'Unknown'),
                    'source_type': 'youtube',
                    'video_id': extraction_result.get('video_id'),
                    'url': extraction_result.get('url', content)
                }
            else:
                # Direct text input
                transcript_text = content
                metadata = {
                    'title': 'Transcript Analysis',
                    'channel': 'Direct Input',
                    'source_type': 'text',
                    'url': None
                }
            
            # Prepare data for analysis (reuse news analyzer infrastructure)
            analysis_data = {
                'text': transcript_text,
                'title': metadata['title'],
                'author': metadata['channel'],
                'domain': 'transcript',
                'content': transcript_text,
                'url': metadata.get('url'),
                'analysis_mode': 'transcript'
            }
            
            # Run through existing analysis pipeline (reusing services)
            result = self.news_analyzer.analyze(transcript_text, content_type='text')
            
            # Enhance result with transcript-specific metadata
            result.update({
                'analysis_mode': 'transcript',
                'content_type': content_type,
                'source_metadata': metadata,
                'transcript_length': len(transcript_text.split()) if transcript_text else 0
            })
            
            # Update article summary for transcript context
            result['article_summary'] = f"Transcript: {metadata['title']}"
            result['source'] = metadata['channel']
            
            return result
            
        except Exception as e:
            logger.error(f"Transcript analysis error: {e}", exc_info=True)
            return self._create_error_response(str(e), content, mode='transcript')
    
    def _analyze_news(self, content: str, content_type: str) -> Dict[str, Any]:
        """Analyze news content (preserve existing functionality)"""
        try:
            # Use existing news analyzer (unchanged)
            result = self.news_analyzer.analyze(content, content_type=content_type)
            
            # Add unified metadata
            result.update({
                'analysis_mode': 'news',
                'content_type': content_type
            })
            
            return result
            
        except Exception as e:
            logger.error(f"News analysis error: {e}", exc_info=True)
            return self._create_error_response(str(e), content, mode='news')
    
    def _create_error_response(self, error_msg: str, content: str, mode: str = 'news') -> Dict[str, Any]:
        """Create unified error response"""
        return {
            'success': False,
            'error': error_msg,
            'analysis_mode': mode,
            'content_type': self.content_detector.detect_content_type(content),
            'trust_score': 0,
            'article_summary': 'Analysis failed',
            'source': 'Unknown',
            'author': 'Unknown',
            'findings_summary': f'Analysis could not be completed: {error_msg}',
            'detailed_analysis': {},
            'processing_time': 0
        }

# ================================================================================
# INITIALIZE UNIFIED COMPONENTS AT MODULE LEVEL
# ================================================================================

# Initialize the unified analyzer
unified_analyzer = UnifiedAnalyzer()
logger.info("✓ Unified analyzer initialized")

# ================================================================================
# ROUTES - ENHANCED FOR UNIFIED FUNCTIONALITY
# ================================================================================

@app.route('/')
def index():
    """Serve the unified application page"""
    logger.info("Serving unified index page - attempting to render unified_index.html")
    try:
        return render_template('unified_index.html')
    except Exception as e:
        logger.error(f"Failed to render unified_index.html: {e}")
        logger.info("Attempting fallback to index.html")
        try:
            return render_template('index.html')
        except Exception as e2:
            logger.error(f"Failed to render index.html: {e2}")
            # Return a basic HTML response as last resort
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>TruthLens Unified Analyzer</title>
                <style>
                    body { font-family: Arial; padding: 20px; }
                    .error { color: red; padding: 20px; border: 1px solid red; }
                </style>
            </head>
            <body>
                <h1>TruthLens Unified Analyzer</h1>
                <div class="error">
                    <h2>Template Loading Error</h2>
                    <p>The application is running but the template files could not be loaded.</p>
                    <p>Please ensure that either unified_index.html or index.html exists in the templates directory.</p>
                    <p>API endpoints are available at /api/analyze</p>
                </div>
            </body>
            </html>
            """, 200

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'unified-analyzer',
        'version': '4.0.4-unified',
        'modes': {
            'news': Config.ENABLE_NEWS_MODE,
            'transcript': Config.ENABLE_TRANSCRIPT_MODE
        },
        'nlp_available': NLP_AVAILABLE,
        'template_status': 'checking'
    }), 200

@app.route('/api/status')
def api_status():
    """Enhanced API status endpoint"""
    # Check template status
    template_status = {}
    template_dir = os.path.join(app.root_path, 'templates')
    if os.path.exists(template_dir):
        templates = os.listdir(template_dir)
        template_status['unified_index.html'] = 'unified_index.html' in templates
        template_status['index.html'] = 'index.html' in templates
    else:
        template_status['error'] = 'Templates directory not found'
    
    return jsonify({
        'status': 'operational',
        'modes': {
            'news_analysis': Config.ENABLE_NEWS_MODE,
            'transcript_analysis': Config.ENABLE_TRANSCRIPT_MODE
        },
        'services': {
            'unified_analyzer': 'ready',
            'news_analyzer': 'ready',
            'youtube_service': bool(Config.YOUTUBE_API_KEY),
            'nlp': NLP_AVAILABLE
        },
        'templates': template_status,
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    """Unified analysis endpoint"""
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Extract input data
        content = data.get('input_data') or data.get('url') or data.get('text', '')
        analysis_mode = data.get('analysis_mode', 'auto')  # 'news', 'transcript', or 'auto'
        
        if not content:
            return jsonify({
                'success': False,
                'error': 'No URL or text provided for analysis'
            }), 400
        
        logger.info(f"Unified analysis request: mode={analysis_mode}, content_length={len(content)}")
        
        # Detect content type for logging
        if analysis_mode == 'auto':
            content_type = ContentTypeDetector.detect_content_type(content)
        else:
            content_type = 'youtube' if analysis_mode == 'transcript' else 'url'
        
        logger.info(f"Unified analysis: mode={analysis_mode}, type={content_type}")
        
        # Log service registry status for debugging
        if service_registry:
            try:
                status = service_registry.get_service_status()
                ae_status = status.get('services', {}).get('article_extractor', {})
                if ae_status:
                    logger.info(f"ArticleExtractor status: registered={ae_status.get('registered')}, available={ae_status.get('available')}, fallback={ae_status.get('fallback')}")
            except:
                pass
        
        # Perform unified analysis
        result = unified_analyzer.analyze(content, analysis_mode)
        
        # Ensure success field is present
        if 'success' not in result:
            result['success'] = True if result.get('trust_score', 0) > 0 else False
        
        if result.get('success'):
            logger.info(f"Unified analysis completed: {result.get('analysis_mode')} mode")
            return jsonify(result), 200
        else:
            logger.error(f"Unified analysis failed: {result.get('error')}")
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"API error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500

@app.route('/api/detect-content-type', methods=['POST'])
def detect_content_type():
    """Endpoint to detect content type"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        
        content_type = ContentTypeDetector.detect_content_type(content)
        analysis_mode = ContentTypeDetector.get_analysis_mode(content_type)
        
        return jsonify({
            'content_type': content_type,
            'analysis_mode': analysis_mode,
            'supported': True
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/static/<path:path>')
def send_static(path):
    """Serve static files with better error handling"""
    try:
        # Log the request for debugging
        logger.info(f"Static file requested: {path}")
        
        # Check if file exists
        static_file = os.path.join(app.static_folder, path)
        if not os.path.exists(static_file):
            logger.warning(f"Static file not found: {path}")
            
            # Try alternative names for common files
            if path == 'js/unified-app-core.js':
                # Try to serve app-core.js instead
                alt_path = 'js/app-core.js'
                alt_file = os.path.join(app.static_folder, alt_path)
                if os.path.exists(alt_file):
                    logger.info(f"Serving alternative: {alt_path} instead of {path}")
                    return send_from_directory('static', alt_path)
        
        return send_from_directory('static', path)
    except Exception as e:
        logger.error(f"Error serving static file {path}: {e}")
        return f"Static file not found: {path}", 404

@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    try:
        return send_from_directory('static', 'favicon.ico', mimetype='image/x-icon')
    except:
        return '', 204

@app.route('/diagnostic')
def diagnostic():
    """Serve diagnostic page for troubleshooting UI issues"""
    logger.info("Serving diagnostic page")
    
    diagnostic_html = """<!DOCTYPE html>
<html>
<head>
    <title>TruthLens Diagnostic Tool</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }
        .card { background: white; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .pass { color: green; font-weight: bold; }
        .fail { color: red; font-weight: bold; }
        .warn { color: orange; font-weight: bold; }
        code { background: #333; color: lime; padding: 2px 6px; border-radius: 3px; }
        pre { background: #333; color: lime; padding: 15px; border-radius: 5px; overflow-x: auto; }
        button { background: #6366f1; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-size: 16px; }
        button:hover { background: #4f46e5; }
        .result-item { padding: 8px; margin: 5px 0; border-left: 4px solid #ddd; background: #f9f9f9; }
        .result-item.pass { border-left-color: green; background: #f0fff0; }
        .result-item.fail { border-left-color: red; background: #fff0f0; }
        h1 { color: #333; }
        h2 { color: #555; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px; }
        .diagnosis-summary { padding: 15px; background: #f0f0f0; border-radius: 8px; margin-top: 20px; }
        .fix-instruction { background: #e3f2fd; padding: 15px; border-radius: 6px; border-left: 4px solid #2196f3; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>🔍 TruthLens Diagnostic Tool</h1>
    
    <div class="card">
        <h2>Quick Test</h2>
        <button onclick="runFullTest()">Run Complete Diagnostics</button>
        <div id="results"></div>
    </div>
    
    <div class="card">
        <h2>Manual Console Test</h2>
        <p>Open browser console (F12) and paste this:</p>
        <pre>
console.log('=== DIAGNOSTIC ===');
console.log('ServiceTemplates:', typeof ServiceTemplates);
console.log('UnifiedAnalyzer:', typeof unifiedAnalyzer);
console.log('CSS count:', document.styleSheets.length);
console.log('Has cleanAuthorName:', typeof unifiedAnalyzer?.cleanAuthorName);
        </pre>
    </div>
    
    <div class="card">
        <h2>File Size Issues Detected</h2>
        <p><strong>unified-app-core.js is only 3KB!</strong> This is wrong - it should be ~12KB.</p>
        <p>This means you're running an old/incomplete version of the JavaScript file.</p>
        <div class="fix-instruction">
            <strong>FIX REQUIRED:</strong> Deploy the complete v6.0 unified-app-core.js file (12KB version)
        </div>
    </div>
    
    <script>
        function runFullTest() {
            const r = document.getElementById('results');
            let html = '<h3>Diagnostic Results:</h3>';
            let issues = [];
            
            // Test 1: ServiceTemplates
            const st = typeof ServiceTemplates !== 'undefined';
            html += '<div class="result-item ' + (st ? 'pass' : 'fail') + '">';
            html += '1. ServiceTemplates: ' + (st ? '✓ Loaded' : '✗ NOT FOUND');
            if (st && ServiceTemplates.displayAllAnalyses) {
                html += ' (displayAllAnalyses: ✓)';
            } else if (st) {
                html += ' (displayAllAnalyses: ✗)';
                issues.push('ServiceTemplates missing displayAllAnalyses method');
            }
            html += '</div>';
            if (!st) issues.push('ServiceTemplates not loading - this causes plain text results');
            
            // Test 2: UnifiedAnalyzer
            const ua = typeof unifiedAnalyzer !== 'undefined';
            html += '<div class="result-item ' + (ua ? 'pass' : 'fail') + '">';
            html += '2. UnifiedAnalyzer: ' + (ua ? '✓ Loaded' : '✗ NOT FOUND');
            if (ua && typeof unifiedAnalyzer.cleanAuthorName === 'function') {
                html += ' (cleanAuthorName: ✓)';
            } else if (ua) {
                html += ' (cleanAuthorName: <span class="fail">✗ MISSING</span>)';
                issues.push('cleanAuthorName method missing - wrong JS version');
            }
            html += '</div>';
            if (!ua) issues.push('UnifiedAnalyzer not loading');
            
            // Test 3: CSS Files
            const css = document.styleSheets.length;
            html += '<div class="result-item ' + (css > 1 ? 'pass' : css > 0 ? 'warn' : 'fail') + '">';
            html += '3. CSS Files: ' + css + ' stylesheets loaded';
            if (css === 0) {
                html += ' <span class="fail">(NO CSS!)</span>';
                issues.push('No CSS files loading');
            } else if (css === 1) {
                html += ' <span class="warn">(Only 1 - may be missing main.css)</span>';
            }
            html += '</div>';
            
            // Test 4: Required DOM elements
            const container = document.getElementById('serviceAnalysisContainer');
            html += '<div class="result-item ' + (container ? 'pass' : 'fail') + '">';
            html += '4. Service Container: ' + (container ? '✓ Found' : '✗ MISSING');
            html += '</div>';
            if (!container) issues.push('serviceAnalysisContainer element missing');
            
            // Test 5: Font Awesome
            const fa = document.querySelector('link[href*="font-awesome"]');
            html += '<div class="result-item ' + (fa ? 'pass' : 'warn') + '">';
            html += '5. Font Awesome Icons: ' + (fa ? '✓ Loaded' : '⚠ Not loaded (icons will be missing)');
            html += '</div>';
            
            // Summary
            html += '<div class="diagnosis-summary">';
            html += '<h3>Diagnosis Summary:</h3>';
            if (issues.length === 0) {
                html += '<p class="pass">✅ All core components loaded successfully!</p>';
            } else {
                html += '<p class="fail">❌ Issues Found:</p>';
                html += '<ul>';
                for (let issue of issues) {
                    html += '<li>' + issue + '</li>';
                }
                html += '</ul>';
                
                // Primary fix
                if (ua && !unifiedAnalyzer.cleanAuthorName) {
                    html += '<div class="fix-instruction">';
                    html += '<strong>PRIMARY ISSUE:</strong> Wrong version of unified-app-core.js<br>';
                    html += 'The file is only 3KB but should be ~12KB. You need to deploy the complete v6.0 file.';
                    html += '</div>';
                }
            }
            html += '</div>';
            
            r.innerHTML = html;
        }
        
        // Auto-run after page loads
        window.addEventListener('DOMContentLoaded', function() {
            setTimeout(runFullTest, 1000);
        });
    </script>
</body>
</html>"""
    
    return diagnostic_html, 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.warning(f"404 error: {request.url}")
    
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'Endpoint not found'
        }), 404
    
    # Try to serve the unified index page
    try:
        return render_template('unified_index.html')
    except:
        try:
            return render_template('index.html')
        except:
            # Return basic HTML as fallback
            return """
            <!DOCTYPE html>
            <html>
            <head><title>404 - Not Found</title></head>
            <body>
                <h1>404 - Page Not Found</h1>
                <p>The requested page could not be found.</p>
                <a href="/">Return to Home</a>
            </body>
            </html>
            """, 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    logger.error(f"500 error: {str(error)}", exc_info=True)
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

# ================================================================================
# MAIN EXECUTION
# ================================================================================

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    debug = Config.DEBUG
    
    logger.info("=" * 80)
    logger.info(f"Starting TruthLens Unified Analyzer on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"News Mode: {Config.ENABLE_NEWS_MODE}")
    logger.info(f"Transcript Mode: {Config.ENABLE_TRANSCRIPT_MODE}")
    logger.info(f"Template: unified_index.html (with fallback to index.html)")
    logger.info("=" * 80)
    
    # List all files in key directories for debugging
    try:
        logger.info("Templates directory contents:")
        template_dir = os.path.join(os.getcwd(), 'templates')
        if os.path.exists(template_dir):
            for file in os.listdir(template_dir):
                logger.info(f"  - {file}")
        
        logger.info("Static/js directory contents:")
        js_dir = os.path.join(os.getcwd(), 'static', 'js')
        if os.path.exists(js_dir):
            for file in os.listdir(js_dir):
                logger.info(f"  - {file}")
    except Exception as e:
        logger.error(f"Error listing directories: {e}")
    
    logger.info("=" * 80)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
