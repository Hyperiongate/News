"""
Enhanced Author Analyzer Service - AI ENHANCED VERSION
Analyzes article authors and their credibility by following bio links with AI insights
FIXED: Returns data wrapped in 'data' field like other services
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
            'a[href*="/author/"]',
            'a[rel="author"]',
            'span[itemprop="author"] a',
            'div.author-bio a',
            'div.author-info a',
            
            # General patterns
            f'a:contains("{author_name}")',
            'a.by-author',
            'a.author-name',
            'a.contributor-link',
            'a.writer-link'
        ]
        
        for selector in selectors:
            try:
                # BeautifulSoup doesn't support :contains, so handle it differently
                if ':contains' in selector:
                    # Find all links that contain the author name
                    author_name_lower = author_name.lower()
                    links = soup.find_all('a', string=lambda text: text and author_name_lower in text.lower())
                    
                    for link in links:
                        href = link.get('href')
                        if href and ('/author/' in href or '/contributor/' in href or '/profile/' in href):
                            author_url = urljoin(article_url, href)
                            logger.info(f"Found author URL via name search: {author_url}")
                            return author_url
                else:
                    element = soup.select_one(selector)
                    if element:
                        href = element.get('href')
                        if href:
                            author_url = urljoin(article_url, href)
                            logger.info(f"Found author URL with selector '{selector}': {author_url}")
                            return author_url
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {e}")
                continue
        
        logger.info("No author URL found in article")
        return None
    
    def _scrape_author_bio(self, author_url: str) -> Dict[str, Any]:
        """Scrape author bio page for additional information"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(author_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            bio_data = {
                'url': author_url,
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
            
            # Extract expertise from bio
            if bio_data['full_bio']:
                expertise_patterns = [
                    r'(?:specializes?|covers?|focuses?|reports?)\s+(?:in|on)\s+([^,.]+)',
                    r'(?:expert|expertise)\s+(?:in|on)\s+([^,.]+)',
                    r'beat:?\s*([^,.]+)'
                ]
                
                for pattern in expertise_patterns:
                    matches = re.findall(pattern, bio_data['full_bio'], re.IGNORECASE)
                    bio_data['expertise_areas'].extend(matches)
                
                bio_data['expertise_areas'] = list(set(bio_data['expertise_areas']))[:5]  # Unique, max 5
            
            # Extract social media links
            social_patterns = {
                'twitter': r'twitter\.com/([A-Za-z0-9_]+)',
                'linkedin': r'linkedin\.com/in/([A-Za-z0-9-]+)',
                'email': r'mailto:([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})'
            }
            
            for platform, pattern in social_patterns.items():
                links = soup.find_all('a', href=re.compile(pattern, re.IGNORECASE))
                if links:
                    match = re.search(pattern, links[0].get('href', ''), re.IGNORECASE)
                    if match:
                        if platform == 'email':
                            bio_data['email'] = match.group(1)
                        else:
                            bio_data['social_media'][platform] = match.group(1)
            
            logger.info(f"Successfully scraped author bio from {author_url}")
            return bio_data
            
        except Exception as e:
            logger.error(f"Error scraping author bio from {author_url}: {e}")
            return {}
    
    def _calculate_credibility_score(self, author_data: Dict[str, Any]) -> int:
        """Calculate author credibility score based on various factors"""
        score = 30  # Base score for having a name
        
        # Has bio (+20)
        if author_data.get('bio') and len(author_data['bio']) > 50:
            score += 20
        
        # Has position/title (+15)
        if author_data.get('position'):
            score += 15
        
        # Has expertise areas (+10)
        if author_data.get('expertise_areas'):
            score += 10
        
        # Has significant article count (+10)
        if author_data.get('article_count', 0) >= 10:
            score += 10
            if author_data['article_count'] >= 50:
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
            Analysis results with author credibility data wrapped in 'data' field
        """
        try:
            author_name = data.get('author', '').strip()
            
            # CRITICAL FIX: Wrap all return data in 'data' field
            if not author_name or author_name.lower() in ['unknown', 'staff', 'admin', 'editor']:
                return {
                    'service': self.service_name,
                    'success': True,
                    'data': {
                        'author_name': author_name or 'Unknown',
                        'credibility_score': 0,
                        'score': 0,  # Add score field for consistency
                        'level': 'Unknown',
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
                        'summary': 'No identifiable author found for this article'
                    },
                    'metadata': {
                        'ai_enhanced': False
                    }
                }
            
            # Initialize author data structure
            author_data = {
                'author_name': author_name,
                'credibility_score': 50,  # Default score
                'author_score': 50,  # Alias for frontend compatibility
                'score': 50,  # Generic score field
                'verified': False,
                'bio': '',
                'position': '',
                'organization': '',
                'expertise_areas': [],
                'article_count': 0,
                'recent_articles': [],
                'social_media': {},
                'bio_scraped': False,
                'ai_enhanced': False
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
                        author_data['bio_scraped'] = True
                        author_data['verified'] = True
                        
                        # Update author data with scraped info
                        author_data['bio'] = bio_data.get('full_bio', '')[:500]  # Limit length
                        author_data['position'] = bio_data.get('position', '')
                        author_data['organization'] = bio_data.get('organization', '')
                        author_data['expertise_areas'] = bio_data.get('expertise_areas', [])
                        author_data['article_count'] = bio_data.get('article_count', 0)
                        author_data['social_media'] = bio_data.get('social_media', {})
                        author_data['email'] = bio_data.get('email', '')
            
            # Calculate credibility score
            author_data['credibility_score'] = self._calculate_credibility_score(author_data)
            author_data['author_score'] = author_data['credibility_score']  # Alias
            author_data['score'] = author_data['credibility_score']  # Generic score
            
            # Determine credibility level
            score = author_data['credibility_score']
            if score >= 80:
                level = 'Excellent'
            elif score >= 65:
                level = 'Good'
            elif score >= 50:
                level = 'Fair'
            elif score >= 35:
                level = 'Poor'
            else:
                level = 'Very Poor'
            author_data['level'] = level
            author_data['credibility_level'] = level  # Alias
            
            # Generate findings
            findings = []
            
            if author_data['verified']:
                findings.append({
                    'type': 'positive',
                    'severity': 'positive',
                    'text': f'{author_name} is a verified author',
                    'explanation': 'Author profile found with credentials'
                })
            
            if author_data['article_count'] >= 50:
                findings.append({
                    'type': 'positive',
                    'severity': 'positive',
                    'text': f'Experienced author with {author_data["article_count"]} articles',
                    'explanation': 'Established track record of journalism'
                })
            elif author_data['article_count'] == 0:
                findings.append({
                    'type': 'warning',
                    'severity': 'medium',
                    'text': 'No article history found',
                    'explanation': 'Could not verify author\'s previous work'
                })
            
            if not author_data['position'] and not author_data['bio']:
                findings.append({
                    'type': 'warning',
                    'severity': 'medium',
                    'text': 'Limited author information available',
                    'explanation': 'No bio or position information found'
                })
            
            # Generate summary
            if author_data['verified']:
                summary = f"{author_name} is a verified author with a credibility score of {score}/100. "
                if author_data['position']:
                    summary += f"Currently {author_data['position']}. "
                if author_data['article_count'] > 0:
                    summary += f"Has written {author_data['article_count']} articles."
            else:
                summary = f"{author_name} could not be fully verified. Basic credibility score: {score}/100."
            
            # AI Enhancement
            if self._ai_available and author_data.get('bio'):
                logger.info("Enhancing author analysis with AI")
                
                ai_assessment = self._ai_assess_author_credibility(
                    author_name=author_name,
                    bio=author_data.get('bio', ''),
                    position=author_data.get('position', ''),
                    article_count=author_data.get('article_count', 0)
                )
                
                if ai_assessment:
                    # Add AI insights to findings
                    if ai_assessment.get('red_flags'):
                        for flag in ai_assessment['red_flags'][:2]:
                            findings.append({
                                'type': 'warning',
                                'severity': 'high',
                                'text': f'AI detected: {flag}',
                                'explanation': 'Potential credibility concern'
                            })
                    
                    if ai_assessment.get('positive_indicators'):
                        for indicator in ai_assessment['positive_indicators'][:2]:
                            findings.append({
                                'type': 'positive',
                                'severity': 'positive',
                                'text': f'AI verified: {indicator}',
                                'explanation': 'Strengthens credibility'
                            })
                    
                    author_data['ai_enhanced'] = True
                    author_data['ai_assessment'] = ai_assessment.get('overall_assessment', '')
            
            # CRITICAL: Return with 'data' wrapper
            return {
                'service': self.service_name,
                'success': True,
                'data': {
                    'author_name': author_data['author_name'],
                    'credibility_score': author_data['credibility_score'],
                    'author_score': author_data['author_score'],
                    'score': author_data['score'],
                    'level': author_data['level'],
                    'credibility_level': author_data['credibility_level'],
                    'verified': author_data['verified'],
                    'author_info': {
                        'bio': author_data['bio'],
                        'position': author_data['position'],
                        'organization': author_data['organization'],
                        'expertise': author_data['expertise_areas']
                    },
                    'metrics': {
                        'article_count': author_data['article_count'],
                        'accuracy_rate': 0,  # Placeholder
                        'awards_count': 0  # Placeholder
                    },
                    'current_position': author_data['position'],
                    'expertise_areas': author_data['expertise_areas'],
                    'findings': findings,
                    'summary': summary,
                    'bio_scraped': author_data['bio_scraped']
                },
                'metadata': {
                    'bio_scraped': author_data['bio_scraped'],
                    'ai_enhanced': author_data.get('ai_enhanced', False)
                }
            }
            
        except Exception as e:
            logger.error(f"Author analysis failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _ai_assess_author_credibility(self, author_name: str, bio: str, 
                                     position: str, article_count: int) -> Optional[Dict[str, Any]]:
        """AI method to assess author credibility"""
        if not hasattr(self, '_ai_analyze_author') or not self._ai_available:
            return None
            
        try:
            author_data = {
                'name': author_name,
                'bio': bio[:500],  # Limit for API
                'position': position,
                'article_count': article_count
            }
            
            # Call the mixin's AI method
            return self._ai_analyze_author(author_data)
        except Exception as e:
            logger.warning(f"AI author assessment failed: {e}")
            return None
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about the service"""
        info = super().get_service_info()
        info.update({
            'capabilities': [
                'Author bio extraction',
                'Credibility scoring',
                'Article count tracking',
                'Expertise identification',
                'Social media verification',
                'Organization affiliation',
                'AI-ENHANCED credibility assessment',
                'AI-powered red flag detection'
            ],
            'scoring_factors': {
                'has_bio': 20,
                'has_position': 15,
                'has_expertise': 10,
                'article_count': 20,
                'recent_activity': 5,
                'awards': 10,
                'social_presence': 5,
                'organization': 5
            },
            'ai_enhanced': self._ai_available
        })
        return info
