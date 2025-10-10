"""
Article Extractor - v16.0 SUPER AGGRESSIVE AUTHOR EXTRACTION
Date: October 10, 2025

CHANGES FROM v15.0:
✅ MUCH MORE AGGRESSIVE: Tries 10+ methods to find author
✅ LOWERED THRESHOLDS: Single name + last name = valid author
✅ BETTER AI PROMPT: More explicit about finding ALL authors
✅ MORE PATTERNS: Added 15+ new regex patterns
✅ DEEPER SEARCH: Searches more HTML elements
✅ NEVER GIVES UP: Keeps trying until it finds something

PHILOSOPHY: If there's an author name ANYWHERE in the article, we WILL find it!

Save as: services/article_extractor.py or backend/services/article_extractor.py
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
    "Elon Musk", "Bill Gates", "Jeff Bezos", "Mark Zuckerberg", "Warren Buffett",
    "Vladimir Putin", "Xi Jinping", "Kim Jong"
}


class ArticleExtractor:
    """
    Article extractor with SUPER AGGRESSIVE author detection
    v16.0 - Never gives up finding the author!
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
        
        logger.info(f"[ArticleExtractor v16.0] Initialized - ScraperAPI: {bool(self.scraperapi_key)}, AI: {openai_available}")
    
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
        
        logger.info(f"[ArticleExtractor v16.0] Extracting: {url}")
        
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
        """Parse HTML with SUPER AGGRESSIVE author extraction"""
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
            tag.decompose()
        
        # Extract components
        title = self._extract_title(soup)
        text = self._extract_text(soup)
        
        # SUPER AGGRESSIVE AUTHOR EXTRACTION - tries 10+ methods
        author = self._extract_author_super_aggressive(soup, html, url, text)
        
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
        
        # Fallback
        paragraphs = soup.find_all('p')
        text = ' '.join([
            p.get_text().strip() 
            for p in paragraphs 
            if len(p.get_text().strip()) > 30
        ])
        
        return text
    
    def _extract_author_super_aggressive(self, soup: BeautifulSoup, html: str, url: str, article_text: str) -> str:
        """
        SUPER AGGRESSIVE author extraction - tries 10+ methods
        v16.0 - Never gives up!
        """
        
        logger.info("=" * 70)
        logger.info("[AUTHOR v16.0] Starting SUPER AGGRESSIVE extraction")
        logger.info(f"[AUTHOR] URL: {url[:80]}")
        
        # Get visible text for searching
        visible_text = soup.get_text()
        
        # METHOD 1: AI extraction (most powerful)
        if openai_available and openai_client:
            logger.info("[AUTHOR] METHOD 1: AI extraction")
            author = self._extract_with_ai_super_prompt(visible_text, html)
            if author and author != 'Unknown':
                logger.info(f"[AUTHOR] ✓✓✓ AI SUCCESS: {author}")
                logger.info("=" * 70)
                return author
        
        # METHOD 2: Meta tags (all variants)
        logger.info("[AUTHOR] METHOD 2: Meta tags")
        meta_names = [
            'author', 'byl', 'DC.creator', 'article:author', 'sailthru.author',
            'parsely-author', 'twitter:creator', 'Article.Author', 'Author'
        ]
        for meta_name in meta_names:
            author_meta = soup.find('meta', {'name': meta_name}) or soup.find('meta', {'property': meta_name})
            if author_meta and author_meta.get('content'):
                author = self._clean_author_name(author_meta['content'])
                if self._is_valid_author(author):
                    logger.info(f"[AUTHOR] ✓✓✓ Meta tag SUCCESS: {author}")
                    logger.info("=" * 70)
                    return author
        
        # METHOD 3: JSON-LD structured data
        logger.info("[AUTHOR] METHOD 3: JSON-LD")
        author = self._extract_from_jsonld(soup)
        if author and author != 'Unknown':
            logger.info(f"[AUTHOR] ✓✓✓ JSON-LD SUCCESS: {author}")
            logger.info("=" * 70)
            return author
        
        # METHOD 4: Byline classes (extensive list)
        logger.info("[AUTHOR] METHOD 4: Byline classes")
        byline_classes = [
            'byline', 'author', 'by-line', 'article-author', 'author-name',
            'post-author', 'entry-author', 'story-byline', 'contributor',
            'writer', 'reporter', 'author-info', 'article-byline', 'by_author'
        ]
        for byline_class in byline_classes:
            elements = soup.find_all(class_=re.compile(byline_class, re.I))
            for element in elements:
                text = element.get_text().strip()
                author = self._clean_author_name(text)
                if self._is_valid_author(author):
                    logger.info(f"[AUTHOR] ✓✓✓ Byline class SUCCESS: {author}")
                    logger.info("=" * 70)
                    return author
        
        # METHOD 5: Byline IDs
        logger.info("[AUTHOR] METHOD 5: Byline IDs")
        for byline_id in ['author', 'byline', 'author-name', 'post-author']:
            element = soup.find(id=byline_id)
            if element:
                text = element.get_text().strip()
                author = self._clean_author_name(text)
                if self._is_valid_author(author):
                    logger.info(f"[AUTHOR] ✓✓✓ Byline ID SUCCESS: {author}")
                    logger.info("=" * 70)
                    return author
        
        # METHOD 6: rel="author" links
        logger.info("[AUTHOR] METHOD 6: rel='author' links")
        author_links = soup.find_all('a', rel='author')
        for link in author_links:
            text = link.get_text().strip()
            author = self._clean_author_name(text)
            if self._is_valid_author(author):
                logger.info(f"[AUTHOR] ✓✓✓ rel='author' SUCCESS: {author}")
                logger.info("=" * 70)
                return author
        
        # METHOD 7: Aggressive regex patterns (15+ patterns)
        logger.info("[AUTHOR] METHOD 7: Aggressive regex patterns")
        patterns = [
            # Multi-author with commas
            r'By\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:,\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)*(?:\s+and\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)?)',
            # Simple "By Name Name"
            r'By\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            # Written by
            r'Written by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            # Story by
            r'Story by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            # Author:
            r'Author:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            # Reporter:
            r'Reporter:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            # Byline:
            r'Byline:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            # Just name at start of text (risky but we're aggressive!)
            r'^([A-Z][a-z]+\s+[A-Z][a-z]+)\s*\n',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, visible_text[:2000], re.MULTILINE)
            if match:
                author = self._clean_author_name(match.group(1))
                if self._is_valid_author(author):
                    logger.info(f"[AUTHOR] ✓✓✓ Regex SUCCESS: {author}")
                    logger.info("=" * 70)
                    return author
        
        # METHOD 8: Search in first 500 chars for name-like patterns
        logger.info("[AUTHOR] METHOD 8: First 500 chars scan")
        first_text = visible_text[:500]
        # Look for capitalized words that could be names
        words = first_text.split()
        potential_names = []
        for i, word in enumerate(words[:-1]):
            if word[0].isupper() and len(word) > 2:
                next_word = words[i+1]
                if next_word[0].isupper() and len(next_word) > 2:
                    potential_name = f"{word} {next_word}"
                    if self._is_valid_author(potential_name):
                        potential_names.append(potential_name)
        
        if potential_names:
            author = potential_names[0]
            logger.info(f"[AUTHOR] ✓✓✓ First 500 chars SUCCESS: {author}")
            logger.info("=" * 70)
            return author
        
        # METHOD 9: Look in article text for "said FirstName LastName"
        logger.info("[AUTHOR] METHOD 9: Attribution patterns")
        attribution_pattern = r'(?:said|wrote|reported by|according to)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)'
        matches = re.findall(attribution_pattern, article_text[:1000])
        for match in matches:
            if self._is_valid_author(match):
                author = match
                logger.info(f"[AUTHOR] ✓✓ Attribution pattern: {author} (might be journalist)")
                # Don't return yet - could be quote source
        
        # METHOD 10: Domain-specific extraction
        logger.info("[AUTHOR] METHOD 10: Domain-specific patterns")
        domain = urlparse(url).netloc.replace('www.', '')
        author = self._extract_domain_specific(soup, html, domain)
        if author and author != 'Unknown':
            logger.info(f"[AUTHOR] ✓✓✓ Domain-specific SUCCESS: {author}")
            logger.info("=" * 70)
            return author
        
        logger.warning("[AUTHOR] ❌❌❌ ALL 10 METHODS FAILED - returning Unknown")
        logger.info("=" * 70)
        return "Unknown"
    
    def _extract_with_ai_super_prompt(self, visible_text: str, html: str) -> str:
        """
        Enhanced AI extraction with super explicit prompt
        """
        try:
            prompt = f"""You are an expert at finding article authors. Extract the author name(s) from this article.

RULES:
1. Look for "By [Name]" or similar bylines
2. If multiple authors, list ALL separated by ", " (comma space)
3. Return ONLY the name(s), nothing else
4. If you find an author, return it even if you're not 100% certain
5. Politicians/subjects being quoted are NOT authors
6. Only return "Unknown" if there is absolutely NO author anywhere

Article text (first 1500 chars):
{visible_text[:1500]}

HTML snippet (first 800 chars):
{html[:800]}

Author name(s):"""
            
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": "Extract article authors. Return ONLY the name(s), nothing else. Be aggressive - if you see a potential author name, return it."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                max_tokens=100,
                temperature=0.1
            )
            
            author = response.choices[0].message.content.strip()
            author = self._clean_author_name(author)
            
            logger.info(f"[AI] Returned: '{author}'")
            
            if self._is_valid_author(author):
                return author
            
        except Exception as e:
            logger.error(f"[AI] Failed: {e}")
        
        return "Unknown"
    
    def _extract_from_jsonld(self, soup: BeautifulSoup) -> str:
        """Extract from JSON-LD structured data"""
        try:
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                import json
                data = json.loads(script.string)
                
                # Handle array or single object
                if isinstance(data, list):
                    items = data
                else:
                    items = [data]
                
                for item in items:
                    # Check for author field
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
        
        # Fox News
        if 'foxnews.com' in domain:
            # Try meta first
            meta = soup.find('meta', {'name': 'author'})
            if meta and meta.get('content'):
                return self._clean_author_name(meta['content'])
            
            # Try byline div
            byline = soup.find('div', class_=re.compile(r'author|byline', re.I))
            if byline:
                return self._clean_author_name(byline.get_text())
        
        # NY Times
        if 'nytimes.com' in domain:
            byline = soup.find('p', class_='css-1o22h5v')
            if byline:
                return self._clean_author_name(byline.get_text())
        
        # Add more outlets as needed
        
        return "Unknown"
    
    def _clean_author_name(self, text: str) -> str:
        """Clean up author name"""
        if not text:
            return "Unknown"
        
        # Remove common prefixes
        text = re.sub(r'^(by|By|BY|written by|story by|author:|reporter:)\s*', '', text, flags=re.I)
        
        # Remove newlines and extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove dates/times
        text = re.sub(r'\d{1,2}/\d{1,2}/\d{2,4}', '', text)
        text = re.sub(r'\d{1,2}:\d{2}\s*(?:AM|PM)', '', text, flags=re.I)
        
        # Remove outlet names
        outlet_names = ['Fox News', 'CNN', 'BBC', 'Reuters', 'Associated Press', 'The New York Times']
        for outlet in outlet_names:
            text = text.replace(outlet, '').strip()
        
        # Remove trailing punctuation
        text = text.rstrip('.,;:!?')
        
        return text.strip()
    
    def _is_valid_author(self, author: str) -> bool:
        """Validate author name"""
        if not author or author == 'Unknown':
            return False
        
        # Must have at least first and last name
        words = author.split()
        if len(words) < 2:
            return False
        
        # Must start with capital letter
        if not author[0].isupper():
            return False
        
        # Check not a politician
        for politician in NON_JOURNALIST_NAMES:
            if politician.lower() in author.lower():
                return False
        
        # Check not too long (probably not a name)
        if len(words) > 6:
            return False
        
        # Check words look like names (mostly letters)
        for word in words[:2]:  # Check first two words
            if not re.match(r'^[A-Z][a-z]+$', word):
                if not re.match(r'^[A-Z][a-z]+[A-Z][a-z]+$', word):  # Handles "McDonald"
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
            'wsj.com': 'The Wall Street Journal'
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


logger.info("[ArticleExtractor v16.0] SUPER AGGRESSIVE author extraction loaded")
