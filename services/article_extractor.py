"""
Article Extractor - v18.1 ENHANCED DEBUGGING + MULTI-AUTHOR
Date: October 10, 2025
Last Updated: October 10, 2025

ENHANCEMENTS FROM v18.0:
✅ ADDED: Aggressive HTML debugging - logs actual byline HTML
✅ ADDED: Multi-author extraction - gets ALL authors, not just first
✅ ADDED: Newsweek-specific patterns for author links
✅ ADDED: Searches entire article for author links (not just byline div)
✅ ADDED: Returns comma-separated author names when multiple found

THE FIX:
User wants all 3 authors: "Jesus Mesa, Tom O'Connor, Jason Lemon"
Currently only getting first one.

NEW FEATURES:
1. Logs the actual HTML of byline elements (so we can see structure)
2. Looks for ALL <a> tags that might be author links
3. Joins multiple authors with ", "
4. Better Newsweek-specific detection

Save as: services/article_extractor.py (REPLACE existing file)
"""

import os
import re
import time
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup

# Import OpenAI if available
try:
    from openai import OpenAI
    openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    openai_available = True
except Exception as e:
    openai_client = None
    openai_available = False

logger = logging.getLogger(__name__)

# Known non-journalists to exclude
NON_JOURNALIST_NAMES = {
    "Donald Trump", "Joe Biden", "Kamala Harris", "Mike Pence", "Barack Obama",
    "Hillary Clinton", "Bernie Sanders", "Elizabeth Warren", "Nancy Pelosi",
    "Mitch McConnell", "Kevin McCarthy", "Chuck Schumer", "Ron DeSantis",
    "Gavin Newsom", "Greg Abbott", "Mike Johnson", "Hakeem Jeffries",
    "Elon Musk", "Bill Gates", "Jeff Bezos", "Mark Zuckerberg", "Warren Buffett",
    "Vladimir Putin", "Xi Jinping", "Kim Jong Un"
}


