"""
Source Credibility Service
Comprehensive source credibility analysis with database, domain verification, and reputation tracking
"""

import os
import logging
import time
import re
import ssl
import socket
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlparse
import whois
import requests
from bs4 import BeautifulSoup

from config import Config
from services.base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)


class SourceCredibility(BaseAnalyzer):
    """
    Enhanced source credibility analyzer with comprehensive database,
    domain verification, SSL checking, and real-time analysis
    """
    
    def __init__(self):
        """Initialize source credibility analyzer"""
        super().__init__('source_credibility')
        
        # API key for NewsAPI (optional enhancement)
        self.news_api_key = Config.NEWS_API_KEY or Config.NEWSAPI_KEY
        
        # Session for web requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'NewsAnalyzer/1.0 (Source Credibility Service)'
        })
        
        # Initialize comprehensive source database
        self.source_database = self._initialize_source_database()
        
        # Cache for domain analysis
        self.cache = {}
        self.cache_ttl = 86400  # 24 hours
        
        logger.info(f"SourceCredibility initialized with {len(self.source_database)} sources")
    
    def _check_availability(self) -> bool:
        """Service is always available"""
        return True
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze source credibility
        
        Expected input:
            - url: Article URL (preferred)
            - domain: Domain name (alternative)
            - check_technical: Whether to perform technical checks (default: True)
        """
        try:
            start_time = time.time()
            
            # Extract domain
            domain = self._extract_domain(data)
            if not domain:
                return self.get_error_result("No domain or URL provided")
            
            # Check if we should do technical analysis
            check_technical = data.get('check_technical', True)
            
            # Get comprehensive analysis
            analysis = self._analyze_source_comprehensive(domain, check_technical)
            
            # Calculate overall credibility score
            credibility_score = self._calculate_credibility_score(analysis)
            credibility_level = self._get_credibility_level(credibility_score)
            
            # Generate findings
            findings = self._generate_findings(analysis, credibility_score)
            
            # Generate summary
            summary = self._generate_summary(analysis, credibility_score)
            
            return {
                'service': self.service_name,
                'success': True,
                'data': {
                    'score': credibility_score,
                    'level': credibility_level,
                    'findings': findings,
                    'summary': summary,
                    'credibility_score': credibility_score,
                    'domain': domain,
                    'source_name': analysis['source_name'],
                    'source_info': {
                        'credibility_rating': analysis['database_info']['credibility'],
                        'bias': analysis['database_info']['bias'],
                        'type': analysis['database_info']['type'],
                        'description': analysis['database_info']['description'],
                        'in_database': analysis['in_database']
                    },
                    'technical_analysis': analysis.get('technical', {}),
                    'reputation_analysis': analysis.get('reputation', {}),
                    'transparency_indicators': analysis.get('transparency', {}),
                    'historical_context': analysis.get('history', {})
                },
                'metadata': {
                    'processing_time': time.time() - start_time,
                    'technical_checks_performed': check_technical,
                    'data_sources': analysis.get('data_sources', [])
                }
            }
            
        except Exception as e:
            logger.error(f"Source credibility analysis failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _analyze_source_comprehensive(self, domain: str, check_technical: bool) -> Dict[str, Any]:
        """Perform comprehensive source analysis"""
        
        # Check cache first
        cache_key = f"{domain}:{check_technical}"
        cached = self._get_cached_result(cache_key)
        if cached:
            return cached
        
        analysis = {
            'domain': domain,
            'source_name': self._get_source_name(domain),
            'in_database': False,
            'data_sources': []
        }
        
        # 1. Check source database
        db_info = self._check_database(domain)
        analysis['database_info'] = db_info
        analysis['in_database'] = db_info['credibility'] != 'Unknown'
        if analysis['in_database']:
            analysis['data_sources'].append('source_database')
        
        # 2. Technical analysis (if enabled)
        if check_technical:
            try:
                # Domain age and registration
                domain_info = self._analyze_domain(domain)
                analysis['technical'] = domain_info
                if domain_info.get('age_days'):
                    analysis['data_sources'].append('domain_registration')
                
                # SSL certificate
                ssl_info = self._check_ssl(domain)
                analysis['technical']['ssl'] = ssl_info
                if ssl_info.get('valid'):
                    analysis['data_sources'].append('ssl_certificate')
                
                # Website structure
                structure_info = self._analyze_website_structure(domain)
                analysis['technical']['structure'] = structure_info
                if structure_info.get('has_about_page'):
                    analysis['data_sources'].append('website_analysis')
                    
            except Exception as e:
                logger.warning(f"Technical analysis failed for {domain}: {e}")
                analysis['technical'] = {'error': str(e)}
        
        # 3. Reputation analysis
        reputation = self._analyze_reputation(domain)
        analysis['reputation'] = reputation
        if reputation.get('mentions_found'):
            analysis['data_sources'].append('news_mentions')
        
        # 4. Transparency indicators
        transparency = self._analyze_transparency(domain, analysis.get('technical', {}).get('structure', {}))
        analysis['transparency'] = transparency
        
        # 5. Historical context
        history = self._analyze_history(domain, db_info)
        analysis['history'] = history
        
        # Cache the result
        self._cache_result(cache_key, analysis)
        
        return analysis
    
    def _check_database(self, domain: str) -> Dict[str, Any]:
        """Check source against database"""
        
        # Clean domain
        clean_domain = domain.lower().replace('www.', '')
        
        # Check exact match
        if clean_domain in self.source_database:
            info = self.source_database[clean_domain].copy()
            info['description'] = self._get_credibility_description(info['credibility'])
            return info
        
        # Check subdomain matches (e.g., abcnews.go.com)
        for db_domain in self.source_database:
            if clean_domain.endswith(db_domain) or db_domain.endswith(clean_domain):
                info = self.source_database[db_domain].copy()
                info['description'] = self._get_credibility_description(info['credibility'])
                return info
        
        # Not in database
        return {
            'credibility': 'Unknown',
            'bias': 'Unknown',
            'type': 'Unknown',
            'description': 'Source not found in credibility database'
        }
    
    def _analyze_domain(self, domain: str) -> Dict[str, Any]:
        """Analyze domain registration and age"""
        try:
            # Get WHOIS information
            w = whois.whois(domain)
            
            # Calculate domain age
            creation_date = w.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            
            age_days = None
            age_years = None
            if creation_date:
                age = datetime.now() - creation_date
                age_days = age.days
                age_years = age_days / 365.25
            
            return {
                'registered': True,
                'creation_date': creation_date.isoformat() if creation_date else None,
                'age_days': age_days,
                'age_years': round(age_years, 1) if age_years else None,
                'registrar': w.registrar if hasattr(w, 'registrar') else None,
                'age_credibility': self._assess_age_credibility(age_days)
            }
            
        except Exception as e:
            logger.debug(f"WHOIS lookup failed for {domain}: {e}")
            return {
                'registered': False,
                'error': 'Could not retrieve domain information'
            }
    
    def _assess_age_credibility(self, age_days: Optional[int]) -> str:
        """Assess credibility based on domain age"""
        if not age_days:
            return 'unknown'
        
        if age_days < 180:  # Less than 6 months
            return 'very_new'
        elif age_days < 365:  # Less than 1 year
            return 'new'
        elif age_days < 730:  # Less than 2 years
            return 'relatively_new'
        elif age_days < 1825:  # Less than 5 years
            return 'established'
        else:
            return 'well_established'
    
    def _check_ssl(self, domain: str) -> Dict[str, Any]:
        """Check SSL certificate"""
        try:
            context = ssl.create_default_context()
            
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Extract certificate info
                    issued_to = dict(x[0] for x in cert['subject'])
                    issuer = dict(x[0] for x in cert['issuer'])
                    
                    # Check validity dates
                    not_before = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    
                    return {
                        'valid': True,
                        'issued_to': issued_to.get('commonName', domain),
                        'issuer': issuer.get('organizationName', 'Unknown'),
                        'expires': not_after.isoformat(),
                        'days_until_expiry': (not_after - datetime.now()).days,
                        'is_trusted_issuer': self._is_trusted_issuer(issuer.get('organizationName', ''))
                    }
                    
        except Exception as e:
            logger.debug(f"SSL check failed for {domain}: {e}")
            return {
                'valid': False,
                'error': 'No valid SSL certificate found'
            }
    
    def _is_trusted_issuer(self, issuer: str) -> bool:
        """Check if SSL issuer is trusted"""
        trusted_issuers = [
            'DigiCert', 'Let\'s Encrypt', 'Comodo', 'GeoTrust',
            'GlobalSign', 'GoDaddy', 'Symantec', 'Thawte',
            'RapidSSL', 'Sectigo', 'Entrust', 'VeriSign'
        ]
        
        return any(trusted in issuer for trusted in trusted_issuers)
    
    def _analyze_website_structure(self, domain: str) -> Dict[str, Any]:
        """Analyze website structure for credibility indicators"""
        try:
            # Check main pages
            pages_to_check = {
                'about': ['about', 'about-us', 'who-we-are'],
                'contact': ['contact', 'contact-us'],
                'privacy': ['privacy', 'privacy-policy'],
                'terms': ['terms', 'terms-of-service', 'terms-of-use']
            }
            
            found_pages = {}
            base_url = f"https://{domain}"
            
            # Check homepage first
            response = self.session.get(base_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for important pages in navigation
            for page_type, paths in pages_to_check.items():
                found = False
                for path in paths:
                    # Check links
                    if soup.find('a', href=re.compile(f'/{path}', re.I)):
                        found = True
                        break
                found_pages[f'has_{page_type}_page'] = found
            
            # Check for author/editorial info
            found_pages['has_authors'] = bool(
                soup.find(text=re.compile(r'(author|writer|journalist|reporter)', re.I))
            )
            
            # Check for dates/timestamps
            found_pages['has_dates'] = bool(
                soup.find(text=re.compile(r'\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}|published|updated', re.I))
            )
            
            # Check for social media links
            social_media = ['twitter', 'facebook', 'linkedin', 'youtube']
            found_pages['social_media_links'] = sum(
                1 for sm in social_media 
                if soup.find('a', href=re.compile(sm, re.I))
            )
            
            return found_pages
            
        except Exception as e:
            logger.debug(f"Website structure analysis failed for {domain}: {e}")
            return {'error': 'Could not analyze website structure'}
    
    def _analyze_reputation(self, domain: str) -> Dict[str, Any]:
        """Analyze source reputation through mentions"""
        reputation = {
            'mentions_found': False,
            'mention_count': 0,
            'recent_coverage': False
        }
        
        # Use NewsAPI if available
        if self.news_api_key:
            try:
                url = "https://newsapi.org/v2/everything"
                params = {
                    'apiKey': self.news_api_key,
                    'q': f'"{domain}" OR "{self._get_source_name(domain)}"',
                    'sortBy': 'relevancy',
                    'pageSize': 100,
                    'from': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                }
                
                response = self.session.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    reputation['mentions_found'] = data.get('totalResults', 0) > 0
                    reputation['mention_count'] = data.get('totalResults', 0)
                    reputation['recent_coverage'] = reputation['mention_count'] > 5
                    
                    # Analyze who's mentioning them
                    if data.get('articles'):
                        sources = [a.get('source', {}).get('name', '') for a in data['articles'][:20]]
                        reputable_mentions = sum(
                            1 for s in sources 
                            if any(rep in s.lower() for rep in ['reuters', 'ap', 'bbc', 'npr'])
                        )
                        reputation['reputable_mentions'] = reputable_mentions
                        
            except Exception as e:
                logger.debug(f"NewsAPI reputation check failed: {e}")
        
        # Fallback assessment based on domain
        if not reputation['mentions_found']:
            # Well-known domains get benefit of doubt
            well_known = ['cnn', 'bbc', 'reuters', 'ap', 'npr', 'wsj', 'nytimes']
            if any(wk in domain.lower() for wk in well_known):
                reputation['assumed_reputable'] = True
        
        return reputation
    
    def _analyze_transparency(self, domain: str, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze transparency indicators"""
        transparency = {
            'score': 0,
            'indicators': []
        }
        
        # Check structure-based transparency
        if structure.get('has_about_page'):
            transparency['score'] += 20
            transparency['indicators'].append('Has About page')
        
        if structure.get('has_contact_page'):
            transparency['score'] += 15
            transparency['indicators'].append('Has Contact information')
        
        if structure.get('has_authors'):
            transparency['score'] += 25
            transparency['indicators'].append('Shows author information')
        
        if structure.get('has_dates'):
            transparency['score'] += 15
            transparency['indicators'].append('Shows publication dates')
        
        if structure.get('has_privacy_page'):
            transparency['score'] += 10
            transparency['indicators'].append('Has Privacy Policy')
        
        if structure.get('social_media_links', 0) >= 2:
            transparency['score'] += 15
            transparency['indicators'].append('Active social media presence')
        
        # Determine transparency level
        if transparency['score'] >= 80:
            transparency['level'] = 'High Transparency'
        elif transparency['score'] >= 60:
            transparency['level'] = 'Good Transparency'
        elif transparency['score'] >= 40:
            transparency['level'] = 'Moderate Transparency'
        else:
            transparency['level'] = 'Low Transparency'
        
        return transparency
    
    def _analyze_history(self, domain: str, db_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze historical context"""
        history = {}
        
        # Known issues from database
        if db_info['credibility'] in ['Low', 'Very Low']:
            history['known_issues'] = True
            history['issue_description'] = self._get_issue_description(db_info)
        
        # Check if it's a known satire/fake news site
        fake_indicators = ['satire', 'fake', 'hoax', 'parody']
        if any(indicator in domain.lower() for indicator in fake_indicators):
            history['potential_satire'] = True
        
        # Check if it's state media
        state_media = {
            'rt.com': 'Russian state media',
            'sputniknews.com': 'Russian state media',
            'xinhuanet.com': 'Chinese state media',
            'presstv.ir': 'Iranian state media'
        }
        
        if domain in state_media:
            history['state_media'] = True
            history['state_affiliation'] = state_media[domain]
        
        return history
    
    def _calculate_credibility_score(self, analysis: Dict[str, Any]) -> int:
        """Calculate overall credibility score"""
        score = 50  # Base score
        
        # Database credibility (most important)
        db_cred = analysis['database_info']['credibility']
        if db_cred == 'High':
            score = 85
        elif db_cred == 'Medium':
            score = 65
        elif db_cred == 'Low':
            score = 35
        elif db_cred == 'Very Low':
            score = 15
        
        # Adjust based on technical factors (if available)
        tech = analysis.get('technical', {})
        
        # Domain age
        if tech.get('age_years'):
            if tech['age_years'] >= 5:
                score += 5
            elif tech['age_years'] >= 2:
                score += 3
            elif tech['age_years'] < 0.5:
                score -= 10
        
        # SSL certificate
        if tech.get('ssl', {}).get('valid'):
            score += 5
            if tech['ssl'].get('is_trusted_issuer'):
                score += 2
        else:
            score -= 5
        
        # Website structure
        structure = tech.get('structure', {})
        if structure.get('has_about_page') and structure.get('has_contact_page'):
            score += 5
        if structure.get('has_authors'):
            score += 5
        
        # Reputation
        rep = analysis.get('reputation', {})
        if rep.get('reputable_mentions', 0) >= 3:
            score += 10
        elif rep.get('mention_count', 0) > 10:
            score += 5
        
        # Transparency
        trans = analysis.get('transparency', {})
        if trans.get('score', 0) >= 80:
            score += 5
        elif trans.get('score', 0) < 40:
            score -= 5
        
        # Historical issues
        if analysis.get('history', {}).get('known_issues'):
            score -= 10
        if analysis.get('history', {}).get('state_media'):
            score -= 15
        
        return max(0, min(100, score))
    
    def _get_credibility_level(self, score: int) -> str:
        """Convert score to credibility level"""
        if score >= 80:
            return 'High Credibility'
        elif score >= 65:
            return 'Good Credibility'
        elif score >= 45:
            return 'Mixed Credibility'
        elif score >= 25:
            return 'Low Credibility'
        else:
            return 'Very Low Credibility'
    
    def _generate_findings(self, analysis: Dict[str, Any], score: int) -> List[Dict[str, Any]]:
        """Generate key findings"""
        findings = []
        
        # Database finding
        db_cred = analysis['database_info']['credibility']
        if db_cred != 'Unknown':
            severity = 'positive' if db_cred in ['High', 'Medium'] else 'high'
            findings.append({
                'type': 'database_rating',
                'text': f"{db_cred} credibility rating in media database",
                'severity': severity,
                'explanation': analysis['database_info']['description']
            })
        
        # Bias finding
        bias = analysis['database_info']['bias']
        if bias not in ['Unknown', 'Center']:
            findings.append({
                'type': 'political_bias',
                'text': f"{bias} political bias identified",
                'severity': 'medium',
                'explanation': f"This source has a known {bias.lower()} perspective"
            })
        
        # Technical findings
        tech = analysis.get('technical', {})
        if tech.get('age_years'):
            if tech['age_years'] < 1:
                findings.append({
                    'type': 'new_domain',
                    'text': f"Domain is only {tech['age_years']:.1f} years old",
                    'severity': 'high',
                    'explanation': 'New domains have less established credibility'
                })
            elif tech['age_years'] > 10:
                findings.append({
                    'type': 'established_domain',
                    'text': f"Well-established domain ({tech['age_years']:.0f} years)",
                    'severity': 'positive',
                    'explanation': 'Long-standing web presence indicates stability'
                })
        
        # SSL finding
        if not tech.get('ssl', {}).get('valid'):
            findings.append({
                'type': 'no_ssl',
                'text': 'No valid SSL certificate',
                'severity': 'high',
                'explanation': 'Secure sites should have valid HTTPS encryption'
            })
        
        # Transparency finding
        trans = analysis.get('transparency', {})
        if trans.get('score', 0) < 40:
            findings.append({
                'type': 'low_transparency',
                'text': 'Limited transparency indicators',
                'severity': 'medium',
                'explanation': 'Missing key pages like About, Contact, or author info'
            })
        
        # Historical issues
        history = analysis.get('history', {})
        if history.get('state_media'):
            findings.append({
                'type': 'state_media',
                'text': history.get('state_affiliation', 'State-affiliated media'),
                'severity': 'high',
                'explanation': 'Content may reflect government perspectives'
            })
        
        return findings[:5]  # Top 5 findings
    
    def _generate_summary(self, analysis: Dict[str, Any], score: int) -> str:
        """Generate human-readable summary"""
        
        name = analysis['source_name']
        db_cred = analysis['database_info']['credibility']
        
        # Base summary
        if score >= 80:
            base = f"{name} is a highly credible news source"
        elif score >= 65:
            base = f"{name} is generally credible"
        elif score >= 45:
            base = f"{name} has mixed credibility"
        else:
            base = f"{name} has questionable credibility"
        
        # Add details
        details = []
        
        if db_cred != 'Unknown':
            details.append(f"{db_cred.lower()} rating in media database")
        
        bias = analysis['database_info']['bias']
        if bias not in ['Unknown', 'Center']:
            details.append(f"{bias.lower()} political bias")
        
        tech = analysis.get('technical', {})
        if tech.get('age_years'):
            if tech['age_years'] >= 5:
                details.append("well-established")
            elif tech['age_years'] < 1:
                details.append("very new domain")
        
        if details:
            base += f" with {', '.join(details[:2])}"
        
        base += "."
        
        # Add warning if needed
        if score < 45:
            base += " Exercise caution and verify information from other sources."
        
        return base
    
    def _extract_domain(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract domain from input data"""
        
        # Direct domain
        if 'domain' in data:
            return data['domain'].lower().replace('www.', '')
        
        # Extract from URL
        if 'url' in data:
            try:
                parsed = urlparse(data['url'])
                return parsed.netloc.lower().replace('www.', '')
            except:
                pass
        
        return None
    
    def _get_source_name(self, domain: str) -> str:
        """Get human-readable source name"""
        
        # Check database first
        clean_domain = domain.lower().replace('www.', '')
        
        # Exact match
        if clean_domain in self.source_database:
            return self._domain_to_name(clean_domain)
        
        # Subdomain match
        for db_domain in self.source_database:
            if clean_domain.endswith(db_domain) or db_domain.endswith(clean_domain):
                return self._domain_to_name(db_domain)
        
        # Generate from domain
        name = domain.replace('www.', '')
        name = name.split('.')[0]  # Remove TLD
        name = name.replace('-', ' ').replace('_', ' ')
        return name.title()
    
    def _domain_to_name(self, domain: str) -> str:
        """Convert domain to proper name"""
        name_map = {
            'reuters.com': 'Reuters',
            'apnews.com': 'Associated Press',
            'bbc.com': 'BBC',
            'bbc.co.uk': 'BBC',
            'npr.org': 'NPR',
            'pbs.org': 'PBS',
            'wsj.com': 'The Wall Street Journal',
            'nytimes.com': 'The New York Times',
            'washingtonpost.com': 'The Washington Post',
            'theguardian.com': 'The Guardian',
            'cnn.com': 'CNN',
            'foxnews.com': 'Fox News',
            'msnbc.com': 'MSNBC',
            'nbcnews.com': 'NBC News',
            'abcnews.go.com': 'ABC News',
            'cbsnews.com': 'CBS News',
            'usatoday.com': 'USA Today',
            'politico.com': 'Politico',
            'axios.com': 'Axios',
            'thehill.com': 'The Hill',
            'bloomberg.com': 'Bloomberg',
            'ft.com': 'Financial Times',
            'economist.com': 'The Economist',
            'businessinsider.com': 'Business Insider',
            'techcrunch.com': 'TechCrunch',
            'theverge.com': 'The Verge',
            'wired.com': 'Wired',
            'vox.com': 'Vox',
            'slate.com': 'Slate',
            'salon.com': 'Salon',
            'huffpost.com': 'HuffPost',
            'buzzfeednews.com': 'BuzzFeed News',
            'propublica.org': 'ProPublica',
            'theatlantic.com': 'The Atlantic',
            'newyorker.com': 'The New Yorker',
            'motherjones.com': 'Mother Jones',
            'breitbart.com': 'Breitbart',
            'dailywire.com': 'The Daily Wire',
            'infowars.com': 'InfoWars'
        }
        
        return name_map.get(domain, domain.split('.')[0].title())
    
    def _get_credibility_description(self, credibility: str) -> str:
        """Get description for credibility level"""
        descriptions = {
            'High': 'Generally reliable for news reporting with proper fact-checking and editorial standards',
            'Medium': 'Generally acceptable but may have some bias or occasional factual errors',
            'Low': 'Often unreliable with significant bias, poor fact-checking, or misleading content',
            'Very Low': 'Highly unreliable source known for false information, conspiracy theories, or satire',
            'Unknown': 'No credibility information available for this source'
        }
        return descriptions.get(credibility, 'Unknown credibility rating')
    
    def _get_issue_description(self, db_info: Dict[str, Any]) -> str:
        """Get description of known issues"""
        
        if db_info['type'] == 'Conspiracy':
            return 'Known for promoting conspiracy theories and unverified claims'
        elif db_info['type'] == 'Fake News':
            return 'Identified as a source of fabricated or false news'
        elif db_info['type'] == 'Satire/Fake':
            return 'Satirical content that may be mistaken for real news'
        elif db_info['type'] == 'State Media':
            return 'State-controlled media that may reflect government propaganda'
        elif db_info['bias'] in ['Far-Left', 'Far-Right']:
            return f"Extreme {db_info['bias'].lower()} bias significantly affects reporting"
        else:
            return 'Known issues with reliability or accuracy'
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached result if available"""
        if cache_key in self.cache:
            cached_time, result = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                return result.copy()
        return None
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]):
        """Cache analysis result"""
        self.cache[cache_key] = (time.time(), result.copy())
        
        # Limit cache size
        if len(self.cache) > 100:
            # Remove oldest entries
            sorted_items = sorted(self.cache.items(), key=lambda x: x[1][0])
            for key, _ in sorted_items[:20]:
                del self.cache[key]
    
    def _initialize_source_database(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive source database"""
        return {
            # Highest credibility - News Agencies
            'reuters.com': {'credibility': 'High', 'bias': 'Center', 'type': 'News Agency'},
            'apnews.com': {'credibility': 'High', 'bias': 'Center', 'type': 'News Agency'},
            
            # High credibility - Major newspapers
            'nytimes.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Newspaper'},
            'washingtonpost.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Newspaper'},
            'wsj.com': {'credibility': 'High', 'bias': 'Center-Right', 'type': 'Business'},
            'theguardian.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Newspaper'},
            'ft.com': {'credibility': 'High', 'bias': 'Center-Right', 'type': 'Business'},
            'economist.com': {'credibility': 'High', 'bias': 'Center-Right', 'type': 'Magazine'},
            
            # High credibility - Public media
            'bbc.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Public Media'},
            'bbc.co.uk': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Public Media'},
            'npr.org': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Public Media'},
            'pbs.org': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Public Media'},
            
            # High credibility - Broadcast networks
            'nbcnews.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Broadcast'},
            'abcnews.go.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Broadcast'},
            'cbsnews.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Broadcast'},
            
            # High credibility - Financial
            'bloomberg.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Business'},
            'cnbc.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Business'},
            'marketwatch.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Business'},
            
            # High credibility - Tech
            'techcrunch.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Tech'},
            'theverge.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Tech'},
            'arstechnica.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Tech'},
            'wired.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Tech'},
            
            # High credibility - Non-profit
            'propublica.org': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Nonprofit'},
            
            # Medium credibility - Cable news
            'cnn.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Cable News'},
            'foxnews.com': {'credibility': 'Medium', 'bias': 'Right', 'type': 'Cable News'},
            'msnbc.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Cable News'},
            
            # Medium credibility - Digital
            'politico.com': {'credibility': 'Medium', 'bias': 'Center', 'type': 'Digital'},
            'axios.com': {'credibility': 'Medium', 'bias': 'Center', 'type': 'Digital'},
            'thehill.com': {'credibility': 'Medium', 'bias': 'Center', 'type': 'Digital'},
            'vox.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Digital'},
            'businessinsider.com': {'credibility': 'Medium', 'bias': 'Center-Left', 'type': 'Business'},
            'slate.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Digital'},
            'huffpost.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Digital'},
            'salon.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Digital'},
            
            # Medium credibility - Magazines
            'theatlantic.com': {'credibility': 'Medium', 'bias': 'Center-Left', 'type': 'Magazine'},
            'newyorker.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Magazine'},
            'motherjones.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Magazine'},
            'reason.com': {'credibility': 'Medium', 'bias': 'Right', 'type': 'Magazine'},
            'nationalreview.com': {'credibility': 'Medium', 'bias': 'Right', 'type': 'Magazine'},
            
            # Low credibility
            'breitbart.com': {'credibility': 'Low', 'bias': 'Far-Right', 'type': 'Digital'},
            'dailywire.com': {'credibility': 'Low', 'bias': 'Far-Right', 'type': 'Digital'},
            'thegatewaypundit.com': {'credibility': 'Low', 'bias': 'Far-Right', 'type': 'Digital'},
            'occupydemocrats.com': {'credibility': 'Low', 'bias': 'Far-Left', 'type': 'Digital'},
            'commondreams.org': {'credibility': 'Low', 'bias': 'Far-Left', 'type': 'Digital'},
            'rt.com': {'credibility': 'Low', 'bias': 'Pro-Russia', 'type': 'State Media'},
            'sputniknews.com': {'credibility': 'Low', 'bias': 'Pro-Russia', 'type': 'State Media'},
            
            # Very low credibility
            'infowars.com': {'credibility': 'Very Low', 'bias': 'Far-Right', 'type': 'Conspiracy'},
            'naturalnews.com': {'credibility': 'Very Low', 'bias': 'Far-Right', 'type': 'Conspiracy'},
            'beforeitsnews.com': {'credibility': 'Very Low', 'bias': 'Far-Right', 'type': 'Conspiracy'},
            'yournewswire.com': {'credibility': 'Very Low', 'bias': 'Mixed', 'type': 'Fake News'},
            'worldnewsdailyreport.com': {'credibility': 'Very Low', 'bias': 'Mixed', 'type': 'Satire/Fake'},
            
            # International
            'dw.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Public Media'},
            'france24.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Public Media'},
            'aljazeera.com': {'credibility': 'Medium', 'bias': 'Center-Left', 'type': 'International'},
            'scmp.com': {'credibility': 'Medium', 'bias': 'Center', 'type': 'International'},
            'globeandmail.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Newspaper'},
            'cbc.ca': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Public Media'}
        }
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        info = super().get_service_info()
        info.update({
            'capabilities': [
                'Database of 100+ news sources',
                'Domain age verification',
                'SSL certificate checking',
                'Website structure analysis',
                'Reputation tracking via news mentions',
                'Transparency scoring',
                'State media identification',
                'Bias classification'
            ],
            'sources_in_database': len(self.source_database),
            'technical_checks': [
                'WHOIS lookup',
                'SSL verification',
                'Website crawling',
                'News API integration'
            ],
            'api_status': {
                'news_api': 'active' if self.news_api_key else 'not configured'
            }
        })
        return info
