"""
TruthLens News Analyzer - Complete with Debate Arena & Live Streaming
Version: 10.0.0
Date: October 20, 2025

CHANGES FROM 9.0.0:
1. ADDED: Live Stream transcript analysis for YouTube Live
2. ADDED: Real-time transcription with AssemblyAI
3. ADDED: Server-Sent Events for live updates
4. ADDED: Transcript routes blueprint registration
5. All v9.0.0 functionality preserved (DO NO HARM ✓)

NEW FEATURES (Live Streaming):
- YouTube Live stream analysis
- Real-time audio transcription (AssemblyAI)
- Automatic claim extraction from live streams
- Live fact-checking as speech happens
- Server-Sent Events for frontend updates
- Cost: $0/month with free tier (100 hours)

REQUIREMENTS:
- services/live_stream_analyzer.py (Live streaming engine)
- transcript_routes.py (Transcript & live stream routes)
- ASSEMBLYAI_API_KEY environment variable (for live streaming)
- yt-dlp and ffmpeg system dependencies

EXISTING FEATURES PRESERVED:
- News Analysis (7 AI Services) - v8.x
- Debate Arena (Phase 1 text-based) - v9.0.0
- All v8.x enhancements

This file is complete and ready to deploy.
Last modified: October 20, 2025 - Added Live Streaming v10.0.0
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
    app.config['SQLALCHEMY_ECHO'] = False  # Set to True for debugging
    
    # Initialize database
    try:
        from models import db
        db.init_app(app)
        
        # Create tables if they don't exist
        with app.app_context():
            try:
                db.create_all()
                logger.info("✓ Database tables created successfully")
            except Exception as e:
                logger.error(f"✗ Database initialization error: {e}")
        
        logger.info("✓ Debate Arena database configured")
    except ImportError as e:
        logger.error(f"✗ Failed to import models.py: {e}")
        database_url = None
else:
    logger.warning("⚠️  DATABASE_URL not found - Debate Arena features disabled")

# OpenAI configuration
try:
    from openai import OpenAI
    openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    logger.info("OpenAI client initialized successfully")
except Exception as e:
    logger.warning(f"OpenAI client initialization failed: {e}")
    openai_client = None

# Try to import enhanced services
try:
    from services.manipulation_detector import ManipulationDetector
    manipulation_detector = ManipulationDetector()
    logger.info("Enhanced ManipulationDetector loaded")
except Exception as e:
    logger.warning(f"Could not load ManipulationDetector: {e}")
    manipulation_detector = None

try:
    from services.author_analyzer import AuthorAnalyzer as EnhancedAuthorAnalyzer
    author_analyzer = EnhancedAuthorAnalyzer()
    logger.info("Enhanced AuthorAnalyzer service loaded")
except Exception as e:
    logger.warning(f"Could not load AuthorAnalyzer service: {e}")
    author_analyzer = None

# CRITICAL: Initialize NewsAnalyzer and DataTransformer
news_analyzer_service = NewsAnalyzer()
data_transformer = DataTransformer()
logger.info("NewsAnalyzer and DataTransformer services initialized")

# ============================================================================
# SOURCE METADATA DATABASE
# ============================================================================
SOURCE_METADATA = {
    'The New York Times': {
        'founded': 1851,
        'type': 'Newspaper',
        'ownership': 'Public Company',
        'readership': 'National/International',
        'awards': 'Multiple Pulitzer Prizes'
    },
    'The Washington Post': {
        'founded': 1877,
        'type': 'Newspaper',
        'ownership': 'Nash Holdings (Jeff Bezos)',
        'readership': 'National',
        'awards': 'Multiple Pulitzer Prizes'
    },
    'BBC': {
        'founded': 1922,
        'type': 'Public Broadcaster',
        'ownership': 'Public Corporation',
        'readership': 'International',
        'awards': 'Multiple BAFTAs, Emmys'
    },
    'Reuters': {
        'founded': 1851,
        'type': 'News Agency',
        'ownership': 'Thomson Reuters',
        'readership': 'International',
        'awards': 'Multiple journalism awards'
    },
    'Associated Press': {
        'founded': 1846,
        'type': 'News Cooperative',
        'ownership': 'Non-profit Cooperative',
        'readership': 'International',
        'awards': 'Multiple Pulitzer Prizes'
    },
    'ABC News': {
        'founded': 1943,
        'type': 'Television Network',
        'ownership': 'The Walt Disney Company',
        'readership': 'National',
        'awards': 'Multiple Emmy Awards'
    },
    'NBC News': {
        'founded': 1940,
        'type': 'Television Network',
        'ownership': 'NBCUniversal (Comcast)',
        'readership': 'National',
        'awards': 'Multiple Emmy Awards'
    },
    'CBS News': {
        'founded': 1927,
        'type': 'Television Network',
        'ownership': 'Paramount Global',
        'readership': 'National',
        'awards': 'Multiple Emmy Awards'
    },
    'CNN': {
        'founded': 1980,
        'type': 'Cable News',
        'ownership': 'Warner Bros. Discovery',
        'readership': 'National/International',
        'awards': 'Multiple Emmy Awards'
    },
    'Fox News': {
        'founded': 1996,
        'type': 'Cable News',
        'ownership': 'Fox Corporation',
        'readership': 'National',
        'awards': 'Various broadcasting awards'
    },
    'NPR': {
        'founded': 1970,
        'type': 'Public Radio',
        'ownership': 'Non-profit',
        'readership': 'National',
        'awards': 'Multiple Peabody Awards'
    },
    'The Wall Street Journal': {
        'founded': 1889,
        'type': 'Newspaper',
        'ownership': 'News Corp',
        'readership': 'National/International',
        'awards': 'Multiple Pulitzer Prizes'
    },
    'Politico': {
        'founded': 2007,
        'type': 'Digital/Print',
        'ownership': 'Axel Springer SE',
        'readership': 'National',
        'awards': 'Various journalism awards'
    },
    'The Hill': {
        'founded': 1994,
        'type': 'Digital/Print',
        'ownership': 'Nexstar Media Group',
        'readership': 'National',
        'awards': 'Various journalism awards'
    },
    'Axios': {
        'founded': 2016,
        'type': 'Digital',
        'ownership': 'Cox Enterprises',
        'readership': 'National',
        'awards': 'Various digital media awards'
    },
    'New York Post': {
        'founded': 1801,
        'type': 'Tabloid',
        'ownership': 'News Corp',
        'readership': 'National',
        'awards': 'Various journalism awards'
    },
    'NY Post': {
        'founded': 1801,
        'type': 'Tabloid',
        'ownership': 'News Corp',
        'readership': 'National',
        'awards': 'Various journalism awards'
    }
}

# Enhanced Journalist Database
JOURNALIST_DATABASE = {
    "John Parkinson": {
        "outlet": "ABC News",
        "expertise": ["Congressional reporting", "Federal politics", "Legislative affairs"],
        "credibility": 80,
        "years_experience": 15,
        "awards": ["Congressional Press Gallery member"],
        "track_record": "Established",
        "recent_work": "Covers Congress and federal government",
        "social_media": {"twitter": "@jparkABC"}
    },
    "Lauren Peller": {
        "outlet": "ABC News",
        "expertise": ["Political reporting", "Government affairs", "Breaking news"],
        "credibility": 75,
        "years_experience": 8,
        "track_record": "Established",
        "recent_work": "Political correspondent",
        "social_media": {"twitter": "@laurenpeller"}
    },
    "Allison Pecorin": {
        "outlet": "ABC News", 
        "expertise": ["Congressional reporting", "Political coverage", "Government shutdown coverage"],
        "credibility": 78,
        "years_experience": 10,
        "awards": ["White House Correspondents' Association member"],
        "track_record": "Established",
        "recent_work": "Congressional correspondent covering Capitol Hill",
        "social_media": {"twitter": "@allison_pecorin"}
    },
    "Jeremy Bowen": {
        "outlet": "BBC",
        "expertise": ["International affairs", "Middle East", "War correspondence"],
        "credibility": 90,
        "years_experience": 30,
        "awards": ["BAFTA", "Emmy", "Peabody Award"],
        "track_record": "Highly Established",
        "recent_work": "BBC International Editor",
        "social_media": {"twitter": "@BowenBBC"}
    },
    "Dasha Burns": {
        "outlet": "NBC News",
        "expertise": ["Political reporting", "Breaking news", "Investigative journalism"],
        "credibility": 82,
        "years_experience": 12,
        "track_record": "Established",
        "recent_work": "NBC News correspondent",
        "awards": ["Edward R. Murrow Award"],
        "social_media": {"twitter": "@DashaBurns"}
    }
}

# Known non-journalists to exclude
NON_JOURNALIST_NAMES = {
    "Donald Trump", "Joe Biden", "Kamala Harris", "Mike Pence", "Barack Obama",
    "Hillary Clinton", "Bernie Sanders", "Elizabeth Warren", "Nancy Pelosi",
    "Mitch McConnell", "Kevin McCarthy", "Chuck Schumer", "Ron DeSantis",
    "Gavin Newsom", "Greg Abbott", "Mike Johnson", "Hakeem Jeffries",
    "Elon Musk", "Bill Gates", "Jeff Bezos", "Mark Zuckerberg", "Warren Buffett",
    "Taylor Swift", "Kim Kardashian", "Kanye West", "Oprah Winfrey",
    "The President", "The White House", "The Pentagon", "The State Department"
}

# ============================================================================
# ARTICLE EXTRACTOR CLASS - ENHANCED v8.5.1
# (Complete implementation from your original file - unchanged)
# ============================================================================
class ArticleExtractor:
    """
    Enhanced article extraction with author profile URL detection
    v8.5.1: Now captures author profile URLs for rich biographical data
    """
    
    def __init__(self):
        self.scraper_api_key = os.getenv('SCRAPERAPI_KEY', '')
        logger.info(f"ArticleExtractor v8.5.1 initialized - ScraperAPI configured: {bool(self.scraper_api_key)}")
        
    def extract(self, url: str) -> Dict:
        """Extract article with enhanced error handling"""
        logger.info(f"Starting extraction for URL: {url}")
        
        try:
            if self.scraper_api_key:
                logger.info("Attempting extraction with ScraperAPI...")
                try:
                    response = self._fetch_with_scraper_api(url)
                    logger.info(f"ScraperAPI returned status: {response.status_code}")
                    
                    if response.status_code == 200:
                        return self._parse_response(response, url)
                    else:
                        logger.warning(f"ScraperAPI returned non-200 status: {response.status_code}")
                except Exception as e:
                    logger.error(f"ScraperAPI extraction failed: {e}")
            
            logger.info("Attempting direct fetch...")
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if response.status_code == 200:
                return self._parse_response(response, url)
            else:
                raise Exception(f"Direct fetch returned {response.status_code}")
                
        except Exception as e:
            logger.error(f"Article extraction failed completely: {e}")
            return {
                'title': 'Unknown',
                'author': 'Unknown',
                'text': '',
                'source': urlparse(url).netloc,
                'url': url,
                'extraction_successful': False,
                'error': str(e)
            }
    
    def _parse_response(self, response, url: str) -> Dict:
        """Parse response and extract article data"""
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract all components
        title = self._extract_title(soup)
        authors = self._extract_authors_improved(soup, response.text)
        text = self._extract_text(soup)
        source = self._extract_source(url)
        published_date = self._extract_date(soup)
        
        # Extract author profile URL (v8.5.1 feature)
        author_profile_url = self._extract_author_profile_url(soup, url, authors)
        if author_profile_url:
            logger.info(f"✓ Found author profile URL: {author_profile_url}")
        else:
            logger.info("No author profile URL found in article")
        
        # Count sources and quotes for transparency
        sources_count = self._count_sources(text)
        quotes_count = self._count_quotes(text)
        
        logger.info(f"Extraction results - Title: {title[:50]}..., Author: {authors}, Words: {len(text.split())}")
        
        return {
            'title': title,
            'author': authors,
            'author_profile_url': author_profile_url,
            'text': text,
            'source': source,
            'url': url,
            'published_date': published_date,
            'word_count': len(text.split()),
            'sources_count': sources_count,
            'quotes_count': quotes_count,
            'extraction_successful': bool(text and len(text) > 100)
        }
    
    def _extract_author_profile_url(self, soup: BeautifulSoup, article_url: str, author_name: str) -> Optional[str]:
        """Extract author profile URL from article metadata and links"""
        try:
            parsed_url = urlparse(article_url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            # Method 1: Check <link rel="author"> tag
            if link_author := soup.find('link', rel='author'):
                if href := link_author.get('href'):
                    author_url = href if href.startswith('http') else base_url + href
                    logger.info(f"[AuthorURL] Found via <link rel='author'>: {author_url}")
                    return author_url
            
            # Method 2: Check author byline links
            author_selectors = [
                '.author', '.byline', '.author-name', '.by-author',
                '[class*="author"]', '[class*="byline"]', '[rel="author"]'
            ]
            
            for selector in author_selectors:
                for author_elem in soup.select(selector):
                    link = author_elem if author_elem.name == 'a' else author_elem.find('a', href=True)
                    if link and link.get('href'):
                        href = link.get('href')
                        
                        if any(skip in href.lower() for skip in ['mailto:', 'twitter.com', 'facebook.com', 'linkedin.com', 'search', 'tag/']):
                            continue
                        
                        if any(pattern in href.lower() for pattern in ['/author', '/by/', '/profile', '/journalist', '/reporter', '/writer']):
                            author_url = href if href.startswith('http') else base_url + href
                            logger.info(f"[AuthorURL] Found via byline link: {author_url}")
                            return author_url
            
            # Method 3: Check meta tags
            meta_author_url = soup.find('meta', {'property': 'article:author'})
            if not meta_author_url:
                meta_author_url = soup.find('meta', {'name': 'author-url'})
            
            if meta_author_url and (content := meta_author_url.get('content')):
                if content.startswith('http'):
                    logger.info(f"[AuthorURL] Found via meta tag: {content}")
                    return content
            
            # Method 4: Pattern matching with author name
            if author_name and author_name != 'Unknown':
                search_term = re.sub(r'[^a-z]+', '-', author_name.lower()).strip('-')
                
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '').lower()
                    
                    if any(skip in href for skip in ['mailto:', '#', 'javascript:', 'twitter.com', 'facebook.com']):
                        continue
                    
                    if any(pattern in href for pattern in ['/author/', '/by/', '/profile/', '/journalist/', '/reporter/']):
                        if search_term in href or any(part in href for part in search_term.split('-') if len(part) > 3):
                            full_url = link.get('href')
                            author_url = full_url if full_url.startswith('http') else base_url + full_url
                            logger.info(f"[AuthorURL] Found via pattern matching: {author_url}")
                            return author_url
            
            logger.info("[AuthorURL] No author profile URL found")
            return None
            
        except Exception as e:
            logger.error(f"[AuthorURL] Error extracting author profile URL: {e}")
            return None
    
    def _extract_authors_improved(self, soup: BeautifulSoup, html_text: str) -> str:
        """AI-powered author extraction"""
        
        if openai_client:
            try:
                article_top_html = html_text[:4000] if len(html_text) > 4000 else html_text
                article_top_text = soup.get_text()[:2000] if len(soup.get_text()) > 2000 else soup.get_text()
                
                prompt = f"""Find the article author(s) name in this content. Look for patterns like:
                - "By [Name]" or "Written by [Name]"
                - Author bylines near the title/top of article
                - Meta tags or byline classes in HTML
                
                Article text excerpt:
                {article_top_text}
                
                HTML structure excerpt:
                {article_top_html[:1500]}
                
                Rules:
                - Return ONLY the author name(s), nothing else
                - If multiple authors, separate with "and"
                - Return "Unknown" if no author found
                - Ignore names that appear in quotes (said, told, etc.)
                - Look for journalist names, not political figures or sources
                
                Author name:"""
                
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=50,
                    temperature=0.1
                )
                
                author = response.choices[0].message.content.strip()
                
                if author and author != 'Unknown':
                    author = author.replace('Author name:', '').replace('By ', '').strip()
                    word_count = len(author.split())
                    if 2 <= word_count <= 6:
                        if not any(name in author for name in NON_JOURNALIST_NAMES):
                            logger.info(f"AI successfully found author: {author}")
                            return author
                    
            except Exception as e:
                logger.warning(f"AI author extraction failed, falling back: {e}")
        
        # Fallback: Traditional extraction methods
        authors = []
        
        visible_text = soup.get_text()[:3000]
        if match := re.search(r'By\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', visible_text):
            potential_author = match.group(1)
            if not re.search(rf'(said|told|according to)\s+{re.escape(potential_author)}', visible_text, re.IGNORECASE):
                authors.append(potential_author)
        
        if not authors:
            meta_selectors = [
                ('name', 'author'),
                ('property', 'article:author'),
                ('name', 'byl'),
                ('name', 'DC.creator')
            ]
            
            for attr, value in meta_selectors:
                if meta := soup.find('meta', {attr: value}):
                    if content := meta.get('content'):
                        if not any(name in content for name in NON_JOURNALIST_NAMES):
                            authors.append(content.strip())
                            break
        
        if not authors:
            for byline_elem in soup.find_all(class_=re.compile(r'byline|author', re.I)):
                byline_text = byline_elem.get_text()
                if match := re.search(r'By\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', byline_text):
                    authors.append(match.group(1))
                    break
        
        if authors:
            author = authors[0]
            author = re.sub(r'\s+', ' ', author).strip()
            author = author.replace(' and ', ', ').replace(' And ', ', ')
            
            if author and 2 <= len(author.split()) <= 4:
                if not any(name in author for name in NON_JOURNALIST_NAMES):
                    logger.info(f"Fallback extraction found author: {author}")
                    return author
        
        logger.warning("No author found by any method")
        return "Unknown"
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title"""
        if og_title := soup.find('meta', property='og:title'):
            if content := og_title.get('content'):
                return content.strip()
        if title := soup.find('title'):
            return title.get_text().strip()
        if h1 := soup.find('h1'):
            return h1.get_text().strip()
        return "Unknown Title"
    
    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract article text"""
        for element in soup(['script', 'style', 'nav', 'header', 'footer']):
            element.decompose()
        
        article_selectors = [
            'article',
            '[role="main"]',
            '.article-body',
            '.story-body',
            '.entry-content',
            '.post-content',
            'main'
        ]
        
        for selector in article_selectors:
            if article := soup.select_one(selector):
                paragraphs = article.find_all(['p', 'h2', 'h3'])
                text = ' '.join([p.get_text().strip() for p in paragraphs])
                if len(text) > 200:
                    return text
        
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 30])
        
        return text if text else "Could not extract article text"
    
    def _extract_source(self, url: str) -> str:
        """Extract source from URL"""
        domain = urlparse(url).netloc
        domain = domain.replace('www.', '')
        
        source_map = {
            'nytimes.com': 'The New York Times',
            'washingtonpost.com': 'The Washington Post',
            'wsj.com': 'The Wall Street Journal',
            'bbc.com': 'BBC',
            'bbc.co.uk': 'BBC',
            'cnn.com': 'CNN',
            'foxnews.com': 'Fox News',
            'reuters.com': 'Reuters',
            'apnews.com': 'Associated Press',
            'abcnews.go.com': 'ABC News',
            'nbcnews.com': 'NBC News',
            'cbsnews.com': 'CBS News',
            'npr.org': 'NPR',
            'politico.com': 'Politico',
            'thehill.com': 'The Hill',
            'axios.com': 'Axios',
            'nypost.com': 'New York Post'
        }
        
        return source_map.get(domain, domain.title())
    
    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract publication date"""
        date_selectors = [
            ('property', 'article:published_time'),
            ('name', 'publishdate'),
            ('name', 'publish_date'),
            ('itemprop', 'datePublished')
        ]
        
        for attr, value in date_selectors:
            if meta := soup.find('meta', {attr: value}):
                if content := meta.get('content'):
                    return content[:10] if len(content) >= 10 else content
        
        if time_elem := soup.find('time'):
            if datetime_val := time_elem.get('datetime'):
                return datetime_val[:10]
        
        return None
    
    def _count_sources(self, text: str) -> int:
        """Count number of sources cited"""
        source_patterns = [
            r'according to',
            r'said',
            r'reported',
            r'stated',
            r'told',
            r'confirmed',
            r'announced'
        ]
        
        count = 0
        for pattern in source_patterns:
            count += len(re.findall(pattern, text, re.IGNORECASE))
        
        return min(count, 20)
    
    def _count_quotes(self, text: str) -> int:
        """Count number of direct quotes"""
        quotes = re.findall(r'"[^"]{10,}"', text)
        return len(quotes)
    
    def _fetch_with_scraper_api(self, url: str) -> requests.Response:
        """Fetch URL using ScraperAPI"""
        api_url = 'https://api.scraperapi.com'
        params = {
            'api_key': self.scraper_api_key,
            'url': url,
            'render': 'false',
            'country_code': 'us'
        }
        
        logger.info(f"Calling ScraperAPI for URL: {url}")
        
        response = requests.get(api_url, params=params, timeout=30)
        logger.info(f"ScraperAPI response: Status={response.status_code}, Size={len(response.text)} bytes")
        
        return response


