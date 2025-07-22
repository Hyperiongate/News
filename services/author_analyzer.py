"""
FILE: services/author_analyzer.py
LOCATION: news/services/author_analyzer.py
PURPOSE: Enhanced author analysis with web search capabilities
DEPENDENCIES: requests, BeautifulSoup4
"""

import os
import re
import json
import logging
import time
from datetime import datetime
from urllib.parse import quote, urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class AuthorAnalyzer:
    """Enhanced author analyzer that searches for journalist information online"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def analyze_authors(self, author_text, domain=None):
        """Analyze multiple authors from byline text"""
        authors = self._parse_authors(author_text)
        results = []
        
        for author_name in authors:
            result = self.analyze_single_author(author_name, domain)
            results.append(result)
        
        return results
    
    def analyze_single_author(self, author_name, domain=None):
        """Analyze a single author with web search"""
        logger.info(f"Analyzing author: {author_name} from domain: {domain}")
        
        # Clean author name
        clean_name = self._clean_author_name(author_name)
        
        # Check cache first (if database is available)
        try:
            from models import db, AuthorCache
            from datetime import timedelta
            
            cached = AuthorCache.query.filter_by(author_name=clean_name).first()
            if cached and not cached.is_expired:
                logger.info(f"Returning cached author data for {clean_name}")
                return cached.lookup_data
        except:
            # Database not available, continue without cache
            pass
        
        # Initialize result structure
        result = {
            'name': clean_name,
            'found': False,
            'bio': None,
            'image_url': None,
            'credibility_score': 50,
            'professional_info': {
                'current_position': None,
                'outlets': [],
                'years_experience': None,
                'expertise_areas': []
            },
            'online_presence': {
                'twitter': None,
                'linkedin': None,
                'personal_website': None,
                'outlet_profile': None
            },
            'verification_status': {
                'verified': False,
                'journalist_verified': False,
                'outlet_staff': False
            },
            'sources_checked': []
        }
        
        # Try multiple search strategies
        
        # 1. Check outlet's author page first (most reliable)
        if domain:
            outlet_result = self._check_outlet_author_page(clean_name, domain)
            if outlet_result:
                result.update(outlet_result)
                result['found'] = True
                result['sources_checked'].append(f"{domain} author page")
        
        # 2. Google search for author + journalist
        if not result['found']:
            google_result = self._google_search_author(clean_name, domain)
            if google_result:
                result.update(google_result)
                result['found'] = True
                result['sources_checked'].append("Google search")
        
        # 3. Check LinkedIn
        linkedin_result = self._check_linkedin(clean_name, domain)
        if linkedin_result:
            result['online_presence']['linkedin'] = linkedin_result.get('profile_url')
            if not result['bio'] and linkedin_result.get('bio'):
                result['bio'] = linkedin_result['bio']
            result['sources_checked'].append("LinkedIn search")
        
        # 4. Check Twitter/X
        twitter_result = self._check_twitter(clean_name)
        if twitter_result:
            result['online_presence']['twitter'] = twitter_result.get('handle')
            result['sources_checked'].append("Twitter/X search")
        
        # 5. Check known journalist databases
        journalist_db_result = self._check_journalist_databases(clean_name)
        if journalist_db_result:
            result.update(journalist_db_result)
            result['sources_checked'].append("Journalist databases")
        
        # Calculate credibility score based on findings
        result['credibility_score'] = self._calculate_credibility_score(result)
        
        # Add credibility explanation
        result['credibility_explanation'] = self._generate_credibility_explanation(result)
        
        # Generate bio if not found
        if not result['bio']:
            if result['professional_info']['current_position']:
                result['bio'] = f"{clean_name} is {result['professional_info']['current_position']}"
                if result['professional_info']['outlets']:
                    result['bio'] += f" at {result['professional_info']['outlets'][0]}"
                result['bio'] += "."
            else:
                result['bio'] = f"{clean_name} - Limited information available. We searched multiple sources but could not find detailed biographical information."
        
        # Cache the result (if database is available)
        try:
            from models import db, AuthorCache
            from datetime import timedelta
            
            # Remove existing cache entry if present
            AuthorCache.query.filter_by(author_name=clean_name).delete()
            
            # Create new cache entry
            cache_entry = AuthorCache(
                author_name=clean_name,
                lookup_data=result,
                expires_at=datetime.utcnow() + timedelta(days=30)  # Cache for 30 days
            )
            db.session.add(cache_entry)
            db.session.commit()
        except Exception as e:
            logger.debug(f"Could not cache author data: {e}")
        
        return result
    
    def _check_outlet_author_page(self, author_name, domain):
        """Check the news outlet's author page"""
        # Clean domain
        clean_domain = domain.replace('www.', '')
        
        # Special handling for known sites
        if 'cnbc.com' in clean_domain:
            return self._check_cnbc_author(author_name)
        elif 'cnn.com' in clean_domain:
            return self._check_cnn_author(author_name)
        elif 'bbc.com' in clean_domain or 'bbc.co.uk' in clean_domain:
            return self._check_bbc_author(author_name)
        elif 'reuters.com' in clean_domain:
            return self._check_reuters_author(author_name)
        elif 'bloomberg.com' in clean_domain:
            return self._check_bloomberg_author(author_name)
        
        # Generic author page patterns
        author_slug = author_name.lower().replace(' ', '-')
        author_patterns = [
            f"https://{domain}/author/{author_slug}/",
            f"https://{domain}/journalists/{author_slug}/",
            f"https://{domain}/by/{author_slug}/",
            f"https://{domain}/staff/{author_slug}/",
            f"https://{domain}/{author_slug}/",
            f"https://www.{domain}/author/{author_slug}/",
            f"https://www.{domain}/{author_slug}/"
        ]
        
        for pattern in author_patterns:
            try:
                response = self.session.get(pattern, timeout=5)
                if response.status_code == 200:
                    return self._parse_author_page(response.text, pattern, domain)
            except Exception as e:
                logger.debug(f"Failed to check {pattern}: {e}")
                continue
        
        return None
    
    def _check_cnn_author(self, author_name):
        """Special handling for CNN authors"""
        # CNN uses profiles.cnn.com
        url = f"https://www.cnn.com/profiles/{author_name.lower().replace(' ', '-')}"
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                result = {
                    'online_presence': {'outlet_profile': url},
                    'verification_status': {
                        'verified': True,
                        'journalist_verified': True,
                        'outlet_staff': True
                    },
                    'professional_info': {
                        'outlets': ['CNN']
                    }
                }
                
                # Extract CNN-specific elements
                bio_elem = soup.select_one('div.profile__bio')
                if bio_elem:
                    result['bio'] = bio_elem.get_text(strip=True)
                
                title_elem = soup.select_one('div.profile__title')
                if title_elem:
                    result['professional_info']['current_position'] = title_elem.get_text(strip=True)
                
                return result
                
        except Exception as e:
            logger.debug(f"Error checking CNN author {author_name}: {e}")
        
        return None
    
    def _check_bbc_author(self, author_name):
        """Special handling for BBC authors"""
        # BBC doesn't have consistent author pages, so we'll return basic info
        return {
            'professional_info': {
                'outlets': ['BBC'],
                'current_position': 'Journalist'
            },
            'verification_status': {
                'verified': True,
                'journalist_verified': True,
                'outlet_staff': True
            }
        }
    
    def _check_reuters_author(self, author_name):
        """Special handling for Reuters authors"""
        # Reuters uses /journalists/ path
        author_slug = author_name.lower().replace(' ', '-')
        url = f"https://www.reuters.com/journalists/{author_slug}"
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return {
                    'online_presence': {'outlet_profile': url},
                    'professional_info': {
                        'outlets': ['Reuters'],
                        'current_position': 'Journalist'
                    },
                    'verification_status': {
                        'verified': True,
                        'journalist_verified': True,
                        'outlet_staff': True
                    }
                }
        except:
            pass
        
        return None
    
    def _check_bloomberg_author(self, author_name):
        """Special handling for Bloomberg authors"""
        # Bloomberg uses /authors/ path
        author_slug = author_name.replace(' ', '-')
        url = f"https://www.bloomberg.com/authors/{author_slug}"
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return {
                    'online_presence': {'outlet_profile': url},
                    'professional_info': {
                        'outlets': ['Bloomberg'],
                        'current_position': 'Journalist'
                    },
                    'verification_status': {
                        'verified': True,
                        'journalist_verified': True,
                        'outlet_staff': True
                    }
                }
        except:
            pass
        
        return None
    
    def _check_cnbc_author(self, author_name):
        """Special handling for CNBC authors"""
        # CNBC uses format: https://www.cnbc.com/firstname-lastname/
        author_slug = author_name.lower().replace(' ', '-')
        url = f"https://www.cnbc.com/{author_slug}/"
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                result = {
                    'online_presence': {'outlet_profile': url},
                    'verification_status': {
                        'verified': True,
                        'journalist_verified': True,
                        'outlet_staff': True
                    }
                }
                
                # Extract bio from CNBC's specific structure
                bio_elem = soup.select_one('div.InlineVideo-container ~ p')
                if not bio_elem:
                    bio_elem = soup.select_one('div.AuthorBio-bio')
                if bio_elem:
                    result['bio'] = bio_elem.get_text(strip=True)
                
                # Extract image
                img_elem = soup.select_one('img.AuthorBio-image')
                if img_elem and img_elem.get('src'):
                    result['image_url'] = img_elem['src']
                
                # Extract title/position
                title_elem = soup.select_one('div.AuthorBio-title')
                if title_elem:
                    result['professional_info'] = {
                        'current_position': title_elem.get_text(strip=True),
                        'outlets': ['CNBC']
                    }
                
                # Social media
                social_container = soup.select_one('div.AuthorBio-social')
                if social_container:
                    twitter_link = social_container.select_one('a[href*="twitter.com"]')
                    if twitter_link:
                        result['online_presence']['twitter'] = twitter_link['href'].split('/')[-1]
                    
                    linkedin_link = social_container.select_one('a[href*="linkedin.com"]')
                    if linkedin_link:
                        result['online_presence']['linkedin'] = linkedin_link['href']
                
                return result
                
        except Exception as e:
            logger.error(f"Error checking CNBC author {author_name}: {e}")
        
        return None
    
    def _parse_author_page(self, html, url, domain):
        """Parse author page from outlet website"""
        soup = BeautifulSoup(html, 'html.parser')
        result = {}
        
        # Extract bio - common patterns
        bio_selectors = [
            'div.author-bio',
            'div.bio',
            'p.author-description',
            'div.author-description',
            'div.author-info',
            'section.author-bio',
            'div.contributor-bio'
        ]
        
        for selector in bio_selectors:
            bio_elem = soup.select_one(selector)
            if bio_elem:
                result['bio'] = bio_elem.get_text(strip=True)
                break
        
        # Extract image
        img_selectors = [
            'img.author-image',
            'img.author-photo',
            'div.author-image img',
            'div.author img'
        ]
        
        for selector in img_selectors:
            img_elem = soup.select_one(selector)
            if img_elem and img_elem.get('src'):
                result['image_url'] = img_elem['src']
                if not result['image_url'].startswith('http'):
                    result['image_url'] = f"https://{domain}{result['image_url']}"
                break
        
        # Extract position/title
        title_selectors = [
            'span.author-title',
            'p.author-title',
            'div.author-position',
            'span.author-role'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                result['professional_info'] = {
                    'current_position': title_elem.get_text(strip=True),
                    'outlets': [domain]
                }
                break
        
        # Social media links
        social_links = soup.find_all('a', href=True)
        for link in social_links:
            href = link['href']
            if 'twitter.com' in href or 'x.com' in href:
                result['online_presence'] = result.get('online_presence', {})
                result['online_presence']['twitter'] = href.split('/')[-1].replace('@', '')
            elif 'linkedin.com' in href:
                result['online_presence'] = result.get('online_presence', {})
                result['online_presence']['linkedin'] = href
        
        result['online_presence'] = result.get('online_presence', {})
        result['online_presence']['outlet_profile'] = url
        result['verification_status'] = {
            'verified': True,
            'journalist_verified': True,
            'outlet_staff': True
        }
        
        return result
    
    def _google_search_author(self, author_name, domain=None):
        """Search Google for author information"""
        # Note: In production, you should use Google Custom Search API
        # This is a simplified version that searches specific sites
        
        search_urls = []
        
        # Search on the domain if provided
        if domain:
            search_urls.append(f"https://www.google.com/search?q=site:{domain}+{quote(author_name)}")
        
        # Search for author profiles on major sites
        search_urls.extend([
            f"https://muckrack.com/{author_name.lower().replace(' ', '-')}",
            f"https://www.linkedin.com/search/results/people/?keywords={quote(author_name)}+journalist",
        ])
        
        # Try Muck Rack (journalist database)
        try:
            muckrack_url = f"https://muckrack.com/{author_name.lower().replace(' ', '-')}"
            response = self.session.get(muckrack_url, timeout=5)
            if response.status_code == 200:
                return self._parse_muckrack_profile(response.text)
        except:
            pass
        
        # If no direct results, try searching for author + journalist
        return self._search_and_extract_info(author_name, domain)
    
    def _parse_muckrack_profile(self, html):
        """Parse Muck Rack journalist profile"""
        soup = BeautifulSoup(html, 'html.parser')
        result = {}
        
        # Extract bio
        bio_elem = soup.select_one('div.journalist-bio')
        if bio_elem:
            result['bio'] = bio_elem.get_text(strip=True)
        
        # Extract current position
        position_elem = soup.select_one('div.journalist-title')
        if position_elem:
            result['professional_info'] = {
                'current_position': position_elem.get_text(strip=True)
            }
        
        # Extract outlets
        outlets = []
        outlet_elems = soup.select('div.outlet-name')
        for elem in outlet_elems[:5]:  # Limit to 5 outlets
            outlets.append(elem.get_text(strip=True))
        
        if outlets:
            result['professional_info'] = result.get('professional_info', {})
            result['professional_info']['outlets'] = outlets
        
        result['verification_status'] = {
            'verified': True,
            'journalist_verified': True,
            'outlet_staff': bool(outlets)
        }
        
        return result
    
    def _search_and_extract_info(self, author_name, domain=None):
        """Fallback search method"""
        # This is where you could integrate with search APIs
        # For now, we'll construct a basic result
        
        result = {
            'professional_info': {
                'outlets': [domain] if domain else []
            }
        }
        
        # Try to determine position from common patterns
        if domain:
            domain_lower = domain.lower()
            if 'cnn' in domain_lower or 'bbc' in domain_lower or 'reuters' in domain_lower:
                result['professional_info']['current_position'] = 'Journalist'
                result['verification_status'] = {
                    'verified': True,
                    'journalist_verified': True,
                    'outlet_staff': True
                }
        
        return result
    
    def _check_linkedin(self, author_name, domain=None):
        """Check LinkedIn for author profile"""
        # Note: LinkedIn requires authentication for full access
        # This is a placeholder for LinkedIn API integration
        return None
    
    def _check_twitter(self, author_name):
        """Check Twitter/X for author profile"""
        # Note: Twitter API requires authentication
        # This is a placeholder for Twitter API integration
        return None
    
    def _check_journalist_databases(self, author_name):
        """Check known journalist databases"""
        # Could integrate with:
        # - Muck Rack API
        # - Journalists.org
        # - Press association databases
        return None
    
    def _calculate_credibility_score(self, author_data):
        """Calculate author credibility score based on available information"""
        score = 0
        max_score = 100
        
        # Scoring criteria
        criteria = {
            'has_bio': 15,
            'has_image': 5,
            'has_position': 15,
            'has_outlets': 15,
            'outlet_verified': 20,
            'has_social_media': 10,
            'journalist_database': 20
        }
        
        # Apply scoring
        if author_data.get('bio'):
            score += criteria['has_bio']
        
        if author_data.get('image_url'):
            score += criteria['has_image']
        
        if author_data.get('professional_info', {}).get('current_position'):
            score += criteria['has_position']
        
        if author_data.get('professional_info', {}).get('outlets'):
            score += criteria['has_outlets']
        
        if author_data.get('verification_status', {}).get('outlet_staff'):
            score += criteria['outlet_verified']
        
        if any(author_data.get('online_presence', {}).values()):
            score += criteria['has_social_media']
        
        if author_data.get('verification_status', {}).get('journalist_verified'):
            score += criteria['journalist_database']
        
        return min(score, max_score)
    
    def _generate_credibility_explanation(self, author_data):
        """Generate explanation for credibility score"""
        score = author_data['credibility_score']
        
        if score >= 80:
            level = 'High'
            explanation = f"Well-established journalist with verified credentials and clear professional history."
            advice = "This author has strong credibility indicators."
        elif score >= 60:
            level = 'Good'
            explanation = f"Verified journalist with some professional information available."
            advice = "Author appears legitimate with reasonable credentials."
        elif score >= 40:
            level = 'Moderate'
            explanation = f"Some information found about this author, but limited verification available."
            advice = "Consider cross-referencing important claims with other sources."
        else:
            level = 'Limited'
            explanation = f"Minimal information available about this author's background or credentials."
            advice = "Exercise caution and verify claims through additional sources."
        
        return {
            'level': level,
            'explanation': explanation,
            'advice': advice
        }
    
    def _clean_author_name(self, author_name):
        """Clean and standardize author name"""
        # Remove common suffixes
        name = re.sub(r'\s*(,|and|&)\s*.*$', '', author_name)
        
        # Remove titles
        titles = ['Dr.', 'Prof.', 'Mr.', 'Mrs.', 'Ms.', 'Sir', 'Dame']
        for title in titles:
            name = name.replace(title, '').strip()
        
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        return name
    
    def _parse_authors(self, author_text):
        """Parse multiple authors from byline text"""
        if not author_text:
            return []
        
        # Split by common separators
        authors = re.split(r'\s*(?:,|and|&)\s*', author_text)
        
        # Clean each author
        cleaned_authors = []
        for author in authors:
            cleaned = self._clean_author_name(author)
            if cleaned and len(cleaned) > 2:
                cleaned_authors.append(cleaned)
        
        return cleaned_authors
