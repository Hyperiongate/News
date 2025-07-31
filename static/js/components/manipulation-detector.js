"""
services/manipulation_detector.py - Manipulation detection service
FIXED: More nuanced scoring that doesn't easily hit 100%
"""
import re
from typing import Dict, List, Any

class ManipulationDetector:
    """Detect manipulation tactics in articles"""
    
    def __init__(self):
        # Enhanced manipulation patterns with severity weights
        self.manipulation_patterns = {
            'fear_mongering': {
                'keywords': [
                    'catastrophe', 'disaster', 'crisis', 'threat', 'danger',
                    'destroy', 'devastate', 'collapse', 'nightmare', 'apocalypse',
                    'terrifying', 'horrifying', 'deadly', 'fatal'
                ],
                'weight': 3,  # Reduced from 10
                'name': 'Fear Mongering',
                'description': 'Using fear-inducing language'
            },
            'emotional_manipulation': {
                'keywords': [
                    'shocking', 'outrageous', 'disgusting', 'horrifying',
                    'unbelievable', 'jaw-dropping', 'mind-blowing', 'heartbreaking',
                    'devastating', 'tragic', 'inspiring', 'miraculous'
                ],
                'weight': 2,  # Lower weight
                'name': 'Emotional Language',
                'description': 'Excessive emotional appeals'
            },
            'false_urgency': {
                'keywords': [
                    'act now', 'limited time', 'don\'t wait', 'expires soon',
                    'last chance', 'hurry', 'immediately', 'breaking', 'urgent',
                    'alert', 'warning', 'right now', 'before it\'s too late'
                ],
                'weight': 2.5,
                'name': 'False Urgency',
                'description': 'Creating artificial time pressure'
            },
            'loaded_language': {
                'keywords': [
                    'radical', 'extreme', 'far-left', 'far-right',
                    'socialist', 'fascist', 'communist', 'nazi', 'terrorist',
                    'thugs', 'mob', 'evil', 'corrupt', 'crooked'
                ],
                'weight': 4,  # Higher weight for more serious terms
                'name': 'Loaded Language',
                'description': 'Using charged political terms'
            },
            'absolutism': {
                'keywords': [
                    'always', 'never', 'every', 'all', 'none',
                    'completely', 'totally', 'absolutely', 'definitely',
                    'undeniable', 'irrefutable', 'proven'
                ],
                'weight': 1.5,  # Lower weight as these are common
                'name': 'Absolutist Claims',
                'description': 'Black-and-white thinking'
            },
            'conspiracy_rhetoric': {
                'keywords': [
                    'cover-up', 'coverup', 'hidden agenda', 'they don\'t want you to know',
                    'mainstream media won\'t tell', 'wake up', 'sheeple',
                    'deep state', 'globalist', 'new world order'
                ],
                'weight': 5,  # High weight for conspiracy language
                'name': 'Conspiracy Language',
                'description': 'Suggesting hidden plots'
            }
        }
    
    def analyze_persuasion(self, text: str, title: str = '') -> Dict[str, Any]:
        """Analyze persuasion tactics in text"""
        full_text = (text + ' ' + title).lower()
        word_count = len(full_text.split())
        
        tactics_found = []
        total_score = 0
        
        # Check for each manipulation type
        for tactic_type, tactic_info in self.manipulation_patterns.items():
            found_keywords = []
            
            # Use word boundaries for more accurate matching
            for keyword in tactic_info['keywords']:
                # Create pattern with word boundaries
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = re.findall(pattern, full_text, re.IGNORECASE)
                if matches:
                    found_keywords.append(keyword)
            
            if found_keywords:
                # Calculate score with diminishing returns
                keyword_count = len(found_keywords)
                
                # Base score calculation with diminishing returns
                if keyword_count == 1:
                    score = tactic_info['weight'] * 1.0
                elif keyword_count == 2:
                    score = tactic_info['weight'] * 1.5
                elif keyword_count == 3:
                    score = tactic_info['weight'] * 1.8
                else:
                    # Logarithmic growth for 4+ keywords
                    score = tactic_info['weight'] * (1.8 + (keyword_count - 3) * 0.1)
                
                # Adjust for article length (longer articles might naturally have more keywords)
                if word_count > 1000:
                    score *= 0.8  # Reduce score for longer articles
                elif word_count < 200:
                    score *= 1.2  # Increase score for short, punchy articles
                
                total_score += score
                
                # Determine severity
                if score < tactic_info['weight'] * 1.2:
                    severity = 'low'
                elif score < tactic_info['weight'] * 2:
                    severity = 'medium'
                else:
                    severity = 'high'
                
                tactics_found.append({
                    'type': tactic_type,
                    'name': tactic_info['name'],
                    'description': tactic_info['description'],
                    'keywords': found_keywords[:5],  # Limit displayed keywords
                    'count': keyword_count,
                    'severity': severity
                })
        
        # Check for ALL CAPS (shouting)
        caps_words = len(re.findall(r'\b[A-Z]{4,}\b', text))
        if caps_words > 3:
            caps_score = min(caps_words * 1.5, 10)  # Cap at 10 points
            tactics_found.append({
                'type': 'excessive_capitalization',
                'name': 'Excessive Capitalization',
                'description': 'Using ALL CAPS for emphasis',
                'count': caps_words,
                'severity': 'medium' if caps_words > 5 else 'low'
            })
            total_score += caps_score
        
        # Check for excessive punctuation
        excessive_punct = len(re.findall(r'[!?]{2,}', text))
        if excessive_punct > 0:
            punct_score = min(excessive_punct * 2, 8)  # Cap at 8 points
            tactics_found.append({
                'type': 'excessive_punctuation',
                'name': 'Excessive Punctuation',
                'description': 'Multiple exclamation/question marks',
                'count': excessive_punct,
                'severity': 'low'
            })
            total_score += punct_score
        
        # Check for clickbait patterns
        clickbait_patterns = [
            r'you won\'t believe',
            r'doctors hate',
            r'this one trick',
            r'what happened next',
            r'number \d+ will shock you'
        ]
        
        clickbait_count = 0
        for pattern in clickbait_patterns:
            if re.search(pattern, full_text, re.IGNORECASE):
                clickbait_count += 1
        
        if clickbait_count > 0:
            clickbait_score = clickbait_count * 3
            tactics_found.append({
                'type': 'clickbait_patterns',
                'name': 'Clickbait Tactics',
                'description': 'Using clickbait formulas',
                'count': clickbait_count,
                'severity': 'medium'
            })
            total_score += clickbait_score
        
        # Normalize score to 0-100 range
        # Max realistic score would be around 40-50 for heavily manipulative content
        # Scale it so that a score of 50 maps to 100%
        normalized_score = min(100, int((total_score / 50) * 100))
        
        # Apply final adjustments
        if normalized_score > 90 and len(tactics_found) < 4:
            # If we got a very high score but few tactics, moderate it
            normalized_score = 80
        
        # Sort tactics by severity
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        tactics_found.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 3))
        
        return {
            'persuasion_score': normalized_score,
            'tactics_found': tactics_found,
            'manipulation_level': self._get_manipulation_level(normalized_score),
            'tactic_count': len(tactics_found),
            'word_count': word_count
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