class ArticleExtractor:
    """
    Article extractor with enhanced debugging and multi-author support
    v18.1 - Debug logging + extracts all authors
    """
    
    def __init__(self):
        self.scraperapi_key = os.getenv('SCRAPERAPI_KEY', '').strip()
        self.session = requests.Session()
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        
        self.is_available = True
        self.service_name = 'article_extractor'
        self.available = True
        
        logger.info(f"[ArticleExtractor v18.1 DEBUG] Multi-author + HTML inspection - OpenAI: {openai_available}")
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Service interface"""
        
        url = data.get('url', '')
        text = data.get('text', '') or data.get('content', '')
        
        try:
            if url and url.startswith('http'):
                result = self.extract(url)
            elif text:
                result = self._process_text(text)
            else:
                return {
                    'service': self.service_name,
                    'success': False,
                    'error': 'No URL or text provided',
                    'data': {}
                }
            
            return {
                'service': self.service_name,
                'success': result.get('extraction_successful', False),
                'data': result,
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"[ArticleExtractor] analyze() error: {e}")
            return {
                'service': self.service_name,
                'success': False,
                'error': str(e),
                'data': {}
            }
    
    def extract(self, url: str) -> Dict[str, Any]:
        """Main extraction method"""
        
        logger.info(f"[ArticleExtractor v18.1] Extracting: {url}")
        
        # Try ScraperAPI first
        if self.scraperapi_key:
            try:
                html = self._fetch_with_scraperapi(url)
                if html:
                    result = self._parse_html(html, url)
                    if result['extraction_successful']:
                        return result
            except Exception as e:
                logger.error(f"[ScraperAPI] Error: {e}")
        
        # Fallback to direct fetch
        try:
            html = self._fetch_direct(url)
            if html:
                result = self._parse_html(html, url)
                if result['extraction_successful']:
                    return result
        except Exception as e:
            logger.error(f"[Direct] Error: {e}")
        
        # Failed
        return {
            'title': 'Extraction Failed',
            'author': 'Unknown',
            'text': '',
            'content': '',
            'source': self._get_source_from_url(url),
            'domain': urlparse(url).netloc.replace('www.', ''),
            'url': url,
            'word_count': 0,
            'extraction_successful': False,
            'sources_count': 0,
            'quotes_count': 0,
            'author_page_url': None,
            'author_page_urls': [],
            'error': 'Could not extract article'
        }
    
    def _fetch_with_scraperapi(self, url: str) -> Optional[str]:
        """Fetch using ScraperAPI"""
        
        api_url = 'http://api.scraperapi.com'
        params = {
            'api_key': self.scraperapi_key,
            'url': url,
            'render': 'false',
            'country_code': 'us'
        }
        
        try:
            response = requests.get(api_url, params=params, timeout=30)
            if response.status_code == 200 and len(response.text) > 100:
                return response.text
        except Exception as e:
            logger.error(f"[ScraperAPI] Failed: {e}")
        
        return None
    
    def _fetch_direct(self, url: str) -> Optional[str]:
        """Direct fetch fallback"""
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            logger.error(f"[Direct] Failed: {e}")
        
        return None
    
    def _parse_html(self, html: str, url: str) -> Dict[str, Any]:
        """Parse HTML with multi-author extraction and debugging"""
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
            tag.decompose()
        
        # Extract components
        title = self._extract_title(soup)
        text = self._extract_text(soup)
        
        # NEW v18.1: Extract author(s) AND author page URL(s) with debugging
        author, author_page_url, author_page_urls = self._extract_author_with_url_debug(soup, html, url, text)
        
        source = self._get_source_from_url(url)
        domain = urlparse(url).netloc.replace('www.', '')
        
        word_count = len(text.split()) if text else 0
        extraction_successful = len(text) > 200
        
        logger.info(f"[Parser] Title: {title[:50]}")
        logger.info(f"[Parser] Author: {author}")
        if author_page_url:
            logger.info(f"[Parser] Author Page: {author_page_url}")
        if len(author_page_urls) > 1:
            logger.info(f"[Parser] Multiple author pages: {len(author_page_urls)}")
        logger.info(f"[Parser] Words: {word_count}")
        
        return {
            'title': title,
            'author': author,
            'author_page_url': author_page_url,
            'author_page_urls': author_page_urls,
            'text': text,
            'content': text,
            'source': source,
            'domain': domain,
            'url': url,
            'word_count': word_count,
            'sources_count': self._count_sources(text),
            'quotes_count': self._count_quotes(text),
            'extraction_successful': extraction_successful,
            'extraction_method': 'scraperapi' if self.scraperapi_key else 'direct'
        }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title"""
        
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        title = soup.find('title')
        if title:
            return title.get_text().strip()
        
        return "Unknown Title"
    
    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract article text"""
        
        # Try article tag
        article = soup.find('article')
        if article:
            paragraphs = article.find_all('p')
            text = ' '.join([p.get_text().strip() for p in paragraphs])
            if len(text) > 200:
                return text
        
        # Try common containers
        for selector in ['main', '[role="main"]', '.article-body', '.story-body', '.content', '.entry-content']:
            container = soup.select_one(selector)
            if container:
                paragraphs = container.find_all('p')
                text = ' '.join([p.get_text().strip() for p in paragraphs])
                if len(text) > 200:
                    return text
        
        # Fallback
        paragraphs = soup.find_all('p')
        text = ' '.join([
            p.get_text().strip() 
            for p in paragraphs 
            if len(p.get_text().strip()) > 30
        ])
        
        return text
    
    def _extract_author_with_url_debug(self, soup: BeautifulSoup, html: str, url: str, article_text: str) -> tuple[str, Optional[str], List[str]]:
        """
        NEW v18.1: Extract author(s) with AGGRESSIVE DEBUGGING
        Returns: (author_names_comma_separated, primary_author_url, all_author_urls)
        """
        
        logger.info("=" * 70)
        logger.info("[AUTHOR v18.1 DEBUG] Starting multi-author extraction with HTML inspection")
        logger.info(f"[AUTHOR] URL: {url[:80]}")
        
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        domain = urlparse(url).netloc.replace('www.', '')
        
        # METHOD 1: Enhanced byline search with HTML debugging
        logger.info("[AUTHOR] METHOD 1: Enhanced byline link search with HTML inspection")
        
        # First, find ALL potential byline containers
        byline_selectors = [
            'byline', 'author', 'by-line', 'article-author', 'author-name',
            'post-author', 'entry-author', 'story-byline', 'contributor',
            'writer', 'reporter', 'author-info', 'article-byline', 'by_author',
            'article-meta', 'meta', 'authors'  # Added more generic ones
        ]
        
        all_byline_elements = []
        for selector_pattern in byline_selectors:
            elements = soup.find_all(class_=re.compile(selector_pattern, re.I))
            all_byline_elements.extend(elements)
            
            # Also try as tag name
            elements_by_tag = soup.find_all(selector_pattern)
            all_byline_elements.extend(elements_by_tag)
        
        logger.info(f"[AUTHOR DEBUG] Found {len(all_byline_elements)} potential byline elements")
        
        # DEBUG: Log the HTML of first few byline elements
        for i, element in enumerate(all_byline_elements[:5]):
            logger.info(f"[AUTHOR DEBUG] Byline element #{i+1}:")
            logger.info(f"[AUTHOR DEBUG]   Tag: {element.name}")
            logger.info(f"[AUTHOR DEBUG]   Classes: {element.get('class', [])}")
            logger.info(f"[AUTHOR DEBUG]   Text: {element.get_text().strip()[:100]}")
            logger.info(f"[AUTHOR DEBUG]   HTML: {str(element)[:300]}")
            
            # Look for links in this element
            links = element.find_all('a', href=True)
            logger.info(f"[AUTHOR DEBUG]   Found {len(links)} <a> tags")
            for j, link in enumerate(links):
                logger.info(f"[AUTHOR DEBUG]     Link #{j+1}: href='{link.get('href')}' text='{link.get_text().strip()}'")
        
        # Now try to extract author names and URLs
        author_data = []  # List of (name, url) tuples
        
        for element in all_byline_elements:
            # Look for <a> tags in this byline element
            author_links = element.find_all('a', href=True)
            
            for link in author_links:
                href = link.get('href', '')
                link_text = link.get_text().strip()
                
                # Check if this looks like an author link
                if self._is_author_profile_link(href, link_text):
                    author_name = self._clean_author_name(link_text)
                    
                    if self._is_valid_author_universal(author_name):
                        # Make URL absolute
                        if href.startswith('/'):
                            full_url = urljoin(base_url, href)
                        elif href.startswith('http'):
                            full_url = href
                        else:
                            full_url = urljoin(base_url, '/' + href)
                        
                        author_data.append((author_name, full_url))
                        logger.info(f"[AUTHOR DEBUG] ✓ Valid author found: {author_name} -> {full_url}")
        
        # If we found authors with links, return them!
        if author_data:
            # Join all author names with ", "
            all_names = ', '.join([name for name, url in author_data])
            primary_url = author_data[0][1]
            all_urls = [url for name, url in author_data]
            
            logger.info(f"[AUTHOR] ✓✓✓ Found {len(author_data)} author(s) with links:")
            logger.info(f"[AUTHOR]   Names: {all_names}")
            logger.info(f"[AUTHOR]   Primary URL: {primary_url}")
            logger.info("=" * 70)
            
            return all_names, primary_url, all_urls
        
        logger.info("[AUTHOR DEBUG] No author links found in byline elements")
        
        # METHOD 2: Search ENTIRE article for author links (sometimes not in byline div)
        logger.info("[AUTHOR] METHOD 2: Searching entire article for author links")
        
        # Get first 2000 characters of article (where authors usually appear)
        article_start = soup.find('article') or soup.find('main') or soup
        
        # Find ALL links in article start
        all_links = article_start.find_all('a', href=True, limit=50)  # First 50 links
        
        logger.info(f"[AUTHOR DEBUG] Checking {len(all_links)} links in article")
        
        for link in all_links:
            href = link.get('href', '')
            link_text = link.get_text().strip()
            
            # More aggressive author detection for Newsweek
            if '/author' in href.lower() or 'newsweek.com/authors/' in href.lower():
                author_name = self._clean_author_name(link_text)
                
                if self._is_valid_author_universal(author_name):
                    full_url = urljoin(base_url, href) if not href.startswith('http') else href
                    author_data.append((author_name, full_url))
                    logger.info(f"[AUTHOR DEBUG] ✓ Found author link: {author_name} -> {full_url}")
        
        if author_data:
            all_names = ', '.join([name for name, url in author_data])
            primary_url = author_data[0][1]
            all_urls = [url for name, url in author_data]
            
            logger.info(f"[AUTHOR] ✓✓✓ Found {len(author_data)} author(s) in article:")
            logger.info(f"[AUTHOR]   Names: {all_names}")
            logger.info(f"[AUTHOR]   Primary URL: {primary_url}")
            logger.info("=" * 70)
            
            return all_names, primary_url, all_urls
        
        logger.info("[AUTHOR DEBUG] No author links found anywhere in article")
        
        # METHOD 3: rel="author" links
        logger.info("[AUTHOR] METHOD 3: rel='author' links")
        author_rel_links = soup.find_all('a', rel='author', href=True)
        
        if author_rel_links:
            logger.info(f"[AUTHOR DEBUG] Found {len(author_rel_links)} rel='author' links")
            
            for link in author_rel_links:
                href = link.get('href', '')
                link_text = link.get_text().strip()
                author_name = self._clean_author_name(link_text)
                
                if self._is_valid_author_universal(author_name):
                    full_url = urljoin(base_url, href) if not href.startswith('http') else href
                    author_data.append((author_name, full_url))
            
            if author_data:
                all_names = ', '.join([name for name, url in author_data])
                primary_url = author_data[0][1]
                all_urls = [url for name, url in author_data]
                
                logger.info(f"[AUTHOR] ✓✓✓ rel='author' SUCCESS: {all_names}")
                logger.info("=" * 70)
                return all_names, primary_url, all_urls
        
        # FALLBACK: Use existing methods but try to get multiple authors from text
        logger.info("[AUTHOR] Falling back to text-based extraction")
        
        # Try AI first
        if openai_available and openai_client:
            logger.info("[AUTHOR] METHOD 4: AI extraction (can get multiple authors)")
            author = self._extract_with_ai_visual_multiauthor(soup.get_text()[:500], html, url)
            if author and author != 'Unknown':
                logger.info(f"[AUTHOR] ✓ AI SUCCESS: {author} (no URLs)")
                logger.info("=" * 70)
                return author, None, []
        
        # Try other fallback methods
        author = self._extract_author_fallback(soup, html, url, soup.get_text())
        
        if author and author != 'Unknown':
            logger.info(f"[AUTHOR] ✓ Fallback SUCCESS: {author} (no URLs)")
            logger.info("=" * 70)
            return author, None, []
        
        logger.warning("[AUTHOR] ❌ ALL METHODS FAILED")
        logger.info("=" * 70)
        return "Unknown", None, []
    
    def _is_author_profile_link(self, href: str, link_text: str) -> bool:
        """Check if a link looks like an author profile page"""
        if not href:
            return False
        
        href_lower = href.lower()
        
        # Common author URL patterns
        author_patterns = [
            '/author/', '/authors/', '/people/', '/staff/', '/writer/', '/writers/',
            '/contributor/', '/contributors/', '/journalist/', '/reporter/', '/profile/',
            '/person/', '/by/', '/byline/'
        ]
        
        # Check if href contains author patterns
        for pattern in author_patterns:
            if pattern in href_lower:
                return True
        
        # Additional check: If link text looks like a name (2-3 words, capitalized)
        words = link_text.split()
        if 2 <= len(words) <= 4:
            if all(word[0].isupper() for word in words if word):
                return True
        
        return False
    
    def _extract_with_ai_visual_multiauthor(self, visible_text: str, html: str, url: str) -> str:
        """AI extraction that can find multiple authors"""
        try:
            byline_area = visible_text[:500].strip()
            
            prompt = f"""Extract ALL author names from this article.

