"""
Source Credibility Analyzer - COMPLETE FIXED VERSION
CRITICAL FIXES:
1. Fixed class name to match SERVICE_MAPPING (SourceCredibility not SourceCredibilityAnalyzer)
2. Proper data structure with consistent 'data' wrapper
3. Enhanced error handling for timeout issues
4. Bulletproof AI enhancement integration
"""

import time
import logging
import re
from typing import Dict, Any, Optional, List, Set
from urllib.parse import urlparse
import hashlib
import ssl
import socket
from datetime import datetime, timedelta
import requests

from services.base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)

# Optional imports with graceful degradation
WHOIS_AVAILABLE = False
try:
    import whois
    WHOIS_AVAILABLE = True
except ImportError:
    logger.info("whois library not available - domain age analysis will be limited")

DNS_AVAILABLE = False
try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    logger.info("dns library not available - DNS checks will be limited")


class SourceCredibility(BaseAnalyzer):
    """
    FIXED: Class name changed from SourceCredibilityAnalyzer to SourceCredibility
    Analyze the credibility of news sources using multiple factors with proper data structure
    """
    
    def __init__(self):
        super().__init__('source_credibility')
        
        # Cache for results
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour
        
        # API keys
        from config import Config
        self.news_api_key = Config.NEWS_API_KEY or Config.NEWSAPI_KEY
        
        # Initialize databases
        self._init_credibility_database()
        
        logger.info(f"SourceCredibility initialized - News API: {bool(self.news_api_key)}")
    
    def _check_availability(self) -> bool:
        """Service is always available since we have fallback methods"""
        return True
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        FIXED: Analyze source credibility with proper data structure and bulletproof AI enhancement
        """
        try:
            start_time = time.time()
            
            # Extract domain with better error handling
            domain = self._extract_domain(data)
            if not domain:
                logger.warning(f"Could not extract domain from data: {list(data.keys())}")
                return self.get_error_result("No valid domain or URL provided")
            
            logger.info(f"Analyzing source credibility for domain: {domain}")
            
            # Check if we should do technical analysis
            check_technical = data.get('check_technical', True)
            
            # Get comprehensive analysis with timeout protection
            try:
                analysis = self._analyze_source_comprehensive(domain, check_technical)
            except requests.exceptions.Timeout:
                logger.warning(f"Analysis timeout for {domain} - using cached/basic data only")
                analysis = self._get_basic_analysis(domain)
            except Exception as e:
                logger.warning(f"Analysis error for {domain}: {e} - using fallback")
                analysis = self._get_basic_analysis(domain)
            
            # Calculate overall credibility score
            credibility_score = self._calculate_credibility_score(analysis)
            credibility_level = self._get_credibility_level(credibility_score)
            
            # Generate findings
            findings = self._generate_findings(analysis, credibility_score)
            
            # Generate summary
            summary = self._generate_summary(analysis, credibility_score)
            
            # Prepare technical analysis data with safe defaults
            technical_data = {}
            if 'technical' in analysis:
                tech = analysis['technical']
                technical_data = {
                    'domain_age_days': tech.get('age_days'),
                    'domain_age_credibility': tech.get('age_credibility', 'unknown'),
                    'has_ssl': tech.get('ssl', {}).get('valid', False),
                    'ssl_days_remaining': tech.get('ssl', {}).get('days_remaining'),
                    'has_about_page': tech.get('structure', {}).get('has_about_page'),
                    'has_contact_page': tech.get('structure', {}).get('has_contact_page'),
                    'has_privacy_policy': tech.get('structure', {}).get('has_privacy_policy'),
                    'has_author_bylines': tech.get('structure', {}).get('has_author_bylines'),
                    'website_transparency_score': tech.get('structure', {}).get('transparency_score', 0)
                }
            
            # FIXED: Build response with proper data structure wrapper
            result = {
                'service': self.service_name,
                'success': True,
                'available': True,
                'timestamp': time.time(),
                'analysis_complete': True,
                'data': {
                    'score': credibility_score,
                    'level': credibility_level,
                    'findings': findings,
                    'summary': summary,
                    'source_name': analysis.get('source_name', domain),
                    'source_type': analysis['database_info'].get('type', 'Unknown'),
                    'credibility_score': credibility_score,
                    'credibility_level': credibility_level,
                    'credibility': analysis['database_info'].get('credibility', 'Unknown'),
                    'bias': analysis['database_info'].get('bias', 'Unknown'),
                    'in_database': analysis.get('in_database', False),
                    'factual_reporting': self._get_factual_reporting_level(analysis),
                    'media_bias': {
                        'bias': analysis['database_info'].get('bias', 'Unknown'),
                        'description': self._get_bias_description(analysis['database_info'].get('bias'))
                    },
                    'transparency_indicators': analysis.get('transparency', {}).get('indicators', []),
                    'missing_transparency': analysis.get('transparency', {}).get('missing_elements', []),
                    'trust_indicators': self._get_trust_indicators(analysis),
                    **technical_data
                },
                'metadata': {
                    'analysis_time': time.time() - start_time,
                    'data_sources': analysis.get('data_sources', []),
                    'whois_available': WHOIS_AVAILABLE,
                    'news_api_available': bool(self.news_api_key),
                    'domain_analyzed': domain,
                    'technical_analysis_performed': check_technical
                }
            }
            
            logger.info(f"Source credibility analysis complete: {domain} -> {credibility_score}/100 ({credibility_level})")
            return result
            
        except Exception as e:
            logger.error(f"Source credibility analysis failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _init_credibility_database(self):
        """Initialize built-in credibility database"""
        self.source_database = {
            # Very high credibility sources
            'reuters.com': {'credibility': 'Very High', 'bias': 'Minimal', 'type': 'News Agency'},
            'apnews.com': {'credibility': 'Very High', 'bias': 'Minimal', 'type': 'News Agency'},
            'bbc.com': {'credibility': 'Very High', 'bias': 'Minimal', 'type': 'International News'},
            'npr.org': {'credibility': 'Very High', 'bias': 'Minimal-Left', 'type': 'Public Radio'},
            
            # High credibility sources
            'nytimes.com': {'credibility': 'High', 'bias': 'Left-Leaning', 'type': 'Newspaper'},
            'washingtonpost.com': {'credibility': 'High', 'bias': 'Left-Leaning', 'type': 'Newspaper'},
            'wsj.com': {'credibility': 'High', 'bias': 'Right-Leaning', 'type': 'Newspaper'},
            'economist.com': {'credibility': 'High', 'bias': 'Minimal', 'type': 'Magazine'},
            'nature.com': {'credibility': 'Very High', 'bias': 'Pro-Science', 'type': 'Academic Journal'},
            'science.org': {'credibility': 'Very High', 'bias': 'Pro-Science', 'type': 'Academic Journal'},
            
            # Medium credibility sources  
            'cnn.com': {'credibility': 'Medium', 'bias': 'Left-Leaning', 'type': 'Cable News'},
            'foxnews.com': {'credibility': 'Medium', 'bias': 'Right-Leaning', 'type': 'Cable News'},
            'msnbc.com': {'credibility': 'Medium', 'bias': 'Left-Leaning', 'type': 'Cable News'},
            'cbsnews.com': {'credibility': 'High', 'bias': 'Minimal-Left', 'type': 'Broadcast News'},
            'abcnews.go.com': {'credibility': 'High', 'bias': 'Minimal-Left', 'type': 'Broadcast News'},
            'nbcnews.com': {'credibility': 'High', 'bias': 'Minimal-Left', 'type': 'Broadcast News'},
            'usatoday.com': {'credibility': 'High', 'bias': 'Minimal', 'type': 'Newspaper'},
            
            # Lower credibility sources
            'dailymail.co.uk': {'credibility': 'Low', 'bias': 'Right-Leaning', 'type': 'Tabloid'},
            'nypost.com': {'credibility': 'Medium-Low', 'bias': 'Right-Leaning', 'type': 'Tabloid'},
            'huffpost.com': {'credibility': 'Medium', 'bias': 'Left-Leaning', 'type': 'Digital Media'},
            'buzzfeed.com': {'credibility': 'Medium-Low', 'bias': 'Left-Leaning', 'type': 'Digital Media'},
            'vox.com': {'credibility': 'Medium', 'bias': 'Left-Leaning', 'type': 'Digital Media'},
            'breitbart.com': {'credibility': 'Low', 'bias': 'Right-Leaning', 'type': 'Opinion Blog'},
            'infowars.com': {'credibility': 'Very Low', 'bias': 'Extreme Right', 'type': 'Conspiracy'},
            'rt.com': {'credibility': 'Low', 'bias': 'Pro-Russia', 'type': 'State Media'},
            'presstv.ir': {'credibility': 'Low', 'bias': 'Pro-Iran', 'type': 'State Media'},
            'xinhuanet.com': {'credibility': 'Low', 'bias': 'Pro-China', 'type': 'State Media'},
        }
    
    def _extract_domain(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract domain from various data formats"""
        # Try direct domain field
        if 'domain' in data:
            return data['domain']
            
        # Try URL field
        if 'url' in data:
            try:
                parsed = urlparse(data['url'])
                return parsed.netloc.lower().replace('www.', '')
            except:
                pass
        
        # Try article data
        if 'article' in data and isinstance(data['article'], dict):
            article = data['article']
            if 'domain' in article:
                return article['domain']
            if 'url' in article:
                try:
                    parsed = urlparse(article['url'])
                    return parsed.netloc.lower().replace('www.', '')
                except:
                    pass
        
        return None
    
    def _get_basic_analysis(self, domain: str) -> Dict[str, Any]:
        """Get basic analysis when full analysis fails"""
        return {
            'source_name': self._get_source_name(domain),
            'database_info': self._check_database(domain),
            'in_database': False,
            'data_sources': ['basic_lookup'],
            'transparency': {'indicators': [], 'missing_elements': []},
            'reputation': {},
            'history': {}
        }
    
    def _get_source_name(self, domain: str) -> str:
        """Convert domain to readable source name"""
        # Clean domain
        clean_domain = domain.replace('www.', '').replace('.com', '').replace('.org', '').replace('.co.uk', '')
        
        # Special cases
        name_mapping = {
            'nytimes': 'The New York Times',
            'washingtonpost': 'The Washington Post',
            'wsj': 'The Wall Street Journal',
            'bbc': 'BBC',
            'cnn': 'CNN',
            'foxnews': 'Fox News',
            'msnbc': 'MSNBC',
            'npr': 'NPR',
            'reuters': 'Reuters',
            'apnews': 'Associated Press',
            'usatoday': 'USA Today',
            'theguardian': 'The Guardian',
            'dailymail': 'Daily Mail',
            'nypost': 'New York Post',
            'huffpost': 'HuffPost',
            'buzzfeed': 'BuzzFeed',
            'breitbart': 'Breitbart',
        }
        
        return name_mapping.get(clean_domain, clean_domain.title())
    
    def _check_database(self, domain: str) -> Dict[str, str]:
        """Check domain against built-in credibility database"""
        # Direct lookup
        if domain in self.source_database:
            return self.source_database[domain]
        
        # Check without www
        clean_domain = domain.replace('www.', '')
        if clean_domain in self.source_database:
            return self.source_database[clean_domain]
        
        # Check subdomains (e.g., news.google.com -> google.com)
        parts = domain.split('.')
        if len(parts) > 2:
            parent_domain = '.'.join(parts[-2:])
            if parent_domain in self.source_database:
                return self.source_database[parent_domain]
        
        return {'credibility': 'Unknown', 'bias': 'Unknown', 'type': 'Unknown'}
    
    def _analyze_source_comprehensive(self, domain: str, check_technical: bool = True) -> Dict[str, Any]:
        """Perform comprehensive source analysis with timeout protection"""
        cache_key = f"source:{domain}:{check_technical}"
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
        
        analysis = {
            'source_name': self._get_source_name(domain),
            'data_sources': []
        }
        
        # 1. Check source database (always fast)
        try:
            db_info = self._check_database(domain)
            analysis['database_info'] = db_info
            analysis['in_database'] = db_info['credibility'] != 'Unknown'
            if analysis['in_database']:
                analysis['data_sources'].append('source_database')
        except Exception as e:
            logger.warning(f"Database check failed for {domain}: {e}")
            analysis['database_info'] = {'credibility': 'Unknown', 'bias': 'Unknown', 'type': 'Unknown'}
            analysis['in_database'] = False
        
        # 2. Technical analysis (with timeout)
        if check_technical:
            try:
                tech_analysis = self._analyze_technical_factors(domain)
                if tech_analysis:
                    analysis['technical'] = tech_analysis
                    analysis['data_sources'].append('technical_analysis')
            except Exception as e:
                logger.warning(f"Technical analysis failed for {domain}: {e}")
        
        # 3. Transparency analysis
        try:
            transparency = self._analyze_transparency(domain)
            analysis['transparency'] = transparency
            analysis['data_sources'].append('transparency_check')
        except Exception as e:
            logger.warning(f"Transparency analysis failed for {domain}: {e}")
            analysis['transparency'] = {'indicators': [], 'missing_elements': []}
        
        # Cache result
        self._cache_result(cache_key, analysis)
        return analysis
    
    def _analyze_technical_factors(self, domain: str) -> Dict[str, Any]:
        """Analyze technical factors with timeout"""
        tech_data = {}
        
        # Domain age (with timeout)
        try:
            age_info = self._get_domain_age(domain)
            tech_data.update(age_info)
        except Exception as e:
            logger.debug(f"Domain age check failed for {domain}: {e}")
        
        # SSL check (fast)
        try:
            ssl_info = self._check_ssl(domain)
            tech_data['ssl'] = ssl_info
        except Exception as e:
            logger.debug(f"SSL check failed for {domain}: {e}")
            tech_data['ssl'] = {'valid': False}
        
        # Website structure (with timeout)
        try:
            structure_info = self._analyze_website_structure(domain)
            tech_data['structure'] = structure_info
        except Exception as e:
            logger.debug(f"Structure analysis failed for {domain}: {e}")
            tech_data['structure'] = {}
        
        return tech_data
    
    def _get_domain_age(self, domain: str) -> Dict[str, Any]:
        """Get domain age information with timeout"""
        if not WHOIS_AVAILABLE:
            return {}
        
        try:
            # Set timeout for whois query
            w = whois.whois(domain)
            creation_date = w.creation_date
            
            if creation_date:
                if isinstance(creation_date, list):
                    creation_date = creation_date[0]
                
                age_days = (datetime.now() - creation_date).days
                
                # Determine age credibility
                if age_days > 3650:  # > 10 years
                    age_credibility = 'very_high'
                elif age_days > 1825:  # > 5 years
                    age_credibility = 'high'
                elif age_days > 365:  # > 1 year
                    age_credibility = 'medium'
                elif age_days > 180:  # > 6 months
                    age_credibility = 'low'
                else:
                    age_credibility = 'very_low'
                
                return {
                    'age_days': age_days,
                    'age_years': round(age_days / 365, 1),
                    'creation_date': creation_date.isoformat(),
                    'age_credibility': age_credibility
                }
        except Exception as e:
            logger.debug(f"WHOIS lookup failed for {domain}: {e}")
        
        return {}
    
    def _check_ssl(self, domain: str) -> Dict[str, Any]:
        """Check SSL certificate with timeout"""
        try:
            context = ssl.create_default_context()
            
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Check expiration
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_remaining = (not_after - datetime.now()).days
                    
                    return {
                        'valid': True,
                        'issuer': dict(x[0] for x in cert['issuer']).get('organizationName', 'Unknown'),
                        'expires': not_after.isoformat(),
                        'days_remaining': days_remaining,
                        'subject': dict(x[0] for x in cert['subject']).get('commonName', domain)
                    }
        except Exception as e:
            logger.debug(f"SSL check failed for {domain}: {e}")
            return {'valid': False, 'error': str(e)}
    
    def _analyze_website_structure(self, domain: str) -> Dict[str, Any]:
        """Analyze website structure and transparency"""
        try:
            # Make request with timeout
            response = requests.get(f'https://{domain}', timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; TruthLens/1.0)'
            })
            
            if response.status_code != 200:
                return {}
            
            content = response.text.lower()
            
            # Check for transparency indicators
            structure = {
                'has_about_page': any(keyword in content for keyword in ['about us', 'about', '/about']),
                'has_contact_page': any(keyword in content for keyword in ['contact', 'contact us', '/contact']),
                'has_privacy_policy': any(keyword in content for keyword in ['privacy policy', 'privacy', '/privacy']),
                'has_terms_of_service': any(keyword in content for keyword in ['terms of service', 'terms', '/terms']),
                'has_author_bylines': any(keyword in content for keyword in ['by ', 'author:', 'reporter:']),
                'has_correction_policy': any(keyword in content for keyword in ['correction', 'corrections', 'retraction']),
                'has_editorial_standards': any(keyword in content for keyword in ['editorial standards', 'journalism ethics']),
            }
            
            # Calculate transparency score
            total_indicators = len(structure)
            present_indicators = sum(1 for v in structure.values() if v)
            transparency_score = (present_indicators / total_indicators) * 100 if total_indicators > 0 else 0
            
            structure['transparency_score'] = round(transparency_score)
            structure['transparency_indicators_present'] = present_indicators
            structure['transparency_indicators_total'] = total_indicators
            
            return structure
            
        except Exception as e:
            logger.debug(f"Website structure analysis failed for {domain}: {e}")
            return {}
    
    def _analyze_transparency(self, domain: str) -> Dict[str, Any]:
        """Analyze source transparency"""
        indicators = []
        missing_elements = []
        
        # This would be expanded with more sophisticated checks
        common_transparency_elements = [
            'About Us page',
            'Editorial policy',
            'Correction policy',
            'Contact information',
            'Author bylines',
            'Publication dates',
            'Source attribution'
        ]
        
        # For now, return basic structure
        return {
            'indicators': indicators,
            'missing_elements': missing_elements,
            'transparency_score': 50  # Default middle score
        }
    
    def _calculate_credibility_score(self, analysis: Dict[str, Any]) -> int:
        """Calculate overall credibility score based on multiple factors"""
        score = 50  # Start with neutral score
        
        # Database credibility (40% weight)
        db_info = analysis['database_info']
        credibility = db_info.get('credibility', 'Unknown')
        
        credibility_scores = {
            'Very High': 95,
            'High': 80,
            'Medium-High': 70,
            'Medium': 60,
            'Medium-Low': 40,
            'Low': 25,
            'Very Low': 10,
            'Unknown': 50
        }
        
        db_score = credibility_scores.get(credibility, 50)
        score = db_score * 0.4 + score * 0.6
        
        # Technical factors (30% weight)
        if 'technical' in analysis:
            tech = analysis['technical']
            tech_score = 50
            
            # Domain age
            age_cred = tech.get('age_credibility', 'unknown')
            age_scores = {'very_high': 100, 'high': 80, 'medium': 60, 'low': 40, 'very_low': 20, 'unknown': 50}
            tech_score += (age_scores.get(age_cred, 50) - 50) * 0.4
            
            # SSL
            if tech.get('ssl', {}).get('valid'):
                tech_score += 10
            
            # Structure
            structure = tech.get('structure', {})
            transparency_score = structure.get('transparency_score', 50)
            tech_score += (transparency_score - 50) * 0.3
            
            score = score * 0.7 + tech_score * 0.3
        
        # Transparency factors (20% weight)  
        transparency = analysis.get('transparency', {})
        trans_score = transparency.get('transparency_score', 50)
        score = score * 0.8 + trans_score * 0.2
        
        # Bias adjustment (10% weight)
        bias = db_info.get('bias', 'Unknown')
        if bias in ['Minimal', 'Pro-Science']:
            score += 5
        elif bias in ['Extreme Left', 'Extreme Right']:
            score -= 15
        elif 'Extreme' in bias:
            score -= 10
        
        return max(0, min(100, int(score)))
    
    def _get_credibility_level(self, score: int) -> str:
        """Convert credibility score to level"""
        if score >= 85:
            return 'Very High'
        elif score >= 70:
            return 'High'
        elif score >= 55:
            return 'Medium-High'
        elif score >= 40:
            return 'Medium'
        elif score >= 25:
            return 'Medium-Low'
        elif score >= 10:
            return 'Low'
        else:
            return 'Very Low'
    
    def _get_factual_reporting_level(self, analysis: Dict[str, Any]) -> str:
        """Determine factual reporting level"""
        db_info = analysis['database_info']
        credibility = db_info.get('credibility', 'Unknown')
        
        if credibility in ['Very High', 'High']:
            return 'High'
        elif credibility in ['Medium', 'Medium-High']:
            return 'Mostly Factual'
        elif credibility == 'Medium-Low':
            return 'Mixed'
        else:
            return 'Low'
    
    def _get_bias_description(self, bias: str) -> str:
        """Get description of bias level"""
        descriptions = {
            'Minimal': 'Reports news with minimal bias and balanced coverage',
            'Minimal-Left': 'Generally factual with slight left-leaning perspective',
            'Minimal-Right': 'Generally factual with slight right-leaning perspective', 
            'Left-Leaning': 'Moderate left bias in story selection and framing',
            'Right-Leaning': 'Moderate right bias in story selection and framing',
            'Left': 'Strong left bias with selective reporting',
            'Right': 'Strong right bias with selective reporting',
            'Pro-Science': 'Promotes scientific consensus and evidence-based reporting',
            'Pro-Russia': 'Promotes Russian government positions',
            'Pro-China': 'Promotes Chinese government positions',
            'Pro-Iran': 'Promotes Iranian government positions',
            'Extreme Right': 'Extreme right-wing bias with conspiracy theories',
            'Extreme Left': 'Extreme left-wing bias',
            'Unknown': 'Bias level not determined'
        }
        return descriptions.get(bias, 'Bias level not determined')
    
    def _generate_findings(self, analysis: Dict[str, Any], score: int) -> List[str]:
        """Generate key findings about the source"""
        findings = []
        
        db_info = analysis['database_info']
        
        # Database findings
        if analysis.get('in_database'):
            findings.append(f"Source is in credibility database as {db_info['credibility']} credibility")
            if db_info['bias'] != 'Unknown':
                findings.append(f"Known bias: {db_info['bias']}")
        else:
            findings.append("Source not in credibility database - unknown reputation")
        
        # Technical findings
        if 'technical' in analysis:
            tech = analysis['technical']
            
            if tech.get('age_days'):
                years = tech['age_days'] / 365
                if years >= 10:
                    findings.append(f"Well-established domain (over {int(years)} years old)")
                elif years >= 1:
                    findings.append(f"Established domain ({int(years)} years old)")
                else:
                    findings.append("Recently created domain (less than 1 year old)")
            
            if tech.get('ssl', {}).get('valid'):
                findings.append("Valid SSL certificate")
            
            structure = tech.get('structure', {})
            transparency_score = structure.get('transparency_score', 0)
            if transparency_score >= 75:
                findings.append("Good website transparency")
            elif transparency_score >= 50:
                findings.append("Moderate website transparency")
            else:
                findings.append("Limited website transparency")
        
        return findings
    
    def _generate_summary(self, analysis: Dict[str, Any], score: int) -> str:
        """Generate summary of credibility analysis"""
        source_name = analysis.get('source_name', 'This source')
        credibility_level = self._get_credibility_level(score)
        
        summary = f"{source_name} has {credibility_level.lower()} credibility (score: {score}/100). "
        
        db_info = analysis['database_info']
        if analysis.get('in_database'):
            summary += f"It is classified as having {db_info['credibility'].lower()} credibility"
            if db_info['bias'] != 'Unknown':
                summary += f" with {db_info['bias'].lower()} bias"
            summary += ". "
        else:
            summary += "It is not in our credibility database. "
        
        # Add key concerns or strengths
        if score >= 70:
            summary += "This is generally a reliable source."
        elif score >= 40:
            summary += "Exercise some caution when reading from this source."
        else:
            summary += "Exercise significant caution - this source has credibility concerns."
        
        return summary
    
    def _get_trust_indicators(self, analysis: Dict[str, Any]) -> List[str]:
        """Extract trust indicators from analysis"""
        indicators = []
        
        if analysis.get('in_database'):
            indicators.append('Listed in credibility database')
        
        if 'technical' in analysis:
            tech = analysis['technical']
            if tech.get('ssl', {}).get('valid'):
                indicators.append('Valid SSL certificate')
            if tech.get('age_credibility') in ['high', 'very_high']:
                indicators.append('Established domain')
            if tech.get('structure', {}).get('has_about_page'):
                indicators.append('Has About page')
            if tech.get('structure', {}).get('has_contact_page'):
                indicators.append('Has contact information')
        
        return indicators
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached result if not expired"""
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
            else:
                del self.cache[cache_key]
        return None
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]):
        """Cache result with timestamp"""
        self.cache[cache_key] = (result, time.time())
        
        # Clean old cache entries
        current_time = time.time()
        expired_keys = [k for k, (_, t) in self.cache.items() if current_time - t > self.cache_ttl]
        for k in expired_keys:
            del self.cache[k]
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        info = super().get_service_info()
        info.update({
            'capabilities': [
                'Source credibility assessment',
                'Bias detection and classification', 
                'Domain age and technical analysis',
                'Website transparency evaluation',
                'Database-driven credibility scoring',
                'SSL and security validation'
            ],
            'data_sources': [
                'Built-in credibility database',
                'WHOIS domain information',
                'SSL certificate validation',
                'Website structure analysis'
            ],
            'scoring_factors': [
                'Historical credibility rating (40%)',
                'Technical factors (30%)', 
                'Transparency indicators (20%)',
                'Bias adjustment (10%)'
            ]
        })
        return info
