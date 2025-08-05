"""
FILE: services/bias_detector.py
LOCATION: news/services/bias_detector.py
PURPOSE: Advanced bias detection and analysis with rich explanations
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
        
        # ENHANCED: Create detailed bias visualization data
        bias_visualization = self._create_bias_visualization(bias_dimensions)
        
        # Bias impact assessment
        bias_impact = self.assess_bias_impact(
            bias_dimensions, bias_patterns, manipulation_tactics
        )
        
        # Comparative context
        comparative_context = self.get_comparative_bias_context(
            basic_bias_score if basic_bias_score else bias_dimensions['political']['score'], 
            domain
        )
        
        # CRITICAL: Generate detailed explanation
        detailed_explanation = self._generate_detailed_explanation(
            bias_dimensions, bias_patterns, loaded_phrases, manipulation_tactics, 
            objectivity_score, opinion_percentage
        )
        
        # ENHANCED: Generate dimension explanations
        dimension_explanations = self._generate_dimension_explanations(bias_dimensions)
        
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
            'comparative_context': comparative_context,
            
            # NEW: Rich explanations
            'detailed_explanation': detailed_explanation,
            'bias_summary': self._generate_bias_summary(bias_dimensions, objectivity_score),
            'key_findings': self._generate_key_findings(bias_patterns, loaded_phrases, manipulation_tactics),
            'dimension_explanations': dimension_explanations
        }
    
    def _create_bias_visualization(self, bias_dimensions: Dict) -> Dict[str, Any]:
        """Create visualization data for bias radar chart"""
        
        # Prepare data for radar chart
        dimensions = []
        for dim_name, dim_data in bias_dimensions.items():
            dimensions.append({
                'axis': self._get_dimension_display_name(dim_name),
                'value': abs(dim_data['score']) * 100,  # Convert to 0-100 scale
                'rawScore': dim_data['score'],  # Keep original -1 to 1 scale
                'label': dim_data['label'],
                'color': self._get_dimension_color(dim_name),
                'description': dim_data.get('explanation', ''),
                'meaning': self._get_dimension_meaning(dim_name)
            })
        
        return {
            'type': 'radar',
            'dimensions': dimensions,
            'summary': self._generate_visualization_summary(bias_dimensions),
            'interpretation': self._generate_visualization_interpretation(bias_dimensions)
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
    
    def _get_dimension_meaning(self, dimension: str) -> str:
        """Get what each dimension means"""
        meanings = {
            'political': 'Measures partisan language and ideological framing from far-left to far-right',
            'corporate': 'Analyzes stance toward business, from anti-corporate criticism to pro-business advocacy',
            'sensational': 'Detects emotionally charged language and attention-grabbing tactics',
            'nationalistic': 'Evaluates focus from global/international perspective to national-first viewpoint',
            'establishment': 'Assesses trust in institutions from anti-establishment skepticism to institutional deference'
        }
        return meanings.get(dimension, '')
    
    def _get_dimension_color(self, dimension: str) -> str:
        """Get color for dimension visualization"""
        colors = {
            'political': '#6366f1',  # Indigo
            'corporate': '#10b981',  # Emerald
            'sensational': '#f59e0b',  # Amber
            'nationalistic': '#ef4444',  # Red
            'establishment': '#8b5cf6'  # Purple
        }
        return colors.get(dimension, '#6b7280')
    
    def _generate_visualization_summary(self, bias_dimensions: Dict) -> str:
        """Generate summary for visualization"""
        high_bias_dims = []
        for dim_name, dim_data in bias_dimensions.items():
            if abs(dim_data['score']) > 0.5 or (dim_name == 'sensational' and dim_data['score'] > 0.5):
                high_bias_dims.append(self._get_dimension_display_name(dim_name))
        
        if not high_bias_dims:
            return "This article shows balanced reporting across all dimensions"
        else:
            return f"Significant bias detected in: {', '.join(high_bias_dims)}"
    
    def _generate_visualization_interpretation(self, bias_dimensions: Dict) -> str:
        """Generate interpretation of the visualization"""
        interpretations = []
        
        # Political dimension
        pol_score = bias_dimensions['political']['score']
        if abs(pol_score) > 0.5:
            direction = "left" if pol_score < 0 else "right"
            interpretations.append(f"Strong {direction}-wing political perspective shapes the narrative")
        
        # Sensational dimension
        if bias_dimensions['sensational']['score'] > 0.5:
            interpretations.append("High emotional language may be manipulating reader reactions")
        
        # Corporate dimension
        corp_score = bias_dimensions['corporate']['score']
        if abs(corp_score) > 0.5:
            stance = "critical of" if corp_score < 0 else "favorable to"
            interpretations.append(f"Notably {stance} business and corporate interests")
        
        return " • ".join(interpretations) if interpretations else "No significant bias patterns detected"
    
    def _generate_dimension_explanations(self, bias_dimensions: Dict) -> Dict[str, Dict[str, str]]:
        """Generate detailed explanations for each dimension"""
        explanations = {}
        
        for dim_name, dim_data in bias_dimensions.items():
            explanations[dim_name] = {
                'what_we_looked_for': self._get_what_we_looked_for(dim_name),
                'why_it_matters': self._get_why_it_matters(dim_name),
                'what_we_found': dim_data.get('explanation', 'No significant indicators found'),
                'what_this_means': self._get_what_this_means(dim_name, dim_data),
                'score': dim_data['score'],
                'label': dim_data['label'],
                'confidence': dim_data['confidence']
            }
        
        return explanations
    
    def _get_what_we_looked_for(self, dimension: str) -> str:
        """Explain what we analyzed for each dimension"""
        explanations = {
            'political': "We analyzed political language, party references, ideological terms, and policy positions to detect partisan bias",
            'corporate': "We examined how businesses, corporations, and economic systems are portrayed - whether favorably or critically",
            'sensational': "We checked for exaggerated claims, emotional manipulation, ALL CAPS, excessive punctuation, and clickbait language",
            'nationalistic': "We looked for language prioritizing national interests versus international cooperation and global perspectives",
            'establishment': "We analyzed trust or skepticism toward institutions, authorities, experts, and traditional sources of information"
        }
        return explanations.get(dimension, '')
    
    def _get_why_it_matters(self, dimension: str) -> str:
        """Explain why each dimension matters"""
        explanations = {
            'political': "Political bias can shape how facts are presented and which viewpoints are emphasized or dismissed",
            'corporate': "Corporate bias affects coverage of business practices, economic policies, and wealth distribution",
            'sensational': "Sensational language manipulates emotions and can distort the importance or urgency of issues",
            'nationalistic': "National focus bias can limit global perspective and affect coverage of international issues",
            'establishment': "Trust in authority affects how official sources are questioned or accepted without scrutiny"
        }
        return explanations.get(dimension, '')
    
    def _get_what_this_means(self, dimension: str, dim_data: Dict) -> str:
        """Explain what the score means for readers"""
        score = dim_data['score']
        label = dim_data['label']
        
        if dimension == 'political':
            if abs(score) < 0.2:
                return "The article maintains political neutrality, allowing readers to form their own opinions"
            elif score > 0.5:
                return "Strong conservative framing may influence how readers interpret the facts presented"
            elif score < -0.5:
                return "Strong progressive framing may influence how readers interpret the facts presented"
            else:
                return f"Moderate {label.lower()} perspective is present but doesn't dominate the reporting"
        
        elif dimension == 'corporate':
            if abs(score) < 0.2:
                return "Business topics are covered objectively without clear pro or anti-corporate bias"
            elif score > 0.5:
                return "Pro-business perspective may downplay corporate criticism or emphasize benefits"
            elif score < -0.5:
                return "Anti-corporate perspective may emphasize business failures over successes"
            else:
                return f"{label} stance influences but doesn't dominate business coverage"
        
        elif dimension == 'sensational':
            if score < 0.2:
                return "Professional, measured tone allows facts to speak for themselves"
            elif score > 0.7:
                return "Extreme sensationalism may be distorting the actual importance of events"
            else:
                return "Some emotional language is used to engage readers but facts remain central"
        
        elif dimension == 'nationalistic':
            if abs(score) < 0.2:
                return "Balanced coverage of both national and international perspectives"
            elif score > 0.5:
                return "Strong national focus may limit international context and global perspectives"
            elif score < -0.5:
                return "International focus may downplay legitimate national interests or concerns"
            else:
                return f"{label} perspective provides some bias in coverage of global issues"
        
        elif dimension == 'establishment':
            if abs(score) < 0.2:
                return "Balanced approach to institutional sources with appropriate skepticism"
            elif score > 0.5:
                return "High trust in official sources may lead to uncritical acceptance of claims"
            elif score < -0.5:
                return "Deep skepticism of institutions may lead to dismissal of credible information"
            else:
                return f"{label} stance affects how institutional sources are presented"
        
        return "Score indicates moderate bias in this dimension"
    
    def _generate_detailed_explanation(self, bias_dimensions: Dict, bias_patterns: List,
                                     loaded_phrases: List, manipulation_tactics: List,
                                     objectivity_score: int, opinion_percentage: int) -> str:
        """Generate human-readable explanation of bias analysis"""
        
        explanations = []
        
        # Start with overall assessment
        strong_biases = sum(1 for d in bias_dimensions.values() if abs(d['score']) > 0.5)
        if strong_biases == 0:
            explanations.append(
                "This article demonstrates relatively balanced reporting without strong bias in any dimension. "
                "While no reporting is perfectly neutral, this piece maintains professional standards."
            )
        elif strong_biases == 1:
            explanations.append(
                "This article shows significant bias in one key dimension that colors the overall reporting. "
                "Readers should be aware of this perspective when evaluating the information presented."
            )
        else:
            explanations.append(
                f"This article exhibits strong bias across {strong_biases} dimensions, significantly affecting "
                f"how information is presented. Multiple biases compound to create a particular narrative."
            )
        
        # Political bias explanation with specifics
        political = bias_dimensions['political']
        if abs(political['score']) > 0.2:
            direction = "conservative/right-wing" if political['score'] > 0 else "progressive/left-wing"
            explanations.append(
                f"The {direction} political bias ({abs(political['score']*100):.0f}%) is evident through "
                f"specific language choices and framing. {political.get('explanation', '')}"
            )
        
        # Objectivity explanation
        if objectivity_score >= 80:
            explanations.append(
                "Despite any ideological leanings, the article maintains high objectivity with "
                "factual reporting, proper sourcing, and minimal emotional manipulation."
            )
        elif objectivity_score >= 60:
            explanations.append(
                f"The article shows reasonable objectivity ({objectivity_score}%) but includes "
                f"subjective elements that may influence interpretation."
            )
        elif objectivity_score < 40:
            explanations.append(
                f"Low objectivity score ({objectivity_score}%) indicates heavy use of opinion, "
                f"emotional language, and subjective interpretation mixed with factual claims."
            )
        
        # Manipulation tactics
        if manipulation_tactics:
            tactic_names = [t['name'] for t in manipulation_tactics[:3]]
            explanations.append(
                f"Several persuasion techniques detected: {', '.join(tactic_names)}. "
                f"These tactics are designed to influence reader emotions and opinions beyond "
                f"straightforward factual reporting."
            )
        
        # Opinion vs fact ratio
        if opinion_percentage > 50:
            explanations.append(
                f"High opinion content ({opinion_percentage}% of sentences) indicates this is "
                f"more commentary than news reporting. Readers should recognize this as analysis "
                f"rather than straight news."
            )
        
        return " ".join(explanations)
    
    def _generate_bias_summary(self, bias_dimensions: Dict, objectivity_score: int) -> str:
        """Generate concise bias summary"""
        
        # Find strongest biases
        strong_biases = []
        for dim_name, dim_data in bias_dimensions.items():
            if abs(dim_data['score']) > 0.5 or (dim_name == 'sensational' and dim_data['score'] > 0.5):
                strong_biases.append(f"{dim_data['label']} ({self._get_dimension_display_name(dim_name)})")
        
        if not strong_biases:
            return f"Relatively unbiased reporting with {objectivity_score}% objectivity score"
        else:
            return f"Detected: {', '.join(strong_biases)} - Objectivity: {objectivity_score}%"
    
    def _generate_key_findings(self, bias_patterns: List, loaded_phrases: List, 
                              manipulation_tactics: List) -> List[str]:
        """Generate key findings list"""
        findings = []
        
        # Add pattern findings with explanations
        for pattern in bias_patterns[:2]:
            findings.append(f"{pattern['type'].replace('_', ' ').title()}: {pattern['description']}")
        
        # Add loaded phrase findings
        if loaded_phrases:
            high_impact = [p for p in loaded_phrases if p['severity'] == 'high']
            if high_impact:
                examples = [f'"{p["text"]}"' for p in high_impact[:2]]
                findings.append(f"Found {len(high_impact)} high-impact loaded phrases including {', '.join(examples)}")
        
        # Add manipulation findings
        if manipulation_tactics:
            findings.append(f"Detected {len(manipulation_tactics)} manipulation tactics affecting credibility")
        
        # Add positive findings if relatively unbiased
        if not findings:
            findings.append("No significant bias patterns or manipulation tactics detected")
            findings.append("Article maintains professional journalistic standards")
        
        return findings[:5]  # Limit to 5 key findings
    
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
        """Analyze political bias dimension with detailed explanation"""
        text_lower = text.lower()
        
        # Find which indicators are present
        left_found = []
        right_found = []
        
        for term, weight in self.left_indicators.items():
            if term in text_lower:
                left_found.append(term)
        
        for term, weight in self.right_indicators.items():
            if term in text_lower:
                right_found.append(term)
        
        left_score = sum(self.left_indicators[term] for term in left_found)
        right_score = sum(self.right_indicators[term] for term in right_found)
        
        total_score = left_score + right_score
        if total_score == 0:
            score = 0
            explanation = "No significant political indicators detected. The article avoids partisan language."
        else:
            score = (right_score - left_score) / max(total_score, 20)
            score = max(-1, min(1, score))
            
            if left_found and right_found:
                explanation = f"Mixed political language with both progressive terms ({', '.join(left_found[:3])}) and conservative terms ({', '.join(right_found[:3])})"
            elif left_found:
                explanation = f"Uses progressive/left-leaning language including: {', '.join(left_found[:5])}"
            else:
                explanation = f"Uses conservative/right-leaning language including: {', '.join(right_found[:5])}"
        
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
            'confidence': min(100, int(abs(score) * 100 * 1.2)),
            'explanation': explanation,
            'indicators_found': {
                'left': left_found[:5],
                'right': right_found[:5]
            }
        }
    
    def _analyze_corporate_dimension(self, text: str) -> Dict[str, Any]:
        """Analyze corporate bias dimension"""
        text_lower = text.lower()
        
        pro_found = [term for term in self.pro_corporate.keys() if term in text_lower]
        anti_found = [term for term in self.anti_corporate.keys() if term in text_lower]
        
        pro_score = sum(self.pro_corporate[term] for term in pro_found)
        anti_score = sum(self.anti_corporate[term] for term in anti_found)
        
        total_score = pro_score + anti_score
        if total_score == 0:
            score = 0
            explanation = "Neutral stance on corporate/business issues. No clear pro or anti-business bias detected."
        else:
            score = (pro_score - anti_score) / max(total_score, 15)
            score = max(-1, min(1, score))
            
            if pro_found and anti_found:
                explanation = f"Mixed coverage with both pro-business ({', '.join(pro_found[:2])}) and critical ({', '.join(anti_found[:2])}) language"
            elif pro_found:
                explanation = f"Favorable to business/corporate interests, using terms like: {', '.join(pro_found[:3])}"
            else:
                explanation = f"Critical of corporate power, using terms like: {', '.join(anti_found[:3])}"
        
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
            'confidence': min(100, int(abs(score) * 100 * 1.2)),
            'explanation': explanation
        }
    
    def _analyze_sensational_dimension(self, text: str) -> Dict[str, Any]:
        """Analyze sensational bias dimension"""
        text_lower = text.lower()
        
        # Check for sensational words
        sensational_found = [term for term in self.sensational_indicators.keys() if term in text_lower]
        sensational_score = sum(self.sensational_indicators[term] for term in sensational_found)
        
        # Check for excessive punctuation
        exclamation_count = text.count('!')
        question_count = text.count('?')
        caps_words = len(re.findall(r'\b[A-Z]{4,}\b', text))
        
        # Build explanation
        issues = []
        if sensational_found:
            issues.append(f"sensational language ({', '.join(sensational_found[:3])})")
        if exclamation_count > 2:
            issues.append(f"{exclamation_count} exclamation marks")
        if caps_words > 3:
            issues.append(f"{caps_words} ALL CAPS words")
        
        # Add punctuation and formatting scores
        sensational_score += min(exclamation_count * 2, 10)
        sensational_score += min(question_count, 5)
        sensational_score += min(caps_words * 3, 15)
        
        # Normalize to 0-1 scale
        score = min(1, sensational_score / 30)
        
        if issues:
            explanation = f"Sensational elements detected: {', '.join(issues)}"
        else:
            explanation = "Measured, professional tone without sensationalism"
        
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
            'confidence': min(100, int(score * 100 * 1.2)),
            'explanation': explanation
        }
    
    def _analyze_nationalistic_dimension(self, text: str) -> Dict[str, Any]:
        """Analyze nationalistic vs internationalist bias"""
        text_lower = text.lower()
        
        nat_found = [term for term in self.nationalistic_indicators.keys() if term in text_lower]
        int_found = [term for term in self.internationalist_indicators.keys() if term in text_lower]
        
        nat_score = sum(self.nationalistic_indicators[term] for term in nat_found)
        int_score = sum(self.internationalist_indicators[term] for term in int_found)
        
        total_score = nat_score + int_score
        if total_score == 0:
            score = 0
            explanation = "Balanced perspective on national vs international interests"
        else:
            score = (nat_score - int_score) / max(total_score, 15)
            score = max(-1, min(1, score))
            
            if nat_found and int_found:
                explanation = f"Mixed perspective with both nationalistic ({', '.join(nat_found[:2])}) and internationalist ({', '.join(int_found[:2])}) themes"
            elif nat_found:
                explanation = f"Nationalistic perspective emphasizing: {', '.join(nat_found[:3])}"
            else:
                explanation = f"Internationalist perspective emphasizing: {', '.join(int_found[:3])}"
        
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
            'confidence': min(100, int(abs(score) * 100 * 1.2)),
            'explanation': explanation
        }
    
    def _analyze_establishment_dimension(self, text: str) -> Dict[str, Any]:
        """Analyze establishment vs anti-establishment bias"""
        text_lower = text.lower()
        
        pro_found = [term for term in self.pro_establishment.keys() if term in text_lower]
        anti_found = [term for term in self.anti_establishment.keys() if term in text_lower]
        
        pro_score = sum(self.pro_establishment[term] for term in pro_found)
        anti_score = sum(self.anti_establishment[term] for term in anti_found)
        
        total_score = pro_score + anti_score
        if total_score == 0:
            score = 0
            explanation = "Neutral stance toward institutions and authority"
        else:
            score = (pro_score - anti_score) / max(total_score, 15)
            score = max(-1, min(1, score))
            
            if pro_found and anti_found:
                explanation = f"Mixed stance with both trust ({', '.join(pro_found[:2])}) and skepticism ({', '.join(anti_found[:2])}) of institutions"
            elif pro_found:
                explanation = f"Trusts institutional authority, referencing: {', '.join(pro_found[:3])}"
            else:
                explanation = f"Skeptical of establishment, using language like: {', '.join(anti_found[:3])}"
        
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
            'confidence': min(100, int(abs(score) * 100 * 1.2)),
            'explanation': explanation
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
                    'severity': 'medium',
                    'example': 'The article references research findings but doesn\'t discuss study limitations or contradicting studies'
                })
        
        # False balance detection
        equal_time_phrases = ['both sides', 'on one hand', 'equally valid', 'opinions differ']
        if any(phrase in text.lower() for phrase in equal_time_phrases):
            patterns.append({
                'type': 'false_balance',
                'description': 'Presents unequal viewpoints as equally valid',
                'severity': 'low',
                'example': 'Gives equal weight to expert consensus and fringe opinions'
            })
        
        # Loaded questions in headlines
        if '?' in text[:100] and any(word in text[:100].lower() 
                                    for word in ['really', 'actually', 'truly']):
            patterns.append({
                'type': 'loaded_question',
                'description': 'Uses questions that imply a specific answer',
                'severity': 'medium',
                'example': 'Headlines with questions like "Is X really...?" that suggest doubt'
            })
        
        # Anecdotal evidence
        if re.search(r'(one woman|one man|a friend|someone I know|I remember when)', 
                    text, re.IGNORECASE):
            patterns.append({
                'type': 'anecdotal_evidence',
                'description': 'Relies on personal stories rather than data',
                'severity': 'low',
                'example': 'Uses individual experiences to support broad claims'
            })
        
        # Strawman arguments
        if re.search(r'(claim that|say that|believe that).*?(ridiculous|absurd|crazy|insane)', 
                    text, re.IGNORECASE):
            patterns.append({
                'type': 'strawman',
                'description': 'Misrepresents opposing viewpoints to make them easier to attack',
                'severity': 'high',
                'example': 'Characterizes opposing views in extreme terms before dismissing them'
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
        
        # Generate explanation
        if active_frames > 0:
            detected_frames = [name.replace('_', ' ') for name, data in framing_indicators.items() if data['detected']]
            explanation = f"Article uses {', '.join(detected_frames)} to shape reader perception"
        else:
            explanation = "Neutral framing without obvious narrative shaping"
        
        return {
            'frames_detected': active_frames,
            'framing_patterns': framing_indicators,
            'framing_bias_level': 'high' if active_frames >= 3 else 'medium' if active_frames >= 2 else 'low',
            'explanation': explanation
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
        
        # Generate explanation
        if bias_indicators:
            explanation = f"Heavy reliance on {bias_indicators[0]['type'].replace('_', ' ')} ({bias_indicators[0]['percentage']:.0f}% of sources)"
        elif source_diversity >= 3:
            explanation = "Good source diversity with multiple viewpoints represented"
        else:
            explanation = "Limited source diversity may indicate bias"
        
        return {
            'source_types': source_types,
            'total_sources': total_sources,
            'source_diversity': source_diversity,
            'diversity_score': min(100, source_diversity * 20),
            'bias_indicators': bias_indicators,
            'explanation': explanation
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
        
        opinion_indicators = [
            'believe', 'think', 'feel', 'opinion', 'seems', 'appears', 
            'probably', 'maybe', 'perhaps', 'suggest', 'argue', 'contend',
            'in my view', 'in my opinion', 'I think', 'I believe'
        ]
        
        sentences = text.split('.')
        opinion_sentences = 0
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            # Check for opinion indicators
            if any(indicator in sentence_lower for indicator in opinion_indicators):
                opinion_sentences += 1
            # Check for subjective adjectives
            elif re.search(r'\b(good|bad|better|worse|right|wrong|should|shouldn\'t)\b', sentence_lower):
                opinion_sentences += 1
        
        percentage = min(100, int((opinion_sentences / max(len(sentences), 1)) * 100))
        
        return percentage
    
    def calculate_emotional_score(self, text: str) -> int:
        """Calculate emotional language score"""
        if not text:
            return 0
        
        emotional_words = [
            'shocking', 'outrageous', 'disgusting', 'amazing', 'terrible', 
            'horrible', 'fantastic', 'disaster', 'crisis', 'scandal', 
            'explosive', 'bombshell', 'devastating', 'tragic', 'heartbreaking',
            'infuriating', 'delightful', 'horrifying', 'wonderful', 'awful'
        ]
        
        text_lower = text.lower()
        word_count = len(text.split())
        
        # Count emotional words and their intensity
        emotional_count = 0
        for word in emotional_words:
            count = text_lower.count(word)
            emotional_count += count
            # Extra weight for very strong emotional words
            if word in ['devastating', 'horrifying', 'explosive', 'bombshell']:
                emotional_count += count  # Double count these
        
        # Calculate score (scaled to be meaningful)
        score = min(100, int((emotional_count / max(word_count, 1)) * 1000))
        
        return score
    
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
            'comparative_context': {},
            'detailed_explanation': 'Unable to analyze bias due to insufficient content',
            'bias_summary': 'Analysis unavailable',
            'key_findings': [],
            'dimension_explanations': {}
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
