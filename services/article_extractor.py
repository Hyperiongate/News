"""
Article Extractor Service - PROFESSIONAL VERSION
Date: 2025-09-28
Purpose: Extract REAL article content for professional analysis

This replaces the broken extractor that returns fallback garbage.
Implements multiple extraction methods with intelligent fallbacks.
"""

import os
import re
import time
import json
import logging
import requests
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    logger.error("BeautifulSoup not available")

try:
    from newspaper import Article as NewspaperArticle
    NEWSPAPER_AVAILABLE = True
except ImportError:
    NEWSPAPER_AVAILABLE = False
    logger.info("Newspaper3k not available - install with: pip install newspaper3k")


class ArticleExtractor:
    """Professional article extraction with multiple methods and quality validation"""
    
    def __init__(self):
        self.service_name = 'article_extractor'
        self.available = True
        self.is_available = True
        
        # API keys
        self.scraperapi_key = os.environ.get('SCRAPERAPI_KEY')
        self.scrapingbee_key = os.environ.get('SCRAPINGBEE_KEY')
        
        # Professional headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        logger.info(f"ArticleExtractor initialized - ScraperAPI: {bool(self.scraperapi_key)}, ScrapingBee: {bool(self.scrapingbee_key)}")
    
    def _check_availability(self) -> bool:
        """Check if service is available"""
        return BS4_AVAILABLE
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract article with multiple methods and quality validation
        RETURNS ACTUAL ARTICLE CONTENT, NOT FALLBACK GARBAGE
        """
        try:
            url = data.get('url')
            if not url:
                logger.error("No URL provided for extraction")
                return self._create_error_response("No URL provided")
            
            logger.info(f"Extracting article from: {url}")
            
            # Try extraction methods in order of reliability
            article_data = None
            extraction_method = None
            
            # Method 1: Newspaper3k (best for article extraction)
            if NEWSPAPER_AVAILABLE and not article_data:
                logger.info("Trying Newspaper3k extraction...")
                article_data = self._extract_with_newspaper(url)
                if article_data:
                    extraction_method = "newspaper3k"
            
            # Method 2: ScraperAPI (handles JavaScript sites)
            if self.scraperapi_key and not article_data:
                logger.info("Trying ScraperAPI extraction...")
                article_data = self._extract_with_scraperapi(url)
                if article_data:
                    extraction_method = "scraperapi"
            
            # Method 3: ScrapingBee (alternative API)
            if self.scrapingbee_key and not article_data:
                logger.info("Trying ScrapingBee extraction...")
                article_data = self._extract_with_scrapingbee(url)
                if article_data:
                    extraction_method = "scrapingbee"
            
            # Method 4: Direct request with BeautifulSoup
            if not article_data:
                logger.info("Trying direct extraction with BeautifulSoup...")
                article_data = self._extract_with_beautifulsoup(url)
                if article_data:
                    extraction_method = "beautifulsoup"
            
            # Method 5: Fallback with requests + smart parsing
            if not article_data:
                logger.info("Trying fallback extraction...")
                article_data = self._extract_with_fallback(url)
                if article_data:
                    extraction_method = "fallback"
            
            # Validate extraction quality
            if article_data and self._validate_extraction(article_data):
                logger.info(f"SUCCESS: Extracted {article_data.get('word_count', 0)} words using {extraction_method}")
                
                # Return ACTUAL article data, not garbage
                return {
                    'success': True,
                    'service': self.service_name,
                    'available': True,
                    'timestamp': time.time(),
                    # CRITICAL: Return the article data directly at root level
                    **article_data,  # Spread article data at root
                    'extraction_method': extraction_method,
                    'extraction_quality': self._calculate_quality_score(article_data)
                }
            else:
                logger.error(f"All extraction methods failed for {url}")
                return self._create_error_response(f"Unable to extract article from {url}")
                
        except Exception as e:
            logger.error(f"Article extraction error: {e}", exc_info=True)
            return self._create_error_response(str(e))
    
    def _extract_with_newspaper(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract using Newspaper3k - best for articles"""
        try:
            article = NewspaperArticle(url)
            article.download()
            article.parse()
            article.nlp()  # Natural language processing for keywords/summary
            
            if not article.text or len(article.text) < 100:
                return None
            
            return {
                'title': article.title or 'Untitled',
                'author': ', '.join(article.authors) if article.authors else 'Unknown',
                'text': article.text,
                'content': article.text,
                'url': url,
                'domain': urlparse(url).netloc.replace('www.', ''),
                'source': urlparse(url).netloc.replace('www.', ''),
                'publish_date': article.publish_date.isoformat() if article.publish_date else None,
                'top_image': article.top_image,
                'keywords': article.keywords[:10] if article.keywords else [],
                'summary': article.summary[:500] if article.summary else '',
                'word_count': len(article.text.split()),
                'extraction_successful': True
            }
            
        except Exception as e:
            logger.error(f"Newspaper extraction failed: {e}")
            return None
    
    def _extract_with_scraperapi(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract using ScraperAPI with proper implementation"""
        try:
            api_url = "http://api.scraperapi.com"
            params = {
                'api_key': self.scraperapi_key,
                'url': url,
                'render': 'true',  # Enable JavaScript rendering
                'premium': 'true'  # Use premium proxies for better success
            }
            
            response = requests.get(api_url, params=params, timeout=30)
            response.raise_for_status()
            
            return self._parse_html_professionally(response.text, url, "scraperapi")
            
        except Exception as e:
            logger.error(f"ScraperAPI extraction failed: {e}")
            return None
    
    def _extract_with_scrapingbee(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract using ScrapingBee API"""
        try:
            api_url = "https://app.scrapingbee.com/api/v1"
            params = {
                'api_key': self.scrapingbee_key,
                'url': url,
                'render_js': 'true',
                'premium_proxy': 'true'
            }
            
            response = requests.get(api_url, params=params, timeout=30)
            response.raise_for_status()
            
            return self._parse_html_professionally(response.text, url, "scrapingbee")
            
        except Exception as e:
            logger.error(f"ScrapingBee extraction failed: {e}")
            return None
    
    def _extract_with_beautifulsoup(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract using direct request with BeautifulSoup"""
        try:
            response = self.session.get(url, timeout=15, headers=self.headers)
            response.raise_for_status()
            
            return self._parse_html_professionally(response.text, url, "beautifulsoup")
            
        except Exception as e:
            logger.error(f"BeautifulSoup extraction failed: {e}")
            return None
    
    def _extract_with_fallback(self, url: str) -> Optional[Dict[str, Any]]:
        """Last resort extraction with aggressive parsing"""
        try:
            # Try with different user agents
            user_agents = [
                'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            ]
            
            for ua in user_agents:
                try:
                    headers = self.headers.copy()
                    headers['User-Agent'] = ua
                    response = requests.get(url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        result = self._parse_html_professionally(response.text, url, "fallback")
                        if result and result.get('word_count', 0) > 100:
                            return result
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Fallback extraction failed: {e}")
            return None
    
    def _parse_html_professionally(self, html: str, url: str, method: str) -> Optional[Dict[str, Any]]:
        """Professional HTML parsing with multiple extraction strategies"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe', 'noscript']):
                element.decompose()
            
            # Extract metadata
            title = self._extract_title(soup)
            author = self._extract_author(soup, url)
            publish_date = self._extract_publish_date(soup)
            
            # Extract article content with multiple strategies
            content = self._extract_content_smart(soup)
            
            if not content or len(content) < 200:
                logger.warning(f"Insufficient content extracted: {len(content) if content else 0} chars")
                return None
            
            # Extract additional metadata
            domain = urlparse(url).netloc.replace('www.', '')
            
            return {
                'title': title,
                'author': author,
                'text': content,
                'content': content,
                'url': url,
                'domain': domain,
                'source': self._get_source_name(domain),
                'publish_date': publish_date,
                'word_count': len(content.split()),
                'sentence_count': len(re.findall(r'[.!?]+', content)),
                'paragraph_count': len(content.split('\n\n')),
                'extraction_successful': True,
                'extraction_method': method
            }
            
        except Exception as e:
            logger.error(f"HTML parsing failed: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title with multiple strategies"""
        # Try OpenGraph
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        
        # Try Twitter Card
        twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
        if twitter_title and twitter_title.get('content'):
            return twitter_title['content'].strip()
        
        # Try article title
        for selector in ['h1.article-title', 'h1.entry-title', 'h1.post-title', 'h1[itemprop="headline"]', 'h1']:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        # Fallback to page title
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text(strip=True).split('|')[0].strip()
        
        return "Untitled Article"
    
    def _extract_author(self, soup: BeautifulSoup, url: str) -> str:
        """Extract author with domain-specific strategies"""
        # Try schema.org
        author_schema = soup.find('span', itemprop='author')
        if author_schema:
            return author_schema.get_text(strip=True)
        
        # Try meta tags
        for meta_name in ['author', 'article:author', 'DC.creator']:
            meta = soup.find('meta', attrs={'name': meta_name})
            if meta and meta.get('content'):
                return meta['content'].strip()
        
        # Try common class names
        for selector in ['.author-name', '.by-author', '.article-author', '[rel="author"]', '.byline']:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                # Clean up author text
                text = re.sub(r'^by\s+', '', text, flags=re.I)
                if text and len(text) < 100:
                    return text
        
        return "Staff Writer"
    
    def _extract_publish_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract publish date"""
        # Try meta tags
        for meta_property in ['article:published_time', 'datePublished', 'DC.date.issued']:
            meta = soup.find('meta', property=meta_property) or soup.find('meta', attrs={'name': meta_property})
            if meta and meta.get('content'):
                return meta['content']
        
        # Try time tag
        time_tag = soup.find('time')
        if time_tag and time_tag.get('datetime'):
            return time_tag['datetime']
        
        return None
    
    def _extract_content_smart(self, soup: BeautifulSoup) -> str:
        """Smart content extraction with multiple strategies"""
        content_parts = []
        
        # Strategy 1: Look for article tag
        article = soup.find('article')
        if article:
            paragraphs = article.find_all('p')
            content = ' '.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30])
            if len(content) > 500:
                return content
        
        # Strategy 2: Look for main content areas
        for selector in ['main', '[role="main"]', '.article-content', '.entry-content', '.post-content']:
            element = soup.select_one(selector)
            if element:
                paragraphs = element.find_all('p')
                content = ' '.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30])
                if len(content) > 500:
                    return content
        
        # Strategy 3: Find the densest text cluster
        all_paragraphs = soup.find_all('p')
        
        # Score paragraphs based on length and position
        scored_paragraphs = []
        for i, p in enumerate(all_paragraphs):
            text = p.get_text(strip=True)
            if len(text) > 50:  # Minimum paragraph length
                # Score based on length and lack of common footer/header words
                score = len(text)
                if any(word in text.lower() for word in ['cookie', 'subscribe', 'newsletter', 'copyright', 'privacy']):
                    score *= 0.3  # Penalize likely non-content
                scored_paragraphs.append((score, text))
        
        # Sort by score and take the best paragraphs
        scored_paragraphs.sort(key=lambda x: x[0], reverse=True)
        
        # Take top paragraphs that form substantial content
        content = []
        total_words = 0
        for score, text in scored_paragraphs:
            content.append(text)
            total_words += len(text.split())
            if total_words > 300:  # Minimum article length
                break
        
        return ' '.join(content)
    
    def _get_source_name(self, domain: str) -> str:
        """Convert domain to readable source name"""
        source_map = {
            'bbc.com': 'BBC News',
            'bbc.co.uk': 'BBC News',
            'cnn.com': 'CNN',
            'foxnews.com': 'Fox News',
            'nytimes.com': 'The New York Times',
            'washingtonpost.com': 'The Washington Post',
            'theguardian.com': 'The Guardian',
            'reuters.com': 'Reuters',
            'apnews.com': 'Associated Press',
            'bloomberg.com': 'Bloomberg',
            'wsj.com': 'Wall Street Journal'
        }
        
        return source_map.get(domain, domain.replace('.com', '').replace('.org', '').title())
    
    def _validate_extraction(self, data: Dict[str, Any]) -> bool:
        """Validate that extraction produced quality content"""
        if not data:
            return False
        
        # Check required fields
        required = ['title', 'text', 'content', 'url', 'domain']
        for field in required:
            if field not in data:
                logger.warning(f"Missing required field: {field}")
                return False
        
        # Check content quality
        text = data.get('text', '')
        if len(text) < 200:
            logger.warning(f"Content too short: {len(text)} chars")
            return False
        
        word_count = data.get('word_count', 0)
        if word_count < 50:
            logger.warning(f"Too few words: {word_count}")
            return False
        
        # Check for garbage content
        if text.count('<') > 10 or text.count('>') > 10:
            logger.warning("Content appears to contain HTML")
            return False
        
        return True
    
    def _calculate_quality_score(self, data: Dict[str, Any]) -> int:
        """Calculate extraction quality score"""
        score = 0
        
        # Content length (max 40 points)
        word_count = data.get('word_count', 0)
        score += min(40, word_count // 25)
        
        # Has title (10 points)
        if data.get('title') and data['title'] != 'Untitled Article':
            score += 10
        
        # Has author (10 points)
        if data.get('author') and data['author'] not in ['Unknown', 'Staff Writer']:
            score += 10
        
        # Has date (10 points)
        if data.get('publish_date'):
            score += 10
        
        # Has clean content (20 points)
        text = data.get('text', '')
        if text and '<' not in text and '>' not in text:
            score += 20
        
        # Has metadata (10 points)
        if data.get('keywords') or data.get('summary'):
            score += 10
        
        return min(100, score)
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            'success': False,
            'service': self.service_name,
            'available': self.is_available,
            'error': error_message,
            'timestamp': time.time()
        }
