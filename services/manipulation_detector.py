"""
Manipulation Detector Service - FIXED VERSION
Detects propaganda techniques and manipulation tactics in news articles
FIXED: Removed AI enhancement bugs that were causing crashes
"""

import re
import logging
from typing import Dict, List, Any, Tuple
from collections import Counter
from services.base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)


class ManipulationDetector(BaseAnalyzer):
    """Detect manipulation tactics and propaganda techniques in articles - FIXED VERSION"""
    
    def __init__(self):
        super().__init__('manipulation_detector')
        self._initialize_manipulation_patterns()
        logger.info("ManipulationDetector initialized with comprehensive pattern database")
    
    def _initialize_manipulation_patterns(self):
        """Initialize comprehensive manipulation and propaganda patterns"""
        self.manipulation_patterns = {
            'fear_mongering': {
                'name': 'Fear Mongering',
                'description': 'Using fear-inducing language to manipulate emotions',
                'severity': 'high',
                'keywords': [
                    'catastrophe', 'disaster', 'crisis', 'threat', 'danger',
                    'destroy', 'devastate', 'collapse', 'nightmare', 'apocalypse',
                    'terrifying', 'horrifying', 'deadly', 'fatal', 'doom'
                ],
                'weight': 3
            },
            'emotional_manipulation': {
                'name': 'Emotional Manipulation',
                'description': 'Excessive emotional appeals to bypass rational thinking',
                'severity': 'medium',
                'keywords': [
                    'shocking', 'outrageous', 'disgusting', 'horrifying',
                    'unbelievable', 'jaw-dropping', 'mind-blowing', 'heartbreaking',
                    'devastating', 'tragic', 'inspiring', 'miraculous'
                ],
                'weight': 2
            },
            'false_urgency': {
                'name': 'False Urgency',
                'description': 'Creating artificial time pressure',
                'severity': 'medium',
                'keywords': [
                    'act now', 'limited time', 'don\'t wait', 'expires soon',
                    'last chance', 'urgent', 'immediately', 'breaking', 'just in'
                ],
                'weight': 2
            },
            'bandwagon': {
                'name': 'Bandwagon Appeal',
                'description': 'Suggesting everyone else believes/does something',
                'severity': 'low',
                'keywords': [
                    'everyone knows', 'everybody agrees', 'most people',
                    'nobody disagrees', 'universally accepted', 'common knowledge',
                    'widespread belief', 'majority thinks'
                ],
                'weight': 2
            },
            'ad_hominem': {
                'name': 'Ad Hominem Attacks',
                'description': 'Attacking the person rather than the argument',
                'severity': 'high',
                'keywords': [
                    'idiot', 'moron', 'stupid', 'ignorant', 'fool',
                    'corrupt', 'evil', 'liar', 'fraud', 'incompetent'
                ],
                'weight': 3
            },
            'loaded_questions': {
                'name': 'Loaded Questions',
                'description': 'Questions that contain unfair assumptions',
                'severity': 'medium',
                'patterns': [
                    r'why (?:do|does|did) .+? always',
                    r'how can .+? justify',
                    r'isn\'t it true that',
                    r'don\'t you think'
                ],
                'weight': 2
            },
            'false_dichotomy': {
                'name': 'False Dichotomy',
                'description': 'Presenting only two options when more exist',
                'severity': 'medium',
                'patterns': [
                    r'either .+? or',
                    r'you\'re either with us or',
                    r'only two (?:choices|options)',
                    r'(?:must|have to) choose between'
                ],
                'weight': 2
            },
            'cherry_picking': {
                'name': 'Cherry Picking',
                'description': 'Selecting only favorable evidence',
                'severity': 'medium',
                'keywords': [
                    'conveniently ignores', 'fails to mention', 'overlooked',
                    'selective', 'one example', 'single case'
                ],
                'weight': 2
            },
            'appeal_to_authority': {
                'name': 'Appeal to Authority',
                'description': 'Using authority figures inappropriately',
                'severity': 'low',
                'patterns': [
                    r'experts? (?:all )?agree',
                    r'scientists? (?:all )?say',
                    r'doctors? (?:all )?recommend',
                    r'authorities confirm'
                ],
                'weight': 1
            },
            'strawman': {
                'name': 'Straw Man',
                'description': 'Misrepresenting opposing arguments',
                'severity': 'high',
                'keywords': [
                    'claims that', 'pretends', 'wants you to believe',
                    'would have you think', 'suggests that all'
                ],
                'weight': 3
            }
        }
        
        # Propaganda techniques
        self.propaganda_techniques = {
            'card_stacking': {
                'name': 'Card Stacking',
                'description': 'Presenting only one side of an argument',
                'indicators': ['only positive', 'only negative', 'one-sided', 'no counterargument']
            },
            'name_calling': {
                'name': 'Name Calling',
                'description': 'Using negative labels to discredit',
                'indicators': ['radical', 'extremist', 'conspiracy theorist', 'denier']
            },
            'glittering_generalities': {
                'name': 'Glittering Generalities',
                'description': 'Using vague positive phrases',
                'indicators': ['freedom', 'democracy', 'justice', 'prosperity', 'security']
            },
            'transfer': {
                'name': 'Transfer Technique',
                'description': 'Connecting something to positive/negative symbols',
                'indicators': ['flag', 'founding fathers', 'constitution', 'tradition']
            }
        }
    
    def _check_availability(self) -> bool:
        """Service is always available"""
        return True
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect manipulation tactics in article - FIXED VERSION
        FIXED: Removed problematic AI enhancement
        
        Expected input:
            - text: Article text to analyze
            - title: (optional) Article title
            
        Returns:
            Standardized response with manipulation analysis
        """
        try:
            text = data.get('text', '')
            if not text:
                return self.get_error_result("No text provided for manipulation analysis")
            
            title = data.get('title', '')
            full_text = f"{title}\n\n{text}" if title else text
            
            logger.info(f"Analyzing manipulation tactics in {len(full_text)} characters of text")
            
            # Detect various manipulation tactics
            tactics_found = self._detect_manipulation_tactics(full_text)
            propaganda = self._detect_propaganda_techniques(full_text)
            logical_fallacies = self._detect_logical_fallacies(full_text)
            clickbait = self._analyze_clickbait(title)
            
            # Calculate scores
            manipulation_score = self._calculate_manipulation_score(
                tactics_found, propaganda, logical_fallacies, clickbait
            )
            
            # Determine manipulation level
            if manipulation_score >= 70:
                level = 'High'
                assessment = 'Significant manipulation tactics detected'
            elif manipulation_score >= 40:
                level = 'Moderate'
                assessment = 'Some manipulation tactics present'
            elif manipulation_score >= 20:
                level = 'Low'
                assessment = 'Minor manipulation indicators'
            else:
                level = 'Minimal'
                assessment = 'Article appears straightforward'
            
            # Get most severe tactics
            all_tactics = tactics_found + propaganda + logical_fallacies
            if clickbait['is_clickbait']:
                all_tactics.append({
                    'name': 'Clickbait Title',
                    'type': 'clickbait',
                    'severity': 'medium',
                    'description': clickbait['reason']
                })
            
            # Sort by severity
            severity_order = {'high': 0, 'medium': 1, 'low': 2}
            all_tactics.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 3))
            
            # Generate findings for UI
            findings = []
            for tactic in all_tactics[:5]:  # Top 5 tactics
                findings.append({
                    'type': 'manipulation',
                    'severity': tactic.get('severity', 'medium'),
                    'text': f"{tactic['name']}: {tactic.get('description', '')}",
                    'finding': tactic['name']
                })
            
            # Generate summary
            summary = self._generate_summary(manipulation_score, level, all_tactics)
            
            logger.info(f"Manipulation analysis complete: {manipulation_score}/100 ({level}) - {len(all_tactics)} tactics found")
            
            return {
                'service': self.service_name,
                'success': True,
                'data': {
                    'score': manipulation_score,
                    'level': level,
                    'findings': findings,
                    'assessment': assessment,
                    'summary': summary,
                    'tactics_found': all_tactics[:10],  # Top 10 tactics
                    'tactic_count': len(all_tactics),
                    'propaganda_techniques': propaganda,
                    'logical_fallacies': logical_fallacies,
                    'clickbait_analysis': clickbait,
                    'manipulation_score': manipulation_score,  # Backward compatibility
                    'manipulation_level': level,  # Backward compatibility
                    'persuasion_score': manipulation_score,  # Backward compatibility
                    'details': {
                        'total_tactics': len(all_tactics),
                        'high_severity_count': sum(1 for t in all_tactics if t.get('severity') == 'high'),
                        'medium_severity_count': sum(1 for t in all_tactics if t.get('severity') == 'medium'),
                        'low_severity_count': sum(1 for t in all_tactics if t.get('severity') == 'low'),
                        'has_clickbait': clickbait['is_clickbait'],
                        'word_count': len(full_text.split())
                    }
                },
                'metadata': {
                    'tactics_detected': len(all_tactics),
                    'analyzed_with_title': bool(title)
                }
            }
            
        except Exception as e:
            logger.error(f"Manipulation analysis failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _detect_manipulation_tactics(self, text: str) -> List[Dict[str, Any]]:
        """Detect manipulation patterns in text"""
        tactics = []
        text_lower = text.lower()
        
        for pattern_name, pattern_info in self.manipulation_patterns.items():
            if 'keywords' in pattern_info:
                # Check keywords
                count = sum(1 for keyword in pattern_info.get('keywords', []) 
                           if keyword in text_lower)
                if count > 0:
                    tactics.append({
                        'type': pattern_name,
                        'name': pattern_info.get('name', pattern_name),
                        'severity': pattern_info.get('severity', 'medium'),
                        'description': pattern_info.get('description', ''),
                        'instances': count
                    })
            
            if 'patterns' in pattern_info:
                # Check regex patterns
                count = 0
                for pattern in pattern_info.get('patterns', []):
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    count += len(matches)
                
                if count > 0:
                    tactics.append({
                        'type': pattern_name,
                        'name': pattern_info.get('name', pattern_name),
                        'severity': pattern_info.get('severity', 'medium'),
                        'description': pattern_info.get('description', ''),
                        'instances': count
                    })
        
        return tactics
    
    def _detect_propaganda_techniques(self, text: str) -> List[Dict[str, Any]]:
        """Detect propaganda techniques"""
        techniques = []
        text_lower = text.lower()
        
        # Card stacking - check for one-sided presentation
        positive_words = ['excellent', 'outstanding', 'perfect', 'amazing', 'wonderful']
        negative_words = ['terrible', 'awful', 'disaster', 'horrible', 'catastrophic']
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if (pos_count > 5 and neg_count == 0) or (neg_count > 5 and pos_count == 0):
            techniques.append({
                'type': 'card_stacking',
                'name': 'Card Stacking',
                'severity': 'medium',
                'description': 'Presents only one side of the argument'
            })
        
        # Name calling
        name_calling_terms = ['radical', 'extremist', 'fanatic', 'conspiracy theorist', 'denier', 'apologist']
        if any(term in text_lower for term in name_calling_terms):
            techniques.append({
                'type': 'name_calling',
                'name': 'Name Calling',
                'severity': 'high',
                'description': 'Uses negative labels to discredit opposition'
            })
        
        # Glittering generalities
        glittering_terms = ['freedom', 'liberty', 'democracy', 'justice', 'patriotic', 'prosperity']
        glitter_count = sum(1 for term in glittering_terms if term in text_lower)
        if glitter_count > 3:
            techniques.append({
                'type': 'glittering_generalities',
                'name': 'Glittering Generalities',
                'severity': 'low',
                'description': 'Uses vague positive terms without substance'
            })
        
        return techniques
    
    def _detect_logical_fallacies(self, text: str) -> List[Dict[str, Any]]:
        """Detect logical fallacies"""
        fallacies = []
        
        # Slippery slope
        if re.search(r'(will lead to|slippery slope|before you know it|next thing)', text, re.IGNORECASE):
            fallacies.append({
                'type': 'slippery_slope',
                'name': 'Slippery Slope',
                'severity': 'medium',
                'description': 'Suggests one event will lead to extreme consequences'
            })
        
        # Appeal to emotion
        emotion_phrases = ['think of the children', 'how would you feel', 'imagine if', 'put yourself in']
        if any(phrase in text.lower() for phrase in emotion_phrases):
            fallacies.append({
                'type': 'appeal_to_emotion',
                'name': 'Appeal to Emotion',
                'severity': 'medium',
                'description': 'Manipulates emotions rather than using logic'
            })
        
        # Hasty generalization
        if re.search(r'(all|every|none|no one|always|never) \w+ (is|are|do|does)', text, re.IGNORECASE):
            fallacies.append({
                'type': 'hasty_generalization',
                'name': 'Hasty Generalization',
                'severity': 'medium',
                'description': 'Makes broad claims from limited examples'
            })
        
        return fallacies
    
    def _analyze_clickbait(self, title: str) -> Dict[str, Any]:
        """Analyze if title is clickbait"""
        if not title:
            return {'is_clickbait': False, 'score': 0, 'reason': 'No title provided'}
        
        clickbait_score = 0
        reasons = []
        
        # Check for clickbait patterns
        if title.endswith('?'):
            clickbait_score += 20
            reasons.append('Question headline')
        
        if re.search(r'you won\'t believe|shocking|amazing|this one trick', title, re.IGNORECASE):
            clickbait_score += 40
            reasons.append('Sensational language')
        
        if re.search(r'\d+ (things|ways|reasons|facts)', title, re.IGNORECASE):
            clickbait_score += 30
            reasons.append('Listicle format')
        
        if '...' in title or title.count('!') > 1:
            clickbait_score += 20
            reasons.append('Excessive punctuation')
        
        return {
            'is_clickbait': clickbait_score > 50,
            'score': clickbait_score,
            'reason': '; '.join(reasons) if reasons else 'No clickbait indicators'
        }
    
    def _calculate_manipulation_score(self, tactics: List, propaganda: List, 
                                    fallacies: List, clickbait: Dict) -> int:
        """Calculate overall manipulation score"""
        base_score = 0
        
        # Add scores for tactics based on severity
        for tactic in tactics:
            if tactic.get('severity') == 'high':
                base_score += 15
            elif tactic.get('severity') == 'medium':
                base_score += 10
            elif tactic.get('severity') == 'low':
                base_score += 5
        
        # Add propaganda score
        base_score += len(propaganda) * 12
        
        # Add fallacy score
        base_score += len(fallacies) * 10
        
        # Add clickbait score
        if clickbait['is_clickbait']:
            base_score += 20
        
        # Normalize to 0-100 scale
        normalized_score = min(100, base_score)
        
        return normalized_score
    
    def _generate_summary(self, score: int, level: str, tactics: List[Dict]) -> str:
        """Generate a summary of manipulation findings"""
        if score < 20:
            return f"Minimal manipulation detected (score: {score}%). Article uses straightforward language and logical arguments."
        elif score < 40:
            tactic_names = [t['name'] for t in tactics[:2]]
            return f"Low manipulation level (score: {score}%). Found: {', '.join(tactic_names)}. Generally factual presentation."
        elif score < 70:
            tactic_names = [t['name'] for t in tactics[:3]]
            return f"Moderate manipulation (score: {score}%). Multiple tactics detected: {', '.join(tactic_names)}. Reader caution advised."
        else:
            high_severity = sum(1 for t in tactics if t.get('severity') == 'high')
            return f"High manipulation level (score: {score}%). {len(tactics)} tactics found including {high_severity} severe issues. Significant bias or propaganda present."
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        info = super().get_service_info()
        info.update({
            'capabilities': [
                'Propaganda technique detection',
                'Logical fallacy identification',
                'Emotional manipulation analysis',
                'Clickbait detection',
                'Fear mongering identification',
                'Ad hominem detection',
                'False dichotomy recognition',
                'Manipulation scoring'
            ],
            'patterns_loaded': len(self.manipulation_patterns),
            'propaganda_types': len(self.propaganda_techniques)
        })
        return info
