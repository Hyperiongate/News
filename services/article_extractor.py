"""
FILE: services/article_extractor.py
Enhanced article extractor with advanced scraping capabilities
Handles paywalls, CloudFlare, and JavaScript-rendered sites
"""

import os
import logging
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
from datetime import datetime
import json
from urllib.parse import urlparse
import time
import random
from fake_useragent import UserAgent

# Try to import advanced scraping libraries
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
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

logger = logging.getLogger(__name__)

class ArticleExtractor:
    """Enhanced article extractor with multiple fallback methods"""
    
    def __init__(self):
        self.timeout = 30
        self.delay_range = (1, 3)  # Increased delay
        self.ua = UserAgent()
        
        # Browser-like session configuration
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=10,
            max_retries=3
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        # Initialize cloudscraper if available
        if CLOUDSCRAPER_AVAILABLE:
            self.cloudscraper_session = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'desktop': True
                }
            )
            
        logger.info(f"ArticleExtractor initialized (CloudScraper: {CLOUDSCRAPER_AVAILABLE}, Curl-CFFI: {CURL_CFFI_AVAILABLE}, Selenium: {SELENIUM_AVAILABLE}, Playwright: {PLAYWRIGHT_AVAILABLE})")
    
    def _get_headers(self, referer=None):
        """Get randomized headers that look like a real browser"""
        headers = {
            'User-Agent': self.ua.chrome,  # Use Chrome UA specifically
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
            'Sec-Ch-Ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Cache-Control': 'max-age=0'
        }
        
        if referer:
            headers['Referer'] = referer
            headers['Sec-Fetch-Site'] = 'same-origin'
            
        return headers
    
    def _delay(self):
        """Random delay to avoid rate limiting"""
        time.sleep(random.uniform(*self.delay_range))
    
    def extract_from_url(self, url: str) -> Dict[str, Any]:
        """
        Extract article content from URL using multiple methods
        
        Returns:
            Dict containing article data or error information
        """
        logger.info(f"Extracting article from: {url}")
        
        # Parse domain for special handling
        domain = urlparse(url).netloc.lower()
        
        # Try methods in order of sophistication
        methods = [
            ("enhanced requests", self._extract_with_enhanced_requests),
            ("cloudscraper", self._extract_with_cloudscraper),
            ("curl-cffi", self._extract_with_curl_cffi),
            ("requests with cookies", self._extract_with_cookies),
        ]
        
        # Add browser-based methods if available
        if SELENIUM_AVAILABLE:
            methods.append(("selenium", self._extract_with_selenium))
        if PLAYWRIGHT_AVAILABLE:
            methods.append(("playwright", self._extract_with_playwright))
            
        # Add final fallback
        methods.append(("proxy rotation", self._extract_with_proxy))
        
        last_error = None
        for method_name, method_func in methods:
            try:
                logger.info(f"Trying {method_name}...")
                content = method_func(url)
                if content and len(content) > 1000:
                    logger.info(f"Success with {method_name}")
                    return self._parse_article(content, url)
            except Exception as e:
                logger.warning(f"{method_name} failed: {str(e)}")
                last_error = str(e)
                continue
        
        # All methods failed
        error_msg = f"All extraction methods failed. Last error: {last_error}"
        logger.error(error_msg)
        return {
            'success': False,
            'error': error_msg,
            'url': url
        }
    
    def _extract_with_enhanced_requests(self, url: str) -> Optional[str]:
        """Enhanced requests with better headers and cookie handling"""
        self._delay()
        
        # First make a request to get cookies
        domain = urlparse(url).netloc
        homepage = f"https://{domain}"
        
        # Visit homepage first to get cookies
        try:
            self.session.get(homepage, headers=self._get_headers(), timeout=10)
        except:
            pass  # Continue anyway
        
        # Now make the actual request with cookies
        headers = self._get_headers(referer=homepage)
        response = self.session.get(
            url, 
            headers=headers, 
            timeout=self.timeout, 
            allow_redirects=True,
            stream=True
        )
        response.raise_for_status()
        
        content = response.text
        if len(content) < 1000 or "blocked" in content.lower() or "captcha" in content.lower():
            raise Exception("Likely blocked or captcha page")
            
        return content
    
    def _extract_with_cloudscraper(self, url: str) -> Optional[str]:
        """CloudScraper method with enhanced options"""
        if not CLOUDSCRAPER_AVAILABLE:
            raise Exception("CloudScraper not available")
            
        self._delay()
        
        # Create a new scraper instance with specific browser
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True,
                'mobile': False
            },
            delay=10,  # CloudFlare delay
            debug=False
        )
        
        response = scraper.get(url, timeout=self.timeout)
        response.raise_for_status()
        
        content = response.text
        if len(content) < 1000:
            raise Exception("Response too short, likely blocked")
            
        return content
    
    def _extract_with_curl_cffi(self, url: str) -> Optional[str]:
        """Curl-CFFI with multiple browser impersonations"""
        if not CURL_CFFI_AVAILABLE:
            raise Exception("Curl-CFFI not available")
            
        self._delay()
        
        # Try different browser impersonations
        browsers = ['chrome120', 'chrome119', 'chrome110', 'edge101', 'safari17_0']
        
        for browser in browsers:
            try:
                response = curl_requests.get(
                    url, 
                    impersonate=browser,
                    headers=self._get_headers(),
                    timeout=self.timeout,
                    allow_redirects=True
                )
                
                if response.status_code == 200 and len(response.text) > 1000:
                    return response.text
            except:
                continue
                
        raise Exception("All browser impersonations failed")
    
    def _extract_with_cookies(self, url: str) -> Optional[str]:
        """Try with cookie manipulation"""
        self._delay()
        
        # Create session with specific cookies that might help
        session = requests.Session()
        
        # Common cookies that might help bypass
        cookies = {
            'CONSENT': 'YES+',
            'euConsent': 'true',
            'cookieConsent': 'true',
            '__cf_bm': str(int(time.time())),
            'sessionid': str(random.randint(1000000, 9999999))
        }
        
        for name, value in cookies.items():
            session.cookies.set(name, value)
        
        headers = self._get_headers()
        headers.update({
            'Cookie': '; '.join([f'{k}={v}' for k, v in cookies.items()])
        })
        
        response = session.get(url, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        
        if len(response.text) < 1000:
            raise Exception("Response too short")
            
        return response.text
    
    def _extract_with_selenium(self, url: str) -> Optional[str]:
        """Selenium-based extraction for JavaScript-heavy sites"""
        if not SELENIUM_AVAILABLE:
            raise Exception("Selenium not available")
            
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument(f'user-agent={self.ua.chrome}')
        
        # Additional options to avoid detection
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = None
        try:
            driver = webdriver.Chrome(options=options)
            
            # Execute script to mask automation
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            driver.get(url)
            
            # Wait for content to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
            )
            
            # Scroll to trigger lazy loading
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            return driver.page_source
            
        finally:
            if driver:
                driver.quit()
    
    def _extract_with_playwright(self, url: str) -> Optional[str]:
        """Playwright-based extraction"""
        if not PLAYWRIGHT_AVAILABLE:
            raise Exception("Playwright not available")
            
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=self.ua.chrome,
                viewport={'width': 1920, 'height': 1080},
                locale='en-US'
            )
            
            # Add extra headers
            context.set_extra_http_headers(self._get_headers())
            
            page = context.new_page()
            
            # Navigate and wait
            page.goto(url, wait_until='networkidle')
            
            # Scroll to load lazy content
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)
            
            content = page.content()
            browser.close()
            
            return content
    
    def _extract_with_proxy(self, url: str) -> Optional[str]:
        """Last resort: try with proxy"""
        self._delay()
        
        # This is a placeholder - in production you'd use actual proxy services
        # For now, just try one more time with different headers
        headers = self._get_headers()
        headers.update({
            'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'X-Real-IP': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'X-Originating-IP': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        })
        
        response = requests.get(url, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        
        return response.text
    
    def _parse_article(self, html_content: str, url: str) -> Dict[str, Any]:
        """Parse article content from HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract metadata
            article_data = {
                'url': url,
                'domain': urlparse(url).netloc,
                'extracted_at': datetime.now().isoformat(),
                'success': True
            }
            
            # Title extraction (multiple strategies)
            title = None
            # Try meta property first
            if not title:
                meta_title = soup.find('meta', property='og:title')
                if meta_title:
                    title = meta_title.get('content', '').strip()
            # Try regular title tag
            if not title:
                title_tag = soup.find('title')
                if title_tag:
                    title = title_tag.get_text().strip()
            # Try h1
            if not title:
                h1 = soup.find('h1')
                if h1:
                    title = h1.get_text().strip()
            
            article_data['title'] = title or 'Untitled'
            
            # Author extraction
            author = self._extract_author(soup)
            article_data['author'] = author
            
            # Date extraction
            publish_date = self._extract_date(soup)
            article_data['publish_date'] = publish_date
            
            # Content extraction with domain-specific selectors
            content = self._extract_content_smart(soup, url)
            article_data['text'] = content
            article_data['word_count'] = len(content.split()) if content else 0
            
            # Description/Summary
            description = None
            meta_desc = soup.find('meta', {'name': 'description'}) or soup.find('meta', property='og:description')
            if meta_desc:
                description = meta_desc.get('content', '').strip()
            article_data['description'] = description
            
            # Image
            image = None
            meta_image = soup.find('meta', property='og:image')
            if meta_image:
                image = meta_image.get('content')
            article_data['image'] = image
            
            # Keywords
            keywords = []
            meta_keywords = soup.find('meta', {'name': 'keywords'})
            if meta_keywords:
                keywords = [k.strip() for k in meta_keywords.get('content', '').split(',')]
            article_data['keywords'] = keywords
            
            return article_data
            
        except Exception as e:
            logger.error(f"Error parsing article: {e}")
            return {
                'success': False,
                'error': f'Parsing error: {str(e)}',
                'url': url
            }
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author with multiple strategies"""
        author = None
        
        # Try JSON-LD first
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if 'author' in data:
                        if isinstance(data['author'], dict):
                            author = data['author'].get('name')
                        elif isinstance(data['author'], str):
                            author = data['author']
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and 'author' in item:
                            if isinstance(item['author'], dict):
                                author = item['author'].get('name')
                            elif isinstance(item['author'], str):
                                author = item['author']
                if author:
                    break
            except:
                continue
        
        # Try meta tags
        if not author:
            meta_author = soup.find('meta', {'name': 'author'}) or soup.find('meta', property='article:author')
            if meta_author:
                author = meta_author.get('content')
        
        # Try byline patterns
        if not author:
            byline_patterns = [
                {'class': ['byline', 'by-line', 'author', 'writer', 'journalist', 'author-name', 'by']},
                {'itemprop': 'author'},
                {'rel': 'author'},
                {'data-testid': 'author-name'},
                {'class': re.compile(r'author|byline', re.I)}
            ]
            
            for pattern in byline_patterns:
                element = soup.find(['span', 'div', 'p', 'a'], pattern)
                if element:
                    text = element.get_text().strip()
                    # Clean common prefixes
                    for prefix in ['By', 'by', 'BY', 'Written by', 'Author:', 'By:']:
                        if text.startswith(prefix):
                            text = text[len(prefix):].strip()
                    if text and len(text) < 100:  # Sanity check
                        author = text
                        break
        
        return author
    
    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract publish date"""
        date_str = None
        
        # Try meta tags first
        date_meta_names = [
            'article:published_time',
            'datePublished',
            'pubdate',
            'publishdate',
            'date',
            'DC.date.issued',
            'publish_date',
            'publication_date',
            'article:published',
            'article:modified_time'
        ]
        
        for name in date_meta_names:
            meta = soup.find('meta', {'property': name}) or soup.find('meta', {'name': name})
            if meta and meta.get('content'):
                date_str = meta.get('content')
                break
        
        # Try time tag
        if not date_str:
            time_tag = soup.find('time')
            if time_tag:
                date_str = time_tag.get('datetime') or time_tag.get_text()
        
        # Try common date patterns in text
        if not date_str:
            date_patterns = [
                {'class': re.compile(r'date|time|published', re.I)},
                {'itemprop': 'datePublished'},
                {'datetime': True}
            ]
            
            for pattern in date_patterns:
                element = soup.find(['time', 'span', 'div'], pattern)
                if element:
                    date_str = element.get('datetime') or element.get_text().strip()
                    break
        
        return date_str
    
    def _extract_content_smart(self, soup: BeautifulSoup, url: str) -> str:
        """Extract content with domain-specific selectors"""
        # Remove script and style elements
        for script in soup(["script", "style", "noscript", "iframe"]):
            script.decompose()
        
        # Domain-specific selectors
        domain = urlparse(url).netloc.lower()
        domain_selectors = {
            'thehill.com': [
                {'class': 'article__text'},
                {'class': 'content-wrp'},
                {'id': 'article-text'}
            ],
            'axios.com': [
                {'class': 'story-body'},
                {'class': 'content-body'}
            ],
            'reuters.com': [
                {'class': 'article-body'},
                {'data-testid': 'article-body'}
            ]
        }
        
        # Try domain-specific selectors first
        if any(d in domain for d in domain_selectors):
            for site, selectors in domain_selectors.items():
                if site in domain:
                    for selector in selectors:
                        content = soup.find('div', selector)
                        if content:
                            text = content.get_text(separator=' ', strip=True)
                            if len(text) > 500:
                                return text
        
        # Try general content candidates
        content_candidates = [
            soup.find('div', {'class': 'article-body'}),
            soup.find('div', {'class': 'article-content'}),
            soup.find('div', {'class': 'entry-content'}),
            soup.find('div', {'class': 'post-content'}),
            soup.find('div', {'class': 'story-body'}),
            soup.find('article'),
            soup.find('main'),
            soup.find('div', {'id': 'article-body'}),
            soup.find('div', {'class': 'content'}),
            soup.find('div', {'itemprop': 'articleBody'}),
            soup.find('div', {'class': re.compile(r'article|content|body|text', re.I)})
        ]
        
        # Find the best content container
        best_content = None
        max_length = 0
        
        for candidate in content_candidates:
            if candidate:
                # Get text from paragraphs within the container
                paragraphs = candidate.find_all('p')
                if paragraphs:
                    text = ' '.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30])
                else:
                    text = candidate.get_text(separator=' ', strip=True)
                    
                if len(text) > max_length:
                    max_length = len(text)
                    best_content = text
        
        # Fallback: get all paragraphs
        if not best_content or max_length < 500:
            paragraphs = soup.find_all('p')
            if paragraphs:
                all_text = ' '.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50])
                if len(all_text) > max_length:
                    best_content = all_text
        
        return best_content or "Could not extract article content"
    
    def extract_from_text(self, text: str) -> Dict[str, Any]:
        """Extract data from raw text (for API compatibility)"""
        return {
            'success': True,
            'title': 'Text Analysis',
            'text': text,
            'author': None,
            'publish_date': datetime.now().isoformat(),
            'url': None,
            'domain': 'text-input',
            'word_count': len(text.split())
        }
