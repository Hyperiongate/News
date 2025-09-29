"""
Article Extractor Service - v5.0 PRODUCTION READY
Date: September 29, 2025
Last Updated: September 29, 2025

THIS VERSION FIXES:
1. Actually extracts content from URLs (was not working)
2. Proper ScraperAPI integration with correct parameters
3. Multiple fallback methods for extraction
4. Clean author/title extraction
5. Handles both news articles and direct text input
6. No duplicate code or conflicting versions
7. Includes service wrapper for pipeline compatibility

DEPLOYMENT NOTES:
- Place this file in: services/article_extractor.py
- Delete any other article_extractor.py files
- Requires SCRAPERAPI_KEY environment variable
- Add PYTHONDONTWRITEBYTECODE=1 to Render environment
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

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress noisy loggers
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('newspaper').setLevel(logging.WARNING)


class ArticleExtractor:
    """
    Enhanced article extraction service with multiple fallback methods
    """
    
    VERSION = "5.0"
    
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
        
        logger.info(f"ArticleExtractor v{self.VERSION} initialized")
        logger.info(f"ScraperAPI configured: {bool(self.scraperapi_key)}")
        
        if not self.scraperapi_key:
            logger.warning("ScraperAPI key not found - extraction may be limited")
    
    def extract(self, url: str, use_scraperapi: bool = True) -> Dict[str, Any]:
        """
        Main extraction method with multiple fallback strategies
        
        Args:
            url: The URL to extract content from
            use_scraperapi: Whether to use ScraperAPI for anti-bot protection
            
        Returns:
            Dict containing extracted article data
        """
        logger.info(f"[v{self.VERSION}] Starting extraction for: {url}")
        
        # Check cache first
        cache_key = self._get_cache_key(url)
        if cache_key in self._cache:
            cache_entry = self._cache[cache_key]
            if time.time() - cache_entry['timestamp'] < self._cache_ttl:
                logger.info("Returning cached article")
                return cache_entry['data']
        
        # Try extraction methods in order
        result = None
        
        # Method 1: ScraperAPI (most reliable for protected sites)
        if use_scraperapi and self.scraperapi_key:
            result = self._extract_with_scraperapi(url)
            if result and result.get('success'):
                logger.info("✓ Extraction successful with ScraperAPI")
                self._cache_result(cache_key, result)
                return result
        
        # Method 2: Newspaper3k with custom headers
        result = self._extract_with_newspaper(url)
        if result and result.get('success'):
            logger.info("✓ Extraction successful with Newspaper3k")
            self._cache_result(cache_key, result)
            return result
        
        # Method 3: Direct requests with BeautifulSoup
        result = self._extract_with_beautifulsoup(url)
        if result and result.get('success'):
            logger.info("✓ Extraction successful with BeautifulSoup")
            self._cache_result(cache_key, result)
            return result
        
        # If all methods fail, return error
        logger.error(f"All extraction methods failed for {url}")
        return self._create_error_response(url, "All extraction methods failed")
    
    def _extract_with_scraperapi(self, url: str) -> Dict[str, Any]:
        """
        Extract using ScraperAPI for anti-bot protection
        """
        try:
            logger.info("Attempting ScraperAPI extraction...")
            
            # ScraperAPI endpoint
            api_url = "https://api.scraperapi.com"
            
            # Parameters for ScraperAPI
            params = {
                'api_key': self.scraperapi_key,
                'url': url,
                'render': 'true',  # Render JavaScript
                'country_code': 'us'
            }
            
            # Only add premium if explicitly enabled
            if os.environ.get('SCRAPERAPI_PREMIUM', 'false').lower() == 'true':
                params['premium'] = 'true'
            
            # Make request to ScraperAPI
            response = self.session.get(api_url, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse the HTML
            html_content = response.text
            if not html_content or len(html_content) < 100:
                raise ValueError("Received empty or minimal content from ScraperAPI")
            
            # Extract article using newspaper
            article = Article(url)
            article.download(input_html=html_content)
            article.parse()
            
            # Validate extraction
            if not article.text or len(article.text) < 100:
                # Fallback to BeautifulSoup parsing
                return self._parse_html_content(html_content, url)
            
            # Clean and prepare result
            return self._prepare_article_result(
                url=url,
                title=article.title,
                text=article.text,
                authors=article.authors,
                publish_date=article.publish_date,
                html=html_content,
                extraction_method='scraperapi_newspaper'
            )
            
        except requests.HTTPError as e:
            if '402' in str(e):
                logger.error("ScraperAPI credits exhausted or invalid key")
            else:
                logger.error(f"ScraperAPI HTTP error: {e}")
            return None
        except requests.RequestException as e:
            logger.error(f"ScraperAPI request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"ScraperAPI extraction failed: {e}")
            return None
    
    def _extract_with_newspaper(self, url: str) -> Dict[str, Any]:
        """
        Extract using Newspaper3k library
        """
        try:
            logger.info("Attempting Newspaper3k extraction...")
            
            # Configure article
            article = Article(url)
            article.config.browser_user_agent = self.session.headers['User-Agent']
            article.config.request_timeout = 20
            
            # Download and parse
            article.download()
            article.parse()
            
            # Validate content
            if not article.text or len(article.text) < 100:
                raise ArticleException("Article text too short or empty")
            
            # Perform NLP if possible
            try:
                article.nlp()
            except:
                pass  # NLP is optional
            
            return self._prepare_article_result(
                url=url,
                title=article.title,
                text=article.text,
                authors=article.authors,
                publish_date=article.publish_date,
                summary=article.summary if hasattr(article, 'summary') else None,
                extraction_method='newspaper'
            )
            
        except ArticleException as e:
            logger.error(f"Newspaper extraction failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Newspaper extraction: {e}")
            return None
    
    def _extract_with_beautifulsoup(self, url: str) -> Dict[str, Any]:
        """
        Direct extraction using requests and BeautifulSoup
        """
        try:
            logger.info("Attempting BeautifulSoup extraction...")
            
            # Make direct request
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            
            # Parse HTML
            return self._parse_html_content(response.text, url)
            
        except requests.RequestException as e:
            logger.error(f"BeautifulSoup request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"BeautifulSoup extraction failed: {e}")
            return None
    
    def _parse_html_content(self, html: str, url: str) -> Dict[str, Any]:
        """
        Parse HTML content using BeautifulSoup
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "meta", "noscript"]):
                script.decompose()
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract main content
            content = self._extract_main_content(soup)
            
            # Extract author
            author = self._extract_author(soup, html)
            
            # Extract publish date
            publish_date = self._extract_publish_date(soup, html)
            
            # Validate content
            if not content or len(content) < 100:
                raise ValueError("Extracted content too short")
            
            return self._prepare_article_result(
                url=url,
                title=title,
                text=content,
                authors=[author] if author else [],
                publish_date=publish_date,
                extraction_method='beautifulsoup'
            )
            
        except Exception as e:
            logger.error(f"HTML parsing failed: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title from HTML"""
        # Try multiple selectors
        selectors = [
            'h1',
            'h1.headline',
            'h1.title',
            'h1.entry-title',
            '[class*="headline"]',
            '[class*="title"]',
            'title',
            'meta[property="og:title"]',
            'meta[name="twitter:title"]'
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
        """Extract main article content"""
        # Common content selectors
        selectors = [
            'article',
            '[role="main"]',
            '[class*="content-body"]',
            '[class*="article-body"]',
            '[class*="entry-content"]',
            '[class*="post-content"]',
            'div.content',
            'div.story-body',
            'main'
        ]
        
        # Try each selector
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                # Get all paragraphs from the first matching element
                content_elem = elements[0]
                paragraphs = content_elem.find_all(['p', 'h2', 'h3', 'h4'])
                
                text_parts = []
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 20:  # Filter out short snippets
                        text_parts.append(text)
                
                if text_parts:
                    content = '\n\n'.join(text_parts)
                    if len(content) > 200:  # Minimum content length
                        return content
        
        # Fallback: get all paragraphs
        all_paragraphs = soup.find_all('p')
        text_parts = []
        
        for p in all_paragraphs:
            text = p.get_text(strip=True)
            if text and len(text) > 30:  # Filter short snippets
                text_parts.append(text)
        
        if text_parts:
            # Take the longest contiguous block of paragraphs
            return '\n\n'.join(text_parts[:50])  # Limit to 50 paragraphs
        
        # Last resort: get all text
        return soup.get_text(separator='\n', strip=True)
    
    def _extract_author(self, soup: BeautifulSoup, html: str) -> str:
        """Extract author from HTML"""
        # Try meta tags first
        meta_selectors = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            'meta[name="byl"]',
            'meta[name="parsely-author"]'
        ]
        
        for selector in meta_selectors:
            element = soup.select_one(selector)
            if element:
                author = element.get('content', '')
                if author:
                    return self._clean_author_name(author)
        
        # Try common author selectors
        selectors = [
            '[class*="author-name"]',
            '[class*="by-author"]',
            '[class*="byline"]',
            '[rel="author"]',
            '.author',
            '.writer',
            'span.by'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                author = element.get_text(strip=True)
                if author and len(author) > 2:
                    return self._clean_author_name(author)
        
        # Try to find author in JSON-LD
        json_lds = soup.find_all('script', type='application/ld+json')
        for json_ld in json_lds:
            try:
                data = json.loads(json_ld.string)
                if isinstance(data, dict):
                    if 'author' in data:
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
        """Extract publish date from HTML"""
        # Try meta tags
        meta_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="publish_date"]',
            'meta[name="parsely-pub-date"]',
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
        
        # Try time elements
        time_element = soup.select_one('time[datetime]')
        if time_element:
            try:
                return datetime.fromisoformat(time_element['datetime'].replace('Z', '+00:00'))
            except:
                pass
        
        return None
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters
        text = re.sub(r'[\r\n\t]', ' ', text)
        
        # Trim
        return text.strip()
    
    def _clean_author_name(self, author: str) -> str:
        """Clean author name"""
        if not author:
            return "Unknown Author"
        
        # Remove common prefixes
        author = re.sub(r'^(by|By|BY)\s+', '', author)
        author = re.sub(r'^(written by|Written by)\s+', '', author, re.IGNORECASE)
        
        # Remove extra whitespace
        author = re.sub(r'\s+', ' ', author)
        
        # Remove special characters
        author = re.sub(r'[<>"]', '', author)
        
        # Trim
        author = author.strip()
        
        # Validate
        if not author or len(author) < 2 or len(author) > 100:
            return "Unknown Author"
        
        return author
    
    def _prepare_article_result(
        self,
        url: str,
        title: str,
        text: str,
        authors: Optional[List[str]] = None,
        publish_date: Optional[datetime] = None,
        summary: Optional[str] = None,
        html: Optional[str] = None,
        extraction_method: str = 'unknown'
    ) -> Dict[str, Any]:
        """Prepare the final article result"""
        
        # Clean text
        title = self._clean_text(title) if title else "Unknown Title"
        text = self._clean_text(text) if text else ""
        
        # Process authors
        if authors:
            authors = [self._clean_author_name(a) for a in authors if a]
            authors = [a for a in authors if a != "Unknown Author"]
        
        author = authors[0] if authors else "Unknown Author"
        
        # Extract domain
        domain = urlparse(url).netloc.replace('www.', '')
        
        # Calculate metrics
        word_count = len(text.split()) if text else 0
        
        # Build result
        result = {
            'success': True,
            'url': url,
            'title': title,
            'text': text,
            'author': author,
            'authors': authors or [author],
            'publish_date': publish_date.isoformat() if publish_date else None,
            'domain': domain,
            'word_count': word_count,
            'extraction_method': extraction_method,
            'extracted_at': datetime.now().isoformat(),
            'version': self.VERSION
        }
        
        # Add summary if available
        if summary:
            result['summary'] = self._clean_text(summary)
        
        # Log success
        logger.info(f"✓ Extracted: {title[:50]}... ({word_count} words) by {author}")
        
        return result
    
    def _create_error_response(self, url: str, error_message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            'success': False,
            'url': url,
            'title': 'Unknown',
            'text': '',
            'author': 'Unknown',
            'authors': [],
            'error': error_message,
            'extraction_method': 'none',
            'version': self.VERSION,
            'extracted_at': datetime.now().isoformat()
        }
    
    def _get_cache_key(self, url: str) -> str:
        """Generate cache key for URL"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def _cache_result(self, key: str, result: Dict[str, Any]) -> None:
        """Cache extraction result"""
        self._cache[key] = {
            'data': result,
            'timestamp': time.time()
        }
        
        # Clean old cache entries
        if len(self._cache) > 100:
            # Remove oldest entries
            sorted_items = sorted(
                self._cache.items(),
                key=lambda x: x[1]['timestamp']
            )
            self._cache = dict(sorted_items[-50:])
    
    def process_text_input(self, text: str, source: str = "direct_input") -> Dict[str, Any]:
        """
        Process direct text input (not from URL)
        
        Args:
            text: The text content to analyze
            source: Source identifier
            
        Returns:
            Dict containing processed text data
        """
        logger.info(f"Processing direct text input ({len(text)} chars)")
        
        # Extract title from first line or generate one
        lines = text.strip().split('\n')
        title = lines[0][:100] if lines else "Direct Text Input"
        
        # Clean the text
        cleaned_text = self._clean_text(text)
        
        return {
            'success': True,
            'url': source,
            'title': title,
            'text': cleaned_text,
            'author': 'Unknown Author',
            'authors': ['Unknown Author'],
            'publish_date': datetime.now().isoformat(),
            'domain': 'text_input',
            'word_count': len(cleaned_text.split()),
            'extraction_method': 'text_input',
            'extracted_at': datetime.now().isoformat(),
            'version': self.VERSION
        }


# Service wrapper for pipeline compatibility
class ArticleExtractorService:
    """Service wrapper that integrates with the analysis pipeline"""
    
    def __init__(self):
        self.extractor = ArticleExtractor()
        logger.info(f"[ARTICLE_EXTRACTOR v{ArticleExtractor.VERSION}] Service wrapper initialized")
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Method the pipeline expects"""
        url = data.get('url', '')
        text = data.get('text', '')
        content = data.get('content', '')
        
        # Handle direct text input
        if not url and (text or content):
            input_text = text or content
            result = self.extractor.process_text_input(input_text, source="direct_input")
        elif url:
            result = self.extractor.extract(url)
        else:
            return {
                'service': 'article_extractor',
                'success': False,
                'error': 'No URL or text provided',
                'data': {},
                'available': True,
                'timestamp': time.time()
            }
        
        # Return in the format the pipeline expects
        if result.get('success'):
            return {
                'service': 'article_extractor',
                'success': True,
                'data': {
                    'text': result.get('text', ''),
                    'title': result.get('title', 'Unknown'),
                    'author': result.get('author', 'Unknown'),
                    'domain': result.get('domain', ''),
                    'content': result.get('text', ''),
                    'url': url or result.get('url', ''),
                    'word_count': result.get('word_count', 0),
                    'extraction_method': result.get('extraction_method', 'unknown')
                },
                'available': True,
                'timestamp': time.time()
            }
        else:
            return {
                'service': 'article_extractor',
                'success': False,
                'error': result.get('error', 'Extraction failed'),
                'data': {
                    'text': '',
                    'title': 'Unknown',
                    'author': 'Unknown',
                    'domain': '',
                    'content': '',
                    'url': url
                },
                'available': True,
                'timestamp': time.time()
            }


# Create singleton instance
_instance = None

def get_extractor() -> ArticleExtractor:
    """Get or create the article extractor instance"""
    global _instance
    if _instance is None:
        _instance = ArticleExtractor()
    return _instance


# For backwards compatibility
def extract_article(url: str) -> Dict[str, Any]:
    """
    Legacy function for compatibility
    
    Args:
        url: URL to extract
        
    Returns:
        Extracted article data
    """
    extractor = get_extractor()
    return extractor.extract(url)


if __name__ == "__main__":
    # Test extraction
    test_url = "https://www.reuters.com/"
    
    print(f"Testing ArticleExtractor v{ArticleExtractor.VERSION}")
    print(f"Test URL: {test_url}")
    print("-" * 50)
    
    # Test direct instantiation
    extractor = ArticleExtractor()
    result = extractor.extract(test_url)
    
    if result['success']:
        print(f"✓ Title: {result['title'][:60]}...")
        print(f"✓ Author: {result['author']}")
        print(f"✓ Word Count: {result['word_count']}")
        print(f"✓ Method: {result['extraction_method']}")
        print(f"✓ Content preview: {result['text'][:200]}...")
    else:
        print(f"✗ Extraction failed: {result.get('error', 'Unknown error')}")
    
    print("-" * 50)
    print("Testing ArticleExtractorService wrapper...")
    
    # Test service wrapper
    service = ArticleExtractorService()
    service_result = service.analyze({'url': test_url})
    
    if service_result['success']:
        print(f"✓ Service wrapper works")
        print(f"✓ Data keys: {list(service_result['data'].keys())}")
    else:
        print(f"✗ Service wrapper failed: {service_result.get('error', 'Unknown error')}")
