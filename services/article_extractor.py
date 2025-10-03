"""
Article Extractor Service - PRODUCTION FIX v9.0
Date Created: October 2, 2025
Last Modified: October 3, 2025

CHANGES IN v9.0 (October 3, 2025):
1. CRITICAL FIX: Properly validates extraction success - requires minimum 200 chars of text
2. CRITICAL FIX: Returns success=False when extraction actually fails
3. Better error handling for ABC News and other blocked sites
4. Enhanced logging to clearly show when extraction fails
5. Improved fallback handling - doesn't claim success on failure
6. Added retry logic with multiple user agents
7. Better detection of blocked/error pages

This fixes the bug where extractor claimed success with only URL (112 chars).
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

# CRITICAL DIAGNOSTIC: Confirm this file is loading
print(f"[ARTICLE_EXTRACTOR v9.0] Loading with proper failure detection...", file=sys.stderr)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress noisy loggers
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('newspaper').setLevel(logging.WARNING)

logger.info("[ARTICLE_EXTRACTOR v9.0] Module loading with proper success validation...")


class ArticleExtractorCore:
    """Core extraction logic with proper failure detection"""
    
    VERSION = "9.0"
    MIN_VALID_TEXT_LENGTH = 200  # Minimum characters for valid article
    
    # Sites that should NOT use ScraperAPI (they block it)
    DIRECT_FETCH_SITES = [
        'abcnews.go.com',
        'abc.net.au',
        'washingtonpost.com',
        'wsj.com',
        'ft.com'
    ]
    
    def __init__(self):
        """Initialize the article extractor with API keys and session management"""
        self.scraperapi_key = os.environ.get('SCRAPERAPI_KEY', '')
        self.session = requests.Session()
        
        # Rotate user agents for better success
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
        
        logger.info(f"[EXTRACTOR v{self.VERSION}] Core initialized - ScraperAPI: {bool(self.scraperapi_key)}")
    
    def extract(self, url: str, use_scraperapi: bool = True) -> Dict[str, Any]:
        """Extract article from URL with proper validation"""
        logger.info(f"[EXTRACTOR v{self.VERSION}] Extracting from URL: {url}")
        
        # Check cache
        cache_key = self._get_cache_key(url)
        if cache_key in self._cache:
            cache_entry = self._cache[cache_key]
            if time.time() - cache_entry['timestamp'] < self._cache_ttl:
                logger.info("Returning cached article")
                return cache_entry['data']
        
        # Clean URL (remove tracking parameters)
        clean_url = self._clean_url(url)
        domain = urlparse(clean_url).netloc.replace('www.', '')
        
        # Determine extraction strategy based on site
        should_use_scraperapi = use_scraperapi and self.scraperapi_key and domain not in self.DIRECT_FETCH_SITES
        
        result = None
        
        # Special handling for ABC News
        if 'abcnews' in domain:
            logger.info(f"[EXTRACTOR] Detected ABC News - using special handler")
            result = self._extract_abc_news(clean_url)
            if result and self._is_valid_extraction(result):
                logger.info(f"✓ ABC News extraction successful - {result.get('word_count', 0)} words")
                self._cache_result(cache_key, result)
                return result
            logger.warning("ABC News extraction failed or returned insufficient content")
        
        # Method 1: ScraperAPI (skip for problematic sites)
        if should_use_scraperapi:
            result = self._extract_with_scraperapi(clean_url)
            if result and self._is_valid_extraction(result):
                logger.info(f"✓ ScraperAPI extraction successful - {result.get('word_count', 0)} words")
                self._cache_result(cache_key, result)
                return result
        
        # Method 2: Direct fetch with BeautifulSoup
        result = self._extract_with_beautifulsoup(clean_url)
        if result and self._is_valid_extraction(result):
            logger.info(f"✓ BeautifulSoup extraction successful - {result.get('word_count', 0)} words")
            self._cache_result(cache_key, result)
            return result
        
        # Method 3: Newspaper3k
        result = self._extract_with_newspaper(clean_url)
        if result and self._is_valid_extraction(result):
            logger.info(f"✓ Newspaper extraction successful - {result.get('word_count', 0)} words")
            self._cache_result(cache_key, result)
            return result
        
        # All methods failed - return proper failure response
        logger.error(f"❌ All extraction methods failed for {url}")
        logger.error(f"❌ Could not extract sufficient content (minimum {self.MIN_VALID_TEXT_LENGTH} chars required)")
        return self._create_error_response(url, "All extraction methods failed - site may be blocking access")
    
    def _is_valid_extraction(self, result: Dict[str, Any]) -> bool:
        """Validate that extraction actually succeeded with real content"""
        if not result:
            return False
        
        if not result.get('success'):
            return False
        
        text = result.get('text', '')
        if not text or len(text) < self.MIN_VALID_TEXT_LENGTH:
            logger.warning(f"Extraction returned insufficient text: {len(text)} chars (minimum {self.MIN_VALID_TEXT_LENGTH})")
            return False
        
        # Check if it's just the URL repeated
        url = result.get('url', '')
        if text.strip() == url.strip():
            logger.warning("Extraction returned only the URL, not actual content")
            return False
        
        return True
    
    def _clean_url(self, url: str) -> str:
        """Clean URL by removing tracking parameters"""
        if 'abcnews' in url:
            base_url = url.split('?')[0]
            return base_url
        return url
    
    def _extract_abc_news(self, url: str) -> Optional[Dict[str, Any]]:
        """Special handler for ABC News which blocks most scrapers"""
        try:
            logger.info("[ABC NEWS] Starting special extraction...")
            
            # Try different user agents
            for idx, user_agent in enumerate(self.user_agents):
                try:
                    logger.info(f"[ABC NEWS] Attempt {idx + 1} with user agent {idx + 1}")
                    
                    headers = {
                        'User-Agent': user_agent,
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Cache-Control': 'max-age=0',
                        'Referer': 'https://www.google.com/'
                    }
                    
                    response = self.session.get(url, headers=headers, timeout=15, allow_redirects=True)
                    
                    if response.status_code == 200:
                        html = response.text
                        
                        # Check if we got a real article (not error page)
                        if any(error_indicator in html[:1000] for error_indicator in ['Oops', '404', 'Page Not Found', 'Access Denied']):
                            logger.warning(f"[ABC NEWS] Got error page on attempt {idx + 1}")
                            continue
                        
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract title
                        title = None
                        title_elem = soup.find('h1') or soup.find('meta', property='og:title')
                        if title_elem:
                            if title_elem.name == 'meta':
                                title = title_elem.get('content', '')
                            else:
                                title = title_elem.get_text(strip=True)
                        
                        # Extract authors
                        authors = self._extract_authors(soup, html)
                        
                        # Extract content - try multiple methods
                        content = ""
                        
                        # Method 1: Article body
                        article_body = soup.find('div', class_='article-body') or \
                                      soup.find('div', {'data-component': 'ArticleBody'}) or \
                                      soup.find('section', class_='content') or \
                                      soup.find('article')
                        
                        if article_body:
                            paragraphs = article_body.find_all('p')
                            content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30])
                        
                        # Method 2: Fallback to all meaningful paragraphs
                        if len(content) < self.MIN_VALID_TEXT_LENGTH:
                            all_paragraphs = soup.find_all('p')
                            text_parts = []
                            for p in all_paragraphs:
                                text = p.get_text(strip=True)
                                if text and len(text) > 30:
                                    # Skip navigation/footer paragraphs
                                    if any(skip in text.lower() for skip in ['cookie', 'privacy', 'terms of use', 'subscribe', 'newsletter']):
                                        continue
                                    text_parts.append(text)
                            
                            if text_parts:
                                content = '\n\n'.join(text_parts[:50])
                        
                        # Validate we got real content
                        if len(content) >= self.MIN_VALID_TEXT_LENGTH:
                            logger.info(f"[ABC NEWS] ✓ Extraction successful - {len(content.split())} words")
                            
                            return self._prepare_article_result(
                                url=url,
                                title=title or "ABC News Article",
                                text=content,
                                authors=authors if authors else ["ABC News"],
                                extraction_method='abc_news_special'
                            )
                        else:
                            logger.warning(f"[ABC NEWS] Insufficient content on attempt {idx + 1}: {len(content)} chars")
                
                except requests.exceptions.RequestException as e:
                    logger.warning(f"[ABC NEWS] Request failed on attempt {idx + 1}: {e}")
                    continue
            
            # All attempts failed
            logger.error("[ABC NEWS] ❌ All extraction attempts failed")
            return None
            
        except Exception as e:
            logger.error(f"[ABC NEWS] ❌ Extraction error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_with_scraperapi(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract using ScraperAPI"""
        try:
            logger.info("Trying ScraperAPI...")
            
            domain = urlparse(url).netloc.replace('www.', '')
            if domain in self.DIRECT_FETCH_SITES:
                logger.info(f"Skipping ScraperAPI for {domain}")
                return None
            
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
                raise ValueError("Empty content from ScraperAPI")
            
            # Check for error pages
            if any(error in html_content[:1000] for error in ['Oops', '404', 'Page not found', 'Access Denied']):
                logger.warning("ScraperAPI returned an error page")
                return None
            
            # Parse with newspaper
            article = Article(url)
            article.download(input_html=html_content)
            article.parse()
            
            if article.text and len(article.text) >= self.MIN_VALID_TEXT_LENGTH:
                return self._prepare_article_result(
                    url=url,
                    title=article.title,
                    text=article.text,
                    authors=article.authors,
                    publish_date=article.publish_date,
                    extraction_method='scraperapi'
                )
            
            # Try BeautifulSoup parsing as fallback
            return self._parse_html_content(html_content, url)
            
        except Exception as e:
            logger.error(f"ScraperAPI failed: {e}")
            return None
    
    def _extract_with_newspaper(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract using Newspaper3k library"""
        try:
            logger.info("Trying Newspaper3k...")
            
            article = Article(url)
            article.config.browser_user_agent = self.session.headers['User-Agent']
            article.config.request_timeout = 20
            
            article.download()
            article.parse()
            
            if not article.text or len(article.text) < self.MIN_VALID_TEXT_LENGTH:
                raise ArticleException(f"Article text too short: {len(article.text)} chars")
            
            # Try NLP features if available
            try:
                article.nlp()
            except:
                pass
            
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
            logger.error(f"Newspaper failed: {e}")
            return None
    
    def _extract_with_beautifulsoup(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract using BeautifulSoup with multiple user agents"""
        try:
            logger.info("Trying BeautifulSoup direct fetch...")
            
            # Use rotating user agents
            for user_agent in self.user_agents:
                try:
                    headers = {
                        'User-Agent': user_agent,
                        'Referer': 'https://www.google.com/'
                    }
                    response = self.session.get(url, headers=headers, timeout=20)
                    
                    if response.status_code == 200:
                        html = response.text
                        
                        # Check for error pages
                        if any(error in html[:1000] for error in ['Oops', '404', 'Access Denied']):
                            continue
                        
                        result = self._parse_html_content(html, url)
                        if result and self._is_valid_extraction(result):
                            return result
                
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"BeautifulSoup failed: {e}")
            return None
    
    def _parse_html_content(self, html: str, url: str) -> Optional[Dict[str, Any]]:
        """Parse HTML content with improved extraction"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unwanted elements
            for script in soup(["script", "style", "meta", "noscript", "header", "footer", "nav"]):
                script.decompose()
            
            # Extract components
            title = self._extract_title(soup)
            content = self._extract_main_content(soup)
            authors = self._extract_authors(soup, html)
            publish_date = self._extract_publish_date(soup, html)
            
            if not content or len(content) < self.MIN_VALID_TEXT_LENGTH:
                logger.warning(f"Parsed content too short: {len(content)} chars")
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
            'h1', 'h1.headline', 'h1.title', 'h1.entry-title',
            '[class*="headline"]', '[class*="title"]',
            'meta[property="og:title"]', 'meta[name="twitter:title"]', 'title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    title = element.get('content', '')
                else:
                    title = element.get_text(strip=True)
                
                if title and len(title) > 10:
                    return self._clean_text(title)
        
        return "Unknown Title"
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content with better filtering"""
        selectors = [
            'article', '[role="main"]', '[class*="content-body"]',
            '[class*="article-body"]', '[class*="entry-content"]',
            '[class*="post-content"]', 'div.content', 'div.story-body',
            'section.content', 'main'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                content_elem = elements[0]
                paragraphs = content_elem.find_all(['p', 'h2', 'h3', 'h4'])
                
                text_parts = []
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 20:
                        if any(skip in text.lower()[:50] for skip in ['cookie', 'subscribe', 'newsletter', 'advertisement']):
                            continue
                        text_parts.append(text)
                
                if text_parts:
                    content = '\n\n'.join(text_parts)
                    if len(content) >= self.MIN_VALID_TEXT_LENGTH:
                        return content
        
        # Fallback: all paragraphs
        all_paragraphs = soup.find_all('p')
        text_parts = []
        
        for p in all_paragraphs:
            text = p.get_text(strip=True)
            if text and len(text) > 30:
                parent_class = str(p.parent.get('class', ''))
                if any(skip in parent_class.lower() for skip in ['footer', 'header', 'nav', 'sidebar']):
                    continue
                text_parts.append(text)
        
        if text_parts:
            return '\n\n'.join(text_parts[:50])
        
        return ""
    
    def _extract_authors(self, soup: BeautifulSoup, html: str) -> List[str]:
        """Extract multiple authors from article"""
        authors = []
        
        # Meta tags
        meta_selectors = [
            'meta[name="author"]', 'meta[property="article:author"]',
            'meta[name="byl"]', 'meta[name="parsely-author"]'
        ]
        
        for selector in meta_selectors:
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
        
        # Common selectors
        if not authors:
            selectors = [
                '[class*="author-name"]', '[class*="by-author"]',
                '[class*="byline"]', '[rel="author"]', '.author',
                '.writer', 'span.by', '.contributor'
            ]
            
            for selector in selectors:
                elements = soup.find_all(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    if text and len(text) > 2:
                        text = re.sub(r'^By\s+', '', text, flags=re.IGNORECASE)
                        parts = re.split(r',\s*and\s*|,\s*|\s+and\s+', text)
                        for part in parts:
                            clean = self._clean_author_name(part.strip())
                            if clean != "Unknown Author" and clean not in authors:
                                authors.append(clean)
        
        return authors[:5] if authors else ["Unknown Author"]  # Limit to 5 authors
    
    def _extract_publish_date(self, soup: BeautifulSoup, html: str) -> Optional[datetime]:
        """Extract publish date from HTML"""
        meta_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="publish_date"]', 'meta[name="parsely-pub-date"]',
            'meta[name="date"]', 'meta[property="article:published"]'
        ]
        
        for selector in meta_selectors:
            element = soup.select_one(selector)
            if element:
                date_str = element.get('content', '')
                if date_str:
                    try:
                        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except:
                        continue
        
        time_element = soup.select_one('time[datetime]')
        if time_element:
            try:
                return datetime.fromisoformat(time_element['datetime'].replace('Z', '+00:00'))
            except:
                pass
        
        return None
    
    def _clean_text(self, text: str) -> str:
        """Clean text content"""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[\r\n\t]', ' ', text)
        return text.strip()
    
    def _clean_author_name(self, author: str) -> str:
        """Clean author name"""
        if not author:
            return "Unknown Author"
        
        author = re.sub(r'^(by|By|BY|written by|Written by|reported by|Reported by)\s+', '', author, re.IGNORECASE)
        author = re.sub(r'\s+', ' ', author)
        author = re.sub(r'[<>"]', '', author)
        author = author.strip()
        author = re.sub(r'\s*,\s*(Reporter|Correspondent|Writer|Journalist|Editor).*$', '', author, re.IGNORECASE)
        
        if not author or len(author) < 2 or len(author) > 100:
            return "Unknown Author"
        
        if author.lower() in ['staff', 'admin', 'administrator', 'editor', 'newsroom', 'wire', 'associated press']:
            return "Unknown Author"
        
        return author
    
    def _prepare_article_result(
        self, url: str, title: str, text: str,
        authors: Optional[List[str]] = None, publish_date: Optional[datetime] = None,
        summary: Optional[str] = None, html: Optional[str] = None,
        extraction_method: str = 'unknown'
    ) -> Dict[str, Any]:
        """Prepare final result with validation"""
        
        title = self._clean_text(title) if title else "Unknown Title"
        text = self._clean_text(text) if text else ""
        
        # Validate minimum text length
        if len(text) < self.MIN_VALID_TEXT_LENGTH:
            logger.warning(f"Text too short: {len(text)} chars (minimum {self.MIN_VALID_TEXT_LENGTH})")
        
        # Process authors
        if authors:
            authors = [self._clean_author_name(a) for a in authors if a]
            authors = [a for a in authors if a != "Unknown Author"]
        
        if not authors:
            domain = urlparse(url).netloc.replace('www.', '')
            if 'abc' in domain.lower():
                authors = ["ABC News"]
            elif 'bbc' in domain.lower():
                authors = ["BBC News"]
            elif 'cnn' in domain.lower():
                authors = ["CNN"]
            else:
                authors = ["Unknown Author"]
        
        # Format author string
        if len(authors) == 1:
            author = authors[0]
        elif len(authors) == 2:
            author = f"{authors[0]} and {authors[1]}"
        elif len(authors) > 2:
            author = f"{', '.join(authors[:-1])}, and {authors[-1]}"
        else:
            author = "Unknown Author"
        
        domain = urlparse(url).netloc.replace('www.', '')
        word_count = len(text.split()) if text else 0
        
        sources_count = self._count_sources(text)
        quotes_count = self._count_quotes(text)
        
        # CRITICAL: Mark as successful only if we have real content
        extraction_successful = word_count > 50 and len(text) >= self.MIN_VALID_TEXT_LENGTH
        
        result = {
            'success': extraction_successful,  # CRITICAL: Only True if we got real content
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
            'sources_count': sources_count,
            'quotes_count': quotes_count,
            'extraction_successful': extraction_successful
        }
        
        if summary:
            result['summary'] = self._clean_text(summary)
        
        if extraction_successful:
            logger.info(f"[EXTRACTOR v{self.VERSION}] ✓ Extracted: {title[:50]}... ({word_count} words)")
        else:
            logger.warning(f"[EXTRACTOR v{self.VERSION}] ⚠ Extraction incomplete: only {word_count} words")
        
        return result
    
    def _count_sources(self, text: str) -> int:
        """Count number of sources cited"""
        if not text:
            return 0
        source_patterns = [
            r'according to', r'said', r'reported', r'stated',
            r'told', r'confirmed', r'announced'
        ]
        count = sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in source_patterns)
        return min(count, 20)
    
    def _count_quotes(self, text: str) -> int:
        """Count number of direct quotes"""
        if not text:
            return 0
        quotes = re.findall(r'"[^"]{10,}"', text)
        return len(quotes)
    
    def _get_source_name(self, domain: str) -> str:
        """Get readable source name from domain"""
        source_map = {
            'nytimes.com': 'The New York Times',
            'washingtonpost.com': 'The Washington Post',
            'wsj.com': 'The Wall Street Journal',
            'bbc.com': 'BBC',
            'bbc.co.uk': 'BBC',
            'cnn.com': 'CNN',
            'foxnews.com': 'Fox News',
            'reuters.com': 'Reuters',
            'apnews.com': 'Associated Press',
            'abcnews.go.com': 'ABC News',
            'nbcnews.com': 'NBC News',
            'cbsnews.com': 'CBS News',
            'npr.org': 'NPR',
            'politico.com': 'Politico',
            'thehill.com': 'The Hill',
            'axios.com': 'Axios'
        }
        return source_map.get(domain, domain.replace('.com', '').replace('.org', '').title())
    
    def _create_error_response(self, url: str, error_message: str) -> Dict[str, Any]:
        """Create error response - CRITICAL: success is False"""
        domain = urlparse(url).netloc.replace('www.', '') if url else ''
        
        return {
            'success': False,  # CRITICAL: This must be False
            'url': url,
            'domain': domain,
            'title': 'Extraction Failed',
            'text': '',
            'content': '',
            'author': 'Unknown',
            'authors': [],
            'error': error_message,
            'extraction_method': 'none',
            'version': self.VERSION,
            'extracted_at': datetime.now().isoformat(),
            'source': self._get_source_name(domain) if domain else 'Unknown',
            'word_count': 0,
            'sources_count': 0,
            'quotes_count': 0,
            'extraction_successful': False
        }
    
    def _get_cache_key(self, url: str) -> str:
        """Generate cache key for URL"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def _cache_result(self, key: str, result: Dict[str, Any]) -> None:
        """Cache extraction result"""
        self._cache[key] = {
            'data': result,
            'timestamp': time.time()
        }
        
        if len(self._cache) > 100:
            sorted_items = sorted(self._cache.items(), key=lambda x: x[1]['timestamp'])
            self._cache = dict(sorted_items[-50:])
    
    def process_text_input(self, text: str, source: str = "direct_input") -> Dict[str, Any]:
        """Process direct text input"""
        logger.info(f"[EXTRACTOR v{self.VERSION}] Processing text input ({len(text)} chars)")
        
        lines = text.strip().split('\n')
        title = lines[0][:100] if lines else "Direct Text Input"
        cleaned_text = self._clean_text(text)
        
        sources_count = self._count_sources(cleaned_text)
        quotes_count = self._count_quotes(cleaned_text)
        
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
            'sources_count': sources_count,
            'quotes_count': quotes_count,
            'extraction_successful': True
        }


class ArticleExtractor:
    """Main class for service registry"""
    
    def __init__(self):
        """Initialize"""
        self.core = ArticleExtractorCore()
        self.is_available = True
        self.service_name = 'article_extractor'
        self.scraperapi_key = self.core.scraperapi_key
        logger.info(f"[ARTICLE_EXTRACTOR v9.0] Initialized with proper failure detection")
    
    def _check_availability(self) -> bool:
        """Check if service is available"""
        return True
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Main analysis method"""
        logger.info(f"[ARTICLE_EXTRACTOR v9.0] analyze() called with keys: {list(data.keys())}")
        
        url = data.get('url', '')
        text = data.get('text', '') or data.get('content', '')
        
        try:
            # Handle URL input
            if url and url.startswith('http'):
                logger.info(f"[ARTICLE_EXTRACTOR v9.0] Extracting from URL: {url}")
                result = self.core.extract(url)
            # Handle text input
            elif text:
                logger.info(f"[ARTICLE_EXTRACTOR v9.0] Processing text input: {len(text)} chars")
                result = self.core.process_text_input(text)
            else:
                logger.error("[ARTICLE_EXTRACTOR v9.0] No valid URL or text provided")
                return {
                    'service': self.service_name,
                    'success': False,
                    'error': 'No URL or text provided',
                    'data': {},
                    'available': True,
                    'timestamp': time.time()
                }
            
            # Format response
            if result.get('success'):
                logger.info(f"[ARTICLE_EXTRACTOR v9.0] ✓ SUCCESS - {result.get('word_count', 0)} words via {result.get('extraction_method')}")
                
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
                logger.error(f"[ARTICLE_EXTRACTOR v9.0] ❌ FAILED - {result.get('error', 'Unknown error')}")
                
                return {
                    'service': self.service_name,
                    'success': False,
                    'error': result.get('error', 'Extraction failed'),
                    'data': {},
                    'available': True,
                    'timestamp': time.time()
                }
                
        except Exception as e:
            logger.error(f"[ARTICLE_EXTRACTOR v9.0] ❌ Exception: {e}")
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
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        return {
            'name': self.service_name,
            'version': '9.0',
            'available': self.is_available,
            'description': 'Article extraction with proper failure detection',
            'scraperapi_configured': bool(self.scraperapi_key),
            'min_valid_length': ArticleExtractorCore.MIN_VALID_TEXT_LENGTH
        }


logger.info("[ARTICLE_EXTRACTOR v9.0] Module loaded with proper failure validation")
print("[ARTICLE_EXTRACTOR v9.0] Ready - validates extraction success properly", file=sys.stderr)
