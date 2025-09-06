"""
Article Extractor Service - COMPLETE ROBUST PRODUCTION VERSION
Date: September 6, 2025
Last Updated: September 6, 2025

CRITICAL: This version ensures proper service registration and initialization
- Works with or without BaseAnalyzer
- Properly registers with service registry
- ScraperAPI as primary method
- Comprehensive author extraction
- No dependencies that could cause import failures
"""
import os
import re
import json
import time
import logging
import requests
import traceback
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
from datetime import datetime

logger = logging.getLogger(__name__)

# Safe import of BeautifulSoup
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    logger.error("BeautifulSoup not available - article extraction will fail")

# Try to import BaseAnalyzer with complete fallback
BASE_ANALYZER_AVAILABLE = False
try:
    from services.base_analyzer import BaseAnalyzer
    BASE_ANALYZER_AVAILABLE = True
    logger.info("BaseAnalyzer imported successfully")
except ImportError:
    logger.warning("BaseAnalyzer not available - creating fallback")
    # Create a complete BaseAnalyzer replacement
    class BaseAnalyzer:
        def __init__(self, service_name):
            self.service_name = service_name
            self.available = True
            self.is_available = True
            self.config = None
            self._performance_stats = {
                'total_calls': 0,
                'successful_calls': 0,
                'failed_calls': 0,
                'total_time': 0,
                'average_time': 0
            }
            
        def check_service(self):
            """Check if service is available"""
            return True
            
        def get_service_info(self):
            """Get service information"""
            return {
                'name': self.service_name,
                'available': self.available,
                'enabled': True,
                'performance': self._performance_stats.copy()
            }
        
        def get_success_result(self, data):
            """Return success result"""
            return {
                'success': True,
                'data': data,
                'service': self.service_name,
                'available': True,
                'timestamp': time.time(),
                'analysis_complete': True
            }
        
        def get_error_result(self, error_message):
            """Return error result"""
            return {
                'success': False,
                'error': error_message,
                'service': self.service_name,
                'available': self.available,
                'timestamp': time.time()
            }
        
        def get_default_result(self):
            """Return default result"""
            return {
                'success': False,
                'service': self.service_name,
                'available': False,
                'error': 'Service unavailable',
                'timestamp': time.time()
            }


