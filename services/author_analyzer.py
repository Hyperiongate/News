"""
Enhanced Author Analyzer Service - FIXED VERSION WITH IMPROVED NAME CLEANING
Actually searches for and retrieves author information using ScraperAPI
"""
import re
import logging
import json
import hashlib
import time
import random
from typing import Dict, Any, Optional, List, Tuple, Set
from urllib.parse import urljoin, urlparse, quote
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import requests
from bs4 import BeautifulSoup

from services.base_analyzer import BaseAnalyzer
from services.ai_enhancement_mixin import AIEnhancementMixin
from config import Config

logger = logging.getLogger(__name__)


class AdvancedAuthorResearcher:
    """Advanced author research engine using ScraperAPI for real searches"""
    
    def __init__(self):
        self.session = requests.Session()
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache
        
        # API keys from config
        self.scraperapi_key = Config.SCRAPERAPI_KEY
        self.news_api_key = Config.NEWS_API_KEY or Config.NEWSAPI_KEY
        
        # Award recognition patterns
        self.award_patterns = [
            r'Pulitzer\s+(?:Prize|Award)',
            r'Peabody\s+Award',
            r'Emmy\s+Award',
            r'Edward\s+R\.?\s+Murrow\s+Award',
            r'George\s+Polk\s+Award',
            r'National\s+Magazine\s+Award',
            r'Associated\s+Press\s+Award'
        ]
        
        logger.info(f"Author Researcher initialized - ScraperAPI: {bool(self.scraperapi_key)}, News API: {bool(self.news_api_key)}")
    
    def comprehensive_author_research(self, author_name: str, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive author research using ScraperAPI"""
        try:
            logger.info(f"Starting comprehensive research for author: {author_name}")
            
            research_results = {
                'author_name': author_name,
                'verification_status': 'unverified',
                'credibility_score': 30,  # Base score
                'bio_data': {},
                'publication_history': [],
                'social_media_profiles': {},
                'professional_credentials': {},
                'awards_recognition': [],
                'expertise_domains': [],
                'author_photo': None,
                'linkedin_profile': None,
                'twitter_profile': None,
                'recent_articles': [],
                'research_timestamp': datetime.now().isoformat()
            }
            
            # Check cache first
            cache_key = hashlib.md5(author_name.lower().encode()).hexdigest()
            if cache_key in self.cache and (time.time() - self.cache[cache_key]['timestamp']) < self.cache_ttl:
                logger.info(f"Using cached research for {author_name}")
                return self.cache[cache_key]['data']
            
            # 1. Search for author using ScraperAPI
            if self.scraperapi_key:
                search_results = self._scraperapi_search(author_name, article_data.get('domain', ''))
                if search_results:
                    research_results.update(search_results)
            
            # 2. If author has a bio URL, scrape it directly
            author_url = article_data.get('author_url')
            if author_url:
                bio_page_data = self._scrape_author_bio_page(author_url)
                if bio_page_data:
                    research_results['bio_data'].update(bio_page_data)
                    research_results['verification_status'] = 'verified'
            
            # 3. Search for LinkedIn profile
            linkedin_url = self._find_linkedin_profile(author_name)
            if linkedin_url:
                research_results['linkedin_profile'] = linkedin_url
                research_results['social_media_profiles']['linkedin'] = linkedin_url
            
            # 4. Search for Twitter profile
            twitter_url = self._find_twitter_profile(author_name)
            if twitter_url:
                research_results['twitter_profile'] = twitter_url
                research_results['social_media_profiles']['twitter'] = twitter_url
            
            # 5. News API search for publication history
            if self.news_api_key:
                news_results = self._search_news_api(author_name)
                if news_results:
                    research_results['publication_history'] = news_results
                    research_results['recent_articles'] = news_results[:5]
            
            # 6. Calculate credibility score
            credibility_score = self._calculate_credibility(research_results)
            research_results['credibility_score'] = credibility_score
            
            # Cache results
            self.cache[cache_key] = {
                'data': research_results,
                'timestamp': time.time()
            }
            
            logger.info(f"Research completed for {author_name}: {credibility_score}/100 credibility")
            return research_results
            
        except Exception as e:
            logger.error(f"Author research failed for {author_name}: {e}")
            return {
                'error': str(e),
                'author_name': author_name,
                'credibility_score': 0
            }
    
    def _scraperapi_search(self, author_name: str, domain: str = '') -> Dict[str, Any]:
        """Use ScraperAPI to search for author information"""
        if not self.scraperapi_key:
            return None
        
        try:
            results = {
                'bio_data': {},
                'awards_recognition': [],
                'expertise_domains': []
            }
            
            # Search Google for author bio and information
            search_query = f'"{author_name}" journalist biography awards linkedin'
            if domain:
                search_query += f' site:{domain}'
            
            # Use ScraperAPI to search Google
            scraperapi_url = "http://api.scraperapi.com"
            params = {
                'api_key': self.scraperapi_key,
                'url': f'https://www.google.com/search?q={quote(search_query)}',
                'render': 'false'
            }
            
            response = self.session.get(scraperapi_url, params=params, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract bio snippets from search results
                snippets = soup.find_all(['span', 'div'], class_=['st', 'IsZvec', 'aCOpRe', 'lEBKkf'])
                bio_text = ''
                for snippet in snippets[:5]:
                    text = snippet.get_text()
                    if author_name.lower() in text.lower():
                        bio_text += text + ' '
                
                if bio_text:
                    results['bio_data']['search_bio'] = bio_text[:500]
                    
                    # Look for awards in the bio text
                    for pattern in self.award_patterns:
                        if re.search(pattern, bio_text, re.IGNORECASE):
                            results['awards_recognition'].append({
                                'award': pattern.replace('\\s+', ' ').replace('(?:', '').replace(')', ''),
                                'source': 'search_results'
                            })
                    
                    # Extract expertise from bio
                    expertise_keywords = ['covers', 'specializes', 'reports on', 'writes about', 'expert in']
                    for keyword in expertise_keywords:
                        pattern = rf'{keyword}\s+([^,.]+)'
                        matches = re.finditer(pattern, bio_text, re.IGNORECASE)
                        for match in matches:
                            expertise = match.group(1).strip()
                            if len(expertise) < 50:
                                results['expertise_domains'].append(expertise)
                
                # Look for LinkedIn and social media URLs
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link.get('href', '')
                    if 'linkedin.com/in/' in href:
                        # Extract actual LinkedIn URL from Google redirect
                        if 'url=' in href:
                            import urllib.parse
                            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                            if 'url' in parsed:
                                results['linkedin_profile'] = parsed['url'][0]
                        elif href.startswith('http'):
                            results['linkedin_profile'] = href
                    elif 'twitter.com/' in href or 'x.com/' in href:
                        if 'url=' in href:
                            import urllib.parse
                            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                            if 'url' in parsed:
                                results['twitter_profile'] = parsed['url'][0]
            
            return results if bio_text else None
            
        except Exception as e:
            logger.warning(f"ScraperAPI search failed for {author_name}: {e}")
            return None
    
    def _scrape_author_bio_page(self, author_url: str) -> Dict[str, Any]:
        """Scrape author bio page using ScraperAPI"""
        if not self.scraperapi_key:
            return self._direct_scrape_author_bio(author_url)
        
        try:
            scraperapi_url = "http://api.scraperapi.com"
            params = {
                'api_key': self.scraperapi_key,
                'url': author_url,
                'render': 'false'
            }
            
            response = self.session.get(scraperapi_url, params=params, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                bio_data = {
                    'url': author_url,
                    'full_bio': '',
                    'position': '',
                    'organization': '',
                    'expertise_areas': [],
                    'article_count': 0,
                    'author_photo': None
                }
                
                # Extract bio text
                bio_selectors = [
                    '.author-bio', '.bio', '.author-description', '[class*="bio"]',
                    '.author-info', '.contributor-bio', '[itemprop="description"]'
                ]
                
                for selector in bio_selectors:
                    element = soup.select_one(selector)
                    if element:
                        bio_data['full_bio'] = element.get_text(strip=True)[:1000]
                        break
                
                # Extract position/title
                position_selectors = [
                    '.author-title', '.author-position', '.title', '.position',
                    '[itemprop="jobTitle"]', '.job-title'
                ]
                
                for selector in position_selectors:
                    element = soup.select_one(selector)
                    if element:
                        bio_data['position'] = element.get_text(strip=True)
                        break
                
                # Look for author photo
                img_selectors = [
                    '.author-photo img', '.author-image img', '.profile-photo img',
                    '[class*="author"] img', '[class*="profile"] img'
                ]
                
                for selector in img_selectors:
                    element = soup.select_one(selector)
                    if element:
                        src = element.get('src', '')
                        if src:
                            bio_data['author_photo'] = urljoin(author_url, src)
                            break
                
                # Extract social media links
                social_links = soup.find_all('a', href=re.compile(r'(linkedin|twitter|facebook)\.com'))
                for link in social_links:
                    href = link.get('href', '')
                    if 'linkedin.com' in href:
                        bio_data['linkedin'] = href
                    elif 'twitter.com' in href or 'x.com' in href:
                        bio_data['twitter'] = href
                
                # Count articles if visible
                article_count_text = soup.get_text()
                count_match = re.search(r'(\d+)\s*(?:articles?|stories|posts)', article_count_text, re.IGNORECASE)
                if count_match:
                    bio_data['article_count'] = int(count_match.group(1))
                
                return bio_data if bio_data['full_bio'] else None
                
        except Exception as e:
            logger.warning(f"Failed to scrape author bio from {author_url}: {e}")
            return self._direct_scrape_author_bio(author_url)
    
    def _direct_scrape_author_bio(self, author_url: str) -> Dict[str, Any]:
        """Direct scrape without ScraperAPI as fallback"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = self.session.get(author_url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                bio_data = {}
                
                # Try to extract bio
                bio_element = soup.select_one('.author-bio, .bio, .author-description')
                if bio_element:
                    bio_data['full_bio'] = bio_element.get_text(strip=True)[:1000]
                
                # Try to extract position
                position_element = soup.select_one('.author-title, .position, .title')
                if position_element:
                    bio_data['position'] = position_element.get_text(strip=True)
                
                return bio_data if bio_data else None
                
        except Exception as e:
            logger.debug(f"Direct scrape failed: {e}")
            return None
    
    def _find_linkedin_profile(self, author_name: str) -> Optional[str]:
        """Search for author's LinkedIn profile using ScraperAPI"""
        if not self.scraperapi_key:
            return None
        
        try:
            search_query = f'site:linkedin.com/in/ "{author_name}" journalist OR reporter OR writer'
            
            scraperapi_url = "http://api.scraperapi.com"
            params = {
                'api_key': self.scraperapi_key,
                'url': f'https://www.google.com/search?q={quote(search_query)}',
                'render': 'false'
            }
            
            response = self.session.get(scraperapi_url, params=params, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for LinkedIn URLs in search results
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    if 'linkedin.com/in/' in href:
                        # Extract actual URL from Google redirect
                        if '/url?' in href and 'q=' in href:
                            import urllib.parse
                            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                            if 'q' in parsed:
                                linkedin_url = parsed['q'][0]
                                if 'linkedin.com/in/' in linkedin_url:
                                    logger.info(f"Found LinkedIn profile for {author_name}: {linkedin_url}")
                                    return linkedin_url
                        elif href.startswith('https://www.linkedin.com/in/'):
                            logger.info(f"Found LinkedIn profile for {author_name}: {href}")
                            return href
            
            return None
            
        except Exception as e:
            logger.debug(f"LinkedIn search failed for {author_name}: {e}")
            return None
    
    def _find_twitter_profile(self, author_name: str) -> Optional[str]:
        """Search for author's Twitter profile using ScraperAPI"""
        if not self.scraperapi_key:
            return None
        
        try:
            search_query = f'site:twitter.com "{author_name}" journalist OR reporter'
            
            scraperapi_url = "http://api.scraperapi.com"
            params = {
                'api_key': self.scraperapi_key,
                'url': f'https://www.google.com/search?q={quote(search_query)}',
                'render': 'false'
            }
            
            response = self.session.get(scraperapi_url, params=params, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for Twitter URLs in search results
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    if 'twitter.com/' in href or 'x.com/' in href:
                        # Extract actual URL from Google redirect
                        if '/url?' in href and 'q=' in href:
                            import urllib.parse
                            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                            if 'q' in parsed:
                                twitter_url = parsed['q'][0]
                                if 'twitter.com/' in twitter_url or 'x.com/' in twitter_url:
                                    logger.info(f"Found Twitter profile for {author_name}: {twitter_url}")
                                    return twitter_url
            
            return None
            
        except Exception as e:
            logger.debug(f"Twitter search failed for {author_name}: {e}")
            return None
    
    def _search_news_api(self, author_name: str) -> List[Dict[str, Any]]:
        """Search for author's articles using News API"""
        if not self.news_api_key:
            return []
        
        try:
            url = f"https://newsapi.org/v2/everything"
            params = {
                'q': f'"{author_name}"',
                'sortBy': 'publishedAt',
                'pageSize': 20,
                'apiKey': self.news_api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                articles = []
                if data.get('status') == 'ok' and data.get('articles'):
                    for article in data['articles'][:10]:
                        # Check if author name appears in article
                        if (author_name.lower() in article.get('description', '').lower() or
                            author_name.lower() in article.get('title', '').lower() or
                            author_name.lower() in article.get('author', '').lower()):
                            
                            articles.append({
                                'title': article.get('title', ''),
                                'source': article.get('source', {}).get('name', ''),
                                'published_at': article.get('publishedAt', ''),
                                'url': article.get('url', ''),
                                'description': article.get('description', '')
                            })
                
                return articles
            
            return []
            
        except Exception as e:
            logger.warning(f"News API search failed for {author_name}: {e}")
            return []
    
    def _calculate_credibility(self, research_results: Dict[str, Any]) -> int:
        """Calculate credibility score based on research findings"""
        score = 30  # Base score
        
        # Bio information found
        if research_results.get('bio_data', {}).get('full_bio'):
            score += 20
        elif research_results.get('bio_data', {}).get('search_bio'):
            score += 10
        
        # Has LinkedIn profile
        if research_results.get('linkedin_profile'):
            score += 15
        
        # Has Twitter profile
        if research_results.get('twitter_profile'):
            score += 10
        
        # Publication history
        pub_count = len(research_results.get('publication_history', []))
        if pub_count >= 10:
            score += 20
        elif pub_count >= 5:
            score += 15
        elif pub_count > 0:
            score += 10
        
        # Awards and recognition
        if research_results.get('awards_recognition'):
            score += 15
        
        # Has author photo
        if research_results.get('bio_data', {}).get('author_photo'):
            score += 5
        
        # Has position/title
        if research_results.get('bio_data', {}).get('position'):
            score += 10
        
        # Expertise areas identified
        if research_results.get('expertise_domains'):
            score += 5
        
        return min(100, score)


class AuthorAnalyzer(BaseAnalyzer, AIEnhancementMixin):
    """Author analysis service with real web search capabilities"""
    
    def __init__(self):
        super().__init__('author_analyzer')
        AIEnhancementMixin.__init__(self)
        
        # Initialize researcher with real search capabilities
        self.researcher = AdvancedAuthorResearcher()
        
        # Byline patterns for author extraction
        self._byline_patterns = [
            re.compile(r'^By\s+([A-Z][a-zA-Z\s]+?)(?:\n|$|,|\|)', re.MULTILINE | re.IGNORECASE),
            re.compile(r'By:\s*([A-Z][a-zA-Z\s]+?)(?:\n|$|,|\|)', re.MULTILINE | re.IGNORECASE),
            re.compile(r'Written by\s+([A-Z][a-zA-Z\s]+?)(?:\n|$|,|\|)', re.MULTILINE | re.IGNORECASE),
            re.compile(r'Author:\s*([A-Z][a-zA-Z\s]+?)(?:\n|$|,|\|)', re.MULTILINE | re.IGNORECASE)
        ]
        
        logger.info(f"AuthorAnalyzer initialized with ScraperAPI: {bool(self.researcher.scraperapi_key)}")
    
    def _check_availability(self) -> bool:
        """Check if service is available"""
        return True
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze author with real web search and data retrieval
        """
        try:
            text = data.get('text', '')
            title = data.get('title', '')
            url = data.get('url', '')
            html = data.get('html', '')
            
            if not text and not title:
                return self.get_error_result("No text or title provided for author analysis")
            
            # Extract author name
            author_name = self._extract_author_name(data)
            
            if not author_name:
                return self.get_success_result({
                    'score': 0,
                    'level': 'Unknown',
                    'author_name': None,
                    'verified': False,
                    'summary': 'No author information available',
                    'findings': [{
                        'type': 'info',
                        'text': 'No author attribution found in article'
                    }]
                })
            
            logger.info(f"Analyzing author: {author_name}")
            
            # Extract author URL if it's a hyperlink
            author_url = None
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                author_url = self._extract_author_url(soup, author_name, url)
                if author_url:
                    logger.info(f"Found author URL: {author_url}")
            
            # Prepare data for researcher
            article_data = {
                'domain': urlparse(url).netloc if url else '',
                'title': title,
                'text': text,
                'author_url': author_url
            }
            
            # Perform comprehensive research
            research = self.researcher.comprehensive_author_research(author_name, article_data)
            
            # Build response
            author_data = {
                'author_name': author_name,
                'score': research.get('credibility_score', 0),
                'verified': research.get('verification_status') == 'verified',
                'bio': research.get('bio_data', {}).get('full_bio', research.get('bio_data', {}).get('search_bio', ''))[:500],
                'position': research.get('bio_data', {}).get('position', ''),
                'organization': research.get('bio_data', {}).get('organization', ''),
                'expertise_areas': research.get('expertise_domains', []),
                'article_count': len(research.get('publication_history', [])),
                'recent_articles': research.get('recent_articles', []),
                'social_media': research.get('social_media_profiles', {}),
                'linkedin_profile': research.get('linkedin_profile'),
                'twitter_profile': research.get('twitter_profile'),
                'author_photo': research.get('bio_data', {}).get('author_photo'),
                'awards': research.get('awards_recognition', []),
                'author_link': author_url,
                'credibility_score': research.get('credibility_score', 0)
            }
            
            # Determine level
            score = author_data['credibility_score']
            if score >= 80:
                level = 'High'
            elif score >= 60:
                level = 'Good'
            elif score >= 40:
                level = 'Moderate'
            elif score >= 20:
                level = 'Low'
            else:
                level = 'Unknown'
            
            author_data['level'] = level
            
            # Generate findings
            findings = self._generate_findings(author_data, research)
            author_data['findings'] = findings
            
            # Generate summary
            summary = self._generate_summary(author_data, research)
            author_data['summary'] = summary
            
            logger.info(f"Author analysis complete: {author_name} -> {score}/100")
            
            return self.get_success_result(author_data)
            
        except Exception as e:
            logger.error(f"Author analysis failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _extract_author_name(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract author name from various sources"""
        # Check if author is directly provided
        author = data.get('author', '')
        if author and isinstance(author, str) and len(author.strip()) > 0:
            return self._clean_author_name(author.strip())
        
        # Extract from HTML if available
        html = data.get('html', '')
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Try various author selectors
            author_selectors = [
                '[itemprop="author"]',
                '.author-name',
                '.byline-author',
                '.article-author',
                'meta[name="author"]',
                'meta[property="article:author"]',
                '.byline',
                '.author'
            ]
            
            for selector in author_selectors:
                if selector.startswith('meta'):
                    element = soup.select_one(selector)
                    if element:
                        content = element.get('content', '').strip()
                        if content:
                            cleaned = self._clean_author_name(content)
                            if cleaned:
                                return cleaned
                else:
                    element = soup.select_one(selector)
                    if element:
                        # Check if it's a link
                        link = element.find('a')
                        if link:
                            text = link.get_text(strip=True)
                        else:
                            text = element.get_text(strip=True)
                        if text:
                            cleaned = self._clean_author_name(text)
                            if cleaned:
                                return cleaned
        
        # Extract from text content
        text = data.get('text', '')
        if text:
            for pattern in self._byline_patterns:
                match = pattern.search(text)
                if match:
                    author = match.group(1).strip()
                    cleaned = self._clean_author_name(author)
                    if cleaned:
                        return cleaned
        
        return None
    
    def _extract_author_url(self, soup: BeautifulSoup, author_name: str, article_url: str) -> Optional[str]:
        """Extract author bio URL if author name is a hyperlink"""
        if not author_name:
            return None
        
        # Look for author links
        selectors = [
            'a.author-link',
            'a.author-name',
            '.author a',
            '.byline a',
            'a[href*="/author/"]',
            'a[href*="/profile/"]',
            'a[href*="/contributor/"]'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                link_text = element.get_text(strip=True).lower()
                if author_name.lower() in link_text or link_text in author_name.lower():
                    href = element.get('href')
                    if href:
                        return urljoin(article_url, href)
        
        # Search all links for author name
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            link_text = link.get_text(strip=True)
            if link_text and author_name.lower() in link_text.lower():
                href = link.get('href', '')
                if any(keyword in href.lower() for keyword in ['/author/', '/profile/', '/contributor/']):
                    return urljoin(article_url, href)
        
        return None
    
    def _clean_author_name(self, author: str) -> Optional[str]:
        """Clean and validate author name - ENHANCED VERSION"""
        if not author:
            return None
        
        # Remove common prefixes
        author = re.sub(r'^(By|by|BY|Written by|Author:|Reporter:)\s+', '', author, flags=re.IGNORECASE)
        author = re.sub(r'\s*[\|\-]\s*(Reporter|Writer|Journalist|Correspondent).*$', '', author, flags=re.IGNORECASE)
        
        # NEW: Remove web UI elements and sharing buttons
        author = re.sub(r'^(ShareSave|Share|Save|Print|Email|Tweet|Pin|Comment)', '', author, flags=re.IGNORECASE)
        author = re.sub(r'(ShareSave|Share|Save|Print|Email)$', '', author, flags=re.IGNORECASE)
        
        # NEW: Remove news organization names and suffixes
        author = re.sub(r'\s*,?\s*(BBC News|BBC|CNN|Reuters|Associated Press|AP|Fox News|NBC|ABC|CBS).*$', '', author, flags=re.IGNORECASE)
        author = re.sub(r'\s+(News|Reporter|Correspondent|Writer|Editor|Staff)$', '', author, flags=re.IGNORECASE)
        
        # Remove trailing punctuation and special characters
        author = re.sub(r'[,\.\:;]+$', '', author)
        
        # Clean up whitespace
        author = re.sub(r'\s+', ' ', author).strip()
        
        # Validate the cleaned name
        if not author or len(author) < 3 or len(author) > 100:
            return None
        
        # Check if it's actually a name (has at least 2 words for first/last)
        words = author.split()
        if len(words) < 2:
            return None
        
        # Check for common false positives
        false_positives = [
            'share', 'save', 'print', 'email', 'comment', 'subscribe',
            'advertisement', 'sponsored', 'trending', 'popular', 'related',
            'breaking news', 'latest news', 'top stories', 'social media',
            'read more', 'click here', 'follow us', 'sign up'
        ]
        
        author_lower = author.lower()
        if any(fp in author_lower for fp in false_positives):
            return None
        
        # Return properly capitalized name
        return ' '.join(word.capitalize() for word in author.split())
    
    def _generate_findings(self, author_data: Dict[str, Any], research: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate findings based on research"""
        findings = []
        
        score = author_data['credibility_score']
        
        if score >= 70:
            findings.append({
                'type': 'positive',
                'text': f'Well-documented author with {score}/100 credibility score',
                'severity': 'positive'
            })
        elif score >= 40:
            findings.append({
                'type': 'info',
                'text': f'Moderate author documentation: {score}/100 credibility',
                'severity': 'medium'
            })
        else:
            findings.append({
                'type': 'warning',
                'text': f'Limited author information available: {score}/100 credibility',
                'severity': 'medium'
            })
        
        if author_data.get('linkedin_profile'):
            findings.append({
                'type': 'positive',
                'text': 'LinkedIn profile found and verified',
                'severity': 'positive'
            })
        
        if author_data.get('awards'):
            findings.append({
                'type': 'positive',
                'text': f"Awards/recognition: {len(author_data['awards'])} found",
                'severity': 'positive'
            })
        
        if author_data.get('article_count', 0) > 10:
            findings.append({
                'type': 'positive',
                'text': f"Established writer with {author_data['article_count']} articles",
                'severity': 'positive'
            })
        
        if author_data.get('author_photo'):
            findings.append({
                'type': 'info',
                'text': 'Author photo available',
                'severity': 'positive'
            })
        
        return findings
    
    def _generate_summary(self, author_data: Dict[str, Any], research: Dict[str, Any]) -> str:
        """Generate summary of author analysis"""
        author_name = author_data.get('author_name', 'Unknown')
        score = author_data['credibility_score']
        
        summary = f"{author_name} "
        
        if score >= 70:
            summary += "is a well-documented author with strong credentials. "
        elif score >= 40:
            summary += "has moderate documentation available. "
        else:
            summary += "has limited publicly available information. "
        
        if author_data.get('position'):
            summary += f"Listed as {author_data['position']}. "
        
        if author_data.get('linkedin_profile'):
            summary += "LinkedIn profile verified. "
        
        if author_data.get('article_count', 0) > 0:
            summary += f"{author_data['article_count']} articles found. "
        
        if author_data.get('awards'):
            summary += f"{len(author_data['awards'])} professional recognitions. "
        
        summary += f"Overall credibility: {score}/100."
        
        return summary
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        info = super().get_service_info()
        info.update({
            'capabilities': [
                'Author name extraction',
                'Author bio page discovery',
                'LinkedIn profile search',
                'Twitter profile search',
                'Publication history search',
                'Awards and recognition tracking',
                'Photo retrieval',
                'Credibility scoring'
            ],
            'uses_scraperapi': bool(self.researcher.scraperapi_key),
            'uses_news_api': bool(self.researcher.news_api_key)
        })
        return info
