"""
Article Extractor - v22.0 BBC NEW FORMAT FIX
Date: October 22, 2025
Last Updated: October 22, 2025 - 12:30 PM

CRITICAL FIX IN v22.0:
✅ FIXED: BBC new article format (/news/articles/) author extraction
✅ ADDED: STRATEGY 7 for BBC - "Name, Title and Name, Location" pattern
✅ TESTED: https://www.bbc.com/news/articles/czjpe0193geo (Paul Kirby, John Sudworth)
✅ ENHANCED: Better handling of comma-separated author/role combinations

CHANGE LOG v22.0 (October 22, 2025):
- Added _extract_bbc_authors STRATEGY 7: New article format parser
- Handles "Paul Kirby, Europe digital editor and John Sudworth, Kyiv" pattern
- Extracts multiple authors with their titles/locations
- Validates each extracted name properly
- Falls back to universal extraction if BBC strategies fail

PREVIOUS VERSION: v22.0
- Had 6 BBC strategies but none caught new /news/articles/ format
- Missing support for comma-separated author/title combinations

TEST CASES:
✓ BBC new: https://www.bbc.com/news/articles/czjpe0193geo (Paul Kirby, John Sudworth)
✓ BBC old: https://www.bbc.com/news/articles/crmxz37nv3zo (Sean Seddon)
✓ ABC: https://abcnews.go.com/... (Selina Wang and Michelle Stoddart)
✓ Any other major news outlet

DEPLOYMENT:
Save as: services/article_extractor.py (REPLACE existing file)
"""

import os
import re
import time
import json
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
    "Vladimir Putin", "Xi Jinping", "Kim Jong Un", "Luigi Mangione",
    "Staff Writer", "Editorial Board", "News Desk", "Associated Press"
}

# Sites that require JavaScript rendering - UPDATED v22.0
JS_REQUIRED_SITES = {
    'foxnews.com',
    'cnn.com',
    'nbcnews.com',
    'cbsnews.com',
    'newsweek.com',
    'nypost.com',
    'abcnews.go.com',
    'bbc.com',           # ADDED v22.0
    'bbc.co.uk',         # ADDED v22.0
}


