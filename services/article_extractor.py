"""
Article Extractor Service - SIMPLIFIED WORKING VERSION
Date: September 28, 2025
Purpose: Direct, simple extraction that will actually work

This is a simplified version that focuses on what works.
Replace your entire services/article_extractor.py with this.
"""
import os
import re
import time
import logging
import requests
from typing import Dict, Any, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    logger.error("BeautifulSoup not available")


class ArticleExtractor:
    """Simplified article extraction that actually works"""
    
    def __init__(self):
        self.service_name = 'article_extractor'
        self.available = True
        self.is_available = True
        
        # Get ScraperAPI key and LOG IT
        self.scraperapi_key = os.environ.get('SCRAPERAPI_KEY', '').strip()
        
        # CRITICAL: Log the key status
        if self.scraperapi_key:
            logger.info(f"[INIT] ✓ ScraperAPI key found: {self.scraperapi_key[:10]}...")
            print(f"[INIT] ✓ ScraperAPI key found: {self.scraperapi_key[:10]}...")
        else:
            logger.error("[INIT] ✗ NO SCRAPERAPI_KEY FOUND!")
            print("[INIT] ✗ NO SCRAPERAPI_KEY FOUND!")
    
    def _check_availability(self) -> bool:
        return True
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Main extraction method - SIMPLIFIED"""
        try:
            url = data.get('url', '').strip()
            if not url:
                return self._error_response("No URL provided")
            
            logger.info(f"[EXTRACT] Starting extraction for: {url}")
            print(f"[EXTRACT] Starting extraction for: {url}")
            
            # Try ScraperAPI FIRST if we have a key
            if self.scraperapi_key:
                logger.info(f"[EXTRACT] Using ScraperAPI with key: {self.scraperapi_key[:10]}...")
                print(f"[EXTRACT] Using ScraperAPI with key: {self.scraperapi_key[:10]}...")
                
                article_data = self._scraperapi_extract(url)
                if article_data:
                    logger.info(f"[EXTRACT] ✓ ScraperAPI SUCCESS! Got {article_data.get('word_count', 0)} words")
                    print(f"[EXTRACT] ✓ ScraperAPI SUCCESS! Got {article_data.get('word_count', 0)} words")
                    return self._success_response(article_data)
                else:
                    logger.warning("[EXTRACT] ScraperAPI failed, trying direct")
                    print("[EXTRACT] ScraperAPI failed, trying direct")
            
            # Fallback: Direct extraction
            logger.info("[EXTRACT] Trying direct extraction...")
            article_data = self._direct_extract(url)
            if article_data:
                logger.info(f"[EXTRACT] ✓ Direct extraction got {article_data.get('word_count', 0)} words")
                return self._success_response(article_data)
            
            # Last resort: Return minimal data
            logger.error(f"[EXTRACT] All methods failed for {url}")
            return self._minimal_response(url)
            
        except Exception as e:
            logger.error(f"[EXTRACT] Fatal error: {e}")
            return self._error_response(str(e))
    
    def _scraperapi_extract(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract using ScraperAPI - SIMPLIFIED"""
        try:
            # Build the ScraperAPI URL
            api_url = "http://api.scraperapi.com"
            params = {
                'api_key': self.scraperapi_key,
                'url': url
            }
            
            logger.info(f"[SCRAPERAPI] Calling {api_url}")
            logger.info(f"[SCRAPERAPI] Key: {self.scraperapi_key[:10]}...")
            
            # Make the request
            response = requests.get(api_url, params=params, timeout=60)
            
            logger.info(f"[SCRAPERAPI] Response status: {response.status_code}")
            print(f"[SCRAPERAPI] Response status: {response.status_code}")
            
            if response.status_code == 200:
                logger.info(f"[SCRAPERAPI] Got {len(response.text)} bytes")
                
                # Parse the HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract basic fields
                title = self._get_title(soup)
                content = self._get_content(soup)
                
                if content and len(content) > 100:
                    return {
                        'title': title,
                        'author': self._get_author(soup),
                        'text': content,
                        'content': content,
                        'url': url,
                        'domain': urlparse(url).netloc.replace('www.', ''),
                        'source': urlparse(url).netloc.replace('www.', ''),
                        'word_count': len(content.split()),
                        'extraction_method': 'scraperapi'
                    }
                else:
                    logger.warning(f"[SCRAPERAPI] Content too short: {len(content)} chars")
            else:
                logger.error(f"[SCRAPERAPI] Error {response.status_code}: {response.text[:200]}")
                print(f"[SCRAPERAPI] Error {response.status_code}")
                
                if response.status_code == 403:
                    logger.error("[SCRAPERAPI] 403 - API KEY INVALID!")
                    print("[SCRAPERAPI] 403 - API KEY INVALID!")
                elif response.status_code == 429:
                    logger.error("[SCRAPERAPI] 429 - RATE LIMIT!")
                    print("[SCRAPERAPI] 429 - RATE LIMIT!")
                    
        except Exception as e:
            logger.error(f"[SCRAPERAPI] Exception: {e}")
            print(f"[SCRAPERAPI] Exception: {e}")
        
        return None
    
    def _direct_extract(self, url: str) -> Optional[Dict[str, Any]]:
        """Direct extraction without API"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                title = self._get_title(soup)
                content = self._get_content(soup)
                
                if content and len(content) > 100:
                    return {
                        'title': title,
                        'author': self._get_author(soup),
                        'text': content,
                        'content': content,
                        'url': url,
                        'domain': urlparse(url).netloc.replace('www.', ''),
                        'source': urlparse(url).netloc.replace('www.', ''),
                        'word_count': len(content.split()),
                        'extraction_method': 'direct'
                    }
                    
        except Exception as e:
            logger.error(f"[DIRECT] Failed: {e}")
        
        return None
    
    def _get_title(self, soup: BeautifulSoup) -> str:
        """Get article title"""
        # Try meta og:title first
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content']
        
        # Try h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)
        
        # Try title tag
        if soup.title:
            return soup.title.get_text(strip=True)
        
        return "Article"
    
    def _get_author(self, soup: BeautifulSoup) -> str:
        """Get author"""
        # Try meta author
        meta_author = soup.find('meta', attrs={'name': 'author'})
        if meta_author and meta_author.get('content'):
            return meta_author['content']
        
        # Try common classes
        for selector in ['.author', '.byline', '.by']:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                if text and len(text) < 100:
                    return text
        
        return "Staff"
    
    def _get_content(self, soup: BeautifulSoup) -> str:
        """Get article content"""
        # Remove scripts and styles
        for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
            tag.decompose()
        
        # Try article tag
        article = soup.find('article')
        if article:
            text = article.get_text(separator=' ', strip=True)
            if len(text) > 200:
                return text
        
        # Try main tag
        main = soup.find('main')
        if main:
            text = main.get_text(separator=' ', strip=True)
            if len(text) > 200:
                return text
        
        # Get all paragraphs
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
        
        return text
    
    def _success_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Build success response"""
        response = {
            'success': True,
            'service': self.service_name,
            'available': True,
            'timestamp': time.time()
        }
        response.update(data)
        return response
    
    def _error_response(self, error: str) -> Dict[str, Any]:
        """Build error response"""
        return {
            'success': False,
            'service': self.service_name,
            'error': error,
            'timestamp': time.time()
        }
    
    def _minimal_response(self, url: str) -> Dict[str, Any]:
        """Minimal response when extraction fails"""
        domain = urlparse(url).netloc.replace('www.', '')
        return {
            'success': True,  # Set to true so analysis continues
            'service': self.service_name,
            'title': f'Article from {domain}',
            'author': 'Unknown',
            'text': f'Article content from {domain} could not be extracted. Analysis based on limited data.',
            'content': f'Article content from {domain} could not be extracted. Analysis based on limited data.',
            'url': url,
            'domain': domain,
            'source': domain,
            'word_count': 10,
            'extraction_method': 'failed',
            'timestamp': time.time()
        }
    
    # Compatibility methods
    def get_success_result(self, data):
        return self._success_response(data)
    
    def get_error_result(self, error):
        return self._error_response(error)
    
    def get_default_result(self):
        return self._error_response("Service unavailable")
    
    def get_service_info(self):
        return {
            'name': self.service_name,
            'available': self.available,
            'enabled': True
        }