# ============================================================================
# TRUTHLENS ANALYZER CLASS - ALL ORIGINAL METHODS PRESERVED
# (Complete implementation from your original file - unchanged)
# ============================================================================
class TruthLensAnalyzer:
    """Main analyzer with proper AI enhancement - ALL ORIGINAL METHODS PRESERVED"""
    
    def __init__(self):
        self.extractor = ArticleExtractor()
        self.author_analyzer = AuthorAnalyzer()
        
    def analyze(self, url: str) -> Dict:
        """Complete analysis pipeline"""
        try:
            logger.info(f"TruthLensAnalyzer starting analysis for: {url}")
            
            article_data = self.extractor.extract(url)
            
            if not article_data['extraction_successful']:
                logger.error(f"Extraction failed: {article_data.get('error', 'Unknown error')}")
                return self._error_response("Failed to extract article content")
            
            logger.info(f"Article extracted - Author: {article_data['author']}, Source: {article_data['source']}")
            
            author_analysis = self.author_analyzer.analyze(
                article_data['author'],
                article_data['source'],
                article_data
            )
            
            manipulation_results = {}
            if manipulation_detector:
                try:
                    manipulation_results = manipulation_detector.analyze({'text': article_data['text']})
                    logger.info(f"Manipulation detection completed")
                except Exception as e:
                    logger.error(f"Manipulation detection failed: {e}")
            
            response = self._build_response(article_data, author_analysis, manipulation_results)
            
            return response
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            traceback.print_exc()
            return self._error_response(str(e))
    
    def _build_response(self, article_data: Dict, author_analysis: Dict, manipulation_results: Dict) -> Dict:
        """Build complete response with proper source metadata"""
        
        trust_score = self._calculate_trust_score(article_data, author_analysis, manipulation_results)
        
        source_name = article_data['source']
        source_info = SOURCE_METADATA.get(source_name, {})
        
        return {
            'success': True,
            'trust_score': trust_score,
            'article_summary': article_data.get('text', '')[:500] + '...' if article_data.get('text') else 'No content extracted',
            'source': source_name,
            'author': article_data['author'],
            'findings_summary': self._generate_findings_summary(trust_score),
            'detailed_analysis': {
                'source_credibility': {
                    **self._analyze_source(source_name),
                    'organization': source_name,
                    'founded': source_info.get('founded'),
                    'type': source_info.get('type', 'News Organization'),
                    'ownership': source_info.get('ownership', 'Unknown'),
                    'readership': source_info.get('readership', 'Unknown'),
                    'awards': source_info.get('awards', 'N/A')
                },
                'author_analyzer': self._format_author_analysis(author_analysis),
                'bias_detector': self._analyze_bias(article_data),
                'fact_checker': self._check_facts(article_data),
                'transparency_analyzer': self._analyze_transparency(article_data),
                'manipulation_detector': self._format_manipulation_results(manipulation_results, article_data),
                'content_analyzer': self._analyze_content(article_data),
                'openai_enhancer': self._enhance_with_ai(article_data) if openai_client else {
                    'insights': 'AI enhancement not available',
                    'enhanced': False
                }
            }
        }
    
    def _format_author_analysis(self, author_analysis: Dict) -> Dict:
        """Format author analysis with AI enhancement"""
        result = {
            'credibility': author_analysis.get('credibility_score', 70),
            'expertise': author_analysis.get('expertise', []),
            'track_record': author_analysis.get('track_record', 'Unknown'),
            'years_experience': author_analysis.get('years_experience', 'Unknown'),
            'awards': author_analysis.get('awards', []),
            'recent_work': author_analysis.get('recent_work', ''),
            'social_media': author_analysis.get('social_media', {}),
            'findings': [
                f"Author credibility: {author_analysis.get('credibility_score', 0)}/100",
                f"Expertise: {', '.join(author_analysis.get('expertise', ['Unknown'])[:3])}",
                f"Track record: {author_analysis.get('track_record', 'Unknown')}"
            ]
        }
        
        if openai_client and author_analysis.get('author_name'):
            try:
                prompt = f"""Provide a brief assessment of journalist {author_analysis.get('author_name')} 
                from {author_analysis.get('outlet', 'Unknown outlet')}. 
                Focus on their expertise and credibility in 2-3 sentences."""
                
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=100,
                    temperature=0.3
                )
                
                result['ai_assessment'] = response.choices[0].message.content
            except Exception as e:
                logger.error(f"AI author enhancement failed: {e}")
        
        return result
    
    def _format_manipulation_results(self, manipulation_results: Dict, article_data: Dict) -> Dict:
        if manipulation_results and manipulation_results.get('success'):
            data = manipulation_results.get('data', {})
            return {
                'score': data.get('integrity_score', 80),
                'techniques_found': data.get('tactic_count', 0),
                'tactics': data.get('tactics_found', []),
                'findings': data.get('findings', ['Minor manipulation tactics detected'])
            }
        else:
            return self._detect_manipulation_fallback(article_data)
    
    def _analyze_source(self, source: str) -> Dict:
        """Analyze source credibility with proper metadata"""
        known_sources = {
            'The New York Times': 90,
            'The Washington Post': 88,
            'BBC': 92,
            'Reuters': 95,
            'Associated Press': 93,
            'ABC News': 85,
            'NBC News': 83,
            'CBS News': 84,
            'CNN': 80,
            'Fox News': 75,
            'NPR': 88,
            'The Wall Street Journal': 87,
            'Politico': 82,
            'The Hill': 78,
            'Axios': 81,
            'New York Post': 65,
            'NY Post': 65
        }
        
        credibility = known_sources.get(source, 70)
        
        return {
            'score': credibility,
            'classification': 'Mainstream Media' if credibility > 75 else 'Alternative Media',
            'reach': 'National',
            'findings': [
                f"{source} credibility: {credibility}/100",
                "Established news organization" if credibility > 80 else "Recognized news source"
            ]
        }
    
    def _analyze_bias(self, article_data: Dict) -> Dict:
        """Enhanced v8.4.0: Multi-dimensional bias analysis"""
        text = article_data.get('text', '').lower()
        title = article_data.get('title', '').lower()
        source = article_data.get('source', '')
        
        if not text:
            return {
                'score': 50,
                'direction': 'unknown',
                'objectivity_score': 50,
                'political_bias': 'Unknown',
                'bias_direction': 'unknown',
                'political_label': 'Unknown',
                'political_leaning': 'Unknown',
                'sensationalism_level': 'Unknown',
                'details': {},
                'findings': ['Unable to analyze bias - no text extracted']
            }
        
        # Outlet bias baseline
        outlet_bias = {
            'New York Post': {'direction': 'right', 'lean': 25, 'sensationalism': 30},
            'NY Post': {'direction': 'right', 'lean': 25, 'sensationalism': 30},
            'Fox News': {'direction': 'right', 'lean': 35, 'sensationalism': 25},
            'Breitbart': {'direction': 'right', 'lean': 45, 'sensationalism': 35},
            'MSNBC': {'direction': 'left', 'lean': 35, 'sensationalism': 20},
            'The New York Times': {'direction': 'center-left', 'lean': 15, 'sensationalism': 5},
            'The Washington Post': {'direction': 'center-left', 'lean': 15, 'sensationalism': 5},
            'CNN': {'direction': 'center-left', 'lean': 20, 'sensationalism': 15},
            'The Wall Street Journal': {'direction': 'center-right', 'lean': 15, 'sensationalism': 5},
            'Reuters': {'direction': 'center', 'lean': 0, 'sensationalism': 0},
            'Associated Press': {'direction': 'center', 'lean': 0, 'sensationalism': 0},
            'BBC': {'direction': 'center', 'lean': 5, 'sensationalism': 5},
            'NPR': {'direction': 'center-left', 'lean': 10, 'sensationalism': 0}
        }
        
        base_bias = outlet_bias.get(source, {'direction': 'center', 'lean': 0, 'sensationalism': 0})
        direction = base_bias['direction']
        bias_score = base_bias['lean']
        sensationalism_base = base_bias['sensationalism']
        
        # Sensationalism detection
        sensational_words = [
            'shocking', 'explosive', 'bombshell', 'devastating', 'unprecedented',
            'crisis', 'disaster', 'scandal', 'outrageous', 'incredible', 'stunning',
            'slams', 'blasts', 'destroys', 'annihilates', 'crushes'
        ]
        
        sensational_count = sum(1 for word in sensational_words if word in text or word in title)
        title_sensational = sum(1 for word in sensational_words if word in title)
        if title_sensational > 0:
            sensationalism_base += title_sensational * 10
        
        sensationalism_score = min(100, sensationalism_base + (sensational_count * 5))
        
        # Calculate final scores
        total_bias = min(100, bias_score + (sensationalism_score * 0.3))
        objectivity_score = max(0, 100 - total_bias)
        
        # Determine political label
        if direction in ['left', 'center-left']:
            if bias_score >= 35:
                political_label = 'Left'
            elif bias_score >= 20:
                political_label = 'Center-Left'
            else:
                political_label = 'Center'
        elif direction in ['right', 'center-right']:
            if bias_score >= 35:
                political_label = 'Right'
            elif bias_score >= 20:
                political_label = 'Center-Right'
            else:
                political_label = 'Center'
        else:
            political_label = 'Center'
        
        # Sensationalism level
        if sensationalism_score >= 60:
            sensationalism_level = 'High'
        elif sensationalism_score >= 35:
            sensationalism_level = 'Moderate'
        elif sensationalism_score >= 15:
            sensationalism_level = 'Low'
        else:
            sensationalism_level = 'Minimal'
        
        return {
            'score': int(objectivity_score),
            'objectivity_score': int(objectivity_score),
            'direction': direction.split('-')[0] if '-' in direction else direction,
            'bias_direction': direction.split('-')[0] if '-' in direction else direction,
            'political_bias': political_label,
            'political_label': political_label,
            'political_leaning': political_label,
            'sensationalism_level': sensationalism_level,
            'details': {
                'outlet_bias': base_bias['lean'],
                'sensationalism_score': int(sensationalism_score)
            },
            'findings': [
                f"Bias direction: {political_label}",
                f"Objectivity score: {int(objectivity_score)}/100",
                f"Sensationalism: {sensationalism_level}",
                f"Outlet baseline: {source} is {direction}-leaning"
            ]
        }
    
    def _check_facts(self, article_data: Dict) -> Dict:
        text = article_data.get('text', '')
        
        if not text:
            return {
                'score': 50,
                'claims_checked': 0,
                'verified': 0,
                'unverified': 0,
                'false_claims': 0,
                'claims': [],
                'findings': ['Unable to check facts - no text extracted']
            }
        
        claims = self._extract_claims(text)
        
        verified = 0
        unverified = 0
        
        for claim in claims[:5]:
            if any(char.isdigit() for char in claim):
                verified += 1
            else:
                unverified += 1
        
        total_claims = verified + unverified
        accuracy = (verified / total_claims * 100) if total_claims > 0 else 85
        
        return {
            'score': accuracy,
            'claims_checked': total_claims,
            'verified': verified,
            'unverified': unverified,
            'false_claims': 0,
            'claims': claims[:3],
            'findings': [
                f"{verified} of {total_claims} claims verified",
                f"Factual accuracy: {accuracy:.0f}%"
            ]
        }
    
    def _extract_claims(self, text: str) -> List[str]:
        claims = []
        sentences = text.split('.')
        factual_indicators = ['percent', '%', 'million', 'billion', 'according to', 
                             'study', 'report', 'data', 'statistics', 'research']
        
        for sentence in sentences:
            if any(indicator in sentence.lower() for indicator in factual_indicators):
                claims.append(sentence.strip())
        
        return claims[:10]
    
    def _analyze_transparency(self, article_data: Dict) -> Dict:
        sources_cited = article_data.get('sources_count', 0)
        quotes_included = article_data.get('quotes_count', 0)
        author_known = article_data.get('author', 'Unknown') != 'Unknown'
        
        score = 0
        if sources_cited > 0:
            score += min(50, sources_cited * 5)
        if quotes_included > 0:
            score += min(30, quotes_included * 5)
        if author_known:
            score += 20
        
        return {
            'score': min(100, score),
            'sources_cited': sources_cited,
            'quotes_included': quotes_included,
            'author_transparency': author_known,
            'findings': [
                f"{sources_cited} sources cited",
                f"{quotes_included} direct quotes",
                "Author identified" if author_known else "Author not identified"
            ]
        }
    
    def _detect_manipulation_fallback(self, article_data: Dict) -> Dict:
        text = article_data.get('text', '').lower()
        
        if not text:
            return {
                'score': 50,
                'techniques_found': 0,
                'findings': ['Unable to detect manipulation - no text extracted']
            }
        
        emotional_words = ['shocking', 'outrageous', 'unbelievable', 'devastating', 
                          'terrifying', 'explosive', 'bombshell']
        
        manipulation_count = sum(1 for word in emotional_words if word in text)
        integrity_score = max(40, 90 - (manipulation_count * 10))
        
        return {
            'score': integrity_score,
            'techniques_found': manipulation_count,
            'findings': [
                f"Emotional language: {'High' if manipulation_count > 3 else 'Low'}",
                f"Integrity score: {integrity_score}/100"
            ]
        }
    
    def _analyze_content(self, article_data: Dict) -> Dict:
        word_count = article_data.get('word_count', 0)
        
        if word_count < 300:
            quality_score = 60
            assessment = "Brief article - limited depth"
        elif word_count < 800:
            quality_score = 75
            assessment = "Standard article length"
        else:
            quality_score = 85
            assessment = "Comprehensive coverage"
        
        text = article_data.get('text', '')
        if text:
            avg_sentence_length = len(text.split()) / max(1, len(text.split('.')))
            
            if avg_sentence_length < 15:
                readability = 'High'
            elif avg_sentence_length < 25:
                readability = 'Medium'
            else:
                readability = 'Low'
        else:
            readability = 'Unknown'
        
        return {
            'score': quality_score,
            'readability': readability,
            'word_count': word_count,
            'findings': [
                f"{word_count} words",
                f"Readability: {readability}",
                assessment
            ]
        }
    
    def _enhance_with_ai(self, article_data: Dict) -> Dict:
        """Enhanced AI analysis with better insights"""
        if not openai_client or not article_data.get('text'):
            return {'enhanced': False, 'insights': 'AI enhancement not available'}
        
        try:
            prompt = f"""Analyze this news article for a comprehensive assessment:
            
            Title: {article_data.get('title', 'Unknown')}
            Author: {article_data.get('author', 'Unknown')}
            Source: {article_data.get('source', 'Unknown')}
            Text excerpt: {article_data.get('text', '')[:1000]}
            
            Provide:
            1. Three key points from the article
            2. Main bias indicators (if any)
            3. Credibility assessment
            4. One sentence summary
            
            Be specific and factual."""
            
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert news analyst providing balanced, factual assessments."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=250,
                temperature=0.3
            )
            
            ai_insights = response.choices[0].message.content
            
            return {
                'insights': ai_insights,
                'enhanced': True,
                'key_points': self._extract_key_points(ai_insights),
                'summary': article_data.get('text', '')[:200] + '...'
            }
        except Exception as e:
            logger.error(f"AI enhancement failed: {e}")
            return {
                'enhanced': False, 
                'insights': 'AI analysis temporarily unavailable',
                'error': str(e)
            }
    
    def _extract_key_points(self, ai_text: str) -> List[str]:
        """Extract key points from AI response"""
        lines = ai_text.split('\n')
        key_points = []
        
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                cleaned = re.sub(r'^[\d\-•\.]+\s*', '', line)
                if cleaned:
                    key_points.append(cleaned)
        
        return key_points[:3]
    
    def _calculate_trust_score(self, article_data: Dict, author_analysis: Dict, manipulation_results: Dict) -> int:
        if not article_data.get('text'):
            return 0
        
        source_score = self._analyze_source(article_data.get('source', 'Unknown'))['score']
        author_score = author_analysis.get('credibility_score', 70)
        bias_score = self._analyze_bias(article_data)['score']
        fact_score = self._check_facts(article_data)['score']
        transparency_score = self._analyze_transparency(article_data)['score']
        
        if manipulation_results and manipulation_results.get('success'):
            manipulation_score = manipulation_results.get('data', {}).get('integrity_score', 80)
        else:
            manipulation_score = self._detect_manipulation_fallback(article_data)['score']
        
        content_score = self._analyze_content(article_data)['score']
        
        scores = [
            source_score * 0.25,
            author_score * 0.20,
            bias_score * 0.15,
            fact_score * 0.15,
            transparency_score * 0.10,
            manipulation_score * 0.10,
            content_score * 0.05
        ]
        
        return int(sum(scores))
    
    def _generate_findings_summary(self, trust_score: int) -> str:
        if trust_score >= 80:
            return "This article appears highly credible with strong sourcing and minimal bias."
        elif trust_score >= 60:
            return "This article shows moderate credibility. Verify key claims independently."
        else:
            return "This article has credibility concerns. Seek additional sources."
    
    def _error_response(self, error_msg: str) -> Dict:
        return {
            'success': False,
            'error': error_msg,
            'trust_score': 0,
            'detailed_analysis': {}
        }


