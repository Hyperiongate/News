"""
FILE: services/news_extractor.py
LOCATION: services/news_extractor.py
PURPOSE: UNIVERSAL author extraction that works on ALL news sites
"""

import logging
import re
import json
from datetime import datetime
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class NewsExtractor:
    """Universal news extractor that finds authors ANYWHERE they might be hiding"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def extract_article(self, url):
        """Extract article content from URL"""
        try:
            logger.info(f"Starting UNIVERSAL extraction for: {url}")
            
            response = self.session.get(url, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            if not response.content:
                logger.error(f"Empty response from {url}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get domain
            domain = urlparse(url).netloc.replace('www.', '')
            
            # Extract components
            title = self._extract_title(soup)
            text = self._extract_text(soup, url)
            
            # UNIVERSAL AUTHOR EXTRACTION
            author = self._extract_author_universal(soup, response.text, domain, url)
            
            publish_date = self._extract_date(soup)
            
            logger.info(f"EXTRACTION COMPLETE: Title='{title[:50]}...', Author='{author}', Text length={len(text)}")
            
            return {
                'title': title or 'No title found',
                'text': text or 'No article text found',
                'author': author,
                'publish_date': publish_date,
                'url': url,
                'domain': domain
            }
            
        except Exception as e:
            logger.error(f"Extraction error for {url}: {str(e)}", exc_info=True)
            return None
    
    def _extract_title(self, soup):
        """Extract article title"""
        selectors = [
            'h1',
            'meta[property="og:title"]',
            'meta[name="twitter:title"]',
            'title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    title = element.get('content', '').strip()
                else:
                    title = element.get_text().strip()
                
                if title:
                    return title
        
        return 'No title found'
    
    def _extract_text(self, soup, url):
        """Extract main article text"""
        # Remove script and style elements
        for script in soup(['script', 'style']):
            script.decompose()
        
        # Try to find article body with common selectors
        article_selectors = [
            'article',
            '[class*="article-body"]',
            '[class*="story-body"]',
            '[class*="content-body"]',
            '[class*="RichTextStoryBody"]',
            'main',
            '.story-body__inner',
            '.article__body',
            '.entry-content',
            '.post-content'
        ]
        
        for selector in article_selectors:
            article = soup.select_one(selector)
            if article:
                paragraphs = article.find_all('p')
                if paragraphs:
                    text = ' '.join([p.get_text().strip() for p in paragraphs])
                    if len(text) > 100:
                        return text
        
        # Fallback: get all paragraphs
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text().strip() for p in paragraphs[:50]])
        
        return text if text else 'No article text found'
    
    def _extract_author_universal(self, soup, html_text, domain, url):
        """UNIVERSAL author extraction using EVERY possible method"""
        
        logger.info("=" * 80)
        logger.info("UNIVERSAL AUTHOR EXTRACTION - TRYING ALL METHODS")
        logger.info("=" * 80)
        
        found_authors = []
        
        # METHOD 1: JSON-LD Structured Data (HIGHEST PRIORITY)
        logger.info("\nMETHOD 1: JSON-LD Structured Data")
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        
        for script in json_ld_scripts:
            try:
                if script.string:
                    data = json.loads(script.string)
                    authors = self._extract_authors_from_json_deep(data)
                    if authors:
                        logger.info(f"✅ JSON-LD authors found: {authors}")
                        found_authors.extend(authors)
            except Exception as e:
                logger.debug(f"JSON-LD parse error: {e}")
        
        # METHOD 2: Meta Tags (ALL POSSIBLE VARIATIONS)
        logger.info("\nMETHOD 2: Meta Tags")
        meta_selectors = [
            ('meta[name="author"]', 'content'),
            ('meta[property="author"]', 'content'),
            ('meta[property="article:author"]', 'content'),
            ('meta[name="byl"]', 'content'),
            ('meta[name="DC.creator"]', 'content'),
            ('meta[name="DC.Creator"]', 'content'),
            ('meta[name="parsely-author"]', 'content'),
            ('meta[name="twitter:creator"]', 'content'),
            ('meta[property="og:article:author"]', 'content'),
            ('meta[name="sailthru.author"]', 'content'),
            ('meta[name="article.author"]', 'content'),
            ('meta[name="cXenseParse:author"]', 'content'),
            ('meta[itemprop="author"]', 'content'),
            ('meta[name="news_keywords"]', 'content'),  # Sometimes has author
            ('meta[property="article:author:name"]', 'content'),
        ]
        
        for selector, attr in meta_selectors:
            elements = soup.select(selector)
            for elem in elements:
                content = elem.get(attr, '').strip()
                if content and self._is_valid_author(content):
                    logger.info(f"✅ Meta tag {selector}: '{content}'")
                    found_authors.append(content)
        
        # METHOD 3: Byline Elements (COMPREHENSIVE)
        logger.info("\nMETHOD 3: Byline Elements")
        byline_selectors = [
            # Class-based selectors
            '.byline', '.by-line', '.byline-name', '.author-name',
            '.article-author', '.story-byline', '.content-author',
            '.post-author', '.entry-author', '.news-author',
            '.journalist', '.writer', '.reporter', '.contributor',
            '.by', '.written-by', '.article-byline', '.story-author',
            '.author-info', '.author-box', '.bio-byline',
            '.article__author', '.article-info__author',
            '[class*="byline"]', '[class*="author"]', '[class*="writer"]',
            '[class*="journalist"]', '[class*="reporter"]',
            
            # ID-based selectors
            '#byline', '#author', '#writer', '#journalist',
            '[id*="byline"]', '[id*="author"]',
            
            # Semantic HTML5
            'address', 'address.author',
            
            # Data attributes
            '[data-author]', '[data-byline]', '[data-writer]',
            
            # Rel attributes
            '[rel="author"]',
            
            # Itemprop
            '[itemprop="author"]', '[itemprop="creator"]',
            
            # Specific tag combinations
            'span.byline', 'div.byline', 'p.byline',
            'span.author', 'div.author', 'p.author',
            'span[class*="author"]', 'div[class*="author"]',
            'p[class*="author"]', 'a[class*="author"]',
            'h3[class*="author"]', 'h4[class*="author"]',
            'h5[class*="author"]', 'h6[class*="author"]',
            
            # Link-based
            'a[href*="/author/"]', 'a[href*="/authors/"]',
            'a[href*="/journalist/"]', 'a[href*="/writer/"]',
            'a[href*="/profile/"]', 'a[href*="/people/"]',
            'a[href*="/staff/"]', 'a[href*="/contributors/"]',
            'a[rel="author"]',
        ]
        
        for selector in byline_selectors:
            elements = soup.select(selector)
            for elem in elements[:5]:  # Check first 5 of each type
                text = elem.get_text().strip()
                
                # Also check data attributes
                if elem.get('data-author'):
                    text = elem.get('data-author')
                
                # Clean and validate
                text = self._clean_author_text(text)
                if text and self._is_valid_author(text):
                    logger.info(f"✅ Byline element {selector}: '{text}'")
                    found_authors.append(text)
        
        # METHOD 4: Text Pattern Matching (AGGRESSIVE)
        logger.info("\nMETHOD 4: Text Pattern Matching")
        
        # Pattern for "By Author Name" in various formats
        author_patterns = [
            # Standard byline patterns
            r'[Bb]y:?\s+([A-Z][a-zA-Z\'\-]+(?:\s+[A-Z][a-zA-Z\'\-]+){1,3})',
            r'[Ww]ritten\s+[Bb]y:?\s+([A-Z][a-zA-Z\'\-]+(?:\s+[A-Z][a-zA-Z\'\-]+){1,3})',
            r'[Rr]eported\s+[Bb]y:?\s+([A-Z][a-zA-Z\'\-]+(?:\s+[A-Z][a-zA-Z\'\-]+){1,3})',
            r'[Aa]uthor:?\s+([A-Z][a-zA-Z\'\-]+(?:\s+[A-Z][a-zA-Z\'\-]+){1,3})',
            r'[Jj]ournalist:?\s+([A-Z][a-zA-Z\'\-]+(?:\s+[A-Z][a-zA-Z\'\-]+){1,3})',
            r'[Cc]orrespondent:?\s+([A-Z][a-zA-Z\'\-]+(?:\s+[A-Z][a-zA-Z\'\-]+){1,3})',
            
            # With titles/credentials
            r'[Bb]y:?\s+(?:Dr\.|Prof\.|Mr\.|Ms\.|Mrs\.)?\s*([A-Z][a-zA-Z\'\-]+(?:\s+[A-Z][a-zA-Z\'\-]+){1,3})',
            
            # Multiple authors
            r'[Bb]y:?\s+([A-Z][a-zA-Z\'\-]+(?:\s+[A-Z][a-zA-Z\'\-]+){1,3})\s+(?:and|&)\s+([A-Z][a-zA-Z\'\-]+(?:\s+[A-Z][a-zA-Z\'\-]+){1,3})',
            
            # With email/twitter
            r'[Bb]y:?\s+([A-Z][a-zA-Z\'\-]+(?:\s+[A-Z][a-zA-Z\'\-]+){1,3})\s*[\(\[]?@',
            
            # In specific HTML contexts
            r'<(?:span|div|p)[^>]*>[Bb]y:?\s+([A-Z][a-zA-Z\'\-]+(?:\s+[A-Z][a-zA-Z\'\-]+){1,3})</(?:span|div|p)>',
        ]
        
        # Search in different text contexts
        search_texts = [
            html_text,  # Full HTML
            soup.get_text(),  # Extracted text
            str(soup.find('body')) if soup.find('body') else '',  # Body HTML
        ]
        
        for search_text in search_texts:
            if not search_text:
                continue
                
            for pattern in author_patterns:
                matches = re.findall(pattern, search_text[:50000])  # Search first 50k chars
                for match in matches:
                    if isinstance(match, tuple):
                        # Handle multiple authors
                        for author in match:
                            if author and self._is_valid_author(author):
                                logger.info(f"✅ Pattern match: '{author}'")
                                found_authors.append(author)
                    else:
                        if match and self._is_valid_author(match):
                            logger.info(f"✅ Pattern match: '{match}'")
                            found_authors.append(match)
        
        # METHOD 5: Schema.org Microdata
        logger.info("\nMETHOD 5: Schema.org Microdata")
        
        # Look for itemscope with author
        author_scopes = soup.find_all(attrs={'itemtype': re.compile('schema.org/Person', re.I)})
        for scope in author_scopes:
            name_elem = scope.find(attrs={'itemprop': 'name'})
            if name_elem:
                name = name_elem.get_text().strip()
                if self._is_valid_author(name):
                    logger.info(f"✅ Schema.org Person: '{name}'")
                    found_authors.append(name)
        
        # METHOD 6: RDFa
        logger.info("\nMETHOD 6: RDFa")
        rdfa_authors = soup.find_all(attrs={'property': re.compile('author|creator', re.I)})
        for elem in rdfa_authors:
            text = elem.get_text().strip()
            if self._is_valid_author(text):
                logger.info(f"✅ RDFa: '{text}'")
                found_authors.append(text)
        
        # METHOD 7: Special Cases - Hidden or JavaScript-rendered content
        logger.info("\nMETHOD 7: Hidden/JS Content")
        
        # Check for hidden author data in data attributes
        all_elements = soup.find_all(attrs={'data-author': True})
        for elem in all_elements:
            author = elem.get('data-author', '').strip()
            if self._is_valid_author(author):
                logger.info(f"✅ Data attribute: '{author}'")
                found_authors.append(author)
        
        # Check comments for author info (some sites hide it there)
        for comment in soup.find_all(string=lambda text: isinstance(text, str) and 'author' in text.lower()):
            if 'author:' in str(comment).lower():
                match = re.search(r'author:\s*([A-Z][a-zA-Z\s\'\-]+)', str(comment), re.I)
                if match and self._is_valid_author(match.group(1)):
                    logger.info(f"✅ HTML comment: '{match.group(1)}'")
                    found_authors.append(match.group(1))
        
        # METHOD 8: Article vicinity search
        logger.info("\nMETHOD 8: Article Vicinity Search")
        
        # Find the main article element
        article = soup.find('article') or soup.find(class_=re.compile('article|story|content'))
        if article:
            # Look for author-like text near the beginning of the article
            first_elements = article.find_all(['p', 'div', 'span'])[:20]
            for elem in first_elements:
                text = elem.get_text().strip()
                if len(text) < 100:  # Short text more likely to be byline
                    # Check if it looks like an author
                    if re.match(r'^[A-Z][a-zA-Z\'\-]+(?:\s+[A-Z][a-zA-Z\'\-]+){1,3}$', text):
                        if self._is_valid_author(text):
                            logger.info(f"✅ Article vicinity: '{text}'")
                            found_authors.append(text)
        
        # FINAL STEP: Deduplicate and select best author
        logger.info("\n" + "=" * 80)
        logger.info("AUTHOR EXTRACTION COMPLETE")
        logger.info(f"Total potential authors found: {len(found_authors)}")
        
        if found_authors:
            # Deduplicate and clean
            unique_authors = []
            seen = set()
            
            for author in found_authors:
                clean = self._normalize_author(author)
                if clean and clean.lower() not in seen:
                    seen.add(clean.lower())
                    unique_authors.append(clean)
            
            logger.info(f"Unique authors: {unique_authors}")
            
            # Return the first valid author (usually the most reliable)
            if unique_authors:
                selected = unique_authors[0]
                # Handle multiple authors
                if len(unique_authors) > 1 and unique_authors[1] != selected:
                    # Check if second author is co-author
                    if len(unique_authors[1].split()) <= 3:  # Likely a name
                        selected = f"{selected} and {unique_authors[1]}"
                
                logger.info(f"🎯 SELECTED AUTHOR: {selected}")
                return selected
        
        logger.info("❌ NO AUTHOR FOUND")
        logger.info("=" * 80)
        
        return None
    
    def _extract_authors_from_json_deep(self, obj, authors=None):
        """Deep recursive extraction of authors from JSON-LD"""
        if authors is None:
            authors = []
        
        if isinstance(obj, dict):
            # Direct author fields
            author_keys = ['author', 'authors', 'creator', 'creators', 'contributor', 'contributors']
            
            for key in author_keys:
                if key in obj:
                    author_data = obj[key]
                    
                    # String author
                    if isinstance(author_data, str) and self._is_valid_author(author_data):
                        authors.append(author_data)
                    
                    # Object with name
                    elif isinstance(author_data, dict):
                        name = author_data.get('name') or author_data.get('@name')
                        if name and self._is_valid_author(name):
                            authors.append(name)
                    
                    # List of authors
                    elif isinstance(author_data, list):
                        for item in author_data:
                            if isinstance(item, str) and self._is_valid_author(item):
                                authors.append(item)
                            elif isinstance(item, dict):
                                name = item.get('name') or item.get('@name')
                                if name and self._is_valid_author(name):
                                    authors.append(name)
            
            # Recurse through all values
            for value in obj.values():
                self._extract_authors_from_json_deep(value, authors)
        
        elif isinstance(obj, list):
            for item in obj:
                self._extract_authors_from_json_deep(item, authors)
        
        return authors
    
    def _clean_author_text(self, text):
        """Clean author text of common prefixes and suffixes"""
        if not text:
            return ''
        
        # Remove common prefixes
        prefixes = [
            r'^[Bb]y\s+', r'^[Ww]ritten\s+[Bb]y\s+', r'^[Rr]eported\s+[Bb]y\s+',
            r'^[Aa]uthor:\s+', r'^[Jj]ournalist:\s+', r'^[Cc]orrespondent:\s+',
            r'^[Ff]rom\s+', r'^[Pp]osted\s+[Bb]y\s+', r'^[Cc]ontributed\s+[Bb]y\s+',
            r'^@\s*',  # Twitter handles
        ]
        
        for prefix in prefixes:
            text = re.sub(prefix, '', text, count=1)
        
        # Remove common suffixes
        suffixes = [
            r'\s*\|.*$',  # Pipe and everything after
            r'\s*,\s*[A-Z]{2,}.*$',  # Comma and location/outlet
            r'\s*[\(\[].*[\)\]].*$',  # Parentheses/brackets content
            r'\s*<.*>.*$',  # HTML tags
            r'\s*@.*$',  # Email/twitter
            r'\s+Reporter$', r'\s+Writer$', r'\s+Correspondent$',
            r'\s+Staff$', r'\s+Editor$', r'\s+Contributor$',
        ]
        
        for suffix in suffixes:
            text = re.sub(suffix, '', text)
        
        # Clean whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def _is_valid_author(self, text):
        """Check if text is a valid author name"""
        if not text or len(text) < 3 or len(text) > 100:
            return False
        
        # Exclude common non-author strings
        exclude_patterns = [
            'staff', 'writer', 'editor', 'team', 'news', 'service', 'wire',
            'correspondent', 'reporter', 'journalist', 'contributor',
            'associated press', 'reuters', 'bloomberg', 'admin', 'administrator',
            'published', 'updated', 'posted', 'share', 'follow', 'email',
            'facebook', 'twitter', 'linkedin', 'subscribe', 'newsletter',
            'http', 'www', '.com', 'click', 'read more', 'continue',
            'advertisement', 'sponsored', 'promotion'
        ]
        
        text_lower = text.lower()
        
        # Check exclusions
        for pattern in exclude_patterns:
            if pattern in text_lower:
                return False
        
        # Must have at least one uppercase letter (proper name)
        if not any(c.isupper() for c in text):
            return False
        
        # Should look like a name (at least one space or dash for full name)
        # But also allow single word names (like "Cher" or international names)
        words = text.split()
        if len(words) > 5:  # Too many words for a name
            return False
        
        # Check if it contains mostly alphabetic characters
        alpha_chars = sum(c.isalpha() or c in " '-." for c in text)
        if alpha_chars < len(text) * 0.8:
            return False
        
        # Looks like a valid name
        return True
    
    def _normalize_author(self, author):
        """Normalize author name for consistency"""
        if not author:
            return ''
        
        # Clean the text first
        author = self._clean_author_text(author)
        
        # Fix common issues
        author = re.sub(r'\s+', ' ', author)  # Multiple spaces
        author = re.sub(r'^\W+|\W+$', '', author)  # Leading/trailing non-word chars
        
        # Title case for consistency (but preserve McNamara, O'Brien, etc.)
        words = author.split()
        normalized_words = []
        
        for word in words:
            if word.isupper() and len(word) > 1:
                # All caps - convert to title case
                word = word.capitalize()
            elif "'" in word or word.startswith('Mc') or word.startswith('Mac'):
                # Preserve special capitalization
                pass
            else:
                # Standard title case
                word = word.capitalize()
            
            normalized_words.append(word)
        
        return ' '.join(normalized_words)
    
    def _extract_date(self, soup):
        """Extract publish date"""
        date_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="publish_date"]',
            'meta[property="datePublished"]',
            'meta[name="publication_date"]',
            'meta[name="DC.date.issued"]',
            'meta[name="date"]',
            'time[datetime]',
            'time[pubdate]',
            '[itemprop="datePublished"]',
            '[property="datePublished"]',
            '.publish-date',
            '.post-date',
            '.article-date',
            '.date',
            'span.date',
            'div.date',
            'p.date'
        ]
        
        for selector in date_selectors:
            elements = soup.select(selector)
            for element in elements:
                date_str = None
                
                if element.name == 'meta':
                    date_str = element.get('content', '')
                elif element.name == 'time':
                    date_str = element.get('datetime', '') or element.get_text()
                else:
                    date_str = element.get('datetime', '') or element.get_text()
                
                if date_str:
                    # Try to parse the date
                    try:
                        # Handle ISO format
                        if 'T' in date_str:
                            return datetime.fromisoformat(date_str.replace('Z', '+00:00')).isoformat()
                        else:
                            # Try common formats
                            for fmt in ['%Y-%m-%d', '%B %d, %Y', '%d %B %Y', '%Y/%m/%d']:
                                try:
                                    return datetime.strptime(date_str.strip(), fmt).isoformat()
                                except:
                                    continue
                            
                            # If all else fails, return as-is if it looks like a date
                            if any(char.isdigit() for char in date_str):
                                return date_str
                    except:
                        if any(char.isdigit() for char in date_str):
                            return date_str
        
        return None
