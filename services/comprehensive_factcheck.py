"""
File: services/comprehensive_factcheck.py
Last Updated: October 14, 2025
Description: Comprehensive Fact-Checking Service using multiple APIs and AI
Changes:
- Created as new file for news repository from transcript repository
- Uses Google Fact Check API, OpenAI, and pattern analysis
- Aggressive AI analysis to minimize "needs context" results
- Handles empty rhetoric and unsubstantiated predictions
- Returns standardized verdict with confidence scores
"""

import re
import logging
import requests
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Verdict categories for standardized responses
VERDICT_CATEGORIES = {
    'true': {
        'label': 'True',
        'icon': '✅',
        'color': '#10b981',
        'score': 100,
        'description': 'The claim is accurate and supported by evidence'
    },
    'mostly_true': {
        'label': 'Mostly True',
        'icon': '✓',
        'color': '#34d399',
        'score': 85,
        'description': 'The claim is largely accurate with minor imprecision'
    },
    'nearly_true': {
        'label': 'Nearly True',
        'icon': '🔵',
        'color': '#6ee7b7',
        'score': 70,
        'description': 'Largely accurate but missing some context'
    },
    'exaggeration': {
        'label': 'Exaggeration',
        'icon': '📏',
        'color': '#fbbf24',
        'score': 50,
        'description': 'Based on truth but overstated'
    },
    'misleading': {
        'label': 'Misleading',
        'icon': '⚠️',
        'color': '#f59e0b',
        'score': 35,
        'description': 'Contains truth but creates false impression'
    },
    'mostly_false': {
        'label': 'Mostly False',
        'icon': '❌',
        'color': '#f87171',
        'score': 20,
        'description': 'Significant inaccuracies with grain of truth'
    },
    'false': {
        'label': 'False',
        'icon': '❌',
        'color': '#ef4444',
        'score': 0,
        'description': 'Demonstrably incorrect'
    },
    'empty_rhetoric': {
        'label': 'Empty Rhetoric',
        'icon': '💨',
        'color': '#94a3b8',
        'score': None,
        'description': 'Vague promises or boasts with no substantive content'
    },
    'unsubstantiated_prediction': {
        'label': 'Unsubstantiated Prediction',
        'icon': '🔮',
        'color': '#a78bfa',
        'score': None,
        'description': 'Future claim with no evidence or plan provided'
    },
    'needs_context': {
        'label': 'Needs Context',
        'icon': '❓',
        'color': '#8b5cf6',
        'score': None,
        'description': 'Cannot verify without additional information'
    },
    'opinion': {
        'label': 'Opinion',
        'icon': '💭',
        'color': '#6366f1',
        'score': None,
        'description': 'Subjective claim analyzed for factual elements'
    }
}


