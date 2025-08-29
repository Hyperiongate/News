"""
Transparency Analyzer Service - BULLETPROOF AI ENHANCED VERSION
Analyzes transparency indicators in news articles with bulletproof AI insights
FIXED: Proper data structure and AI enhancement integration
"""

import re
import logging
import time
import os
from typing import Dict, Any, Optional, List
from services.base_analyzer import BaseAnalyzer
from services.ai_enhancement_mixin import AIEnhancementMixin

logger = logging.getLogger(__name__)


class TransparencyAnalyzer(BaseAnalyzer, AIEnhancementMixin):
    """Analyze transparency in news articles WITH BULLETPROOF AI ENHANCEMENT"""
    
    def __init__(self):
        super().__init__('transparency_analyzer')
        AIEnhancementMixin.__init__(self)
        
        # Initialize transparency patterns
        self._initialize_transparency_patterns()
        
        logger.info(f"TransparencyAnalyzer initialized with AI enhancement: {self._ai_available}")
    
    def _check_availability(self) -> bool:
        """Service is always available"""
        return True
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze transparency indicators WITH BULLETPROOF AI ENHANCEMENT
        FIXED: Proper data structure and AI integration
        """
        try:
            start_time = time.time()
            
            text = data.get('text', '')
            if not text:
                return self.get_error_result("No text provided for transparency analysis")
            
            title = data.get('title', '')
            author = data.get('author', '')
            domain = data.get('domain', '')
            
            logger.info(f"Analyzing transparency in {len(text)} characters of text")
            
            # Core transparency analysis
            source_attribution = self._analyze_source_attribution(text)
            disclosure_analysis = self._analyze_disclosures(text)
            correction_indicators = self._analyze_corrections(text)
            author_transparency = self._analyze_author_transparency(text, author)
            methodology_transparency = self._analyze_methodology(text)
            
            # Calculate overall transparency score
            transparency_components = {
                'source_attribution': source_attribution,
                'disclosures': disclosure_analysis,
                'corrections': correction_indicators,
                'author_transparency': author_transparency,
                'methodology': methodology_transparency
            }
            
            overall_score = self._calculate_transparency_score(transparency_components)
            transparency_level = self._get_transparency_level(overall_score)
            
            # Generate findings
            findings = self._generate_findings(transparency_components, overall_score)
            
            # Generate summary
            summary = self._generate_summary(transparency_components, overall_score, transparency_level)
            
            # Compile all transparency indicators
            all_indicators = []
            missing_elements = []
            
            for component_name, component_data in transparency_components.items():
                indicators = component_data.get('indicators', [])
                all_indicators.extend(indicators)
                
                missing = component_data.get('missing', [])
                missing_elements.extend(missing)
            
            # FIXED: Ensure consistent data structure
            result = {
                'service': self.service_name,
                'success': True,
                'data': {
                    'score': overall_score,
                    'level': transparency_level,
                    'transparency_score': overall_score,
                    'transparency_level': transparency_level,
                    'findings': findings,
                    'summary': summary,
                    'indicators': all_indicators,
                    'missing_elements': missing_elements[:10],
                    'components': transparency_components,
                    'source_count': source_attribution.get('source_count', 0),
                    'quote_count': source_attribution.get('quote_count', 0),
                    'has_disclosures': disclosure_analysis.get('has_disclosures', False),
                    'disclosure_types': disclosure_analysis.get('types_found', []),
                    'methodology_score': methodology_transparency.get('score', 0),
                    'details': {
                        'sources_cited': source_attribution.get('source_count', 0),
                        'quotes_used': source_attribution.get('quote_count', 0),
                        'disclosures_found': len(disclosure_analysis.get('types_found', [])),
                        'transparency_indicators': len(all_indicators),
                        'missing_elements_count': len(missing_elements),
                        'author_identified': author_transparency.get('author_present', False),
                        'has_corrections': correction_indicators.get('has_corrections', False),
                        'methodology_elements': len(methodology_transparency.get('methodology_elements', []))
                    }
                },
                'metadata': {
                    'analysis_time': time.time() - start_time,
                    'text_length': len(text),
                    'analyzed_with_author': bool(author),
                    'analyzed_with_domain': bool(domain)
                }
            }
            
            # BULLETPROOF AI ENHANCEMENT
            if text:
                logger.info("Enhancing transparency analysis with AI insights")
                
                # Prepare data for AI analysis
                transparency_data = {
                    'indicators': all_indicators,
                    'source_count': source_attribution.get('source_count', 0),
                    'quote_count': source_attribution.get('quote_count', 0),
                    'has_disclosures': disclosure_analysis.get('has_disclosures', False)
                }
                
                article_data = {
                    'title': title,
                    'author': author,
                    'source': domain
                }
                
                result = self._safely_enhance_service_result(
                    result,
                    '_ai_analyze_transparency',
                    transparency_data=transparency_data,
                    article_data=article_data
                )
            
            logger.info(f"Transparency analysis complete: {overall_score}/100 ({transparency_level})")
            return result
            
        except Exception as e:
            logger.error(f"Transparency analysis failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _initialize_transparency_patterns(self):
        """Initialize patterns for transparency detection"""
        
        # Source attribution patterns
        self.source_patterns = [
            r'according to\s+([^,.]+)',
            r'(?:said|stated|reported|told)\s+([^,.]+)',
            r'([^,.]+)\s+(?:said|stated|reported)',
            r'in (?:an? )?(?:interview|statement)',
            r'(?:data|statistics) from\s+([^,.]+)'
        ]
        
        # Disclosure patterns
        self.disclosure_patterns = {
            'conflicts': ['conflict of interest', 'financial interest', 'investment in', 'shareholder'],
            'funding': ['funded by', 'sponsored by', 'supported by', 'grant from'],
            'corrections': ['correction:', 'updated:', 'clarification:', 'editor\'s note'],
            'methodology': ['survey of', 'poll conducted', 'data collected', 'methodology']
        }
        
        # Transparency indicators
        self.transparency_indicators = [
            'sources', 'documents', 'records', 'data', 'statistics',
            'interview', 'statement', 'report', 'study', 'analysis'
        ]
    
    def _analyze_source_attribution(self, text: str) -> Dict[str, Any]:
        """Analyze how well sources are attributed"""
        
        # Count quoted sources
        quote_count = text.count('"') // 2  # Pairs of quotes
        
        # Count source attributions
        source_count = 0
        source_mentions = []
        
        for pattern in self.source_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            source_count += len(matches)
            source_mentions.extend(matches[:3])  # Sample mentions
        
        # Analyze attribution quality
        indicators = []
        missing = []
        
        if quote_count > 0:
            indicators.append("Direct quotes present")
        else:
            missing.append("No direct quotes found")
        
        if source_count >= 3:
            indicators.append("Multiple sources cited")
        elif source_count >= 1:
            indicators.append("Sources cited")
        else:
            missing.append("No clear source attribution")
        
        # Check for anonymous sources
        anonymous_count = len(re.findall(r'anonymous|unnamed|confidential source', text, re.IGNORECASE))
        if anonymous_count > 0:
            indicators.append(f"Anonymous sources identified ({anonymous_count})")
        
        score = min(100, (source_count * 15) + (quote_count * 5) + (len(indicators) * 10))
        
        return {
            'score': score,
            'source_count': source_count,
            'quote_count': quote_count,
            'anonymous_sources': anonymous_count,
            'source_mentions': source_mentions,
            'indicators': indicators,
            'missing': missing
        }
    
    def _analyze_disclosures(self, text: str) -> Dict[str, Any]:
        """Analyze disclosure statements"""
        
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
        
        # Check for common missing disclosures
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
        """Analyze correction and update indicators"""
        
        correction_patterns = [
            'correction:', 'updated:', 'clarification:', 'editor\'s note:',
            'this story has been updated', 'corrected to reflect'
        ]
        
        text_lower = text.lower()
        corrections_found = []
        indicators = []
        
        for pattern in correction_patterns:
            if pattern in text_lower:
                corrections_found.append(pattern)
                indicators.append("Contains correction/update notice")
        
        return {
            'has_corrections': len(corrections_found) > 0,
            'correction_count': len(corrections_found),
            'patterns_found': corrections_found,
            'indicators': indicators,
            'missing': [] if corrections_found else ["No correction policy visible"],
            'score': 100 if corrections_found else 50  # Not finding corrections isn't necessarily bad
        }
    
    def _analyze_author_transparency(self, text: str, author: str) -> Dict[str, Any]:
        """Analyze author-related transparency"""
        
        indicators = []
        missing = []
        
        if author:
            indicators.append("Author identified")
            
            # Check for author credentials in text
            if any(word in text.lower() for word in ['reporter', 'correspondent', 'journalist', 'editor']):
                indicators.append("Author credentials mentioned")
            else:
                missing.append("Author credentials not mentioned")
        else:
            missing.append("No author identified")
        
        # Check for contact information
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
            indicators.append("Contact information provided")
        else:
            missing.append("No contact information")
        
        score = len(indicators) * 25
        
        return {
            'author_present': bool(author),
            'indicators': indicators,
            'missing': missing,
            'score': min(100, score)
        }
    
    def _analyze_methodology(self, text: str) -> Dict[str, Any]:
        """Analyze methodology transparency"""
        
        methodology_indicators = [
            'survey', 'poll', 'study', 'research', 'data collected',
            'methodology', 'sample size', 'margin of error', 'confidence interval'
        ]
        
        text_lower = text.lower()
        found_indicators = []
        indicators = []
        missing = []
        
        for indicator in methodology_indicators:
            if indicator in text_lower:
                found_indicators.append(indicator)
                indicators.append(f"Methodology element: {indicator}")
        
        # Check for statistical information
        if re.search(r'\d+%|\d+\s*percent', text):
            indicators.append("Statistical data presented")
        
        if not found_indicators and ('study' in text_lower or 'research' in text_lower):
            missing.append("Study methodology not explained")
        
        score = min(100, len(found_indicators) * 20)
        
        return {
            'methodology_elements': found_indicators,
            'element_count': len(found_indicators),
            'indicators': indicators,
            'missing': missing,
            'score': score
        }
    
    def _calculate_transparency_score(self, components: Dict[str, Any]) -> int:
        """Calculate overall transparency score"""
        
        # Weight different components
        weights = {
            'source_attribution': 0.3,
            'disclosures': 0.25,
            'author_transparency': 0.2,
            'methodology': 0.15,
            'corrections': 0.1
        }
        
        total_score = 0
        for component_name, weight in weights.items():
            component_score = components.get(component_name, {}).get('score', 0)
            total_score += component_score * weight
        
        return min(100, int(total_score))
    
    def _get_transparency_level(self, score: int) -> str:
        """Convert score to transparency level"""
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
        """Generate findings based on transparency analysis"""
        findings = []
        
        # Overall assessment
        if overall_score >= 80:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': f'Excellent transparency ({overall_score}/100)',
                'explanation': 'Article provides comprehensive transparency information'
            })
        elif overall_score >= 50:
            findings.append({
                'type': 'info',
                'severity': 'medium',
                'text': f'Good transparency ({overall_score}/100)',
                'explanation': 'Article provides adequate transparency information'
            })
        else:
            findings.append({
                'type': 'warning',
                'severity': 'medium',
                'text': f'Poor transparency ({overall_score}/100)',
                'explanation': 'Article lacks important transparency information'
            })
        
        # Source attribution findings
        source_data = components['source_attribution']
        if source_data['source_count'] >= 3:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': f"Multiple sources cited ({source_data['source_count']})",
                'explanation': 'Article cites multiple sources for verification'
            })
        elif source_data['source_count'] == 0:
            findings.append({
                'type': 'warning',
                'severity': 'high',
                'text': 'No sources cited',
                'explanation': 'Article lacks proper source attribution'
            })
        
        # Disclosure findings
        disclosure_data = components['disclosures']
        if disclosure_data['has_disclosures']:
            types = ', '.join(disclosure_data['types_found'])
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': f'Disclosures present: {types}',
                'explanation': 'Article includes transparency disclosures'
            })
        
        # Author transparency
        author_data = components['author_transparency']
        if not author_data['author_present']:
            findings.append({
                'type': 'warning',
                'severity': 'medium',
                'text': 'No author identified',
                'explanation': 'Article lacks author attribution'
            })
        
        return findings
    
    def _generate_summary(self, components: Dict[str, Any], score: int, level: str) -> str:
        """Generate summary of transparency analysis"""
        
        if score >= 80:
            base = "This article demonstrates excellent transparency practices. "
        elif score >= 65:
            base = "This article shows good transparency with most elements present. "
        elif score >= 50:
            base = "This article provides fair transparency with some missing elements. "
        else:
            base = "This article has poor transparency and lacks important disclosure information. "
        
        # Add specific details
        source_count = components['source_attribution']['source_count']
        if source_count > 0:
            base += f"Cites {source_count} sources. "
        
        if components['disclosures']['has_disclosures']:
            base += "Contains disclosure statements. "
        
        if components['author_transparency']['author_present']:
            base += "Author identified. "
        
        base += f"Overall transparency score: {score}/100."
        
        return base
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        info = super().get_service_info()
        info.update({
            'capabilities': [
                'Source attribution analysis',
                'Disclosure statement detection',
                'Author transparency assessment',
                'Methodology transparency evaluation',
                'Correction policy analysis',
                'Statistical transparency verification',
                'BULLETPROOF AI-enhanced transparency assessment'
            ],
            'transparency_elements': [
                'source_attribution',
                'disclosures',
                'corrections',
                'author_transparency',
                'methodology'
            ],
            'ai_enhanced': self._ai_available
        })
        return info
