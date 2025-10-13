"""
Manipulation Detector - v3.0 COMPLETE IMPLEMENTATION
Date: October 12, 2025
Last Updated: October 12, 2025 - FIXED ABSTRACT METHOD ERROR

FIXES IN v3.0:
✅ CRITICAL: Implemented missing _check_availability() method (was causing abstract class error)
✅ ENHANCED: Full manipulation detection: clickbait, fear-mongering, loaded language, false equivalence
✅ ENHANCED: AI-powered manipulation pattern detection when OpenAI available
✅ PRESERVED: All existing functionality, added proper implementation

THE BUG WE FIXED:
- Error: "Can't instantiate abstract class ManipulationDetector with abstract method _check_availability"
- Service was defined but not properly implemented
- Missing required method from BaseAnalyzer

THE SOLUTION:
- Implemented _check_availability() method
- Complete manipulation detection based on psychological tactics
- Proper service structure that matches other working services

Save as: services/manipulation_detector.py (REPLACE existing file)
"""

import logging
import time
import re
from typing import Dict, Any, List, Optional, Tuple

try:
    from openai import OpenAI
    import httpx
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from services.base_analyzer import BaseAnalyzer
from config import Config

logger = logging.getLogger(__name__)


class ManipulationDetector(BaseAnalyzer):
    """
    Detects manipulation tactics in articles: clickbait, fear-mongering, loaded language
    v3.0 - Fully implemented with _check_availability()
    """
    
    def __init__(self):
        super().__init__('manipulation_detector')
        
        # Initialize OpenAI if available
        self.openai_client = None
        if OPENAI_AVAILABLE and Config.OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(
                    api_key=Config.OPENAI_API_KEY,
                    timeout=httpx.Timeout(8.0, connect=2.0)
                )
                logger.info("[ManipulationDetector v3.0] OpenAI client initialized")
            except Exception as e:
                logger.warning(f"[ManipulationDetector v3.0] Failed to initialize OpenAI: {e}")
                self.openai_client = None
        
        # Manipulation pattern libraries
        self._initialize_patterns()
        
        logger.info(f"[ManipulationDetector v3.0] Initialized - AI: {bool(self.openai_client)}")
    
    def _check_availability(self) -> bool:
        """
        CRITICAL FIX v3.0: Implement required abstract method
        Service is always available (runs with or without AI)
        """
        return True
    
    def _initialize_patterns(self):
        """Initialize manipulation detection patterns"""
        
        # Fear-mongering words
        self.fear_words = [
            'crisis', 'disaster', 'catastrophe', 'epidemic', 'pandemic',
            'threat', 'danger', 'risk', 'warning', 'alert', 'urgent',
            'terrifying', 'horrifying', 'shocking', 'devastating', 'deadly'
        ]
        
        # Clickbait phrases
        self.clickbait_phrases = [
            r'you won\'t believe',
            r'what happened next',
            r'will shock you',
            r'this is why',
            r'the truth about',
            r'what [A-Z].*doesn\'t want you to know',
            r'everything you know.*is wrong',
            r'number \d+ will',
            r'doctors hate',
            r'this one trick'
        ]
        
        # Loaded/emotional language
        self.loaded_words = [
            'slammed', 'blasted', 'destroyed', 'annihilated', 'crushed',
            'obliterated', 'demolished', 'eviscerated', 'shredded',
            'radical', 'extreme', 'outrageous', 'insane', 'crazy',
            'unbelievable', 'incredible', 'amazing', 'stunning'
        ]
        
        # Appeal to emotion
        self.emotion_appeals = [
            r'think of the children',
            r'for your [family|loved ones]',
            r'protect your [family|children|loved ones]',
            r'imagine if',
            r'what if',
            r'could happen to you'
        ]
        
        # False urgency
        self.urgency_phrases = [
            r'act now',
            r'limited time',
            r'before it\'s too late',
            r'don\'t wait',
            r'urgent',
            r'breaking',
            r'just in'
        ]
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze article for manipulation tactics
        Detects: clickbait, fear-mongering, loaded language, false equivalence, appeals to emotion
        """
        try:
            start_time = time.time()
            
            # Extract content
            text = data.get('text', '') or data.get('content', '')
            title = data.get('title', '')
            
            if not text:
                return self.get_error_result("No content provided for manipulation detection")
            
            # Extract metadata
            source = data.get('source', 'Unknown')
            url = data.get('url', '')
            
            logger.info(f"[ManipulationDetector v3.0] Analyzing {len(text)} chars from {source}")
            
            # 1. Detect clickbait in title
            clickbait_score, clickbait_detected = self._detect_clickbait(title)
            
            # 2. Detect fear-mongering
            fear_score, fear_examples = self._detect_fear_mongering(text)
            
            # 3. Detect loaded language
            loaded_language_score, loaded_examples = self._detect_loaded_language(text)
            
            # 4. Detect emotional manipulation
            emotion_score, emotion_examples = self._detect_emotional_manipulation(text)
            
            # 5. Detect false urgency
            urgency_score, urgency_examples = self._detect_false_urgency(text + ' ' + title)
            
            # 6. Detect false balance/equivalence
            false_balance_score = self._detect_false_balance(text)
            
            # 7. Calculate emotional intensity
            emotional_intensity = self._calculate_emotional_intensity(text)
            
            # 8. AI enhancement if available
            ai_tactics = []
            if self.openai_client:
                ai_tactics = self._get_ai_manipulation_analysis(text[:2000], title)
            
            # Compile all detected tactics
            tactics_found = []
            
            if clickbait_detected:
                tactics_found.append({
                    'name': 'Clickbait Headline',
                    'severity': 'medium',
                    'description': 'Headline uses attention-grabbing techniques',
                    'example': title
                })
            
            for example in fear_examples:
                tactics_found.append({
                    'name': 'Fear-Mongering',
                    'severity': 'high',
                    'description': 'Uses scary language to trigger emotional response',
                    'example': example
                })
            
            for example in loaded_examples[:3]:  # Limit to 3
                tactics_found.append({
                    'name': 'Loaded Language',
                    'severity': 'medium',
                    'description': 'Uses emotionally charged words',
                    'example': example
                })
            
            for example in emotion_examples:
                tactics_found.append({
                    'name': 'Emotional Appeal',
                    'severity': 'medium',
                    'description': 'Appeals to emotions rather than facts',
                    'example': example
                })
            
            for example in urgency_examples:
                tactics_found.append({
                    'name': 'False Urgency',
                    'severity': 'low',
                    'description': 'Creates artificial sense of urgency',
                    'example': example
                })
            
            if false_balance_score > 50:
                tactics_found.append({
                    'name': 'False Balance',
                    'severity': 'medium',
                    'description': 'Treats unequal things as equally valid',
                    'example': 'Both sides framing detected'
                })
            
            # Add AI-detected tactics
            tactics_found.extend(ai_tactics)
            
            # Calculate integrity score (inverse of manipulation)
            integrity_score = self._calculate_integrity_score(
                clickbait_score, fear_score, loaded_language_score,
                emotion_score, urgency_score, false_balance_score,
                emotional_intensity, len(tactics_found)
            )
            
            integrity_level = self._get_integrity_level(integrity_score)
            
            # Generate findings
            findings = self._generate_findings(
                tactics_found, integrity_score, emotional_intensity
            )
            
            # Generate analysis
            analysis = self._generate_analysis(
                integrity_score, tactics_found, emotional_intensity
            )
            
            # Generate summary
            summary = self._generate_summary(integrity_score, len(tactics_found))
            
            # Build result
            result = {
                'service': self.service_name,
                'success': True,
                'available': True,
                'timestamp': time.time(),
                'analysis_complete': True,
                
                # Core scores
                'score': integrity_score,
                'integrity_score': integrity_score,
                'manipulation_score': 100 - integrity_score,  # Inverse
                'level': integrity_level,
                'integrity_level': integrity_level,
                
                # Detailed findings
                'findings': findings,
                'analysis': analysis,
                'summary': summary,
                
                # Tactics detected
                'techniques_found': len(tactics_found),
                'tactics_found': tactics_found,
                'techniques': tactics_found,  # Alias
                
                # Scores by type
                'clickbait_score': clickbait_score,
                'fear_mongering_score': fear_score,
                'loaded_language_score': loaded_language_score,
                'emotional_manipulation_score': emotion_score,
                'false_urgency_score': urgency_score,
                'emotional_intensity': emotional_intensity,
                'emotional_score': emotional_intensity,
                
                # Chart data
                'chart_data': {
                    'type': 'radar',
                    'data': {
                        'labels': ['Clickbait', 'Fear', 'Loaded Language', 'Emotion', 'Urgency', 'Balance'],
                        'datasets': [{
                            'label': 'Manipulation Scores',
                            'data': [clickbait_score, fear_score, loaded_language_score, 
                                   emotion_score, urgency_score, false_balance_score],
                            'backgroundColor': 'rgba(239, 68, 68, 0.2)',
                            'borderColor': '#ef4444'
                        }]
                    }
                },
                
                # Details
                'details': {
                    'tactics_count': len(tactics_found),
                    'integrity_score': integrity_score,
                    'emotional_intensity': emotional_intensity,
                    'high_severity_tactics': len([t for t in tactics_found if t.get('severity') == 'high']),
                    'medium_severity_tactics': len([t for t in tactics_found if t.get('severity') == 'medium']),
                    'low_severity_tactics': len([t for t in tactics_found if t.get('severity') == 'low'])
                },
                
                'metadata': {
                    'analysis_time': time.time() - start_time,
                    'text_length': len(text),
                    'title': title,
                    'version': '3.0.0',
                    'ai_enhanced': bool(self.openai_client and ai_tactics)
                }
            }
            
            logger.info(f"[ManipulationDetector v3.0] Complete: {integrity_score}/100 ({integrity_level}), {len(tactics_found)} tactics")
            return self.get_success_result(result)
            
        except Exception as e:
            logger.error(f"[ManipulationDetector v3.0] Error: {e}", exc_info=True)
            return self.get_error_result(f"Manipulation detection error: {str(e)}")
    
    def _detect_clickbait(self, title: str) -> Tuple[int, bool]:
        """Detect clickbait in title"""
        
        if not title:
            return 0, False
        
        score = 0
        title_lower = title.lower()
        
        # Check for clickbait phrases
        for pattern in self.clickbait_phrases:
            if re.search(pattern, title_lower):
                score += 30
        
        # Check for excessive punctuation
        if title.count('!') > 1:
            score += 20
        if title.count('?') > 1:
            score += 15
        
        # Check for all caps words
        caps_words = re.findall(r'\b[A-Z]{3,}\b', title)
        if len(caps_words) > 1:
            score += 20
        
        # Check for numbers in title (listicle indicator)
        if re.search(r'\b\d+\s+(?:ways|reasons|things|facts)', title_lower):
            score += 15
        
        detected = score > 30
        return min(score, 100), detected
    
    def _detect_fear_mongering(self, text: str) -> Tuple[int, List[str]]:
        """Detect fear-mongering language"""
        
        text_lower = text.lower()
        examples = []
        
        # Find sentences with fear words
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences[:50]:  # Check first 50 sentences
            sentence_lower = sentence.lower()
            fear_count = sum(1 for word in self.fear_words if word in sentence_lower)
            
            if fear_count >= 2:
                examples.append(sentence.strip()[:150])
        
        score = min(len(examples) * 20, 100)
        return score, examples[:3]  # Return top 3
    
    def _detect_loaded_language(self, text: str) -> Tuple[int, List[str]]:
        """Detect loaded/emotional language"""
        
        text_lower = text.lower()
        examples = []
        
        # Find sentences with loaded words
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences[:50]:
            sentence_lower = sentence.lower()
            
            for word in self.loaded_words:
                if word in sentence_lower:
                    examples.append(f"{word}: {sentence.strip()[:120]}")
                    break
        
        score = min(len(examples) * 10, 100)
        return score, examples[:5]  # Return top 5
    
    def _detect_emotional_manipulation(self, text: str) -> Tuple[int, List[str]]:
        """Detect emotional manipulation tactics"""
        
        examples = []
        
        # Check for emotional appeals
        for pattern in self.emotion_appeals:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Get surrounding context
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 100)
                context = text[start:end].strip()
                examples.append(context)
        
        score = min(len(examples) * 25, 100)
        return score, examples[:3]
    
    def _detect_false_urgency(self, text: str) -> Tuple[int, List[str]]:
        """Detect false urgency tactics"""
        
        examples = []
        
        for pattern in self.urgency_phrases:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Get surrounding context
                start = max(0, match.start() - 30)
                end = min(len(text), match.end() + 80)
                context = text[start:end].strip()
                examples.append(context)
        
        score = min(len(examples) * 15, 100)
        return score, examples[:3]
    
    def _detect_false_balance(self, text: str) -> int:
        """Detect false balance/equivalence"""
        
        score = 0
        text_lower = text.lower()
        
        # Look for "both sides" framing
        if re.search(r'both sides', text_lower):
            score += 30
        
        # Look for false equivalence patterns
        if re.search(r'on the one hand.*on the other', text_lower):
            score += 20
        
        # Look for "some say... others say" without context
        if re.search(r'some\s+(?:say|argue|believe).*others\s+(?:say|argue|believe)', text_lower):
            score += 25
        
        return min(score, 100)
    
    def _calculate_emotional_intensity(self, text: str) -> int:
        """Calculate overall emotional intensity of text"""
        
        # Count emotional indicators
        exclamations = text.count('!')
        questions = text.count('?')
        caps_words = len(re.findall(r'\b[A-Z]{3,}\b', text))
        
        # Count emotional words
        text_lower = text.lower()
        emotional_word_count = sum(text_lower.count(word) for word in self.fear_words + self.loaded_words)
        
        # Calculate intensity
        intensity = min((exclamations * 2) + (questions * 1) + (caps_words * 3) + (emotional_word_count * 2), 100)
        
        return intensity
    
    def _get_ai_manipulation_analysis(self, text: str, title: str) -> List[Dict[str, Any]]:
        """Use AI to detect manipulation tactics"""
        
        if not self.openai_client:
            return []
        
        try:
            prompt = f"""Analyze this article for manipulation tactics:

