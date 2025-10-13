"""
Transparency Analyzer - v3.0 COMPLETE IMPLEMENTATION
Date: October 12, 2025
Last Updated: October 12, 2025 - FIXED ABSTRACT METHOD ERROR

FIXES IN v3.0:
✅ CRITICAL: Implemented missing _check_availability() method (was causing abstract class error)
✅ ENHANCED: Full transparency analysis with source attribution, corrections policy, methodology
✅ ENHANCED: AI-powered analysis when OpenAI available
✅ PRESERVED: All existing functionality, added proper implementation

THE BUG WE FIXED:
- Error: "Can't instantiate abstract class TransparencyAnalyzer with abstract method _check_availability"
- Service was defined but not properly implemented
- Missing required method from BaseAnalyzer

THE SOLUTION:
- Implemented _check_availability() method
- Complete transparency scoring based on citations, sources, author disclosure
- Proper service structure that matches other working services

Save as: services/transparency_analyzer.py (REPLACE existing file)
"""

import logging
import time
import re
from typing import Dict, Any, List, Optional

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
    Analyzes article transparency: sources, citations, methodology, corrections
    v3.0 - Fully implemented with _check_availability()
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
                logger.info("[TransparencyAnalyzer v3.0] OpenAI client initialized")
            except Exception as e:
                logger.warning(f"[TransparencyAnalyzer v3.0] Failed to initialize OpenAI: {e}")
                self.openai_client = None
        
        logger.info(f"[TransparencyAnalyzer v3.0] Initialized - AI: {bool(self.openai_client)}")
    
    def _check_availability(self) -> bool:
        """
        CRITICAL FIX v3.0: Implement required abstract method
        Service is always available (runs with or without AI)
        """
        return True
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze article transparency
        Checks: source attribution, citations, methodology disclosure, corrections policy
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
            
            logger.info(f"[TransparencyAnalyzer v3.0] Analyzing {len(text)} chars from {source}")
            
            # 1. Count and analyze sources cited
            sources_cited = self._count_sources(text)
            quotes_included = self._count_quotes(text)
            
            # 2. Check for methodology disclosure
            has_methodology = self._check_methodology_disclosure(text)
            
            # 3. Check for corrections/updates disclosure
            has_corrections = self._check_corrections_disclosure(text)
            
            # 4. Check author transparency
            author_transparency = self._check_author_transparency(author, text)
            
            # 5. Check for conflicts of interest disclosure
            has_conflict_disclosure = self._check_conflict_disclosure(text)
            
            # 6. Analyze citation quality
            citation_quality = self._analyze_citation_quality(text, sources_cited)
            
            # 7. AI enhancement if available
            ai_insights = None
            if self.openai_client:
                ai_insights = self._get_ai_transparency_analysis(text[:2000], source)
            
            # Calculate transparency score
            transparency_score = self._calculate_transparency_score(
                sources_cited=sources_cited,
                quotes_included=quotes_included,
                has_methodology=has_methodology,
                has_corrections=has_corrections,
                author_transparency=author_transparency,
                has_conflict_disclosure=has_conflict_disclosure,
                citation_quality=citation_quality,
                ai_insights=ai_insights
            )
            
            transparency_level = self._get_transparency_level(transparency_score)
            
            # Generate findings
            findings = self._generate_findings(
                sources_cited, quotes_included, has_methodology, 
                has_corrections, author_transparency, citation_quality
            )
            
            # Generate analysis
            analysis = self._generate_analysis(
                transparency_score, sources_cited, quotes_included, 
                has_methodology, has_corrections, citation_quality
            )
            
            # Generate summary
            summary = self._generate_summary(transparency_score, sources_cited, findings)
            
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
                
                # Detailed findings
                'findings': findings,
                'analysis': analysis,
                'summary': summary,
                
                # Metrics
                'sources_cited': sources_cited,
                'source_count': sources_cited,
                'quotes_included': quotes_included,
                'quote_count': quotes_included,
                'quotes_used': quotes_included,
                'has_methodology': has_methodology,
                'has_corrections_policy': has_corrections,
                'author_transparency': author_transparency,
                'has_conflict_disclosure': has_conflict_disclosure,
                'citation_quality': citation_quality,
                
                # Chart data
                'chart_data': {
                    'type': 'bar',
                    'data': {
                        'labels': ['Sources Cited', 'Quotes Used', 'Methodology', 'Corrections', 'Author Info'],
                        'datasets': [{
                            'label': 'Transparency Indicators',
                            'data': [
                                min(sources_cited * 10, 100),
                                min(quotes_included * 15, 100),
                                100 if has_methodology else 0,
                                100 if has_corrections else 0,
                                100 if author_transparency else 0
                            ],
                            'backgroundColor': '#8b5cf6'
                        }]
                    }
                },
                
                # Details
                'details': {
                    'sources_cited': sources_cited,
                    'quotes_included': quotes_included,
                    'methodology_disclosed': has_methodology,
                    'corrections_policy': has_corrections,
                    'author_identified': author_transparency,
                    'conflict_disclosure': has_conflict_disclosure,
                    'citation_quality_score': citation_quality
                },
                
                'metadata': {
                    'analysis_time': time.time() - start_time,
                    'text_length': len(text),
                    'article_title': title,
                    'version': '3.0.0',
                    'ai_enhanced': bool(self.openai_client and ai_insights)
                }
            }
            
            logger.info(f"[TransparencyAnalyzer v3.0] Complete: {transparency_score}/100 ({transparency_level})")
            return self.get_success_result(result)
            
        except Exception as e:
            logger.error(f"[TransparencyAnalyzer v3.0] Error: {e}", exc_info=True)
            return self.get_error_result(f"Transparency analysis error: {str(e)}")
    
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
        
        return min(count, 20)  # Cap at 20 to avoid over-counting
    
    def _count_quotes(self, text: str) -> int:
        """Count direct quotes"""
        # Find quoted text (at least 10 chars between quotes)
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
    
    def _check_author_transparency(self, author: str, text: str) -> bool:
        """Check if author is clearly identified"""
        
        if not author or author in ['Unknown', 'Unknown Author']:
            return False
        
        # Check if author appears in text
        if author.lower() in text.lower()[:500]:
            return True
        
        return True  # If we have an author name, consider it transparent
    
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
    
    def _analyze_citation_quality(self, text: str, sources_cited: int) -> int:
        """Analyze quality of citations (0-100)"""
        
        if sources_cited == 0:
            return 0
        
        score = 50  # Base score
        
        # Check for specific citations
        if re.search(r'(?:study|report|paper)\s+published\s+in', text, re.IGNORECASE):
            score += 15
        
        # Check for links/URLs
        if re.search(r'https?://', text):
            score += 10
        
        # Check for dates
        if re.search(r'(?:in|on|dated)\s+\d{4}', text):
            score += 10
        
        # Check for specific names
        if re.search(r'[A-Z][a-z]+\s+[A-Z][a-z]+\s+(?:said|told|wrote)', text):
            score += 15
        
        return min(score, 100)
    
    def _get_ai_transparency_analysis(self, text: str, source: str) -> Optional[Dict[str, Any]]:
        """Use AI to analyze transparency"""
        
        if not self.openai_client:
            return None
        
        try:
            prompt = f"""Analyze the transparency of this article excerpt from {source}:

{text}

Evaluate:
1. Are sources clearly identified?
2. Is methodology explained (for data/studies)?
3. Are potential biases or conflicts disclosed?
4. Are claims properly attributed?

Respond with:
TRANSPARENCY: [0-100 score]
STRENGTHS: [2-3 transparency strengths]
WEAKNESSES: [2-3 transparency weaknesses]"""
            
            response = self.openai_client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {"role": "system", "content": "You analyze journalistic transparency."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            
            # Parse response
            ai_score = 50
            strengths = []
            weaknesses = []
            
            for line in content.split('\n'):
                if line.startswith('TRANSPARENCY:'):
                    score_match = re.search(r'\d+', line)
                    if score_match:
                        ai_score = int(score_match.group())
                elif line.startswith('STRENGTHS:'):
                    strengths_text = line.replace('STRENGTHS:', '').strip()
                    strengths = [s.strip() for s in strengths_text.split(',') if s.strip()]
                elif line.startswith('WEAKNESSES:'):
                    weaknesses_text = line.replace('WEAKNESSES:', '').strip()
                    weaknesses = [w.strip() for w in weaknesses_text.split(',') if w.strip()]
            
            return {
                'score': ai_score,
                'strengths': strengths,
                'weaknesses': weaknesses
            }
            
        except Exception as e:
            logger.error(f"[TransparencyAnalyzer v3.0] AI analysis failed: {e}")
            return None
    
    def _calculate_transparency_score(self, sources_cited: int, quotes_included: int,
                                     has_methodology: bool, has_corrections: bool,
                                     author_transparency: bool, has_conflict_disclosure: bool,
                                     citation_quality: int, ai_insights: Optional[Dict]) -> int:
        """Calculate overall transparency score"""
        
        score = 0
        
        # Sources cited (up to 30 points)
        score += min(sources_cited * 3, 30)
        
        # Quotes included (up to 20 points)
        score += min(quotes_included * 2, 20)
        
        # Methodology disclosure (15 points)
        if has_methodology:
            score += 15
        
        # Corrections policy (10 points)
        if has_corrections:
            score += 10
        
        # Author transparency (10 points)
        if author_transparency:
            score += 10
        
        # Conflict disclosure (5 points)
        if has_conflict_disclosure:
            score += 5
        
        # Citation quality (up to 10 points)
        score += int(citation_quality * 0.1)
        
        # AI insights (adjust by up to ±10)
        if ai_insights:
            ai_adjustment = (ai_insights['score'] - 50) * 0.2
            score += int(ai_adjustment)
        
        return int(max(0, min(100, score)))
    
    def _get_transparency_level(self, score: int) -> str:
        """Convert score to level"""
        if score >= 80: return 'Highly Transparent'
        elif score >= 60: return 'Transparent'
        elif score >= 40: return 'Moderately Transparent'
        else: return 'Limited Transparency'
    
    def _generate_findings(self, sources_cited: int, quotes_included: int,
                          has_methodology: bool, has_corrections: bool,
                          author_transparency: bool, citation_quality: int) -> List[Dict[str, Any]]:
        """Generate detailed findings"""
        
        findings = []
        
        # Sources
        if sources_cited >= 5:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': f'Well-sourced: {sources_cited} sources cited',
                'explanation': 'Article provides adequate source attribution for verification'
            })
        elif sources_cited == 0:
            findings.append({
                'type': 'warning',
                'severity': 'high',
                'text': 'No sources cited',
                'explanation': 'Article lacks source attribution, making verification difficult'
            })
        
        # Quotes
        if quotes_included >= 3:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': f'{quotes_included} direct quotes included',
                'explanation': 'Article uses direct quotes for transparency'
            })
        
        # Methodology
        if has_methodology:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': 'Methodology disclosed',
                'explanation': 'Article explains how data was collected or analyzed'
            })
        
        # Corrections
        if has_corrections:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': 'Corrections/updates disclosed',
                'explanation': 'Article transparently notes corrections or updates'
            })
        
        # Author
        if not author_transparency:
            findings.append({
                'type': 'warning',
                'severity': 'medium',
                'text': 'Author not clearly identified',
                'explanation': 'Lack of clear author attribution reduces accountability'
            })
        
        # Citation quality
        if citation_quality >= 70:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': 'High-quality citations',
                'explanation': 'Sources are specific and verifiable'
            })
        elif citation_quality < 40:
            findings.append({
                'type': 'warning',
                'severity': 'medium',
                'text': 'Low-quality citations',
                'explanation': 'Sources lack specificity or verifiability'
            })
        
        return findings
    
    def _generate_analysis(self, score: int, sources_cited: int, quotes_included: int,
                          has_methodology: bool, has_corrections: bool, citation_quality: int) -> Dict[str, str]:
        """Generate comprehensive analysis"""
        
        what_we_looked = (
            f"We analyzed source attribution, citation quality, methodology disclosure, "
            f"corrections policy, and author transparency. We examined {sources_cited} source citations "
            f"and {quotes_included} direct quotes in the article."
        )
        
        findings_parts = []
        if sources_cited >= 5:
            findings_parts.append(f"well-sourced with {sources_cited} citations")
        else:
            findings_parts.append(f"limited sourcing ({sources_cited} citations)")
        
        if has_methodology:
            findings_parts.append("methodology disclosed")
        if has_corrections:
            findings_parts.append("corrections policy evident")
        if citation_quality >= 70:
            findings_parts.append("high-quality citations")
        
        what_we_found = f"The article is {', '.join(findings_parts) if findings_parts else 'lacking transparency indicators'}."
        
        if score >= 70:
            what_it_means = (
                f"This article demonstrates strong transparency ({score}/100). "
                f"Sources are well-attributed, and readers can verify claims. "
                f"The outlet shows commitment to transparent journalism practices."
            )
        elif score >= 50:
            what_it_means = (
                f"This article has moderate transparency ({score}/100). "
                f"Some transparency elements are present, but improvements could be made in "
                f"source attribution or methodology disclosure."
            )
        else:
            what_it_means = (
                f"This article has limited transparency ({score}/100). "
                f"Lack of clear source attribution and methodology disclosure makes it difficult "
                f"for readers to verify claims independently."
            )
        
        return {
            'what_we_looked': what_we_looked,
            'what_we_found': what_we_found,
            'what_it_means': what_it_means
        }
    
    def _generate_summary(self, score: int, sources_cited: int, findings: List[Dict]) -> str:
        """Generate conversational summary"""
        
        positive_findings = len([f for f in findings if f['type'] == 'positive'])
        warning_findings = len([f for f in findings if f['type'] == 'warning'])
        
        summary = f"Transparency score: {score}/100. "
        
        if positive_findings > warning_findings:
            summary += f"Article shows good transparency with {sources_cited} sources cited and clear attribution. "
        elif warning_findings > positive_findings:
            summary += f"Article lacks transparency in key areas. {sources_cited} sources cited. "
        else:
            summary += f"Article has mixed transparency. {sources_cited} sources cited. "
        
        if score >= 70:
            summary += "Readers can verify most claims."
        else:
            summary += "Verification may be challenging."
        
        return summary


logger.info("[TransparencyAnalyzer v3.0] ✓ Fully implemented with _check_availability()")
