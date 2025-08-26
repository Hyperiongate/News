"""
AI Enhancement Mixin - BULLETPROOF VERSION
Provides AI capabilities to any service that inherits from it
FIXED: Bulletproof error handling prevents any crashes
"""
import logging
import json
import os
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class AIEnhancementMixin:
    """
    Bulletproof mixin to add AI capabilities to any analysis service
    Services can inherit from both BaseAnalyzer and this mixin
    FIXED: Never crashes, always degrades gracefully
    """
    
    def __init__(self):
        """Initialize AI client if available - never crashes"""
        self._ai_client = None
        self._ai_model = "gpt-3.5-turbo"
        self._ai_available = False
        self._ai_error_count = 0
        self._ai_max_errors = 3  # Disable AI after 3 errors
        
        try:
            # Use environment variables directly to avoid Config dependency
            api_key = os.environ.get('OPENAI_API_KEY')
            
            if api_key:
                try:
                    from openai import OpenAI
                    self._ai_client = OpenAI(api_key=api_key)
                    self._ai_available = True
                    logger.info(f"{self.__class__.__name__} AI enhancement initialized")
                except ImportError:
                    logger.info(f"OpenAI library not installed for {self.__class__.__name__} - AI features disabled")
                except Exception as e:
                    logger.info(f"AI client initialization failed for {self.__class__.__name__}: {e}")
            else:
                logger.debug(f"No OpenAI API key configured for {self.__class__.__name__} - AI features disabled")
                
        except Exception as e:
            logger.warning(f"AI enhancement initialization error for {self.__class__.__name__}: {e}")
            self._ai_available = False
    
    def _is_ai_available(self) -> bool:
        """Check if AI is available and not disabled due to errors"""
        return self._ai_available and self._ai_error_count < self._ai_max_errors
    
    def _enhance_with_ai(self, prompt: str, temperature: float = 0.3, 
                        max_tokens: int = 1000, json_mode: bool = False) -> Optional[Dict[str, Any]]:
        """
        Generic AI enhancement method - BULLETPROOF VERSION
        Never crashes, always returns None on any error
        
        Args:
            prompt: The prompt to send to AI
            temperature: Creativity level (0-1)
            max_tokens: Maximum response length
            json_mode: Whether to request JSON response
            
        Returns:
            AI response dict or None if unavailable/failed
        """
        # Quick availability check
        if not self._is_ai_available():
            return None
            
        try:
            # Validate inputs
            if not prompt or not isinstance(prompt, str) or len(prompt.strip()) == 0:
                logger.debug("AI enhancement: Invalid prompt provided")
                return None
            
            # Limit prompt size to prevent API errors
            if len(prompt) > 8000:
                prompt = prompt[:8000] + "..."
            
            messages = [
                {"role": "system", "content": "You are an expert news analysis AI assistant."},
                {"role": "user", "content": prompt}
            ]
            
            kwargs = {
                "model": self._ai_model,
                "messages": messages,
                "temperature": max(0.0, min(1.0, temperature)),  # Clamp temperature
                "max_tokens": max(10, min(4000, max_tokens))  # Clamp tokens
            }
            
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            
            # Make the API call with timeout
            response = self._ai_client.chat.completions.create(**kwargs)
            
            if not response or not response.choices:
                logger.debug("AI enhancement: Empty response from API")
                return None
            
            content = response.choices[0].message.content
            
            if not content:
                logger.debug("AI enhancement: Empty content in API response")
                return None
            
            if json_mode:
                try:
                    parsed = json.loads(content)
                    # Validate that it's actually a dict
                    if isinstance(parsed, dict):
                        return parsed
                    else:
                        logger.debug("AI enhancement: JSON response is not a dictionary")
                        return None
                except json.JSONDecodeError as e:
                    logger.debug(f"AI enhancement: Failed to parse JSON: {e}")
                    return None
            else:
                return {"response": content}
                
        except Exception as e:
            self._ai_error_count += 1
            logger.debug(f"AI enhancement failed (error #{self._ai_error_count}): {e}")
            
            # Disable AI if too many errors
            if self._ai_error_count >= self._ai_max_errors:
                logger.info(f"AI enhancement disabled for {self.__class__.__name__} due to repeated errors")
                self._ai_available = False
            
            return None
    
    # BULLETPROOF AI METHODS - All return None gracefully on any error
    
    def _ai_detect_credibility_issues(self, domain: str = "", content: str = "", 
                                    source_info: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """AI credibility analysis - bulletproof version"""
        try:
            if not self._is_ai_available():
                return None
                
            source_info = source_info or {}
            
            prompt = f"""Analyze the credibility of this news source:

Domain: {domain or 'Unknown'}
Content excerpt: {(content or '')[:800]}
Database credibility: {source_info.get('credibility', 'Unknown')}
Bias rating: {source_info.get('bias', 'Unknown')}
Source type: {source_info.get('type', 'Unknown')}

Identify red flags and trust signals.

Format as JSON with keys:
- red_flags: array of objects with 'issue' and 'explanation' fields
- trust_signals: array of strings
- overall_assessment: string assessment"""

            result = self._enhance_with_ai(prompt, temperature=0.2, json_mode=True)
            
            # Validate result structure
            if result and isinstance(result, dict):
                # Ensure expected keys exist with defaults
                result.setdefault('red_flags', [])
                result.setdefault('trust_signals', [])
                result.setdefault('overall_assessment', 'Unable to assess')
                return result
            
            return None
            
        except Exception as e:
            logger.debug(f"AI credibility analysis failed: {e}")
            return None
    
    def _ai_detect_bias_patterns(self, text: str = "", initial_findings: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """AI bias detection - bulletproof version"""
        try:
            if not self._is_ai_available():
                return None
                
            initial_findings = initial_findings or {}
            
            prompt = f"""Analyze bias patterns in this article:

Text excerpt: {(text or '')[:1500]}
Initial findings:
- Political bias: {initial_findings.get('political_label', 'Unknown')}
- Bias score: {initial_findings.get('bias_score', 0)}/100

Identify subtle bias patterns not yet detected.

Format as JSON with keys:
- subtle_biases: array of strings
- framing_issues: array of strings
- missing_perspectives: array of strings
- severity_assessment: string"""

            result = self._enhance_with_ai(prompt, temperature=0.3, json_mode=True)
            
            # Validate result structure
            if result and isinstance(result, dict):
                result.setdefault('subtle_biases', [])
                result.setdefault('framing_issues', [])
                result.setdefault('missing_perspectives', [])
                result.setdefault('severity_assessment', 'low')
                return result
            
            return None
            
        except Exception as e:
            logger.debug(f"AI bias analysis failed: {e}")
            return None
    
    def _ai_analyze_author(self, author_data: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """AI author analysis - bulletproof version"""
        try:
            if not self._is_ai_available():
                return None
                
            author_data = author_data or {}
            author_name = author_data.get('name', author_data.get('author_name', 'Unknown'))
            bio = author_data.get('bio', '')
            position = author_data.get('position', '')
            article_count = author_data.get('article_count', 0)
            
            prompt = f"""Analyze this journalist's credibility:

Author: {author_name}
Bio: {bio[:500]}
Position: {position}
Article count: {article_count}

Assess professional qualifications and credibility.

Format as JSON with keys:
- expertise_indicators: array of strings
- red_flags: array of strings
- positive_indicators: array of strings
- credibility_adjustment: integer from -20 to +20
- overall_assessment: string"""

            result = self._enhance_with_ai(prompt, temperature=0.2, json_mode=True)
            
            # Validate result structure
            if result and isinstance(result, dict):
                result.setdefault('expertise_indicators', [])
                result.setdefault('red_flags', [])
                result.setdefault('positive_indicators', [])
                result.setdefault('credibility_adjustment', 0)
                result.setdefault('overall_assessment', 'Unable to assess')
                return result
            
            return None
            
        except Exception as e:
            logger.debug(f"AI author analysis failed: {e}")
            return None
    
    def _ai_detect_manipulation(self, text: str = "", emotional_score: int = 0, 
                              tactics_found: List[str] = None) -> Optional[Dict[str, Any]]:
        """AI manipulation detection - bulletproof version"""
        try:
            if not self._is_ai_available():
                return None
                
            tactics_found = tactics_found or []
            
            prompt = f"""Analyze manipulation tactics in this article:

Text excerpt: {(text or '')[:1500]}
Emotional intensity: {emotional_score}/100
Detected tactics: {json.dumps(tactics_found[:5])}

Identify additional manipulation techniques.

Format as JSON with keys:
- emotional_tactics: array of strings
- logical_fallacies: array of strings
- psychological_tactics: array of strings
- severity: string (low/medium/high)"""

            result = self._enhance_with_ai(prompt, temperature=0.3, json_mode=True)
            
            # Validate result structure
            if result and isinstance(result, dict):
                result.setdefault('emotional_tactics', [])
                result.setdefault('logical_fallacies', [])
                result.setdefault('psychological_tactics', [])
                result.setdefault('severity', 'low')
                return result
            
            return None
            
        except Exception as e:
            logger.debug(f"AI manipulation analysis failed: {e}")
            return None
    
    def _ai_analyze_transparency(self, transparency_data: Dict[str, Any] = None, 
                                article_data: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """AI transparency analysis - bulletproof version"""
        try:
            if not self._is_ai_available():
                return None
                
            transparency_data = transparency_data or {}
            article_data = article_data or {}
            
            prompt = f"""Assess article transparency:

Title: {article_data.get('title', 'Unknown')}
Author: {article_data.get('author', 'Unknown')}
Source count: {transparency_data.get('source_count', 0)}
Has disclosures: {transparency_data.get('has_disclosures', False)}

Evaluate transparency quality.

Format as JSON with keys:
- transparency_score: integer 0-100
- missing_elements: array of strings
- red_flags: array of strings
- positive_indicators: array of strings"""

            result = self._enhance_with_ai(prompt, temperature=0.2, json_mode=True)
            
            # Validate result structure
            if result and isinstance(result, dict):
                result.setdefault('transparency_score', 50)
                result.setdefault('missing_elements', [])
                result.setdefault('red_flags', [])
                result.setdefault('positive_indicators', [])
                return result
            
            return None
            
        except Exception as e:
            logger.debug(f"AI transparency analysis failed: {e}")
            return None
    
    def _ai_analyze_content_quality(self, text: str = "", metrics: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """AI content quality analysis - bulletproof version"""
        try:
            if not self._is_ai_available():
                return None
                
            metrics = metrics or {}
            
            prompt = f"""Analyze content quality:

Text preview: {(text or '')[:1000]}
Readability: {metrics.get('readability_score', 'Unknown')}
Complexity: {metrics.get('sentence_complexity', 'Unknown')}

Assess quality and professionalism.

Format as JSON with keys:
- quality_score: integer 0-100
- strengths: array of strings
- weaknesses: array of strings
- professionalism: string (low/medium/high)"""

            result = self._enhance_with_ai(prompt, temperature=0.2, json_mode=True)
            
            # Validate result structure
            if result and isinstance(result, dict):
                result.setdefault('quality_score', 50)
                result.setdefault('strengths', [])
                result.setdefault('weaknesses', [])
                result.setdefault('professionalism', 'medium')
                return result
            
            return None
            
        except Exception as e:
            logger.debug(f"AI content analysis failed: {e}")
            return None
    
    def _ai_analyze_claims(self, claims: List[str] = None, text: str = "") -> Optional[Dict[str, Any]]:
        """AI claims analysis - bulletproof version"""
        try:
            if not self._is_ai_available():
                return None
                
            claims = claims or []
            
            if not claims:
                # Extract claims if none provided
                prompt = f"""Extract factual claims from this text:

{(text or '')[:1500]}

Format as JSON with key 'claims' containing array of claim strings."""
            else:
                prompt = f"""Analyze these claims for fact-checking:

Claims: {json.dumps(claims[:10])}
Context: {(text or '')[:500]}

Format as JSON with key 'claim_analysis' containing array of objects with fields:
- claim: string
- priority: string (high/medium/low)
- verification_approach: string"""

            result = self._enhance_with_ai(prompt, temperature=0.2, json_mode=True)
            
            # Validate result structure
            if result and isinstance(result, dict):
                if 'claims' not in result and 'claim_analysis' not in result:
                    result['claims'] = []
                return result
            
            return None
            
        except Exception as e:
            logger.debug(f"AI claims analysis failed: {e}")
            return None
    
    def _safely_enhance_service_result(self, service_results: Dict[str, Any], 
                                     ai_method_name: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Safely enhance service results with AI - never crashes
        
        Args:
            service_results: Original service results to enhance
            ai_method_name: Name of AI method to call
            *args, **kwargs: Arguments to pass to AI method
            
        Returns:
            Enhanced results or original results if AI fails
        """
        try:
            # Get the AI method
            ai_method = getattr(self, ai_method_name, None)
            if not ai_method or not callable(ai_method):
                logger.debug(f"AI method {ai_method_name} not found")
                return service_results
            
            # Call AI method safely
            ai_result = ai_method(*args, **kwargs)
            
            if ai_result and isinstance(ai_result, dict):
                # Add AI insights to results
                if 'ai_insights' not in service_results:
                    service_results['ai_insights'] = {}
                
                service_results['ai_insights'][ai_method_name] = ai_result
                
                # Mark as AI-enhanced
                if 'metadata' not in service_results:
                    service_results['metadata'] = {}
                
                service_results['metadata']['ai_enhanced'] = True
                
                logger.debug(f"AI enhancement {ai_method_name} successful")
            else:
                logger.debug(f"AI enhancement {ai_method_name} returned no usable data")
            
            return service_results
            
        except Exception as e:
            logger.debug(f"Safe AI enhancement failed for {ai_method_name}: {e}")
            return service_results  # Always return original results
