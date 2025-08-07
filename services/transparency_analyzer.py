"""
FILE: services/transparency_analyzer.py
PURPOSE: Transparency analysis service
REFACTORED: Now inherits from BaseAnalyzer for new architecture
"""

import re
import logging
from typing import Dict, Any, Optional
from services.base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)


class LegacyTransparencyAnalyzer:
    """Analyze transparency in news articles"""
    
    def analyze(self, text: str, author: Optional[str] = None) -> Dict[str, Any]:
        """Analyze transparency indicators in text"""
        transparency_score = 50  # Base score
        indicators = []
        
        # Check for author attribution
        if author:
            transparency_score += 15
            indicators.append('Has author attribution')
        else:
            indicators.append('Missing author attribution')
        
        # Check for source citations
        source_patterns = [
            r'according to',
            r'sources? (?:said|told|confirmed)',
            r'reported by',
            r'cited',
            r'study by',
            r'research (?:from|by)',
            r'data from',
            r'survey conducted by'
        ]
        
        sources_found = 0
        for pattern in source_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            sources_found += len(matches)
        
        if sources_found > 0:
            transparency_score += min(sources_found * 5, 25)
            indicators.append(f'Found {sources_found} source citations')
        else:
            indicators.append('No source citations found')
        
        # Check for direct quotes
        quote_count = text.count('"')
        if quote_count >= 4:  # At least 2 quoted sections
            transparency_score += 10
            indicators.append('Contains direct quotes')
        
        # Check for data/statistics with sources
        data_pattern = r'\d+\s*(?:percent|%|million|billion).*?(?:according to|source:|from)'
        if re.search(data_pattern, text, re.IGNORECASE):
            transparency_score += 10
            indicators.append('Statistics include sources')
        
        # Check for disclosure statements
        disclosure_patterns = [
            r'disclosure:',
            r'disclaimer:',
            r'conflict of interest',
            r'funded by',
            r'sponsored by'
        ]
        
        for pattern in disclosure_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                transparency_score += 5
                indicators.append('Contains disclosure statement')
                break
        
        # Ensure score is within bounds
        transparency_score = min(100, max(0, transparency_score))
        
        return {
            'transparency_score': transparency_score,
            'indicators': indicators,
            'sources_cited': sources_found,
            'has_author': bool(author),
            'has_quotes': quote_count >= 4,
            'transparency_level': self._get_transparency_level(transparency_score)
        }
    
    def _get_transparency_level(self, score: int) -> str:
        """Determine transparency level based on score"""
        if score >= 80:
            return 'High'
        elif score >= 60:
            return 'Good'
        elif score >= 40:
            return 'Moderate'
        else:
            return 'Low'


# ============= NEW REFACTORED CLASS =============

class TransparencyAnalyzer(BaseAnalyzer):
    """Transparency analysis service that inherits from BaseAnalyzer"""
    
    def __init__(self):
        super().__init__('transparency_analyzer')
        try:
            self._legacy = LegacyTransparencyAnalyzer()
            logger.info("Legacy TransparencyAnalyzer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize legacy TransparencyAnalyzer: {e}")
            self._legacy = None
    
    def _check_availability(self) -> bool:
        """Check if the service is available"""
        return self._legacy is not None
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze transparency using the standardized interface
        
        Expected input:
            - text: Article text to analyze
            - author: (optional) Author name for attribution check
            
        Returns:
            Standardized response with transparency analysis
        """
        # Validate input
        if not self.is_available:
            return self.get_default_result()
        
        text = data.get('text')
        if not text:
            return self.get_error_result("Missing required field: 'text'")
        
        # Get optional author
        author = data.get('author')
        
        return self._analyze_transparency(text, author)
    
    def _analyze_transparency(self, text: str, author: Optional[str] = None) -> Dict[str, Any]:
        """Analyze transparency indicators"""
        try:
            # Use legacy method
            result = self._legacy.analyze(text, author)
            
            # Transform to standardized format
            return {
                'service': self.service_name,
                'success': True,
                'data': {
                    'transparency_score': result.get('transparency_score', 50),
                    'transparency_level': result.get('transparency_level', 'Unknown'),
                    'indicators': result.get('indicators', []),
                    'sources_cited': result.get('sources_cited', 0),
                    'has_author': result.get('has_author', False),
                    'has_quotes': result.get('has_quotes', False),
                    'analysis_details': {
                        'author_provided': bool(author),
                        'author_name': author if author else 'Not provided',
                        'citation_count': result.get('sources_cited', 0),
                        'has_disclosure': any('disclosure' in ind.lower() for ind in result.get('indicators', []))
                    }
                },
                'metadata': {
                    'indicators_found': len(result.get('indicators', []))
                }
            }
            
        except Exception as e:
            logger.error(f"Transparency analysis failed: {e}")
            return self.get_error_result(str(e))
    
    def analyze_transparency(self, text: str, author: Optional[str] = None) -> Dict[str, Any]:
        """Legacy compatibility method"""
        return self.analyze({'text': text, 'author': author})
