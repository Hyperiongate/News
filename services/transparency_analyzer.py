"""
Transparency Analyzer Service - v4.0.0 COMPLETE OVERHAUL
Last Updated: October 10, 2025

CHANGES FROM v3.0:
✅ ENHANCED: Detailed "what_we_looked/found/means" analysis
✅ ENHANCED: Specific findings showing WHICH sources are verifiable
✅ ENHANCED: Clear distinction between mentioned vs. linked sources
✅ ENHANCED: Examples of vague sourcing found in text
✅ ENHANCED: Actionable recommendations for improvement
✅ PRESERVES: All existing enhanced detection from v3.0
✅ NO BREAKING CHANGES: All existing fields maintained

PHILOSOPHY: Show users EXACTLY what transparency issues we found
TARGET: Users should understand source quality without being experts
"""

import re
import logging
import time
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
from services.base_analyzer import BaseAnalyzer
from services.ai_enhancement_mixin import AIEnhancementMixin

try:
    AI_MIXIN_AVAILABLE = True
except ImportError:
    AI_MIXIN_AVAILABLE = False

logger = logging.getLogger(__name__)


class TransparencyAnalyzer(BaseAnalyzer, AIEnhancementMixin):
    """Analyze article transparency with detailed explanations - v4.0.0"""
    
    def __init__(self):
        super().__init__('transparency_analyzer')
        if AI_MIXIN_AVAILABLE:
            AIEnhancementMixin.__init__(self)
        self._initialize_transparency_patterns()
        logger.info(f"TransparencyAnalyzer v4.0 initialized with AI: {getattr(self, '_ai_available', False)}")
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main transparency analysis with detailed explanations
        v4.0.0: Returns specific findings instead of vague scores
        """
        try:
            start_time = time.time()
            
            text = data.get('text', '')
            if not text:
                return self.get_error_result("No text provided for transparency analysis")
            
            title = data.get('title', '')
            author = data.get('author', '')
            domain = data.get('domain', '')
            url = data.get('url', '')
            
            logger.info(f"[TransparencyAnalyzer v4.0] Analyzing {len(text)} characters")
            
            # Enhanced analysis with examples
            source_attribution = self._analyze_source_attribution_detailed(text, url)
            disclosure_analysis = self._analyze_disclosures_detailed(text)
            correction_indicators = self._analyze_corrections_detailed(text)
            author_transparency = self._analyze_author_transparency_detailed(text, author)
            methodology_transparency = self._analyze_methodology_detailed(text)
            vague_sourcing = self._detect_vague_sourcing_detailed(text)
            
            # Calculate score with penalties
            transparency_components = {
                'source_attribution': source_attribution,
                'disclosures': disclosure_analysis,
                'corrections': correction_indicators,
                'author_transparency': author_transparency,
                'methodology': methodology_transparency,
                'vague_sourcing': vague_sourcing
            }
            
            overall_score = self._calculate_transparency_score_enhanced(transparency_components)
            transparency_level = self._get_transparency_level(overall_score)
            
            # Generate detailed findings
            findings = self._generate_detailed_findings(transparency_components, text)
            
            # Generate comprehensive analysis
            analysis = self._generate_comprehensive_analysis(
                transparency_components, overall_score, len(text.split())
            )
            
            # Generate conversational summary
            summary = self._generate_conversational_summary(
                transparency_components, overall_score, transparency_level
            )
            
            # Collect all indicators
            all_indicators = []
            missing_elements = []
            
            for component_name, component_data in transparency_components.items():
                if isinstance(component_data, dict):
                    all_indicators.extend(component_data.get('indicators', []))
                    missing_elements.extend(component_data.get('missing', []))
            
            # Build result
            result = {
                'service': self.service_name,
                'success': True,
                'available': True,
                'timestamp': time.time(),
                'data': {
                    # Core scores
                    'score': overall_score,
                    'level': transparency_level,
                    'transparency_score': overall_score,
                    'transparency_level': transparency_level,
                    
                    # NEW v4.0: Detailed findings
                    'findings': findings,
                    
                    # NEW v4.0: Comprehensive analysis
                    'analysis': analysis,
                    
                    # Conversational summary
                    'summary': summary,
                    
                    # Indicators and missing elements
                    'indicators': all_indicators,
                    'missing_elements': missing_elements[:10],
                    
                    # Component data
                    'components': transparency_components,
                    
                    # Source counts
                    'source_count': source_attribution.get('total_sources', 0),
                    'verifiable_sources': source_attribution.get('verifiable_count', 0),
                    'linked_sources': source_attribution.get('linked_sources', 0),
                    'vague_sources': source_attribution.get('vague_count', 0),
                    'source_quality': source_attribution.get('quality_rating', 'Poor'),
                    
                    # Quote counts
                    'quote_count': source_attribution.get('quote_count', 0),
                    'direct_quotes': source_attribution.get('direct_quotes', 0),
                    'indirect_quotes': source_attribution.get('indirect_quotes', 0),
                    
                    # Other transparency elements
                    'has_disclosures': disclosure_analysis.get('has_disclosures', False),
                    'disclosure_types': disclosure_analysis.get('types_found', []),
                    'methodology_score': methodology_transparency.get('score', 0),
                    'has_author': author_transparency.get('author_present', False),
                    
                    # Chart data
                    'details': {
                        'sources_cited': source_attribution.get('total_sources', 0),
                        'verifiable_sources': source_attribution.get('verifiable_count', 0),
                        'linked_sources': source_attribution.get('linked_sources', 0),
                        'vague_sources': source_attribution.get('vague_count', 0),
                        'quotes_used': source_attribution.get('quote_count', 0),
                        'direct_quotes': source_attribution.get('direct_quotes', 0),
                        'indirect_quotes': source_attribution.get('indirect_quotes', 0),
                        'disclosures_found': len(disclosure_analysis.get('types_found', [])),
                        'transparency_indicators': len(all_indicators),
                        'missing_elements_count': len(missing_elements),
                        'author_identified': author_transparency.get('author_present', False),
                        'has_corrections': correction_indicators.get('has_corrections', False),
                        'methodology_elements': len(methodology_transparency.get('methodology_elements', [])),
                        'vague_sourcing_penalty': vague_sourcing.get('penalty', 0)
                    }
                },
                'metadata': {
                    'analysis_time': time.time() - start_time,
                    'text_length': len(text),
                    'analyzed_with_author': bool(author),
                    'analyzed_with_domain': bool(domain),
                    'version': '4.0.0',
                    'enhanced_detection': True
                }
            }
            
            # AI Enhancement
            if text and getattr(self, '_ai_available', False) and AI_MIXIN_AVAILABLE:
                logger.info("[TransparencyAnalyzer v4.0] Enhancing with AI")
                try:
                    result = self._safely_enhance_service_result(
                        result,
                        '_ai_analyze_transparency',
                        transparency_data={
                            'indicators': all_indicators,
                            'source_count': source_attribution.get('total_sources', 0),
                            'verifiable_count': source_attribution.get('verifiable_count', 0)
                        },
                        article_data={'title': title, 'author': author, 'source': domain}
                    )
                    if result:
                        result['metadata']['ai_enhancement_applied'] = True
                except Exception as ai_error:
                    logger.warning(f"AI enhancement failed: {ai_error}")
                    result['metadata']['ai_enhancement_failed'] = str(ai_error)
            
            logger.info(f"[TransparencyAnalyzer v4.0] Complete: {overall_score}/100 ({transparency_level})")
            return result
            
        except Exception as e:
            logger.error(f"[TransparencyAnalyzer v4.0] Failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _initialize_transparency_patterns(self):
        """Initialize patterns for transparency detection"""
        
        self.source_patterns = [
            r'according to\s+([^,.]+)',
            r'(?:said|stated|reported|told|claimed|announced)\s+([^,.]+)',
            r'([^,.]+)\s+(?:said|stated|reported|told|claimed)',
            r'in (?:an? )?(?:interview|statement|report)',
            r'(?:data|statistics) from\s+([^,.]+)',
            r'(?:study|research|report) (?:by|from|conducted by)\s+([^,.]+)'
        ]
        
        self.vague_source_patterns = [
            r'(?:studies|research) (?:show|shows|suggest|suggests|indicate|indicates)',
            r'(?:one|two|a few|some|several) (?:study|studies|report|reports)',
            r'(?:experts?|officials?|sources?) (?:say|said|claim|claimed)',
            r'according to (?:reports|sources|officials)',
            r'(?:unnamed|anonymous|confidential) sources?',
            r'it has been reported',
            r'reports suggest',
            r'there(?:\'s|\s+is) evidence',
            r'(?:many|most) (?:experts?|scientists?) (?:believe|think|agree)'
        ]
        
        self.indirect_quote_patterns = [
            r'(?:said|stated|claimed|announced|reported|explained|noted) that',
            r'according to .+?, ',
        ]
        
        self.disclosure_patterns = {
            'conflicts': ['conflict of interest', 'financial interest', 'investment in', 'shareholder'],
            'funding': ['funded by', 'sponsored by', 'supported by', 'grant from'],
            'corrections': ['correction:', 'updated:', 'clarification:', 'editor\'s note'],
            'methodology': ['survey of', 'poll conducted', 'data collected', 'methodology']
        }
    
    def _analyze_source_attribution_detailed(self, text: str, url: str = '') -> Dict[str, Any]:
        """Enhanced source attribution with specific examples"""
        
        # Count quotes
        direct_quote_count = text.count('"') // 2
        indirect_quote_count = sum(1 for pattern in self.indirect_quote_patterns 
                                   if re.search(pattern, text, re.IGNORECASE))
        total_quote_count = direct_quote_count + indirect_quote_count
        
        # Count source attributions
        total_sources = 0
        source_mentions = []
        source_examples = []
        
        for pattern in self.source_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                total_sources += 1
                if len(source_mentions) < 5:
                    source_text = match[:50] if isinstance(match, str) else str(match)[:50]
                    source_mentions.append(source_text)
                    
                    # Get context for example
                    match_str = match if isinstance(match, str) else str(match)
                    pos = text.lower().find(match_str.lower())
                    if pos != -1 and len(source_examples) < 3:
                        start = max(0, pos - 30)
                        end = min(len(text), pos + len(match_str) + 50)
                        example = text[start:end].strip()
                        if start > 0:
                            example = "..." + example
                        if end < len(text):
                            example = example + "..."
                        source_examples.append(example)
        
        # Detect hyperlinks
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        links_found = re.findall(url_pattern, text)
        linked_sources = len(set(links_found))
        
        # Count vague sourcing
        vague_count = 0
        vague_examples = []
        for pattern in self.vague_source_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                vague_count += 1
                if len(vague_examples) < 3:
                    start = max(0, match.start() - 20)
                    end = min(len(text), match.end() + 40)
                    example = text[start:end].strip()
                    if start > 0:
                        example = "..." + example
                    if end < len(text):
                        example = example + "..."
                    vague_examples.append({
                        'text': example,
                        'phrase': match.group()
                    })
        
        # Calculate verifiable sources
        specific_sources = self._count_specific_sources(text)
        verifiable_count = min(specific_sources, linked_sources) if linked_sources > 0 else max(0, specific_sources - vague_count)
        
        # Determine quality rating
        if verifiable_count >= 3 and linked_sources >= 2:
            quality_rating = "Excellent"
        elif verifiable_count >= 2 or linked_sources >= 1:
            quality_rating = "Good"
        elif total_sources >= 3 and vague_count < 2:
            quality_rating = "Fair"
        elif total_sources > 0:
            quality_rating = "Poor"
        else:
            quality_rating = "Very Poor"
        
        # Build indicators and issues
        indicators = []
        issues = []
        
        if direct_quote_count > 0:
            indicators.append(f"{direct_quote_count} direct quote(s) found")
        else:
            issues.append({
                'type': 'no_quotes',
                'text': 'No direct quotes found',
                'impact': 'Direct quotes add credibility and allow readers to verify statements'
            })
        
        if indirect_quote_count > 0:
            indicators.append(f"{indirect_quote_count} indirect quote(s) detected")
        
        if linked_sources > 0:
            indicators.append(f"{linked_sources} clickable source link(s) provided")
        else:
            issues.append({
                'type': 'no_links',
                'text': 'No hyperlinks to verify sources',
                'impact': 'Links allow readers to verify claims independently',
                'severity': 'high'
            })
        
        if verifiable_count >= 3:
            indicators.append(f"{verifiable_count} verifiable source(s)")
        elif verifiable_count == 0:
            issues.append({
                'type': 'no_verifiable',
                'text': 'No verifiable source attribution',
                'impact': 'Cannot independently verify any claims',
                'severity': 'high'
            })
        
        if vague_count > 0:
            issues.append({
                'type': 'vague_sourcing',
                'text': f'{vague_count} instance(s) of vague sourcing',
                'impact': 'Phrases like "studies show" without specific citations reduce credibility',
                'examples': vague_examples[:2],
                'severity': 'high' if vague_count >= 3 else 'medium'
            })
        
        # Calculate score
        base_score = (verifiable_count * 25) + (linked_sources * 15) + (total_quote_count * 5)
        vague_penalty = vague_count * 10
        final_score = max(0, min(100, base_score - vague_penalty))
        
        return {
            'score': final_score,
            'total_sources': total_sources,
            'verifiable_count': verifiable_count,
            'linked_sources': linked_sources,
            'vague_count': vague_count,
            'quote_count': total_quote_count,
            'direct_quotes': direct_quote_count,
            'indirect_quotes': indirect_quote_count,
            'source_mentions': source_mentions,
            'source_examples': source_examples,
            'vague_examples': vague_examples,
            'quality_rating': quality_rating,
            'indicators': indicators,
            'issues': issues
        }
    
    def _count_specific_sources(self, text: str) -> int:
        """Count sources with specific names/institutions"""
        specific_patterns = [
            r'(?:Dr\.|Professor|Secretary) [A-Z][a-z]+ [A-Z][a-z]+',
            r'[A-Z][a-z]+ [A-Z][a-z]+ (?:Jr\.|Sr\.|III)',
            r'(?:University of|Institute of|Department of) [A-Z][a-z]+',
            r'(?:New York Times|Washington Post|Reuters|Associated Press|CNN|BBC|NPR)',
            r'(?:FDA|CDC|WHO|NIH|JAMA|NASA|EPA)',
            r'\d{4} (?:study|report) (?:from|in|by) .+?(?:\.|,)',
            r'Journal of [A-Z][a-z]+'
        ]
        
        count = 0
        for pattern in specific_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            count += len(matches)
        
        return count
    
    def _detect_vague_sourcing_detailed(self, text: str) -> Dict[str, Any]:
        """Detect vague sourcing with examples"""
        
        vague_instances = []
        
        for pattern in self.vague_source_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(vague_instances) < 5:
                    start = max(0, match.start() - 30)
                    end = min(len(text), match.end() + 50)
                    example = text[start:end].strip()
                    
                    vague_instances.append({
                        'phrase': match.group(),
                        'example': f"...{example}..." if start > 0 else example
                    })
        
        penalty = min(50, len(vague_instances) * 10)
        
        issues = []
        if vague_instances:
            issues.append({
                'type': 'vague_sourcing',
                'text': f'Found {len(vague_instances)} vague source reference(s)',
                'examples': vague_instances[:3]
            })
        
        return {
            'penalty': penalty,
            'instance_count': len(vague_instances),
            'instances': vague_instances,
            'issues': issues
        }
    
    def _analyze_disclosures_detailed(self, text: str) -> Dict[str, Any]:
        """Analyze disclosures with specific findings"""
        
        text_lower = text.lower()
        found_disclosures = []
        indicators = []
        issues = []
        disclosure_examples = []
        
        for disclosure_type, patterns in self.disclosure_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    found_disclosures.append(disclosure_type)
                    indicators.append(f"Contains {disclosure_type} disclosure")
                    
                    # Get example
                    pos = text_lower.find(pattern)
                    if pos != -1 and len(disclosure_examples) < 3:
                        start = max(0, pos - 20)
                        end = min(len(text), pos + len(pattern) + 80)
                        example = text[start:end].strip()
                        disclosure_examples.append({
                            'type': disclosure_type,
                            'example': f"...{example}..."
                        })
                    break
        
        if 'conflicts' not in found_disclosures:
            issues.append({
                'type': 'no_conflict_disclosure',
                'text': 'No conflict of interest disclosure',
                'impact': 'Readers cannot assess potential biases'
            })
        
        if 'funding' not in found_disclosures and len(text) > 800:
            issues.append({
                'type': 'no_funding_disclosure',
                'text': 'No funding source disclosure',
                'impact': 'Financial backing can influence content'
            })
        
        return {
            'has_disclosures': len(found_disclosures) > 0,
            'types_found': found_disclosures,
            'disclosure_count': len(found_disclosures),
            'examples': disclosure_examples,
            'indicators': indicators,
            'issues': issues,
            'score': min(100, len(found_disclosures) * 25)
        }
    
    def _analyze_corrections_detailed(self, text: str) -> Dict[str, Any]:
        """Analyze correction policy with details"""
        
        correction_indicators = ['correction:', 'update:', 'clarification:', 'editor\'s note', 'corrected']
        has_corrections = any(indicator in text.lower() for indicator in correction_indicators)
        
        indicators = []
        issues = []
        
        if has_corrections:
            # Find the correction
            text_lower = text.lower()
            for indicator in correction_indicators:
                pos = text_lower.find(indicator)
                if pos != -1:
                    start = max(0, pos - 10)
                    end = min(len(text), pos + 150)
                    example = text[start:end].strip()
                    indicators.append(f"Correction notice present: ...{example}...")
                    break
        
        return {
            'has_corrections': has_corrections,
            'indicators': indicators,
            'issues': issues,
            'score': 100 if has_corrections else 50
        }
    
    def _analyze_author_transparency_detailed(self, text: str, author: str) -> Dict[str, Any]:
        """Analyze author transparency with details"""
        
        author_present = bool(author and author.strip() and author.lower() != 'unknown')
        
        indicators = []
        issues = []
        
        if author_present:
            indicators.append(f"Author identified: {author}")
            
            # Check for credentials
            credentials = ['ph.d', 'md', 'professor', 'dr.', 'journalist', 'correspondent', 'editor']
            found_creds = [cred for cred in credentials if cred in text.lower()]
            
            if found_creds:
                indicators.append(f"Author credentials mentioned: {', '.join(found_creds[:2])}")
        else:
            issues.append({
                'type': 'no_author',
                'text': 'Author not identified',
                'impact': 'Cannot assess writer\'s expertise or accountability'
            })
        
        return {
            'author_present': author_present,
            'author_name': author if author_present else None,
            'indicators': indicators,
            'issues': issues,
            'score': 100 if author_present else 30
        }
    
    def _analyze_methodology_detailed(self, text: str) -> Dict[str, Any]:
        """Analyze methodology transparency with details"""
        
        methodology_keywords = [
            'methodology', 'methods', 'survey of', 'poll conducted',
            'data collected', 'sample size', 'participants', 'respondents',
            'random sample', 'control group', 'peer-reviewed'
        ]
        
        found_elements = [kw for kw in methodology_keywords if kw in text.lower()]
        
        indicators = []
        issues = []
        examples = []
        
        if found_elements:
            indicators.append(f"Methodology elements present: {', '.join(found_elements[:3])}")
            
            # Get example
            for element in found_elements[:1]:
                pos = text.lower().find(element)
                if pos != -1:
                    start = max(0, pos - 20)
                    end = min(len(text), pos + len(element) + 80)
                    example = text[start:end].strip()
                    examples.append(f"...{example}...")
        else:
            issues.append({
                'type': 'no_methodology',
                'text': 'No methodology explanation',
                'impact': 'Cannot assess data collection reliability'
            })
        
        score = min(100, len(found_elements) * 20)
        
        return {
            'methodology_elements': found_elements,
            'count': len(found_elements),
            'examples': examples,
            'indicators': indicators,
            'issues': issues,
            'score': score
        }
    
    def _calculate_transparency_score_enhanced(self, components: Dict[str, Any]) -> int:
        """Calculate transparency score with penalties"""
        
        weights = {
            'source_attribution': 0.40,
            'disclosures': 0.20,
            'author_transparency': 0.15,
            'methodology': 0.15,
            'corrections': 0.10
        }
        
        total_score = 0
        for component_name, weight in weights.items():
            component_score = components.get(component_name, {}).get('score', 0)
            total_score += component_score * weight
        
        # Apply vague sourcing penalty
        vague_penalty = components.get('vague_sourcing', {}).get('penalty', 0)
        final_score = max(0, int(total_score - vague_penalty))
        
        return min(100, final_score)
    
    def _get_transparency_level(self, score: int) -> str:
        """Convert score to level"""
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
    
    def _generate_detailed_findings(self, components: Dict[str, Any], text: str) -> List[Dict[str, Any]]:
        """Generate detailed findings with examples"""
        findings = []
        
        # Collect all issues from components
        for component_name, component_data in components.items():
            if isinstance(component_data, dict):
                issues = component_data.get('issues', [])
                for issue in issues:
                    if isinstance(issue, dict):
                        findings.append({
                            'type': 'warning',
                            'severity': issue.get('severity', 'medium'),
                            'category': component_name,
                            'text': issue.get('text', ''),
                            'explanation': issue.get('impact', ''),
                            'examples': issue.get('examples', [])
                        })
        
        # Add positive findings for high-scoring components
        for component_name, component_data in components.items():
            if isinstance(component_data, dict) and component_data.get('score', 0) >= 75:
                indicators = component_data.get('indicators', [])
                if indicators:
                    findings.append({
                        'type': 'positive',
                        'severity': 'positive',
                        'category': component_name,
                        'text': indicators[0] if isinstance(indicators[0], str) else str(indicators[0]),
                        'explanation': f'Strong {component_name.replace("_", " ")} in this article'
                    })
        
        # Sort by severity
        severity_order = {'high': 0, 'medium': 1, 'low': 2, 'positive': 3}
        findings.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 4))
        
        return findings[:15]
    
    def _generate_comprehensive_analysis(self, components: Dict[str, Any],
                                        score: int, word_count: int) -> Dict[str, str]:
        """Generate comprehensive what_we_looked/found/means analysis"""
        
        # What we looked at
        what_we_looked = (
            f"We analyzed {word_count} words examining source attribution (verifiable vs. vague sources, "
            f"hyperlinks), disclosure statements, author transparency, methodology explanations, and "
            f"correction policies to assess how transparently this article presents information."
        )
        
        # What we found
        source_data = components['source_attribution']
        verifiable = source_data.get('verifiable_count', 0)
        vague = source_data.get('vague_count', 0)
        linked = source_data.get('linked_sources', 0)
        
        findings_parts = []
        
        if verifiable > 0:
            findings_parts.append(f"{verifiable} verifiable source(s)")
        if linked > 0:
            findings_parts.append(f"{linked} clickable link(s)")
        if vague > 0:
            findings_parts.append(f"{vague} vague source reference(s)")
        
        if components['disclosures'].get('has_disclosures'):
            types = components['disclosures'].get('types_found', [])
            findings_parts.append(f"disclosure statements ({', '.join(types)})")
        else:
            findings_parts.append("no disclosure statements")
        
        if components['author_transparency'].get('author_present'):
            findings_parts.append("author identified")
        else:
            findings_parts.append("no author attribution")
        
        what_we_found = "Found: " + ", ".join(findings_parts) + "."
        
        # What it means
        if score >= 70:
            what_it_means = (
                f"This article demonstrates strong transparency ({score}/100). "
                f"Sources are verifiable, proper attribution is present, and readers can independently "
                f"verify claims. This level of transparency indicates professional journalism standards."
            )
        elif score >= 50:
            what_it_means = (
                f"This article has moderate transparency ({score}/100). "
                f"Some transparency elements are present, but {'vague sourcing' if vague > 0 else 'missing elements'} "
                f"reduce reliability. Readers should verify important claims independently."
            )
        else:
            what_it_means = (
                f"This article has poor transparency ({score}/100). "
                f"{'Vague sourcing, ' if vague > 0 else ''}Lack of verifiable sources and missing transparency "
                f"elements make it difficult to assess credibility. Treat claims with significant skepticism and "
                f"verify all important information through other sources."
            )
        
        return {
            'what_we_looked': what_we_looked,
            'what_we_found': what_we_found,
            'what_it_means': what_it_means
        }
    
    def _generate_conversational_summary(self, components: Dict[str, Any],
                                         score: int, level: str) -> str:
        """Generate conversational summary"""
        
        source_data = components['source_attribution']
        verifiable = source_data.get('verifiable_count', 0)
        vague = source_data.get('vague_count', 0)
        
        if score >= 80:
            base = f"Excellent transparency ({score}/100). "
        elif score >= 65:
            base = f"Good transparency ({score}/100). "
        elif score >= 50:
            base = f"Fair transparency ({score}/100). "
        else:
            base = f"Poor transparency ({score}/100). "
        
        if verifiable > 0:
            base += f"Contains {verifiable} verifiable source(s). "
        elif source_data.get('total_sources', 0) > 0:
            base += f"Mentions sources but lacks verification. "
        
        if vague > 0:
            base += f"Uses vague sourcing ({vague} instances). "
        
        if components.get('disclosures', {}).get('has_disclosures'):
            base += "Includes disclosure statements. "
        
        if components.get('author_transparency', {}).get('author_present'):
            base += "Author identified. "
        
        return base.strip()
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        info = super().get_service_info()
        info.update({
            'version': '4.0.0',
            'capabilities': [
                'Verifiable vs vague source detection',
                'Hyperlink verification',
                'Direct and indirect quote analysis',
                'Disclosure statement detection',
                'Author transparency assessment',
                'Methodology explanation evaluation',
                'Correction policy analysis',
                'Specific examples of issues found',
                'AI-enhanced transparency analysis' if getattr(self, '_ai_available', False) else 'Pattern-based analysis'
            ],
            'transparency_elements': [
                'source_attribution', 'verifiable_sources', 'link_verification',
                'disclosures', 'corrections', 'author_transparency', 'methodology'
            ],
            'ai_enhanced': getattr(self, '_ai_available', False)
        })
        return info
