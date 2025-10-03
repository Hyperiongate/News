""""""
Article Extractor Service - v6.0 PRODUCTION FIXED
Date: September 29, 2025
Last Updated: September 29, 2025

THIS VERSION FIXES THE ACTUAL PROBLEM:
1. The service registry expects 'ArticleExtractor' class that takes NO arguments
2. The analyze method must handle BOTH url AND text extraction properly
3. Returns data in exact format pipeline expects
4. Has diagnostic logging to confirm it's loading
5. No circular dependencies or naming conflicts
6. Fallback returns score:58 - if you see that, this code isn't loading!

CRITICAL: This must replace services/article_extractor.py entirely
"""

import os
import sys
import re
import json
import time
import logging
import hashlib
from typing import Dict, Any, Optional, Tuple, List
from urllib.parse import urlparse, quote_plus
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from newspaper import Article, ArticleException

# CRITICAL DIAGNOSTIC: Confirm this file is loading
print("[ARTICLE_EXTRACTOR v6.0] Loading article_extractor.py...", file=sys.stderr)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress noisy loggers
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('newspaper').setLevel(logging.WARNING)

# Log that we're loading
logger.info("[ARTICLE_EXTRACTOR v6.0] Module loading started...")


class ArticleExtractorCore:
    """Core extraction logic"""
    
    VERSION = "6.0"
    
    def __init__(self):
        """Initialize the article extractor with API keys"""
        self.scraperapi_key = os.environ.get('SCRAPERAPI_KEY', '')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Cache for extracted articles
        self._cache = {}
        self._cache_ttl = 3600  # 1 hour
        
        logger.info(f"[EXTRACTOR v{self.VERSION}] Core initialized - ScraperAPI: {bool(self.scraperapi_key)}")
    
    def extract(self, url: str, use_scraperapi: bool = True) -> Dict[str, Any]:
        """Extract article from URL"""
        logger.info(f"[EXTRACTOR v{self.VERSION}] Extracting from URL: {url}")
        
        # Check cache
        cache_key = self._get_cache_key(url)
        if cache_key in self._cache:
            cache_entry = self._cache[cache_key]
            if time.time() - cache_entry['timestamp'] < self._cache_ttl:
                logger.info("Returning cached article")
                return cache_entry['data']
        
        # Try extraction methods
        result = None
        
        # Method 1: ScraperAPI
        if use_scraperapi and self.scraperapi_key:
            result = self._extract_with_scraperapi(url)
            if result and result.get('success'):
                logger.info(f"✓ ScraperAPI extraction successful - {result.get('word_count', 0)} words")
                self._cache_result(cache_key, result)
                return result
        
        # Method 2: Newspaper3k
        result = self._extract_with_newspaper(url)
        if result and result.get('success'):
            logger.info(f"✓ Newspaper extraction successful - {result.get('word_count', 0)} words")
            self._cache_result(cache_key, result)
            return result
        
        # Method 3: BeautifulSoup
        result = self._extract_with_beautifulsoup(url)
        if result and result.get('success'):
            logger.info(f"✓ BeautifulSoup extraction successful - {result.get('word_count', 0)} words")
            self._cache_result(cache_key, result)
            return result
        
        # All methods failed
        logger.error(f"All extraction methods failed for {url}")
        return self._create_error_response(url, "All extraction methods failed")
    
    def _extract_with_scraperapi(self, url: str) -> Dict[str, Any]:
        """Extract using ScraperAPI"""
        try:
            logger.info("Trying ScraperAPI...")
            
            api_url = "https://api.scraperapi.com"
            params = {
                'api_key': self.scraperapi_key,
                'url': url,
                'render': 'true',
                'country_code': 'us'
            }
            
            response = self.session.get(api_url, params=params, timeout=30)
            response.raise_for_status()
            
            html_content = response.text
            if not html_content or len(html_content) < 100:
                raise ValueError("Empty content from ScraperAPI")
            
            # Parse with newspaper
            article = Article(url)
            article.download(input_html=html_content)
            article.parse()
            
            if not article.text or len(article.text) < 100:
                return self._parse_html_content(html_content, url)
            
            return self._prepare_article_result(
                url=url,
                title=article.title,
                text=article.text,
                authors=article.authors,
                publish_date=article.publish_date,
                extraction_method='scraperapi'
            )
            
        except Exception as e:
            logger.error(f"ScraperAPI failed: {e}")
            return None
    
    def _extract_with_newspaper(self, url: str) -> Dict[str, Any]:
        """Extract using Newspaper3k"""
        try:
            logger.info("Trying Newspaper3k...")
            
            article = Article(url)
            article.config.browser_user_agent = self.session.headers['User-Agent']
            article.config.request_timeout = 20
            
            article.download()
            article.parse()
            
            if not article.text or len(article.text) < 100:
                raise ArticleException("Article text too short")
            
            try:
                article.nlp()
            except:
                pass
            
            return self._prepare_article_result(
                url=url,
                title=article.title,
                text=article.text,
                authors=article.authors,
                publish_date=article.publish_date,
                summary=article.summary if hasattr(article, 'summary') else None,
                extraction_method='newspaper'
            )
            
        except Exception as e:
            logger.error(f"Newspaper failed: {e}")
            return None
    
    def _extract_with_beautifulsoup(self, url: str) -> Dict[str, Any]:
        """Extract using BeautifulSoup"""
        try:
            logger.info("Trying BeautifulSoup...")
            
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            
            return self._parse_html_content(response.text, url)
            
        except Exception as e:
            logger.error(f"BeautifulSoup failed: {e}")
            return None
    
    def _parse_html_content(self, html: str, url: str) -> Dict[str, Any]:
        """Parse HTML content"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unwanted elements
            for script in soup(["script", "style", "meta", "noscript"]):
                script.decompose()
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract content
            content = self._extract_main_content(soup)
            
            # Extract author
            author = self._extract_author(soup, html)
            
            # Extract date
            publish_date = self._extract_publish_date(soup, html)
            
            if not content or len(content) < 100:
                raise ValueError("Content too short")
            
            return self._prepare_article_result(
                url=url,
                title=title,
                text=content,
                authors=[author] if author and author != "Unknown Author" else [],
                publish_date=publish_date,
                extraction_method='beautifulsoup'
            )
            
        except Exception as e:
            logger.error(f"HTML parsing failed: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title from HTML"""
        selectors = [
            'h1', 'h1.headline', 'h1.title', 'h1.entry-title',
            '[class*="headline"]', '[class*="title"]',
            'meta[property="og:title"]', 'meta[name="twitter:title"]', 'title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    title = element.get('content', '')
                else:
                    title = element.get_text(strip=True)
                
                if title and len(title) > 10:
                    return self._clean_text(title)
        
        return "Unknown Title"
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content"""
        selectors = [
            'article', '[role="main"]', '[class*="content-body"]',
            '[class*="article-body"]', '[class*="entry-content"]',
            '[class*="post-content"]', 'div.content', 'div.story-body', 'main'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                content_elem = elements[0]
                paragraphs = content_elem.find_all(['p', 'h2', 'h3', 'h4'])
                
                text_parts = []
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 20:
                        text_parts.append(text)
                
                if text_parts:
                    content = '\n\n'.join(text_parts)
                    if len(content) > 200:
                        return content
        
        # Fallback: all paragraphs
        all_paragraphs = soup.find_all('p')
        text_parts = []
        
        for p in all_paragraphs:
            text = p.get_text(strip=True)
            if text and len(text) > 30:
                text_parts.append(text)
        
        if text_parts:
            return '\n\n'.join(text_parts[:50])
        
        return soup.get_text(separator='\n', strip=True)
    
    def _extract_author(self, soup: BeautifulSoup, html: str) -> str:
        """Extract author"""
        # Meta tags
        meta_selectors = [
            'meta[name="author"]', 'meta[property="article:author"]',
            'meta[name="byl"]', 'meta[name="parsely-author"]'
        ]
        
        for selector in meta_selectors:
            element = soup.select_one(selector)
            if element:
                author = element.get('content', '')
                if author:
                    return self._clean_author_name(author)
        
        # Common selectors
        selectors = [
            '[class*="author-name"]', '[class*="by-author"]',
            '[class*="byline"]', '[rel="author"]', '.author', '.writer', 'span.by'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                author = element.get_text(strip=True)
                if author and len(author) > 2:
                    return self._clean_author_name(author)
        
        # JSON-LD
        json_lds = soup.find_all('script', type='application/ld+json')
        for json_ld in json_lds:
            try:
                data = json.loads(json_ld.string)
                if isinstance(data, dict) and 'author' in data:
                    author_data = data['author']
                    if isinstance(author_data, dict):
                        author = author_data.get('name', '')
                    else:
                        author = str(author_data)
                    if author:
                        return self._clean_author_name(author)
            except:
                continue
        
        return "Unknown Author"
    
    def _extract_publish_date(self, soup: BeautifulSoup, html: str) -> Optional[datetime]:
        """Extract publish date"""
        meta_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="publish_date"]', 'meta[name="parsely-pub-date"]',
            'meta[name="date"]'
        ]
        
        for selector in meta_selectors:
            element = soup.select_one(selector)
            if element:
                date_str = element.get('content', '')
                if date_str:
                    try:
                        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except:
                        continue
        
        time_element = soup.select_one('time[datetime]')
        if time_element:
            try:
                return datetime.fromisoformat(time_element['datetime'].replace('Z', '+00:00'))
            except:
                pass
        
        return None
    
    def _clean_text(self, text: str) -> str:
        """Clean text"""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[\r\n\t]', ' ', text)
        return text.strip()
    
    def _clean_author_name(self, author: str) -> str:
        """Clean author name"""
        if not author:
            return "Unknown Author"
        
        author = re.sub(r'^(by|By|BY)\s+', '', author)
        author = re.sub(r'^(written by|Written by)\s+', '', author, re.IGNORECASE)
        author = re.sub(r'\s+', ' ', author)
        author = re.sub(r'[<>"]', '', author)
        author = author.strip()
        
        if not author or len(author) < 2 or len(author) > 100:
            return "Unknown Author"
        
        return author
    
    def _prepare_article_result(
        self, url: str, title: str, text: str,
        authors: Optional[List[str]] = None, publish_date: Optional[datetime] = None,
        summary: Optional[str] = None, html: Optional[str] = None,
        extraction_method: str = 'unknown'
    ) -> Dict[str, Any]:
        """Prepare final result"""
        
        title = self._clean_text(title) if title else "Unknown Title"
        text = self._clean_text(text) if text else ""
        
        if authors:
            authors = [self._clean_author_name(a) for a in authors if a]
            authors = [a for a in authors if a != "Unknown Author"]
        
        author = authors[0] if authors else "Unknown Author"
        domain = urlparse(url).netloc.replace('www.', '')
        word_count = len(text.split()) if text else 0
        
        result = {
            'success': True,
            'url': url,
            'title': title,
            'text': text,
            'content': text,  # Duplicate for compatibility
            'author': author,
            'authors': authors or [author],
            'publish_date': publish_date.isoformat() if publish_date else None,
            'domain': domain,
            'word_count': word_count,
            'extraction_method': extraction_method,
            'extracted_at': datetime.now().isoformat(),
            'version': self.VERSION
        }
        
        if summary:
            result['summary'] = self._clean_text(summary)
        
        logger.info(f"[EXTRACTOR v{self.VERSION}] ✓ Extracted: {title[:50]}... ({word_count} words) by {author}")
        
        return result
    
    def _create_error_response(self, url: str, error_message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            'success': False,
            'url': url,
            'title': 'Unknown',
            'text': '',
            'content': '',
            'author': 'Unknown',
            'authors': [],
            'error': error_message,
            'extraction_method': 'none',
            'version': self.VERSION,
            'extracted_at': datetime.now().isoformat()
        }
    
    def _get_cache_key(self, url: str) -> str:
        """Generate cache key"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def _cache_result(self, key: str, result: Dict[str, Any]) -> None:
        """Cache result"""
        self._cache[key] = {
            'data': result,
            'timestamp': time.time()
        }
        
        if len(self._cache) > 100:
            sorted_items = sorted(
                self._cache.items(),
                key=lambda x: x[1]['timestamp']
            )
            self._cache = dict(sorted_items[-50:])
    
    def process_text_input(self, text: str, source: str = "direct_input") -> Dict[str, Any]:
        """Process direct text input"""
        logger.info(f"[EXTRACTOR v{self.VERSION}] Processing text input ({len(text)} chars)")
        
        lines = text.strip().split('\n')
        title = lines[0][:100] if lines else "Direct Text Input"
        cleaned_text = self._clean_text(text)
        
        return {
            'success': True,
            'url': source,
            'title': title,
            'text': cleaned_text,
            'content': cleaned_text,
            'author': 'Unknown Author',
            'authors': ['Unknown Author'],
            'publish_date': datetime.now().isoformat(),
            'domain': 'text_input',
            'word_count': len(cleaned_text.split()),
            'extraction_method': 'text_input',
            'extracted_at': datetime.now().isoformat(),
            'version': self.VERSION
        }


class ArticleExtractor:
    """
    Main class that service_registry expects
    CRITICAL: Must be named exactly 'ArticleExtractor'
    CRITICAL: Must take NO arguments in __init__
    CRITICAL: Must have analyze() method that works with pipeline
    """
    
    def __init__(self):
        """Initialize - NO ARGUMENTS as per service_registry requirements"""
        self.core = ArticleExtractorCore()
        self.is_available = True  # Required by service_registry
        logger.info(f"[ARTICLE_EXTRACTOR v6.0] ArticleExtractor initialized successfully")
        print("[ARTICLE_EXTRACTOR v6.0] Service ready for pipeline", file=sys.stderr)
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method called by the pipeline
        MUST handle both URL and text input
        MUST return in exact format expected by pipeline
        """
        logger.info(f"[ARTICLE_EXTRACTOR v6.0] analyze() called with keys: {list(data.keys())}")
        
        # Determine input type
        url = data.get('url', '')
        text = data.get('text', '') or data.get('content', '')
        
        try:
            # Handle URL input
            if url and url.startswith('http'):
                logger.info(f"[ARTICLE_EXTRACTOR v6.0] Extracting from URL: {url}")
                result = self.core.extract(url)
            # Handle text input
            elif text:
                logger.info(f"[ARTICLE_EXTRACTOR v6.0] Processing text input: {len(text)} chars")
                result = self.core.process_text_input(text)
            else:
                logger.error("[ARTICLE_EXTRACTOR v6.0] No valid URL or text provided")
                return {
                    'service': 'article_extractor',
                    'success': False,
                    'error': 'No URL or text provided',
                    'data': {
                        'text': '',
                        'title': 'Unknown',
                        'author': 'Unknown',
                        'domain': '',
                        'content': ''
                    },
                    'available': True,
                    'timestamp': time.time()
                }
            
            # Format response for pipeline
            if result.get('success'):
                logger.info(f"[ARTICLE_EXTRACTOR v6.0] SUCCESS - Extracted {result.get('word_count', 0)} words")
                return {
                    'service': 'article_extractor',
                    'success': True,
                    'data': {
                        'text': result.get('text', ''),
                        'content': result.get('text', ''),  # Duplicate for compatibility
                        'title': result.get('title', 'Unknown'),
                        'author': result.get('author', 'Unknown'),
                        'domain': result.get('domain', ''),
                        'url': url or result.get('url', ''),
                        'word_count': result.get('word_count', 0),
                        'extraction_method': result.get('extraction_method', 'unknown'),
                        'publish_date': result.get('publish_date'),
                        'authors': result.get('authors', [])
                    },
                    'available': True,
                    'timestamp': time.time()
                }
            else:
                logger.error(f"[ARTICLE_EXTRACTOR v6.0] FAILED - {result.get('error', 'Unknown error')}")
                return {
                    'service': 'article_extractor',
                    'success': False,
                    'error': result.get('error', 'Extraction failed'),
                    'data': {
                        'text': '',
                        'content': '',
                        'title': 'Unknown',
                        'author': 'Unknown',
                        'domain': '',
                        'url': url
                    },
                    'available': True,
                    'timestamp': time.time()
                }
                
        except Exception as e:
            logger.error(f"[ARTICLE_EXTRACTOR v6.0] Exception in analyze: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'service': 'article_extractor',
                'success': False,
                'error': str(e),
                'data': {
                    'text': '',
                    'content': '',
                    'title': 'Unknown',
                    'author': 'Unknown',
                    'domain': '',
                    'url': url
                },
                'available': True,
                'timestamp': time.time()
            }
    
    def _check_availability(self) -> bool:
        """Check if service is available"""
        return True
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        return {
            'name': 'article_extractor',
            'version': '6.0',
            'available': self.is_available,
            'description': 'Extracts article content from URLs or processes text input',
            'scraperapi_configured': bool(self.core.scraperapi_key)
        }


# Module-level diagnostic
logger.info("[ARTICLE_EXTRACTOR v6.0] Module loaded completely")
print("[ARTICLE_EXTRACTOR v6.0] Module ready", file=sys.stderr)


# Test function
if __name__ == "__main__":
    print("\n" + "="*80)
    print("TESTING ARTICLE EXTRACTOR v6.0")
    print("="*80)
    
    # Test instantiation
    print("\n1. Testing ArticleExtractor instantiation...")
    try:
        extractor = ArticleExtractor()
        print("   ✓ ArticleExtractor created successfully")
        print(f"   ✓ Available: {extractor.is_available}")
    except Exception as e:
        print(f"   ✗ Failed to create ArticleExtractor: {e}")
        sys.exit(1)
    
    # Test with sample URL
    test_url = "https://www.reuters.com/"
    print(f"\n2. Testing URL extraction: {test_url}")
    
    result = extractor.analyze({'url': test_url})
    
    if result['success']:
        print(f"   ✓ Extraction successful")
        print(f"   ✓ Title: {result['data']['title'][:60]}...")
        print(f"   ✓ Author: {result['data']['author']}")
        print(f"   ✓ Word Count: {result['data']['word_count']}")
        print(f"   ✓ Text preview: {result['data']['text'][:100]}...")
    else:
        print(f"   ✗ Extraction failed: {result.get('error')}")
    
    # Test with text input
    print("\n3. Testing text input processing...")
    test_text = "This is a test article.\n\nIt has multiple paragraphs.\n\nAnd some content to analyze."
    
    result = extractor.analyze({'text': test_text})
    
    if result['success']:
        print(f"   ✓ Text processing successful")
        print(f"   ✓ Word count: {result['data']['word_count']}")
    else:
        print(f"   ✗ Text processing failed: {result.get('error')}")
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)
Article Extractor Service - v6.0 PRODUCTION FIXED
Date: September 29, 2025
Last Updated: September 29, 2025

THIS VERSION FIXES THE ACTUAL PROBLEM:
1. The service registry expects 'ArticleExtractor' class that takes NO arguments
2. The analyze method must handle BOTH url AND text extraction properly
3. Returns data in exact format pipeline expects
4. Has diagnostic logging to confirm it's loading
5. No circular dependencies or naming conflicts
6. Fallback returns score:58 - if you see that, this code isn't loading!

CRITICAL: This must replace services/article_extractor.py entirely
"""

import os
import sys
import re
import json
import time
import logging
import hashlib
from typing import Dict, Any, Optional, Tuple, List
from urllib.parse import urlparse, quote_plus
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from newspaper import Article, ArticleException

# CRITICAL DIAGNOSTIC: Confirm this file is loading
print("[ARTICLE_EXTRACTOR v6.0] Loading article_extractor.py...", file=sys.stderr)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress noisy loggers
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('newspaper').setLevel(logging.WARNING)

# Log that we're loading
logger.info("[ARTICLE_EXTRACTOR v6.0] Module loading started...")


class ArticleExtractorCore:
    """Core extraction logic"""
    
    VERSION = "6.0"
    
    def __init__(self):
        """Initialize the article extractor with API keys"""
        self.scraperapi_key = os.environ.get('SCRAPERAPI_KEY', '')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Cache for extracted articles
        self._cache = {}
        self._cache_ttl = 3600  # 1 hour
        
        logger.info(f"[EXTRACTOR v{self.VERSION}] Core initialized - ScraperAPI: {bool(self.scraperapi_key)}")
    
    def extract(self, url: str, use_scraperapi: bool = True) -> Dict[str, Any]:
        """Extract article from URL"""
        logger.info(f"[EXTRACTOR v{self.VERSION}] Extracting from URL: {url}")
        
        # Check cache
        cache_key = self._get_cache_key(url)
        if cache_key in self._cache:
            cache_entry = self._cache[cache_key]
            if time.time() - cache_entry['timestamp'] < self._cache_ttl:
                logger.info("Returning cached article")
                return cache_entry['data']
        
        # Try extraction methods
        result = None
        
        # Method 1: ScraperAPI
        if use_scraperapi and self.scraperapi_key:
            result = self._extract_with_scraperapi(url)
            if result and result.get('success'):
                logger.info(f"✓ ScraperAPI extraction successful - {result.get('word_count', 0)} words")
                self._cache_result(cache_key, result)
                return result
        
        # Method 2: Newspaper3k
        result = self._extract_with_newspaper(url)
        if result and result.get('success'):
            logger.info(f"✓ Newspaper extraction successful - {result.get('word_count', 0)} words")
            self._cache_result(cache_key, result)
            return result
        
        # Method 3: BeautifulSoup
        result = self._extract_with_beautifulsoup(url)
        if result and result.get('success'):
            logger.info(f"✓ BeautifulSoup extraction successful - {result.get('word_count', 0)} words")
            self._cache_result(cache_key, result)
            return result
        
        # All methods failed
        logger.error(f"All extraction methods failed for {url}")
        return self._create_error_response(url, "All extraction methods failed")
    
    def _extract_with_scraperapi(self, url: str) -> Dict[str, Any]:
        """Extract using ScraperAPI"""
        try:
            logger.info("Trying ScraperAPI...")
            
            api_url = "https://api.scraperapi.com"
            params = {
                'api_key': self.scraperapi_key,
                'url': url,
                'render': 'true',
                'country_code': 'us'
            }
            
            response = self.session.get(api_url, params=params, timeout=30)
            response.raise_for_status()
            
            html_content = response.text
            if not html_content or len(html_content) < 100:
                raise ValueError("Empty content from ScraperAPI")
            
            # Parse with newspaper
            article = Article(url)
            article.download(input_html=html_content)
            article.parse()
            
            if not article.text or len(article.text) < 100:
                return self._parse_html_content(html_content, url)
            
            return self._prepare_article_result(
                url=url,
                title=article.title,
                text=article.text,
                authors=article.authors,
                publish_date=article.publish_date,
                extraction_method='scraperapi'
            )
            
        except Exception as e:
            logger.error(f"ScraperAPI failed: {e}")
            return None
    
    def _extract_with_newspaper(self, url: str) -> Dict[str, Any]:
        """Extract using Newspaper3k"""
        try:
            logger.info("Trying Newspaper3k...")
            
            article = Article(url)
            article.config.browser_user_agent = self.session.headers['User-Agent']
            article.config.request_timeout = 20
            
            article.download()
            article.parse()
            
            if not article.text or len(article.text) < 100:
                raise ArticleException("Article text too short")
            
            try:
                article.nlp()
            except:
                pass
            
            return self._prepare_article_result(
                url=url,
                title=article.title,
                text=article.text,
                authors=article.authors,
                publish_date=article.publish_date,
                summary=article.summary if hasattr(article, 'summary') else None,
                extraction_method='newspaper'
            )
            
        except Exception as e:
            logger.error(f"Newspaper failed: {e}")
            return None
    
    def _extract_with_beautifulsoup(self, url: str) -> Dict[str, Any]:
        """Extract using BeautifulSoup"""
        try:
            logger.info("Trying BeautifulSoup...")
            
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            
            return self._parse_html_content(response.text, url)
            
        except Exception as e:
            logger.error(f"BeautifulSoup failed: {e}")
            return None
    
    def _parse_html_content(self, html: str, url: str) -> Dict[str, Any]:
        """Parse HTML content"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unwanted elements
            for script in soup(["script", "style", "meta", "noscript"]):
                script.decompose()
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract content
            content = self._extract_main_content(soup)
            
            # Extract author
            author = self._extract_author(soup, html)
            
            # Extract date
            publish_date = self._extract_publish_date(soup, html)
            
            if not content or len(content) < 100:
                raise ValueError("Content too short")
            
            return self._prepare_article_result(
                url=url,
                title=title,
                text=content,
                authors=[author] if author and author != "Unknown Author" else [],
                publish_date=publish_date,
                extraction_method='beautifulsoup'
            )
            
        except Exception as e:
            logger.error(f"HTML parsing failed: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title from HTML"""
        selectors = [
            'h1', 'h1.headline', 'h1.title', 'h1.entry-title',
            '[class*="headline"]', '[class*="title"]',
            'meta[property="og:title"]', 'meta[name="twitter:title"]', 'title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    title = element.get('content', '')
                else:
                    title = element.get_text(strip=True)
                
                if title and len(title) > 10:
                    return self._clean_text(title)
        
        return "Unknown Title"
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content"""
        selectors = [
            'article', '[role="main"]', '[class*="content-body"]',
            '[class*="article-body"]', '[class*="entry-content"]',
            '[class*="post-content"]', 'div.content', 'div.story-body', 'main'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                content_elem = elements[0]
                paragraphs = content_elem.find_all(['p', 'h2', 'h3', 'h4'])
                
                text_parts = []
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 20:
                        text_parts.append(text)
                
                if text_parts:
                    content = '\n\n'.join(text_parts)
                    if len(content) > 200:
                        return content
        
        # Fallback: all paragraphs
        all_paragraphs = soup.find_all('p')
        text_parts = []
        
        for p in all_paragraphs:
            text = p.get_text(strip=True)
            if text and len(text) > 30:
                text_parts.append(text)
        
        if text_parts:
            return '\n\n'.join(text_parts[:50])
        
        return soup.get_text(separator='\n', strip=True)
    
    def _extract_author(self, soup: BeautifulSoup, html: str) -> str:
        """Extract author"""
        # Meta tags
        meta_selectors = [
            'meta[name="author"]', 'meta[property="article:author"]',
            'meta[name="byl"]', 'meta[name="parsely-author"]'
        ]
        
        for selector in meta_selectors:
            element = soup.select_one(selector)
            if element:
                author = element.get('content', '')
                if author:
                    return self._clean_author_name(author)
        
        # Common selectors
        selectors = [
            '[class*="author-name"]', '[class*="by-author"]',
            '[class*="byline"]', '[rel="author"]', '.author', '.writer', 'span.by'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                author = element.get_text(strip=True)
                if author and len(author) > 2:
                    return self._clean_author_name(author)
        
        # JSON-LD
        json_lds = soup.find_all('script', type='application/ld+json')
        for json_ld in json_lds:
            try:
                data = json.loads(json_ld.string)
                if isinstance(data, dict) and 'author' in data:
                    author_data = data['author']
                    if isinstance(author_data, dict):
                        author = author_data.get('name', '')
                    else:
                        author = str(author_data)
                    if author:
                        return self._clean_author_name(author)
            except:
                continue
        
        return "Unknown Author"
    
    def _extract_publish_date(self, soup: BeautifulSoup, html: str) -> Optional[datetime]:
        """Extract publish date"""
        meta_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="publish_date"]', 'meta[name="parsely-pub-date"]',
            'meta[name="date"]'
        ]
        
        for selector in meta_selectors:
            element = soup.select_one(selector)
            if element:
                date_str = element.get('content', '')
                if date_str:
                    try:
                        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except:
                        continue
        
        time_element = soup.select_one('time[datetime]')
        if time_element:
            try:
                return datetime.fromisoformat(time_element['datetime'].replace('Z', '+00:00'))
            except:
                pass
        
        return None
    
    def _clean_text(self, text: str) -> str:
        """Clean text"""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[\r\n\t]', ' ', text)
        return text.strip()
    
    def _clean_author_name(self, author: str) -> str:
        """Clean author name"""
        if not author:
            return "Unknown Author"
        
        author = re.sub(r'^(by|By|BY)\s+', '', author)
        author = re.sub(r'^(written by|Written by)\s+', '', author, re.IGNORECASE)
        author = re.sub(r'\s+', ' ', author)
        author = re.sub(r'[<>"]', '', author)
        author = author.strip()
        
        if not author or len(author) < 2 or len(author) > 100:
            return "Unknown Author"
        
        return author
    
    def _prepare_article_result(
        self, url: str, title: str, text: str,
        authors: Optional[List[str]] = None, publish_date: Optional[datetime] = None,
        summary: Optional[str] = None, html: Optional[str] = None,
        extraction_method: str = 'unknown'
    ) -> Dict[str, Any]:
        """Prepare final result"""
        
        title = self._clean_text(title) if title else "Unknown Title"
        text = self._clean_text(text) if text else ""
        
        if authors:
            authors = [self._clean_author_name(a) for a in authors if a]
            authors = [a for a in authors if a != "Unknown Author"]
        
        author = authors[0] if authors else "Unknown Author"
        domain = urlparse(url).netloc.replace('www.', '')
        word_count = len(text.split()) if text else 0
        
        result = {
            'success': True,
            'url': url,
            'title': title,
            'text': text,
            'content': text,  # Duplicate for compatibility
            'author': author,
            'authors': authors or [author],
            'publish_date': publish_date.isoformat() if publish_date else None,
            'domain': domain,
            'word_count': word_count,
            'extraction_method': extraction_method,
            'extracted_at': datetime.now().isoformat(),
            'version': self.VERSION
        }
        
        if summary:
            result['summary'] = self._clean_text(summary)
        
        logger.info(f"[EXTRACTOR v{self.VERSION}] ✓ Extracted: {title[:50]}... ({word_count} words) by {author}")
        
        return result
    
    def _create_error_response(self, url: str, error_message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            'success': False,
            'url': url,
            'title': 'Unknown',
            'text': '',
            'content': '',
            'author': 'Unknown',
            'authors': [],
            'error': error_message,
            'extraction_method': 'none',
            'version': self.VERSION,
            'extracted_at': datetime.now().isoformat()
        }
    
    def _get_cache_key(self, url: str) -> str:
        """Generate cache key"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def _cache_result(self, key: str, result: Dict[str, Any]) -> None:
        """Cache result"""
        self._cache[key] = {
            'data': result,
            'timestamp': time.time()
        }
        
        if len(self._cache) > 100:
            sorted_items = sorted(
                self._cache.items(),
                key=lambda x: x[1]['timestamp']
            )
            self._cache = dict(sorted_items[-50:])
    
    def process_text_input(self, text: str, source: str = "direct_input") -> Dict[str, Any]:
        """Process direct text input"""
        logger.info(f"[EXTRACTOR v{self.VERSION}] Processing text input ({len(text)} chars)")
        
        lines = text.strip().split('\n')
        title = lines[0][:100] if lines else "Direct Text Input"
        cleaned_text = self._clean_text(text)
        
        return {
            'success': True,
            'url': source,
            'title': title,
            'text': cleaned_text,
            'content': cleaned_text,
            'author': 'Unknown Author',
            'authors': ['Unknown Author'],
            'publish_date': datetime.now().isoformat(),
            'domain': 'text_input',
            'word_count': len(cleaned_text.split()),
            'extraction_method': 'text_input',
            'extracted_at': datetime.now().isoformat(),
            'version': self.VERSION
        }


class ArticleExtractor:
    """
    Main class that service_registry expects
    CRITICAL: Must be named exactly 'ArticleExtractor'
    CRITICAL: Must take NO arguments in __init__
    CRITICAL: Must have analyze() method that works with pipeline
    """
    
    def __init__(self):
        """Initialize - NO ARGUMENTS as per service_registry requirements"""
        self.core = ArticleExtractorCore()
        self.is_available = True  # Required by service_registry
        logger.info(f"[ARTICLE_EXTRACTOR v6.0] ArticleExtractor initialized successfully")
        print("[ARTICLE_EXTRACTOR v6.0] Service ready for pipeline", file=sys.stderr)
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method called by the pipeline
        MUST handle both URL and text input
        MUST return in exact format expected by pipeline
        """
        logger.info(f"[ARTICLE_EXTRACTOR v6.0] analyze() called with keys: {list(data.keys())}")
        
        # Determine input type
        url = data.get('url', '')
        text = data.get('text', '') or data.get('content', '')
        
        try:
            # Handle URL input
            if url and url.startswith('http'):
                logger.info(f"[ARTICLE_EXTRACTOR v6.0] Extracting from URL: {url}")
                result = self.core.extract(url)
            # Handle text input
            elif text:
                logger.info(f"[ARTICLE_EXTRACTOR v6.0] Processing text input: {len(text)} chars")
                result = self.core.process_text_input(text)
            else:
                logger.error("[ARTICLE_EXTRACTOR v6.0] No valid URL or text provided")
                return {
                    'service': 'article_extractor',
                    'success': False,
                    'error': 'No URL or text provided',
                    'data': {
                        'text': '',
                        'title': 'Unknown',
                        'author': 'Unknown',
                        'domain': '',
                        'content': ''
                    },
                    'available': True,
                    'timestamp': time.time()
                }
            
            # Format response for pipeline
            if result.get('success'):
                logger.info(f"[ARTICLE_EXTRACTOR v6.0] SUCCESS - Extracted {result.get('word_count', 0)} words")
                return {
                    'service': 'article_extractor',
                    'success': True,
                    'data': {
                        'text': result.get('text', ''),
                        'content': result.get('text', ''),  # Duplicate for compatibility
                        'title': result.get('title', 'Unknown'),
                        'author': result.get('author', 'Unknown'),
                        'domain': result.get('domain', ''),
                        'url': url or result.get('url', ''),
                        'word_count': result.get('word_count', 0),
                        'extraction_method': result.get('extraction_method', 'unknown'),
                        'publish_date': result.get('publish_date'),
                        'authors': result.get('authors', [])
                    },
                    'available': True,
                    'timestamp': time.time()
                }
            else:
                logger.error(f"[ARTICLE_EXTRACTOR v6.0] FAILED - {result.get('error', 'Unknown error')}")
                return {
                    'service': 'article_extractor',
                    'success': False,
                    'error': result.get('error', 'Extraction failed'),
                    'data': {
                        'text': '',
                        'content': '',
                        'title': 'Unknown',
                        'author': 'Unknown',
                        'domain': '',
                        'url': url
                    },
                    'available': True,
                    'timestamp': time.time()
                }
                
        except Exception as e:
            logger.error(f"[ARTICLE_EXTRACTOR v6.0] Exception in analyze: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'service': 'article_extractor',
                'success': False,
                'error': str(e),
                'data': {
                    'text': '',
                    'content': '',
                    'title': 'Unknown',
                    'author': 'Unknown',
                    'domain': '',
                    'url': url
                },
                'available': True,
                'timestamp': time.time()
            }
    
    def _check_availability(self) -> bool:
        """Check if service is available"""
        return True
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        return {
            'name': 'article_extractor',
            'version': '6.0',
            'available': self.is_available,
            'description': 'Extracts article content from URLs or processes text input',
            'scraperapi_configured': bool(self.core.scraperapi_key)
        }


# Module-level diagnostic
logger.info("[ARTICLE_EXTRACTOR v6.0] Module loaded completely")
print("[ARTICLE_EXTRACTOR v6.0] Module ready", file=sys.stderr)


# Test function
if __name__ == "__main__":
    print("\n" + "="*80)
    print("TESTING ARTICLE EXTRACTOR v6.0")
    print("="*80)
    
    # Test instantiation
    print("\n1. Testing ArticleExtractor instantiation...")
    try:
        extractor = ArticleExtractor()
        print("   ✓ ArticleExtractor created successfully")
        print(f"   ✓ Available: {extractor.is_available}")
    except Exception as e:
        print(f"   ✗ Failed to create ArticleExtractor: {e}")
        sys.exit(1)
    
    # Test with sample URL
    test_url = "https://www.reuters.com/"
    print(f"\n2. Testing URL extraction: {test_url}")
    
    result = extractor.analyze({'url': test_url})
    
    if result['success']:
        print(f"   ✓ Extraction successful")
        print(f"   ✓ Title: {result['data']['title'][:60]}...")
        print(f"   ✓ Author: {result['data']['author']}")
        print(f"   ✓ Word Count: {result['data']['word_count']}")
        print(f"   ✓ Text preview: {result['data']['text'][:100]}...")
    else:
        print(f"   ✗ Extraction failed: {result.get('error')}")
    
    # Test with text input
    print("\n3. Testing text input processing...")
    test_text = "This is a test article.\n\nIt has multiple paragraphs.\n\nAnd some content to analyze."
    
    result = extractor.analyze({'text': test_text})
    
    if result['success']:
        print(f"   ✓ Text processing successful")
        print(f"   ✓ Word count: {result['data']['word_count']}")
    else:
        print(f"   ✗ Text processing failed: {result.get('error')}")
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)
