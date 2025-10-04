"""
Article Extractor - ENHANCED WITH AI AUTHOR EXTRACTION
Date: October 4, 2025
Version: 14.0

CHANGES:
- Added AI-powered author extraction using OpenAI
- Enhanced fallback methods for author detection
- Added comprehensive logging for debugging
- Maintains all ScraperAPI functionality

Complete replacement for services/article_extractor.py
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
    Article extractor with AI-powered author detection
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
        self.available = True  # For compatibility
        
        if self.scraperapi_key:
            logger.info(f"[ArticleExtractor] ✓ ScraperAPI KEY FOUND: {self.scraperapi_key[:8]}...")
        else:
            logger.warning("[ArticleExtractor] ✗ No ScraperAPI key - will use fallback")
        
        if openai_available:
            logger.info("[ArticleExtractor] ✓ OpenAI available for AI author extraction")
        else:
            logger.warning("[ArticleExtractor] ✗ OpenAI not available - using fallback author extraction")
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Service interface - calls extract internally"""
        
        url = data.get('url', '')
        text = data.get('text', '') or data.get('content', '')
        
        logger.info(f"[ArticleExtractor] analyze() called - URL: {bool(url)}, Text: {bool(text)}")
        
        try:
            if url and url.startswith('http'):
                # Extract from URL
                result = self.extract(url)
            elif text:
                # Process text
                result = self._process_text(text)
            else:
                return {
                    'service': self.service_name,
                    'success': False,
                    'error': 'No URL or text provided',
                    'data': {}
                }
            
            # Wrap in service response
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
        """Main extraction method - USES SCRAPERAPI FIRST"""
        
        logger.info(f"[ArticleExtractor] Starting extraction for: {url}")
        logger.info(f"[ArticleExtractor] ScraperAPI key configured: {bool(self.scraperapi_key)}")
        
        # METHOD 1: ScraperAPI (if we have a key)
        if self.scraperapi_key:
            logger.info("[ArticleExtractor] METHOD 1: Trying ScraperAPI...")
            try:
                html = self._fetch_with_scraperapi(url)
                if html:
                    result = self._parse_html(html, url)
                    if result['extraction_successful']:
                        logger.info(f"[ArticleExtractor] ✓ ScraperAPI SUCCESS: {result['word_count']} words")
                        logger.info(f"[ArticleExtractor] Author found: {result['author']}")
                        return result
                    else:
                        logger.warning("[ArticleExtractor] ScraperAPI returned content but parsing failed")
                else:
                    logger.warning("[ArticleExtractor] ScraperAPI returned no content")
            except Exception as e:
                logger.error(f"[ArticleExtractor] ScraperAPI error: {e}")
        
        # METHOD 2: Direct fetch as fallback
        logger.info("[ArticleExtractor] METHOD 2: Trying direct fetch...")
        try:
            html = self._fetch_direct(url)
            if html:
                result = self._parse_html(html, url)
                if result['extraction_successful']:
                    logger.info(f"[ArticleExtractor] ✓ Direct fetch SUCCESS: {result['word_count']} words")
                    logger.info(f"[ArticleExtractor] Author found: {result['author']}")
                    return result
        except Exception as e:
            logger.error(f"[ArticleExtractor] Direct fetch error: {e}")
        
        # FAILED
        logger.error(f"[ArticleExtractor] ❌ All methods failed for {url}")
        
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
        """ACTUALLY CALL SCRAPERAPI"""
        
        logger.info(f"[ScraperAPI] Making request with key: {self.scraperapi_key[:8]}...")
        
        # ScraperAPI endpoint
        api_url = 'http://api.scraperapi.com'
        
        # Parameters
        params = {
            'api_key': self.scraperapi_key,
            'url': url,
            'render': 'false',  # Don't render JavaScript
            'country_code': 'us'
        }
        
        logger.info(f"[ScraperAPI] Request URL: {api_url}")
        logger.info(f"[ScraperAPI] Target URL: {url}")
        
        try:
            response = requests.get(api_url, params=params, timeout=30)
            logger.info(f"[ScraperAPI] Response status: {response.status_code}")
            logger.info(f"[ScraperAPI] Response size: {len(response.text)} bytes")
            
            if response.status_code == 200 and len(response.text) > 100:
                return response.text
            else:
                logger.warning(f"[ScraperAPI] Bad response: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"[ScraperAPI] Request failed: {e}")
            return None
    
    def _fetch_direct(self, url: str) -> Optional[str]:
        """Direct fetch fallback"""
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
            
            if response.status_code == 200:
                return response.text
            else:
                logger.warning(f"[Direct] Status {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"[Direct] Failed: {e}")
            return None
    
    def _parse_html(self, html: str, url: str) -> Dict[str, Any]:
        """Parse HTML content with enhanced author extraction"""
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
            tag.decompose()
        
        # Extract components
        title = self._extract_title(soup)
        text = self._extract_text(soup)
        
        # ENHANCED AUTHOR EXTRACTION
        author = self._extract_author_ai_enhanced(soup, html)
        
        source = self._get_source_from_url(url)
        domain = urlparse(url).netloc.replace('www.', '')
        
        # Metrics
        word_count = len(text.split()) if text else 0
        extraction_successful = len(text) > 200
        
        logger.info(f"[Parser] Title: {title[:50]}")
        logger.info(f"[Parser] Author: {author}")
        logger.info(f"[Parser] Text length: {len(text)}")
        logger.info(f"[Parser] Word count: {word_count}")
        logger.info(f"[Parser] Successful: {extraction_successful}")
        
        return {
            'title': title,
            'author': author,
            'text': text,
            'content': text,  # Duplicate for compatibility
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
        
        # Try og:title first
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        
        # Try h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        # Try title tag
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
    
    def _extract_author_ai_enhanced(self, soup: BeautifulSoup, html: str) -> str:
        """AI-Enhanced author extraction"""
        
        logger.info("=" * 60)
        logger.info("[AUTHOR EXTRACTION] Starting enhanced author extraction")
        logger.info(f"[AUTHOR EXTRACTION] OpenAI available: {openai_available}")
        
        # FIRST: Try AI extraction if available
        if openai_available and openai_client:
            logger.info("[AUTHOR EXTRACTION] Using AI-powered extraction")
            try:
                # Get clean text from the top of the article
                visible_text = soup.get_text()[:3000]
                
                # Also get a snippet of HTML for structure
                html_snippet = html[:4000] if len(html) > 4000 else html
                
                # Check if there's a clear "By" pattern
                if 'By ' in visible_text[:1000] or 'by ' in visible_text[:1000]:
                    logger.info("[AUTHOR EXTRACTION] Found 'By' pattern in text - good sign!")
                
                prompt = f"""Find the article author name. Look for:
- "By [Name]" pattern near the top
- Author bylines
- Meta tags with author
- NOT quotes or people mentioned in the article

Article text start:
{visible_text[:1500]}

HTML snippet:
{html_snippet[:1000]}

Return ONLY the author name(s) or "Unknown" if not found.
Do not include "By" or any other text.

Author name:"""
                
                logger.info("[AUTHOR EXTRACTION] Sending to OpenAI...")
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=50,
                    temperature=0.1
                )
                
                author = response.choices[0].message.content.strip()
                logger.info(f"[AUTHOR EXTRACTION] OpenAI returned: '{author}'")
                
                # Clean and validate
                if author and author.lower() != 'unknown':
                    # Remove common prefixes
                    author = author.replace('By ', '').replace('by ', '')
                    author = author.replace('Author name:', '').strip()
                    
                    # Validate it's a real name
                    word_count = len(author.split())
                    if 2 <= word_count <= 6:
                        # Check it's not a politician
                        is_politician = any(name in author for name in NON_JOURNALIST_NAMES)
                        if not is_politician:
                            logger.info(f"[AUTHOR EXTRACTION] SUCCESS - AI found: {author}")
                            logger.info("=" * 60)
                            return author
                        else:
                            logger.info(f"[AUTHOR EXTRACTION] Rejected - politician: {author}")
                    else:
                        logger.info(f"[AUTHOR EXTRACTION] Rejected - word count: {word_count}")
                        
            except Exception as e:
                logger.error(f"[AUTHOR EXTRACTION] AI extraction failed: {e}")
        
        # FALLBACK: Traditional extraction
        logger.info("[AUTHOR EXTRACTION] Using fallback extraction methods")
        
        # Method 1: Meta tags
        for meta_name in ['author', 'byl', 'DC.creator']:
            author_meta = soup.find('meta', {'name': meta_name})
            if author_meta and author_meta.get('content'):
                author = author_meta['content'].strip()
                author = re.sub(r'^(by|By)\s+', '', author)
                if author and 2 <= len(author.split()) <= 4:
                    logger.info(f"[AUTHOR EXTRACTION] Found in meta tag: {author}")
                    logger.info("=" * 60)
                    return author
        
        # Method 2: Property meta tags
        author_meta = soup.find('meta', {'property': 'article:author'})
        if author_meta and author_meta.get('content'):
            author = author_meta['content'].strip()
            author = re.sub(r'^(by|By)\s+', '', author)
            if author and 2 <= len(author.split()) <= 4:
                logger.info(f"[AUTHOR EXTRACTION] Found in property tag: {author}")
                logger.info("=" * 60)
                return author
        
        # Method 3: Byline class
        for byline_class in ['byline', 'author', 'by-line', 'article-author']:
            byline = soup.find(class_=re.compile(byline_class, re.I))
            if byline:
                text = byline.get_text().strip()
                # Extract name after "By"
                match = re.search(r'By\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', text)
                if match:
                    author = match.group(1)
                    logger.info(f"[AUTHOR EXTRACTION] Found in byline: {author}")
                    logger.info("=" * 60)
                    return author
        
        # Method 4: Simple text pattern
        visible_text = soup.get_text()[:2000]
        match = re.search(r'By\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', visible_text)
        if match:
            author = match.group(1)
            # Make sure it's not in a quote
            context = visible_text[max(0, match.start()-50):match.end()+50]
            if not re.search(r'(said|told|according to)', context, re.I):
                logger.info(f"[AUTHOR EXTRACTION] Found in text pattern: {author}")
                logger.info("=" * 60)
                return author
        
        logger.warning("[AUTHOR EXTRACTION] No author found by any method")
        logger.info("=" * 60)
        return "Unknown"
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """Legacy author extraction - redirects to enhanced version"""
        return self._extract_author_ai_enhanced(soup, str(soup))
    
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
            'thehill.com': 'The Hill'
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
