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
                            if name:
                                return name.strip()
                        elif isinstance(author, str):
                            return author.strip()
                        elif isinstance(author, list) and author:
                            # If it's a list, get the first author
                            first_author = author[0]
                            if isinstance(first_author, dict):
                                name = first_author.get('name', '')
                                if name:
                                    return name.strip()
                            elif isinstance(first_author, str):
                                return first_author.strip()
                    
                    # Check in @graph structure
                    if '@graph' in data:
                        for item in data['@graph']:
                            if isinstance(item, dict) and item.get('@type') in ['NewsArticle', 'Article']:
                                author = item.get('author')
                                if author:
                                    if isinstance(author, dict):
                                        name = author.get('name', '')
                                        if name:
                                            return name.strip()
                                    elif isinstance(author, str):
                                        return author.strip()
            except:
                continue
        
        # Method 2: Meta tags
        meta_selectors = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            'meta[name="byl"]',
            'meta[name="DC.creator"]'
        ]
        
        for selector in meta_selectors:
            meta = soup.select_one(selector)
            if meta and meta.get('content'):
                author = meta['content'].strip()
                # Clean up common prefixes
                author = re.sub(r'^(by|By|BY)\s+', '', author)
                if author:
                    return author
        
        # Method 3: Common byline patterns
        byline_selectors = [
            '[class*="byline"]',
            '[class*="author"]',
            '[class*="by-line"]',
            '[class*="writer"]',
            'span[itemprop="author"]',
            '[rel="author"]'
        ]
        
        for selector in byline_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text().strip()
                # Clean up the text
                text = re.sub(r'^(by|By|BY)\s+', '', text)
                text = re.sub(r'\s+', ' ', text)
                if text and len(text) < 100:  # Reasonable length for an author name
                    return text
        
        # Method 4: Site-specific patterns
        domain = urlparse(url).netloc.replace('www.', '')
        
        if 'bbc.com' in domain or 'bbc.co.uk' in domain:
            # BBC specific
            author_div = soup.find('div', {'class': 'ssrcss-68pt20-Text-TextContributorName'})
            if author_div:
                return author_div.get_text().strip()
        
        elif 'cnn.com' in domain:
            # CNN specific
            byline = soup.find('span', {'class': 'byline__name'})
            if byline:
                return byline.get_text().strip()
        
        elif 'nytimes.com' in domain:
            # NYTimes specific
            byline = soup.find('span', {'itemprop': 'name'})
            if byline:
                return byline.get_text().strip()
        
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
