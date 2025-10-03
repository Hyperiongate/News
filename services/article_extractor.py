"""
Article Extractor Service - COMPLETE PRODUCTION FIX v8.0
Date Created: October 2, 2025
Last Modified: October 3, 2025 

CHANGES IN v8.0 (October 3, 2025):
1. Fixed ABC News extraction - they block ScraperAPI, using direct fetch
2. CRITICAL FIX: Ensures 'domain' and 'url' are passed in data dict for source_credibility
3. Enhanced BeautifulSoup extraction with better content detection
4. Added multiple fallback methods when primary extraction fails
5. Improved author extraction for multi-author articles
6. Better handling of sites that block automated access
7. ALL ORIGINAL FUNCTIONALITY PRESERVED - this is the complete file

PREVIOUS CHANGES (v7.0):
- Added specific handling for ABC News
- Added site-specific extraction logic
- Improved author extraction for multi-author articles
- Added better fallback for sites that block scrapers
- Added direct fetch option for problematic sites
- Better error handling and logging for debugging

This is the COMPLETE file - replaces services/article_extractor.py entirely
No functionality has been removed, only enhanced and fixed.
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
print(f"[ARTICLE_EXTRACTOR v8.0] Loading article_extractor.py with ABC News fixes and domain passing...", file=sys.stderr)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress noisy loggers
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('newspaper').setLevel(logging.WARNING)

# Log that we're loading
logger.info("[ARTICLE_EXTRACTOR v8.0] Module loading started with ABC News handling and domain fix...")


class ArticleExtractorCore:
    """Core extraction logic with site-specific handling and complete functionality"""
    
    VERSION = "8.0"
    
    # Sites that should NOT use ScraperAPI (they block it)
    DIRECT_FETCH_SITES = [
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
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
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
        """Extract article from URL with site-specific handling and multiple fallback methods"""
        logger.info(f"[EXTRACTOR v{self.VERSION}] Extracting from URL: {url}")
        
        # Check cache
        cache_key = self._get_cache_key(url)
        if cache_key in self._cache:
            cache_entry = self._cache[cache_key]
            if time.time() - cache_entry['timestamp'] < self._cache_ttl:
                logger.info("Returning cached article")
                return cache_entry['data']
        
        # Clean URL (remove tracking parameters for ABC News)
        clean_url = self._clean_url(url)
        domain = urlparse(clean_url).netloc.replace('www.', '')
        
        # Determine extraction strategy based on site
        should_use_scraperapi = use_scraperapi and self.scraperapi_key and domain not in self.DIRECT_FETCH_SITES
        
        result = None
        
        # Special handling for ABC News
        if 'abcnews' in domain:
            logger.info(f"[EXTRACTOR] Detected ABC News - using special handler")
            result = self._extract_abc_news(clean_url)
            if result and result.get('success'):
                logger.info(f"✓ ABC News extraction successful - {result.get('word_count', 0)} words")
                self._cache_result(cache_key, result)
                return result
        
        # Method 1: ScraperAPI (skip for problematic sites)
        if should_use_scraperapi:
            result = self._extract_with_scraperapi(clean_url)
            if result and result.get('success'):
                logger.info(f"✓ ScraperAPI extraction successful - {result.get('word_count', 0)} words")
                self._cache_result(cache_key, result)
                return result
        
        # Method 2: Direct fetch with BeautifulSoup
        result = self._extract_with_beautifulsoup(clean_url)
        if result and result.get('success'):
            logger.info(f"✓ BeautifulSoup extraction successful - {result.get('word_count', 0)} words")
            self._cache_result(cache_key, result)
            return result
        
        # Method 3: Newspaper3k
        result = self._extract_with_newspaper(clean_url)
        if result and result.get('success'):
            logger.info(f"✓ Newspaper extraction successful - {result.get('word_count', 0)} words")
            self._cache_result(cache_key, result)
            return result
        
        # All methods failed
        logger.error(f"All extraction methods failed for {url}")
        return self._create_error_response(url, "All extraction methods failed")
    
    def _clean_url(self, url: str) -> str:
        """Clean URL by removing tracking parameters"""
        if 'abcnews' in url:
            # Remove query parameters that might confuse scrapers
            base_url = url.split('?')[0]
            return base_url
        return url
    
    def _extract_abc_news(self, url: str) -> Dict[str, Any]:
        """Special handler for ABC News which blocks most scrapers"""
        try:
            logger.info("[ABC NEWS] Starting special extraction...")
            
            # Try different user agents if first fails
            for user_agent in self.user_agents:
                try:
                    headers = {
                        'User-Agent': user_agent,
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Cache-Control': 'max-age=0'
                    }
                    
                    response = self.session.get(url, headers=headers, timeout=15, allow_redirects=True)
                    
                    if response.status_code == 200:
                        html = response.text
                        
                        # Check if we got a real article (not error page)
                        if 'Oops' in html[:1000] or '404' in html[:1000]:
                            logger.warning("[ABC NEWS] Got error page, trying alternative approach")
                            continue
                        
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # ABC News specific selectors
                        title = None
                        title_elem = soup.find('h1') or soup.find('meta', property='og:title')
                        if title_elem:
                            if title_elem.name == 'meta':
                                title = title_elem.get('content', '')
                            else:
                                title = title_elem.get_text(strip=True)
                        
                        # Extract authors - ABC News specific
                        authors = []
                        
                        # Method 1: Look for byline
                        byline = soup.find('div', class_='byline') or soup.find('span', class_='byline')
                        if byline:
                            byline_text = byline.get_text(strip=True)
                            # Parse "By Author1, Author2, and Author3"
                            byline_text = re.sub(r'^By\s+', '', byline_text, flags=re.IGNORECASE)
                            # Split on commas and "and"
                            author_parts = re.split(r',\s*and\s*|,\s*', byline_text)
                            authors = [a.strip() for a in author_parts if a.strip() and len(a.strip()) > 2]
                        
                        # Method 2: Check meta tags
                        if not authors:
                            author_meta = soup.find('meta', {'name': 'author'}) or soup.find('meta', {'property': 'article:author'})
                            if author_meta:
                                author_text = author_meta.get('content', '')
                                if author_text:
                                    authors = [author_text]
                        
                        # Method 3: Look for author links
                        if not authors:
                            author_links = soup.find_all('a', href=re.compile(r'/author/|/reporter/'))
                            authors = [a.get_text(strip=True) for a in author_links if a.get_text(strip=True)]
                        
                        # Extract content
                        content = ""
                        
                        # Try article body first
                        article_body = soup.find('div', class_='article-body') or \
                                      soup.find('div', {'data-component': 'ArticleBody'}) or \
                                      soup.find('section', class_='content')
                        
                        if article_body:
                            paragraphs = article_body.find_all('p')
                            content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                        
                        # Fallback to all paragraphs
                        if not content or len(content) < 200:
                            all_paragraphs = soup.find_all('p')
                            text_parts = []
                            for p in all_paragraphs:
                                text = p.get_text(strip=True)
                                if text and len(text) > 30:
                                    # Skip navigation/footer paragraphs
                                    if any(skip in text.lower() for skip in ['cookie', 'privacy', 'terms of use', 'subscribe']):
                                        continue
                                    text_parts.append(text)
                            
                            if text_parts:
                                content = '\n\n'.join(text_parts[:50])
                        
                        if content and len(content) > 200:
                            # Clean up authors
                            if authors:
                                authors = [self._clean_author_name(a) for a in authors]
                                authors = [a for a in authors if a != "Unknown Author"]
                            
                            logger.info(f"[ABC NEWS] Extraction successful - {len(content.split())} words, Authors: {authors}")
                            
                            return self._prepare_article_result(
                                url=url,
                                title=title or "ABC News Article",
                                text=content,
                                authors=authors if authors else ["ABC News"],
                                extraction_method='abc_news_special'
                            )
                
                except requests.exceptions.RequestException as e:
                    logger.warning(f"[ABC NEWS] Request failed with user agent {user_agent[:30]}...: {e}")
                    continue
            
            # All attempts failed
            logger.error("[ABC NEWS] All extraction attempts failed")
            return None
            
        except Exception as e:
            logger.error(f"[ABC NEWS] Extraction error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_with_scraperapi(self, url: str) -> Dict[str, Any]:
        """Extract using ScraperAPI (skip for problematic sites)"""
        try:
            logger.info("Trying ScraperAPI...")
            
            # Skip if site is in direct fetch list
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
            if 'Oops' in html_content[:1000] or '404' in html_content[:1000] or 'Page not found' in html_content[:1000]:
                logger.warning("ScraperAPI returned an error page")
                return None
            
            # Parse with newspaper
            article = Article(url)
            article.download(input_html=html_content)
            article.parse()
            
            if not article.text or len(article.text) < 100:
                return self._parse_html_content(html_content, url)
            
            return self._prepare_article_result(
                url=url,
                title=article.title,
                text=article.text,
                authors=article.authors,
                publish_date=article.publish_date,
                extraction_method='scraperapi'
            )
            
        except Exception as e:
            logger.error(f"ScraperAPI failed: {e}")
            return None
    
    def _extract_with_newspaper(self, url: str) -> Dict[str, Any]:
        """Extract using Newspaper3k library"""
        try:
            logger.info("Trying Newspaper3k...")
            
            article = Article(url)
            article.config.browser_user_agent = self.session.headers['User-Agent']
            article.config.request_timeout = 20
            
            article.download()
            article.parse()
            
            if not article.text or len(article.text) < 100:
                raise ArticleException("Article text too short")
            
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
    
    def _extract_with_beautifulsoup(self, url: str) -> Dict[str, Any]:
        """Extract using BeautifulSoup with better error handling"""
        try:
            logger.info("Trying BeautifulSoup direct fetch...")
            
            # Use rotating user agents
            for user_agent in self.user_agents:
                try:
                    headers = {'User-Agent': user_agent}
                    response = self.session.get(url, headers=headers, timeout=20)
                    
                    if response.status_code == 200:
                        html = response.text
                        
                        # Check for error pages
                        if 'Oops' in html[:1000] or '404' in html[:1000]:
                            continue
                        
                        result = self._parse_html_content(html, url)
                        if result and result.get('success'):
                            return result
                
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"BeautifulSoup failed: {e}")
            return None
    
    def _parse_html_content(self, html: str, url: str) -> Dict[str, Any]:
        """Parse HTML content with improved extraction"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unwanted elements
            for script in soup(["script", "style", "meta", "noscript", "header", "footer", "nav"]):
                script.decompose()
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract content
            content = self._extract_main_content(soup)
            
            # Extract author(s) - improved for multi-author articles
            authors = self._extract_authors(soup, html)
            
            # Extract date
            publish_date = self._extract_publish_date(soup, html)
            
            if not content or len(content) < 100:
                raise ValueError("Content too short")
            
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
                        # Skip common non-content text
                        if any(skip in text.lower()[:50] for skip in ['cookie', 'subscribe', 'newsletter', 'advertisement']):
                            continue
                        text_parts.append(text)
                
                if text_parts:
                    content = '\n\n'.join(text_parts)
                    if len(content) > 200:
                        return content
        
        # Fallback: all paragraphs
        all_paragraphs = soup.find_all('p')
        text_parts = []
        
        for p in all_paragraphs:
            text = p.get_text(strip=True)
            if text and len(text) > 30:
                # Skip footer/header content
                parent_class = str(p.parent.get('class', ''))
                if any(skip in parent_class.lower() for skip in ['footer', 'header', 'nav', 'sidebar']):
                    continue
                text_parts.append(text)
        
        if text_parts:
            return '\n\n'.join(text_parts[:50])
        
        return soup.get_text(separator='\n', strip=True)
    
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
                    # Handle "Author1, Author2, and Author3" format
                    author = re.sub(r'^By\s+', '', author, flags=re.IGNORECASE)
                    # Split on commas and "and"
                    parts = re.split(r',\s*and\s*|,\s*|\s+and\s+', author)
                    for part in parts:
                        clean = self._clean_author_name(part.strip())
                        if clean != "Unknown Author":
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
                        # Parse byline format
                        text = re.sub(r'^By\s+', '', text, flags=re.IGNORECASE)
                        parts = re.split(r',\s*and\s*|,\s*|\s+and\s+', text)
                        for part in parts:
                            clean = self._clean_author_name(part.strip())
                            if clean != "Unknown Author" and clean not in authors:
                                authors.append(clean)
        
        # JSON-LD
        if not authors:
            json_lds = soup.find_all('script', type='application/ld+json')
            for json_ld in json_lds:
                try:
                    data = json.loads(json_ld.string)
                    if isinstance(data, dict) and 'author' in data:
                        author_data = data['author']
                        if isinstance(author_data, list):
                            for author in author_data:
                                if isinstance(author, dict):
                                    name = author.get('name', '')
                                else:
                                    name = str(author)
                                if name:
                                    clean = self._clean_author_name(name)
                                    if clean != "Unknown Author":
                                        authors.append(clean)
                        elif isinstance(author_data, dict):
                            name = author_data.get('name', '')
                            if name:
                                clean = self._clean_author_name(name)
                                if clean != "Unknown Author":
                                    authors.append(clean)
                        else:
                            clean = self._clean_author_name(str(author_data))
                            if clean != "Unknown Author":
                                authors.append(clean)
                except:
                    continue
        
        # Remove duplicates while preserving order
        seen = set()
        unique_authors = []
        for author in authors:
            if author not in seen:
                seen.add(author)
                unique_authors.append(author)
        
        return unique_authors if unique_authors else ["Unknown Author"]
    
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
        """Clean author name with better handling"""
        if not author:
            return "Unknown Author"
        
        # Remove common prefixes
        author = re.sub(r'^(by|By|BY)\s+', '', author)
        author = re.sub(r'^(written by|Written by|WRITTEN BY)\s+', '', author, re.IGNORECASE)
        author = re.sub(r'^(reported by|Reported by)\s+', '', author, re.IGNORECASE)
        
        # Clean up
        author = re.sub(r'\s+', ' ', author)
        author = re.sub(r'[<>"]', '', author)
        author = author.strip()
        
        # Remove role descriptions
        author = re.sub(r'\s*,\s*(Reporter|Correspondent|Writer|Journalist|Editor).*$', '', author, re.IGNORECASE)
        
        # Validate
        if not author or len(author) < 2 or len(author) > 100:
            return "Unknown Author"
        
        # Check for obviously invalid names
        if author.lower() in ['staff', 'admin', 'administrator', 'editor', 'newsroom', 'wire', 'associated press']:
            return "Unknown Author"
        
        return author
    
    def _prepare_article_result(
        self, url: str, title: str, text: str,
        authors: Optional[List[str]] = None, publish_date: Optional[datetime] = None,
        summary: Optional[str] = None, html: Optional[str] = None,
        extraction_method: str = 'unknown'
    ) -> Dict[str, Any]:
        """Prepare final result with better author handling and CRITICAL domain/url fields"""
        
        title = self._clean_text(title) if title else "Unknown Title"
        text = self._clean_text(text) if text else ""
        
        # Process authors list
        if authors:
            authors = [self._clean_author_name(a) for a in authors if a]
            authors = [a for a in authors if a != "Unknown Author"]
        
        # If no valid authors found, use source name
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
        
        # Format author string (handle multiple authors)
        if len(authors) == 1:
            author = authors[0]
        elif len(authors) == 2:
            author = f"{authors[0]} and {authors[1]}"
        elif len(authors) > 2:
            author = f"{', '.join(authors[:-1])}, and {authors[-1]}"
        else:
            author = "Unknown Author"
        
        # CRITICAL: Extract domain for other services
        domain = urlparse(url).netloc.replace('www.', '')
        word_count = len(text.split()) if text else 0
        
        # Count sources and quotes for transparency analysis
        sources_count = self._count_sources(text)
        quotes_count = self._count_quotes(text)
        
        result = {
            'success': True,
            'url': url,  # CRITICAL: Include URL for source_credibility
            'domain': domain,  # CRITICAL: Include domain for source_credibility  
            'title': title,
            'text': text,
            'content': text,  # Duplicate for compatibility
            'author': author,  # Formatted string
            'authors': authors,  # List of authors
            'publish_date': publish_date.isoformat() if publish_date else None,
            'source': self._get_source_name(domain),  # Add source name
            'word_count': word_count,
            'extraction_method': extraction_method,
            'extracted_at': datetime.now().isoformat(),
            'version': self.VERSION,
            'sources_count': sources_count,  # For transparency analyzer
            'quotes_count': quotes_count,  # For transparency analyzer
            'extraction_successful': word_count > 100  # Mark as successful if we got meaningful content
        }
        
        if summary:
            result['summary'] = self._clean_text(summary)
        
        logger.info(f"[EXTRACTOR v{self.VERSION}] ✓ Extracted: {title[:50]}... ({word_count} words) by {author}")
        logger.info(f"[EXTRACTOR v{self.VERSION}] Domain: {domain}, URL: {url[:50]}...")
        
        return result
    
    def _count_sources(self, text: str) -> int:
        """Count number of sources cited in article"""
        if not text:
            return 0
            
        source_patterns = [
            r'according to',
            r'said',
            r'reported',
            r'stated',
            r'told',
            r'confirmed',
            r'announced'
        ]
        
        count = 0
        for pattern in source_patterns:
            count += len(re.findall(pattern, text, re.IGNORECASE))
        
        return min(count, 20)  # Cap at 20 to avoid inflated counts
    
    def _count_quotes(self, text: str) -> int:
        """Count number of direct quotes in article"""
        if not text:
            return 0
            
        # Find quoted text that's at least 10 characters long
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
        """Create error response with proper structure"""
        domain = urlparse(url).netloc.replace('www.', '') if url else ''
        
        return {
            'success': False,
            'url': url,
            'domain': domain,  # Still include domain even on error
            'title': 'Unknown',
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
        
        # Limit cache size
        if len(self._cache) > 100:
            # Remove oldest entries
            sorted_items = sorted(
                self._cache.items(),
                key=lambda x: x[1]['timestamp']
            )
            self._cache = dict(sorted_items[-50:])
    
    def process_text_input(self, text: str, source: str = "direct_input") -> Dict[str, Any]:
        """Process direct text input (when user provides text instead of URL)"""
        logger.info(f"[EXTRACTOR v{self.VERSION}] Processing text input ({len(text)} chars)")
        
        lines = text.strip().split('\n')
        title = lines[0][:100] if lines else "Direct Text Input"
        cleaned_text = self._clean_text(text)
        
        # Count sources and quotes
        sources_count = self._count_sources(cleaned_text)
        quotes_count = self._count_quotes(cleaned_text)
        
        return {
            'success': True,
            'url': source,
            'domain': 'text_input',  # Special domain for text input
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
    """
    Main class that service_registry expects
    CRITICAL: Must be named exactly 'ArticleExtractor'
    CRITICAL: Must take NO arguments in __init__
    CRITICAL: Must have analyze() method that works with pipeline
    """
    
    def __init__(self):
        """Initialize - NO ARGUMENTS as per service_registry requirements"""
        self.core = ArticleExtractorCore()
        self.is_available = True  # Required by service_registry
        self.service_name = 'article_extractor'  # Add service name
        logger.info(f"[ARTICLE_EXTRACTOR v8.0] ArticleExtractor initialized with ABC News fixes and domain passing")
        print("[ARTICLE_EXTRACTOR v8.0] Service ready with site-specific handlers and domain fix", file=sys.stderr)
    
    def _check_availability(self) -> bool:
        """Check if service is available - required by BaseAnalyzer"""
        return True
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method called by the pipeline
        MUST handle both URL and text input
        MUST return in exact format expected by pipeline
        CRITICAL: Must include domain and url in data for other services
        """
        logger.info(f"[ARTICLE_EXTRACTOR v8.0] analyze() called with keys: {list(data.keys())}")
        
        # Determine input type
        url = data.get('url', '')
        text = data.get('text', '') or data.get('content', '')
        
        try:
            # Handle URL input
            if url and url.startswith('http'):
                logger.info(f"[ARTICLE_EXTRACTOR v8.0] Extracting from URL: {url}")
                result = self.core.extract(url)
            # Handle text input
            elif text:
                logger.info(f"[ARTICLE_EXTRACTOR v8.0] Processing text input: {len(text)} chars")
                result = self.core.process_text_input(text)
            else:
                logger.error("[ARTICLE_EXTRACTOR v8.0] No valid URL or text provided")
                return {
                    'service': self.service_name,
                    'success': False,
                    'error': 'No URL or text provided',
                    'data': {
                        'text': '',
                        'title': 'Unknown',
                        'author': 'Unknown',
                        'domain': '',
                        'url': '',
                        'content': '',
                        'source': '',
                        'sources_count': 0,
                        'quotes_count': 0
                    },
                    'available': True,
                    'timestamp': time.time()
                }
            
            # Format response for pipeline - CRITICAL: include all needed fields
            if result.get('success'):
                logger.info(f"[ARTICLE_EXTRACTOR v8.0] SUCCESS - Extracted {result.get('word_count', 0)} words from {result.get('extraction_method')}")
                logger.info(f"[ARTICLE_EXTRACTOR v8.0] Authors: {result.get('authors', [])}")
                logger.info(f"[ARTICLE_EXTRACTOR v8.0] Domain: {result.get('domain')}, URL: {result.get('url', '')[:50]}...")
                
                # CRITICAL: Ensure all fields are in data dict for other services
                response_data = {
                    'text': result.get('text', ''),
                    'content': result.get('text', ''),  # Duplicate for compatibility
                    'title': result.get('title', 'Unknown'),
                    'author': result.get('author', 'Unknown'),
                    'authors': result.get('authors', []),
                    'domain': result.get('domain', ''),  # CRITICAL for source_credibility
                    'url': url or result.get('url', ''),  # CRITICAL for source_credibility
                    'source': result.get('source', ''),
                    'word_count': result.get('word_count', 0),
                    'extraction_method': result.get('extraction_method', 'unknown'),
                    'publish_date': result.get('publish_date'),
                    'sources_count': result.get('sources_count', 0),  # For transparency
                    'quotes_count': result.get('quotes_count', 0),  # For transparency
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
                logger.error(f"[ARTICLE_EXTRACTOR v8.0] FAILED - {result.get('error', 'Unknown error')}")
                
                # Even on failure, provide whatever we have
                return {
                    'service': self.service_name,
                    'success': False,
                    'error': result.get('error', 'Extraction failed'),
                    'data': {
                        'text': result.get('text', ''),
                        'content': result.get('content', ''),
                        'title': result.get('title', 'Unknown'),
                        'author': result.get('author', 'Unknown'),
                        'domain': result.get('domain', ''),  # Include domain even on failure
                        'url': url or result.get('url', ''),
                        'source': result.get('source', ''),
                        'sources_count': 0,
                        'quotes_count': 0,
                        'extraction_successful': False
                    },
                    'available': True,
                    'timestamp': time.time()
                }
                
        except Exception as e:
            logger.error(f"[ARTICLE_EXTRACTOR v8.0] Exception in analyze: {e}")
            import traceback
            traceback.print_exc()
            
            # Return valid response even on exception
            return {
                'service': self.service_name,
                'success': False,
                'error': str(e),
                'data': {
                    'text': '',
                    'content': '',
                    'title': 'Unknown',
                    'author': 'Unknown',
                    'domain': '',
                    'url': url,
                    'source': '',
                    'sources_count': 0,
                    'quotes_count': 0,
                    'extraction_successful': False
                },
                'available': True,
                'timestamp': time.time()
            }
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information - required by service registry"""
        return {
            'name': self.service_name,
            'version': '8.0',
            'available': self.is_available,
            'description': 'Extracts article content with ABC News and multi-author support, ensures domain/url passing',
            'scraperapi_configured': bool(self.core.scraperapi_key),
            'special_handlers': ['ABC News', 'Multi-author extraction', 'Domain/URL passing fix']
        }


# Module-level diagnostic
logger.info("[ARTICLE_EXTRACTOR v8.0] Module loaded with ABC News fixes and domain passing")
print("[ARTICLE_EXTRACTOR v8.0] Module ready - ABC News handler active, domain fix applied", file=sys.stderr)


# Test function for development
if __name__ == "__main__":
    print("\n" + "="*80)
    print("TESTING ARTICLE EXTRACTOR v8.0 - ABC NEWS FIX + DOMAIN PASSING")
    print("="*80)
    
    # Test instantiation
    print("\n1. Testing ArticleExtractor instantiation...")
    try:
        extractor = ArticleExtractor()
        print("   ✓ ArticleExtractor created successfully")
        print(f"   ✓ Available: {extractor.is_available}")
    except Exception as e:
        print(f"   ✗ Failed to create ArticleExtractor: {e}")
        sys.exit(1)
    
    # Test with ABC News URL if provided
    test_urls = [
        "https://abcnews.go.com/Politics/speaker-mike-johnson-win-government-funding-fight-democrats/story?id=114334651",
        "https://www.bbc.com/news/articles/c8xp0nkwgrgo",
        "https://www.reuters.com/"
    ]
    
    for test_url in test_urls[:1]:  # Test just the first URL
        print(f"\n2. Testing extraction: {test_url[:60]}...")
        
        result = extractor.analyze({'url': test_url})
        
        if result['success']:
            data = result['data']
            print(f"   ✓ Extraction successful via {data.get('extraction_method', 'unknown')}")
            print(f"   ✓ Title: {data['title'][:60]}...")
            print(f"   ✓ Author(s): {data.get('authors', [data['author']])}")
            print(f"   ✓ Domain: {data['domain']}")  # Check domain is present
            print(f"   ✓ URL: {data['url'][:50]}...")  # Check URL is present
            print(f"   ✓ Word Count: {data['word_count']}")
            print(f"   ✓ Sources: {data.get('sources_count', 0)}, Quotes: {data.get('quotes_count', 0)}")
            print(f"   ✓ Text preview: {data['text'][:100]}...")
        else:
            print(f"   ✗ Extraction failed: {result.get('error')}")
            print(f"   Data provided: {list(result.get('data', {}).keys())}")
    
    print("\n" + "="*80)
    print("TESTING COMPLETE - Check that domain and url are in data dict")
    print("="*80)
