"""
Article Extractor - DATA WRAPPER FORMAT FIX
CRITICAL FIXES:
1. Returns data in proper 'data' wrapper format that pipeline expects
2. Enhanced author extraction with comprehensive strategies
3. Proper domain cleaning and URL handling
4. Consistent success/error response format
"""

import json
import re
import time
import logging
import requests
import urllib3
from bs4 import BeautifulSoup
from typing import Dict, Optional, Any
from urllib.parse import urlparse
from datetime import datetime
import random

from services.base_analyzer import BaseAnalyzer

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class ArticleExtractor(BaseAnalyzer):
    """
    FIXED: Article extraction with proper data wrapper format
    """
    
    def __init__(self):
        super().__init__('article_extractor')
        
        # Get ScraperAPI key from config
        try:
            from config import Config
            self.scraperapi_key = Config.SCRAPERAPI_KEY
            logger.info(f"ArticleExtractor initialized - ScraperAPI: {bool(self.scraperapi_key)}")
        except:
            self.scraperapi_key = None
            logger.warning("ScraperAPI key not available")
        
        # Initialize session for requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
    
    def _check_availability(self) -> bool:
        """Check if service is available"""
        return True  # Always available with fallback methods
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        CRITICAL FIX: Main analysis method that returns proper data wrapper format
        """
        logger.info("=" * 60)
        logger.info("ARTICLE EXTRACTOR - DATA WRAPPER FORMAT FIX")
        logger.info("=" * 60)
        
        try:
            # Parse input
            url = data.get('url')
            text = data.get('text')
            
            if url:
                logger.info(f"Extracting from URL: {url}")
                result = self._extract_from_url(url)
            elif text:
                logger.info("Processing provided text")
                result = self._process_text(text)
            else:
                return self.get_error_result("No URL or text provided")
            
            # CRITICAL FIX: Ensure proper wrapper format
            if result.get('success'):
                # Return using BaseAnalyzer format with data wrapper
                return self.get_success_result(result)
            else:
                return self.get_error_result(result.get('error', 'Extraction failed'))
                
        except Exception as e:
            logger.error(f"ArticleExtractor.analyze failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _extract_from_url(self, url: str) -> Dict[str, Any]:
        """Extract article content from URL with multiple strategies"""
        
        strategies = [
            ('scraperapi', self._extract_with_scraperapi),
            ('enhanced_requests', self._extract_with_requests),
            ('basic_fallback', self._extract_basic_fallback)
        ]
        
        last_error = None
        
        for strategy_name, strategy_func in strategies:
            try:
                logger.info(f"Trying {strategy_name}...")
                result = strategy_func(url)
                
                if result.get('success') and self._validate_extraction(result):
                    logger.info(f"SUCCESS: {strategy_name} extracted content")
                    return result
                else:
                    last_error = result.get('error', f'{strategy_name} returned insufficient content')
                    logger.warning(f"{strategy_name} failed: {last_error}")
                    
            except Exception as e:
                last_error = str(e)
                logger.error(f"{strategy_name} threw exception: {e}")
                continue
        
        return {
            'success': False,
            'error': f'All extraction methods failed. Last error: {last_error}'
        }
    
    def _extract_with_scraperapi(self, url: str) -> Dict[str, Any]:
        """Extract using ScraperAPI if available"""
        if not self.scraperapi_key:
            return {'success': False, 'error': 'ScraperAPI key not available'}
        
        try:
            params = {
                'api_key': self.scraperapi_key,
                'url': url,
                'render': 'false',
                'country_code': 'us'
            }
            
            response = requests.get('http://api.scraperapi.com', params=params, timeout=60)
            response.raise_for_status()
            
            return self._parse_html_content(response.text, url, 'scraperapi')
            
        except Exception as e:
            return {'success': False, 'error': f'ScraperAPI failed: {str(e)}'}
    
    def _extract_with_requests(self, url: str) -> Dict[str, Any]:
        """Extract using enhanced requests session"""
        try:
            # Add some randomization to avoid detection
            self.session.headers['User-Agent'] = self._get_random_user_agent()
            
            response = self.session.get(url, timeout=30, verify=False, allow_redirects=True)
            response.raise_for_status()
            
            return self._parse_html_content(response.text, url, 'requests')
            
        except Exception as e:
            return {'success': False, 'error': f'Enhanced requests failed: {str(e)}'}
    
    def _extract_basic_fallback(self, url: str) -> Dict[str, Any]:
        """Basic fallback extraction method"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            response = requests.get(url, headers=headers, timeout=30, verify=False)
            response.raise_for_status()
            
            return self._parse_html_content(response.text, url, 'basic_fallback')
            
        except Exception as e:
            return {'success': False, 'error': f'Basic fallback failed: {str(e)}'}
    
    def _parse_html_content(self, html: str, url: str, method: str) -> Dict[str, Any]:
        """
        CRITICAL FIX: Parse HTML and return in proper data structure
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'nav', 'aside', 'footer', 'header']):
                element.decompose()
            
            # Extract components
            title = self._extract_title(soup)
            content = self._extract_content(soup)
            author = self._extract_author_comprehensive(soup, url)
            publish_date = self._extract_publish_date(soup)
            description = self._extract_description(soup)
            
            # Calculate metrics
            word_count = len(content.split()) if content else 0
            domain = self._clean_domain(urlparse(url).netloc)
            
            # CRITICAL FIX: Return in exact format expected by pipeline
            return {
                'success': True,
                'data': {  # This is the wrapper format pipeline expects
                    'title': title,
                    'text': content,
                    'author': author,
                    'publish_date': publish_date,
                    'url': url,
                    'domain': domain,
                    'description': description,
                    'word_count': word_count,
                    'language': 'en',
                'extraction_successful': True
            }
        }en',
                    'extraction_successful': bool(content and len(content) > 100)
                },
                'extraction_metadata': {
                    'method': method,
                    'extracted_at': datetime.now().isoformat(),
                    'content_length': len(content) if content else 0,
                    'author_found': bool(author and author != 'Unknown'),
                    'title_found': bool(title and title != 'Unknown Title')
                }
            }
            
        except Exception as e:
            logger.error(f"HTML parsing failed: {e}", exc_info=True)
            return {'success': False, 'error': f'HTML parsing failed: {str(e)}'}
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title"""
        # Try multiple selectors in order of preference
        selectors = [
            'h1',
            'title', 
            '[property="og:title"]',
            '[name="twitter:title"]',
            '.entry-title',
            '.post-title',
            '.article-title',
            '.headline'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    title = element.get('content', '').strip()
                else:
                    title = element.get_text(strip=True)
                
                if title and len(title) > 5:
                    # Clean up title
                    title = re.sub(r'\s+', ' ', title)
                    return title[:200]  # Limit length
        
        return 'Unknown Title'
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main article content"""
        # Try content selectors in order of preference
        content_selectors = [
            'article',
            '[role="article"]', 
            '.entry-content',
            '.post-content',
            '.article-body',
            '.article-content',
            '.content',
            'main',
            '.main-content'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                # Remove ads and unwanted nested content
                for unwanted in element.find_all(['.ad', '.advertisement', '.sidebar', 'aside']):
                    unwanted.decompose()
                
                text = element.get_text(separator=' ', strip=True)
                if text and len(text) > 200:  # Must have substantial content
                    return text
        
        # Fallback: extract all paragraph text
        paragraphs = soup.find_all('p')
        if paragraphs:
            content_parts = []
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text and len(text) > 20:  # Skip very short paragraphs
                    content_parts.append(text)
            
            if content_parts:
                return ' '.join(content_parts)
        
        # Final fallback: all text
        return soup.get_text(separator=' ', strip=True) or ''
    
    def _extract_author_comprehensive(self, soup: BeautifulSoup, url: str) -> str:
        """
        CRITICAL FIX: Comprehensive author extraction with multiple strategies
        """
        logger.info(f"=== COMPREHENSIVE AUTHOR EXTRACTION for {url} ===")
        
        # Strategy 1: Structured data (JSON-LD, microdata)
        author = self._extract_author_structured(soup)
        if author:
            logger.info(f"✓ Author from structured data: {author}")
            return author
        
        # Strategy 2: Meta tags
        author = self._extract_author_meta(soup)
        if author:
            logger.info(f"✓ Author from meta tags: {author}")
            return author
        
        # Strategy 3: CSS selectors
        author = self._extract_author_selectors(soup)
        if author:
            logger.info(f"✓ Author from CSS selectors: {author}")
            return author
        
        # Strategy 4: Text pattern matching
        author = self._extract_author_patterns(soup)
        if author:
            logger.info(f"✓ Author from text patterns: {author}")
            return author
        
        logger.info("✗ No author found with any method")
        return 'Unknown'
    
    def _extract_author_structured(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author from structured data"""
        # JSON-LD
        scripts = soup.find_all('script', {'type': 'application/ld+json'})
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    data = data[0]
                
                if isinstance(data, dict) and 'author' in data:
                    author_data = data['author']
                    if isinstance(author_data, dict):
                        name = author_data.get('name')
                        if name:
                            return self._clean_author_name(name)
                    elif isinstance(author_data, str):
                        return self._clean_author_name(author_data)
            except:
                continue
        
        return None
    
    def _extract_author_meta(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author from meta tags"""
        meta_selectors = [
            '[name="author"]',
            '[property="article:author"]', 
            '[name="article:author"]',
            '[property="author"]',
            '[name="byl"]'
        ]
        
        for selector in meta_selectors:
            element = soup.select_one(selector)
            if element:
                author = element.get('content', '').strip()
                if author:
                    return self._clean_author_name(author)
        
        return None
    
    def _extract_author_selectors(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author using CSS selectors"""
        author_selectors = [
            '.author', '.byline', '.author-name', '.byline-author',
            '.article-author', '.post-author', '.entry-author',
            '.writer', '.journalist', '.reporter',
            '[rel="author"]', '[itemprop="author"]',
            '.author-info', '.author-details', '.byline-name',
            '.article-byline', '.story-byline', '.news-byline'
        ]
        
        for selector in author_selectors:
            elements = soup.select(selector)
            for element in elements:
                # Skip if inside navigation or footer
                if element.find_parent(['nav', 'footer', 'aside']):
                    continue
                
                # Try text content first
                author_text = element.get_text(strip=True)
                if author_text and len(author_text) < 100:
                    cleaned = self._clean_author_name(author_text)
                    if self._is_valid_author_name(cleaned):
                        return cleaned
                
                # Try links within author elements
                link = element.find('a')
                if link:
                    link_text = link.get_text(strip=True)
                    if link_text and len(link_text) < 100:
                        cleaned = self._clean_author_name(link_text)
                        if self._is_valid_author_name(cleaned):
                            return cleaned
        
        return None
    
    def _extract_author_patterns(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author using text pattern matching"""
        full_text = soup.get_text()
        
        patterns = [
            r'By\s+([A-Z][a-zA-Z\-\']+(?:\s+[A-Z][a-zA-Z\-\']+)+)(?:\s|$|,|\.|:|;)',
            r'BY\s+([A-Z][a-zA-Z\-\']+(?:\s+[A-Z][a-zA-Z\-\']+)+)(?:\s|$|,|\.|:|;)', 
            r'Written by\s+([A-Z][a-zA-Z\-\']+(?:\s+[A-Z][a-zA-Z\-\']+)+)',
            r'Story by\s+([A-Z][a-zA-Z\-\']+(?:\s+[A-Z][a-zA-Z\-\']+)+)',
            r'Author:\s*([A-Z][a-zA-Z\-\']+(?:\s+[A-Z][a-zA-Z\-\']+)+)',
            r'Reporter:\s*([A-Z][a-zA-Z\-\']+(?:\s+[A-Z][a-zA-Z\-\']+)+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, full_text)
            if match:
                author_name = match.group(1).strip()
                cleaned = self._clean_author_name(author_name)
                if self._is_valid_author_name(cleaned):
                    return cleaned
        
        return None
    
    def _clean_author_name(self, author: str) -> str:
        """Clean and normalize author name"""
        if not author:
            return ''
        
        # Remove common prefixes
        author = re.sub(r'^(By|by|BY|Written by|Story by|Author:|Reporter:)\s+', '', author)
        
        # Remove suffixes and publication info
        author = re.sub(r'\s*[\|\-]\s*(Reporter|Writer|Journalist|Correspondent).*', '', author)
        author = re.sub(r'\s*,\s*(CNN|BBC|Reuters|Associated Press|AP).*', '', author)
        
        # Clean whitespace and punctuation
        author = re.sub(r'\s+', ' ', author).strip()
        author = re.sub(r'[,\.\:;]+$', '', author)
        
        return author
    
    def _is_valid_author_name(self, author: str) -> bool:
        """Validate author name"""
        if not author or len(author) < 3 or len(author) > 100:
            return False
        
        # Must have at least 2 words
        words = author.split()
        if len(words) < 2:
            return False
        
        # Should start with capital letter
        if not author[0].isupper():
            return False
        
        # No numbers or most special characters
        if re.search(r'[0-9@#$%^&*()_+={}|\[\]\\";\'<>?,./]', author):
            return False
        
        # Reject common false positives
        false_positives = [
            'read more', 'click here', 'share this', 'comments',
            'breaking news', 'latest news', 'social media'
        ]
        
        author_lower = author.lower()
        if any(fp in author_lower for fp in false_positives):
            return False
        
        return True
    
    def _extract_publish_date(self, soup: BeautifulSoup) -> str:
        """Extract publish date"""
        date_selectors = [
            '[property="article:published_time"]',
            '[name="publish_date"]',
            '[name="date"]', 
            'time[datetime]',
            '.publish-date',
            '.article-date',
            '.post-date'
        ]
        
        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                date = (element.get('content') or 
                       element.get('datetime') or 
                       element.get_text(strip=True))
                if date:
                    return date[:50]
        
        return ''
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract article description"""
        desc_selectors = [
            '[name="description"]',
            '[property="og:description"]',
            '[name="twitter:description"]'
        ]
        
        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element:
                desc = element.get('content', '').strip()
                if desc:
                    return desc[:500]
        
        return ''
    
    def _clean_domain(self, domain: str) -> str:
        """Clean domain for display"""
        if not domain:
            return ''
        
        # Remove www prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        
        return domain.lower()
    
    def _get_random_user_agent(self) -> str:
        """Get random user agent to avoid detection"""
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0'
        ]
        return random.choice(agents)
    
    def _validate_extraction(self, result: Dict[str, Any]) -> bool:
        """Validate extraction result has sufficient content"""
        if not result.get('success') or not result.get('data'):
            return False
        
        data = result['data']
        text = data.get('text', '')
        title = data.get('title', '')
        
        # Must have either substantial text or at least a title
        return (text and len(text.strip()) > 100) or (title and title != 'Unknown Title')
    
    def _process_text(self, text: str) -> Dict[str, Any]:
        """Process direct text input"""
        lines = text.strip().split('\n')
        title = lines[0][:100] if lines else 'Text Analysis'
        
        word_count = len(text.split())
        
        return {
            'success': True,
            'data': {
                'title': title,
                'text': text,
                'author': 'Unknown',
                'publish_date': '',
                'url': '',
                'domain': '',
                'description': '',
                'word_count': word_count,
                'language': '
