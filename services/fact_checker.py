"""
Fact Checker Service
Comprehensive fact checking using Google Fact Check API and multiple verification sources
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

logger = logging.getLogger(__name__)


class FactChecker(BaseAnalyzer):
    """
    Fact checking service using Google Fact Check API and multiple verification sources
    """
    
    def __init__(self):
        """Initialize the fact checker with API keys and configuration"""
        super().__init__('fact_checker')
        
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
        
        logger.info(f"FactChecker initialized - Google API: {bool(self.google_api_key)}, "
                   f"News API: {bool(self.news_api_key)}")
    
    def _check_availability(self) -> bool:
        """Check if the service has required dependencies"""
        # Service can work with pattern analysis even without API keys
        return True
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform fact checking analysis
        
        Expected input:
            - text: Article text to analyze
            - title: Article title (optional)
            - url: Article URL (optional)
            - published_date: Publication date (optional)
            - claims: Pre-extracted claims (optional)
        """
        try:
            start_time = time.time()
            
            # Extract or get claims
            if 'claims' in data and data['claims']:
                claims = data['claims']
            else:
                text = data.get('text', '')
                title = data.get('title', '')
                full_text = f"{title} {text}" if title else text
                
                if not full_text:
                    return self.get_error_result("No text provided for fact checking")
                
                claims = self._extract_claims(full_text)
            
            if not claims:
                return {
                    'service': self.service_name,
                    'success': True,
                    'data': {
                        'score': 100,  # No claims to verify
                        'level': 'No Claims',
                        'findings': [],
                        'summary': 'No verifiable claims found in the article',
                        'fact_checks': [],
                        'verification_score': 100
                    },
                    'metadata': {
                        'processing_time': time.time() - start_time,
                        'claims_found': 0
                    }
                }
            
            # Check claims
            fact_checks = self._check_claims(
                claims,
                article_url=data.get('url'),
                article_date=data.get('published_date')
            )
            
            # Calculate scores and summary
            verification_score = self._calculate_verification_score(fact_checks)
            trust_impact = self._calculate_trust_impact(fact_checks)
            findings = self._generate_findings(fact_checks)
            
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
                        'average_confidence': sum(fc.get('confidence', 0) for fc in fact_checks) / max(len(fact_checks), 1)
                    }
                },
                'metadata': {
                    'processing_time': time.time() - start_time,
                    'claims_found': len(claims),
                    'sources_used': self._get_sources_used(fact_checks),
                    'api_keys_available': {
                        'google_fact_check': bool(self.google_api_key),
                        'news_api': bool(self.news_api_key)
                    }
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
        sentences = [s.replace('<PERIOD>', '.') for s in sentences]
        
        # Filter out very short sentences
        return [s for s in sentences if len(s.split()) > 5]
    
    def _is_verifiable_claim(self, sentence: str) -> bool:
        """Determine if a sentence contains a verifiable claim"""
        sentence_lower = sentence.lower()
        
        # Must contain patterns
        must_patterns = [
            r'\b\d+\s*(?:percent|%)\b',  # Percentages
            r'\b(?:million|billion|thousand|hundred)\b',  # Large numbers
            r'\b(?:study|research|report|survey|poll)\b',  # Research references
            r'\b(?:increased|decreased|rose|fell|grew|declined)\b',  # Trends
            r'\b(?:data|statistics|numbers|figures)\b',  # Data references
            r'\b(?:according to|reported|found|discovered)\b',  # Attribution
            r'\b(?:caused|leads to|results in|due to)\b',  # Causation
            r'\b(?:first|last|only|largest|smallest|biggest)\b',  # Superlatives
            r'\b(?:always|never|all|none|every)\b',  # Absolutes
            r'\b(?:proven|confirmed|verified|established)\b',  # Certainty claims
        ]
        
        # Avoid patterns (not verifiable)
        avoid_patterns = [
            r'\b(?:I think|I believe|I feel|in my opinion)\b',  # Opinions
            r'\b(?:maybe|perhaps|possibly|might|could)\b',  # Too uncertain
            r'\?$',  # Questions
            r'^(?:However|Therefore|Thus|Hence|Moreover)',  # Transition sentences
        ]
        
        # Check avoid patterns first
        for pattern in avoid_patterns:
            if re.search(pattern, sentence_lower):
                return False
        
        # Check must patterns
        for pattern in must_patterns:
            if re.search(pattern, sentence_lower):
                return True
        
        return False
    
    def _prioritize_claims(self, claims: List[str]) -> List[str]:
        """Prioritize claims by importance and verifiability"""
        scored_claims = []
        
        for claim in claims:
            score = self._calculate_claim_priority_score(claim)
            scored_claims.append((claim, score))
        
        # Sort by score (highest first)
        scored_claims.sort(key=lambda x: x[1], reverse=True)
        
        return [claim for claim, _ in scored_claims]
    
    def _calculate_claim_priority_score(self, claim: str) -> float:
        """Calculate priority score for a claim"""
        score = 0.0
        claim_lower = claim.lower()
        
        # High priority indicators
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
            # Check cache first
            cache_key = self._get_cache_key(claim)
            cached_result = self._get_cached_result(cache_key)
            
            if cached_result:
                cached_result['from_cache'] = True
                fact_checks.append(cached_result)
                continue
            
            # Perform fact check
            result = self._check_single_claim(claim, i, article_url, article_date)
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
            google_result = self._check_with_google_api(claim)
            if google_result['found']:
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
    
    def _check_with_google_api(self, claim: str) -> Dict[str, Any]:
        """Check claim using Google Fact Check API"""
        try:
            url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
            
            params = {
                'key': self.google_api_key,
                'query': claim[:200],  # API has query length limits
                'languageCode': 'en',
                'pageSize': 5
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
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
            r'\b(?:big pharma|deep state|mainstream media)\b': ('conspiracy terminology', -20),
            r'\bone weird trick\b': ('clickbait pattern', -15),
        }
        
        for pattern, (description, modifier) in false_patterns.items():
            if re.search(pattern, claim_lower):
                evidence_points.append(f"Contains {description}")
                confidence_modifiers.append(modifier)
                result['verdict'] = 'likely_false'
        
        # Check for credible patterns (likely true)
        true_patterns = {
            r'according to (?:a |the )?(?:\d{4} )?(?:study|research|report) (?:published |)(?:in|by)': 
                ('cited research', 25),
            r'(?:approximately|about|around|nearly|roughly) \d+': 
                ('qualified numbers', 15),
            r'between \d+ and \d+': 
                ('range instead of absolute', 15),
            r'\b(?:may|might|could|potentially)\b': 
                ('appropriately cautious language', 10),
            r'peer[- ]reviewed': 
                ('peer-reviewed source', 20),
        }
        
        for pattern, (description, modifier) in true_patterns.items():
            if re.search(pattern, claim_lower):
                evidence_points.append(f"Uses {description}")
                confidence_modifiers.append(modifier)
                if result['verdict'] == 'unverified':
                    result['verdict'] = 'likely_true'
        
        # Check for mixed signals
        if len([m for m in confidence_modifiers if m > 0]) > 0 and \
           len([m for m in confidence_modifiers if m < 0]) > 0:
            result['verdict'] = 'partially_true'
            evidence_points.append("Contains both credible and questionable elements")
        
        # Calculate final confidence
        base_confidence = 50
        total_modifier = sum(confidence_modifiers)
        result['confidence'] = max(10, min(90, base_confidence + total_modifier))
        
        # Set explanation
        if evidence_points:
            result['explanation'] = f"Pattern analysis: {'; '.join(evidence_points[:2])}"
        
        result['evidence'] = evidence_points
        
        return result
    
    def _cross_reference_news(self, claim: str) -> Dict[str, Any]:
        """Cross-reference claim with recent news articles"""
        try:
            # Extract key terms for search
            key_terms = self._extract_key_search_terms(claim)
            search_query = ' '.join(key_terms)
            
            url = "https://newsapi.org/v2/everything"
            params = {
                'apiKey': self.news_api_key,
                'q': search_query,
                'searchIn': 'title,description',
                'sortBy': 'relevancy',
                'pageSize': 10,
                'language': 'en'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('articles'):
                    # Analyze coverage
                    reputable_sources = []
                    coverage_count = 0
                    
                    for article in data['articles']:
                        source = article.get('source', {}).get('name', '')
                        if self._is_reputable_news_source(source):
                            reputable_sources.append(source)
                            coverage_count += 1
                    
                    if coverage_count >= 2:
                        return {
                            'found': True,
                            'sources': list(set(reputable_sources))[:3],
                            'evidence': [f"Reported by {coverage_count} reputable news sources"],
                            'coverage_level': 'high' if coverage_count >= 3 else 'moderate'
                        }
            
            return {'found': False}
            
        except Exception as e:
            logger.error(f"News cross-reference error: {e}")
            return {'found': False}
    
    def _verify_statistics(self, claim: str) -> Dict[str, Any]:
        """Verify statistical claims for plausibility"""
        result = {
            'checked': False,
            'plausible': True,
            'analysis': ''
        }
        
        # Extract numbers and check for issues
        issues = []
        
        # Check percentages
        percentages = re.findall(r'(\d+(?:\.\d+)?)\s*%', claim)
        for pct_str in percentages:
            pct = float(pct_str)
            if pct > 100:
                issues.append(f"Impossible percentage: {pct}%")
                result['plausible'] = False
            elif pct == 100 or pct == 0:
                issues.append(f"Suspicious absolute percentage: {pct}%")
        
        # Check for contradictions
        if re.search(r'increased.*decreased|decreased.*increased', claim.lower()):
            issues.append("Contains contradictory trends")
            result['plausible'] = False
        
        # Check number magnitude consistency
        numbers = re.findall(r'\b(\d+(?:,\d{3})*(?:\.\d+)?)\b', claim)
        if numbers:
            parsed_numbers = []
            for num_str in numbers:
                try:
                    num = float(num_str.replace(',', ''))
                    parsed_numbers.append(num)
                except:
                    continue
            
            # Check for scale inconsistencies
            if len(parsed_numbers) >= 2:
                max_num = max(parsed_numbers)
                min_num = min(parsed_numbers)
                if min_num > 0 and max_num / min_num > 10000:
                    issues.append("Numbers vary by more than 4 orders of magnitude")
        
        if issues:
            result['analysis'] = f"Statistical issues: {'; '.join(issues)}"
            result['checked'] = True
        elif numbers or percentages:
            result['analysis'] = "Statistical claims appear plausible"
            result['checked'] = True
        
        return result
    
    def _contains_statistics(self, claim: str) -> bool:
        """Check if claim contains statistical information"""
        stat_patterns = [
            r'\b\d+\s*%',  # Percentages
            r'\b\d+(?:,\d{3})*(?:\.\d+)?\b',  # Numbers
            r'\b(?:million|billion|thousand)\b',  # Scale words
            r'\b(?:increase|decrease|rise|fall|grew|declined)\b',  # Trends
            r'\b(?:average|median|mean)\b',  # Statistical terms
        ]
        
        return any(re.search(pattern, claim) for pattern in stat_patterns)
    
    def _determine_consensus_verdict(self, verdicts: List[str]) -> str:
        """Determine consensus from multiple fact check verdicts"""
        if not verdicts:
            return 'unverified'
        
        # Normalize verdicts
        normalized = []
        for verdict in verdicts:
            verdict_lower = verdict.lower()
            if any(term in verdict_lower for term in ['false', 'incorrect', 'wrong', 'misleading', 'fake']):
                normalized.append('false')
            elif any(term in verdict_lower for term in ['true', 'correct', 'accurate', 'right']):
                normalized.append('true')
            elif any(term in verdict_lower for term in ['partly', 'partially', 'mixed', 'half']):
                normalized.append('partially_true')
            else:
                normalized.append('unverified')
        
        # Get most common verdict
        verdict_counts = Counter(normalized)
        most_common = verdict_counts.most_common(1)[0][0]
        
        # Add likely_ prefix if not unanimous
        if len(set(normalized)) > 1:
            if most_common in ['true', 'false']:
                return f'likely_{most_common}'
        
        return most_common
    
    def _calculate_api_confidence(self, verdicts: List[str], publishers: List[str]) -> int:
        """Calculate confidence based on API results"""
        base_confidence = 70
        
        # Boost for multiple verdicts
        confidence = base_confidence + (len(verdicts) * 5)
        
        # Boost for reputable publishers
        reputable_count = sum(1 for p in publishers if self._is_reputable_fact_checker(p))
        confidence += reputable_count * 10
        
        # Cap at 95
        return min(confidence, 95)
    
    def _is_reputable_fact_checker(self, publisher: str) -> bool:
        """Check if fact-checking organization is reputable"""
        reputable = {
            'snopes', 'factcheck.org', 'politifact', 'associated press',
            'reuters', 'afp fact check', 'full fact', 'africa check',
            'chequeado', 'correctiv', 'les décodeurs', 'pagella politica'
        }
        
        publisher_lower = publisher.lower()
        return any(org in publisher_lower for org in reputable)
    
    def _is_reputable_news_source(self, source: str) -> bool:
        """Check if news source is reputable"""
        reputable = {
            'reuters', 'associated press', 'ap news', 'bbc', 'the guardian',
            'new york times', 'washington post', 'wall street journal',
            'financial times', 'the economist', 'npr', 'pbs', 'cnn',
            'abc news', 'nbc news', 'cbs news', 'bloomberg', 'the atlantic'
        }
        
        source_lower = source.lower()
        return any(org in source_lower for org in reputable)
    
    def _extract_key_search_terms(self, claim: str) -> List[str]:
        """Extract key terms for searching"""
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are',
            'were', 'been', 'be', 'have', 'has', 'had', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can', 'that', 'this'
        }
        
        words = re.findall(r'\b\w+\b', claim.lower())
        key_terms = []
        
        # Prioritize proper nouns (capitalized in original)
        for match in re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', claim):
            key_terms.append(match.lower())
        
        # Add other significant words
        for word in words:
            if word not in stop_words and len(word) > 2 and word not in key_terms:
                key_terms.append(word)
        
        return key_terms[:6]  # Limit to 6 terms
    
    def _get_claim_priority(self, claim: str) -> str:
        """Determine claim priority level"""
        score = self._calculate_claim_priority_score(claim)
        
        if score >= 50:
            return 'high'
        elif score >= 20:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_verification_score(self, fact_checks: List[Dict[str, Any]]) -> int:
        """Calculate overall verification score"""
        if not fact_checks:
            return 100  # No claims to verify
        
        total_weight = 0
        weighted_score = 0
        
        for fc in fact_checks:
            # Weight by confidence and priority
            confidence = fc.get('confidence', 0)
            priority_weights = {'high': 3, 'medium': 2, 'low': 1}
            weight = priority_weights.get(fc.get('priority', 'medium'), 2)
            
            # Score based on verdict
            verdict_scores = {
                'true': 100,
                'likely_true': 80,
                'partially_true': 50,
                'unverified': 50,
                'likely_false': 20,
                'false': 0
            }
            
            score = verdict_scores.get(fc['verdict'], 50)
            
            weighted_score += score * weight * (confidence / 100)
            total_weight += weight
        
        if total_weight > 0:
            return int(weighted_score / total_weight)
        
        return 50
    
    def _calculate_trust_impact(self, fact_checks: List[Dict[str, Any]]) -> int:
        """Calculate impact on article trust score"""
        if not fact_checks:
            return 100
        
        # Count verdicts
        false_count = sum(1 for fc in fact_checks if fc['verdict'] in ['false', 'likely_false'])
        true_count = sum(1 for fc in fact_checks if fc['verdict'] in ['true', 'likely_true'])
        partial_count = sum(1 for fc in fact_checks if fc['verdict'] == 'partially_true')
        
        # Weight by priority
        high_priority_false = sum(1 for fc in fact_checks 
                                 if fc['verdict'] in ['false', 'likely_false'] 
                                 and fc.get('priority') == 'high')
        
        # Calculate score
        total = len(fact_checks)
        base_score = ((true_count * 100) + (partial_count * 50)) / total
        
        # Apply penalties
        false_penalty = false_count * 10
        high_priority_penalty = high_priority_false * 20
        
        trust_impact = max(0, base_score - false_penalty - high_priority_penalty)
        
        return int(trust_impact)
    
    def _generate_findings(self, fact_checks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate findings from fact checks"""
        findings = []
        
        # Group by verdict
        false_claims = [fc for fc in fact_checks if fc['verdict'] in ['false', 'likely_false']]
        true_claims = [fc for fc in fact_checks if fc['verdict'] in ['true', 'likely_true']]
        partial_claims = [fc for fc in fact_checks if fc['verdict'] == 'partially_true']
        unverified_claims = [fc for fc in fact_checks if fc['verdict'] == 'unverified']
        
        # Report false claims first (most important)
        for fc in false_claims[:3]:  # Top 3 false claims
            findings.append({
                'type': 'false_claim',
                'text': fc['claim'][:150] + '...' if len(fc['claim']) > 150 else fc['claim'],
                'severity': 'high' if fc.get('priority') == 'high' else 'medium',
                'explanation': fc.get('explanation', 'Fact checkers determined this claim is false')
            })
        
        # Report partially true claims
        for fc in partial_claims[:2]:
            findings.append({
                'type': 'partial_truth',
                'text': fc['claim'][:150] + '...' if len(fc['claim']) > 150 else fc['claim'],
                'severity': 'medium',
                'explanation': fc.get('explanation', 'This claim contains both true and false elements')
            })
        
        # Summary finding if many claims couldn't be verified
        if len(unverified_claims) > 3:
            findings.append({
                'type': 'verification_difficulty',
                'text': f'{len(unverified_claims)} claims could not be verified',
                'severity': 'low',
                'explanation': 'Multiple claims lack sufficient evidence or sources for verification'
            })
        
        return findings
    
    def _generate_summary(self, fact_checks: List[Dict[str, Any]], verification_score: int) -> str:
        """Generate human-readable summary"""
        if not fact_checks:
            return "No verifiable claims found in the article."
        
        total = len(fact_checks)
        false_count = sum(1 for fc in fact_checks if fc['verdict'] in ['false', 'likely_false'])
        true_count = sum(1 for fc in fact_checks if fc['verdict'] in ['true', 'likely_true'])
        partial_count = sum(1 for fc in fact_checks if fc['verdict'] == 'partially_true')
        
        # Build summary
        summary_parts = []
        
        summary_parts.append(f"Analyzed {total} claim{'s' if total != 1 else ''}:")
        
        if false_count > 0:
            summary_parts.append(f"{false_count} false")
        if true_count > 0:
            summary_parts.append(f"{true_count} true")
        if partial_count > 0:
            summary_parts.append(f"{partial_count} partially true")
        
        summary = " - ".join(summary_parts)
        
        # Add overall assessment
        if verification_score >= 80:
            summary += ". Most claims are well-supported by evidence."
        elif verification_score >= 60:
            summary += ". Mixed accuracy with some questionable claims."
        elif verification_score >= 40:
            summary += ". Several claims lack support or are disputed."
        else:
            summary += ". Many claims appear to be false or misleading."
        
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
                'Multi-source verification'
            ],
            'api_status': {
                'google_fact_check': 'active' if self.google_api_key else 'not configured',
                'news_api': 'active' if self.news_api_key else 'not configured'
            },
            'claim_limit': 15,
            'cache_enabled': True,
            'cache_ttl': self.cache_ttl
        })
        return info
