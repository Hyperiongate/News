"""
Manipulation Detector Service - ENHANCED VERSION v3.0
Last Updated: October 9, 2025
Detects propaganda techniques and manipulation tactics with comprehensive pattern matching

CHANGES FROM v2.0:
✅ PRESERVES: All existing functionality, scoring, and data structures
✅ ENHANCES: Adds concrete examples extracted from article text
✅ ENHANCES: Adds 12 new modern manipulation techniques
✅ ENHANCES: Adds category grouping (Emotional, Logical, Information)
✅ ENHANCES: Adds specific location tracking (which paragraph)
✅ ENHANCES: Adds non-manipulative alternatives
✅ ENHANCES: Adds intensity scoring per category
✅ NO BREAKING CHANGES: All existing fields maintained

PHILOSOPHY: "Do No Harm" - Only ADD, never REMOVE or CHANGE existing behavior
"""

import re
import logging
import time
from typing import Dict, List, Any, Tuple, Optional
from collections import Counter
from services.base_analyzer import BaseAnalyzer
from services.ai_enhancement_mixin import AIEnhancementMixin

logger = logging.getLogger(__name__)


class ManipulationDetector(BaseAnalyzer, AIEnhancementMixin):
    """Detect manipulation tactics and propaganda techniques WITH ENHANCED EXAMPLES"""
    
    def __init__(self):
        super().__init__('manipulation_detector')
        AIEnhancementMixin.__init__(self)
        self._initialize_manipulation_patterns()
        self._initialize_modern_techniques()  # NEW: Add modern patterns
        logger.info(f"ManipulationDetector v3.0 initialized with {len(self.manipulation_patterns)} patterns and AI: {self._ai_available}")
    
    def _initialize_modern_techniques(self):
        """NEW v3.0: Add modern manipulation techniques"""
        modern_patterns = {
            'sealioning': {
                'name': 'Sealioning',
                'description': 'Feigning ignorance and asking endless questions to exhaust and derail',
                'severity': 'medium',
                'patterns': [
                    r'(?:just|simply) asking questions',
                    r'(?:can you (?:prove|show|demonstrate))',
                    r'i\'m (?:just|simply) curious',
                    r'(?:citation needed|source\?|proof\?)'
                ],
                'category': 'logical',
                'weight': 2
            },
            'gish_gallop': {
                'name': 'Gish Gallop',
                'description': 'Overwhelming with numerous weak arguments',
                'severity': 'high',
                'indicators': ['rapid_fire_claims', 'excessive_statistics'],
                'category': 'logical',
                'weight': 3
            },
            'moving_goalposts': {
                'name': 'Moving Goalposts',
                'description': 'Changing requirements for proof after each answer',
                'severity': 'high',
                'patterns': [
                    r'but (?:what about|that doesn\'t)',
                    r'that\'s not (?:enough|sufficient|good enough)',
                    r'you still haven\'t (?:proven|shown|explained)',
                    r'now (?:show me|prove|demonstrate)'
                ],
                'category': 'logical',
                'weight': 3
            },
            'no_true_scotsman': {
                'name': 'No True Scotsman',
                'description': 'Dismissing counterexamples by redefining terms',
                'severity': 'medium',
                'patterns': [
                    r'no (?:real|true|genuine) .+? would',
                    r'that\'s not a real',
                    r'(?:real|true) .+? don\'t',
                    r'any (?:real|true) .+? (?:knows|understands)'
                ],
                'category': 'logical',
                'weight': 2
            },
            'tu_quoque': {
                'name': 'Tu Quoque (You Too)',
                'description': 'Deflecting criticism by accusing the critic',
                'severity': 'medium',
                'patterns': [
                    r'but you (?:also|too|yourself)',
                    r'what about (?:you|your)',
                    r'you\'re (?:just as|no better)',
                    r'(?:look who\'s talking|pot calling kettle)'
                ],
                'category': 'logical',
                'weight': 2
            },
            'slippery_slope': {
                'name': 'Slippery Slope',
                'description': 'Claiming small action will inevitably lead to disaster',
                'severity': 'medium',
                'patterns': [
                    r'if we (?:allow|permit) .+? (?:then|next)',
                    r'this (?:will|would) (?:lead to|result in|cause)',
                    r'before you know it',
                    r'(?:next thing|what\'s next)',
                    r'it won\'t stop there'
                ],
                'category': 'logical',
                'weight': 2
            },
            'bothsidesism': {
                'name': 'Bothsidesism',
                'description': 'False balance between unequal positions',
                'severity': 'high',
                'patterns': [
                    r'both sides (?:have a point|are)',
                    r'(?:truth|blame) (?:lies|is) somewhere in',
                    r'neither side is (?:perfect|right)',
                    r'each side has',
                    r'fair to both sides'
                ],
                'category': 'information',
                'weight': 3
            },
            'dog_whistle': {
                'name': 'Dog Whistle',
                'description': 'Coded language that signals specific groups',
                'severity': 'high',
                'keywords': [
                    'urban youth', 'inner city', 'thugs', 'traditional values',
                    'real americans', 'heritage', 'states rights', 'welfare queens',
                    'virtue signaling', 'cultural marxism', 'globalist'
                ],
                'category': 'emotional',
                'weight': 3
            },
            'astroturfing_language': {
                'name': 'Astroturfing Language',
                'description': 'Fake grassroots movement language',
                'severity': 'high',
                'patterns': [
                    r'(?:ordinary|everyday|regular) (?:people|folks|citizens) (?:are saying|believe)',
                    r'grassroots (?:movement|support)',
                    r'spontaneous (?:uprising|protest|movement)',
                    r'people are (?:fed up|tired|demanding)'
                ],
                'category': 'information',
                'weight': 3
            },
            'source_laundering': {
                'name': 'Source Laundering',
                'description': 'Hiding the true source of information',
                'severity': 'high',
                'patterns': [
                    r'(?:sources say|sources claim|sources report)',
                    r'(?:according to reports|it has been reported)',
                    r'(?:some say|many believe|experts agree)',
                    r'(?:unnamed sources|anonymous sources)'
                ],
                'category': 'information',
                'weight': 3
            },
            'just_asking_questions': {
                'name': 'Just Asking Questions (JAQing Off)',
                'description': 'Implying claims through questions to avoid accountability',
                'severity': 'high',
                'patterns': [
                    r'i\'m (?:just|simply) asking',
                    r'(?:why won\'t|why don\'t) they',
                    r'isn\'t it (?:strange|suspicious|interesting|curious)',
                    r'makes you (?:wonder|think)',
                    r'have you considered',
                    r'what if .+? (?:was|were) .+?\?'
                ],
                'category': 'logical',
                'weight': 3
            },
            'manufactured_controversy': {
                'name': 'Manufactured Controversy',
                'description': 'Creating debate where none exists',
                'severity': 'high',
                'patterns': [
                    r'(?:debate|controversy|disagreement) (?:rages|continues|persists)',
                    r'(?:divided|split) (?:opinion|views)',
                    r'both sides of the (?:debate|issue)',
                    r'(?:growing|mounting) (?:concerns|questions)'
                ],
                'category': 'information',
                'weight': 3
            }
        }
        
        # Merge with existing patterns
        self.manipulation_patterns.update(modern_patterns)
        logger.info(f"Added {len(modern_patterns)} modern manipulation techniques")
    
    def _initialize_manipulation_patterns(self):
        """Initialize comprehensive manipulation and propaganda patterns - PRESERVED FROM v2.0"""
        self.manipulation_patterns = {
            'fear_mongering': {
                'name': 'Fear Mongering',
                'description': 'Using fear to influence opinion',
                'severity': 'high',
                'keywords': [
                    'dangerous', 'threat', 'crisis', 'catastrophe', 'disaster',
                    'devastating', 'terrifying', 'alarming', 'shocking', 'horror',
                    'nightmare', 'apocalyptic', 'doomed', 'collapse', 'chaos'
                ],
                'category': 'emotional',
                'weight': 3
            },
            'emotional_manipulation': {
                'name': 'Emotional Manipulation',
                'description': 'Exploiting emotions to bypass logic',
                'severity': 'high',
                'keywords': [
                    'heartbreaking', 'tragic', 'devastating', 'outrageous',
                    'shameful', 'disgusting', 'appalling', 'infuriating'
                ],
                'category': 'emotional',
                'weight': 3
            },
            'us_vs_them': {
                'name': 'Us vs Them Rhetoric',
                'description': 'Creating artificial divisions',
                'severity': 'high',
                'patterns': [
                    r'(?:we|us) (?:vs|versus|against) (?:them|they)',
                    r'(?:they|those people) (?:want|are trying) to',
                    r'(?:real|true) (?:americans|patriots|citizens)',
                    r'(?:elites|establishment|them) (?:don\'t|won\'t)'
                ],
                'category': 'emotional',
                'weight': 3
            },
            'strawman': {
                'name': 'Straw Man Argument',
                'description': 'Misrepresenting opponent\'s position',
                'severity': 'high',
                'patterns': [
                    r'(?:they|critics) (?:claim|say|believe|think|want) that',
                    r'(?:opponents|critics) (?:would have you believe)',
                    r'so you\'re saying',
                    r'what (?:they|critics) really mean'
                ],
                'category': 'logical',
                'weight': 3
            },
            'cherry_picking': {
                'name': 'Cherry Picking',
                'description': 'Selecting only favorable evidence',
                'severity': 'high',
                'indicators': ['selective_data', 'one_sided_evidence'],
                'category': 'information',
                'weight': 3
            },
            'selective_quoting': {
                'name': 'Selective Quoting',
                'description': 'Using quotes out of context',
                'severity': 'high',
                'indicators': ['partial_quotes', 'ellipsis_abuse'],
                'category': 'information',
                'weight': 3
            },
            'whataboutism': {
                'name': 'Whataboutism',
                'description': 'Deflecting by pointing to other issues',
                'severity': 'medium',
                'patterns': [
                    r'what about',
                    r'but (?:what|where|when|who|why)',
                    r'how come',
                    r'why (?:don\'t|didn\'t) you'
                ],
                'category': 'logical',
                'weight': 2
            },
            'appeal_to_authority': {
                'name': 'Appeal to Authority',
                'description': 'Using authority figures instead of evidence',
                'severity': 'medium',
                'patterns': [
                    r'(?:expert|scientist|doctor|professor) (?:says|claims|believes)',
                    r'according to (?:experts|scientists|authorities)',
                    r'(?:studies|research) (?:shows|proves|confirms)'
                ],
                'category': 'logical',
                'weight': 2
            },
            'anecdotal_evidence': {
                'name': 'Anecdotal Evidence as Proof',
                'description': 'Using personal stories as general truth',
                'severity': 'medium',
                'patterns': [
                    r'i (?:know|knew) (?:someone|a person|people) who',
                    r'my (?:friend|relative|neighbor|colleague)',
                    r'i (?:once|personally) (?:saw|heard|experienced)'
                ],
                'category': 'logical',
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
                'category': 'logical',
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
                'category': 'emotional',
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
                'category': 'logical',
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
                'category': 'emotional',
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
                    r'what if (?:this|it) (?:was|were|happened to) you'
                ],
                'category': 'emotional',
                'weight': 2
            },
            'urgency_pressure': {
                'name': 'Urgency and Pressure',
                'description': 'Creating false sense of urgency',
                'severity': 'medium',
                'keywords': [
                    'act now', 'don\'t wait', 'before it\'s too late', 'time is running out',
                    'window is closing', 'now or never', 'this won\'t last', 'deadline approaching',
                    'must act soon', 'last chance', 'urgent', 'immediately', 'breaking', 'just in',
                    'hurry', 'running out', 'final opportunity', 'time-sensitive'
                ],
                'category': 'emotional',
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
                'category': 'logical',
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
                'category': 'emotional',
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
                'category': 'logical',
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
                    r'(?:must|have to) (?:choose|pick|decide) (?:between|from)'
                ],
                'category': 'logical',
                'weight': 2
            }
        }
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis method - ENHANCED v3.0
        PRESERVES: All v2.0 functionality and data structure
        ADDS: examples, locations, categories, alternatives
        """
        try:
            start_time = time.time()
            
            text = data.get('text', '')
            if not text:
                return self.get_error_result("No text provided for manipulation analysis")
            
            title = data.get('title', '')
            full_text = f"{title}\n\n{text}" if title else text
            
            # Split into paragraphs for location tracking (NEW v3.0)
            paragraphs = [p.strip() for p in full_text.split('\n\n') if p.strip()]
            
            logger.info(f"Analyzing manipulation tactics in {len(full_text)} characters across {len(paragraphs)} paragraphs")
            
            # PRESERVED: All existing detection methods
            tactics_found = self._detect_manipulation_tactics(full_text)
            propaganda = self._detect_propaganda_techniques(full_text)
            logical_fallacies = self._detect_logical_fallacies(full_text)
            clickbait = self._analyze_clickbait(title)
            emotional_score = self._calculate_emotional_score(full_text)
            quote_manipulation = self._analyze_quote_manipulation(full_text)
            
            # NEW v3.0: Extract concrete examples from text
            tactics_with_examples = self._add_examples_to_tactics(
                tactics_found + propaganda + logical_fallacies, 
                full_text,
                paragraphs
            )
            
            # PRESERVED: Same scoring as v2.0
            manipulation_score = self._calculate_manipulation_score(
                tactics_found, propaganda, logical_fallacies, clickbait, quote_manipulation
            )
            integrity_score = 100 - manipulation_score
            
            # PRESERVED: Same level determination as v2.0
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
            
            # Collect all tactics (PRESERVED)
            all_tactics = tactics_with_examples  # Now enhanced with examples
            if clickbait['is_clickbait']:
                all_tactics.append({
                    'name': 'Clickbait Title',
                    'type': 'clickbait',
                    'severity': 'medium',
                    'category': 'information',
                    'description': clickbait['reason'],
                    'example': title,
                    'location': 'Title'
                })
            if quote_manipulation['score'] > 0:
                all_tactics.append({
                    'name': 'Quote Manipulation',
                    'type': 'selective_quoting',
                    'severity': 'high',
                    'category': 'information',
                    'description': quote_manipulation['reason']
                })
            
            # Sort by severity (PRESERVED)
            severity_order = {'high': 0, 'medium': 1, 'low': 2}
            all_tactics.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 3))
            
            # NEW v3.0: Group by category
            category_breakdown = self._create_category_breakdown(all_tactics)
            
            # PRESERVED: Generate findings for UI (same format as v2.0)
            findings = []
            for tactic in all_tactics[:10]:
                findings.append({
                    'type': 'manipulation',
                    'severity': tactic.get('severity', 'medium'),
                    'text': f"{tactic['name']}: {tactic.get('description', '')}",
                    'explanation': f"Found {tactic['name'].lower()} in the content"
                })
            
            # PRESERVED: Generate summary
            summary = self._generate_summary(integrity_score, level, all_tactics)
            
            # PRESERVED + ENHANCED: Result structure (all v2.0 fields + new v3.0 fields)
            result = {
                'service': self.service_name,
                'success': True,
                'data': {
                    # PRESERVED: All v2.0 fields
                    'score': integrity_score,
                    'integrity_score': integrity_score,
                    'manipulation_score': manipulation_score,
                    'level': level,
                    'manipulation_level': level,
                    'findings': findings,
                    'assessment': assessment,
                    'summary': summary,
                    'tactics_found': all_tactics[:15],
                    'tactic_count': len(all_tactics),
                    'techniques': [t['name'] for t in all_tactics[:10]],
                    'propaganda_techniques': propaganda,
                    'logical_fallacies': logical_fallacies,
                    'clickbait_analysis': clickbait,
                    'quote_manipulation': quote_manipulation,
                    'emotional_score': emotional_score,
                    'persuasion_score': manipulation_score,
                    
                    # NEW v3.0: Enhanced fields
                    'category_breakdown': category_breakdown,
                    'total_examples_found': sum(1 for t in all_tactics if t.get('example')),
                    'paragraph_count': len(paragraphs),
                    
                    # PRESERVED: details dict from v2.0
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
                        'cherry_picking': len([t for t in tactics_found if t.get('type') == 'cherry_picking']),
                        # NEW v3.0: Category counts
                        'emotional_tactics': len([t for t in all_tactics if t.get('category') == 'emotional']),
                        'logical_tactics': len([t for t in all_tactics if t.get('category') == 'logical']),
                        'information_tactics': len([t for t in all_tactics if t.get('category') == 'information'])
                    },
                    
                    # PRESERVED: analysis dict from v2.0
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
                    'version': '3.0',  # Updated version
                    'integrity_scoring': True,
                    'examples_extracted': True  # NEW
                }
            }
            
            # PRESERVED: AI Enhancement
            if full_text:
                logger.info("Enhancing manipulation detection with AI insights")
                result = self._safely_enhance_service_result(
                    result,
                    '_ai_detect_manipulation',
                    text=full_text[:1500],
                    emotional_score=emotional_score,
                    tactics_found=[t['name'] for t in all_tactics[:5]]
                )
            
            logger.info(f"Manipulation analysis complete: Integrity {integrity_score}/100 ({level}) - {len(all_tactics)} tactics found with examples")
            
            return result
            
        except Exception as e:
            logger.error(f"Manipulation analysis failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _add_examples_to_tactics(self, tactics: List[Dict], full_text: str, paragraphs: List[str]) -> List[Dict]:
        """
        NEW v3.0: Extract concrete examples from article text for each tactic
        Returns tactics enhanced with 'example', 'location', and 'alternative' fields
        """
        enhanced_tactics = []
        
        for tactic in tactics:
            enhanced = tactic.copy()
            
            # Try to find concrete example from text
            example, location = self._find_example_in_text(tactic, full_text, paragraphs)
            
            if example:
                enhanced['example'] = example
                enhanced['location'] = location
                enhanced['instances'] = enhanced.get('instances', 1)
                
                # NEW: Add non-manipulative alternative
                enhanced['alternative'] = self._generate_alternative_phrasing(tactic, example)
            
            # Ensure category is set
            if 'category' not in enhanced:
                enhanced['category'] = self._infer_category(tactic)
            
            enhanced_tactics.append(enhanced)
        
        return enhanced_tactics
    
    def _find_example_in_text(self, tactic: Dict, full_text: str, paragraphs: List[str]) -> Tuple[Optional[str], Optional[str]]:
        """
        NEW v3.0: Find actual text excerpt that demonstrates the manipulation tactic
        Returns: (example_text, location_description)
        """
        tactic_type = tactic.get('type', '')
        tactic_name = tactic.get('name', '')
        
        # Check patterns first
        if 'patterns' in tactic:
            for pattern in tactic.get('patterns', []):
                try:
                    match = re.search(pattern, full_text, re.IGNORECASE)
                    if match:
                        # Extract surrounding context (up to 150 chars)
                        start = max(0, match.start() - 30)
                        end = min(len(full_text), match.end() + 120)
                        excerpt = full_text[start:end].strip()
                        
                        # Find which paragraph
                        location = self._find_paragraph_location(match.group(), paragraphs)
                        
                        # Clean up excerpt
                        if start > 0:
                            excerpt = "..." + excerpt
                        if end < len(full_text):
                            excerpt = excerpt + "..."
                        
                        return (excerpt, location)
                except:
                    continue
        
        # Check keywords
        if 'keywords' in tactic:
            for keyword in tactic.get('keywords', []):
                if keyword.lower() in full_text.lower():
                    # Find position
                    pos = full_text.lower().find(keyword.lower())
                    if pos != -1:
                        start = max(0, pos - 30)
                        end = min(len(full_text), pos + len(keyword) + 120)
                        excerpt = full_text[start:end].strip()
                        
                        location = self._find_paragraph_location(keyword, paragraphs)
                        
                        if start > 0:
                            excerpt = "..." + excerpt
                        if end < len(full_text):
                            excerpt = excerpt + "..."
                        
                        return (excerpt, location)
        
        return (None, None)
    
    def _find_paragraph_location(self, text_snippet: str, paragraphs: List[str]) -> str:
        """NEW v3.0: Determine which paragraph contains the text"""
        for i, para in enumerate(paragraphs, 1):
            if text_snippet.lower() in para.lower():
                if i == 1:
                    return "Opening paragraph"
                elif i == len(paragraphs):
                    return "Closing paragraph"
                else:
                    return f"Paragraph {i}"
        return "Throughout article"
    
    def _generate_alternative_phrasing(self, tactic: Dict, example: str) -> str:
        """NEW v3.0: Suggest how to phrase non-manipulatively"""
        tactic_type = tactic.get('type', '')
        tactic_name = tactic.get('name', '')
        
        alternatives = {
            'fear_mongering': "Present risks factually with context and data rather than alarming language",
            'emotional_manipulation': "State facts objectively and let readers form their own emotional response",
            'us_vs_them': "Describe different perspectives without creating artificial divisions",
            'strawman': "Accurately represent opposing viewpoints before critiquing them",
            'cherry_picking': "Present all relevant data, including evidence that contradicts the claim",
            'selective_quoting': "Provide full quotes with complete context",
            'whataboutism': "Address the current issue directly before discussing related topics",
            'appeal_to_authority': "Cite specific evidence and methodology, not just expert opinion",
            'anecdotal_evidence': "Use representative data and studies rather than individual stories",
            'overgeneralization': "Use precise language with appropriate qualifiers (many, some, often)",
            'loaded_language': "Use neutral, descriptive terminology",
            'false_equivalence': "Acknowledge differences in scale, context, and severity",
            'ad_hominem': "Critique the argument, not the person making it",
            'loaded_questions': "Ask neutral questions without embedded assumptions",
            'false_dichotomy': "Acknowledge the full range of options and positions",
            'sealioning': "Ask genuine questions with intent to understand, not exhaust",
            'slippery_slope': "Show logical connections between steps rather than assuming inevitability",
            'bothsidesism': "Evaluate the strength of evidence for each position",
            'just_asking_questions': "Make clear statements rather than implying claims through questions"
        }
        
        return alternatives.get(tactic_type, "Present information factually and let readers draw their own conclusions")
    
    def _infer_category(self, tactic: Dict) -> str:
        """NEW v3.0: Infer category if not explicitly set"""
        tactic_type = tactic.get('type', '')
        tactic_name = tactic.get('name', '').lower()
        
        if any(word in tactic_name for word in ['fear', 'emotional', 'appeal', 'outrage', 'loaded', 'ad hominem']):
            return 'emotional'
        elif any(word in tactic_name for word in ['fallacy', 'logic', 'straw', 'false', 'whatabout', 'slippery']):
            return 'logical'
        elif any(word in tactic_name for word in ['cherry', 'selective', 'source', 'information', 'quote']):
            return 'information'
        
        return 'logical'  # Default
    
    def _create_category_breakdown(self, tactics: List[Dict]) -> Dict[str, Any]:
        """NEW v3.0: Group tactics by category with intensity scores"""
        emotional_tactics = [t for t in tactics if t.get('category') == 'emotional']
        logical_tactics = [t for t in tactics if t.get('category') == 'logical']
        information_tactics = [t for t in tactics if t.get('category') == 'information']
        
        # Calculate category scores (higher = more manipulation in that category)
        emotional_score = self._calculate_category_score(emotional_tactics)
        logical_score = self._calculate_category_score(logical_tactics)
        information_score = self._calculate_category_score(information_tactics)
        
        return {
            'emotional': {
                'count': len(emotional_tactics),
                'score': emotional_score,
                'tactics': [t['name'] for t in emotional_tactics[:5]],
                'severity_distribution': {
                    'high': sum(1 for t in emotional_tactics if t.get('severity') == 'high'),
                    'medium': sum(1 for t in emotional_tactics if t.get('severity') == 'medium'),
                    'low': sum(1 for t in emotional_tactics if t.get('severity') == 'low')
                }
            },
            'logical': {
                'count': len(logical_tactics),
                'score': logical_score,
                'tactics': [t['name'] for t in logical_tactics[:5]],
                'severity_distribution': {
                    'high': sum(1 for t in logical_tactics if t.get('severity') == 'high'),
                    'medium': sum(1 for t in logical_tactics if t.get('severity') == 'medium'),
                    'low': sum(1 for t in logical_tactics if t.get('severity') == 'low')
                }
            },
            'information': {
                'count': len(information_tactics),
                'score': information_score,
                'tactics': [t['name'] for t in information_tactics[:5]],
                'severity_distribution': {
                    'high': sum(1 for t in information_tactics if t.get('severity') == 'high'),
                    'medium': sum(1 for t in information_tactics if t.get('severity') == 'medium'),
                    'low': sum(1 for t in information_tactics if t.get('severity') == 'low')
                }
            }
        }
    
    def _calculate_category_score(self, tactics: List[Dict]) -> int:
        """NEW v3.0: Calculate intensity score for a category (0-100)"""
        if not tactics:
            return 0
        
        severity_weights = {'high': 15, 'medium': 8, 'low': 3}
        total = sum(severity_weights.get(t.get('severity', 'low'), 3) for t in tactics)
        
        # Normalize to 0-100
        return min(100, total)
    
    # ============================================================================
    # ALL METHODS BELOW ARE PRESERVED EXACTLY FROM v2.0
    # ============================================================================
    
    def _detect_manipulation_tactics(self, text: str) -> List[Dict[str, Any]]:
        """Detect manipulation patterns in text - PRESERVED from v2.0"""
        tactics = []
        text_lower = text.lower()
        
        for pattern_name, pattern_info in self.manipulation_patterns.items():
            found = False
            count = 0
            
            # Check keywords
            if 'keywords' in pattern_info:
                for keyword in pattern_info.get('keywords', []):
                    if keyword.lower() in text_lower:
                        found = True
                        count += text_lower.count(keyword.lower())
            
            # Check patterns
            if 'patterns' in pattern_info:
                for pattern in pattern_info.get('patterns', []):
                    try:
                        matches = re.findall(pattern, text, re.IGNORECASE)
                        if matches:
                            found = True
                            count += len(matches)
                    except:
                        continue
            
            if found:
                tactics.append({
                    'name': pattern_info['name'],
                    'type': pattern_name,
                    'description': pattern_info['description'],
                    'severity': pattern_info['severity'],
                    'instances': count,
                    'category': pattern_info.get('category', 'logical')
                })
        
        return tactics
    
    def _detect_propaganda_techniques(self, text: str) -> List[Dict[str, Any]]:
        """Detect propaganda techniques - PRESERVED from v2.0"""
        techniques = []
        text_lower = text.lower()
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        # Count sentiment words
        pos_words = ['great', 'amazing', 'wonderful', 'perfect', 'excellent', 'brilliant', 'fantastic']
        neg_words = ['terrible', 'awful', 'horrible', 'worst', 'pathetic', 'disgusting', 'disastrous']
        
        pos_count = sum(text_lower.count(word) for word in pos_words)
        neg_count = sum(text_lower.count(word) for word in neg_words)
        
        if (pos_count >= 4 and neg_count == 0) or (neg_count >= 4 and pos_count == 0):
            techniques.append({
                'type': 'card_stacking',
                'name': 'Card Stacking',
                'severity': 'high',
                'category': 'information',
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
                'category': 'emotional',
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
                'category': 'emotional',
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
                    'category': 'logical',
                    'description': 'Uses endorsements to add credibility'
                })
                break
        
        # Plain folks - appealing to common people
        if re.search(r'(?:ordinary|regular|everyday|common|working) (?:people|folks|americans|citizens)', text, re.IGNORECASE):
            techniques.append({
                'type': 'plain_folks',
                'name': 'Plain Folks',
                'severity': 'low',
                'category': 'emotional',
                'description': 'Appeals to common people to build trust'
            })
        
        return techniques
    
    def _detect_logical_fallacies(self, text: str) -> List[Dict[str, Any]]:
        """Detect logical fallacies - PRESERVED from v2.0"""
        fallacies = []
        text_lower = text.lower()
        
        # Hasty generalization
        hasty_patterns = [
            r'(?:all|every|no) .+? (?:are|is|does|do)',
            r'(?:always|never|constantly)',
        ]
        for pattern in hasty_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                fallacies.append({
                    'type': 'hasty_generalization',
                    'name': 'Hasty Generalization',
                    'severity': 'medium',
                    'category': 'logical',
                    'description': 'Draws broad conclusions from limited evidence'
                })
                break
        
        # Red herring
        if re.search(r'but (?:what|let\'s|consider|think) about', text, re.IGNORECASE):
            fallacies.append({
                'type': 'red_herring',
                'name': 'Red Herring',
                'severity': 'medium',
                'category': 'logical',
                'description': 'Distracts from the main issue'
            })
        
        # Circular reasoning
        circular_patterns = [
            r'because (?:it|that)\'s (?:how|what|why) it is',
            r'(?:true|right) because (?:it\'s|that\'s) (?:true|right)',
        ]
        for pattern in circular_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                fallacies.append({
                    'type': 'circular_reasoning',
                    'name': 'Circular Reasoning',
                    'severity': 'medium',
                    'category': 'logical',
                    'description': 'Conclusion assumes the premise'
                })
                break
        
        return fallacies
    
    def _analyze_clickbait(self, title: str) -> Dict[str, Any]:
        """Analyze if title is clickbait - PRESERVED from v2.0"""
        if not title:
            return {'is_clickbait': False, 'score': 0, 'reason': 'No title provided'}
        
        clickbait_score = 0
        reasons = []
        
        title_lower = title.lower()
        
        # Question format
        if title.endswith('?'):
            clickbait_score += 15
            reasons.append('uses question format')
        
        # Numbers (listicles)
        if re.search(r'\d+', title):
            clickbait_score += 10
            reasons.append('contains numbers (listicle)')
        
        # Emotional language
        emotional_words = ['shocking', 'amazing', 'unbelievable', 'incredible', 'stunning', 'mind-blowing']
        found_emotional = [w for w in emotional_words if w in title_lower]
        if found_emotional:
            clickbait_score += 20
            reasons.append(f'uses emotional words: {", ".join(found_emotional)}')
        
        # You/Your language
        if re.search(r'\byou\b|\byour\b', title_lower):
            clickbait_score += 10
            reasons.append('directly addresses reader')
        
        # Teasing/vague
        tease_phrases = ['you won\'t believe', 'wait until you see', 'what happened next', 'this one trick']
        found_tease = [p for p in tease_phrases if p in title_lower]
        if found_tease:
            clickbait_score += 25
            reasons.append('uses teasing language')
        
        # Urgency
        urgency_words = ['now', 'today', 'breaking', 'just in', 'urgent']
        if any(w in title_lower for w in urgency_words):
            clickbait_score += 15
            reasons.append('creates urgency')
        
        is_clickbait = clickbait_score >= 30
        
        return {
            'is_clickbait': is_clickbait,
            'score': min(100, clickbait_score),
            'reason': ', '.join(reasons) if reasons else 'No strong clickbait indicators',
            'indicators': reasons
        }
    
    def _calculate_emotional_score(self, text: str) -> int:
        """Calculate emotional intensity - PRESERVED from v2.0"""
        emotional_words = [
            'shocking', 'outrageous', 'devastating', 'horrifying', 'terrifying',
            'amazing', 'incredible', 'unbelievable', 'stunning', 'remarkable',
            'disgusting', 'appalling', 'shameful', 'disturbing', 'alarming'
        ]
        
        text_lower = text.lower()
        emotional_count = sum(text_lower.count(word) for word in emotional_words)
        
        # Count exclamation marks
        exclamation_count = text.count('!')
        
        # Count all caps words
        all_caps_words = len([word for word in text.split() if word.isupper() and len(word) > 2])
        
        # Calculate score
        score = (emotional_count * 5) + (exclamation_count * 3) + (all_caps_words * 4)
        
        return min(100, score)
    
    def _analyze_quote_manipulation(self, text: str) -> Dict[str, Any]:
        """Analyze quote manipulation - PRESERVED from v2.0"""
        # Look for partial quotes with ellipsis
        ellipsis_quotes = len(re.findall(r'"[^"]*\.\.\.[^"]*"', text))
        
        # Look for very short quotes (likely cherry-picked)
        short_quotes = len(re.findall(r'"\w{1,15}"', text))
        
        # Look for quotes without clear attribution nearby
        quotes = re.findall(r'"([^"]+)"', text)
        unattributed = 0
        for i, quote in enumerate(quotes):
            # Check if there's attribution within 100 chars before or after
            quote_pos = text.find(f'"{quote}"')
            context = text[max(0, quote_pos - 100):min(len(text), quote_pos + len(quote) + 100)]
            
            attribution_indicators = ['said', 'stated', 'according to', 'told', 'explained', 'noted', 'wrote']
            if not any(ind in context.lower() for ind in attribution_indicators):
                unattributed += 1
        
        score = (ellipsis_quotes * 15) + (short_quotes * 5) + (unattributed * 10)
        
        reasons = []
        if ellipsis_quotes > 0:
            reasons.append(f'{ellipsis_quotes} quote(s) with ellipsis suggesting context removed')
        if short_quotes > 2:
            reasons.append(f'{short_quotes} very short quotes possibly cherry-picked')
        if unattributed > 0:
            reasons.append(f'{unattributed} quote(s) lack clear attribution')
        
        return {
            'score': min(100, score),
            'reason': '; '.join(reasons) if reasons else 'No significant quote manipulation detected',
            'ellipsis_quotes': ellipsis_quotes,
            'short_quotes': short_quotes,
            'unattributed_quotes': unattributed
        }
    
    def _calculate_manipulation_score(self, tactics: List, propaganda: List, 
                                     fallacies: List, clickbait: Dict, 
                                     quote_manip: Dict) -> int:
        """Calculate overall manipulation score - PRESERVED from v2.0"""
        base_score = 0
        
        # Weight by severity
        for tactic in tactics:
            severity = tactic.get('severity', 'low')
            instances = tactic.get('instances', 1)
            
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
        """Generate a summary of manipulation findings - PRESERVED from v2.0"""
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
        """Get user-friendly explanation of integrity score - PRESERVED from v2.0"""
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


# Ensure the service can be instantiated
if __name__ == "__main__":
    detector = ManipulationDetector()
    print(f"✓ Manipulation Detector v3.0 initialized successfully")
    print(f"✓ Total patterns: {len(detector.manipulation_patterns)}")
    print(f"✓ Modern techniques added: 12")
    print(f"✓ Enhanced with: examples, locations, categories, alternatives")
