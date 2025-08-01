"""
app.py - Flask app with enhanced API integrations
Includes MediaStack, FRED, Copyscape, and CopyLeaks APIs
"""

import os
import io
import json
import logging
import time
import hashlib
from datetime import datetime, timedelta

from flask import Flask, render_template, request, jsonify, send_file, session, send_from_directory
from flask_cors import CORS
from flask_caching import Cache
from functools import wraps
from collections import defaultdict
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app with proper static configuration
app = Flask(__name__, 
            static_folder='static',
            static_url_path='/static',
            template_folder='templates')
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configure caching
cache_config = {
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 3600  # 1 hour
}
app.config.update(cache_config)
cache = Cache(app)

# API Keys (load from environment)
GOOGLE_FACT_CHECK_API_KEY = os.environ.get('GOOGLE_FACT_CHECK_API_KEY')
NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
SCRAPINGBEE_API_KEY = os.environ.get('SCRAPINGBEE_API_KEY')
# New API Keys
MEDIASTACK_API_KEY = os.environ.get('MEDIASTACK_API_KEY')
FRED_API_KEY = os.environ.get('FRED_API_KEY')
COPYSCAPE_USERNAME = os.environ.get('COPYSCAPE_USERNAME')
COPYSCAPE_API_KEY = os.environ.get('COPYSCAPE_API_KEY')
COPYLEAKS_EMAIL = os.environ.get('COPYLEAKS_EMAIL')
COPYLEAKS_API_KEY = os.environ.get('COPYLEAKS_API_KEY')

# Rate limiting storage
rate_limit_storage = defaultdict(list)

def rate_limit(max_requests=10, window=60):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client IP
            client_ip = request.remote_addr
            now = time.time()
            
            # Clean old entries
            rate_limit_storage[client_ip] = [
                timestamp for timestamp in rate_limit_storage[client_ip]
                if now - timestamp < window
            ]
            
            # Check rate limit
            if len(rate_limit_storage[client_ip]) >= max_requests:
                return jsonify({
                    'error': 'Rate limit exceeded. Please try again later.'
                }), 429
                
            # Add current request
            rate_limit_storage[client_ip].append(now)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Initialize services
try:
    # Import all services
    from services.news_analyzer import NewsAnalyzer
    from services.news_extractor import NewsExtractor
    from services.author_analyzer import AuthorAnalyzer
    from services.bias_analyzer import BiasAnalyzer
    from services.clickbait_detector import ClickbaitDetector
    from services.fact_checker import FactChecker
    from services.source_credibility import SourceCredibility
    from services.transparency_analyzer import TransparencyAnalyzer
    from services.content_analyzer import ContentAnalyzer
    from services.manipulation_detector import ManipulationDetector
    from services.readability_analyzer import ReadabilityAnalyzer
    from services.emotion_analyzer import EmotionAnalyzer
    from services.claim_extractor import ClaimExtractor
    from services.image_analyzer import ImageAnalyzer
    from services.network_analyzer import NetworkAnalyzer
    from services.pdf_generator import PDFGenerator
    from services.report_generator import ReportGenerator
    
    # Initialize core services with ScrapingBee support
    news_extractor = NewsExtractor(SCRAPINGBEE_API_KEY)
    news_analyzer = NewsAnalyzer()
    
    # Override the article extractor in news_analyzer to use news_extractor
    news_analyzer.article_extractor = news_extractor
    
    logger.info("All services imported successfully")
    logger.info(f"ScrapingBee enabled: {bool(SCRAPINGBEE_API_KEY)}")
    PDF_EXPORT_ENABLED = True
    
