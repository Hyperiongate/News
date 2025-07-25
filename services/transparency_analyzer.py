
# FILE: services/transparency_analyzer.py
"""
services/transparency_analyzer.py - Transparency analysis service
"""

import re
from typing import Dict, Any, Optional

class TransparencyAnalyzer:
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
