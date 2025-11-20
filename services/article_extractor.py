"""
Article Extractor - v24.2 OUTLET NAME REJECTION FIX
Date: October 26, 2025
Last Updated: November 20, 2025

CHANGES IN v24.2 (November 20, 2025):
✅ CRITICAL FIX: Added OUTLET_NAMES set to reject outlet names as authors
✅ FIX: "MSNBC" and other network names now rejected as invalid author names
✅ ADDED: 50+ outlet names/acronyms to rejection list
✅ ENHANCED: _is_valid_author_name() now checks against OUTLET_NAMES
✅ PRESERVED: All v24.1 functionality (MS.NOW domain support)

ISSUE FIXED:
- User reported MS.NOW articles showing "MSNBC" as author instead of real journalist
- Root cause: _is_valid_author_name() didn't reject outlet names
- Solution: Added OUTLET_NAMES set and check in validation
- Result: "MSNBC", "CNN", "BBC", etc. now rejected as author names

PREVIOUS CHANGES v24.1 (November 19, 2025):
✅ ADDED: 'msnbc.com': 'MSNBC' and 'ms.now': 'MSNBC' to source name mapping
✅ FIX: MS.NOW articles now display source name correctly

PREVIOUS UPDATE v24.0 (October 26, 2025):
✅ MIGRATED: ScraperAPI → ScrapingBee (better YouTube support)
✅ ADDED: Native YouTube video scraping support  
✅ ENHANCED: Better JavaScript rendering with premium proxies

Save as: services/article_extractor.py (REPLACE existing file)
I did no harm and this file is not truncated.
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

# NEW IN v24.2: Outlet names/acronyms to reject as author names
# These are NOT valid author names - they are news organizations
OUTLET_NAMES = {
    # TV Networks & Cable
    "MSNBC", "CNN", "BBC", "NBC", "CBS", "ABC", "Fox", "PBS", "NPR",
    "Fox News", "NBC News", "CBS News", "ABC News", "BBC News",
    "CNBC", "C-SPAN", "Al Jazeera", "Sky News", "Bloomberg",
    
    # Major Newspapers
    "Reuters", "Associated Press", "AP", "AFP", "UPI",
    "The New York Times", "New York Times", "NYT", "NY Times",
    "Washington Post", "The Washington Post", "WaPo",
    "Wall Street Journal", "The Wall Street Journal", "WSJ",
    "Los Angeles Times", "LA Times", "Chicago Tribune",
    "USA Today", "New York Post", "NY Post", "Boston Globe",
    
    # Digital/Online
    "Politico", "The Hill", "Axios", "Vox", "Vice", "BuzzFeed",
    "HuffPost", "Huffington Post", "The Daily Beast", "Slate",
    "Salon", "The Atlantic", "The New Yorker", "Time", "Newsweek",
    "The Guardian", "The Independent", "Daily Mail", "The Telegraph",
    
    # Tech/Business
    "TechCrunch", "The Verge", "Wired", "Ars Technica", "Engadget",
    "Forbes", "Fortune", "Business Insider", "MarketWatch",
    
    # Generic terms that appear as "authors"
    "Staff", "Editorial", "Staff Writer", "Staff Report", "Wire Services",
    "News Staff", "Editorial Board", "Editorial Staff", "Newsroom",
    "News Team", "Web Staff", "Digital Staff", "Breaking News",
    "Special Report", "Exclusive", "Analysis", "Opinion",
    
    # Common false positives
    "Admin", "Administrator", "Webmaster", "Editor", "Editors",
    "Contributor", "Contributors", "Guest", "Anonymous",
}

# Common words that look like names but aren't (prevents "The Earth" false positives)
COMMON_NON_NAME_WORDS = {
    # Articles and determiners
    "The", "A", "An", "This", "That", "These", "Those",
    # Places/concepts that get capitalized
    "Earth", "World", "Nation", "Country", "State", "City", "Town",
    "North", "South", "East", "West", "America", "Europe", "Asia", "Africa",
    # Organizations/institutions (when not part of full name)
    "House", "Senate", "Congress", "Court", "Department", "Agency",
    # Time periods
    "Today", "Tomorrow", "Yesterday", "Morning", "Evening", "Night",
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
    "January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December",
    # Publication types
    "Times", "Post", "News", "Press", "Journal", "Tribune", "Herald",
    "Gazette", "Observer", "Chronicle", "Examiner", "Dispatch",
    # Generic roles (already covered but adding here for clarity)
    "Editor", "Reporter", "Correspondent", "Journalist", "Writer", "Author",
    # Common words that appear capitalized
    "President", "Senator", "Governor", "Mayor", "Chief", "Director",
    # Other common false positives
    "Online", "Digital", "Video", "Photo", "Story", "Article", "Report"
}

# Sites that require JavaScript rendering
JS_REQUIRED_SITES = {
    'foxnews.com',
    'cnn.com',
    'nbcnews.com',
    'cbsnews.com',
    'newsweek.com',
    'nypost.com',
    'abcnews.go.com',
    'bbc.com',
    'bbc.co.uk',
    'youtube.com',
    'youtu.be',
    'msnbc.com',
    'ms.now',
}


class ArticleExtractor:
    """
    Article extractor with JavaScript rendering support
    v24.2 - OUTLET NAME REJECTION FIX
    v24.1 - MS.NOW domain support added
    v23.1 - ENHANCED NAME VALIDATION: Rejects false positives
    """
    
    def __init__(self):
        self.scrapingbee_api_key = os.getenv('SCRAPINGBEE_API_KEY', '').strip()
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
        
        logger.info(f"[ArticleExtractor v24.2 OUTLET FIX] Ready - OpenAI: {openai_available}, ScrapingBee: {bool(self.scrapingbee_api_key)}")
    
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
            logger.info(f"[JSDetect v24.2] ✓ {domain} requires JavaScript rendering")
        else:
            logger.info(f"[JSDetect v24.2] ○ {domain} uses static HTML")
        
        return needs_js
    
    def _is_youtube_url(self, url: str) -> bool:
        """Check if URL is a YouTube video"""
        youtube_patterns = [
            'youtube.com/watch',
            'youtu.be/',
            'youtube.com/embed/',
            'youtube.com/v/',
        ]
        is_youtube = any(pattern in url.lower() for pattern in youtube_patterns)
        if is_youtube:
            logger.info(f"[YouTube Detection v24.2] ✓ YouTube URL detected")
        return is_youtube
    
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
        
        logger.info(f"[ArticleExtractor v24.2] Extracting: {url}")
        
        extraction_errors = []
        
        # ATTEMPT 1: ScrapingBee with JavaScript rendering
        if self.scrapingbee_api_key:
            logger.info("[Attempt 1/3] ScrapingBee with smart JS rendering...")
            try:
                html, error = self._fetch_with_scrapingbee(url)
                if html:
                    logger.info(f"[ScrapingBee] ✓ Got {len(html)} chars of HTML")
                    result = self._parse_html(html, url)
                    if result['extraction_successful']:
                        logger.info("[ScrapingBee] ✓ Extraction successful")
                        return result
                    else:
                        extraction_errors.append(f"ScrapingBee parse failed: {result.get('error', 'Unknown')}")
                else:
                    extraction_errors.append(f"ScrapingBee fetch failed: {error}")
                    logger.warning(f"[ScrapingBee] ✗ Failed: {error}")
            except Exception as e:
                error_msg = f"ScrapingBee exception: {str(e)}"
                extraction_errors.append(error_msg)
                logger.error(f"[ScrapingBee] ✗ Exception: {e}", exc_info=True)
        else:
            logger.info("[ScrapingBee] Skipped (not configured)")
            extraction_errors.append("ScrapingBee: Not configured")
        
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
                logger.error(f"[Direct] ✗ Attempt {attempt + 1} exception: {e}", exc_info=True)
        
        # ATTEMPT 3: OpenAI fallback (if available)
        if openai_available and url:
            logger.info("[Attempt 3/3] OpenAI intelligent extraction...")
            try:
                ai_result = self._openai_extract(url)
                if ai_result and ai_result.get('extraction_successful'):
                    logger.info("[OpenAI] ✓ Extraction successful")
                    return ai_result
                else:
                    extraction_errors.append("OpenAI: Failed or not available")
            except Exception as e:
                error_msg = f"OpenAI exception: {str(e)}"
                extraction_errors.append(error_msg)
                logger.error(f"[OpenAI] ✗ Exception: {e}", exc_info=True)
        else:
            logger.info("[OpenAI] Skipped (not available)")
            extraction_errors.append("OpenAI: Not available")
        
        # All attempts failed
        combined_errors = " | ".join(extraction_errors)
        logger.error(f"[ArticleExtractor] ❌ All extraction attempts failed: {combined_errors}")
        return self._get_fallback_result(url, combined_errors)
    
    def _fetch_with_scrapingbee(self, url: str) -> tuple:
        """Fetch using ScrapingBee with smart JS rendering"""
        
        try:
            # Determine if JavaScript is needed
            needs_js = self._needs_js_rendering(url)
            is_youtube = self._is_youtube_url(url)
            
            # ScrapingBee API parameters
            params = {
                'api_key': self.scrapingbee_api_key,
                'url': url,
                'render_js': 'True' if needs_js else 'False',
                'premium_proxy': 'True',
                'country_code': 'us'
            }
            
            # Add extra wait time for YouTube videos to load
            if is_youtube:
                params['wait'] = '3000'
                params['wait_for'] = '#player'
                logger.info(f"[ScrapingBee v24.2] YouTube detected - added wait parameters")
            
            logger.info(f"[ScrapingBee v24.2] Fetching with render_js={params['render_js']}, YouTube: {is_youtube}")
            
            response = requests.get(
                'https://app.scrapingbee.com/api/v1/',
                params=params,
                timeout=45
            )
            
            if response.status_code == 200:
                html = response.text
                logger.info(f"[ScrapingBee] ✓ Success: {len(html)} chars, JS render: {needs_js}, YouTube: {is_youtube}")
                return html, None
            else:
                error_msg = f"Status {response.status_code}: {response.text[:200]}"
                logger.warning(f"[ScrapingBee] ✗ {error_msg}")
                return None, error_msg
                
        except Exception as e:
            error_msg = f"Exception: {str(e)}"
            logger.error(f"[ScrapingBee] ✗ {error_msg}", exc_info=True)
            return None, error_msg
    
    def _fetch_direct(self, url: str, attempt_num: int) -> tuple:
        """Direct fetch with user agent"""
        
        try:
            logger.info(f"[Direct Fetch] Attempt {attempt_num}...")
            response = self.session.get(url, timeout=20, allow_redirects=True)
            
            if response.status_code == 200:
                html = response.text
                logger.info(f"[Direct] ✓ Got {len(html)} chars")
                return html, None
            else:
                error_msg = f"Status {response.status_code}"
                logger.warning(f"[Direct] ✗ {error_msg}")
                return None, error_msg
                
        except Exception as e:
            error_msg = f"Exception: {str(e)}"
            logger.error(f"[Direct] ✗ {error_msg}")
            return None, error_msg
    
    def _openai_extract(self, url: str) -> Optional[Dict[str, Any]]:
        """Use OpenAI to extract article data (fallback method)"""
        
        if not openai_client:
            return None
        
        try:
            logger.info("[OpenAI] Attempting intelligent extraction...")
            
            prompt = f"""Extract article information from this URL: {url}

