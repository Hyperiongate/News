# services/article_extractor.py
"""
Article Extractor Service
Extracts and processes article content from URLs
"""

import re
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class ArticleExtractor:
    """
    Extract article content from URLs
    This is a wrapper around NewsExtractor for backward compatibility
    but can also work standalone
    """
    
    def __init__(self):
        """Initialize the article extractor"""
        self.timeout = 10
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Try to import NewsExtractor if available
        self.news_extractor = None
        try:
            from .news_extractor import NewsExtractor
            self.news_extractor = NewsExtractor()
        except ImportError:
            logger.warning("NewsExtractor not available, using basic extraction")
    
    def extract(self, url: str) -> Dict[str, Any]:
        """
        Extract article content from URL
        
        Args:
            url: URL of the article to extract
            
        Returns:
            Dictionary containing article data or error
        """
        # Use NewsExtractor if available
        if self.news_extractor:
            result = self.news_extractor.extract_article(url)
            # Ensure all expected fields exist
            return self._normalize_result(result)
        
        # Otherwise use basic extraction
        try:
            # Validate URL
            if not url or not self._is_valid_url(url):
                return {'error': 'Invalid URL provided'}
            
            # Fetch the page
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract article data
            article_data = {
                'url': url,
                'title': self._extract_title(soup),
                'author': self._extract_author(soup),
                'date': self._extract_date(soup),
                'content': self._extract_content(soup),
                'excerpt': '',
                'images': self._extract_images(soup, url),
                'domain': urlparse(url).netloc.replace('www.', ''),
                'html': str(soup),
                'success': True
            }
            
            # Process content
            if article_data['content']:
                article_data['text'] = article_data['content']  # Alias for compatibility
                article_data['word_count'] = len(article_data['content'].split())
                article_data['reading_time'] = max(1, article_data['word_count'] // 200)
                article_data['excerpt'] = self._create_excerpt(article_data['content'])
                article_data['language'] = self._detect_language(article_data['content'])
            else:
                article_data['word_count'] = 0
                article_data['reading_time'] = 0
                article_data['language'] = 'en'
            
            # Extract additional metadata
            article_data['keywords'] = self._extract_keywords(soup)
            article_data['categories'] = self._extract_categories(soup)
            article_data['tags'] = self._extract_tags(soup)
            article_data['links'] = self._extract_links(soup, url)
            
            return article_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error extracting article: {e}")
            return {'error': f'Network error: {str(e)}'}
        except Exception as e:
            logger.error(f"Error extracting article: {e}")
            return {'error': f'Extraction failed: {str(e)}'}
    
    def _normalize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize result to ensure all expected fields exist"""
        if result.get('error'):
            return result
        
        # Ensure all fields exist
        normalized = {
            'url': result.get('url', ''),
            'title': result.get('title', 'Unknown Title'),
            'author': result.get('author', 'Unknown'),
            'date': result.get('date') or result.get('publish_date'),
            'domain': result.get('domain', ''),
            'content': result.get('content') or result.get('text', ''),
            'text': result.get('text') or result.get('content', ''),
            'excerpt': result.get('excerpt', ''),
            'images': result.get('images', []),
            'word_count': result.get('word_count', 0),
            'reading_time': result.get('reading_time', 0),
            'language': result.get('language', 'en'),
            'keywords': result.get('keywords', []),
            'categories': result.get('categories', []),
            'tags': result.get('tags', []),
            'links': result.get('links', []),
            'html': result.get('html', ''),
            'success': True
        }
        
        # Create excerpt if missing
        if not normalized['excerpt'] and normalized['content']:
            normalized['excerpt'] = self._create_excerpt(normalized['content'])
        
        # Calculate word count and reading time if missing
        if normalized['content'] and not normalized['word_count']:
            normalized['word_count'] = len(normalized['content'].split())
            normalized['reading_time'] = max(1, normalized['word_count'] // 200)
        
        # Extract domain if missing
        if not normalized['domain'] and normalized['url']:
            normalized['domain'] = urlparse(normalized['url']).netloc.replace('www.', '')
        
        return normalized
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title"""
        # Try multiple selectors
        selectors = [
            'h1',
            'title',
            'meta[property="og:title"]',
            'meta[name="twitter:title"]',
            '.article-title',
            '.entry-title',
            '#article-title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    return element.get('content', '').strip()
                else:
                    return element.get_text().strip()
        
        return 'Unknown Title'
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """Extract article author"""
        # Try multiple selectors
        selectors = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            'meta[name="byl"]',
            '.author-name',
            '.by-author',
            '.article-author',
            'span[itemprop="author"]',
            'div[itemprop="author"]',
            '.byline'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    author = element.get('content', '').strip()
                else:
                    author = element.get_text().strip()
                
                # Clean up author name
                author = re.sub(r'^\s*by\s+', '', author, flags=re.IGNORECASE)
                author = author.strip()
                
                if author and len(author) > 2:
                    return author
        
        return 'Unknown'
    
    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract publication date"""
        # Try multiple selectors
        selectors = [
            'meta[property="article:published_time"]',
            'meta[name="publish_date"]',
            'time[datetime]',
            'time[pubdate]',
            '.publish-date',
            '.article-date',
            '.entry-date'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    date_str = element.get('content', '')
                elif element.name == 'time':
                    date_str = element.get('datetime', element.get_text())
                else:
                    date_str = element.get_text()
                
                # Try to parse date
                try:
                    # Simple date parsing - in production use dateutil
                    return date_str.strip()
                except:
                    continue
        
        return None
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main article content"""
        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Try to find article body
        content_selectors = [
            'article',
            '[role="main"]',
            '.article-body',
            '.article-content',
            '.entry-content',
            '.post-content',
            '#article-body',
            '.story-body'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                # Extract paragraphs
                paragraphs = element.find_all('p')
                if paragraphs:
                    content = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                    if len(content) > 100:
                        return content
        
        # Fallback: get all paragraphs
        paragraphs = soup.find_all('p')
        content = ' '.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 50])
        
        return content
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract article images"""
        images = []
        
        # Try to find main image
        main_image_selectors = [
            'meta[property="og:image"]',
            'meta[name="twitter:image"]',
            '.article-image img',
            '.featured-image img',
            'article img'
        ]
        
        for selector in main_image_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    img_url = element.get('content', '')
                else:
                    img_url = element.get('src', '')
                
                if img_url:
                    # Make URL absolute
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        parsed = urlparse(base_url)
                        img_url = f"{parsed.scheme}://{parsed.netloc}{img_url}"
                    
                    if img_url not in images:
                        images.append(img_url)
        
        return images
    
    def _create_excerpt(self, content: str, length: int = 200) -> str:
        """Create excerpt from content"""
        if not content:
            return ''
        
        # Clean content
        excerpt = ' '.join(content.split())
        
        # Truncate to length
        if len(excerpt) > length:
            excerpt = excerpt[:length]
            # Try to end at word boundary
            last_space = excerpt.rfind(' ')
            if last_space > length * 0.8:
                excerpt = excerpt[:last_space]
            excerpt += '...'
        
        return excerpt
    
    def _detect_language(self, content: str) -> str:
        """Simple language detection"""
        # Very basic - in production use langdetect or similar
        if not content:
            return 'en'
        
        # Check for common non-English characters
        if re.search(r'[à-ÿ]', content):
            if re.search(r'[àâäæçèéêëîïôùûüÿœ]', content):
                return 'fr'
            elif re.search(r'[áéíóúñ¿¡]', content):
                return 'es'
            elif re.search(r'[äöüß]', content):
                return 'de'
        
        return 'en'
    
    def _extract_keywords(self, soup: BeautifulSoup) -> List[str]:
        """Extract keywords from meta tags"""
        keywords = []
        
        # Try meta keywords
        meta_keywords = soup.select_one('meta[name="keywords"]')
        if meta_keywords:
            content = meta_keywords.get('content', '')
            keywords = [k.strip() for k in content.split(',') if k.strip()]
        
        # Try article tags
        tag_selectors = ['.tags a', '.article-tags a', '.post-tags a']
        for selector in tag_selectors:
            tags = soup.select(selector)
            if tags:
                keywords.extend([tag.get_text().strip() for tag in tags])
                break
        
        # Remove duplicates and limit
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw.lower() not in seen:
                seen.add(kw.lower())
                unique_keywords.append(kw)
        
        return unique_keywords[:10]
    
    def _extract_categories(self, soup: BeautifulSoup) -> List[str]:
        """Extract article categories"""
        categories = []
        
        # Try different category selectors
        selectors = [
            '.category a',
            '.article-category a',
            '.post-category a',
            'nav.breadcrumb a'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                categories = [elem.get_text().strip() for elem in elements if elem.get_text().strip()]
                break
        
        return categories[:5]
    
    def _extract_tags(self, soup: BeautifulSoup) -> List[str]:
        """Extract article tags"""
        # This might overlap with keywords, but kept separate for compatibility
        return self._extract_keywords(soup)
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract external links from article"""
        links = []
        parsed_base = urlparse(base_url)
        
        # Find all links in article content
        article = soup.select_one('article') or soup
        
        for link in article.find_all('a', href=True):
            href = link['href']
            
            # Make absolute URL
            if href.startswith('//'):
                href = 'https:' + href
            elif href.startswith('/'):
                href = f"{parsed_base.scheme}://{parsed_base.netloc}{href}"
            elif not href.startswith(('http://', 'https://')):
                continue
            
            # Check if external
            parsed_link = urlparse(href)
            if parsed_link.netloc and parsed_link.netloc != parsed_base.netloc:
                if href not in links:
                    links.append(href)
        
        return links[:20]  # Limit to 20 links
