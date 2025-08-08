"""
FILE: services/content_analyzer.py
PURPOSE: Enhanced content quality analysis service with readability scores, evidence detection, and structure assessment
"""

import logging
import re
import math
from typing import Dict, Any, List, Tuple, Optional
from collections import Counter
from services.base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)


class ContentAnalyzer(BaseAnalyzer):
    """Enhanced content quality analysis service that inherits from BaseAnalyzer"""
    
    def __init__(self):
        super().__init__('content_analyzer')
        logger.info("Enhanced ContentAnalyzer initialized")
        
        # Statistical claim patterns
        self.stat_patterns = {
            'percentage': r'\b\d+(?:\.\d+)?\s*(?:percent|%)',
            'comparison': r'(?:increased?|decreased?|grew|fell|rose|dropped)\s+(?:by\s+)?\d+(?:\.\d+)?\s*(?:percent|%|times|fold)',
            'ranking': r'(?:ranked?|ranks?)\s+(?:#|number|no\.?)?\s*\d+',
            'population': r'\b\d+(?:,\d{3})*(?:\.\d+)?\s*(?:million|billion|thousand)\s+(?:people|users|customers|citizens)',
            'monetary': r'(?:\$|USD|EUR|£|¥)\s*\d+(?:,\d{3})*(?:\.\d+)?\s*(?:million|billion|thousand)?',
            'ratio': r'\b\d+\s*(?:to|:)\s*\d+\b',
            'survey': r'\b\d+(?:\.\d+)?\s*(?:percent|%)\s+of\s+(?:respondents|people|surveyed|participants)'
        }
        
        # Evidence quality indicators
        self.evidence_indicators = {
            'strong': [
                r'according to (?:a )?\w+ (?:study|research|report|analysis)',
                r'peer[- ]reviewed',
                r'published in \w+ journal',
                r'data from \w+ (?:agency|organization|institution)',
                r'official statistics',
                r'government report',
                r'academic research'
            ],
            'moderate': [
                r'survey (?:conducted|shows|reveals)',
                r'experts? (?:say|believe|argue)',
                r'analysis (?:shows|reveals|indicates)',
                r'industry report',
                r'market research'
            ],
            'weak': [
                r'some (?:say|believe|think)',
                r'critics argue',
                r'observers note',
                r'reportedly',
                r'allegedly'
            ]
        }
    
    def _check_availability(self) -> bool:
        """Check if the service is available"""
        return True  # Always available as it's self-contained
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze content quality using the standardized interface
        
        Expected input:
            - text: Article text to analyze
            - title: (optional) Article title
            - images: (optional) List of image URLs
            - videos: (optional) List of video URLs
            
        Returns:
            Standardized response with comprehensive content quality analysis
        """
        if not self.is_available:
            return self.get_default_result()
        
        text = data.get('text')
        if not text:
            return self.get_error_result("Missing required field: 'text'")
        
        title = data.get('title', '')
        images = data.get('images', [])
        videos = data.get('videos', [])
        
        return self._analyze_content(text, title, images, videos)
    
    def _analyze_content(self, text: str, title: str = '', images: List[str] = None, videos: List[str] = None) -> Dict[str, Any]:
        """Perform comprehensive content analysis"""
        try:
            # Core analyses
            readability = self._calculate_readability_scores(text)
            structure = self._analyze_structure_quality(text)
            language = self._analyze_language_quality(text)
            evidence = self._analyze_evidence_quality(text)
            
            # Additional analyses
            stats = self._analyze_statistical_claims(text)
            media_ratio = self._analyze_media_ratio(text, images or [], videos or [])
            
            # Calculate overall quality score
            quality_score = self._calculate_overall_quality(
                readability, structure, language, evidence, stats, media_ratio
            )
            
            # Determine quality level
            quality_level = self._get_quality_level(quality_score)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                readability, structure, language, evidence, stats
            )
            
            return {
                'service': self.service_name,
                'success': True,
                'data': {
                    'quality_score': quality_score,
                    'quality_level': quality_level,
                    'readability': readability,
                    'structure': structure,
                    'language_quality': language,
                    'evidence_quality': evidence,
                    'statistical_claims': stats,
                    'media_analysis': media_ratio,
                    'recommendations': recommendations,
                    'summary': self._generate_comprehensive_summary(
                        quality_score, quality_level, readability, structure,
                        language, evidence, stats
                    ),
                    'key_metrics': {
                        'word_count': len(text.split()),
                        'sentence_count': len(re.split(r'[.!?]+', text)),
                        'paragraph_count': structure['paragraph_count'],
                        'evidence_score': evidence['score'],
                        'has_citations': evidence['citation_count'] > 0
                    }
                },
                'metadata': {
                    'text_length': len(text),
                    'has_title': bool(title),
                    'image_count': len(images or []),
                    'video_count': len(videos or [])
                }
            }
            
        except Exception as e:
            logger.error(f"Content analysis failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _calculate_readability_scores(self, text: str) -> Dict[str, Any]:
        """Calculate multiple readability scores including Flesch-Kincaid"""
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        words = re.findall(r'\b\w+\b', text.lower())
        
        if not sentences or not words:
            return {
                'flesch_reading_ease': 0,
                'flesch_kincaid_grade': 0,
                'gunning_fog': 0,
                'avg_sentence_length': 0,
                'avg_syllables_per_word': 0,
                'reading_level': 'Unknown',
                'reading_time_minutes': 0
            }
        
        # Count syllables
        total_syllables = sum(self._count_syllables(word) for word in words)
        
        # Calculate metrics
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables_per_word = total_syllables / len(words)
        
        # Flesch Reading Ease (0-100, higher is easier)
        flesch_reading_ease = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word
        flesch_reading_ease = max(0, min(100, flesch_reading_ease))
        
        # Flesch-Kincaid Grade Level
        flesch_kincaid_grade = 0.39 * avg_sentence_length + 11.8 * avg_syllables_per_word - 15.59
        flesch_kincaid_grade = max(0, flesch_kincaid_grade)
        
        # Gunning Fog Index
        complex_words = sum(1 for word in words if self._count_syllables(word) > 2)
        fog_index = 0.4 * (avg_sentence_length + 100 * (complex_words / len(words)))
        
        # Determine reading level
        if flesch_reading_ease >= 90:
            reading_level = "Very Easy (5th grade)"
        elif flesch_reading_ease >= 80:
            reading_level = "Easy (6th grade)"
        elif flesch_reading_ease >= 70:
            reading_level = "Fairly Easy (7th grade)"
        elif flesch_reading_ease >= 60:
            reading_level = "Standard (8-9th grade)"
        elif flesch_reading_ease >= 50:
            reading_level = "Fairly Difficult (10-12th grade)"
        elif flesch_reading_ease >= 30:
            reading_level = "Difficult (College)"
        else:
            reading_level = "Very Difficult (Graduate)"
        
        # Estimate reading time (average 200-250 words per minute)
        reading_time = len(words) / 225
        
        return {
            'flesch_reading_ease': round(flesch_reading_ease, 1),
            'flesch_kincaid_grade': round(flesch_kincaid_grade, 1),
            'gunning_fog': round(fog_index, 1),
            'avg_sentence_length': round(avg_sentence_length, 1),
            'avg_syllables_per_word': round(avg_syllables_per_word, 2),
            'reading_level': reading_level,
            'reading_time_minutes': round(reading_time, 1),
            'complex_word_percentage': round((complex_words / len(words)) * 100, 1)
        }
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified algorithm)"""
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
        
        # Ensure at least one syllable
        return max(1, syllable_count)
    
    def _analyze_structure_quality(self, text: str) -> Dict[str, Any]:
        """Analyze document structure quality"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        # Detect structural elements
        has_introduction = self._detect_introduction(paragraphs)
        has_conclusion = self._detect_conclusion(paragraphs)
        subheadings = self._detect_subheadings(text)
        
        # Analyze paragraph quality
        paragraph_lengths = [len(p.split()) for p in paragraphs]
        avg_paragraph_length = sum(paragraph_lengths) / len(paragraph_lengths) if paragraph_lengths else 0
        
        # Check for logical flow
        transition_words = self._count_transition_words(text)
        
        # Calculate structure score
        structure_score = 40  # Base score
        
        if has_introduction:
            structure_score += 15
        if has_conclusion:
            structure_score += 15
        if len(subheadings) > 0:
            structure_score += 10
        if 50 <= avg_paragraph_length <= 150:  # Ideal paragraph length
            structure_score += 10
        if transition_words > len(paragraphs):
            structure_score += 10
        
        return {
            'score': min(100, structure_score),
            'paragraph_count': len(paragraphs),
            'avg_paragraph_length': round(avg_paragraph_length, 1),
            'has_introduction': has_introduction,
            'has_conclusion': has_conclusion,
            'subheading_count': len(subheadings),
            'subheadings': subheadings[:5],  # First 5 subheadings
            'transition_word_count': transition_words,
            'structure_quality': self._get_structure_quality_level(structure_score)
        }
    
    def _detect_introduction(self, paragraphs: List[str]) -> bool:
        """Detect if article has proper introduction"""
        if not paragraphs:
            return False
        
        first_para = paragraphs[0].lower()
        intro_indicators = ['this article', 'we will', 'in this', 'overview', 'introduction']
        
        return any(indicator in first_para for indicator in intro_indicators) or len(paragraphs[0].split()) > 40
    
    def _detect_conclusion(self, paragraphs: List[str]) -> bool:
        """Detect if article has proper conclusion"""
        if len(paragraphs) < 3:
            return False
        
        last_para = paragraphs[-1].lower()
        conclusion_indicators = ['in conclusion', 'to sum up', 'in summary', 'overall', 'finally']
        
        return any(indicator in last_para for indicator in conclusion_indicators)
    
    def _detect_subheadings(self, text: str) -> List[str]:
        """Detect subheadings in the text"""
        # Pattern for lines that are likely subheadings
        lines = text.split('\n')
        subheadings = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check if line is likely a subheading
            if (len(line) < 100 and  # Not too long
                not line.endswith('.') and  # Doesn't end with period
                (line[0].isupper() or line.startswith(tuple('0123456789'))) and  # Starts with capital or number
                (i == 0 or not lines[i-1].strip() or lines[i-1].strip() == '')):  # Preceded by blank line
                
                subheadings.append(line)
        
        return subheadings
    
    def _count_transition_words(self, text: str) -> int:
        """Count transition words that indicate logical flow"""
        transition_words = [
            'however', 'therefore', 'moreover', 'furthermore', 'additionally',
            'consequently', 'nevertheless', 'meanwhile', 'subsequently',
            'in contrast', 'on the other hand', 'for example', 'for instance',
            'in addition', 'as a result', 'in conclusion'
        ]
        
        text_lower = text.lower()
        count = sum(1 for word in transition_words if word in text_lower)
        
        return count
    
    def _analyze_language_quality(self, text: str) -> Dict[str, Any]:
        """Analyze language quality and style"""
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        words = re.findall(r'\b\w+\b', text.lower())
        
        issues = []
        strengths = []
        
        # Check for passive voice
        passive_patterns = [
            r'\b(?:is|are|was|were|been|being)\s+\w+ed\b',
            r'\b(?:is|are|was|were|been|being)\s+\w+en\b'
        ]
        passive_count = sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in passive_patterns)
        passive_percentage = (passive_count / len(sentences)) * 100 if sentences else 0
        
        if passive_percentage > 30:
            issues.append(f'High passive voice usage ({passive_percentage:.1f}%)')
        elif passive_percentage < 10:
            strengths.append('Active voice predominant')
        
        # Vocabulary diversity
        unique_words = set(words)
        vocabulary_diversity = len(unique_words) / len(words) if words else 0
        
        if vocabulary_diversity < 0.4:
            issues.append('Limited vocabulary diversity')
        elif vocabulary_diversity > 0.6:
            strengths.append('Rich vocabulary')
        
        # Sentence variety
        sentence_lengths = [len(s.split()) for s in sentences]
        if sentence_lengths:
            length_variance = self._calculate_variance(sentence_lengths)
            if length_variance < 20:
                issues.append('Monotonous sentence structure')
            else:
                strengths.append('Good sentence variety')
        
        # Check for clichés and overused phrases
        cliches = self._detect_cliches(text)
        if cliches:
            issues.append(f'Contains clichés: {", ".join(cliches[:3])}')
        
        # Check for jargon
        jargon_score = self._detect_jargon_density(text)
        if jargon_score > 0.05:
            issues.append('High jargon density')
        elif jargon_score < 0.02:
            strengths.append('Clear, accessible language')
        
        # Calculate overall language score
        language_score = 70  # Base score
        language_score -= len(issues) * 10
        language_score += len(strengths) * 5
        language_score = max(0, min(100, language_score))
        
        return {
            'score': language_score,
            'issues': issues,
            'strengths': strengths,
            'passive_voice_percentage': round(passive_percentage, 1),
            'vocabulary_diversity': round(vocabulary_diversity, 3),
            'avg_sentence_length': round(sum(sentence_lengths) / len(sentence_lengths), 1) if sentence_lengths else 0,
            'sentence_length_variance': round(length_variance, 1) if sentence_lengths else 0,
            'cliche_count': len(cliches),
            'jargon_density': round(jargon_score, 3)
        }
    
    def _calculate_variance(self, numbers: List[float]) -> float:
        """Calculate variance of a list of numbers"""
        if not numbers:
            return 0
        mean = sum(numbers) / len(numbers)
        variance = sum((x - mean) ** 2 for x in numbers) / len(numbers)
        return variance
    
    def _detect_cliches(self, text: str) -> List[str]:
        """Detect common clichés in text"""
        cliches = [
            'at the end of the day', 'think outside the box', 'low hanging fruit',
            'paradigm shift', 'synergy', 'game changer', 'moving forward',
            'circle back', 'touch base', 'take it to the next level',
            'win-win situation', 'cutting edge', 'best practice'
        ]
        
        text_lower = text.lower()
        found_cliches = [cliche for cliche in cliches if cliche in text_lower]
        
        return found_cliches
    
    def _detect_jargon_density(self, text: str) -> float:
        """Detect density of jargon and technical terms"""
        # Simplified jargon detection - looks for complex/technical words
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Words that are likely jargon (long, contain certain suffixes)
        jargon_indicators = ['-ization', '-ality', '-ology', '-ism', '-ive', '-ment']
        jargon_count = 0
        
        for word in words:
            if len(word) > 12 or any(word.endswith(suffix) for suffix in jargon_indicators):
                jargon_count += 1
        
        return jargon_count / len(words) if words else 0
    
    def _analyze_evidence_quality(self, text: str) -> Dict[str, Any]:
        """Analyze quality and presence of evidence"""
        evidence_score = 0
        evidence_types = []
        
        # Count different types of evidence
        citation_count = len(re.findall(r'(?:according to|cited by|source:|reference:)', text, re.IGNORECASE))
        quote_count = len(re.findall(r'"[^"]{20,}"', text))  # Quotes longer than 20 chars
        stat_count = len(re.findall(r'\b\d+(?:\.\d+)?\s*(?:percent|%)', text))
        
        # Check for strong evidence
        strong_evidence_count = 0
        for pattern in self.evidence_indicators['strong']:
            if re.search(pattern, text, re.IGNORECASE):
                strong_evidence_count += 1
                evidence_types.append('Strong academic/official sources')
        
        # Check for moderate evidence
        moderate_evidence_count = 0
        for pattern in self.evidence_indicators['moderate']:
            if re.search(pattern, text, re.IGNORECASE):
                moderate_evidence_count += 1
        
        # Check for weak evidence
        weak_evidence_count = 0
        for pattern in self.evidence_indicators['weak']:
            if re.search(pattern, text, re.IGNORECASE):
                weak_evidence_count += 1
        
        # Calculate evidence score
        evidence_score = min(100, (
            strong_evidence_count * 20 +
            moderate_evidence_count * 10 +
            weak_evidence_count * 5 +
            citation_count * 5 +
            quote_count * 3 +
            stat_count * 2
        ))
        
        # Determine evidence quality
        if evidence_score >= 80:
            quality_level = "Excellent"
        elif evidence_score >= 60:
            quality_level = "Good"
        elif evidence_score >= 40:
            quality_level = "Moderate"
        elif evidence_score >= 20:
            quality_level = "Weak"
        else:
            quality_level = "Very Weak"
        
        # Check for source diversity
        source_diversity = self._check_source_diversity(text)
        
        return {
            'score': evidence_score,
            'quality_level': quality_level,
            'citation_count': citation_count,
            'quote_count': quote_count,
            'statistic_count': stat_count,
            'strong_evidence_count': strong_evidence_count,
            'moderate_evidence_count': moderate_evidence_count,
            'weak_evidence_count': weak_evidence_count,
            'source_diversity': source_diversity,
            'evidence_types': list(set(evidence_types)),
            'has_primary_sources': strong_evidence_count > 0,
            'evidence_density': round((citation_count + quote_count) / (len(text.split()) / 100), 2)
        }
    
    def _check_source_diversity(self, text: str) -> str:
        """Check diversity of sources cited"""
        source_patterns = [
            r'according to (\w+)',
            r'(\w+) (?:said|says|stated)',
            r'(?:study|research|report) (?:by|from) (\w+)',
            r'(\w+) (?:reported|reports)'
        ]
        
        sources = set()
        for pattern in source_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            sources.update(matches)
        
        if len(sources) >= 5:
            return "High"
        elif len(sources) >= 3:
            return "Moderate"
        elif len(sources) >= 1:
            return "Low"
        else:
            return "None"
    
    def _analyze_statistical_claims(self, text: str) -> Dict[str, Any]:
        """Analyze and verify statistical claims"""
        claims = []
        
        for claim_type, pattern in self.stat_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                claims.append({
                    'type': claim_type,
                    'text': match,
                    'context': self._get_claim_context(text, match)
                })
        
        # Analyze claim quality
        verified_count = 0
        sourced_count = 0
        
        for claim in claims:
            context = claim['context'].lower()
            
            # Check if claim is sourced
            if any(indicator in context for indicator in ['according to', 'study', 'report', 'survey']):
                sourced_count += 1
                claim['is_sourced'] = True
            else:
                claim['is_sourced'] = False
            
            # Check for verification language
            if any(word in context for word in ['verified', 'confirmed', 'official']):
                verified_count += 1
                claim['is_verified'] = True
            else:
                claim['is_verified'] = False
        
        # Calculate statistics score
        if claims:
            sourced_percentage = (sourced_count / len(claims)) * 100
            verified_percentage = (verified_count / len(claims)) * 100
        else:
            sourced_percentage = 0
            verified_percentage = 0
        
        return {
            'total_claims': len(claims),
            'sourced_claims': sourced_count,
            'verified_claims': verified_count,
            'sourced_percentage': round(sourced_percentage, 1),
            'verified_percentage': round(verified_percentage, 1),
            'claims': claims[:10],  # First 10 claims
            'claim_types': Counter(claim['type'] for claim in claims),
            'statistics_quality': self._get_statistics_quality(sourced_percentage)
        }
    
    def _get_claim_context(self, text: str, claim: str, context_size: int = 100) -> str:
        """Get context around a statistical claim"""
        index = text.find(claim)
        if index == -1:
            return claim
        
        start = max(0, index - context_size)
        end = min(len(text), index + len(claim) + context_size)
        
        return text[start:end]
    
    def _get_statistics_quality(self, sourced_percentage: float) -> str:
        """Determine quality of statistical claims"""
        if sourced_percentage >= 80:
            return "Excellent - Most claims are properly sourced"
        elif sourced_percentage >= 60:
            return "Good - Majority of claims have sources"
        elif sourced_percentage >= 40:
            return "Moderate - Some claims lack sources"
        elif sourced_percentage >= 20:
            return "Weak - Most claims unsourced"
        else:
            return "Very Weak - Claims lack proper sourcing"
    
    def _analyze_media_ratio(self, text: str, images: List[str], videos: List[str]) -> Dict[str, Any]:
        """Analyze text to media ratio"""
        word_count = len(text.split())
        image_count = len(images)
        video_count = len(videos)
        total_media = image_count + video_count
        
        # Calculate ratios
        if total_media > 0:
            words_per_media = word_count / total_media
            media_density = total_media / (word_count / 1000)  # Media per 1000 words
        else:
            words_per_media = word_count
            media_density = 0
        
        # Determine if ratio is appropriate
        if word_count < 300 and total_media > 1:
            ratio_assessment = "Too many media elements for short text"
            ratio_score = 60
        elif words_per_media < 200 and total_media > 0:
            ratio_assessment = "High media density"
            ratio_score = 70
        elif words_per_media > 1000 and total_media > 0:
            ratio_assessment = "Could benefit from more visual elements"
            ratio_score = 70
        elif 300 <= words_per_media <= 700:
            ratio_assessment = "Well-balanced media distribution"
            ratio_score = 100
        else:
            ratio_assessment = "Acceptable media ratio"
            ratio_score = 85
        
        return {
            'image_count': image_count,
            'video_count': video_count,
            'total_media': total_media,
            'words_per_media': round(words_per_media, 1) if total_media > 0 else 'N/A',
            'media_density': round(media_density, 2),
            'ratio_assessment': ratio_assessment,
            'ratio_score': ratio_score,
            'has_multimedia': total_media > 0
        }
    
    def _calculate_overall_quality(self, readability: Dict, structure: Dict, 
                                  language: Dict, evidence: Dict, stats: Dict, 
                                  media: Dict) -> int:
        """Calculate overall content quality score"""
        # Weight different components
        weights = {
            'readability': 0.20,
            'structure': 0.20,
            'language': 0.20,
            'evidence': 0.25,
            'statistics': 0.10,
            'media': 0.05
        }
        
        # Calculate weighted score
        scores = {
            'readability': self._normalize_readability_score(readability['flesch_reading_ease']),
            'structure': structure['score'],
            'language': language['score'],
            'evidence': evidence['score'],
            'statistics': stats['sourced_percentage'],
            'media': media['ratio_score']
        }
        
        overall_score = sum(scores[component] * weights[component] 
                           for component in weights)
        
        return round(overall_score)
    
    def _normalize_readability_score(self, flesch_score: float) -> float:
        """Normalize Flesch score to 0-100 quality scale"""
        # Ideal Flesch score is 60-70 (standard difficulty)
        if 60 <= flesch_score <= 70:
            return 100
        elif 50 <= flesch_score < 60 or 70 < flesch_score <= 80:
            return 90
        elif 30 <= flesch_score < 50 or 80 < flesch_score <= 90:
            return 70
        else:
            return 50
    
    def _get_quality_level(self, score: int) -> str:
        """Determine overall quality level"""
        if score >= 85:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 55:
            return "Moderate"
        elif score >= 40:
            return "Fair"
        else:
            return "Poor"
    
    def _get_structure_quality_level(self, score: int) -> str:
        """Determine structure quality level"""
        if score >= 80:
            return "Well-structured"
        elif score >= 60:
            return "Good structure"
        elif score >= 40:
            return "Basic structure"
        else:
            return "Poor structure"
    
    def _generate_recommendations(self, readability: Dict, structure: Dict,
                                 language: Dict, evidence: Dict, stats: Dict) -> List[str]:
        """Generate specific recommendations for improvement"""
        recommendations = []
        
        # Readability recommendations
        if readability['flesch_reading_ease'] < 30:
            recommendations.append("Simplify complex sentences and reduce word length for better readability")
        elif readability['flesch_reading_ease'] > 90:
            recommendations.append("Consider using more sophisticated language for your target audience")
        
        if readability['avg_sentence_length'] > 25:
            recommendations.append("Break up long sentences for improved clarity")
        
        # Structure recommendations
        if not structure['has_introduction']:
            recommendations.append("Add a clear introduction to orient readers")
        if not structure['has_conclusion']:
            recommendations.append("Include a conclusion to summarize key points")
        if structure['subheading_count'] == 0 and structure['paragraph_count'] > 5:
            recommendations.append("Add subheadings to improve document structure")
        
        # Language recommendations
        if language['passive_voice_percentage'] > 30:
            recommendations.append("Reduce passive voice usage for more engaging writing")
        if language['vocabulary_diversity'] < 0.4:
            recommendations.append("Vary your word choice to improve engagement")
        if language['cliche_count'] > 2:
            recommendations.append("Replace clichés with original expressions")
        
        # Evidence recommendations
        if evidence['citation_count'] == 0:
            recommendations.append("Add citations to support claims and build credibility")
        if evidence['source_diversity'] in ['None', 'Low']:
            recommendations.append("Include diverse sources to strengthen arguments")
        
        # Statistics recommendations
        if stats['total_claims'] > 0 and stats['sourced_percentage'] < 50:
            recommendations.append("Provide sources for statistical claims")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _generate_comprehensive_summary(self, score: int, level: str, readability: Dict,
                                      structure: Dict, language: Dict, evidence: Dict,
                                      stats: Dict) -> str:
        """Generate comprehensive quality summary"""
        summary_parts = []
        
        # Overall assessment
        summary_parts.append(f"This content has {level.lower()} quality with a score of {score}/100.")
        
        # Readability insight
        summary_parts.append(f"The text has a {readability['reading_level']} reading level, "
                           f"suitable for {self._get_audience_from_reading_level(readability['flesch_kincaid_grade'])}.")
        
        # Structure insight
        if structure['structure_quality'] == "Well-structured":
            summary_parts.append("The document is well-organized with clear sections.")
        elif structure['structure_quality'] == "Poor structure":
            summary_parts.append("The document lacks clear organization.")
        
        # Evidence insight
        if evidence['quality_level'] in ['Excellent', 'Good']:
            summary_parts.append(f"Evidence quality is {evidence['quality_level'].lower()} with "
                               f"{evidence['citation_count']} citations.")
        else:
            summary_parts.append("The content would benefit from stronger evidence and citations.")
        
        # Key strength or weakness
        if score >= 70:
            if evidence['score'] >= 80:
                summary_parts.append("Key strength: Well-supported claims with diverse sources.")
            elif structure['score'] >= 80:
                summary_parts.append("Key strength: Excellent document organization.")
        else:
            if evidence['score'] < 40:
                summary_parts.append("Key weakness: Insufficient evidence to support claims.")
            elif readability['flesch_reading_ease'] < 30:
                summary_parts.append("Key weakness: Text is too complex for general audiences.")
        
        return " ".join(summary_parts)
    
    def _get_audience_from_reading_level(self, grade_level: float) -> str:
        """Convert grade level to audience description"""
        if grade_level <= 6:
            return "general audiences including children"
        elif grade_level <= 9:
            return "general adult audiences"
        elif grade_level <= 12:
            return "high school educated readers"
        elif grade_level <= 16:
            return "college-educated readers"
        else:
            return "academic or professional audiences"