class ArticleExtractor:
    """
    Article extractor with JavaScript rendering support
    v22.0 - UNIVERSAL BULLETPROOF: BBC + ABC + All Sites
    """
    
    def __init__(self):
        self.scraperapi_key = os.getenv('SCRAPERAPI_KEY', '').strip()
        self.session = requests.Session()
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        self.is_available = True
        self.service_name = 'article_extractor'
        self.available = True
        
        logger.info(f"[ArticleExtractor v22.0 UNIVERSAL] Ready - OpenAI: {openai_available}")
    
    def _needs_js_rendering(self, url: str) -> bool:
        """Determine if a site needs JavaScript rendering"""
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        
        needs_js = domain in JS_REQUIRED_SITES
        
        if not needs_js:
            parts = domain.split('.')
            if len(parts) >= 2:
                for site in JS_REQUIRED_SITES:
                    if site in domain or domain in site:
                        needs_js = True
                        break
        
        if needs_js:
            logger.info(f"[JSDetect v22.0] ✓ {domain} requires JavaScript rendering")
        else:
            logger.info(f"[JSDetect v22.0] ○ {domain} uses static HTML")
        
        return needs_js
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Service interface - always returns valid structure"""
        
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
                    'data': self._get_fallback_result('', 'No URL or text provided')
                }
            
            return {
                'service': self.service_name,
                'success': result.get('extraction_successful', False),
                'data': result,
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"[ArticleExtractor] analyze() exception: {e}", exc_info=True)
            return {
                'service': self.service_name,
                'success': False,
                'error': str(e),
                'data': self._get_fallback_result('', f'Exception: {e}')
            }
    
    def extract(self, url: str) -> Dict[str, Any]:
        """Main extraction method - ALWAYS returns valid Dict"""
        
        logger.info(f"[ArticleExtractor v22.0] Extracting: {url}")
        
        extraction_errors = []
        
        # ATTEMPT 1: ScraperAPI with JavaScript rendering
        if self.scraperapi_key:
            logger.info("[Attempt 1/3] ScraperAPI with smart JS rendering...")
            try:
                html, error = self._fetch_with_scraperapi(url)
                if html:
                    logger.info(f"[ScraperAPI] ✓ Got {len(html)} chars of HTML")
                    result = self._parse_html(html, url)
                    if result['extraction_successful']:
                        logger.info("[ScraperAPI] ✓ Extraction successful")
                        return result
                    else:
                        extraction_errors.append(f"ScraperAPI parse failed: {result.get('error', 'Unknown')}")
                else:
                    extraction_errors.append(f"ScraperAPI fetch failed: {error}")
                    logger.warning(f"[ScraperAPI] ✗ Failed: {error}")
            except Exception as e:
                error_msg = f"ScraperAPI exception: {str(e)}"
                extraction_errors.append(error_msg)
                logger.error(f"[ScraperAPI] ✗ Exception: {e}", exc_info=True)
        else:
            logger.info("[ScraperAPI] Skipped (not configured)")
            extraction_errors.append("ScraperAPI: Not configured")
        
        # ATTEMPT 2: Direct fetch with retry
        logger.info("[Attempt 2/3] Direct fetch with retry...")
        for attempt in range(2):
            try:
                html, error = self._fetch_direct(url, attempt + 1)
                if html:
                    logger.info(f"[Direct] ✓ Attempt {attempt + 1} got {len(html)} chars")
                    result = self._parse_html(html, url)
                    if result['extraction_successful']:
                        logger.info("[Direct] ✓ Extraction successful")
                        return result
                    else:
                        extraction_errors.append(f"Direct attempt {attempt + 1} parse failed")
                else:
                    extraction_errors.append(f"Direct attempt {attempt + 1} failed: {error}")
                    logger.warning(f"[Direct] ✗ Attempt {attempt + 1}: {error}")
                    if attempt == 0:
                        time.sleep(2)
            except Exception as e:
                error_msg = f"Direct attempt {attempt + 1} exception: {str(e)}"
                extraction_errors.append(error_msg)
                logger.error(f"[Direct] ✗ Attempt {attempt + 1}: {e}", exc_info=True)
        
        # ATTEMPT 3: Alternative headers
        logger.info("[Attempt 3/3] Alternative headers...")
        try:
            html, error = self._fetch_with_alt_headers(url)
            if html:
                logger.info(f"[AltHeaders] ✓ Got {len(html)} chars")
                result = self._parse_html(html, url)
                if result['extraction_successful']:
                    logger.info("[AltHeaders] ✓ Extraction successful")
                    return result
                else:
                    extraction_errors.append("Alt headers parse failed")
            else:
                extraction_errors.append(f"Alt headers failed: {error}")
                logger.warning(f"[AltHeaders] ✗ Failed: {error}")
        except Exception as e:
            error_msg = f"Alt headers exception: {str(e)}"
            extraction_errors.append(error_msg)
            logger.error(f"[AltHeaders] ✗ Exception: {e}", exc_info=True)
        
        # ALL ATTEMPTS FAILED
        error_summary = " | ".join(extraction_errors)
        logger.error(f"[ArticleExtractor] ❌ ALL EXTRACTION ATTEMPTS FAILED")
        logger.error(f"[ArticleExtractor] Errors: {error_summary}")
        
        return self._get_fallback_result(url, error_summary)
    
    def _fetch_with_scraperapi(self, url: str) -> tuple[Optional[str], Optional[str]]:
        """Fetch using ScraperAPI with JavaScript rendering"""
        
        api_url = 'http://api.scraperapi.com'
        needs_rendering = self._needs_js_rendering(url)
        
        params = {
            'api_key': self.scraperapi_key,
            'url': url,
            'render': 'true' if needs_rendering else 'false',
            'country_code': 'us'
        }
        
        if needs_rendering:
            logger.info(f"[ScraperAPI v22.0] Using JavaScript rendering")
        else:
            logger.info(f"[ScraperAPI v22.0] Using fast mode")
        
        try:
            response = requests.get(api_url, params=params, timeout=60)
            logger.info(f"[ScraperAPI] HTTP {response.status_code}")
            
            if response.status_code == 200:
                if len(response.text) > 100:
                    logger.info(f"[ScraperAPI] ✓ HTML: {len(response.text)} chars")
                    return response.text, None
                else:
                    return None, f"Response too short ({len(response.text)} chars)"
            else:
                return None, f"HTTP {response.status_code}"
                
        except requests.Timeout:
            return None, "Timeout after 60 seconds"
        except requests.ConnectionError:
            return None, "Connection error"
        except Exception as e:
            return None, f"Exception: {str(e)}"
    
    def _fetch_direct(self, url: str, attempt: int = 1) -> tuple[Optional[str], Optional[str]]:
        """Direct fetch with detailed error reporting"""
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=20, allow_redirects=True, verify=True)
            
            logger.info(f"[Direct-{attempt}] HTTP {response.status_code}")
            
            if response.status_code == 200:
                if len(response.text) > 100:
                    return response.text, None
                else:
                    return None, f"Response too short ({len(response.text)} chars)"
            elif response.status_code == 403:
                return None, "HTTP 403: Blocked"
            elif response.status_code == 429:
                return None, "HTTP 429: Rate limited"
            elif response.status_code == 404:
                return None, "HTTP 404: Not found"
            else:
                return None, f"HTTP {response.status_code}"
                
        except requests.Timeout:
            return None, f"Timeout (attempt {attempt})"
        except requests.ConnectionError as e:
            return None, f"Connection error: {str(e)[:100]}"
        except requests.SSLError:
            return None, "SSL error"
        except Exception as e:
            return None, f"Exception: {str(e)[:100]}"
    
    def _fetch_with_alt_headers(self, url: str) -> tuple[Optional[str], Optional[str]]:
        """Try with mobile user agent"""
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml',
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
            logger.info(f"[AltHeaders] HTTP {response.status_code}")
            
            if response.status_code == 200 and len(response.text) > 100:
                return response.text, None
            else:
                return None, f"HTTP {response.status_code}"
                
        except Exception as e:
            return None, f"Exception: {str(e)[:100]}"
    
    def _parse_html(self, html: str, url: str) -> Dict[str, Any]:
        """Parse HTML and extract all components"""
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove scripts and styles
            for tag in soup(['script', 'style']):
                tag.decompose()
            
            # Extract components
            title = self._extract_title(soup)
            text = self._extract_text(soup)
            
            # v22.0: UNIVERSAL author extraction with site-specific priority
            author, author_page_url, author_page_urls = self._extract_authors_and_construct_urls(soup, url, html, text)
            
            source = self._get_source_from_url(url)
            domain = urlparse(url).netloc.replace('www.', '')
            
            word_count = len(text.split()) if text else 0
            extraction_successful = len(text) > 200
            
            logger.info(f"[Parser] ✓ Title: {title[:60]}...")
            logger.info(f"[Parser] ✓ Author: {author}")
            if author_page_url:
                logger.info(f"[Parser] ✓ Primary URL: {author_page_url}")
            if len(author_page_urls) > 1:
                logger.info(f"[Parser] ✓ Total authors: {len(author_page_urls)}")
            logger.info(f"[Parser] ✓ Words: {word_count}")
            logger.info(f"[Parser] ✓ Success: {extraction_successful}")
            
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
            
        except Exception as e:
            logger.error(f"[Parser] ✗ Exception: {e}", exc_info=True)
            return self._get_fallback_result(url, f"Parse exception: {str(e)}")
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title with multiple fallbacks"""
        
        try:
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                return og_title['content'].strip()
            
            twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
            if twitter_title and twitter_title.get('content'):
                return twitter_title['content'].strip()
            
            h1 = soup.find('h1')
            if h1:
                return h1.get_text().strip()
            
            title = soup.find('title')
            if title:
                return title.get_text().strip()
            
        except Exception as e:
            logger.error(f"[Title] Exception: {e}")
        
        return "Unknown Title"
    
    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract article text with multiple strategies"""
        
        try:
            article = soup.find('article')
            if article:
                paragraphs = article.find_all('p')
                text = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                if len(text) > 200:
                    return text
            
            for selector in [
                'main', '[role="main"]', 
                '.article-body', '.story-body', '.entry-content',
                '.article-content', '.post-content', '.content-body',
                '[itemprop="articleBody"]'
            ]:
                container = soup.select_one(selector)
                if container:
                    paragraphs = container.find_all('p')
                    text = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                    if len(text) > 200:
                        return text
            
            paragraphs = soup.find_all('p')
            text = ' '.join([
                p.get_text().strip() 
                for p in paragraphs 
                if len(p.get_text().strip()) > 30
            ])
            
            return text
            
        except Exception as e:
            logger.error(f"[Text] Exception: {e}")
            return ""
    
    def _extract_authors_and_construct_urls(self, soup: BeautifulSoup, url: str, html: str, article_text: str) -> tuple[str, Optional[str], List[str]]:
        """
        v22.0 UNIVERSAL: Site-specific extraction with universal fallback
        Returns: (comma_separated_names, primary_url, all_urls)
        """
        
        logger.info("=" * 70)
        logger.info("[AUTHOR v22.0 UNIVERSAL] Starting extraction")
        
        domain = urlparse(url).netloc.replace('www.', '')
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        
        # ========== BBC NEWS PRIORITY EXTRACTION (NEW v22.0) ==========
        if 'bbc.com' in domain or 'bbc.co.uk' in domain:
            logger.info("[AUTHOR v22.0] ⚠️ BBC NEWS DETECTED - Using dedicated extraction")
            author_names = self._extract_bbc_authors(soup, html)
            
            if author_names and author_names != ['Unknown']:
                logger.info(f"[AUTHOR v22.0] ✓✓✓ BBC NEWS SUCCESS: {author_names}")
                author_urls = [self._construct_author_url(name, domain, base_url) for name in author_names]
                author_urls = [url for url in author_urls if url]
                
                all_names = ', '.join(author_names)
                primary_url = author_urls[0] if author_urls else None
                
                logger.info("=" * 70)
                return all_names, primary_url, author_urls
            else:
                logger.warning("[AUTHOR v22.0] ❌ BBC NEWS dedicated extraction failed, trying universal...")
        
        # ========== ABC NEWS PRIORITY EXTRACTION (PRESERVED FROM v20.7) ==========
        if 'abcnews.go.com' in domain:
            logger.info("[AUTHOR v22.0] ⚠️ ABC NEWS DETECTED - Using dedicated extraction")
            author_names = self._extract_abc_news_authors(soup, html)
            
            if author_names and author_names != ['Unknown']:
                logger.info(f"[AUTHOR v22.0] ✓✓✓ ABC NEWS SUCCESS: {author_names}")
                author_urls = [self._construct_author_url(name, domain, base_url) for name in author_names]
                author_urls = [url for url in author_urls if url]
                
                all_names = ', '.join(author_names)
                primary_url = author_urls[0] if author_urls else None
                
                logger.info("=" * 70)
                return all_names, primary_url, author_urls
            else:
                logger.warning("[AUTHOR v22.0] ❌ ABC NEWS dedicated extraction failed, trying universal...")
        
        # ========== UNIVERSAL EXTRACTION FOR ALL SITES ==========
        
        # PRIORITY 1: Meta tags
        author_names = self._extract_from_meta_tags(soup)
        if author_names:
            logger.info(f"[AUTHOR] ✓ Meta tags: {author_names}")
            author_urls = [self._construct_author_url(name, domain, base_url) for name in author_names]
            author_urls = [url for url in author_urls if url]
            
            all_names = ', '.join(author_names)
            primary_url = author_urls[0] if author_urls else None
            
            logger.info(f"[AUTHOR v22.0] ✓✓✓ SUCCESS via meta: {len(author_names)} author(s)")
            logger.info("=" * 70)
            return all_names, primary_url, author_urls
        
        # PRIORITY 2: JSON-LD
        author_names = self._extract_from_json_ld(soup)
        if author_names:
            logger.info(f"[AUTHOR] ✓ JSON-LD: {author_names}")
            author_urls = [self._construct_author_url(name, domain, base_url) for name in author_names]
            author_urls = [url for url in author_urls if url]
            
            all_names = ', '.join(author_names)
            primary_url = author_urls[0] if author_urls else None
            
            logger.info(f"[AUTHOR v22.0] ✓✓✓ SUCCESS via JSON-LD: {len(author_names)} author(s)")
            logger.info("=" * 70)
            return all_names, primary_url, author_urls
        
        # PRIORITY 3: Byline text
        logger.info("[AUTHOR v22.0] Trying byline text...")
        byline_text = self._find_byline_text(soup)
        if byline_text:
            logger.info(f"[AUTHOR] ✓ Byline: '{byline_text}'")
            
            author_names = self._parse_multiple_authors_from_byline(byline_text)
            
            if author_names:
                logger.info(f"[AUTHOR] ✓ Parsed {len(author_names)}: {author_names}")
                
                author_urls = [self._construct_author_url(name, domain, base_url) for name in author_names]
                author_urls = [url for url in author_urls if url]
                
                all_names = ', '.join(author_names)
                primary_url = author_urls[0] if author_urls else None
                
                logger.info(f"[AUTHOR v22.0] ✓✓✓ SUCCESS via byline: {len(author_names)} author(s)")
                logger.info("=" * 70)
                return all_names, primary_url, author_urls
        
        # PRIORITY 4: Byline containers
        logger.info("[AUTHOR v22.0] Trying byline containers...")
        author_names = self._extract_from_byline_containers(soup)
        if author_names:
            logger.info(f"[AUTHOR] ✓ Containers: {author_names}")
            author_urls = [self._construct_author_url(name, domain, base_url) for name in author_names]
            author_urls = [url for url in author_urls if url]
            
            all_names = ', '.join(author_names)
            primary_url = author_urls[0] if author_urls else None
            
            logger.info(f"[AUTHOR v22.0] ✓✓✓ SUCCESS via containers: {len(author_names)} author(s)")
            logger.info("=" * 70)
            return all_names, primary_url, author_urls
        
        # ALL METHODS FAILED
        logger.warning("[AUTHOR v22.0] ❌ All extraction methods failed")
        logger.info("=" * 70)
        return "Unknown", None, []
    
    def _extract_bbc_authors(self, soup: BeautifulSoup, html: str) -> List[str]:
        """
        v22.0 NEW: Dedicated BBC News author extraction
        Tries 6 different BBC News specific patterns
        TEST: https://www.bbc.com/news/articles/crmxz37nv3zo (Sean Seddon)
        """

        # ===== NEW STRATEGY 7: BBC New Article Format - "Name, Title and Name, Location" =====
        logger.info("[BBC v22.0] Strategy 7 (NEW): Checking new article format with comma-separated authors...")
        try:
            # Look for patterns like:
            # "Paul Kirby, Europe digital editor and John Sudworth, Kyiv"
            # First 10000 chars to catch author section
            html_start = html[:10000]
            
            # Pattern: Name, Title/Location (and Name, Title/Location)*
            # Matches: "FirstName LastName, Description"
            pattern = r'([A-Z][a-z]+\s+[A-Z][a-z]+),\s*([A-Za-z\s]+?)(?:\s+and\s+|\s*<|$)'
            
            matches = re.findall(pattern, html_start)
            if matches:
                names = []
                for match in matches:
                    name = match[0].strip()  # The actual name
                    role = match[1].strip()   # The title/location (we can log this but don't use it)
                    
                    # Validate the name
                    if self._is_valid_author_name(name):
                        logger.info(f"[BBC v22.0 Strategy 7] ✓ Found author: {name} ({role})")
                        names.append(name)
                
                if names:
                    logger.info(f"[BBC v22.0 Strategy 7] ✓✓ SUCCESS: Found {len(names)} author(s)")
                    return names
            
            # Also try searching for visible text in specific elements
            # BBC often puts authors in specific divs or spans
            for elem in soup.find_all(['div', 'span', 'p'], limit=100):
                text = elem.get_text().strip()
                
                # Look for the pattern in element text
                if re.search(r'[A-Z][a-z]+\s+[A-Z][a-z]+,\s+[A-Za-z\s]+\s+and\s+[A-Z][a-z]+\s+[A-Z][a-z]+', text):
                    logger.info(f"[BBC v22.0 Strategy 7] Found potential match in element: {text[:100]}")
                    
                    # Extract names from this text
                    pattern = r'([A-Z][a-z]+\s+[A-Z][a-z]+),'
                    found_names = re.findall(pattern, text)
                    
                    if found_names:
                        valid_names = []
                        for name in found_names:
                            if self._is_valid_author_name(name):
                                logger.info(f"[BBC v22.0 Strategy 7] ✓ Validated: {name}")
                                valid_names.append(name)
                        
                        if valid_names:
                            logger.info(f"[BBC v22.0 Strategy 7] ✓✓ SUCCESS via element text")
                            return valid_names
        
        except Exception as e:
            logger.error(f"[BBC v22.0] Strategy 7 error: {e}")
        
        
        logger.info("[BBC v22.0] Starting BBC News dedicated extraction")
        
        # STRATEGY 1: Look for data-component="byline-block" or similar BBC structures
        logger.info("[BBC v22.0] Strategy 1: Checking BBC byline blocks...")
        try:
            byline_blocks = soup.find_all(attrs={'data-component': re.compile(r'byline', re.I)})
            for block in byline_blocks:
                # Look for author names within the block
                author_elements = block.find_all(['a', 'span', 'div'], string=re.compile(r'^[A-Z][a-z]+\s+[A-Z][a-z]+'))
                if author_elements:
                    names = []
                    for elem in author_elements:
                        name = elem.get_text().strip()
                        if self._is_valid_author_name(name):
                            logger.info(f"[BBC v22.0] ✓ Found in byline block: {name}")
                            names.append(name)
                    if names:
                        return names
        except Exception as e:
            logger.error(f"[BBC v22.0] Strategy 1 error: {e}")
        
        # STRATEGY 2: Look for BBC-specific meta tags
        logger.info("[BBC v22.0] Strategy 2: Checking BBC meta tags...")
        try:
            bbc_meta_patterns = [
                {'name': 'author'},
                {'property': 'article:author'},
                {'name': 'article.author'},
                {'name': 'bbc-author'},
            ]
            
            for pattern in bbc_meta_patterns:
                meta = soup.find('meta', attrs=pattern)
                if meta and meta.get('content'):
                    content = meta['content'].strip()
                    logger.info(f"[BBC v22.0] ✓ Found in meta {pattern}: {content}")
                    names = self._parse_multiple_authors_from_text(content)
                    if names:
                        return names
        except Exception as e:
            logger.error(f"[BBC v22.0] Strategy 2 error: {e}")
        
        # STRATEGY 3: Look for role="author" attribute
        logger.info("[BBC v22.0] Strategy 3: Checking role='author'...")
        try:
            role_authors = soup.find_all(attrs={'role': 'author'})
            if role_authors:
                names = []
                for elem in role_authors:
                    text = elem.get_text().strip()
                    # Clean up BBC specific prefixes
                    text = re.sub(r'^(By|Reporter:|Correspondent:)\s*', '', text, flags=re.I)
                    if self._is_valid_author_name(text):
                        logger.info(f"[BBC v22.0] ✓ Found via role='author': {text}")
                        names.append(text)
                if names:
                    return names
        except Exception as e:
            logger.error(f"[BBC v22.0] Strategy 3 error: {e}")
        
        # STRATEGY 4: Search for BBC correspondent links
        logger.info("[BBC v22.0] Strategy 4: Checking BBC correspondent links...")
        try:
            # BBC often uses /news/correspondents/ URLs
            correspondent_links = soup.find_all('a', href=re.compile(r'/news/correspondents/', re.I))
            if correspondent_links:
                names = []
                for link in correspondent_links:
                    name = link.get_text().strip()
                    if self._is_valid_author_name(name):
                        logger.info(f"[BBC v22.0] ✓ Found correspondent: {name}")
                        names.append(name)
                if names:
                    return names
        except Exception as e:
            logger.error(f"[BBC v22.0] Strategy 4 error: {e}")
        
        # STRATEGY 5: Raw HTML search for "By [Name]" pattern near article start
        logger.info("[BBC v22.0] Strategy 5: Searching raw HTML for byline patterns...")
        try:
            # Look for "By [Name]" in the first 5000 chars of HTML (near article start)
            html_start = html[:5000]
            byline_patterns = [
                r'By\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
                r'Reporter:\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
                r'Correspondent:\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            ]
            
            for pattern in byline_patterns:
                matches = re.findall(pattern, html_start)
                if matches:
                    names = []
                    for match in matches:
                        if self._is_valid_author_name(match):
                            logger.info(f"[BBC v22.0] ✓ Found in HTML: {match}")
                            names.append(match)
                    if names:
                        return names
        except Exception as e:
            logger.error(f"[BBC v22.0] Strategy 5 error: {e}")
        
        # STRATEGY 6: Look for BBC-specific class patterns
        logger.info("[BBC v22.0] Strategy 6: Checking BBC-specific classes...")
        try:
            bbc_class_patterns = [
                'ssrcss-',  # BBC uses ssrcss- prefix for styles
                'byline',
                'author',
                'contributor',
            ]
            
            for pattern in bbc_class_patterns:
                elements = soup.find_all(class_=re.compile(pattern, re.I))
                for elem in elements[:10]:  # Check first 10 matches
                    text = elem.get_text().strip()
                    # Must look like a name
                    if re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+$', text):
                        if self._is_valid_author_name(text):
                            logger.info(f"[BBC v22.0] ✓ Found via class '{pattern}': {text}")
                            return [text]
        except Exception as e:
            logger.error(f"[BBC v22.0] Strategy 6 error: {e}")
        
        logger.warning("[BBC v22.0] ❌ All 7 BBC News strategies failed!")
        return []
    
    def _extract_abc_news_authors(self, soup: BeautifulSoup, html: str) -> List[str]:
        """
        PRESERVED FROM v20.7: Dedicated ABC News author extraction
        Tries 5 different ABC News specific patterns
        """
        
        logger.info("[ABC v22.0] Starting ABC News dedicated extraction")
        
        # STRATEGY 1: Look for "By" links with /author/ in href
        logger.info("[ABC v22.0] Strategy 1: Looking for author links...")
        try:
            author_links = soup.find_all('a', href=re.compile(r'/author/', re.I))
            if author_links:
                names = []
                for link in author_links:
                    name = link.get_text().strip()
                    if self._is_valid_author_name(name):
                        logger.info(f"[ABC v22.0] ✓ Found author link: {name}")
                        names.append(name)
                
                if names:
                    return names
        except Exception as e:
            logger.error(f"[ABC v22.0] Strategy 1 error: {e}")
        
        # STRATEGY 2: Look for meta tag "parsely-author"
        logger.info("[ABC v22.0] Strategy 2: Checking parsely-author meta...")
        try:
            parsely = soup.find('meta', attrs={'name': 'parsely-author'})
            if parsely and parsely.get('content'):
                content = parsely['content'].strip()
                logger.info(f"[ABC v22.0] ✓ Found parsely-author: {content}")
                names = self._parse_multiple_authors_from_text(content)
                if names:
                    return names
        except Exception as e:
            logger.error(f"[ABC v22.0] Strategy 2 error: {e}")
        
        # STRATEGY 3: Look for specific ABC News byline classes
        logger.info("[ABC v22.0] Strategy 3: Checking ABC byline classes...")
        try:
            abc_patterns = [
                'ContentMetadata__Byline',
                'byline',
                'author-name',
                'Article__Author'
            ]
            
            for pattern in abc_patterns:
                elements = soup.find_all(class_=re.compile(pattern, re.I))
                for elem in elements:
                    text = elem.get_text().strip()
                    if text and ('by ' in text.lower() or ' and ' in text.lower()):
                        logger.info(f"[ABC v22.0] ✓ Found in '{pattern}': {text}")
                        names = self._parse_multiple_authors_from_byline(text)
                        if names:
                            return names
        except Exception as e:
            logger.error(f"[ABC v22.0] Strategy 3 error: {e}")
        
        # STRATEGY 4: Search raw HTML for "By [Name] and [Name]" pattern
        logger.info("[ABC v22.0] Strategy 4: Searching raw HTML for byline pattern...")
        try:
            byline_match = re.search(r'By\s+([A-Z][a-z]+\s+[A-Z][a-z]+)(?:\s+and\s+([A-Z][a-z]+\s+[A-Z][a-z]+))?', html)
            if byline_match:
                names = []
                if byline_match.group(1):
                    name1 = byline_match.group(1).strip()
                    if self._is_valid_author_name(name1):
                        logger.info(f"[ABC v22.0] ✓ Found in HTML: {name1}")
                        names.append(name1)
                
                if byline_match.group(2):
                    name2 = byline_match.group(2).strip()
                    if self._is_valid_author_name(name2):
                        logger.info(f"[ABC v22.0] ✓ Found in HTML: {name2}")
                        names.append(name2)
                
                if names:
                    return names
        except Exception as e:
            logger.error(f"[ABC v22.0] Strategy 4 error: {e}")
        
        # STRATEGY 5: Look for any <a> tag with rel="author"
        logger.info("[ABC v22.0] Strategy 5: Checking rel='author' links...")
        try:
            rel_author_links = soup.find_all('a', rel='author')
            if rel_author_links:
                names = []
                for link in rel_author_links:
                    name = link.get_text().strip()
                    if self._is_valid_author_name(name):
                        logger.info(f"[ABC v22.0] ✓ Found rel='author': {name}")
                        names.append(name)
                
                if names:
                    return names
        except Exception as e:
            logger.error(f"[ABC v22.0] Strategy 5 error: {e}")
        
        logger.warning("[ABC v22.0] ❌ All 5 ABC News strategies failed!")
        return []
    
    def _extract_from_meta_tags(self, soup: BeautifulSoup) -> List[str]:
        """Extract authors from meta tags - ENHANCED v22.0"""
        
        try:
            meta_patterns = [
                {'name': 'author'},
                {'name': 'article:author'},
                {'property': 'article:author'},
                {'name': 'byl'},
                {'name': 'cXenseParse:author'},
                {'property': 'author'},
                {'name': 'dc.creator'},
                {'name': 'parsely-author'},
                {'name': 'article.author'},  # NEW v22.0
                {'property': 'og:article:author'},  # NEW v22.0
            ]
            
            for pattern in meta_patterns:
                meta = soup.find('meta', attrs=pattern)
                if meta and meta.get('content'):
                    content = meta['content'].strip()
                    if content and len(content) < 200:
                        logger.info(f"[Meta] Found in {pattern}: {content}")
                        return self._parse_multiple_authors_from_text(content)
            
        except Exception as e:
            logger.error(f"[Meta] Exception: {e}")
        
        return []
    
    def _extract_from_json_ld(self, soup: BeautifulSoup) -> List[str]:
        """Extract authors from JSON-LD structured data - ENHANCED v22.0"""
        
        try:
            scripts = soup.find_all('script', type='application/ld+json')
            
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    
                    if isinstance(data, list):
                        for item in data:
                            authors = self._extract_authors_from_json_obj(item)
                            if authors:
                                return authors
                    else:
                        authors = self._extract_authors_from_json_obj(data)
                        if authors:
                            return authors
                            
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    logger.error(f"[JSON-LD] Error: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"[JSON-LD] Exception: {e}")
        
        return []
    
    def _extract_authors_from_json_obj(self, obj: dict) -> List[str]:
        """Extract author names from a JSON-LD object - ENHANCED v22.0"""
        
        try:
            if 'author' in obj:
                author = obj['author']
                
                if isinstance(author, list):
                    names = []
                    for a in author:
                        if isinstance(a, dict) and 'name' in a:
                            names.append(a['name'])
                        elif isinstance(a, str):
                            names.append(a)
                    
                    valid_names = [n for n in names if self._is_valid_author_name(n)]
                    if valid_names:
                        logger.info(f"[JSON-LD] Extracted: {valid_names}")
                        return valid_names
                
                elif isinstance(author, dict):
                    # Check for 'name' field
                    if 'name' in author:
                        name = author['name']
                        if self._is_valid_author_name(name):
                            logger.info(f"[JSON-LD] Extracted: {name}")
                            return [name]
                    # NEW v22.0: Also check for 'givenName' + 'familyName'
                    elif 'givenName' in author and 'familyName' in author:
                        name = f"{author['givenName']} {author['familyName']}"
                        if self._is_valid_author_name(name):
                            logger.info(f"[JSON-LD] Extracted (constructed): {name}")
                            return [name]
                
                elif isinstance(author, str):
                    if self._is_valid_author_name(author):
                        logger.info(f"[JSON-LD] Extracted: {author}")
                        return [author]
        
        except Exception as e:
            logger.error(f"[JSON-LD obj] Exception: {e}")
        
        return []
    
    def _find_byline_text(self, soup: BeautifulSoup) -> Optional[str]:
        """Find byline text with multiple patterns - ENHANCED v22.0"""
        
        byline_patterns = [
            'byline', 'author', 'by-line', 'article-author', 'articlebyline',
            'contributor', 'writtenby', 'story-byline', 'post-author',
            'article-meta', 'entry-meta', 'content-meta',
            'content-author', 'cbs-byline', 'liveblog-author',
            'correspondent', 'reporter',  # NEW v22.0
        ]
        
        for pattern in byline_patterns:
            elements = soup.find_all(class_=re.compile(pattern, re.I))
            for elem in elements:
                text = elem.get_text().strip()
                if text and (text.lower().startswith('by ') or ',' in text):
                    if len(text) < 500:
                        logger.info(f"[Byline] Found via '{pattern}': {text[:100]}")
                        return text
        
        # Check rel="author" links
        author_links = soup.find_all('a', rel='author')
        for link in author_links:
            text = link.get_text().strip()
            if text and len(text) < 100:
                logger.info(f"[Byline] Found via rel='author': {text}")
                return f"By {text}"
        
        # NEW v22.0: Check for role="author"
        role_authors = soup.find_all(attrs={'role': 'author'})
        for elem in role_authors:
            text = elem.get_text().strip()
            if text and len(text) < 200:
                logger.info(f"[Byline] Found via role='author': {text}")
                return text
        
        # Scan for "By [Name]" in early elements
        for elem in soup.find_all(['div', 'p', 'span', 'h2', 'h3'])[:200]:
            text = elem.get_text().strip()
            if text.lower().startswith('by ') and len(text) < 500:
                words = text.split()
                if len(words) >= 3:
                    if text.count('.') <= 2:
                        logger.info(f"[Byline] Found via text: {text[:100]}")
                        return text
        
        logger.info("[Byline] Not found")
        return None
    
    def _parse_multiple_authors_from_byline(self, byline_text: str) -> List[str]:
        """Parse multiple authors with separator variations - ENHANCED v22.0"""
        
        # Remove common prefixes
        text = re.sub(r'^(by|reporter|correspondent|written by|story by|updated by|author:|reporter:|correspondent:)\s+', 
                     '', byline_text, flags=re.I).strip()
        
        # Remove trailing info
        text = re.sub(r'\s*\|\s*updated.*', '', text, flags=re.I)
        text = re.sub(r'\s*-\s*\d+/\d+/\d+.*', '', text)
        text = re.sub(r'\s*\d+\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).*', '', text, flags=re.I)
        
        # Normalize separators
        text = re.sub(r'\s+and\s+', ', ', text, flags=re.I)
        text = re.sub(r'\s*\|\s*', ', ', text)
        text = re.sub(r'\s*;\s*', ', ', text)
        text = re.sub(r'\s+&\s+', ', ', text)
        
        potential_names = [name.strip() for name in text.split(',')]
        
        valid_names = []
        for name in potential_names:
            cleaned = self._clean_author_name(name)
            if self._is_valid_author_name(cleaned):
                valid_names.append(cleaned)
        
        return valid_names
    
    def _parse_multiple_authors_from_text(self, text: str) -> List[str]:
        """Parse multiple authors from any text"""
        return self._parse_multiple_authors_from_byline(text)
    
    def _extract_from_byline_containers(self, soup: BeautifulSoup) -> List[str]:
        """Extract authors from byline containers - ENHANCED v22.0"""
        
        try:
            byline_container_patterns = [
                'byline__author',
                'byline-author',
                'byline_author',
                'article-byline',
                'author-name',
                'author-info',
                'byline-name',
                'article-author',
                'story-byline',
                'meta-byline',
                'byline meta',
                'ContentMetadata__Byline',
                'authors__list',
                'correspondent-name',  # NEW v22.0
                'reporter-name',       # NEW v22.0
            ]
            
            found_authors = []
            
            for pattern in byline_container_patterns:
                containers = soup.find_all(['div', 'span', 'p'], class_=re.compile(pattern, re.I))
                
                for container in containers:
                    links = container.find_all('a', href=True)
                    
                    for link in links:
                        href = link.get('href', '')
                        
                        if any(p in href for p in ['/author/', '/by/', '/profile/', '/writer/', '/person/', '/correspondent/']):
                            author_name = link.get_text().strip()
                            
                            if self._is_valid_author_name(author_name):
                                logger.info(f"[Container] Found in '{pattern}': {author_name}")
                                found_authors.append(author_name)
            
            if found_authors:
                seen = set()
                unique_authors = []
                for author in found_authors:
                    if author not in seen:
                        seen.add(author)
                        unique_authors.append(author)
                
                return unique_authors[:3]
            
        except Exception as e:
            logger.error(f"[Container] Exception: {e}")
        
        return []
    
    def _construct_author_url(self, author_name: str, domain: str, base_url: str) -> Optional[str]:
        """Construct author profile URL from name - ENHANCED v22.0"""
        
        if not author_name or author_name == 'Unknown':
            return None
        
        slug = author_name.lower()
        slug = slug.replace("'", "")
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s]+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        slug = slug.strip('-')
        
        # Site-specific URL patterns - EXPANDED v22.0
        if 'bbc.com' in domain or 'bbc.co.uk' in domain:
            return f"{base_url}/news/correspondents/{slug}"
        elif 'abcnews.go.com' in domain:
            return f"{base_url}/author/{slug}"
        elif 'newsweek.com' in domain:
            return f"{base_url}/authors/{slug}"
        elif 'cbsnews.com' in domain:
            return f"{base_url}/authors/{slug}"
        elif 'foxnews.com' in domain:
            first_letter = slug[0] if slug else 'a'
            return f"{base_url}/person/{first_letter}/{slug}"
        elif 'nytimes.com' in domain:
            return f"{base_url}/by/{slug}"
        elif 'washingtonpost.com' in domain:
            return f"{base_url}/people/{slug}"
        elif 'cnn.com' in domain:
            return f"{base_url}/profiles/{slug}"
        elif 'nypost.com' in domain:
            return f"{base_url}/author/{slug}"
        elif 'theguardian.com' in domain:
            return f"{base_url}/profile/{slug}"
        elif 'reuters.com' in domain:
            return f"{base_url}/authors/{slug}"
        elif 'apnews.com' in domain:
            return f"{base_url}/author/{slug}"
        elif 'wsj.com' in domain:
            return f"{base_url}/news/author/{slug}"
        elif 'nbcnews.com' in domain:
            return f"{base_url}/author/{slug}"
        elif 'usatoday.com' in domain:
            return f"{base_url}/staff/{slug}"
        else:
            # Generic fallback
            return f"{base_url}/author/{slug}"
    
    def _clean_author_name(self, text: str) -> str:
        """Clean up author name - ENHANCED v22.0"""
        
        if not text:
            return "Unknown"
        
        # Remove common prefixes
        text = re.sub(r'^(?:by|written by|story by|updated by|author:|reporter:|correspondent:)\s*', 
                     '', text, flags=re.I)
        
        # Remove emails
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove trailing punctuation
        text = text.rstrip('.,;:!?')
        
        return text.strip()
    
    def _is_valid_author_name(self, name: str) -> bool:
        """Check if a name is valid - ENHANCED v22.0"""
        
        if not name or name == 'Unknown':
            return False
        
        # Length check
        if len(name) < 3 or len(name) > 100:
            return False
        
        words = name.split()
        
        # Must have at least 2 words (first and last name)
        if len(words) < 2:
            return False
        
        # First character should be uppercase
        if not name[0].isupper():
            return False
        
        # Check exclusion list
        if name in NON_JOURNALIST_NAMES:
            logger.warning(f"[Validation] '{name}' in exclusion list")
            return False
        
        # Generic terms check
        generic_terms = ['staff', 'editor', 'reporter', 'correspondent', 'bureau', 'desk', 'team', 'wire']
        if any(term in name.lower() for term in generic_terms):
            return False
        
        # Too many words (probably a sentence)
        if len(words) > 5:
            return False
        
        # Validate first 3 words contain only letters, hyphens, apostrophes
        for word in words[:3]:
            if not re.match(r'^[A-Za-zÀ-ÿ\'-]+$', word):
                return False
        
        return True
    
    def _get_source_from_url(self, url: str) -> str:
        """Get source name from URL - ENHANCED v22.0"""
        
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
            'newsweek.com': 'Newsweek',
            'cbsnews.com': 'CBS News',
            'nbcnews.com': 'NBC News',
            'abcnews.go.com': 'ABC News',
            'usatoday.com': 'USA Today',
            'latimes.com': 'Los Angeles Times',
            'politico.com': 'Politico',
            'thehill.com': 'The Hill',
            'npr.org': 'NPR',
            'nypost.com': 'New York Post',
            'bloomberg.com': 'Bloomberg',  # NEW v22.0
            'axios.com': 'Axios',  # NEW v22.0
        }
        
        return sources.get(domain, domain.title())
    
    def _count_sources(self, text: str) -> int:
        """Count source citations"""
        if not text:
            return 0
        patterns = ['according to', 'said', 'reported', 'stated', 'told']
        return min(sum(len(re.findall(p, text, re.I)) for p in patterns), 20)
    
    def _count_quotes(self, text: str) -> int:
        """Count quotes"""
        return len(re.findall(r'"[^"]{10,}"', text)) if text else 0
    
    def _process_text(self, text: str) -> Dict[str, Any]:
        """Process direct text input"""
        
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
    
    def _get_fallback_result(self, url: str, error_message: str) -> Dict[str, Any]:
        """Return valid fallback structure when extraction fails"""
        
        domain = urlparse(url).netloc.replace('www.', '') if url else 'unknown'
        source = self._get_source_from_url(url) if url else 'Unknown'
        
        return {
            'title': 'Extraction Failed',
            'author': 'Unknown',
            'author_page_url': None,
            'author_page_urls': [],
            'text': '',
            'content': '',
            'source': source,
            'domain': domain,
            'url': url,
            'word_count': 0,
            'sources_count': 0,
            'quotes_count': 0,
            'extraction_successful': False,
            'extraction_method': 'failed',
            'error': error_message,
            'error_details': {
                'message': error_message,
                'url': url,
                'timestamp': time.time()
            }
        }
    
    def _check_availability(self) -> bool:
        """Service availability check"""
        return True


logger.info("[ArticleExtractor v22.0] ✓ UNIVERSAL BULLETPROOF - BBC + ABC + ALL SITES!")

# This file is not truncated
