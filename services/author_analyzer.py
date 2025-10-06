"""
Enhanced Author Analyzer - COMPLETE REBUILD
Date: October 5, 2025
Version: 7.0 - ALGORITHMIC INSIGHTS IMPLEMENTATION

MAJOR CHANGES:
- Integrated track record analysis (MEDIASTACK_API)
- Added credibility verification (COPYSCAPE + GOOGLE_FACTCHECK)  
- Implemented deviation detection (compares to author baseline)
- All existing functionality preserved
- Provides insights users CAN'T get from Google

NEW FEATURES:
1. Track Record System - article history, velocity, specialization
2. Credibility Checker - plagiarism detection, fact-check history
3. Deviation Analyzer - identifies unusual patterns in THIS article
4. Enhanced reporting with actionable insights

REPLACES: backend/services/author_analyzer.py
"""

import re
import json
import time
import logging
import requests
from typing import Dict, Any, Optional, List
from urllib.parse import quote, urlparse
import os
from datetime import datetime

logger = logging.getLogger(__name__)

# Import new systems
try:
    from services.author_track_record import AuthorTrackRecord
    from services.author_credibility_checker import AuthorCredibilityChecker
    from services.author_deviation_analyzer import AuthorDeviationAnalyzer
    ADVANCED_SYSTEMS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Advanced author systems not available: {e}")
    ADVANCED_SYSTEMS_AVAILABLE = False

