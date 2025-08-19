"""
OpenAI Enhancement Service - FIXED VERSION
Removes the proxies parameter that's causing the initialization error
"""
import os
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import openai
from openai import OpenAI

from services.base_analyzer import BaseAnalyzer
from config import Config

logger = logging.getLogger(__name__)


class OpenAIEnhancer(BaseAnalyzer):
    """
    Enhanced AI analysis using OpenAI GPT-4
    Provides deep insights, summaries, and fact-checking
    """
    
    def __init__(self):
        super().__init__('openai_enhancer')
        self.client = None
        self.model = "gpt-4-turbo-preview"  # Best model for analysis
        self.max_tokens = 2000
        
        if self.is_available:
            # FIXED: Remove proxies parameter - not supported in current OpenAI library
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
            logger.info(f"OpenAI Enhancer initialized with model: {self.model}")
    
    def _check_availability(self) -> bool:
        """Check if OpenAI API is available"""
        return bool(Config.OPENAI_API_KEY) and Config.is_service_enabled(self.service_name)
    
    def analyze(self, article_data: Dict[str, Any], 
                service_results: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform enhanced AI analysis on article
        
        Args:
            article_data: Extracted article data
            service_results: Results from other services for context
            
        Returns:
            Enhanced analysis results
        """
        if not self.is_available:
            return self._build_error_result("OpenAI API not configured")
        
        try:
            # Extract key data
            title = article_data.get('title', 'Unknown')
            text = article_data.get('text', '')
            author = article_data.get('author', 'Unknown')
            source = article_data.get('source', 'Unknown')
            
            if not text:
                return self._build_error_result("No article text to analyze")
            
            # Prepare context from other services
            context = self._prepare_context(service_results)
            
            # Run multiple AI analyses
            results = {
                'success': True,
                'service': self.service_name,
                'timestamp': datetime.now().isoformat()
            }
            
            # 1. Comprehensive Summary
            summary_result = self._generate_summary(text, title, author)
            results.update(summary_result)
            
            # 2. Key Claims Extraction
            claims_result = self._extract_key_claims(text)
            results['key_claims'] = claims_result
            
            # 3. Bias and Framing Analysis
            bias_result = self._analyze_bias_and_framing(text, title)
            results['ai_bias_analysis'] = bias_result
            
            # 4. Critical Questions
            questions = self._generate_critical_questions(text, title, context)
            results['critical_questions'] = questions
            
            # 5. Overall Assessment
            assessment = self._generate_overall_assessment(
                text, title, author, source, context
            )
            results['overall_assessment'] = assessment
            
            # 6. Fact-Check Suggestions
            if context.get('fact_checker'):
                fact_suggestions = self._suggest_fact_checks(
                    text, context['fact_checker']
                )
                results['fact_check_suggestions'] = fact_suggestions
            
            return results
            
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}", exc_info=True)
            return self._build_error_result(str(e))
    
    def _prepare_context(self, service_results: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare context from other service results"""
        if not service_results:
            return {}
        
        context = {}
        
        # Extract key findings from each service
        for service, result in service_results.items():
            if isinstance(result, dict) and result.get('success'):
                if service == 'source_credibility':
                    context['source_score'] = result.get('credibility_score', 0)
                    context['source_info'] = result.get('domain_info', {})
                elif service == 'author_analyzer':
                    context['author_score'] = result.get('credibility_score', 0)
                    context['author_expertise'] = result.get('expertise', {})
                elif service == 'bias_detector':
                    context['bias_score'] = result.get('bias_score', 0)
                    context['political_lean'] = result.get('political_lean', 'center')
                elif service == 'fact_checker':
                    context['fact_checker'] = result
                elif service == 'manipulation_detector':
                    context['manipulation_level'] = result.get('manipulation_level', 'low')
                    
        return context
    
    def _generate_summary(self, text: str, title: str, author: str) -> Dict[str, str]:
        """Generate comprehensive article summary"""
        try:
            prompt = f"""Provide a comprehensive summary of this news article.

Title: {title}
Author: {author}
Text: {text[:4000]}  # Limit to avoid token limits

Create a detailed summary that includes:
1. Main topic and key points (3-4 sentences)
2. Primary claims or arguments made
3. Supporting evidence mentioned
4. Any conclusions or implications

Keep the summary factual and neutral. Format as a single paragraph."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional news analyst providing objective summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            return {
                'summary': response.choices[0].message.content,
                'summary_generated': True
            }
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return {
                'summary': 'Summary generation failed',
                'summary_generated': False
            }
    
    def _extract_key_claims(self, text: str) -> List[Dict[str, Any]]:
        """Extract and categorize key claims from the article"""
        try:
            prompt = f"""Extract the key factual claims from this article that would need verification.

Text: {text[:4000]}

For each claim, provide:
1. The claim itself (exact or paraphrased)
2. Category (statistic, quote, event, prediction, comparison, etc.)
3. Verifiability (easily verifiable, difficult to verify, opinion)
4. Importance (high, medium, low)

Return as JSON array with objects containing: claim, category, verifiability, importance"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a fact-checking expert identifying claims that need verification."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('claims', [])[:10]  # Limit to top 10 claims
            
        except Exception as e:
            logger.error(f"Claims extraction error: {e}")
            return []
    
    def _analyze_bias_and_framing(self, text: str, title: str) -> Dict[str, Any]:
        """Analyze bias and framing techniques"""
        try:
            prompt = f"""Analyze the bias and framing in this article.

Title: {title}
Text: {text[:6000]}

Examine:
1. Language bias (loaded words, emotional language)
2. Framing techniques (how issues are presented)
3. Perspective bias (whose voices are included/excluded)
4. Selection bias (what facts are emphasized/omitted)
5. Headline vs content alignment

Provide an objective analysis with specific examples.
Format as JSON with keys: language_bias, framing_techniques, perspective_bias, selection_bias, headline_alignment, overall_bias_assessment"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a media bias expert providing neutral, evidence-based analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Bias analysis error: {e}")
            return {}
    
    def _generate_critical_questions(self, text: str, title: str, context: Dict[str, Any]) -> List[str]:
        """Generate critical questions readers should ask"""
        try:
            context_info = f"""
Context from other analyses:
- Source credibility: {context.get('source_score', 'unknown')}/100
- Author credibility: {context.get('author_score', 'unknown')}/100
- Bias level: {context.get('bias_score', 'unknown')}/100
- Political lean: {context.get('political_lean', 'unknown')}
"""

            prompt = f"""Based on this article and its analysis context, generate 5 critical questions readers should ask.

Title: {title}
Text excerpt: {text[:3000]}
{context_info}

Create thought-provoking questions that:
1. Challenge assumptions in the article
2. Identify missing information
3. Question sources and evidence
4. Explore alternative perspectives
5. Consider broader implications

Return as a JSON object with a 'questions' array."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a critical thinking expert helping readers analyze news articles."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=800,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('questions', [])[:5]
            
        except Exception as e:
            logger.error(f"Question generation error: {e}")
            return []
    
    def _generate_overall_assessment(self, text: str, title: str, author: str, 
                                   source: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall credibility assessment"""
        try:
            prompt = f"""Provide an overall credibility assessment of this article.

Title: {title}
Author: {author}
Source: {source}
Text excerpt: {text[:3000]}

Context from other analyses:
- Source credibility: {context.get('source_score', 'unknown')}/100
- Author credibility: {context.get('author_score', 'unknown')}/100
- Bias level: {context.get('bias_score', 'unknown')}/100
- Manipulation level: {context.get('manipulation_level', 'unknown')}

Provide:
1. Overall credibility rating (high/medium/low)
2. Main strengths (2-3 points)
3. Main concerns (2-3 points)
4. Recommendation for readers
5. Confidence level in assessment (high/medium/low)

Format as JSON with keys: credibility_rating, strengths, concerns, recommendation, confidence_level"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior news analyst providing balanced credibility assessments."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Assessment generation error: {e}")
            return {
                'credibility_rating': 'unknown',
                'error': str(e)
            }
    
    def _suggest_fact_checks(self, text: str, fact_checker_results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Suggest additional fact-checks based on analysis"""
        try:
            # Get claims that weren't checked
            checked_claims = fact_checker_results.get('claims_checked', [])
            
            prompt = f"""Based on this article, suggest additional fact-checks that should be performed.

Text excerpt: {text[:3000]}

Already checked claims:
{json.dumps(checked_claims, indent=2)}

Suggest 3-5 additional claims or facts that should be verified, focusing on:
1. Important claims not yet checked
2. Statistics or data that need verification
3. Quotes that should be confirmed
4. Historical facts or comparisons

For each suggestion, provide:
- The claim to check
- Why it's important
- Suggested verification method

Format as JSON array with objects containing: claim, importance, verification_method"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a fact-checking expert suggesting verification priorities."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('suggestions', [])[:5]
            
        except Exception as e:
            logger.error(f"Fact-check suggestion error: {e}")
            return []
    
    def _build_error_result(self, error_message: str) -> Dict[str, Any]:
        """Build standardized error result"""
        return {
            'success': False,
            'service': self.service_name,
            'error': error_message,
            'timestamp': datetime.now().isoformat()
        }
