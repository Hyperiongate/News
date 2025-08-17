"""
Enhanced Author Analyzer Service
Analyzes article authors and their credibility by following bio links
"""
import re
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from .base_analyzer import BaseAnalyzer, AnalysisError
from config import Config

logger = logging.getLogger(__name__)


class AuthorAnalyzer(BaseAnalyzer):
    """Enhanced author analysis service that follows bio links"""
    
    def __init__(self):
        super().__init__()
        self.service_name = 'author_analyzer'
        self._check_availability()
        
    def _check_availability(self) -> bool:
        """Check if service is available"""
        self._available = Config.is_service_enabled(self.service_name)
        return self._available
    
    def _extract_author_url(self, soup: BeautifulSoup, author_name: str, article_url: str) -> Optional[str]:
        """Extract author bio URL from the article"""
        if not author_name:
            return None
            
        # Common patterns for author links
        author_link = None
        
        # Try different selectors for author links
        selectors = [
            f'a:contains("{author_name}")',  # Direct name match
            f'a[href*="/author/"]',          # Common author URL pattern
            f'a[href*="/staff/"]',           # Staff pages
            f'a[href*="/contributors/"]',    # Contributors
            f'a[href*="/people/"]',          # People pages
            f'a[href*="/bio/"]',            # Bio pages
            '.author-link a',                # Class-based
            '.byline a',                     # Byline links
            '[rel="author"] a',              # Semantic markup
            '.author-name a',                # Author name class
            '.article-author a',             # Article author class
        ]
        
        for selector in selectors:
            try:
                links = soup.select(selector)
                for link in links:
                    # Check if this link contains the author name
                    link_text = link.get_text(strip=True)
                    if author_name.lower() in link_text.lower():
                        href = link.get('href')
                        if href:
                            # Make URL absolute
                            author_link = urljoin(article_url, href)
                            logger.info(f"Found author bio link: {author_link}")
                            return author_link
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {e}")
                continue
        
        # Try to find link by searching all links for author name
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            link_text = link.get_text(strip=True)
            if author_name.lower() in link_text.lower():
                # Filter out social media and non-bio links
                href = link.get('href')
                if href and not any(domain in href for domain in ['twitter.com', 'facebook.com', 'instagram.com', 'linkedin.com']):
                    if any(pattern in href for pattern in ['/author/', '/staff/', '/people/', '/contributors/', '/bio/']):
                        author_link = urljoin(article_url, href)
                        logger.info(f"Found author bio link via text search: {author_link}")
                        return author_link
        
        return None
    
    def _scrape_author_bio(self, bio_url: str) -> Dict[str, Any]:
        """Scrape author bio page for detailed information"""
        try:
            logger.info(f"Scraping author bio from: {bio_url}")
            
            # Fetch the bio page
            response = requests.get(bio_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            bio_data = {
                'bio_url': bio_url,
                'full_bio': None,
                'position': None,
                'experience': None,
                'education': None,
                'expertise_areas': [],
                'social_media': {},
                'email': None,
                'recent_articles': [],
                'awards': [],
                'organization': None
            }
            
            # Extract bio text - try multiple selectors
            bio_selectors = [
                '.author-bio', '.bio-content', '.biography',
                '.author-description', '.staff-bio', '.contributor-bio',
                '[class*="bio"]', '[id*="bio"]', '.about-author',
                '.author-info', '.author-details'
            ]
            
            for selector in bio_selectors:
                bio_elem = soup.select_one(selector)
                if bio_elem:
                    bio_data['full_bio'] = bio_elem.get_text(strip=True)
                    break
            
            # Extract position/title
            position_selectors = [
                '.author-title', '.author-position', '.job-title',
                '.title', '.position', '.role', '.author-role'
            ]
            
            for selector in position_selectors:
                pos_elem = soup.select_one(selector)
                if pos_elem:
                    bio_data['position'] = pos_elem.get_text(strip=True)
                    break
            
            # Extract expertise areas
            expertise_selectors = [
                '.expertise', '.specialties', '.beats', '.topics',
                '.coverage-areas', '.focus-areas'
            ]
            
            for selector in expertise_selectors:
                exp_elems = soup.select(selector)
                for elem in exp_elems:
                    bio_data['expertise_areas'].extend([
                        e.strip() for e in elem.get_text().split(',')
                    ])
            
            # Extract social media links
            social_patterns = {
                'twitter': r'twitter\.com/(\w+)',
                'linkedin': r'linkedin\.com/in/([\w-]+)',
                'facebook': r'facebook\.com/([\w.]+)',
                'instagram': r'instagram\.com/(\w+)'
            }
            
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                for platform, pattern in social_patterns.items():
                    match = re.search(pattern, href)
                    if match:
                        bio_data['social_media'][platform] = match.group(1)
            
            # Extract email
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            page_text = soup.get_text()
            emails = re.findall(email_pattern, page_text)
            if emails:
                bio_data['email'] = emails[0]
            
            # Extract recent articles
            article_selectors = [
                '.author-articles', '.recent-posts', '.articles-list',
                '.author-posts', '.by-author', '.more-articles'
            ]
            
            for selector in article_selectors:
                articles_container = soup.select_one(selector)
                if articles_container:
                    article_links = articles_container.select('a')[:10]  # Get up to 10 recent articles
                    for link in article_links:
                        article_data = {
                            'title': link.get_text(strip=True),
                            'url': urljoin(bio_url, link.get('href', ''))
                        }
                        # Try to get date
                        date_elem = link.find_next_sibling(string=re.compile(r'\d{4}'))
                        if date_elem:
                            article_data['date'] = date_elem.strip()
                        bio_data['recent_articles'].append(article_data)
                    break
            
            # Extract awards/recognition
            award_selectors = [
                '.awards', '.recognition', '.honors',
                '.achievements', '.accolades'
            ]
            
            for selector in award_selectors:
                award_elems = soup.select(selector)
                for elem in award_elems:
                    awards_text = elem.get_text(strip=True)
                    bio_data['awards'].extend([
                        a.strip() for a in awards_text.split('\n') if a.strip()
                    ])
            
            # Try to extract years of experience from bio text
            if bio_data['full_bio']:
                exp_patterns = [
                    r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
                    r'(?:for|over|nearly)\s*(\d+)\s*years?',
                    r'(\d+)\s*years?\s*(?:as|in|covering)',
                    r'since\s*(\d{4})'  # Calculate from year
                ]
                
                for pattern in exp_patterns:
                    match = re.search(pattern, bio_data['full_bio'], re.IGNORECASE)
                    if match:
                        if pattern == r'since\s*(\d{4})':
                            # Calculate years from start year
                            start_year = int(match.group(1))
                            current_year = datetime.now().year
                            bio_data['experience'] = f"{current_year - start_year} years"
                        else:
                            bio_data['experience'] = f"{match.group(1)} years"
                        break
            
            return bio_data
            
        except Exception as e:
            logger.warning(f"Error scraping author bio from {bio_url}: {e}")
            return {}
    
    def _calculate_credibility_score(self, author_data: Dict[str, Any]) -> int:
        """Calculate author credibility score based on available information"""
        score = 50  # Base score
        
        # Has bio page (+20)
        if author_data.get('bio_url'):
            score += 20
        
        # Has detailed bio text (+10)
        if author_data.get('full_bio') and len(author_data['full_bio']) > 100:
            score += 10
        
        # Has position/title (+10)
        if author_data.get('position'):
            score += 10
            # Bonus for senior positions
            if any(term in author_data['position'].lower() for term in 
                   ['senior', 'chief', 'editor', 'director', 'head']):
                score += 5
        
        # Has experience (+10)
        if author_data.get('experience'):
            score += 10
            # Bonus for extensive experience
            try:
                years = int(re.search(r'(\d+)', author_data['experience']).group(1))
                if years >= 10:
                    score += 10
                elif years >= 5:
                    score += 5
            except:
                pass
        
        # Has expertise areas (+5)
        if author_data.get('expertise_areas'):
            score += 5
        
        # Has recent articles (+10)
        if author_data.get('recent_articles'):
            score += 5
            if len(author_data['recent_articles']) >= 5:
                score += 5
        
        # Has awards/recognition (+10)
        if author_data.get('awards'):
            score += 10
        
        # Has social media presence (+5)
        if author_data.get('social_media'):
            score += 5
        
        # Has contact information (+5)
        if author_data.get('email'):
            score += 5
        
        # Cap at 100
        return min(score, 100)
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze article author with enhanced bio scraping
        
        Args:
            data: Must contain 'author' and optionally article HTML/URL
            
        Returns:
            Analysis results with author credibility data
        """
        try:
            author_name = data.get('author', '').strip()
            
            if not author_name or author_name.lower() in ['unknown', 'staff', 'admin', 'editor']:
                return self._create_response(
                    success=True,
                    data={
                        'author_name': author_name or 'Unknown',
                        'credibility_score': 0,
                        'verified': False,
                        'author_info': {
                            'message': 'No identifiable author found'
                        }
                    }
                )
            
            # Initialize author data
            author_data = {
                'author_name': author_name,
                'credibility_score': 50,  # Default score
                'verified': False,
                'author_info': {}
            }
            
            # Try to get author bio URL if we have article HTML or URL
            article_url = data.get('url')
            article_html = data.get('html')
            
            if article_url and article_html:
                try:
                    soup = BeautifulSoup(article_html, 'html.parser')
                    bio_url = self._extract_author_url(soup, author_name, article_url)
                    
                    if bio_url:
                        # Scrape the bio page
                        bio_data = self._scrape_author_bio(bio_url)
                        
                        if bio_data:
                            # Update author_info with scraped data
                            author_data['author_info'] = {
                                'bio': bio_data.get('full_bio', ''),
                                'position': bio_data.get('position', ''),
                                'experience': bio_data.get('experience', ''),
                                'expertise': bio_data.get('expertise_areas', []),
                                'organization': bio_data.get('organization', ''),
                                'bio_url': bio_data.get('bio_url', ''),
                                'social_media': bio_data.get('social_media', {}),
                                'recent_articles_count': len(bio_data.get('recent_articles', []))
                            }
                            
                            # Add recent articles if found
                            if bio_data.get('recent_articles'):
                                author_data['recent_articles'] = bio_data['recent_articles'][:5]
                            
                            # Add awards if found
                            if bio_data.get('awards'):
                                author_data['author_info']['awards'] = bio_data['awards']
                            
                            # Calculate enhanced credibility score
                            author_data['credibility_score'] = self._calculate_credibility_score(bio_data)
                            author_data['verified'] = True
                            
                            # Add key findings
                            findings = []
                            
                            if bio_data.get('position'):
                                findings.append(f"Verified position: {bio_data['position']}")
                            
                            if bio_data.get('experience'):
                                findings.append(f"Experience: {bio_data['experience']}")
                            
                            if bio_data.get('awards'):
                                findings.append(f"Has {len(bio_data['awards'])} awards/recognitions")
                            
                            if bio_data.get('recent_articles'):
                                findings.append(f"Published {len(bio_data['recent_articles'])} recent articles")
                            
                            author_data['findings'] = findings
                            
                except Exception as e:
                    logger.warning(f"Error processing author bio: {e}")
            
            # If no bio found or scraped, try basic analysis
            if not author_data.get('verified'):
                # Check if it's a common news agency
                agencies = ['Associated Press', 'AP', 'Reuters', 'AFP', 'Bloomberg', 'UPI']
                if any(agency in author_name for agency in agencies):
                    author_data['credibility_score'] = 85
                    author_data['author_info']['bio'] = f"{author_name} is a recognized news agency"
                    author_data['verified'] = True
                else:
                    # Basic scoring based on name format
                    if ' ' in author_name:  # Has first and last name
                        author_data['credibility_score'] = 60
                    
                    author_data['author_info']['bio'] = 'Limited author information available'
            
            return self._create_response(success=True, data=author_data)
            
        except Exception as e:
            logger.error(f"Author analysis failed: {e}")
            return self._create_response(
                success=False,
                error=str(e)
            )
    
    def _create_response(self, success: bool, data: Optional[Dict[str, Any]] = None, 
                        error: Optional[str] = None) -> Dict[str, Any]:
        """Create standardized response"""
        response = {
            'service': self.service_name,
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
        
        if success and data:
            response.update(data)
        elif error:
            response['error'] = error
            
        return response