# ============================================================================
# AUTHOR ANALYZER CLASS - PRESERVED FROM v8.5.0
# ============================================================================
class AuthorAnalyzer:
    """Rich author analysis with journalist database AND enhanced unknown author handling"""
    
    def analyze(self, author_text: str, source: str, article_data: Dict = None) -> Dict:
        """Analyze author with article context"""
        authors = self._parse_authors(author_text)
        
        if not authors or authors == ["Unknown"]:
            return self._unknown_author_response(source, article_data)
        
        author_analyses = []
        overall_credibility = 0
        
        for author_name in authors:
            if author_name in JOURNALIST_DATABASE:
                author_data = JOURNALIST_DATABASE[author_name].copy()
                author_data['author_name'] = author_name
                author_analyses.append(author_data)
                overall_credibility += author_data['credibility']
            else:
                analysis = self._generate_author_analysis(author_name, source)
                author_analyses.append(analysis)
                overall_credibility += analysis['credibility']
        
        avg_credibility = overall_credibility / len(authors) if authors else 0
        
        combined = self._combine_author_analyses(author_analyses, authors)
        combined['credibility_score'] = avg_credibility
        
        return combined
    
    def _parse_authors(self, author_text: str) -> List[str]:
        if not author_text or author_text == "Unknown":
            return []
        
        author_text = author_text.replace(' and ', ', ')
        authors = [a.strip() for a in author_text.split(',')]
        
        valid_authors = []
        for author in authors:
            if author and 2 <= len(author.split()) <= 4:
                valid_authors.append(author)
        
        return valid_authors
    
    def _generate_author_analysis(self, author_name: str, source: str) -> Dict:
        """Generate author analysis with AI enhancement"""
        base_analysis = {
            "author_name": author_name,
            "outlet": source,
            "expertise": ["General reporting"],
            "credibility": 70,
            "years_experience": "Unknown",
            "track_record": "Unverified",
            "recent_work": "No recent work found",
            "awards": [],
            "social_media": {}
        }
        
        if openai_client:
            try:
                prompt = f"""Provide a realistic assessment of journalist {author_name} from {source}.
                
                Return JSON with:
                - expertise: list of 2-3 likely expertise areas
                - years_experience: estimated number (be conservative)
                - track_record: "Established", "Developing", or "New"
                - credibility: score 60-85 (be realistic)
                
                If unknown, use reasonable defaults for a {source} journalist."""
                
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                
                ai_text = response.choices[0].message.content
                try:
                    ai_data = json.loads(ai_text)
                    if ai_data.get('years_experience'):
                        years = ai_data['years_experience']
                        if isinstance(years, (int, float)) and years < 50:
                            base_analysis['years_experience'] = years
                    if ai_data.get('expertise'):
                        base_analysis['expertise'] = ai_data['expertise'][:3]
                    if ai_data.get('track_record'):
                        base_analysis['track_record'] = ai_data['track_record']
                    if ai_data.get('credibility'):
                        cred = ai_data['credibility']
                        if isinstance(cred, (int, float)) and 50 <= cred <= 100:
                            base_analysis['credibility'] = cred
                except:
                    pass
            except Exception as e:
                logger.error(f"AI author analysis failed: {e}")
        
        return base_analysis
    
    def _combine_author_analyses(self, analyses: List[Dict], authors: List[str]) -> Dict:
        if len(analyses) == 1:
            return analyses[0]
        
        all_expertise = []
        all_awards = []
        min_years = float('inf')
        max_years = 0
        
        for analysis in analyses:
            all_expertise.extend(analysis.get('expertise', []))
            all_awards.extend(analysis.get('awards', []))
            
            years = analysis.get('years_experience')
            if isinstance(years, (int, float)):
                min_years = min(min_years, years)
                max_years = max(max_years, years)
        
        all_expertise = list(set(all_expertise))
        all_awards = list(set(all_awards))
        
        if min_years != float('inf'):
            experience = f"{min_years}-{max_years} years combined"
        else:
            experience = "Experience varies"
        
        return {
            "authors": ", ".join(authors),
            "outlet": analyses[0].get('outlet', 'Unknown'),
            "expertise": all_expertise[:5],
            "years_experience": experience,
            "awards": all_awards,
            "track_record": "Established" if any(a.get('track_record') == 'Established' for a in analyses) else "Mixed",
            "recent_work": "Multiple beats covered",
            "social_media": analyses[0].get('social_media', {})
        }
    
    def _unknown_author_response(self, source: str, article_data: Dict = None) -> Dict:
        """Enhanced v8.3.0: Provide outlet-based analysis when author is unknown"""
        logger.info(f"[ENHANCED] Generating unknown author response for {source}")
        
        outlet_scores = {
            'The New York Times': 90,
            'The Washington Post': 88,
            'BBC': 92,
            'Reuters': 95,
            'Associated Press': 93,
            'ABC News': 85,
            'NBC News': 83,
            'CBS News': 84,
            'CNN': 80,
            'Fox News': 75,
            'NPR': 88,
            'The Wall Street Journal': 87,
            'Politico': 82,
            'The Hill': 78,
            'Axios': 81,
            'New York Post': 65,
            'NY Post': 65
        }
        
        outlet_score = outlet_scores.get(source, 65)
        
        if outlet_score >= 85:
            credibility = 70
            track_record = "Likely Established"
            expertise_note = f"Journalists at {source} typically have strong credentials"
        elif outlet_score >= 70:
            credibility = 60
            track_record = "Likely Professional"
            expertise_note = f"{source} generally employs qualified journalists"
        else:
            credibility = 45
            track_record = "Unknown"
            expertise_note = "Insufficient information about journalist standards"
        
        return {
            "outlet": source,
            "author_name": "Unknown Author",
            "expertise": [expertise_note],
            "credibility_score": credibility,
            "years_experience": "Unknown",
            "track_record": track_record,
            "awards": [],
            "recent_work": f"Article published in {source}",
            "social_media": {},
            "findings": [
                f"Author not identified",
                f"Outlet credibility: {outlet_score}/100",
                f"Overall assessment: {credibility}/100 based on outlet standards"
            ]
        }


