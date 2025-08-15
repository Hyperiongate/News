# services/article_extractor.py
"""
Enhanced Article Extraction Service
Extracts article content from URLs or raw text with support for live news pages
"""

import json
import re
import time
import logging
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse, urljoin
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import random
import os

from services.base_analyzer import BaseAnalyzer

# Optional imports
try:
    from fake_useragent import UserAgent
    FAKE_UA_AVAILABLE = True
except ImportError:
    FAKE_UA_AVAILABLE = False

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
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
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
    """Simple circuit breaker for domain-specific failures"""
    
    def __init__(self, failure_threshold=3, timeout=300):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = {}
        self.last_failure_time = {}
        self.blocked_until = {}
        self.last_error = {}
    
    def record_failure(self, domain: str, error: str):
        """Record a failure for a domain"""
        current_time = time.time()
        
        if domain not in self.failures:
            self.failures[domain] = 0
            
        self.failures[domain] += 1
        self.last_failure_time[domain] = current_time
        self.last_error[domain] = error
        
        if self.failures[domain] >= self.failure_threshold:
            self.blocked_until[domain] = current_time + self.timeout
            logger.warning(f"Circuit breaker activated for {domain}, blocked until {self.blocked_until[domain]}")
    
    def record_success(self, domain: str):
        """Record a success for a domain"""
        if domain in self.failures:
            self.failures[domain] = 0
            if domain in self.blocked_until:
                del self.blocked_until[domain]
    
    def is_blocked(self, domain: str) -> bool:
        """Check if a domain is currently blocked"""
        if domain not in self.blocked_until:
            return False
            
        current_time = time.time()
        if current_time >= self.blocked_until[domain]:
            # Reset the block
            del self.blocked_until[domain]
            self.failures[domain] = 0
            return False
            
        return True
    
    def get_last_error(self, domain: str) -> str:
        """Get the last error for a domain"""
        return self.last_error.get(domain, "Unknown error")