Title: {title}
Text: {text}

Identify manipulation tactics such as:
- Cherry-picking data
- Strawman arguments
- Ad hominem attacks
- False dichotomy
- Slippery slope
- Appeal to authority (without evidence)

List only CLEAR manipulation tactics found. For each, provide:
TACTIC: [name]
SEVERITY: [high/medium/low]
DESCRIPTION: [brief description]
EXAMPLE: [quote from text]

If no clear manipulation found, respond with: NONE"""
            
            response = self.openai_client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {"role": "system", "content": "You identify manipulation tactics in journalism."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=400
            )
            
            content = response.choices[0].message.content
            
            if 'NONE' in content:
                return []
            
            # Parse tactics
            tactics = []
            current_tactic = {}
            
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('TACTIC:'):
                    if current_tactic:
                        tactics.append(current_tactic)
                    current_tactic = {'name': line.replace('TACTIC:', '').strip()}
                elif line.startswith('SEVERITY:'):
                    current_tactic['severity'] = line.replace('SEVERITY:', '').strip().lower()
                elif line.startswith('DESCRIPTION:'):
                    current_tactic['description'] = line.replace('DESCRIPTION:', '').strip()
                elif line.startswith('EXAMPLE:'):
                    current_tactic['example'] = line.replace('EXAMPLE:', '').strip()[:150]
            
            if current_tactic:
                tactics.append(current_tactic)
            
            return tactics[:5]  # Limit to 5
            
        except Exception as e:
            logger.error(f"[ManipulationDetector v3.0] AI analysis failed: {e}")
            return []
    
    def _calculate_integrity_score(self, clickbait: int, fear: int, loaded: int,
                                   emotion: int, urgency: int, false_balance: int,
                                   emotional_intensity: int, tactics_count: int) -> int:
        """Calculate integrity score (inverse of manipulation)"""
        
        # Average of manipulation scores
        avg_manipulation = (clickbait + fear + loaded + emotion + urgency + false_balance) / 6
        
        # Penalty for emotional intensity
        intensity_penalty = emotional_intensity * 0.2
        
        # Penalty for number of tactics
        tactics_penalty = min(tactics_count * 5, 30)
        
        # Calculate integrity (inverse)
        integrity = 100 - avg_manipulation - intensity_penalty - tactics_penalty
        
        return int(max(0, min(100, integrity)))
    
    def _get_integrity_level(self, score: int) -> str:
        """Convert score to level"""
        if score >= 80: return 'High Integrity'
        elif score >= 60: return 'Moderate Integrity'
        elif score >= 40: return 'Low Integrity'
        else: return 'Very Low Integrity'
    
    def _generate_findings(self, tactics: List[Dict], integrity_score: int,
                          emotional_intensity: int) -> List[Dict[str, Any]]:
        """Generate detailed findings"""
        
        findings = []
        
        high_severity = [t for t in tactics if t.get('severity') == 'high']
        if high_severity:
            findings.append({
                'type': 'critical',
                'severity': 'high',
                'text': f'{len(high_severity)} high-severity manipulation tactic(s) detected',
                'explanation': f'Tactics like {high_severity[0]["name"]} can significantly distort information'
            })
        
        if integrity_score < 50:
            findings.append({
                'type': 'warning',
                'severity': 'high',
                'text': f'Low integrity score ({integrity_score}/100)',
                'explanation': 'Article uses multiple manipulation tactics that may distort the truth'
            })
        elif integrity_score >= 80:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': f'High integrity score ({integrity_score}/100)',
                'explanation': 'Article presents information straightforwardly without significant manipulation'
            })
        
        if emotional_intensity > 60:
            findings.append({
                'type': 'warning',
                'severity': 'medium',
                'text': f'High emotional intensity ({emotional_intensity}/100)',
                'explanation': 'Article uses emotional language that may cloud rational judgment'
            })
        
        if len(tactics) == 0:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': 'No significant manipulation tactics detected',
                'explanation': 'Article appears to present information fairly'
            })
        
        return findings
    
    def _generate_analysis(self, integrity_score: int, tactics: List[Dict],
                          emotional_intensity: int) -> Dict[str, str]:
        """Generate comprehensive analysis"""
        
        what_we_looked = (
            f"We analyzed the article for manipulation tactics including clickbait, fear-mongering, "
            f"loaded language, emotional manipulation, false urgency, and logical fallacies. "
            f"We examined both the headline and body content."
        )
        
        if len(tactics) == 0:
            what_we_found = "No significant manipulation tactics were detected. The article presents information straightforwardly."
        else:
            tactic_names = [t['name'] for t in tactics[:3]]
            what_we_found = f"Detected {len(tactics)} manipulation tactic(s): {', '.join(tactic_names)}. "
            what_we_found += f"Emotional intensity: {emotional_intensity}/100."
        
        if integrity_score >= 70:
            what_it_means = (
                f"This article has high integrity ({integrity_score}/100). "
                f"While some emotional language may be present, the article doesn't rely on manipulation "
                f"tactics to make its points. Information is presented fairly."
            )
        elif integrity_score >= 50:
            what_it_means = (
                f"This article has moderate integrity ({integrity_score}/100). "
                f"Some manipulation tactics are present that may influence how you perceive the information. "
                f"Read critically and consider multiple sources."
            )
        else:
            what_it_means = (
                f"This article has low integrity ({integrity_score}/100). "
                f"Multiple manipulation tactics are used that may significantly distort the truth. "
                f"Approach this content with skepticism and verify claims independently."
            )
        
        return {
            'what_we_looked': what_we_looked,
            'what_we_found': what_we_found,
            'what_it_means': what_it_means
        }
    
    def _generate_summary(self, integrity_score: int, tactics_count: int) -> str:
        """Generate conversational summary"""
        
        if tactics_count == 0:
            return f"Integrity score: {integrity_score}/100. No manipulation tactics detected. Article presents information straightforwardly."
        else:
            return f"Integrity score: {integrity_score}/100. Detected {tactics_count} manipulation tactic(s). Read critically."


logger.info("[ManipulationDetector v3.0] ✓ Fully implemented with _check_availability()")
