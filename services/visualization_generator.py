"""
FILE: services/visualization_generator.py
PURPOSE: Generate visualizations for analysis results (charts, graphs, etc.)
"""

import logging
import json
import base64
from typing import Dict, Any, List, Optional, Tuple
from io import BytesIO
from services.base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)

# Try to import visualization libraries
MATPLOTLIB_AVAILABLE = False
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.patches import Circle, Rectangle, FancyBboxPatch
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
    logger.info("Matplotlib loaded successfully")
except ImportError:
    logger.warning("Matplotlib not installed - some visualizations will be unavailable")


class VisualizationGenerator(BaseAnalyzer):
    """Generate visualizations for news analysis results"""
    
    def __init__(self):
        super().__init__('visualization_generator')
        
        # Color schemes for different visualizations
        self.color_schemes = {
            'trust': {
                'high': '#10b981',    # Green
                'moderate': '#f59e0b', # Amber
                'low': '#ef4444'       # Red
            },
            'bias': {
                'political': '#6366f1',   # Indigo
                'corporate': '#10b981',   # Emerald
                'sensational': '#f59e0b', # Amber
                'nationalistic': '#ef4444', # Red
                'establishment': '#8b5cf6' # Purple
            },
            'general': {
                'primary': '#3b82f6',
                'secondary': '#6b7280',
                'accent': '#1e40af',
                'background': '#f3f4f6',
                'text': '#1f2937'
            }
        }
        
        logger.info(f"VisualizationGenerator initialized - Matplotlib available: {MATPLOTLIB_AVAILABLE}")
    
    def _check_availability(self) -> bool:
        """Check if visualization libraries are available"""
        return MATPLOTLIB_AVAILABLE
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate visualizations based on analysis data
        
        Expected input:
            - trust_score: Overall trust score
            - bias_analysis: Bias detection results
            - fact_checks: Fact checking results
            - source_credibility: Source analysis results
            - author_info: Author analysis results
            - visualization_type: (optional) Specific visualization requested
            
        Returns:
            Standardized response with generated visualizations
        """
        if not self.is_available:
            # Return data-only visualizations that frontend can render
            return self._generate_data_visualizations(data)
        
        return self._generate_visualizations(data)
    
    def _generate_visualizations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate all relevant visualizations"""
        try:
            visualizations = {}
            
            # Generate trust score gauge
            if 'trust_score' in data:
                visualizations['trust_gauge'] = self._create_trust_gauge(data['trust_score'])
            
            # Generate bias radar chart
            if 'bias_analysis' in data and data['bias_analysis'].get('bias_dimensions'):
                visualizations['bias_radar'] = self._create_bias_radar(data['bias_analysis']['bias_dimensions'])
            
            # Generate fact check summary
            if 'fact_checks' in data:
                visualizations['fact_check_summary'] = self._create_fact_check_chart(data['fact_checks'])
            
            # Generate source credibility comparison
            if 'source_credibility' in data:
                visualizations['credibility_meter'] = self._create_credibility_meter(data['source_credibility'])
            
            # Generate author credibility visualization
            if 'author_info' in data:
                visualizations['author_profile'] = self._create_author_visualization(data['author_info'])
            
            # Generate comprehensive dashboard
            visualizations['analysis_dashboard'] = self._create_analysis_dashboard(data)
            
            # Add data-only visualizations for frontend
            visualizations['data_visualizations'] = self._generate_data_visualizations(data)['data']['visualizations']
            
            return {
                'service': self.service_name,
                'success': True,
                'data': {
                    'visualizations': visualizations,
                    'visualization_count': len(visualizations),
                    'formats_available': ['png', 'svg', 'json'],
                    'summary': self._generate_visualization_summary(visualizations)
                },
                'metadata': {
                    'library_used': 'matplotlib',
                    'charts_generated': list(visualizations.keys())
                }
            }
            
        except Exception as e:
            logger.error(f"Visualization generation failed: {e}", exc_info=True)
            # Fall back to data-only visualizations
            return self._generate_data_visualizations(data)
    
    def _generate_data_visualizations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate visualization data that frontend can render"""
        visualizations = {}
        
        # Trust score data
        if 'trust_score' in data:
            visualizations['trust_gauge_data'] = {
                'type': 'gauge',
                'value': data['trust_score'],
                'max': 100,
                'thresholds': {
                    'low': 40,
                    'medium': 70,
                    'high': 100
                },
                'colors': self.color_schemes['trust'],
                'label': self._get_trust_label(data['trust_score'])
            }
        
        # Bias radar data
        if 'bias_analysis' in data and data['bias_analysis'].get('bias_dimensions'):
            dimensions = data['bias_analysis']['bias_dimensions']
            visualizations['bias_radar_data'] = {
                'type': 'radar',
                'axes': [],
                'data': []
            }
            
            for dim_name, dim_data in dimensions.items():
                visualizations['bias_radar_data']['axes'].append({
                    'axis': dim_name.title(),
                    'label': self._get_dimension_label(dim_name)
                })
                visualizations['bias_radar_data']['data'].append({
                    'value': abs(dim_data.get('score', 0)) * 100,
                    'color': self.color_schemes['bias'].get(dim_name, '#6b7280')
                })
        
        # Fact check summary data
        if 'fact_checks' in data and isinstance(data['fact_checks'], list):
            fact_summary = self._summarize_fact_checks(data['fact_checks'])
            visualizations['fact_check_data'] = {
                'type': 'donut',
                'segments': [
                    {'label': 'True', 'value': fact_summary['true'], 'color': '#10b981'},
                    {'label': 'False', 'value': fact_summary['false'], 'color': '#ef4444'},
                    {'label': 'Unverified', 'value': fact_summary['unverified'], 'color': '#6b7280'}
                ],
                'total': fact_summary['total'],
                'center_text': f"{fact_summary['accuracy']}% Accurate"
            }
        
        # Source credibility data
        if 'source_credibility' in data:
            cred = data['source_credibility']
            cred_score = cred.get('credibility_score', 50)
            visualizations['credibility_meter_data'] = {
                'type': 'meter',
                'value': cred_score,
                'max': 100,
                'zones': [
                    {'from': 0, 'to': 30, 'color': '#ef4444', 'label': 'Low'},
                    {'from': 30, 'to': 70, 'color': '#f59e0b', 'label': 'Medium'},
                    {'from': 70, 'to': 100, 'color': '#10b981', 'label': 'High'}
                ],
                'label': cred.get('credibility', 'Unknown'),
                'sublabel': cred.get('category', '')
            }
        
        # Timeline visualization data
        visualizations['analysis_timeline_data'] = self._create_timeline_data(data)
        
        return {
            'service': self.service_name,
            'success': True,
            'data': {
                'visualizations': visualizations,
                'visualization_count': len(visualizations),
                'formats_available': ['json'],
                'frontend_renderable': True,
                'summary': self._generate_visualization_summary(visualizations)
            },
            'metadata': {
                'library_used': 'data_only',
                'requires_frontend_rendering': True
            }
        }
    
    def _create_trust_gauge(self, trust_score: float) -> Dict[str, Any]:
        """Create a trust score gauge visualization"""
        fig, ax = plt.subplots(figsize=(6, 4), subplot_kw=dict(projection='polar'))
        
        # Convert score to angle (0-180 degrees)
        angle = np.pi * (1 - trust_score / 100)
        
        # Create gauge background
        theta = np.linspace(np.pi, 0, 100)
        r = np.ones_like(theta)
        
        # Color zones
        colors = []
        for t in theta:
            if t > 2*np.pi/3:  # Low (0-33%)
                colors.append(self.color_schemes['trust']['low'])
            elif t > np.pi/3:  # Moderate (33-67%)
                colors.append(self.color_schemes['trust']['moderate'])
            else:  # High (67-100%)
                colors.append(self.color_schemes['trust']['high'])
        
        # Plot gauge
        for i in range(len(theta)-1):
            ax.fill_between([theta[i], theta[i+1]], 0, 1, color=colors[i], alpha=0.8)
        
        # Add needle
        ax.plot([angle, angle], [0, 0.9], 'k-', linewidth=3)
        ax.scatter([angle], [0.9], s=100, c='black', zorder=5)
        
        # Style
        ax.set_ylim(0, 1)
        ax.set_theta_offset(np.pi)
        ax.set_theta_direction(-1)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['polar'].set_visible(False)
        ax.grid(False)
        
        # Add labels
        ax.text(0, -0.2, f'{trust_score}%', ha='center', va='center', fontsize=24, fontweight='bold')
        ax.text(0, -0.35, self._get_trust_label(trust_score), ha='center', va='center', fontsize=14)
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', transparent=True)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return {
            'type': 'gauge',
            'format': 'png',
            'data': f'data:image/png;base64,{image_base64}',
            'value': trust_score,
            'label': self._get_trust_label(trust_score)
        }
    
    def _create_bias_radar(self, bias_dimensions: Dict[str, Any]) -> Dict[str, Any]:
        """Create a radar chart for bias dimensions"""
        # Prepare data
        categories = []
        values = []
        colors = []
        
        for dim_name, dim_data in bias_dimensions.items():
            categories.append(self._get_dimension_label(dim_name))
            values.append(abs(dim_data.get('score', 0)) * 100)
            colors.append(self.color_schemes['bias'].get(dim_name, '#6b7280'))
        
        # Number of variables
        num_vars = len(categories)
        
        # Compute angle for each axis
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        values += values[:1]  # Complete the circle
        angles += angles[:1]
        
        # Create plot
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        
        # Draw the outline of our data
        ax.plot(angles, values, color='#1f2937', linewidth=2)
        ax.fill(angles, values, color='#3b82f6', alpha=0.25)
        
        # Fix axis to go in the right order and start at 12 o'clock
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        
        # Draw axis lines for each angle and label
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, size=10)
        
        # Set y-axis limits and labels
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80])
        ax.set_yticklabels(['20%', '40%', '60%', '80%'], size=8)
        ax.yaxis.grid(True, linestyle='--', alpha=0.7)
        
        # Add a title
        plt.title('Bias Analysis by Dimension', size=16, pad=20)
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', transparent=True)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return {
            'type': 'radar',
            'format': 'png',
            'data': f'data:image/png;base64,{image_base64}',
            'dimensions': categories,
            'values': values[:-1]  # Remove duplicated last value
        }
    
    def _create_fact_check_chart(self, fact_checks: List[Dict]) -> Dict[str, Any]:
        """Create a donut chart for fact check results"""
        if not fact_checks:
            return {'type': 'no_data', 'message': 'No fact checks available'}
        
        # Summarize fact checks
        summary = self._summarize_fact_checks(fact_checks)
        
        # Data for the donut chart
        sizes = [summary['true'], summary['false'], summary['unverified']]
        labels = ['Verified True', 'False', 'Unverified']
        colors = ['#10b981', '#ef4444', '#6b7280']
        
        # Create donut chart
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Create pie chart with hole in center
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                          startangle=90, wedgeprops=dict(width=0.5))
        
        # Add center text
        centre_circle = Circle((0, 0), 0.70, fc='white')
        fig.gca().add_artist(centre_circle)
        
        # Add accuracy percentage in center
        ax.text(0, 0, f"{summary['accuracy']}%\nAccuracy", ha='center', va='center',
                fontsize=20, fontweight='bold')
        
        # Add title
        plt.title(f'Fact Check Summary ({summary["total"]} claims)', fontsize=14, pad=20)
        
        # Equal aspect ratio ensures that pie is drawn as a circle
        ax.axis('equal')
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', transparent=True)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return {
            'type': 'donut',
            'format': 'png',
            'data': f'data:image/png;base64,{image_base64}',
            'summary': summary
        }
    
    def _create_credibility_meter(self, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a credibility meter visualization"""
        fig, ax = plt.subplots(figsize=(8, 4))
        
        # Get credibility score
        score = source_data.get('credibility_score', 50)
        credibility = source_data.get('credibility', 'Unknown')
        
        # Create meter background
        meter_width = 0.8
        meter_height = 0.2
        meter_bottom = 0.4
        
        # Draw zones
        zones = [
            (0, 0.3, self.color_schemes['trust']['low'], 'Low'),
            (0.3, 0.7, self.color_schemes['trust']['moderate'], 'Medium'),
            (0.7, 1.0, self.color_schemes['trust']['high'], 'High')
        ]
        
        for start, end, color, label in zones:
            rect = Rectangle((start, meter_bottom), end - start, meter_height,
                           facecolor=color, alpha=0.7)
            ax.add_patch(rect)
            ax.text((start + end) / 2, meter_bottom - 0.1, label,
                   ha='center', va='top', fontsize=10)
        
        # Draw needle
        needle_pos = score / 100
        ax.arrow(needle_pos, meter_bottom + meter_height + 0.05, 0, -0.04,
                head_width=0.03, head_length=0.02, fc='black', ec='black')
        
        # Add score text
        ax.text(needle_pos, meter_bottom + meter_height + 0.15, f'{score}',
               ha='center', va='bottom', fontsize=16, fontweight='bold')
        
        # Add title and subtitle
        ax.text(0.5, 0.9, f'Source Credibility: {credibility}', ha='center', va='center',
               fontsize=18, fontweight='bold', transform=ax.transAxes)
        
        if 'domain' in source_data:
            ax.text(0.5, 0.8, source_data['domain'], ha='center', va='center',
                   fontsize=12, transform=ax.transAxes)
        
        # Remove axes
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', transparent=True)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return {
            'type': 'meter',
            'format': 'png',
            'data': f'data:image/png;base64,{image_base64}',
            'score': score,
            'credibility': credibility
        }
    
    def _create_author_visualization(self, author_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create author credibility visualization"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        
        # Author credibility score (left)
        score = author_data.get('credibility_score', 0)
        name = author_data.get('name', 'Unknown Author')
        
        # Create circular progress
        theta = np.linspace(0, 2 * np.pi * (score / 100), 100)
        r = np.ones_like(theta)
        
        ax1.plot(theta, r, color=self._get_score_color(score), linewidth=10)
        ax1.fill(theta, r * 0.8, color=self._get_score_color(score), alpha=0.3)
        
        ax1.text(0, 0, f'{score}%', ha='center', va='center', fontsize=24, fontweight='bold')
        ax1.text(0, -0.3, 'Credibility', ha='center', va='center', fontsize=12)
        
        ax1.set_xlim(-1.5, 1.5)
        ax1.set_ylim(-1.5, 1.5)
        ax1.axis('off')
        ax1.set_aspect('equal')
        
        # Author details (right)
        details = []
        if author_data.get('years_experience'):
            details.append(f"Experience: {author_data['years_experience']} years")
        if author_data.get('article_count'):
            details.append(f"Articles: {author_data['article_count']}")
        if author_data.get('expertise_areas'):
            areas = ', '.join(author_data['expertise_areas'][:3])
            details.append(f"Expertise: {areas}")
        
        ax2.text(0.1, 0.9, name, fontsize=16, fontweight='bold', transform=ax2.transAxes)
        
        y_pos = 0.7
        for detail in details:
            ax2.text(0.1, y_pos, detail, fontsize=12, transform=ax2.transAxes)
            y_pos -= 0.15
        
        ax2.axis('off')
        
        plt.suptitle('Author Analysis', fontsize=18)
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', transparent=True)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return {
            'type': 'author_profile',
            'format': 'png',
            'data': f'data:image/png;base64,{image_base64}',
            'author': name,
            'score': score
        }
    
    def _create_analysis_dashboard(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a comprehensive analysis dashboard"""
        fig = plt.figure(figsize=(16, 10))
        
        # Create grid
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # Trust Score (top left)
        ax1 = fig.add_subplot(gs[0, 0])
        trust_score = data.get('trust_score', 0)
        self._draw_mini_gauge(ax1, trust_score, 'Trust Score')
        
        # Key Metrics (top center and right)
        ax2 = fig.add_subplot(gs[0, 1:])
        self._draw_key_metrics(ax2, data)
        
        # Bias Distribution (middle left)
        if 'bias_analysis' in data:
            ax3 = fig.add_subplot(gs[1, 0])
            self._draw_bias_bars(ax3, data['bias_analysis'])
        
        # Fact Check Summary (middle center)
        if 'fact_checks' in data:
            ax4 = fig.add_subplot(gs[1, 1])
            self._draw_fact_summary(ax4, data['fact_checks'])
        
        # Source Info (middle right)
        if 'source_credibility' in data:
            ax5 = fig.add_subplot(gs[1, 2])
            self._draw_source_info(ax5, data['source_credibility'])
        
        # Analysis Summary (bottom)
        ax6 = fig.add_subplot(gs[2, :])
        self._draw_analysis_summary(ax6, data)
        
        plt.suptitle('News Analysis Dashboard', fontsize=20, fontweight='bold')
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', transparent=True, dpi=150)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return {
            'type': 'dashboard',
            'format': 'png',
            'data': f'data:image/png;base64,{image_base64}',
            'components': ['trust_score', 'metrics', 'bias', 'facts', 'source', 'summary']
        }
    
    def _draw_mini_gauge(self, ax, score: float, title: str):
        """Draw a mini gauge on given axes"""
        # Create semi-circle gauge
        theta = np.linspace(np.pi, 0, 100)
        
        # Color based on score
        if score >= 70:
            color = self.color_schemes['trust']['high']
        elif score >= 40:
            color = self.color_schemes['trust']['moderate']
        else:
            color = self.color_schemes['trust']['low']
        
        # Draw arc
        arc = patches.Arc((0.5, 0.3), 0.8, 0.8, angle=0, theta1=0, theta2=180,
                         color=color, linewidth=15)
        ax.add_patch(arc)
        
        # Add score text
        ax.text(0.5, 0.3, f'{int(score)}%', ha='center', va='center',
               fontsize=24, fontweight='bold')
        ax.text(0.5, 0.1, title, ha='center', va='center', fontsize=12)
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 0.6)
        ax.axis('off')
    
    def _draw_key_metrics(self, ax, data: Dict[str, Any]):
        """Draw key metrics summary"""
        metrics = []
        
        if 'bias_analysis' in data:
            bias = data['bias_analysis']
            political_lean = bias.get('political_lean', 0)
            if political_lean < -20:
                lean = "Left-leaning"
            elif political_lean > 20:
                lean = "Right-leaning"
            else:
                lean = "Centrist"
            metrics.append(('Political Stance:', lean))
        
        if 'transparency_analysis' in data:
            trans_score = data['transparency_analysis'].get('score', 0)
            metrics.append(('Transparency:', f'{trans_score}%'))
        
        if 'clickbait_analysis' in data:
            click_score = data['clickbait_analysis'].get('score', 0)
            metrics.append(('Clickbait Level:', f'{click_score}%'))
        
        # Display metrics
        y_pos = 0.8
        for label, value in metrics:
            ax.text(0.1, y_pos, label, fontsize=12, fontweight='bold')
            ax.text(0.6, y_pos, value, fontsize=12)
            y_pos -= 0.3
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
    
    def _draw_bias_bars(self, ax, bias_data: Dict[str, Any]):
        """Draw bias dimension bars"""
        if not bias_data.get('bias_dimensions'):
            ax.text(0.5, 0.5, 'No bias data', ha='center', va='center')
            ax.axis('off')
            return
        
        dimensions = bias_data['bias_dimensions']
        labels = []
        values = []
        colors = []
        
        for dim, data in dimensions.items():
            labels.append(dim.capitalize())
            values.append(abs(data.get('score', 0)) * 100)
            colors.append(self.color_schemes['bias'].get(dim, '#6b7280'))
        
        y_pos = np.arange(len(labels))
        ax.barh(y_pos, values, color=colors, alpha=0.8)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.set_xlabel('Bias Level (%)')
        ax.set_xlim(0, 100)
        ax.set_title('Bias by Dimension', fontsize=12)
    
    def _draw_fact_summary(self, ax, fact_checks: List[Dict]):
        """Draw fact check summary"""
        summary = self._summarize_fact_checks(fact_checks)
        
        # Create pie chart
        sizes = [summary['true'], summary['false'], summary['unverified']]
        labels = ['True', 'False', 'Unverified']
        colors = ['#10b981', '#ef4444', '#6b7280']
        
        # Remove zero values
        non_zero = [(s, l, c) for s, l, c in zip(sizes, labels, colors) if s > 0]
        if non_zero:
            sizes, labels, colors = zip(*non_zero)
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.0f%%', startangle=90)
        
        ax.set_title(f'Fact Checks ({summary["total"]} total)', fontsize=12)
    
    def _draw_source_info(self, ax, source_data: Dict[str, Any]):
        """Draw source credibility info"""
        info = []
        info.append(('Source:', source_data.get('domain', 'Unknown')))
        info.append(('Credibility:', source_data.get('credibility', 'Unknown')))
        info.append(('Category:', source_data.get('category', 'Unknown')))
        
        if source_data.get('age_days'):
            age_years = source_data['age_days'] / 365
            info.append(('Domain Age:', f'{age_years:.1f} years'))
        
        y_pos = 0.9
        for label, value in info:
            ax.text(0.1, y_pos, label, fontsize=10, fontweight='bold')
            ax.text(0.1, y_pos - 0.1, value, fontsize=10)
            y_pos -= 0.25
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        ax.set_title('Source Information', fontsize=12)
    
    def _draw_analysis_summary(self, ax, data: Dict[str, Any]):
        """Draw analysis summary text"""
        summary_points = []
        
        trust_score = data.get('trust_score', 0)
        if trust_score >= 70:
            summary_points.append("✓ High overall trustworthiness")
        elif trust_score >= 40:
            summary_points.append("⚠ Moderate trustworthiness - verify key claims")
        else:
            summary_points.append("✗ Low trustworthiness - approach with caution")
        
        if 'bias_analysis' in data:
            bias = data['bias_analysis']
            if bias.get('objectivity_score', 0) > 70:
                summary_points.append("✓ Generally objective reporting")
            else:
                summary_points.append("⚠ Contains subjective or biased content")
        
        if 'fact_checks' in data and data['fact_checks']:
            summary = self._summarize_fact_checks(data['fact_checks'])
            if summary['accuracy'] >= 80:
                summary_points.append("✓ Most claims are factually accurate")
            elif summary['accuracy'] >= 50:
                summary_points.append("⚠ Mixed factual accuracy")
            else:
                summary_points.append("✗ Many false or unverified claims")
        
        # Display summary
        ax.text(0.05, 0.8, 'Analysis Summary:', fontsize=14, fontweight='bold')
        y_pos = 0.6
        for point in summary_points[:4]:  # Limit to 4 points
            ax.text(0.05, y_pos, point, fontsize=12)
            y_pos -= 0.2
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
    
    # Helper methods
    def _get_trust_label(self, score: float) -> str:
        """Get label for trust score"""
        if score >= 80:
            return "Very High Trust"
        elif score >= 70:
            return "High Trust"
        elif score >= 50:
            return "Moderate Trust"
        elif score >= 30:
            return "Low Trust"
        else:
            return "Very Low Trust"
    
    def _get_dimension_label(self, dimension: str) -> str:
        """Get display label for bias dimension"""
        labels = {
            'political': 'Political',
            'corporate': 'Corporate',
            'sensational': 'Sensational',
            'nationalistic': 'National',
            'establishment': 'Authority'
        }
        return labels.get(dimension, dimension.title())
    
    def _get_score_color(self, score: float) -> str:
        """Get color based on score"""
        if score >= 70:
            return self.color_schemes['trust']['high']
        elif score >= 40:
            return self.color_schemes['trust']['moderate']
        else:
            return self.color_schemes['trust']['low']
    
    def _summarize_fact_checks(self, fact_checks: List[Dict]) -> Dict[str, Any]:
        """Summarize fact check results"""
        total = len(fact_checks)
        if total == 0:
            return {
                'total': 0,
                'true': 0,
                'false': 0,
                'unverified': 0,
                'accuracy': 0
            }
        
        true_count = sum(1 for fc in fact_checks 
                        if fc.get('verdict', '').lower() in ['true', 'verified', 'correct'])
        false_count = sum(1 for fc in fact_checks 
                         if fc.get('verdict', '').lower() in ['false', 'incorrect', 'wrong'])
        unverified_count = total - true_count - false_count
        
        accuracy = int((true_count / total) * 100) if total > 0 else 0
        
        return {
            'total': total,
            'true': true_count,
            'false': false_count,
            'unverified': unverified_count,
            'accuracy': accuracy
        }
    
    def _create_timeline_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create timeline visualization data"""
        events = []
        
        # Add analysis milestones
        if 'article' in data and data['article'].get('date'):
            events.append({
                'date': data['article']['date'],
                'event': 'Article Published',
                'type': 'publication'
            })
        
        if 'analysis_timestamp' in data:
            events.append({
                'date': data['analysis_timestamp'],
                'event': 'Analysis Performed',
                'type': 'analysis'
            })
        
        # Add any updates or corrections noted
        if 'corrections' in data:
            for correction in data['corrections']:
                events.append({
                    'date': correction.get('date'),
                    'event': f"Correction: {correction.get('description', 'Updated')}",
                    'type': 'correction'
                })
        
        return {
            'type': 'timeline',
            'events': sorted(events, key=lambda x: x['date']) if events else [],
            'span_days': self._calculate_timeline_span(events) if events else 0
        }
    
    def _calculate_timeline_span(self, events: List[Dict]) -> int:
        """Calculate span of timeline in days"""
        if not events:
            return 0
        
        # This is simplified - in production, parse actual dates
        return 30  # Placeholder
    
    def _generate_visualization_summary(self, visualizations: Dict[str, Any]) -> str:
        """Generate summary of created visualizations"""
        viz_count = len(visualizations)
        viz_types = [v.get('type', 'unknown') for v in visualizations.values() if isinstance(v, dict)]
        
        summary = f"Generated {viz_count} visualizations"
        if viz_types:
            unique_types = list(set(viz_types))
            summary += f" including: {', '.join(unique_types)}"
        
        return summary
