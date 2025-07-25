# FILE: services/manipulation_detector.py
"""
services/manipulation_detector.py - Manipulation detection service
"""

import re
from typing import Dict, List, Any

class ManipulationDetector:
    """Detect manipulation tactics in articles"""
    
    def __init__(self):
        self.manipulation_patterns = {
            'fear_mongering': [
                'catastrophe', 'disaster', 'crisis', 'threat', 'danger',
                'destroy', 'devastate', 'collapse', 'nightmare'
            ],
            'emotional_manipulation': [
                'shocking', 'outrageous', 'disgusting', 'horrifying',
                'unbelievable', 'jaw-dropping', 'mind-blowing'
            ],
            'false_urgency': [
                'act now', 'limited time', 'don\'t wait', 'expires soon',
                'last chance', 'hurry', 'immediately'
            ],
            'loaded_language': [
                'radical', 'extreme', 'far-left', 'far-right',
                'socialist', 'fascist', 'communist', 'nazi'
            ]
        }
    
    def analyze_persuasion(self, text: str, title: str = '') -> Dict[str, Any]:
        """Analyze persuasion tactics in text"""
        full_text = (text + ' ' + title).lower()
        
        tactics_found = []
        total_score = 0
        
        # Check for each manipulation type
        for tactic_type, keywords in self.manipulation_patterns.items():
            found_keywords = [kw for kw in keywords if kw in full_text]
            if found_keywords:
                tactics_found.append({
                    'type': tactic_type,
                    'keywords': found_keywords,
                    'count': len(found_keywords)
                })
                total_score += len(found_keywords) * 10
        
        # Check for ALL CAPS (shouting)
        caps_words = len(re.findall(r'\b[A-Z]{4,}\b', text))
        if caps_words > 3:
            tactics_found.append({
                'type': 'excessive_capitalization',
                'count': caps_words
            })
            total_score += caps_words * 5
        
        # Check for excessive punctuation
        excessive_punct = len(re.findall(r'[!?]{2,}', text))
        if excessive_punct > 0:
            tactics_found.append({
                'type': 'excessive_punctuation',
                'count': excessive_punct
            })
            total_score += excessive_punct * 5
        
        return {
            'persuasion_score': min(100, total_score),
            'tactics_found': tactics_found,
            'manipulation_level': self._get_manipulation_level(total_score)
        }
    
    def _get_manipulation_level(self, score: int) -> str:
        """Determine manipulation level based on score"""
        if score >= 70:
            return 'High'
        elif score >= 40:
            return 'Moderate'
        elif score >= 20:
            return 'Low'
        else:
            return 'Minimal'
