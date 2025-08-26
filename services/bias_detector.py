"""
Bias Detector Service - BULLETPROOF AI ENHANCED VERSION
Advanced multi-dimensional bias detection with bulletproof AI insights
"""

import re
import logging
import time
import os
from typing import Dict, List, Any, Tuple, Optional
from collections import Counter
import statistics

from services.base_analyzer import BaseAnalyzer
from services.ai_enhancement_mixin import AIEnhancementMixin

logger = logging.getLogger(__name__)


class BiasDetector(BaseAnalyzer, AIEnhancementMixin):
    """
    Advanced bias detection analyzing multiple dimensions WITH BULLETPROOF AI ENHANCEMENT
    """
    
    def __init__(self):
        """Initialize bias detector with comprehensive pattern database and bulletproof AI"""
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
        Perform comprehensive bias analysis WITH BULLETPROOF AI ENHANCEMENT
        
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
            
            title = data.get('title', '')
            full_text = f"{title}\n\n{text}" if title else text
            
            logger.info(f"Analyzing bias in {len(full_text)} characters of text")
            
            # Core bias analysis
            political_bias = self._analyze_political_bias(full_text)
            sensationalism = self._analyze_sensationalism(full_text)
            corporate_bias = self._analyze_corporate_bias(full_text)
            loaded_language = self._detect_loaded_language(full_text)
            framing_analysis = self._analyze_framing(full_text)
            
            # Calculate overall bias metrics
            bias_dimensions = {
                'political': political_bias,
                'sensationalism': sensationalism,
                'corporate': corporate_bias,
                'loaded_language': loaded_language,
                'framing': framing_analysis
            }
            
            overall_bias_score = self._calculate_overall_bias_score(bias_dimensions)
            objectivity_score = 100 - overall_bias_score
            bias_level = self._get_bias_level(overall_bias_score)
            
            # Generate findings
            findings = self._generate_findings(bias_dimensions, overall_bias_score)
            
            # Generate summary
            summary = self._generate_summary(bias_dimensions, overall_bias_score, bias_level)
            
            # Build response
            result = {
                'service': self.service_name,
                'success': True,
                'data': {
                    'score': overall_bias_score,
                    'bias_score': overall_bias_score,
                    'level': bias_level,
                    'bias_level': bias_level,
                    'objectivity_score': objectivity_score,
                    'findings': findings,
                    'summary': summary,
                    'dimensions': bias_dimensions,
                    'loaded_phrases': loaded_language.get('phrases', [])[:10],  # Top 10
                    'dominant_bias': self._get_dominant_bias(bias_dimensions),
                    'political_label': political_bias.get('label', 'Neutral'),
                    'sensationalism_level': sensationalism.get('level', 'Low'),
                    'overall_bias_score': overall_bias_score,
                    'details': {
                        'political_score': political_bias.get('score', 0),
                        'sensationalism_score': sensationalism.get('score', 0),
                        'corporate_score': corporate_bias.get('score', 0),
                        'loaded_language_count': len(loaded_language.get('phrases', [])),
                        'framing_issues': len(framing_analysis.get('issues', []))
                    }
                },
                'metadata': {
                    'analysis_time': time.time() - start_time,
                    'text_length': len(full_text),
                    'analyzed_with_title': bool(title)
                }
            }
            
            # BULLETPROOF AI ENHANCEMENT
            if full_text:
                logger.info("Enhancing bias detection with AI insights")
                result = self._safely_enhance_service_result(
                    result,
                    '_ai_detect_bias_patterns',
                    text=full_text[:1500],
                    initial_findings=result['data']
                )
            
            logger.info(f"Bias analysis complete: {overall_bias_score}/100 ({bias_level})")
            return result
            
        except Exception as e:
            logger.error(f"Bias analysis failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _initialize_bias_patterns(self):
        """Initialize comprehensive bias detection patterns"""
        
        # Political bias indicators
        self.political_patterns = {
            'left_indicators': [
                'progressive', 'liberal', 'social justice', 'inequality', 'climate crisis',
                'systemic racism', 'corporate greed', 'wealth gap', 'social programs'
            ],
            'right_indicators': [
                'conservative', 'traditional values', 'free market', 'personal responsibility',
                'law and order', 'strong defense', 'fiscal responsibility', 'family values'
            ],
            'extremist_indicators': [
                'radical', 'extremist', 'deep state', 'mainstream media', 'establishment',
                'wake up', 'sheeple', 'crisis actor', 'false flag'
            ]
        }
        
        # Sensationalism patterns
        self.sensationalism_patterns = [
            'shocking', 'explosive', 'bombshell', 'devastating', 'unprecedented',
            'crisis', 'disaster', 'scandal', 'outrageous', 'incredible'
        ]
        
        # Corporate bias indicators
        self.corporate_patterns = {
            'pro_business': ['innovation', 'job creation', 'economic growth', 'efficiency'],
            'anti_business': ['corporate greed', 'exploitation', 'price gouging', 'monopoly']
        }
        
        # Loaded language patterns
        self.loaded_patterns = [
            'alleged', 'claimed', 'so-called', 'notorious', 'infamous',
            'controversial', 'divisive', 'polarizing'
        ]
    
    def _analyze_political_bias(self, text: str) -> Dict[str, Any]:
        """Analyze political bias in the text"""
        text_lower = text.lower()
        
        left_score = sum(1 for indicator in self.political_patterns['left_indicators'] 
                        if indicator in text_lower)
        right_score = sum(1 for indicator in self.political_patterns['right_indicators'] 
                         if indicator in text_lower)
        extremist_score = sum(1 for indicator in self.political_patterns['extremist_indicators'] 
                             if indicator in text_lower)
        
        # Calculate political lean
        total_political = left_score + right_score
        if total_political == 0:
            political_lean = 'Neutral'
            lean_intensity = 0
        elif left_score > right_score:
            lean_intensity = min(100, (left_score / total_political) * 100)
            political_lean = 'Left' if lean_intensity > 60 else 'Center-Left'
        else:
            lean_intensity = min(100, (right_score / total_political) * 100)
            political_lean = 'Right' if lean_intensity > 60 else 'Center-Right'
        
        # Add extremist adjustment
        extremist_adjustment = min(30, extremist_score * 10)
        
        return {
            'label': political_lean,
            'score': min(100, lean_intensity + extremist_adjustment),
            'left_indicators': left_score,
            'right_indicators': right_score,
            'extremist_indicators': extremist_score,
            'lean_intensity': lean_intensity
        }
    
    def _analyze_sensationalism(self, text: str) -> Dict[str, Any]:
        """Analyze sensationalism in the text"""
        text_lower = text.lower()
        
        sensational_count = sum(1 for pattern in self.sensationalism_patterns 
                               if pattern in text_lower)
        
        # Calculate sensationalism score based on density
        word_count = len(text.split())
        sensational_density = (sensational_count / max(word_count, 1)) * 1000
        
        sensationalism_score = min(100, sensational_density * 10)
        
        if sensationalism_score >= 70:
            level = 'High'
        elif sensationalism_score >= 40:
            level = 'Moderate'
        elif sensationalism_score >= 15:
            level = 'Low'
        else:
            level = 'Minimal'
        
        return {
            'score': int(sensationalism_score),
            'level': level,
            'sensational_phrases': sensational_count,
            'density': sensational_density
        }
    
    def _analyze_corporate_bias(self, text: str) -> Dict[str, Any]:
        """Analyze corporate/business bias"""
        text_lower = text.lower()
        
        pro_business = sum(1 for indicator in self.corporate_patterns['pro_business'] 
                          if indicator in text_lower)
        anti_business = sum(1 for indicator in self.corporate_patterns['anti_business'] 
                           if indicator in text_lower)
        
        total_corporate = pro_business + anti_business
        if total_corporate == 0:
            corporate_bias = 'Neutral'
            score = 0
        elif pro_business > anti_business:
            score = min(100, (pro_business / total_corporate) * 100)
            corporate_bias = 'Pro-Business'
        else:
            score = min(100, (anti_business / total_corporate) * 100)
            corporate_bias = 'Anti-Business'
        
        return {
            'bias': corporate_bias,
            'score': int(score),
            'pro_business_indicators': pro_business,
            'anti_business_indicators': anti_business
        }
    
    def _detect_loaded_language(self, text: str) -> Dict[str, Any]:
        """Detect loaded/biased language"""
        text_lower = text.lower()
        sentences = re.split(r'[.!?]+', text)
        
        loaded_phrases = []
        for sentence in sentences:
            for pattern in self.loaded_patterns:
                if pattern in sentence.lower():
                    # Extract context around the loaded word
                    context = sentence.strip()
                    if len(context) > 10:  # Skip very short sentences
                        loaded_phrases.append({
                            'phrase': pattern,
                            'context': context[:200],
                            'sentence': context
                        })
        
        # Remove duplicates
        unique_phrases = []
        seen_contexts = set()
        for phrase in loaded_phrases:
            if phrase['context'] not in seen_contexts:
                unique_phrases.append(phrase)
                seen_contexts.add(phrase['context'])
        
        return {
            'phrases': unique_phrases[:15],  # Limit to 15 examples
            'count': len(unique_phrases),
            'density': len(unique_phrases) / max(len(sentences), 1)
        }
    
    def _analyze_framing(self, text: str) -> Dict[str, Any]:
        """Analyze how the article frames issues"""
        
        # Look for framing indicators
        framing_issues = []
        
        # One-sided framing
        if 'however' not in text.lower() and 'but' not in text.lower():
            if len(text) > 500:  # Only for substantial articles
                framing_issues.append("Limited counterarguments presented")
        
        # Emotional framing
        emotional_words = ['outraged', 'devastated', 'thrilled', 'shocked', 'horrified']
        emotional_count = sum(1 for word in emotional_words if word in text.lower())
        if emotional_count > 3:
            framing_issues.append("Heavy emotional language usage")
        
        # Source diversity
        quote_count = text.count('"')
        source_indicators = ['according to', 'said', 'stated', 'reported']
        source_count = sum(1 for indicator in source_indicators if indicator in text.lower())
        
        if quote_count > 0 and source_count < 2:
            framing_issues.append("Limited source diversity")
        
        return {
            'issues': framing_issues,
            'emotional_language_count': emotional_count,
            'source_diversity_score': min(100, source_count * 25)
        }
    
    def _calculate_overall_bias_score(self, dimensions: Dict[str, Any]) -> int:
        """Calculate overall bias score from all dimensions"""
        
        political_score = dimensions['political'].get('score', 0)
        sensationalism_score = dimensions['sensationalism'].get('score', 0)
        corporate_score = dimensions['corporate'].get('score', 0)
        loaded_count = dimensions['loaded_language'].get('count', 0)
        framing_issues = len(dimensions['framing'].get('issues', []))
        
        # Weight different types of bias
        weighted_score = (
            political_score * 0.3 +
            sensationalism_score * 0.25 +
            corporate_score * 0.2 +
            min(100, loaded_count * 5) * 0.15 +
            min(100, framing_issues * 15) * 0.1
        )
        
        return min(100, int(weighted_score))
    
    def _get_bias_level(self, score: int) -> str:
        """Convert bias score to level"""
        if score >= 70:
            return 'High Bias'
        elif score >= 50:
            return 'Moderate Bias'
        elif score >= 30:
            return 'Low Bias'
        elif score >= 15:
            return 'Minimal Bias'
        else:
            return 'Very Low Bias'
    
    def _get_dominant_bias(self, dimensions: Dict[str, Any]) -> str:
        """Identify the dominant type of bias"""
        scores = {
            'Political': dimensions['political'].get('score', 0),
            'Sensationalism': dimensions['sensationalism'].get('score', 0),
            'Corporate': dimensions['corporate'].get('score', 0),
            'Loaded Language': min(100, dimensions['loaded_language'].get('count', 0) * 10)
        }
        
        if max(scores.values()) < 20:
            return 'None'
        
        return max(scores, key=scores.get)
    
    def _generate_findings(self, dimensions: Dict[str, Any], overall_score: int) -> List[Dict[str, Any]]:
        """Generate findings based on bias analysis"""
        findings = []
        
        # Overall assessment
        if overall_score >= 70:
            findings.append({
                'type': 'warning',
                'severity': 'high',
                'text': f'High bias detected ({overall_score}/100)',
                'explanation': 'Article shows significant bias that may affect objectivity'
            })
        elif overall_score >= 40:
            findings.append({
                'type': 'warning',
                'severity': 'medium',
                'text': f'Moderate bias detected ({overall_score}/100)',
                'explanation': 'Article shows some bias that readers should be aware of'
            })
        elif overall_score < 20:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': f'Low bias detected ({overall_score}/100)',
                'explanation': 'Article maintains good objectivity'
            })
        
        # Political bias
        political = dimensions['political']
        if political['score'] > 50:
            findings.append({
                'type': 'info',
                'severity': 'medium',
                'text': f'Political lean: {political["label"]}',
                'explanation': f'Article shows {political["label"].lower()} political perspective'
            })
        
        # Sensationalism
        sensationalism = dimensions['sensationalism']
        if sensationalism['score'] > 60:
            findings.append({
                'type': 'warning',
                'severity': 'medium',
                'text': f'High sensationalism ({sensationalism["score"]}/100)',
                'explanation': 'Article uses sensational language that may exaggerate issues'
            })
        
        # Loaded language
        loaded = dimensions['loaded_language']
        if loaded['count'] > 5:
            findings.append({
                'type': 'warning',
                'severity': 'medium',
                'text': f'Loaded language detected ({loaded["count"]} instances)',
                'explanation': 'Article uses biased or emotionally charged language'
            })
        
        return findings
    
    def _generate_summary(self, dimensions: Dict[str, Any], score: int, level: str) -> str:
        """Generate summary of bias analysis"""
        objectivity = 100 - score
        
        if score < 20:
            base = "This article maintains excellent objectivity with minimal bias."
        elif score < 40:
            base = "This article shows some bias but maintains reasonable objectivity."
        elif score < 60:
            base = "This article contains moderate bias that may influence interpretation."
        else:
            base = "This article shows significant bias that substantially affects objectivity."
        
        # Add specific findings
        dominant = self._get_dominant_bias(dimensions)
        if dominant != 'None':
            base += f" Primary bias type: {dominant}."
        
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
                'Loaded language extraction',
                'Framing analysis',
                'Source diversity assessment',
                'BULLETPROOF AI-enhanced bias detection'
            ],
            'dimensions_analyzed': 5,
            'patterns_detected': len(self.loaded_patterns),
            'visualization_ready': True,
            'ai_enhanced': self._ai_available
        })
        return info
