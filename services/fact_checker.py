"""
Fact Checker Service - BULLETPROOF AI ENHANCED VERSION
Fixed AIEnhancementMixin method calls and data structure warnings
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
    Fact-check article claims using multiple sources
    FIXED: Corrected AI enhancement method calls and data structure warnings
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
        
        logger.info(f"FactChecker initialized - Google API: {bool(self.google_api_key)}")
    
    def _check_availability(self) -> bool:
        """Service is available if we have pattern matching (always) or Google API"""
        return True  # Always available with fallback methods
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze article for fact-checkable claims
        FIXED: Corrected AI method call and data structure warnings
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
            
            logger.info(f"Fact checking article with {len(content)} characters")
            
            # 1. Extract claims from content
            extracted_claims = self._extract_claims(content)
            
            # 2. AI Enhancement - FIXED: Using correct method without invalid parameters
            ai_enhanced_claims = []
            if extracted_claims:
                logger.info("Enhancing fact checking with AI")
                try:
                    # Use the correct AI method with proper parameters
                    ai_result = self._safely_enhance_service_result(
                        {'claims': extracted_claims, 'content': content[:1500]},
                        '_ai_analyze_claims',
                        claims=extracted_claims[:5],
                        article_text=content[:1500]
                    )
                    
                    if ai_result and ai_result.get('ai_insights', {}).get('enhanced_claims'):
                        enhanced_claims_data = ai_result['ai_insights']['enhanced_claims']
                        if isinstance(enhanced_claims_data, list):
                            ai_enhanced_claims = enhanced_claims_data[:10]
                        else:
                            ai_enhanced_claims = extracted_claims[:10]
                    else:
                        ai_enhanced_claims = extracted_claims[:10]
                        
                except Exception as e:
                    logger.warning(f"AI enhancement failed, using basic claims: {e}")
                    ai_enhanced_claims = extracted_claims[:10]
            else:
                ai_enhanced_claims = extracted_claims[:10]
            
            # 3. Fact check the claims
            if ai_enhanced_claims:
                fact_checks = self._check_claims(ai_enhanced_claims, article_url, article_date)
            else:
                fact_checks = []
            
            # 4. Calculate verification score
            verification_score = self._calculate_verification_score(fact_checks)
            verification_level = self._get_verification_level(verification_score)
            
            # 5. Generate summary
            summary = self._generate_fact_check_summary(fact_checks, verification_score)
            
            # 6. Identify sources used
            sources_used = self._get_sources_used(fact_checks)
            
            # FIXED: Ensure all data structure elements are properly defined
            result = {
                'service': self.service_name,
                'success': True,
                'data': {
                    'score': verification_score,
                    'level': verification_level,
                    'verification_score': verification_score,
                    'verification_level': verification_level,
                    'findings': self._generate_findings(fact_checks, verification_score),
                    'summary': summary,
                    'claims_found': len(extracted_claims),
                    'claims_checked': len(fact_checks),
                    'fact_checks': fact_checks[:10],  # Limit to prevent data bloat
                    'sources_used': sources_used,
                    'google_api_used': bool(self.google_api_key),
                    'details': {
                        'total_claims': len(extracted_claims),
                        'verified_claims': len([fc for fc in fact_checks if fc.get('verdict') in ['true', 'likely_true']]),
                        'disputed_claims': len([fc for fc in fact_checks if fc.get('verdict') in ['false', 'likely_false']]),
                        'unverified_claims': len([fc for fc in fact_checks if fc.get('verdict') == 'unverified']),
                        'average_confidence': sum(fc.get('confidence', 0) for fc in fact_checks) / max(len(fact_checks), 1)
                    }
                },
                'metadata': {
                    'analysis_time': time.time() - start_time,
                    'content_length': len(content),
                    'api_available': bool(self.google_api_key)
                }
            }
            
            logger.info(f"Fact checking complete: {len(fact_checks)} claims checked, score: {verification_score}/100")
            return result
            
        except Exception as e:
            logger.error(f"Fact checking failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _extract_claims(self, content: str) -> List[str]:
        """Extract potentially fact-checkable claims from content"""
        claims = []
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', content)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:  # Skip very short sentences
                continue
            
            # Score claim importance
            importance_score = self._score_claim_importance(sentence)
            
            if importance_score >= 15:  # Threshold for potentially fact-checkable claims
                claims.append({
                    'text': sentence,
                    'importance_score': importance_score,
                    'type': self._classify_claim_type(sentence)
                })
        
        # Sort by importance score and return top claims
        claims.sort(key=lambda x: x['importance_score'], reverse=True)
        return [claim['text'] for claim in claims[:15]]  # Return top 15 claims
    
    def _score_claim_importance(self, claim: str) -> int:
        """Score how important/fact-checkable a claim is"""
        score = 0
        claim_lower = claim.lower()
        
        # Boost for statistical claims
        if re.search(r'\b\d+\s*(?:percent|%|million|billion|thousand)\b', claim):
            score += 20
        
        # Boost for specific numbers
        numbers = re.findall(r'\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\s*%?\b', claim)
        score += len(numbers) * 5
        
        # Boost for named entities (likely proper nouns)
        capital_words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', claim)
        score += len(capital_words) * 3
        
        # Penalty for hedging language
        if re.search(r'\b(?:may|might|could|possibly|perhaps)\b', claim_lower):
            score -= 10
        
        return score
    
    def _classify_claim_type(self, claim: str) -> str:
        """Classify the type of claim"""
        claim_lower = claim.lower()
        
        if re.search(r'\b\d+\s*(?:percent|%)\b', claim):
            return 'statistical'
        elif re.search(r'\b(?:study|research|report)\b', claim_lower):
            return 'research'
        elif re.search(r'\b(?:said|stated|claimed|announced)\b', claim_lower):
            return 'quote'
        elif re.search(r'\b(?:increased|decreased|rose|fell)\b', claim_lower):
            return 'trend'
        else:
            return 'factual'
    
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
        
        # 1. Try Google Fact Check API first
        if self.google_api_key:
            google_result = self._check_google_fact_check_api(claim)
            methods_tried.append('google_api')
            
            if google_result['found']:
                result.update(google_result['data'])
                result['methods_used'] = methods_tried
                return result
        
        # 2. Pattern-based analysis as fallback
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
                'query': claim[:500],  # Limit query length
                'languageCode': 'en'
            }
            
            response = requests.get(
                url, 
                params=params, 
                timeout=10
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
            r'\b(?:miracle|breakthrough|revolutionary)\s+(?:cure|treatment|discovery)\b': ('sensational claims', -15),
            r'\b(?:doctors hate|they don\'t want you to know|hidden truth)\b': ('clickbait language', -30)
        }
        
        for pattern, (description, modifier) in false_patterns.items():
            if re.search(pattern, claim_lower):
                confidence_modifiers.append(modifier)
                evidence_points.append(f"Contains {description}")
        
        # Check for credible patterns (likely true)
        credible_patterns = {
            r'\b(?:according to|study by|research from)\s+(?:the\s+)?[A-Z][a-z]+': ('attributed source', 15),
            r'\b(?:peer-reviewed|published in|journal of)\b': ('academic source', 20),
            r'\b(?:fda|cdc|who|nih)\b': ('official health authority', 25),
            r'\b\d{4}\s+study\b': ('dated research', 10)
        }
        
        for pattern, (description, modifier) in credible_patterns.items():
            if re.search(pattern, claim_lower):
                confidence_modifiers.append(modifier)
                evidence_points.append(f"References {description}")
        
        # Apply confidence modifiers
        final_confidence = result['confidence'] + sum(confidence_modifiers)
        result['confidence'] = max(0, min(100, final_confidence))
        result['evidence'] = evidence_points
        
        # Determine verdict based on confidence
        if result['confidence'] >= 70:
            result['verdict'] = 'likely_true'
            result['explanation'] = 'Pattern analysis suggests this claim is likely accurate'
        elif result['confidence'] >= 40:
            result['verdict'] = 'mixed'
            result['explanation'] = 'Pattern analysis shows mixed reliability indicators'
        elif result['confidence'] <= 20:
            result['verdict'] = 'likely_false'
            result['explanation'] = 'Pattern analysis suggests this claim may be inaccurate'
        
        return result
    
    def _determine_consensus_verdict(self, verdicts: List[str]) -> str:
        """Determine consensus verdict from multiple fact checks"""
        if not verdicts:
            return 'unverified'
        
        # Normalize verdicts
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
        
        # Count verdicts
        verdict_counts = {}
        for verdict in normalized:
            verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
        
        # Return most common verdict
        if verdict_counts:
            return max(verdict_counts.items(), key=lambda x: x[1])[0]
        
        return 'unverified'
    
    def _calculate_api_confidence(self, verdicts: List[str], publishers: List[str]) -> int:
        """Calculate confidence based on API results"""
        base_confidence = 60
        
        # Boost for multiple consistent verdicts
        if len(verdicts) > 1:
            base_confidence += min(20, len(verdicts) * 5)
        
        # Boost for reputable publishers
        reputable_publishers = ['snopes', 'politifact', 'factcheck.org', 'reuters', 'ap news']
        for publisher in publishers:
            if any(rep in publisher.lower() for rep in reputable_publishers):
                base_confidence += 10
                break
        
        return min(95, base_confidence)
    
    def _calculate_verification_score(self, fact_checks: List[Dict[str, Any]]) -> int:
        """Calculate overall verification score"""
        if not fact_checks:
            return 0
        
        total_confidence = 0
        verdict_scores = {'true': 100, 'likely_true': 80, 'mixed': 50, 'likely_false': 20, 'false': 0, 'unverified': 30}
        
        for check in fact_checks:
            confidence = check.get('confidence', 0)
            verdict = check.get('verdict', 'unverified')
            verdict_score = verdict_scores.get(verdict, 30)
            
            # Weight by confidence
            weighted_score = (verdict_score * confidence) / 100
            total_confidence += weighted_score
        
        return int(total_confidence / len(fact_checks))
    
    def _generate_fact_check_summary(self, fact_checks: List[Dict[str, Any]], 
                                   verification_score: int) -> str:
        """Generate summary of fact checking results"""
        if not fact_checks:
            return "No fact-checkable claims were identified in this article."
        
        summary = f"Analyzed {len(fact_checks)} claims. "
        
        # Count verdicts
        verdicts = [check.get('verdict', 'unverified') for check in fact_checks]
        verdict_counts = {}
        for verdict in verdicts:
            verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
        
        # Report verdict distribution
        if verdict_counts.get('true', 0) + verdict_counts.get('likely_true', 0) > len(fact_checks) / 2:
            summary += "Most claims appear to be accurate. "
        elif verdict_counts.get('false', 0) + verdict_counts.get('likely_false', 0) > len(fact_checks) / 2:
            summary += "Several claims appear to be inaccurate. "
        else:
            summary += "Mixed accuracy in claims. "
        
        # Overall assessment
        if verification_score >= 80:
            summary += "Most claims are well-supported by evidence."
        elif verification_score >= 60:
            summary += "Mixed accuracy with some questionable claims."
        elif verification_score >= 40:
            summary += "Several claims lack support or are disputed."
        else:
            summary += "Many claims appear to be false or misleading."
        
        return summary
    
    def _generate_findings(self, fact_checks: List[Dict[str, Any]], score: int) -> List[Dict[str, Any]]:
        """Generate findings for UI display"""
        findings = []
        
        if score >= 80:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': f'High verification score ({score}/100)',
                'explanation': 'Most claims are well-supported by evidence'
            })
        elif score >= 60:
            findings.append({
                'type': 'info',
                'severity': 'medium',
                'text': f'Moderate verification ({score}/100)',
                'explanation': 'Mixed accuracy with some questionable claims'
            })
        else:
            findings.append({
                'type': 'warning',
                'severity': 'high',
                'text': f'Low verification score ({score}/100)',
                'explanation': 'Many claims lack verification or are disputed'
            })
        
        # Add specific fact check findings
        verified_count = len([fc for fc in fact_checks if fc.get('verdict') in ['true', 'likely_true']])
        disputed_count = len([fc for fc in fact_checks if fc.get('verdict') in ['false', 'likely_false']])
        
        if verified_count > 0:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': f'{verified_count} claims verified as accurate',
                'explanation': 'These claims are supported by fact-checking sources'
            })
        
        if disputed_count > 0:
            findings.append({
                'type': 'warning',
                'severity': 'high',
                'text': f'{disputed_count} claims disputed or false',
                'explanation': 'These claims are contradicted by fact-checking sources'
            })
        
        return findings
    
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
                r'\b\d+\s+(?:times|fold) (?:more|less|higher|lower)\b',
                r'\b(?:majority|minority|most|few|many) of\b',
                r'\b\d+\s+(?:out of|in) \d+\b'
            ]
        }
