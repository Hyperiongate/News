"""
Article Extractor - FIXED MULTI-AUTHOR EXTRACTION
Date: October 5, 2025
Version: 15.0

CRITICAL FIXES:
- Fixed Fox News multi-author bug (handles "By Name, Name, Name, Name" format)
- Enhanced regex patterns for comma-separated and "and" separated authors
- Improved OpenAI prompt to handle co-authored articles
- Added specific HTML structure detection for major outlets
- All existing ScraperAPI functionality preserved

CHANGES FROM v14.0:
- Line 310-330: New multi-author parsing logic
- Line 350-380: Enhanced regex patterns for bylines
- Line 400-420: Improved OpenAI prompt for co-authors
- Line 450-470: Fox News specific HTML detection

Complete replacement for backend/services/article_extractor.py
"""

import os
import re
import time
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse

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
    "Elon Musk", "Bill Gates", "Jeff Bezos", "Mark Zuckerberg", "Warren Buffett"
}


class ArticleExtractor:
    """
    Article extractor with FIXED multi-author detection
    """
    
    def __init__(self):
        self.scraperapi_key = os.getenv('SCRAPERAPI_KEY', '').strip()
        self.session = requests.Session()
        
        # Basic headers for fallback
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        
        self.is_available = True
        self.service_name = 'article_extractor'
        self.available = True
        
        if self.scraperapi_key:
            logger.info(f"[ArticleExtractor] ✓ ScraperAPI configured")
        else:
            logger.warning("[ArticleExtractor] ✗ No ScraperAPI key")
        
        if openai_available:
            logger.info("[ArticleExtractor] ✓ OpenAI available for AI author extraction")
        else:
            logger.warning("[ArticleExtractor] ✗ OpenAI not available")
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Service interface - calls extract internally"""
        
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
        
        logger.info(f"[ArticleExtractor] Starting extraction for: {url}")
        
        # METHOD 1: ScraperAPI (if available)
        if self.scraperapi_key:
            logger.info("[ArticleExtractor] Trying ScraperAPI...")
            try:
                html = self._fetch_with_scraperapi(url)
                if html:
                    result = self._parse_html(html, url)
                    if result['extraction_successful']:
                        logger.info(f"[ArticleExtractor] ✓ ScraperAPI SUCCESS")
                        return result
            except Exception as e:
                logger.error(f"[ArticleExtractor] ScraperAPI error: {e}")
        
        # METHOD 2: Direct fetch
        logger.info("[ArticleExtractor] Trying direct fetch...")
        try:
            html = self._fetch_direct(url)
            if html:
                result = self._parse_html(html, url)
                if result['extraction_successful']:
                    logger.info(f"[ArticleExtractor] ✓ Direct fetch SUCCESS")
                    return result
        except Exception as e:
            logger.error(f"[ArticleExtractor] Direct fetch error: {e}")
        
        # FAILED
        logger.error(f"[ArticleExtractor] ❌ All methods failed")
        
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
            'error': 'Could not extract article content'
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
            return None
        except Exception as e:
            logger.error(f"[ScraperAPI] Request failed: {e}")
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
            return None
        except Exception as e:
            logger.error(f"[Direct] Failed: {e}")
            return None
    
    def _parse_html(self, html: str, url: str) -> Dict[str, Any]:
        """Parse HTML with FIXED multi-author extraction"""
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
            tag.decompose()
        
        # Extract components
        title = self._extract_title(soup)
        text = self._extract_text(soup)
        
        # FIXED AUTHOR EXTRACTION - handles multi-author formats
        author = self._extract_author_enhanced(soup, html, url)
        
        source = self._get_source_from_url(url)
        domain = urlparse(url).netloc.replace('www.', '')
        
        word_count = len(text.split()) if text else 0
        extraction_successful = len(text) > 200
        
        logger.info(f"[Parser] Title: {title[:50]}")
        logger.info(f"[Parser] Author: {author}")
        logger.info(f"[Parser] Words: {word_count}")
        
        return {
            'title': title,
            'author': author,
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
        
        # Fallback to all paragraphs
        paragraphs = soup.find_all('p')
        text = ' '.join([
            p.get_text().strip() 
            for p in paragraphs 
            if len(p.get_text().strip()) > 30
        ])
        
        return text
    
    def _extract_author_enhanced(self, soup: BeautifulSoup, html: str, url: str) -> str:
        """
        ENHANCED multi-author extraction - fixes Fox News bug
        Handles: "By Greg Wehner, Bill Melugin, Matt Finn, Michael Tobin"
        """
        
        logger.info("=" * 60)
        logger.info("[AUTHOR] Starting ENHANCED extraction")
        logger.info(f"[AUTHOR] URL: {url}")
        
        # STEP 1: Check outlet-specific patterns first
        domain = urlparse(url).netloc.replace('www.', '')
        
        # Fox News specific extraction
        if 'foxnews.com' in domain:
            logger.info("[AUTHOR] Fox News detected - using specific patterns")
            author = self._extract_foxnews_author(soup, html)
            if author and author != 'Unknown':
                logger.info(f"[AUTHOR] Fox News extraction: {author}")
                logger.info("=" * 60)
                return author
        
        # STEP 2: Try AI extraction if available
        if openai_available and openai_client:
            logger.info("[AUTHOR] Using AI-powered extraction")
            try:
                visible_text = soup.get_text()[:3000]
                html_snippet = html[:4000] if len(html) > 4000 else html
                
                # IMPROVED PROMPT for multi-author handling
                prompt = f"""Extract the article author name(s). 

