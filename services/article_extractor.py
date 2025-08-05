"""
FILE: services/article_extractor.py
Enhanced article extractor with robust timeout handling and circuit breaker
Fixes timeout issues with problematic sites like Washington Post
"""

import os
import logging
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, Set
from datetime import datetime, timedelta
import json
from urllib.parse import urlparse
import time
import random
import re
from fake_useragent import UserAgent
from collections import defaultdict
import threading

# Try to import advanced scraping libraries
try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False
    
try:
    from curl_cffi import requests as curl_requests
    CURL_CFFI_AVAILABLE = True
except ImportError:
    CURL_CFFI_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

logger = logging.getLogger(__name__)

class CircuitBreaker:
    """Circuit breaker to prevent repeated attempts to problematic domains"""
    def __init__(self):
        self.failed_domains = defaultdict(lambda: {'count': 0, 'last_attempt': None})
        self.threshold = 3  # failures before opening circuit
        self.timeout = 300  # 5 minutes before retry
        self._lock = threading.Lock()
    
    def is_open(self, domain: str) -> bool:
        """Check if circuit is open for domain"""
        with self._lock:
            if domain not in self.failed_domains:
                return False
            
            failure_data = self.failed_domains[domain]
            if failure_data['count'] >= self.threshold:
                if failure_data['last_attempt']:
                    time_since_failure = (datetime.now() - failure_data['last_attempt']).total_seconds()
                    if time_since_failure < self.timeout:
                        return True
                    else:
                        # Reset after timeout
                        self.failed_domains[domain] = {'count': 0, 'last_attempt': None}
            return False
    
    def record_failure(self, domain: str):
        """Record a failure for domain"""
        with self._lock:
            self.failed_domains[domain]['count'] += 1
            self.failed_domains[domain]['last_attempt'] = datetime.now()
    
    def record_success(self, domain: str):
        """Record success and reset counter"""
        with self._lock:
            if domain in self.failed_domains:
                del self.failed_domains[domain]

