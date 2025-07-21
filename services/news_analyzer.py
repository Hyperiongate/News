"""
FILE: services/author_analyzer.py
LOCATION: news/services/author_analyzer.py
PURPOSE: Analyze journalist/author credibility using Google Search
"""

import os
import logging
import requests
import re
import json
from urllib.parse import quote

logger = logging.getLogger(__name__)

class AuthorAnalyzer:
    """Analyze author credibility and background using Google Search"""
    
    def __init__(self):
        self.session = requests.Session()
        self.google_api_key = os.environ.get('GOOGLE_API_KEY')
        self.google_cse_id = os.environ.get('GOOGLE_CSE_ID')  # Custom Search Engine ID
        
        # Initialize with basic known journalists data
        self.known_journalists = {
            'yolande knell': {
                'outlets': ['BBC'],
                'expertise': ['Middle East correspondent'],
                'base_credibility': 80
            }
        }
    
    def analyze_author(self, author_name, article_domain=None):
        """
        Comprehensive author analysis using Google Search
        """
        if not author_name:
            return {
                'found': False,
                'message': 'No author information available'
            }
        
        # Clean author name
        author_name = self._clean_author_name(author_name)
        
        analysis = {
            'name': author_name,
            'found': True,
            'credibility_score': 50,  # Start neutral
            'bio': None,
            'expertise': [],
            'awards': [],
            'website': None,
            'social_media': {},
            'previous_work': [],
            'outlets': [],
            'verification_status': 'unverified',
            'search_results': []
        }
        
        # Check known journalists first
        known_info = self.known_journalists.get(author_name.lower())
        if known_info:
            analysis['credibility_score'] = known_info.get('base_credibility', 70)
            analysis['outlets'] = known_info.get('outlets', [])
            analysis['expertise'] = known_info.get('expertise', [])
        
        # Search Google if API key available
        if self.google_api_key and self.google_cse_id:
            google_results = self._google_search_author(author_name, article_domain)
            analysis.update(google_results)
        elif self.google_api_key:
            # Use regular Google Search API
            google_results = self._google_web_search(author_name, article_domain)
            analysis.update(google_results)
        
        # Calculate final credibility score
        analysis['credibility_score'] = self._calculate_credibility_score(analysis)
        analysis['credibility_assessment'] = self._generate_credibility_assessment(analysis)
        
        return analysis
    
    def _clean_author_name(self, name):
        """Clean and normalize author name"""
        # Remove common prefixes
        name = re.sub(r'^(by|By|BY)\s+', '', name)
        # Remove extra whitespace
        name = ' '.join(name.split())
        # Remove trailing punctuation
        name = name.rstrip('.,;:')
        return name
    
    def _google_web_search(self, author_name, domain=None):
        """Use Google Search API to find author information"""
        results = {
            'bio': None,
            'website': None,
            'expertise': [],
            'awards': [],
            'outlets': [],
            'search_results': []
        }
        
        if not self.google_api_key:
            return results
        
        try:
            # Search for author information
            queries = [
                f'"{author_name}" journalist biography',
                f'"{author_name}" reporter profile',
                f'"{author_name}" journalist awards credentials'
            ]
            
            if domain:
                queries[0] += f' site:{domain}'
            
            base_url = 'https://www.googleapis.com/customsearch/v1'
            
            for query in queries[:2]:  # Limit API calls
                params = {
                    'key': self.google_api_key,
                    'q': query,
                    'num': 10
                }
                
                if self.google_cse_id:
                    params['cx'] = self.google_cse_id
                
                response = self.session.get(base_url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for item in data.get('items', []):
                        result_info = {
                            'title': item.get('title', ''),
                            'snippet': item.get('snippet', ''),
                            'link': item.get('link', '')
                        }
                        results['search_results'].append(result_info)
                        
                        snippet = item.get('snippet', '').lower()
                        title = item.get('title', '').lower()
                        link = item.get('link', '')
                        
                        # Extract bio
                        if not results['bio'] and any(word in snippet for word in ['journalist', 'reporter', 'correspondent']):
                            results['bio'] = item.get('snippet')
                        
                        # Look for credentials and awards
                        award_keywords = ['award', 'pulitzer', 'emmy', 'peabody', 'murrow', 'polk', 'honor']
                        if any(word in snippet for word in award_keywords):
                            results['awards'].append(item.get('snippet'))
                        
                        # Find social media/website
                        if author_name.lower() in link.lower():
                            if 'twitter.com' in link or 'x.com' in link:
                                results['website'] = link
                                results['social_media']['twitter'] = link
                            elif 'linkedin.com' in link:
                                results['social_media']['linkedin'] = link
                            elif 'muckrack.com' in link:
                                results['website'] = link
                            elif not results['website'] and ('bio' in link or 'about' in link or 'profile' in link):
                                results['website'] = link
                        
                        # Extract outlets
                        major_outlets = ['new york times', 'washington post', 'cnn', 'bbc', 'reuters', 
                                       'associated press', 'guardian', 'npr', 'wsj', 'forbes']
                        for outlet in major_outlets:
                            if outlet in snippet or outlet in title:
                                outlet_name = outlet.title()
                                if outlet_name not in results['outlets']:
                                    results['outlets'].append(outlet_name)
                        
                        # Extract expertise
                        if 'correspondent' in snippet:
                            expertise_match = re.search(r'(\w+\s+correspondent)', snippet, re.I)
                            if expertise_match:
                                results['expertise'].append(expertise_match.group(1))
                
                else:
                    logger.warning(f"Google API error: {response.status_code}")
            
            # Remove duplicates
            results['awards'] = list(set(results['awards']))[:3]
            results['expertise'] = list(set(results['expertise']))
            results['outlets'] = list(set(results['outlets']))
            
        except Exception as e:
            logger.error(f"Error searching for author {author_name}: {str(e)}")
        
        return results
    
    def _calculate_credibility_score(self, analysis):
        """Calculate author credibility score based on found information"""
        score = 40  # Base score
        
        # Positive factors
        if analysis.get('bio'):
            score += 15
        
        if analysis.get('website'):
            score += 10
            if 'linkedin' in str(analysis.get('social_media', {})):
                score += 5
        
        if analysis.get('awards'):
            score += min(len(analysis['awards']) * 10, 30)  # Max 30 points for awards
        
        if analysis.get('outlets'):
            # Major outlets add credibility
            major_outlets = ['New York Times', 'Washington Post', 'BBC', 'CNN', 'Reuters', 
                           'Associated Press', 'Guardian', 'NPR', 'WSJ']
            for outlet in analysis['outlets']:
                if outlet in major_outlets:
                    score += 5
            score = min(score, 95)  # Cap contribution
        
        if len(analysis.get('search_results', [])) > 5:
            score += 5  # Well-documented online presence
        
        # Ensure score is within bounds
        score = min(100, max(0, score))
        
        return score
    
    def _generate_credibility_assessment(self, analysis):
        """Generate human-readable credibility assessment"""
        score = analysis.get('credibility_score', 50)
        name = analysis.get('name', 'The author')
        
        assessment = f"{name} "
        
        if score >= 80:
            assessment += "appears to be a well-established journalist with strong credentials. "
            if analysis.get('awards'):
                assessment += f"Has received recognition for their work. "
            if analysis.get('outlets'):
                assessment += f"Has written for: {', '.join(analysis['outlets'][:3])}. "
        elif score >= 60:
            assessment += "appears to be a legitimate journalist with verified work history. "
            if analysis.get('outlets'):
                assessment += f"Associated with: {', '.join(analysis['outlets'][:2])}. "
        elif score >= 40:
            assessment += "has limited publicly available information. "
            assessment += "This doesn't necessarily indicate poor credibility, but independent verification is recommended. "
        else:
            assessment += "could not be verified through public sources. "
            assessment += "Consider checking the article's claims carefully and consulting additional sources. "
        
        if analysis.get('expertise'):
            assessment += f"Areas of expertise: {', '.join(analysis['expertise'][:2])}. "
        
        return assessment.strip()
