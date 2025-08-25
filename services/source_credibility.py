"""
Source Credibility Analyzer Service - AI ENHANCED VERSION
Comprehensive source credibility analysis with domain checks, reputation analysis,
and AI-powered insights - FIXED: AI null handling bug
"""

import os
import time
import logging
import re
import ssl
import socket
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

# Import after basic setup
try:
    import whois
    WHOIS_AVAILABLE = True
except ImportError:
    WHOIS_AVAILABLE = False
    logging.warning("python-whois not available - domain age checks disabled")

from config import Config
from services.base_analyzer import BaseAnalyzer
from services.ai_enhancement_mixin import AIEnhancementMixin

logger = logging.getLogger(__name__)


class SourceCredibilityAnalyzer(BaseAnalyzer, AIEnhancementMixin):
    """
    Analyze source credibility using multiple signals WITH AI ENHANCEMENT
    FIXED: Proper AI error handling to prevent crashes
    """
    
    def __init__(self):
        """Initialize the source credibility analyzer"""
        super().__init__('source_credibility')
        AIEnhancementMixin.__init__(self)
        
        # API keys
        self.news_api_key = Config.NEWS_API_KEY or Config.NEWSAPI_KEY
        
        # Initialize source database
        self.source_database = self._initialize_source_database()
        
        # Session for web requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Cache
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour
        
        logger.info(f"SourceCredibilityAnalyzer initialized - AI: {self._ai_available}, NewsAPI: {bool(self.news_api_key)}")
    
    def _check_availability(self) -> bool:
        """Check if the service is available"""
        return True  # Always available since we have fallback methods
    
    def _is_valid_domain(self, domain: str) -> bool:
        """Check if domain format is valid"""
        # Basic domain validation
        domain_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-_]*[a-zA-Z0-9]*\.[a-zA-Z]{2,}$'
        return bool(re.match(domain_pattern, domain.lower()))
    
    def _extract_domain(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract domain from various input formats"""
        # Check if domain is directly provided
        domain = data.get('domain', '')
        if domain:
            return domain.lower().replace('www.', '')
        
        # Extract from URL
        url = data.get('url', '')
        if url:
            try:
                parsed = urlparse(url)
                domain = parsed.netloc.lower().replace('www.', '')
                if domain:
                    return domain
            except Exception as e:
                logger.warning(f"Failed to parse URL {url}: {e}")
        
        # Try to extract from source field
        source = data.get('source', '')
        if source:
            # If source looks like a domain
            if '.' in source and not ' ' in source:
                return source.lower().replace('www.', '')
        
        return None
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze source credibility WITH AI ENHANCEMENT
        FIXED: Proper AI error handling prevents crashes
        
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
            
            # Build response
            result = {
                'service': self.service_name,
                'success': True,
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
                    **technical_data
                },
                'metadata': {
                    'analysis_time': time.time() - start_time,
                    'data_sources': analysis.get('data_sources', []),
                    'whois_available': WHOIS_AVAILABLE,
                    'news_api_available': bool(self.news_api_key),
                    'ai_enhanced': self._ai_available
                }
            }
            
            # FIXED AI ENHANCEMENT - Proper null handling prevents crashes
            text = data.get('text', '')
            if self._ai_available and text:
                logger.info("Enhancing source credibility with AI insights")
                try:
                    ai_flags = self._ai_detect_credibility_issues(
                        domain=domain,
                        content=text[:2000],
                        source_info=analysis['database_info']
                    )
                    
                    # CRITICAL FIX: Proper type and null checking
                    if ai_flags and isinstance(ai_flags, dict):
                        ai_insights_added = False
                        
                        # Add AI-detected red flags with validation
                        red_flags = ai_flags.get('red_flags', [])
                        if red_flags and isinstance(red_flags, list):
                            for flag in red_flags[:3]:
                                if isinstance(flag, dict) and 'issue' in flag:
                                    findings.append({
                                        'type': 'warning',
                                        'severity': 'high',
                                        'text': f"AI detected: {flag['issue']}",
                                        'explanation': flag.get('explanation', '')
                                    })
                                    ai_insights_added = True
                        
                        # Add trust signals with validation
                        trust_signals = ai_flags.get('trust_signals', [])
                        if trust_signals and isinstance(trust_signals, list):
                            for signal in trust_signals[:2]:
                                if isinstance(signal, str) and signal.strip():
                                    findings.append({
                                        'type': 'positive',
                                        'severity': 'positive',
                                        'text': f"AI verified: {signal}",
                                        'explanation': 'Indicates credible source'
                                    })
                                    ai_insights_added = True
                        
                        if ai_insights_added:
                            result['metadata']['ai_insights_added'] = True
                            logger.info("AI insights successfully added to findings")
                        else:
                            logger.info("AI returned data but no usable insights")
                    else:
                        logger.info("AI enhancement returned no usable data")
                        
                except Exception as ai_error:
                    logger.warning(f"AI enhancement failed but continuing analysis: {ai_error}")
                    # Don't crash the entire analysis if AI fails
            elif self._ai_available and not text:
                logger.debug("AI available but no text content provided for enhancement")
            else:
                logger.debug("AI enhancement not available")
            
            return result
            
        except Exception as e:
            logger.error(f"Source credibility analysis failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _analyze_source_comprehensive(self, domain: str, check_technical: bool = True) -> Dict[str, Any]:
        """Perform comprehensive source analysis"""
        # Check cache first
        cache_key = f"source:{domain}:{check_technical}"
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
        
        analysis = {
            'source_name': self._get_source_name(domain),
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
                
                # Website structure - PATCHED WITH TIMEOUT AND CONFIG
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
        
        # Return unknown
        return {
            'credibility': 'Unknown',
            'bias': 'Unknown', 
            'type': 'Unknown',
            'description': 'Source not found in credibility database'
        }
    
    def _get_source_name(self, domain: str) -> str:
        """Get human-readable source name"""
        # Remove common prefixes/suffixes
        name = domain.lower().replace('www.', '').replace('.com', '').replace('.org', '').replace('.net', '')
        
        # Known names mapping
        known_names = {
            'nytimes': 'The New York Times',
            'wsj': 'The Wall Street Journal',
            'washingtonpost': 'The Washington Post',
            'bbc': 'BBC',
            'cnn': 'CNN',
            'foxnews': 'Fox News',
            'npr': 'NPR',
            'apnews': 'Associated Press',
            'reuters': 'Reuters',
            'theguardian': 'The Guardian',
            'bloomberg': 'Bloomberg',
            'ft': 'Financial Times'
        }
        
        return known_names.get(name, domain.capitalize())
    
    def _analyze_domain(self, domain: str) -> Dict[str, Any]:
        """Analyze domain registration and age"""
        if not WHOIS_AVAILABLE:
            return {'error': 'WHOIS lookup not available'}
        
        try:
            w = whois.whois(domain)
            
            # Extract creation date
            creation_date = w.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            
            if creation_date:
                age_days = (datetime.now() - creation_date).days
                age_years = age_days / 365.25
                
                # Determine credibility based on age
                if age_years < 0.5:
                    age_credibility = 'very_new'
                elif age_years < 1:
                    age_credibility = 'new'
                elif age_years < 3:
                    age_credibility = 'moderate'
                else:
                    age_credibility = 'established'
                
                return {
                    'age_days': age_days,
                    'age_years': round(age_years, 1),
                    'age_credibility': age_credibility,
                    'creation_date': creation_date.isoformat()
                }
            
            return {'error': 'No creation date found'}
            
        except Exception as e:
            logger.warning(f"WHOIS lookup failed for {domain}: {e}")
            return {'error': str(e)}
    
    def _check_ssl(self, domain: str) -> Dict[str, Any]:
        """Check SSL certificate validity"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Check certificate validity
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_remaining = (not_after - datetime.now()).days
                    
                    return {
                        'valid': True,
                        'issuer': dict(x[0] for x in cert['issuer']),
                        'expires': not_after.isoformat(),
                        'days_remaining': days_remaining,
                        'expired': days_remaining < 0
                    }
                    
        except Exception as e:
            logger.warning(f"SSL check failed for {domain}: {e}")
            return {
                'valid': False,
                'error': str(e)
            }
    
    def _analyze_website_structure(self, domain: str) -> Dict[str, Any]:
        """Analyze website structure for transparency indicators with proper timeout"""
        try:
            url = f"https://{domain}"
            
            # Get timeout from config or use default - PATCHED
            timeout = self.config.options.get('web_request_timeout', 5) if self.config and self.config.options else 5
            
            response = self.session.get(
                url, 
                timeout=timeout,  # Use configured timeout instead of hardcoded 10
                allow_redirects=True,
                verify=False  # Skip SSL verification for speed
            )
            
            # Quick analysis without BeautifulSoup for speed
            text = response.text.lower()
            
            return {
                'has_about_page': '/about' in text or 'about-us' in text,
                'has_contact_page': '/contact' in text or 'contact-us' in text,
                'has_privacy_policy': 'privacy' in text,
                'has_terms': 'terms' in text,
                'has_author_bylines': 'author' in text or 'by ' in text,
                'has_date_stamps': any(year in text for year in ['2023', '2024', '2025']),
                'response_time': response.elapsed.total_seconds()
            }
                
        except Exception as e:
            logger.warning(f"Website structure analysis failed for {domain}: {e}")
            return {'error': str(e)}
    
    def _analyze_reputation(self, domain: str) -> Dict[str, Any]:
        """Analyze domain reputation using news mentions"""
        if not self.news_api_key:
            return {
                'api_available': False,
                'mentions_found': False
            }
        
        try:
            # Search for domain mentions in news
            url = 'https://newsapi.org/v2/everything'
            params = {
                'q': f'"{domain}"',
                'apiKey': self.news_api_key,
                'sortBy': 'relevancy',
                'pageSize': 10,
                'language': 'en',
                'from': (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                total_results = data.get('totalResults', 0)
                
                if total_results > 0:
                    # Analyze sentiment of mentions
                    articles = data.get('articles', [])
                    positive_mentions = 0
                    negative_mentions = 0
                    
                    negative_keywords = ['fake', 'false', 'misleading', 'propaganda', 'conspiracy', 'debunked']
                    positive_keywords = ['reliable', 'trusted', 'credible', 'accurate', 'award', 'respected']
                    
                    for article in articles[:10]:
                        title = (article.get('title', '') + ' ' + article.get('description', '')).lower()
                        
                        if any(keyword in title for keyword in negative_keywords):
                            negative_mentions += 1
                        elif any(keyword in title for keyword in positive_keywords):
                            positive_mentions += 1
                    
                    # Calculate reputation score
                    reputation_score = 50  # Base score
                    reputation_score += (positive_mentions * 10)
                    reputation_score -= (negative_mentions * 15)
                    reputation_score = max(0, min(100, reputation_score))
                    
                    return {
                        'api_available': True,
                        'mentions_found': True,
                        'total_mentions': total_results,
                        'positive_mentions': positive_mentions,
                        'negative_mentions': negative_mentions,
                        'reputation_score': reputation_score
                    }
                
                # No mentions found
                return {
                    'api_available': True,
                    'mentions_found': False,
                    'total_mentions': 0,
                    'reputation_score': 50  # Neutral
                }
            else:
                return {
                    'api_available': True,
                    'mentions_found': False,
                    'error': data.get('message', 'Unknown error')
                }
                
        except Exception as e:
            logger.warning(f"Reputation analysis failed for {domain}: {e}")
            return {
                'api_available': True,
                'mentions_found': False,
                'error': str(e)
            }
    
    def _analyze_transparency(self, domain: str, structure_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze transparency indicators"""
        transparency_score = 50  # Base score
        indicators = []
        
        # Use structure info if available
        if structure_info and not structure_info.get('error'):
            if structure_info.get('has_about_page'):
                transparency_score += 10
                indicators.append('About page present')
            
            if structure_info.get('has_contact_page'):
                transparency_score += 10
                indicators.append('Contact information available')
            
            if structure_info.get('has_privacy_policy'):
                transparency_score += 5
                indicators.append('Privacy policy published')
            
            if structure_info.get('has_author_bylines'):
                transparency_score += 15
                indicators.append('Author attribution present')
            
            if structure_info.get('has_date_stamps'):
                transparency_score += 10
                indicators.append('Publication dates shown')
        
        return {
            'score': min(100, transparency_score),
            'indicators': indicators,
            'missing_elements': self._get_missing_transparency_elements(structure_info)
        }
    
    def _get_missing_transparency_elements(self, structure_info: Dict[str, Any]) -> List[str]:
        """Identify missing transparency elements"""
        missing = []
        
        if not structure_info or structure_info.get('error'):
            return ['Unable to analyze website structure']
        
        if not structure_info.get('has_about_page'):
            missing.append('No about page found')
        
        if not structure_info.get('has_contact_page'):
            missing.append('No contact information')
        
        if not structure_info.get('has_author_bylines'):
            missing.append('No author attribution')
        
        if not structure_info.get('has_date_stamps'):
            missing.append('No publication dates')
        
        return missing
    
    def _analyze_history(self, domain: str, db_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze historical context of the source"""
        history = {
            'established_source': db_info['credibility'] != 'Unknown',
            'known_issues': [],
            'awards': []
        }
        
        # Add known issues for specific sources
        if db_info['credibility'] == 'Low':
            history['known_issues'].append('History of publishing unverified information')
        
        if db_info['bias'] in ['Far-Left', 'Far-Right']:
            history['known_issues'].append(f'Known for {db_info["bias"]} political bias')
        
        # Add positive history for high-credibility sources
        if db_info['credibility'] == 'High':
            if db_info['type'] == 'News Agency':
                history['awards'].append('Internationally recognized news agency')
            elif 'Prize' in db_info.get('description', ''):
                history['awards'].append('Award-winning journalism')
        
        return history
    
    def _calculate_credibility_score(self, analysis: Dict[str, Any]) -> int:
        """Calculate overall credibility score"""
        score = 50  # Base score
        
        # Database credibility (0-40 points)
        db_credibility = analysis['database_info']['credibility']
        if db_credibility == 'High':
            score += 40
        elif db_credibility == 'Medium':
            score += 25
        elif db_credibility == 'Low':
            score += 5
        # Unknown gets 0 additional points
        
        # Technical factors (0-30 points)
        if 'technical' in analysis and not analysis['technical'].get('error'):
            tech = analysis['technical']
            
            # Domain age (0-15 points)
            age_cred = tech.get('age_credibility', 'unknown')
            if age_cred == 'established':
                score += 15
            elif age_cred == 'moderate':
                score += 10
            elif age_cred == 'new':
                score += 5
            # very_new gets 0 points
            
            # SSL (0-10 points)
            if tech.get('ssl', {}).get('valid'):
                score += 10
            
            # Website structure (0-5 points)
            structure_score = tech.get('structure', {}).get('transparency_score', 0)
            score += int(structure_score * 0.05)
        
        # Reputation (0-20 points)
        if 'reputation' in analysis and analysis['reputation'].get('mentions_found'):
            rep_score = analysis['reputation'].get('reputation_score', 50)
            score += int((rep_score - 50) * 0.4)  # Convert to 0-20 range
        
        # Transparency (0-10 points)
        if 'transparency' in analysis:
            trans_score = analysis['transparency'].get('score', 50)
            score += int(trans_score * 0.1)
        
        # Ensure score is within bounds
        return max(0, min(100, score))
    
    def _get_credibility_level(self, score: int) -> str:
        """Convert score to credibility level"""
        if score >= 80:
            return 'Very High'
        elif score >= 65:
            return 'High'
        elif score >= 50:
            return 'Medium'
        elif score >= 35:
            return 'Low'
        else:
            return 'Very Low'
    
    def _get_credibility_description(self, credibility: str) -> str:
        """Get description for credibility level"""
        descriptions = {
            'High': 'Established source with strong reputation for accuracy',
            'Medium': 'Generally reliable with good journalistic standards',
            'Low': 'Questionable reliability, often publishes unverified information',
            'Unknown': 'Source not in our database, credibility cannot be determined'
        }
        return descriptions.get(credibility, 'No description available')
    
    def _generate_findings(self, analysis: Dict[str, Any], score: int) -> List[Dict[str, Any]]:
        """Generate findings based on analysis"""
        findings = []
        
        # Database findings
        db_info = analysis['database_info']
        if db_info['credibility'] == 'High':
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': f'Recognized as {db_info["type"]} with high credibility',
                'explanation': db_info['description']
            })
        elif db_info['credibility'] == 'Low':
            findings.append({
                'type': 'warning',
                'severity': 'high',
                'text': 'Source has history of unreliable reporting',
                'explanation': db_info['description']
            })
        elif db_info['credibility'] == 'Unknown':
            findings.append({
                'type': 'info',
                'severity': 'medium',
                'text': 'Source not in credibility database',
                'explanation': 'Unable to verify source reputation'
            })
        
        # Bias findings
        if db_info['bias'] in ['Far-Left', 'Far-Right']:
            findings.append({
                'type': 'warning',
                'severity': 'medium',
                'text': f'Strong {db_info["bias"]} political bias detected',
                'explanation': 'Content may reflect ideological perspective'
            })
        
        # Technical findings
        if 'technical' in analysis and not analysis['technical'].get('error'):
            tech = analysis['technical']
            
            # Domain age
            if tech.get('age_credibility') == 'very_new':
                findings.append({
                    'type': 'warning',
                    'severity': 'high',
                    'text': 'Very new domain (less than 1 year old)',
                    'explanation': 'New sites have not established credibility'
                })
            elif tech.get('age_credibility') == 'established':
                # FIXED: Use single quotes inside f-string
                age_years = tech.get('age_years', '?')
                findings.append({
                    'type': 'positive',
                    'severity': 'positive',
                    'text': f'Established domain ({age_years} years)',
                    'explanation': 'Long-standing web presence'
                })
            
            # SSL
            if not tech.get('ssl', {}).get('valid'):
                findings.append({
                    'type': 'warning',
                    'severity': 'medium',
                    'text': 'No valid SSL certificate',
                    'explanation': 'Site may not be secure'
                })
        
        # Transparency findings
        trans = analysis.get('transparency', {})
        if trans.get('missing_elements'):
            if len(trans['missing_elements']) > 2:
                findings.append({
                    'type': 'warning',
                    'severity': 'medium',
                    'text': 'Lacks transparency indicators',
                    'explanation': ', '.join(trans['missing_elements'][:2])
                })
        
        return findings
    
    def _generate_summary(self, analysis: Dict[str, Any], score: int) -> str:
        """Generate summary of credibility analysis"""
        db_info = analysis['database_info']
        
        if db_info['credibility'] == 'High':
            summary = f"{analysis['source_name']} is a well-established {db_info['type'].lower()} with high credibility. "
        elif db_info['credibility'] == 'Medium':
            summary = f"{analysis['source_name']} is a {db_info['type'].lower()} with moderate credibility. "
        elif db_info['credibility'] == 'Low':
            summary = f"{analysis['source_name']} has questionable credibility with a history of unreliable reporting. "
        else:
            summary = f"{analysis['source_name']} is not in our credibility database. "
        
        # Add bias information if significant
        if db_info['bias'] in ['Far-Left', 'Far-Right']:
            summary += f"The source has a strong {db_info['bias']} political bias. "
        elif db_info['bias'] in ['Left', 'Right']:
            summary += f"The source leans {db_info['bias']} politically. "
        
        # Add technical assessment if available
        if 'technical' in analysis and not analysis['technical'].get('error'):
            tech = analysis['technical']
            if tech.get('age_credibility') == 'very_new':
                summary += "Warning: This is a very new website. "
            elif tech.get('age_credibility') == 'established':
                summary += "The domain has been established for several years. "
        
        # Overall assessment
        summary += f"Overall credibility score: {score}/100."
        
        return summary
    
    def _get_cached_result(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached result if available and not expired"""
        if key in self.cache:
            cached_data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
            else:
                del self.cache[key]
        return None
    
    def _cache_result(self, key: str, data: Dict[str, Any]) -> None:
        """Cache analysis result"""
        self.cache[key] = (data, time.time())
    
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
                'Bias classification',
                'AI-ENHANCED credibility insights',
                'AI-powered red flag detection'
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
                'whois': 'available' if WHOIS_AVAILABLE else 'not installed',
                'openai': 'active' if self._ai_available else 'not configured'
            },
            'ai_enhanced': self._ai_available
        })
        return info
    
    def _initialize_source_database(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive source database"""
        return {
            # Highest credibility - News Agencies
            'reuters.com': {'credibility': 'High', 'bias': 'Center', 'type': 'News Agency'},
            'apnews.com': {'credibility': 'High', 'bias': 'Center', 'type': 'News Agency'},
            'ap.org': {'credibility': 'High', 'bias': 'Center', 'type': 'News Agency'},
            
            # High credibility - Major newspapers
            'nytimes.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Newspaper'},
            'washingtonpost.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Newspaper'},
            'wsj.com': {'credibility': 'High', 'bias': 'Center-Right', 'type': 'Business'},
            'theguardian.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Newspaper'},
            'ft.com': {'credibility': 'High', 'bias': 'Center-Right', 'type': 'Business'},
            'economist.com': {'credibility': 'High', 'bias': 'Center-Right', 'type': 'Magazine'},
            
            # High credibility - Broadcast
            'bbc.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Broadcast'},
            'bbc.co.uk': {'credibility': 'High', 'bias': 'Center', 'type': 'Broadcast'},
            'npr.org': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Broadcast'},
            'pbs.org': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Broadcast'},
            
            # High credibility - International
            'dw.com': {'credibility': 'High', 'bias': 'Center', 'type': 'International'},
            'france24.com': {'credibility': 'High', 'bias': 'Center', 'type': 'International'},
            'aljazeera.com': {'credibility': 'Medium', 'bias': 'Center-Left', 'type': 'International'},
            
            # Medium credibility - Major outlets
            'cnn.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Broadcast'},
            'foxnews.com': {'credibility': 'Medium', 'bias': 'Right', 'type': 'Broadcast'},
            'msnbc.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Broadcast'},
            'abcnews.go.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Broadcast'},
            'cbsnews.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Broadcast'},
            'nbcnews.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Broadcast'},
            
            # Medium credibility - Digital
            'politico.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Digital'},
            'axios.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Digital'},
            'vox.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Digital'},
            'slate.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Digital'},
            'salon.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Digital'},
            'thehill.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Digital'},
            
            # Medium credibility - Conservative
            'nationalreview.com': {'credibility': 'Medium', 'bias': 'Right', 'type': 'Magazine'},
            'theamericanconservative.com': {'credibility': 'Medium', 'bias': 'Right', 'type': 'Magazine'},
            'reason.com': {'credibility': 'Medium', 'bias': 'Libertarian-Right', 'type': 'Magazine'},
            'dailycaller.com': {'credibility': 'Low', 'bias': 'Right', 'type': 'Digital'},
            'dailywire.com': {'credibility': 'Low', 'bias': 'Right', 'type': 'Digital'},
            
            # Low credibility - Partisan
            'breitbart.com': {'credibility': 'Low', 'bias': 'Far-Right', 'type': 'Digital'},
            'infowars.com': {'credibility': 'Low', 'bias': 'Far-Right', 'type': 'Conspiracy'},
            'naturalnews.com': {'credibility': 'Low', 'bias': 'Far-Right', 'type': 'Pseudoscience'},
            'occupydemocrats.com': {'credibility': 'Low', 'bias': 'Far-Left', 'type': 'Digital'},
            'bipartisanreport.com': {'credibility': 'Low', 'bias': 'Far-Left', 'type': 'Digital'},
            
            # Fact checking sites
            'snopes.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Fact-Checking'},
            'factcheck.org': {'credibility': 'High', 'bias': 'Center', 'type': 'Fact-Checking'},
            'politifact.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Fact-Checking'},
            
            # International sources
            'rt.com': {'credibility': 'Low', 'bias': 'Pro-Russia', 'type': 'State Media'},
            'sputniknews.com': {'credibility': 'Low', 'bias': 'Pro-Russia', 'type': 'State Media'},
            'cgtn.com': {'credibility': 'Low', 'bias': 'Pro-China', 'type': 'State Media'},
            'globaltimes.cn': {'credibility': 'Low', 'bias': 'Pro-China', 'type': 'State Media'},
        }
    
    def _get_factual_reporting_level(self, analysis: Dict[str, Any]) -> str:
        """Determine factual reporting level based on analysis"""
        db_info = analysis.get('database_info', {})
        credibility = db_info.get('credibility', 'Unknown')
        
        if credibility == 'High':
            return 'Very High'
        elif credibility == 'Medium':
            return 'Mostly Factual'
        elif credibility == 'Low':
            return 'Mixed' 
        else:
            return 'Unknown'
    
    def _get_bias_description(self, bias: str) -> str:
        """Get description for bias rating"""
        descriptions = {
            'Far-Left': 'Extreme liberal bias with agenda-driven reporting',
            'Left': 'Liberal editorial bias in story selection and reporting',
            'Center-Left': 'Slight liberal bias in reporting and story selection',
            'Center': 'Minimal bias with balanced reporting',
            'Center-Right': 'Slight conservative bias in reporting and story selection',
            'Right': 'Conservative editorial bias in story selection and reporting',
            'Far-Right': 'Extreme conservative bias with agenda-driven reporting',
            'Pro-Russia': 'Russian state-controlled media',
            'Pro-China': 'Chinese state-controlled media',
            'Libertarian-Right': 'Libertarian perspective with right-leaning bias',
            'Unknown': 'Bias orientation not determined'
        }
        return descriptions.get(bias, 'No bias information available')
