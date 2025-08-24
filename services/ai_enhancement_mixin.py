"""
AI Enhancement Mixin
Provides AI capabilities to any service that inherits from it
FIXED: Handles initialization errors gracefully
"""
import logging
import json
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class AIEnhancementMixin:
    """
    Mixin to add AI capabilities to any analysis service
    Services can inherit from both BaseAnalyzer and this mixin
    """
    
    def __init__(self):
        """Initialize AI client if available"""
        self._ai_client = None
        self._ai_model = "gpt-3.5-turbo"  # Using faster model
        self._ai_available = False
        
        try:
            from config import Config
            if Config.OPENAI_API_KEY:
                try:
                    from openai import OpenAI
                    self._ai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
                    self._ai_available = True
                    logger.info(f"{self.__class__.__name__} AI enhancement initialized")
                except ImportError:
                    logger.warning(f"OpenAI library not installed for {self.__class__.__name__}")
                except Exception as e:
                    logger.warning(f"AI enhancement not available for {self.__class__.__name__}: {e}")
            else:
                logger.debug(f"No OpenAI API key configured for {self.__class__.__name__}")
        except Exception as e:
            logger.warning(f"Error initializing AI enhancement for {self.__class__.__name__}: {e}")
    
    def _enhance_with_ai(self, prompt: str, temperature: float = 0.3, 
                        max_tokens: int = 1000, json_mode: bool = False) -> Optional[Dict[str, Any]]:
        """
        Generic AI enhancement method
        
        Args:
            prompt: The prompt to send to AI
            temperature: Creativity level (0-1)
            max_tokens: Maximum response length
            json_mode: Whether to request JSON response
            
        Returns:
            AI response or None if unavailable
        """
        if not self._ai_available or not self._ai_client:
            return None
            
        try:
            messages = [
                {"role": "system", "content": "You are an expert news analysis AI assistant."},
                {"role": "user", "content": prompt}
            ]
            
            kwargs = {
                "model": self._ai_model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            
            response = self._ai_client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content
            
            if json_mode:
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse AI JSON response: {content}")
                    return None
            else:
                return {"response": content}
                
        except Exception as e:
            logger.error(f"AI enhancement failed: {e}")
            return None
    
    # Source Credibility AI Methods
    def _ai_detect_credibility_issues(self, source_name: str, domain: str, 
                                    analysis_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """AI method to detect credibility issues in sources"""
        if not self._ai_available:
            return None
            
        prompt = f"""Analyze the credibility of this news source:

Source: {source_name}
Domain: {domain}
Database Status: {analysis_data.get('in_database', False)}
Technical Score: {analysis_data.get('technical', {}).get('age_credibility', 'unknown')}

Identify:
1. Red flags that indicate low credibility
2. Trust signals that indicate high credibility
3. Specific concerns if any

Format as JSON with keys: red_flags (array of objects with 'issue' and 'explanation'), trust_signals (array of strings), overall_assessment"""

        return self._enhance_with_ai(prompt, temperature=0.2, json_mode=True)
    
    # Bias Detection AI Methods
    def _ai_detect_bias_patterns(self, text: str, initial_bias_score: int) -> Optional[Dict[str, Any]]:
        """AI method to detect bias patterns in article text"""
        if not self._ai_available:
            return None
            
        prompt = f"""Analyze the bias in this news article:

Text excerpt: {text[:1500]}
Initial bias score: {initial_bias_score}/100

Identify:
1. Specific biased phrases or framing
2. Missing perspectives
3. Emotional manipulation techniques
4. One-sided arguments

Format as JSON with keys: biased_phrases (array), missing_perspectives (array), emotional_language (array), bias_assessment"""

        return self._enhance_with_ai(prompt, temperature=0.3, json_mode=True)
    
    # Author Analysis AI Methods
    def _ai_analyze_author(self, author_name: str, author_history: List[Dict], 
                          article_content: str) -> Optional[Dict[str, Any]]:
        """AI method to analyze author credibility"""
        if not self._ai_available:
            return None
            
        # Handle empty bio_text
        history_titles = [a.get('title', '') for a in (author_history or [])[:5]]
        
        prompt = f"""Analyze the credibility of this journalist:

Author: {author_name}
Previous article titles: {json.dumps(history_titles, indent=2)}
Current article excerpt: {article_content[:500]}

Assess:
1. Writing style consistency
2. Topic expertise indicators
3. Potential bias patterns
4. Credibility indicators
5. Red flags if any

Format as JSON with keys: style_assessment, expertise_indicators (array), bias_patterns (array), credibility_factors (array), red_flags (array), strengths (array), credibility_adjustment (integer from -20 to +20), expertise_assessment (array)"""

        return self._enhance_with_ai(prompt, temperature=0.2, json_mode=True)
    
    # Transparency AI Methods
    def _ai_analyze_transparency(self, transparency_data: Dict[str, Any], 
                                article_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """AI method to assess transparency"""
        if not self._ai_available:
            return None
            
        prompt = f"""Assess the transparency of this news article:

Title: {article_data.get('title', 'Unknown')}
Author: {article_data.get('author', 'Unknown')}
Source count: {transparency_data.get('source_count', 0)}
Has disclosures: {transparency_data.get('has_disclosures', False)}
Transparency indicators: {json.dumps(transparency_data.get('indicators', []))}

Evaluate:
1. Source attribution quality
2. Conflict of interest disclosures
3. Funding transparency
4. Correction policy
5. Author credentials disclosure

Format as JSON with keys: transparency_score (0-100), missing_elements (array), red_flags (array), positive_indicators (array)"""

        return self._enhance_with_ai(prompt, temperature=0.2, json_mode=True)
    
    # Manipulation Detection AI Methods
    def _ai_detect_manipulation(self, text: str, tactics_found: List[str]) -> Optional[Dict[str, Any]]:
        """AI method to detect manipulation tactics"""
        if not self._ai_available:
            return None
            
        prompt = f"""Analyze manipulation tactics in this article:

Text excerpt: {text[:1500]}
Already detected tactics: {json.dumps(tactics_found)}

Identify:
1. Emotional manipulation techniques
2. Logical fallacies
3. Propaganda techniques
4. Misleading framing
5. Hidden agendas

Format as JSON with keys: emotional_tactics (array), logical_fallacies (array), propaganda_techniques (array), misleading_elements (array), severity_assessment"""

        return self._enhance_with_ai(prompt, temperature=0.3, json_mode=True)
    
    # Content Analysis AI Methods
    def _ai_analyze_content_quality(self, text: str, metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """AI-enhanced content quality analysis"""
        if not self._ai_available:
            return None
            
        prompt = f"""Analyze the quality and structure of this news article:

Text preview: {text[:1000]}...

Current metrics:
- Readability score: {metrics.get('readability_score', 'Unknown')}
- Sentence complexity: {metrics.get('sentence_complexity', 'Unknown')}
- Word diversity: {metrics.get('vocabulary_diversity', 'Unknown')}

Assess:
1. Argument structure and logic
2. Evidence quality
3. Writing clarity
4. Professional standards
5. Information density

Format as JSON with keys: argument_quality, evidence_assessment, clarity_score, professionalism, information_value, strengths (array), weaknesses (array)"""

        return self._enhance_with_ai(prompt, temperature=0.2, json_mode=True)
    
    # Fact Checking AI Methods
    def _ai_fact_check_claims(self, claims: List[str], context: str) -> Optional[Dict[str, Any]]:
        """AI method to help with fact checking"""
        if not self._ai_available:
            return None
            
        if not claims:
            # Extract claims if none provided
            prompt = f"""Extract factual claims from this text that should be fact-checked:

{context[:1000]}

List up to 10 specific, verifiable claims. Format as JSON with key 'claims' containing an array of objects with 'claim' and 'context' fields."""
        else:
            prompt = f"""Analyze these claims for fact-checking:

Claims:
{json.dumps(claims[:10], indent=2)}

For each claim, suggest:
1. Verification approach
2. Potential sources to check
3. Red flags if any

Format as JSON with key 'fact_checks' containing array of objects with fields: claim, verification_approach, suggested_sources, red_flags"""

        return self._enhance_with_ai(prompt, temperature=0.2, json_mode=True)
    
    def _merge_ai_enhancements(self, original_results: Dict[str, Any], 
                              ai_results: Optional[Dict[str, Any]], 
                              enhancement_type: str) -> Dict[str, Any]:
        """
        Merge AI enhancements into original results
        
        Args:
            original_results: Original service analysis results
            ai_results: AI enhancement results
            enhancement_type: Type of enhancement for logging
            
        Returns:
            Merged results
        """
        if not ai_results:
            return original_results
            
        # Add AI enhancement marker
        if 'metadata' not in original_results:
            original_results['metadata'] = {}
            
        original_results['metadata']['ai_enhanced'] = True
        original_results['metadata']['ai_enhancement_type'] = enhancement_type
        
        # Store AI results separately
        if 'ai_insights' not in original_results:
            original_results['ai_insights'] = {}
        
        original_results['ai_insights'][enhancement_type] = ai_results
        
        # Update summary if AI found significant issues
        if 'summary' in original_results and ai_results.get('concerns'):
            original_results['summary'] += f" AI analysis identified additional concerns."
        
        return original_results
