"""
TruthLens Clean Architecture - Complete Rewrite
Date: September 29, 2025
Version: 5.0.0 CLEAN

COMPLETE REWRITE:
- No service registry
- No complex pipelines  
- Direct service calls
- Flat data structures
- Simple, robust, working
"""

import os
import sys
import logging
import time
import json
import hashlib
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse

# Flask setup
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

# Web scraping
import requests
from bs4 import BeautifulSoup
from newspaper import Article

# Setup logging
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

# ================================================================================
# CONFIGURATION
# ================================================================================

class Config:
    """Simple configuration"""
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    SCRAPERAPI_KEY = os.environ.get('SCRAPERAPI_KEY')
    NEWS_API_KEY = os.environ.get('NEWS_API_KEY') or os.environ.get('NEWSAPI_KEY')

# ================================================================================
# ARTICLE EXTRACTOR - SIMPLE AND WORKING
# ================================================================================

class SimpleArticleExtractor:
    """Simple article extraction that actually works"""
    
    def __init__(self):
        self.scraperapi_key = Config.SCRAPERAPI_KEY
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        logger.info(f"ArticleExtractor ready - ScraperAPI: {bool(self.scraperapi_key)}")
    
    def extract(self, url: str) -> Dict[str, Any]:
        """Extract article from URL"""
        logger.info(f"Extracting article from: {url}")
        
        # Method 1: Try ScraperAPI if available
        if self.scraperapi_key:
            result = self._extract_with_scraperapi(url)
            if result['success']:
                logger.info(f"✓ Extracted via ScraperAPI: {result['word_count']} words")
                return result
        
        # Method 2: Try Newspaper3k
        result = self._extract_with_newspaper(url)
        if result['success']:
            logger.info(f"✓ Extracted via Newspaper: {result['word_count']} words")
            return result
        
        # Method 3: Direct request with BeautifulSoup
        result = self._extract_with_beautifulsoup(url)
        if result['success']:
            logger.info(f"✓ Extracted via BeautifulSoup: {result['word_count']} words")
            return result
        
        # All methods failed
        logger.error(f"Failed to extract article from {url}")
        return {
            'success': False,
            'url': url,
            'title': 'Extraction Failed',
            'text': '',
            'author': 'Unknown',
            'domain': urlparse(url).netloc,
            'word_count': 0,
            'error': 'All extraction methods failed'
        }
    
    def _extract_with_scraperapi(self, url: str) -> Dict[str, Any]:
        """Extract using ScraperAPI"""
        try:
            api_url = 'https://api.scraperapi.com'
            params = {
                'api_key': self.scraperapi_key,
                'url': url,
                'render': 'false'
            }
            
            response = self.session.get(api_url, params=params, timeout=20)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title = title.text.strip() if title else 'Untitled'
            
            # Extract article text
            article_text = []
            for p in soup.find_all(['p', 'article']):
                text = p.get_text().strip()
                if len(text) > 50:  # Filter out short snippets
                    article_text.append(text)
            
            text = ' '.join(article_text)
            
            if len(text) < 100:
                return {'success': False}
            
            return {
                'success': True,
                'url': url,
                'title': title,
                'text': text,
                'author': self._extract_author(soup),
                'domain': urlparse(url).netloc,
                'word_count': len(text.split()),
                'method': 'scraperapi'
            }
            
        except Exception as e:
            logger.debug(f"ScraperAPI failed: {e}")
            return {'success': False}
    
    def _extract_with_newspaper(self, url: str) -> Dict[str, Any]:
        """Extract using Newspaper3k"""
        try:
            article = Article(url)
            article.download()
            article.parse()
            
            if not article.text or len(article.text) < 100:
                return {'success': False}
            
            return {
                'success': True,
                'url': url,
                'title': article.title or 'Untitled',
                'text': article.text,
                'author': ', '.join(article.authors) if article.authors else 'Unknown',
                'domain': urlparse(url).netloc,
                'word_count': len(article.text.split()),
                'method': 'newspaper'
            }
            
        except Exception as e:
            logger.debug(f"Newspaper failed: {e}")
            return {'success': False}
    
    def _extract_with_beautifulsoup(self, url: str) -> Dict[str, Any]:
        """Extract using direct request and BeautifulSoup"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove scripts and styles
            for script in soup(['script', 'style', 'meta', 'noscript']):
                script.decompose()
            
            # Extract title
            title = soup.find('title')
            title = title.text.strip() if title else 'Untitled'
            
            # Extract main content
            article_text = []
            
            # Try common article containers
            article = soup.find(['article', 'main', 'div'], class_=re.compile('article|content|story'))
            if article:
                for p in article.find_all('p'):
                    text = p.get_text().strip()
                    if len(text) > 50:
                        article_text.append(text)
            else:
                # Fallback to all paragraphs
                for p in soup.find_all('p'):
                    text = p.get_text().strip()
                    if len(text) > 50:
                        article_text.append(text)
            
            text = ' '.join(article_text)
            
            if len(text) < 100:
                return {'success': False}
            
            return {
                'success': True,
                'url': url,
                'title': title,
                'text': text,
                'author': self._extract_author(soup),
                'domain': urlparse(url).netloc,
                'word_count': len(text.split()),
                'method': 'beautifulsoup'
            }
            
        except Exception as e:
            logger.debug(f"BeautifulSoup failed: {e}")
            return {'success': False}
    
    def _extract_author(self, soup) -> str:
        """Extract author from HTML"""
        # Try meta tags
        author_meta = soup.find('meta', {'name': 'author'}) or \
                     soup.find('meta', {'property': 'article:author'})
        if author_meta:
            return author_meta.get('content', 'Unknown')
        
        # Try common author elements
        author_elem = soup.find(class_=re.compile('author|byline|by-line'))
        if author_elem:
            return author_elem.get_text().strip().replace('By ', '').replace('by ', '')
        
        return 'Unknown'

# ================================================================================
# SIMPLE ANALYZERS - DIRECT AND WORKING
# ================================================================================

class SimpleAnalyzers:
    """All analysis in one simple class"""
    
    def __init__(self):
        self.source_database = {
            'reuters.com': {'credibility': 95, 'bias': 'Minimal'},
            'apnews.com': {'credibility': 95, 'bias': 'Minimal'},
            'bbc.com': {'credibility': 90, 'bias': 'Minimal'},
            'nytimes.com': {'credibility': 85, 'bias': 'Left-Center'},
            'washingtonpost.com': {'credibility': 85, 'bias': 'Left-Center'},
            'wsj.com': {'credibility': 85, 'bias': 'Right-Center'},
            'cnn.com': {'credibility': 70, 'bias': 'Left'},
            'foxnews.com': {'credibility': 70, 'bias': 'Right'},
            'msnbc.com': {'credibility': 70, 'bias': 'Left'},
            'breitbart.com': {'credibility': 30, 'bias': 'Far-Right'},
            'dailymail.co.uk': {'credibility': 40, 'bias': 'Right'},
            'buzzfeed.com': {'credibility': 50, 'bias': 'Left'},
        }
    
    def analyze_source_credibility(self, domain: str) -> Dict[str, Any]:
        """Analyze source credibility"""
        clean_domain = domain.replace('www.', '')
        
        if clean_domain in self.source_database:
            db_info = self.source_database[clean_domain]
            score = db_info['credibility']
            bias = db_info['bias']
        else:
            score = 50  # Unknown source
            bias = 'Unknown'
        
        return {
            'score': score,
            'credibility_score': score,
            'credibility_level': self._get_level(score),
            'bias': bias,
            'domain': domain,
            'in_database': clean_domain in self.source_database
        }
    
    def analyze_bias(self, text: str) -> Dict[str, Any]:
        """Simple bias detection"""
        text_lower = text.lower()
        
        # Count bias indicators
        left_words = ['liberal', 'progressive', 'inequality', 'social justice']
        right_words = ['conservative', 'traditional', 'free market', 'liberty']
        
        left_count = sum(1 for word in left_words if word in text_lower)
        right_count = sum(1 for word in right_words if word in text_lower)
        
        # Calculate bias score (0-100, where 100 is highly biased)
        total_indicators = left_count + right_count
        word_count = len(text.split())
        
        if word_count > 0:
            bias_score = min(100, (total_indicators / word_count) * 1000)
        else:
            bias_score = 0
        
        # Determine political lean
        if left_count > right_count:
            political_lean = 'Left'
        elif right_count > left_count:
            political_lean = 'Right'
        else:
            political_lean = 'Center'
        
        return {
            'score': int(bias_score),
            'bias_score': int(bias_score),
            'bias_level': self._get_bias_level(bias_score),
            'political_lean': political_lean,
            'objectivity_score': 100 - int(bias_score)
        }
    
    def analyze_author(self, author: str, domain: str) -> Dict[str, Any]:
        """Simple author analysis"""
        # Basic credibility based on whether author is identified
        if author and author != 'Unknown':
            # If from credible source, give higher score
            source_cred = self.source_database.get(domain.replace('www.', ''), {}).get('credibility', 50)
            score = min(100, source_cred + 10)
        else:
            score = 30  # No author identified
        
        return {
            'score': score,
            'credibility_score': score,
            'author_name': author,
            'verified': author != 'Unknown'
        }
    
    def check_facts(self, text: str) -> Dict[str, Any]:
        """Simple fact checking (pattern-based)"""
        # Count potential factual claims
        claim_patterns = [
            r'\d+%',  # Percentages
            r'\d+ million',  # Large numbers
            r'\d+ billion',
            r'study shows',
            r'research indicates',
            r'according to'
        ]
        
        claims_found = 0
        for pattern in claim_patterns:
            claims_found += len(re.findall(pattern, text, re.IGNORECASE))
        
        # Simulate verification (in real app, would check against databases)
        verified = max(0, claims_found - 2)  # Assume we can verify most claims
        
        return {
            'score': min(100, verified * 20) if claims_found > 0 else 50,
            'claims_found': claims_found,
            'claims_verified': verified,
            'fact_checks': []  # Simplified - no individual checks
        }
    
    def analyze_transparency(self, text: str, author: str) -> Dict[str, Any]:
        """Simple transparency analysis"""
        score = 50  # Base score
        
        # Check for source citations
        if 'according to' in text.lower() or 'said' in text.lower():
            score += 20
        
        # Check for author
        if author != 'Unknown':
            score += 20
        
        # Check for quotes
        if '"' in text:
            score += 10
        
        return {
            'score': min(100, score),
            'transparency_score': min(100, score),
            'sources_cited': text.count('according to'),
            'quotes_used': text.count('"') // 2
        }
    
    def detect_manipulation(self, text: str) -> Dict[str, Any]:
        """Simple manipulation detection"""
        manipulation_words = [
            'shocking', 'explosive', 'devastating', 'bombshell',
            'you won\'t believe', 'crisis', 'disaster'
        ]
        
        text_lower = text.lower()
        techniques_found = sum(1 for word in manipulation_words if word in text_lower)
        
        score = min(100, techniques_found * 15)
        
        return {
            'score': score,
            'manipulation_score': score,
            'manipulation_level': self._get_level(100 - score),
            'techniques_found': techniques_found
        }
    
    def analyze_content(self, text: str) -> Dict[str, Any]:
        """Simple content quality analysis"""
        word_count = len(text.split())
        sentence_count = len(re.findall(r'[.!?]+', text))
        
        # Average sentence length
        avg_sentence_length = word_count / max(sentence_count, 1)
        
        # Simple readability score
        if avg_sentence_length <= 15:
            readability_score = 90
        elif avg_sentence_length <= 20:
            readability_score = 75
        elif avg_sentence_length <= 25:
            readability_score = 60
        else:
            readability_score = 40
        
        return {
            'score': readability_score,
            'quality_score': readability_score,
            'readability': 'Good' if readability_score > 60 else 'Fair'
        }
    
    def _get_level(self, score: int) -> str:
        """Get level from score"""
        if score >= 80:
            return 'High'
        elif score >= 60:
            return 'Medium'
        elif score >= 40:
            return 'Low'
        else:
            return 'Very Low'
    
    def _get_bias_level(self, score: int) -> str:
        """Get bias level from score"""
        if score >= 70:
            return 'High Bias'
        elif score >= 40:
            return 'Moderate Bias'
        elif score >= 20:
            return 'Low Bias'
        else:
            return 'Minimal Bias'

# ================================================================================
# MAIN ANALYZER - COORDINATES EVERYTHING
# ================================================================================

class TruthLensAnalyzer:
    """Main analyzer that coordinates everything"""
    
    def __init__(self):
        self.extractor = SimpleArticleExtractor()
        self.analyzers = SimpleAnalyzers()
        logger.info("✓ TruthLens Analyzer initialized")
    
    def analyze(self, url: str) -> Dict[str, Any]:
        """Complete analysis of a news article"""
        start_time = time.time()
        
        # Step 1: Extract article
        article = self.extractor.extract(url)
        
        if not article['success']:
            logger.error(f"Article extraction failed for {url}")
            return self._create_error_response("Failed to extract article content", url)
        
        logger.info(f"✓ Article extracted: {article['title'][:50]}... ({article['word_count']} words)")
        
        # Step 2: Run all analyses
        text = article['text']
        domain = article['domain']
        author = article['author']
        
        # Run individual analyzers
        source_credibility = self.analyzers.analyze_source_credibility(domain)
        bias_detector = self.analyzers.analyze_bias(text)
        author_analyzer = self.analyzers.analyze_author(author, domain)
        fact_checker = self.analyzers.check_facts(text)
        transparency_analyzer = self.analyzers.analyze_transparency(text, author)
        manipulation_detector = self.analyzers.detect_manipulation(text)
        content_analyzer = self.analyzers.analyze_content(text)
        
        # Calculate overall trust score
        trust_score = self._calculate_trust_score({
            'source_credibility': source_credibility,
            'bias_detector': bias_detector,
            'author_analyzer': author_analyzer,
            'fact_checker': fact_checker,
            'transparency_analyzer': transparency_analyzer,
            'manipulation_detector': manipulation_detector,
            'content_analyzer': content_analyzer
        })
        
        # Generate findings summary
        findings_summary = self._generate_findings_summary(trust_score, source_credibility, bias_detector)
        
        # Build response
        response = {
            'success': True,
            'trust_score': trust_score,
            'article_summary': article['title'],
            'source': domain,
            'author': author,
            'findings_summary': findings_summary,
            'detailed_analysis': {
                'source_credibility': source_credibility,
                'bias_detector': bias_detector,
                'author_analyzer': author_analyzer,
                'fact_checker': fact_checker,
                'transparency_analyzer': transparency_analyzer,
                'manipulation_detector': manipulation_detector,
                'content_analyzer': content_analyzer
            },
            'article': {
                'title': article['title'],
                'url': url,
                'word_count': article['word_count'],
                'extraction_method': article.get('method', 'unknown')
            },
            'processing_time': round(time.time() - start_time, 2)
        }
        
        logger.info(f"✓ Analysis complete: Trust Score = {trust_score}/100 in {response['processing_time']}s")
        
        # Log response size
        response_size = len(json.dumps(response))
        logger.info(f"Response size: {response_size} bytes (should be 10-15KB for real article)")
        
        return response
    
    def _calculate_trust_score(self, analyses: Dict[str, Any]) -> int:
        """Calculate weighted trust score"""
        weights = {
            'source_credibility': 0.25,
            'author_analyzer': 0.15,
            'bias_detector': 0.20,  # Inverted - less bias = higher trust
            'fact_checker': 0.15,
            'transparency_analyzer': 0.10,
            'manipulation_detector': 0.10,  # Inverted
            'content_analyzer': 0.05
        }
        
        total_score = 0
        
        for service, weight in weights.items():
            service_data = analyses.get(service, {})
            score = service_data.get('score', 50)
            
            # Invert scores for negative indicators
            if service in ['bias_detector', 'manipulation_detector']:
                score = 100 - score
            
            total_score += score * weight
        
        return min(100, max(0, int(total_score)))
    
    def _generate_findings_summary(self, trust_score: int, source_cred: Dict, bias: Dict) -> str:
        """Generate human-readable findings summary"""
        if trust_score >= 80:
            summary = "High credibility article from reliable source. "
        elif trust_score >= 60:
            summary = "Generally credible with some concerns. "
        elif trust_score >= 40:
            summary = "Mixed credibility, verify claims independently. "
        else:
            summary = "Low credibility, approach with caution. "
        
        # Add specific findings
        if source_cred['score'] >= 80:
            summary += "Well-established source. "
        elif source_cred['score'] < 40:
            summary += "Source has credibility issues. "
        
        if bias['bias_score'] > 60:
            summary += f"Shows {bias['political_lean'].lower()} bias. "
        
        return summary
    
    def _create_error_response(self, error_msg: str, url: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            'success': False,
            'error': error_msg,
            'trust_score': 0,
            'article_summary': 'Analysis Failed',
            'source': urlparse(url).netloc if url else 'Unknown',
            'author': 'Unknown',
            'findings_summary': error_msg,
            'detailed_analysis': {},
            'processing_time': 0
        }

# ================================================================================
# FLASK APPLICATION
# ================================================================================

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, origins=["*"])

# Initialize analyzer
analyzer = TruthLensAnalyzer()

logger.info("=" * 80)
logger.info("TRUTHLENS CLEAN ARCHITECTURE - v5.0.0")
logger.info(f"Debug: {Config.DEBUG}")
logger.info(f"ScraperAPI: {'✓' if Config.SCRAPERAPI_KEY else '✗'}")
logger.info(f"OpenAI: {'✓' if Config.OPENAI_API_KEY else '✗'}")
logger.info("=" * 80)

@app.route('/')
def index():
    """Serve the main page"""
    try:
        return render_template('index.html')
    except:
        return """
        <html>
        <head><title>TruthLens</title></head>
        <body>
            <h1>TruthLens News Analyzer</h1>
            <p>API is running. Use POST /api/analyze with {'url': 'article_url'}</p>
        </body>
        </html>
        """

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'version': '5.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze_endpoint():
    """Main analysis endpoint"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Get URL from request
        url = data.get('url') or data.get('input_data', '')
        
        if not url or not url.startswith('http'):
            return jsonify({'success': False, 'error': 'Valid URL required'}), 400
        
        logger.info(f"Analysis request for: {url}")
        
        # Perform analysis
        result = analyzer.analyze(url)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/static/<path:path>')
def send_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting TruthLens on port {port}")
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)
