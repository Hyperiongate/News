"""
Data Enricher - Adds Comparative Context & Rankings
Date: October 6, 2025
Version: 1.0.0
FILE 2 OF 3 - COMPLETE VERSION

DEPLOYMENT:
Save as: services/data_enricher.py

PURPOSE:
Enriches existing service data with comparative context, percentile rankings,
visual indicators, and performance badges WITHOUT changing data structure.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class DataEnricher:
    """Adds comparative context and rankings to analysis results"""
    
    def __init__(self):
        self.service_name = 'data_enricher'
        
        # Benchmark thresholds
        self.benchmarks = {
            'trust_score': {'excellent': 85, 'good': 70, 'average': 55, 'poor': 40},
            'source_credibility': {'excellent': 85, 'good': 70, 'average': 55, 'poor': 40},
            'author_credibility': {'excellent': 80, 'good': 65, 'average': 50, 'poor': 35},
            'bias_objectivity': {'excellent': 85, 'good': 70, 'average': 55, 'poor': 40},
            'fact_accuracy': {'excellent': 90, 'good': 75, 'average': 60, 'poor': 45},
            'transparency': {'excellent': 80, 'good': 65, 'average': 50, 'poor': 35},
            'integrity': {'excellent': 90, 'good': 75, 'average': 60, 'poor': 45},
            'content_quality': {'excellent': 85, 'good': 70, 'average': 55, 'poor': 40}
        }
        
        logger.info("[DataEnricher] Initialized")
    
    def enrich_data(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point: Enrich results with comparative context"""
        try:
            logger.info("[DataEnricher] Starting enrichment")
            
            enriched = analysis_results.copy()
            
            # Enrich trust score
            trust_score = enriched.get('trust_score', 50)
            enriched['trust_score_enrichment'] = self._enrich_score(
                trust_score, 'trust_score', 'Overall Trust'
            )
            
            # Enrich each service
            detailed = enriched.get('detailed_analysis', {})
            
            if 'source_credibility' in detailed:
                detailed['source_credibility']['enrichment'] = self._enrich_source(
                    detailed['source_credibility']
                )
            
            if 'author_analyzer' in detailed:
                detailed['author_analyzer']['enrichment'] = self._enrich_author(
                    detailed['author_analyzer']
                )
            
            if 'bias_detector' in detailed:
                detailed['bias_detector']['enrichment'] = self._enrich_bias(
                    detailed['bias_detector']
                )
            
            if 'fact_checker' in detailed:
                detailed['fact_checker']['enrichment'] = self._enrich_facts(
                    detailed['fact_checker']
                )
            
            if 'transparency_analyzer' in detailed:
                detailed['transparency_analyzer']['enrichment'] = self._enrich_transparency(
                    detailed['transparency_analyzer']
                )
            
            if 'manipulation_detector' in detailed:
                detailed['manipulation_detector']['enrichment'] = self._enrich_manipulation(
                    detailed['manipulation_detector']
                )
            
            if 'content_analyzer' in detailed:
                detailed['content_analyzer']['enrichment'] = self._enrich_content(
                    detailed['content_analyzer']
                )
            
            # Add comparative summary
            enriched['comparative_summary'] = self._generate_summary(enriched)
            
            logger.info("[DataEnricher] Enrichment complete")
            return enriched
            
        except Exception as e:
            logger.error(f"[DataEnricher] Error: {e}", exc_info=True)
            return analysis_results  # Return original on error
    
    def _enrich_score(self, score: int, category: str, label: str) -> Dict[str, Any]:
        """Generic score enrichment with percentile ranking"""
        benchmarks = self.benchmarks.get(category, self.benchmarks['trust_score'])
        
        if score >= benchmarks['excellent']:
            level = 'excellent'
            badge = '⭐⭐⭐⭐⭐'
            percentile = self._score_to_percentile(score)
            comparison = f"Top {100 - percentile}% performance"
        elif score >= benchmarks['good']:
            level = 'good'
            badge = '⭐⭐⭐⭐'
            percentile = self._score_to_percentile(score)
            comparison = f"Above average (top {100 - percentile}%)"
        elif score >= benchmarks['average']:
            level = 'average'
            badge = '⭐⭐⭐'
            comparison = "Average performance"
        elif score >= benchmarks['poor']:
            level = 'below_average'
            badge = '⭐⭐'
            comparison = "Below average"
        else:
            level = 'poor'
            badge = '⭐'
            comparison = "Significantly below average"
        
        return {
            'level': level,
            'badge': badge,
            'comparison': comparison,
            'percentile': self._score_to_percentile(score),
            'label': label,
            'visual_indicator': self._get_visual(level)
        }
    
    def _enrich_source(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich source credibility data"""
        score = data.get('score', 50)
        enrichment = self._enrich_score(score, 'source_credibility', 'Source Credibility')
        
        if score >= 85:
            enrichment['context'] = "Highly reputable news source with strong track record"
            enrichment['trust_indicator'] = "🟢 Verified Reliable Source"
        elif score >= 70:
            enrichment['context'] = "Generally credible source with good standards"
            enrichment['trust_indicator'] = "🟢 Credible Source"
        elif score >= 55:
            enrichment['context'] = "Moderate credibility - verify important claims"
            enrichment['trust_indicator'] = "🟡 Verify Key Claims"
        else:
            enrichment['context'] = "Limited credibility - seek additional sources"
            enrichment['trust_indicator'] = "🔴 Verification Recommended"
        
        return enrichment
    
    def _enrich_author(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich author analysis data"""
        score = data.get('credibility_score', 50)
        enrichment = self._enrich_score(score, 'author_credibility', 'Author Credibility')
        
        years_exp = data.get('years_experience', 0)
        awards = data.get('awards', [])
        verified = data.get('verified', False)
        
        # Build credibility indicators
        indicators = []
        if verified:
            indicators.append("✓ Identity Verified")
        if isinstance(years_exp, int) and years_exp >= 10:
            indicators.append(f"✓ {years_exp}+ Years Experience")
        elif isinstance(years_exp, int) and years_exp >= 5:
            indicators.append(f"✓ {years_exp} Years Experience")
        if awards and len(awards) > 0:
            indicators.append(f"✓ {len(awards)} Award(s)")
        
        enrichment['credibility_indicators'] = indicators
        
        # Author ranking
        if score >= 85 and len(awards) > 0:
            enrichment['author_rank'] = "Top-Tier Journalist"
            enrichment['rank_badge'] = "🏆 ELITE"
        elif score >= 75:
            enrichment['author_rank'] = "Highly Credible"
            enrichment['rank_badge'] = "⭐ VERIFIED"
        elif score >= 60:
            enrichment['author_rank'] = "Established Professional"
            enrichment['rank_badge'] = "✓ CREDIBLE"
        else:
            enrichment['author_rank'] = "Limited Information"
            enrichment['rank_badge'] = "? UNVERIFIED"
        
        return enrichment
    
    def _enrich_bias(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich bias analysis data"""
        bias_score = data.get('bias_score', 50)
        objectivity_score = 100 - bias_score
        enrichment = self._enrich_score(objectivity_score, 'bias_objectivity', 'Objectivity')
        
        direction = data.get('political_lean', 'center').lower()
        
        if bias_score <= 15:
            enrichment['bias_level'] = "Minimal Bias"
            enrichment['bias_indicator'] = "🟢 Highly Objective"
            enrichment['context'] = "Exceptional objectivity - balanced reporting"
        elif bias_score <= 30:
            enrichment['bias_level'] = "Slight Bias"
            enrichment['bias_indicator'] = "🟢 Generally Objective"
            enrichment['context'] = f"Minor {direction} lean but largely balanced"
        elif bias_score <= 50:
            enrichment['bias_level'] = "Moderate Bias"
            enrichment['bias_indicator'] = "🟡 Noticeable Bias"
            enrichment['context'] = f"Clear {direction} perspective present"
        else:
            enrichment['bias_level'] = "Strong Bias"
            enrichment['bias_indicator'] = "🔴 Heavily Biased"
            enrichment['context'] = f"Strong {direction} bias - seek balanced sources"
        
        enrichment['spectrum_position'] = self._get_bias_position(bias_score, direction)
        return enrichment
    
    def _enrich_facts(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich fact-checking data"""
        score = data.get('score', 50)
        enrichment = self._enrich_score(score, 'fact_accuracy', 'Factual Accuracy')
        
        claims_checked = data.get('claims_checked', 0)
        claims_verified = data.get('claims_verified', 0)
        
        if claims_checked > 0:
            accuracy_pct = int((claims_verified / claims_checked) * 100)
            enrichment['accuracy_rate'] = f"{accuracy_pct}%"
            enrichment['claims_summary'] = f"{claims_verified}/{claims_checked} verified"
            
            if accuracy_pct >= 90:
                enrichment['accuracy_badge'] = "🟢 HIGHLY ACCURATE"
                enrichment['context'] = "Exceptional fact-checking record"
            elif accuracy_pct >= 75:
                enrichment['accuracy_badge'] = "🟢 ACCURATE"
                enrichment['context'] = "Strong factual accuracy"
            elif accuracy_pct >= 60:
                enrichment['accuracy_badge'] = "🟡 MOSTLY ACCURATE"
                enrichment['context'] = "Some factual concerns"
            else:
                enrichment['accuracy_badge'] = "🔴 ACCURACY CONCERNS"
                enrichment['context'] = "Multiple factual issues detected"
        else:
            enrichment['accuracy_rate'] = "N/A"
            enrichment['claims_summary'] = "No claims checked"
            enrichment['accuracy_badge'] = "⚪ NO DATA"
            enrichment['context'] = "Fact-checking not performed"
        
        return enrichment
    
    def _enrich_transparency(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich transparency data"""
        score = data.get('score', 50)
        enrichment = self._enrich_score(score, 'transparency', 'Transparency')
        
        sources_cited = data.get('sources_cited', 0)
        quotes_used = data.get('quotes_used', 0)
        
        if score >= 80:
            enrichment['transparency_level'] = "Highly Transparent"
            enrichment['indicator'] = "🟢 EXCELLENT"
            enrichment['context'] = f"Strong sourcing ({sources_cited} sources, {quotes_used} quotes)"
        elif score >= 65:
            enrichment['transparency_level'] = "Good Transparency"
            enrichment['indicator'] = "🟢 GOOD"
            enrichment['context'] = f"Adequate sourcing ({sources_cited} sources, {quotes_used} quotes)"
        elif score >= 50:
            enrichment['transparency_level'] = "Moderate Transparency"
            enrichment['indicator'] = "🟡 FAIR"
            enrichment['context'] = f"Limited sourcing ({sources_cited} sources, {quotes_used} quotes)"
        else:
            enrichment['transparency_level'] = "Poor Transparency"
            enrichment['indicator'] = "🔴 POOR"
            enrichment['context'] = "Insufficient source attribution"
        
        return enrichment
    
    def _enrich_manipulation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich manipulation detection data"""
        integrity_score = data.get('integrity_score', 100)
        manipulation_score = 100 - integrity_score
        enrichment = self._enrich_score(integrity_score, 'integrity', 'Content Integrity')
        
        techniques = data.get('techniques', [])
        technique_count = len(techniques)
        
        if manipulation_score <= 10:
            enrichment['manipulation_level'] = "No Manipulation"
            enrichment['indicator'] = "🟢 CLEAN"
            enrichment['context'] = "No manipulation tactics detected"
        elif manipulation_score <= 25:
            enrichment['manipulation_level'] = "Minimal Manipulation"
            enrichment['indicator'] = "🟢 ACCEPTABLE"
            enrichment['context'] = f"Minor rhetoric ({technique_count} technique(s))"
        elif manipulation_score <= 40:
            enrichment['manipulation_level'] = "Moderate Manipulation"
            enrichment['indicator'] = "🟡 CAUTION"
            enrichment['context'] = f"Notable tactics ({technique_count} technique(s))"
        else:
            enrichment['manipulation_level'] = "Heavy Manipulation"
            enrichment['indicator'] = "🔴 WARNING"
            enrichment['context'] = f"Extensive manipulation ({technique_count} technique(s))"
        
        return enrichment
    
    def _enrich_content(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich content quality data"""
        score = data.get('score', 50)
        enrichment = self._enrich_score(score, 'content_quality', 'Content Quality')
        
        if score >= 85:
            enrichment['quality_level'] = "Excellent Quality"
            enrichment['indicator'] = "🟢 PROFESSIONAL"
        elif score >= 70:
            enrichment['quality_level'] = "High Quality"
            enrichment['indicator'] = "🟢 WELL-WRITTEN"
        elif score >= 55:
            enrichment['quality_level'] = "Good Quality"
            enrichment['indicator'] = "🟡 ACCEPTABLE"
        else:
            enrichment['quality_level'] = "Poor Quality"
            enrichment['indicator'] = "🔴 SUBSTANDARD"
        
        return enrichment
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall comparative summary"""
        trust_score = results.get('trust_score', 50)
        detailed = results.get('detailed_analysis', {})
        
        services_above_average = 0
        services_below_average = 0
        total_services = 0
        
        service_scores = {
            'source_credibility': detailed.get('source_credibility', {}).get('score', 50),
            'author_credibility': detailed.get('author_analyzer', {}).get('credibility_score', 50),
            'objectivity': 100 - detailed.get('bias_detector', {}).get('bias_score', 50),
            'fact_accuracy': detailed.get('fact_checker', {}).get('score', 50),
            'transparency': detailed.get('transparency_analyzer', {}).get('score', 50),
            'integrity': detailed.get('manipulation_detector', {}).get('integrity_score', 100),
            'content_quality': detailed.get('content_analyzer', {}).get('score', 50)
        }
        
        for score in service_scores.values():
            total_services += 1
            if score >= 65:
                services_above_average += 1
            elif score < 55:
                services_below_average += 1
        
        return {
            'overall_percentile': self._score_to_percentile(trust_score),
            'services_above_average': services_above_average,
            'services_below_average': services_below_average,
            'total_services_analyzed': total_services,
            'performance_summary': self._get_performance_summary(
                services_above_average, services_below_average, total_services
            )
        }
    
    def _score_to_percentile(self, score: int) -> int:
        """Convert score to percentile (simplified estimation)"""
        if score >= 90: return 90
        elif score >= 85: return 85
        elif score >= 80: return 75
        elif score >= 75: return 65
        elif score >= 70: return 55
        elif score >= 65: return 45
        elif score >= 60: return 35
        elif score >= 55: return 25
        else: return 15
    
    def _get_visual(self, level: str) -> str:
        """Get visual indicator emoji"""
        indicators = {
            'excellent': '🟢',
            'good': '🟢',
            'average': '🟡',
            'below_average': '🟠',
            'poor': '🔴'
        }
        return indicators.get(level, '⚪')
    
    def _get_bias_position(self, bias_score: int, direction: str) -> str:
        """Get position on political bias spectrum"""
        if bias_score <= 15:
            return "CENTER"
        elif direction.lower() == 'left':
            if bias_score <= 30: return "CENTER-LEFT"
            elif bias_score <= 50: return "LEFT"
            else: return "FAR-LEFT"
        elif direction.lower() == 'right':
            if bias_score <= 30: return "CENTER-RIGHT"
            elif bias_score <= 50: return "RIGHT"
            else: return "FAR-RIGHT"
        else:
            return "CENTER"
    
    def _get_performance_summary(self, above: int, below: int, total: int) -> str:
        """Get performance summary text"""
        if above >= total * 0.7:
            return "Strong performance across most dimensions"
        elif above >= total * 0.5:
            return "Mixed performance with strengths and weaknesses"
        elif below >= total * 0.5:
            return "Multiple areas need improvement"
        else:
            return "Average performance overall"
