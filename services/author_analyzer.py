"""
FILE: services/author_analyzer.py
PURPOSE: Enhanced author analyzer that collects MAXIMUM information
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
    """Enhanced author analyzer that searches for comprehensive journalist information"""
    
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
        """Analyze a single author with comprehensive web search"""
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
        
        # Initialize comprehensive result structure
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
                'email': None,
                'muckrack': None,
                'facebook': None,
                'instagram': None,
                'youtube': None,
                'substack': None,
                'medium': None
            },
            'verification_status': {
                'verified': False,
                'journalist_verified': False,
                'outlet_staff': False
            },
            'education': None,
            'awards': [],
            'previous_positions': [],
            'recent_articles': [],
            'issues_corrections': False,
            'sources_checked': [],
            'credibility_explanation': {
                'level': 'Unknown',
                'explanation': 'Limited information available',
                'advice': 'Verify claims through additional sources'
            }
        }
        
        # Try multiple search strategies in order of reliability
        
        # 1. Check outlet's author page first (most reliable)
        if domain:
            try:
                outlet_result = self._check_outlet_author_page(clean_name, domain)
                if outlet_result:
                    self._safe_merge_results(result, outlet_result)
                    result['found'] = True
                    result['sources_checked'].append(f"{domain} author page")
            except Exception as e:
                logger.error(f"Error checking outlet author page: {e}")
        
        # 2. Enhanced Google search for comprehensive information
        try:
            google_result = self._enhanced_google_search(clean_name, domain)
            if google_result:
                self._safe_merge_results(result, google_result)
                result['found'] = True
                if "Google search" not in result['sources_checked']:
                    result['sources_checked'].append("Google search")
        except Exception as e:
            logger.error(f"Error in Google search: {e}")
        
        # 3. Check journalist databases (Muck Rack, LinkedIn, etc.)
        try:
            journalist_db_result = self._check_journalist_databases(clean_name)
            if journalist_db_result:
                self._safe_merge_results(result, journalist_db_result)
                result['sources_checked'].extend(journalist_db_result.get('sources_checked', []))
        except Exception as e:
            logger.error(f"Error checking journalist databases: {e}")
        
        # 4. Search for recent articles by the author
        try:
            recent_articles = self._search_recent_articles(clean_name, domain)
            if recent_articles:
                result['recent_articles'] = recent_articles
                result['articles_count'] = len(recent_articles)
        except Exception as e:
            logger.error(f"Error searching recent articles: {e}")
        
        # 5. Extract education and awards from various sources
        try:
            education_awards = self._extract_education_awards(clean_name)
            if education_awards:
                self._safe_merge_results(result, education_awards)
        except Exception as e:
            logger.error(f"Error extracting education/awards: {e}")
        
        # Calculate credibility score based on all findings
        result['credibility_score'] = self._calculate_credibility_score(result)
        
        # Generate comprehensive credibility explanation
        result['credibility_explanation'] = self._generate_credibility_explanation(result)
        
        # Generate comprehensive bio if not found
        if not result['bio'] or result['bio'] == 'Limited information available':
            result['bio'] = self._generate_comprehensive_bio(result)
        
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
    
    def _enhanced_google_search(self, author_name, domain=None):
        """Enhanced Google search that extracts maximum information"""
        logger.info(f"Starting enhanced Google search for author: {author_name}")
        
        result = {
            'found': False,
            'professional_info': {
                'outlets': [],
                'current_position': None,
                'expertise_areas': []
            },
            'online_presence': {},
            'bio': None,
            'education': None,
            'awards': [],
            'previous_positions': [],
            'sources_checked': ['Google search']
        }
        
        # Multiple search queries for comprehensive results
        search_queries = [
            f'"{author_name}" journalist reporter writer bio',
            f'"{author_name}" journalism award education',
            f'"{author_name}" linkedin journalist',
            f'"{author_name}" twitter journalist reporter'
        ]
        
        if domain:
            search_queries.insert(0, f'"{author_name}" site:{domain}')
        
        all_snippets = []
        
        for query in search_queries:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
                
                search_url = f"https://www.google.com/search?q={quote(query)}"
                response = self.session.get(search_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract all text snippets
                    for elem in soup.find_all(['span', 'div', 'em']):
                        text = elem.get_text(strip=True)
                        if author_name in text and len(text) > 50 and len(text) < 500:
                            all_snippets.append(text)
                    
                    # Look for specific Google result elements
                    for result_div in soup.find_all('div', class_='g'):
                        snippet = result_div.get_text(separator=' ', strip=True)
                        if author_name in snippet:
                            all_snippets.append(snippet)
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error in search query '{query}': {e}")
                continue
        
        # Analyze all collected snippets
        if all_snippets:
            result['found'] = True
            
            # Extract comprehensive information from snippets
            for snippet in all_snippets:
                snippet_lower = snippet.lower()
                
                # Extract current position
                position_patterns = [
                    rf"{author_name}\s+is\s+(?:a|an|the)?\s*([^,\.]+?)(?:\s+at\s+|$)",
                    rf"{author_name},\s*([^,]+?),",
                    rf"by\s+{author_name},\s*([^,\.]+)"
                ]
                
                for pattern in position_patterns:
                    match = re.search(pattern, snippet, re.IGNORECASE)
                    if match and not result['professional_info']['current_position']:
                        position = match.group(1).strip()
                        if self._is_valid_position(position):
                            result['professional_info']['current_position'] = position
                
                # Extract outlets
                outlet_pattern = r'(?:at|for|with|from)\s+([A-Z][A-Za-z\s&]+?)(?:\.|,|$)'
                outlet_matches = re.findall(outlet_pattern, snippet)
                for outlet in outlet_matches:
                    outlet = outlet.strip()
                    if self._is_valid_outlet(outlet) and outlet not in result['professional_info']['outlets']:
                        result['professional_info']['outlets'].append(outlet)
                
                # Extract education
                if 'graduated' in snippet_lower or 'degree' in snippet_lower or 'university' in snippet_lower:
                    edu_pattern = r'(?:graduated from|degree from|studied at|attended)\s+([^,\.]+)'
                    edu_match = re.search(edu_pattern, snippet, re.IGNORECASE)
                    if edu_match and not result['education']:
                        result['education'] = edu_match.group(1).strip()
                
                # Extract awards
                award_keywords = ['award', 'prize', 'honor', 'recognition', 'winner', 'recipient']
                if any(keyword in snippet_lower for keyword in award_keywords):
                    award_pattern = r'(?:won|received|awarded|recipient of)\s+(?:the\s+)?([^,\.]+?(?:award|prize|honor)[^,\.]*)'
                    award_matches = re.findall(award_pattern, snippet, re.IGNORECASE)
                    for award in award_matches:
                        award = award.strip()
                        if award not in result['awards'] and len(award) < 100:
                            result['awards'].append(award)
                
                # Extract expertise areas
                expertise_keywords = ['covers', 'reports on', 'writes about', 'specializes in', 'focuses on', 'beat']
                for keyword in expertise_keywords:
                    if keyword in snippet_lower:
                        pattern = rf"{keyword}\s+([^,\.]+)"
                        match = re.search(pattern, snippet_lower)
                        if match:
                            expertise = match.group(1).strip()
                            if len(expertise) < 50 and expertise not in result['professional_info']['expertise_areas']:
                                result['professional_info']['expertise_areas'].append(expertise)
                
                # Extract social media presence
                if 'linkedin' in snippet_lower:
                    linkedin_match = re.search(r'linkedin\.com/in/([^/\s]+)', snippet_lower)
                    if linkedin_match:
                        result['online_presence']['linkedin'] = f"https://linkedin.com/in/{linkedin_match.group(1)}"
                
                if 'twitter' in snippet_lower or '@' in snippet:
                    twitter_match = re.search(r'@(\w+)', snippet)
                    if twitter_match:
                        result['online_presence']['twitter'] = twitter_match.group(1)
                
                # Extract previous positions
                if 'previously' in snippet_lower or 'former' in snippet_lower:
                    prev_pattern = r'(?:previously|former|formerly)\s+(?:was\s+)?(?:a|an|the)?\s*([^,\.]+?)(?:\s+at\s+([^,\.]+))?'
                    prev_matches = re.findall(prev_pattern, snippet, re.IGNORECASE)
                    for match in prev_matches:
                        position = match[0].strip()
                        outlet = match[1].strip() if len(match) > 1 else ''
                        if self._is_valid_position(position):
                            prev_pos = {'title': position}
                            if outlet and self._is_valid_outlet(outlet):
                                prev_pos['outlet'] = outlet
                            if prev_pos not in result['previous_positions']:
                                result['previous_positions'].append(prev_pos)
            
            # Select best bio from snippets
            bio_candidates = [s for s in all_snippets if 'is a' in s or 'is an' in s]
            if bio_candidates:
                # Choose the longest informative snippet
                result['bio'] = max(bio_candidates, key=lambda x: len(x) if author_name in x else 0)
            elif all_snippets:
                result['bio'] = all_snippets[0]
        
        return result if result['found'] else None
    
    def _search_recent_articles(self, author_name, domain=None):
        """Search for recent articles by the author"""
        articles = []
        
        try:
            # Search query for recent articles
            query = f'"{author_name}" article OR story OR report -linkedin -twitter'
            if domain:
                query = f'site:{domain} {query}'
            
            search_url = f"https://www.google.com/search?q={quote(query)}&tbs=qdr:y"  # Last year
            
            response = self.session.get(search_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract article titles and URLs
                for result in soup.find_all('h3')[:10]:  # First 10 results
                    parent = result.find_parent('a')
                    if parent and parent.get('href'):
                        title = result.get_text(strip=True)
                        # Clean up title
                        if ' - ' in title:
                            title = title.split(' - ')[0]
                        if ' | ' in title:
                            title = title.split(' | ')[0]
                        
                        articles.append({
                            'title': title,
                            'url': parent['href'] if parent['href'].startswith('http') else None
                        })
        
        except Exception as e:
            logger.error(f"Error searching recent articles: {e}")
        
        return articles[:5]  # Return top 5 articles
    
    def _extract_education_awards(self, author_name):
        """Extract education and awards information"""
        result = {}
        
        try:
            # Search specifically for education and awards
            query = f'"{author_name}" journalist "graduated from" OR "degree" OR "award" OR "winner"'
            search_url = f"https://www.google.com/search?q={quote(query)}"
            
            response = self.session.get(search_url, timeout=10)
            if response.status_code == 200:
                text = response.text
                
                # Education patterns
                edu_patterns = [
                    r'graduated from ([^,\.]+)',
                    r'holds a ([^,\.]+) from ([^,\.]+)',
                    r'earned (?:a|an|his|her) ([^,\.]+) at ([^,\.]+)',
                    r'([A-Z][^,\.]+University[^,\.]*)',
                    r'([A-Z][^,\.]+College[^,\.]*)'
                ]
                
                for pattern in edu_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches and not result.get('education'):
                        if isinstance(matches[0], tuple):
                            result['education'] = ' '.join(matches[0])
                        else:
                            result['education'] = matches[0]
                        break
                
                # Award patterns
                award_patterns = [
                    r'(?:won|received|awarded) (?:the )?([^,\.]+?(?:Award|Prize|Honor)[^,\.]*)',
                    r'([^,\.]+?(?:Award|Prize|Honor)[^,\.]*) (?:winner|recipient)',
                ]
                
                awards = []
                for pattern in award_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    for match in matches:
                        award = match.strip()
                        if len(award) < 100 and award not in awards:
                            awards.append(award)
                
                if awards:
                    result['awards'] = awards[:5]  # Limit to 5 awards
        
        except Exception as e:
            logger.error(f"Error extracting education/awards: {e}")
        
        return result
    
    def _generate_comprehensive_bio(self, author_data):
        """Generate a comprehensive bio from collected data"""
        bio_parts = []
        
        name = author_data['name']
        prof_info = author_data.get('professional_info', {})
        
        # Start with name and current position
        if prof_info.get('current_position'):
            if prof_info.get('outlets'):
                bio_parts.append(f"{name} is {prof_info['current_position']} at {prof_info['outlets'][0]}")
            else:
                bio_parts.append(f"{name} is {prof_info['current_position']}")
        elif prof_info.get('outlets'):
            bio_parts.append(f"{name} is a journalist who writes for {', '.join(prof_info['outlets'][:3])}")
        else:
            bio_parts.append(f"{name} is a journalist")
        
        # Add expertise
        if prof_info.get('expertise_areas'):
            areas = prof_info['expertise_areas'][:3]
            bio_parts.append(f"specializing in {', '.join(areas)}")
        
        # Add education
        if author_data.get('education'):
            bio_parts.append(f"They graduated from {author_data['education']}")
        
        # Add experience
        if prof_info.get('years_experience'):
            bio_parts.append(f"with {prof_info['years_experience']} years of experience")
        
        # Add awards
        if author_data.get('awards'):
            bio_parts.append(f"They have received {len(author_data['awards'])} journalism awards")
        
        # Combine parts into natural sentences
        if len(bio_parts) > 1:
            bio = bio_parts[0]
            if len(bio_parts) > 2:
                bio += ', ' + ', '.join(bio_parts[1:-1]) + ', and ' + bio_parts[-1] + '.'
            else:
                bio += ' ' + bio_parts[1] + '.'
        else:
            bio = bio_parts[0] + '.'
        
        return bio
    
    def _is_valid_position(self, position):
        """Check if a position title is valid"""
        if not position or len(position) < 3 or len(position) > 100:
            return False
        
        # Filter out non-position phrases
        invalid_phrases = ['is', 'was', 'has', 'the', 'article', 'story', 'report']
        position_lower = position.lower()
        
        if any(phrase == position_lower for phrase in invalid_phrases):
            return False
        
        # Must contain at least one position-related word
        position_words = ['journalist', 'reporter', 'writer', 'editor', 'correspondent', 
                         'columnist', 'contributor', 'author', 'producer', 'anchor']
        
        return any(word in position_lower for word in position_words) or len(position.split()) >= 2
    
    def _is_valid_outlet(self, outlet):
        """Check if an outlet name is valid"""
        if not outlet or len(outlet) < 2 or len(outlet) > 50:
            return False
        
        # Filter out common non-outlet phrases
        invalid_outlets = ['the', 'and', 'or', 'is', 'was', 'has', 'with', 'from']
        
        return outlet.lower() not in invalid_outlets and outlet[0].isupper()
    
    def _check_outlet_author_page(self, author_name, domain):
        """Enhanced outlet author page checker"""
        # Implementation remains the same as in previous version
        # but with additional patterns and better parsing
        # [Previous implementation code here...]
        return self._check_outlet_author_page_original(author_name, domain)
    
    def _check_outlet_author_page_original(self, author_name, domain):
        """Original outlet page checker - enhanced version"""
        clean_domain = domain.replace('www.', '')
        author_slug = author_name.lower().replace(' ', '-')
        author_underscore = author_name.lower().replace(' ', '_')
        author_plus = author_name.lower().replace(' ', '+')
        
        # Enhanced URL patterns
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
            f"https://{domain}/columnist/{author_slug}/",
            f"https://{domain}/editor/{author_slug}/",
            f"https://www.{clean_domain}/{author_slug}/",
            f"https://www.{clean_domain}/author/{author_slug}/",
            # Try underscore versions
            f"https://{domain}/author/{author_underscore}/",
            f"https://{domain}/authors/{author_underscore}/",
            # Try plus sign versions
            f"https://{domain}/author/{author_plus}/",
            # Try without hyphens
            f"https://{domain}/author/{author_name.lower().replace(' ', '')}/",
        ]
        
        for url in url_patterns:
            try:
                response = self.session.get(url, timeout=5)
                if response.status_code == 200:
                    result = self._parse_author_page_enhanced(response.text, url, domain, author_name)
                    if result and result.get('found_author_page'):
                        return result
            except Exception as e:
                logger.debug(f"Failed to check {url}: {e}")
                continue
        
        return None
    
    def _parse_author_page_enhanced(self, html, url, domain, author_name):
        """Enhanced parser for author pages with maximum data extraction"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Check if this is actually an author page
            page_text = soup.get_text().lower()
            author_name_lower = author_name.lower()
            
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
            
            # 1. Extract from JSON-LD structured data first
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    self._extract_from_json_ld_enhanced(data, author_name, result)
                except:
                    continue
            
            # 2. Extract from meta tags
            self._extract_from_meta_tags_enhanced(soup, author_name, result)
            
            # 3. Extract author image
            image_selectors = [
                f'img[alt*="{author_name}"]',
                '.author-image img', '.author-photo img', '.author-avatar img',
                '.bio-image img', '.profile-image img', '.headshot img',
                '[class*="author"] img', '[id*="author"] img'
            ]
            
            for selector in image_selectors:
                img = soup.select_one(selector)
                if img and img.get('src'):
                    result['image_url'] = self._make_absolute_url(img['src'], domain)
                    break
            
            # 4. Enhanced bio extraction
            bio_candidates = []
            
            # Look for bio in common containers
            bio_selectors = [
                '[class*="bio"]', '[class*="Bio"]', '[class*="author-desc"]',
                '[class*="author-info"]', '[class*="author-about"]',
                '[class*="description"]', '[id*="bio"]', '[id*="Bio"]',
                '.about', '.profile', '.author-details'
            ]
            
            for selector in bio_selectors:
                elements = soup.select(selector)
                for elem in elements:
                    text = elem.get_text(strip=True)
                    if len(text) > 50 and author_name.split()[-1].lower() in text.lower():
                        bio_candidates.append(text)
            
            # Also check paragraphs that mention the author
            for p in soup.find_all('p'):
                text = p.get_text(strip=True)
                if (len(text) > 50 and 
                    any(name_part.lower() in text.lower() for name_part in author_name.split()) and
                    any(keyword in text.lower() for keyword in 
                        ['is a', 'journalist', 'reporter', 'correspondent', 'writer', 
                         'covers', 'reports', 'joined', 'experience', 'previously',
                         'graduated', 'award', 'specializ'])):
                    bio_candidates.append(text)
            
            # Select the most comprehensive bio
            if bio_candidates:
                result['bio'] = max(bio_candidates, key=lambda x: len(x))
            
            # 5. Extract title/position with more patterns
            title_patterns = [
                rf"{author_name}\s*,\s*([^,\.\n]+)",
                rf"{author_name}\s+is\s+(?:a|an|the)?\s*([^\.\n]+?)(?:\s+at\s+|$)",
                rf"(?:by|By)\s+{author_name}\s*,\s*([^,\.\n]+)",
                rf"<h\d[^>]*>[^<]*{author_name}[^<]*</h\d>\s*<[^>]+>([^<]+)",
            ]
            
            page_text_full = str(soup)
            for pattern in title_patterns:
                match = re.search(pattern, page_text_full, re.IGNORECASE | re.DOTALL)
                if match:
                    title = match.group(1).strip()
                    title = re.sub(r'<[^>]+>', '', title)  # Remove HTML tags
                    if len(title) < 100 and self._is_valid_position(title):
                        result.setdefault('professional_info', {})['current_position'] = title
                        break
            
            # 6. Extract social media links with more platforms
            social_patterns = {
                'twitter': [r'twitter\.com/(@?\w+)', r'x\.com/(@?\w+)'],
                'linkedin': [r'linkedin\.com/in/([\w-]+)'],
                'facebook': [r'facebook\.com/([\w\.]+)'],
                'instagram': [r'instagram\.com/([\w\.]+)'],
                'youtube': [r'youtube\.com/(@?[\w-]+)'],
                'substack': [r'(\w+)\.substack\.com'],
                'medium': [r'medium\.com/@([\w-]+)']
            }
            
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href'].lower()
                
                for platform, patterns in social_patterns.items():
                    for pattern in patterns:
                        match = re.search(pattern, href)
                        if match:
                            username = match.group(1).replace('@', '')
                            if username not in ['share', 'intent', 'home', 'search', 'about']:
                                result.setdefault('online_presence', {})[platform] = username
                                break
                
                # Email
                if href.startswith('mailto:'):
                    email = href.replace('mailto:', '').split('?')[0]
                    if '@' in email:
                        result.setdefault('online_presence', {})['email'] = email
            
            # 7. Extract education information
            education_patterns = [
                r'(?:graduated from|alumnus of|attended)\s+([^,\.\n]+(?:University|College)[^,\.\n]*)',
                r'(?:holds?|earned?|received?)\s+(?:a|an|his|her)\s+([^,\.\n]+)\s+(?:from|at)\s+([^,\.\n]+)',
                r'(?:B\.A\.|B\.S\.|M\.A\.|M\.S\.|Ph\.D\.|Bachelor|Master|Doctor)[^,\.\n]*\s+(?:from|at)\s+([^,\.\n]+)'
            ]
            
            for pattern in education_patterns:
                match = re.search(pattern, page_text_full, re.IGNORECASE)
                if match:
                    if len(match.groups()) > 1:
                        result['education'] = f"{match.group(1)} from {match.group(2)}"
                    else:
                        result['education'] = match.group(1)
                    break
            
            # 8. Extract awards
            award_patterns = [
                r'(?:won|received|awarded|recipient of)\s+(?:the\s+)?([^,\.\n]+?(?:Award|Prize|Honor)[^,\.\n]*)',
                r'([^,\.\n]+?(?:Award|Prize|Honor)[^,\.\n]*)\s+(?:winner|recipient)',
                r'(?:honors?|awards?|recognition):[^:]+?([^,\.\n]+)'
            ]
            
            awards = []
            for pattern in award_patterns:
                matches = re.findall(pattern, page_text_full, re.IGNORECASE)
                for match in matches:
                    award = match.strip()
                    if len(award) < 100 and award not in awards:
                        awards.append(award)
            
            if awards:
                result['awards'] = awards[:10]  # Limit to 10 awards
            
            # 9. Extract previous positions
            prev_patterns = [
                r'(?:previously|formerly|former|prior to)\s+(?:was\s+)?(?:a|an|the)?\s*([^,\.\n]+?)(?:\s+at\s+([^,\.\n]+))?',
                r'(?:worked as|served as)\s+(?:a|an|the)?\s*([^,\.\n]+?)(?:\s+at\s+([^,\.\n]+))?',
                r'(?:Before|Prior to)[^,\.\n]+,\s*(?:he|she|they)\s+(?:was|were)\s+(?:a|an|the)?\s*([^,\.\n]+)'
            ]
            
            previous_positions = []
            for pattern in prev_patterns:
                matches = re.findall(pattern, page_text_full, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        position = match[0].strip()
                        outlet = match[1].strip() if len(match) > 1 and match[1] else None
                    else:
                        position = match.strip()
                        outlet = None
                    
                    if self._is_valid_position(position):
                        pos_entry = {'title': position}
                        if outlet and self._is_valid_outlet(outlet):
                            pos_entry['outlet'] = outlet
                        if pos_entry not in previous_positions:
                            previous_positions.append(pos_entry)
            
            if previous_positions:
                result['previous_positions'] = previous_positions[:5]  # Limit to 5
            
            # 10. Extract recent articles from the author page
            article_selectors = [
                '.author-articles article', '.articles-list article',
                '[class*="article-item"]', '[class*="post-item"]',
                '.author-posts .post', '.stories article'
            ]
            
            recent_articles = []
            for selector in article_selectors:
                articles = soup.select(selector)[:10]  # Limit to 10
                for article in articles:
                    title_elem = article.find(['h2', 'h3', 'h4', 'a'])
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        link = article.find('a', href=True)
                        
                        article_data = {'title': title}
                        if link:
                            article_data['url'] = self._make_absolute_url(link['href'], domain)
                        
                        # Try to find date
                        date_elem = article.find(['time', '.date', '.publish-date'])
                        if date_elem:
                            date_text = date_elem.get('datetime') or date_elem.get_text(strip=True)
                            article_data['date'] = date_text
                        
                        recent_articles.append(article_data)
            
            if recent_articles:
                result['recent_articles'] = recent_articles[:5]
            
            # 11. Extract years of experience
            experience_patterns = [
                r'(\d+)\+?\s*years?\s+(?:of\s+)?(?:experience|journalism|reporting)',
                r'(?:experience|journalism|reporting)\s+(?:of\s+)?(\d+)\+?\s*years?',
                r'(?:for|over|nearly)\s+(\d+)\+?\s*years?'
            ]
            
            for pattern in experience_patterns:
                match = re.search(pattern, page_text_full, re.IGNORECASE)
                if match:
                    years = int(match.group(1))
                    if 1 <= years <= 50:  # Reasonable range
                        result.setdefault('professional_info', {})['years_experience'] = years
                        break
            
            # 12. Extract expertise areas
            expertise_patterns = [
                r'(?:covers?|reports? on|writes? about|specializes? in|focuses? on)\s+([^,\.\n]+)',
                r'(?:beat|expertise|specialty):\s*([^,\.\n]+)',
                r'(?:topics?|areas?):\s*([^,\.\n]+)'
            ]
            
            expertise_areas = []
            for pattern in expertise_patterns:
                matches = re.findall(pattern, page_text_full, re.IGNORECASE)
                for match in matches:
                    areas = match.strip()
                    # Split by common delimiters
                    for delimiter in [',', ';', ' and ', ' & ']:
                        if delimiter in areas:
                            for area in areas.split(delimiter):
                                area = area.strip()
                                if len(area) > 2 and len(area) < 50 and area not in expertise_areas:
                                    expertise_areas.append(area)
                            break
                    else:
                        if len(areas) > 2 and len(areas) < 50 and areas not in expertise_areas:
                            expertise_areas.append(areas)
            
            if expertise_areas:
                result.setdefault('professional_info', {})['expertise_areas'] = expertise_areas[:5]
            
            # 13. Check for issues/corrections
            if any(phrase in page_text.lower() for phrase in ['correction', 'retraction', 'corrected', 'updated']):
                result['issues_corrections'] = True
            
            # 14. Extract article count
            count_patterns = [
                r'(\d+)\+?\s*(?:articles?|stories?|posts?)',
                r'(?:written|published|authored)\s+(?:over\s+)?(\d+)\+?\s*(?:articles?|stories?)',
                r'(?:articles?|stories?|posts?):\s*(\d+)'
            ]
            
            for pattern in count_patterns:
                match = re.search(pattern, page_text_full, re.IGNORECASE)
                if match:
                    count = int(match.group(1))
                    if count > 0 and count < 10000:  # Reasonable range
                        result['articles_count'] = count
                        break
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing author page: {e}")
            return None
    
    def _extract_from_json_ld_enhanced(self, data, author_name, result):
        """Enhanced extraction from JSON-LD with more fields"""
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
                    if data.get('alumniOf'):
                        alumni = data['alumniOf']
                        if isinstance(alumni, dict):
                            result['education'] = alumni.get('name', '')
                        elif isinstance(alumni, str):
                            result['education'] = alumni
                    if data.get('award'):
                        awards = data['award'] if isinstance(data['award'], list) else [data['award']]
                        result['awards'] = [a.get('name') if isinstance(a, dict) else str(a) for a in awards]
                    if data.get('sameAs'):
                        # Extract social media from sameAs
                        same_as = data['sameAs'] if isinstance(data['sameAs'], list) else [data['sameAs']]
                        for url in same_as:
                            self._extract_social_from_url(url, result)
                    return True
                
                # Article with author
                if data.get('@type') in ['Article', 'NewsArticle'] and data.get('author'):
                    author = data['author']
                    if isinstance(author, dict) and author_name.lower() in author.get('name', '').lower():
                        return self._extract_from_json_ld_enhanced(author, author_name, result)
            
            elif isinstance(data, list):
                for item in data:
                    if self._extract_from_json_ld_enhanced(item, author_name, result):
                        return True
        except Exception as e:
            logger.debug(f"Error extracting from JSON-LD: {e}")
        
        return False
    
    def _extract_from_meta_tags_enhanced(self, soup, author_name, result):
        """Enhanced extraction from meta tags"""
        try:
            # Extended meta tag mappings
            meta_mappings = {
                'bio': ['description', 'author.description', 'twitter:description', 'og:description'],
                'image': ['author.image', 'twitter:image', 'og:image', 'profile:image'],
                'title': ['author.title', 'author.jobTitle', 'profile:job_title'],
                'email': ['author.email', 'profile:email'],
                'twitter': ['twitter:creator', 'twitter:site'],
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
                        elif field == 'email':
                            result.setdefault('online_presence', {})['email'] = content
                        elif field == 'twitter':
                            handle = content.replace('@', '')
                            if handle and handle not in ['share', 'intent']:
                                result.setdefault('online_presence', {})['twitter'] = handle
        except Exception as e:
            logger.debug(f"Error extracting from meta tags: {e}")
    
    def _extract_social_from_url(self, url, result):
        """Extract social media username from URL"""
        if not url:
            return
        
        url_lower = url.lower()
        
        # Twitter/X
        if 'twitter.com/' in url_lower or 'x.com/' in url_lower:
            match = re.search(r'(?:twitter\.com|x\.com)/(@?\w+)', url_lower)
            if match:
                handle = match.group(1).replace('@', '')
                if handle not in ['share', 'intent', 'home']:
                    result.setdefault('online_presence', {})['twitter'] = handle
        
        # LinkedIn
        elif 'linkedin.com/in/' in url_lower:
            result.setdefault('online_presence', {})['linkedin'] = url
        
        # Other platforms
        elif 'facebook.com/' in url_lower:
            match = re.search(r'facebook\.com/([\w\.]+)', url_lower)
            if match:
                result.setdefault('online_presence', {})['facebook'] = match.group(1)
        
        elif 'instagram.com/' in url_lower:
            match = re.search(r'instagram\.com/([\w\.]+)', url_lower)
            if match:
                result.setdefault('online_presence', {})['instagram'] = match.group(1)
    
    def _make_absolute_url(self, url, domain):
        """Convert relative URLs to absolute"""
        if not url:
            return None
        
        if url.startswith('http'):
            return url
        
        if url.startswith('//'):
            return 'https:' + url
        
        if url.startswith('/'):
            return f'https://{domain}{url}'
        
        return f'https://{domain}/{url}'
    
    def _check_journalist_databases(self, author_name):
        """Enhanced journalist database checking"""
        # [Previous implementation remains the same]
        # Just calling the original method
        result = self._check_journalist_databases_original(author_name)
        
        # Add additional database checks here if needed
        return result
    
    def _check_journalist_databases_original(self, author_name):
        """Original journalist database implementation"""
        logger.info(f"Checking journalist databases for {author_name}")
        
        result = {
            'found': False,
            'sources_checked': []
        }
        
        # Try Muck Rack directly
        try:
            author_slug = author_name.lower().replace(' ', '-')
            muckrack_url = f"https://muckrack.com/{author_slug}"
            
            response = self.session.get(muckrack_url, timeout=5)
            if response.status_code == 200:
                if author_name.lower() in response.text.lower():
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    result['found'] = True
                    result['online_presence'] = {'muckrack': muckrack_url}
                    result['verification_status'] = {
                        'journalist_verified': True,
                        'verified': True
                    }
                    
                    bio_elem = soup.find('div', class_='bio')
                    if bio_elem:
                        result['bio'] = bio_elem.get_text(strip=True)
                    
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
        
        # Try searching via Google for author profiles
        try:
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
                        result['found'] = True
                        site_name = site.replace('site:', '').replace('.com', '')
                        result['sources_checked'].append(site_name)
                        
                        if 'linkedin.com' in response.text:
                            linkedin_match = re.search(r'(https?://[a-z]{2,3}\.linkedin\.com/in/[^"\s&]+)', response.text)
                            if linkedin_match:
                                result['online_presence'] = {'linkedin': linkedin_match.group(1)}
                        
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
        """Safely merge source dict into target dict"""
        if not source:
            return
            
        for key, value in source.items():
            if key not in target:
                target[key] = value
            elif isinstance(value, dict) and isinstance(target[key], dict):
                self._safe_merge_results(target[key], value)
            elif isinstance(value, list) and isinstance(target[key], list):
                # Merge lists without duplicates
                for item in value:
                    if item not in target[key]:
                        target[key].append(item)
            elif value is not None and (not isinstance(value, (list, str)) or value):
                # Only update if source value is meaningful
                target[key] = value
    
    def _calculate_credibility_score(self, author_data):
        """Enhanced credibility scoring with more factors"""
        score = 0
        
        # Enhanced scoring criteria
        criteria = {
            'has_bio': 10,
            'has_comprehensive_bio': 5,  # Bonus for detailed bio
            'has_image': 5,
            'has_position': 10,
            'has_outlets': 10,
            'multiple_outlets': 5,  # Bonus for multiple publications
            'outlet_verified': 15,
            'has_social_media': 5,
            'multiple_social': 5,  # Bonus for multiple platforms
            'journalist_database': 15,
            'has_education': 5,
            'has_awards': 10,
            'has_experience': 5,
            'has_recent_articles': 5,
            'no_issues': 5,  # Bonus for no corrections/retractions
        }
        
        # Apply enhanced scoring
        if author_data.get('bio'):
            score += criteria['has_bio']
            if len(author_data['bio']) > 200:  # Comprehensive bio
                score += criteria['has_comprehensive_bio']
        
        if author_data.get('image_url'):
            score += criteria['has_image']
        
        if author_data.get('professional_info', {}).get('current_position'):
            score += criteria['has_position']
        
        outlets = author_data.get('professional_info', {}).get('outlets', [])
        if outlets:
            score += criteria['has_outlets']
            if len(outlets) > 1:
                score += criteria['multiple_outlets']
        
        if author_data.get('verification_status', {}).get('outlet_staff'):
            score += criteria['outlet_verified']
        
        online_presence = author_data.get('online_presence', {})
        social_count = sum(1 for v in online_presence.values() if v)
        if social_count > 0:
            score += criteria['has_social_media']
            if social_count > 2:
                score += criteria['multiple_social']
        
        if author_data.get('verification_status', {}).get('journalist_verified'):
            score += criteria['journalist_database']
        
        if author_data.get('education'):
            score += criteria['has_education']
        
        if author_data.get('awards'):
            score += criteria['has_awards']
        
        if author_data.get('professional_info', {}).get('years_experience'):
            score += criteria['has_experience']
        
        if author_data.get('recent_articles'):
            score += criteria['has_recent_articles']
        
        if not author_data.get('issues_corrections', False):
            score += criteria['no_issues']
        
        return min(score, 100)
    
    def _generate_credibility_explanation(self, author_data):
        """Generate detailed credibility explanation"""
        score = author_data.get('credibility_score', 0)
        
        if score >= 80:
            level = 'High'
            explanation = f"Well-established journalist with verified credentials, clear professional history, and strong online presence."
            advice = "This author has excellent credibility indicators. Their work can generally be trusted."
        elif score >= 60:
            level = 'Good'
            explanation = f"Verified journalist with substantial professional information and good credentials."
            advice = "Author appears credible with solid professional background. Standard verification of claims still recommended."
        elif score >= 40:
            level = 'Moderate'
            explanation = f"Some professional information found, but limited verification or incomplete profile."
            advice = "Consider cross-referencing important claims with other sources due to limited author information."
        else:
            level = 'Limited'
            explanation = f"Minimal verifiable information about this author's professional background or credentials."
            advice = "Exercise caution and verify all claims through additional sources. Limited author credibility."
        
        # Add specific factors to explanation
        factors = []
        if author_data.get('verification_status', {}).get('outlet_staff'):
            factors.append("verified staff writer")
        if author_data.get('awards'):
            factors.append(f"{len(author_data['awards'])} journalism awards")
        if author_data.get('professional_info', {}).get('years_experience'):
            factors.append(f"{author_data['professional_info']['years_experience']} years experience")
        
        if factors:
            explanation += f" Key credibility factors include: {', '.join(factors)}."
        
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
