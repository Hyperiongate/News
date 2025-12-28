"""
File: services/transcript_bias_detector.py
Created: December 28, 2024 - v1.0.0
Last Updated: December 28, 2024 - v1.0.0
Description: Detect political and ideological bias in transcripts

PURPOSE:
========
Identifies political lean, ideological framing, and partisan language in
speeches, interviews, and debates. Helps users understand the speaker's
perspective and potential biases.

BIAS INDICATORS DETECTED:
=========================
1. **Partisan Talking Points:**
   - Conservative vs progressive language
   - Party-specific framing
   - Buzzwords and dog whistles

2. **Framing Analysis:**
   - How issues are presented
   - What's emphasized vs downplayed
   - Narrative structure

3. **Source Selection:**
   - Which sources are cited
   - Which perspectives are included/excluded
   - Balance of viewpoints

4. **Language Patterns:**
   - Loaded terminology
   - Euphemisms
   - Connotation analysis

SCORING:
========
Score: 0-100 (higher is better, neutral is around 50)
- 90-100: Highly balanced, minimal bias
- 70-89: Generally balanced with slight lean
- 50-69: Moderate bias present
- 30-49: Strong bias
- 0-29: Extreme bias

Bias Direction:
- Left/Progressive
- Center-Left
- Centrist
- Center-Right  
- Right/Conservative

This is the COMPLETE file ready for deployment.
Last modified: December 28, 2024 - v1.0.0 TRANSCRIPT BIAS DETECTOR
I did no harm and this file is not truncated.
"""

import logging
import os
import re
from typing import Dict, Any, List, Optional
import json

logger = logging.getLogger(__name__)

# Try to import AI clients
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available for bias detection")


