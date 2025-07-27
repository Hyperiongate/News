"""
FILE: services/news_extractor.py
LOCATION: services/news_extractor.py
PURPOSE: Fixed extractor that gets authors from JSON-LD first
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
    """Extract article content from URLs with correct author detection"""
    
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
            logger.info(f"Starting extraction for: {url}")
            
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
            
            # CRITICAL: Extract author with JSON-LD priority
            author = self._extract_author(soup, response.text, domain)
            
            publish_date = self._extract_date(soup)
            
            logger.info(f"Extracted from {domain}: Title='{title[:50]}...', Author='{author}', Text length={len(text)}")
            
            return {
                'title': title or 'No title found',
                'text': text or 'No article text found',
                'author': author,
                'publish_date': publish_date,
                'url': url,
                'domain': domain
            }
            
        except Exception as e:
            logger.error(f"Extraction error for {url}: {str(e)}")
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
            '[class*="body-text"]',
            '[class*="article__content"]',
            '[class*="entry-content"]',
            '[class*="post-content"]',
            '[class*="RichTextStoryBody"]',
            'main',
            '[role="main"]',
            '[itemprop="articleBody"]'
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
        text = ' '.join([p.get_text().strip() for p in paragraphs[:30]])
        
        return text if text else 'No article text found'
    
    def _extract_author(self, soup, html_text, domain):
        """Extract author using multiple strategies - JSON-LD first!"""
        
        # List of organization names to filter out
        org_names = [
            'ABC News', 'CNN', 'BBC', 'Reuters', 'AP', 'Associated Press',
            'Fox News', 'NBC News', 'CBS News', 'MSNBC', 'NPR', 'PBS',
            'The New York Times', 'The Washington Post', 'The Guardian',
            'Bloomberg', 'CNBC', 'The Hill', 'Politico', 'Axios',
            'The Wall Street Journal', 'USA Today', 'The Independent',
            'AP News', 'The Associated Press', 'Staff', 'Newsroom',
            'Editorial Board', 'News Service', 'Wire Service'
        ]
        
        def is_organization_name(text):
            """Check if text is an organization name rather than a person"""
            if not text:
                return True
            text_lower = text.lower()
            for org in org_names:
                if org.lower() in text_lower:
                    return True
            if any(word in text_lower for word in ['news', 'staff', 'team', 'correspondent', 'newsroom', 'editorial', 'wire service', 'service']):
                return True
            return False
        
        def clean_author_text(text):
            """Clean up author text"""
            if not text:
                return None
            # Remove common prefixes
            text = re.sub(r'^(by|By|BY)\s+', '', text.strip())
            text = re.sub(r'\s+', ' ', text)
            # Remove organization suffixes
            for org in org_names:
                text = text.replace(f' and {org}', '').replace(f' / {org}', '').replace(f', {org}', '')
            return text.strip()
        
        # STRATEGY 1: Check JSON-LD structured data FIRST (highest priority)
        logger.info("Checking JSON-LD structured data for author")
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        
        for script in json_ld_scripts:
            try:
                # Parse JSON content
                json_text = script.string
                if json_text:
                    data = json.loads(json_text)
                    
                    # Check for author in the JSON structure
                    author = self._extract_author_from_json(data)
                    if author and not is_organization_name(author):
                        logger.info(f"Found author in JSON-LD: {author}")
                        return author
                        
            except json.JSONDecodeError:
                continue
            except Exception as e:
                logger.debug(f"Error parsing JSON-LD: {e}")
                continue
        
        # STRATEGY 2: Check for author in raw HTML metadata (for sites that don't use proper JSON-LD)
        # This is what found the AP News authors
        if '"author"' in html_text:
            # Look for patterns like "author" : "NAME,NAME"
            author_match = re.search(r'"author"\s*:\s*"([^"]+)"', html_text)
            if author_match:
                author_text = author_match.group(1)
                # Handle comma-separated authors
                if ',' in author_text and not any(org in author_text for org in org_names):
                    # This looks like multiple authors
                    authors = [a.strip() for a in author_text.split(',')]
                    # Join with "and" for readability
                    author = ' and '.join(authors)
                    if not is_organization_name(author):
                        logger.info(f"Found author in HTML metadata: {author}")
                        return author
        
        # STRATEGY 3: Meta tags
        logger.info("Checking meta tags")
        meta_selectors = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            'meta[name="byl"]',
            'meta[name="DC.creator"]',
            'meta[name="parsely-author"]',
            'meta[property="og:article:author"]',
            'meta[name="twitter:creator"]',
            'meta[itemprop="author"]',
            'meta[name="cXenseParse:author"]'
        ]
        
        for selector in meta_selectors:
            meta = soup.select_one(selector)
            if meta and meta.get('content'):
                author = clean_author_text(meta['content'])
                if author and not is_organization_name(author):
                    logger.info(f"Found author in meta tag: {author}")
                    return author
        
        # STRATEGY 4: Look for byline elements in specific areas
        logger.info("Looking for byline elements")
        
        # First check header/top of article for bylines
        header_selectors = [
            'header [class*="byline"]',
            'header [class*="author"]',
            '[class*="article-header"] [class*="byline"]',
            '[class*="article-header"] [class*="author"]',
            '.byline',
            '.author-name',
            '[itemprop="author"]',
            '[rel="author"]'
        ]
        
        for selector in header_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text().strip()
                if text and len(text) < 100:
                    author = clean_author_text(text)
                    if author and not is_organization_name(author):
                        logger.info(f"Found author in byline element: {author}")
                        return author
        
        # STRATEGY 5: Look for "By NAME" patterns ONLY in article header area
        # This prevents picking up names from the article body
        header = soup.find(['header', 'div'], class_=re.compile(r'(article-header|story-header|headline)', re.I))
        if header:
            header_text = header.get_text()
            by_pattern = r'[Bb]y\s+([A-Z][a-zA-Z]+(?:\s+[A-Z]\.?\s*)?[A-Z][a-zA-Z]+(?:\s+(?:and|&)\s+[A-Z][a-zA-Z]+(?:\s+[A-Z]\.?\s*)?[A-Z][a-zA-Z]+)*)'
            match = re.search(by_pattern, header_text)
            if match:
                author = clean_author_text(match.group(1))
                if author and not is_organization_name(author):
                    logger.info(f"Found author in header 'By' pattern: {author}")
                    return author
        
        logger.info("No author found after all strategies")
        return None
    
    def _extract_author_from_json(self, obj):
        """Recursively extract author from JSON-LD object"""
        if isinstance(obj, dict):
            # Direct author field
            if 'author' in obj:
                author_data = obj['author']
                if isinstance(author_data, str):
                    return author_data
                elif isinstance(author_data, dict) and 'name' in author_data:
                    return author_data['name']
                elif isinstance(author_data, list) and author_data:
                    # Multiple authors
                    authors = []
                    for a in author_data:
                        if isinstance(a, str):
                            authors.append(a)
                        elif isinstance(a, dict) and 'name' in a:
                            authors.append(a['name'])
                    if authors:
                        return ' and '.join(authors)
            
            # Check in @graph array
            if '@graph' in obj and isinstance(obj['@graph'], list):
                for item in obj['@graph']:
                    author = self._extract_author_from_json(item)
                    if author:
                        return author
            
            # Check other fields that might contain author
            for key, value in obj.items():
                if key not in ['@context', '@id', '@type']:
                    author = self._extract_author_from_json(value)
                    if author:
                        return author
                        
        elif isinstance(obj, list):
            for item in obj:
                author = self._extract_author_from_json(item)
                if author:
                    return author
        
        return None
    
    def _extract_date(self, soup):
        """Extract publish date"""
        # Try meta tags first
        date_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="publish_date"]',
            'meta[name="publication_date"]',
            'meta[property="og:published_time"]',
            'meta[property="article:published"]',
            'meta[name="pubdate"]',
            'meta[name="publishdate"]',
            'time[datetime]',
            'time[pubdate]'
        ]
        
        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    date_str = element.get('content', '')
                else:
                    date_str = element.get('datetime', '') or element.get('pubdate', '')
                
                if date_str:
                    try:
                        # Parse ISO format
                        return datetime.fromisoformat(date_str.replace('Z', '+00:00')).isoformat()
                    except:
                        return date_str
        
        return None
