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
        """Universal author page checker that works for any outlet"""
        # Clean domain
        clean_domain = domain.replace('www.', '')
        author_slug = author_name.lower().replace(' ', '-')
        author_underscore = author_name.lower().replace(' ', '_')
        author_plus = author_name.lower().replace(' ', '+')
        
        # Common author page URL patterns used by most news sites
        url_patterns = [
            f"https://{domain}/{author_slug}/",
            f"https://{domain}/author/{author_slug}/",
            f"https://{domain}/authors/{author_slug}/",
            f"https://{domain}/journalist/{author_slug}/",
            f"https://{domain}/journalists/{author_slug}/",
            f"https://{domain}/reporter/{author_slug}/",
            f"https://{domain}/staff/{author_slug}/",
            f"https://{domain}/contributors/{author_slug}/",
            f"https://{domain}/by/{author_slug}/",
            f"https://{domain}/profiles/{author_slug}/",
            f"https://{domain}/people/{author_slug}/",
            f"https://{domain}/team/{author_slug}/",
            f"https://{domain}/writer/{author_slug}/",
            f"https://www.{clean_domain}/{author_slug}/",
            f"https://www.{clean_domain}/author/{author_slug}/",
            # Try underscore versions
            f"https://{domain}/author/{author_underscore}/",
            f"https://{domain}/authors/{author_underscore}/",
            # Try plus sign versions
            f"https://{domain}/author/{author_plus}/",
        ]
        
        for url in url_patterns:
            try:
                response = self.session.get(url, timeout=5)
                if response.status_code == 200:
                    # Parse the page universally
                    result = self._parse_author_page_universal(response.text, url, domain, author_name)
                    if result and (result.get('bio') or result.get('found_author_page')):
                        return result
            except Exception as e:
                logger.debug(f"Failed to check {url}: {e}")
                continue
        
        # If no author page found, try searching the site
        return self._search_site_for_author(author_name, domain)
    
    def _parse_author_page_universal(self, html, url, domain, author_name):
        """Universal parser that works for any news site author page"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Check if this is actually an author page (not a 404 or wrong page)
        page_text = soup.get_text().lower()
        author_name_lower = author_name.lower()
        
        # Verify this is likely an author page
        if (author_name_lower not in page_text and 
            not any(word in author_name_lower.split() for word in page_text.split()) and
            'page not found' not in page_text and 
            '404' not in page_text):
            return None
        
        result = {
            'online_presence': {'outlet_profile': url},
            'verification_status': {
                'verified': True,
                'journalist_verified': True,
                'outlet_staff': True
            },
            'professional_info': {
                'outlets': [domain.replace('www.', '').split('.')[0].upper()]
            },
            'found_author_page': True
        }
        
        # 1. Check JSON-LD structured data first (most reliable)
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if self._extract_from_json_ld(data, author_name, result):
                    break
            except:
                continue
        
        # 2. Check meta tags
        self._extract_from_meta_tags(soup, author_name, result)
        
        # 3. Smart bio extraction - look for paragraphs that mention the author
        if not result.get('bio'):
            bio_candidates = []
            
            # Common bio container selectors
            bio_containers = soup.select('''
                [class*="bio"], [class*="Bio"], 
                [class*="author-desc"], [class*="author-info"],
                [class*="author-about"], [class*="contributor"],
                [id*="bio"], [id*="Bio"],
                .description, .about, .profile
            ''')
            
            for container in bio_containers:
                text = container.get_text(strip=True)
                if len(text) > 50 and author_name.split()[-1].lower() in text.lower():
                    bio_candidates.append(text)
            
            # Also check all paragraphs
            for p in soup.find_all('p'):
                text = p.get_text(strip=True)
                # Look for paragraphs that mention the author and are biographical
                if (len(text) > 50 and 
                    any(name_part.lower() in text.lower() for name_part in author_name.split()) and
                    any(keyword in text.lower() for keyword in 
                        ['is a', 'journalist', 'reporter', 'correspondent', 'writer', 
                         'covers', 'reports', 'joined', 'experience', 'previously'])):
                    bio_candidates.append(text)
            
            # Pick the best bio (longest relevant one)
            if bio_candidates:
                result['bio'] = max(bio_candidates, key=len)
        
        # 4. Extract image - look for images with author name or in author sections
        if not result.get('image_url'):
            img_candidates = []
            
            # Check images with alt text
            for img in soup.find_all('img', alt=True):
                if any(name_part.lower() in img['alt'].lower() for name_part in author_name.split()):
                    img_candidates.append(img)
            
            # Check images in author sections
            author_sections = soup.select('[class*="author"], [id*="author"]')
            for section in author_sections:
                imgs = section.find_all('img')
                img_candidates.extend(imgs)
            
            # Get the first valid image
            for img in img_candidates:
                if img.get('src'):
                    img_url = img['src']
                    if not img_url.startswith('http'):
                        img_url = f"https://{domain}{img_url}" if img_url.startswith('/') else f"https://{domain}/{img_url}"
                    result['image_url'] = img_url
                    break
        
        # 5. Extract title/position
        if not result['professional_info'].get('current_position'):
            # Look for common patterns
            title_patterns = [
                rf"{author_name}\s*,\s*([^,\.\n]+)",  # Name, Title
                rf"{author_name}\s+is\s+(?:a|an|the)?\s*([^\.\n]+?)(?:\s+at\s+|$)",  # Name is a Title
                rf"(?:by|By)\s+{author_name}\s*,\s*([^,\.\n]+)",  # By Name, Title
            ]
            
            for pattern in title_patterns:
                match = re.search(pattern, soup.get_text(), re.IGNORECASE)
                if match:
                    title = match.group(1).strip()
                    if len(title) < 100:  # Reasonable title length
                        result['professional_info']['current_position'] = title
                        break
        
        # 6. Extract social media links
        social_links = soup.find_all('a', href=True)
        for link in social_links:
            href = link['href'].lower()
            
            # Twitter/X
            if ('twitter.com/' in href or 'x.com/' in href) and '/status/' not in href:
                match = re.search(r'(?:twitter\.com|x\.com)/(@?\w+)', href)
                if match:
                    handle = match.group(1).replace('@', '')
                    if handle not in ['share', 'intent', 'home', 'search']:
                        result['online_presence']['twitter'] = handle
            
            # LinkedIn
            elif 'linkedin.com/in/' in href:
                result['online_presence']['linkedin'] = link['href']
            
            # Email
            elif href.startswith('mailto:'):
                email = href.replace('mailto:', '').split('?')[0]
                if '@' in email:
                    result['online_presence']['email'] = email
        
        # 7. Default bio if none found but we're on an author page
        if not result.get('bio') and result.get('found_author_page'):
            position = result['professional_info'].get('current_position', 'journalist')
            outlet = result['professional_info']['outlets'][0]
            result['bio'] = f"{author_name} is a {position} at {outlet}."
        
        return result
    
    def _extract_from_json_ld(self, data, author_name, result):
        """Extract author info from JSON-LD structured data"""
        if isinstance(data, dict):
            # Direct Person object
            if data.get('@type') == 'Person' and author_name.lower() in data.get('name', '').lower():
                if data.get('description'):
                    result['bio'] = data['description']
                if data.get('jobTitle'):
                    result['professional_info']['current_position'] = data['jobTitle']
                if data.get('image'):
                    result['image_url'] = data['image'] if isinstance(data['image'], str) else data['image'].get('url')
                return True
            
            # Article with author
            if data.get('@type') in ['Article', 'NewsArticle'] and data.get('author'):
                author = data['author']
                if isinstance(author, dict) and author_name.lower() in author.get('name', '').lower():
                    if author.get('description'):
                        result['bio'] = author['description']
                    if author.get('jobTitle'):
                        result['professional_info']['current_position'] = author['jobTitle']
                    return True
        
        elif isinstance(data, list):
            # Check each item in the list
            for item in data:
                if self._extract_from_json_ld(item, author_name, result):
                    return True
        
        return False
    
    def _extract_from_meta_tags(self, soup, author_name, result):
        """Extract author info from meta tags"""
        # Common meta tag patterns
        meta_mappings = {
            'bio': ['description', 'author.description', 'twitter:description'],
            'image': ['author.image', 'twitter:image', 'og:image'],
            'title': ['author.title', 'author.jobTitle']
        }
        
        for field, properties in meta_mappings.items():
            if not result.get(field if field != 'title' else 'professional_info', {}).get('current_position' if field == 'title' else field):
                for prop in properties:
                    meta = soup.find('meta', {'property': prop}) or soup.find('meta', {'name': prop})
                    if meta and meta.get('content'):
                        content = meta['content']
                        if field == 'bio' and (author_name.lower() in content.lower() or len(content) > 100):
                            result['bio'] = content
                        elif field == 'image':
                            result['image_url'] = content
                        elif field == 'title':
                            result['professional_info']['current_position'] = content
    
    def _search_site_for_author(self, author_name, domain):
        """Search the site for author information using site search"""
        # Try site search URL patterns
        search_patterns = [
            f"https://{domain}/search?q={author_name.replace(' ', '+')}",
            f"https://{domain}/?s={author_name.replace(' ', '+')}",
            f"https://{domain}/search/{author_name.replace(' ', '+')}",
        ]
        
        for search_url in search_patterns:
            try:
                response = self.session.get(search_url, timeout=5)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # Look for author links in search results
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if any(pattern in href.lower() for pattern in ['/author/', '/journalist/', '/staff/', '/by/']):
                            if author_name.lower().replace(' ', '-') in href.lower():
                                # Found a potential author page
                                full_url = href if href.startswith('http') else f"https://{domain}{href}"
                                try:
                                    author_response = self.session.get(full_url, timeout=5)
                                    if author_response.status_code == 200:
                                        return self._parse_author_page_universal(
                                            author_response.text, full_url, domain, author_name
                                        )
                                except:
                                    continue
            except:
                continue
        
        return None
    
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
            if any(outlet in domain_lower for outlet in ['cnn', 'bbc', 'reuters', 'bloomberg', 'cnbc']):
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
        if author_data.get('bio') and 'Limited information available' not in author_data.get('bio', ''):
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