class ArticleExtractor(BaseAnalyzer):
    """
    Robust article extraction service with comprehensive error handling
    """
    
    def __init__(self):
        """Initialize with complete error handling"""
        super().__init__('article_extractor')
        
        # Ensure service is marked as available
        self.available = True
        self.is_available = True
        
        # Get API keys from environment
        self.scraperapi_key = os.environ.get('SCRAPERAPI_KEY')
        self.scrapingbee_key = os.environ.get('SCRAPINGBEE_API_KEY')
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Domain-specific author selectors
        self.author_selectors = {
            'bbc.com': [
                'span.ssrcss-68pt20-Text-TextContributorName',
                'div.ssrcss-68pt20-Text-TextContributorName',
                'span[class*="TextContributorName"]',
                'div[class*="TextContributorName"]',
                'div.byline',
                'span.byline__name',
                'p[class*="Contributor"]'
            ],
            'cnn.com': [
                'span.byline__name',
                'div.byline__names',
                'span.metadata__byline__author'
            ],
            'reuters.com': [
                'div.author-name',
                'span.author-name',
                'div.ArticleHeader__author',
                'a[href*="/authors/"]'
            ],
            'nytimes.com': [
                'span.by-author',
                'p.byline',
                'div.byline',
                'span[itemprop="author"]'
            ]
        }
        
        logger.info("=" * 60)
        logger.info("ArticleExtractor initialized successfully")
        logger.info(f"  Service name: {self.service_name}")
        logger.info(f"  Available: {self.available}")
        logger.info(f"  ScraperAPI: {'✓ Configured' if self.scraperapi_key else '✗ Not configured'}")
        logger.info(f"  BeautifulSoup: {'✓ Available' if BS4_AVAILABLE else '✗ Not available'}")
        logger.info(f"  BaseAnalyzer: {'✓ Original' if BASE_ANALYZER_AVAILABLE else '✓ Fallback'}")
        logger.info("=" * 60)
    
    def check_service(self) -> bool:
        """Verify service is operational"""
        return BS4_AVAILABLE  # Can't extract without BeautifulSoup
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis method - extracts article from URL
        """
        try:
            logger.info("=" * 60)
            logger.info("ARTICLE EXTRACTOR - STARTING EXTRACTION")
            logger.info("=" * 60)
            
            # Check BeautifulSoup availability
            if not BS4_AVAILABLE:
                error_msg = "BeautifulSoup not available - cannot extract articles"
                logger.error(error_msg)
                return self.get_error_result(error_msg)
            
            # Get URL from input
            url = data.get('url')
            if not url:
                return self.get_error_result("No URL provided")
            
            logger.info(f"Extracting from URL: {url}")
            
            # Try extraction methods in priority order
            extracted_data = None
            
            # Method 1: ScraperAPI (best for difficult sites)
            if self.scraperapi_key:
                extracted_data = self._extract_with_scraperapi(url)
            
            # Method 2: Enhanced requests (fallback)
            if not extracted_data:
                extracted_data = self._extract_with_enhanced_requests(url)
            
            # Method 3: Basic requests (last resort)
            if not extracted_data:
                extracted_data = self._extract_with_basic_requests(url)
            
            # Check if extraction succeeded
            if extracted_data:
                logger.info("=== EXTRACTION COMPLETE ===")
                logger.info(f"Title: {extracted_data.get('title', 'Unknown')[:50]}...")
                logger.info(f"Author: {extracted_data.get('author', 'Unknown')}")
                logger.info(f"Domain: {extracted_data.get('domain', 'Unknown')}")
                logger.info(f"Word count: {extracted_data.get('word_count', 0)}")
                
                # Ensure all required fields are present
                extracted_data['extraction_successful'] = True
                extracted_data['analysis_complete'] = True
                
                return self.get_success_result(extracted_data)
            else:
                error_msg = "All extraction methods failed"
                logger.error(error_msg)
                return self.get_error_result(error_msg)
                
        except Exception as e:
            error_msg = f"Article extraction error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return self.get_error_result(error_msg)
    
    def _extract_with_scraperapi(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract using ScraperAPI - primary method"""
        try:
            logger.info("Trying scraperapi...")
            
            api_url = "http://api.scraperapi.com"
            params = {
                'api_key': self.scraperapi_key,
                'url': url,
                'render': 'false',
                'country_code': 'us'
            }
            
            response = requests.get(api_url, params=params, timeout=30)
            response.raise_for_status()
            
            return self._parse_html_content(response.text, url, 'scraperapi')
            
        except Exception as e:
            logger.error(f"ScraperAPI extraction failed: {e}")
            return None
    
    def _extract_with_enhanced_requests(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract using enhanced requests - fallback method"""
        try:
            logger.info("Trying enhanced_requests...")
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            return self._parse_html_content(response.text, url, 'enhanced_requests')
            
        except Exception as e:
            logger.error(f"Enhanced requests extraction failed: {e}")
            return None
    
    def _extract_with_basic_requests(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract using basic requests - last resort"""
        try:
            logger.info("Trying basic_fallback...")
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            return self._parse_html_content(response.text, url, 'basic_fallback')
            
        except Exception as e:
            logger.error(f"Basic fallback extraction failed: {e}")
            return None
    
    def _parse_html_content(self, html: str, url: str, method: str) -> Optional[Dict[str, Any]]:
        """Parse HTML content and extract article data"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract components
            title = self._extract_title(soup)
            author = self._extract_author(soup, url)
            content = self._extract_content(soup)
            publish_date = self._extract_publish_date(soup)
            
            # Get domain
            domain = urlparse(url).netloc.replace('www.', '')
            
            # Validate content
            if not content or len(content) < 100:
                logger.warning(f"{method} returned insufficient content")
                return None
            
            # Log extraction details
            logger.info(f"Extracting author for domain: {domain}")
            if author != "Unknown":
                logger.info(f"Found valid author: {author}")
            else:
                logger.info("No valid author found with any method")
            
            logger.info(f"Extraction results - Author: {author}, Title: {title[:50]}, Words: {len(content.split())}")
            logger.info(f"SUCCESS: {method} extracted content")
            
            return {
                'title': title,
                'author': author,
                'content': content,
                'text': content,
                'publish_date': publish_date,
                'url': url,
                'domain': domain,
                'source': domain,
                'description': title,  # Fallback description
                'word_count': len(content.split()),
                'language': 'en',  # Default to English
                'extraction_method': method
            }
            
        except Exception as e:
            logger.error(f"HTML parsing failed: {e}")
            return None
    
    def _extract_author(self, soup: BeautifulSoup, url: str) -> str:
        """Extract author with domain-specific patterns"""
        domain = urlparse(url).netloc.replace('www.', '')
        
        # Try domain-specific selectors first
        if domain in self.author_selectors:
            for selector in self.author_selectors[domain]:
                try:
                    element = soup.select_one(selector)
                    if element:
                        author = element.get_text(strip=True)
                        # Clean common prefixes
                        author = re.sub(r'^(By|Written by)\s+', '', author, flags=re.I)
                        if self._is_valid_author(author):
                            return author
                except:
                    continue
        
        # Try meta tags
        for name in ['author', 'article:author', 'dc.creator', 'byl']:
            meta = soup.find('meta', attrs={'name': name}) or \
                   soup.find('meta', attrs={'property': name})
            if meta and meta.get('content'):
                author = meta['content'].strip()
                if self._is_valid_author(author):
                    return author
        
        # Try schema.org
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if 'author' in data:
                    if isinstance(data['author'], dict):
                        author = data['author'].get('name', '')
                    else:
                        author = str(data['author'])
                    if self._is_valid_author(author):
                        return author
            except:
                continue
        
        # Try common class patterns
        for pattern in ['byline', 'author', 'writer', 'contributor']:
            elements = soup.find_all(class_=re.compile(pattern, re.I))
            for element in elements[:5]:  # Limit to first 5 to avoid performance issues
                text = element.get_text(strip=True)
                text = re.sub(r'^(By|Written by)\s+', '', text, flags=re.I)
                if self._is_valid_author(text):
                    return text
        
        return "Unknown"
    
    def _is_valid_author(self, author: str) -> bool:
        """Check if author name is valid"""
        if not author or len(author) < 3 or len(author) > 100:
            return False
        
        # Must contain letters
        if not re.search(r'[a-zA-Z]', author):
            return False
        
        # Filter out invalid patterns
        invalid = ['unknown', 'admin', 'editor', 'staff', '@', 'http', '<', '>']
        author_lower = author.lower()
        for pattern in invalid:
            if pattern in author_lower:
                return False
        
        return True
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title"""
        # Try OpenGraph
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        
        # Try h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)
        
        # Try title tag
        title = soup.find('title')
        if title:
            text = title.get_text(strip=True)
            # Remove site name
            return re.split(r' [-|] ', text)[0]
        
        return "No title found"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main article content"""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer']):
            element.decompose()
        
        # Try article tag
        article = soup.find('article')
        if article:
            paragraphs = article.find_all('p')
            if paragraphs:
                content = ' '.join([p.get_text(strip=True) for p in paragraphs])
                if len(content) > 200:
                    return content
        
        # Try main content areas
        for selector in ['main', 'div[role="main"]', 'div.content', 'div.article']:
            element = soup.select_one(selector)
            if element:
                paragraphs = element.find_all('p')
                if paragraphs:
                    content = ' '.join([p.get_text(strip=True) for p in paragraphs])
                    if len(content) > 200:
                        return content
        
        # Fallback: all paragraphs
        all_p = soup.find_all('p')
        content = ' '.join([p.get_text(strip=True) for p in all_p if len(p.get_text(strip=True)) > 30])
        return content
    
    def _extract_publish_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract publish date"""
        # Try meta tags
        date_metas = [
            ('property', 'article:published_time'),
            ('name', 'publish_date'),
            ('property', 'og:article:published_time'),
            ('itemprop', 'datePublished')
        ]
        
        for attr, value in date_metas:
            meta = soup.find('meta', {attr: value})
            if meta and meta.get('content'):
                return meta['content']
        
        # Try time element
        time_elem = soup.find('time')
        if time_elem:
            return time_elem.get('datetime') or time_elem.get_text(strip=True)
        
        return None
