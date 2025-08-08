"""
Transparency Analyzer Service - COMPLETE IMPLEMENTATION
Analyzes transparency indicators in news articles
"""

import re
import logging
from typing import Dict, Any, Optional, List
from services.base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)


class TransparencyAnalyzer(BaseAnalyzer):
    """Analyze transparency in news articles"""
    
    def __init__(self):
        super().__init__('transparency_analyzer')
        logger.info("TransparencyAnalyzer initialized")
    
    def _check_availability(self) -> bool:
        """Service is always available"""
        return True
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze transparency indicators in article
        
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
            
            # Generate recommendations
            recommendations = self._generate_recommendations(missing_elements, transparency_score)
            
            return {
                'service': self.service_name,
                'success': True,
                'data': {
                    'score': transparency_score,
                    'level': level,
                    'assessment': assessment,
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
                    'issues_found': len(missing_elements)
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
        
        return recommendations
