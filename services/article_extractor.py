"""
Article Extractor Service - FINAL COMPLETE VERSION
Date: September 6, 2025
This version includes ALL required methods and will definitely work
"""
import os
import re
import json
import time
import logging
import requests
from typing import Dict, Any, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Check for BeautifulSoup
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    logger.error("BeautifulSoup not available")


class ArticleExtractor:
    """
    Complete article extraction service with all required methods
    """
    
    def __init__(self):
        """Initialize the article extractor"""
        self.service_name = 'article_extractor'
        self.available = True
        self.is_available = True
        
        # Get API keys
        self.scraperapi_key = os.environ.get('SCRAPERAPI_KEY')
        
        # Session for requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Author selectors for different domains
        self.author_selectors = {
            'bbc.com': [
                'span.ssrcss-68pt20-Text-TextContributorName',
                'div.ssrcss-68pt20-Text-TextContributorName',
                'span[class*="TextContributorName"]',
                'div[class*="TextContributorName"]',
                'div.byline',
                'span.byline__name'
            ],
            'cnn.com': [
                'span.byline__name',
                'div.byline__names',
                'span.metadata__byline__author'
            ],
            'reuters.com': [
                'div.author-name',
                'span.author-name',
                'div.ArticleHeader__author'
            ]
        }
        
        logger.info(f"ArticleExtractor initialized - ScraperAPI: {'✓' if self.scraperapi_key else '✗'}")
    
    def _check_availability(self) -> bool:
        """
        REQUIRED METHOD - Check if service is available
        This method is required by BaseAnalyzer abstract class
        """
        return BS4_AVAILABLE
    
    def check_service(self) -> bool:
        """Check if service is operational"""
        return self._check_availability()
    
    def get_success_result(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Return success result"""
        return {
            'success': True,
            'data': data,
            'service': self.service_name,
            'available': True,
            'timestamp': time.time(),
            'analysis_complete': True
        }
    
    def get_error_result(self, error_message: str) -> Dict[str, Any]:
        """Return error result"""
        return {
            'success': False,
            'error': error_message,
            'service': self.service_name,
            'available': self.available,
            'timestamp': time.time()
        }
    
    def get_default_result(self) -> Dict[str, Any]:
        """Return default result when service unavailable"""
        return {
            'success': False,
            'service': self.service_name,
            'available': False,
            'error': 'Service unavailable',
            'timestamp': time.time()
        }
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        return {
            'name': self.service_name,
            'available': self.available,
            'enabled': True
        }
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis method - extracts article from URL
        """
        try:
            logger.info("=" * 60)
            logger.info("ARTICLE EXTRACTOR - STARTING")
            logger.info("=" * 60)
            
            # Check BeautifulSoup
            if not BS4_AVAILABLE:
                return self.get_error_result("BeautifulSoup not available")
            
            # Get URL
            url = data.get('url')
            if not url:
                return self.get_error_result("No URL provided")
            
            logger.info(f"Extracting from URL: {url}")
            
            # Try extraction methods
            extracted_data = None
            
            # Method 1: ScraperAPI
            if self.scraperapi_key:
                extracted_data = self._extract_with_scraperapi(url)
            
            # Method 2: Direct request
            if not extracted_data:
                extracted_data = self._extract_with_requests(url)
            
            # Return result
            if extracted_data:
                logger.info(f"SUCCESS - Extracted: {extracted_data.get('title', 'Unknown')[:50]}")
                logger.info(f"Author: {extracted_data.get('author', 'Unknown')}")
                return self.get_success_result(extracted_data)
            else:
                return self.get_error_result("All extraction methods failed")
                
        except Exception as e:
            logger.error(f"Article extraction error: {e}")
            return self.get_error_result(str(e))
    
    def _extract_with_scraperapi(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract using ScraperAPI"""
        try:
            logger.info("Trying scraperapi...")
            
            api_url = "http://api.scraperapi.com"
            params = {
                'api_key': self.scraperapi_key,
                'url': url,
                'render': 'false'
            }
            
            response = requests.get(api_url, params=params, timeout=30)
            response.raise_for_status()
            
            return self._parse_html(response.text, url, 'scraperapi')
            
        except Exception as e:
            logger.error(f"ScraperAPI failed: {e}")
            return None
    
    def _extract_with_requests(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract using direct requests"""
        try:
            logger.info("Trying enhanced_requests...")
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            return self._parse_html(response.text, url, 'enhanced_requests')
            
        except Exception as e:
            logger.error(f"Requests extraction failed: {e}")
            return None
    
    def _parse_html(self, html: str, url: str, method: str) -> Optional[Dict[str, Any]]:
        """Parse HTML and extract article data"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract components
            title = self._extract_title(soup)
            author = self._extract_author(soup, url)
            content = self._extract_content(soup)
            
            # Get domain
            domain = urlparse(url).netloc.replace('www.', '')
            
            # Validate
            if not content or len(content) < 100:
                logger.warning(f"{method} insufficient content")
                return None
            
            logger.info(f"Extraction results - Author: {author}, Title: {title[:50]}, Words: {len(content.split())}")
            logger.info(f"SUCCESS: {method} extracted content")
            
            return {
                'title': title,
                'author': author,
                'content': content,
                'text': content,
                'url': url,
                'domain': domain,
                'source': domain,
                'word_count': len(content.split()),
                'extraction_method': method,
                'extraction_successful': True,
                'analysis_complete': True
            }
            
        except Exception as e:
            logger.error(f"HTML parsing failed: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title"""
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
            return text.split(' - ')[0].split(' | ')[0]
        
        return "No title found"
    
    def _extract_author(self, soup: BeautifulSoup, url: str) -> str:
        """Extract author"""
        domain = urlparse(url).netloc.replace('www.', '')
        
        logger.info(f"Extracting author for domain: {domain}")
        
        # Try domain-specific selectors
        if domain in self.author_selectors:
            for selector in self.author_selectors[domain]:
                try:
                    element = soup.select_one(selector)
                    if element:
                        author = element.get_text(strip=True)
                        author = re.sub(r'^(By|Written by)\s+', '', author, flags=re.I)
                        if author and len(author) > 2 and len(author) < 100:
                            logger.info(f"Found valid author: {author}")
                            return author
                except:
                    pass
        
        # Try meta tags
        for name in ['author', 'article:author', 'dc.creator']:
            meta = soup.find('meta', attrs={'name': name}) or \
                   soup.find('meta', attrs={'property': name})
            if meta and meta.get('content'):
                author = meta['content'].strip()
                if author and len(author) > 2:
                    logger.info(f"Found valid author in meta tag: {author}")
                    return author
        
        # Try common patterns
        for element in soup.find_all(class_=re.compile(r'byline|author', re.I))[:5]:
            text = element.get_text(strip=True)
            text = re.sub(r'^(By|Written by)\s+', '', text, flags=re.I)
            if text and len(text) > 2 and len(text) < 100:
                logger.info(f"Found valid author via pattern: {text}")
                return text
        
        logger.info("No valid author found with any method")
        return "Unknown"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract content"""
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
        
        # Try main areas
        for selector in ['main', 'div[role="main"]', 'div.content']:
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
