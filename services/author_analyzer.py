"""
Fact Checker Service - v9.1.0 ENHANCED CLAIM DETECTION
Last Updated: October 11, 2025

CHANGES FROM v9.0.0:
✅ FIXED: Improved claim detection - finds claims in news articles
✅ FIXED: Lowered scoring threshold (was too strict)
✅ ENHANCED: Better pattern matching for news content
✅ ENHANCED: Detects direct quotes, statements, announcements
✅ ENHANCED: Handles political/government news better
✅ NO BREAKING CHANGES: All v9.0.0 functionality preserved

CRITICAL FIX: v9.0 was finding 0 claims in rich news articles
CAUSE: Scoring threshold too high (15 points minimum)
SOLUTION: Lower threshold (8 points) + better patterns

Save as: services/fact_checker.py (REPLACE existing file)
"""

import re
import json
import time
import hashlib
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
from urllib.parse import quote

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI library not available for FactChecker")

from services.base_analyzer import BaseAnalyzer
from config import Config

logger = logging.getLogger(__name__)


class FactChecker(BaseAnalyzer):
    """
    Enhanced fact-checker with improved claim detection
    v9.1.0 - Better at finding claims in news articles
    """
    
    def __init__(self):
        super().__init__('fact_checker')
        
        # Initialize OpenAI client
        self.openai_client = None
        if OPENAI_AVAILABLE and Config.OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
                logger.info("[FactChecker v9.1] OpenAI client initialized successfully")
            except Exception as e:
                logger.warning(f"[FactChecker v9.1] Failed to initialize OpenAI: {e}")
                self.openai_client = None
        
        # Cache for fact check results
        self.cache = {}
        self.cache_ttl = 86400  # 24 hours
        
        # API configuration
        self.google_api_key = Config.GOOGLE_FACT_CHECK_API_KEY or Config.GOOGLE_FACTCHECK_API_KEY
        
        # Initialize patterns
        self.claim_patterns = self._initialize_claim_patterns()
        self.exclusion_patterns = self._initialize_exclusion_patterns()
        
        logger.info(f"[FactChecker v9.1] Initialized - Google API: {bool(self.google_api_key)}, OpenAI: {bool(self.openai_client)}")
    
    def _check_availability(self) -> bool:
        """Service is always available"""
        return True
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze article with enhanced claim detection
        v9.1.0: Finds claims in news articles
        """
        try:
            start_time = time.time()
            
            # Extract content
            content = data.get('text', '') or data.get('content', '')
            if not content:
                return self.get_error_result("No content provided for fact checking")
            
            # Extract metadata
            article_url = data.get('url', '')
            article_title = data.get('title', '')
            article_date = data.get('publish_date', '')
            sources_count = data.get('sources_count', 0)
            quotes_count = data.get('quotes_count', 0)
            author = data.get('author', '')
            
            logger.info(f"[FactChecker v9.1] Analyzing: {len(content)} chars, {sources_count} sources")
            
            # 1. Extract claims from content (ENHANCED v9.1)
            extracted_claims = self._extract_claims_enhanced(content)
            logger.info(f"[FactChecker v9.1] Extracted {len(extracted_claims)} claims")
            
            # 2. Check each claim with enhanced verification
            fact_checks = self._check_claims_enhanced(extracted_claims, article_url, article_title)
            
            # 3. Calculate verification score
            verification_score = self._calculate_enhanced_score(
                fact_checks, sources_count, quotes_count, len(extracted_claims), bool(author)
            )
            
            verification_level = self._get_verification_level(verification_score)
            
            # 4. Generate detailed findings
            findings = self._generate_detailed_findings(fact_checks, sources_count, verification_score)
            
            # 5. Generate comprehensive analysis
            analysis = self._generate_comprehensive_analysis(
                fact_checks, verification_score, sources_count, quotes_count, len(extracted_claims)
            )
            
            # 6. Generate conversational summary
            summary = self._generate_conversational_summary(fact_checks, verification_score, sources_count)
            
            # 7. Identify sources used
            sources_used = self._get_sources_used(fact_checks)
            
            # Count claim verdicts
            verified_true = len([fc for fc in fact_checks if fc.get('verdict') in ['true', 'mostly_true', 'likely_true']])
            verified_false = len([fc for fc in fact_checks if fc.get('verdict') in ['false', 'mostly_false', 'likely_false']])
            unverified = len([fc for fc in fact_checks if fc.get('verdict') == 'unverified'])
            mixed = len([fc for fc in fact_checks if fc.get('verdict') in ['mixed', 'misleading', 'needs_context']])
            
            # Build comprehensive result
            result = {
                'service': self.service_name,
                'success': True,
                'available': True,
                'timestamp': time.time(),
                'analysis_complete': True,
                
                # Core scores
                'score': verification_score,
                'level': verification_level,
                'verification_score': verification_score,
                'verification_level': verification_level,
                'accuracy_score': verification_score,
                
                # NEW v9.0: Detailed findings
                'findings': findings,
                
                # NEW v9.0: Comprehensive analysis
                'analysis': analysis,
                
                # Conversational summary
                'summary': summary,
                
                # Claim statistics
                'claims_found': len(extracted_claims),
                'claims_checked': len(fact_checks),
                'claims_verified': verified_true + verified_false + mixed,
                'claims_verified_true': verified_true,
                'claims_verified_false': verified_false,
                'claims_mixed': mixed,
                'claims_unverified': unverified,
                
                # Detailed fact checks (for display)
                'fact_checks': fact_checks[:10],
                'claims': fact_checks[:10],  # Alias for frontend
                
                # Sources used
                'sources_used': sources_used,
                'sources_cited_in_article': sources_count,
                
                # Verification methods
                'google_api_used': bool(self.google_api_key),
                'ai_verification_used': bool(self.openai_client),
                
                # Chart data
                'chart_data': {
                    'type': 'doughnut',
                    'data': {
                        'labels': ['Verified True', 'Verified False', 'Mixed', 'Unverified'],
                        'datasets': [{
                            'data': [verified_true, verified_false, mixed, unverified],
                            'backgroundColor': ['#10b981', '#ef4444', '#f59e0b', '#94a3b8']
                        }]
                    }
                },
                
                # Details
                'details': {
                    'total_claims': len(extracted_claims),
                    'verified_true': verified_true,
                    'verified_false': verified_false,
                    'mixed_verdicts': mixed,
                    'unverified': unverified,
                    'verification_rate': round((verified_true + verified_false + mixed) / max(len(fact_checks), 1) * 100, 1),
                    'accuracy_rate': round(verified_true / max(verified_true + verified_false, 1) * 100, 1) if (verified_true + verified_false) > 0 else 0,
                    'average_confidence': round(sum(fc.get('confidence', 0) for fc in fact_checks) / max(len(fact_checks), 1), 1),
                    'sources_cited': sources_count,
                    'quotes_included': quotes_count,
                    'has_author': bool(author)
                },
                
                'metadata': {
                    'analysis_time': time.time() - start_time,
                    'text_length': len(content),
                    'article_url': article_url,
                    'article_title': article_title,
                    'version': '9.1.0',
                    'ai_enhanced': bool(self.openai_client)
                }
            }
            
            logger.info(f"[FactChecker v9.1] Complete: {verification_score}/100 ({verification_level}) - {verified_true} verified, {verified_false} disputed")
            return self.get_success_result(result)
            
        except Exception as e:
            logger.error(f"[FactChecker v9.1] Error: {e}", exc_info=True)
            return self.get_error_result(f"Fact checking error: {str(e)}")
    
    def _extract_claims_enhanced(self, content: str) -> List[str]:
        """
        ENHANCED v9.1: Better claim extraction for news articles
        
        FIXES:
        - Lower threshold from 15 to 8 points
        - Better patterns for government/political news
        - Detect statements, announcements, declarations
        - Handle direct quotes as claims
        """
        sentences = self._split_sentences(content)
        claims = []
        
        logger.info(f"[FactChecker v9.1] Evaluating {len(sentences)} sentences...")
        
        for i, sentence in enumerate(sentences):
            # Skip excluded patterns
            if self._matches_exclusion_patterns(sentence):
                continue
            
            # Score claim likelihood (ENHANCED)
            score = self._score_claim_likelihood_enhanced(sentence)
            
            # CRITICAL FIX: Lower threshold from 15 to 8
            if score >= 8:
                claim = sentence.strip()
                if 20 < len(claim) < 500:  # Slightly longer minimum (was 15)
                    claims.append(claim)
                    logger.debug(f"[FactChecker v9.1] Claim (score={score}): {claim[:100]}...")
        
        logger.info(f"[FactChecker v9.1] Found {len(claims)} potential claims")
        return claims[:15]  # Increased from 10 to 15
    
    def _score_claim_likelihood_enhanced(self, sentence: str) -> int:
        """
        ENHANCED v9.1: Better scoring for news content
        
        NEW: Detects government announcements, statements, declarations
        NEW: Recognizes direct quotes as factual claims
        NEW: Better handling of political news
        """
        score = 0
        sentence_lower = sentence.lower()
        
        # ===== STRONG INDICATORS (25-30 points) =====
        
        # Research/studies (highest confidence)
        if re.search(r'\b(?:study|research|report|survey|poll|analysis)\s+(?:shows?|finds?|found|indicates?|suggests?|reveals?)\b', sentence_lower):
            score += 30
            logger.debug(f"[Claim Score] +30 research/study")
        
        # Statistics and numbers
        if re.search(r'\b\d+\s*(?:percent|%)\b', sentence):
            score += 25
            logger.debug(f"[Claim Score] +25 percentage")
        
        if re.search(r'\b\d+(?:,\d{3})*\s+(?:people|workers|employees|individuals|Americans|voters)\b', sentence):
            score += 25
            logger.debug(f"[Claim Score] +25 specific count")
        
        # ===== NEW v9.1: GOVERNMENT/OFFICIAL STATEMENTS (20-25 points) =====
        
        # Official announcements
        if re.search(r'\b(?:announced?|declared?|stated?|confirmed?|revealed?|disclosed?)\s+(?:that|today|yesterday|this week)\b', sentence_lower):
            score += 20
            logger.debug(f"[Claim Score] +20 official statement")
        
        # Government/administration actions
        if re.search(r'\b(?:administration|government|agency|department|officials?)\s+(?:says?|said|announced?|confirmed?|reported?)\b', sentence_lower):
            score += 20
            logger.debug(f"[Claim Score] +20 government statement")
        
        # Policy/action statements
        if re.search(r'\b(?:will|plans to|intends to|expects to|is expected to)\s+\w+\s+(?:employees?|workers?|people|programs?|funding)\b', sentence_lower):
            score += 18
            logger.debug(f"[Claim Score] +18 policy action")
        
        # ===== NEW v9.1: DIRECT QUOTES (15-20 points) =====
        
        # Quoted statements (often factual)
        if '"' in sentence and len(re.findall(r'"[^"]{20,}"', sentence)) > 0:
            score += 15
            logger.debug(f"[Claim Score] +15 direct quote")
        
        # Attribution phrases
        if re.search(r'\b(?:according to|as reported by|as stated by|officials? said|sources? (?:say|said|told))\b', sentence_lower):
            score += 18
            logger.debug(f"[Claim Score] +18 attribution")
        
        # ===== MODERATE INDICATORS (10-15 points) =====
        
        # Numeric changes
        if re.search(r'\b(?:increased?|decreased?|rose|fell|grew|declined?|dropped?)\s+(?:by|to|from)\s+\d+', sentence_lower):
            score += 12
            logger.debug(f"[Claim Score] +12 numeric change")
        
        # Dates and timeframes
        if re.search(r'\b(?:in|by|since|from|during)\s+\d{4}\b', sentence):
            score += 10
            logger.debug(f"[Claim Score] +10 date reference")
        
        # Named entities making statements
        if re.search(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\s+(?:said|told|announced|confirmed|stated)\b', sentence):
            score += 10
            logger.debug(f"[Claim Score] +10 named person statement")
        
        # ===== NEW v9.1: SPECIFIC FACTUAL PATTERNS (8-12 points) =====
        
        # Specific locations/organizations
        if re.search(r'\b(?:in|at|from)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', sentence):
            score += 8
            logger.debug(f"[Claim Score] +8 location/org")
        
        # Time-specific claims
        if re.search(r'\b(?:this year|last year|in 20\d{2}|by 20\d{2})\b', sentence_lower):
            score += 8
            logger.debug(f"[Claim Score] +8 time-specific")
        
        # Comparative statements
        if re.search(r'\b(?:more|less|higher|lower|greater|fewer)\s+than\b', sentence_lower):
            score += 8
            logger.debug(f"[Claim Score] +8 comparative")
        
        # ===== NEGATIVE INDICATORS =====
        
        # Uncertainty (reduce score)
        if re.search(r'\b(?:may|might|could|possibly|perhaps|allegedly|reportedly)\b', sentence_lower):
            score -= 5
            logger.debug(f"[Claim Score] -5 uncertain")
        
        # Questions (strong negative)
        if sentence.strip().endswith('?'):
            score -= 15
            logger.debug(f"[Claim Score] -15 question")
        
        # Opinion words
        if re.search(r'\b(?:I think|I believe|in my opinion|seems like|appears to)\b', sentence_lower):
            score -= 10
            logger.debug(f"[Claim Score] -10 opinion")
        
        final_score = max(0, score)
        if final_score >= 8:
            logger.debug(f"[Claim Score] FINAL: {final_score} - INCLUDED")
        
        return final_score
    
    def _check_claims_enhanced(self, claims: List[str], article_url: Optional[str] = None,
                               article_title: Optional[str] = None) -> List[Dict[str, Any]]:
        """Enhanced claim checking with multiple verification methods"""
        fact_checks = []
        
        for i, claim in enumerate(claims):
            # Check cache first
            cache_key = self._get_cache_key(claim)
            cached_result = self._get_cached_result(cache_key)
            
            if cached_result:
                cached_result['from_cache'] = True
                fact_checks.append(cached_result)
                logger.info(f"[FactChecker v9.1] Claim {i+1}: Using cached result")
                continue
            
            # Enhanced verification
            result = self._verify_claim_comprehensive(claim, i, article_url, article_title)
            fact_checks.append(result)
            self._cache_result(cache_key, result)
            
            logger.info(f"[FactChecker v9.1] Claim {i+1}: {result.get('verdict')} ({result.get('confidence')}%)")
            
            # Rate limiting
            if i < len(claims) - 1:
                time.sleep(0.2)
        
        return fact_checks
    
    def _verify_claim_comprehensive(self, claim: str, index: int,
                                   article_url: Optional[str],
                                   article_title: Optional[str]) -> Dict[str, Any]:
        """Comprehensive claim verification using multiple methods"""
        
        try:
            # Skip trivial claims
            if len(claim.strip()) < 15:
                return {
                    'claim': claim,
                    'verdict': 'opinion',
                    'explanation': 'Statement too short to verify meaningfully',
                    'confidence': 50,
                    'sources': [],
                    'evidence': [],
                    'method_used': 'filtered'
                }
            
            # METHOD 1: AI Analysis (BEST)
            if self.openai_client:
                logger.info(f"[FactChecker v9.1] Trying AI analysis")
                ai_result = self._ai_verify_claim(claim, article_title)
                if ai_result and ai_result.get('verdict') != 'needs_context':
                    ai_result['method_used'] = 'AI Verification'
                    logger.info(f"[FactChecker v9.1] ✓ AI verified: {ai_result.get('verdict')}")
                    return ai_result
            
            # METHOD 2: Google Fact Check API
            if self.google_api_key:
                logger.info(f"[FactChecker v9.1] Trying Google Fact Check API")
                google_result = self._check_google_api(claim)
                if google_result.get('found'):
                    result = google_result['data']
                    result['claim'] = claim
                    result['method_used'] = 'Google Fact Check Database'
                    logger.info(f"[FactChecker v9.1] ✓ Google found: {result.get('verdict')}")
                    return result
            
            # METHOD 3: Pattern Analysis (fallback)
            logger.info(f"[FactChecker v9.1] Using pattern analysis")
            pattern_result = self._analyze_claim_patterns(claim)
            pattern_result['claim'] = claim
            pattern_result['method_used'] = 'Pattern Analysis'
            return pattern_result
            
        except Exception as e:
            logger.error(f"[FactChecker v9.1] Error verifying claim: {e}")
            return {
                'claim': claim,
                'verdict': 'unverified',
                'explanation': f'Verification error: {str(e)}',
                'confidence': 0,
                'sources': [],
                'evidence': [],
                'method_used': 'error'
            }
    
    # ===== All other methods remain EXACTLY THE SAME as v9.0 =====
    # (Copying them below to maintain complete file)
    
    def _ai_verify_claim(self, claim: str, article_context: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Use AI to verify a claim"""
        if not self.openai_client:
            return None
        
        try:
            prompt = self._build_verification_prompt(claim, article_context)
            
            response = self.openai_client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert fact-checker. Analyze claims and provide clear verdicts with explanations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            result = self._parse_ai_verification(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.warning(f"[FactChecker v9.1] AI verification failed: {e}")
            return None
    
    def _build_verification_prompt(self, claim: str, context: Optional[str] = None) -> str:
        """Build prompt for AI verification"""
        prompt_parts = [
            f"Verify this factual claim: \"{claim}\"",
            ""
        ]
        
        if context:
            prompt_parts.append(f"Context: This claim appears in an article titled \"{context}\"")
            prompt_parts.append("")
        
        prompt_parts.extend([
            "Analyze this claim and provide:",
            "1. VERDICT: Is it true, false, misleading, or needs more context?",
            "2. CONFIDENCE: Your confidence level (50-95%)",
            "3. EXPLANATION: Why you reached this verdict (2-3 sentences)",
            "",
            "Possible verdicts:",
            "- true: Claim is accurate",
            "- mostly_true: Claim is largely accurate with minor issues",
            "- mixed: Claim has both true and false elements",
            "- misleading: Technically true but creates false impression",
            "- mostly_false: Claim is largely inaccurate",
            "- false: Claim is demonstrably false",
            "- unverified: Cannot be verified with available information",
            "",
            "Format your response EXACTLY like this:",
            "VERDICT: [verdict]",
            "CONFIDENCE: [number]",
            "EXPLANATION: [explanation]"
        ])
        
        return "\n".join(prompt_parts)
    
    def _parse_ai_verification(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse AI verification response"""
        try:
            lines = response.strip().split('\n')
            result = {
                'verdict': 'unverified',
                'confidence': 50,
                'explanation': 'AI analysis completed',
                'sources': ['AI Analysis']
            }
            
            for line in lines:
                line = line.strip()
                if line.startswith('VERDICT:'):
                    verdict = line.replace('VERDICT:', '').strip().lower()
                    verdict_map = {
                        'true': 'true',
                        'mostly true': 'mostly_true',
                        'mostly_true': 'mostly_true',
                        'mixed': 'mixed',
                        'misleading': 'misleading',
                        'mostly false': 'mostly_false',
                        'mostly_false': 'mostly_false',
                        'false': 'false',
                        'unverified': 'unverified',
                        'needs context': 'needs_context'
                    }
                    result['verdict'] = verdict_map.get(verdict, 'unverified')
                    
                elif line.startswith('CONFIDENCE:'):
                    conf_str = re.findall(r'\d+', line)
                    if conf_str:
                        result['confidence'] = min(int(conf_str[0]), 95)
                        
                elif line.startswith('EXPLANATION:'):
                    explanation = line.replace('EXPLANATION:', '').strip()
                    if explanation:
                        result['explanation'] = explanation
            
            # Collect remaining lines as explanation if needed
            explanation_lines = [l for l in lines if not l.startswith(('VERDICT:', 'CONFIDENCE:', 'EXPLANATION:')) and l.strip()]
            if explanation_lines and len(result['explanation']) < 50:
                result['explanation'] = ' '.join(explanation_lines[:3])
            
            return result
            
        except Exception as e:
            logger.error(f"[FactChecker v9.1] Failed to parse AI response: {e}")
            return None
    
    def _check_google_api(self, claim: str) -> Dict[str, Any]:
        """Check Google Fact Check API"""
        if not self.google_api_key:
            return {'found': False}
        
        try:
            url = 'https://factchecktools.googleapis.com/v1alpha1/claims:search'
            params = {
                'key': self.google_api_key,
                'query': claim[:500],
                'languageCode': 'en'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'claims' in data and len(data['claims']) > 0:
                    verdicts = []
                    explanations = []
                    publishers = []
                    urls = []
                    
                    for claim_item in data['claims'][:3]:
                        for review in claim_item.get('claimReview', [])[:2]:
                            if 'textualRating' in review:
                                verdicts.append(review['textualRating'])
                            if 'title' in review:
                                explanations.append(review['title'])
                            if 'publisher' in review:
                                publishers.append(review['publisher'].get('name', 'Unknown'))
                            if 'url' in review:
                                urls.append(review['url'])
                    
                    verdict = self._determine_consensus_verdict(verdicts)
                    confidence = self._calculate_api_confidence(verdicts, publishers)
                    
                    return {
                        'found': True,
                        'data': {
                            'verdict': verdict,
                            'explanation': explanations[0] if explanations else 'Verified by fact checkers',
                            'confidence': confidence,
                            'sources': list(set(publishers))[:3],
                            'evidence': explanations[:3],
                            'fact_check_urls': urls[:3]
                        }
                    }
            
            return {'found': False}
            
        except Exception as e:
            logger.error(f"[FactChecker v9.1] Google API error: {e}")
            return {'found': False}
    
    def _analyze_claim_patterns(self, claim: str) -> Dict[str, Any]:
        """Analyze claim using pattern matching"""
        result = {
            'verdict': 'unverified',
            'explanation': 'This claim could not be verified automatically. Check if the article provides sources.',
            'confidence': 30,
            'sources': ['Pattern Analysis'],
            'evidence': []
        }
        
        claim_lower = claim.lower()
        
        # Check for attributed statements
        if re.search(r'\b(?:said|stated|according to|claimed)\b', claim_lower):
            result['confidence'] = 40
            result['explanation'] = 'This is an attributed statement. Verify by checking the original source mentioned.'
        
        # Check for statistical claims
        if re.search(r'\b\d+\s*(?:percent|%)\b', claim) or re.search(r'\b\d+\s+(?:million|billion|thousand)\b', claim):
            result['confidence'] = 35
            result['explanation'] = 'This claim contains statistics. Verify against official data sources or the article\'s citations.'
        
        # Check for absolute language (red flag)
        if re.search(r'\b(?:always|never|all|none|every|no one)\b', claim_lower):
            result['confidence'] = 25
            result['explanation'] = 'This claim uses absolute language which is often a sign of exaggeration. Such claims are rarely completely accurate.'
            result['evidence'] = ['Contains absolute language that suggests exaggeration']
        
        return result
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        text = re.sub(r'\n+', '. ', text)
        sentences = re.split(r'[.!?]+(?=\s+[A-Z]|\s*$)', text)
        
        cleaned = []
        for s in sentences:
            s = s.strip()
            if len(s) > 15 and not s.isupper():
                cleaned.append(s)
        
        return cleaned
    
    def _matches_exclusion_patterns(self, sentence: str) -> bool:
        """Check if sentence matches exclusion patterns"""
        if len(sentence) < 20 or len(sentence) > 500:
            return True
        
        exclusions = [
            r'^(?:By|Reporting by|Written by|Edited by|Photography by)\s+[A-Z]',
            r'^(?:Photo|Image|Video|Figure|Table)\s*:',
            r'^\d+:\d+',
            r'^(?:Click here|Subscribe|Follow us|Sign up|Read more)',
            r'^(?:Copyright|©|All rights reserved)',
            r'^(?:This article|This story|This report)\s+(?:was|is)',
            r'^\[.*?\]$',
            r'^https?://',
            r'@\w+'
        ]
        
        for pattern in exclusions:
            if re.match(pattern, sentence, re.IGNORECASE):
                return True
        
        return False
    
    def _calculate_enhanced_score(self, fact_checks: List[Dict], sources_count: int,
                                  quotes_count: int, total_claims: int, has_author: bool) -> int:
        """Calculate verification score"""
        
        # Base score from sourcing
        base_score = 50
        source_score = min(30, sources_count * 5)
        quote_score = min(20, quotes_count * 7)
        
        # Score from verification results
        verified_true = len([fc for fc in fact_checks if fc.get('verdict') in ['true', 'mostly_true', 'likely_true']])
        verified_false = len([fc for fc in fact_checks if fc.get('verdict') in ['false', 'mostly_false', 'likely_false']])
        
        claim_score = 0
        if total_claims > 0:
            verification_rate = (verified_true + verified_false) / total_claims
            accuracy_rate = verified_true / max(verified_true + verified_false, 1)
            claim_score = int(verification_rate * accuracy_rate * 20)
        
        # Bonuses
        author_score = 5 if has_author else 0
        complexity_score = 5 if total_claims >= 10 else (3 if total_claims >= 5 else 0)
        
        final_score = base_score + source_score + quote_score + claim_score + author_score + complexity_score
        final_score = max(0, min(100, final_score))
        
        return int(final_score)
    
    def _determine_consensus_verdict(self, verdicts: List[str]) -> str:
        """Determine consensus verdict"""
        if not verdicts:
            return 'unverified'
        
        normalized = []
        for v in verdicts:
            v_lower = v.lower()
            if 'true' in v_lower and 'false' not in v_lower:
                normalized.append('true')
            elif 'false' in v_lower:
                normalized.append('false')
            elif 'misleading' in v_lower or 'mixed' in v_lower:
                normalized.append('mixed')
            else:
                normalized.append('unverified')
        
        from collections import Counter
        counts = Counter(normalized)
        return counts.most_common(1)[0][0]
    
    def _calculate_api_confidence(self, verdicts: List[str], publishers: List[str]) -> int:
        """Calculate confidence from API results"""
        if not verdicts:
            return 30
        
        confidence = 60
        
        if len(verdicts) >= 3:
            confidence += 15
        elif len(verdicts) >= 2:
            confidence += 10
        
        reputable = ['snopes', 'politifact', 'factcheck.org', 'reuters', 'ap']
        for pub in publishers:
            if any(rep in pub.lower() for rep in reputable):
                confidence += 5
                break
        
        return min(confidence, 95)
    
    def _generate_detailed_findings(self, fact_checks: List[Dict[str, Any]], 
                                    sources_count: int, score: int) -> List[Dict[str, Any]]:
        """Generate detailed findings with specific examples"""
        findings = []
        
        # Count verdicts
        verified_true = len([fc for fc in fact_checks if fc.get('verdict') in ['true', 'mostly_true']])
        verified_false = len([fc for fc in fact_checks if fc.get('verdict') in ['false', 'mostly_false']])
        unverified = len([fc for fc in fact_checks if fc.get('verdict') == 'unverified'])
        
        # Finding: False claims
        if verified_false > 0:
            false_claims = [fc for fc in fact_checks if fc.get('verdict') in ['false', 'mostly_false']]
            findings.append({
                'type': 'critical',
                'severity': 'high',
                'text': f'{verified_false} claim(s) found to be false or mostly false',
                'explanation': f'We identified inaccurate claims in this article. Example: "{false_claims[0].get("claim", "")[:100]}..."',
                'examples': [fc.get('claim', '')[:150] for fc in false_claims[:2]]
            })
        
        # Finding: Verified true claims
        if verified_true > 0:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': f'{verified_true} claim(s) verified as accurate',
                'explanation': 'These claims were confirmed through fact-checking databases or AI verification'
            })
        
        # Finding: Unverified claims
        if unverified > len(fact_checks) * 0.5 and len(fact_checks) > 0:
            findings.append({
                'type': 'warning',
                'severity': 'medium',
                'text': f'{unverified} claim(s) could not be verified',
                'explanation': 'Many claims lack available verification. This doesn\'t mean they\'re false, but readers should verify important claims independently.'
            })
        
        # Finding: Overall verification
        if score >= 70:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': f'Strong verification score ({score}/100)',
                'explanation': 'Article demonstrates good sourcing and factual accuracy'
            })
        elif score < 50:
            findings.append({
                'type': 'warning',
                'severity': 'high',
                'text': f'Low verification score ({score}/100)',
                'explanation': 'Limited sourcing and verification. Treat claims with skepticism.'
            })
        
        # Finding: Sourcing
        if sources_count >= 5:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': f'Well-sourced ({sources_count} sources cited)',
                'explanation': 'Article provides adequate citations to verify claims'
            })
        elif sources_count == 0:
            findings.append({
                'type': 'warning',
                'severity': 'high',
                'text': 'No sources cited',
                'explanation': 'Article lacks citations, making claims difficult to verify'
            })
        
        return findings
    
    def _generate_comprehensive_analysis(self, fact_checks: List[Dict[str, Any]], 
                                        score: int, sources_count: int,
                                        quotes_count: int, total_claims: int) -> Dict[str, str]:
        """Generate comprehensive what_we_looked/found/means analysis"""
        
        # What we looked at
        verification_methods = []
        if any(fc.get('method_used') == 'AI Verification' for fc in fact_checks):
            verification_methods.append('AI verification')
        if any(fc.get('method_used') == 'Google Fact Check Database' for fc in fact_checks):
            verification_methods.append('Google Fact Check database')
        verification_methods.append('pattern analysis')
        
        what_we_looked = (
            f"We extracted {total_claims} factual claims from the article and verified them using "
            f"{', '.join(verification_methods)}. We also analyzed the article's sourcing quality "
            f"({sources_count} sources cited, {quotes_count} quotes) and author attribution."
        )
        
        # What we found
        verified_true = len([fc for fc in fact_checks if fc.get('verdict') in ['true', 'mostly_true']])
        verified_false = len([fc for fc in fact_checks if fc.get('verdict') in ['false', 'mostly_false']])
        unverified = len([fc for fc in fact_checks if fc.get('verdict') == 'unverified'])
        mixed = len([fc for fc in fact_checks if fc.get('verdict') in ['mixed', 'misleading']])
        
        findings_parts = []
        
        if verified_true > 0:
            findings_parts.append(f"{verified_true} claim(s) verified as accurate")
        if verified_false > 0:
            findings_parts.append(f"{verified_false} claim(s) found to be false or misleading")
        if mixed > 0:
            findings_parts.append(f"{mixed} claim(s) with mixed accuracy")
        if unverified > 0:
            findings_parts.append(f"{unverified} claim(s) could not be verified")
        
        what_we_found = ". ".join(findings_parts) + f". The article cites {sources_count} sources."
        
        # What it means
        if score >= 70:
            what_it_means = (
                f"This article demonstrates strong factual accuracy ({score}/100). "
                f"The claims we could verify were accurate, and the article provides adequate sourcing. "
                f"Readers can generally trust the information presented, though verifying critical claims independently is always recommended."
            )
        elif score >= 50:
            what_it_means = (
                f"This article has moderate verification ({score}/100). "
                f"Some claims were verified as accurate, but {'we found inaccuracies' if verified_false > 0 else 'many claims lack verification'}. "
                f"Exercise caution and cross-reference important information with other sources."
            )
        else:
            what_it_means = (
                f"This article has low verification ({score}/100). "
                f"{'We found false or misleading claims, and ' if verified_false > 0 else ''}The article lacks adequate sourcing. "
                f"Treat claims with skepticism and verify all important information independently before relying on it."
            )
        
        return {
            'what_we_looked': what_we_looked,
            'what_we_found': what_we_found,
            'what_it_means': what_it_means
        }
    
    def _generate_conversational_summary(self, fact_checks: List[Dict[str, Any]],
                                         score: int, sources_count: int) -> str:
        """Generate conversational summary"""
        
        verified_true = len([fc for fc in fact_checks if fc.get('verdict') in ['true', 'mostly_true']])
        verified_false = len([fc for fc in fact_checks if fc.get('verdict') in ['false', 'mostly_false']])
        
        if len(fact_checks) == 0:
            return f"No specific fact-checkable claims found. Article cites {sources_count} sources. Verification score: {score}/100."
        
        summary = f"Checked {len(fact_checks)} claims. "
        
        if verified_true > 0 and verified_false == 0:
            summary += f"{verified_true} verified as accurate. "
        elif verified_true > 0 and verified_false > 0:
            summary += f"{verified_true} accurate, {verified_false} false. "
        elif verified_false > 0:
            summary += f"{verified_false} found to be false or misleading. "
        
        summary += f"Article cites {sources_count} sources. "
        summary += f"Overall verification: {score}/100."
        
        return summary
    
    def _get_verification_level(self, score: int) -> str:
        """Convert score to level"""
        if score >= 80:
            return 'Highly Verified'
        elif score >= 60:
            return 'Well Verified'
        elif score >= 40:
            return 'Partially Verified'
        else:
            return 'Poorly Verified'
    
    def _get_sources_used(self, fact_checks: List[Dict[str, Any]]) -> List[str]:
        """Get unique sources used"""
        sources = set()
        for fc in fact_checks:
            if 'sources' in fc:
                if isinstance(fc['sources'], list):
                    sources.update(fc['sources'])
            if 'method_used' in fc:
                sources.add(fc['method_used'])
        return list(sources)
    
    def _get_cache_key(self, claim: str) -> str:
        """Generate cache key"""
        return hashlib.sha256(claim.encode()).hexdigest()[:16]
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached result"""
        if cache_key in self.cache:
            cached_time, result = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                return result.copy()
        return None
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]):
        """Cache result"""
        self.cache[cache_key] = (time.time(), result.copy())
        
        if len(self.cache) > 1000:
            sorted_items = sorted(self.cache.items(), key=lambda x: x[1][0])
            for key, _ in sorted_items[:100]:
                del self.cache[key]
    
    def _initialize_claim_patterns(self) -> Dict[str, Any]:
        """Initialize patterns"""
        return {
            'claim_indicators': [
                r'\b(?:study|research|report|survey) (?:shows?|finds?|indicates?|suggests?)\b',
                r'\b(?:according to|based on|as reported by)\b',
                r'\b(?:data|statistics) (?:show|indicate|reveal)\b',
            ]
        }
    
    def _initialize_exclusion_patterns(self) -> List[str]:
        """Initialize exclusion patterns"""
        return [
            r'^(?:By|Reporting by|Written by)\s+[A-Z]',
            r'^(?:Photo|Image)\s+(?:by|credit)',
            r'^\d+:\d+',
        ]
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        info = super().get_service_info()
        info.update({
            'version': '9.1.0',
            'capabilities': [
                'Enhanced claim detection for news articles',
                'AI-powered claim verification',
                'Google Fact Check database integration',
                'Multi-method verification (AI → API → Pattern)',
                'Claim-by-claim accuracy assessment',
                'Source citation analysis',
                'Detailed findings with examples',
                'Comprehensive explanations'
            ],
            'verification_methods': [
                'AI Verification' if self.openai_client else None,
                'Google Fact Check Database' if self.google_api_key else None,
                'Pattern Analysis'
            ],
            'ai_enhanced': bool(self.openai_client)
        })
        return info


logger.info("[FactChecker v9.1] Module loaded - Enhanced claim detection enabled")
