"""
FILE: services/author_analyzer.py
LOCATION: news/services/author_analyzer.py
PURPOSE: Analyze journalist/author credibility and background
"""

import os
import logging
import requests
import re
from urllib.parse import quote

logger = logging.getLogger(__name__)

class AuthorAnalyzer:
    """Analyze author credibility and background"""
    
    def __init__(self):
        self.session = requests.Session()
        self.google_api_key = os.environ.get('GOOGLE_API_KEY')
        self.news_api_key = os.environ.get('NEWS_API_KEY')
    
    def analyze_author(self, author_name, article_domain=None):
        """
        Comprehensive author analysis
        
        Returns:
            dict: Author information including credibility, bio, website, etc.
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
            'credibility_score': None,
            'bio': None,
            'expertise': [],
            'awards': [],
            'website': None,
            'social_media': {},
            'previous_work': [],
            'controversies': [],
            'verification_status': 'unverified'
        }
        
        # Search for author information
        if self.google_api_key:
            analysis.update(self._google_search_author(author_name, article_domain))
        
        # Search for author's other articles
        if self.news_api_key:
            analysis['previous_work'] = self._find_other_articles(author_name)
        
        # Analyze author credibility based on available data
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
    
    def _google_search_author(self, author_name, domain=None):
        """Search Google for author information"""
        results = {
            'bio': None,
            'website': None,
            'expertise': [],
            'awards': []
        }
        
        try:
            # Search for author bio and credentials
            search_query = f'"{author_name}" journalist biography credentials'
            if domain:
                search_query += f' site:{domain}'
            
            url = 'https://www.googleapis.com/customsearch/v1'
            params = {
                'key': self.google_api_key,
                'cx': os.environ.get('GOOGLE_CSE_ID'),  # Custom Search Engine ID
                'q': search_query,
                'num': 5
            }
            
            response = self.session.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                
                # Extract information from search results
                for item in items:
                    snippet = item.get('snippet', '').lower()
                    
                    # Look for bio information
                    if 'journalist' in snippet or 'reporter' in snippet:
                        if not results['bio']:
                            results['bio'] = item.get('snippet')
                    
                    # Look for awards
                    if any(word in snippet for word in ['award', 'pulitzer', 'emmy', 'peabody']):
                        results['awards'].append(item.get('snippet'))
                    
                    # Check for author website
                    if author_name.lower() in item.get('link', '').lower():
                        if not results['website']:
                            results['website'] = item.get('link')
            
            # Search for author's professional website
            if not results['website']:
                website_search = f'"{author_name}" journalist website portfolio'
                params['q'] = website_search
                params['num'] = 3
                
                response = self.session.get(url, params=params, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get('items', []):
                        link = item.get('link', '')
                        if any(platform in link for platform in ['linkedin.com', 'muckrack.com', 'twitter.com']):
                            results['website'] = link
                            break
                            
        except Exception as e:
            logger.error(f"Error searching for author {author_name}: {str(e)}")
        
        return results
    
    def _find_other_articles(self, author_name):
        """Find other articles by the same author"""
        articles = []
        
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                'apiKey': self.news_api_key,
                'q': f'"{author_name}"',
                'searchIn': 'author',
                'sortBy': 'relevancy',
                'pageSize': 10,
                'language': 'en'
            }
            
            response = self.session.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                for article in data.get('articles', [])[:5]:
                    if article.get('author') and author_name.lower() in article['author'].lower():
                        articles.append({
                            'title': article.get('title'),
                            'source': article.get('source', {}).get('name'),
                            'url': article.get('url'),
                            'publishedAt': article.get('publishedAt')
                        })
                        
        except Exception as e:
            logger.error(f"Error finding articles by {author_name}: {str(e)}")
        
        return articles
    
    def _calculate_credibility_score(self, analysis):
        """Calculate author credibility score based on available information"""
        score = 50  # Start at neutral
        
        # Positive factors
        if analysis.get('bio'):
            score += 10
        if analysis.get('website'):
            score += 10
        if analysis.get('awards'):
            score += 20
        if len(analysis.get('previous_work', [])) > 3:
            score += 15
        
        # Normalize to 0-100
        score = min(100, max(0, score))
        
        return score
    
    def _generate_credibility_assessment(self, analysis):
        """Generate human-readable credibility assessment"""
        score = analysis.get('credibility_score', 50)
        name = analysis.get('name', 'The author')
        
        if score >= 80:
            assessment = f"{name} appears to be a well-established journalist with a strong track record. "
            if analysis.get('awards'):
                assessment += "They have received recognition for their work. "
        elif score >= 60:
            assessment = f"{name} seems to be a legitimate journalist with some established work. "
            if analysis.get('previous_work'):
                assessment += f"Found {len(analysis['previous_work'])} other articles by this author. "
        elif score >= 40:
            assessment = f"{name} has limited publicly available information. "
            assessment += "This doesn't necessarily indicate poor credibility, but more research may be needed. "
        else:
            assessment = f"Could not find substantial information about {name}. "
            assessment += "Consider verifying the author's credentials independently. "
        
        if analysis.get('website'):
            assessment += f"Author website/profile found. "
        
        return assessment
    
    def get_author_snippet(self, author_name, article_domain=None):
        """Get a brief author snippet for inline display"""
        if not author_name:
            return "Author information not available"
        
        # For quick display, just return basic info
        # Full analysis happens separately
        clean_name = self._clean_author_name(author_name)
        
        if article_domain and article_domain in ['nytimes.com', 'washingtonpost.com', 'bbc.com', 'reuters.com', 'apnews.com']:
            return f"{clean_name} - Staff journalist at {article_domain}"
        
        return clean_name
