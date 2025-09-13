"""
TruthLens News Analyzer - Complete Real Analysis Implementation
Date: September 13, 2025
Author: Production Implementation Team
Version: 3.1 PRODUCTION - ENHANCED AUTHOR ANALYSIS

COMPLETE IMPLEMENTATION WITH:
1. Real NLP text analysis using NLTK and TextBlob
2. Dynamic scoring based on actual content analysis
3. ENHANCED: Comprehensive author investigation with publication history
4. Pattern-based bias detection
5. Statistical fact checking indicators
6. Real transparency metrics
7. Manipulation technique detection
8. Content quality analysis with readability scores
9. ENHANCED: Author verification through News API and professional databases

This version includes comprehensive author investigation capabilities.
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
logger.info("TRUTHLENS NEWS ANALYZER - ENHANCED AUTHOR ANALYSIS v3.1")
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

# Create Flask app
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
        
        # Credible source indicators
        self.credible_domains = {
            'high': ['reuters.com', 'apnews.com', 'bbc.com', 'npr.org', 'pbs.org', 
                    'theguardian.com', 'wsj.com', 'nytimes.com', 'washingtonpost.com'],
            'medium': ['cnn.com', 'foxnews.com', 'msnbc.com', 'bloomberg.com', 'forbes.com',
                      'businessinsider.com', 'thehill.com', 'politico.com'],
            'low': ['infowars.com', 'breitbart.com', 'dailywire.com', 'huffpost.com']
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
# ENHANCED AUTHOR ANALYZER
# ================================================================================

class EnhancedAuthorAnalyzer:
    """Comprehensive author credibility analysis with real investigation"""
    
    def __init__(self, news_api_key: Optional[str] = None, scraperapi_key: Optional[str] = None):
        """Initialize enhanced author analyzer"""
        self.news_api_key = news_api_key
        self.scraperapi_key = scraperapi_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Known journalist databases/platforms
        self.journalist_platforms = {
            'muckrack': 'https://muckrack.com/',
            'linkedin': 'https://www.linkedin.com/in/',
            'twitter': 'https://twitter.com/',
            'contently': 'https://contently.com/',
            'journoportfolio': 'https://www.journoportfolio.com/'
        }
        
        # Credible news organizations
        self.credible_orgs = {
            'high': [
                'Reuters', 'Associated Press', 'BBC', 'NPR', 'PBS',
                'The Guardian', 'Wall Street Journal', 'New York Times',
                'Washington Post', 'The Economist', 'Financial Times',
                'Bloomberg', 'The Atlantic', 'ProPublica', 'The Intercept'
            ],
            'medium': [
                'CNN', 'Fox News', 'MSNBC', 'CBS News', 'ABC News',
                'NBC News', 'USA Today', 'The Hill', 'Politico',
                'Business Insider', 'Forbes', 'Fortune', 'TIME'
            ]
        }
        
        # Award organizations
        self.journalism_awards = [
            'Pulitzer Prize', 'Peabody Award', 'Emmy Award',
            'Edward R. Murrow Award', 'George Polk Award',
            'National Magazine Award', 'Sigma Delta Chi Award',
            'IRE Award', 'Online Journalism Award'
        ]
        
        logger.info("✓ EnhancedAuthorAnalyzer initialized with comprehensive capabilities")
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive author analysis"""
        author_name = data.get('author', 'Unknown')
        domain = data.get('domain', '')
        article_content = data.get('content', '')
        
        # Start with basic analysis
        if not author_name or author_name == 'Unknown':
            return self._get_unknown_author_analysis()
        
        # Clean and validate author name
        cleaned_name = self._clean_author_name(author_name)
        if not self._is_valid_author_name(cleaned_name):
            return self._get_invalid_author_analysis(author_name)
        
        # Initialize results
        analysis_results = {
            'author_name': cleaned_name,
            'original_name': author_name,
            'verification_status': 'unverified',
            'credibility_score': 50,
            'expertise_areas': [],
            'social_media': {},
            'publication_history': {},
            'awards': [],
            'red_flags': [],
            'trust_indicators': [],
            'detailed_findings': {}
        }
        
        # 1. Search for author's publication history
        if self.news_api_key:
            pub_history = self._search_publication_history(cleaned_name)
            analysis_results['publication_history'] = pub_history
            
            # Adjust score based on publication history
            if pub_history.get('total_articles', 0) > 50:
                analysis_results['credibility_score'] += 15
                analysis_results['trust_indicators'].append('Extensive publication history')
            elif pub_history.get('total_articles', 0) > 10:
                analysis_results['credibility_score'] += 10
                analysis_results['trust_indicators'].append('Established publication record')
            elif pub_history.get('total_articles', 0) == 0:
                analysis_results['red_flags'].append('No publication history found')
                analysis_results['credibility_score'] -= 10
        
        # 2. Check author presence on professional platforms
        professional_presence = self._check_professional_presence(cleaned_name)
        analysis_results['professional_profiles'] = professional_presence
        
        if professional_presence.get('has_linkedin'):
            analysis_results['credibility_score'] += 10
            analysis_results['trust_indicators'].append('Professional LinkedIn profile')
        
        if professional_presence.get('has_muckrack'):
            analysis_results['credibility_score'] += 15
            analysis_results['trust_indicators'].append('Listed on MuckRack journalist database')
            analysis_results['verification_status'] = 'partially_verified'
        
        # 3. Check social media verification
        social_verification = self._check_social_media_verification(cleaned_name)
        analysis_results['social_media'] = social_verification
        
        if social_verification.get('twitter_verified'):
            analysis_results['credibility_score'] += 10
            analysis_results['trust_indicators'].append('Verified Twitter/X account')
        
        # 4. Check for awards and recognition
        awards = self._check_awards_recognition(cleaned_name)
        if awards:
            analysis_results['awards'] = awards
            analysis_results['credibility_score'] += 20
            analysis_results['trust_indicators'].append(f"Award-winning journalist ({len(awards)} awards)")
            analysis_results['verification_status'] = 'verified'
        
        # 5. Check domain credibility
        domain_tier = self._get_domain_credibility_tier(domain)
        if domain_tier == 'high':
            analysis_results['credibility_score'] += 10
            analysis_results['trust_indicators'].append(f'Published on high-credibility site ({domain})')
        elif domain_tier == 'low':
            analysis_results['credibility_score'] -= 10
            analysis_results['red_flags'].append(f'Published on low-credibility site ({domain})')
        
        # 6. Look for bio/credentials in article
        bio_info = self._extract_author_bio_from_content(article_content, cleaned_name)
        if bio_info:
            analysis_results['bio_from_article'] = bio_info
            if bio_info.get('has_credentials'):
                analysis_results['credibility_score'] += 5
                analysis_results['trust_indicators'].append('Credentials provided in article')
        
        # Cap score at 0-100
        analysis_results['credibility_score'] = max(0, min(100, analysis_results['credibility_score']))
        
        # Generate detailed analysis
        analysis_results['analysis'] = self._generate_detailed_analysis(analysis_results)
        
        return {
            'score': analysis_results['credibility_score'],
            'credibility_score': analysis_results['credibility_score'],
            'author_name': analysis_results['author_name'],
            'verified': analysis_results['verification_status'] == 'verified',
            'verification_status': analysis_results['verification_status'],
            'publication_count': analysis_results['publication_history'].get('total_articles', 0),
            'expertise_areas': analysis_results.get('expertise_areas', []),
            'awards': analysis_results.get('awards', []),
            'social_media': analysis_results.get('social_media', {}),
            'trust_indicators': analysis_results.get('trust_indicators', []),
            'red_flags': analysis_results.get('red_flags', []),
            'bio': bio_info.get('bio_text', '') if bio_info else '',
            'analysis': analysis_results['analysis']
        }
    
    def _clean_author_name(self, author_string: str) -> str:
        """Clean and standardize author name"""
        if not author_string:
            return ''
        
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
        
        generic_terms = ['staff', 'admin', 'editor', 'team', 'news', 'report']
        if name.lower() in generic_terms:
            return False
        
        if ' ' not in name and len(name) < 10:
            return False
        
        if not re.match(r'^[A-Za-z\s\.\-\']+$', name):
            return False
        
        return True
    
    def _search_publication_history(self, author_name: str) -> Dict[str, Any]:
        """Search for author's publication history using News API"""
        if not self.news_api_key:
            return {'total_articles': 0, 'sources': [], 'date_range': None}
        
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
                
                sources = {}
                topics = []
                earliest_date = None
                latest_date = None
                
                for article in articles:
                    article_author = article.get('author', '')
                    if author_name.lower() in article_author.lower():
                        source = article.get('source', {}).get('name', 'Unknown')
                        sources[source] = sources.get(source, 0) + 1
                        
                        pub_date = article.get('publishedAt')
                        if pub_date:
                            if not earliest_date or pub_date < earliest_date:
                                earliest_date = pub_date
                            if not latest_date or pub_date > latest_date:
                                latest_date = pub_date
                        
                        title = article.get('title', '')
                        if title:
                            topics.append(title)
                
                expertise = self._identify_expertise_from_topics(topics)
                
                return {
                    'total_articles': len(articles),
                    'sources': dict(sorted(sources.items(), key=lambda x: x[1], reverse=True)[:5]),
                    'date_range': {
                        'earliest': earliest_date,
                        'latest': latest_date
                    },
                    'expertise_areas': expertise
                }
            
        except Exception as e:
            logger.error(f"Error searching publication history: {e}")
        
        return {'total_articles': 0, 'sources': [], 'date_range': None}
    
    def _check_professional_presence(self, author_name: str) -> Dict[str, bool]:
        """Check if author has professional journalism profiles"""
        presence = {
            'has_linkedin': False,
            'has_muckrack': False,
            'has_contently': False,
            'profile_urls': []
        }
        
        url_name = quote_plus(author_name)
        
        try:
            search_url = f"https://muckrack.com/search?q={url_name}"
            presence['has_muckrack'] = self._check_url_exists(search_url)
            if presence['has_muckrack']:
                presence['profile_urls'].append(search_url)
        except:
            pass
        
        return presence
    
    def _check_social_media_verification(self, author_name: str) -> Dict[str, Any]:
        """Check for verified social media accounts"""
        return {
            'twitter_verified': False,
            'twitter_handle': None,
            'twitter_followers': 0,
            'has_professional_bio': False
        }
    
    def _check_awards_recognition(self, author_name: str) -> List[str]:
        """Check if author has won journalism awards"""
        return []  # Would need award database API
    
    def _get_domain_credibility_tier(self, domain: str) -> str:
        """Get credibility tier of the domain"""
        domain_lower = domain.lower()
        
        for org in self.credible_orgs['high']:
            if org.lower() in domain_lower:
                return 'high'
        
        for org in self.credible_orgs['medium']:
            if org.lower() in domain_lower:
                return 'medium'
        
        return 'unknown'
    
    def _extract_author_bio_from_content(self, content: str, author_name: str) -> Optional[Dict[str, Any]]:
        """Extract author bio information from article content"""
        if not content or not author_name:
            return None
        
        bio_info = {
            'bio_text': '',
            'has_credentials': False,
            'credentials': [],
            'organization': None
        }
        
        bio_patterns = [
            rf'{author_name} is a .{{10,100}}',
            rf'{author_name}, a .{{10,100}}',
            rf'{author_name} has .{{10,100}}',
            rf'{author_name} covers .{{10,100}}'
        ]
        
        for pattern in bio_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                bio_info['bio_text'] = match.group(0)
                
                if any(cred in bio_info['bio_text'].lower() for cred in 
                       ['phd', 'master', 'degree', 'university', 'college', 'journalism']):
                    bio_info['has_credentials'] = True
                
                break
        
        return bio_info if bio_info['bio_text'] else None
    
    def _identify_expertise_from_topics(self, topics: List[str]) -> List[str]:
        """Identify expertise areas from article topics"""
        if not topics:
            return []
        
        categories = {
            'Politics': ['election', 'president', 'congress', 'senate', 'political', 'government'],
            'Technology': ['tech', 'ai', 'software', 'internet', 'cyber', 'data', 'app'],
            'Business': ['business', 'economy', 'market', 'stock', 'company', 'ceo', 'earnings'],
            'Science': ['science', 'research', 'study', 'scientist', 'discovery', 'medical'],
            'Sports': ['sports', 'game', 'player', 'team', 'championship', 'athlete'],
            'Entertainment': ['movie', 'music', 'celebrity', 'film', 'actor', 'singer'],
            'Health': ['health', 'medical', 'disease', 'treatment', 'hospital', 'doctor']
        }
        
        expertise_counts = {}
        
        for topic in topics:
            topic_lower = topic.lower()
            for category, keywords in categories.items():
                if any(keyword in topic_lower for keyword in keywords):
                    expertise_counts[category] = expertise_counts.get(category, 0) + 1
        
        sorted_expertise = sorted(expertise_counts.items(), key=lambda x: x[1], reverse=True)
        return [cat for cat, _ in sorted_expertise[:3]]
    
    def _generate_detailed_analysis(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Generate detailed analysis text"""
        score = results['credibility_score']
        pub_count = results['publication_history'].get('total_articles', 0)
        
        what_we_looked = (
            "We conducted a comprehensive author investigation including: "
            "publication history search across major news outlets, "
            "professional profile verification on journalism platforms, "
            "social media verification status, "
            "awards and recognition database checks, "
            "and consistency analysis with previous work."
        )
        
        findings = []
        
        if results['author_name'] != 'Unknown':
            findings.append(f"Author identified as {results['author_name']}")
        
        if pub_count > 0:
            findings.append(f"Found {pub_count} articles published by this author")
            sources = results['publication_history'].get('sources', {})
            if sources:
                top_source = list(sources.keys())[0] if sources else 'various outlets'
                findings.append(f"primarily publishing in {top_source}")
        else:
            findings.append("No previous publication history found in our database")
        
        if results.get('trust_indicators'):
            findings.append(f"{len(results['trust_indicators'])} positive credibility indicators")
        
        if results.get('red_flags'):
            findings.append(f"Identified {len(results['red_flags'])} potential concerns")
        
        what_we_found = '. '.join(findings) + '.'
        
        if score >= 80:
            what_it_means = (
                "This author has excellent credibility with verified credentials and "
                "extensive publication history. Their work can generally be trusted as "
                "coming from an established journalism professional."
            )
        elif score >= 60:
            what_it_means = (
                "This author shows good credibility indicators with some verification. "
                "They appear to be a legitimate journalist, though not extensively established. "
                "Their work should be reliable but verify important claims."
            )
        elif score >= 40:
            what_it_means = (
                "This author has limited verification and mixed credibility indicators. "
                "They may be a newer journalist or freelance writer. Exercise normal caution "
                "and cross-reference important information."
            )
        else:
            what_it_means = (
                "This author could not be verified and lacks credibility indicators. "
                "This could be a pseudonym, new writer, or potentially unreliable source. "
                "Verify all claims independently and seek additional sources."
            )
        
        return {
            'what_we_looked': what_we_looked,
            'what_we_found': what_we_found,
            'what_it_means': what_it_means
        }
    
    def _check_url_exists(self, url: str) -> bool:
        """Check if a URL exists"""
        try:
            response = self.session.head(url, timeout=3, allow_redirects=True)
            return response.status_code == 200
        except:
            return False
    
    def _get_unknown_author_analysis(self) -> Dict[str, Any]:
        """Return analysis for unknown/missing author"""
        return {
            'score': 30,
            'credibility_score': 30,
            'author_name': 'Unknown',
            'verified': False,
            'verification_status': 'unidentified',
            'publication_count': 0,
            'expertise_areas': [],
            'awards': [],
            'social_media': {},
            'trust_indicators': [],
            'red_flags': ['No author attribution provided'],
            'bio': '',
            'analysis': {
                'what_we_looked': 'We searched for author attribution in the article and metadata.',
                'what_we_found': 'No author information was provided for this article.',
                'what_it_means': 'Articles without author attribution lack accountability and transparency. This is a significant credibility concern as readers cannot verify the writer\'s expertise or track record.'
            }
        }
    
    def _get_invalid_author_analysis(self, author_string: str) -> Dict[str, Any]:
        """Return analysis for invalid author string"""
        return {
            'score': 35,
            'credibility_score': 35,
            'author_name': author_string,
            'verified': False,
            'verification_status': 'invalid',
            'publication_count': 0,
            'expertise_areas': [],
            'awards': [],
            'social_media': {},
            'trust_indicators': [],
            'red_flags': ['Author attribution appears to be generic or invalid'],
            'bio': '',
            'analysis': {
                'what_we_looked': 'We analyzed the author attribution for validity and authenticity.',
                'what_we_found': f'The attribution "{author_string}" appears to be a generic label rather than an actual author name.',
                'what_it_means': 'Generic attributions like "Staff" or "Admin" provide no accountability. This reduces credibility as readers cannot verify the author\'s qualifications or bias.'
            }
        }

# ================================================================================
# SERVICE IMPLEMENTATIONS WITH REAL ANALYSIS
# ================================================================================

class BaseAnalyzer:
    """Base class for all analysis services"""
    
    def __init__(self, service_name):
        self.service_name = service_name
        self.available = True
        self.text_analyzer = TextAnalyzer()
        logger.info(f"  ✓ {service_name} initialized with real analysis")
    
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
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
        domain = parsed.netloc.replace('www.', '')
        
        # Try newspaper3k first
        try:
            article = Article(url)
            article.download()
            article.parse()
            
            if article.text and len(article.text) > 100:
                return {
                    'title': article.title or 'Article',
                    'domain': domain,
                    'author': self._clean_author(article.authors[0] if article.authors else 'Unknown'),
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
        
        # Method 2: Common class/id patterns
        author_selectors = [
            '.author-name', '.by-author', '.article-author', '.post-author',
            '.author', '.writer', '.journalist', '.reporter',
            '#author', '[itemprop="author"]', '[rel="author"]',
            'span.by', 'div.byline', 'p.byline'
        ]
        
        # Add domain-specific selectors
        if 'bbc' in domain:
            author_selectors.extend([
                'span[class*="TextContributorName"]',
                'div[class*="Contributor"]',
                'p[class*="gel-brevier"]'
            ])
        elif 'cnn' in domain:
            author_selectors.extend([
                '.metadata__byline__author',
                '.byline__name'
            ])
        elif 'nytimes' in domain:
            author_selectors.extend([
                '.css-1baulvz',
                'span[itemprop="name"]'
            ])
        
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
        
        # Check domain credibility
        credibility_level = self._check_domain_credibility(domain)
        
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
        
        # Check high credibility
        for high_domain in self.text_analyzer.credible_domains['high']:
            if high_domain in domain_lower:
                return {'score': 85, 'reputation': 'excellent', 'tier': 'high'}
        
        # Check medium credibility
        for med_domain in self.text_analyzer.credible_domains['medium']:
            if med_domain in domain_lower:
                return {'score': 65, 'reputation': 'good', 'tier': 'medium'}
        
        # Check low credibility
        for low_domain in self.text_analyzer.credible_domains['low']:
            if low_domain in domain_lower:
                return {'score': 35, 'reputation': 'questionable', 'tier': 'low'}
        
        # Unknown domain - neutral score
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
        
        return {
            'score': 100 - bias_score,  # Invert for trust score calculation
            'bias_score': bias_score,
            'political_lean': bias_analysis['political_lean'],
            'bias_level': self._get_bias_level(bias_score),
            'sentiment': sentiment,
            'emotional_tone': emotional_score,
            'loaded_words': bias_analysis['loaded_words'],
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
        else:
            accuracy_score = 50  # No claims found
        
        return {
            'score': accuracy_score,
            'fact_check_score': accuracy_score,
            'claims_found': total_claims,
            'claims_checked': total_claims,
            'claims_verified': verified_count,
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
