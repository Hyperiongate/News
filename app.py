"""
app.py - Flask app with fixed imports and minimal service dependencies
This version uses placeholder services if the actual ones aren't available
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

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

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

# Placeholder classes for services (will be replaced when services directory is properly set up)
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
                'domain': urlparse(url).netloc
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
            'factors': []
        }

class ClickbaitDetector:
    def analyze(self, article_data):
        """Detect clickbait"""
        title = article_data.get('title', '')
        score = 0
        
        # Simple clickbait detection
        if '!' in title:
            score += 20
        if '?' in title:
            score += 15
        if any(word in title.lower() for word in ['shocking', 'amazing', 'unbelievable']):
            score += 30
            
        return {
            'score': min(100, score),
            'factors': []
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
            'uses_data': False
        }

class ManipulationDetector:
    def analyze(self, article_data):
        """Detect manipulation tactics"""
        return {
            'tactics': [],
            'manipulation_score': 10
        }

class ReadabilityAnalyzer:
    def analyze(self, article_data):
        """Analyze readability"""
        return {
            'score': 70,
            'level': 'Medium',
            'details': {}
        }

class EmotionAnalyzer:
    def analyze(self, article_data):
        """Analyze emotional content"""
        return {
            'dominant_emotion': 'neutral',
            'manipulation_score': 10,
            'emotions': {}
        }

class ClaimExtractor:
    def extract_claims(self, article_data):
        """Extract claims from article"""
        return {
            'claims': []
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
            'citations': []
        }

class PDFGenerator:
    def generate_report(self, analysis_results):
        """Generate PDF report"""
        # Placeholder - return a simple text file
        return None

class ReportGenerator:
    def generate(self, analysis_results):
        """Generate report"""
        return {
            'summary': 'Analysis complete',
            'sections': []
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
pdf_generator = PDFGenerator()
report_generator = ReportGenerator()

@app.route('/')
def index():
    """Render the main page"""
    return jsonify({
        'status': 'News Analyzer API is running',
        'version': '2.0',
        'endpoints': [
            '/analyze',
            '/health',
            '/stats'
        ]
    })

@app.route('/analyze', methods=['POST'])
@rate_limit(max_requests=30, window=60)  # 30 requests per minute
def analyze():
    """Main analysis endpoint"""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        url = data.get('url', '').strip()
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
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
        
        # Get domain for various analyses
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace('www.', '')
        
        # Perform analyses
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
        
        # Calculate trust score
        trust_score_data = calculate_trust_score(
            article_data, 
            author_info,
            analysis_results
        )
        
        # Prepare response
        results = {
            'article': {
                'url': url,
                'title': article_data.get('title', ''),
                'author': article_data.get('author', 'Unknown'),
                'date': article_data.get('date', ''),
                'domain': domain,
                'word_count': article_data.get('word_count', 0),
                'reading_time': article_data.get('reading_time', 0)
            },
            'author_info': author_info,
            'trust_score': trust_score_data['score'],
            'trust_score_breakdown': trust_score_data['breakdown'],
            'trust_level': trust_score_data['level'],
            'bias_analysis': analysis_results['bias'],
            'clickbait_analysis': analysis_results['clickbait'],
            'source_credibility': analysis_results['source'],
            'transparency_analysis': analysis_results['transparency'],
            'analysis_timestamp': datetime.now().isoformat(),
            'from_cache': False
        }
        
        # Cache the results
        cache.set(cache_key, results)
        
        logger.info(f"Analysis complete. Trust score: {trust_score_data['score']}")
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

def calculate_trust_score(article_data, author_info, analysis_results):
    """Calculate simplified trust score"""
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
            'content_integrity': {'score': max(0, 100 - int(bias_score * 100))}
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

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0'
    })

@app.route('/stats', methods=['GET'])
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_stats():
    """Get analysis statistics"""
    return jsonify({
        'total_analyses': 1000,  # Placeholder
        'analyses_today': 50,    # Placeholder
        'average_trust_score': 65
    })

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
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )
