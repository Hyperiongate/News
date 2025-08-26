"""
Content Analyzer Service - BULLETPROOF AI ENHANCED VERSION
Analyzes writing quality, structure, and professionalism with bulletproof AI insights
"""

import re
import logging
import time
import string
from typing import Dict, Any, List, Optional
from collections import Counter
import statistics

from services.base_analyzer import BaseAnalyzer
from services.ai_enhancement_mixin import AIEnhancementMixin

logger = logging.getLogger(__name__)


class ContentAnalyzer(BaseAnalyzer, AIEnhancementMixin):
    """Analyze content quality and structure WITH BULLETPROOF AI ENHANCEMENT"""
    
    def __init__(self):
        super().__init__('content_analyzer')
        AIEnhancementMixin.__init__(self)
        
        # Initialize analysis patterns
        self._initialize_content_patterns()
        
        logger.info(f"ContentAnalyzer initialized with AI enhancement: {self._ai_available}")
    
    def _check_availability(self) -> bool:
        """Service is always available"""
        return True
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze content quality WITH BULLETPROOF AI ENHANCEMENT
        
        Expected input:
            - text: Article text to analyze (required)
            - title: Article title (optional)
        """
        try:
            start_time = time.time()
            
            text = data.get('text', '')
            if not text:
                return self.get_error_result("No text provided for content analysis")
            
            title = data.get('title', '')
            full_text = f"{title}\n\n{text}" if title else text
            
            logger.info(f"Analyzing content quality in {len(full_text)} characters of text")
            
            # Core content analysis
            readability = self._analyze_readability(text)
            structure = self._analyze_structure(text)
            vocabulary = self._analyze_vocabulary(text)
            grammar = self._analyze_grammar(text)
            professionalism = self._analyze_professionalism(text)
            coherence = self._analyze_coherence(text)
            
            # Calculate overall content score
            content_metrics = {
                'readability': readability,
                'structure': structure,
                'vocabulary': vocabulary,
                'grammar': grammar,
                'professionalism': professionalism,
                'coherence': coherence
            }
            
            overall_score = self._calculate_content_score(content_metrics)
            quality_level = self._get_quality_level(overall_score)
            
            # Generate findings
            findings = self._generate_findings(content_metrics, overall_score)
            
            # Generate summary
            summary = self._generate_summary(content_metrics, overall_score, quality_level)
            
            # Build response
            result = {
                'service': self.service_name,
                'success': True,
                'data': {
                    'score': overall_score,
                    'level': quality_level,
                    'content_score': overall_score,
                    'quality_level': quality_level,
                    'findings': findings,
                    'summary': summary,
                    'metrics': content_metrics,
                    'readability_score': readability.get('score', 0),
                    'structure_score': structure.get('score', 0),
                    'vocabulary_score': vocabulary.get('score', 0),
                    'grammar_score': grammar.get('score', 0),
                    'professionalism_score': professionalism.get('score', 0),
                    'coherence_score': coherence.get('score', 0),
                    'word_count': len(text.split()),
                    'sentence_count': len(re.findall(r'[.!?]+', text)),
                    'paragraph_count': len(text.split('\n\n')),
                    'details': {
                        'avg_sentence_length': readability.get('avg_sentence_length', 0),
                        'vocabulary_diversity': vocabulary.get('diversity_score', 0),
                        'complex_words': vocabulary.get('complex_word_count', 0),
                        'grammar_issues': grammar.get('issue_count', 0),
                        'structure_elements': len(structure.get('elements_found', [])),
                        'professionalism_indicators': len(professionalism.get('indicators', []))
                    }
                },
                'metadata': {
                    'analysis_time': time.time() - start_time,
                    'text_length': len(text),
                    'analyzed_with_title': bool(title)
                }
            }
            
            # BULLETPROOF AI ENHANCEMENT
            if text:
                logger.info("Enhancing content analysis with AI insights")
                
                result = self._safely_enhance_service_result(
                    result,
                    '_ai_analyze_content_quality',
                    text=text[:1000],
                    metrics=content_metrics
                )
            
            logger.info(f"Content analysis complete: {overall_score}/100 ({quality_level})")
            return result
            
        except Exception as e:
            logger.error(f"Content analysis failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _initialize_content_patterns(self):
        """Initialize patterns for content analysis"""
        
        # Professional indicators
        self.professional_indicators = [
            'according to', 'data shows', 'research indicates', 'study found',
            'analysis reveals', 'experts say', 'evidence suggests'
        ]
        
        # Grammar issue patterns (simplified)
        self.grammar_patterns = [
            r'\b(there|their|they\'re)\b',  # Common confusion words
            r'\b(your|you\'re)\b',
            r'\b(its|it\'s)\b',
            r'\s{2,}',  # Multiple spaces
            r'[.!?]{2,}',  # Multiple punctuation
        ]
        
        # Structure elements
        self.structure_elements = [
            'introduction', 'background', 'methodology', 'results',
            'conclusion', 'summary', 'analysis', 'discussion'
        ]
    
    def _analyze_readability(self, text: str) -> Dict[str, Any]:
        """Analyze text readability"""
        
        # Basic readability metrics
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        words = text.split()
        
        if not sentences or not words:
            return {'score': 0, 'level': 'Poor', 'avg_sentence_length': 0}
        
        avg_sentence_length = len(words) / len(sentences)
        
        # Simple readability score based on sentence length
        if avg_sentence_length <= 15:
            readability_score = 90  # Very easy
        elif avg_sentence_length <= 20:
            readability_score = 75  # Easy
        elif avg_sentence_length <= 25:
            readability_score = 60  # Moderate
        elif avg_sentence_length <= 30:
            readability_score = 45  # Difficult
        else:
            readability_score = 30  # Very difficult
        
        # Adjust for very short or very long sentences
        sentence_lengths = [len(s.split()) for s in sentences]
        if sentence_lengths:
            length_variance = statistics.stdev(sentence_lengths) if len(sentence_lengths) > 1 else 0
            if length_variance > 15:  # High variance is good
                readability_score += 10
        
        readability_level = self._get_readability_level(readability_score)
        
        return {
            'score': min(100, int(readability_score)),
            'level': readability_level,
            'avg_sentence_length': round(avg_sentence_length, 1),
            'sentence_count': len(sentences),
            'word_count': len(words),
            'length_variance': round(length_variance, 1) if sentence_lengths else 0
        }
    
    def _analyze_structure(self, text: str) -> Dict[str, Any]:
        """Analyze text structure"""
        
        text_lower = text.lower()
        paragraphs = text.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        elements_found = []
        structure_indicators = []
        
        # Check for structural elements
        for element in self.structure_elements:
            if element in text_lower:
                elements_found.append(element)
                structure_indicators.append(f"Contains {element} section")
        
        # Analyze paragraph structure
        if len(paragraphs) >= 3:
            structure_indicators.append("Well-structured paragraphs")
        elif len(paragraphs) >= 1:
            structure_indicators.append("Basic paragraph structure")
        else:
            structure_indicators.append("Poor paragraph structure")
        
        # Check for transitions
        transition_words = ['however', 'therefore', 'moreover', 'furthermore', 'additionally']
        transition_count = sum(1 for word in transition_words if word in text_lower)
        if transition_count >= 2:
            structure_indicators.append("Good use of transitions")
        
        # Calculate structure score
        structure_score = min(100, 
                            (len(elements_found) * 15) +
                            (len(paragraphs) * 5) +
                            (transition_count * 10) +
                            20  # Base score
                            )
        
        return {
            'score': int(structure_score),
            'paragraph_count': len(paragraphs),
            'elements_found': elements_found,
            'transition_count': transition_count,
            'indicators': structure_indicators,
            'avg_paragraph_length': sum(len(p.split()) for p in paragraphs) / max(len(paragraphs), 1)
        }
    
    def _analyze_vocabulary(self, text: str) -> Dict[str, Any]:
        """Analyze vocabulary diversity and complexity"""
        
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        if not words:
            return {'score': 0, 'diversity_score': 0, 'complex_word_count': 0}
        
        # Vocabulary diversity (unique words / total words)
        unique_words = set(words)
        diversity_ratio = len(unique_words) / len(words)
        diversity_score = min(100, diversity_ratio * 200)  # Scale to 0-100
        
        # Complex words (6+ letters)
        complex_words = [w for w in words if len(w) >= 6]
        complex_ratio = len(complex_words) / len(words)
        complexity_score = min(100, complex_ratio * 300)
        
        # Overall vocabulary score
        vocab_score = (diversity_score * 0.6) + (complexity_score * 0.4)
        
        return {
            'score': int(vocab_score),
            'diversity_score': round(diversity_score, 1),
            'complexity_score': round(complexity_score, 1),
            'unique_words': len(unique_words),
            'total_words': len(words),
            'complex_word_count': len(complex_words),
            'diversity_ratio': round(diversity_ratio, 3)
        }
    
    def _analyze_grammar(self, text: str) -> Dict[str, Any]:
        """Analyze grammar and writing mechanics"""
        
        issues_found = []
        issue_count = 0
        
        # Check for multiple spaces
        if re.search(r'\s{2,}', text):
            issues_found.append("Multiple spaces found")
            issue_count += len(re.findall(r'\s{2,}', text))
        
        # Check for multiple punctuation
        if re.search(r'[.!?]{2,}', text):
            issues_found.append("Multiple punctuation marks")
            issue_count += len(re.findall(r'[.!?]{2,}', text))
        
        # Check capitalization after periods
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences[1:]:  # Skip first
            sentence = sentence.strip()
            if sentence and sentence[0].islower():
                issues_found.append("Capitalization issues")
                issue_count += 1
                break
        
        # Simple grammar score based on issues found
        word_count = len(text.split())
        if word_count > 0:
            error_rate = issue_count / word_count
            grammar_score = max(0, 100 - (error_rate * 1000))  # Penalize errors
        else:
            grammar_score = 0
        
        return {
            'score': int(grammar_score),
            'issue_count': issue_count,
            'issues_found': issues_found[:5],  # Top 5 issues
            'error_rate': round(error_rate, 4) if word_count > 0 else 0
        }
    
    def _analyze_professionalism(self, text: str) -> Dict[str, Any]:
        """Analyze professional writing indicators"""
        
        text_lower = text.lower()
        indicators = []
        professional_score = 50  # Base score
        
        # Check for professional phrases
        for indicator in self.professional_indicators:
            if indicator in text_lower:
                indicators.append(f"Uses professional phrase: '{indicator}'")
                professional_score += 5
        
        # Check for citations or references
        if re.search(r'\([^)]*\d{4}[^)]*\)', text):  # Year in parentheses
            indicators.append("Contains citations")
            professional_score += 15
        
        # Check for statistics or data
        if re.search(r'\d+%|\d+\s*percent', text):
            indicators.append("Includes statistical data")
            professional_score += 10
        
        # Check for quotes
        if '"' in text:
            indicators.append("Uses quotations")
            professional_score += 5
        
        # Penalize unprofessional language
        unprofessional_words = ['awesome', 'totally', 'super', 'really really']
        unprofessional_count = sum(1 for word in unprofessional_words if word in text_lower)
        professional_score -= unprofessional_count * 5
        
        professional_score = max(0, min(100, professional_score))
        
        return {
            'score': int(professional_score),
            'indicators': indicators,
            'unprofessional_count': unprofessional_count,
            'citation_found': bool(re.search(r'\([^)]*\d{4}[^)]*\)', text)),
            'statistics_found': bool(re.search(r'\d+%|\d+\s*percent', text))
        }
    
    def _analyze_coherence(self, text: str) -> Dict[str, Any]:
        """Analyze text coherence and flow"""
        
        paragraphs = text.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        coherence_indicators = []
        coherence_score = 50  # Base score
        
        # Check paragraph consistency
        if len(paragraphs) > 1:
            paragraph_lengths = [len(p.split()) for p in paragraphs]
            avg_length = sum(paragraph_lengths) / len(paragraph_lengths)
            
            # Penalize extremely short or long paragraphs
            reasonable_paragraphs = sum(1 for length in paragraph_lengths 
                                     if 20 <= length <= 150)
            consistency_ratio = reasonable_paragraphs / len(paragraphs)
            
            if consistency_ratio > 0.8:
                coherence_indicators.append("Consistent paragraph lengths")
                coherence_score += 15
            elif consistency_ratio > 0.5:
                coherence_indicators.append("Mostly consistent paragraphs")
                coherence_score += 10
        
        # Check for logical connectors
        connectors = ['therefore', 'however', 'furthermore', 'additionally', 'consequently']
        connector_count = sum(1 for connector in connectors if connector in text.lower())
        
        if connector_count >= 3:
            coherence_indicators.append("Good use of logical connectors")
            coherence_score += 20
        elif connector_count >= 1:
            coherence_indicators.append("Some logical connectors")
            coherence_score += 10
        
        # Check for topic consistency (simple keyword analysis)
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        if len(words) > 50:  # Only for substantial text
            word_freq = Counter(words)
            # Remove common words
            common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must', 'a', 'an', 'this', 'that', 'these', 'those'}
            content_words = {word: freq for word, freq in word_freq.items() 
                           if word not in common_words and len(word) > 3}
            
            if content_words:
                top_words = sorted(content_words.items(), key=lambda x: x[1], reverse=True)[:5]
                topic_consistency = sum(freq for _, freq in top_words) / len(words)
                
                if topic_consistency > 0.1:
                    coherence_indicators.append("Strong topic consistency")
                    coherence_score += 15
        
        coherence_score = max(0, min(100, coherence_score))
        
        return {
            'score': int(coherence_score),
            'indicators': coherence_indicators,
            'connector_count': connector_count,
            'paragraph_consistency': consistency_ratio if len(paragraphs) > 1 else 1.0
        }
    
    def _calculate_content_score(self, metrics: Dict[str, Any]) -> int:
        """Calculate overall content quality score"""
        
        # Weight different aspects
        weights = {
            'readability': 0.2,
            'structure': 0.2,
            'vocabulary': 0.15,
            'grammar': 0.2,
            'professionalism': 0.15,
            'coherence': 0.1
        }
        
        total_score = 0
        for metric_name, weight in weights.items():
            metric_score = metrics.get(metric_name, {}).get('score', 0)
            total_score += metric_score * weight
        
        return min(100, int(total_score))
    
    def _get_quality_level(self, score: int) -> str:
        """Convert score to quality level"""
        if score >= 85:
            return 'Excellent'
        elif score >= 70:
            return 'Good'
        elif score >= 55:
            return 'Fair'
        elif score >= 40:
            return 'Poor'
        else:
            return 'Very Poor'
    
    def _get_readability_level(self, score: int) -> str:
        """Convert readability score to level"""
        if score >= 80:
            return 'Very Easy'
        elif score >= 60:
            return 'Easy'
        elif score >= 40:
            return 'Moderate'
        elif score >= 20:
            return 'Difficult'
        else:
            return 'Very Difficult'
    
    def _generate_findings(self, metrics: Dict[str, Any], overall_score: int) -> List[Dict[str, Any]]:
        """Generate findings based on content analysis"""
        findings = []
        
        # Overall assessment
        if overall_score >= 80:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': f'Excellent content quality ({overall_score}/100)',
                'explanation': 'Article demonstrates professional writing standards'
            })
        elif overall_score >= 60:
            findings.append({
                'type': 'info',
                'severity': 'medium',
                'text': f'Good content quality ({overall_score}/100)',
                'explanation': 'Article meets most professional writing standards'
            })
        else:
            findings.append({
                'type': 'warning',
                'severity': 'medium',
                'text': f'Poor content quality ({overall_score}/100)',
                'explanation': 'Article has significant writing quality issues'
            })
        
        # Specific metric findings
        readability = metrics['readability']
        if readability['score'] < 40:
            findings.append({
                'type': 'warning',
                'severity': 'medium',
                'text': f'Poor readability ({readability["score"]}/100)',
                'explanation': f'Average sentence length: {readability["avg_sentence_length"]} words'
            })
        elif readability['score'] > 80:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': f'Excellent readability ({readability["score"]}/100)',
                'explanation': 'Text is easy to read and understand'
            })
        
        # Grammar findings
        grammar = metrics['grammar']
        if grammar['issue_count'] > 5:
            findings.append({
                'type': 'warning',
                'severity': 'high',
                'text': f'Grammar issues detected ({grammar["issue_count"]})',
                'explanation': 'Multiple writing mechanics problems found'
            })
        
        # Professional findings
        professionalism = metrics['professionalism']
        if professionalism['score'] > 75:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': 'Professional writing style',
                'explanation': 'Uses appropriate professional language and citations'
            })
        
        return findings
    
    def _generate_summary(self, metrics: Dict[str, Any], score: int, level: str) -> str:
        """Generate summary of content analysis"""
        
        if score >= 80:
            base = "This article demonstrates excellent writing quality with professional standards. "
        elif score >= 60:
            base = "This article shows good writing quality with most professional elements present. "
        elif score >= 40:
            base = "This article has fair writing quality but could be improved. "
        else:
            base = "This article has poor writing quality with significant issues. "
        
        # Add specific details
        readability = metrics['readability']
        base += f"Readability: {readability['level']}. "
        
        structure = metrics['structure']
        base += f"Structure: {structure['paragraph_count']} paragraphs. "
        
        professionalism = metrics['professionalism']
        if professionalism['citation_found']:
            base += "Includes citations. "
        
        base += f"Overall content score: {score}/100."
        
        return base
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        info = super().get_service_info()
        info.update({
            'capabilities': [
                'Readability analysis',
                'Text structure evaluation',
                'Vocabulary diversity assessment',
                'Grammar and mechanics checking',
                'Professional writing analysis',
                'Coherence and flow evaluation',
                'BULLETPROOF AI-enhanced content quality assessment'
            ],
            'metrics_analyzed': [
                'readability',
                'structure',
                'vocabulary',
                'grammar',
                'professionalism',
                'coherence'
            ],
            'ai_enhanced': self._ai_available
        })
        return info