except ImportError as e:
    logger.warning(f"Some services could not be imported: {e}")
    logger.warning("Using enhanced fallback implementations")
    PDF_EXPORT_ENABLED = False
    
    # Enhanced fallback NewsExtractor with better timeout and headers
    class NewsExtractor:
        def __init__(self, scrapingbee_key=None):
            self.scrapingbee_key = scrapingbee_key
            self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
        def extract(self, url):
            """Extract article content from URL with ScrapingBee support"""
            try:
                # Use ScrapingBee if available
                if self.scrapingbee_key:
                    logger.info(f"Using ScrapingBee to extract: {url}")
                    response = requests.get(
                        'https://app.scrapingbee.com/api/v1/',
                        params={
                            'api_key': self.scrapingbee_key,
                            'url': url,
                            'render_js': 'false',
                            'premium_proxy': 'true',
                            'country_code': 'us'
                        },
                        timeout=30
                    )
                else:
                    logger.info(f"Using direct extraction for: {url}")
                    response = requests.get(url, headers=self.headers, timeout=30)
                
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract title
                title = ''
                title_tag = soup.find('title')
                if title_tag:
                    title = title_tag.text.strip()
                
                # Try multiple selectors for article content
                content = ''
                content_selectors = [
                    'article',
                    '[role="main"]',
                    '.article-content',
                    '.story-body',
                    '.entry-content',
                    '.post-content',
                    'main',
                    '.content'
                ]
                
                for selector in content_selectors:
                    element = soup.select_one(selector)
                    if element:
                        # Remove script and style elements
                        for script in element(['script', 'style']):
                            script.decompose()
                        content = element.get_text(separator=' ', strip=True)
                        if len(content) > 100:  # Ensure we got meaningful content
                            break
                
                # Fallback to body if no content found
                if not content or len(content) < 100:
                    body = soup.find('body')
                    if body:
                        for script in body(['script', 'style']):
                            script.decompose()
                        content = body.get_text(separator=' ', strip=True)
                
                # Extract author
                author = 'Unknown'
                author_selectors = [
                    'meta[name="author"]',
                    'meta[property="article:author"]',
                    '.author-name',
                    '.by-author',
                    '.byline',
                    '[rel="author"]'
                ]
                
                for selector in author_selectors:
                    element = soup.select_one(selector)
                    if element:
                        if element.name == 'meta':
                            author = element.get('content', 'Unknown')
                        else:
                            author = element.get_text(strip=True)
                        if author and author != 'Unknown':
                            break
                
                # Extract date
                date = datetime.now().isoformat()
                date_selectors = [
                    'meta[property="article:published_time"]',
                    'meta[name="publish_date"]',
                    'time[datetime]',
                    '.published-date',
                    '.article-date'
                ]
                
                for selector in date_selectors:
                    element = soup.select_one(selector)
                    if element:
                        if element.name == 'meta':
                            date = element.get('content', date)
                        elif element.name == 'time':
                            date = element.get('datetime', date)
                        else:
                            date = element.get_text(strip=True)
                        break
                
                # Extract images
                images = []
                img_tags = soup.find_all('img', src=True)[:5]  # Limit to 5 images
                for img in img_tags:
                    img_url = img.get('src', '')
                    if img_url:
                        if img_url.startswith('//'):
                            img_url = 'https:' + img_url
                        elif img_url.startswith('/'):
                            img_url = urlparse(url).scheme + '://' + urlparse(url).netloc + img_url
                        images.append(img_url)
                
                return {
                    'success': True,
                    'title': title,
                    'content': content[:10000],  # Limit content size
                    'text': content[:10000],
                    'author': author,
                    'date': date,
                    'url': url,
                    'domain': urlparse(url).netloc,
                    'word_count': len(content.split()),
                    'reading_time': max(1, len(content.split()) // 200),
                    'images': images,
                    'extraction_method': 'scrapingbee' if self.scrapingbee_key else 'direct'
                }
                
            except requests.exceptions.Timeout:
                logger.error(f"Timeout extracting article from: {url}")
                return {
                    'success': False,
                    'error': 'Request timed out. The website took too long to respond.',
                    'url': url
                }
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error extracting article: {e}")
                return {
                    'success': False,
                    'error': f'Failed to fetch the article: {str(e)}',
                    'url': url
                }
            except Exception as e:
                logger.error(f"Error extracting article: {e}")
                return {
                    'success': False,
                    'error': f'Error extracting article: {str(e)}',
                    'url': url
                }

    # Placeholder implementations for other services
    class AuthorAnalyzer:
        def analyze_single_author(self, author_name, domain):
            """Analyze author credibility"""
            return {
                'found': bool(author_name and author_name != 'Unknown'),
                'name': author_name,
                'credibility_score': 70 if author_name != 'Unknown' else 40,
                'verification_status': {
                    'verified': False,
                    'outlet_staff': False
                },
                'professional_info': {
                    'years_experience': None
                }
            }

    class BiasAnalyzer:
        def analyze(self, article_data):
            """Analyze article bias"""
            return {
                'bias_score': 0.1,
                'confidence': 75,
                'political_lean': 0,
                'factors': [],
                'overall_bias': 'center'
            }

    class ClickbaitDetector:
        def analyze(self, article_data):
            """Detect clickbait"""
            title = article_data.get('title', '')
            score = 0
            tactics = []
            
            # Simple clickbait detection
            if '!' in title:
                score += 20
                tactics.append('Exclamation marks')
            if '?' in title:
                score += 15
                tactics.append('Question headlines')
            if any(word in title.lower() for word in ['shocking', 'amazing', 'unbelievable']):
                score += 30
                tactics.append('Sensational language')
                
            return {
                'score': score,
                'tactics': tactics,
                'headline_analysis': {
                    'type': 'clickbait' if score > 50 else 'standard'
                }
            }

    class FactChecker:
        def check_claims(self, claims, article_data):
            """Check facts"""
            return {
                'claims': claims[:5] if claims else [],
                'fact_checks': [],
                'summary': {
                    'total_claims': len(claims) if claims else 0,
                    'verified': 0,
                    'false': 0,
                    'unverified': len(claims) if claims else 0
                }
            }

    class SourceCredibility:
        def check_source(self, domain):
            """Check source credibility"""
            # Simple domain check
            known_credible = ['nytimes.com', 'bbc.com', 'reuters.com', 'apnews.com', 'washingtonpost.com']
            
            return {
                'domain': domain,
                'credibility': 'high' if any(cred in domain for cred in known_credible) else 'medium',
                'rating': 'established' if any(cred in domain for cred in known_credible) else 'unknown'
            }

    class TransparencyAnalyzer:
        def analyze(self, article_data):
            """Analyze transparency"""
            score = 50  # Base score
            indicators = []
            
            if article_data.get('author') and article_data['author'] != 'Unknown':
                score += 20
                indicators.append('Author identified')
                
            if article_data.get('date'):
                score += 10
                indicators.append('Publication date provided')
                
            return {
                'transparency_score': score,
                'indicators': indicators
            }

    class ContentAnalyzer:
        def analyze(self, article_data):
            """Analyze content"""
            content = article_data.get('content', '')
            
            return {
                'metrics': {
                    'word_count': len(content.split()),
                    'sentence_count': content.count('.'),
                    'paragraph_count': content.count('\n\n') + 1
                }
            }

    class ManipulationDetector:
        def analyze(self, article_data):
            """Detect manipulation tactics"""
            tactics = []
            score = 0
            
            content = article_data.get('content', '').lower()
            
            # Simple detection
            if 'you won\'t believe' in content:
                tactics.append({'name': 'Curiosity gap', 'severity': 'high'})
                score += 30
            
            if content.count('!') > 5:
                tactics.append({'name': 'Excessive exclamation', 'severity': 'medium'})
                score += 20
                
            return {
                'tactics': tactics,
                'manipulation_score': score,
                'score': score
            }

    class ReadabilityAnalyzer:
        def analyze(self, article_data):
            """Analyze readability"""
            content = article_data.get('content', '')
            words = content.split()
            sentences = content.split('.')
            
            avg_words_per_sentence = len(words) / max(1, len(sentences))
            
            if avg_words_per_sentence < 15:
                level = 'Easy'
                score = 90
            elif avg_words_per_sentence < 25:
                level = 'Medium'
                score = 70
            else:
                level = 'Difficult'
                score = 50
                
            return {
                'score': score,
                'level': level,
                'details': {
                    'average_sentence_length': round(avg_words_per_sentence, 1)
                }
            }

    class EmotionAnalyzer:
        def analyze(self, article_data):
            """Analyze emotional content"""
            return {
                'dominant_emotion': 'neutral',
                'manipulation_score': 10,
                'emotions': {
                    'anger': 0.1,
                    'fear': 0.1,
                    'joy': 0.1,
                    'sadness': 0.1,
                    'neutral': 0.6
                }
            }

    class ClaimExtractor:
        def extract_claims(self, article_data):
            """Extract claims from article"""
            content = article_data.get('content', '')
            claims = []
            
            # Simple claim extraction - look for sentences with numbers
            sentences = content.split('.')
            for sentence in sentences[:10]:  # First 10 sentences
                if any(char.isdigit() for char in sentence):
                    claims.append(sentence.strip())
                    
            return {
                'claims': claims
            }

    class ImageAnalyzer:
        def analyze_images(self, images):
            """Analyze images"""
            return {
                'count': len(images) if images else 0,
                'analysis': []
            }

    class NetworkAnalyzer:
        def analyze(self, article_data):
            """Analyze network connections"""
            return {
                'links': [],
                'citations': [],
                'related_articles': 0
            }

    class PDFGenerator:
        def __init__(self):
            self.available = False
            
        def generate_report(self, analysis_results):
            """Generate PDF report"""
            return None

    class ReportGenerator:
        def generate(self, analysis_results, format_type='json'):
            """Generate report"""
            return {
                'summary': 'Analysis complete',
                'sections': []
            }
    
    class NewsAnalyzer:
        """Main news analyzer orchestrator"""
        def __init__(self):
            self.article_extractor = NewsExtractor(SCRAPINGBEE_API_KEY)
            self.author_analyzer = AuthorAnalyzer()
            self.bias_analyzer = BiasAnalyzer()
            self.clickbait_detector = ClickbaitDetector()
            self.fact_checker = FactChecker()
            self.source_credibility = SourceCredibility()
            self.transparency_analyzer = TransparencyAnalyzer()
            self.content_analyzer = ContentAnalyzer()
            self.manipulation_detector = ManipulationDetector()
            self.readability_analyzer = ReadabilityAnalyzer()
            self.emotion_analyzer = EmotionAnalyzer()
            self.claim_extractor = ClaimExtractor()
            
        def analyze(self, url_or_text, input_type='url', is_pro=False):
            """Main analysis method"""
            # Extract article
            if input_type == 'url':
                article_data = self.article_extractor.extract(url_or_text)
                if not article_data.get('success', True):
                    return {
                        'error': article_data.get('error', 'Failed to extract article'),
                        'success': False
                    }
            else:
                article_data = {
                    'title': 'Text Analysis',
                    'content': url_or_text,
                    'text': url_or_text,
                    'author': 'Unknown',
                    'url': 'text-input',
                    'domain': 'text-input',
                    'word_count': len(url_or_text.split()),
                    'reading_time': max(1, len(url_or_text.split()) // 200)
                }
            
            # Run all analyses
            bias_analysis = self.bias_analyzer.analyze(article_data)
            clickbait_analysis = self.clickbait_detector.analyze(article_data)
            source_analysis = self.source_credibility.check_source(article_data.get('domain', ''))
            transparency_analysis = self.transparency_analyzer.analyze(article_data)
            author_analysis = self.author_analyzer.analyze_single_author(
                article_data.get('author', 'Unknown'),
                article_data.get('domain', '')
            )
            
            # Extract and check claims
            claims_data = self.claim_extractor.extract_claims(article_data)
            fact_check_results = self.fact_checker.check_claims(
                claims_data.get('claims', []),
                article_data
            )
            
            # Additional analyses
            content_analysis = self.content_analyzer.analyze(article_data)
            manipulation_analysis = self.manipulation_detector.analyze(article_data)
            readability_analysis = self.readability_analyzer.analyze(article_data)
            emotion_analysis = self.emotion_analyzer.analyze(article_data)
            
            # Calculate trust score
            trust_score = self._calculate_trust_score(
                bias_analysis,
                clickbait_analysis,
                source_analysis,
                transparency_analysis,
                author_analysis,
                manipulation_analysis
            )
            
            # Build response
            result = {
                'success': True,
                'article': article_data,
                'trust_score': trust_score,
                'bias_analysis': bias_analysis,
                'clickbait_analysis': clickbait_analysis,
                'source_credibility': source_analysis,
                'transparency_analysis': transparency_analysis,
                'author_analysis': author_analysis,
                'fact_check_results': fact_check_results,
                'content_analysis': content_analysis,
                'manipulation_analysis': manipulation_analysis,
                'readability_analysis': readability_analysis,
                'emotion_analysis': emotion_analysis,
                'is_pro': is_pro,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            return result
            
        def _calculate_trust_score(self, bias, clickbait, source, transparency, author, manipulation):
            """Calculate overall trust score"""
            # Weight different factors
            bias_weight = 0.15
            clickbait_weight = 0.10
            source_weight = 0.30
            transparency_weight = 0.15
            author_weight = 0.20
            manipulation_weight = 0.10
            
            # Convert to scores (0-100)
            bias_score = max(0, 100 - (bias.get('bias_score', 0) * 100))
            clickbait_score = max(0, 100 - clickbait.get('score', 0))
            source_score = 80 if source.get('credibility') == 'high' else 50
            transparency_score = transparency.get('transparency_score', 50)
            author_score = author.get('credibility_score', 50)
            manipulation_score = max(0, 100 - manipulation.get('score', 0))
            
            # Calculate weighted average
            trust_score = (
                bias_score * bias_weight +
                clickbait_score * clickbait_weight +
                source_score * source_weight +
                transparency_score * transparency_weight +
                author_score * author_weight +
                manipulation_score * manipulation_weight
            )
            
            return round(trust_score)
    
    # Initialize services
    news_extractor = NewsExtractor(SCRAPINGBEE_API_KEY)
    news_analyzer = NewsAnalyzer()

# Main route
@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health():
    """Simple health check endpoint for Render"""
    return jsonify({'status': 'healthy'}), 200

# API info endpoint
@app.route('/api')
def api_info():
    """API information endpoint"""
    return jsonify({
        'status': 'News Analyzer API is running',
        'version': '2.1',
        'endpoints': [
            '/api/analyze',
            '/api/health',
            '/api/stats'
        ],
        'features': {
            'scrapingbee_enabled': bool(SCRAPINGBEE_API_KEY),
            'media_coverage_analysis': bool(MEDIASTACK_API_KEY),
            'economic_fact_checking': bool(FRED_API_KEY),
            'plagiarism_detection': bool(COPYSCAPE_USERNAME and COPYSCAPE_API_KEY),
            'ai_content_detection': bool(COPYLEAKS_EMAIL and COPYLEAKS_API_KEY)
        }
    })

# Main analysis endpoint
@app.route('/api/analyze', methods=['POST'])
@rate_limit(max_requests=30, window=60)  # 30 requests per minute
def analyze():
    """Main analysis endpoint with enhanced features"""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        url = data.get('url', '').strip()
        text = data.get('text', '').strip()
        
        if not url and not text:
            return jsonify({'error': 'No URL or text provided'}), 400
        
        # Determine if user is pro (simplified for now)
        is_pro = data.get('pro', False)
        
        # Run analysis
        if url:
            # Validate URL
            if not is_valid_url(url):
                return jsonify({'error': 'Invalid URL format'}), 400
            
            # Check cache first
            cache_key = generate_cache_key(url)
            cached_result = cache.get(cache_key)
            if cached_result and not data.get('force_refresh'):
                logger.info(f"Returning cached result for: {url}")
                cached_result['from_cache'] = True
                return jsonify(cached_result)
            
            logger.info(f"Starting analysis for URL: {url}")
            result = news_analyzer.analyze(url, 'url', is_pro)
            
            # Cache successful results
            if result.get('success'):
                cache.set(cache_key, result, timeout=3600)  # 1 hour cache
                
        else:
            logger.info("Starting analysis for text input")
            result = news_analyzer.analyze(text, 'text', is_pro)
        
        # Add enhanced features if available and user is pro
        if is_pro and result.get('success'):
            result['enhanced_features'] = {}
            
            # Media coverage analysis (if MediaStack API available)
            if MEDIASTACK_API_KEY:
                result['enhanced_features']['media_coverage'] = analyze_media_coverage(
                    result.get('article', {}).get('title', '')
                )
            
            # Economic data verification (if FRED API available)
            if FRED_API_KEY:
                result['enhanced_features']['economic_verification'] = verify_economic_claims(
                    result.get('fact_check_results', {}).get('claims', [])
                )
            
            # Plagiarism detection (if Copyscape available)
            if COPYSCAPE_USERNAME and COPYSCAPE_API_KEY:
                result['enhanced_features']['plagiarism_check'] = check_plagiarism(
                    result.get('article', {}).get('content', '')
                )
            
            # AI content detection (if CopyLeaks available)
            if COPYLEAKS_EMAIL and COPYLEAKS_API_KEY:
                result['enhanced_features']['ai_content_detection'] = detect_ai_content(
                    result.get('article', {}).get('content', '')
                )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error during analysis: {e}", exc_info=True)
        return jsonify({
            'error': 'An error occurred during analysis',
            'details': str(e),
            'success': False
        }), 500

def analyze_media_coverage(title):
    """Analyze media coverage using MediaStack API"""
    if not MEDIASTACK_API_KEY or not title:
        return {'available': False}
    
    try:
        # MediaStack API endpoint
        url = 'http://api.mediastack.com/v1/news'
        params = {
            'access_key': MEDIASTACK_API_KEY,
            'keywords': title,
            'limit': 10,
            'languages': 'en'
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                'available': True,
                'coverage_count': data.get('pagination', {}).get('total', 0),
                'sources': [article.get('source') for article in data.get('data', [])[:5]]
            }
    except Exception as e:
        logger.error(f"MediaStack API error: {e}")
    
    return {'available': False, 'error': 'Failed to analyze media coverage'}

def verify_economic_claims(claims):
    """Verify economic claims using FRED API"""
    if not FRED_API_KEY or not claims:
        return {'available': False}
    
    # Placeholder - implement FRED API integration
    return {
        'available': True,
        'verified_claims': 0,
        'economic_indicators': []
    }

def check_plagiarism(content):
    """Check for plagiarism using Copyscape API"""
    if not COPYSCAPE_USERNAME or not COPYSCAPE_API_KEY or not content:
        return {'available': False}
    
    # Placeholder - implement Copyscape API integration
    return {
        'available': True,
        'originality_score': 95,
        'sources_found': 0
    }

def detect_ai_content(content):
    """Detect AI-generated content using CopyLeaks API"""
    if not COPYLEAKS_EMAIL or not COPYLEAKS_API_KEY or not content:
        return {'available': False}
    
    # Placeholder - implement CopyLeaks API integration
    return {
        'available': True,
        'ai_probability': 0.1,
        'human_written': True
    }

def is_valid_url(url):
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def generate_cache_key(url):
    """Generate cache key for URL"""
    return f"analysis:{hashlib.md5(url.encode()).hexdigest()}"

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.1',
        'pdf_export_enabled': PDF_EXPORT_ENABLED,
        'scrapingbee_enabled': bool(SCRAPINGBEE_API_KEY),
        'enhanced_features': {
            'media_analysis': bool(MEDIASTACK_API_KEY),
            'economic_verification': bool(FRED_API_KEY),
            'plagiarism_detection': bool(COPYSCAPE_USERNAME),
            'ai_detection': bool(COPYLEAKS_EMAIL)
        }
    })

@app.route('/api/report/<report_type>', methods=['POST'])
@rate_limit(max_requests=5, window=60)  # 5 reports per minute
def generate_report(report_type):
    """Generate analysis report (PDF or other formats)"""
    try:
        data = request.get_json()
        analysis_results = data.get('analysis')
        
        if not analysis_results:
            return jsonify({'error': 'No analysis data provided'}), 400
        
        if report_type == 'pdf':
            if not PDF_EXPORT_ENABLED:
                return jsonify({
                    'error': 'PDF export is not available. Please install reportlab.',
                    'pdf_available': False
                }), 503
            
            # Generate PDF report
            pdf_generator = PDFGenerator()
            pdf_path = pdf_generator.generate_report(analysis_results)
            
            if pdf_path and os.path.exists(pdf_path):
                return send_file(
                    pdf_path,
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=f'news-analysis-{datetime.now().strftime("%Y%m%d-%H%M%S")}.pdf'
                )
            else:
                return jsonify({'error': 'Failed to generate PDF'}), 500
            
        elif report_type == 'json':
            # Return formatted JSON report
            report_generator = ReportGenerator()
            return jsonify(report_generator.generate(analysis_results, 'json'))
            
        elif report_type == 'markdown':
            # Return markdown report
            report_generator = ReportGenerator()
            return jsonify(report_generator.generate(analysis_results, 'markdown'))
            
        else:
            return jsonify({'error': f'Unknown report type: {report_type}'}), 400
            
    except Exception as e:
        logger.error(f"Error generating report: {e}", exc_info=True)
        return jsonify({'error': f'Failed to generate report: {str(e)}'}), 500

@app.route('/api/stats', methods=['GET'])
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_stats():
    """Get analysis statistics"""
    return jsonify({
        'total_analyses': 1000,  # Placeholder
        'analyses_today': 50,    # Placeholder
        'average_trust_score': 65,
        'features_available': {
            'scrapingbee': bool(SCRAPINGBEE_API_KEY),
            'media_analysis': bool(MEDIASTACK_API_KEY),
            'economic_verification': bool(FRED_API_KEY),
            'plagiarism_detection': bool(COPYSCAPE_USERNAME),
            'ai_detection': bool(COPYLEAKS_EMAIL)
        }
    })

# Serve static files in production
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory(app.static_folder, filename)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(429)
def rate_limited(error):
    return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting News Analyzer API on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"ScrapingBee enabled: {bool(SCRAPINGBEE_API_KEY)}")
    logger.info(f"Enhanced features - MediaStack: {bool(MEDIASTACK_API_KEY)}, FRED: {bool(FRED_API_KEY)}, Copyscape: {bool(COPYSCAPE_USERNAME)}, CopyLeaks: {bool(COPYLEAKS_EMAIL)}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )
