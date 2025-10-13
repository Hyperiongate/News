"""
Manipulation Detector - v4.0 EDUCATIONAL GUIDE
Date: October 13, 2025
Last Updated: October 13, 2025 - ALWAYS INTERESTING & VALUABLE

VISION:
✅ Always provide educational value about manipulation risks
✅ Teach users what manipulation looks like in THIS article type
✅ Context-aware guidance (breaking news vs opinion vs investigation)
✅ Help users think critically, not just give scores

CHANGES FROM v3.0:
✅ NEW: Article type awareness (different risks for different formats)
✅ NEW: Type-specific manipulation patterns
✅ NEW: Educational "How to Spot" guidance
✅ NEW: "Why it Works" psychological explanations
✅ ENHANCED: Meaningful analysis even when no tactics detected

THE PHILOSOPHY:
Not finding manipulation tactics is ALSO interesting - it tells us the article
uses straightforward presentation. Our job is to help users understand what
manipulation could look like in this format, and whether it's present.

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
    Educational manipulation guide - always valuable, always interesting
    v4.0 - Teaches users what manipulation means for THIS article type
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
                logger.info("[ManipulationGuide v4.0] OpenAI client initialized")
            except Exception as e:
                logger.warning(f"[ManipulationGuide v4.0] Failed to initialize OpenAI: {e}")
                self.openai_client = None
        
        self._initialize_patterns()
        
        logger.info(f"[ManipulationGuide v4.0] Initialized - Educational mode enabled")
    
    def _check_availability(self) -> bool:
        """Service is always available"""
        return True
    
    def _initialize_patterns(self):
        """Initialize manipulation pattern libraries"""
        
        self.fear_words = [
            'crisis', 'disaster', 'catastrophe', 'epidemic', 'pandemic',
            'threat', 'danger', 'risk', 'warning', 'alert', 'urgent',
            'terrifying', 'horrifying', 'shocking', 'devastating', 'deadly'
        ]
        
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
        
        self.loaded_words = [
            'slammed', 'blasted', 'destroyed', 'annihilated', 'crushed',
            'obliterated', 'demolished', 'eviscerated', 'shredded',
            'radical', 'extreme', 'outrageous', 'insane', 'crazy'
        ]
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide educational manipulation guidance
        Always valuable, regardless of tactics found
        """
        try:
            start_time = time.time()
            
            # Extract content
            text = data.get('text', '') or data.get('content', '')
            title = data.get('title', '')
            
            if not text:
                return self.get_error_result("No content provided for manipulation detection")
            
            source = data.get('source', 'Unknown')
            word_count = len(text.split())
            
            logger.info(f"[ManipulationGuide v4.0] Analyzing {word_count} words from {source}")
            
            # STEP 1: Detect article type (matches TransparencyAnalyzer)
            article_type, type_confidence = self._detect_article_type(title, text, word_count)
            logger.info(f"[ManipulationGuide] Detected type: {article_type} (confidence: {type_confidence}%)")
            
            # STEP 2: Get type-specific manipulation risks
            risk_profile = self._get_manipulation_risks(article_type)
            
            # STEP 3: Detect manipulation tactics
            tactics_found = self._detect_all_tactics(title, text, article_type)
            
            # STEP 4: Calculate integrity score (contextual)
            integrity_score = self._calculate_contextual_integrity(
                article_type, tactics_found, word_count, title, text
            )
            
            integrity_level = self._get_integrity_level(integrity_score)
            
            # STEP 5: Generate educational findings
            findings = self._generate_educational_findings(
                article_type, tactics_found, integrity_score, risk_profile
            )
            
            # STEP 6: Generate "How to Spot" guide
            how_to_spot = self._generate_how_to_spot(article_type, risk_profile)
            
            # STEP 7: Generate educational analysis
            analysis = self._generate_educational_analysis(
                article_type, integrity_score, tactics_found, word_count, risk_profile
            )
            
            # STEP 8: Generate conversational summary
            summary = self._generate_educational_summary(
                article_type, integrity_score, len(tactics_found)
            )
            
            # STEP 9: Manipulation lessons
            lessons = self._generate_manipulation_lessons(article_type, tactics_found)
            
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
                'manipulation_score': 100 - integrity_score,
                'level': integrity_level,
                'integrity_level': integrity_level,
                
                # Educational content
                'article_type': article_type,
                'type_confidence': type_confidence,
                'how_to_spot': how_to_spot,
                'manipulation_lessons': lessons,
                'risk_profile': risk_profile,
                
                # Findings
                'findings': findings,
                'analysis': analysis,
                'summary': summary,
                
                # Tactics
                'techniques_found': len(tactics_found),
                'tactics_found': tactics_found,
                'techniques': tactics_found,
                
                # Chart data
                'chart_data': self._generate_chart_data(tactics_found),
                
                'metadata': {
                    'analysis_time': time.time() - start_time,
                    'text_length': len(text),
                    'word_count': word_count,
                    'title': title,
                    'version': '4.0.0',
                    'educational_mode': True
                }
            }
            
            logger.info(f"[ManipulationGuide v4.0] Complete: {integrity_score}/100 ({article_type})")
            return self.get_success_result(result)
            
        except Exception as e:
            logger.error(f"[ManipulationGuide v4.0] Error: {e}", exc_info=True)
            return self.get_error_result(f"Manipulation analysis error: {str(e)}")
    
    def _detect_article_type(self, title: str, text: str, word_count: int) -> Tuple[str, int]:
        """Detect article type (matches TransparencyAnalyzer logic)"""
        
        title_lower = title.lower()
        text_lower = text.lower()
        
        # Breaking News
        if word_count < 300:
            breaking_indicators = ['breaking', 'just in', 'developing', 'update', 'report']
            breaking_score = sum(10 for indicator in breaking_indicators if indicator in title_lower or indicator in text_lower[:200])
            if breaking_score >= 20:
                return 'Breaking News', min(90, 60 + breaking_score)
        
        # Opinion/Editorial
        opinion_indicators = ['opinion', 'editorial', 'commentary', 'i believe', 'in my view', 'i think']
        opinion_score = sum(12 for indicator in opinion_indicators if indicator in title_lower or indicator in text_lower[:500])
        if opinion_score >= 24 or 'opinion' in title_lower:
            return 'Opinion/Editorial', min(90, 60 + opinion_score)
        
        # Analysis
        analysis_indicators = ['analysis', 'explained', 'what to know', 'context', 'why', 'how']
        analysis_score = sum(10 for indicator in analysis_indicators if indicator in title_lower)
        if analysis_score >= 20:
            return 'Analysis', min(85, 55 + analysis_score)
        
        # Investigation
        if word_count > 1500:
            investigation_indicators = ['investigation', 'documents show', 'obtained by', 'reviewed']
            investigation_score = sum(15 for indicator in investigation_indicators if indicator in text_lower)
            if investigation_score >= 30:
                return 'Investigation', min(95, 65 + investigation_score)
        
        return 'News Report', 70
    
    def _get_manipulation_risks(self, article_type: str) -> Dict[str, Any]:
        """
        Get manipulation risks specific to article type
        This is what makes the analysis educational
        """
        
        if article_type == 'Breaking News':
            return {
                'common_tactics': ['Sensational headlines', 'Unverified claims', 'Missing context', 'False urgency'],
                'why_vulnerable': 'Speed pressure can lead to sensationalism over accuracy',
                'what_to_watch': 'Dramatic language, definitive claims without verification, alarmist tone',
                'psychological_hooks': 'Fear of missing out (FOMO), urgency bias, novelty seeking',
                'typical_manipulation': 'Exaggerated headlines to drive clicks during breaking events',
                'how_to_resist': 'Wait for verification, check multiple sources, note what\'s still unknown',
                'red_flags': [
                    'Headline much more dramatic than content',
                    'Definitive claims about developing situations',
                    'No acknowledgment of uncertainty',
                    'Emotional language exceeds factual content'
                ]
            }
        
        elif article_type == 'Opinion/Editorial':
            return {
                'common_tactics': ['Cherry-picking data', 'Strawman arguments', 'Emotional appeals', 'False dichotomy'],
                'why_vulnerable': 'Opinions are persuasive by nature - line between advocacy and manipulation is thin',
                'what_to_watch': 'Selective evidence, misrepresenting opponents, appeals to fear/anger',
                'psychological_hooks': 'Confirmation bias, tribalism, emotional reasoning',
                'typical_manipulation': 'Presenting opinion as fact, ignoring counterevidence, demonizing opposition',
                'how_to_resist': 'Distinguish facts from opinions, seek opposing views, check cherry-picked stats',
                'red_flags': [
                    'All opposing views presented as extreme or stupid',
                    'Statistics without context',
                    'Emotional language replacing logical arguments',
                    'False choice: "either A or B" when more options exist'
                ]
            }
        
        elif article_type == 'Analysis':
            return {
                'common_tactics': ['Biased interpretation', 'Selective focus', 'Loaded language', 'False expertise'],
                'why_vulnerable': 'Analysis blends facts and interpretation - manipulation hides in the framing',
                'what_to_watch': 'One-sided interpretation, ignoring alternative explanations, presenting analysis as fact',
                'psychological_hooks': 'Authority bias, complexity exploitation, narrative fallacy',
                'typical_manipulation': 'Framing events to support predetermined conclusion, ignoring complexity',
                'how_to_resist': 'Read competing analyses, separate facts from interpretation, check analyst expertise',
                'red_flags': [
                    'Analysis presented as objective truth',
                    'No acknowledgment of alternative interpretations',
                    'Loaded language in supposedly neutral analysis',
                    'Expertise or credentials unclear'
                ]
            }
        
        elif article_type == 'Investigation':
            return {
                'common_tactics': ['Selective disclosure', 'Loaded framing', 'Guilt by association', 'Omission'],
                'why_vulnerable': 'Long-form allows building narrative - what\'s left out matters as much as what\'s in',
                'what_to_watch': 'One-sided narrative, missing context, documents presented without full story',
                'psychological_hooks': 'Narrative transportation, hindsight bias, pattern seeking',
                'typical_manipulation': 'Building case against target while omitting exonerating information',
                'how_to_resist': 'Consider what might be omitted, check if subjects fully responded, seek independent verification',
                'red_flags': [
                    'Story has clear villain but no complexity',
                    'Subject\'s full response not included',
                    'Documents cherry-picked to support narrative',
                    'No acknowledgment of conflicting evidence'
                ]
            }
        
        else:  # Standard News Report
            return {
                'common_tactics': ['False balance', 'Loaded language', 'Selective quotes', 'Buried context'],
                'why_vulnerable': 'Objectivity is hard - choices about what to emphasize can manipulate',
                'what_to_watch': 'Treating unequal things as equal, headline vs story mismatch, missing context',
                'psychological_hooks': 'Availability bias, framing effects, recency bias',
                'typical_manipulation': 'Headlines that mislead, false equivalence, burying key context',
                'how_to_resist': 'Read past headline, check if both sides truly equivalent, look for buried context',
                'red_flags': [
                    'Headline contradicts or exaggerates story',
                    'False balance (presenting fringe view as equally valid)',
                    'Key context buried deep in article',
                    'Quotes taken out of context'
                ]
            }
    
    def _detect_all_tactics(self, title: str, text: str, article_type: str) -> List[Dict[str, Any]]:
        """
        Detect manipulation tactics with context awareness
        """
        
        tactics = []
        
        # Headline analysis
        clickbait_detected = self._check_clickbait(title)
        if clickbait_detected:
            tactics.append({
                'name': 'Clickbait Headline',
                'severity': 'medium',
                'description': 'Headline uses attention-grabbing techniques rather than informative approach',
                'example': title,
                'why_it_works': 'Exploits curiosity gap - promises information to get clicks',
                'how_to_spot': 'Overpromises, uses "you won\'t believe" phrases, creates artificial mystery'
            })
        
        # Fear-mongering (more acceptable in breaking news about actual dangers)
        fear_count = sum(1 for word in self.fear_words if word in text.lower())
        if fear_count >= 3:
            # Context matters
            severity = 'low' if article_type == 'Breaking News' else 'high'
            tactics.append({
                'name': 'Fear-Based Language',
                'severity': severity,
                'description': f'Uses {fear_count} fear-inducing words to trigger emotional response',
                'example': ', '.join([w for w in self.fear_words if w in text.lower()][:3]),
                'why_it_works': 'Fear bypasses rational thinking, makes content feel urgent and important',
                'how_to_spot': 'Count scary words - are they necessary to report facts?'
            })
        
        # Loaded language
        loaded_count = sum(1 for word in self.loaded_words if word in text.lower())
        if loaded_count >= 2:
            tactics.append({
                'name': 'Loaded Language',
                'severity': 'medium',
                'description': 'Uses emotionally charged words that editorialize',
                'example': ', '.join([w for w in self.loaded_words if w in text.lower()][:2]),
                'why_it_works': 'Emotional words shape perception of events before you process facts',
                'how_to_spot': 'Notice inflammatory verbs - "said" vs "slammed", "disagreed" vs "destroyed"'
            })
        
        # False urgency in non-breaking news
        if article_type != 'Breaking News':
            urgency_phrases = ['act now', 'before it\'s too late', 'urgent', 'don\'t wait']
            urgency_found = [phrase for phrase in urgency_phrases if phrase in text.lower()]
            if urgency_found:
                tactics.append({
                    'name': 'False Urgency',
                    'severity': 'low',
                    'description': 'Creates artificial sense of urgency',
                    'example': urgency_found[0],
                    'why_it_works': 'Urgency prompts action without reflection',
                    'how_to_spot': 'Ask: is this really time-sensitive or just framed that way?'
                })
        
        # Opinion presented as fact (critical in opinion pieces)
        if article_type == 'Opinion/Editorial':
            fact_markers = ['clearly', 'obviously', 'undeniably', 'unquestionably']
            fact_count = sum(1 for marker in fact_markers if marker in text.lower())
            if fact_count >= 2:
                tactics.append({
                    'name': 'Opinion as Fact',
                    'severity': 'high',
                    'description': 'Presents opinions as objective truths',
                    'example': 'Uses words like "clearly" and "obviously" to present debatable points as facts',
                    'why_it_works': 'Bypasses critical thinking by asserting rather than arguing',
                    'how_to_spot': 'Watch for "clearly", "obviously" - often signals opinion being sold as fact'
                })
        
        return tactics
    
    def _check_clickbait(self, title: str) -> bool:
        """Check if headline is clickbait"""
        if not title:
            return False
        
        title_lower = title.lower()
        
        # Check patterns
        for pattern in self.clickbait_phrases:
            if re.search(pattern, title_lower):
                return True
        
        # Check excessive punctuation
        if title.count('!') > 1 or title.count('?') > 1:
            return True
        
        # Check all caps words
        caps_words = re.findall(r'\b[A-Z]{3,}\b', title)
        if len(caps_words) > 1:
            return True
        
        return False
    
    def _calculate_contextual_integrity(self, article_type: str, tactics: List[Dict],
                                       word_count: int, title: str, text: str) -> int:
        """
        Calculate integrity score with context awareness
        """
        
        base_score = 85  # Start high - most journalism is not manipulative
        
        # Deduct for tactics found
        for tactic in tactics:
            severity = tactic.get('severity', 'medium')
            if severity == 'high':
                base_score -= 20
            elif severity == 'medium':
                base_score -= 12
            else:
                base_score -= 7
        
        # Context adjustments
        if article_type == 'Breaking News':
            # Be lenient - some dramatic language acceptable in breaking news
            base_score += 5
        elif article_type == 'Opinion/Editorial':
            # Expect persuasive language - that's the format
            if len(tactics) <= 2:
                base_score += 5
        
        # Short articles with no tactics - likely straightforward
        if word_count < 300 and len(tactics) == 0:
            base_score = min(92, base_score + 7)
        
        return int(max(0, min(100, base_score)))
    
    def _generate_educational_findings(self, article_type: str, tactics: List[Dict],
                                      integrity_score: int, risk_profile: Dict) -> List[Dict[str, Any]]:
        """
        Generate findings that TEACH about manipulation
        """
        
        findings = []
        
        # Context-setting finding
        findings.append({
            'type': 'info',
            'severity': 'info',
            'icon': '📋',
            'text': f'Article Type: {article_type}',
            'explanation': f"{risk_profile['why_vulnerable']}"
        })
        
        # If tactics found - explain them
        if tactics:
            for tactic in tactics[:3]:  # Show top 3
                findings.append({
                    'type': 'warning',
                    'severity': tactic['severity'],
                    'icon': '⚠️',
                    'text': f"{tactic['name']} detected",
                    'explanation': f"{tactic['description']} - {tactic['why_it_works']}"
                })
        else:
            # NO tactics found - still educational!
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'icon': '✓',
                'text': 'Straightforward presentation',
                'explanation': f'No major manipulation tactics detected. Article presents information directly without obvious emotional manipulation or clickbait techniques.'
            })
        
        # Educational finding about what to watch for
        findings.append({
            'type': 'education',
            'severity': 'info',
            'icon': '💡',
            'text': f'Key manipulation risks for {article_type.lower()}s',
            'explanation': risk_profile['typical_manipulation']
        })
        
        # How to be a critical reader
        findings.append({
            'type': 'education',
            'severity': 'info',
            'icon': '🧠',
            'text': 'Think critically',
            'explanation': risk_profile['how_to_resist']
        })
        
        return findings
    
    def _generate_how_to_spot(self, article_type: str, risk_profile: Dict) -> List[str]:
        """
        Generate specific guidance: "Here's how to spot manipulation in this format"
        """
        
        guidance = [
            f"📋 **Article Type**: {article_type}",
            f"🎯 **Manipulation Risk**: {risk_profile['why_vulnerable']}",
            "",
            "**How to Spot Manipulation:**"
        ]
        
        # Add type-specific guidance
        guidance.extend([
            f"• {risk_profile['what_to_watch']}",
            "",
            "**Common Tactics in This Format:**"
        ])
        
        for i, tactic in enumerate(risk_profile['common_tactics'], 1):
            guidance.append(f"{i}. {tactic}")
        
        guidance.extend([
            "",
            "**Red Flags to Watch For:**"
        ])
        
        for flag in risk_profile['red_flags']:
            guidance.append(f"• {flag}")
        
        guidance.extend([
            "",
            "**How Manipulation Works:**",
            f"• {risk_profile['psychological_hooks']}"
        ])
        
        return guidance
    
    def _generate_manipulation_lessons(self, article_type: str, tactics: List[Dict]) -> List[str]:
        """
        Generate key lessons users can apply
        """
        
        if len(tactics) == 0:
            return [
                f"Not finding manipulation is also a finding - this {article_type.lower()} presents information straightforwardly",
                "Always stay alert: absence of obvious tactics doesn't mean perfect objectivity",
                "Consider what's emphasized vs what's downplayed - framing can be subtle manipulation"
            ]
        else:
            lessons = [
                "Manipulation often works by triggering emotions before you process facts",
                "The most effective manipulation doesn't feel like manipulation - stay skeptical",
            ]
            
            # Add specific lesson based on tactics found
            if any(t['name'] == 'Clickbait Headline' for t in tactics):
                lessons.append("Clickbait headlines manipulate by creating curiosity gaps - read the full article")
            if any(t['name'] == 'Fear-Based Language' for t in tactics):
                lessons.append("Fear-based language triggers fight-or-flight response - pause to think rationally")
            if any(t['name'] == 'Opinion as Fact' for t in tactics):
                lessons.append("Words like 'clearly' and 'obviously' often signal opinion being sold as fact")
            
            return lessons
    
    def _generate_educational_analysis(self, article_type: str, integrity_score: int,
                                      tactics: List[Dict], word_count: int,
                                      risk_profile: Dict) -> Dict[str, str]:
        """
        Generate analysis that TEACHES about manipulation
        """
        
        what_we_looked = (
            f"We analyzed this {article_type.lower()} ({word_count} words) for manipulation tactics. "
            f"For this format, common manipulation includes: {', '.join(risk_profile['common_tactics'][:3])}. "
            f"We checked for emotional manipulation, clickbait, loaded language, and logical fallacies."
        )
        
        if len(tactics) == 0:
            what_we_found = (
                f"No significant manipulation tactics detected. The article presents information directly. "
                f"For a {article_type.lower()}, this means: {risk_profile['typical_manipulation'].lower()} is not evident. "
                f"However, all journalism involves choices about framing and emphasis."
            )
        else:
            tactic_names = [t['name'] for t in tactics[:3]]
            what_we_found = (
                f"Found {len(tactics)} manipulation tactic(s): {', '.join(tactic_names)}. "
                f"These tactics work by: {risk_profile['psychological_hooks'].lower()}. "
                f"In {article_type.lower()}s, {risk_profile['why_vulnerable'].lower()}"
            )
        
        if integrity_score >= 80:
            what_it_means = (
                f"Integrity score: {integrity_score}/100. "
                f"This {article_type.lower()} maintains high integrity with straightforward presentation. "
                f"Still, remain alert for: {risk_profile['what_to_watch'].lower()}"
            )
        elif integrity_score >= 60:
            what_it_means = (
                f"Integrity score: {integrity_score}/100. "
                f"This {article_type.lower()} has moderate integrity with some manipulative elements. "
                f"To resist manipulation: {risk_profile['how_to_resist'].lower()}"
            )
        else:
            what_it_means = (
                f"Integrity score: {integrity_score}/100. "
                f"This {article_type.lower()} uses significant manipulation tactics. "
                f"Critical approach needed: {risk_profile['how_to_resist'].lower()}"
