"""
FILE: services/news_extractor.py
LOCATION: services/news_extractor.py
PURPOSE: UNIVERSAL news extractor that works with ANY URL using multiple fallback methods
"""

import logging
import re
import json
import time
from datetime import datetime
from urllib.parse import urlparse, urljoin
from collections import Counter

import requests
from bs4 import BeautifulSoup, NavigableString

# Try to import optional libraries for enhanced extraction
try:
    import trafilatura
    TRAFILATURA_AVAILABLE = True
except ImportError:
    TRAFILATURA_AVAILABLE = False
    
try:
    from readability import Readability
    READABILITY_AVAILABLE = True
except ImportError:
    READABILITY_AVAILABLE = False

logger = logging.getLogger(__name__)

class NewsExtractor:
    """Universal news extractor with multiple fallback methods"""
    
    def __init__(self):
        self.session = requests.Session()
        
        # Rotate through different user agents to avoid blocks
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        self.current_ua_index = 0
        self._update_session_headers()
        
        # Common first and last names for validation (existing code)
        self.common_first_names = {
            'james', 'john', 'robert', 'michael', 'william', 'david', 'richard', 'joseph',
            'thomas', 'charles', 'mary', 'patricia', 'jennifer', 'linda', 'elizabeth',
            'barbara', 'susan', 'jessica', 'sarah', 'karen', 'daniel', 'matthew', 'donald',
            'mark', 'paul', 'steven', 'andrew', 'kenneth', 'joshua', 'kevin', 'brian',
            'george', 'edward', 'ronald', 'timothy', 'jason', 'jeffrey', 'ryan', 'jacob',
            'gary', 'nicholas', 'eric', 'jonathan', 'stephen', 'larry', 'justin', 'scott',
            'brandon', 'benjamin', 'samuel', 'frank', 'gregory', 'raymond', 'alexander',
            'patrick', 'jack', 'dennis', 'jerry', 'tyler', 'aaron', 'jose', 'nathan',
            'henry', 'zachary', 'douglas', 'peter', 'adam', 'noah', 'christopher', 'nancy',
            'betty', 'helen', 'sandra', 'donna', 'carol', 'ruth', 'sharon', 'michelle',
            'laura', 'kimberly', 'deborah', 'rachel', 'amy', 'anna', 'maria', 'dorothy',
            'lisa', 'ashley', 'madison', 'amanda', 'melissa', 'debra', 'stephanie', 'rebecca',
            'virginia', 'kathleen', 'pamela', 'martha', 'angela', 'katherine', 'christine',
            'emma', 'olivia', 'sophia', 'isabella', 'charlotte', 'amelia', 'evelyn',
            'jeremy', 'simon', 'martin', 'peter', 'alan', 'ian', 'colin', 'graham',
            'daniella', 'didi', 'martinez', 'silva'
        }
        
        self.common_last_names = {
            'smith', 'johnson', 'williams', 'brown', 'jones', 'garcia', 'miller', 'davis',
            'rodriguez', 'martinez', 'hernandez', 'lopez', 'gonzalez', 'wilson', 'anderson',
            'thomas', 'taylor', 'moore', 'jackson', 'martin', 'lee', 'perez', 'thompson',
            'white', 'harris', 'sanchez', 'clark', 'ramirez', 'lewis', 'robinson', 'walker',
            'young', 'allen', 'king', 'wright', 'scott', 'torres', 'nguyen', 'hill',
            'flores', 'green', 'adams', 'nelson', 'baker', 'hall', 'rivera', 'campbell',
            'mitchell', 'carter', 'roberts', 'bowen', 'cohen', 'chen', 'wang', 'kim',
            'silva', 'martinez'
        }
        
        self.org_names = {
            'nbc', 'cnn', 'fox', 'abc', 'cbs', 'bbc', 'npr', 'reuters', 'associated press',
            'bloomberg', 'new york times', 'washington post', 'guardian', 'daily mail',
            'usa today', 'wall street journal', 'los angeles times', 'chicago tribune',
            'boston globe', 'miami herald', 'news', 'media', 'press', 'network',
            'broadcasting', 'times', 'post', 'journal', 'herald', 'globe', 'tribune'
        }
    
    def _update_session_headers(self):
        """Update session with current user agent"""
        self.session.headers.update({
            'User-Agent': self.user_agents[self.current_ua_index],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        })
    
    def _rotate_user_agent(self):
        """Rotate to next user agent"""
        self.current_ua_index = (self.current_ua_index + 1) % len(self.user_agents)
        self._update_session_headers()
    
    def extract_article(self, url):
        """Extract article content from URL using multiple methods"""
        logger.info(f"🌐 UNIVERSAL EXTRACTION for: {url}")
        
        # Try multiple extraction methods in order
        methods = [
            ("Standard", self._extract_standard),
            ("Enhanced", self._extract_enhanced),
            ("Aggressive", self._extract_aggressive),
            ("Trafilatura", self._extract_with_trafilatura),
            ("Readability", self._extract_with_readability),
            ("Emergency", self._extract_emergency)
        ]
        
        for method_name, method_func in methods:
            try:
                logger.info(f"Trying {method_name} extraction...")
                result = method_func(url)
                
                if result and result.get('text') and len(result['text']) > 200:
                    logger.info(f"✅ {method_name} extraction successful!")
                    return result
                else:
                    logger.warning(f"{method_name} extraction returned insufficient content")
                    
            except Exception as e:
                logger.warning(f"{method_name} extraction failed: {str(e)}")
                # Rotate user agent after failure
                self._rotate_user_agent()
                continue
        
        # If all methods fail, return with basic metadata
        logger.error(f"All extraction methods failed for {url}")
        return self._create_fallback_result(url)
    
    def _extract_standard(self, url):
        """Standard extraction method (original implementation)"""
        response = self.session.get(url, timeout=30, allow_redirects=True)
        response.raise_for_status()
        
        if not response.content:
            raise ValueError("Empty response")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        domain = urlparse(url).netloc.replace('www.', '')
        
        # Extract components
        title = self._extract_title(soup)
        text = self._extract_text(soup, url)
        author = self._extract_author_ultimate(soup, response.text, title, text, domain)
        publish_date = self._extract_date(soup)
        
        return {
            'title': title or 'No title found',
            'text': text or 'No article text found',
            'author': author,
            'publish_date': publish_date,
            'url': url,
            'domain': domain
        }
    
    def _extract_enhanced(self, url):
        """Enhanced extraction with more aggressive content finding"""
        # Try multiple request strategies
        for attempt in range(3):
            try:
                headers = self.session.headers.copy()
                
                # Add additional headers that might help
                headers.update({
                    'Referer': 'https://www.google.com/',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'cross-site'
                })
                
                response = self.session.get(url, headers=headers, timeout=45, allow_redirects=True)
                response.raise_for_status()
                break
            except Exception as e:
                if attempt == 2:
                    raise
                self._rotate_user_agent()
                time.sleep(1)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        domain = urlparse(url).netloc.replace('www.', '')
        
        # Remove all scripts, styles, and comments more aggressively
        for element in soup(['script', 'style', 'noscript', 'iframe', 'svg']):
            element.decompose()
        
        # Remove all comments
        for element in soup.find_all(string=lambda text: isinstance(text, NavigableString) and '<!--' in str(text)):
            element.extract()
        
        title = self._extract_title(soup)
        
        # Enhanced text extraction
        text = self._extract_text_enhanced(soup, url)
        
        # Use both HTML and cleaned text for author extraction
        author = self._extract_author_ultimate(soup, response.text, title, text, domain)
        
        # If no author found, try emergency author extraction
        if not author:
            author = self._extract_author_emergency(soup, response.text, domain)
        
        publish_date = self._extract_date(soup)
        
        return {
            'title': title,
            'text': text,
            'author': author,
            'publish_date': publish_date,
            'url': url,
            'domain': domain
        }
    
    def _extract_text_enhanced(self, soup, url):
        """Enhanced text extraction with more patterns"""
        # Try JSON-LD structured data first
        json_ld_text = self._extract_from_json_ld(soup)
        if json_ld_text and len(json_ld_text) > 200:
            return json_ld_text
        
        # Extended list of content selectors
        content_selectors = [
            # Standard selectors
            'article', '[role="main"]', 'main',
            
            # Class-based selectors (more specific)
            '[class*="article-body"]', '[class*="story-body"]', 
            '[class*="content-body"]', '[class*="post-body"]',
            '[class*="entry-content"]', '[class*="article-content"]',
            '[class*="story-content"]', '[class*="article__body"]',
            '[class*="post__body"]', '[class*="content__body"]',
            
            # ID-based selectors
            '[id*="article-body"]', '[id*="story-body"]',
            '[id*="content-body"]', '[id*="post-body"]',
            '[id*="main-content"]', '[id*="primary-content"]',
            
            # Specific site patterns
            '.story-body-text', '.article-text', '.post-content',
            '.entry', '.prose', '.story-text', '.article-wrap',
            '.story-wrapper', '.article-wrapper', '.body-copy',
            
            # News site specific
            '.wsj-snippet-body', '.css-1fanzo5', '.StoryBodyCompanionColumn',
            '.article__body-content', '.body__content', '.c-entry-content',
            '.js-article__body', '.article__chunks', '.paywall',
            
            # Generic containers
            '.content', '#content', '.container article',
            '.post', '.entry-wrapper', '.main-content',
            '.td-post-content', '.jeg_content', '.post_content'
        ]
        
        article_text = ""
        
        for selector in content_selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    # Skip if inside nav, header, or footer
                    if element.find_parent(['nav', 'header', 'footer', 'aside']):
                        continue
                    
                    # Get all text blocks
                    paragraphs = element.find_all(['p', 'h2', 'h3', 'h4', 'blockquote', 'li'])
                    
                    if paragraphs:
                        texts = []
                        for p in paragraphs:
                            text = p.get_text().strip()
                            # More lenient text filtering
                            if text and len(text) > 10:
                                texts.append(text)
                        
                        if texts:
                            potential_text = ' '.join(texts)
                            if len(potential_text) > len(article_text):
                                article_text = potential_text
            except:
                continue
        
        # If still no content, try more aggressive approach
        if not article_text or len(article_text) < 200:
            article_text = self._extract_all_paragraphs(soup)
        
        return article_text if article_text else 'No article text found'
    
    def _extract_all_paragraphs(self, soup):
        """Extract all paragraphs as last resort"""
        all_paragraphs = []
        
        # Get all p tags that likely contain article content
        for p in soup.find_all('p'):
            # Skip if in navigation/header/footer
            if p.find_parent(['nav', 'header', 'footer', 'menu']):
                continue
            
            text = p.get_text().strip()
            
            # Filter out likely non-article content
            if (len(text) > 30 and 
                not text.startswith('Cookie') and
                not text.startswith('Subscribe') and
                not text.startswith('Sign up') and
                not text.startswith('Follow us') and
                'javascript' not in text.lower() and
                'browser' not in text.lower() and
                'cookies' not in text.lower()):
                all_paragraphs.append(text)
        
        # Return the paragraphs if we have substantial content
        if len(all_paragraphs) >= 3:
            return ' '.join(all_paragraphs)
        
        return ""
    
    def _extract_from_json_ld(self, soup):
        """Extract article text from JSON-LD structured data"""
        try:
            json_scripts = soup.find_all('script', type='application/ld+json')
            
            for script in json_scripts:
                try:
                    data = json.loads(script.string)
                    
                    # Handle both single objects and arrays
                    if isinstance(data, list):
                        data = data[0]
                    
                    # Look for article body in common locations
                    article_body = None
                    
                    if '@type' in data and 'Article' in str(data.get('@type')):
                        article_body = data.get('articleBody') or data.get('text')
                    
                    if not article_body and 'mainEntity' in data:
                        article_body = data['mainEntity'].get('text')
                    
                    if article_body and len(article_body) > 200:
                        return article_body
                        
                except:
                    continue
        except:
            pass
        
        return None
    
    def _extract_aggressive(self, url):
        """Aggressive extraction using text density analysis"""
        response = self.session.get(url, timeout=45, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        domain = urlparse(url).netloc.replace('www.', '')
        
        # Remove noise
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
            tag.decompose()
        
        title = self._extract_title(soup)
        
        # Text density based extraction
        text = self._extract_by_text_density(soup)
        
        author = self._extract_author_ultimate(soup, str(soup), title, text, domain)
        publish_date = self._extract_date(soup)
        
        return {
            'title': title,
            'text': text,
            'author': author,
            'publish_date': publish_date,
            'url': url,
            'domain': domain
        }
    
    def _extract_by_text_density(self, soup):
        """Extract content based on text density analysis"""
        # Find all div, section, and article tags
        containers = soup.find_all(['div', 'section', 'article'])
        
        best_container = None
        best_score = 0
        
        for container in containers:
            # Skip if too high in hierarchy
            if container.name == 'div' and not container.get('class'):
                continue
            
            # Calculate text density score
            text = container.get_text().strip()
            if len(text) < 200:
                continue
            
            # Count paragraphs and sentences
            paragraphs = container.find_all('p')
            sentences = text.count('.') + text.count('!') + text.count('?')
            
            # Score based on text length, paragraph count, and sentence count
            score = len(text) + (len(paragraphs) * 100) + (sentences * 10)
            
            # Penalty for too many links or ads
            links = container.find_all('a')
            if len(links) > len(paragraphs) * 2:
                score *= 0.5
            
            if score > best_score:
                best_score = score
                best_container = container
        
        if best_container:
            paragraphs = best_container.find_all(['p', 'h2', 'h3', 'h4'])
            texts = []
            
            for p in paragraphs:
                text = p.get_text().strip()
                if text and len(text) > 20:
                    texts.append(text)
            
            return ' '.join(texts)
        
        return ""
    
    def _extract_with_trafilatura(self, url):
        """Use trafilatura library if available"""
        if not TRAFILATURA_AVAILABLE:
            raise ValueError("Trafilatura not available")
        
        try:
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                raise ValueError("Failed to download")
            
            text = trafilatura.extract(downloaded, include_comments=False, 
                                     include_tables=False, deduplicate=True)
            
            if not text:
                raise ValueError("No text extracted")
            
            # Also extract metadata
            metadata = trafilatura.extract_metadata(downloaded)
            
            domain = urlparse(url).netloc.replace('www.', '')
            
            return {
                'title': metadata.title if metadata else self._extract_title_from_text(text),
                'text': text,
                'author': metadata.author if metadata else None,
                'publish_date': metadata.date if metadata else None,
                'url': url,
                'domain': domain
            }
        except Exception as e:
            raise ValueError(f"Trafilatura extraction failed: {str(e)}")
    
    def _extract_with_readability(self, url):
        """Use readability library if available"""
        if not READABILITY_AVAILABLE:
            raise ValueError("Readability not available")
        
        try:
            response = self.session.get(url, timeout=45)
            response.raise_for_status()
            
            doc = Readability(response.text, url)
            article = doc.summary()
            
            soup = BeautifulSoup(article, 'html.parser')
            text = soup.get_text().strip()
            
            if not text or len(text) < 200:
                raise ValueError("Insufficient content")
            
            # Parse full page for metadata
            full_soup = BeautifulSoup(response.text, 'html.parser')
            
            domain = urlparse(url).netloc.replace('www.', '')
            
            return {
                'title': doc.title(),
                'text': text,
                'author': self._extract_author_ultimate(full_soup, response.text, doc.title(), text, domain),
                'publish_date': self._extract_date(full_soup),
                'url': url,
                'domain': domain
            }
        except Exception as e:
            raise ValueError(f"Readability extraction failed: {str(e)}")
    
    def _extract_emergency(self, url):
        """Emergency extraction - get whatever we can"""
        try:
            # Try with different headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                'Accept': '*/*'
            }
            
            response = requests.get(url, headers=headers, timeout=60, allow_redirects=True)
            
            if response.status_code != 200:
                raise ValueError(f"Status code: {response.status_code}")
            
            # Basic BeautifulSoup parsing
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get any text we can find
            title = (soup.find('title').get_text() if soup.find('title') else '') or 'Article'
            
            # Get all text, filter short lines
            all_text = []
            for element in soup.find_all(['p', 'div', 'span', 'article', 'section']):
                text = element.get_text().strip()
                if len(text) > 50:
                    all_text.append(text)
            
            # Deduplicate and join
            seen = set()
            unique_text = []
            for text in all_text:
                if text not in seen:
                    seen.add(text)
                    unique_text.append(text)
            
            final_text = ' '.join(unique_text[:100])  # Limit to first 100 blocks
            
            if len(final_text) < 100:
                raise ValueError("Could not extract sufficient text")
            
            domain = urlparse(url).netloc.replace('www.', '')
            
            return {
                'title': title,
                'text': final_text,
                'author': None,  # Don't waste time on author in emergency mode
                'publish_date': None,
                'url': url,
                'domain': domain
            }
            
        except Exception as e:
            raise ValueError(f"Emergency extraction failed: {str(e)}")
    
    def _create_fallback_result(self, url):
        """Create a fallback result when all extraction methods fail"""
        domain = urlparse(url).netloc.replace('www.', '')
        
        return {
            'title': f'Article from {domain}',
            'text': f'Unable to extract article content from {url}. The page may require JavaScript, be behind a paywall, or have an unusual structure. Please try copying and pasting the article text directly.',
            'author': None,
            'publish_date': None,
            'url': url,
            'domain': domain,
            'extraction_failed': True
        }
    
    # Keep all existing methods below (_extract_title, _extract_text, _extract_author_ultimate, etc.)
    # These remain unchanged to preserve compatibility
    
    def _extract_title(self, soup):
        """Extract article title - original implementation"""
        # Try Open Graph title first
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        
        # Try Twitter title
        twitter_title = soup.find('meta', {'name': 'twitter:title'})
        if twitter_title and twitter_title.get('content'):
            return twitter_title['content'].strip()
        
        # Try article title
        article_title = soup.find('meta', {'name': 'title'})
        if article_title and article_title.get('content'):
            return article_title['content'].strip()
        
        # Try h1 tags
        h1_tags = soup.find_all('h1')
        for h1 in h1_tags:
            title = h1.get_text().strip()
            if title and len(title) > 10:
                # Clean up the title
                title = re.sub(r'\s+', ' ', title)
                # Remove common suffixes
                for suffix in [' - CNN', ' | CNN', ' - BBC', ' | BBC', ' - Reuters', ' | Reuters',
                             ' - The New York Times', ' | The New York Times', ' - The Guardian',
                             ' | The Guardian', ' - Fox News', ' | Fox News', ' | NBC News']:
                    if title.endswith(suffix):
                        title = title[:-len(suffix)]
                
                # Remove "Share" and similar words at the end
                title = re.sub(r'\s*(Share|Tweet|Email|Print|Comment).*$', '', title)
                return title
        
        # Fall back to page title
        if soup.title:
            title = soup.title.string
            if title:
                # Clean up site name from title
                title = title.strip()
                # Remove common separators and everything after them
                for separator in [' - ', ' | ', ' — ', ' :: ', ' » ']:
                    if separator in title:
                        title = title.split(separator)[0].strip()
                
                # Remove trailing "Share" etc.
                title = re.sub(r'\s*(Share|Tweet|Email|Print|Comment).*$', '', title)
                return title
        
        return 'No title found'
    
    def _extract_text(self, soup, url):
        """Extract main article text - original implementation"""
        # Remove script and style elements
        for script in soup(['script', 'style', 'noscript']):
            script.decompose()
        
        # Remove navigation, header, footer elements
        for elem in soup(['nav', 'header', 'footer', 'aside']):
            elem.decompose()
        
        # Try to find article body with common selectors
        article_selectors = [
            'article',
            '[role="main"]',
            'main',
            '[class*="article-body"]',
            '[class*="story-body"]', 
            '[class*="content-body"]',
            '[class*="post-body"]',
            '[class*="entry-content"]',
            '[class*="article-content"]',
            '[class*="story-content"]',
            '[id*="article-body"]',
            '[id*="story-body"]',
            '.content',
            '#content',
            '.story',
            '.post',
            '.article'
        ]
        
        article_text = ""
        
        for selector in article_selectors:
            article = soup.select_one(selector)
            if article:
                # Get all paragraphs
                paragraphs = article.find_all(['p', 'h2', 'h3', 'h4', 'blockquote'])
                if paragraphs:
                    texts = []
                    for p in paragraphs:
                        # Skip if paragraph contains navigation/menu items
                        if p.find_parent(['nav', 'menu']):
                            continue
                        text = p.get_text().strip()
                        if text and len(text) > 20:
                            texts.append(text)
                    
                    if texts:
                        article_text = ' '.join(texts)
                        if len(article_text) > 200:  # Substantial content found
                            break
        
        # Fallback: get all paragraphs if no article container found
        if not article_text or len(article_text) < 200:
            paragraphs = soup.find_all('p')
            texts = []
            for p in paragraphs[:100]:  # Limit to first 100 paragraphs
                # Skip short paragraphs and navigation items
                if p.find_parent(['nav', 'menu', 'header', 'footer']):
                    continue
                text = p.get_text().strip()
                if text and len(text) > 50:
                    texts.append(text)
            
            article_text = ' '.join(texts)
        
        return article_text if article_text else 'No article text found'
    
    def _extract_date(self, soup):
        """Extract publish date - original implementation"""
        date_selectors = [
            ('meta', {'property': 'article:published_time'}),
            ('meta', {'name': 'publish_date'}),
            ('meta', {'property': 'datePublished'}),
            ('meta', {'name': 'publication_date'}),
            ('meta', {'name': 'DC.date.issued'}),
            ('meta', {'name': 'date'}),
            ('meta', {'itemprop': 'datePublished'}),
            ('meta', {'name': 'article:published_time'}),
            ('time', {'datetime': True}),
            ('time', {'pubdate': True}),
            ('[itemprop="datePublished"]', None),
            ('[property="datePublished"]', None),
            ('[class*="publish-date"]', None),
            ('[class*="published-date"]', None),
            ('[class*="article-date"]', None),
            ('[class*="post-date"]', None),
            ('[class*="entry-date"]', None)
        ]
        
        for selector, attrs in date_selectors:
            if attrs:
                elements = soup.find_all(selector, attrs)
            else:
                elements = soup.select(selector)
                
            for element in elements:
                date_str = None
                
                if element.name == 'meta':
                    date_str = element.get('content')
                elif element.name == 'time':
                    date_str = element.get('datetime') or element.get_text()
                else:
                    date_str = element.get_text()
                
                if date_str:
                    date_str = date_str.strip()
                    # Try to parse the date
                    try:
                        # Handle ISO format
                        if 'T' in date_str:
                            return date_str.split('T')[0]
                        # Return as is if it looks like a date
                        if any(char in date_str for char in ['-', '/', '.']) and any(char.isdigit() for char in date_str):
                            return date_str
                    except:
                        continue
        
        return None
    
    def _extract_author_emergency(self, soup, html_text, domain):
        """Emergency author extraction when all else fails"""
        logger.info("🚨 EMERGENCY AUTHOR EXTRACTION")
        
        # Try to find any text that looks like a byline
        potential_authors = []
        
        # Look for any element containing common name patterns
        all_elements = soup.find_all(text=re.compile(r'[A-Z][a-z]+\s+[A-Z][a-z]+'))
        
        for element in all_elements[:50]:  # Check first 50 matches
            if isinstance(element, NavigableString):
                parent = element.parent
                if parent and parent.name not in ['script', 'style', 'title']:
                    text = str(element).strip()
                    
                    # Look for name patterns
                    name_matches = re.findall(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})', text)
                    
                    for match in name_matches:
                        if self._is_valid_author_name(match):
                            # Check context
                            full_text = parent.get_text().strip()
                            if len(full_text) < 200:  # Likely a byline, not article text
                                potential_authors.append(match)
        
        # Deduplicate and return most common
        if potential_authors:
            from collections import Counter
            author_counts = Counter(potential_authors)
            most_common = author_counts.most_common(1)[0][0]
            logger.info(f"  Emergency extraction found: {most_common}")
            return most_common
        
        return None
    
    def _extract_title_from_text(self, text):
        """Extract title from article text as fallback"""
        if not text:
            return "Article"
        
        # Try to find first sentence or heading-like text
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and 10 < len(line) < 200:
                return line
        
        # Fallback to first 100 chars
        return text[:100] + "..." if len(text) > 100 else text
    
    def _extract_author_ultimate(self, soup, html_text, title, article_text, domain):
        """ULTIMATE author extraction using every conceivable method"""
        
        logger.info("🔍 ULTIMATE AUTHOR EXTRACTION ENGAGED")
        
        # Store all candidates with confidence scores
        author_candidates = {}  # author -> confidence score
        
        # METHOD 0: Domain-specific patterns (BBC, CNN, etc.)
        domain_patterns = {
            'bbc.com': [
                r'By\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'<span class="byline__name">([^<]+)</span>',
                r'<p class="contributor__name">([^<]+)</p>'
            ],
            'cnn.com': [
                r'class="byline__name">([^<]+)</span>',
                r'class="metadata__byline__author">([^<]+)</span>',
                r'"author":\s*{\s*"name":\s*"([^"]+)"'
            ],
            'reuters.com': [
                r'By\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'class="author-name">([^<]+)',
                r'"author":\s*"([^"]+)"'
            ],
            'nytimes.com': [
                r'class="byline__name">([^<]+)',
                r'"author":\s*{\s*"name":\s*"([^"]+)"',
                r'By\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
            ],
            'politico.com': [
                r'class="story-meta__authors">([^<]+)</p>',
                r'class="byline">([^<]+)</span>',
                r'class="vcard">([^<]+)</span>',
                r'itemprop="author"[^>]*>([^<]+)<',
                r'rel="author"[^>]*>([^<]+)<',
                r'"authors":\s*\[([^\]]+)\]',
                r'"author":\s*{\s*"name":\s*"([^"]+)"',
                r'By\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*(?:and|,)',
                r'<a[^>]+href="[^"]*\/staff\/[^"]*"[^>]*>([^<]+)</a>'
            ],
            'washingtonpost.com': [
                r'class="author-name">([^<]+)',
                r'rel="author">([^<]+)</a>',
                r'"author":\s*{\s*"name":\s*"([^"]+)"'
            ],
            'theguardian.com': [
                r'rel="author">([^<]+)</a>',
                r'class="byline">([^<]+)</span>',
                r'"author":\s*{\s*"name":\s*"([^"]+)"'
            ],
            'foxnews.com': [
                r'class="author-byline">([^<]+)',
                r'class="author">([^<]+)',
                r'"author":\s*"([^"]+)"'
            ],
            'npr.org': [
                r'class="byline__name">([^<]+)',
                r'By\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'"author":\s*{\s*"name":\s*"([^"]+)"'
            ],
            'wsj.com': [
                r'class="byline">([^<]+)',
                r'class="author-name">([^<]+)',
                r'"author":\s*{\s*"name":\s*"([^"]+)"'
            ],
            'bloomberg.com': [
                r'class="author">([^<]+)',
                r'rel="author">([^<]+)',
                r'"author":\s*{\s*"name":\s*"([^"]+)"'
            ],
            'apnews.com': [
                r'By\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'class="Component-bylines">([^<]+)',
                r'"author":\s*"([^"]+)"'
            ]
        }
        
        if domain in domain_patterns:
            for pattern in domain_patterns[domain]:
                matches = re.findall(pattern, html_text)
                for match in matches:
                    author = self._clean_author_name(match)
                    if author and self._is_valid_author_name(author):
                        author_candidates[author] = author_candidates.get(author, 0) + 10
        
        # Continue with all other methods from original implementation...
        # [Rest of the _extract_author_ultimate method remains the same]
        
        # METHOD 1: JSON-LD structured data
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                self._extract_author_from_json_ld(data, author_candidates)
            except:
                continue
        
        # METHOD 2: Meta tags
        meta_selectors = [
            ('meta', {'name': 'author'}),
            ('meta', {'property': 'author'}),
            ('meta', {'name': 'article:author'}),
            ('meta', {'property': 'article:author'}),
            ('meta', {'name': 'byl'}),
            ('meta', {'name': 'DC.creator'}),
            ('meta', {'name': 'citation_author'}),
            ('meta', {'property': 'og:article:author'}),
            ('meta', {'itemprop': 'author'}),
            ('meta', {'name': 'twitter:creator'}),
            ('meta', {'name': 'sailthru.author'}),
            ('meta', {'name': 'parsely-author'})
        ]
        
        for tag, attrs in meta_selectors:
            elements = soup.find_all(tag, attrs)
            for element in elements:
                content = element.get('content', '')
                if content:
                    author = self._clean_author_name(content)
                    if author and self._is_valid_author_name(author):
                        author_candidates[author] = author_candidates.get(author, 0) + 8
        
        # METHOD 3: Common byline patterns
        byline_selectors = [
            '[class*="author"]', '[class*="byline"]', '[class*="writer"]',
            '[class*="reporter"]', '[class*="contributor"]', '[class*="journalist"]',
            '[class*="by-line"]', '[class*="article-author"]', '[class*="post-author"]',
            '[class*="entry-author"]', '[class*="news-author"]', '[class*="story-author"]',
            '[id*="author"]', '[id*="byline"]', '[itemprop="author"]',
            '[rel="author"]', '[data-author]', '[data-byline]',
            'address', '.by', '.writtenby', '.author-name', '.author-info',
            '.byline-name', '.contributor', '.story-byline', '.article-byline',
            '.content-author', '.post-meta-author', '.entry-meta-author',
            # Add more specific selectors
            '.story-meta__authors', '.story-meta', '.metadata', '.meta-author',
            '.article-meta', '.post-meta', '.entry-meta', '.content-meta',
            'span.vcard', 'p.vcard', 'div.vcard', '.h-card',
            '[class*="meta"] [class*="author"]', '[class*="meta"] a[href*="/staff/"]',
            'a[href*="/author/"]', 'a[href*="/authors/"]', 'a[href*="/staff/"]',
            'a[href*="/people/"]', 'a[href*="/contributors/"]'
        ]
        
        for selector in byline_selectors:
            try:
                elements = soup.select(selector)
                for element in elements[:10]:
                    text = element.get_text().strip()
                    
                    # Clean and extract author name
                    author = self._extract_author_from_byline(text)
                    if author and self._is_valid_author_name(author):
                        # Higher score for more specific selectors
                        score = 7 if 'author' in selector.lower() else 5
                        author_candidates[author] = author_candidates.get(author, 0) + score
            except:
                continue
        
        # METHOD 4: "By" pattern in text
        by_patterns = [
            r'[Bb]y\s+([A-Z][a-z]+(?:\s+[A-Z\'][a-z]+){1,3})',
            r'[Ww]ritten\s+by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
            r'[Rr]eported\s+by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
            r'[Aa]uthor:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
            r'[Bb]y:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})',
            r'–\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\s*$',
            r'—\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\s*$'
        ]
        
        # Search in HTML
        for pattern in by_patterns:
            matches = re.findall(pattern, html_text[:5000])  # Check first 5000 chars
            for match in matches:
                author = self._clean_author_name(match)
                if author and self._is_valid_author_name(author):
                    author_candidates[author] = author_candidates.get(author, 0) + 6
        
        # METHOD 5: Link patterns
        author_link_patterns = [
            r'/author/([^/"]+)',
            r'/authors/([^/"]+)',
            r'/profile/([^/"]+)',
            r'/contributor/([^/"]+)',
            r'/staff/([^/"]+)',
            r'/people/([^/"]+)',
            r'/by/([^/"]+)',
            r'/writer/([^/"]+)'
        ]
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag.get('href', '')
            for pattern in author_link_patterns:
                match = re.search(pattern, href)
                if match:
                    author_slug = match.group(1)
                    # Try to get name from link text
                    link_text = a_tag.get_text().strip()
                    if link_text and self._is_valid_author_name(link_text):
                        author_candidates[link_text] = author_candidates.get(link_text, 0) + 4
                    # Also try to convert slug to name
                    elif author_slug:
                        name = author_slug.replace('-', ' ').title()
                        if self._is_valid_author_name(name):
                            author_candidates[name] = author_candidates.get(name, 0) + 3
        
        # METHOD 6: Email pattern for author
        email_pattern = r'([a-zA-Z0-9._%+-]+)@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email_matches = re.findall(email_pattern, html_text[:3000])
        for email_user in email_matches[:5]:
            # Convert email username to potential name
            name_parts = re.split(r'[._-]', email_user)
            if len(name_parts) >= 2:
                potential_name = ' '.join(part.capitalize() for part in name_parts[:2])
                if self._is_valid_author_name(potential_name):
                    author_candidates[potential_name] = author_candidates.get(potential_name, 0) + 2
        
        # METHOD 7: Schema.org microdata
        schema_selectors = [
            '[itemtype*="schema.org/Person"]',
            '[itemtype*="schema.org/Author"]',
            '[typeof="Person"]',
            '[typeof="Author"]'
        ]
        
        for selector in schema_selectors:
            elements = soup.select(selector)
            for element in elements:
                name_elem = element.select_one('[itemprop="name"]')
                if name_elem:
                    author = self._clean_author_name(name_elem.get_text())
                    if author and self._is_valid_author_name(author):
                        author_candidates[author] = author_candidates.get(author, 0) + 7
        
        # METHOD 8: Specific class/id patterns that often contain authors
        specific_patterns = [
            ('span', {'class': re.compile(r'by__author|article__author-name|post-author-name')}),
            ('div', {'class': re.compile(r'author-bio|author-info|writer-info')}),
            ('p', {'class': re.compile(r'author|byline|writer')}),
            ('cite', {}),  # Often used for attributions
            ('address', {})  # Sometimes used for author info
        ]
        
        for tag, attrs in specific_patterns:
            elements = soup.find_all(tag, attrs)
            for element in elements:
                text = element.get_text().strip()
                author = self._extract_author_from_byline(text)
                if author and self._is_valid_author_name(author):
                    author_candidates[author] = author_candidates.get(author, 0) + 5
        
        # METHOD 9: Check near "by" in clean text
        if article_text:
            first_500_chars = article_text[:500]
            for pattern in by_patterns:
                matches = re.findall(pattern, first_500_chars)
                for match in matches:
                    author = self._clean_author_name(match)
                    if author and self._is_valid_author_name(author):
                        author_candidates[author] = author_candidates.get(author, 0) + 5
        
        # METHOD 10: Twitter meta tag
        twitter_creator = soup.find('meta', {'name': 'twitter:creator'})
        if twitter_creator and twitter_creator.get('content'):
            twitter_handle = twitter_creator['content'].strip()
            # Try to extract real name from nearby elements
            # or just use the handle as a last resort
            if twitter_handle.startswith('@'):
                twitter_handle = twitter_handle[1:]
            author_candidates[f"@{twitter_handle}"] = author_candidates.get(f"@{twitter_handle}", 0) + 1
        
        # METHOD 11: Aggressive link-based extraction
        logger.info("🔗 METHOD 11: Aggressive link extraction")
        
        # Look for any links that might contain author info
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text().strip()
            
            # Check if link points to author/staff page
            if any(pattern in href.lower() for pattern in ['/author/', '/authors/', '/staff/', '/people/', '/contributors/', '/profile/', '/bio/']):
                if text and self._is_valid_author_name(text):
                    author_candidates[text] = author_candidates.get(text, 0) + 6
                    logger.info(f"  Found via author link: {text}")
            
            # Check parent elements for byline context
            parent = link.parent
            if parent:
                parent_text = parent.get_text().strip()
                if any(indicator in parent_text.lower() for indicator in ['by', 'author', 'written', 'reported']):
                    if text and self._is_valid_author_name(text):
                        author_candidates[text] = author_candidates.get(text, 0) + 7
                        logger.info(f"  Found via parent context: {text}")
        
        # METHOD 12: Deep text search in first part of article
        logger.info("📝 METHOD 12: Deep text pattern search")
        
        # Get first 1000 chars of clean text
        all_text = soup.get_text()[:3000]
        
        # More aggressive patterns
        deep_patterns = [
            r'(?:By|FROM|BY)\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})(?:\s*[,\n\r])',
            r'(?:Written by|Reported by|WRITTEN BY)\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})',
            r'^([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})\s+(?:is|writes|reports)',
            r'(?:Story by|STORY BY)\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})',
            r'([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})\s+\|\s+\d{1,2}[/\.]\d{1,2}',
            r'([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})\s+Updated:',
            r'Contact\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})\s+at'
        ]
        
        for pattern in deep_patterns:
            matches = re.findall(pattern, all_text, re.MULTILINE)
            for match in matches:
                author = self._clean_author_name(match)
                if author and self._is_valid_author_name(author):
                    author_candidates[author] = author_candidates.get(author, 0) + 4
                    logger.info(f"  Found via deep text search: {author}")
        
        # Select best candidate
        if author_candidates:
            # Sort by score and name quality
            sorted_candidates = sorted(
                author_candidates.items(),
                key=lambda x: (x[1], len(x[0].split()), -len(x[0])),
                reverse=True
            )
            
            best_author = sorted_candidates[0][0]
            logger.info(f"✅ Author found: {best_author} (score: {sorted_candidates[0][1]})")
            logger.info(f"All candidates: {sorted_candidates[:5]}")
            return best_author
        
        logger.warning("❌ No author found")
        return None
    
    def _extract_author_from_json_ld(self, data, author_candidates):
        """Extract author from JSON-LD data"""
        if isinstance(data, dict):
            # Direct author field
            if 'author' in data:
                author_data = data['author']
                if isinstance(author_data, str):
                    author = self._clean_author_name(author_data)
                    if author and self._is_valid_author_name(author):
                        author_candidates[author] = author_candidates.get(author, 0) + 10
                elif isinstance(author_data, dict):
                    name = author_data.get('name', '')
                    if name:
                        author = self._clean_author_name(name)
                        if author and self._is_valid_author_name(author):
                            author_candidates[author] = author_candidates.get(author, 0) + 10
                elif isinstance(author_data, list):
                    for auth in author_data:
                        if isinstance(auth, dict):
                            name = auth.get('name', '')
                        else:
                            name = str(auth)
                        if name:
                            author = self._clean_author_name(name)
                            if author and self._is_valid_author_name(author):
                                author_candidates[author] = author_candidates.get(author, 0) + 10
            
            # Check nested structures
            for key in ['mainEntity', 'mainEntityOfPage', '@graph']:
                if key in data:
                    self._extract_author_from_json_ld(data[key], author_candidates)
        
        elif isinstance(data, list):
            for item in data:
                self._extract_author_from_json_ld(item, author_candidates)
    
    def _extract_author_from_byline(self, text):
        """Extract author name from byline text"""
        if not text or len(text) > 200:
            return None
        
        # Remove common prefixes
        text = re.sub(r'^(By|Written by|Reported by|Author:|By:|Contributor:|Posted by|Published by)\s*', '', text, flags=re.I)
        text = re.sub(r'^(By|by)\s+', '', text)
        
        # Remove dates, times, and common suffixes
        text = re.sub(r'\d{1,2}[/:]\d{1,2}[/:]\d{2,4}.*$', '', text)
        text = re.sub(r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).*$', '', text, flags=re.I)
        text = re.sub(r'(Posted|Published|Updated|Modified).*$', '', text, flags=re.I)
        text = re.sub(r'\|.*$', '', text)
        text = re.sub(r'\s+[-–—]\s+.*$', '', text)
        
        # Extract name part
        text = text.strip()
        
        # Skip if it's too long or too short
        if len(text) < 3 or len(text) > 50:
            return None
        
        # Skip if it contains certain words
        skip_words = ['share', 'tweet', 'email', 'print', 'comment', 'subscribe', 
                     'follow', 'advertisement', 'sponsored', 'promoted']
        if any(word in text.lower() for word in skip_words):
            return None
        
        return text
    
    def _clean_author_name(self, name):
        """Clean and normalize author name"""
        if not name:
            return None
        
        # Basic cleaning
        name = str(name).strip()
        name = re.sub(r'\s+', ' ', name)
        
        # Remove common suffixes/prefixes
        name = re.sub(r'^(By|Written by|Reported by|Author:|By:|Staff|Reporter|Correspondent)\s*', '', name, flags=re.I)
        name = re.sub(r'\s*(Staff|Reporter|Correspondent|Writer|Contributor|Editor|Journalist)$', '', name, flags=re.I)
        
        # Remove email
        name = re.sub(r'\S+@\S+', '', name)
        
        # Remove URLs
        name = re.sub(r'https?://\S+', '', name)
        
        # Remove special characters but keep apostrophes and hyphens in names
        name = re.sub(r'[^\w\s\'-]', ' ', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Remove trailing numbers
        name = re.sub(r'\s*\d+$', '', name)
        
        # Handle "and" for multiple authors
        if ' and ' in name.lower():
            # Take the first author
            name = name.split(' and ')[0].strip()
        
        return name if name else None
    
    def _is_valid_author_name(self, name):
        """Validate if the extracted text is likely an author name"""
        if not name or len(name) < 3 or len(name) > 50:
            return False
        
        # Must contain at least one letter
        if not any(c.isalpha() for c in name):
            return False
        
        # Skip if it's all caps (might be a section header)
        if name.isupper() and len(name.split()) > 2:
            return False
        
        # Skip common non-name phrases
        skip_phrases = [
            'click here', 'read more', 'share this', 'follow us', 'sign up',
            'subscribe', 'newsletter', 'breaking news', 'exclusive', 'update',
            'advertisement', 'sponsored', 'staff', 'admin', 'editor',
            'associated press', 'reuters', 'staff writer', 'guest post',
            'press release', 'news desk', 'web desk', 'news service',
            'digital team', 'online team', 'newsroom', 'editorial'
        ]
        
        name_lower = name.lower()
        if any(phrase in name_lower for phrase in skip_phrases):
            return False
        
        # Check if it contains organization names
        org_keywords = ['news', 'media', 'press', 'agency', 'network', 'broadcasting',
                       'corporation', 'company', 'institute', 'organization', 'group']
        
        # If has org keywords and is not a known journalist, likely invalid
        if any(keyword in name_lower for keyword in org_keywords):
            # But allow if it's part of a person's title like "News Reporter John Smith"
            parts = name.split()
            if len(parts) < 2:
                return False
        
        # Must have at least first and last name (with some exceptions)
        parts = name.split()
        if len(parts) < 2:
            # Allow single names if they're in our known names
            if name_lower not in self.common_first_names and name_lower not in self.common_last_names:
                # Exception for known single-name journalists or foreign names
                if not (len(name) > 5 and name[0].isupper()):
                    return False
        
        # Check if at least one part is a common name
        has_common_name = False
        for part in parts:
            part_lower = part.lower().strip("'").strip("-")
            if part_lower in self.common_first_names or part_lower in self.common_last_names:
                has_common_name = True
                break
        
        # If no common names found, be more strict
        if not has_common_name and len(parts) >= 2:
            # At least require proper capitalization
            for part in parts:
                if part and not part[0].isupper() and part not in ['van', 'de', 'la', 'von', 'der']:
                    return False
        
        return True
