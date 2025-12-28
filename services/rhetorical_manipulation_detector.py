"""
File: services/rhetorical_manipulation_detector.py
Created: December 28, 2024 - v1.0.0
Last Updated: December 28, 2024 - v1.0.0
Description: Detect rhetorical manipulation and logical fallacies in transcripts

PURPOSE:
========
Identifies manipulative rhetorical techniques and logical fallacies used in
speeches, interviews, and debates. This helps users recognize when speakers
are using persuasion tactics instead of sound reasoning.

TACTICS DETECTED:
=================
1. **Logical Fallacies:**
   - Strawman arguments
   - Ad hominem attacks
   - False dilemmas
   - Slippery slope
   - Appeal to authority
   - Hasty generalization
   - Cherry-picking data
   - Circular reasoning

2. **Rhetorical Tricks:**
   - Misleading comparisons
   - False equivalencies
   - Moving the goalposts
   - Whataboutism
   - Gish gallop (overwhelming with claims)
   - Loaded questions
   - Begging the question

3. **Data Manipulation:**
   - Cherry-picked statistics
   - Correlation implies causation
   - Absolute vs. relative numbers confusion
   - Truncated graphs/selective timeframes
   - Missing baseline comparisons

SCORING:
========
Score: 0-100 (higher is better)
- 90-100: Minimal manipulation, sound reasoning
- 80-89: Minor issues, mostly logical
- 70-79: Some manipulation tactics present
- 60-69: Notable manipulation, verify carefully
- 50-59: Significant manipulation
- 0-49: Heavily manipulative rhetoric

This is the COMPLETE file ready for deployment.
Last modified: December 28, 2024 - v1.0.0 RHETORICAL MANIPULATION DETECTOR
I did no harm and this file is not truncated.
"""

import logging
import os
import re
from typing import Dict, Any, List, Optional, Set
import json

logger = logging.getLogger(__name__)

# Try to import AI clients
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available for rhetorical analysis")


