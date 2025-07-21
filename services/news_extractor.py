"""
FILE: services/news_extractor.py
LOCATION: news/services/news_extractor.py
PURPOSE: Extract article content from news websites
DEPENDENCIES: requests, BeautifulSoup4
SERVICE: News extractor - Handles content extraction from URLs
"""

import logging
import re
import json
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class NewsExtractor:
    """Extract article content from news websites"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache'
        })
        
        # Site-specific selectors
        self.site_selectors = {
            'reuters.com': 'div[data-testid="article-body"]',
            'apnews.com': 'div.RichTextStoryBody',
            'bbc.com': 'main[role="main"]',
            'bbc.co.uk': 'main[role="main"]',
            'theguardian.com': 'div.article-body-commercial-selector',
            'cnn.com': 'div.article__content',
            'foxnews.com': 'div.article-body',
            'usatoday.com': 'div.gnt_ar_b',
            'npr.org': 'div#storytext',
            'politico.com': 'div.story-text',
            'thehill.com': 'div.article__text',
            'nbcnews.com': 'div.article-body',
            'cbsnews.com': 'section.content__body',
            'abcnews.go.com': 'div.Article__Content',
            'axios.com': 'div[class*="gtm-story-text"]'
        }
    
    def extract_from_url(self, url):
        """Extract article content from URL"""
        try:
            domain = urlparse(url).netloc.replace('www.', '')
            logger.info(f"Extracting from {domain}")
            
            response = self.session.get(url, timeout=10, allow_redirects=True)
            
            if response.status_code != 200:
                logger.error(f"HTTP {response.status_code} for {url}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try multiple extraction methods
            result = (
                self._extract_json_ld(soup, url, domain) or
                self._extract_nextjs_data(response.text, url, domain) or
                self._extract_site_specific(soup, url, domain) or
                self._extract_generic(soup, url, domain)
            )
            
            if result:
                logger.info(f"Successfully extracted from {domain} using {result.get('extraction_method', 'unknown')}")
            else:
                logger.warning(f"All extraction methods failed for {domain}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting from {url}: {str(e)}")
            return None
    
    def _extract_json_ld(self, soup, url, domain):
        """Extract from JSON-LD structured data"""
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                article_data = None
                
                if isinstance(data, dict) and data.get('@type') in ['NewsArticle', 'Article', 'BlogPosting']:
                    article_data = data
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get('@type') in ['NewsArticle', 'Article']:
                            article_data = item
                            break
                
                if article_data:
                    title = article_data.get('headline', '')
                    text = article_data.get('articleBody', '') or article_data.get('text', '')
                    
                    author = None
                    if 'author' in article_data:
                        if isinstance(article_data['author'], dict):
                            author = article_data['author'].get('name')
                        else:
                            author = str(article_data['author'])
                    
                    if text and len(text) > 500:
                        return {
                            'url': url,
                            'domain': domain,
                            'title': title or 'Article',
                            'text': text[:5000],
                            'author': author or f'{domain} Staff',
                            'publish_date': article_data.get('datePublished'),
                            'extraction_method': 'json_ld'
                        }
            except:
                continue
        return None
    
    def _extract_nextjs_data(self, html, url, domain):
        """Extract from Next.js __NEXT_DATA__"""
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
        if not match:
            return None
        
        try:
            data = json.loads(match.group(1))
            
            # Common paths in Next.js apps
            paths = [
                ['props', 'pageProps', 'article'],
                ['props', 'pageProps', 'story'],
                ['props', 'pageProps', 'post'],
                ['props', 'pageProps', 'data']
            ]
            
            for path in paths:
                current = data
                for key in path:
                    if isinstance(current, dict) and key in current:
                        current = current[key]
                    else:
                        break
                else:
                    # Found article data
                    text = self._extract_text_from_object(current)
                    if text and len(text) > 500:
                        return {
                            'url': url,
                            'domain': domain,
                            'title': self._find_in_dict(current, ['title', 'headline']) or 'Article',
                            'text': text[:5000],
                            'author': self._find_in_dict(current, ['author', 'byline']) or f'{domain} Staff',
                            'publish_date': self._find_in_dict(current, ['publishedAt', 'datePublished']),
                            'extraction_method': 'nextjs'
                        }
        except:
            pass
        return None
    
    def _extract_site_specific(self, soup, url, domain):
        """Extract using site-specific selectors"""
        # Clean up soup
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        if domain in self.site_selectors:
            selector = self.site_selectors[domain]
            content = soup.select_one(selector)
            
            if content:
                paragraphs = content.find_all(['p', 'h2', 'h3'])
                text = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                
                if text and len(text) > 500:
                    title = self._extract_title(soup)
                    author = self._extract_author(soup)
                    
                    return {
                        'url': url,
                        'domain': domain,
                        'title': title or f'{domain} Article',
                        'text': text[:5000],
                        'author': author or f'{domain} Staff',
                        'publish_date': self._extract_date(soup),
                        'extraction_method': 'site_specific'
                    }
        return None
    
    def _extract_generic(self, soup, url, domain):
        """Generic extraction method"""
        # Find the largest text block
        all_containers = soup.find_all(['div', 'section', 'article', 'main'])
        best_container = None
        max_text_length = 0
        
        for container in all_containers:
            paragraphs = container.find_all('p')
            text_length = sum(len(p.get_text().strip()) for p in paragraphs if len(p.get_text().strip()) > 50)
            
            if text_length > max_text_length:
                max_text_length = text_length
                best_container = container
        
        if best_container and max_text_length > 500:
            title = self._extract_title(soup)
            author = self._extract_author(soup)
            
            text_elements = best_container.find_all(['p', 'h2', 'h3', 'blockquote'])
            article_parts = []
            
            for elem in text_elements:
                text = elem.get_text().strip()
                if text and len(text) > 30 and not self._is_boilerplate(text):
                    article_parts.append(text)
            
            article_text = ' '.join(article_parts)
            
            if len(article_text) > 500:
                return {
                    'url': url,
                    'domain': domain,
                    'title': title or f'{domain} Article',
                    'text': article_text[:5000],
                    'author': author or f'{domain} Staff',
                    'publish_date': self._extract_date(soup),
                    'extraction_method': 'generic'
                }
        
        return None
    
    def _extract_title(self, soup):
        """Extract article title"""
        selectors = [
            'h1',
            'meta[property="og:title"]',
            'meta[name="twitter:title"]',
            'title',
            '.headline',
            '.article-title'
        ]
        
        for selector in selectors:
            if selector.startswith('meta'):
                elem = soup.select_one(selector)
                if elem and elem.get('content'):
                    return elem['content'].strip()
            else:
                elem = soup.select_one(selector)
                if elem:
                    title = elem.get_text().strip()
                    if title and len(title) > 10:
                        return title
        return None
    
    def _extract_author(self, soup):
        """Extract article author"""
        org_names = [
            'staff', 'team', 'newsroom', 'correspondent', 'editor',
            'associated press', 'reuters', 'bloomberg'
        ]
        
        selectors = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            '.byline',
            '.author-name',
            '[rel="author"]'
        ]
        
        for selector in selectors:
            if selector.startswith('meta'):
                elem = soup.select_one(selector)
                if elem and elem.get('content'):
                    author = elem['content'].strip()
                    author = re.sub(r'^(By|BY|by)\s+', '', author)
                    if author and not any(org in author.lower() for org in org_names):
                        return author
            else:
                elem = soup.select_one(selector)
                if elem:
                    author = elem.get_text().strip()
                    author = re.sub(r'^(By|BY|by)\s+', '', author)
                    if author and len(author) > 2 and not any(org in author.lower() for org in org_names):
                        return author
        return None
    
    def _extract_date(self, soup):
        """Extract publish date"""
        selectors = [
            'time[datetime]',
            'meta[property="article:published_time"]',
            'meta[name="publish_date"]'
        ]
        
        for selector in selectors:
            if selector.startswith('meta'):
                elem = soup.select_one(selector)
                if elem and elem.get('content'):
                    return elem['content']
            else:
                elem = soup.select_one(selector)
                if elem and elem.get('datetime'):
                    return elem['datetime']
        return None
    
    def _extract_text_from_object(self, obj):
        """Extract text from nested objects"""
        if isinstance(obj, str):
            return obj
        elif isinstance(obj, dict):
            for key in ['content', 'body', 'text', 'articleBody']:
                if key in obj:
                    return self._extract_text_from_object(obj[key])
            texts = []
            for value in obj.values():
                if isinstance(value, str) and len(value) > 50:
                    texts.append(value)
            return ' '.join(texts)
        elif isinstance(obj, list):
            texts = []
            for item in obj:
                text = self._extract_text_from_object(item)
                if text:
                    texts.append(text)
            return ' '.join(texts)
        return ''
    
    def _find_in_dict(self, obj, keys):
        """Find value by trying multiple keys"""
        if isinstance(obj, dict):
            for key in keys:
                if key in obj and obj[key]:
                    return obj[key]
        return None
    
    def _is_boilerplate(self, text):
        """Check if text is boilerplate content"""
        boilerplate_phrases = [
            'cookie', 'subscribe', 'newsletter', 'sign up',
            'advertisement', 'sponsored', 'related articles',
            'read more', 'share this', 'follow us'
        ]
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in boilerplate_phrases)
