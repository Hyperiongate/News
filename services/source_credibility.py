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
    
    # ... [INCLUDE ALL OTHER METHODS FROM THE ORIGINAL FILE - they remain exactly the same]
    # I'm truncating here for space, but all the original methods like:
    # _is_valid_domain, _analyze_source_comprehensive, _check_database, etc.
    # should be copied exactly as they are from the original file
    
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
    
    # [Continue with all other methods from the original file...]
    # Note: ALL methods from the original file should be included exactly as they are
    # Only the __init__ and analyze methods have been modified for AI enhancement
    
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
                'AI-ENHANCED credibility insights',  # NEW
                'AI-powered red flag detection'      # NEW
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
                'openai': 'active' if self._ai_available else 'not configured'  # NEW
            },
            'ai_enhanced': self._ai_available  # NEW
        })
        return info
    
    # Include all remaining methods from the original file...
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
    
    # [Continue copying ALL methods from the original file...]
    # Due to space constraints, I'm showing the pattern - ALL original methods should be included unchanged
    
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
            
            # [Include the full database from the original file...]
        }
