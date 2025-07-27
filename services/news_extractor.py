"""
FILE: services/news_extractor.py
LOCATION: news/services/news_extractor.py
PURPOSE: Extract article content with better error handling and CNN support
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
        # Updated user agent to avoid blocking
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
            # Add timeout and better error handling
            response = self.session.get(url, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            # Check if we got a valid response
            if not response.content:
                logger.error(f"Empty response from {url}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract components
            title = self._extract_title(soup)
            text = self._extract_text(soup, url)  # Pass URL for site-specific handling
            author = self._extract_author(soup, url)
            publish_date = self._extract_date(soup)
            
            # Get domain
            domain = urlparse(url).netloc.replace('www.', '')
            
            # Validate we have minimum content
            if not title or not text or len(text) < 50:
                logger.error(f"Insufficient content extracted from {url}")
                # Try alternative extraction for problematic sites
                if not text or len(text) < 50:
                    text = self._extract_text_fallback(soup)
            
            return {
                'title': title or 'No title found',
                'text': text or 'No article text found',
                'author': author,
                'publish_date': publish_date,
                'url': url,
                'domain': domain
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout error for {url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {url}: {str(e)}")
            return None
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
                    title = element.get('content', '').strip()
                else:
                    title = element.get_text().strip()
                
                if title:
                    return title
        
        return 'No title found'
    
    def _extract_text(self, soup, url):
        """Extract main article text with site-specific handling"""
        # Remove script and style elements
        for script in soup(['script', 'style']):
            script.decompose()
        
        # CNN specific handling
        if 'cnn.com' in url:
            # CNN specific selectors
            cnn_selectors = [
                'div.zn-body__paragraph',
                'div.l-container div.zn-body__paragraph',
                'div[class*="paragraph"]',
                'div.article__content',
                'div.pg-rail-tall__body'
            ]
            
            for selector in cnn_selectors:
                paragraphs = soup.select(selector)
                if paragraphs:
                    text = ' '.join([p.get_text().strip() for p in paragraphs])
                    if len(text) > 100:
                        return text
        
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
        text = ' '.join([p.get_text().strip() for p in paragraphs[:30]])  # Increased from 20
        
        return text if text else 'No article text found'
    
    def _extract_text_fallback(self, soup):
        """Fallback text extraction for difficult sites"""
        # Try div tags with common content classes
        content_divs = soup.find_all('div', class_=re.compile(r'(content|article|story|body|text)', re.I))
        
        all_text = []
        for div in content_divs[:10]:  # Limit to avoid too much noise
            text = div.get_text(separator=' ', strip=True)
            if len(text) > 100:  # Only include substantial text blocks
                all_text.append(text)
        
        if all_text:
            return ' '.join(all_text)
        
        # Last resort: get all text from body
        body = soup.find('body')
        if body:
            text = body.get_text(separator=' ', strip=True)
            # Try to clean it up a bit
            lines = text.split('\n')
            cleaned_lines = [line.strip() for line in lines if len(line.strip()) > 50]
            return ' '.join(cleaned_lines[:20])
        
        return 'No article text found'
    
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
        
        # CNN specific
        if 'cnn.com' in domain:
            # CNN often has author in specific classes
            cnn_selectors = [
                '.metadata__byline__author',
                '.byline__name',
                '[class*="author-name"]',
                '[class*="byline__name"]'
            ]
            for selector in cnn_selectors:
                elem = soup.select_one(selector)
                if elem:
                    author = clean_author_text(elem.get_text())
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
                        return date_str
        
        return None
