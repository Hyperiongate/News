# services/report_generator.py
"""
Report Generation Service - v2.0
Creates various report formats from analysis results

CHANGE LOG:
- 2025-10-13: v2.0 - Enhanced "What We Found" summary generation
  * Added dynamic, conversational summaries (2-5 sentences)
  * Summaries now highlight specific findings from each service
  * Intelligently identifies concerns vs strengths
  * Added Pro version prompt at end
  * Summaries are informative and actionable, not generic

Previous versions:
- v1.0 - Initial report generation with basic summary
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generate various report formats from analysis results"""
    
    def generate(self, analysis_results, format='summary'):
        """
        Generate report in specified format
        
        Args:
            analysis_results: Dictionary containing analysis results
            format: Report format ('summary', 'detailed', 'json', 'markdown')
            
        Returns:
            Report in specified format
        """
        if format == 'summary':
            return self._generate_summary_report(analysis_results)
        elif format == 'detailed':
            return self._generate_detailed_report(analysis_results)
        elif format == 'json':
            return self._generate_json_report(analysis_results)
        elif format == 'markdown':
            return self._generate_markdown_report(analysis_results)
        else:
            logger.warning(f"Unknown report format: {format}")
            return self._generate_summary_report(analysis_results)
    
    def _generate_summary_report(self, data):
        """Generate summary report"""
        article = data.get('article', {})
        
        summary = {
            'report_type': 'summary',
            'generated_at': datetime.now().isoformat(),
            'article_info': {
                'title': article.get('title', 'Unknown'),
                'source': article.get('domain', 'Unknown'),
                'author': article.get('author', 'Unknown'),
                'url': article.get('url', '')
            },
            'key_metrics': {
                'trust_score': data.get('trust_score', 0),
                'bias_score': data.get('bias_score', 0),
                'clickbait_score': data.get('clickbait_analysis', {}).get('score', 0),
                'transparency_score': data.get('transparency_analysis', {}).get('score', 0)
            },
            'summary': self._create_enhanced_text_summary(data),
            'recommendations': self._get_key_recommendations(data)
        }
        
        return summary
    
    def _create_enhanced_text_summary(self, data):
        """
        Create enhanced, conversational text summary (2-5 sentences)
        Highlights specific findings from analysis services
        """
        trust_score = data.get('trust_score', 0)
        article_domain = data.get('article', {}).get('domain', 'this source')
        
        # Collect specific concerns and strengths from each service
        concerns = []
        strengths = []
        
        # Source Credibility Analysis (25% weight)
        source_data = data.get('source_credibility', {})
        if source_data:
            source_score = source_data.get('score', 0)
            source_max = source_data.get('max_score', 25)
            source_pct = (source_score / source_max * 100) if source_max > 0 else 0
            
            if source_pct < 60:
                concerns.append('weak source credibility')
            elif source_pct >= 80:
                strengths.append('strong source credibility')
        
        # Bias Detection (20% weight)
        bias_data = data.get('bias_analysis', {})
        if bias_data:
            bias_score = bias_data.get('score', 0)
            bias_max = bias_data.get('max_score', 20)
            bias_pct = (bias_score / bias_max * 100) if bias_max > 0 else 0
            political_lean = abs(bias_data.get('political_lean', 0))
            
            if bias_pct < 70 or political_lean > 0.5:
                if political_lean > 0.7:
                    concerns.append('significant political bias')
                else:
                    concerns.append('noticeable bias')
            elif bias_pct >= 90 and political_lean < 0.3:
                strengths.append('minimal bias')
        
        # Author Analysis (15% weight)
        author_data = data.get('author_info', {})
        if author_data:
            author_score = author_data.get('score', 0)
            author_max = author_data.get('max_score', 15)
            author_pct = (author_score / author_max * 100) if author_max > 0 else 0
            
            if author_pct < 60:
                concerns.append('limited author credibility')
            elif author_pct >= 85:
                strengths.append('credible author')
        
        # Fact Checking (15% weight)
        fact_data = data.get('fact_checking', {})
        if fact_data:
            fact_score = fact_data.get('score', 0)
            fact_max = fact_data.get('max_score', 15)
            fact_pct = (fact_score / fact_max * 100) if fact_max > 0 else 0
            
            if fact_pct >= 90:
                strengths.append('strong factual accuracy')
            elif fact_pct < 60:
                concerns.append('factual accuracy issues')
        
        # Transparency (10% weight)
        trans_data = data.get('transparency_analysis', {})
        if trans_data:
            trans_score = trans_data.get('score', 0)
            trans_max = trans_data.get('max_score', 10)
            trans_pct = (trans_score / trans_max * 100) if trans_max > 0 else 0
            
            if trans_pct < 50:
                concerns.append('poor transparency')
            elif trans_pct >= 85:
                strengths.append('good transparency')
        
        # Manipulation Detection (10% weight)
        manip_data = data.get('persuasion_analysis', {})
        if manip_data:
            manip_score = manip_data.get('score', 0)
            manip_max = manip_data.get('max_score', 10)
            manip_pct = (manip_score / manip_max * 100) if manip_max > 0 else 0
            manipulation_detected = manip_data.get('manipulation_detected', False)
            
            if manip_pct < 60 or manipulation_detected:
                concerns.append('manipulative techniques detected')
        
        # Content Quality (5% weight)
        quality_data = data.get('content_quality', {})
        if quality_data:
            quality_score = quality_data.get('score', 0)
            quality_max = quality_data.get('max_score', 5)
            quality_pct = (quality_score / quality_max * 100) if quality_max > 0 else 0
            
            if quality_pct < 50:
                concerns.append('low content quality')
        
        # Build conversational summary (2-5 sentences)
        summary_parts = []
        
        # Sentence 1: Overall assessment
        if trust_score >= 70:
            summary_parts.append(
                f"This article from {article_domain} shows moderate to high credibility "
                f"with a trust score of {trust_score}/100."
            )
        elif trust_score >= 40:
            summary_parts.append(
                f"This article from {article_domain} shows mixed credibility "
                f"with a trust score of {trust_score}/100."
            )
        else:
            summary_parts.append(
                f"This article from {article_domain} shows low credibility "
                f"with a trust score of {trust_score}/100."
            )
        
        # Sentence 2-3: Specific findings
        if concerns:
            # Format concerns naturally
            if len(concerns) == 1:
                summary_parts.append(f"Our analysis identified {concerns[0]}.")
            elif len(concerns) == 2:
                summary_parts.append(f"Our analysis identified {concerns[0]} and {concerns[1]}.")
            else:
                # Multiple concerns: list them naturally
                last_concern = concerns[-1]
                other_concerns = ', '.join(concerns[:-1])
                summary_parts.append(
                    f"Our analysis identified {other_concerns}, and {last_concern}."
                )
        elif strengths:
            # If no concerns, highlight strengths
            if len(strengths) == 1:
                summary_parts.append(f"The article demonstrates {strengths[0]}.")
            else:
                summary_parts.append(f"The article demonstrates {' and '.join(strengths)}.")
        
        # Sentence 4: Recommendation (if needed)
        if trust_score < 60:
            summary_parts.append("We recommend verifying claims through additional sources.")
        
        # Sentence 5: Pro version prompt (always included)
        summary_parts.append("Upgrade to Pro for detailed breakdowns and source comparisons.")
        
        return ' '.join(summary_parts)
    
    def _generate_detailed_report(self, data):
        """Generate detailed report"""
        report = {
            'report_type': 'detailed',
            'generated_at': datetime.now().isoformat(),
            'article_info': data.get('article', {}),
            'analysis_results': {
                'trust_analysis': {
                    'score': data.get('trust_score', 0),
                    'level': data.get('trust_level', 'Unknown'),
                    'breakdown': data.get('trust_score_breakdown', {})
                },
                'bias_analysis': data.get('bias_analysis', {}),
                'source_credibility': data.get('source_credibility', {}),
                'author_credibility': data.get('author_info', {}),
                'transparency': data.get('transparency_analysis', {}),
                'manipulation_detection': data.get('persuasion_analysis', {}),
                'fact_checking': {
                    'claims_checked': len(data.get('fact_checks', [])),
                    'results': data.get('fact_checks', [])
                }
            },
            'sections': self._create_detailed_sections(data)
        }
        
        return report
    
    def _generate_json_report(self, data):
        """Generate JSON report"""
        # Clean up data for JSON serialization
        clean_data = self._clean_for_json(data)
        
        return {
            'report_type': 'json',
            'generated_at': datetime.now().isoformat(),
            'data': clean_data
        }
    
    def _generate_markdown_report(self, data):
        """Generate Markdown report"""
        article = data.get('article', {})
        
        markdown = f"""# News Article Analysis Report

## Article Information
- **Title**: {article.get('title', 'Unknown')}
- **Source**: {article.get('domain', 'Unknown')}
- **Author**: {article.get('author', 'Unknown')}
- **URL**: {article.get('url', 'N/A')}
- **Analysis Date**: {datetime.now().strftime('%B %d, %Y')}

## Overall Assessment
- **Trust Score**: {data.get('trust_score', 0)}% ({data.get('trust_level', 'Unknown')})
- **Political Bias**: {data.get('bias_analysis', {}).get('political_lean', 0)}
- **Clickbait Score**: {data.get('clickbait_analysis', {}).get('score', 0)}%
- **Transparency Score**: {data.get('transparency_analysis', {}).get('score', 0)}%

## Key Findings

### Bias Analysis
{self._format_bias_findings(data.get('bias_analysis', {}))}

### Source Credibility
- **Rating**: {data.get('source_credibility', {}).get('credibility', 'Unknown')}
- **Factual Reporting**: {data.get('source_credibility', {}).get('factual_reporting', 'Unknown')}

### Transparency
{self._format_transparency_findings(data.get('transparency_analysis', {}))}

## Recommendations
{self._format_recommendations(data)}

---
*Generated by News Analyzer*
"""
        
        return {
            'report_type': 'markdown',
            'generated_at': datetime.now().isoformat(),
            'content': markdown
        }
    
    def _get_key_recommendations(self, data):
        """Get key recommendations from analysis"""
        recommendations = []
        
        # Trust-based recommendations
        if data.get('trust_score', 0) < 40:
            recommendations.append("Verify claims through multiple independent sources")
        
        # Bias recommendations
        if abs(data.get('bias_score', 0)) > 0.6:
            recommendations.append("Be aware of strong political bias in reporting")
        
        # Clickbait recommendations
        if data.get('clickbait_analysis', {}).get('score', 0) > 60:
            recommendations.append("Headline may be misleading - focus on article content")
        
        # Transparency recommendations
        if data.get('transparency_analysis', {}).get('score', 0) < 40:
            recommendations.append("Limited transparency - seek additional context")
        
        if not recommendations:
            recommendations.append("Article appears reasonably credible - standard verification recommended")
        
        return recommendations
    
    def _create_detailed_sections(self, data):
        """Create detailed report sections"""
        sections = []
        
        # Bias section
        if data.get('bias_analysis'):
            sections.append({
                'title': 'Bias Analysis',
                'content': self._format_bias_section(data['bias_analysis'])
            })
        
        # Credibility section
        sections.append({
            'title': 'Credibility Assessment',
            'content': self._format_credibility_section(data)
        })
        
        # Transparency section
        if data.get('transparency_analysis'):
            sections.append({
                'title': 'Transparency Analysis',
                'content': self._format_transparency_section(data['transparency_analysis'])
            })
        
        return sections
    
    def _format_bias_findings(self, bias_data):
        """Format bias findings for markdown"""
        if not bias_data:
            return "No bias analysis available"
        
        findings = []
        findings.append(f"- **Political Lean**: {bias_data.get('political_lean', 0)}")
        findings.append(f"- **Objectivity Score**: {bias_data.get('objectivity_score', 'N/A')}")
        findings.append(f"- **Confidence**: {bias_data.get('confidence', 0)}%")
        
        if bias_data.get('factors'):
            findings.append("\n**Bias Factors Detected:**")
            for factor in bias_data.get('factors', []):
                findings.append(f"  - {factor}")
        
        return '\n'.join(findings)
    
    def _format_transparency_findings(self, transparency_data):
        """Format transparency findings"""
        if not transparency_data:
            return "No transparency analysis available"
        
        findings = []
        findings.append(f"Score: {transparency_data.get('score', 0)}%")
        
        indicators = transparency_data.get('indicators', [])
        if indicators:
            findings.append("\n**Transparency Indicators:**")
            for indicator in indicators:
                findings.append(f"- {indicator}")
        
        return '\n'.join(findings)
    
    def _format_recommendations(self, data):
        """Format recommendations"""
        recommendations = self._get_key_recommendations(data)
        return '\n'.join([f"- {rec}" for rec in recommendations])
    
    def _format_bias_section(self, bias_data):
        """Format detailed bias section"""
        return {
            'political_lean': bias_data.get('political_lean', 0),
            'objectivity_score': bias_data.get('objectivity_score', 0),
            'bias_factors': bias_data.get('factors', []),
            'confidence': bias_data.get('confidence', 0)
        }
    
    def _format_credibility_section(self, data):
        """Format credibility section"""
        return {
            'trust_score': data.get('trust_score', 0),
            'source_rating': data.get('source_credibility', {}).get('credibility', 'Unknown'),
            'author_score': data.get('author_info', {}).get('credibility_score', 0),
            'transparency': data.get('transparency_analysis', {}).get('score', 0)
        }
    
    def _format_transparency_section(self, transparency_data):
        """Format transparency section"""
        return {
            'score': transparency_data.get('score', 0),
            'indicators_found': transparency_data.get('indicators', []),
            'missing_elements': transparency_data.get('missing', [])
        }
    
    def _clean_for_json(self, data):
        """Clean data for JSON serialization"""
        # Remove any non-serializable objects
        import copy
        clean_data = copy.deepcopy(data)
        
        # Remove any datetime objects or other non-serializable items
        for key in list(clean_data.keys()):
            if isinstance(clean_data[key], datetime):
                clean_data[key] = clean_data[key].isoformat()
        
        return clean_data
    
    def generate_batch_report(self, analyses_list, format='summary'):
        """
        Generate report for multiple analyses
        
        Args:
            analyses_list: List of analysis results
            format: Report format
            
        Returns:
            Batch report
        """
        return {
            'report_type': f'batch_{format}',
            'generated_at': datetime.now().isoformat(),
            'total_articles': len(analyses_list),
            'analyses': [self.generate(analysis, format) for analysis in analyses_list],
            'aggregate_stats': self._calculate_aggregate_stats(analyses_list)
        }
    
    def _calculate_aggregate_stats(self, analyses_list):
        """Calculate aggregate statistics for batch report"""
        if not analyses_list:
            return {}
        
        trust_scores = [a.get('trust_score', 0) for a in analyses_list]
        bias_scores = [abs(a.get('bias_score', 0)) for a in analyses_list]
        
        return {
            'average_trust_score': sum(trust_scores) / len(trust_scores),
            'average_bias_score': sum(bias_scores) / len(bias_scores),
            'high_trust_count': len([s for s in trust_scores if s >= 70]),
            'low_trust_count': len([s for s in trust_scores if s < 40])
        }
