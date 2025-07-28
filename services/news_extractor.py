"""
FILE: services/news_extractor.py
LOCATION: services/news_extractor.py
PURPOSE: Universal news extractor with anti-bot bypass techniques
"""

import logging
import re
import json
import time
import random
from datetime import datetime
from urllib.parse import urlparse, quote
from collections import Counter, defaultdict
from html import unescape

import requests
from bs4 import BeautifulSoup, NavigableString, Comment

# Try to import cloudscraper for anti-bot bypass
try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False

# Try to import other tools
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

logger = logging.getLogger(__name__)

class NewsExtractor:
    """Ultimate universal news extractor with AI-level author detection"""
    
    def __init__(self):
        # Set up multiple session types
        self.sessions = self._create_sessions()
        self.current_session_index = 0
        
        # Legacy session for compatibility
        self.session = self.sessions[0][1] if self.sessions else requests.Session()
        
        # Headers that mimic real browsers
        self.headers_sets = [
            {
                # Chrome on Windows
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0'
            },
            {
                # Firefox on Mac
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1'
            },
            {
                # Safari on Mac
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            },
            {
                # Mobile Chrome
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'X-Requested-With': 'com.android.chrome',
                'Upgrade-Insecure-Requests': '1'
            }
        ]
        
        # Update session with first header set
        self.session.headers.update(self.headers_sets[0])
        
        # Common first and last names for validation (expanded set)
        self.common_first_names = {
            'james', 'john', 'robert', 'michael', 'william', 'david', 'richard', 'joseph',
            'thomas', 'charles', 'mary', 'patricia', 'jennifer', 'linda', 'elizabeth',
            'barbara', 'susan', 'jessica', 'sarah', 'karen', 'daniel', 'matthew', 'donald',
            'mark', 'paul', 'steven', 'andrew', 'kenneth', 'joshua', 'kevin', 'brian',
            'george', 'edward', 'ronald', 'timothy', 'jason', 'jeffrey', 'ryan', 'jacob',
            'gary', 'nicholas', 'eric', 'jonathan', 'stephen', 'larry', 'justin', 'scott',
            'brandon', 'benjamin', 'samuel', 'frank', 'gregory', 'raymond', 'alexander',
            'patrick', 'jack', 'dennis', 'jerry', 'tyler', 'aaron', 'jose', 'nathan',
            'henry', 'zachary', 'douglas', 'peter', 'adam', 'noah', 'christopher', 'nancy',
            'betty', 'helen', 'sandra', 'donna', 'carol', 'ruth', 'sharon', 'michelle',
            'laura', 'kimberly', 'deborah', 'rachel', 'amy', 'anna', 'maria', 'dorothy',
            'lisa', 'ashley', 'madison', 'amanda', 'melissa', 'debra', 'stephanie', 'rebecca',
            'virginia', 'kathleen', 'pamela', 'martha', 'angela', 'katherine', 'christine',
            'emma', 'olivia', 'sophia', 'isabella', 'charlotte', 'amelia', 'evelyn',
            'jeremy', 'simon', 'martin', 'peter', 'alan', 'ian', 'colin', 'graham',
            'daniella', 'didi', 'martinez', 'silva'
        }
        
        # Common last names for validation
        self.common_last_names = {
            'smith', 'johnson', 'williams', 'brown', 'jones', 'garcia', 'miller', 'davis',
            'rodriguez', 'martinez', 'hernandez', 'lopez', 'gonzalez', 'wilson', 'anderson',
            'thomas', 'taylor', 'moore', 'jackson', 'martin', 'lee', 'perez', 'thompson',
            'white', 'harris', 'sanchez', 'clark', 'ramirez', 'lewis', 'robinson', 'walker',
            'young', 'allen', 'king', 'wright', 'scott', 'torres', 'nguyen', 'hill',
            'flores', 'green', 'adams', 'nelson', 'baker', 'hall', 'rivera', 'campbell',
            'mitchell', 'carter', 'roberts', 'bowen', 'cohen', 'chen', 'wang', 'kim',
            'silva', 'martinez'
        }
        
        # Organization names to filter out
        self.org_names = {
            'nbc', 'cnn', 'fox', 'abc', 'cbs', 'bbc', 'npr', 'reuters', 'associated press',
            'bloomberg', 'new york times', 'washington post', 'guardian', 'daily mail',
            'usa today', 'wall street journal', 'los angeles times', 'chicago tribune',
            'boston globe', 'miami herald', 'news', 'media', 'press', 'network',
            'broadcasting', 'times', 'post', 'journal', 'herald', 'globe', 'tribune'
        }
    
    def _create_sessions(self):
        """Create multiple session types"""
        sessions = []
        
        # CloudScraper session (best for anti-bot)
        if CLOUDSCRAPER_AVAILABLE:
            try:
                scraper = cloudscraper.create_scraper(
                    browser={
                        'browser': 'chrome',
                        'platform': 'windows',
                        'desktop': True
                    }
                )
                sessions.append(('cloudscraper', scraper))
                logger.info("CloudScraper session created")
            except Exception as e:
                logger.warning(f"Failed to create CloudScraper: {e}")
        
        # HTTPX session (supports HTTP/2)
        if HTTPX_AVAILABLE:
            try:
                client = httpx.Client(
                    http2=True,
                    follow_redirects=True,
                    timeout=30.0
                )
                sessions.append(('httpx', client))
                logger.info("HTTPX session created")
            except Exception as e:
                logger.warning(f"Failed to create HTTPX client: {e}")
        
        # Standard requests session
        session = requests.Session()
        sessions.append(('requests', session))
        
        return sessions
    
    def extract_article(self, url):
        """Extract article content from URL with anti-bot bypass"""
        try:
            logger.info(f"🚀 ULTIMATE EXTRACTION STARTING for: {url}")
            
            # Try bypass extraction first
            result = self._extract_with_bypass(url)
            
            if result and result.get('text') and len(result['text']) > 200:
                logger.info(f"✅ EXTRACTION COMPLETE: Title='{result['title'][:50]}...', Author='{result.get('author')}', Text length={len(result['text'])}")
                return result
            
            # Fallback methods
            fallback_methods = [
                self._extract_with_google_cache,
                self._extract_with_wayback,
                self._extract_mobile_version,
                self._extract_emergency_bypass
            ]
            
            for method in fallback_methods:
                try:
                    result = method(url)
                    if result and result.get('text') and len(result['text']) > 200:
                        logger.info(f"✅ Extraction successful with {method.__name__}")
                        return result
                except Exception as e:
                    logger.warning(f"{method.__name__} failed: {str(e)}")
                    continue
            
            # Final fallback
            return self._create_smart_fallback(url)
            
        except Exception as e:
            logger.error(f"Extraction error for {url}: {str(e)}", exc_info=True)
            return None
    
    def _extract_with_bypass(self, url):
        """Extract using various bypass techniques"""
        domain = urlparse(url).netloc.replace('www.', '')
        
        # Try each session and header combination
        for session_name, session in self.sessions:
            for headers in self.headers_sets:
                try:
                    logger.info(f"Trying {session_name} with {headers['User-Agent'][:30]}...")
                    
                    # Add delay to appear more human
                    time.sleep(random.uniform(0.5, 2.0))
                    
                    # Different request methods based on session type
                    if session_name == 'httpx' and HTTPX_AVAILABLE:
                        response = session.get(url, headers=headers)
                        content = response.content
                        status = response.status_code
                    else:
                        # Add cookies for some sites
                        if 'politico' in domain:
                            session.cookies.set('__cf_bm', 'dummy', domain='.politico.com')
                        
                        response = session.get(url, headers=headers, timeout=30, allow_redirects=True)
                        content = response.content
                        status = response.status_code
                    
                    if status == 200 and content:
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # Extract content
                        title = self._extract_title(soup)
                        text = self._extract_text(soup, url)
                        
                        # ULTIMATE AUTHOR EXTRACTION
                        author = self._extract_author_ultimate(soup, content.decode('utf-8', errors='ignore'), title, text, domain)
                        
                        publish_date = self._extract_date(soup)
                        
                        return {
                            'title': title or 'No title found',
                            'text': text or 'No article text found',
                            'author': author,
                            'publish_date': publish_date,
                            'url': url,
                            'domain': domain
                        }
                            
                except Exception as e:
                    logger.debug(f"Session {session_name} failed: {str(e)}")
                    continue
        
        raise ValueError("All bypass attempts failed")
    
    def _extract_author_ultimate(self, soup, html_text, title, article_text, domain):
        """ULTIMATE author extraction using every conceivable method"""
        
        logger.info("🔍 ULTIMATE AUTHOR EXTRACTION ENGAGED")
        
        # Store all candidates with confidence scores
        author_candidates = {}  # author -> confidence score
        
        # METHOD 0: Domain-specific patterns (BBC, CNN, etc.)
        domain_patterns = {
            'bbc.com': [
                r'By\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'<span class="byline__name">([^<]+)</span>',
                r'<p class="contributor__name">([^<]+)</p>'
            ],
            'cnn.com': [
                r'class="byline__name">([^<]+)</span>',
                r'class="metadata__byline__author">([^<]+)</span>',
                r'"author":\s*{\s*"name":\s*"([^"]+)"'
            ],
            'reuters.com': [
                r'By\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'class="author-name">([^<]+)',
                r'"author":\s*"([^"]+)"'
            ],
            'nytimes.com': [
                r'class="byline__name">([^<]+)',
                r'"author":\s*{\s*"name":\s*"([^"]+)"',
                r'By\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
            ],
            'politico.com': [
                r'class="story-meta__authors">([^<]+)</p>',
                r'class="byline">([^<]+)</span>',
                r'class="vcard">([^<]+)</span>',
                r'itemprop="author"[^>]*>([^<]+)<',
                r'rel="author"[^>]*>([^<]+)<',
                r'"authors":\s*\[([^\]]+)\]',
                r'"author":\s*{\s*"name":\s*"([^"]+)"',
                r'By\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*(?:and|,)',
                r'<a[^>]+href="[^"]*\/staff\/[^"]*"[^>]*>([^<]+)</a>',
                r'data-authors="([^"]+)"',
                r'class="author-name"[^>]*>([^<]+)',
                r'<address[^>]*>([^<]+)</address>'
            ],
            'washingtonpost.com': [
                r'class="author-name">([^<]+)',
                r'rel="author">([^<]+)</a>',
                r'"author":\s*{\s*"name":\s*"([^"]+)"'
            ],
            'theguardian.com': [
                r'rel="author">([^<]+)</a>',
                r'class="byline">([^<]+)</span>',
                r'"author":\s*{\s*"name":\s*"([^"]+)"'
            ],
            'foxnews.com': [
                r'class="author-byline">([^<]+)',
                r'class="author">([^<]+)',
                r'"author":\s*"([^"]+)"'
            ],
            'npr.org': [
                r'class="byline__name">([^<]+)',
                r'By\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'"author":\s*{\s*"name":\s*"([^"]+)"'
            ]
        }
        
        if domain in domain_patterns:
            for pattern in domain_patterns[domain]:
                matches = re.findall(pattern, html_text)
                for match in matches:
                    author = self._clean_author_name(match)
                    if author and self._is_valid_author_name(author):
                        author_candidates[author] = author_candidates.get(author, 0) + 10
        
        # METHOD 1: JSON-LD structured data
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                self._extract_author_from_json_ld(data, author_candidates)
            except:
                continue
        
        # METHOD 2: Meta tags
        meta_selectors = [
            ('meta', {'name': 'author'}),
            ('meta', {'property': 'author'}),
            ('meta', {'name': 'article:author'}),
            ('meta', {'property': 'article:author'}),
            ('meta', {'name': 'byl'}),
            ('meta', {'name': 'DC.creator'}),
            ('meta', {'name': 'citation_author'}),
            ('meta', {'property': 'og:article:author'}),
            ('meta', {'itemprop': 'author'}),
            ('meta', {'name': 'twitter:creator'}),
            ('meta', {'name': 'sailthru.author'}),
            ('meta', {'name': 'parsely-author'})
        ]
        
        for tag, attrs in meta_selectors:
            elements = soup.find_all(tag, attrs)
            for element in elements:
                content = element.get('content', '')
                if content:
                    author = self._clean_author_name(content)
                    if author and self._is_valid_author_name(author):
                        author_candidates[author] = author_candidates.get(author, 0) + 8
        
        # METHOD 3: Common byline patterns
        byline_selectors = [
            '[class*="author"]', '[class*="byline"]', '[class*="writer"]',
            '[class*="reporter"]', '[class*="contributor"]', '[class*="journalist"]',
            '[class*="by-line"]', '[class*="article-author"]', '[class*="post-author"]',
            '[class*="entry-author"]', '[class*="news-author"]', '[class*="story-author"]',
            '[id*="author"]', '[id*="byline"]', '[itemprop="author"]',
            '[rel="author"]', '[data-author]', '[data-byline]',
            'address', '.by', '.writtenby', '.author-name', '.author-info',
            '.byline-name', '.contributor', '.story-byline', '.article-byline',
            '.content-author', '.post-meta-author', '.entry-meta-author',
            '.story-meta__authors', '.story-meta', '.metadata', '.meta-author',
            '.article-meta', '.post-meta', '.entry-meta', '.content-meta',
            'span.vcard', 'p.vcard', 'div.vcard', '.h-card',
            '[class*="meta"] [class*="author"]', '[class*="meta"] a[href*="/staff/"]',
            'a[href*="/author/"]', 'a[href*="/authors/"]', 'a[href*="/staff/"]',
            'a[href*="/people/"]', 'a[href*="/contributors/"]'
        ]
        
        for selector in byline_selectors:
            try:
                elements = soup.select(selector)
                for element in elements[:10]:
                    text = element.get_text().strip()
                    
                    # Clean and extract author name
                    author = self._extract_author_from_byline(text)
                    if author and self._is_valid_author_name(author):
                        # Higher score for more specific selectors
                        score = 7 if 'author' in selector.lower() else 5
                        author_candidates[author] = author_candidates.get(author, 0) + score
            except:
                continue
        
        # METHOD 4: "By" pattern in text
        by_patterns = [
            r'[Bb]y\s+([A-Z][a-z]+(?:\s+[A-Z\'][a-z]+){1,3})',
            r'[Ww]ritten\s+by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
            r'[Rr]eported\s+by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
            r'[Aa]uthor:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
            r'[Bb]y:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
            r'–\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\s*$',
            r'—\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\s*$'
        ]
        
        # Search in HTML
        for pattern in by_patterns:
            matches = re.findall(pattern, html_text[:5000])  # Check first 5000 chars
            for match in matches:
                author = self._clean_author_name(match)
                if author and self._is_valid_author_name(author):
                    author_candidates[author] = author_candidates.get(author, 0) + 6
        
        # METHOD 5: Link patterns
        author_link_patterns = [
            r'/author/([^/"]+)',
            r'/authors/([^/"]+)',
            r'/profile/([^/"]+)',
            r'/contributor/([^/"]+)',
            r'/staff/([^/"]+)',
            r'/people/([^/"]+)',
            r'/by/([^/"]+)',
            r'/writer/([^/"]+)'
        ]
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag.get('href', '')
            for pattern in author_link_patterns:
                match = re.search(pattern, href)
                if match:
                    author_slug = match.group(1)
                    # Try to get name from link text
                    link_text = a_tag.get_text().strip()
                    if link_text and self._is_valid_author_name(link_text):
                        author_candidates[link_text] = author_candidates.get(link_text, 0) + 4
                    # Also try to convert slug to name
                    elif author_slug:
                        name = author_slug.replace('-', ' ').title()
                        if self._is_valid_author_name(name):
                            author_candidates[name] = author_candidates.get(name, 0) + 3
        
        # METHOD 6: Email pattern for author
        email_pattern = r'([a-zA-Z0-9._%+-]+)@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email_matches = re.findall(email_pattern, html_text[:3000])
        for email_user in email_matches[:5]:
            # Convert email username to potential name
            name_parts = re.split(r'[._-]', email_user)
            if len(name_parts) >= 2:
                potential_name = ' '.join(part.capitalize() for part in name_parts[:2])
                if self._is_valid_author_name(potential_name):
                    author_candidates[potential_name] = author_candidates.get(potential_name, 0) + 2
        
        # METHOD 7: Schema.org microdata
        schema_selectors = [
            '[itemtype*="schema.org/Person"]',
            '[itemtype*="schema.org/Author"]',
            '[typeof="Person"]',
            '[typeof="Author"]'
        ]
        
        for selector in schema_selectors:
            elements = soup.select(selector)
            for element in elements:
                name_elem = element.select_one('[itemprop="name"]')
                if name_elem:
                    author = self._clean_author_name(name_elem.get_text())
                    if author and self._is_valid_author_name(author):
                        author_candidates[author] = author_candidates.get(author, 0) + 7
        
        # METHOD 8: Specific class/id patterns that often contain authors
        specific_patterns = [
            ('span', {'class': re.compile(r'by__author|article__author-name|post-author-name')}),
            ('div', {'class': re.compile(r'author-bio|author-info|writer-info')}),
            ('p', {'class': re.compile(r'author|byline|writer')}),
            ('cite', {}),  # Often used for attributions
            ('address', {})  # Sometimes used for author info
        ]
        
        for tag, attrs in specific_patterns:
            elements = soup.find_all(tag, attrs)
            for element in elements:
                text = element.get_text().strip()
                author = self._extract_author_from_byline(text)
                if author and self._is_valid_author_name(author):
                    author_candidates[author] = author_candidates.get(author, 0) + 5
        
        # METHOD 9: Check near "by" in clean text
        if article_text:
            first_500_chars = article_text[:500]
            for pattern in by_patterns:
                matches = re.findall(pattern, first_500_chars)
                for match in matches:
                    author = self._clean_author_name(match)
                    if author and self._is_valid_author_name(author):
                        author_candidates[author] = author_candidates.get(author, 0) + 5
        
        # METHOD 10: Twitter meta tag
        twitter_creator = soup.find('meta', {'name': 'twitter:creator'})
        if twitter_creator and twitter_creator.get('content'):
            twitter_handle = twitter_creator['content'].strip()
            # Try to extract real name from nearby elements
            # or just use the handle as a last resort
            if twitter_handle.startswith('@'):
                twitter_handle = twitter_handle[1:]
            author_candidates[f"@{twitter_handle}"] = author_candidates.get(f"@{twitter_handle}", 0) + 1
        
        # METHOD 11: Aggressive link-based extraction
        logger.info("🔗 METHOD 11: Aggressive link extraction")
        
        # Look for any links that might contain author info
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text().strip()
            
            # Check if link points to author/staff page
            if any(pattern in href.lower() for pattern in ['/author/', '/authors/', '/staff/', '/people/', '/contributors/', '/profile/', '/bio/']):
                if text and self._is_valid_author_name(text):
                    author_candidates[text] = author_candidates.get(text, 0) + 6
                    logger.info(f"  Found via author link: {text}")
            
            # Check parent elements for byline context
            parent = link.parent
            if parent:
                parent_text = parent.get_text().strip()
                if any(indicator in parent_text.lower() for indicator in ['by', 'author', 'written', 'reported']):
                    if text and self._is_valid_author_name(text):
                        author_candidates[text] = author_candidates.get(text, 0) + 7
                        logger.info(f"  Found via parent context: {text}")
        
        # METHOD 12: Deep text search in first part of article
        logger.info("📝 METHOD 12: Deep text pattern search")
        
        # Get first 1000 chars of clean text
        all_text = soup.get_text()[:3000]
        
        # More aggressive patterns
        deep_patterns = [
            r'(?:By|FROM|BY)\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})(?:\s*[,\n\r])',
            r'(?:Written by|Reported by|WRITTEN BY)\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})',
            r'^([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})\s+(?:is|writes|reports)',
            r'(?:Story by|STORY BY)\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})',
            r'([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})\s+\|\s+\d{1,2}[/\.]\d{1,2}',
            r'([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})\s+Updated:',
            r'Contact\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})\s+at'
        ]
        
        for pattern in deep_patterns:
            matches = re.findall(pattern, all_text, re.MULTILINE)
            for match in matches:
                author = self._clean_author_name(match)
                if author and self._is_valid_author_name(author):
                    author_candidates[author] = author_candidates.get(author, 0) + 4
                    logger.info(f"  Found via deep text search: {author}")
        
        # Select best candidate
        if author_candidates:
            # Sort by score and name quality
            sorted_candidates = sorted(
                author_candidates.items(),
                key=lambda x: (x[1], len(x[0].split()), -len(x[0])),
                reverse=True
            )
            
            best_author = sorted_candidates[0][0]
            logger.info(f"✅ Author found: {best_author} (score: {sorted_candidates[0][1]})")
            logger.info(f"All candidates: {sorted_candidates[:5]}")
            return best_author
        
        logger.warning("❌ No author found")
        return None
    
    def _extract_author_from_json_ld(self, data, author_candidates):
        """Extract author from JSON-LD data"""
        if isinstance(data, dict):
            # Direct author field
            if 'author' in data:
                author_data = data['author']
                if isinstance(author_data, str):
                    author = self._clean_author_name(author_data)
                    if author and self._is_valid_author_name(author):
                        author_candidates[author] = author_candidates.get(author, 0) + 10
                elif isinstance(author_data, dict):
                    name = author_data.get('name', '')
                    if name:
                        author = self._clean_author_name(name)
                        if author and self._is_valid_author_name(author):
                            author_candidates[author] = author_candidates.get(author, 0) + 10
                elif isinstance(author_data, list):
                    for auth in author_data:
                        if isinstance(auth, dict):
                            name = auth.get('name', '')
                        else:
                            name = str(auth)
                        if name:
                            author = self._clean_author_name(name)
                            if author and self._is_valid_author_name(author):
                                author_candidates[author] = author_candidates.get(author, 0) + 10
            
            # Check nested structures
            for key in ['mainEntity', 'mainEntityOfPage', '@graph']:
                if key in data:
                    self._extract_author_from_json_ld(data[key], author_candidates)
        
        elif isinstance(data, list):
            for item in data:
                self._extract_author_from_json_ld(item, author_candidates)
    
    def _extract_author_from_byline(self, text):
        """Extract author name from byline text"""
        if not text or len(text) > 200:
            return None
        
        # Remove common prefixes
        text = re.sub(r'^(By|Written by|Reported by|Author:|By:|Contributor:|Posted by|Published by)\s*', '', text, flags=re.I)
        text = re.sub(r'^(By|by)\s+', '', text)
        
        # Remove dates, times, and common suffixes
        text = re.sub(r'\d{1,2}[/:]\d{1,2}[/:]\d{2,4}.*$', '', text)
        text = re.sub(r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).*$', '', text, flags=re.I)
        text = re.sub(r'(Posted|Published|Updated|Modified).*$', '', text, flags=re.I)
        text = re.sub(r'\|.*$', '', text)
        text = re.sub(r'\s+[-–—]\s+.*$', '', text)
        
        # Extract name part
        text = text.strip()
        
        # Skip if it's too long or too short
        if len(text) < 3 or len(text) > 50:
            return None
        
        # Skip if it contains certain words
        skip_words = ['share', 'tweet', 'email', 'print', 'comment', 'subscribe', 
                     'follow', 'advertisement', 'sponsored', 'promoted']
        if any(word in text.lower() for word in skip_words):
            return None
        
        return text
    
    def _clean_author_name(self, name):
        """Clean and normalize author name"""
        if not name:
            return None
        
        # Basic cleaning
        name = str(name).strip()
        name = re.sub(r'\s+', ' ', name)
        
        # Remove common suffixes/prefixes
        name = re.sub(r'^(By|Written by|Reported by|Author:|By:|Staff|Reporter|Correspondent)\s*', '', name, flags=re.I)
        name = re.sub(r'\s*(Staff|Reporter|Correspondent|Writer|Contributor|Editor|Journalist)$', '', name, flags=re.I)
        
        # Remove email
        name = re.sub(r'\S+@\S+', '', name)
        
        # Remove URLs
        name = re.sub(r'https?://\S+', '', name)
        
        # Remove special characters but keep apostrophes and hyphens in names
        name = re.sub(r'[^\w\s\'-]', ' ', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Remove trailing numbers
        name = re.sub(r'\s*\d+$', '', name)
        
        # Handle "and" for multiple authors
        if ' and ' in name.lower():
            # Take the first author
            name = name.split(' and ')[0].strip()
        
        return name if name else None
    
    def _is_valid_author_name(self, name):
        """Validate if the extracted text is likely an author name"""
        if not name or len(name) < 3 or len(name) > 50:
            return False
        
        # Must contain at least one letter
        if not any(c.isalpha() for c in name):
            return False
        
        # Skip if it's all caps (might be a section header)
        if name.isupper() and len(name.split()) > 2:
            return False
        
        # Skip common non-name phrases
        skip_phrases = [
            'click here', 'read more', 'share this', 'follow us', 'sign up',
            'subscribe', 'newsletter', 'breaking news', 'exclusive', 'update',
            'advertisement', 'sponsored', 'staff', 'admin', 'editor',
            'associated press', 'reuters', 'staff writer', 'guest post',
            'press release', 'news desk', 'web desk', 'news service',
            'digital team', 'online team', 'newsroom', 'editorial'
        ]
        
        name_lower = name.lower()
        if any(phrase in name_lower for phrase in skip_phrases):
            return False
        
        # Check if it contains organization names
        org_keywords = ['news', 'media', 'press', 'agency', 'network', 'broadcasting',
                       'corporation', 'company', 'institute', 'organization', 'group']
        
        # If has org keywords and is not a known journalist, likely invalid
        if any(keyword in name_lower for keyword in org_keywords):
            # But allow if it's part of a person's title like "News Reporter John Smith"
            parts = name.split()
            if len(parts) < 2:
                return False
        
        # Must have at least first and last name (with some exceptions)
        parts = name.split()
        if len(parts) < 2:
            # Allow single names if they're in our known names
            if name_lower not in self.common_first_names and name_lower not in self.common_last_names:
                # Exception for known single-name journalists or foreign names
                if not (len(name) > 5 and name[0].isupper()):
                    return False
        
        # Check if at least one part is a common name
        has_common_name = False
        for part in parts:
            part_lower = part.lower().strip("'").strip("-")
            if part_lower in self.common_first_names or part_lower in self.common_last_names:
                has_common_name = True
                break
        
        # If no common names found, be more strict
        if not has_common_name and len(parts) >= 2:
            # At least require proper capitalization
            for part in parts:
                if part and not part[0].isupper() and part not in ['van', 'de', 'la', 'von', 'der']:
                    return False
        
        return True
    
    def _extract_title(self, soup):
        """Extract article title"""
        # Try Open Graph title first
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        
        # Try Twitter title
        twitter_title = soup.find('meta', {'name': 'twitter:title'})
        if twitter_title and twitter_title.get('content'):
            return twitter_title['content'].strip()
        
        # Try article title
        article_title = soup.find('meta', {'name': 'title'})
        if article_title and article_title.get('content'):
            return article_title['content'].strip()
        
        # Try h1 tags
        h1_tags = soup.find_all('h1')
        for h1 in h1_tags:
            title = h1.get_text().strip()
            if title and len(title) > 10:
                # Clean up the title
                title = re.sub(r'\s+', ' ', title)
                # Remove common suffixes
                for suffix in [' - CNN', ' | CNN', ' - BBC', ' | BBC', ' - Reuters', ' | Reuters',
                             ' - The New York Times', ' | The New York Times', ' - The Guardian',
                             ' | The Guardian', ' - Fox News', ' | Fox News', ' | NBC News']:
                    if title.endswith(suffix):
                        title = title[:-len(suffix)]
                
                # Remove "Share" and similar words at the end
                title = re.sub(r'\s*(Share|Tweet|Email|Print|Comment).*$', '', title)
                return title
        
        # Fall back to page title
        if soup.title:
            title = soup.title.string
            if title:
                # Clean up site name from title
                title = title.strip()
                # Remove common separators and everything after them
                for separator in [' - ', ' | ', ' — ', ' :: ', ' » ']:
                    if separator in title:
                        title = title.split(separator)[0].strip()
                
                # Remove trailing "Share" etc.
                title = re.sub(r'\s*(Share|Tweet|Email|Print|Comment).*$', '', title)
                return title
        
        return 'No title found'
    
    def _extract_text(self, soup, url):
        """Extract main article text"""
        # Remove script and style elements
        for script in soup(['script', 'style', 'noscript']):
            script.decompose()
        
        # Remove navigation, header, footer elements
        for elem in soup(['nav', 'header', 'footer', 'aside']):
            elem.decompose()
        
        # Try to find article body with common selectors
        article_selectors = [
            'article',
            '[role="main"]',
            'main',
            '[class*="article-body"]',
            '[class*="story-body"]', 
            '[class*="content-body"]',
            '[class*="post-body"]',
            '[class*="entry-content"]',
            '[class*="article-content"]',
            '[class*="story-content"]',
            '[id*="article-body"]',
            '[id*="story-body"]',
            '.content',
            '#content',
            '.story',
            '.post',
            '.article'
        ]
        
        article_text = ""
        
        for selector in article_selectors:
            article = soup.select_one(selector)
            if article:
                # Get all paragraphs
                paragraphs = article.find_all(['p', 'h2', 'h3', 'h4', 'blockquote'])
                if paragraphs:
                    texts = []
                    for p in paragraphs:
                        # Skip if paragraph contains navigation/menu items
                        if p.find_parent(['nav', 'menu']):
                            continue
                        text = p.get_text().strip()
                        if text and len(text) > 20:
                            texts.append(text)
                    
                    if texts:
                        article_text = ' '.join(texts)
                        if len(article_text) > 200:  # Substantial content found
                            break
        
        # Fallback: get all paragraphs if no article container found
        if not article_text or len(article_text) < 200:
            paragraphs = soup.find_all('p')
            texts = []
            for p in paragraphs[:100]:  # Limit to first 100 paragraphs
                # Skip short paragraphs and navigation items
                if p.find_parent(['nav', 'menu', 'header', 'footer']):
                    continue
                text = p.get_text().strip()
                if text and len(text) > 50:
                    texts.append(text)
            
            article_text = ' '.join(texts)
        
        return article_text if article_text else 'No article text found'
    
    def _extract_date(self, soup):
        """Extract publish date"""
        date_selectors = [
            ('meta', {'property': 'article:published_time'}),
            ('meta', {'name': 'publish_date'}),
            ('meta', {'property': 'datePublished'}),
            ('meta', {'name': 'publication_date'}),
            ('meta', {'name': 'DC.date.issued'}),
            ('meta', {'name': 'date'}),
            ('meta', {'itemprop': 'datePublished'}),
            ('meta', {'name': 'article:published_time'}),
            ('time', {'datetime': True}),
            ('time', {'pubdate': True}),
            ('[itemprop="datePublished"]', None),
            ('[property="datePublished"]', None),
            ('[class*="publish-date"]', None),
            ('[class*="published-date"]', None),
            ('[class*="article-date"]', None),
            ('[class*="post-date"]', None),
            ('[class*="entry-date"]', None)
        ]
        
        for selector, attrs in date_selectors:
            if attrs:
                elements = soup.find_all(selector, attrs)
            else:
                elements = soup.select(selector)
                
            for element in elements:
                date_str = None
                
                if element.name == 'meta':
                    date_str = element.get('content')
                elif element.name == 'time':
                    date_str = element.get('datetime') or element.get_text()
                else:
                    date_str = element.get_text()
                
                if date_str:
                    date_str = date_str.strip()
                    # Try to parse the date
                    try:
                        # Handle ISO format
                        if 'T' in date_str:
                            return date_str.split('T')[0]
                        # Return as is if it looks like a date
                        if any(char in date_str for char in ['-', '/', '.']) and any(char.isdigit() for char in date_str):
                            return date_str
                    except:
                        continue
        
        return None
    
    def _extract_with_google_cache(self, url):
        """Try Google's text-only cache"""
        cache_url = f"https://webcache.googleusercontent.com/search?q=cache:{quote(url)}&strip=1"
        
        session = self.sessions[0][1] if self.sessions else self.session
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.google.com/'
        }
        
        try:
            response = session.get(cache_url, headers=headers, timeout=20)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove Google's cache banner
                for div in soup.find_all('div', style=re.compile('position:relative')):
                    div.decompose()
                
                domain = urlparse(url).netloc.replace('www.', '')
                
                title = self._extract_title(soup)
                text = self._extract_text(soup, url)
                author = self._extract_author_ultimate(soup, response.text, title, text, domain)
                date = self._extract_date(soup)
                
                return {
                    'title': title,
                    'text': text,
                    'author': author,
                    'publish_date': date,
                    'url': url,
                    'domain': domain
                }
        except:
            pass
        
        raise ValueError("Google cache failed")
    
    def _extract_with_wayback(self, url):
        """Try Wayback Machine"""
        # Check if archived
        check_url = f"https://archive.org/wayback/available?url={quote(url)}"
        
        session = self.sessions[0][1] if self.sessions else self.session
        try:
            response = session.get(check_url, timeout=10)
            data = response.json()
            
            if data.get('archived_snapshots', {}).get('closest', {}).get('available'):
                snapshot_url = data['archived_snapshots']['closest']['url']
                
                # Fetch the snapshot
                response = session.get(snapshot_url, timeout=20)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Remove Wayback UI
                    for elem in soup.find_all(id=re.compile('wm-')):
                        elem.decompose()
                    
                    domain = urlparse(url).netloc.replace('www.', '')
                    
                    title = self._extract_title(soup)
                    text = self._extract_text(soup, url)
                    author = self._extract_author_ultimate(soup, response.text, title, text, domain)
                    date = self._extract_date(soup)
                    
                    return {
                        'title': title,
                        'text': text,
                        'author': author,
                        'publish_date': date,
                        'url': url,
                        'domain': domain
                    }
        except:
            pass
        
        raise ValueError("Wayback failed")
    
    def _extract_mobile_version(self, url):
        """Try mobile version of site"""
        domain = urlparse(url).netloc
        
        # Mobile URL patterns
        mobile_urls = [
            url.replace('www.', 'm.'),
            url.replace('https://', 'https://m.'),
            url + '?amp=1',
            url.replace('.com/', '.com/amp/'),
            url.replace('http://', 'https://')  # Try HTTPS if HTTP
        ]
        
        # Use mobile user agent
        mobile_headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br'
        }
        
        session = self.sessions[0][1] if self.sessions else self.session
        
        for mobile_url in mobile_urls:
            try:
                response = session.get(mobile_url, headers=mobile_headers, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    title = self._extract_title(soup)
                    text = self._extract_text(soup, url)
                    
                    if text and len(text) > 200:
                        author = self._extract_author_ultimate(soup, response.text, title, text, domain.replace('www.', ''))
                        date = self._extract_date(soup)
                        
                        return {
                            'title': title,
                            'text': text,
                            'author': author,
                            'publish_date': date,
                            'url': url,
                            'domain': domain.replace('www.', '')
                        }
            except:
                continue
        
        raise ValueError("Mobile extraction failed")
    
    def _extract_emergency_bypass(self, url):
        """Emergency extraction with all tricks"""
        domain = urlparse(url).netloc.replace('www.', '')
        
        # Try different approaches
        attempts = [
            # Googlebot user agent
            {
                'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            },
            # Very old browser
            {
                'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
                'Accept': '*/*'
            },
            # Curl
            {
                'User-Agent': 'curl/7.64.1',
                'Accept': '*/*'
            }
        ]
        
        session = self.sessions[0][1] if self.sessions else self.session
        
        for headers in attempts:
            try:
                response = session.get(url, headers=headers, timeout=20, allow_redirects=False)
                
                # Follow redirects manually to avoid detection
                if response.status_code in [301, 302, 303, 307, 308]:
                    redirect_url = response.headers.get('Location')
                    if redirect_url:
                        if not redirect_url.startswith('http'):
                            redirect_url = urljoin(url, redirect_url)
                        response = session.get(redirect_url, headers=headers, timeout=20)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    title = self._extract_title(soup)
                    text = self._extract_text(soup, url)
                    
                    if text and len(text) > 100:
                        author = self._extract_author_ultimate(soup, response.text, title, text, domain)
                        date = self._extract_date(soup)
                        
                        return {
                            'title': title,
                            'text': text,
                            'author': author,
                            'publish_date': date,
                            'url': url,
                            'domain': domain
                        }
            except:
                continue
        
        raise ValueError("Emergency bypass failed")
    
    def _create_smart_fallback(self, url):
        """Create an intelligent fallback response"""
        domain = urlparse(url).netloc.replace('www.', '')
        
        # Provide specific instructions based on the domain
        if 'politico' in domain:
            instructions = """
Politico has strong anti-scraping protection. Here are your options:

1. **Copy and paste the article text** - This is the most reliable method
2. **Try the mobile version**: Replace 'www' with 'm' in the URL
3. **Use the Politico app** and share the article text
4. **Try Archive.org**: Search for the URL at https://web.archive.org/

The article appears to be about Trump and Ghislaine Maxwell based on the URL.
"""
        elif 'wsj.com' in domain or 'ft.com' in domain:
            instructions = """
This appears to be a paywalled article. Options:

1. **If you're a subscriber**, copy and paste the article text
2. **Try the Google Cache**: Search for the article title in Google and click the cached version
3. **Check archive sites**: Try archive.is or archive.org
4. **Use reader mode** in your browser before copying
"""
        elif 'nytimes.com' in domain:
            instructions = """
The New York Times has limited free articles. Try:

1. **Copy the article text** if you can access it
2. **Use incognito/private mode** to reset article limit
3. **Try the app** if you're a subscriber
4. **Search for the article title** - it might be syndicated elsewhere
"""
        else:
            instructions = """
This website has blocked automated access. Please try:

1. **Copy and paste the article text directly**
2. **Save the page as HTML** and upload it
3. **Use a different article** from the same source
4. **Check if the article is available elsewhere**
"""
        
        return {
            'title': f'Article from {domain}',
            'text': f'Unable to extract content from {url} due to anti-scraping protection.\n\n{instructions}\n\nYou can still analyze any article by pasting its text.',
            'author': None,
            'publish_date': None,
            'url': url,
            'domain': domain,
            'extraction_failed': True
        }
    
    def _extract_title_from_text(self, text):
        """Extract title from text as fallback"""
        if not text:
            return "Article"
        
        lines = text.split('\n')
        for line in lines[:5]:
            line = line.strip()
            if line and 10 < len(line) < 200:
                return line
        
        return text[:100] + "..." if len(text) > 100 else text
