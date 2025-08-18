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
import requests
from bs4 import BeautifulSoup

# Handle whois import gracefully
try:
    import whois
    WHOIS_AVAILABLE = True
except ImportError:
    WHOIS_AVAILABLE = False
    logging.warning("python-whois not installed. Domain age checking will be limited.")

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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        # Note: timeout must be passed to individual requests, not session
        
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
            
            # Validate domain format
            if not self._is_valid_domain(domain):
                return self.get_error_result(f"Invalid domain format: {domain}")
            
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
            
            # Prepare technical analysis data with safe defaults
            technical_data = {}
            if 'technical' in analysis:
                tech = analysis['technical']
                technical_data = {
                    'age_years': tech.get('age_years'),
                    'age_credibility': tech.get('age_credibility', 'unknown'),
                    'ssl': tech.get('ssl', {}),
                    'registrar': tech.get('registrar'),
                    'structure': tech.get('structure', {})
                }
            
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
                    'technical_analysis': technical_data,
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
    
    def _is_valid_domain(self, domain: str) -> bool:
        """Validate domain format"""
        # Basic domain validation pattern
        domain_pattern = re.compile(
            r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$'
        )
        return bool(domain_pattern.match(domain))
    
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
                technical_results = {}
                
                # Domain age and registration
                if WHOIS_AVAILABLE:
                    domain_info = self._analyze_domain(domain)
                    technical_results.update(domain_info)
                    if domain_info.get('age_days'):
                        analysis['data_sources'].append('domain_registration')
                
                # SSL certificate
                ssl_info = self._check_ssl(domain)
                technical_results['ssl'] = ssl_info
                if ssl_info.get('valid'):
                    analysis['data_sources'].append('ssl_certificate')
                
                # Website structure
                structure_info = self._analyze_website_structure(domain)
                technical_results['structure'] = structure_info
                if structure_info.get('has_about_page'):
                    analysis['data_sources'].append('website_analysis')
                
                analysis['technical'] = technical_results
                    
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
            if clean_domain.endswith('.' + db_domain) or db_domain.endswith('.' + clean_domain):
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
        if not WHOIS_AVAILABLE:
            return {
                'registered': False,
                'error': 'WHOIS module not available'
            }
            
        try:
            # Get WHOIS information
            w = whois.whois(domain)
            
            # Handle various whois response formats
            creation_date = None
            if hasattr(w, 'creation_date'):
                creation_date = w.creation_date
                if isinstance(creation_date, list) and creation_date:
                    creation_date = creation_date[0]
            
            age_days = None
            age_years = None
            if creation_date and isinstance(creation_date, datetime):
                age = datetime.now() - creation_date
                age_days = age.days
                age_years = age_days / 365.25
            
            return {
                'registered': True,
                'creation_date': creation_date.isoformat() if creation_date else None,
                'age_days': age_days,
                'age_years': round(age_years, 1) if age_years else None,
                'registrar': getattr(w, 'registrar', None),
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
                    
                    # Extract certificate info safely
                    issued_to = dict(x[0] for x in cert.get('subject', []))
                    issuer = dict(x[0] for x in cert.get('issuer', []))
                    
                    # Parse dates more safely
                    not_before = cert.get('notBefore', '')
                    not_after = cert.get('notAfter', '')
                    
                    # Handle different date formats
                    try:
                        # Try parsing with timezone
                        not_after_dt = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                    except ValueError:
                        try:
                            # Try without timezone
                            not_after_dt = datetime.strptime(not_after.replace(' GMT', ''), '%b %d %H:%M:%S %Y')
                        except ValueError:
                            # Fallback to current time + 90 days
                            not_after_dt = datetime.now() + timedelta(days=90)
                    
                    days_until_expiry = (not_after_dt - datetime.now()).days
                    
                    return {
                        'valid': True,
                        'issued_to': issued_to.get('commonName', domain),
                        'issuer': issuer.get('organizationName', 'Unknown'),
                        'expires': not_after_dt.isoformat(),
                        'days_until_expiry': days_until_expiry,
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
            'RapidSSL', 'Sectigo', 'Entrust', 'VeriSign',
            'Amazon', 'Google Trust Services', 'Cloudflare'
        ]
        
        issuer_lower = issuer.lower()
        return any(trusted.lower() in issuer_lower for trusted in trusted_issuers)
    
    def _analyze_website_structure(self, domain: str) -> Dict[str, Any]:
        """Analyze website structure for credibility indicators"""
        try:
            # Check main pages
            pages_to_check = {
                'about': ['about', 'about-us', 'who-we-are', 'mission'],
                'contact': ['contact', 'contact-us', 'reach-us'],
                'privacy': ['privacy', 'privacy-policy', 'privacy-statement'],
                'terms': ['terms', 'terms-of-service', 'terms-of-use', 'tos']
            }
            
            found_pages = {}
            base_url = f"https://{domain}"
            
            # Make request with timeout
            try:
                response = self.session.get(base_url, timeout=10, allow_redirects=True)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                logger.debug(f"Failed to fetch {base_url}: {e}")
                return {'error': 'Could not access website'}
            
            # Parse with BeautifulSoup
            try:
                soup = BeautifulSoup(response.text, 'html.parser')
            except Exception as e:
                logger.debug(f"Failed to parse HTML: {e}")
                return {'error': 'Could not parse website content'}
            
            # Look for important pages in navigation
            for page_type, paths in pages_to_check.items():
                found = False
                for path in paths:
                    # Check links (case insensitive)
                    links = soup.find_all('a', href=re.compile(f'/{path}(?:/|$|\\?|#)', re.I))
                    if links:
                        found = True
                        break
                found_pages[f'has_{page_type}_page'] = found
            
            # Check for author/editorial info
            author_patterns = [
                r'author|writer|journalist|reporter|editor|by\s+\w+',
                r'written\s+by|published\s+by|staff'
            ]
            found_pages['has_authors'] = any(
                soup.find(text=re.compile(pattern, re.I)) 
                for pattern in author_patterns
            )
            
            # Check for dates/timestamps
            date_patterns = [
                r'\d{4}-\d{2}-\d{2}',
                r'\d{1,2}/\d{1,2}/\d{4}',
                r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}',
                r'published|updated|posted'
            ]
            found_pages['has_dates'] = any(
                soup.find(text=re.compile(pattern, re.I))
                for pattern in date_patterns
            )
            
            # Check for social media links
            social_media = ['twitter.com', 'facebook.com', 'linkedin.com', 'youtube.com', 'instagram.com']
            social_links = 0
            for sm in social_media:
                if soup.find('a', href=re.compile(sm, re.I)):
                    social_links += 1
            found_pages['social_media_links'] = social_links
            
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
                    total_results = data.get('totalResults', 0)
                    reputation['mentions_found'] = total_results > 0
                    reputation['mention_count'] = total_results
                    reputation['recent_coverage'] = total_results > 5
                    
                    # Analyze who's mentioning them
                    if data.get('articles'):
                        sources = [
                            article.get('source', {}).get('name', '') 
                            for article in data.get('articles', [])[:20]
                        ]
                        reputable_mentions = sum(
                            1 for s in sources 
                            if any(rep in s.lower() for rep in ['reuters', 'ap', 'bbc', 'npr', 'guardian'])
                        )
                        reputation['reputable_mentions'] = reputable_mentions
                        
            except Exception as e:
                logger.debug(f"NewsAPI reputation check failed: {e}")
        
        # Fallback assessment based on domain
        if not reputation['mentions_found']:
            # Well-known domains get benefit of doubt
            well_known = ['cnn', 'bbc', 'reuters', 'ap', 'npr', 'wsj', 'nytimes', 'guardian']
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
        fake_indicators = ['satire', 'fake', 'hoax', 'parody', 'onion']
        if any(indicator in domain.lower() for indicator in fake_indicators):
            history['potential_satire'] = True
        
        # Check if it's state media
        state_media = {
            'rt.com': 'Russian state media',
            'sputniknews.com': 'Russian state media',
            'xinhuanet.com': 'Chinese state media',
            'presstv.ir': 'Iranian state media',
            'telesurtv.net': 'Venezuelan state media',
            'cgtn.com': 'Chinese state media'
        }
        
        clean_domain = domain.lower().replace('www.', '')
        if clean_domain in state_media:
            history['state_media'] = True
            history['state_affiliation'] = state_media[clean_domain]
        
        return history
    
    def _calculate_credibility_score(self, analysis: Dict[str, Any]) -> int:
        """Calculate overall credibility score"""
        score = 50  # Base score
        
        # Database credibility (most important - 40 points range)
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
        
        # Domain age (up to +/-10 points)
        if tech.get('age_years') is not None:
            if tech['age_years'] >= 10:
                score += 10
            elif tech['age_years'] >= 5:
                score += 5
            elif tech['age_years'] >= 2:
                score += 3
            elif tech['age_years'] < 0.5:
                score -= 10
            elif tech['age_years'] < 1:
                score -= 5
        
        # SSL certificate (up to +/-7 points)
        ssl_info = tech.get('ssl', {})
        if ssl_info.get('valid'):
            score += 5
            if ssl_info.get('is_trusted_issuer'):
                score += 2
        elif ssl_info.get('valid') is False:
            score -= 5
        
        # Website structure (up to +10 points)
        structure = tech.get('structure', {})
        if structure:
            if structure.get('has_about_page') and structure.get('has_contact_page'):
                score += 5
            if structure.get('has_authors'):
                score += 5
        
        # Reputation (up to +10 points)
        rep = analysis.get('reputation', {})
        if rep.get('reputable_mentions', 0) >= 3:
            score += 10
        elif rep.get('mention_count', 0) > 10:
            score += 5
        
        # Transparency (up to +/-5 points)
        trans = analysis.get('transparency', {})
        if trans.get('score', 0) >= 80:
            score += 5
        elif trans.get('score', 0) < 40:
            score -= 5
        
        # Historical issues (negative adjustments)
        history = analysis.get('history', {})
        if history.get('known_issues'):
            score -= 10
        if history.get('state_media'):
            score -= 15
        if history.get('potential_satire'):
            score -= 20
        
        # Ensure score is within bounds
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
        if tech and not tech.get('error'):
            # Domain age
            if tech.get('age_years') is not None:
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
            ssl_info = tech.get('ssl', {})
            if ssl_info.get('valid', None) is False:
                findings.append({
                    'type': 'no_ssl',
                    'text': 'No valid SSL certificate',
                    'severity': 'high',
                    'explanation': 'Secure sites should have valid HTTPS encryption'
                })
        
        # Transparency finding
        trans = analysis.get('transparency', {})
        if trans.get('score', 100) < 40:
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
        
        if history.get('potential_satire'):
            findings.append({
                'type': 'satire_warning',
                'text': 'Possible satire or parody site',
                'severity': 'high',
                'explanation': 'Content may be intentionally false for humor'
            })
        
        # Sort by severity and return top 5
        severity_order = {'high': 0, 'medium': 1, 'positive': 2}
        findings.sort(key=lambda x: severity_order.get(x['severity'], 3))
        
        return findings[:5]
    
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
        if tech.get('age_years') is not None:
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
        if 'domain' in data and data['domain']:
            domain = data['domain'].lower().strip()
            # Remove protocol if present
            domain = re.sub(r'^https?://', '', domain)
            # Remove path if present
            domain = domain.split('/')[0]
            # Remove www
            domain = domain.replace('www.', '')
            return domain
        
        # Extract from URL
        if 'url' in data and data['url']:
            try:
                parsed = urlparse(data['url'])
                if parsed.netloc:
                    domain = parsed.netloc.lower()
                    # Remove www
                    domain = domain.replace('www.', '')
                    return domain
            except Exception as e:
                logger.debug(f"Failed to parse URL: {e}")
        
        return None
    
    def _get_source_name(self, domain: str) -> str:
        """Get human-readable source name"""
        
        # Check database first
        clean_domain = domain.lower().replace('www.', '')
        
        # Use the name map
        name = self._domain_to_name(clean_domain)
        if name != clean_domain:
            return name
        
        # Check for subdomain matches
        for db_domain in self.source_database:
            if clean_domain.endswith('.' + db_domain):
                return self._domain_to_name(db_domain)
        
        # Generate from domain
        name = domain.replace('www.', '')
        # Remove common TLDs
        for tld in ['.com', '.org', '.net', '.co.uk', '.co', '.io', '.news', '.tv']:
            if name.endswith(tld):
                name = name[:-len(tld)]
                break
        
        # Convert to title case
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
            'infowars.com': 'InfoWars',
            'rt.com': 'RT (Russia Today)',
            'aljazeera.com': 'Al Jazeera',
            'dw.com': 'Deutsche Welle',
            'france24.com': 'France 24',
            'scmp.com': 'South China Morning Post'
        }
        
        return name_map.get(domain, domain)
    
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
        
        source_type = db_info.get('type', '')
        
        if source_type == 'Conspiracy':
            return 'Known for promoting conspiracy theories and unverified claims'
        elif source_type == 'Fake News':
            return 'Identified as a source of fabricated or false news'
        elif source_type == 'Satire/Fake':
            return 'Satirical content that may be mistaken for real news'
        elif source_type == 'State Media':
            return 'State-controlled media that may reflect government propaganda'
        elif db_info.get('bias') in ['Far-Left', 'Far-Right']:
            return f"Extreme {db_info['bias'].lower()} bias significantly affects reporting"
        else:
            return 'Known issues with reliability or accuracy'
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached result if available"""
        if cache_key in self.cache:
            cached_time, result = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                logger.debug(f"Using cached result for {cache_key}")
                return result.copy()
            else:
                # Remove expired cache
                del self.cache[cache_key]
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
            'theonion.com': {'credibility': 'Very Low', 'bias': 'Mixed', 'type': 'Satire/Fake'},
            'babylonbee.com': {'credibility': 'Very Low', 'bias': 'Right', 'type': 'Satire/Fake'},
            
            # International
            'dw.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Public Media'},
            'france24.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Public Media'},
            'aljazeera.com': {'credibility': 'Medium', 'bias': 'Center-Left', 'type': 'International'},
            'scmp.com': {'credibility': 'Medium', 'bias': 'Center', 'type': 'International'},
            'globeandmail.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Newspaper'},
            'cbc.ca': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Public Media'},
            'xinhuanet.com': {'credibility': 'Low', 'bias': 'Pro-China', 'type': 'State Media'},
            'presstv.ir': {'credibility': 'Low', 'bias': 'Pro-Iran', 'type': 'State Media'}
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
                'WHOIS lookup' if WHOIS_AVAILABLE else 'WHOIS lookup (not available)',
                'SSL verification',
                'Website crawling',
                'News API integration'
            ],
            'api_status': {
                'news_api': 'active' if self.news_api_key else 'not configured',
                'whois': 'available' if WHOIS_AVAILABLE else 'not installed'
            }
        })
        return info
