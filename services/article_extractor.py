# services/article_extractor.py
"""
Enhanced Article Extraction Service
Extracts article content from URLs or raw text with support for live news pages
"""

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
        self.min_content_length = 100
        self.min_paragraphs = 3
        self.min_words_per_paragraph = 10
    
    def _get_headers(self, referer: Optional[str] = None) -> Dict[str, str]:
        """Get randomized headers"""
        static_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
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
        ]
        
        # Filter out None methods
        methods = [m for m in methods if m is not None]
        
        last_error = None
        for method_name, method_func in methods:
            try:
                logger.info(f"Trying {method_name} for {url}")
                result = method_func(url)
                
                if result.get('success'):
                    # Record success
                    self.circuit_breaker.record_success(domain)
                    
                    # Add timing info
                    result['extraction_metadata'] = result.get('extraction_metadata', {})
                    result['extraction_metadata']['duration'] = time.time() - start_time
                    result['extraction_metadata']['method'] = method_name
                    
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
            return emergency_result
        
        error_msg = f"All extraction methods failed. Last error: {last_error}"
        logger.error(f"{error_msg} for {url}")
        
        return {
            'success': False,
            'error': error_msg,
            'url': url,
            'domain': domain,
            'extraction_metadata': {
                'all_methods_failed': True,
                'duration': time.time() - start_time
            }
        }
    
    def _quick_extract(self, url: str) -> Dict[str, Any]:
        """Quick extraction using requests"""
        try:
            headers = self._get_headers()
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            return self._parse_content(response.text, url)
            
        except Exception as e:
            logger.error(f"Quick extract failed: {e}")
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
                return {
                    'service': self.service_name,
                    'success': False,
                    'available': self.is_available,
                    'error': error_msg,
                    'timestamp': time.time()
                }
                
        except Exception as e:
            logger.error(f"ArticleExtractor.analyze failed with unexpected error: {e}", exc_info=True)
            return {
                'service': self.service_name,
                'success': False,
                'available': self.is_available,
                'error': f"Unexpected error during extraction: {str(e)}",
                'timestamp': time.time()
            }
    
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
