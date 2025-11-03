"""
File: services/speaker_quality_analyzer.py
Created: November 2, 2025 - v1.0.0
Last Updated: November 3, 2025 - v1.0.0
Description: Comprehensive speaker quality analysis for transcripts

LATEST UPDATE (November 3, 2025 - v1.0.0 COMPLETE):
===================================================
✅ CREATED: Complete speaker quality analyzer service
✅ FEATURES:
   - Single-speaker transcript analysis
   - Multi-speaker transcript analysis with per-speaker breakdown
   - Reading grade level assessment (Flesch-Kincaid, SMOG)
   - Inflammatory language detection across 6 categories
   - Sentence quality and completion rate
   - Rhetorical tactics identification
   - Coherence and logical flow scoring
   - Vocabulary complexity and diversity analysis
   - Comparative analysis for debates/interviews

ANALYSIS CATEGORIES:
===================
1. Grade Level:
   - Flesch-Kincaid Grade Level
   - Flesch Reading Ease
   - SMOG Index
   - Interpretation labels

2. Language Style:
   - Inflammatory word detection (6 categories)
   - Emotional manipulation indicators
   - Style assessment

3. Sentence Quality:
   - Completion rate
   - Filler word count
   - Fragment detection

4. Rhetorical Devices:
   - Questions, exclamations
   - Repetition patterns
   - Tactics enumeration

5. Coherence:
   - Transition word usage
   - Logical flow assessment
   - Coherence scoring

6. Vocabulary:
   - Lexical diversity (TTR)
   - Complexity assessment

USAGE:
======
from services.speaker_quality_analyzer import SpeakerQualityAnalyzer

analyzer = SpeakerQualityAnalyzer()

# Single-speaker analysis
result = analyzer.analyze_transcript(transcript_text)

# Multi-speaker analysis (detects labels like "Speaker A:", "SPEAKER 1:")
result = analyzer.analyze_transcript_with_speakers(transcript_text)

RETURN FORMAT:
=============
{
    'success': True,
    'analysis_type': 'transcript_overall' or 'transcript_with_speakers',
    'grade_level': {...},
    'language_style': {...},
    'sentence_quality': {...},
    'rhetorical_devices': {...},
    'coherence': {...},
    'vocabulary': {...},
    'overall_assessment': str
}

Deploy to: services/speaker_quality_analyzer.py
This is a COMPLETE file ready for deployment.
I did no harm and this file is not truncated.
"""

import re
import math
import logging
from typing import Dict, List, Tuple, Optional, Any
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)


