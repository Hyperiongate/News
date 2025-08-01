# services/report_generator.py
"""
Report Generation Service
Creates various report formats from analysis results
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
            'summary': self._create_text_summary(data),
            'recommendations': self._get_key_recommendations(data)
        }
        
        return summary
    
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
    
    def _create_text_summary(self, data):
        """Create text summary of analysis"""
        trust_score = data.get('trust_score', 0)
        bias_score = abs(data.get('bias_score', 0))
        
        if trust_score >= 70:
            trust_assessment = "high credibility"
        elif trust_score >= 40:
            trust_assessment = "moderate credibility"
        else:
            trust_assessment = "low credibility"
        
        if bias_score < 0.3:
            bias_assessment = "minimal bias"
        elif bias_score < 0.6:
            bias_assessment = "moderate bias"
        else:
            bias_assessment = "significant bias"
        
        summary = f"""
        This article from {data.get('article', {}).get('domain', 'unknown source')} shows {trust_assessment} 
        with a trust score of {trust_score}%. The analysis detected {bias_assessment} with a political lean 
        score of {data.get('bias_analysis', {}).get('political_lean', 0)}. 
        
        The source has a {data.get('source_credibility', {}).get('credibility', 'unknown')} credibility rating.
        Transparency score is {data.get('transparency_analysis', {}).get('score', 0)}%, 
        indicating {'good' if data.get('transparency_analysis', {}).get('score', 0) > 60 else 'poor'} disclosure practices.
        """
        
        return summary.strip()
    
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
        findings.append(f"- **Objectivity Score**: {bias_data.get('objectivity_score', 'N/A')}")  # Fixed line!
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