class ArticleExtractor:
    """Enhanced article extractor with timeout protection and circuit breaker"""
    
    def __init__(self):
        # Reduced timeouts for faster failure
        self.timeout = 10  # 10 seconds max per request
        self.total_timeout = 30  # 30 seconds max for entire extraction
        self.delay_range = (0.5, 1.5)  # Reduced delay
        self.ua = UserAgent()
        self.circuit_breaker = CircuitBreaker()
        
        # Problematic domains that need special handling
        self.slow_domains = {
            'washingtonpost.com', 'wsj.com', 'nytimes.com', 
            'ft.com', 'economist.com', 'bloomberg.com'
        }
        
        # Initialize session with optimized settings
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=10,
            max_retries=requests.adapters.Retry(
                total=2,  # Reduced retries
                backoff_factor=0.3,
                status_forcelist=[500, 502, 503, 504]
            )
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.session.headers.update(self._get_headers())
        
        # Initialize cloudscraper if available
        if CLOUDSCRAPER_AVAILABLE:
            self.cloudscraper_session = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'desktop': True
                }
            )
            
        logger.info(f"ArticleExtractor initialized (CloudScraper: {CLOUDSCRAPER_AVAILABLE}, Curl-CFFI: {CURL_CFFI_AVAILABLE})")
    
    def _get_headers(self, referer=None):
        """Get randomized headers that look like a real browser"""
        headers = {
            'User-Agent': self.ua.chrome,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        if referer:
            headers['Referer'] = referer
            headers['Sec-Fetch-Site'] = 'same-origin'
            
        return headers
    
    def _delay(self):
        """Random delay to avoid rate limiting"""
        time.sleep(random.uniform(*self.delay_range))
    
    def extract_from_url(self, url: str) -> Dict[str, Any]:
        """
        Extract article content from URL with timeout protection
        
        Returns:
            Dict containing article data or error information
        """
        start_time = time.time()
        logger.info(f"Extracting article from: {url}")
        
        # Parse domain
        domain = urlparse(url).netloc.lower().replace('www.', '')
        
        # Check circuit breaker
        if self.circuit_breaker.is_open(domain):
            logger.warning(f"Circuit breaker open for {domain}, returning cached error")
            return {
                'success': False,
                'error': f'Too many failures for {domain}. Please try again later.',
                'url': url
            }
        
        # Determine extraction strategy based on domain
        if domain in self.slow_domains:
            # For known slow sites, try faster methods only
            methods = [
                ("fast requests", self._extract_with_fast_requests),
            ]
            if CURL_CFFI_AVAILABLE:
                methods.append(("curl-cffi", self._extract_with_curl_cffi))
        else:
            # For other sites, use standard order
            methods = [
                ("fast requests", self._extract_with_fast_requests),
            ]
            if CLOUDSCRAPER_AVAILABLE:
                methods.append(("cloudscraper", self._extract_with_cloudscraper))
            if CURL_CFFI_AVAILABLE:
                methods.append(("curl-cffi", self._extract_with_curl_cffi))
        
        last_error = None
        for method_name, method_func in methods:
            # Check total timeout
            if time.time() - start_time > self.total_timeout:
                logger.error(f"Total timeout exceeded for {url}")
                self.circuit_breaker.record_failure(domain)
                return {
                    'success': False,
                    'error': 'Extraction timeout - site is too slow to respond',
                    'url': url
                }
            
            try:
                logger.info(f"Trying {method_name}...")
                content = method_func(url)
                if content and len(content) > 1000:
                    logger.info(f"Success with {method_name}")
                    self.circuit_breaker.record_success(domain)
                    return self._parse_article(content, url)
            except requests.Timeout:
                logger.warning(f"{method_name} timed out")
                last_error = "Request timeout"
                continue
            except Exception as e:
                logger.warning(f"{method_name} failed: {str(e)}")
                last_error = str(e)
                continue
        
        # All methods failed
        self.circuit_breaker.record_failure(domain)
        error_msg = f"All extraction methods failed. Last error: {last_error}"
        logger.error(error_msg)
        
        # For known problematic sites, provide helpful message
        if domain in self.slow_domains:
            error_msg = f"Unable to extract from {domain} - this site often has slow response times"
        
        return {
            'success': False,
            'error': error_msg,
            'url': url
        }
    
    def _extract_with_fast_requests(self, url: str) -> Optional[str]:
        """Fast requests with strict timeout"""
        self._delay()
        
        # Update headers
        headers = self._get_headers()
        headers['User-Agent'] = self.ua.random
        
        # Make request with strict timeout
        response = self.session.get(
            url, 
            headers=headers, 
            timeout=self.timeout,  # Strict timeout
            allow_redirects=True,
            stream=False  # Don't stream for faster failure
        )
        response.raise_for_status()
        
        content = response.text
        if len(content) < 1000:
            raise Exception("Response too short, likely blocked")
            
        return content
    
    def _extract_with_cloudscraper(self, url: str) -> Optional[str]:
        """CloudScraper method with timeout"""
        if not CLOUDSCRAPER_AVAILABLE:
            raise Exception("CloudScraper not available")
            
        self._delay()
        
        # Use session for connection pooling
        response = self.cloudscraper_session.get(
            url, 
            timeout=self.timeout,
            allow_redirects=True
        )
        response.raise_for_status()
        
        content = response.text
        if len(content) < 1000:
            raise Exception("Response too short, likely blocked")
            
        return content
    
    def _extract_with_curl_cffi(self, url: str) -> Optional[str]:
        """Curl-CFFI method with timeout"""
        if not CURL_CFFI_AVAILABLE:
            raise Exception("Curl-CFFI not available")
            
        self._delay()
        
        # Try Chrome impersonation
        response = curl_requests.get(
            url, 
            impersonate='chrome110',
            headers=self._get_headers(),
            timeout=self.timeout,
            allow_redirects=True
        )
        response.raise_for_status()
        
        content = response.text
        if len(content) < 1000:
            raise Exception("Response too short, likely blocked")
            
        return content
    
    def _parse_article(self, html_content: str, url: str) -> Dict[str, Any]:
        """Parse article content from HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract metadata
            article_data = {
                'url': url,
                'domain': urlparse(url).netloc,
                'extracted_at': datetime.now().isoformat(),
                'success': True
            }
            
            # Title extraction (multiple strategies)
            title = None
            # Try meta property first
            if not title:
                meta_title = soup.find('meta', property='og:title')
                if meta_title:
                    title = meta_title.get('content', '').strip()
            # Try regular title tag
            if not title:
                title_tag = soup.find('title')
                if title_tag:
                    title = title_tag.get_text().strip()
            # Try h1
            if not title:
                h1 = soup.find('h1')
                if h1:
                    title = h1.get_text().strip()
            
            article_data['title'] = title or 'Untitled'
            
            # Author extraction
            author = self._extract_author(soup)
            article_data['author'] = author
            
            # Date extraction
            publish_date = self._extract_date(soup)
            article_data['publish_date'] = publish_date
            
            # Content extraction with domain-specific handling
            content = self._extract_content_smart(soup, url)
            article_data['text'] = content
            article_data['word_count'] = len(content.split()) if content else 0
            
            # Description/Summary
            description = None
            meta_desc = soup.find('meta', {'name': 'description'}) or soup.find('meta', property='og:description')
            if meta_desc:
                description = meta_desc.get('content', '').strip()
            article_data['description'] = description
            
            # Image
            image = None
            meta_image = soup.find('meta', property='og:image')
            if meta_image:
                image = meta_image.get('content')
            article_data['image'] = image
            
            # Keywords
            keywords = []
            meta_keywords = soup.find('meta', {'name': 'keywords'})
            if meta_keywords:
                keywords = [k.strip() for k in meta_keywords.get('content', '').split(',')]
            article_data['keywords'] = keywords
            
            return article_data
            
        except Exception as e:
            logger.error(f"Error parsing article: {e}")
            return {
                'success': False,
                'error': f'Parsing error: {str(e)}',
                'url': url
            }
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author with multiple strategies"""
        author = None
        
        # Try JSON-LD first
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if 'author' in data:
                        if isinstance(data['author'], dict):
                            author = data['author'].get('name')
                        elif isinstance(data['author'], str):
                            author = data['author']
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and 'author' in item:
                            if isinstance(item['author'], dict):
                                author = item['author'].get('name')
                            elif isinstance(item['author'], str):
                                author = item['author']
                if author:
                    break
            except:
                continue
        
        # Try meta tags
        if not author:
            meta_author = soup.find('meta', {'name': 'author'}) or soup.find('meta', property='article:author')
            if meta_author:
                author = meta_author.get('content')
        
        # Try byline patterns
        if not author:
            byline_patterns = [
                {'class': ['byline', 'by-line', 'author', 'writer', 'journalist']},
                {'itemprop': 'author'},
                {'rel': 'author'}
            ]
            
            for pattern in byline_patterns:
                element = soup.find(['span', 'div', 'p', 'a'], pattern)
                if element:
                    text = element.get_text().strip()
                    # Clean common prefixes
                    for prefix in ['By', 'by', 'BY', 'Written by', 'Author:']:
                        if text.startswith(prefix):
                            text = text[len(prefix):].strip()
                    if text and len(text) < 100:  # Sanity check
                        author = text
                        break
        
        return author
    
    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract publish date"""
        date_str = None
        
        # Try meta tags first
        date_meta_names = [
            'article:published_time',
            'datePublished',
            'pubdate',
            'publishdate',
            'date',
            'DC.date.issued',
            'publish_date'
        ]
        
        for name in date_meta_names:
            meta = soup.find('meta', {'property': name}) or soup.find('meta', {'name': name})
            if meta and meta.get('content'):
                date_str = meta.get('content')
                break
        
        # Try time tag
        if not date_str:
            time_tag = soup.find('time')
            if time_tag:
                date_str = time_tag.get('datetime') or time_tag.get_text()
        
        return date_str
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main article content"""
        # Remove script and style elements
        for script in soup(["script", "style", "noscript"]):
            script.decompose()
        
        # Try to find article body
        content_candidates = [
            soup.find('div', {'class': 'article-body'}),
            soup.find('div', {'class': 'article-content'}),
            soup.find('div', {'class': 'entry-content'}),
            soup.find('div', {'class': 'post-content'}),
            soup.find('article'),
            soup.find('main'),
            soup.find('div', {'id': 'article-body'}),
            soup.find('div', {'class': 'story-body'}),
            soup.find('div', {'class': 'content'}),
            soup.find('div', {'itemprop': 'articleBody'})
        ]
        
        # Find the best content container
        best_content = None
        max_length = 0
        
        for candidate in content_candidates:
            if candidate:
                text = candidate.get_text(separator=' ', strip=True)
                if len(text) > max_length:
                    max_length = len(text)
                    best_content = text
        
        # Fallback: get all paragraphs
        if not best_content or max_length < 500:
            paragraphs = soup.find_all('p')
            if paragraphs:
                all_text = ' '.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50])
                if len(all_text) > max_length:
                    best_content = all_text
        
        return best_content or "Could not extract article content"
    
    def _extract_content_smart(self, soup: BeautifulSoup, url: str) -> str:
        """Extract content with domain-specific selectors"""
        # Remove script and style elements
        for script in soup(["script", "style", "noscript", "iframe"]):
            script.decompose()
        
        # Domain-specific selectors
        domain = urlparse(url).netloc.lower()
        domain_selectors = {
            'washingtonpost.com': [
                {'class': 'article-body'},
                {'class': 'story-body'},
                {'data-qa': 'article-body'}
            ],
            'nytimes.com': [
                {'class': 'story-body'},
                {'class': 'story-content'},
                {'name': 'articleBody'}
            ],
            'thehill.com': [
                {'class': 'article__text'},
                {'class': 'content-wrp'},
                {'id': 'article-text'}
            ],
            'axios.com': [
                {'class': 'story-body'},
                {'class': 'content-body'}
            ],
            'reuters.com': [
                {'class': 'article-body'},
                {'data-testid': 'article-body'}
            ],
            'wsj.com': [
                {'class': 'article-content'},
                {'class': 'story-body'}
            ],
            'ft.com': [
                {'class': 'article__content'},
                {'class': 'body-content'}
            ]
        }
        
        # Try domain-specific selectors first
        for domain_key, selectors in domain_selectors.items():
            if domain_key in domain:
                for selector in selectors:
                    content = soup.find('div', selector)
                    if content:
                        text = content.get_text(separator=' ', strip=True)
                        if len(text) > 500:
                            return text
        
        # Fall back to general extraction
        return self._extract_content(soup)
    
    def extract_from_text(self, text: str) -> Dict[str, Any]:
        """Extract data from raw text (for API compatibility)"""
        return {
            'success': True,
            'title': 'Text Analysis',
            'text': text,
            'author': None,
            'publish_date': datetime.now().isoformat(),
            'url': None,
            'domain': 'text-input',
            'word_count': len(text.split())
        }
