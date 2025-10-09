"""
Transparency Analyzer Service - ENHANCED VERSION v3.0
Last Updated: October 9, 2025
Analyzes how transparently articles present information and sources

CHANGES FROM v2.0:
✅ ENHANCED: Distinguishes between mentioned sources vs. linked/verifiable sources
✅ ENHANCED: Detects indirect quotes ("Kennedy said that...")
✅ ENHANCED: Penalizes "source laundering" ("studies show" without specifics)
✅ ENHANCED: Requires actual hyperlinks for high transparency scores
✅ ENHANCED: Grades attribution quality (specific > vague > missing)
✅ ENHANCED: Detects vague sourcing patterns
✅ PRESERVES: All existing functionality and data structures
✅ NO BREAKING CHANGES: All existing fields maintained

TARGET: RFK/Tylenol article should score 20-30/100, not 46/100

PHILOSOPHY: "Do No Harm" - Only enhance detection, never break existing behavior
"""

import re
import logging
import time
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
from services.base_analyzer import BaseAnalyzer
from services.ai_enhancement_mixin import AIEnhancementMixin

# Check if AI mixin is available
try:
    AI_MIXIN_AVAILABLE = True
except ImportError:
    AI_MIXIN_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("AI Enhancement Mixin not available")

logger = logging.getLogger(__name__)


class TransparencyAnalyzer(BaseAnalyzer, AIEnhancementMixin):
    """Analyze article transparency - v3.0 ENHANCED"""
    
    def __init__(self):
        super().__init__('transparency_analyzer')
        if AI_MIXIN_AVAILABLE:
            AIEnhancementMixin.__init__(self)
        self._initialize_transparency_patterns()
        logger.info(f"TransparencyAnalyzer v3.0 initialized with AI: {getattr(self, '_ai_available', False)}")
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main transparency analysis method - v3.0 ENHANCED
        
        PRESERVES: All v2.0 functionality
        ENHANCES: Better source detection, link verification, vague sourcing penalties
        """
        try:
            start_time = time.time()
            
            text = data.get('text', '')
            if not text:
                return self.get_error_result("No text provided for transparency analysis")
            
            title = data.get('title', '')
            author = data.get('author', '')
            domain = data.get('domain', '')
            url = data.get('url', '')  # NEW v3.0: Track original URL
            
            logger.info(f"Analyzing transparency in {len(text)} characters of text")
            
            # v3.0 ENHANCED: Source attribution with link detection
            source_attribution = self._analyze_source_attribution_enhanced(text, url)
            
            # PRESERVED: All existing analysis methods
            disclosure_analysis = self._analyze_disclosures(text)
            correction_indicators = self._analyze_corrections(text)
            author_transparency = self._analyze_author_transparency(text, author)
            methodology_transparency = self._analyze_methodology(text)
            
            # NEW v3.0: Vague sourcing penalties
            vague_sourcing_penalty = self._detect_vague_sourcing(text)
            
            # Calculate overall transparency score with penalties
            transparency_components = {
                'source_attribution': source_attribution,
                'disclosures': disclosure_analysis,
                'corrections': correction_indicators,
                'author_transparency': author_transparency,
                'methodology': methodology_transparency,
                'vague_sourcing_penalty': vague_sourcing_penalty  # NEW v3.0
            }
            
            overall_score = self._calculate_transparency_score_enhanced(transparency_components)
            transparency_level = self._get_transparency_level(overall_score)
            
            # Generate findings
            findings = self._generate_findings(transparency_components, overall_score)
            
            # Generate summary
            summary = self._generate_summary(transparency_components, overall_score, transparency_level)
            
            # Compile all transparency indicators
            all_indicators = []
            missing_elements = []
            
            for component_name, component_data in transparency_components.items():
                if isinstance(component_data, dict):
                    indicators = component_data.get('indicators', [])
                    all_indicators.extend(indicators)
                    
                    missing = component_data.get('missing', [])
                    missing_elements.extend(missing)
            
            # PRESERVED + ENHANCED: Result structure (all v2.0 fields + new v3.0 fields)
            result = {
                'service': self.service_name,
                'success': True,
                'available': True,
                'timestamp': time.time(),
                'data': {
                    # PRESERVED: All v2.0 fields
                    'score': overall_score,
                    'level': transparency_level,
                    'transparency_score': overall_score,
                    'transparency_level': transparency_level,
                    'findings': findings,
                    'summary': summary,
                    'indicators': all_indicators,
                    'missing_elements': missing_elements[:10],
                    'components': transparency_components,
                    'source_count': source_attribution.get('total_sources', 0),
                    'quote_count': source_attribution.get('quote_count', 0),
                    'has_disclosures': disclosure_analysis.get('has_disclosures', False),
                    'disclosure_types': disclosure_analysis.get('types_found', []),
                    'methodology_score': methodology_transparency.get('score', 0),
                    
                    # NEW v3.0: Enhanced source tracking
                    'verifiable_sources': source_attribution.get('verifiable_count', 0),
                    'linked_sources': source_attribution.get('linked_sources', 0),
                    'vague_sources': source_attribution.get('vague_count', 0),
                    'source_quality': source_attribution.get('quality_rating', 'Poor'),
                    'vague_sourcing_score': vague_sourcing_penalty,
                    
                    # PRESERVED: details dict
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
                        'vague_sourcing_detected': vague_sourcing_penalty > 0
                    }
                },
                'metadata': {
                    'analysis_time': time.time() - start_time,
                    'text_length': len(text),
                    'analyzed_with_author': bool(author),
                    'analyzed_with_domain': bool(domain),
                    'version': '3.0',
                    'enhanced_source_detection': True
                }
            }
            
            # PRESERVED: AI Enhancement
            if text and getattr(self, '_ai_available', False) and AI_MIXIN_AVAILABLE:
                logger.info("Enhancing transparency analysis with AI insights")
                
                transparency_data = {
                    'indicators': all_indicators,
                    'source_count': source_attribution.get('total_sources', 0),
                    'verifiable_count': source_attribution.get('verifiable_count', 0),
                    'quote_count': source_attribution.get('quote_count', 0),
                    'has_disclosures': disclosure_analysis.get('has_disclosures', False)
                }
                
                article_data = {
                    'title': title,
                    'author': author,
                    'source': domain
                }
                
                try:
                    result = self._safely_enhance_service_result(
                        result,
                        '_ai_analyze_transparency',
                        transparency_data=transparency_data,
                        article_data=article_data
                    )
                    if result:
                        result['metadata']['ai_enhancement_applied'] = True
                except Exception as ai_error:
                    logger.warning(f"AI enhancement failed safely: {ai_error}")
                    result['metadata']['ai_enhancement_failed'] = str(ai_error)
            
            logger.info(f"Transparency analysis complete: {overall_score}/100 ({transparency_level}) - {source_attribution.get('verifiable_count', 0)} verifiable sources")
            return result
            
        except Exception as e:
            logger.error(f"Transparency analysis failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _initialize_transparency_patterns(self):
        """Initialize patterns for transparency detection - ENHANCED v3.0"""
        
        # Source attribution patterns (PRESERVED + ENHANCED)
        self.source_patterns = [
            r'according to\s+([^,.]+)',
            r'(?:said|stated|reported|told|claimed|announced)\s+([^,.]+)',
            r'([^,.]+)\s+(?:said|stated|reported|told|claimed)',
            r'in (?:an? )?(?:interview|statement|report)',
            r'(?:data|statistics) from\s+([^,.]+)',
            r'(?:study|research|report) (?:by|from|conducted by)\s+([^,.]+)'
        ]
        
        # NEW v3.0: Vague sourcing patterns (these are RED FLAGS)
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
        
        # NEW v3.0: Indirect quote patterns
        self.indirect_quote_patterns = [
            r'(?:said|stated|claimed|announced|reported|explained|noted) that',
            r'according to .+?, ',
            r'(?:Kennedy|Trump|officials?|experts?) (?:said|claimed) .+? (?:could|would|might|should)'
        ]
        
        # Disclosure patterns (PRESERVED)
        self.disclosure_patterns = {
            'conflicts': ['conflict of interest', 'financial interest', 'investment in', 'shareholder'],
            'funding': ['funded by', 'sponsored by', 'supported by', 'grant from'],
            'corrections': ['correction:', 'updated:', 'clarification:', 'editor\'s note'],
            'methodology': ['survey of', 'poll conducted', 'data collected', 'methodology']
        }
        
        # Transparency indicators (PRESERVED)
        self.transparency_indicators = [
            'sources', 'documents', 'records', 'data', 'statistics',
            'interview', 'statement', 'report', 'study', 'analysis'
        ]
    
    def _analyze_source_attribution_enhanced(self, text: str, url: str = '') -> Dict[str, Any]:
        """
        NEW v3.0: Enhanced source attribution analysis
        
        Distinguishes between:
        - Verifiable sources (with links/specific details)
        - Vague sources ("studies show")
        - Mentioned sources (named but not linked)
        """
        
        # Count direct quotes
        direct_quote_count = text.count('"') // 2
        
        # NEW v3.0: Count indirect quotes
        indirect_quote_count = sum(1 for pattern in self.indirect_quote_patterns 
                                   if re.search(pattern, text, re.IGNORECASE))
        
        total_quote_count = direct_quote_count + indirect_quote_count
        
        # Count source attributions
        total_sources = 0
        source_mentions = []
        
        for pattern in self.source_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            total_sources += len(matches)
            source_mentions.extend([m[:50] if isinstance(m, str) else str(m)[:50] for m in matches[:3]])
        
        # NEW v3.0: Detect hyperlinks (actual verifiable sources)
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        links_found = re.findall(url_pattern, text)
        linked_sources = len(set(links_found))  # Unique links
        
        # NEW v3.0: Count vague sourcing
        vague_count = sum(1 for pattern in self.vague_source_patterns 
                         if re.search(pattern, text, re.IGNORECASE))
        
        # NEW v3.0: Calculate verifiable sources
        # Verifiable = has specific name AND (linked OR institutional)
        specific_sources = self._count_specific_sources(text)
        verifiable_count = min(specific_sources, linked_sources) if linked_sources > 0 else max(0, specific_sources - vague_count)
        
        # NEW v3.0: Determine quality rating
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
        
        # Build indicators and missing elements
        indicators = []
        missing = []
        
        if direct_quote_count > 0:
            indicators.append(f"Direct quotes present ({direct_quote_count})")
        else:
            missing.append("No direct quotes found")
        
        if indirect_quote_count > 0:
            indicators.append(f"Indirect quotes detected ({indirect_quote_count})")
        
        if linked_sources > 0:
            indicators.append(f"Hyperlinks to sources provided ({linked_sources})")
        else:
            missing.append("No clickable links to verify sources")
        
        if verifiable_count >= 3:
            indicators.append("Multiple verifiable sources")
        elif verifiable_count >= 1:
            indicators.append("Some verifiable sources")
        else:
            missing.append("No verifiable source attribution")
        
        if vague_count > 0:
            missing.append(f"Vague sourcing detected ({vague_count} instances)")
        
        # Check for anonymous sources
        anonymous_count = len(re.findall(r'anonymous|unnamed|confidential source', text, re.IGNORECASE))
        if anonymous_count > 0:
            indicators.append(f"Anonymous sources identified ({anonymous_count})")
        
        # Calculate score with harsh penalties for lack of verifiability
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
            'anonymous_sources': anonymous_count,
            'source_mentions': source_mentions,
            'quality_rating': quality_rating,
            'indicators': indicators,
            'missing': missing
        }
    
    def _count_specific_sources(self, text: str) -> int:
        """NEW v3.0: Count sources with specific names/institutions"""
        specific_patterns = [
            r'(?:Dr\.|Professor|Secretary) [A-Z][a-z]+ [A-Z][a-z]+',  # Dr. John Smith
            r'[A-Z][a-z]+ [A-Z][a-z]+ (?:Jr\.|Sr\.|III)',  # Robert Kennedy Jr.
            r'(?:University of|Institute of|Department of) [A-Z][a-z]+',  # University of X
            r'(?:New York Times|Washington Post|Reuters|Associated Press)',  # Major outlets
            r'(?:FDA|CDC|WHO|NIH|JAMA)',  # Institutions
            r'\d{4} (?:study|report) (?:from|in|by) .+?(?:\.|,)',  # 2015 study from X
            r'Journal of [A-Z][a-z]+'  # Journal of Medicine
        ]
        
        count = 0
        for pattern in specific_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            count += len(matches)
        
        return count
    
    def _detect_vague_sourcing(self, text: str) -> int:
        """
        NEW v3.0: Detect and score vague sourcing (penalty component)
        Returns penalty points (0-50)
        """
        vague_instances = []
        
        for pattern in self.vague_source_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                vague_instances.extend(matches[:2])  # Sample up to 2
        
        # Penalty: 10 points per vague instance, max 50
        penalty = min(50, len(vague_instances) * 10)
        
        return penalty
    
    # ============================================================================
    # ALL METHODS BELOW ARE PRESERVED FROM v2.0
    # ============================================================================
    
    def _analyze_disclosures(self, text: str) -> Dict[str, Any]:
        """Analyze disclosure statements - PRESERVED from v2.0"""
        
        text_lower = text.lower()
        found_disclosures = []
        indicators = []
        missing = []
        
        for disclosure_type, patterns in self.disclosure_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    found_disclosures.append(disclosure_type)
                    indicators.append(f"Contains {disclosure_type} disclosure")
                    break
        
        if 'conflicts' not in found_disclosures:
            missing.append("No conflict of interest disclosure")
        if 'funding' not in found_disclosures and len(text) > 800:
            missing.append("No funding source disclosure")
        
        return {
            'has_disclosures': len(found_disclosures) > 0,
            'types_found': found_disclosures,
            'disclosure_count': len(found_disclosures),
            'indicators': indicators,
            'missing': missing,
            'score': min(100, len(found_disclosures) * 25)
        }
    
    def _analyze_corrections(self, text: str) -> Dict[str, Any]:
        """Analyze correction policy - PRESERVED from v2.0"""
        
        correction_indicators = ['correction:', 'update:', 'clarification:', 'editor\'s note', 'corrected']
        has_corrections = any(indicator in text.lower() for indicator in correction_indicators)
        
        indicators = []
        if has_corrections:
            indicators.append("Correction or update notice present")
        
        return {
            'has_corrections': has_corrections,
            'indicators': indicators,
            'score': 100 if has_corrections else 50
        }
    
    def _analyze_author_transparency(self, text: str, author: str) -> Dict[str, Any]:
        """Analyze author transparency - PRESERVED from v2.0"""
        
        author_present = bool(author and author.strip() and author.lower() != 'unknown')
        
        indicators = []
        missing = []
        
        if author_present:
            indicators.append(f"Author identified: {author}")
            
            # Check for author credentials in text
            credentials = ['ph.d', 'md', 'professor', 'dr.', 'journalist', 'correspondent']
            if any(cred in text.lower() for cred in credentials):
                indicators.append("Author credentials mentioned")
        else:
            missing.append("Author not identified")
        
        return {
            'author_present': author_present,
            'author_name': author if author_present else None,
            'indicators': indicators,
            'missing': missing,
            'score': 100 if author_present else 30
        }
    
    def _analyze_methodology(self, text: str) -> Dict[str, Any]:
        """Analyze methodology transparency - PRESERVED from v2.0"""
        
        methodology_keywords = [
            'methodology', 'methods', 'survey of', 'poll conducted', 
            'data collected', 'sample size', 'participants', 'respondents'
        ]
        
        found_elements = [kw for kw in methodology_keywords if kw in text.lower()]
        
        indicators = []
        missing = []
        
        if found_elements:
            indicators.append(f"Methodology elements present: {', '.join(found_elements[:3])}")
        else:
            missing.append("No methodology explanation")
        
        score = min(100, len(found_elements) * 20)
        
        return {
            'methodology_elements': found_elements,
            'count': len(found_elements),
            'indicators': indicators,
            'missing': missing,
            'score': score
        }
    
    def _calculate_transparency_score_enhanced(self, components: Dict[str, Any]) -> int:
        """NEW v3.0: Calculate transparency score with vague sourcing penalties"""
        
        # Weights (adjusted to account for penalties)
        weights = {
            'source_attribution': 0.40,  # Increased from 0.30
            'disclosures': 0.20,         # Decreased from 0.25
            'author_transparency': 0.15,  # Decreased from 0.20
            'methodology': 0.15,
            'corrections': 0.10
        }
        
        total_score = 0
        for component_name, weight in weights.items():
            component_score = components.get(component_name, {}).get('score', 0)
            total_score += component_score * weight
        
        # NEW v3.0: Apply vague sourcing penalty
        vague_penalty = components.get('vague_sourcing_penalty', 0)
        final_score = max(0, int(total_score - vague_penalty))
        
        return min(100, final_score)
    
    def _get_transparency_level(self, score: int) -> str:
        """Convert score to transparency level - PRESERVED from v2.0"""
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
    
    def _generate_findings(self, components: Dict[str, Any], overall_score: int) -> List[Dict[str, Any]]:
        """Generate findings - ENHANCED v3.0"""
        findings = []
        
        # Overall assessment
        if overall_score >= 80:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': f'Excellent transparency ({overall_score}/100)',
                'explanation': 'Article provides comprehensive transparency information with verifiable sources'
            })
        elif overall_score >= 50:
            findings.append({
                'type': 'info',
                'severity': 'medium',
                'text': f'Fair transparency ({overall_score}/100)',
                'explanation': 'Article provides some transparency but lacks verifiable sourcing'
            })
        else:
            findings.append({
                'type': 'warning',
                'severity': 'high',
                'text': f'Poor transparency ({overall_score}/100)',
                'explanation': 'Article lacks adequate transparency and verifiable sources'
            })
        
        # Source attribution findings (ENHANCED)
        source_data = components['source_attribution']
        verifiable = source_data.get('verifiable_count', 0)
        
        if verifiable >= 3:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': f"Multiple verifiable sources ({verifiable})",
                'explanation': 'Article cites specific, verifiable sources'
            })
        elif source_data.get('total_sources', 0) == 0:
            findings.append({
                'type': 'warning',
                'severity': 'high',
                'text': 'No sources cited',
                'explanation': 'Article lacks proper source attribution'
            })
        elif source_data.get('vague_count', 0) > 0:
            findings.append({
                'type': 'warning',
                'severity': 'medium',
                'text': f"Vague sourcing detected ({source_data['vague_count']} instances)",
                'explanation': 'Article uses phrases like "studies show" without specific citations'
            })
        
        # Disclosure findings (PRESERVED)
        disclosure_data = components['disclosures']
        if disclosure_data.get('has_disclosures', False):
            types = ', '.join(disclosure_data.get('types_found', []))
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': f'Disclosures present: {types}',
                'explanation': 'Article includes transparency disclosures'
            })
        
        # Author transparency (PRESERVED)
        author_data = components['author_transparency']
        if not author_data.get('author_present', False):
            findings.append({
                'type': 'warning',
                'severity': 'medium',
                'text': 'No author identified',
                'explanation': 'Article lacks author attribution'
            })
        
        return findings
    
    def _generate_summary(self, components: Dict[str, Any], score: int, level: str) -> str:
        """Generate summary - ENHANCED v3.0"""
        
        if score >= 80:
            base = "This article demonstrates excellent transparency practices with verifiable sources. "
        elif score >= 65:
            base = "This article shows good transparency with most elements present. "
        elif score >= 50:
            base = "This article provides fair transparency but lacks some verifiable sourcing. "
        elif score >= 35:
            base = "This article has poor transparency and lacks verifiable sources. "
        else:
            base = "This article has very poor transparency with significant sourcing issues. "
        
        # Add specific details
        source_data = components.get('source_attribution', {})
        verifiable = source_data.get('verifiable_count', 0)
        total = source_data.get('total_sources', 0)
        vague = source_data.get('vague_count', 0)
        
        if verifiable > 0:
            base += f"Contains {verifiable} verifiable source{'s' if verifiable != 1 else ''}. "
        elif total > 0:
            base += f"Mentions {total} source{'s' if total != 1 else ''} but lacks verification. "
        
        if vague > 0:
            base += f"Uses vague sourcing ({vague} instances). "
        
        if components.get('disclosures', {}).get('has_disclosures', False):
            base += "Contains disclosure statements. "
        
        if components.get('author_transparency', {}).get('author_present', False):
            base += "Author identified. "
        
        base += f"Overall transparency score: {score}/100."
        
        return base
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information - ENHANCED v3.0"""
        info = super().get_service_info()
        info.update({
            'capabilities': [
                'Enhanced source attribution analysis',
                'Verifiable vs vague source detection',
                'Hyperlink verification',
                'Direct and indirect quote detection',
                'Disclosure statement detection',
                'Author transparency assessment',
                'Methodology transparency evaluation',
                'Correction policy analysis',
                'Vague sourcing penalty system',
                'AI-enhanced transparency assessment' if getattr(self, '_ai_available', False) else 'Pattern-based transparency analysis'
            ],
            'transparency_elements': [
                'source_attribution',
                'verifiable_sources',
                'link_verification',
                'disclosures',
                'corrections',
                'author_transparency',
                'methodology',
                'vague_sourcing_detection'
            ],
            'version': '3.0',
            'ai_enhanced': getattr(self, '_ai_available', False)
        })
        return info


# Ensure the service can be instantiated
if __name__ == "__main__":
    analyzer = TransparencyAnalyzer()
    print(f"✓ Transparency Analyzer v3.0 initialized successfully")
    print(f"✓ Enhanced source detection enabled")
    print(f"✓ Vague sourcing penalty system active")
