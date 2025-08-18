"""
OpenAI Enhancement Service
Adds powerful AI features to news analysis using GPT-4
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
            
            # 4. Fact Check Suggestions
            fact_check_result = self._suggest_fact_checks(text, claims_result)
            results['fact_check_suggestions'] = fact_check_result
            
            # 5. Reader Questions
            questions_result = self._generate_critical_questions(text, context)
            results['critical_questions'] = questions_result
            
            # 6. Overall AI Assessment
            assessment = self._generate_overall_assessment(text, title, context)
            results['ai_assessment'] = assessment
            
            # Calculate AI confidence score
            results['ai_confidence'] = self._calculate_confidence(results)
            
            return results
            
        except Exception as e:
            logger.error(f"OpenAI analysis error: {e}")
            return self._build_error_result(str(e))
    
    def _prepare_context(self, service_results: Optional[Dict[str, Any]]) -> str:
        """Prepare context from other service results"""
        if not service_results:
            return "No additional context available."
        
        context_parts = []
        
        # Add relevant findings from other services
        if 'source_credibility' in service_results:
            score = service_results['source_credibility'].get('credibility_score', 0)
            context_parts.append(f"Source credibility score: {score}/100")
        
        if 'author_analyzer' in service_results:
            author_info = service_results['author_analyzer'].get('summary', '')
            if author_info:
                context_parts.append(f"Author info: {author_info}")
        
        if 'bias_detector' in service_results:
            bias_score = service_results['bias_detector'].get('overall_bias_score', 0)
            context_parts.append(f"Bias detection score: {bias_score}/100")
        
        return " | ".join(context_parts) if context_parts else "Limited context available."
    
    def _generate_summary(self, text: str, title: str, author: str) -> Dict[str, Any]:
        """Generate comprehensive article summary"""
        try:
            # Truncate text if too long
            max_chars = 12000  # Leave room for response
            if len(text) > max_chars:
                text = text[:max_chars] + "..."
            
            prompt = f"""Analyze this news article and provide a comprehensive summary.

Title: {title}
Author: {author}

Article Text:
{text}

Provide:
1. A concise 2-3 sentence summary
2. Main topic and angle
3. Key points (3-5 bullet points)
4. Notable quotes or statistics
5. What's missing or not addressed

Format as JSON with keys: summary, topic, key_points, notable_quotes, missing_context"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert news analyst providing objective, thorough analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            result['tokens_used'] = response.usage.total_tokens
            
            return result
            
        except Exception as e:
            logger.error(f"Summary generation error: {e}")
            return {
                'summary': 'Unable to generate summary',
                'error': str(e)
            }
    
    def _extract_key_claims(self, text: str) -> List[Dict[str, Any]]:
        """Extract and categorize key claims"""
        try:
            prompt = f"""Extract the key factual claims from this article.

Article Text:
{text[:8000]}

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
                temperature=0.4,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Bias analysis error: {e}")
            return {'error': str(e)}
    
    def _suggest_fact_checks(self, text: str, claims: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Suggest specific fact-checks for claims"""
        try:
            # Focus on high-importance, verifiable claims
            priority_claims = [c for c in claims if c.get('importance') == 'high' 
                              and c.get('verifiability') != 'opinion'][:5]
            
            if not priority_claims:
                return []
            
            claims_text = "\n".join([f"- {c['claim']}" for c in priority_claims])
            
            prompt = f"""For these key claims, suggest specific fact-checking approaches:

{claims_text}

For each claim, provide:
1. Suggested verification method
2. Potential sources to check
3. Red flags to watch for
4. Questions to ask

Format as JSON array with objects containing: claim, verification_method, sources, red_flags, questions"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional fact-checker providing actionable verification strategies."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('fact_checks', [])
            
        except Exception as e:
            logger.error(f"Fact check suggestions error: {e}")
            return []
    
    def _generate_critical_questions(self, text: str, context: str) -> List[str]:
        """Generate critical questions readers should ask"""
        try:
            prompt = f"""Based on this article, generate 5 critical questions readers should ask.

Article: {text[:4000]}
Context: {context}

Create thought-provoking questions that:
1. Challenge assumptions
2. Seek missing information
3. Question sources and evidence
4. Explore alternative perspectives
5. Examine implications

Return as JSON with key 'questions' containing an array of question strings."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a critical thinking expert helping readers analyze news critically."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=400,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('questions', [])
            
        except Exception as e:
            logger.error(f"Question generation error: {e}")
            return []
    
    def _generate_overall_assessment(self, text: str, title: str, context: str) -> Dict[str, Any]:
        """Generate overall AI assessment"""
        try:
            prompt = f"""Provide an overall journalistic assessment of this article.

Title: {title}
Context: {context}
Text: {text[:5000]}

Assess:
1. Journalistic quality (structure, clarity, completeness)
2. Evidence quality (sources, data, expert opinions)
3. Balance and fairness
4. Potential impact or agenda
5. Reliability for readers

Provide a nuanced assessment with specific observations.
Format as JSON with keys: quality_score (0-100), strengths (array), weaknesses (array), 
evidence_quality, balance_assessment, reliability_notes, recommendation"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior journalism professor providing constructive analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=800,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Assessment generation error: {e}")
            return {
                'quality_score': 0,
                'error': str(e)
            }
    
    def _calculate_confidence(self, results: Dict[str, Any]) -> int:
        """Calculate AI confidence in analysis"""
        confidence = 85  # Base confidence
        
        # Adjust based on completeness
        if results.get('error'):
            confidence -= 30
        if not results.get('key_claims'):
            confidence -= 10
        if not results.get('ai_assessment'):
            confidence -= 10
        
        # Boost for successful analyses
        if results.get('ai_assessment', {}).get('quality_score', 0) > 70:
            confidence += 5
        
        return max(0, min(100, confidence))
    
    def _build_error_result(self, error: str) -> Dict[str, Any]:
        """Build error result"""
        return {
            'success': False,
            'service': self.service_name,
            'error': error,
            'timestamp': datetime.now().isoformat()
        }


# Cost estimation helper
def estimate_openai_cost(text_length: int, num_analyses: int = 6) -> Dict[str, float]:
    """
    Estimate OpenAI API cost for analyzing an article
    
    GPT-4 Turbo pricing (as of 2024):
    - Input: $0.01 per 1K tokens
    - Output: $0.03 per 1K tokens
    """
    # Rough token estimation (1 token ≈ 4 characters)
    input_tokens = text_length / 4
    
    # Estimate tokens per analysis
    tokens_per_analysis = {
        'summary': 1000,
        'claims': 1200,
        'bias': 1200,
        'fact_check': 1000,
        'questions': 600,
        'assessment': 1000
    }
    
    total_output_tokens = sum(tokens_per_analysis.values())
    
    # Calculate costs
    input_cost = (input_tokens * num_analyses / 1000) * 0.01
    output_cost = (total_output_tokens / 1000) * 0.03
    total_cost = input_cost + output_cost
    
    return {
        'input_tokens': input_tokens * num_analyses,
        'output_tokens': total_output_tokens,
        'input_cost': input_cost,
        'output_cost': output_cost,
        'total_cost': total_cost,
        'analyses_per_dollar': 1 / total_cost if total_cost > 0 else 0
    }
