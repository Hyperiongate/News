"""
Article Extraction Service (Complete Fixed Version)
Multi-method article extraction with correct response format
"""
import logging
import time
import random
import re
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import threading
import requests
from bs4 import BeautifulSoup

from services.base_analyzer import BaseAnalyzer

# Optional imports with availability checks
try:
    from fake_useragent import UserAgent
    USER_AGENT_AVAILABLE = True
except ImportError:
    USER_AGENT_AVAILABLE = False
    logging.warning("fake_useragent not available, using static user agents")

try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False
    logging.info("CloudScraper not available")

try:
    from curl_cffi import requests as curl_requests
    CURL_CFFI_AVAILABLE = True
except ImportError:
    CURL_CFFI_AVAILABLE = False
    logging.info("curl-cffi not available")

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logging.info("Selenium not available")

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.info("Playwright not available")

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Circuit breaker for handling failed domains"""
    
    def __init__(self, failure_threshold=3, timeout_duration=300):
        self.failure_threshold = failure_threshold
        self.timeout_duration = timeout_duration
        self.failed_domains = {}
        self._lock = threading.Lock()
    
    def is_blocked(self, domain: str) -> bool:
        with self._lock:
            if domain in self.failed_domains:
                failure_data = self.failed_domains[domain]
                if failure_data['count'] >= self.failure_threshold:
                    time_since_failure = (datetime.now() - failure_data['last_attempt']).total_seconds()
                    if time_since_failure < self.timeout_duration:
                        return True
                    else:
                        self.failed_domains[domain] = {'count': 0, 'last_attempt': None, 'last_error': None}
            return False
    
    def record_failure(self, domain: str, error: str = None):
        with self._lock:
            if domain not in self.failed_domains:
                self.failed_domains[domain] = {'count': 0, 'last_attempt': None, 'last_error': None}
            self.failed_domains[domain]['count'] += 1
            self.failed_domains[domain]['last_attempt'] = datetime.now()
            self.failed_domains[domain]['last_error'] = error
    
    def record_success(self, domain: str):
        with self._lock:
            if domain in self.failed_domains:
                del self.failed_domains[domain]
    
    def get_last_error(self, domain: str) -> Optional[str]:
        with self._lock:
            if domain in self.failed_domains:
                return self.failed_domains[domain].get('last_error')
        return None


class ContentExtractor:
    """Intelligent content extraction using text density and pattern analysis"""
    
    def __init__(self):
        # Common non-content indicators
        self.non_content_patterns = [
            r'sign\s*in', r'log\s*in', r'subscribe', r'newsletter', r'cookie', 
            r'privacy\s*policy', r'terms\s*of\s*service', r'advertisement',
            r'please\s*enable\s*javascript', r'your\s*browser', r'supported\s*browser',
            r'©\s*\d{4}', r'all\s*rights\s*reserved', r'follow\s*us', r'share\s*this'
        ]
        
        # Paywall indicators
        self.paywall_patterns = [
            r'subscribe\s*to\s*read', r'continue\s*reading', r'already\s*a\s*subscriber',
            r'unlimited\s*access', r'free\s*trial', r'paywall', r'premium\s*content',
            r'members?\s*only', r'exclusive\s*content', r'sign\s*up\s*to\s*read'
        ]
        
        # Minimum thresholds
        self.min_paragraphs = 2
        self.min_words_per_paragraph = 10
        self.min_total_words = 50
    
    def extract_content(self, soup: BeautifulSoup) -> Tuple[Optional[str], Dict[str, Any]]:
        """Extract article content from BeautifulSoup object"""
        metadata = {
            'extraction_method': 'unknown',
            'content_indicators': [],
            'issues': []
        }
        
        # Try multiple extraction strategies
        strategies = [
            ('article_tag', self._extract_by_article_tag),
            ('schema_org', self._extract_by_schema),
            ('main_content', self._extract_by_main_content),
            ('density_analysis', self._extract_by_density),
            ('paragraph_clustering', self._extract_by_paragraph_clustering)
        ]
        
        for strategy_name, strategy_func in strategies:
            try:
                content = strategy_func(soup)
                if content and self._validate_content(content):
                    metadata['extraction_method'] = strategy_name
                    logger.info(f"Content extracted successfully using {strategy_name}")
                    return content, metadata
            except Exception as e:
                logger.debug(f"Strategy {strategy_name} failed: {e}")
                metadata['issues'].append(f"{strategy_name}: {str(e)}")
        
        # Check for paywall
        if self._detect_paywall(soup):
            metadata['issues'].append('paywall_detected')
            metadata['paywall'] = True
            logger.warning("Paywall detected")
        
        logger.warning("All content extraction strategies failed")
        return None, metadata
    
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
    
    def _extract_by_schema(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract content from schema.org structured data"""
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if data.get('@type') in ['NewsArticle', 'Article', 'BlogPosting']:
                        if 'articleBody' in data:
                            return data['articleBody']
                elif isinstance(data, list):
                    for item in data:
                        if item.get('@type') in ['NewsArticle', 'Article', 'BlogPosting']:
                            if 'articleBody' in item:
                                return item['articleBody']
            except:
                continue
        return None
    
    def _extract_by_main_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract from common main content containers"""
        main_selectors = [
            'main',
            '[role="main"]',
            '.main-content',
            '#main-content',
            '.article-content',
            '.post-content',
            '.entry-content',
            '.content-body'
        ]
        
        for selector in main_selectors:
            container = soup.select_one(selector)
            if container:
                paragraphs = container.find_all('p')
                if len(paragraphs) >= self.min_paragraphs:
                    text = '\n\n'.join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True).split()) >= self.min_words_per_paragraph)
                    if text:
                        return text
        
        return None
    
    def _extract_by_density(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract content based on text density analysis"""
        # Calculate text density for all div elements
        densities = []
        for div in soup.find_all('div'):
            text = div.get_text(strip=True)
            if len(text) < 100:
                continue
            
            # Calculate link density
            links_text = sum(len(a.get_text(strip=True)) for a in div.find_all('a'))
            link_density = links_text / len(text) if text else 1
            
            if link_density < 0.3:  # Low link density indicates content
                densities.append((len(text), text, div))
        
        # Get the longest low-link-density text
        if densities:
            densities.sort(reverse=True)
            return densities[0][1]
        
        return None
    
    def _extract_by_paragraph_clustering(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract content by finding clusters of paragraphs"""
        all_paragraphs = soup.find_all('p')
        
        # Filter and cluster paragraphs
        clusters = []
        current_cluster = []
        
        for p in all_paragraphs:
            text = p.get_text(strip=True)
            word_count = len(text.split())
            
            if word_count >= self.min_words_per_paragraph:
                current_cluster.append(text)
            elif current_cluster and len(current_cluster) >= self.min_paragraphs:
                clusters.append('\n\n'.join(current_cluster))
                current_cluster = []
        
        # Add final cluster
        if current_cluster and len(current_cluster) >= self.min_paragraphs:
            clusters.append('\n\n'.join(current_cluster))
        
        # Return longest cluster
        if clusters:
            return max(clusters, key=len)
        
        return None
    
    def _detect_paywall(self, soup: BeautifulSoup) -> bool:
        """Detect if content is behind a paywall"""
        page_text = soup.get_text().lower()
        for pattern in self.paywall_patterns:
            if re.search(pattern, page_text, re.IGNORECASE):
                return True
        return False
    
    def _validate_content(self, content: str) -> bool:
        """Validate extracted content"""
        if not content:
            return False
        
        # Check minimum length
        word_count = len(content.split())
        if word_count < self.min_total_words:
            return False
        
        # Check for non-content patterns
        content_lower = content.lower()
        non_content_count = sum(1 for pattern in self.non_content_patterns if re.search(pattern, content_lower))
        if non_content_count > 3:
            return False
        
        # Check structure
        sentences = re.split(r'[.!?]+', content)
        valid_sentences = [s for s in sentences if 5 <= len(s.split()) <= 50]
        if len(valid_sentences) < 2:
            return False
        
        return True


class LegacyArticleExtractor:
    """Universal article extractor that works with any site"""
    
    def __init__(self):
        # Timeout configuration
        self.quick_timeout = 10
        self.browser_timeout = 20
        self.total_timeout = 60
        self.delay_range = (0.5, 2)
        
        # User agent handling
        if USER_AGENT_AVAILABLE:
            try:
                self.ua = UserAgent()
            except:
                self.ua = None
        else:
            self.ua = None
        
        self.circuit_breaker = CircuitBreaker()
        
        # Initialize content extractor
        self.content_extractor = ContentExtractor()
        
        # Thread pool for timeout control
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Browser-like session configuration with default headers
        self.session = requests.Session()
        
        # Set default headers for the session
        self.session.headers.update(self._get_headers())
        
        # Configure retries and connection pooling
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=10,
            max_retries=requests.adapters.Retry(
                total=2,
                backoff_factor=0.3,
                status_forcelist=[500, 502, 503, 504]
            )
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        # Initialize cloudscraper if available
        if CLOUDSCRAPER_AVAILABLE:
            try:
                self.cloudscraper_session = cloudscraper.create_scraper(
                    browser={
                        'browser': 'chrome',
                        'platform': 'windows',
                        'desktop': True
                    }
                )
                # Set default headers for cloudscraper too
                self.cloudscraper_session.headers.update(self._get_headers())
            except:
                self.cloudscraper_session = None
        else:
            self.cloudscraper_session = None
            
        logger.info(f"ArticleExtractor initialized (CloudScraper: {CLOUDSCRAPER_AVAILABLE}, "
                   f"Curl-CFFI: {CURL_CFFI_AVAILABLE}, Selenium: {SELENIUM_AVAILABLE}, "
                   f"Playwright: {PLAYWRIGHT_AVAILABLE})")
    
    def _get_headers(self, referer=None):
        """Get randomized headers that look like a real browser"""
        # More diverse and recent user agents
        static_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        ]
        
        if self.ua:
            try:
                user_agent = self.ua.random
            except:
                user_agent = random.choice(static_agents)
        else:
            user_agent = random.choice(static_agents)
        
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
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
            'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
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
        
        # Parse domain for circuit breaker
        domain = urlparse(url).netloc
        
        # Check circuit breaker
        if self.circuit_breaker.is_blocked(domain):
            last_error = self.circuit_breaker.get_last_error(domain)
            logger.warning(f"Domain {domain} is circuit-broken. Last error: {last_error}")
            return {
                'success': False,
                'error': f'Domain temporarily blocked due to repeated failures: {last_error}',
                'extraction_metadata': {
                    'circuit_breaker': True,
                    'domain': domain
                }
            }
        
        # Try extraction methods in order
        methods = [
            ('quick_extract', self._quick_extract),
            ('cloudscraper_extract', self._cloudscraper_extract) if self.cloudscraper_session else None,
            ('curl_extract', self._curl_extract) if CURL_CFFI_AVAILABLE else None,
            ('selenium_extract', self._selenium_extract) if SELENIUM_AVAILABLE else None,
            ('playwright_extract', self._playwright_extract) if PLAYWRIGHT_AVAILABLE else None
        ]
        
        # Filter out None methods
        methods = [m for m in methods if m is not None]
        
        last_error = None
        for method_name, method_func in methods:
            if time.time() - start_time > self.total_timeout:
                logger.warning(f"Total timeout reached for {url}")
                break
            
            try:
                logger.info(f"Trying {method_name} for {url}")
                
                # Use thread pool for timeout control
                future = self.executor.submit(method_func, url)
                try:
                    result = future.result(timeout=self.browser_timeout if 'browser' in method_name else self.quick_timeout)
                    
                    if result and result.get('success'):
                        result['extraction_metadata'] = {
                            'method': method_name,
                            'duration': time.time() - start_time,
                            'attempts': methods.index((method_name, method_func)) + 1
                        }
                        self.circuit_breaker.record_success(domain)
                        logger.info(f"Successfully extracted content using {method_name}")
                        return result
                    else:
                        logger.warning(f"{method_name} failed: {result.get('error', 'Unknown error')}")
                        last_error = result.get('error', f"{method_name} failed")
                    
                except FutureTimeoutError:
                    logger.warning(f"{method_name} timed out for {url}")
                    last_error = f"{method_name} timeout"
                    continue
                    
            except Exception as e:
                logger.error(f"{method_name} failed for {url}: {str(e)}", exc_info=True)
                last_error = str(e)
                continue
            
            # Small delay between attempts
            if method_func != methods[-1][1]:
                time.sleep(random.uniform(*self.delay_range))
        
        # Record failure
        self.circuit_breaker.record_failure(domain, last_error)
        
        logger.error(f"All extraction methods failed for {url}. Last error: {last_error}")
        return {
            'success': False,
            'error': f'All extraction methods failed. Last error: {last_error}',
            'extraction_metadata': {
                'duration': time.time() - start_time,
                'methods_tried': len(methods),
                'domain': domain
            }
        }
    
    def _quick_extract(self, url: str) -> Dict[str, Any]:
        """Quick extraction using requests and BeautifulSoup"""
        try:
            # Create a new session for this request with fresh headers
            headers = self._get_headers(referer=url)
            
            # Add additional headers that might help with 403 errors
            headers.update({
                'Pragma': 'no-cache',
                'Sec-Ch-Ua-Platform-Version': '"10.0.0"',
                'Sec-Ch-Ua-Full-Version': '"121.0.6167.85"',
                'Sec-Ch-Ua-Arch': '"x86"',
                'Sec-Ch-Ua-Bitness': '"64"',
                'Sec-Ch-Ua-Model': '""',
                'Sec-Ch-Ua-Full-Version-List': '"Not A(Brand";v="99.0.0.0", "Google Chrome";v="121.0.6167.85", "Chromium";v="121.0.6167.85"'
            })
            
            # Make request with all headers
            response = self.session.get(
                url, 
                headers=headers, 
                timeout=self.quick_timeout,
                allow_redirects=True,
                verify=True
            )
            
            # Check for specific error codes
            if response.status_code == 403:
                logger.error(f"Quick extract got 403 for {url}, will try other methods")
                return {'success': False, 'error': f'403 Forbidden'}
            
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                return {'success': False, 'error': f'Non-HTML content type: {content_type}'}
            
            soup = BeautifulSoup(response.text, 'html.parser')
            return self._parse_content(soup, url)
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                logger.error(f"Quick extract failed with 403 for {url}")
                return {'success': False, 'error': '403 Forbidden'}
            logger.error(f"Quick extract HTTP error for {url}: {e}")
            return {'success': False, 'error': str(e)}
        except requests.RequestException as e:
            logger.error(f"Quick extract failed for {url}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _cloudscraper_extract(self, url: str) -> Dict[str, Any]:
        """Extract using cloudscraper for Cloudflare protection"""
        if not self.cloudscraper_session:
            return {'success': False, 'error': 'CloudScraper not available'}
        
        try:
            # Update headers for this specific request
            headers = self._get_headers(referer=url)
            
            # Make request with headers
            response = self.cloudscraper_session.get(
                url, 
                headers=headers,
                timeout=self.quick_timeout,
                allow_redirects=True
            )
            
            # Check for specific error codes
            if response.status_code == 403:
                logger.error(f"CloudScraper extract got 403 for {url}")
                return {'success': False, 'error': '403 Forbidden'}
            
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            return self._parse_content(soup, url)
            
        except Exception as e:
            logger.error(f"CloudScraper extract failed for {url}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _curl_extract(self, url: str) -> Dict[str, Any]:
        """Extract using curl-cffi for better compatibility"""
        try:
            # curl-cffi with Chrome impersonation often bypasses 403 errors
            response = curl_requests.get(
                url,
                impersonate="chrome110",
                timeout=self.quick_timeout,
                allow_redirects=True,
                verify=True
            )
            
            if response.status_code == 403:
                # Try with different impersonation
                response = curl_requests.get(
                    url,
                    impersonate="safari15_5",
                    timeout=self.quick_timeout,
                    allow_redirects=True,
                    verify=True
                )
            
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            return self._parse_content(soup, url)
            
        except Exception as e:
            logger.error(f"Curl extract failed for {url}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _selenium_extract(self, url: str) -> Dict[str, Any]:
        """Extract using Selenium for JavaScript-heavy sites"""
        driver = None
        try:
            options = ChromeOptions()
            options.add_argument('--headless=new')  # Use new headless mode
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Set user agent
            user_agent = self._get_headers()["User-Agent"]
            options.add_argument(f'user-agent={user_agent}')
            
            driver = webdriver.Chrome(options=options)
            
            # Execute CDP commands to mask automation
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            
            driver.set_page_load_timeout(self.browser_timeout)
            
            driver.get(url)
            
            # Wait for content to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "p"))
            )
            
            # Additional wait for dynamic content
            time.sleep(2)
            
            # Get page source
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            return self._parse_content(soup, url)
            
        except Exception as e:
            logger.error(f"Selenium extract failed for {url}: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def _playwright_extract(self, url: str) -> Dict[str, Any]:
        """Extract using Playwright for modern JavaScript sites"""
        try:
            with sync_playwright() as p:
                # Launch with more realistic settings
                browser = p.chromium.launch(
                    headless=True,
                    args=['--disable-blink-features=AutomationControlled']
                )
                
                # Create context with realistic viewport and user agent
                context = browser.new_context(
                    user_agent=self._get_headers()['User-Agent'],
                    viewport={'width': 1920, 'height': 1080},
                    locale='en-US',
                    timezone_id='America/Los_Angeles'
                )
                
                # Add scripts to avoid detection
                context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                """)
                
                page = context.new_page()
                
                # Navigate with realistic behavior
                page.goto(url, wait_until='domcontentloaded', timeout=self.browser_timeout * 1000)
                
                # Wait for content
                page.wait_for_selector('p', timeout=10000)
                
                # Additional wait for dynamic content
                page.wait_for_timeout(2000)
                
                content = page.content()
                browser.close()
                
                soup = BeautifulSoup(content, 'html.parser')
                return self._parse_content(soup, url)
                
        except Exception as e:
            logger.error(f"Playwright extract failed for {url}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _parse_content(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Parse content from BeautifulSoup object"""
        try:
            # Extract metadata
            title = self._extract_title(soup)
            author = self._extract_author(soup)
            publish_date = self._extract_date(soup)
            description = self._extract_description(soup)
            image = self._extract_image(soup, url)
            keywords = self._extract_keywords(soup)
            
            # Extract main content
            content, extraction_metadata = self.content_extractor.extract_content(soup)
            
            if not content:
                logger.warning(f"Could not extract article content from {url}")
                return {
                    'success': False,
                    'error': 'Could not extract article content',
                    'extraction_metadata': extraction_metadata
                }
            
            # Clean and validate content
            content = self._clean_content(content)
            word_count = len(content.split())
            
            logger.info(f"Successfully parsed content from {url}: {word_count} words")
            
            return {
                'success': True,
                'title': title,
                'text': content,
                'author': author,
                'publish_date': publish_date,
                'url': url,
                'domain': urlparse(url).netloc,
                'description': description,
                'image': image,
                'keywords': keywords,
                'word_count': word_count,
                'extracted_at': datetime.now().isoformat(),
                'extraction_metadata': extraction_metadata
            }
            
        except Exception as e:
            logger.error(f"Content parsing failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': f'Content parsing error: {str(e)}'
            }
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article title"""
        # Try multiple strategies
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
        """Extract article author"""
        strategies = [
            lambda: soup.find('meta', {'name': 'author'})['content'],
            lambda: soup.find('meta', property='article:author')['content'],
            lambda: soup.find('span', {'class': re.compile(r'author|byline', re.I)}).get_text(strip=True),
            lambda: soup.find('div', {'class': re.compile(r'author|byline', re.I)}).get_text(strip=True),
        ]
        
        for strategy in strategies:
            try:
                author = strategy()
                if author:
                    # Clean up author name
                    author = re.sub(r'^by\s+', '', author, flags=re.I)
                    return author.strip()
            except:
                continue
        
        return None
    
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
        # For raw text, we don't need extraction, just analysis
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
    
    def __del__(self):
        """Cleanup thread pool on deletion"""
        try:
            self.executor.shutdown(wait=False)
        except:
            pass


# ============= NEW REFACTORED CLASS =============

class ArticleExtractor(BaseAnalyzer):
    """Article extraction service that inherits from BaseAnalyzer"""
    
    def __init__(self):
        logger.info("=" * 60)
        logger.info("ArticleExtractor.__init__() STARTING")
        logger.info("=" * 60)
        
        super().__init__('article_extractor')
        
        logger.info(f"ArticleExtractor after super().__init__: is_available={self.is_available}")
        
        try:
            self._legacy = LegacyArticleExtractor()
            logger.info("ArticleExtractor initialized successfully with legacy extractor")
        except Exception as e:
            logger.error(f"Failed to initialize LegacyArticleExtractor: {e}")
            self._legacy = None
            logger.warning("ArticleExtractor will use basic extraction fallback")
        
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
            'error': f'Analysis timed out after {self.config.timeout}s',
            'timeout': True,
            'timestamp': time.time()
        }
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract article content using the standardized interface
        
        Expected input:
            - url: URL to extract article from
            OR
            - text: Raw text to analyze
            OR
            - content: URL or text (for backward compatibility)
            - content_type: 'url' or 'text' (for backward compatibility)
            
        Returns:
            Standardized service response with article data in 'data' field
        """
        logger.info("=" * 60)
        logger.info("ArticleExtractor.analyze() CALLED")
        logger.info("=" * 60)
        
        try:
            # Log the incoming data for debugging
            logger.info(f"ArticleExtractor.analyze called with data keys: {list(data.keys())}")
            logger.info(f"Full data received: {data}")
            
            # Handle different input formats for compatibility
            url = data.get('url')
            text = data.get('text')
            
            # Support legacy format from pipeline
            if not url and not text:
                content = data.get('content')
                content_type = data.get('content_type', 'url')
                logger.info(f"Using legacy format - content: {content}, content_type: {content_type}")
                if content_type == 'url':
                    url = content
                else:
                    text = content
            
            # Log what we're extracting
            if url:
                logger.info(f"Extracting from URL: {url}")
            elif text:
                logger.info(f"Extracting from text input: {len(text)} characters")
            else:
                logger.error("No URL or text provided for extraction")
            
            # Check what type of extraction is needed
            if url:
                result = self._extract_from_url(url)
                logger.info(f"Extraction result: success={result.get('success')}, has_error={bool(result.get('error'))}")
                return result
            elif text:
                result = self._extract_from_text(text)
                logger.info(f"Text extraction result: success={result.get('success')}")
                return result
            else:
                error_msg = "Missing required field: 'url' or 'text'"
                logger.error(error_msg)
                result = self.get_error_result(error_msg)
                logger.info(f"Returning error result: {result}")
                return result
                
        except Exception as e:
            logger.error(f"ArticleExtractor.analyze failed with unexpected error: {e}", exc_info=True)
            result = self.get_error_result(f"Unexpected error: {str(e)}")
            logger.info(f"Returning exception result: {result}")
            return result
    
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
                    'url': None,
                    'domain': result.get('domain', 'text-input'),
                    'word_count': result.get('word_count', len(text.split())),
                    'source': 'text_input'
                },
                'metadata': {
                    'input_type': 'text'
                }
            }
            
            logger.info("Text extraction completed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Article extraction from text failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _basic_url_extraction(self, url: str) -> Dict[str, Any]:
        """Basic URL extraction fallback"""
        try:
            logger.info(f"Attempting basic URL extraction for {url}")
            
            # More robust headers for basic extraction
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
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
            }
            
            response = requests.get(url, timeout=10, headers=headers, allow_redirects=True)
            
            if response.status_code == 403:
                logger.error(f"Got 403 Forbidden for {url}")
                return {
                    'success': False,
                    'error': '403 Forbidden - Access denied by website'
                }
            
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
