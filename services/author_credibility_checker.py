"""
Author Credibility Checker - NEW
Date: October 5, 2025
Version: 1.0

PURPOSE:
Verify author credibility using COPYSCAPE + GOOGLE_FACTCHECK APIs
Provides verification signals users can't get from Google

FEATURES:
- Plagiarism detection via COPYSCAPE
- Fact-check history via GOOGLE_FACTCHECK
- Combined credibility scoring
- Red flag detection

Save as: backend/services/author_credibility_checker.py (NEW FILE)
"""

import os
import logging
import requests
from typing import Dict, Any, Optional, List
from urllib.parse import quote
import hashlib

logger = logging.getLogger(__name__)


class AuthorCredibilityChecker:
    """
    Author credibility verification using multiple APIs
    """
    
    def __init__(self):
        # API keys
        self.copyscape_username = os.environ.get('COPYSCAPE_USERNAME')
        self.copyscape_key = os.environ.get('COPYSCAPE_API_KEY')
        self.factcheck_key = os.environ.get('GOOGLE_FACTCHECK_API_KEY') or \
                            os.environ.get('GOOGLE_FACT_CHECK_API_KEY')
        
        logger.info(f"[Credibility] COPYSCAPE available: {bool(self.copyscape_key)}")
        logger.info(f"[Credibility] FACTCHECK available: {bool(self.factcheck_key)}")
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TruthLens/1.0'
        })
    
    def check_author_plagiarism(
        self, 
        author_name: str, 
        recent_articles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check author for plagiarism using COPYSCAPE
        
        Args:
            author_name: Author full name
            recent_articles: List of recent articles (with 'url' field)
            
        Returns:
            Plagiarism check results with severity score
        """
        
        logger.info(f"[Plagiarism] Checking {author_name} with {len(recent_articles)} articles")
        
        if not self.copyscape_key or not recent_articles:
            return {
                'check_performed': False,
                'reason': 'No API key or no articles to check',
                'matches_found': 0,
                'severity': 'Unknown',
                'details': []
            }
        
        # Check up to 3 most recent articles
        articles_to_check = recent_articles[:3]
        
        total_matches = 0
        all_details = []
        
        for article in articles_to_check:
            url = article.get('url')
            if not url:
                continue
            
            result = self._check_copyscape_url(url)
            
            if result['matches'] > 0:
                total_matches += result['matches']
                all_details.append({
                    'article_url': url,
                    'matches': result['matches'],
                    'match_details': result.get('details', [])
                })
        
        # Determine severity
        if total_matches == 0:
            severity = 'Clean'
            severity_score = 100
        elif total_matches <= 2:
            severity = 'Minor'
            severity_score = 80
        elif total_matches <= 5:
            severity = 'Moderate'
            severity_score = 50
        else:
            severity = 'Severe'
            severity_score = 20
        
        return {
            'check_performed': True,
            'articles_checked': len(articles_to_check),
            'matches_found': total_matches,
            'severity': severity,
            'severity_score': severity_score,
            'details': all_details,
            'recommendation': self._get_plagiarism_recommendation(severity)
        }
    
    def _check_copyscape_url(self, url: str) -> Dict[str, Any]:
        """
        Check a single URL via COPYSCAPE API
        """
        
        try:
            # Copyscape API endpoint
            api_url = "https://www.copyscape.com/api/"
            
            # Build request parameters
            params = {
                'u': self.copyscape_username,
                'k': self.copyscape_key,
                'o': 'csearch',  # Check URL operation
                'f': 'json',
                'q': url
            }
            
            response = self.session.get(api_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse results
                matches = int(data.get('count', 0))
                result_details = []
                
                for result in data.get('result', []):
                    result_details.append({
                        'url': result.get('url', ''),
                        'title': result.get('title', ''),
                        'percentmatched': result.get('percentmatched', 0)
                    })
                
                logger.info(f"[COPYSCAPE] Found {matches} matches for {url}")
                
                return {
                    'matches': matches,
                    'details': result_details
                }
            else:
                logger.error(f"[COPYSCAPE] Error {response.status_code}: {response.text}")
                return {'matches': 0, 'details': []}
                
        except Exception as e:
            logger.error(f"[COPYSCAPE] Exception: {e}")
            return {'matches': 0, 'details': []}
    
    def get_factcheck_history(
        self, 
        author_name: str, 
        outlet: str
    ) -> Dict[str, Any]:
        """
        Get fact-check history from GOOGLE FACTCHECK API
        
        Args:
            author_name: Author full name
            outlet: Publication name
            
        Returns:
            Fact-check record summary
        """
        
        logger.info(f"[FactCheck] Checking history for {author_name} at {outlet}")
        
        if not self.factcheck_key:
            return {
                'check_performed': False,
                'reason': 'No API key',
                'fact_checks_found': 0,
                'verified_claims': 0,
                'disputed_claims': 0
            }
        
        # Query Google Fact Check API
        try:
            url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
            
            # Search for author name + outlet
            query = f"{author_name} {outlet}"
            
            params = {
                'key': self.factcheck_key,
                'query': query,
                'languageCode': 'en',
                'pageSize': 10
            }
            
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                claims = data.get('claims', [])
                
                verified = 0
                disputed = 0
                all_ratings = []
                
                for claim in claims:
                    reviews = claim.get('claimReview', [])
                    for review in reviews:
                        rating = review.get('textualRating', '').lower()
                        all_ratings.append(rating)
                        
                        # Categorize
                        if any(word in rating for word in ['true', 'correct', 'accurate', 'verified']):
                            verified += 1
                        elif any(word in rating for word in ['false', 'incorrect', 'misleading', 'disputed']):
                            disputed += 1
                
                # Calculate credibility from fact-checks
                total_checks = verified + disputed
                if total_checks > 0:
                    fact_check_score = (verified / total_checks * 100)
                else:
                    fact_check_score = None
                
                logger.info(f"[FactCheck] Found {len(claims)} claims: {verified} verified, {disputed} disputed")
                
                return {
                    'check_performed': True,
                    'fact_checks_found': len(claims),
                    'verified_claims': verified,
                    'disputed_claims': disputed,
                    'fact_check_score': fact_check_score,
                    'all_ratings': all_ratings[:5],  # Top 5 ratings
                    'interpretation': self._interpret_factcheck_history(verified, disputed)
                }
            else:
                logger.error(f"[FactCheck] Error {response.status_code}")
                return {
                    'check_performed': False,
                    'fact_checks_found': 0,
                    'verified_claims': 0,
                    'disputed_claims': 0
                }
                
        except Exception as e:
            logger.error(f"[FactCheck] Exception: {e}")
            return {
                'check_performed': False,
                'fact_checks_found': 0,
                'verified_claims': 0,
                'disputed_claims': 0
            }
    
    def build_credibility_score(
        self,
        track_record: Dict[str, Any],
        plagiarism_check: Dict[str, Any],
        factcheck_history: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build comprehensive credibility score from all signals
        
        Score factors (0-100):
        - Track record: 40%
        - Plagiarism check: 35%
        - Fact-check history: 25%
        
        Returns:
            Combined credibility assessment
        """
        
        logger.info("[Credibility] Building comprehensive score")
        
        # FACTOR 1: Track Record (40%)
        total_articles = track_record.get('total_articles', 0)
        years_active = track_record.get('years_active', 0)
        
        if total_articles >= 50 and years_active >= 3:
            track_score = 90
        elif total_articles >= 20 and years_active >= 1:
            track_score = 70
        elif total_articles >= 10:
            track_score = 50
        else:
            track_score = 30
        
        # FACTOR 2: Plagiarism Check (35%)
        if plagiarism_check.get('check_performed'):
            plagiarism_score = plagiarism_check.get('severity_score', 70)
        else:
            plagiarism_score = 70  # Neutral if not checked
        
        # FACTOR 3: Fact-Check History (25%)
        if factcheck_history.get('check_performed'):
            fact_score = factcheck_history.get('fact_check_score')
            if fact_score is not None:
                factcheck_score = fact_score
            else:
                factcheck_score = 70  # Neutral if no fact-checks found
        else:
            factcheck_score = 70  # Neutral if not checked
        
        # Calculate weighted score
        combined_score = int(
            (track_score * 0.40) +
            (plagiarism_score * 0.35) +
            (factcheck_score * 0.25)
        )
        
        # Build explanation
        factors = []
        
        if track_record.get('total_articles', 0) > 0:
            factors.append(f"Published {track_record['total_articles']} articles over {track_record.get('years_active', 0)} years")
        
        if plagiarism_check.get('check_performed'):
            factors.append(f"Plagiarism check: {plagiarism_check['severity']}")
        
        if factcheck_history.get('check_performed') and factcheck_history.get('fact_checks_found', 0) > 0:
            factors.append(f"Fact-check history: {factcheck_history['verified_claims']} verified, {factcheck_history['disputed_claims']} disputed")
        
        # Determine trust level
        if combined_score >= 80:
            trust_level = 'High'
            trust_label = 'Highly Credible'
        elif combined_score >= 60:
            trust_level = 'Moderate-High'
            trust_label = 'Generally Credible'
        elif combined_score >= 40:
            trust_level = 'Moderate'
            trust_label = 'Mixed Signals'
        else:
            trust_level = 'Low'
            trust_label = 'Credibility Concerns'
        
        return {
            'combined_credibility_score': combined_score,
            'trust_level': trust_level,
            'trust_label': trust_label,
            'score_breakdown': {
                'track_record_score': track_score,
                'plagiarism_score': plagiarism_score,
                'factcheck_score': factcheck_score
            },
            'factors_considered': factors,
            'explanation': self._build_credibility_explanation(
                combined_score, 
                plagiarism_check, 
                factcheck_history
            )
        }
    
    def _get_plagiarism_recommendation(self, severity: str) -> str:
        """Get recommendation based on plagiarism severity"""
        
        if severity == 'Clean':
            return 'No plagiarism detected - good integrity signal'
        elif severity == 'Minor':
            return 'Minor matches found - likely coincidental or properly cited'
        elif severity == 'Moderate':
            return 'Some concerning matches - verify original sourcing'
        else:
            return 'Significant plagiarism detected - major credibility concern'
    
    def _interpret_factcheck_history(self, verified: int, disputed: int) -> str:
        """Interpret fact-check history"""
        
        total = verified + disputed
        
        if total == 0:
            return 'No fact-checks found in database'
        
        if disputed == 0:
            return 'All fact-checked claims verified - excellent record'
        elif verified > disputed * 2:
            return 'Mostly accurate with some disputed claims'
        elif verified > disputed:
            return 'More verified than disputed claims'
        else:
            return 'Significant fact-check disputes - credibility concern'
    
    def _build_credibility_explanation(
        self,
        score: int,
        plagiarism: Dict[str, Any],
        factcheck: Dict[str, Any]
    ) -> str:
        """Build human-readable explanation"""
        
        parts = []
        
        # Score interpretation
        if score >= 80:
            parts.append("This author demonstrates strong credibility indicators.")
        elif score >= 60:
            parts.append("This author shows generally good credibility.")
        elif score >= 40:
            parts.append("Mixed credibility signals detected for this author.")
        else:
            parts.append("Multiple credibility concerns identified.")
        
        # Plagiarism
        if plagiarism.get('check_performed'):
            severity = plagiarism.get('severity', 'Unknown')
            if severity == 'Clean':
                parts.append("No plagiarism detected.")
            elif severity != 'Unknown':
                parts.append(f"Plagiarism check: {severity} issues found.")
        
        # Fact-checks
        if factcheck.get('check_performed'):
            verified = factcheck.get('verified_claims', 0)
            disputed = factcheck.get('disputed_claims', 0)
            if verified + disputed > 0:
                parts.append(f"Fact-check record: {verified} verified, {disputed} disputed claims.")
        
        return ' '.join(parts)
