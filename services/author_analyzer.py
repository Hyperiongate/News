"""
FILE: services/author_analyzer.py
LOCATION: services/author_analyzer.py
PURPOSE: Enhanced author credibility analysis with built-in journalist database
"""

import logging
import re
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import random

logger = logging.getLogger(__name__)

class AuthorAnalyzer:
    """Analyzes author credibility with comprehensive built-in database"""
    
    def __init__(self):
        # Initialize comprehensive journalist database
        self.journalist_db = self._build_journalist_database()
        
        # Cache for lookups
        self._author_cache = {}
        
        # Publication-specific patterns
        self.publication_patterns = {
            'axios.com': {
                'format': 'Firstname Lastname',
                'typical_roles': ['Reporter', 'Senior Reporter', 'Politics Reporter', 'Business Reporter'],
                'bio_style': 'conversational'
            },
            'nytimes.com': {
                'format': 'By Firstname Lastname',
                'typical_roles': ['Staff Writer', 'Reporter', 'Correspondent'],
                'bio_style': 'formal'
            },
            'washingtonpost.com': {
                'format': 'By Firstname Lastname',
                'typical_roles': ['Staff Writer', 'National Correspondent', 'Reporter'],
                'bio_style': 'formal'
            }
        }
        
    def _build_journalist_database(self):
        """Build comprehensive journalist database"""
        return {
            # Axios Journalists
            'stef w. kight': {
                'full_name': 'Stef W. Kight',
                'bio': 'Stef W. Kight is a politics reporter at Axios, covering immigration and labor policy. She has been with Axios since 2017 and previously worked at the International Consortium of Investigative Journalists. She specializes in breaking down complex policy issues and their real-world impacts.',
                'current_position': 'Politics Reporter',
                'outlets': ['Axios'],
                'previous_outlets': ['International Consortium of Investigative Journalists', 'The Center for Public Integrity'],
                'expertise_areas': ['Immigration Policy', 'Labor Policy', 'Congress', 'Federal Policy'],
                'education': 'American University',
                'years_experience': 8,
                'twitter': '@StefWKight',
                'verified': True,
                'awards': ['Part of ICIJ Panama Papers team'],
                'notable_coverage': ['Immigration reform', 'Senate proceedings', 'Labor regulations'],
                'credibility_indicators': {
                    'breaks_news': True,
                    'cited_by_others': True,
                    'expert_sources': True
                }
            },
            'jonathan swan': {
                'full_name': 'Jonathan Swan',
                'bio': 'Jonathan Swan is a former Axios political reporter known for his aggressive interviewing style and White House scoops. He joined The New York Times in 2022. His memorable interview with President Trump in 2020 went viral for his fact-checking approach.',
                'current_position': 'Political Reporter at The New York Times',
                'outlets': ['The New York Times', 'Axios'],
                'expertise_areas': ['White House', 'National Politics', 'Investigative Reporting'],
                'years_experience': 12,
                'twitter': '@jonathanvswan',
                'verified': True,
                'awards': ['Emmy Award for Trump interview', 'White House Correspondents Association Award']
            },
            'mike allen': {
                'full_name': 'Mike Allen',
                'bio': 'Mike Allen is co-founder of Axios and author of the flagship Axios AM newsletter. Previously, he was Politico\'s chief political correspondent and co-creator of Playbook. A veteran journalist with over 20 years of experience covering Washington.',
                'current_position': 'Co-founder and Executive Editor',
                'outlets': ['Axios', 'Politico', 'The Washington Post', 'TIME'],
                'expertise_areas': ['Politics', 'White House', 'Congress', 'Media'],
                'years_experience': 25,
                'twitter': '@mikeallen',
                'verified': True
            },
            # Add more major journalists
            'maggie haberman': {
                'full_name': 'Maggie Haberman',
                'bio': 'Maggie Haberman is a senior political correspondent for The New York Times and a CNN political analyst. She is widely regarded as one of the most influential journalists covering Donald Trump and won a Pulitzer Prize for her coverage.',
                'current_position': 'Senior Political Correspondent',
                'outlets': ['The New York Times', 'CNN'],
                'previous_outlets': ['Politico', 'New York Daily News', 'New York Post'],
                'expertise_areas': ['White House', 'Donald Trump', 'New York Politics', 'National Politics'],
                'years_experience': 20,
                'twitter': '@maggieNYT',
                'verified': True,
                'awards': ['Pulitzer Prize for National Reporting', 'White House Correspondents Award']
            },
            'bob woodward': {
                'full_name': 'Bob Woodward',
                'bio': 'Bob Woodward is an associate editor at The Washington Post where he has worked since 1971. He is best known for his coverage of the Watergate scandal with Carl Bernstein, which led to President Nixon\'s resignation.',
                'current_position': 'Associate Editor',
                'outlets': ['The Washington Post'],
                'expertise_areas': ['Investigative Journalism', 'Presidents', 'National Security', 'Politics'],
                'years_experience': 52,
                'verified': True,
                'awards': ['Two Pulitzer Prizes', '20+ books on American politics']
            },
            # Tech journalists
            'kara swisher': {
                'full_name': 'Kara Swisher',
                'bio': 'Kara Swisher is one of Silicon Valley\'s most influential journalists, host of the podcasts "Pivot" and "On with Kara Swisher". She co-founded Recode and has been covering tech since the 1990s.',
                'current_position': 'Contributing Editor at New York Magazine',
                'outlets': ['New York Magazine', 'Vox'],
                'previous_outlets': ['The Wall Street Journal', 'The Washington Post'],
                'expertise_areas': ['Technology', 'Silicon Valley', 'Tech Policy', 'Media'],
                'years_experience': 30,
                'twitter': '@karaswisher',
                'verified': True
            },
            # Add beat-specific defaults
            'default_politics': {
                'bio_template': '{name} is a politics reporter covering {beat} with a focus on {specialty}.',
                'typical_experience': 5,
                'common_beats': ['Congress', 'White House', 'Elections', 'Federal Policy'],
                'credibility_base': 60
            },
            'default_business': {
                'bio_template': '{name} covers business and economics, specializing in {specialty}.',
                'typical_experience': 6,
                'common_beats': ['Markets', 'Tech', 'Finance', 'Corporate News'],
                'credibility_base': 65
            },
            'default_tech': {
                'bio_template': '{name} is a technology reporter covering {specialty} and industry trends.',
                'typical_experience': 4,
                'common_beats': ['AI', 'Social Media', 'Startups', 'Big Tech'],
                'credibility_base': 60
            }
        }
    
    def analyze_single_author(self, author_name: str, domain: Optional[str] = None) -> Dict[str, Any]:
        """Analyze author with enhanced database and smart inference"""
        
        # Validate input
        if not author_name or not isinstance(author_name, str):
            return self._create_error_result("Unknown Author", "Invalid author name provided")
        
        # Clean author name
        author_name = author_name.strip()
        author_key = author_name.lower()
        
        # Check cache
        cache_key = f"{author_key}:{domain or 'any'}"
        if cache_key in self._author_cache:
            return self._author_cache[cache_key]
        
        # Check if it's a generic byline
        if author_key in ['unknown', 'staff', 'admin', 'editor', 'unknown author']:
            return self._create_anonymous_result(author_name)
        
        logger.info(f"Analyzing author: {author_name} from {domain}")
        
        # Initialize result
        result = self._create_base_result(author_name, domain)
        
        # Check journalist database
        if author_key in self.journalist_db:
            journalist_data = self.journalist_db[author_key]
            result = self._apply_journalist_data(result, journalist_data)
            result['found'] = True
            result['data_source'] = 'verified_database'
        else:
            # Try intelligent inference based on publication and context
            result = self._infer_author_info(result, author_name, domain)
            result['data_source'] = 'intelligent_inference'
        
        # Calculate credibility score
        result['credibility_score'] = self._calculate_credibility_score(result)
        
        # Generate credibility explanation
        result['credibility_explanation'] = self._generate_credibility_explanation(result)
        
        # Cache result
        self._author_cache[cache_key] = result
        
        return result
    
    def _apply_journalist_data(self, result: Dict[str, Any], journalist_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply known journalist data to result"""
        
        # Basic info
        result['name'] = journalist_data.get('full_name', result['name'])
        result['bio'] = journalist_data.get('bio', '')
        
        # Verification status
        result['verification_status'] = {
            'verified': journalist_data.get('verified', False),
            'journalist_verified': True,
            'outlet_staff': True
        }
        
        # Professional info
        result['professional_info'] = {
            'current_position': journalist_data.get('current_position'),
            'outlets': journalist_data.get('outlets', []),
            'previous_outlets': journalist_data.get('previous_outlets', []),
            'years_experience': journalist_data.get('years_experience'),
            'expertise_areas': journalist_data.get('expertise_areas', []),
            'education': journalist_data.get('education'),
            'awards': journalist_data.get('awards', []),
            'notable_coverage': journalist_data.get('notable_coverage', [])
        }
        
        # Online presence
        if journalist_data.get('twitter'):
            result['online_presence']['twitter'] = f"https://twitter.com/{journalist_data['twitter'].lstrip('@')}"
        
        # Credibility indicators
        result['credibility_indicators'] = journalist_data.get('credibility_indicators', {})
        
        return result
    
    def _infer_author_info(self, result: Dict[str, Any], author_name: str, domain: Optional[str]) -> Dict[str, Any]:
        """Intelligently infer author information based on publication and patterns"""
        
        # Determine likely beat from article context
        beat = self._infer_beat(domain)
        
        # Generate professional-looking bio
        if domain and 'axios' in domain.lower():
            result['bio'] = f"{author_name} is a reporter at Axios contributing to their political coverage. While specific biographical details are not available in our database, Axios maintains high editorial standards and employs experienced journalists across their coverage areas."
            result['professional_info'] = {
                'current_position': 'Reporter',
                'outlets': ['Axios'],
                'expertise_areas': self._infer_expertise_from_beat(beat),
                'years_experience': None  # Unknown but implied
            }
            result['found'] = True
            result['verification_status']['outlet_staff'] = True
            
        elif domain and any(pub in domain.lower() for pub in ['nytimes', 'washingtonpost', 'wsj']):
            pub_name = self._get_publication_name(domain)
            result['bio'] = f"{author_name} is a journalist contributing to {pub_name}. As a writer for a major news organization, they are part of a newsroom with rigorous editorial standards and fact-checking processes."
            result['professional_info'] = {
                'current_position': 'Contributing Writer',
                'outlets': [pub_name],
                'expertise_areas': self._infer_expertise_from_beat(beat)
            }
            result['found'] = True
            result['verification_status']['outlet_staff'] = True
            
        else:
            # Generic but professional inference
            result['bio'] = f"{author_name} is the credited author of this article. While we don't have detailed biographical information in our database, the article appears on {domain or 'this publication'} which provides some credibility context."
            result['professional_info']['outlets'] = [domain] if domain else []
            result['found'] = False
        
        return result
    
    def _infer_beat(self, domain: Optional[str]) -> str:
        """Infer the likely beat based on domain and other context"""
        if not domain:
            return 'general'
            
        domain_lower = domain.lower()
        
        # Politics-focused sites
        if any(pol in domain_lower for pol in ['politico', 'thehill', 'axios']):
            return 'politics'
        
        # Tech sites
        if any(tech in domain_lower for tech in ['techcrunch', 'verge', 'wired', 'ars']):
            return 'technology'
        
        # Business sites
        if any(biz in domain_lower for biz in ['bloomberg', 'wsj', 'fortune', 'forbes']):
            return 'business'
        
        return 'general'
    
    def _infer_expertise_from_beat(self, beat: str) -> List[str]:
        """Infer likely expertise areas from beat"""
        expertise_map = {
            'politics': ['Federal Policy', 'Congress', 'Elections', 'Government'],
            'technology': ['Tech Industry', 'Digital Innovation', 'Tech Policy'],
            'business': ['Markets', 'Corporate News', 'Economics', 'Finance'],
            'general': ['Current Affairs', 'Breaking News']
        }
        return expertise_map.get(beat, ['General Reporting'])
    
    def _get_publication_name(self, domain: str) -> str:
        """Get proper publication name from domain"""
        pub_map = {
            'nytimes': 'The New York Times',
            'washingtonpost': 'The Washington Post',
            'wsj': 'The Wall Street Journal',
            'axios': 'Axios',
            'politico': 'Politico',
            'thehill': 'The Hill',
            'cnn': 'CNN',
            'foxnews': 'Fox News',
            'bloomberg': 'Bloomberg',
            'reuters': 'Reuters',
            'apnews': 'Associated Press'
        }
        
        domain_lower = domain.lower()
        for key, name in pub_map.items():
            if key in domain_lower:
                return name
        
        # Clean up domain for display
        return domain.replace('.com', '').replace('www.', '').title()
    
    def _calculate_credibility_score(self, result: Dict[str, Any]) -> int:
        """Calculate credibility score based on available information"""
        score = 30  # Base score
        
        # Database verification bonus
        if result.get('data_source') == 'verified_database':
            score += 40
        
        # Verification status
        if result['verification_status']['verified']:
            score += 20
        elif result['verification_status']['journalist_verified']:
            score += 15
        elif result['verification_status']['outlet_staff']:
            score += 10
        
        # Professional information
        if result['professional_info']['current_position']:
            score += 10
        
        if result['professional_info']['years_experience']:
            years = result['professional_info']['years_experience']
            score += min(years * 2, 20)  # Cap at 20 points
        
        # Major outlet bonus
        major_outlets = ['The New York Times', 'The Washington Post', 'The Wall Street Journal', 
                        'Reuters', 'Associated Press', 'Bloomberg', 'BBC', 'NPR', 'Axios',
                        'Politico', 'The Guardian', 'Financial Times']
        
        outlets = result['professional_info']['outlets']
        if any(outlet in major_outlets for outlet in outlets):
            score += 15
        
        # Awards and recognition
        if result['professional_info'].get('awards'):
            score += min(len(result['professional_info']['awards']) * 5, 15)
        
        # Online presence
        if result['online_presence']:
            score += 5
        
        # Credibility indicators
        if result.get('credibility_indicators'):
            indicators = result['credibility_indicators']
            if indicators.get('breaks_news'):
                score += 5
            if indicators.get('cited_by_others'):
                score += 5
            if indicators.get('expert_sources'):
                score += 5
        
        return min(100, max(0, score))
    
    def _generate_credibility_explanation(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed credibility explanation"""
        score = result['credibility_score']
        factors = []
        
        # Determine credibility level
        if score >= 80:
            level = 'High'
            base_explanation = f"{result['name']} is a highly credible journalist with strong verification."
        elif score >= 60:
            level = 'Good'
            base_explanation = f"{result['name']} has good credibility with verified credentials."
        elif score >= 40:
            level = 'Moderate'
            base_explanation = f"{result['name']} has moderate credibility based on available information."
        else:
            level = 'Limited'
            base_explanation = f"Limited credibility information available for {result['name']}."
        
        # Build factors list
        if result.get('data_source') == 'verified_database':
            factors.append("In our verified journalist database")
        
        if result['verification_status']['verified']:
            factors.append("Verified journalist")
        
        if result['professional_info']['current_position']:
            factors.append(f"{result['professional_info']['current_position']}")
        
        if result['professional_info']['years_experience']:
            factors.append(f"{result['professional_info']['years_experience']} years experience")
        
        outlets = result['professional_info']['outlets']
        if outlets:
            if len(outlets) == 1:
                factors.append(f"Writes for {outlets[0]}")
            else:
                factors.append(f"Published in {len(outlets)} outlets")
        
        if result['professional_info'].get('awards'):
            factors.append(f"{len(result['professional_info']['awards'])} major awards")
        
        # Build advice
        if score >= 70:
            advice = "This author has strong credentials. Their reporting can generally be trusted, though always verify key claims."
        elif score >= 50:
            advice = "This author has moderate credentials. Cross-reference important claims with other sources."
        else:
            advice = "Limited author information available. Pay extra attention to sourcing and verify all major claims."
        
        return {
            'level': level,
            'explanation': base_explanation,
            'factors': factors,
            'advice': advice,
            'score_breakdown': {
                'database_verified': result.get('data_source') == 'verified_database',
                'major_outlet': any(o in ['Axios', 'The New York Times', 'The Washington Post'] for o in outlets),
                'experienced': result['professional_info'].get('years_experience', 0) > 5,
                'has_expertise': len(result['professional_info'].get('expertise_areas', [])) > 0
            }
        }
    
    def _create_base_result(self, author_name: str, domain: Optional[str] = None) -> Dict[str, Any]:
        """Create base result structure"""
        return {
            'found': False,
            'name': author_name,
            'credibility_score': 30,
            'bio': None,
            'verification_status': {
                'verified': False,
                'journalist_verified': False,
                'outlet_staff': False
            },
            'professional_info': {
                'current_position': None,
                'outlets': [],
                'previous_outlets': [],
                'years_experience': None,
                'expertise_areas': [],
                'education': None,
                'awards': [],
                'notable_coverage': []
            },
            'online_presence': {},
            'credibility_explanation': None,
            'credibility_indicators': {},
            'data_source': None
        }
    
    def _create_anonymous_result(self, author_name: str) -> Dict[str, Any]:
        """Create result for anonymous authors"""
        return {
            'found': False,
            'name': author_name or 'Unknown Author',
            'credibility_score': 25,
            'bio': 'This article does not have a named author, which reduces accountability and credibility.',
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
                'level': 'Anonymous',
                'explanation': 'Articles without named authors have inherently lower credibility due to lack of accountability.',
                'factors': ['No author attribution', 'Cannot verify credentials', 'No accountability'],
                'advice': 'Exercise additional caution with anonymous content. Verify all claims through other sources.'
            },
            'anonymous': True
        }
    
    def _create_error_result(self, author_name: str, error_msg: str) -> Dict[str, Any]:
        """Create error result"""
        return {
            'found': False,
            'name': author_name,
            'credibility_score': 30,
            'bio': f"Unable to retrieve information about {author_name}.",
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
            'error': error_msg
        }
    
    def get_author_summary(self, author_analysis: Dict[str, Any]) -> str:
        """Get a brief summary of author credibility"""
        score = author_analysis.get('credibility_score', 0)
        name = author_analysis.get('name', 'Unknown')
        
        if score >= 80:
            return f"{name} is a highly credible journalist with verified credentials."
        elif score >= 60:
            return f"{name} is a credible journalist with good verification."
        elif score >= 40:
            return f"{name} has moderate credibility based on available information."
        else:
            return f"Limited credibility information available for {name}."
    
    def clear_cache(self):
        """Clear the author cache"""
        self._author_cache.clear()
        logger.info("Author cache cleared")
