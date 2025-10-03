"""
Article Extractor Service - PRODUCTION v10.0
Date Created: October 2, 2025
Last Modified: October 3, 2025

CHANGES IN v10.0 (October 3, 2025):
1. TRIES SCRAPERAPI FIRST for all sites (including ABC News) - best chance of success
2. Falls back to special handlers only if ScraperAPI fails
3. Returns user-friendly prompts when extraction fails - asks user to paste content
4. Proper validation - requires minimum 200 chars of actual text
5. Clear error messages explaining what went wrong and what to do

This version maximizes extraction success by using ScraperAPI properly.
"""

import os
import sys
import re
import json
import time
import logging
import hashlib
from typing import Dict, Any, Optional, Tuple, List
from urllib.parse import urlparse, quote_plus, parse_qs
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from newspaper import Article, ArticleException

print(f"[ARTICLE_EXTRACTOR v10.0] Loading with ScraperAPI priority and user prompts...", file=sys.stderr)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress noisy loggers
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('newspaper').setLevel(logging.WARNING)

logger.info("[ARTICLE_EXTRACTOR v10.0] Module loading with ScraperAPI priority...")


class ArticleExtractorCore:
    """Core extraction logic that tries ScraperAPI first"""
    
    VERSION = "10.0"
    MIN_VALID_TEXT_LENGTH = 200  # Minimum characters for valid article
    
    def __init__(self):
        """Initialize the article extractor"""
        self.scraperapi_key = os.environ.get('SCRAPERAPI_KEY', '')
        self.session = requests.Session()
        
        # Multiple user agents for fallback attempts
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
        ]
        
        self.session.headers.update({
            'User-Agent': self.user_agents[0],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Cache for extracted articles
        self._cache = {}
        self._cache_ttl = 3600  # 1 hour
        
        logger.info(f"[EXTRACTOR v{self.VERSION}] Initialized - ScraperAPI: {'CONFIGURED' if self.scraperapi_key else 'NOT CONFIGURED'}")
    
    def extract(self, url: str) -> Dict[str, Any]:
        """
        Extract article from URL with ScraperAPI priority
        
        Extraction strategy:
        1. Try ScraperAPI first (if configured) - highest success rate
        2. Try site-specific handlers (for known problematic sites)
        3. Try BeautifulSoup with multiple user agents
        4. Try Newspaper3k
        5. If all fail, return helpful error asking user to paste content
        """
        logger.info(f"[EXTRACTOR v{self.VERSION}] Extracting from URL: {url}")
        
        # Check cache
        cache_key = self._get_cache_key(url)
        if cache_key in self._cache:
            cache_entry = self._cache[cache_key]
            if time.time() - cache_entry['timestamp'] < self._cache_ttl:
                logger.info("✓ Returning cached article")
                return cache_entry['data']
        
        # Clean URL
        clean_url = self._clean_url(url)
        domain = urlparse(clean_url).netloc.replace('www.', '')
        
        result = None
        
        # METHOD 1: Try ScraperAPI first (if configured) - BEST SUCCESS RATE
        if self.scraperapi_key:
            logger.info("Method 1: Trying ScraperAPI (highest success rate)...")
            result = self._extract_with_scraperapi(clean_url)
            if result and self._is_valid_extraction(result):
                logger.info(f"✓ ScraperAPI SUCCESS - {result.get('word_count', 0)} words")
                self._cache_result(cache_key, result)
                return result
            logger.warning("✗ ScraperAPI failed or returned insufficient content")
        else:
            logger.warning("⚠ ScraperAPI not configured - skipping (set SCRAPERAPI_KEY for better results)")
        
        # METHOD 2: Try site-specific handlers for known problematic sites
        if 'abcnews' in domain:
            logger.info("Method 2: Trying ABC News special handler...")
            result = self._extract_abc_news(clean_url)
            if result and self._is_valid_extraction(result):
                logger.info(f"✓ ABC News handler SUCCESS - {result.get('word_count', 0)} words")
                self._cache_result(cache_key, result)
                return result
            logger.warning("✗ ABC News special handler failed")
        
        # METHOD 3: Try BeautifulSoup with multiple user agents
        logger.info("Method 3: Trying BeautifulSoup with multiple user agents...")
        result = self._extract_with_beautifulsoup(clean_url)
        if result and self._is_valid_extraction(result):
            logger.info(f"✓ BeautifulSoup SUCCESS - {result.get('word_count', 0)} words")
            self._cache_result(cache_key, result)
            return result
        logger.warning("✗ BeautifulSoup failed")
        
        # METHOD 4: Try Newspaper3k as last resort
        logger.info("Method 4: Trying Newspaper3k...")
        result = self._extract_with_newspaper(clean_url)
        if result and self._is_valid_extraction(result):
            logger.info(f"✓ Newspaper3k SUCCESS - {result.get('word_count', 0)} words")
            self._cache_result(cache_key, result)
            return result
        logger.warning("✗ Newspaper3k failed")
        
        # ALL METHODS FAILED - Return user-friendly error
        logger.error(f"❌ ALL EXTRACTION METHODS FAILED for {url}")
        return self._create_blocked_error_response(url, domain)
    
    def _is_valid_extraction(self, result: Dict[str, Any]) -> bool:
        """Validate that extraction actually succeeded with real content"""
        if not result or not result.get('success'):
            return False
        
        text = result.get('text', '')
        if not text or len(text) < self.MIN_VALID_TEXT_LENGTH:
            logger.warning(f"Insufficient text: {len(text)} chars (minimum {self.MIN_VALID_TEXT_LENGTH})")
            return False
        
        # Check if it's just the URL
        url = result.get('url', '')
        if text.strip() == url.strip():
            logger.warning("Text is just the URL, not actual content")
            return False
        
        return True
    
    def _clean_url(self, url: str) -> str:
        """Clean URL by removing tracking parameters"""
        if 'abcnews' in url or '?' in url:
            base_url = url.split('?')[0]
            return base_url
        return url
    
    def _extract_with_scraperapi(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract using ScraperAPI - HIGHEST SUCCESS RATE"""
        try:
            logger.info("[ScraperAPI] Attempting extraction...")
            
            api_url = "https://api.scraperapi.com"
            params = {
                'api_key': self.scraperapi_key,
                'url': url,
                'render': 'true',
                'country_code': 'us'
            }
            
            response = self.session.get(api_url, params=params, timeout=30)
            response.raise_for_status()
            
            html_content = response.text
            if not html_content or len(html_content) < 100:
                logger.warning("[ScraperAPI] Empty response")
                return None
            
            # Check for error pages
            error_indicators = ['Oops', '404', 'Page not found', 'Access Denied', 'Page Not Found']
            if any(error in html_content[:1000] for error in error_indicators):
                logger.warning("[ScraperAPI] Returned error page")
                return None
            
            # Parse with newspaper
            article = Article(url)
            article.download(input_html=html_content)
            article.parse()
            
            if article.text and len(article.text) >= self.MIN_VALID_TEXT_LENGTH:
                logger.info(f"[ScraperAPI] Newspaper parsing successful - {len(article.text)} chars")
                return self._prepare_article_result(
                    url=url,
                    title=article.title,
                    text=article.text,
                    authors=article.authors,
                    publish_date=article.publish_date,
                    extraction_method='scraperapi'
                )
            
            # Try BeautifulSoup parsing as fallback
            logger.info("[ScraperAPI] Newspaper parsing insufficient, trying BeautifulSoup...")
            result = self._parse_html_content(html_content, url)
            if result:
                result['extraction_method'] = 'scraperapi_beautifulsoup'
            return result
            
        except Exception as e:
            logger.error(f"[ScraperAPI] Failed: {e}")
            return None
    
    def _extract_abc_news(self, url: str) -> Optional[Dict[str, Any]]:
        """Special handler for ABC News"""
        try:
            logger.info("[ABC News Handler] Attempting extraction...")
            
            for idx, user_agent in enumerate(self.user_agents):
                try:
                    headers = {
                        'User-Agent': user_agent,
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Connection': 'keep-alive',
                        'Referer': 'https://www.google.com/'
                    }
                    
                    response = self.session.get(url, headers=headers, timeout=15, allow_redirects=True)
                    
                    if response.status_code == 200:
                        html = response.text
                        
                        if any(err in html[:1000] for err in ['Oops', '404', 'Page Not Found', 'Access Denied']):
                            continue
                        
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract title
                        title = None
                        title_elem = soup.find('h1') or soup.find('meta', property='og:title')
                        if title_elem:
                            title = title_elem.get('content') if title_elem.name == 'meta' else title_elem.get_text(strip=True)
                        
                        # Extract authors
                        authors = self._extract_authors(soup, html)
                        
                        # Extract content
                        content = ""
                        article_body = soup.find('div', class_='article-body') or \
                                      soup.find('div', {'data-component': 'ArticleBody'}) or \
                                      soup.find('article')
                        
                        if article_body:
                            paragraphs = article_body.find_all('p')
                            content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30])
                        
                        if len(content) >= self.MIN_VALID_TEXT_LENGTH:
                            logger.info(f"[ABC News Handler] Success - {len(content.split())} words")
                            return self._prepare_article_result(
                                url=url,
                                title=title or "ABC News Article",
                                text=content,
                                authors=authors if authors else ["ABC News"],
                                extraction_method='abc_news_handler'
                            )
                
                except requests.exceptions.RequestException:
                    continue
            
            logger.error("[ABC News Handler] All attempts failed")
            return None
            
        except Exception as e:
            logger.error(f"[ABC News Handler] Error: {e}")
            return None
    
    def _extract_with_newspaper(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract using Newspaper3k library"""
        try:
            logger.info("[Newspaper3k] Attempting extraction...")
            
            article = Article(url)
            article.config.browser_user_agent = self.session.headers['User-Agent']
            article.config.request_timeout = 20
            
            article.download()
            article.parse()
            
            if not article.text or len(article.text) < self.MIN_VALID_TEXT_LENGTH:
                return None
            
            try:
                article.nlp()
            except:
                pass
            
            logger.info(f"[Newspaper3k] Success - {len(article.text)} chars")
            return self._prepare_article_result(
                url=url,
                title=article.title,
                text=article.text,
                authors=article.authors,
                publish_date=article.publish_date,
                summary=article.summary if hasattr(article, 'summary') else None,
                extraction_method='newspaper'
            )
            
        except Exception as e:
            logger.error(f"[Newspaper3k] Failed: {e}")
            return None
    
    def _extract_with_beautifulsoup(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract using BeautifulSoup with multiple user agents"""
        try:
            logger.info("[BeautifulSoup] Attempting extraction with multiple user agents...")
            
            for idx, user_agent in enumerate(self.user_agents):
                try:
                    headers = {
                        'User-Agent': user_agent,
                        'Referer': 'https://www.google.com/'
                    }
                    response = self.session.get(url, headers=headers, timeout=20)
                    
                    if response.status_code == 200:
                        html = response.text
                        
                        if any(err in html[:1000] for err in ['Oops', '404', 'Access Denied']):
                            continue
                        
                        result = self._parse_html_content(html, url)
                        if result and self._is_valid_extraction(result):
                            logger.info(f"[BeautifulSoup] Success on attempt {idx + 1}")
                            return result
                
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"[BeautifulSoup] Failed: {e}")
            return None
    
    def _parse_html_content(self, html: str, url: str) -> Optional[Dict[str, Any]]:
        """Parse HTML content"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            for script in soup(["script", "style", "meta", "noscript", "header", "footer", "nav"]):
                script.decompose()
            
            title = self._extract_title(soup)
            content = self._extract_main_content(soup)
            authors = self._extract_authors(soup, html)
            publish_date = self._extract_publish_date(soup, html)
            
            if not content or len(content) < self.MIN_VALID_TEXT_LENGTH:
                return None
            
            return self._prepare_article_result(
                url=url,
                title=title,
                text=content,
                authors=authors if authors else ["Unknown Author"],
                publish_date=publish_date,
                extraction_method='beautifulsoup'
            )
            
        except Exception as e:
            logger.error(f"HTML parsing failed: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title from HTML"""
        selectors = [
            'h1', 'meta[property="og:title"]', 'meta[name="twitter:title"]', 'title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get('content') if element.name == 'meta' else element.get_text(strip=True)
                if title and len(title) > 10:
                    return self._clean_text(title)
        
        return "Unknown Title"
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content"""
        selectors = [
            'article', '[role="main"]', '[class*="article-body"]',
            '[class*="entry-content"]', 'div.content', 'main'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                paragraphs = elements[0].find_all(['p', 'h2', 'h3'])
                text_parts = []
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 20:
                        if not any(skip in text.lower()[:50] for skip in ['cookie', 'subscribe', 'newsletter']):
                            text_parts.append(text)
                
                if text_parts:
                    content = '\n\n'.join(text_parts)
                    if len(content) >= self.MIN_VALID_TEXT_LENGTH:
                        return content
        
        # Fallback: all paragraphs
        all_paragraphs = soup.find_all('p')
        text_parts = [p.get_text(strip=True) for p in all_paragraphs 
                     if p.get_text(strip=True) and len(p.get_text(strip=True)) > 30]
        
        if text_parts:
            return '\n\n'.join(text_parts[:50])
        
        return ""
    
    def _extract_authors(self, soup: BeautifulSoup, html: str) -> List[str]:
        """Extract authors"""
        authors = []
        
        for selector in ['meta[name="author"]', 'meta[property="article:author"]']:
            elements = soup.find_all(selector)
            for element in elements:
                author = element.get('content', '')
                if author:
                    author = re.sub(r'^By\s+', '', author, flags=re.IGNORECASE)
                    parts = re.split(r',\s*and\s*|,\s*|\s+and\s+', author)
                    for part in parts:
                        clean = self._clean_author_name(part.strip())
                        if clean != "Unknown Author" and clean not in authors:
                            authors.append(clean)
        
        return authors[:5] if authors else ["Unknown Author"]
    
    def _extract_publish_date(self, soup: BeautifulSoup, html: str) -> Optional[datetime]:
        """Extract publish date"""
        for selector in ['meta[property="article:published_time"]', 'time[datetime]']:
            element = soup.select_one(selector)
            if element:
                date_str = element.get('content') or element.get('datetime', '')
                if date_str:
                    try:
                        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except:
                        continue
        return None
    
    def _clean_text(self, text: str) -> str:
        """Clean text content"""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _clean_author_name(self, author: str) -> str:
        """Clean author name"""
        if not author:
            return "Unknown Author"
        
        author = re.sub(r'^(by|By|written by|reported by)\s+', '', author, re.IGNORECASE)
        author = re.sub(r'\s+', ' ', author).strip()
        
        if not author or len(author) < 2 or len(author) > 100:
            return "Unknown Author"
        
        if author.lower() in ['staff', 'admin', 'editor', 'newsroom']:
            return "Unknown Author"
        
        return author
    
    def _prepare_article_result(
        self, url: str, title: str, text: str,
        authors: Optional[List[str]] = None, publish_date: Optional[datetime] = None,
        summary: Optional[str] = None, extraction_method: str = 'unknown'
    ) -> Dict[str, Any]:
        """Prepare final result"""
        
        title = self._clean_text(title) if title else "Unknown Title"
        text = self._clean_text(text) if text else ""
        
        if authors:
            authors = [self._clean_author_name(a) for a in authors if a]
            authors = [a for a in authors if a != "Unknown Author"]
        
        if not authors:
            domain = urlparse(url).netloc.replace('www.', '')
            source_map = {'abcnews.go.com': 'ABC News', 'bbc.com': 'BBC', 'cnn.com': 'CNN'}
            authors = [source_map.get(domain, "Unknown Author")]
        
        author = authors[0] if len(authors) == 1 else \
                 f"{authors[0]} and {authors[1]}" if len(authors) == 2 else \
                 f"{', '.join(authors[:-1])}, and {authors[-1]}"
        
        domain = urlparse(url).netloc.replace('www.', '')
        word_count = len(text.split())
        extraction_successful = word_count > 50 and len(text) >= self.MIN_VALID_TEXT_LENGTH
        
        return {
            'success': extraction_successful,
            'url': url,
            'domain': domain,
            'title': title,
            'text': text,
            'content': text,
            'author': author,
            'authors': authors,
            'publish_date': publish_date.isoformat() if publish_date else None,
            'source': self._get_source_name(domain),
            'word_count': word_count,
            'extraction_method': extraction_method,
            'extracted_at': datetime.now().isoformat(),
            'version': self.VERSION,
            'sources_count': self._count_sources(text),
            'quotes_count': self._count_quotes(text),
            'extraction_successful': extraction_successful
        }
    
    def _count_sources(self, text: str) -> int:
        """Count sources"""
        if not text:
            return 0
        patterns = [r'according to', r'said', r'reported', r'stated', r'told', r'confirmed']
        return min(sum(len(re.findall(p, text, re.IGNORECASE)) for p in patterns), 20)
    
    def _count_quotes(self, text: str) -> int:
        """Count quotes"""
        return len(re.findall(r'"[^"]{10,}"', text)) if text else 0
    
    def _get_source_name(self, domain: str) -> str:
        """Get readable source name"""
        source_map = {
            'nytimes.com': 'The New York Times',
            'washingtonpost.com': 'The Washington Post',
            'bbc.com': 'BBC',
            'cnn.com': 'CNN',
            'abcnews.go.com': 'ABC News',
            'reuters.com': 'Reuters'
        }
        return source_map.get(domain, domain.replace('.com', '').title())
    
    def _create_blocked_error_response(self, url: str, domain: str) -> Dict[str, Any]:
        """Create error response when site blocks extraction"""
        
        # Create user-friendly error message
        user_message = (
            f"Unable to extract content from {domain}. This website is blocking automated access.\n\n"
            "Please copy and paste the article text below to analyze it."
        )
        
        return {
            'success': False,
            'url': url,
            'domain': domain,
            'title': 'Extraction Blocked',
            'text': '',
            'content': '',
            'author': 'Unknown',
            'authors': [],
            'error': 'Site blocking automated access',
            'user_message': user_message,
            'prompt_for_text': True,  # Signal to frontend to show text input
            'extraction_method': 'none',
            'version': self.VERSION,
            'extracted_at': datetime.now().isoformat(),
            'source': self._get_source_name(domain),
            'word_count': 0,
            'sources_count': 0,
            'quotes_count': 0,
            'extraction_successful': False
        }
    
    def _get_cache_key(self, url: str) -> str:
        """Generate cache key"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def _cache_result(self, key: str, result: Dict[str, Any]) -> None:
        """Cache result"""
        self._cache[key] = {'data': result, 'timestamp': time.time()}
        if len(self._cache) > 100:
            sorted_items = sorted(self._cache.items(), key=lambda x: x[1]['timestamp'])
            self._cache = dict(sorted_items[-50:])
    
    def process_text_input(self, text: str, source: str = "direct_input") -> Dict[str, Any]:
        """Process direct text input"""
        logger.info(f"[EXTRACTOR v{self.VERSION}] Processing text input ({len(text)} chars)")
        
        lines = text.strip().split('\n')
        title = lines[0][:100] if lines else "Direct Text Input"
        cleaned_text = self._clean_text(text)
        
        return {
            'success': True,
            'url': source,
            'domain': 'text_input',
            'title': title,
            'text': cleaned_text,
            'content': cleaned_text,
            'author': 'User Provided',
            'authors': ['User Provided'],
            'publish_date': datetime.now().isoformat(),
            'source': 'Direct Input',
            'word_count': len(cleaned_text.split()),
            'extraction_method': 'text_input',
            'extracted_at': datetime.now().isoformat(),
            'version': self.VERSION,
            'sources_count': self._count_sources(cleaned_text),
            'quotes_count': self._count_quotes(cleaned_text),
            'extraction_successful': True
        }


class ArticleExtractor:
    """Main class for service registry"""
    
    def __init__(self):
        self.core = ArticleExtractorCore()
        self.is_available = True
        self.service_name = 'article_extractor'
        self.scraperapi_key = self.core.scraperapi_key
        logger.info(f"[ARTICLE_EXTRACTOR v10.0] Initialized - ScraperAPI: {'YES' if self.scraperapi_key else 'NO'}")
    
    def _check_availability(self) -> bool:
        return True
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Main analysis method"""
        logger.info(f"[ARTICLE_EXTRACTOR v10.0] analyze() called")
        
        url = data.get('url', '')
        text = data.get('text', '') or data.get('content', '')
        
        try:
            if url and url.startswith('http'):
                logger.info(f"[ARTICLE_EXTRACTOR v10.0] Extracting from URL: {url}")
                result = self.core.extract(url)
            elif text:
                logger.info(f"[ARTICLE_EXTRACTOR v10.0] Processing text input: {len(text)} chars")
                result = self.core.process_text_input(text)
            else:
                logger.error("[ARTICLE_EXTRACTOR v10.0] No valid input")
                return {
                    'service': self.service_name,
                    'success': False,
                    'error': 'No URL or text provided',
                    'data': {},
                    'available': True,
                    'timestamp': time.time()
                }
            
            if result.get('success'):
                logger.info(f"[ARTICLE_EXTRACTOR v10.0] ✓ SUCCESS - {result.get('word_count', 0)} words")
                
                response_data = {
                    'text': result.get('text', ''),
                    'content': result.get('text', ''),
                    'title': result.get('title', 'Unknown'),
                    'author': result.get('author', 'Unknown'),
                    'authors': result.get('authors', []),
                    'domain': result.get('domain', ''),
                    'url': url or result.get('url', ''),
                    'source': result.get('source', ''),
                    'word_count': result.get('word_count', 0),
                    'extraction_method': result.get('extraction_method', 'unknown'),
                    'publish_date': result.get('publish_date'),
                    'sources_count': result.get('sources_count', 0),
                    'quotes_count': result.get('quotes_count', 0),
                    'extraction_successful': result.get('extraction_successful', False)
                }
                
                return {
                    'service': self.service_name,
                    'success': True,
                    'data': response_data,
                    'available': True,
                    'timestamp': time.time()
                }
            else:
                logger.error(f"[ARTICLE_EXTRACTOR v10.0] ❌ FAILED - {result.get('error', 'Unknown')}")
                
                # Return error with user prompt if available
                return {
                    'service': self.service_name,
                    'success': False,
                    'error': result.get('error', 'Extraction failed'),
                    'user_message': result.get('user_message'),
                    'prompt_for_text': result.get('prompt_for_text', False),
                    'data': {
                        'domain': result.get('domain', ''),
                        'url': url
                    },
                    'available': True,
                    'timestamp': time.time()
                }
                
        except Exception as e:
            logger.error(f"[ARTICLE_EXTRACTOR v10.0] ❌ Exception: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'service': self.service_name,
                'success': False,
                'error': str(e),
                'data': {},
                'available': True,
                'timestamp': time.time()
            }


logger.info("[ARTICLE_EXTRACTOR v10.0] Module loaded - ScraperAPI priority + user prompts")
print("[ARTICLE_EXTRACTOR v10.0] Ready - tries ScraperAPI first, prompts user on failure", file=sys.stderr)
