# services/emotion_analyzer.py
"""
Emotion Analysis Service
Analyzes emotional tone and sentiment in articles
"""

import re
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class EmotionAnalyzer:
    """Analyze emotional content and tone in articles"""
    
    def __init__(self):
        """Initialize emotion patterns"""
        self._initialize_emotion_lexicon()
    
    def _initialize_emotion_lexicon(self):
        """Initialize emotion word lists"""
        # Basic emotion categories with example words
        self.emotion_lexicon = {
            'anger': {
                'words': ['angry', 'furious', 'outraged', 'incensed', 'livid', 'irate',
                         'enraged', 'infuriated', 'mad', 'annoyed', 'frustrated', 'aggravated'],
                'weight': 2
            },
            'fear': {
                'words': ['afraid', 'scared', 'terrified', 'frightened', 'anxious', 'worried',
                         'nervous', 'panic', 'dread', 'horror', 'terror', 'alarmed'],
                'weight': 2
            },
            'joy': {
                'words': ['happy', 'joyful', 'delighted', 'pleased', 'cheerful', 'glad',
                         'excited', 'thrilled', 'ecstatic', 'elated', 'jubilant', 'content'],
                'weight': 1
            },
            'sadness': {
                'words': ['sad', 'depressed', 'miserable', 'gloomy', 'sorrowful', 'melancholy',
                         'dejected', 'despondent', 'grief', 'mourning', 'heartbroken', 'upset'],
                'weight': 2
            },
            'disgust': {
                'words': ['disgusted', 'revolted', 'repulsed', 'sickened', 'appalled', 'offended',
                         'nauseated', 'abhorrent', 'detestable', 'vile', 'gross', 'repugnant'],
                'weight': 2
            },
            'surprise': {
                'words': ['surprised', 'amazed', 'astonished', 'shocked', 'stunned', 'startled',
                         'bewildered', 'flabbergasted', 'astounded', 'dumbfounded', 'speechless'],
                'weight': 1
            },
            'neutral': {
                'words': ['stated', 'said', 'reported', 'announced', 'described', 'explained',
                         'noted', 'observed', 'mentioned', 'indicated', 'revealed', 'showed'],
                'weight': 0
            }
        }
        
        # Intensity modifiers
        self.intensifiers = {
            'very': 1.5,
            'extremely': 2.0,
            'somewhat': 0.5,
            'slightly': 0.3,
            'incredibly': 2.0,
            'remarkably': 1.8,
            'utterly': 2.0,
            'completely': 1.8,
            'absolutely': 2.0,
            'fairly': 0.7
        }
        
        # Sentiment indicators
        self.positive_indicators = ['fortunately', 'thankfully', 'hopefully', 'luckily',
                                   'positively', 'optimistic', 'encouraging', 'promising']
        
        self.negative_indicators = ['unfortunately', 'sadly', 'regrettably', 'worryingly',
                                   'alarmingly', 'disturbingly', 'troubling', 'concerning']
    
    def analyze(self, article_data):
        """
        Analyze emotional content in article
        
        Args:
            article_data: Dictionary containing article information
            
        Returns:
            Dictionary with emotion analysis
        """
        content = article_data.get('content') or article_data.get('text', '')
        title = article_data.get('title', '')
        
        if not content and not title:
            return self._get_empty_analysis()
        
        # Combine title and content
        full_text = f"{title} {content}"
        
        # Analyze emotions
        emotion_scores = self._analyze_emotions(full_text)
        
        # Determine dominant emotion
        dominant_emotion = self._get_dominant_emotion(emotion_scores)
        
        # Calculate emotional intensity
        emotional_intensity = self._calculate_emotional_intensity(emotion_scores)
        
        # Analyze sentiment
        sentiment = self._analyze_sentiment(full_text, emotion_scores)
        
        # Check for emotional manipulation
        manipulation_score = self._detect_emotional_manipulation(full_text, emotion_scores)
        
        return {
            'dominant_emotion': dominant_emotion,
            'emotions': emotion_scores,
            'emotional_intensity': emotional_intensity,
            'sentiment': sentiment,
            'manipulation_score': manipulation_score,
            'emotional_balance': self._calculate_emotional_balance(emotion_scores),
            'recommendations': self._get_recommendations(emotional_intensity, manipulation_score)
        }
    
    def _analyze_emotions(self, text):
        """Analyze emotions in text"""
        text_lower = text.lower()
        words = text_lower.split()
        
        emotion_scores = {emotion: 0 for emotion in self.emotion_lexicon.keys()}
        
        # Count emotion words
        for i, word in enumerate(words):
            # Check for intensifiers
            intensity = 1.0
            if i > 0 and words[i-1] in self.intensifiers:
                intensity = self.intensifiers[words[i-1]]
            
            # Check each emotion category
            for emotion, data in self.emotion_lexicon.items():
                if word in data['words']:
                    emotion_scores[emotion] += data['weight'] * intensity
        
        # Normalize scores
        total_words = len(words)
        if total_words > 0:
            for emotion in emotion_scores:
                emotion_scores[emotion] = round((emotion_scores[emotion] / total_words) * 100, 2)
        
        return emotion_scores
    
    def _get_dominant_emotion(self, emotion_scores):
        """Determine dominant emotion"""
        # Remove neutral from consideration
        active_emotions = {k: v for k, v in emotion_scores.items() if k != 'neutral'}
        
        if not active_emotions or max(active_emotions.values()) == 0:
            return 'neutral'
        
        return max(active_emotions, key=active_emotions.get)
    
    def _calculate_emotional_intensity(self, emotion_scores):
        """Calculate overall emotional intensity"""
        # Sum all non-neutral emotion scores
        active_emotions = {k: v for k, v in emotion_scores.items() if k != 'neutral'}
        total_emotion = sum(active_emotions.values())
        
        # Scale to 0-100
        intensity = min(100, total_emotion * 10)
        
        return round(intensity, 1)
    
    def _analyze_sentiment(self, text, emotion_scores):
        """Analyze overall sentiment"""
        text_lower = text.lower()
        
        # Basic sentiment from emotions
        positive_emotions = emotion_scores.get('joy', 0) + emotion_scores.get('surprise', 0) * 0.5
        negative_emotions = (emotion_scores.get('anger', 0) + emotion_scores.get('fear', 0) + 
                           emotion_scores.get('sadness', 0) + emotion_scores.get('disgust', 0))
        
        # Check sentiment indicators
        positive_count = sum(1 for word in self.positive_indicators if word in text_lower)
        negative_count = sum(1 for word in self.negative_indicators if word in text_lower)
        
        # Calculate sentiment score (-100 to 100)
        sentiment_score = positive_emotions - negative_emotions + (positive_count - negative_count) * 5
        sentiment_score = max(-100, min(100, sentiment_score))
        
        # Determine sentiment category
        if sentiment_score > 20:
            sentiment = 'positive'
        elif sentiment_score < -20:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'label': sentiment,
            'score': round(sentiment_score, 1),
            'confidence': self._calculate_sentiment_confidence(emotion_scores)
        }
    
    def _detect_emotional_manipulation(self, text, emotion_scores):
        """Detect potential emotional manipulation"""
        manipulation_score = 0
        
        # High intensity negative emotions
        negative_intensity = (emotion_scores.get('anger', 0) + emotion_scores.get('fear', 0) + 
                            emotion_scores.get('disgust', 0))
        
        if negative_intensity > 10:
            manipulation_score += 30
        
        # Excessive emotional language
        emotional_words = ['shocking', 'devastating', 'horrifying', 'outrageous', 'terrible']
        emotional_count = sum(1 for word in emotional_words if word in text.lower())
        manipulation_score += min(emotional_count * 10, 40)
        
        # Rapid emotional shifts (would need more sophisticated analysis)
        if emotion_scores.get('anger', 0) > 5 and emotion_scores.get('fear', 0) > 5:
            manipulation_score += 20
        
        return min(100, manipulation_score)
    
    def _calculate_emotional_balance(self, emotion_scores):
        """Calculate emotional balance in content"""
        # Remove neutral
        active_emotions = {k: v for k, v in emotion_scores.items() if k != 'neutral' and v > 0}
        
        if len(active_emotions) == 0:
            return 'neutral'
        elif len(active_emotions) == 1:
            return 'single-emotion'
        elif len(active_emotions) <= 3:
            return 'balanced'
        else:
            return 'mixed'
    
    def _calculate_sentiment_confidence(self, emotion_scores):
        """Calculate confidence in sentiment analysis"""
        # Higher emotion scores = higher confidence
        total_emotion = sum(emotion_scores.values())
        
        if total_emotion > 20:
            return 'high'
        elif total_emotion > 10:
            return 'medium'
        else:
            return 'low'
    
    def _get_recommendations(self, intensity, manipulation_score):
        """Get recommendations based on emotional analysis"""
        recommendations = []
        
        if intensity > 70:
            recommendations.append("High emotional content detected - read critically")
        
        if manipulation_score > 50:
            recommendations.append("Potential emotional manipulation - verify facts independently")
        
        if intensity < 20:
            recommendations.append("Low emotional content - appears objective")
        
        return recommendations
    
    def _get_empty_analysis(self):
        """Return empty analysis structure"""
        return {
            'dominant_emotion': 'neutral',
            'emotions': {emotion: 0 for emotion in self.emotion_lexicon.keys()},
            'emotional_intensity': 0,
            'sentiment': {'label': 'neutral', 'score': 0, 'confidence': 'low'},
            'manipulation_score': 0,
            'emotional_balance': 'neutral',
            'recommendations': ['No content to analyze']
        }
