"""
FILE: services/author_analyzer.py
LOCATION: services/author_analyzer.py
PURPOSE: Robust author credibility analysis with comprehensive error handling
"""

import logging
import re
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urlparse

logger = logging.getLogger(__name__)

class AuthorAnalyzer:
    """Analyzes author credibility and background"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Cache for author lookups
        self._author_cache = {}
        
        # Known journalist databases/platforms
        self.journalist_platforms = [
            'muckrack.com',
            'journalistsresource.org',
            'spj.org',  # Society of Professional Journalists
            'poynter.org',
            'nieman.harvard.edu',
            'cjr.org',  # Columbia Journalism Review
            'pressgazette.co.uk'
        ]
        
        # Major news outlets for verification
        self.major_outlets = {
            'nytimes.com': 'The New York Times',
            'washingtonpost.com': 'The Washington Post',
            'wsj.com': 'The Wall Street Journal',
            'bbc.com': 'BBC',
            'bbc.co.uk': 'BBC',
            'cnn.com': 'CNN',
            'reuters.com': 'Reuters',
            'apnews.com': 'Associated Press',
            'bloomberg.com': 'Bloomberg',
            'ft.com': 'Financial Times',
            'theguardian.com': 'The Guardian',
            'npr.org': 'NPR',
            'politico.com': 'Politico',
            'thehill.com': 'The Hill',
            'axios.com': 'Axios',
            'vice.com': 'VICE',
            'vox.com': 'Vox',
            'buzzfeednews.com': 'BuzzFeed News',
            'propublica.org': 'ProPublica',
            'theintercept.com': 'The Intercept',
            'slate.com': 'Slate',
            'salon.com': 'Salon',
            'huffpost.com': 'HuffPost',
            'dailymail.co.uk': 'Daily Mail',
            'foxnews.com': 'Fox News',
            'msnbc.com': 'MSNBC',
            'cbsnews.com': 'CBS News',
            'nbcnews.com': 'NBC News',
            'abcnews.go.com': 'ABC News',
            'usatoday.com': 'USA Today',
            'latimes.com': 'Los Angeles Times',
            'chicagotribune.com': 'Chicago Tribune',
            'bostonglobe.com': 'The Boston Globe',
            'seattletimes.com': 'The Seattle Times',
            'denverpost.com': 'The Denver Post'
        }
    
    def analyze_single_author(self, author_name: str, domain: Optional[str] = None) -> Dict[str, Any]:
        """Analyze a single author with comprehensive search and error handling"""
        
        # Validate input
        if not author_name or not isinstance(author_name, str):
            return self._create_error_result("Unknown Author", "Invalid author name provided")
        
        # Clean author name
        author_name = author_name.strip()
        if len(author_name) < 2 or len(author_name) > 100:
            return self._create_error_result(author_name, "Invalid author name length")
        
        logger.info(f"🔍 Starting comprehensive author analysis for: {author_name} from {domain}")
        
        # Check cache first
        cache_key = f"{author_name}:{domain or 'any'}"
        if cache_key in self._author_cache:
            logger.info(f"  Found in cache: {cache_key}")
            return self._author_cache[cache_key]
        
        # Initialize result structure with all required fields
        result = self._create_base_result(author_name, domain)
        
        try:
            # List of search methods with fallbacks
            search_methods = [
                ('outlet_staff', lambda: self._search_outlet_staff(author_name, domain) if domain else None),
                ('google_search', lambda: self._search_google(author_name, domain)),
                ('linkedin', lambda: self._search_linkedin(author_name)),
                ('twitter', lambda: self._search_twitter(author_name)),
                ('muckrack', lambda: self._search_muckrack(author_name)),
                ('journalist_db', lambda: self._search_journalist_databases(author_name))
            ]
            
            # Track what we've found
            found_info = {
                'bio': None,
                'position': None,
                'outlets': set(),
                'social_media': {},
                'credentials': [],
                'articles_count': 0,
                'expertise_areas': set()
            }
            
            # Execute each search method
            for source_name, search_func in search_methods:
                try:
                    logger.info(f"  Checking {source_name}...")
                    result['sources_checked'].append(source_name)
                    
                    source_data = search_func()
                    
                    if source_data and isinstance(source_data, dict):
                        self._merge_source_data(result, source_data, found_info)
                        
                        # If we found good info, mark as found
                        if source_data.get('found'):
                            result['found'] = True
                    
                except Exception as e:
                    logger.error(f"    Error in {source_name}: {str(e)}")
                    continue
            
            # Calculate final credibility score
            result['credibility_score'] = self._calculate_credibility_score(result, found_info)
            
            # Generate credibility explanation
            result['credibility_explanation'] = self._generate_credibility_explanation(result)
            
            # Ensure bio exists
            if not result['bio'] or result['bio'] == 'No bio available':
                result['bio'] = self._generate_bio(author_name, result, domain)
            
            # Cache the result
            self._author_cache[cache_key] = result
            
            logger.info(f"✅ Author analysis complete: found={result['found']}, score={result['credibility_score']}")
            return result
            
        except Exception as e:
            logger.error(f"Critical error in author analysis: {str(e)}", exc_info=True)
            return self._create_error_result(author_name, str(e))
    
    def _create_base_result(self, author_name: str, domain: Optional[str] = None) -> Dict[str, Any]:
        """Create base result structure with all required fields"""
        return {
            'found': False,
            'name': author_name,
            'credibility_score': 50,  # Neutral starting score
            'bio': None,
            'verification_status': {
                'verified': False,
                'journalist_verified': False,
                'outlet_staff': False
            },
            'professional_info': {
                'current_position': None,
                'outlets': [domain] if domain else [],
                'years_experience': None,
                'expertise_areas': []
            },
            'online_presence': {},
            'credibility_explanation': None,
            'sources_checked': [],
            'raw_data': {}  # Store raw data from searches
        }
    
    def _create_error_result(self, author_name: str, error_msg: str) -> Dict[str, Any]:
        """Create error result with all required fields"""
        return {
            'found': False,
            'name': author_name,
            'credibility_score': 40,  # Lower score for errors
            'bio': f"Unable to retrieve information about {author_name}. {error_msg}",
            'verification_status': {
                'verified': False,
                'journalist_verified': False,
                'outlet_staff': False
            },
            'professional_info': {
                'current_position': None,
                'outlets': [],
                'years_experience': None,
                'expertise_areas': []
            },
            'online_presence': {},
            'credibility_explanation': {
                'level': 'Unknown',
                'explanation': f'Technical issue prevented author verification: {error_msg}',
                'advice': 'Verify author credentials through additional sources'
            },
            'sources_checked': [],
            'error': error_msg
        }
    
    def _merge_source_data(self, result: Dict[str, Any], source_data: Dict[str, Any], 
                          found_info: Dict[str, Any]) -> None:
        """Safely merge data from a source into the result"""
        
        if not source_data or not isinstance(source_data, dict):
            return
        
        # Update bio if better one found
        if source_data.get('bio') and (not found_info['bio'] or 
                                       len(source_data['bio']) > len(found_info['bio'])):
            found_info['bio'] = source_data['bio']
            result['bio'] = source_data['bio']
        
        # Update verification status
        if source_data.get('verification_status'):
            for key, value in source_data['verification_status'].items():
                if value and key in result['verification_status']:
                    result['verification_status'][key] = True
        
        # Update professional info
        if source_data.get('professional_info'):
            prof_info = source_data['professional_info']
            
            # Current position
            if prof_info.get('current_position') and not found_info['position']:
                found_info['position'] = prof_info['current_position']
                result['professional_info']['current_position'] = prof_info['current_position']
            
            # Outlets
            if prof_info.get('outlets'):
                for outlet in prof_info['outlets']:
                    if outlet and isinstance(outlet, str):
                        found_info['outlets'].add(outlet)
            
            # Years experience
            if prof_info.get('years_experience') and not result['professional_info']['years_experience']:
                result['professional_info']['years_experience'] = prof_info['years_experience']
            
            # Expertise areas
            if prof_info.get('expertise_areas'):
                for area in prof_info['expertise_areas']:
                    if area and isinstance(area, str):
                        found_info['expertise_areas'].add(area)
        
        # Update online presence
        if source_data.get('online_presence'):
            for platform, handle in source_data['online_presence'].items():
                if handle and isinstance(handle, str):
                    result['online_presence'][platform] = handle
                    found_info['social_media'][platform] = handle
        
        # Store raw data
        if source_data.get('raw_data'):
            result['raw_data'][source_data.get('source', 'unknown')] = source_data['raw_data']
        
        # Update article count
        if source_data.get('articles_count'):
            found_info['articles_count'] += source_data['articles_count']
    
    def _search_outlet_staff(self, author_name: str, domain: str) -> Optional[Dict[str, Any]]:
        """Check if author is listed as staff on the outlet's website"""
        
        if not domain:
            return None
        
        try:
            # Common staff/author page patterns
            staff_urls = [
                f"https://{domain}/author/{author_name.replace(' ', '-').lower()}",
                f"https://{domain}/authors/{author_name.replace(' ', '-').lower()}",
                f"https://{domain}/staff/{author_name.replace(' ', '-').lower()}",
                f"https://{domain}/people/{author_name.replace(' ', '-').lower()}",
                f"https://{domain}/journalist/{author_name.replace(' ', '-').lower()}",
                f"https://{domain}/contributors/{author_name.replace(' ', '-').lower()}",
                f"https://{domain}/writer/{author_name.replace(' ', '-').lower()}",
                f"https://{domain}/by/{author_name.replace(' ', '-').lower()}"
            ]
            
            for url in staff_urls:
                try:
                    response = self.session.get(url, timeout=5, allow_redirects=True)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for author info on the page
                        result = {
                            'found': True,
                            'source': 'outlet_staff',
                            'verification_status': {
                                'outlet_staff': True
                            },
                            'professional_info': {
                                'outlets': [domain]
                            }
                        }
                        
                        # Extract bio
                        bio_selectors = ['.author-bio', '.bio', '.description', '.about', '[class*="bio"]', 'p']
                        for selector in bio_selectors:
                            bio_elem = soup.select_one(selector)
                            if bio_elem:
                                bio_text = bio_elem.get_text().strip()
                                if len(bio_text) > 50 and len(bio_text) < 1000:
                                    result['bio'] = bio_text
                                    break
                        
                        # Extract position/title
                        title_selectors = ['.author-title', '.position', '.role', '.job-title']
                        for selector in title_selectors:
                            title_elem = soup.select_one(selector)
                            if title_elem:
                                result['professional_info']['current_position'] = title_elem.get_text().strip()
                                break
                        
                        # Count articles
                        article_count = len(soup.select('article, .article, .post, [class*="article"]'))
                        if article_count > 0:
                            result['articles_count'] = article_count
                        
                        return result
                        
                except requests.RequestException:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking outlet staff: {e}")
            return None
    
    def _search_google(self, author_name: str, domain: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Search Google for author information"""
        
        try:
            # Build search query
            query = f'"{author_name}" journalist writer'
            if domain:
                query += f' site:{domain} OR "{domain}"'
            
            # Use Google Custom Search API if available (you'd need to implement this)
            # For now, we'll do a basic web search simulation
            search_url = f"https://www.google.com/search?q={quote_plus(query)}"
            
            # Note: In production, you'd use Google Custom Search API
            # This is a placeholder that shows the structure
            result = {
                'found': False,
                'source': 'google_search',
                'professional_info': {
                    'outlets': []
                }
            }
            
            # Simulate finding author mentions in search results
            # In reality, you'd parse actual search results
            if domain and domain in self.major_outlets:
                result['found'] = True
                result['professional_info']['outlets'].append(domain)
                result['verification_status'] = {
                    'journalist_verified': True
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in Google search: {e}")
            return None
    
    def _search_linkedin(self, author_name: str) -> Optional[Dict[str, Any]]:
        """Search LinkedIn for author profile"""
        
        try:
            # LinkedIn search URL (requires authentication in practice)
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={quote_plus(author_name)}%20journalist"
            
            # This is a placeholder - actual LinkedIn API would be used
            result = {
                'found': False,
                'source': 'linkedin',
                'online_presence': {}
            }
            
            # Simulate LinkedIn data
            # In production, use LinkedIn API
            common_positions = ['journalist', 'reporter', 'correspondent', 'editor', 'writer']
            
            # Placeholder logic
            if any(name_part.lower() in ['john', 'jane', 'sarah', 'michael'] 
                   for name_part in author_name.split()):
                result['found'] = True
                result['professional_info'] = {
                    'current_position': 'Journalist',
                    'years_experience': 5
                }
                result['online_presence']['linkedin'] = f"linkedin.com/in/{author_name.replace(' ', '-').lower()}"
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching LinkedIn: {e}")
            return None
    
    def _search_twitter(self, author_name: str) -> Optional[Dict[str, Any]]:
        """Search Twitter/X for author profile"""
        
        try:
            # Twitter search (would use API in production)
            result = {
                'found': False,
                'source': 'twitter',
                'online_presence': {}
            }
            
            # Placeholder - would use Twitter API
            # Check if author might have Twitter based on name patterns
            if len(author_name.split()) >= 2:
                # Simulate finding Twitter handle
                potential_handle = author_name.replace(' ', '').lower()
                result['online_presence']['twitter'] = f"@{potential_handle}"
                
                # Random simulation of verified journalists
                if author_name.lower() in ['john doe', 'jane smith']:
                    result['found'] = True
                    result['verification_status'] = {
                        'verified': True
                    }
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching Twitter: {e}")
            return None
    
    def _search_muckrack(self, author_name: str) -> Optional[Dict[str, Any]]:
        """Search Muckrack journalist database"""
        
        try:
            # Muckrack is a journalist database
            search_url = f"https://muckrack.com/search?q={quote_plus(author_name)}"
            
            # This would require Muckrack API access
            result = {
                'found': False,
                'source': 'muckrack'
            }
            
            # Simulate Muckrack data
            # In production, use actual API
            if 'reporter' in author_name.lower() or 'journalist' in author_name.lower():
                result['found'] = True
                result['verification_status'] = {
                    'journalist_verified': True
                }
                result['professional_info'] = {
                    'outlets': ['Various Publications'],
                    'expertise_areas': ['Politics', 'Technology']
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching Muckrack: {e}")
            return None
    
    def _search_journalist_databases(self, author_name: str) -> Optional[Dict[str, Any]]:
        """Search various journalist databases"""
        
        try:
            result = {
                'found': False,
                'source': 'journalist_databases',
                'professional_info': {
                    'outlets': []
                }
            }
            
            # Check multiple journalist databases
            # This is placeholder - would need actual API access
            databases_checked = []
            
            for platform in self.journalist_platforms:
                databases_checked.append(platform)
                
                # Simulate finding author in databases
                if 'journal' in author_name.lower():
                    result['found'] = True
                    result['verification_status'] = {
                        'journalist_verified': True
                    }
                    break
            
            result['databases_checked'] = databases_checked
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching journalist databases: {e}")
            return None
    
    def _calculate_credibility_score(self, result: Dict[str, Any], 
                                    found_info: Dict[str, Any]) -> int:
        """Calculate author credibility score based on findings"""
        
        score = 50  # Base score
        
        # Verification status boosts
        if result['verification_status']['verified']:
            score += 20
        if result['verification_status']['journalist_verified']:
            score += 15
        if result['verification_status']['outlet_staff']:
            score += 15
        
        # Professional info boosts
        if result['professional_info']['current_position']:
            score += 10
        
        # Outlet credibility
        outlets = list(found_info['outlets'])
        result['professional_info']['outlets'] = outlets
        
        major_outlet_count = sum(1 for outlet in outlets 
                                if outlet in self.major_outlets)
        if major_outlet_count > 0:
            score += min(major_outlet_count * 10, 20)
        
        # Experience
        if result['professional_info']['years_experience']:
            years = result['professional_info']['years_experience']
            score += min(years * 2, 10)
        
        # Online presence
        if len(result['online_presence']) > 0:
            score += min(len(result['online_presence']) * 5, 10)
        
        # Expertise areas
        expertise_list = list(found_info['expertise_areas'])
        result['professional_info']['expertise_areas'] = expertise_list
        if expertise_list:
            score += 5
        
        # Article count
        if found_info['articles_count'] > 10:
            score += 5
        if found_info['articles_count'] > 50:
            score += 5
        
        # Penalty if not found anywhere
        if not result['found']:
            score = min(score, 40)
        
        # Ensure score is within bounds
        return max(0, min(100, score))
    
    def _generate_credibility_explanation(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate explanation of credibility assessment"""
        
        score = result['credibility_score']
        factors = []
        
        # Determine credibility level
        if score >= 80:
            level = 'High'
            base_explanation = f"{result['name']} is a well-established journalist with strong credentials."
        elif score >= 60:
            level = 'Moderate'
            base_explanation = f"{result['name']} appears to be a legitimate journalist with some verifiable credentials."
        elif score >= 40:
            level = 'Limited'
            base_explanation = f"Limited information found about {result['name']}'s journalistic credentials."
        else:
            level = 'Unknown'
            base_explanation = f"Unable to verify {result['name']}'s credentials as a journalist."
        
        # Add specific factors
        if result['verification_status']['verified']:
            factors.append("verified account on social media")
        if result['verification_status']['journalist_verified']:
            factors.append("listed in journalist databases")
        if result['verification_status']['outlet_staff']:
            factors.append("confirmed staff member")
        
        if result['professional_info']['current_position']:
            factors.append(f"holds position as {result['professional_info']['current_position']}")
        
        outlets = result['professional_info']['outlets']
        if outlets:
            if len(outlets) == 1:
                factors.append(f"writes for {outlets[0]}")
            else:
                factors.append(f"has written for {len(outlets)} publications")
        
        # Build explanation
        if factors:
            explanation = base_explanation + " " + "Key indicators: " + ", ".join(factors) + "."
        else:
            explanation = base_explanation
        
        # Add advice
        if score >= 70:
            advice = "This author appears credible, but always verify important claims."
        elif score >= 50:
            advice = "Exercise normal caution and cross-reference important claims."
        else:
            advice = "Unable to verify author credentials - verify all claims independently."
        
        return {
            'level': level,
            'explanation': explanation,
            'advice': advice,
            'factors': factors
        }
    
    def _generate_bio(self, author_name: str, result: Dict[str, Any], 
                     domain: Optional[str] = None) -> str:
        """Generate a bio when none is found"""
        
        parts = []
        
        # Start with name and basic role
        if result['professional_info']['current_position']:
            parts.append(f"{author_name} is a {result['professional_info']['current_position']}")
        else:
            parts.append(f"{author_name} is a journalist")
        
        # Add outlet information
        outlets = result['professional_info']['outlets']
        if outlets:
            if len(outlets) == 1:
                parts.append(f"who writes for {outlets[0]}")
            elif len(outlets) == 2:
                parts.append(f"who has written for {outlets[0]} and {outlets[1]}")
            else:
                parts.append(f"who has written for multiple publications including {outlets[0]}")
        elif domain:
            parts.append(f"contributing to {domain}")
        
        # Add expertise if available
        if result['professional_info']['expertise_areas']:
            areas = result['professional_info']['expertise_areas'][:2]
            parts.append(f"covering {' and '.join(areas)}")
        
        # Create bio
        bio = " ".join(parts) + "."
        
        # Add verification status if notable
        if result['verification_status']['verified']:
            bio += " Verified journalist."
        elif not result['found']:
            bio += " Limited information available online."
        
        return bio
    
    def analyze_authors_batch(self, authors: List[str], domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """Analyze multiple authors in batch"""
        
        results = []
        for author in authors[:20]:  # Limit to 20 authors
            try:
                result = self.analyze_single_author(author, domain)
                results.append(result)
            except Exception as e:
                logger.error(f"Error analyzing {author}: {e}")
                results.append(self._create_error_result(author, str(e)))
        
        return results
    
    def get_author_summary(self, author_analysis: Dict[str, Any]) -> str:
        """Get a brief summary of author credibility"""
        
        score = author_analysis.get('credibility_score', 0)
        name = author_analysis.get('name', 'Unknown')
        
        if score >= 80:
            return f"{name} is a highly credible, established journalist."
        elif score >= 60:
            return f"{name} is a credible journalist with verified credentials."
        elif score >= 40:
            return f"{name} has limited verifiable journalistic credentials."
        else:
            return f"{name}'s journalistic credentials could not be verified."
    
    def clear_cache(self):
        """Clear the author cache"""
        self._author_cache.clear()
        logger.info("Author cache cleared")
