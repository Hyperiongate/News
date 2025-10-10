"""
Article Extractor - v18.2 CONSTRUCT AUTHOR URLS FROM NAMES
Date: October 10, 2025
Last Updated: October 10, 2025

CRITICAL FIX FROM v18.1:
✅ DISCOVERED: Newsweek author links are JavaScript-rendered (not in static HTML)
✅ SOLUTION: Extract author names from text, CONSTRUCT URLs from names
✅ PATTERN: https://www.newsweek.com/authors/[lowercase-hyphenated-name]
✅ MULTI-AUTHOR: Gets ALL authors and builds URL for each

THE DISCOVERY:
User: "I clicked on the link and it took me to the author's page"
Logs: "Found 0 <a> tags"
Reality: Links exist but are rendered by JavaScript after page loads

THE FIX:
1. Extract: "Jesus Mesa, Tom O'Connor, and Jason Lemon" from byline text
2. Construct: /authors/jesus-mesa, /authors/tom-oconnor, /authors/jason-lemon
3. Return: All 3 authors with their profile URLs
4. Scrape: Those constructed URLs for real data

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
    Article extractor with constructed author URLs
    v18.2 - Builds author URLs from extracted names
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
        
        logger.info(f"[ArticleExtractor v18.2 CONSTRUCT] Builds author URLs from names - OpenAI: {openai_available}")
    
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
        
        logger.info(f"[ArticleExtractor v18.2] Extracting: {url}")
        
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
        """Parse HTML and construct author URLs"""
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
            tag.decompose()
        
        # Extract components
        title = self._extract_title(soup)
        text = self._extract_text(soup)
        
        # NEW v18.2: Extract authors and CONSTRUCT URLs
        author, author_page_url, author_page_urls = self._extract_authors_and_construct_urls(soup, url)
        
        source = self._get_source_from_url(url)
        domain = urlparse(url).netloc.replace('www.', '')
        
        word_count = len(text.split()) if text else 0
        extraction_successful = len(text) > 200
        
        logger.info(f"[Parser] Title: {title[:50]}")
        logger.info(f"[Parser] Author: {author}")
        if author_page_url:
            logger.info(f"[Parser] Author Page (CONSTRUCTED): {author_page_url}")
        if len(author_page_urls) > 1:
            logger.info(f"[Parser] Total author pages: {len(author_page_urls)}")
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
    
    def _extract_authors_and_construct_urls(self, soup: BeautifulSoup, url: str) -> tuple[str, Optional[str], List[str]]:
        """
        NEW v18.2: Extract author names and CONSTRUCT profile URLs
        Newsweek pattern: /authors/[lowercase-hyphenated-name]
        Returns: (comma_separated_names, primary_url, all_urls)
        """
        
        logger.info("=" * 70)
        logger.info("[AUTHOR v18.2 CONSTRUCT] Extracting authors and building URLs")
        
        domain = urlparse(url).netloc.replace('www.', '')
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        
        # STEP 1: Extract author name(s) from byline text
        # Look for the byline with all author names
        byline_text = self._find_byline_text(soup)
        
        if byline_text:
            logger.info(f"[AUTHOR] Found byline text: '{byline_text}'")
            
            # Extract all author names from byline
            author_names = self._parse_multiple_authors_from_byline(byline_text)
            
            if author_names:
                logger.info(f"[AUTHOR] Extracted {len(author_names)} author(s): {author_names}")
                
                # STEP 2: Construct author page URLs for each name
                author_urls = []
                for name in author_names:
                    constructed_url = self._construct_author_url(name, domain, base_url)
                    if constructed_url:
                        author_urls.append(constructed_url)
                        logger.info(f"[AUTHOR] Constructed URL for '{name}': {constructed_url}")
                
                # Join all names with comma
                all_names = ', '.join(author_names)
                primary_url = author_urls[0] if author_urls else None
                
                logger.info(f"[AUTHOR] ✓✓✓ SUCCESS: {len(author_names)} authors with constructed URLs")
                logger.info(f"[AUTHOR]   Names: {all_names}")
                logger.info(f"[AUTHOR]   Primary URL: {primary_url}")
                logger.info("=" * 70)
                
                return all_names, primary_url, author_urls
        
        # FALLBACK: Try other extraction methods
        logger.info("[AUTHOR] No byline found, trying fallback methods")
        
        # Try AI or regex extraction
        if openai_available and openai_client:
            logger.info("[AUTHOR] Using AI to extract author(s)")
            author_text = self._extract_with_ai_multiauthor(soup.get_text()[:500])
            
            if author_text and author_text != 'Unknown':
                # Parse the AI result for multiple authors
                author_names = self._parse_multiple_authors_from_text(author_text)
                
                if author_names:
                    # Construct URLs
                    author_urls = [self._construct_author_url(name, domain, base_url) for name in author_names]
                    author_urls = [url for url in author_urls if url]  # Remove None
                    
                    all_names = ', '.join(author_names)
                    primary_url = author_urls[0] if author_urls else None
                    
                    logger.info(f"[AUTHOR] ✓ AI extracted: {all_names}")
                    logger.info("=" * 70)
                    return all_names, primary_url, author_urls
        
        # Try regex patterns
        author_text = self._extract_with_universal_patterns(soup.get_text())
        if author_text and author_text != 'Unknown':
            author_names = self._parse_multiple_authors_from_text(author_text)
            
            if author_names:
                author_urls = [self._construct_author_url(name, domain, base_url) for name in author_names]
                author_urls = [url for url in author_urls if url]
                
                all_names = ', '.join(author_names)
                primary_url = author_urls[0] if author_urls else None
                
                logger.info(f"[AUTHOR] ✓ Regex extracted: {all_names}")
                logger.info("=" * 70)
                return all_names, primary_url, author_urls
        
        logger.warning("[AUTHOR] ❌ Failed to extract authors")
        logger.info("=" * 70)
        return "Unknown", None, []
    
    def _find_byline_text(self, soup: BeautifulSoup) -> Optional[str]:
        """Find the byline text containing author names"""
        
        # Look for elements with "by" or author classes
        byline_patterns = [
            'byline', 'author', 'by-line', 'article-author', 'articlebyline'
        ]
        
        for pattern in byline_patterns:
            # Try class search
            elements = soup.find_all(class_=re.compile(pattern, re.I))
            for elem in elements:
                text = elem.get_text().strip()
                # Check if it looks like a byline (starts with "By" or contains author names)
                if text and (text.lower().startswith('by ') or len(text.split(',')) >= 2):
                    if len(text) < 200:  # Bylines are usually short
                        return text
        
        # Also try finding text that starts with "By"
        for elem in soup.find_all(['div', 'p', 'span'])[:50]:
            text = elem.get_text().strip()
            if text.lower().startswith('by ') and len(text) < 200:
                # Check if it contains name-like words
                words = text.split()
                if len(words) >= 3:  # "By First Last"
                    return text
        
        return None
    
    def _parse_multiple_authors_from_byline(self, byline_text: str) -> List[str]:
        """
        Parse multiple author names from byline text
        Handles: "By Jesus Mesa, Tom O'Connor, and Jason Lemon"
        """
        
        # Remove "By" prefix
        text = re.sub(r'^by\s+', '', byline_text, flags=re.I).strip()
        
        # Split by commas and "and"
        # Replace " and " with ", " for uniform splitting
        text = re.sub(r'\s+and\s+', ', ', text, flags=re.I)
        
        # Split by comma
        potential_names = [name.strip() for name in text.split(',')]
        
        # Validate each name
        valid_names = []
        for name in potential_names:
            cleaned = self._clean_author_name(name)
            if self._is_valid_author_name(cleaned):
                valid_names.append(cleaned)
        
        return valid_names
    
    def _parse_multiple_authors_from_text(self, text: str) -> List[str]:
        """Parse multiple authors from any text"""
        return self._parse_multiple_authors_from_byline(text)
    
    def _construct_author_url(self, author_name: str, domain: str, base_url: str) -> Optional[str]:
        """
        Construct author profile URL from name
        Newsweek: /authors/jesus-mesa
        Fox: /person/j/jesus-mesa
        NYT: /by/jesus-mesa
        """
        
        if not author_name or author_name == 'Unknown':
            return None
        
        # Convert name to URL slug: lowercase, replace spaces with hyphens
        slug = author_name.lower()
        slug = slug.replace("'", "")  # Remove apostrophes (O'Connor -> oconnor)
        slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special chars except spaces and hyphens
        slug = re.sub(r'[\s]+', '-', slug)  # Replace spaces with hyphens
        slug = re.sub(r'-+', '-', slug)  # Collapse multiple hyphens
        slug = slug.strip('-')  # Remove leading/trailing hyphens
        
        # Domain-specific patterns
        if 'newsweek.com' in domain:
            return f"{base_url}/authors/{slug}"
        elif 'foxnews.com' in domain:
            # Fox uses /person/first-letter/name
            first_letter = slug[0] if slug else 'a'
            return f"{base_url}/person/{first_letter}/{slug}"
        elif 'nytimes.com' in domain:
            return f"{base_url}/by/{slug}"
        elif 'washingtonpost.com' in domain:
            return f"{base_url}/people/{slug}"
        elif 'cnn.com' in domain:
            return f"{base_url}/profiles/{slug}"
        else:
            # Generic pattern - most sites use /author/ or /authors/
            return f"{base_url}/authors/{slug}"
    
    def _extract_with_ai_multiauthor(self, visible_text: str) -> str:
        """AI extraction for multiple authors"""
        try:
            prompt = f"""Extract ALL author names from this article beginning.

