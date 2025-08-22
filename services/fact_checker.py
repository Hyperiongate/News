"""
Fact Checker Service - AI ENHANCED VERSION
Comprehensive fact checking using Google Fact Check API, multiple verification sources, and AI insights
"""

import os
import logging
import time
import re
import json
from urllib.parse import urlparse, quote
from datetime import datetime, timedelta
import hashlib
from typing import List, Dict, Optional, Tuple, Any
from collections import Counter

import requests
from bs4 import BeautifulSoup

from config import Config
from services.base_analyzer import BaseAnalyzer
from services.ai_enhancement_mixin import AIEnhancementMixin

logger = logging.getLogger(__name__)


class FactChecker(BaseAnalyzer, AIEnhancementMixin):
    """
    Fact checking service using Google Fact Check API, multiple verification sources, and AI enhancement
    """
    
    def __init__(self):
        """Initialize the fact checker with API keys and configuration"""
        super().__init__('fact_checker')
        AIEnhancementMixin.__init__(self)
        
        # API Keys
        self.google_api_key = Config.GOOGLE_FACT_CHECK_API_KEY or Config.GOOGLE_FACTCHECK_API_KEY
        self.news_api_key = Config.NEWS_API_KEY or Config.NEWSAPI_KEY
        
        # Session for API calls
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'NewsAnalyzer/1.0 (Fact Checker Service)'
        })
        
        # Cache for API responses
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour
        
        # Claim extraction patterns
        self.claim_patterns = self._initialize_claim_patterns()
        
        logger.info(f"FactChecker initialized - Google API: {bool(self.google_api_key)}, AI: {self._ai_available}")
    
    def _check_availability(self) -> bool:
        """Check if the service is available"""
        # Available if we have at least pattern-based checking
        return True
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze article for fact-checkable claims WITH AI ENHANCEMENT
        
        Expected input:
            - text: Article text to analyze
            - url: (optional) Article URL
            - title: (optional) Article title
            - date: (optional) Publication date
            
        Returns:
            Comprehensive fact-checking analysis
        """
        try:
            start_time = time.time()
            
            text = data.get('text', '')
            if not text:
                return self.get_error_result("No text provided for fact checking")
            
            article_url = data.get('url')
            article_date = data.get('date')
            
            # Extract claims from text
            claims = self._extract_claims(text)
            
            if not claims:
                return {
                    'service': self.service_name,
                    'success': True,
                    'data': {
                        'score': 100,
                        'level': 'No Claims',
                        'findings': [{
                            'type': 'info',
                            'severity': 'low',
                            'text': 'No fact-checkable claims found',
                            'explanation': 'Article contains no specific factual claims to verify'
                        }],
                        'summary': 'No specific factual claims were found in this article that require verification.',
                        'fact_checks': [],
                        'verification_score': 100,
                        'statistics': {
                            'total_claims': 0,
                            'verified_claims': 0,
                            'true_claims': 0,
                            'false_claims': 0,
                            'partially_true': 0,
                            'average_confidence': 0
                        }
                    },
                    'metadata': {
                        'processing_time': time.time() - start_time,
                        'claims_found': 0
                    }
                }
            
            # AI ENHANCEMENT - Prioritize and enhance claims
            if self._ai_available and claims:
                logger.info("Enhancing fact checking with AI")
                
                # Get AI help to identify key claims
                ai_claims = self._ai_analyze_claims(
                    claims=claims[:10],  # Analyze top 10 claims
                    context=text[:2000]
                )
                
                if ai_claims and ai_claims.get('claims'):
                    # Enhance claims with AI insights
                    ai_enhanced_claims = {}
                    for ai_claim in ai_claims['claims']:
                        claim_text = ai_claim.get('claim', '')
                        if claim_text:
                            ai_enhanced_claims[claim_text] = {
                                'verifiability': ai_claim.get('verifiability', 'medium'),
                                'approach': ai_claim.get('approach', []),
                                'red_flags': ai_claim.get('red_flags', []),
                                'search_queries': ai_claim.get('search_queries', [])
                            }
                    
                    # Use AI insights in fact checking
                    for i, claim in enumerate(claims):
                        if claim in ai_enhanced_claims:
                            claims[i] = {
                                'text': claim,
                                'ai_enhanced': True,
                                'ai_data': ai_enhanced_claims[claim]
                            }
            
            # Check claims
            fact_checks = self._check_claims(claims, article_url, article_date)
            
            # Calculate verification score and statistics
            verification_score = self._calculate_verification_score(fact_checks)
            trust_impact = self._calculate_trust_impact(fact_checks)
            
            # Generate findings
            findings = self._generate_findings(fact_checks, verification_score)
            
            # Generate summary
            summary = self._generate_summary(fact_checks, verification_score)
            
            return {
                'service': self.service_name,
                'success': True,
                'data': {
                    'score': trust_impact,
                    'level': self._get_verification_level(verification_score),
                    'findings': findings,
                    'summary': summary,
                    'fact_checks': fact_checks,
                    'verification_score': verification_score,
                    'statistics': {
                        'total_claims': len(fact_checks),
                        'verified_claims': sum(1 for fc in fact_checks if fc['verdict'] != 'unverified'),
                        'true_claims': sum(1 for fc in fact_checks if fc['verdict'] in ['true', 'likely_true']),
                        'false_claims': sum(1 for fc in fact_checks if fc['verdict'] in ['false', 'likely_false']),
                        'partially_true': sum(1 for fc in fact_checks if fc['verdict'] == 'partially_true'),
                        'average_confidence': sum(fc.get('confidence', 0) for fc in fact_checks) / max(len(fact_checks), 1),
                        'ai_enhanced_claims': sum(1 for fc in fact_checks if 'ai_analysis' in fc)
                    }
                },
                'metadata': {
                    'processing_time': time.time() - start_time,
                    'claims_found': len(claims),
                    'sources_used': self._get_sources_used(fact_checks),
                    'api_keys_available': {
                        'google_fact_check': bool(self.google_api_key),
                        'news_api': bool(self.news_api_key)
                    },
                    'ai_enhanced': self._ai_available
                }
            }
            
        except Exception as e:
            logger.error(f"Fact checking failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _extract_claims(self, text: str) -> List[str]:
        """Extract verifiable claims from text"""
        claims = []
        sentences = self._split_into_sentences(text)
        
        for sentence in sentences:
            if self._is_verifiable_claim(sentence):
                claims.append(sentence.strip())
        
        # Limit and prioritize claims
        prioritized = self._prioritize_claims(claims)
        return prioritized[:15]  # Check up to 15 claims
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences more accurately"""
        # Handle common abbreviations
        text = re.sub(r'\b(Dr|Mr|Mrs|Ms|Prof|Sr|Jr)\.\s*', r'\1<PERIOD> ', text)
        text = re.sub(r'\b(Inc|Ltd|Corp|Co)\.\s*', r'\1<PERIOD> ', text)
        text = re.sub(r'\b(Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.\s*', r'\1<PERIOD> ', text)
        
        # Split on sentence endings
        sentences = re.split(r'[.!?]+\s+', text)
        
        # Restore periods
        sentences = [s.replace('<PERIOD>', '.') for s in sentences if s.strip()]
        
        return sentences
    
    def _is_verifiable_claim(self, sentence: str) -> bool:
        """Determine if a sentence contains a verifiable claim"""
        sentence_lower = sentence.lower()
        
        # Skip opinions and subjective statements
        opinion_indicators = ['i think', 'i believe', 'in my opinion', 'it seems', 
                            'arguably', 'perhaps', 'maybe', 'possibly']
        if any(indicator in sentence_lower for indicator in opinion_indicators):
            return False
        
        # Look for factual claim indicators
        for pattern in self.claim_patterns['claim_indicators']:
            if re.search(pattern, sentence, re.IGNORECASE):
                return True
        
        # Look for specific fact patterns
        for pattern in self.claim_patterns['fact_patterns']:
            if re.search(pattern, sentence, re.IGNORECASE):
                return True
        
        return False
    
    def _prioritize_claims(self, claims: List[str]) -> List[str]:
        """Prioritize claims by importance and verifiability"""
        scored_claims = []
        
        for claim in claims:
            score = self._score_claim_priority(claim)
            scored_claims.append((score, claim))
        
        # Sort by score (descending) and return claims
        scored_claims.sort(reverse=True)
        return [claim for score, claim in scored_claims]
    
    def _score_claim_priority(self, claim: str) -> int:
        """Score claim priority based on various factors"""
        score = 0
        claim_lower = claim.lower()
        
        # High priority patterns
        high_priority = {
            r'\b(?:death|kill|die|fatal|deadly)\b': 30,
            r'\b(?:cure|treatment|vaccine|drug)\b': 25,
            r'\b(?:million|billion)\s+(?:people|dollars|deaths)\b': 25,
            r'\b(?:cancer|covid|pandemic|epidemic)\b': 20,
            r'\b(?:election|vote|fraud|rigged)\b': 20,
            r'\b(?:climate|global warming|temperature)\b': 15,
            r'\b(?:study|research|scientists?)\s+(?:found|discovered|proved)\b': 15,
        }
        
        # Check patterns
        for pattern, points in high_priority.items():
            if re.search(pattern, claim_lower):
                score += points
        
        # Boost for specific numbers and percentages
        numbers = re.findall(r'\b\d+(?:\.\d+)?\s*%?\b', claim)
        score += len(numbers) * 5
        
        # Boost for named entities (likely proper nouns)
        capital_words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', claim)
        score += len(capital_words) * 3
        
        # Penalty for hedging language
        if re.search(r'\b(?:may|might|could|possibly|perhaps)\b', claim_lower):
            score -= 10
        
        return score
    
    def _check_claims(self, claims: List[str], article_url: Optional[str] = None,
                     article_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Check multiple claims using available sources"""
        fact_checks = []
        
        for i, claim in enumerate(claims):
            # Handle both string claims and dict claims (with AI enhancement)
            if isinstance(claim, dict):
                claim_text = claim['text']
                ai_data = claim.get('ai_data', {})
            else:
                claim_text = claim
                ai_data = {}
            
            # Check cache first
            cache_key = self._get_cache_key(claim_text)
            cached_result = self._get_cached_result(cache_key)
            
            if cached_result:
                cached_result['from_cache'] = True
                fact_checks.append(cached_result)
                continue
            
            # Perform fact check
            result = self._check_single_claim(claim_text, i, article_url, article_date)
            
            # Add AI enhancement if available
            if ai_data:
                result['ai_analysis'] = ai_data
                
                # Use AI red flags to adjust confidence
                if ai_data.get('red_flags'):
                    result['confidence'] = max(0, result['confidence'] - 10 * len(ai_data['red_flags']))
                    result['evidence'].extend([f"AI flag: {flag}" for flag in ai_data['red_flags'][:2]])
            
            fact_checks.append(result)
            
            # Cache the result
            self._cache_result(cache_key, result)
            
            # Rate limiting
            if i < len(claims) - 1:
                time.sleep(0.1)  # Small delay between checks
        
        return fact_checks
    
    def _check_single_claim(self, claim: str, index: int, 
                           article_url: Optional[str], 
                           article_date: Optional[str]) -> Dict[str, Any]:
        """Check a single claim using multiple methods"""
        result = {
            'claim': claim[:300] + '...' if len(claim) > 300 else claim,
            'verdict': 'unverified',
            'explanation': 'Unable to verify this claim',
            'confidence': 0,
            'sources': [],
            'evidence': [],
            'checked_at': datetime.now().isoformat()
        }
        
        methods_tried = []
        
        # 1. Try Google Fact Check API first (if available)
        if self.google_api_key:
            google_result = self._check_google_fact_check(claim)
            if google_result and google_result.get('found'):
                result.update(google_result['data'])
                methods_tried.append('Google Fact Check API')
        
        # 2. Pattern analysis (always available)
        pattern_result = self._analyze_claim_patterns(claim)
        if pattern_result['confidence'] > result['confidence']:
            result.update(pattern_result)
            methods_tried.append('Pattern Analysis')
        
        # 3. Cross-reference with news (if API available and needed)
        if self.news_api_key and result['confidence'] < 70:
            news_result = self._cross_reference_news(claim)
            if news_result['found']:
                result['confidence'] = min(result['confidence'] + 20, 95)
                result['sources'].extend(news_result['sources'])
                result['evidence'].extend(news_result['evidence'])
                methods_tried.append('News Cross-Reference')
        
        # 4. Statistical verification (for claims with numbers)
        if self._contains_statistics(claim):
            stat_result = self._verify_statistics(claim)
            if stat_result['checked']:
                result['evidence'].append(stat_result['analysis'])
                if not stat_result['plausible']:
                    result['verdict'] = 'likely_false'
                    result['confidence'] = max(result['confidence'], 70)
                methods_tried.append('Statistical Analysis')
        
        # Update metadata
        result['methods_used'] = methods_tried
        result['priority'] = self._get_claim_priority(claim)
        
        return result
    
    def _check_google_fact_check(self, claim: str) -> Optional[Dict[str, Any]]:
        """Check claim using Google Fact Check API with timeout"""
        if not self.google_api_key:
            return None
        
        # Get timeout from config - PATCHED
        timeout = self.config.options.get('web_request_timeout', 5)
        
        try:
            response = self.session.get(
                self.GOOGLE_FACT_CHECK_ENDPOINT,
                params={
                    'query': claim,
                    'key': self.google_api_key,
                    'languageCode': 'en'
                },
                timeout=timeout  # Use configured timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if 'claims' in data and data['claims']:
                    # Process multiple fact checks
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
                                publisher_name = review['publisher'].get('name', 'Unknown')
                                publishers.append(publisher_name)
                            if 'url' in review:
                                urls.append(review['url'])
                    
                    # Determine consensus
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
            logger.error(f"Google Fact Check API error: {e}")
            return {'found': False}
    
    def _analyze_claim_patterns(self, claim: str) -> Dict[str, Any]:
        """Analyze claim using pattern matching and heuristics"""
        result = {
            'verdict': 'unverified',
            'explanation': 'Pattern-based analysis',
            'confidence': 30,
            'sources': ['Pattern Analysis Engine'],
            'evidence': []
        }
        
        claim_lower = claim.lower()
        confidence_modifiers = []
        evidence_points = []
        
        # Check for red flag patterns (likely false)
        false_patterns = {
            r'\b(?:always|never|all|none|every|no one)\b': ('absolute language', -20),
            r'\b100%\s+(?:safe|effective|proven)\b': ('impossible certainty', -25),
            r'\b(?:miracle|breakthrough|revolutionary)\s+(?:cure|treatment)\b': ('hyperbolic medical claim', -30),
            r'\bthey don\'t want you to know\b': ('conspiracy language', -25),
            r'\b(?:secret|hidden|suppressed)\s+(?:cure|treatment|truth)\b': ('conspiracy theory', -25),
            r'\bdoctors hate (?:him|her|this)\b': ('clickbait pattern', -20)
        }
        
        # Check for credible patterns (likely true)
        true_patterns = {
            r'\baccording to (?:a |the )?(?:CDC|WHO|FDA|NIH)\b': ('authoritative source', 20),
            r'\bpeer[- ]reviewed (?:study|research)\b': ('academic source', 15),
            r'\bpublished in (?:Nature|Science|NEJM|JAMA|The Lancet)\b': ('top journal', 20),
            r'\b(?:confirmed|verified) by (?:multiple|independent) sources\b': ('multi-source verification', 15)
        }
        
        # Apply patterns
        for pattern, (description, modifier) in false_patterns.items():
            if re.search(pattern, claim_lower):
                confidence_modifiers.append(modifier)
                evidence_points.append(f"Red flag: {description}")
                result['confidence'] = max(0, result['confidence'] + modifier)
        
        for pattern, (description, modifier) in true_patterns.items():
            if re.search(pattern, claim_lower):
                confidence_modifiers.append(modifier)
                evidence_points.append(f"Credibility indicator: {description}")
                result['confidence'] = min(100, result['confidence'] + modifier)
        
        # Determine verdict based on confidence
        if result['confidence'] >= 70:
            result['verdict'] = 'likely_true'
            result['explanation'] = 'Claim shows credible patterns'
        elif result['confidence'] <= 20:
            result['verdict'] = 'likely_false'
            result['explanation'] = 'Claim shows suspicious patterns'
        else:
            result['verdict'] = 'uncertain'
            result['explanation'] = 'Mixed signals, further verification needed'
        
        result['evidence'] = evidence_points
        
        return result
    
    def _cross_reference_news(self, claim: str) -> Dict[str, Any]:
        """Cross-reference claim with news sources"""
        if not self.news_api_key:
            return {'found': False}
        
        try:
            # Extract key terms from claim
            key_terms = self._extract_key_terms(claim)
            query = ' '.join(key_terms[:3])  # Use top 3 terms
            
            url = 'https://newsapi.org/v2/everything'
            params = {
                'q': query,
                'apiKey': self.news_api_key,
                'sortBy': 'relevancy',
                'pageSize': 5,
                'language': 'en'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                if articles:
                    sources = []
                    evidence = []
                    
                    for article in articles[:3]:
                        source = article.get('source', {}).get('name', 'Unknown')
                        sources.append(source)
                        
                        title = article.get('title', '')
                        if title:
                            evidence.append(f"Reported by {source}: {title}")
                    
                    return {
                        'found': True,
                        'sources': sources,
                        'evidence': evidence
                    }
            
            return {'found': False}
            
        except Exception as e:
            logger.error(f"News cross-reference failed: {e}")
            return {'found': False}
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text for search"""
        # Remove common words
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                    'of', 'with', 'by', 'from', 'is', 'was', 'are', 'were', 'been', 'be',
                    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                    'should', 'may', 'might', 'must', 'can', 'that', 'this', 'these', 'those'}
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Filter and count
        word_counts = Counter(word for word in words if word not in stopwords and len(word) > 2)
        
        # Return most common terms
        return [word for word, count in word_counts.most_common(5)]
    
    def _contains_statistics(self, claim: str) -> bool:
        """Check if claim contains statistical information"""
        stat_patterns = [
            r'\b\d+(?:\.\d+)?\s*(?:percent|%)',
            r'\b\d+\s*(?:million|billion|thousand)',
            r'\b\d+\s*(?:times|fold)\b',
            r'\b(?:increased?|decreased?|grew|fell)\s+(?:by\s+)?\d+'
        ]
        
        return any(re.search(pattern, claim, re.IGNORECASE) for pattern in stat_patterns)
    
    def _verify_statistics(self, claim: str) -> Dict[str, Any]:
        """Verify statistical claims for plausibility"""
        result = {
            'checked': False,
            'plausible': True,
            'analysis': ''
        }
        
        # Extract percentages
        percentages = re.findall(r'(\d+(?:\.\d+)?)\s*(?:percent|%)', claim, re.IGNORECASE)
        for pct in percentages:
            value = float(pct)
            if value > 100:
                result['checked'] = True
                result['plausible'] = False
                result['analysis'] = f"Impossible percentage: {value}% exceeds 100%"
                return result
        
        # Check for unrealistic numbers
        large_numbers = re.findall(r'(\d+)\s*(million|billion|trillion)', claim, re.IGNORECASE)
        for number, unit in large_numbers:
            value = int(number)
            if unit.lower() == 'billion' and value > 100:
                result['checked'] = True
                result['analysis'] = f"Extremely large number: {value} billion (verify context)"
            elif unit.lower() == 'trillion' and value > 10:
                result['checked'] = True
                result['plausible'] = False
                result['analysis'] = f"Implausible number: {value} trillion"
        
        # Check for impossible growth rates
        growth_patterns = re.findall(r'(?:increased?|grew)\s+(?:by\s+)?(\d+)(?:\s*times|\s*fold)?', claim, re.IGNORECASE)
        for growth in growth_patterns:
            value = int(growth)
            if value > 1000:
                result['checked'] = True
                result['plausible'] = False
                result['analysis'] = f"Implausible growth: {value}x increase"
        
        if result['checked'] and result['plausible']:
            result['analysis'] = "Statistical claims appear plausible"
        
        return result
    
    def _determine_consensus_verdict(self, verdicts: List[str]) -> str:
        """Determine consensus from multiple fact check verdicts"""
        if not verdicts:
            return 'unverified'
        
        # Normalize verdicts
        normalized = []
        for verdict in verdicts:
            verdict_lower = verdict.lower()
            if any(word in verdict_lower for word in ['true', 'correct', 'accurate']):
                normalized.append('true')
            elif any(word in verdict_lower for word in ['false', 'incorrect', 'wrong']):
                normalized.append('false')
            elif any(word in verdict_lower for word in ['partly', 'partially', 'mixed']):
                normalized.append('partially_true')
            else:
                normalized.append('uncertain')
        
        # Count verdicts
        verdict_counts = Counter(normalized)
        
        # Determine consensus
        if verdict_counts['false'] > verdict_counts['true']:
            return 'false'
        elif verdict_counts['true'] > verdict_counts['false']:
            return 'true'
        elif verdict_counts['partially_true'] > 0:
            return 'partially_true'
        else:
            return 'uncertain'
    
    def _calculate_api_confidence(self, verdicts: List[str], publishers: List[str]) -> int:
        """Calculate confidence based on API results"""
        if not verdicts:
            return 30
        
        base_confidence = 60
        
        # More verdicts = higher confidence
        base_confidence += min(len(verdicts) * 10, 30)
        
        # Consistent verdicts = higher confidence
        unique_verdicts = len(set(verdicts))
        if unique_verdicts == 1:
            base_confidence += 10
        
        # Known publishers = higher confidence
        known_publishers = ['Snopes', 'FactCheck.org', 'PolitiFact', 'Reuters', 'AP']
        if any(pub in publishers for pub in known_publishers):
            base_confidence += 10
        
        return min(base_confidence, 95)
    
    def _get_claim_priority(self, claim: str) -> str:
        """Determine claim priority level"""
        score = self._score_claim_priority(claim)
        
        if score >= 50:
            return 'high'
        elif score >= 25:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_verification_score(self, fact_checks: List[Dict[str, Any]]) -> int:
        """Calculate overall verification score"""
        if not fact_checks:
            return 100
        
        total_score = 0
        total_weight = 0
        
        for fc in fact_checks:
            # Weight by priority
            weight = {'high': 3, 'medium': 2, 'low': 1}.get(fc.get('priority', 'medium'), 2)
            
            # Score by verdict
            if fc['verdict'] in ['true', 'likely_true']:
                score = 100
            elif fc['verdict'] == 'partially_true':
                score = 60
            elif fc['verdict'] in ['false', 'likely_false']:
                score = 20
            elif fc['verdict'] == 'uncertain':
                score = 50
            else:  # unverified
                score = 40
            
            # Adjust by confidence
            confidence = fc.get('confidence', 50) / 100
            adjusted_score = score * confidence
            
            total_score += adjusted_score * weight
            total_weight += weight
        
        return round(total_score / total_weight) if total_weight > 0 else 50
    
    def _calculate_trust_impact(self, fact_checks: List[Dict[str, Any]]) -> int:
        """Calculate impact on trust score"""
        if not fact_checks:
            return 100
        
        # Start with neutral score
        trust_score = 70
        
        # Adjust based on false claims
        false_claims = sum(1 for fc in fact_checks if fc['verdict'] in ['false', 'likely_false'])
        true_claims = sum(1 for fc in fact_checks if fc['verdict'] in ['true', 'likely_true'])
        
        # Heavy penalty for false claims
        trust_score -= false_claims * 15
        
        # Small bonus for verified true claims
        trust_score += true_claims * 5
        
        # Ensure within bounds
        return max(0, min(100, trust_score))
    
    def _generate_findings(self, fact_checks: List[Dict[str, Any]], verification_score: int) -> List[Dict[str, Any]]:
        """Generate findings from fact checks"""
        findings = []
        
        # Count verdicts
        false_count = sum(1 for fc in fact_checks if fc['verdict'] in ['false', 'likely_false'])
        true_count = sum(1 for fc in fact_checks if fc['verdict'] in ['true', 'likely_true'])
        unverified_count = sum(1 for fc in fact_checks if fc['verdict'] == 'unverified')
        
        # Overall verification finding
        if verification_score >= 80:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': 'Most claims are well-verified',
                'explanation': f'{true_count} of {len(fact_checks)} claims verified as accurate'
            })
        elif verification_score < 40:
            findings.append({
                'type': 'critical',
                'severity': 'high',
                'text': 'Multiple false or misleading claims',
                'explanation': f'{false_count} claims appear to be false or misleading'
            })
        
        # Specific false claim warnings
        for fc in fact_checks:
            if fc['verdict'] in ['false', 'likely_false'] and fc.get('priority') == 'high':
                findings.append({
                    'type': 'warning',
                    'severity': 'high',
                    'text': f'False claim: "{fc["claim"][:100]}..."',
                    'explanation': fc.get('explanation', 'Claim contradicted by fact checkers')
                })
        
        # Unverified claims
        if unverified_count > len(fact_checks) * 0.5:
            findings.append({
                'type': 'info',
                'severity': 'medium',
                'text': 'Many claims could not be verified',
                'explanation': 'Limited fact-checking sources available for these claims'
            })
        
        # AI enhancement finding
        ai_enhanced = sum(1 for fc in fact_checks if 'ai_analysis' in fc)
        if ai_enhanced > 0:
            findings.append({
                'type': 'info',
                'severity': 'low',
                'text': f'AI-enhanced analysis for {ai_enhanced} claims',
                'explanation': 'Additional verification strategies suggested by AI'
            })
        
        return findings[:5]  # Limit to 5 most important findings
    
    def _generate_summary(self, fact_checks: List[Dict[str, Any]], verification_score: int) -> str:
        """Generate fact checking summary"""
        if not fact_checks:
            return "No fact-checkable claims were found in this article."
        
        total = len(fact_checks)
        verified = sum(1 for fc in fact_checks if fc['verdict'] != 'unverified')
        true_claims = sum(1 for fc in fact_checks if fc['verdict'] in ['true', 'likely_true'])
        false_claims = sum(1 for fc in fact_checks if fc['verdict'] in ['false', 'likely_false'])
        
        summary = f"Analyzed {total} fact-checkable claims. "
        
        if verified > 0:
            summary += f"{verified} claims were verified: "
            if true_claims > 0:
                summary += f"{true_claims} true"
            if false_claims > 0:
                if true_claims > 0:
                    summary += f", {false_claims} false"
                else:
                    summary += f"{false_claims} false"
            summary += ". "
        
        if verification_score >= 80:
            summary += "Most claims are well-supported by evidence."
        elif verification_score >= 60:
            summary += "Mixed accuracy with some questionable claims."
        elif verification_score >= 40:
            summary += "Several claims lack support or are disputed."
        else:
            summary += "Many claims appear to be false or misleading."
        
        return summary
    
    def _get_verification_level(self, score: int) -> str:
        """Convert verification score to level"""
        if score >= 80:
            return 'Well Verified'
        elif score >= 60:
            return 'Mostly Verified'
        elif score >= 40:
            return 'Partially Verified'
        elif score >= 20:
            return 'Poorly Verified'
        else:
            return 'Unverified'
    
    def _get_sources_used(self, fact_checks: List[Dict[str, Any]]) -> List[str]:
        """Get unique sources used in fact checking"""
        sources = set()
        
        for fc in fact_checks:
            if 'sources' in fc:
                sources.update(fc['sources'])
            if 'methods_used' in fc:
                sources.update(fc['methods_used'])
        
        return list(sources)
    
    def _get_cache_key(self, claim: str) -> str:
        """Generate cache key for claim"""
        return hashlib.sha256(claim.encode()).hexdigest()[:16]
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached result if available and not expired"""
        if cache_key in self.cache:
            cached_time, result = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                return result.copy()
        return None
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]):
        """Cache fact check result"""
        self.cache[cache_key] = (time.time(), result.copy())
        
        # Limit cache size
        if len(self.cache) > 1000:
            # Remove oldest entries
            sorted_items = sorted(self.cache.items(), key=lambda x: x[1][0])
            for key, _ in sorted_items[:100]:
                del self.cache[key]
    
    def _initialize_claim_patterns(self) -> Dict[str, Any]:
        """Initialize patterns for claim extraction and analysis"""
        return {
            'claim_indicators': [
                r'\b(?:study|research|report|survey) (?:shows?|finds?|indicates?|suggests?)\b',
                r'\b(?:according to|based on|as reported by)\b',
                r'\b(?:data|statistics|numbers|figures) (?:show|indicate|reveal)\b',
                r'\b(?:scientists?|researchers?|experts?) (?:say|claim|believe|found)\b',
                r'\b(?:evidence|proof|analysis) (?:shows?|demonstrates?|indicates?)\b',
            ],
            'fact_patterns': [
                r'\b\d+\s*(?:percent|%)\s+of\b',
                r'\b(?:increased?|decreased?|rose|fell) by \d+',
                r'\b(?:first|last|only|largest|smallest|biggest)\b',
                r'\b(?:caused?|leads? to|results? in|linked to)\b',
            ]
        }
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about the service"""
        info = super().get_service_info()
        info.update({
            'capabilities': [
                'Google Fact Check API integration',
                'Pattern-based claim analysis',
                'Statistical verification',
                'News cross-referencing',
                'Multi-source verification',
                'AI-ENHANCED claim prioritization',
                'AI-powered verification strategies'
            ],
            'api_status': {
                'google_fact_check': 'active' if self.google_api_key else 'not configured',
                'news_api': 'active' if self.news_api_key else 'not configured',
                'openai': 'active' if self._ai_available else 'not configured'
            },
            'claim_limit': 15,
            'cache_enabled': True,
            'cache_ttl': self.cache_ttl,
            'ai_enhanced': self._ai_available
        })
        return info
