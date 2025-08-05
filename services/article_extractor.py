"""
FILE: services/article_extractor.py
Universal article extractor that works with ANY site of ANY size
Uses intelligent content detection instead of brittle selectors
FIXED: All NoneType errors with proper null checking
"""

import os
import logging
import requests
from bs4 import BeautifulSoup, NavigableString, Comment
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import json
from urllib.parse import urlparse
import time
import random
import re
from fake_useragent import UserAgent
from collections import defaultdict
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

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

class CircuitBreaker:
    """Circuit breaker to prevent repeated attempts to problematic domains"""
    def __init__(self):
        self.failed_domains = defaultdict(lambda: {'count': 0, 'last_attempt': None, 'last_error': None})
        self.threshold = 3
        self.timeout_duration = 300
        self._lock = threading.Lock()
    
    def is_open(self, domain: str) -> bool:
        with self._lock:
            if domain not in self.failed_domains:
                return False
            
            failure_data = self.failed_domains[domain]
            if failure_data['count'] >= self.threshold:
                if failure_data['last_attempt']:
                    time_since_failure = (datetime.now() - failure_data['last_attempt']).total_seconds()
                    if time_since_failure < self.timeout_duration:
                        return True
                    else:
                        self.failed_domains[domain] = {'count': 0, 'last_attempt': None, 'last_error': None}
            return False
    
    def record_failure(self, domain: str, error: str = None):
        with self._lock:
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
        self.min_paragraphs = 2  # At least 2 paragraphs for an article
        self.min_words_per_paragraph = 10  # At least 10 words per paragraph
        self.min_total_words = 50  # At least 50 words total (handles very short articles)
    
    def extract_content(self, soup: BeautifulSoup) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Extract article content using multiple strategies
        Returns: (content_text, metadata_dict)
        """
        # Clean the soup first
        self._clean_soup(soup)
        
        # Try multiple extraction strategies in order of reliability
        strategies = [
            ("structured_data", self._extract_from_structured_data),
            ("article_tag", self._extract_from_article_tag),
            ("main_tag", self._extract_from_main_tag),
            ("text_density", self._extract_by_text_density),
            ("paragraph_clustering", self._extract_by_paragraph_clustering),
            ("heuristic", self._extract_by_heuristics)
        ]
        
        best_content = None
        best_score = 0
        best_method = None
        metadata = {}
        
        for method_name, method_func in strategies:
            try:
                logger.debug(f"Trying extraction method: {method_name}")
                content, score = method_func(soup)
                if content and score > best_score:
                    # Validate it's not paywall/error content
                    if not self._is_paywall_content(content) and self._is_valid_article_content(content):
                        best_content = content
                        best_score = score
                        best_method = method_name
                        logger.info(f"Found content with {method_name}: score={score}, length={len(content)}")
                    else:
                        logger.debug(f"{method_name} content failed validation")
            except Exception as e:
                logger.debug(f"Strategy {method_name} failed: {e}")
                continue
        
        if best_content:
            metadata['extraction_method'] = best_method
            metadata['confidence_score'] = best_score
            return best_content, metadata
        
        # If we get here, no content was found
        logger.warning("No content found after trying all extraction methods")
        return None, {"error": "No article content found"}
    
    def _clean_soup(self, soup: BeautifulSoup):
        """Remove non-content elements from soup"""
        # Remove script, style, and other non-content tags
        for tag in soup(['script', 'style', 'noscript', 'iframe', 'svg', 'canvas']):
            tag.decompose()
        
        # Remove comments
        for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
            comment.extract()
        
        # Remove hidden elements
        for hidden in soup.find_all(style=re.compile(r'display:\s*none', re.I)):
            hidden.decompose()
        
        for hidden in soup.find_all(class_=re.compile(r'hidden|invisible', re.I)):
            if not any(term in str(hidden.get('class', [])) for term in ['article', 'content', 'body']):
                hidden.decompose()
    
    def _extract_from_structured_data(self, soup: BeautifulSoup) -> Tuple[Optional[str], float]:
        """Extract from JSON-LD or microdata"""
        # Try JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                if script.string:
                    data = json.loads(script.string)
                    content = self._get_content_from_structured_data(data)
                    if content and len(content.split()) > self.min_total_words:
                        return content, 0.95  # High confidence
            except json.JSONDecodeError:
                logger.debug("Invalid JSON-LD found, skipping")
                continue
            except Exception as e:
                logger.debug(f"Error parsing structured data: {e}")
                continue
        
        # Try microdata
        article_body = soup.find(attrs={'itemprop': 'articleBody'})
        if article_body:
            content = article_body.get_text(separator=' ', strip=True)
            if len(content.split()) >= self.min_total_words:
                return content, 0.90
        
        return None, 0
    
    def _get_content_from_structured_data(self, data: Any) -> Optional[str]:
        """Recursively extract article content from structured data"""
        if data is None:
            return None
            
        if isinstance(data, dict):
            # Direct article body
            if 'articleBody' in data and data['articleBody']:
                return data['articleBody']
            # NewsArticle schema
            if data.get('@type') in ['NewsArticle', 'Article', 'BlogPosting']:
                body = data.get('articleBody') or data.get('text')
                if body:
                    return body
            # Recursively check nested structures
            for key, value in data.items():
                if value is not None:
                    content = self._get_content_from_structured_data(value)
                    if content:
                        return content
        elif isinstance(data, list):
            for item in data:
                if item is not None:
                    content = self._get_content_from_structured_data(item)
                    if content:
                        return content
        return None
    
    def _extract_from_article_tag(self, soup: BeautifulSoup) -> Tuple[Optional[str], float]:
        """Extract from <article> tag with quality scoring"""
        articles = soup.find_all('article')
        
        best_content = None
        best_score = 0
        
        for article in articles:
            paragraphs = article.find_all('p')
            if len(paragraphs) >= self.min_paragraphs:
                content = ' '.join([p.get_text(strip=True) for p in paragraphs 
                                  if len(p.get_text(strip=True).split()) >= self.min_words_per_paragraph])
                
                # Score based on content quality
                score = self._score_content(content, len(paragraphs))
                if score > best_score:
                    best_content = content
                    best_score = score
        
        return best_content, best_score
    
    def _extract_from_main_tag(self, soup: BeautifulSoup) -> Tuple[Optional[str], float]:
        """Extract from <main> tag"""
        main = soup.find('main')
        if main:
            paragraphs = main.find_all('p')
            if len(paragraphs) >= self.min_paragraphs:
                content = ' '.join([p.get_text(strip=True) for p in paragraphs 
                                  if len(p.get_text(strip=True).split()) >= self.min_words_per_paragraph])
                score = self._score_content(content, len(paragraphs))
                return content, score
        return None, 0
    
    def _extract_by_text_density(self, soup: BeautifulSoup) -> Tuple[Optional[str], float]:
        """Extract content based on text density analysis"""
        # Find all potential content containers
        containers = soup.find_all(['div', 'section', 'article', 'main'], recursive=True)
        
        best_content = None
        best_density = 0
        best_score = 0
        
        for container in containers:
            try:
                # Skip very small containers
                if not container.get_text(strip=True):
                    continue
                    
                # Skip if container has too many links (likely navigation)
                links = container.find_all('a')
                total_text = container.get_text(strip=True)
                
                # More lenient link ratio check
                if links and len(links) > 30 and len(total_text) / (len(links) + 1) < 30:
                    continue
                
                # Calculate text density
                text_length = len(total_text)
                html_length = len(str(container))
                
                if html_length == 0:
                    continue
                    
                density = text_length / html_length
                
                # Extract paragraphs
                paragraphs = container.find_all('p')
                if len(paragraphs) >= self.min_paragraphs:
                    # Get good paragraphs
                    good_paragraphs = []
                    for p in paragraphs:
                        p_text = p.get_text(strip=True)
                        if len(p_text.split()) >= self.min_words_per_paragraph:
                            good_paragraphs.append(p_text)
                    
                    if len(good_paragraphs) >= self.min_paragraphs:
                        content = ' '.join(good_paragraphs)
                        
                        # Score based on density and content quality
                        if density > 0.1 and len(content.split()) >= self.min_total_words:
                            score = self._score_content(content, len(good_paragraphs)) * min(density * 5, 1.0)
                            if score > best_score:
                                best_content = content
                                best_density = density
                                best_score = score
            except Exception as e:
                logger.debug(f"Error processing container in text_density: {e}")
                continue
        
        # Normalize score
        return best_content, min(best_score, 0.85)
    
    def _extract_by_paragraph_clustering(self, soup: BeautifulSoup) -> Tuple[Optional[str], float]:
        """Extract content by finding clusters of paragraphs"""
        all_paragraphs = soup.find_all('p')
        
        if len(all_paragraphs) < self.min_paragraphs:
            return None, 0
        
        # Group consecutive paragraphs
        clusters = []
        current_cluster = []
        
        for i, p in enumerate(all_paragraphs):
            text = p.get_text(strip=True)
            word_count = len(text.split())
            
            # Skip short paragraphs
            if word_count < self.min_words_per_paragraph:
                if current_cluster:
                    clusters.append(current_cluster)
                    current_cluster = []
                continue
            
            # Check if paragraph is likely content
            if not self._is_likely_navigation_text(text):
                current_cluster.append(text)
            else:
                if current_cluster:
                    clusters.append(current_cluster)
                    current_cluster = []
        
        if current_cluster:
            clusters.append(current_cluster)
        
        # Find the best cluster
        best_cluster = None
        best_score = 0
        
        for cluster in clusters:
            if len(cluster) >= self.min_paragraphs:
                content = ' '.join(cluster)
                score = self._score_content(content, len(cluster))
                if score > best_score:
                    best_cluster = content
                    best_score = score
        
        return best_cluster, best_score * 0.8  # Slightly lower confidence
    
    def _extract_by_heuristics(self, soup: BeautifulSoup) -> Tuple[Optional[str], float]:
        """Last resort: use heuristics to find content"""
        # Look for divs with high paragraph density
        potential_containers = []
        
        # Try more flexible selectors
        for elem in soup.find_all(['div', 'section', 'article', 'main', 'aside'], recursive=True):
            try:
                # Get direct paragraph children
                paragraphs = elem.find_all('p', recursive=True)  # Changed to recursive=True
                if len(paragraphs) >= self.min_paragraphs:
                    # Check paragraph quality
                    good_paragraphs = []
                    for p in paragraphs:
                        p_text = p.get_text(strip=True)
                        if len(p_text.split()) >= self.min_words_per_paragraph:
                            good_paragraphs.append(p_text)
                    
                    if len(good_paragraphs) >= self.min_paragraphs:
                        content = ' '.join(good_paragraphs)
                        score = self._score_content(content, len(good_paragraphs))
                        potential_containers.append((content, score * 0.7))  # Lower confidence
            except Exception as e:
                logger.debug(f"Error in heuristics container processing: {e}")
                continue
        
        if potential_containers:
            # Return the best one
            potential_containers.sort(key=lambda x: x[1], reverse=True)
            return potential_containers[0]
        
        # Absolute last resort: get all good paragraphs
        logger.debug("Falling back to collecting all paragraphs")
        all_paragraphs = []
        for p in soup.find_all('p'):
            try:
                text = p.get_text(strip=True)
                if (len(text.split()) >= self.min_words_per_paragraph and 
                    not self._is_likely_navigation_text(text)):
                    all_paragraphs.append(text)
            except Exception as e:
                logger.debug(f"Error processing paragraph: {e}")
                continue
        
        if len(all_paragraphs) >= self.min_paragraphs:
            content = ' '.join(all_paragraphs)
            return content, 0.5  # Low confidence
        
        logger.debug(f"Heuristics found {len(all_paragraphs)} paragraphs, needed {self.min_paragraphs}")
        return None, 0
    
    def _score_content(self, content: str, paragraph_count: int) -> float:
        """Score content quality (0-1)"""
        if not content:
            return 0
        
        words = content.split()
        word_count = len(words)
        
        # Base score on word count
        if word_count < self.min_total_words:
            return 0
        
        score = min(word_count / 500, 1.0)  # Max out at 500 words
        
        # Bonus for paragraph count
        score += min(paragraph_count / 10, 0.3)  # Max 0.3 bonus
        
        # Penalty for too many short sentences (might be navigation)
        sentences = re.split(r'[.!?]+', content)
        short_sentences = sum(1 for s in sentences if len(s.split()) < 5)
        if short_sentences > len(sentences) * 0.5:
            score *= 0.7
        
        # Penalty for repetitive content
        unique_words = len(set(words))
        if unique_words < word_count * 0.3:  # Less than 30% unique words
            score *= 0.5
        
        return min(score, 1.0)
    
    def _is_likely_navigation_text(self, text: str) -> bool:
        """Check if text is likely navigation/menu/footer content"""
        text_lower = text.lower()
        
        # Check length
        if len(text.split()) < 5:
            return True
        
        # Check for common navigation patterns
        nav_patterns = [
            r'^(home|about|contact|privacy|terms|search|menu|subscribe|follow)',
            r'^\d+$',  # Just numbers
            r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$',  # Email
            r'©|®|™',  # Copyright symbols
            r'all rights reserved',
            r'^\s*$'  # Empty or whitespace
        ]
        
        for pattern in nav_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def _is_paywall_content(self, content: str) -> bool:
        """Check if content is likely a paywall message"""
        if not content or len(content) < 100:
            return False
        
        content_lower = content.lower()
        
        # Check for paywall indicators
        for pattern in self.paywall_patterns:
            if re.search(pattern, content_lower):
                return True
        
        # Check for suspiciously short content with subscribe message
        if len(content.split()) < 100 and 'subscribe' in content_lower:
            return True
        
        return False
    
    def _is_valid_article_content(self, content: str) -> bool:
        """Validate that extracted content is actually an article"""
        if not content:
            return False
        
        words = content.split()
        word_count = len(words)
        
        # Check minimum length
        if word_count < self.min_total_words:
            return False
        
        # Check for too many non-content indicators
        content_lower = content.lower()
        non_content_count = sum(1 for pattern in self.non_content_patterns 
                               if re.search(pattern, content_lower))
        
        if non_content_count > 3:
            return False
        
        # Check for reasonable sentence structure
        sentences = re.split(r'[.!?]+', content)
        valid_sentences = [s for s in sentences if 5 <= len(s.split()) <= 50]
        
        if len(valid_sentences) < 2:
            return False
        
        return True

class ArticleExtractor:
    """Universal article extractor that works with any site"""
    
    def __init__(self):
        # Timeout configuration
        self.quick_timeout = 10
        self.browser_timeout = 20
        self.total_timeout = 60
        self.delay_range = (0.5, 2)
        self.ua = UserAgent()
        self.circuit_breaker = CircuitBreaker()
        
        # Initialize content extractor
        self.content_extractor = ContentExtractor()
        
        # Thread pool for timeout control
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Browser-like session configuration
        self.session = requests.Session()
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
            self.cloudscraper_session = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'desktop': True
                }
            )
            
        logger.info(f"ArticleExtractor initialized (CloudScraper: {CLOUDSCRAPER_AVAILABLE}, "
                   f"Curl-CFFI: {CURL_CFFI_AVAILABLE}, Selenium: {SELENIUM_AVAILABLE}, "
                   f"Playwright: {PLAYWRIGHT_AVAILABLE})")
    
    def _get_headers(self, referer=None):
        """Get randomized headers that look like a real browser"""
        headers = {
            'User-Agent': self.ua.chrome,
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
            'Cache-Control': 'max-age=0'
        }
        
        if referer:
            headers['Referer'] = referer
            headers['Sec-Fetch-Site'] = 'same-origin'
            
        return headers
    
    def _delay(self):
        """Random delay to avoid rate limiting"""
        time.sleep(random.uniform(*self.delay_range))
    
    def _execute_with_timeout(self, func, url, timeout):
        """Execute function with timeout using thread pool"""
        future = self.executor.submit(func, url)
        try:
            return future.result(timeout=timeout)
        except FutureTimeoutError:
            future.cancel()
            raise TimeoutError(f"Method timed out after {timeout} seconds")
    
    def extract_from_url(self, url: str) -> Dict[str, Any]:
        """
        Extract article content from URL using multiple methods
        
        Returns:
            Dict containing article data or error information
        """
        start_time = time.time()
        logger.info(f"Extracting article from: {url}")
        
        # Parse domain for circuit breaker
        domain = urlparse(url).netloc.lower().replace('www.', '')
        
        # Check circuit breaker
        if self.circuit_breaker.is_open(domain):
            last_error = self.circuit_breaker.get_last_error(domain)
            logger.warning(f"Circuit breaker open for {domain}")
            return {
                'success': False,
                'error': f'Too many failures for {domain}. Last error: {last_error}',
                'url': url
            }
        
        # Determine extraction methods
        methods = []
        
        # Always try enhanced requests first (fastest)
        methods.append(("enhanced requests", self._extract_with_enhanced_requests, self.quick_timeout))
        
        # Add advanced methods if available
        if CLOUDSCRAPER_AVAILABLE:
            methods.append(("cloudscraper", self._extract_with_cloudscraper, self.quick_timeout))
        if CURL_CFFI_AVAILABLE:
            methods.append(("curl-cffi", self._extract_with_curl_cffi, self.quick_timeout))
        
        # Add cookies method
        methods.append(("requests with cookies", self._extract_with_cookies, self.quick_timeout))
        
        # Add browser methods for sites that need them
        if SELENIUM_AVAILABLE:
            methods.append(("selenium", self._extract_with_selenium, self.browser_timeout))
        if PLAYWRIGHT_AVAILABLE:
            methods.append(("playwright", self._extract_with_playwright, self.browser_timeout))
            
        # Add proxy as last resort
        methods.append(("proxy rotation", self._extract_with_proxy, self.quick_timeout))
        
        last_error = None
        for method_name, method_func, method_timeout in methods:
            # Check total timeout
            elapsed = time.time() - start_time
            if elapsed > self.total_timeout:
                logger.error(f"Total timeout exceeded for {url}")
                self.circuit_breaker.record_failure(domain, "Total timeout exceeded")
                return {
                    'success': False,
                    'error': f'Extraction timeout after {elapsed:.1f}s',
                    'url': url
                }
            
            # Calculate remaining time
            remaining_time = self.total_timeout - elapsed
            actual_timeout = min(method_timeout, remaining_time)
            
            try:
                logger.info(f"Trying {method_name}... (timeout: {actual_timeout:.1f}s)")
                
                # Execute with timeout protection
                html_content = self._execute_with_timeout(method_func, url, actual_timeout)
                
                if html_content:
                    logger.info(f"Got HTML with {method_name} ({len(html_content)} chars)")
                    
                    # Parse and extract content using intelligent extraction
                    parsed_result = self._parse_article(html_content, url)
                    
                    # Check if we successfully extracted content
                    if parsed_result.get('success') and parsed_result.get('text'):
                        logger.info(f"Successfully extracted article: {parsed_result.get('word_count', 0)} words")
                        self.circuit_breaker.record_success(domain)
                        return parsed_result
                    else:
                        logger.warning(f"Content extraction failed: {parsed_result.get('error', 'Unknown error')}")
                        last_error = parsed_result.get('error', 'Content extraction failed')
                        # Continue trying other methods
                        continue
                        
            except TimeoutError as e:
                logger.warning(f"{method_name} timed out: {str(e)}")
                last_error = f"Timeout: {str(e)}"
                continue
            except requests.exceptions.HTTPError as e:
                if e.response and e.response.status_code == 403:
                    logger.warning(f"{method_name} got 403 Forbidden")
                    last_error = "403 Forbidden - Site blocking automated access"
                    # Don't give up on 403s until we try browser methods
                    if methods.index((method_name, method_func, method_timeout)) > 3:
                        self.circuit_breaker.record_failure(domain, last_error)
                else:
                    logger.warning(f"{method_name} HTTP error: {str(e)}")
                    last_error = str(e)
                continue
            except Exception as e:
                logger.warning(f"{method_name} failed: {str(e)}")
                last_error = str(e)
                continue
        
        # All methods failed
        self.circuit_breaker.record_failure(domain, last_error)
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
            self.session.get(homepage, headers=self._get_headers(), timeout=5)
        except:
            pass  # Continue anyway
        
        # Now make the actual request with cookies
        headers = self._get_headers(referer=homepage)
        response = self.session.get(
            url, 
            headers=headers, 
            timeout=self.quick_timeout,
            allow_redirects=True,
            stream=False
        )
        response.raise_for_status()
        
        return response.text
    
    def _extract_with_cloudscraper(self, url: str) -> Optional[str]:
        """CloudScraper method with enhanced options"""
        if not CLOUDSCRAPER_AVAILABLE:
            raise Exception("CloudScraper not available")
            
        self._delay()
        
        response = self.cloudscraper_session.get(url, timeout=self.quick_timeout)
        response.raise_for_status()
        
        return response.text
    
    def _extract_with_curl_cffi(self, url: str) -> Optional[str]:
        """Curl-CFFI with multiple browser impersonations"""
        if not CURL_CFFI_AVAILABLE:
            raise Exception("Curl-CFFI not available")
            
        self._delay()
        
        # Try different browser impersonations
        browsers = ['chrome120', 'chrome119', 'chrome110']
        
        for browser in browsers:
            try:
                response = curl_requests.get(
                    url, 
                    impersonate=browser,
                    headers=self._get_headers(),
                    timeout=self.quick_timeout,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 403:
                    raise requests.exceptions.HTTPError("403 Client Error: Forbidden", response=response)
            except Exception as e:
                if "403" in str(e):
                    raise
                continue
                
        raise Exception("All browser impersonations failed")
    
    def _extract_with_cookies(self, url: str) -> Optional[str]:
        """Try with cookie manipulation"""
        self._delay()
        
        # Create session with specific cookies
        session = requests.Session()
        
        # Common cookies that might help bypass
        cookies = {
            'CONSENT': 'YES+',
            'euConsent': 'true',
            'cookieConsent': 'true',
        }
        
        for name, value in cookies.items():
            session.cookies.set(name, value)
        
        headers = self._get_headers()
        
        response = session.get(url, headers=headers, timeout=self.quick_timeout)
        response.raise_for_status()
        
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
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        driver = None
        try:
            driver = webdriver.Chrome(options=options)
            
            # Execute script to mask automation
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set page load timeout
            driver.set_page_load_timeout(self.browser_timeout)
            
            driver.get(url)
            
            # Wait for content to load
            try:
                WebDriverWait(driver, 10).until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )
            except:
                pass
            
            # Scroll to trigger lazy loading
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            # Get the rendered HTML
            return driver.page_source
            
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def _extract_with_playwright(self, url: str) -> Optional[str]:
        """Playwright-based extraction"""
        if not PLAYWRIGHT_AVAILABLE:
            raise Exception("Playwright not available")
            
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
            context = browser.new_context(
                user_agent=self.ua.chrome,
                viewport={'width': 1920, 'height': 1080},
                locale='en-US'
            )
            
            # Add extra headers
            context.set_extra_http_headers(self._get_headers())
            
            page = context.new_page()
            
            # Set timeout
            page.set_default_timeout(self.browser_timeout * 1000)
            
            # Navigate and wait
            page.goto(url, wait_until='domcontentloaded')
            
            # Wait for content
            page.wait_for_load_state('networkidle')
            
            # Scroll to load lazy content
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1000)
            
            content = page.content()
            browser.close()
            
            return content
    
    def _extract_with_proxy(self, url: str) -> Optional[str]:
        """Last resort: try with proxy headers"""
        self._delay()
        
        # Try with different headers to appear as proxy
        headers = self._get_headers()
        headers.update({
            'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'X-Real-IP': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        })
        
        response = requests.get(url, headers=headers, timeout=self.quick_timeout)
        response.raise_for_status()
        
        return response.text
    
    def _parse_article(self, html_content: str, url: str) -> Dict[str, Any]:
        """Parse article content from HTML using intelligent extraction"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Initialize result
            article_data = {
                'url': url,
                'domain': urlparse(url).netloc,
                'extracted_at': datetime.now().isoformat(),
                'success': False
            }
            
            # Extract metadata first - FIXED with proper null checks
            # Title extraction
            title = None
            meta_title = soup.find('meta', property='og:title')
            if meta_title and meta_title.get('content'):
                title = meta_title.get('content', '').strip()
            if not title:
                title_tag = soup.find('title')
                if title_tag:
                    title = title_tag.get_text().strip()
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
            
            # Description - FIXED with proper null checks
            description = None
            meta_desc = soup.find('meta', {'name': 'description'})
            if not meta_desc:
                meta_desc = soup.find('meta', property='og:description')
            
            if meta_desc and meta_desc.get('content'):
                content_value = meta_desc.get('content')
                if content_value:
                    description = content_value.strip()
            
            article_data['description'] = description
            
            # Image - FIXED with proper null checks
            image = None
            meta_image = soup.find('meta', property='og:image')
            if meta_image and meta_image.get('content'):
                content_value = meta_image.get('content')
                if content_value:
                    image = content_value
            article_data['image'] = image
            
            # Keywords - FIXED with proper null checks
            keywords = []
            meta_keywords = soup.find('meta', {'name': 'keywords'})
            if meta_keywords and meta_keywords.get('content'):
                content_value = meta_keywords.get('content')
                if content_value:
                    keywords = [k.strip() for k in content_value.split(',') if k.strip()]
            article_data['keywords'] = keywords
            
            # Now extract the actual content using intelligent extraction
            content, extraction_metadata = self.content_extractor.extract_content(soup)
            
            if content:
                article_data['text'] = content
                article_data['word_count'] = len(content.split())
                article_data['success'] = True
                article_data['extraction_metadata'] = extraction_metadata
                logger.info(f"Content extracted using {extraction_metadata.get('extraction_method', 'unknown')} method")
            else:
                article_data['error'] = extraction_metadata.get('error', 'Failed to extract article content')
                article_data['text'] = None
                article_data['word_count'] = 0
            
            return article_data
            
        except Exception as e:
            logger.error(f"Error parsing article: {e}")
            return {
                'success': False,
                'error': f'Parsing error: {str(e)}',
                'url': url
            }
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author with multiple strategies - FIXED with proper null checks"""
        # Try JSON-LD first with error handling
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                if script and script.string:
                    data = json.loads(script.string)
                    author = self._get_author_from_structured_data(data)
                    if author:
                        return author
            except (json.JSONDecodeError, AttributeError, TypeError) as e:
                logger.debug(f"Error parsing JSON-LD for author: {e}")
                continue
            except Exception as e:
                logger.debug(f"Unexpected error parsing structured data for author: {e}")
                continue
        
        # Try meta tags - FIXED with proper null checks
        meta_author = soup.find('meta', {'name': 'author'})
        if not meta_author:
            meta_author = soup.find('meta', property='article:author')
        
        if meta_author and meta_author.get('content'):
            content_value = meta_author.get('content')
            if content_value:
                return content_value.strip()
        
        # Try common author patterns
        author_selectors = [
            {'class': re.compile(r'author|byline|writer|by\b', re.I)},
            {'itemprop': 'author'},
            {'rel': 'author'},
            {'data-testid': re.compile(r'author', re.I)}
        ]
        
        for selector in author_selectors:
            element = soup.find(['span', 'div', 'p', 'a', 'address'], selector)
            if element:
                text = element.get_text().strip()
                # Clean common prefixes
                for prefix in ['By', 'by', 'BY', 'Written by', 'Author:', 'By:']:
                    if text.startswith(prefix):
                        text = text[len(prefix):].strip()
                
                # Validate it looks like a name
                if text and 2 <= len(text.split()) <= 5 and len(text) < 100:
                    return text
        
        return None
    
    def _get_author_from_structured_data(self, data: Any) -> Optional[str]:
        """Extract author from structured data"""
        if isinstance(data, dict):
            if 'author' in data:
                author_data = data['author']
                if author_data is None:
                    return None
                if isinstance(author_data, dict):
                    return author_data.get('name')
                elif isinstance(author_data, str):
                    return author_data
            # Check nested structures
            for value in data.values():
                if value is not None:
                    author = self._get_author_from_structured_data(value)
                    if author:
                        return author
        elif isinstance(data, list):
            for item in data:
                if item is not None:
                    author = self._get_author_from_structured_data(item)
                    if author:
                        return author
        return None
    
    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract publish date - FIXED with proper null checks"""
        # Try meta tags first
        date_meta_names = [
            'article:published_time', 'datePublished', 'pubdate',
            'publishdate', 'date', 'DC.date.issued', 'publish_date'
        ]
        
        for name in date_meta_names:
            meta = soup.find('meta', {'property': name})
            if not meta:
                meta = soup.find('meta', {'name': name})
            
            if meta and meta.get('content'):
                content_value = meta.get('content')
                if content_value:
                    return content_value.strip()
        
        # Try time tag
        time_tag = soup.find('time')
        if time_tag:
            datetime_attr = time_tag.get('datetime')
            if datetime_attr:
                return datetime_attr.strip()
            text = time_tag.get_text()
            if text:
                return text.strip()
        
        # Try common date patterns
        date_selectors = [
            {'class': re.compile(r'date|time|published', re.I)},
            {'itemprop': 'datePublished'},
            {'datetime': True}
        ]
        
        for selector in date_selectors:
            element = soup.find(['time', 'span', 'div'], selector)
            if element:
                datetime_attr = element.get('datetime')
                if datetime_attr:
                    return datetime_attr.strip()
                text = element.get_text()
                if text:
                    return text.strip()
        
        return None
    
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
    
    def __del__(self):
        """Cleanup thread pool on deletion"""
        try:
            self.executor.shutdown(wait=False)
        except:
            pass
