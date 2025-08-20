"""
AI Enhancement Mixin
Provides AI capabilities to any service that inherits from it
"""
import logging
import json
from typing import Dict, Any, List, Optional
from openai import OpenAI
from config import Config

logger = logging.getLogger(__name__)


class AIEnhancementMixin:
    """
    Mixin to add AI capabilities to any analysis service
    Services can inherit from both BaseAnalyzer and this mixin
    """
    
    def __init__(self):
        """Initialize AI client if available"""
        self._ai_client = None
        self._ai_model = "gpt-4-turbo-preview"
        self._ai_available = False
        
        if Config.OPENAI_API_KEY:
            try:
                self._ai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
                self._ai_available = True
                logger.info(f"{self.__class__.__name__} AI enhancement initialized")
            except Exception as e:
                logger.warning(f"AI enhancement not available for {self.__class__.__name__}: {e}")
    
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
                return json.loads(content)
            return {"response": content}
            
        except Exception as e:
            logger.error(f"AI enhancement failed: {e}")
            return None
    
    def _ai_analyze_credibility(self, source_info: Dict[str, Any], article_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """AI-enhanced credibility analysis"""
        prompt = f"""Analyze the credibility of this news source:

Source: {source_info.get('domain', 'Unknown')}
Source Type: {source_info.get('type', 'Unknown')}
Known Rating: {source_info.get('credibility_rating', 'Unknown')}

Article Title: {article_data.get('title', 'Unknown')}
Article Preview: {article_data.get('text', '')[:500]}...

Provide a credibility assessment including:
1. Red flags or credibility indicators
2. Comparison to known reliable sources
3. Writing style assessment
4. Specific concerns if any

Format as JSON with keys: red_flags (array), credibility_indicators (array), style_assessment, concerns, overall_assessment, confidence_level"""

        return self._enhance_with_ai(prompt, temperature=0.2, json_mode=True)
    
    def _ai_detect_bias_patterns(self, text: str, initial_findings: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """AI-enhanced bias pattern detection"""
        prompt = f"""Analyze this text for subtle bias patterns that automated detection might miss:

Text: {text[:1500]}...

Initial findings:
- Political lean: {initial_findings.get('political_label', 'Unknown')}
- Sensationalism: {initial_findings.get('sensationalism', 'Unknown')}
- Loaded phrases found: {len(initial_findings.get('loaded_phrases', []))}

Look for:
1. Subtle framing bias
2. Selective fact presentation
3. Implicit assumptions
4. Emotional manipulation
5. Missing context or perspectives

Format as JSON with keys: subtle_biases (array), framing_issues (array), missing_perspectives (array), manipulation_techniques (array), severity_assessment"""

        return self._enhance_with_ai(prompt, temperature=0.3, json_mode=True)
    
    def _ai_fact_check_claims(self, claims: List[str], context: str) -> Optional[Dict[str, Any]]:
        """AI-enhanced fact checking assistance"""
        prompt = f"""Review these claims for fact-checking priority and potential issues:

Claims:
{json.dumps(claims[:10], indent=2)}

Article context: {context[:500]}...

For each claim:
1. Assess verifiability (easy/medium/hard)
2. Identify potential fact-checking approaches
3. Note any obvious red flags
4. Suggest search queries for verification

Format as JSON with key 'claims' containing array of objects with: claim, verifiability, approach, red_flags, search_queries"""

        return self._enhance_with_ai(prompt, temperature=0.2, json_mode=True)
    
    def _ai_analyze_transparency(self, transparency_data: Dict[str, Any], article_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """AI-enhanced transparency analysis"""
        prompt = f"""Analyze transparency and disclosure in this article:

Article: {article_data.get('title', 'Unknown')}
Author: {article_data.get('author', 'Unknown')}
Source: {article_data.get('source', 'Unknown')}

Current transparency indicators:
{json.dumps(transparency_data.get('indicators', []), indent=2)}

Assess:
1. Source attribution quality
2. Conflict of interest disclosures
3. Methodology transparency (if applicable)
4. Author expertise disclosure
5. Funding/sponsorship disclosure

Format as JSON with keys: attribution_quality, disclosure_issues (array), transparency_gaps (array), recommendations (array), trust_impact"""

        return self._enhance_with_ai(prompt, temperature=0.2, json_mode=True)
    
    def _ai_detect_manipulation(self, text: str, emotional_score: int) -> Optional[Dict[str, Any]]:
        """AI-enhanced manipulation detection"""
        prompt = f"""Analyze this text for psychological manipulation tactics:

Text: {text[:1500]}...
Emotional intensity score: {emotional_score}/100

Identify:
1. Emotional manipulation techniques
2. Logical fallacies
3. Persuasion tactics
4. Misleading presentation
5. Gaslighting or reality distortion

Format as JSON with keys: emotional_tactics (array), logical_fallacies (array), persuasion_methods (array), severity, specific_examples (array with quotes)"""

        return self._enhance_with_ai(prompt, temperature=0.3, json_mode=True)
    
    def _ai_analyze_author(self, author_name: str, author_history: List[Dict], article_content: str) -> Optional[Dict[str, Any]]:
        """AI-enhanced author analysis"""
        prompt = f"""Analyze this author's credibility and potential biases:

Author: {author_name}
Recent articles: {len(author_history)}
Current article preview: {article_content[:500]}...

Previous article titles:
{json.dumps([a.get('title', '') for a in author_history[:5]], indent=2)}

Assess:
1. Writing style consistency
2. Topic expertise indicators
3. Potential bias patterns
4. Credibility indicators
5. Red flags if any

Format as JSON with keys: style_assessment, expertise_indicators (array), bias_patterns (array), credibility_factors (array), concerns (array), overall_rating"""

        return self._enhance_with_ai(prompt, temperature=0.2, json_mode=True)
    
    def _ai_analyze_content_quality(self, text: str, metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """AI-enhanced content quality analysis"""
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
        if 'ai_enhanced' not in original_results:
            original_results['ai_enhanced'] = {}
        
        original_results['ai_enhanced'][enhancement_type] = ai_results
        
        # Update summary if AI found significant issues
        if 'summary' in original_results and ai_results.get('concerns'):
            original_results['summary'] += f" AI analysis identified additional concerns."
        
        # Update confidence if AI confidence differs significantly
        if 'confidence' in original_results and 'confidence_level' in ai_results:
            ai_confidence = self._parse_confidence(ai_results['confidence_level'])
            if ai_confidence and abs(original_results['confidence'] - ai_confidence) > 20:
                # Average the confidences
                original_results['confidence'] = int((original_results['confidence'] + ai_confidence) / 2)
        
        logger.debug(f"AI enhanced {enhancement_type} for {self.__class__.__name__}")
        return original_results
    
    def _parse_confidence(self, confidence_str: str) -> Optional[int]:
        """Parse confidence level from AI response"""
        if isinstance(confidence_str, (int, float)):
            return int(confidence_str)
        
        confidence_map = {
            'very low': 20,
            'low': 40,
            'medium': 60,
            'high': 80,
            'very high': 95
        }
        
        confidence_lower = str(confidence_str).lower()
        for key, value in confidence_map.items():
            if key in confidence_lower:
                return value
        
        return None
