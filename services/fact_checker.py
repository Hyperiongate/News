"""
Fact Checker Service - FIXED CLAIM EXTRACTION + AI SUMMARY
Date: October 7, 2025
Version: 7.0.0 - MAJOR FIX

CRITICAL CHANGES FROM 6.0.0:
- FIXED: No longer extracts bylines, author bios, or boilerplate as "claims"
- ADDED: Filters out metadata patterns (Reporting by, Written by, etc.)
- ADDED: AI conversational summary explaining results
- IMPROVED: Better claim extraction focusing on substantive statements
- IMPROVED: Better explanations for unverified claims

THE BUG WE FIXED:
  Old: Extracted "Reporting by Andrea Shalal..." as a claim to verify
  New: Filters out bylines and only extracts REAL factual claims

Save as: services/fact_checker.py (REPLACE existing file)
"""

import re
import json
import time
import hashlib
import logging
import requests
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from urllib.parse import quote

from services.base_analyzer import BaseAnalyzer
from services.ai_enhancement_mixin import AIEnhancementMixin

logger = logging.getLogger(__name__)


class FactChecker(BaseAnalyzer, AIEnhancementMixin):
    """
    Fact-check article claims using improved scoring and claim extraction
    """
    
    def __init__(self):
        super().__init__('fact_checker')
        AIEnhancementMixin.__init__(self)
        
        # Cache for fact check results
        self.cache = {}
        self.cache_ttl = 86400  # 24 hours
        
        # API configuration
        from config import Config
        self.google_api_key = Config.GOOGLE_FACT_CHECK_API_KEY or Config.GOOGLE_FACTCHECK_API_KEY
        
        # Initialize claim extraction patterns
        self.claim_patterns = self._initialize_claim_patterns()
        
        # Boilerplate patterns to EXCLUDE from claims
        self.exclusion_patterns = self._initialize_exclusion_patterns()
        
        logger.info(f"FactChecker v7.0.0 initialized - Google API: {bool(self.google_api_key)}")
    
    def _check_availability(self) -> bool:
        """Service is available if we have pattern matching (always) or Google API"""
        return True
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze article with FIXED claim extraction and AI summary
        """
        try:
            start_time = time.time()
            
            # Extract content
            content = data.get('text', '') or data.get('content', '')
            if not content:
                return self.get_error_result("No content provided for fact checking")
            
            # Extract article metadata
            article_url = data.get('url', '')
            article_title = data.get('title', '')
            article_date = data.get('publish_date', '')
            
            # Extract contextual quality indicators
            sources_count = data.get('sources_count', 0)
            quotes_count = data.get('quotes_count', 0)
            author = data.get('author', '')
            
            logger.info(f"[FactChecker v7] Analyzing: {len(content)} chars, {sources_count} sources, {quotes_count} quotes")
            
            # 1. Extract REAL claims from content (FIXED to filter boilerplate)
            extracted_claims = self._extract_claims(content)
            logger.info(f"[FactChecker v7] Extracted {len(extracted_claims)} claims after filtering")
            
            # 2. Fact check the claims (if any)
            if extracted_claims:
                fact_checks = self._check_claims(extracted_claims, article_url, article_date)
            else:
                fact_checks = []
            
            # 3. Calculate verification score
            verification_score = self._calculate_improved_verification_score(
                fact_checks, 
                sources_count, 
                quotes_count,
                len(extracted_claims),
                bool(author and author != 'Unknown')
            )
            
            verification_level = self._get_verification_level(verification_score)
            
            # 4. Generate AI conversational summary
            ai_summary = self._generate_ai_summary(
                fact_checks,
                verification_score,
                sources_count,
                quotes_count,
                len(extracted_claims)
            )
            
            # 5. Generate standard summary
            summary = self._generate_improved_summary(
                fact_checks, 
                verification_score, 
                sources_count, 
                quotes_count
            )
            
            # 6. Identify sources used
            sources_used = self._get_sources_used(fact_checks)
            
            # Build response with improved data
            result = {
                'service': self.service_name,
                'success': True,
                'data': {
                    'score': verification_score,
                    'level': verification_level,
                    'verification_score': verification_score,
                    'verification_level': verification_level,
                    'accuracy_score': verification_score,
                    'ai_summary': ai_summary,  # NEW: AI conversational summary
                    'summary': summary,
                    'findings': self._generate_improved_findings(fact_checks, verification_score, sources_count),
                    'claims_found': len(extracted_claims),
                    'claims_checked': len(fact_checks),
                    'claims_verified': len([fc for fc in fact_checks if fc.get('verdict') in ['true', 'likely_true']]),
                    'fact_checks': fact_checks[:10],
                    'sources_used': sources_used,
                    'google_api_used': bool(self.google_api_key),
                    'details': {
                        'total_claims': len(extracted_claims),
                        'verified_claims': len([fc for fc in fact_checks if fc.get('verdict') in ['true', 'likely_true']]),
                        'disputed_claims': len([fc for fc in fact_checks if fc.get('verdict') in ['false', 'likely_false']]),
                        'unverified_claims': len([fc for fc in fact_checks if fc.get('verdict') == 'unverified']),
                        'average_confidence': sum(fc.get('confidence', 0) for fc in fact_checks) / max(len(fact_checks), 1),
                        'sources_cited': sources_count,
                        'quotes_included': quotes_count
                    },
                    'analysis': {
                        'what_we_looked': 'We extracted factual claims from the article and attempted to verify them using multiple sources.',
                        'what_we_found': ai_summary,
                        'what_it_means': self._generate_what_it_means(verification_score, len(extracted_claims), len(fact_checks))
                    }
                },
                'metadata': {
                    'analysis_time': time.time() - start_time,
                    'content_length': len(content),
                    'api_available': bool(self.google_api_key),
                    'scoring_type': 'improved',
                    'version': '7.0.0'
                }
            }
            
            logger.info(f"[FactChecker v7] Complete: {len(fact_checks)} claims checked, score: {verification_score}/100")
            return result
            
        except Exception as e:
            logger.error(f"[FactChecker v7] Error: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _initialize_exclusion_patterns(self) -> List[re.Pattern]:
        """
        Initialize patterns for boilerplate/metadata to EXCLUDE from claims
        
        CRITICAL: This fixes the bug where bylines were extracted as claims
        """
        patterns = [
            # Bylines and reporting credits
            r'^(?:reporting|written|edited|produced|photography)\s+by\s+',
            r'^(?:additional\s+)?reporting\s+(?:by|from)',
            r'^(?:story\s+)?by\s+[A-Z]',
            
            # Author bios and affiliations
            r'^she\s+(?:previously|currently|also|has)',
            r'^he\s+(?:previously|currently|also|has)',
            r'^[A-Z][a-z]+\s+is\s+(?:a|an)\s+(?:reporter|journalist|editor|writer)',
            
            # Disclaimers and boilerplate
            r'^(?:our|the)\s+standards:',
            r'trust\s+principles',
            r'^(?:read|see|learn)\s+more\s+(?:about|at)',
            r'^(?:for|with)\s+more\s+information',
            r'^(?:follow|contact)\s+(?:us|me|the)',
            
            # Copyright and legal
            r'^\(c\)\s+\d{4}',
            r'^copyright\s+',
            r'all\s+rights\s+reserved',
            
            # Social media and links
            r'^(?:twitter|facebook|instagram|linkedin):',
            r'^email:',
            r'^@[a-z0-9_]+',
            
            # Navigation and UI elements
            r'^(?:click|tap|scroll|swipe)\s+(?:here|to)',
            r'^share\s+this\s+(?:story|article)',
            r'^subscribe\s+to',
        ]
        
        return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def _is_boilerplate(self, text: str) -> bool:
        """Check if text matches boilerplate/metadata patterns"""
        text_lower = text.strip().lower()
        
        # Check exclusion patterns
        for pattern in self.exclusion_patterns:
            if pattern.search(text):
                return True
        
        # Additional heuristics
        # Very short or very long sentences are likely not factual claims
        if len(text) < 30 or len(text) > 400:
            return True
        
        # Sentences with too many capital words are likely names/titles
        words = text.split()
        if len(words) > 3:
            capital_ratio = sum(1 for w in words if w and w[0].isupper()) / len(words)
            if capital_ratio > 0.6:  # More than 60% capitalized = probably boilerplate
                return True
        
        return False
    
    def _extract_claims(self, content: str) -> List[str]:
        """
        Extract REAL fact-checkable claims from content
        
        FIXED v7.0.0: Now filters out bylines, author bios, and boilerplate
        """
        claims = []
        sentences = re.split(r'[.!?]+', content)
        
        logger.info(f"[FactChecker v7] Processing {len(sentences)} sentences")
        
        for sentence in sentences:
            sentence = sentence.strip()
            
            # Skip if too short
            if len(sentence) < 30:
                continue
            
            # CRITICAL FIX: Skip if this is boilerplate/metadata
            if self._is_boilerplate(sentence):
                logger.debug(f"[FactChecker v7] Filtered boilerplate: {sentence[:50]}...")
                continue
            
            # Score the claim's importance
            importance_score = self._score_claim_importance(sentence)
            
            # Only include claims with sufficient importance
            if importance_score >= 15:
                claim_type = self._classify_claim_type(sentence)
                claims.append({
                    'text': sentence,
                    'importance_score': importance_score,
                    'type': claim_type
                })
                logger.debug(f"[FactChecker v7] Found {claim_type} claim (score={importance_score}): {sentence[:60]}...")
        
        # Sort by importance and return top claims
        claims.sort(key=lambda x: x['importance_score'], reverse=True)
        top_claims = [claim['text'] for claim in claims[:10]]  # Limit to top 10
        
        logger.info(f"[FactChecker v7] Extracted {len(top_claims)} substantive claims from {len(sentences)} sentences")
        
        return top_claims
    
    def _score_claim_importance(self, claim: str) -> int:
        """Score how important/fact-checkable a claim is"""
        score = 0
        claim_lower = claim.lower()
        
        # Statistical claims (high value)
        if re.search(r'\b\d+\s*(?:percent|%|million|billion|thousand)\b', claim):
            score += 25
        
        # Numerical data
        numbers = re.findall(r'\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b', claim)
        score += len(numbers) * 5
        
        # Attribution indicators (medium value)
        if re.search(r'\b(?:according to|said|stated|claimed|announced|reported)\b', claim_lower):
            score += 15
        
        # Specific claims about events, policies, etc.
        if re.search(r'\b(?:will|plans to|announced|proposed|signed|passed)\b', claim_lower):
            score += 12
        
        # Research/study citations
        if re.search(r'\b(?:study|research|report|survey|investigation)\s+(?:found|showed|revealed)\b', claim_lower):
            score += 20
        
        # Reduce score for hedging language
        if re.search(r'\b(?:may|might|could|possibly|perhaps|potentially)\b', claim_lower):
            score -= 8
        
        # Reduce score for opinion language
        if re.search(r'\b(?:believe|think|feel|opinion|seems)\b', claim_lower):
            score -= 10
        
        return max(0, score)
    
    def _classify_claim_type(self, claim: str) -> str:
        """Classify the type of claim"""
        claim_lower = claim.lower()
        
        if re.search(r'\b\d+\s*(?:percent|%)\b', claim):
            return 'statistical'
        elif re.search(r'\b(?:study|research|report|investigation)\b', claim_lower):
            return 'research'
        elif re.search(r'\b(?:said|stated|claimed|announced|declared)\b', claim_lower):
            return 'attributed'
        elif re.search(r'\b(?:will|plans?\s+to|announced|proposed)\b', claim_lower):
            return 'future_action'
        elif re.search(r'\b(?:increased?|decreased?|rose|fell|grew|declined)\b', claim_lower):
            return 'trend'
        else:
            return 'factual'
    
    def _generate_ai_summary(
        self,
        fact_checks: List[Dict[str, Any]],
        score: int,
        sources_count: int,
        quotes_count: int,
        total_claims: int
    ) -> str:
        """
        Generate conversational AI summary explaining the fact-checking results
        
        NEW in v7.0.0: Provides context and actionable guidance
        """
        
        # Case 1: No claims found
        if total_claims == 0:
            if sources_count >= 5:
                return (
                    f"This article doesn't contain specific factual claims that require verification - "
                    f"it's primarily composed of reporting, context, and analysis. However, it cites "
                    f"{sources_count} sources, which is excellent for transparency. The {score}/100 score "
                    f"reflects the strong sourcing rather than claim verification."
                )
            else:
                return (
                    f"We didn't identify specific fact-checkable claims in this article. This could mean "
                    f"it's opinion/editorial content, breaking news without substantive details yet, or "
                    f"primarily narrative reporting. With only {sources_count} sources cited, verify "
                    f"important information independently. Score: {score}/100."
                )
        
        # Case 2: Claims found but none verified
        verified_count = len([fc for fc in fact_checks if fc.get('verdict') in ['true', 'likely_true']])
        disputed_count = len([fc for fc in fact_checks if fc.get('verdict') in ['false', 'likely_false']])
        unverified_count = len([fc for fc in fact_checks if fc.get('verdict') == 'unverified'])
        
        if verified_count == 0 and disputed_count == 0:
            return (
                f"We found {total_claims} factual claims but couldn't verify them against our fact-checking "
                f"databases. This doesn't mean they're false - many legitimate claims simply haven't been "
                f"independently fact-checked yet. The article cites {sources_count} sources and includes "
                f"{quotes_count} quotes, giving you some basis to assess credibility. Your score of {score}/100 "
                f"reflects sourcing quality rather than verified accuracy."
            )
        
        # Case 3: Mixed results
        summary_parts = []
        
        # Opening
        summary_parts.append(f"We checked {len(fact_checks)} claims from this article.")
        
        # Verified claims
        if verified_count > 0:
            summary_parts.append(
                f"{verified_count} {'claim' if verified_count == 1 else 'claims'} checked out as accurate "
                f"against independent fact-checking sources - that's a good sign."
            )
        
        # Disputed claims
        if disputed_count > 0:
            summary_parts.append(
                f"⚠️ {disputed_count} {'claim' if disputed_count == 1 else 'claims'} appear problematic "
                f"or contradicted by fact-checkers. Read those carefully."
            )
        
        # Unverified claims
        if unverified_count > 0:
            summary_parts.append(
                f"{unverified_count} {'claim' if unverified_count == 1 else 'claims'} couldn't be verified "
                f"(not necessarily wrong, just not independently checked)."
            )
        
        # Sourcing context
        if sources_count >= 5:
            summary_parts.append(
                f"On the plus side, the article cites {sources_count} sources, which helps you verify things yourself."
            )
        elif sources_count == 0:
            summary_parts.append(
                f"⚠️ No sources are cited, making independent verification difficult."
            )
        
        # Score interpretation
        if score >= 80:
            summary_parts.append(f"Overall score: {score}/100 - strong verification and sourcing.")
        elif score >= 60:
            summary_parts.append(f"Overall score: {score}/100 - decent but verify key claims yourself.")
        else:
            summary_parts.append(f"Overall score: {score}/100 - approach with healthy skepticism.")
        
        return " ".join(summary_parts)
    
    def _generate_what_it_means(self, score: int, total_claims: int, checked_claims: int) -> str:
        """Generate 'what it means' explanation"""
        
        if total_claims == 0:
            return (
                "This article doesn't contain specific fact-checkable claims. That's normal for "
                "some types of reporting (analysis, opinion, breaking news). Look for strong sourcing instead."
            )
        
        if score >= 80:
            return (
                "Strong fact-checking and sourcing indicate this is reliable journalism. "
                "The claims we could verify checked out, and sourcing is transparent."
            )
        elif score >= 60:
            return (
                "This article has decent credibility, though not all claims could be verified. "
                "The sourcing provides some ability to verify information yourself."
            )
        elif score >= 40:
            return (
                "Limited verification means you should be cautious. Cross-check important claims "
                "with other sources before relying on this information."
            )
        else:
            return (
                "Weak verification and sourcing are red flags. Treat claims skeptically and "
                "seek corroboration from more established sources."
            )
    
    def _calculate_improved_verification_score(
        self, 
        fact_checks: List[Dict[str, Any]], 
        sources_count: int,
        quotes_count: int,
        total_claims: int,
        has_author: bool
    ) -> int:
        """Calculate verification score (unchanged from v6.0.0)"""
        
        base_score = 50
        
        # Source Quality (0-30 points)
        source_score = 0
        if sources_count >= 10:
            source_score = 30
        elif sources_count >= 5:
            source_score = 20
        elif sources_count >= 3:
            source_score = 15
        elif sources_count >= 1:
            source_score = 10
        else:
            source_score = -10
        
        # Quote Quality (0-10 points)
        quote_score = 0
        if quotes_count >= 5:
            quote_score = 10
        elif quotes_count >= 3:
            quote_score = 7
        elif quotes_count >= 1:
            quote_score = 5
        
        # Claim Verification (0-20 points or penalty)
        claim_score = 0
        if fact_checks:
            verified = len([fc for fc in fact_checks if fc.get('verdict') in ['true', 'likely_true']])
            disputed = len([fc for fc in fact_checks if fc.get('verdict') in ['false', 'likely_false']])
            
            if verified > 0:
                verification_rate = verified / len(fact_checks)
                claim_score += int(verification_rate * 20)
            
            if disputed > 0:
                dispute_rate = disputed / len(fact_checks)
                claim_score -= int(dispute_rate * 30)
        
        # Author Attribution (0-5 points)
        author_score = 5 if has_author else 0
        
        # Claim Complexity Bonus (0-5 points)
        complexity_score = 0
        if total_claims >= 10:
            complexity_score = 5
        elif total_claims >= 5:
            complexity_score = 3
        
        final_score = base_score + source_score + quote_score + claim_score + author_score + complexity_score
        final_score = max(0, min(100, final_score))
        
        logger.info(
            f"[FactChecker v7 Scoring] Base: {base_score}, Sources: +{source_score}, "
            f"Quotes: +{quote_score}, Claims: {claim_score:+d}, Author: +{author_score}, "
            f"Complexity: +{complexity_score}, Final: {final_score}"
        )
        
        return int(final_score)
    
    def _check_claims(self, claims: List[str], article_url: Optional[str] = None,
                     article_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Check multiple claims using available sources"""
        fact_checks = []
        
        for i, claim in enumerate(claims):
            cache_key = self._get_cache_key(claim)
            cached_result = self._get_cached_result(cache_key)
            
            if cached_result:
                cached_result['from_cache'] = True
                fact_checks.append(cached_result)
                continue
            
            result = self._check_single_claim(claim, i, article_url, article_date)
            fact_checks.append(result)
            self._cache_result(cache_key, result)
            
            if i < len(claims) - 1:
                time.sleep(0.1)
        
        return fact_checks
    
    def _check_single_claim(self, claim: str, index: int, 
                           article_url: Optional[str], 
                           article_date: Optional[str]) -> Dict[str, Any]:
        """Check a single claim using multiple methods"""
        result = {
            'claim': claim[:300] + '...' if len(claim) > 300 else claim,
            'verdict': 'unverified',
            'explanation': 'This claim has not been independently fact-checked yet',
            'confidence': 0,
            'sources': [],
            'evidence': [],
            'checked_at': datetime.now().isoformat()
        }
        
        methods_tried = []
        
        # Try Google Fact Check API first
        if self.google_api_key:
            google_result = self._check_google_fact_check_api(claim)
            methods_tried.append('google_api')
            
            if google_result['found']:
                result.update(google_result['data'])
                result['methods_used'] = methods_tried
                return result
        
        # Fallback to pattern analysis
        pattern_result = self._analyze_claim_patterns(claim)
        methods_tried.append('pattern_analysis')
        result.update(pattern_result)
        result['methods_used'] = methods_tried
        
        return result
    
    def _check_google_fact_check_api(self, claim: str) -> Dict[str, Any]:
        """Check claim using Google Fact Check Tools API"""
        try:
            url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
            params = {
                'key': self.google_api_key,
                'query': claim[:500],
                'languageCode': 'en'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'claims' in data and data['claims']:
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
            logger.error(f"[FactChecker v7] Google API error: {e}")
            return {'found': False}
    
    def _analyze_claim_patterns(self, claim: str) -> Dict[str, Any]:
        """Analyze claim using pattern matching and heuristics"""
        result = {
            'verdict': 'unverified',
            'explanation': 'Pattern analysis could not verify this claim. It may be accurate but requires external fact-checking.',
            'confidence': 30,
            'sources': ['Pattern Analysis'],
            'evidence': []
        }
        
        claim_lower = claim.lower()
        confidence_modifiers = []
        evidence_points = []
        
        # Red flag patterns
        false_patterns = {
            r'\b(?:always|never|all|none|every|no one)\b': ('absolute language', -20),
            r'\b100%\s+(?:safe|effective|proven)\b': ('impossible certainty', -25),
            r'\b(?:miracle|breakthrough|revolutionary)\s+(?:cure|treatment|discovery)\b': ('sensational claims', -15)
        }
        
        for pattern, (description, modifier) in false_patterns.items():
            if re.search(pattern, claim_lower):
                confidence_modifiers.append(modifier)
                evidence_points.append(f"Contains {description}")
        
        # Credibility patterns
        credible_patterns = {
            r'\b(?:according to|study by|research from)\s+(?:the\s+)?[A-Z][a-z]+': ('attributed source', 15),
            r'\b(?:peer-reviewed|published in|journal of)\b': ('academic source', 20),
            r'\b(?:fda|cdc|who|nih)\b': ('official authority', 25)
        }
        
        for pattern, (description, modifier) in credible_patterns.items():
            if re.search(pattern, claim_lower):
                confidence_modifiers.append(modifier)
                evidence_points.append(f"References {description}")
        
        final_confidence = result['confidence'] + sum(confidence_modifiers)
        result['confidence'] = max(0, min(100, final_confidence))
        result['evidence'] = evidence_points
        
        if result['confidence'] >= 70:
            result['verdict'] = 'likely_true'
            result['explanation'] = 'Pattern analysis suggests this claim is likely accurate based on credible indicators'
        elif result['confidence'] >= 40:
            result['verdict'] = 'mixed'
            result['explanation'] = 'Pattern analysis shows mixed reliability - some credible indicators but also concerns'
        elif result['confidence'] <= 20:
            result['verdict'] = 'likely_false'
            result['explanation'] = 'Pattern analysis suggests this claim may be inaccurate - contains red flags'
        
        return result
    
    def _determine_consensus_verdict(self, verdicts: List[str]) -> str:
        """Determine consensus verdict from multiple fact checks"""
        if not verdicts:
            return 'unverified'
        
        normalized = []
        for verdict in verdicts:
            v_lower = verdict.lower()
            if any(term in v_lower for term in ['true', 'correct', 'accurate']):
                normalized.append('true')
            elif any(term in v_lower for term in ['false', 'incorrect', 'inaccurate']):
                normalized.append('false')
            elif any(term in v_lower for term in ['mixed', 'partly', 'mostly']):
                normalized.append('mixed')
            else:
                normalized.append('unclear')
        
        verdict_counts = {}
        for verdict in normalized:
            verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
        
        if verdict_counts:
            return max(verdict_counts.items(), key=lambda x: x[1])[0]
        
        return 'unverified'
    
    def _calculate_api_confidence(self, verdicts: List[str], publishers: List[str]) -> int:
        """Calculate confidence based on API results"""
        base_confidence = 60
        
        if len(verdicts) > 1:
            base_confidence += min(20, len(verdicts) * 5)
        
        reputable_publishers = ['snopes', 'politifact', 'factcheck.org', 'reuters', 'ap news']
        for publisher in publishers:
            if any(rep in publisher.lower() for rep in reputable_publishers):
                base_confidence += 10
                break
        
        return min(95, base_confidence)
    
    def _generate_improved_summary(
        self, 
        fact_checks: List[Dict[str, Any]], 
        verification_score: int,
        sources_count: int,
        quotes_count: int
    ) -> str:
        """Generate standard summary (legacy compatibility)"""
        
        if not fact_checks:
            if sources_count >= 5:
                return f"Well-sourced article with {sources_count} citations. Score: {verification_score}/100"
            else:
                return f"Limited sourcing. Score: {verification_score}/100 - verify claims independently."
        
        verdicts = [check.get('verdict', 'unverified') for check in fact_checks]
        verified = verdicts.count('true') + verdicts.count('likely_true')
        disputed = verdicts.count('false') + verdicts.count('likely_false')
        
        summary = f"Checked {len(fact_checks)} claims: "
        
        if verified > 0:
            summary += f"{verified} verified, "
        if disputed > 0:
            summary += f"{disputed} disputed, "
        
        summary += f"Score: {verification_score}/100"
        
        return summary
    
    def _generate_improved_findings(
        self, 
        fact_checks: List[Dict[str, Any]], 
        score: int,
        sources_count: int
    ) -> List[Dict[str, Any]]:
        """Generate findings for UI display"""
        findings = []
        
        if score >= 80:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': f'Strong verification ({score}/100)',
                'explanation': 'Good fact-checking and sourcing'
            })
        elif score >= 60:
            findings.append({
                'type': 'info',
                'severity': 'medium',
                'text': f'Decent verification ({score}/100)',
                'explanation': 'Adequate sourcing and checking'
            })
        else:
            findings.append({
                'type': 'warning',
                'severity': 'high',
                'text': f'Limited verification ({score}/100)',
                'explanation': 'Verify claims independently'
            })
        
        if sources_count >= 5:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': f'Good sourcing ({sources_count} sources)',
                'explanation': 'Article provides adequate citations'
            })
        
        return findings
    
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
                sources.update(fc['sources'])
            if 'methods_used' in fc:
                sources.update(fc['methods_used'])
        return list(sources)
    
    def _get_cache_key(self, claim: str) -> str:
        """Generate cache key"""
        return hashlib.sha256(claim.encode()).hexdigest()[:16]
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached result if available"""
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
        """Initialize patterns for claim analysis"""
        return {
            'claim_indicators': [
                r'\b(?:study|research|report|survey) (?:shows?|finds?|indicates?|suggests?)\b',
                r'\b(?:according to|based on|as reported by)\b',
                r'\b(?:data|statistics|numbers|figures) (?:show|indicate|reveal)\b',
                r'\b(?:scientists?|researchers?|experts?) (?:say|claim|believe|found)\b',
            ],
            'fact_patterns': [
                r'\b\d+\s*(?:percent|%)\s+of\b',
                r'\b(?:increased?|decreased?|rose|fell) by \d+',
                r'\b\d+\s+(?:times|fold) (?:more|less|higher|lower)\b',
            ]
        }
