"""
Chart Generator Service - SERVICE-INTEGRATED CHARTS
Date: October 8, 2025
Version: 2.1.0 - COMPLETE WITH ALL METHODS

DEPLOYMENT:
Save as: services/chart_generator.py (REPLACE existing file completely)

CRITICAL METHODS:
- generate_service_chart(service_id, data) - For individual services
- generate_all_charts(response) - For top-level charts
- Both methods are required by news_analyzer.py

This is a COMPLETE file - deploy as-is.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ChartGenerator:
    """Generates service-integrated chart visualizations"""
    
    def __init__(self):
        self.service_name = 'chart_generator'
        
        # Vibrant color schemes per service
        self.colors = {
            'source_credibility': {
                'primary': '#6366f1',
                'gradient_start': '#818cf8',
                'gradient_end': '#4f46e5',
                'excellent': '#10b981',
                'good': '#3b82f6',
                'moderate': '#f59e0b',
                'low': '#ef4444'
            },
            'bias_detector': {
                'primary': '#f59e0b',
                'left': '#3b82f6',
                'center': '#10b981',
                'right': '#f59e0b',
                'far_right': '#ef4444',
                'far_left': '#1e40af'
            },
            'fact_checker': {
                'primary': '#3b82f6',
                'verified': '#10b981',
                'false': '#ef4444',
                'mixed': '#f59e0b',
                'unverified': '#6b7280'
            },
            'transparency': {
                'primary': '#8b5cf6',
                'sources': '#6366f1',
                'quotes': '#3b82f6',
                'attribution': '#8b5cf6',
                'verifiable': '#06b6d4'
            },
            'manipulation': {
                'primary': '#ef4444',
                'high_risk': '#dc2626',
                'medium_risk': '#f59e0b',
                'low_risk': '#10b981',
                'none': '#6b7280'
            },
            'author': {
                'primary': '#06b6d4',
                'high_cred': '#10b981',
                'medium_cred': '#3b82f6',
                'low_cred': '#f59e0b'
            }
        }
        
        logger.info("[ChartGenerator v2.1.0] Service-integrated charts initialized")
    
    # ============================================================================
    # CRITICAL METHOD 1: For individual service charts
    # ============================================================================
    def generate_service_chart(self, service_id: str, service_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate chart for a SPECIFIC service (called by news_analyzer.py)
        
        Args:
            service_id: Service identifier (e.g., 'source_credibility')
            service_data: Data for that specific service
            
        Returns:
            Chart configuration dict or None
        """
        try:
            chart_generators = {
                'source_credibility': self._create_source_credibility_chart,
                'bias_detector': self._create_bias_detector_chart,
                'fact_checker': self._create_fact_checker_chart,
                'transparency_analyzer': self._create_transparency_chart,
                'manipulation_detector': self._create_manipulation_chart,
                'author_analyzer': self._create_author_chart,
                'content_analyzer': self._create_content_chart
            }
            
            generator = chart_generators.get(service_id)
            if not generator:
                logger.debug(f"[ChartGenerator] No chart generator for {service_id}")
                return None
            
            chart_data = generator(service_data)
            
            if chart_data:
                logger.debug(f"[ChartGenerator] ✓ Generated chart for {service_id}")
            
            return chart_data
            
        except Exception as e:
            logger.error(f"[ChartGenerator] Error generating chart for {service_id}: {e}")
            return None
    
    # ============================================================================
    # CRITICAL METHOD 2: For top-level overview charts
    # ============================================================================
    def generate_all_charts(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate all top-level overview charts (called by news_analyzer.py)
        
        Args:
            response: Complete analysis response
            
        Returns:
            Dict with success status and charts dict
        """
        try:
            logger.info("[ChartGenerator] Generating overview charts...")
            
            charts = {}
            detailed = response.get('detailed_analysis', {})
            trust_score = response.get('trust_score', 50)
            
            # Trust gauge chart
            charts['trust_gauge'] = self._create_trust_gauge_chart(trust_score)
            
            # Service breakdown chart
            charts['service_breakdown'] = self._create_service_breakdown_chart(detailed)
            
            # Bias radar chart
            if 'bias_detector' in detailed:
                charts['bias_radar'] = self._create_bias_radar_chart(detailed['bias_detector'])
            
            # Fact check pie chart
            if 'fact_checker' in detailed:
                charts['fact_check_pie'] = self._create_fact_check_pie_chart(detailed['fact_checker'])
            
            # Source comparison
            if 'source_credibility' in detailed:
                charts['source_comparison'] = self._create_source_comparison_chart(detailed['source_credibility'])
            
            # Transparency bars
            if 'transparency_analyzer' in detailed:
                charts['transparency_bars'] = self._create_transparency_bars_chart(detailed['transparency_analyzer'])
            
            chart_count = len(charts)
            logger.info(f"[ChartGenerator] ✓ Generated {chart_count} overview charts")
            
            return {
                'success': True,
                'charts': charts,
                'chart_count': chart_count
            }
            
        except Exception as e:
            logger.error(f"[ChartGenerator] Error generating overview charts: {e}")
            return {
                'success': False,
                'charts': {},
                'chart_count': 0,
                'error': str(e)
            }
    
    # ============================================================================
    # INDIVIDUAL SERVICE CHART CREATORS
    # ============================================================================
    
    def _create_source_credibility_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Source Credibility: Comparison bar chart"""
        article_score = data.get('credibility_score', data.get('score', 0))
        source_name = data.get('source_name', data.get('source', 'This Source'))
        
        # Top outlets for comparison
        outlets = [
            {'name': 'Reuters', 'score': 95},
            {'name': 'Associated Press', 'score': 94},
            {'name': 'BBC News', 'score': 92},
            {'name': 'The New York Times', 'score': 88},
            {'name': 'The Washington Post', 'score': 87}
        ]
        
        # Add current source if not in list
        if not any(o['name'].lower() == source_name.lower() for o in outlets):
            outlets.append({'name': source_name, 'score': article_score})
        
        # Sort by score
        outlets.sort(key=lambda x: x['score'], reverse=True)
        outlets = outlets[:6]  # Top 6
        
        labels = [o['name'] for o in outlets]
        scores = [o['score'] for o in outlets]
        colors = [self.colors['source_credibility']['primary'] if o['name'] == source_name 
                 else '#94a3b8' for o in outlets]
        
        return {
            'type': 'bar',
            'data': {
                'labels': labels,
                'datasets': [{
                    'data': scores,
                    'backgroundColor': colors,
                    'borderRadius': 8,
                    'barThickness': 40
                }]
            },
            'options': {
                'indexAxis': 'y',
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'legend': {'display': False},
                    'title': {
                        'display': True,
                        'text': 'Outlet Credibility Comparison',
                        'font': {'size': 16, 'weight': 'bold'}
                    }
                },
                'scales': {
                    'x': {
                        'beginAtZero': True,
                        'max': 100,
                        'grid': {'color': '#f1f5f9'}
                    },
                    'y': {
                        'grid': {'display': False}
                    }
                }
            }
        }
    
    def _create_bias_detector_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Bias: Radar chart showing dimensions"""
        dimensions = data.get('dimensions', {})
        
        # Default dimensions if not provided
        if not dimensions:
            score = data.get('objectivity_score', data.get('score', 50))
            dimensions = {
                'language': score,
                'source_selection': score,
                'framing': score,
                'tone': score,
                'balance': score
            }
        
        labels = [k.replace('_', ' ').title() for k in dimensions.keys()]
        values = list(dimensions.values())
        
        return {
            'type': 'radar',
            'data': {
                'labels': labels,
                'datasets': [{
                    'data': values,
                    'backgroundColor': 'rgba(245, 158, 11, 0.2)',
                    'borderColor': self.colors['bias_detector']['primary'],
                    'borderWidth': 3,
                    'pointBackgroundColor': self.colors['bias_detector']['primary'],
                    'pointBorderColor': '#fff',
                    'pointBorderWidth': 2,
                    'pointRadius': 5
                }]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'scales': {
                    'r': {
                        'beginAtZero': True,
                        'max': 100,
                        'ticks': {'display': False},
                        'grid': {'color': '#f1f5f9'}
                    }
                },
                'plugins': {
                    'legend': {'display': False}
                }
            }
        }
    
    def _create_fact_checker_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fact Checker: Pie chart of verdicts"""
        claims = data.get('fact_checks', data.get('claims', []))
        
        # Count verdicts
        verdicts = {'verified': 0, 'false': 0, 'mixed': 0, 'unverified': 0}
        
        for claim in claims:
            verdict = claim.get('verdict', 'unverified').lower()
            if 'true' in verdict or 'verified' in verdict:
                verdicts['verified'] += 1
            elif 'false' in verdict:
                verdicts['false'] += 1
            elif 'mixed' in verdict or 'partial' in verdict:
                verdicts['mixed'] += 1
            else:
                verdicts['unverified'] += 1
        
        total = sum(verdicts.values())
        if total == 0:
            verdicts['unverified'] = 1
            total = 1
        
        return {
            'type': 'doughnut',
            'data': {
                'labels': ['Verified', 'False', 'Mixed', 'Unverified'],
                'datasets': [{
                    'data': [verdicts['verified'], verdicts['false'], 
                            verdicts['mixed'], verdicts['unverified']],
                    'backgroundColor': [
                        self.colors['fact_checker']['verified'],
                        self.colors['fact_checker']['false'],
                        self.colors['fact_checker']['mixed'],
                        self.colors['fact_checker']['unverified']
                    ],
                    'borderWidth': 3,
                    'borderColor': '#fff',
                    'hoverOffset': 10
                }]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'cutout': '60%',
                'plugins': {
                    'legend': {
                        'position': 'bottom',
                        'labels': {
                            'padding': 20,
                            'font': {'size': 13, 'weight': '600'},
                            'usePointStyle': True,
                            'pointStyle': 'circle'
                        }
                    },
                    'title': {
                        'display': True,
                        'text': f'{total} Claims Analyzed',
                        'font': {'size': 16, 'weight': 'bold'}
                    }
                }
            }
        }
    
    def _create_transparency_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transparency: Stacked bar showing components"""
        sources = data.get('source_count', data.get('sources_cited', 0))
        quotes = data.get('quote_count', data.get('quotes_included', 0))
        score = data.get('transparency_score', data.get('score', 0))
        
        # Calculate component scores
        source_score = min(30, sources * 5)
        quote_score = min(25, quotes * 8)
        attribution_score = int(score * 0.25)
        verifiable_score = int(score * 0.20)
        
        return {
            'type': 'bar',
            'data': {
                'labels': ['Transparency Score'],
                'datasets': [
                    {
                        'label': 'Sources',
                        'data': [source_score],
                        'backgroundColor': self.colors['transparency']['sources']
                    },
                    {
                        'label': 'Quotes',
                        'data': [quote_score],
                        'backgroundColor': self.colors['transparency']['quotes']
                    },
                    {
                        'label': 'Attribution',
                        'data': [attribution_score],
                        'backgroundColor': self.colors['transparency']['attribution']
                    },
                    {
                        'label': 'Verifiable',
                        'data': [verifiable_score],
                        'backgroundColor': self.colors['transparency']['verifiable']
                    }
                ]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'scales': {
                    'x': {'stacked': True, 'grid': {'display': False}},
                    'y': {'stacked': True, 'max': 100, 'grid': {'color': '#f1f5f9'}}
                },
                'plugins': {
                    'legend': {
                        'position': 'bottom',
                        'labels': {'padding': 15, 'font': {'size': 12}}
                    },
                    'title': {
                        'display': True,
                        'text': 'Transparency Breakdown',
                        'font': {'size': 16, 'weight': 'bold'}
                    }
                }
            }
        }
    
    def _create_manipulation_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Manipulation: Bar chart by severity"""
        tactics = data.get('tactics_found', [])
        
        # Count by severity
        severity_counts = {'high': 0, 'medium': 0, 'low': 0}
        
        for tactic in tactics:
            severity = tactic.get('severity', 'low').lower()
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        return {
            'type': 'bar',
            'data': {
                'labels': ['High Risk', 'Medium Risk', 'Low Risk'],
                'datasets': [{
                    'data': [severity_counts['high'], severity_counts['medium'], severity_counts['low']],
                    'backgroundColor': [
                        self.colors['manipulation']['high_risk'],
                        self.colors['manipulation']['medium_risk'],
                        self.colors['manipulation']['low_risk']
                    ],
                    'borderRadius': 8,
                    'barThickness': 50
                }]
            },
            'options': {
                'indexAxis': 'y',
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'legend': {'display': False},
                    'title': {
                        'display': True,
                        'text': 'Manipulation Techniques by Severity',
                        'font': {'size': 16, 'weight': 'bold'}
                    }
                },
                'scales': {
                    'x': {'grid': {'color': '#f1f5f9'}, 'ticks': {'stepSize': 1}},
                    'y': {'grid': {'display': False}}
                }
            }
        }
    
    def _create_author_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Author: Simple credibility gauge"""
        credibility = data.get('credibility_score', data.get('score', 50))
        
        # Determine color
        if credibility >= 80:
            color = self.colors['author']['high_cred']
        elif credibility >= 60:
            color = self.colors['author']['medium_cred']
        else:
            color = self.colors['author']['low_cred']
        
        return {
            'type': 'doughnut',
            'data': {
                'datasets': [{
                    'data': [credibility, 100 - credibility],
                    'backgroundColor': [color, '#e5e7eb'],
                    'borderWidth': 0,
                    'circumference': 180,
                    'rotation': 270
                }]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'cutout': '70%',
                'plugins': {
                    'legend': {'display': False},
                    'tooltip': {'enabled': False}
                }
            },
            'centerText': {
                'value': str(credibility),
                'label': 'Credibility',
                'color': color
            }
        }
    
    def _create_content_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Content: Quality metrics radar"""
        quality = data.get('quality_score', data.get('score', 0))
        readability = data.get('readability_score', 50)
        
        return {
            'type': 'radar',
            'data': {
                'labels': ['Quality', 'Readability', 'Structure', 'Depth'],
                'datasets': [{
                    'data': [quality, readability, quality * 0.9, quality * 0.8],
                    'backgroundColor': 'rgba(236, 72, 153, 0.2)',
                    'borderColor': '#ec4899',
                    'borderWidth': 3,
                    'pointBackgroundColor': '#ec4899',
                    'pointBorderColor': '#fff',
                    'pointBorderWidth': 2,
                    'pointRadius': 5
                }]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'scales': {
                    'r': {
                        'beginAtZero': True,
                        'max': 100,
                        'ticks': {'display': False},
                        'grid': {'color': '#f1f5f9'}
                    }
                },
                'plugins': {
                    'legend': {'display': False}
                }
            }
        }
    
    # ============================================================================
    # TOP-LEVEL OVERVIEW CHART CREATORS
    # ============================================================================
    
    def _create_trust_gauge_chart(self, trust_score: int) -> Dict[str, Any]:
        """Trust gauge (semi-circle)"""
        if trust_score >= 80:
            color = '#10b981'
        elif trust_score >= 60:
            color = '#3b82f6'
        elif trust_score >= 40:
            color = '#f59e0b'
        else:
            color = '#ef4444'
        
        return {
            'type': 'doughnut',
            'data': {
                'datasets': [{
                    'data': [trust_score, 100 - trust_score],
                    'backgroundColor': [color, '#e5e7eb'],
                    'borderWidth': 0,
                    'circumference': 180,
                    'rotation': 270
                }]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'cutout': '75%',
                'plugins': {
                    'legend': {'display': False},
                    'tooltip': {'enabled': False}
                }
            },
            'centerText': {
                'value': str(trust_score),
                'label': 'Trust Score',
                'color': color
            }
        }
    
    def _create_service_breakdown_chart(self, detailed: Dict[str, Any]) -> Dict[str, Any]:
        """Service scores bar chart"""
        services = {
            'Source': detailed.get('source_credibility', {}).get('score', 0),
            'Bias': detailed.get('bias_detector', {}).get('score', 0),
            'Facts': detailed.get('fact_checker', {}).get('score', 0),
            'Author': detailed.get('author_analyzer', {}).get('score', 0),
            'Transparency': detailed.get('transparency_analyzer', {}).get('score', 0),
            'Manipulation': detailed.get('manipulation_detector', {}).get('score', 0),
            'Content': detailed.get('content_analyzer', {}).get('score', 0)
        }
        
        labels = list(services.keys())
        scores = list(services.values())
        
        return {
            'type': 'bar',
            'data': {
                'labels': labels,
                'datasets': [{
                    'data': scores,
                    'backgroundColor': '#3b82f6',
                    'borderRadius': 6,
                    'barThickness': 40
                }]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'legend': {'display': False},
                    'title': {
                        'display': True,
                        'text': 'Service Score Breakdown',
                        'font': {'size': 16, 'weight': 'bold'}
                    }
                },
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'max': 100,
                        'grid': {'color': '#f1f5f9'}
                    },
                    'x': {
                        'grid': {'display': False}
                    }
                }
            }
        }
    
    def _create_bias_radar_chart(self, bias_data: Dict[str, Any]) -> Dict[str, Any]:
        """Bias dimensions radar (same as service chart)"""
        return self._create_bias_detector_chart(bias_data)
    
    def _create_fact_check_pie_chart(self, fact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fact check pie (same as service chart)"""
        return self._create_fact_checker_chart(fact_data)
    
    def _create_source_comparison_chart(self, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """Source comparison (same as service chart)"""
        return self._create_source_credibility_chart(source_data)
    
    def _create_transparency_bars_chart(self, trans_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transparency bars (same as service chart)"""
        return self._create_transparency_chart(trans_data)


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================
_chart_generator_instance = None

def get_chart_generator() -> ChartGenerator:
    """Get or create chart generator instance"""
    global _chart_generator_instance
    if _chart_generator_instance is None:
        _chart_generator_instance = ChartGenerator()
    return _chart_generator_instance
