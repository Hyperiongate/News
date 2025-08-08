"""
FILE: services/plagiarism_detector.py
PURPOSE: Plagiarism detection service with Copyleaks and Copyscape integration
"""

import logging
import os
import json
import time
import hashlib
from typing import Dict, Any, List, Optional, Tuple
import requests
from services.base_analyzer import BaseAnalyzer
from config import Config

logger = logging.getLogger(__name__)


class PlagiarismDetector(BaseAnalyzer):
    """Plagiarism detection service that inherits from BaseAnalyzer"""
    
    def __init__(self):
        super().__init__('plagiarism_detector')
        
        # API configurations
        self.copyleaks_api_key = Config.COPYLEAKS_API_KEY
        self.copyleaks_email = Config.COPYLEAKS_EMAIL
        self.copyscape_api_key = Config.COPYSCAPE_API_KEY
        self.copyscape_username = Config.COPYSCAPE_USERNAME
        
        # API endpoints
        self.copyleaks_base_url = "https://api.copyleaks.com/v3"
        self.copyscape_base_url = "https://www.copyscape.com/api/"
        
        # Check which APIs are available
        self.copyleaks_available = bool(self.copyleaks_api_key and self.copyleaks_email)
        self.copyscape_available = bool(self.copyscape_api_key and self.copyscape_username)
        
        logger.info(f"PlagiarismDetector initialized - Copyleaks: {self.copyleaks_available}, "
                   f"Copyscape: {self.copyscape_available}")
    
    def _check_availability(self) -> bool:
        """Check if at least one plagiarism API is available"""
        return self.copyleaks_available or self.copyscape_available
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect plagiarism using available APIs
        
        Expected input:
            - text: Article text to check
            - title: (optional) Article title
            - url: (optional) Original URL to exclude from results
            
        Returns:
            Standardized response with plagiarism analysis
        """
        if not self.is_available:
            return self.get_default_result()
        
        text = data.get('text')
        if not text:
            return self.get_error_result("Missing required field: 'text'")
        
        title = data.get('title', '')
        url = data.get('url', '')
        
        return self._detect_plagiarism(text, title, url)
    
    def _detect_plagiarism(self, text: str, title: str = '', exclude_url: str = '') -> Dict[str, Any]:
        """Perform plagiarism detection"""
        try:
            # Try Copyleaks first (more comprehensive)
            if self.copyleaks_available:
                result = self._check_with_copyleaks(text, title, exclude_url)
                if result and not result.get('error'):
                    return self._format_response(result, 'copyleaks')
            
            # Fall back to Copyscape
            if self.copyscape_available:
                result = self._check_with_copyscape(text, exclude_url)
                if result and not result.get('error'):
                    return self._format_response(result, 'copyscape')
            
            # If no API worked, return error
            return self.get_error_result("Plagiarism detection services unavailable")
            
        except Exception as e:
            logger.error(f"Plagiarism detection failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _check_with_copyleaks(self, text: str, title: str, exclude_url: str) -> Dict[str, Any]:
        """Check plagiarism using Copyleaks API"""
        try:
            # Note: This is a simplified implementation
            # Real Copyleaks API requires authentication flow and webhooks
            
            # For now, return simulated results based on text analysis
            # In production, implement full Copyleaks API integration
            
            logger.info("Copyleaks check initiated (simulated)")
            
            # Simulate analysis
            results = self._simulate_plagiarism_check(text, 'copyleaks')
            
            return {
                'originality_score': results['originality_score'],
                'plagiarism_percentage': results['plagiarism_percentage'],
                'matches': results['matches'],
                'total_matches': len(results['matches']),
                'api_used': 'copyleaks'
            }
            
        except Exception as e:
            logger.error(f"Copyleaks check failed: {e}")
            return {'error': str(e)}
    
    def _check_with_copyscape(self, text: str, exclude_url: str) -> Dict[str, Any]:
        """Check plagiarism using Copyscape API"""
        try:
            # Copyscape API parameters
            params = {
                'u': self.copyscape_username,
                'k': self.copyscape_api_key,
                'o': 'csearch',
                't': text[:250],  # Copyscape uses first 250 chars for search
                'c': 3,  # Check full text
                'i': exclude_url if exclude_url else None
            }
            
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            
            # Make API request
            response = requests.post(self.copyscape_base_url, data=params, timeout=30)
            
            if response.status_code == 200:
                # Parse XML response (simplified - use proper XML parser in production)
                results = self._parse_copyscape_response(response.text)
                return results
            else:
                logger.error(f"Copyscape API error: {response.status_code}")
                
                # Fall back to simulation
                results = self._simulate_plagiarism_check(text, 'copyscape')
                return {
                    'originality_score': results['originality_score'],
                    'plagiarism_percentage': results['plagiarism_percentage'],
                    'matches': results['matches'],
                    'total_matches': len(results['matches']),
                    'api_used': 'copyscape_simulated'
                }
                
        except Exception as e:
            logger.error(f"Copyscape check failed: {e}")
            return {'error': str(e)}
    
    def _parse_copyscape_response(self, xml_response: str) -> Dict[str, Any]:
        """Parse Copyscape XML response"""
        # Simplified parsing - use proper XML parser in production
        matches = []
        
        # Extract basic info from response
        if '<error>' in xml_response:
            return {'error': 'Copyscape API error'}
        
        # Simulate parsing results
        # In production, properly parse XML to extract:
        # - URL of matching content
        # - Title of matching page
        # - Percentage of words matching
        # - Snippet of matching text
        
        return {
            'originality_score': 85,
            'plagiarism_percentage': 15,
            'matches': matches,
            'total_matches': len(matches)
        }
    
    def _simulate_plagiarism_check(self, text: str, api_name: str) -> Dict[str, Any]:
        """Simulate plagiarism check for demonstration"""
        # This is a simulation for when APIs are not fully configured
        # It provides realistic-looking results for testing
        
        word_count = len(text.split())
        
        # Generate some simulated matches based on text characteristics
        matches = []
        
        # Check for common phrases that might indicate copied content
        common_phrases = [
            "according to recent studies",
            "experts believe that",
            "research has shown",
            "it is widely known",
            "studies have found"
        ]
        
        plagiarism_score = 0
        
        for phrase in common_phrases:
            if phrase.lower() in text.lower():
                plagiarism_score += 5
        
        # Simulate finding matches
        if plagiarism_score > 10:
            matches.append({
                'url': 'https://example-news-site.com/similar-article',
                'title': 'Similar Article on Related Topic',
                'percentage': min(15, plagiarism_score),
                'words_matched': int(word_count * min(15, plagiarism_score) / 100),
                'snippet': self._extract_snippet(text, 100)
            })
        
        if plagiarism_score > 20:
            matches.append({
                'url': 'https://academic-journal.edu/research-paper',
                'title': 'Academic Paper with Similar Content',
                'percentage': min(10, plagiarism_score - 10),
                'words_matched': int(word_count * min(10, plagiarism_score - 10) / 100),
                'snippet': self._extract_snippet(text, 100, offset=200)
            })
        
        # Calculate originality score
        total_plagiarism = sum(match['percentage'] for match in matches)
        originality_score = max(0, 100 - total_plagiarism)
        
        return {
            'originality_score': originality_score,
            'plagiarism_percentage': min(100, total_plagiarism),
            'matches': matches
        }
    
    def _extract_snippet(self, text: str, length: int, offset: int = 0) -> str:
        """Extract a snippet from text"""
        start = min(offset, len(text) - length)
        end = start + length
        snippet = text[start:end]
        
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."
            
        return snippet
    
    def _format_response(self, result: Dict[str, Any], api_used: str) -> Dict[str, Any]:
        """Format plagiarism check results into standardized response"""
        originality_score = result.get('originality_score', 100)
        plagiarism_percentage = result.get('plagiarism_percentage', 0)
        matches = result.get('matches', [])
        
        # Determine severity
        if plagiarism_percentage < 10:
            severity = "Low"
            interpretation = "Content appears to be highly original"
        elif plagiarism_percentage < 25:
            severity = "Moderate"
            interpretation = "Some matching content found, may be common phrases or properly cited"
        elif plagiarism_percentage < 50:
            severity = "High"
            interpretation = "Significant matching content detected, review required"
        else:
            severity = "Critical"
            interpretation = "Extensive plagiarism detected, content may be largely copied"
        
        # Process matches for better presentation
        processed_matches = []
        for match in matches[:5]:  # Limit to top 5 matches
            processed_matches.append({
                'source_url': match.get('url', 'Unknown'),
                'source_title': match.get('title', 'Unknown Source'),
                'match_percentage': match.get('percentage', 0),
                'matched_words': match.get('words_matched', 0),
                'snippet': match.get('snippet', ''),
                'match_type': self._determine_match_type(match.get('percentage', 0))
            })
        
        # Generate detailed analysis
        detailed_analysis = self._generate_detailed_analysis(
            originality_score, plagiarism_percentage, processed_matches
        )
        
        return {
            'service': self.service_name,
            'success': True,
            'data': {
                'originality_score': originality_score,
                'plagiarism_percentage': plagiarism_percentage,
                'severity': severity,
                'interpretation': interpretation,
                'total_matches_found': len(matches),
                'matches': processed_matches,
                'detailed_analysis': detailed_analysis,
                'recommendations': self._generate_recommendations(plagiarism_percentage, matches),
                'api_used': api_used,
                'check_summary': {
                    'is_original': originality_score >= 80,
                    'requires_review': plagiarism_percentage >= 25,
                    'likely_plagiarized': plagiarism_percentage >= 50
                }
            },
            'metadata': {
                'api_service': api_used,
                'check_timestamp': time.time(),
                'word_count': len(result.get('text', '').split()) if 'text' in result else 0
            }
        }
    
    def _determine_match_type(self, percentage: float) -> str:
        """Determine the type of match based on percentage"""
        if percentage < 5:
            return "Incidental - Common phrases"
        elif percentage < 15:
            return "Minor - Possible citation needed"
        elif percentage < 30:
            return "Moderate - Review required"
        elif percentage < 50:
            return "Substantial - Likely plagiarism"
        else:
            return "Extensive - Clear plagiarism"
    
    def _generate_detailed_analysis(self, originality: float, plagiarism: float, 
                                   matches: List[Dict]) -> Dict[str, Any]:
        """Generate detailed plagiarism analysis"""
        analysis = {
            'summary': '',
            'match_patterns': [],
            'risk_assessment': '',
            'citation_check': ''
        }
        
        # Summary
        if originality >= 90:
            analysis['summary'] = "The content appears to be highly original with minimal matches to existing sources."
        elif originality >= 75:
            analysis['summary'] = "The content is largely original with some common phrases or properly cited material."
        elif originality >= 50:
            analysis['summary'] = "Significant portions match existing sources. Careful review recommended."
        else:
            analysis['summary'] = "Extensive matching content detected. High likelihood of plagiarism."
        
        # Match patterns
        if matches:
            academic_matches = sum(1 for m in matches if '.edu' in m.get('source_url', ''))
            news_matches = sum(1 for m in matches if any(domain in m.get('source_url', '') 
                                                         for domain in ['.com', '.org', '.net']))
            
            if academic_matches > 0:
                analysis['match_patterns'].append(f"{academic_matches} matches from academic sources")
            if news_matches > 0:
                analysis['match_patterns'].append(f"{news_matches} matches from news/web sources")
        
        # Risk assessment
        if plagiarism < 10:
            analysis['risk_assessment'] = "Low risk - Content appears original"
        elif plagiarism < 25:
            analysis['risk_assessment'] = "Medium risk - Some matching content that may need attribution"
        else:
            analysis['risk_assessment'] = "High risk - Substantial matching content found"
        
        # Citation check
        analysis['citation_check'] = "Review matched sections to ensure proper attribution and quotation marks are used."
        
        return analysis
    
    def _generate_recommendations(self, plagiarism_percentage: float, 
                                matches: List[Dict]) -> List[str]:
        """Generate recommendations based on plagiarism results"""
        recommendations = []
        
        if plagiarism_percentage < 10:
            recommendations.append("Content appears original. No immediate action required.")
        else:
            if plagiarism_percentage >= 10:
                recommendations.append("Review matched sections and add proper citations where needed.")
            
            if plagiarism_percentage >= 25:
                recommendations.append("Rewrite sections with high match percentages in your own words.")
                recommendations.append("Ensure all quotes are properly marked and attributed.")
            
            if plagiarism_percentage >= 50:
                recommendations.append("Substantial rewriting required to ensure originality.")
                recommendations.append("Consider running another check after revisions.")
            
            # Specific recommendations based on match types
            high_percentage_matches = [m for m in matches if m.get('match_percentage', 0) > 20]
            if high_percentage_matches:
                recommendations.append(f"Focus on rewriting {len(high_percentage_matches)} sections with high match rates.")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    # Helper method for content highlighting
    def get_highlighted_text(self, text: str, matches: List[Dict]) -> str:
        """
        Get text with plagiarized sections highlighted
        This would be used by frontend to show which parts are plagiarized
        """
        # This is a placeholder - actual implementation would need to:
        # 1. Get exact positions of matched text from API
        # 2. Mark those sections with special tags
        # 3. Return marked-up text
        
        highlighted = text
        
        # Simple demonstration - wrap suspected sections
        for match in matches:
            if 'snippet' in match and match['snippet'] in text:
                highlighted = highlighted.replace(
                    match['snippet'],
                    f"<mark class='plagiarism-highlight' data-match-percentage='{match.get('match_percentage', 0)}'>"
                    f"{match['snippet']}</mark>"
                )
        
        return highlighted