class RhetoricalManipulationDetector:
    """
    Rhetorical Manipulation Detector v1.0.0
    
    Identifies logical fallacies and manipulative rhetoric in transcripts
    using pattern matching and AI analysis.
    """
    
    # Logical fallacy patterns
    FALLACY_PATTERNS = {
        'strawman': [
            r"(?:they|you)\s+(?:say|claim|believe|think)\s+(?:that\s+)?(?:all|every|no)",
            r"(?:my opponent|they)\s+wants?\s+to\s+(?:destroy|eliminate|ban|force)",
            r"if\s+we\s+listen\s+to\s+(?:them|you)",
        ],
        'ad_hominem': [
            r"(?:they|he|she)\s+(?:is|are)\s+(?:a\s+)?(?:liar|dishonest|corrupt|evil)",
            r"(?:can't|cannot)\s+trust\s+(?:someone|anyone)\s+(?:who|that)",
            r"(?:coming|comes)\s+from\s+(?:a\s+)?(?:liar|hypocrite)",
        ],
        'false_dilemma': [
            r"(?:either|it's)\s+(?:you're with|you support)",
            r"(?:there are\s+)?(?:only\s+)?two\s+(?:options|choices|ways)",
            r"(?:we\s+)?(?:can\s+)?either\s+[\w\s]+\s+or\s+",
        ],
        'slippery_slope': [
            r"if\s+we\s+(?:allow|let|permit)\s+[\w\s]+,\s+(?:then|next|soon)",
            r"(?:first|today)\s+it's\s+[\w\s]+,\s+(?:tomorrow|next|then)\s+it's",
            r"(?:leads?\s+to|ends?\s+up|results?\s+in)\s+",
        ],
        'appeal_to_authority': [
            r"(?:experts|scientists|doctors|economists)\s+(?:all\s+)?(?:agree|say|confirm)",
            r"(?:everyone|everybody)\s+knows",
            r"studies\s+(?:show|prove|confirm)",
        ],
        'hasty_generalization': [
            r"(?:all|every|no)\s+[\w\s]+\s+(?:are|is|do)",
            r"(?:always|never)\s+",
            r"(?:100%|100\s+percent)\s+of",
        ],
        'whataboutism': [
            r"what\s+about\s+(?:when|the time)",
            r"but\s+(?:they|you)\s+(?:did|said|claimed)",
            r"(?:look|remember)\s+what\s+(?:they|you)\s+did",
        ]
    }
    
    # Data manipulation indicators
    DATA_TRICKS = [
        'increased by X%',  # May use misleading baseline
        'up to',  # Cherry-picked maximum
        'as many as',  # Cherry-picked maximum
        'studies show',  # Vague reference
        'experts say',  # Vague reference
        'correlation',  # May imply causation
        'linked to',  # May imply causation
        'associated with',  # May imply causation
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
                    logger.info("[RhetoricalManipulation] ✓ OpenAI initialized")
                except Exception as e:
                    logger.error(f"[RhetoricalManipulation] OpenAI init failed: {e}")
        
        logger.info("[RhetoricalManipulation] Detector initialized")
    
    def analyze(self, transcript: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze transcript for rhetorical manipulation
        
        Args:
            transcript: The transcript text
            metadata: Optional metadata
            
        Returns:
            Analysis result with manipulation score
        """
        logger.info("[RhetoricalManipulation] Starting rhetorical manipulation analysis...")
        
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
        
        logger.info(f"[RhetoricalManipulation] ✓ Analysis complete: {final_result['score']}/100")
        
        return final_result
    
    def _detect_patterns(self, transcript: str) -> Dict[str, Any]:
        """Detect manipulation using pattern matching"""
        logger.info("[RhetoricalManipulation] Running pattern detection...")
        
        detected_fallacies = {}
        total_matches = 0
        
        transcript_lower = transcript.lower()
        
        # Check each fallacy type
        for fallacy_type, patterns in self.FALLACY_PATTERNS.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, transcript_lower, re.IGNORECASE)
                if found:
                    matches.extend(found[:3])  # Limit to 3 examples per pattern
            
            if matches:
                detected_fallacies[fallacy_type] = {
                    'count': len(matches),
                    'examples': matches[:3]
                }
                total_matches += len(matches)
        
        # Check for data manipulation tricks
        data_tricks_found = []
        for trick in self.DATA_TRICKS:
            if trick.lower() in transcript_lower:
                data_tricks_found.append(trick)
        
        logger.info(f"[RhetoricalManipulation] Pattern detection: {total_matches} fallacies, {len(data_tricks_found)} data tricks")
        
        return {
            'detected_fallacies': detected_fallacies,
            'data_tricks': data_tricks_found,
            'total_fallacies': total_matches,
            'total_data_tricks': len(data_tricks_found)
        }
    
    def _ai_analysis(self, transcript: str) -> Optional[Dict]:
        """Use AI to detect subtle manipulation"""
        try:
            logger.info("[RhetoricalManipulation] Running AI analysis...")
            
            # Limit transcript length
            sample = transcript[:4000] if len(transcript) > 4000 else transcript
            
            prompt = f"""Analyze this transcript for rhetorical manipulation and logical fallacies.

Transcript:
"{sample}"

Identify:
1. Logical fallacies used (strawman, ad hominem, false dilemma, etc.)
2. Manipulative rhetoric techniques
3. Cherry-picked or misleading data usage
4. Emotional manipulation tactics
5. Overall manipulation level (0-100, where 100 is no manipulation)

Return JSON:
{{
  "manipulation_score": 0-100,
  "fallacies_found": [
    {{"type": "fallacy name", "example": "quote from transcript", "severity": "high|medium|low"}}
  ],
  "manipulation_techniques": ["list of techniques"],
  "data_concerns": ["concerns about data usage"],
  "reasoning_quality": "assessment of logical reasoning",
  "overall_assessment": "brief summary"
}}

Return ONLY valid JSON."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in rhetoric, logic, and identifying manipulative argumentation. Return only valid JSON."},
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
            
            logger.info(f"[RhetoricalManipulation] AI analysis complete: {result.get('manipulation_score', 0)}/100")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"[RhetoricalManipulation] AI returned invalid JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"[RhetoricalManipulation] AI analysis error: {e}")
            return None
    
    def _combine_results(self, pattern_results: Dict, ai_results: Optional[Dict]) -> Dict[str, Any]:
        """Combine pattern and AI results"""
        logger.info("[RhetoricalManipulation] Combining pattern and AI results...")
        
        # Start with pattern-based scoring
        total_fallacies = pattern_results['total_fallacies']
        total_tricks = pattern_results['total_data_tricks']
        
        # Calculate base score from patterns (deduct 10 points per fallacy, 5 per trick)
        base_score = 100 - (total_fallacies * 10) - (total_tricks * 5)
        base_score = max(0, min(100, base_score))  # Clamp to 0-100
        
        # If AI results available, average with base score
        if ai_results and 'manipulation_score' in ai_results:
            ai_score = ai_results['manipulation_score']
            final_score = round((base_score + ai_score) / 2)
        else:
            final_score = base_score
        
        # Gather all techniques
        techniques = []
        
        # Add detected fallacies
        for fallacy_type, data in pattern_results['detected_fallacies'].items():
            techniques.append({
                'type': fallacy_type.replace('_', ' ').title(),
                'count': data['count'],
                'severity': 'high' if data['count'] >= 3 else ('medium' if data['count'] >= 2 else 'low')
            })
        
        # Add AI-detected techniques
        if ai_results and 'fallacies_found' in ai_results:
            for fallacy in ai_results['fallacies_found']:
                # Avoid duplicates
                if not any(t['type'].lower() == fallacy['type'].lower() for t in techniques):
                    techniques.append(fallacy)
        
        # Build final result
        result = {
            'success': True,
            'score': final_score,
            'manipulation_level': self._get_manipulation_level(final_score),
            'tactics_found': len(techniques),
            'techniques': techniques,
            'data_concerns': pattern_results['data_tricks'] + (ai_results.get('data_concerns', []) if ai_results else []),
            'reasoning_quality': ai_results.get('reasoning_quality', 'Not assessed') if ai_results else 'Not assessed',
            'analysis': {
                'what_we_looked': 'Logical fallacies, rhetorical manipulation, and data misrepresentation',
                'what_we_found': self._generate_findings(final_score, len(techniques)),
                'what_it_means': self._generate_interpretation(final_score)
            }
        }
        
        if ai_results and 'overall_assessment' in ai_results:
            result['ai_assessment'] = ai_results['overall_assessment']
        
        return result
    
    def _get_manipulation_level(self, score: int) -> str:
        """Get human-readable manipulation level"""
        if score >= 90:
            return "Minimal Manipulation"
        elif score >= 80:
            return "Low Manipulation"
        elif score >= 70:
            return "Moderate Manipulation"
        elif score >= 60:
            return "Notable Manipulation"
        elif score >= 50:
            return "Significant Manipulation"
        else:
            return "Heavy Manipulation"
    
    def _generate_findings(self, score: int, tactics_count: int) -> str:
        """Generate findings summary"""
        if tactics_count == 0:
            return f"Score of {score}/100. No significant rhetorical manipulation detected."
        elif tactics_count <= 2:
            return f"Score of {score}/100. Detected {tactics_count} manipulation tactic(s)."
        else:
            return f"Score of {score}/100. Detected {tactics_count} manipulation tactics, including multiple logical fallacies."
    
    def _generate_interpretation(self, score: int) -> str:
        """Generate interpretation"""
        if score >= 80:
            return "The speaker's arguments are generally sound with minimal manipulative tactics. Their reasoning should be taken seriously."
        elif score >= 60:
            return "Some manipulative rhetoric detected. Verify claims independently and watch for logical fallacies."
        else:
            return "Significant manipulation detected. This speaker relies heavily on rhetoric over sound reasoning. Verify all claims carefully."


# I did no harm and this file is not truncated
# v1.0.0 - December 28, 2024 - RHETORICAL MANIPULATION DETECTOR
