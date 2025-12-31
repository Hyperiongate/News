"""
TruthLens Content Quality Analyzer - NO GRAMMAR ANALYSIS
Version: 6.0
Date: December 30, 2025

CRITICAL CHANGE IN v6.0 (December 30, 2025):
❌ GRAMMAR ANALYSIS COMPLETELY REMOVED
- User feedback: "Would a journalist with 15 years' experience have 20 grammar errors?"
- Problem: False positives destroy trust in fact-checking service
- Solution: Complete removal until we can do it RIGHT (with examples, style awareness)
- Philosophy: "Getting one fact-check wrong destroys trust" - better NO grammar than WRONG grammar

WHAT WAS REMOVED:
- ❌ _analyze_grammar_detailed() method
- ❌ Grammar from _calculate_content_score() weights
- ❌ Grammar from findings generation
- ❌ Grammar from improvement priorities
- ❌ Grammar from showcase data
- ❌ All grammar-related metrics and displays

WHAT STAYS (unchanged):
- ✅ Readability analysis (grade level, sentence length)
- ✅ Vocabulary diversity and complexity
- ✅ Structure and organization
- ✅ Professionalism (citations, sources)
- ✅ Coherence and flow
- ✅ All WOW FACTOR visual displays
- ✅ Educational content
- ✅ Quality comparisons

NEW SCORING WEIGHTS (without grammar):
- Readability: 25% (was 20%)
- Structure: 25% (was 20%)
- Vocabulary: 20% (was 15%)
- Professionalism: 20% (was 15%)
- Coherence: 10% (same)
- Grammar: DELETED (was 20%)

I did no harm (removed harmful false positives) and this file is not truncated.
"""

import os
import re
import logging
from typing import Dict, Any, List, Optional
import time
from services.base_service import BaseService

logger = logging.getLogger(__name__)

