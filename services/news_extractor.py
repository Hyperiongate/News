"""
FILE: services/news_extractor.py
LOCATION: news/services/news_extractor.py
PURPOSE: Article extraction without newspaper3k dependency
"""

import re
import json
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
from datetime import datetime

class NewsExtractor:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Author patterns
        self.author_patterns = [
            r'[Bb]y\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
            r'[Ww]ritten\s+by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
            r'[Aa]uthor:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
        ]
        
        # Site-specific selectors
        self.author_selectors = {
            'bbc.com': [
                ('span', {'class': 'ssrcss-68pt20-Text-TextContributorName'}),
                ('div', {'data-testid': 'byline-name'}),
                ('p', {'class': 'ssrcss-1rv0moy-Contributor'}),
            ],
            'cnn.com': [
                ('span', {'class': 'byline__name'}),
                ('span', {'class': 'metadata__byline__author'}),
            ],
            'nytimes.com': [
                ('span', {'class': 'byline-name'}),
                ('span', {'itemprop': 'name'}),
            ],
            'reuters.com': [
                ('span', {'data-testid': 'author-name'}),
                ('div', {'class': 'author-name'}),
            ],
            'theguardian.com': [
                ('span', {'itemprop': 'name'}),
                ('address', {'aria-label': re.compile('Written by')}),
            ],
        }

    def extract_article(self, url):
        """Extract article content and metadata"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            domain = urlparse(url).netloc
            
            # Extract components
            title = self._extract_title(soup)
            author = self._extract_author(soup, domain)
            text = self._extract_text(soup)
            publish_date = self._extract_date(soup)
            
            return {
                'success': True,
                'title': title,
                'author': author,
                'text': text,
                'publish_date': publish_date,
                'domain': domain,
                'url': url
            }
            
        except Exception as e:
            print(f"Extraction error: {e}")
            return {
                'success': False,
                'error': str(e),
                'url': url
            }
    
    def _extract_title(self, soup):
        """Extract article title"""
        # Try og:title first
        og_title = soup.find('meta', {'property': 'og:title'})
        if og_title and og_title.get('content'):
            return og_title.get('content').strip()
        
        # Try regular title tag
        if soup.title:
            return soup.title.string.strip()
        
        # Try h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        return "Unknown Title"
    
    def _extract_author(self, soup, domain):
        """Extract author with multiple strategies"""
        # Method 1: Site-specific selectors
        for site, selectors in self.author_selectors.items():
            if site in domain:
                for tag, attrs in selectors:
                    elem = soup.find(tag, attrs)
                    if elem:
                        author = self._clean_author(elem.get_text())
                        if author:
                            return author
        
        # Method 2: Meta tags
        meta_names = ['author', 'article:author', 'og:author', 'twitter:creator']
        for name in meta_names:
            meta = soup.find('meta', {'property': name}) or soup.find('meta', {'name': name})
            if meta and meta.get('content'):
                author = self._clean_author(meta.get('content'))
                if author:
                    return author
        
        # Method 3: JSON-LD
        json_ld = soup.find('script', {'type': 'application/ld+json'})
        if json_ld:
            try:
                data = json.loads(json_ld.string)
                if isinstance(data, dict) and 'author' in data:
                    if isinstance(data['author'], dict):
                        author = data['author'].get('name', '')
                    else:
                        author = str(data['author'])
                    author = self._clean_author(author)
                    if author:
                        return author
            except:
                pass
        
        # Method 4: Byline patterns
        for pattern in self.author_patterns:
            # Look in common byline locations
            for tag in ['p', 'span', 'div']:
                elements = soup.find_all(tag, string=re.compile(pattern, re.I))
                for elem in elements:
                    match = re.search(pattern, elem.get_text())
                    if match:
                        author = self._clean_author(match.group(1))
                        if author:
                            return author
        
        # Method 5: Schema.org
        author_elem = soup.find(attrs={'itemprop': 'author'})
        if author_elem:
            name_elem = author_elem.find(attrs={'itemprop': 'name'})
            if name_elem:
                author = self._clean_author(name_elem.get_text())
            else:
                author = self._clean_author(author_elem.get_text())
            if author:
                return author
        
        return None
    
    def _clean_author(self, text):
        """Clean author text"""
        if not text:
            return None
        
        # Remove common prefixes
        text = re.sub(r'^(by|written by|author:)\s*', '', text, flags=re.I)
        
        # Remove email/twitter handles
        text = re.sub(r'@\S+', '', text)
        text = re.sub(r'\S+@\S+', '', text)
        
        # Clean up
        text = ' '.join(text.split())
        
        # Validate
        if len(text) < 3 or len(text) > 100:
            return None
        
        # Must have letters
        if not re.search(r'[a-zA-Z]', text):
            return None
        
        # Exclude common non-names
        if text.lower() in ['staff', 'editor', 'admin', 'correspondent', 'reporter']:
            return None
        
        return text.strip()
    
    def _extract_text(self, soup):
        """Extract article text"""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer']):
            element.decompose()
        
        # Try to find article body
        article_body = soup.find('article') or soup.find('div', {'class': re.compile('article|content|story')})
        
        if article_body:
            # Get paragraphs
            paragraphs = article_body.find_all('p')
            text = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        else:
            # Fallback to all paragraphs
            paragraphs = soup.find_all('p')
            text = ' '.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 50])
        
        return text[:5000]  # Limit length
    
    def _extract_date(self, soup):
        """Extract publish date"""
        # Try meta tags
        date_metas = ['article:published_time', 'datePublished', 'publish_date']
        for name in date_metas:
            meta = soup.find('meta', {'property': name}) or soup.find('meta', {'name': name})
            if meta and meta.get('content'):
                try:
                    return datetime.fromisoformat(meta.get('content').replace('Z', '+00:00'))
                except:
                    pass
        
        # Try time tag
        time_tag = soup.find('time')
        if time_tag and time_tag.get('datetime'):
            try:
                return datetime.fromisoformat(time_tag.get('datetime').replace('Z', '+00:00'))
            except:
                pass
        
        return None
