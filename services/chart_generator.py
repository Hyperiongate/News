"""
Chart Generator Service - Backend Chart Data Generator
Date: October 8, 2025
Version: 1.0.0 - TIER 2: VISUAL IMPACT

PURPOSE:
Generates chart-ready data structures for frontend Chart.js rendering.
Does NOT generate images - creates JSON data that Chart.js consumes.

DEPLOYMENT:
1. Save as: services/chart_generator.py
2. No dependencies beyond standard library
3. Works with existing analysis pipeline

CHARTS PROVIDED:
1. Trust Score Gauge (speedometer)
2. Bias Spectrum Radar
3. Fact-Check Pie Chart
4. Source Comparison Bar Chart
5. Service Breakdown Donut
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ChartGenerator:
    """Generates chart data for frontend visualization"""
    
    def __init__(self):
        self.service_name = 'chart_generator'
        
        # Chart color schemes
        self.colors = {
            'trust': {
                'high': '#10b981',      # Green
                'medium': '#3b82f6',    # Blue
                'low': '#ef4444'        # Red
            },
            'services': {
                'source_credibility': '#6366f1',
                'author_analyzer': '#06b6d4',
                'bias_detector': '#f59e0b',
                'fact_checker': '#3b82f6',
                'transparency_analyzer': '#8b5cf6',
                'manipulation_detector': '#ef4444',
                'content_analyzer': '#ec4899'
            },
            'bias': {
                'far_left': '#1e40af',
                'left': '#3b82f6',
                'center': '#10b981',
                'right': '#f59e0b',
                'far_right': '#ef4444'
            },
            'verdict': {
                'true': '#10b981',
                'false': '#ef4444',
                'mixed': '#f59e0b',
                'unverified': '#6b7280'
            }
        }
        
        logger.info("[ChartGenerator] Initialized")
    
    def generate_all_charts(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point: Generate all chart data from analysis results
        
        Args:
            analysis_data: Complete analysis results from news_analyzer
            
        Returns:
            Dict with chart data for each visualization
        """
        try:
            logger.info("[ChartGenerator] Generating chart data...")
            
            trust_score = analysis_data.get('trust_score', 50)
            detailed = analysis_data.get('detailed_analysis', {})
            
            charts = {
                'trust_gauge': self._create_trust_gauge(trust_score),
                'service_breakdown': self._create_service_breakdown(detailed),
                'bias_radar': self._create_bias_radar(detailed.get('bias_detector', {})),
                'fact_check_pie': self._create_fact_check_pie(detailed.get('fact_checker', {})),
                'source_comparison': self._create_source_comparison(
                    detailed.get('source_credibility', {}), 
                    analysis_data.get('source', 'Unknown')
                ),
                'transparency_bars': self._create_transparency_bars(
                    detailed.get('transparency_analyzer', {})
                )
            }
            
            logger.info(f"[ChartGenerator] ✓ Generated {len(charts)} chart datasets")
            
            return {
                'success': True,
                'charts': charts,
                'chart_count': len(charts)
            }
            
        except Exception as e:
            logger.error(f"[ChartGenerator] Error: {e}", exc_info=True)
            return {
                'success': False,
                'charts': {},
                'error': str(e)
            }
    
    def _create_trust_gauge(self, trust_score: int) -> Dict[str, Any]:
        """
        Create trust score gauge/speedometer data
        
        Returns Chart.js doughnut chart data configured as gauge
        """
        score = max(0, min(100, trust_score))
        
        # Determine color
        if score >= 70:
            color = self.colors['trust']['high']
            label = 'High Trust'
        elif score >= 40:
            color = self.colors['trust']['medium']
            label = 'Medium Trust'
        else:
            color = self.colors['trust']['low']
            label = 'Low Trust'
        
        return {
            'type': 'doughnut',
            'data': {
                'labels': ['Score', 'Remaining'],
                'datasets': [{
                    'data': [score, 100 - score],
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
                    'legend': {
                        'display': False
                    },
                    'tooltip': {
                        'enabled': False
                    }
                }
            },
            'centerText': {
                'value': str(score),
                'label': label,
                'color': color
            }
        }
    
    def _create_service_breakdown(self, detailed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create service contribution breakdown chart
        
        Returns Chart.js horizontal bar chart data
        """
        weights = {
            'source_credibility': 25,
            'bias_detector': 20,
            'author_analyzer': 15,
            'fact_checker': 15,
            'transparency_analyzer': 10,
            'manipulation_detector': 10,
            'content_analyzer': 5
        }
        
        labels = []
        data = []
        colors = []
        
        for service, weight in weights.items():
            service_data = detailed.get(service, {})
            
            # Get score from various possible field names
            score = 0
            if service == 'source_credibility':
                score = service_data.get('credibility_score', service_data.get('score', 0))
            elif service == 'bias_detector':
                score = service_data.get('objectivity_score', service_data.get('score', 0))
            elif service == 'fact_checker':
                score = service_data.get('verification_score', 
                        service_data.get('accuracy_score', service_data.get('score', 0)))
            elif service == 'author_analyzer':
                score = service_data.get('credibility_score', service_data.get('score', 0))
            elif service == 'transparency_analyzer':
                score = service_data.get('transparency_score', service_data.get('score', 0))
            elif service == 'manipulation_detector':
                score = service_data.get('integrity_score', service_data.get('score', 0))
            elif service == 'content_analyzer':
                score = service_data.get('quality_score', service_data.get('score', 0))
            else:
                score = service_data.get('score', 0)
            
            contribution = round(score * (weight / 100), 1)
            
            labels.append(service.replace('_', ' ').title())
            data.append(contribution)
            colors.append(self.colors['services'].get(service, '#6b7280'))
        
        return {
            'type': 'bar',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': 'Contribution to Trust Score',
                    'data': data,
                    'backgroundColor': colors,
                    'borderRadius': 6
                }]
            },
            'options': {
                'indexAxis': 'y',
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'legend': {
                        'display': False
                    },
                    'tooltip': {
                        'callbacks': {
                            'label': 'function(context) { return context.parsed.x + " points"; }'
                        }
                    }
                },
                'scales': {
                    'x': {
                        'beginAtZero': True,
                        'max': 25,
                        'ticks': {
                            'callback': 'function(value) { return value + " pts"; }'
                        }
                    }
                }
            }
        }
    
    def _create_bias_radar(self, bias_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create bias spectrum radar chart
        
        Returns Chart.js radar chart data
        """
        # Get bias dimensions if available
        dimensions = bias_data.get('bias_dimensions', {})
        
        if not dimensions:
            # Default dimensions
            labels = ['Political', 'Emotional', 'Sensational', 'Factual', 'Balance']
            data = [50, 50, 50, 50, 50]
        else:
            labels = []
            data = []
            
            for dim_name, dim_data in list(dimensions.items())[:6]:  # Max 6 dimensions
                labels.append(dim_name.replace('_', ' ').title())
                score = abs(dim_data.get('score', 0)) * 100
                data.append(min(100, score))
        
        return {
            'type': 'radar',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': 'Bias Analysis',
                    'data': data,
                    'backgroundColor': 'rgba(99, 102, 241, 0.2)',
                    'borderColor': '#6366f1',
                    'borderWidth': 2,
                    'pointBackgroundColor': '#6366f1',
                    'pointBorderColor': '#fff',
                    'pointHoverBackgroundColor': '#fff',
                    'pointHoverBorderColor': '#6366f1'
                }]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'scales': {
                    'r': {
                        'beginAtZero': True,
                        'max': 100,
                        'ticks': {
                            'stepSize': 25
                        }
                    }
                },
                'plugins': {
                    'legend': {
                        'display': False
                    }
                }
            }
        }
    
    def _create_fact_check_pie(self, fact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create fact-check verdict breakdown pie chart
        
        Returns Chart.js pie chart data
        """
        fact_checks = fact_data.get('fact_checks', [])
        
        # Count verdicts
        verdicts = {'true': 0, 'false': 0, 'mixed': 0, 'unverified': 0}
        
        for check in fact_checks:
            verdict = (check.get('verdict', 'unverified') or 'unverified').lower()
            
            if verdict in ['true', 'likely_true', 'verified']:
                verdicts['true'] += 1
            elif verdict in ['false', 'likely_false']:
                verdicts['false'] += 1
            elif verdict in ['mixed', 'partially_true']:
                verdicts['mixed'] += 1
            else:
                verdicts['unverified'] += 1
        
        # If no checks, show placeholder
        if sum(verdicts.values()) == 0:
            return {
                'type': 'pie',
                'data': {
                    'labels': ['No Data'],
                    'datasets': [{
                        'data': [1],
                        'backgroundColor': ['#e5e7eb']
                    }]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'legend': {
                            'position': 'bottom'
                        }
                    }
                }
            }
        
        return {
            'type': 'pie',
            'data': {
                'labels': ['True', 'False', 'Mixed', 'Unverified'],
                'datasets': [{
                    'data': [verdicts['true'], verdicts['false'], 
                            verdicts['mixed'], verdicts['unverified']],
                    'backgroundColor': [
                        self.colors['verdict']['true'],
                        self.colors['verdict']['false'],
                        self.colors['verdict']['mixed'],
                        self.colors['verdict']['unverified']
                    ],
                    'borderWidth': 2,
                    'borderColor': '#fff'
                }]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'legend': {
                        'position': 'bottom',
                        'labels': {
                            'padding': 15,
                            'usePointStyle': True
                        }
                    },
                    'tooltip': {
                        'callbacks': {
                            'label': 'function(context) { return context.label + ": " + context.parsed + " claims"; }'
                        }
                    }
                }
            }
        }
    
    def _create_source_comparison(self, source_data: Dict[str, Any], 
                                  current_source: str) -> Dict[str, Any]:
        """
        Create source comparison bar chart
        
        Returns Chart.js bar chart comparing current source to top outlets
        """
        top_sources = [
            {'name': 'Reuters', 'score': 95},
            {'name': 'Associated Press', 'score': 94},
            {'name': 'BBC News', 'score': 92},
            {'name': 'The New York Times', 'score': 88},
            {'name': 'The Washington Post', 'score': 87},
            {'name': 'NPR', 'score': 86},
            {'name': 'Wall Street Journal', 'score': 85}
        ]
        
        current_score = source_data.get('credibility_score', source_data.get('score', 0))
        
        # Add current source if not in list
        source_in_list = any(
            s['name'].lower() in current_source.lower() or 
            current_source.lower() in s['name'].lower() 
            for s in top_sources
        )
        
        if not source_in_list and current_source not in ['Unknown', 'This Source']:
            top_sources.append({
                'name': current_source[:20] + '...' if len(current_source) > 20 else current_source,
                'score': current_score,
                'current': True
            })
        
        # Sort by score
        top_sources.sort(key=lambda x: x['score'], reverse=True)
        top_sources = top_sources[:8]  # Show top 8
        
        labels = [s['name'] for s in top_sources]
        data = [s['score'] for s in top_sources]
        colors = [
            '#6366f1' if s.get('current') else '#94a3b8' 
            for s in top_sources
        ]
        
        return {
            'type': 'bar',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': 'Credibility Score',
                    'data': data,
                    'backgroundColor': colors,
                    'borderRadius': 6
                }]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'legend': {
                        'display': False
                    },
                    'tooltip': {
                        'callbacks': {
                            'label': 'function(context) { return "Score: " + context.parsed.y + "/100"; }'
                        }
                    }
                },
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'max': 100,
                        'ticks': {
                            'callback': 'function(value) { return value; }'
                        }
                    }
                }
            }
        }
    
    def _create_transparency_bars(self, trans_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create transparency breakdown bar chart
        
        Returns Chart.js bar chart showing transparency components
        """
        sources = trans_data.get('source_count', trans_data.get('sources_cited', 0))
        quotes = trans_data.get('quote_count', trans_data.get('quotes_included', 0))
        
        # Calculate component scores
        source_score = min(30, sources * 5)
        quote_score = min(25, quotes * 8)
        attribution_score = trans_data.get('attribution_quality', 20)
        verifiable_score = trans_data.get('verifiable_claims', 15)
        
        return {
            'type': 'bar',
            'data': {
                'labels': ['Sources Cited', 'Direct Quotes', 'Attribution', 'Verifiable'],
                'datasets': [{
                    'label': 'Points',
                    'data': [source_score, quote_score, attribution_score, verifiable_score],
                    'backgroundColor': ['#6366f1', '#3b82f6', '#8b5cf6', '#06b6d4'],
                    'borderRadius': 6
                }]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'legend': {
                        'display': False
                    }
                },
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'max': 30,
                        'ticks': {
                            'callback': 'function(value) { return value + " pts"; }'
                        }
                    }
                }
            }
        }
