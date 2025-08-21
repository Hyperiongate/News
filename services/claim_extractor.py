# services/claim_extractor.py
"""
Claim Extraction Service - AI ENHANCED VERSION
Extracts and categorizes factual claims from articles with AI assistance
"""

import re
import logging
from typing import Dict, List, Any
from services.base_analyzer import BaseAnalyzer
from services.ai_enhancement_mixin import AIEnhancementMixin

logger = logging.getLogger(__name__)

class ClaimExtractor(BaseAnalyzer, AIEnhancementMixin):
    """Extract factual claims from article content with AI enhancement"""
    
    def __init__(self):
        """Initialize claim patterns and AI"""
        super().__init__('claim_extractor')
        AIEnhancementMixin.__init__(self)
        self._initialize_patterns()
        logger.info(f"ClaimExtractor initialized with AI: {self._ai_available}")
    
    def _check_availability(self) -> bool:
        """Service is always available"""
        return True
    
    def _initialize_patterns(self):
        """Initialize patterns for claim detection"""
        # Statistical claim patterns
        self.stat_patterns = [
            r'\b\d+\.?\d*\s*%',  # Percentages
            r'\b\d{1,3}(,\d{3})*(\.\d+)?\s+(people|dollars|euros|pounds|deaths|cases|victims)',
            r'\b(increased|decreased|rose|fell|jumped)\s+by\s+\d+',
            r'\b(more|less|fewer)\s+than\s+\d+',
            r'\b\d+\s+out\s+of\s+\d+',
            r'\b(doubled|tripled|quadrupled|halved)',
            r'\bmajority\s+of',
            r'\b(most|many|few|several)\s+\w+\s+(are|were|have|had)'
        ]
        
        # Causal claim patterns
        self.causal_patterns = [
            r'(causes?|caused|causing)',
            r'(leads?\s+to|led\s+to|leading\s+to)',
            r'(results?\s+in|resulted\s+in|resulting\s+in)',
            r'(because\s+of|due\s+to|owing\s+to)',
            r'(contributes?\s+to|contributed\s+to)',
            r'(responsible\s+for)',
            r'(triggers?|triggered)',
            r'(creates?|created|creating)'
        ]
        
        # Comparison claim patterns
        self.comparison_patterns = [
            r'(more|less|fewer)\s+than',
            r'(better|worse)\s+than',
            r'(higher|lower)\s+than',
            r'(bigger|smaller)\s+than',
            r'compared\s+to',
            r'in\s+contrast\s+to',
            r'unlike',
            r'whereas'
        ]
        
        # Attribution patterns
        self.attribution_patterns = [
            r'according\s+to\s+([^,\.]+)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+said',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+stated',
            r'study\s+by\s+([^,\.]+)',
            r'research\s+from\s+([^,\.]+)',
            r'report\s+by\s+([^,\.]+)',
            r'survey\s+conducted\s+by\s+([^,\.]+)'
        ]
        
        # Temporal claim patterns
        self.temporal_patterns = [
            r'(will|would|could|may|might)\s+\w+',
            r'by\s+\d{4}',
            r'in\s+the\s+next\s+\d+\s+(years?|months?|weeks?|days?)',
            r'(yesterday|today|tomorrow)',
            r'last\s+(year|month|week)',
            r'this\s+(year|month|week)',
            r'next\s+(year|month|week)'
        ]
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract claims from article using BaseAnalyzer interface
        """
        try:
            content = data.get('content') or data.get('text', '')
            
            if not content:
                return {
                    'service': self.service_name,
                    'success': True,
                    'data': {
                        'claims': [],
                        'claim_count': 0,
                        'claim_types': {}
                    },
                    'metadata': {
                        'ai_enhanced': False
                    }
                }
            
            # Extract claims using patterns
            result = self.extract_claims({'content': content})
            
            # AI ENHANCEMENT - Extract additional claims
            if self._ai_available and content:
                logger.info("Enhancing claim extraction with AI")
                
                # Use the AI fact-check claims method from mixin
                ai_claims = self._ai_fact_check_claims(
                    claims=[],  # Empty list to trigger claim extraction
                    context=content[:2000]  # Provide context for extraction
                )
                
                if ai_claims and ai_claims.get('claims'):
                    # Convert AI claims to our format
                    for ai_claim in ai_claims['claims'][:5]:  # Add up to 5 AI claims
                        claim_text = ai_claim.get('claim', '')
                        if claim_text and len(claim_text) > 20:
                            # Check if this claim isn't already in our list
                            already_found = any(
                                claim['text'].lower() in claim_text.lower() or
                                claim_text.lower() in claim['text'].lower()
                                for claim in result['claims']
                            )
                            
                            if not already_found:
                                result['claims'].append({
                                    'text': claim_text,
                                    'type': 'ai_extracted',
                                    'importance': ai_claim.get('verifiability', 'medium'),
                                    'verifiable': ai_claim.get('verifiability', 'medium') != 'hard',
                                    'source': 'ai'
                                })
                                
                                # Update claim types
                                if 'ai_extracted' not in result['claim_types']:
                                    result['claim_types']['ai_extracted'] = []
                                result['claim_types']['ai_extracted'].append({
                                    'text': claim_text,
                                    'type': 'ai_extracted',
                                    'importance': ai_claim.get('verifiability', 'medium'),
                                    'verifiable': ai_claim.get('verifiability', 'medium') != 'hard'
                                })
                    
                    # Update claim count
                    result['claim_count'] = len(result['claims'])
                    result['ai_claims_added'] = len([c for c in result['claims'] if c.get('source') == 'ai'])
            
            # Format as standard service response
            return {
                'service': self.service_name,
                'success': True,
                'data': result,
                'metadata': {
                    'ai_enhanced': self._ai_available,
                    'total_claims': result['claim_count'],
                    'claim_breakdown': {
                        claim_type: len(claims) 
                        for claim_type, claims in result['claim_types'].items()
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Claim extraction failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def extract_claims(self, article_data):
        """
        Extract claims from article (original method maintained for compatibility)
        
        Args:
            article_data: Dictionary containing article information
            
        Returns:
            Dictionary with extracted claims
        """
        content = article_data.get('content') or article_data.get('text', '')
        
        if not content:
            return {'claims': [], 'claim_count': 0, 'claim_types': {}}
        
        # Extract different types of claims
        claims = []
        
        # Extract statistical claims
        stat_claims = self._extract_statistical_claims(content)
        claims.extend(stat_claims)
        
        # Extract causal claims
        causal_claims = self._extract_causal_claims(content)
        claims.extend(causal_claims)
        
        # Extract comparison claims
        comparison_claims = self._extract_comparison_claims(content)
        claims.extend(comparison_claims)
        
        # Extract temporal/predictive claims
        temporal_claims = self._extract_temporal_claims(content)
        claims.extend(temporal_claims)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_claims = []
        for claim in claims:
            claim_text = claim['text'].lower()
            if claim_text not in seen:
                seen.add(claim_text)
                unique_claims.append(claim)
        
        # Categorize claims by type
        claim_types = {}
        for claim in unique_claims:
            claim_type = claim['type']
            if claim_type not in claim_types:
                claim_types[claim_type] = []
            claim_types[claim_type].append(claim)
        
        return {
            'claims': unique_claims[:20],  # Limit to top 20 claims
            'claim_count': len(unique_claims),
            'claim_types': claim_types
        }
    
    def _extract_statistical_claims(self, text):
        """Extract statistical claims"""
        claims = []
        sentences = self._split_into_sentences(text)
        
        for sentence in sentences:
            for pattern in self.stat_patterns:
                matches = re.finditer(pattern, sentence, re.IGNORECASE)
                for match in matches:
                    # Get context around the match
                    start = max(0, match.start() - 50)
                    end = min(len(sentence), match.end() + 50)
                    context = sentence[start:end].strip()
                    
                    # Extract the specific claim
                    claim_text = self._clean_claim_text(context)
                    
                    if len(claim_text) > 20:  # Ensure meaningful claim
                        claims.append({
                            'text': claim_text,
                            'type': 'statistical',
                            'importance': 'high' if '%' in match.group() else 'medium',
                            'verifiable': True
                        })
        
        return claims
    
    def _extract_causal_claims(self, text):
        """Extract causal relationship claims"""
        claims = []
        sentences = self._split_into_sentences(text)
        
        for sentence in sentences:
            for pattern in self.causal_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    claim_text = self._clean_claim_text(sentence)
                    
                    if len(claim_text) > 30:  # Ensure meaningful claim
                        claims.append({
                            'text': claim_text,
                            'type': 'causal',
                            'importance': 'high',
                            'verifiable': True
                        })
                    break  # One causal claim per sentence
        
        return claims
    
    def _extract_comparison_claims(self, text):
        """Extract comparison claims"""
        claims = []
        sentences = self._split_into_sentences(text)
        
        for sentence in sentences:
            for pattern in self.comparison_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    claim_text = self._clean_claim_text(sentence)
                    
                    if len(claim_text) > 25:
                        claims.append({
                            'text': claim_text,
                            'type': 'comparison',
                            'importance': 'medium',
                            'verifiable': True
                        })
                    break
        
        return claims
    
    def _extract_temporal_claims(self, text):
        """Extract temporal/predictive claims"""
        claims = []
        sentences = self._split_into_sentences(text)
        
        for sentence in sentences:
            # Check for future predictions
            if re.search(r'\b(will|would|could|may|might)\s+\w+', sentence):
                # Also check for time reference
                if re.search(r'(by\s+\d{4}|next\s+\w+|future|soon)', sentence, re.IGNORECASE):
                    claim_text = self._clean_claim_text(sentence)
                    
                    if len(claim_text) > 30:
                        claims.append({
                            'text': claim_text,
                            'type': 'predictive',
                            'importance': 'medium',
                            'verifiable': False  # Future claims not immediately verifiable
                        })
        
        return claims
    
    def _split_into_sentences(self, text):
        """Split text into sentences"""
        # Simple sentence splitter
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 20]
        return sentences
    
    def _clean_claim_text(self, text):
        """Clean and format claim text"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove quotes if they wrap the entire claim
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        
        # Ensure proper capitalization
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        
        # Add period if missing
        if text and text[-1] not in '.!?':
            text += '.'
        
        return text
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        info = super().get_service_info()
        info.update({
            'capabilities': [
                'Statistical claim extraction',
                'Causal relationship detection',
                'Comparison claim identification',
                'Temporal/predictive claim extraction',
                'AI-ENHANCED claim discovery',
                'AI-powered claim prioritization'
            ],
            'claim_types': ['statistical', 'causal', 'comparison', 'predictive', 'ai_extracted'],
            'max_claims': 20,
            'ai_enhanced': self._ai_available
        })
        return info
