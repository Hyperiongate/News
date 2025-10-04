"""
Article Extractor - WORKING VERSION THAT USES SCRAPERAPI
Date: October 4, 2025
Version: 13.0

This ACTUALLY uses your ScraperAPI key when it's configured.
Complete replacement for services/article_extractor.py
"""

import os
import re
import time
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ArticleExtractor:
    """
    Article extractor that ACTUALLY USES ScraperAPI
    """
    
    def __init__(self):
        self.scraperapi_key = os.getenv('SCRAPERAPI_KEY', '').strip()
        self.session = requests.Session()
        
        # Basic headers for fallback
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        
        self.is_available = True
        self.service_name = 'article_extractor'
        self.available = True  # For compatibility
        
        if self.scraperapi_key:
            logger.info(f"[ArticleExtractor] ✓ ScraperAPI KEY FOUND: {self.scraperapi_key[:8]}...")
        else:
            logger.warning("[ArticleExtractor] ✗ No ScraperAPI key - will use fallback")
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Service interface - calls extract internally"""
        
        url = data.get('url', '')
        text = data.get('text', '') or data.get('content', '')
        
        logger.info(f"[ArticleExtractor] analyze() called - URL: {bool(url)}, Text: {bool(text)}")
        
        try:
            if url and url.startswith('http'):
                # Extract from URL
                result = self.extract(url)
            elif text:
                # Process text
                result = self._process_text(text)
            else:
                return {
                    'service': self.service_name,
                    'success': False,
                    'error': 'No URL or text provided',
                    'data': {}
                }
            
            # Wrap in service response
            return {
                'service': self.service_name,
                'success': result.get('extraction_successful', False),
                'data': result,
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"[ArticleExtractor] analyze() error: {e}")
            return {
                'service': self.service_name,
                'success': False,
                'error': str(e),
                'data': {}
            }
    
    def extract(self, url: str) -> Dict[str, Any]:
        """Main extraction method - USES SCRAPERAPI FIRST"""
        
        logger.info(f"[ArticleExtractor] Starting extraction for: {url}")
        logger.info(f"[ArticleExtractor] ScraperAPI key configured: {bool(self.scraperapi_key)}")
        
        # METHOD 1: ScraperAPI (if we have a key)
        if self.scraperapi_key:
            logger.info("[ArticleExtractor] METHOD 1: Trying ScraperAPI...")
            try:
                html = self._fetch_with_scraperapi(url)
                if html:
                    result = self._parse_html(html, url)
                    if result['extraction_successful']:
                        logger.info(f"[ArticleExtractor] ✓ ScraperAPI SUCCESS: {result['word_count']} words")
                        return result
                    else:
                        logger.warning("[ArticleExtractor] ScraperAPI returned content but parsing failed")
                else:
                    logger.warning("[ArticleExtractor] ScraperAPI returned no content")
            except Exception as e:
                logger.error(f"[ArticleExtractor] ScraperAPI error: {e}")
        
        # METHOD 2: Direct fetch as fallback
        logger.info("[ArticleExtractor] METHOD 2: Trying direct fetch...")
        try:
            html = self._fetch_direct(url)
            if html:
                result = self._parse_html(html, url)
                if result['extraction_successful']:
                    logger.info(f"[ArticleExtractor] ✓ Direct fetch SUCCESS: {result['word_count']} words")
                    return result
        except Exception as e:
            logger.error(f"[ArticleExtractor] Direct fetch error: {e}")
        
        # FAILED
        logger.error(f"[ArticleExtractor] ❌ All methods failed for {url}")
        
        return {
            'title': 'Extraction Failed',
            'author': 'Unknown',
            'text': '',
            'content': '',
            'source': self._get_source_from_url(url),
            'domain': urlparse(url).netloc.replace('www.', ''),
            'url': url,
            'word_count': 0,
            'extraction_successful': False,
            'sources_count': 0,
            'quotes_count': 0,
            'error': 'Could not extract article content'
        }
    
    def _fetch_with_scraperapi(self, url: str) -> Optional[str]:
        """ACTUALLY CALL SCRAPERAPI"""
        
        logger.info(f"[ScraperAPI] Making request with key: {self.scraperapi_key[:8]}...")
        
        # ScraperAPI endpoint
        api_url = 'http://api.scraperapi.com'
        
        # Parameters
        params = {
            'api_key': self.scraperapi_key,
            'url': url,
            'render': 'false',  # Don't render JavaScript
            'country_code': 'us'
        }
        
        logger.info(f"[ScraperAPI] Request URL: {api_url}")
        logger.info(f"[ScraperAPI] Target URL: {url}")
        
        try:
            response = requests.get(api_url, params=params, timeout=30)
            logger.info(f"[ScraperAPI] Response status: {response.status_code}")
            logger.info(f"[ScraperAPI] Response size: {len(response.text)} bytes")
            
            if response.status_code == 200 and len(response.text) > 100:
                return response.text
            else:
                logger.warning(f"[ScraperAPI] Bad response: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"[ScraperAPI] Request failed: {e}")
            return None
    
    def _fetch_direct(self, url: str) -> Optional[str]:
        """Direct fetch fallback"""
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
            
            if response.status_code == 200:
                return response.text
            else:
                logger.warning(f"[Direct] Status {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"[Direct] Failed: {e}")
            return None
    
    def _parse_html(self, html: str, url: str) -> Dict[str, Any]:
        """Parse HTML content"""
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
            tag.decompose()
        
        # Extract components
        title = self._extract_title(soup)
        text = self._extract_text(soup)
        author = self._extract_author(soup)
        source = self._get_source_from_url(url)
        domain = urlparse(url).netloc.replace('www.', '')
        
        # Metrics
        word_count = len(text.split()) if text else 0
        extraction_successful = len(text) > 200
        
        logger.info(f"[Parser] Title: {title[:50]}")
        logger.info(f"[Parser] Text length: {len(text)}")
        logger.info(f"[Parser] Word count: {word_count}")
        logger.info(f"[Parser] Successful: {extraction_successful}")
        
        return {
            'title': title,
            'author': author,
            'text': text,
            'content': text,  # Duplicate for compatibility
            'source': source,
            'domain': domain,
            'url': url,
            'word_count': word_count,
            'sources_count': self._count_sources(text),
            'quotes_count': self._count_quotes(text),
            'extraction_successful': extraction_successful,
            'extraction_method': 'scraperapi' if self.scraperapi_key else 'direct'
        }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title"""
        
        # Try og:title first
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        
        # Try h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        # Try title tag
        title = soup.find('title')
        if title:
            return title.get_text().strip()
        
        return "Unknown Title"
    
    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract article text"""
        
        # Try article tag
        article = soup.find('article')
        if article:
            paragraphs = article.find_all('p')
            text = ' '.join([p.get_text().strip() for p in paragraphs])
            if len(text) > 200:
                return text
        
        # Try common containers
        for selector in ['main', '[role="main"]', '.article-body', '.story-body', '.content', '.entry-content']:
            container = soup.select_one(selector)
            if container:
                paragraphs = container.find_all('p')
                text = ' '.join([p.get_text().strip() for p in paragraphs])
                if len(text) > 200:
                    return text
        
        # Fallback to all paragraphs
        paragraphs = soup.find_all('p')
        text = ' '.join([
            p.get_text().strip() 
            for p in paragraphs 
            if len(p.get_text().strip()) > 30
        ])
        
        return text
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """Extract author"""
        
        # Try meta author
        author_meta = soup.find('meta', {'name': 'author'})
        if author_meta and author_meta.get('content'):
            author = author_meta['content'].strip()
            author = re.sub(r'^(by|By)\s+', '', author)
            return author
        
        # Try byline
        byline = soup.find(class_=re.compile(r'byline|author', re.I))
        if byline:
            text = byline.get_text().strip()
            text = re.sub(r'^(by|By)\s+', '', text)
            if text and len(text) < 100:
                return text
        
        return "Unknown"
    
    def _get_source_from_url(self, url: str) -> str:
        """Get source name from URL"""
        
        domain = urlparse(url).netloc.replace('www.', '')
        
        sources = {
            'nytimes.com': 'The New York Times',
            'washingtonpost.com': 'The Washington Post',
            'bbc.com': 'BBC',
            'bbc.co.uk': 'BBC',
            'cnn.com': 'CNN',
            'foxnews.com': 'Fox News',
            'reuters.com': 'Reuters',
            'apnews.com': 'Associated Press',
            'theguardian.com': 'The Guardian',
            'wsj.com': 'The Wall Street Journal',
            'independent.co.uk': 'The Independent',
            'npr.org': 'NPR',
            'politico.com': 'Politico',
            'axios.com': 'Axios',
            'thehill.com': 'The Hill'
        }
        
        return sources.get(domain, domain.title())
    
    def _count_sources(self, text: str) -> int:
        """Count source citations"""
        if not text:
            return 0
        
        patterns = ['according to', 'said', 'reported', 'stated']
        count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in patterns)
        return min(count, 20)
    
    def _count_quotes(self, text: str) -> int:
        """Count quotes"""
        if not text:
            return 0
        return len(re.findall(r'"[^"]{10,}"', text))
    
    def _process_text(self, text: str) -> Dict[str, Any]:
        """Process direct text input"""
        
        lines = text.strip().split('\n')
        title = lines[0][:100] if lines else "Text Analysis"
        
        return {
            'title': title,
            'author': 'User Provided',
            'text': text,
            'content': text,
            'source': 'Direct Input',
            'domain': 'user_input',
            'url': '',
            'word_count': len(text.split()),
            'sources_count': self._count_sources(text),
            'quotes_count': self._count_quotes(text),
            'extraction_successful': True,
            'extraction_method': 'text_input'
        }
    
    def _check_availability(self) -> bool:
        """Service availability check"""
        return True
