"""
FILE: services/author_analyzer.py
PURPOSE: Fixed author analyzer that actually searches for author information
LOCATION: services/author_analyzer.py
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
        
        # Initialize result structure with ALL fields having safe defaults
        result = {
            'name': clean_name,
            'found': False,
            'bio': None,
            'image_url': None,
            'credibility_score': 50,
            'articles_count': 0,
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
                'outlet_profile': None,
                'email': None
            },
            'verification_status': {
                'verified': False,
                'journalist_verified': False,
                'outlet_staff': False
            },
            'sources_checked': [],
            'issues_corrections': False,
            'credibility_explanation': {
                'level': 'Unknown',
                'explanation': 'Limited information available',
                'advice': 'Verify claims through additional sources'
            }
        }
        
        # Try multiple search strategies
        
        # 1. Check outlet's author page first (most reliable)
        if domain:
            try:
                outlet_result = self._check_outlet_author_page(clean_name, domain)
                if outlet_result:
                    # Safely merge results
                    self._safe_merge_results(result, outlet_result)
                    result['found'] = True
                    result['sources_checked'].append(f"{domain} author page")
            except Exception as e:
                logger.error(f"Error checking outlet author page: {e}")
        
        # 2. Google search for author + journalist
        try:
            google_result = self._google_search_author(clean_name, domain)
            if google_result:
                self._safe_merge_results(result, google_result)
                result['found'] = True
                result['sources_checked'].append("Google search")
        except Exception as e:
            logger.error(f"Error in Google search: {e}")
        
        # 3. Check journalist databases
        try:
            journalist_db_result = self._check_journalist_databases(clean_name)
            if journalist_db_result:
                self._safe_merge_results(result, journalist_db_result)
                result['sources_checked'].extend(journalist_db_result.get('sources_checked', []))
        except Exception as e:
            logger.error(f"Error checking journalist databases: {e}")
        
        # Calculate credibility score based on findings
        result['credibility_score'] = self._calculate_credibility_score(result)
        
        # Add credibility explanation
        result['credibility_explanation'] = self._generate_credibility_explanation(result)
        
        # Generate bio if not found
        if not result['bio']:
            # Safe access to nested dictionary
            current_position = result.get('professional_info', {}).get('current_position')
            outlets = result.get('professional_info', {}).get('outlets', [])
            
            if current_position:
                result['bio'] = f"{clean_name} is {current_position}"
                if outlets:
                    result['bio'] += f" at {outlets[0]}"
                result['bio'] += "."
            elif outlets:
                result['bio'] = f"{clean_name} is a journalist who has written for {', '.join(outlets[:3])}."
            elif result['found']:
                result['bio'] = f"{clean_name} is a journalist with verified online presence."
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
    
    def _google_search_author(self, author_name, domain=None):
        """Simple but effective Google search for author information"""
        logger.info(f"Starting Google search for author: {author_name}")
        
        result = {
            'found': False,
            'professional_info': {
                'outlets': [],
                'current_position': None,
                'expertise_areas': []
            },
            'online_presence': {},
            'bio': None,
            'sources_checked': ['Google search']
        }
        
        # Basic search query - just search for the author as a journalist
        query = f'"{author_name}" journalist OR reporter OR writer'
        if domain:
            query += f' {domain}'
        
        try:
            # Simple Google search using requests
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            # Use Google search URL
            search_url = f"https://www.google.com/search?q={quote(query)}"
            
            response = self.session.get(search_url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Get all text from the page
                page_text = soup.get_text()
                
                # Check if author name appears with journalist/reporter/writer
                if author_name.lower() in page_text.lower():
                    result['found'] = True
                    
                    # Extract snippets that mention the author
                    snippets = []
                    
                    # Find all search result snippets
                    for elem in soup.find_all(['span', 'div']):
                        text = elem.get_text(strip=True)
                        if author_name in text and len(text) > 50 and len(text) < 500:
                            snippets.append(text)
                    
                    # Analyze snippets for information
                    for snippet in snippets[:10]:  # Limit to first 10 snippets
                        snippet_lower = snippet.lower()
                        
                        # Extract position/title
                        if 'is a' in snippet or 'is an' in snippet:
                            # Try to extract what comes after "is a/an"
                            pattern = rf"{author_name}\s+is\s+(?:a|an|the)?\s*([^,\.]+?)(?:\s+at\s+|$)"
                            match = re.search(pattern, snippet, re.IGNORECASE)
                            if match and not result['professional_info']['current_position']:
                                position = match.group(1).strip()
                                if len(position) < 100:  # Reasonable length
                                    result['professional_info']['current_position'] = position
                        
                        # Extract outlets mentioned
                        # Look for "at [Outlet]" or "for [Outlet]"
                        outlet_pattern = r'(?:at|for|with|from)\s+([A-Z][A-Za-z\s&]+?)(?:\.|,|$)'
                        outlet_matches = re.findall(outlet_pattern, snippet)
                        for outlet in outlet_matches:
                            outlet = outlet.strip()
                            if len(outlet) > 2 and len(outlet) < 50:
                                if outlet not in result['professional_info']['outlets']:
                                    result['professional_info']['outlets'].append(outlet)
                        
                        # Extract expertise
                        expertise_keywords = ['covers', 'reports on', 'writes about', 'specializes in']
                        for keyword in expertise_keywords:
                            if keyword in snippet_lower:
                                # Extract what follows
                                pattern = rf"{keyword}\s+([^,\.]+)"
                                match = re.search(pattern, snippet_lower)
                                if match:
                                    expertise = match.group(1).strip()
                                    if len(expertise) < 50 and expertise not in result['professional_info']['expertise_areas']:
                                        result['professional_info']['expertise_areas'].append(expertise)
                        
                        # Look for LinkedIn
                        if 'linkedin' in snippet_lower:
                            result['online_presence']['linkedin'] = 'Found on LinkedIn'
                        
                        # Look for Twitter
                        if 'twitter' in snippet_lower or '@' in snippet:
                            # Try to extract Twitter handle
                            twitter_match = re.search(r'@(\w+)', snippet)
                            if twitter_match:
                                result['online_presence']['twitter'] = twitter_match.group(1)
                    
                    # Use best snippet as bio if we found good information
                    if snippets:
                        # Prefer snippets that have "is a" statements
                        bio_candidates = [s for s in snippets if 'is a' in s or 'is an' in s]
                        if bio_candidates:
                            result['bio'] = bio_candidates[0]
                        else:
                            result['bio'] = snippets[0]
                    
                    # If we found the author is associated with the domain, boost credibility
                    if domain and domain.lower() in page_text.lower():
                        result['verification_status'] = {
                            'outlet_staff': True,
                            'verified': True
                        }
                    
                    # Log what we found
                    logger.info(f"Found info for {author_name}: position={result['professional_info']['current_position']}, outlets={len(result['professional_info']['outlets'])}")
        
        except Exception as e:
            logger.error(f"Error in Google search: {e}")
            return None
        
        # Only return if we found something meaningful
        if result['found'] and (result['bio'] or result['professional_info']['current_position'] or result['professional_info']['outlets']):
            return result
        
        return None
    
    def _check_journalist_databases(self, author_name):
        """Check common journalist sites for author information"""
        logger.info(f"Checking journalist databases for {author_name}")
        
        result = {
            'found': False,
            'sources_checked': []
        }
        
        # Try Muck Rack directly
        try:
            # Format author name for URL (lowercase, replace spaces with hyphens)
            author_slug = author_name.lower().replace(' ', '-')
            muckrack_url = f"https://muckrack.com/{author_slug}"
            
            response = self.session.get(muckrack_url, timeout=5)
            if response.status_code == 200:
                # Check if it's actually the author's page
                if author_name.lower() in response.text.lower():
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    result['found'] = True
                    result['online_presence'] = {'muckrack': muckrack_url}
                    result['verification_status'] = {
                        'journalist_verified': True,
                        'verified': True
                    }
                    
                    # Try to extract bio
                    bio_elem = soup.find('div', class_='bio')
                    if bio_elem:
                        result['bio'] = bio_elem.get_text(strip=True)
                    
                    # Try to extract current outlet
                    outlet_elem = soup.find('div', class_='outlet')
                    if outlet_elem:
                        result['professional_info'] = {
                            'outlets': [outlet_elem.get_text(strip=True)]
                        }
                    
                    result['sources_checked'].append('Muck Rack')
                    logger.info(f"Found {author_name} on Muck Rack")
                    return result
        except Exception as e:
            logger.debug(f"Muck Rack check failed: {e}")
        
        # Try searching via Google for author profiles on journalism sites
        try:
            # Search for the author on known journalism sites
            sites_to_check = [
                'site:muckrack.com',
                'site:contently.com', 
                'site:journoportfolio.com',
                'site:linkedin.com/in'
            ]
            
            for site in sites_to_check:
                query = f'{site} "{author_name}"'
                search_url = f"https://www.google.com/search?q={quote(query)}"
                
                try:
                    response = self.session.get(search_url, timeout=5)
                    if response.status_code == 200 and author_name.lower() in response.text.lower():
                        # Found a mention
                        result['found'] = True
                        site_name = site.replace('site:', '').replace('.com', '')
                        result['sources_checked'].append(site_name)
                        
                        # Extract any LinkedIn URL
                        if 'linkedin.com' in response.text:
                            linkedin_match = re.search(r'(https?://[a-z]{2,3}\.linkedin\.com/in/[^"\s&]+)', response.text)
                            if linkedin_match:
                                result['online_presence'] = {'linkedin': linkedin_match.group(1)}
                        
                        # If we found them on any journalism site, they're likely a real journalist
                        result['verification_status'] = {
                            'journalist_verified': True
                        }
                        
                        logger.info(f"Found {author_name} on {site_name}")
                        break
                        
                except Exception as e:
                    logger.debug(f"Error checking {site}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error in journalist database search: {e}")
        
        return result if result['found'] else None
    
    def _safe_merge_results(self, target, source):
        """Safely merge source dict into target dict without overwriting None with empty values"""
        if not source:
            return
            
        for key, value in source.items():
            if key not in target:
                target[key] = value
            elif isinstance(value, dict) and isinstance(target[key], dict):
                # Recursively merge dictionaries
                self._safe_merge_results(target[key], value)
            elif value is not None and (not isinstance(value, (list, str)) or value):
                # Only update if source value is meaningful
                target[key] = value
    
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
        
        # Apply scoring with safe access
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
        
        online_presence = author_data.get('online_presence', {})
        if any(online_presence.get(key) for key in ['twitter', 'linkedin', 'personal_website', 'outlet_profile']):
            score += criteria['has_social_media']
        
        if author_data.get('verification_status', {}).get('journalist_verified'):
            score += criteria['journalist_database']
        
        return min(score, max_score)
    
    def _generate_credibility_explanation(self, author_data):
        """Generate explanation for credibility score"""
        score = author_data.get('credibility_score', 0)
        
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
        if not author_name:
            return "Unknown"
            
        # Remove common suffixes
        name = re.sub(r'\s*(,|and|&)\s*.*', '', author_name)
        
        # Remove titles
        titles = ['Dr.', 'Prof.', 'Mr.', 'Mrs.', 'Ms.', 'Sir', 'Dame']
        for title in titles:
            name = name.replace(title, '').strip()
        
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        return name if name else "Unknown"
    
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
            if cleaned and len(cleaned) > 2 and cleaned != "Unknown":
                cleaned_authors.append(cleaned)
        
        return cleaned_authors
    
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
        
        return None
    
    def _parse_author_page_universal(self, html, url, domain, author_name):
        """Universal parser that works for any news site author page"""
        try:
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
            
            # 4. Extract title/position
            if not result.get('professional_info', {}).get('current_position'):
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
                            result.setdefault('professional_info', {})['current_position'] = title
                            break
            
            # 5. Extract social media links
            social_links = soup.find_all('a', href=True)
            for link in social_links:
                href = link['href'].lower()
                
                # Twitter/X
                if ('twitter.com/' in href or 'x.com/' in href) and '/status/' not in href:
                    match = re.search(r'(?:twitter\.com|x\.com)/(@?\w+)', href)
                    if match:
                        handle = match.group(1).replace('@', '')
                        if handle not in ['share', 'intent', 'home', 'search']:
                            result.setdefault('online_presence', {})['twitter'] = handle
                
                # LinkedIn
                elif 'linkedin.com/in/' in href:
                    result.setdefault('online_presence', {})['linkedin'] = link['href']
                
                # Email
                elif href.startswith('mailto:'):
                    email = href.replace('mailto:', '').split('?')[0]
                    if '@' in email:
                        result.setdefault('online_presence', {})['email'] = email
            
            # 6. Default bio if none found but we're on an author page
            if not result.get('bio') and result.get('found_author_page'):
                position = result.get('professional_info', {}).get('current_position', 'journalist')
                outlets = result.get('professional_info', {}).get('outlets', [])
                outlet = outlets[0] if outlets else domain
                result['bio'] = f"{author_name} is a {position} at {outlet}."
            
            return result
        except Exception as e:
            logger.error(f"Error parsing author page: {e}")
            return None
    
    def _extract_from_json_ld(self, data, author_name, result):
        """Extract author info from JSON-LD structured data"""
        try:
            if isinstance(data, dict):
                # Direct Person object
                if data.get('@type') == 'Person' and author_name.lower() in data.get('name', '').lower():
                    if data.get('description'):
                        result['bio'] = data['description']
                    if data.get('jobTitle'):
                        result.setdefault('professional_info', {})['current_position'] = data['jobTitle']
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
                            result.setdefault('professional_info', {})['current_position'] = author['jobTitle']
                        return True
            
            elif isinstance(data, list):
                # Check each item in the list
                for item in data:
                    if self._extract_from_json_ld(item, author_name, result):
                        return True
        except Exception as e:
            logger.debug(f"Error extracting from JSON-LD: {e}")
        
        return False
    
    def _extract_from_meta_tags(self, soup, author_name, result):
        """Extract author info from meta tags"""
        try:
            # Common meta tag patterns
            meta_mappings = {
                'bio': ['description', 'author.description', 'twitter:description'],
                'image': ['author.image', 'twitter:image', 'og:image'],
                'title': ['author.title', 'author.jobTitle']
            }
            
            for field, properties in meta_mappings.items():
                for prop in properties:
                    meta = soup.find('meta', {'property': prop}) or soup.find('meta', {'name': prop})
                    if meta and meta.get('content'):
                        content = meta['content']
                        if field == 'bio' and (author_name.lower() in content.lower() or len(content) > 100):
                            result['bio'] = content
                        elif field == 'image':
                            result['image_url'] = content
                        elif field == 'title':
                            result.setdefault('professional_info', {})['current_position'] = content
        except Exception as e:
            logger.debug(f"Error extracting from meta tags: {e}")
