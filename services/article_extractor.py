"""
FILE: services/article_extractor.py
Enhanced article extractor with advanced scraping capabilities
Handles paywalls, CloudFlare, and JavaScript-rendered sites
"""

import os
import logging
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
from datetime import datetime
import json
from urllib.parse import urlparse
import time
import random
from fake_useragent import UserAgent

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

logger = logging.getLogger(__name__)

class ArticleExtractor:
    """Enhanced article extractor with multiple fallback methods"""
    
    def __init__(self):
        self.timeout = 30
        self.delay_range = (0.5, 2)
        self.ua = UserAgent()
        
        # Initialize session for connection pooling
        self.session = requests.Session()
        self.session.headers.update(self._get_headers())
        
        # Initialize cloudscraper if available
        if CLOUDSCRAPER_AVAILABLE:
            self.cloudscraper_session = cloudscraper.create_scraper()
            self.cloudscraper_session.headers.update(self._get_headers())
            
        logger.info(f"ArticleExtractor initialized (CloudScraper: {CLOUDSCRAPER_AVAILABLE}, Curl-CFFI: {CURL_CFFI_AVAILABLE})")
    
    def _get_headers(self):
        """Get randomized headers that look like a real browser"""
        return {
            'User-Agent': self.ua.random,
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
    
    def _delay(self):
        """Random delay to avoid rate limiting"""
        time.sleep(random.uniform(*self.delay_range))
    
    def extract_from_url(self, url: str) -> Dict[str, Any]:
        """
        Extract article content from URL using multiple methods
        
        Returns:
            Dict containing article data or error information
        """
        logger.info(f"Extracting article from: {url}")
        
        # Try methods in order of speed/reliability
        methods = [
            ("standard requests", self._extract_with_requests),
        ]
        
        # Only add advanced methods if available
        if CLOUDSCRAPER_AVAILABLE:
            methods.append(("cloudscraper", self._extract_with_cloudscraper))
        if CURL_CFFI_AVAILABLE:
            methods.append(("curl-cffi", self._extract_with_curl_cffi))
        
        last_error = None
        for method_name, method_func in methods:
            try:
                logger.info(f"Trying {method_name}...")
                content = method_func(url)
                if content:
                    logger.info(f"Success with {method_name}")
                    return self._parse_article(content, url)
            except Exception as e:
                logger.warning(f"{method_name} failed: {str(e)}")
                last_error = str(e)
                continue
        
        # All methods failed
        error_msg = f"All extraction methods failed. Last error: {last_error}"
        logger.error(error_msg)
        return {
            'success': False,
            'error': error_msg,
            'url': url
        }
    
    def _extract_with_requests(self, url: str) -> Optional[str]:
        """Standard requests method"""
        self._delay()
        
        # Update headers with fresh user agent
        self.session.headers.update({'User-Agent': self.ua.random})
        
        response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
        response.raise_for_status()
        
        # Check if we got real content
        if len(response.text) < 1000:
            raise Exception("Response too short, likely blocked")
            
        return response.text
    
    def _extract_with_cloudscraper(self, url: str) -> Optional[str]:
        """CloudScraper method for CloudFlare bypass"""
        if not CLOUDSCRAPER_AVAILABLE:
            raise Exception("CloudScraper not available")
            
        self._delay()
        
        # Update headers
        self.cloudscraper_session.headers.update({'User-Agent': self.ua.random})
        
        response = self.cloudscraper_session.get(url, timeout=self.timeout)
        response.raise_for_status()
        
        if len(response.text) < 1000:
            raise Exception("Response too short, likely blocked")
            
        return response.text
    
    def _extract_with_curl_cffi(self, url: str) -> Optional[str]:
        """Curl-CFFI method for TLS fingerprinting bypass"""
        if not CURL_CFFI_AVAILABLE:
            raise Exception("Curl-CFFI not available")
            
        self._delay()
        
        # Use Chrome TLS fingerprint
        response = curl_requests.get(
            url, 
            impersonate='chrome110',
            headers=self._get_headers(),
            timeout=self.timeout
        )
        response.raise_for_status()
        
        if len(response.text) < 1000:
            raise Exception("Response too short, likely blocked")
            
        return response.text
    
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
            
            # Content extraction
            content = self._extract_content(soup)
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
