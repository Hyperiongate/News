# FILE: services/content_analyzer.py
"""
services/content_analyzer.py - Content analysis service
"""

import re
from typing import Dict, Any, List

class ContentAnalyzer:
    """Analyze article content structure and quality"""
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze content structure and characteristics"""
        if not text:
            return self._empty_analysis()
        
        # Basic metrics
        word_count = len(text.split())
        sentence_count = len(re.split(r'[.!?]+', text))
        paragraph_count = len(re.split(r'\n\n+', text.strip()))
        
        # Readability metrics
        avg_sentence_length = word_count / max(sentence_count, 1)
        avg_word_length = sum(len(word) for word in text.split()) / max(word_count, 1)
        
        # Content quality indicators
        quality_indicators = self._analyze_quality_indicators(text)
        
        # Structure analysis
        structure_analysis = self._analyze_structure(text)
        
        # Determine readability level
        readability_level = self._calculate_readability(avg_sentence_length, avg_word_length)
        
        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'paragraph_count': paragraph_count,
            'average_sentence_length': round(avg_sentence_length, 1),
            'average_word_length': round(avg_word_length, 1),
            'readability_level': readability_level,
            'quality_indicators': quality_indicators,
            'structure_analysis': structure_analysis,
            'content_density': self._calculate_content_density(text),
            'vocabulary_complexity': self._analyze_vocabulary_complexity(text)
        }
    
    def _analyze_quality_indicators(self, text: str) -> Dict[str, bool]:
        """Analyze indicators of content quality"""
        return {
            'has_statistics': bool(re.search(r'\d+\s*(?:percent|%)', text)),
            'has_quotes': '"' in text,
            'has_questions': '?' in text,
            'has_examples': bool(re.search(r'(?:for example|for instance|such as)', text, re.IGNORECASE)),
            'has_comparisons': bool(re.search(r'(?:compared to|in contrast|whereas|unlike)', text, re.IGNORECASE)),
            'has_expert_mentions': bool(re.search(r'(?:expert|professor|researcher|analyst|scientist)', text, re.IGNORECASE))
        }
    
    def _analyze_structure(self, text: str) -> Dict[str, Any]:
        """Analyze document structure"""
        lines = text.split('\n')
        
        # Check for headings (lines that are shorter and possibly in caps)
        potential_headings = []
        for line in lines:
            if line.strip() and len(line.strip()) < 100:
                if line.isupper() or line.strip().endswith(':'):
                    potential_headings.append(line.strip())
        
        # Check for lists
        has_bullet_points = any(line.strip().startswith(('•', '-', '*', '–')) for line in lines)
        has_numbered_list = bool(re.search(r'^\d+\.', text, re.MULTILINE))
        
        return {
            'has_headings': len(potential_headings) > 0,
            'heading_count': len(potential_headings),
            'has_lists': has_bullet_points or has_numbered_list,
            'has_bullet_points': has_bullet_points,
            'has_numbered_list': has_numbered_list
        }
    
    def _calculate_readability(self, avg_sentence_length: float, avg_word_length: float) -> str:
        """Calculate readability level based on sentence and word length"""
        # Simplified readability calculation
        if avg_sentence_length < 14 and avg_word_length < 5:
            return 'Easy'
        elif avg_sentence_length < 20 and avg_word_length < 5.5:
            return 'Moderate'
        elif avg_sentence_length < 25 and avg_word_length < 6:
            return 'Difficult'
        else:
            return 'Very Difficult'
    
    def _calculate_content_density(self, text: str) -> str:
        """Calculate information density of content"""
        # Count substantive words (nouns, verbs, adjectives)
        words = text.split()
        
        # Simple heuristic: longer words are more likely to be substantive
        substantive_words = [w for w in words if len(w) > 4]
        density_ratio = len(substantive_words) / max(len(words), 1)
        
        if density_ratio > 0.4:
            return 'High'
        elif density_ratio > 0.25:
            return 'Medium'
        else:
            return 'Low'
    
    def _analyze_vocabulary_complexity(self, text: str) -> str:
        """Analyze vocabulary complexity"""
        words = text.split()
        
        # Count complex words (3+ syllables, approximated by length)
        complex_words = [w for w in words if len(w) > 10]
        complexity_ratio = len(complex_words) / max(len(words), 1)
        
        if complexity_ratio > 0.15:
            return 'Complex'
        elif complexity_ratio > 0.08:
            return 'Moderate'
        else:
            return 'Simple'
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure"""
        return {
            'word_count': 0,
            'sentence_count': 0,
            'paragraph_count': 0,
            'average_sentence_length': 0,
            'average_word_length': 0,
            'readability_level': 'Unknown',
            'quality_indicators': {},
            'structure_analysis': {},
            'content_density': 'Unknown',
            'vocabulary_complexity': 'Unknown'
        }
