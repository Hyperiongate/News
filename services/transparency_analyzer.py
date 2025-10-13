"""
Transparency Analyzer - v4.0 EDUCATIONAL GUIDE
Date: October 13, 2025
Last Updated: October 13, 2025 - ALWAYS INTERESTING & VALUABLE

VISION:
✅ Always provide educational value, regardless of data
✅ Teach users what to look for in THIS type of article
✅ Context-aware guidance (breaking news vs investigation vs opinion)
✅ Actionable insights users can apply immediately

CHANGES FROM v3.0:
✅ NEW: Article type detection (breaking news, investigation, opinion, analysis)
✅ NEW: Type-specific transparency expectations
✅ NEW: Educational "what to look for" guidance
✅ NEW: "Why it matters" explanations
✅ ENHANCED: Meaningful findings even with minimal data

THE PHILOSOPHY:
Every article tells us something through what it includes AND what it omits.
Our job is to help users understand the transparency landscape of what they're reading.

Save as: services/transparency_analyzer.py (REPLACE existing file)
"""

import logging
import time
import re
from typing import Dict, Any, List, Optional, Tuple

try:
    from openai import OpenAI
    import httpx
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from services.base_analyzer import BaseAnalyzer
from config import Config

logger = logging.getLogger(__name__)


class TransparencyAnalyzer(BaseAnalyzer):
    """
    Educational transparency guide - always valuable, always interesting
    v4.0 - Teaches users what transparency means for THIS article type
    """
    
    def __init__(self):
        super().__init__('transparency_analyzer')
        
        # Initialize OpenAI if available
        self.openai_client = None
        if OPENAI_AVAILABLE and Config.OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(
                    api_key=Config.OPENAI_API_KEY,
                    timeout=httpx.Timeout(8.0, connect=2.0)
                )
                logger.info("[TransparencyGuide v4.0] OpenAI client initialized")
            except Exception as e:
                logger.warning(f"[TransparencyGuide v4.0] Failed to initialize OpenAI: {e}")
                self.openai_client = None
        
        logger.info(f"[TransparencyGuide v4.0] Initialized - Educational mode enabled")
    
    def _check_availability(self) -> bool:
        """Service is always available"""
        return True
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide educational transparency guidance
        Always valuable, regardless of article length or data
        """
        try:
            start_time = time.time()
            
            # Extract content
            text = data.get('text', '') or data.get('content', '')
            if not text:
                return self.get_error_result("No content provided for transparency analysis")
            
            # Extract metadata
            title = data.get('title', 'Unknown')
            author = data.get('author', 'Unknown')
            source = data.get('source', 'Unknown')
            url = data.get('url', '')
            word_count = len(text.split())
            
            logger.info(f"[TransparencyGuide v4.0] Analyzing {word_count} words from {source}")
            
            # STEP 1: Detect article type
            article_type, type_confidence = self._detect_article_type(title, text, word_count, source)
            logger.info(f"[TransparencyGuide] Detected type: {article_type} (confidence: {type_confidence}%)")
            
            # STEP 2: Count transparency indicators
            sources_cited = self._count_sources(text)
            quotes_included = self._count_quotes(text)
            has_methodology = self._check_methodology_disclosure(text)
            has_corrections = self._check_corrections_disclosure(text)
            author_disclosed = author not in ['Unknown', 'Unknown Author']
            has_conflict_disclosure = self._check_conflict_disclosure(text)
            
            # STEP 3: Get type-specific expectations
            expectations = self._get_type_expectations(article_type, word_count)
            
            # STEP 4: Calculate contextual score
            transparency_score = self._calculate_contextual_score(
                article_type=article_type,
                word_count=word_count,
                sources_cited=sources_cited,
                quotes_included=quotes_included,
                has_methodology=has_methodology,
                author_disclosed=author_disclosed,
                expectations=expectations
            )
            
            transparency_level = self._get_transparency_level(transparency_score)
            
            # STEP 5: Generate educational findings
            findings = self._generate_educational_findings(
                article_type=article_type,
                word_count=word_count,
                sources_cited=sources_cited,
                quotes_included=quotes_included,
                has_methodology=has_methodology,
                author_disclosed=author_disclosed,
                expectations=expectations
            )
            
            # STEP 6: Generate "What to Look For" guide
            what_to_look_for = self._generate_what_to_look_for(article_type, expectations)
            
            # STEP 7: Generate educational analysis
            analysis = self._generate_educational_analysis(
                article_type=article_type,
                transparency_score=transparency_score,
                sources_cited=sources_cited,
                word_count=word_count,
                expectations=expectations,
                author_disclosed=author_disclosed
            )
            
            # STEP 8: Generate conversational summary
            summary = self._generate_educational_summary(
                article_type, transparency_score, sources_cited, word_count
            )
            
            # STEP 9: Transparency lessons
            lessons = self._generate_transparency_lessons(article_type, findings)
            
            # Build result
            result = {
                'service': self.service_name,
                'success': True,
                'available': True,
                'timestamp': time.time(),
                'analysis_complete': True,
                
                # Core scores
                'score': transparency_score,
                'transparency_score': transparency_score,
                'level': transparency_level,
                'transparency_level': transparency_level,
                
                # Educational content
                'article_type': article_type,
                'type_confidence': type_confidence,
                'what_to_look_for': what_to_look_for,
                'transparency_lessons': lessons,
                'expectations': expectations,
                
                # Detailed findings
                'findings': findings,
                'analysis': analysis,
                'summary': summary,
                
                # Metrics
                'sources_cited': sources_cited,
                'source_count': sources_cited,
                'quotes_included': quotes_included,
                'quote_count': quotes_included,
                'has_methodology': has_methodology,
                'has_corrections_policy': has_corrections,
                'author_disclosed': author_disclosed,
                'has_conflict_disclosure': has_conflict_disclosure,
                'word_count': word_count,
                
                # Chart data
                'chart_data': {
                    'type': 'bar',
                    'data': {
                        'labels': ['Sources', 'Quotes', 'Methodology', 'Author ID', 'Corrections'],
                        'datasets': [{
                            'label': 'Transparency Indicators',
                            'data': [
                                min(sources_cited * 20, 100),
                                min(quotes_included * 15, 100),
                                100 if has_methodology else 0,
                                100 if author_disclosed else 0,
                                100 if has_corrections else 0
                            ],
                            'backgroundColor': '#8b5cf6'
                        }]
                    }
                },
                
                'metadata': {
                    'analysis_time': time.time() - start_time,
                    'text_length': len(text),
                    'article_title': title,
                    'version': '4.0.0',
                    'educational_mode': True
                }
            }
            
            logger.info(f"[TransparencyGuide v4.0] Complete: {transparency_score}/100 ({article_type})")
            return self.get_success_result(result)
            
        except Exception as e:
            logger.error(f"[TransparencyGuide v4.0] Error: {e}", exc_info=True)
            return self.get_error_result(f"Transparency analysis error: {str(e)}")
    
    def _detect_article_type(self, title: str, text: str, word_count: int, source: str) -> Tuple[str, int]:
        """
        Detect article type to set appropriate expectations
        Returns: (type, confidence_percentage)
        """
        
        title_lower = title.lower()
        text_lower = text.lower()
        
        # Breaking News (short, time-sensitive)
        if word_count < 300:
            breaking_indicators = ['breaking', 'just in', 'developing', 'update', 'report', 'according to']
            breaking_score = sum(10 for indicator in breaking_indicators if indicator in title_lower or indicator in text_lower[:200])
            if breaking_score >= 20:
                return 'Breaking News', min(90, 60 + breaking_score)
        
        # Investigation (long, detailed, methodology)
        if word_count > 1500:
            investigation_indicators = ['investigation', 'documents show', 'obtained by', 'reviewed', 'interviewed', 'months-long', 'exclusive']
            investigation_score = sum(15 for indicator in investigation_indicators if indicator in text_lower)
            if investigation_score >= 30:
                return 'Investigation', min(95, 65 + investigation_score)
        
        # Opinion/Editorial (first person, subjective)
        opinion_indicators = ['opinion', 'editorial', 'commentary', 'i believe', 'in my view', 'i think', 'we must', 'we should']
        opinion_score = sum(12 for indicator in opinion_indicators if indicator in title_lower or indicator in text_lower[:500])
        if opinion_score >= 24 or 'opinion' in title_lower:
            return 'Opinion/Editorial', min(90, 60 + opinion_score)
        
        # Analysis (explains trends, context, "what it means")
        analysis_indicators = ['analysis', 'explained', 'what to know', 'context', 'why', 'how', 'means for']
        analysis_score = sum(10 for indicator in analysis_indicators if indicator in title_lower)
        if analysis_score >= 20:
            return 'Analysis', min(85, 55 + analysis_score)
        
        # Feature/Profile (human interest, storytelling)
        if word_count > 800:
            feature_indicators = ['profile', 'inside', 'the story of', 'journey', 'life of', 'day in']
            feature_score = sum(12 for indicator in feature_indicators if indicator in title_lower)
            if feature_score >= 24:
                return 'Feature', min(85, 55 + feature_score)
        
        # Default: Standard News Report
        return 'News Report', 70
    
    def _get_type_expectations(self, article_type: str, word_count: int) -> Dict[str, Any]:
        """
        Get transparency expectations based on article type
        This is what makes the analysis contextual and educational
        """
        
        if article_type == 'Breaking News':
            return {
                'sources_expected': '1-3 (speed prioritized)',
                'quotes_expected': '0-2 (often sparse)',
                'methodology_expected': False,
                'author_expected': 'Sometimes omitted',
                'priority': 'Speed over detail',
                'what_matters_most': 'Source of initial report, verification status',
                'typical_gaps': 'Limited context, single source, unverified claims',
                'follow_up': 'Expect more detailed coverage as story develops',
                'scoring_adjustment': 'Lenient - judged on speed vs accuracy'
            }
        
        elif article_type == 'Investigation':
            return {
                'sources_expected': '10+ (extensive)',
                'quotes_expected': '5+ (diverse voices)',
                'methodology_expected': True,
                'author_expected': 'Required (accountability)',
                'priority': 'Depth and verification',
                'what_matters_most': 'Methodology disclosure, document trail, multiple independent sources',
                'typical_gaps': 'Should have minimal gaps - red flag if sources unclear',
                'follow_up': 'Often stands alone as definitive report',
                'scoring_adjustment': 'Strict - high standards expected'
            }
        
        elif article_type == 'Opinion/Editorial':
            return {
                'sources_expected': '2-5 (supporting arguments)',
                'quotes_expected': '1-3 (authority references)',
                'methodology_expected': False,
                'author_expected': 'Required (opinion ownership)',
                'priority': 'Author credentials and logic',
                'what_matters_most': 'Author expertise, acknowledgment of counterarguments',
                'typical_gaps': 'May omit opposing views, selective sourcing',
                'follow_up': 'One perspective - seek diverse opinions',
                'scoring_adjustment': 'Focus on author disclosure, not source count'
            }
        
        elif article_type == 'Analysis':
            return {
                'sources_expected': '3-7 (context providers)',
                'quotes_expected': '2-4 (expert perspectives)',
                'methodology_expected': 'Helpful but not required',
                'author_expected': 'Preferred (expertise matters)',
                'priority': 'Context and interpretation',
                'what_matters_most': 'Author credentials, diverse perspectives, clear reasoning',
                'typical_gaps': 'May lack opposing interpretations',
                'follow_up': 'Compare with other analyses',
                'scoring_adjustment': 'Moderate - balance depth with accessibility'
            }
        
        elif article_type == 'Feature':
            return {
                'sources_expected': '3-8 (storytelling)',
                'quotes_expected': '5+ (narrative building)',
                'methodology_expected': 'Implicit in reporting',
                'author_expected': 'Usually disclosed',
                'priority': 'Story and human interest',
                'what_matters_most': 'Access to subjects, time spent reporting',
                'typical_gaps': 'May focus on one narrative thread',
                'follow_up': 'Provides human context to news events',
                'scoring_adjustment': 'Moderate - quality of access matters'
            }
        
        else:  # Standard News Report
            return {
                'sources_expected': '3-5 (standard practice)',
                'quotes_expected': '2-4 (multiple perspectives)',
                'methodology_expected': 'For data/studies',
                'author_expected': 'Standard practice',
                'priority': 'Accuracy and balance',
                'what_matters_most': 'Multiple sources, clear attribution, balance',
                'typical_gaps': 'Watch for single-source stories, unnamed sources',
                'follow_up': 'Should provide foundation for understanding event',
                'scoring_adjustment': 'Standard - normal journalistic expectations'
            }
    
    def _calculate_contextual_score(self, article_type: str, word_count: int,
                                   sources_cited: int, quotes_included: int,
                                   has_methodology: bool, author_disclosed: bool,
                                   expectations: Dict) -> int:
        """
        Calculate score based on article type expectations
        A breaking news brief with 3 sources could score 70+
        An investigation with 3 sources would score 40-
        """
        
        score = 50  # Start neutral
        
        if article_type == 'Breaking News':
            # Be lenient - speed matters
            if sources_cited >= 1:
                score += 25  # Any source is good
            if sources_cited >= 2:
                score += 15  # Multiple sources excellent
            if quotes_included >= 1:
                score += 10
            # Don't penalize missing methodology or corrections in breaking news
            
        elif article_type == 'Investigation':
            # Be strict - thoroughness expected
            score += min(sources_cited * 3, 35)  # Need many sources
            if has_methodology:
                score += 20  # Methodology crucial
            else:
                score -= 15  # Missing methodology is a problem
            if author_disclosed:
                score += 10  # Accountability matters
            if quotes_included >= 5:
                score += 10
            
        elif article_type in ['Opinion/Editorial', 'Analysis']:
            # Focus on author disclosure
            if author_disclosed:
                score += 25  # Author identity crucial
            else:
                score -= 20  # Anonymous opinion is problematic
            if sources_cited >= 2:
                score += 20  # Some sourcing expected
            
        else:  # Standard news or feature
            # Balanced approach
            score += min(sources_cited * 5, 25)
            score += min(quotes_included * 4, 16)
            if author_disclosed:
                score += 12
            if has_methodology and word_count > 500:
                score += 12
        
        # Word count adjustments
        if word_count < 300 and sources_cited >= 2:
            score += 10  # Bonus for good sourcing in brief
        
        return int(max(0, min(100, score)))
    
    def _generate_educational_findings(self, article_type: str, word_count: int,
                                      sources_cited: int, quotes_included: int,
                                      has_methodology: bool, author_disclosed: bool,
                                      expectations: Dict) -> List[Dict[str, Any]]:
        """
        Generate findings that TEACH users what to look for
        """
        
        findings = []
        
        # Context-setting finding
        findings.append({
            'type': 'info',
            'severity': 'info',
            'icon': '📰',
            'text': f'Article Type: {article_type}',
            'explanation': f"This is a {article_type.lower()}. {expectations['priority']} is the priority for this format."
        })
        
        # Source analysis with context
        if article_type == 'Breaking News':
            if sources_cited >= 2:
                findings.append({
                    'type': 'positive',
                    'severity': 'positive',
                    'icon': '✓',
                    'text': f'{sources_cited} sources cited - Good for breaking news',
                    'explanation': 'Breaking news often relies on 1-2 initial sources. Multiple sources suggest verification efforts.'
                })
            elif sources_cited == 1:
                findings.append({
                    'type': 'info',
                    'severity': 'info',
                    'icon': 'ℹ️',
                    'text': 'Single source - Common in breaking news',
                    'explanation': 'Breaking stories often start with one source. Verify by checking multiple outlets and waiting for updates.'
                })
            else:
                findings.append({
                    'type': 'warning',
                    'severity': 'medium',
                    'icon': '⚠️',
                    'text': 'No clear sources cited',
                    'explanation': 'Even breaking news should indicate source (e.g., "according to reports"). Unclear origin is a red flag.'
                })
        else:
            # Standard sourcing analysis
            if sources_cited >= 5:
                findings.append({
                    'type': 'positive',
                    'severity': 'positive',
                    'icon': '✓',
                    'text': f'Well-sourced: {sources_cited} sources cited',
                    'explanation': 'Multiple sources allow for verification and diverse perspectives.'
                })
            elif sources_cited >= 2:
                findings.append({
                    'type': 'neutral',
                    'severity': 'info',
                    'icon': '○',
                    'text': f'{sources_cited} sources cited - Adequate',
                    'explanation': 'Minimum sourcing present. More sources would strengthen credibility.'
                })
            else:
                findings.append({
                    'type': 'warning',
                    'severity': 'medium',
                    'icon': '⚠️',
                    'text': 'Limited sourcing',
                    'explanation': 'Single-source stories are harder to verify. Look for corroboration from other outlets.'
                })
        
        # Author disclosure
        if article_type in ['Opinion/Editorial', 'Analysis']:
            if author_disclosed:
                findings.append({
                    'type': 'positive',
                    'severity': 'positive',
                    'icon': '✓',
                    'text': 'Author identified - Critical for opinion/analysis',
                    'explanation': "Opinions and analysis should always be attributed. Author's expertise and potential biases matter."
                })
            else:
                findings.append({
                    'type': 'warning',
                    'severity': 'high',
                    'icon': '⚠️',
                    'text': 'Anonymous opinion/analysis - Red flag',
                    'explanation': 'Opinion pieces without author attribution lack accountability. Who is making these claims?'
                })
        else:
            if not author_disclosed:
                findings.append({
                    'type': 'info',
                    'severity': 'info',
                    'icon': 'ℹ️',
                    'text': 'Author not identified',
                    'explanation': f"Some outlets don't byline {article_type.lower()}s. Reduces accountability but common in breaking news."
                })
        
        # Methodology (for investigations and data stories)
        if article_type == 'Investigation':
            if has_methodology:
                findings.append({
                    'type': 'positive',
                    'severity': 'positive',
                    'icon': '✓',
                    'text': 'Methodology disclosed',
                    'explanation': 'Investigations should explain how evidence was gathered. Transparency about methods builds trust.'
                })
            else:
                findings.append({
                    'type': 'warning',
                    'severity': 'medium',
                    'icon': '⚠️',
                    'text': 'Methodology unclear',
                    'explanation': 'Investigative pieces should explain their reporting process. How did they get this information?'
                })
        
        # Educational "what this means" finding
        findings.append({
            'type': 'education',
            'severity': 'info',
            'icon': '💡',
            'text': 'What to verify',
            'explanation': expectations['what_matters_most']
        })
        
        return findings
    
    def _generate_what_to_look_for(self, article_type: str, expectations: Dict) -> List[str]:
        """
        Generate specific guidance: "Here's what to look for in this type of article"
        """
        
        guidance = [
            f"📋 **Article Type**: {article_type}",
            f"🎯 **Priority**: {expectations['priority']}",
            "",
            "**What to Look For:**"
        ]
        
        if article_type == 'Breaking News':
            guidance.extend([
                "• Where did this information come from? (Look for 'according to...')",
                "• Is this a single source or multiple sources?",
                "• Does the outlet indicate verification status?",
                "• What's NOT known yet? (Good reporting acknowledges gaps)",
                "• Check other outlets - do they confirm this report?",
                "",
                "**Red Flags:**",
                "• No source attribution at all",
                "• Definitive claims in developing situations",
                "• No acknowledgment of what's still unclear"
            ])
        
        elif article_type == 'Investigation':
            guidance.extend([
                "• How was this information obtained? (FOIA, interviews, documents?)",
                "• How many independent sources verified key claims?",
                "• Are documents/evidence linked or described?",
                "• Did reporters give subjects a chance to respond?",
                "• How long did the investigation take?",
                "",
                "**Red Flags:**",
                "• Unclear methodology or sourcing",
                "• Single-source investigation",
                "• No response from accused parties",
                "• No documentation trail"
            ])
        
        elif article_type == 'Opinion/Editorial':
            guidance.extend([
                "• Who is the author? What's their expertise?",
                "• Are claims backed by evidence or sources?",
                "• Does it acknowledge counterarguments?",
                "• Is the author transparent about potential biases?",
                "• Does it separate facts from opinions?",
                "",
                "**Red Flags:**",
                "• Anonymous opinion pieces",
                "• Cherry-picked data without context",
                "• Strawman arguments (misrepresenting other views)",
                "• No acknowledgment of complexity or limitations"
            ])
        
        elif article_type == 'Analysis':
            guidance.extend([
                "• What expertise does the analyst bring?",
                "• Are multiple perspectives considered?",
                "• Is reasoning clearly explained?",
                "• Are predictions/interpretations clearly labeled as such?",
                "• Are alternative explanations acknowledged?",
                "",
                "**Red Flags:**",
                "• Analysis presented as fact",
                "• One-sided interpretation of events",
                "• No consideration of alternative views",
                "• Expertise not established"
            ])
        
        else:  # Standard news
            guidance.extend([
                "• Are multiple sources quoted?",
                "• Do sources have direct knowledge?",
                "• Are sources named (not all anonymous)?",
                "• Are different perspectives included?",
                "• Is author identified?",
                "",
                "**Red Flags:**",
                "• All unnamed sources",
                "• Only one side of story presented",
                "• Vague attribution ('sources say')",
                "• No official on-record sources"
            ])
        
        guidance.extend([
            "",
            f"**Remember**: {expectations['follow_up']}"
        ])
        
        return guidance
    
    def _generate_transparency_lessons(self, article_type: str, findings: List[Dict]) -> List[str]:
        """
        Generate 2-3 key lessons users can apply to future articles
        """
        
        lessons = []
        
        if article_type == 'Breaking News':
            lessons = [
                "Breaking news trades detail for speed - verify across multiple sources",
                "Look for updates: breaking stories gain context and sourcing over time",
                "The first report is often incomplete - note what's still unknown"
            ]
        elif article_type == 'Investigation':
            lessons = [
                "Investigations should show their work - methodology matters",
                "Look for document trails and multiple independent sources",
                "Best investigations allow subjects to respond before publication"
            ]
        elif article_type == 'Opinion/Editorial':
            lessons = [
                "Opinions should be clearly labeled and attributed to a named author",
                "Good opinion writing acknowledges counterarguments",
                "Check if author has relevant expertise or potential conflicts"
            ]
        else:
            lessons = [
                "Multiple sources with direct knowledge strengthen credibility",
                "Named sources are more accountable than anonymous ones",
                "Balanced reporting presents multiple perspectives fairly"
            ]
        
        return lessons
    
    def _generate_educational_analysis(self, article_type: str, transparency_score: int,
                                      sources_cited: int, word_count: int,
                                      expectations: Dict, author_disclosed: bool) -> Dict[str, str]:
        """
        Generate analysis that TEACHES, not just reports
        """
        
        what_we_looked = (
            f"We analyzed this {article_type.lower()} ({word_count} words) for transparency indicators. "
            f"For this article type, we expect: {expectations['sources_expected']} sources, "
            f"{expectations['quotes_expected']} quotes, and "
            f"{'methodology disclosure' if expectations['methodology_expected'] else 'standard attribution'}."
        )
        
        # Context-aware findings
        if article_type == 'Breaking News' and sources_cited >= 1:
            what_we_found = (
                f"This breaking news brief cites {sources_cited} source(s). "
                f"For a {word_count}-word breaking story, this is {'adequate' if sources_cited >= 2 else 'typical'}. "
                f"{'Author identified. ' if author_disclosed else 'Author not disclosed (common in breaking news). '}"
                f"{expectations['typical_gaps']}"
            )
        elif article_type == 'Investigation':
            what_we_found = (
                f"This investigation cites {sources_cited} source(s). "
                f"Investigative pieces typically need 10+ sources. "
                f"{'Methodology disclosed - good.' if expectations.get('has_methodology') else 'Methodology unclear - problematic for investigations.'} "
                f"Author {'identified (accountability)' if author_disclosed else 'not identified (reduces accountability)'}."
            )
        else:
            what_we_found = (
                f"Found {sources_cited} source citations, {'author identified' if author_disclosed else 'author not disclosed'}. "
                f"For a {article_type.lower()}, {expectations['what_matters_most'].lower()}."
            )
        
        # Scoring context
        if transparency_score >= 70:
            what_it_means = (
                f"Transparency score: {transparency_score}/100. "
                f"This {article_type.lower()} meets good transparency standards for its format. "
                f"{expectations['what_matters_most']} {expectations['follow_up']}"
            )
        elif transparency_score >= 50:
            what_it_means = (
                f"Transparency score: {transparency_score}/100. "
                f"This {article_type.lower()} has moderate transparency. "
                f"Could be improved by: {expectations['typical_gaps'].lower()} "
                f"{expectations['follow_up']}"
            )
        else:
            what_it_means = (
                f"Transparency score: {transparency_score}/100. "
                f"This {article_type.lower()} has limited transparency. "
                f"Key concerns: {expectations['typical_gaps'].lower()} "
                f"Recommendation: {expectations['follow_up'].lower()}"
            )
        
        return {
            'what_we_looked': what_we_looked,
            'what_we_found': what_we_found,
            'what_it_means': what_it_means
        }
    
    def _generate_educational_summary(self, article_type: str, transparency_score: int,
                                     sources_cited: int, word_count: int) -> str:
        """
        Generate a conversational summary that provides context
        """
        
        type_context = {
            'Breaking News': 'Breaking news brief - speed prioritized over detail',
            'Investigation': 'In-depth investigation - high transparency standards expected',
            'Opinion/Editorial': 'Opinion piece - author disclosure crucial',
            'Analysis': 'News analysis - context and expertise matter',
            'Feature': 'Feature story - narrative and access important',
            'News Report': 'Standard news report - balanced sourcing expected'
        }
        
        context = type_context.get(article_type, 'News article')
        
        if transparency_score >= 70:
            return f"{context}. Transparency score: {transparency_score}/100. Good disclosure for this format. {sources_cited} sources cited in {word_count} words."
        elif transparency_score >= 50:
            return f"{context}. Transparency score: {transparency_score}/100. Adequate but could be more transparent. {sources_cited} sources cited in {word_count} words."
        else:
            return f"{context}. Transparency score: {transparency_score}/100. Limited transparency - verify claims independently. {sources_cited} sources cited in {word_count} words."
    
    def _count_sources(self, text: str) -> int:
        """Count explicit source citations"""
        source_patterns = [
            r'according to\s+[A-Z]',
            r'[A-Z][a-z]+\s+(?:said|told|stated|confirmed)',
            r'(?:study|report|survey|research)\s+(?:by|from|published)',
            r'cited by',
            r'reported by',
            r'data from',
            r'source:\s*[A-Z]'
        ]
        
        count = 0
        for pattern in source_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            count += len(matches)
        
        return min(count, 25)
    
    def _count_quotes(self, text: str) -> int:
        """Count direct quotes"""
        quotes = re.findall(r'"[^"]{10,}"', text)
        return len(quotes)
    
    def _check_methodology_disclosure(self, text: str) -> bool:
        """Check if article discloses methodology"""
        methodology_indicators = [
            r'methodology',
            r'methods?\s+(?:used|employed|applied)',
            r'data\s+(?:was|were)\s+(?:collected|gathered|obtained)',
            r'sample\s+size',
            r'participants?\s+(?:were|was)\s+(?:selected|recruited)',
            r'survey\s+(?:was\s+)?conducted',
            r'interviewed?\s+\d+',
            r'analyzed?\s+\d+\s+(?:cases|responses|participants)'
        ]
        
        text_lower = text.lower()
        for indicator in methodology_indicators:
            if re.search(indicator, text_lower):
                return True
        
        return False
    
    def _check_corrections_disclosure(self, text: str) -> bool:
        """Check for corrections or updates disclosure"""
        corrections_indicators = [
            r'(?:updated?|corrected?|amended?)[\s:]+',
            r'editor\'?s?\s+note',
            r'correction[:|\s]',
            r'this\s+(?:article|story)\s+(?:was|has\s+been)\s+(?:updated|corrected)',
            r'originally\s+(?:published|stated)',
            r'clarification[:|\s]'
        ]
        
        text_lower = text.lower()
        for indicator in corrections_indicators:
            if re.search(indicator, text_lower):
                return True
        
        return False
    
    def _check_conflict_disclosure(self, text: str) -> bool:
        """Check for conflict of interest disclosure"""
        conflict_indicators = [
            r'conflict\s+of\s+interest',
            r'disclosure[:|\s]',
            r'(?:financial|funding)\s+(?:relationship|interest|support)',
            r'sponsored\s+by',
            r'funded\s+by',
            r'the\s+author[s]?\s+(?:work|worked|is\s+employed)\s+(?:for|at|with)'
        ]
        
        text_lower = text.lower()
        for indicator in conflict_indicators:
            if re.search(indicator, text_lower):
                return True
        
        return False
    
    def _get_transparency_level(self, score: int) -> str:
        """Convert score to level"""
        if score >= 80: return 'Highly Transparent'
        elif score >= 60: return 'Transparent'
        elif score >= 40: return 'Moderately Transparent'
        else: return 'Limited Transparency'


logger.info("[TransparencyGuide v4.0] ✓ Educational mode - Always valuable!")