class LegacyArticleExtractor:
    """Legacy article extraction implementation with enhanced live news support"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Initialize optional components
        self.ua = UserAgent() if FAKE_UA_AVAILABLE else None
        self.cloudscraper_session = cloudscraper.create_scraper() if CLOUDSCRAPER_AVAILABLE else None
        
        # Circuit breaker for problematic domains
        self.circuit_breaker = CircuitBreaker()
        
        # Thread pool for parallel extraction attempts
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # Configuration
        self.timeout = 15
        self.browser_timeout = 30
        self.min_content_length = 100
        self.min_paragraphs = 3
        self.min_words_per_paragraph = 10
        
        # Track which methods have been tried for better error messaging
        self.methods_tried = []
    
    def _get_headers(self, referer: Optional[str] = None, use_chrome: bool = False) -> Dict[str, str]:
        """Get randomized headers"""
        static_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        ]
        
        if self.ua and not use_chrome:
            try:
                user_agent = self.ua.random
            except:
                user_agent = random.choice(static_agents)
        else:
            user_agent = random.choice(static_agents)
        
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
        }
        
        if referer:
            headers['Referer'] = referer
            headers['Sec-Fetch-Site'] = 'same-origin'
        
        return headers
    
    def extract_from_url(self, url: str) -> Dict[str, Any]:
        """Main extraction method that tries multiple approaches"""
        start_time = time.time()
        logger.info(f"Starting extraction for URL: {url}")
        
        # Reset methods tried for this extraction
        self.methods_tried = []
        
        # Parse domain for circuit breaker
        domain = urlparse(url).netloc
        
        # Check circuit breaker
        if self.circuit_breaker.is_blocked(domain):
            last_error = self.circuit_breaker.get_last_error(domain)
            logger.warning(f"Domain {domain} is circuit-broken. Last error: {last_error}")
            return self._create_user_friendly_error(url, domain, f'Domain temporarily blocked due to repeated failures: {last_error}')
        
        # Build list of extraction methods to try
        methods = []
        
        # Quick methods first (fast, but may be blocked)
        methods.append(('enhanced_requests', self._enhanced_requests_extract))
        
        if CLOUDSCRAPER_AVAILABLE:
            methods.append(('cloudscraper', self._cloudscraper_extract))
        
        if CURL_CFFI_AVAILABLE:
            methods.append(('curl_cffi', self._curl_cffi_extract))
        
        # Cookie-based extraction
        methods.append(('cookies', self._cookies_extract))
        
        # Browser automation methods (slower but more reliable)
        if SELENIUM_AVAILABLE:
            methods.append(('selenium', self._selenium_extract))
        
        if PLAYWRIGHT_AVAILABLE:
            methods.append(('playwright', self._playwright_extract))
        
        # Proxy as last resort
        methods.append(('proxy', self._proxy_extract))
        
        last_error = None
        for method_name, method_func in methods:
            try:
                logger.info(f"Trying {method_name} for {url}")
                self.methods_tried.append(method_name)
                result = method_func(url)
                
                if result.get('success'):
                    # Record success
                    self.circuit_breaker.record_success(domain)
                    
                    # Add timing info
                    result['extraction_metadata'] = result.get('extraction_metadata', {})
                    result['extraction_metadata']['duration'] = time.time() - start_time
                    result['extraction_metadata']['method'] = method_name
                    result['extraction_metadata']['methods_tried'] = self.methods_tried
                    
                    logger.info(f"Successfully extracted {result.get('word_count', 0)} words using {method_name}")
                    return result
                else:
                    last_error = result.get('error', 'Unknown error')
                    logger.warning(f"{method_name} failed: {last_error}")
                    
            except Exception as e:
                last_error = str(e)
                logger.warning(f"{method_name} exception: {last_error}")
        
        # All methods failed
        self.circuit_breaker.record_failure(domain, last_error)
        
        # Try emergency fallback
        logger.info("All extraction methods failed, trying emergency fallback")
        emergency_result = self._emergency_fallback_extraction(url)
        if emergency_result.get('success'):
            emergency_result['extraction_metadata']['methods_tried'] = self.methods_tried + ['emergency_fallback']
            return emergency_result
        
        # Complete failure - return user-friendly error
        return self._create_user_friendly_error(url, domain, last_error)
    
    def _create_user_friendly_error(self, url: str, domain: str, last_error: str) -> Dict[str, Any]:
        """Create a user-friendly error message when all extraction methods fail"""
        methods_summary = f"Tried {len(self.methods_tried)} extraction methods"
        
        user_message = (
            f"Unable to extract article from {domain}.\n\n"
            f"This website may be blocking automated access. "
            f"You can try using the 'Text' option instead:\n"
            f"1. Copy the article text from your browser\n"
            f"2. Select 'Text' instead of 'URL'\n"
            f"3. Paste the article content\n\n"
            f"Technical details: {methods_summary}"
        )
        
        return {
            'success': False,
            'error': user_message,
            'url': url,
            'domain': domain,
            'extraction_metadata': {
                'all_methods_failed': True,
                'methods_tried': self.methods_tried,
                'last_technical_error': last_error,
                'suggestion': 'use_text_option'
            }
        }
    
    def _enhanced_requests_extract(self, url: str) -> Dict[str, Any]:
        """Enhanced extraction using requests with better headers"""
        try:
            headers = self._get_headers(use_chrome=True)
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            return self._parse_content(response.text, url)
            
        except Exception as e:
            logger.error(f"Enhanced requests extract failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _cloudscraper_extract(self, url: str) -> Dict[str, Any]:
        """Extract using cloudscraper for cloudflare protection"""
        try:
            response = self.cloudscraper_session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            return self._parse_content(response.text, url)
            
        except Exception as e:
            logger.error(f"Cloudscraper extract failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _curl_cffi_extract(self, url: str) -> Dict[str, Any]:
        """Extract using curl_cffi which mimics real browser TLS fingerprints"""
        try:
            headers = self._get_headers()
            response = curl_requests.get(
                url, 
                headers=headers, 
                timeout=self.timeout,
                impersonate="chrome110"  # Impersonate Chrome browser
            )
            response.raise_for_status()
            
            return self._parse_content(response.text, url)
            
        except Exception as e:
            logger.error(f"Curl-cffi extract failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _cookies_extract(self, url: str) -> Dict[str, Any]:
        """Extract using requests with common cookie configurations"""
        try:
            # Create new session with cookies
            session = requests.Session()
            
            # Add common cookies that might help bypass restrictions
            cookies = {
                'consent': 'yes',
                'gdpr': '1',
                'cookies_accepted': '1',
                'adult_confirmed': '1',
            }
            
            headers = self._get_headers(use_chrome=True)
            
            # First visit to get initial cookies
            session.get(url, headers=headers, timeout=5)
            
            # Add our cookies
            for key, value in cookies.items():
                session.cookies.set(key, value, domain=urlparse(url).netloc)
            
            # Try again with cookies
            response = session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            return self._parse_content(response.text, url)
            
        except Exception as e:
            logger.error(f"Cookies extract failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _selenium_extract(self, url: str) -> Dict[str, Any]:
        """Selenium-based extraction for JavaScript-heavy sites"""
        if not SELENIUM_AVAILABLE:
            return {'success': False, 'error': 'Selenium not available'}
        
        driver = None
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument(f'user-agent={self._get_headers()["User-Agent"]}')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            driver = webdriver.Chrome(options=options)
            
            # Execute script to mask automation
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            driver.set_page_load_timeout(self.browser_timeout)
            driver.get(url)
            
            # Wait for content to load
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "article"))
                )
            except:
                # Try alternative wait
                time.sleep(3)
            
            # Scroll to trigger lazy loading
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            # Get page source
            html = driver.page_source
            
            return self._parse_content(html, url)
            
        except Exception as e:
            logger.error(f"Selenium extract failed: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def _playwright_extract(self, url: str) -> Dict[str, Any]:
        """Playwright-based extraction - modern alternative to Selenium"""
        if not PLAYWRIGHT_AVAILABLE:
            return {'success': False, 'error': 'Playwright not available'}
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=['--disable-blink-features=AutomationControlled']
                )
                
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent=self._get_headers()["User-Agent"]
                )
                
                # Add script to mask automation
                context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                page = context.new_page()
                page.goto(url, timeout=self.browser_timeout * 1000)
                
                # Wait for content
                try:
                    page.wait_for_selector('article', timeout=10000)
                except:
                    page.wait_for_timeout(3000)
                
                # Scroll to load lazy content
                page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
                page.wait_for_timeout(1000)
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1000)
                
                html = page.content()
                browser.close()
                
                return self._parse_content(html, url)
                
        except Exception as e:
            logger.error(f"Playwright extract failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _proxy_extract(self, url: str) -> Dict[str, Any]:
        """Extract using proxy rotation as last resort"""
        try:
            # Try to use free proxy services (note: these are unreliable)
            proxy_options = [
                None,  # First try without proxy
                {'http': 'http://proxy.server:3128', 'https': 'http://proxy.server:3128'},
            ]
            
            # Check if we have proxy environment variables
            if os.environ.get('HTTP_PROXY'):
                proxy_options.append({
                    'http': os.environ.get('HTTP_PROXY'),
                    'https': os.environ.get('HTTPS_PROXY', os.environ.get('HTTP_PROXY'))
                })
            
            headers = self._get_headers()
            
            for proxies in proxy_options:
                try:
                    response = requests.get(
                        url,
                        headers=headers,
                        proxies=proxies,
                        timeout=self.timeout,
                        verify=False  # Disable SSL verification for proxy
                    )
                    response.raise_for_status()
                    
                    result = self._parse_content(response.text, url)
                    if result.get('success'):
                        return result
                        
                except:
                    continue
            
            return {'success': False, 'error': 'All proxy attempts failed'}
            
        except Exception as e:
            logger.error(f"Proxy extract failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _emergency_fallback_extraction(self, url: str) -> Dict[str, Any]:
        """Emergency fallback using minimal extraction"""
        try:
            headers = self._get_headers()
            response = self.session.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic metadata
            title = None
            for selector in ['meta[property="og:title"]', 'meta[name="twitter:title"]', 'title']:
                elem = soup.select_one(selector)
                if elem:
                    title = elem.get('content', elem.get_text(strip=True))
                    if title:
                        break
            
            description = None
            for selector in ['meta[property="og:description"]', 'meta[name="description"]']:
                elem = soup.select_one(selector)
                if elem and elem.get('content'):
                    description = elem['content']
                    break
            
            author = None
            for selector in ['meta[name="author"]', 'meta[property="article:author"]']:
                elem = soup.select_one(selector)
                if elem and elem.get('content'):
                    author = elem['content']
                    break
            
            # Create minimal content
            content = description or "Content extraction failed - using metadata only"
            if title and title not in content:
                content = f"{title}\n\n{content}"
            
            return {
                'success': True,
                'title': title or 'Unknown Title',
                'text': content,
                'author': author,
                'url': url,
                'domain': urlparse(url).netloc,
                'word_count': len(content.split()),
                'extraction_metadata': {
                    'method': 'emergency_fallback',
                    'used_metadata_only': True
                }
            }
            
        except Exception as e:
            logger.error(f"Emergency fallback failed: {e}")
            return {'success': False, 'error': f'Emergency fallback failed: {str(e)}'}
    
    def _parse_content(self, html: str, url: str = None) -> Dict[str, Any]:
        """Parse HTML and extract article data"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Check if this is a live news page
            is_live_page = url and any(indicator in url.lower() for indicator in ['/live-news/', '/live/', '/updates/'])
            
            # Extract content using appropriate method
            content, extraction_metadata = self.extract_article_content(soup, url)
            
            if not content:
                # If it's a live page, try to get any summary/description as fallback
                if is_live_page:
                    live_metadata = self._extract_metadata_from_live_page(soup, url)
                    if live_metadata.get('summary'):
                        content = live_metadata['summary']
                        extraction_metadata['used_summary_fallback'] = True
                    else:
                        return {
                            'success': False,
                            'error': 'Could not extract content from live news page'
                        }
                else:
                    return {
                        'success': False,
                        'error': 'Could not extract article content'
                    }
            
            # Extract other metadata
            title = self._extract_title(soup) or 'Untitled'
            author = self._extract_author(soup)
            publish_date = self._extract_date(soup)
            description = self._extract_description(soup)
            image = self._extract_image(soup, url) if url else None
            keywords = self._extract_keywords(soup)
            
            # Clean content
            content = self._clean_content(content)
            word_count = len(content.split())
            
            # For live pages, prepend update info
            if is_live_page and extraction_metadata.get('page_type') == 'live_news':
                update_count = extraction_metadata.get('update_count', 0)
                if update_count > 0:
                    content = f"[LIVE NEWS FEED - {update_count} updates extracted]\n\n{content}"
            
            return {
                'success': True,
                'title': title,
                'text': content,
                'author': author,
                'publish_date': publish_date,
                'url': url,
                'domain': urlparse(url).netloc if url else None,
                'description': description,
                'image': image,
                'keywords': keywords,
                'word_count': word_count,
                'extraction_metadata': extraction_metadata,
                'extracted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Content parsing failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': f'Content parsing error: {str(e)}'
            }
    
    def extract_article_content(self, soup: BeautifulSoup, url: str = None) -> Tuple[Optional[str], Dict[str, Any]]:
        """Extract article content from BeautifulSoup object"""
        metadata = {
            'extraction_method': 'unknown',
            'content_indicators': [],
            'issues': []
        }
        
        # Try multiple extraction strategies, including live news
        strategies = [
            ('live_news', lambda s: self._extract_live_news_content(s, url)),
            ('article_tag', self._extract_by_article_tag),
            ('main_content', self._extract_by_main_content),
            ('paragraph_clustering', self._extract_by_paragraph_clustering)
        ]
        
        for strategy_name, strategy_func in strategies:
            try:
                if strategy_name == 'live_news':
                    content, meta = strategy_func(soup)
                    if content:
                        metadata.update(meta)
                        logger.info(f"Content extracted successfully using {strategy_name}")
                        return content, metadata
                else:
                    content = strategy_func(soup)
                    if content and self._validate_content(content):
                        metadata['extraction_method'] = strategy_name
                        logger.info(f"Content extracted successfully using {strategy_name}")
                        return content, metadata
            except Exception as e:
                logger.debug(f"Strategy {strategy_name} failed: {e}")
                metadata['issues'].append(f"{strategy_name}: {str(e)}")
        
        logger.warning("All content extraction strategies failed")
        return None, metadata
    
    def _extract_live_news_content(self, soup: BeautifulSoup, url: str) -> Tuple[Optional[str], Dict[str, Any]]:
        """Extract content from live news pages (CNN, BBC, etc.)"""
        metadata = {
            'extraction_method': 'live_news',
            'content_indicators': [],
            'issues': []
        }
        
        # Check if this is a live news page
        is_live_page = any(indicator in url.lower() for indicator in ['/live-news/', '/live/', '/updates/'])
        
        if not is_live_page:
            # Also check page content for live indicators
            live_indicators = soup.find_all(class_=re.compile(r'live|update|ticker', re.I))
            is_live_page = len(live_indicators) > 3
        
        if not is_live_page:
            return None, metadata
        
        logger.info(f"Detected live news page: {url}")
        metadata['page_type'] = 'live_news'
        
        # Strategy 1: Look for live update containers
        content_parts = []
        
        # Common live update selectors
        live_selectors = [
            {'class': re.compile(r'live-update|update-item|post-update', re.I)},
            {'class': re.compile(r'post__content|update__content', re.I)},
            {'class': re.compile(r'article-wrap|story-body', re.I)},
            {'role': 'article'},
            {'data-type': 'article'},
        ]
        
        for selector in live_selectors:
            updates = soup.find_all('div', selector)
            if updates:
                logger.info(f"Found {len(updates)} updates using selector {selector}")
                for update in updates[:10]:  # Limit to first 10 updates
                    # Extract timestamp if available
                    time_elem = update.find(['time', 'span'], class_=re.compile(r'time|date|timestamp', re.I))
                    timestamp = time_elem.get_text(strip=True) if time_elem else ''
                    
                    # Extract update content
                    paragraphs = update.find_all('p')
                    if paragraphs:
                        update_text = '\n'.join(p.get_text(strip=True) for p in paragraphs)
                        if timestamp:
                            content_parts.append(f"[{timestamp}] {update_text}")
                        else:
                            content_parts.append(update_text)
                
                if content_parts:
                    break
        
        # Strategy 2: Extract from article body if no updates found
        if not content_parts:
            article_body = soup.find('div', class_=re.compile(r'article|story|content', re.I))
            if article_body:
                paragraphs = article_body.find_all('p')
                content_parts = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50]
        
        # Strategy 3: Fall back to all paragraphs
        if not content_parts:
            all_paragraphs = soup.find_all('p')
            content_parts = [p.get_text(strip=True) for p in all_paragraphs[:20] if len(p.get_text(strip=True)) > 50]
        
        if content_parts:
            content = '\n\n'.join(content_parts)
            metadata['update_count'] = len(content_parts)
            return content, metadata
        
        return None, metadata
    
    def _extract_metadata_from_live_page(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract metadata specific to live news pages"""
        metadata = {}
        
        # Try to get a summary or description
        summary_selectors = [
            {'class': re.compile(r'summary|description|intro', re.I)},
            {'property': 'og:description'},
            {'name': 'description'}
        ]
        
        for selector in summary_selectors:
            if 'property' in selector or 'name' in selector:
                elem = soup.find('meta', selector)
                if elem and elem.get('content'):
                    metadata['summary'] = elem['content']
                    break
            else:
                elem = soup.find(['div', 'p'], selector)
                if elem:
                    metadata['summary'] = elem.get_text(strip=True)
                    break
        
        # Get headline from title or h1
        headline = soup.find('h1')
        if headline:
            metadata['headline'] = headline.get_text(strip=True)
        
        # Get update count
        updates = soup.find_all(['div', 'article'], class_=re.compile(r'update|post', re.I))
        metadata['total_updates'] = len(updates)
        
        # Get last update time
        time_elements = soup.find_all('time')
        if time_elements:
            metadata['last_updated'] = time_elements[0].get('datetime', time_elements[0].get_text(strip=True))
        
        return metadata
    
    def _extract_by_article_tag(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract content from article tags"""
        article = soup.find('article')
        if article:
            # Remove non-content elements
            for element in article.find_all(['script', 'style', 'aside', 'nav']):
                element.decompose()
            
            paragraphs = article.find_all('p')
            if len(paragraphs) >= self.min_paragraphs:
                return '\n\n'.join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True).split()) >= self.min_words_per_paragraph)
        
        return None
    
    def _extract_by_main_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract content from main content areas"""
        # Common content selectors
        content_selectors = [
            {'class': re.compile(r'article-body|story-body|content-body', re.I)},
            {'id': re.compile(r'article|story|content', re.I)},
            {'role': 'main'},
            'main'
        ]
        
        for selector in content_selectors:
            if isinstance(selector, str):
                content_elem = soup.find(selector)
            else:
                content_elem = soup.find('div', selector)
            
            if content_elem:
                paragraphs = content_elem.find_all('p')
                if len(paragraphs) >= self.min_paragraphs:
                    content = '\n\n'.join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True).split()) >= self.min_words_per_paragraph)
                    if content:
                        return content
        
        return None
    
    def _extract_by_paragraph_clustering(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract content by finding clusters of paragraphs"""
        all_paragraphs = soup.find_all('p')
        
        # Filter paragraphs by minimum length
        valid_paragraphs = []
        for p in all_paragraphs:
            text = p.get_text(strip=True)
            if len(text.split()) >= self.min_words_per_paragraph:
                valid_paragraphs.append(text)
        
        # Need at least min_paragraphs
        if len(valid_paragraphs) >= self.min_paragraphs:
            return '\n\n'.join(valid_paragraphs)
        
        return None
    
    def _validate_content(self, content: str) -> bool:
        """Validate extracted content"""
        if not content:
            return False
        
        word_count = len(content.split())
        if word_count < self.min_content_length:
            return False
        
        # Check for common extraction failures
        if content.lower().startswith(('subscribe', 'please enable javascript', 'you need to enable')):
            return False
        
        return True
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article title"""
        strategies = [
            lambda: soup.find('meta', property='og:title')['content'],
            lambda: soup.find('meta', {'name': 'twitter:title'})['content'],
            lambda: soup.find('h1').get_text(strip=True),
            lambda: soup.find('title').get_text(strip=True).split('|')[0].strip(),
        ]
        
        for strategy in strategies:
            try:
                title = strategy()
                if title:
                    return title
            except:
                continue
        
        return None
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Universal author extraction with extensive fallbacks"""
        logger.info("Starting author extraction...")
        
        # Track what we've tried for debugging
        attempts = []
        
        # 1. JSON-LD structured data (most reliable)
        try:
            scripts = soup.find_all('script', {'type': 'application/ld+json'})
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    author = self._extract_author_from_json_ld(data)
                    if author:
                        logger.info(f"Found author in JSON-LD: {author}")
                        return author
                except:
                    continue
            attempts.append("JSON-LD")
        except:
            pass
        
        # 2. Meta tags (comprehensive list)
        meta_selectors = [
            {'name': 'author'},
            {'property': 'author'},
            {'property': 'article:author'},
            {'property': 'og:article:author'},
            {'name': 'byl'},
            {'name': 'DC.creator'},
            {'name': 'DC.Creator'},
            {'name': 'citation_author'},
            {'name': 'twitter:creator'},
            {'property': 'twitter:creator'},
            {'name': 'sailthru.author'},
            {'name': 'parsely-author'},
            {'itemprop': 'author'},
            {'name': 'article.author'},
            {'name': 'author_name'},
            {'property': 'dcsext.author'},
            {'name': 'cXenseParse:author'},
        ]
        
        for selector in meta_selectors:
            try:
                meta = soup.find('meta', selector)
                if meta and meta.get('content'):
                    author = self._clean_author_name(meta['content'])
                    if author and self._validate_author_name(author):
                        logger.info(f"Found author in meta tag {selector}: {author}")
                        return author
            except:
                continue
        attempts.append("Meta tags")
        
        # 3. Common byline selectors (expanded list)
        byline_selectors = [
            # Specific class names
            {'class': 'byline-name'},
            {'class': 'byline__name'},
            {'class': 'byline-author'},
            {'class': 'by-author'},
            {'class': 'author-name'},
            {'class': 'author__name'},
            {'class': 'article-author'},
            {'class': 'article__author'},
            {'class': 'story-byline'},
            {'class': 'content-author'},
            {'class': 'post-author'},
            {'class': 'entry-author'},
            {'class': 'writer'},
            {'class': 'journalist'},
            {'class': 'reporter'},
            {'class': 'contributor'},
            {'class': 'by'},
            {'class': 'byline'},
            {'class': 'author'},
            # ID selectors
            {'id': 'author'},
            {'id': 'byline'},
            {'id': 'article-author'},
            # Regex patterns for classes
            {'class': re.compile(r'byline', re.I)},
            {'class': re.compile(r'author(?!.*share)(?!.*follow)', re.I)},
            {'class': re.compile(r'writer', re.I)},
            {'class': re.compile(r'by-line', re.I)},
            {'class': re.compile(r'artikel__author', re.I)},  # International
            # Data attributes
            {'data-author': True},
            {'data-byline': True},
            # Microdata
            {'itemprop': 'author'},
            {'itemprop': 'creator'},
            {'rel': 'author'},
        ]
        
        # Try each selector with multiple tag types
        for selector in byline_selectors:
            for tag in ['span', 'div', 'p', 'a', 'address', 'cite', 'h3', 'h4', 'h5', 'strong']:
                try:
                    # Handle data attributes specially
                    if any(key.startswith('data-') for key in selector.keys()):
                        elements = soup.find_all(tag)
                        for elem in elements:
                            for attr, value in selector.items():
                                if elem.get(attr):
                                    author = self._extract_text_from_element(elem)
                                    if author and self._validate_author_name(author):
                                        logger.info(f"Found author in {tag} with {attr}: {author}")
                                        return author
                    else:
                        elem = soup.find(tag, selector)
                        if elem:
                            author = self._extract_text_from_element(elem)
                            if author and self._validate_author_name(author):
                                logger.info(f"Found author in {tag} with selector {selector}: {author}")
                                return author
                except:
                    continue
        attempts.append("Byline selectors")
        
        # 4. Look for author in specific page sections
        section_selectors = [
            {'class': re.compile(r'article[_-]?header', re.I)},
            {'class': re.compile(r'article[_-]?meta', re.I)},
            {'class': re.compile(r'post[_-]?meta', re.I)},
            {'class': re.compile(r'entry[_-]?meta', re.I)},
            {'class': re.compile(r'article[_-]?info', re.I)},
            {'class': re.compile(r'story[_-]?meta', re.I)},
            {'id': re.compile(r'article[_-]?header', re.I)},
            {'role': 'article'},
            'header',
            'article',
        ]
        
        for selector in section_selectors:
            try:
                if isinstance(selector, str):
                    section = soup.find(selector)
                else:
                    section = soup.find(['div', 'header', 'section'], selector)
                
                if section:
                    # Look for author within this section
                    author_elem = section.find(['span', 'div', 'p', 'a'], 
                                             class_=re.compile(r'author|byline|writer', re.I))
                    if author_elem:
                        author = self._extract_text_from_element(author_elem)
                        if author and self._validate_author_name(author):
                            logger.info(f"Found author in section {selector}: {author}")
                            return author
                    
                    # Look for "By Name" pattern in section text
                    section_text = section.get_text()
                    by_match = re.search(r'\bBy\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,3})', section_text)
                    if by_match:
                        author = by_match.group(1).strip()
                        if self._validate_author_name(author):
                            logger.info(f"Found author in section text: {author}")
                            return author
            except:
                continue
        attempts.append("Section search")
        
        # 5. Link with rel="author"
        try:
            author_link = soup.find('a', {'rel': 'author'})
            if author_link:
                author = self._clean_author_name(author_link.get_text(strip=True))
                if author and self._validate_author_name(author):
                    logger.info(f"Found author in rel=author link: {author}")
                    return author
        except:
            pass
        attempts.append("Author link")
        
        # 6. Schema.org microdata
        try:
            person_elem = soup.find(attrs={'itemtype': re.compile(r'schema\.org/Person', re.I)})
            if person_elem:
                name_elem = person_elem.find(attrs={'itemprop': 'name'})
                if name_elem:
                    author = self._clean_author_name(name_elem.get_text(strip=True))
                    if author and self._validate_author_name(author):
                        logger.info(f"Found author in schema.org: {author}")
                        return author
        except:
            pass
        attempts.append("Schema.org")
        
        # 7. "By Name" text pattern search (last resort)
        try:
            # Look for text nodes containing "By "
            by_pattern = re.compile(r'\b(?:By|by|BY)\s+([A-Z][a-zA-Z]+(?:\s+(?:and|&)\s+[A-Z][a-zA-Z]+)?(?:\s+[A-Z][a-zA-Z]+){0,3})')
            
            # Search in all text
            for text in soup.find_all(text=True):
                if text.parent.name not in ['script', 'style', 'meta']:
                    match = by_pattern.search(text)
                    if match:
                        author = match.group(1).strip()
                        # Extra validation for pattern matches
                        if (self._validate_author_name(author) and 
                            len(author.split()) <= 5 and
                            not any(word.lower() in ['the', 'staff', 'team', 'editor'] for word in author.split())):
                            logger.info(f"Found author in text pattern: {author}")
                            return author
        except:
            pass
        attempts.append("Text pattern")
        
        # 8. Check WordPress-style author URLs
        try:
            author_url = soup.find('a', href=re.compile(r'/author/|/profile/|/people/', re.I))
            if author_url and author_url.get_text(strip=True):
                author = self._clean_author_name(author_url.get_text(strip=True))
                if author and self._validate_author_name(author):
                    logger.info(f"Found author in author URL: {author}")
                    return author
        except:
            pass
        attempts.append("Author URL")
        
        logger.info(f"No author found. Attempted: {', '.join(attempts)}")
        return None
    
    def _extract_author_from_json_ld(self, data: Any) -> Optional[str]:
        """Extract author from JSON-LD data structure"""
        if isinstance(data, dict):
            # Direct author field
            if 'author' in data:
                author_data = data['author']
                if isinstance(author_data, str):
                    return self._clean_author_name(author_data)
                elif isinstance(author_data, dict):
                    # Try different name fields
                    for name_field in ['name', 'Name', 'fullName', 'displayName']:
                        if name_field in author_data:
                            return self._clean_author_name(author_data[name_field])
                elif isinstance(author_data, list) and author_data:
                    # Multiple authors - take first
                    first_author = author_data[0]
                    if isinstance(first_author, str):
                        return self._clean_author_name(first_author)
                    elif isinstance(first_author, dict):
                        for name_field in ['name', 'Name', 'fullName', 'displayName']:
                            if name_field in first_author:
                                return self._clean_author_name(first_author[name_field])
            
            # Check nested structures
            if '@graph' in data and isinstance(data['@graph'], list):
                for item in data['@graph']:
                    author = self._extract_author_from_json_ld(item)
                    if author:
                        return author
            
            # Check if this is a Person object
            if data.get('@type') == 'Person' and 'name' in data:
                return self._clean_author_name(data['name'])
                
        elif isinstance(data, list):
            # Check each item in the list
            for item in data:
                author = self._extract_author_from_json_ld(item)
                if author:
                    return author
        
        return None
    
    def _extract_text_from_element(self, elem) -> Optional[str]:
        """Extract and clean text from an element"""
        if not elem:
            return None
        
        # First try to get text without children
        text = elem.get_text(strip=True)
        
        # If the element has nested structure, try to get just the name
        name_elem = elem.find(['span', 'a'], class_=re.compile(r'name|author-name', re.I))
        if name_elem:
            text = name_elem.get_text(strip=True)
        
        return self._clean_author_name(text)
    
    def _clean_author_name(self, author: str) -> Optional[str]:
        """Clean and normalize author name"""
        if not author:
            return None
        
        # Remove common prefixes
        author = re.sub(r'^(By|by|BY|Written by|Reported by|Author:|Posted by|Published by)\s+', '', author, flags=re.I)
        
        # Remove common suffixes
        author = re.sub(r'\s*[\|\-,]\s*(Reporter|Writer|Journalist|Correspondent|Editor|Staff|Contributor).*$', '', author, flags=re.I)
        author = re.sub(r'\s*[\|\-,]\s*\w+\s*(News|Times|Post|Journal|Magazine).*$', '', author, flags=re.I)
        
        # Remove email addresses
        author = re.sub(r'\s*[\(\[]?[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}[\)\]]?', '', author)
        
        # Remove social media handles
        author = re.sub(r'\s*@[\w]+', '', author)
        
        # Remove extra whitespace
        author = re.sub(r'\s+', ' ', author).strip()
        
        # Remove parenthetical additions
        author = re.sub(r'\s*\([^)]*\)', '', author)
        
        return author if author else None
    
    def _validate_author_name(self, author: str) -> bool:
        """Validate that the extracted text is likely an author name"""
        if not author:
            return False
        
        # Check length
        if len(author) < 3 or len(author) > 100:
            return False
        
        # Check word count (most names are 2-5 words)
        word_count = len(author.split())
        if word_count < 1 or word_count > 6:
            return False
        
        # Skip common non-author values
        skip_values = [
            'staff', 'editor', 'admin', 'administrator', 'newsroom', 'team',
            'correspondent', 'reporter', 'writer', 'journalist', 'contributor',
            'guest', 'anonymous', 'unknown', 'author', 'by', 'posted',
            'associated press', 'reuters', 'ap', 'afp', 'bloomberg',
            'follow', 'share', 'subscribe', 'comment', 'more stories',
            'related articles', 'read more', 'click here', 'advertisement'
        ]
        
        author_lower = author.lower()
        if any(skip in author_lower for skip in skip_values):
            return False
        
        # Check if it contains at least one uppercase letter (names usually do)
        if not any(c.isupper() for c in author):
            return False
        
        # Check for reasonable character set (letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[A-Za-z\s\-'.]+$", author):
            return False
        
        # Looks like a valid name
        return True
    
    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract publish date"""
        strategies = [
            lambda: soup.find('meta', property='article:published_time')['content'],
            lambda: soup.find('meta', {'name': 'publish_date'})['content'],
            lambda: soup.find('time')['datetime'],
            lambda: soup.find('time').get_text(strip=True),
        ]
        
        for strategy in strategies:
            try:
                date = strategy()
                if date:
                    return date
            except:
                continue
        
        return None
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article description"""
        strategies = [
            lambda: soup.find('meta', property='og:description')['content'],
            lambda: soup.find('meta', {'name': 'description'})['content'],
            lambda: soup.find('meta', {'name': 'twitter:description'})['content'],
        ]
        
        for strategy in strategies:
            try:
                desc = strategy()
                if desc:
                    return desc
            except:
                continue
        
        return None
    
    def _extract_image(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Extract main article image"""
        strategies = [
            lambda: soup.find('meta', property='og:image')['content'],
            lambda: soup.find('meta', {'name': 'twitter:image'})['content'],
        ]
        
        for strategy in strategies:
            try:
                image_url = strategy()
                if image_url:
                    # Make URL absolute
                    return urljoin(base_url, image_url)
            except:
                continue
        
        return None
    
    def _extract_keywords(self, soup: BeautifulSoup) -> List[str]:
        """Extract article keywords"""
        try:
            keywords_tag = soup.find('meta', {'name': 'keywords'})
            if keywords_tag and keywords_tag.get('content'):
                return [k.strip() for k in keywords_tag['content'].split(',')]
        except:
            pass
        
        return []
    
    def _clean_content(self, content: str) -> str:
        """Clean extracted content"""
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        # Remove common artifacts
        content = re.sub(r'Share this article.*?$', '', content, flags=re.I)
        content = re.sub(r'Read more:.*?$', '', content, flags=re.I)
        
        return content.strip()
    
    def extract_from_text(self, text: str) -> Dict[str, Any]:
        """Extract/analyze raw text input"""
        word_count = len(text.split())
        
        # Try to extract a title from the first line
        lines = text.strip().split('\n')
        title = lines[0] if lines else 'Text Analysis'
        
        return {
            'success': True,
            'title': title[:100],  # Limit title length
            'text': text,
            'author': None,
            'publish_date': None,
            'url': None,
            'domain': 'text-input',
            'word_count': word_count
        }


# Main ArticleExtractor class that inherits from BaseAnalyzer
class ArticleExtractor(BaseAnalyzer):
    """Article extraction service that inherits from BaseAnalyzer"""
    
    def __init__(self):
        # CRITICAL: Initialize parent class FIRST
        super().__init__('article_extractor')
        
        logger.info("=" * 60)
        logger.info("ArticleExtractor.__init__() STARTING")
        logger.info(f"Service name: {self.service_name}")
        logger.info(f"Is available (from parent): {self.is_available}")
        logger.info("=" * 60)
        
        try:
            self._legacy = LegacyArticleExtractor()
            logger.info("ArticleExtractor initialized successfully with legacy extractor")
        except Exception as e:
            logger.error(f"Failed to initialize LegacyArticleExtractor: {e}")
            self._legacy = None
            logger.warning("ArticleExtractor will use basic extraction fallback")
        
        # Double-check availability
        self.is_available = self._check_availability()
        
        logger.info(f"ArticleExtractor initialization complete: is_available={self.is_available}")
        logger.info("=" * 60)
    
    def _check_availability(self) -> bool:
        """Check if the service is available"""
        # Article extraction is always available (has fallback methods)
        return True
    
    def get_error_result(self, error_message: str) -> Dict[str, Any]:
        """Override to ensure 'success' field is always included"""
        return {
            'service': self.service_name,
            'success': False,  # CRITICAL: This must be included!
            'available': self.is_available,
            'error': error_message,
            'timestamp': time.time()
        }
    
    def get_timeout_result(self) -> Dict[str, Any]:
        """Override to ensure 'success' field is always included"""
        return {
            'service': self.service_name,
            'success': False,  # CRITICAL: This must be included!
            'available': self.is_available,
            'error': 'Service timeout',
            'timestamp': time.time()
        }
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract article from URL or text
        Returns standardized service response
        """
        logger.info("=" * 60)
        logger.info("ArticleExtractor.analyze() CALLED")
        logger.info("=" * 60)
        
        try:
            logger.info(f"ArticleExtractor.analyze called with data keys: {list(data.keys())}")
            
            # Handle different input formats
            url = None
            text = None
            content_type = 'unknown'
            
            # New format: { 'url': '...' } or { 'text': '...' }
            if 'url' in data:
                url = data['url']
                content_type = 'url'
                logger.info(f"Using new format - URL: {url}")
            elif 'text' in data:
                text = data['text']
                content_type = 'text'
                logger.info(f"Using new format - text length: {len(text)}")
            # Legacy format: { 'content': '...', 'content_type': 'url'/'text' }
            elif 'content' in data and 'content_type' in data:
                if data['content_type'] == 'url':
                    url = data['content']
                    content_type = 'url'
                else:
                    text = data['content']
                    content_type = 'text'
                logger.info(f"Using legacy format - content: {data['content'][:100]}..., content_type: {data['content_type']}")
            else:
                error_msg = "Invalid input format. Expected {'url': '...'} or {'text': '...'}"
                logger.error(f"ArticleExtractor.analyze error: {error_msg}")
                return self.get_error_result(error_msg)
            
            # Process based on content type
            if content_type == 'url' and url:
                logger.info(f"Extracting from URL: {url}")
                result = self._extract_from_url(url)
                logger.info(f"URL extraction completed - success={result.get('success', False)}, has_error={'error' in result}")
                return result
            elif content_type == 'text' and text:
                logger.info(f"Extracting from text, length: {len(text)}")
                result = self._extract_from_text(text)
                logger.info(f"Text extraction completed - success={result.get('success', False)}")
                return result
            else:
                error_msg = f"Invalid content type or missing content: content_type={content_type}"
                logger.error(f"ArticleExtractor.analyze error: {error_msg}")
                return self.get_error_result(error_msg)
                
        except Exception as e:
            logger.error(f"ArticleExtractor.analyze failed with unexpected error: {e}", exc_info=True)
            return self.get_error_result(f"Unexpected error during extraction: {str(e)}")
    
    def _extract_from_url(self, url: str) -> Dict[str, Any]:
        """Extract article from URL and return standardized response"""
        try:
            logger.info(f"Starting URL extraction for: {url}")
            
            if self._legacy:
                # Use legacy method if available
                result = self._legacy.extract_from_url(url)
            else:
                # Fallback to basic extraction
                logger.warning("Using basic extraction fallback (legacy extractor not available)")
                result = self._basic_url_extraction(url)
            
            # Log the extraction result
            logger.info(f"Extraction result - success: {result.get('success')}, "
                       f"error: {result.get('error', 'None')}, "
                       f"word_count: {result.get('word_count', 0)}")
            
            # Check if extraction succeeded
            if result.get('success'):
                # Return standardized service response with data wrapped
                response = {
                    'service': self.service_name,
                    'success': True,
                    'data': {
                        'title': result.get('title', 'Untitled'),
                        'text': result.get('text', ''),
                        'author': result.get('author'),
                        'publish_date': result.get('publish_date'),
                        'url': result.get('url', url),
                        'domain': result.get('domain'),
                        'description': result.get('description'),
                        'image': result.get('image'),
                        'keywords': result.get('keywords', []),
                        'word_count': result.get('word_count', 0),
                        'extraction_metadata': result.get('extraction_metadata', {}),
                        'extracted_at': result.get('extracted_at')
                    },
                    'metadata': {
                        'extraction_method': result.get('extraction_metadata', {}).get('method', 'unknown'),
                        'duration': result.get('extraction_metadata', {}).get('duration', 0)
                    }
                }
                logger.info(f"Returning successful extraction response for {url}")
                return response
            else:
                # Return error in standard format
                error_msg = result.get('error', 'Extraction failed')
                logger.error(f"Extraction failed for {url}: {error_msg}")
                return self.get_error_result(error_msg)
                
        except Exception as e:
            logger.error(f"Article extraction from URL failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _extract_from_text(self, text: str) -> Dict[str, Any]:
        """Extract/analyze raw text and return standardized response"""
        try:
            logger.info("Starting text extraction")
            
            if self._legacy:
                # Use legacy method if available
                result = self._legacy.extract_from_text(text)
            else:
                # Fallback to basic text analysis
                result = self._basic_text_extraction(text)
            
            # Return standardized service response with data wrapped
            response = {
                'service': self.service_name,
                'success': True,
                'data': {
                    'title': result.get('title', 'Text Analysis'),
                    'text': result.get('text', text),
                    'author': result.get('author'),
                    'publish_date': result.get('publish_date'),
                    'url': result.get('url'),
                    'domain': result.get('domain', 'text-input'),
                    'word_count': result.get('word_count', len(text.split())),
                    'extraction_metadata': {'method': 'text_analysis'}
                }
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Text extraction failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _basic_url_extraction(self, url: str) -> Dict[str, Any]:
        """Basic URL extraction fallback"""
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic information
            title = soup.find('title')
            title = title.get_text(strip=True) if title else 'Untitled'
            
            # Try to find main content
            content = None
            for tag in ['article', 'main', 'div']:
                element = soup.find(tag)
                if element:
                    paragraphs = element.find_all('p')
                    if paragraphs:
                        content = '\n\n'.join(p.get_text(strip=True) for p in paragraphs)
                        break
            
            if not content:
                # Fallback to all paragraphs
                paragraphs = soup.find_all('p')
                content = '\n\n'.join(p.get_text(strip=True) for p in paragraphs[:20])  # Limit to 20 paragraphs
            
            word_count = len(content.split()) if content else 0
            logger.info(f"Basic extraction completed: {word_count} words extracted")
            
            return {
                'success': True,
                'title': title,
                'text': content or 'Content extraction failed',
                'url': url,
                'domain': urlparse(url).netloc,
                'word_count': word_count,
                'extraction_metadata': {
                    'method': 'basic_fallback'
                }
            }
            
        except Exception as e:
            logger.error(f"Basic extraction failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': f'Basic extraction failed: {str(e)}'
            }
    
    def _basic_text_extraction(self, text: str) -> Dict[str, Any]:
        """Basic text analysis fallback"""
        lines = text.strip().split('\n')
        title = lines[0][:100] if lines else 'Text Analysis'
        
        return {
            'success': True,
            'title': title,
            'text': text,
            'domain': 'text-input',
            'word_count': len(text.split())
        }
    
    def extract_article(self, url: str) -> Dict[str, Any]:
        """Legacy compatibility method"""
        return self.analyze({'url': url})
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        info = super().get_service_info()
        info.update({
            'extraction_methods': {
                'enhanced_requests': True,
                'cloudscraper': CLOUDSCRAPER_AVAILABLE,
                'curl_cffi': CURL_CFFI_AVAILABLE,
                'selenium': SELENIUM_AVAILABLE,
                'playwright': PLAYWRIGHT_AVAILABLE,
                'cookies': True,
                'proxy': True,
                'emergency_fallback': True
            },
            'supports_live_news': True,
            'supports_text_input': True
        })
        return info
