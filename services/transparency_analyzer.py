"""
Transparency Analyzer Service - AI ENHANCED VERSION
Analyzes transparency indicators in news articles with AI insights
"""

import re
import logging
from typing import Dict, Any, Optional, List
from services.base_analyzer import BaseAnalyzer
from services.ai_enhancement_mixin import AIEnhancementMixin

logger = logging.getLogger(__name__)


class TransparencyAnalyzer(BaseAnalyzer, AIEnhancementMixin):
    """Analyze transparency in news articles WITH AI ENHANCEMENT"""
    
    def __init__(self):
        super().__init__('transparency_analyzer')
        AIEnhancementMixin.__init__(self)
        logger.info(f"TransparencyAnalyzer initialized with AI enhancement: {self._ai_available}")
    
    def _check_availability(self) -> bool:
        """Service is always available"""
        return True
    
    def _ai_assess_transparency(self, text: str, initial_findings: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """AI method to assess transparency - calls the mixin's AI method"""
        try:
            if hasattr(self, '_ai_analyze_transparency') and self._ai_available:
                # Prepare data in the format expected by the mixin
                transparency_data = {
                    'indicators': initial_findings.get('indicators', []),
                    'source_count': initial_findings.get('source_count', 0),
                    'quote_count': initial_findings.get('quote_count', 0),
                    'has_disclosures': initial_findings.get('has_disclosures', False)
                }
                
                article_data = {
                    'title': initial_findings.get('title', 'Unknown'),
                    'author': initial_findings.get('author', 'Unknown'),
                    'source': initial_findings.get('source', 'Unknown')
                }
                
                # Call the mixin's AI method with proper parameters
                ai_result = self._ai_analyze_transparency(transparency_data, article_data)
                
                if ai_result:
                    # Transform the result to match what the analyze method expects
                    transformed_result = {
                        'hidden_issues': [],
                        'transparency_strengths': [],
                        'potential_conflicts': [],
                        'sponsorship_indicators': False
                    }
                    
                    # Extract issues from AI result
                    if ai_result.get('disclosure_issues'):
                        transformed_result['hidden_issues'] = ai_result['disclosure_issues'][:2]
                    
                    if ai_result.get('transparency_gaps'):
                        transformed_result['hidden_issues'].extend(ai_result['transparency_gaps'][:2])
                    
                    # Extract strengths
                    if ai_result.get('attribution_quality') == 'high':
                        transformed_result['transparency_strengths'].append('Strong source attribution')
                    
                    # Check for conflicts
                    if ai_result.get('trust_impact') and 'conflict' in str(ai_result.get('trust_impact', '')).lower():
                        transformed_result['potential_conflicts'] = ['Possible undisclosed conflict of interest']
                    
                    # Check for sponsorship
                    if any('sponsor' in issue.lower() or 'funding' in issue.lower() 
                           for issue in ai_result.get('disclosure_issues', [])):
                        transformed_result['sponsorship_indicators'] = True
                    
                    return transformed_result
                
        except Exception as e:
            logger.warning(f"AI transparency assessment failed: {e}")
        
        return None
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze transparency indicators in article WITH AI ENHANCEMENT
        
        Expected input:
            - text: Article text to analyze
            - author: (optional) Author name
            - domain: (optional) Source domain
            
        Returns:
            Standardized response with transparency analysis
        """
        try:
            text = data.get('text', '')
            if not text:
                return self.get_error_result("No text provided for transparency analysis")
            
            author = data.get('author')
            domain = data.get('domain', '')
            
            # Perform analysis
            transparency_score = 50  # Base score
            indicators = []
            missing_elements = []
            disclosures = []
            
            # 1. Author Attribution (20 points)
            if author and author.lower() not in ['unknown', 'staff', 'editor', 'admin']:
                transparency_score += 20
                indicators.append('Clear author attribution')
            else:
                missing_elements.append('No clear author attribution')
                transparency_score -= 10
            
            # 2. Source Citations (up to 30 points)
            source_patterns = [
                r'according to [\w\s]+',
                r'(?:said|told|confirmed) [\w\s]+ (?:in an? (?:interview|statement|report))',
                r'(?:reported by|cited by) [\w\s]+',
                r'(?:study|research|report) (?:by|from) [\w\s]+',
                r'data from [\w\s]+',
                r'survey conducted by [\w\s]+',
                r'(?:based on|derived from) [\w\s]+'
            ]
            
            sources_found = 0
            source_examples = []
            for pattern in source_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                sources_found += len(matches)
                if matches:
                    source_examples.extend(matches[:2])  # Keep first 2 examples
            
            if sources_found > 0:
                points = min(sources_found * 5, 30)
                transparency_score += points
                indicators.append(f'Found {sources_found} source citations')
                if source_examples:
                    indicators.append(f'Examples: {", ".join(source_examples[:3])}')
            else:
                missing_elements.append('No source citations found')
                transparency_score -= 15
            
            # 3. Direct Quotes (15 points)
            quote_pattern = r'"[^"]{20,}"'  # Quotes with at least 20 characters
            quotes = re.findall(quote_pattern, text)
            quote_count = len(quotes)
            
            if quote_count >= 2:
                transparency_score += 15
                indicators.append(f'Contains {quote_count} direct quotes')
            elif quote_count == 1:
                transparency_score += 7
                indicators.append('Contains 1 direct quote')
            else:
                missing_elements.append('No direct quotes from sources')
            
            # 4. Data/Statistics with Sources (15 points)
            data_pattern = r'(\d+(?:\.\d+)?%?)\s*(?:of|from|according to|based on|source:)\s*([\w\s]+)'
            data_matches = re.findall(data_pattern, text, re.IGNORECASE)
            
            if data_matches:
                transparency_score += 15
                indicators.append(f'Statistics include sources ({len(data_matches)} instances)')
            else:
                # Check for unsourced statistics
                unsourced_stats = re.findall(r'\d+(?:\.\d+)?%', text)
                if len(unsourced_stats) > 2:
                    missing_elements.append('Statistics lack source attribution')
                    transparency_score -= 10
            
            # 5. Disclosure Statements (10 points)
            disclosure_patterns = [
                r'disclosure:\s*[^.]+',
                r'disclaimer:\s*[^.]+',
                r'conflict of interest:\s*[^.]+',
                r'funded by\s*[^.]+',
                r'sponsored by\s*[^.]+',
                r'correction:\s*[^.]+',
                r'update:\s*[^.]+'
            ]
            
            for pattern in disclosure_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    transparency_score += 10
                    disclosures.extend(matches)
                    indicators.append('Contains disclosure statements')
                    break
            
            # 6. Contact Information (5 points)
            contact_patterns = [
                r'contact (?:us|me|the author) at',
                r'email:?\s*[\w\.-]+@[\w\.-]+',
                r'reach out (?:at|to)',
                r'for more information'
            ]
            
            has_contact = False
            for pattern in contact_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    transparency_score += 5
                    indicators.append('Provides contact information')
                    has_contact = True
                    break
            
            if not has_contact:
                missing_elements.append('No contact information provided')
            
            # 7. Methodology (10 points for investigative pieces)
            methodology_keywords = ['methodology', 'how we', 'our investigation', 'we analyzed', 'we reviewed']
            if any(keyword in text.lower() for keyword in methodology_keywords):
                transparency_score += 10
                indicators.append('Explains methodology or process')
            
            # 8. External Links/References (5 points)
            url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
            urls = re.findall(url_pattern, text)
            if urls:
                transparency_score += 5
                indicators.append(f'Includes {len(urls)} external references')
            
            # Ensure score is within bounds
            transparency_score = max(0, min(100, transparency_score))
            
            # AI ENHANCEMENT - Add deeper transparency insights
            if self._ai_available and text:
                logger.info("Enhancing transparency analysis with AI")
                
                # Prepare initial findings for AI assessment
                initial_findings = {
                    'author': author,
                    'source': domain,
                    'title': data.get('title', 'Unknown'),
                    'author_provided': bool(author),
                    'source_count': sources_found,
                    'quote_count': quote_count,
                    'has_disclosures': len(disclosures) > 0,
                    'transparency_score': transparency_score,
                    'indicators': indicators
                }
                
                # Get AI transparency assessment
                ai_transparency = self._ai_assess_transparency(
                    text=text[:2000],  # Limit text for API
                    initial_findings=initial_findings
                )
                
                if ai_transparency:
                    # Add AI-detected transparency issues
                    if ai_transparency.get('hidden_issues'):
                        for issue in ai_transparency['hidden_issues'][:2]:
                            missing_elements.append(f"AI detected: {issue}")
                            transparency_score = max(0, transparency_score - 5)
                    
                    # Add AI-found transparency strengths
                    if ai_transparency.get('transparency_strengths'):
                        for strength in ai_transparency['transparency_strengths'][:2]:
                            indicators.append(f"AI noted: {strength}")
                    
                    # Check for conflicts of interest AI might detect
                    if ai_transparency.get('potential_conflicts'):
                        missing_elements.append(f"Potential conflict: {ai_transparency['potential_conflicts'][0]}")
                        transparency_score = max(0, transparency_score - 10)
                    
                    # Check for hidden sponsorship patterns
                    if ai_transparency.get('sponsorship_indicators'):
                        missing_elements.append("AI detected possible undisclosed sponsorship")
                        transparency_score = max(0, transparency_score - 15)
            
            # Recalculate score bounds after AI adjustments
            transparency_score = max(0, min(100, transparency_score))
            
            # Determine transparency level
            if transparency_score >= 80:
                level = 'Excellent'
                assessment = 'Very transparent with clear sourcing and attribution'
            elif transparency_score >= 65:
                level = 'Good'
                assessment = 'Generally transparent with most key elements present'
            elif transparency_score >= 50:
                level = 'Moderate'
                assessment = 'Some transparency but missing important elements'
            elif transparency_score >= 35:
                level = 'Low'
                assessment = 'Limited transparency with many missing elements'
            else:
                level = 'Very Low'
                assessment = 'Lacks basic transparency standards'
            
            # Generate findings for UI
            findings = []
            
            # Add positive findings
            if transparency_score >= 65:
                findings.append({
                    'type': 'transparency',
                    'severity': 'positive',
                    'text': f'Good transparency practices: {", ".join(indicators[:2])}',
                    'finding': 'Strong transparency'
                })
            
            # Add negative findings
            if missing_elements:
                severity = 'high' if len(missing_elements) > 3 else 'medium'
                findings.append({
                    'type': 'transparency',
                    'severity': severity,
                    'text': f'Missing: {", ".join(missing_elements[:2])}',
                    'finding': 'Transparency issues'
                })
            
            # Add AI-specific findings if enhanced
            if self._ai_available and any('AI' in elem for elem in missing_elements + indicators):
                findings.append({
                    'type': 'transparency',
                    'severity': 'info',
                    'text': 'AI analysis provided additional transparency insights',
                    'finding': 'AI-enhanced analysis'
                })
            
            # Generate recommendations
            recommendations = self._generate_recommendations(missing_elements, transparency_score)
            
            return {
                'service': self.service_name,
                'success': True,
                'data': {
                    'score': transparency_score,
                    'level': level,
                    'findings': findings,
                    'assessment': assessment,
                    'summary': f"Transparency score: {transparency_score}%. {assessment}",
                    'indicators': indicators,
                    'missing_elements': missing_elements,
                    'disclosures': disclosures,
                    'recommendations': recommendations,
                    'transparency_score': transparency_score,  # For backward compatibility
                    'transparency_level': level,  # For backward compatibility
                    'sources_cited': sources_found,
                    'has_author': bool(author),
                    'has_quotes': quote_count > 0,
                    'details': {
                        'author_provided': bool(author),
                        'quote_count': quote_count,
                        'source_count': sources_found,
                        'has_methodology': any(keyword in text.lower() for keyword in methodology_keywords),
                        'has_disclosures': len(disclosures) > 0,
                        'external_links': len(urls) if 'urls' in locals() else 0
                    }
                },
                'metadata': {
                    'indicators_found': len(indicators),
                    'issues_found': len(missing_elements),
                    'ai_enhanced': self._ai_available,
                    'ai_insights_added': self._ai_available and any('AI' in elem for elem in missing_elements + indicators)
                }
            }
            
        except Exception as e:
            logger.error(f"Transparency analysis failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _generate_recommendations(self, missing_elements: List[str], score: int) -> List[str]:
        """Generate specific recommendations based on missing elements"""
        recommendations = []
        
        if 'No clear author attribution' in missing_elements:
            recommendations.append('Add clear author byline with full name and credentials')
        
        if 'No source citations found' in missing_elements:
            recommendations.append('Include specific sources for all claims and data')
        
        if 'No direct quotes from sources' in missing_elements:
            recommendations.append('Add direct quotes from named sources to support claims')
        
        if 'Statistics lack source attribution' in missing_elements:
            recommendations.append('Provide sources for all statistics and data points')
        
        if 'No contact information provided' in missing_elements:
            recommendations.append('Include contact information for corrections or questions')
        
        if score < 50:
            recommendations.append('Consider adding disclosure statements about funding or conflicts')
        
        # Add AI-specific recommendations if detected
        ai_issues = [elem for elem in missing_elements if 'AI detected' in elem]
        if ai_issues:
            recommendations.append('Address subtle transparency issues identified by AI analysis')
        
        return recommendations
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        info = super().get_service_info()
        info.update({
            'capabilities': [
                'Author attribution checking',
                'Source citation analysis',
                'Direct quote detection',
                'Data source verification',
                'Disclosure statement identification',
                'Contact information detection',
                'Methodology transparency',
                'External reference tracking',
                'AI-ENHANCED transparency assessment',
                'AI-powered conflict detection',
                'Hidden sponsorship detection'
            ],
            'transparency_elements': 8,
            'scoring_range': '0-100',
            'ai_enhanced': self._ai_available
        })
        return info
