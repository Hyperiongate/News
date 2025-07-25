"""
services/clickbait_analyzer.py - Clickbait detection service
"""

import re
from typing import Dict, Any

class ClickbaitAnalyzer:
    """Analyze headlines for clickbait characteristics"""
    
    def __init__(self):
        self.clickbait_patterns = [
            # Curiosity gap
            r"you won't believe",
            r"what happened next",
            r"will shock you",
            r"will blow your mind",
            r"you'll never guess",
            
            # Numbered lists
            r"^\d+\s+(?:ways|things|reasons|facts)",
            r"top\s+\d+",
            
            # Extreme language
            r"(?:totally|completely|absolutely)\s+(?:destroyed|obliterated|annihilated)",
            r"epic fail",
            r"mind-blowing",
            r"jaw-dropping",
            
            # Direct address
            r"this is why you",
            r"here's why you",
            r"you need to",
            
            # Vague pronouns
            r"this (?:man|woman|person|kid)",
            r"what (?:he|she|they) did",
            
            # False claims
            r"doctors hate",
            r"one weird trick",
            r"companies don't want you to know"
        ]
    
    def analyze_headline(self, headline: str, article_text: str = '') -> int:
        """
        Analyze headline for clickbait score (0-100)
        
        Args:
            headline: Article headline
            article_text: Full article text (optional)
            
        Returns:
            Clickbait score from 0-100
        """
        if not headline:
            return 0
        
        score = 0
        headline_lower = headline.lower()
        
        # Check clickbait patterns
        for pattern in self.clickbait_patterns:
            if re.search(pattern, headline_lower):
                score += 15
        
        # Check for excessive punctuation
        if headline.count('!') > 0:
            score += 10
        if headline.count('?') > 1:
            score += 10
        
        # Check for ALL CAPS words
        caps_words = re.findall(r'\b[A-Z]{3,}\b', headline)
        if len(caps_words) > 0:
            score += len(caps_words) * 5
        
        # Check for emotional words
        emotional_words = ['shocking', 'amazing', 'incredible', 'unbelievable', 
                          'horrifying', 'stunning', 'explosive']
        for word in emotional_words:
            if word in headline_lower:
                score += 10
        
        # Check if headline asks a question that's immediately answered
        if '?' in headline and article_text:
            # Simple check: if headline is a question and article starts with "No" or "Yes"
            if article_text.strip().startswith(('No,', 'Yes,', 'No.', 'Yes.')):
                score += 20  # Betteridge's law of headlines
        
        # Check for hyperbolic numbers
        if re.search(r'\b\d{3,}\b', headline):  # 3+ digit numbers
            score += 5
        
        # Ensure score is within bounds
        return min(100, max(0, score))