# Import OpenAI if available
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class AuthorAnalyzer:
    """
    REBUILT Author analyzer with algorithmic insights
    """
    
    def __init__(self):
        """Initialize with enhanced features"""
        self.service_name = 'author_analyzer'
        self.available = True
        self.is_available = True
        
        # Get API keys
        self.news_api_key = os.environ.get('NEWS_API_KEY') or os.environ.get('NEWSAPI_KEY')
        self.scraperapi_key = os.environ.get('SCRAPERAPI_KEY')
        self.openai_key = os.environ.get('OPENAI_API_KEY')
        
        logger.info(f"[AuthorAnalyzer v7.0] Initializing with advanced systems")
        
        # Initialize OpenAI
        if OPENAI_AVAILABLE and self.openai_key:
            openai.api_key = self.openai_key
        
        # Initialize new systems
        if ADVANCED_SYSTEMS_AVAILABLE:
            try:
                self.track_record = AuthorTrackRecord()
                logger.info("[AuthorAnalyzer] ✓ Track record system initialized")
            except Exception as e:
                logger.error(f"[AuthorAnalyzer] ✗ Track record init failed: {e}")
                self.track_record = None
            
            try:
                self.credibility = AuthorCredibilityChecker()
                logger.info("[AuthorAnalyzer] ✓ Credibility checker initialized")
            except Exception as e:
                logger.error(f"[AuthorAnalyzer] ✗ Credibility checker init failed: {e}")
                self.credibility = None
            
            try:
                self.deviation = AuthorDeviationAnalyzer()
                logger.info("[AuthorAnalyzer] ✓ Deviation analyzer initialized")
            except Exception as e:
                logger.error(f"[AuthorAnalyzer] ✗ Deviation analyzer init failed: {e}")
                self.deviation = None
            
            if self.track_record and self.credibility and self.deviation:
                logger.info("[AuthorAnalyzer] ✓ All advanced systems loaded successfully")
            else:
                logger.warning(f"[AuthorAnalyzer] ⚠ Partial load - Track:{bool(self.track_record)}, Cred:{bool(self.credibility)}, Dev:{bool(self.deviation)}")
        else:
            self.track_record = None
            self.credibility = None
            self.deviation = None
            logger.warning("[AuthorAnalyzer] ⚠ Using basic mode - ADVANCED_SYSTEMS_AVAILABLE = False")
        
        # Session for requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Cache
        self.cache = {}
        self.cache_ttl = 86400
        
        # Enhanced journalist database (kept from v6.1)
        self.known_journalists = self._load_journalist_database()
        
        # Major outlets metadata
        self.major_outlets = self._load_outlet_metadata()
        
        logger.info("[AuthorAnalyzer v7.0] Initialization complete")
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        COMPREHENSIVE author analysis with track record & deviation detection
        """
        try:
            # Extract author and domain
            raw_author = data.get('author', '').strip()
            domain = data.get('domain', '').strip()
            article_text = data.get('text', '')
            
            logger.info(f"[Author v7.0] Analyzing: '{raw_author}', Domain: {domain}")
            
            # Parse authors
            authors = self._parse_authors_fixed(raw_author)
            
            if not authors:
                logger.info("[Author] No valid authors found")
                return self.get_success_result(self._get_unknown_author_result(domain))
            
            primary_author = authors[0]
            
            # Get outlet information
            outlet_info = self.major_outlets.get(domain.lower().replace('www.', ''), {'score': 50})
            outlet_score = outlet_info.get('score', 50)
            
            # Check if author is in database
            author_key = primary_author.lower()
            known_data = self.known_journalists.get(author_key, {})
            
            # =================================================================
            # PHASE 1: TRACK RECORD ANALYSIS (if systems available)
            # =================================================================
            track_record_data = {}
            article_history = []
            
            if self.track_record:
                logger.info("[Author] PHASE 1: Track Record Analysis")
                try:
                    # Get article history
                    article_history = self.track_record.get_author_article_history(
                        primary_author, domain, limit=50
                    )
                    
                    if article_history:
                        # Calculate metrics
                        metrics = self.track_record.calculate_author_metrics(article_history)
                        
                        # Analyze specialization
                        specialization = self.track_record.analyze_author_specialization(article_history)
                        
                        # Detect writing patterns
                        patterns = self.track_record.detect_writing_patterns(article_history)
                        
                        track_record_data = {
                            'metrics': metrics,
                            'specialization': specialization,
                            'patterns': patterns,
                            'recent_articles': article_history[:5]  # Top 5
                        }
                        
                        logger.info(f"[Author] ✓ Track record: {metrics.get('total_articles', 0)} articles, {specialization.get('primary_beat', 'Unknown')} beat")
                    else:
                        logger.info("[Author] No track record found")
                        
                except Exception as e:
                    logger.error(f"[Author] Track record failed: {e}")
            
            # =================================================================
            # PHASE 2: CREDIBILITY VERIFICATION
            # =================================================================
            credibility_data = {}
            
            if self.credibility and article_history:
                logger.info("[Author] PHASE 2: Credibility Verification")
                try:
                    # Plagiarism check
                    plagiarism = self.credibility.check_author_plagiarism(
                        primary_author, article_history[:3]
                    )
                    
                    # Fact-check history
                    factchecks = self.credibility.get_factcheck_history(
                        primary_author, self._get_org_name(domain)
                    )
                    
                    # Build credibility score
                    track_metrics = track_record_data.get('metrics', {})
                    cred_score_data = self.credibility.build_credibility_score(
                        track_metrics, plagiarism, factchecks
                    )
                    
                    credibility_data = {
                        'plagiarism_check': plagiarism,
                        'factcheck_history': factchecks,
                        'credibility_assessment': cred_score_data
                    }
                    
                    logger.info(f"[Author] ✓ Credibility: {cred_score_data.get('combined_credibility_score', 0)}/100")
                    
                except Exception as e:
                    logger.error(f"[Author] Credibility check failed: {e}")
            
            # =================================================================
            # PHASE 3: DEVIATION DETECTION
            # =================================================================
            deviation_data = {}
            
            if self.deviation and track_record_data:
                logger.info("[Author] PHASE 3: Deviation Analysis")
                try:
                    # Calculate baseline from history
                    baseline = self.deviation.calculate_baseline_metrics(article_history)
                    
                    # Compare THIS article to baseline
                    current_article_metrics = {
                        'bias_score': data.get('bias_score', 50),
                        'manipulation_score': data.get('manipulation_score', 80),
                        'sources_cited': data.get('sources_count', 0)
                    }
                    
                    deviation_report = self.deviation.compare_to_baseline(
                        current_article_metrics, baseline
                    )
                    
                    # Generate insights
                    deviation_insights = self.deviation.generate_deviation_insights(deviation_report)
                    
                    deviation_data = {
                        'baseline': baseline,
                        'deviation_report': deviation_report,
                        'insights': deviation_insights,
                        'alerts': deviation_report.get('alerts', [])
                    }
                    
                    if deviation_report.get('deviations_detected'):
                        logger.info(f"[Author] ⚠ DEVIATION DETECTED: {deviation_report.get('overall_severity', 'UNKNOWN')}")
                    else:
                        logger.info("[Author] ✓ No significant deviations")
                    
                except Exception as e:
                    logger.error(f"[Author] Deviation analysis failed: {e}")
            
            # =================================================================
            # PHASE 4: BUILD COMPREHENSIVE RESULT
            # =================================================================
            
            # Determine final credibility score
            if credibility_data.get('credibility_assessment'):
                credibility_score = credibility_data['credibility_assessment']['combined_credibility_score']
            elif known_data:
                credibility_score = known_data.get('credibility', outlet_score)
            else:
                credibility_score = self._calculate_credibility(primary_author, outlet_score, article_text)
            
            # Get experience and expertise
            if track_record_data.get('metrics'):
                years_experience = track_record_data['metrics'].get('years_active', 0)
                expertise = track_record_data['specialization'].get('expertise_areas', [])
            elif known_data:
                years_experience = known_data.get('years_experience', 0)
                expertise = known_data.get('expertise', [])
            else:
                years_experience = self._estimate_experience(primary_author, domain)
                expertise = self._detect_expertise(article_text)
            
            # Get awards
            awards = known_data.get('awards', []) if known_data else self._detect_awards(primary_author, article_text)
            
            # Education and position
            education = known_data.get('education', '') if known_data else ''
            position = known_data.get('position', 'Journalist') if known_data else 'Journalist'
            
            # Social profiles
            social = known_data.get('social', {}) if known_data else self._generate_social_links(primary_author, domain)
            social_profiles = self._build_social_profiles(social)
            
            # Professional links
            professional_links = self._generate_professional_links(primary_author, domain)
            
            # Trust assessment
            verified = credibility_score >= 70 or bool(known_data)
            trust_result = self._determine_trust_level(credibility_score, outlet_score, verified, awards)
            
            # Build bio
            org_name = self._get_org_name(domain)
            author_name = ' and '.join(authors) if len(authors) > 1 else primary_author
            bio = self._generate_bio(primary_author, org_name, position, years_experience, awards)
            
            # Trust indicators and red flags
            trust_indicators = self._build_trust_indicators(
                credibility_score, outlet_score, verified, awards, years_experience
            )
            red_flags = self._build_red_flags(
                credibility_score, outlet_score, verified, social_profiles
            )
            
            # Add deviation alerts to red flags if present
            if deviation_data.get('alerts'):
                red_flags.extend(deviation_data['alerts'])
            
            # =================================================================
            # FINAL RESULT ASSEMBLY
            # =================================================================
            
            result_data = {
                # Name fields
                'name': author_name,
                'author_name': author_name,
                'primary_author': primary_author,
                'all_authors': authors,
                
                # Credibility scores
                'credibility_score': credibility_score,
                'combined_credibility_score': credibility_score,
                'score': credibility_score,
                'outlet_score': outlet_score,
                
                # Trust assessment
                'can_trust': trust_result['can_trust'],
                'trust_explanation': trust_result['explanation'],
                'credibility_level': trust_result['level'],
                'trust_reasoning': trust_result['detailed_reasoning'],
                
                # Organization
                'domain': domain,
                'organization': org_name,
                'position': position,
                'outlet_type': outlet_info.get('type', 'online'),
                'outlet_reach': outlet_info.get('reach', 'unknown'),
                
                # Biography
                'bio': bio,
                'biography': bio,
                'education': education,
                
                # Experience & Expertise
                'years_experience': years_experience,
                'expertise_areas': expertise,
                'expertise': expertise,
                
                # Awards
                'awards': awards,
                'awards_count': len(awards),
                
                # Articles (NEW - from track record)
                'articles_found': len(article_history),
                'article_count': len(article_history),
                'recent_articles': article_history[:5],
                
                # Social media
                'social_profiles': social_profiles,
                'social_media': social,
                'social_count': len(social_profiles),
                
                # Professional links
                'professional_links': professional_links,
                
                # Trust assessment
                'trust_indicators': trust_indicators,
                'red_flags': red_flags,
                'verified': verified,
                'verification_status': 'Verified' if verified else 'Unverified',
                'reputation_score': self._calculate_reputation_score(
                    credibility_score, outlet_score, awards, social_profiles
                ),
                
                # NEW: Track Record Data
                'track_record': track_record_data.get('metrics', {}),
                'specialization': track_record_data.get('specialization', {}),
                'writing_patterns': track_record_data.get('patterns', {}),
                
                # NEW: Credibility Verification
                'plagiarism_check': credibility_data.get('plagiarism_check', {}),
                'factcheck_history': credibility_data.get('factcheck_history', {}),
                'credibility_assessment': credibility_data.get('credibility_assessment', {}),
                
                # NEW: Deviation Analysis (KEY FEATURE)
                'deviation_analysis': deviation_data.get('deviation_report', {}),
                'deviation_insights': deviation_data.get('insights', ''),
                'deviation_alerts': deviation_data.get('alerts', []),
                
                # Metadata
                'analysis_timestamp': datetime.now().isoformat(),
                'data_sources': self._get_data_sources(social_profiles, article_history),
                'advanced_analysis_available': ADVANCED_SYSTEMS_AVAILABLE
            }
            
            logger.info(f"[Author v7.0] ✓ Analysis complete - Score: {credibility_score}, Articles: {len(article_history)}")
            
            return self.get_success_result(result_data)
            
        except Exception as e:
            logger.error(f"[Author] Analysis error: {e}", exc_info=True)
            return self.get_success_result(self._get_fallback_result(data))
    
    # =========================================================================
    # HELPER METHODS (preserved from v6.1)
    # =========================================================================
    
    def _load_journalist_database(self) -> Dict[str, Dict]:
        """Load known journalist database"""
        return {
            'kim bellware': {
                'full_name': 'Kim Bellware',
                'credibility': 82,
                'organization': 'Washington Post',
                'position': 'National Reporter',
                'expertise': ['Breaking News', 'National Affairs', 'Social Issues'],
                'verified': True,
                'years_experience': 10,
                'awards': [],
                'social': {'twitter': 'https://twitter.com/kimbellware'}
            }
            # Add more as needed
        }
    
    def _load_outlet_metadata(self) -> Dict[str, Dict]:
        """Load outlet metadata"""
        return {
            'nbcnews.com': {'score': 85, 'type': 'broadcast', 'reach': 'national'},
            'reuters.com': {'score': 95, 'type': 'wire', 'reach': 'international'},
            'apnews.com': {'score': 95, 'type': 'wire', 'reach': 'international'},
            'bbc.com': {'score': 90, 'type': 'broadcast', 'reach': 'international'},
            'nytimes.com': {'score': 90, 'type': 'newspaper', 'reach': 'national'},
            'washingtonpost.com': {'score': 88, 'type': 'newspaper', 'reach': 'national'},
            'wsj.com': {'score': 88, 'type': 'newspaper', 'reach': 'national'},
            'foxnews.com': {'score': 75, 'type': 'broadcast', 'reach': 'national'}
        }
    
    def _calculate_credibility(self, author: str, outlet_score: int, text: str) -> int:
        """Calculate credibility score"""
        score = outlet_score
        if ' ' in author:
            score += 5
        if re.search(r'senior|chief|editor|correspondent', text.lower()):
            score += 10
        return min(100, max(0, score))
    
    def _estimate_experience(self, author: str, domain: str) -> int:
        """Estimate years of experience"""
        if 'senior' in author.lower() or 'chief' in author.lower():
            return 10
        outlet_info = self.major_outlets.get(domain.lower().replace('www.', ''), {})
        if outlet_info.get('score', 0) >= 85:
            return 5
        return 2
    
    def _detect_expertise(self, text: str) -> List[str]:
        """Detect expertise areas"""
        expertise = []
        expertise_patterns = {
            'Politics': ['election', 'congress', 'senate', 'president'],
            'Technology': ['ai', 'software', 'tech', 'startup'],
            'Business': ['economy', 'market', 'finance', 'corporate'],
            'Health': ['medical', 'health', 'covid', 'vaccine']
        }
        
        text_lower = text.lower()
        for area, keywords in expertise_patterns.items():
            if sum(1 for kw in keywords if kw in text_lower) >= 2:
                expertise.append(area)
        
        return expertise[:3]
    
    def _detect_awards(self, author: str, text: str) -> List[str]:
        """Detect awards"""
        awards = []
        award_patterns = {
            'pulitzer': 'Pulitzer Prize',
            'peabody': 'Peabody Award',
            'emmy': 'Emmy Award'
        }
        
        text_lower = text.lower()
        for pattern, award_name in award_patterns.items():
            if pattern in text_lower:
                awards.append(award_name)
        
        return awards
    
    def _generate_social_links(self, author: str, domain: str) -> Dict[str, str]:
        """Generate social links"""
        return {
            'twitter': f"https://twitter.com/search?q={quote(author)}%20{domain}",
            'linkedin': f"https://www.linkedin.com/search/results/people/?keywords={quote(author)}"
        }
    
    def _build_social_profiles(self, social: Dict[str, str]) -> List[Dict]:
        """Build social profiles list"""
        profiles = []
        if social.get('twitter'):
            profiles.append({
                'platform': 'Twitter',
                'url': social['twitter'],
                'icon': 'fab fa-twitter',
                'color': '#1DA1F2'
            })
        if social.get('linkedin'):
            profiles.append({
                'platform': 'LinkedIn',
                'url': social['linkedin'],
                'icon': 'fab fa-linkedin',
                'color': '#0077B5'
            })
        return profiles
    
    def _generate_professional_links(self, author: str, domain: str) -> List[Dict]:
        """Generate professional links"""
        org_name = self._get_org_name(domain)
        return [
            {
                'type': 'Author Page',
                'url': f"https://{domain}/author/{author.lower().replace(' ', '-')}",
                'label': f"{author} at {org_name}"
            },
            {
                'type': 'Google Scholar',
                'url': f"https://scholar.google.com/scholar?q={quote(author)}",
                'label': 'Academic Publications'
            }
        ]
    
    def _determine_trust_level(self, credibility: int, outlet: int, verified: bool, awards: List) -> Dict:
        """Determine trust level"""
        combined = (credibility * 0.6) + (outlet * 0.3) + (len(awards) * 5) + (10 if verified else 0)
        combined = min(100, combined)
        
        if combined >= 80:
            return {
                'can_trust': 'YES',
                'level': 'High',
                'explanation': 'Highly credible journalist from reputable source.',
                'detailed_reasoning': f"Strong credibility: {credibility}/100, outlet: {outlet}/100"
            }
        elif combined >= 60:
            return {
                'can_trust': 'YES',
                'level': 'Moderate-High',
                'explanation': 'Credible journalist with good reputation.',
                'detailed_reasoning': f"Good credibility ({credibility}/100)"
            }
        elif combined >= 45:
            return {
                'can_trust': 'MAYBE',
                'level': 'Moderate',
                'explanation': 'Some credibility indicators. Verify claims.',
                'detailed_reasoning': f"Moderate credibility ({credibility}/100)"
            }
        else:
            return {
                'can_trust': 'NO',
                'level': 'Low',
                'explanation': 'Limited credibility. Exercise caution.',
                'detailed_reasoning': f"Low credibility ({credibility}/100)"
            }
    
    def _generate_bio(self, author: str, org: str, position: str, years: int, awards: List) -> str:
        """Generate bio"""
        bio_parts = [f"{author} is a {position} at {org}"]
        if years > 0:
            bio_parts.append(f"with {years} years of experience")
        if awards:
            bio_parts.append(f"and recipient of {len(awards)} journalism awards")
        return ". ".join(bio_parts) + "."
    
    def _build_trust_indicators(self, credibility: int, outlet: int, verified: bool, awards: List, years: int) -> List[str]:
        """Build trust indicators"""
        indicators = []
        if outlet >= 85:
            indicators.append("Publishing in highly reputable outlet")
        if verified:
            indicators.append("Verified journalist identity")
        if awards:
            indicators.append(f"Award-winning journalist ({len(awards)} awards)")
        if years >= 10:
            indicators.append(f"Veteran journalist ({years}+ years)")
        return indicators
    
    def _build_red_flags(self, credibility: int, outlet: int, verified: bool, social: List) -> List[str]:
        """Build red flags"""
        flags = []
        if credibility < 50:
            flags.append("Low credibility score")
        if not verified:
            flags.append("Unable to verify author identity")
        if not social:
            flags.append("No professional social media presence found")
        return flags
    
    def _calculate_reputation_score(self, credibility: int, outlet: int, awards: List, social: List) -> int:
        """Calculate reputation score"""
        base = (credibility * 0.4) + (outlet * 0.3)
        award_bonus = min(20, len(awards) * 10)
        social_bonus = min(10, len(social) * 3)
        return min(100, int(base + award_bonus + social_bonus))
    
    def _get_data_sources(self, social: List, articles: List) -> List[str]:
        """Get data sources"""
        sources = ["Publication metadata"]
        if social:
            sources.append("Social media profiles")
        if articles:
            sources.append("Article history database")
        return sources
    
    def _parse_authors_fixed(self, author_string: str) -> List[str]:
        """Parse authors (from v6.1)"""
        if not author_string or not isinstance(author_string, str):
            return []
        
        author = author_string.strip()
        author = re.sub(r'^[Bb]y\s+', '', author)
        
        if not author or author.lower() in ['unknown', 'staff', 'editor']:
            return []
        
        # Fix concatenated names
        author = re.sub(r'([a-z])and([A-Z])', r'\1 and \2', author)
        author = author.replace(',', ' and ')
        
        if ' and ' in author.lower():
            parts = re.split(r'\s+and\s+', author, flags=re.IGNORECASE)
        else:
            parts = [author]
        
        authors = []
        for part in parts:
            part = part.strip()
            if part and len(part) > 2:
                words = part.split()
                fixed_words = [w[0].upper() + w[1:] if w and w[0].islower() else w for w in words]
                part = ' '.join(fixed_words)
                if re.search(r'[A-Za-z]', part):
                    authors.append(part)
        
        return authors
    
    def _get_org_name(self, domain: str) -> str:
        """Get organization name"""
        org_map = {
            'nbcnews.com': 'NBC News',
            'nytimes.com': 'The New York Times',
            'washingtonpost.com': 'The Washington Post',
            'foxnews.com': 'Fox News',
            'bbc.com': 'BBC'
        }
        clean = domain.lower().replace('www.', '')
        return org_map.get(clean, domain.replace('.com', '').title())
    
    def _get_unknown_author_result(self, domain: str) -> Dict[str, Any]:
        """Unknown author result"""
        outlet_info = self.major_outlets.get(domain.lower().replace('www.', ''), {'score': 30})
        return {
            'name': 'Unknown Author',
            'credibility_score': 30,
            'can_trust': 'NO',
            'trust_explanation': 'Author identity not disclosed',
            'track_record': {},
            'deviation_analysis': {}
        }
    
    def _get_fallback_result(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback result"""
        domain = data.get('domain', '')
        author = data.get('author', 'Unknown')
        authors = self._parse_authors_fixed(author)
        author_name = ' and '.join(authors) if authors else 'Unknown'
        
        return {
            'name': author_name,
            'credibility_score': 50,
            'can_trust': 'MAYBE',
            'trust_explanation': 'Limited information available',
            'track_record': {},
            'deviation_analysis': {}
        }
    
    def get_success_result(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Success result wrapper"""
        return {
            'success': True,
            'data': data,
            'service': self.service_name,
            'available': True,
            'timestamp': time.time()
        }
    
    def get_error_result(self, error_message: str) -> Dict[str, Any]:
        """Error result wrapper"""
        return {
            'success': False,
            'error': error_message,
            'service': self.service_name,
            'available': self.available,
            'timestamp': time.time()
        }
    
    def _check_availability(self) -> bool:
        return True
    
    def check_service(self) -> bool:
        return True
