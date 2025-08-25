"""
Enhanced Article Extraction Service - Robust version for resistant sites
Extracts article content from URLs with multiple anti-bot bypass methods
"""

import json
import re
import time
import logging
import requests
import urllib3
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse, urljoin
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

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    OPTIONAL_LIBRARIES['selenium'] = True
except ImportError:
    OPTIONAL_LIBRARIES['selenium'] = False

try:
    from playwright.sync_api import sync_playwright
    OPTIONAL_LIBRARIES['playwright'] = True
except ImportError:
    OPTIONAL_LIBRARIES['playwright'] = False

try:
    import undetected_chromedriver as uc
    OPTIONAL_LIBRARIES['undetected_chromedriver'] = True
except ImportError:
    OPTIONAL_LIBRARIES['undetected_chromedriver'] = False

logger = logging.getLogger(__name__)

class RobustCircuitBreaker:
    """Improved circuit breaker with exponential backoff"""
    
    def __init__(self, failure_threshold=5, base_timeout=60, max_timeout=1800):
        self.failure_threshold = failure_threshold
        self.base_timeout = base_timeout
        self.max_timeout = max_timeout
        self.failures = {}
        self.last_failure_time = {}
        self.blocked_until = {}
        self.last_error = {}
    
    def record_failure(self, domain: str, error: str):
        """Record failure with exponential backoff"""
        current_time = time.time()
        
        if domain not in self.failures:
            self.failures[domain] = 0
            
        self.failures[domain] += 1
        self.last_failure_time[domain] = current_time
        self.last_error[domain] = error
        
        if self.failures[domain] >= self.failure_threshold:
            # Exponential backoff: 60s, 120s, 240s, 480s, up to max
            timeout = min(self.base_timeout * (2 ** (self.failures[domain] - self.failure_threshold)), 
                         self.max_timeout)
            self.blocked_until[domain] = current_time + timeout
            logger.warning(f"Circuit breaker activated for {domain} (attempt #{self.failures[domain]}), "
                         f"blocked for {timeout}s until {self.blocked_until[domain]}")
    
    def record_success(self, domain: str):
        """Record success and reset counters"""
        if domain in self.failures:
            self.failures[domain] = 0
            if domain in self.blocked_until:
                del self.blocked_until[domain]
                logger.info(f"Circuit breaker reset for {domain}")
    
    def is_blocked(self, domain: str) -> bool:
        """Check if domain is blocked"""
        if domain not in self.blocked_until:
            return False
            
        current_time = time.time()
        if current_time >= self.blocked_until[domain]:
            # Reset the block
            del self.blocked_until[domain]
            self.failures[domain] = max(0, self.failures[domain] - 1)  # Slowly reduce failure count
            return False
            
        return True
    
    def get_last_error(self, domain: str) -> str:
        return self.last_error.get(domain, "Unknown error")


class RobustArticleExtractor:
    """Robust article extraction with extensive anti-bot measures"""
    
    def __init__(self):
        logger.info(f"Initializing RobustArticleExtractor with available libraries: {OPTIONAL_LIBRARIES}")
        
        # Initialize session with robust configuration
        self.session = self._create_robust_session()
        
        # Initialize optional components
        self.ua = None
        if OPTIONAL_LIBRARIES.get('fake_useragent'):
            try:
                self.ua = UserAgent()
                logger.info("UserAgent initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize UserAgent: {e}")
        
        self.cloudscraper_session = None
        if OPTIONAL_LIBRARIES.get('cloudscraper'):
            try:
                self.cloudscraper_session = cloudscraper.create_scraper(
                    browser={
                        'browser': 'chrome',
                        'platform': 'windows',
                        'desktop': True
                    }
                )
                logger.info("Cloudscraper session initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Cloudscraper: {e}")
        
        # Circuit breaker with improved settings
        self.circuit_breaker = RobustCircuitBreaker()
        
        # Thread pool for parallel attempts
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # Configuration
        self.timeout = 30  # Increased timeout
        self.browser_timeout = 45
        self.min_content_length = 50  # Reduced for better detection
        self.min_paragraphs = 2  # Reduced for better detection
        self.min_words_per_paragraph = 5  # Reduced for better detection
        
        # Track methods
        self.methods_tried = []
        
        # User agents pool
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0'
        ]
    
    def _create_robust_session(self) -> requests.Session:
        """Create a robust requests session with retry logic and proper headers"""
        session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504, 520, 522, 524],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Default headers
        session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        return session
    
    def _get_random_headers(self, url: str = None) -> Dict[str, str]:
        """Generate realistic, randomized headers"""
        
        # Get user agent
        if self.ua:
            try:
                user_agent = self.ua.random
            except:
                user_agent = random.choice(self.user_agents)
        else:
            user_agent = random.choice(self.user_agents)
        
        headers = {
            'User-Agent': user_agent,
            'Accept': random.choice([
                'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            ]),
            'Accept-Language': random.choice([
                'en-US,en;q=0.9',
                'en-US,en;q=0.8',
                'en-US,en;q=0.5'
            ]),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': random.choice(['none', 'same-origin', 'cross-site']),
            'Sec-Fetch-User': '?1',
            'Cache-Control': random.choice(['max-age=0', 'no-cache']),
        }
        
        # Add referrer sometimes
        if url and random.random() > 0.5:
            domain = urlparse(url).netloc
            headers['Referer'] = f'https://www.google.com/search?q={domain}'
        
        return headers
    
    def extract_from_url(self, url: str) -> Dict[str, Any]:
        """Main extraction method with multiple robust approaches"""
        start_time = time.time()
        logger.info(f"Starting robust extraction for URL: {url}")
        
        # Reset methods tried
        self.methods_tried = []
        domain = urlparse(url).netloc
        
        # Check circuit breaker
        if self.circuit_breaker.is_blocked(domain):
            last_error = self.circuit_breaker.get_last_error(domain)
            logger.warning(f"Domain {domain} is circuit-broken. Last error: {last_error}")
            return self._create_user_friendly_error(url, domain, f'Domain temporarily blocked: {last_error}')
        
        # Build extraction methods in order of preference
        extraction_methods = []
        
        # Quick HTTP methods first
        extraction_methods.append(('enhanced_requests', self._enhanced_requests_extract))
        extraction_methods.append(('requests_with_session', self._requests_with_session_extract))
        
        # Anti-cloudflare methods
        if self.cloudscraper_session:
            extraction_methods.append(('cloudscraper', self._cloudscraper_extract))
        
        if OPTIONAL_LIBRARIES.get('curl_cffi'):
            extraction_methods.append(('curl_cffi', self._curl_cffi_extract))
        
        # Cookie and header manipulation
        extraction_methods.append(('cookies_bypass', self._cookies_bypass_extract))
        extraction_methods.append(('mobile_headers', self._mobile_headers_extract))
        
        # Browser automation (most reliable but slower)
        if OPTIONAL_LIBRARIES.get('undetected_chromedriver'):
            extraction_methods.append(('undetected_chrome', self._undetected_chrome_extract))
        
        if OPTIONAL_LIBRARIES.get('selenium'):
            extraction_methods.append(('selenium_stealth', self._selenium_stealth_extract))
        
        if OPTIONAL_LIBRARIES.get('playwright'):
            extraction_methods.append(('playwright_stealth', self._playwright_stealth_extract))
        
        # Final fallbacks
        extraction_methods.append(('archive_fallback', self._archive_fallback_extract))
        extraction_methods.append(('rss_fallback', self._rss_fallback_extract))
        
        last_error = None
        html_content = None
        
        # Try each method
        for method_name, method_func in extraction_methods:
            try:
                logger.info(f"Attempting {method_name} for {url}")
                self.methods_tried.append(method_name)
                
                result = method_func(url)
                
                if result.get('success') and result.get('word_count', 0) > self.min_content_length:
                    # Success!
                    self.circuit_breaker.record_success(domain)
                    
                    # Store HTML content
                    if 'html' in result:
                        html_content = result['html']
                    
                    # Add metadata
                    result['extraction_metadata'] = result.get('extraction_metadata', {})
                    result['extraction_metadata'].update({
                        'duration': time.time() - start_time,
                        'method': method_name,
                        'methods_tried': self.methods_tried,
                        'libraries_available': OPTIONAL_LIBRARIES
                    })
                    
                    if html_content:
                        result['html'] = html_content
                    
                    logger.info(f"SUCCESS: Extracted {result.get('word_count', 0)} words using {method_name}")
                    return result
                
                else:
                    last_error = result.get('error', f'{method_name} returned insufficient content')
                    logger.warning(f"{method_name} failed: {last_error}")
                    
            except Exception as e:
                last_error = f"{method_name} exception: {str(e)}"
                logger.warning(last_error, exc_info=True)
        
        # All methods failed
        logger.error(f"All {len(extraction_methods)} extraction methods failed for {url}")
        self.circuit_breaker.record_failure(domain, last_error)
        
        return self._create_user_friendly_error(url, domain, last_error)
    
    def _enhanced_requests_extract(self, url: str) -> Dict[str, Any]:
        """Enhanced requests with better headers and error handling"""
        try:
            headers = self._get_random_headers(url)
            
            # Add delay to seem more human
            time.sleep(random.uniform(0.5, 2.0))
            
            response = self.session.get(
                url, 
                headers=headers, 
                timeout=self.timeout,
                allow_redirects=True,
                verify=False  # Skip SSL verification for problematic sites
            )
            response.raise_for_status()
            
            if len(response.content) < 1000:  # Too small, likely blocked
                return {'success': False, 'error': 'Response too small, likely blocked'}
            
            return self._parse_content(response.text, url)
            
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Request timeout'}
        except requests.exceptions.ConnectionError:
            return {'success': False, 'error': 'Connection failed'}
        except Exception as e:
            return {'success': False, 'error': f'Enhanced requests failed: {str(e)}'}
    
    def _requests_with_session_extract(self, url: str) -> Dict[str, Any]:
        """Requests with persistent session and cookie handling"""
        try:
            # Create fresh session for this attempt
            session = requests.Session()
            headers = self._get_random_headers(url)
            session.headers.update(headers)
            
            # First, visit the homepage to get cookies
            domain = urlparse(url).netloc
            homepage = f"https://{domain}"
            
            try:
                session.get(homepage, timeout=10, verify=False)
                time.sleep(random.uniform(1, 3))
            except:
                pass  # Continue even if homepage fails
            
            # Now get the actual page
            response = session.get(url, timeout=self.timeout, verify=False)
            response.raise_for_status()
            
            return self._parse_content(response.text, url)
            
        except Exception as e:
            return {'success': False, 'error': f'Session requests failed: {str(e)}'}
    
    def _cloudscraper_extract(self, url: str) -> Dict[str, Any]:
        """CloudScraper for Cloudflare bypass"""
        try:
            if not self.cloudscraper_session:
                return {'success': False, 'error': 'Cloudscraper not available'}
            
            time.sleep(random.uniform(1, 3))
            response = self.cloudscraper_session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            return self._parse_content(response.text, url)
            
        except Exception as e:
            return {'success': False, 'error': f'Cloudscraper failed: {str(e)}'}
    
    def _curl_cffi_extract(self, url: str) -> Dict[str, Any]:
        """curl_cffi for TLS fingerprint spoofing"""
        try:
            headers = self._get_random_headers(url)
            
            response = curl_requests.get(
                url,
                headers=headers,
                timeout=self.timeout,
                impersonate="chrome120",  # Latest Chrome impersonation
                verify=False
            )
            response.raise_for_status()
            
            return self._parse_content(response.text, url)
            
        except Exception as e:
            return {'success': False, 'error': f'curl_cffi failed: {str(e)}'}
    
    def _cookies_bypass_extract(self, url: str) -> Dict[str, Any]:
        """Try with common consent/bypass cookies"""
        try:
            session = requests.Session()
            headers = self._get_random_headers(url)
            session.headers.update(headers)
            
            domain = urlparse(url).netloc
            
            # Common consent/bypass cookies
            bypass_cookies = {
                'gdpr': '1',
                'consent': 'yes',
                'cookies_accepted': 'true',
                'age_verified': 'true',
                'cookie_consent': 'accepted',
                'privacy_consent': 'true',
                'euconsent-v2': 'accepted',
                '_sp_enable_dfp_personalized_ads': 'true'
            }
            
            for name, value in bypass_cookies.items():
                session.cookies.set(name, value, domain=domain)
            
            time.sleep(random.uniform(1, 2))
            response = session.get(url, timeout=self.timeout, verify=False)
            response.raise_for_status()
            
            return self._parse_content(response.text, url)
            
        except Exception as e:
            return {'success': False, 'error': f'Cookies bypass failed: {str(e)}'}
    
    def _mobile_headers_extract(self, url: str) -> Dict[str, Any]:
        """Try with mobile user agent - some sites are less restrictive"""
        try:
            mobile_agents = [
                'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36',
                'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36'
            ]
            
            headers = {
                'User-Agent': random.choice(mobile_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(url, headers=headers, timeout=self.timeout, verify=False)
            response.raise_for_status()
            
            return self._parse_content(response.text, url)
            
        except Exception as e:
            return {'success': False, 'error': f'Mobile headers failed: {str(e)}'}
    
    def _undetected_chrome_extract(self, url: str) -> Dict[str, Any]:
        """Undetected Chrome - most effective for bot detection"""
        try:
            if not OPTIONAL_LIBRARIES.get('undetected_chromedriver'):
                return {'success': False, 'error': 'undetected-chromedriver not available'}
            
            options = uc.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-extensions')
            options.add_argument('--no-first-run')
            options.add_argument('--disable-default-apps')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=VizDisplayCompositor')
            
            # Run headless
            options.add_argument('--headless=new')
            
            driver = uc.Chrome(options=options)
            
            try:
                driver.set_page_load_timeout(self.browser_timeout)
                driver.get(url)
                
                # Wait for content to load
                time.sleep(random.uniform(3, 7))
                
                # Scroll to trigger lazy loading
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
                time.sleep(1)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight*2/3);")
                time.sleep(1)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                html = driver.page_source
                
                return self._parse_content(html, url)
                
            finally:
                try:
                    driver.quit()
                except:
                    pass
                    
        except Exception as e:
            return {'success': False, 'error': f'Undetected Chrome failed: {str(e)}'}
    
    def _selenium_stealth_extract(self, url: str) -> Dict[str, Any]:
        """Selenium with stealth techniques"""
        try:
            if not OPTIONAL_LIBRARIES.get('selenium'):
                return {'success': False, 'error': 'Selenium not available'}
            
            options = Options()
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=VizDisplayCompositor')
            options.add_argument(f'--user-agent={random.choice(self.user_agents)}')
            
            # Additional stealth options
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            driver = webdriver.Chrome(options=options)
            
            try:
                # Execute stealth script
                driver.execute_script("""
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                    Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                """)
                
                driver.set_page_load_timeout(self.browser_timeout)
                driver.get(url)
                
                # Wait and scroll
                time.sleep(random.uniform(3, 6))
                
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                time.sleep(2)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                html = driver.page_source
                
                return self._parse_content(html, url)
                
            finally:
                try:
                    driver.quit()
                except:
                    pass
                    
        except Exception as e:
            return {'success': False, 'error': f'Selenium stealth failed: {str(e)}'}
    
    def _playwright_stealth_extract(self, url: str) -> Dict[str, Any]:
        """Playwright with stealth configuration"""
        try:
            if not OPTIONAL_LIBRARIES.get('playwright'):
                return {'success': False, 'error': 'Playwright not available'}
            
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor',
                        '--disable-blink-features=AutomationControlled'
                    ]
                )
                
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent=random.choice(self.user_agents)
                )
                
                # Add stealth scripts
                context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                    Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                """)
                
                page = context.new_page()
                
                try:
                    response = page.goto(url, timeout=self.browser_timeout * 1000, wait_until='domcontentloaded')
                    
                    if response and response.status >= 400:
                        return {'success': False, 'error': f'HTTP {response.status}'}
                    
                    # Wait for content
                    page.wait_for_timeout(random.randint(3000, 6000))
                    
                    # Scroll to load content
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
                    page.wait_for_timeout(2000)
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(2000)
                    
                    html = page.content()
                    
                    return self._parse_content(html, url)
                    
                finally:
                    browser.close()
                    
        except Exception as e:
            return {'success': False, 'error': f'Playwright stealth failed: {str(e)}'}
    
    def _archive_fallback_extract(self, url: str) -> Dict[str, Any]:
        """Try to get content from archive.org as fallback"""
        try:
            archive_url = f"http://web.archive.org/web/{url}"
            headers = self._get_random_headers()
            
            response = requests.get(archive_url, headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                # Archive.org sometimes wraps content, so we need to extract carefully
                return self._parse_content(response.text, url)
            else:
                return {'success': False, 'error': 'No archive.org version found'}
                
        except Exception as e:
            return {'success': False, 'error': f'Archive fallback failed: {str(e)}'}
    
    def _rss_fallback_extract(self, url: str) -> Dict[str, Any]:
        """Try to find RSS feed and extract content"""
        try:
            domain = urlparse(url).netloc
            
            # Common RSS URLs to try
            rss_urls = [
                f"https://{domain}/rss",
                f"https://{domain}/feed",
                f"https://{domain}/rss.xml",
                f"https://{domain}/feed.xml",
                f"https://{domain}/atom.xml",
            ]
            
            headers = self._get_random_headers()
            
            for rss_url in rss_urls:
                try:
                    response = requests.get(rss_url, headers=headers, timeout=10)
                    if response.status_code == 200 and 'xml' in response.headers.get('content-type', '').lower():
                        # Found RSS feed - could extract article summaries
                        # For now, just indicate we found something
                        return {'success': False, 'error': 'Found RSS but article extraction from feeds not implemented'}
                except:
                    continue
            
            return {'success': False, 'error': 'No RSS feeds found'}
            
        except Exception as e:
            return {'success': False, 'error': f'RSS fallback failed: {str(e)}'}
    
    def _parse_content(self, html: str, url: str = None) -> Dict[str, Any]:
        """Robust content parsing with multiple extraction strategies"""
        try:
            if not html or len(html) < 100:
                return {'success': False, 'error': 'HTML content too short'}
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unwanted elements that interfere with extraction
            for element in soup.find_all(['script', 'style', 'nav', 'aside', 'footer', 'header']):
                element.decompose()
            
            # Extract content using multiple strategies
            content, extraction_metadata = self._extract_article_content_robust(soup, url)
            
            if not content or len(content.strip()) < self.min_content_length:
                return {'success': False, 'error': 'Could not extract sufficient article content'}
            
            # Extract metadata
            title = self._extract_title_robust(soup) or 'Untitled Article'
            author = self._extract_author_robust(soup)
            publish_date = self._extract_date_robust(soup)
            description = self._extract_description_robust(soup)
            image = self._extract_image_robust(soup, url) if url else None
            keywords = self._extract_keywords_robust(soup)
            
            # Clean and validate content
            content = self._clean_content_robust(content)
            word_count = len(content.split())
            
            if word_count < self.min_content_length:
                return {'success': False, 'error': f'Content too short: {word_count} words'}
            
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
                'extracted_at': datetime.now().isoformat(),
                'html': html  # Store HTML for other analyzers
            }
            
        except Exception as e:
            logger.error(f"Content parsing failed: {e}", exc_info=True)
            return {'success': False, 'error': f'Content parsing error: {str(e)}'}
    
    def _extract_article_content_robust(self, soup: BeautifulSoup, url: str = None) -> Tuple[Optional[str], Dict[str, Any]]:
        """Robust content extraction with multiple strategies"""
        metadata = {'extraction_method': 'unknown', 'content_indicators': [], 'issues': []}
        
        # Strategy 1: Structured data (JSON-LD)
        content = self._extract_from_structured_data(soup)
        if content and len(content.strip()) > self.min_content_length:
            metadata['extraction_method'] = 'structured_data'
            return content, metadata
        
        # Strategy 2: Article tags
        content = self._extract_from_article_tags(soup)
        if content and len(content.strip()) > self.min_content_length:
            metadata['extraction_method'] = 'article_tags'
            return content, metadata
        
        # Strategy 3: Main content containers
        content = self._extract_from_main_containers(soup)
        if content and len(content.strip()) > self.min_content_length:
            metadata['extraction_method'] = 'main_containers'
            return content, metadata
        
        # Strategy 4: Paragraph density analysis
        content = self._extract_by_paragraph_density(soup)
        if content and len(content.strip()) > self.min_content_length:
            metadata['extraction_method'] = 'paragraph_density'
            return content, metadata
        
        # Strategy 5: Fallback - all paragraphs
        content = self._extract_all_paragraphs(soup)
        if content and len(content.strip()) > self.min_content_length:
            metadata['extraction_method'] = 'all_paragraphs'
            return content, metadata
        
        return None, metadata
    
    def _extract_from_structured_data(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract content from JSON-LD structured data"""
        try:
            scripts = soup.find_all('script', {'type': 'application/ld+json'})
            for script in scripts:
                if script.string:
                    try:
                        data = json.loads(script.string)
                        content = self._extract_content_from_json_ld(data)
                        if content:
                            return content
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.debug(f"Structured data extraction failed: {e}")
        
        return None
    
    def _extract_content_from_json_ld(self, data: Any) -> Optional[str]:
        """Recursively extract article content from JSON-LD"""
        if isinstance(data, dict):
            # Look for articleBody or text content
            for field in ['articleBody', 'text', 'description', 'mainEntity']:
                if field in data and isinstance(data[field], str) and len(data[field]) > 100:
                    return data[field]
            
            # Check nested structures
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    content = self._extract_content_from_json_ld(value)
                    if content:
                        return content
                        
        elif isinstance(data, list):
            for item in data:
                content = self._extract_content_from_json_ld(item)
                if content:
                    return content
        
        return None
    
    def _extract_from_article_tags(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract from article HTML5 tags"""
        article_tags = soup.find_all('article')
        for article in article_tags:
            paragraphs = article.find_all('p')
            if len(paragraphs) >= self.min_paragraphs:
                content_parts = []
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if len(text.split()) >= self.min_words_per_paragraph:
                        content_parts.append(text)
                
                if content_parts:
                    return '\n\n'.join(content_parts)
        
        return None
    
    def _extract_from_main_containers(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract from common content container selectors"""
        selectors = [
            {'class': re.compile(r'article[-_]?body|story[-_]?body|content[-_]?body|post[-_]?content', re.I)},
            {'class': re.compile(r'entry[-_]?content|main[-_]?content', re.I)},
            {'id': re.compile(r'article|story|content|main', re.I)},
            {'role': 'main'},
            'main'
        ]
        
        for selector in selectors:
            if isinstance(selector, str):
                elements = soup.find_all(selector)
            else:
                elements = soup.find_all('div', selector)
                if not elements:
                    elements = soup.find_all(['main', 'section', 'article'], selector)
            
            for element in elements:
                paragraphs = element.find_all('p')
                if len(paragraphs) >= self.min_paragraphs:
                    content_parts = []
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if len(text.split()) >= self.min_words_per_paragraph:
                            content_parts.append(text)
                    
                    if len(content_parts) >= self.min_paragraphs:
                        return '\n\n'.join(content_parts)
        
        return None
    
    def _extract_by_paragraph_density(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract by finding areas with high paragraph density"""
        all_elements = soup.find_all(['div', 'section', 'article'])
        
        best_element = None
        best_score = 0
        
        for element in all_elements:
            paragraphs = element.find_all('p', recursive=False)  # Direct children only
            if len(paragraphs) < self.min_paragraphs:
                continue
            
            # Score based on paragraph count and average length
            total_words = sum(len(p.get_text(strip=True).split()) for p in paragraphs)
            avg_words = total_words / len(paragraphs) if paragraphs else 0
            
            # Good content has moderate paragraph count and reasonable word count
            score = len(paragraphs) * min(avg_words / 20, 1.0)  # Cap at 20 words avg
            
            if score > best_score:
                best_score = score
                best_element = element
        
        if best_element:
            paragraphs = best_element.find_all('p')
            content_parts = []
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text.split()) >= self.min_words_per_paragraph:
                    content_parts.append(text)
            
            if len(content_parts) >= self.min_paragraphs:
                return '\n\n'.join(content_parts)
        
        return None
    
    def _extract_all_paragraphs(self, soup: BeautifulSoup) -> Optional[str]:
        """Fallback: extract all reasonable paragraphs"""
        all_paragraphs = soup.find_all('p')
        content_parts = []
        
        for p in all_paragraphs:
            text = p.get_text(strip=True)
            # Skip very short paragraphs and navigation/menu text
            if (len(text.split()) >= self.min_words_per_paragraph and 
                not re.match(r'^(home|about|contact|menu|search|login)', text.lower())):
                content_parts.append(text)
        
        if len(content_parts) >= self.min_paragraphs:
            return '\n\n'.join(content_parts)
        
        return None
    
    def _extract_title_robust(self, soup: BeautifulSoup) -> Optional[str]:
        """Robust title extraction"""
        strategies = [
            lambda: soup.find('meta', property='og:title')['content'],
            lambda: soup.find('meta', {'name': 'twitter:title'})['content'],
            lambda: soup.find('h1').get_text(strip=True),
            lambda: soup.find('title').get_text(strip=True).split('|')[0].split('-')[0].strip(),
            lambda: soup.find('meta', property='article:title')['content'],
        ]
        
        for strategy in strategies:
            try:
                title = strategy()
                if title and len(title.strip()) > 3:
                    return title.strip()
            except:
                continue
        
        return None
    
    def _extract_author_robust(self, soup: BeautifulSoup) -> Optional[str]:
        """Robust author extraction"""
        # Try JSON-LD first
        try:
            scripts = soup.find_all('script', {'type': 'application/ld+json'})
            for script in scripts:
                if script.string:
                    try:
                        data = json.loads(script.string)
                        author = self._extract_author_from_json_ld(data)
                        if author:
                            return author
                    except:
                        continue
        except:
            pass
        
        # Meta tags
        meta_selectors = [
            {'name': 'author'},
            {'property': 'article:author'},
            {'name': 'byl'},
            {'name': 'citation_author'},
        ]
        
        for selector in meta_selectors:
            try:
                meta = soup.find('meta', selector)
                if meta and meta.get('content'):
                    author = self._clean_author_name(meta['content'])
                    if author:
                        return author
            except:
                continue
        
        # Byline elements
        byline_selectors = [
            {'class': re.compile(r'byline|author|writer', re.I)},
            {'itemprop': 'author'},
        ]
        
        for selector in byline_selectors:
            try:
                elem = soup.find(['span', 'div', 'p', 'a'], selector)
                if elem:
                    author = self._clean_author_name(elem.get_text(strip=True))
                    if author:
                        return author
            except:
                continue
        
        return None
    
    def _extract_author_from_json_ld(self, data: Any) -> Optional[str]:
        """Extract author from JSON-LD data"""
        if isinstance(data, dict):
            if 'author' in data:
                author_data = data['author']
                if isinstance(author_data, str):
                    return self._clean_author_name(author_data)
                elif isinstance(author_data, dict) and 'name' in author_data:
                    return self._clean_author_name(author_data['name'])
                elif isinstance(author_data, list) and author_data:
                    first_author = author_data[0]
                    if isinstance(first_author, str):
                        return self._clean_author_name(first_author)
                    elif isinstance(first_author, dict) and 'name' in first_author:
                        return self._clean_author_name(first_author['name'])
        
        return None
    
    def _clean_author_name(self, author: str) -> Optional[str]:
        """Clean author name"""
        if not author:
            return None
        
        # Remove common prefixes and suffixes
        author = re.sub(r'^(By|by|BY|Written by|Author:)\s+', '', author)
        author = re.sub(r'\s*[\|\-]\s*(Reporter|Writer|Journalist).*$', '', author, flags=re.I)
        author = re.sub(r'\s+', ' ', author).strip()
        
        # Validate
        if (len(author) > 2 and len(author) < 100 and 
            len(author.split()) <= 5 and
            re.match(r"^[A-Za-z\s\-'.]+$", author)):
            return author
        
        return None
    
    def _extract_date_robust(self, soup: BeautifulSoup) -> Optional[str]:
        """Robust date extraction"""
        strategies = [
            lambda: soup.find('meta', property='article:published_time')['content'],
            lambda: soup.find('meta', {'name': 'publish_date'})['content'],
            lambda: soup.find('time')['datetime'],
            lambda: soup.find('meta', property='article:modified_time')['content'],
        ]
        
        for strategy in strategies:
            try:
                date = strategy()
                if date:
                    return date
            except:
                continue
        
        return None
    
    def _extract_description_robust(self, soup: BeautifulSoup) -> Optional[str]:
        """Robust description extraction"""
        strategies = [
            lambda: soup.find('meta', property='og:description')['content'],
            lambda: soup.find('meta', {'name': 'description'})['content'],
            lambda: soup.find('meta', {'name': 'twitter:description'})['content'],
        ]
        
        for strategy in strategies:
            try:
                desc = strategy()
                if desc and len(desc.strip()) > 10:
                    return desc.strip()
            except:
                continue
        
        return None
    
    def _extract_image_robust(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Robust image extraction"""
        strategies = [
            lambda: soup.find('meta', property='og:image')['content'],
            lambda: soup.find('meta', {'name': 'twitter:image'})['content'],
        ]
        
        for strategy in strategies:
            try:
                image_url = strategy()
                if image_url:
                    return urljoin(base_url, image_url)
            except:
                continue
        
        return None
    
    def _extract_keywords_robust(self, soup: BeautifulSoup) -> List[str]:
        """Robust keywords extraction"""
        try:
            keywords_tag = soup.find('meta', {'name': 'keywords'})
            if keywords_tag and keywords_tag.get('content'):
                keywords = [k.strip() for k in keywords_tag['content'].split(',')]
                return [k for k in keywords if len(k) > 2]
        except:
            pass
        
        return []
    
    def _clean_content_robust(self, content: str) -> str:
        """Robust content cleaning"""
        if not content:
            return ""
        
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        
        # Remove common artifacts
        content = re.sub(r'Share this article.*?(\n|$)', '', content, flags=re.I)
        content = re.sub(r'Read more:.*?(\n|$)', '', content, flags=re.I)
        content = re.sub(r'Subscribe.*?(\n|$)', '', content, flags=re.I)
        content = re.sub(r'Advertisement\s*', '', content, flags=re.I)
        
        return content.strip()
    
    def _create_user_friendly_error(self, url: str, domain: str, last_error: str) -> Dict[str, Any]:
        """Create user-friendly error message"""
        methods_summary = f"Tried {len(self.methods_tried)} extraction methods: {', '.join(self.methods_tried)}"
        
        user_message = (
            f"Unable to extract article from {domain}.\n\n"
            f"This website appears to have strong anti-bot protection. "
            f"You can try:\n"
            f"1. Copy the article text from your browser\n"
            f"2. Use the 'Text' option instead of 'URL'\n"
            f"3. Try again later (site may be temporarily blocking requests)\n\n"
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
                'libraries_available': OPTIONAL_LIBRARIES,
                'suggestion': 'use_text_option'
            }
        }
    
    def extract_from_text(self, text: str) -> Dict[str, Any]:
        """Extract/analyze raw text input"""
        if not text or len(text.strip()) < 10:
            return {
                'success': False,
                'error': 'Text input is too short'
            }
        
        lines = text.strip().split('\n')
        title = lines[0][:100] if lines else 'Text Analysis'
        word_count = len(text.split())
        
        return {
            'success': True,
            'title': title,
            'text': text,
            'author': None,
            'publish_date': None,
            'url': None,
            'domain': 'text-input',
            'word_count': word_count,
            'extraction_metadata': {
                'method': 'text_analysis',
                'libraries_available': OPTIONAL_LIBRARIES
            }
        }


# Main ArticleExtractor class that inherits from BaseAnalyzer
class ArticleExtractor(BaseAnalyzer):
    """Article extraction service with robust anti-bot capabilities"""
    
    def __init__(self):
        super().__init__('article_extractor')
        
        logger.info("=" * 60)
        logger.info("RobustArticleExtractor.__init__() STARTING")
        logger.info(f"Service name: {self.service_name}")
        logger.info(f"Available libraries: {OPTIONAL_LIBRARIES}")
        logger.info("=" * 60)
        
        # Initialize _extractor first
        self._extractor = None
        
        try:
            self._extractor = RobustArticleExtractor()
            logger.info("RobustArticleExtractor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RobustArticleExtractor: {e}", exc_info=True)
            self._extractor = None
        
        # Now check availability
        self.is_available = self._check_availability()
        logger.info(f"ArticleExtractor initialization complete: is_available={self.is_available}")
        logger.info("=" * 60)
    
    def _check_availability(self) -> bool:
        """Check if service is available"""
        # Always return True - we have fallback methods even if advanced libraries fail
        return True
    
    def get_error_result(self, error_message: str) -> Dict[str, Any]:
        """Standardized error response"""
        return {
            'service': self.service_name,
            'success': False,
            'available': self.is_available,
            'error': error_message,
            'timestamp': time.time()
        }
    
    def get_timeout_result(self) -> Dict[str, Any]:
        """Standardized timeout response"""
        return {
            'service': self.service_name,
            'success': False,
            'available': self.is_available,
            'error': 'Service timeout',
            'timestamp': time.time()
        }
    
    def _basic_extraction_fallback(self, url: str) -> Dict[str, Any]:
        """Basic extraction using only standard libraries as absolute fallback"""
        try:
            import urllib.request
            import urllib.error
            
            # Create request with basic headers
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
                }
            )
            
            # Get the page
            with urllib.request.urlopen(req, timeout=30) as response:
                html = response.read().decode('utf-8', errors='ignore')
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title = title.get_text(strip=True) if title else 'Untitled'
            
            # Extract content - try multiple strategies
            content = None
            
            # Strategy 1: Article tags
            article = soup.find('article')
            if article:
                paragraphs = article.find_all('p')
                if paragraphs and len(paragraphs) >= 2:
                    content = '\n\n'.join(p.get_text(strip=True) for p in paragraphs 
                                        if len(p.get_text(strip=True).split()) >= 5)
            
            # Strategy 2: Main content containers
            if not content:
                for selector in ['main', '[role="main"]', '.article-body', '.story-body', '.content']:
                    try:
                        element = soup.select_one(selector)
                        if element:
                            paragraphs = element.find_all('p')
                            if paragraphs and len(paragraphs) >= 2:
                                content = '\n\n'.join(p.get_text(strip=True) for p in paragraphs 
                                                    if len(p.get_text(strip=True).split()) >= 5)
                                break
                    except:
                        continue
            
            # Strategy 3: All paragraphs as fallback
            if not content:
                all_paragraphs = soup.find_all('p')
                valid_paragraphs = []
                for p in all_paragraphs:
                    text = p.get_text(strip=True)
                    if len(text.split()) >= 10:  # Longer paragraphs only
                        valid_paragraphs.append(text)
                
                if len(valid_paragraphs) >= 2:
                    content = '\n\n'.join(valid_paragraphs[:20])  # Limit to first 20
            
            if not content or len(content.strip()) < 100:
                return {
                    'success': False,
                    'error': 'Could not extract sufficient content'
                }
            
            word_count = len(content.split())
            
            return {
                'success': True,
                'title': title,
                'text': content,
                'author': None,
                'publish_date': None,
                'url': url,
                'domain': urlparse(url).netloc,
                'description': None,
                'image': None,
                'keywords': [],
                'word_count': word_count,
                'extraction_metadata': {
                    'method': 'basic_fallback',
                    'libraries_available': OPTIONAL_LIBRARIES
                },
                'extracted_at': datetime.now().isoformat(),
                'html': html
            }
            
        except Exception as e:
            logger.error(f"Basic extraction fallback failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': f'Basic extraction failed: {str(e)}'
            }
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Main analysis method"""
        logger.info("=" * 60)
        logger.info("RobustArticleExtractor.analyze() CALLED")
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
                logger.info(f"Extracting from URL: {url}")
                
                # Try robust extractor first
                result = None
                if self._extractor:
                    try:
                        result = self._extractor.extract_from_url(url)
                    except Exception as e:
                        logger.warning(f"Robust extractor failed: {e}")
                        result = None
                
                # Fallback to basic extraction if robust failed
                if not result or not result.get('success'):
                    logger.info("Using basic extraction fallback")
                    result = self._basic_extraction_fallback(url)
                
            elif text:
                logger.info(f"Processing text input, length: {len(text)}")
                
                # Try robust extractor first
                result = None
                if self._extractor:
                    try:
                        result = self._extractor.extract_from_text(text)
                    except Exception as e:
                        logger.warning(f"Robust text processor failed: {e}")
                        result = None
                
                # Fallback to basic text processing
                if not result or not result.get('success'):
                    lines = text.strip().split('\n')
                    title = lines[0][:100] if lines else 'Text Analysis'
                    word_count = len(text.split())
                    
                    result = {
                        'success': True,
                        'title': title,
                        'text': text,
                        'author': None,
                        'publish_date': None,
                        'url': None,
                        'domain': 'text-input',
                        'word_count': word_count,
                        'extraction_metadata': {'method': 'basic_text_analysis'}
                    }
            else:
                return self.get_error_result("No URL or text provided")
            
            # Return standardized response
            if result and result.get('success'):
                return {
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
                        'extracted_at': result.get('extracted_at'),
                        'html': result.get('html')  # For other analyzers
                    },
                    'metadata': {
                        'extraction_method': result.get('extraction_metadata', {}).get('method', 'unknown'),
                        'methods_tried': result.get('extraction_metadata', {}).get('methods_tried', []),
                        'libraries_available': OPTIONAL_LIBRARIES,
                        'robust_extractor_available': self._extractor is not None
                    }
                }
            else:
                error_msg = result.get('error', 'Extraction failed') if result else 'No extraction result'
                return self.get_error_result(error_msg)
                
        except Exception as e:
            logger.error(f"ArticleExtractor.analyze failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        info = super().get_service_info()
        info.update({
            'extraction_methods': [
                'enhanced_requests',
                'requests_with_session', 
                'cloudscraper',
                'curl_cffi',
                'cookies_bypass',
                'mobile_headers',
                'undetected_chrome',
                'selenium_stealth',
                'playwright_stealth',
                'archive_fallback',
                'rss_fallback'
            ],
            'libraries_available': OPTIONAL_LIBRARIES,
            'supports_anti_bot_bypass': True,
            'supports_live_news': True,
            'supports_text_input': True
        })
        return info
