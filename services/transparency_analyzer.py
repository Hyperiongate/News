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
    
    def _analyze_text_only(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform text-only analysis when web checks are disabled"""
        text = data.get('text', '')
        if not text:
            return self.get_error_result("No text provided for transparency analysis")
        
        # Perform the standard analysis without any web components
        return self.analyze({**data, '_skip_web_components': True})
    
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
            # Skip web checks if configured - PATCHED
            if self.config.options.get('skip_web_checks', False):
                # Do only text-based analysis, no web requests
                return self._analyze_text_only(data)
            
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
                r'(?:a |the )?(?:New York Times|Washington Post|CNN|BBC|Reuters|AP|Bloomberg|Guardian)',
                r'(?:told|said to|confirmed to) (?:reporters|this publication|our correspondent)'
            ]
            
            sources_found = 0
            for pattern in source_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                sources_found += len(matches)
            
            if sources_found > 5:
                transparency_score += 30
                indicators.append(f'Multiple sources cited ({sources_found} references)')
            elif sources_found > 2:
                transparency_score += 20
                indicators.append(f'Some sources cited ({sources_found} references)')
            elif sources_found > 0:
                transparency_score += 10
                indicators.append(f'Limited sources cited ({sources_found} references)')
            else:
                missing_elements.append('No source citations found')
                transparency_score -= 10
            
            # 3. Direct Quotes (10 points)
            quote_pattern = r'"[^"]{20,}"'
            quotes = re.findall(quote_pattern, text)
            quote_count = len(quotes)
            
            if quote_count > 3:
                transparency_score += 10
                indicators.append(f'Includes direct quotes ({quote_count} found)')
            elif quote_count > 0:
                transparency_score += 5
                indicators.append(f'Some direct quotes ({quote_count} found)')
            else:
                missing_elements.append('No direct quotes from sources')
            
            # 4. Data/Statistics Attribution (10 points)
            stat_patterns = [
                r'\d+(?:\.\d+)?\s*(?:percent|%)',
                r'\d+\s*(?:million|billion|thousand)',
                r'(?:survey|poll|study) of \d+',
                r'(?:increase|decrease|growth|decline) of \d+'
            ]
            
            stats_found = 0
            for pattern in stat_patterns:
                stats_found += len(re.findall(pattern, text, re.IGNORECASE))
            
            if stats_found > 0:
                # Check if stats have sources
                stat_with_source = 0
                for i, pattern in enumerate(stat_patterns):
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        # Check if source mentioned within 100 chars
                        context = text[max(0, match.start()-100):match.end()+100]
                        if any(src in context.lower() for src in ['according', 'report', 'study', 'survey', 'data from']):
                            stat_with_source += 1
                
                if stat_with_source > stats_found * 0.5:
                    transparency_score += 10
                    indicators.append('Statistics include source attribution')
                else:
                    transparency_score += 3
                    missing_elements.append('Statistics lack source attribution')
            
            # 5. Disclosure Statements (15 points)
            disclosure_patterns = [
                r'(?:disclosure|disclaimer):\s*[^.]+',
                r'(?:the author|I|we) (?:work|worked|consult|consulted) (?:for|with|at)',
                r'(?:conflict of interest|financial interest)',
                r'(?:funded by|sponsored by|supported by)',
                r'(?:affiliate link|commission|compensated)',
                r'(?:own|hold|bought) (?:shares|stock|position)'
            ]
            
            for pattern in disclosure_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                disclosures.extend(matches)
            
            if disclosures:
                transparency_score += 15
                indicators.append(f'Includes disclosure statements ({len(disclosures)} found)')
            
            # 6. Contact Information (5 points)
            contact_patterns = [
                r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                r'(?:contact|reach|email) (?:us|me|the author) at',
                r'(?:twitter|facebook|linkedin)\.com/[a-zA-Z0-9_]+',
                r'for (?:corrections|questions|more information)'
            ]
            
            contact_found = any(re.search(pattern, text, re.IGNORECASE) for pattern in contact_patterns)
            if contact_found:
                transparency_score += 5
                indicators.append('Contact information provided')
            else:
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
                            indicators.append(f"AI verified: {strength}")
                            transparency_score = min(100, transparency_score + 3)
                    
                    # Check for potential conflicts
                    if ai_transparency.get('potential_conflicts'):
                        missing_elements.extend(ai_transparency['potential_conflicts'][:1])
                        transparency_score = max(0, transparency_score - 10)
                    
                    # Check for sponsored content
                    if ai_transparency.get('sponsorship_indicators'):
                        missing_elements.append("Possible undisclosed sponsored content")
                        transparency_score = max(0, transparency_score - 15)
            
            # Generate summary and level
            level = self._get_transparency_level(transparency_score)
            assessment = self._generate_assessment(transparency_score, indicators, missing_elements)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(missing_elements, transparency_score)
            
            return {
                'service': self.service_name,
                'success': True,
                'data': {
                    'score': transparency_score,
                    'level': level,
                    'findings': self._generate_findings(transparency_score, indicators, missing_elements),
                    'summary': f"{assessment}",
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
            recommendations.append('Consider adding disclosure statements for any potential conflicts')
        
        return recommendations[:3]  # Top 3 recommendations
    
    def _get_transparency_level(self, score: int) -> str:
        """Convert transparency score to level"""
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
    
    def _generate_findings(self, score: int, indicators: List[str], missing: List[str]) -> List[Dict[str, Any]]:
        """Generate structured findings"""
        findings = []
        
        # Add positive findings
        if score >= 65:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': 'Strong transparency practices',
                'explanation': f'{len(indicators)} transparency indicators found'
            })
        
        # Add missing element warnings
        for element in missing[:3]:  # Top 3 issues
            severity = 'high' if score < 50 else 'medium'
            findings.append({
                'type': 'warning',
                'severity': severity,
                'text': element,
                'explanation': 'Reduces article transparency'
            })
        
        # Add overall assessment
        if score < 35:
            findings.append({
                'type': 'critical',
                'severity': 'high',
                'text': 'Severe transparency issues',
                'explanation': 'Article lacks basic transparency elements'
            })
        
        return findings
    
    def _generate_assessment(self, score: int, indicators: List[str], missing: List[str]) -> str:
        """Generate transparency assessment summary"""
        if score >= 80:
            return f"Excellent transparency with {len(indicators)} positive indicators including clear attribution and sourcing."
        elif score >= 65:
            return f"Good transparency practices with {len(indicators)} indicators, though some elements could be improved."
        elif score >= 50:
            return f"Fair transparency with {len(indicators)} indicators present but {len(missing)} important elements missing."
        elif score >= 35:
            return f"Poor transparency with only {len(indicators)} indicators found and significant gaps in disclosure."
        else:
            return f"Very poor transparency with {len(missing)} critical elements missing, raising credibility concerns."
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about the service"""
        info = super().get_service_info()
        info.update({
            'capabilities': [
                'Author attribution analysis',
                'Source citation detection',
                'Quote extraction and analysis',
                'Statistical claim verification',
                'Disclosure statement detection',
                'Contact information checking',
                'Methodology transparency',
                'External reference tracking',
                'AI-ENHANCED transparency assessment',
                'AI-powered conflict detection'
            ],
            'transparency_factors': {
                'author_attribution': 20,
                'source_citations': 30,
                'direct_quotes': 10,
                'data_attribution': 10,
                'disclosures': 15,
                'contact_info': 5,
                'methodology': 10
            },
            'ai_enhanced': self._ai_available
        })
        return info
