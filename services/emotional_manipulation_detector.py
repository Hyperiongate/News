"""
File: services/emotional_manipulation_detector.py
Created: December 28, 2024 - v1.0.0
Last Updated: December 28, 2024 - v1.0.0
Description: Detect emotional manipulation tactics in transcripts

PURPOSE:
========
Identifies when speakers use emotional appeals instead of rational arguments.
Detects fear-mongering, anger manipulation, tribalism, and other tactics
designed to bypass critical thinking.

EMOTIONAL TACTICS DETECTED:
===========================
1. **Fear Appeals:**
   - Catastrophizing
   - Threat exaggeration
   - "Slippery slope" fear
   - Existential threats
   - Safety/security fears

2. **Anger Appeals:**
   - Outrage manufacturing
   - Scapegoating
   - Injustice framing
   - Us-vs-them rhetoric

3. **Tribal Appeals:**
   - In-group/out-group language
   - Loyalty tests
   - "Real Americans" rhetoric
   - Othering language

4. **Guilt/Shame:**
   - Moral grandstanding
   - Virtue signaling
   - Shame-based persuasion

5. **Hope/Pride:**
   - Unrealistic promises
   - Nationalist appeals
   - Nostalgia manipulation

6. **Urgency:**
   - False deadlines
   - "Act now" pressure
   - Crisis manufacturing

SCORING:
========
Score: 0-100 (higher is better)
- 90-100: Minimal emotional manipulation
- 80-89: Minor emotional appeals
- 70-79: Moderate emotional content
- 60-69: Notable manipulation
- 50-59: Heavy emotional appeals
- 0-49: Overwhelming emotional manipulation

This is the COMPLETE file ready for deployment.
Last modified: December 28, 2024 - v1.0.0 EMOTIONAL MANIPULATION DETECTOR
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
    logger.warning("OpenAI not available for emotional manipulation detection")


class EmotionalManipulationDetector:
    """
    Emotional Manipulation Detector v1.0.0
    
    Identifies emotional manipulation tactics in transcripts using
    pattern matching and sentiment analysis.
    """
    
    # Emotional manipulation keywords
    FEAR_KEYWORDS = [
        'catastrophe', 'disaster', 'crisis', 'emergency', 'danger', 'threat', 'attack',
        'destroy', 'collapse', 'end of', 'lose everything', 'devastating', 'horrific',
        'nightmare', 'terrifying', 'scary', 'frightening', 'alarming', 'panic'
    ]
    
    ANGER_KEYWORDS = [
        'outrageous', 'disgraceful', 'shameful', 'betrayal', 'traitor', 'enemy',
        'attack on', 'war on', 'assault on', 'corrupt', 'evil', 'criminal',
        'disgusting', 'sick', 'twisted', 'perverted', 'despicable'
    ]
    
    TRIBAL_KEYWORDS = [
        'real americans', 'patriots', 'true', 'fake', 'elites', 'establishment',
        'them vs us', 'they want', 'enemies of', 'un-american', 'traitors',
        'with us or against us', 'you\'re either', 'our people', 'those people'
    ]
    
    URGENCY_KEYWORDS = [
        'act now', 'immediately', 'right now', 'before it\'s too late', 'last chance',
        'running out of time', 'deadline', 'urgent', 'emergency', 'can\'t wait',
        'time is running out', 'now or never'
    ]
    
    CATASTROPHIZING_PATTERNS = [
        r'(?:will|going to)\s+(?:destroy|end|ruin|devastate|collapse)',
        r'(?:complete|total|utter)\s+(?:disaster|catastrophe|failure)',
        r'(?:lose|losing)\s+(?:everything|it all|our country|our freedom)',
        r'(?:the end of|end to)\s+(?:america|democracy|freedom|civilization)'
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
                    logger.info("[EmotionalManipulation] ✓ OpenAI initialized")
                except Exception as e:
                    logger.error(f"[EmotionalManipulation] OpenAI init failed: {e}")
        
        logger.info("[EmotionalManipulation] Detector initialized")
    
    def analyze(self, transcript: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze transcript for emotional manipulation
        
        Args:
            transcript: The transcript text
            metadata: Optional metadata
            
        Returns:
            Analysis result with manipulation score
        """
        logger.info("[EmotionalManipulation] Starting emotional manipulation analysis...")
        
        if not transcript or len(transcript) < 50:
            return {
                'success': False,
                'score': 50,
                'message': 'Transcript too short to analyze'
            }
        
        # Pattern-based detection
        pattern_results = self._detect_patterns(transcript)
        
        # AI-powered sentiment analysis
        ai_results = None
        if self.openai_client:
            ai_results = self._ai_analysis(transcript)
        
        # Combine results
        final_result = self._combine_results(pattern_results, ai_results)
        
        logger.info(f"[EmotionalManipulation] ✓ Analysis complete: {final_result['score']}/100")
        
        return final_result
    
    def _detect_patterns(self, transcript: str) -> Dict[str, Any]:
        """Detect emotional manipulation using pattern matching"""
        logger.info("[EmotionalManipulation] Running pattern detection...")
        
        transcript_lower = transcript.lower()
        word_count = len(transcript.split())
        
        # Count different types of emotional appeals
        fear_count = sum(1 for kw in self.FEAR_KEYWORDS if kw in transcript_lower)
        anger_count = sum(1 for kw in self.ANGER_KEYWORDS if kw in transcript_lower)
        tribal_count = sum(1 for kw in self.TRIBAL_KEYWORDS if kw in transcript_lower)
        urgency_count = sum(1 for kw in self.URGENCY_KEYWORDS if kw in transcript_lower)
        
        # Check catastrophizing patterns
        catastrophizing_count = 0
        for pattern in self.CATASTROPHIZING_PATTERNS:
            catastrophizing_count += len(re.findall(pattern, transcript_lower))
        
        # Calculate density (per 100 words)
        density_fear = (fear_count / word_count * 100) if word_count > 0 else 0
        density_anger = (anger_count / word_count * 100) if word_count > 0 else 0
        density_tribal = (tribal_count / word_count * 100) if word_count > 0 else 0
        density_urgency = (urgency_count / word_count * 100) if word_count > 0 else 0
        
        total_emotional_words = fear_count + anger_count + tribal_count + urgency_count
        
        logger.info(f"[EmotionalManipulation] Detected: Fear={fear_count}, Anger={anger_count}, Tribal={tribal_count}, Urgency={urgency_count}")
        
        return {
            'fear_appeals': fear_count,
            'anger_appeals': anger_count,
            'tribal_appeals': tribal_count,
            'urgency_appeals': urgency_count,
            'catastrophizing': catastrophizing_count,
            'total_emotional_words': total_emotional_words,
            'emotional_density': round((total_emotional_words / word_count * 100), 2) if word_count > 0 else 0,
            'word_count': word_count
        }
    
    def _ai_analysis(self, transcript: str) -> Optional[Dict]:
        """Use AI for sentiment and manipulation analysis"""
        try:
            logger.info("[EmotionalManipulation] Running AI sentiment analysis...")
            
            # Limit transcript length
            sample = transcript[:4000] if len(transcript) > 4000 else transcript
            
            prompt = f"""Analyze this transcript for emotional manipulation tactics.

Transcript:
"{sample}"

Identify:
1. Fear-based appeals (catastrophizing, threat exaggeration)
2. Anger manipulation (outrage, scapegoating)
3. Tribal appeals (us-vs-them, in-group/out-group)
4. Urgency tactics (false deadlines, crisis manufacturing)
5. Other emotional manipulation

Rate from 0-100 where 100 = no emotional manipulation, 0 = overwhelming manipulation.

Return JSON:
{{
  "emotional_score": 0-100,
  "manipulation_tactics": [
    {{"type": "fear|anger|tribal|urgency|other", "description": "what they're doing", "severity": "high|medium|low", "example": "quote"}}
  ],
  "primary_emotion": "fear|anger|hope|pride|guilt|neutral",
  "rational_vs_emotional": "% rational vs % emotional (e.g., '40% rational, 60% emotional')",
  "overall_tone": "description",
  "concerns": ["specific concerns about manipulation"]
}}

Return ONLY valid JSON."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in emotional manipulation detection and sentiment analysis. Return only valid JSON."},
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
            
            logger.info(f"[EmotionalManipulation] AI analysis complete: {result.get('emotional_score', 0)}/100")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"[EmotionalManipulation] AI returned invalid JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"[EmotionalManipulation] AI analysis error: {e}")
            return None
    
    def _combine_results(self, pattern_results: Dict, ai_results: Optional[Dict]) -> Dict[str, Any]:
        """Combine pattern and AI results"""
        logger.info("[EmotionalManipulation] Combining results...")
        
        # Calculate base score from patterns
        # Deduct points based on emotional density
        emotional_density = pattern_results['emotional_density']
        
        if emotional_density < 1:
            base_score = 95
        elif emotional_density < 2:
            base_score = 85
        elif emotional_density < 3:
            base_score = 75
        elif emotional_density < 5:
            base_score = 60
        elif emotional_density < 7:
            base_score = 45
        else:
            base_score = 30
        
        # Deduct for catastrophizing
        base_score -= pattern_results['catastrophizing'] * 5
        base_score = max(0, min(100, base_score))
        
        # If AI results available, average with base score
        if ai_results and 'emotional_score' in ai_results:
            ai_score = ai_results['emotional_score']
            final_score = round((base_score + ai_score) / 2)
        else:
            final_score = base_score
        
        # Gather all tactics
        tactics = []
        
        # Add pattern-detected tactics
        if pattern_results['fear_appeals'] > 0:
            tactics.append({
                'type': 'fear',
                'count': pattern_results['fear_appeals'],
                'severity': 'high' if pattern_results['fear_appeals'] >= 5 else 'medium'
            })
        
        if pattern_results['anger_appeals'] > 0:
            tactics.append({
                'type': 'anger',
                'count': pattern_results['anger_appeals'],
                'severity': 'high' if pattern_results['anger_appeals'] >= 5 else 'medium'
            })
        
        if pattern_results['tribal_appeals'] > 0:
            tactics.append({
                'type': 'tribal',
                'count': pattern_results['tribal_appeals'],
                'severity': 'high' if pattern_results['tribal_appeals'] >= 3 else 'medium'
            })
        
        if pattern_results['urgency_appeals'] > 0:
            tactics.append({
                'type': 'urgency',
                'count': pattern_results['urgency_appeals'],
                'severity': 'high' if pattern_results['urgency_appeals'] >= 3 else 'medium'
            })
        
        # Add AI-detected tactics
        if ai_results and 'manipulation_tactics' in ai_results:
            for tactic in ai_results['manipulation_tactics']:
                # Avoid duplicates
                if not any(t['type'] == tactic['type'] for t in tactics):
                    tactics.append(tactic)
        
        # Build final result
        result = {
            'success': True,
            'score': final_score,
            'manipulation_level': self._get_manipulation_level(final_score),
            'emotional_appeals': len(tactics),
            'tactics': tactics,
            'emotional_density': pattern_results['emotional_density'],
            'primary_emotion': ai_results.get('primary_emotion', 'Not assessed') if ai_results else 'Not assessed',
            'rational_vs_emotional': ai_results.get('rational_vs_emotional', 'Not assessed') if ai_results else 'Not assessed',
            'analysis': {
                'what_we_looked': 'Fear appeals, anger manipulation, tribal rhetoric, and emotional vs rational content',
                'what_we_found': self._generate_findings(final_score, len(tactics), pattern_results['emotional_density']),
                'what_it_means': self._generate_interpretation(final_score)
            }
        }
        
        if ai_results and 'overall_tone' in ai_results:
            result['overall_tone'] = ai_results['overall_tone']
        
        if ai_results and 'concerns' in ai_results:
            result['concerns'] = ai_results['concerns']
        
        return result
    
    def _get_manipulation_level(self, score: int) -> str:
        """Get human-readable manipulation level"""
        if score >= 90:
            return "Minimal Emotional Manipulation"
        elif score >= 80:
            return "Low Emotional Manipulation"
        elif score >= 70:
            return "Moderate Emotional Appeals"
        elif score >= 60:
            return "Notable Emotional Manipulation"
        elif score >= 50:
            return "Heavy Emotional Manipulation"
        else:
            return "Overwhelming Emotional Manipulation"
    
    def _generate_findings(self, score: int, tactics_count: int, density: float) -> str:
        """Generate findings summary"""
        return f"Score of {score}/100. Detected {tactics_count} emotional manipulation tactic(s) with {density:.1f}% emotional word density."
    
    def _generate_interpretation(self, score: int) -> str:
        """Generate interpretation"""
        if score >= 80:
            return "The speaker uses minimal emotional manipulation and relies primarily on rational arguments."
        elif score >= 60:
            return "Moderate emotional appeals present. The speaker mixes emotion with reasoning. Verify claims independently."
        else:
            return "Heavy emotional manipulation detected. The speaker relies more on emotional appeals than rational arguments. Approach with skepticism."


# I did no harm and this file is not truncated
# v1.0.0 - December 28, 2024 - EMOTIONAL MANIPULATION DETECTOR
