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
from services.ai_enhancement_mixin import AIEnhancementMixin

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


class SourceCredibility(BaseAnalyzer, AIEnhancementMixin):
    """
    FIXED: Class name changed from SourceCredibilityAnalyzer to SourceCredibility
    Analyze the credibility of news sources using multiple factors with proper data structure
    """
    
    def __init__(self):
        super().__init__('source_credibility')
        AIEnhancementMixin.__init__(self)
        
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
            
            # BULLETPROOF AI ENHANCEMENT - Never crashes
            text = data.get('text', '')
            if text and self._ai_available:
                logger.info("Enhancing source credibility with AI insights")
                try:
                    enhanced_result = self._safely_enhance_service_result(
                        result,
                        '_ai_detect_credibility_issues',
                        domain=domain,
                        content=text[:2000],
                        source_info=analysis['database_info']
                    )
                    if enhanced_result:
                        result = enhanced_result
                except Exception as ai_error:
                    logger.warning(f"AI enhancement failed safely: {ai_error}")
            
            logger.info(f"Source credibility analysis complete: {domain} -> {credibility_score}/100 ({credibility_level})")
            return result
            
        except Exception as e:
            logger.error(f"Source credibility analysis failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
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
        
        # 2. Technical analysis (with timeout protection)
        if check_technical:
            try:
                technical_results = {}
                
                # Domain analysis with timeout
                if WHOIS_AVAILABLE:
                    try:
                        domain_info = self._analyze_domain_with_timeout(domain, timeout=10)
                        technical_results.update(domain_info)
                        if domain_info.get('age_days'):
                            analysis['data_sources'].append('domain_registration')
                    except Exception as e:
                        logger.warning(f"Domain analysis timeout/error for {domain}: {e}")
                
                # SSL check with timeout
                try:
                    ssl_info = self._check_ssl_with_timeout(domain, timeout=5)
                    technical_results['ssl'] = ssl_info
                    if ssl_info.get('valid'):
                        analysis['data_sources'].append('ssl_certificate')
                except Exception as e:
                    logger.warning(f"SSL check timeout/error for {domain}: {e}")
                    technical_results['ssl'] = {'valid': False, 'error': str(e)}
                
                # Website structure with timeout
                try:
                    structure_info = self._analyze_website_structure_with_timeout(domain, timeout=15)
                    technical_results['structure'] = structure_info
                    if structure_info.get('has_about_page'):
                        analysis['data_sources'].append('website_analysis')
                except Exception as e:
                    logger.warning(f"Website analysis timeout/error for {domain}: {e}")
                    technical_results['structure'] = {'has_about_page': False, 'error': str(e)}
                
                analysis['technical'] = technical_results
                    
            except Exception as e:
                logger.warning(f"Technical analysis failed for {domain}: {e}")
                analysis['technical'] = {'error': str(e)}
        
        # 3. Quick reputation analysis
        try:
            reputation = self._analyze_reputation_quick(domain)
            analysis['reputation'] = reputation
        except Exception as e:
            logger.warning(f"Reputation analysis failed for {domain}: {e}")
            analysis['reputation'] = {}
        
        # 4. Transparency indicators
        try:
            transparency = self._analyze_transparency(domain, analysis.get('technical', {}).get('structure', {}))
            analysis['transparency'] = transparency
        except Exception as e:
            logger.warning(f"Transparency analysis failed for {domain}: {e}")
            analysis['transparency'] = {'indicators': [], 'missing_elements': []}
        
        # 5. Historical context
        try:
            history = self._analyze_history(domain, analysis.get('database_info', {}))
            analysis['history'] = history
        except Exception as e:
            logger.warning(f"History analysis failed for {domain}: {e}")
            analysis['history'] = {}
        
        self._cache_result(cache_key, analysis)
        return analysis
    
    def _analyze_domain_with_timeout(self, domain: str, timeout: int = 10) -> Dict[str, Any]:
        """Analyze domain with timeout protection"""
        try:
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Domain analysis timeout")
            
            # Set timeout
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)
            
            try:
                result = self._analyze_domain(domain)
                signal.alarm(0)  # Cancel alarm
                return result
            except TimeoutError:
                raise
            finally:
                signal.alarm(0)  # Ensure alarm is cancelled
                
        except Exception as e:
            logger.warning(f"Domain analysis with timeout failed: {e}")
            return {'whois_available': False, 'error': str(e)}
    
    def _check_ssl_with_timeout(self, domain: str, timeout: int = 5) -> Dict[str, Any]:
        """Check SSL with timeout protection"""
        try:
            import socket
            socket.setdefaulttimeout(timeout)
            return self._check_ssl(domain)
        except Exception as e:
            return {'valid': False, 'error': f'SSL check timeout: {str(e)}'}
        finally:
            socket.setdefaulttimeout(None)  # Reset default
    
    def _analyze_website_structure_with_timeout(self, domain: str, timeout: int = 15) -> Dict[str, Any]:
        """Analyze website structure with timeout protection"""
        try:
            return self._analyze_website_structure_timeout_protected(domain, timeout)
        except Exception as e:
            return {
                'has_about_page': False,
                'has_contact_page': False,
                'has_privacy_policy': False,
                'has_author_bylines': False,
                'transparency_score': 0,
                'error': f'Website analysis timeout: {str(e)}'
            }
    
    def _analyze_website_structure_timeout_protected(self, domain: str, timeout: int) -> Dict[str, Any]:
        """Website structure analysis with timeout protection"""
        structure = {
            'has_about_page': False,
            'has_contact_page': False,
            'has_privacy_policy': False,
            'has_author_bylines': False,
            'transparency_score': 0
        }
        
        try:
            base_url = f"https://{domain}"
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (compatible; CredibilityAnalyzer/1.0)'
            })
            
            # Check main page with timeout
            response = session.get(base_url, timeout=timeout)
            if response.status_code == 200:
                content = response.text.lower()
                
                # Look for transparency indicators
                if any(phrase in content for phrase in ['about us', 'about', '/about']):
                    structure['has_about_page'] = True
                    structure['transparency_score'] += 25
                
                if any(phrase in content for phrase in ['contact us', 'contact', '/contact']):
                    structure['has_contact_page'] = True
                    structure['transparency_score'] += 25
                
                if any(phrase in content for phrase in ['privacy policy', 'privacy']):
                    structure['has_privacy_policy'] = True
                    structure['transparency_score'] += 20
                
                if any(phrase in content for phrase in ['by:', 'author:', 'reporter:', 'correspondent:']):
                    structure['has_author_bylines'] = True
                    structure['transparency_score'] += 30
            
        except Exception as e:
            logger.warning(f"Website structure analysis failed for {domain}: {e}")
            structure['error'] = str(e)
        
        return structure
    
    def _analyze_reputation_quick(self, domain: str) -> Dict[str, Any]:
        """Quick reputation analysis without external API calls"""
        return {
            'mentions_found': False,
            'positive_mentions': 0,
            'negative_mentions': 0,
            'total_mentions': 0,
            'analysis_method': 'basic'
        }
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached result if available and not expired"""
        if cache_key in self.cache:
            cached_time, result = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                return result.copy()
        return None
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]):
        """Cache analysis result"""
        self.cache[cache_key] = (time.time(), result.copy())
        
        # Limit cache size
        if len(self.cache) > 500:
            # Remove oldest entries
            sorted_items = sorted(self.cache.items(), key=lambda x: x[1][0])
            for key, _ in sorted_items[:50]:
                del self.cache[key]
    
    def _extract_domain(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract domain from various input formats"""
        # Check if domain is directly provided
        domain = data.get('domain', '')
        if domain and isinstance(domain, str):
            clean_domain = domain.lower().replace('www.', '').strip()
            if self._is_valid_domain(clean_domain):
                return clean_domain
        
        # Extract from URL
        url = data.get('url', '')
        if url and isinstance(url, str):
            try:
                parsed = urlparse(url if url.startswith(('http://', 'https://')) else f'https://{url}')
                domain = parsed.netloc.lower().replace('www.', '').strip()
                if domain and self._is_valid_domain(domain):
                    return domain
            except Exception as e:
                logger.warning(f"Failed to parse URL {url}: {e}")
        
        # Try to extract from source field
        source = data.get('source', '')
        if source and isinstance(source, str):
            source = source.strip().lower().replace('www.', '')
            if '.' in source and not ' ' in source and len(source) > 3:
                if self._is_valid_domain(source):
                    return source
        
        # Try to extract from article data if present
        if 'article' in data and isinstance(data['article'], dict):
            article_url = data['article'].get('url', '')
            if article_url:
                try:
                    parsed = urlparse(article_url)
                    domain = parsed.netloc.lower().replace('www.', '').strip()
                    if domain and self._is_valid_domain(domain):
                        return domain
                except:
                    pass
        
        return None
    
    def _is_valid_domain(self, domain: str) -> bool:
        """Check if domain format is valid"""
        if not domain or len(domain) < 3:
            return False
        domain_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9\-_.]*[a-zA-Z0-9]*\.[a-zA-Z]{2,}$'
        return bool(re.match(domain_pattern, domain.lower()))
    
    def _init_credibility_database(self):
        """Initialize built-in credibility database"""
        self.source_database = {
            # High credibility sources
            'reuters.com': {'credibility': 'Very High', 'bias': 'Minimal', 'type': 'News Agency'},
            'ap.org': {'credibility': 'Very High', 'bias': 'Minimal', 'type': 'News Agency'}, 
            'apnews.com': {'credibility': 'Very High', 'bias': 'Minimal', 'type': 'News Agency'},
            'bbc.com': {'credibility': 'Very High', 'bias': 'Minimal-Left', 'type': 'Public Broadcaster'},
            'bbc.co.uk': {'credibility': 'Very High', 'bias': 'Minimal-Left', 'type': 'Public Broadcaster'},
            'npr.org': {'credibility': 'Very High', 'bias': 'Minimal-Left', 'type': 'Public Radio'},
            'pbs.org': {'credibility': 'Very High', 'bias': 'Minimal-Left', 'type': 'Public Television'},
            'theguardian.com': {'credibility': 'High', 'bias': 'Left-Leaning', 'type': 'Newspaper'},
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
    
    def _get_source_name(self, domain: str) -> str:
        """Get human-readable source name from domain"""
        name_mapping = {
            'nytimes.com': 'The New York Times',
            'washingtonpost.com': 'The Washington Post',
            'theguardian.com': 'The Guardian',
            'wsj.com': 'The Wall Street Journal',
            'reuters.com': 'Reuters',
            'ap.org': 'Associated Press',
            'apnews.com': 'Associated Press',
            'bbc.com': 'BBC News',
            'bbc.co.uk': 'BBC News',
            'cnn.com': 'CNN',
            'foxnews.com': 'Fox News',
            'msnbc.com': 'MSNBC',
            'npr.org': 'NPR',
            'pbs.org': 'PBS NewsHour',
            'cbsnews.com': 'CBS News',
            'abcnews.go.com': 'ABC News',
            'nbcnews.com': 'NBC News',
            'usatoday.com': 'USA Today'
        }
        
        if domain in name_mapping:
            return name_mapping[domain]
        
        # Generate name from domain
        name = domain.replace('www.', '').replace('.com', '').replace('.org', '').replace('.net', '')
        return name.title()
    
    def _analyze_domain(self, domain: str) -> Dict[str, Any]:
        """Analyze domain registration information"""
        try:
            if not WHOIS_AVAILABLE:
                return {'error': 'WHOIS not available'}
            
            w = whois.whois(domain)
            
            creation_date = w.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            
            if creation_date:
                age_days = (datetime.now() - creation_date).days
                
                # Determine age credibility
                if age_days > 3650:  # 10+ years
                    age_credibility = 'very_high'
                elif age_days > 1825:  # 5+ years  
                    age_credibility = 'high'
                elif age_days > 365:  # 1+ years
                    age_credibility = 'medium'
                elif age_days > 90:  # 3+ months
                    age_credibility = 'low'
                else:
                    age_credibility = 'very_low'
                
                return {
                    'creation_date': creation_date.isoformat() if creation_date else None,
                    'age_days': age_days,
                    'age_credibility': age_credibility,
                    'registrar': str(w.registrar) if w.registrar else None,
                    'whois_available': True
                }
            
        except Exception as e:
            logger.warning(f"WHOIS lookup failed for {domain}: {e}")
        
        return {'whois_available': False, 'error': 'WHOIS lookup failed'}
    
    def _check_ssl(self, domain: str) -> Dict[str, Any]:
        """Check SSL certificate validity"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Check expiration
                    not_after = cert.get('notAfter')
                    if not_after:
                        expiry_date = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                        days_remaining = (expiry_date - datetime.now()).days
                        
                        return {
                            'valid': True,
                            'expires': expiry_date.isoformat(),
                            'days_remaining': days_remaining,
                            'issuer': dict(x[0] for x in cert['issuer']).get('organizationName', 'Unknown')
                        }
            
        except Exception as e:
            logger.warning(f"SSL check failed for {domain}: {e}")
        
        return {'valid': False, 'error': 'SSL check failed'}
    
    def _analyze_website_structure(self, domain: str) -> Dict[str, Any]:
        """Analyze website structure for credibility indicators"""
        structure = {
            'has_about_page': False,
            'has_contact_page': False,
            'has_privacy_policy': False,
            'has_author_bylines': False,
            'transparency_score': 0
        }
        
        try:
            base_url = f"https://{domain}"
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (compatible; CredibilityAnalyzer/1.0)'
            })
            
            # Check main page
            response = session.get(base_url, timeout=10)
            if response.status_code == 200:
                content = response.text.lower()
                
                # Look for transparency indicators
                if any(phrase in content for phrase in ['about us', 'about', '/about']):
                    structure['has_about_page'] = True
                    structure['transparency_score'] += 25
                
                if any(phrase in content for phrase in ['contact us', 'contact', '/contact']):
                    structure['has_contact_page'] = True
                    structure['transparency_score'] += 25
                
                if any(phrase in content for phrase in ['privacy policy', 'privacy']):
                    structure['has_privacy_policy'] = True
                    structure['transparency_score'] += 20
                
                if any(phrase in content for phrase in ['by:', 'author:', 'reporter:', 'correspondent:']):
                    structure['has_author_bylines'] = True
                    structure['transparency_score'] += 30
            
        except Exception as e:
            logger.warning(f"Website structure analysis failed for {domain}: {e}")
            structure['error'] = str(e)
        
        return structure
    
    def _analyze_reputation(self, domain: str) -> Dict[str, Any]:
        """Analyze source reputation through news mentions"""
        reputation = {
            'mentions_found': False,
            'positive_mentions': 0,
            'negative_mentions': 0,
            'total_mentions': 0
        }
        
        # This would typically use news APIs to search for mentions
        # For now, return basic structure
        return reputation
    
    def _analyze_transparency(self, domain: str, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze transparency indicators"""
        indicators = []
        missing_elements = []
        
        if structure.get('has_about_page'):
            indicators.append('About page available')
        else:
            missing_elements.append('About page')
        
        if structure.get('has_contact_page'):
            indicators.append('Contact information provided')
        else:
            missing_elements.append('Contact information')
        
        if structure.get('has_privacy_policy'):
            indicators.append('Privacy policy available')
        else:
            missing_elements.append('Privacy policy')
        
        if structure.get('has_author_bylines'):
            indicators.append('Author attribution present')
        else:
            missing_elements.append('Author attribution')
        
        return {
            'indicators': indicators,
            'missing_elements': missing_elements,
            'transparency_score': len(indicators) * 25
        }
    
    def _analyze_history(self, domain: str, db_info: Dict[str, str]) -> Dict[str, Any]:
        """Analyze historical context"""
        return {
            'established': db_info.get('type') in ['Newspaper', 'News Agency', 'Broadcast News'],
            'category': db_info.get('type', 'Unknown')
        }
    
    def _calculate_credibility_score(self, analysis: Dict[str, Any]) -> int:
        """Calculate overall credibility score (0-100)"""
        score = 50  # Base score
        
        # Database credibility (40% weight)
        db_credibility = analysis['database_info'].get('credibility', 'Unknown')
        if db_credibility == 'Very High':
            score += 40
        elif db_credibility == 'High':
            score += 30
        elif db_credibility == 'Medium':
            score += 10
        elif db_credibility == 'Medium-Low':
            score -= 10
        elif db_credibility == 'Low':
            score -= 25
        elif db_credibility == 'Very Low':
            score -= 40
        
        # Technical factors (30% weight)
        if 'technical' in analysis:
            tech = analysis['technical']
            
            # Domain age
            age_cred = tech.get('age_credibility')
            if age_cred == 'very_high':
                score += 10
            elif age_cred == 'high':
                score += 7
            elif age_cred == 'medium':
                score += 4
            elif age_cred == 'low':
                score -= 5
            elif age_cred == 'very_low':
                score -= 10
            
            # SSL certificate
            if tech.get('ssl', {}).get('valid'):
                score += 5
            
            # Website structure
            structure = tech.get('structure', {})
            score += min(15, structure.get('transparency_score', 0) // 5)
        
        # Transparency (20% weight)
        if 'transparency' in analysis:
            transparency_score = analysis['transparency'].get('transparency_score', 0)
            score += min(20, transparency_score // 5)
        
        # Reputation (10% weight)
        if 'reputation' in analysis:
            rep = analysis['reputation']
            if rep.get('mentions_found'):
                net_mentions = rep.get('positive_mentions', 0) - rep.get('negative_mentions', 0)
                score += min(10, max(-10, net_mentions))
        
        return max(0, min(100, score))
    
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
