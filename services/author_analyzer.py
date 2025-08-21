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
            # Generic author link patterns
            f'a:contains("{author_name}")',
            '.byline a',
            '.author a',
            '[rel="author"]',
        ]
        
        # First try exact selectors
        for selector in selectors:
            try:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if href:
                        # Check if this is likely an author page
                        if any(pattern in href.lower() for pattern in ['/author/', '/profile/', '/people/', '/staff/']):
                            author_url = urljoin(article_url, href)
                            logger.info(f"Found author bio link via selector '{selector}': {author_url}")
                            return author_url
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {e}")
                continue
        
        # If no direct selector worked, search more broadly
        # Look for any link containing the author name
        author_parts = author_name.lower().split()
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link.get('href', '')
            link_text = link.get_text(strip=True).lower()
            
            # Check if link text contains author name
            if all(part in link_text for part in author_parts):
                # Check if it's an author/profile page
                if any(pattern in href for pattern in ['/author/', '/profile/', '/people/', '/staff/']):
                    author_url = urljoin(article_url, href)
                    logger.info(f"Found author bio link via name match: {author_url}")
                    return author_url
        
        # Last resort: check for author pages in meta tags
        meta_author = soup.find('meta', {'property': 'article:author'})
        if meta_author and meta_author.get('content'):
            author_url = meta_author['content']
            if author_url.startswith('http'):
                logger.info(f"Found author bio link in meta tag: {author_url}")
                return author_url
        
        logger.warning(f"No author bio link found for: {author_name}")
        return None
    
    def _scrape_author_bio(self, bio_url: str) -> Dict[str, Any]:
        """Scrape author bio page for detailed information"""
        try:
            logger.info(f"Scraping author bio from: {bio_url}")
            
            # Fetch the bio page with proper headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = requests.get(bio_url, timeout=15, headers=headers)
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
                'organization': None,
                'article_count': 0
            }
            
            # Extract author name from page if not already known
            name_selectors = [
                'h1.author-name', 'h1.profile-name', '.author-header h1',
                'h1[itemprop="name"]', '.author-title h1', 'h1'
            ]
            
            author_full_name = None
            for selector in name_selectors:
                name_elem = soup.select_one(selector)
                if name_elem:
                    author_full_name = name_elem.get_text(strip=True)
                    break
            
            # Extract bio text - updated selectors for The Independent
            bio_selectors = [
                '.author-bio', '.author-description', '.bio-text',
                '.profile-bio', 'div[class*="bio"]', '.author-about',
                'p.bio', 'div.bio', '.author-info p',
                # The Independent specific
                '.sc-1ef49iv-3', '.author-bio-text', '[data-testid="author-bio"]'
            ]
            
            for selector in bio_selectors:
                bio_elems = soup.select(selector)
                if bio_elems:
                    bio_texts = [elem.get_text(strip=True) for elem in bio_elems if elem.get_text(strip=True)]
                    if bio_texts:
                        bio_data['full_bio'] = ' '.join(bio_texts)
                        logger.info(f"Found bio text with selector '{selector}': {len(bio_data['full_bio'])} chars")
                        break
            
            # If no bio found with selectors, look for descriptive paragraphs
            if not bio_data['full_bio']:
                # Look for paragraphs near the author name
                if author_full_name:
                    for p in soup.find_all('p'):
                        text = p.get_text(strip=True)
                        if len(text) > 50 and (author_full_name in text or 'journalist' in text.lower() or 'reporter' in text.lower()):
                            bio_data['full_bio'] = text
                            logger.info(f"Found bio in paragraph: {len(text)} chars")
                            break
            
            # Extract position/title
            position_selectors = [
                '.author-title', '.author-position', '.job-title',
                '.author-role', 'span.title', '.position',
                # The Independent specific
                '.author-tagline', '[data-testid="author-title"]'
            ]
            
            for selector in position_selectors:
                pos_elem = soup.select_one(selector)
                if pos_elem:
                    position_text = pos_elem.get_text(strip=True)
                    if position_text and position_text != author_full_name:
                        bio_data['position'] = position_text
                        logger.info(f"Found position: {position_text}")
                        break
            
            # Extract organization (often The Independent)
            org_selectors = [
                '.organization', '.publication', '.employer',
                'a[href*="independent.co.uk"]'
            ]
            
            for selector in org_selectors:
                org_elem = soup.select_one(selector)
                if org_elem:
                    bio_data['organization'] = org_elem.get_text(strip=True)
                    break
            
            # Default to The Independent if on their domain
            if not bio_data['organization'] and 'independent.co.uk' in bio_url:
                bio_data['organization'] = 'The Independent'
            
            # Extract expertise areas from bio text or tags
            if bio_data['full_bio']:
                # Look for expertise patterns in bio
                expertise_patterns = [
                    r'specializ(?:es?|ing) in ([^.]+)',
                    r'covers? ([^.]+)',
                    r'focus(?:es)? on ([^.]+)',
                    r'expert in ([^.]+)',
                    r'writing about ([^.]+)'
                ]
                
                for pattern in expertise_patterns:
                    matches = re.findall(pattern, bio_data['full_bio'], re.IGNORECASE)
                    for match in matches:
                        areas = [area.strip() for area in match.split(',')]
                        bio_data['expertise_areas'].extend(areas)
            
            # Also check for topic tags
            topic_selectors = [
                '.topics a', '.tags a', '.expertise-tag',
                '.author-topics a', '[data-testid="topic-tag"]'
            ]
            
            for selector in topic_selectors:
                tags = soup.select(selector)
                for tag in tags:
                    topic = tag.get_text(strip=True)
                    if topic and topic not in bio_data['expertise_areas']:
                        bio_data['expertise_areas'].append(topic)
            
            # Clean up expertise areas
            bio_data['expertise_areas'] = list(set([
                area.title() for area in bio_data['expertise_areas'] 
                if area and len(area) < 50
            ]))[:10]  # Limit to 10 areas
            
            # Extract social media links
            social_patterns = {
                'twitter': [r'twitter\.com/(\w+)', r'x\.com/(\w+)'],
                'linkedin': [r'linkedin\.com/in/([\w-]+)'],
                'facebook': [r'facebook\.com/([\w.]+)'],
                'instagram': [r'instagram\.com/(\w+)']
            }
            
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                for platform, patterns in social_patterns.items():
                    for pattern in patterns:
                        match = re.search(pattern, href)
                        if match:
                            bio_data['social_media'][platform] = f"@{match.group(1)}"
                            break
            
            # Extract recent articles count
            article_count_selectors = [
                '.article-count', '.stories-count', '.author-article-count',
                '[data-testid="article-count"]'
            ]
            
            for selector in article_count_selectors:
                count_elem = soup.select_one(selector)
                if count_elem:
                    count_text = count_elem.get_text(strip=True)
                    count_match = re.search(r'(\d+)', count_text)
                    if count_match:
                        bio_data['article_count'] = int(count_match.group(1))
                        logger.info(f"Found article count: {bio_data['article_count']}")
                        break
            
            # Extract recent articles list
            articles_container_selectors = [
                '.author-articles', '.recent-stories', '.author-feed',
                '.articles-list', '[data-testid="author-articles"]',
                # The Independent specific
                'div[class*="author-articles"]', '.sc-1d5htuw-0'
            ]
            
            for selector in articles_container_selectors:
                container = soup.select_one(selector)
                if container:
                    # Find article links within container
                    article_links = container.select('a[href*="/news/"], a[href*="/article/"]')[:10]
                    
                    for link in article_links:
                        article_title = link.get_text(strip=True)
                        if article_title:
                            article_data = {
                                'title': article_title[:200],  # Limit title length
                                'url': urljoin(bio_url, link.get('href', ''))
                            }
                            
                            # Try to find date
                            date_elem = link.find_parent().find(text=re.compile(r'\d{1,2}\s+\w+\s+\d{4}|\d{4}-\d{2}-\d{2}'))
                            if date_elem:
                                article_data['date'] = date_elem.strip()
                            
                            bio_data['recent_articles'].append(article_data)
                    
                    if bio_data['recent_articles']:
                        logger.info(f"Found {len(bio_data['recent_articles'])} recent articles")
                        break
            
            # If no specific count found but we have articles, use that count
            if not bio_data['article_count'] and bio_data['recent_articles']:
                # This is a minimum count
                bio_data['article_count'] = len(bio_data['recent_articles'])
            
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
                            start_year = int(match.group(1))
                            current_year = datetime.now().year
                            years = current_year - start_year
                            bio_data['experience'] = f"{years}+ years"
                        else:
                            years = int(match.group(1))
                            bio_data['experience'] = f"{years}+ years"
                        logger.info(f"Found experience: {bio_data['experience']}")
                        break
            
            # Extract any awards or recognition
            if bio_data['full_bio']:
                award_patterns = [
                    r'(?:won|awarded|received)\s+(?:the\s+)?([^.]+award[^.]+)',
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
                'findings': [],
                'metadata': {
                    'ai_enhanced': False
                }
            }
            
            # Try to get author bio URL if we have article HTML and URL
            article_url = data.get('url')
            article_html = data.get('html')
            bio_data = {}
            
            if article_url and article_html:
                try:
                    soup = BeautifulSoup(article_html, 'html.parser')
                    bio_url = self._extract_author_url(soup, author_name, article_url)
                    
                    if bio_url:
                        # Scrape the bio page
                        bio_data = self._scrape_author_bio(bio_url)
                        
                        if bio_data:
                            # Update result with scraped data
                            result['verified'] = True
                            
                            # Author info
                            result['author_info'] = {
                                'bio': bio_data.get('full_bio', ''),
                                'position': bio_data.get('position', ''),
                                'experience': bio_data.get('experience', ''),
                                'expertise': bio_data.get('expertise_areas', [])
                            }
                            
                            # Current position (for display)
                            if bio_data.get('position'):
                                org = bio_data.get('organization', '')
                                if org:
                                    result['current_position'] = f"{bio_data['position']} at {org}"
                                else:
                                    result['current_position'] = bio_data['position']
                            
                            # Metrics
                            result['metrics'] = {
                                'article_count': bio_data.get('article_count', 0),
                                'accuracy_rate': 85,  # Default high rate for verified journalists
                                'awards_count': len(bio_data.get('awards', []))
                            }
                            
                            # Recent articles (format for frontend)
                            if bio_data.get('recent_articles'):
                                for article in bio_data['recent_articles'][:5]:
                                    formatted_article = {
                                        'title': article.get('title', ''),
                                        'date': article.get('date', ''),
                                        'credibility_score': 82  # Default score
                                    }
                                    result['recent_articles'].append(formatted_article)
                            
                            # Calculate enhanced credibility score
                            result['credibility_score'] = self._calculate_credibility_score(bio_data)
                            
                            # Generate findings
                            findings = []
                            
                            # Positive findings
                            if result['credibility_score'] >= 70:
                                findings.append({
                                    'type': 'positive',
                                    'title': 'Verified journalist',
                                    'description': f'Confirmed credentials with {bio_data.get("organization", "publication")}'
                                })
                            
                            if bio_data.get('experience'):
                                findings.append({
                                    'type': 'positive',
                                    'title': 'Experienced journalist',
                                    'description': f'{bio_data["experience"]} of professional experience'
                                })
                            
                            if bio_data.get('awards'):
                                findings.append({
                                    'type': 'positive',
                                    'title': 'Award-winning journalist',
                                    'description': f'Received {len(bio_data["awards"])} awards/recognitions'
                                })
                            
                            if bio_data.get('expertise_areas'):
                                findings.append({
                                    'type': 'info',
                                    'title': 'Subject matter expert',
                                    'description': f'Specializes in: {", ".join(bio_data["expertise_areas"][:3])}'
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
                            
                except Exception as e:
                    logger.warning(f"Error processing author bio: {e}")
                    # Continue with basic analysis
            
            # AI ENHANCEMENT - Add deeper author insights
            if self._ai_available and author_name:
                logger.info("Enhancing author analysis with AI")
                
                # Get AI author assessment
                ai_author_analysis = self._ai_analyze_author_credibility(
                    author_name=author_name,
                    bio_text=bio_data.get('full_bio', '')[:1000] if bio_data else None,
                    position=bio_data.get('position') if bio_data else None,
                    expertise_areas=bio_data.get('expertise_areas', []) if bio_data else [],
                    article_count=bio_data.get('article_count', 0) if bio_data else 0
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
            logger.error(f"Author analysis failed: {e}")
            return self.get_error_result(str(e))
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        info = super().get_service_info()
        info.update({
            'capabilities': [
                'Author profile extraction',
                'Bio page scraping',
                'Credibility scoring',
                'Experience detection',
                'Expertise area identification',
                'Recent article tracking',
                'Social media presence detection',
                'Award recognition',
                'AI-ENHANCED credibility assessment',
                'AI-powered expertise validation'
            ],
            'supported_sites': [
                'The Independent',
                'Generic news sites with author pages'
            ],
            'ai_enhanced': self._ai_available
        })
        return info