Look for:
- "By [Name]" or "By [Name], [Name], [Name]" patterns
- Author bylines with multiple authors separated by commas or "and"
- Author meta tags

Article text:
{visible_text[:1500]}

HTML snippet:
{html_snippet[:1000]}

IMPORTANT:
- If multiple authors, list ALL separated by ", " (comma-space)
- Return ONLY the author name(s), nothing else
- Return "Unknown" if no authors found
- Do NOT include "By" or any prefix

Author(s):"""
                
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=100,
                    temperature=0.1
                )
                
                author = response.choices[0].message.content.strip()
                logger.info(f"[AUTHOR] AI returned: '{author}'")
                
                # Validate and clean
                if author and author.lower() != 'unknown':
                    author = author.replace('By ', '').replace('by ', '').strip()
                    author = author.replace('Author(s):', '').strip()
                    
                    # Check it's valid
                    if len(author.split()) >= 2:
                        # Check not a politician
                        is_politician = any(name in author for name in NON_JOURNALIST_NAMES)
                        if not is_politician:
                            logger.info(f"[AUTHOR] ✓ AI SUCCESS: {author}")
                            logger.info("=" * 60)
                            return author
                        
            except Exception as e:
                logger.error(f"[AUTHOR] AI failed: {e}")
        
        # STEP 3: Enhanced regex patterns for multi-author
        logger.info("[AUTHOR] Using enhanced regex patterns")
        
        # Pattern 1: "By Name, Name, Name, Name" (Fox News style)
        visible_text = soup.get_text()[:2000]
        
        # Match: By [Names with commas and optional 'and']
        pattern1 = r'By\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:,\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)*(?:\s+and\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)?)'
        match = re.search(pattern1, visible_text)
        if match:
            authors = match.group(1)
            # Clean up the result
            authors = re.sub(r'\s+', ' ', authors)  # Normalize spaces
            logger.info(f"[AUTHOR] ✓ Regex pattern 1: {authors}")
            logger.info("=" * 60)
            return authors
        
        # Pattern 2: Simple "By Name Name"
        pattern2 = r'By\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'
        match = re.search(pattern2, visible_text)
        if match:
            author = match.group(1)
            logger.info(f"[AUTHOR] ✓ Regex pattern 2: {author}")
            logger.info("=" * 60)
            return author
        
        # STEP 4: Meta tags
        for meta_name in ['author', 'byl', 'DC.creator', 'article:author']:
            author_meta = soup.find('meta', {'name': meta_name}) or soup.find('meta', {'property': meta_name})
            if author_meta and author_meta.get('content'):
                author = author_meta['content'].strip()
                author = re.sub(r'^(by|By)\s+', '', author)
                if author and len(author.split()) >= 2:
                    logger.info(f"[AUTHOR] ✓ Meta tag: {author}")
                    logger.info("=" * 60)
                    return author
        
        # STEP 5: Byline classes
        for byline_class in ['byline', 'author', 'by-line', 'article-author', 'author-name']:
            byline = soup.find(class_=re.compile(byline_class, re.I))
            if byline:
                text = byline.get_text().strip()
                # Remove "By" prefix
                text = re.sub(r'^(by|By)\s+', '', text)
                if text and len(text.split()) >= 2:
                    logger.info(f"[AUTHOR] ✓ Byline class: {text}")
                    logger.info("=" * 60)
                    return text
        
        logger.warning("[AUTHOR] ❌ No author found")
        logger.info("=" * 60)
        return "Unknown"
    
    def _extract_foxnews_author(self, soup: BeautifulSoup, html: str) -> str:
        """
        Fox News specific author extraction
        Handles their specific HTML structure
        """
        
        # Method 1: Look for Fox News byline structure
        byline_div = soup.find('div', class_=re.compile(r'author|byline', re.I))
        if byline_div:
            text = byline_div.get_text().strip()
            # Remove "By" and "Fox News" artifacts
            text = re.sub(r'^(by|By)\s+', '', text)
            text = re.sub(r'Fox News', '', text, flags=re.I)
            text = text.strip()
            
            if text and len(text.split()) >= 2:
                return text
        
        # Method 2: Look for specific Fox News meta patterns
        # They often use: <meta name="author" content="Name, Name, Name">
        author_meta = soup.find('meta', {'name': 'author'})
        if author_meta and author_meta.get('content'):
            author = author_meta['content'].strip()
            # Fox News sometimes includes "By" in meta
            author = re.sub(r'^(by|By)\s+', '', author)
            if author and len(author.split()) >= 2:
                return author
        
        # Method 3: Text search for Fox News byline pattern
        # "By Greg Wehner, Bill Melugin, Matt Finn, Michael Tobin"
        text = soup.get_text()[:1500]
        match = re.search(r'By\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:,\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)+)', text)
        if match:
            return match.group(1)
        
        return "Unknown"
    
    def _get_source_from_url(self, url: str) -> str:
        """Get source name from URL"""
        
        domain = urlparse(url).netloc.replace('www.', '')
        
        sources = {
            'nytimes.com': 'The New York Times',
            'washingtonpost.com': 'The Washington Post',
            'bbc.com': 'BBC',
            'bbc.co.uk': 'BBC',
            'cnn.com': 'CNN',
            'foxnews.com': 'Fox News',
            'reuters.com': 'Reuters',
            'apnews.com': 'Associated Press',
            'theguardian.com': 'The Guardian',
            'wsj.com': 'The Wall Street Journal',
            'independent.co.uk': 'The Independent',
            'npr.org': 'NPR',
            'politico.com': 'Politico',
            'axios.com': 'Axios',
            'thehill.com': 'The Hill',
            'nbcnews.com': 'NBC News'
        }
        
        return sources.get(domain, domain.title())
    
    def _count_sources(self, text: str) -> int:
        """Count source citations"""
        if not text:
            return 0
        
        patterns = ['according to', 'said', 'reported', 'stated']
        count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in patterns)
        return min(count, 20)
    
    def _count_quotes(self, text: str) -> int:
        """Count quotes"""
        if not text:
            return 0
        return len(re.findall(r'"[^"]{10,}"', text))
    
    def _process_text(self, text: str) -> Dict[str, Any]:
        """Process direct text input"""
        
        lines = text.strip().split('\n')
        title = lines[0][:100] if lines else "Text Analysis"
        
        return {
            'title': title,
            'author': 'User Provided',
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
        """Service availability check"""
        return True
