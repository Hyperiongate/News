"""
OpenAI Enhancement Service - FIXED for Pipeline Integration
Provides AI-powered summaries and insights
"""
import os
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import time

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI library not available")

from services.base_analyzer import BaseAnalyzer
from config import Config

logger = logging.getLogger(__name__)


class OpenAIEnhancer(BaseAnalyzer):
    """
    Enhanced AI analysis using OpenAI GPT
    Provides summaries and insights
    """
    
    def __init__(self):
        super().__init__('openai_enhancer')
        self.client = None
        self.model = "gpt-3.5-turbo"  # Faster model for better performance
        self.max_tokens = 1000
        
        if self.is_available and OPENAI_AVAILABLE:
            try:
                self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
                logger.info(f"OpenAI Enhancer initialized with model: {self.model}")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self._available = False
    
    def _check_availability(self) -> bool:
        """Check if OpenAI API is available"""
        return bool(Config.OPENAI_API_KEY) and OPENAI_AVAILABLE and Config.is_service_enabled(self.service_name)
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform enhanced AI analysis on article
        
        Args:
            data: Input data containing article and other service results
            
        Returns:
            Enhanced analysis results
        """
        if not self.is_available or not self.client:
            return self.get_error_result("OpenAI API not configured or unavailable")
        
        try:
            start_time = time.time()
            
            # Extract article data
            article = data.get('article', {})
            if not article:
                # Try to extract from data directly
                article = {
                    'title': data.get('title', 'Unknown'),
                    'text': data.get('text', ''),
                    'author': data.get('author', 'Unknown'),
                    'domain': data.get('domain', 'Unknown')
                }
            
            title = article.get('title', 'Unknown')
            text = article.get('text', '')
            author = article.get('author', 'Unknown')
            domain = article.get('domain', article.get('source', 'Unknown'))
            
            if not text:
                return self.get_error_result("No article text to analyze")
            
            # Initialize results
            results = {
                'success': True,
                'service': self.service_name,
                'timestamp': datetime.now().isoformat()
            }
            
            # Generate comprehensive summary
            summary = self._generate_summary(text, title, author)
            if summary:
                results['summary'] = summary
                results['ai_summary'] = summary  # Duplicate for compatibility
            
            # Extract key points
            key_points = self._extract_key_points(text, title)
            if key_points:
                results['key_points'] = key_points
            
            # Generate critical questions
            questions = self._generate_critical_questions(text, title)
            if questions:
                results['critical_questions'] = questions
            
            # Overall assessment
            assessment = self._generate_assessment(text, title, author, domain)
            if assessment:
                results['overall_assessment'] = assessment
            
            # Add processing time
            results['processing_time'] = time.time() - start_time
            
            return results
            
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _generate_summary(self, text: str, title: str, author: str) -> Optional[str]:
        """Generate comprehensive article summary"""
        try:
            # Limit text to avoid token limits
            text_preview = text[:4000] if len(text) > 4000 else text
            
            prompt = f"""Provide a clear, concise summary of this news article in 2-3 paragraphs.

Title: {title}
Author: {author}
Text: {text_preview}

Focus on:
1. The main topic and key claims
2. Important facts and evidence presented
3. Any conclusions or implications

Keep the summary factual, neutral, and easy to understand."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional news analyst providing clear, unbiased summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=400
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return None
    
    def _extract_key_points(self, text: str, title: str) -> Optional[List[str]]:
        """Extract key points from the article"""
        try:
            text_preview = text[:3000] if len(text) > 3000 else text
            
            prompt = f"""Extract the 3-5 most important points from this article.

Title: {title}
Text: {text_preview}

Format as a simple list of key points, each on a new line starting with a dash (-)."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at identifying key information in news articles."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=200
            )
            
            # Parse the response into a list
            content = response.choices[0].message.content.strip()
            points = [line.strip().lstrip('-').strip() 
                     for line in content.split('\n') 
                     if line.strip() and line.strip().startswith('-')]
            
            return points[:5]  # Limit to 5 points
            
        except Exception as e:
            logger.error(f"Key points extraction failed: {e}")
            return None
    
    def _generate_critical_questions(self, text: str, title: str) -> Optional[List[str]]:
        """Generate critical thinking questions about the article"""
        try:
            text_preview = text[:2000] if len(text) > 2000 else text
            
            prompt = f"""Generate 3 critical thinking questions that readers should consider about this article.

Title: {title}
Text: {text_preview}

Focus on:
- What information might be missing
- Potential biases or assumptions
- Need for additional sources or verification

Format as a simple list, each question on a new line starting with a dash (-)."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a critical thinking expert helping readers analyze news articles."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=150
            )
            
            # Parse the response into a list
            content = response.choices[0].message.content.strip()
            questions = [line.strip().lstrip('-').strip() 
                        for line in content.split('\n') 
                        if line.strip() and line.strip().startswith('-')]
            
            return questions[:3]  # Limit to 3 questions
            
        except Exception as e:
            logger.error(f"Critical questions generation failed: {e}")
            return None
    
    def _generate_assessment(self, text: str, title: str, author: str, domain: str) -> Optional[str]:
        """Generate overall assessment of the article"""
        try:
            text_preview = text[:2500] if len(text) > 2500 else text
            
            prompt = f"""Provide a brief overall assessment of this article's quality and reliability in 1 paragraph.

Title: {title}
Author: {author}
Source: {domain}
Text: {text_preview}

Consider:
- Writing quality and clarity
- Use of sources and evidence
- Potential biases or issues
- Overall trustworthiness

Keep the assessment balanced and professional."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert news analyst providing balanced assessments."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Assessment generation failed: {e}")
            return None