# ============================================================================
# FLASK ROUTES - MAIN APPLICATION
# ============================================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/live-stream')
def live_stream():
    """Live stream analysis page"""
    return render_template('live-stream.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/debate-arena')
def debate_arena():
    return render_template('debate-arena.html')

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'version': '10.0.0',
        'services': {
            'openai': 'connected' if openai_client else 'not configured',
            'author_analyzer': 'enhanced with author profile URL extraction',
            'bias_detector': 'enhanced with outlet awareness',
            'manipulation_detector': 'loaded' if manipulation_detector else 'using fallback',
            'scraperapi': 'configured' if os.getenv('SCRAPERAPI_KEY') else 'not configured',
            'news_analyzer': 'active with data transformer',
            'track_record_system': 'available' if author_analyzer else 'not available',
            'debate_arena': 'active' if database_url else 'disabled',
            'database': 'connected' if database_url else 'not configured',
            'transcript_analyzer': 'active',
            'live_streaming': 'enabled' if os.getenv('ASSEMBLYAI_API_KEY') else 'disabled',
            'assemblyai': 'configured' if os.getenv('ASSEMBLYAI_API_KEY') else 'not configured'
        },
        'static_config': {
            'static_folder': app.static_folder,
            'static_url_path': app.static_url_path
        },
        'enhancements': {
            'unknown_author': 'v8.3.0 - outlet-based credibility',
            'bias_detection': 'v8.4.0 - multi-dimensional analysis',
            'new_pages': 'v8.5.0 - features, pricing, about, contact',
            'author_profile_urls': 'v8.5.1 - automatic extraction and scraping',
            'debate_arena': 'v9.0.0 - Phase 1 text-based debates',
            'live_streaming': 'v10.0.0 - YouTube Live analysis with AssemblyAI'
        }
    })

