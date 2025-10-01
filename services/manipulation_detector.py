"""
Manipulation Detector Service - ENHANCED VERSION v2.0
Last Updated: October 1, 2025
Detects propaganda techniques and manipulation tactics with comprehensive pattern matching

MAJOR CHANGES:
- Inverted integrity score (100 = good, 0 = bad) to match UI expectations
- Added 15+ new manipulation patterns including selective quoting, cherry-picking, whataboutism
- Enhanced scoring algorithm with better severity weighting
- Improved quote and source manipulation detection
- More nuanced emotional analysis
- Better fallacy detection including appeals to authority, anecdotal evidence
- Enhanced propaganda technique detection
- Comprehensive context analysis for selective presentation
"""

import re
import logging
import time
from typing import Dict, List, Any, Tuple
from collections import Counter
from services.base_analyzer import BaseAnalyzer
from services.ai_enhancement_mixin import AIEnhancementMixin

logger = logging.getLogger(__name__)


class ManipulationDetector(BaseAnalyzer, AIEnhancementMixin):
    """Detect manipulation tactics and propaganda techniques WITH BULLETPROOF AI ENHANCEMENT"""
    
    def __init__(self):
        super().__init__('manipulation_detector')
        AIEnhancementMixin.__init__(self)
        self._initialize_manipulation_patterns()
        logger.info(f"ManipulationDetector v2.0 initialized with {len(self.manipulation_patterns)} patterns and AI: {self._ai_available}")
    
    def _initialize_manipulation_patterns(self):
        """Initialize comprehensive manipulation and propaganda patterns - ENHANCED v2.0"""
        self.manipulation_patterns = {
            'fear_mongering': {
                'name': 'Fear Mongering',
                'description': 'Using fear-inducing language to manipulate emotions',
                'severity': 'high',
                'keywords': [
                    'catastrophe', 'disaster', 'crisis', 'threat', 'danger',
                    'destroy', 'devastate', 'collapse', 'nightmare', 'apocalypse',
                    'terrifying', 'horrifying', 'deadly', 'fatal', 'doom',
                    'chaos', 'mayhem', 'peril', 'menace', 'calamity'
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
                    'devastating', 'tragic', 'inspiring', 'miraculous',
                    'stunning', 'breathtaking', 'overwhelming', 'gut-wrenching'
                ],
                'weight': 2
            },
            'false_urgency': {
                'name': 'False Urgency',
                'description': 'Creating artificial time pressure',
                'severity': 'medium',
                'keywords': [
                    'act now', 'limited time', 'don\'t wait', 'expires soon',
                    'last chance', 'urgent', 'immediately', 'breaking', 'just in',
                    'hurry', 'running out', 'final opportunity', 'time-sensitive'
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
                    'widespread belief', 'majority thinks', 'consensus is',
                    'all experts agree', 'undeniable fact'
                ],
                'weight': 2
            },
            'ad_hominem': {
                'name': 'Ad Hominem Attacks',
                'description': 'Attacking the person rather than the argument',
                'severity': 'high',
                'keywords': [
                    'idiot', 'moron', 'stupid', 'ignorant', 'fool',
                    'corrupt', 'evil', 'liar', 'fraud', 'incompetent',
                    'disgrace', 'pathetic', 'worthless', 'hypocrite'
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
                    r'don\'t you think',
                    r'when will .+? stop',
                    r'why won\'t .+? admit'
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
                    r'(?:must|have to) choose between',
                    r'if not .+?, then'
                ],
                'weight': 2
            },
            'strawman': {
                'name': 'Straw Man',
                'description': 'Misrepresenting opposing arguments',
                'severity': 'high',
                'keywords': [
                    'claims that', 'pretends', 'wants you to believe',
                    'would have you think', 'suggests that all',
                    'trying to convince', 'expects us to accept'
                ],
                'weight': 3
            },
            'selective_quoting': {
                'name': 'Selective Quoting',
                'description': 'Using quotes out of context or cherry-picking statements',
                'severity': 'high',
                'patterns': [
                    r'(?:said|stated|claimed|admitted)[\s\S]{0,50}["\'](?:(?!however|but|although).){20,}["\'](?![\s\S]{0,100}(?:however|but|although|context))',
                    r'according to[\s\S]{0,30}["\'][^"\']{10,}["\'][\s\S]{0,50}(?:but |however |although )',
                ],
                'keywords': [
                    'out of context', 'partial quote', 'selectively quoted',
                    'cherry-picked', 'misleading quote'
                ],
                'weight': 3
            },
            'cherry_picking': {
                'name': 'Cherry-Picking Data',
                'description': 'Selecting only data that supports the argument',
                'severity': 'high',
                'keywords': [
                    'one study shows', 'according to this data', 'this evidence proves',
                    'one expert said', 'a report found', 'research indicates'
                ],
                'patterns': [
                    r'(?:one|a single|this) (?:study|survey|poll|report) (?:shows|found|proves|indicates)',
                    r'according to (?:one|this|a) (?:expert|study|source)'
                ],
                'weight': 3
            },
            'whataboutism': {
                'name': 'Whataboutism',
                'description': 'Deflecting criticism by pointing to others\' faults',
                'severity': 'medium',
                'patterns': [
                    r'what about',
                    r'but what about',
                    r'(?:they|others) (?:also|too) did',
                    r'look at what .+? did'
                ],
                'keywords': [
                    'hypocrisy', 'double standard', 'they did it too'
                ],
                'weight': 2
            },
            'appeal_to_authority': {
                'name': 'False Appeal to Authority',
                'description': 'Citing irrelevant or questionable authorities',
                'severity': 'medium',
                'patterns': [
                    r'(?:celebrity|actor|athlete) .+? (?:says|believes|endorses)',
                    r'famous .+? (?:agrees|supports)',
                    r'as .+? once said'
                ],
                'keywords': [
                    'expert consensus', 'leading experts', 'top scientists',
                    'renowned authority', 'celebrity endorsement'
                ],
                'weight': 2
            },
            'anecdotal_evidence': {
                'name': 'Anecdotal Evidence',
                'description': 'Using personal stories as proof of general claims',
                'severity': 'low',
                'patterns': [
                    r'I (?:know|met|heard about) (?:someone|a person|a guy|a woman)',
                    r'my (?:friend|cousin|neighbor|uncle)',
                    r'this one time',
                    r'I once (?:saw|heard|experienced)'
                ],
                'weight': 1
            },
            'overgeneralization': {
                'name': 'Overgeneralization',
                'description': 'Making sweeping statements from limited evidence',
                'severity': 'medium',
                'patterns': [
                    r'all .+? (?:are|do|believe|think)',
                    r'(?:every|each) .+? (?:is|does|believes)',
                    r'no .+? (?:can|will|would)',
                    r'(?:always|never|constantly|invariably) .+? (?:does|is|believes)'
                ],
                'weight': 2
            },
            'loaded_language': {
                'name': 'Loaded Language',
                'description': 'Using emotionally charged words to influence opinion',
                'severity': 'medium',
                'keywords': [
                    'extremist', 'radical', 'fanatic', 'zealot', 'militant',
                    'regime', 'propaganda', 'conspiracy', 'scheme', 'plot',
                    'elites', 'establishment', 'mainstream', 'deep state'
                ],
                'weight': 2
            },
            'false_equivalence': {
                'name': 'False Equivalence',
                'description': 'Comparing two things that aren\'t really comparable',
                'severity': 'medium',
                'patterns': [
                    r'just (?:like|as bad as)',
                    r'no different (?:from|than)',
                    r'same as',
                    r'equally (?:bad|good|wrong|right)'
                ],
                'weight': 2
            },
            'guilt_by_association': {
                'name': 'Guilt by Association',
                'description': 'Discrediting ideas by linking them to disliked groups',
                'severity': 'medium',
                'patterns': [
                    r'sounds like something .+? would say',
                    r'reminds me of .+?',
                    r'similar to (?:Nazi|Communist|Fascist|terrorist)',
                    r'associated with'
                ],
                'weight': 2
            },
            'appeal_to_emotion': {
                'name': 'Appeal to Emotion',
                'description': 'Manipulating emotions rather than using logic',
                'severity': 'medium',
                'keywords': [
                    'think of the children', 'imagine if', 'how would you feel',
                    'picture this', 'what if it was you', 'your family could be next'
                ],
                'patterns': [
                    r'think of (?:the|your) (?:children|family|future)',
                    r'imagine (?:if|how|what)',
                    r'what if (?:this|it) (?:was|happened to) you'
                ],
                'weight': 2
            },
            'sensationalism': {
                'name': 'Sensationalism',
                'description': 'Exaggerating for dramatic effect',
                'severity': 'medium',
                'keywords': [
                    'unprecedented', 'historic', 'epic', 'massive', 'explosive',
                    'bombshell', 'game-changer', 'revolutionary', 'groundbreaking',
                    'world-shattering', 'earth-shattering'
                ],
                'weight': 2
            },
            'victimization': {
                'name': 'Victimization',
                'description': 'Portraying as victim to gain sympathy',
                'severity': 'low',
                'keywords': [
                    'attacked', 'persecuted', 'silenced', 'censored', 'cancelled',
                    'witch hunt', 'vendetta', 'targeted', 'scapegoat'
                ],
                'weight': 1
            },
            'us_vs_them': {
                'name': 'Us vs Them',
                'description': 'Creating artificial divisions',
                'severity': 'high',
                'patterns': [
                    r'(?:we|us|our side) (?:vs|versus|against) (?:them|they|their side)',
                    r'real Americans',
                    r'the people (?:vs|versus|against)',
                    r'enemies of'
                ],
                'keywords': [
                    'real americans', 'true patriots', 'the people', 'ordinary folks',
                    'elites', 'establishment', 'them', 'those people'
                ],
                'weight': 3
            }
        }
    
    def _check_availability(self) -> bool:
        """Service is always available"""
        return True
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect manipulation tactics WITH BULLETPROOF AI ENHANCEMENT
        v2.0: INVERTED INTEGRITY SCORE - Higher is better!
        """
        try:
            start_time = time.time()
            
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
            emotional_score = self._calculate_emotional_score(full_text)
            quote_manipulation = self._analyze_quote_manipulation(full_text)
            
            # Calculate MANIPULATION score (higher = more manipulation)
            manipulation_score = self._calculate_manipulation_score(
                tactics_found, propaganda, logical_fallacies, clickbait, quote_manipulation
            )
            
            # INVERT to INTEGRITY score (higher = better)
            integrity_score = 100 - manipulation_score
            
            # Determine manipulation level based on INTEGRITY score
            if integrity_score >= 80:
                level = 'Minimal'
                assessment = 'Article appears straightforward with minimal manipulation'
            elif integrity_score >= 60:
                level = 'Low'
                assessment = 'Minor manipulation indicators present'
            elif integrity_score >= 40:
                level = 'Moderate'
                assessment = 'Some manipulation tactics present'
            elif integrity_score >= 20:
                level = 'High'
                assessment = 'Significant manipulation tactics detected'
            else:
                level = 'Severe'
                assessment = 'Extensive manipulation and propaganda techniques'
            
            # Collect all tactics
            all_tactics = tactics_found + propaganda + logical_fallacies
            if clickbait['is_clickbait']:
                all_tactics.append({
                    'name': 'Clickbait Title',
                    'type': 'clickbait',
                    'severity': 'medium',
                    'description': clickbait['reason']
                })
            if quote_manipulation['score'] > 0:
                all_tactics.append({
                    'name': 'Quote Manipulation',
                    'type': 'selective_quoting',
                    'severity': 'high',
                    'description': quote_manipulation['reason']
                })
            
            # Sort by severity
            severity_order = {'high': 0, 'medium': 1, 'low': 2}
            all_tactics.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 3))
            
            # Generate findings for UI
            findings = []
            for tactic in all_tactics[:10]:  # Top 10 tactics for display
                findings.append({
                    'type': 'manipulation',
                    'severity': tactic.get('severity', 'medium'),
                    'text': f"{tactic['name']}: {tactic.get('description', '')}",
                    'explanation': f"Found {tactic['name'].lower()} in the content"
                })
            
            # Generate summary with INTEGRITY perspective
            summary = self._generate_summary(integrity_score, level, all_tactics)
            
            # FIXED: Ensure consistent data structure with INTEGRITY score
            result = {
                'service': self.service_name,
                'success': True,
                'data': {
                    'score': integrity_score,  # This is now INTEGRITY (100 = good)
                    'integrity_score': integrity_score,  # Make it explicit
                    'manipulation_score': manipulation_score,  # Raw manipulation (100 = bad)
                    'level': level,
                    'manipulation_level': level,
                    'findings': findings,
                    'assessment': assessment,
                    'summary': summary,
                    'tactics_found': all_tactics[:15],  # More tactics for analysis
                    'tactic_count': len(all_tactics),
                    'techniques': [t['name'] for t in all_tactics[:10]],  # For UI compatibility
                    'propaganda_techniques': propaganda,
                    'logical_fallacies': logical_fallacies,
                    'clickbait_analysis': clickbait,
                    'quote_manipulation': quote_manipulation,
                    'emotional_score': emotional_score,
                    'persuasion_score': manipulation_score,  # Backward compatibility
                    'details': {
                        'total_tactics': len(all_tactics),
                        'high_severity_count': sum(1 for t in all_tactics if t.get('severity') == 'high'),
                        'medium_severity_count': sum(1 for t in all_tactics if t.get('severity') == 'medium'),
                        'low_severity_count': sum(1 for t in all_tactics if t.get('severity') == 'low'),
                        'has_clickbait': clickbait['is_clickbait'],
                        'has_quote_manipulation': quote_manipulation['score'] > 0,
                        'emotional_intensity': emotional_score,
                        'word_count': len(full_text.split()),
                        'fear_tactics': len([t for t in tactics_found if t.get('type') == 'fear_mongering']),
                        'emotional_appeals': len([t for t in tactics_found if t.get('type') == 'emotional_manipulation']),
                        'selective_quoting': len([t for t in tactics_found if t.get('type') == 'selective_quoting']),
                        'cherry_picking': len([t for t in tactics_found if t.get('type') == 'cherry_picking'])
                    },
                    'analysis': {
                        'what_we_looked': 'AI checked for emotional manipulation, propaganda techniques, logical fallacies, selective quoting, and deceptive framing.',
                        'what_we_found': f"Integrity score: {integrity_score}/100. Detected {len(all_tactics)} manipulation technique{'s' if len(all_tactics) != 1 else ''} across {sum(1 for t in all_tactics if t.get('severity') == 'high')} high-severity, {sum(1 for t in all_tactics if t.get('severity') == 'medium')} medium-severity, and {sum(1 for t in all_tactics if t.get('severity') == 'low')} low-severity categories.",
                        'what_it_means': self._get_integrity_meaning(integrity_score, all_tactics)
                    }
                },
                'metadata': {
                    'analysis_time': time.time() - start_time,
                    'tactics_detected': len(all_tactics),
                    'analyzed_with_title': bool(title),
                    'version': '2.0',
                    'integrity_scoring': True
                }
            }
            
            # BULLETPROOF AI ENHANCEMENT
            if full_text:
                logger.info("Enhancing manipulation detection with AI insights")
                
                result = self._safely_enhance_service_result(
                    result,
                    '_ai_detect_manipulation',
                    text=full_text[:1500],
                    emotional_score=emotional_score,
                    tactics_found=[t['name'] for t in all_tactics[:5]]
                )
            
            logger.info(f"Manipulation analysis complete: Integrity {integrity_score}/100 ({level}) - {len(all_tactics)} tactics found")
            
            return result
            
        except Exception as e:
            logger.error(f"Manipulation analysis failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _detect_manipulation_tactics(self, text: str) -> List[Dict[str, Any]]:
        """Detect manipulation patterns in text - ENHANCED v2.0"""
        tactics = []
        text_lower = text.lower()
        
        for pattern_name, pattern_info in self.manipulation_patterns.items():
            found = False
            count = 0
            
            # Check keywords
            if 'keywords' in pattern_info:
                for keyword in pattern_info.get('keywords', []):
                    if keyword in text_lower:
                        count += text_lower.count(keyword)
                        found = True
            
            # Check regex patterns
            if 'patterns' in pattern_info:
                for pattern in pattern_info.get('patterns', []):
                    try:
                        matches = re.findall(pattern, text, re.IGNORECASE)
                        if matches:
                            count += len(matches)
                            found = True
                    except re.error:
                        logger.warning(f"Invalid regex pattern: {pattern}")
                        continue
            
            # Add to tactics if found
            if found and count > 0:
                tactics.append({
                    'type': pattern_name,
                    'name': pattern_info.get('name', pattern_name),
                    'severity': pattern_info.get('severity', 'medium'),
                    'description': pattern_info.get('description', ''),
                    'instances': count
                })
        
        return tactics
    
    def _detect_propaganda_techniques(self, text: str) -> List[Dict[str, Any]]:
        """Detect propaganda techniques - ENHANCED v2.0"""
        techniques = []
        text_lower = text.lower()
        
        # Card stacking - check for one-sided presentation
        positive_words = ['excellent', 'outstanding', 'perfect', 'amazing', 'wonderful', 'brilliant', 'superb', 'fantastic']
        negative_words = ['terrible', 'awful', 'disaster', 'horrible', 'catastrophic', 'dreadful', 'appalling', 'atrocious']
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        # More nuanced detection
        if (pos_count >= 4 and neg_count == 0) or (neg_count >= 4 and pos_count == 0):
            techniques.append({
                'type': 'card_stacking',
                'name': 'Card Stacking',
                'severity': 'high',
                'description': f'Presents only one side ({"positive" if pos_count > neg_count else "negative"} words: {max(pos_count, neg_count)})'
            })
        
        # Name calling - expanded
        name_calling_terms = [
            'radical', 'extremist', 'fanatic', 'conspiracy theorist', 'denier', 
            'apologist', 'shill', 'puppet', 'sellout', 'traitor', 'hack'
        ]
        name_calling_found = [term for term in name_calling_terms if term in text_lower]
        if name_calling_found:
            techniques.append({
                'type': 'name_calling',
                'name': 'Name Calling',
                'severity': 'high',
                'description': f'Uses negative labels: {", ".join(name_calling_found[:3])}'
            })
        
        # Glittering generalities - expanded
        glittering_terms = [
            'freedom', 'liberty', 'democracy', 'justice', 'patriotic', 'prosperity',
            'progress', 'hope', 'change', 'truth', 'values', 'integrity'
        ]
        glitter_count = sum(1 for term in glittering_terms if term in text_lower)
        if glitter_count >= 4:
            techniques.append({
                'type': 'glittering_generalities',
                'name': 'Glittering Generalities',
                'severity': 'medium',
                'description': f'Uses {glitter_count} vague positive terms without substance'
            })
        
        # Testimonial - celebrity/authority endorsement
        testimonial_patterns = [
            r'(?:celebrity|famous|renowned|leading) .+? (?:endorses|supports|recommends)',
            r'as .+? (?:said|stated|wrote)',
        ]
        for pattern in testimonial_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                techniques.append({
                    'type': 'testimonial',
                    'name': 'Testimonial',
                    'severity': 'low',
                    'description': 'Uses endorsements to add credibility'
                })
                break
        
        # Plain folks - appealing to common people
        if re.search(r'(?:ordinary|regular|everyday|common|working) (?:people|folks|americans|citizens)', text, re.IGNORECASE):
            techniques.append({
                'type': 'plain_folks',
                'name': 'Plain Folks',
                'severity': 'low',
                'description': 'Appeals to common people to build trust'
            })
        
        return techniques
    
    def _detect_logical_fallacies(self, text: str) -> List[Dict[str, Any]]:
        """Detect logical fallacies - ENHANCED v2.0"""
        fallacies = []
        
        # Slippery slope
        slippery_patterns = [
            r'will lead to', r'slippery slope', r'before you know it', 
            r'next thing', r'inevitable(?:ly)? result', r'domino effect'
        ]
        for pattern in slippery_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                fallacies.append({
                    'type': 'slippery_slope',
                    'name': 'Slippery Slope',
                    'severity': 'medium',
                    'description': 'Suggests one event will lead to extreme consequences'
                })
                break
        
        # Appeal to emotion - expanded
        emotion_phrases = [
            'think of the children', 'how would you feel', 'imagine if', 
            'put yourself in', 'what if it was you', 'your family could be'
        ]
        if any(phrase in text.lower() for phrase in emotion_phrases):
            fallacies.append({
                'type': 'appeal_to_emotion',
                'name': 'Appeal to Emotion',
                'severity': 'medium',
                'description': 'Manipulates emotions rather than using logic'
            })
        
        # Hasty generalization - improved
        hasty_patterns = [
            r'\b(?:all|every|none|no one) \w+ (?:is|are|do|does|believe|think)',
            r'\b(?:always|never|constantly|invariably) \w+ (?:does|is|are)',
            r'\beveryone (?:knows|agrees|believes)',
            r'\bnobody (?:thinks|believes|agrees)'
        ]
        for pattern in hasty_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                fallacies.append({
                    'type': 'hasty_generalization',
                    'name': 'Hasty Generalization',
                    'severity': 'medium',
                    'description': 'Makes broad claims from limited examples'
                })
                break
        
        # Red herring - deflection
        if re.search(r'but (?:what about|consider|look at) .+? instead', text, re.IGNORECASE):
            fallacies.append({
                'type': 'red_herring',
                'name': 'Red Herring',
                'severity': 'medium',
                'description': 'Introduces irrelevant information to distract'
            })
        
        # Circular reasoning
        if re.search(r'because .+? (?:is|are) .+?, (?:it|they) (?:is|are) .+?', text, re.IGNORECASE):
            fallacies.append({
                'type': 'circular_reasoning',
                'name': 'Circular Reasoning',
                'severity': 'medium',
                'description': 'Conclusion restates the premise'
            })
        
        # Post hoc ergo propter hoc (false cause)
        if re.search(r'after .+?, (?:therefore|thus|so) .+?', text, re.IGNORECASE):
            fallacies.append({
                'type': 'false_cause',
                'name': 'False Cause',
                'severity': 'low',
                'description': 'Assumes correlation implies causation'
            })
        
        return fallacies
    
    def _analyze_clickbait(self, title: str) -> Dict[str, Any]:
        """Analyze if title is clickbait - ENHANCED v2.0"""
        if not title:
            return {'is_clickbait': False, 'score': 0, 'reason': 'No title provided'}
        
        clickbait_score = 0
        reasons = []
        
        # Question headline
        if title.endswith('?'):
            clickbait_score += 15
            reasons.append('Question headline')
        
        # Sensational language
        sensational_terms = [
            r'you won\'t believe', r'shocking', r'amazing', r'this one trick',
            r'doctors hate', r'what happened next', r'will blow your mind',
            r'changed everything', r'secret', r'exposed'
        ]
        for term in sensational_terms:
            if re.search(term, title, re.IGNORECASE):
                clickbait_score += 25
                reasons.append('Sensational language')
                break
        
        # Listicle format
        if re.search(r'\d+ (?:things|ways|reasons|facts|tips|tricks|secrets)', title, re.IGNORECASE):
            clickbait_score += 20
            reasons.append('Listicle format')
        
        # Excessive punctuation
        if '...' in title or title.count('!') > 1 or title.count('?') > 1:
            clickbait_score += 15
            reasons.append('Excessive punctuation')
        
        # Withholding information
        withholding_terms = [
            r'what .+? (?:don\'t|doesn\'t) want you to know',
            r'the truth about',
            r'they (?:don\'t|won\'t) tell you',
            r'hidden .+? revealed'
        ]
        for term in withholding_terms:
            if re.search(term, title, re.IGNORECASE):
                clickbait_score += 20
                reasons.append('Withholds information')
                break
        
        # ALL CAPS WORDS
        caps_words = re.findall(r'\b[A-Z]{3,}\b', title)
        if len(caps_words) > 1:
            clickbait_score += 10
            reasons.append('Excessive capitalization')
        
        return {
            'is_clickbait': clickbait_score > 40,  # Lower threshold
            'score': min(100, clickbait_score),
            'reason': '; '.join(reasons) if reasons else 'No clickbait indicators'
        }
    
    def _analyze_quote_manipulation(self, text: str) -> Dict[str, Any]:
        """Analyze potential quote manipulation - NEW in v2.0"""
        score = 0
        reasons = []
        
        # Find all quoted text
        quotes = re.findall(r'["\']([^"\']{20,})["\']', text)
        
        if not quotes:
            return {'score': 0, 'reason': 'No quotes found'}
        
        # Check for partial quotes indicator
        partial_indicators = ['according to', 'said', 'stated', 'claimed']
        for quote in quotes:
            # Look for context around quote
            for indicator in partial_indicators:
                pattern = f'{indicator}[^"\']*["\'][^"\']*["\'][^"\']*(?:but|however|although)'
                if re.search(pattern, text, re.IGNORECASE):
                    score += 20
                    reasons.append('Selective quoting detected')
                    break
        
        # Check for ellipses in quotes (indicates omission)
        ellipsis_quotes = [q for q in quotes if '...' in q]
        if ellipsis_quotes:
            score += 15 * min(len(ellipsis_quotes), 3)
            reasons.append(f'{len(ellipsis_quotes)} quotes with omissions')
        
        # Check for very short quotes that might be out of context
        short_quotes = [q for q in quotes if len(q.split()) < 5]
        if len(short_quotes) > 3:
            score += 10
            reasons.append('Multiple very short quotes')
        
        # Check for negative framing of quotes
        negative_framing = [
            r'(?:even|admitted|conceded) .+? ["\']',
            r'["\'][^"\']+["\'] (?:but|however|unfortunately)'
        ]
        for pattern in negative_framing:
            if re.search(pattern, text, re.IGNORECASE):
                score += 15
                reasons.append('Negative framing of quotes')
                break
        
        return {
            'score': min(100, score),
            'reason': '; '.join(reasons) if reasons else 'No quote manipulation detected',
            'quote_count': len(quotes)
        }
    
    def _calculate_emotional_score(self, text: str) -> int:
        """Calculate emotional intensity for analysis - ENHANCED v2.0"""
        emotional_words = {
            # High intensity (3 points)
            'shocking': 3, 'devastating': 3, 'horrifying': 3, 'outrageous': 3,
            'explosive': 3, 'catastrophic': 3, 'terrifying': 3, 'stunning': 3,
            'breathtaking': 3, 'jaw-dropping': 3, 'mind-blowing': 3,
            # Medium intensity (2 points)
            'amazing': 2, 'terrible': 2, 'wonderful': 2, 'awful': 2,
            'fantastic': 2, 'horrible': 2, 'incredible': 2, 'tragic': 2,
            'heartbreaking': 2, 'inspiring': 2, 'miraculous': 2,
            # Low intensity (1 point)
            'surprising': 1, 'concerning': 1, 'interesting': 1, 'notable': 1,
            'remarkable': 1, 'significant': 1
        }
        
        text_lower = text.lower()
        word_count = len(text.split())
        
        if word_count == 0:
            return 0
        
        emotional_score = 0
        for word, weight in emotional_words.items():
            count = text_lower.count(word)
            emotional_score += count * weight
        
        # Normalize to 0-100 scale with better scaling
        score = min(100, int((emotional_score / word_count) * 300))
        
        return score
    
    def _calculate_manipulation_score(self, tactics: List, propaganda: List, 
                                    fallacies: List, clickbait: Dict, 
                                    quote_manip: Dict) -> int:
        """
        Calculate overall MANIPULATION score (0-100, higher = worse)
        This will be INVERTED to integrity score in main analyze()
        ENHANCED v2.0 with better weighting
        """
        base_score = 0
        
        # Tactics scoring with severity weighting
        for tactic in tactics:
            severity = tactic.get('severity', 'medium')
            instances = min(tactic.get('instances', 1), 5)  # Cap at 5 instances
            
            if severity == 'high':
                base_score += 12 * instances
            elif severity == 'medium':
                base_score += 7 * instances
            elif severity == 'low':
                base_score += 3 * instances
        
        # Propaganda techniques (these are serious)
        base_score += len(propaganda) * 10
        
        # Logical fallacies
        base_score += len(fallacies) * 8
        
        # Clickbait adds to manipulation
        if clickbait.get('is_clickbait', False):
            base_score += min(clickbait.get('score', 0) // 2, 15)
        
        # Quote manipulation is serious
        if quote_manip.get('score', 0) > 0:
            base_score += min(quote_manip.get('score', 0) // 3, 20)
        
        # Normalize to 0-100
        normalized_score = min(100, base_score)
        
        return normalized_score
    
    def _generate_summary(self, integrity_score: int, level: str, tactics: List[Dict]) -> str:
        """Generate a summary of manipulation findings - v2.0 with INTEGRITY perspective"""
        tactic_count = len(tactics)
        high_severity = sum(1 for t in tactics if t.get('severity') == 'high')
        
        if integrity_score >= 90:
            return f"Excellent integrity (score: {integrity_score}/100). No significant manipulation detected. Article uses straightforward language and logical arguments."
        elif integrity_score >= 80:
            return f"High integrity (score: {integrity_score}/100). Minimal manipulation detected. Article is generally straightforward with only minor concerns."
        elif integrity_score >= 60:
            tactic_names = [t['name'] for t in tactics[:2]]
            tactic_list = ', '.join(tactic_names) if tactic_names else 'minor issues'
            return f"Moderate integrity (score: {integrity_score}/100). Found {tactic_count} technique{'s' if tactic_count != 1 else ''}: {tactic_list}. Generally factual but some persuasive techniques used."
        elif integrity_score >= 40:
            tactic_names = [t['name'] for t in tactics[:3]]
            tactic_list = ', '.join(tactic_names) if tactic_names else 'various tactics'
            return f"Low integrity (score: {integrity_score}/100). Multiple manipulation tactics detected: {tactic_list}. Reader caution advised - verify claims independently."
        elif integrity_score >= 20:
            return f"Very low integrity (score: {integrity_score}/100). {tactic_count} manipulation techniques including {high_severity} high-severity issues. Significant bias and propaganda present. Highly unreliable."
        else:
            return f"Minimal integrity (score: {integrity_score}/100). Extensive manipulation detected with {tactic_count} techniques and {high_severity} severe issues. This content appears designed to manipulate rather than inform."
    
    def _get_integrity_meaning(self, integrity_score: int, tactics: List[Dict]) -> str:
        """Get user-friendly explanation of integrity score - NEW in v2.0"""
        if integrity_score >= 80:
            return "This article shows high integrity with minimal manipulation. The content is presented fairly and uses logical argumentation."
        elif integrity_score >= 60:
            return "This article has moderate integrity. While some persuasive techniques are present, they don't severely compromise the information's reliability."
        elif integrity_score >= 40:
            return "This article shows signs of manipulation. Multiple techniques are used to influence reader perception. Cross-reference claims with other sources."
        elif integrity_score >= 20:
            return "This article has low integrity with significant manipulation tactics. The content uses emotional appeals, selective presentation, and other techniques to bypass critical thinking."
        else:
            return "This article has very low integrity and appears designed primarily to manipulate. Extensive use of propaganda techniques and emotional manipulation detected. Treat with extreme skepticism."
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        info = super().get_service_info()
        info.update({
            'version': '2.0',
            'capabilities': [
                'Propaganda technique detection',
                'Logical fallacy identification',
                'Emotional manipulation analysis',
                'Clickbait detection',
                'Selective quoting detection',
                'Cherry-picking detection',
                'Whataboutism detection',
                'False authority appeals',
                'Anecdotal evidence detection',
                'Overgeneralization detection',
                'Loaded language analysis',
                'False equivalence detection',
                'Guilt by association detection',
                'Appeal to emotion detection',
                'Sensationalism detection',
                'Victimization rhetoric',
                'Us vs Them framing',
                'Quote manipulation analysis',
                'Fear mongering identification',
                'Ad hominem detection',
                'False dichotomy recognition',
                'Integrity scoring (inverted)',
                'BULLETPROOF AI-enhanced manipulation detection'
            ],
            'patterns_loaded': len(self.manipulation_patterns),
            'ai_enhanced': self._ai_available,
            'scoring_method': 'integrity_based',
            'score_interpretation': '100=high integrity (minimal manipulation), 0=low integrity (extensive manipulation)'
        })
        return info
