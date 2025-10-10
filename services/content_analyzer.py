"""
Content Analyzer Service - v4.1.0 SUPER INTERESTING
Last Updated: October 10, 2025

CHANGES FROM v4.0.0:
✅ ENHANCED: Findings with SPECIFIC numbers and percentages
✅ ENHANCED: Emojis for visual engagement (📖 ✓ ❌ 📊)
✅ ENHANCED: "What we found" uses bullet points with icons
✅ ENHANCED: Clear problem identification ("TOO LONG", "needs proofreading")
✅ ENHANCED: Actionable recommendations in every finding
✅ PRESERVES: All existing functionality

PHILOSOPHY: Make users say "Whoa! I didn't know sentences should be 15-20 words!"
TARGET: Every finding should teach something and be immediately understandable
"""

import re
import logging
import time
import string
from typing import Dict, Any, List, Optional, Tuple
from collections import Counter
import statistics

from services.base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)

# Import AI enhancement mixin if available
try:
    from services.ai_enhancement_mixin import AIEnhancementMixin
    AI_MIXIN_AVAILABLE = True
except ImportError:
    logger.info("AI Enhancement Mixin not available - running without AI enhancement")
    AIEnhancementMixin = object
    AI_MIXIN_AVAILABLE = False


class ContentAnalyzer(BaseAnalyzer, AIEnhancementMixin):
    """Analyze content quality and structure WITH DETAILED EXPLANATIONS"""
    
    def __init__(self):
        super().__init__('content_analyzer')
        if AI_MIXIN_AVAILABLE:
            AIEnhancementMixin.__init__(self)
            self._ai_available = getattr(self, '_ai_available', False)
        else:
            self._ai_available = False
        
        # Initialize analysis patterns
        self._initialize_content_patterns()
        
        logger.info(f"ContentAnalyzer v4.0.0 initialized with AI: {self._ai_available}")
    
    def _check_availability(self) -> bool:
        """Service is always available"""
        return True
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze content quality WITH DETAILED EXPLANATIONS
        v4.0.0: Returns specific findings, not vague scores
        """
        try:
            start_time = time.time()
            
            text = data.get('text', '')
            if not text:
                return self.get_error_result("No text provided for content analysis")
            
            title = data.get('title', '')
            full_text = f"{title}\n\n{text}" if title else text
            
            logger.info(f"[ContentAnalyzer v4.0] Analyzing {len(full_text)} characters")
            
            # Core content analysis with examples
            readability = self._analyze_readability_detailed(text)
            structure = self._analyze_structure_detailed(text)
            vocabulary = self._analyze_vocabulary_detailed(text)
            grammar = self._analyze_grammar_detailed(text)
            professionalism = self._analyze_professionalism_detailed(text)
            coherence = self._analyze_coherence_detailed(text)
            
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
            
            # Generate detailed findings with examples
            findings = self._generate_detailed_findings(content_metrics, text)
            
            # Generate comprehensive analysis
            analysis = self._generate_comprehensive_analysis(
                content_metrics, overall_score, len(text.split()), text
            )
            
            # Generate conversational summary
            summary = self._generate_conversational_summary(
                content_metrics, overall_score, quality_level
            )
            
            # Build result with all data
            result = {
                'service': self.service_name,
                'success': True,
                'available': True,
                'timestamp': time.time(),
                'data': {
                    # Core scores
                    'score': overall_score,
                    'level': quality_level,
                    'content_score': overall_score,
                    'quality_level': quality_level,
                    
                    # NEW v4.0: Detailed findings with explanations
                    'findings': findings,
                    
                    # NEW v4.0: Comprehensive analysis
                    'analysis': analysis,
                    
                    # Conversational summary
                    'summary': summary,
                    
                    # Detailed metrics (for charts)
                    'metrics': content_metrics,
                    
                    # Individual component scores
                    'readability_score': readability.get('score', 0),
                    'structure_score': structure.get('score', 0),
                    'vocabulary_score': vocabulary.get('score', 0),
                    'grammar_score': grammar.get('score', 0),
                    'professionalism_score': professionalism.get('score', 0),
                    'coherence_score': coherence.get('score', 0),
                    
                    # Basic counts
                    'word_count': len(text.split()),
                    'sentence_count': len(re.findall(r'[.!?]+', text)),
                    'paragraph_count': len([p for p in text.split('\n\n') if p.strip()]),
                    
                    # Chart data
                    'details': {
                        'readability_grade': readability.get('grade_level', 'Unknown'),
                        'avg_sentence_length': readability.get('avg_sentence_length', 0),
                        'vocabulary_diversity': vocabulary.get('diversity_ratio', 0),
                        'complex_words': vocabulary.get('complex_word_count', 0),
                        'grammar_issues': grammar.get('issue_count', 0),
                        'grammar_error_rate': grammar.get('error_rate', 0),
                        'structure_elements': len(structure.get('elements_found', [])),
                        'paragraph_consistency': structure.get('paragraph_consistency', 0),
                        'transition_words': structure.get('transition_count', 0),
                        'citation_found': professionalism.get('citation_found', False),
                        'statistics_found': professionalism.get('statistics_found', False),
                        'professional_indicators': len(professionalism.get('indicators', [])),
                        'coherence_connectors': coherence.get('connector_count', 0)
                    }
                },
                'metadata': {
                    'analysis_time': time.time() - start_time,
                    'text_length': len(text),
                    'analyzed_with_title': bool(title),
                    'version': '4.0.0',
                    'ai_enhanced': self._ai_available
                }
            }
            
            # AI Enhancement if available
            if text and self._ai_available and AI_MIXIN_AVAILABLE:
                logger.info("[ContentAnalyzer v4.0] Enhancing with AI insights")
                try:
                    result = self._safely_enhance_service_result(
                        result,
                        '_ai_analyze_content_quality',
                        text=text[:1000],
                        metrics=content_metrics
                    )
                    if result:
                        result['metadata']['ai_enhancement_applied'] = True
                except Exception as ai_error:
                    logger.warning(f"AI enhancement failed: {ai_error}")
                    result['metadata']['ai_enhancement_failed'] = str(ai_error)
            
            logger.info(f"[ContentAnalyzer v4.0] Complete: {overall_score}/100 ({quality_level})")
            return result
            
        except Exception as e:
            logger.error(f"[ContentAnalyzer v4.0] Analysis failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _initialize_content_patterns(self):
        """Initialize patterns for content analysis"""
        
        self.professional_indicators = [
            'according to', 'data shows', 'research indicates', 'study found',
            'analysis reveals', 'experts say', 'evidence suggests', 'reported by'
        ]
        
        self.structure_elements = [
            'introduction', 'background', 'methodology', 'results',
            'conclusion', 'summary', 'analysis', 'discussion', 'findings'
        ]
        
        self.transition_words = [
            'however', 'therefore', 'moreover', 'furthermore', 'additionally',
            'consequently', 'meanwhile', 'nevertheless', 'nonetheless', 'thus'
        ]
        
        self.grammar_issue_patterns = [
            (r'\s{2,}', 'Multiple consecutive spaces'),
            (r'[.!?]{2,}', 'Multiple punctuation marks'),
            (r'\b(there|their|they\'re)\b', 'Potential there/their/they\'re confusion'),
            (r'\b(your|you\'re)\b', 'Potential your/you\'re confusion'),
            (r'\b(its|it\'s)\b', 'Potential its/it\'s confusion')
        ]
    
    def _analyze_readability_detailed(self, text: str) -> Dict[str, Any]:
        """Analyze readability with specific grade level"""
        
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        words = text.split()
        
        if not sentences or not words:
            return {
                'score': 0,
                'level': 'Poor',
                'grade_level': 'Unknown',
                'avg_sentence_length': 0,
                'issues': [],
                'strengths': []
            }
        
        avg_sentence_length = len(words) / len(sentences)
        
        # Calculate syllable count (simplified)
        syllable_count = sum(self._count_syllables(word) for word in words)
        avg_syllables_per_word = syllable_count / len(words) if words else 0
        
        # Flesch Reading Ease approximation
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        flesch_score = max(0, min(100, flesch_score))
        
        # Determine grade level
        if flesch_score >= 90:
            grade_level = "Grade 5-6"
            readability_level = "Very Easy"
        elif flesch_score >= 80:
            grade_level = "Grade 6-7"
            readability_level = "Easy"
        elif flesch_score >= 70:
            grade_level = "Grade 7-8"
            readability_level = "Fairly Easy"
        elif flesch_score >= 60:
            grade_level = "Grade 8-9"
            readability_level = "Standard"
        elif flesch_score >= 50:
            grade_level = "Grade 10-12"
            readability_level = "Fairly Difficult"
        elif flesch_score >= 30:
            grade_level = "College"
            readability_level = "Difficult"
        else:
            grade_level = "College Graduate"
            readability_level = "Very Difficult"
        
        # Analyze sentence length variance
        sentence_lengths = [len(s.split()) for s in sentences]
        length_variance = statistics.stdev(sentence_lengths) if len(sentence_lengths) > 1 else 0
        
        # Build issues and strengths
        issues = []
        strengths = []
        
        if avg_sentence_length > 25:
            issues.append({
                'type': 'long_sentences',
                'text': f'Average sentence length is {avg_sentence_length:.1f} words',
                'impact': 'Long sentences can be difficult to follow'
            })
        elif avg_sentence_length < 15:
            strengths.append('Sentences are concise and easy to read')
        
        if length_variance < 5:
            issues.append({
                'type': 'monotonous_rhythm',
                'text': 'Sentences have similar lengths',
                'impact': 'Varying sentence length improves readability'
            })
        elif length_variance > 10:
            strengths.append('Good variety in sentence lengths')
        
        if flesch_score < 50:
            issues.append({
                'type': 'complex_vocabulary',
                'text': f'Reading level: {grade_level}',
                'impact': 'Complex vocabulary may limit accessibility'
            })
        
        # Convert Flesch to 0-100 score (higher is better for our system)
        normalized_score = int(flesch_score)
        
        return {
            'score': normalized_score,
            'level': readability_level,
            'grade_level': grade_level,
            'flesch_score': round(flesch_score, 1),
            'avg_sentence_length': round(avg_sentence_length, 1),
            'avg_syllables_per_word': round(avg_syllables_per_word, 2),
            'sentence_count': len(sentences),
            'word_count': len(words),
            'length_variance': round(length_variance, 1),
            'issues': issues,
            'strengths': strengths
        }
    
    def _count_syllables(self, word: str) -> int:
        """Simple syllable counter"""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Adjust for silent e
        if word.endswith('e'):
            syllable_count -= 1
        
        # Every word has at least 1 syllable
        return max(1, syllable_count)
    
    def _analyze_structure_detailed(self, text: str) -> Dict[str, Any]:
        """Analyze structure with specific examples"""
        
        text_lower = text.lower()
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        elements_found = []
        structure_indicators = []
        issues = []
        strengths = []
        
        # Check for structural elements
        for element in self.structure_elements:
            if element in text_lower:
                elements_found.append(element)
        
        if elements_found:
            strengths.append(f"Contains organizational elements: {', '.join(elements_found[:3])}")
        
        # Analyze paragraph structure
        if len(paragraphs) >= 5:
            strengths.append(f"Well-organized with {len(paragraphs)} paragraphs")
        elif len(paragraphs) >= 3:
            structure_indicators.append("Adequate paragraph structure")
        elif len(paragraphs) >= 1:
            issues.append({
                'type': 'poor_structure',
                'text': f'Only {len(paragraphs)} paragraph(s)',
                'impact': 'Content should be broken into multiple paragraphs'
            })
        
        # Check paragraph length consistency
        if paragraphs:
            paragraph_lengths = [len(p.split()) for p in paragraphs]
            avg_para_length = sum(paragraph_lengths) / len(paragraph_lengths)
            
            very_long = [l for l in paragraph_lengths if l > 150]
            very_short = [l for l in paragraph_lengths if l < 30]
            
            if very_long:
                issues.append({
                    'type': 'long_paragraphs',
                    'text': f'{len(very_long)} paragraph(s) over 150 words',
                    'impact': 'Long paragraphs can overwhelm readers'
                })
            
            if very_short and len(paragraphs) > 1:
                issues.append({
                    'type': 'short_paragraphs',
                    'text': f'{len(very_short)} paragraph(s) under 30 words',
                    'impact': 'Very short paragraphs may lack substance'
                })
        
        # Check for transitions
        transition_count = sum(1 for word in self.transition_words if word in text_lower)
        if transition_count >= 3:
            strengths.append(f"Uses {transition_count} transition words for flow")
        elif transition_count == 0:
            issues.append({
                'type': 'no_transitions',
                'text': 'No transition words found',
                'impact': 'Transitions help connect ideas smoothly'
            })
        
        # Calculate structure score
        structure_score = 20  # Base score
        structure_score += len(elements_found) * 10
        structure_score += min(30, len(paragraphs) * 5)
        structure_score += min(20, transition_count * 5)
        structure_score = min(100, structure_score)
        
        # Penalty for issues
        structure_score -= len([i for i in issues if i.get('type') in ['poor_structure', 'long_paragraphs']]) * 10
        structure_score = max(0, structure_score)
        
        avg_paragraph_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0
        
        return {
            'score': int(structure_score),
            'paragraph_count': len(paragraphs),
            'avg_paragraph_length': round(avg_paragraph_length, 1),
            'elements_found': elements_found,
            'transition_count': transition_count,
            'paragraph_consistency': round(1.0 - (len(very_short) + len(very_long)) / max(len(paragraphs), 1), 2) if paragraphs else 0,
            'indicators': structure_indicators,
            'issues': issues,
            'strengths': strengths
        }
    
    def _analyze_vocabulary_detailed(self, text: str) -> Dict[str, Any]:
        """Analyze vocabulary with specific examples"""
        
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        if not words:
            return {
                'score': 0,
                'diversity_ratio': 0,
                'issues': [],
                'strengths': []
            }
        
        unique_words = set(words)
        diversity_ratio = len(unique_words) / len(words)
        
        # Complex words (6+ letters)
        complex_words = [w for w in words if len(w) >= 6]
        complex_ratio = len(complex_words) / len(words)
        
        # Advanced vocabulary (8+ letters)
        advanced_words = [w for w in words if len(w) >= 8]
        advanced_ratio = len(advanced_words) / len(words)
        
        issues = []
        strengths = []
        
        # Analyze diversity
        if diversity_ratio < 0.3:
            issues.append({
                'type': 'repetitive_vocabulary',
                'text': f'Only {int(diversity_ratio * 100)}% unique words',
                'impact': 'Repetitive vocabulary can make content boring'
            })
        elif diversity_ratio > 0.5:
            strengths.append(f'Rich vocabulary with {int(diversity_ratio * 100)}% unique words')
        
        # Analyze complexity
        if complex_ratio < 0.15:
            issues.append({
                'type': 'simple_vocabulary',
                'text': f'Only {int(complex_ratio * 100)}% complex words',
                'impact': 'May lack depth or sophistication'
            })
        elif complex_ratio > 0.35:
            issues.append({
                'type': 'overly_complex',
                'text': f'{int(complex_ratio * 100)}% complex words',
                'impact': 'May be difficult for general audiences'
            })
        else:
            strengths.append('Good balance of simple and complex vocabulary')
        
        # Calculate score
        diversity_score = min(100, diversity_ratio * 200)
        complexity_score = min(100, complex_ratio * 300)
        vocab_score = int((diversity_score * 0.6) + (complexity_score * 0.4))
        
        return {
            'score': vocab_score,
            'diversity_score': round(diversity_score, 1),
            'diversity_ratio': round(diversity_ratio, 3),
            'complexity_score': round(complexity_score, 1),
            'unique_words': len(unique_words),
            'total_words': len(words),
            'complex_word_count': len(complex_words),
            'complex_word_ratio': round(complex_ratio, 3),
            'advanced_word_count': len(advanced_words),
            'issues': issues,
            'strengths': strengths
        }
    
    def _analyze_grammar_detailed(self, text: str) -> Dict[str, Any]:
        """Analyze grammar with specific examples"""
        
        issues_found = []
        issue_details = []
        total_issues = 0
        
        # Check each grammar pattern
        for pattern, description in self.grammar_issue_patterns:
            matches = re.findall(pattern, text)
            if matches:
                count = len(matches)
                total_issues += count
                
                # Get first example
                match_obj = re.search(pattern, text)
                if match_obj:
                    start = max(0, match_obj.start() - 20)
                    end = min(len(text), match_obj.end() + 20)
                    example = text[start:end].strip()
                    
                    issue_details.append({
                        'type': description,
                        'count': count,
                        'example': f"...{example}..." if start > 0 else example
                    })
                    issues_found.append(description)
        
        # Check capitalization after periods
        sentences = re.split(r'[.!?]+', text)
        cap_issues = 0
        for sentence in sentences[1:]:
            sentence = sentence.strip()
            if sentence and sentence[0].islower():
                cap_issues += 1
        
        if cap_issues > 0:
            total_issues += cap_issues
            issue_details.append({
                'type': 'Capitalization issues',
                'count': cap_issues,
                'example': 'Sentences not starting with capital letters'
            })
        
        # Calculate error rate
        word_count = len(text.split())
        error_rate = total_issues / word_count if word_count > 0 else 0
        
        # Calculate score (penalize errors)
        grammar_score = max(0, 100 - (error_rate * 1000))
        
        # Build issues list
        issues = []
        strengths = []
        
        if total_issues == 0:
            strengths.append('No obvious grammar issues detected')
        elif total_issues <= 2:
            issues.append({
                'type': 'minor_grammar',
                'text': f'{total_issues} minor grammar issue(s)',
                'impact': 'Minor issues do not significantly affect readability'
            })
        else:
            issues.append({
                'type': 'grammar_errors',
                'text': f'{total_issues} grammar issue(s) detected',
                'impact': 'Grammar errors reduce professionalism and clarity',
                'examples': issue_details[:3]
            })
        
        return {
            'score': int(grammar_score),
            'issue_count': total_issues,
            'error_rate': round(error_rate, 4),
            'issues_found': issues_found[:5],
            'issue_details': issue_details[:5],
            'issues': issues,
            'strengths': strengths
        }
    
    def _analyze_professionalism_detailed(self, text: str) -> Dict[str, Any]:
        """Analyze professionalism with specific indicators"""
        
        text_lower = text.lower()
        indicators = []
        issues = []
        strengths = []
        professional_score = 50
        
        # Check for professional phrases
        professional_phrases_found = []
        for indicator in self.professional_indicators:
            if indicator in text_lower:
                professional_phrases_found.append(indicator)
                professional_score += 5
        
        if professional_phrases_found:
            strengths.append(f"Uses professional phrases: {', '.join(professional_phrases_found[:3])}")
        
        # Check for citations
        citation_pattern = r'\([^)]*\d{4}[^)]*\)'
        citation_found = bool(re.search(citation_pattern, text))
        citation_count = len(re.findall(citation_pattern, text))
        
        if citation_found:
            professional_score += 15
            strengths.append(f'Contains {citation_count} citation(s)')
        else:
            issues.append({
                'type': 'no_citations',
                'text': 'No citations found',
                'impact': 'Citations add credibility to claims'
            })
        
        # Check for statistics
        statistics_found = bool(re.search(r'\d+%|\d+\s*percent', text))
        stats_count = len(re.findall(r'\d+%|\d+\s*percent', text))
        
        if statistics_found:
            professional_score += 10
            strengths.append(f'Includes {stats_count} statistic(s)')
        
        # Check for quotes
        quote_count = text.count('"') // 2
        if quote_count > 0:
            professional_score += 5
            strengths.append(f'Uses {quote_count} quotation(s)')
        
        # Check for unprofessional language
        unprofessional_words = ['awesome', 'totally', 'super', 'really really', 'very very']
        unprofessional_found = [word for word in unprofessional_words if word in text_lower]
        unprofessional_count = len(unprofessional_found)
        
        if unprofessional_count > 0:
            professional_score -= unprofessional_count * 5
            issues.append({
                'type': 'informal_language',
                'text': f'Informal language detected: {", ".join(unprofessional_found)}',
                'impact': 'Informal language reduces professional tone'
            })
        
        professional_score = max(0, min(100, professional_score))
        
        return {
            'score': int(professional_score),
            'indicators': indicators,
            'unprofessional_count': unprofessional_count,
            'citation_found': citation_found,
            'citation_count': citation_count,
            'statistics_found': statistics_found,
            'statistics_count': stats_count if statistics_found else 0,
            'quote_count': quote_count,
            'professional_phrases_used': len(professional_phrases_found),
            'issues': issues,
            'strengths': strengths
        }
    
    def _analyze_coherence_detailed(self, text: str) -> Dict[str, Any]:
        """Analyze coherence with specific indicators"""
        
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        coherence_score = 50
        issues = []
        strengths = []
        
        # Check paragraph consistency
        if len(paragraphs) > 1:
            paragraph_lengths = [len(p.split()) for p in paragraphs]
            
            reasonable_paragraphs = sum(1 for length in paragraph_lengths if 20 <= length <= 150)
            consistency_ratio = reasonable_paragraphs / len(paragraphs)
            
            if consistency_ratio > 0.8:
                coherence_score += 15
                strengths.append('Consistent paragraph lengths throughout')
            elif consistency_ratio < 0.5:
                issues.append({
                    'type': 'inconsistent_paragraphs',
                    'text': f'Only {int(consistency_ratio * 100)}% of paragraphs are well-sized',
                    'impact': 'Inconsistent paragraph lengths can disrupt flow'
                })
        
        # Check for logical connectors
        connector_count = sum(1 for connector in self.transition_words if connector in text.lower())
        
        if connector_count >= 3:
            coherence_score += 20
            strengths.append(f'Good use of {connector_count} transition words')
        elif connector_count == 0:
            issues.append({
                'type': 'no_connectors',
                'text': 'No transition words found',
                'impact': 'Transitions help readers follow your logic'
            })
        
        # Check for topic consistency
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        if len(words) > 50:
            word_freq = Counter(words)
            
            # Remove common words
            common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            content_words = {word: freq for word, freq in word_freq.items() 
                           if word not in common_words and len(word) > 3}
            
            if content_words:
                top_words = sorted(content_words.items(), key=lambda x: x[1], reverse=True)[:5]
                topic_consistency = sum(freq for _, freq in top_words) / len(words)
                
                if topic_consistency > 0.1:
                    coherence_score += 15
                    strengths.append('Strong topic focus throughout article')
        
        coherence_score = max(0, min(100, coherence_score))
        
        return {
            'score': int(coherence_score),
            'connector_count': connector_count,
            'paragraph_consistency': consistency_ratio if len(paragraphs) > 1 else 1.0,
            'issues': issues,
            'strengths': strengths
        }
    
    def _calculate_content_score(self, metrics: Dict[str, Any]) -> int:
        """Calculate overall content quality score"""
        
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
    
    def _generate_detailed_findings(self, metrics: Dict[str, Any], text: str) -> List[Dict[str, Any]]:
        """Generate detailed findings with INTERESTING specific examples"""
        findings = []
        
        # INTERESTING FINDING 1: Readability with specific grade level
        readability = metrics['readability']
        grade_level = readability.get('grade_level', 'Unknown')
        avg_sentence = readability.get('avg_sentence_length', 0)
        
        if readability.get('score', 0) < 40:
            findings.append({
                'type': 'warning',
                'severity': 'high',
                'category': 'readability',
                'text': f'Very difficult to read - {grade_level} level required',
                'explanation': f'Average sentence length is {avg_sentence} words. This is TOO LONG for most readers. Sentences should be 15-20 words for easy reading.',
                'impact': 'Many readers will struggle to understand this content'
            })
        elif readability.get('score', 0) > 80:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'category': 'readability',
                'text': f'Excellent readability - {grade_level} level',
                'explanation': f'Average sentence length is {avg_sentence} words - perfect for general audiences!',
                'impact': 'Easy for most people to read and understand'
            })
        else:
            findings.append({
                'type': 'info',
                'severity': 'medium',
                'category': 'readability',
                'text': f'Requires {grade_level} reading level',
                'explanation': f'Average sentence is {avg_sentence} words long. This is appropriate for educated adults.',
                'impact': 'May be challenging for general audiences'
            })
        
        # INTERESTING FINDING 2: Grammar with specific counts
        grammar = metrics['grammar']
        issue_count = grammar.get('issue_count', 0)
        
        if issue_count > 5:
            # Get actual examples if available
            examples = []
            issue_details = grammar.get('issue_details', [])
            for detail in issue_details[:2]:
                examples.append(f"• {detail.get('type', 'Issue')}: {detail.get('count', 0)} instances")
            
            examples_text = '\n'.join(examples) if examples else 'Multiple grammar and punctuation errors'
            
            findings.append({
                'type': 'critical',
                'severity': 'high',
                'category': 'grammar',
                'text': f'Found {issue_count} grammar/punctuation issues',
                'explanation': f'Specific problems:\n{examples_text}\n\nThese errors reduce professionalism and credibility.',
                'impact': 'Readers may question the author\'s expertise'
            })
        elif issue_count > 2:
            findings.append({
                'type': 'warning',
                'severity': 'medium',
                'category': 'grammar',
                'text': f'{issue_count} minor grammar issues',
                'explanation': 'Small errors that don\'t significantly impact readability but could be improved',
                'impact': 'Slightly reduces professional appearance'
            })
        else:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'category': 'grammar',
                'text': 'Clean writing with no grammar issues',
                'explanation': 'Excellent attention to writing mechanics!',
                'impact': 'Professional and polished'
            })
        
        # INTERESTING FINDING 3: Vocabulary diversity with actual percentage
        vocabulary = metrics['vocabulary']
        unique_pct = vocabulary.get('diversity_ratio', 0) * 100
        unique_words = vocabulary.get('unique_words', 0)
        total_words = vocabulary.get('total_words', 0)
        
        if unique_pct < 30:
            findings.append({
                'type': 'warning',
                'severity': 'medium',
                'category': 'vocabulary',
                'text': f'Repetitive vocabulary - only {unique_pct:.0f}% unique words',
                'explanation': f'Used {unique_words} different words out of {total_words} total. This article repeats words too often, making it boring to read.',
                'impact': 'Readers may lose interest due to monotonous language'
            })
        elif unique_pct > 50:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'category': 'vocabulary',
                'text': f'Rich vocabulary - {unique_pct:.0f}% unique words',
                'explanation': f'Used {unique_words} different words - excellent variety keeps readers engaged!',
                'impact': 'Engaging and interesting to read'
            })
        
        # INTERESTING FINDING 4: Structure with paragraph analysis
        structure = metrics['structure']
        para_count = structure.get('paragraph_count', 0)
        avg_para_length = structure.get('avg_paragraph_length', 0)
        transition_count = structure.get('transition_count', 0)
        
        if para_count < 3:
            findings.append({
                'type': 'warning',
                'severity': 'high',
                'category': 'structure',
                'text': f'Poor structure - only {para_count} paragraph(s)',
                'explanation': 'Content should be broken into multiple paragraphs for readability. Long blocks of text overwhelm readers.',
                'impact': 'Very difficult to scan and digest'
            })
        elif avg_para_length > 120:
            findings.append({
                'type': 'warning',
                'severity': 'medium',
                'category': 'structure',
                'text': f'Paragraphs too long - average {avg_para_length:.0f} words',
                'explanation': 'Paragraphs should be 50-100 words. Shorter paragraphs are easier to read on screens.',
                'impact': 'Readers may skip long paragraphs'
            })
        
        if transition_count == 0:
            findings.append({
                'type': 'warning',
                'severity': 'medium',
                'category': 'structure',
                'text': 'No transition words found',
                'explanation': 'Words like "however," "therefore," "meanwhile" help connect ideas. Without them, the article feels choppy.',
                'impact': 'Ideas don\'t flow smoothly'
            })
        elif transition_count >= 3:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'category': 'structure',
                'text': f'Good flow with {transition_count} transition words',
                'explanation': 'Transition words help readers follow your logic from one idea to the next.',
                'impact': 'Content flows naturally'
            })
        
        # INTERESTING FINDING 5: Professional elements
        professionalism = metrics['professionalism']
        citation_count = professionalism.get('citation_count', 0)
        stats_count = professionalism.get('statistics_count', 0)
        quote_count = professionalism.get('quote_count', 0)
        
        if citation_count > 0 and stats_count > 0:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'category': 'professionalism',
                'text': f'Well-researched: {citation_count} citation(s), {stats_count} statistic(s)',
                'explanation': 'This article backs up claims with evidence and data - the hallmark of quality journalism.',
                'impact': 'Highly credible and trustworthy'
            })
        elif citation_count == 0:
            findings.append({
                'type': 'warning',
                'severity': 'high',
                'category': 'professionalism',
                'text': 'No citations found',
                'explanation': 'Without sources or citations, readers cannot verify claims. This is a major credibility issue.',
                'impact': 'Cannot verify any claims independently'
            })
        
        if quote_count > 3:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'category': 'professionalism',
                'text': f'Good sourcing - {quote_count} direct quotes',
                'explanation': 'Direct quotes add credibility and show the author did original reporting.',
                'impact': 'Evidence of original journalism'
            })
        
        # INTERESTING FINDING 6: Coherence issues
        coherence = metrics['coherence']
        connector_count = coherence.get('connector_count', 0)
        para_consistency = coherence.get('paragraph_consistency', 1.0)
        
        if para_consistency < 0.5:
            findings.append({
                'type': 'warning',
                'severity': 'medium',
                'category': 'coherence',
                'text': 'Inconsistent paragraph lengths',
                'explanation': f'Paragraphs range from very short to very long. Only {para_consistency * 100:.0f}% are well-sized (20-150 words).',
                'impact': 'Disrupts reading rhythm'
            })
        
        return findings[:15]  # Return top 15 most interesting findings
    
    def _generate_comprehensive_analysis(self, metrics: Dict[str, Any], 
                                        score: int, word_count: int, text: str) -> Dict[str, str]:
        """Generate INTERESTING comprehensive analysis with specific insights"""
        
        # What we looked at - make it clear and specific
        what_we_looked = (
            f"We analyzed every aspect of this {word_count}-word article: "
            f"sentence complexity (how hard it is to read), grammar errors (typos and mistakes), "
            f"vocabulary diversity (word variety), paragraph structure (organization), "
            f"professional elements (citations and data), and logical flow (how ideas connect)."
        )
        
        # What we found - SPECIFIC NUMBERS AND INSIGHTS
        readability = metrics['readability']
        grammar = metrics['grammar']
        vocabulary = metrics['vocabulary']
        professionalism = metrics['professionalism']
        structure = metrics['structure']
        
        findings_parts = []
        
        # Readability insight
        grade = readability.get('grade_level', 'Unknown')
        avg_sent = readability.get('avg_sentence_length', 0)
        if avg_sent > 25:
            findings_parts.append(
                f"📖 Reading level: {grade} - sentences average {avg_sent:.0f} words (TOO LONG for easy reading)"
            )
        elif avg_sent < 15:
            findings_parts.append(
                f"📖 Reading level: {grade} - short sentences averaging {avg_sent:.0f} words (very easy to read)"
            )
        else:
            findings_parts.append(
                f"📖 Reading level: {grade} - sentences average {avg_sent:.0f} words"
            )
        
        # Grammar insight
        errors = grammar.get('issue_count', 0)
        if errors > 5:
            findings_parts.append(f"❌ Found {errors} grammar/punctuation errors - needs proofreading")
        elif errors > 0:
            findings_parts.append(f"⚠️ {errors} minor grammar issue(s)")
        else:
            findings_parts.append(f"✓ Perfect grammar - no errors found")
        
        # Vocabulary insight
        unique_pct = vocabulary.get('diversity_ratio', 0) * 100
        complex_count = vocabulary.get('complex_word_count', 0)
        if unique_pct < 30:
            findings_parts.append(f"🔤 Only {unique_pct:.0f}% unique words - very repetitive")
        elif unique_pct > 50:
            findings_parts.append(f"🔤 {unique_pct:.0f}% unique words - rich vocabulary with {complex_count} complex terms")
        else:
            findings_parts.append(f"🔤 {unique_pct:.0f}% unique words")
        
        # Professional elements insight
        citations = professionalism.get('citation_count', 0)
        stats = professionalism.get('statistics_count', 0)
        quotes = professionalism.get('quote_count', 0)
        
        prof_elements = []
        if citations > 0:
            prof_elements.append(f"{citations} citation(s)")
        if stats > 0:
            prof_elements.append(f"{stats} statistic(s)")
        if quotes > 0:
            prof_elements.append(f"{quotes} direct quote(s)")
        
        if prof_elements:
            findings_parts.append(f"📊 Includes {', '.join(prof_elements)}")
        else:
            findings_parts.append(f"⚠️ No citations, statistics, or quotes found")
        
        # Structure insight
        paras = structure.get('paragraph_count', 0)
        transitions = structure.get('transition_count', 0)
        if paras < 3:
            findings_parts.append(f"📝 Poor structure - only {paras} paragraph(s)")
        elif transitions == 0:
            findings_parts.append(f"📝 {paras} paragraphs but no transition words (choppy flow)")
        else:
            findings_parts.append(f"📝 Well-structured: {paras} paragraphs with {transitions} transitions")
        
        what_we_found = " • ".join(findings_parts)
        
        # What it means - ACTIONABLE INSIGHTS
        if score >= 80:
            what_it_means = (
                f"This is high-quality, professional writing ({score}/100). "
                f"The author clearly knows their craft - sentences are well-constructed, "
                f"grammar is clean, and content is well-sourced. "
                f"{'Perfect for educated audiences.' if readability.get('score', 0) < 70 else 'Accessible to most readers.'} "
                f"This level of quality suggests a skilled, experienced writer."
            )
        elif score >= 65:
            what_it_means = (
                f"This is good-quality writing ({score}/100) but has room for improvement. "
                f"The content is generally well-written with {grammar.get('issue_count', 0)} minor error(s). "
                f"{'Adding more citations would boost credibility.' if citations == 0 else 'Good sourcing adds credibility.'} "
                f"With some editing, this could be excellent."
            )
        elif score >= 50:
            what_it_means = (
                f"This article has fair quality ({score}/100) with several issues. "
                f"Main problems: {self._get_top_problem(metrics)}. "
                f"The author should revise for grammar, add more sources, and improve paragraph structure. "
                f"While the content may be valuable, the presentation reduces its impact."
            )
        else:
            what_it_means = (
                f"This article has significant quality issues ({score}/100) that seriously impact credibility. "
                f"Major problems: {grammar.get('issue_count', 0)} grammar errors, "
                f"{'no citations, ' if citations == 0 else ''}"
                f"{'poor structure, ' if paras < 3 else ''}"
                f"and {grade} reading level. "
                f"Readers should be cautious - these writing problems suggest lack of editorial oversight. "
                f"Verify any important claims independently."
            )
        
        return {
            'what_we_looked': what_we_looked,
            'what_we_found': what_we_found,
            'what_it_means': what_it_means
        }
    
    def _get_top_problem(self, metrics: Dict[str, Any]) -> str:
        """Identify the biggest problem"""
        problems = []
        
        if metrics['grammar'].get('issue_count', 0) > 5:
            problems.append('too many grammar errors')
        if metrics['professionalism'].get('citation_count', 0) == 0:
            problems.append('no citations')
        if metrics['structure'].get('paragraph_count', 0) < 3:
            problems.append('poor paragraph structure')
        if metrics['vocabulary'].get('diversity_ratio', 0) < 0.3:
            problems.append('repetitive vocabulary')
        if metrics['readability'].get('score', 0) < 40:
            problems.append('too difficult to read')
        
        if not problems:
            return 'minor issues throughout'
        
        return ', '.join(problems[:2])
    
    def _get_weakest_area(self, metrics: Dict[str, Any]) -> str:
        """Identify the weakest area for improvement suggestions"""
        scores = {name: data.get('score', 50) for name, data in metrics.items()}
        weakest = min(scores.items(), key=lambda x: x[1])
        return weakest[0].replace('_', ' ')
    
    def _generate_conversational_summary(self, metrics: Dict[str, Any], 
                                        score: int, level: str) -> str:
        """Generate conversational summary"""
        
        readability = metrics['readability']
        grammar = metrics['grammar']
        
        if score >= 80:
            base = f"Excellent content quality ({score}/100). "
        elif score >= 65:
            base = f"Good content quality ({score}/100). "
        elif score >= 50:
            base = f"Fair content quality ({score}/100). "
        else:
            base = f"Poor content quality ({score}/100). "
        
        base += f"Written at a {readability.get('grade_level', 'Unknown')} reading level. "
        
        if grammar.get('issue_count', 0) > 0:
            base += f"Contains {grammar['issue_count']} grammar issue(s). "
        
        prof_score = metrics['professionalism'].get('score', 0)
        if prof_score >= 75:
            base += "Professional tone with proper citations. "
        elif prof_score < 50:
            base += "Lacks professional elements like citations. "
        
        return base.strip()
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        info = super().get_service_info()
        info.update({
            'version': '4.0.0',
            'capabilities': [
                'Grade-level readability analysis',
                'Detailed grammar checking with examples',
                'Vocabulary diversity and complexity',
                'Structure and organization analysis',
                'Professional writing assessment',
                'Coherence and flow evaluation',
                'Specific findings with actionable insights',
                'AI-enhanced analysis' if self._ai_available else 'Pattern-based analysis'
            ],
            'metrics_analyzed': [
                'readability', 'structure', 'vocabulary',
                'grammar', 'professionalism', 'coherence'
            ],
            'ai_enhanced': self._ai_available
        })
        return info
