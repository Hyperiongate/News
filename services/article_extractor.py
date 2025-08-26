"""
Enhanced Article Extraction Service - Universal Scraper with Progressive Escalation
Incorporates the universal scraper strategy discussed for handling any URL
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


class EnhancedCircuitBreaker:
    """Enhanced circuit breaker with better recovery and domain-specific strategies"""
    
    def __init__(self):
        self.failures = {}
        self.last_error = {}
        self.domain_strategies = {}  # Track what worked for each domain
        self.success_methods = {}    # Track successful methods per domain
        self.max_failures = 8       # Increased threshold
        self.recovery_time = 600    # 10 minutes recovery
        self.last_attempt = {}
        
    def record_failure(self, domain: str, error: str, method: str):
        """Record failure with method information"""
        self.failures[domain] = self.failures.get(domain, 0) + 1
        self.last_error[domain] = error
        self.last_attempt[domain] = time.time()
        logger.warning(f"Circuit breaker: {domain} failed {self.failures[domain]} times with {method}: {error}")
        
    def record_success(self, domain: str, method: str):
        """Record successful method for future prioritization"""
        self.failures[domain] = 0
        if domain not in self.success_methods:
            self.success_methods[domain] = []
        if method not in self.success_methods[domain]:
            self.success_methods[domain].insert(0, method)  # Prioritize successful methods
        logger.info(f"Circuit breaker: {domain} succeeded with {method}")
        
    def is_blocked(self, domain: str) -> bool:
        """Check if domain is temporarily blocked with recovery logic"""
        if domain not in self.failures:
            return False
            
        failure_count = self.failures[domain]
        if failure_count < self.max_failures:
            return False
            
        # Check if recovery time has passed
        last_attempt = self.last_attempt.get(domain, 0)
        if time.time() - last_attempt > self.recovery_time:
            self.failures[domain] = max(0, self.failures[domain] - 2)  # Reduce failures
            return False
            
        return True
        
    def get_preferred_methods(self, domain: str) -> List[str]:
        """Get preferred methods for a domain based on past success"""
        return self.success_methods.get(domain, [])
        
    def get_last_error(self, domain: str) -> str:
        return self.last_error.get(domain, "Unknown error")


class UniversalScraper:
    """Universal scraper implementing the progressive escalation strategy"""
    
    def __init__(self):
        logger.info(f"Initializing UniversalScraper with available libraries: {OPTIONAL_LIBRARIES}")
        
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
        
        # Enhanced circuit breaker
        self.circuit_breaker = EnhancedCircuitBreaker()
        
        # Thread pool for parallel attempts
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # Configuration
        self.timeout = 30
        self.browser_timeout = 45
        self.min_content_length = 50
        self.min_paragraphs = 2
        self.min_words_per_paragraph = 5
        
        # Track methods
        self.methods_tried = []
        
        # Enhanced user agents pool (more realistic and current)
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0',
            # Mobile user agents for sites that are less restrictive to mobile
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36',
        ]
        
        # Common blocking indicators
        self.blocking_indicators = [
            'blocked', 'access denied', 'captcha', 'robot', 'bot detected',
            'please enable javascript', 'cloudflare', 'checking your browser',
            'ddos protection', 'security check', 'verify you are human',
            'too many requests', 'rate limit', 'temporarily unavailable',
            'service unavailable', 'forbidden', '403 forbidden', 'unauthorized'
        ]
    
    def _create_robust_session(self) -> requests.Session:
        """Create a robust requests session with retry logic and proper headers"""
        session = requests.Session()
        
        # Enhanced retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=2,  # Exponential backoff
            status_forcelist=[429, 500, 502, 503, 504, 520, 522, 524],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            raise_on_status=False
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Default headers (will be overridden by specific methods)
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
    
    def _get_enhanced_headers(self, url: str = None, strategy: str = "default") -> Dict[str, str]:
        """Generate enhanced headers based on strategy"""
        
        # Get user agent based on strategy
        if strategy == "mobile":
            user_agents = [ua for ua in self.user_agents if 'Mobile' in ua or 'iPhone' in ua or 'Android' in ua]
            user_agent = random.choice(user_agents) if user_agents else self.user_agents[0]
        elif self.ua:
            try:
                user_agent = self.ua.random
            except:
                user_agent = random.choice(self.user_agents)
        else:
            user_agent = random.choice(self.user_agents)
        
        # Base headers
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
                'en-US,en;q=0.5',
                'en-GB,en-US;q=0.9,en;q=0.8'
            ]),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Strategy-specific enhancements
        if strategy == "stealth":
            headers.update({
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': random.choice(['none', 'same-origin', 'cross-site']),
                'Sec-Fetch-User': '?1',
                'Cache-Control': random.choice(['max-age=0', 'no-cache']),
                'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"'
            })
        elif strategy == "social":
            # Add referer from social media
            headers['Referer'] = random.choice([
                'https://www.facebook.com/',
                'https://twitter.com/',
                'https://www.reddit.com/',
                'https://news.ycombinator.com/'
            ])
        elif strategy == "search":
            # Add referer from search engines
            if url:
                domain = urlparse(url).netloc
                headers['Referer'] = f'https://www.google.com/search?q={domain}'
            else:
                headers['Referer'] = 'https://www.google.com/'
                
        return headers
    
    def _is_valid_content(self, soup: BeautifulSoup) -> bool:
        """Enhanced content validation"""
        if not soup:
            return False
        
        text = soup.get_text().lower()
        
        # Check for blocking indicators
        for indicator in self.blocking_indicators:
            if indicator in text:
                logger.debug(f"Found blocking indicator: {indicator}")
                return False
        
        # Check for minimum content
        paragraphs = soup.find_all('p')
        valid_paragraphs = [p for p in paragraphs if len(p.get_text().split()) >= 5]
        
        if len(valid_paragraphs) < 2:
            logger.debug("Not enough valid paragraphs found")
            return False
            
        return True
    
    def extract_from_url(self, url: str) -> Dict[str, Any]:
        """Universal extraction with progressive escalation strategy"""
        start_time = time.time()
        logger.info(f"Starting universal extraction for URL: {url}")
        
        # Reset methods tried
        self.methods_tried = []
        domain = urlparse(url).netloc
        
        # Check circuit breaker
        if self.circuit_breaker.is_blocked(domain):
            last_error = self.circuit_breaker.get_last_error(domain)
            logger.warning(f"Domain {domain} is circuit-broken. Last error: {last_error}")
            return self._create_user_friendly_error(url, domain, f'Domain temporarily blocked: {last_error}')
        
        # Get preferred methods for this domain (if any worked before)
        preferred_methods = self.circuit_breaker.get_preferred_methods(domain)
        
        # Build extraction strategies in escalation order
        strategies = self._build_escalation_strategies(preferred_methods)
        
        last_error = None
        html_content = None
        
        # Try each strategy with enhanced error handling
        for strategy_name, strategy_func in strategies:
            try:
                logger.info(f"Attempting {strategy_name} for {url}")
                self.methods_tried.append(strategy_name)
                
                result = strategy_func(url)
                
                if result.get('success'):
                    # Validate content quality
                    if result.get('word_count', 0) > self.min_content_length:
                        # Success! Record this method for future use
                        self.circuit_breaker.record_success(domain, strategy_name)
                        
                        execution_time = time.time() - start_time
                        result['extraction_metadata']['execution_time'] = execution_time
                        result['extraction_metadata']['methods_tried'] = self.methods_tried
                        result['extraction_metadata']['successful_method'] = strategy_name
                        
                        logger.info(f"Successful extraction with {strategy_name} in {execution_time:.2f}s")
                        return result
                    else:
                        logger.warning(f"{strategy_name} returned insufficient content")
                else:
                    last_error = result.get('error', f'{strategy_name} failed')
                    logger.warning(f"{strategy_name} failed: {last_error}")
                    
                # Small delay between attempts to be respectful
                time.sleep(random.uniform(0.5, 1.5))
                
            except Exception as e:
                last_error = str(e)
                logger.error(f"{strategy_name} threw exception: {e}")
                self.circuit_breaker.record_failure(domain, last_error, strategy_name)
                continue
        
        # All methods failed
        self.circuit_breaker.record_failure(domain, last_error or 'All strategies failed', 'all')
        logger.error(f"All extraction strategies failed for {url}")
        return self._create_user_friendly_error(url, domain, last_error or 'All extraction methods failed')
    
    def _build_escalation_strategies(self, preferred_methods: List[str]) -> List[Tuple[str, callable]]:
        """Build extraction strategies in escalation order, prioritizing known working methods"""
        
        all_strategies = []
        
        # Level 1: Simple HTTP (fastest, works for ~50% of sites)
        all_strategies.append(('basic_requests', self._basic_requests_extract))
        all_strategies.append(('enhanced_headers', self._enhanced_headers_extract))
        
        # Level 2: Session and cookie handling (~70% success)
        all_strategies.append(('session_with_cookies', self._session_with_cookies_extract))
        all_strategies.append(('social_referer', self._social_referer_extract))
        all_strategies.append(('search_referer', self._search_referer_extract))
        
        # Level 3: Anti-bot libraries (~80% success)
        if self.cloudscraper_session:
            all_strategies.append(('cloudscraper', self._cloudscraper_extract))
        
        if OPTIONAL_LIBRARIES.get('curl_cffi'):
            all_strategies.append(('curl_cffi_stealth', self._curl_cffi_stealth_extract))
        
        # Level 4: Mobile and header spoofing (~85% success)
        all_strategies.append(('mobile_headers', self._mobile_headers_extract))
        all_strategies.append(('consent_cookies', self._consent_cookies_extract))
        
        # Level 5: Browser automation (~90% success but slower)
        if OPTIONAL_LIBRARIES.get('undetected_chromedriver'):
            all_strategies.append(('undetected_chrome', self._undetected_chrome_extract))
        
        if OPTIONAL_LIBRARIES.get('selenium'):
            all_strategies.append(('selenium_stealth', self._selenium_stealth_extract))
        
        if OPTIONAL_LIBRARIES.get('playwright'):
            all_strategies.append(('playwright_stealth', self._playwright_stealth_extract))
        
        # Level 6: Fallback methods
        all_strategies.append(('archive_fallback', self._archive_fallback_extract))
        
        # Prioritize known working methods for this domain
        if preferred_methods:
            prioritized = []
            remaining = []
            
            for name, func in all_strategies:
                if name in preferred_methods:
                    prioritized.append((name, func))
                else:
                    remaining.append((name, func))
            
            # Return prioritized methods first, then remaining
            return prioritized + remaining
        
        return all_strategies
    
    # EXTRACTION METHODS - Enhanced versions of existing methods
    
    def _basic_requests_extract(self, url: str) -> Dict[str, Any]:
        """Basic requests - fastest method"""
        try:
            headers = self._get_enhanced_headers(url)
            response = requests.get(url, headers=headers, timeout=15, verify=False, allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            if not self._is_valid_content(soup):
                return {'success': False, 'error': 'Content appears to be blocked or invalid'}
            
            return self._parse_content(response.text, url)
            
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Request timeout'}
        except requests.exceptions.ConnectionError:
            return {'success': False, 'error': 'Connection failed'}
        except Exception as e:
            return {'success': False, 'error': f'Basic requests failed: {str(e)}'}
    
    def _enhanced_headers_extract(self, url: str) -> Dict[str, Any]:
        """Enhanced headers with stealth techniques"""
        try:
            headers = self._get_enhanced_headers(url, strategy="stealth")
            
            session = requests.Session()
            session.headers.update(headers)
            
            response = session.get(url, timeout=20, verify=False, allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            if not self._is_valid_content(soup):
                return {'success': False, 'error': 'Content blocked with enhanced headers'}
            
            return self._parse_content(response.text, url)
            
        except Exception as e:
            return {'success': False, 'error': f'Enhanced headers failed: {str(e)}'}
    
    def _session_with_cookies_extract(self, url: str) -> Dict[str, Any]:
        """Session with persistent cookies and homepage visit"""
        try:
            session = requests.Session()
            headers = self._get_enhanced_headers(url)
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
            response = session.get(url, timeout=self.timeout, verify=False, allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            if not self._is_valid_content(soup):
                return {'success': False, 'error': 'Content blocked despite session'}
            
            return self._parse_content(response.text, url)
            
        except Exception as e:
            return {'success': False, 'error': f'Session extraction failed: {str(e)}'}
    
    def _social_referer_extract(self, url: str) -> Dict[str, Any]:
        """Extract with social media referer"""
        try:
            headers = self._get_enhanced_headers(url, strategy="social")
            response = requests.get(url, headers=headers, timeout=self.timeout, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            if not self._is_valid_content(soup):
                return {'success': False, 'error': 'Content blocked despite social referer'}
            
            return self._parse_content(response.text, url)
            
        except Exception as e:
            return {'success': False, 'error': f'Social referer failed: {str(e)}'}
    
    def _search_referer_extract(self, url: str) -> Dict[str, Any]:
        """Extract with search engine referer"""
        try:
            headers = self._get_enhanced_headers(url, strategy="search")
            response = requests.get(url, headers=headers, timeout=self.timeout, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            if not self._is_valid_content(soup):
                return {'success': False, 'error': 'Content blocked despite search referer'}
            
            return self._parse_content(response.text, url)
            
        except Exception as e:
            return {'success': False, 'error': f'Search referer failed: {str(e)}'}
    
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
    
    def _mobile_headers_extract(self, url: str) -> Dict[str, Any]:
        """Mobile user agent - sites are often less restrictive for mobile"""
        try:
            headers = self._get_enhanced_headers(url, strategy="mobile")
            response = requests.get(url, headers=headers, timeout=self.timeout, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            if not self._is_valid_content(soup):
                return {'success': False, 'error': 'Content blocked despite mobile headers'}
            
            return self._parse_content(response.text, url)
            
        except Exception as e:
            return {'success': False, 'error': f'Mobile headers failed: {str(e)}'}
    
    def _consent_cookies_extract(self, url: str) -> Dict[str, Any]:
        """Extract with common consent/bypass cookies"""
        try:
            session = requests.Session()
            headers = self._get_enhanced_headers(url)
            session.headers.update(headers)
            
            domain = urlparse(url).netloc
            
            # Enhanced consent cookies
            bypass_cookies = {
                'gdpr': '1',
                'consent': 'yes',
                'cookies_accepted': 'true',
                'age_verified': 'true',
                'cookie_consent': 'accepted',
                'privacy_consent': 'true',
                'euconsent-v2': 'accepted',
                '_sp_enable_dfp_personalized_ads': 'true',
                'cookieConsent': '1',
                'cookie-agreed': '2',
                'cookie_notice_accepted': 'true',
                'cookies-eu-agreed': 'true'
            }
            
            for name, value in bypass_cookies.items():
                session.cookies.set(name, value, domain=domain)
            
            time.sleep(random.uniform(1, 2))
            response = session.get(url, timeout=self.timeout, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            if not self._is_valid_content(soup):
                return {'success': False, 'error': 'Content blocked despite consent cookies'}
            
            return self._parse_content(response.text, url)
            
        except Exception as e:
            return {'success': False, 'error': f'Consent cookies failed: {str(e)}'}
    
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
            options.add_argument('--headless=new')
            
            driver = uc.Chrome(options=options)
            
            try:
                driver.set_page_load_timeout(self.browser_timeout)
                driver.get(url)
                
                # Wait for content to load with human-like behavior
                time.sleep(random.uniform(3, 7))
                
                # Scroll gradually to trigger lazy loading
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
                time.sleep(random.uniform(1, 2))
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight*2/3);")
                time.sleep(random.uniform(1, 2))
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(2, 3))
                
                html = driver.page_source
                
                soup = BeautifulSoup(html, 'html.parser')
                if not self._is_valid_content(soup):
                    return {'success': False, 'error': 'Content blocked in undetected Chrome'}
                
                return self._parse_content(html, url)
                
            finally:
                try:
                    driver.quit()
                except:
                    pass
                    
        except Exception as e:
            return {'success': False, 'error': f'Undetected Chrome failed: {str(e)}'}
    
    def _selenium_stealth_extract(self, url: str) -> Dict[str, Any]:
        """Enhanced Selenium with comprehensive stealth"""
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
            
            # Enhanced stealth options
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
            
            driver = webdriver.Chrome(options=options)
            
            try:
                # Execute comprehensive stealth script
                driver.execute_script("""
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                    Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                    Object.defineProperty(navigator, 'permissions', {get: () => undefined});
                    window.chrome = {runtime: {}};
                    Object.defineProperty(navigator, 'maxTouchPoints', {get: () => 1});
                """)
                
                driver.set_page_load_timeout(self.browser_timeout)
                driver.get(url)
                
                # Wait and scroll with human-like behavior
                time.sleep(random.uniform(3, 6))
                
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                time.sleep(2)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                html = driver.page_source
                
                soup = BeautifulSoup(html, 'html.parser')
                if not self._is_valid_content(soup):
                    return {'success': False, 'error': 'Content blocked in Selenium stealth'}
                
                return self._parse_content(html, url)
                
            finally:
                try:
                    driver.quit()
                except:
                    pass
                    
        except Exception as e:
            return {'success': False, 'error': f'Selenium stealth failed: {str(e)}'}
    
    def _playwright_stealth_extract(self, url: str) -> Dict[str, Any]:
        """Enhanced Playwright with comprehensive stealth"""
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
                    user_agent=random.choice(self.user_agents),
                    locale='en-US',
                    timezone_id='America/New_York'
                )
                
                # Comprehensive stealth scripts
                context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                    Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                    Object.defineProperty(navigator, 'permissions', {get: () => undefined});
                    window.chrome = {runtime: {}};
                    Object.defineProperty(navigator, 'maxTouchPoints', {get: () => 1});
                    delete navigator.__proto__.webdriver;
                """)
                
                page = context.new_page()
                
                # Handle common popups automatically
                page.on('dialog', lambda dialog: dialog.accept())
                
                try:
                    response = page.goto(url, timeout=self.browser_timeout * 1000, wait_until='domcontentloaded')
                    
                    if response and response.status >= 400:
                        return {'success': False, 'error': f'HTTP {response.status}'}
                    
                    # Wait for content with human-like behavior
                    page.wait_for_timeout(random.randint(3000, 6000))
                    
                    # Handle common overlays
                    try:
                        # Close common popup selectors
                        popup_selectors = [
                            '[data-testid="close-button"]',
                            '.close-button',
                            '.popup-close',
                            '.modal-close',
                            '.cookie-banner button'
                        ]
                        for selector in popup_selectors:
                            try:
                                page.click(selector, timeout=1000)
                                break
                            except:
                                continue
                    except:
                        pass
                    
                    # Scroll to load content
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
                    page.wait_for_timeout(2000)
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(2000)
                    
                    html = page.content()
                    
                    soup = BeautifulSoup(html, 'html.parser')
                    if not self._is_valid_content(soup):
                        return {'success': False, 'error': 'Content blocked in Playwright stealth'}
                    
                    return self._parse_content(html, url)
                    
                finally:
                    browser.close()
                    
        except Exception as e:
            return {'success': False, 'error': f'Playwright stealth failed: {str(e)}'}
    
    def _archive_fallback_extract(self, url: str) -> Dict[str, Any]:
        """Enhanced archive.org fallback"""
        try:
            archive_urls = [
                f"http://web.archive.org/web/{url}",
                f"https://archive.ph/{url}",
                f"https://webcache.googleusercontent.com/search?q=cache:{url}"
            ]
            
            headers = self._get_enhanced_headers()
            
            for archive_url in archive_urls:
                try:
                    response = requests.get(archive_url, headers=headers, timeout=20)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        if self._is_valid_content(soup):
                            return self._parse_content(response.text, url)
                except:
                    continue
            
            return {'success': False, 'error': 'No archived version found'}
                
        except Exception as e:
            return {'success': False, 'error': f'Archive fallback failed: {str(e)}'}
    
    # CONTENT PARSING METHODS
    
    def _parse_content(self, html: str, url: str = None) -> Dict[str, Any]:
        """Enhanced content parsing with multiple extraction strategies"""
        try:
            if not html or len(html) < 100:
                return {'success': False, 'error': 'HTML content too short'}
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'nav', 'aside', 'footer', 'header', 'advertisement']):
                element.decompose()
            
            # Extract content using multiple strategies
            content, extraction_metadata = self._extract_article_content_universal(soup, url)
            
            if not content or len(content.strip()) < self.min_content_length:
                return {'success': False, 'error': 'Could not extract sufficient article content'}
            
            # Extract metadata
            title = self._extract_title_universal(soup) or 'Untitled Article'
            author = self._extract_author_universal(soup)
            publish_date = self._extract_date_universal(soup)
            description = self._extract_description_universal(soup)
            image = self._extract_image_universal(soup, url) if url else None
            keywords = self._extract_keywords_universal(soup)
            
            # Clean and validate content
            content = self._clean_content_universal(content)
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
    
    def _extract_article_content_universal(self, soup: BeautifulSoup, url: str = None) -> Tuple[Optional[str], Dict[str, Any]]:
        """Universal content extraction with comprehensive strategies"""
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
        
        # Strategy 5: Content scoring
        content = self._extract_by_content_scoring(soup)
        if content and len(content.strip()) > self.min_content_length:
            metadata['extraction_method'] = 'content_scoring'
            return content, metadata
        
        # Strategy 6: Fallback to all paragraphs
        content = self._extract_all_paragraphs_filtered(soup)
        if content and len(content.strip()) > self.min_content_length:
            metadata['extraction_method'] = 'filtered_paragraphs'
            return content, metadata
        
        metadata['extraction_method'] = 'failed'
        return None, metadata
    
    def _extract_from_structured_data(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract from JSON-LD structured data"""
        try:
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, list):
                        data = data[0]
                    
                    # Look for article content
                    if data.get('@type') in ['Article', 'NewsArticle', 'BlogPosting']:
                        content = data.get('articleBody') or data.get('text')
                        if content and len(content.strip()) > 100:
                            return content
                except:
                    continue
        except:
            pass
        return None
    
    def _extract_from_article_tags(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract from HTML5 article tags"""
        try:
            articles = soup.find_all('article')
            for article in articles:
                paragraphs = article.find_all('p')
                if len(paragraphs) >= self.min_paragraphs:
                    content = '\n\n'.join(
                        p.get_text(strip=True) for p in paragraphs 
                        if len(p.get_text(strip=True).split()) >= self.min_words_per_paragraph
                    )
                    if len(content.strip()) > 100:
                        return content
        except:
            pass
        return None
    
    def _extract_from_main_containers(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract from common main content containers"""
        selectors = [
            'main', '[role="main"]', '.article-body', '.story-body', '.content', 
            '.post-content', '.entry-content', '.article-content', '.main-content',
            '#content', '#main-content', '.article-text', '.story-text'
        ]
        
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    paragraphs = element.find_all('p')
                    if len(paragraphs) >= self.min_paragraphs:
                        content = '\n\n'.join(
                            p.get_text(strip=True) for p in paragraphs 
                            if len(p.get_text(strip=True).split()) >= self.min_words_per_paragraph
                        )
                        if len(content.strip()) > 100:
                            return content
            except:
                continue
        
        return None
    
    def _extract_by_paragraph_density(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract by finding areas with high paragraph density"""
        try:
            all_paragraphs = soup.find_all('p')
            if len(all_paragraphs) < self.min_paragraphs:
                return None
            
            # Score paragraphs by their content quality
            scored_paragraphs = []
            for p in all_paragraphs:
                text = p.get_text(strip=True)
                if len(text.split()) >= self.min_words_per_paragraph:
                    score = len(text.split())  # Basic scoring by word count
                    scored_paragraphs.append((score, text))
            
            # Take the top paragraphs
            scored_paragraphs.sort(reverse=True)
            top_paragraphs = scored_paragraphs[:min(20, len(scored_paragraphs))]
            
            if len(top_paragraphs) >= self.min_paragraphs:
                content = '\n\n'.join(p[1] for p in top_paragraphs)
                return content
                
        except:
            pass
        return None
    
    def _extract_by_content_scoring(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract by scoring content blocks"""
        try:
            # Find all text-containing elements
            text_elements = soup.find_all(['p', 'div', 'section'])
            
            scored_elements = []
            for element in text_elements:
                text = element.get_text(strip=True)
                if len(text.split()) >= 10:  # Minimum viable content
                    # Score based on text length and structure
                    score = len(text.split())
                    
                    # Bonus for article-like classes
                    classes = ' '.join(element.get('class', []))
                    if any(indicator in classes.lower() for indicator in ['article', 'content', 'story', 'post']):
                        score *= 1.5
                    
                    scored_elements.append((score, text))
            
            if scored_elements:
                scored_elements.sort(reverse=True)
                # Take top elements that form a coherent article
                top_content = []
                total_words = 0
                
                for score, text in scored_elements:
                    if total_words + len(text.split()) < 2000:  # Don't exceed reasonable length
                        top_content.append(text)
                        total_words += len(text.split())
                    if len(top_content) >= 10 or total_words > 500:
                        break
                
                if len(top_content) >= 2:
                    return '\n\n'.join(top_content)
                    
        except:
            pass
        return None
    
    def _extract_all_paragraphs_filtered(self, soup: BeautifulSoup) -> Optional[str]:
        """Fallback: extract all paragraphs with filtering"""
        try:
            all_paragraphs = soup.find_all('p')
            valid_paragraphs = []
            
            for p in all_paragraphs:
                text = p.get_text(strip=True)
                words = text.split()
                
                # Filter out likely navigation, ads, etc.
                if (len(words) >= 10 and 
                    not any(skip in text.lower() for skip in ['cookie', 'subscribe', 'advertisement', 'click here', 'read more']) and
                    len(text) < 1000):  # Not too long (likely not spam)
                    
                    valid_paragraphs.append(text)
            
            if len(valid_paragraphs) >= 2:
                return '\n\n'.join(valid_paragraphs[:15])  # Limit to first 15 good paragraphs
                
        except:
            pass
        return None
    
    def _extract_title_universal(self, soup: BeautifulSoup) -> Optional[str]:
        """Universal title extraction"""
        strategies = [
            lambda: soup.find('meta', property='og:title')['content'],
            lambda: soup.find('meta', {'name': 'twitter:title'})['content'],
            lambda: soup.find('h1').get_text(strip=True),
            lambda: soup.find('title').get_text(strip=True),
            lambda: soup.select_one('.article-title, .post-title, .story-title').get_text(strip=True)
        ]
        
        for strategy in strategies:
            try:
                title = strategy()
                if title and len(title.strip()) > 3:
                    # Clean title
                    title = re.sub(r'\s+', ' ', title.strip())
                    if len(title) < 200:  # Reasonable title length
                        return title
            except:
                continue
        
        return None
    
    def _extract_author_universal(self, soup: BeautifulSoup) -> Optional[str]:
        """Universal author extraction"""
        strategies = [
            lambda: soup.find('meta', {'name': 'author'})['content'],
            lambda: soup.find('meta', property='article:author')['content'],
            lambda: soup.select_one('.author, .byline, [rel="author"]').get_text(strip=True),
            lambda: soup.find('span', class_=re.compile(r'author', re.I)).get_text(strip=True)
        ]
        
        for strategy in strategies:
            try:
                author = strategy()
                if author and len(author.strip()) > 2:
                    author = re.sub(r'^[Bb]y\s+', '', author.strip())
                    author = re.sub(r'\s+', ' ', author)
                    if len(author) < 100 and re.match(r"^[A-Za-z\s\-'.]+$", author):
                        return author
            except:
                continue
        
        return None
    
    def _extract_date_universal(self, soup: BeautifulSoup) -> Optional[str]:
        """Universal date extraction"""
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
    
    def _extract_description_universal(self, soup: BeautifulSoup) -> Optional[str]:
        """Universal description extraction"""
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
    
    def _extract_image_universal(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Universal image extraction"""
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
    
    def _extract_keywords_universal(self, soup: BeautifulSoup) -> List[str]:
        """Universal keywords extraction"""
        try:
            keywords_tag = soup.find('meta', {'name': 'keywords'})
            if keywords_tag and keywords_tag.get('content'):
                keywords = [k.strip() for k in keywords_tag['content'].split(',')]
                return [k for k in keywords if len(k) > 2]
        except:
            pass
        
        return []
    
    def _clean_content_universal(self, content: str) -> str:
        """Universal content cleaning"""
        if not content:
            return ""
        
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        
        # Remove common artifacts
        artifacts = [
            r'Share this article.*?(\n|$)',
            r'Read more:.*?(\n|$)', 
            r'Subscribe.*?(\n|$)',
            r'Advertisement\s*',
            r'Click here.*?(\n|$)',
            r'Continue reading.*?(\n|$)'
        ]
        
        for artifact in artifacts:
            content = re.sub(artifact, '', content, flags=re.I)
        
        return content.strip()
    
    def _create_user_friendly_error(self, url: str, domain: str, last_error: str) -> Dict[str, Any]:
        """Create user-friendly error message with actionable suggestions"""
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
    """Article extraction service with universal scraper capabilities"""
    
    def __init__(self):
        super().__init__('article_extractor')
        
        logger.info("=" * 60)
        logger.info("UniversalScraper ArticleExtractor.__init__() STARTING")
        logger.info(f"Service name: {self.service_name}")
        logger.info(f"Available libraries: {OPTIONAL_LIBRARIES}")
        logger.info("=" * 60)
        
        # Initialize universal scraper
        self._extractor = None
        
        try:
            self._extractor = UniversalScraper()
            logger.info("UniversalScraper initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize UniversalScraper: {e}")
            self._extractor = None
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Main analysis method using universal scraper"""
        logger.info("=" * 60)
        logger.info("UniversalScraper ArticleExtractor.analyze() CALLED")
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
                logger.info(f"Extracting from URL with Universal Scraper: {url}")
                
                result = None
                if self._extractor:
                    try:
                        result = self._extractor.extract_from_url(url)
                    except Exception as e:
                        logger.warning(f"Universal scraper failed: {e}")
                        result = None
                
                # Fallback to basic extraction if universal scraper failed
                if not result or not result.get('success'):
                    logger.warning("Universal scraper failed, trying basic fallback")
                    try:
                        result = self._basic_fallback_extract(url)
                    except Exception as e:
                        logger.error(f"Basic fallback also failed: {e}")
                        result = {'success': False, 'error': f'All extraction methods failed: {str(e)}'}
                
                if result and result.get('success'):
                    return {
                        'success': True,
                        'service': self.service_name,
                        'timestamp': datetime.now().isoformat(),
                        'data': {
                            'title': result.get('title'),
                            'text': result.get('text'),
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
                            'extraction_method': result.get('extraction_metadata', {}).get('successful_method', 'unknown'),
                            'methods_tried': result.get('extraction_metadata', {}).get('methods_tried', []),
                            'execution_time': result.get('extraction_metadata', {}).get('execution_time', 0),
                            'libraries_available': OPTIONAL_LIBRARIES,
                            'universal_scraper_available': self._extractor is not None
                        }
                    }
                else:
                    error_msg = result.get('error', 'Universal extraction failed') if result else 'No extraction result'
                    return self.get_error_result(error_msg)
                
            elif text:
                logger.info("Analyzing raw text input")
                result = self._extractor.extract_from_text(text) if self._extractor else None
                
                if not result:
                    # Simple text analysis fallback
                    lines = text.strip().split('\n')
                    title = lines[0][:100] if lines else 'Text Analysis'
                    word_count = len(text.split())
                    
                    result = {
                        'success': True,
                        'title': title,
                        'text': text,
                        'word_count': word_count,
                        'extraction_metadata': {'method': 'simple_text_analysis'}
                    }
                
                return {
                    'success': True,
                    'service': self.service_name,
                    'timestamp': datetime.now().isoformat(),
                    'data': result,
                    'metadata': {
                        'extraction_method': 'text_input',
                        'universal_scraper_available': self._extractor is not None
                    }
                }
            
        except Exception as e:
            logger.error(f"UniversalScraper ArticleExtractor.analyze failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _basic_fallback_extract(self, url: str) -> Dict[str, Any]:
        """Basic fallback extraction when universal scraper fails"""
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
                'html': response.text
            }
            
        except Exception as e:
            logger.error(f"Basic extraction fallback failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': f'Basic extraction failed: {str(e)}'
            }
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        info = super().get_service_info()
        info.update({
            'extraction_strategies': [
                'basic_requests',
                'enhanced_headers',
                'session_with_cookies',
                'social_referer',
                'search_referer',
                'cloudscraper',
                'curl_cffi_stealth',
                'mobile_headers',
                'consent_cookies',
                'undetected_chrome',
                'selenium_stealth',
                'playwright_stealth',
                'archive_fallback'
            ],
            'libraries_available': OPTIONAL_LIBRARIES,
            'supports_anti_bot_bypass': True,
            'supports_progressive_escalation': True,
            'supports_universal_scraping': True,
            'supports_live_news': True,
            'supports_text_input': True,
            'circuit_breaker_enabled': True,
            'success_rate_optimization': True
        })
        return info
