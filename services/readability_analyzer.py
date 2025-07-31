# services/readability_analyzer.py
"""
Readability Analysis Service
Analyzes text readability and complexity
"""

import re
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class ReadabilityAnalyzer:
    """Analyze text readability and provide recommendations"""
    
    def analyze(self, article_data):
        """
        Analyze article readability
        
        Args:
            article_data: Dictionary containing article information
            
        Returns:
            Dictionary with readability analysis
        """
        content = article_data.get('content') or article_data.get('text', '')
        
        if not content:
            return self._get_empty_analysis()
        
        # Calculate readability metrics
        metrics = self._calculate_readability_metrics(content)
        
        # Determine readability level
        level = self._determine_readability_level(metrics['flesch_score'])
        
        # Get recommendations
        recommendations = self._get_recommendations(metrics, level)
        
        return {
            'score': metrics['flesch_score'],
            'level': level,
            'details': {
                'average_sentence_length': metrics['avg_sentence_length'],
                'average_syllables_per_word': metrics['avg_syllables'],
                'complex_word_percentage': metrics['complex_word_percentage'],
                'sentence_complexity': metrics['sentence_complexity'],
                'paragraph_length': metrics['avg_paragraph_length']
            },
            'metrics': metrics,
            'recommendations': recommendations,
            'target_audience': self._determine_target_audience(level)
        }
    
    def _calculate_readability_metrics(self, text):
        """Calculate various readability metrics"""
        # Basic text processing
        sentences = self._split_sentences(text)
        words = text.split()
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        
        # Count syllables
        total_syllables = sum(self._count_syllables(word) for word in words)
        
        # Calculate averages
        avg_sentence_length = len(words) / max(len(sentences), 1)
        avg_syllables = total_syllables / max(len(words), 1)
        avg_paragraph_length = len(sentences) / max(len(paragraphs), 1)
        
        # Count complex words (3+ syllables)
        complex_words = [w for w in words if self._count_syllables(w) >= 3]
        complex_word_percentage = (len(complex_words) / max(len(words), 1)) * 100
        
        # Flesch Reading Ease Score
        flesch_score = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables
        flesch_score = max(0, min(100, flesch_score))
        
        # Flesch-Kincaid Grade Level
        fk_grade = 0.39 * avg_sentence_length + 11.8 * avg_syllables - 15.59
        fk_grade = max(0, fk_grade)
        
        # Gunning Fog Index
        fog_index = 0.4 * (avg_sentence_length + complex_word_percentage)
        
        # SMOG Index (Simplified)
        smog_index = 1.0430 * (30 * (len(complex_words) / len(sentences))) ** 0.5 + 3.1291 if len(sentences) >= 30 else 0
        
        # Coleman-Liau Index
        letters_per_100_words = sum(len(word) for word in words) / len(words) * 100
        sentences_per_100_words = len(sentences) / len(words) * 100
        coleman_liau = 0.0588 * letters_per_100_words - 0.296 * sentences_per_100_words - 15.8
        
        # Automated Readability Index
        characters = sum(len(word) for word in words)
        ari = 4.71 * (characters / len(words)) + 0.5 * (len(words) / len(sentences)) - 21.43
        
        # Sentence complexity
        sentence_complexity = self._calculate_sentence_complexity(sentences)
        
        return {
            'flesch_score': round(flesch_score, 1),
            'flesch_kincaid_grade': round(fk_grade, 1),
            'gunning_fog': round(fog_index, 1),
            'smog_index': round(smog_index, 1),
            'coleman_liau_index': round(coleman_liau, 1),
            'automated_readability_index': round(ari, 1),
            'avg_sentence_length': round(avg_sentence_length, 1),
            'avg_syllables': round(avg_syllables, 2),
            'avg_paragraph_length': round(avg_paragraph_length, 1),
            'complex_word_percentage': round(complex_word_percentage, 1),
            'sentence_complexity': sentence_complexity,
            'total_words': len(words),
            'total_sentences': len(sentences),
            'total_paragraphs': len(paragraphs),
            'avg_word_length': round(sum(len(word) for word in words) / max(len(words), 1), 1),
            'vocabulary_diversity': round(len(set(word.lower() for word in words)) / max(len(words), 1), 3)
        }
    
    def _split_sentences(self, text):
        """Split text into sentences"""
        # Improved sentence splitter
        # Handle abbreviations
        text = re.sub(r'\b(Mr|Mrs|Dr|Ms|Prof|Sr|Jr)\.\s*', r'\1<PERIOD> ', text)
        text = re.sub(r'\b(Inc|Ltd|Corp|Co)\.\s*', r'\1<PERIOD> ', text)
        text = re.sub(r'\b(Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.\s*', r'\1<PERIOD> ', text)
        
        # Split on sentence endings
        sentences = re.split(r'[.!?]+\s+', text)
        
        # Restore periods
        sentences = [s.replace('<PERIOD>', '.') for s in sentences]
        
        # Filter out empty sentences
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        
        return sentences
    
    def _count_syllables(self, word):
        """Estimate syllable count for a word"""
        word = word.lower().strip()
        
        # Remove non-alphabetic characters
        word = re.sub(r'[^a-z]', '', word)
        
        if len(word) <= 2:
            return 1
        
        # Count vowel groups
        vowels = 'aeiouy'
        syllables = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllables += 1
            previous_was_vowel = is_vowel
        
        # Adjust for silent e
        if word.endswith('e') and syllables > 1:
            syllables -= 1
        
        # Adjust for certain endings
        if word.endswith('le') and len(word) > 2 and word[-3] not in vowels:
            syllables += 1
        
        # Special cases
        if word.endswith('ism'):
            syllables += 1
        
        # Ensure at least 1 syllable
        return max(1, syllables)
    
    def _calculate_sentence_complexity(self, sentences):
        """Calculate sentence complexity score"""
        if not sentences:
            return 'simple'
        
        complex_count = 0
        very_complex_count = 0
        
        for sentence in sentences:
            # Count complexity indicators
            commas = sentence.count(',')
            semicolons = sentence.count(';')
            colons = sentence.count(':')
            dashes = sentence.count('—') + sentence.count(' - ')
            words = len(sentence.split())
            
            # Count subordinate conjunctions
            subordinates = ['because', 'although', 'while', 'since', 'unless', 'whereas', 'wherever']
            sub_count = sum(1 for sub in subordinates if f' {sub} ' in sentence.lower())
            
            # Determine complexity
            complexity_score = (
                (words > 25) * 2 +
                (commas >= 3) * 2 +
                (semicolons > 0) * 3 +
                (colons > 0) * 1 +
                (dashes > 0) * 1 +
                (sub_count > 0) * 2
            )
            
            if complexity_score >= 6:
                very_complex_count += 1
            elif complexity_score >= 3:
                complex_count += 1
        
        # Determine overall complexity
        total = len(sentences)
        if very_complex_count > total * 0.3:
            return 'very complex'
        elif (complex_count + very_complex_count) > total * 0.5:
            return 'complex'
        elif (complex_count + very_complex_count) > total * 0.3:
            return 'moderate'
        else:
            return 'simple'
    
    def _determine_readability_level(self, flesch_score):
        """Determine readability level from Flesch score"""
        if flesch_score >= 90:
            return 'Very Easy'
        elif flesch_score >= 80:
            return 'Easy'
        elif flesch_score >= 70:
            return 'Fairly Easy'
        elif flesch_score >= 60:
            return 'Medium'
        elif flesch_score >= 50:
            return 'Fairly Difficult'
        elif flesch_score >= 30:
            return 'Difficult'
        else:
            return 'Very Difficult'
    
    def _determine_target_audience(self, level):
        """Determine target audience based on readability level"""
        audience_map = {
            'Very Easy': '5th grade level - Very accessible to general public',
            'Easy': '6th grade level - Accessible to most readers',
            'Fairly Easy': '7th grade level - Standard newspaper level',
            'Medium': '8th-9th grade level - High school level',
            'Fairly Difficult': '10th-12th grade level - Some college',
            'Difficult': 'College level - Academic or professional',
            'Very Difficult': 'Graduate level - Specialized academic'
        }
        
        return audience_map.get(level, 'General audience')
    
    def _get_recommendations(self, metrics, level):
        """Get readability improvement recommendations"""
        recommendations = []
        
        # Sentence length recommendations
        if metrics['avg_sentence_length'] > 20:
            recommendations.append({
                'issue': 'Long sentences',
                'suggestion': 'Break up sentences longer than 20 words for better readability',
                'impact': 'high'
            })
        elif metrics['avg_sentence_length'] < 10:
            recommendations.append({
                'issue': 'Short sentences',
                'suggestion': 'Combine related short sentences to improve flow',
                'impact': 'medium'
            })
        
        # Word complexity recommendations
        if metrics['complex_word_percentage'] > 20:
            recommendations.append({
                'issue': 'Complex vocabulary',
                'suggestion': 'Replace complex words with simpler alternatives where possible',
                'impact': 'high'
            })
        
        # Paragraph length
        if metrics['avg_paragraph_length'] > 8:
            recommendations.append({
                'issue': 'Long paragraphs',
                'suggestion': 'Break up paragraphs into smaller chunks (3-5 sentences)',
                'impact': 'medium'
            })
        
        # Sentence complexity
        if metrics['sentence_complexity'] in ['complex', 'very complex']:
            recommendations.append({
                'issue': 'Complex sentence structure',
                'suggestion': 'Simplify sentence structure by reducing subordinate clauses',
                'impact': 'high'
            })
        
        # Overall difficulty
        if level in ['Difficult', 'Very Difficult']:
            recommendations.append({
                'issue': 'High reading difficulty',
                'suggestion': 'Consider rewriting for a broader audience (aim for 8th-grade level)',
                'impact': 'high'
            })
        elif level in ['Very Easy', 'Easy'] and metrics['total_words'] > 500:
            recommendations.append({
                'issue': 'Very simple language',
                'suggestion': 'Consider adding more sophisticated vocabulary for professional audiences',
                'impact': 'low'
            })
        
        # Vocabulary diversity
        if metrics['vocabulary_diversity'] < 0.4:
            recommendations.append({
                'issue': 'Repetitive vocabulary',
                'suggestion': 'Use synonyms to avoid word repetition',
                'impact': 'medium'
            })
        
        # Grade level specific
        if metrics['flesch_kincaid_grade'] > 12:
            recommendations.append({
                'issue': 'Graduate-level reading required',
                'suggestion': 'Simplify to reach a wider audience',
                'impact': 'high'
            })
        
        if not recommendations:
            recommendations.append({
                'issue': None,
                'suggestion': 'Readability is well-balanced for the target audience',
                'impact': 'none'
            })
        
        return recommendations
    
    def _get_empty_analysis(self):
        """Return empty analysis structure"""
        return {
            'score': 0,
            'level': 'Unknown',
            'details': {
                'average_sentence_length': 0,
                'average_syllables_per_word': 0,
                'complex_word_percentage': 0,
                'sentence_complexity': 'unknown',
                'paragraph_length': 0
            },
            'metrics': {
                'flesch_score': 0,
                'flesch_kincaid_grade': 0,
                'gunning_fog': 0,
                'smog_index': 0,
                'coleman_liau_index': 0,
                'automated_readability_index': 0,
                'avg_sentence_length': 0,
                'avg_syllables': 0,
                'avg_paragraph_length': 0,
                'complex_word_percentage': 0,
                'sentence_complexity': 'unknown',
                'total_words': 0,
                'total_sentences': 0,
                'total_paragraphs': 0,
                'avg_word_length': 0,
                'vocabulary_diversity': 0
            },
            'recommendations': [{'issue': 'No content', 'suggestion': 'No content to analyze', 'impact': 'none'}],
            'target_audience': 'Unknown'
        }
