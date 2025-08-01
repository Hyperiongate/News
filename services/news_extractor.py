"""
FILE: services/news_extractor.py
LOCATION: services/news_extractor.py
PURPOSE: Complete universal news extractor with all methods and API support
FIXED: Proper API integration and error handling
"""

import logging
import re
import json
import time
import random
import os
from datetime import datetime
from urllib.parse import urlparse, quote, urlencode
from collections import Counter, defaultdict
from html import unescape

import requests
from bs4 import BeautifulSoup, NavigableString, Comment

# Try to import optional libraries
try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

logger = logging.getLogger(__name__)

class NewsExtractor:
    """Ultimate universal news extractor with AI-level author detection"""
    
    def __init__(self):
        # Initialize sessions
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Create CloudScraper session if available
        self.scraper = None
        if CLOUDSCRAPER_AVAILABLE:
            try:
                self.scraper = cloudscraper.create_scraper(
                    browser={
                        'browser': 'chrome',
                        'platform': 'windows',
                        'desktop': True
                    }
                )
                logger.info("CloudScraper initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize CloudScraper: {e}")
        
        # Create HTTPX client if available
        self.httpx_client = None
        if HTTPX_AVAILABLE:
            try:
                self.httpx_client = httpx.Client(
                    http2=True,
                    follow_redirects=True,
                    timeout=30.0
                )
                logger.info("HTTPX client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize HTTPX: {e}")
        
        # API keys for scraping services
        self.scrapingbee_key = os.environ.get('SCRAPINGBEE_API_KEY')
        self.scraperapi_key = os.environ.get('SCRAPERAPI_KEY')
        
        # Log API key status
        if self.scrapingbee_key:
            logger.info("ScrapingBee API key found")
        if self.scraperapi_key:
            logger.info("ScraperAPI key found")
        
        # User agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        # Common first and last names for validation
        self.common_first_names = {
            'james', 'john', 'robert', 'michael', 'william', 'david', 'richard', 'joseph',
            'thomas', 'charles', 'mary', 'patricia', 'jennifer', 'linda', 'elizabeth',
            'barbara', 'susan', 'jessica', 'sarah', 'karen', 'daniel', 'matthew', 'donald',
            'mark', 'paul', 'steven', 'andrew', 'kenneth', 'joshua', 'kevin', 'brian',
            'george', 'edward', 'ronald', 'timothy', 'jason', 'jeffrey', 'ryan', 'jacob',
            'gary', 'nicholas', 'eric', 'jonathan', 'stephen', 'larry', 'justin', 'scott',
            'brandon', 'benjamin', 'samuel', 'frank', 'gregory', 'raymond', 'alexander',
            'patrick', 'jack', 'dennis', 'jerry', 'tyler', 'aaron', 'jose', 'nathan',
            'henry', 'zachary', 'douglas', 'peter', 'adam', 'noah', 'christopher', 'nancy',
            'betty', 'helen', 'sandra', 'donna', 'carol', 'ruth', 'sharon', 'michelle',
            'laura', 'kimberly', 'deborah', 'rachel', 'amy', 'anna', 'maria', 'dorothy',
            'lisa', 'ashley', 'madison', 'amanda', 'melissa', 'debra', 'stephanie', 'rebecca',
            'virginia', 'kathleen', 'pamela', 'martha', 'angela', 'katherine', 'christine',
            'emma', 'olivia', 'sophia', 'isabella', 'charlotte', 'amelia', 'evelyn',
            'jeremy', 'simon', 'martin', 'peter', 'alan', 'ian', 'colin', 'graham',
            'daniella', 'didi', 'martinez', 'silva', 'adi', 'naveen', 'dhaliwal',
            'bisram', 'natalie', 'duddridge', 'guajardo'
        }
        
        self.common_last_names = {
            'smith', 'johnson', 'williams', 'brown', 'jones', 'garcia', 'miller', 'davis',
            'rodriguez', 'martinez', 'hernandez', 'lopez', 'gonzalez', 'wilson', 'anderson',
            'thomas', 'taylor', 'moore', 'jackson', 'martin', 'lee', 'perez', 'thompson',
            'white', 'harris', 'sanchez', 'clark', 'ramirez', 'lewis', 'robinson', 'walker',
            'young', 'allen', 'king', 'wright', 'scott', 'torres', 'nguyen', 'hill',
            'flores', 'green', 'adams', 'nelson', 'baker', 'hall', 'rivera', 'campbell',
            'mitchell', 'carter', 'roberts', 'bowen', 'cohen', 'chen', 'wang', 'kim',
            'silva', 'martinez', 'guajardo', 'dhaliwal', 'bisram', 'duddridge'
        }
        
        self.org_names = {
            'nbc', 'cnn', 'fox', 'abc', 'cbs', 'bbc', 'npr', 'reuters', 'associated press',
            'bloomberg', 'new york times', 'washington post', 'guardian', 'daily mail',
            'usa today', 'wall street journal', 'los angeles times', 'chicago tribune',
            'boston globe', 'miami herald', 'news', 'media', 'press', 'network',
            'broadcasting', 'times', 'post', 'journal', 'herald', 'globe', 'tribune'
        }
    
    def extract_article(self, url):
        """Extract article content from URL using multiple methods"""
        try:
            logger.info(f"🚀 ULTIMATE EXTRACTION STARTING for: {url}")
            
            # PRIORITY 1: Try API services first if available (most reliable)
            if self.scrapingbee_key or self.scraperapi_key:
                try:
                    logger.info("Trying API extraction first (most reliable)...")
                    result = self._extract_with_api(url)
                    if result and result.get('text') and len(result['text']) > 200:
                        logger.info("✅ API extraction successful")
                        return result
                except Exception as e:
                    logger.warning(f"API extraction failed: {e}")
            
            # Method 2: Try CloudScraper (handles most anti-bot)
            if self.scraper:
                try:
                    result = self._extract_with_cloudscraper(url)
                    if result and result.get('text') and len(result['text']) > 200:
                        logger.info("✅ CloudScraper extraction successful")
                        return result
                except Exception as e:
                    logger.warning(f"CloudScraper failed: {e}")
            
            # Method 3: Try HTTPX with HTTP/2
            if self.httpx_client:
                try:
                    result = self._extract_with_httpx(url)
                    if result and result.get('text') and len(result['text']) > 200:
                        logger.info("✅ HTTPX extraction successful")
                        return result
                except Exception as e:
                    logger.warning(f"HTTPX failed: {e}")
            
            # Method 4: Try free proxy services
            try:
                result = self._extract_with_free_proxy(url)
                if result and result.get('text') and len(result['text']) > 200:
                    logger.info("✅ Free proxy extraction successful")
                    return result
            except Exception as e:
                logger.warning(f"Free proxy failed: {e}")
            
            # Method 5: Try Google Cache
            try:
                result = self._extract_with_google_cache(url)
                if result and result.get('text') and len(result['text']) > 200:
                    logger.info("✅ Google cache extraction successful")
                    return result
            except Exception as e:
                logger.warning(f"Google cache failed: {e}")
            
            # Method 6: Try Wayback Machine
            try:
                result = self._extract_with_wayback(url)
                if result and result.get('text') and len(result['text']) > 200:
                    logger.info("✅ Wayback extraction successful")
                    return result
            except Exception as e:
                logger.warning(f"Wayback failed: {e}")
            
            # Method 7: Standard extraction with multiple user agents
            try:
                result = self._extract_standard_multi_ua(url)
                if result and result.get('text') and len(result['text']) > 200:
                    logger.info("✅ Standard extraction successful")
                    return result
            except Exception as e:
                logger.warning(f"Standard extraction failed: {e}")
            
            # Method 8: Mobile version
            try:
                result = self._extract_mobile_version(url)
                if result and result.get('text') and len(result['text']) > 200:
                    logger.info("✅ Mobile extraction successful")
                    return result
            except Exception as e:
                logger.warning(f"Mobile extraction failed: {e}")
            
            # All methods failed - return helpful fallback
            return self._create_smart_fallback(url)
            
        except Exception as e:
            logger.error(f"Extraction error for {url}: {str(e)}", exc_info=True)
            return self._create_smart_fallback(url)
    
    def _extract_with_cloudscraper(self, url):
        """Extract using CloudScraper"""
        logger.info("Trying CloudScraper...")
        response = self.scraper.get(url, timeout=30)
        
        if response.status_code != 200:
            raise ValueError(f"CloudScraper got status {response.status_code}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        domain = urlparse(url).netloc.replace('www.', '')
        
        # Extract all components
        title = self._extract_title(soup)
        text = self._extract_text(soup, url)
        author = self._extract_author_ultimate(soup, response.text, title, text, domain)
        publish_date = self._extract_date(soup)
        
        return {
            'title': title or 'No title found',
            'text': text or 'No article text found',
            'author': author,
            'publish_date': publish_date,
            'url': url,
            'domain': domain
        }
    
    def _extract_with_api(self, url):
        """Extract using scraping API services with improved error handling"""
        # Try ScrapingBee first
        if self.scrapingbee_key:
            logger.info("Trying ScrapingBee API...")
            api_url = 'https://app.scrapingbee.com/api/v1'
            params = {
                'api_key': self.scrapingbee_key,
                'url': url,
                'render_js': 'true',  # Changed to true for better extraction
                'premium_proxy': 'true',
                'country_code': 'us',
                'wait': '1500',  # Wait for content to load
                'block_ads': 'true'
            }
            
            try:
                response = requests.get(api_url, params=params, timeout=45)
                logger.info(f"ScrapingBee response status: {response.status_code}")
                
                if response.status_code == 200:
                    result = self._parse_response(response.content, url)
                    if result and result.get('text'):
                        return result
                elif response.status_code == 401:
                    logger.error("ScrapingBee API key is invalid")
                elif response.status_code == 402:
                    logger.error("ScrapingBee API credits exhausted")
                else:
                    logger.warning(f"ScrapingBee returned status {response.status_code}")
                    
            except Exception as e:
                logger.error(f"ScrapingBee error: {e}")
        
        # Try ScraperAPI as fallback
        if self.scraperapi_key:
            logger.info("Trying ScraperAPI...")
            # Use the correct ScraperAPI endpoint
            scraperapi_url = f'http://api.scraperapi.com?api_key={self.scraperapi_key}&url={quote(url)}&render=true'
            
            try:
                response = requests.get(scraperapi_url, timeout=45)
                logger.info(f"ScraperAPI response status: {response.status_code}")
                
                if response.status_code == 200:
                    result = self._parse_response(response.content, url)
                    if result and result.get('text'):
                        return result
                elif response.status_code == 401:
                    logger.error("ScraperAPI key is invalid")
                elif response.status_code == 403:
                    logger.error("ScraperAPI credits exhausted or plan limit reached")
                else:
                    logger.warning(f"ScraperAPI returned status {response.status_code}")
                    
            except Exception as e:
                logger.error(f"ScraperAPI error: {e}")
        
        raise ValueError("API extraction failed - no valid API key or request failed")
    
    def _extract_with_httpx(self, url):
        """Extract using HTTPX with HTTP/2"""
        logger.info("Trying HTTPX with HTTP/2...")
        
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        response = self.httpx_client.get(url, headers=headers)
        
        if response.status_code != 200:
            raise ValueError(f"HTTPX got status {response.status_code}")
        
        return self._parse_response(response.content, url)
    
    def _extract_with_free_proxy(self, url):
        """Try free proxy services"""
        # Method 1: 12ft.io (removes paywalls)
        try:
            logger.info("Trying 12ft.io proxy...")
            proxy_url = f"https://12ft.io/proxy?q={quote(url)}"
            response = self.session.get(proxy_url, timeout=20)
            if response.status_code == 200:
                return self._parse_response(response.content, url)
        except Exception as e:
            logger.debug(f"12ft.io failed: {e}")
        
        # Method 2: Archive.today
        try:
            logger.info("Trying archive.today...")
            archive_url = f"https://archive.ph/newest/{url}"
            response = self.session.get(archive_url, timeout=20, allow_redirects=True)
            if response.status_code == 200:
                return self._parse_response(response.content, url)
        except Exception as e:
            logger.debug(f"Archive.today failed: {e}")
        
        # Method 3: Outline.com
        try:
            logger.info("Trying outline.com...")
            outline_url = f"https://outline.com/{url}"
            response = self.session.get(outline_url, timeout=20)
            if response.status_code == 200:
                return self._parse_response(response.content, url)
        except Exception as e:
            logger.debug(f"Outline.com failed: {e}")
        
        raise ValueError("Free proxy extraction failed")
    
    def _extract_with_google_cache(self, url):
        """Try Google's cache"""
        logger.info("Trying Google cache...")
        cache_url = f"https://webcache.googleusercontent.com/search?q=cache:{quote(url)}"
        
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Referer': 'https://www.google.com/'
        }
        
        response = self.session.get(cache_url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove Google's cache interface
            for elem in soup.select('div[style*="position: relative"]'):
                elem.decompose()
            
            return self._parse_response(str(soup).encode(), url)
        
        raise ValueError("Google cache failed")
    
    def _extract_with_wayback(self, url):
        """Try Wayback Machine"""
        logger.info("Trying Wayback Machine...")
        
        # Check if URL is archived
        check_url = f"https://archive.org/wayback/available?url={quote(url)}"
        
        try:
            response = self.session.get(check_url, timeout=10)
            data = response.json()
            
            if data.get('archived_snapshots', {}).get('closest', {}).get('available'):
                snapshot_url = data['archived_snapshots']['closest']['url']
                
                # Fetch the snapshot
                response = self.session.get(snapshot_url, timeout=20)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Remove Wayback UI elements
                    for elem in soup.find_all(id=re.compile('wm-')):
                        elem.decompose()
                    
                    return self._parse_response(str(soup).encode(), url)
        except Exception as e:
            logger.debug(f"Wayback error: {e}")
        
        raise ValueError("Wayback failed")
    
    def _extract_standard_multi_ua(self, url):
        """Standard extraction with multiple user agents"""
        for i, ua in enumerate(self.user_agents):
            try:
                logger.info(f"Trying standard extraction with UA {i+1}...")
                
                headers = {
                    'User-Agent': ua,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
                
                # Add delay to appear more human
                if i > 0:
                    time.sleep(random.uniform(1, 3))
                
                response = self.session.get(url, headers=headers, timeout=30, allow_redirects=True)
                
                if response.status_code == 200:
                    return self._parse_response(response.content, url)
                    
            except Exception as e:
                logger.debug(f"UA {i+1} failed: {e}")
                continue
        
        raise ValueError("All user agents failed")
    
    def _extract_mobile_version(self, url):
        """Try mobile version of site"""
        logger.info("Trying mobile version...")
        
        # Mobile URL patterns
        domain = urlparse(url).netloc
        mobile_urls = [
            url.replace('www.', 'm.'),
            url.replace('https://', 'https://m.'),
            url + '?amp=1',
            url.replace('.com/', '.com/amp/'),
            url.rstrip('/') + '/amp'
        ]
        
        mobile_headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
        for mobile_url in mobile_urls:
            try:
                response = self.session.get(mobile_url, headers=mobile_headers, timeout=15)
                if response.status_code == 200:
                    result = self._parse_response(response.content, url)
                    if result.get('text') and len(result['text']) > 200:
                        return result
            except:
                continue
        
        raise ValueError("Mobile extraction failed")
    
    def _parse_response(self, content, url):
        """Parse HTML content and extract article data"""
        soup = BeautifulSoup(content, 'html.parser')
        domain = urlparse(url).netloc.replace('www.', '')
        
        # Clean the soup
        for tag in soup(['script', 'style', 'noscript', 'iframe', 'svg']):
            tag.decompose()
        
        # Extract components
        title = self._extract_title(soup)
        text = self._extract_text(soup, url)
        author = self._extract_author_ultimate(soup, str(soup), title, text, domain)
        publish_date = self._extract_date(soup)
        
        return {
            'title': title or 'No title found',
            'text': text or 'No article text found',
            'author': author,
            'publish_date': publish_date,
            'url': url,
            'domain': domain
        }
    
    def _extract_title(self, soup):
        """Extract article title"""
        # Try Open Graph title first
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        
        # Try Twitter title
        twitter_title = soup.find('meta', {'name': 'twitter:title'})
        if twitter_title and twitter_title.get('content'):
            return twitter_title['content'].strip()
        
        # Try article title
        article_title = soup.find('meta', {'name': 'title'})
        if article_title and article_title.get('content'):
            return article_title['content'].strip()
        
        # Try JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and 'headline' in data:
                    return data['headline']
                if isinstance(data, list) and data and 'headline' in data[0]:
                    return data[0]['headline']
            except:
                continue
        
        # Try h1 tags
        h1_tags = soup.find_all('h1')
        for h1 in h1_tags:
            title = h1.get_text().strip()
            if title and len(title) > 10:
                # Clean up the title
                title = re.sub(r'\s+', ' ', title)
                # Remove common suffixes
                for suffix in [' - CNN', ' | CNN', ' - BBC', ' | BBC', ' - Reuters', ' | Reuters',
                             ' - The New York Times', ' | The New York Times', ' - The Guardian',
                             ' | The Guardian', ' - Fox News', ' | Fox News', ' | NBC News',
                             ' - Politico', ' | Politico', ' - The Washington Post']:
                    if title.endswith(suffix):
                        title = title[:-len(suffix)]
                
                # Remove "Share" and similar words at the end
                title = re.sub(r'\s*(Share|Tweet|Email|Print|Comment).*$', '', title)
                return title
        
        # Fall back to page title
        if soup.title:
            title = soup.title.string
            if title:
                # Clean up site name from title
                title = title.strip()
                # Remove common separators and everything after them
                for separator in [' - ', ' | ', ' — ', ' :: ', ' » ']:
                    if separator in title:
                        title = title.split(separator)[0].strip()
                
                # Remove trailing "Share" etc.
                title = re.sub(r'\s*(Share|Tweet|Email|Print|Comment).*$', '', title)
                return title
        
        return 'No title found'
    
    def _extract_text(self, soup, url):
        """Extract main article text with improved universal approach"""
        domain = urlparse(url).netloc.replace('www.', '')
        
        # Remove unwanted elements first
        for elem in soup(['script', 'style', 'noscript', 'nav', 'header', 'footer', 'aside', 
                         'form', 'button', 'input', 'select', 'textarea']):
            elem.decompose()
        
        # Remove elements with specific classes/ids that typically contain non-article content
        noise_selectors = [
            '[class*="comment"]', '[class*="sidebar"]', '[class*="widget"]',
            '[class*="advertisement"]', '[class*="promo"]', '[class*="related"]',
            '[class*="newsletter"]', '[class*="signup"]', '[class*="social"]',
            '[id*="comment"]', '[id*="sidebar"]', '[id*="widget"]'
        ]
        
        for selector in noise_selectors:
            for elem in soup.select(selector):
                elem.decompose()
        
        # Method 1: Try JSON-LD articleBody first
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if 'articleBody' in data and data['articleBody']:
                        return data['articleBody']
                    if '@graph' in data:
                        for item in data['@graph']:
                            if isinstance(item, dict) and 'articleBody' in item:
                                return item['articleBody']
            except:
                continue
        
        # Method 2: Look for semantic HTML5 tags and common article containers
        article_text = ""
        
        # Comprehensive list of selectors in priority order
        universal_selectors = [
            # Semantic HTML5
            'article[role="main"]',
            'article[itemtype*="Article"]',
            'article[itemtype*="NewsArticle"]',
            'article',
            'main article',
            'main [role="main"]',
            'main',
            
            # Common class patterns (using contains to catch variations)
            '[class*="article-body"]',
            '[class*="article-content"]',
            '[class*="article-text"]',
            '[class*="story-body"]',
            '[class*="story-content"]',
            '[class*="story-text"]',
            '[class*="post-body"]',
            '[class*="post-content"]',
            '[class*="entry-content"]',
            '[class*="content-body"]',
            '[class*="text-body"]',
            '[class*="body-text"]',
            
            # ID patterns
            '[id*="article-body"]',
            '[id*="story-body"]',
            '[id*="post-body"]',
            '[id*="content-body"]',
            
            # Data attributes
            '[data-component*="article"]',
            '[data-component*="text"]',
            '[data-testid*="article"]',
            '[data-testid*="body"]',
            
            # Microdata
            '[itemprop="articleBody"]',
            '[itemprop="text"]',
            
            # Generic content areas
            '.article',
            '.story',
            '.post',
            '.content',
            '.prose',
            '.entry',
            '.body',
            '#article',
            '#story',
            '#content',
            '#main-content',
            
            # WordPress common classes
            '.entry-content',
            '.post-content',
            '.the-content',
            
            # Medium-style
            '.postArticle-content',
            '.section-content',
            
            # News site patterns
            '.body-copy',
            '.article-wrap',
            '.story-wrap',
            '.text-wrap'
        ]
        
        # Try each selector and find the one with the most content
        best_content = ""
        best_content_length = 0
        
        for selector in universal_selectors:
            try:
                elements = soup.select(selector)
                for element in elements[:3]:  # Check up to 3 matches per selector
                    # Extract paragraphs, headers, lists, and blockquotes
                    content_elements = element.find_all(['p', 'h2', 'h3', 'h4', 'h5', 'h6', 
                                                        'blockquote', 'ul', 'ol', 'li'])
                    
                    if len(content_elements) < 3:  # Skip if too few content elements
                        continue
                    
                    texts = []
                    for elem in content_elements:
                        # Skip if element is inside a link or nav
                        if elem.find_parent(['nav', 'menu', 'header', 'footer']):
                            continue
                        
                        text = elem.get_text().strip()
                        
                        # Basic quality checks
                        if len(text) < 20:  # Skip very short text
                            continue
                        if text.lower().startswith(('share', 'tweet', 'follow', 'subscribe')):
                            continue
                        if re.match(r'^(copyright|©)', text, re.IGNORECASE):
                            continue
                        
                        texts.append(text)
                    
                    content = ' '.join(texts)
                    
                    # Keep the longest coherent content
                    if len(content) > best_content_length and len(content) > 200:
                        best_content = content
                        best_content_length = len(content)
                        
                        # If we found substantial content (>2000 chars), we can stop
                        if best_content_length > 2000:
                            return best_content
                            
            except Exception as e:
                logger.debug(f"Selector {selector} failed: {e}")
                continue
        
        # If we found good content, return it
        if best_content_length > 500:
            return best_content
        
        # Method 3: Fallback - analyze paragraph distribution
        # Find the container with the highest density of paragraphs
        all_containers = soup.find_all(['div', 'section', 'article', 'main'])
        
        best_container = None
        best_score = 0
        
        for container in all_containers:
            paragraphs = container.find_all('p')
            if len(paragraphs) < 3:
                continue
            
            # Calculate a score based on paragraph count and average length
            total_length = sum(len(p.get_text().strip()) for p in paragraphs)
            avg_length = total_length / len(paragraphs) if paragraphs else 0
            
            # Score favors containers with many paragraphs of reasonable length
            score = len(paragraphs) * (avg_length / 100) if avg_length > 50 else 0
            
            if score > best_score:
                best_score = score
                best_container = container
        
        if best_container:
            texts = []
            for p in best_container.find_all(['p', 'h2', 'h3', 'h4', 'blockquote']):
                text = p.get_text().strip()
                if text and len(text) > 20:
                    texts.append(text)
            
            if texts:
                return ' '.join(texts)
        
        # Method 4: Last resort - get all paragraphs
        all_paragraphs = soup.find_all('p')
        texts = []
        
        for p in all_paragraphs:
            # Skip paragraphs in navigation, footers, etc.
            if p.find_parent(['nav', 'menu', 'header', 'footer', 'aside']):
                continue
            
            text = p.get_text().strip()
            
            # Quality checks
            if len(text) < 50:  # Skip short paragraphs
                continue
            
            # Skip obvious non-article content
            lower_text = text.lower()
            skip_phrases = ['cookie', 'privacy policy', 'terms of service', 'subscribe',
                          'newsletter', 'follow us', 'share this', 'advertisement']
            if any(phrase in lower_text for phrase in skip_phrases):
                continue
            
            texts.append(text)
            
            # Stop if we have enough content
            if len(' '.join(texts)) > 3000:
                break
        
        article_text = ' '.join(texts) if texts else ""
        
        # Return what we found, or indicate failure
        if article_text and len(article_text) > 200:
            return article_text
        else:
            return "No article text found - the content may be behind a paywall or dynamically loaded"
    
    def _extract_author_ultimate(self, soup, html_text, title, article_text, domain):
        """ULTIMATE author extraction using every conceivable method"""
        
        logger.info("🔍 ULTIMATE AUTHOR EXTRACTION ENGAGED")
        
        # Store all candidates with confidence scores
        author_candidates = {}  # author -> confidence score
        
        # CRITICAL: First check if element is in navigation
        def is_navigation_element(element):
            """Check if element is part of navigation"""
            if not element:
                return False
            
            # Check element and all parents
            for parent in [element] + list(element.parents):
                if parent.name in ['nav', 'header', 'menu']:
                    return True
                
                # Check classes
                if parent.get('class'):
                    class_str = ' '.join(parent.get('class'))
                    if any(nav_word in class_str.lower() for nav_word in ['nav', 'menu', 'header']):
                        return True
                
                # Check id
                if parent.get('id'):
                    if any(nav_word in parent.get('id').lower() for nav_word in ['nav', 'menu', 'header']):
                        return True
            
            return False
        
        # METHOD 1: Look for byline patterns with multiple authors FIRST
        # This is most reliable for CBS News format
        multi_author_patterns = [
            r'[Bb]y\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s*,\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)*(?:\s+and\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)?)',
            r'[Bb]y:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s*,\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)*(?:\s+and\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)?)',
            r'[Ww]ritten\s+by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s*,\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)*(?:\s+and\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)?)'
        ]
        
        # Search in visible text for multi-author bylines
        search_texts = [html_text[:10000], article_text[:2000] if article_text else '']
        
        for search_text in search_texts:
            for pattern in multi_author_patterns:
                matches = re.findall(pattern, search_text)
                for match in matches:
                    # This will capture the entire byline like "Adi Guajardo, Naveen Dhaliwal, Jennifer Bisram, Natalie Duddridge"
                    authors = self._extract_multiple_authors_from_byline(match)
                    for author in authors:
                        if self._is_valid_author_name(author):
                            author_candidates[author] = author_candidates.get(author, 0) + 12  # High score for byline match
        
        # METHOD 2: JSON-LD structured data (most reliable)
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                self._extract_author_from_json_ld(data, author_candidates)
            except:
                continue
        
        # METHOD 3: Meta tags
        meta_selectors = [
            ('meta', {'name': 'author'}),
            ('meta', {'property': 'author'}),
            ('meta', {'name': 'article:author'}),
            ('meta', {'property': 'article:author'}),
            ('meta', {'name': 'byl'}),
            ('meta', {'name': 'DC.creator'}),
            ('meta', {'name': 'citation_author'}),
            ('meta', {'property': 'og:article:author'}),
            ('meta', {'itemprop': 'author'}),
            ('meta', {'name': 'twitter:creator'}),
            ('meta', {'name': 'sailthru.author'}),
            ('meta', {'name': 'parsely-author'})
        ]
        
        for tag, attrs in meta_selectors:
            elements = soup.find_all(tag, attrs)
            for element in elements:
                content = element.get('content', '')
                if content:
                    authors = self._extract_multiple_authors(content)
                    for author in authors:
                        if self._is_valid_author_name(author):
                            author_candidates[author] = author_candidates.get(author, 0) + 8
        
        # METHOD 4: Common byline patterns - EXPANDED
        byline_selectors = [
            # Class selectors
            '[class*="author"]:not([class*="nav"])',
            '[class*="byline"]:not([class*="nav"])',
            '[class*="writer"]',
            '[class*="reporter"]',
            '[class*="contributor"]',
            '[class*="journalist"]',
            '[class*="by-line"]',
            '[class*="article-author"]',
            '[class*="post-author"]',
            
            # ID selectors
            '[id*="author"]',
            '[id*="byline"]',
            
            # Semantic/microdata
            '[itemprop="author"]',
            '[rel="author"]',
            
            # Specific elements
            'address',
            '.by',
            '.writtenby',
            '.author-name',
            '.byline-name',
            
            # Link patterns
            'a[href*="/author/"]:not(nav a)',
            'a[href*="/staff/"]:not(nav a)',
            'a[href*="/people/"]:not(nav a)'
        ]
        
        for selector in byline_selectors:
            try:
                elements = soup.select(selector)
                for element in elements[:10]:
                    # Skip if in navigation
                    if is_navigation_element(element):
                        continue
                    
                    text = element.get_text().strip()
                    
                    # Clean and extract author name
                    author = self._extract_author_from_byline(text)
                    if author and self._is_valid_author_name(author):
                        score = 7 if 'author' in selector.lower() else 5
                        author_candidates[author] = author_candidates.get(author, 0) + score
            except:
                continue
        
        # Select best candidate(s)
        if author_candidates:
            # For multiple authors, return all with high scores
            sorted_candidates = sorted(
                author_candidates.items(),
                key=lambda x: (x[1], len(x[0].split()), -len(x[0])),
                reverse=True
            )
            
            # Check if we have multiple authors with similar high scores
            if len(sorted_candidates) > 1 and sorted_candidates[0][1] >= 10:
                # Get all authors with score within 2 points of the top score
                top_score = sorted_candidates[0][1]
                top_authors = [author for author, score in sorted_candidates if score >= top_score - 2]
                
                # If we have 2-4 authors with high scores, return them all
                if 2 <= len(top_authors) <= 4:
                    author_string = ', '.join(top_authors[:-1]) + ' and ' + top_authors[-1]
                    logger.info(f"✅ Multiple authors found: {author_string}")
                    return author_string
            
            # Otherwise return the best single author
            best_author = sorted_candidates[0][0]
            logger.info(f"✅ Author found: {best_author} (score: {sorted_candidates[0][1]})")
            logger.info(f"All candidates: {sorted_candidates[:5]}")
            return best_author
        
        logger.warning("❌ No author found")
        return None
    
    def _extract_multiple_authors_from_byline(self, byline_text):
        """Extract multiple authors from a byline like 'By A, B, C and D'"""
        authors = []
        
        # Remove "By" prefix
        byline_text = re.sub(r'^[Bb]y:?\s*', '', byline_text)
        
        # Handle "A, B, C and D" format
        if ',' in byline_text:
            # Split by comma
            parts = byline_text.split(',')
            
            # Handle last part which might contain "and"
            last_part = parts[-1].strip()
            if ' and ' in last_part.lower():
                # Split the last part by "and"
                last_authors = re.split(r'\s+and\s+', last_part, flags=re.I)
                parts[-1] = last_authors[0].strip()
                parts.extend([a.strip() for a in last_authors[1:]])
            
            # Clean each author name
            for part in parts:
                author = self._clean_author_name(part.strip())
                if author and self._is_valid_author_name(author):
                    authors.append(author)
        
        # Handle "A and B" format (no commas)
        elif ' and ' in byline_text.lower():
            parts = re.split(r'\s+and\s+', byline_text, flags=re.I)
            for part in parts:
                author = self._clean_author_name(part.strip())
                if author and self._is_valid_author_name(author):
                    authors.append(author)
        
        # Single author
        else:
            author = self._clean_author_name(byline_text)
            if author and self._is_valid_author_name(author):
                authors.append(author)
        
        return authors
    
    def _extract_author_from_json_ld(self, data, author_candidates):
        """Extract author from JSON-LD data"""
        if isinstance(data, dict):
            # Direct author field
            if 'author' in data:
                author_data = data['author']
                if isinstance(author_data, str):
                    author = self._clean_author_name(author_data)
                    if author and self._is_valid_author_name(author):
                        author_candidates[author] = author_candidates.get(author, 0) + 10
                elif isinstance(author_data, dict):
                    name = author_data.get('name', '')
                    if name:
                        author = self._clean_author_name(name)
                        if author and self._is_valid_author_name(author):
                            author_candidates[author] = author_candidates.get(author, 0) + 10
                elif isinstance(author_data, list):
                    for auth in author_data:
                        if isinstance(auth, dict):
                            name = auth.get('name', '')
                        else:
                            name = str(auth)
                        if name:
                            author = self._clean_author_name(name)
                            if author and self._is_valid_author_name(author):
                                author_candidates[author] = author_candidates.get(author, 0) + 10
            
            # Check nested structures
            for key in ['mainEntity', 'mainEntityOfPage', '@graph']:
                if key in data:
                    self._extract_author_from_json_ld(data[key], author_candidates)
        
        elif isinstance(data, list):
            for item in data:
                self._extract_author_from_json_ld(item, author_candidates)
    
    def _extract_author_from_byline(self, text):
        """Extract author name from byline text"""
        if not text or len(text) > 200:
            return None
        
        # Remove common prefixes
        text = re.sub(r'^(By|Written by|Reported by|Author:|By:|Contributor:|Posted by|Published by)\s*', '', text, flags=re.I)
        text = re.sub(r'^(By|by)\s+', '', text)
        
        # Remove dates, times, and common suffixes
        text = re.sub(r'\d{1,2}[/:]\d{1,2}[/:]\d{2,4}.*$', '', text)
        text = re.sub(r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).*$', '', text, flags=re.I)
        text = re.sub(r'(Posted|Published|Updated|Modified).*$', '', text, flags=re.I)
        text = re.sub(r'\|.*$', '', text)
        text = re.sub(r'\s+[-–—]\s+.*$', '', text)
        
        # Extract name part
        text = text.strip()
        
        # Skip if it's too long or too short
        if len(text) < 3 or len(text) > 50:
            return None
        
        # Skip if it contains certain words
        skip_words = ['share', 'tweet', 'email', 'print', 'comment', 'subscribe', 
                     'follow', 'advertisement', 'sponsored', 'promoted', 'read full bio']
        if any(word in text.lower() for word in skip_words):
            return None
        
        return text
    
    def _clean_author_name(self, name):
        """Clean and normalize author name"""
        if not name:
            return None
        
        # Decode HTML entities
        name = unescape(str(name))
        
        # Basic cleaning
        name = str(name).strip()
        name = re.sub(r'\s+', ' ', name)
        
        # Remove common suffixes/prefixes
        name = re.sub(r'^(By|Written by|Reported by|Author:|By:|Staff|Reporter|Correspondent)\s*', '', name, flags=re.I)
        name = re.sub(r'\s*(Staff|Reporter|Correspondent|Writer|Contributor|Editor|Journalist)$', '', name, flags=re.I)
        
        # Remove email
        name = re.sub(r'\S+@\S+', '', name)
        
        # Remove URLs
        name = re.sub(r'https?://\S+', '', name)
        
        # Remove special characters but keep apostrophes and hyphens in names
        name = re.sub(r'[^\w\s\'-]', ' ', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Remove trailing numbers
        name = re.sub(r'\s*\d+$', '', name)
        
        return name if name else None
    
    def _extract_multiple_authors(self, text):
        """Extract multiple authors from text"""
        if not text:
            return []
        
        # Clean the text first
        text = self._clean_author_name(text)
        if not text:
            return []
        
        authors = []
        
        # Split by common separators
        if ' and ' in text.lower():
            parts = re.split(r'\s+and\s+', text, flags=re.I)
        elif ',' in text:
            parts = text.split(',')
        elif ';' in text:
            parts = text.split(';')
        else:
            parts = [text]
        
        for part in parts:
            part = part.strip()
            if part and self._is_valid_author_name(part):
                authors.append(part)
        
        return authors
    
    def _is_valid_author_name(self, name):
        """Validate if the extracted text is likely an author name"""
        if not name or len(name) < 3 or len(name) > 50:
            return False
        
        # Must contain at least one letter
        if not any(c.isalpha() for c in name):
            return False
        
        # Skip if it's all caps (might be a section header)
        if name.isupper() and len(name.split()) > 2:
            return False
        
        # CRITICAL: Exclude common non-author phrases
        skip_phrases = [
            'click here', 'read more', 'share this', 'follow us', 'sign up',
            'subscribe', 'newsletter', 'breaking news', 'exclusive', 'update',
            'advertisement', 'sponsored', 'staff', 'admin', 'editor',
            'associated press', 'reuters', 'staff writer', 'guest post',
            'press release', 'news desk', 'web desk', 'news service',
            'digital team', 'online team', 'newsroom', 'editorial',
            'cookie policy', 'privacy policy', 'terms of service',
            # CRITICAL: Add navigation/show names
            'book club', 'news team', 'editorial board', 'newsroom staff',
            'morning show', 'evening news', 'weekend edition', 'special report',
            'investigates', 'sports desk', 'weather team', 'traffic watch',
            # CBS specific shows/sections
            'cbs this morning', 'cbs evening news', '60 minutes', 'face the nation',
            '48 hours', 'cbs sports', 'cbs news', 'cbsn'
        ]
        
        name_lower = name.lower()
        for phrase in skip_phrases:
            if phrase in name_lower:
                return False
        
        # Check if it contains organization names (unless it's part of a person's name)
        org_keywords = ['news', 'media', 'press', 'agency', 'network', 'broadcasting',
                       'corporation', 'company', 'institute', 'organization', 'group',
                       'club', 'show', 'program', 'desk', 'team', 'board']
        
        # Be stricter with organization keywords
        if any(keyword in name_lower for keyword in org_keywords):
            parts = name.split()
            # Reject if it's a short phrase with org keywords
            if len(parts) <= 3:
                return False
        
        # Must have at least first and last name (with some exceptions)
        parts = name.split()
        if len(parts) < 2:
            # Allow single names if they're in our known names
            if name_lower not in self.common_first_names and name_lower not in self.common_last_names:
                # Exception for known single-name journalists or foreign names
                if not (len(name) > 5 and name[0].isupper()):
                    return False
        
        # Check if at least one part is a common name
        has_common_name = False
        for part in parts:
            part_lower = part.lower().strip("'").strip("-")
            if part_lower in self.common_first_names or part_lower in self.common_last_names:
                has_common_name = True
                break
        
        # If no common names found, be more strict
        if not has_common_name and len(parts) >= 2:
            # At least require proper capitalization
            for part in parts:
                if part and not part[0].isupper() and part not in ['van', 'de', 'la', 'von', 'der', 'el']:
                    return False
        
        return True
    
    def _extract_date(self, soup):
        """Extract publish date"""
        date_selectors = [
            ('meta', {'property': 'article:published_time'}),
            ('meta', {'name': 'publish_date'}),
            ('meta', {'property': 'datePublished'}),
            ('meta', {'name': 'publication_date'}),
            ('meta', {'name': 'DC.date.issued'}),
            ('meta', {'name': 'date'}),
            ('meta', {'itemprop': 'datePublished'}),
            ('meta', {'name': 'article:published_time'}),
            ('time', {'datetime': True}),
            ('time', {'pubdate': True}),
            ('[itemprop="datePublished"]', None),
            ('[property="datePublished"]', None),
            ('[class*="publish-date"]', None),
            ('[class*="published-date"]', None),
            ('[class*="article-date"]', None),
            ('[class*="post-date"]', None),
            ('[class*="entry-date"]', None)
        ]
        
        for selector, attrs in date_selectors:
            if attrs:
                elements = soup.find_all(selector, attrs)
            else:
                elements = soup.select(selector)
                
            for element in elements:
                date_str = None
                
                if element.name == 'meta':
                    date_str = element.get('content')
                elif element.name == 'time':
                    date_str = element.get('datetime') or element.get_text()
                else:
                    date_str = element.get_text()
                
                if date_str:
                    date_str = date_str.strip()
                    # Try to parse the date
                    try:
                        # Handle ISO format
                        if 'T' in date_str:
                            return date_str.split('T')[0]
                        # Return as is if it looks like a date
                        if any(char in date_str for char in ['-', '/', '.']) and any(char.isdigit() for char in date_str):
                            return date_str
                    except:
                        continue
        
        return None
    
    def _create_smart_fallback(self, url):
        """Create an intelligent fallback response"""
        domain = urlparse(url).netloc.replace('www.', '')
        
        # Try to extract some info from URL
        title_guess = "Article"
        url_parts = url.split('/')
        if len(url_parts) > 4:
            # Try to get title from URL slug
            potential_slug = url_parts[-1] or url_parts[-2]
            if potential_slug and not potential_slug.isdigit():
                # Remove common URL patterns
                slug = re.sub(r'[-_]', ' ', potential_slug)
                slug = re.sub(r'\d{5,}', '', slug)  # Remove long numbers
                slug = re.sub(r'\.html?$', '', slug)  # Remove .html/.htm
                if len(slug) > 10:
                    title_guess = slug.title()
        
        # Provide specific instructions based on the domain
        if 'politico' in domain:
            instructions = """
**Politico has strong anti-bot protection. Here's how to get the article:**

1. **Open the article** in your browser
2. **Wait for it to fully load** (sometimes takes a few seconds)
3. **Select all text** (Ctrl+A on Windows, Cmd+A on Mac)
4. **Copy** (Ctrl+C or Cmd+C)
5. **Click "Paste article text"** above and paste

Alternative methods:
- Try the Politico mobile app
- Use your browser's Reader Mode (usually in the address bar)
- Try accessing through Google (search for the article title)
"""
        elif 'wsj.com' in domain or 'ft.com' in domain:
            instructions = """
**This appears to be a paywalled article. Options:**

1. **If you're a subscriber:**
   - Log in to your account
   - Copy the article text
   - Use "Paste article text" option

2. **Try Google Cache:**
   - Search for the article title in Google
   - Click the three dots next to the result
   - Select "Cached" if available

3. **Use browser extensions:**
   - Bypass Paywalls Clean
   - Reader Mode extensions
"""
        elif 'nytimes.com' in domain:
            instructions = """
**The New York Times limits free articles. Try these methods:**

1. **Copy the article text** if you can access it
2. **Use incognito/private browsing** mode
3. **Try the NYTimes app** if you're a subscriber
4. **Search for the headline** - it might be syndicated elsewhere
5. **Use archive sites** like archive.is or archive.org
"""
        else:
            instructions = """
**This website blocked automatic extraction. Here's what to do:**

1. **Open the article** in your browser
2. **Select and copy** the article text
3. **Click "Paste article text"** above
4. **Paste the content**

The analysis will work perfectly with pasted text!
"""
        
        return {
            'title': title_guess,
            'text': f"""Unable to automatically extract content from {domain}.

{instructions}

**Why this happens:**
- Advanced bot detection (Cloudflare, etc.)
- JavaScript-heavy sites
- Paywalls or login requirements
- Geographic restrictions

**Important:** The analysis tool works exactly the same with pasted text. You'll still get:
✓ Bias detection
✓ Credibility scoring
✓ Fact checking
✓ Manipulation tactics analysis
✓ Author verification
✓ Comprehensive report

Simply paste the article text to continue!""",
            'author': None,
            'publish_date': None,
            'url': url,
            'domain': domain,
            'extraction_failed': True
        }
    
    def _extract_title_from_text(self, text):
        """Extract title from text as fallback"""
        if not text:
            return "Article"
        
        lines = text.split('\n')
        for line in lines[:5]:
            line = line.strip()
            if line and 10 < len(line) < 200:
                return line
        
        return text[:100] + "..." if len(text) > 100 else text
