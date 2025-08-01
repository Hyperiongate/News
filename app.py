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

# Import services with fallback to placeholders
try:
    from services.article_extractor import ArticleExtractor
    from services.author_analyzer import AuthorAnalyzer
    from services.bias_analyzer import BiasAnalyzer
    from services.clickbait_detector import ClickbaitDetector
    from services.fact_checker import FactChecker
    from services.source_credibility import SourceCredibilityAnalyzer
    from services.transparency_analyzer import TransparencyAnalyzer
    from services.content_analyzer import ContentAnalyzer
    from services.manipulation_detector import ManipulationDetector
    from services.readability_analyzer import ReadabilityAnalyzer
    from services.emotion_analyzer import EmotionAnalyzer
    from services.claim_extractor import ClaimExtractor
    from services.image_analyzer import ImageAnalyzer
    from services.network_analyzer import NetworkAnalyzer
    from services.report_generator import ReportGenerator
    # Import new services
    from services.enhanced_context_analyzer import EnhancedContextAnalyzer
    from services.economic_fact_checker import EconomicFactChecker
    from services.originality_analyzer import OriginalityAnalyzer
except ImportError as e:
    logger.warning(f"Using placeholder services due to import error: {e}")
    
    # Placeholder classes for services
    class ArticleExtractor:
        def extract(self, url):
            """Extract article content from URL"""
            try:
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract title
                title = soup.find('title').text if soup.find('title') else 'Unknown Title'
                
                # Extract content (simplified)
                paragraphs = soup.find_all('p')
                content = ' '.join([p.text.strip() for p in paragraphs if p.text.strip()])
                
                # Extract author (basic)
                author = 'Unknown'
                author_meta = soup.find('meta', {'name': 'author'})
                if author_meta:
                    author = author_meta.get('content', 'Unknown')
                
                return {
                    'title': title,
                    'content': content[:5000],  # Limit content
                    'author': author,
                    'url': url,
                    'word_count': len(content.split()),
                    'reading_time': max(1, len(content.split()) // 200),
                    'date': datetime.now().isoformat(),
                    'domain': urlparse(url).netloc,
                    'text': content  # Add text field for compatibility
                }
            except Exception as e:
                logger.error(f"Error extracting article: {e}")
                return {'error': str(e)}

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
                tactics.append('Question in headline')
            if any(word in title.lower() for word in ['shocking', 'amazing', 'unbelievable']):
                score += 30
                tactics.append('Sensational language')
                
            return {
                'score': min(100, score),
                'factors': [],
                'tactics': tactics
            }

    class FactChecker:
        def check_article(self, article_data):
            """Check facts in article"""
            return {
                'claims': [],
                'summary': {
                    'total_claims': 0,
                    'verified': 0,
                    'unverified': 0
                }
            }

    class SourceCredibilityAnalyzer:
        def analyze_source(self, domain):
            """Analyze source credibility"""
            # Simple domain-based credibility
            high_cred_domains = ['reuters.com', 'bbc.com', 'npr.org', 'apnews.com']
            medium_cred_domains = ['cnn.com', 'foxnews.com', 'msnbc.com']
            
            if domain in high_cred_domains:
                return {'credibility': 'high', 'factual_reporting': 'Very High'}
            elif domain in medium_cred_domains:
                return {'credibility': 'medium', 'factual_reporting': 'Mixed'}
            else:
                return {'credibility': 'unknown', 'factual_reporting': 'Unknown'}

    class TransparencyAnalyzer:
        def analyze(self, article_data):
            """Analyze transparency"""
            score = 0
            factors = {}
            
            if article_data.get('author') and article_data['author'] != 'Unknown':
                score += 25
                factors['has_author'] = True
            
            if article_data.get('date'):
                score += 25
                factors['has_date'] = True
                
            return {
                'score': score,
                'factors': factors
            }

    class ContentAnalyzer:
        def analyze(self, article_data):
            """Analyze content quality"""
            return {
                'quality_score': 60,
                'has_sources': False,
                'uses_data': False,
                'word_count': article_data.get('word_count', 0),
                'sentence_count': len(article_data.get('content', '').split('.')),
                'paragraph_count': article_data.get('content', '').count('\n\n') + 1
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
    
    # Placeholder new services if not available
    class EnhancedContextAnalyzer:
        def analyze(self, article_data):
            """Enhanced context analysis placeholder"""
            return {
                'related_articles_count': 0,
                'related_articles': [],
                'coverage_analysis': {},
                'media_consensus': {'consensus_level': 'unknown', 'agreement_score': 0},
                'first_reported': None,
                'breaking_news_verified': False,
                'story_timeline': [],
                'geographic_spread': {},
                'source_diversity': {'unique_sources': 0}
            }
    
    class EconomicFactChecker:
        def verify_economic_claims(self, claims):
            """Economic fact checking placeholder"""
            return []
    
    class OriginalityAnalyzer:
        def analyze_originality(self, article_data):
            """Originality analysis placeholder"""
            return {
                'originality_score': 100,
                'plagiarism_detected': False,
                'ai_content_detected': False,
                'duplicate_sources': [],
                'ai_probability': 0,
                'originality_issues': [],
                'recommendations': []
            }

# Initialize analyzers
article_extractor = ArticleExtractor()
author_analyzer = AuthorAnalyzer()
bias_analyzer = BiasAnalyzer()
clickbait_detector = ClickbaitDetector()
fact_checker = FactChecker()
source_analyzer = SourceCredibilityAnalyzer()
transparency_analyzer = TransparencyAnalyzer()
content_analyzer = ContentAnalyzer()
manipulation_detector = ManipulationDetector()
readability_analyzer = ReadabilityAnalyzer()
emotion_analyzer = EmotionAnalyzer()
claim_extractor = ClaimExtractor()
image_analyzer = ImageAnalyzer()
network_analyzer = NetworkAnalyzer()
report_generator = ReportGenerator()

# Initialize new analyzers
enhanced_context_analyzer = EnhancedContextAnalyzer()
economic_fact_checker = EconomicFactChecker()
originality_analyzer = OriginalityAnalyzer()

# PDF Generator with proper error handling
PDF_EXPORT_ENABLED = False
pdf_generator = None

try:
    from services.pdf_generator import PDFGenerator
    pdf_generator = PDFGenerator()
    if pdf_generator.available:
        PDF_EXPORT_ENABLED = True
        logger.info("PDF export enabled")
    else:
        logger.warning("PDFGenerator initialized but reportlab not available")
except Exception as e:
    logger.warning(f"PDF export disabled: {e}")
    pdf_generator = PDFGenerator()

# Main route
@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

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
            
            # Extract article content
            article_data = article_extractor.extract(url)
            
            if not article_data or article_data.get('error'):
                error_msg = article_data.get('error') if article_data else 'Failed to extract article'
                logger.error(f"Article extraction failed: {error_msg}")
                return jsonify({'error': f'Failed to extract article: {error_msg}'}), 400
        else:
            # Handle text input
            article_data = {
                'title': 'Text Analysis',
                'content': text,
                'text': text,
                'author': 'Unknown',
                'url': 'text-input',
                'word_count': len(text.split()),
                'reading_time': max(1, len(text.split()) // 200),
                'date': datetime.now().isoformat(),
                'domain': 'text-input'
            }
        
        # Get domain for various analyses
        if url:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.replace('www.', '')
        else:
            domain = 'text-input'
        
        # Perform standard analyses
        author_info = author_analyzer.analyze_single_author(
            article_data.get('author', ''),
            domain
        )
        
        analysis_results = {
            'bias': bias_analyzer.analyze(article_data),
            'clickbait': clickbait_detector.analyze(article_data),
            'facts': fact_checker.check_article(article_data),
            'source': source_analyzer.analyze_source(domain),
            'transparency': transparency_analyzer.analyze(article_data),
            'content': content_analyzer.analyze(article_data),
            'manipulation': manipulation_detector.analyze(article_data),
            'readability': readability_analyzer.analyze(article_data),
            'emotion': emotion_analyzer.analyze(article_data),
            'claims': claim_extractor.extract_claims(article_data),
            'network': network_analyzer.analyze(article_data)
        }
        
        if article_data.get('images'):
            analysis_results['images'] = image_analyzer.analyze_images(article_data['images'])
        
        # NEW: Enhanced analyses with new APIs
        
        # Enhanced context analysis with MediaStack
        if MEDIASTACK_API_KEY:
            logger.info("Performing enhanced context analysis with MediaStack")
            enhanced_context = enhanced_context_analyzer.analyze(article_data)
        else:
            enhanced_context = {
                'related_articles_count': 0,
                'media_consensus': {'consensus_level': 'unavailable'},
                'api_available': False
            }
        
        # Economic fact checking with FRED
        economic_facts = []
        if FRED_API_KEY and analysis_results['claims'].get('claims'):
            logger.info("Performing economic fact checking with FRED")
            economic_facts = economic_fact_checker.verify_economic_claims(
                analysis_results['claims'].get('claims', [])
            )
        
        # Originality analysis with Copyscape & CopyLeaks
        if COPYSCAPE_USERNAME or COPYLEAKS_EMAIL:
            logger.info("Performing originality analysis")
            originality_results = originality_analyzer.analyze_originality(article_data)
        else:
            originality_results = {
                'originality_score': 100,
                'api_available': False
            }
        
        # Calculate trust score
        trust_score_data = calculate_trust_score(
            article_data, 
            author_info,
            analysis_results,
            originality_results
        )
        
        # Prepare response with enhanced data
        results = {
            'success': True,
            'article': {
                'url': article_data.get('url', 'text-input'),
                'title': article_data.get('title', ''),
                'author': article_data.get('author', 'Unknown'),
                'date': article_data.get('date', ''),
                'domain': domain,
                'word_count': article_data.get('word_count', 0),
                'reading_time': article_data.get('reading_time', 0),
                'content': article_data.get('content', '')  # Include content for frontend
            },
            'author_analysis': author_info,
            'trust_score': trust_score_data['score'],
            'trust_score_breakdown': trust_score_data['breakdown'],
            'trust_level': trust_score_data['level'],
            'bias_analysis': analysis_results['bias'],
            'clickbait_score': analysis_results['clickbait']['score'],
            'clickbait_analysis': analysis_results['clickbait'],
            'source_credibility': analysis_results['source'],
            'transparency_analysis': analysis_results['transparency'],
            'fact_checks': analysis_results['facts'],
            'content_analysis': analysis_results['content'],
            'manipulation_analysis': analysis_results['manipulation'],
            'readability_analysis': analysis_results['readability'],
            'emotion_analysis': analysis_results['emotion'],
            'key_claims': analysis_results['claims'].get('claims', []),
            'network_analysis': analysis_results['network'],
            # NEW: Enhanced analysis results
            'enhanced_context': enhanced_context,
            'economic_verification': economic_facts,
            'originality_analysis': originality_results,
            'media_coverage': enhanced_context.get('related_articles', [])[:10],  # Top 10
            'coverage_consensus': enhanced_context.get('media_consensus', {}),
            # Metadata
            'analysis_timestamp': datetime.now().isoformat(),
            'from_cache': False,
            'api_features': {
                'media_analysis': bool(MEDIASTACK_API_KEY),
                'economic_checking': bool(FRED_API_KEY),
                'plagiarism_detection': bool(COPYSCAPE_USERNAME or COPYLEAKS_EMAIL)
            }
        }
        
        # Cache the results if URL
        if url:
            cache.set(cache_key, results)
        
        logger.info(f"Analysis complete. Trust score: {trust_score_data['score']}")
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500

def calculate_trust_score(article_data, author_info, analysis_results, originality_results):
    """Calculate enhanced trust score including originality"""
    score = 50  # Base score
    
    # Author credibility
    if author_info.get('found'):
        score += 10
    
    # Source credibility
    if analysis_results['source'].get('credibility') == 'high':
        score += 20
    elif analysis_results['source'].get('credibility') == 'medium':
        score += 10
    
    # Bias penalty
    bias_score = abs(analysis_results['bias'].get('bias_score', 0))
    score -= int(bias_score * 20)
    
    # Clickbait penalty
    clickbait_score = analysis_results['clickbait'].get('score', 0)
    score -= int(clickbait_score / 5)
    
    # NEW: Originality bonus/penalty
    originality_score = originality_results.get('originality_score', 100)
    if originality_score < 50:
        score -= 20  # Heavy penalty for plagiarism
    elif originality_score < 80:
        score -= 10
    
    # AI content penalty
    if originality_results.get('ai_content_detected'):
        score -= 15
    
    # Ensure score is between 0 and 100
    score = max(0, min(100, score))
    
    # Determine trust level
    if score >= 80:
        level = 'Excellent'
    elif score >= 60:
        level = 'Good'
    elif score >= 40:
        level = 'Fair'
    else:
        level = 'Poor'
    
    return {
        'score': score,
        'level': level,
        'breakdown': {
            'author_credibility': {'score': author_info.get('credibility_score', 50)},
            'source_quality': {'score': 70 if analysis_results['source'].get('credibility') == 'high' else 50},
            'content_integrity': {'score': max(0, 100 - int(bias_score * 100))},
            'originality': {'score': originality_score}
        }
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
            return jsonify(report_generator.generate(analysis_results, 'json'))
            
        elif report_type == 'markdown':
            # Return markdown report
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
    logger.info(f"Enhanced features - MediaStack: {bool(MEDIASTACK_API_KEY)}, FRED: {bool(FRED_API_KEY)}, Copyscape: {bool(COPYSCAPE_USERNAME)}, CopyLeaks: {bool(COPYLEAKS_EMAIL)}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )
