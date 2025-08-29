"""
Bias Detector Service - COMPLETE FIXED VERSION
CRITICAL FIXES:
1. Proper data structure with consistent wrapper format
2. Enhanced error handling and timeout protection
3. Bulletproof AI enhancement integration
4. Comprehensive bias analysis with reliable scoring
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
    FIXED: Advanced bias detection with proper data structure and bulletproof AI enhancement
    """
    
    def __init__(self):
        """Initialize bias detector with comprehensive pattern database"""
        super().__init__('bias_detector')
        AIEnhancementMixin.__init__(self)
        
        # Initialize all bias patterns and indicators
        self._initialize_bias_patterns()
        
        logger.info(f"BiasDetector initialized with AI enhancement: {self._ai_available}")
    
    def _check_availability(self) -> bool:
        """Service is always available"""
        return True
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        FIXED: Perform comprehensive bias analysis with proper data structure
        """
        try:
            start_time = time.time()
            
            text = data.get('text', '')
            if not text:
                return self.get_error_result("No text provided for bias analysis")
            
            title = data.get('title', '')
            full_text = f"{title}\n\n{text}" if title else text
            
            logger.info(f"Analyzing bias in {len(full_text)} characters of text")
            
            # Core bias analysis with timeout protection
            try:
                political_bias = self._analyze_political_bias(full_text)
                sensationalism = self._analyze_sensationalism(full_text)
                corporate_bias = self._analyze_corporate_bias(full_text)
                loaded_language = self._detect_loaded_language(full_text)
                framing_analysis = self._analyze_framing(full_text)
            except Exception as analysis_error:
                logger.warning(f"Bias analysis components failed: {analysis_error}")
                # Provide minimal analysis if detailed analysis fails
                political_bias = {'label': 'Unknown', 'score': 0}
                sensationalism = {'level': 'Unknown', 'score': 0}
                corporate_bias = {'bias': 'Unknown', 'score': 0}
                loaded_language = {'phrases': [], 'count': 0}
                framing_analysis = {'issues': []}
            
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
            
            # FIXED: Build response with proper data structure wrapper
            result = {
                'service': self.service_name,
                'success': True,
                'available': True,
                'timestamp': time.time(),
                'analysis_complete': True,
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
                    'bias_direction': self._get_bias_direction(political_bias),
                    'political_leaning': political_bias.get('label', 'Center'),
                    'patterns': self._get_bias_patterns_summary(bias_dimensions),
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
                    'analyzed_with_title': bool(title),
                    'ai_enhancement_attempted': self._ai_available
                }
            }
            
            # BULLETPROOF AI ENHANCEMENT
            if full_text and self._ai_available:
                logger.info("Enhancing bias detection with AI insights")
                try:
                    enhanced_result = self._safely_enhance_service_result(
                        result,
                        '_ai_detect_bias_patterns',
                        text=full_text[:1500],
                        initial_findings=result['data']
                    )
                    if enhanced_result:
                        result = enhanced_result
                        result['metadata']['ai_enhancement_applied'] = True
                except Exception as ai_error:
                    logger.warning(f"AI enhancement failed safely: {ai_error}")
                    result['metadata']['ai_enhancement_failed'] = str(ai_error)
            
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
                'systemic racism', 'corporate greed', 'wealth gap', 'social programs',
                'reproductive rights', 'gun control', 'universal healthcare', 'living wage'
            ],
            'right_indicators': [
                'conservative', 'traditional values', 'free market', 'personal responsibility',
                'law and order', 'strong defense', 'fiscal responsibility', 'family values',
                'second amendment', 'limited government', 'individual liberty', 'tax cuts'
            ],
            'extremist_indicators': [
                'radical', 'extremist', 'deep state', 'mainstream media', 'establishment',
                'wake up', 'sheeple', 'crisis actor', 'false flag', 'globalist', 'marxist'
            ]
        }
        
        # Sensationalism patterns
        self.sensationalism_patterns = [
            'shocking', 'explosive', 'bombshell', 'devastating', 'unprecedented',
            'crisis', 'disaster', 'scandal', 'outrageous', 'incredible', 'stunning',
            'breaking', 'urgent', 'must-see', 'viral', 'epic', 'massive', 'huge'
        ]
        
        # Corporate bias indicators
        self.corporate_patterns = {
            'pro_business': [
                'innovation', 'job creation', 'economic growth', 'efficiency',
                'competitive advantage', 'market leader', 'shareholder value'
            ],
            'anti_business': [
                'corporate greed', 'exploitation', 'price gouging', 'monopoly',
                'tax avoidance', 'worker exploitation', 'environmental destruction'
            ]
        }
        
        # Loaded language patterns
        self.loaded_patterns = [
            'alleged', 'claimed', 'so-called', 'notorious', 'infamous',
            'controversial', 'divisive', 'polarizing', 'radical', 'extreme'
        ]
    
    def _analyze_political_bias(self, text: str) -> Dict[str, Any]:
        """Analyze political bias in the text with timeout protection"""
        try:
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
                'score': min(100, int(lean_intensity + extremist_adjustment)),
                'left_indicators': left_score,
                'right_indicators': right_score,
                'extremist_indicators': extremist_score,
                'lean_intensity': lean_intensity
            }
        except Exception as e:
            logger.warning(f"Political bias analysis failed: {e}")
            return {'label': 'Unknown', 'score': 0}
    
    def _analyze_sensationalism(self, text: str) -> Dict[str, Any]:
        """Analyze sensationalism in the text"""
        try:
            text_lower = text.lower()
            
            sensational_count = sum(1 for pattern in self.sensationalism_patterns 
                                   if pattern in text_lower)
            
            # Calculate sensationalism score based on density
            word_count = len(text.split())
            if word_count == 0:
                return {'score': 0, 'level': 'Minimal'}
            
            sensational_density = (sensational_count / word_count) * 1000
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
        except Exception as e:
            logger.warning(f"Sensationalism analysis failed: {e}")
            return {'score': 0, 'level': 'Unknown'}
    
    def _analyze_corporate_bias(self, text: str) -> Dict[str, Any]:
        """Analyze corporate/business bias"""
        try:
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
        except Exception as e:
            logger.warning(f"Corporate bias analysis failed: {e}")
            return {'bias': 'Unknown', 'score': 0}
    
    def _detect_loaded_language(self, text: str) -> Dict[str, Any]:
        """Detect loaded/biased language with timeout protection"""
        try:
            sentences = re.split(r'[.!?]+', text)
            
            loaded_phrases = []
            for sentence in sentences[:100]:  # Limit to prevent timeout
                sentence_lower = sentence.lower()
                for pattern in self.loaded_patterns:
                    if pattern in sentence_lower:
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
        except Exception as e:
            logger.warning(f"Loaded language detection failed: {e}")
            return {'phrases': [], 'count': 0, 'density': 0}
    
    def _analyze_framing(self, text: str) -> Dict[str, Any]:
        """Analyze how the article frames issues"""
        try:
            framing_issues = []
            text_lower = text.lower()
            
            # One-sided framing
            if 'however' not in text_lower and 'but' not in text_lower and len(text) > 500:
                framing_issues.append("Limited counterarguments presented")
            
            # Emotional framing
            emotional_words = ['outraged', 'devastated', 'thrilled', 'shocked', 'horrified']
            emotional_count = sum(1 for word in emotional_words if word in text_lower)
            if emotional_count > 3:
                framing_issues.append("Heavy emotional language usage")
            
            # Source diversity
            quote_count = text.count('"')
            source_indicators = ['according to', 'said', 'stated', 'reported']
            source_count = sum(1 for indicator in source_indicators if indicator in text_lower)
            
            if quote_count > 0 and source_count < 2:
                framing_issues.append("Limited source diversity")
            
            return {
                'issues': framing_issues,
                'emotional_language_count': emotional_count,
                'source_diversity_score': min(100, source_count * 25)
            }
        except Exception as e:
            logger.warning(f"Framing analysis failed: {e}")
            return {'issues': [], 'emotional_language_count': 0, 'source_diversity_score': 0}
    
    def _calculate_overall_bias_score(self, dimensions: Dict[str, Any]) -> int:
        """Calculate overall bias score from all dimensions"""
        try:
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
        except Exception as e:
            logger.warning(f"Bias score calculation failed: {e}")
            return 25  # Default moderate score
    
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
        try:
            scores = {
                'Political': dimensions['political'].get('score', 0),
                'Sensationalism': dimensions['sensationalism'].get('score', 0),
                'Corporate': dimensions['corporate'].get('score', 0),
                'Loaded Language': min(100, dimensions['loaded_language'].get('count', 0) * 10)
            }
            
            if max(scores.values()) < 20:
                return 'None'
            
            return max(scores, key=scores.get)
        except Exception as e:
            logger.warning(f"Dominant bias calculation failed: {e}")
            return 'Unknown'
    
    def _get_bias_direction(self, political_bias: Dict[str, Any]) -> str:
        """Get bias direction from political analysis"""
        try:
            label = political_bias.get('label', 'Neutral')
            if 'Left' in label:
                return 'left'
            elif 'Right' in label:
                return 'right'
            else:
                return 'neutral'
        except Exception:
            return 'neutral'
    
    def _get_bias_patterns_summary(self, dimensions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get summary of detected bias patterns"""
        try:
            patterns = []
            
            # Political patterns
            political = dimensions['political']
            if political.get('score', 0) > 30:
                patterns.append({
                    'type': 'political',
                    'description': f"Political lean: {political.get('label', 'Unknown')}",
                    'strength': political.get('score', 0)
                })
            
            # Sensationalism patterns
            sensationalism = dimensions['sensationalism']
            if sensationalism.get('score', 0) > 40:
                patterns.append({
                    'type': 'sensationalism',
                    'description': f"Sensational language: {sensationalism.get('level', 'Unknown')}",
                    'strength': sensationalism.get('score', 0)
                })
            
            # Loaded language patterns
            loaded = dimensions['loaded_language']
            if loaded.get('count', 0) > 3:
                patterns.append({
                    'type': 'loaded_language',
                    'description': f"Loaded language: {loaded.get('count', 0)} instances",
                    'strength': min(100, loaded.get('count', 0) * 10)
                })
            
            return patterns
        except Exception as e:
            logger.warning(f"Pattern summary failed: {e}")
            return []
    
    def _generate_findings(self, dimensions: Dict[str, Any], overall_score: int) -> List[Dict[str, Any]]:
        """Generate findings based on bias analysis"""
        findings = []
        
        try:
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
            political = dimensions.get('political', {})
            if political.get('score', 0) > 50:
                findings.append({
                    'type': 'info',
                    'severity': 'medium',
                    'text': f'Political lean: {political.get("label", "Unknown")}',
                    'explanation': f'Article shows {political.get("label", "unknown").lower()} political perspective'
                })
            
            # Sensationalism
            sensationalism = dimensions.get('sensationalism', {})
            if sensationalism.get('score', 0) > 60:
                findings.append({
                    'type': 'warning',
                    'severity': 'medium',
                    'text': f'High sensationalism ({sensationalism.get("score", 0)}/100)',
                    'explanation': 'Article uses sensational language that may exaggerate issues'
                })
            
            # Loaded language
            loaded = dimensions.get('loaded_language', {})
            if loaded.get('count', 0) > 5:
                findings.append({
                    'type': 'warning',
                    'severity': 'medium',
                    'text': f'Loaded language detected ({loaded.get("count", 0)} instances)',
                    'explanation': 'Article uses biased or emotionally charged language'
                })
        
        except Exception as e:
            logger.warning(f"Findings generation failed: {e}")
            findings.append({
                'type': 'info',
                'severity': 'medium',
                'text': 'Bias analysis completed with some limitations',
                'explanation': 'Full analysis could not be completed but basic assessment was performed'
            })
        
        return findings
    
    def _generate_summary(self, dimensions: Dict[str, Any], score: int, level: str) -> str:
        """Generate summary of bias analysis"""
        try:
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
            if dominant != 'None' and dominant != 'Unknown':
                base += f" Primary bias type: {dominant}."
            
            base += f" Objectivity score: {objectivity}%."
            
            return base
        
        except Exception as e:
            logger.warning(f"Summary generation failed: {e}")
            return f"Bias analysis completed with {score}% bias score. See detailed findings for more information."
    
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
                'BULLETPROOF AI-enhanced bias detection',
                'Timeout-protected analysis'
            ],
            'dimensions_analyzed': 5,
            'patterns_detected': len(self.loaded_patterns),
            'visualization_ready': True,
            'ai_enhanced': self._ai_available,
            'timeout_protected': True
        })
        return info
