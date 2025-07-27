"""
FILE: services/news_extractor.py
LOCATION: services/news_extractor.py
PURPOSE: Universal article extraction that finds authors on any news site
"""

import logging
import re
from datetime import datetime
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class NewsExtractor:
    """Extract article content from URLs with intelligent author detection"""
    
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
            response = self.session.get(url, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            if not response.content:
                logger.error(f"Empty response from {url}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract components
            title = self._extract_title(soup)
            text = self._extract_text(soup, url)
            author = self._extract_author(soup, url)
            publish_date = self._extract_date(soup)
            
            # Get domain
            domain = urlparse(url).netloc.replace('www.', '')
            
            # Validate we have minimum content
            if not title or not text or len(text) < 50:
                logger.error(f"Insufficient content extracted from {url}")
                if not text or len(text) < 50:
                    text = self._extract_text_fallback(soup)
            
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
    
    def _extract_text_fallback(self, soup):
        """Fallback text extraction for difficult sites"""
        # Try div tags with common content classes
        content_divs = soup.find_all('div', class_=re.compile(r'(content|article|story|body|text)', re.I))
        
        all_text = []
        for div in content_divs[:10]:
            text = div.get_text(separator=' ', strip=True)
            if len(text) > 100:
                all_text.append(text)
        
        if all_text:
            return ' '.join(all_text)
        
        # Last resort: get all text from body
        body = soup.find('body')
        if body:
            text = body.get_text(separator=' ', strip=True)
            lines = text.split('\n')
            cleaned_lines = [line.strip() for line in lines if len(line.strip()) > 50]
            return ' '.join(cleaned_lines[:20])
        
        return 'No article text found'
    
    def _extract_author(self, soup, url):
        """Extract author using multiple intelligent strategies"""
        
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
            # Check against known orgs
            for org in org_names:
                if org.lower() in text_lower:
                    return True
            # Check for common organization patterns
            if any(word in text_lower for word in ['news', 'staff', 'team', 'correspondent', 'newsroom', 'editorial', 'wire service', 'service']):
                return True
            # Check if it looks like a person name (First Last)
            parts = text.strip().split()
            if len(parts) >= 2 and len(parts) <= 4:
                # Check if words are capitalized (like names)
                if all(part[0].isupper() for part in parts if part):
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
            text = re.sub(r'\s+(and|for|of)\s+.*(News|Staff|Team|Service).*$', '', text, flags=re.IGNORECASE)
            # Remove organization names that might be appended
            for org in org_names:
                text = text.replace(f' and {org}', '').replace(f' / {org}', '').replace(f', {org}', '')
            return text.strip()
        
        # STRATEGY 1: Look for "By NAME and NAME" patterns in the full page text
        logger.info("Strategy 1: Looking for 'By NAME and NAME' patterns")
        page_text = soup.get_text()
        
        # Pattern for "By First Last and First Last"
        by_patterns = [
            r'By\s+([A-Z][A-Za-z]+(?:\s+[A-Z]\.?\s*)?[A-Z][A-Za-z]+(?:\s+(?:and|&)\s+[A-Z][A-Za-z]+(?:\s+[A-Z]\.?\s*)?[A-Z][A-Za-z]+)*)',
            r'BY\s+([A-Z][A-Za-z]+(?:\s+[A-Z]\.?\s*)?[A-Z][A-Za-z]+(?:\s+(?:AND|&)\s+[A-Z][A-Za-z]+(?:\s+[A-Z]\.?\s*)?[A-Z][A-Za-z]+)*)',
            r'by\s+([A-Z][A-Za-z]+(?:\s+[A-Z]\.?\s*)?[A-Z][A-Za-z]+(?:\s+(?:and|&)\s+[A-Z][A-Za-z]+(?:\s+[A-Z]\.?\s*)?[A-Z][A-Za-z]+)*)',
        ]
        
        for pattern in by_patterns:
            matches = re.findall(pattern, page_text)
            for match in matches:
                author = clean_author_text(match)
                if author and not is_organization_name(author):
                    logger.info(f"Found author via 'By' pattern: {author}")
                    return author
        
        # STRATEGY 2: Check structured data (JSON-LD)
        logger.info("Strategy 2: Checking JSON-LD structured data")
        json_ld = soup.find_all('script', type='application/ld+json')
        for script in json_ld:
            try:
                import json
                data = json.loads(script.string)
                
                def extract_from_json(obj):
                    if isinstance(obj, dict):
                        # Direct author field
                        if 'author' in obj:
                            author_data = obj['author']
                            if isinstance(author_data, str):
                                author = clean_author_text(author_data)
                                if author and not is_organization_name(author):
                                    return author
                            elif isinstance(author_data, dict) and 'name' in author_data:
                                author = clean_author_text(author_data['name'])
                                if author and not is_organization_name(author):
                                    return author
                            elif isinstance(author_data, list):
                                # Multiple authors
                                authors = []
                                for a in author_data:
                                    if isinstance(a, str):
                                        name = clean_author_text(a)
                                    elif isinstance(a, dict) and 'name' in a:
                                        name = clean_author_text(a['name'])
                                    else:
                                        continue
                                    if name and not is_organization_name(name):
                                        authors.append(name)
                                if authors:
                                    return ' and '.join(authors)
                        
                        # Check in @graph
                        if '@graph' in obj:
                            for item in obj['@graph']:
                                result = extract_from_json(item)
                                if result:
                                    return result
                        
                        # Recursively check other fields
                        for key, value in obj.items():
                            if key not in ['@context', '@id']:
                                result = extract_from_json(value)
                                if result:
                                    return result
                    elif isinstance(obj, list):
                        for item in obj:
                            result = extract_from_json(item)
                            if result:
                                return result
                    return None
                
                author = extract_from_json(data)
                if author:
                    logger.info(f"Found author in JSON-LD: {author}")
                    return author
                    
            except Exception as e:
                logger.debug(f"Error parsing JSON-LD: {e}")
                continue
        
        # STRATEGY 3: Meta tags
        logger.info("Strategy 3: Checking meta tags")
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
        
        # STRATEGY 4: Look for elements containing "by" or author-related classes
        logger.info("Strategy 4: Looking for byline elements")
        
        # First, try to find elements that contain "by" text
        all_elements = soup.find_all(['div', 'span', 'p', 'h3', 'h4', 'h5'])
        for elem in all_elements:
            text = elem.get_text().strip()
            if text.lower().startswith('by ') and len(text) < 100:
                author = clean_author_text(text)
                if author and not is_organization_name(author):
                    logger.info(f"Found author in element with 'By': {author}")
                    return author
        
        # Look for elements with author-related classes or attributes
        author_selectors = [
            '[class*="byline"]',
            '[class*="author"]',
            '[class*="by-line"]',
            '[class*="writer"]',
            '[class*="contributor"]',
            '[class*="journalist"]',
            '[itemprop="author"]',
            '[rel="author"]',
            'a[href*="/author/"]',
            'a[href*="/by/"]',
            'a[href*="/journalist/"]',
            'a[href*="/contributor/"]'
        ]
        
        for selector in author_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text().strip()
                
                # Skip if too long or too short
                if len(text) < 3 or len(text) > 100:
                    continue
                
                # Clean and check
                author = clean_author_text(text)
                if author and not is_organization_name(author):
                    logger.info(f"Found author in selector {selector}: {author}")
                    return author
        
        # STRATEGY 5: Look near the title or date
        logger.info("Strategy 5: Looking near title/date for author")
        
        # Find the main heading
        h1 = soup.find('h1')
        if h1:
            # Look at the next few elements after the title
            next_elem = h1.find_next_sibling()
            for _ in range(10):  # Check next 10 elements
                if next_elem:
                    text = next_elem.get_text().strip()
                    if text and len(text) < 100:
                        # Check if it matches author pattern
                        if re.match(r'^(by|By|BY)\s+[A-Z]', text):
                            author = clean_author_text(text)
                            if author and not is_organization_name(author):
                                logger.info(f"Found author near title: {author}")
                                return author
                    next_elem = next_elem.find_next_sibling()
        
        # STRATEGY 6: Look in the article header area
        logger.info("Strategy 6: Checking article header area")
        header_selectors = ['article header', 'header', '[class*="article-header"]', '[class*="story-header"]']
        for selector in header_selectors:
            header = soup.select_one(selector)
            if header:
                # Get all text in header
                header_text = header.get_text()
                # Look for By patterns
                for pattern in by_patterns:
                    match = re.search(pattern, header_text)
                    if match:
                        author = clean_author_text(match.group(1))
                        if author and not is_organization_name(author):
                            logger.info(f"Found author in header: {author}")
                            return author
        
        logger.info("No author found after all strategies")
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
            if re.search(r'\d{4}', text):  # Has a year
                return text
        
        return None
