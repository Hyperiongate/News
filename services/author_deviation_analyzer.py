"""
Author Deviation Analyzer - NEW
Date: October 5, 2025 
Version: 1.0

PURPOSE:
Compare THIS article to author's normal patterns
Detect significant deviations from baseline behavior

FEATURES:
- Baseline metric calculation from history
- Deviation detection and scoring
- Alert generation for anomalies
- AI-powered insight generation

UNIQUE VALUE:
This is what users CAN'T get from Google - algorithmic comparison
of an article to the author's established patterns

Save as: backend/services/author_deviation_analyzer.py (NEW FILE)
"""

import logging
from typing import Dict, Any, List, Optional
import statistics

logger = logging.getLogger(__name__)

# Import OpenAI if available
try:
    from openai import OpenAI
    import os
    openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    OPENAI_AVAILABLE = True
except:
    openai_client = None
    OPENAI_AVAILABLE = False


class AuthorDeviationAnalyzer:
    """
    Detects when an article deviates from author's normal patterns
    """
    
    def __init__(self):
        self.deviation_threshold = 20  # Points difference to flag
        logger.info("[Deviation] Analyzer initialized")
    
    def calculate_baseline_metrics(
        self, 
        article_history: List[Dict[str, Any]],
        past_analyses: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Calculate baseline metrics from author's article history
        
        Args:
            article_history: List of past articles
            past_analyses: Optional list of past analysis results
            
        Returns:
            Baseline metrics dict
        """
        
        logger.info(f"[Deviation] Calculating baseline from {len(article_history)} articles")
        
        if not article_history:
            return {
                'available': False,
                'reason': 'No article history available'
            }
        
        # If we have past analyses, use those
        if past_analyses and len(past_analyses) >= 5:
            return self._calculate_from_analyses(past_analyses)
        
        # Otherwise, estimate from article metadata
        return self._estimate_baseline(article_history)
    
    def _calculate_from_analyses(
        self, 
        past_analyses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate baseline from past analysis results"""
        
        # Extract metrics
        bias_scores = []
        manipulation_scores = []
        source_counts = []
        
        for analysis in past_analyses:
            if 'bias_score' in analysis:
                bias_scores.append(analysis['bias_score'])
            if 'manipulation_score' in analysis:
                manipulation_scores.append(analysis['manipulation_score'])
            if 'sources_cited' in analysis:
                source_counts.append(analysis['sources_cited'])
        
        return {
            'available': True,
            'avg_bias_score': statistics.mean(bias_scores) if bias_scores else None,
            'avg_manipulation_score': statistics.mean(manipulation_scores) if manipulation_scores else None,
            'avg_source_count': statistics.mean(source_counts) if source_counts else None,
            'sample_size': len(past_analyses)
        }
    
    def _estimate_baseline(
        self, 
        article_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Estimate baseline from article metadata"""
        
        # Estimate word count patterns
        word_counts = []
        title_lengths = []
        
        for article in article_history:
            if 'word_count' in article:
                word_counts.append(article['word_count'])
            
            title = article.get('title', '')
            if title:
                title_lengths.append(len(title.split()))
        
        return {
            'available': True,
            'avg_word_count': statistics.mean(word_counts) if word_counts else None,
            'avg_title_length': statistics.mean(title_lengths) if title_lengths else None,
            'sample_size': len(article_history),
            'note': 'Estimated from metadata (limited)'
        }
    
    def compare_to_baseline(
        self,
        current_article: Dict[str, Any],
        baseline_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare current article to baseline
        
        Args:
            current_article: Current article analysis results
            baseline_metrics: Baseline from calculate_baseline_metrics()
            
        Returns:
            Deviation report with flags
        """
        
        logger.info("[Deviation] Comparing article to baseline")
        
        if not baseline_metrics.get('available'):
            return {
                'deviations_detected': False,
                'reason': 'No baseline available',
                'alerts': []
            }
        
        deviations = []
        severity_scores = []
        
        # Check bias deviation
        if baseline_metrics.get('avg_bias_score') is not None:
            current_bias = current_article.get('bias_score', 50)
            baseline_bias = baseline_metrics['avg_bias_score']
            diff = abs(current_bias - baseline_bias)
            
            if diff >= self.deviation_threshold:
                severity = 'HIGH' if diff >= 35 else 'MODERATE'
                deviations.append({
                    'metric': 'Bias Score',
                    'baseline': round(baseline_bias, 1),
                    'current': current_bias,
                    'difference': round(diff, 1),
                    'severity': severity,
                    'alert': f"⚠️ Bias score ({current_bias}) is {round(diff)}pts {'higher' if current_bias > baseline_bias else 'lower'} than author's typical {round(baseline_bias)}"
                })
                severity_scores.append(diff)
        
        # Check manipulation deviation
        if baseline_metrics.get('avg_manipulation_score') is not None:
            current_manip = current_article.get('manipulation_score', 80)
            baseline_manip = baseline_metrics['avg_manipulation_score']
            diff = abs(current_manip - baseline_manip)
            
            if diff >= self.deviation_threshold:
                severity = 'HIGH' if diff >= 35 else 'MODERATE'
                deviations.append({
                    'metric': 'Manipulation Score',
                    'baseline': round(baseline_manip, 1),
                    'current': current_manip,
                    'difference': round(diff, 1),
                    'severity': severity,
                    'alert': f"⚠️ Manipulation score ({current_manip}) differs by {round(diff)}pts from author's typical {round(baseline_manip)}"
                })
                severity_scores.append(diff)
        
        # Check source count deviation
        if baseline_metrics.get('avg_source_count') is not None:
            current_sources = current_article.get('sources_cited', 0)
            baseline_sources = baseline_metrics['avg_source_count']
            diff = abs(current_sources - baseline_sources)
            
            # For source count, deviation is relative (50% change is significant)
            if baseline_sources > 0:
                pct_change = (diff / baseline_sources) * 100
                if pct_change >= 50:
                    severity = 'HIGH' if pct_change >= 80 else 'MODERATE'
                    deviations.append({
                        'metric': 'Source Count',
                        'baseline': round(baseline_sources, 1),
                        'current': current_sources,
                        'difference': round(diff, 1),
                        'severity': severity,
                        'alert': f"⚠️ Source citations ({current_sources}) {'much lower' if current_sources < baseline_sources else 'much higher'} than author's typical {round(baseline_sources)}"
                    })
                    severity_scores.append(pct_change / 2)  # Scale to match other scores
        
        # Calculate overall deviation severity
        if severity_scores:
            avg_deviation = statistics.mean(severity_scores)
            if avg_deviation >= 35:
                overall_severity = 'HIGH'
            elif avg_deviation >= 20:
                overall_severity = 'MODERATE'
            else:
                overall_severity = 'LOW'
        else:
            overall_severity = 'NONE'
        
        return {
            'deviations_detected': len(deviations) > 0,
            'deviation_count': len(deviations),
            'overall_severity': overall_severity,
            'deviations': deviations,
            'alerts': [d['alert'] for d in deviations],
            'summary': self._build_deviation_summary(deviations, overall_severity)
        }
    
    def generate_deviation_insights(
        self,
        deviation_report: Dict[str, Any]
    ) -> str:
        """
        Generate human-readable insights about deviations
        
        Uses AI if available for contextual analysis
        """
        
        if not deviation_report.get('deviations_detected'):
            return "This article is consistent with the author's typical patterns. No unusual deviations detected."
        
        deviations = deviation_report.get('deviations', [])
        severity = deviation_report.get('overall_severity', 'NONE')
        
        # Use AI for enhanced insights if available
        if OPENAI_AVAILABLE and openai_client and deviations:
            try:
                # Build context
                context = "Author deviation analysis:\n"
                for dev in deviations:
                    context += f"- {dev['metric']}: Current={dev['current']}, Typical={dev['baseline']}, Difference={dev['difference']}\n"
                
                prompt = f"""{context}

Generate a brief, insightful explanation (2-3 sentences) of what these deviations might mean. Focus on:
1. Why this article differs from the author's normal work
2. What readers should consider about these differences
3. Whether this raises credibility concerns

Be direct and analytical, not alarmist."""
                
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=150,
                    temperature=0.5
                )
                
                ai_insight = response.choices[0].message.content.strip()
                return ai_insight
                
            except Exception as e:
                logger.error(f"[Deviation] AI insight generation failed: {e}")
        
        # Fallback: Template-based insights
        if severity == 'HIGH':
            return f"SIGNIFICANT DEVIATION: This article shows {len(deviations)} major differences from the author's typical work. {deviations[0]['alert']}. This unusual pattern warrants extra scrutiny and fact-checking."
        elif severity == 'MODERATE':
            return f"Notable differences detected: This article deviates from the author's normal patterns in {len(deviations)} area(s). While not necessarily problematic, these changes are worth noting when evaluating the content."
        else:
            return f"Minor deviations detected in {len(deviations)} metric(s), but within normal variation for this author."
    
    def _build_deviation_summary(
        self,
        deviations: List[Dict[str, Any]],
        severity: str
    ) -> str:
        """Build summary text for deviation report"""
        
        if not deviations:
            return "No significant deviations from author's baseline detected."
        
        summary_parts = []
        
        for dev in deviations:
            metric = dev['metric']
            direction = 'higher' if dev['current'] > dev['baseline'] else 'lower'
            summary_parts.append(f"{metric} is {direction} than typical")
        
        summary = f"{severity} deviation detected: " + ", ".join(summary_parts)
        return summary
