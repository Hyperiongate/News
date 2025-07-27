"""
FILE: services/news_extractor.py
LOCATION: services/news_extractor.py
PURPOSE: Enhanced article extraction with better author detection for AP News and other sites
"""

import logging
import re
from datetime import datetime
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class NewsExtractor:
    """Extract article content from URLs with enhanced author detection"""
    
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
            
            # Log what we found for debugging
            logger.info(f"Extracted from {domain}: Title='{title[:50]}...', Author='{author}', Text length={len(text)}")
            
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
        
        # AP News specific handling
        if 'apnews.com' in url:
            # AP News specific selectors
            ap_selectors = [
                'div.RichTextStoryBody',
                'div[class*="RichTextStoryBody"]',
                'div.Article',
                'div[class*="Page-content"]',
                'main p',
                'div[class*="story-body"] p'
            ]
            
            for selector in ap_selectors:
                if ' ' in selector:
                    # Handle compound selectors
                    container, tag = selector.rsplit(' ', 1)
                    containers = soup.select(container)
                    for cont in containers:
                        paragraphs = cont.find_all(tag)
                        if paragraphs:
                            text = ' '.join([p.get_text().strip() for p in paragraphs])
                            if len(text) > 100:
                                return text
                else:
                    elements = soup.select(selector)
                    if elements:
                        text = ' '.join([e.get_text().strip() for e in elements])
                        if len(text) > 100:
                            return text
        
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
        """Extract author with enhanced AP News support"""
        
        # List of organization names to filter out
        org_names = [
            'ABC News', 'CNN', 'BBC', 'Reuters', 'AP', 'Associated Press',
            'Fox News', 'NBC News', 'CBS News', 'MSNBC', 'NPR', 'PBS',
            'The New York Times', 'The Washington Post', 'The Guardian',
            'Bloomberg', 'CNBC', 'The Hill', 'Politico', 'Axios',
            'The Wall Street Journal', 'USA Today', 'The Independent',
            'AP News', 'The Associated Press'
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
            if any(word in text.lower() for word in ['news', 'staff', 'team', 'correspondent', 'newsroom', 'editorial', 'wire service']):
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
            # Remove organization names that might be appended
            for org in org_names:
                text = text.replace(f' and {org}', '').replace(f' / {org}', '').replace(f', {org}', '')
            return text.strip()
        
        # Get domain for site-specific handling
        domain = urlparse(url).netloc.replace('www.', '')
        
        # AP News specific extraction FIRST
        if 'apnews.com' in domain:
            logger.info("Using AP News specific author extraction")
            
            # AP News specific selectors - updated for their current site structure
            ap_author_selectors = [
                'span.Page-authors',
                'div.Page-authors',
                'span[class*="Component-authors"]',
                'div[class*="Component-authors"]',
                'a[class*="Component-authorLink"]',
                'span[class*="authorName"]',
                'div.CardHeadline-author',
                'div[class*="Byline"]',
                'a[class*="Link--author"]',
                'span.Byline-author',
                'a.author-name',
                # Look for the author in the hero/header area
                'div[class*="Page-header"] a[href*="/author/"]',
                'div[class*="Page-header"] span[class*="author"]',
                # Sometimes it's just a link with author in the URL
                'a[href*="/author/"]'
            ]
            
            for selector in ap_author_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    
                    # AP News sometimes prefixes with "By"
                    text = clean_author_text(text)
                    
                    # Skip if it's an organization or empty
                    if text and not is_organization_name(text) and text.lower() != 'ap':
                        logger.info(f"Found AP News author: {text}")
                        return text
            
            # Look for author in links that contain /author/ in the URL
            author_links = soup.find_all('a', href=re.compile(r'/author/|/by/', re.I))
            for link in author_links:
                text = link.get_text().strip()
                text = clean_author_text(text)
                if text and not is_organization_name(text):
                    logger.info(f"Found AP News author from link: {text}")
                    return text
        
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
                                logger.info(f"Found author from JSON-LD: {name}")
                                return name
                        elif isinstance(author, str):
                            name = clean_author_text(author)
                            if name and not is_organization_name(name):
                                logger.info(f"Found author from JSON-LD string: {name}")
                                return name
                        elif isinstance(author, list) and author:
                            # If it's a list, get the first valid author
                            for auth in author:
                                if isinstance(auth, dict):
                                    name = auth.get('name', '')
                                    name = clean_author_text(name)
                                    if name and not is_organization_name(name):
                                        logger.info(f"Found author from JSON-LD list: {name}")
                                        return name
                                elif isinstance(auth, str):
                                    name = clean_author_text(auth)
                                    if name and not is_organization_name(name):
                                        logger.info(f"Found author from JSON-LD list string: {name}")
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
                                            logger.info(f"Found author from @graph: {name}")
                                            return name
                                    elif isinstance(author, str):
                                        name = clean_author_text(author)
                                        if name and not is_organization_name(name):
                                            logger.info(f"Found author from @graph string: {name}")
                                            return name
            except:
                continue
        
        # Method 2: Meta tags
        meta_selectors = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            'meta[name="byl"]',
            'meta[name="DC.creator"]',
            'meta[name="parsely-author"]',
            'meta[property="og:article:author"]',
            'meta[name="twitter:creator"]'
        ]
        
        for selector in meta_selectors:
            meta = soup.select_one(selector)
            if meta and meta.get('content'):
                author = clean_author_text(meta['content'])
                if author and not is_organization_name(author):
                    logger.info(f"Found author from meta tag: {author}")
                    return author
        
        # Method 3: Common byline patterns with better filtering
        byline_selectors = [
            '[class*="byline"]:not([class*="date"])',
            '[class*="author"]:not([class*="bio"])',
            '[class*="by-line"]',
            '[class*="writer"]',
            'span[itemprop="author"]',
            '[rel="author"]',
            '.byline__name',
            '.authors__name',
            '.contributor__name',
            '.ArticleByline',
            '.article-author',
            '.by-author',
            '.story-meta__author',
            '.author-name',
            '[data-testid="author-name"]'
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
                    logger.info(f"Found author from byline selector: {text}")
                    return text
        
        # Method 4: Look for "By [Name]" pattern in the article
        # This is especially important for sites that don't use structured markup
        by_patterns = [
            r'^(?:by|By|BY)\s+([A-Z][a-z]+(?:\s+[A-Z]\.?\s+)?[A-Z][a-z]+)',  # Matches "By First Last" or "By First M. Last"
            r'^(?:by|By|BY)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',  # Matches "By First Last Last"
            r'^\s*([A-Z][a-z]+(?:\s+[A-Z]\.?\s+)?[A-Z][a-z]+)\s*\|',  # Matches "First Last |"
        ]
        
        # Look in the first part of the article for bylines
        article_start = soup.find(['article', 'main', '[role="main"]'])
        if article_start:
            # Check first few elements
            for elem in article_start.find_all(['p', 'div', 'span'])[:20]:
                text = elem.get_text().strip()
                if text:
                    for pattern in by_patterns:
                        match = re.match(pattern, text)
                        if match:
                            author = match.group(1)
                            if not is_organization_name(author):
                                logger.info(f"Found author from text pattern: {author}")
                                return author
        
        # Method 5: Site-specific patterns
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
                        logger.info(f"Found CNN author: {author}")
                        return author
        
        # If no valid author found, log it and return None
        logger.info(f"No author found for {domain}")
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
        
        # Look for date in common date containers
        date_containers = soup.select('[class*="date"], [class*="time"], [class*="published"]')
        for container in date_containers:
            text = container.get_text().strip()
            # Try to parse various date formats
            # This is simplified - in production you'd want more robust date parsing
            if re.search(r'\d{4}', text):  # Has a year
                return text
        
        return None
