"""
Enhanced Article Extraction Service - FIXED with ScraperAPI Integration
CRITICAL FIX: Now properly utilizes upgraded ScraperAPI for web scraping
UNIVERSAL AUTHOR FIX: Robust author extraction for all news sites
"""

import json
import re
import time
import logging
import requests
import urllib3
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse, urljoin, quote
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import os
import ssl
import socket
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from services.base_analyzer import BaseAnalyzer

# Disable SSL warnings for development/testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Optional imports with better error handling
OPTIONAL_LIBRARIES = {}

try:
    from fake_useragent import UserAgent
    OPTIONAL_LIBRARIES['fake_useragent'] = True
except ImportError:
    OPTIONAL_LIBRARIES['fake_useragent'] = False

try:
    import cloudscraper
    OPTIONAL_LIBRARIES['cloudscraper'] = True
except ImportError:
    OPTIONAL_LIBRARIES['cloudscraper'] = False

try:
    from curl_cffi import requests as curl_requests
    OPTIONAL_LIBRARIES['curl_cffi'] = True
except ImportError:
    OPTIONAL_LIBRARIES['curl_cffi'] = False

logger = logging.getLogger(__name__)


class ScraperAPIIntegration:
    """
    ScraperAPI Integration - CRITICAL FIX
    Properly utilizes upgraded ScraperAPI for robust web scraping
    """
    
    def __init__(self):
        from config import Config
        self.scraperapi_key = Config.SCRAPERAPI_KEY
        self.scrapingbee_key = Config.SCRAPINGBEE_API_KEY
        
        # ScraperAPI configuration
        self.scraperapi_base = "http://api.scraperapi.com"
        self.scrapingbee_base = "https://app.scrapingbee.com/api/v1"
        
        logger.info(f"ScraperAPI Integration - ScraperAPI: {bool(self.scraperapi_key)}, ScrapingBee: {bool(self.scrapingbee_key)}")
    
    def scraperapi_request(self, url: str, **kwargs) -> requests.Response:
        """Make request through ScraperAPI - FIXED: This is the key method that was missing!"""
        if not self.scraperapi_key:
            raise Exception("ScraperAPI key not configured")
        
        # ScraperAPI parameters - ENHANCED configuration for difficult sites
        params = {
            'api_key': self.scraperapi_key,
            'url': url,
            'render': 'false',  # Set to true for JavaScript-heavy sites
            'country_code': 'us',
            'premium': 'false',  # Set to true for premium proxies if needed
            'session_number': random.randint(1, 100),  # Session stickiness
            'keep_headers': 'true',  # Keep original headers
            'autoparse': 'false'  # Don't auto-parse, we want raw HTML
        }
        
        # Add custom parameters if specified
        if 'render_js' in kwargs and kwargs['render_js']:
            params['render'] = 'true'
        
        if 'country' in kwargs:
            params['country_code'] = kwargs['country']
        
        if 'premium' in kwargs:
            params['premium'] = 'true' if kwargs['premium'] else 'false'
        
        # Custom headers through ScraperAPI
        headers = kwargs.get('headers', {})
        if headers:
            for key, value in headers.items():
                params[f'custom_headers[{key}]'] = value
        
        # Make the request with retry logic
        logger.info(f"Using ScraperAPI for: {url}")
        
        # Try with different timeout and retry strategy
        for attempt in range(2):
            try:
                timeout = 45 if attempt == 0 else 60  # Increase timeout on retry
                response = requests.get(self.scraperapi_base, params=params, timeout=timeout)
                break
            except requests.exceptions.Timeout:
                if attempt == 0:
                    logger.warning(f"ScraperAPI timeout on attempt {attempt + 1}, retrying with longer timeout...")
                    time.sleep(2)
                    continue
                else:
                    raise
        
        # ScraperAPI returns the scraped content directly in response.text
        # We need to create a mock response object that looks like a regular requests response
        mock_response = requests.Response()
        mock_response._content = response.content
        mock_response.status_code = response.status_code
        mock_response.headers.update(response.headers)
        mock_response.url = url  # Set the original URL
        mock_response.encoding = response.encoding
        
        return mock_response
    
    def scrapingbee_request(self, url: str, **kwargs) -> requests.Response:
        """Make request through ScrapingBee"""
        if not self.scrapingbee_key:
            raise Exception("ScrapingBee key not configured")
        
        params = {
            'api_key': self.scrapingbee_key,
            'url': url,
            'render_js': 'false',
            'premium_proxy': 'false',
            'country_code': 'us'
        }
        
        # Add JavaScript rendering if needed
        if kwargs.get('render_js'):
            params['render_js'] = 'true'
        
        # Add premium proxies if needed
        if kwargs.get('premium'):
            params['premium_proxy'] = 'true'
        
        # Custom headers
        headers = kwargs.get('headers', {})
        for key, value in headers.items():
            params[f'custom_headers[{key}]'] = value
        
        logger.info(f"Using ScrapingBee for: {url}")
        response = requests.get(self.scrapingbee_base, params=params, timeout=30)
        
        # Create mock response
        mock_response = requests.Response()
        mock_response._content = response.content
        mock_response.status_code = response.status_code
        mock_response.headers.update(response.headers)
        mock_response.url = url
        mock_response.encoding = response.encoding
        
        return mock_response


