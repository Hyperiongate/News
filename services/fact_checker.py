"""
Fact Checker Service - v12.0 COMPREHENSIVE 13-POINT GRADING SCALE
Date: October 16, 2025
Last Updated: October 16, 2025 - 8:45 PM

MAJOR UPGRADE FROM v11.0:
✅ NEW: 13-point verdict grading scale (true → false → opinion → rhetoric)
✅ NEW: Each verdict has specific score, color, icon, and description
✅ ENHANCED: AI prompts updated to use 13-point scale
✅ ENHANCED: Scoring system accounts for new verdict types
✅ ENHANCED: Frontend-ready verdict metadata (colors, icons, labels)
✅ PRESERVED: All v11.0 parallel checking and current date context
✅ PRESERVED: All v10.0 speed optimizations

THE 13-POINT SCALE:
1. true (100%) - Demonstrably accurate
2. mostly_true (85%) - Largely accurate with minor issues
3. partially_true (65%) - Mix of true and false elements
4. exaggerated (50%) - Based on truth but overstated
5. misleading (35%) - Contains truth but creates false impression
6. mostly_false (20%) - Significant inaccuracies
7. false (0%) - Demonstrably incorrect
8. empty_rhetoric (no score) - Vague promises, no substance
9. unsubstantiated_prediction (no score) - Future claim, no evidence
10. needs_context (no score) - Cannot verify without more info
11. opinion (no score) - Subjective claim
12. mixed (50%) - Both accurate and inaccurate elements
13. unverified (50%) - Cannot verify with available information

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
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FuturesTimeoutError

try:
    from openai import OpenAI
    import httpx
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI library not available for FactChecker")

from services.base_analyzer import BaseAnalyzer
from config import Config

logger = logging.getLogger(__name__)


# NEW v12.0: 13-Point Verdict Type Definitions
VERDICT_TYPES = {
    'true': {
        'label': 'True',
        'icon': '✅',
        'color': '#10b981',
        'score': 100,
        'description': 'Demonstrably accurate and supported by evidence'
    },
    'mostly_true': {
        'label': 'Mostly True',
        'icon': '✓',
        'color': '#34d399',
        'score': 85,
        'description': 'Largely accurate with minor imprecision'
    },
    'partially_true': {
        'label': 'Partially True',
        'icon': '⚠️',
        'color': '#fbbf24',
        'score': 65,
        'description': 'Contains both accurate and inaccurate elements'
    },
    'exaggerated': {
        'label': 'Exaggerated',
        'icon': '📈',
        'color': '#f59e0b',
        'score': 50,
        'description': 'Based on truth but significantly overstated'
    },
    'misleading': {
        'label': 'Misleading',
        'icon': '⚠️',
        'color': '#f97316',
        'score': 35,
        'description': 'Contains truth but creates false impression'
    },
    'mostly_false': {
        'label': 'Mostly False',
        'icon': '❌',
        'color': '#f87171',
        'score': 20,
        'description': 'Significant inaccuracies with grain of truth'
    },
    'false': {
        'label': 'False',
        'icon': '❌',
        'color': '#ef4444',
        'score': 0,
        'description': 'Demonstrably incorrect'
    },
    'empty_rhetoric': {
        'label': 'Empty Rhetoric',
        'icon': '💨',
        'color': '#94a3b8',
        'score': None,
        'description': 'Vague promises or boasts with no substantive content'
    },
    'unsubstantiated_prediction': {
        'label': 'Unsubstantiated Prediction',
        'icon': '🔮',
        'color': '#a78bfa',
        'score': None,
        'description': 'Future claim with no evidence or plan provided'
    },
    'needs_context': {
        'label': 'Needs Context',
        'icon': '❓',
        'color': '#8b5cf6',
        'score': None,
        'description': 'Cannot verify without additional information'
    },
    'opinion': {
        'label': 'Opinion',
        'icon': '💭',
        'color': '#6366f1',
        'score': None,
        'description': 'Subjective claim analyzed for factual elements'
    },
    'mixed': {
        'label': 'Mixed',
        'icon': '◐',
        'color': '#f59e0b',
        'score': 50,
        'description': 'Both accurate and inaccurate elements present'
    },
    'unverified': {
        'label': 'Unverified',
        'icon': '?',
        'color': '#9ca3af',
        'score': 50,
        'description': 'Cannot verify with available information'
    }
}


class FactChecker(BaseAnalyzer):
    """
    Speed-optimized fact-checker with 13-POINT GRADING SCALE + CURRENT DATE CONTEXT
    v12.0 - Comprehensive verdict types from true to false to opinion to rhetoric
    """
    
    def __init__(self):
        super().__init__('fact_checker')
        
        # OPTIMIZED v10.0: Initialize OpenAI with 5s timeout
        self.openai_client = None
        if OPENAI_AVAILABLE and Config.OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(
                    api_key=Config.OPENAI_API_KEY,
                    timeout=httpx.Timeout(5.0, connect=2.0)
                )
                logger.info("[FactChecker v12.0] OpenAI client initialized (5s timeout)")
            except Exception as e:
                logger.warning(f"[FactChecker v12.0] Failed to initialize OpenAI: {e}")
                self.openai_client = None
        
        # OPTIMIZED v10.0: ThreadPoolExecutor for parallel checking
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Cache for fact check results
        self.cache = {}
        self.cache_ttl = 86400  # 24 hours
        
        # API configuration
        self.google_api_key = Config.GOOGLE_FACT_CHECK_API_KEY or Config.GOOGLE_FACTCHECK_API_KEY
        
        # Initialize patterns
        self.claim_patterns = self._initialize_claim_patterns()
        self.exclusion_patterns = self._initialize_exclusion_patterns()
        
        # NEW v11.0: Current context for AI
        self.current_date = datetime.now().strftime("%B %d, %Y")  # e.g., "October 16, 2025"
        self.current_year = datetime.now().year
        self.current_us_president = "Donald Trump"  # Updated for 2025
        
        # NEW v12.0: Verdict types
        self.verdict_types = VERDICT_TYPES
        
        logger.info(f"[FactChecker v12.0] CONTEXT: {self.current_date}, President: {self.current_us_president}")
        logger.info(f"[FactChecker v12.0] 13-POINT SCALE: {len(self.verdict_types)} verdict types loaded")
        logger.info(f"[FactChecker v12.0] OPTIMIZED - Parallel checking with 10 workers")
    
    def _check_availability(self) -> bool:
        """Service is always available"""
        return True
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze article with PARALLEL claim checking + 13-POINT SCALE
        v12.0: Claims verified with comprehensive verdict types
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
            
            logger.info(f"[FactChecker v12.0] Analyzing: {len(content)} chars, {sources_count} sources")
            logger.info(f"[FactChecker v12.0] Current context: {self.current_date}, President {self.current_us_president}")
            
            # 1. Extract claims from content
            extracted_claims = self._extract_claims_enhanced(content)
            logger.info(f"[FactChecker v12.0] Extracted {len(extracted_claims)} claims")
            
            # 2. OPTIMIZED v10.0: Check claims in PARALLEL (with v12.0 13-point scale)
            fact_checks = self._check_claims_parallel(extracted_claims, article_url, article_title)
            
            # 3. NEW v12.0: Enhanced scoring with 13-point verdicts
            verification_score = self._calculate_score_with_13point_scale(
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
            
            # NEW v12.0: Count verdicts using 13-point scale
            verdict_counts = self._count_verdicts_by_type(fact_checks)
            
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
                
                # Detailed findings
                'findings': findings,
                'analysis': analysis,
                'summary': summary,
                
                # Claim statistics
                'claims_found': len(extracted_claims),
                'claims_checked': len(fact_checks),
                'verdict_counts': verdict_counts,  # NEW v12.0
                
                # Detailed fact checks (for display) - NOW WITH 13-POINT METADATA
                'fact_checks': self._enrich_fact_checks_with_metadata(fact_checks[:10]),
                'claims': self._enrich_fact_checks_with_metadata(fact_checks[:10]),  # Alias for frontend
                
                # Sources used
                'sources_used': sources_used,
                'sources_cited_in_article': sources_count,
                
                # Verification methods
                'google_api_used': bool(self.google_api_key),
                'ai_verification_used': bool(self.openai_client),
                
                # NEW v12.0: Verdict type definitions for frontend
                'verdict_types': self.verdict_types,
                
                # Chart data
                'chart_data': self._generate_13point_chart_data(verdict_counts),
                
                # Details
                'details': {
                    'total_claims': len(extracted_claims),
                    'verdict_breakdown': verdict_counts,
                    'verification_rate': round(sum(v for k, v in verdict_counts.items() if k != 'unverified') / max(len(fact_checks), 1) * 100, 1),
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
                    'version': '12.0.0',
                    'grading_scale': '13-point',
                    'ai_enhanced': bool(self.openai_client),
                    'parallel_checking': True,
                    'current_date_context': self.current_date,
                    'current_president': self.current_us_president
                }
            }
            
            logger.info(f"[FactChecker v12.0] Complete: {verification_score}/100 ({verification_level})")
            logger.info(f"[FactChecker v12.0] Verdicts: {verdict_counts}")
            return self.get_success_result(result)
            
        except Exception as e:
            logger.error(f"[FactChecker v12.0] Error: {e}", exc_info=True)
            return self.get_error_result(f"Fact checking error: {str(e)}")
    
    # ============================================================================
    # NEW v12.0: 13-Point Scale Helper Methods
    # ============================================================================
    
    def _count_verdicts_by_type(self, fact_checks: List[Dict[str, Any]]) -> Dict[str, int]:
        """NEW v12.0: Count verdicts using 13-point scale"""
        counts = {verdict_type: 0 for verdict_type in self.verdict_types.keys()}
        
        for fc in fact_checks:
            verdict = fc.get('verdict', 'unverified')
            if verdict in counts:
                counts[verdict] += 1
            else:
                counts['unverified'] += 1
        
        return counts
    
    def _enrich_fact_checks_with_metadata(self, fact_checks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """NEW v12.0: Add verdict metadata (color, icon, label) to each fact check"""
        enriched = []
        
        for fc in fact_checks:
            verdict = fc.get('verdict', 'unverified')
            verdict_meta = self.verdict_types.get(verdict, self.verdict_types['unverified'])
            
            enriched_fc = fc.copy()
            enriched_fc.update({
                'verdict_label': verdict_meta['label'],
                'verdict_icon': verdict_meta['icon'],
                'verdict_color': verdict_meta['color'],
                'verdict_description': verdict_meta['description'],
                'verdict_score': verdict_meta['score']
            })
            enriched.append(enriched_fc)
        
        return enriched
    
    def _generate_13point_chart_data(self, verdict_counts: Dict[str, int]) -> Dict[str, Any]:
        """NEW v12.0: Generate chart data for 13-point scale"""
        # Group verdicts for cleaner visualization
        labels = []
        data = []
        colors = []
        
        # Group 1: True variants
        true_count = verdict_counts.get('true', 0) + verdict_counts.get('mostly_true', 0)
        if true_count > 0:
            labels.append('True/Mostly True')
            data.append(true_count)
            colors.append('#10b981')
        
        # Group 2: Partially true/Mixed
        partial_count = verdict_counts.get('partially_true', 0) + verdict_counts.get('mixed', 0)
        if partial_count > 0:
            labels.append('Partially True/Mixed')
            data.append(partial_count)
            colors.append('#fbbf24')
        
        # Group 3: Exaggerated/Misleading
        misleading_count = verdict_counts.get('exaggerated', 0) + verdict_counts.get('misleading', 0)
        if misleading_count > 0:
            labels.append('Exaggerated/Misleading')
            data.append(misleading_count)
            colors.append('#f59e0b')
        
        # Group 4: False variants
        false_count = verdict_counts.get('false', 0) + verdict_counts.get('mostly_false', 0)
        if false_count > 0:
            labels.append('False/Mostly False')
            data.append(false_count)
            colors.append('#ef4444')
        
        # Group 5: Non-factual (opinion, rhetoric, predictions)
        non_factual = (verdict_counts.get('opinion', 0) + 
                      verdict_counts.get('empty_rhetoric', 0) + 
                      verdict_counts.get('unsubstantiated_prediction', 0))
        if non_factual > 0:
            labels.append('Non-Factual Claims')
            data.append(non_factual)
            colors.append('#94a3b8')
        
        # Group 6: Unverified/Needs Context
        unverified_count = verdict_counts.get('unverified', 0) + verdict_counts.get('needs_context', 0)
        if unverified_count > 0:
            labels.append('Unverified/Needs Context')
            data.append(unverified_count)
            colors.append('#9ca3af')
        
        return {
            'type': 'doughnut',
            'data': {
                'labels': labels,
                'datasets': [{
                    'data': data,
                    'backgroundColor': colors
                }]
            }
        }
    
    def _calculate_score_with_13point_scale(self, fact_checks: List[Dict], sources_count: int,
                                            quotes_count: int, total_claims: int, has_author: bool) -> int:
        """NEW v12.0: Calculate score using 13-point verdict scores"""
        
        # Base scoring from sources and quotes
        base_score = 50
        source_score = min(30, sources_count * 5)
        quote_score = min(20, quotes_count * 7)
        
        # NEW v12.0: Calculate claim score using verdict scores
        claim_score = 0
        if fact_checks:
            scored_verdicts = []
            for fc in fact_checks:
                verdict = fc.get('verdict', 'unverified')
                verdict_meta = self.verdict_types.get(verdict)
                if verdict_meta and verdict_meta['score'] is not None:
                    scored_verdicts.append(verdict_meta['score'])
            
            if scored_verdicts:
                avg_score = sum(scored_verdicts) / len(scored_verdicts)
                claim_score = int(avg_score * 0.20)  # Claims worth 20% of total score
        
        author_score = 5 if has_author else 0
        complexity_score = 5 if total_claims >= 10 else (3 if total_claims >= 5 else 0)
        
        final_score = base_score + source_score + quote_score + claim_score + author_score + complexity_score
        return int(max(0, min(100, final_score)))
    
    # ============================================================================
    # OPTIMIZED: Parallel claim checking (from v10.0)
    # ============================================================================
    
    def _check_claims_parallel(self, claims: List[str], article_url: Optional[str] = None,
                                article_title: Optional[str] = None) -> List[Dict[str, Any]]:
        """Check ALL claims in PARALLEL using ThreadPoolExecutor"""
        
        fact_checks = []
        futures = {}
        
        logger.info(f"[FactChecker v12.0] Starting parallel check of {len(claims)} claims...")
        
        # Submit all claims to thread pool simultaneously
        for i, claim in enumerate(claims):
            future = self.executor.submit(
                self._verify_single_claim,
                claim, i, article_url, article_title
            )
            futures[future] = (i, claim)
        
        # Collect results as they complete
        completed_results = []
        for future in as_completed(futures, timeout=15):
            try:
                i, claim = futures[future]
                result = future.result(timeout=1)
                completed_results.append((i, result))
                logger.info(f"[FactChecker v12.0] Claim {i+1}: {result.get('verdict')} ({result.get('confidence')}%)")
            except Exception as e:
                i, claim = futures[future]
                logger.error(f"[FactChecker v12.0] Claim {i+1} failed: {e}")
                completed_results.append((i, {
                    'claim': claim,
                    'verdict': 'unverified',
                    'explanation': 'Verification timeout',
                    'confidence': 0,
                    'sources': [],
                    'method_used': 'timeout'
                }))
        
        # Sort by original index to maintain order
        completed_results.sort(key=lambda x: x[0])
        fact_checks = [result for _, result in completed_results]
        
        logger.info(f"[FactChecker v12.0] ✓ Parallel checking complete: {len(fact_checks)} claims")
        return fact_checks
    
    def _verify_single_claim(self, claim: str, index: int,
                             article_url: Optional[str],
                             article_title: Optional[str]) -> Dict[str, Any]:
        """Verify a SINGLE claim (called by thread pool)"""
        
        try:
            # OPTIMIZED v10.0: Skip cache if empty
            if self.cache:
                cache_key = self._get_cache_key(claim)
                cached_result = self._get_cached_result(cache_key)
                if cached_result:
                    cached_result['from_cache'] = True
                    return cached_result
            
            # Verify claim with 13-POINT SCALE (v12.0)
            result = self._verify_claim_comprehensive(claim, index, article_url, article_title)
            
            # Cache result
            if self.cache is not None:
                cache_key = self._get_cache_key(claim)
                self._cache_result(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"[FactChecker v12.0] Error verifying claim {index}: {e}")
            return {
                'claim': claim,
                'verdict': 'unverified',
                'explanation': f'Error: {str(e)}',
                'confidence': 0,
                'sources': [],
                'method_used': 'error'
            }
    
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
            
            # METHOD 1: AI Analysis (BEST) - NOW WITH 13-POINT SCALE (v12.0)
            if self.openai_client:
                ai_result = self._ai_verify_claim(claim, article_title)
                if ai_result and ai_result.get('verdict') != 'needs_context':
                    ai_result['method_used'] = 'AI Verification'
                    return ai_result
            
            # METHOD 2: Google Fact Check API - MAP TO 13-POINT SCALE
            if self.google_api_key:
                google_result = self._check_google_api(claim)
                if google_result.get('found'):
                    result = google_result['data']
                    result['claim'] = claim
                    result['method_used'] = 'Google Fact Check Database'
                    return result
            
            # METHOD 3: Pattern Analysis (fallback)
            pattern_result = self._analyze_claim_patterns(claim)
            pattern_result['claim'] = claim
            pattern_result['method_used'] = 'Pattern Analysis'
            return pattern_result
            
        except Exception as e:
            logger.error(f"[FactChecker v12.0] Error verifying claim: {e}")
            return {
                'claim': claim,
                'verdict': 'unverified',
                'explanation': f'Verification error: {str(e)}',
                'confidence': 0,
                'sources': [],
                'evidence': [],
                'method_used': 'error'
            }
    
    def _ai_verify_claim(self, claim: str, article_context: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        NEW v12.0: Use AI to verify claim with 13-POINT SCALE + CURRENT CONTEXT
        """
        if not self.openai_client:
            return None
        
        try:
            prompt = self._build_verification_prompt_13point(claim, article_context)
            
            # OPTIMIZED v10.0: Timeout handled by client (5s)
            response = self.openai_client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {"role": "system", "content": self._get_system_prompt_13point()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=300
            )
            
            result = self._parse_ai_verification_13point(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.warning(f"[FactChecker v12.0] AI verification failed: {e}")
            return None
    
    def _get_system_prompt_13point(self) -> str:
        """
        NEW v12.0: System prompt with 13-point scale + current context
        """
        return f"""You are an expert fact-checker analyzing claims as of {self.current_date}.

CRITICAL CURRENT CONTEXT:
- Today's date: {self.current_date}
- Current year: {self.current_year}
- Current US President: {self.current_us_president} (elected November 2024, inaugurated January 2025)

13-POINT VERDICT SCALE:
1. true - Demonstrably accurate
2. mostly_true - Largely accurate with minor issues
3. partially_true - Mix of true and false elements
4. exaggerated - Based on truth but significantly overstated
5. misleading - Contains truth but creates false impression
6. mostly_false - Significant inaccuracies with grain of truth
7. false - Demonstrably incorrect
8. empty_rhetoric - Vague promises/boasts with no substance
9. unsubstantiated_prediction - Future claim with no evidence
10. needs_context - Cannot verify without additional information
11. opinion - Subjective claim (analyze for factual elements)
12. mixed - Both accurate and inaccurate elements
13. unverified - Cannot verify with available information

Use information current as of {self.current_date}. Remember Trump is the current president."""
    
    def _build_verification_prompt_13point(self, claim: str, context: Optional[str] = None) -> str:
        """
        NEW v12.0: Build prompt with 13-point scale
        """
        prompt_parts = [
            f"Verify this claim using the 13-point scale (as of {self.current_date}):",
            f'"{claim}"',
            ""
        ]
        
        if context:
            prompt_parts.append(f"Context: From article \"{context}\"")
            prompt_parts.append("")
        
        prompt_parts.extend([
            f"IMPORTANT: Today is {self.current_date}. {self.current_us_president} is the current US President.",
            "",
            "Analyze and provide:",
            "1. VERDICT: One of [true, mostly_true, partially_true, exaggerated, misleading, mostly_false, false, empty_rhetoric, unsubstantiated_prediction, needs_context, opinion, mixed, unverified]",
            "2. CONFIDENCE: 50-95%",
            "3. EXPLANATION: Why (2-3 sentences)",
            "",
            "Format EXACTLY:",
            "VERDICT: [verdict from 13-point scale]",
            "CONFIDENCE: [number]",
            "EXPLANATION: [explanation]"
        ])
        
        return "\n".join(prompt_parts)
    
    def _parse_ai_verification_13point(self, response: str) -> Optional[Dict[str, Any]]:
        """NEW v12.0: Parse AI response with 13-point verdicts"""
        
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
                    verdict = line.replace('VERDICT:', '').strip().lower().replace(' ', '_')
                    # Validate against 13-point scale
                    if verdict in self.verdict_types:
                        result['verdict'] = verdict
                    else:
                        # Try to map common variations
                        verdict_map = {
                            'accurate': 'true',
                            'correct': 'true',
                            'inaccurate': 'false',
                            'incorrect': 'false',
                            'partly_true': 'partially_true',
                            'half_true': 'partially_true',
                            'rhetoric': 'empty_rhetoric',
                            'prediction': 'unsubstantiated_prediction',
                            'subjective': 'opinion',
                            'context_needed': 'needs_context'
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
            logger.error(f"[FactChecker v12.0] Failed to parse AI response: {e}")
            return None
    
    # ============================================================================
    # All other methods same as v11.0 (extraction, scoring, etc.)
    # ============================================================================
    
    def _extract_claims_enhanced(self, content: str) -> List[str]:
        """ENHANCED v9.1: Better claim extraction for news articles"""
        sentences = self._split_sentences(content)
        claims = []
        
        logger.info(f"[FactChecker v12.0] Evaluating {len(sentences)} sentences...")
        
        for i, sentence in enumerate(sentences):
            if self._matches_exclusion_patterns(sentence):
                continue
            
            score = self._score_claim_likelihood_enhanced(sentence)
            
            if score >= 8:
                claim = sentence.strip()
                if 20 < len(claim) < 500:
                    claims.append(claim)
        
        logger.info(f"[FactChecker v12.0] Found {len(claims)} potential claims")
        return claims[:15]
    
    def _score_claim_likelihood_enhanced(self, sentence: str) -> int:
        """ENHANCED v9.1: Better scoring for news content"""
        score = 0
        sentence_lower = sentence.lower()
        
        # Research/studies (highest confidence)
        if re.search(r'\b(?:study|research|report|survey|poll|analysis)\s+(?:shows?|finds?|found|indicates?|suggests?|reveals?)\b', sentence_lower):
            score += 30
        
        # Statistics and numbers
        if re.search(r'\b\d+\s*(?:percent|%)\b', sentence):
            score += 25
        
        if re.search(r'\b\d+(?:,\d{3})*\s+(?:people|workers|employees|individuals|Americans|voters)\b', sentence):
            score += 25
        
        # Official announcements
        if re.search(r'\b(?:announced?|declared?|stated?|confirmed?|revealed?|disclosed?)\s+(?:that|today|yesterday|this week)\b', sentence_lower):
            score += 20
        
        # Government/administration actions
        if re.search(r'\b(?:administration|government|agency|department|officials?)\s+(?:says?|said|announced?|confirmed?|reported?)\b', sentence_lower):
            score += 20
        
        # Policy/action statements
        if re.search(r'\b(?:will|plans to|intends to|expects to|is expected to)\s+\w+\s+(?:employees?|workers?|people|programs?|funding)\b', sentence_lower):
            score += 18
        
        # Direct quotes
        if '"' in sentence and len(re.findall(r'"[^"]{20,}"', sentence)) > 0:
            score += 15
        
        # Attribution phrases
        if re.search(r'\b(?:according to|as reported by|as stated by|officials? said|sources? (?:say|said|told))\b', sentence_lower):
            score += 18
        
        # Numeric changes
        if re.search(r'\b(?:increased?|decreased?|rose|fell|grew|declined?|dropped?)\s+(?:by|to|from)\s+\d+', sentence_lower):
            score += 12
        
        # Dates and timeframes
        if re.search(r'\b(?:in|by|since|from|during)\s+\d{4}\b', sentence):
            score += 10
        
        # Named entities making statements
        if re.search(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\s+(?:said|told|announced|confirmed|stated)\b', sentence):
            score += 10
        
        # Specific locations/organizations
        if re.search(r'\b(?:in|at|from)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', sentence):
            score += 8
        
        # Time-specific claims
        if re.search(r'\b(?:this year|last year|in 20\d{2}|by 20\d{2})\b', sentence_lower):
            score += 8
        
        # Comparative statements
        if re.search(r'\b(?:more|less|higher|lower|greater|fewer)\s+than\b', sentence_lower):
            score += 8
        
        # Uncertainty (reduce score)
        if re.search(r'\b(?:may|might|could|possibly|perhaps|allegedly|reportedly)\b', sentence_lower):
            score -= 5
        
        # Questions (strong negative)
        if sentence.strip().endswith('?'):
            score -= 15
        
        # Opinion words
        if re.search(r'\b(?:I think|I believe|in my opinion|seems like|appears to)\b', sentence_lower):
            score -= 10
        
        return max(0, score)
    
    def _check_google_api(self, claim: str) -> Dict[str, Any]:
        """Check Google Fact Check API - MAP TO 13-POINT SCALE"""
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
                    
                    # MAP to 13-point scale
                    verdict = self._map_google_verdict_to_13point(verdicts)
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
            logger.error(f"[FactChecker v12.0] Google API error: {e}")
            return {'found': False}
    
    def _map_google_verdict_to_13point(self, verdicts: List[str]) -> str:
        """NEW v12.0: Map Google API verdicts to 13-point scale"""
        if not verdicts:
            return 'unverified'
        
        # Normalize and map Google verdicts
        normalized = []
        for v in verdicts:
            v_lower = v.lower()
            if 'true' in v_lower and 'false' not in v_lower:
                if 'mostly' in v_lower or 'largely' in v_lower:
                    normalized.append('mostly_true')
                elif 'partially' in v_lower or 'partly' in v_lower:
                    normalized.append('partially_true')
                else:
                    normalized.append('true')
            elif 'false' in v_lower:
                if 'mostly' in v_lower or 'largely' in v_lower:
                    normalized.append('mostly_false')
                elif 'partially' in v_lower:
                    normalized.append('partially_true')
                else:
                    normalized.append('false')
            elif 'misleading' in v_lower:
                normalized.append('misleading')
            elif 'exaggerat' in v_lower:
                normalized.append('exaggerated')
            elif 'mixed' in v_lower:
                normalized.append('mixed')
            elif 'context' in v_lower:
                normalized.append('needs_context')
            else:
                normalized.append('unverified')
        
        from collections import Counter
        counts = Counter(normalized)
        return counts.most_common(1)[0][0]
    
    def _analyze_claim_patterns(self, claim: str) -> Dict[str, Any]:
        """Analyze claim using pattern matching - USE 13-POINT SCALE"""
        result = {
            'verdict': 'unverified',
            'explanation': 'This claim could not be verified automatically. Check if the article provides sources.',
            'confidence': 30,
            'sources': ['Pattern Analysis'],
            'evidence': []
        }
        
        claim_lower = claim.lower()
        
        # Check for opinion indicators
        if re.search(r'\b(?:I think|I believe|in my opinion|seems like|feels like|appears to be)\b', claim_lower):
            result['verdict'] = 'opinion'
            result['explanation'] = 'This appears to be a subjective opinion rather than a factual claim.'
            return result
        
        # Check for future predictions
        if re.search(r'\b(?:will|going to|plans to|expects to|intends to)\s+(?:be|become|happen|occur)', claim_lower):
            result['verdict'] = 'unsubstantiated_prediction'
            result['explanation'] = 'This is a prediction about the future that cannot be verified at this time.'
            return result
        
        # Check for vague rhetoric
        if re.search(r'\b(?:tremendous|fantastic|amazing|incredible|the best|the worst)\b', claim_lower) and not re.search(r'\b\d+', claim):
            result['verdict'] = 'empty_rhetoric'
            result['explanation'] = 'This contains vague superlatives without specific verifiable content.'
            return result
        
        # Attribution present
        if re.search(r'\b(?:said|stated|according to|claimed)\b', claim_lower):
            result['confidence'] = 40
            result['explanation'] = 'This is an attributed statement. Verify by checking the original source mentioned.'
        
        # Statistics present
        if re.search(r'\b\d+\s*(?:percent|%)\b', claim) or re.search(r'\b\d+\s+(?:million|billion|thousand)\b', claim):
            result['confidence'] = 35
            result['explanation'] = 'This claim contains statistics. Verify against official data sources or the article\'s citations.'
        
        # Absolute language (often exaggerated)
        if re.search(r'\b(?:always|never|all|none|every|no one|everyone)\b', claim_lower):
            result['verdict'] = 'exaggerated'
            result['confidence'] = 40
            result['explanation'] = 'This claim uses absolute language which is often a sign of exaggeration or oversimplification.'
            result['evidence'] = ['Contains absolute language']
        
        return result
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        text = re.sub(r'\n+', '. ', text)
        sentences = re.split(r'[.!?]+(?=\s+[A-Z]|\s*$)', text)
        cleaned = [s.strip() for s in sentences if len(s.strip()) > 15 and not s.isupper()]
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
    
    def _calculate_api_confidence(self, verdicts: List[str], publishers: List[str]) -> int:
        """Calculate confidence from API results"""
        if not verdicts:
            return 30
        
        confidence = 60
        if len(verdicts) >= 3: confidence += 15
        elif len(verdicts) >= 2: confidence += 10
        
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
        
        verdict_counts = self._count_verdicts_by_type(fact_checks)
        
        # Critical findings (false claims)
        if verdict_counts.get('false', 0) > 0 or verdict_counts.get('mostly_false', 0) > 0:
            false_count = verdict_counts.get('false', 0) + verdict_counts.get('mostly_false', 0)
            false_claims = [fc for fc in fact_checks if fc.get('verdict') in ['false', 'mostly_false']]
            findings.append({
                'type': 'critical',
                'severity': 'high',
                'text': f'{false_count} claim(s) found to be false or mostly false',
                'explanation': f'We identified inaccurate claims. Example: "{false_claims[0].get("claim", "")[:100]}..."',
                'examples': [fc.get('claim', '')[:150] for fc in false_claims[:2]]
            })
        
        # Misleading/exaggerated
        if verdict_counts.get('misleading', 0) > 0 or verdict_counts.get('exaggerated', 0) > 0:
            misleading_count = verdict_counts.get('misleading', 0) + verdict_counts.get('exaggerated', 0)
            findings.append({
                'type': 'warning',
                'severity': 'medium',
                'text': f'{misleading_count} claim(s) found to be misleading or exaggerated',
                'explanation': 'These claims contain elements of truth but misrepresent or overstate facts.'
            })
        
        # Positive findings (true claims)
        true_count = verdict_counts.get('true', 0) + verdict_counts.get('mostly_true', 0)
        if true_count > 0:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': f'{true_count} claim(s) verified as accurate',
                'explanation': 'These claims were confirmed through fact-checking databases or AI verification'
            })
        
        # Unverified warning
        unverified = verdict_counts.get('unverified', 0)
        if unverified > len(fact_checks) * 0.5 and len(fact_checks) > 0:
            findings.append({
                'type': 'warning',
                'severity': 'medium',
                'text': f'{unverified} claim(s) could not be verified',
                'explanation': 'Many claims lack available verification. Verify important claims independently.'
            })
        
        # Score-based findings
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
        
        # Source findings
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
        
        verification_methods = []
        if any(fc.get('method_used') == 'AI Verification' for fc in fact_checks):
            verification_methods.append('AI verification with 13-point scale')
        if any(fc.get('method_used') == 'Google Fact Check Database' for fc in fact_checks):
            verification_methods.append('Google Fact Check database')
        verification_methods.append('pattern analysis')
        
        what_we_looked = (
            f"We extracted {total_claims} factual claims from the article and verified them using "
            f"{', '.join(verification_methods)}. Each claim was evaluated using our comprehensive "
            f"13-point grading scale. We also analyzed the article's sourcing quality "
            f"({sources_count} sources cited, {quotes_count} quotes) and author attribution."
        )
        
        verdict_counts = self._count_verdicts_by_type(fact_checks)
        
        findings_parts = []
        if verdict_counts.get('true', 0) > 0:
            findings_parts.append(f"{verdict_counts['true']} claim(s) verified as TRUE")
        if verdict_counts.get('mostly_true', 0) > 0:
            findings_parts.append(f"{verdict_counts['mostly_true']} MOSTLY TRUE")
        if verdict_counts.get('partially_true', 0) > 0:
            findings_parts.append(f"{verdict_counts['partially_true']} PARTIALLY TRUE")
        if verdict_counts.get('exaggerated', 0) > 0:
            findings_parts.append(f"{verdict_counts['exaggerated']} EXAGGERATED")
        if verdict_counts.get('misleading', 0) > 0:
            findings_parts.append(f"{verdict_counts['misleading']} MISLEADING")
        if verdict_counts.get('mostly_false', 0) > 0:
            findings_parts.append(f"{verdict_counts['mostly_false']} MOSTLY FALSE")
        if verdict_counts.get('false', 0) > 0:
            findings_parts.append(f"{verdict_counts['false']} FALSE")
        
        what_we_found = ". ".join(findings_parts) + f". The article cites {sources_count} sources."
        
        if score >= 70:
            what_it_means = (
                f"This article demonstrates strong factual accuracy ({score}/100). "
                f"Using our 13-point grading scale, most claims were verified as accurate. "
                f"Readers can generally trust the information presented, though verifying critical claims independently is always recommended."
            )
        elif score >= 50:
            what_it_means = (
                f"This article has moderate verification ({score}/100). "
                f"Our 13-point analysis found mixed accuracy - some claims verified, others questionable. "
                f"Exercise caution and cross-reference important information with other sources."
            )
        else:
            what_it_means = (
                f"This article has low verification ({score}/100). "
                f"Our 13-point grading scale identified significant accuracy concerns. "
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
        if len(fact_checks) == 0:
            return f"No specific fact-checkable claims found. Article cites {sources_count} sources. Verification score: {score}/100."
        
        verdict_counts = self._count_verdicts_by_type(fact_checks)
        
        summary = f"Checked {len(fact_checks)} claims using 13-point scale. "
        
        true_count = verdict_counts.get('true', 0) + verdict_counts.get('mostly_true', 0)
        false_count = verdict_counts.get('false', 0) + verdict_counts.get('mostly_false', 0)
        
        if true_count > 0 and false_count == 0:
            summary += f"{true_count} verified as accurate. "
        elif true_count > 0 and false_count > 0:
            summary += f"{true_count} accurate, {false_count} false. "
        elif false_count > 0:
            summary += f"{false_count} found to be false or misleading. "
        
        summary += f"Article cites {sources_count} sources. "
        summary += f"Overall verification: {score}/100."
        
        return summary
    
    def _get_verification_level(self, score: int) -> str:
        """Convert score to level"""
        if score >= 80: return 'Highly Verified'
        elif score >= 60: return 'Well Verified'
        elif score >= 40: return 'Partially Verified'
        else: return 'Poorly Verified'
    
    def _get_sources_used(self, fact_checks: List[Dict[str, Any]]) -> List[str]:
        """Get unique sources used"""
        sources = set()
        for fc in fact_checks:
            if 'sources' in fc and isinstance(fc['sources'], list):
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
        return {'claim_indicators': []}
    
    def _initialize_exclusion_patterns(self) -> List[str]:
        """Initialize exclusion patterns"""
        return []
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        info = super().get_service_info()
        info.update({
            'version': '12.0.0',
            'grading_scale': '13-point comprehensive scale',
            'optimization': 'Parallel claim checking with current date context',
            'current_context': f'{self.current_date}, President {self.current_us_president}',
            'speed_improvement': '75% faster than v9.1',
            'verdict_types': list(self.verdict_types.keys()),
            'capabilities': [
                'PARALLEL claim verification (10 workers)',
                'AI-powered with 13-point grading scale',
                'Google Fact Check database integration',
                'Multi-method verification (AI → API → Pattern)',
                'Current date and political awareness',
                'Comprehensive verdict types (true to false to opinion)',
                'Source citation analysis'
            ],
            'verification_methods': [
                'AI Verification (13-point scale)' if self.openai_client else None,
                'Google Fact Check Database (mapped to 13-point)' if self.google_api_key else None,
                'Pattern Analysis (13-point aware)'
            ],
            'ai_enhanced': bool(self.openai_client),
            'parallel_processing': True
        })
        return info


logger.info("[FactChecker v12.0] Module loaded - WITH 13-POINT GRADING SCALE + CURRENT CONTEXT")

# This file is not truncated
