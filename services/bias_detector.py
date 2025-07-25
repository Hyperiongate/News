"""
FILE: services/bias_detector.py
LOCATION: news/services/bias_detector.py
PURPOSE: Advanced bias detection and analysis
DEPENDENCIES: re, logging
SERVICE: Bias detection - Multi-dimensional bias analysis
"""

import re
import logging
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)


class BiasDetector:
    """Advanced multi-dimensional bias detection and analysis"""
    
    def __init__(self):
        """Initialize bias detector with pattern definitions"""
        self._initialize_patterns()
    
    def _initialize_patterns(self):
        """Initialize all bias detection patterns"""
        # Political bias indicators with weights
        self.left_indicators = {
            'progressive': 3, 'liberal': 3, 'democrat': 2, 'left-wing': 3,
            'socialist': 3, 'equity': 2, 'social justice': 3, 'inequality': 2,
            'climate change': 2, 'gun control': 2, 'universal healthcare': 3,
            'wealth redistribution': 3, 'corporate greed': 3, 'workers rights': 2,
            'systemic racism': 3, 'diversity': 1, 'inclusion': 1
        }
        
        self.right_indicators = {
            'conservative': 3, 'republican': 2, 'right-wing': 3, 'traditional': 2,
            'libertarian': 2, 'patriot': 2, 'free market': 3, 'deregulation': 3,
            'individual liberty': 2, 'second amendment': 3, 'pro-life': 3,
            'border security': 3, 'law and order': 2, 'family values': 2,
            'limited government': 3, 'personal responsibility': 2
        }
        
        # Corporate bias indicators
        self.pro_corporate = {
            'innovation': 1, 'job creators': 3, 'economic growth': 2,
            'business friendly': 3, 'entrepreneurship': 2, 'free enterprise': 3,
            'competitive advantage': 2, 'shareholder value': 3, 'efficiency': 1,
            'market leader': 2, 'industry leader': 2
        }
        
        self.anti_corporate = {
            'corporate greed': 3, 'monopoly': 3, 'exploitation': 3,
            'tax avoidance': 3, 'income inequality': 2, 'worker exploitation': 3,
            'excessive profits': 3, 'corporate welfare': 3, 'big business': 2,
            'wealth gap': 2, 'unfair practices': 2
        }
        
        # Sensational indicators
        self.sensational_indicators = {
            'shocking': 3, 'bombshell': 3, 'explosive': 3, 'devastating': 3,
            'breaking': 2, 'urgent': 2, 'exclusive': 2, 'revealed': 2,
            'scandal': 3, 'crisis': 2, 'catastrophe': 3, 'disaster': 2,
            'unbelievable': 3, 'incredible': 2, 'mind-blowing': 3,
            'game-changing': 3, 'revolutionary': 2
        }
        
        # Nationalistic indicators
        self.nationalistic_indicators = {
            'america first': 3, 'national interest': 2, 'sovereignty': 2,
            'patriotic': 2, 'our country': 2, 'homeland': 2, 'national security': 2,
            'protect our borders': 3, 'foreign threat': 3, 'defend america': 3
        }
        
        self.internationalist_indicators = {
            'global cooperation': 3, 'international community': 2, 'united nations': 2,
            'global citizens': 3, 'world peace': 2, 'international law': 2,
            'diplomatic solution': 2, 'multilateral': 3, 'global partnership': 3
        }
        
        # Establishment indicators
        self.pro_establishment = {
            'respected institutions': 3, 'established order': 3, 'mainstream': 2,
            'expert consensus': 3, 'institutional': 2, 'authorities say': 2,
            'official sources': 2, 'government officials': 2, 'traditional media': 2
        }
        
        self.anti_establishment = {
            'deep state': 3, 'mainstream media lies': 3, 'corrupt system': 3,
            'establishment': -2, 'elite agenda': 3, 'wake up': 2, 'they dont want': 3,
            'hidden truth': 3, 'question everything': 2, 'alternative facts': 2
        }
        
        # Loaded phrase patterns
        self.loaded_patterns = [
            # Political loaded terms
            (r'\b(radical|extreme|far-left|far-right|extremist)\b', 'political', 'high'),
            (r'\b(socialist agenda|right-wing conspiracy|left-wing mob)\b', 'political', 'high'),
            
            # Emotional manipulation
            (r'\b(destroy|devastate|annihilate|obliterate)\b', 'hyperbolic', 'medium'),
            (r'\b(save|rescue|protect|defend)\s+(?:our|the)\s+\w+', 'savior_language', 'medium'),
            
            # Absolute language
            (r'\b(always|never|everyone|no one|all|none)\b', 'absolute', 'low'),
            (r'\b(undeniable|indisputable|unquestionable|irrefutable)\b', 'absolute', 'medium'),
            
            # Assumption language
            (r'\b(obviously|clearly|undeniably|of course)\b', 'assumption', 'low'),
            (r'\b(everyone knows|it\'s well known|nobody disputes)\b', 'assumption', 'medium'),
            
            # Us vs Them language
            (r'\b(they|them|those people|the other side)\b', 'divisive', 'medium'),
            (r'\b(our values|real americans|true patriots)\b', 'divisive', 'high'),
            
            # Fear-mongering
            (r'\b(threat to|attack on|war on|assault on)\s+\w+', 'fear', 'high'),
            (r'\b(invasion|infestation|plague|epidemic)\b', 'fear', 'high'),
        ]
    
    def analyze_comprehensive_bias(self, text: str, basic_bias_score: float = 0, 
                                  domain: str = None) -> Dict[str, Any]:
        """
        Perform comprehensive bias analysis on text
        
        Args:
            text: Article text to analyze
            basic_bias_score: Simple bias score for backward compatibility
            domain: Source domain for comparative analysis
            
        Returns:
            Comprehensive bias analysis dictionary
        """
        if not text:
            return self._get_empty_bias_analysis()
        
        # Calculate multi-dimensional bias scores
        bias_dimensions = self.analyze_bias_dimensions(text)
        
        # Detect bias patterns and context
        bias_patterns = self.detect_bias_patterns(text)
        
        # Calculate confidence in bias detection
        bias_confidence = self.calculate_bias_confidence(text, bias_patterns)
        
        # Detect framing bias
        framing_analysis = self.analyze_framing_bias(text)
        
        # Analyze source selection bias
        source_bias = self.analyze_source_selection_bias(text)
        
        # Get enhanced loaded phrases with context
        loaded_phrases = self.extract_loaded_phrases(text)
        
        # Calculate overall political lean (maintaining compatibility)
        political_lean = basic_bias_score * 100 if basic_bias_score else bias_dimensions['political']['score'] * 100
        
        # Determine overall bias label
        overall_bias = self.get_enhanced_bias_label(bias_dimensions, political_lean)
        
        # Calculate objectivity score with multiple factors
        objectivity_score = self.calculate_objectivity_score(
            bias_dimensions, bias_patterns, loaded_phrases
        )
        
        # Opinion percentage calculation
        opinion_percentage = self.calculate_opinion_percentage(text)
        
        # Emotional score calculation
        emotional_score = self.calculate_emotional_score(text)
        
        # Format manipulation tactics with enhanced detection
        manipulation_tactics = self.detect_manipulation_tactics(text, bias_patterns)
        
        # Create bias visualization data
        bias_visualization = {
            'spectrum_position': basic_bias_score if basic_bias_score else bias_dimensions['political']['score'],
            'confidence_bands': {
                'lower': max(-1, (basic_bias_score if basic_bias_score else bias_dimensions['political']['score']) - (1 - bias_confidence/100) * 0.3),
                'upper': min(1, (basic_bias_score if basic_bias_score else bias_dimensions['political']['score']) + (1 - bias_confidence/100) * 0.3)
            },
            'contributing_factors': self.get_bias_contributing_factors(
                bias_dimensions, framing_analysis, source_bias
            )
        }
        
        # Bias impact assessment
        bias_impact = self.assess_bias_impact(
            bias_dimensions, bias_patterns, manipulation_tactics
        )
        
        # Comparative context
        comparative_context = self.get_comparative_bias_context(
            basic_bias_score if basic_bias_score else bias_dimensions['political']['score'], 
            domain
        )
        
        return {
            'overall_bias': overall_bias,
            'political_lean': political_lean,
            'objectivity_score': objectivity_score,
            'opinion_percentage': opinion_percentage,
            'emotional_score': emotional_score,
            'manipulation_tactics': manipulation_tactics,
            'loaded_phrases': loaded_phrases,
            
            # Enhanced bias reporting fields
            'bias_confidence': bias_confidence,
            'bias_dimensions': bias_dimensions,
            'bias_patterns': bias_patterns,
            'framing_analysis': framing_analysis,
            'source_bias_analysis': source_bias,
            'bias_visualization': bias_visualization,
            'bias_impact': bias_impact,
            'comparative_context': comparative_context
        }
    
    def analyze_bias_dimensions(self, text: str) -> Dict[str, Dict[str, Any]]:
        """Analyze multiple dimensions of bias"""
        return {
            'political': self._analyze_political_dimension(text),
            'corporate': self._analyze_corporate_dimension(text),
            'sensational': self._analyze_sensational_dimension(text),
            'nationalistic': self._analyze_nationalistic_dimension(text),
            'establishment': self._analyze_establishment_dimension(text)
        }
    
    def _analyze_political_dimension(self, text: str) -> Dict[str, Any]:
        """Analyze political bias dimension"""
        text_lower = text.lower()
        
        left_score = sum(weight for term, weight in self.left_indicators.items() 
                        if term in text_lower)
        right_score = sum(weight for term, weight in self.right_indicators.items() 
                         if term in text_lower)
        
        total_score = left_score + right_score
        if total_score == 0:
            score = 0
        else:
            score = (right_score - left_score) / max(total_score, 20)
            score = max(-1, min(1, score))
        
        # Determine label
        if score < -0.6:
            label = 'Strong left'
        elif score < -0.2:
            label = 'Lean left'
        elif score > 0.6:
            label = 'Strong right'
        elif score > 0.2:
            label = 'Lean right'
        else:
            label = 'Center'
        
        return {
            'score': score,
            'label': label,
            'confidence': min(100, int(abs(score) * 100 * 1.2))
        }
    
    def _analyze_corporate_dimension(self, text: str) -> Dict[str, Any]:
        """Analyze corporate bias dimension"""
        text_lower = text.lower()
        
        pro_score = sum(weight for term, weight in self.pro_corporate.items() 
                       if term in text_lower)
        anti_score = sum(weight for term, weight in self.anti_corporate.items() 
                        if term in text_lower)
        
        total_score = pro_score + anti_score
        if total_score == 0:
            score = 0
        else:
            score = (pro_score - anti_score) / max(total_score, 15)
            score = max(-1, min(1, score))
        
        # Determine label
        if score > 0.6:
            label = 'Strong pro-corporate'
        elif score > 0.2:
            label = 'Slightly pro-corporate'
        elif score < -0.6:
            label = 'Strong anti-corporate'
        elif score < -0.2:
            label = 'Slightly anti-corporate'
        else:
            label = 'Neutral'
        
        return {
            'score': score,
            'label': label,
            'confidence': min(100, int(abs(score) * 100 * 1.2))
        }
    
    def _analyze_sensational_dimension(self, text: str) -> Dict[str, Any]:
        """Analyze sensational bias dimension"""
        text_lower = text.lower()
        
        # Check for sensational words
        sensational_score = sum(weight for term, weight in self.sensational_indicators.items() 
                               if term in text_lower)
        
        # Check for excessive punctuation
        exclamation_count = text.count('!')
        question_count = text.count('?')
        caps_words = len(re.findall(r'\b[A-Z]{4,}\b', text))
        
        # Add punctuation and formatting scores
        sensational_score += min(exclamation_count * 2, 10)
        sensational_score += min(question_count, 5)
        sensational_score += min(caps_words * 3, 15)
        
        # Normalize to 0-1 scale
        score = min(1, sensational_score / 30)
        
        # Determine label
        if score > 0.7:
            label = 'Highly sensational'
        elif score > 0.4:
            label = 'Moderately sensational'
        elif score > 0.2:
            label = 'Slightly sensational'
        else:
            label = 'Factual'
        
        return {
            'score': score,
            'label': label,
            'confidence': min(100, int(score * 100 * 1.2))
        }
    
    def _analyze_nationalistic_dimension(self, text: str) -> Dict[str, Any]:
        """Analyze nationalistic vs internationalist bias"""
        text_lower = text.lower()
        
        nat_score = sum(weight for term, weight in self.nationalistic_indicators.items() 
                       if term in text_lower)
        int_score = sum(weight for term, weight in self.internationalist_indicators.items() 
                       if term in text_lower)
        
        total_score = nat_score + int_score
        if total_score == 0:
            score = 0
        else:
            score = (nat_score - int_score) / max(total_score, 15)
            score = max(-1, min(1, score))
        
        # Determine label
        if abs(score) > 0.6:
            label = 'Strongly nationalistic' if score > 0 else 'Strongly internationalist'
        elif abs(score) > 0.2:
            label = 'Moderately nationalistic' if score > 0 else 'Moderately internationalist'
        else:
            label = 'Balanced'
        
        return {
            'score': score,
            'label': label,
            'confidence': min(100, int(abs(score) * 100 * 1.2))
        }
    
    def _analyze_establishment_dimension(self, text: str) -> Dict[str, Any]:
        """Analyze establishment vs anti-establishment bias"""
        text_lower = text.lower()
        
        pro_score = sum(weight for term, weight in self.pro_establishment.items() 
                       if term in text_lower)
        anti_score = sum(weight for term, weight in self.anti_establishment.items() 
                        if term in text_lower)
        
        total_score = pro_score + anti_score
        if total_score == 0:
            score = 0
        else:
            score = (pro_score - anti_score) / max(total_score, 15)
            score = max(-1, min(1, score))
        
        # Determine label
        if score > 0.6:
            label = 'Strong pro-establishment'
        elif score > 0.2:
            label = 'Lean establishment'
        elif score < -0.6:
            label = 'Strong anti-establishment'
        elif score < -0.2:
            label = 'Lean anti-establishment'
        else:
            label = 'Neutral'
        
        return {
            'score': score,
            'label': label,
            'confidence': min(100, int(abs(score) * 100 * 1.2))
        }
    
    def detect_bias_patterns(self, text: str) -> List[Dict[str, str]]:
        """Detect specific bias patterns in the text"""
        patterns = []
        
        # Cherry-picking detection
        if re.search(r'(study shows|research finds|data indicates)(?!.*however|.*but|.*although)', 
                    text, re.IGNORECASE):
            if not re.search(r'(methodology|sample size|limitations|peer.review)', 
                           text, re.IGNORECASE):
                patterns.append({
                    'type': 'cherry_picking',
                    'description': 'Cites studies without mentioning limitations or opposing research',
                    'severity': 'medium'
                })
        
        # False balance detection
        equal_time_phrases = ['both sides', 'on one hand', 'equally valid', 'opinions differ']
        if any(phrase in text.lower() for phrase in equal_time_phrases):
            patterns.append({
                'type': 'false_balance',
                'description': 'Presents unequal viewpoints as equally valid',
                'severity': 'low'
            })
        
        # Loaded questions in headlines
        if '?' in text[:100] and any(word in text[:100].lower() 
                                    for word in ['really', 'actually', 'truly']):
            patterns.append({
                'type': 'loaded_question',
                'description': 'Uses questions that imply a specific answer',
                'severity': 'medium'
            })
        
        # Anecdotal evidence
        if re.search(r'(one woman|one man|a friend|someone I know|I remember when)', 
                    text, re.IGNORECASE):
            patterns.append({
                'type': 'anecdotal_evidence',
                'description': 'Relies on personal stories rather than data',
                'severity': 'low'
            })
        
        # Strawman arguments
        if re.search(r'(claim that|say that|believe that).*?(ridiculous|absurd|crazy|insane)', 
                    text, re.IGNORECASE):
            patterns.append({
                'type': 'strawman',
                'description': 'Misrepresents opposing viewpoints to make them easier to attack',
                'severity': 'high'
            })
        
        return patterns
    
    def calculate_bias_confidence(self, text: str, bias_patterns: List[Dict]) -> int:
        """Calculate confidence in bias detection"""
        confidence = 50  # Base confidence
        
        # Increase confidence based on text length
        word_count = len(text.split())
        if word_count > 1000:
            confidence += 20
        elif word_count > 500:
            confidence += 10
        
        # Increase confidence based on pattern detection
        confidence += min(len(bias_patterns) * 5, 20)
        
        # Decrease confidence for ambiguous language
        ambiguous_terms = ['might', 'could', 'possibly', 'perhaps', 'maybe']
        ambiguous_count = sum(1 for term in ambiguous_terms if term in text.lower())
        confidence -= min(ambiguous_count * 2, 10)
        
        return max(20, min(95, confidence))
    
    def analyze_framing_bias(self, text: str) -> Dict[str, Any]:
        """Analyze how issues are framed in the text"""
        framing_indicators = {
            'victim_framing': {
                'patterns': ['victim of', 'suffered under', 'targeted by', 'persecuted'],
                'detected': False,
                'examples': []
            },
            'hero_framing': {
                'patterns': ['champion of', 'defender of', 'fighting for', 'standing up'],
                'detected': False,
                'examples': []
            },
            'threat_framing': {
                'patterns': ['threat to', 'danger to', 'risk to', 'attacking our'],
                'detected': False,
                'examples': []
            },
            'progress_framing': {
                'patterns': ['step forward', 'progress toward', 'advancement', 'improvement'],
                'detected': False,
                'examples': []
            }
        }
        
        text_lower = text.lower()
        sentences = text.split('.')
        
        for frame_type, frame_data in framing_indicators.items():
            for pattern in frame_data['patterns']:
                if pattern in text_lower:
                    frame_data['detected'] = True
                    # Find example sentences
                    for sentence in sentences:
                        if pattern in sentence.lower() and len(frame_data['examples']) < 2:
                            frame_data['examples'].append(sentence.strip())
        
        # Calculate framing bias score
        active_frames = sum(1 for f in framing_indicators.values() if f['detected'])
        
        return {
            'frames_detected': active_frames,
            'framing_patterns': framing_indicators,
            'framing_bias_level': 'high' if active_frames >= 3 else 'medium' if active_frames >= 2 else 'low'
        }
    
    def analyze_source_selection_bias(self, text: str) -> Dict[str, Any]:
        """Analyze bias in source selection"""
        source_types = {
            'government_officials': 0,
            'experts': 0,
            'activists': 0,
            'citizens': 0,
            'anonymous': 0,
            'documents': 0
        }
        
        # Count different source types
        patterns = {
            'government_officials': r'(official|spokesperson|secretary|minister)',
            'experts': r'(expert|professor|researcher|analyst)',
            'activists': r'(activist|advocate|campaigner)',
            'citizens': r'(resident|citizen|voter|parent)',
            'anonymous': r'(sources say|sources told|anonymous)'
        }
        
        for source_type, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            source_types[source_type] = len(matches)
        
        total_sources = sum(source_types.values())
        
        # Analyze diversity
        source_diversity = len([st for st in source_types.values() if st > 0])
        
        # Detect over-reliance on specific source types
        bias_indicators = []
        if total_sources > 0:
            for source_type, count in source_types.items():
                percentage = (count / total_sources) * 100
                if percentage > 60:
                    bias_indicators.append({
                        'type': source_type,
                        'percentage': percentage,
                        'assessment': f'Over-reliance on {source_type.replace("_", " ")}'
                    })
        
        return {
            'source_types': source_types,
            'total_sources': total_sources,
            'source_diversity': source_diversity,
            'diversity_score': min(100, source_diversity * 20),
            'bias_indicators': bias_indicators
        }
    
    def extract_loaded_phrases(self, text: str) -> List[Dict[str, str]]:
        """Extract loaded phrases with enhanced context and categorization"""
        if not text:
            return []
        
        phrases = []
        seen_phrases = set()
        
        for pattern, phrase_type, severity in self.loaded_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                phrase_text = match.group()
                
                # Skip if we've already captured this phrase
                if phrase_text.lower() in seen_phrases:
                    continue
                seen_phrases.add(phrase_text.lower())
                
                # Get surrounding context
                start = max(0, match.start() - 40)
                end = min(len(text), match.end() + 40)
                context = text[start:end].strip()
                
                # Clean up context
                if start > 0:
                    context = '...' + context
                if end < len(text):
                    context = context + '...'
                
                # Determine impact based on severity and placement
                impact = severity
                if match.start() < 200:  # In headline or lead
                    impact = 'high'
                
                phrases.append({
                    'text': phrase_text,
                    'type': phrase_type,
                    'severity': severity,
                    'impact': impact,
                    'context': context,
                    'explanation': self._get_loaded_phrase_explanation(phrase_type, phrase_text)
                })
                
                if len(phrases) >= 10:
                    break
        
        # Sort by severity
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        phrases.sort(key=lambda x: severity_order.get(x['severity'], 3))
        
        return phrases
    
    def _get_loaded_phrase_explanation(self, phrase_type: str, phrase_text: str) -> str:
        """Get explanation for why a phrase is considered loaded"""
        explanations = {
            'political': f'"{phrase_text}" is a politically charged term that can polarize readers',
            'hyperbolic': f'"{phrase_text}" uses exaggerated language to amplify emotional impact',
            'absolute': f'"{phrase_text}" makes sweeping generalizations that oversimplify complex issues',
            'assumption': f'"{phrase_text}" assumes agreement without providing evidence',
            'divisive': f'"{phrase_text}" creates an us-versus-them narrative',
            'fear': f'"{phrase_text}" uses fear-based language to influence reader emotions',
            'savior_language': f'"{phrase_text}" frames one side as heroic saviors'
        }
        return explanations.get(phrase_type, f'"{phrase_text}" may influence reader perception')
    
    def get_enhanced_bias_label(self, bias_dimensions: Dict, political_lean: float) -> str:
        """Generate comprehensive bias label based on multiple dimensions"""
        # Start with political bias as base
        political_bias = bias_dimensions['political']
        
        # Find the most prominent bias dimension
        max_bias_dim = max(bias_dimensions.items(), 
                          key=lambda x: abs(x[1]['score']) if x[0] != 'sensational' else x[1]['score'])
        
        # If political bias is minimal, use the most prominent dimension
        if abs(political_bias['score']) < 0.2 and abs(max_bias_dim[1]['score']) > 0.3:
            return f"{max_bias_dim[1]['label']} bias detected"
        
        # If sensationalism is high, include it
        if bias_dimensions['sensational']['score'] > 0.5:
            return f"{political_bias['label']} / Highly sensational"
        
        # If multiple strong biases, create compound label
        strong_biases = [
            dim_name for dim_name, dim_data in bias_dimensions.items()
            if abs(dim_data['score']) > 0.5 or (dim_name == 'sensational' and dim_data['score'] > 0.5)
        ]
        
        if len(strong_biases) > 1:
            return f"Multiple biases: {', '.join(bias_dimensions[b]['label'] for b in strong_biases[:2])}"
        
        # Default to political bias label
        return political_bias['label']
    
    def calculate_objectivity_score(self, bias_dimensions: Dict, bias_patterns: List, 
                                   loaded_phrases: List) -> int:
        """Calculate objectivity score based on multiple factors"""
        score = 100  # Start with perfect objectivity
        
        # Deduct for each bias dimension
        for dim_name, dim_data in bias_dimensions.items():
            if dim_name == 'sensational':
                # Sensationalism has stronger impact on objectivity
                score -= min(30, dim_data['score'] * 40)
            else:
                # Other biases
                score -= min(20, abs(dim_data['score']) * 25)
        
        # Deduct for bias patterns
        pattern_deductions = {
            'cherry_picking': 15,
            'strawman': 20,
            'loaded_question': 10,
            'anecdotal_evidence': 5,
            'false_balance': 8
        }
        
        for pattern in bias_patterns:
            score -= pattern_deductions.get(pattern['type'], 5)
        
        # Deduct for loaded phrases
        score -= min(20, len(loaded_phrases) * 2)
        
        return max(0, min(100, score))
    
    def calculate_opinion_percentage(self, text: str) -> int:
        """Calculate percentage of opinion vs facts"""
        if not text:
            return 0
        
        opinion_words = ['believe', 'think', 'feel', 'opinion', 'seems', 'appears', 
                        'probably', 'maybe', 'perhaps']
        text_lower = text.lower()
        
        sentences = text.split('.')
        opinion_sentences = sum(1 for s in sentences 
                              if any(word in s.lower() for word in opinion_words))
        
        return min(100, int((opinion_sentences / max(len(sentences), 1)) * 100))
    
    def calculate_emotional_score(self, text: str) -> int:
        """Calculate emotional language score"""
        if not text:
            return 0
        
        emotional_words = ['shocking', 'outrageous', 'disgusting', 'amazing', 'terrible', 
                          'horrible', 'fantastic', 'disaster', 'crisis', 'scandal', 
                          'explosive', 'bombshell']
        text_lower = text.lower()
        
        emotional_count = sum(1 for word in emotional_words if word in text_lower)
        word_count = len(text.split())
        
        return min(100, int((emotional_count / max(word_count, 1)) * 1000))
    
    def detect_manipulation_tactics(self, text: str, bias_patterns: List[Dict]) -> List[Dict]:
        """Enhanced manipulation tactics detection"""
        tactics = []
        
        # Pattern-based tactics
        for pattern in bias_patterns:
            if pattern['severity'] in ['medium', 'high']:
                tactics.append({
                    'name': pattern['type'].replace('_', ' ').title(),
                    'type': pattern['type'],
                    'description': pattern['description'],
                    'severity': pattern['severity']
                })
        
        # Excessive capitalization
        caps_words = len(re.findall(r'\b[A-Z]{3,}\b', text))
        if caps_words > 5:
            tactics.append({
                'name': 'Excessive Capitalization',
                'type': 'formatting_manipulation',
                'description': 'Using ALL CAPS to create false urgency or emphasis',
                'severity': 'medium'
            })
        
        # Multiple exclamation marks
        if len(re.findall(r'!{2,}', text)) > 0:
            tactics.append({
                'name': 'Multiple Exclamation Marks',
                'type': 'formatting_manipulation',
                'description': 'Using excessive punctuation to manipulate emotions',
                'severity': 'low'
            })
        
        # Clickbait patterns
        clickbait_patterns = [
            (r'you won\'t believe', 'Clickbait Hook', 'Uses curiosity gap to manipulate clicks'),
            (r'doctors hate', 'False Authority', 'Claims false opposition from authorities'),
            (r'one weird trick', 'Oversimplification', 'Promises unrealistic simple solutions')
        ]
        
        for pattern, name, description in clickbait_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                tactics.append({
                    'name': name,
                    'type': 'clickbait',
                    'description': description,
                    'severity': 'medium'
                })
        
        # Remove duplicates
        seen = set()
        unique_tactics = []
        for tactic in tactics:
            if tactic['name'] not in seen:
                seen.add(tactic['name'])
                unique_tactics.append(tactic)
        
        return unique_tactics[:8]
    
    def get_bias_contributing_factors(self, bias_dimensions: Dict, framing_analysis: Dict, 
                                     source_bias: Dict) -> List[Dict]:
        """Determine main factors contributing to bias"""
        factors = []
        
        # Check each bias dimension
        for dim_name, dim_data in bias_dimensions.items():
            if abs(dim_data['score']) > 0.3 or (dim_name == 'sensational' and dim_data['score'] > 0.3):
                impact = abs(dim_data['score'])
                factors.append({
                    'factor': dim_name.replace('_', ' ').title() + ' bias',
                    'impact': min(1.0, impact),
                    'description': dim_data['label']
                })
        
        # Check framing bias
        if framing_analysis['frames_detected'] >= 2:
            factors.append({
                'factor': 'Framing bias',
                'impact': min(1.0, framing_analysis['frames_detected'] * 0.25),
                'description': f"{framing_analysis['frames_detected']} framing patterns detected"
            })
        
        # Check source selection bias
        if source_bias['diversity_score'] < 40:
            factors.append({
                'factor': 'Source selection',
                'impact': 0.3,
                'description': 'Limited source diversity'
            })
        
        # Sort by impact and return top 5
        factors.sort(key=lambda x: x['impact'], reverse=True)
        return factors[:5]
    
    def assess_bias_impact(self, bias_dimensions: Dict, bias_patterns: List, 
                          manipulation_tactics: List) -> Dict[str, Any]:
        """Assess the impact of detected biases on reader understanding"""
        # Calculate overall bias severity
        total_bias = sum(abs(d['score']) for d in bias_dimensions.values()) / len(bias_dimensions)
        
        # Determine severity level
        if total_bias > 0.6 or len(manipulation_tactics) > 3:
            severity = 'high'
        elif total_bias > 0.3 or len(manipulation_tactics) > 1:
            severity = 'moderate'
        else:
            severity = 'low'
        
        # Determine reader impact
        impacts = []
        
        if bias_dimensions['political']['score'] > 0.5:
            impacts.append('May reinforce existing political beliefs')
        elif bias_dimensions['political']['score'] < -0.5:
            impacts.append('May challenge conservative viewpoints')
        
        if bias_dimensions['sensational']['score'] > 0.5:
            impacts.append('May exaggerate the importance or urgency of issues')
        
        if bias_dimensions['corporate']['score'] > 0.5:
            impacts.append('May present business interests favorably')
        
        if len(bias_patterns) > 2:
            impacts.append('Uses multiple persuasion techniques that may affect objectivity')
        
        # Factual accuracy assessment
        factual_accuracy = 'Bias present but facts appear accurately presented'
        for pattern in bias_patterns:
            if pattern['type'] == 'cherry_picking':
                factual_accuracy = 'Facts may be accurate but selectively presented'
                break
            elif pattern['type'] == 'strawman':
                factual_accuracy = 'May misrepresent opposing viewpoints'
                break
        
        return {
            'severity': severity,
            'reader_impact': impacts[:3] if impacts else ['Minimal impact on reader perception'],
            'factual_accuracy': factual_accuracy,
            'recommendation': self._get_bias_recommendation(severity)
        }
    
    def _get_bias_recommendation(self, severity: str) -> str:
        """Get recommendation based on bias severity"""
        recommendations = {
            'high': 'Read with caution and seek alternative perspectives from multiple sources',
            'moderate': 'Be aware of potential bias and verify key claims independently',
            'low': 'Minor bias detected - consider author perspective while reading'
        }
        return recommendations.get(severity, 'Read critically and verify important claims')
    
    def get_comparative_bias_context(self, bias_score: float, domain: str = None) -> Dict[str, Any]:
        """Get context about how this bias compares to typical content"""
        context = {
            'source_comparison': None,
            'topic_comparison': None,
            'industry_standard': None
        }
        
        # Industry standard comparison
        if abs(bias_score) < 0.2:
            context['industry_standard'] = 'Well within industry standards for objective reporting'
        elif abs(bias_score) < 0.5:
            context['industry_standard'] = 'Moderate bias, common in opinion or analysis pieces'
        else:
            context['industry_standard'] = 'High bias, typically seen in editorial or advocacy content'
        
        # Note: Source comparison would require SOURCE_CREDIBILITY data
        # This would be imported and used in the main analyzer
        
        return context
    
    def _get_empty_bias_analysis(self) -> Dict[str, Any]:
        """Return empty bias analysis structure"""
        return {
            'overall_bias': 'Unknown',
            'political_lean': 0,
            'objectivity_score': 50,
            'opinion_percentage': 0,
            'emotional_score': 0,
            'manipulation_tactics': [],
            'loaded_phrases': [],
            'bias_confidence': 0,
            'bias_dimensions': {},
            'bias_patterns': [],
            'framing_analysis': {},
            'source_bias_analysis': {},
            'bias_visualization': {},
            'bias_impact': {},
            'comparative_context': {}
        }
    
    # Simple interface methods for backward compatibility
    def detect_political_bias(self, text: str) -> float:
        """Simple political bias detection for backward compatibility"""
        result = self._analyze_political_dimension(text)
        return result['score']
    
    def detect_manipulation(self, text: str) -> List[str]:
        """Simple manipulation detection for backward compatibility"""
        patterns = self.detect_bias_patterns(text)
        tactics = self.detect_manipulation_tactics(text, patterns)
        return [t['name'] for t in tactics]