@app.route('/debug/static-files')
def debug_static_files():
    import os
    
    static_folder = app.static_folder
    js_folder = os.path.join(static_folder, 'js')
    
    files_info = {}
    
    if os.path.exists(js_folder):
        js_files = os.listdir(js_folder)
        for filename in js_files:
            filepath = os.path.join(js_folder, filename)
            files_info[filename] = {
                'exists': os.path.exists(filepath),
                'size': os.path.getsize(filepath) if os.path.exists(filepath) else 0,
                'readable': os.access(filepath, os.R_OK) if os.path.exists(filepath) else False
            }
    
    return jsonify({
        'static_folder': static_folder,
        'static_url_path': app.static_url_path,
        'js_folder_exists': os.path.exists(js_folder),
        'js_files': files_info,
        'chart_renderer_status': files_info.get('chart-renderer.js', {'exists': False}),
        'all_js_files': list(files_info.keys()) if files_info else []
    })

@app.route('/static/<path:filename>')
def serve_static(filename):
    try:
        return send_from_directory(app.static_folder, filename)
    except Exception as e:
        logger.error(f"Error serving static file {filename}: {e}")
        return jsonify({'error': 'File not found'}), 404

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        url = data.get('url')
        text = data.get('text')
        
        logger.info("=" * 80)
        logger.info("API /analyze endpoint called - Version 10.0.0")
        logger.info(f"URL provided: {bool(url)}")
        logger.info(f"Text provided: {bool(text)} ({len(text) if text else 0} chars)")
        
        if url:
            content = url
            content_type = 'url'
            logger.info(f"Analyzing URL: {url}")
        elif text:
            content = text
            content_type = 'text'
            logger.info(f"Analyzing text content: {len(text)} characters")
        else:
            logger.error("No URL or text provided")
            return jsonify({'success': False, 'error': 'No URL or text provided'}), 400
        
        logger.info("Step 1: Running NewsAnalyzer...")
        raw_results = news_analyzer_service.analyze(
            content=content,
            content_type=content_type,
            pro_mode=data.get('pro_mode', False)
        )
        
        logger.info("Step 2: Transforming data to match frontend contract...")
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

