"""
Article Extractor Service - COMPLETE FIXED VERSION
Date: September 28, 2025
Last Updated: September 28, 2025

FIXES:
- Returns actual article content instead of garbage fallback data
- Properly structures response for pipeline consumption
- Includes emergency extraction fallback
- Maintains all existing helper methods
"""
import os
import re
import json
import time
import logging
import requests
from typing import Dict, Any, Optional, List
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
    Complete article extraction service with robust extraction
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
                'span.byline__name',
                'p[class*="Contributor"]',
                'div[class*="contributor"]',
                'span.qa-contributor-name',
                'div[class*="ssrcss"][class*="Text"]',
                'p[class*="ssrcss"]'
            ],
            'bbc.co.uk': [  # Same as bbc.com
                'span.ssrcss-68pt20-Text-TextContributorName',
                'div.ssrcss-68pt20-Text-TextContributorName',
                'span[class*="TextContributorName"]',
                'div[class*="TextContributorName"]',
                'div.byline',
                'span.byline__name',
                'p[class*="Contributor"]',
                'div[class*="contributor"]',
                'span.qa-contributor-name',
                'div[class*="ssrcss"][class*="Text"]',
                'p[class*="ssrcss"]'
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
            ],
            'chicagotribune.com': [
                'span.byline',
                'div.byline',
                'span[class*="author"]',
                'div[class*="author"]'
            ]
        }
        
        logger.info(f"ArticleExtractor initialized - ScraperAPI: {'✓' if self.scraperapi_key else '✗'}")
    
    def _check_availability(self) -> bool:
        """
        REQUIRED METHOD - Check if service is available
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
        FIXED: Extract article and return ACTUAL CONTENT
        This replaces the broken method that returns fallback garbage
        """
        try:
            logger.info("=" * 60)
            logger.info("ARTICLE EXTRACTOR - STARTING")
            logger.info("=" * 60)
            
            # Check BeautifulSoup
            if not BS4_AVAILABLE:
                # Don't return fallback - return actual error
                logger.error("BeautifulSoup not available")
                return {
                    'success': False,
                    'service': self.service_name,
                    'error': 'BeautifulSoup not installed',
                    'timestamp': time.time()
                }
            
            # Get URL
            url = data.get('url')
            if not url:
                logger.error("No URL provided")
                return {
                    'success': False,
                    'service': self.service_name,
                    'error': 'No URL provided',
                    'timestamp': time.time()
                }
            
            logger.info(f"Extracting from URL: {url}")
            
            # Try extraction methods
            extracted_data = None
            
            # Method 1: ScraperAPI (if available)
            if self.scraperapi_key:
                logger.info("Attempting ScraperAPI extraction...")
                extracted_data = self._extract_with_scraperapi(url)
                if extracted_data:
                    logger.info(f"ScraperAPI SUCCESS: Got {extracted_data.get('word_count', 0)} words")
            
            # Method 2: Direct request with enhanced headers
            if not extracted_data:
                logger.info("Attempting direct extraction...")
                extracted_data = self._extract_with_requests(url)
                if extracted_data:
                    logger.info(f"Direct extraction SUCCESS: Got {extracted_data.get('word_count', 0)} words")
            
            # CRITICAL FIX: Return the actual article data, not garbage
            if extracted_data:
                logger.info(f"✓ Extraction successful - Title: {extracted_data.get('title', '')[:50]}")
                logger.info(f"✓ Word count: {extracted_data.get('word_count', 0)}")
                
                # FIXED: Return article data in the correct format
                result = {
                    'success': True,
                    'service': self.service_name,
                    'available': True,
                    'timestamp': time.time(),
                    'analysis_complete': True
                }
                
                # CRITICAL: Merge article data at root level, not nested
                result.update(extracted_data)
                
                # Ensure all required fields exist
                result.setdefault('title', 'Untitled Article')
                result.setdefault('author', 'Unknown')
                result.setdefault('content', result.get('text', ''))
                result.setdefault('text', result.get('content', ''))
                result.setdefault('domain', urlparse(url).netloc.replace('www.', ''))
                result.setdefault('source', result.get('domain', 'Unknown'))
                result.setdefault('word_count', len(result.get('text', '').split()))
                
                return result
            else:
                # Extraction failed - try emergency fallback
                logger.warning("All extraction methods failed - attempting emergency extraction")
                
                # Emergency extraction - just get SOMETHING
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
                    }
                    
                    response = requests.get(url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Remove scripts and styles
                        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                            element.decompose()
                        
                        # Get title
                        title = 'Untitled'
                        if soup.title:
                            title = soup.title.get_text(strip=True)
                        elif soup.find('h1'):
                            title = soup.find('h1').get_text(strip=True)
                        
                        # Get all text
                        text = soup.get_text(separator=' ', strip=True)
                        
                        # Clean up text
                        text = ' '.join(text.split())  # Remove extra whitespace
                        
                        if len(text) > 200:  # Got some content
                            logger.info(f"Emergency extraction got {len(text)} characters")
                            
                            return {
                                'success': True,
                                'service': self.service_name,
                                'available': True,
                                'timestamp': time.time(),
                                'title': title[:200],
                                'author': 'Unknown',
                                'text': text[:10000],  # Limit to 10k chars
                                'content': text[:10000],
                                'url': url,
                                'domain': urlparse(url).netloc.replace('www.', ''),
                                'source': urlparse(url).netloc.replace('www.', ''),
                                'word_count': len(text.split()),
                                'extraction_method': 'emergency',
                                'extraction_successful': True,
                                'analysis_complete': True
                            }
                    
                except Exception as e:
                    logger.error(f"Emergency extraction failed: {e}")
                
                # All methods failed - return error (NOT garbage data)
                logger.error(f"Unable to extract article from {url}")
                return {
                    'success': False,
                    'service': self.service_name,
                    'available': True,
                    'error': f'Unable to extract article from {url}',
                    'timestamp': time.time(),
                    # Include minimal data so analysis can proceed
                    'title': f'Article from {urlparse(url).netloc}',
                    'author': 'Unknown',
                    'text': f'Unable to extract content from {url}. Please try a different article.',
                    'content': f'Unable to extract content from {url}. Please try a different article.',
                    'url': url,
                    'domain': urlparse(url).netloc.replace('www.', ''),
                    'source': urlparse(url).netloc.replace('www.', ''),
                    'word_count': 0
                }
                
        except Exception as e:
            logger.error(f"Article extraction error: {e}", exc_info=True)
            return {
                'success': False,
                'service': self.service_name,
                'available': self.is_available,
                'error': str(e),
                'timestamp': time.time()
            }
    
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
            author = self._extract_author(soup, url, html)
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
    
    def _extract_author(self, soup: BeautifulSoup, url: str, html_text: str = "") -> str:
        """Enhanced author extraction with robust BBC support"""
        domain = urlparse(url).netloc.replace('www.', '')
        
        logger.info(f"Extracting author for domain: {domain}")
        
        # Special handling for BBC
        if 'bbc.com' in domain or 'bbc.co.uk' in domain:
            authors = self._extract_bbc_authors_robust(soup, html_text)
            if authors:
                # Join multiple authors with " and "
                author_string = ' and '.join(authors)
                logger.info(f"Found BBC author(s): {author_string}")
                return author_string
        
        # Try domain-specific selectors
        if domain in self.author_selectors:
            for selector in self.author_selectors[domain]:
                try:
                    element = soup.select_one(selector)
                    if element:
                        author = element.get_text(strip=True)
                        author = self._clean_author_text(author)
                        if author and len(author) > 2 and len(author) < 100:
                            logger.info(f"Found valid author: {author}")
                            return author
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
        
        # Generic author extraction
        return self._extract_generic_author(soup)
    
    def _extract_bbc_authors_robust(self, soup: BeautifulSoup, html_text: str = "") -> List[str]:
        """Robust BBC author extraction"""
        authors = []
        
        # Try various BBC selectors
        selectors = [
            'span.ssrcss-68pt20-Text-TextContributorName',
            'div.ssrcss-68pt20-Text-TextContributorName',
            'span[class*="TextContributorName"]',
            'div[class*="TextContributorName"]',
            'span[class*="Contributor"]',
            'div[class*="Contributor"]'
        ]
        
        for selector in selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    author = element.get_text(strip=True)
                    author = self._clean_author_text(author)
                    if author and len(author) > 2 and len(author) < 100:
                        if author not in authors:
                            authors.append(author)
            except Exception as e:
                logger.debug(f"BBC selector {selector} failed: {e}")
                continue
        
        return authors
    
    def _extract_generic_author(self, soup: BeautifulSoup) -> str:
        """Generic author extraction"""
        # Try meta tags
        for meta_name in ['author', 'article:author', 'DC.creator']:
            meta = soup.find('meta', attrs={'name': meta_name})
            if meta and meta.get('content'):
                return self._clean_author_text(meta['content'])
        
        # Try common selectors
        selectors = [
            '.author-name', '.by-author', '.article-author',
            '[rel="author"]', '.byline', 'span.author'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                author = element.get_text(strip=True)
                author = self._clean_author_text(author)
                if author and len(author) > 2 and len(author) < 100:
                    return author
        
        return "Unknown"
    
    def _clean_author_text(self, text: str) -> str:
        """Clean author text"""
        if not text:
            return ""
        
        # Remove common prefixes
        text = re.sub(r'^(by|from|written by)\s+', '', text, flags=re.I)
        
        # Remove BBC specific text
        text = re.sub(r'BBC.*?correspondent', '', text, flags=re.I)
        text = re.sub(r'.*?correspondent', '', text, flags=re.I)
        
        # Remove role descriptions
        text = re.sub(r',\s*(Reporter|Writer|Journalist|Editor|Correspondent|Staff Writer).*', '', text, flags=re.I)
        
        # Clean up
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract content"""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Try article tag
        article = soup.find('article')
        if article:
            paragraphs = article.find_all('p')
            if paragraphs:
                content = ' '.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
                if len(content) > 200:
                    return content
        
        # Try main areas
        for selector in ['main', 'div[role="main"]', 'div.content', 'div[class*="article-body"]', 'div[class*="story-body"]']:
            element = soup.select_one(selector)
            if element:
                paragraphs = element.find_all('p')
                if paragraphs:
                    content = ' '.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
                    if len(content) > 200:
                        return content
        
        # Fallback: all paragraphs
        all_p = soup.find_all('p')
        content = ' '.join([p.get_text(strip=True) for p in all_p if len(p.get_text(strip=True)) > 30])
        return content
