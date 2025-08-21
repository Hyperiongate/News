"""
Enhanced Author Analyzer Service - AI ENHANCED VERSION
Analyzes article authors and their credibility by following bio links with AI insights
"""
import re
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from .base_analyzer import BaseAnalyzer
from .ai_enhancement_mixin import AIEnhancementMixin
from config import Config

logger = logging.getLogger(__name__)


class AuthorAnalyzer(BaseAnalyzer, AIEnhancementMixin):
    """Enhanced author analysis service that follows bio links WITH AI ENHANCEMENT"""
    
    def __init__(self):
        super().__init__('author_analyzer')
        AIEnhancementMixin.__init__(self)
        logger.info(f"AuthorAnalyzer initialized with AI enhancement: {self._ai_available}")
        
    def _check_availability(self) -> bool:
        """Check if service is available"""
        # Service is always available as it doesn't require external APIs
        return Config.is_service_enabled(self.service_name)
    
    def _extract_author_url(self, soup: BeautifulSoup, author_name: str, article_url: str) -> Optional[str]:
        """Extract author bio URL from the article"""
        if not author_name:
            return None
            
        logger.info(f"Searching for author URL for: {author_name}")
        
        # For The Independent, author links are typically in specific patterns
        # Updated selectors for The Independent's current structure
        selectors = [
            # The Independent specific selectors
            'a.author-link',
            'div.author-bio a',
            'span.author-name a',
            'div.article-author a',
            '.sc-fjqEFS a',  # Component class they use
            '[data-author] a',
            'a[href*="/author/"]',
            'a[href*="/profile/"]',
            
            # General news site patterns
            'a[rel="author"]',
            '.byline a',
            '.author a',
            'span[itemprop="author"] a',
            'div[class*="author"] a',
            '[class*="byline"] a',
            
            # Search for links containing author name
            f'a:contains("{author_name}")'
        ]
        
        author_url = None
        base_url = f"{urlparse(article_url).scheme}://{urlparse(article_url).netloc}"
        
        # Try each selector
        for selector in selectors:
            try:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href', '')
                    if href and ('/author/' in href or '/profile/' in href or 
                               author_name.lower().replace(' ', '-') in href.lower()):
                        author_url = urljoin(base_url, href)
                        logger.info(f"Found author URL via selector '{selector}': {author_url}")
                        return author_url
            except Exception as e:
                logger.debug(f"Selector '{selector}' failed: {e}")
                continue
        
        # Alternative: Check meta tags
        meta_author = soup.find('meta', {'property': 'article:author'})
        if meta_author and meta_author.get('content'):
            potential_url = meta_author['content']
            if potential_url.startswith('http'):
                logger.info(f"Found author URL in meta tag: {potential_url}")
                return potential_url
        
        # Alternative: Look for JSON-LD data
        json_ld = soup.find('script', {'type': 'application/ld+json'})
        if json_ld:
            try:
                import json
                data = json.loads(json_ld.string)
                if isinstance(data, dict) and 'author' in data:
                    author_data = data['author']
                    if isinstance(author_data, dict) and 'url' in author_data:
                        logger.info(f"Found author URL in JSON-LD: {author_data['url']}")
                        return author_data['url']
            except:
                pass
        
        logger.info(f"No author URL found for {author_name}")
        return None
    
    def _scrape_author_bio(self, bio_url: str) -> Dict[str, Any]:
        """Scrape author bio information from their profile page"""
        try:
            logger.info(f"Scraping author bio from: {bio_url}")
            
            # Request the bio page
            response = requests.get(bio_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            bio_data = {
                'bio_url': bio_url,
                'full_bio': '',
                'position': '',
                'organization': '',
                'experience': '',
                'expertise_areas': [],
                'education': [],
                'awards': [],
                'social_media': {},
                'email': '',
                'article_count': 0,
                'recent_articles': []
            }
            
            # Extract bio text - multiple possible selectors
            bio_selectors = [
                'div.author-bio',
                'div.bio',
                'div.author-description',
                'div[class*="bio"]',
                'p.author-bio',
                'section.author-info',
                'div.contributor-bio',
                'div.writer-bio',
                '[itemprop="description"]'
            ]
            
            for selector in bio_selectors:
                bio_element = soup.select_one(selector)
                if bio_element:
                    bio_data['full_bio'] = bio_element.get_text(strip=True)
                    break
            
            # Extract position/title
            position_selectors = [
                'span.author-title',
                'div.author-position',
                'span.title',
                'p.position',
                '[itemprop="jobTitle"]'
            ]
            
            for selector in position_selectors:
                position_element = soup.select_one(selector)
                if position_element:
                    bio_data['position'] = position_element.get_text(strip=True)
                    break
            
            # Look for article count
            count_patterns = [
                r'(\d+)\s*(?:articles?|stories|posts)',
                r'(?:written|authored|published)\s*(\d+)',
                r'(\d+)\s*(?:contributions?)'
            ]
            
            page_text = soup.get_text()
            for pattern in count_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    bio_data['article_count'] = int(match.group(1))
                    break
            
            # Extract recent articles
            article_selectors = [
                'article.author-article',
                'div.article-item',
                'li.article',
                'div[class*="article-list"] article',
                'a.article-link'
            ]
            
            for selector in article_selectors:
                articles = soup.select(selector)[:5]  # Get up to 5 recent articles
                for article in articles:
                    title_elem = article.select_one('h2, h3, h4, a')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        link = title_elem.get('href', '') if title_elem.name == 'a' else ''
                        if not link:
                            link_elem = article.select_one('a')
                            if link_elem:
                                link = link_elem.get('href', '')
                        
                        bio_data['recent_articles'].append({
                            'title': title,
                            'url': urljoin(bio_url, link) if link else ''
                        })
            
            # Extract expertise areas from bio text
            if bio_data['full_bio']:
                # Common expertise indicators
                expertise_patterns = [
                    r'(?:specializes?|focuses?|covers?|reports? on|expertise in)\s+([^.]+)',
                    r'(?:expert in|covering|beat includes?)\s+([^.]+)',
                    r'(?:writes? about|columnist for)\s+([^.]+)'
                ]
                
                for pattern in expertise_patterns:
                    matches = re.findall(pattern, bio_data['full_bio'], re.IGNORECASE)
                    for match in matches:
                        # Clean up and split expertise areas
                        areas = re.split(r',|and|&', match)
                        for area in areas:
                            area = area.strip()
                            if area and len(area) < 50:
                                bio_data['expertise_areas'].append(area)
            
            # Extract experience
            experience_patterns = [
                r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|journalism)',
                r'(?:since|from)\s*(\d{4})',
                r'(?:joined|started)\s*(?:in\s*)?\s*(\d{4})'
            ]
            
            for pattern in experience_patterns:
                match = re.search(pattern, bio_data['full_bio'], re.IGNORECASE)
                if match:
                    bio_data['experience'] = match.group(0)
                    break
            
            # Extract awards/recognition
            if bio_data['full_bio']:
                award_patterns = [
                    r'(?:award|prize|honor|recognition)\s+(?:for|in)\s+([^.]+)',
                    r'(?:winner of|recipient of)\s+(?:the\s+)?([^.]+)',
                    r'(?:nominated for|finalist for)\s+(?:the\s+)?([^.]+)'
                ]
                
                for pattern in award_patterns:
                    matches = re.findall(pattern, bio_data['full_bio'], re.IGNORECASE)
                    for match in matches:
                        award = match.strip()
                        if award and len(award) < 100:
                            bio_data['awards'].append(award)
            
            logger.info(f"Successfully scraped author bio: {bio_url}")
            return bio_data
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Network error scraping author bio from {bio_url}: {e}")
            return {}
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
                   ['senior', 'chief', 'editor', 'director', 'head', 'correspondent']):
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
        
        # Has many articles (+10)
        if author_data.get('article_count', 0) > 0:
            score += 5
            if author_data['article_count'] >= 100:
                score += 5
        
        # Has recent articles (+5)
        if author_data.get('recent_articles'):
            score += 5
        
        # Has awards/recognition (+10)
        if author_data.get('awards'):
            score += 10
        
        # Has social media presence (+5)
        if author_data.get('social_media'):
            score += 5
        
        # Has organization (+5)
        if author_data.get('organization'):
            score += 5
        
        # Cap at 100
        return min(score, 100)
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze article author with enhanced bio scraping AND AI ENHANCEMENT
        
        Args:
            data: Must contain 'author' and optionally 'url' and 'html'
            
        Returns:
            Analysis results with author credibility data
        """
        try:
            author_name = data.get('author', '').strip()
            
            if not author_name or author_name.lower() in ['unknown', 'staff', 'admin', 'editor']:
                return {
                    'service': self.service_name,
                    'success': True,
                    'timestamp': datetime.now().isoformat(),
                    'author_name': author_name or 'Unknown',
                    'credibility_score': 0,
                    'verified': False,
                    'author_info': {
                        'bio': 'No identifiable author found'
                    },
                    'metrics': {
                        'article_count': 0,
                        'accuracy_rate': 0,
                        'awards_count': 0
                    },
                    'findings': [],
                    'metadata': {
                        'ai_enhanced': False
                    }
                }
            
            # Initialize result structure matching frontend expectations
            result = {
                'service': self.service_name,
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'author_name': author_name,
                'credibility_score': 50,  # Default score
                'verified': False,
                'author_info': {
                    'bio': '',
                    'position': '',
                    'experience': '',
                    'expertise': []
                },
                'metrics': {
                    'article_count': 0,
                    'accuracy_rate': 0,
                    'awards_count': 0
                },
                'recent_articles': [],
                'current_position': '',
                'expertise_areas': [],
                'findings': [],
                'metadata': {
                    'bio_scraped': False,
                    'ai_enhanced': False
                }
            }
            
            # Try to extract author bio URL from article HTML
            bio_data = {}
            article_url = data.get('url')
            article_html = data.get('html')
            
            if article_url and article_html:
                soup = BeautifulSoup(article_html, 'html.parser')
                author_url = self._extract_author_url(soup, author_name, article_url)
                
                if author_url:
                    # Scrape the author bio page
                    bio_data = self._scrape_author_bio(author_url)
                    
                    if bio_data:
                        result['metadata']['bio_scraped'] = True
                        result['verified'] = True
                        
                        # Update result with scraped data
                        result['author_info']['bio'] = bio_data.get('full_bio', '')[:500]  # Limit length
                        result['author_info']['position'] = bio_data.get('position', '')
                        result['author_info']['experience'] = bio_data.get('experience', '')
                        result['author_info']['expertise'] = bio_data.get('expertise_areas', [])
                        
                        result['current_position'] = bio_data.get('position', '')
                        result['expertise_areas'] = bio_data.get('expertise_areas', [])
                        
                        result['metrics']['article_count'] = bio_data.get('article_count', 0)
                        result['metrics']['awards_count'] = len(bio_data.get('awards', []))
                        
                        if bio_data.get('recent_articles'):
                            result['recent_articles'] = bio_data['recent_articles'][:5]
                        
                        # Calculate credibility score
                        result['credibility_score'] = self._calculate_credibility_score(bio_data)
                        
                        # Generate findings based on bio data
                        findings = []
                        
                        # Positive findings
                        if bio_data.get('position'):
                            findings.append({
                                'type': 'positive',
                                'title': 'Verified position',
                                'description': f'Currently: {bio_data["position"]}'
                            })
                        
                        if bio_data.get('experience'):
                            findings.append({
                                'type': 'positive',
                                'title': 'Professional experience',
                                'description': bio_data['experience']
                            })
                        
                        if bio_data.get('awards'):
                            findings.append({
                                'type': 'positive',
                                'title': 'Awards and recognition',
                                'description': f'Received: {", ".join(bio_data["awards"][:2])}'
                            })
                        
                        if bio_data.get('article_count', 0) > 50:
                            findings.append({
                                'type': 'positive',
                                'title': 'Prolific writer',
                                'description': f'Published {bio_data["article_count"]} articles'
                            })
                        
                        # Warning findings
                        if not bio_data.get('experience'):
                            findings.append({
                                'type': 'warning',
                                'title': 'Experience unclear',
                                'description': 'Years of experience not specified in bio'
                            })
                        
                        result['findings'] = findings
                        
                        logger.info(f"Successfully analyzed author {author_name} with score {result['credibility_score']}")
            
            # AI ENHANCEMENT - Add deeper author insights
            if self._ai_available and author_name:
                logger.info("Enhancing author analysis with AI")
                
                # Prepare data for AI analysis
                author_history = result.get('recent_articles', [])
                article_content = data.get('text', '')
                
                # Get AI author assessment using the correct method name
                ai_author_analysis = self._ai_analyze_author(
                    author_name=author_name,
                    author_history=author_history,
                    article_content=article_content[:1000]  # Limit text
                )
                
                if ai_author_analysis:
                    # Add AI insights to findings
                    if ai_author_analysis.get('red_flags'):
                        for flag in ai_author_analysis['red_flags'][:2]:
                            result['findings'].append({
                                'type': 'warning',
                                'title': 'AI concern',
                                'description': flag
                            })
                    
                    if ai_author_analysis.get('strengths'):
                        for strength in ai_author_analysis['strengths'][:2]:
                            result['findings'].append({
                                'type': 'positive',
                                'title': 'AI insight',
                                'description': strength
                            })
                    
                    # Adjust credibility score based on AI assessment
                    if ai_author_analysis.get('credibility_adjustment'):
                        adjustment = ai_author_analysis['credibility_adjustment']
                        result['credibility_score'] = max(0, min(100, result['credibility_score'] + adjustment))
                    
                    # Add AI expertise assessment
                    if ai_author_analysis.get('expertise_assessment') and not result['author_info']['expertise']:
                        result['author_info']['expertise'] = ai_author_analysis['expertise_assessment']
                    
                    result['metadata']['ai_enhanced'] = True
            
            # If no bio found or scraped, provide basic analysis
            if not result['verified']:
                # Check if it's a news agency
                agencies = ['Associated Press', 'AP', 'Reuters', 'AFP', 'Bloomberg', 'UPI']
                if any(agency.lower() in author_name.lower() for agency in agencies):
                    result['credibility_score'] = 85
                    result['author_info']['bio'] = f"{author_name} is a recognized news agency"
                    result['verified'] = True
                    result['findings'] = [{
                        'type': 'positive',
                        'title': 'Established news agency',
                        'description': f'{author_name} is a trusted news organization'
                    }]
                else:
                    # Basic scoring based on name format
                    if ' ' in author_name:  # Has first and last name
                        result['credibility_score'] = 60
                        result['findings'] = [{
                            'type': 'warning',
                            'title': 'Limited author information',
                            'description': 'Unable to verify author credentials'
                        }]
                    else:
                        result['credibility_score'] = 40
                        result['findings'] = [{
                            'type': 'warning',
                            'title': 'Incomplete author attribution',
                            'description': 'Only partial name provided'
                        }]
                    
                    result['author_info']['bio'] = 'Limited author information available. Unable to access author profile page.'
            
            return result
            
        except Exception as e:
            logger.error(f"Author analysis failed: {e}", exc_info=True)
            return self.get_error_result(f"Analysis failed: {str(e)}")
    
    def get_service_info(self) -> Dict[str, Any]:
        """Return service information"""
        return {
            'service': self.service_name,
            'name': 'Author Analyzer',
            'version': '2.0',
            'description': 'Analyzes article authors by scraping their bio pages for credibility assessment',
            'capabilities': [
                'Author bio page extraction',
                'Professional background analysis',
                'Article count tracking',
                'Recent publications listing',
                'Awards and recognition detection',
                'Experience assessment',
                'Expertise area identification',
                'Credibility scoring',
                'AI-enhanced author insights',
                'Bias pattern detection'
            ],
            'limitations': [
                'Requires author bio page to be accessible',
                'Some sites may block scraping attempts',
                'Limited to publicly available information'
            ],
            'score_range': '0-100',
            'score_interpretation': {
                '90-100': 'Highly credible, verified journalist',
                '70-89': 'Established writer with good credentials',
                '50-69': 'Moderate credibility, limited information',
                '30-49': 'Low credibility, minimal verification',
                '0-29': 'Very low credibility or unknown'
            }
        }