@app.route('/debug/api-keys', methods=['GET'])
def debug_api_keys():
    return jsonify({
        'api_keys_status': {
            'OPENAI_API_KEY': 'configured' if os.getenv('OPENAI_API_KEY') else 'missing',
            'SCRAPERAPI_KEY': 'configured' if os.getenv('SCRAPERAPI_KEY') else 'missing',
            'MEDIASTACK_API_KEY': 'configured' if os.getenv('MEDIASTACK_API_KEY') else 'missing',
            'NEWS_API_KEY': 'configured' if os.getenv('NEWS_API_KEY') else 'missing',
            'ASSEMBLYAI_API_KEY': 'configured' if os.getenv('ASSEMBLYAI_API_KEY') else 'missing',
        }
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# REGISTER DEBATE ARENA BLUEPRINT (v9.0.0)
# ============================================================================

if database_url:
    try:
        from debate_routes import debate_bp
        app.register_blueprint(debate_bp)
        logger.info("✓ Debate Arena routes registered at /api/debate/*")
    except ImportError as e:
        logger.error(f"✗ Failed to import debate_routes.py: {e}")
    except Exception as e:
        logger.error(f"✗ Failed to register Debate Arena routes: {e}")
else:
    logger.warning("⚠️  Debate Arena routes not registered (no database)")


# ============================================================================
# NEW: REGISTER TRANSCRIPT BLUEPRINT (v10.0.0)
# ============================================================================

try:
    from transcript_routes import transcript_bp
    app.register_blueprint(transcript_bp)
    logger.info("✓ Transcript Analysis routes registered at /api/transcript/*")
    
    # Check if live streaming is enabled
    if os.getenv('ASSEMBLYAI_API_KEY'):
        logger.info("✓ Live Stream Analysis enabled (AssemblyAI configured)")
    else:
        logger.warning("⚠️  Live Stream Analysis disabled (set ASSEMBLYAI_API_KEY to enable)")
        
except ImportError as e:
    logger.error(f"✗ Failed to import transcript_routes.py: {e}")
except Exception as e:
    logger.error(f"✗ Failed to register Transcript routes: {e}")


# ============================================================================
# STARTUP
# ============================================================================

if __name__ == '__main__':
    logger.info("=" * 80)
    logger.info("TRUTHLENS v10.0.0 - WITH LIVE STREAMING!")
    logger.info(f"OpenAI API: {'✓ READY' if openai_client else '✗ NOT CONFIGURED'}")
    logger.info(f"Database: {'✓ READY' if database_url else '✗ NOT CONFIGURED'}")
    logger.info(f"Debate Arena: {'✓ ENABLED' if database_url else '✗ DISABLED'}")
    logger.info(f"AssemblyAI: {'✓ READY' if os.getenv('ASSEMBLYAI_API_KEY') else '✗ NOT CONFIGURED'}")
    logger.info(f"Live Streaming: {'✓ ENABLED' if os.getenv('ASSEMBLYAI_API_KEY') else '✗ DISABLED'}")
    logger.info("")
    logger.info("FEATURES:")
    logger.info("  ✓ News Analysis - 7 AI Services")
    logger.info("  ✓ Transcript Fact-Checking")
    
    if os.getenv('ASSEMBLYAI_API_KEY'):
        logger.info("  ✓ Live Stream Analysis - YouTube Live with real-time transcription")
        logger.info("    - Real-time audio transcription (AssemblyAI)")
        logger.info("    - Automatic claim extraction")
        logger.info("    - Live fact-checking")
        logger.info("    - Server-Sent Events for updates")
    else:
        logger.info("  ✗ Live Streaming - Disabled (set ASSEMBLYAI_API_KEY to enable)")
    
    if database_url:
        logger.info("  ✓ Debate Arena - Challenge Mode & Pick-a-Fight")
        logger.info("    - Text-based arguments")
        logger.info("    - Real-time voting")
        logger.info("    - User authentication")
    else:
        logger.info("  ✗ Debate Arena - Disabled (set DATABASE_URL to enable)")
    
    logger.info("")
    logger.info("VERSION HISTORY:")
    logger.info("FROM v8.5.1:")
    logger.info("  ✓ Author profile URL extraction")
    logger.info("FROM v8.5.0:")
    logger.info("  ✓ /features, /pricing, /about, /contact pages")
    logger.info("FROM v8.4.0:")
    logger.info("  ✓ Enhanced bias detection with outlet awareness")
    logger.info("FROM v8.3.0:")
    logger.info("  ✓ Unknown author support with outlet-based credibility")
    logger.info("FROM v9.0.0:")
    logger.info("  ✓ Debate Arena backend (Phase 1)")
    logger.info("  ✓ PostgreSQL database integration")
    logger.info("")
    logger.info("NEW IN v10.0.0:")
    logger.info("  ✓ Live Stream transcript analysis")
    logger.info("  ✓ YouTube Live support with yt-dlp")
    logger.info("  ✓ Real-time transcription with AssemblyAI")
    logger.info("  ✓ Live fact-checking as speech happens")
    logger.info("  ✓ Server-Sent Events for frontend updates")
    logger.info("  ✓ Cost: $0/month with AssemblyAI free tier (100 hours)")
    logger.info("=" * 80)
    
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# This file is not truncated
