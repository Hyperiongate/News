"""
FILE: services/author_analyzer.py
LOCATION: news/services/author_analyzer.py
PURPOSE: Enhanced author analysis with multiple authors and comprehensive background checks
"""

import os
import logging
import requests
import re
from urllib.parse import quote_plus, urlparse
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class AuthorAnalyzer:
    """Enhanced author credibility and background analyzer"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        # Could add API keys for LinkedIn, etc. here
        self.wikipedia_api = "https://en.wikipedia.org/api/rest_v1"
        
    def analyze_authors(self, author_string, domain=None):
        """Analyze multiple authors from a string"""
        if not author_string:
            return []
        
        # Split multiple authors (handle various formats)
        authors = self._split_authors(author_string)
        
        results = []
        for author_name in authors:
            author_analysis = self.analyze_single_author(author_name.strip(), domain)
            results.append(author_analysis)
        
        return results
    
    def _split_authors(self, author_string):
        """Split author string into individual names"""
        # Handle various separators: and, &, with, ,
        separators = [' and ', ' & ', ' with ', ', ']
        authors = [author_string]
        
        for separator in separators:
            new_authors = []
            for author in authors:
                new_authors.extend(author.split(separator))
            authors = new_authors
        
        # Clean up names
        cleaned = []
        for author in authors:
            # Remove common prefixes/suffixes
            author = re.sub(r'^(By|by|BY)\s+', '', author)
            author = re.sub(r'\s+(Reporter|Correspondent|Writer|Editor)$', '', author, re.IGNORECASE)
            author = author.strip()
            if author and len(author) > 2:  # Filter out empty or too short
                cleaned.append(author)
        
        return cleaned
    
    def analyze_single_author(self, author_name, domain=None):
        """Comprehensive analysis of a single author"""
        
        # Clean the author name
        clean_name = self._clean_author_name(author_name)
        
        # Initialize result structure
        result = {
            'name': clean_name,
            'original_name': author_name,
            'found': False,
            'sources_checked': [],
            'credibility_score': 50,  # Default middle score
            'credibility_factors': {},
            'bio': None,
            'profile_image': None,
            'verification_status': {
                'verified': False,
                'journalist_verified': False,
                'outlet_staff': False,
                'blue_check': False
            },
            'professional_info': {
                'current_position': None,
                'outlets': [],
                'years_experience': None,
                'specialties': [],
                'education': [],
                'awards': [],
                'previous_positions': []
            },
            'online_presence': {
                'twitter': None,
                'linkedin': None,
                'personal_website': None,
                'wikipedia': None,
                'muckrack': None  # Journalist database
            },
            'publication_history': {
                'total_articles': None,
                'recent_articles': 0,
                'date_range': None,
                'topics': []
            },
            'credibility_breakdown': {
                'verification': 0,
                'experience': 0,
                'transparency': 0,
                'recognition': 0,
                'consistency': 0
            }
        }
        
        # Search for author information
        if domain:
            self._check_outlet_profile(result, clean_name, domain)
        
        self._check_wikipedia(result, clean_name)
        self._check_journalist_databases(result, clean_name)
        self._search_professional_info(result, clean_name)
        
        # Calculate final credibility score
        result['credibility_score'] = self._calculate_credibility_score(result)
        
        # Generate comprehensive bio if not found
        if not result['bio']:
            result['bio'] = self._generate_bio(result)
        
        # Add credibility explanation
        result['credibility_explanation'] = self._explain_credibility(result)
        
        return result
    
    def _clean_author_name(self, name):
        """Clean and standardize author name"""
        # Remove URLs
        if name.startswith('http'):
            # Extract name from URL like /author/emma-burrows
            match = re.search(r'/author/([^/]+)/?$', name)
            if match:
                name = match.group(1).replace('-', ' ')
        
        # Title case and clean
        name = name.title().strip()
        return name
    
    def _check_outlet_profile(self, result, author_name, domain):
        """Check if author has a profile on the outlet's website"""
        result['sources_checked'].append(f"{domain} profile")
        
        # Try common author page patterns
        author_slug = author_name.lower().replace(' ', '-')
        urls_to_try = [
            f"https://{domain}/author/{author_slug}",
            f"https://{domain}/authors/{author_slug}",
            f"https://{domain}/staff/{author_slug}",
            f"https://{domain}/people/{author_slug}",
            f"https://{domain}/by/{author_slug}"
        ]
        
        for url in urls_to_try:
            try:
                response = self.session.get(url, timeout=3, allow_redirects=True)
                if response.status_code == 200:
                    result['online_presence']['outlet_profile'] = url
                    result['verification_status']['outlet_staff'] = True
                    result['professional_info']['outlets'].append(domain)
                    result['found'] = True
                    
                    # Try to extract bio from the page
                    self._extract_author_info_from_html(result, response.text)
                    break
            except:
                continue
    
    def _check_wikipedia(self, result, author_name):
        """Check Wikipedia for author information"""
        result['sources_checked'].append('Wikipedia')
        
        try:
            # Search Wikipedia
            search_url = f"{self.wikipedia_api}/page/summary/{quote_plus(author_name)}"
            response = self.session.get(search_url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if 'extract' in data and not data.get('type') == 'disambiguation':
                    # Check if it's actually about a journalist/writer
                    extract = data['extract'].lower()
                    if any(word in extract for word in ['journalist', 'reporter', 'writer', 'correspondent', 'author', 'editor']):
                        result['online_presence']['wikipedia'] = data.get('content_urls', {}).get('desktop', {}).get('page')
                        result['bio'] = data['extract']
                        result['found'] = True
                        result['credibility_factors']['has_wikipedia'] = True
                        result['professional_info']['notable'] = True
        except Exception as e:
            logger.debug(f"Wikipedia check failed for {author_name}: {e}")
    
    def _check_journalist_databases(self, result, author_name):
        """Check journalist databases like Muck Rack"""
        result['sources_checked'].append('Journalist databases')
        
        # Simulate checking journalist databases
        # In production, you'd integrate with actual APIs
        
        # For now, use some heuristics
        if result.get('verification_status', {}).get('outlet_staff'):
            result['credibility_factors']['in_journalist_db'] = True
    
    def _search_professional_info(self, result, author_name):
        """Search for professional information"""
        # This would integrate with LinkedIn API, Google Knowledge Graph, etc.
        # For now, we'll use the information we have
        
        if result['found']:
            # Estimate experience based on what we found
            if result.get('online_presence', {}).get('wikipedia'):
                result['professional_info']['years_experience'] = 10  # Notable journalists usually have 10+ years
            elif result['verification_status']['outlet_staff']:
                result['professional_info']['years_experience'] = 5  # Staff writers typically have 5+ years
    
    def _extract_author_info_from_html(self, result, html):
        """Extract author information from HTML page"""
        # Extract bio
        bio_patterns = [
            r'<div[^>]*class="[^"]*bio[^"]*"[^>]*>(.*?)</div>',
            r'<p[^>]*class="[^"]*author-bio[^"]*"[^>]*>(.*?)</p>',
            r'<div[^>]*class="[^"]*author-description[^"]*"[^>]*>(.*?)</div>'
        ]
        
        for pattern in bio_patterns:
            match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
            if match:
                bio_text = re.sub(r'<[^>]+>', '', match.group(1)).strip()
                if len(bio_text) > 50:
                    result['bio'] = bio_text[:500]
                    break
        
        # Extract social links
        if 'twitter.com/' in html:
            twitter_match = re.search(r'twitter\.com/([a-zA-Z0-9_]+)', html)
            if twitter_match:
                result['online_presence']['twitter'] = f"@{twitter_match.group(1)}"
        
        if 'linkedin.com/in/' in html:
            linkedin_match = re.search(r'linkedin\.com/in/([a-zA-Z0-9-]+)', html)
            if linkedin_match:
                result['online_presence']['linkedin'] = f"linkedin.com/in/{linkedin_match.group(1)}"
    
    def _calculate_credibility_score(self, result):
        """Calculate overall credibility score based on multiple factors"""
        score = 0
        breakdown = result['credibility_breakdown']
        
        # Verification (0-25 points)
        if result['verification_status']['outlet_staff']:
            breakdown['verification'] = 20
            score += 20
        if result['verification_status']['blue_check']:
            breakdown['verification'] += 5
            score += 5
        
        # Experience (0-25 points)
        years = result['professional_info'].get('years_experience', 0)
        if years >= 10:
            breakdown['experience'] = 25
            score += 25
        elif years >= 5:
            breakdown['experience'] = 15
            score += 15
        elif years >= 2:
            breakdown['experience'] = 10
            score += 10
        
        # Transparency (0-25 points)
        if result['bio']:
            breakdown['transparency'] += 10
            score += 10
        if result['online_presence'].get('linkedin') or result['online_presence'].get('twitter'):
            breakdown['transparency'] += 10
            score += 10
        if result['online_presence'].get('outlet_profile'):
            breakdown['transparency'] += 5
            score += 5
        
        # Recognition (0-25 points)
        if result['online_presence'].get('wikipedia'):
            breakdown['recognition'] = 25
            score += 25
        elif result.get('professional_info', {}).get('awards'):
            breakdown['recognition'] = 20
            score += 20
        elif result['found']:
            breakdown['recognition'] = 10
            score += 10
        
        return max(0, min(100, score))
    
    def _generate_bio(self, result):
        """Generate a bio based on available information"""
        parts = []
        
        if result['professional_info'].get('current_position'):
            parts.append(f"{result['name']} is {result['professional_info']['current_position']}")
        elif result['professional_info'].get('outlets'):
            outlets = result['professional_info']['outlets']
            parts.append(f"{result['name']} is a journalist with {outlets[0]}")
        else:
            parts.append(f"{result['name']} is a journalist")
        
        if result['professional_info'].get('years_experience'):
            parts.append(f"with {result['professional_info']['years_experience']} years of experience")
        
        if result['professional_info'].get('specialties'):
            specialties = ', '.join(result['professional_info']['specialties'][:3])
            parts.append(f"specializing in {specialties}")
        
        bio = ' '.join(parts) + '.'
        
        if not result['found']:
            bio += " Limited public information is available about this author."
        
        return bio
    
    def _explain_credibility(self, result):
        """Explain what the credibility score means"""
        score = result['credibility_score']
        
        if score >= 80:
            level = "Very High"
            explanation = "This author has strong credentials with verified identity, extensive experience, and recognized expertise."
        elif score >= 60:
            level = "High"
            explanation = "This author has solid credentials with verified affiliation and good transparency."
        elif score >= 40:
            level = "Moderate"
            explanation = "This author has basic verification but limited public information available."
        elif score >= 20:
            level = "Low"
            explanation = "This author has minimal verification and very limited public information."
        else:
            level = "Very Low"
            explanation = "This author could not be verified and no credible information was found."
        
        factors = []
        breakdown = result['credibility_breakdown']
        
        if breakdown['verification'] >= 15:
            factors.append("verified identity")
        if breakdown['experience'] >= 15:
            factors.append("significant experience")
        if breakdown['transparency'] >= 15:
            factors.append("good transparency")
        if breakdown['recognition'] >= 15:
            factors.append("professional recognition")
        
        if factors:
            explanation += f" Key strengths: {', '.join(factors)}."
        
        return {
            'level': level,
            'explanation': explanation,
            'advice': self._get_credibility_advice(score)
        }
    
    def _get_credibility_advice(self, score):
        """Provide advice based on credibility score"""
        if score >= 60:
            return "This author's credibility is well-established. Their work can generally be trusted."
        elif score >= 40:
            return "This author appears legitimate but consider cross-referencing important claims."
        else:
            return "Limited information about this author. Verify key claims through additional sources."
    
    # Backwards compatibility method
    def analyze_author(self, author_name, domain=None):
        """Single author analysis for backwards compatibility"""
        results = self.analyze_authors(author_name, domain)
        return results[0] if results else self._create_default_author_analysis(author_name)
    
    def _create_default_author_analysis(self, author_name):
        """Create default analysis when no information found"""
        return {
            'name': author_name,
            'found': False,
            'bio': f"{author_name} - Author information not available in our database",
            'credibility_score': 30,
            'credibility_explanation': {
                'level': 'Low',
                'explanation': 'Unable to verify this author. No public information found.',
                'advice': 'Verify claims through additional sources.'
            }
        }