class TranscriptBiasDetector:
    """
    Transcript Bias Detector v1.0.0
    
    Identifies political and ideological bias in transcripts.
    """
    
    # Conservative-leaning keywords
    CONSERVATIVE_KEYWORDS = [
        'freedom', 'liberty', 'constitution', 'founding fathers', 'patriot', 
        'traditional values', 'law and order', 'personal responsibility',
        'free market', 'small government', 'second amendment', 'pro-life',
        'illegal immigration', 'border security', 'family values'
    ]
    
    # Progressive-leaning keywords
    PROGRESSIVE_KEYWORDS = [
        'equality', 'equity', 'social justice', 'systemic', 'marginalized',
        'climate crisis', 'renewable energy', 'healthcare is a right',
        'living wage', 'wealth inequality', 'reproductive rights', 'pro-choice',
        'immigrant rights', 'inclusive', 'diversity'
    ]
    
    # Loaded terms (negative framing)
    LOADED_CONSERVATIVE = [
        'radical left', 'socialist', 'woke', 'cancel culture', 'mainstream media',
        'big government', 'tax and spend', 'job-killing'
    ]
    
    LOADED_PROGRESSIVE = [
        'far-right', 'extremist', 'corporate greed', 'trickle-down',
        'climate denier', 'voter suppression', 'dark money'
    ]
    
    def __init__(self):
        """Initialize the detector"""
        self.openai_client = None
        
        # Initialize OpenAI if available
        if OPENAI_AVAILABLE:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                try:
                    self.openai_client = OpenAI(api_key=api_key)
                    logger.info("[TranscriptBias] ✓ OpenAI initialized")
                except Exception as e:
                    logger.error(f"[TranscriptBias] OpenAI init failed: {e}")
        
        logger.info("[TranscriptBias] Detector initialized")
    
    def analyze(self, transcript: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze transcript for political/ideological bias
        
        Args:
            transcript: The transcript text
            metadata: Optional metadata
            
        Returns:
            Analysis result with bias score
        """
        logger.info("[TranscriptBias] Starting bias detection...")
        
        if not transcript or len(transcript) < 50:
            return {
                'success': False,
                'score': 50,
                'message': 'Transcript too short to analyze'
            }
        
        # Pattern-based detection
        pattern_results = self._detect_patterns(transcript)
        
        # AI-powered analysis
        ai_results = None
        if self.openai_client:
            ai_results = self._ai_analysis(transcript)
        
        # Combine results
        final_result = self._combine_results(pattern_results, ai_results)
        
        logger.info(f"[TranscriptBias] ✓ Analysis complete: {final_result['score']}/100, {final_result['bias_direction']}")
        
        return final_result
    
    def _detect_patterns(self, transcript: str) -> Dict[str, Any]:
        """Detect bias using keyword analysis"""
        logger.info("[TranscriptBias] Running keyword analysis...")
        
        transcript_lower = transcript.lower()
        
        # Count keywords
        conservative_count = sum(1 for kw in self.CONSERVATIVE_KEYWORDS if kw in transcript_lower)
        progressive_count = sum(1 for kw in self.PROGRESSIVE_KEYWORDS if kw in transcript_lower)
        
        loaded_conservative_count = sum(1 for kw in self.LOADED_CONSERVATIVE if kw in transcript_lower)
        loaded_progressive_count = sum(1 for kw in self.LOADED_PROGRESSIVE if kw in transcript_lower)
        
        # Calculate bias lean
        total_partisan = conservative_count + progressive_count
        
        if total_partisan > 0:
            conservative_ratio = conservative_count / total_partisan
            progressive_ratio = progressive_count / total_partisan
        else:
            conservative_ratio = 0.5
            progressive_ratio = 0.5
        
        logger.info(f"[TranscriptBias] Keywords: Conservative={conservative_count}, Progressive={progressive_count}")
        logger.info(f"[TranscriptBias] Loaded terms: Conservative={loaded_conservative_count}, Progressive={loaded_progressive_count}")
        
        return {
            'conservative_keywords': conservative_count,
            'progressive_keywords': progressive_count,
            'loaded_conservative': loaded_conservative_count,
            'loaded_progressive': loaded_progressive_count,
            'conservative_ratio': round(conservative_ratio, 2),
            'progressive_ratio': round(progressive_ratio, 2),
            'total_partisan_keywords': total_partisan
        }
    
    def _ai_analysis(self, transcript: str) -> Optional[Dict]:
        """Use AI for sophisticated bias detection"""
        try:
            logger.info("[TranscriptBias] Running AI bias analysis...")
            
            # Limit transcript length
            sample = transcript[:4000] if len(transcript) > 4000 else transcript
            
            prompt = f"""Analyze this transcript for political and ideological bias.

Transcript:
"{sample}"

Assess:
1. Political lean (far-left, left, center-left, center, center-right, right, far-right)
2. Bias indicators (framing, language, source selection)
3. Balance and fairness
4. Partisan talking points used
5. Overall bias level (0-100, where 50 is neutral, higher is less biased)

Return JSON:
{{
  "bias_score": 0-100,
  "political_lean": "far-left|left|center-left|center|center-right|right|far-right",
  "lean_confidence": 0-100,
  "bias_indicators": [
    {{"type": "framing|language|sources|talking_points", "description": "what indicates bias", "example": "quote"}}
  ],
  "talking_points": ["list partisan talking points detected"],
  "balance_assessment": "how balanced or biased",
  "fairness_concerns": ["specific concerns"]
}}

Return ONLY valid JSON."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in political communication and bias detection. Be objective and evidence-based. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
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
            
            result = json.loads(content)
            
            logger.info(f"[TranscriptBias] AI analysis: {result.get('bias_score', 0)}/100, {result.get('political_lean', 'unknown')}")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"[TranscriptBias] AI returned invalid JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"[TranscriptBias] AI analysis error: {e}")
            return None
    
    def _combine_results(self, pattern_results: Dict, ai_results: Optional[Dict]) -> Dict[str, Any]:
        """Combine pattern and AI results"""
        logger.info("[TranscriptBias] Combining results...")
        
        # Determine bias direction from patterns
        conservative_ratio = pattern_results['conservative_ratio']
        progressive_ratio = pattern_results['progressive_ratio']
        
        # Calculate base score
        # Score decreases with loaded language and partisan imbalance
        loaded_total = pattern_results['loaded_conservative'] + pattern_results['loaded_progressive']
        
        # Start at 100, deduct for bias
        base_score = 100
        base_score -= loaded_total * 5  # 5 points per loaded term
        
        # Deduct for partisan imbalance
        imbalance = abs(conservative_ratio - progressive_ratio)
        if imbalance > 0.7:
            base_score -= 30  # Heavy lean
        elif imbalance > 0.5:
            base_score -= 20  # Moderate lean
        elif imbalance > 0.3:
            base_score -= 10  # Slight lean
        
        base_score = max(0, min(100, base_score))
        
        # Determine direction from keywords
        if conservative_ratio > 0.6:
            pattern_direction = "right" if conservative_ratio < 0.8 else "far-right"
        elif progressive_ratio > 0.6:
            pattern_direction = "left" if progressive_ratio < 0.8 else "far-left"
        else:
            pattern_direction = "center"
        
        # If AI results available, use them with higher weight
        if ai_results and 'bias_score' in ai_results:
            ai_score = ai_results['bias_score']
            final_score = round((base_score * 0.4) + (ai_score * 0.6))
            
            bias_direction = ai_results.get('political_lean', pattern_direction)
        else:
            final_score = base_score
            bias_direction = pattern_direction
        
        # Gather bias indicators
        indicators = []
        
        if pattern_results['loaded_conservative'] > 0:
            indicators.append({
                'type': 'language',
                'description': f"Uses {pattern_results['loaded_conservative']} conservative-leaning loaded terms",
                'severity': 'medium'
            })
        
        if pattern_results['loaded_progressive'] > 0:
            indicators.append({
                'type': 'language',
                'description': f"Uses {pattern_results['loaded_progressive']} progressive-leaning loaded terms",
                'severity': 'medium'
            })
        
        # Add AI indicators
        if ai_results and 'bias_indicators' in ai_results:
            indicators.extend(ai_results['bias_indicators'])
        
        # Build result
        result = {
            'success': True,
            'score': final_score,
            'bias_direction': bias_direction,
            'bias_level': self._get_bias_level(final_score),
            'conservative_ratio': pattern_results['conservative_ratio'],
            'progressive_ratio': pattern_results['progressive_ratio'],
            'bias_indicators': indicators,
            'talking_points': ai_results.get('talking_points', []) if ai_results else [],
            'analysis': {
                'what_we_looked': 'Political lean, partisan language, framing, and talking points',
                'what_we_found': self._generate_findings(final_score, bias_direction, len(indicators)),
                'what_it_means': self._generate_interpretation(final_score, bias_direction)
            }
        }
        
        if ai_results and 'balance_assessment' in ai_results:
            result['balance_assessment'] = ai_results['balance_assessment']
        
        return result
    
    def _get_bias_level(self, score: int) -> str:
        """Get human-readable bias level"""
        if score >= 90:
            return "Minimal Bias"
        elif score >= 70:
            return "Slight Bias"
        elif score >= 50:
            return "Moderate Bias"
        elif score >= 30:
            return "Strong Bias"
        else:
            return "Extreme Bias"
    
    def _generate_findings(self, score: int, direction: str, indicators_count: int) -> str:
        """Generate findings summary"""
        return f"Score of {score}/100 with {direction} lean. Detected {indicators_count} bias indicator(s)."
    
    def _generate_interpretation(self, score: int, direction: str) -> str:
        """Generate interpretation"""
        if score >= 80:
            return f"The speaker shows minimal bias with a slight {direction} lean. Generally balanced perspective."
        elif score >= 60:
            return f"Moderate {direction} bias detected. Consider alternative perspectives when evaluating claims."
        else:
            return f"Strong {direction} bias detected. This speaker presents a clearly partisan perspective. Verify claims independently."


# I did no harm and this file is not truncated
# v1.0.0 - December 28, 2024 - TRANSCRIPT BIAS DETECTOR
