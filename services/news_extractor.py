"""
FILE: services/news_extractor.py
LOCATION: services/news_extractor.py
PURPOSE: Aggressive debugging to find why author extraction fails
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
    """Extract article content from URLs with aggressive author debugging"""
    
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
            
            # AGGRESSIVE DEBUG: Extract author with maximum logging
            author = self._extract_author_debug(soup, response.text, domain)
            
            publish_date = self._extract_date(soup)
            
            logger.info(f"FINAL EXTRACTION RESULT: Title='{title[:50]}...', Author='{author}', Text length={len(text)}")
            
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
            'main'
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
    
    def _extract_author_debug(self, soup, html_text, domain):
        """Extract author with AGGRESSIVE debugging"""
        
        logger.info("=" * 80)
        logger.info("STARTING AGGRESSIVE AUTHOR EXTRACTION DEBUG")
        logger.info("=" * 80)
        
        # STRATEGY 1: Direct pattern search in raw HTML
        logger.info("STRATEGY 1: Searching for author patterns in raw HTML")
        
        # Look for the exact pattern we saw in the logs
        if '"author"' in html_text:
            logger.info("✅ Found '\"author\"' in HTML!")
            
            # Multiple patterns to try
            patterns = [
                r'"author"\s*:\s*"([^"]+)"',
                r'&quot;author&quot;\s*:\s*&quot;([^&]+)&quot;',
                r'"author":\s*"([^"]+)"',
                r'author["\']?\s*:\s*["\']([^"\']+)["\']'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html_text)
                if matches:
                    logger.info(f"✅ Pattern '{pattern}' found {len(matches)} matches:")
                    for match in matches:
                        logger.info(f"   - Match: '{match}'")
                        # Clean and return the first valid match
                        if match and not any(org in match for org in ['Staff', 'News Service', 'Wire Service']):
                            # Handle comma-separated authors
                            if ',' in match:
                                authors = [a.strip() for a in match.split(',')]
                                author = ' and '.join(authors)
                            else:
                                author = match.strip()
                            logger.info(f"🎯 RETURNING AUTHOR: {author}")
                            return author
                else:
                    logger.info(f"❌ Pattern '{pattern}' found no matches")
        else:
            logger.warning("❌ '\"author\"' NOT found in HTML at all!")
        
        # STRATEGY 2: Check JSON-LD
        logger.info("\nSTRATEGY 2: Checking JSON-LD structured data")
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        logger.info(f"Found {len(json_ld_scripts)} JSON-LD scripts")
        
        for i, script in enumerate(json_ld_scripts):
            try:
                json_text = script.string
                if json_text:
                    logger.info(f"Parsing JSON-LD script {i+1}...")
                    # Log first 200 chars of JSON
                    logger.info(f"JSON preview: {json_text[:200]}...")
                    
                    data = json.loads(json_text)
                    author = self._extract_author_from_json(data)
                    if author:
                        logger.info(f"🎯 Found author in JSON-LD: {author}")
                        return author
                    else:
                        logger.info("No author found in this JSON-LD")
            except Exception as e:
                logger.info(f"Error parsing JSON-LD {i+1}: {e}")
        
        # STRATEGY 3: Meta tags
        logger.info("\nSTRATEGY 3: Checking meta tags")
        meta_selectors = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            'meta[name="byl"]',
            'meta[name="DC.creator"]',
            'meta[name="parsely-author"]'
        ]
        
        for selector in meta_selectors:
            meta = soup.select_one(selector)
            if meta:
                content = meta.get('content', '').strip()
                logger.info(f"Meta {selector}: '{content}'")
                if content and not any(org in content for org in ['Staff', 'News Service']):
                    return content
        
        # STRATEGY 4: Common byline selectors
        logger.info("\nSTRATEGY 4: Checking common byline selectors")
        byline_selectors = [
            '.byline',
            '.author',
            '[class*="byline"]',
            '[class*="author"]',
            'span.byline',
            'div.byline',
            'p.byline'
        ]
        
        for selector in byline_selectors:
            elements = soup.select(selector)
            logger.info(f"Selector '{selector}' found {len(elements)} elements")
            for elem in elements[:3]:  # Check first 3
                text = elem.get_text().strip()
                if text:
                    logger.info(f"   - Text: '{text[:100]}'")
                    # Clean up
                    text = re.sub(r'^(By|BY|by)\s+', '', text)
                    if text and len(text) < 100 and not any(org in text for org in ['Staff', 'News Service']):
                        return text
        
        # STRATEGY 5: Brute force - look for any element containing author-like text
        logger.info("\nSTRATEGY 5: Brute force search for 'By NAME' patterns")
        all_text_elements = soup.find_all(['p', 'span', 'div', 'h3', 'h4', 'h5'])
        by_pattern = re.compile(r'^(By|BY|by)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)', re.MULTILINE)
        
        for elem in all_text_elements[:50]:  # Check first 50 elements
            text = elem.get_text().strip()
            if text and len(text) < 100:
                match = by_pattern.match(text)
                if match:
                    author = match.group(2)
                    logger.info(f"Found potential author: '{author}' in element: {elem.name}")
                    if not any(org in author for org in ['Staff', 'News Service']):
                        return author
        
        logger.info("\n" + "=" * 80)
        logger.info("NO AUTHOR FOUND AFTER ALL STRATEGIES")
        logger.info("=" * 80)
        
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
            
            # Check other fields
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
        date_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="publish_date"]',
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
                        return datetime.fromisoformat(date_str.replace('Z', '+00:00')).isoformat()
                    except:
                        return date_str
        
        return None
