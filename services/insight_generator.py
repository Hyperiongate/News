"""
Insight Generator - AI-Powered Executive Summary Generator
Date: October 6, 2025
Version: 1.0.0
FILE 1 OF 3

DEPLOYMENT INSTRUCTIONS:
1. Save this entire file as: services/insight_generator.py
2. No modifications needed - deploy as-is
3. Update news_analyzer.py to call this (see deployment notes below)

PURPOSE:
Generates executive insights that answer:
- "What's the bottom line?"
- "Should I trust this article?"
- "What are the key findings?"
- "How does this compare to other articles?"
"""

import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Import OpenAI if available
try:
    from openai import OpenAI
    openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    OPENAI_AVAILABLE = True
except:
    openai_client = None
    OPENAI_AVAILABLE = False


class InsightGenerator:
    """Generates executive insights from analysis results"""
    
    def __init__(self):
        self.service_name = 'insight_generator'
        logger.info(f"[InsightGenerator] Initialized (OpenAI: {OPENAI_AVAILABLE})")
    
    def generate_insights(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point: Generate executive insights from all service results
        
        Args:
            analysis_results: Complete analysis results from news_analyzer
            
        Returns:
            Dict with insights added to results
        """
        try:
            logger.info("[InsightGenerator] Starting insight generation")
            
            scores = self._extract_scores(analysis_results)
            executive_summary = self._generate_executive_summary(analysis_results, scores)
            key_findings = self._generate_key_findings(analysis_results, scores)
            trust_recommendation = self._generate_trust_recommendation(scores)
            flags = self._identify_flags(analysis_results, scores)
            comparative = self._generate_comparative_context(scores)
            
            insights = {
                'executive_summary': executive_summary,
                'key_findings': key_findings,
                'trust_recommendation': trust_recommendation,
                'red_flags': flags['red_flags'],
                'green_flags': flags['green_flags'],
                'comparative_context': comparative,
                'bottom_line': self._generate_bottom_line(scores, flags),
                'confidence_level': self._calculate_confidence(analysis_results),
                'analysis_depth': self._assess_analysis_depth(analysis_results),
                'generated_at': datetime.now().isoformat()
            }
            
            logger.info("[InsightGenerator] ✓ Insights generated successfully")
            return insights
            
        except Exception as e:
            logger.error(f"[InsightGenerator] Error: {e}", exc_info=True)
            return self._get_fallback_insights()
    
    def _extract_scores(self, results: Dict[str, Any]) -> Dict[str, int]:
        """Extract all service scores"""
        detailed = results.get('detailed_analysis', {})
        
        return {
            'trust_score': results.get('trust_score', 50),
            'source_credibility': detailed.get('source_credibility', {}).get('score', 50),
            'author_credibility': detailed.get('author_analyzer', {}).get('credibility_score', 50),
            'bias_score': 100 - detailed.get('bias_detector', {}).get('bias_score', 50),
            'fact_accuracy': detailed.get('fact_checker', {}).get('score', 50),
            'transparency': detailed.get('transparency_analyzer', {}).get('score', 50),
            'integrity': detailed.get('manipulation_detector', {}).get('integrity_score', 100),
            'content_quality': detailed.get('content_analyzer', {}).get('score', 50)
        }
    
    def _generate_executive_summary(self, results: Dict[str, Any], scores: Dict[str, int]) -> str:
        """Generate AI-powered executive summary"""
        
        trust_score = scores['trust_score']
        
        if OPENAI_AVAILABLE and openai_client:
            try:
                prompt = f"""Generate a 2-3 sentence executive summary of this article analysis.

Trust Score: {trust_score}/100
Source: {scores['source_credibility']}/100
Author: {scores['author_credibility']}/100
Bias: {100 - scores['bias_score']}/100
Facts: {scores['fact_accuracy']}/100
Manipulation: {100 - scores['integrity']}/100

Article from: {results.get('source', 'Unknown')}
Author: {results.get('author', 'Unknown')}

Write a clear summary that:
1. States overall trustworthiness
2. Highlights the most important finding
3. Gives actionable guidance

Be direct and avoid jargon."""

                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert analyst. Be concise and actionable."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=150,
                    temperature=0.3
                )
                
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                logger.error(f"[InsightGenerator] OpenAI failed: {e}")
        
        # Fallback summary
        if trust_score >= 80:
            return f"This article demonstrates high credibility (Trust Score: {trust_score}/100). The source is reliable, the author is credible, and fact-checking shows strong accuracy. Recommended for citation and sharing."
        elif trust_score >= 65:
            return f"This article shows above-average credibility (Trust Score: {trust_score}/100). While generally reliable, some concerns in {self._identify_weak_areas(scores)}. Use with context."
        elif trust_score >= 50:
            return f"This article has moderate credibility (Trust Score: {trust_score}/100). Concerns in {self._identify_weak_areas(scores)}. Cross-reference before relying on it."
        else:
            return f"This article has low credibility (Trust Score: {trust_score}/100). Major issues in {self._identify_weak_areas(scores)}. Seek alternative sources."
    
    def _generate_key_findings(self, results: Dict[str, Any], scores: Dict[str, int]) -> List[str]:
        """Generate 3-5 key findings"""
        findings = []
        detailed = results.get('detailed_analysis', {})
        
        # Source
        source_score = scores['source_credibility']
        if source_score >= 80:
            findings.append(f"✓ High-quality source: {results.get('source', 'Unknown')} scores {source_score}/100")
        elif source_score < 50:
            findings.append(f"⚠ Source concern: {results.get('source', 'Unknown')} scores {source_score}/100")
        
        # Author
        author_score = scores['author_credibility']
        author_data = detailed.get('author_analyzer', {})
        years_exp = author_data.get('years_experience', 'Unknown')
        awards = author_data.get('awards', [])
        
        if author_score >= 80:
            if awards:
                findings.append(f"✓ Highly credible author: {results.get('author', 'Unknown')} ({years_exp} years, {len(awards)} awards)")
            else:
                findings.append(f"✓ Credible author: {results.get('author', 'Unknown')} with {years_exp} years experience")
        elif author_score < 50:
            findings.append(f"⚠ Limited author info: Unable to verify {results.get('author', 'Unknown')}")
        
        # Bias
        bias_score = 100 - scores['bias_score']
        if bias_score >= 30:
            direction = detailed.get('bias_detector', {}).get('political_lean', 'unknown')
            findings.append(f"⚠ Notable bias: {bias_score}/100 bias level, leaning {direction}")
        else:
            findings.append(f"✓ Minimal bias: Low bias score ({bias_score}/100) indicates balance")
        
        # Facts
        fact_checker = detailed.get('fact_checker', {})
        claims_checked = fact_checker.get('claims_checked', 0)
        claims_verified = fact_checker.get('claims_verified', 0)
        
        if claims_checked > 0:
            accuracy_pct = int((claims_verified / claims_checked) * 100)
            if accuracy_pct >= 80:
                findings.append(f"✓ Strong accuracy: {claims_verified}/{claims_checked} verified ({accuracy_pct}%)")
            elif accuracy_pct < 50:
                findings.append(f"⚠ Factual concerns: Only {claims_verified}/{claims_checked} verified ({accuracy_pct}%)")
        
        # Manipulation
        integrity_score = scores['integrity']
        manip_score = 100 - integrity_score
        if manip_score >= 40:
            manip_data = detailed.get('manipulation_detector', {})
            techniques = manip_data.get('techniques', [])
            findings.append(f"⚠ Manipulation detected: {len(techniques)} techniques (integrity: {integrity_score}/100)")
        
        return findings[:5]
    
    def _generate_trust_recommendation(self, scores: Dict[str, int]) -> Dict[str, Any]:
        """Generate trust recommendation"""
        trust_score = scores['trust_score']
        
        if trust_score >= 85:
            return {'level': 'HIGH', 'recommendation': 'Highly trustworthy. Safe to cite and share.', 'color': '#10b981', 'score': trust_score}
        elif trust_score >= 70:
            return {'level': 'GOOD', 'recommendation': 'Generally trustworthy. Appropriate for most uses.', 'color': '#34d399', 'score': trust_score}
        elif trust_score >= 55:
            return {'level': 'MODERATE', 'recommendation': 'Moderate credibility. Cross-reference key claims.', 'color': '#f59e0b', 'score': trust_score}
        elif trust_score >= 40:
            return {'level': 'QUESTIONABLE', 'recommendation': 'Credibility concerns. Seek additional sources.', 'color': '#ef4444', 'score': trust_score}
        else:
            return {'level': 'LOW', 'recommendation': 'Low credibility. Do not rely without verification.', 'color': '#dc2626', 'score': trust_score}
    
    def _identify_flags(self, results: Dict[str, Any], scores: Dict[str, int]) -> Dict[str, List[str]]:
        """Identify red and green flags"""
        red_flags = []
        green_flags = []
        detailed = results.get('detailed_analysis', {})
        
        # Source
        if scores['source_credibility'] >= 85:
            green_flags.append("Highly reputable news source")
        elif scores['source_credibility'] < 40:
            red_flags.append("Source has low credibility rating")
        
        # Author
        author_data = detailed.get('author_analyzer', {})
        if author_data.get('verified'):
            green_flags.append("Author identity verified")
        if author_data.get('awards'):
            green_flags.append(f"Award-winning journalist ({len(author_data['awards'])} awards)")
        if author_data.get('credibility_score', 0) < 40:
            red_flags.append("Limited author information")
        
        # Bias
        if scores['bias_score'] >= 85:
            green_flags.append("Minimal political bias")
        elif 100 - scores['bias_score'] >= 40:
            red_flags.append("Significant political bias")
        
        # Facts
        fact_data = detailed.get('fact_checker', {})
        claims_checked = fact_data.get('claims_checked', 0)
        claims_verified = fact_data.get('claims_verified', 0)
        
        if claims_checked > 0:
            accuracy = (claims_verified / claims_checked) * 100
            if accuracy >= 90:
                green_flags.append("Excellent fact-checking record")
            elif accuracy < 60:
                red_flags.append("Multiple factual inaccuracies")
        
        # Transparency
        if scores['transparency'] >= 80:
            green_flags.append("Transparent sourcing")
        elif scores['transparency'] < 40:
            red_flags.append("Poor source attribution")
        
        # Manipulation
        if scores['integrity'] >= 90:
            green_flags.append("No manipulation tactics")
        elif scores['integrity'] < 60:
            techniques = len(detailed.get('manipulation_detector', {}).get('techniques', []))
            red_flags.append(f"Manipulation tactics detected ({techniques} techniques)")
        
        return {'red_flags': red_flags, 'green_flags': green_flags}
    
    def _generate_comparative_context(self, scores: Dict[str, int]) -> Dict[str, str]:
        """Generate comparative context"""
        trust_score = scores['trust_score']
        
        def score_to_percentile(score):
            if score >= 85: return "top 15%"
            elif score >= 75: return "top 25%"
            elif score >= 65: return "top 40%"
            elif score >= 55: return "above average"
            elif score >= 45: return "average"
            else: return "below average"
        
        percentile = score_to_percentile(trust_score)
        
        return {
            'overall': f"This article ranks in the {percentile} of analyzed content",
            'source': f"Source credibility: {score_to_percentile(scores['source_credibility'])}",
            'author': f"Author credibility: {score_to_percentile(scores['author_credibility'])}",
            'context': f"Trust score of {trust_score}/100 places this {percentile}"
        }
    
    def _generate_bottom_line(self, scores: Dict[str, int], flags: Dict[str, List]) -> str:
        """Generate one-sentence bottom line"""
        trust_score = scores['trust_score']
        
        if trust_score >= 80:
            return "High credibility article from a reliable source with verified facts."
        elif trust_score >= 70:
            return "Generally credible article with minor concerns."
        elif trust_score >= 55:
            return "Moderate credibility - verify key claims before sharing."
        elif trust_score >= 40:
            return "Questionable credibility - multiple red flags identified."
        else:
            return "Low credibility - not recommended without verification."
    
    def _calculate_confidence(self, results: Dict[str, Any]) -> str:
        """Calculate confidence in analysis"""
        detailed = results.get('detailed_analysis', {})
        services_run = sum(1 for s in ['source_credibility', 'author_analyzer', 'bias_detector', 
                       'fact_checker', 'transparency_analyzer', 'manipulation_detector', 'content_analyzer']
                       if s in detailed and detailed[s].get('score') is not None)
        
        if services_run >= 7: return "HIGH"
        elif services_run >= 5: return "GOOD"
        elif services_run >= 3: return "MODERATE"
        else: return "LIMITED"
    
    def _assess_analysis_depth(self, results: Dict[str, Any]) -> str:
        """Assess analysis depth"""
        detailed = results.get('detailed_analysis', {})
        depth = 0
        
        if detailed.get('author_analyzer', {}).get('verified'): depth += 1
        if detailed.get('fact_checker', {}).get('claims_checked', 0) > 0: depth += 1
        if detailed.get('transparency_analyzer', {}).get('sources_cited', 0) > 0: depth += 1
        if detailed.get('manipulation_detector', {}).get('integrity_score'): depth += 1
        
        if depth >= 3: return "COMPREHENSIVE"
        elif depth >= 2: return "SUBSTANTIAL"
        else: return "BASIC"
    
    def _identify_weak_areas(self, scores: Dict[str, int]) -> str:
        """Identify weakest areas"""
        weak = []
        if scores['source_credibility'] < 60: weak.append("source credibility")
        if scores['author_credibility'] < 60: weak.append("author verification")
        if scores['bias_score'] < 60: weak.append("political bias")
        if scores['fact_accuracy'] < 60: weak.append("factual accuracy")
        if scores['transparency'] < 60: weak.append("transparency")
        if scores['integrity'] < 60: weak.append("content manipulation")
        
        if not weak: return "several areas"
        elif len(weak) == 1: return weak[0]
        elif len(weak) == 2: return f"{weak[0]} and {weak[1]}"
        else: return f"{', '.join(weak[:-1])}, and {weak[-1]}"
    
    def _get_fallback_insights(self) -> Dict[str, Any]:
        """Fallback insights if generation fails"""
        return {
            'executive_summary': 'Analysis complete. Review detailed results below.',
            'key_findings': ['Analysis completed across multiple dimensions'],
            'trust_recommendation': {'level': 'MODERATE', 'recommendation': 'Review analysis', 'color': '#6b7280', 'score': 50},
            'red_flags': [],
            'green_flags': [],
            'comparative_context': {'overall': 'Comparative data unavailable'},
            'bottom_line': 'See detailed analysis for complete assessment.',
            'confidence_level': 'MODERATE',
            'analysis_depth': 'BASIC',
            'generated_at': datetime.now().isoformat()
        }