class ComprehensiveFactChecker:
    """Enhanced fact-checking that aggressively analyzes claims with AI"""
    
    def __init__(self, config):
        self.config = config
        self.current_speaker = None
        self.full_transcript = None  # Store full transcript for better context
        
        # Initialize API keys
        self.google_api_key = getattr(config, 'GOOGLE_FACTCHECK_API_KEY', None)
        self.openai_api_key = getattr(config, 'OPENAI_API_KEY', None)
        
        # Initialize OpenAI
        self.openai_client = None
        if self.openai_api_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=self.openai_api_key)
                logger.info("OpenAI client initialized for fact-checking")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")
        
        # Settings
        self.force_verdict = getattr(config, 'FORCE_VERDICT_ON_ALL_CLAIMS', True)
        self.confidence_threshold = getattr(config, 'CONFIDENCE_THRESHOLD_FOR_VERDICT', 50)
    
    def check_claim_with_verdict(self, claim: str, context: Optional[Dict] = None) -> Dict:
        """Main entry point - check claim using all available resources"""
        try:
            # Clean claim
            claim = claim.strip()
            
            # Store transcript context for better analysis
            if context and context.get('transcript'):
                self.full_transcript = context['transcript']
            
            # Set current speaker for pattern analysis
            self.current_speaker = context.get('speaker', 'Unknown') if context else 'Unknown'
            
            # Check if this is trivial content
            if self._is_trivial_claim(claim):
                return None  # Skip trivial claims entirely
            
            # Check for empty rhetoric patterns first
            rhetoric_check = self._check_empty_rhetoric(claim)
            if rhetoric_check:
                return self._create_final_result(claim, rhetoric_check, context)
            
            # Check for unsubstantiated predictions
            prediction_check = self._check_unsubstantiated_prediction(claim)
            if prediction_check:
                return self._create_final_result(claim, prediction_check, context)
            
            # Use AI for comprehensive analysis if available
            if self.openai_client:
                ai_result = self._ai_comprehensive_analysis(claim, context)
                if ai_result and ai_result.get('verdict') != 'needs_context':
                    return self._create_final_result(claim, ai_result, context)
            
            # Fallback to Google Fact Check API
            if self.google_api_key:
                api_result = self._check_google_factcheck_api(claim)
                if api_result and api_result.get('verdict') != 'needs_context':
                    return self._create_final_result(claim, api_result, context)
            
            # Last resort: analyze claim structure for a verdict
            structural_analysis = self._analyze_claim_structure(claim)
            return self._create_final_result(claim, structural_analysis, context)
            
        except Exception as e:
            logger.error(f"Error checking claim '{claim}': {e}")
            return {
                'claim': claim,
                'speaker': self.current_speaker,
                'verdict': 'error',
                'explanation': f'Analysis failed: {str(e)}',
                'confidence': 0,
                'sources': [],
                'timestamp': datetime.now().isoformat()
            }
    
    def _is_trivial_claim(self, claim: str) -> bool:
        """Check if claim is too trivial to fact-check"""
        if len(claim.strip()) < 10:
            return True
            
        # Skip greetings, thanks, etc.
        trivial_patterns = [
            r'^(hello|hi|hey|thanks|thank you|good morning|good evening)',
            r'^(yes|no|okay|ok|sure|right|exactly)\.?\s*$',
            r'^(um|uh|er|ah)\s',
            r'^\s*\.\.\.\s*$'
        ]
        
        for pattern in trivial_patterns:
            if re.match(pattern, claim.lower().strip()):
                return True
        
        return False
    
    def _check_empty_rhetoric(self, claim: str) -> Optional[Dict]:
        """Check for vague promises or empty rhetoric"""
        claim_lower = claim.lower().strip()
        
        # Patterns for empty promises
        rhetoric_patterns = [
            r'\b(will be|going to be)\s+(the )?(best|greatest|most|biggest|largest|strongest)\b',
            r'\b(nobody|no one)\s+(has ever|will ever)\b',
            r'\b(everyone|everybody)\s+(knows|agrees|wants)\b',
            r'\b(totally|completely|absolutely)\s+(destroy|fix|solve|end)\b',
            r'\b(make .* great again|better than ever)\b'
        ]
        
        has_rhetoric = any(re.search(pattern, claim_lower) for pattern in rhetoric_patterns)
        
        if has_rhetoric:
            # Check if there's any specific detail or evidence
            specificity_patterns = [
                r'\b\d+\.?\d*\s*%',  # Percentages
                r'\b\d{1,3}(,\d{3})*',  # Numbers
                r'\b(by|within|before)\s+\d{4}\b',  # Dates
                r'\b(plan|proposal|bill|legislation)\b',  # Specific policy references
            ]
            
            has_specifics = any(re.search(pattern, claim_lower) for pattern in specificity_patterns)
            
            if not has_specifics:
                return {
                    'verdict': 'empty_rhetoric',
                    'explanation': 'This statement contains vague superlatives or promises without specific, verifiable details or evidence.',
                    'confidence': 75,
                    'sources': []
                }
        
        return None
    
    def _check_unsubstantiated_prediction(self, claim: str) -> Optional[Dict]:
        """Check for unsubstantiated future predictions"""
        claim_lower = claim.lower().strip()
        
        # Look for future-tense predictions without supporting evidence
        prediction_patterns = [
            r'\b(will|going to|shall)\s+\w+\s+(by|in|within)\s+\d+\s+(years?|months?|days?)\b',
            r'\b(predict|forecast|expect|anticipate)\s+\w+\s+will\b',
            r'\bin\s+(the future|coming years|next decade)\b',
            r'\b(will definitely|will certainly|guaranteed to)\b'
        ]
        
        has_prediction = any(re.search(pattern, claim_lower) for pattern in prediction_patterns)
        
        if has_prediction:
            # Check if there's evidence or a plan mentioned
            evidence_patterns = [
                r'\b(because|since|due to|based on)\b',
                r'\b(data shows|studies show|research indicates)\b',
                r'\b(plan|strategy|approach|method)\b',
                r'\b(budget|funding|investment)\b'
            ]
            
            has_evidence = any(re.search(pattern, claim_lower) for pattern in evidence_patterns)
            
            if not has_evidence:
                return {
                    'verdict': 'unsubstantiated_prediction',
                    'explanation': 'This is a future-oriented claim without presented evidence, plan, or methodology to support the prediction.',
                    'confidence': 70,
                    'sources': []
                }
        
        return None
    
    def _ai_comprehensive_analysis(self, claim: str, context: Optional[Dict]) -> Optional[Dict]:
        """Use AI for comprehensive claim analysis"""
        if not self.openai_client:
            return None
        
        try:
            # Build comprehensive prompt
            prompt = self._build_ai_analysis_prompt(claim, context)
            
            response = self.openai_client.chat.completions.create(
                model=getattr(self.config, 'OPENAI_MODEL', 'gpt-4'),
                messages=[
                    {"role": "system", "content": "You are an expert fact-checker. Analyze claims thoroughly and always provide a definitive verdict with high confidence."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            return self._parse_ai_response(response.choices[0].message.content)
            
        except Exception as e:
            logger.warning(f"AI analysis failed: {e}")
            return None
    
    def _build_ai_analysis_prompt(self, claim: str, context: Optional[Dict]) -> str:
        """Build comprehensive AI analysis prompt"""
        prompt_parts = [
            f"Analyze this claim for factual accuracy: \"{claim}\"",
            "",
            "Consider these aspects:",
            "1. Is this a verifiable factual claim or opinion/rhetoric?",
            "2. Can this be checked against known data or evidence?",
            "3. Are there any logical inconsistencies or red flags?",
            "4. What is the most appropriate verdict?"
        ]
        
        if context:
            if context.get('speaker'):
                prompt_parts.append(f"5. Speaker: {context['speaker']}")
            if context.get('topics'):
                prompt_parts.append(f"6. Topics: {', '.join(context['topics'])}")
        
        prompt_parts.extend([
            "",
            "Provide your analysis in this format:",
            "VERDICT: [true|mostly_true|nearly_true|exaggeration|misleading|mostly_false|false|empty_rhetoric|unsubstantiated_prediction|opinion]",
            "CONFIDENCE: [50-95]",
            "EXPLANATION: [detailed explanation]",
            "",
            "Always provide a definitive verdict. Avoid 'needs_context' unless absolutely impossible to analyze."
        ])
        
        return "\n".join(prompt_parts)
    
    def _parse_ai_response(self, response: str) -> Optional[Dict]:
        """Parse AI response into structured result"""
        try:
            lines = response.strip().split('\n')
            result = {}
            
            for line in lines:
                if line.startswith('VERDICT:'):
                    verdict = line.replace('VERDICT:', '').strip().lower()
                    result['verdict'] = self._normalize_verdict(verdict)
                elif line.startswith('CONFIDENCE:'):
                    confidence = re.findall(r'\d+', line)
                    result['confidence'] = int(confidence[0]) if confidence else 60
                elif line.startswith('EXPLANATION:'):
                    result['explanation'] = line.replace('EXPLANATION:', '').strip()
            
            # Ensure minimum fields
            if 'verdict' not in result:
                result['verdict'] = 'opinion'
            if 'confidence' not in result:
                result['confidence'] = 60
            if 'explanation' not in result:
                result['explanation'] = 'AI analysis completed but detailed explanation not available.'
            
            result['sources'] = ['AI Analysis']
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            return None
    
    def _check_google_factcheck_api(self, claim: str) -> Optional[Dict]:
        """Check claim against Google Fact Check API"""
        if not self.google_api_key:
            return None
        
        try:
            url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
            params = {
                'key': self.google_api_key,
                'query': claim,
                'languageCode': 'en'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                claims = data.get('claims', [])
                
                if claims:
                    # Use the first matching claim
                    first_claim = claims[0]
                    claim_review = first_claim.get('claimReview', [{}])[0]
                    
                    # Extract verdict
                    rating = claim_review.get('textualRating', '').lower()
                    verdict = self._map_google_rating_to_verdict(rating)
                    
                    # Extract explanation
                    explanation = claim_review.get('title', 'Verified by fact-checkers.')
                    
                    # Extract sources
                    publisher = claim_review.get('publisher', {}).get('name', 'Fact-checker')
                    url = claim_review.get('url', '')
                    sources = [f"{publisher}: {url}"] if url else [publisher]
                    
                    # Calculate confidence based on rating clarity
                    confidence = 75 if verdict in ['true', 'false'] else 65
                    
                    return {
                        'verdict': verdict,
                        'explanation': explanation,
                        'confidence': confidence,
                        'sources': sources
                    }
            
            return None
            
        except Exception as e:
            logger.warning(f"Google Fact Check API error: {e}")
            return None
    
    def _map_google_rating_to_verdict(self, rating: str) -> str:
        """Map Google's textual ratings to our verdict categories"""
        rating = rating.lower()
        
        if any(word in rating for word in ['true', 'correct', 'accurate']):
            if 'mostly' in rating:
                return 'mostly_true'
            return 'true'
        
        if any(word in rating for word in ['false', 'incorrect', 'inaccurate']):
            if 'mostly' in rating:
                return 'mostly_false'
            return 'false'
        
        if any(word in rating for word in ['misleading', 'distorts']):
            return 'misleading'
        
        if any(word in rating for word in ['exaggerat', 'inflat']):
            return 'exaggeration'
        
        if any(word in rating for word in ['mixed', 'half', 'partial']):
            return 'nearly_true'
        
        if any(word in rating for word in ['opinion', 'commentary']):
            return 'opinion'
        
        return 'needs_context'
    
    def _analyze_claim_structure(self, claim: str) -> Dict:
        """Analyze claim structure for patterns when other methods fail"""
        claim_lower = claim.lower().strip()
        
        # Check for statistical/numerical claims
        if re.search(r'\b\d+(\.\d+)?%?\b', claim) or re.search(r'\b(million|billion|trillion)\b', claim):
            return self._create_verdict(
                'needs_context',
                'This claim contains specific numbers or statistics that require verification against authoritative sources.',
                confidence=55
            )
        
        # Check for comparative claims
        if re.search(r'\b(more|less|higher|lower|better|worse|faster|slower)\s+than\b', claim_lower):
            return self._create_verdict(
                'needs_context', 
                'This is a comparative claim that requires specific data points and context for verification.',
                confidence=55
            )
        
        # Check for opinion/subjective language
        opinion_indicators = ['think', 'believe', 'feel', 'opinion', 'seems', 'appears', 'probably', 'maybe', 'might']
        if any(indicator in claim_lower for indicator in opinion_indicators):
            return self._create_verdict(
                'opinion',
                'This appears to be an opinion or subjective statement rather than a factual claim that can be definitively verified.',
                confidence=65
            )
        
        # Check for policy/value statements
        if re.search(r'\b(should|must|ought to|need to|have to)\b', claim_lower):
            return self._create_verdict(
                'opinion',
                'This statement expresses what should be done (normative claim) rather than what is factually the case.',
                confidence=55
            )
        
        # Default to opinion for unclassifiable claims
        return self._create_verdict(
            'opinion',
            'This statement does not appear to make specific, verifiable factual claims.',
            confidence=50
        )
    
    def _normalize_verdict(self, verdict: str) -> str:
        """Normalize verdict strings"""
        if not verdict:
            return 'opinion'
            
        verdict = verdict.lower().strip().replace(' ', '_')
        
        # Direct mappings
        verdict_map = {
            'true': 'true',
            'mostly_true': 'mostly_true', 
            'nearly_true': 'nearly_true',
            'exaggeration': 'exaggeration',
            'misleading': 'misleading',
            'mostly_false': 'mostly_false',
            'false': 'false',
            'empty_rhetoric': 'empty_rhetoric',
            'unsubstantiated_prediction': 'unsubstantiated_prediction',
            'opinion': 'opinion',
            'mixed': 'exaggeration',  # Treat mixed as exaggeration
            'needs_context': 'needs_context'
        }
        
        return verdict_map.get(verdict, 'opinion')
    
    def _create_verdict(self, verdict: str, explanation: str, confidence: int = 60, sources: List[str] = None) -> Dict:
        """Create standardized verdict"""
        return {
            'verdict': verdict,
            'verdict_details': VERDICT_CATEGORIES.get(verdict, VERDICT_CATEGORIES['needs_context']),
            'explanation': explanation,
            'confidence': max(confidence, 50),  # Minimum confidence of 50
            'sources': sources or [],
            'timestamp': datetime.now().isoformat()
        }
    
    def _create_final_result(self, original_claim: str, analysis_result: Dict, context: Optional[Dict]) -> Dict:
        """Create final formatted result"""
        return {
            'claim': original_claim,
            'speaker': context.get('speaker', 'Unknown') if context else 'Unknown',
            'verdict': analysis_result.get('verdict', 'opinion'),
            'explanation': analysis_result.get('explanation', 'No explanation available'),
            'confidence': analysis_result.get('confidence', 50),
            'sources': analysis_result.get('sources', []),
            'timestamp': analysis_result.get('timestamp', datetime.now().isoformat())
        }


# Compatibility - ensure this class can be imported as FactChecker
FactChecker = ComprehensiveFactChecker
