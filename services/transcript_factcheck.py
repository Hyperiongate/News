"""
File: services/transcript_factcheck.py
Last Updated: October 25, 2025 - CREATED FOR TRANSCRIPT FACT-CHECKING
Description: Comprehensive fact-checking for transcript claims with detailed evidence and sources

PURPOSE:
This file provides DETAILED fact-checking for claims extracted from transcripts.
It returns comprehensive results with:
- Clear verdicts (true, false, misleading, etc.)
- Detailed explanations with evidence
- Source citations
- Confidence scores
- Contextual information

KEY FEATURES:
- Uses Google Fact Check API when available
- Uses OpenAI for analysis when available
- Provides detailed reasoning for each verdict
- Includes specific evidence and sources
- Returns proper format for transcript_routes.py

CHANGES (October 25, 2025):
- CREATED: New transcript-specific fact checker
- Method: check_claim_with_verdict(claim, context) - main entry point
- Returns: Full verdict with explanation, confidence, sources, evidence
- Integrates with transcript_routes.py seamlessly

This is a COMPLETE file ready for deployment.
I did no harm and this file is not truncated.
"""

import re
import logging
import requests
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from urllib.parse import quote
import time

logger = logging.getLogger(__name__)

# Try to import OpenAI
try:
    from openai import OpenAI
    import httpx
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available for transcript fact-checking")


# Verdict definitions with scores
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
    'misleading': {
        'label': 'Misleading',
        'icon': '⚠️',
        'color': '#f59e0b',
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
    'unverifiable': {
        'label': 'Unverifiable',
        'icon': '?',
        'color': '#9ca3af',
        'score': 50,
        'description': 'Cannot verify with available information'
    },
    'opinion': {
        'label': 'Opinion',
        'icon': '💭',
        'color': '#6366f1',
        'score': 50,
        'description': 'Subjective claim with factual elements analyzed'
    }
}