class UniversalScraper:
    """Universal web scraper with progressive escalation and ScraperAPI integration"""
    
    def __init__(self):
        self.timeout = 15
        self.max_retries = 2
        self.methods_tried = []
        
        # Initialize ScraperAPI integration - CRITICAL FIX!
        self.scraper_apis = ScraperAPIIntegration()
        
        # Initialize optional libraries
        self.user_agent = None
        if OPTIONAL_LIBRARIES.get('fake_useragent'):
            try:
                self.user_agent = UserAgent()
            except:
                pass
        
        self.cloudscraper_session = None
        if OPTIONAL_LIBRARIES.get('cloudscraper'):
            try:
                self.cloudscraper_session = cloudscraper.create_scraper()
            except:
                pass
        
        logger.info(f"UniversalScraper initialized with ScraperAPI: {bool(self.scraper_apis.scraperapi_key)}")
    
    def extract_from_url(self, url: str) -> Dict[str, Any]:
        """Extract article from URL using progressive escalation with ScraperAPI FIRST"""
        self.methods_tried = []
        domain = urlparse(url).netloc
        
        # Build escalation strategies - ScraperAPI FIRST!
        strategies = self._build_escalation_strategies([])
        
        last_error = None
        start_time = time.time()
        
        for strategy_name, strategy_func in strategies:
            try:
                self.methods_tried.append(strategy_name)
                logger.info(f"Trying extraction method: {strategy_name}")
                
                result = strategy_func(url)
                
                if result.get('success'):
                    if self._is_sufficient_content(result):
                        execution_time = time.time() - start_time
                        result['extraction_metadata']['execution_time'] = execution_time
                        result['extraction_metadata']['methods_tried'] = self.methods_tried
                        result['extraction_metadata']['successful_method'] = strategy_name
                        
                        logger.info(f"SUCCESS: {strategy_name} extracted {result.get('word_count', 0)} words in {execution_time:.2f}s")
                        return result
                    else:
                        logger.warning(f"{strategy_name} returned insufficient content")
                else:
                    last_error = result.get('error', f'{strategy_name} failed')
                    logger.warning(f"{strategy_name} failed: {last_error}")
                
                # Small delay between attempts
                time.sleep(random.uniform(0.5, 1.5))
                
            except Exception as e:
                last_error = str(e)
                logger.error(f"{strategy_name} threw exception: {e}")
                continue
        
        # All methods failed
        logger.error(f"All extraction strategies failed for {url}")
        return self._create_user_friendly_error(url, domain, last_error or 'All extraction methods failed')
    
    def _build_escalation_strategies(self, preferred_methods: List[str]) -> List[Tuple[str, callable]]:
        """Build extraction strategies - ScraperAPI FIRST for maximum success rate"""
        
        strategies = []
        
        # LEVEL 1: ScraperAPI (highest success rate) - CRITICAL FIX!
        if self.scraper_apis.scraperapi_key:
            strategies.append(('scraperapi_basic', self._scraperapi_basic_extract))
            strategies.append(('scraperapi_premium', self._scraperapi_premium_extract))
        
        if self.scraper_apis.scrapingbee_key:
            strategies.append(('scrapingbee_basic', self._scrapingbee_basic_extract))
        
        # LEVEL 2: Enhanced requests (for sites that don't block)
        strategies.append(('enhanced_headers', self._enhanced_headers_extract))
        strategies.append(('session_with_cookies', self._session_with_cookies_extract))
        
        # LEVEL 3: Anti-bot libraries
        if self.cloudscraper_session:
            strategies.append(('cloudscraper', self._cloudscraper_extract))
        
        if OPTIONAL_LIBRARIES.get('curl_cffi'):
            strategies.append(('curl_cffi_stealth', self._curl_cffi_stealth_extract))
        
        # LEVEL 4: Fallback methods
        strategies.append(('basic_requests', self._basic_requests_extract))
        
        return strategies
    
    # SCRAPERAPI EXTRACTION METHODS - CRITICAL FIX!
    
    def _scraperapi_basic_extract(self, url: str) -> Dict[str, Any]:
        """Extract using ScraperAPI basic - ENHANCED with better timeout handling"""
        try:
            response = self.scraper_apis.scraperapi_request(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            if not self._is_valid_content(soup):
                return {'success': False, 'error': 'Content appears to be blocked'}
            
            result = self._parse_content(response.text, url)
            result['extraction_metadata']['method'] = 'scraperapi_basic'
            result['extraction_metadata']['api_used'] = True
            logger.info("✅ SUCCESS: ScraperAPI basic extraction succeeded!")
            return result
            
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'ScraperAPI timeout - site may be slow to respond'}
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                return {'success': False, 'error': 'Site is blocking ScraperAPI requests (403 Forbidden)'}
            else:
                return {'success': False, 'error': f'ScraperAPI HTTP error: {e.response.status_code}'}
        except Exception as e:
            return {'success': False, 'error': f'ScraperAPI basic failed: {str(e)}'}
    
    def _scraperapi_premium_extract(self, url: str) -> Dict[str, Any]:
        """Extract using ScraperAPI with premium proxies and JavaScript rendering"""
        try:
            response = self.scraper_apis.scraperapi_request(
                url, 
                render_js=True, 
                premium=True,
                country='us',
                headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                }
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            if not self._is_valid_content(soup):
                return {'success': False, 'error': 'Content appears to be blocked despite premium ScraperAPI'}
            
            result = self._parse_content(response.text, url)
            result['extraction_metadata']['method'] = 'scraperapi_premium'
            result['extraction_metadata']['api_used'] = True
            result['extraction_metadata']['javascript_rendered'] = True
            logger.info("✅ SUCCESS: ScraperAPI premium extraction succeeded!")
            return result
            
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'ScraperAPI premium timeout - site may be very slow'}
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                return {'success': False, 'error': 'Site is blocking premium ScraperAPI requests (403 Forbidden)'}
            else:
                return {'success': False, 'error': f'ScraperAPI premium HTTP error: {e.response.status_code}'}
        except Exception as e:
            return {'success': False, 'error': f'ScraperAPI premium failed: {str(e)}'}
    
    def _scrapingbee_basic_extract(self, url: str) -> Dict[str, Any]:
        """Extract using ScrapingBee"""
        try:
            response = self.scraper_apis.scrapingbee_request(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            if not self._is_valid_content(soup):
                return {'success': False, 'error': 'Content appears to be blocked'}
            
            result = self._parse_content(response.text, url)
            result['extraction_metadata']['method'] = 'scrapingbee_basic'
            result['extraction_metadata']['api_used'] = True
            return result
            
        except Exception as e:
            return {'success': False, 'error': f'ScrapingBee failed: {str(e)}'}
    
    # REGULAR EXTRACTION METHODS (fallbacks)
    
    def _enhanced_headers_extract(self, url: str) -> Dict[str, Any]:
        """Enhanced headers extraction"""
        try:
            headers = self._get_enhanced_headers(url)
            response = requests.get(url, headers=headers, timeout=self.timeout, verify=False, allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            if not self._is_valid_content(soup):
                return {'success': False, 'error': 'Content appears to be blocked'}
            
            return self._parse_content(response.text, url)
            
        except Exception as e:
            return {'success': False, 'error': f'Enhanced headers failed: {str(e)}'}
    
    def _session_with_cookies_extract(self, url: str) -> Dict[str, Any]:
        """Session with cookies extraction"""
        try:
            session = requests.Session()
            session.headers.update(self._get_enhanced_headers(url))
            
            # Set some common cookies
            session.cookies.update({
                'accepted_cookies': 'true',
                'cookie_consent': 'accepted',
                'gdpr_consent': 'true'
            })
            
            response = session.get(url, timeout=self.timeout, verify=False, allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            if not self._is_valid_content(soup):
                return {'success': False, 'error': 'Content appears to be blocked'}
            
            return self._parse_content(response.text, url)
            
        except Exception as e:
            return {'success': False, 'error': f'Session with cookies failed: {str(e)}'}
    
    def _cloudscraper_extract(self, url: str) -> Dict[str, Any]:
        """CloudScraper for Cloudflare bypass"""
        try:
            if not self.cloudscraper_session:
                return {'success': False, 'error': 'Cloudscraper not available'}
            
            time.sleep(random.uniform(1, 3))
            response = self.cloudscraper_session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            if not self._is_valid_content(soup):
                return {'success': False, 'error': 'Content blocked despite Cloudscraper'}
            
            return self._parse_content(response.text, url)
            
        except Exception as e:
            return {'success': False, 'error': f'Cloudscraper failed: {str(e)}'}
    
    def _curl_cffi_stealth_extract(self, url: str) -> Dict[str, Any]:
        """curl_cffi with enhanced stealth"""
        try:
            headers = self._get_enhanced_headers(url, strategy="stealth")
            
            response = curl_requests.get(
                url,
                headers=headers,
                timeout=self.timeout,
                impersonate="chrome120",
                verify=False,
                allow_redirects=True
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            if not self._is_valid_content(soup):
                return {'success': False, 'error': 'Content blocked despite curl_cffi stealth'}
            
            return self._parse_content(response.text, url)
            
        except Exception as e:
            return {'success': False, 'error': f'curl_cffi stealth failed: {str(e)}'}
    
    def _basic_requests_extract(self, url: str) -> Dict[str, Any]:
        """Basic requests - last resort fallback"""
        try:
            headers = self._get_enhanced_headers(url)
            response = requests.get(url, headers=headers, timeout=self.timeout, verify=False, allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            if not self._is_valid_content(soup):
                return {'success': False, 'error': 'Content appears to be blocked or invalid'}
            
            return self._parse_content(response.text, url)
            
        except Exception as e:
            return {'success': False, 'error': f'Basic requests failed: {str(e)}'}
    
    def _get_enhanced_headers(self, url: str, strategy: str = "default") -> Dict[str, str]:
        """Get enhanced headers based on strategy"""
        base_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
        
        # User-Agent selection
        if self.user_agent and strategy == "stealth":
            try:
                base_headers['User-Agent'] = self.user_agent.random
            except:
                base_headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        else:
            base_headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        
        # Add referer for some strategies
        if strategy == "social":
            base_headers['Referer'] = 'https://www.facebook.com/'
        elif strategy == "search":
            base_headers['Referer'] = 'https://www.google.com/'
        
        return base_headers
    
    def _is_valid_content(self, soup: BeautifulSoup) -> bool:
        """Check if scraped content is valid - RELAXED for ScraperAPI responses"""
        if not soup:
            return False
        
        text = soup.get_text().lower()
        
        # For ScraperAPI responses, be more lenient
        # Only reject if completely empty or obvious error pages
        if len(text.strip()) < 50:
            return False
        
        # Check for severe blocking indicators only
        severe_blocking = [
            'access denied',
            'forbidden',
            'page not found',
            '404 not found',
            '503 service unavailable',
            'this site is blocked'
        ]
        
        # Only reject if we find severe blocking and very little content
        severe_block_found = any(indicator in text for indicator in severe_blocking)
        if severe_block_found and len(text.strip()) < 200:
            return False
        
        # Accept content if we have reasonable amount of text
        return len(text.strip()) >= 100
    
    def _is_sufficient_content(self, result: Dict[str, Any]) -> bool:
        """Check if extraction result has sufficient content"""
        if not result.get('success'):
            return False
        
        text = result.get('text', '')
        if not text or len(text.strip()) < 200:
            return False
        
        word_count = result.get('word_count', 0)
        if word_count < 50:
            return False
        
        return True
    
    def _parse_content(self, html: str, url: str) -> Dict[str, Any]:
        """Parse HTML content and extract article data - ENHANCED for ScraperAPI responses"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'nav', 'aside', 'footer', 'header', 'advertisement']):
                element.decompose()
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract main content - Try multiple strategies
            content = self._extract_main_content(soup)
            
            # If content is still minimal, try extracting from any available text
            if not content or len(content.strip()) < 200:
                # Fallback: get all meaningful text from the page
                all_paragraphs = soup.find_all(['p', 'div', 'article', 'section'])
                content_parts = []
                
                for elem in all_paragraphs:
                    text = elem.get_text(strip=True)
                    if text and len(text) > 30:  # Skip very short snippets
                        content_parts.append(text)
                
                if content_parts:
                    content = ' '.join(content_parts[:20])  # Take first 20 meaningful parts
            
            # Extract metadata - UNIVERSAL AUTHOR EXTRACTION
            author = self._extract_author(soup, url)
            publish_date = self._extract_publish_date(soup)
            description = self._extract_description(soup)
            
            # Calculate word count
            word_count = len(content.split()) if content else 0
            
            # Even if content is limited, return what we have
            return {
                'success': True,
                'title': title or 'Article',
                'text': content or 'Content extraction was limited by site protection',
                'author': author,
                'publish_date': publish_date,
                'url': url,
                'domain': urlparse(url).netloc,
                'description': description,
                'word_count': word_count,
                'extraction_metadata': {
                    'method': 'content_parsing',
                    'extracted_at': datetime.now().isoformat(),
                    'limited_extraction': word_count < 100
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Content parsing failed: {str(e)}'}
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title"""
        # Try multiple title extraction methods
        title_selectors = [
            'h1',
            'title',
            '[property="og:title"]',
            '[name="twitter:title"]',
            '.entry-title',
            '.post-title',
            '.article-title'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get('content') if element.name in ['meta'] else element.get_text(strip=True)
                if title and len(title) > 10:
                    return title[:200]  # Limit title length
        
        return 'Untitled Article'
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main article content"""
        # Try multiple content extraction strategies
        content_selectors = [
            'article',
            '[role="article"]',
            '.entry-content',
            '.post-content',
            '.article-body',
            '.content',
            'main',
            '.main-content'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                # Remove unwanted nested elements
                for unwanted in element.find_all(['aside', 'nav', 'advertisement', '.ad', '.sidebar']):
                    unwanted.decompose()
                
                text = element.get_text(separator=' ', strip=True)
                if text and len(text) > 200:
                    return text
        
        # Fallback: get all paragraph text
        paragraphs = soup.find_all('p')
        content = ' '.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        
        return content if content else soup.get_text(separator=' ', strip=True)
    
    def _extract_author(self, soup: BeautifulSoup, url: str) -> Optional[str]:
        """UNIVERSAL author extraction that works for all news sites"""
        
        # Step 1: Try structured data (JSON-LD, microdata, meta tags)
        author = self._extract_author_structured(soup)
        if author:
            logger.info(f"Author found via structured data: {author}")
            return author
        
        # Step 2: Try standard author selectors
        author = self._extract_author_selectors(soup)
        if author:
            logger.info(f"Author found via selectors: {author}")
            return author
        
        # Step 3: Try text pattern matching (universal approach)
        author = self._extract_author_text_patterns(soup)
        if author:
            logger.info(f"Author found via text patterns: {author}")
            return author
        
        # Step 4: Try positional extraction (near headline)
        author = self._extract_author_positional(soup)
        if author:
            logger.info(f"Author found via positional extraction: {author}")
            return author
        
        logger.info("No author found by any method")
        return None
    
    def _extract_author_structured(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author from structured data"""
        # JSON-LD structured data
        json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    data = data[0] if data else {}
                
                if isinstance(data, dict):
                    # Check for author field
                    if 'author' in data:
                        author_data = data['author']
                        if isinstance(author_data, dict) and 'name' in author_data:
                            return self._clean_author_name(author_data['name'])
                        elif isinstance(author_data, str):
                            return self._clean_author_name(author_data)
                        elif isinstance(author_data, list) and author_data:
                            first_author = author_data[0]
                            if isinstance(first_author, dict) and 'name' in first_author:
                                return self._clean_author_name(first_author['name'])
                            elif isinstance(first_author, str):
                                return self._clean_author_name(first_author)
            except:
                continue
        
        # Meta tags
        meta_selectors = [
            '[name="author"]',
            '[property="article:author"]',
            '[name="article:author"]',
            '[property="author"]'
        ]
        
        for selector in meta_selectors:
            element = soup.select_one(selector)
            if element:
                author = element.get('content', '').strip()
                if author:
                    return self._clean_author_name(author)
        
        return None
    
    def _extract_author_selectors(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author using CSS selectors"""
        author_selectors = [
            # Standard author classes
            '.author', '.byline', '.article-author', '.author-name', '.byline-author',
            '.post-author', '.entry-author', '.writer', '.journalist',
            
            # Microdata and semantic markup
            '[rel="author"]', '[itemprop="author"]', '[class*="author"]', '[class*="byline"]',
            
            # Common news site patterns
            '.author-bio', '.author-info', '.author-details', '.byline-name',
            '.article-byline', '.story-byline', '.news-byline',
            
            # Generic content selectors that might contain author
            '.meta-author', '.post-meta .author', '.article-meta .author'
        ]
        
        for selector in author_selectors:
            elements = soup.select(selector)
            for element in elements:
                # Skip if element is inside navigation, footer, or sidebar
                if element.find_parent(['nav', 'footer', 'aside', '.sidebar', '.navigation']):
                    continue
                
                # Get text content
                author_text = element.get_text(strip=True)
                if author_text and len(author_text) < 100:  # Authors shouldn't be very long
                    cleaned = self._clean_author_name(author_text)
                    if cleaned and self._is_valid_author_name(cleaned):
                        return cleaned
                
                # Check for links within author elements
                author_link = element.find('a')
                if author_link:
                    link_text = author_link.get_text(strip=True)
                    if link_text and len(link_text) < 100:
                        cleaned = self._clean_author_name(link_text)
                        if cleaned and self._is_valid_author_name(cleaned):
                            return cleaned
        
        return None
    
    def _extract_author_text_patterns(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author using text pattern matching - works for BBC and similar sites"""
        
        # Get the full text content
        full_text = soup.get_text()
        
        # Universal author patterns (works for most news sites)
        author_patterns = [
            # Standard byline patterns
            r'By\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)(?:\s|$|,|\.|:)',
            r'BY\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)(?:\s|$|,|\.|:)',
            r'by\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)(?:\s|$|,|\.|:)',
            
            # "Written by" patterns
            r'Written by\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)',
            r'Story by\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)',
            r'Report by\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)',
            
            # Author: patterns
            r'Author:\s*([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)',
            r'Reporter:\s*([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)',
            
            # BBC-style patterns (Author Name BBC News, Location)
            r'([A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+(?:\s+and\s+[A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+)?)\s+BBC News',
            r'([A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+(?:\s+and\s+[A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+)?)\s+CNN',
            r'([A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+(?:\s+and\s+[A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+)?)\s+Reuters',
            
            # Multiple authors patterns
            r'([A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+\s+and\s+[A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+)',
            r'([A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+,\s+[A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+)',
        ]
        
        for pattern in author_patterns:
            match = re.search(pattern, full_text)
            if match:
                author_name = match.group(1).strip()
                cleaned = self._clean_author_name(author_name)
                if cleaned and self._is_valid_author_name(cleaned):
                    return cleaned
        
        return None
    
    def _extract_author_positional(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author by looking near the headline - universal approach"""
        
        # Find the main headline
        headline_selectors = ['h1', '.headline', '.title', '.entry-title', '.post-title']
        headline = None
        
        for selector in headline_selectors:
            headline = soup.select_one(selector)
            if headline:
                break
        
        if not headline:
            return None
        
        # Look in elements immediately following the headline
        elements_to_check = []
        
        # Check next siblings
        current = headline
        for _ in range(5):  # Check next 5 siblings
            current = current.next_sibling
            if current and hasattr(current, 'get_text'):
                elements_to_check.append(current)
        
        # Check parent's next siblings (common pattern)
        if headline.parent:
            current = headline.parent
            for _ in range(3):
                current = current.next_sibling
                if current and hasattr(current, 'get_text'):
                    elements_to_check.append(current)
        
        # Look for author patterns in these elements
        for element in elements_to_check:
            text = element.get_text(strip=True)
            if text and len(text) < 200:  # Author info is usually short
                
                # Try pattern matching on this text
                author_patterns = [
                    r'^([A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+(?:\s+and\s+[A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+)?)(?:\s+BBC|\s+CNN|\s+Reuters|$|,)',
                    r'By\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)',
                    r'^([A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+)(?:\s|$|,)',
                ]
                
                for pattern in author_patterns:
                    match = re.search(pattern, text)
                    if match:
                        author_name = match.group(1).strip()
                        cleaned = self._clean_author_name(author_name)
                        if cleaned and self._is_valid_author_name(cleaned):
                            return cleaned
        
        return None
    
    def _clean_author_name(self, author: str) -> Optional[str]:
        """Clean and normalize author name"""
        if not author:
            return None
        
        # Remove common prefixes and suffixes
        author = re.sub(r'^(By|by|BY|Written by|Author:|Reporter:)\s+', '', author, flags=re.IGNORECASE)
        author = re.sub(r'\s*[\|\-]\s*(Reporter|Writer|Journalist|Correspondent).*$', '', author, flags=re.IGNORECASE)
        author = re.sub(r'\s*,\s*(BBC News|CNN|Reuters).*$', '', author, flags=re.IGNORECASE)
        
        # Clean up whitespace
        author = re.sub(r'\s+', ' ', author).strip()
        
        # Remove trailing punctuation
        author = re.sub(r'[,\.\:;]+$', '', author)
        
        return author if author else None
    
    def _is_valid_author_name(self, author: str) -> bool:
        """Validate that the extracted text looks like a real author name"""
        if not author or len(author) < 3 or len(author) > 100:
            return False
        
        # Must have at least 2 words (first and last name)
        words = author.split()
        if len(words) < 2:
            return False
        
        # Check for reasonable author name patterns
        # Should start with capital letter
        if not author[0].isupper():
            return False
        
        # Shouldn't contain numbers or special characters (except spaces, hyphens, apostrophes)
        if re.search(r'[0-9@#$%^&*()_+={}|\[\]\\:";\'<>?,./]', author):
            return False
        
        # Common false positives to reject
        false_positives = [
            'read more', 'click here', 'share this', 'comments', 'subscribe',
            'advertisement', 'sponsored', 'trending', 'popular', 'related',
            'breaking news', 'latest news', 'top stories', 'social media'
        ]
        
        author_lower = author.lower()
        if any(fp in author_lower for fp in false_positives):
            return False
        
        return True
    
    def _extract_publish_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract publish date"""
        date_selectors = [
            '[property="article:published_time"]',
            '[name="publish_date"]',
            '[name="date"]',
            'time[datetime]',
            '.publish-date',
            '.article-date'
        ]
        
        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                date = element.get('content') or element.get('datetime') or element.get_text(strip=True)
                if date:
                    return date[:50]  # Limit length
        
        return None
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article description/summary"""
        desc_selectors = [
            '[name="description"]',
            '[property="og:description"]',
            '[name="twitter:description"]'
        ]
        
        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element:
                desc = element.get('content', '').strip()
                if desc:
                    return desc[:500]  # Limit length
        
        return None
    
    def _create_user_friendly_error(self, url: str, domain: str, technical_error: str) -> Dict[str, Any]:
        """Create user-friendly error message"""
        return {
            'success': False,
            'error': f"Could not extract content from {domain}. The site may be blocking automated requests.",
            'url': url,
            'domain': domain,
            'extraction_metadata': {
                'all_methods_failed': True,
                'methods_tried': self.methods_tried,
                'technical_error': technical_error,
                'suggestion': 'Try copying the article text directly from your browser'
            }
        }


# Main ArticleExtractor class that inherits from BaseAnalyzer
class ArticleExtractor(BaseAnalyzer):
    """Article extraction service with ScraperAPI integration - FIXED VERSION"""
    
    def __init__(self):
        super().__init__('article_extractor')
        
        logger.info("=" * 60)
        logger.info("FIXED ArticleExtractor with UNIVERSAL Author Detection")
        logger.info("=" * 60)
        
        # Initialize universal scraper with ScraperAPI
        self._extractor = None
        
        try:
            self._extractor = UniversalScraper()
            scraperapi_available = bool(self._extractor.scraper_apis.scraperapi_key)
            logger.info(f"UniversalScraper initialized - ScraperAPI: {scraperapi_available}")
            
            if scraperapi_available:
                logger.info("🚀 ScraperAPI integration ACTIVE - upgraded key will be used!")
            else:
                logger.warning("⚠️  ScraperAPI key not found - will use fallback methods")
                
        except Exception as e:
            logger.error(f"Failed to initialize UniversalScraper: {e}")
            self._extractor = None
    
    def _check_availability(self) -> bool:
        """Check if service is available"""
        return True  # Always available with fallback methods
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Main analysis method - FIXED to use ScraperAPI"""
        logger.info("=" * 60)
        logger.info("FIXED ArticleExtractor.analyze() - WITH SCRAPERAPI")
        logger.info("=" * 60)
        
        try:
            # Handle input formats
            url = None
            text = None
            
            if 'url' in data:
                url = data['url']
            elif 'text' in data:
                text = data['text']
            elif 'content' in data and 'content_type' in data:
                if data['content_type'] == 'url':
                    url = data['content']
                else:
                    text = data['content']
            else:
                return self.get_error_result("Invalid input format")
            
            # Extract content
            if url:
                logger.info(f"Extracting from URL with ScraperAPI: {url}")
                
                result = None
                if self._extractor:
                    try:
                        result = self._extractor.extract_from_url(url)
                        
                        # Log ScraperAPI usage
                        if result.get('success') and result.get('extraction_metadata', {}).get('api_used'):
                            logger.info("✅ SUCCESS: ScraperAPI successfully extracted content!")
                        elif result.get('success'):
                            logger.info("✅ SUCCESS: Fallback method extracted content")
                        else:
                            logger.warning("❌ All extraction methods failed")
                            
                    except Exception as e:
                        logger.warning(f"Universal scraper failed: {e}")
                        result = None
                
                # If extraction failed, try basic fallback
                if not result or not result.get('success'):
                    logger.warning("Universal scraper failed, trying basic fallback")
                    result = self._basic_fallback_extract(url)
                
                return self.get_success_result(result) if result.get('success') else self.get_error_result(result.get('error', 'Extraction failed'))
            
            elif text:
                logger.info("Analyzing provided text content")
                
                # Simple text analysis
                lines = text.strip().split('\n')
                title = lines[0][:100] if lines else 'Text Analysis'
                word_count = len(text.split())
                
                result = {
                    'success': True,
                    'title': title,
                    'text': text,
                    'word_count': word_count,
                    'extraction_metadata': {'method': 'text_analysis'}
                }
                
                return self.get_success_result(result)
            
        except Exception as e:
            logger.error(f"ArticleExtractor.analyze failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _basic_fallback_extract(self, url: str) -> Dict[str, Any]:
        """Basic fallback extraction when all else fails"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(url, headers=headers, timeout=15, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'nav', 'aside', 'footer', 'header']):
                element.decompose()
            
            # Extract basic title
            title_elem = soup.find('title') or soup.find('h1')
            title = title_elem.get_text(strip=True) if title_elem else 'Untitled'
            
            # Extract content - try multiple strategies
            content = None
            
            # Strategy 1: Article tags
            article = soup.find('article')
            if article:
                content = article.get_text(separator=' ', strip=True)
            
            # Strategy 2: Content divs
            if not content:
                content_selectors = ['.content', '.entry-content', '.post-content', '.article-body', 'main']
                for selector in content_selectors:
                    elem = soup.select_one(selector)
                    if elem:
                        content = elem.get_text(separator=' ', strip=True)
                        break
            
            # Strategy 3: All paragraphs
            if not content:
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text(strip=True) for p in paragraphs])
            
            # Strategy 4: All text
            if not content:
                content = soup.get_text(separator=' ', strip=True)
            
            if not content or len(content) < 100:
                return {'success': False, 'error': 'Insufficient content extracted'}
            
            word_count = len(content.split())
            
            # UNIVERSAL AUTHOR EXTRACTION - Apply same logic as main extractor
            universal_scraper = UniversalScraper()
            author = universal_scraper._extract_author(soup, url)
            
            return {
                'success': True,
                'title': title,
                'text': content,
                'author': author,
                'publish_date': None,
                'url': url,
                'domain': urlparse(url).netloc,
                'description': None,
                'image': None,
                'keywords': [],
                'word_count': word_count,
                'extraction_metadata': {
                    'method': 'basic_fallback',
                    'api_used': False
                },
                'extracted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Basic extraction fallback failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': f'Basic extraction failed: {str(e)}'
            }
