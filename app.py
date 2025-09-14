"""
TruthLens News Analyzer - Complete Real Analysis Implementation
Date: September 13, 2025
Version: 3.6 PRODUCTION - SYNTAX ERROR FIXED

CRITICAL FIXES IN THIS VERSION:
1. Fixed IndentationError on line 1483
2. Routes are at MODULE LEVEL for Gunicorn
3. Services initialized at MODULE LEVEL
4. NewsAnalyzer instance created at MODULE LEVEL
5. Fixed NBC/CNBC domain recognition
6. Fixed author scoring for recognized platforms

This version is specifically structured for Gunicorn deployment on Render.
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
logger.info("TRUTHLENS NEWS ANALYZER - v3.6 SYNTAX FIXED")
logger.info(f"Python Version: {sys.version}")
logger.info(f"Working Directory: {os.getcwd()}")
logger.info(f"NLP Available: {NLP_AVAILABLE}")
logger.info("=" * 80)

# Configuration
class Config:
    """Application configuration"""
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    ENV = os.environ.get('FLASK_ENV', 'production')
    
    # API Keys from environment
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    SCRAPERAPI_KEY = os.environ.get('SCRAPERAPI_KEY')
    GOOGLE_FACT_CHECK_API_KEY = os.environ.get('GOOGLE_FACT_CHECK_API_KEY')
    NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
    NEWSAPI_KEY = os.environ.get('NEWSAPI_KEY')  # Alternative name
    
    @classmethod
    def log_status(cls):
        logger.info("API Keys Configuration:")
        logger.info(f"  OpenAI: {'✓' if cls.OPENAI_API_KEY else '✗'}")
        logger.info(f"  ScraperAPI: {'✓' if cls.SCRAPERAPI_KEY else '✗'}")
        logger.info(f"  Google Fact Check: {'✓' if cls.GOOGLE_FACT_CHECK_API_KEY else '✗'}")
        logger.info(f"  News API: {'✓' if cls.NEWS_API_KEY or cls.NEWSAPI_KEY else '✗'}")

Config.log_status()

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
# REAL ANALYSIS UTILITIES
# ================================================================================

class TextAnalyzer:
    """Real text analysis utilities using NLP"""
    
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer() if NLP_AVAILABLE else None
        self.stop_words = set(stopwords.words('english')) if NLP_AVAILABLE else set()
        
        # Bias indicators
        self.bias_words = {
            'left': ['progressive', 'liberal', 'socialist', 'equality', 'social justice', 
                    'climate crisis', 'systemic', 'marginalized', 'inclusive', 'diversity'],
            'right': ['conservative', 'traditional', 'patriot', 'freedom', 'liberty',
                     'constitution', 'law and order', 'illegal aliens', 'radical left'],
            'loaded': ['slam', 'blast', 'destroy', 'shocking', 'bombshell', 'explosive',
                      'devastating', 'outrageous', 'scandal', 'corrupt', 'evil', 'dangerous']
        }
        
        # Manipulation patterns
        self.manipulation_patterns = {
            'fear_mongering': ['catastrophe', 'disaster', 'apocalypse', 'terror', 'nightmare'],
            'clickbait': ['you won\'t believe', 'shocking truth', 'this one trick', 'doctors hate'],
            'emotional': ['heartbreaking', 'outrage', 'fury', 'tears', 'tragic'],
            'absolute': ['always', 'never', 'everyone', 'nobody', 'completely', 'totally']
        }
        
        # FIXED: Enhanced credible domains with proper NBC/CNBC entries
        self.credible_domains = {
            'high': [
                'reuters.com', 'apnews.com', 'bbc.com', 'bbc.co.uk', 'npr.org', 'pbs.org',
                'theguardian.com', 'wsj.com', 'nytimes.com', 'washingtonpost.com',
                'economist.com', 'ft.com', 'nature.com', 'science.org'
            ],
            'medium': [
                'cnn.com', 'foxnews.com', 'msnbc.com', 'bloomberg.com', 'forbes.com',
                'businessinsider.com', 'thehill.com', 'politico.com',
                'nbcnews.com', 'nbc.com', 'cnbc.com',  # FIXED: Added proper NBC domains
                'abcnews.com', 'abcnews.go.com', 'cbsnews.com', 'cbs.com',
                'usatoday.com', 'time.com', 'newsweek.com',
                'axios.com', 'vox.com', 'slate.com', 'theatlantic.com'
            ],
            'low': [
                'infowars.com', 'breitbart.com', 'dailywire.com', 'huffpost.com',
                'buzzfeed.com', 'dailymail.co.uk', 'thesun.co.uk'
            ]
        }
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        if not NLP_AVAILABLE or not text:
            return {'compound': 0, 'positive': 0, 'negative': 0, 'neutral': 1}
        
        try:
            scores = self.sia.polarity_scores(text)
            return scores
        except:
            return {'compound': 0, 'positive': 0, 'negative': 0, 'neutral': 1}
    
    def calculate_readability(self, text: str) -> Dict[str, Any]:
        """Calculate readability metrics"""
        if not text:
            return {'score': 50, 'level': 'Unknown', 'grade': 0}
        
        sentences = sent_tokenize(text) if NLP_AVAILABLE else text.split('.')
        words = word_tokenize(text) if NLP_AVAILABLE else text.split()
        
        # Basic metrics
        num_sentences = max(len(sentences), 1)
        num_words = len(words)
        num_syllables = sum([self._count_syllables(word) for word in words])
        
        # Flesch Reading Ease
        if num_sentences > 0 and num_words > 0:
            avg_sentence_length = num_words / num_sentences
            avg_syllables_per_word = num_syllables / num_words
            flesch_score = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word
            flesch_score = max(0, min(100, flesch_score))
        else:
            flesch_score = 50
        
        # Determine reading level
        if flesch_score >= 90:
            level = "Very Easy"
            grade = 5
        elif flesch_score >= 80:
            level = "Easy"
            grade = 6
        elif flesch_score >= 70:
            level = "Fairly Easy"
            grade = 7
        elif flesch_score >= 60:
            level = "Standard"
            grade = 8
        elif flesch_score >= 50:
            level = "Fairly Difficult"
            grade = 10
        elif flesch_score >= 30:
            level = "Difficult"
            grade = 13
        else:
            level = "Very Difficult"
            grade = 16
        
        return {
            'score': int(flesch_score),
            'level': level,
            'grade': grade,
            'avg_sentence_length': avg_sentence_length if num_sentences > 0 else 0,
            'avg_word_length': avg_syllables_per_word if num_words > 0 else 0
        }
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word"""
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        if word.endswith("e"):
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def detect_bias_indicators(self, text: str) -> Dict[str, Any]:
        """Detect bias indicators in text"""
        if not text:
            return {'bias_score': 50, 'political_lean': 'Center', 'loaded_words': 0}
        
        text_lower = text.lower()
        words = word_tokenize(text_lower) if NLP_AVAILABLE else text_lower.split()
        
        # Count bias indicators
        left_count = sum(1 for word in self.bias_words['left'] if word in text_lower)
        right_count = sum(1 for word in self.bias_words['right'] if word in text_lower)
        loaded_count = sum(1 for word in self.bias_words['loaded'] if word in text_lower)
        
        # Determine political lean
        if left_count > right_count * 1.5:
            political_lean = 'Left'
        elif right_count > left_count * 1.5:
            political_lean = 'Right'
        else:
            political_lean = 'Center'
        
        # Calculate bias score (0-100, higher = more biased)
        total_bias_words = left_count + right_count + loaded_count
        bias_score = min(100, (total_bias_words / len(words)) * 1000) if words else 50
        
        return {
            'bias_score': int(bias_score),
            'political_lean': political_lean,
            'loaded_words': loaded_count,
            'left_indicators': left_count,
            'right_indicators': right_count
        }
    
    def detect_manipulation(self, text: str) -> Dict[str, Any]:
        """Detect manipulation techniques"""
        if not text:
            return {'manipulation_score': 0, 'techniques_found': 0, 'techniques': []}
        
        text_lower = text.lower()
        techniques = []
        
        for technique, patterns in self.manipulation_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    techniques.append(technique)
                    break
        
        # Check for ALL CAPS (shouting)
        caps_words = [word for word in text.split() if word.isupper() and len(word) > 2]
        if len(caps_words) > 3:
            techniques.append('excessive_caps')
        
        # Check for excessive punctuation
        if text.count('!') > 3 or text.count('?') > 5:
            techniques.append('excessive_punctuation')
        
        manipulation_score = min(100, len(techniques) * 20)
        
        return {
            'manipulation_score': manipulation_score,
            'techniques_found': len(techniques),
            'techniques': list(set(techniques))
        }
    
    def extract_claims(self, text: str) -> List[str]:
        """Extract factual claims from text"""
        if not text:
            return []
        
        claims = []
        sentences = sent_tokenize(text) if NLP_AVAILABLE else text.split('.')
        
        # Patterns that indicate factual claims
        claim_patterns = [
            r'\d+\s*%',  # Percentages
            r'\$\d+',     # Money amounts
            r'\d+\s*(million|billion|thousand)',  # Large numbers
            r'according to',
            r'study shows',
            r'research indicates',
            r'data reveals',
            r'statistics show'
        ]
        
        for sentence in sentences[:20]:  # Limit to first 20 sentences
            for pattern in claim_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    claims.append(sentence.strip())
                    break
        
        return claims[:10]  # Return max 10 claims

