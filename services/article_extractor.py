"""
Article Extractor Service - ENHANCED BBC AUTHOR EXTRACTION
Date: September 7, 2025
Last Updated: September 7, 2025

FIXES:
- Enhanced BBC author extraction for their specific byline format
- Handles multi-author articles
- Extracts authors from inline text patterns
- Cleans author names from roles and locations
"""
import os
import re
import json
import time
import logging
import requests
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Check for BeautifulSoup
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    logger.error("BeautifulSoup not available")


class ArticleExtractor:
    """
    Complete article extraction service with enhanced BBC author support
    """
    
    def __init__(self):
        """Initialize the article extractor"""
        self.service_name = 'article_extractor'
        self.available = True
        self.is_available = True
        
        # Get API keys
        self.scraperapi_key = os.environ.get('SCRAPERAPI_KEY')
        
        # Session for requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Author selectors for different domains
        self.author_selectors = {
            'bbc.com': [
                'span.ssrcss-68pt20-Text-TextContributorName',
                'div.ssrcss-68pt20-Text-TextContributorName',
                'span[class*="TextContributorName"]',
                'div[class*="TextContributorName"]',
                'div.byline',
                'span.byline__name',
                'p[class*="Contributor"]',
                'div[class*="contributor"]',
                'span.qa-contributor-name'
            ],
            'bbc.co.uk': [  # Same as bbc.com
                'span.ssrcss-68pt20-Text-TextContributorName',
                'div.ssrcss-68pt20-Text-TextContributorName',
                'span[class*="TextContributorName"]',
                'div[class*="TextContributorName"]',
                'div.byline',
                'span.byline__name',
                'p[class*="Contributor"]',
                'div[class*="contributor"]',
                'span.qa-contributor-name'
            ],
            'cnn.com': [
                'span.byline__name',
                'div.byline__names',
                'span.metadata__byline__author'
            ],
            'reuters.com': [
                'div.author-name',
                'span.author-name',
                'div.ArticleHeader__author'
            ],
            'chicagotribune.com': [
                'span.byline',
                'div.byline',
                'span[class*="author"]',
                'div[class*="author"]'
            ]
        }
        
        logger.info(f"ArticleExtractor initialized - ScraperAPI: {'✓' if self.scraperapi_key else '✗'}")
    
    def _check_availability(self) -> bool:
        """
        REQUIRED METHOD - Check if service is available
        This method is required by BaseAnalyzer abstract class
        """
        return BS4_AVAILABLE
    
    def check_service(self) -> bool:
        """Check if service is operational"""
        return self._check_availability()
    
    def get_success_result(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Return success result"""
        return {
            'success': True,
            'data': data,
            'service': self.service_name,
            'available': True,
            'timestamp': time.time(),
            'analysis_complete': True
        }
    
    def get_error_result(self, error_message: str) -> Dict[str, Any]:
        """Return error result"""
        return {
            'success': False,
            'error': error_message,
            'service': self.service_name,
            'available': self.available,
            'timestamp': time.time()
        }
    
    def get_default_result(self) -> Dict[str, Any]:
        """Return default result when service unavailable"""
        return {
            'success': False,
            'service': self.service_name,
            'available': False,
            'error': 'Service unavailable',
            'timestamp': time.time()
        }
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        return {
            'name': self.service_name,
            'available': self.available,
            'enabled': True
        }
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis method - extracts article from URL
        """
        try:
            logger.info("=" * 60)
            logger.info("ARTICLE EXTRACTOR - STARTING")
            logger.info("=" * 60)
            
            # Check BeautifulSoup
            if not BS4_AVAILABLE:
                return self.get_error_result("BeautifulSoup not available")
            
            # Get URL
            url = data.get('url')
            if not url:
                return self.get_error_result("No URL provided")
            
            logger.info(f"Extracting from URL: {url}")
            
            # Try extraction methods
            extracted_data = None
            
            # Method 1: ScraperAPI
            if self.scraperapi_key:
                extracted_data = self._extract_with_scraperapi(url)
            
            # Method 2: Direct request
            if not extracted_data:
                extracted_data = self._extract_with_requests(url)
            
            # Return result
            if extracted_data:
                logger.info(f"SUCCESS - Extracted: {extracted_data.get('title', 'Unknown')[:50]}")
                logger.info(f"Author: {extracted_data.get('author', 'Unknown')}")
                return self.get_success_result(extracted_data)
            else:
                return self.get_error_result("All extraction methods failed")
                
        except Exception as e:
            logger.error(f"Article extraction error: {e}")
            return self.get_error_result(str(e))
    
    def _extract_with_scraperapi(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract using ScraperAPI"""
        try:
            logger.info("Trying scraperapi...")
            
            api_url = "http://api.scraperapi.com"
            params = {
                'api_key': self.scraperapi_key,
                'url': url,
                'render': 'false'
            }
            
            response = requests.get(api_url, params=params, timeout=30)
            response.raise_for_status()
            
            return self._parse_html(response.text, url, 'scraperapi')
            
        except Exception as e:
            logger.error(f"ScraperAPI failed: {e}")
            return None
    
    def _extract_with_requests(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract using direct requests"""
        try:
            logger.info("Trying enhanced_requests...")
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            return self._parse_html(response.text, url, 'enhanced_requests')
            
        except Exception as e:
            logger.error(f"Requests extraction failed: {e}")
            return None
    
    def _parse_html(self, html: str, url: str, method: str) -> Optional[Dict[str, Any]]:
        """Parse HTML and extract article data"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract components
            title = self._extract_title(soup)
            author = self._extract_author(soup, url)
            content = self._extract_content(soup)
            
            # Get domain
            domain = urlparse(url).netloc.replace('www.', '')
            
            # Validate
            if not content or len(content) < 100:
                logger.warning(f"{method} insufficient content")
                return None
            
            logger.info(f"Extraction results - Author: {author}, Title: {title[:50]}, Words: {len(content.split())}")
            logger.info(f"SUCCESS: {method} extracted content")
            
            return {
                'title': title,
                'author': author,
                'content': content,
                'text': content,
                'url': url,
                'domain': domain,
                'source': domain,
                'word_count': len(content.split()),
                'extraction_method': method,
                'extraction_successful': True,
                'analysis_complete': True
            }
            
        except Exception as e:
            logger.error(f"HTML parsing failed: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title"""
        # Try OpenGraph
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        
        # Try h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)
        
        # Try title tag
        title = soup.find('title')
        if title:
            text = title.get_text(strip=True)
            return text.split(' - ')[0].split(' | ')[0]
        
        return "No title found"
    
    def _extract_author(self, soup: BeautifulSoup, url: str) -> str:
        """Enhanced author extraction with BBC support"""
        domain = urlparse(url).netloc.replace('www.', '')
        
        logger.info(f"Extracting author for domain: {domain}")
        
        # Special handling for BBC
        if 'bbc.com' in domain or 'bbc.co.uk' in domain:
            authors = self._extract_bbc_authors(soup, html_text=str(soup))
            if authors:
                # Join multiple authors with " and "
                author_string = ' and '.join(authors)
                logger.info(f"Found BBC author(s): {author_string}")
                return author_string
        
        # Try domain-specific selectors
        if domain in self.author_selectors:
            for selector in self.author_selectors[domain]:
                try:
                    element = soup.select_one(selector)
                    if element:
                        author = element.get_text(strip=True)
                        author = self._clean_author_text(author)
                        if author and len(author) > 2 and len(author) < 100:
                            logger.info(f"Found valid author via selector: {author}")
                            return author
                except:
                    pass
        
        # Try meta tags
        for name in ['author', 'article:author', 'dc.creator', 'byl']:
            meta = soup.find('meta', attrs={'name': name}) or \
                   soup.find('meta', attrs={'property': name})
            if meta and meta.get('content'):
                author = meta['content'].strip()
                author = self._clean_author_text(author)
                if author and len(author) > 2:
                    logger.info(f"Found valid author in meta tag: {author}")
                    return author
        
        # Try common patterns
        for element in soup.find_all(class_=re.compile(r'byline|author|contributor', re.I))[:10]:
            text = element.get_text(strip=True)
            text = self._clean_author_text(text)
            if text and len(text) > 2 and len(text) < 100:
                # Check if it's actually a name (contains letters, not just roles)
                if re.search(r'[A-Z][a-z]+\s+[A-Z][a-z]+', text):
                    logger.info(f"Found valid author via pattern: {text}")
                    return text
        
        logger.info("No valid author found with any method")
        return "Unknown"
    
    def _extract_bbc_authors(self, soup: BeautifulSoup, html_text: str = "") -> List[str]:
        """
        Special extraction for BBC's unique author format
        BBC often shows authors as:
        "Rushdi Abualouf Gaza correspondent reporting from Istanbul and Wyre Davies BBC News, Jerusalem"
        """
        authors = []
        
        # Method 1: Look for the author paragraph pattern in BBC articles
        # BBC often has authors in a specific paragraph near the top
        for p in soup.find_all('p')[:20]:  # Check first 20 paragraphs
            text = p.get_text(strip=True)
            
            # Pattern 1: "Name Role reporting from Location"
            # Pattern 2: "Name BBC News, Location"
            # Pattern 3: Multiple authors with "and" between them
            
            # Check if this looks like an author line
            if any(keyword in text.lower() for keyword in ['correspondent', 'reporting from', 'bbc news', 'editor', 'reporter']):
                # Extract names using patterns
                
                # Pattern for "Rushdi Abualouf Gaza correspondent"
                pattern1 = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)(?:\s+[A-Za-z]+\s+correspondent|\s+BBC\s+News|\s+reporter|\s+editor)'
                
                # Pattern for names at the beginning of the text
                pattern2 = r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'
                
                # Find all matches
                matches = re.findall(pattern1, text)
                if not matches:
                    matches = re.findall(pattern2, text)
                
                for match in matches:
                    # Clean the name
                    name = match.strip()
                    # Filter out common non-name words
                    if name and not any(skip in name.lower() for skip in ['bbc', 'news', 'correspondent', 'editor', 'reporter']):
                        if len(name.split()) >= 2:  # At least first and last name
                            authors.append(name)
                
                # If we found authors in this paragraph, we're done
                if authors:
                    break
        
        # Method 2: Look for specific BBC author elements
        if not authors:
            # Try contributor name classes
            for selector in ['span[class*="Contributor"]', 'div[class*="contributor"]', 'p[class*="contributor"]']:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    # Extract just the name part
                    name_match = re.match(r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', text)
                    if name_match:
                        authors.append(name_match.group(1))
        
        # Method 3: Check the article text for the specific format from your example
        if not authors and html_text:
            # Look for the exact pattern from your BBC article
            patterns = [
                r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+Gaza correspondent',
                r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+BBC News',
                r'By\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html_text)
                for match in matches:
                    if match and match not in authors:
                        authors.append(match)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_authors = []
        for author in authors:
            if author not in seen:
                seen.add(author)
                unique_authors.append(author)
        
        return unique_authors[:2]  # Return max 2 authors for BBC articles
    
    def _clean_author_text(self, text: str) -> str:
        """Clean author text"""
        if not text:
            return ""
        
        # Remove common prefixes
        text = re.sub(r'^(By|Written by|Author:|Reporter:)\s+', '', text, flags=re.I)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+\.\S+', '', text)
        
        # Remove dates
        text = re.sub(r'\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)', '', text, flags=re.I)
        
        # Remove "Updated" timestamps
        text = re.sub(r'(UPDATED|PUBLISHED|POSTED).*', '', text, flags=re.I)
        
        # Remove role descriptions after name (but keep the name)
        text = re.sub(r',\s*(Reporter|Writer|Journalist|Editor|Correspondent|Staff Writer).*', '', text, flags=re.I)
        
        # Clean up
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
        
        return text
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract content"""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Try article tag
        article = soup.find('article')
        if article:
            paragraphs = article.find_all('p')
            if paragraphs:
                content = ' '.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
                if len(content) > 200:
                    return content
        
        # Try main areas
        for selector in ['main', 'div[role="main"]', 'div.content', 'div[class*="article-body"]', 'div[class*="story-body"]']:
            element = soup.select_one(selector)
            if element:
                paragraphs = element.find_all('p')
                if paragraphs:
                    content = ' '.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
                    if len(content) > 200:
                        return content
        
        # Fallback: all paragraphs
        all_p = soup.find_all('p')
        content = ' '.join([p.get_text(strip=True) for p in all_p if len(p.get_text(strip=True)) > 30])
        return content