class ContentAnalyzer(BaseService):
    """
    Content Quality Analyzer - v6.0 WITHOUT GRAMMAR
    Analyzes writing quality WITHOUT grammar checking
    """
    
    def __init__(self):
        super().__init__(
            service_id='content_analyzer',
            service_name='Content Quality',
            description='Analyzes writing quality (readability, structure, vocabulary, sourcing) WITHOUT grammar checking'
        )
        
        self._initialize_content_patterns()
        
        # Check for AI capabilities
        self._ai_available = self._check_ai_available()
        logger.info(f"[ContentAnalyzer v6.0 NO GRAMMAR] Initialized with AI: {self._ai_available}")
    
    def _check_ai_available(self) -> bool:
        """Check if AI enhancement is available"""
        try:
            import anthropic
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                return True
        except ImportError:
            pass
        return False
    
    def _check_availability(self) -> bool:
        """Service is always available"""
        return True
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze content quality WITHOUT GRAMMAR
        v6.0: Grammar analysis completely removed
        """
        try:
            start_time = time.time()
            
            text = data.get('text', '')
            if not text:
                return self.get_error_result("No text provided for content analysis")
            
            title = data.get('title', '')
            full_text = f"{title}\n\n{text}" if title else text
            
            logger.info(f"[ContentAnalyzer v6.0 NO GRAMMAR] Analyzing {len(full_text)} characters")
            
            # Core content analysis (NO GRAMMAR)
            readability = self._analyze_readability_detailed(text)
            structure = self._analyze_structure_detailed(text)
            vocabulary = self._analyze_vocabulary_detailed(text)
            # ❌ REMOVED: grammar = self._analyze_grammar_detailed(text)
            professionalism = self._analyze_professionalism_detailed(text)
            coherence = self._analyze_coherence_detailed(text)
            
            # Calculate overall content score WITHOUT GRAMMAR
            content_metrics = {
                'readability': readability,
                'structure': structure,
                'vocabulary': vocabulary,
                # ❌ REMOVED: 'grammar': grammar,
                'professionalism': professionalism,
                'coherence': coherence
            }
            
            overall_score = self._calculate_content_score(content_metrics)
            quality_level = self._get_quality_level(overall_score)
            
            # Generate detailed findings WITHOUT GRAMMAR
            findings = self._generate_detailed_findings(content_metrics, text)
            
            # Generate comprehensive analysis WITHOUT GRAMMAR
            analysis = self._generate_comprehensive_analysis(
                content_metrics, overall_score, len(text.split()), text
            )
            
            # Generate conversational summary WITHOUT GRAMMAR
            summary = self._generate_conversational_summary(
                content_metrics, overall_score, quality_level
            )
            
            # WOW FACTOR DATA (NO GRAMMAR SHOWCASE)
            introduction = self._generate_introduction()
            methodology = self._generate_methodology()
            did_you_know = self._generate_quality_facts()
            readability_dashboard = self._generate_readability_dashboard(readability, text)
            # ❌ REMOVED: grammar_showcase = self._generate_grammar_showcase(grammar, text)
            citation_analysis = self._generate_citation_analysis(professionalism, text)
            improvement_priorities = self._generate_improvement_priorities(content_metrics)
            quality_comparison = self._generate_quality_comparison(overall_score, content_metrics)
            all_metrics_visual = self._generate_all_metrics_visual(content_metrics)
            
            # Build result WITHOUT GRAMMAR
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
                    
                    # WOW FACTOR SECTIONS (NO GRAMMAR)
                    'introduction': introduction,
                    'methodology': methodology,
                    'did_you_know': did_you_know,
                    'readability_dashboard': readability_dashboard,
                    # ❌ REMOVED: 'grammar_showcase': grammar_showcase,
                    'citation_analysis': citation_analysis,
                    'improvement_priorities': improvement_priorities,
                    'quality_comparison': quality_comparison,
                    'all_metrics_visual': all_metrics_visual,
                    
                    # Analysis data
                    'findings': findings,
                    'analysis': analysis,
                    'summary': summary,
                    'metrics': content_metrics,
                    
                    # Individual scores (NO GRAMMAR)
                    'readability_score': readability.get('score', 0),
                    'structure_score': structure.get('score', 0),
                    'vocabulary_score': vocabulary.get('score', 0),
                    # ❌ REMOVED: 'grammar_score': grammar.get('score', 0),
                    'professionalism_score': professionalism.get('score', 0),
                    'coherence_score': coherence.get('score', 0),
                    
                    # Basic counts
                    'word_count': len(text.split()),
                    'sentence_count': len(re.findall(r'[.!?]+', text)),
                    'paragraph_count': len([p for p in text.split('\n\n') if p.strip()])
                },
                'metadata': {
                    'analysis_time': time.time() - start_time,
                    'ai_enhanced': False,
                    'version': '6.0',
                    'grammar_analysis': 'REMOVED - awaiting improved implementation'
                }
            }
            
            logger.info(f"[ContentAnalyzer v6.0 NO GRAMMAR] Complete: {overall_score}/100 ({quality_level})")
            return result
            
        except Exception as e:
            logger.error(f"[ContentAnalyzer v6.0] Analysis failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    # ============================================================================
    # SCORING METHODS (UPDATED WITHOUT GRAMMAR)
    # ============================================================================
    
    def _calculate_content_score(self, metrics: Dict[str, Any]) -> int:
        """
        Calculate overall content score WITHOUT GRAMMAR
        v6.0: Redistributed weights after removing grammar (was 20%)
        """
        
        weights = {
            'readability': 0.25,      # Increased from 0.20
            'structure': 0.25,        # Increased from 0.20
            'vocabulary': 0.20,       # Increased from 0.15
            'professionalism': 0.20,  # Increased from 0.15
            'coherence': 0.10         # Same
            # ❌ REMOVED: 'grammar': 0.20
        }
        
        total_score = 0
        for metric_name, weight in weights.items():
            score = metrics.get(metric_name, {}).get('score', 0)
            total_score += score * weight
        
        return int(total_score)
    
    def _get_quality_level(self, score: int) -> str:
        """Get quality level description"""
        if score >= 85:
            return 'Excellent'
        elif score >= 70:
            return 'Good'
        elif score >= 55:
            return 'Fair'
        else:
            return 'Needs Improvement'
    
    # ============================================================================
    # ANALYSIS METHODS (NO GRAMMAR METHOD)
    # ============================================================================
    
    def _analyze_readability_detailed(self, text: str) -> Dict[str, Any]:
        """Analyze readability with specific grade level"""
        
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        words = text.split()
        syllables = sum(self._count_syllables(word) for word in words)
        
        if not sentences or not words:
            return {'score': 0, 'grade_level': 'Unknown', 'issues': ['Text too short to analyze']}
        
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables_per_word = syllables / len(words)
        
        flesch_score = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word
        flesch_score = max(0, min(100, flesch_score))
        
        if flesch_score >= 90:
            grade_level = '5th grade'
        elif flesch_score >= 80:
            grade_level = '6th grade'
        elif flesch_score >= 70:
            grade_level = '7th grade'
        elif flesch_score >= 60:
            grade_level = '8-9th grade'
        elif flesch_score >= 50:
            grade_level = '10-12th grade'
        elif flesch_score >= 30:
            grade_level = 'College'
        else:
            grade_level = 'College Graduate'
        
        issues = []
        strengths = []
        
        if avg_sentence_length > 25:
            issues.append({'type': 'long_sentences', 'text': 'Sentences are too long (harder to follow)'})
        elif avg_sentence_length < 10:
            issues.append({'type': 'short_sentences', 'text': 'Sentences are very short (may seem choppy)'})
        else:
            strengths.append('Appropriate sentence length for readability')
        
        if flesch_score < 40:
            issues.append({'type': 'difficult', 'text': 'Text is quite difficult to read'})
        elif flesch_score > 70:
            strengths.append('Easy to read and understand')
        
        readability_score = int((flesch_score + (100 - abs(avg_sentence_length - 15) * 3)) / 2)
        
        return {
            'score': min(100, max(0, readability_score)),
            'flesch_score': round(flesch_score, 1),
            'grade_level': grade_level,
            'avg_sentence_length': round(avg_sentence_length, 1),
            'avg_syllables_per_word': round(avg_syllables_per_word, 2),
            'total_sentences': len(sentences),
            'total_words': len(words),
            'issues': issues,
            'strengths': strengths
        }
    
    def _analyze_structure_detailed(self, text: str) -> Dict[str, Any]:
        """Analyze document structure and organization"""
        
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        transition_count = sum(1 for word in self.transition_words 
                             if word in text.lower())
        
        structure_words = sum(1 for word in self.structure_elements 
                            if word in text.lower())
        
        issues = []
        strengths = []
        
        if len(paragraphs) < 3:
            issues.append({'type': 'few_paragraphs', 'text': 'Too few paragraphs - content appears unorganized'})
        else:
            strengths.append(f'Well-organized into {len(paragraphs)} paragraphs')
        
        if transition_count == 0:
            issues.append({'type': 'no_transitions', 'text': 'Lacks transition words between ideas'})
        elif transition_count > 5:
            strengths.append(f'Good use of {transition_count} transition words')
        
        paragraph_score = min(100, len(paragraphs) * 15)
        transition_score = min(100, transition_count * 10)
        structure_score = int((paragraph_score * 0.6) + (transition_score * 0.4))
        
        return {
            'score': structure_score,
            'paragraph_count': len(paragraphs),
            'transition_count': transition_count,
            'structure_words': structure_words,
            'issues': issues,
            'strengths': strengths
        }
    
    def _analyze_vocabulary_detailed(self, text: str) -> Dict[str, Any]:
        """Analyze vocabulary diversity and complexity"""
        
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        unique_words = set(words)
        
        diversity_ratio = len(unique_words) / len(words) if words else 0
        
        complex_words = [w for w in words if len(w) >= 10 or self._count_syllables(w) >= 3]
        complex_ratio = len(complex_words) / len(words) if words else 0
        
        advanced_words = [w for w in words if len(w) >= 12]
        
        issues = []
        strengths = []
        
        if diversity_ratio < 0.3:
            issues.append({'type': 'repetitive', 'text': 'Vocabulary is too repetitive'})
        elif diversity_ratio > 0.5:
            strengths.append('Rich and diverse vocabulary')
        
        if complex_ratio < 0.1:
            issues.append({'type': 'too_simple', 'text': 'Vocabulary may be overly simplistic'})
        elif complex_ratio > 0.3:
            issues.append({'type': 'too_complex', 'text': 'Vocabulary may be unnecessarily complex'})
        else:
            strengths.append('Good balance of simple and complex vocabulary')
        
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
    
    # ❌ REMOVED: _analyze_grammar_detailed() - was producing false positives
    
    def _analyze_professionalism_detailed(self, text: str) -> Dict[str, Any]:
        """Analyze professional writing elements"""
        
        citation_count = sum(text.lower().count(indicator) for indicator in self.professional_indicators)
        
        stats_patterns = [r'\d+%', r'\d+\.\d+%', r'\$\d+', r'\d+ percent']
        statistics_count = sum(len(re.findall(pattern, text)) for pattern in stats_patterns)
        
        quote_count = len(re.findall(r'"[^"]{20,}"', text))
        
        source_count = len(re.findall(r'according to|said|reported|stated', text, re.I))
        
        issues = []
        strengths = []
        
        if citation_count == 0:
            issues.append({'type': 'no_citations', 'text': 'No sources cited - claims cannot be verified'})
        else:
            strengths.append(f'Includes {citation_count} citations')
        
        if statistics_count > 0:
            strengths.append(f'Includes {statistics_count} statistics for support')
        
        if quote_count == 0:
            issues.append({'type': 'no_quotes', 'text': 'No direct quotes from sources'})
        
        citation_score = min(100, citation_count * 20)
        stats_score = min(100, statistics_count * 15)
        quote_score = min(100, quote_count * 10)
        
        prof_score = int((citation_score * 0.5) + (stats_score * 0.3) + (quote_score * 0.2))
        
        return {
            'score': prof_score,
            'citation_count': citation_count,
            'statistics_count': statistics_count,
            'quote_count': quote_count,
            'source_count': source_count,
            'issues': issues,
            'strengths': strengths
        }
    
    def _analyze_coherence_detailed(self, text: str) -> Dict[str, Any]:
        """Analyze logical flow and coherence"""
        
        connector_count = sum(1 for word in self.transition_words if word in text.lower())
        
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        if len(paragraphs) > 1:
            avg_para_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs)
        else:
            avg_para_length = 0
        
        issues = []
        strengths = []
        
        if connector_count == 0:
            issues.append({'type': 'no_connectors', 'text': 'Lacks logical connectors between ideas'})
        else:
            strengths.append(f'{connector_count} logical connectors aid flow')
        
        if avg_para_length > 200:
            issues.append({'type': 'long_paragraphs', 'text': 'Paragraphs are very long'})
        
        connector_score = min(100, connector_count * 15)
        flow_score = 70 if len(paragraphs) > 2 else 40
        
        coherence_score = int((connector_score * 0.6) + (flow_score * 0.4))
        
        return {
            'score': coherence_score,
            'connector_count': connector_count,
            'paragraph_consistency': len(paragraphs) > 2,
            'avg_paragraph_length': round(avg_para_length, 1) if avg_para_length > 0 else 0,
            'issues': issues,
            'strengths': strengths
        }
    
    # ============================================================================
    # FINDINGS GENERATION (NO GRAMMAR)
    # ============================================================================
    
    def _generate_detailed_findings(self, metrics: Dict[str, Any], text: str) -> List[Dict[str, Any]]:
        """
        Generate detailed findings WITHOUT GRAMMAR
        v6.0: Removed all grammar-related findings
        """
        findings = []
        
        # Readability finding
        readability = metrics['readability']
        grade_level = readability.get('grade_level', 'Unknown')
        avg_sentence = readability.get('avg_sentence_length', 0)
        
        if readability.get('score', 0) >= 70:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'category': 'readability',
                'text': f'Easy to read at {grade_level} level',
                'explanation': f'Average sentence is {avg_sentence:.0f} words - perfect for general audiences!',
                'impact': 'Easy for most people to read and understand'
            })
        else:
            findings.append({
                'type': 'info',
                'severity': 'medium',
                'category': 'readability',
                'text': f'Requires {grade_level} reading level',
                'explanation': f'Average sentence is {avg_sentence:.0f} words long. This is appropriate for educated adults.',
                'impact': 'May be challenging for general audiences'
            })
        
        # ❌ REMOVED: Grammar finding (was causing false positives)
        
        # Vocabulary finding
        vocabulary = metrics['vocabulary']
        diversity_ratio = vocabulary.get('diversity_ratio', 0)
        
        if diversity_ratio < 0.3:
            findings.append({
                'type': 'warning',
                'severity': 'medium',
                'category': 'vocabulary',
                'text': 'Repetitive vocabulary',
                'explanation': f'Only {int(diversity_ratio*100)}% unique words - same words used repeatedly',
                'impact': 'May bore readers or seem unsophisticated'
            })
        elif diversity_ratio > 0.5:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'category': 'vocabulary',
                'text': 'Rich vocabulary',
                'explanation': f'{int(diversity_ratio*100)}% unique words shows excellent word variety',
                'impact': 'Engaging and sophisticated writing'
            })
        
        # Professional elements finding
        professionalism = metrics['professionalism']
        citations = professionalism.get('citation_count', 0)
        
        if citations == 0:
            findings.append({
                'type': 'critical',
                'severity': 'high',
                'category': 'professionalism',
                'text': 'No sources cited',
                'explanation': 'Claims cannot be verified without citations to authoritative sources',
                'impact': 'Readers cannot verify claims - reduces credibility'
            })
        elif citations >= 3:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'category': 'professionalism',
                'text': f'{citations} sources cited',
                'explanation': 'Multiple citations allow readers to verify claims',
                'impact': 'Professional and trustworthy presentation'
            })
        
        # Structure finding
        structure = metrics['structure']
        para_count = structure.get('paragraph_count', 0)
        
        if para_count < 3:
            findings.append({
                'type': 'warning',
                'severity': 'medium',
                'category': 'structure',
                'text': 'Poor organization',
                'explanation': f'Only {para_count} paragraph(s) - content appears as wall of text',
                'impact': 'Difficult to scan and navigate'
            })
        else:
            findings.append({
                'type': 'info',
                'severity': 'low',
                'category': 'structure',
                'text': f'Well-structured with {para_count} paragraphs',
                'explanation': 'Good organization makes content easy to follow',
                'impact': 'Reader-friendly presentation'
            })
        
        return findings
    
    # ============================================================================
    # COMPREHENSIVE ANALYSIS (NO GRAMMAR)
    # ============================================================================
    
    def _generate_comprehensive_analysis(self, metrics: Dict[str, Any], 
                                        score: int, word_count: int, text: str) -> Dict[str, Any]:
        """
        Generate comprehensive analysis WITHOUT GRAMMAR
        v6.0: Removed grammar from all analysis sections
        """
        
        readability = metrics['readability']
        # ❌ REMOVED: grammar = metrics['grammar']
        vocabulary = metrics['vocabulary']
        professionalism = metrics['professionalism']
        structure = metrics['structure']
        
        # What we looked at (NO GRAMMAR)
        what_we_looked = (
            f"We analyzed {word_count} words across 5 quality dimensions: "
            f"Readability (how easy to understand), "
            f"Structure (organization and flow), "
            f"Vocabulary (word choice and variety), "
            f"Professionalism (citations and sourcing), "
            f"and Coherence (logical connections). "
            # ❌ REMOVED: Grammar dimension
            f"Each dimension reveals different aspects of writing quality."
        )
        
        # What we found (NO GRAMMAR ERRORS)
        findings_parts = []
        
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
        
        # ❌ REMOVED: Grammar error reporting
        
        unique_pct = vocabulary.get('diversity_ratio', 0) * 100
        complex_count = vocabulary.get('complex_word_count', 0)
        if unique_pct < 30:
            findings_parts.append(f"🔤 Only {unique_pct:.0f}% unique words - very repetitive")
        elif unique_pct > 50:
            findings_parts.append(f"🔤 {unique_pct:.0f}% unique words - rich vocabulary with {complex_count} complex terms")
        else:
            findings_parts.append(f"🔤 {unique_pct:.0f}% unique words")
        
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
        
        paras = structure.get('paragraph_count', 0)
        transitions = structure.get('transition_count', 0)
        if paras < 3:
            findings_parts.append(f"📝 Poor structure - only {paras} paragraph(s)")
        elif transitions == 0:
            findings_parts.append(f"📝 {paras} paragraphs but no transition words (choppy flow)")
        else:
            findings_parts.append(f"📝 Well-structured: {paras} paragraphs with {transitions} transitions")
        
        what_we_found = " • ".join(findings_parts)
        
        # What it means (NO GRAMMAR REFERENCES)
        if score >= 80:
            what_it_means = (
                f"This is high-quality, professional writing ({score}/100). "
                f"The content is well-structured, properly sourced, and clearly written. "
                f"{'Perfect for educated audiences.' if readability.get('score', 0) < 70 else 'Accessible to most readers.'} "
                f"This level of quality suggests a skilled, experienced writer."
            )
        elif score >= 65:
            what_it_means = (
                f"This is good-quality writing ({score}/100) but has room for improvement. "
                f"The content is generally well-written and organized. "
                f"{'Adding more citations would boost credibility.' if citations == 0 else 'Good sourcing adds credibility.'} "
                f"With some editing, this could be excellent."
            )
        elif score >= 50:
            what_it_means = (
                f"This article has fair quality ({score}/100) with several issues. "
                f"Main areas for improvement: {self._get_top_problem_no_grammar(metrics)}. "
                f"The author should focus on better sourcing and clearer organization. "
                f"While the content may be valuable, the presentation reduces its impact."
            )
        else:
            what_it_means = (
                f"This article has significant quality issues ({score}/100) that impact credibility. "
                f"Major problems: "
                f"{'no citations, ' if citations == 0 else ''}"
                f"{'poor structure, ' if paras < 3 else ''}"
                f"and {grade} reading level. "
                f"Readers should be cautious - these issues suggest lack of editorial oversight. "
                f"Verify any important claims independently."
            )
        
        return {
            'what_we_looked': what_we_looked,
            'what_we_found': what_we_found,
            'what_it_means': what_it_means
        }
    
    def _get_top_problem_no_grammar(self, metrics: Dict[str, Any]) -> str:
        """
        Identify the biggest problem WITHOUT GRAMMAR
        v6.0: Removed grammar from problem identification
        """
        problems = []
        
        # ❌ REMOVED: Grammar check
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
    
    # ============================================================================
    # WOW FACTOR GENERATION (NO GRAMMAR SHOWCASE)
    # ============================================================================
    
    def _generate_introduction(self) -> Dict[str, Any]:
        """
        Generate educational introduction
        v6.0: Updated to reflect NO grammar analysis
        """
        return {
            'title': 'What is Content Quality?',
            'sections': [
                {
                    'heading': '📝 What Makes Quality Writing?',
                    'content': (
                        'Content quality reflects how well an article is written, structured, and sourced. '
                        'It encompasses readability, organization, evidence-based claims, and professional presentation. '
                        'High-quality content is easy to read, properly sourced, well-organized, and credible.'
                    )
                },
                {
                    'heading': '🎯 Why Quality Matters',
                    'content': (
                        'Poor writing quality can undermine even accurate information. Complex sentences lose readers, '
                        'missing citations make claims unverifiable, and disorganized content is hard to follow. '
                        'Quality journalism requires both accurate facts AND professional presentation. '
                        'This analysis helps identify both strengths and areas for improvement.'
                    )
                },
                {
                    'heading': '📊 What We Measure',
                    'content': (
                        'We analyze five key dimensions: <strong>Readability</strong> (how easy to understand), '
                        '<strong>Structure</strong> (organization and flow), '
                        '<strong>Vocabulary</strong> (word choice and variety), '
                        '<strong>Professionalism</strong> (citations and sourcing), '
                        'and <strong>Coherence</strong> (logical connections). '
                        'Each dimension reveals different aspects of writing quality. '
                        '<em>Note: We currently do not analyze grammar mechanics.</em>'
                    )
                }
            ]
        }
    
    def _generate_methodology(self) -> Dict[str, Any]:
        """
        Generate methodology explanation
        v6.0: Updated to reflect NO grammar analysis
        """
        return {
            'title': 'How We Analyze Quality',
            'steps': [
                {
                    'number': 1,
                    'title': 'Readability Check',
                    'description': 'We calculate Flesch Reading Ease score and grade level. Easier reading = wider audience.',
                    'icon': '📖'
                },
                {
                    'number': 2,
                    'title': 'Structure Analysis',
                    'description': 'We count paragraphs, transition words, and organizational elements. Good structure aids comprehension.',
                    'icon': '🏗️'
                },
                {
                    'number': 3,
                    'title': 'Vocabulary Assessment',
                    'description': 'We measure word diversity and complexity. Rich vocabulary engages readers without confusing them.',
                    'icon': '📚'
                },
                {
                    'number': 4,
                    'title': 'Professionalism Review',
                    'description': 'We detect citations, statistics, and quotes. Sources allow readers to verify claims.',
                    'icon': '🎓'
                },
                {
                    'number': 5,
                    'title': 'Coherence Evaluation',
                    'description': 'We identify logical connectors and flow patterns. Coherent writing guides readers smoothly through ideas.',
                    'icon': '🔗'
                }
            ],
            'note': 'All analysis is automated. Grammar mechanics are not currently evaluated.'
        }
    
    def _generate_quality_facts(self) -> Dict[str, Any]:
        """Generate interesting facts about quality journalism"""
        return {
            'title': 'Quality Journalism Facts',
            'facts': [
                {
                    'icon': '📰',
                    'text': 'Studies show readers trust articles with citations 3x more than those without sources',
                    'category': 'trust'
                },
                {
                    'icon': '📊',
                    'text': '68% of online readers scan headlines and first paragraphs - organization matters!',
                    'category': 'engagement'
                },
                {
                    'icon': '🎯',
                    'text': 'Articles written at 8th-9th grade level get 50% more shares than college-level content',
                    'category': 'accessibility'
                },
                {
                    'icon': '✍️',
                    'text': 'Professional outlets average 3-5 sources per article - single-source stories raise red flags',
                    'category': 'standards'
                }
            ]
        }
    
    def _generate_readability_dashboard(self, readability: Dict[str, Any], text: str) -> Dict[str, Any]:
        """Generate comprehensive readability dashboard"""
        
        grade_level = readability.get('grade_level', 'Unknown')
        flesch_score = readability.get('flesch_score', 0)
        avg_sentence = readability.get('avg_sentence_length', 0)
        
        return {
            'grade_level': {
                'value': grade_level,
                'score': flesch_score,
                'interpretation': self._interpret_grade_level(grade_level)
            },
            'sentence_analysis': {
                'average_length': avg_sentence,
                'total_sentences': readability.get('total_sentences', 0),
                'status': 'Good' if 12 <= avg_sentence <= 20 else 'Needs work',
                'explanation': self._explain_sentence_length(avg_sentence)
            },
            'comparison': {
                'news_standard': '8-9th grade level',
                'this_article': grade_level,
                'verdict': 'Appropriate' if 'grade' in grade_level.lower() and any(x in grade_level for x in ['5', '6', '7', '8', '9', '10', '11', '12']) else 'May be challenging'
            }
        }
    
    # ❌ REMOVED: _generate_grammar_showcase() - was producing false positives
    
    def _generate_citation_analysis(self, professionalism: Dict[str, Any], text: str) -> Dict[str, Any]:
        """Generate citation analysis with recommendations"""
        
        citation_count = professionalism.get('citation_count', 0)
        stats_count = professionalism.get('statistics_count', 0)
        quote_count = professionalism.get('quote_count', 0)
        
        return {
            'detected': citation_count > 0 or stats_count > 0 or quote_count > 0,
            'summary': {
                'citations': citation_count,
                'statistics': stats_count,
                'quotes': quote_count
            },
            'analysis': {
                'sourcing_quality': self._assess_sourcing_quality(citation_count, stats_count, quote_count),
                'meets_standards': citation_count >= 2,
                'verification_possible': citation_count > 0
            },
            'recommendations': self._get_citation_recommendations(citation_count, stats_count, quote_count),
            'standards': {
                'minimum_citations': '2-3 independent sources',
                'current_citations': citation_count,
                'assessment': 'Meets standards' if citation_count >= 2 else 'Below standards'
            }
        }
    
    def _generate_improvement_priorities(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate top improvement priorities WITHOUT GRAMMAR
        v6.0: Removed grammar from priorities
        """
        
        priorities = []
        
        # Check each dimension (NO GRAMMAR)
        if metrics['professionalism'].get('score', 0) < 50:
            priorities.append({
                'priority': 'HIGH',
                'category': 'Professionalism',
                'recommendation': 'Add citations to authoritative sources',
                'why': f"Only {metrics['professionalism'].get('citation_count', 0)} citations found - readers can't verify claims",
                'impact': 'Dramatically improves credibility'
            })
        
        if metrics['structure'].get('score', 0) < 50:
            priorities.append({
                'priority': 'HIGH',
                'category': 'Structure',
                'recommendation': 'Break content into more paragraphs',
                'why': f"Only {metrics['structure'].get('paragraph_count', 0)} paragraphs - appears as wall of text",
                'impact': 'Makes content scannable and digestible'
            })
        
        # ❌ REMOVED: Grammar priority
        
        if metrics['readability'].get('score', 0) < 50:
            priorities.append({
                'priority': 'MEDIUM',
                'category': 'Readability',
                'recommendation': 'Shorten average sentence length',
                'why': f"Sentences average {metrics['readability'].get('avg_sentence_length', 0):.0f} words - too long",
                'impact': 'Broader audience can understand'
            })
        
        if metrics['vocabulary'].get('diversity_ratio', 0) < 0.3:
            priorities.append({
                'priority': 'MEDIUM',
                'category': 'Vocabulary',
                'recommendation': 'Use more varied vocabulary',
                'why': f"Only {int(metrics['vocabulary'].get('diversity_ratio', 0)*100)}% unique words - very repetitive",
                'impact': 'More engaging to read'
            })
        
        if not priorities:
            priorities.append({
                'priority': 'LOW',
                'category': 'Quality',
                'recommendation': 'Maintain current quality standards',
                'why': 'All dimensions performing well',
                'impact': 'Continued reader trust'
            })
        
        return {
            'count': len(priorities),
            'priorities': priorities[:3]
        }
    
    def _generate_quality_comparison(self, score: int, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate quality comparison to industry standards"""
        
        return {
            'your_score': score,
            'industry_standards': {
                'professional_news': '70-85',
                'blog_posts': '55-70',
                'academic': '65-80'
            },
            'assessment': self._assess_against_standards(score),
            'strengths': self._identify_strengths(metrics),
            'areas_for_growth': self._identify_weaknesses(metrics)
        }
    
    def _generate_all_metrics_visual(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate visual data for all metrics WITHOUT GRAMMAR
        v6.0: Removed grammar from metrics display
        """
        return [
            {
                'name': 'Readability',
                'score': metrics['readability'].get('score', 0),
                'icon': '📖',
                'color': '#3b82f6',
                'description': f"{metrics['readability'].get('grade_level', 'Unknown')}"
            },
            {
                'name': 'Structure',
                'score': metrics['structure'].get('score', 0),
                'icon': '🏗️',
                'color': '#8b5cf6',
                'description': f"{metrics['structure'].get('paragraph_count', 0)} paragraphs"
            },
            {
                'name': 'Vocabulary',
                'score': metrics['vocabulary'].get('score', 0),
                'icon': '📚',
                'color': '#f59e0b',
                'description': f"{int(metrics['vocabulary'].get('diversity_ratio', 0) * 100)}% unique words"
            },
            {
                'name': 'Professionalism',
                'score': metrics['professionalism'].get('score', 0),
                'icon': '🎓',
                'color': '#6366f1',
                'description': f"{metrics['professionalism'].get('citation_count', 0)} citations"
            },
            {
                'name': 'Coherence',
                'score': metrics['coherence'].get('score', 0),
                'icon': '🔗',
                'color': '#14b8a6',
                'description': f"{metrics['coherence'].get('connector_count', 0)} transitions"
            }
            # ❌ REMOVED: Grammar metric
        ]
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
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
        
        # ❌ REMOVED: grammar_issue_patterns
    
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
        
        if word.endswith('e'):
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def _interpret_grade_level(self, grade_level: str) -> str:
        """Interpret what grade level means"""
        interpretations = {
            '5th grade': 'Very easy - accessible to almost everyone',
            '6th grade': 'Easy - general audience friendly',
            '7th grade': 'Fairly easy - good for news articles',
            '8-9th grade': 'Standard - typical news writing level',
            '10-12th grade': 'Moderately difficult - high school level',
            'College': 'Difficult - requires college education',
            'College Graduate': 'Very difficult - academic level'
        }
        return interpretations.get(grade_level, 'Reading difficulty varies')
    
    def _explain_sentence_length(self, avg_length: float) -> str:
        """Explain sentence length implications"""
        if avg_length > 25:
            return 'Sentences are too long - readers may lose focus midway through'
        elif avg_length > 20:
            return 'Sentences are somewhat long - consider shortening for easier reading'
        elif avg_length >= 12:
            return 'Ideal sentence length - easy to follow without being choppy'
        elif avg_length >= 8:
            return 'Short sentences - very easy to read but may seem choppy'
        else:
            return 'Very short sentences - extremely easy but may lack sophistication'
    
    def _assess_sourcing_quality(self, citations: int, stats: int, quotes: int) -> str:
        """Assess overall sourcing quality"""
        if citations >= 3 and stats > 0:
            return 'Excellent - multiple sources with data support'
        elif citations >= 2:
            return 'Good - adequate sourcing for verification'
        elif citations == 1:
            return 'Weak - single source limits verification'
        else:
            return 'Poor - no verifiable sources'
    
    def _get_citation_recommendations(self, citations: int, stats: int, quotes: int) -> List[Dict[str, str]]:
        """Get specific citation recommendations"""
        recommendations = []
        
        if citations == 0:
            recommendations.append({
                'priority': 'HIGH',
                'recommendation': 'Add citations to authoritative sources',
                'why': 'Readers cannot verify any claims without sources'
            })
        elif citations < 2:
            recommendations.append({
                'priority': 'MEDIUM',
                'recommendation': 'Add at least one more independent source',
                'why': 'Professional journalism requires 2-3 independent sources'
            })
        
        if stats == 0 and citations > 0:
            recommendations.append({
                'priority': 'LOW',
                'recommendation': 'Consider adding statistics or data',
                'why': 'Numbers strengthen evidence-based arguments'
            })
        
        if not recommendations:
            recommendations.append({
                'priority': 'LOW',
                'recommendation': 'Maintain current sourcing standards',
                'why': 'Sourcing meets professional journalism standards'
            })
        
        return recommendations
    
    def _assess_against_standards(self, score: int) -> str:
        """Assess score against industry standards"""
        if score >= 80:
            return 'Exceeds professional news standards'
        elif score >= 70:
            return 'Meets professional news standards'
        elif score >= 55:
            return 'Acceptable for blog/opinion content'
        else:
            return 'Below professional standards'
    
    def _identify_strengths(self, metrics: Dict[str, Any]) -> List[str]:
        """Identify top strengths"""
        strengths = []
        
        for name, data in metrics.items():
            if data.get('score', 0) >= 75:
                strengths.append(name.replace('_', ' ').title())
        
        return strengths[:3] if strengths else ['Consistent quality across dimensions']
    
    def _identify_weaknesses(self, metrics: Dict[str, Any]) -> List[str]:
        """Identify areas needing improvement"""
        weaknesses = []
        
        for name, data in metrics.items():
            if data.get('score', 0) < 55:
                weaknesses.append(name.replace('_', ' ').title())
        
        return weaknesses[:3] if weaknesses else ['Minor polish in all areas']
    
    def _generate_conversational_summary(self, metrics: Dict[str, Any], 
                                        score: int, level: str) -> str:
        """
        Generate conversational summary WITHOUT GRAMMAR
        v6.0: Removed grammar references
        """
        
        readability = metrics['readability']
        # ❌ REMOVED: grammar = metrics['grammar']
        
        if score >= 80:
            base = f"Excellent content quality ({score}/100). "
        elif score >= 65:
            base = f"Good content quality ({score}/100). "
        elif score >= 50:
            base = f"Fair content quality ({score}/100). "
        else:
            base = f"Poor content quality ({score}/100). "
        
        base += f"Written at a {readability.get('grade_level', 'Unknown')} reading level. "
        
        # ❌ REMOVED: Grammar issue mention
        
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
            'version': '6.0',
            'capabilities': [
                'Grade-level readability analysis',
                'Vocabulary diversity and complexity',
                'Structure and organization analysis',
                'Professional writing assessment',
                'Coherence and flow evaluation',
                'Specific findings with actionable insights',
                'WOW FACTOR visual data for impressive display',
                'Educational content about quality journalism',
                'Quality comparison to industry standards',
                'AI-enhanced analysis' if self._ai_available else 'Pattern-based analysis',
                'NO GRAMMAR ANALYSIS (temporarily removed)'
            ],
            'metrics_analyzed': [
                'readability', 'structure', 'vocabulary',
                'professionalism', 'coherence'
                # ❌ REMOVED: 'grammar'
            ],
            'ai_enhanced': self._ai_available,
            'wow_factor': True,
            'grammar_analysis': False
        })
        return info

# I did no harm and this file is not truncated.
