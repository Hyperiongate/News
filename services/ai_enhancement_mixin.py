"""
AI Enhancement Mixin - COMPLETE FIXED VERSION
Provides AI capabilities to any service that inherits from it
FIXED: Parameter signatures match what services are calling
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
    
    # FIXED: Source Credibility AI Methods - Match service parameters
    def _ai_detect_credibility_issues(self, domain: str, content: str, source_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """AI method to detect credibility issues in sources - FIXED SIGNATURE"""
        if not self._ai_available:
            return None
            
        prompt = f"""Analyze the credibility of this news source:

Domain: {domain}
Content excerpt: {content[:800]}
Database credibility: {source_info.get('credibility', 'Unknown')}
Bias rating: {source_info.get('bias', 'Unknown')}
Source type: {source_info.get('type', 'Unknown')}

Identify:
1. Red flags that indicate low credibility
2. Trust signals that indicate high credibility  
3. Specific concerns based on content and source

Format as JSON with keys:
- red_flags: array of objects with 'issue' and 'explanation' fields
- trust_signals: array of strings
- overall_assessment: string assessment"""

        return self._enhance_with_ai(prompt, temperature=0.2, json_mode=True)
    
    # FIXED: Bias Detection AI Methods - Match service parameters
    def _ai_detect_bias_patterns(self, text: str, initial_findings: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """AI method to detect bias patterns in article text - FIXED SIGNATURE"""
        if not self._ai_available:
            return None
            
        prompt = f"""Analyze additional bias patterns in this news article:

Text excerpt: {text[:1500]}
Initial findings:
- Political bias: {initial_findings.get('political_label', 'Unknown')}
- Sensationalism: {initial_findings.get('sensationalism', 'Unknown')}
- Bias score: {initial_findings.get('bias_score', 0)}/100
- Already detected phrases: {json.dumps(initial_findings.get('loaded_phrases', [])[:3])}

Identify additional subtle bias patterns:
1. Framing issues not yet detected
2. Missing perspectives
3. Subtle manipulation techniques
4. Hidden assumptions

Format as JSON with keys:
- subtle_biases: array of strings
- framing_issues: array of strings
- missing_perspectives: array of strings
- severity_assessment: string (low/medium/high/severe)"""

        return self._enhance_with_ai(prompt, temperature=0.3, json_mode=True)
    
    # FIXED: Author Analysis AI Methods - Match service parameters  
    def _ai_analyze_author(self, author_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """AI method to analyze author credibility - FIXED SIGNATURE"""
        if not self._ai_available:
            return None
        
        author_name = author_data.get('name', 'Unknown')
        bio = author_data.get('bio', '')
        position = author_data.get('position', '')
        article_count = author_data.get('article_count', 0)
            
        prompt = f"""Analyze the credibility of this journalist:

Author: {author_name}
Bio: {bio[:500]}
Position: {position}
Article count: {article_count}

Assess:
1. Professional qualifications
2. Topic expertise indicators
3. Potential bias patterns in background
4. Credibility indicators and red flags
5. Overall assessment

Format as JSON with keys:
- expertise_indicators: array of strings
- red_flags: array of strings  
- positive_indicators: array of strings
- credibility_adjustment: integer from -20 to +20
- overall_assessment: string assessment"""

        return self._enhance_with_ai(prompt, temperature=0.2, json_mode=True)
    
    # FIXED: Manipulation Detection AI Methods - Match service parameters
    def _ai_detect_manipulation(self, text: str, emotional_score: int, tactics_found: List[str]) -> Optional[Dict[str, Any]]:
        """AI method to detect manipulation tactics - FIXED SIGNATURE"""
        if not self._ai_available:
            return None
            
        prompt = f"""Analyze manipulation tactics in this article:

Text excerpt: {text[:1500]}
Emotional intensity score: {emotional_score}/100
Already detected tactics: {json.dumps(tactics_found)}

Identify additional manipulation techniques:
1. Gaslighting patterns
2. False dichotomies not yet caught
3. Appeal to emotion techniques
4. Psychological manipulation tactics
5. Hidden persuasion techniques

Format as JSON with keys:
- gaslighting_patterns: array of strings
- psychological_tactics: array of strings
- emotional_manipulation: array of strings
- severity_assessment: string (low/medium/high)"""

        return self._enhance_with_ai(prompt, temperature=0.3, json_mode=True)
    
    # FIXED: Transparency AI Methods - Match service parameters
    def _ai_analyze_transparency(self, transparency_data: Dict[str, Any], 
                                article_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """AI method to assess transparency - EXISTING SIGNATURE IS CORRECT"""
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

Format as JSON with keys:
- transparency_score: integer 0-100
- missing_elements: array of strings
- red_flags: array of strings
- positive_indicators: array of strings"""

        return self._enhance_with_ai(prompt, temperature=0.2, json_mode=True)
    
    # FIXED: Content Analysis AI Methods - Match service parameters
    def _ai_analyze_content_quality(self, text: str, metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """AI-enhanced content quality analysis - EXISTING SIGNATURE IS CORRECT"""
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

Format as JSON with keys:
- argument_quality: string assessment
- evidence_assessment: string assessment
- clarity_score: integer 0-100
- professionalism: string assessment
- strengths: array of strings
- weaknesses: array of strings"""

        return self._enhance_with_ai(prompt, temperature=0.2, json_mode=True)
    
    # NEW: Fact Checking AI Methods - ADD MISSING METHOD
    def _ai_analyze_claims(self, claims: List[str], article_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """AI method to analyze and prioritize claims for fact checking - NEW METHOD"""
        if not self._ai_available:
            return None
            
        text = article_data.get('text', '')[:1000]
        
        if not claims:
            # Extract claims if none provided
            prompt = f"""Extract factual claims from this news article that should be fact-checked:

Article text: {text}

Identify up to 10 specific, verifiable claims that can be fact-checked.

Format as JSON with key 'claims' containing array of objects with fields:
- claim: string (the specific claim)
- context: string (surrounding context)
- priority: string (high/medium/low)
- type: string (statistic/quote/event/policy)"""
        else:
            prompt = f"""Analyze these claims for fact-checking priority and approach:

Claims to verify:
{json.dumps(claims[:10], indent=2)}

Article context: {text}

For each claim, provide verification guidance.

Format as JSON with key 'claim_analysis' containing array of objects with fields:
- claim: string
- verification_approach: string
- suggested_sources: array of strings
- priority: string (high/medium/low)
- red_flags: array of strings"""

        return self._enhance_with_ai(prompt, temperature=0.2, json_mode=True)
    
    # UTILITY METHODS - Keep existing
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
