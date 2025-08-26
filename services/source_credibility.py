"""
Source Credibility Analyzer Service - AI ENHANCED BULLETPROOF VERSION
Comprehensive source credibility analysis with bulletproof AI insights
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

from services.base_analyzer import BaseAnalyzer
from services.ai_enhancement_mixin import AIEnhancementMixin

logger = logging.getLogger(__name__)


class SourceCredibilityAnalyzer(BaseAnalyzer, AIEnhancementMixin):
    """
    Analyze source credibility using multiple signals WITH BULLETPROOF AI ENHANCEMENT
    """
    
    def __init__(self):
        """Initialize the source credibility analyzer"""
        super().__init__('source_credibility')
        AIEnhancementMixin.__init__(self)
        
        # API keys from environment
        self.news_api_key = os.environ.get('NEWS_API_KEY') or os.environ.get('NEWSAPI_KEY')
        
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
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze source credibility WITH BULLETPROOF AI ENHANCEMENT
        
        Expected input:
            - url: Article URL (preferred)
            - domain: Domain name (alternative)
            - text: Article text (for AI analysis)
            - check_technical: Whether to perform technical checks (default: True)
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
                    'domain_analyzed': domain
                }
            }
            
            # BULLETPROOF AI ENHANCEMENT - Never crashes
            text = data.get('text', '')
            if text:
                logger.info("Enhancing source credibility with AI insights")
                result = self._safely_enhance_service_result(
                    result,
                    '_ai_detect_credibility_issues',
                    domain=domain,
                    content=text[:2000],
                    source_info=analysis['database_info']
                )
            
            logger.info(f"Source credibility analysis complete: {domain} -> {credibility_score}/100 ({credibility_level})")
            return result
            
        except Exception as e:
            logger.error(f"Source credibility analysis failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _extract_domain(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract domain from various input formats - ROBUST VERSION"""
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
    
    # ... [All the other methods remain the same as in the fixed version] ...
    # [Including _analyze_source_comprehensive, _check_database, etc.]
    
    def _analyze_source_comprehensive(self, domain: str, check_technical: bool = True) -> Dict[str, Any]:
        """Perform comprehensive source analysis"""
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
                
                if WHOIS_AVAILABLE:
                    domain_info = self._analyze_domain(domain)
                    technical_results.update(domain_info)
                    if domain_info.get('age_days'):
                        analysis['data_sources'].append('domain_registration')
                
                ssl_info = self._check_ssl(domain)
                technical_results['ssl'] = ssl_info
                if ssl_info.get('valid'):
                    analysis['data_sources'].append('ssl_certificate')
                
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
        
        self._cache_result(cache_key, analysis)
        return analysis
    
    # [Include all other helper methods from the fixed version...]
    # [_check_database, _get_source_name, _analyze_domain, _check_ssl, etc.]
    
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
            
            # Digital outlets
            'politico.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Digital'},
            'axios.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Digital'},
            'thehill.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Digital'},
            
            # Medium credibility outlets
            'cnn.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Broadcast'},
            'foxnews.com': {'credibility': 'Medium', 'bias': 'Right', 'type': 'Broadcast'},
            'msnbc.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Broadcast'},
            
            # Fact checking sites
            'snopes.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Fact-Checking'},
            'factcheck.org': {'credibility': 'High', 'bias': 'Center', 'type': 'Fact-Checking'},
            'politifact.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Fact-Checking'},
        }
    
    # [All other helper methods would be included here - truncated for space]
    # [_check_database, _get_source_name, _analyze_domain, _check_ssl, etc.]
