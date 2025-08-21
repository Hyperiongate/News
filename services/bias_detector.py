"""
Bias Detector Service - AI ENHANCED VERSION
Advanced multi-dimensional bias detection with rich explanations, visualizations, and AI insights
"""

import re
import logging
import time
from typing import Dict, List, Any, Tuple, Optional
from collections import Counter
import statistics

from config import Config
from services.base_analyzer import BaseAnalyzer
from services.ai_enhancement_mixin import AIEnhancementMixin

logger = logging.getLogger(__name__)


class BiasDetector(BaseAnalyzer, AIEnhancementMixin):
    """
    Advanced bias detection analyzing multiple dimensions including political,
    corporate, sensational, nationalistic, and establishment bias WITH AI ENHANCEMENT
    """
    
    def __init__(self):
        """Initialize bias detector with comprehensive pattern database and AI"""
        super().__init__('bias_detector')
        AIEnhancementMixin.__init__(self)
        
        # Initialize all bias patterns and indicators
        self._initialize_bias_patterns()
        
        logger.info(f"BiasDetector initialized with multi-dimensional analysis and AI enhancement: {self._ai_available}")
    
    def _check_availability(self) -> bool:
        """Service is always available"""
        return True
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive bias analysis WITH AI ENHANCEMENT
        
        Expected input:
            - text: Article text to analyze (required)
            - title: Article title (optional)
            - domain: Source domain (optional)
            - author: Author name (optional)
        """
        try:
            start_time = time.time()
            
            text = data.get('text', '')
            if not text:
                return self.get_error_result("No text provided for bias analysis")
            
            # Include title in analysis if provided
            title = data.get('title', '')
            full_text = f"{title}\n\n{text}" if title else text
            
            # Perform multi-dimensional analysis
            dimensions = self._analyze_all_dimensions(full_text)
            patterns = self._detect_bias_patterns(full_text)
            loaded_phrases = self._extract_loaded_phrases(full_text)
            manipulation_tactics = self._detect_manipulation_tactics(full_text, patterns)
            
            # Calculate scores
            objectivity_score = self._calculate_objectivity_score(dimensions, patterns, loaded_phrases)
            opinion_percentage = self._calculate_opinion_percentage(full_text)
            emotional_score = self._calculate_emotional_score(full_text)
            confidence = self._calculate_confidence(full_text, patterns)
            
            # Generate bias score and level
            bias_score = self._calculate_overall_bias_score(dimensions, objectivity_score)
            bias_level = self._get_bias_level(bias_score)
            
            # Additional analysis
            framing_analysis = self._analyze_framing(full_text)
            source_analysis = self._analyze_source_diversity(full_text)
            
            # Generate findings and explanations
            findings = self._generate_findings(dimensions, patterns, loaded_phrases, manipulation_tactics)
            summary = self._generate_summary(dimensions, objectivity_score, bias_score)
            
            # Create visualization data
            visualization = self._create_visualization_data(dimensions)
            
            # AI ENHANCEMENT - Add deeper bias insights
            if self._ai_available and text:
                logger.info("Enhancing bias analysis with AI")
                
                # Get AI bias pattern detection
                ai_bias_patterns = self._ai_detect_bias_patterns(
                    text=full_text[:2000],  # Limit text for API
                    initial_findings={
                        'political_label': dimensions['political']['label'],
                        'sensationalism': dimensions['sensational']['label'],
                        'loaded_phrases': loaded_phrases[:5],  # Top 5 phrases
                        'bias_score': bias_score
                    }
                )
                
                if ai_bias_patterns:
                    # Add AI-detected subtle biases
                    if ai_bias_patterns.get('subtle_biases'):
                        for bias in ai_bias_patterns['subtle_biases']:
                            patterns.append({
                                'type': 'ai_subtle_bias',
                                'description': f'AI detected: {bias}',
                                'severity': 'medium',
                                'impact': 'May influence reader perception subtly',
                                'source': 'ai'
                            })
                    
                    # Add AI framing issues to findings
                    if ai_bias_patterns.get('framing_issues'):
                        for issue in ai_bias_patterns['framing_issues'][:2]:
                            findings.append({
                                'type': 'ai_framing_bias',
                                'text': f'AI: {issue}',
                                'severity': 'medium',
                                'explanation': 'Subtle framing bias detected by AI analysis'
                            })
                    
                    # Update summary with AI insights
                    if ai_bias_patterns.get('severity_assessment') in ['high', 'severe']:
                        summary += " AI analysis reveals additional subtle bias patterns that may not be immediately apparent."
                        # Adjust scores
                        bias_score = min(100, bias_score + 10)
                        objectivity_score = max(0, objectivity_score - 10)
                    
                    # Add missing perspectives if detected
                    if ai_bias_patterns.get('missing_perspectives'):
                        source_analysis['ai_missing_perspectives'] = ai_bias_patterns['missing_perspectives']
            
            # Build final result
            result = {
                'service': self.service_name,
                'success': True,
                'data': {
                    'score': bias_score,
                    'level': bias_level,
                    'findings': findings[:5],  # Top 5 findings
                    'summary': summary,
                    'bias_score': bias_score,
                    'objectivity_score': objectivity_score,
                    'opinion_percentage': opinion_percentage,
                    'emotional_score': emotional_score,
                    'confidence': confidence,
                    'dimensions': dimensions,
                    'patterns': patterns[:10],  # Top 10 patterns
                    'loaded_phrases': loaded_phrases[:10],  # Top 10
                    'manipulation_tactics': manipulation_tactics,
                    'framing_analysis': framing_analysis,
                    'source_analysis': source_analysis,
                    'visualization': visualization,
                    'detailed_analysis': {
                        'political_lean': dimensions['political']['score'] * 100,
                        'political_label': dimensions['political']['label'],
                        'corporate_stance': dimensions['corporate']['label'],
                        'sensationalism': dimensions['sensational']['label'],
                        'establishment_trust': dimensions['establishment']['label'],
                        'national_focus': dimensions['nationalistic']['label']
                    }
                },
                'metadata': {
                    'processing_time': time.time() - start_time,
                    'text_length': len(text.split()),
                    'title_analyzed': bool(title),
                    'patterns_found': len(patterns),
                    'loaded_phrases_found': len(loaded_phrases),
                    'ai_enhanced': self._ai_available,
                    'ai_patterns_found': len([p for p in patterns if p.get('source') == 'ai'])
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Bias analysis failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _initialize_bias_patterns(self):
        """Initialize comprehensive bias detection patterns"""
        
        # Political indicators with weights
        self.left_indicators = {
            'progressive': 3, 'liberal': 3, 'democrat': 2, 'left-wing': 3,
            'socialist': 3, 'equity': 2, 'social justice': 3, 'inequality': 2,
            'climate change': 2, 'gun control': 2, 'universal healthcare': 3,
            'wealth redistribution': 3, 'corporate greed': 3, 'workers rights': 2,
            'systemic racism': 3, 'diversity': 1, 'inclusion': 1, 'regulation': 2,
            'public option': 3, 'green new deal': 3, 'medicare for all': 3
        }
        
        self.right_indicators = {
            'conservative': 3, 'republican': 2, 'right-wing': 3, 'traditional': 2,
            'libertarian': 2, 'patriot': 2, 'free market': 3, 'deregulation': 3,
            'individual liberty': 2, 'second amendment': 3, 'pro-life': 3,
            'border security': 3, 'law and order': 2, 'family values': 2,
            'limited government': 3, 'personal responsibility': 2, 'states rights': 2,
            'religious freedom': 2, 'constitutional': 2, 'free enterprise': 3
        }
        
        # Corporate bias indicators
        self.pro_corporate = {
            'innovation': 1, 'job creators': 3, 'economic growth': 2,
            'business friendly': 3, 'entrepreneurship': 2, 'free enterprise': 3,
            'competitive advantage': 2, 'shareholder value': 3, 'efficiency': 1,
            'market leader': 2, 'industry leader': 2, 'disruption': 1,
            'startup': 1, 'investment': 1, 'prosperity': 2
        }
        
        self.anti_corporate = {
            'corporate greed': 3, 'monopoly': 3, 'exploitation': 3,
            'tax avoidance': 3, 'income inequality': 2, 'worker exploitation': 3,
            'excessive profits': 3, 'corporate welfare': 3, 'big business': 2,
            'wealth gap': 2, 'unfair practices': 2, 'price gouging': 3,
            'wage theft': 3, 'union busting': 3, 'offshore': 2
        }
        
        # Sensational indicators
        self.sensational_indicators = {
            'shocking': 3, 'bombshell': 3, 'explosive': 3, 'devastating': 3,
            'breaking': 2, 'urgent': 2, 'exclusive': 2, 'revealed': 2,
            'scandal': 3, 'crisis': 2, 'catastrophe': 3, 'disaster': 2,
            'unbelievable': 3, 'incredible': 2, 'mind-blowing': 3,
            'game-changing': 3, 'revolutionary': 2, 'stunning': 2,
            'jaw-dropping': 3, 'earth-shattering': 3, 'unprecedented': 2
        }
        
        # Nationalistic vs internationalist
        self.nationalistic_indicators = {
            'america first': 3, 'national interest': 2, 'sovereignty': 2,
            'patriotic': 2, 'our country': 2, 'homeland': 2, 'national security': 2,
            'protect our borders': 3, 'foreign threat': 3, 'defend america': 3,
            'american values': 2, 'national pride': 2, 'domestic': 1
        }
        
        self.internationalist_indicators = {
            'global cooperation': 3, 'international community': 2, 'united nations': 2,
            'global citizens': 3, 'world peace': 2, 'international law': 2,
            'diplomatic solution': 2, 'multilateral': 3, 'global partnership': 3,
            'international order': 2, 'global governance': 3, 'transnational': 2
        }
        
        # Establishment indicators
        self.pro_establishment = {
            'respected institutions': 3, 'established order': 3, 'mainstream': 2,
            'expert consensus': 3, 'institutional': 2, 'authorities say': 2,
            'official sources': 2, 'government officials': 2, 'traditional media': 2,
            'scientific consensus': 3, 'peer reviewed': 3, 'leading experts': 2
        }
        
        self.anti_establishment = {
            'deep state': 3, 'mainstream media lies': 3, 'corrupt system': 3,
            'establishment': -2, 'elite agenda': 3, 'wake up': 2, 'they dont want': 3,
            'hidden truth': 3, 'question everything': 2, 'alternative facts': 2,
            'conspiracy': 3, 'cover up': 3, 'suppressed': 2
        }
        
        # Loaded phrase patterns with categories and severity
        self.loaded_patterns = [
            # Political loaded terms
            (r'\b(radical|extreme|far-left|far-right|extremist)\b', 'political', 'high'),
            (r'\b(socialist agenda|right-wing conspiracy|left-wing mob)\b', 'political', 'high'),
            (r'\b(fascist|communist|marxist|nazi)\b', 'political', 'high'),
            
            # Emotional manipulation
            (r'\b(destroy|devastate|annihilate|obliterate)\b', 'hyperbolic', 'medium'),
            (r'\b(save|rescue|protect|defend)\s+(?:our|the)\s+\w+', 'savior_language', 'medium'),
            (r'\b(under attack|under siege|war on)\b', 'conflict_framing', 'high'),
            
            # Absolute language
            (r'\b(always|never|everyone|no one|all|none)\b', 'absolute', 'low'),
            (r'\b(undeniable|indisputable|unquestionable|irrefutable)\b', 'absolute', 'medium'),
            (r'\b(complete|total|utter|absolute)\s+(failure|success|disaster)', 'absolute', 'medium'),
            
            # Assumption language
            (r'\b(obviously|clearly|undeniably|of course)\b', 'assumption', 'low'),
            (r'\b(everyone knows|it\'s well known|nobody disputes)\b', 'assumption', 'medium'),
            (r'\b(common sense|self-evident|goes without saying)\b', 'assumption', 'low'),
            
            # Us vs Them language
            (r'\b(they|them|those people|the other side)\b', 'divisive', 'medium'),
            (r'\b(our values|real americans|true patriots)\b', 'divisive', 'high'),
            (r'\b(us versus them|our way of life)\b', 'divisive', 'high'),
            
            # Fear-mongering
            (r'\b(threat to|attack on|assault on)\s+\w+', 'fear', 'high'),
            (r'\b(invasion|infestation|plague|epidemic)\b', 'fear', 'high'),
            (r'\b(existential threat|grave danger|imminent)\b', 'fear', 'high'),
        ]
    
    def _analyze_all_dimensions(self, text: str) -> Dict[str, Dict[str, Any]]:
        """Analyze all bias dimensions"""
        return {
            'political': self._analyze_political_dimension(text),
            'corporate': self._analyze_corporate_dimension(text),
            'sensational': self._analyze_sensational_dimension(text),
            'nationalistic': self._analyze_nationalistic_dimension(text),
            'establishment': self._analyze_establishment_dimension(text)
        }
    
    def _analyze_political_dimension(self, text: str) -> Dict[str, Any]:
        """Analyze political bias with detailed indicators"""
        text_lower = text.lower()
        
        # Count indicators
        left_found = []
        right_found = []
        
        for term, weight in self.left_indicators.items():
            count = len(re.findall(rf'\b{term}\b', text_lower))
            if count > 0:
                left_found.extend([term] * count)
        
        for term, weight in self.right_indicators.items():
            count = len(re.findall(rf'\b{term}\b', text_lower))
            if count > 0:
                right_found.extend([term] * count)
        
        # Calculate weighted scores
        left_score = sum(self.left_indicators.get(term, 1) for term in left_found)
        right_score = sum(self.right_indicators.get(term, 1) for term in right_found)
        
        # Normalize score
        total_score = left_score + right_score
        if total_score == 0:
            score = 0
            explanation = "No significant political indicators detected"
        else:
            # Scale to -1 to 1 (negative = left, positive = right)
            score = (right_score - left_score) / max(total_score, 20)
            score = max(-1, min(1, score))
            
            # Generate explanation
            if left_found and right_found:
                explanation = f"Mixed political language detected"
            elif left_found:
                top_terms = Counter(left_found).most_common(3)
                explanation = f"Left-leaning language: {', '.join([t[0] for t in top_terms])}"
            else:
                top_terms = Counter(right_found).most_common(3)
                explanation = f"Right-leaning language: {', '.join([t[0] for t in top_terms])}"
        
        # Determine label
        if score <= -0.6:
            label = 'Strong Left'
        elif score <= -0.2:
            label = 'Lean Left'
        elif score >= 0.6:
            label = 'Strong Right'
        elif score >= 0.2:
            label = 'Lean Right'
        else:
            label = 'Center'
        
        return {
            'score': score,
            'label': label,
            'confidence': min(100, int(abs(score) * 100 * 1.2)),
            'explanation': explanation,
            'indicators': {
                'left': list(set(left_found))[:5],
                'right': list(set(right_found))[:5]
            }
        }
    
    def _analyze_corporate_dimension(self, text: str) -> Dict[str, Any]:
        """Analyze corporate/business bias"""
        text_lower = text.lower()
        
        # Count indicators
        pro_found = []
        anti_found = []
        
        for term in self.pro_corporate:
            if term in text_lower:
                pro_found.append(term)
        
        for term in self.anti_corporate:
            if term in text_lower:
                anti_found.append(term)
        
        # Calculate scores
        pro_score = sum(self.pro_corporate[term] for term in pro_found)
        anti_score = sum(self.anti_corporate[term] for term in anti_found)
        
        total_score = pro_score + anti_score
        if total_score == 0:
            score = 0
            explanation = "Neutral stance on corporate issues"
        else:
            score = (pro_score - anti_score) / max(total_score, 15)
            score = max(-1, min(1, score))
            
            if pro_found and anti_found:
                explanation = "Mixed corporate coverage"
            elif pro_found:
                explanation = f"Pro-business: {', '.join(pro_found[:3])}"
            else:
                explanation = f"Corporate criticism: {', '.join(anti_found[:3])}"
        
        # Label
        if score >= 0.6:
            label = 'Strongly Pro-Corporate'
        elif score >= 0.2:
            label = 'Slightly Pro-Corporate'
        elif score <= -0.6:
            label = 'Strongly Anti-Corporate'
        elif score <= -0.2:
            label = 'Slightly Anti-Corporate'
        else:
            label = 'Neutral'
        
        return {
            'score': score,
            'label': label,
            'confidence': min(100, int(abs(score) * 100)),
            'explanation': explanation
        }
    
    def _analyze_sensational_dimension(self, text: str) -> Dict[str, Any]:
        """Analyze sensationalism and emotional manipulation"""
        text_lower = text.lower()
        
        # Count sensational words
        sensational_found = []
        for term in self.sensational_indicators:
            if term in text_lower:
                sensational_found.append(term)
        
        sensational_score = sum(self.sensational_indicators[term] for term in sensational_found)
        
        # Check formatting issues
        exclamation_count = text.count('!')
        question_count = text.count('?')
        caps_words = len(re.findall(r'\b[A-Z]{3,}\b', text))
        
        # Add to score
        sensational_score += min(exclamation_count * 2, 10)
        sensational_score += min(caps_words * 3, 15)
        
        # Normalize to 0-1
        score = min(1, sensational_score / 30)
        
        # Explanation
        issues = []
        if sensational_found:
            issues.append(f"sensational words: {', '.join(sensational_found[:3])}")
        if exclamation_count > 2:
            issues.append(f"{exclamation_count} exclamation marks")
        if caps_words > 3:
            issues.append(f"{caps_words} CAPS words")
        
        explanation = '; '.join(issues) if issues else "Professional tone maintained"
        
        # Label
        if score >= 0.7:
            label = 'Highly Sensational'
        elif score >= 0.4:
            label = 'Moderately Sensational'
        elif score >= 0.2:
            label = 'Slightly Sensational'
        else:
            label = 'Measured'
        
        return {
            'score': score,
            'label': label,
            'confidence': min(100, int(score * 120)),
            'explanation': explanation
        }
    
    def _analyze_nationalistic_dimension(self, text: str) -> Dict[str, Any]:
        """Analyze nationalistic vs internationalist perspective"""
        text_lower = text.lower()
        
        nat_found = [t for t in self.nationalistic_indicators if t in text_lower]
        int_found = [t for t in self.internationalist_indicators if t in text_lower]
        
        nat_score = sum(self.nationalistic_indicators[t] for t in nat_found)
        int_score = sum(self.internationalist_indicators[t] for t in int_found)
        
        total = nat_score + int_score
        if total == 0:
            score = 0
            explanation = "Balanced national/international perspective"
        else:
            score = (nat_score - int_score) / max(total, 15)
            score = max(-1, min(1, score))
            
            if score > 0:
                explanation = f"Nationalistic focus: {', '.join(nat_found[:3])}"
            else:
                explanation = f"International focus: {', '.join(int_found[:3])}"
        
        # Label
        if score >= 0.6:
            label = 'Strongly Nationalistic'
        elif score >= 0.2:
            label = 'Moderately Nationalistic'
        elif score <= -0.6:
            label = 'Strongly Internationalist'
        elif score <= -0.2:
            label = 'Moderately Internationalist'
        else:
            label = 'Balanced'
        
        return {
            'score': score,
            'label': label,
            'confidence': min(100, int(abs(score) * 100)),
            'explanation': explanation
        }
    
    def _analyze_establishment_dimension(self, text: str) -> Dict[str, Any]:
        """Analyze trust/skepticism toward institutions"""
        text_lower = text.lower()
        
        pro_found = [t for t in self.pro_establishment if t in text_lower]
        anti_found = [t for t in self.anti_establishment if t in text_lower]
        
        pro_score = sum(self.pro_establishment[t] for t in pro_found)
        anti_score = sum(abs(self.anti_establishment[t]) for t in anti_found)
        
        total = pro_score + anti_score
        if total == 0:
            score = 0
            explanation = "Neutral stance toward institutions"
        else:
            score = (pro_score - anti_score) / max(total, 15)
            score = max(-1, min(1, score))
            
            if score > 0:
                explanation = f"Trusts institutions: {', '.join(pro_found[:3])}"
            else:
                explanation = f"Skeptical: {', '.join(anti_found[:3])}"
        
        # Label
        if score >= 0.6:
            label = 'Strongly Pro-Establishment'
        elif score >= 0.2:
            label = 'Moderately Pro-Establishment'
        elif score <= -0.6:
            label = 'Strongly Anti-Establishment'
        elif score <= -0.2:
            label = 'Moderately Anti-Establishment'
        else:
            label = 'Neutral'
        
        return {
            'score': score,
            'label': label,
            'confidence': min(100, int(abs(score) * 100)),
            'explanation': explanation
        }
    
    def _detect_bias_patterns(self, text: str) -> List[Dict[str, Any]]:
        """Detect specific bias patterns"""
        patterns = []
        
        # Cherry-picking
        if re.search(r'(study shows|research finds|data indicates)', text, re.I):
            if not re.search(r'(however|but|although|limitation|methodology)', text, re.I):
                patterns.append({
                    'type': 'cherry_picking',
                    'description': 'Cites research without acknowledging limitations',
                    'severity': 'medium',
                    'impact': 'May present incomplete picture'
                })
        
        # False balance
        if re.search(r'(both sides|on one hand.*on the other|equally valid)', text, re.I):
            patterns.append({
                'type': 'false_balance',
                'description': 'Presents unequal viewpoints as equivalent',
                'severity': 'low',
                'impact': 'Can legitimize fringe views'
            })
        
        # Loaded questions
        if re.search(r'\?.*\b(really|actually|truly)\b', text[:200], re.I):
            patterns.append({
                'type': 'loaded_question',
                'description': 'Uses questions that imply specific answers',
                'severity': 'medium',
                'impact': 'Guides reader to predetermined conclusion'
            })
        
        # Anecdotal evidence
        if re.search(r'(one (man|woman)|a friend|someone I know)', text, re.I):
            patterns.append({
                'type': 'anecdotal_evidence',
                'description': 'Relies on personal stories over data',
                'severity': 'low',
                'impact': 'May not represent broader trends'
            })
        
        # Strawman
        if re.search(r'(claim that|say that).*?(ridiculous|absurd|crazy)', text, re.I):
            patterns.append({
                'type': 'strawman',
                'description': 'Misrepresents opposing views',
                'severity': 'high',
                'impact': 'Prevents fair consideration of alternatives'
            })
        
        # Appeal to fear
        if len(re.findall(r'\b(threat|danger|risk|attack)\b', text, re.I)) > 3:
            patterns.append({
                'type': 'fear_appeal',
                'description': 'Excessive use of fear-based language',
                'severity': 'high',
                'impact': 'Manipulates through emotional response'
            })
        
        return patterns
    
    def _extract_loaded_phrases(self, text: str) -> List[Dict[str, Any]]:
        """Extract and categorize loaded phrases"""
        phrases = []
        seen = set()
        
        for pattern, category, severity in self.loaded_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                phrase = match.group()
                phrase_lower = phrase.lower()
                
                if phrase_lower in seen:
                    continue
                seen.add(phrase_lower)
                
                # Get context
                start = max(0, match.start() - 40)
                end = min(len(text), match.end() + 40)
                context = text[start:end].strip()
                
                if start > 0:
                    context = '...' + context
                if end < len(text):
                    context = context + '...'
                
                phrases.append({
                    'text': phrase,
                    'type': category,
                    'severity': severity,
                    'context': context,
                    'position': match.start(),
                    'explanation': self._get_phrase_explanation(category, phrase)
                })
        
        # Sort by severity and position
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        phrases.sort(key=lambda x: (severity_order[x['severity']], x['position']))
        
        return phrases
    
    def _get_phrase_explanation(self, category: str, phrase: str) -> str:
        """Explain why a phrase is problematic"""
        explanations = {
            'political': f'"{phrase}" is politically charged language',
            'hyperbolic': f'"{phrase}" uses exaggeration for emotional impact',
            'absolute': f'"{phrase}" makes sweeping generalizations',
            'assumption': f'"{phrase}" assumes reader agreement',
            'divisive': f'"{phrase}" creates us-vs-them dynamic',
            'fear': f'"{phrase}" uses fear to influence',
            'savior_language': f'"{phrase}" implies heroic narrative',
            'conflict_framing': f'"{phrase}" frames issue as conflict'
        }
        return explanations.get(category, f'"{phrase}" may bias perception')
    
    def _detect_manipulation_tactics(self, text: str, patterns: List[Dict]) -> List[Dict[str, Any]]:
        """Detect manipulation tactics"""
        tactics = []
        
        # Add pattern-based tactics
        for pattern in patterns:
            if pattern['severity'] in ['medium', 'high']:
                tactics.append({
                    'name': pattern['type'].replace('_', ' ').title(),
                    'type': pattern['type'],
                    'description': pattern['description'],
                    'severity': pattern['severity']
                })
        
        # Check formatting manipulation
        caps_words = len(re.findall(r'\b[A-Z]{3,}\b', text))
        if caps_words > 5:
            tactics.append({
                'name': 'Excessive Capitalization',
                'type': 'formatting',
                'description': f'{caps_words} ALL CAPS words create false urgency',
                'severity': 'medium'
            })
        
        # Multiple punctuation
        excessive_punct = len(re.findall(r'[!?]{2,}', text))
        if excessive_punct > 0:
            tactics.append({
                'name': 'Excessive Punctuation',
                'type': 'formatting',
                'description': 'Multiple punctuation marks manipulate emotion',
                'severity': 'low'
            })
        
        # Clickbait patterns
        clickbait_patterns = [
            (r'you won\'t believe', 'Curiosity Gap'),
            (r'(doctors|experts) hate', 'False Authority'),
            (r'one weird trick', 'Oversimplification'),
            (r'what (they|nobody) want you to know', 'Conspiracy Hook')
        ]
        
        for pattern, name in clickbait_patterns:
            if re.search(pattern, text, re.I):
                tactics.append({
                    'name': name,
                    'type': 'clickbait',
                    'description': 'Uses psychological triggers for engagement',
                    'severity': 'medium'
                })
        
        # Remove duplicates
        seen = set()
        unique_tactics = []
        for tactic in tactics:
            key = tactic['name']
            if key not in seen:
                seen.add(key)
                unique_tactics.append(tactic)
        
        return unique_tactics
    
    def _calculate_objectivity_score(self, dimensions: Dict, patterns: List, 
                                    phrases: List) -> int:
        """Calculate overall objectivity score"""
        score = 100
        
        # Deduct for dimensional biases
        for dim_name, dim_data in dimensions.items():
            if dim_name == 'sensational':
                score -= min(30, dim_data['score'] * 40)
            else:
                score -= min(20, abs(dim_data['score']) * 25)
        
        # Deduct for patterns
        pattern_penalties = {
            'cherry_picking': 15,
            'strawman': 20,
            'loaded_question': 10,
            'fear_appeal': 15,
            'false_balance': 5
        }
        
        for pattern in patterns:
            score -= pattern_penalties.get(pattern['type'], 5)
        
        # Deduct for loaded phrases
        high_severity = sum(1 for p in phrases if p['severity'] == 'high')
        score -= min(20, high_severity * 5 + len(phrases))
        
        return max(0, min(100, score))
    
    def _calculate_opinion_percentage(self, text: str) -> int:
        """Calculate percentage of opinion vs fact"""
        if not text:
            return 0
        
        opinion_indicators = [
            r'\b(believe|think|feel|seems?|appears?|probably|maybe|perhaps)\b',
            r'\b(in my (view|opinion)|I (think|believe|feel))\b',
            r'\b(should|shouldn\'t|ought|must)\b',
            r'\b(good|bad|better|worse|best|worst)\b'
        ]
        
        sentences = re.split(r'[.!?]+', text)
        opinion_count = 0
        
        for sentence in sentences:
            if any(re.search(pattern, sentence, re.I) for pattern in opinion_indicators):
                opinion_count += 1
        
        return min(100, int((opinion_count / max(len(sentences), 1)) * 100))
    
    def _calculate_emotional_score(self, text: str) -> int:
        """Calculate emotional intensity"""
        emotional_words = {
            # High intensity
            'shocking': 3, 'devastating': 3, 'horrifying': 3, 'outrageous': 3,
            'explosive': 3, 'catastrophic': 3, 'terrifying': 3,
            # Medium intensity
            'amazing': 2, 'terrible': 2, 'wonderful': 2, 'awful': 2,
            'fantastic': 2, 'horrible': 2, 'incredible': 2,
            # Low intensity
            'surprising': 1, 'concerning': 1, 'interesting': 1, 'notable': 1
        }
        
        text_lower = text.lower()
        word_count = len(text.split())
        
        emotional_score = 0
        for word, weight in emotional_words.items():
            count = text_lower.count(word)
            emotional_score += count * weight
        
        # Normalize
        score = min(100, int((emotional_score / max(word_count, 1)) * 500))
        
        return score
    
    def _calculate_confidence(self, text: str, patterns: List) -> int:
        """Calculate confidence in bias detection"""
        confidence = 50
        
        # Text length
        words = len(text.split())
        if words > 1000:
            confidence += 20
        elif words > 500:
            confidence += 10
        elif words < 100:
            confidence -= 20
        
        # Pattern detection
        confidence += min(20, len(patterns) * 5)
        
        # Ambiguous language reduces confidence
        ambiguous = len(re.findall(r'\b(might|could|possibly|perhaps|maybe)\b', text, re.I))
        confidence -= min(15, ambiguous * 2)
        
        return max(20, min(95, confidence))
    
    def _calculate_overall_bias_score(self, dimensions: Dict, objectivity: int) -> int:
        """Calculate single bias score from dimensions"""
        # Weight different dimensions
        weights = {
            'political': 0.3,
            'sensational': 0.25,
            'corporate': 0.15,
            'establishment': 0.15,
            'nationalistic': 0.15
        }
        
        # Calculate weighted bias
        total_bias = 0
        for dim, weight in weights.items():
            if dim in dimensions:
                # For sensational, only positive scores indicate bias
                if dim == 'sensational':
                    total_bias += dimensions[dim]['score'] * weight
                else:
                    total_bias += abs(dimensions[dim]['score']) * weight
        
        # Convert to 0-100 scale
        bias_from_dimensions = int(total_bias * 100)
        
        # Factor in objectivity (inverted)
        bias_from_objectivity = 100 - objectivity
        
        # Weighted average
        final_score = int(bias_from_dimensions * 0.7 + bias_from_objectivity * 0.3)
        
        return max(0, min(100, final_score))
    
    def _get_bias_level(self, score: int) -> str:
        """Convert bias score to level"""
        if score >= 70:
            return 'High Bias'
        elif score >= 50:
            return 'Moderate Bias'
        elif score >= 30:
            return 'Some Bias'
        elif score >= 15:
            return 'Minimal Bias'
        else:
            return 'Very Low Bias'
    
    def _analyze_framing(self, text: str) -> Dict[str, Any]:
        """Analyze how issues are framed"""
        frames = {
            'victim': ['victim of', 'suffered under', 'targeted by'],
            'hero': ['champion of', 'defender of', 'fighting for'],
            'threat': ['threat to', 'danger to', 'risk to'],
            'progress': ['step forward', 'advancement', 'improvement']
        }
        
        detected = {}
        text_lower = text.lower()
        
        for frame_type, patterns in frames.items():
            count = sum(1 for p in patterns if p in text_lower)
            if count > 0:
                detected[frame_type] = count
        
        return {
            'frames_detected': detected,
            'dominant_frame': max(detected.items(), key=lambda x: x[1])[0] if detected else None,
            'frame_diversity': len(detected)
        }
    
    def _analyze_source_diversity(self, text: str) -> Dict[str, Any]:
        """Analyze diversity of sources cited"""
        source_patterns = {
            'official': r'(official|spokesperson|department|agency)',
            'expert': r'(expert|professor|researcher|analyst|study)',
            'activist': r'(activist|advocate|campaigner)',
            'anonymous': r'(sources? say|sources? told|anonymous)'
        }
        
        source_counts = {}
        for source_type, pattern in source_patterns.items():
            count = len(re.findall(pattern, text, re.I))
            if count > 0:
                source_counts[source_type] = count
        
        total = sum(source_counts.values())
        diversity = len(source_counts)
        
        return {
            'source_types': source_counts,
            'total_sources': total,
            'diversity_score': min(100, diversity * 25),
            'primary_source': max(source_counts.items(), key=lambda x: x[1])[0] if source_counts else None
        }
    
    def _create_visualization_data(self, dimensions: Dict) -> Dict[str, Any]:
        """Create data for bias visualization"""
        viz_data = []
        
        for dim_name, dim_data in dimensions.items():
            viz_data.append({
                'dimension': self._get_dimension_display_name(dim_name),
                'score': abs(dim_data['score']) * 100,
                'direction': dim_data['label'],
                'raw_score': dim_data['score'],
                'explanation': dim_data['explanation']
            })
        
        return {
            'type': 'radar',
            'data': viz_data,
            'summary': self._generate_viz_summary(dimensions)
        }
    
    def _get_dimension_display_name(self, dimension: str) -> str:
        """Get display name for dimension"""
        names = {
            'political': 'Political Bias',
            'corporate': 'Corporate Stance',
            'sensational': 'Sensationalism',
            'nationalistic': 'National Focus',
            'establishment': 'Authority Trust'
        }
        return names.get(dimension, dimension.title())
    
    def _generate_viz_summary(self, dimensions: Dict) -> str:
        """Generate visualization summary"""
        high_bias = []
        for name, data in dimensions.items():
            if abs(data['score']) > 0.5 or (name == 'sensational' and data['score'] > 0.5):
                high_bias.append(self._get_dimension_display_name(name))
        
        if not high_bias:
            return "Relatively balanced across all dimensions"
        else:
            return f"Strong bias in: {', '.join(high_bias)}"
    
    def _generate_findings(self, dimensions: Dict, patterns: List, 
                          phrases: List, tactics: List) -> List[Dict[str, Any]]:
        """Generate key findings"""
        findings = []
        
        # Dimensional bias findings
        for dim_name, dim_data in dimensions.items():
            if abs(dim_data['score']) > 0.5 or (dim_name == 'sensational' and dim_data['score'] > 0.4):
                findings.append({
                    'type': f'{dim_name}_bias',
                    'text': f"{dim_data['label']} bias detected",
                    'severity': 'high' if abs(dim_data['score']) > 0.7 else 'medium',
                    'explanation': dim_data['explanation']
                })
        
        # Pattern findings
        high_severity_patterns = [p for p in patterns if p['severity'] == 'high']
        if high_severity_patterns:
            findings.append({
                'type': 'bias_patterns',
                'text': f"{len(high_severity_patterns)} concerning bias patterns found",
                'severity': 'high',
                'explanation': high_severity_patterns[0]['description']
            })
        
        # Loaded phrase findings
        high_phrases = [p for p in phrases if p['severity'] == 'high']
        if len(high_phrases) > 2:
            findings.append({
                'type': 'loaded_language',
                'text': f"{len(high_phrases)} instances of highly loaded language",
                'severity': 'medium',
                'explanation': 'Emotional language may manipulate reader perception'
            })
        
        # Manipulation findings
        if tactics:
            findings.append({
                'type': 'manipulation',
                'text': f"{len(tactics)} manipulation tactics detected",
                'severity': tactics[0]['severity'] if tactics else 'medium',
                'explanation': tactics[0]['description'] if tactics else ''
            })
        
        # Positive finding if relatively unbiased
        if not findings:
            findings.append({
                'type': 'balanced',
                'text': 'Article maintains relative objectivity',
                'severity': 'positive',
                'explanation': 'No significant bias patterns detected'
            })
        
        return findings[:5]  # Top 5 findings
    
    def _generate_summary(self, dimensions: Dict, objectivity: int, bias_score: int) -> str:
        """Generate human-readable summary"""
        
        # Identify strongest biases
        strong_biases = []
        for name, data in dimensions.items():
            if abs(data['score']) > 0.5 or (name == 'sensational' and data['score'] > 0.4):
                strong_biases.append(data['label'])
        
        # Build summary
        if bias_score < 20:
            base = "This article demonstrates good objectivity with minimal bias."
        elif bias_score < 40:
            base = "This article shows some bias but maintains reasonable objectivity."
        elif bias_score < 60:
            base = "This article contains moderate bias that may influence interpretation."
        else:
            base = "This article shows significant bias that substantially affects objectivity."
        
        # Add details
        if strong_biases:
            base += f" Detected: {', '.join(strong_biases[:2])}."
        
        base += f" Objectivity score: {objectivity}%."
        
        return base
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        info = super().get_service_info()
        info.update({
            'capabilities': [
                'Multi-dimensional bias analysis',
                'Political spectrum detection',
                'Sensationalism measurement',
                'Corporate bias detection',
                'Manipulation tactic identification',
                'Loaded language extraction',
                'Framing analysis',
                'Source diversity assessment',
                'AI-ENHANCED subtle bias detection',
                'AI-powered framing analysis'
            ],
            'dimensions_analyzed': 5,
            'patterns_detected': len(self.loaded_patterns),
            'visualization_ready': True,
            'ai_enhanced': self._ai_available
        })
        return info
