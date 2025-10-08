"""
Chart Generator Service - SERVICE-INTEGRATED CHARTS
Date: October 8, 2025
Version: 2.0.0 - COMPLETE REWRITE FOR SERVICE INTEGRATION

DEPLOYMENT:
Save as: services/chart_generator.py (REPLACE existing file completely)

CHANGES:
- Charts now embedded IN each service card
- Vibrant, service-specific color schemes
- Contextual visualizations that tell stories
- No more separate charts section at bottom

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
        
        logger.info("[ChartGenerator v2.0.0] Service-integrated charts initialized")
    
    def generate_service_charts(self, service_id: str, service_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate chart for a SPECIFIC service
        
        Args:
            service_id: Service identifier (e.g., 'source_credibility')
            service_data: Data for that specific service
            
        Returns:
            Chart configuration or None
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
                return None
            
            chart_data = generator(service_data)
            
            if chart_data:
                logger.info(f"[ChartGenerator] ✓ Generated chart for {service_id}")
            
            return chart_data
            
        except Exception as e:
            logger.error(f"[ChartGenerator] Error generating chart for {service_id}: {e}")
            return None
    
    def _create_source_credibility_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Source Credibility: Comparison bar chart"""
        article_score = data.get('credibility_score', data.get('score', 0))
        source_name = data.get('source_name', 'This Source')
        
        # Top outlets for comparison
        outlets = [
            {'name': 'Reuters', 'score': 95},
            {'name': 'AP', 'score': 94},
            {'name': 'BBC', 'score': 92},
            {'name': 'NYT', 'score': 88},
            {'name': source_name[:15], 'score': article_score, 'highlight': True}
        ]
        
        # Sort and get top 6
        outlets.sort(key=lambda x: x['score'], reverse=True)
        outlets = outlets[:6]
        
        labels = [o['name'] for o in outlets]
        scores = [o['score'] for o in outlets]
        colors = [
            self.colors['source_credibility']['primary'] if o.get('highlight') 
            else self.colors['source_credibility']['gradient_start']
            for o in outlets
        ]
        
        return {
            'type': 'bar',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': 'Credibility',
                    'data': scores,
                    'backgroundColor': colors,
                    'borderRadius': 8,
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
                        'text': 'How This Article Compares',
                        'font': {'size': 16, 'weight': 'bold'},
                        'color': '#1e293b',
                        'padding': {'bottom': 20}
                    }
                },
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'max': 100,
                        'grid': {'color': '#f1f5f9'},
                        'ticks': {'color': '#64748b', 'font': {'size': 12}}
                    },
                    'x': {
                        'grid': {'display': False},
                        'ticks': {'color': '#334155', 'font': {'size': 13, 'weight': '600'}}
                    }
                }
            }
        }
    
    def _create_bias_detector_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Bias Detector: Political spectrum with position marker"""
        objectivity_score = data.get('objectivity_score', data.get('score', 50))
        political_label = data.get('political_label', 'Center')
        
        # Convert political label to position
        position_map = {
            'Far Left': 10, 'Left': 25, 'Center-Left': 40,
            'Center': 50, 'Center-Right': 60, 'Right': 75, 'Far Right': 90
        }
        position = position_map.get(political_label, 50)
        
        # Create spectrum segments
        segments = [
            {'label': 'Far Left', 'score': 100 if position <= 10 else 0, 'color': self.colors['bias_detector']['far_left']},
            {'label': 'Left', 'score': 100 if 10 < position <= 35 else 0, 'color': self.colors['bias_detector']['left']},
            {'label': 'Center', 'score': 100 if 35 < position <= 65 else 0, 'color': self.colors['bias_detector']['center']},
            {'label': 'Right', 'score': 100 if 65 < position <= 85 else 0, 'color': self.colors['bias_detector']['right']},
            {'label': 'Far Right', 'score': 100 if position > 85 else 0, 'color': self.colors['bias_detector']['far_right']}
        ]
        
        return {
            'type': 'bar',
            'data': {
                'labels': [s['label'] for s in segments],
                'datasets': [{
                    'label': 'Position',
                    'data': [s['score'] for s in segments],
                    'backgroundColor': [s['color'] for s in segments],
                    'borderRadius': 12,
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
                        'text': f'Political Spectrum: {political_label}',
                        'font': {'size': 16, 'weight': 'bold'},
                        'color': '#1e293b'
                    }
                },
                'scales': {
                    'x': {'display': False},
                    'y': {
                        'grid': {'display': False},
                        'ticks': {'font': {'size': 14, 'weight': '600'}}
                    }
                }
            }
        }
    
    def _create_fact_checker_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fact Checker: Verdict breakdown pie chart"""
        fact_checks = data.get('fact_checks', [])
        
        # Count verdicts
        verdicts = {'verified': 0, 'false': 0, 'mixed': 0, 'unverified': 0}
        
        for check in fact_checks:
            verdict = (check.get('verdict', 'unverified') or 'unverified').lower()
            
            if verdict in ['true', 'likely_true', 'verified']:
                verdicts['verified'] += 1
            elif verdict in ['false', 'likely_false']:
                verdicts['false'] += 1
            elif verdict in ['mixed', 'partially_true']:
                verdicts['mixed'] += 1
            else:
                verdicts['unverified'] += 1
        
        total = sum(verdicts.values())
        
        if total == 0:
            return None  # No data to show
        
        return {
            'type': 'doughnut',
            'data': {
                'labels': ['✓ Verified', '✗ False', '◐ Mixed', '? Unverified'],
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
                        'font': {'size': 16, 'weight': 'bold'},
                        'color': '#1e293b'
                    }
                }
            },
            'centerText': {
                'value': f'{verdicts["verified"]}/{total}',
                'label': 'Verified',
                'color': self.colors['fact_checker']['verified']
            }
        }
    
    def _create_transparency_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transparency: Stacked bar showing sources, quotes, attribution"""
        sources = data.get('source_count', data.get('sources_cited', 0))
        quotes = data.get('quote_count', data.get('quotes_included', 0))
        
        # Calculate scores
        source_score = min(30, sources * 5)
        quote_score = min(25, quotes * 8)
        attribution = min(25, data.get('attribution_quality', 15))
        verifiable = min(20, data.get('verifiable_claims', 10))
        
        return {
            'type': 'bar',
            'data': {
                'labels': ['Transparency Score'],
                'datasets': [
                    {
                        'label': f'Sources ({sources})',
                        'data': [source_score],
                        'backgroundColor': self.colors['transparency']['sources'],
                        'borderRadius': {'topLeft': 8, 'topRight': 8}
                    },
                    {
                        'label': f'Quotes ({quotes})',
                        'data': [quote_score],
                        'backgroundColor': self.colors['transparency']['quotes']
                    },
                    {
                        'label': 'Attribution',
                        'data': [attribution],
                        'backgroundColor': self.colors['transparency']['attribution']
                    },
                    {
                        'label': 'Verifiable',
                        'data': [verifiable],
                        'backgroundColor': self.colors['transparency']['verifiable'],
                        'borderRadius': {'bottomLeft': 8, 'bottomRight': 8}
                    }
                ]
            },
            'options': {
                'indexAxis': 'y',
                'responsive': True,
                'maintainAspectRatio': False,
                'scales': {
                    'x': {
                        'stacked': True,
                        'max': 100,
                        'grid': {'color': '#f1f5f9'},
                        'ticks': {'callback': "function(value) { return value + ' pts'; }"}
                    },
                    'y': {
                        'stacked': True,
                        'display': False
                    }
                },
                'plugins': {
                    'legend': {
                        'display': True,
                        'position': 'bottom',
                        'labels': {'padding': 15, 'font': {'size': 12}}
                    },
                    'title': {
                        'display': True,
                        'text': 'Transparency Breakdown',
                        'font': {'size': 16, 'weight': 'bold'},
                        'color': '#1e293b'
                    }
                }
            }
        }
    
    def _create_manipulation_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Manipulation: Horizontal bar showing technique severity"""
        tactics = data.get('tactics_found', [])
        
        if not tactics:
            return None
        
        # Group by severity
        severity_counts = {'high': 0, 'medium': 0, 'low': 0}
        
        for tactic in tactics[:10]:  # Top 10
            severity = tactic.get('severity', 'low').lower()
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        return {
            'type': 'bar',
            'data': {
                'labels': ['High Risk', 'Medium Risk', 'Low Risk'],
                'datasets': [{
                    'label': 'Techniques',
                    'data': [
                        severity_counts['high'],
                        severity_counts['medium'],
                        severity_counts['low']
                    ],
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
                        'font': {'size': 16, 'weight': 'bold'},
                        'color': '#1e293b'
                    }
                },
                'scales': {
                    'x': {
                        'grid': {'color': '#f1f5f9'},
                        'ticks': {'stepSize': 1}
                    },
                    'y': {
                        'grid': {'display': False}
                    }
                }
            }
        }
    
    def _create_author_chart(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Author: Simple credibility meter"""
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
        quality = data.get('quality_score', 0)
        readability = data.get('readability_score', 0) if data.get('readability_score') else 50
        
        return {
            'type': 'radar',
            'data': {
                'labels': ['Quality', 'Readability', 'Structure', 'Depth'],
                'datasets': [{
                    'data': [quality, readability, quality * 0.9, quality * 0.8],
                    'backgroundColor': 'rgba(236, 72, 153, 0.2)',
                    'borderColor': self.colors['author']['primary'],
                    'borderWidth': 3,
                    'pointBackgroundColor': self.colors['author']['primary'],
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


# Initialize singleton
_chart_generator_instance = None

def get_chart_generator() -> ChartGenerator:
    """Get or create chart generator instance"""
    global _chart_generator_instance
    if _chart_generator_instance is None:
        _chart_generator_instance = ChartGenerator()
    return _chart_generator_instance
