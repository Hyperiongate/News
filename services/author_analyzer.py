"""
Enhanced Author Analyzer Service - BULLETPROOF AI ENHANCED VERSION
Analyzes article authors and their credibility with bulletproof AI insights
"""
import re
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from services.base_analyzer import BaseAnalyzer
from services.ai_enhancement_mixin import AIEnhancementMixin

logger = logging.getLogger(__name__)


class AuthorAnalyzer(BaseAnalyzer, AIEnhancementMixin):
    """Enhanced author analysis service WITH BULLETPROOF AI ENHANCEMENT"""
    
    def __init__(self):
        super().__init__('author_analyzer')
        AIEnhancementMixin.__init__(self)
        
        # Compile regex patterns once for efficiency
        self._byline_patterns = [
            re.compile(r'^By\s+([A-Z][a-zA-Z\s]+?)(?:\n|$|,|\|)', re.MULTILINE | re.IGNORECASE),
            re.compile(r'By:\s*([A-Z][a-zA-Z\s]+?)(?:\n|$|,|\|)', re.MULTILINE | re.IGNORECASE),
            re.compile(r'Written by\s+([A-Z][a-zA-Z\s]+?)(?:\n|$|,|\|)', re.MULTILINE | re.IGNORECASE),
            re.compile(r'Author:\s*([A-Z][a-zA-Z\s]+?)(?:\n|$|,|\|)', re.MULTILINE | re.IGNORECASE),
            re.compile(r'\n([A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+)\s*\n', re.MULTILINE),
            re.compile(r'- ([A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+)(?:\n|$)', re.MULTILINE)
        ]
        
        logger.info(f"AuthorAnalyzer initialized with AI enhancement: {self._ai_available}") re.MULTILINE | re.IGNORECASE),
            re.compile(r'By:\s*([A-Z][a-zA-Z\s]+?)(?:\n|$|,|\|)', re.MULTILINE | re.IGNORECASE),
            re.compile(r'Written by\s+([A-Z][a-zA-Z\s]+?)(?:\n|$|,|\|)', re.MULTILINE | re.IGNORECASE),
            re.compile(r'Author:\s*([A-Z][a-zA-Z\s]+?)(?:\n|$|,|\|)', re.MULTILINE | re.IGNORECASE),
            re.compile(r'\n([A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+)\s*\n', re.MULTILINE),
            re.compile(r'- ([A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+)(?:\n|$)', re.MULTILINE)
        ]
        
        logger.info("AuthorAnalyzer initialized")
        
    def _check_availability(self) -> bool:
        """Check if service is available"""
        return True  # Always available, doesn't require external APIs
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze author credibility and information - FIXED VERSION
        FIXED: Improved author extraction and removed AI enhancement bugs
        
        Expected input:
            - text: Article text
            - title: Article title
            - url: Article URL (optional)
            - html: Article HTML (optional)
            
        Returns:
            Standardized response with author analysis
        """
        try:
            text = data.get('text', '')
            title = data.get('title', '')
            
            if not text and not title:
                return self.get_error_result("No text or title provided for author analysis")
            
            logger.info(f"Analyzing author information for article: {title[:50] if title else 'No title'}...")
            
            # Extract author name from multiple sources
            author_name = self._extract_author_name(data)
            
            if not author_name:
                logger.info("No author name found in article")
                return {
                    'service': self.service_name,
                    'success': True,
                    'data': {
                        'score': 0,
                        'level': 'Unknown',
                        'findings': [{
                            'type': 'info',
                            'severity': 'medium',
                            'text': 'No author information found',
                            'explanation': 'Article does not contain identifiable author attribution'
                        }],
                        'summary': 'No author information available for analysis',
                        'author_name': None,
                        'verified': False,
                        'bio': '',
                        'position': '',
                        'organization': '',
                        'expertise_areas': [],
                        'article_count': 0,
                        'recent_articles': [],
                        'social_media': {},
                        'bio_scraped': False,
                        'credibility_score': 0,
                        'author_score': 0,
                        'has_byline': False,
                        'author_link': None
                    }
                }
            
            logger.info(f"Found author: {author_name}")
            
            # Initialize author data
            author_data = {
                'author_name': author_name,
                'score': 50,  # Default score
                'verified': False,
                'bio': '',
                'position': '',
                'organization': '',
                'expertise_areas': [],
                'article_count': 0,
                'recent_articles': [],
                'social_media': {},
                'bio_scraped': False,
                'has_byline': True,
                'author_link': None
            }
            
            # Try to extract author bio URL from article HTML
            bio_data = {}
            article_url = data.get('url')
            article_html = data.get('html')
            
            if article_url and article_html:
                try:
                    soup = BeautifulSoup(article_html, 'html.parser')
                    author_url = self._extract_author_url(soup, author_name, article_url)
                    
                    if author_url:
                        author_data['author_link'] = author_url
                        logger.info(f"Found author URL: {author_url}")
                        
                        # Scrape the author bio page
                        bio_data = self._scrape_author_bio(author_url)
                        
                        if bio_data:
                            author_data['bio_scraped'] = True
                            author_data['verified'] = True
                            
                            # Update author data with scraped info
                            author_data['bio'] = bio_data.get('full_bio', '')[:500]  # Limit length
                            author_data['position'] = bio_data.get('position', '')
                            author_data['organization'] = bio_data.get('organization', '')
                            author_data['expertise_areas'] = bio_data.get('expertise_areas', [])
                            author_data['article_count'] = bio_data.get('article_count', 0)
                            author_data['social_media'] = bio_data.get('social_media', {})
                            
                            logger.info(f"Successfully scraped bio data for {author_name}")
                        else:
                            logger.info(f"Could not scrape bio data from {author_url}")
                    else:
                        logger.info("No author URL found in article")
                except Exception as e:
                    logger.warning(f"Error processing author bio: {e}")
            
            # Also try to extract basic author info from the article text itself
            if not author_data.get('bio'):
                author_info = self._extract_author_info_from_text(text, author_name)
                if author_info:
                    author_data.update(author_info)
            
            # Calculate credibility score
            credibility_score = self._calculate_credibility_score(author_data)
            author_data['credibility_score'] = credibility_score
            author_data['author_score'] = credibility_score  # Alias
            author_data['score'] = credibility_score  # Generic score
            
            # Determine level
            if credibility_score >= 80:
                level = 'High'
            elif credibility_score >= 60:
                level = 'Good'
            elif credibility_score >= 40:
                level = 'Moderate'
            elif credibility_score >= 20:
                level = 'Low'
            else:
                level = 'Unknown'
            
            # Generate findings
            findings = self._generate_findings(author_data, credibility_score)
            
            # Generate summary
            summary = self._generate_summary(author_data, credibility_score)
            
            logger.info(f"Author analysis complete: {author_name} -> {credibility_score}/100 ({level})")
            
            return {
                'service': self.service_name,
                'success': True,
                'data': {
                    **author_data,
                    'level': level,
                    'findings': findings,
                    'summary': summary
                }
            }
            
        except Exception as e:
            logger.error(f"Author analysis failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _extract_author_name(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract author name from various sources with improved detection"""
        # Check if author is directly provided
        author = data.get('author', '')
        if author and isinstance(author, str) and len(author.strip()) > 0:
            cleaned = self._clean_author_name(author.strip())
            if cleaned:
                return cleaned
        
        # Extract from HTML if available
        html = data.get('html', '')
        if html:
            try:
                soup = BeautifulSoup(html, 'html.parser')
                if soup:  # Verify soup was created successfully
                    
                    # Try various author selectors
                author_selectors = [
                    # Schema.org markup
                    '[itemprop="author"]',
                    '[itemtype*="Person"] [itemprop="name"]',
                    
                    # Common class names
                    '.author-name',
                    '.byline-author',
                    '.article-author',
                    '.post-author',
                    '.writer-name',
                    '.contributor-name',
                    
                    # Meta tags
                    'meta[name="author"]',
                    'meta[property="article:author"]',
                    
                    # Byline patterns
                    '.byline',
                    '.author',
                    '.by-author'
                ]
                
                for selector in author_selectors:
                    try:
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
                                text = element.get_text(strip=True)
                                if text:
                                    cleaned = self._clean_author_name(text)
                                    if cleaned:
                                        return cleaned
                    except Exception as e:
                        logger.debug(f"Error with selector {selector}: {e}")
                        continue
                        
            except Exception as e:
                logger.warning(f"Error parsing HTML for author: {e}")
        
        # Extract from text content
        text = data.get('text', '')
        if text:
            author = self._extract_author_from_text(text)
            if author:
                return author
        
        return None
    
    def _extract_author_from_text(self, text: str) -> Optional[str]:
        """Extract author from text using pre-compiled patterns"""
        for pattern in self._byline_patterns:
            match = pattern.search(text)
            if match:
                author = match.group(1).strip()
                cleaned = self._clean_author_name(author)
                if cleaned and len(cleaned.split()) >= 2:  # At least first and last name
                    return cleaned
        
        return None
    
    def _clean_author_name(self, author: str) -> Optional[str]:
        """Clean author name and validate it"""
        if not author or not isinstance(author, str):
            return None
        
        try:
            # Remove common prefixes and suffixes
            author = re.sub(r'^(By|by|BY|Written by|Author:)\s+', '', author)
            author = re.sub(r'\s*[\|\-]\s*(Reporter|Writer|Journalist|Correspondent|Editor).*
    
    def _extract_author_url(self, soup: BeautifulSoup, author_name: str, article_url: str) -> Optional[str]:
        """Extract author bio URL from the article"""
        if not author_name:
            return None
            
        logger.debug(f"Searching for author URL for: {author_name}")
        
        # Try various selectors to find author links
        selectors = [
            # Specific author link selectors
            'a.author-link',
            'a[href*="/author/"]',
            'a[href*="/profile/"]',
            'a[href*="/contributor/"]',
            'a[href*="/writer/"]',
            'a[rel="author"]',
            '[itemprop="author"] a',
            '.byline a',
            '.author a',
            '.author-bio a',
            '.author-info a',
            '.by-author a'
        ]
        
        for selector in selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    href = element.get('href')
                    if href:
                        # Check if link text contains author name or looks like author link
                        link_text = element.get_text(strip=True).lower()
                        author_lower = author_name.lower()
                        
                        if (author_lower in link_text or 
                            any(word in href.lower() for word in ['author', 'profile', 'contributor', 'writer'])):
                            
                            author_url = urljoin(article_url, href)
                            logger.debug(f"Found potential author URL: {author_url}")
                            return author_url
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {e}")
                continue
        
        # Try to find links that contain the author's name
        try:
            author_name_parts = author_name.lower().split()
            all_links = soup.find_all('a', href=True)
            
            for link in all_links:
                href = link.get('href', '')
                link_text = link.get_text(strip=True).lower()
                
                # Check if link contains author name parts
                name_matches = sum(1 for part in author_name_parts if part in link_text)
                
                if (name_matches >= len(author_name_parts) // 2 and  # At least half the name parts
                    any(keyword in href.lower() for keyword in ['/author/', '/profile/', '/contributor/', '/writer/'])):
                    
                    author_url = urljoin(article_url, href)
                    logger.debug(f"Found author URL via name matching: {author_url}")
                    return author_url
                    
        except Exception as e:
            logger.debug(f"Error in name-based author URL search: {e}")
        
        logger.debug("No author URL found")
        return None
    
    def _scrape_author_bio(self, author_url: str) -> Dict[str, Any]:
        """Scrape author bio page for additional information"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
            }
            
            response = requests.get(author_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            bio_data = {
                'url': author_url,
                'full_bio': '',
                'position': '',
                'organization': '',
                'expertise_areas': [],
                'article_count': 0,
                'social_media': {}
            }
            
            # Extract bio text - multiple possible selectors
            bio_selectors = [
                '.author-bio',
                '.bio',
                '.author-description',
                '[class*="bio"]',
                '.author-bio p',
                '.author-info',
                '.contributor-bio',
                '.writer-bio',
                '[itemprop="description"]',
                '.profile-bio',
                '.about'
            ]
            
            for selector in bio_selectors:
                try:
                    element = soup.select_one(selector)
                    if element:
                        text = element.get_text(strip=True)
                        if len(text) > 50:  # Meaningful bio length
                            bio_data['full_bio'] = text
                            break
                except:
                    continue
            
            # Extract position/title
            position_selectors = [
                '.author-title',
                '.author-position',
                '.title',
                '.position',
                '[itemprop="jobTitle"]',
                '.job-title'
            ]
            
            for selector in position_selectors:
                try:
                    element = soup.select_one(selector)
                    if element:
                        position = element.get_text(strip=True)
                        if position and len(position) < 200:
                            bio_data['position'] = position
                            break
                except:
                    continue
            
            # Look for article count patterns in text
            page_text = soup.get_text()
            count_patterns = [
                r'(\d+)\s*(?:articles?|stories|posts)',
                r'(?:written|authored|published)\s*(\d+)',
                r'(\d+)\s*(?:contributions?|pieces?)'
            ]
            
            for pattern in count_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    count = int(match.group(1))
                    if count < 10000:  # Reasonable upper limit
                        bio_data['article_count'] = count
                        break
            
            # Extract expertise areas from bio text
            if bio_data['full_bio']:
                expertise = self._extract_expertise_from_bio(bio_data['full_bio'])
                bio_data['expertise_areas'] = expertise
            
            # Look for social media links
            social_selectors = [
                'a[href*="twitter.com"]',
                'a[href*="linkedin.com"]',
                'a[href*="facebook.com"]'
            ]
            
            for selector in social_selectors:
                try:
                    elements = soup.select(selector)
                    for element in elements:
                        href = element.get('href', '')
                        if 'twitter.com' in href:
                            bio_data['social_media']['twitter'] = href
                        elif 'linkedin.com' in href:
                            bio_data['social_media']['linkedin'] = href
                        elif 'facebook.com' in href:
                            bio_data['social_media']['facebook'] = href
                except:
                    continue
            
            return bio_data if bio_data['full_bio'] else None
            
        except Exception as e:
            logger.warning(f"Failed to scrape author bio from {author_url}: {e}")
            return None
    
    def _extract_author_info_from_text(self, text: str, author_name: str) -> Dict[str, Any]:
        """Extract basic author info from article text"""
        info = {}
        
        # Look for author description in the text
        author_patterns = [
            rf"{re.escape(author_name)}\s+is\s+([^.]+)",
            rf"{re.escape(author_name)},\s+([^.]+)",
            rf"^([^.]+)\s+{re.escape(author_name)}"
        ]
        
        for pattern in author_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                description = match.group(1).strip()
                if len(description) > 10 and len(description) < 200:
                    info['bio'] = description
                    break
        
        return info
    
    def _extract_expertise_from_bio(self, bio_text: str) -> List[str]:
        """Extract expertise areas from bio text"""
        expertise = []
        
        # Patterns to identify expertise
        expertise_patterns = [
            r'(?:specializes?|covers?|focuses?|reports?)\s+(?:in|on)\s+([^,.]+)',
            r'(?:expert|expertise)\s+(?:in|on)\s+([^,.]+)',
            r'beat:?\s*([^,.]+)',
            r'covers?\s+([^,.]+)'
        ]
        
        for pattern in expertise_patterns:
            matches = re.finditer(pattern, bio_text, re.IGNORECASE)
            for match in matches:
                area = match.group(1).strip()
                if len(area) > 3 and len(area) < 50:
                    expertise.append(area.title())
        
        return expertise[:5]  # Limit to 5 expertise areas
    
    def _calculate_credibility_score(self, author_data: Dict[str, Any]) -> int:
        """Calculate author credibility score"""
        score = 30  # Base score for having a byline
        
        # Bio available
        if author_data.get('bio'):
            score += 20
            
        # Bio scraped from dedicated page
        if author_data.get('bio_scraped'):
            score += 15
            
        # Has position/title
        if author_data.get('position'):
            score += 10
            
        # Has organization
        if author_data.get('organization'):
            score += 10
            
        # Article count
        article_count = author_data.get('article_count', 0)
        if article_count > 50:
            score += 15
        elif article_count > 10:
            score += 10
        elif article_count > 0:
            score += 5
        
        # Has expertise areas
        if author_data.get('expertise_areas'):
            score += 10
        
        # Social media presence
        if author_data.get('social_media'):
            score += 5
        
        # Has author link (verified presence)
        if author_data.get('author_link'):
            score += 10
        
        return min(100, score)
    
    def _generate_findings(self, author_data: Dict[str, Any], score: int) -> List[Dict[str, Any]]:
        """Generate findings based on author analysis"""
        findings = []
        
        author_name = author_data.get('author_name', 'Unknown')
        
        if score >= 70:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': f'Well-documented author: {author_name}',
                'explanation': 'Author has comprehensive biographical information available'
            })
        elif score >= 40:
            findings.append({
                'type': 'info',
                'severity': 'medium',
                'text': f'Partially documented author: {author_name}',
                'explanation': 'Some author information available'
            })
        else:
            findings.append({
                'type': 'warning',
                'severity': 'medium',
                'text': f'Limited author information: {author_name}',
                'explanation': 'Minimal biographical details available'
            })
        
        # Add specific findings
        if author_data.get('bio_scraped'):
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': 'Author has dedicated bio page',
                'explanation': 'Indicates established presence at publication'
            })
        
        if author_data.get('article_count', 0) > 20:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': f'Prolific author ({author_data["article_count"]} articles)',
                'explanation': 'Extensive publication history indicates experience'
            })
        
        if author_data.get('expertise_areas'):
            areas = ', '.join(author_data['expertise_areas'][:3])
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': f'Specialized expertise: {areas}',
                'explanation': 'Author has identified areas of specialization'
            })
        
        return findings
    
    def _generate_summary(self, author_data: Dict[str, Any], score: int) -> str:
        """Generate summary of author analysis"""
        author_name = author_data.get('author_name', 'Unknown author')
        
        if score >= 70:
            summary = f"{author_name} is a well-documented author with comprehensive biographical information. "
        elif score >= 40:
            summary = f"{author_name} has some available biographical information. "
        else:
            summary = f"{author_name} has limited available biographical information. "
        
        if author_data.get('position'):
            summary += f"Listed as {author_data['position']}. "
        
        if author_data.get('article_count', 0) > 0:
            summary += f"Has published {author_data['article_count']} articles. "
        
        if author_data.get('expertise_areas'):
            areas = ', '.join(author_data['expertise_areas'][:2])
            summary += f"Specializes in {areas}. "
        
        summary += f"Credibility score: {score}/100."
        
        return summary
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        info = super().get_service_info()
        info.update({
            'capabilities': [
                'Author name extraction from multiple sources',
                'Author bio page discovery and scraping',
                'Expertise area identification',
                'Publication history analysis',
                'Social media presence detection',
                'Author credibility scoring',
                'Byline verification'
            ],
            'extraction_methods': [
                'HTML meta tags',
                'Schema.org markup',
                'Byline patterns',
                'Author links',
                'Bio page scraping'
            ]
        })
        return info, '', author, flags=re.I)
            author = re.sub(r'\s+', ' ', author).strip()
            
            # Remove email addresses and social handles
            author = re.sub(r'\S*@\S*', '', author)
            author = re.sub(r'@\w+', '', author)
            
            # Clean up extra whitespace
            author = re.sub(r'\s+', ' ', author).strip()
            
            # Validate - should be reasonable length and format
            if (len(author) >= 3 and len(author) <= 100 and 
                author.split() and len(author.split()) >= 1 and len(author.split()) <= 5 and
                re.match(r"^[A-Za-z\s\-'.]+$", author)):
                
                # Convert to proper case
                return ' '.join(word.capitalize() for word in author.split())
        except re.error:
            # Handle regex errors gracefully
            logger.warning(f"Regex error while cleaning author name: {author}")
        except Exception as e:
            # Handle any other unexpected errors
            logger.warning(f"Error cleaning author name '{author}': {e}")
        
        return None
    
    def _extract_author_url(self, soup: BeautifulSoup, author_name: str, article_url: str) -> Optional[str]:
        """Extract author bio URL from the article"""
        if not author_name:
            return None
            
        logger.debug(f"Searching for author URL for: {author_name}")
        
        # Try various selectors to find author links
        selectors = [
            # Specific author link selectors
            'a.author-link',
            'a[href*="/author/"]',
            'a[href*="/profile/"]',
            'a[href*="/contributor/"]',
            'a[href*="/writer/"]',
            'a[rel="author"]',
            '[itemprop="author"] a',
            '.byline a',
            '.author a',
            '.author-bio a',
            '.author-info a',
            '.by-author a'
        ]
        
        for selector in selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    href = element.get('href')
                    if href:
                        # Check if link text contains author name or looks like author link
                        link_text = element.get_text(strip=True).lower()
                        author_lower = author_name.lower()
                        
                        if (author_lower in link_text or 
                            any(word in href.lower() for word in ['author', 'profile', 'contributor', 'writer'])):
                            
                            author_url = urljoin(article_url, href)
                            logger.debug(f"Found potential author URL: {author_url}")
                            return author_url
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {e}")
                continue
        
        # Try to find links that contain the author's name
        try:
            author_name_parts = author_name.lower().split()
            all_links = soup.find_all('a', href=True)
            
            for link in all_links:
                href = link.get('href', '')
                link_text = link.get_text(strip=True).lower()
                
                # Check if link contains author name parts
                name_matches = sum(1 for part in author_name_parts if part in link_text)
                
                if (name_matches >= len(author_name_parts) // 2 and  # At least half the name parts
                    any(keyword in href.lower() for keyword in ['/author/', '/profile/', '/contributor/', '/writer/'])):
                    
                    author_url = urljoin(article_url, href)
                    logger.debug(f"Found author URL via name matching: {author_url}")
                    return author_url
                    
        except Exception as e:
            logger.debug(f"Error in name-based author URL search: {e}")
        
        logger.debug("No author URL found")
        return None
    
    def _scrape_author_bio(self, author_url: str) -> Dict[str, Any]:
        """Scrape author bio page for additional information"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
            }
            
            response = requests.get(author_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            bio_data = {
                'url': author_url,
                'full_bio': '',
                'position': '',
                'organization': '',
                'expertise_areas': [],
                'article_count': 0,
                'social_media': {}
            }
            
            # Extract bio text - multiple possible selectors
            bio_selectors = [
                '.author-bio',
                '.bio',
                '.author-description',
                '[class*="bio"]',
                '.author-bio p',
                '.author-info',
                '.contributor-bio',
                '.writer-bio',
                '[itemprop="description"]',
                '.profile-bio',
                '.about'
            ]
            
            for selector in bio_selectors:
                try:
                    element = soup.select_one(selector)
                    if element:
                        text = element.get_text(strip=True)
                        if len(text) > 50:  # Meaningful bio length
                            bio_data['full_bio'] = text
                            break
                except:
                    continue
            
            # Extract position/title
            position_selectors = [
                '.author-title',
                '.author-position',
                '.title',
                '.position',
                '[itemprop="jobTitle"]',
                '.job-title'
            ]
            
            for selector in position_selectors:
                try:
                    element = soup.select_one(selector)
                    if element:
                        position = element.get_text(strip=True)
                        if position and len(position) < 200:
                            bio_data['position'] = position
                            break
                except:
                    continue
            
            # Look for article count patterns in text
            page_text = soup.get_text()
            count_patterns = [
                r'(\d+)\s*(?:articles?|stories|posts)',
                r'(?:written|authored|published)\s*(\d+)',
                r'(\d+)\s*(?:contributions?|pieces?)'
            ]
            
            for pattern in count_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    count = int(match.group(1))
                    if count < 10000:  # Reasonable upper limit
                        bio_data['article_count'] = count
                        break
            
            # Extract expertise areas from bio text
            if bio_data['full_bio']:
                expertise = self._extract_expertise_from_bio(bio_data['full_bio'])
                bio_data['expertise_areas'] = expertise
            
            # Look for social media links
            social_selectors = [
                'a[href*="twitter.com"]',
                'a[href*="linkedin.com"]',
                'a[href*="facebook.com"]'
            ]
            
            for selector in social_selectors:
                try:
                    elements = soup.select(selector)
                    for element in elements:
                        href = element.get('href', '')
                        if 'twitter.com' in href:
                            bio_data['social_media']['twitter'] = href
                        elif 'linkedin.com' in href:
                            bio_data['social_media']['linkedin'] = href
                        elif 'facebook.com' in href:
                            bio_data['social_media']['facebook'] = href
                except:
                    continue
            
            return bio_data if bio_data['full_bio'] else None
            
        except Exception as e:
            logger.warning(f"Failed to scrape author bio from {author_url}: {e}")
            return None
    
    def _extract_author_info_from_text(self, text: str, author_name: str) -> Dict[str, Any]:
        """Extract basic author info from article text"""
        info = {}
        
        # Look for author description in the text
        author_patterns = [
            rf"{re.escape(author_name)}\s+is\s+([^.]+)",
            rf"{re.escape(author_name)},\s+([^.]+)",
            rf"^([^.]+)\s+{re.escape(author_name)}"
        ]
        
        for pattern in author_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                description = match.group(1).strip()
                if len(description) > 10 and len(description) < 200:
                    info['bio'] = description
                    break
        
        return info
    
    def _extract_expertise_from_bio(self, bio_text: str) -> List[str]:
        """Extract expertise areas from bio text"""
        expertise = []
        
        # Patterns to identify expertise
        expertise_patterns = [
            r'(?:specializes?|covers?|focuses?|reports?)\s+(?:in|on)\s+([^,.]+)',
            r'(?:expert|expertise)\s+(?:in|on)\s+([^,.]+)',
            r'beat:?\s*([^,.]+)',
            r'covers?\s+([^,.]+)'
        ]
        
        for pattern in expertise_patterns:
            matches = re.finditer(pattern, bio_text, re.IGNORECASE)
            for match in matches:
                area = match.group(1).strip()
                if len(area) > 3 and len(area) < 50:
                    expertise.append(area.title())
        
        return expertise[:5]  # Limit to 5 expertise areas
    
    def _calculate_credibility_score(self, author_data: Dict[str, Any]) -> int:
        """Calculate author credibility score"""
        score = 30  # Base score for having a byline
        
        # Bio available
        if author_data.get('bio'):
            score += 20
            
        # Bio scraped from dedicated page
        if author_data.get('bio_scraped'):
            score += 15
            
        # Has position/title
        if author_data.get('position'):
            score += 10
            
        # Has organization
        if author_data.get('organization'):
            score += 10
            
        # Article count
        article_count = author_data.get('article_count', 0)
        if article_count > 50:
            score += 15
        elif article_count > 10:
            score += 10
        elif article_count > 0:
            score += 5
        
        # Has expertise areas
        if author_data.get('expertise_areas'):
            score += 10
        
        # Social media presence
        if author_data.get('social_media'):
            score += 5
        
        # Has author link (verified presence)
        if author_data.get('author_link'):
            score += 10
        
        return min(100, score)
    
    def _generate_findings(self, author_data: Dict[str, Any], score: int) -> List[Dict[str, Any]]:
        """Generate findings based on author analysis"""
        findings = []
        
        author_name = author_data.get('author_name', 'Unknown')
        
        if score >= 70:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': f'Well-documented author: {author_name}',
                'explanation': 'Author has comprehensive biographical information available'
            })
        elif score >= 40:
            findings.append({
                'type': 'info',
                'severity': 'medium',
                'text': f'Partially documented author: {author_name}',
                'explanation': 'Some author information available'
            })
        else:
            findings.append({
                'type': 'warning',
                'severity': 'medium',
                'text': f'Limited author information: {author_name}',
                'explanation': 'Minimal biographical details available'
            })
        
        # Add specific findings
        if author_data.get('bio_scraped'):
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': 'Author has dedicated bio page',
                'explanation': 'Indicates established presence at publication'
            })
        
        if author_data.get('article_count', 0) > 20:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': f'Prolific author ({author_data["article_count"]} articles)',
                'explanation': 'Extensive publication history indicates experience'
            })
        
        if author_data.get('expertise_areas'):
            areas = ', '.join(author_data['expertise_areas'][:3])
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': f'Specialized expertise: {areas}',
                'explanation': 'Author has identified areas of specialization'
            })
        
        return findings
    
    def _generate_summary(self, author_data: Dict[str, Any], score: int) -> str:
        """Generate summary of author analysis"""
        author_name = author_data.get('author_name', 'Unknown author')
        
        if score >= 70:
            summary = f"{author_name} is a well-documented author with comprehensive biographical information. "
        elif score >= 40:
            summary = f"{author_name} has some available biographical information. "
        else:
            summary = f"{author_name} has limited available biographical information. "
        
        if author_data.get('position'):
            summary += f"Listed as {author_data['position']}. "
        
        if author_data.get('article_count', 0) > 0:
            summary += f"Has published {author_data['article_count']} articles. "
        
        if author_data.get('expertise_areas'):
            areas = ', '.join(author_data['expertise_areas'][:2])
            summary += f"Specializes in {areas}. "
        
        summary += f"Credibility score: {score}/100."
        
        return summary
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        info = super().get_service_info()
        info.update({
            'capabilities': [
                'Author name extraction from multiple sources',
                'Author bio page discovery and scraping',
                'Expertise area identification',
                'Publication history analysis',
                'Social media presence detection',
                'Author credibility scoring',
                'Byline verification'
            ],
            'extraction_methods': [
                'HTML meta tags',
                'Schema.org markup',
                'Byline patterns',
                'Author links',
                'Bio page scraping'
            ]
        })
        return info