Please provide:
1. Article title
2. Author name(s) - IMPORTANT: Only real people names, NOT outlet names like "MSNBC", "CNN", "BBC", etc.
3. Main content (first 500 words)
4. Source/publisher name

Return as JSON with keys: title, author, content, source"""
            
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                timeout=30
            )
            
            content = response.choices[0].message.content
            logger.info(f"[OpenAI] Got response: {len(content)} chars")
            
            # Try to parse JSON response
            try:
                data = json.loads(content)
                
                # Validate author is not an outlet name
                author = data.get('author', 'Unknown')
                if self._is_outlet_name_string(author):
                    logger.warning(f"[OpenAI] ⚠ Author '{author}' is outlet name - setting to Unknown")
                    author = 'Unknown'
                
                # Build result
                result = {
                    'title': data.get('title', 'Unknown Title'),
                    'author': author,
                    'author_page_url': None,
                    'author_page_urls': [],
                    'text': data.get('content', ''),
                    'content': data.get('content', ''),
                    'source': data.get('source', self._get_source_from_url(url)),
                    'domain': urlparse(url).netloc.replace('www.', ''),
                    'url': url,
                    'word_count': len(data.get('content', '').split()),
                    'sources_count': 0,
                    'quotes_count': 0,
                    'extraction_successful': True,
                    'extraction_method': 'openai_intelligent'
                }
                
                logger.info("[OpenAI] ✓ Successfully parsed response")
                return result
                
            except json.JSONDecodeError:
                logger.warning("[OpenAI] Response not valid JSON")
                return None
                
        except Exception as e:
            logger.error(f"[OpenAI] ✗ Exception: {e}", exc_info=True)
            return None
    
    def _is_outlet_name_string(self, text: str) -> bool:
        """
        NEW v24.2: Check if a string is an outlet name
        Used to validate author names aren't actually outlet names
        """
        if not text:
            return False
        
        text_clean = text.strip()
        text_upper = text_clean.upper()
        text_lower = text_clean.lower()
        
        # Direct match against OUTLET_NAMES (case-insensitive)
        for outlet in OUTLET_NAMES:
            if text_lower == outlet.lower():
                logger.info(f"[OutletCheck v24.2] ✓ '{text}' matches outlet '{outlet}'")
                return True
        
        # Check if text contains only outlet name
        if text_upper in {'MSNBC', 'CNN', 'BBC', 'NBC', 'CBS', 'ABC', 'PBS', 'NPR', 'AP', 'AFP', 'UPI', 'CNBC'}:
            logger.info(f"[OutletCheck v24.2] ✓ '{text}' is network acronym")
            return True
        
        return False
    
    def _parse_html(self, html: str, url: str) -> Dict[str, Any]:
        """Parse HTML and extract article data - ALWAYS returns valid Dict"""
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.replace('www.', '')
            
            logger.info(f"[Parse v24.2] Parsing {domain}...")
            
            # Extract components
            title = self._extract_title(soup)
            authors, author_page_urls = self._extract_authors(soup, html, url)
            text = self._extract_text(soup)
            
            # Build result
            result = {
                'title': title or 'Unknown Title',
                'author': authors if authors != 'Unknown' else 'Unknown',
                'author_page_url': author_page_urls[0] if author_page_urls else None,
                'author_page_urls': author_page_urls,
                'text': text,
                'content': text,
                'source': self._get_source_from_url(url),
                'domain': domain,
                'url': url,
                'word_count': len(text.split()) if text else 0,
                'sources_count': self._count_sources(text),
                'quotes_count': self._count_quotes(text),
                'extraction_successful': bool(title and text),
                'extraction_method': 'html_parse'
            }
            
            # Log result
            if result['extraction_successful']:
                logger.info(f"[Parse v24.2] ✓ SUCCESS: Title={len(title or '')} chars, "
                          f"Author={authors}, Text={len(text)} chars")
            else:
                logger.warning(f"[Parse v24.2] ⚠ PARTIAL: Missing title or text")
            
            return result
            
        except Exception as e:
            logger.error(f"[Parse v24.2] ✗ Exception: {e}", exc_info=True)
            return self._get_fallback_result(url, f"Parse exception: {e}")
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article title"""
        
        # Strategy 1: OpenGraph
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        
        # Strategy 2: Twitter Card
        twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
        if twitter_title and twitter_title.get('content'):
            return twitter_title['content'].strip()
        
        # Strategy 3: Standard title tag
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        
        # Strategy 4: h1 tag
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        return None
    
    def _extract_authors(self, soup: BeautifulSoup, html: str, url: str) -> tuple:
        """
        Extract author names and author page URLs
        Returns: (author_string, list_of_author_urls)
        """
        
        domain = urlparse(url).netloc.replace('www.', '')
        author_page_urls = []
        
        # Site-specific extraction
        if 'bbc.com' in domain or 'bbc.co.uk' in domain:
            authors = self._extract_bbc_authors(soup, html)
            if authors:
                for author in authors:
                    profile_url = self._construct_author_profile_url(author, url)
                    if profile_url:
                        author_page_urls.append(profile_url)
                
                author_string = ' and '.join(authors)
                logger.info(f"[Authors v24.2] BBC: {author_string}")
                return author_string, author_page_urls
        
        elif 'abcnews.go.com' in domain:
            authors = self._extract_abc_news_authors(soup, html)
            if authors:
                for author in authors:
                    profile_url = self._construct_author_profile_url(author, url)
                    if profile_url:
                        author_page_urls.append(profile_url)
                
                author_string = ' and '.join(authors)
                logger.info(f"[Authors v24.2] ABC: {author_string}")
                return author_string, author_page_urls
        
        # Universal extraction
        authors = self._extract_universal_authors(soup, html)
        if authors:
            for author in authors:
                profile_url = self._construct_author_profile_url(author, url)
                if profile_url:
                    author_page_urls.append(profile_url)
            
            author_string = ' and '.join(authors)
            logger.info(f"[Authors v24.2] Universal: {author_string}")
            return author_string, author_page_urls
        
        logger.warning("[Authors v24.2] ⚠ No authors found - returning Unknown")
        return 'Unknown', []
    
    def _extract_bbc_authors(self, soup: BeautifulSoup, html: str) -> List[str]:
        """
        BBC-specific author extraction with 8 strategies
        Returns list of author names
        """
        
        # ===== STRATEGY 7: BBC New Article Format - "Name, Title and Name, Location" =====
        logger.info("[BBC v24.2] Strategy 7: Checking new article format with comma-separated authors...")
        try:
            html_start = html[:10000]
            
            pattern = r'([A-Z][a-z]+\s+[A-Z][a-z]+),\s*([A-Za-z\s]+?)(?:\s+and\s+|\s*<|$)'
            
            matches = re.findall(pattern, html_start)
            if matches:
                names = []
                for match in matches:
                    name = match[0].strip()
                    role = match[1].strip()
                    
                    if self._is_valid_author_name(name):
                        logger.info(f"[BBC v24.2 Strategy 7] ✓ Found author: {name} ({role})")
                        names.append(name)
                
                if names:
                    logger.info(f"[BBC v24.2 Strategy 7] ✓✓ SUCCESS: Found {len(names)} author(s)")
                    return names
            
            for elem in soup.find_all(['div', 'span', 'p'], limit=100):
                text = elem.get_text().strip()
                
                if re.search(r'[A-Z][a-z]+\s+[A-Z][a-z]+,\s+[A-Za-z\s]+\s+and\s+[A-Z][a-z]+\s+[A-Z][a-z]+', text):
                    logger.info(f"[BBC v24.2 Strategy 7] Found potential match in element: {text[:100]}")
                    
                    pattern = r'([A-Z][a-z]+\s+[A-Z][a-z]+),'
                    found_names = re.findall(pattern, text)
                    
                    if found_names:
                        valid_names = []
                        for name in found_names:
                            if self._is_valid_author_name(name):
                                logger.info(f"[BBC v24.2 Strategy 7] ✓ Validated: {name}")
                                valid_names.append(name)
                        
                        if valid_names:
                            logger.info(f"[BBC v24.2 Strategy 7] ✓✓ SUCCESS via element text")
                            return valid_names
        
        except Exception as e:
            logger.error(f"[BBC v24.2] Strategy 7 error: {e}")
        
        logger.info("[BBC v24.2] Starting BBC News dedicated extraction")
        
        # STRATEGY 1: Look for data-component="byline-block"
        logger.info("[BBC v24.2] Strategy 1: Checking BBC byline blocks...")
        try:
            byline_blocks = soup.find_all(attrs={'data-component': re.compile(r'byline', re.I)})
            for block in byline_blocks:
                author_elements = block.find_all(['a', 'span', 'div'], string=re.compile(r'^[A-Z][a-z]+\s+[A-Z][a-z]+'))
                if author_elements:
                    names = []
                    for elem in author_elements:
                        name = elem.get_text().strip()
                        if self._is_valid_author_name(name):
                            logger.info(f"[BBC v24.2] ✓ Found in byline block: {name}")
                            names.append(name)
                    if names:
                        return names
        except Exception as e:
            logger.error(f"[BBC v24.2] Strategy 1 error: {e}")
        
        # STRATEGY 2: BBC-specific meta tags
        logger.info("[BBC v24.2] Strategy 2: Checking BBC meta tags...")
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
                    logger.info(f"[BBC v24.2] ✓ Found in meta {pattern}: {content}")
                    names = self._parse_multiple_authors_from_text(content)
                    if names:
                        return names
        except Exception as e:
            logger.error(f"[BBC v24.2] Strategy 2 error: {e}")
        
        # STRATEGY 3: role="author" attribute
        logger.info("[BBC v24.2] Strategy 3: Checking role='author'...")
        try:
            role_authors = soup.find_all(attrs={'role': 'author'})
            if role_authors:
                names = []
                for elem in role_authors:
                    text = elem.get_text().strip()
                    text = re.sub(r'^(By|Reporter:|Correspondent:)\s*', '', text, flags=re.I)
                    if self._is_valid_author_name(text):
                        logger.info(f"[BBC v24.2] ✓ Found via role='author': {text}")
                        names.append(text)
                if names:
                    return names
        except Exception as e:
            logger.error(f"[BBC v24.2] Strategy 3 error: {e}")
        
        # STRATEGY 4: BBC correspondent links
        logger.info("[BBC v24.2] Strategy 4: Checking BBC correspondent links...")
        try:
            correspondent_links = soup.find_all('a', href=re.compile(r'/news/correspondents/', re.I))
            if correspondent_links:
                names = []
                for link in correspondent_links:
                    name = link.get_text().strip()
                    if self._is_valid_author_name(name):
                        logger.info(f"[BBC v24.2] ✓ Found correspondent: {name}")
                        names.append(name)
                if names:
                    return names
        except Exception as e:
            logger.error(f"[BBC v24.2] Strategy 4 error: {e}")
        
        # STRATEGY 5: Raw HTML search for "By [Name]"
        logger.info("[BBC v24.2] Strategy 5: Searching raw HTML for byline patterns...")
        try:
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
                            logger.info(f"[BBC v24.2] ✓ Found in HTML: {match}")
                            names.append(match)
                    if names:
                        return names
        except Exception as e:
            logger.error(f"[BBC v24.2] Strategy 5 error: {e}")
        
        # STRATEGY 6: BBC-specific class patterns
        logger.info("[BBC v24.2] Strategy 6: Checking BBC-specific classes...")
        try:
            bbc_class_patterns = [
                'ssrcss-',
                'byline',
                'author',
                'contributor',
            ]
            
            for pattern in bbc_class_patterns:
                elements = soup.find_all(class_=re.compile(pattern, re.I))
                for elem in elements[:10]:
                    text = elem.get_text().strip()
                    if re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+$', text):
                        if self._is_valid_author_name(text):
                            logger.info(f"[BBC v24.2] ✓ Found via class '{pattern}': {text}")
                            return [text]
        except Exception as e:
            logger.error(f"[BBC v24.2] Strategy 6 error: {e}")
        
        # STRATEGY 8: NUCLEAR OPTION - Brute force search
        logger.info("[BBC v24.2] Strategy 8 (NUCLEAR): Brute force name extraction...")
        try:
            all_text = soup.get_text()
            
            logger.info(f"[BBC v24.2 Strategy 8] Total text length: {len(all_text)} chars")
            
            all_potential_names = re.findall(r'\b([A-Z][a-z]{2,15}\s+[A-Z][a-z]{2,15})\b', all_text)
            
            logger.info(f"[BBC v24.2 Strategy 8] Found {len(all_potential_names)} potential names total")
            
            valid_names = []
            seen = set()
            
            for name in all_potential_names:
                if name not in seen:
                    seen.add(name)
                    if self._is_valid_author_name(name):
                        valid_names.append(name)
                        logger.info(f"[BBC v24.2 Strategy 8] Valid name: {name}")
                        
                        if len(valid_names) >= 2:
                            name1_pos = all_text.find(valid_names[0])
                            name2_pos = all_text.find(valid_names[1])
                            distance = abs(name1_pos - name2_pos)
                            logger.info(f"[BBC v24.2 Strategy 8] Distance between names: {distance} chars")
                            
                            if distance < 500:
                                logger.info(f"[BBC v24.2 Strategy 8] ✓✓ NUCLEAR SUCCESS: {valid_names[:2]}")
                                return valid_names[:2]
            
            if valid_names:
                logger.info(f"[BBC v24.2 Strategy 8] ✓ Found {len(valid_names)} name(s)")
                return valid_names[:2]
                
        except Exception as e:
            logger.error(f"[BBC v24.2] Strategy 8 error: {e}")

        logger.warning("[BBC v24.2] ❌ All 8 BBC News strategies failed!")
        return []
    
    def _extract_abc_news_authors(self, soup: BeautifulSoup, html: str) -> List[str]:
        """
        Dedicated ABC News author extraction
        Tries 5 different ABC News specific patterns
        """
        
        logger.info("[ABC v24.2] Starting ABC News dedicated extraction")
        
        # STRATEGY 1: Look for "By" links with /author/ in href
        logger.info("[ABC v24.2] Strategy 1: Looking for author links...")
        try:
            author_links = soup.find_all('a', href=re.compile(r'/author/', re.I))
            if author_links:
                names = []
                for link in author_links:
                    name = link.get_text().strip()
                    if self._is_valid_author_name(name):
                        logger.info(f"[ABC v24.2] ✓ Found author link: {name}")
                        names.append(name)
                
                if names:
                    return names
        except Exception as e:
            logger.error(f"[ABC v24.2] Strategy 1 error: {e}")
        
        # STRATEGY 2: Look for meta tag "parsely-author"
        logger.info("[ABC v24.2] Strategy 2: Checking parsely-author meta...")
        try:
            parsely = soup.find('meta', attrs={'name': 'parsely-author'})
            if parsely and parsely.get('content'):
                content = parsely['content'].strip()
                logger.info(f"[ABC v24.2] ✓ Found parsely-author: {content}")
                names = self._parse_multiple_authors_from_text(content)
                if names:
                    return names
        except Exception as e:
            logger.error(f"[ABC v24.2] Strategy 2 error: {e}")
        
        # STRATEGY 3: ABC News byline classes
        logger.info("[ABC v24.2] Strategy 3: Checking ABC News byline classes...")
        try:
            byline_elements = soup.find_all(class_=re.compile(r'byline|author', re.I))
            for elem in byline_elements:
                text = elem.get_text().strip()
                text = re.sub(r'^By\s+', '', text, flags=re.I)
                
                if re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+', text):
                    names = self._parse_multiple_authors_from_text(text)
                    if names:
                        logger.info(f"[ABC v24.2] ✓ Found in byline: {names}")
                        return names
        except Exception as e:
            logger.error(f"[ABC v24.2] Strategy 3 error: {e}")
        
        # STRATEGY 4: Search raw HTML
        logger.info("[ABC v24.2] Strategy 4: Searching raw HTML...")
        try:
            html_start = html[:5000]
            pattern = r'By\s+([A-Z][a-z]+\s+[A-Z][a-z]+)(?:\s+and\s+([A-Z][a-z]+\s+[A-Z][a-z]+))?'
            matches = re.findall(pattern, html_start)
            
            if matches:
                names = []
                for match in matches:
                    for name in match:
                        if name and self._is_valid_author_name(name):
                            logger.info(f"[ABC v24.2] ✓ Found in HTML: {name}")
                            names.append(name)
                
                if names:
                    return names
        except Exception as e:
            logger.error(f"[ABC v24.2] Strategy 4 error: {e}")
        
        # STRATEGY 5: JSON-LD structured data
        logger.info("[ABC v24.2] Strategy 5: Checking JSON-LD...")
        try:
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    
                    if 'author' in data:
                        author_data = data['author']
                        
                        if isinstance(author_data, list):
                            names = []
                            for author in author_data:
                                if isinstance(author, dict) and 'name' in author:
                                    name = author['name']
                                    if self._is_valid_author_name(name):
                                        logger.info(f"[ABC v24.2] ✓ Found in JSON-LD: {name}")
                                        names.append(name)
                            if names:
                                return names
                        
                        elif isinstance(author_data, dict) and 'name' in author_data:
                            name = author_data['name']
                            if self._is_valid_author_name(name):
                                logger.info(f"[ABC v24.2] ✓ Found in JSON-LD: {name}")
                                return [name]
                        
                        elif isinstance(author_data, str):
                            names = self._parse_multiple_authors_from_text(author_data)
                            if names:
                                logger.info(f"[ABC v24.2] ✓ Found in JSON-LD: {names}")
                                return names
                
                except (json.JSONDecodeError, KeyError):
                    continue
        except Exception as e:
            logger.error(f"[ABC v24.2] Strategy 5 error: {e}")
        
        logger.warning("[ABC v24.2] ❌ All ABC News strategies failed!")
        return []
    
    def _extract_universal_authors(self, soup: BeautifulSoup, html: str) -> List[str]:
        """
        UNIVERSAL author extraction - works for most sites
        """
        
        logger.info("[Universal v24.2] Starting universal author extraction")
        
        # STRATEGY 1: Author meta tags
        logger.info("[Universal v24.2] Strategy 1: Checking meta tags...")
        try:
            meta_patterns = [
                {'name': 'author'},
                {'property': 'article:author'},
                {'name': 'article:author'},
                {'name': 'parsely-author'},
                {'name': 'sailthru.author'},
                {'name': 'byl'},
            ]
            
            for pattern in meta_patterns:
                meta = soup.find('meta', attrs=pattern)
                if meta and meta.get('content'):
                    content = meta['content'].strip()
                    logger.info(f"[Universal v24.2] ✓ Found meta {pattern}: {content}")
                    names = self._parse_multiple_authors_from_text(content)
                    if names:
                        return names
        except Exception as e:
            logger.error(f"[Universal v24.2] Strategy 1 error: {e}")
        
        # STRATEGY 2: Author-related classes
        logger.info("[Universal v24.2] Strategy 2: Checking author classes...")
        try:
            author_classes = ['author', 'byline', 'by-author', 'article-author', 'contributor']
            
            for class_name in author_classes:
                elements = soup.find_all(class_=re.compile(class_name, re.I))
                for elem in elements[:5]:
                    text = elem.get_text().strip()
                    text = re.sub(r'^(By|Written by|Story by)\s+', '', text, flags=re.I)
                    
                    if re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+', text):
                        names = self._parse_multiple_authors_from_text(text)
                        if names:
                            logger.info(f"[Universal v24.2] ✓ Found in class '{class_name}': {names}")
                            return names
        except Exception as e:
            logger.error(f"[Universal v24.2] Strategy 2 error: {e}")
        
        # STRATEGY 3: rel="author" links
        logger.info("[Universal v24.2] Strategy 3: Checking rel='author' links...")
        try:
            author_links = soup.find_all('a', rel='author')
            if author_links:
                names = []
                for link in author_links:
                    name = link.get_text().strip()
                    if self._is_valid_author_name(name):
                        logger.info(f"[Universal v24.2] ✓ Found rel='author': {name}")
                        names.append(name)
                if names:
                    return names
        except Exception as e:
            logger.error(f"[Universal v24.2] Strategy 3 error: {e}")
        
        # STRATEGY 4: JSON-LD structured data
        logger.info("[Universal v24.2] Strategy 4: Checking JSON-LD...")
        try:
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and 'author' in item:
                                names = self._extract_authors_from_jsonld(item)
                                if names:
                                    return names
                    elif isinstance(data, dict) and 'author' in data:
                        names = self._extract_authors_from_jsonld(data)
                        if names:
                            return names
                
                except (json.JSONDecodeError, KeyError):
                    continue
        except Exception as e:
            logger.error(f"[Universal v24.2] Strategy 4 error: {e}")
        
        # STRATEGY 5: Search raw HTML for byline patterns
        logger.info("[Universal v24.2] Strategy 5: Searching raw HTML for bylines...")
        try:
            html_start = html[:5000]
            byline_patterns = [
                r'By\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
                r'Written by\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
                r'Story by\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            ]
            
            for pattern in byline_patterns:
                matches = re.findall(pattern, html_start)
                if matches:
                    names = []
                    for match in matches:
                        if self._is_valid_author_name(match):
                            logger.info(f"[Universal v24.2] ✓ Found in HTML: {match}")
                            names.append(match)
                    if names:
                        return names
        except Exception as e:
            logger.error(f"[Universal v24.2] Strategy 5 error: {e}")
        
        logger.warning("[Universal v24.2] ⚠ No authors found via universal extraction")
        return []
    
    def _extract_authors_from_jsonld(self, data: dict) -> List[str]:
        """Extract authors from JSON-LD data"""
        
        author_data = data.get('author')
        names = []
        
        if isinstance(author_data, list):
            for author in author_data:
                if isinstance(author, dict) and 'name' in author:
                    name = author['name']
                    if self._is_valid_author_name(name):
                        names.append(name)
                elif isinstance(author, str):
                    parsed = self._parse_multiple_authors_from_text(author)
                    names.extend(parsed)
        
        elif isinstance(author_data, dict) and 'name' in author_data:
            name = author_data['name']
            if self._is_valid_author_name(name):
                names.append(name)
        
        elif isinstance(author_data, str):
            names = self._parse_multiple_authors_from_text(author_data)
        
        if names:
            logger.info(f"[JSON-LD v24.2] ✓ Extracted: {names}")
        
        return names
    
    def _parse_multiple_authors_from_text(self, text: str) -> List[str]:
        """Parse multiple authors from a text string"""
        
        if not text:
            return []
        
        # Clean the text
        text = self._clean_author_name(text)
        
        # CRITICAL v24.2: Check if entire text is an outlet name BEFORE parsing
        if self._is_outlet_name_string(text):
            logger.warning(f"[AuthorParse v24.2] ❌ '{text}' is outlet name - rejecting")
            return []
        
        # Try to split on common delimiters
        separators = [' and ', ', and ', ' & ', ';', ',']
        
        for sep in separators:
            if sep in text:
                parts = text.split(sep)
                names = []
                for part in parts:
                    part = part.strip()
                    if self._is_valid_author_name(part):
                        names.append(part)
                
                if names:
                    return names
        
        # No separator found - check if it's a single valid name
        if self._is_valid_author_name(text):
            return [text]
        
        return []
    
    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract main article text"""
        
        # Strategy 1: Look for article tag
        article = soup.find('article')
        if article:
            paragraphs = article.find_all('p')
            if paragraphs:
                text = '\n\n'.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 50])
                if len(text) > 200:
                    return text
        
        # Strategy 2: Look for main content div
        main_content = soup.find(['main', 'div'], class_=re.compile(r'content|article|story|body', re.I))
        if main_content:
            paragraphs = main_content.find_all('p')
            if paragraphs:
                text = '\n\n'.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 50])
                if len(text) > 200:
                    return text
        
        # Strategy 3: Get all paragraphs
        paragraphs = soup.find_all('p')
        if paragraphs:
            text = '\n\n'.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 50])
            if len(text) > 200:
                return text
        
        return ''
    
    def _construct_author_profile_url(self, author_name: str, article_url: str) -> Optional[str]:
        """Construct probable author profile URL based on site patterns"""
        
        if not author_name or author_name == 'Unknown':
            return None
        
        parsed = urlparse(article_url)
        domain = parsed.netloc.replace('www.', '')
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        # Create slug from author name
        slug = author_name.lower().replace(' ', '-')
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s]+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        slug = slug.strip('-')
        
        # Site-specific URL patterns
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
        elif 'msnbc.com' in domain or 'ms.now' in domain:
            return f"{base_url}/author/{slug}"
        else:
            return f"{base_url}/author/{slug}"
    
    def _clean_author_name(self, text: str) -> str:
        """Clean up author name"""
        
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
        """
        Check if a name is valid - ENHANCED v24.2
        NOW REJECTS OUTLET NAMES LIKE "MSNBC", "CNN", etc.
        """
        
        if not name or name == 'Unknown':
            return False
        
        # Length check
        if len(name) < 3 or len(name) > 100:
            return False
        
        words = name.split()
        
        # Must have at least 2 words (first and last name)
        if len(words) < 2:
            # EXCEPTION: Single word that's an outlet name should be rejected with a clear message
            if self._is_outlet_name_string(name):
                logger.warning(f"[Validation v24.2] ❌ '{name}' is a single-word outlet name")
            return False
        
        # First character should be uppercase
        if not name[0].isupper():
            return False
        
        # Check exclusion list (politicians, celebrities, etc.)
        if name in NON_JOURNALIST_NAMES:
            logger.warning(f"[Validation v24.2] ❌ '{name}' in exclusion list")
            return False
        
        # NEW v24.2: Check if it's an outlet name
        if self._is_outlet_name_string(name):
            logger.warning(f"[Validation v24.2] ❌ '{name}' is an outlet name")
            return False
        
        # Check each word against common non-name words
        for word in words:
            if word in COMMON_NON_NAME_WORDS:
                logger.warning(f"[Validation v24.2] ❌ '{name}' contains non-name word '{word}'")
                return False
        
        # Generic terms check
        generic_terms = ['staff', 'editor', 'reporter', 'correspondent', 'bureau', 'desk', 'team', 'wire']
        if any(term in name.lower() for term in generic_terms):
            logger.warning(f"[Validation v24.2] ❌ '{name}' contains generic term")
            return False
        
        # Too many words (probably a sentence)
        if len(words) > 5:
            logger.warning(f"[Validation v24.2] ❌ '{name}' has too many words ({len(words)})")
            return False
        
        # Validate first 3 words contain only letters, hyphens, apostrophes
        for word in words[:3]:
            if not re.match(r'^[A-Za-zÀ-ÿ\'-]+$', word):
                logger.warning(f"[Validation v24.2] ❌ '{name}' contains invalid characters in '{word}'")
                return False
        
        logger.info(f"[Validation v24.2] ✓ '{name}' is valid")
        return True
    
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
            'msnbc.com': 'MSNBC',
            'ms.now': 'MSNBC',
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
            'bloomberg.com': 'Bloomberg',
            'axios.com': 'Axios',
            'youtube.com': 'YouTube',
            'youtu.be': 'YouTube',
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


logger.info("[ArticleExtractor v24.2] ✓ OUTLET NAME REJECTION FIX + MS.NOW + SCRAPINGBEE!")

# I did no harm and this file is not truncated.
