"""
services/connection_analyzer.py - Connection and relationship analysis
"""

import re
from typing import Dict, Any, List

class ConnectionAnalyzer:
    """Analyze connections and relationships in articles"""
    
    def analyze_connections(self, text: str, title: str, claims: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze logical connections and relationships in text"""
        
        # Connection words and phrases
        causal_connectors = [
            'therefore', 'thus', 'hence', 'consequently', 'as a result',
            'because', 'since', 'due to', 'owing to', 'thanks to',
            'leads to', 'causes', 'results in', 'brings about'
        ]
        
        contrast_connectors = [
            'however', 'but', 'yet', 'although', 'though', 'whereas',
            'on the other hand', 'in contrast', 'nevertheless', 'nonetheless'
        ]
        
        sequence_connectors = [
            'first', 'second', 'then', 'next', 'finally', 'subsequently',
            'meanwhile', 'afterward', 'before', 'after'
        ]
        
        # Count connections
        causal_count = sum(1 for conn in causal_connectors if conn in text.lower())
        contrast_count = sum(1 for conn in contrast_connectors if conn in text.lower())
        sequence_count = sum(1 for conn in sequence_connectors if conn in text.lower())
        
        total_connections = causal_count + contrast_count + sequence_count
        
        # Analyze claim relationships
        claim_connections = self._analyze_claim_connections(claims, text)
        
        # Determine connection strength
        if total_connections > 10:
            connection_strength = 'Strong'
        elif total_connections > 5:
            connection_strength = 'Moderate'
        elif total_connections > 2:
            connection_strength = 'Weak'
        else:
            connection_strength = 'Minimal'
        
        # Analyze logical flow
        logical_flow = self._analyze_logical_flow(text)
        
        return {
            'total_claims': len(claims),
            'connections_found': total_connections,
            'connection_strength': connection_strength,
            'connection_types': {
                'causal': causal_count,
                'contrast': contrast_count,
                'sequence': sequence_count
            },
            'claim_relationships': claim_connections,
            'logical_flow': logical_flow,
            'coherence_score': self._calculate_coherence_score(
                total_connections, len(claims), logical_flow
            )
        }
    
    def _analyze_claim_connections(self, claims: List[Dict[str, Any]], text: str) -> Dict[str, Any]:
        """Analyze how claims are connected"""
        if not claims:
            return {
                'supported_claims': 0,
                'unsupported_claims': 0,
                'interconnected_claims': 0
            }
        
        supported = 0
        unsupported = 0
        
        # Simple heuristic: check if claims are followed by supporting language
        for claim in claims:
            claim_text = claim.get('text', '')
            if claim_text in text:
                # Look for supporting language after the claim
                claim_pos = text.find(claim_text)
                if claim_pos != -1:
                    following_text = text[claim_pos:claim_pos + 200].lower()
                    if any(word in following_text for word in 
                          ['because', 'evidence', 'study', 'research', 'data']):
                        supported += 1
                    else:
                        unsupported += 1
        
        return {
            'supported_claims': supported,
            'unsupported_claims': unsupported,
            'interconnected_claims': min(supported, len(claims) // 2)
        }
    
    def _analyze_logical_flow(self, text: str) -> str:
        """Analyze the logical flow of the article"""
        sentences = re.split(r'[.!?]+', text)
        
        # Check for logical progression
        has_introduction = any(word in sentences[0].lower() if sentences else '' 
                             for word in ['report', 'study', 'research', 'today', 'new'])
        
        has_conclusion = False
        if len(sentences) > 3:
            last_sentences = ' '.join(sentences[-3:]).lower()
            has_conclusion = any(word in last_sentences 
                               for word in ['conclude', 'summary', 'overall', 'finally'])
        
        if has_introduction and has_conclusion:
            return 'Well-structured'
        elif has_introduction or has_conclusion:
            return 'Partially structured'
        else:
            return 'Loosely structured'
    
    def _calculate_coherence_score(self, connections: int, claims: int, 
                                 logical_flow: str) -> int:
        """Calculate overall coherence score"""
        base_score = 50
        
        # Add points for connections relative to claims
        if claims > 0:
            connection_ratio = connections / claims
            base_score += min(25, int(connection_ratio * 25))
        
        # Add points for logical flow
        flow_scores = {
            'Well-structured': 25,
            'Partially structured': 15,
            'Loosely structured': 5
        }
        base_score += flow_scores.get(logical_flow, 0)
        
        return min(100, max(0, base_score))