Article beginning:
{byline_area}

TASK: Find ALL journalists who wrote this article.

RULES:
1. Look for "By [Name]", "By [Name1], [Name2], and [Name3]"
2. Return ALL authors separated by ", " (comma space)
3. Examples:
   - "Jesus Mesa, Tom O'Connor, Jason Lemon" (3 authors)
   - "Mary Smith and John Doe" (2 authors)  
   - "Sarah Lee" (1 author)
4. Ignore politicians being quoted
5. Return ONLY the names, nothing else

All author names:"""
            
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": "You extract ALL article authors. Return names separated by commas."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                max_tokens=100,
                temperature=0.1
            )
            
            author = response.choices[0].message.content.strip()
            author = author.replace('Author:', '').replace('author:', '').strip().strip('"\'')
            
            if self._is_valid_author_universal(author):
                return author
            
            return "Unknown"
            
        except Exception as e:
            logger.error(f"[AI] Failed: {e}")
            return "Unknown"
    
    def _extract_author_fallback(self, soup: BeautifulSoup, html: str, url: str, visible_text: str) -> str:
        """Fallback methods for author extraction (without URL)"""
        
        # Meta tags
        meta_names = [
            'author', 'byl', 'DC.creator', 'article:author', 'sailthru.author',
            'parsely-author', 'twitter:creator', 'Article.Author', 'Author'
        ]
        for meta_name in meta_names:
            author_meta = soup.find('meta', {'name': meta_name}) or soup.find('meta', {'property': meta_name})
            if author_meta and author_meta.get('content'):
                author = self._clean_author_name(author_meta['content'])
                if self._is_valid_author_universal(author):
                    return author
        
        # JSON-LD
        author = self._extract_from_jsonld(soup)
        if author and author != 'Unknown':
            return author
        
        # Universal regex patterns
        author = self._extract_with_universal_patterns(visible_text)
        if author and author != 'Unknown':
            return author
        
        # Domain-specific
        domain = urlparse(url).netloc.replace('www.', '')
        author = self._extract_domain_specific(soup, html, domain)
        if author and author != 'Unknown':
            return author
        
        return "Unknown"
    
    def _extract_with_universal_patterns(self, visible_text: str) -> str:
        """Universal regex patterns for author extraction"""
        
        NAME_PART = r"[A-Z][a-zà-ÿÀ-ÿ''-]+"
        
        patterns = [
            # Multi-author patterns
            rf'By\s+({NAME_PART}(?:\s+{NAME_PART})+(?:,\s*{NAME_PART}(?:\s+{NAME_PART})+)*(?:\s+and\s+{NAME_PART}(?:\s+{NAME_PART})+)?)',
            rf'By\s+({NAME_PART}(?:\s+{NAME_PART})+)',
            rf'Written by\s+({NAME_PART}(?:\s+{NAME_PART})+)',
            rf'Story by\s+({NAME_PART}(?:\s+{NAME_PART})+)',
            rf'(?:Author|Reporter):\s*({NAME_PART}(?:\s+{NAME_PART})+)',
        ]
        
        search_area = visible_text[:2000]
        
        for pattern in patterns:
            match = re.search(pattern, search_area, re.MULTILINE | re.IGNORECASE)
            if match:
                author_raw = match.group(1)
                author = self._clean_author_name(author_raw)
                
                if self._is_valid_author_universal(author):
                    return author
        
        return "Unknown"
    
    def _extract_from_jsonld(self, soup: BeautifulSoup) -> str:
        """Extract from JSON-LD structured data"""
        try:
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                import json
                data = json.loads(script.string)
                
                items = data if isinstance(data, list) else [data]
                
                for item in items:
                    if 'author' in item:
                        author_data = item['author']
                        if isinstance(author_data, dict):
                            name = author_data.get('name', '')
                            if name:
                                return self._clean_author_name(name)
                        elif isinstance(author_data, str):
                            return self._clean_author_name(author_data)
                        elif isinstance(author_data, list):
                            names = [a.get('name', '') if isinstance(a, dict) else str(a) for a in author_data]
                            names = [n for n in names if n]
                            if names:
                                return ', '.join(names[:3])
        except Exception as e:
            logger.debug(f"[JSON-LD] Error: {e}")
        
        return "Unknown"
    
    def _extract_domain_specific(self, soup: BeautifulSoup, html: str, domain: str) -> str:
        """Domain-specific extraction patterns"""
        
        if 'newsweek.com' in domain or 'foxnews.com' in domain:
            meta = soup.find('meta', {'name': 'author'})
            if meta and meta.get('content'):
                return self._clean_author_name(meta['content'])
            
            byline = soup.find('div', class_=re.compile(r'author|byline', re.I))
            if byline:
                return self._clean_author_name(byline.get_text())
        
        if 'nytimes.com' in domain:
            byline = soup.find('p', class_='css-1o22h5v')
            if byline:
                return self._clean_author_name(byline.get_text())
        
        return "Unknown"
    
    def _clean_author_name(self, text: str) -> str:
        """Clean up author name"""
        if not text:
            return "Unknown"
        
        text = re.sub(r'^(?:by|written by|story by|author:|reporter:)\s*', '', text, flags=re.I)
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'\d{1,2}/\d{1,2}/\d{2,4}', '', text)
        text = re.sub(r'\d{1,2}:\d{2}\s*(?:AM|PM)', '', text, flags=re.I)
        
        outlet_names = ['Fox News', 'CNN', 'BBC', 'Reuters', 'Associated Press', 'The New York Times', 'Newsweek']
        for outlet in outlet_names:
            text = text.replace(outlet, '').strip()
        
        text = text.rstrip('.,;:!?')
        
        return text.strip()
    
    def _is_valid_author_universal(self, author: str) -> bool:
        """Universal author validation"""
        if not author or author == 'Unknown':
            return False
        
        author_list = [a.strip() for a in author.split(',')]
        
        for single_author in author_list:
            single_author = re.sub(r'^\s*and\s+', '', single_author, flags=re.I)
            
            words = single_author.split()
            
            if len(words) < 2:
                return False
            
            if not single_author[0].isupper():
                return False
            
            for politician in NON_JOURNALIST_NAMES:
                if politician.lower() in single_author.lower():
                    return False
            
            if len(words) > 6:
                return False
            
            for word in words[:2]:
                if not re.match(r"^[A-ZÀ-Ÿ][a-zà-ÿ''-]+$", word, re.UNICODE):
                    return False
        
        return True
    
    def _get_source_from_url(self, url: str) -> str:
        """Get source name"""
        domain = urlparse(url).netloc.replace('www.', '')
        
        sources = {
            'nytimes.com': 'The New York Times',
            'washingtonpost.com': 'The Washington Post',
            'bbc.com': 'BBC',
            'cnn.com': 'CNN',
            'foxnews.com': 'Fox News',
            'reuters.com': 'Reuters',
            'apnews.com': 'Associated Press',
            'theguardian.com': 'The Guardian',
            'wsj.com': 'The Wall Street Journal',
            'newsweek.com': 'Newsweek'
        }
        
        return sources.get(domain, domain.title())
    
    def _count_sources(self, text: str) -> int:
        """Count source citations"""
        if not text:
            return 0
        patterns = ['according to', 'said', 'reported', 'stated']
        return min(sum(len(re.findall(p, text, re.I)) for p in patterns), 20)
    
    def _count_quotes(self, text: str) -> int:
        """Count quotes"""
        return len(re.findall(r'"[^"]{10,}"', text)) if text else 0
    
    def _process_text(self, text: str) -> Dict[str, Any]:
        """Process direct text"""
        lines = text.strip().split('\n')
        title = lines[0][:100] if lines else "Text Analysis"
        
        return {
            'title': title,
            'author': 'User Provided',
            'author_page_url': None,
            'author_page_urls': [],
            'text': text,
            'content': text,
            'source': 'Direct Input',
            'domain': 'user_input',
            'url': '',
            'word_count': len(text.split()),
            'sources_count': self._count_sources(text),
            'quotes_count': self._count_quotes(text),
            'extraction_successful': True,
            'extraction_method': 'text_input'
        }
    
    def _check_availability(self) -> bool:
        """Service availability"""
        return True


logger.info("[ArticleExtractor v18.1] ENHANCED DEBUG + MULTI-AUTHOR - Aggressive HTML inspection enabled!")