Text:
{visible_text}

Return ALL journalists who wrote this, separated by commas.
Examples:
- "Jesus Mesa, Tom O'Connor, Jason Lemon"
- "Mary Smith and John Doe"
- "Sarah Lee"

Return ONLY the names:"""
            
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": "Extract all article authors. Return names separated by commas."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                max_tokens=100,
                temperature=0.1
            )
            
            author = response.choices[0].message.content.strip()
            author = author.replace('Author:', '').strip().strip('"\'')
            
            return author if author else "Unknown"
            
        except Exception as e:
            logger.error(f"[AI] Failed: {e}")
            return "Unknown"
    
    def _extract_with_universal_patterns(self, visible_text: str) -> str:
        """Extract authors with regex patterns"""
        
        NAME_PART = r"[A-Z][a-zà-ÿÀ-ÿ''-]+"
        
        patterns = [
            # Multi-author with commas and "and"
            rf'By\s+({NAME_PART}(?:\s+{NAME_PART})+(?:,\s*{NAME_PART}(?:\s+{NAME_PART})+)*(?:,?\s+and\s+{NAME_PART}(?:\s+{NAME_PART})+)?)',
            rf'By\s+({NAME_PART}(?:\s+{NAME_PART})+)',
        ]
        
        search_area = visible_text[:2000]
        
        for pattern in patterns:
            match = re.search(pattern, search_area, re.MULTILINE | re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "Unknown"
    
    def _clean_author_name(self, text: str) -> str:
        """Clean up author name"""
        if not text:
            return "Unknown"
        
        text = re.sub(r'^(?:by|written by|story by|author:|reporter:)\s*', '', text, flags=re.I)
        text = re.sub(r'\s+', ' ', text).strip()
        text = text.rstrip('.,;:!?')
        
        return text.strip()
    
    def _is_valid_author_name(self, name: str) -> bool:
        """Check if a name is valid"""
        if not name or name == 'Unknown':
            return False
        
        words = name.split()
        
        # Must have first and last name
        if len(words) < 2:
            return False
        
        # Must start with capital
        if not name[0].isupper():
            return False
        
        # Not a politician
        for politician in NON_JOURNALIST_NAMES:
            if politician.lower() in name.lower():
                return False
        
        # Not too long
        if len(words) > 5:
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


logger.info("[ArticleExtractor v18.2] CONSTRUCTS AUTHOR URLS - Works around JavaScript-rendered links!")
