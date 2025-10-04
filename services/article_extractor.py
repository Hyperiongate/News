"""
Article Extractor Service - CLEAN AND WORKING
Date: October 4, 2025
Version: 12.0

This is a COMPLETE, CLEAN replacement for services/article_extractor.py
- Simplified extraction that works
- ScraperAPI when available, direct fetch as fallback
- Proper error handling
- Clean data structure
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
    Clean article extractor that actually works
    """
    
    def __init__(self):
        """Initialize extractor with clean configuration"""
        self.scraperapi_key = os.getenv('SCRAPERAPI_KEY', '')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        self.is_available = True
        self.service_name = 'article_extractor'
        
        logger.info(f"[ArticleExtractor] Initialized - ScraperAPI: {'YES' if self.scraperapi_key else 'NO'}")
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point for extraction"""
        
        url = data.get('url', '')
        text = data.get('text', '') or data.get('content', '')
        
        try:
            if url and url.startswith('http'):
                logger.info(f"[ArticleExtractor] Extracting from URL: {url}")
                article_data = self._extract_from_url(url)
            elif text:
                logger.info(f"[ArticleExtractor] Processing text: {len(text)} chars")
                article_data = self._process_text(text)
            else:
                return {
                    'service': self.service_name,
                    'success': False,
                    'error': 'No URL or text provided',
                    'data': {}
                }
            
            # Return clean, flat structure
            return {
                'service': self.service_name,
                'success': article_data.get('extraction_successful', False),
                'data': article_data
            }
            
        except Exception as e:
            logger.error(f"[ArticleExtractor] Error: {e}")
            return {
                'service': self.service_name,
                'success': False,
                'error': str(e),
                'data': {}
            }
    
    def _extract_from_url(self, url: str) -> Dict[str, Any]:
        """Extract article from URL"""
        
        # Try ScraperAPI first if available
        if self.scraperapi_key:
            try:
                logger.info("[ArticleExtractor] Trying ScraperAPI...")
                html = self._fetch_with_scraperapi(url)
                if html:
                    result = self._parse_html(html, url)
                    if result['extraction_successful']:
                        logger.info(f"[ArticleExtractor] ✓ ScraperAPI success: {result['word_count']} words")
                        return result
            except Exception as e:
                logger.warning(f"[ArticleExtractor] ScraperAPI failed: {e}")
        
        # Fallback to direct fetch
        try:
            logger.info("[ArticleExtractor] Trying direct fetch...")
            html = self._fetch_direct(url)
            if html:
                result = self._parse_html(html, url)
                if result['extraction_successful']:
                    logger.info(f"[ArticleExtractor] ✓ Direct fetch success: {result['word_count']} words")
                    return result
        except Exception as e:
            logger.warning(f"[ArticleExtractor] Direct fetch failed: {e}")
        
        # Return failure result
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
        """Fetch using ScraperAPI"""
        
        api_url = 'https://api.scraperapi.com'
        params = {
            'api_key': self.scraperapi_key,
            'url': url,
            'render': 'false',  # Faster without JS rendering
            'country_code': 'us'
        }
        
        response = self.session.get(api_url, params=params, timeout=30)
        
        if response.status_code == 200:
            return response.text
        
        return None
    
    def _fetch_direct(self, url: str) -> Optional[str]:
        """Direct fetch with multiple user agents"""
        
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'
        ]
        
        for ua in user_agents:
            try:
                headers = self.session.headers.copy()
                headers['User-Agent'] = ua
                headers['Referer'] = 'https://www.google.com/'
                
                response = self.session.get(url, headers=headers, timeout=15, allow_redirects=True)
                
                if response.status_code == 200:
                    return response.text
                    
            except:
                continue
        
        return None
    
    def _parse_html(self, html: str, url: str) -> Dict[str, Any]:
        """Parse HTML and extract article data"""
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Extract components
        title = self._extract_title(soup)
        text = self._extract_text(soup)
        author = self._extract_author(soup)
        source = self._get_source_from_url(url)
        domain = urlparse(url).netloc.replace('www.', '')
        
        # Calculate metrics
        word_count = len(text.split()) if text else 0
        sources_count = self._count_sources(text)
        quotes_count = self._count_quotes(text)
        
        # Determine if extraction was successful
        extraction_successful = len(text) > 200
        
        return {
            'title': title,
            'author': author,
            'text': text,
            'content': text,  # Duplicate for compatibility
            'source': source,
            'domain': domain,
            'url': url,
            'word_count': word_count,
            'sources_count': sources_count,
            'quotes_count': quotes_count,
            'extraction_successful': extraction_successful,
            'extraction_method': 'scraperapi' if self.scraperapi_key else 'direct'
        }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title"""
        
        # Try multiple methods
        methods = [
            lambda: soup.find('meta', property='og:title')['content'] if soup.find('meta', property='og:title') else None,
            lambda: soup.find('h1').get_text().strip() if soup.find('h1') else None,
            lambda: soup.find('title').get_text().strip() if soup.find('title') else None,
            lambda: soup.find('meta', {'name': 'twitter:title'})['content'] if soup.find('meta', {'name': 'twitter:title'}) else None
        ]
        
        for method in methods:
            try:
                title = method()
                if title:
                    return title
            except:
                continue
        
        return "Unknown Title"
    
    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract main article text"""
        
        # Try common article containers
        selectors = [
            'article',
            '[role="main"]',
            '.article-body',
            '.story-body',
            '.entry-content',
            '.post-content',
            'main',
            '.content'
        ]
        
        for selector in selectors:
            container = soup.select_one(selector)
            if container:
                paragraphs = container.find_all(['p', 'h2', 'h3'])
                text = ' '.join([p.get_text().strip() for p in paragraphs])
                if len(text) > 200:
                    return text
        
        # Fallback: all paragraphs
        paragraphs = soup.find_all('p')
        text = ' '.join([
            p.get_text().strip() 
            for p in paragraphs 
            if len(p.get_text().strip()) > 30
        ])
        
        return text
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """Extract author name"""
        
        # Try meta tags
        for attr, value in [('name', 'author'), ('property', 'article:author')]:
            meta = soup.find('meta', {attr: value})
            if meta and meta.get('content'):
                author = meta['content'].strip()
                # Clean common prefixes
                author = re.sub(r'^(by|By|BY)\s+', '', author)
                if author and len(author) < 100:
                    return author
        
        # Try byline
        byline = soup.find(class_=re.compile(r'byline|author', re.I))
        if byline:
            text = byline.get_text().strip()
            text = re.sub(r'^(by|By|BY)\s+', '', text)
            if text and len(text) < 100:
                return text
        
        return "Unknown"
    
    def _get_source_from_url(self, url: str) -> str:
        """Get source name from URL"""
        
        domain = urlparse(url).netloc.replace('www.', '')
        
        source_map = {
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
        
        return source_map.get(domain, domain.title())
    
    def _count_sources(self, text: str) -> int:
        """Count source citations"""
        
        if not text:
            return 0
        
        patterns = ['according to', 'said', 'reported', 'stated', 'told', 'confirmed']
        count = sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in patterns)
        
        return min(count, 20)
    
    def _count_quotes(self, text: str) -> int:
        """Count direct quotes"""
        
        if not text:
            return 0
        
        return len(re.findall(r'"[^"]{10,}"', text))
    
    def _process_text(self, text: str) -> Dict[str, Any]:
        """Process direct text input"""
        
        lines = text.strip().split('\n')
        title = lines[0][:100] if lines else "Direct Text Input"
        
        return {
            'title': title,
            'author': 'User Provided',
            'text': text,
            'content': text,
            'source': 'Direct Input',
            'domain': 'text_input',
            'url': '',
            'word_count': len(text.split()),
            'sources_count': self._count_sources(text),
            'quotes_count': self._count_quotes(text),
            'extraction_successful': True,
            'extraction_method': 'text_input'
        }
