"""
FILE: services/content_analyzer.py
PURPOSE: Enhanced content quality analysis service with readability scores, evidence detection, and structure assessment
NOW WITH AI ENHANCEMENT for deeper content insights
"""

import logging
import re
import math
from typing import Dict, Any, List, Tuple, Optional
from collections import Counter
from services.base_analyzer import BaseAnalyzer
from services.ai_enhancement_mixin import AIEnhancementMixin

logger = logging.getLogger(__name__)


class ContentAnalyzer(BaseAnalyzer, AIEnhancementMixin):
    """Enhanced content quality analysis service with AI capabilities"""
    
    def __init__(self):
        super().__init__('content_analyzer')
        AIEnhancementMixin.__init__(self)
        logger.info(f"Enhanced ContentAnalyzer initialized with AI: {self._ai_available}")
        
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
    
    def _analyze_text_quality_only(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform text quality analysis only when web checks are disabled"""
        text = data.get('text', '')
        if not text:
            return self.get_error_result("Missing required field: 'text'")
        
        title = data.get('title', '')
        
        # Perform text-only analysis without any web components
        # Skip image/video analysis and structure checks that might require web access
        return self.analyze({
            **data,
            'images': [],  # Ignore images
            'videos': [],  # Ignore videos
            '_skip_structure_checks': True
        })
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze content quality using the standardized interface WITH AI ENHANCEMENT
        
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
        
        # Skip web checks if configured - PATCHED
        if self.config.options.get('skip_web_checks', False):
            # Do only text-based analysis, no structure checks
            return self._analyze_text_quality_only(data)
        
        text = data.get('text')
        if not text:
            return self.get_error_result("Missing required field: 'text'")
        
        title = data.get('title', '')
        images = data.get('images', [])
        videos = data.get('videos', [])
        
        # Perform base analysis
        result = self._analyze_content(text, title, images, videos)
        
        # AI ENHANCEMENT - Add deeper content quality insights
        if self._ai_available and text:
            logger.info("Enhancing content analysis with AI")
            
            # Get AI content quality insights
            ai_quality = self._ai_analyze_content_quality(
                text=text[:3000],  # Limit text for API
                metrics={
                    'readability_score': result['data']['readability']['flesch_reading_ease'],
                    'sentence_complexity': result['data']['readability']['avg_sentence_length'],
                    'vocabulary_diversity': result['data']['language_quality']['vocabulary_diversity'],
                    'evidence_score': result['data']['evidence_quality']['score']
                }
            )
            
            if ai_quality:
                # Add AI-detected quality issues
                if ai_quality.get('clarity_issues'):
                    for issue in ai_quality['clarity_issues'][:2]:
                        result['data']['findings'].append({
                            'type': 'warning',
                            'severity': 'medium',
                            'text': f"AI detected: {issue}",
                            'explanation': 'May impact reader comprehension'
                        })
                
                # Add AI writing insights
                if ai_quality.get('writing_strengths'):
                    for strength in ai_quality['writing_strengths'][:2]:
                        result['data']['findings'].append({
                            'type': 'positive',
                            'severity': 'positive',
                            'text': f"AI noted: {strength}",
                            'explanation': 'Enhances content quality'
                        })
                
                # Update overall quality assessment with AI insights
                if ai_quality.get('overall_assessment'):
                    result['data']['ai_assessment'] = ai_quality['overall_assessment']
                    result['metadata']['ai_enhanced'] = True
        
        return result
    
    def _analyze_content(self, text: str, title: str, images: List[str], videos: List[str]) -> Dict[str, Any]:
        """Core content analysis logic"""
        try:
            # Calculate various metrics
            readability = self._analyze_readability(text)
            language_quality = self._analyze_language_quality(text)
            structure_quality = self._analyze_structure_quality(text) if not self.config.options.get('skip_web_checks', False) else {'score': 50}
            evidence_quality = self._analyze_evidence_quality(text)
            statistical_analysis = self._analyze_statistical_claims(text)
            multimedia_quality = self._analyze_multimedia(images, videos)
            
            # Calculate overall content score
            content_score = self._calculate_content_score(
                readability, language_quality, structure_quality, 
                evidence_quality, statistical_analysis, multimedia_quality
            )
            
            # Generate findings
            findings = self._generate_findings(
                content_score, readability, language_quality, 
                structure_quality, evidence_quality, statistical_analysis
            )
            
            # Generate summary
            summary = self._generate_summary(content_score, readability, evidence_quality)
            
            return {
                'service': self.service_name,
                'success': True,
                'data': {
                    'score': content_score,
                    'level': self._get_quality_level(content_score),
                    'findings': findings,
                    'summary': summary,
                    'content_score': content_score,
                    'quality_level': self._get_quality_level(content_score),
                    'readability': readability,
                    'language_quality': language_quality,
                    'structure_quality': structure_quality,
                    'evidence_quality': evidence_quality,
                    'statistical_analysis': statistical_analysis,
                    'multimedia': multimedia_quality,
                    'word_count': len(text.split()),
                    'reading_time_minutes': readability['reading_time_minutes']
                },
                'metadata': {
                    'analysis_depth': 'comprehensive',
                    'factors_analyzed': 6,
                    'ai_enhanced': False  # Will be updated if AI is used
                }
            }
            
        except Exception as e:
            logger.error(f"Content analysis failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _analyze_readability(self, text: str) -> Dict[str, Any]:
        """Analyze text readability using multiple metrics"""
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        words = text.split()
        
        if not sentences or not words:
            return {
                'flesch_reading_ease': 0,
                'flesch_kincaid_grade': 0,
                'avg_sentence_length': 0,
                'avg_syllables_per_word': 0,
                'reading_level': 'Unknown',
                'reading_time_minutes': 0,
                'complex_word_percentage': 0
            }
        
        # Calculate metrics
        total_syllables = sum(self._count_syllables(word) for word in words)
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables_per_word = total_syllables / len(words)
        
        # Flesch Reading Ease
        flesch_score = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word
        flesch_score = max(0, min(100, flesch_score))
        
        # Flesch-Kincaid Grade Level
        fk_grade = 0.39 * avg_sentence_length + 11.8 * avg_syllables_per_word - 15.59
        fk_grade = max(0, fk_grade)
        
        # Complex words (3+ syllables)
        complex_words = sum(1 for word in words if self._count_syllables(word) >= 3)
        
        # Reading time (avg 238 words per minute)
        reading_time = len(words) / 238
        
        # Determine reading level
        if flesch_score >= 90:
            reading_level = "Very Easy (5th grade)"
        elif flesch_score >= 80:
            reading_level = "Easy (6th grade)"
        elif flesch_score >= 70:
            reading_level = "Fairly Easy (7th grade)"
        elif flesch_score >= 60:
            reading_level = "Standard (8-9th grade)"
        elif flesch_score >= 50:
            reading_level = "Fairly Difficult (10-12th grade)"
        elif flesch_score >= 30:
            reading_level = "Difficult (College)"
        else:
            reading_level = "Very Difficult (Graduate)"
        
        return {
            'flesch_reading_ease': round(flesch_score, 1),
            'flesch_kincaid_grade': round(fk_grade, 1),
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
                i > 0 and i < len(lines) - 1 and  # Not first or last line
                not lines[i-1].strip() and  # Preceded by blank line
                lines[i+1].strip()):  # Followed by content
                subheadings.append(line)
        
        return subheadings
    
    def _count_transition_words(self, text: str) -> int:
        """Count transition words that indicate logical flow"""
        transition_words = [
            'however', 'therefore', 'furthermore', 'moreover', 'consequently',
            'nevertheless', 'meanwhile', 'subsequently', 'additionally',
            'first', 'second', 'third', 'finally', 'next', 'then',
            'in conclusion', 'in summary', 'for example', 'for instance',
            'on the other hand', 'in contrast', 'similarly', 'likewise'
        ]
        
        text_lower = text.lower()
        count = 0
        
        for word in transition_words:
            count += len(re.findall(r'\b' + word + r'\b', text_lower))
        
        return count
    
    def _analyze_language_quality(self, text: str) -> Dict[str, Any]:
        """Analyze language quality and style"""
        words = text.split()
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        # Vocabulary diversity (unique words / total words)
        unique_words = set(word.lower() for word in words)
        vocabulary_diversity = len(unique_words) / len(words) if words else 0
        
        # Passive voice detection
        passive_patterns = [
            r'\b(?:is|are|was|were|been|being)\s+\w+ed\b',
            r'\b(?:is|are|was|were|been|being)\s+\w+en\b'
        ]
        passive_count = sum(len(re.findall(pattern, text, re.IGNORECASE)) 
                           for pattern in passive_patterns)
        passive_percentage = (passive_count / len(sentences)) * 100 if sentences else 0
        
        # Adverb usage (can indicate weak writing if overused)
        adverb_pattern = r'\b\w+ly\b'
        adverb_count = len(re.findall(adverb_pattern, text))
        adverb_percentage = (adverb_count / len(words)) * 100 if words else 0
        
        # Cliché detection
        cliches = [
            'at the end of the day', 'think outside the box', 'low-hanging fruit',
            'paradigm shift', 'synergy', 'circle back', 'touch base',
            'game changer', 'no-brainer', 'win-win'
        ]
        cliche_count = sum(text.lower().count(cliche) for cliche in cliches)
        
        # Calculate language quality score
        quality_score = 70  # Base score
        
        # Vocabulary diversity bonus/penalty
        if vocabulary_diversity > 0.5:
            quality_score += 10
        elif vocabulary_diversity < 0.3:
            quality_score -= 10
        
        # Passive voice penalty
        if passive_percentage > 30:
            quality_score -= 15
        elif passive_percentage < 10:
            quality_score += 5
        
        # Adverb overuse penalty
        if adverb_percentage > 5:
            quality_score -= 10
        
        # Cliché penalty
        quality_score -= (cliche_count * 2)
        
        return {
            'score': max(0, min(100, quality_score)),
            'vocabulary_diversity': round(vocabulary_diversity, 3),
            'passive_voice_percentage': round(passive_percentage, 1),
            'adverb_usage_percentage': round(adverb_percentage, 1),
            'cliche_count': cliche_count,
            'avg_word_length': round(sum(len(word) for word in words) / len(words), 1) if words else 0
        }
    
    def _analyze_evidence_quality(self, text: str) -> Dict[str, Any]:
        """Analyze the quality and quantity of evidence presented"""
        evidence_score = 0
        evidence_found = []
        
        # Check for strong evidence
        for pattern in self.evidence_indicators['strong']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                evidence_score += len(matches) * 10
                evidence_found.extend([('strong', match) for match in matches])
        
        # Check for moderate evidence
        for pattern in self.evidence_indicators['moderate']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                evidence_score += len(matches) * 5
                evidence_found.extend([('moderate', match) for match in matches])
        
        # Check for weak evidence
        for pattern in self.evidence_indicators['weak']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                evidence_score += len(matches) * 2
                evidence_found.extend([('weak', match) for match in matches])
        
        # Cap the score at 100
        evidence_score = min(100, evidence_score)
        
        # Analyze source diversity
        source_diversity = self._analyze_source_diversity(text)
        
        return {
            'score': evidence_score,
            'evidence_count': len(evidence_found),
            'strong_evidence_count': sum(1 for e in evidence_found if e[0] == 'strong'),
            'moderate_evidence_count': sum(1 for e in evidence_found if e[0] == 'moderate'),
            'weak_evidence_count': sum(1 for e in evidence_found if e[0] == 'weak'),
            'source_diversity': source_diversity,
            'evidence_quality': self._get_evidence_quality_level(evidence_score)
        }
    
    def _analyze_source_diversity(self, text: str) -> str:
        """Analyze diversity of sources cited"""
        # Look for named sources
        source_patterns = [
            r'(?:according to|said|told|reported) (\w+)',
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
            'claims': claims[:10],  # First 10 claims
            'sourced_count': sourced_count,
            'verified_count': verified_count,
            'sourced_percentage': round(sourced_percentage, 1),
            'verified_percentage': round(verified_percentage, 1)
        }
    
    def _get_claim_context(self, text: str, claim: str, context_size: int = 100) -> str:
        """Get context around a claim"""
        try:
            index = text.find(claim)
            if index == -1:
                return claim
            
            start = max(0, index - context_size)
            end = min(len(text), index + len(claim) + context_size)
            
            return text[start:end]
        except:
            return claim
    
    def _analyze_multimedia(self, images: List[str], videos: List[str]) -> Dict[str, Any]:
        """Analyze multimedia content quality"""
        multimedia_score = 50  # Base score
        
        # Images analysis
        if images:
            multimedia_score += min(20, len(images) * 5)  # Up to 20 points for images
        
        # Videos analysis
        if videos:
            multimedia_score += min(20, len(videos) * 10)  # Up to 20 points for videos
        
        # Balance check
        text_to_media_balance = "Good"
        if not images and not videos:
            text_to_media_balance = "Text only"
            multimedia_score -= 10
        elif len(images) + len(videos) > 10:
            text_to_media_balance = "Media heavy"
        
        return {
            'score': min(100, multimedia_score),
            'image_count': len(images),
            'video_count': len(videos),
            'total_media': len(images) + len(videos),
            'balance': text_to_media_balance
        }
    
    def _calculate_content_score(self, readability: Dict[str, Any], 
                               language: Dict[str, Any],
                               structure: Dict[str, Any],
                               evidence: Dict[str, Any],
                               statistics: Dict[str, Any],
                               multimedia: Dict[str, Any]) -> int:
        """Calculate overall content quality score"""
        # Weighted scoring
        weights = {
            'readability': 0.20,
            'language': 0.15,
            'structure': 0.20,
            'evidence': 0.25,
            'statistics': 0.10,
            'multimedia': 0.10
        }
        
        # Get normalized scores
        readability_score = self._normalize_readability_score(readability['flesch_reading_ease'])
        
        # Calculate weighted score
        weighted_score = (
            readability_score * weights['readability'] +
            language['score'] * weights['language'] +
            structure['score'] * weights['structure'] +
            evidence['score'] * weights['evidence'] +
            self._calculate_statistics_score(statistics) * weights['statistics'] +
            multimedia['score'] * weights['multimedia']
        )
        
        return round(weighted_score)
    
    def _normalize_readability_score(self, flesch_score: float) -> float:
        """Normalize Flesch score to 0-100 quality scale"""
        # Ideal Flesch score is 60-70 (standard reading level)
        if 60 <= flesch_score <= 70:
            return 100
        elif 50 <= flesch_score < 60 or 70 < flesch_score <= 80:
            return 85
        elif 40 <= flesch_score < 50 or 80 < flesch_score <= 90:
            return 70
        elif 30 <= flesch_score < 40 or 90 < flesch_score <= 100:
            return 55
        else:
            return 40
    
    def _calculate_statistics_score(self, statistics: Dict[str, Any]) -> float:
        """Calculate score for statistical claims quality"""
        if statistics['total_claims'] == 0:
            return 70  # Neutral score if no claims
        
        score = 40  # Base score
        
        # Bonus for sourced claims
        score += (statistics['sourced_percentage'] / 100) * 40
        
        # Bonus for verified claims
        score += (statistics['verified_percentage'] / 100) * 20
        
        return min(100, score)
    
    def _generate_findings(self, score: int, readability: Dict[str, Any],
                          language: Dict[str, Any], structure: Dict[str, Any],
                          evidence: Dict[str, Any], statistics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate findings based on analysis"""
        findings = []
        
        # Overall content quality
        if score >= 80:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': 'High-quality content with strong evidence',
                'explanation': 'Well-written and thoroughly researched'
            })
        elif score < 50:
            findings.append({
                'type': 'warning',
                'severity': 'high',
                'text': 'Content quality concerns identified',
                'explanation': 'Multiple areas need improvement'
            })
        
        # Readability findings
        if readability['flesch_reading_ease'] < 30:
            findings.append({
                'type': 'warning',
                'severity': 'medium',
                'text': 'Very difficult to read',
                'explanation': f'Reading level: {readability["reading_level"]}'
            })
        elif readability['flesch_reading_ease'] > 90:
            findings.append({
                'type': 'info',
                'severity': 'low',
                'text': 'Very simple writing style',
                'explanation': 'May lack depth or nuance'
            })
        
        # Evidence findings
        if evidence['score'] < 30:
            findings.append({
                'type': 'critical',
                'severity': 'high', 
                'text': 'Lack of credible evidence',
                'explanation': 'Few sources or citations provided'
            })
        elif evidence['strong_evidence_count'] > 3:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': 'Strong evidence base',
                'explanation': f'{evidence["strong_evidence_count"]} credible sources cited'
            })
        
        # Structure findings
        if not structure.get('has_introduction', True) or not structure.get('has_conclusion', True):
            findings.append({
                'type': 'warning',
                'severity': 'low',
                'text': 'Incomplete article structure',
                'explanation': 'Missing introduction or conclusion'
            })
        
        # Statistical claims findings
        if statistics['total_claims'] > 0 and statistics['sourced_percentage'] < 50:
            findings.append({
                'type': 'warning',
                'severity': 'medium',
                'text': 'Unsourced statistical claims',
                'explanation': f'Only {statistics["sourced_percentage"]}% of statistics are sourced'
            })
        
        return findings
    
    def _generate_summary(self, score: int, readability: Dict[str, Any], 
                         evidence: Dict[str, Any]) -> str:
        """Generate content quality summary"""
        quality_level = self._get_quality_level(score)
        
        summary = f"Content quality is {quality_level.lower()} with a score of {score}/100. "
        summary += f"The article has a {readability['reading_level'].lower()} reading level "
        summary += f"and takes approximately {readability['reading_time_minutes']} minutes to read. "
        
        if evidence['score'] >= 70:
            summary += "Evidence quality is strong with multiple credible sources."
        elif evidence['score'] >= 40:
            summary += "Evidence quality is moderate with some supporting sources."
        else:
            summary += "Evidence quality is weak with limited supporting sources."
        
        return summary
    
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
    
    def _get_structure_quality_level(self, score: int) -> str:
        """Convert structure score to quality level"""
        if score >= 80:
            return 'Well Structured'
        elif score >= 60:
            return 'Good Structure'
        elif score >= 40:
            return 'Basic Structure'
        else:
            return 'Poor Structure'
    
    def _get_evidence_quality_level(self, score: int) -> str:
        """Convert evidence score to quality level"""
        if score >= 80:
            return 'Strong Evidence'
        elif score >= 60:
            return 'Good Evidence'
        elif score >= 40:
            return 'Some Evidence'
        elif score >= 20:
            return 'Weak Evidence'
        else:
            return 'No Evidence'
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about the service"""
        info = super().get_service_info()
        info.update({
            'capabilities': [
                'Readability analysis (Flesch scores)',
                'Language quality assessment',
                'Document structure analysis',
                'Evidence quality evaluation',
                'Statistical claim verification',
                'Multimedia balance checking',
                'Reading time estimation',
                'Vocabulary diversity analysis',
                'AI-ENHANCED content insights',
                'AI-powered quality assessment'
            ],
            'metrics': {
                'readability': ['flesch_reading_ease', 'flesch_kincaid_grade'],
                'language': ['vocabulary_diversity', 'passive_voice', 'cliches'],
                'structure': ['paragraphs', 'transitions', 'headings'],
                'evidence': ['citations', 'sources', 'verification']
            },
            'ai_enhanced': self._ai_available
        })
        return info