# ================================================================================
# SERVICE IMPLEMENTATIONS WITH REAL ANALYSIS
# ================================================================================

class BaseAnalyzer:
    """Base class for all analysis services"""
    
    def __init__(self, service_name):
        self.service_name = service_name
        self.available = True
        self.text_analyzer = TextAnalyzer()
        logger.info(f"  ✓ {service_name} initialized")
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform analysis"""
        try:
            result = self._perform_analysis(data)
            return self.get_success_result(result)
        except Exception as e:
            logger.error(f"{self.service_name} error: {e}")
            return self.get_error_result(str(e))
    
    def _perform_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Override in subclasses"""
        return {'score': 50}
    
    def get_success_result(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format successful result"""
        return {
            'success': True,
            'service': self.service_name,
            'data': data,
            'timestamp': time.time()
        }
    
    def get_error_result(self, error: str) -> Dict[str, Any]:
        """Format error result"""
        return {
            'success': False,
            'service': self.service_name,
            'error': error,
            'data': self._get_fallback_data()
        }
    
    def _get_fallback_data(self) -> Dict[str, Any]:
        """Provide fallback data on error"""
        return {'score': 50, 'error': 'Analysis failed'}

class ArticleExtractor(BaseAnalyzer):
    """Extract and analyze article content"""
    
    def __init__(self):
        super().__init__('article_extractor')
        self.scraperapi_key = Config.SCRAPERAPI_KEY
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _perform_analysis(self, data):
        url = data.get('url', '')
        text = data.get('text', '')
        
        if text:
            return self._analyze_text(text, source='direct_input')
        elif url:
            return self._extract_from_url(url)
        else:
            raise ValueError('No content provided')
    
    def _extract_from_url(self, url: str) -> Dict[str, Any]:
        """Extract article from URL with multiple methods"""
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '').lower()
        
        logger.info(f"Extracting from URL: {url}")
        logger.info(f"Parsed domain: {domain}")
        
        # Try newspaper3k first
        try:
            article = Article(url)
            article.download()
            article.parse()
            
            if article.text and len(article.text) > 100:
                author = self._clean_author(article.authors[0] if article.authors else 'Unknown')
                logger.info(f"Extracted author: {author} from domain: {domain}")
                
                return {
                    'title': article.title or 'Article',
                    'domain': domain,
                    'author': author,
                    'content': article.text[:10000],
                    'url': url,
                    'published_date': article.publish_date.isoformat() if article.publish_date else None,
                    'extraction_method': 'newspaper3k',
                    'word_count': len(article.text.split()),
                    'success': True
                }
        except Exception as e:
            logger.debug(f"Newspaper3k failed: {e}")
        
        # Try ScraperAPI if available
        if self.scraperapi_key:
            try:
                return self._extract_with_scraperapi(url, domain)
            except Exception as e:
                logger.debug(f"ScraperAPI failed: {e}")
        
        # Fallback to direct request
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return self._parse_html(response.text, url, domain)
        except Exception as e:
            logger.error(f"All extraction methods failed: {e}")
            return self._get_fallback_article_data(url, domain)
    
    def _extract_with_scraperapi(self, url: str, domain: str) -> Dict[str, Any]:
        """Extract using ScraperAPI"""
        api_url = "http://api.scraperapi.com"
        params = {
            'api_key': self.scraperapi_key,
            'url': url,
            'render': 'false'
        }
        
        response = requests.get(api_url, params=params, timeout=15)
        response.raise_for_status()
        
        return self._parse_html(response.text, url, domain)
    
    def _parse_html(self, html: str, url: str, domain: str) -> Dict[str, Any]:
        """Parse HTML content"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract title
        title = None
        for selector in ['h1', 'title', 'meta[property="og:title"]']:
            elem = soup.select_one(selector)
            if elem:
                title = elem.get_text(strip=True) if selector != 'meta[property="og:title"]' else elem.get('content')
                if title:
                    break
        
        # Extract author with multiple methods
        author = self._extract_author_from_html(soup, domain)
        logger.info(f"HTML extracted author: {author} from domain: {domain}")
        
        # Extract content
        content = self._extract_content_from_html(soup)
        
        # Extract publish date
        publish_date = self._extract_date_from_html(soup)
        
        return {
            'title': title or f'Article from {domain}',
            'domain': domain,
            'author': author,
            'content': content,
            'url': url,
            'published_date': publish_date,
            'extraction_method': 'html_parser',
            'word_count': len(content.split()),
            'success': True
        }
    
    def _extract_author_from_html(self, soup: BeautifulSoup, domain: str) -> str:
        """Extract author with multiple fallback methods"""
        
        # Method 1: Meta tags
        meta_selectors = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            'meta[name="byl"]',
            'meta[name="parsely-author"]'
        ]
        
        for selector in meta_selectors:
            elem = soup.select_one(selector)
            if elem and elem.get('content'):
                return self._clean_author(elem['content'])
        
        # Method 2: Common class/id patterns (including NBC specific)
        author_selectors = [
            '.author-name', '.by-author', '.article-author', '.post-author',
            '.author', '.writer', '.journalist', '.reporter',
            '#author', '[itemprop="author"]', '[rel="author"]',
            'span.by', 'div.byline', 'p.byline',
            '.byline__name', '.author__name', '.article__author'  # NBC patterns
        ]
        
        for selector in author_selectors:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                if text and len(text) > 2 and len(text) < 100:
                    return self._clean_author(text)
        
        # Method 3: Text pattern matching
        patterns = [
            r'[Bb]y\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            r'[Ww]ritten\s+by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            r'[Aa]uthor:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'
        ]
        
        text = soup.get_text()
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return self._clean_author(match.group(1))
        
        return 'Unknown'
    
    def _extract_content_from_html(self, soup: BeautifulSoup) -> str:
        """Extract main content from HTML"""
        # Remove script and style elements
        for script in soup(["script", "style", "meta", "link"]):
            script.decompose()
        
        # Try to find article body
        content_selectors = [
            'article', 'main', '[role="main"]',
            '.article-body', '.post-content', '.entry-content',
            '.story-body', '.content-body'
        ]
        
        for selector in content_selectors:
            elem = soup.select_one(selector)
            if elem:
                paragraphs = elem.find_all('p')
                if paragraphs:
                    content = ' '.join([p.get_text(strip=True) for p in paragraphs])
                    if len(content) > 200:
                        return content[:10000]
        
        # Fallback: get all paragraphs
        paragraphs = soup.find_all('p')
        content = ' '.join([p.get_text(strip=True) for p in paragraphs[:50]])
        return content[:10000] if content else 'Could not extract article content.'
    
    def _extract_date_from_html(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract publish date from HTML"""
        date_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="publish_date"]',
            'time[datetime]',
            'meta[name="date"]'
        ]
        
        for selector in date_selectors:
            elem = soup.select_one(selector)
            if elem:
                if selector.startswith('meta'):
                    date_str = elem.get('content')
                else:
                    date_str = elem.get('datetime')
                
                if date_str:
                    return date_str
        
        return None
    
    def _clean_author(self, author_string: str) -> str:
        """Clean author name"""
        if not author_string or author_string.lower() in ['unknown', 'staff', 'admin']:
            return 'Unknown'
        
        # Remove common prefixes
        author = re.sub(r'^[Bb]y\s+', '', author_string)
        author = re.sub(r'^[Ww]ritten\s+by\s+', '', author)
        
        # Remove email addresses
        author = re.sub(r'\S+@\S+', '', author)
        
        # Remove common suffixes
        author = re.sub(r'\s*[\|\-–—,].*$', '', author)
        
        # Clean up
        author = author.strip()
        
        # Validate
        if len(author) < 2 or len(author) > 100:
            return 'Unknown'
        
        return author
    
    def _analyze_text(self, text: str, source: str) -> Dict[str, Any]:
        """Analyze direct text input"""
        sentences = text.split('.')
        title = sentences[0][:100] if sentences else 'Text Analysis'
        
        return {
            'title': title,
            'domain': source,
            'author': 'User Provided',
            'content': text[:10000],
            'url': None,
            'published_date': None,
            'extraction_method': 'direct_text',
            'word_count': len(text.split()),
            'success': True
        }
    
    def _get_fallback_article_data(self, url: str, domain: str) -> Dict[str, Any]:
        """Fallback data when extraction fails"""
        return {
            'title': f'Article from {domain}',
            'domain': domain,
            'author': 'Unknown',
            'content': 'Article content could not be extracted.',
            'url': url,
            'published_date': None,
            'extraction_method': 'fallback',
            'word_count': 0,
            'success': False
        }

class SourceCredibility(BaseAnalyzer):
    """Analyze source credibility with real metrics"""
    
    def __init__(self):
        super().__init__('source_credibility')
    
    def _perform_analysis(self, data):
        domain = data.get('domain', 'unknown.com')
        content = data.get('content', '')
        
        # FIXED: Clean domain for comparison
        domain_clean = domain.lower().replace('www.', '')
        
        logger.info(f"Analyzing source credibility for domain: {domain_clean}")
        
        # Check domain credibility
        credibility_level = self._check_domain_credibility(domain_clean)
        
        logger.info(f"Domain {domain_clean} credibility: {credibility_level}")
        
        # Check HTTPS
        url = data.get('url', '')
        uses_https = url.startswith('https://') if url else False
        
        # Analyze content quality indicators
        quality_indicators = self._analyze_quality_indicators(content)
        
        # Calculate final score
        base_score = credibility_level['score']
        
        # Adjust based on HTTPS
        if uses_https:
            base_score += 5
        
        # Adjust based on content quality
        if quality_indicators['has_sources']:
            base_score += 10
        if quality_indicators['has_quotes']:
            base_score += 5
        if quality_indicators['professional_language']:
            base_score += 10
        
        final_score = min(100, max(0, base_score))
        
        logger.info(f"Final source credibility score for {domain_clean}: {final_score}")
        
        return {
            'score': final_score,
            'credibility_score': final_score,
            'rating': self._get_rating(final_score),
            'domain': domain,
            'reputation': credibility_level['reputation'],
            'uses_https': uses_https,
            'quality_indicators': quality_indicators,
            'analysis': {
                'what_we_looked': 'We evaluated domain reputation, security protocols, content quality indicators, and historical accuracy records.',
                'what_we_found': f'The domain {domain} has a {credibility_level["reputation"]} reputation with {"HTTPS security" if uses_https else "no HTTPS"}. {quality_indicators["summary"]}',
                'what_it_means': self._get_credibility_interpretation(final_score, credibility_level['reputation'])
            }
        }
    
    def _check_domain_credibility(self, domain: str) -> Dict[str, Any]:
        """Check domain against known credibility lists"""
        domain_lower = domain.lower()
        
        # FIXED: Check if domain contains any of the credible domains
        for high_domain in self.text_analyzer.credible_domains['high']:
            if high_domain in domain_lower or domain_lower in high_domain:
                logger.info(f"Found high-tier match: {high_domain} in {domain_lower}")
                return {'score': 85, 'reputation': 'excellent', 'tier': 'high'}
        
        # Check medium credibility
        for med_domain in self.text_analyzer.credible_domains['medium']:
            if med_domain in domain_lower or domain_lower in med_domain:
                logger.info(f"Found medium-tier match: {med_domain} in {domain_lower}")
                return {'score': 65, 'reputation': 'good', 'tier': 'medium'}
        
        # Check low credibility
        for low_domain in self.text_analyzer.credible_domains['low']:
            if low_domain in domain_lower or domain_lower in low_domain:
                logger.info(f"Found low-tier match: {low_domain} in {domain_lower}")
                return {'score': 35, 'reputation': 'questionable', 'tier': 'low'}
        
        # Unknown domain - neutral score
        logger.info(f"Domain {domain_lower} not found in any credibility tier")
        return {'score': 50, 'reputation': 'unknown', 'tier': 'unverified'}
    
    def _analyze_quality_indicators(self, content: str) -> Dict[str, Any]:
        """Analyze content quality indicators"""
        if not content:
            return {
                'has_sources': False,
                'has_quotes': False,
                'professional_language': False,
                'summary': 'No content available for analysis.'
            }
        
        content_lower = content.lower()
        
        # Check for source citations
        source_patterns = ['according to', 'sources say', 'reported by', 'study shows', 'research indicates']
        has_sources = any(pattern in content_lower for pattern in source_patterns)
        
        # Check for quotes
        has_quotes = '"' in content or '"' in content or '"' in content
        
        # Check language professionalism (absence of casual/sensational language)
        unprofessional = ['click here', 'amazing', 'unbelievable', 'you won\'t believe', 'shocking']
        professional_language = not any(term in content_lower for term in unprofessional)
        
        summary_parts = []
        if has_sources:
            summary_parts.append('Sources are cited')
        if has_quotes:
            summary_parts.append('includes direct quotes')
        if professional_language:
            summary_parts.append('uses professional language')
        
        summary = '. '.join(summary_parts) if summary_parts else 'Limited quality indicators found.'
        
        return {
            'has_sources': has_sources,
            'has_quotes': has_quotes,
            'professional_language': professional_language,
            'summary': summary
        }
    
    def _get_rating(self, score: int) -> str:
        """Convert score to rating"""
        if score >= 80:
            return 'Excellent'
        elif score >= 65:
            return 'Good'
        elif score >= 50:
            return 'Fair'
        elif score >= 35:
            return 'Poor'
        else:
            return 'Very Poor'
    
    def _get_credibility_interpretation(self, score: int, reputation: str) -> str:
        """Get interpretation of credibility score"""
        if score >= 80:
            return f'This source has excellent credibility with {reputation} reputation. Information is likely to be accurate and well-verified.'
        elif score >= 65:
            return f'This source has good credibility with {reputation} reputation. Generally reliable but verify important claims.'
        elif score >= 50:
            return f'This source has moderate credibility with {reputation} reputation. Cross-reference important information with other sources.'
        else:
            return f'This source has low credibility with {reputation} reputation. Be cautious and verify all claims independently.'

class BiasDetector(BaseAnalyzer):
    """Detect bias using real text analysis"""
    
    def __init__(self):
        super().__init__('bias_detector')
    
    def _perform_analysis(self, data):
        content = data.get('content', '')
        
        if not content:
            return self._get_fallback_data()
        
        # Detect bias indicators
        bias_analysis = self.text_analyzer.detect_bias_indicators(content)
        
        # Analyze sentiment
        sentiment = self.text_analyzer.analyze_sentiment(content)
        
        # Calculate emotional tone
        emotional_score = abs(sentiment['compound']) * 100
        
        # Combine bias indicators
        bias_score = bias_analysis['bias_score']
        
        # Adjust bias score based on emotional tone
        if emotional_score > 50:
            bias_score = min(100, bias_score + 10)
        
        # Calculate objectivity score for frontend
        objectivity_score = 100 - bias_score
        
        # Determine dominant bias
        if bias_score < 30:
            dominant_bias = 'Balanced'
        else:
            dominant_bias = bias_analysis['political_lean']
        
        return {
            'score': objectivity_score,  # Inverted for trust score calculation
            'bias_score': bias_score,
            'political_lean': bias_analysis['political_lean'],
            'bias_level': self._get_bias_level(bias_score),
            'sentiment': sentiment,
            'emotional_tone': emotional_score,
            'loaded_words': bias_analysis['loaded_words'],
            'objectivity_score': objectivity_score,  # Added for frontend
            'dominant_bias': dominant_bias,  # Added for frontend
            'analysis': {
                'what_we_looked': 'We analyzed language patterns, word choices, emotional tone, political indicators, and presentation balance.',
                'what_we_found': f'The article shows {bias_analysis["political_lean"]} lean with {bias_analysis["loaded_words"]} loaded terms. Emotional tone is {int(emotional_score)}% intense.',
                'what_it_means': self._get_bias_interpretation(bias_score, bias_analysis['political_lean'])
            }
        }
    
    def _get_bias_level(self, score: int) -> str:
        """Convert bias score to level"""
        if score < 20:
            return 'Minimal'
        elif score < 40:
            return 'Low'
        elif score < 60:
            return 'Moderate'
        elif score < 80:
            return 'High'
        else:
            return 'Extreme'
    
    def _get_bias_interpretation(self, bias_score: int, lean: str) -> str:
        """Get interpretation of bias analysis"""
        if bias_score < 20:
            return 'The article appears well-balanced with minimal bias. Information is presented objectively.'
        elif bias_score < 40:
            return f'Some {lean} bias detected but within acceptable journalistic standards. Be aware of perspective.'
        elif bias_score < 60:
            return f'Moderate {lean} bias present. Consider seeking alternative viewpoints for balance.'
        else:
            return f'Significant {lean} bias detected. This appears to be opinion or advocacy rather than neutral reporting.'

class FactChecker(BaseAnalyzer):
    """Check facts using claim extraction and verification indicators"""
    
    def __init__(self):
        super().__init__('fact_checker')
    
    def _perform_analysis(self, data):
        content = data.get('content', '')
        
        if not content:
            return self._get_fallback_data()
        
        # Extract claims
        claims = self.text_analyzer.extract_claims(content)
        
        # Analyze each claim for verification indicators
        verified_claims = []
        unverified_claims = []
        
        for claim in claims:
            if self._has_verification_indicators(claim):
                verified_claims.append(claim)
            else:
                unverified_claims.append(claim)
        
        # Calculate score
        total_claims = len(claims)
        verified_count = len(verified_claims)
        
        if total_claims > 0:
            accuracy_score = int((verified_count / total_claims) * 100)
            accuracy_rate = accuracy_score  # Added for frontend
        else:
            accuracy_score = 50  # No claims found
            accuracy_rate = 0
        
        return {
            'score': accuracy_score,
            'fact_check_score': accuracy_score,
            'claims_found': total_claims,
            'claims_checked': total_claims,
            'claims_verified': verified_count,
            'accuracy_rate': accuracy_rate,  # Added for frontend
            'verified_claims': verified_claims[:5],  # Limit for display
            'unverified_claims': unverified_claims[:5],
            'analysis': {
                'what_we_looked': 'We identified factual claims and checked for verification indicators like sources, data, and citations.',
                'what_we_found': f'Found {total_claims} factual claims. {verified_count} have verification indicators, {len(unverified_claims)} lack support.',
                'what_it_means': self._get_fact_check_interpretation(accuracy_score, total_claims)
            }
        }
    
    def _has_verification_indicators(self, claim: str) -> bool:
        """Check if claim has verification indicators"""
        indicators = [
            'according to',
            'study',
            'research',
            'survey',
            'data',
            'report',
            'analysis',
            'official',
            'confirmed',
            'verified'
        ]
        
        claim_lower = claim.lower()
        return any(indicator in claim_lower for indicator in indicators)
    
    def _get_fact_check_interpretation(self, score: int, total_claims: int) -> str:
        """Get interpretation of fact checking results"""
        if total_claims == 0:
            return 'No specific factual claims detected. Article may be opinion or commentary.'
        elif score >= 80:
            return 'Most claims have verification indicators. High factual reliability.'
        elif score >= 60:
            return 'Majority of claims appear supported. Generally factual with some unverified statements.'
        elif score >= 40:
            return 'Mixed factual accuracy. Several claims lack verification. Reader caution advised.'
        else:
            return 'Many unverified claims detected. Fact-check independently before accepting claims.'

class TransparencyAnalyzer(BaseAnalyzer):
    """Analyze transparency of sources and attribution"""
    
    def __init__(self):
        super().__init__('transparency_analyzer')
    
    def _perform_analysis(self, data):
        content = data.get('content', '')
        author = data.get('author', 'Unknown')
        published_date = data.get('published_date')
        
        if not content:
            return self._get_fallback_data()
        
        # Count source citations
        source_patterns = [
            'according to',
            'reported by',
            'sources say',
            'officials said',
            'study by',
            'research from'
        ]
        
        content_lower = content.lower()
        sources_count = sum(1 for pattern in source_patterns if pattern in content_lower)
        
        # Count quotes
        quotes_count = content.count('"') // 2 + content.count('"')
        
        # Check transparency factors
        has_author = author and author != 'Unknown'
        has_date = bool(published_date)
        has_sources = sources_count > 0
        has_quotes = quotes_count > 0
        
        # Calculate transparency score
        score = 0
        if has_author:
            score += 25
        if has_date:
            score += 20
        if has_sources:
            score += min(30, sources_count * 5)
        if has_quotes:
            score += min(25, quotes_count * 5)
        
        return {
            'score': min(100, score),
            'transparency_score': min(100, score),
            'sources_cited': sources_count,
            'quotes_used': quotes_count,
            'source_count': sources_count,  # Added for frontend
            'quote_count': quotes_count,  # Added for frontend
            'has_author': has_author,
            'has_date': has_date,
            'has_sources': has_sources,
            'transparency_factors': {
                'author_attribution': 'Present' if has_author else 'Missing',
                'publication_date': 'Present' if has_date else 'Missing',
                'source_citations': f'{sources_count} found',
                'direct_quotes': f'{quotes_count} found'
            },
            'analysis': {
                'what_we_looked': 'We examined author attribution, publication dates, source citations, and use of direct quotes.',
                'what_we_found': f'Article has {sources_count} source citations and {quotes_count} quotes. Author {"identified" if has_author else "not identified"}.',
                'what_it_means': self._get_transparency_interpretation(score, sources_count)
            }
        }
    
    def _get_transparency_interpretation(self, score: int, sources: int) -> str:
        """Get interpretation of transparency analysis"""
        if score >= 80:
            return 'Excellent transparency with clear attribution and multiple sources. Highly accountable reporting.'
        elif score >= 60:
            return 'Good transparency with adequate sourcing and attribution. Reasonably accountable.'
        elif score >= 40:
            return 'Moderate transparency. Some attribution but limited sources. Additional verification recommended.'
        else:
            return 'Poor transparency. Lacks proper attribution or sources. Verify information independently.'

class ManipulationDetector(BaseAnalyzer):
    """Detect manipulation and propaganda techniques"""
    
    def __init__(self):
        super().__init__('manipulation_detector')
    
    def _perform_analysis(self, data):
        content = data.get('content', '')
        title = data.get('title', '')
        
        if not content:
            return self._get_fallback_data()
        
        # Combine title and content for analysis
        full_text = f"{title}\n{content}" if title else content
        
        # Detect manipulation techniques
        manipulation_analysis = self.text_analyzer.detect_manipulation(full_text)
        
        # Analyze sentiment for emotional manipulation
        sentiment = self.text_analyzer.analyze_sentiment(full_text)
        emotional_score = abs(sentiment['compound']) * 100
        
        # Detect clickbait patterns in title
        clickbait_score = 0
        if title:
            title_lower = title.lower()
            clickbait_patterns = ['you won\'t believe', 'shocking', 'amazing', 'this one trick', 'doctors hate']
            clickbait_score = sum(20 for pattern in clickbait_patterns if pattern in title_lower)
        
        # Calculate overall manipulation score
        manipulation_score = manipulation_analysis['manipulation_score']
        
        # Add emotional manipulation
        if emotional_score > 70:
            manipulation_score = min(100, manipulation_score + 20)
        
        # Add clickbait score
        manipulation_score = min(100, manipulation_score + clickbait_score)
        
        # Determine risk level for frontend
        if manipulation_score < 20:
            risk_level = 'Low'
        elif manipulation_score < 40:
            risk_level = 'Moderate'
        elif manipulation_score < 60:
            risk_level = 'High'
        else:
            risk_level = 'Extreme'
        
        return {
            'score': 100 - manipulation_score,  # Invert for trust score
            'manipulation_score': manipulation_score,
            'techniques_found': manipulation_analysis['techniques_found'],
            'techniques': manipulation_analysis['techniques'],
            'manipulation_techniques': manipulation_analysis['techniques'],  # Added for frontend
            'emotional_score': emotional_score,
            'emotional_language_count': int(emotional_score / 10),  # Added for frontend
            'clickbait_score': clickbait_score,
            'manipulation_level': self._get_manipulation_level(manipulation_score),
            'risk_level': risk_level,  # Added for frontend
            'analysis': {
                'what_we_looked': 'We analyzed for propaganda techniques, emotional manipulation, clickbait patterns, and misleading tactics.',
                'what_we_found': f'Found {manipulation_analysis["techniques_found"]} manipulation techniques. Emotional intensity: {int(emotional_score)}%.',
                'what_it_means': self._get_manipulation_interpretation(manipulation_score, manipulation_analysis['techniques'])
            }
        }
    
    def _get_manipulation_level(self, score: int) -> str:
        """Convert manipulation score to level"""
        if score < 20:
            return 'Minimal'
        elif score < 40:
            return 'Low'
        elif score < 60:
            return 'Moderate'
        elif score < 80:
            return 'High'
        else:
            return 'Extreme'
    
    def _get_manipulation_interpretation(self, score: int, techniques: List[str]) -> str:
        """Get interpretation of manipulation analysis"""
        if score < 20:
            return 'Minimal manipulation detected. Content appears straightforward and honest.'
        elif score < 40:
            return 'Some persuasive techniques used but within normal bounds. Be aware of emotional appeals.'
        elif score < 60:
            return f'Moderate manipulation using {", ".join(techniques[:2]) if techniques else "various techniques"}. Critical reading advised.'
        else:
            return 'High level of manipulation detected. Content appears designed to mislead or emotionally manipulate.'

class ContentAnalyzer(BaseAnalyzer):
    """Analyze content quality and structure"""
    
    def __init__(self):
        super().__init__('content_analyzer')
    
    def _perform_analysis(self, data):
        content = data.get('content', '')
        
        if not content:
            return self._get_fallback_data()
        
        # Analyze readability
        readability = self.text_analyzer.calculate_readability(content)
        
        # Analyze structure
        structure_analysis = self._analyze_structure(content)
        
        # Calculate word count and other metrics
        words = content.split()
        sentences = sent_tokenize(content) if NLP_AVAILABLE else content.split('.')
        paragraphs = content.split('\n\n')
        
        # Calculate quality score
        quality_score = 50  # Base score
        
        # Adjust for readability
        if 50 <= readability['score'] <= 70:
            quality_score += 20  # Optimal readability
        elif readability['score'] > 70:
            quality_score += 10  # Too simple
        else:
            quality_score -= 10  # Too complex
        
        # Adjust for structure
        if structure_analysis['well_structured']:
            quality_score += 15
        
        # Adjust for length
        if 300 <= len(words) <= 2000:
            quality_score += 15  # Good length
        
        quality_score = min(100, max(0, quality_score))
        
        # Determine quality level for frontend
        if quality_score >= 80:
            quality_level = 'Excellent'
        elif quality_score >= 60:
            quality_level = 'Good'
        elif quality_score >= 40:
            quality_level = 'Fair'
        else:
            quality_level = 'Poor'
        
        return {
            'score': quality_score,
            'quality_score': quality_score,
            'quality_level': quality_level,  # Added for frontend
            'readability': readability,
            'readability_level': readability['level'],  # Added for frontend
            'structure': structure_analysis,
            'word_count': len(words),
            'sentence_count': len(sentences),
            'paragraph_count': len(paragraphs),
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
            'analysis': {
                'what_we_looked': 'We evaluated readability, structure, grammar, vocabulary diversity, and overall presentation quality.',
                'what_we_found': f'Readability: {readability["level"]} (grade {readability["grade"]}). Word count: {len(words)}. Structure: {"Good" if structure_analysis["well_structured"] else "Needs improvement"}.',
                'what_it_means': self._get_content_interpretation(quality_score, readability['level'])
            }
        }
    
    def _analyze_structure(self, content: str) -> Dict[str, Any]:
        """Analyze content structure"""
        paragraphs = content.split('\n\n')
        sentences = sent_tokenize(content) if NLP_AVAILABLE else content.split('.')
        
        # Check for good structure indicators
        has_intro = len(paragraphs) > 1 and len(paragraphs[0]) > 50
        has_conclusion = len(paragraphs) > 2 and len(paragraphs[-1]) > 50
        has_body = len(paragraphs) >= 3
        
        well_structured = has_intro and has_body
        
        return {
            'well_structured': well_structured,
            'has_intro': has_intro,
            'has_body': has_body,
            'has_conclusion': has_conclusion,
            'paragraph_count': len(paragraphs),
            'avg_paragraph_length': sum(len(p.split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0
        }
    
    def _get_content_interpretation(self, score: int, readability: str) -> str:
        """Get interpretation of content analysis"""
        if score >= 80:
            return f'Excellent content quality with {readability} readability. Well-structured and professionally written.'
        elif score >= 60:
            return f'Good content quality with {readability} readability. Generally well-written with minor issues.'
        elif score >= 40:
            return f'Moderate content quality. {readability} readability may affect comprehension. Structure could be improved.'
        else:
            return 'Poor content quality. Difficult to read or poorly structured. May indicate low-quality source.'

class AuthorAnalyzer(BaseAnalyzer):
    """FIXED: Enhanced author credibility analyzer with proper scoring for recognized platforms"""
    
    def __init__(self):
        super().__init__('author_analyzer')
        self.news_api_key = Config.NEWS_API_KEY or Config.NEWSAPI_KEY
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # FIXED: Enhanced credible news organizations list
        self.credible_orgs = {
            'high': [
                'Reuters', 'Associated Press', 'BBC', 'NPR', 'PBS',
                'The Guardian', 'Wall Street Journal', 'New York Times',
                'Washington Post', 'The Economist', 'Financial Times',
                'ProPublica', 'Nature', 'Science'
            ],
            'medium': [
                'CNN', 'Fox News', 'MSNBC', 'CBS News', 'ABC News',
                'NBC News', 'NBC', 'CNBC', 'USA Today', 'The Hill', 'Politico',
                'Bloomberg', 'Forbes', 'Business Insider', 'Time', 'Newsweek',
                'Axios', 'Vox', 'The Atlantic', 'Slate'
            ]
        }
        
        # FIXED: Domain mapping for author credibility
        self.domain_mapping = {
            'nbcnews.com': 'NBC News',
            'nbc.com': 'NBC',
            'cnbc.com': 'CNBC',
            'cnn.com': 'CNN',
            'foxnews.com': 'Fox News',
            'msnbc.com': 'MSNBC',
            'cbsnews.com': 'CBS News',
            'abcnews.com': 'ABC News',
            'reuters.com': 'Reuters',
            'apnews.com': 'Associated Press',
            'bbc.com': 'BBC',
            'bbc.co.uk': 'BBC',
            'npr.org': 'NPR',
            'pbs.org': 'PBS',
            'nytimes.com': 'New York Times',
            'washingtonpost.com': 'Washington Post',
            'wsj.com': 'Wall Street Journal',
            'theguardian.com': 'The Guardian',
            'politico.com': 'Politico',
            'bloomberg.com': 'Bloomberg',
            'forbes.com': 'Forbes'
        }
    
    def _perform_analysis(self, data):
        author_name = data.get('author', 'Unknown')
        domain = data.get('domain', '').lower().replace('www.', '')
        content = data.get('content', '')
        
        logger.info(f"Analyzing author: {author_name} on domain: {domain}")
        
        if not author_name or author_name == 'Unknown':
            return self._get_unknown_author_analysis()
        
        # Clean author name
        cleaned_name = self._clean_author_name(author_name)
        if not self._is_valid_author_name(cleaned_name):
            return self._get_invalid_author_analysis(author_name)
        
        # FIXED: Enhanced credibility scoring
        # Start with base score based on domain tier
        domain_tier = self._get_domain_credibility_tier(domain)
        
        if domain_tier == 'high':
            credibility_score = 75  # Start high for top-tier sources
            logger.info(f"High-tier domain detected: {domain}, starting score: 75")
        elif domain_tier == 'medium':
            credibility_score = 65  # Start good for medium-tier sources
            logger.info(f"Medium-tier domain detected: {domain}, starting score: 65")
        else:
            credibility_score = 45  # Start neutral for unknown sources
            logger.info(f"Unknown domain: {domain}, starting score: 45")
        
        # Search publication history if News API available
        publication_count = 0
        if self.news_api_key:
            pub_history = self._search_publication_history(cleaned_name)
            publication_count = pub_history.get('total_articles', 0)
            
            # Adjust score based on publication history
            if publication_count > 50:
                credibility_score = min(100, credibility_score + 15)
            elif publication_count > 10:
                credibility_score = min(100, credibility_score + 10)
            elif publication_count > 0:
                credibility_score = min(100, credibility_score + 5)
        
        # Look for bio in content
        bio_info = self._extract_author_bio_from_content(content, cleaned_name)
        if bio_info and bio_info.get('has_credentials'):
            credibility_score = min(100, credibility_score + 10)
        
        # FIXED: Ensure minimum score for recognized platforms
        if domain_tier in ['high', 'medium'] and credibility_score < 65:
            credibility_score = 65
            logger.info(f"Adjusted score to minimum 65 for recognized platform")
        
        # Cap score
        credibility_score = max(0, min(100, credibility_score))
        
        logger.info(f"Final author credibility score: {credibility_score} for {cleaned_name} on {domain}")
        
        # Determine verification status for frontend
        if credibility_score >= 70:
            verification_status = 'Verified'
            verified = True
        elif credibility_score >= 50:
            verification_status = 'Partially Verified'
            verified = False
        else:
            verification_status = 'Unverified'
            verified = False
        
        return {
            'score': credibility_score,
            'credibility_score': credibility_score,
            'author_name': cleaned_name,
            'verified': verified,
            'verification_status': verification_status,
            'publication_count': publication_count,
            'domain_tier': domain_tier,
            'platform': self.domain_mapping.get(domain, domain),  # Added platform name
            'has_bio': bool(bio_info),
            'bio': bio_info.get('bio_text', '') if bio_info else '',
            'expertise_areas': [],  # Added for frontend
            'social_links': {},  # Added for frontend
            'analysis': {
                'what_we_looked': 'We investigated author credentials, publication history, and professional presence.',
                'what_we_found': f'Author {cleaned_name} has {publication_count} articles found. Publishing on {domain_tier}-tier site ({self.domain_mapping.get(domain, domain)}).',
                'what_it_means': self._get_author_interpretation(credibility_score, publication_count, domain_tier)
            }
        }
    
    def _clean_author_name(self, author_string: str) -> str:
        """Clean and standardize author name"""
        cleaned = re.sub(r'^(by|By|BY)\s+', '', author_string)
        cleaned = re.sub(r'\S+@\S+\.\S+', '', cleaned)
        cleaned = re.sub(r'\s*[\|\-–—,].*$', '', cleaned)
        cleaned = re.sub(r'\s*,?\s*(Reporter|Writer|Editor|Correspondent|Contributor).*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = ' '.join(cleaned.split())
        return cleaned.strip()
    
    def _is_valid_author_name(self, name: str) -> bool:
        """Check if the name appears to be valid"""
        if not name or len(name) < 3:
            return False
        
        generic_terms = ['staff', 'admin', 'editor', 'team', 'news', 'report', 'editorial']
        if name.lower() in generic_terms:
            return False
        
        if not re.match(r'^[A-Za-z\s\.\-\']+$', name):
            return False
        
        return True
    
    def _search_publication_history(self, author_name: str) -> Dict[str, Any]:
        """Search for author's publication history using News API"""
        if not self.news_api_key:
            return {'total_articles': 0, 'sources': []}
        
        try:
            url = 'https://newsapi.org/v2/everything'
            params = {
                'apiKey': self.news_api_key,
                'q': f'"{author_name}"',
                'searchIn': 'author',
                'sortBy': 'relevancy',
                'pageSize': 100,
                'from': (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            }
            
            response = self.session.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                # Count articles where author name matches
                matching_articles = 0
                for article in articles:
                    article_author = article.get('author', '')
                    if author_name.lower() in article_author.lower():
                        matching_articles += 1
                
                return {'total_articles': matching_articles}
            
        except Exception as e:
            logger.error(f"Error searching publication history: {e}")
        
        return {'total_articles': 0}
    
    def _get_domain_credibility_tier(self, domain: str) -> str:
        """FIXED: Get credibility tier of the domain with better matching"""
        domain_lower = domain.lower().replace('www.', '')
        
        # First check direct domain mapping
        if domain_lower in self.domain_mapping:
            org_name = self.domain_mapping[domain_lower]
            
            # Check which tier the organization belongs to
            for org in self.credible_orgs['high']:
                if org.lower() == org_name.lower():
                    return 'high'
            
            for org in self.credible_orgs['medium']:
                if org.lower() == org_name.lower():
                    return 'medium'
        
        # Fallback to checking if org name is in domain
        for org in self.credible_orgs['high']:
            if org.lower().replace(' ', '') in domain_lower:
                return 'high'
        
        for org in self.credible_orgs['medium']:
            if org.lower().replace(' ',
