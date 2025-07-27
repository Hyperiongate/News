"""
FILE: services/author_analyzer_diagnostic.py
PURPOSE: Diagnostic version of author analyzer to identify where the problem is
LOCATION: services/author_analyzer_diagnostic.py
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

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AuthorAnalyzer:
    """Diagnostic author analyzer with extensive logging"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        logger.info("🟢 AuthorAnalyzer initialized - DIAGNOSTIC MODE")
        self.diagnostic_data = {
            'initialization': 'success',
            'searches_attempted': [],
            'searches_successful': [],
            'data_found': {}
        }
        
    def analyze_authors(self, author_text, domain=None):
        """Analyze multiple authors from byline text"""
        authors = self._parse_authors(author_text)
        results = []
        
        for author_name in authors:
            result = self.analyze_single_author(author_name, domain)
            results.append(result)
        
        return results
    
    def analyze_single_author(self, author_name, domain=None):
        """Analyze a single author with diagnostic output"""
        logger.info(f"🔍 DIAGNOSTIC: Starting analysis for author: '{author_name}' from domain: '{domain}'")
        
        # Clean author name
        clean_name = self._clean_author_name(author_name)
        logger.info(f"📝 Cleaned author name: '{clean_name}'")
        
        # Initialize result with diagnostic info
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
            },
            # DIAGNOSTIC DATA
            '_diagnostic': {
                'timestamp': datetime.now().isoformat(),
                'searches_performed': [],
                'errors_encountered': [],
                'data_sources': []
            }
        }
        
        # Skip database cache for diagnostic purposes
        logger.info("⏭️ DIAGNOSTIC: Skipping database cache check")
        
        # 1. Check outlet's author page
        if domain:
            try:
                logger.info(f"🌐 DIAGNOSTIC: Checking outlet author page on {domain}")
                outlet_result = self._check_outlet_author_page_diagnostic(clean_name, domain)
                if outlet_result:
                    self._safe_merge_results(result, outlet_result)
                    result['found'] = True
                    result['sources_checked'].append(f"{domain} author page")
                    result['_diagnostic']['data_sources'].append('outlet_page')
                    logger.info(f"✅ Found author on {domain}")
                else:
                    logger.info(f"❌ No author page found on {domain}")
            except Exception as e:
                logger.error(f"❌ ERROR checking outlet author page: {e}")
                result['_diagnostic']['errors_encountered'].append(f"outlet_page: {str(e)}")
        
        # 2. Simple web search test
        try:
            logger.info(f"🔍 DIAGNOSTIC: Testing simple web search")
            test_url = f"https://html.duckduckgo.com/html/?q={quote(clean_name + ' journalist')}"
            result['_diagnostic']['searches_performed'].append(test_url)
            
            response = self.session.get(test_url, timeout=10)
            logger.info(f"📊 Search response status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                results_found = len(soup.find_all('div', class_='result'))
                logger.info(f"📈 Found {results_found} search results")
                
                if clean_name.lower() in response.text.lower():
                    result['found'] = True
                    result['_diagnostic']['data_sources'].append('web_search')
                    
                    # Extract some basic info
                    for result_div in soup.find_all('div', class_='result')[:5]:
                        snippet = result_div.get_text(separator=' ', strip=True)
                        if clean_name.lower() in snippet.lower() and 'journalist' in snippet.lower():
                            logger.info(f"✅ Found relevant snippet: {snippet[:100]}...")
                            if not result['bio']:
                                result['bio'] = snippet[:300]
                            break
            else:
                logger.error(f"❌ Search failed with status {response.status_code}")
                result['_diagnostic']['errors_encountered'].append(f"search_status: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ ERROR in web search: {e}")
            result['_diagnostic']['errors_encountered'].append(f"web_search: {str(e)}")
        
        # 3. Generate diagnostic bio if nothing found
        if not result['bio']:
            if result['found']:
                result['bio'] = f"{clean_name} is a journalist. Additional biographical information is currently being compiled."
            else:
                result['bio'] = f"Limited information available about {clean_name}. Unable to verify journalist credentials at this time."
            logger.info(f"📝 Generated fallback bio")
        
        # 4. Set credibility score based on findings
        if result['found']:
            result['credibility_score'] = 60
            if result['_diagnostic']['data_sources']:
                result['credibility_score'] = 70
            if domain and 'outlet_page' in result['_diagnostic']['data_sources']:
                result['credibility_score'] = 80
        else:
            result['credibility_score'] = 40
        
        logger.info(f"📊 Final credibility score: {result['credibility_score']}")
        
        # 5. Generate diagnostic explanation
        result['credibility_explanation'] = self._generate_diagnostic_explanation(result)
        
        # Log final diagnostic summary
        logger.info(f"""
🎯 DIAGNOSTIC SUMMARY for {clean_name}:
- Found: {result['found']}
- Credibility Score: {result['credibility_score']}
- Data Sources: {result['_diagnostic']['data_sources']}
- Errors: {result['_diagnostic']['errors_encountered']}
- Bio Length: {len(result.get('bio', ''))}
- Sources Checked: {result['sources_checked']}
        """)
        
        return result
    
    def _check_outlet_author_page_diagnostic(self, author_name, domain):
        """Diagnostic version of outlet page checker"""
        clean_domain = domain.replace('www.', '')
        author_slug = author_name.lower().replace(' ', '-')
        
        # Try just a few URL patterns for diagnostic
        url_patterns = [
            f"https://{domain}/author/{author_slug}/",
            f"https://{domain}/authors/{author_slug}/",
            f"https://{domain}/{author_slug}/",
            f"https://www.{clean_domain}/author/{author_slug}/"
        ]
        
        for url in url_patterns:
            try:
                logger.info(f"🔗 Checking URL: {url}")
                response = self.session.get(url, timeout=5, allow_redirects=True)
                logger.info(f"📊 Response: {response.status_code}, Final URL: {response.url}")
                
                if response.status_code == 200:
                    if author_name.lower() in response.text.lower():
                        logger.info(f"✅ Author name found in page")
                        return {
                            'online_presence': {'outlet_profile': url},
                            'verification_status': {
                                'verified': True,
                                'outlet_staff': True
                            },
                            'bio': f"{author_name} is a verified staff writer at {self._clean_outlet_name(domain)}."
                        }
            except Exception as e:
                logger.debug(f"❌ Failed to check {url}: {e}")
                continue
        
        return None
    
    def _generate_diagnostic_explanation(self, author_data):
        """Generate diagnostic explanation"""
        score = author_data.get('credibility_score', 0)
        found = author_data.get('found', False)
        sources = author_data.get('_diagnostic', {}).get('data_sources', [])
        errors = author_data.get('_diagnostic', {}).get('errors_encountered', [])
        
        if errors:
            level = 'Error'
            explanation = f"Encountered errors during author verification: {', '.join(errors[:2])}"
            advice = "Author verification system experiencing issues. Please verify author independently."
        elif found and sources:
            level = 'Verified'
            explanation = f"Author verified through: {', '.join(sources)}"
            advice = "Author credentials have been confirmed through multiple sources."
        elif found:
            level = 'Found'
            explanation = "Author found in search results but limited verification available."
            advice = "Basic author information found. Verify credentials through additional sources."
        else:
            level = 'Unverified'
            explanation = "Unable to find verifiable information about this author."
            advice = "Could not verify author credentials. Exercise caution and verify claims independently."
        
        return {
            'level': level,
            'explanation': explanation,
            'advice': advice,
            'diagnostic_info': f"Score: {score}, Sources: {len(sources)}, Errors: {len(errors)}"
        }
    
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
                for item in value:
                    if item not in target[key]:
                        target[key].append(item)
            elif key == 'bio':
                if not target.get(key) or (value and len(str(value)) > len(str(target[key]))):
                    target[key] = value
            elif value is not None:
                target[key] = value
    
    def _clean_author_name(self, author_name):
        """Clean and standardize author name"""
        if not author_name:
            return "Unknown"
            
        # Remove common suffixes
        name = re.sub(r'\s*(,|and|&)\s*.*', '', author_name)
        
        # Remove common prefixes
        name = re.sub(r'^(by|written by|article by|reported by)\s+', '', name, flags=re.I)
        
        # Remove titles
        titles = ['Dr.', 'Prof.', 'Mr.', 'Mrs.', 'Ms.', 'Sir', 'Dame']
        for title in titles:
            name = name.replace(title, '').strip()
        
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        return name if name else "Unknown"
    
    def _clean_outlet_name(self, domain):
        """Extract clean outlet name from domain"""
        if not domain:
            return "Unknown Outlet"
        
        domain = domain.lower()
        domain = domain.replace('www.', '')
        domain = domain.replace('.com', '').replace('.org', '').replace('.net', '')
        domain = domain.replace('.co.uk', '').replace('.co', '')
        
        # Known outlets
        outlet_map = {
            'nytimes': 'The New York Times',
            'washingtonpost': 'The Washington Post',
            'cnn': 'CNN',
            'bbc': 'BBC',
            'foxnews': 'Fox News',
            'abcnews': 'ABC News'
        }
        
        for key, value in outlet_map.items():
            if key in domain:
                return value
        
        parts = domain.split('-')
        return ' '.join(word.capitalize() for word in parts)
    
    def _parse_authors(self, author_text):
        """Parse multiple authors from byline text"""
        if not author_text:
            return []
        
        author_text = re.sub(r'^(by|written by|article by|reported by)\s+', '', author_text, flags=re.I)
        authors = re.split(r'\s*(?:,|and|&)\s*', author_text)
        
        cleaned_authors = []
        for author in authors:
            cleaned = self._clean_author_name(author)
            if cleaned and len(cleaned) > 2 and cleaned != "Unknown":
                cleaned_authors.append(cleaned)
        
        return cleaned_authors