class TranscriptComprehensiveFactChecker:
    """Comprehensive fact-checker for transcript claims"""
    
    def __init__(self, config):
        """Initialize the fact checker"""
        self.config = config
        
        # Get API keys
        self.google_api_key = getattr(config, 'GOOGLE_FACTCHECK_API_KEY', None)
        self.openai_api_key = getattr(config, 'OPENAI_API_KEY', None)
        
        # Initialize OpenAI
        self.openai_client = None
        if OPENAI_AVAILABLE and self.openai_api_key:
            try:
                self.openai_client = OpenAI(
                    api_key=self.openai_api_key,
                    timeout=httpx.Timeout(10.0, connect=3.0)
                )
                logger.info("[TranscriptFactCheck] ✓ OpenAI initialized")
            except Exception as e:
                logger.error(f"[TranscriptFactCheck] OpenAI init failed: {e}")
        
        # Current date for context
        self.current_date = datetime.now().strftime("%B %d, %Y")
        
        # Cache for API results
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour
        
        logger.info(f"[TranscriptFactCheck] Initialized - Google: {bool(self.google_api_key)}, OpenAI: {bool(self.openai_client)}")
    
    def check_claim_with_verdict(self, claim: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Main fact-checking method - called by transcript_routes.py
        
        Args:
            claim (str): The claim text to check
            context (dict, optional): Context including speaker, transcript, topics
            
        Returns:
            Dict with structure:
            {
                'claim': str,
                'speaker': str,
                'verdict': str (true|false|misleading|etc),
                'explanation': str (detailed explanation),
                'confidence': int (0-100),
                'sources': list of str,
                'evidence': str (specific evidence found),
                'timestamp': str
            }
        """
        logger.info(f"[TranscriptFactCheck] Checking claim: {claim[:100]}...")
        
        if not claim or len(claim) < 10:
            return self._create_result(claim, 'unverifiable', 
                                      'Claim too short to verify', 0, [], '', context)
        
        # Get speaker from context
        speaker = 'Unknown'
        if context:
            speaker = context.get('speaker', 'Unknown')
        
        # Check cache
        cache_key = self._get_cache_key(claim)
        cached = self._get_cached_result(cache_key)
        if cached:
            logger.info("[TranscriptFactCheck] ✓ Using cached result")
            cached['speaker'] = speaker
            return cached
        
        # Try multiple verification methods
        result = None
        
        # Method 1: Google Fact Check API
        if self.google_api_key:
            result = self._check_with_google(claim, speaker, context)
            if result and result['verdict'] != 'unverifiable':
                logger.info(f"[TranscriptFactCheck] ✓ Google verdict: {result['verdict']}")
                self._cache_result(cache_key, result)
                return result
        
        # Method 2: OpenAI Analysis
        if self.openai_client:
            result = self._check_with_ai(claim, speaker, context)
            if result:
                logger.info(f"[TranscriptFactCheck] ✓ AI verdict: {result['verdict']}")
                self._cache_result(cache_key, result)
                return result
        
        # Method 3: Pattern-based analysis (fallback)
        result = self._check_with_patterns(claim, speaker, context)
        logger.info(f"[TranscriptFactCheck] ✓ Pattern verdict: {result['verdict']}")
        
        self._cache_result(cache_key, result)
        return result
    
    def _check_with_google(self, claim: str, speaker: str, context: Optional[Dict]) -> Optional[Dict]:
        """Check claim using Google Fact Check API"""
        try:
            url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
            params = {
                'query': claim[:200],  # API has length limits
                'key': self.google_api_key,
                'languageCode': 'en'
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'claims' in data and len(data['claims']) > 0:
                    # Get the first (most relevant) result
                    first_claim = data['claims'][0]
                    
                    # Extract review information
                    reviews = first_claim.get('claimReview', [])
                    if reviews:
                        review = reviews[0]
                        
                        # Get verdict
                        rating = review.get('textualRating', 'Unverified').lower()
                        verdict = self._normalize_verdict(rating)
                        
                        # Get explanation
                        explanation = review.get('title', '') or first_claim.get('text', 'No explanation provided')
                        
                        # Get source
                        publisher = review.get('publisher', {})
                        source = publisher.get('name', 'Google Fact Check')
                        
                        # Get URL for evidence
                        evidence_url = review.get('url', '')
                        evidence = f"Fact-checked by {source}. {explanation}"
                        if evidence_url:
                            evidence += f" Source: {evidence_url}"
                        
                        # Calculate confidence based on rating
                        confidence = self._calculate_confidence(verdict, True)
                        
                        return self._create_result(
                            claim, verdict, explanation, confidence, 
                            [source, 'Google Fact Check API'], evidence, context
                        )
            
            return None
            
        except Exception as e:
            logger.error(f"[TranscriptFactCheck] Google API error: {e}")
            return None
    
    def _check_with_ai(self, claim: str, speaker: str, context: Optional[Dict]) -> Optional[Dict]:
        """Check claim using OpenAI analysis"""
        try:
            # Build context for AI
            context_info = ""
            if context:
                transcript_preview = context.get('transcript', '')[:500] if context.get('transcript') else ''
                topics = context.get('topics', [])
                
                context_info = f"\nSpeaker: {speaker}\n"
                if topics:
                    context_info += f"Topics: {', '.join(topics)}\n"
                if transcript_preview:
                    context_info += f"Context: ...{transcript_preview}...\n"
            
            prompt = f"""Fact-check this claim from a transcript/speech. Provide a detailed analysis.

Current Date: {self.current_date}

Claim: "{claim}"
{context_info}

Analyze this claim and return ONLY a JSON object with this structure:
{{
  "verdict": "true|mostly_true|partially_true|misleading|mostly_false|false|unverifiable",
  "explanation": "Detailed explanation of why this verdict was chosen (2-3 sentences)",
  "evidence": "Specific evidence or reasoning that supports this verdict",
  "confidence": 70,
  "sources": ["Source 1", "Source 2"]
}}

Rules:
- Be specific about what's true or false
- If numbers are mentioned, verify them
- If it's a prediction, note that future claims are unverifiable
- If it's an opinion, say so but analyze factual elements
- Be objective and thorough"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional fact-checker. Provide detailed, evidence-based analysis. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            result_data = json.loads(content)
            
            # Extract and validate data
            verdict = self._normalize_verdict(result_data.get('verdict', 'unverifiable'))
            explanation = result_data.get('explanation', 'Analysis completed')
            evidence = result_data.get('evidence', 'See explanation above')
            confidence = int(result_data.get('confidence', 70))
            sources = result_data.get('sources', ['AI Analysis'])
            
            if 'AI Analysis' not in sources:
                sources.append('AI Analysis')
            
            return self._create_result(
                claim, verdict, explanation, confidence, sources, evidence, context
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"[TranscriptFactCheck] AI returned invalid JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"[TranscriptFactCheck] AI check error: {e}")
            return None
    
    def _check_with_patterns(self, claim: str, speaker: str, context: Optional[Dict]) -> Dict:
        """Fallback pattern-based analysis"""
        claim_lower = claim.lower()
        
        # Check for opinion indicators
        opinion_words = ['best', 'worst', 'good', 'bad', 'great', 'terrible', 'should', 'believe', 'think']
        if any(word in claim_lower for word in opinion_words):
            return self._create_result(
                claim, 'opinion',
                'This appears to be an opinion or value judgment rather than a factual claim.',
                50, ['Pattern Analysis'], 
                'Opinion indicators detected in claim', context
            )
        
        # Check for future predictions
        future_words = ['will', 'going to', 'shall', 'predict', 'forecast', 'expect']
        if any(word in claim_lower for word in future_words):
            return self._create_result(
                claim, 'unverifiable',
                'This is a prediction about the future and cannot be verified at this time.',
                40, ['Pattern Analysis'],
                'Future-tense claim detected', context
            )
        
        # Check for vague claims
        vague_words = ['many', 'some', 'several', 'most', 'few', 'often', 'rarely']
        if any(word in claim_lower for word in vague_words) and not re.search(r'\d', claim):
            return self._create_result(
                claim, 'unverifiable',
                'This claim is too vague to verify without specific data or context.',
                30, ['Pattern Analysis'],
                'Vague language without specific figures', context
            )
        
        # Check for statistical claims (more likely to be verifiable)
        if re.search(r'\d+\.?\d*\s*%', claim) or re.search(r'\$?\d{1,3}(,\d{3})*', claim):
            return self._create_result(
                claim, 'unverifiable',
                'This claim contains specific statistics that would require fact-checking against official data sources. Without access to those sources, verification is not possible.',
                50, ['Pattern Analysis'],
                'Statistical claim requiring external data verification', context
            )
        
        # Default: unverifiable
        return self._create_result(
            claim, 'unverifiable',
            'Unable to verify this claim with available methods. Additional context or sources would be needed for proper fact-checking.',
            40, ['Pattern Analysis'],
            'Claim requires specialized fact-checking resources', context
        )
    
    def _normalize_verdict(self, verdict_str: str) -> str:
        """Normalize verdict strings to standard categories"""
        verdict_lower = verdict_str.lower().replace(' ', '_').replace('-', '_')
        
        # Direct matches
        if verdict_lower in VERDICT_TYPES:
            return verdict_lower
        
        # Variations mapping
        if verdict_lower in ['correct', 'accurate', 'verified', 'confirmed']:
            return 'true'
        elif verdict_lower in ['incorrect', 'inaccurate', 'debunked', 'wrong']:
            return 'false'
        elif verdict_lower in ['half_true', 'half_correct', 'mixture', 'mixed']:
            return 'partially_true'
        elif verdict_lower in ['exaggerated', 'overstated', 'inflated']:
            return 'misleading'
        elif verdict_lower in ['unverified', 'unknown', 'unclear', 'uncertain']:
            return 'unverifiable'
        
        return 'unverifiable'
    
    def _calculate_confidence(self, verdict: str, has_external_source: bool) -> int:
        """Calculate confidence score"""
        base_confidence = {
            'true': 90,
            'mostly_true': 80,
            'partially_true': 70,
            'misleading': 75,
            'mostly_false': 80,
            'false': 90,
            'unverifiable': 50,
            'opinion': 60
        }
        
        confidence = base_confidence.get(verdict, 50)
        
        # Boost confidence if we have external sources
        if has_external_source and verdict != 'unverifiable':
            confidence = min(confidence + 10, 95)
        
        return confidence
    
    def _create_result(self, claim: str, verdict: str, explanation: str, 
                       confidence: int, sources: List[str], evidence: str,
                       context: Optional[Dict]) -> Dict[str, Any]:
        """Create standardized result dictionary"""
        
        # Get speaker from context
        speaker = 'Unknown'
        if context:
            speaker = context.get('speaker', 'Unknown')
        
        # Get verdict info
        verdict_info = VERDICT_TYPES.get(verdict, VERDICT_TYPES['unverifiable'])
        
        return {
            'claim': claim,
            'speaker': speaker,
            'verdict': verdict,
            'verdict_label': verdict_info['label'],
            'verdict_icon': verdict_info['icon'],
            'verdict_color': verdict_info['color'],
            'verdict_score': verdict_info['score'],
            'explanation': explanation,
            'confidence': confidence,
            'sources': sources if sources else ['Pattern Analysis'],
            'evidence': evidence if evidence else explanation,
            'timestamp': datetime.now().isoformat(),
            'method_used': ', '.join(sources) if sources else 'Pattern Analysis'
        }
    
    def _get_cache_key(self, claim: str) -> str:
        """Generate cache key from claim"""
        import hashlib
        return hashlib.md5(claim.lower().encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict]:
        """Get cached result if available and not expired"""
        if cache_key in self.cache:
            cached_time, result = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                return result.copy()
        return None
    
    def _cache_result(self, cache_key: str, result: Dict):
        """Cache a result"""
        self.cache[cache_key] = (time.time(), result.copy())
        
        # Limit cache size
        if len(self.cache) > 500:
            # Remove oldest 100 entries
            sorted_items = sorted(self.cache.items(), key=lambda x: x[1][0])
            for key, _ in sorted_items[:100]:
                del self.cache[key]


# Backward compatibility alias
ComprehensiveFactChecker = TranscriptComprehensiveFactChecker

# I did no harm and this file is not truncated
