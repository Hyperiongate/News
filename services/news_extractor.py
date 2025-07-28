"""
FILE: services/news_extractor.py
LOCATION: services/news_extractor.py
PURPOSE: ULTIMATE UNIVERSAL news extractor - extracts from ANY website
"""

import logging
import re
import json
import time
import random
from datetime import datetime
from urllib.parse import urlparse, urljoin, parse_qs
from collections import Counter, defaultdict
from html import unescape

import requests
from bs4 import BeautifulSoup, NavigableString, Comment

# Try to import optional libraries
try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    import trafilatura
    TRAFILATURA_AVAILABLE = True
except ImportError:
    TRAFILATURA_AVAILABLE = False

try:
    from newspaper import Article
    NEWSPAPER_AVAILABLE = True
except ImportError:
    NEWSPAPER_AVAILABLE = False

logger = logging.getLogger(__name__)

class NewsExtractor:
    """Ultimate universal news extractor that WILL extract from any URL"""
    
    def __init__(self):
        # Initialize session with cloudscraper if available
        if CLOUDSCRAPER_AVAILABLE:
            self.session = cloudscraper.create_scraper(
                browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
            )
        else:
            self.session = requests.Session()
        
        # Multiple user agents including mobile
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)'
        ]
        
        self.current_ua_index = 0
        self._update_session_headers()
        
        # Common name lists
        self.common_first_names = set(['james', 'john', 'robert', 'michael', 'william', 'david', 'richard', 'joseph',
            'thomas', 'charles', 'mary', 'patricia', 'jennifer', 'linda', 'elizabeth', 'barbara', 'susan', 
            'jessica', 'sarah', 'karen', 'daniel', 'matthew', 'donald', 'mark', 'paul', 'steven', 'andrew',
            'kenneth', 'joshua', 'kevin', 'brian', 'george', 'edward', 'ronald', 'timothy', 'jason',
            'jeffrey', 'ryan', 'jacob', 'gary', 'nicholas', 'eric', 'jonathan', 'stephen', 'larry',
            'justin', 'scott', 'brandon', 'benjamin', 'samuel', 'frank', 'gregory', 'raymond', 'alexander',
            'patrick', 'jack', 'dennis', 'jerry', 'tyler', 'aaron', 'jose', 'nathan', 'henry', 'zachary',
            'douglas', 'peter', 'adam', 'noah', 'christopher', 'nancy', 'betty', 'helen', 'sandra', 'donna',
            'carol', 'ruth', 'sharon', 'michelle', 'laura', 'kimberly', 'deborah', 'rachel', 'amy', 'anna',
            'maria', 'dorothy', 'lisa', 'ashley', 'madison', 'amanda', 'melissa', 'debra', 'stephanie',
            'rebecca', 'virginia', 'kathleen', 'pamela', 'martha', 'angela', 'katherine', 'christine',
            'emma', 'olivia', 'sophia', 'isabella', 'charlotte', 'amelia', 'evelyn', 'harper', 'luna',
            'jeremy', 'simon', 'martin', 'alan', 'ian', 'colin', 'graham', 'ben', 'alex', 'sam'])
        
        self.common_last_names = set(['smith', 'johnson', 'williams', 'brown', 'jones', 'garcia', 'miller', 
            'davis', 'rodriguez', 'martinez', 'hernandez', 'lopez', 'gonzalez', 'wilson', 'anderson',
            'thomas', 'taylor', 'moore', 'jackson', 'martin', 'lee', 'perez', 'thompson', 'white',
            'harris', 'sanchez', 'clark', 'ramirez', 'lewis', 'robinson', 'walker', 'young', 'allen',
            'king', 'wright', 'scott', 'torres', 'nguyen', 'hill', 'flores', 'green', 'adams', 'nelson',
            'baker', 'hall', 'rivera', 'campbell', 'mitchell', 'carter', 'roberts', 'bowen', 'cohen',
            'chen', 'wang', 'kim', 'silva', 'patel', 'khan', 'murphy', 'stewart', 'morgan', 'cooper'])
    
    def _update_session_headers(self):
        """Update session with comprehensive headers"""
        ua = self.user_agents[self.current_ua_index]
        
        headers = {
            'User-Agent': ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Pragma': 'no-cache'
        }
        
        # Add mobile-specific headers if using mobile UA
        if 'iPhone' in ua or 'Android' in ua:
            headers['X-Requested-With'] = 'XMLHttpRequest'
            
        self.session.headers.update(headers)
    
    def extract_article(self, url):
        """Extract article with ultimate fallback chain"""
        logger.info(f"🚀 ULTIMATE EXTRACTION for: {url}")
        
        methods = [
            ("Method 1: Smart Extraction", self._extract_smart),
            ("Method 2: JavaScript Rendering", self._extract_with_js),
            ("Method 3: Newspaper3k", self._extract_with_newspaper),
            ("Method 4: Trafilatura", self._extract_with_trafilatura),
            ("Method 5: Mobile Site", self._extract_mobile),
            ("Method 6: Archive.org", self._extract_from_archive),
            ("Method 7: Google Cache", self._extract_from_google_cache),
            ("Method 8: Raw HTML Mining", self._extract_raw_mining),
            ("Method 9: Emergency Extraction", self._extract_emergency_final)
        ]
        
        best_result = None
        best_score = 0
        
        for method_name, method_func in methods:
            try:
                logger.info(f"Trying {method_name}...")
                result = method_func(url)
                
                if result:
                    # Score the result
                    score = self._score_extraction(result)
                    logger.info(f"{method_name} score: {score}")
                    
                    if score > best_score:
                        best_result = result
                        best_score = score
                    
                    # If we have a great result, stop trying
                    if score > 80:
                        logger.info(f"✅ Excellent result from {method_name}")
                        return result
                        
            except Exception as e:
                logger.warning(f"{method_name} failed: {str(e)}")
                continue
        
        # Return best result or create fallback
        if best_result:
            return best_result
        else:
            return self._create_ultimate_fallback(url)
    
    def _extract_smart(self, url):
        """Smart extraction with all enhancements"""
        # Try different request strategies
        response = None
        
        # Strategy 1: Normal request
        try:
            response = self.session.get(url, timeout=30, allow_redirects=True)
            if response.status_code != 200:
                response = None
        except:
            pass
        
        # Strategy 2: With referrer
        if not response:
            try:
                headers = {'Referer': 'https://www.google.com/'}
                response = self.session.get(url, headers=headers, timeout=30)
            except:
                pass
        
        # Strategy 3: Mobile user agent
        if not response:
            try:
                self._rotate_user_agent()
                response = self.session.get(url, timeout=30)
            except:
                pass
        
        if not response or response.status_code != 200:
            raise ValueError("Failed to fetch page")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        domain = urlparse(url).netloc.replace('www.', '')
        
        # Clean the soup
        self._deep_clean_soup(soup)
        
        # Extract everything
        title = self._extract_title_ultimate(soup, response.text)
        text = self._extract_text_ultimate(soup, response.text, url)
        author = self._extract_author_max(soup, response.text, domain)
        date = self._extract_date_ultimate(soup, response.text)
        
        return {
            'title': title or 'Article',
            'text': text or 'Unable to extract text',
            'author': author,
            'publish_date': date,
            'url': url,
            'domain': domain
        }
    
    def _deep_clean_soup(self, soup):
        """Aggressively clean HTML soup"""
        # Remove all unwanted tags
        for tag in soup(['script', 'style', 'noscript', 'iframe', 'svg', 'canvas', 
                        'embed', 'object', 'param', 'source', 'track']):
            tag.decompose()
        
        # Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        
        # Remove hidden elements
        for element in soup.find_all(style=re.compile(r'display:\s*none')):
            element.decompose()
        
        for element in soup.find_all(class_=re.compile(r'hidden|hide')):
            element.decompose()
    
    def _extract_title_ultimate(self, soup, html_text):
        """Extract title using every possible method"""
        candidates = []
        
        # Method 1: Meta tags
        meta_tags = [
            ('meta', {'property': 'og:title'}),
            ('meta', {'name': 'twitter:title'}),
            ('meta', {'property': 'article:title'}),
            ('meta', {'name': 'title'}),
            ('meta', {'itemprop': 'headline'}),
            ('meta', {'name': 'dc.title'}),
            ('meta', {'name': 'DC.title'})
        ]
        
        for tag, attrs in meta_tags:
            elem = soup.find(tag, attrs)
            if elem and elem.get('content'):
                candidates.append(elem['content'].strip())
        
        # Method 2: H1 tags
        for h1 in soup.find_all('h1'):
            text = h1.get_text().strip()
            if text and 10 < len(text) < 200:
                candidates.append(text)
        
        # Method 3: Title tag
        if soup.title:
            title_text = soup.title.get_text().strip()
            # Clean common suffixes
            for sep in [' - ', ' | ', ' — ', ' :: ', ' » ', ' / ']:
                if sep in title_text:
                    title_text = title_text.split(sep)[0].strip()
            if title_text:
                candidates.append(title_text)
        
        # Method 4: JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if 'headline' in data:
                        candidates.append(data['headline'])
                    if '@graph' in data:
                        for item in data['@graph']:
                            if isinstance(item, dict) and 'headline' in item:
                                candidates.append(item['headline'])
            except:
                continue
        
        # Return best candidate
        if candidates:
            # Prefer longer, more descriptive titles
            candidates.sort(key=lambda x: len(x), reverse=True)
            return candidates[0]
        
        return "Article"
    
    def _extract_text_ultimate(self, soup, html_text, url):
        """Ultimate text extraction"""
        # Method 1: Try structured data first
        text = self._extract_from_structured_data(soup)
        if text and len(text) > 500:
            return text
        
        # Method 2: Content scoring algorithm
        text = self._extract_by_scoring(soup)
        if text and len(text) > 500:
            return text
        
        # Method 3: Density-based extraction
        text = self._extract_by_density(soup)
        if text and len(text) > 500:
            return text
        
        # Method 4: Pattern-based extraction
        text = self._extract_by_patterns(soup)
        if text and len(text) > 500:
            return text
        
        # Method 5: Just get all paragraphs
        paragraphs = []
        for p in soup.find_all(['p', 'div']):
            text = p.get_text().strip()
            if len(text) > 50:
                paragraphs.append(text)
        
        if paragraphs:
            return ' '.join(paragraphs[:100])  # Limit to 100 paragraphs
        
        return "Unable to extract article content"
    
    def _extract_from_structured_data(self, soup):
        """Extract from JSON-LD or microdata"""
        # Try JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                
                # Navigate different structures
                if isinstance(data, list):
                    data = data[0]
                
                # Look for article body
                if isinstance(data, dict):
                    # Direct articleBody
                    if 'articleBody' in data:
                        return data['articleBody']
                    
                    # In @graph
                    if '@graph' in data:
                        for item in data['@graph']:
                            if isinstance(item, dict):
                                if 'articleBody' in item:
                                    return item['articleBody']
                                if '@type' in item and 'Article' in str(item['@type']):
                                    if 'text' in item:
                                        return item['text']
                    
                    # Other fields
                    for field in ['text', 'description', 'mainEntityOfPage']:
                        if field in data and isinstance(data[field], str):
                            if len(data[field]) > 500:
                                return data[field]
            except:
                continue
        
        return None
    
    def _extract_by_scoring(self, soup):
        """Score-based content extraction"""
        candidates = []
        
        # Score all major containers
        for container in soup.find_all(['div', 'section', 'article', 'main']):
            score = 0
            text = container.get_text().strip()
            
            if len(text) < 200:
                continue
            
            # Positive signals
            score += len(container.find_all('p')) * 3
            score += len(text) / 100
            score += text.count('.') * 2
            score += text.count(',')
            
            # Check for article indicators
            classes = ' '.join(container.get('class', []))
            if any(ind in classes.lower() for ind in ['article', 'content', 'body', 'story', 'post']):
                score += 50
            
            # Negative signals
            score -= len(container.find_all('a')) * 2
            score -= len(container.find_all(['script', 'style']))
            
            if any(ind in classes.lower() for ind in ['comment', 'sidebar', 'menu', 'nav', 'footer']):
                score -= 100
            
            candidates.append((score, container))
        
        # Get best candidate
        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            best_container = candidates[0][1]
            
            # Extract text from best container
            paragraphs = []
            for p in best_container.find_all(['p', 'h2', 'h3', 'h4', 'blockquote']):
                text = p.get_text().strip()
                if text and len(text) > 20:
                    paragraphs.append(text)
            
            return ' '.join(paragraphs)
        
        return None
    
    def _extract_by_density(self, soup):
        """Density-based extraction"""
        # Calculate text density for each element
        densities = []
        
        for elem in soup.find_all(['div', 'section', 'article']):
            text = elem.get_text().strip()
            if len(text) < 100:
                continue
            
            # Calculate link density
            link_text = sum(len(a.get_text()) for a in elem.find_all('a'))
            total_text = len(text)
            
            if total_text > 0:
                link_density = link_text / total_text
                
                # Low link density is good
                if link_density < 0.3:
                    densities.append((1 - link_density, elem))
        
        if densities:
            densities.sort(key=lambda x: x[0], reverse=True)
            best_elem = densities[0][1]
            
            # Extract paragraphs
            return ' '.join(p.get_text().strip() for p in best_elem.find_all('p') if p.get_text().strip())
        
        return None
    
    def _extract_by_patterns(self, soup):
        """Pattern-based extraction"""
        # Extended selectors
        selectors = [
            'article', '[role="main"]', 'main', '.article-body', '.story-body',
            '.content-body', '.post-body', '.entry-content', '.article-content',
            '.story-content', '#article-body', '#story-body', '.content',
            '#content', '.story', '.post', '.article', '.article-text',
            '.article__body', '.article__content', '.story__content',
            '.c-entry-content', '.entry__content', '.post__content',
            '[itemprop="articleBody"]', '[class*="body"]', '[class*="content"]',
            '.prose', '.rich-text', '.text-content', '.main-content',
            '.primary-content', '.page-content', '.post-content'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text().strip()
                if len(text) > 500:
                    # Extract paragraphs properly
                    paragraphs = []
                    for p in elem.find_all(['p', 'div']):
                        p_text = p.get_text().strip()
                        if len(p_text) > 30:
                            paragraphs.append(p_text)
                    
                    if paragraphs:
                        return ' '.join(paragraphs)
        
        return None
    
    def _extract_author_max(self, soup, html_text, domain):
        """Maximum effort author extraction"""
        candidates = defaultdict(int)
        
        # Method 1: Domain-specific patterns
        domain_patterns = {
            'politico.com': [
                r'<p[^>]*class="story-meta__authors"[^>]*>([^<]+)</p>',
                r'<span[^>]*class="story-by-author"[^>]*>([^<]+)</span>',
                r'<div[^>]*class="byline"[^>]*>([^<]+)</div>',
                r'href="/staff/([^"]+)"[^>]*>([^<]+)</a>',
                r'"authors":\s*\[([^\]]+)\]',
                r'data-authors="([^"]+)"',
                r'<address[^>]*>([^<]+)</address>'
            ],
            'cnn.com': [
                r'class="byline__name"[^>]*>([^<]+)',
                r'class="metadata__byline__author"[^>]*>([^<]+)',
                r'"author"[^}]*"name":\s*"([^"]+)"'
            ],
            'bbc': [
                r'<span[^>]*class="byline__name"[^>]*>([^<]+)</span>',
                r'By\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'<p[^>]*class="contributor[^>]*>([^<]+)</p>'
            ],
            'nytimes.com': [
                r'itemprop="author"[^>]*>([^<]+)',
                r'class="byline-author"[^>]*>([^<]+)',
                r'"author"[^}]*"name":\s*"([^"]+)"'
            ],
            'washingtonpost.com': [
                r'class="author-name"[^>]*>([^<]+)',
                r'rel="author"[^>]*>([^<]+)',
                r'"author"[^}]*"name":\s*"([^"]+)"'
            ],
            'reuters.com': [
                r'class="author-name"[^>]*>([^<]+)',
                r'By\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'"author":\s*"([^"]+)"'
            ]
        }
        
        # Apply domain patterns
        for pattern_domain, patterns in domain_patterns.items():
            if pattern_domain in domain:
                for pattern in patterns:
                    matches = re.findall(pattern, html_text, re.IGNORECASE | re.DOTALL)
                    for match in matches:
                        if isinstance(match, tuple):
                            match = match[-1]  # Take last group
                        
                        author = self._clean_author_name(match)
                        if author and self._is_valid_author(author):
                            candidates[author] += 10
        
        # Method 2: Meta tags
        meta_selectors = [
            ('meta', {'name': 'author'}),
            ('meta', {'property': 'author'}),
            ('meta', {'property': 'article:author'}),
            ('meta', {'name': 'byl'}),
            ('meta', {'name': 'DC.creator'}),
            ('meta', {'name': 'citation_author'}),
            ('meta', {'property': 'og:article:author'}),
            ('meta', {'itemprop': 'author'}),
            ('meta', {'name': 'parsely-author'}),
            ('meta', {'name': 'sailthru.author'})
        ]
        
        for tag, attrs in meta_selectors:
            elements = soup.find_all(tag, attrs)
            for elem in elements:
                content = elem.get('content', '')
                if content:
                    authors = self._parse_author_string(content)
                    for author in authors:
                        if self._is_valid_author(author):
                            candidates[author] += 8
        
        # Method 3: JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                authors_found = self._extract_authors_from_json(data)
                for author in authors_found:
                    if self._is_valid_author(author):
                        candidates[author] += 9
            except:
                continue
        
        # Method 4: Byline selectors
        byline_selectors = [
            '.author', '.byline', '.by-line', '.writer', '.author-name',
            '.story-meta__authors', '.article-author', '.post-author',
            '.contributor', '.journalist', '.reporter', '.staff-name',
            '[class*="author"]', '[class*="byline"]', '[class*="writer"]',
            '[itemprop="author"]', '[rel="author"]', 'address',
            '.vcard', '.h-card', '.byline-name', '.by', '.written-by',
            'a[href*="/author/"]', 'a[href*="/staff/"]', 'a[href*="/people/"]'
        ]
        
        for selector in byline_selectors:
            elements = soup.select(selector)
            for elem in elements[:10]:  # Limit to avoid false positives
                text = elem.get_text().strip()
                
                # Skip if too long or contains excluded phrases
                if len(text) > 100 or self._is_excluded_text(text):
                    continue
                
                authors = self._parse_author_string(text)
                for author in authors:
                    if self._is_valid_author(author):
                        candidates[author] += 5
        
        # Method 5: Text patterns
        text_patterns = [
            r'(?:By|BY|by)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,3})',
            r'(?:Written by|WRITTEN BY)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,3})',
            r'(?:Reported by|REPORTED BY)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,3})',
            r'(?:Author:|AUTHOR:)\s*([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,3})',
            r'^([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,3})\s+(?:is|writes|reports)',
            r'Contact\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,3})\s+at',
            r'([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,3})\s+\|\s+\d{1,2}[/.-]\d{1,2}',
            r'—\s*([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,3})$'
        ]
        
        # Search in first 3000 chars
        search_text = html_text[:3000] + ' ' + soup.get_text()[:2000]
        
        for pattern in text_patterns:
            matches = re.findall(pattern, search_text, re.MULTILINE)
            for match in matches:
                author = self._clean_author_name(match)
                if author and self._is_valid_author(author):
                    candidates[author] += 3
        
        # Method 6: Look near date/time
        date_elements = soup.find_all(['time', 'span', 'div'], class_=re.compile(r'date|time|published'))
        for date_elem in date_elements:
            # Check siblings and parent
            parent = date_elem.parent
            if parent:
                text = parent.get_text()
                authors = self._parse_author_string(text)
                for author in authors:
                    if self._is_valid_author(author):
                        candidates[author] += 2
        
        # Method 7: Email patterns
        email_pattern = r'([a-zA-Z0-9._%+-]+)@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, search_text)
        for email_user in emails[:5]:
            # Convert email to potential name
            name_parts = re.split(r'[._-]', email_user)
            if len(name_parts) >= 2:
                potential_name = ' '.join(part.capitalize() for part in name_parts[:2])
                if self._is_valid_author(potential_name):
                    candidates[potential_name] += 1
        
        # Return best candidate
        if candidates:
            # Sort by score and name quality
            sorted_candidates = sorted(candidates.items(), key=lambda x: (x[1], len(x[0].split())), reverse=True)
            return sorted_candidates[0][0]
        
        return None
    
    def _extract_authors_from_json(self, data):
        """Recursively extract authors from JSON data"""
        authors = []
        
        if isinstance(data, dict):
            # Direct author fields
            for field in ['author', 'authors', 'creator', 'creators', 'byline']:
                if field in data:
                    value = data[field]
                    if isinstance(value, str):
                        authors.extend(self._parse_author_string(value))
                    elif isinstance(value, dict) and 'name' in value:
                        authors.append(value['name'])
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, str):
                                authors.append(item)
                            elif isinstance(item, dict) and 'name' in item:
                                authors.append(item['name'])
            
            # Recurse into nested structures
            for key in ['@graph', 'mainEntity', 'mainEntityOfPage']:
                if key in data:
                    authors.extend(self._extract_authors_from_json(data[key]))
                    
        elif isinstance(data, list):
            for item in data:
                authors.extend(self._extract_authors_from_json(item))
        
        return authors
    
    def _parse_author_string(self, text):
        """Parse author string to extract individual names"""
        if not text:
            return []
        
        # Clean the text
        text = re.sub(r'^(By|Written by|Reported by|Author:|Story by)\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Skip if too long
        if len(text) > 100:
            return []
        
        authors = []
        
        # Split by common separators
        parts = re.split(r'\s+and\s+|\s*,\s*|\s*&\s*', text)
        
        for part in parts:
            part = part.strip()
            if part:
                # Remove common suffixes
                part = re.sub(r'\s*(Reporter|Correspondent|Editor|Writer|Contributor|Staff)$', '', part, flags=re.IGNORECASE)
                
                if part and 2 < len(part) < 50:
                    authors.append(part)
        
        return authors
    
    def _clean_author_name(self, name):
        """Clean author name"""
        if not name:
            return None
        
        # Decode HTML entities
        name = unescape(str(name))
        
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Remove common prefixes/suffixes
        name = re.sub(r'^(By|Written by|Reported by|Author:|Story by|From)\s+', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*(Reporter|Correspondent|Editor|Writer|Contributor|Staff Writer)$', '', name, flags=re.IGNORECASE)
        
        # Remove email
        name = re.sub(r'\S+@\S+', '', name).strip()
        
        # Remove special characters but keep apostrophes and hyphens
        name = re.sub(r'[^\w\s\'-]', ' ', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name if name else None
    
    def _is_valid_author(self, name):
        """Validate author name"""
        if not name or len(name) < 3 or len(name) > 60:
            return False
        
        # Must contain letters
        if not any(c.isalpha() for c in name):
            return False
        
        # Skip organization names
        org_keywords = ['news', 'staff', 'team', 'desk', 'editorial', 'admin',
                       'associated press', 'reuters', 'agency', 'wire service']
        
        name_lower = name.lower()
        if any(keyword in name_lower for keyword in org_keywords):
            return False
        
        # Check for common name patterns
        parts = name.split()
        if len(parts) >= 2:
            # At least one part should be a common name
            for part in parts:
                part_lower = part.lower()
                if (part_lower in self.common_first_names or 
                    part_lower in self.common_last_names):
                    return True
        
        # Allow single names if they're capitalized properly
        if len(parts) == 1 and name[0].isupper():
            return True
        
        # Check for proper capitalization
        if len(parts) >= 2:
            for part in parts:
                if part and part[0].islower() and part not in ['de', 'van', 'von', 'der', 'la']:
                    return False
        
        return True
    
    def _is_excluded_text(self, text):
        """Check if text should be excluded"""
        if not text:
            return True
        
        text_lower = text.lower()
        
        exclude_phrases = [
            'share', 'tweet', 'email', 'print', 'comment', 'subscribe',
            'follow us', 'advertisement', 'sponsored', 'more stories',
            'related articles', 'continue reading', 'sign up', 'log in',
            'privacy policy', 'terms of service', 'cookie policy'
        ]
        
        return any(phrase in text_lower for phrase in exclude_phrases)
    
    def _extract_date_ultimate(self, soup, html_text):
        """Extract date using all methods"""
        # Try meta tags first
        date_meta_tags = [
            ('meta', {'property': 'article:published_time'}),
            ('meta', {'name': 'publish_date'}),
            ('meta', {'property': 'datePublished'}),
            ('meta', {'itemprop': 'datePublished'}),
            ('meta', {'name': 'publication_date'}),
            ('meta', {'name': 'date'}),
            ('meta', {'name': 'DC.date.issued'}),
            ('meta', {'name': 'article.published'}),
            ('meta', {'name': 'published_time'})
        ]
        
        for tag, attrs in date_meta_tags:
            elem = soup.find(tag, attrs)
            if elem and elem.get('content'):
                date_str = elem['content']
                if date_str:
                    return self._parse_date(date_str)
        
        # Try time elements
        for time_elem in soup.find_all('time'):
            datetime_attr = time_elem.get('datetime')
            if datetime_attr:
                return self._parse_date(datetime_attr)
        
        # Try JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                date_str = self._extract_date_from_json(data)
                if date_str:
                    return self._parse_date(date_str)
            except:
                continue
        
        # Try patterns in text
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})',
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, html_text[:5000], re.IGNORECASE)
            if matches:
                return self._parse_date(matches[0])
        
        return None
    
    def _extract_date_from_json(self, data):
        """Extract date from JSON data"""
        if isinstance(data, dict):
            # Check common date fields
            for field in ['datePublished', 'dateCreated', 'dateModified', 'publishedDate', 'date']:
                if field in data:
                    return data[field]
            
            # Check nested structures
            for key in ['@graph', 'mainEntity']:
                if key in data:
                    result = self._extract_date_from_json(data[key])
                    if result:
                        return result
                        
        elif isinstance(data, list):
            for item in data:
                result = self._extract_date_from_json(item)
                if result:
                    return result
        
        return None
    
    def _parse_date(self, date_str):
        """Parse date string to standard format"""
        if not date_str:
            return None
        
        # Already in good format
        if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
            return date_str.split('T')[0]
        
        # Try to parse other formats
        try:
            # Common formats
            formats = [
                '%Y-%m-%d',
                '%m/%d/%Y',
                '%d/%m/%Y',
                '%B %d, %Y',
                '%b %d, %Y',
                '%d %B %Y',
                '%d %b %Y'
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d')
                except:
                    continue
        except:
            pass
        
        return date_str
    
    def _score_extraction(self, result):
        """Score extraction quality"""
        score = 0
        
        # Title quality
        if result.get('title') and result['title'] != 'Article':
            score += 20
            if len(result['title']) > 20:
                score += 10
        
        # Text quality
        text = result.get('text', '')
        if text:
            text_len = len(text)
            if text_len > 1000:
                score += 30
            elif text_len > 500:
                score += 20
            elif text_len > 200:
                score += 10
            
            # Check for paragraph structure
            if text.count('.') > 10:
                score += 10
            
            # Penalize "unable to extract" messages
            if 'unable to extract' in text.lower():
                score -= 50
        
        # Author presence
        if result.get('author'):
            score += 20
        
        # Date presence  
        if result.get('publish_date'):
            score += 10
        
        return score
    
    def _extract_with_js(self, url):
        """Extract using Selenium for JavaScript sites"""
        if not SELENIUM_AVAILABLE:
            raise ValueError("Selenium not available")
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument(f'user-agent={self.user_agents[0]}')
        
        driver = None
        try:
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            
            # Wait for content to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Scroll to trigger lazy loading
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(1)
            
            # Get the rendered HTML
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract using standard methods
            domain = urlparse(url).netloc.replace('www.', '')
            
            return {
                'title': self._extract_title_ultimate(soup, html),
                'text': self._extract_text_ultimate(soup, html, url),
                'author': self._extract_author_max(soup, html, domain),
                'publish_date': self._extract_date_ultimate(soup, html),
                'url': url,
                'domain': domain
            }
            
        finally:
            if driver:
                driver.quit()
    
    def _extract_with_newspaper(self, url):
        """Extract using newspaper3k"""
        if not NEWSPAPER_AVAILABLE:
            raise ValueError("Newspaper not available")
        
        article = Article(url)
        article.download()
        article.parse()
        
        if not article.text or len(article.text) < 200:
            raise ValueError("Insufficient content")
        
        # Get authors
        authors = article.authors
        author = authors[0] if authors else None
        
        return {
            'title': article.title or 'Article',
            'text': article.text,
            'author': author,
            'publish_date': article.publish_date.strftime('%Y-%m-%d') if article.publish_date else None,
            'url': url,
            'domain': urlparse(url).netloc.replace('www.', '')
        }
    
    def _extract_with_trafilatura(self, url):
        """Extract using trafilatura"""
        if not TRAFILATURA_AVAILABLE:
            raise ValueError("Trafilatura not available")
        
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            raise ValueError("Failed to download")
        
        # Extract with metadata
        result = trafilatura.extract(downloaded, output_format='json', 
                                   include_comments=False, include_tables=True)
        
        if result:
            data = json.loads(result)
            
            return {
                'title': data.get('title', 'Article'),
                'text': data.get('text', ''),
                'author': data.get('author'),
                'publish_date': data.get('date'),
                'url': url,
                'domain': data.get('hostname', urlparse(url).netloc)
            }
        
        raise ValueError("Extraction failed")
    
    def _extract_mobile(self, url):
        """Try mobile version of site"""
        # Convert to mobile URL
        mobile_url = url
        
        # Common mobile patterns
        if 'm.' not in url:
            parsed = urlparse(url)
            mobile_url = f"{parsed.scheme}://m.{parsed.netloc}{parsed.path}"
        
        # Use mobile user agent
        old_ua = self.session.headers['User-Agent']
        self.session.headers['User-Agent'] = self.user_agents[4]  # iPhone UA
        
        try:
            return self._extract_smart(mobile_url)
        finally:
            self.session.headers['User-Agent'] = old_ua
    
    def _extract_from_archive(self, url):
        """Try archive.org version"""
        archive_url = f"https://web.archive.org/web/2/{url}"
        
        try:
            response = self.session.get(archive_url, timeout=30)
            if response.status_code == 200:
                # Process with standard extraction
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove archive.org elements
                for elem in soup.find_all(id=re.compile('wm-')):
                    elem.decompose()
                
                domain = urlparse(url).netloc.replace('www.', '')
                
                return {
                    'title': self._extract_title_ultimate(soup, response.text),
                    'text': self._extract_text_ultimate(soup, response.text, url),
                    'author': self._extract_author_max(soup, response.text, domain),
                    'publish_date': self._extract_date_ultimate(soup, response.text),
                    'url': url,
                    'domain': domain
                }
        except:
            raise ValueError("Archive extraction failed")
    
    def _extract_from_google_cache(self, url):
        """Try Google cache version"""
        cache_url = f"https://webcache.googleusercontent.com/search?q=cache:{url}"
        
        try:
            response = self.session.get(cache_url, timeout=30)
            if response.status_code == 200:
                return self._extract_smart(url)
        except:
            raise ValueError("Cache extraction failed")
    
    def _extract_raw_mining(self, url):
        """Raw HTML mining as last resort"""
        response = self.session.get(url, timeout=60)
        
        if response.status_code != 200:
            raise ValueError("Failed to fetch")
        
        # Get raw text
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get ALL text
        all_text = soup.get_text()
        
        # Clean it up
        lines = all_text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line and len(line) > 30:
                # Skip navigation/menu items
                if not any(skip in line.lower() for skip in ['menu', 'search', 'sign in', 'subscribe']):
                    cleaned_lines.append(line)
        
        # Find the longest contiguous block
        if cleaned_lines:
            text = ' '.join(cleaned_lines[:200])  # First 200 good lines
            
            return {
                'title': self._extract_title_ultimate(soup, response.text) or cleaned_lines[0][:100],
                'text': text,
                'author': self._extract_author_max(soup, response.text, urlparse(url).netloc),
                'publish_date': self._extract_date_ultimate(soup, response.text),
                'url': url,
                'domain': urlparse(url).netloc.replace('www.', '')
            }
        
        raise ValueError("No content found")
    
    def _extract_emergency_final(self, url):
        """Final emergency extraction"""
        try:
            # Try with requests-html or other tools
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            
            if response.status_code == 200:
                # Just get something
                text = re.sub(r'<[^>]+>', ' ', response.text)
                text = re.sub(r'\s+', ' ', text)
                
                # Find blocks of text
                sentences = re.findall(r'[A-Z][^.!?]*[.!?]', text)
                
                if sentences:
                    content = ' '.join(sentences[:100])
                    
                    return {
                        'title': 'Article from ' + urlparse(url).netloc,
                        'text': content,
                        'author': None,
                        'publish_date': None,
                        'url': url,
                        'domain': urlparse(url).netloc.replace('www.', '')
                    }
        except:
            pass
        
        raise ValueError("Emergency extraction failed")
    
    def _create_ultimate_fallback(self, url):
        """Create fallback result"""
        domain = urlparse(url).netloc.replace('www.', '')
        
        return {
            'title': f'Article from {domain}',
            'text': f'''Unable to extract article content from {url}.
            
This could be due to:
- The page requires JavaScript rendering
- Content is behind a paywall
- The site blocks automated access
- Unusual page structure

Please try:
1. Copying and pasting the article text directly
2. Using a different article from the same source
3. Checking if the URL is correct and accessible

The analysis can still be performed on pasted text.''',
            'author': None,
            'publish_date': None,
            'url': url,
            'domain': domain,
            'extraction_failed': True
        }
    
    def _rotate_user_agent(self):
        """Rotate to next user agent"""
        self.current_ua_index = (self.current_ua_index + 1) % len(self.user_agents)
        self._update_session_headers()
