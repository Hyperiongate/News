"""
FILE: services/content_analyzer.py
PURPOSE: Content quality analysis service
REFACTORED: Creates a content quality analyzer that inherits from BaseAnalyzer
Note: This is a new service as content_analyzer.py was not provided
"""

import logging
import re
from typing import Dict, Any, List
from services.base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)


class ContentAnalyzer(BaseAnalyzer):
    """Content quality analysis service that inherits from BaseAnalyzer"""
    
    def __init__(self):
        super().__init__('content_analyzer')
        logger.info("ContentAnalyzer initialized")
    
    def _check_availability(self) -> bool:
        """Check if the service is available"""
        # This service is always available as it's self-contained
        return True
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze content quality using the standardized interface
        
        Expected input:
            - text: Article text to analyze
            - title: (optional) Article title
            
        Returns:
            Standardized response with content quality analysis
        """
        # Validate input
        if not self.is_available:
            return self.get_default_result()
        
        text = data.get('text')
        if not text:
            return self.get_error_result("Missing required field: 'text'")
        
        title = data.get('title', '')
        
        return self._analyze_content(text, title)
    
    def _analyze_content(self, text: str, title: str = '') -> Dict[str, Any]:
        """Analyze content quality"""
        try:
            # Perform various content analyses
            readability = self._analyze_readability(text)
            structure = self._analyze_structure(text)
            language_quality = self._analyze_language_quality(text)
            evidence_quality = self._analyze_evidence_quality(text)
            
            # Calculate overall quality score
            quality_score = self._calculate_quality_score(
                readability, structure, language_quality, evidence_quality
            )
            
            # Generate quality level
            quality_level = self._get_quality_level(quality_score)
            
            return {
                'service': self.service_name,
                'success': True,
                'data': {
                    'quality_score': quality_score,
                    'quality_level': quality_level,
                    'readability': readability,
                    'structure': structure,
                    'language_quality': language_quality,
                    'evidence_quality': evidence_quality,
                    'summary': self._generate_quality_summary(
                        quality_score, quality_level, readability, structure, 
                        language_quality, evidence_quality
                    )
                },
                'metadata': {
                    'text_length': len(text),
                    'word_count': len(text.split()),
                    'has_title': bool(title)
                }
            }
            
        except Exception as e:
            logger.error(f"Content analysis failed: {e}")
            return self.get_error_result(str(e))
    
    def _analyze_readability(self, text: str) -> Dict[str, Any]:
        """Analyze text readability"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        words = text.split()
        
        if not sentences or not words:
            return {
                'score': 0,
                'level': 'Unknown',
                'avg_sentence_length': 0,
                'avg_word_length': 0
            }
        
        # Calculate metrics
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Simple readability score (inverse of complexity)
        readability_score = 100
        
        # Penalize very long sentences
        if avg_sentence_length > 25:
            readability_score -= 20
        elif avg_sentence_length > 20:
            readability_score -= 10
        
        # Penalize long words
        if avg_word_length > 6:
            readability_score -= 15
        elif avg_word_length > 5:
            readability_score -= 5
        
        # Determine level
        if readability_score >= 80:
            level = 'Easy'
        elif readability_score >= 60:
            level = 'Moderate'
        else:
            level = 'Difficult'
        
        return {
            'score': max(0, readability_score),
            'level': level,
            'avg_sentence_length': round(avg_sentence_length, 1),
            'avg_word_length': round(avg_word_length, 1)
        }
    
    def _analyze_structure(self, text: str) -> Dict[str, Any]:
        """Analyze content structure"""
        paragraphs = text.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        # Check for structural elements
        has_introduction = len(paragraphs) > 0 and len(paragraphs[0].split()) > 30
        has_conclusion = len(paragraphs) > 2 and len(paragraphs[-1].split()) > 20
        
        # Check for subheadings (simple heuristic)
        has_subheadings = bool(re.search(r'\n[A-Z][^.!?]*\n', text))
        
        # Calculate structure score
        structure_score = 50  # Base score
        
        if has_introduction:
            structure_score += 20
        if has_conclusion:
            structure_score += 20
        if has_subheadings:
            structure_score += 10
        
        # Good paragraph count (not too many, not too few)
        if 3 <= len(paragraphs) <= 10:
            structure_score += 10
        
        return {
            'score': min(100, structure_score),
            'paragraph_count': len(paragraphs),
            'has_introduction': has_introduction,
            'has_conclusion': has_conclusion,
            'has_subheadings': has_subheadings
        }
    
    def _analyze_language_quality(self, text: str) -> Dict[str, Any]:
        """Analyze language quality"""
        # Check for grammar/style issues (simplified)
        issues = []
        
        # Check for passive voice (simple heuristic)
        passive_count = len(re.findall(r'\b(was|were|been|being)\s+\w+ed\b', text, re.IGNORECASE))
        if passive_count > 5:
            issues.append('Excessive passive voice')
        
        # Check for repetition
        words = text.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 5:  # Only count longer words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        repetitive_words = [word for word, count in word_freq.items() if count > 5]
        if repetitive_words:
            issues.append(f'Repetitive words: {", ".join(repetitive_words[:3])}')
        
        # Check for clichés (simple list)
        cliches = ['at the end of the day', 'think outside the box', 'low hanging fruit']
        found_cliches = [c for c in cliches if c in text.lower()]
        if found_cliches:
            issues.append('Contains clichés')
        
        # Calculate score
        language_score = 100 - (len(issues) * 20)
        
        return {
            'score': max(0, language_score),
            'issues': issues,
            'passive_voice_count': passive_count,
            'vocabulary_diversity': len(set(words)) / max(len(words), 1)
        }
    
    def _analyze_evidence_quality(self, text: str) -> Dict[str, Any]:
        """Analyze evidence and sourcing quality"""
        # Look for evidence indicators
        evidence_patterns = {
            'citations': r'(?:according to|source:|cited by|reference:)',
            'statistics': r'\b\d+\s*(?:percent|%|million|billion)',
            'quotes': r'"[^"]{10,}"',
            'studies': r'(?:study|research|survey|report)\s+(?:by|from|conducted)',
            'experts': r'(?:expert|professor|dr\.|researcher|analyst)'
        }
        
        evidence_found = {}
        for evidence_type, pattern in evidence_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            evidence_found[evidence_type] = len(matches)
        
        # Calculate evidence score
        evidence_score = 40  # Base score
        
        if evidence_found['citations'] > 0:
            evidence_score += min(evidence_found['citations'] * 10, 20)
        if evidence_found['statistics'] > 0:
            evidence_score += min(evidence_found['statistics'] * 5, 15)
        if evidence_found['quotes'] > 0:
            evidence_score += min(evidence_found['quotes'] * 5, 15)
        if evidence_found['studies'] > 0:
            evidence_score += 10
        
        return {
            'score': min(100, evidence_score),
            'evidence_types': evidence_found,
            'total_evidence_points': sum(evidence_found.values()),
            'has_citations': evidence_found['citations'] > 0,
            'has_data': evidence_found['statistics'] > 0
        }
    
    def _calculate_quality_score(self, readability: Dict, structure: Dict, 
                                language: Dict, evidence: Dict) -> int:
        """Calculate overall content quality score"""
        # Weighted average
        weights = {
            'readability': 0.25,
            'structure': 0.20,
            'language': 0.25,
            'evidence': 0.30
        }
        
        score = (
            readability['score'] * weights['readability'] +
            structure['score'] * weights['structure'] +
            language['score'] * weights['language'] +
            evidence['score'] * weights['evidence']
        )
        
        return int(score)
    
    def _get_quality_level(self, score: int) -> str:
        """Determine quality level from score"""
        if score >= 80:
            return 'Excellent'
        elif score >= 65:
            return 'Good'
        elif score >= 50:
            return 'Fair'
        elif score >= 35:
            return 'Poor'
        else:
            return 'Very Poor'
    
    def _generate_quality_summary(self, score: int, level: str, readability: Dict,
                                 structure: Dict, language: Dict, evidence: Dict) -> str:
        """Generate a summary of content quality"""
        strengths = []
        weaknesses = []
        
        # Check strengths and weaknesses
        if readability['score'] >= 70:
            strengths.append('clear and readable')
        else:
            weaknesses.append('difficult to read')
        
        if structure['score'] >= 70:
            strengths.append('well-structured')
        else:
            weaknesses.append('poor structure')
        
        if language['score'] >= 70:
            strengths.append('good language quality')
        else:
            weaknesses.append('language issues')
        
        if evidence['score'] >= 70:
            strengths.append('well-sourced')
        else:
            weaknesses.append('lacks evidence')
        
        # Build summary
        summary = f"Content quality: {level} ({score}/100). "
        
        if strengths:
            summary += f"Strengths: {', '.join(strengths)}. "
        
        if weaknesses:
            summary += f"Areas for improvement: {', '.join(weaknesses)}."
        
        return summary
