"""
FILE: services/news_extractor_diagnostic.py
LOCATION: news/services/news_extractor_diagnostic.py
PURPOSE: Diagnostic version to find extraction problems
"""

import logging
import re
from datetime import datetime
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class NewsExtractor:
    """Extract article content from URLs with diagnostics"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        logger.info("🟢 NewsExtractor initialized - DIAGNOSTIC MODE")
    
    def extract_article(self, url):
        """Extract article content from URL with diagnostics"""
        logger.info(f"🔍 DIAGNOSTIC: Starting extraction for URL: {url}")
        
        try:
            # Step 1: Fetch the page
            logger.info(f"📡 Fetching URL...")
            response = self.session.get(url, timeout=15, allow_redirects=True)
            logger.info(f"📊 Response status: {response.status_code}")
            logger.info(f"📊 Final URL: {response.url}")
            logger.info(f"📊 Content length: {len(response.content)} bytes")
            
            if response.status_code != 200:
                logger.error(f"❌ Bad status code: {response.status_code}")
                return None
            
            response.raise_for_status()
            
            # Step 2: Parse HTML
            logger.info(f"🔧 Parsing HTML...")
            soup = BeautifulSoup(response.content, 'html.parser')
            logger.info(f"✅ HTML parsed successfully")
            
            # Step 3: Extract components
            title = self._extract_title(soup)
            logger.info(f"📰 Title extracted: {title[:50]}..." if title else "❌ No title found")
            
            text = self._extract_text(soup)
            logger.info(f"📝 Text extracted: {len(text)} characters" if text else "❌ No text found")
            if text:
                logger.info(f"📝 Text preview: {text[:100]}...")
            
            author = self._extract_author(soup, url)
            logger.info(f"👤 Author extracted: {author}" if author else "❌ No author found")
            
            publish_date = self._extract_date(soup)
            logger.info(f"📅 Date extracted: {publish_date}" if publish_date else "❌ No date found")
            
            # Get domain
            domain = urlparse(url).netloc.replace('www.', '')
            logger.info(f"🌐 Domain: {domain}")
            
            # Check if we have minimum required data
            if not title and not text:
                logger.error("❌ CRITICAL: No title or text found - extraction failed")
                return None
            
            result = {
                'title': title or 'No title found',
                'text': text or 'No article text found',
                'author': author,
                'publish_date': publish_date,
                'url': url,
                'domain': domain
            }
            
            logger.info(f"✅ EXTRACTION SUCCESSFUL - Title: {bool(title)}, Text: {bool(text)}, Author: {bool(author)}")
            return result
            
        except requests.exceptions.Timeout:
            logger.error(f"❌ TIMEOUT: Request took too long")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ CONNECTION ERROR: Could not connect to {url}")
            return None
        except Exception as e:
            logger.error(f"❌ EXTRACTION ERROR: {str(e)}", exc_info=True)
            return None
    
    def _extract_title(self, soup):
        """Extract article title with diagnostics"""
        logger.info("🔍 Extracting title...")
        
        # Try common title selectors
        selectors = [
            ('h1', 'H1 tag'),
            ('meta[property="og:title"]', 'og:title meta'),
            ('meta[name="twitter:title"]', 'twitter:title meta'),
            ('title', 'title tag')
        ]
        
        for selector, name in selectors:
            logger.debug(f"  Trying {name}...")
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    title = element.get('content', '').strip()
                else:
                    title = element.get_text().strip()
                
                if title:
                    logger.info(f"  ✅ Found title via {name}: {title[:50]}...")
                    return title
        
        logger.warning("  ❌ No title found with standard selectors")
        return 'No title found'
    
    def _extract_text(self, soup):
        """Extract main article text with diagnostics"""
        logger.info("🔍 Extracting article text...")
        
        # Remove script and style elements
        for script in soup(['script', 'style']):
            script.decompose()
        
        # Try to find article body
        article_selectors = [
            ('article', 'article tag'),
            ('[class*="article-body"]', 'article-body class'),
            ('[class*="story-body"]', 'story-body class'),
            ('[class*="content-body"]', 'content-body class'),
            ('[class*="body-text"]', 'body-text class'),
            ('[class*="article__content"]', 'article__content class'),
            ('[class*="zn-body__paragraph"]', 'CNN specific class'),
            ('main', 'main tag'),
            ('[role="main"]', 'role=main')
        ]
        
        for selector, name in article_selectors:
            logger.debug(f"  Trying {name}...")
            article = soup.select_one(selector)
            if article:
                paragraphs = article.find_all('p')
                logger.debug(f"    Found {len(paragraphs)} paragraphs")
                if paragraphs:
                    text = ' '.join([p.get_text().strip() for p in paragraphs])
                    if len(text) > 100:
                        logger.info(f"  ✅ Found text via {name}: {len(text)} chars")
                        return text
        
        # Fallback: get all paragraphs
        logger.warning("  ⚠️ Using fallback: all paragraphs")
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text().strip() for p in paragraphs[:20]])
        
        if text:
            logger.info(f"  ✅ Fallback found {len(text)} chars")
        else:
            logger.error("  ❌ No text found at all")
        
        return text if text else 'No article text found'
    
    def _extract_author(self, soup, url):
        """Extract author with diagnostics"""
        logger.info("🔍 Extracting author...")
        
        # Organization names to filter out
        org_names = [
            'ABC News', 'CNN', 'BBC', 'Reuters', 'AP', 'Associated Press',
            'Fox News', 'NBC News', 'CBS News', 'MSNBC', 'NPR'
        ]
        
        def is_organization_name(text):
            if not text:
                return True
            for org in org_names:
                if org.lower() in text.lower():
                    logger.debug(f"  ❌ Filtered out organization: {text}")
                    return True
            return False
        
        def clean_author_text(text):
            if not text:
                return None
            text = re.sub(r'^(by|By|BY)\s+', '', text.strip())
            text = re.sub(r'\s+', ' ', text)
            return text.strip()
        
        # Try different methods
        methods = [
            'JSON-LD', 'Meta tags', 'Byline selectors', 
            'By pattern', 'CNN specific'
        ]
        
        # Method 1: JSON-LD
        logger.debug("  Trying JSON-LD...")
        json_ld = soup.find_all('script', type='application/ld+json')
        for script in json_ld:
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, dict) and 'author' in data:
                    author = data.get('author')
                    if isinstance(author, dict):
                        name = author.get('name', '')
                    elif isinstance(author, str):
                        name = author
                    else:
                        continue
                    
                    name = clean_author_text(name)
                    if name and not is_organization_name(name):
                        logger.info(f"  ✅ Found via JSON-LD: {name}")
                        return name
            except:
                pass
        
        # Method 2: Meta tags
        logger.debug("  Trying meta tags...")
        meta_selectors = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            'meta[name="byl"]'
        ]
        
        for selector in meta_selectors:
            meta = soup.select_one(selector)
            if meta and meta.get('content'):
                author = clean_author_text(meta['content'])
                if author and not is_organization_name(author):
                    logger.info(f"  ✅ Found via meta tag: {author}")
                    return author
        
        # Method 3: CNN specific selectors
        if 'cnn.com' in url:
            logger.debug("  Trying CNN specific selectors...")
            cnn_selectors = [
                '.byline__name',
                '.metadata__byline__author',
                '[class*="author"]'
            ]
            for selector in cnn_selectors:
                elem = soup.select_one(selector)
                if elem:
                    author = clean_author_text(elem.get_text())
                    if author and not is_organization_name(author):
                        logger.info(f"  ✅ Found via CNN selector: {author}")
                        return author
        
        logger.warning("  ❌ No author found")
        return None
    
    def _extract_date(self, soup):
        """Extract publish date with diagnostics"""
        logger.info("🔍 Extracting date...")
        
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
                    logger.info(f"  ✅ Found date: {date_str}")
                    return date_str
        
        logger.warning("  ❌ No date found")
        return None
                paragraphs = article.find_all('p')
                logger.debug(f"    Found {len(paragraphs)} paragraphs")
                if paragraphs:
                    text = ' '.join([p.get_text().strip() for p in paragraphs])
                    if len(text) > 100:
                        logger.info(f"  ✅ Found text via {name}: {len(text)} chars")
                        return text
        
        # Fallback: get all paragraphs
        logger.warning("  ⚠️ Using fallback: all paragraphs")
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text().strip() for p in paragraphs[:20]])
        
        if text:
            logger.info(f"  ✅ Fallback found {len(text)} chars")
        else:
            logger.error("  ❌ No text found at all")
        
        return text if text else 'No article text found'
