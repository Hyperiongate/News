"""
FILE: services/news_extractor.py
LOCATION: services/news_extractor.py
PURPOSE: Debug version to see exactly what HTML we're getting
"""

import logging
import re
from datetime import datetime
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class NewsExtractor:
    """Extract article content from URLs with debug logging"""
    
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
            logger.info(f"🔍 Starting extraction for: {url}")
            
            response = self.session.get(url, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            if not response.content:
                logger.error(f"Empty response from {url}")
                return None
            
            # DEBUG: Save the HTML to a file for inspection
            domain = urlparse(url).netloc.replace('www.', '')
            debug_filename = f"debug_{domain.replace('.', '_')}.html"
            with open(debug_filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            logger.info(f"📄 HTML saved to {debug_filename} for debugging")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # DEBUG: Log the first 500 chars of text to see what we're getting
            page_text = soup.get_text()[:500]
            logger.info(f"📝 First 500 chars of page text:\n{page_text}")
            
            # DEBUG: Search for "JINTAMAS" or "CHEANG" anywhere in the HTML
            if "JINTAMAS" in response.text:
                logger.info("✅ Found 'JINTAMAS' in raw HTML!")
                # Find the context around it
                idx = response.text.find("JINTAMAS")
                context = response.text[max(0, idx-100):idx+200]
                logger.info(f"Context around JINTAMAS:\n{context}")
            else:
                logger.warning("❌ 'JINTAMAS' NOT found in raw HTML!")
            
            # Extract components
            title = self._extract_title(soup)
            logger.info(f"📰 Title: {title}")
            
            # Simple author extraction for debugging
            author = self._debug_extract_author(soup, response.text)
            logger.info(f"👤 Author found: {author}")
            
            text = self._extract_text(soup, url)
            publish_date = self._extract_date(soup)
            
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
    
    def _debug_extract_author(self, soup, html_text):
        """Debug version of author extraction"""
        logger.info("🔍 DEBUG: Starting author extraction")
        
        # First, let's see if the author names appear anywhere in the HTML
        author_patterns = [
            r'By\s+([A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+(?:\s+and\s+[A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+)*)',
            r'BY\s+([A-Z][A-Z\s]+)',
            r'by\s+([A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+)',
        ]
        
        for pattern in author_patterns:
            matches = re.findall(pattern, html_text)
            if matches:
                logger.info(f"✅ Pattern '{pattern}' found matches: {matches}")
                for match in matches:
                    # Clean and validate
                    if match and not any(org in match for org in ['News', 'Staff', 'Service', 'Team']):
                        return match.strip()
        
        # Check specific AP News structure
        logger.info("🔍 Checking AP News specific selectors...")
        
        # AP News often uses specific classes
        ap_selectors = [
            'span.Page-authorText',
            'div.Page-author',
            'span.byline',
            'div.byline',
            '[class*="author"]',
            '[class*="byline"]'
        ]
        
        for selector in ap_selectors:
            elements = soup.select(selector)
            logger.info(f"Selector '{selector}' found {len(elements)} elements")
            for elem in elements:
                text = elem.get_text().strip()
                if text:
                    logger.info(f"  - Text: '{text}'")
                    if 'By' in text or 'BY' in text:
                        # Clean it up
                        author = re.sub(r'^(By|BY)\s+', '', text).strip()
                        if author and not any(org in author for org in ['News', 'Staff']):
                            return author
        
        # Let's check ALL text elements that might contain author
        logger.info("🔍 Checking all span and div elements containing 'By'...")
        for elem in soup.find_all(['span', 'div', 'p']):
            text = elem.get_text().strip()
            if text.startswith(('By ', 'BY ', 'by ')) and len(text) < 100:
                logger.info(f"  Found potential author element: '{text}'")
        
        logger.warning("❌ No author found after all attempts")
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
        
        # Try to find article body
        article_selectors = [
            'article',
            '[class*="article-body"]',
            '[class*="story-body"]',
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
