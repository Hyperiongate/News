"""
FILE: services/news_extractor.py
LOCATION: news/services/news_extractor.py
PURPOSE: Enhanced article extraction with improved author detection
"""

import re
from newspaper import Article
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse

class NewsExtractor:
    def __init__(self):
        # Common author patterns and meta tags
        self.author_meta_tags = [
            'author',
            'article:author',
            'og:author',
            'twitter:creator',
            'byl',
            'dc.creator',
            'dcterms.creator',
            'sailthru.author',
            'parsely-author',
            'article.author',
            'cXenseParse:author'
        ]
        
        # Site-specific selectors for major news sites
        self.site_selectors = {
            'bbc.com': [
                {'tag': 'span', 'class': 'author-name'},
                {'tag': 'span', 'attrs': {'data-testid': 'byline-name'}},
                {'tag': 'p', 'class': 'ssrcss-1rv0moy-Contributor'},
                {'tag': 'div', 'class': 'ssrcss-68pt20-Text-TextContributorName'},
                {'tag': 'span', 'class': 'qa-contributor-name'},
            ],
            'nytimes.com': [
                {'tag': 'span', 'class': 'byline-name'},
                {'tag': 'span', 'attrs': {'itemprop': 'name'}},
                {'tag': 'p', 'class': 'css-1siyg7m'},
                {'tag': 'span', 'class': 'css-1baulvz'},
            ],
            'cnn.com': [
                {'tag': 'span', 'class': 'byline__name'},
                {'tag': 'span', 'class': 'metadata__byline__author'},
                {'tag': 'div', 'class': 'byline__names'},
            ],
            'reuters.com': [
                {'tag': 'span', 'class': 'author-name'},
                {'tag': 'div', 'class': 'author-name'},
                {'tag': 'span', 'attrs': {'data-testid': 'author-name'}},
            ],
            'theguardian.com': [
                {'tag': 'span', 'attrs': {'itemprop': 'name'}},
                {'tag': 'address', 'attrs': {'aria-label': re.compile('Written by')}},
                {'tag': 'p', 'class': 'byline'},
            ],
            'washingtonpost.com': [
                {'tag': 'span', 'class': 'author-name'},
                {'tag': 'a', 'attrs': {'rel': 'author'}},
                {'tag': 'span', 'attrs': {'itemprop': 'name'}},
            ],
            'foxnews.com': [
                {'tag': 'div', 'class': 'author-byline'},
                {'tag': 'span', 'class': 'author'},
            ],
            'apnews.com': [
                {'tag': 'span', 'class': 'Component-bylines'},
                {'tag': 'div', 'class': 'CardHeadline-byline'},
            ],
        }

    def extract_article(self, url):
        """Extract article with enhanced author detection"""
        try:
            # First try with newspaper3k
            article = Article(url)
            article.download()
            article.parse()
            
            # Get basic info
            result = {
                'title': article.title,
                'text': article.text,
                'author': article.authors,  # This is often empty or wrong
                'publish_date': article.publish_date,
                'domain': urlparse(url).netloc,
                'url': url
            }
            
            # Enhanced author extraction
            enhanced_author = self._extract_author_enhanced(url, article.html)
            if enhanced_author:
                result['author'] = enhanced_author
            
            return result
            
        except Exception as e:
            print(f"Error extracting article: {e}")
            # Fallback to BeautifulSoup only
            return self._extract_with_beautifulsoup(url)
    
    def _extract_author_enhanced(self, url, html_content):
        """Enhanced author extraction using multiple methods"""
        soup = BeautifulSoup(html_content, 'html.parser')
        domain = urlparse(url).netloc
        
        # Method 1: Try site-specific selectors
        for site, selectors in self.site_selectors.items():
            if site in domain:
                for selector in selectors:
                    elements = soup.find_all(**selector)
                    for elem in elements:
                        author = self._clean_author_name(elem.get_text())
                        if author and self._is_valid_author(author):
                            return author
        
        # Method 2: Try meta tags
        for tag_name in self.author_meta_tags:
            # Try property attribute
            meta = soup.find('meta', {'property': tag_name})
            if not meta:
                # Try name attribute
                meta = soup.find('meta', {'name': tag_name})
            
            if meta and meta.get('content'):
                author = self._clean_author_name(meta.get('content'))
                if author and self._is_valid_author(author):
                    return author
        
        # Method 3: Try JSON-LD structured data
        json_ld_author = self._extract_from_json_ld(soup)
        if json_ld_author:
            return json_ld_author
        
        # Method 4: Try common patterns in text
        patterns = [
            r'[Bb]y\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            r'[Ww]ritten\s+by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            r'[Aa]uthor:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            r'[Rr]eporter:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        ]
        
        # Look for byline patterns
        for pattern in patterns:
            # Search in specific areas first
            for tag in ['p', 'span', 'div', 'address']:
                elements = soup.find_all(tag, string=re.compile(pattern))
                for elem in elements:
                    match = re.search(pattern, elem.get_text())
                    if match:
                        author = self._clean_author_name(match.group(1))
                        if author and self._is_valid_author(author):
                            return author
        
        # Method 5: Look for elements with itemprop="author"
        author_elem = soup.find(attrs={'itemprop': 'author'})
        if author_elem:
            # Check if it's a Person schema
            name_elem = author_elem.find(attrs={'itemprop': 'name'})
            if name_elem:
                author = self._clean_author_name(name_elem.get_text())
                if author and self._is_valid_author(author):
                    return author
            else:
                author = self._clean_author_name(author_elem.get_text())
                if author and self._is_valid_author(author):
                    return author
        
        return None
    
    def _extract_from_json_ld(self, soup):
        """Extract author from JSON-LD structured data"""
        scripts = soup.find_all('script', {'type': 'application/ld+json'})
        for script in scripts:
            try:
                import json
                data = json.loads(script.string)
                
                # Handle single object or array
                if isinstance(data, list):
                    data = data[0] if data else {}
                
                # Look for author in different formats
                if 'author' in data:
                    author_data = data['author']
                    if isinstance(author_data, dict):
                        author = author_data.get('name', '')
                    elif isinstance(author_data, str):
                        author = author_data
                    else:
                        author = ''
                    
                    author = self._clean_author_name(author)
                    if author and self._is_valid_author(author):
                        return author
                
                # Sometimes it's in @graph
                if '@graph' in data:
                    for item in data['@graph']:
                        if item.get('@type') in ['NewsArticle', 'Article']:
                            return self._extract_from_json_ld_item(item)
                            
            except:
                continue
        return None
    
    def _extract_from_json_ld_item(self, item):
        """Helper to extract from JSON-LD item"""
        if 'author' in item:
            author_data = item['author']
            if isinstance(author_data, dict):
                author = author_data.get('name', '')
            elif isinstance(author_data, str):
                author = author_data
            else:
                author = ''
            
            author = self._clean_author_name(author)
            if author and self._is_valid_author(author):
                return author
        return None
    
    def _clean_author_name(self, author):
        """Clean up author name"""
        if not author:
            return None
        
        # Remove "By" prefix
        author = re.sub(r'^[Bb]y\s+', '', author)
        
        # Remove common suffixes
        author = re.sub(r'\s*(,\s*.+|and\s+.+|\|.+|-.+|for\s+.+|at\s+.+)$', '', author)
        
        # Remove email addresses
        author = re.sub(r'\S+@\S+', '', author)
        
        # Remove extra whitespace
        author = ' '.join(author.split())
        
        return author.strip()
    
    def _is_valid_author(self, author):
        """Check if the extracted author string is valid"""
        if not author or len(author) < 3:
            return False
        
        # Exclude common false positives
        invalid_patterns = [
            r'^(staff|editor|admin|correspondent|reporter|news|team|desk)$',
            r'^\d+$',  # Just numbers
            r'^[A-Z]+$',  # All caps (probably abbreviation)
            r'[<>]',  # HTML tags
            r'^\W+$',  # Only special characters
        ]
        
        for pattern in invalid_patterns:
            if re.search(pattern, author, re.IGNORECASE):
                return False
        
        # Should have at least one letter
        if not re.search(r'[a-zA-Z]', author):
            return False
        
        # Reasonable length
        if len(author) > 100:
            return False
        
        return True
    
    def _extract_with_beautifulsoup(self, url):
        """Fallback extraction method using BeautifulSoup only"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = None
            if soup.title:
                title = soup.title.string
            else:
                # Try meta og:title
                og_title = soup.find('meta', {'property': 'og:title'})
                if og_title:
                    title = og_title.get('content')
            
            # Extract text
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Try enhanced author extraction
            author = self._extract_author_enhanced(url, str(soup))
            
            return {
                'title': title,
                'text': text[:5000],  # Limit text length
                'author': author,
                'domain': urlparse(url).netloc,
                'url': url
            }
            
        except Exception as e:
            print(f"BeautifulSoup extraction failed: {e}")
            return None