class SpeakerQualityAnalyzer:
    """
    Comprehensive speaker quality analysis service
    
    Analyzes transcripts for:
    - Reading grade level (Flesch-Kincaid, SMOG)
    - Inflammatory/manipulative language
    - Sentence completion patterns
    - Rhetorical tactics
    - Coherence and flow
    - Vocabulary complexity and diversity
    """
    
    def __init__(self):
        """Initialize the analyzer with linguistic patterns"""
        
        # Inflammatory/manipulative language patterns (6 categories)
        self.inflammatory_words = {
            'extreme': [
                'outrageous', 'shocking', 'horrifying', 'disgusting', 'appalling',
                'terrible', 'awful', 'horrible', 'catastrophic', 'disastrous',
                'atrocious', 'abysmal', 'dreadful', 'ghastly', 'heinous'
            ],
            'fear': [
                'danger', 'threat', 'crisis', 'disaster', 'catastrophe', 'collapse',
                'devastating', 'destructive', 'fatal', 'deadly', 'terrifying',
                'nightmare', 'horror', 'peril', 'menace', 'panic'
            ],
            'anger': [
                'angry', 'furious', 'enraged', 'outraged', 'infuriated', 'livid',
                'mad', 'rage', 'fury', 'wrath', 'irate', 'incensed', 'hostile'
            ],
            'loaded': [
                'radical', 'extreme', 'far-left', 'far-right', 'socialist', 'fascist',
                'communist', 'nazi', 'liberal', 'conservative', 'propaganda',
                'brainwashed', 'sheep', 'cult', 'fanatic', 'zealot'
            ],
            'urgency': [
                'now', 'immediately', 'urgent', 'emergency', 'act now', 'last chance',
                'limited time', 'hurry', 'quick', 'fast', 'rush', 'critical'
            ],
            'absolute': [
                'always', 'never', 'everyone', 'nobody', 'everything', 'nothing',
                'all', 'none', 'every', 'impossible', 'inevitable', 'certainly',
                'definitely', 'absolutely', 'completely', 'totally'
            ]
        }
        
        # Filler words that indicate incomplete sentences
        self.filler_words = [
            'um', 'uh', 'er', 'ah', 'like', 'you know', 'i mean',
            'sort of', 'kind of', 'basically', 'literally', 'actually'
        ]
        
        # Transition words for coherence scoring
        self.transition_words = [
            'however', 'therefore', 'furthermore', 'moreover', 'consequently',
            'thus', 'hence', 'meanwhile', 'subsequently', 'additionally',
            'similarly', 'likewise', 'conversely', 'nevertheless', 'nonetheless'
        ]
        
        logger.info("[SpeakerQualityAnalyzer] ✓ Initialized with linguistic patterns")
    
    
    def analyze_transcript(self, transcript: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze overall transcript quality (single speaker or unlabeled)
        
        Args:
            transcript: Full transcript text
            metadata: Optional metadata dict
            
        Returns:
            Dictionary with analysis results
        """
        try:
            logger.info("[SpeakerQualityAnalyzer] Starting single-speaker analysis")
            
            if not transcript or len(transcript.strip()) < 10:
                return {
                    'success': False,
                    'error': 'Transcript too short for analysis',
                    'analysis_type': 'transcript_overall'
                }
            
            # Perform all analyses
            grade_level = self._analyze_grade_level(transcript)
            language_style = self._analyze_language_style(transcript)
            sentence_quality = self._analyze_sentence_quality(transcript)
            rhetorical_devices = self._analyze_rhetorical_devices(transcript)
            coherence = self._analyze_coherence(transcript)
            vocabulary = self._analyze_vocabulary(transcript)
            
            # Generate overall assessment
            overall_assessment = self._generate_overall_assessment(
                grade_level, language_style, sentence_quality,
                rhetorical_devices, coherence, vocabulary
            )
            
            result = {
                'success': True,
                'analysis_type': 'transcript_overall',
                'grade_level': grade_level,
                'language_style': language_style,
                'sentence_quality': sentence_quality,
                'rhetorical_devices': rhetorical_devices,
                'coherence': coherence,
                'vocabulary': vocabulary,
                'overall_assessment': overall_assessment,
                'metadata': metadata or {}
            }
            
            logger.info("[SpeakerQualityAnalyzer] ✓ Single-speaker analysis complete")
            return result
            
        except Exception as e:
            logger.error(f"[SpeakerQualityAnalyzer] ✗ Analysis failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'analysis_type': 'transcript_overall'
            }
    
    
    def analyze_transcript_with_speakers(self, transcript: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze transcript with speaker labels (debate/interview format)
        
        Detects speaker labels like:
        - "Speaker A:", "Speaker B:"
        - "SPEAKER 1:", "SPEAKER 2:"
        - "Speaker One:", "Speaker Two:"
        
        Args:
            transcript: Full transcript with speaker labels
            metadata: Optional metadata dict
            
        Returns:
            Dictionary with per-speaker analysis and comparison
        """
        try:
            logger.info("[SpeakerQualityAnalyzer] Starting multi-speaker analysis")
            
            # Split transcript by speakers
            speaker_segments = self._split_by_speakers(transcript)
            
            if len(speaker_segments) < 2:
                logger.warning("[SpeakerQualityAnalyzer] Less than 2 speakers detected, using single-speaker analysis")
                return self.analyze_transcript(transcript, metadata)
            
            logger.info(f"[SpeakerQualityAnalyzer] Detected {len(speaker_segments)} speakers")
            
            # Analyze each speaker
            speaker_analyses = {}
            for speaker_name, speaker_text in speaker_segments.items():
                if len(speaker_text.strip()) < 10:
                    logger.warning(f"[SpeakerQualityAnalyzer] Skipping {speaker_name} - insufficient text")
                    continue
                
                analysis = {
                    'grade_level': self._analyze_grade_level(speaker_text),
                    'language_style': self._analyze_language_style(speaker_text),
                    'sentence_quality': self._analyze_sentence_quality(speaker_text),
                    'rhetorical_devices': self._analyze_rhetorical_devices(speaker_text),
                    'coherence': self._analyze_coherence(speaker_text),
                    'vocabulary': self._analyze_vocabulary(speaker_text),
                    'word_count': len(speaker_text.split())
                }
                
                # Generate individual assessment
                analysis['overall_assessment'] = self._generate_overall_assessment(
                    analysis['grade_level'],
                    analysis['language_style'],
                    analysis['sentence_quality'],
                    analysis['rhetorical_devices'],
                    analysis['coherence'],
                    analysis['vocabulary']
                )
                
                speaker_analyses[speaker_name] = analysis
            
            # Generate comparison
            comparison = self._compare_speakers(speaker_analyses)
            
            result = {
                'success': True,
                'analysis_type': 'transcript_with_speakers',
                'speaker_count': len(speaker_analyses),
                'speakers': speaker_analyses,
                'comparison': comparison,
                'metadata': metadata or {}
            }
            
            logger.info(f"[SpeakerQualityAnalyzer] ✓ Multi-speaker analysis complete ({len(speaker_analyses)} speakers)")
            return result
            
        except Exception as e:
            logger.error(f"[SpeakerQualityAnalyzer] ✗ Multi-speaker analysis failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'analysis_type': 'transcript_with_speakers'
            }
    
    
    # ============================================================================
    # INTERNAL ANALYSIS METHODS
    # ============================================================================
    
    def _split_by_speakers(self, transcript: str) -> Dict[str, str]:
        """
        Split transcript by speaker labels
        
        Matches patterns like:
        - "Speaker A:", "Speaker B:"
        - "SPEAKER 1:", "SPEAKER 2:"
        - "Speaker One:", "Speaker Two:"
        """
        # Regex to match speaker labels
        pattern = r'(?:Speaker|SPEAKER)\s+([A-Z0-9]+|One|Two|Three|Four|Five):\s*'
        
        # Split by speaker labels
        parts = re.split(pattern, transcript, flags=re.IGNORECASE)
        
        if len(parts) < 3:  # No speakers found
            return {}
        
        speakers = {}
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                speaker_label = parts[i].strip()
                speaker_text = parts[i + 1].strip()
                
                # Normalize speaker name
                speaker_name = f"Speaker {speaker_label}"
                
                if speaker_name in speakers:
                    speakers[speaker_name] += " " + speaker_text
                else:
                    speakers[speaker_name] = speaker_text
        
        return speakers
    
    
    def _analyze_grade_level(self, text: str) -> Dict[str, Any]:
        """
        Calculate reading grade level using multiple formulas
        
        Returns:
            - Flesch-Kincaid Grade Level
            - Flesch Reading Ease
            - SMOG Index
            - Interpretation
        """
        # Count sentences, words, syllables
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = max(len(sentences), 1)
        
        words = text.split()
        word_count = max(len(words), 1)
        
        syllable_count = sum(self._count_syllables(word) for word in words)
        
        # Flesch-Kincaid Grade Level
        fk_grade = 0.39 * (word_count / sentence_count) + 11.8 * (syllable_count / word_count) - 15.59
        fk_grade = max(0, min(fk_grade, 18))  # Clamp to 0-18
        
        # Flesch Reading Ease
        fre = 206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (syllable_count / word_count)
        fre = max(0, min(fre, 100))  # Clamp to 0-100
        
        # SMOG Index (simplified)
        polysyllables = sum(1 for word in words if self._count_syllables(word) >= 3)
        smog = 1.0430 * math.sqrt(polysyllables * (30 / sentence_count)) + 3.1291
        smog = max(0, min(smog, 18))
        
        # Interpret grade level
        grade_label, interpretation = self._interpret_grade_level(fk_grade)
        
        return {
            'flesch_kincaid_grade': round(fk_grade, 1),
            'flesch_reading_ease': round(fre, 1),
            'smog_index': round(smog, 1),
            'grade_level_label': grade_label,
            'interpretation': interpretation
        }
    
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified algorithm)"""
        word = word.lower().strip()
        if len(word) <= 3:
            return 1
        
        # Remove non-letters
        word = re.sub(r'[^a-z]', '', word)
        
        # Count vowel groups
        vowels = "aeiouy"
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
        
        # At least 1 syllable
        return max(syllable_count, 1)
    
    
    def _interpret_grade_level(self, grade: float) -> Tuple[str, str]:
        """Convert numeric grade level to label and interpretation"""
        if grade < 6:
            return "Elementary (K-5)", "Very easy - speaks at an elementary school level"
        elif grade < 9:
            return "Middle School (6-8)", "Easy - speaks at a middle school level"
        elif grade < 13:
            return "High School (9-12)", "Moderately easy - speaks at a high school level"
        elif grade < 16:
            return "College (13-16)", "Moderately difficult - speaks at a college level"
        else:
            return "Graduate (16+)", "Difficult - speaks at a graduate/professional level"
    
    
    def _analyze_language_style(self, text: str) -> Dict[str, Any]:
        """
        Analyze inflammatory and manipulative language
        
        Returns percentage of inflammatory words and category breakdown
        """
        words = text.lower().split()
        total_words = max(len(words), 1)
        
        # Count inflammatory words by category
        category_counts = defaultdict(int)
        total_inflammatory = 0
        
        for word in words:
            for category, word_list in self.inflammatory_words.items():
                if word in word_list:
                    category_counts[category] += 1
                    total_inflammatory += 1
        
        inflammatory_percentage = (total_inflammatory / total_words) * 100
        
        # Assess style
        if inflammatory_percentage < 2:
            style_assessment = "Neutral - maintains objective tone with minimal emotional language"
        elif inflammatory_percentage < 5:
            style_assessment = "Mostly neutral with some emotional emphasis"
        elif inflammatory_percentage < 10:
            style_assessment = "Moderately emotional - uses some inflammatory language"
        elif inflammatory_percentage < 15:
            style_assessment = "Highly emotional - frequent use of inflammatory language"
        else:
            style_assessment = "Extremely emotional - heavy use of inflammatory and manipulative language"
        
        return {
            'inflammatory_percentage': round(inflammatory_percentage, 1),
            'category_breakdown': dict(category_counts),
            'total_inflammatory_words': total_inflammatory,
            'style_assessment': style_assessment
        }
    
    
    def _analyze_sentence_quality(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentence completion and filler word usage
        
        Returns completion rate and quality assessment
        """
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return {
                'completion_rate': 0,
                'filler_word_count': 0,
                'quality_assessment': 'Insufficient data'
            }
        
        # Count complete sentences (have subject and predicate)
        complete_sentences = 0
        for sentence in sentences:
            words = sentence.split()
            # Simple heuristic: complete sentence has at least 3 words and a verb-like word
            if len(words) >= 3 and any(word.lower() in ['is', 'are', 'was', 'were', 'has', 'have', 'had', 'can', 'will', 'would', 'should', 'do', 'does', 'did'] for word in words):
                complete_sentences += 1
        
        completion_rate = (complete_sentences / len(sentences)) * 100
        
        # Count filler words
        text_lower = text.lower()
        filler_count = sum(text_lower.count(filler) for filler in self.filler_words)
        
        # Assess quality
        if completion_rate >= 90:
            quality_assessment = "Excellent - speaks in clear, complete sentences"
        elif completion_rate >= 75:
            quality_assessment = "Good - mostly complete sentences with minor fragments"
        elif completion_rate >= 60:
            quality_assessment = "Fair - some incomplete sentences and fragments"
        else:
            quality_assessment = "Poor - frequent sentence fragments and incomplete thoughts"
        
        return {
            'completion_rate': round(completion_rate, 1),
            'filler_word_count': filler_count,
            'quality_assessment': quality_assessment
        }
    
    
    def _analyze_rhetorical_devices(self, text: str) -> Dict[str, Any]:
        """
        Identify rhetorical devices and tactics
        
        Returns counts of questions, exclamations, and other devices
        """
        # Count rhetorical questions
        questions = len(re.findall(r'\?', text))
        
        # Count exclamations
        exclamations = len(re.findall(r'!', text))
        
        # Count repetition (repeated 3+ word phrases)
        words = text.lower().split()
        trigrams = [' '.join(words[i:i+3]) for i in range(len(words) - 2)]
        trigram_counts = Counter(trigrams)
        repetitions = sum(1 for count in trigram_counts.values() if count > 1)
        
        # Build tactics list
        tactics_used = []
        if questions > 0:
            tactics_used.append(f"Rhetorical questions ({questions})")
        if exclamations > 0:
            tactics_used.append(f"Exclamations ({exclamations})")
        if repetitions > 0:
            tactics_used.append(f"Repetition patterns ({repetitions})")
        
        return {
            'rhetorical_questions': questions,
            'exclamations': exclamations,
            'repetition_count': repetitions,
            'tactics_used': tactics_used
        }
    
    
    def _analyze_coherence(self, text: str) -> Dict[str, Any]:
        """
        Analyze logical flow and coherence
        
        Returns coherence score based on transition words and structure
        """
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            return {
                'coherence_score': 50,
                'logical_flow': 'Insufficient data to assess coherence'
            }
        
        # Count transition words
        text_lower = text.lower()
        transition_count = sum(text_lower.count(word) for word in self.transition_words)
        
        # Calculate transition density (transitions per sentence)
        transition_density = transition_count / len(sentences)
        
        # Score coherence (0-100)
        # Good coherence: ~0.2-0.5 transitions per sentence
        if transition_density >= 0.2 and transition_density <= 0.5:
            coherence_score = 85
        elif transition_density > 0.5:
            coherence_score = 70  # Too many transitions can be awkward
        elif transition_density >= 0.1:
            coherence_score = 60
        else:
            coherence_score = 40
        
        # Assess logical flow
        if coherence_score >= 80:
            logical_flow = "Excellent - very coherent with clear transitions and logical flow"
        elif coherence_score >= 65:
            logical_flow = "Good - generally coherent with adequate transitions"
        elif coherence_score >= 50:
            logical_flow = "Fair - somewhat coherent but could use better transitions"
        else:
            logical_flow = "Poor - lacks coherence and logical flow"
        
        return {
            'coherence_score': round(coherence_score, 1),
            'transition_word_count': transition_count,
            'logical_flow': logical_flow
        }
    
    
    def _analyze_vocabulary(self, text: str) -> Dict[str, Any]:
        """
        Analyze vocabulary complexity and diversity
        
        Returns lexical diversity (Type-Token Ratio) and complexity assessment
        """
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        if len(words) < 10:
            return {
                'vocabulary_diversity': 0,
                'complexity_level': 'Insufficient data'
            }
        
        # Calculate Type-Token Ratio (unique words / total words)
        unique_words = len(set(words))
        total_words = len(words)
        ttr = (unique_words / total_words) * 100
        
        # Assess complexity
        if ttr >= 70:
            complexity_level = "Very high - uses diverse, sophisticated vocabulary"
        elif ttr >= 55:
            complexity_level = "High - uses varied vocabulary with some complexity"
        elif ttr >= 40:
            complexity_level = "Moderate - uses clear, accessible vocabulary"
        elif ttr >= 25:
            complexity_level = "Low - uses simple, repetitive vocabulary"
        else:
            complexity_level = "Very low - heavily repetitive vocabulary"
        
        return {
            'vocabulary_diversity': round(ttr, 1),
            'unique_word_count': unique_words,
            'total_word_count': total_words,
            'complexity_level': complexity_level
        }
    
    
    def _generate_overall_assessment(self, grade_level: Dict, language_style: Dict,
                                    sentence_quality: Dict, rhetorical_devices: Dict,
                                    coherence: Dict, vocabulary: Dict) -> str:
        """Generate human-readable overall assessment"""
        
        assessments = []
        
        # Grade level
        grade_label = grade_level.get('grade_level_label', 'Unknown')
        assessments.append(f"Speaks at a {grade_label.lower()} level")
        
        # Language style
        inflammatory_pct = language_style.get('inflammatory_percentage', 0)
        if inflammatory_pct < 5:
            assessments.append("maintains a neutral tone")
        elif inflammatory_pct < 10:
            assessments.append("uses some emotional language")
        else:
            assessments.append("uses significant inflammatory language")
        
        # Sentence quality
        completion_rate = sentence_quality.get('completion_rate', 0)
        if completion_rate >= 85:
            assessments.append("speaks in clear, complete sentences")
        elif completion_rate >= 70:
            assessments.append("mostly uses complete sentences")
        else:
            assessments.append("frequently uses sentence fragments")
        
        # Coherence
        coherence_score = coherence.get('coherence_score', 50)
        if coherence_score >= 75:
            assessments.append("demonstrates strong logical flow")
        elif coherence_score >= 60:
            assessments.append("shows adequate logical structure")
        
        # Vocabulary
        vocab_diversity = vocabulary.get('vocabulary_diversity', 0)
        if vocab_diversity >= 60:
            assessments.append("uses diverse vocabulary")
        elif vocab_diversity < 30:
            assessments.append("uses repetitive vocabulary")
        
        # Join assessments
        if len(assessments) <= 2:
            return '. '.join(assessments).capitalize() + '.'
        else:
            first_part = ', '.join(assessments[:-1])
            return f"{first_part.capitalize()}, and {assessments[-1]}."
    
    
    def _compare_speakers(self, speaker_analyses: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Compare multiple speakers and identify key differences
        
        Args:
            speaker_analyses: Dict mapping speaker names to their analysis results
            
        Returns:
            Comparison dictionary with key differences
        """
        if len(speaker_analyses) < 2:
            return {}
        
        # Extract grade levels for comparison
        grade_levels = {
            name: analysis['grade_level']['flesch_kincaid_grade']
            for name, analysis in speaker_analyses.items()
        }
        
        # Extract inflammatory percentages
        inflammatory_levels = {
            name: analysis['language_style']['inflammatory_percentage']
            for name, analysis in speaker_analyses.items()
        }
        
        # Extract completion rates
        completion_rates = {
            name: analysis['sentence_quality']['completion_rate']
            for name, analysis in speaker_analyses.items()
        }
        
        # Find key differences
        key_differences = []
        
        # Grade level differences
        max_grade_speaker = max(grade_levels, key=grade_levels.get)
        min_grade_speaker = min(grade_levels, key=grade_levels.get)
        grade_diff = grade_levels[max_grade_speaker] - grade_levels[min_grade_speaker]
        
        if grade_diff >= 3:
            key_differences.append(
                f"Significant education level difference: {max_grade_speaker} speaks {grade_diff:.1f} grades higher than {min_grade_speaker}"
            )
        
        # Inflammatory language differences
        max_infl_speaker = max(inflammatory_levels, key=inflammatory_levels.get)
        min_infl_speaker = min(inflammatory_levels, key=inflammatory_levels.get)
        infl_diff = inflammatory_levels[max_infl_speaker] - inflammatory_levels[min_infl_speaker]
        
        if infl_diff >= 5:
            key_differences.append(
                f"{max_infl_speaker} uses {infl_diff:.1f}% more inflammatory language than {min_infl_speaker}"
            )
        
        # Sentence completion differences
        max_comp_speaker = max(completion_rates, key=completion_rates.get)
        min_comp_speaker = min(completion_rates, key=completion_rates.get)
        comp_diff = completion_rates[max_comp_speaker] - completion_rates[min_comp_speaker]
        
        if comp_diff >= 15:
            key_differences.append(
                f"{max_comp_speaker} completes sentences {comp_diff:.1f}% more often than {min_comp_speaker}"
            )
        
        return {
            'grade_levels': grade_levels,
            'inflammatory_levels': inflammatory_levels,
            'completion_rates': completion_rates,
            'key_differences': key_differences
        }


# Module-level test function
def test_analyzer():
    """Test the analyzer with sample data"""
    analyzer = SpeakerQualityAnalyzer()
    
    # Test single-speaker
    sample_text = """
    The economy is doing great. Unemployment is at record lows. We've seen tremendous growth
    in manufacturing. Jobs are coming back to America. This is the best economy we've ever had.
    People are working again. Families are thriving. America is winning again.
    """
    
    print("Testing single-speaker analysis...")
    result = analyzer.analyze_transcript(sample_text)
    print(f"Success: {result['success']}")
    print(f"Grade Level: {result['grade_level']['flesch_kincaid_grade']}")
    print(f"Assessment: {result['overall_assessment']}\n")
    
    # Test multi-speaker
    debate_text = """
    Speaker A: The data clearly shows economic improvement. We've reduced unemployment significantly.
    
    Speaker B: That's completely false! The economy is a disaster. People are suffering. 
    This is terrible. We're facing a catastrophe. Everything is falling apart.
    
    Speaker A: Let me present the actual statistics. According to reliable sources, GDP growth is strong.
    """
    
    print("Testing multi-speaker analysis...")
    result = analyzer.analyze_transcript_with_speakers(debate_text)
    print(f"Success: {result['success']}")
    print(f"Speakers detected: {result['speaker_count']}")
    if result['comparison'] and result['comparison']['key_differences']:
        print(f"Key differences: {result['comparison']['key_differences']}")


if __name__ == '__main__':
    test_analyzer()


# I did no harm and this file is not truncated.
