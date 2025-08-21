"""
Source Credibility Service - AI ENHANCED VERSION
Comprehensive source credibility analysis with database, domain verification, and reputation tracking
NOW WITH AI ENHANCEMENT for deeper insights
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
from services.ai_enhancement_mixin import AIEnhancementMixin

logger = logging.getLogger(__name__)


class SourceCredibility(BaseAnalyzer, AIEnhancementMixin):
    """
    Enhanced source credibility analyzer with comprehensive database,
    domain verification, SSL checking, real-time analysis, and AI enhancement
    """
    
    def __init__(self):
        """Initialize source credibility analyzer with AI enhancement"""
        # Initialize base analyzer
        super().__init__('source_credibility')
        
        # Initialize AI enhancement
        AIEnhancementMixin.__init__(self)
        
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
        
        logger.info(f"SourceCredibility initialized with {len(self.source_database)} sources and AI enhancement: {self._ai_available}")
    
    def _check_availability(self) -> bool:
        """Service is always available"""
        return True
    
    def _extract_domain(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract domain from data (URL or domain field)"""
        # Check for direct domain
        if 'domain' in data and data['domain']:
            return data['domain'].lower().replace('www.', '')
        
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
            
            # Build base results
            base_results = {
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
            
            # AI ENHANCEMENT - Add deeper insights
            if self._ai_available:
                logger.info(f"Enhancing source credibility analysis with AI for {domain}")
                
                # Prepare data for AI analysis
                article_data = {
                    'title': data.get('title', ''),
                    'text': data.get('text', ''),
                    'author': data.get('author', ''),
                    'source': domain
                }
                
                # Get AI credibility insights
                ai_credibility = self._ai_analyze_credibility(
                    source_info={
                        'domain': domain,
                        'type': analysis['database_info']['type'],
                        'credibility_rating': analysis['database_info']['credibility'],
                        'bias': analysis['database_info']['bias'],
                        'age_years': technical_data.get('age_years'),
                        'ssl_valid': technical_data.get('ssl', {}).get('valid', False)
                    },
                    article_data=article_data
                )
                
                # Merge AI enhancements
                if ai_credibility:
                    base_results['data'] = self._merge_ai_enhancements(
                        base_results['data'],
                        ai_credibility,
                        'credibility_analysis'
                    )
                    
                    # Add AI findings if significant
                    if ai_credibility.get('red_flags'):
                        for flag in ai_credibility['red_flags'][:2]:
                            findings.append({
                                'type': 'ai_red_flag',
                                'text': flag,
                                'severity': 'high',
                                'explanation': 'AI-detected credibility concern'
                            })
                    
                    # Update summary with AI insights
                    if ai_credibility.get('overall_assessment'):
                        base_results['data']['summary'] += f" AI assessment: {ai_credibility['overall_assessment']}"
                    
                    # Adjust score if AI found serious issues
                    if ai_credibility.get('red_flags') and len(ai_credibility['red_flags']) > 2:
                        base_results['data']['score'] = max(0, base_results['data']['score'] - 10)
                        base_results['data']['credibility_score'] = base_results['data']['score']
                        base_results['data']['level'] = self._get_credibility_level(base_results['data']['score'])
                
                # Log AI enhancement
                base_results['metadata']['ai_enhanced'] = True
                logger.info(f"AI enhancement completed for {domain}")
            else:
                base_results['metadata']['ai_enhanced'] = False
            
            return base_results
            
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
    
    def _get_source_name(self, domain: str) -> str:
        """Get human-readable source name from domain"""
        # Remove common suffixes
        name = domain.replace('.com', '').replace('.org', '').replace('.net', '')
        name = name.replace('.co.uk', '').replace('.edu', '').replace('.gov', '')
        
        # Handle special cases
        special_cases = {
            'nytimes': 'New York Times',
            'wsj': 'Wall Street Journal',
            'washingtonpost': 'Washington Post',
            'bbc': 'BBC',
            'cnn': 'CNN',
            'foxnews': 'Fox News',
            'msnbc': 'MSNBC',
            'npr': 'NPR',
            'apnews': 'Associated Press',
            'reuters': 'Reuters'
        }
        
        if name in special_cases:
            return special_cases[name]
        
        # Capitalize first letter of each word
        return ' '.join(word.capitalize() for word in name.split('.'))
    
    def _analyze_domain(self, domain: str) -> Dict[str, Any]:
        """Analyze domain registration and age"""
        try:
            w = whois.whois(domain)
            
            # Extract creation date
            creation_date = None
            if w.creation_date:
                if isinstance(w.creation_date, list):
                    creation_date = w.creation_date[0]
                else:
                    creation_date = w.creation_date
            
            # Calculate age
            if creation_date:
                age = datetime.now() - creation_date
                age_days = age.days
                age_years = age_days / 365.25
                
                # Determine credibility based on age
                if age_years >= 5:
                    age_credibility = 'established'
                elif age_years >= 2:
                    age_credibility = 'moderate'
                elif age_years >= 1:
                    age_credibility = 'new'
                else:
                    age_credibility = 'very_new'
            else:
                age_days = None
                age_years = None
                age_credibility = 'unknown'
            
            return {
                'creation_date': creation_date.isoformat() if creation_date else None,
                'age_days': age_days,
                'age_years': round(age_years, 1) if age_years else None,
                'age_credibility': age_credibility,
                'registrar': getattr(w, 'registrar', None)
            }
            
        except Exception as e:
            logger.warning(f"Domain analysis failed for {domain}: {e}")
            return {
                'error': str(e),
                'age_credibility': 'unknown'
            }
    
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
        """Analyze website structure for credibility indicators"""
        try:
            response = self.session.get(f'https://{domain}', timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for common credibility indicators
            has_about = bool(soup.find('a', href=re.compile(r'/about|about-us|who-we-are', re.I)))
            has_contact = bool(soup.find('a', href=re.compile(r'/contact|contact-us', re.I)))
            has_privacy = bool(soup.find('a', href=re.compile(r'/privacy|privacy-policy', re.I)))
            has_terms = bool(soup.find('a', href=re.compile(r'/terms|terms-of-service', re.I)))
            
            # Check for author bylines
            has_authors = bool(soup.find(class_=re.compile(r'author|byline|writer', re.I)))
            
            # Check for date stamps
            has_dates = bool(soup.find(class_=re.compile(r'date|time|published', re.I)))
            
            return {
                'has_about_page': has_about,
                'has_contact_page': has_contact,
                'has_privacy_policy': has_privacy,
                'has_terms_of_service': has_terms,
                'has_author_bylines': has_authors,
                'has_date_stamps': has_dates,
                'transparency_score': sum([has_about, has_contact, has_privacy, has_terms, has_authors, has_dates]) * 100 / 6
            }
            
        except Exception as e:
            logger.warning(f"Website structure analysis failed for {domain}: {e}")
            return {
                'error': str(e),
                'transparency_score': 0
            }
    
    def _analyze_reputation(self, domain: str) -> Dict[str, Any]:
        """Analyze source reputation through news mentions"""
        if not self.news_api_key:
            return {
                'api_available': False,
                'mentions_found': False
            }
        
        try:
            # Search for mentions of the domain in news
            url = 'https://newsapi.org/v2/everything'
            params = {
                'q': f'"{domain}"',
                'apiKey': self.news_api_key,
                'pageSize': 10,
                'sortBy': 'relevancy'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('status') == 'ok':
                articles = data.get('articles', [])
                
                # Analyze sentiment of mentions
                positive_keywords = ['reliable', 'trusted', 'credible', 'accurate', 'award']
                negative_keywords = ['fake', 'misleading', 'false', 'disinformation', 'bias']
                
                positive_mentions = 0
                negative_mentions = 0
                
                for article in articles:
                    title = (article.get('title', '') + ' ' + article.get('description', '')).lower()
                    
                    if any(keyword in title for keyword in positive_keywords):
                        positive_mentions += 1
                    if any(keyword in title for keyword in negative_keywords):
                        negative_mentions += 1
                
                return {
                    'api_available': True,
                    'mentions_found': len(articles) > 0,
                    'total_mentions': len(articles),
                    'positive_mentions': positive_mentions,
                    'negative_mentions': negative_mentions,
                    'reputation_score': (positive_mentions - negative_mentions) * 10 + 50
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
                findings.append({
                    'type': 'positive',
                    'severity': 'positive',
                    'text': f'Established domain ({tech.get("age_years", "?")} years)',
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
            'reason.com': {'credibility': 'Medium', 'bias': 'Libertarian', 'type': 'Magazine'},
            'thefederalist.com': {'credibility': 'Low', 'bias': 'Right', 'type': 'Digital'},
            
            # Medium credibility - Progressive
            'motherjones.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Magazine'},
            'thenation.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Magazine'},
            'commondreams.org': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Digital'},
            
            # Low credibility sources
            'breitbart.com': {'credibility': 'Low', 'bias': 'Far-Right', 'type': 'Digital'},
            'infowars.com': {'credibility': 'Low', 'bias': 'Far-Right', 'type': 'Digital'},
            'naturalnews.com': {'credibility': 'Low', 'bias': 'Far-Right', 'type': 'Digital'},
            'occupydemocrats.com': {'credibility': 'Low', 'bias': 'Far-Left', 'type': 'Digital'},
            'bipartisanreport.com': {'credibility': 'Low', 'bias': 'Far-Left', 'type': 'Digital'},
            
            # Fact-checking sites
            'snopes.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Fact-Check'},
            'factcheck.org': {'credibility': 'High', 'bias': 'Center', 'type': 'Fact-Check'},
            'politifact.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Fact-Check'},
            
            # State media
            'rt.com': {'credibility': 'Low', 'bias': 'Far-Right', 'type': 'State Media'},
            'sputniknews.com': {'credibility': 'Low', 'bias': 'Far-Right', 'type': 'State Media'},
            'xinhuanet.com': {'credibility': 'Low', 'bias': 'Far-Left', 'type': 'State Media'},
            'presstv.com': {'credibility': 'Low', 'bias': 'Far-Left', 'type': 'State Media'},
        }
