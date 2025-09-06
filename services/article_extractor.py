"""
Article Extractor - FIXED PRODUCTION VERSION
Date: December 2024
Last Updated: 2025-09-06
Purpose: Extract article content with proper author validation
Critical Fix: Enhanced author validation to reject non-author text like "signing up, and you agree"
Notes:
- Added comprehensive rejection patterns for non-author text
- Maintains all existing functionality
- Properly validates author names before accepting them
- Handles multi-author bylines correctly
"""

import json
import re
import time
import logging
import requests
import urllib3
from bs4 import BeautifulSoup
from typing import Dict, Optional, Any, List
from urllib.parse import urlparse
from datetime import datetime
import random
import os

# Import the base analyzer that your system uses
from services.base_analyzer import BaseAnalyzer

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class ArticleExtractor(BaseAnalyzer):
    """
    Complete article extraction with FIXED author validation
    Properly rejects non-author text like "signing up, and you agree to our"
    """
    
    def __init__(self):
        super().__init__('article_extractor')
        
        # Get ScraperAPI key from config
        try:
            from config import Config
            self.scraperapi_key = Config.SCRAPERAPI_KEY
            logger.info(f"ArticleExtractor initialized - ScraperAPI: {bool(self.scraperapi_key)}")
        except:
            self.scraperapi_key = os.getenv('SCRAPERAPI_KEY')
            logger.warning("Using environment variable for ScraperAPI key")
        
        # Initialize session for requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Site-specific author selectors - COMPREHENSIVE INCLUDING ABC NEWS
        self.author_selectors = {
            'abcnews.go.com': [
                # ABC News specific selectors
                '.News__Author',
                '.News__Byline__Author',
                'span.Byline__Author',
                '.byline__authors',
                '.authors',
                '.FITT_Article_new__authors',
                '.FITT_Article_new__byline',
                '[data-testid="byline"] span',
                '.ContentRoll__Headline__Author',
                '.ContentRoll__Headline__Date__Container span',
                # Meta tags for ABC
                'meta[name="author"]',
                'meta[property="article:author"]',
                'meta[name="DC.creator"]'
            ],
            'aljazeera.com': [
                # Al Jazeera specific selectors
                '.article-author-name',
                '.author-name',
                '.author__name',
                'span.author-link',
                '[data-author-name]',
                'meta[name="author"]',
                'meta[property="article:author"]'
            ],
            'theguardian.com': [
                # Guardian specific selectors
                'span[itemprop="name"]',
                'a[rel="author"] span',
                'a[data-link-name="auto tag link"] span',
                'address[aria-label*="author"] span',
                'div.dcr-1cfvqy6 span',
                'a[rel="author"]',
                'span.css-1rv9jn8',
                'div[data-gu-name="meta"] a span',
                'meta[name="author"]',
                'meta[property="article:author"]',
                '.contributor__name',
                '.byline span',
                '.content__meta-container span[itemprop="name"]',
                '[data-component="byline"] span',
                '[data-gu-name="byline"] span'
            ],
            'bbc.com': [
                'span.qa-contributor-name',
                'p.ssrcss-1rv9jn8-Contributor span',
                'div[data-component="byline"] span',
                '.author-unit__text',
                '.byline__name'
            ],
            'cnn.com': [
                'span.metadata__byline__author',
                'div.byline__names',
                '.Article__subtitle',
                'meta[name="author"]'
            ],
            'reuters.com': [
                'div.author-name',
                'span[class*="author"]',
                '.ArticleHeader__author',
                'meta[name="article:author"]'
            ],
            'nytimes.com': [
                'span.byline-name',
                'meta[name="byl"]',
                'p.css-1cjnqko span',
                'span[itemprop="name"]'
            ],
            'npr.org': [
                '.byline__name',
                '.byline__name a',
                '.byline__authors',
                'span.byline__name'
            ],
            'washingtonpost.com': [
                'span[data-qa="author-name"]',
                'a[data-qa="author-name"]',
                'meta[name="author"]'
            ],
            'foxnews.com': [
                '.author-byline span',
                '.article-meta-author',
                'span.author',
                'meta[name="dc.creator"]'
            ],
            'usatoday.com': [
                '.gnt_ar_by_a',
                '.gnt_ar_by',
                'a[data-c-br="native"]',
                'meta[name="news_keywords"]'
            ],
            'apnews.com': [
                '.CardHeadline-module-byline',
                '.Component-bylines',
                'span[data-key="byline"]',
                'meta[name="author"]'
            ]
        }
    
    def _check_availability(self) -> bool:
        """Check if service is available"""
        return True  # Always available with fallback methods
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis method - maintains compatibility with pipeline
        """
        logger.info("=" * 60)
        logger.info("ARTICLE EXTRACTOR - FIXED AUTHOR VALIDATION VERSION")
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
            
            # Return in BaseAnalyzer format
            if result.get('success'):
                article_data = result.get('data', {})
                
                logger.info("=== EXTRACTION COMPLETE ===")
                logger.info(f"Title: {article_data.get('title', 'Unknown')[:50]}...")
                logger.info(f"Author: {article_data.get('author', 'Unknown')}")
                logger.info(f"Domain: {article_data.get('domain', 'Unknown')}")
                logger.info(f"Word count: {article_data.get('word_count', 0)}")
                
                return self.get_success_result(article_data)
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
        best_result = None
        
        for strategy_name, strategy_func in strategies:
            try:
                logger.info(f"Trying {strategy_name}...")
                result = strategy_func(url)
                
                if result.get('success'):
                    # Special handling for specific sites
                    if 'abcnews' in url.lower() and result.get('data', {}).get('author') == 'Unknown':
                        logger.info("ABC News article detected - enhancing author extraction")
                        result = self._enhance_abc_extraction(result, url)
                    elif 'guardian' in url.lower() and result.get('data', {}).get('author') == 'Unknown':
                        logger.info("Guardian article detected - enhancing author extraction")
                        result = self._enhance_guardian_extraction(result, url)
                    elif 'aljazeera' in url.lower() and result.get('data', {}).get('author') == 'Unknown':
                        logger.info("Al Jazeera article detected - enhancing author extraction")
                        result = self._enhance_aljazeera_extraction(result, url)
                    
                    if self._validate_extraction(result):
                        logger.info(f"SUCCESS: {strategy_name} extracted content")
                        return result
                    
                # Keep best partial result
                if result.get('data', {}).get('text'):
                    if not best_result or len(result['data']['text']) > len(best_result.get('data', {}).get('text', '')):
                        best_result = result
                
                last_error = result.get('error', f'{strategy_name} failed')
                    
            except Exception as e:
                last_error = str(e)
                logger.error(f"{strategy_name} exception: {e}")
                continue
        
        # Return best partial result if available
        if best_result:
            logger.warning("Returning best partial result")
            return best_result
        
        return {
            'success': False,
            'error': f'All extraction methods failed. Last error: {last_error}'
        }
    
    def _extract_with_scraperapi(self, url: str) -> Dict[str, Any]:
        """Extract using ScraperAPI with JavaScript rendering for dynamic sites"""
        if not self.scraperapi_key:
            return {'success': False, 'error': 'ScraperAPI key not available'}
        
        try:
            params = {
                'api_key': self.scraperapi_key,
                'url': url,
                'render': 'true',  # Enable JS rendering for dynamic sites
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
            # Randomize user agent
            self.session.headers['User-Agent'] = self._get_random_user_agent()
            
            # Add referer for some sites
            domain = urlparse(url).netloc
            self.session.headers['Referer'] = f'https://{domain}/'
            
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
        """Parse HTML and extract article data"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'nav', 'aside', 'footer', 'header']):
                element.decompose()
            
            # Remove cookie banners and popups
            for selector in ['.cookie', '.gdpr', '.privacy', '.consent', '.newsletter', '.popup', '.modal']:
                for element in soup.select(selector):
                    element.decompose()
            
            # Extract components
            title = self._extract_title(soup)
            content = self._extract_content(soup)
            author = self._extract_author_universal(soup, url)
            publish_date = self._extract_publish_date(soup)
            description = self._extract_description(soup)
            
            # Calculate metrics
            word_count = len(content.split()) if content else 0
            domain = self._clean_domain(urlparse(url).netloc)
            
            logger.info(f"Extraction results - Author: {author}, Title: {title[:50]}, Words: {word_count}")
            
            return {
                'success': True,
                'data': {
                    'title': title,
                    'text': content,
                    'content': content,  # Some services expect 'content' field
                    'author': author,
                    'publish_date': publish_date,
                    'url': url,
                    'domain': domain,
                    'source': domain,  # Alias for domain
                    'description': description,
                    'word_count': word_count,
                    'language': 'en',
                    'extraction_successful': bool(content and len(content) > 100)
                },
                'extraction_metadata': {
                    'method': method,
                    'extracted_at': datetime.now().isoformat(),
                    'author_found': bool(author and author != 'Unknown')
                }
            }
            
        except Exception as e:
            logger.error(f"HTML parsing failed: {e}", exc_info=True)
            return {'success': False, 'error': f'HTML parsing failed: {str(e)}'}
    
    def _extract_author_universal(self, soup: BeautifulSoup, url: str) -> str:
        """
        Universal author extraction with FIXED validation
        """
        domain = urlparse(url).netloc.replace('www.', '')
        logger.info(f"Extracting author for domain: {domain}")
        
        # Method 1: JSON-LD Structured Data
        author = self._extract_author_from_json_ld(soup)
        if author and author != 'Unknown' and self._validate_author_name(author):
            logger.info(f"Found valid author in JSON-LD: {author}")
            return self._clean_author_name(author)
        
        # Method 2: Site-specific selectors
        site_key = None
        for key in self.author_selectors.keys():
            if key in domain:
                site_key = key
                break
        
        if site_key:
            selectors = self.author_selectors[site_key]
            for selector in selectors:
                try:
                    if selector.startswith('meta'):
                        # Handle meta tags
                        parts = selector.split('"')
                        if len(parts) >= 2:
                            attr_value = parts[1]
                            if 'name=' in selector:
                                element = soup.find('meta', attrs={'name': attr_value})
                            elif 'property=' in selector:
                                element = soup.find('meta', attrs={'property': attr_value})
                            else:
                                element = None
                            
                            if element and element.get('content'):
                                author = element['content'].strip()
                                if self._validate_author_name(author):
                                    logger.info(f"Found valid author in meta tag: {author}")
                                    return self._clean_author_name(author)
                    else:
                        # CSS selector
                        elements = soup.select(selector)
                        for element in elements:
                            text = element.get_text(strip=True)
                            if text and self._validate_author_name(text):
                                logger.info(f"Found valid author with selector {selector}: {text}")
                                return self._clean_author_name(text)
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
        
        # Method 3: Look for byline patterns
        byline_patterns = [
            # Look for elements containing "By" text
            lambda s: s.find_all(text=re.compile(r'^By\s+', re.IGNORECASE)),
            # Look for common byline classes
            lambda s: s.find_all(class_=re.compile(r'byline|author', re.IGNORECASE))
        ]
        
        for pattern_func in byline_patterns:
            elements = pattern_func(soup)
            for element in elements:
                if hasattr(element, 'parent'):
                    parent = element.parent
                    if parent:
                        full_text = parent.get_text(strip=True)
                else:
                    full_text = element.get_text(strip=True) if hasattr(element, 'get_text') else str(element)
                
                # Extract author names after "By" with support for multiple authors
                match = re.match(
                    r'^By\s+(.+?)(?:\s*[\d,]+\s*(?:January|February|March|April|May|June|July|August|September|October|November|December)|\s*\d{1,2}[:\/]\d{2}|\s*\d{4}|$)',
                    full_text,
                    re.IGNORECASE | re.DOTALL
                )
                if match:
                    authors_text = match.group(1).strip()
                    # Clean up the authors text
                    authors_text = re.sub(r'\s+', ' ', authors_text)
                    authors_text = re.sub(r',?\s+and\s+', ', ', authors_text)
                    if self._validate_author_name(authors_text):
                        logger.info(f"Found valid author in byline text: {authors_text}")
                        return self._clean_author_name(authors_text)
        
        # Method 4: Generic meta tags
        meta_selectors = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            'meta[name="byl"]',
            'meta[name="DC.creator"]',
            'meta[name="dc.creator"]',
            'meta[name="sailthru.author"]',
            'meta[name="parsely-author"]',
            'meta[name="twitter:creator"]'
        ]
        
        for selector in meta_selectors:
            element = soup.select_one(selector)
            if element:
                content = element.get('content', '').strip()
                if content and self._validate_author_name(content):
                    logger.info(f"Found valid author in generic meta: {content}")
                    return self._clean_author_name(content)
        
        # Method 5: Common byline selectors
        byline_selectors = [
            '.author', '.author-name', '.byline', '.byline-author',
            '.article-author', '.post-author', '.story-author',
            '[rel="author"]', '.vcard .fn', '.h-card .p-name',
            'span[itemprop="author"]', 'span[itemprop="name"]',
            '.contributor', '.journalist', '.reporter'
        ]
        
        for selector in byline_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if text and self._validate_author_name(text):
                    logger.info(f"Found valid author in byline: {text}")
                    return self._clean_author_name(text)
        
        logger.info("No valid author found with any method")
        return 'Unknown'
    
    def _extract_author_from_json_ld(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author from JSON-LD structured data"""
        json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
        
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                
                # Handle different JSON-LD structures
                if isinstance(data, list):
                    for item in data:
                        author = self._extract_author_from_json_object(item)
                        if author and self._validate_author_name(author):
                            return author
                else:
                    author = self._extract_author_from_json_object(data)
                    if author and self._validate_author_name(author):
                        return author
                        
            except (json.JSONDecodeError, AttributeError, TypeError):
                continue
        
        return None
    
    def _extract_author_from_json_object(self, data: dict) -> Optional[str]:
        """Extract author from a JSON-LD object"""
        if not isinstance(data, dict):
            return None
        
        # Direct author field
        if 'author' in data:
            author_data = data['author']
            
            if isinstance(author_data, str):
                return author_data
            elif isinstance(author_data, dict):
                return author_data.get('name')
            elif isinstance(author_data, list):
                authors = []
                for item in author_data:
                    if isinstance(item, str):
                        authors.append(item)
                    elif isinstance(item, dict):
                        name = item.get('name')
                        if name:
                            authors.append(name)
                if authors:
                    return ', '.join(authors)
        
        # Check @graph structure
        if '@graph' in data:
            for item in data['@graph']:
                if isinstance(item, dict) and 'author' in item:
                    return self._extract_author_from_json_object({'author': item['author']})
        
        return None
    
    def _enhance_abc_extraction(self, result: Dict[str, Any], url: str) -> Dict[str, Any]:
        """Special enhancement for ABC News articles"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://abcnews.go.com/'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try ABC-specific extraction
                author = self._extract_author_universal(soup, url)
                if author and author != 'Unknown':
                    result['data']['author'] = author
                    logger.info(f"Enhanced ABC extraction found author: {author}")
        except Exception as e:
            logger.error(f"ABC enhancement failed: {e}")
        
        return result
    
    def _enhance_guardian_extraction(self, result: Dict[str, Any], url: str) -> Dict[str, Any]:
        """Special enhancement for Guardian articles"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-GB,en;q=0.9',
                'Referer': 'https://www.theguardian.com/'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try Guardian-specific extraction
                author = self._extract_author_universal(soup, url)
                if author and author != 'Unknown':
                    result['data']['author'] = author
                    logger.info(f"Enhanced Guardian extraction found author: {author}")
        except Exception as e:
            logger.error(f"Guardian enhancement failed: {e}")
        
        return result
    
    def _enhance_aljazeera_extraction(self, result: Dict[str, Any], url: str) -> Dict[str, Any]:
        """Special enhancement for Al Jazeera articles"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.aljazeera.com/'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try Al Jazeera-specific extraction
                author = self._extract_author_universal(soup, url)
                if author and author != 'Unknown':
                    result['data']['author'] = author
                    logger.info(f"Enhanced Al Jazeera extraction found author: {author}")
        except Exception as e:
            logger.error(f"Al Jazeera enhancement failed: {e}")
        
        return result
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title"""
        selectors = [
            'h1',
            'title',
            'meta[property="og:title"]',
            'meta[name="twitter:title"]',
            '.entry-title',
            '.post-title',
            '.article-title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    title = element.get('content', '').strip()
                else:
                    title = element.get_text(strip=True)
                
                if title and len(title) > 5:
                    return re.sub(r'\s+', ' ', title)[:200]
        
        return 'Unknown Title'
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main article content"""
        content_selectors = [
            'article',
            '[role="article"]',
            '.article-body',
            '.article-content',
            '.entry-content',
            '.post-content',
            '.storytext',  # NPR
            '#storytext',  # NPR
            '.story-body',  # BBC
            'main',
            '.main-content'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                # Remove unwanted nested elements
                for unwanted in element.find_all(['aside', '.ad', '.advertisement', '.sidebar']):
                    unwanted.decompose()
                
                paragraphs = element.find_all('p')
                if paragraphs:
                    text = ' '.join([p.get_text(strip=True) for p in paragraphs])
                    if len(text) > 100:
                        return re.sub(r'\s+', ' ', text)
        
        # Fallback to all paragraphs
        paragraphs = soup.find_all('p')
        content = ' '.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
        return re.sub(r'\s+', ' ', content)
    
    def _extract_publish_date(self, soup: BeautifulSoup) -> str:
        """Extract publish date"""
        date_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="publish_date"]',
            'time[datetime]',
            '.publish-date',
            '.article-date'
        ]
        
        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                date = element.get('content') or element.get('datetime') or element.get_text(strip=True)
                if date:
                    return date[:50]
        
        return ''
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract article description"""
        desc_selectors = [
            'meta[name="description"]',
            'meta[property="og:description"]',
            'meta[name="twitter:description"]'
        ]
        
        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element:
                desc = element.get('content', '').strip()
                if desc:
                    return desc[:500]
        
        return ''
    
    def _clean_author_name(self, author: str) -> str:
        """Clean and normalize author name - handles multiple authors"""
        if not author:
            return ""
        
        # Remove common prefixes
        author = re.sub(r'^(By\s+|Written\s+by\s+|Author:\s*)', '', author, flags=re.IGNORECASE)
        
        # Handle multiple authors - preserve commas but clean "and"
        if ',' in author or ' and ' in author.lower():
            # Split by comma and "and"
            parts = re.split(r',|\s+and\s+', author, flags=re.IGNORECASE)
            # Clean each part
            cleaned_parts = []
            for part in parts:
                part = part.strip()
                if part and self._validate_author_name(part):
                    # Remove publication names from individual authors
                    for pub in ['BBC', 'CNN', 'Reuters', 'NPR', 'AP', 'ABC News', 'Guardian', 'The Guardian']:
                        part = re.sub(rf'\s*{pub}(?:\s+News)?$', '', part, flags=re.IGNORECASE)
                    part = part.strip()
                    if part:
                        cleaned_parts.append(part)
            
            # Rejoin with commas
            if cleaned_parts:
                if len(cleaned_parts) > 1:
                    # Format as "Author1, Author2, and Author3"
                    return ', '.join(cleaned_parts[:-1]) + ', and ' + cleaned_parts[-1]
                else:
                    return cleaned_parts[0]
        
        # Single author - remove publication names
        for pub in ['BBC', 'CNN', 'Reuters', 'NPR', 'AP', 'ABC News', 'Guardian', 'The Guardian']:
            author = re.sub(rf'\s*,?\s*{pub}(?:\s+News)?(?:\s*,.*)?$', '', author, flags=re.IGNORECASE)
        
        # Remove role suffixes
        author = re.sub(r'\s+(Staff\s+Writer|Correspondent|Reporter|Editor)$', '', author, flags=re.IGNORECASE)
        
        # Clean whitespace
        author = re.sub(r'\s+', ' ', author).strip(' ,-')
        
        # Convert ALL CAPS to Title Case
        if author.isupper():
            author = author.title()
        
        return author.strip()
    
    def _validate_author_name(self, text: str) -> bool:
        """
        FIXED: Validate that text looks like a real author name
        Critical fix: Rejects text containing website UI elements
        """
        if not text or len(text.strip()) < 3:
            return False
        
        # Allow longer text for multiple authors
        if ',' in text or ' and ' in text.lower():
            if len(text) > 200:  # Multiple authors can be longer
                return False
        elif len(text) > 100:  # Single author shouldn't be too long
            return False
        
        text_lower = text.strip().lower()
        
        # CRITICAL FIX: Expanded rejection patterns for website UI elements
        rejected_patterns = [
            # Website UI elements (THIS IS THE KEY FIX)
            'sign', 'signing', 'sign up', 'sign in', 'login', 'log in',
            'agree', 'agreement', 'terms', 'conditions', 'privacy', 'policy',
            'cookie', 'cookies', 'consent', 'accept', 'decline',
            'subscribe', 'subscription', 'newsletter', 'email',
            'register', 'registration', 'create account',
            'password', 'forgot', 'remember',
            'click', 'tap', 'press', 'button',
            'menu', 'navigation', 'search',
            'share', 'follow', 'like',
            'comment', 'reply', 'post',
            
            # Common non-author text
            'staff', 'editor', 'admin', 'administrator',
            'correspondent', 'contributor', 'desk',
            'team', 'group', 'department',
            'associated press', 'reuters staff',
            'unknown', 'anonymous', 'guest',
            
            # Media elements
            'photo', 'image', 'video', 'audio',
            'copyright', 'getty', 'shutterstock',
            'caption', 'credit',
            
            # Navigation elements
            'read more', 'continue', 'next', 'previous',
            'related', 'trending', 'popular',
            'home', 'about', 'contact',
            
            # Section names
            'news', 'sports', 'business', 'politics',
            'opinion', 'lifestyle', 'entertainment',
            'technology', 'science', 'health',
            
            # Social media
            'facebook', 'twitter', 'instagram',
            'youtube', 'linkedin', 'pinterest',
            
            # Legal/disclaimer text
            'disclaimer', 'legal', 'copyright',
            'all rights reserved', 'trademark'
        ]
        
        # Check each rejected pattern
        for pattern in rejected_patterns:
            if pattern in text_lower:
                logger.debug(f"Rejected author '{text}' - contains '{pattern}'")
                return False
        
        # For multiple authors, check each part
        if ',' in text or ' and ' in text_lower:
            parts = re.split(r',|\s+and\s+', text, flags=re.IGNORECASE)
            for part in parts:
                part = part.strip().lower()
                for pattern in rejected_patterns:
                    if pattern in part:
                        logger.debug(f"Rejected multi-author '{text}' - part contains '{pattern}'")
                        return False
        
        # Must contain letters
        if not re.search(r'[a-zA-Z]', text):
            return False
        
        # Must contain at least one capital letter (for names)
        if not re.search(r'[A-Z]', text):
            return False
        
        # Should look like a name (has proper name pattern)
        # At least one word starting with capital letter
        name_pattern = r'[A-Z][a-z]+'
        if not re.search(name_pattern, text):
            return False
        
        return True
    
    def _clean_domain(self, domain: str) -> str:
        """Clean domain for display"""
        if domain and domain.startswith('www.'):
            domain = domain[4:]
        return domain.lower() if domain else ''
    
    def _get_random_user_agent(self) -> str:
        """Get random user agent"""
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0'
        ]
        return random.choice(agents)
    
    def _validate_extraction(self, result: Dict[str, Any]) -> bool:
        """Validate extraction result"""
        if not result.get('success') or not result.get('data'):
            return False
        
        data = result['data']
        return bool((data.get('text') and len(data['text']) > 100) or data.get('title'))
    
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
                'content': text,
                'author': 'Unknown',
                'publish_date': '',
                'url': '',
                'domain': '',
                'source': '',
                'description': '',
                'word_count': word_count,
                'language': 'en',
                'extraction_successful': True
            }
        }
