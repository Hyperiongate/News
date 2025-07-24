"""
FILE: services/news_extractor.py
LOCATION: news/services/news_extractor.py
PURPOSE: Extract article content with fixed author formatting
"""

import logging
import re
from datetime import datetime
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class NewsExtractor:
    """Extract article content from URLs"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def extract_article(self, url):
        """Extract article content from URL"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract components
            title = self._extract_title(soup)
            text = self._extract_text(soup)
            author = self._extract_author(soup, url)
            publish_date = self._extract_date(soup)
            
            # Get domain
            domain = urlparse(url).netloc.replace('www.', '')
            
            return {
                'title': title,
                'text': text,
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
        # Try common title selectors
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
                    return element.get('content', '').strip()
                else:
                    return element.get_text().strip()
        
        return 'No title found'
    
    def _extract_text(self, soup):
        """Extract main article text"""
        # Remove script and style elements
        for script in soup(['script', 'style']):
            script.decompose()
        
        # Try to find article body
        article_selectors = [
            'article',
            '[class*="article-body"]',
            '[class*="story-body"]',
            '[class*="content-body"]',
            'main',
            '[role="main"]'
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
        text = ' '.join([p.get_text().strip() for p in paragraphs[:20]])
        
        return text if text else 'No article text found'
    
    def _extract_author(self, soup, url):
        """Extract author with proper formatting"""
        
        # List of organization names to filter out
        org_names = [
            'ABC News', 'CNN', 'BBC', 'Reuters', 'AP', 'Associated Press',
            'Fox News', 'NBC News', 'CBS News', 'MSNBC', 'NPR', 'PBS',
            'The New York Times', 'The Washington Post', 'The Guardian',
            'Bloomberg', 'CNBC', 'The Hill', 'Politico', 'Axios',
            'The Wall Street Journal', 'USA Today', 'The Independent'
        ]
        
        def is_organization_name(text):
            """Check if text is an organization name rather than a person"""
            if not text:
                return True
            # Check against known orgs
            for org in org_names:
                if org.lower() in text.lower():
                    return True
            # Check for common organization patterns
            if any(word in text.lower() for word in ['news', 'staff', 'team', 'correspondent', 'newsroom', 'editorial']):
                return True
            # Check if it looks like a person name (First Last)
            parts = text.strip().split()
            if len(parts) >= 2 and len(parts) <= 4:
                # Likely a person's name
                return False
            return True
        
        def clean_author_text(text):
            """Clean up author text"""
            if not text:
                return None
            # Remove common prefixes
            text = re.sub(r'^(by|By|BY)\s+', '', text.strip())
            text = re.sub(r'\s+', ' ', text)
            # Remove "and ABC News" type suffixes
            text = re.sub(r'\s+(and|for)\s+.*(News|Staff|Team).*$', '', text, flags=re.IGNORECASE)
            return text.strip()
        
        # Method 1: JSON-LD structured data
        json_ld = soup.find_all('script', type='application/ld+json')
        for script in json_ld:
            try:
                import json
                data = json.loads(script.string)
                
                # Handle different JSON-LD formats
                if isinstance(data, dict):
                    # Check for author in main object
                    author = data.get('author')
                    if author:
                        # Handle different author formats
                        if isinstance(author, dict):
                            name = author.get('name', '')
                            name = clean_author_text(name)
                            if name and not is_organization_name(name):
                                return name
                        elif isinstance(author, str):
                            name = clean_author_text(author)
                            if name and not is_organization_name(name):
                                return name
                        elif isinstance(author, list) and author:
                            # If it's a list, get the first valid author
                            for auth in author:
                                if isinstance(auth, dict):
                                    name = auth.get('name', '')
                                    name = clean_author_text(name)
                                    if name and not is_organization_name(name):
                                        return name
                                elif isinstance(auth, str):
                                    name = clean_author_text(auth)
                                    if name and not is_organization_name(name):
                                        return name
                    
                    # Check in @graph structure
                    if '@graph' in data:
                        for item in data['@graph']:
                            if isinstance(item, dict) and item.get('@type') in ['NewsArticle', 'Article']:
                                author = item.get('author')
                                if author:
                                    if isinstance(author, dict):
                                        name = author.get('name', '')
                                        name = clean_author_text(name)
                                        if name and not is_organization_name(name):
                                            return name
                                    elif isinstance(author, str):
                                        name = clean_author_text(author)
                                        if name and not is_organization_name(name):
                                            return name
            except:
                continue
        
        # Method 2: Meta tags
        meta_selectors = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            'meta[name="byl"]',
            'meta[name="DC.creator"]',
            'meta[name="parsely-author"]'
        ]
        
        for selector in meta_selectors:
            meta = soup.select_one(selector)
            if meta and meta.get('content'):
                author = clean_author_text(meta['content'])
                if author and not is_organization_name(author):
                    return author
        
        # Method 3: Common byline patterns with better filtering
        byline_selectors = [
            '[class*="byline"]:not([class*="date"])',
            '[class*="author"]:not([class*="bio"])',
            '[class*="by-line"]',
            '[class*="writer"]',
            'span[itemprop="author"]',
            '[rel="author"]',
            '.byline__name',  # CNN
            '.authors__name',  # Various sites
            '.contributor__name'  # Various sites
        ]
        
        for selector in byline_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text().strip()
                
                # Skip if it's too long (likely not just a name)
                if len(text) > 100:
                    continue
                    
                # Clean the text
                text = clean_author_text(text)
                
                # Skip if it's an organization
                if text and not is_organization_name(text):
                    return text
        
        # Method 4: Look for "By [Name]" pattern in the article
        for p in soup.find_all(['p', 'div', 'span']):
            text = p.get_text().strip()
            # Look for "By Name" pattern at the start of a line
            match = re.match(r'^(?:by|By|BY)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', text)
            if match:
                author = match.group(1)
                if not is_organization_name(author):
                    return author
        
        # Method 5: Site-specific patterns
        domain = urlparse(url).netloc.replace('www.', '')
        
        if 'abcnews.go.com' in domain:
            # ABC News specific - look for author in article body
            # Try to find author near the dateline
            for elem in soup.find_all(['div', 'p', 'span']):
                text = elem.get_text().strip()
                # ABC often has "By FIRSTNAME LASTNAME" in the article
                if text.startswith(('By ', 'BY ')):
                    author = clean_author_text(text)
                    if author and not is_organization_name(author) and len(author.split()) >= 2:
                        return author
        
        elif 'bbc.com' in domain or 'bbc.co.uk' in domain:
            # BBC specific
            author_div = soup.find('div', {'class': 'ssrcss-68pt20-Text-TextContributorName'})
            if author_div:
                author = clean_author_text(author_div.get_text())
                if author and not is_organization_name(author):
                    return author
        
        elif 'cnn.com' in domain:
            # CNN specific
            byline = soup.find('span', {'class': 'byline__name'})
            if byline:
                author = clean_author_text(byline.get_text())
                if author and not is_organization_name(author):
                    return author
        
        elif 'nytimes.com' in domain:
            # NYTimes specific
            byline = soup.find('span', {'itemprop': 'name'})
            if byline:
                author = clean_author_text(byline.get_text())
                if author and not is_organization_name(author):
                    return author
        
        # If no valid author found, return None instead of organization name
        return None
    
    def _extract_date(self, soup):
        """Extract publish date"""
        # Try meta tags first
        date_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="publish_date"]',
            'meta[name="publication_date"]',
            'meta[property="og:published_time"]',
            'time[datetime]'
        ]
        
        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    date_str = element.get('content', '')
                else:
                    date_str = element.get('datetime', '')
                
                if date_str:
                    try:
                        # Parse ISO format
                        return datetime.fromisoformat(date_str.replace('Z', '+00:00')).isoformat()
                    except:
                        pass
        
        return None
